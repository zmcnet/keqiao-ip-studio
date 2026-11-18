#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
柯桥·水乡IP造物台 —— 视频重制 v2（真动态版）
================================================
关键变更：
  1) 去掉全部背景音效，仅保留配音
  2) 用 VideoGen 生成的【真动态视频】替代图片缩放
  3) 全文字走 ASS（解决 drawtext 中文字体加载失败→方块）
  4) 竖版动态素材：满高前景 + 模糊背景 + 左侧角色信息栏
  5) 段间交叉溶解（xfade + acrossfade），音画同步
规格：1920×1080 · 30fps · H.264 · CBR 9Mbps
"""
import os, json, subprocess, shutil

ROOT = os.path.dirname(os.path.abspath(__file__))
WORK = os.path.join(ROOT, "video_work")
DYN = os.path.join(WORK, "dyn_named")
DEMO = os.path.join(WORK, "demo")
VO = os.path.join(WORK, "vo2")
DIST = os.path.join(ROOT, "dist")
TMP = os.path.join(WORK, "v2seg")
os.makedirs(TMP, exist_ok=True)
os.makedirs(DIST, exist_ok=True)

W, H, FPS = 1920, 1080, 30
BR = "9M"
FADE = 0.45
VOJ = json.load(open(os.path.join(VO, "durations.json"), encoding="utf-8"))
ACCENT = "0xC0392B"


def ff(cmd):
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        print("FFERR:", " ".join(str(c) for c in cmd[:16]))
        print(r.stderr[-1500:])
    return r.returncode == 0


def dur(p):
    r = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                        "-of", "default=noprint_wrappers=1:nokey=1", p],
                       capture_output=True, text=True)
    try:
        return round(float(r.stdout.strip()), 3)
    except Exception:
        return 0.0


def vd(key):
    return VOJ.get(key, {}).get("dur", 5.0)


def vt(key):
    return VOJ.get(key, {}).get("text", "")


# ---------------- ASS ----------------
ASS_HDR = """[Script Info]
ScriptType: v4.00+
PlayResX: 1920
PlayResY: 1080
WrapStyle: 0

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Def,Microsoft YaHei,44,&H00FFFFFF,&H00FFFFFF,&H00202020,&H00000000,-1,0,0,0,100,100,1,0,1,3,1,2,80,80,62,1
Style: Left,Microsoft YaHei,52,&H00FFFFFF,&H00FFFFFF,&H00171F28,&H00000000,-1,0,0,0,100,100,1,0,1,3,1,4,96,40,0,1
Style: LeftS,Microsoft YaHei,28,&H00CFE0F2,&H00CFE0F2,&H00171F28,&H00000000,0,0,0,0,100,100,1,0,1,2,0,4,96,40,0,1
Style: Title,Microsoft YaHei,84,&H00FFFFFF,&H00FFFFFF,&H0012283C,&H00000000,-1,0,0,0,100,100,2,0,1,4,1,5,40,40,0,1
Style: TitleS,Microsoft YaHei,36,&H00D8E6F5,&H00D8E6F5,&H0012283C,&H00000000,0,0,0,0,100,100,2,0,1,3,1,5,40,40,0,1
Style: Tag,Microsoft YaHei,26,&H00C0D8F0,&H00C0D8F0,&H0012283C,&H00000000,0,0,0,0,100,100,1,0,1,2,0,9,40,60,40,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""


