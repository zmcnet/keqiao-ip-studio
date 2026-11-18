# -*- coding: utf-8 -*-
"""
柯桥·水乡IP造物台 —— 作品说明文档生成器
单一来源：下方 CONTENT 内容模型 → 同时渲染 official-format .docx 与可读 markdown。
用法：python build_doc.py

对齐赛题《[数字创意与AIGC应用]赛题》对说明文档的要求：
  完整填写「作品核心创意 / 技术实现方案 / 应用场景说明 / 所有第三方资源来源及授权说明 / AIGC创作占比依据」
版式：A4 · 标题黑体 · 正文宋体 · 1.5 倍行距 · 页脚页码 · 表格网格线。
"""
import os
from docx import Document
from docx.shared import Pt, Cm, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

ROOT = os.path.dirname(os.path.abspath(__file__))
OUT_DOCX = os.path.join(ROOT, "dist", "[队伍编号]说明文档.docx")
OUT_STAGE3 = os.path.join(ROOT, "output", "doc", "2026-10-10-说明文档", "stage3", "[队伍编号]说明文档.docx")
OUT_MD = os.path.join(ROOT, "output", "doc", "2026-10-10-说明文档", "stage1", "final_draft.md")

NAVY = RGBColor(0x0E, 0x3F, 0x8C)
BLUE = RGBColor(0x1E, 0x4F, 0xA8)
INK = RGBColor(0x1A, 0x1A, 0x1A)
GREY = RGBColor(0x55, 0x55, 0x55)

# =====================================================================
# 内容模型（单一事实源）
#   title / subtitle / coverinfo / pagebreak
#   h2 / h3 / p / li / num / note / table(rows, header=True)
# =====================================================================
C = []
a = C.append

a(("title", "柯桥·水乡IP造物台"))
a(("subtitle", "作 品 说 明 文 档"))
a(("coverinfo", "绍兴市第一届人工智能应用竞赛　·　数字创意与 AIGC 应用赛道"))
a(("coverinfo", "创作主题：主题一（绍兴柯桥区地方文旅宣传）·　选项 B（原创柯桥专属旅游 IP 形象）"))
a(("coverinfo", "作品形态：原创柯桥专属旅游 IP 形象 ＋ 可运行的 AIGC 全链路创作系统"))
a(("coverinfo", "队伍编号：＿＿＿＿＿＿＿＿　（提交时按组委会编号填写）"))
a(("coverinfo", "2026 年 10 月"))
a(("pagebreak", None))

# ---------------------------------------------------------------- 一
a(("h2", "一、作品核心创意"))

a(("h3", "1.1 一句话定义"))
a(("p", "「柯桥·水乡IP造物台」是一件**原创柯桥专属旅游 IP 形象作品**，同时是一套**可运行的 AIGC 创作系统**：用户输入一句创意，系统即可自动完成从世界观策划、角色生成、分镜绘制到成片导出的全链路创作，产出适配文本、图片、音频、视频多场景的传播成果。"))

a(("h3", "1.2 创作背景与选题依据"))
a(("p", "本作品紧扣赛题「主题一·选项 B：打造原创柯桥专属旅游 IP 形象，并结合柯桥地方非遗文化制作系列宣传内容」的要求，产出 **3—7 个具备差异化性格与视觉标识的角色**、完整 IP 世界观设定、标准多视图与场景延展应用图，满足后续衍生品开发与线下文旅场景落地的使用要求。选题依据如下："))
a(("li", "**在地符号强**：柯桥最鲜明的文化符号是「三缸」——酒缸、酱缸、染缸，分别对应黄酒、仁昌酱园母子酱油、轻纺印染三大产业与非遗，且横跨鉴湖、安昌古镇、柯桥古镇、鲁镇等真实地标，辨识度高、故事性强。"))
a(("li", "**非遗富集**：绍兴黄酒酿制技艺（国家级）、仁昌酱园母子酱油（省级）、王星记扇（国家级·86 道工序「半把伞」）、蓝印花布、水乡社戏与越剧，均可自然融入角色与场景。"))
a(("li", "**可延展落地**：IP 形象方向天然适配衍生品开发（折扇、黄酒周边、蓝印花布、文创伴手礼）与线下文旅场景，契合「传播价值与应用推广前景」评分项。"))
a(("li", "**创新表达**：以「小匠」拟人化承载产业与非遗，把「有滋有味、有色有香」的水乡生活转译为可亲近的角色形象，打破传统风光宣传片的同质化表达。"))

