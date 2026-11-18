#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
柯桥·水乡IP造物台 —— 作品演示视频合成（v3 · 专业版）
=====================================================
设计逻辑（对齐 SaaS / AI 产品演示片的通行做法）：
  钩子 → 方案登场 → 全流程（真实录屏 × 动效插片交替）→ 成果 → 尾板
  · 画面：真实录屏证明"系统跑得通"；AI 生成图配 Ken Burns 运镜提供节奏
  · 版式：UI 镜头走"窗口内嵌"版式（上方章节徽标、下方字幕）；
          影像镜头满幅，配标题/角色卡
  · 字幕：白字 + 深色描边（无黑框），底部居中
  · 转场：交叉溶解；底部常驻进度条
  · 音频：水乡环境音底噪（无配音）

素材：video_work/demo/（Playwright 录屏 + 截图 + marks.json）
      assets/generated/（6 角色立绘 + 6 分镜图）
输出：video_work/promo/master.mp4 → dist/作品演示视频.mp4

依赖：Pillow、ffmpeg
"""
import os, json, glob, subprocess, shutil, math
from PIL import Image, ImageDraw, ImageFont, ImageFilter

ROOT = os.path.dirname(os.path.abspath(__file__))
GEN = os.path.join(ROOT, "assets", "generated")
DEMO = os.path.join(ROOT, "video_work", "demo")
WORK = os.path.join(ROOT, "video_work", "promo")
DIST = os.path.join(ROOT, "dist")
for p in (WORK, DIST):
    os.makedirs(p, exist_ok=True)

W, H, FPS = 1920, 1080, 30
BW, BH = 2400, 1350                    # 静帧基底画布（为运镜留余量）

FB = "C:/Windows/Fonts/msyhbd.ttc"      # 微软雅黑 Bold
FR = "C:/Windows/Fonts/Alibaba_PuHuiTi.ttf"   # 阿里巴巴普惠体

INK = (11, 20, 29)
INK2 = (17, 31, 44)
GOLD = (226, 183, 96)
CYAN = (93, 180, 214)
RICE = (240, 246, 249)
MUTED = (156, 186, 204)

# UI 镜头窗口几何（16:9 = 1624×914）
WIN_X, WIN_Y, WIN_W, WIN_H = 148, 84, 1624, 914

_font_cache = {}


def font(path, size):
    key = (path, size)
    if key not in _font_cache:
        try:
            _font_cache[key] = ImageFont.truetype(path, size)
        except Exception:
            _font_cache[key] = ImageFont.load_default()
    return _font_cache[key]


def ff(cmd, quiet=True):
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        print("FFMPEG ERR:", " ".join(str(c) for c in cmd[:10]))
        print(r.stderr[-900:])
    return r.returncode == 0


def dur_of(path):
    r = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                        "-of", "default=nw=1:nk=1", path], capture_output=True, text=True)
    try:
        return float(r.stdout.strip())
    except Exception:
        return 0.0


# ---------------------------------------------------------------- 图形工具
def cover(im, w, h, zoom=1.0):
    r = max(w / im.width, h / im.height) * zoom
    im2 = im.resize((max(1, int(im.width * r + 1)), max(1, int(im.height * r + 1))), Image.LANCZOS)
    x = (im2.width - w) // 2
    y = (im2.height - h) // 2
    return im2.crop((x, y, x + w, y + h))


def wrap_cjk(text, fnt, max_w, draw):
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


def pill(d, x, y, text, fnt, fg=RICE, bg=(10, 20, 30, 165), border=GOLD, pad=20, h=44, r=None):
    """胶囊徽标（返回右边界 x）"""
    tw = d.textlength(text, font=fnt)
    r = h // 2 if r is None else r
    d.rounded_rectangle([x, y, x + tw + pad * 2, y + h], radius=r, fill=bg,
                        outline=border + (190,) if len(border) == 3 else border, width=2)
    d.text((x + pad, y + h / 2), text, font=fnt, fill=fg, anchor="lm")
    return x + tw + pad * 2


def subtitle(d, text, y=H - 128, max_w=1560, size=41):
    f = font(FR, size)
    lines = wrap_cjk(text, f, max_w, d)
    lh = int(size * 1.32)
    for i, ln in enumerate(lines):
        d.text((W / 2, y + i * lh), ln, font=f, fill=(255, 255, 255, 255),
               anchor="ma", stroke_width=4, stroke_fill=(9, 18, 26, 238))


def brand_mark(d, x, y):
    f = font(FB, 24)
    pill(d, x, y, "柯桥 · 水乡IP造物台", f, fg=(238, 245, 249, 240),
         bg=(9, 18, 26, 150), border=(226, 183, 96, 165), h=42)


# ---------------------------------------------------------------- 底图
def base_full(img_path, dark=0.42, blur=0, focus=None, zoom=1.0):
    """满幅底图（影像镜头）"""
    im = Image.open(img_path).convert("RGB")
    if focus:
        x, y, w, h = focus
        im = im.crop((x, y, x + w, y + h))
    c = cover(im, BW, BH, zoom)
    if blur:
        c = c.filter(ImageFilter.GaussianBlur(blur))
    if dark != 1.0:
        c = Image.eval(c, lambda v: max(0, min(255, int(v * dark))))
    return c


def _rmask(size, r):
    m = Image.new("L", size, 0)
    ImageDraw.Draw(m).rounded_rectangle([0, 0, size[0] - 1, size[1] - 1], radius=r, fill=255)
    return m


def base_char(img_path):
    """角色卡底图：模糊背景 + 右侧立绘（圆角卡片 + 投影）"""
    im = Image.open(img_path).convert("RGB")
    bg = cover(im, BW, BH).filter(ImageFilter.GaussianBlur(46))
    bg = Image.eval(bg, lambda v: int(v * 0.40))
    c = bg
    fh = 1200
    fw = int(im.width / im.height * fh)
    fg = im.resize((fw, fh), Image.LANCZOS)
    x = BW - fw - 235
    y = (BH - fh) // 2 + 18
    sh = Image.new("RGBA", (fw + 130, fh + 130), (0, 0, 0, 0))
    ImageDraw.Draw(sh).rounded_rectangle([65, 65, 65 + fw, 65 + fh], radius=28, fill=(0, 0, 0, 185))
    sh = sh.filter(ImageFilter.GaussianBlur(32))
    c.paste(sh.convert("RGB"), (x - 65, y - 65), sh.split()[3])
    c.paste(fg, (x, y), _rmask((fw, fh), 28))
    return c


def base_shot(img_path):
    """分镜卡底图：模糊背景 + 居中作品图（圆角卡片 + 投影）"""
    im = Image.open(img_path).convert("RGB")
    bg = cover(im, BW, BH).filter(ImageFilter.GaussianBlur(52))
    bg = Image.eval(bg, lambda v: int(v * 0.34))
    c = bg
    fh = 1140
    fw = int(im.width / im.height * fh)
    fg = im.resize((fw, fh), Image.LANCZOS)
    x = (BW - fw) // 2 + 265
    y = (BH - fh) // 2
    sh = Image.new("RGBA", (fw + 130, fh + 130), (0, 0, 0, 0))
    ImageDraw.Draw(sh).rounded_rectangle([65, 65, 65 + fw, 65 + fh], radius=28, fill=(0, 0, 0, 190))
    sh = sh.filter(ImageFilter.GaussianBlur(32))
    c.paste(sh.convert("RGB"), (x - 65, y - 65), sh.split()[3])
    c.paste(fg, (x, y), _rmask((fw, fh), 28))
    return c


def grad_bg():
    """深色渐变底（UI 镜头背景）"""
    c = Image.new("RGB", (W, H), INK)
    d = ImageDraw.Draw(c)
    for y in range(H):
        t = y / H
        r = int(INK[0] + (INK2[0] - INK[0]) * t)
        g = int(INK[1] + (INK2[1] - INK[1]) * t)
        b = int(INK[2] + (INK2[2] - INK[2]) * t)
        d.line([(0, y), (W, y)], fill=(r, g, b))
    # 窗口后的柔光
    gl = Image.new("RGB", (W, H), (0, 0, 0))
    gd = ImageDraw.Draw(gl)
    gd.rectangle([WIN_X - 26, WIN_Y - 26, WIN_X + WIN_W + 26, WIN_Y + WIN_H + 26], fill=(46, 92, 120))
    gl = gl.filter(ImageFilter.GaussianBlur(64))
    return Image.blend(c, Image.blend(c, gl, 0.30), 0.5)


# ---------------------------------------------------------------- 叠加层
def make_overlay(chapter=None, sub=None, title=None, kicker=None, tag=None,
                 info=None, ui=False, shot_tag=None):
    ov = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(ov)

    if ui:
        # 窗口描边
        d.rounded_rectangle([WIN_X - 1, WIN_Y - 1, WIN_X + WIN_W + 1, WIN_Y + WIN_H + 1],
                            radius=13, outline=(150, 200, 224, 120), width=2)
        if chapter:
            pill(d, WIN_X, 22, chapter, font(FB, 25), fg=(255, 255, 255, 245),
                 bg=(226, 183, 96, 232), border=(0, 0, 0, 0), h=46)
        bf = font(FB, 22)
        bt = "柯桥 · 水乡IP造物台"
        tw = d.textlength(bt, font=bf)
        d.text((WIN_X + WIN_W - tw, 30), bt, font=bf, fill=(214, 232, 242, 210),
               stroke_width=3, stroke_fill=(9, 18, 26, 200))
        if sub:
            subtitle(d, sub, y=1006, max_w=WIN_W, size=38)
        return ov

    # 满幅影像镜头
    brand_mark(d, 54, 42)
    if chapter:
        f = font(FB, 25)
        tw = d.textlength(chapter, font=f)
        pill(d, W - 54 - (tw + 40), 42, chapter, f, fg=(255, 255, 255, 246),
             bg=(226, 183, 96, 232), border=(0, 0, 0, 0), h=42)

    if title:
        if kicker:
            fk = font(FR, 30)
            d.text((W / 2, 332), kicker, font=fk, fill=(228, 200, 140, 240),
                   anchor="ma", stroke_width=3, stroke_fill=(9, 18, 26, 210))
        ft = font(FB, 104)
        d.text((W / 2, 452), title, font=ft, fill=(250, 252, 254, 255),
               anchor="mm", stroke_width=7, stroke_fill=(8, 16, 24, 235))
        d.rounded_rectangle([W / 2 - 78, 540, W / 2 + 78, 546], radius=3, fill=GOLD + (235,))
        if tag:
            fs = font(FR, 40)
            d.text((W / 2, 606), tag, font=fs, fill=(226, 238, 246, 245),
                   anchor="ma", stroke_width=4, stroke_fill=(9, 18, 26, 215))

    if info:
        col = info.get("color", "#2E7DB5")
        rgb = tuple(int(col[i:i + 2], 16) for i in (1, 3, 5))
        d.rounded_rectangle([150, 330, 158, 560], radius=4, fill=rgb + (240,))
        d.text((196, 330), info["name"], font=font(FB, 88), fill=(250, 252, 254, 255),
               stroke_width=6, stroke_fill=(8, 16, 24, 230))
        d.text((200, 456), info["element"], font=font(FR, 34), fill=rgb + (255,),
               stroke_width=4, stroke_fill=(8, 16, 24, 215))
        d.text((200, 516), info["persona"], font=font(FR, 31), fill=(222, 236, 244, 235),
               stroke_width=4, stroke_fill=(8, 16, 24, 205))
        pill(d, 200, 578, info.get("symbol", ""), font(FR, 26), fg=(255, 255, 255, 240),
             bg=(10, 22, 32, 170), border=rgb + (200,), h=44)

    if shot_tag:
        no, scene, spot = shot_tag
        f1 = font(FB, 46)
        f2 = font(FR, 28)
        d.text((132, 300), no, font=f1, fill=(240, 200, 120, 255),
               stroke_width=6, stroke_fill=(8, 16, 24, 230))
        d.text((132, 372), scene, font=font(FB, 56), fill=(250, 252, 254, 255),
               stroke_width=6, stroke_fill=(8, 16, 24, 230))
        d.text((136, 462), spot, font=f2, fill=(206, 228, 240, 235),
               stroke_width=4, stroke_fill=(8, 16, 24, 210))

    if sub:
        subtitle(d, sub)
    return ov


def make_flow_overlay(steps):
    ov = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(ov)
    brand_mark(d, 54, 42)
    f = font(FB, 25)
    tw = d.textlength("全链路 · 创编一体", font=f)
    pill(d, W - 54 - (tw + 40), 42, "全链路 · 创编一体", f, fg=(255, 255, 255, 246),
         bg=(226, 183, 96, 232), border=(0, 0, 0, 0), h=42)

    fd = font(FB, 30)
    d.text((W / 2, 210), "AI 驱动的全链路数字创意体系", font=font(FR, 30), fill=(226, 200, 140, 245),
           anchor="ma", stroke_width=3, stroke_fill=(9, 18, 26, 215))
    d.text((W / 2, 288), "五个环节 · 一个数据源 · 一条闭环", font=font(FB, 62), fill=(250, 252, 254, 255),
           anchor="mm", stroke_width=6, stroke_fill=(8, 16, 24, 235))

    n = len(steps)
    pw, gap = 286, 62
    total = n * pw + (n - 1) * gap
    x = (W - total) / 2
    y = 470
    for i, s in enumerate(steps):
        d.rounded_rectangle([x, y, x + pw, y + 168], radius=18,
                            fill=(14, 30, 43, 200), outline=CYAN + (170,), width=2)
        d.ellipse([x + 26, y + 24, x + 74, y + 72], fill=GOLD + (238,))
        d.text((x + 50, y + 48), str(i + 1), font=font(FB, 26), fill=(20, 30, 40, 255), anchor="mm")
        d.text((x + pw / 2, y + 118), s, font=font(FB, 36), fill=(246, 250, 252, 255),
               anchor="mm", stroke_width=3, stroke_fill=(8, 16, 24, 200))
        if i < n - 1:
            cx = x + pw + gap / 2
            d.polygon([(cx - 11, y + 70), (cx + 11, y + 84), (cx - 11, y + 98)],
                      fill=(226, 183, 96, 235))
        x += pw + gap

    d.text((W / 2, 700), "策划产出「结构化项目模型」——下游全部消费它，数据不断链",
           font=font(FR, 32), fill=(216, 234, 244, 240), anchor="ma",
           stroke_width=4, stroke_fill=(9, 18, 26, 210))
    subtitle(d, "五环贯通 · 一次策划，驱动生成、编辑、预览与导出全流程")
    return ov


# ---------------------------------------------------------------- 运镜
def kb_filter(mode, dur):
    N = max(2, int(dur * FPS))
    cx, cy = "iw/2-(iw/zoom/2)", "ih/2-(ih/zoom/2)"
    if mode == "in":
        z, x, y = f"min(zoom+{(1.20-1)/N:.6f},1.20)", cx, cy
    elif mode == "out":
        z, x, y = f"if(eq(on,0),1.20,max(zoom-{(1.20-1)/N:.6f},1.0))", cx, cy
    elif mode == "right":
        z, x, y = "1.10", f"(iw-iw/zoom)*on/{N}", cy
    elif mode == "left":
        z, x, y = "1.10", f"(iw-iw/zoom)*(1-on/{N})", cy
    elif mode == "up":
        z, x, y = "1.10", cx, f"(ih-ih/zoom)*(1-on/{N})"
    elif mode == "down":
        z, x, y = "1.10", cx, f"(ih-ih/zoom)*on/{N}"
    else:
        z, x, y = "1.0", cx, cy
    return f"zoompan=z='{z}':x='{x}':y='{y}':d={N + 8}:s={W}x{H}:fps={FPS}"


# ---------------------------------------------------------------- 片段生成
def clip_cinematic(idx, base, ov, d, mode):
    """满幅影像镜头"""
    bp = os.path.join(WORK, f"b{idx:02d}.png")
    op = os.path.join(WORK, f"o{idx:02d}.png")
    base.save(bp); ov.save(op)
    out = os.path.join(WORK, f"c{idx:02d}.mp4")
    fc = (f"[0:v]{kb_filter(mode, d)}[bg];"
          f"[1:v]format=rgba[ov];[bg][ov]overlay=0:0:format=auto,format=yuv420p[v]")
    ff(["ffmpeg", "-y", "-framerate", str(FPS), "-loop", "1", "-i", bp,
        "-loop", "1", "-i", op, "-filter_complex", fc, "-map", "[v]",
        "-t", f"{d:.3f}", "-an", "-c:v", "libx264", "-preset", "medium", "-crf", "18",
        "-pix_fmt", "yuv420p", "-r", str(FPS), out])
    return out


_UI_BG = None


def clip_ui(idx, base, ov, d, mode=None, seg=None):
    """UI 镜头：窗口内嵌真实界面/截图"""
    global _UI_BG
    if _UI_BG is None:
        _UI_BG = grad_bg()
        _UI_BG.save(os.path.join(WORK, "ui_bg.png"))
    op = os.path.join(WORK, f"o{idx:02d}.png")
    ov.save(op)
    out = os.path.join(WORK, f"c{idx:02d}.mp4")
    bgp = os.path.join(WORK, "ui_bg.png")

    if seg:      # 真实录屏
        rec, a, b = seg
        fc = (f"[0:v]setpts=PTS-STARTPTS,scale={WIN_W}:{WIN_H},setsar=1,fps={FPS}[sc];"
              f"[1:v]scale={W}:{H}[bg];"
              f"[bg][sc]overlay={WIN_X}:{WIN_Y}:eof_action=repeat[w];"
              f"[2:v]format=rgba[ov];[w][ov]overlay=0:0:format=auto,format=yuv420p[v]")
        ff(["ffmpeg", "-y", "-ss", f"{max(0,a):.3f}", "-i", rec,
            "-loop", "1", "-i", bgp, "-loop", "1", "-i", op,
            "-filter_complex", fc, "-map", "[v]", "-t", f"{d:.3f}", "-an",
            "-c:v", "libx264", "-preset", "medium", "-crf", "18",
            "-pix_fmt", "yuv420p", "-r", str(FPS), out])
    else:        # 截图 + 运镜
        bp = os.path.join(WORK, f"b{idx:02d}.png")
        base.save(bp)
        kf = kb_filter(mode or "in", d).replace(f"s={W}x{H}", f"s={WIN_W}x{WIN_H}")
        fc = (f"[0:v]{kf}[sc];[1:v]scale={W}:{H}[bg];"
              f"[bg][sc]overlay={WIN_X}:{WIN_Y}[w];"
              f"[2:v]format=rgba[ov];[w][ov]overlay=0:0:format=auto,format=yuv420p[v]")
        ff(["ffmpeg", "-y", "-framerate", str(FPS), "-loop", "1", "-i", bp,
            "-loop", "1", "-i", bgp, "-loop", "1", "-i", op,
            "-filter_complex", fc, "-map", "[v]", "-t", f"{d:.3f}", "-an",
            "-c:v", "libx264", "-preset", "medium", "-crf", "18",
            "-pix_fmt", "yuv420p", "-r", str(FPS), out])
    return out


# ---------------------------------------------------------------- 主流程
def main():
    marks = json.load(open(os.path.join(DEMO, "marks.json"), encoding="utf-8"))
    rec = sorted(glob.glob(os.path.join(DEMO, "rec", "*.webm")))[-1]
    print("录屏:", os.path.basename(rec), "| 时长", round(dur_of(rec), 1))

    s1, s1s, s2, s3, s4 = marks["s1"], marks["s1_scroll"], marks["s2"], marks["s3"], marks["s4"]
    cht, chr_, s5, endp = marks["chat_type"], marks["chat_reply"], marks["s5"], marks["_end_perf"]

    SEG = {
        "s1": (0.6, max(6.0, s2 - 4.6)),
        "s2": (s2 - 4.4, s3 - 4.6),
        "s3": (s3 - 4.4, s4 - 4.6),
        "s4": (s4 - 4.2, cht - 1.6),
        "chat": (cht - 1.0, min(chr_ + 2.6, endp - 2.0)),
        "s5": (s5 - 4.2, endp - 0.4),
    }
    for k, v in SEG.items():
        print(f"  段[{k}] {v[0]:.1f}→{v[1]:.1f}  ({v[1]-v[0]:.1f}s)")

    def shot_img(n):
        return os.path.join(GEN, f"shot_{n}.jpg")

    def char_img(cid):
        return os.path.join(GEN, f"char_{cid}.jpg")

    def ui_shot(name):
        return os.path.join(DEMO, f"{name}.png")

    CHARS = [
        ("ajian", "阿鉴", "鉴湖 · 乌篷船", "温和 · 善引路 · 慢生活", "鉴湖水纹", "#2E7DB5"),
        ("achun", "阿醇", "绍兴黄酒酿制技艺（国家级非遗）", "憨厚 · 豪爽 · 热心肠", "酒坛", "#C8892B"),
        ("xianbao", "鲜宝", "仁昌酱园母子酱油（省级非遗） · 安昌古镇", "勤恳 · 守时 · 爱「晒」", "酱缸", "#8C4A2F"),
        ("buxiaocai", "布小彩", "染缸 · 蓝印花布 · 中国轻纺城", "灵巧 · 爱美 · 会变装", "蓝印花布", "#2F5D8C"),
        ("shanxiaoya", "扇小雅", "王星记扇（国家级非遗 · 86 道工序）", "风雅 · 睿智 · 爱丹青", "折扇", "#2F6B4F"),
        ("lixiaoshe", "梨小社", "鲁镇 · 水乡社戏 · 越剧", "热情 · 爱唱演 · 人来疯", "水袖", "#C0392B"),
    ]
    SHOTS = [
        (1, "鉴湖晨雾", "鉴湖 · 古纤道", "大远景 · 缓慢推近", "桨声欸乃，柯桥的水，醒了。"),
        (2, "安昌酱香", "安昌古镇 · 仁昌酱园", "中景 · 跟拍", "晒足一百八十天，才是安昌的老味道。"),
        (3, "柯岩揽胜", "柯岩 · 采石遗迹", "全景 · 上升", "鉴湖水酿的酒，配得上这一方山水！"),
        (4, "三桥夜泊", "柯桥古镇 · 三桥四水", "近景 · 缓摇", "一缸靛蓝，染出会跳舞的颜色。"),
        (5, "扇面丹青", "王星记扇馆 · 柯桥非遗馆", "特写 · 推近", "一扇之间，装得下整条鉴湖。"),
        (6, "社戏台上", "鲁镇 · 社戏台", "中景 · 环绕", "锣鼓一响，柯桥的故事就开演啦！"),
    ]

    jobs = []      # (kind, payload, dur, overlap_to_prev)

    # ① 钩子
    jobs.append(("cin", dict(base=base_full(shot_img(1), dark=0.52),
                             ov=make_overlay(kicker="数字创意与 AIGC 应用赛道",
                                             title="柯桥 · 水乡IP造物台",
                                             tag="支持多模态的全链路数字创意工作台",
                                             sub="一件原创文旅 IP · 一个可运行的系统 · 一条完整创作链路"),
                             mode="in"), 6.6, 0))

    # ② 方案：五环
    jobs.append(("cin", dict(base=base_full(shot_img(2), dark=0.34, blur=34),
                             ov=make_flow_overlay(["智能策划", "多模态生成", "智能编辑", "实时预览", "一键导出"]),
                             mode="out"), 7.4, 0.6))

    # ③ 环1 智能策划（真实录屏 + 细节放大）
    jobs.append(("ui", dict(base=None, ov=make_overlay(chapter="01 · 智能策划", ui=True,
                                                       sub="输入一句创意，AI 扩写为结构化项目"),
                            seg=(rec, *SEG["s1"])), 9.4, 0.6))
    jobs.append(("ui", dict(base=base_full(ui_shot("s1_top"), focus=(300, 250, 1000, 560)),
                            ov=make_overlay(chapter="01 · 智能策划", ui=True,
                                            sub="产出：世界观设定 + 6 位角色 + 6 个分镜脚本"),
                            mode="right"), 8.2, 0.6))

    # ④ 环2 角色资产（主角色详卡 + 六位轮播）
    jobs.append(("cin", dict(base=base_char(char_img("ajian")),
                             ov=make_overlay(chapter="02 · 角色资产锁定",
                                             info=dict(name="阿鉴", element="鉴湖 · 乌篷船",
                                                       persona="温和 · 善引路 · 慢生活",
                                                       symbol="鉴湖水纹", color="#2E7DB5"),
                                             sub="先锁定角色种子图 —— 后续所有分镜的「脸」"),
                             mode="in"), 8.6, 0.6))
    for i, (cid, nm, el, pe, sy, col) in enumerate(CHARS):
        jobs.append(("cin", dict(base=base_char(char_img(cid)),
                                 ov=make_overlay(info=dict(name=nm, element=el, persona=pe, symbol=sy, color=col),
                                                 sub=f"「{sy}」 · 绑定柯桥非遗与地标"),
                                 mode="in" if i % 2 == 0 else "out"), 2.9, 0.30))

    # ⑤ 环3 分镜生成（录屏 + 六镜轮播）
    jobs.append(("ui", dict(base=None, ov=make_overlay(chapter="03 · 分镜生成", ui=True,
                                                       sub="每一镜自动绑定角色参考图 · 换场景不换脸"),
                            seg=(rec, *SEG["s3"])), 9.2, 0.6))
    for i, (no, sc, sp, st, dl) in enumerate(SHOTS):
        jobs.append(("cin", dict(base=base_shot(shot_img(no)),
                                 ov=make_overlay(shot_tag=(f"镜 {no}", sc, sp), sub=f"「{dl}」"),
                                 mode=["right", "left", "up", "down", "in", "out"][i % 6]), 3.4, 0.30))

    # ⑥ 环4 时间轴 + 对话式编辑
    jobs.append(("ui", dict(base=None, ov=make_overlay(chapter="04 · 时间轴预览", ui=True,
                                                       sub="按分镜顺序排成时间轴 · 逐镜可控"),
                            seg=(rec, *SEG["s4"])), 7.4, 0.6))
    jobs.append(("ui", dict(base=None, ov=make_overlay(chapter="04 · 对话式编辑", ui=True,
                                                       sub="用自然语言下指令：「把第3镜改成近景」"),
                            seg=(rec, *SEG["chat"])), 11.4, 0.6))
    jobs.append(("ui", dict(base=base_full(ui_shot("s4_chat"), focus=(980, 430, 760, 500)),
                            ov=make_overlay(chapter="04 · 对话式编辑", ui=True,
                                            sub="AI 返回修改后的分镜脚本 · 可继续追问"),
                            mode="in"), 6.6, 0.6))

    # ⑦ 环5 成片导出
    jobs.append(("ui", dict(base=None, ov=make_overlay(chapter="05 · 成片导出", ui=True,
                                                       sub="说明文档 / A3 作品图 / 分镜脚本 / 全量项目"),
                            seg=(rec, *SEG["s5"])), 7.0, 0.6))

    # ⑧ 合规与占比
    jobs.append(("ui", dict(base=base_full(ui_shot("s1_top"), focus=(1270, 180, 650, 800)),
                            ov=make_overlay(chapter="合规 · 可复现", ui=True,
                                            sub="第三方资源逐一登记 · AIGC 占比 80%（红线 ≥60%）"),
                            mode="up"), 8.0, 0.6))

    # ⑨ 成果全家福
    jobs.append(("cin", dict(base=base_full(shot_img(6), dark=0.44, zoom=1.02),
                             ov=make_overlay(kicker="三缸集章 · 水乡寻韵",
                                             title="六位水乡小匠 · 在柯桥等你",
                                             tag="原创文旅 IP 家族 · 可延展衍生品与线下落地",
                                             sub="柯桥 · 水乡IP造物台 · 让 AI 创作看得见、跑得通、可复现"),
                             mode="in"), 7.0, 0.7))

    # ---------- 校正录屏片段时长 ----------
    norm = []
    for kind, pl, d, ovl in jobs:
        if pl.get("seg"):
            _, a, b = pl["seg"]
            d = min(d, max(3.0, (b - a) - 0.15))
        norm.append((kind, pl, d, ovl))
    jobs = norm

    # ---------- 逐镜生成 ----------
    clips = []
    for i, (kind, pl, d, ov_) in enumerate(jobs):
        if kind == "cin":
            c = clip_cinematic(i, pl["base"], pl["ov"], d, pl["mode"])
        else:
            c = clip_ui(i, pl.get("base"), pl["ov"], d, pl.get("mode"), pl.get("seg"))
        clips.append(c)
        print(f"  ✓ 片段 {i+1:02d}/{len(jobs)}  {kind}  {d}s")
        pl["base"] = None  # 释放

    # ---------- 交叉溶解串接 ----------
    inputs, fc, prev = [], [], "[0:v]"
    for c in clips:
        inputs += ["-i", c]
    lens = [dur_of(c) for c in clips]
    t = lens[0]
    for i in range(1, len(clips)):
        d = jobs[i][3]
        off = max(0.0, t - d)
        lab = f"[x{i}]"
        fc.append(f"{prev}[{i}:v]xfade=transition=fade:duration={d:.2f}:offset={off:.3f}{lab}")
        t = off + lens[i]
        prev = lab
    master = os.path.join(WORK, "master_silent.mp4")
    ff(["ffmpeg", "-y", *inputs, "-filter_complex", ";".join(fc), "-map", prev,
        "-c:v", "libx264", "-preset", "medium", "-crf", "16", "-pix_fmt", "yuv420p",
        "-r", str(FPS), master])
    total = dur_of(master)
    print("无声母片:", round(total, 1), "s")

    # ---------- 环境音底噪 → 进度条 → 赛题规格成片 ----------
    amb = sorted(glob.glob(os.path.join(ROOT, "video_work", "amb_*.mp3")))
    bed = None
    if amb:
        args = []
        for a in amb:
            args += ["-i", a]
        n = len(amb)
        bed = os.path.join(WORK, "bed.wav")
        ff(["ffmpeg", "-y", *args, "-filter_complex",
            "".join(f"[{i}:a]" for i in range(n)) + f"concat=n={n}:v=0:a=1[b]",
            "-map", "[b]", bed])
    finalize(master, total, bed)


def finalize(master, total, bed=None):
    """叠加贯穿全片的进度条 + 环境音底噪；按赛题规格 CBR 8–10 Mbps 编码"""
    final = os.path.join(DIST, "作品演示视频.mp4")
    track = os.path.join(WORK, "track.png")
    Image.new("RGB", (W, 6), INK).save(track)
    # 进度条：底色画满金色，再用同色"幕布"按时间从左遮到右
    fc_v = (f"[0:v]drawbox=x=0:y={H-6}:w=iw:h=6:color=0xE2B760@0.92:t=fill[bg];"
            f"[bg][1:v]overlay=x='main_w*t/{total:.2f}':y={H-6}:format=auto,format=yuv420p[v]")
    venc = ["-c:v", "libx264", "-preset", "medium",
            "-b:v", "9M", "-minrate", "9M", "-maxrate", "9M", "-bufsize", "9M",
            "-x264-params", "nal-hrd=cbr:force-cfr=1:filler=1"]
    if bed and os.path.exists(bed):
        fc = (fc_v + ";"
              + f"[2:a]volume=0.30,atrim=0:{total:.2f},asetpts=N/SR/TB,"
                f"afade=t=in:st=0:d=1.4,afade=t=out:st={max(0.1, total-2.2):.2f}:d=2.2[a]")
        ff(["ffmpeg", "-y", "-i", master,
            "-loop", "1", "-t", f"{total:.2f}", "-i", track,      # 输入端限时，避免无限循环
            "-stream_loop", "-1", "-t", f"{total:.2f}", "-i", bed,
            "-filter_complex", fc, "-map", "[v]", "-map", "[a]", *venc,
            "-c:a", "aac", "-b:a", "192k", "-ar", "44100",
            "-t", f"{total:.2f}", "-movflags", "+faststart", final])
    else:
        ff(["ffmpeg", "-y", "-i", master,
            "-loop", "1", "-t", f"{total:.2f}", "-i", track,
            "-filter_complex", fc_v, "-map", "[v]", *venc,
            "-t", f"{total:.2f}", "-movflags", "+faststart", final])
    shutil.copy(final, os.path.join(DIST, "[队伍编号]作品演示视频.mp4"))
    print("成片:", final, "|", round(dur_of(final), 1), "s")


if __name__ == "__main__":
    import sys
    if "--finalize-only" in sys.argv:
        ms = os.path.join(WORK, "master_silent.mp4")
        finalize(ms, dur_of(ms), os.path.join(WORK, "bed.wav"))
    else:
        main()
