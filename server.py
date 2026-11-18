#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
柯桥·水乡IP造物台 —— 本地代理服务（安全加固版）
================================================
作用：
  1) 托管工作台静态页面（推荐用同源访问，无需 CORS）
  2) 代理 SenseAudio 全模态 API，API Key 只存在于服务端，绝不下发前端
  3) 上游不可用时优雅降级（返回 mode=sim，前端自动回退模拟层）
  4) 安全加固：Origin 白名单、请求体大小限制、路径穿越防护、密钥脱敏

启动：  python server.py
访问：  http://127.0.0.1:8899/index.html
密钥：  优先读环境变量 SENSEAUDIO_API_KEY，其次 config.json
"""
import os, json, base64, uuid, mimetypes, io
import urllib.request, urllib.error
from urllib.parse import urlparse
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

ROOT = os.path.dirname(os.path.abspath(__file__))
CONFIG_PATH = os.path.join(ROOT, "config.json")


def load_config():
    try:
        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}


CONFIG = load_config()
API_KEY = os.environ.get("SENSEAUDIO_API_KEY") or CONFIG.get("api_key", "")
BASE = CONFIG.get("base_url", "https://api.senseaudio.cn").rstrip("/")
MODELS = CONFIG.get("models", {})
VOICE = CONFIG.get("voice_id", "child_0001_a")
IMG_SIZE = CONFIG.get("image_size", "1024x1536")
TEAM_ID = os.environ.get("TEAM_ID") or CONFIG.get("team_id", "队伍编号")
PORT = int(os.environ.get("PORT", CONFIG.get("port", 8899)))

# 允许的浏览器来源（host 白名单）；非白名单来源一律拒绝，防止代理被跨站滥用。
# 本地默认放行回环地址；线上通过环境变量 ALLOWED_HOSTS 追加（逗号分隔），例如：
#   ALLOWED_HOSTS=demo.kybll.cn,www.demo.kybll.cn
ALLOW_HOSTS = {"127.0.0.1", "localhost", "::1"}
_extra_hosts = os.environ.get("ALLOWED_HOSTS", "").strip()
if _extra_hosts:
    ALLOW_HOSTS |= {h.strip().lower() for h in _extra_hosts.split(",") if h.strip()}
MAX_BODY = 24 * 1024 * 1024  # 24MB

# A3 @ 300dpi 版面像素（赛题图片规格）
A3_300 = (3508, 4961)


# ---------------- 上游调用 ----------------
def call_json(path, payload, timeout=120, method="POST"):
    body = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(BASE + path, data=body, method=method, headers={
        "Authorization": "Bearer " + API_KEY,
        "Content-Type": "application/json",
    })
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.loads(r.read().decode("utf-8"))


def build_multipart(fields, file_field, filename, file_bytes, file_ct="audio/mpeg"):
    boundary = "----kqstudio" + uuid.uuid4().hex
    out = bytearray()
    for k, v in fields.items():
        out += f"--{boundary}\r\nContent-Disposition: form-data; name=\"{k}\"\r\n\r\n{v}\r\n".encode()
    out += (f"--{boundary}\r\nContent-Disposition: form-data; name=\"{file_field}\"; "
            f"filename=\"{filename}\"\r\nContent-Type: {file_ct}\r\n\r\n").encode()
    out += file_bytes + b"\r\n" + f"--{boundary}--\r\n".encode()
    return bytes(out), "multipart/form-data; boundary=" + boundary


def call_multipart(path, fields, filename, file_bytes, timeout=180):
    body, ct = build_multipart(fields, "file", filename, file_bytes)
    req = urllib.request.Request(BASE + path, data=body, method="POST", headers={
        "Authorization": "Bearer " + API_KEY, "Content-Type": ct})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.loads(r.read().decode("utf-8"))


# ---------------- 业务处理器 ----------------
def handle_plan(payload):
    """① 结构化策划：LLM 输出项目模型（世界观 + 角色 + 分镜脚本）"""
    theme = str(payload.get("theme", "柯桥水乡旅游IP"))[:200]
    sys_p = "你是绍兴柯桥文旅的AIGC导演。只输出JSON，不要markdown代码块，不要任何解释。"
    user = (f"围绕主题「{theme}」创作一套柯桥水乡旅游IP项目。输出JSON，结构：\n"
            '{"world":{"name":"","theme":"","origin":"","core":"","play":""},'
            '"characters":[{"name":"","element":"","persona":"","visual":"","color":"#hex"}],'
            '"shots":[{"no":1,"scene":"","spot":"","shotType":"","action":"","dialogue":"","emotion":""}]}\n'
            "要求：characters 输出 3-6 个，深度绑定柯桥「三缸文化」（酒缸/酱缸/染缸）与非遗"
            "（黄酒/仁昌酱油/蓝印花布/王星记扇/越剧）；shots 输出 6 个分镜，"
            "覆盖鉴湖、安昌古镇、柯岩、柯桥三桥、王星记扇馆、鲁镇社戏等柯桥真实地标。"
            "color 用 #RRGGBB 十六进制。")
    d = call_json("/v1/chat/completions", {
        "model": MODELS.get("llm", "senseaudio-s2"),
        "messages": [{"role": "system", "content": sys_p}, {"role": "user", "content": user}],
        "temperature": 0.7, "response_format": {"type": "json_object"},
    }, timeout=120)
    txt = d["choices"][0]["message"]["content"].strip()
    if txt.startswith("```"):
        txt = txt.split("```")[1]
        if txt.startswith("json"):
            txt = txt[4:]
    return {"mode": "live", "project": json.loads(txt), "model": d.get("model")}


def handle_text(payload):
    prompt = str(payload.get("prompt", ""))[:4000]
    d = call_json("/v1/chat/completions", {
        "model": MODELS.get("llm", "senseaudio-s2"),
        "messages": [{"role": "system", "content": "你是文旅文案专家，语言凝练有感染力，每条不超过60字。"},
                     {"role": "user", "content": prompt}],
        "temperature": 0.8, "response_format": {"type": "json_object"},
    }, timeout=90)
    return {"mode": "live", "text": d["choices"][0]["message"]["content"].strip()}


def handle_image(payload):
    """②③ 图像生成：角色立绘 / 分镜图（支持 reference 参考图保角色一致性）"""
    prompt = str(payload.get("prompt", ""))[:2000]
    body = {"model": MODELS.get("image", "senseaudio-image-2.0-260319"), "prompt": prompt}
    ref = payload.get("reference")
    if ref:
        body["reference"] = ref
    else:
        body["size"] = payload.get("size", IMG_SIZE)  # 无参考图时尺寸必填
    d = call_json("/v1/image/sync", body, timeout=300)
    url = d.get("url") or (d.get("data") or {}).get("url")
    return {"mode": "live", "url": url}


def handle_tts(payload):
    """语音合成：返回 base64 音频（平台返回 hex，此处统一转 base64）"""
    d = call_json("/v1/t2a_v2", {
        "model": MODELS.get("tts", "sensenova-tts-2.0"),
        "text": str(payload.get("text", ""))[:10000],
        "stream": False,
        "voice_setting": {"voice_id": payload.get("voice_id", VOICE), "speed": 1, "vol": 1, "pitch": 0},
        "audio_setting": {"format": "mp3", "sample_rate": 32000, "bitrate": 128000, "channel": 2},
    }, timeout=90)
    audio = (d.get("data") or {}).get("audio")
    if not audio:
        raise RuntimeError("no audio in response")
    try:
        audio = base64.b64encode(bytes.fromhex(audio)).decode("ascii")
    except ValueError:
        pass
    return {"mode": "live", "audio": audio, "format": "mp3"}


def handle_asr(payload):
    b64 = str(payload.get("audio", ""))
    filename = str(payload.get("filename", "audio.webm"))
    raw = base64.b64decode(b64.split(",")[-1])
    fields = {"model": payload.get("model", MODELS.get("asr", "senseaudio-asr-1.5-260319")),
              "language": payload.get("language", "zh")}
    ct = "audio/webm" if filename.endswith("webm") else "audio/mpeg"
    d = call_multipart("/v1/audio/transcriptions", fields, filename, raw, timeout=120)
    return {"mode": "live", "text": d.get("text", "")}


def handle_fetch_image(payload):
    """把远程/本地图片取回并转 Data URI —— 供前端安全地生成"角色参考图"（规避 CORS）"""
    url = str(payload.get("url", ""))
    if url.startswith("assets/") or url.startswith("/assets/"):
        fp = os.path.join(ROOT, url.lstrip("/"))
        with open(fp, "rb") as f:
            raw = f.read()
        ct = mimetypes.guess_type(fp)[0] or "image/jpeg"
    else:
        p = urlparse(url)
        if p.scheme not in ("http", "https"):
            raise ValueError("unsupported url")
        req = urllib.request.Request(url, headers={"User-Agent": "KQStudio/1.0"})
        with urllib.request.urlopen(req, timeout=60) as r:
            raw = r.read()
        ct = r.headers.get("Content-Type", "image/jpeg").split(";")[0]
    return {"mode": "live", "datauri": f"data:{ct};base64," + base64.b64encode(raw).decode("ascii")}


def handle_export_sheet(payload):
    """把生成图放大到 A3 @300dpi 并写入 DPI 元数据 —— 满足赛题图片规格"""
    url = str(payload.get("url", ""))
    name = str(payload.get("name", "作品图片"))
    if url.startswith("assets/") or url.startswith("/assets/"):
        fp = os.path.join(ROOT, url.lstrip("/"))
        with open(fp, "rb") as f:
            raw = f.read()
    else:
        req = urllib.request.Request(url, headers={"User-Agent": "KQStudio/1.0"})
        with urllib.request.urlopen(req, timeout=60) as r:
            raw = r.read()
    from PIL import Image
    im = Image.open(io.BytesIO(raw)).convert("RGB")
    # 等比缩放后居中贴到 A3 版面
    canvas = Image.new("RGB", A3_300, (255, 255, 255))
    ratio = min(A3_300[0] / im.width, A3_300[1] / im.height)
    nw, nh = max(1, int(im.width * ratio)), max(1, int(im.height * ratio))
    im = im.resize((nw, nh), Image.LANCZOS)
    canvas.paste(im, ((A3_300[0] - nw) // 2, (A3_300[1] - nh) // 2))
    buf = io.BytesIO()
    canvas.save(buf, "JPEG", quality=92, dpi=(300, 300))
    return {"mode": "live", "filename": f"{name}_A3_300dpi.jpg",
            "data": base64.b64encode(buf.getvalue()).decode("ascii")}


ROUTES = {
    "/api/plan": handle_plan, "/api/text": handle_text, "/api/image": handle_image,
    "/api/tts": handle_tts, "/api/asr": handle_asr,
    "/api/fetch_image": handle_fetch_image, "/api/export_sheet": handle_export_sheet,
}


# ---------------- HTTP 服务 ----------------
class Handler(BaseHTTPRequestHandler):
    def log_message(self, *a):
        pass

    def _origin_ok(self):
        o = self.headers.get("Origin")
        if not o:
            return True                     # 同源/非浏览器请求
        try:
            return urlparse(o).hostname in ALLOW_HOSTS
        except Exception:
            return False

    def _send(self, code, body, ctype="application/json", allow_cors=False):
        data = body if isinstance(body, bytes) else json.dumps(body, ensure_ascii=False).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", ctype + "; charset=utf-8")
        self.send_header("X-Content-Type-Options", "nosniff")
        if allow_cors:
            self.send_header("Access-Control-Allow-Origin", self.headers.get("Origin"))
            self.send_header("Vary", "Origin")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def do_OPTIONS(self):
        if not self._origin_ok():
            return self._send(403, {"error": "forbidden origin"})
        self.send_response(204)
        self.send_header("Access-Control-Allow-Origin", self.headers.get("Origin"))
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.send_header("Access-Control-Allow-Methods", "POST, GET, OPTIONS")
        self.send_header("Vary", "Origin")
        self.end_headers()

    def do_GET(self):
        if self.path == "/api/health":
            if not self._origin_ok():
                return self._send(403, {"error": "forbidden origin"})
            # 只暴露前端所需的最小字段（不回传上游地址/模型名，减少信息暴露）
            return self._send(200, {"ok": True, "key_loaded": bool(API_KEY),
                                    "team_id": TEAM_ID})
        path = self.path.split("?")[0]
        if path == "/":
            path = "/index.html"
        fp = os.path.normpath(os.path.join(ROOT, path.lstrip("/")))
        # 路径穿越防护：必须严格位于 ROOT 之内
        try:
            inside = os.path.commonpath([ROOT, fp]) == ROOT and os.path.isfile(fp)
        except ValueError:
            inside = False
        if not inside:
            return self._send(404, {"error": "not found"})
        ct = mimetypes.guess_type(fp)[0] or "application/octet-stream"
        with open(fp, "rb") as f:
            self._send(200, f.read(), ct)

    def do_POST(self):
        if not self._origin_ok():
            return self._send(403, {"error": "forbidden origin"})
        path = self.path.split("?")[0]
        fn = ROUTES.get(path)
        if not fn:
            return self._send(404, {"error": "no route"})
        length = int(self.headers.get("Content-Length", 0) or 0)
        if length > MAX_BODY:
            return self._send(413, {"error": "payload too large"})
        try:
            payload = json.loads(self.rfile.read(length).decode("utf-8")) if length else {}
        except Exception:
            payload = {}
        try:
            return self._send(200, fn(payload))
        except urllib.error.HTTPError as e:
            detail = e.read().decode("utf-8", "ignore")[:300]
            return self._send(200, {"mode": "sim", "error": f"upstream {e.code}: {detail}",
                                    "hint": "上游鉴权或参数失败，已降级到模拟层"})
        except Exception as e:
            return self._send(200, {"mode": "sim", "error": f"{type(e).__name__}: {e}",
                                    "hint": "上游不可用，已降级到模拟层"})


if __name__ == "__main__":
    print("=" * 60)
    print("  柯桥·水乡IP造物台 · 本地代理服务（安全加固版）")
    print(f"  地址： http://127.0.0.1:{PORT}/index.html")
    print(f"  上游： {BASE}")
    print(f"  API Key： {'已加载 ' + API_KEY[:6] + '***' if API_KEY else '未配置（将以模拟层运行）'}")
    print(f"  队伍编号： {TEAM_ID}")
    print(f"  安全： Origin 白名单 {sorted(ALLOW_HOSTS)} · 请求体上限 {MAX_BODY // 1048576}MB")
    print("=" * 60)
    ThreadingHTTPServer(("127.0.0.1", PORT), Handler).serve_forever()