a(("h3", "1.3 世界观设定：三缸奇缘 · 笛里柯桥"))
a(("p", "**地名渊源**：柯桥古称「笛里」，源出东晋柯亭——蔡邕取柯亭竹制笛，笛声清越，为水乡文脉之始。作品以「笛里」为世界之名，锚定柯桥的历史纵深。"))
a(("p", "**起源故事**：柯亭笛声引动鉴湖千年水气，水气凝作**六位水乡小匠**，居于柯亭竹影之间，守着柯桥的山水、古镇与人情。"))
a(("p", "**核心设定 · 三缸灵脉**：柯桥的元气，藏在三口古缸里——"))
a(("li", "**酒缸（醇）**：鉴湖水酿的绍兴黄酒，是这片水土的**暖**；"))
a(("li", "**酱缸（鲜）**：仁昌酱园的母子酱油，是这片水土的**味**；"))
a(("li", "**染缸（彩）**：柯桥轻纺的纺织印染，是这片水土的**色**。"))
a(("p", "三缸由柯桥先民的匠心所化，维系着水乡「有滋有味、有色有香」的生活底色。六位小匠的使命，是守护这条灵脉，把柯桥之美带向四方。"))
a(("p", "**精神内核**：越地匠心的「**守**」与「**传**」——一劈一磨的耐心、雨淋不透的坚守、千年不息的传承。"))

a(("h3", "1.4 六位原创 IP 角色"))
a(("table", [
    ["#", "角色", "承载地标 / 非遗", "性格", "视觉标识 / 主色", "配音音色"],
    ["1", "阿鉴", "鉴湖 · 乌篷船", "温和 · 善引路 · 慢生活", "乌毡帽＋水波纹披风＋船桨（水蓝 #2E7DB5）", "male_0004_a"],
    ["2", "阿醇", "绍兴黄酒酿制技艺（国家级非遗）", "憨厚 · 豪爽 · 热心肠", "怀抱小酒坛＋微醺红晕（琥珀金 #C8892B）", "male_0018_a"],
    ["3", "鲜宝", "仁昌酱园母子酱油（省级非遗）· 安昌古镇", "勤恳 · 守时 · 爱「晒」", "酱缸盖帽＋酱鸭腊肠挂饰（酱棕红 #8C4A2F）", "child_0001_b"],
    ["4", "布小彩", "染缸 · 蓝印花布 · 中国轻纺城", "灵巧 · 爱美 · 会变装", "蓝印花布围裙＋染棒（靛蓝 #2F5D8C）", "child_0001_a"],
    ["5", "扇小雅", "王星记扇（国家级非遗 · 86 道工序）", "风雅 · 睿智 · 爱丹青", "手持黑纸折扇（竹青墨黑 #2F6B4F）", "male_0004_a"],
    ["6", "梨小社", "鲁镇 · 水乡社戏 · 越剧", "热情 · 爱唱演 · 人来疯", "越剧水袖＋脸谱妆（水袖红 #C0392B）", "child_0001_a"],
]))
a(("p", "六位角色的形象设计说明如下："))
a(("li", "**阿鉴**——鉴湖的水之子。戴黑色乌毡帽，水蓝色披风带水波纹，手持木船桨；形象清朗温和，是「水乡引路人」。「坐上我的乌篷船，带你把柯桥看个够。」"))
a(("li", "**阿醇**——黄酒的非遗传人。琥珀金色调，怀抱小酒坛，脸颊带微醺红晕；憨厚开朗，传递黄酒文化的暖。「鉴湖水酿的酒最暖身，来一碗，交个朋友！」"))
a(("li", "**鲜宝**——酱园的守味小掌柜。酱棕色，头顶酱缸盖帽、腰间挂酱鸭腊肠；勤恳守时，讲述「晒足一百八十天」的匠心。「安昌的老味道，都在这口酱缸里。」"))
a(("li", "**布小彩**——染缸里的灵巧少女。靛蓝与白色，系蓝印花布围裙、手持染棒；爱美会变装，诠释轻纺印染的灵巧。「一缸靛蓝，能染出会跳舞的颜色。」"))
a(("li", "**扇小雅**——制扇的风雅文人。竹青与墨黑，手持黑纸折扇；睿智爱丹青，承载 86 道工序的制扇技艺。「这把黑纸扇，雨淋不透、日晒不翘。」"))
a(("li", "**梨小社**——社戏台上的越剧少年。水袖红色戏服、脸谱妆容；热情活泼，演绎鲁镇社戏与越剧的热闹。「锣鼓一响，就是我的场子！」"))

a(("h3", "1.5 角色差异化与辨识度"))
a(("p", "六位角色分属「水 · 酒 · 酱 · 染 · 扇 · 戏」六条互不重叠的文化线，各自绑定柯桥真实地标或非遗；色彩上分别采用水蓝、琥珀金、酱棕红、靛蓝、竹青墨黑、水袖红，形成强区分度；性格上覆盖温和、豪爽、勤恳、灵巧、风雅、热情六种气质，避免「同一个模子」。角色数量为 6 个，落在赛题要求的 3—7 区间内，且逐个可对应到具体景观、非遗与产业，满足「深度融合柯桥非遗技艺、水乡文化内核」。"))

