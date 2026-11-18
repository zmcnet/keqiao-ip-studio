#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
柯桥·水乡IP造物台 —— 作品演示素材录制（v2）
================================================
用 Playwright 真实驱动浏览器，完整走一遍工作台五大环节。
产出（video_work/demo/）：
  · rec.webm        全程真实录屏（用于成片中的"操作"镜头）
  · marks.json      各环节时间戳（供合成脚本精确切片）
  · shot_*.png      各环节页面截图（供成片的"细节放大"镜头）

依赖：playwright（chromium 已缓存）；运行前请确保 server.py 已启动。
"""
import os, glob, shutil, json, time
from playwright.sync_api import sync_playwright

ROOT = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(ROOT, "video_work", "demo")
REC = os.path.join(OUT, "rec")
URL = "http://127.0.0.1:8899/index.html"
VW, VH = 1920, 1080

# 注入可见光标 + 点击涟漪，让录屏看得出操作
CURSOR = """
(() => {
  const add = () => {
    const c = document.createElement('div');
    c.style.cssText = 'position:fixed;z-index:2147483647;width:30px;height:30px;border-radius:50%;' +
      'background:rgba(46,125,181,.45);border:3px solid #fff;box-shadow:0 0 18px rgba(0,0,0,.5);' +
      'pointer-events:none;left:-100px;top:-100px;transition:left .06s linear,top .06s linear;';
    document.body.appendChild(c);
    window.addEventListener('mousemove', e => { c.style.left = (e.clientX-15) + 'px'; c.style.top = (e.clientY-15) + 'px'; });
    document.addEventListener('click', e => {
      const r = document.createElement('div');
      r.style.cssText = 'position:fixed;z-index:2147483646;width:34px;height:34px;border-radius:50%;' +
        'border:4px solid #2E7DB5;pointer-events:none;left:' + (e.clientX-17) + 'px;top:' + (e.clientY-17) + 'px;' +
        'animation:kqpulse .6s ease-out forwards;';
      document.body.appendChild(r);
      setTimeout(() => r.remove(), 700);
    });
  };
  if (document.body) add(); else document.addEventListener('DOMContentLoaded', add);
  const st = document.createElement('style');
  st.textContent = '@keyframes kqpulse{to{transform:scale(2.6);opacity:0}}';
  document.head && document.head.appendChild(st);
})();
"""

MARKS = {}


def stamp(page, key):
    """记录相对录屏起点的秒数（performance.now 更稳）"""
    try:
        ms = page.evaluate("() => performance.now()")
    except Exception:
        ms = 0
    MARKS[key] = round(ms / 1000.0, 2)


def glide(page, x, y, steps=22):
    page.mouse.move(x, y, steps=steps)
    page.wait_for_timeout(320)


def click_center(page, sel, wait=1200, idx=0):
    el = page.query_selector_all(sel)[idx]
    box = el.bounding_box()
    glide(page, box["x"] + box["width"] / 2, box["y"] + box["height"] / 2)
    el.click()
    page.wait_for_timeout(wait)


def shot(page, name, full=False):
    page.screenshot(path=os.path.join(OUT, name + ".png"), full_page=full)


def main():
    if os.path.isdir(REC):
        shutil.rmtree(REC)
    for f in glob.glob(os.path.join(OUT, "*.png")):
        os.remove(f)
    os.makedirs(REC, exist_ok=True)

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True, args=["--force-color-profile=srgb", "--hide-scrollbars"])
        ctx = browser.new_context(viewport={"width": VW, "height": VH},
                                  record_video_dir=REC,
                                  record_video_size={"width": VW, "height": VH},
                                  device_scale_factor=1)
        ctx.add_init_script(CURSOR)
        t0 = time.time()
        page = ctx.new_page()
        page.goto(URL + "#s1", wait_until="networkidle")
        page.wait_for_timeout(4200)

        # —— ① 智能策划（展示结构化项目） ——
        stamp(page, "s1")
        shot(page, "s1_top")
        glide(page, 700, 400)
        page.evaluate("window.scrollTo({top:520})")
        page.wait_for_timeout(3400)
        stamp(page, "s1_scroll")
        shot(page, "s1_table")
        page.evaluate("window.scrollTo({top:0})")
        page.wait_for_timeout(900)

        # —— ② 角色资产锁定 ——
        click_center(page, ".step", wait=600, idx=1)
        page.wait_for_timeout(3600)
        stamp(page, "s2")
        shot(page, "s2")
        try:
            click_center(page, ".g-item", wait=1800, idx=1)
        except Exception:
            pass

        # —— ③ 分镜生成 ——
        click_center(page, ".step", wait=600, idx=2)
        page.wait_for_timeout(4200)
        stamp(page, "s3")
        shot(page, "s3")
        page.evaluate("window.scrollTo({top:430})")
        page.wait_for_timeout(2600)
        shot(page, "s3_scroll")
        page.evaluate("window.scrollTo({top:0})")

        # —— ④ 时间轴 + 对话式编辑 ——
        click_center(page, ".step", wait=600, idx=3)
        page.wait_for_timeout(3200)
        stamp(page, "s4")
        shot(page, "s4")
        try:
            click_center(page, ".tl-item", wait=1600, idx=2)
        except Exception:
            pass
        try:
            el = page.query_selector("#chatInput")
            b = el.bounding_box()
            glide(page, b["x"] + b["width"] / 2, b["y"] + b["height"] / 2)
            el.click()
            for ch in "把第3镜改成近景，突出阿醇抱酒坛":
                page.keyboard.type(ch)
                page.wait_for_timeout(75)
            stamp(page, "chat_type")
            page.wait_for_timeout(700)
            shot(page, "s4_typed")
            click_center(page, "text=发送")
            page.wait_for_timeout(13000)
            stamp(page, "chat_reply")
            shot(page, "s4_chat")
        except Exception as e:
            print("对话编辑跳过:", e)

        # —— ⑤ 成片导出 ——
        click_center(page, ".step", wait=600, idx=4)
        page.wait_for_timeout(3800)
        stamp(page, "s5")
        shot(page, "s5")
        page.wait_for_timeout(1200)

        MARKS["_end_perf"] = round(page.evaluate("() => performance.now()") / 1000.0, 2)
        MARKS["_wall"] = round(time.time() - t0, 2)

        ctx.close()
        browser.close()

    with open(os.path.join(OUT, "marks.json"), "w", encoding="utf-8") as f:
        json.dump(MARKS, f, ensure_ascii=False, indent=2)

    vids = sorted(glob.glob(os.path.join(REC, "*.webm")))
    print("录制完成:", vids)
    print("时间戳:", json.dumps(MARKS, ensure_ascii=False))


if __name__ == "__main__":
    main()
