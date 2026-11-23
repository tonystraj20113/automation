import base64, json, os, re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

def env(name, default=""):
    return os.environ.get(name, default)

def load_config():
    return json.loads((ROOT / "config" / "channels.json").read_text(encoding="utf-8"))

def prompt(name, **kwargs):
    text = (ROOT / "prompts" / f"{name}.md").read_text(encoding="utf-8")
    for k, v in kwargs.items():
        text = text.replace("{" + k + "}", str(v))
    return text

def decode_secret(name):
    raw = env(name)
    if not raw:
        return None
    try:
        return base64.b64decode(raw)
    except Exception:
        return None

def slug(text):
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")[:60] or "story"

def write_json(path, data):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")

def read_json(path, default=None):
    p = Path(path)
    return json.loads(p.read_text(encoding="utf-8")) if p.exists() else default

def ensure_dirs():
    for d in ("output", "data", "output/audio", "output/frames"):
        (ROOT / d).mkdir(parents=True, exist_ok=True)
