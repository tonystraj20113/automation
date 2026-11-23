import re, os, json, sys
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
D = "research/raw/subs"
IDS = ["YLexXtj0V6Q","8H-aT3Cbrko","-JV8En1ONuM","0iBC3Q5CZQw","JngwoSrXXvI","pwipzRBq-WE","uwfAd08q_U0"]

def ts(s):
    h, m, rest = s.split(":")
    sec, ms = rest.split(".")
    return int(h)*3600 + int(m)*60 + int(sec) + int(ms)/1000

def parse(path):
    text = open(path, encoding="utf-8-sig").read().replace("\r\n", "\n")
    blocks = re.split(r"\n\s*\n", text)
    cues = []
    for b in blocks:
        lines = [l for l in b.strip().split("\n") if l.strip()]
        if not lines: continue
        m = None
        for i, l in enumerate(lines):
            if "-->" in l:
                m = i; break
        if m is None: continue
        times = re.search(r"(\d+:\d+:\d+\.\d+)\s*-->\s*(\d+:\d+:\d+\.\d+)", lines[m])
        if not times: continue
        start, end = ts(times.group(1)), ts(times.group(2))
        words = []
        for l in lines[m+1:]:
            # strip inline VTT tags
            l = re.sub(r"<[^>]+>", "", l)
            l = re.sub(r"\{[^}]+\}", "", l)
            words.append(l.strip())
        sent = " ".join(w for w in words if w)
        if sent: cues.append((start, end, sent))
    return cues

def dedupe(cues):
    # YouTube rolling captions: keep only new suffix of each cue vs previous
    out = []
    prev = ""
    for s, e, t in cues:
        cur = t.strip()
        # remove exact repeat of previous
        if cur and cur == prev:
            continue
        # rolling: if cur starts with prev, take suffix
        if prev and cur.startswith(prev + " "):
            cur = cur[len(prev)+1:].strip()
        elif prev and len(prev) > 15:
            # try word overlap suffix/prefix
            pw, cw = prev.split(), cur.split()
            best = 0
            for k in range(min(len(pw), len(cw), 12), 0, -1):
                if pw[-k:] == cw[:k]:
                    best = k; break
            if best:
                cur = " ".join(cw[best:])
        if cur:
            out.append((s, e, cur))
            prev = (prev + " " + cur).strip() if not cur.startswith(prev) else cur
            if len(prev) > 300: prev = prev[-200:]
    return out

os.makedirs("research/raw/transcripts", exist_ok=True)
summary = {}
for vid in IDS:
    path = os.path.join(D, vid + ".en-orig.vtt")
    cues = dedupe(parse(path))
    lines = [f"[{s:6.2f}-{e:6.2f}] {t}" for s, e, t in cues]
    with open("research/raw/transcripts/" + vid + ".txt", "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    words = sum(len(t.split()) for _, _, t in cues)
    dur = cues[-1][1] if cues else 0
    summary[vid] = {"cues": len(cues), "words": words, "duration": dur, "wpm": round(words/(dur/60),1) if dur else 0,
                    "first12": [t for _,_,t in cues[:12]]}
    print("=====", vid, "cues", len(cues), "words", words, "dur", round(dur,1), "wpm", summary[vid]["wpm"])
    for s,e,t in cues[:25]:
        print(f" [{s:5.1f}] {t}")

json.dump(summary, open("research/raw/transcripts/summary.json","w",encoding="utf-8"), indent=2, ensure_ascii=False)