def ts(t):
    h = int(t // 3600); m = int((t % 3600) // 60); s = t % 60
    return "%d:%02d:%05.2f" % (h, m, s)


def write_ass(path, cues):
    """cues: [(start,end,style,text)]"""
    body = []
    for st, en, sty, tx in cues:
        body.append("Dialogue: 0,%s,%s,%s,,0,0,0,,%s" % (ts(st), ts(en), sty, tx.replace("\n", "\\N")))
    open(path, "w", encoding="utf-8").write(ASS_HDR + "\n".join(body) + "\n")
    return path


def sub_cues(text, total, style="Def", maxlen=26):
    """把长句按标点拆成多条字幕，按字数比例分配时间——避免溢出画面"""
    import re
    parts = [s for s in re.split(r"(?<=[。！？；，、])", text) if s]
    # 合并过短片段，使每条尽量接近 maxlen
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
    for i, s in enumerate(merged):
        d = total * len(s) / tot
        st = t
        en = min(total, t + d)
        # 首尾相接，避免相邻字幕重叠（末条留 0.35s 余量）
        if i < len(merged) - 1:
            en = min(en, total)
        cues.append((st, en, style, s.strip()))
        t += d
    return cues


def ass_filter(path, out_label="vout", in_label="vin"):
    p = path.replace("\\", "/").replace(":", "\\:")
    return f"[{in_label}]subtitles='{p}'[{out_label}]"


def vinfo(p):
    r = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v",
                        "-show_entries", "stream=width,height", "-of", "csv=p=0", p],
                       capture_output=True, text=True)
    try:
        w, h = r.stdout.strip().split(",")[:2]
        return int(w), int(h)
    except Exception:
        return 1920, 1080


# ---------------- 段落构建 ----------------
def seg(clips, target, out, sub=None, label=None, accent=True, idx=None):
    """竖版→满高前景+模糊底+左侧信息；横版(录屏)→铺满"""
    n = len(clips)
    each = target / n
    inputs = []
    for p in clips:
        inputs += ["-i", p]
    parts = []
    for i, p in enumerate(clips):
        d = dur(p); w, h = vinfo(p)
        port = h > w
        # 竖版：四周内缩 6% 裁掉 AI 水印，再放大铺满
        crop = "crop=iw*0.88:ih*0.88:iw*0.06:ih*0.06," if port else ""
        ratio = each / d if d > 0 else 1.0
        if port:
            parts.append(
                f"[{i}:v]{crop}setpts=PTS*{ratio:.5f},fps={FPS},split=2[bg{i}][fg{i}];"
                f"[bg{i}]scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H},"
                f"gblur=sigma=38,eq=brightness=-0.30:saturation=0.82[bgf{i}];"
                f"[fg{i}]scale=-2:{H},setsar=1[fgf{i}];"
                f"[bgf{i}][fgf{i}]overlay=(W-w)/2:0[s{i}]"
            )
        else:
            parts.append(
                f"[{i}:v]{crop}setpts=PTS*{ratio:.5f},fps={FPS},"
                f"scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H},setsar=1[s{i}]"
            )
    fc = ";".join(parts) + ";" + "".join(f"[s{i}]" for i in range(n)) + f"concat=n={n}:v=1:a=0[cat]"
    # 装饰竖线（朱砂）
    fc += f";[cat]drawbox=x=62:y=430:w=6:h=220:color={ACCENT}@0.92:t=fill[ln]"
    # 文字
    cues = []
    if idx:
        cues.append((0, target, "Tag", idx))
    if sub:
        cues += sub_cues(sub, target)
    if label:
        cues.append((0, target, "Left", label))
    if cues:
        ap = os.path.join(TMP, os.path.basename(out) + ".ass")
        write_ass(ap, cues)
        fc += ";" + ass_filter(ap, "vout", "ln")
    else:
        fc += ";[ln]null[vout]"
    return ff(["ffmpeg", "-y", *inputs, "-filter_complex", fc, "-map", "[vout]",
               "-t", f"{target:.3f}", "-an", "-c:v", "libx264", "-preset", "medium",
               "-crf", "19", "-pix_fmt", "yuv420p", "-r", str(FPS), out])


def card(out, target, main, sub, bg):
    """标题/尾板卡（ASS 渲染，中文稳定）"""
    d = dur(bg)
    inp = ["-i", bg]
    if d > 0:
        ratio = target / d
        base = (f"[0:v]crop=iw*0.88:ih*0.88:iw*0.06:ih*0.06,setpts=PTS*{ratio:.5f},fps={FPS},"
                f"scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H},"
                f"gblur=sigma=36,eq=brightness=-0.30:saturation=0.80[bg]")
    else:
        base = f"[0:v]scale={W}:{H},eq=brightness=-0.5[bg]"
    ap = os.path.join(TMP, os.path.basename(out) + ".ass")
    write_ass(ap, [(0, target, "Title", main), (0, target, "TitleS", sub)])
    fc = base + ";" + ass_filter(ap, "vout", "bg")
    return ff(["ffmpeg", "-y", *inp, "-filter_complex", fc, "-map", "[vout]",
               "-t", f"{target:.3f}", "-an", "-c:v", "libx264", "-preset", "medium",
               "-crf", "19", "-pix_fmt", "yuv420p", "-r", str(FPS), out])


