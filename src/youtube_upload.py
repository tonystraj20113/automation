"""Upload and schedule with the YouTube Data API v3 using OAuth secrets."""
import json
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from .utils import decode_secret, env

SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]

def _service():
    client = json.loads(decode_secret("YOUTUBE_CLIENT_SECRET_B64"))
    token = json.loads(decode_secret("YOUTUBE_TOKEN_B64"))
    cfg = client.get("installed", client.get("web", {}))
    creds = Credentials(
        token=token.get("token"),
        refresh_token=token.get("refresh_token"),
        token_uri=cfg.get("token_uri", "https://oauth2.googleapis.com/token"),
        client_id=cfg.get("client_id"),
        client_secret=cfg.get("client_secret"),
        scopes=SCOPES,
    )
    return build("youtube", "v3", credentials=creds, cache_discovery=False)

def upload(path, title, description, tags, publish_at=None, category_id="24"):
    privacy = env("YT_PUBLISH_PRIVACY", "private")
    status = {"privacyStatus": privacy, "selfDeclaredMadeForKids": True}
    if publish_at:
        status["privacyStatus"] = "private"
        status["publishAt"] = publish_at
    body = {
        "snippet": {
            "title": title[:100],
            "description": description[:5000],
            "tags": tags[:20],
            "categoryId": category_id,
            "defaultLanguage": "en",
        },
        "status": status,
    }
    media = MediaFileUpload(str(path), mimetype="video/mp4", resumable=True)
    req = _service().videos().insert(part="snippet,status", body=body, media_body=media)
    response = None
    while response is None:
        _, response = req.next_chunk()
    return response.get("id")
