import json, subprocess, sys, os
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

IDS = [
    "YLexXtj0V6Q",
    "8H-aT3Cbrko",
    "-JV8En1ONuM",
    "0iBC3Q5CZQw",
    "JngwoSrXXvI",
    "pwipzRBq-WE",
    "uwfAd08q_U0",
]

out = []
for vid in IDS:
    url = "https://www.youtube.com/shorts/" + vid
    p = subprocess.run(
        ["yt-dlp", "--dump-single-json", "--no-warnings", "--skip-download", url],
        capture_output=True, text=True, encoding="utf-8", errors="replace",
    )
    if p.returncode != 0 or not p.stdout.strip():
        print("FAILED", vid, p.stderr[-500:], file=sys.stderr)
        continue
    try:
        d = json.loads(p.stdout)
    except Exception as e:
        print("PARSE FAILED", vid, e, file=sys.stderr)
        continue
    keys = ["id", "title", "view_count", "like_count", "comment_count", "upload_date",
            "duration", "description", "channel", "channel_follower_count", "webpage_url",
            "categories", "tags", "availability", "thumbnail"]
    rec = {k: d.get(k) for k in keys}
    out.append(rec)
    print(json.dumps(rec, ensure_ascii=False), flush=True)

os.makedirs("research/raw", exist_ok=True)
with open("research/raw/gneef_meta.json", "w", encoding="utf-8") as f:
    json.dump(out, f, indent=2, ensure_ascii=False)