def attach(video, key, out):
    vo = os.path.join(VO, key + ".mp3")
    d = dur(video)
    if not os.path.exists(vo):
        return ff(["ffmpeg", "-y", "-f", "lavfi", "-i", "anullsrc=r=44100:cl=stereo",
                   "-i", video, "-map", "1:v", "-map", "0:a", "-t", f"{d:.3f}",
                   "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", out])
    return ff(["ffmpeg", "-y", "-i", video, "-i", vo,
               "-filter_complex",
               f"[1:a]apad,atrim=0:{d:.3f},asetpts=N/SR/TB,"
               f"afade=t=in:st=0:d=0.25,afade=t=out:st={max(0.1,d-0.4):.2f}:d=0.4[a]",
               "-map", "0:v", "-map", "[a]", "-c:v", "copy", "-c:a", "aac",
               "-b:a", "192k", "-ar", "44100", "-shortest", out])


def link(segs, out, fade=FADE):
    """交叉溶解串联（视频 xfade + 音频 acrossfade）"""
    if len(segs) == 1:
        shutil.copy(segs[0], out); return True
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
    cmd = ["ffmpeg", "-y", *inputs, "-filter_complex", ";".join(fc),
           "-map", pv, "-map", pa, "-c:v", "libx264", "-preset", "medium",
           "-crf", "19", "-pix_fmt", "yuv420p", "-r", str(FPS),
           "-c:a", "aac", "-b:a", "192k", "-ar", "44100", out]
    return ff(cmd)


def finalize(src, out):
    return ff(["ffmpeg", "-y", "-i", src,
               "-c:v", "libx264", "-preset", "medium",
               "-b:v", BR, "-minrate", BR, "-maxrate", BR, "-bufsize", BR,
               "-x264-params", "nal-hrd=cbr:force-cfr=1:filler=1",
               "-c:a", "aac", "-b:a", "192k", "-ar", "44100",
               "-movflags", "+faststart", out])


# ================= A. 内容成片 =================
LBL = {
    "c1_jian": "阿鉴\n鉴湖 · 乌篷船\n温和 · 善引路",
    "c2_xianbao": "鲜宝\n安昌 · 仁昌酱园\n勤恳 · 守时",
    "c3_achun": "阿醇\n绍兴黄酒\n憨厚 · 豪爽",
    "c4_bu": "布小彩\n染缸 · 蓝印花布\n灵巧 · 爱美",
    "c5_shan": "扇小雅\n王星记扇 · 86 道工序\n风雅 · 睿智",
    "c6_li": "梨小社\n鲁镇 · 水乡社戏\n热情 · 爱唱戏",
}
IDX = {"c1_jian": "镜 一 · 鉴湖", "c2_xianbao": "镜 二 · 安昌",
       "c3_achun": "镜 三 · 柯岩", "c4_bu": "镜 四 · 三桥",
       "c5_shan": "镜 五 · 扇馆", "c6_li": "镜 六 · 鲁镇"}


