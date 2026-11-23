"""Instagram Reels publishing through the Meta Graph API (two-step)."""
import mimetypes, requests
from .utils import env

GRAPH = "https://graph.facebook.com/v20.0"

def publish(media_url, caption):
    token = env("IG_ACCESS_TOKEN")
    ig_user = env("IG_USER_ID")
    if not token or not ig_user:
        return {"skipped": "missing IG credentials"}
    container = requests.post(
        f"{GRAPH}/{ig_user}/media",
        data={"media_type": "REELS", "video_url": media_url,
              "caption": caption[:2200], "access_token": token},
        timeout=60,
    )
    container.raise_for_status()
    cid = container.json()["id"]
    result = requests.post(
        f"{GRAPH}/{ig_user}/media_publish",
        data={"creation_id": cid, "access_token": token},
        timeout=60,
    )
    result.raise_for_status()
    return result.json()