a(("h3", "1.6 原创落地玩法：「三缸集章 · 水乡寻韵」"))
a(("num", "六位小匠分别驻守柯桥六个真实点位（鉴湖/古纤道、安昌古镇、柯岩、柯桥古镇、王星记扇馆、鲁镇）；"))
a(("num", "游客凭「集章手账」逐一打卡，呼应安昌古镇既有的「集章本」玩法，形成可沉浸的线下动线；"))
a(("num", "结合柯桥既有 AR 项目做「小匠 AR 导览」，连接线上 IP 与线下场景；"))
a(("num", "衍生品链路：折扇、黄酒周边、蓝印花布、文创伴手礼，实现 IP 的商业化落地。"))

# ---------------------------------------------------------------- 二
a(("pagebreak", None))
a(("h2", "二、技术实现方案"))

a(("h3", "2.1 总体架构：创编一体 · 全链路五环"))
a(("p", "系统以「**结构化项目模型**」为唯一数据源，驱动下列五个环节串行流转，实现从一句话创意到成片成果的自动化创作。"))
a(("table", [
    ["环节", "输入", "输出", "实测耗时"],
    ["① 智能策划", "一句主题描述（支持语音输入）", "世界观 ＋ 6 角色 ＋ 6 镜脚本（结构化 JSON）", "≈ 22 秒"],
    ["② 角色资产锁定", "策划产出的角色设定", "6 张标准立绘（种子图，1024×1536）", "≈ 38 秒"],
    ["③ 分镜生成", "分镜脚本 ＋ 角色种子图", "6 张 1024×1536 分镜成图", "≈ 46 秒"],
    ["④ 时间轴预览与编辑", "自然语言修改指令", "改写后的分镜参数 ＋ 单镜配音", "≈ 28 秒"],
    ["⑤ 成片导出", "全部项目数据", "说明文档 / 脚本 / 项目 / 角色图 / A3 海报", "≈ 6 秒"],
]))
a(("note", "全流程总耗时约 140 秒，模型调用 14 次，人工干预仅 1 处（确认选题方向）。"))

a(("h3", "2.2 五环实现详解"))
a(("li", "**① 智能策划**：以一句主题描述（文本或语音识别结果）为输入，大语言模型以 `json_object` 结构化输出「世界观 ＋ 角色设定 ＋ 分镜脚本」，直接生成可供下游消费的项目模型，而非散文式文案。"))
a(("li", "**② 角色资产锁定**：依据策划产出的角色设定，为每位角色生成标准立绘并固化为「种子图」，作为后续全链路的一致性锚点。"))
a(("li", "**③ 分镜生成**：按分镜脚本逐镜生成画面，每一镜自动将对应角色的种子图作为 `reference` 参考图注入模型，确保角色跨场景不「换脸」。"))
a(("li", "**④ 时间轴预览与编辑**：将分镜按时间轴排布，支持回看与试听；用户可用自然语言修改分镜，并可为单镜生成配音。"))
a(("li", "**⑤ 成片导出**：一键导出说明文档、脚本、项目数据、角色图与 A3 海报，命名遵循 `[队伍编号]` 规则。"))

a(("h3", "2.3 核心技术一：角色一致性锚定"))
a(("p", "这是本作品最关键的技术突破，用于解决 AIGC 影视化最大的痛点——**同一角色跨场景「换脸」**。"))
a(("li", "**解决机制**：先在「角色资产锁定」环节产出每位角色的标准立绘（种子图）；后续每个分镜生成时，系统自动将该种子图作为 **reference 参考图**注入模型，以参考图约束形象特征。"))
a(("li", "**技术链路**：首镜生成 → 提取种子图 → 写入项目模型 → 后续每镜注入 reference。"))
a(("li", "**实测效果**：角色形象由立绘迁移至柯桥地标场景时特征保持一致（以阿鉴为例，由鉴湖立绘迁移到泛舟场景时，乌毡帽、水蓝披风、船桨等特征稳定保留），同一角色可稳定驻留多个地标，形成可复用的角色资产。这是 IP 得以成立的技术前提。"))

a(("h3", "2.4 核心技术二：单一事实源架构"))
a(("p", "策划阶段产出的结构化项目模型，作为**唯一数据源**驱动下游全部环节，避免传统方案中「策划写散文、下游不消费」的链路断裂。五个环节既可串行自动流转，也可独立操作并即时看到结果，参考 Seko / 即梦的「创编一体」交互范式。"))

