"""Topic picking and Gneef-grammar story generation for the Roblox Studio film."""
import json, re
from datetime import datetime, timezone

from .scripts import _chat, _parse_json
from .utils import ROOT, prompt, read_json, write_json

BANNED = re.compile(r"\b(roblox|blood|gore|gun|kill|suicide|nazi|terror|porn|fuck|shit)\b", re.I)


def next_topic(override=""):
    cfg = read_json(ROOT / "config" / "topics.json", {})
    topics = cfg.get("topics", [])
    if override:
        for t in topics:
            if override.lower() in (t["id"] + " " + t["title"]).lower():
                return t
        return {"id": "custom", "title": override, "hook": override, "score": 8.0}
    pool = [t for t in topics if t.get("status") != "done"] or topics
    pool = sorted(pool, key=lambda t: -float(t.get("score", 0)))
    # Rotate inside the top band so every run is a different story.
    idx = datetime.now(timezone.utc).timetuple().tm_yday % min(3, len(pool))
    return pool[idx]


def lessons():
    perf = read_json(ROOT / "data" / "performance.json", {})
    return json.dumps(perf.get("lessons", []))[:2500]


def generate(topic, signals=""):
    from .utils import env
    if not env("GROQ_API_KEY"):
        # Zero-secret mode: ship the pre-approved, hand-checked story so the
        # very first cloud run can render and upload without waiting on keys.
        fallback = read_json(ROOT / "config" / "fallback_stories.json", {})
        key = topic.get("id", "lost-property")
        if key not in fallback:
            key = "lost-property"
        data = json.loads(json.dumps(fallback[key]))
        print(f"[story] using approved fallback: {data['title'].encode('ascii', 'replace').decode()}")
        return data
    try:
        raw = _chat("You are an original short-story writer. Output JSON only.",
                    prompt("script_roblox", topic=topic.get("hook") or topic.get("title"),
                           signals=str(signals)[:3500], lessons=lessons()))
    except Exception as exc:
        print(f"[story] Groq unavailable ({exc}); using approved fallback")
        fallback = read_json(ROOT / "config" / "fallback_stories.json", {})
        return json.loads(json.dumps(fallback.get(topic.get("id"), fallback["lost-property"])))
    data = _parse_json(raw)
    for key, n in (("lines", 15), ("captions", 15), ("scenes", 15)):
        if not isinstance(data.get(key), list) or len(data[key]) != n:
            raise ValueError(f"script field {key} must have {n} entries")
    blob = " ".join(data["lines"]) + " " + data.get("title", "")
    if BANNED.search(blob):
        raise ValueError("Generated script contains blocked wording; regenerate")
    data["topic_id"] = topic.get("id", "custom")
    data["hook"] = data.get("hook") or topic.get("hook", "")
    return data
