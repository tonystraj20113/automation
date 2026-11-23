"""Script generation through the free Groq API (OpenAI-compatible)."""
import json, re, requests
from .utils import env, prompt

GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"

def _chat(system, user):
    key = env("GROQ_API_KEY")
    if not key:
        raise RuntimeError("GROQ_API_KEY is not set")
    resp = requests.post(GROQ_URL, headers={
        "Authorization": f"Bearer {key}",
        "Content-Type": "application/json",
    }, json={
        "model": env("GROQ_MODEL", "llama-3.3-70b-versatile"),
        "messages": [
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
        "temperature": 0.8,
        "max_tokens": 1600,
    }, timeout=120)
    resp.raise_for_status()
    return resp.json()["choices"][0]["message"]["content"]

def _parse_json(text):
    text = text.strip()
    m = re.search(r"\{.*\}", text, re.S)
    if not m:
        raise ValueError("No JSON object in model response")
    return json.loads(m.group(0))

def generate_short(topic, signals):
    raw = _chat("You are a precise script writer. Output JSON only.",
                prompt("script_short", topic=topic, signals=signals))
    data = _parse_json(raw)
    required = ("title", "lines", "story_style", "captions")
    for k in required:
        if k not in data:
            raise ValueError(f"Missing script field: {k}")
    if data["story_style"] not in ("ukiyo-e", "claymation"):
        data["story_style"] = "claymation"
    n = len(data["captions"])
    if not isinstance(data["lines"], list) or not data["lines"]:
        raise ValueError("Script has no narration lines")
    if not isinstance(data["scenes"], list) or len(data["scenes"]) != n:
        data["scenes"] = [{} for _ in range(n)]
    return data

def generate_long(stories):
    raw = _chat("You are a precise script writer. Output JSON only.",
                prompt("script_long", stories=json.dumps(stories)))
    data = _parse_json(raw)
    if "chapters" not in data or "title" not in data:
        raise ValueError("Bad long script")
    return data