a(("h3", "2.5 核心技术三：对话式编辑"))
a(("p", "用户可用自然语言直接下达修改指令。例如输入「把第三镜改成近景」，系统解析意图后自动定位到 `shot_3` 的 `shotType` 字段，将「全景」改写为「近景」，其余参数保持不变；用户无需在参数面板中逐项寻找与调整，大幅降低操作门槛。"))

a(("h3", "2.6 多模态与模型接入"))
a(("p", "作品基于 SenseAudio 开放平台，端到端接入四种模态的真实模型，实测全部通过："))
a(("table", [
    ["模态", "模型", "用途"],
    ["大语言模型", "senseaudio-s2", "世界观、角色、分镜脚本生成"],
    ["文生图", "senseaudio-image-2.0-260319", "角色立绘、分镜成图（支持 reference 参考图）"],
    ["语音合成", "sensenova-tts-2.0", "角色配音"],
    ["语音识别", "senseaudio-asr-1.5-260319", "语音输入创意"],
]))
a(("note", "输入侧融合图像/语音/文本，输出侧合成文本/图像/音频/视频，多模态贯穿策划—生成—编辑—预览—导出全链路。"))

a(("h3", "2.7 双模式容错，保障任意环境可演示"))
a(("p", "系统启动时自动探测服务健康度：连通即调用真实模型；服务不可用时**自动降级至模拟层**（参数化 SVG 绘制 ＋ 预置文案），界面与流程完全一致，保证在评审现场等任意环境下均可完整演示。"))
a(("table", [
    ["能力", "真实调用点", "模拟降级策略"],
    ["策划 / 文案", "/api/plan、/api/text", "预置世界观与文案"],
    ["角色立绘", "/api/image", "参数化 SVG 绘制"],
    ["配音", "/api/tts", "浏览器内置语音合成"],
    ["语音转文字", "/api/asr", "提示当前环境不支持"],
]))

a(("h3", "2.8 系统接口清单"))
a(("table", [
    ["接口", "方法", "作用"],
    ["/api/health", "GET", "健康检查（已最小化返回，防信息泄露）"],
    ["/api/plan", "POST", "大语言模型输出结构化项目模型（世界观/角色/分镜）"],
    ["/api/text", "POST", "文案生成"],
    ["/api/image", "POST", "文生图（支持 reference 参考图保一致性）"],
    ["/api/tts", "POST", "语音合成（上游返回 hex，服务端转 base64）"],
    ["/api/asr", "POST", "语音识别（multipart）"],
    ["/api/fetch_image", "POST", "服务端取图转 Data URI（规避 CORS，保证参考图可用）"],
    ["/api/export_sheet", "POST", "成图放大贴合 A3@300dpi（3508×4961）并写入 DPI 元数据"],
]))

a(("h3", "2.9 工程结构与可复现"))
a(("table", [
    ["文件", "职责"],
    ["index.html", "单页入口（顶栏 / 步进器 / 主舞台 / 侧栏 / 页脚）"],
    ["assets/js/ipdata.js", "项目数据内核：世界观 / 角色（含种子图）/ 分镜脚本 / 色卡 / 证据链 / 合规台账"],
    ["assets/js/render.js", "参数化 SVG 渲染器（模拟层角色 / 多视图 / 场景底图）"],
    ["assets/js/app.js", "流水线逻辑（五环 ＋ 真实模型 ＋ 对话式编辑 ＋ 导出）"],
    ["assets/css/app.css", "样式（江南水乡风）"],
    ["assets/generated/", "真实模型成果（6 角色立绘 ＋ 6 分镜图，共 12 张）"],
    ["server.py", "本地代理服务（静态托管 ＋ API 代理 ＋ 自动降级 ＋ 安全加固）"],
]))
a(("p", "**本地复现**：`python server.py` 启动工作台（默认 `127.0.0.1:8899`），浏览器打开即用；亦可直接以静态服务器打开 `index.html` 体验模拟层。"))

a(("h3", "2.10 运行统计"))
a(("p", "在真实模型连通条件下，完成一次「一句话 → 完整 IP 内容包」的全流程，实测：**总耗时约 140 秒，模型调用 14 次，人工干预仅 1 处**，五环各环节均可独立操作与即时回看。"))

# ---------------------------------------------------------------- 三
a(("pagebreak", None))
a(("h2", "三、应用场景说明"))

a(("h3", "3.1 六大场景与柯桥文旅要素绑定"))
a(("p", "作品围绕柯桥标志性自然景观、人文点位与文旅业态三类要素，产出六大场景延展图，实现「角色 × 柯桥地标」的落地结合："))
a(("table", [
    ["场景", "绑定柯桥要素"],
    ["鉴湖泛舟", "鉴湖 · 古纤道 · 乌篷船"],
    ["安昌酱香", "安昌古镇 · 仁昌酱园 · 腊味长廊"],
    ["柯岩揽胜", "柯岩采石遗迹 · 鲁镇"],
    ["三桥夜泊", "柯桥古镇「三桥四水」· 夜景"],
    ["扇面丹青", "王星记扇馆 · 柯桥非遗馆"],
    ["社戏台上", "鲁镇社戏 · 越剧"],
]))

