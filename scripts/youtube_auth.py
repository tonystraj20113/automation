"""ONE-TIME local helper: authorize the YouTube account and print secret values.

Run locally (not in Actions):
    pip install -r requirements.txt
    python scripts/youtube_auth.py client_secret.json

Paste the two printed base64 blobs into GitHub Secrets:
    YOUTUBE_CLIENT_SECRET_B64
    YOUTUBE_TOKEN_B64
"""
import base64, json, sys
from google_auth_oauthlib.flow import InstalledAppFlow

SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]

def main():
    if len(sys.argv) < 2:
        raise SystemExit("Usage: python scripts/youtube_auth.py client_secret.json")
    client_path = sys.argv[1]
    flow = InstalledAppFlow.from_client_secrets_file(client_path, SCOPES)
    creds = flow.run_local_server(port=0)
    token = {
        "token": creds.token,
        "refresh_token": creds.refresh_token,
        "client_id": creds.client_id,
        "client_secret": creds.client_secret,
        "token_uri": creds.token_uri,
    }
    client = json.load(open(client_path, encoding="utf-8"))
    print("YOUTUBE_CLIENT_SECRET_B64=" + b64(client))
    print("YOUTUBE_TOKEN_B64=" + b64(token))

def b64(obj):
    return base64.b64encode(json.dumps(obj).encode()).decode()

if __name__ == "__main__":
    main()
