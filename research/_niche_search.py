import subprocess, json, sys, os
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

QUERIES = [
    "roblox story shorts strange rules world",
    "roblox animation story short mystery的规则",
    "roblox story short the rule nobody breaks",
    "roblox animation short what if town",
    "roblox storytime shorts scary rules",
    "roblox animation short moral story",
    "roblox story shorts quiet town mystery",
    "minecraft story short strange rules world",
    "roblox animation shorts copycat replacement",
    "roblox story short lost and found",
    "roblox animation short elevator mystery",
    "roblox story short lighthouse",
    "roblox animation short bus stop mystery",
    "roblox story short library rule",
    "roblox animation short memory shop",
]

out = {}
for q in QUERIES:
    cmd = ["yt-dlp", "--flat-playlist", "--dump-single-json", "--no-warnings",
           "ytsearch12:" + q]
    p = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace")
    if p.returncode != 0:
        print("FAIL", q, p.stderr[-200:], file=sys.stderr)
        continue
    try:
        d = json.loads(p.stdout)
    except Exception:
        continue
    entries = []
    for e in d.get("entries", []):
        entries.append({
            "title": e.get("title"), "channel": e.get("channel"), "views": e.get("view_count"),
            "duration": e.get("duration"), "url": e.get("url"), "id": e.get("id"),
        })
    out[q] = entries
    print("QUERY", q, "n", len(entries))
    for e in entries[:6]:
        print("  ", (e["title"] or "")[:80], "|", e["channel"], "|", e["views"], "|", e["duration"])

json.dump(out, open("research/raw/niche_search.json","w",encoding="utf-8"), indent=2, ensure_ascii=False)
