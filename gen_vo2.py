#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
生成两片配音（SenseAudio TTS）并测量精确时长
输出：video_work/vo2/<key>.mp3 + video_work/vo2/durations.json
"""
import os, json, time, base64, binascii, subprocess, urllib.request, urllib.error

ROOT = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(ROOT, "video_work", "vo2")
os.makedirs(OUT, exist_ok=True)
CFG = json.load(open(os.path.join(ROOT, "config.json"), encoding="utf-8"))

# 配音清单：(key, 音色, 文本)
LINES = [
    # ---- 作品内容成片 ----
    ("c0_title", "male_0004_a",
     "东晋柯亭，蔡邕取竹制笛。笛声引动鉴湖千年水气，凝作六位水乡小匠——他们守着柯桥的山水、古镇与人情。"),
    ("c1_jian", "male_0004_a",
     "桨声欸乃，柯桥的水，醒了。我是阿鉴，鉴湖的水之子。坐上我的乌篷船，带你把柯桥看个够。"),
    ("c2_xianbao", "child_0001_b",
     "晒足一百八十天，才是安昌的老味道。我是鲜宝，安昌的酱香都在这口缸里——伏酱秋油，急不得。"),
    ("c3_achun", "male_0018_a",
     "鉴湖水酿的酒，配得上这一方山水！我是阿醇，越酒行天下，这一碗暖，敬柯桥。"),
    ("c4_bu", "child_0001_a",
     "一缸靛蓝，染出会跳舞的颜色。我是布小彩，三桥四水的夜里，蓝印花布也会发光。"),
    ("c5_shan", "male_0004_a",
     "一把扇子半把伞——八十六道工序，才撑得起这份从容。我是扇小雅，一扇之间，装得下整条鉴湖。"),
    ("c6_li", "child_0001_a",
     "锣鼓一响，就是我的场子！我是梨小社，鲁镇的社戏台上，柯桥的故事就开演啦！"),
    ("c7_outro", "male_0004_a",
     "酒缸、酱缸、染缸——三口古缸，是柯桥的元气。三缸集章，水乡寻韵。六位小匠，在柯桥等你。"),

    # ---- 作品演示视频 ----
    ("d0_hook", "male_0004_a",
     "一句创意，能走多远？从一句想法，到一部成片——柯桥·水乡IP造物台，把全链路交给 AI。"),
    ("d1_arch", "male_0004_a",
     "我们围绕柯桥原创旅游 IP，打通五个环节：智能策划、角色资产锁定、分镜生成、时间轴预览、成片导出。策划产出的结构化项目模型，是驱动全链路的唯一数据源。"),
    ("d2_plan", "male_0004_a",
     "输入一句创意，AI 扩写为结构化项目。你看，世界观、角色设定、六镜分镜脚本，一次性生成完毕——每个人物绑定了对应的柯桥地标与非遗符号。"),
    ("d3_asset", "male_0004_a",
     "接下来锁定角色资产。为每位小匠生成标准立绘，也就是种子图。这一步很关键——它将成为后续所有分镜的一致性锚点。"),
    ("d4_shot", "male_0004_a",
     "分镜环节，系统自动把角色种子图作为参考图注入模型。同一张脸，穿越不同场景，形象不崩——这正是 IP 得以成立的技术前提。"),
    ("d5_edit", "male_0004_a",
     "镜头排上时间轴。不满意？用自然语言下指令——把第三镜改成近景，系统即刻改写参数。每一镜都可以单独配音试听。"),
    ("d6_export", "male_0004_a",
     "最后，一键导出。说明文档、分镜脚本、全量项目、角色图，连同 A3 规格海报，一次交付。"),
    ("d7_comply", "male_0004_a",
     "合规不是事后补。工作台内置合规台账，八项第三方资源逐条登记来源与授权；AIGC 参与占比实时核算——百分之八十，远高于赛题百分之六十的红线。"),
    ("d8_family", "male_0004_a",
     "六位原创 IP，六个柯桥地标，六镜成片。一条完整的 AIGC 创作链路，在这里跑通。"),
    ("d9_end", "male_0004_a",
     "柯桥·水乡IP造物台——让柯桥之美，被世界看见。"),
]


def tts(text, voice):
    body = {"model": CFG["models"]["tts"], "text": text, "stream": False,
            "voice_setting": {"voice_id": voice, "speed": 1, "vol": 1, "pitch": 0},
            "audio_setting": {"format": "mp3", "sample_rate": 32000, "bitrate": 128000, "channel": 1}}
    req = urllib.request.Request(CFG["base_url"] + "/v1/t2a_v2",
                                 data=json.dumps(body).encode(),
                                 headers={"Authorization": "Bearer " + CFG["api_key"],
                                          "Content-Type": "application/json"}, method="POST")
    r = urllib.request.urlopen(req, timeout=120)
    d = json.loads(r.read().decode())
    au = d.get("data", {}).get("audio", "")
    if not au:
        raise RuntimeError("no audio: " + json.dumps(d)[:300])
    try:
        return binascii.unhexlify(au)
    except Exception:
        return base64.b64decode(au)


def dur(path):
    r = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                        "-of", "default=noprint_wrappers=1:nokey=1", path],
                       capture_output=True, text=True)
    try:
        return round(float(r.stdout.strip()), 2)
    except Exception:
        return 0.0


def main():
    res = {}
    for key, voice, text in LINES:
        p = os.path.join(OUT, key + ".mp3")
        try:
            raw = tts(text, voice)
            open(p, "wb").write(raw)
            d = dur(p)
            res[key] = {"voice": voice, "dur": d, "text": text, "chars": len(text)}
            print("%-12s %-14s %6.2fs  (%d字)" % (key, voice, d, len(text)))
        except Exception as e:
            print("%-12s ERR %s" % (key, str(e)[:120]))
            res[key] = {"voice": voice, "dur": 0, "text": text, "error": str(e)[:200]}
        time.sleep(0.4)
    json.dump(res, open(os.path.join(OUT, "durations.json"), "w", encoding="utf-8"),
              ensure_ascii=False, indent=2)
    # 汇总
    content = [k for k in res if k.startswith("c")]
    demo = [k for k in res if k.startswith("d")]
    print("\n内容成片合计: %.2fs" % sum(res[k]["dur"] for k in content))
    print("演示视频合计: %.2fs" % sum(res[k]["dur"] for k in demo))


if __name__ == "__main__":
    main()
