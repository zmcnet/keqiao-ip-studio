#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
《作品演示视频》v3 —— 跟 PPT 讲（彻底解决字幕与画面对不上）
================================================
思路：把「作品演示PPT」的 10 页作为画面主体，逐页对应 10 段配音。
  画面来源 = PPT 页面渲染图（每页讲什么，画面就是什么）
  转场 = 推近/平移的轻微运镜 + 页间交叉溶解（非图片缩放硬凑）
  字幕 = 白字 + 深色描边，按配音分句
  音频 = 仅配音（无背景音效）
规格：1920×1080 · 30fps · H.264 · CBR 9Mbps
"""
import os, json, subprocess, shutil

ROOT = os.path.dirname(os.path.abspath(__file__))
WORK = os.path.join(ROOT, "video_work")
VO = os.path.join(WORK, "vo2")
DIST = os.path.join(ROOT, "dist")
TMP = os.path.join(WORK, "v3demo")
PAGES = os.path.join(ROOT, "演示PPT", "_check", "render")
os.makedirs(TMP, exist_ok=True)
os.makedirs(DIST, exist_ok=True)

W, H, FPS = 1920, 1080, 30
BR = "9M"
FADE = 0.5
VOJ = json.load(open(os.path.join(VO, "durations.json"), encoding="utf-8"))

# 页序 → 配音 key（严格一一对应）
PAGES_MAP = [
    ("幻灯片1.PNG", "d0_hook"),
    ("幻灯片2.PNG", "d1_arch"),
    ("幻灯片3.PNG", "d2_plan"),
    ("幻灯片4.PNG", "d3_asset"),
    ("幻灯片5.PNG", "d4_shot"),
    ("幻灯片6.PNG", "d5_edit"),
    ("幻灯片7.PNG", "d6_export"),
    ("幻灯片8.PNG", "d7_comply"),
    ("幻灯片9.PNG", "d8_family"),
    ("幻灯片10.PNG", "d9_end"),
]

ASS_HDR = """[Script Info]
ScriptType: v4.00+
PlayResX: 1920
PlayResY: 1080
WrapStyle: 0

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Def,Microsoft YaHei,46,&H00FFFFFF,&H00FFFFFF,&H00202020,&H00000000,-1,0,0,0,100,100,1,0,1,3,1,2,80,80,58,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""


def ff(cmd):
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        print("FFERR:", " ".join(str(c) for c in cmd[:14]))
        print(r.stderr[-1200:])
    return r.returncode == 0


def dur(p):
    r = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                        "-of", "default=noprint_wrappers=1:nokey=1", p],
                       capture_output=True, text=True)
    try:
        return round(float(r.stdout.strip()), 3)
    except Exception:
        return 0.0


