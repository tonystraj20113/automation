"""Add a free, procedurally generated audio bed and transition SFX.

No copyrighted music and no paid service: a low atmospheric drone plus soft
filtered-noise whooshes at beat changes, mixed under the narration.
"""
import subprocess
from pathlib import Path


def add_bed(narration, out_path, boundaries=None, total_duration=None):
    """Return a mixed audio file: narration + drone + whooshes."""
    narration = Path(narration)
    out_path = Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    boundaries = [b for b in (boundaries or []) if b > 0.4][:10]

    cmd = ["ffmpeg", "-y", "-i", str(narration)]
    for f in (55.0, 82.41, 110.0):
        cmd += ["-f", "lavfi", "-i", f"sine=frequency={f}:sample_rate=24000"]
    for b in boundaries:
        cmd += ["-f", "lavfi", "-i",
                f"anoisesrc=color=brown:duration=0.35:sample_rate=24000"]

    fc = ("[1]lowpass=f=200,volume=0.055[a];"
          "[2]lowpass=f=300,volume=0.035[b];"
          "[3]lowpass=f=420,volume=0.022[c];")
    for k, b in enumerate(boundaries):
        ms = int(b * 1000)
        fc += (f"[{4+k}]highpass=f=180,lowpass=f=1600,"
               f"afade=t=in:st=0:d=0.05,afade=t=out:st=0.2:d=0.15,"
               f"volume=0.09,adelay={ms}|{ms}[w{k}];")
    fc += "[0]volume=1.0[n];"
    labels = ["[n]", "[a]", "[b]", "[c]"] + [f"[w{k}]" for k in range(len(boundaries))]
    fc += "".join(labels) + f"amix=inputs={len(labels)}:duration=first:normalize=0[out]"

    cmd += ["-filter_complex", fc, "-map", "[out]"]
    if total_duration:
        cmd += ["-t", f"{total_duration:.3f}"]
    cmd += ["-c:a", "libmp3lame", "-b:a", "160k", str(out_path)]
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        raise RuntimeError("ffmpeg audio mix failed: " + r.stderr[-1500:])
    return out_path
