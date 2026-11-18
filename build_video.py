#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
柯桥·水乡IP造物台 —— 作品视频合成脚本（可复现）
================================================
流程：分镜图 + TTS配音 + AI环境音 → 1080p 作品视频
  1) 用 PIL 合成每一帧（模糊背景 + 居中前景 + 字幕），中文渲染稳定
  2) 用 ffmpeg 帧+音频生成片段，再拼接、混入环境音
输出：dist/作品视频.mp4（1920×1080 · H.264 · 约45秒）

依赖：Pillow、ffmpeg（本机已安装）
"""
import os, json, subprocess, sys
from PIL import Image, ImageFilter, ImageDraw, ImageFont

ROOT = os.path.dirname(os.path.abspath(__file__))
GEN = os.path.join(ROOT, "assets", "generated")
WORK = os.path.join(ROOT, "video_work")
DIST = os.path.join(ROOT, "dist")
FRAMES = os.path.join(WORK, "frames")
os.makedirs(FRAMES, exist_ok=True)
os.makedirs(DIST, exist_ok=True)

W, H = 1920, 1080
FONT_BOLD = "C:/Windows/Fonts/msyhbd.ttc"
FONT_REG = "C:/Windows/Fonts/msyh.ttc"


def font(path, size):
    try:
        return ImageFont.truetype(path, size)
    except Exception:
        return ImageFont.load_default()


def cover(im, w, h):
    r = max(w / im.width, h / im.height)
    im2 = im.resize((max(1, int(im.width * r + 1)), max(1, int(im.height * r + 1))), Image.LANCZOS)
    x = (im2.width - w) // 2
    y = (im2.height - h) // 2
    return im2.crop((x, y, x + w, y + h))


def wrap_cjk(text, fnt, max_w, draw):
    """按像素宽度对中文文本断行"""
    lines, cur = [], ""
    for ch in text:
        if ch == "\n":
            lines.append(cur); cur = ""; continue
        if draw.textlength(cur + ch, font=fnt) <= max_w:
            cur += ch
        else:
            lines.append(cur); cur = ch
    if cur:
        lines.append(cur)
    return lines


def base_canvas(src=None):
    """生成 1920×1080 画布：模糊背景 + 居中前景"""
    if src is None:
        c = Image.new("RGB", (W, H), (18, 28, 38))
        return c, 0
    im = Image.open(src).convert("RGB")
    bg = cover(im, W, H).filter(ImageFilter.GaussianBlur(30))
    bg = Image.eval(bg, lambda v: int(v * 0.45))
    c = bg
    fg_h = 980
    fg_w = int(im.width / im.height * fg_h)
    fg = im.resize((fg_w, fg_h), Image.LANCZOS)
    c.paste(fg, ((W - fg_w) // 2, (H - fg_h) // 2 - 20))
    return c, fg_w


def draw_subtitle(d, text, y=None):
    """底部半透明字幕条 + 白字"""
    f = font(FONT_REG, 40)
    lines = wrap_cjk(text, f, W - 400, d)
    lh = 56
    box_h = lh * len(lines) + 36
    y0 = y if y is not None else H - box_h - 60
    bar = Image.new("RGBA", (W - 240, box_h), (0, 0, 0, 130))
    base = d._image
    base.paste(bar, (120, y0), bar)
    yy = y0 + 18
    for ln in lines:
        tw = d.textlength(ln, font=f)
        d.text(((W - tw) / 2, yy), ln, font=f, fill=(255, 255, 255))
        yy += lh


def make_shot_frame(idx, scene, spot, line, src):
    c, _ = base_canvas(src)
    d = ImageDraw.Draw(c)
    # 左上角镜头标签
    tag = f"镜 {idx}   {scene}"
    ft = font(FONT_BOLD, 34)
    tw = d.textlength(tag, font=ft)
    lab = Image.new("RGBA", (int(tw) + 44, 62), (46, 125, 181, 215))
    c.paste(lab, (70, 60), lab)
    d.text((92, 72), tag, font=ft, fill=(255, 255, 255))
    # 点位小字
    fs = font(FONT_REG, 24)
    d.text((70, 140), spot, font=fs, fill=(210, 230, 240))
    # 字幕
    draw_subtitle(d, line)
    p = os.path.join(FRAMES, f"shot_{idx}.png")
    c.save(p)
    return p


def make_intro_frame(sub):
    c = Image.new("RGB", (W, H), (14, 26, 36))
    # 顶部水墨渐层
    top = Image.new("RGB", (W, 300), (20, 40, 56))
    c.paste(top, (0, 0))
    # 六位角色立绘 3列2行
    ids = ["ajian", "achun", "xianbao", "buxiaocai", "shanxiaoya", "lixiaoshe"]
    cw, ch = 250, 330
    gapx, gapy = 46, 34
    total_w = 3 * cw + 2 * gapx
    x0 = (W - total_w) // 2
    y0 = 300
    for i, cid in enumerate(ids):
        fp = os.path.join(GEN, f"char_{cid}.jpg")
        if not os.path.exists(fp):
            continue
        im = Image.open(fp).convert("RGB").resize((cw, ch), Image.LANCZOS)
        r, col = divmod(i, 3)
        c.paste(im, (x0 + col * (cw + gapx), y0 + r * (ch + gapy)))
    d = ImageDraw.Draw(c)
    # 标题
    ft = font(FONT_BOLD, 92)
    title = "笛 里 · 柯 桥"
    tw = d.textlength(title, font=ft)
    d.text(((W - tw) / 2, 70), title, font=ft, fill=(240, 214, 150))
    fs = font(FONT_REG, 34)
    st = "三缸奇缘 · 水乡小匠 —— 原创文旅IP形象"
    sw = d.textlength(st, font=fs)
    d.text(((W - sw) / 2, 185), st, font=fs, fill=(190, 214, 228))
    # 旁白字幕
    draw_subtitle(d, sub)
    p = os.path.join(FRAMES, "intro.png")
    c.save(p)
    return p


def make_outro_frame():
    c, _ = base_canvas(os.path.join(GEN, "shot_1.jpg"))
    d = ImageDraw.Draw(c)
    # 中部半透明衬底，提升文字可读性
    panel = Image.new("RGBA", (W - 300, 300), (10, 22, 32, 170))
    c.paste(panel, (150, 360), panel)
    ft = font(FONT_BOLD, 68)
    t1 = "三缸集章 · 水乡寻韵"
    tw = d.textlength(t1, font=ft)
    d.text(((W - tw) / 2, 400), t1, font=ft, fill=(255, 232, 170))
    fs = font(FONT_REG, 42)
    t2 = "六位水乡小匠，在柯桥等你"
    sw = d.textlength(t2, font=fs)
    d.text(((W - sw) / 2, 505), t2, font=fs, fill=(238, 246, 252))
    fs2 = font(FONT_REG, 30)
    t3 = "柯桥·水乡IP造物台 · 数字创意与AIGC应用赛道"
    sw3 = d.textlength(t3, font=fs2)
    d.text(((W - sw3) / 2, 575), t3, font=fs2, fill=(170, 200, 218))
    p = os.path.join(FRAMES, "outro.png")
    c.save(p)
    return p


def ff(cmd):
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        print("FFMPEG ERR:", " ".join(cmd[:8]), "...\n", r.stderr[-800:])
    return r.returncode == 0


def main():
    P = json.load(open(os.path.join(WORK, "plan.json"), encoding="utf-8"))
    segs = []

    # 片头（配开场白）
    intro_png = make_intro_frame(P["intro_sub"])
    segs.append((intro_png, "vo_title.mp3", P["intro_dur"]))

    # 六个分镜
    for s in P["shots"]:
        png = make_shot_frame(s["no"], s["scene"], s["spot"], s["line"], os.path.join(GEN, f"shot_{s['no']}.jpg"))
        segs.append((png, s["vo"], s["dur"]))

    # 尾板
    outro_png = make_outro_frame()
    segs.append((outro_png, None, 2.6))

    # 生成每个片段
    parts = []
    for i, (png, vo, dur) in enumerate(segs):
        out = os.path.join(WORK, f"part_{i:02d}.mp4")
        if vo:
            cmd = ["ffmpeg", "-y", "-loop", "1", "-i", png,
                   "-i", os.path.join(WORK, vo),
                   "-t", f"{dur}",
                   "-vf", "scale=1920:1080,format=yuv420p",
                   "-c:v", "libx264", "-preset", "medium", "-crf", "20",
                   "-c:a", "aac", "-b:a", "192k", "-ar", "44100",
                   "-shortest", out]
        else:
            cmd = ["ffmpeg", "-y",
                   "-f", "lavfi", "-i", "anullsrc=r=44100:cl=stereo",
                   "-loop", "1", "-i", png, "-t", f"{dur}",
                   "-vf", "scale=1920:1080,format=yuv420p",
                   "-c:v", "libx264", "-preset", "medium", "-crf", "20",
                   "-c:a", "aac", "-b:a", "192k",
                   "-shortest", out]
        if ff(cmd):
            parts.append(out)
            print("片段完成:", os.path.basename(out))

    # 拼接
    listfile = os.path.join(WORK, "concat.txt")
    with open(listfile, "w", encoding="utf-8") as f:
        for p in parts:
            f.write(f"file '{p.replace(chr(92), '/')}'\n")
    merged = os.path.join(WORK, "merged.mp4")
    ff(["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", listfile, "-c", "copy", merged])

    # 环境音：4条10s首尾相接 → 混入（低音量）
    amb = os.path.join(WORK, "bed.wav")
    ff(["ffmpeg", "-y",
        "-i", os.path.join(WORK, "amb_0.mp3"), "-i", os.path.join(WORK, "amb_1.mp3"),
        "-i", os.path.join(WORK, "amb_2.mp3"), "-i", os.path.join(WORK, "amb_3.mp3"),
        "-filter_complex", "[0][1][2][3]concat=n=4:v=0:a=1[bed]",
        "-map", "[bed]", amb])

    final = os.path.join(DIST, "作品视频.mp4")
    ff(["ffmpeg", "-y", "-i", merged, "-stream_loop", "-1", "-i", amb,
        "-filter_complex",
        "[1:a]volume=0.16,atrim=0:60[bg];[0:a][bg]amix=inputs=2:duration=first:dropout_transition=0[a]",
        "-map", "0:v", "-map", "[a]",
        "-c:v", "copy", "-c:a", "aac", "-b:a", "192k",
        "-movflags", "+faststart", "-shortest", final])
    print("成片:", final)


if __name__ == "__main__":
    main()
