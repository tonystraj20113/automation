import subprocess, re, os, json, sys, statistics
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
IDS = ["YLexXtj0V6Q","8H-aT3Cbrko","-JV8En1ONuM","0iBC3Q5CZQw","JngwoSrXXvI","pwipzRBq-WE","uwfAd08q_U0"]

def get_scores(vid):
    out = "research/raw/cuts_%s.txt" % vid
    if not os.path.exists(out):
        subprocess.run([
            "ffmpeg","-hide_banner","-loglevel","error","-i",
            "research/raw/video/%s.mp4" % vid,
            "-vf", "select='gte(scene,0)',metadata=print:key=lavfi.scene_score:file=" + out.replace("\\","/"),
            "-an","-f","null","NUL"], check=True)
    txt = open(out, encoding="utf-8", errors="replace").read()
    times = [float(x) for x in re.findall(r"pts_time:([0-9.]+)", txt)]
    scores = [float(x) for x in re.findall(r"lavfi\.scene_score=([0-9.]+)", txt)]
    return list(zip(times, scores))

res = {}
for vid in IDS:
    data = get_scores(vid)
    dur = data[-1][0] if data else 0
    row = {"duration": dur, "frames": len(data)}
    for th in [0.2, 0.3, 0.4, 0.5]:
        cuts = [t for t,s in data if s > th]
        # merge cuts closer than 0.35s (one hard cut creates 2 high-score frames)
        merged = []
        for t in cuts:
            if not merged or t - merged[-1] > 0.35:
                merged.append(t)
        intervals = [b-a for a,b in zip(merged, merged[1:])]
        row[f"th{th}"] = {
            "raw": len(cuts), "cuts": len(merged),
            "cuts_per_sec": round(len(merged)/dur, 2) if dur else 0,
            "median_gap_s": round(statistics.median(intervals),2) if intervals else None,
        }
    res[vid] = row
    print(vid, "dur", round(dur,1), "frames", len(data), json.dumps({k:v for k,v in row.items() if k.startswith("th")}))
json.dump(res, open("research/raw/cut_analysis.json","w",encoding="utf-8"), indent=2)
