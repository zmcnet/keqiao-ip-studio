# 柯桥·水乡IP造物台（Keqiao IP Studio）

> 绍兴市第一届人工智能应用竞赛 · 数字创意与AIGC应用赛道
> 主题一（绍兴柯桥区地方文旅宣传）· 选项B（原创柯桥专属旅游IP形象）

一个**支持多模态的「创编一体」全链路创作工作台**：围绕柯桥原创旅游IP，
打通 **意图理解 → 结构化策划 → 角色资产锁定 → 分镜生成 → 时间轴预览 → 成片导出**。

**核心逻辑**：策划阶段由 LLM 产出**结构化项目模型**（世界观 + 角色 + 分镜脚本），
作为**单一事实源**驱动下游全部环节——先锁定「角色种子图」，后续每个分镜生成都以它作为
`reference` 参考图，从而保证**同一角色跨场景形象一致**（不"换脸"）。

在线体验：见项目主页（无需登录，打开即用）

---

## 功能特性

| 环节 | 能力 |
|------|------|
| 智能策划 | 自然语言描述 → 结构化项目模型（世界观/角色/分镜） |
| 角色资产锁定 | 生成并锁定角色种子图，作为后续分镜的一致性参考 |
| 分镜生成 | 逐镜生成画面，支持参考图约束 |
| 配音与音频 | TTS 语音合成、字幕与音轨对齐 |
| 时间轴预览 | 多轨时间轴，实时预览成片 |
| 成片导出 | 一键导出视频与交付包 |
| 优雅降级 | 上游 API 不可用时自动回退模拟层（`mode=sim`），流程不中断 |

---

## 技术栈

| 组件 | 说明 |
|------|------|
| 后端 | Python 3（**仅标准库**，`http.server` + `urllib`，无第三方依赖） |
| 前端 | 原生 HTML / CSS / JavaScript，单页工作台 |
| 上游 API | SenseAudio 全模态（LLM / 图像 / TTS / ASR） |
| 部署 | Ubuntu 24.04 LTS · Nginx + systemd |

> `server.py` 运行时**零第三方依赖**，克隆下来即可直接跑。
> 仓库中的 `build_*.py`、`gen_vo2.py`、`make_vo_tracks.py` 等脚本仅用于**生成素材**，
> 额外依赖 `python-docx`、`Pillow`、`playwright`、`PyMuPDF`、`pywin32`，不影响主程序运行。

---

## 快速开始

### 1. 本地运行（无需任何依赖）

```bash
git clone <this-repo>
cd keqiao-ip-studio

# 方式一：直接运行（读取 config.json）
python server.py

# 方式二：用环境变量注入密钥（推荐，更安全）
export SENSEAUDIO_API_KEY="sk-你的密钥"
python server.py
```

浏览器打开 <http://127.0.0.1:8899/index.html>。

### 2. 配置密钥

密钥**不要提交到仓库**。仓库已提供模板：

```bash
cp config.example.json config.json
# 编辑 config.json，填入 api_key
```

或直接使用环境变量 `SENSEAUDIO_API_KEY`（优先级高于 `config.json`）。

`config.json` 已列入 `.gitignore`。

---

## 生产部署

完整部署记录见 [`docs/部署说明.md`](docs/部署说明.md)（含 Nginx 配置、systemd 单元、
SSL、限流、fail2ban、SSH 加固、密钥隔离策略）。

架构概览：

```
Internet ──:443(HTTPS)──> Nginx ──┬── 静态资源  /opt/keqiao-ip-studio
                        (SSL / 安全头 / 限流)
                                  └── /api/*  反代 ──> 127.0.0.1:8899 (server.py)
                                                          └──> SenseAudio API（密钥仅存服务端）
```

核心要点：

- 应用仅监听 `127.0.0.1:8899`，外网不可直连
- API 密钥存于 `/etc/keqiao-ip-studio/secret.env`（`600 root`），web 目录零明文
- `/server.py`、`/config.json`、`/.git` 等路径一律返回 404

---

## 构建素材脚本

以下脚本用于生成演示素材与交付包，**按需运行**，产物不纳入版本库：

| 脚本 | 用途 |
|------|------|
| `build_doc.py` | 生成说明文档（依赖 `python-docx`） |
| `build_demo_v3.py` | 构建演示项目素材 |
| `build_demo_video.py` / `build_video.py` | 合成演示视频（依赖 `ffmpeg`） |
| `build_package.py` | 打包最终交付件 |
| `gen_vo2.py` | 生成配音 |
| `make_vo_tracks.py` | 对齐音轨 |
| `record_demo.py` | 录制演示 |
| `_check_doc.py` | 文档自检 |

安装可选依赖：

```bash
pip install python-docx pillow playwright pymupdf pywin32
```

---

## 目录结构

```
keqiao-ip-studio/
├── index.html            # 工作台主页面
├── server.py             # 本地代理服务（标准库实现）
├── config.example.json   # 配置模板
├── config.json           # 本地配置（gitignored）
├── assets/               # 静态资源（图片/字体/音效）
├── docs/                 # 设计文档与部署说明
├── 答辩PPT/              # 答辩材料
├── 演示PPT/              # 演示材料
├── 配音素材包/            # 配音素材
└── build_*.py            # 素材构建脚本
```

---

## 文档

| 文档 | 说明 |
|------|------|
| [全链路方案与评分策略](docs/全链路方案与评分策略.md) | 产品设计与竞赛策略 |
| [柯桥IP世界观设计](docs/柯桥IP世界观设计.md) | 世界观与角色设定 |
| [自查与合规报告](docs/自查与合规报告.md) | 合规自检 |
| [部署说明](docs/部署说明.md) | 生产环境部署记录 |

---

## 许可

本项目源码采用 [MIT License](LICENSE) — © 2026 ZMCNET。

第三方声明：
- SenseAudio 相关素材与 API 版权归其所有者所有
- 演示素材中引用的第三方内容版权归各自作者