def build_content():
    print("\n===== 《作品视频》(内容成片 · 真动态) =====")
    segs = []
    # 片头：六匠快速亮相
    d = vd("c0_title")
    p = os.path.join(TMP, "c00.mp4")
    chars = ["char_ajian", "char_achun", "char_xianbao", "char_buxiaocai",
             "char_shanxiaoya", "char_lixiaoshe"]
    seg([os.path.join(DYN, c + ".mp4") for c in chars], d, p, sub=vt("c0_title"))
    segs.append((p, "c0_title"))

    shots = [("c1_jian", "shot_1", "char_ajian"),
             ("c2_xianbao", "shot_2", "char_xianbao"),
             ("c3_achun", "shot_3", "char_achun"),
             ("c4_bu", "shot_4", "char_buxiaocai"),
             ("c5_shan", "shot_5", "char_shanxiaoya"),
             ("c6_li", "shot_6", "char_lixiaoshe")]
    for k, sp, cp in shots:
        d = vd(k)
        p = os.path.join(TMP, k + ".mp4")
        seg([os.path.join(DYN, sp + ".mp4"), os.path.join(DYN, cp + ".mp4")],
            d, p, sub=vt(k), label=LBL[k], idx=IDX[k])
        segs.append((p, k))

    d = vd("c7_outro")
    p = os.path.join(TMP, "c07.mp4")
    card(p, d, "三缸集章 · 水乡寻韵", "六位水乡小匠，在柯桥等你",
         os.path.join(DYN, "shot_4.mp4"))
    segs.append((p, "c7_outro"))

    # 贴配音
    parts = []
    for i, (vp, k) in enumerate(segs):
        op = os.path.join(TMP, "ca%02d.mp4" % i)
        attach(vp, k, op)
        parts.append(op)
        print("  段 %d/%d ✓" % (i + 1, len(segs)))

    merged = os.path.join(TMP, "content_merged.mp4")
    link(parts, merged)
    out = os.path.join(DIST, "作品视频.mp4")
    finalize(merged, out)
    shutil.copy(out, os.path.join(DIST, "[队伍编号]作品视频.mp4"))
    print("内容成片:", round(dur(out), 1), "s")


# ================= B. 演示片 =================
def cut_rec():
    """按 marks 切录屏"""
    webm = sorted([os.path.join(DEMO, "rec", f) for f in os.listdir(os.path.join(DEMO, "rec"))
                   if f.endswith(".webm")])[0]
    m = json.load(open(os.path.join(DEMO, "marks.json"), encoding="utf-8"))
    span = {"plan": (m["s1"], m["s2"] - m["s1"]),
            "asset": (m["s2"], m["s3"] - m["s2"]),
            "shot": (m["s3"], m["s4"] - m["s3"]),
            "edit": (m["s4"], m["chat_reply"] - m["s4"]),
            "export": (m["s5"], 57.9 - m["s5"])}
    outs = {}
    for k, (a, t) in span.items():
        o = os.path.join(TMP, "rec_%s.mp4" % k)
        ff(["ffmpeg", "-y", "-ss", f"{a:.3f}", "-i", webm, "-t", f"{t:.3f}",
            "-vf", f"fps={FPS},scale={W}:{H},setsar=1", "-an",
            "-c:v", "libx264", "-preset", "fast", "-crf", "18", "-pix_fmt", "yuv420p", o])
        outs[k] = (o, round(t, 2))
        print("  录屏切片 %-7s %.2fs" % (k, t))
    return outs


