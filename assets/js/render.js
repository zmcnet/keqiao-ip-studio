/* =========================================================
   柯桥·水乡IP造物台  ——  角色渲染器（模拟生成层）
   参数化 SVG 绘制六位水乡小匠：多视图 / 表情 / 服饰 / 场景
   ========================================================= */

(function () {
  function hatSVG(type, hairColor) {
    switch (type) {
      case "wuzhan": // 乌毡帽
        return `<ellipse cx="110" cy="62" rx="52" ry="12" fill="#2B2B2B"/>
                <path d="M74 62 Q78 34 110 34 Q142 34 146 62 Z" fill="#333"/>
                <ellipse cx="110" cy="62" rx="52" ry="10" fill="#262626"/>`;
      case "pot": // 酱缸盖帽
        return `<path d="M70 60 Q110 40 150 60 L150 66 Q110 52 70 66 Z" fill="#8C4A2F"/>
                <rect x="100" y="40" width="20" height="10" rx="5" fill="#6E3820"/>`;
      case "kerchief": // 蓝印花布头巾
        return `<path d="M64 70 Q110 40 156 70 Q110 62 64 70 Z" fill="${hairColor}"/>
                <path d="M150 66 q16 6 22 20 q-14 2 -24 -8 Z" fill="#2F5D8C"/>
                <circle cx="70" cy="70" r="4" fill="#2F5D8C"/><circle cx="150" cy="70" r="4" fill="#2F5D8C"/>`;
      case "headdress": // 越剧头饰
        return `<path d="M66 70 Q110 34 154 70 Q110 60 66 70 Z" fill="#1E1E1E"/>
                <circle cx="86" cy="60" r="5" fill="#C0392B"/><circle cx="110" cy="52" r="6" fill="#E4B23C"/>
                <circle cx="134" cy="60" r="5" fill="#C0392B"/>
                <path d="M64 70 q-10 14 -6 30" stroke="#C0392B" stroke-width="3" fill="none"/>
                <path d="M156 70 q10 14 6 30" stroke="#C0392B" stroke-width="3" fill="none"/>`;
      default:
        return "";
    }
  }

  function propSVG(type, color) {
    switch (type) {
      case "oar": // 船桨
        return `<g transform="rotate(24 176 178)"><rect x="173" y="140" width="7" height="86" rx="3" fill="#9A6B3F"/>
                <ellipse cx="176.5" cy="150" rx="10" ry="20" fill="#B58352"/></g>`;
      case "jar": // 小酒坛
        return `<g><ellipse cx="176" cy="186" rx="17" ry="18" fill="${color}"/>
                <rect x="164" y="162" width="24" height="10" rx="4" fill="#6E3820"/>
                <text x="176" y="192" font-size="13" text-anchor="middle" fill="#F3E2C0">酒</text></g>`;
      case "sausage": // 酱鸭腊肠挂饰
        return `<g><rect x="164" y="150" width="6" height="34" rx="3" fill="#7A3B22"/>
                <rect x="174" y="150" width="6" height="40" rx="3" fill="#8C4A2F"/>
                <rect x="184" y="150" width="6" height="30" rx="3" fill="#7A3B22"/></g>`;
      case "dyestick": // 染棒
        return `<g transform="rotate(18 176 180)"><rect x="173" y="146" width="6" height="70" rx="3" fill="#8A6B4A"/>
                <path d="M166 150 q10 -14 20 0 q-10 10 -20 0 Z" fill="#2F5D8C"/></g>`;
      case "fan": // 黑纸折扇
        return `<g transform="translate(158 150)"><path d="M0 40 A40 40 0 0 1 60 18 L40 40 Z" fill="#2B2B2B"/>
                <path d="M0 40 A40 40 0 0 1 60 18" stroke="#8C6B3F" stroke-width="2" fill="none"/>
                <path d="M6 40 L46 26 M20 40 L46 30 M34 40 L44 36" stroke="#8C6B3F" stroke-width="1.4"/></g>`;
      case "sleeve": // 越剧水袖
        return `<path d="M150 168 q34 6 40 40 q-20 -6 -30 -22 Z" fill="#F6D9D4" stroke="#C0392B" stroke-width="1.5"/>`;
      default:
        return "";
    }
  }

  function faceSVG(view, expression) {
    if (view === "back") return "";
    const head = 110, y = 104;
    let eyes;
    if (expression === "happy") {
      eyes = `<path d="M84 102 q8 -10 16 0" stroke="#2B2B2B" stroke-width="3.2" fill="none" stroke-linecap="round"/>
              <path d="M120 102 q8 -10 16 0" stroke="#2B2B2B" stroke-width="3.2" fill="none" stroke-linecap="round"/>`;
    } else if (expression === "wink") {
      eyes = `<ellipse cx="92" cy="104" rx="6" ry="8" fill="#2B2B2B"/><circle cx="90" cy="101" r="2" fill="#fff"/>
              <path d="M120 104 q8 -8 16 0" stroke="#2B2B2B" stroke-width="3" fill="none" stroke-linecap="round"/>`;
    } else {
      eyes = `<ellipse cx="92" cy="104" rx="6" ry="8.5" fill="#2B2B2B"/><ellipse cx="128" cy="104" rx="6" ry="8.5" fill="#2B2B2B"/>
              <circle cx="90" cy="101" r="2.2" fill="#fff"/><circle cx="126" cy="101" r="2.2" fill="#fff"/>`;
    }
    if (view === "side") {
      eyes = `<ellipse cx="124" cy="104" rx="6" ry="8.5" fill="#2B2B2B"/><circle cx="122" cy="101" r="2.2" fill="#fff"/>`;
    }
    const blush = view === "side"
      ? `<ellipse cx="138" cy="118" rx="9" ry="5" fill="#F5B7AE" opacity="0.8"/>`
      : `<ellipse cx="80" cy="119" rx="9" ry="5" fill="#F5B7AE" opacity="0.8"/><ellipse cx="140" cy="119" rx="9" ry="5" fill="#F5B7AE" opacity="0.8"/>`;
    const mouth = expression === "happy"
      ? `<path d="M104 121 q6 8 12 0" stroke="#B5483C" stroke-width="2.4" fill="none" stroke-linecap="round"/>`
      : `<path d="M106 122 q4 5 8 0" stroke="#B5483C" stroke-width="2.2" fill="none" stroke-linecap="round"/>`;
    const nos = view === "side" ? "" : `<path d="M110 112 l3 5 l-6 0 Z" fill="#E7B391" opacity="0.7"/>`;
    return eyes + blush + mouth + nos;
  }

  function costumePattern(costume, color2) {
    switch (costume) {
      case "lanhua":
        return `<g fill="#fff" opacity="0.85"><circle cx="88" cy="176" r="3"/><circle cx="110" cy="190" r="3"/>
                <circle cx="132" cy="176" r="3"/><circle cx="99" cy="205" r="3"/><circle cx="121" cy="205" r="3"/></g>`;
      case "jinxiu":
        return `<g stroke="${color2}" stroke-width="1.6" fill="none" opacity="0.9">
                <path d="M92 178 q18 -10 36 0"/><path d="M92 196 q18 -10 36 0"/></g>`;
      case "sumo":
        return `<g stroke="#2B2B2B" stroke-width="1.4" fill="none" opacity="0.5">
                <path d="M86 186 q24 12 48 0"/><circle cx="110" cy="196" r="3"/></g>`;
      default:
        return "";
    }
  }

  function kqCharSVG(char, opts = {}) {
    const view = opts.view || "front";
    const expression = opts.expression || "smile";
    const costume = opts.costume || "default";
    const c = char.color, c2 = char.color2, h = char.hair, sk = char.skin;
    const flip = view === "side" ? ' transform="scale(-1,1) translate(-220,0)"' : "";

    // 身体（袍）
    const body = `
      <path d="M70 152 Q110 138 150 152 L158 216 Q110 232 62 216 Z" fill="${c}"/>
      <path d="M70 152 Q110 138 150 152 L152 166 Q110 154 68 166 Z" fill="${c2}" opacity="0.55"/>
      ${costumePattern(costume, c2)}`;
    // 手臂
    const arms = `
      <rect x="58" y="158" width="20" height="52" rx="10" fill="${c}"/>
      <rect x="142" y="158" width="20" height="52" rx="10" fill="${c}"/>`;
    // 脚
    const feet = `<ellipse cx="92" cy="224" rx="15" ry="8" fill="#3A3A3A"/><ellipse cx="128" cy="224" rx="15" ry="8" fill="#3A3A3A"/>`;
    // 头
    const head = `<circle cx="110" cy="104" r="47" fill="${sk}"/>`;
    // 头发
    const hair = view === "back"
      ? `<path d="M63 104 Q63 50 110 50 Q157 50 157 104 Q150 84 110 80 Q70 84 63 104 Z" fill="${h}"/>
         <path d="M74 120 q6 60 -4 74 q20 -8 18 -60 Z" fill="${h}"/>`
      : `<path d="M64 100 Q64 52 110 52 Q156 52 156 100 Q140 78 110 78 Q80 78 64 100 Z" fill="${h}"/>`;
    const hat = hatSVG(char.hat, h);
    const face = faceSVG(view, expression);
    const prop = char.prop === "sleeve" ? propSVG("sleeve") : propSVG(char.prop, c);

    return `<svg viewBox="0 0 220 260" xmlns="http://www.w3.org/2000/svg" class="kq-char">
      <ellipse cx="110" cy="238" rx="62" ry="12" fill="#000" opacity="0.08"/>
      <g${flip}>
        ${feet}${body}${arms}
        ${head}${hair}${hat}${face}
        ${prop}
      </g>
    </svg>`;
  }

  /* 三视图：正 / 侧 / 背 */
  function kqCharViews(char, costume) {
    return `<div class="views-row">
      <div class="view-item">${kqCharSVG(char, { view: "front", costume })}<span>正视图</span></div>
      <div class="view-item">${kqCharSVG(char, { view: "side", costume })}<span>侧视图</span></div>
      <div class="view-item">${kqCharSVG(char, { view: "back", costume })}<span>背视图</span></div>
    </div>`;
  }

  /* 场景特征物（依据柯桥地标） */
  function sceneMotif(scene) {
    const a = scene.accent;
    switch (scene.id) {
      case "jianhu": // 鉴湖：乌篷船 + 水波
        return `<g><path d="M34 178 q28 14 56 0 q6 6 -4 10 l-48 0 q-10 -4 -4 -10 Z" fill="#2B3A33"/>
                <rect x="52" y="162" width="3" height="18" fill="#2B3A33"/>
                <path d="M20 200 q30 -8 60 0 M200 202 q30 -8 60 0" stroke="${a}" stroke-width="1.5" fill="none" opacity="0.6"/></g>`;
      case "anchang": // 安昌：酱缸一排 + 廊檐腊味
        return `<g><ellipse cx="46" cy="196" rx="15" ry="13" fill="#6E3820"/><ellipse cx="46" cy="188" rx="15" ry="5" fill="#8C4A2F"/>
                <ellipse cx="82" cy="198" rx="13" ry="11" fill="#6E3820"/><ellipse cx="82" cy="191" rx="13" ry="4" fill="#8C4A2F"/>
                <rect x="230" y="150" width="6" height="26" rx="3" fill="#7A3B22"/><rect x="246" y="150" width="6" height="32" rx="3" fill="#8C4A2F"/>
                <rect x="262" y="150" width="6" height="24" rx="3" fill="#7A3B22"/></g>`;
      case "keyan": // 柯岩：采石石宕
        return `<g fill="#8A9B8A" opacity="0.85"><path d="M226 190 L246 130 L266 190 Z"/>
                <path d="M262 190 L282 118 L302 190 Z"/><path d="M200 192 L214 156 L228 192 Z"/></g>`;
      case "sanqiao": // 三桥：三孔石拱桥 + 月
        return `<g><circle cx="252" cy="46" r="20" fill="#F5E7B8" opacity="0.9"/>
                <path d="M28 176 q44 -40 88 0 M188 172 q40 -34 80 0" stroke="#D9C08A" stroke-width="6" fill="none"/>
                <circle cx="72" cy="176" r="9" fill="${scene.ground}"/><circle cx="228" cy="172" r="8" fill="${scene.ground}"/></g>`;
      case "shanmian": // 扇面：折扇 + 墨点
        return `<g transform="translate(238 118)"><path d="M0 40 A44 44 0 0 1 66 16 L44 40 Z" fill="#2B2B2B"/>
                <path d="M0 40 A44 44 0 0 1 66 16" stroke="#8C6B3F" stroke-width="2" fill="none"/></g>
                <circle cx="60" cy="176" r="4" fill="${a}" opacity="0.6"/><circle cx="96" cy="188" r="5" fill="${a}" opacity="0.5"/>`;
      case "shexi": // 社戏：戏台 + 灯笼
        return `<g><rect x="214" y="150" width="76" height="8" rx="2" fill="#8C2E24"/>
                <rect x="222" y="158" width="6" height="30" fill="#7A2A20"/><rect x="276" y="158" width="6" height="30" fill="#7A2A20"/>
                <ellipse cx="238" cy="144" rx="7" ry="10" fill="#E4B23C"/><ellipse cx="266" cy="144" rx="7" ry="10" fill="#E4B23C"/></g>`;
      default:
        return "";
    }
  }

  /* 场景延展图：柯桥地标背景 + 角色 */
  function kqSceneSVG(char, scene, costume) {
    const dark = scene.id === "sanqiao";
    const titleColor = dark ? "#F5E7B8" : scene.accent;
    const barFill = dark ? "#16233A" : "#ffffff";
    return `<svg viewBox="0 0 320 240" xmlns="http://www.w3.org/2000/svg" class="kq-scene">
      <defs><linearGradient id="sky-${scene.id}" x1="0" y1="0" x2="0" y2="1">
        <stop offset="0" stop-color="${scene.sky}"/><stop offset="1" stop-color="${dark ? "#3A4A68" : "#ffffff"}"/></linearGradient></defs>
      <rect width="320" height="240" fill="url(#sky-${scene.id})"/>
      ${dark ? "" : `<circle cx="258" cy="52" r="24" fill="#fff" opacity="0.6"/>`}
      <path d="M0 150 Q80 128 160 150 T320 150 L320 190 L0 190 Z" fill="${scene.ground}" opacity="0.55"/>
      <path d="M0 178 Q90 160 180 178 T320 178 L320 240 L0 240 Z" fill="${scene.accent}" opacity="0.42"/>
      <path d="M40 176 q40 -34 80 0" stroke="${scene.accent}" stroke-width="5" fill="none" opacity="0.7"/>
      ${sceneMotif(scene)}
      <g transform="translate(78 76) scale(0.60)">${kqCharSVG(char, { costume }).replace(/^<svg[^>]*>|<\/svg>$/g, "")}</g>
      <rect x="12" y="206" width="296" height="26" rx="8" fill="${barFill}" opacity="${dark ? 0.45 : 0.82}"/>
      <text x="24" y="224" font-size="13" fill="${titleColor}" font-family="sans-serif">${scene.name} · ${scene.spot}</text>
    </svg>`;
  }

  window.KQ_RENDER = { kqCharSVG, kqCharViews, kqSceneSVG };
})();
