import json, re, subprocess

f = "output/sample2.mp4"
r = subprocess.run(["ffprobe", "-v", "error", "-show_entries",
                    "format=duration:stream=width,height,r_frame_rate,codec_name",
                    "-of", "json", f], capture_output=True, text=True)
d = json.loads(r.stdout)
dur = float(d["format"]["duration"])
v = [s for s in d["streams"] if s.get("codec_name") != "aac"][0]
sc = subprocess.run(["ffmpeg", "-v", "info", "-i", f, "-vf",
                     "select=gt(scene\\,0.28),showinfo", "-f", "null", "-"],
                    capture_output=True, text=True)
times = [float(x) for x in re.findall(r"pts_time:([0-9.]+)", sc.stderr)]
print(f"{f}: {dur:.1f}s, {v['width']}x{v['height']}, fps {v['r_frame_rate']}")
print(f"hard cuts: {len(times)} ({len(times)/dur:.2f}/sec)")
print("cut times:", [round(t, 1) for t in times[:20]])
