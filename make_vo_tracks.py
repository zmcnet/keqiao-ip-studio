#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""生成两条完整配音轨（按时间轴顺序拼接）"""
import json, os, subprocess

ROOT = os.path.dirname(os.path.abspath(__file__))
P = os.path.join(ROOT, "配音素材包")
VO = os.path.join(ROOT, "video_work", "vo2")
os.makedirs(os.path.join(P, "完整配音轨"), exist_ok=True)

C_KEYS = ["c0_title", "c1_jian", "c2_xianbao", "c3_achun",
          "c4_bu", "c5_shan", "c6_li", "c7_outro"]
D_KEYS = ["d0_hook", "d1_arch", "d2_plan", "d3_asset", "d4_shot",
          "d5_edit", "d6_export", "d7_comply", "d8_family", "d9_end"]


def dur(p):
    r = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                        "-of", "default=noprint_wrappers=1:nokey=1", p],
                       capture_output=True, text=True)
    try:
        return round(float(r.stdout.strip()), 2)
    except Exception:
        return 0.0


def build_track(keys, out):
    lst = os.path.join(P, "_tl.txt")
    with open(lst, "w", encoding="utf-8") as f:
        for k in keys:
            p = os.path.join(VO, k + ".mp3").replace(os.sep, "/")
            f.write("file '%s'\n" % p)
    r = subprocess.run(["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", lst,
                        "-c", "copy", out], capture_output=True, text=True)
    if r.returncode != 0:
        subprocess.run(["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", lst,
                        "-c:a", "libmp3lame", "-b:a", "192k", out],
                       capture_output=True, text=True)
    try:
        os.remove(lst)
    except Exception:
        pass
    return out


if __name__ == "__main__":
    c = build_track(C_KEYS, os.path.join(P, "完整配音轨", "作品视频_完整配音.mp3"))
    d = build_track(D_KEYS, os.path.join(P, "完整配音轨", "作品演示视频_完整配音.mp3"))
    print("内容成片完整配音: %.2fs" % dur(c))
    print("演示片完整配音:   %.2fs" % dur(d))