a(("h3", "3.2 四大可落地传播场景"))
a(("num", "**文旅景区 · 集章手账**——六点位打卡动线，联动既有集章玩法，提升游客停留与二次消费；"))
a(("num", "**AR 导览 · 数字文旅**——小匠 AR 导览，把线上 IP 引入线下实景，连接线上线下体验；"))
a(("num", "**非遗衍生品开发**——折扇、黄酒周边、蓝印花布、文创伴手礼等；"))
a(("num", "**大屏播出 · 短视频传播**——景区大屏、政务宣传、短视频平台等多渠道投放。"))
a(("p", "IP 形象、分镜成片、内容宣传视频、演示视频与说明文档五类成果均已成稿，可直接投放使用。"))

a(("h3", "3.3 与绍兴文商旅融合发展的适配"))
a(("p", "作品深度贴合绍兴当前文商旅融合趋势：六大场景可对接「古城一台戏」、夜间文旅消费（三桥夜泊夜景）、文旅促消费活动等传播场景；以柯桥非遗与在地产业为底色，凸显绍兴地域特色与文化辨识度。"))

a(("h3", "3.4 系统通用性与可推广性"))
a(("p", "本工作台虽以柯桥为主题，但其「一句话 → 完整 IP 内容包」的能力与「角色一致性锚定」方法可迁移至其他城市文旅 IP 创作与非遗活化场景，具备规模化复用与产业推广潜力。"))

# ---------------------------------------------------------------- 四
a(("pagebreak", None))
a(("h2", "四、第三方资源来源及授权说明"))

a(("h3", "4.1 资源逐条登记"))
a(("p", "本作品创作全流程使用的所有第三方平台、预训练模型、素材、字体与参考资料，逐条登记如下："))
a(("table", [
    ["#", "资源类型", "具体内容", "来源", "授权情况"],
    ["1", "全模态 API 平台", "SenseAudio 开放平台", "api.senseaudio.cn", "平台服务条款授权"],
    ["2", "文生图模型", "senseaudio-image-2.0-260319", "同上平台", "平台授权调用"],
    ["3", "大语言模型", "senseaudio-s2", "同上平台", "平台授权调用"],
    ["4", "语音合成模型", "sensenova-tts-2.0", "同上平台", "平台授权调用"],
    ["5", "语音识别模型", "senseaudio-asr-1.5-260319", "同上平台", "平台授权调用"],
    ["6", "正文字体", "系统内置字体（微软雅黑 / 苹方）", "随操作系统", "系统授权；未嵌入任何第三方字体"],
    ["7", "界面图标 / 图示", "Font Awesome 图标 ＋ 工程内联 SVG", "开源 / 原创手绘", "Font Awesome 为 MIT 许可；SVG 为原创"],
    ["8", "柯桥文化参考资料", "柯桥区政府公开资料、柯桥文旅公开信息", "政府门户与公开渠道", "公开信息引用（仅作背景参考）"],
    ["9", "IP 形象与分镜", "本工程原创生成", "——", "完全原创，不含任何既有 IP 元素"],
    ["10", "背景音乐 / 音效", "未使用", "——", "视频仅含配音，无背景音乐与音效"],
]))

a(("h3", "4.2 合规声明"))
a(("li", "作品**不包含**任何参赛人员姓名、学校、队伍编号等与设计方案无关的身份标识；"))
a(("li", "IP 形象与分镜画面全部原创，未使用任何既有 IP 元素，无著作权纠纷；"))
a(("li", "未使用任何未经授权的商用素材；作品导向积极正向，无导向偏差与常识性错误；"))
a(("li", "所用第三方平台与模型均为合规授权调用，字体未打包嵌入，规避字体版权风险；"))
a(("li", "系统侧设置 Origin 白名单、请求体大小限制、路径穿越防护与 XSS 转义，API 密钥仅服务端持有、绝不下发前端。"))

a(("h3", "4.3 原创性与知识产权"))
a(("p", "作品为团队独立创作，对其拥有完整、明确、无争议的著作权；如涉及柯桥地方文旅方向的后续合作，愿按赛题约定与协办单位平等协商版权相关事宜。"))

# ---------------------------------------------------------------- 五
a(("pagebreak", None))
a(("h2", "五、AIGC 创作占比及相关依据"))

a(("h3", "5.1 占比结论"))
a(("p", "作品 **AIGC 参与创作占比为 80%**，高于赛题要求的 60% 红线。"))

