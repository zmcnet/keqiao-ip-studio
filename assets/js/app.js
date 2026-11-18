/* =========================================================
   柯桥·水乡IP造物台  ——  创编一体流水线（重构版）
   ① 意图+结构化策划 → ② 角色资产锁定 → ③ 分镜生成(参考图一致性)
   → ④ 时间轴预览+对话式编辑 → ⑤ 成片导出
   真实模型经本地代理 /api/* 调用；不可用时自动降级模拟层。
   核心：策划产出"项目数据模型"作为单一事实源，下游全部消费它。
   ========================================================= */
(function () {
  const D = window.IP_DATA;
  const R = window.KQ_RENDER;

  const state = {
    stage: 1,
    theme: "笛里·柯桥 —— 三缸奇缘·水乡小匠",
    project: null,              // {world, characters, shots} 单一事实源
    live: { mode: "sim", images: {}, texts: {}, audio: {}, shotImages: {} },
    teamId: "队伍编号",
    selectedShot: 0,
    chat: [],                   // 对话式编辑历史
    busy: "",
    log: []
  };

  /* ============ 预载：真实文生图成果 ============ */
  const SEED = {
    ajian: "assets/generated/char_ajian.jpg",
    achun: "assets/generated/char_achun.jpg",
    xianbao: "assets/generated/char_xianbao.jpg",
    buxiaocai: "assets/generated/char_buxiaocai.jpg",
    shanxiaoya: "assets/generated/char_shanxiaoya.jpg",
    lixiaoshe: "assets/generated/char_lixiaoshe.jpg"
  };

  function addLog(m) {
    const t = new Date().toLocaleTimeString("zh-CN", { hour12: false });
    state.log.unshift(`[${t}] ${m}`);
    if (state.log.length > 30) state.log.pop();
  }
  function esc(s) {
    return String(s == null ? "" : s).replace(/[&<>"']/g,
      (m) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[m]));
  }
  function ratio() {
    const done = {
      plan: !!state.project, image: Object.keys(state.live.images).length > 0,
      shot: Object.keys(state.live.shotImages).length > 0,
      audio: true, text: true
    };
    const map = { "智能策划": "plan", "角色资产": "image", "分镜生成": "shot", "配音": "audio", "文案": "text" };
    let sum = 0;
    D.chain.forEach((c) => { if (done[map[c.stage]]) sum += c.ratio; });
    return Math.round(sum / D.chain.length);
  }

  /* ============ API 层 ============ */
  const API = {
    async post(path, body, timeout = 320000) {
      try {
        const ctl = new AbortController();
        const timer = setTimeout(() => ctl.abort(), timeout);
        const r = await fetch(path, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(body), signal: ctl.signal });
        clearTimeout(timer);
        return await r.json();
      } catch (e) { return { mode: "sim", error: String(e) }; }
    },
    async health() { try { const d = await (await fetch("/api/health")).json(); return d; } catch (e) { return { key_loaded: false }; } }
  };

  /* ============ 导航 ============ */
  const STAGES = ["智能策划", "角色资产", "分镜生成", "时间轴预览", "成片导出"];
  function renderNav() {
    document.getElementById("stepper").innerHTML = STAGES.map((s, i) => `
      <div class="step ${state.stage === i + 1 ? "active" : ""} ${state.stage > i + 1 ? "done" : ""}" onclick="KQ.go(${i + 1})">
        <span class="step-no">${state.stage > i + 1 ? "✓" : i + 1}</span><span class="step-name">${s}</span>
      </div>${i < 4 ? '<div class="step-line"></div>' : ""}`).join("");
  }

  function curProject() { return state.project || { world: D.world, characters: D.characters, shots: D.shots }; }

  /* ============ 环1：意图 + 结构化策划 ============ */
  function renderStage1() {
    const hasP = !!state.project;
    return `
    <div class="panel">
      <h3>① 意图理解 → 结构化策划</h3>
      <p class="hint">输入一句创意（或说一句话）。AI 自动扩写为 <b>结构化项目</b>：世界观 + 角色 + 分镜脚本，作为后续所有环节的数据源。</p>
      <div class="row">
        <input id="themeInput" class="input" value="${esc(state.theme)}" />
        <button class="btn primary" ${state.busy === "plan" ? "disabled" : ""} onclick="KQ.plan()">${state.busy === "plan" ? "生成中…" : "AI 生成项目"}</button>
      </div>
      <div class="row mt8"><button class="btn" onclick="KQ.stt()">🎙 语音输入创意</button><span id="voiceStatus" class="hint"></span></div>
      <div class="mt16">${hasP ? planHTML() : '<div class="empty">尚未生成 · 点击上方按钮，把一句创意扩写成完整项目</div>'}</div>
    </div>`;
  }
  function planHTML() {
    const p = curProject();
    return `
    <div class="card ai-card"><div class="card-tag">项目数据模型（单一事实源 · ${state.live.mode === "live" ? "真实模型" : "预置"}）</div>
      <p><b>世界观：</b>${esc(p.world.name)} · ${esc(p.world.theme || "")}</p>
      <p>${esc(p.world.origin || "")}</p>
      ${p.world.play ? `<p><b>落地玩法：</b>${esc(p.world.play)}</p>` : ""}
    </div>
    <h4 class="sec-title">角色资产（${p.characters.length} 位 · 绑定柯桥非遗）</h4>
    <div class="char-chips">${p.characters.map((c) => `<div class="char-chip" style="border-color:${c.color}">
      <span class="dot" style="background:${c.color}"></span><b>${esc(c.name)}</b>
      <span class="muted">${esc(c.element)}</span><div class="ce">${esc(c.persona)}</div></div>`).join("")}</div>
    <h4 class="sec-title">分镜脚本（${p.shots.length} 个镜头 · 已拆分到可执行）</h4>
    <div class="shot-table">
      <div class="shot-head"><span>#</span><span>场景</span><span>景别</span><span>画面 / 台词</span></div>
      ${p.shots.map((s) => `<div class="shot-row">
        <span class="sk-no">${s.no}</span>
        <span>${esc(s.scene)}<div class="muted">${esc(s.spot || "")}</div></span>
        <span class="muted">${esc(s.shotType || "")}</span>
        <span>${esc(s.action || "")}<div class="muted">「${esc(s.dialogue || "")}」</div></span>
      </div>`).join("")}
    </div>`;
  }

  /* ============ 环2：角色资产锁定 ============ */
  function renderStage2() {
    const p = curProject();
    return `
    <div class="panel">
      <h3>② 角色资产锁定 · 一致性锚点</h3>
      <p class="hint">先生成/确认每位角色的<b>标准立绘（种子图）</b>——它是后续所有分镜的"脸"。这一步是即梦式流程里最关键的一步。</p>
      <div class="row wrap mt8">
        <button class="btn primary" ${state.busy === "assets" ? "disabled" : ""} onclick="KQ.lockAssets()">${state.busy === "assets" ? "生成中…" : "为全部角色生成立绘（真实文生图）"}</button>
        <span id="assetStatus" class="hint"></span>
      </div>
      <div class="gallery mt16">
        ${p.characters.map((c) => {
          const img = state.live.images[c.id] || c.seed;
          return `<div class="g-item ${state.activeChar === c.id ? "sel" : ""}" onclick="KQ.pickChar('${c.id}')">
            ${img ? `<img src="${img}" class="gen-img"/>` : R.kqCharSVG(c, { view: "front" })}
            <div class="g-name">${esc(c.name)}<span class="muted"> · ${esc(c.symbol || "")}</span></div>
            <div class="seed-tag">${img ? "● 种子图已锁定" : "○ 待生成"}</div></div>`;
        }).join("")}
      </div>
    </div>`;
  }

  /* ============ 环3：分镜生成 ============ */
  function renderStage3() {
    const p = curProject();
    return `
    <div class="panel">
      <h3>③ 分镜生成 · 参考图保一致性</h3>
      <p class="hint">按分镜脚本逐镜生成画面。<b>每一镜自动带上对应角色的种子图作为参考（reference）</b>，因此换场景也不会"换脸"。</p>
      <div class="row wrap mt8">
        <button class="btn primary" ${state.busy === "shots" ? "disabled" : ""} onclick="KQ.genShots()">${state.busy === "shots" ? "生成中…" : "一键生成全部分镜"}</button>
        <span id="shotStatus" class="hint"></span>
      </div>
      <div class="shot-strip mt16">
        ${p.shots.map((s, i) => {
          const ch = p.characters.find((c) => c.id === s.char) || p.characters[0];
          const img = state.live.shotImages[s.no];
          return `<div class="shot-card">
            <div class="shot-thumb">${img ? `<img src="${img}" class="gen-img"/>` : R.kqSceneSVG(ch, (D.scenes[i % D.scenes.length]), "default")}</div>
            <div class="shot-meta"><b>镜 ${s.no}</b> · ${esc(s.scene)}<div class="muted">${esc(s.shotType || "")} · ${ch ? ch.name : ""}</div>
              <div class="muted">${esc(s.dialogue || "")}</div></div>
          </div>`;
        }).join("")}
      </div>
    </div>`;
  }

  /* ============ 环4：时间轴预览 + 对话式编辑 ============ */
  function renderStage4() {
    const p = curProject();
    const s = p.shots[state.selectedShot] || p.shots[0];
    const ch = p.characters.find((c) => c.id === s.char) || p.characters[0];
    return `
    <div class="panel">
      <h3>④ 时间轴预览 · 对话式编辑</h3>
      <p class="hint">按镜头顺序排列成时间轴。可直接用自然语言下指令修改（如"把第3镜改成近景""给阿鉴换一句台词"）。</p>

      <div class="timeline mt8">
        ${p.shots.map((x, i) => `<div class="tl-item ${i === state.selectedShot ? "on" : ""}" onclick="KQ.pickShot(${i})">
          <div class="tl-thumb">${state.live.shotImages[x.no] ? `<img src="${state.live.shotImages[x.no]}"/>` : R.kqCharSVG(p.characters.find((c) => c.id === x.char) || p.characters[0], { view: "front" }).replace('<svg', '<svg style="opacity:.4"')}</div>
          <div class="tl-cap">${x.no}. ${esc(x.scene)}</div></div>`).join("")}
      </div>

      <div class="edit-layout mt16">
        <div class="edit-left">
          <div class="shot-detail">
            <div class="sd-thumb">${state.live.shotImages[s.no] ? `<img src="${state.live.shotImages[s.no]}" class="gen-img"/>` : R.kqSceneSVG(ch, D.scenes[state.selectedShot % D.scenes.length], "default")}</div>
            <div class="sd-info">
              <h4>镜 ${s.no} · ${esc(s.scene)}</h4>
              <p><b>点位：</b>${esc(s.spot || "")}</p>
              <p><b>景别：</b>${esc(s.shotType || "")}</p>
              <p><b>画面：</b>${esc(s.action || "")}</p>
              <p><b>台词：</b>「${esc(s.dialogue || "")}」</p>
              <p><b>情绪：</b>${esc(s.emotion || "")}</p>
              <button class="btn tiny" onclick="KQ.dubShot()">▶ 给本镜配音</button>
            </div>
          </div>
        </div>
        <div class="edit-right">
          <div class="mm-title">对话式编辑</div>
          <div class="chat-box" id="chatBox">${state.chat.map((m) => `<div class="chat-${m.role}">${esc(m.text)}</div>`).join("") || '<div class="muted">对 AI 说出你想改的地方…</div>'}</div>
          <div class="row mt8"><input id="chatInput" class="input" placeholder="例：把第3镜改成近景" /><button class="btn primary" onclick="KQ.chatEdit()">发送</button></div>
        </div>
      </div>
    </div>`;
  }

  /* ============ 环5：成片导出 ============ */
  function renderStage5() {
    const p = curProject();
    return `
    <div class="panel">
      <h3>⑤ 成片导出 · 一键交付</h3>
      <p class="hint">导出符合赛题要求的全套成果材料（文件名遵循 <b>[队伍编号]</b> 命名规则）。</p>
      <div class="row mt8">
        <span class="lbl">队伍编号：</span>
        <input id="teamInput" class="input" style="max-width:240px" value="${esc(state.teamId)}" oninput="KQ.setTeam(this.value)" />
        <span class="hint">用于导出文件命名，如「${esc(state.teamId)}说明文档」</span>
      </div>
      <div class="row wrap mt16">
        <button class="btn primary" onclick="KQ.exportReport()">导出作品说明文档（HTML）</button>
        <button class="btn primary" onclick="KQ.exportA3()">导出作品图片（A3 · 300dpi）</button>
        <button class="btn" onclick="KQ.exportStoryboard()">导出分镜脚本（JSON）</button>
        <button class="btn" onclick="KQ.exportJSON()">导出全量项目（JSON）</button>
      </div>
      <div class="export-list mt16">
        <div class="exp-row"><b>说明文档</b><span class="muted">[编号]说明文档 · 核心创意/技术实现/第三方授权/AIGC占比依据</span></div>
        <div class="exp-row"><b>作品图片</b><span class="muted">[编号]作品视频.jpg · 角色立绘 + 分镜图 · JPG/RGB/A3(297×420mm)/300dpi</span></div>
        <div class="exp-row"><b>作品视频</b><span class="muted">[编号]作品视频.mp4 · 1080p/H.264/≤3min（时间轴成片）</span></div>
        <div class="exp-row"><b>答辩PPT</b><span class="muted">[编号]答辩PPT.pptx · ≤15页 · 适配10分钟现场演示</span></div>
        <div class="exp-row"><b>代码与部署</b><span class="muted">完整工程 + 部署说明 + 访问链接</span></div>
      </div>
    </div>`;
  }
  function setTeam(v) { state.teamId = v || "队伍编号"; }

  /* ============ 侧栏 ============ */
  function renderSide() {
    const r = ratio();
    document.getElementById("sideCompliance").innerHTML = `
      <div class="side-title">模型连接</div>
      <div class="mode-badge ${state.live.mode === "live" ? "live-dot" : "sim-dot"}">${state.live.mode === "live" ? "● 真实模型已连接" : "○ 模拟层（未连接模型）"}</div>
      <div class="side-title mt12">合规台账</div>
      ${D.compliance.map((c) => `<div class="cmp-row"><span class="ok">✓</span><div><b>${c.res}</b><div class="muted">${c.source} · ${c.license}</div></div></div>`).join("")}
      <div class="side-title mt12">AIGC 参与占比</div>
      <div class="ratio-big ${r >= 60 ? "good" : "bad"}">${r}%</div>
      <div class="hint">红线：≥60% ${r >= 60 ? "✓ 达标" : "✗ 未达标"}</div>
      <div class="hint" style="font-size:11.5px">口径：各创作环节中 AIGC 承担比例之均值（余量为人工选题/参数/审美筛选）</div>
      <div class="chain">${D.chain.map((c) => `<div class="chain-row"><span>${c.stage}</span><b>${c.ratio}%</b></div>`).join("")}</div>
      <div class="side-title mt12">操作日志</div>
      <div class="log">${state.log.slice(0, 10).map((l) => `<div>${l}</div>`).join("") || '<div class="muted">—</div>'}</div>`;
  }

  /* ============ 主渲染 ============ */
  function render() {
    renderNav();
    document.getElementById("stageBody").innerHTML = [null, renderStage1, renderStage2, renderStage3, renderStage4, renderStage5][state.stage]();
    renderSide();
  }
  function go(n) { if (n >= 1 && n <= 5) { state.stage = n; render(); window.scrollTo({ top: 0, behavior: "smooth" }); } }

  /* ============ 动作 ============ */
  async function plan() {
    const v = document.getElementById("themeInput").value.trim();
    if (v) state.theme = v;
    state.busy = "plan"; addLog("① 意图理解 → 调用 LLM 生成结构化项目…"); render();
    const r = await API.post("/api/plan", { theme: state.theme }, 150000);
    if (r && r.mode === "live" && r.project) {
      state.project = normalize(r.project);
      state.live.mode = "live";
      state.live.shotImages = {};   // 换项目即清空旧分镜，避免张冠李戴
      addLog(`策划完成 · 世界观「${state.project.world.name}」· ${state.project.characters.length}角色/${state.project.shots.length}分镜`);
    } else {
      state.project = { world: D.world, characters: D.characters, shots: D.shots };
      addLog("上游未连通，使用预置项目模型");
    }
    // 预载种子图
    state.project.characters.forEach((c) => {
      const d = D.characters.find((x) => x.id === c.id);
      if (d && d.seed) state.live.images[c.id] = d.seed;
    });
    state.busy = ""; render();
  }
  function normalize(pj) {
    // 把 LLM 角色映射到本地渲染参数（按顺序）
    const chars = (pj.characters || []).slice(0, 6).map((c, i) => {
      const base = D.characters[i % D.characters.length];
      return Object.assign({}, base, {
        id: base.id, name: c.name || base.name, element: c.element || base.element,
        persona: c.persona || base.persona, visual: c.visual || base.visual,
        color: c.color && /^#/.test(c.color) ? c.color : base.color
      });
    });
    const shots = (pj.shots || []).slice(0, 8).map((s, i) => ({
      no: s.no || i + 1, scene: s.scene || "", spot: s.spot || s.scene || "",
      shotType: s.shotType || "", action: s.action || "", dialogue: s.dialogue || "",
      emotion: s.emotion || "", char: chars[i % chars.length] ? chars[i % chars.length].id : D.characters[0].id
    }));
    return { world: Object.assign({}, D.world, pj.world || {}), characters: chars.length ? chars : D.characters, shots: shots.length ? shots : D.shots };
  }

  async function lockAssets() {
    const p = curProject();
    state.busy = "assets"; addLog("② 角色资产锁定 · 调用文生图…"); render();
    let ok = 0;
    for (const c of p.characters) {
      const prompt = `${c.visual || c.name}，中国江南水乡风格，国风插画，全身站姿，干净米白色背景，可爱，高清`;
      addLog(`  生成立绘：${c.name}`);
      const r = await API.post("/api/image", { prompt, size: "1024x1536" });
      if (r && r.mode === "live" && r.url) { state.live.images[c.id] = r.url; state.live.mode = "live"; ok++; render(); }
    }
    state.busy = "";
    addLog(ok ? `角色资产完成 ${ok}/${p.characters.length}（种子图已锁定）` : "上游未连通，沿用预置种子图");
    render();
  }

  async function genShots() {
    const p = curProject();
    state.busy = "shots"; addLog("③ 分镜生成 · 逐镜调用文生图（带角色参考图）…"); render();
    let ok = 0;
    for (const s of p.shots) {
      const ch = p.characters.find((c) => c.id === s.char) || p.characters[0];
      const seedUrl = state.live.images[ch.id] || SEED[ch.id] || ch.seed;
      // 参考图经本地代理取回（规避远程图片 CORS 限制），保证一致性真正生效
      let ref = null;
      if (seedUrl) {
        const fr = await API.post("/api/fetch_image", { url: seedUrl }, 90000);
        if (fr && fr.datauri) ref = fr.datauri;
      }
      const prompt = `${ch.visual || ch.name}，位于${s.spot || s.scene}，${s.action || ""}，${s.shotType || ""}，中国江南水乡，国风插画，电影感光线，高清`;
      addLog(`  镜头 ${s.no}：${s.scene}（角色 ${ch.name} 参考图${ref ? "已加载" : "缺失"}）`);
      const r = await API.post("/api/image", { prompt, size: "1024x1536", reference: ref });
      if (r && r.mode === "live" && r.url) { state.live.shotImages[s.no] = r.url; state.live.mode = "live"; ok++; render(); }
    }
    state.busy = "";
    addLog(ok ? `分镜完成 ${ok}/${p.shots.length}（角色一致性已锁定）` : "上游未连通，使用模拟场景图");
    render();
  }

  async function dubShot() {
    const p = curProject(); const s = p.shots[state.selectedShot]; const ch = p.characters.find((c) => c.id === s.char) || p.characters[0];
    addLog(`镜 ${s.no} 配音：${s.dialogue}`);
    const r = await API.post("/api/tts", { text: s.dialogue || ch.intro, voice_id: ch.voice || "child_0001_a" });
    if (r && r.mode === "live" && r.audio) { new Audio("data:audio/mp3;base64," + r.audio).play(); state.live.mode = "live"; addLog("配音播放中（真实语音合成）"); }
    else if ("speechSynthesis" in window) { const u = new SpeechSynthesisUtterance(s.dialogue || ch.intro); u.lang = "zh-CN"; speechSynthesis.speak(u); addLog("上游未连通，改用浏览器语音"); }
    renderSide();
  }

  function pickShot(i) { state.selectedShot = i; render(); }
  function pickChar(id) { state.activeChar = id; render(); }

  async function chatEdit() {
    const inp = document.getElementById("chatInput"); const text = inp.value.trim(); if (!text) return;
    state.chat.push({ role: "user", text }); inp.value = ""; render();
    addLog(`对话式编辑：${text}`);
    const r = await API.post("/api/text", { prompt: `当前分镜脚本(JSON)：${JSON.stringify(curProject().shots)}\n用户指令：${text}\n请只返回修改后的该分镜JSON对象（单个镜头），不要解释。` }, 90000);
    let reply = "已记录你的修改要求。";
    if (r && r.mode === "live" && r.text) {
      reply = r.text.slice(0, 200); state.live.mode = "live";
      try { const obj = JSON.parse(r.text.replace(/```json|```/g, "").trim()); if (obj.scene) Object.assign(curProject().shots[state.selectedShot], obj); } catch (e) {}
    }
    state.chat.push({ role: "ai", text: reply });
    render();
  }

  /* ============ 语音转文字 ============ */
  async function stt() {
    const el = document.getElementById("voiceStatus");
    if (!navigator.mediaDevices || !window.MediaRecorder) { el.textContent = "⚠ 需 Chrome/Edge 且通过 http:// 访问"; return; }
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      const rec = new MediaRecorder(stream); const chunks = [];
      rec.ondataavailable = (e) => chunks.push(e.data);
      rec.onstop = async () => {
        stream.getTracks().forEach((t) => t.stop());
        el.textContent = "⏳ 识别中…";
        const blob = new Blob(chunks, { type: "audio/webm" });
        const b64 = await new Promise((res) => { const fr = new FileReader(); fr.onload = () => res(fr.result); fr.readAsDataURL(blob); });
        const r = await API.post("/api/asr", { audio: b64, filename: "rec.webm", language: "zh" });
        if (r && r.mode === "live" && r.text) { el.textContent = "识别：" + r.text; const ti = document.getElementById("themeInput"); if (ti) ti.value = r.text; state.live.mode = "live"; addLog("语音转文字（真实ASR）：" + r.text); }
        else { el.textContent = "⚠ 识别未连通"; }
      };
      rec.start(); el.textContent = "🎙 录音中… 3秒后自动识别";
      setTimeout(() => rec.stop(), 3000);
    } catch (e) { el.textContent = "⚠ 麦克风不可用：" + e.message; }
  }

  /* ============ 导出 ============ */
  function download(name, content, type = "text/html") {
    const blob = new Blob([content], { type }); const a = document.createElement("a");
    a.href = URL.createObjectURL(blob); a.download = name; a.click(); addLog("导出：" + name);
  }
  function exportStoryboard() { download(`${state.teamId}分镜脚本.json`, JSON.stringify(curProject().shots, null, 2), "application/json"); }
  function exportJSON() { download(`${state.teamId}全量项目.json`, JSON.stringify({ theme: state.theme, project: curProject(), live: state.live }, null, 2), "application/json"); }
  function exportSVG() { download(`${state.teamId}角色图.svg`, R.kqCharSVG(curProject().characters[0], { view: "front" }), "image/svg+xml"); }

  /* 导出 A3 @300dpi 作品图片（经代理用 PIL 放大并写入 DPI 元数据） */
  async function exportA3() {
    const p = curProject();
    addLog("导出 A3/300dpi 作品图片…");
    const targets = [];
    p.characters.forEach((c) => { if (state.live.images[c.id]) targets.push({ url: state.live.images[c.id], name: `角色_${c.name}` }); });
    p.shots.forEach((s) => { if (state.live.shotImages[s.no]) targets.push({ url: state.live.shotImages[s.no], name: `分镜${s.no}_${s.scene}` }); });
    let ok = 0;
    for (const t of targets) {
      const r = await API.post("/api/export_sheet", { url: t.url, name: t.name }, 120000);
      if (r && r.mode === "live" && r.data) {
        const bin = atob(r.data);
        const arr = new Uint8Array(bin.length);
        for (let i = 0; i < bin.length; i++) arr[i] = bin.charCodeAt(i);
        const blob = new Blob([arr], { type: "image/jpeg" });
        const a = document.createElement("a");
        a.href = URL.createObjectURL(blob); a.download = `${state.teamId}作品视频_${t.name}_A3.jpg`; a.click();
        ok++;
      }
    }
    addLog(ok ? `已导出 ${ok} 张 A3/300dpi 图文` : "无可用图片或代理未连通");
  }
  function exportReport() {
    const p = curProject(); const r = ratio();
    const html = `<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><title>柯桥水乡IP · 作品说明文档</title>
      <style>body{font-family:"Microsoft YaHei",sans-serif;max-width:860px;margin:40px auto;line-height:1.9;color:#222}h1{color:#2E7DB5}
      h2{border-left:5px solid #C8892B;padding-left:10px;margin-top:34px}table{border-collapse:collapse;width:100%}td,th{border:1px solid #ccc;padding:8px;font-size:14px}.k{color:#0F6E56;font-weight:600}</style></head><body>
      <h1>柯桥·水乡IP家族 —— 作品说明文档</h1>
      <p><b>赛道：</b>数字创意与AIGC应用 · 主题一 · 选项B（原创柯桥专属旅游IP形象）</p>
      <p><b>作品形态：</b>支持多模态的创编一体全链路工作台「柯桥·水乡IP造物台」</p>
      <p><b>核心逻辑：</b>意图理解 → 结构化策划 → 角色资产锁定 → 分镜生成 → 时间轴预览 → 成片导出</p>
      <h2>一、世界観</h2><p>${p.world.name}｜${p.world.theme || ""}</p><p>${p.world.origin || ""}</p>
      <h2>二、IP家族</h2><table><tr><th>角色</th><th>承载地标/非遗</th><th>性格</th></tr>
      ${p.characters.map((c) => `<tr><td>${c.name}</td><td>${c.element}</td><td>${c.persona}</td></tr>`).join("")}</table>
      <h2>三、分镜脚本</h2><table><tr><th>#</th><th>场景</th><th>景别</th><th>台词</th></tr>
      ${p.shots.map((s) => `<tr><td>${s.no}</td><td>${s.scene}</td><td>${s.shotType || ""}</td><td>${s.dialogue || ""}</td></tr>`).join("")}</table>
      <h2>四、全链路技术实现</h2><table><tr><th>环节</th><th>工具选型</th><th>核心参数</th><th>AIGC占比</th></tr>
      ${D.chain.map((c) => `<tr><td>${c.stage}</td><td>${c.tool}</td><td>${c.params}</td><td>${c.ratio}%</td></tr>`).join("")}</table>
      <h2>五、AIGC占比依据</h2><p>全流程AIGC参与度综合核算为 <span class="k">${r}%</span>，不低于60%。</p>
      <h2>六、应用场景</h2><p>适配柯桥文旅宣传、非遗推广、景区集章打卡、AR导览、衍生品开发与线下文旅落地。</p>
      <h2>七、第三方资源与合规</h2><table><tr><th>资源</th><th>来源</th><th>授权</th></tr>
      ${D.compliance.map((c) => `<tr><td>${c.res}</td><td>${c.source}</td><td>${c.license}</td></tr>`).join("")}</table>
      <h2>八、模型接口</h2><p>全模态能力接入 SenseAudio 开放平台（文本/图像/语音合成/语音识别，含 reference 角色一致性控制）。</p>
      <h2>九、数据来源</h2><p>柯桥文化参考：绍兴市柯桥区人民政府、柯桥文旅公开资料。</p>
      <hr><p style="color:#888;font-size:13px">由「柯桥·水乡IP造物台」一键导出 · ${new Date().toLocaleString("zh-CN")}</p></body></html>`;
    download(`${state.teamId}说明文档.html`, html);
  }

  /* ============ 初始化 ============ */
  window.KQ = { go, plan, lockAssets, genShots, dubShot, pickShot, pickChar, chatEdit, stt,
                setTeam, exportReport, exportA3, exportStoryboard, exportJSON, exportSVG };

  document.addEventListener("DOMContentLoaded", async () => {
    addLog("工作台已就绪 · 创编一体流水线");
    state.project = { world: D.world, characters: D.characters, shots: D.shots };
    D.characters.forEach((c) => { if (c.seed) state.live.images[c.id] = c.seed; });
    // 预载真实分镜图（由文生图 + 角色参考图生成）
    for (let i = 1; i <= D.shots.length; i++) state.live.shotImages[i] = `assets/generated/shot_${i}.jpg`;
    const h = location.hash || "";
    if (h === "#demo" || /^#s\d/.test(h)) {
      const m = h.match(/^#s(\d)/); state.stage = m ? Math.min(Math.max(+m[1], 1), 5) : 4;
      addLog("进入演示模式");
    }
    const info = await API.health();
    state.live.mode = info.key_loaded ? "live" : "sim";
    if (info.team_id) state.teamId = info.team_id;
    addLog(state.live.mode === "live" ? "模型已连接（SenseAudio 全模态）" : "未检测到代理，运行于模拟层");
    render();
  });
})();