def ts(t):
    h = int(t // 3600); m = int((t % 3600) // 60); s = t % 60
    return "%d:%02d:%05.2f" % (h, m, s)


def sub_cues(text, total, maxlen=26):
    import re
    parts = [s for s in re.split(r"(?<=[。！？；，、])", text) if s]
    merged, cur = [], ""
    for s in parts:
        if len(cur) + len(s) <= maxlen or not cur:
            cur += s
        else:
            merged.append(cur); cur = s
    if cur:
        merged.append(cur)
    if not merged:
        merged = [text]
    tot = sum(len(s) for s in merged) or 1
    cues, t = [], 0.0
    for s in merged:
        d = total * len(s) / tot
        cues.append((t, min(total, t + d), s.strip()))
        t += d
    return cues


def ass_for(text, total, path):
    body = []
    for st, en, tx in sub_cues(text, total):
        body.append("Dialogue: 0,%s,%s,Def,,0,0,0,,%s" % (ts(st), ts(en), tx.replace("\n", "\\N")))
    open(path, "w", encoding="utf-8").write(ASS_HDR + "\n".join(body) + "\n")
    return path


def build_seg(img, key, out):
    """页图 + 轻微推近运镜 + 字幕；时长 = 配音时长"""
    d = VOJ[key]["dur"]
    ap = ass_for(VOJ[key]["text"], d, os.path.join(TMP, key + ".ass"))
    apf = ap.replace("\\", "/").replace(":", "\\:")
    # 从 2933×1650 轻微推近（scale 放大 4%）再裁到 1920×1080；稳定不抖
    scale_w = int(W * 1.04)
    scale_h = int(H * 1.04)
    vf = (
        f"scale={scale_w}:{scale_h},"
        f"zoompan=z={scale_w/W:.4f}:x='(iw-{W})/2':y='(ih-{H})/2':d={int(d*FPS)}:s={W}x{H}:fps={FPS},"
        f"subtitles='{apf}',setsar=1"
    )
    return ff(["ffmpeg", "-y", "-loop", "1", "-i", img, "-t", f"{d:.3f}",
               "-vf", vf, "-an", "-c:v", "libx264", "-preset", "medium",
               "-crf", "19", "-pix_fmt", "yuv420p", "-r", str(FPS), out])


def attach(video, key, out):
    vo = os.path.join(VO, key + ".mp3")
    d = dur(video)
    return ff(["ffmpeg", "-y", "-i", video, "-i", vo,
               "-filter_complex",
               f"[1:a]apad,atrim=0:{d:.3f},asetpts=N/SR/TB,"
               f"afade=t=in:st=0:d=0.25,afade=t=out:st={max(0.1,d-0.4):.2f}:d=0.4[a]",
               "-map", "0:v", "-map", "[a]", "-c:v", "copy", "-c:a", "aac",
               "-b:a", "192k", "-ar", "44100", "-shortest", out])


def link(segs, out, fade=FADE):
    inputs = []
    for s in segs:
        inputs += ["-i", s]
    ds = [dur(s) for s in segs]
    fc = []
    pv, pa = "[0:v]", "[0:a]"
    t = ds[0]
    for i in range(1, len(segs)):
        off = max(0.0, t - fade)
        fc.append(f"{pv}[{i}:v]xfade=transition=fade:duration={fade}:offset={off:.3f}[v{i}]")
        fc.append(f"{pa}[{i}:a]acrossfade=d={fade}:c1=tri:c2=tri[a{i}]")
        t = t + ds[i] - fade
        pv, pa = f"[v{i}]", f"[a{i}]"
    return ff(["ffmpeg", "-y", *inputs, "-filter_complex", ";".join(fc),
               "-map", pv, "-map", pa, "-c:v", "libx264", "-preset", "medium",
               "-crf", "19", "-pix_fmt", "yuv420p", "-r", str(FPS),
               "-c:a", "aac", "-b:a", "192k", "-ar", "44100", out])


def finalize(src, out):
    return ff(["ffmpeg", "-y", "-i", src,
               "-c:v", "libx264", "-preset", "medium",
               "-b:v", BR, "-minrate", BR, "-maxrate", BR, "-bufsize", BR,
               "-x264-params", "nal-hrd=cbr:force-cfr=1:filler=1",
               "-c:a", "aac", "-b:a", "192k", "-ar", "44100",
               "-movflags", "+faststart", out])


def main():
    print("===== 《作品演示视频》v3（跟 PPT 讲）=====")
    if not os.path.isdir(PAGES):
        raise SystemExit("未找到 PPT 页面渲染图：%s" % PAGES)
    parts = []
    for i, (img, key) in enumerate(PAGES_MAP, 1):
        ip = os.path.join(PAGES, img)
        vp = os.path.join(TMP, "seg%02d.mp4" % i)
        ap = os.path.join(TMP, "au%02d.mp4" % i)
        if not build_seg(ip, key, vp):
            print("  第 %d 页构建失败" % i); continue
        attach(vp, key, ap)
        parts.append(ap)
        print("  第 %2d 页 ✓  %-11s %5.2fs" % (i, key, VOJ[key]["dur"]))

    merged = os.path.join(TMP, "demo3_merged.mp4")
    link(parts, merged)
    out = os.path.join(DIST, "作品演示视频.mp4")
    finalize(merged, out)
    shutil.copy(out, os.path.join(DIST, "[队伍编号]作品演示视频.mp4"))
    print("\n演示视频: %.1fs" % dur(out))


if __name__ == "__main__":
    main()
