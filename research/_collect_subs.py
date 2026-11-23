import subprocess, sys, os
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
IDS = ["YLexXtj0V6Q","8H-aT3Cbrko","-JV8En1ONuM","0iBC3Q5CZQw","JngwoSrXXvI","pwipzRBq-WE","uwfAd08q_U0"]
os.makedirs("research/raw/subs", exist_ok=True)
for vid in IDS:
    p = subprocess.run([
        "yt-dlp", "--skip-download", "--no-warnings",
        "--write-auto-subs", "--sub-langs", "en-orig", "--sub-format", "vtt",
        "-o", "research/raw/subs/%(id)s.%(ext)s",
        "https://www.youtube.com/shorts/" + vid,
    ], capture_output=True, text=True, encoding="utf-8", errors="replace")
    print(vid, "rc", p.returncode, p.stderr[-300:].replace("\n", " "), flush=True)
