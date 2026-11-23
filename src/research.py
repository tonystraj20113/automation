"""Mine public competitor signals with the YouTube Data API (free quota)."""
import requests
from .utils import env, load_config

YOUTUBE_SEARCH = "https://www.googleapis.com/youtube/v3/search"
YOUTUBE_VIDEOS = "https://www.googleapis.com/youtube/v3/videos"

def _top_shorts_for_channel(api_key, handle, limit=8):
    s = requests.get(YOUTUBE_SEARCH, params={
        "part": "snippet", "type": "video", "videoDuration": "short",
        "order": "viewCount", "maxResults": limit, "q": handle,
        "key": api_key,
    }, timeout=30)
    s.raise_for_status()
    items = s.json().get("items", [])
    if not items:
        return []
    ids = ",".join(i["id"]["videoId"] for i in items)
    v = requests.get(YOUTUBE_VIDEOS, params={
        "part": "statistics,snippet", "id": ids, "key": api_key,
    }, timeout=30)
    v.raise_for_status()
    out = []
    for row in v.json().get("items", []):
        out.append({
            "title": row["snippet"]["title"],
            "views": int(row["statistics"].get("viewCount", 0)),
            "video_id": row["id"],
        })
    return sorted(out, key=lambda x: -x["views"])

def collect_signals():
    """Return a compact brief string. Degrades gracefully without an API key."""
    cfg = load_config()
    key = env("YOUTUBE_API_KEY")
    brief = []
    for ch in cfg["competitors"]:
        if ch["platform"] != "youtube" or "UNCONFIRMED" in ch["focus"]:
            continue
        if not key:
            brief.append(f"- {ch['handle']}: {ch['focus']}")
            continue
        try:
            tops = _top_shorts_for_channel(key, ch["handle"])
            titles = "; ".join(f"{t['title']} ({t['views']:,})" for t in tops[:5])
            brief.append(f"- {ch['handle']}: {ch['focus']}. Top: {titles}")
        except Exception as exc:
            brief.append(f"- {ch['handle']}: {ch['focus']} [API error: {exc}]")
    return "Competitor signals:\n" + "\n".join(brief)
