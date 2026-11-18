/* =========================================================
   柯桥·水乡IP造物台  ——  项目数据内核（创编一体模型）
   单一事实源：策划产出 → 下游全链路消费
   结构：world / characters(含种子图) / shots(分镜脚本) / 色卡 / 证据链 / 台账
   ========================================================= */

const IP_DATA = {
  /* ---------- 世界观 ---------- */
  world: {
    name: "笛里·柯桥",
    theme: "三缸奇缘 · 水乡小匠",
    origin: "东晋柯亭，蔡邕取柯亭竹制笛，笛声引动鉴湖千年水气，凝作六位「水乡小匠」，守着柯桥的山水、古镇与人情。",
    core: "柯桥的元气藏在三口古缸里——酒缸（醇）、酱缸（鲜）、染缸（彩）。小匠们的使命，是守护「三缸灵脉」，把柯桥之美带向四方。",
    spirit: "越地匠心的「守」与「传」：一劈一磨的耐心、雨淋不透的坚守、千年不息的传承。",
    play: "「三缸集章 · 水乡寻韵」——六位小匠驻守柯桥六大真实点位，游客凭集章手账打卡，结合 AR 导览与非遗衍生品，形成可沉浸、可复用的文旅玩法。"
  },

  /* ---------- 角色资产（含渲染参数 + 种子图 + 生成提示词） ---------- */
  characters: [
    {
      id: "ajian", name: "阿鉴", element: "鉴湖 · 乌篷船",
      persona: "温和 · 善引路 · 慢生活", symbol: "鉴湖水纹",
      color: "#2E7DB5", color2: "#BFE0F2", hair: "#23506E", skin: "#FCE3C8",
      hat: "wuzhan", prop: "oar", voice: "male_0004_a",
      intro: "我是阿鉴，鉴湖的水之子。坐上我的乌篷船，带你把柯桥看个够。",
      visual: "Q版卡通吉祥物，柯桥水乡小匠，戴黑色乌毡帽，水蓝色披风带水波纹，手持木船桨，温和少年",
      seed: "assets/generated/char_ajian.jpg"
    },
    {
      id: "achun", name: "阿醇", element: "绍兴黄酒酿制技艺（国家级非遗）",
      persona: "憨厚 · 豪爽 · 热心肠", symbol: "酒坛",
      color: "#C8892B", color2: "#F3E2C0", hair: "#7A4A12", skin: "#FCE3C8",
      hat: "none", prop: "jar", voice: "male_0018_a",
      intro: "阿拉阿醇，鉴湖水酿的酒最暖身。来一碗，交个朋友！",
      visual: "Q版卡通吉祥物，柯桥酿酒小匠，琥珀金色调，怀抱小酒坛，脸颊微醺红晕，憨厚开朗的少年",
      seed: "assets/generated/char_achun.jpg"
    },
    {
      id: "xianbao", name: "鲜宝", element: "仁昌酱园母子酱油（省级非遗）· 安昌古镇",
      persona: "勤恳 · 守时 · 爱「晒」", symbol: "酱缸",
      color: "#8C4A2F", color2: "#E7CDB8", hair: "#4A2412", skin: "#F7DCC0",
      hat: "pot", prop: "sausage", voice: "child_0001_b",
      intro: "我是鲜宝，安昌的老味道都在这口酱缸里。晒足一百八十天，才有这一口鲜。",
      visual: "Q版卡通吉祥物，柯桥酱园小掌柜，酱棕色，头顶酱缸盖帽，腰间挂酱鸭腊肠，勤恳的小伙计",
      seed: "assets/generated/char_xianbao.jpg"
    },
    {
      id: "buxiaocai", name: "布小彩", element: "染缸 · 蓝印花布 · 中国轻纺城",
      persona: "灵巧 · 爱美 · 会变装", symbol: "蓝印花布",
      color: "#2F5D8C", color2: "#E8EEF5", hair: "#1E3A57", skin: "#FCE3C8",
      hat: "kerchief", prop: "dyestick", voice: "child_0001_a",
      intro: "我是布小彩！一缸靛蓝，能染出会跳舞的颜色，要不要给你变个装？",
      visual: "Q版卡通吉祥物，柯桥染缸姑娘，靛蓝与白色，系蓝印花布围裙，手持染棒，灵巧爱美的少女",
      seed: "assets/generated/char_buxiaocai.jpg"
    },
    {
      id: "shanxiaoya", name: "扇小雅", element: "王星记扇（国家级非遗 · 86道工序「半把伞」）",
      persona: "风雅 · 睿智 · 爱丹青", symbol: "折扇",
      color: "#2F6B4F", color2: "#EFE9D8", hair: "#243B2C", skin: "#FCE3C8",
      hat: "none", prop: "fan", voice: "male_0004_a",
      intro: "在下扇小雅。这把黑纸扇，雨淋不透、日晒不翘，扇面之上，能装下整条鉴湖。",
      visual: "Q版卡通吉祥物，柯桥制扇匠人，竹青与墨黑色，手持黑纸折扇，风雅睿智的文人",
      seed: "assets/generated/char_shanxiaoya.jpg"
    },
    {
      id: "lixiaoshe", name: "梨小社", element: "鲁镇 · 水乡社戏 · 越剧",
      persona: "热情 · 爱唱演 · 人来疯", symbol: "水袖",
      color: "#C0392B", color2: "#F6D9D4", hair: "#2A1512", skin: "#FCE3C8",
      hat: "headdress", prop: "sleeve", voice: "child_0001_a",
      intro: "锣鼓一响，就是我的场子！鲁镇的社戏台上，咱们不见不散呀～",
      visual: "Q版卡通吉祥物，柯桥鲁镇社戏越剧演员，水袖红色戏服，脸谱妆容，热情活泼的少年",
      seed: "assets/generated/char_lixiaoshe.jpg"
    }
  ],

  /* ---------- 分镜脚本（宣传内容分镜 · 覆盖柯桥地标） ---------- */
  shots: [
    { no: 1, scene: "鉴湖晨雾", spot: "鉴湖 · 古纤道", shotType: "大远景 · 缓慢推近", char: "ajian", emotion: "悠远·宁静",
      action: "乌篷船划破鉴湖晨雾，阿鉴立于船头回望远山", dialogue: "桨声欸乃，柯桥的水，醒了。" },
    { no: 2, scene: "安昌酱香", spot: "安昌古镇 · 仁昌酱园", shotType: "中景 · 跟拍", char: "xianbao", emotion: "烟火·温暖",
      action: "鲜宝走过挂满腊味的廊檐，身后酱缸排成行", dialogue: "晒足一百八十天，才是安昌的老味道。" },
    { no: 3, scene: "柯岩揽胜", spot: "柯岩 · 采石遗迹", char: "achun", shotType: "全景 · 上升", emotion: "豪迈·开阔",
      action: "阿醇抱酒坛立于柯岩石宕前，仰头畅饮", dialogue: "鉴湖水酿的酒，配得上这一方山水！" },
    { no: 4, scene: "三桥夜泊", spot: "柯桥古镇 · 三桥四水", char: "buxiaocai", shotType: "近景 · 缓摇", emotion: "梦幻·灵巧",
      action: "布小彩在三桥月下抖开一匹蓝印花布，纹样流动", dialogue: "一缸靛蓝，染出会跳舞的颜色。" },
    { no: 5, scene: "扇面丹青", spot: "王星记扇馆 · 柯桥非遗馆", char: "shanxiaoya", shotType: "特写 · 推近", emotion: "风雅·专注",
      action: "扇小雅挥毫于黑纸扇面，山水渐次浮现", dialogue: "一扇之间，装得下整条鉴湖。" },
    { no: 6, scene: "社戏台上", spot: "鲁镇 · 社戏台", char: "lixiaoshe", shotType: "中景 · 环绕", emotion: "热烈·欢腾",
      action: "梨小社甩起水袖登台，台下座无虚席", dialogue: "锣鼓一响，柯桥的故事就开演啦！" }
  ],

  /* ---------- 场景底图（模拟层 / 分镜占位用，绑定柯桥地标） ---------- */
  scenes: [
    { id: "jianhu", name: "鉴湖泛舟", spot: "鉴湖 · 古纤道 · 乌篷船", char: "ajian", sky: "#CFE8F5", ground: "#5AA0C9", accent: "#2E7DB5" },
    { id: "anchang", name: "安昌酱香", spot: "安昌古镇 · 仁昌酱园 · 腊味长廊", char: "xianbao", sky: "#F3E4CB", ground: "#A9713F", accent: "#8C4A2F" },
    { id: "keyan", name: "柯岩揽胜", spot: "柯岩采石遗迹 · 鉴湖水酿", char: "achun", sky: "#E4EFE0", ground: "#5E8C5A", accent: "#C8892B" },
    { id: "sanqiao", name: "三桥夜泊", spot: "柯桥古镇「三桥四水」· 夜景", char: "buxiaocai", sky: "#2B3A55", ground: "#16233A", accent: "#C8892B" },
    { id: "shanmian", name: "扇面丹青", spot: "王星记扇馆 · 柯桥非遗馆", char: "shanxiaoya", sky: "#EFE9D8", ground: "#9AA98C", accent: "#2F6B4F" },
    { id: "shexi", name: "社戏台上", spot: "鲁镇社戏台 · 越剧", char: "lixiaoshe", sky: "#F6D9D4", ground: "#B5483C", accent: "#C0392B" }
  ],

  /* ---------- 非遗色卡（供图像识别匹配） ---------- */
  colorCards: [
    { name: "鉴湖水蓝", hex: "#2E7DB5", char: "ajian", note: "鉴湖 · 乌篷船" },
    { name: "黄酒琥珀", hex: "#C8892B", char: "achun", note: "绍兴黄酒" },
    { name: "母子酱棕", hex: "#8C4A2F", char: "xianbao", note: "仁昌酱园" },
    { name: "蓝印靛蓝", hex: "#2F5D8C", char: "buxiaocai", note: "蓝印花布" },
    { name: "黑纸竹青", hex: "#2F6B4F", char: "shanxiaoya", note: "王星记扇" },
    { name: "越剧水袖红", hex: "#C0392B", char: "lixiaoshe", note: "鲁镇社戏" }
  ],

  /* ---------- AIGC 证据链 ---------- */
  chain: [
    { stage: "智能策划", tool: "SenseAudio LLM (json_object)", params: "temperature 0.7 · 结构化输出", prompt: "柯桥三缸文化 → 世界观/角色/分镜脚本", ratio: 90 },
    { stage: "角色资产", tool: "SenseAudio 文生图", params: "1024×1536 · 国风水墨", prompt: "锁定角色种子图，作为一致性锚点", ratio: 85 },
    { stage: "分镜生成", tool: "文生图 + reference 参考图", params: "reference=角色种子图 · 一致性约束", prompt: "角色 × 柯桥地标，逐镜生成", ratio: 80 },
    { stage: "配音", tool: "SenseAudio 语音合成", params: "系统音色 · 32000Hz", prompt: "分镜台词 → 音频", ratio: 70 },
    { stage: "文案", tool: "SenseAudio LLM", params: "temperature 0.8", prompt: "角色宣传语与场景解说", ratio: 75 }
  ],

  /* ---------- 合规台账（如实标注，杜绝"写了却没用"） ---------- */
  compliance: [
    { res: "全模态 API 平台", type: "平台", source: "SenseAudio 开放平台（api.senseaudio.cn）", license: "平台服务条款授权", ok: true,
      note: "文本/图像/语音均经该平台接口生成，授权以平台服务条款为准" },
    { res: "文生图模型", type: "模型", source: "senseaudio-image-2.0-260319", license: "平台授权调用", ok: true },
    { res: "大语言模型", type: "模型", source: "senseaudio-s2", license: "平台授权调用", ok: true },
    { res: "语音合成 / 识别模型", type: "模型", source: "sensenova-tts-2.0 / senseaudio-asr-1.5", license: "平台授权调用", ok: true },
    { res: "正文字体", type: "字体", source: "系统内置字体（微软雅黑 / 苹方）", license: "随操作系统授权，未嵌入第三方字体", ok: true,
      note: "工程未打包任何第三方字体文件，规避字体版权风险" },
    { res: "界面图标 / 图示", type: "素材", source: "工程内联 SVG 手绘（原创）", license: "原创，无第三方素材", ok: true },
    { res: "柯桥文化资料", type: "参考素材", source: "柯桥区人民政府 / 柯桥文旅公开资料", license: "公开信息引用（仅作背景参考）", ok: true },
    { res: "IP 形象与分镜", type: "生成内容", source: "本工程通过上述模型原创生成", license: "原创，不含任何既有 IP 元素", ok: true }
  ],
};

window.IP_DATA = IP_DATA;
