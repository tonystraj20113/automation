import glob, json, os, re, subprocess

for f in sorted(glob.glob("research/*.mp4")):
    r = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries",
         "format=duration:stream=width,height,r_frame_rate,codec_name",
         "-of", "json", f], capture_output=True, text=True)
    d = json.loads(r.stdout)
    vids = [s for s in d["streams"] if s.get("codec_name") != "aac"]
    auds = [s for s in d["streams"] if s.get("codec_name") == "aac"]
    v = vids[0]
    dur = float(d["format"]["duration"])
    vf = "select=gt(scene\\,0.28),showinfo"
    sc = subprocess.run(
        ["ffmpeg", "-v", "info", "-i", f, "-vf", vf, "-f", "null", "-"],
        capture_output=True, text=True)
    times = [float(x) for x in re.findall(r"pts_time:([0-9.]+)", sc.stderr)]
    gaps = [round(times[i+1] - times[i], 2) for i in range(len(times) - 1)]
    print(os.path.basename(f),
          "| %.1fs" % dur,
          "| %sx%s" % (v["width"], v["height"]),
          "| fps", v["r_frame_rate"],
          "| cuts", len(times),
          "| cuts/sec", round(len(times) / dur, 2),
          "| audio", bool(auds))
    print("   cut times:", [round(t, 2) for t in times[:14]])
    print("   avg gap:", round(sum(gaps) / len(gaps), 2) if gaps else "n/a")
