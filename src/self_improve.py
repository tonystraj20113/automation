"""Daily self-analysis: scan the niche, score our uploads, propose next topics.

Everything runs on free public data (yt-dlp) plus the free Groq API. It writes
data/performance.json and appends fresh premises to config/topics.json, which
the next film run reads. No paid analytics tool and no card.
"""
import json, statistics, subprocess
from datetime import datetime, timezone

from .scripts import _chat, _parse_json
from .utils import ROOT, env, read_json, write_json

CHANNELS = ["@Gneef", "@RicksClips3000"]
QUERIES = ["lost and found story", "post office short story", "unfinished letters story",
           "umbrella stand story", "world rule short story"]


def ytdlp_json(args, timeout=180):
    try:
        r = subprocess.run(["yt-dlp", "--ignore-errors", "--no-warnings", *args],
                           capture_output=True, text=True, timeout=timeout)
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return []
    rows = []
    for line in r.stdout.splitlines():
        try:
            rows.append(json.loads(line))
        except Exception:
            pass
    return rows


def scan_competitors():
    out = {}
    for ch in CHANNELS:
        rows = ytdlp_json(["--flat-playlist", "--dump-json", f"https://www.youtube.com/{ch}/shorts"])
        items = [{"title": x.get("title", ""), "views": int(x.get("view_count") or 0)}
                 for x in rows[:40]]
        out[ch] = items
    return out


def scan_queries():
    key = env("YOUTUBE_API_KEY")
    if not key:
        return {}
    import requests
    out = {}
    for q in QUERIES:
        try:
            r = requests.get("https://www.googleapis.com/youtube/v3/search", params={
                "part": "snippet", "type": "video", "videoDuration": "short",
                "order": "viewCount", "maxResults": 10, "q": q, "key": key}, timeout=30)
            ids = ",".join(i["id"]["videoId"] for i in r.json().get("items", []))
            if not ids:
                continue
            v = requests.get("https://www.googleapis.com/youtube/v3/videos", params={
                "part": "statistics", "id": ids, "key": key}, timeout=30).json()
            views = [int(i["statistics"].get("viewCount", 0)) for i in v.get("items", [])]
            out[q] = {"median": int(statistics.median(views)) if views else 0,
                      "over_100k": sum(x > 100000 for x in views), "n": len(views)}
        except Exception:
            continue
    return out


def our_stats():
    key = env("YOUTUBE_API_KEY")
    ids = []
    for f in sorted((ROOT / "data" / "shorts").glob("*.json")):
        m = json.loads(f.read_text(encoding="utf-8"))
        if m.get("youtube_id"):
            ids.append(m["youtube_id"])
    if not key or not ids:
        return []
    import requests
    out = []
    for i in range(0, len(ids), 40):
        try:
            v = requests.get("https://www.googleapis.com/youtube/v3/videos", params={
                "part": "statistics,snippet", "id": ",".join(ids[i:i + 40]), "key": key},
                timeout=30).json()
            for row in v.get("items", []):
                out.append({"id": row["id"], "title": row["snippet"]["title"],
                            "views": int(row["statistics"].get("viewCount", 0)),
                            "likes": int(row["statistics"].get("likeCount", 0))})
        except Exception:
            pass
    return out


def propose(competitors, queries, ours):
    brief = json.dumps({"competitors": competitors, "queries": queries, "ours": ours})[:12000]
    raw = _chat(
        "You are a YouTube/Instagram growth analyst. Output JSON only. Be concrete and honest.",
        "Here is fresh public data for a blocky 3D story Shorts channel: " + brief + "\n\n"
        "Return JSON: {\"lessons\":[\"short rule learned\"],\"topics\":["
        "{\"id\":\"slug\",\"title\":\"title + emoji\",\"hook\":\"In this town, ...\","
        "\"score\":9.1}],\"titles\":[\"packaging pattern\"]}. Give 5 original, "
        "monetization-safe world-rule premises with almost no direct competition. "
        "No brands, no violence, no real people, no copying competitor wording.")
    return _parse_json(raw)


def main():
    competitors = scan_competitors()
    queries = scan_queries()
    ours = our_stats()
    if not env("GROQ_API_KEY"):
        print("[self-improve] GROQ_API_KEY missing; topics unchanged")
        return
    ideas = propose(competitors, queries, ours)
    write_json(ROOT / "data" / "performance.json", {
        "date": datetime.now(timezone.utc).isoformat(),
        "competitors": competitors, "queries": queries, "ours": ours,
        "lessons": ideas.get("lessons", []), "titles": ideas.get("titles", []),
    })
    path = ROOT / "config" / "topics.json"
    cfg = read_json(path, {"topics": []})
    known = {t.get("hook", "").lower() for t in cfg["topics"]}
    for t in ideas.get("topics", []):
        if t.get("hook") and t["hook"].lower() not in known and "roblox" not in t["hook"].lower():
            t.setdefault("status", "pending")
            cfg["topics"].append(t)
    cfg["topics"] = sorted(cfg["topics"], key=lambda t: -float(t.get("score", 0)))[:40]
    write_json(path, cfg)
    print(f"[self-improve] {len(competitors)} channels, {len(queries)} queries, "
          f"{len(ours)} own videos, {len(ideas.get('topics', []))} new topics")


if __name__ == "__main__":
    main()