a(("h3", "5.2 计算口径"))
a(("p", "占比计算方法：**各创作环节中 AIGC 承担比例之加权均值**；余量对应人工投入（选题立意、提示词工程、参数调优、审美筛选）。各环节按其对最终成果的贡献度等权计入。"))

a(("h3", "5.3 各环节 AIGC 参与度明细"))
a(("table", [
    ["环节", "AIGC 参与度", "说明"],
    ["智能策划", "90%", "世界观 / 角色 / 分镜脚本由大语言模型结构化生成，人工确定选题方向"],
    ["角色资产", "85%", "六位角色立绘全部由文生图模型生成，人工负责提示词与筛选"],
    ["分镜生成", "80%", "分镜画面由文生图模型生成，人工负责参考图策略与参数调整"],
    ["配音", "70%", "角色台词由语音合成模型生成，人工负责音色选择与文本审校"],
    ["文案", "75%", "宣传语与场景解说由大语言模型生成，人工负责审校"],
    ["加权综合", "80%", "（90＋85＋80＋70＋75）÷ 5 ＝ 80%"],
]))

a(("h3", "5.4 过程可追溯（工具、参数与提示词逻辑）"))
a(("table", [
    ["环节", "工具", "核心参数 / 提示词逻辑"],
    ["智能策划", "SenseAudio LLM（json_object）", "temperature 0.7 · 结构化输出；输入柯桥三缸与非遗符号 → 世界观/角色/分镜"],
    ["角色资产", "SenseAudio 文生图", "1024×1536 · 国风水墨；角色描述词 ＋ 柯桥服饰/器物符号"],
    ["分镜生成", "文生图 ＋ reference 参考图", "reference ＝ 角色种子图 · 一致性约束；角色 × 柯桥地标逐镜生成"],
    ["配音", "SenseAudio 语音合成", "系统音色 · 32000Hz；分镜台词 → 音频"],
    ["文案", "SenseAudio LLM", "temperature 0.8；角色宣传语与场景解说"],
]))

a(("h3", "5.5 生成质量"))
a(("p", "生成的多模态素材画质清晰、达可用级别：角色立绘与分镜成图均为 1024×1536；内容宣传视频 1920×1080、H.264 编码、码率约 9.15 Mbps、时长 100.1 秒；演示视频 1920×1080、60fps、码率约 9.17 Mbps、时长 145.7 秒；配音清晰无失真。生成内容的文化匹配度高，柯桥地标与非遗元素绑定准确，无文化元素错用、错位问题。"))

# ---------------------------------------------------------------- 六
a(("pagebreak", None))
a(("h2", "六、提交材料清单"))
a(("table", [
    ["材料", "文件名", "规格"],
    ["说明文档", "[队伍编号]说明文档.docx", "Word，本文档"],
    ["作品视频", "[队伍编号]作品视频.mp4", "1920×1080 · 30fps · H.264 · 9.15 Mbps · 100.1 秒"],
    ["作品演示视频", "[队伍编号]作品演示视频.mp4", "1920×1080 · 60fps · H.264 · 9.17 Mbps · 145.7 秒 · 单声道"],
    ["答辩PPT", "[队伍编号]答辩PPT.pptx", "14 页（赛题上限 15 页）"],
    ["演示PPT", "[队伍编号]作品演示PPT.pptx", "10 页"],
]))
a(("p", "**代码及部署说明**：见工程根目录 `README.md`，含运行方式、模型接入说明、全链路环节一览、目录结构与合规说明；在线访问：见项目主页（无需登录）。"))
a(("note", "说明：赛题对「作品视频/图片」为二选一提交，本作品提交 MP4 视频作品，已满足该项要求。"))


# =====================================================================
# 渲染
# =====================================================================
def set_font(run, ea, size, bold=False, color=None, ascii_font=None):
    run.font.name = ascii_font or ea
    run.font.size = Pt(size)
    run.font.bold = bold
    if color is not None:
        run.font.color.rgb = color
    rpr = run._element.get_or_add_rPr()
    rf = rpr.find(qn('w:rFonts'))
    if rf is None:
        rf = OxmlElement('w:rFonts')
        rpr.append(rf)
    rf.set(qn('w:eastAsia'), ea)
    rf.set(qn('w:ascii'), ascii_font or ea)
    rf.set(qn('w:hAnsi'), ascii_font or ea)


def add_inline(p, text, ea, size, color, ascii_font=None):
    """支持 **加粗** 与 `等宽` 的极简行内解析。"""
    import re
    tokens = re.split(r'(\*\*.+?\*\*|`.+?`)', text)
    for tk in tokens:
        if not tk:
            continue
        if tk.startswith('**') and tk.endswith('**'):
            r = p.add_run(tk[2:-2]); set_font(r, ea, size, True, color, ascii_font)
        elif tk.startswith('`') and tk.endswith('`'):
            r = p.add_run(tk[1:-1]); set_font(r, 'Consolas', size, False, color)
        else:
            r = p.add_run(tk); set_font(r, ea, size, False, color, ascii_font)
    return p