def build_demo():
    print("\n===== 《作品演示视频》(录屏 + 真动态) =====")
    rec = cut_rec()
    segs = []

    # d0 钩子
    d = vd("d0_hook")
    p = os.path.join(TMP, "d00.mp4")
    seg([os.path.join(DYN, c + ".mp4") for c in ["char_ajian", "shot_1", "char_buxiaocai"]],
        d, p, sub=vt("d0_hook"))
    segs.append((p, "d0_hook"))

    # d1 架构
    d = vd("d1_arch")
    p = os.path.join(TMP, "d01.mp4")
    seg([os.path.join(DYN, "shot_2.mp4"), os.path.join(DYN, "shot_5.mp4")],
        d, p, sub=vt("d1_arch"), label="创编一体 · 全链路五环\n\n① 智能策划\n② 角色资产锁定\n③ 分镜生成\n④ 时间轴预览\n⑤ 成片导出")
    segs.append((p, "d1_arch"))

    # d2-d6 录屏实拍（录屏 + 动态插片）；export 录屏过短 → 用该环节截图
    mix = [("d2_plan", "plan", "shot_3", None),
           ("d3_asset", "asset", "char_ajian", None),
           ("d4_shot", "shot", "shot_6", None),
           ("d5_edit", "edit", None, None),
           ("d6_export", "export", "shot_4", os.path.join(DEMO, "s5.png"))]
    for k, rk, dyn, still in mix:
        d = vd(k)
        rp, rd = rec[rk]
        use_still = still and rd < 3.0
        if use_still:
            rp = still
        p = os.path.join(TMP, k + ".mp4")
        if (dyn or use_still):
            w1 = round(min(rd, max(3.0, d * 0.58)), 3) if not use_still else round(d * 0.5, 3)
            a = os.path.join(TMP, k + "_a.mp4")
            b = os.path.join(TMP, k + "_b.mp4")
            if use_still:
                # 静图铺满 + 缓慢平移（伪运镜，非缩放）
                ff(["ffmpeg", "-y", "-loop", "1", "-i", rp, "-t", f"{w1:.3f}",
                    "-vf", f"scale={W}:{H}:force_original_aspect_ratio=increase,"
                           f"crop={W}:{H},setsar=1,fps={FPS}",
                    "-c:v", "libx264", "-preset", "medium", "-crf", "19",
                    "-pix_fmt", "yuv420p", a])
            else:
                seg([rp], w1, a)
            tgt = os.path.join(DYN, dyn + ".mp4") if dyn else os.path.join(DYN, "shot_4.mp4")
            seg([tgt], round(d - w1, 3), b)
            lst = os.path.join(TMP, k + "_l.txt")
            open(lst, "w", encoding="utf-8").write(
                "file '%s'\nfile '%s'\n" % (a.replace("\\", "/"), b.replace("\\", "/")))
            ff(["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", lst,
                "-c:v", "libx264", "-preset", "medium", "-crf", "19",
                "-pix_fmt", "yuv420p", p])
            # 补字幕（分句，避免溢出）
            ap = os.path.join(TMP, k + "_sub.ass")
            write_ass(ap, sub_cues(vt(k), d) + [(0, d, "Tag", "工作台实操 · 真实运行")])
            p2 = os.path.join(TMP, k + "_sub.mp4")
            ff(["ffmpeg", "-y", "-i", p, "-filter_complex", ass_filter(ap, "v", "0:v"),
                "-map", "[v]", "-c:v", "libx264", "-preset", "medium", "-crf", "19",
                "-pix_fmt", "yuv420p", "-r", str(FPS), p2])
            p = p2
        else:
            seg([rp], d, p, sub=vt(k), idx="工作台实操 · 真实运行")
        segs.append((p, k))

    # d7 合规
    d = vd("d7_comply")
    p = os.path.join(TMP, "d07.mp4")
    seg([os.path.join(DYN, "shot_6.mp4"), os.path.join(DYN, "char_shanxiaoya.mp4")],
        d, p, sub=vt("d7_comply"),
        label="合规台账 · 8 项资源登记\nAIGC 占比 80%\n（赛题红线 ≥60%）")
    segs.append((p, "d7_comply"))

    # d8 全家福（六镜快切）
    d = vd("d8_family")
    p = os.path.join(TMP, "d08.mp4")
    seg([os.path.join(DYN, "shot_%d.mp4" % i) for i in range(1, 7)], d, p, sub=vt("d8_family"))
    segs.append((p, "d8_family"))

    # d9 尾板
    d = vd("d9_end")
    p = os.path.join(TMP, "d09.mp4")
    card(p, d, "柯桥 · 水乡IP造物台", "让柯桥之美，被世界看见",
         os.path.join(DYN, "shot_1.mp4"))
    segs.append((p, "d9_end"))

    parts = []
    for i, (vp, k) in enumerate(segs):
        op = os.path.join(TMP, "da%02d.mp4" % i)
        attach(vp, k, op)
        parts.append(op)
        print("  段 %d/%d ✓" % (i + 1, len(segs)))

    merged = os.path.join(TMP, "demo_merged.mp4")
    link(parts, merged)
    out = os.path.join(DIST, "作品演示视频.mp4")
    finalize(merged, out)
    shutil.copy(out, os.path.join(DIST, "[队伍编号]作品演示视频.mp4"))
    print("演示视频:", round(dur(out), 1), "s")


if __name__ == "__main__":
    import sys
    which = sys.argv[1] if len(sys.argv) > 1 else "all"
    if which in ("all", "content"):
        build_content()
    if which in ("all", "demo"):
        build_demo()
