import subprocess, json, sys, statistics
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

QUERIES = {
 "core_formula": 'roblox animation "in this town" short',
 "lost_and_found": 'roblox animation "lost and found" story short',
 "library": 'roblox animation "library" "in this town"',
 "elevator": 'roblox animation "elevator" story short',
 "lighthouse": 'roblox animation "lighthouse" story short',
 "bus_stop": 'roblox animation "bus stop" story short',
 "laundromat": 'roblox animation "laundromat" story short',
 "post_office": 'roblox animation "post office" story short',
 "clockmaker": 'roblox animation "clock" "in this town"',
 "shoe_shop": 'roblox animation "shoes" "in this town" story',
 "umbrella": 'roblox animation "umbrella" "in this town"',
 "benchmark_knocks": 'roblox animation "knocks" story short',
 "benchmark_garden": 'roblox animation "garden" "in this town" story',
 "benchmark_mime": 'roblox animation "mime" story short',
 "gentle_mystery": 'roblox animation "kindness" "in this town" short',
 "not_scary": 'roblox story animation short wholesome mystery',
 "dupes": 'roblox animation "copy" "in this town" short',
}

out = {}
for name, q in QUERIES.items():
    p = subprocess.run(["yt-dlp","--flat-playlist","--dump-single-json","--no-warnings","ytsearch15:"+q],
                       capture_output=True, text=True, encoding="utf-8", errors="replace")
    if p.returncode != 0:
        print("FAIL", name, p.stderr[-150:], file=sys.stderr); continue
    try: d = json.loads(p.stdout)
    except Exception: continue
    es = [{"title":e.get("title"),"channel":e.get("channel"),"views":e.get("view_count") or 0,
           "dur":e.get("duration"),"url":e.get("url")} for e in d.get("entries",[])]
    views = [e["views"] for e in es]
    big = sum(1 for v in views if v >= 100000)
    med = statistics.median(views) if views else 0
    out[name] = {"query":q, "n":len(es), "median_views":med, "over100k":big,
                 "top":sorted(es,key=lambda e:-e["views"])[:8]}
    print(f"{name:20s} n={len(es):2d} median={int(med):>10,d} >=100k={big:2d} top={(sorted([e['views'] for e in es],reverse=True)[:5])}")

json.dump(out, open("research/raw/niche_competition.json","w",encoding="utf-8"), indent=2, ensure_ascii=False)