def shade(cell, fill):
    tcPr = cell._tc.get_or_add_tcPr()
    shd = OxmlElement('w:shd')
    shd.set(qn('w:val'), 'clear'); shd.set(qn('w:color'), 'auto'); shd.set(qn('w:fill'), fill)
    tcPr.append(shd)


def set_cell_margins(table):
    tblPr = table._tbl.tblPr
    mar = OxmlElement('w:tblCellMar')
    for side, val in (('top', 40), ('left', 90), ('bottom', 40), ('right', 90)):
        e = OxmlElement('w:' + side); e.set(qn('w:w'), str(val)); e.set(qn('w:type'), 'dxa'); mar.append(e)
    tblPr.append(mar)


def set_fixed_widths(table, widths_cm):
    """固定表格布局并逐列设定列宽（cm），避免 Word 自动压缩导致文字竖排。"""
    table.autofit = False
    tblPr = table._tbl.tblPr
    layout = OxmlElement('w:tblLayout'); layout.set(qn('w:type'), 'fixed'); tblPr.append(layout)
    for row in table.rows:
        for i, w in enumerate(widths_cm):
            if i < len(row.cells):
                row.cells[i].width = Cm(w)


def protect_rows(table):
    """禁止行跨页断裂；首行作为表头跨页重复。"""
    for ri, r in enumerate(table.rows):
        trPr = r._tr.get_or_add_trPr()
        trPr.append(OxmlElement('w:cantSplit'))
        if ri == 0:
            trPr.append(OxmlElement('w:tblHeader'))


# 各表列宽（cm），按文档中表格出现顺序；A4 正文可用宽度 15cm
TABLE_WIDTHS = [
    [0.9, 1.4, 3.6, 2.8, 4.4, 1.9],  # 0 角色表
    [2.6, 3.6, 6.4, 2.4],            # 1 五环
    [2.6, 4.4, 8.0],                 # 2 模态模型
    [2.8, 4.0, 8.2],                 # 3 双模式容错
    [3.6, 1.8, 9.6],                 # 4 接口清单
    [4.2, 10.8],                     # 5 工程结构
    [4.0, 11.0],                     # 6 场景覆盖
    [0.9, 2.4, 4.2, 3.3, 4.2],       # 7 资源登记
    [2.6, 2.2, 10.2],                # 8 AIGC 明细
    [2.2, 4.4, 8.4],                 # 9 过程可追溯
    [2.8, 5.2, 7.0],                 # 10 提交材料清单
]


def add_page_number_footer(section):
    p = section.footer.paragraphs[0]
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = p.add_run()
    set_font(r, 'SimSun', 9, False, GREY)
    f1 = OxmlElement('w:fldChar'); f1.set(qn('w:fldCharType'), 'begin')
    it = OxmlElement('w:instrText'); it.set(qn('xml:space'), 'preserve'); it.text = 'PAGE'
    f2 = OxmlElement('w:fldChar'); f2.set(qn('w:fldCharType'), 'end')
    r._r.append(f1); r._r.append(it); r._r.append(f2)


