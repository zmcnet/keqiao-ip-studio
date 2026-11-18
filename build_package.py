# -*- coding: utf-8 -*-
"""
构建参赛交付包 —— 汇总全部必需与附加材料，输出到桌面并压缩为 zip。
安全：排除 config.json（含 API 密钥）；排除 video_work（中间产物与备份）。
"""
import os, shutil, zipfile, sys

ROOT = r"C:\Users\kybll\Desktop\AIGC\keqiao-ip-studio"
WSC  = r"C:\Users\kybll\Desktop\AIGC"
OUT  = r"C:\Users\kybll\Desktop\柯桥水乡IP造物台_参赛交付包"
ZIP  = r"C:\Users\kybll\Desktop\柯桥水乡IP造物台_参赛交付包.zip"

# ---------- 清理旧产物 ----------
for p in (OUT, ZIP):
    if os.path.isdir(p): shutil.rmtree(p, ignore_errors=True)
    elif os.path.isfile(p):
        try: os.remove(p)
        except OSError: pass

def mk(*a):
    d = os.path.join(OUT, *a)
    os.makedirs(d, exist_ok=True)
    return d

def cp(src, dst_dir, newname=None):
    if not os.path.exists(src):
        print("  [跳过·不存在] %s" % src); return False
    os.makedirs(dst_dir, exist_ok=True)
    shutil.copy2(src, os.path.join(dst_dir, newname or os.path.basename(src)))
    print("  [√] %s" % (newname or os.path.basename(src)))
    return True

def cptree(src, dst):
    if not os.path.isdir(src):
        print("  [跳过·不存在] %s" % src); return
    shutil.copytree(src, dst, dirs_exist_ok=True)
    print("  [√] 目录 %s" % os.path.basename(src))

print("=" * 64)
print("  构建参赛交付包")
print("=" * 64)

# ========== 01 参赛作品（五件套）==========
print("\n[01] 参赛作品")
d = mk("01_参赛作品")
cp(os.path.join(ROOT, "dist", "[队伍编号]说明文档.docx"), d)
cp(os.path.join(ROOT, "dist", "[队伍编号]作品视频.mp4"), d)
cp(os.path.join(ROOT, "dist", "[队伍编号]作品演示视频.mp4"), d)
cp(os.path.join(ROOT, "dist", "[队伍编号]答辩PPT.pptx"), d)
cp(os.path.join(ROOT, "dist", "[队伍编号]作品演示PPT.pptx"), d)

# ========== 02 源代码与部署说明 ==========
print("\n[02] 源代码与部署说明")
d = mk("02_源代码与部署说明")
# 运行入口
for f in ["index.html", "server.py", "config.example.json"]:
    cp(os.path.join(ROOT, f), d)
# 前端资源（css + js + 生成图）
cptree(os.path.join(ROOT, "assets"), os.path.join(d, "assets"))
# 构建/工具脚本
d2 = mk("02_源代码与部署说明", "构建脚本")
for f in ["build_v2.py", "build_demo_v3.py", "build_demo_video.py", "build_video.py",
          "gen_vo2.py", "make_vo_tracks.py", "record_demo.py", "build_doc.py"]:
    cp(os.path.join(ROOT, f), d2)
# 部署说明（赛题要求"代码及部署说明"）
cp(os.path.join(ROOT, "docs", "部署说明.md"), d)
cp(os.path.join(ROOT, "README.md"), d)

# ========== 03 配音素材包 ==========
print("\n[03] 配音素材包")
cptree(os.path.join(ROOT, "配音素材包"), mk("03_配音素材包"))

# ========== 04 项目文档 ==========
print("\n[04] 项目文档")
d = mk("04_项目文档")
for f in ["柯桥IP世界观设计.md", "全链路方案与评分策略.md", "自查与合规报告.md", "部署说明.md"]:
    cp(os.path.join(ROOT, "docs", f), d)
cp(os.path.join(WSC, "AIGC赛道_要点与注意事项清单.md"), d)
cp(os.path.join(WSC, "交接文档.md"), d)

# ========== 05 PPT / 视频工程源文件 ==========
print("\n[05] 工程源文件")
cptree(os.path.join(ROOT, "答辩PPT"), mk("05_工程源文件", "答辩PPT"))
cptree(os.path.join(ROOT, "演示PPT"), mk("05_工程源文件", "演示PPT"))

print("\n构建完成 -> %s" % OUT)