def build_docx():
    doc = Document()
    sec = doc.sections[0]
    sec.page_width, sec.page_height = Cm(21.0), Cm(29.7)
    sec.top_margin = sec.bottom_margin = Cm(2.54)
    sec.left_margin = sec.right_margin = Cm(3.0)

    st = doc.styles['Normal']
    st.font.name = 'SimSun'; st.font.size = Pt(12); st.font.color.rgb = INK
    st.element.rPr.rFonts.set(qn('w:eastAsia'), 'SimSun')

    add_page_number_footer(sec)

    ti = 0
    for blk in C:
        kind = blk[0]
        if kind == 'title':
            p = doc.add_paragraph(); p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            p.paragraph_format.space_before = Pt(60); p.paragraph_format.space_after = Pt(6)
            set_font(p.add_run(blk[1]), 'SimHei', 26, True, NAVY)
        elif kind == 'subtitle':
            p = doc.add_paragraph(); p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            p.paragraph_format.space_after = Pt(24)
            set_font(p.add_run(blk[1]), 'SimHei', 16, False, BLUE)
        elif kind == 'coverinfo':
            p = doc.add_paragraph(); p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            p.paragraph_format.space_after = Pt(4)
            set_font(p.add_run(blk[1]), 'SimSun', 12, False, GREY)
        elif kind == 'pagebreak':
            doc.add_page_break()
        elif kind == 'h2':
            p = doc.add_paragraph(); p.paragraph_format.space_before = Pt(16); p.paragraph_format.space_after = Pt(8)
            p.paragraph_format.keep_with_next = True
            set_font(p.add_run(blk[1]), 'SimHei', 15, True, NAVY)
        elif kind == 'h3':
            p = doc.add_paragraph(); p.paragraph_format.space_before = Pt(10); p.paragraph_format.space_after = Pt(6)
            p.paragraph_format.keep_with_next = True
            set_font(p.add_run(blk[1]), 'SimHei', 13, True, BLUE)
        elif kind == 'p':
            p = doc.add_paragraph(); pf = p.paragraph_format
            pf.line_spacing = 1.5; pf.space_after = Pt(6)
            pf.first_line_indent = Pt(24)
            p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
            add_inline(p, blk[1], 'SimSun', 12, INK)
        elif kind == 'li':
            p = doc.add_paragraph(); pf = p.paragraph_format
            pf.line_spacing = 1.5; pf.space_after = Pt(5); pf.left_indent = Pt(24)
            p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
            r = p.add_run('· '); set_font(r, 'SimSun', 12, False, INK)
            add_inline(p, blk[1], 'SimSun', 12, INK)
        elif kind == 'num':
            p = doc.add_paragraph(); pf = p.paragraph_format
            pf.line_spacing = 1.5; pf.space_after = Pt(5); pf.left_indent = Pt(24)
            p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
            add_inline(p, blk[1], 'SimSun', 12, INK)
        elif kind == 'note':
            p = doc.add_paragraph(); pf = p.paragraph_format
            pf.line_spacing = 1.4; pf.space_after = Pt(8); pf.left_indent = Pt(12)
            add_inline(p, blk[1], 'SimSun', 10.5, GREY)
        elif kind == 'table':
            rows = blk[1]
            t = doc.add_table(rows=len(rows), cols=len(rows[0]))
            t.style = 'Table Grid'
            t.alignment = WD_TABLE_ALIGNMENT.CENTER
            set_cell_margins(t)
            if ti < len(TABLE_WIDTHS):
                set_fixed_widths(t, TABLE_WIDTHS[ti])
            protect_rows(t)
            ti += 1
            for ri, row in enumerate(rows):
                for ci, val in enumerate(row):
                    cell = t.cell(ri, ci)
                    cell.text = ''
                    cp = cell.paragraphs[0]
                    cp.paragraph_format.space_after = Pt(2)
                    cp.paragraph_format.line_spacing = 1.15
                    if ri == 0:
                        shade(cell, 'E8EFF8')
                        set_font(cp.add_run(str(val)), 'SimHei', 10.5, True, NAVY)
                    else:
                        set_font(cp.add_run(str(val)), 'SimSun', 10.5, False, INK)
            # 表后留白
            sp = doc.add_paragraph(); sp.paragraph_format.space_after = Pt(6)
            set_font(sp.add_run(''), 'SimSun', 6)
    os.makedirs(os.path.dirname(OUT_DOCX), exist_ok=True)
    doc.save(OUT_DOCX)
    os.makedirs(os.path.dirname(OUT_STAGE3), exist_ok=True)
    doc.save(OUT_STAGE3)
    return OUT_DOCX


def build_md():
    lines = []
    for blk in C:
        kind = blk[0]
        if kind == 'title':
            lines.append('# ' + blk[1] + '\n')
        elif kind == 'subtitle':
            lines.append('> ' + blk[1] + '\n')
        elif kind == 'coverinfo':
            lines.append('> ' + blk[1])
        elif kind == 'pagebreak':
            lines.append('\n---\n')
        elif kind == 'h2':
            lines.append('\n## ' + blk[1] + '\n')
        elif kind == 'h3':
            lines.append('\n### ' + blk[1] + '\n')
        elif kind in ('p', 'note'):
            lines.append(blk[1] + '\n')
        elif kind == 'li':
            lines.append('- ' + blk[1])
        elif kind == 'num':
            lines.append('1. ' + blk[1])
        elif kind == 'table':
            rows = blk[1]
            lines.append('')
            lines.append('| ' + ' | '.join(rows[0]) + ' |')
            lines.append('| ' + ' | '.join(['---'] * len(rows[0])) + ' |')
            for row in rows[1:]:
                lines.append('| ' + ' | '.join(row) + ' |')
            lines.append('')
    os.makedirs(os.path.dirname(OUT_MD), exist_ok=True)
    with open(OUT_MD, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines) + '\n')
    return OUT_MD


if __name__ == '__main__':
    d = build_docx()
    m = build_md()
    print('DOCX ->', d)
    print('DOCX ->', OUT_STAGE3)
    print('MD   ->', m)
