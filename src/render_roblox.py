"""Render the Studio-built world with headless Edge/Chrome, then mux audio."""
import os, shutil, subprocess
from pathlib import Path

from .utils import ROOT

RENDERER = ROOT / "renderer"
KEEP = ("index.html", "film.js", "three.module.js", "f3.woff2",
        "render.js", "scene.js", "timeline.js")


def render(work_dir, dur, out_path, preview=False, workers=2):
    work = Path(work_dir)
    work.mkdir(parents=True, exist_ok=True)
    for name in KEEP:
        src = work / name if name in ("scene.js", "timeline.js") else RENDERER / name
        if src.exists():
            shutil.copy2(src, work / name)
    (work / "audio").mkdir(exist_ok=True)
    shutil.copy2(work / "mix.wav", work / "audio" / "mix.wav")

    env = dict(os.environ)
    env["DUR"] = f"{dur:.3f}"
    env["FPS"] = "30"
    env["VIDEOHUB_ENCODER"] = env.get("VIDEOHUB_ENCODER", "x264")
    env["NODE_PATH"] = str(RENDERER / "node_modules")
    if preview:
        env["PREVIEW"] = "1"
    chrome = env.get("CHROME", "")
    if chrome:
        env["CHROME"] = chrome

    cmd = ["node", "render.js", str(workers)]
    print("[render]", " ".join(cmd), "in", work, flush=True)
    proc = subprocess.run(cmd, cwd=str(work), env=env, text=True,
                          stdout=subprocess.PIPE, stderr=subprocess.STDOUT, timeout=5400)
    print(proc.stdout[-4000:])
    if proc.returncode:
        raise RuntimeError(f"renderer exited {proc.returncode}")

    folder = work / ("render/preview" if preview else "render")
    movies = [p for p in folder.glob("*.mp4") if p.name != "video.mp4"]
    if not movies:
        raise RuntimeError(f"No rendered MP4 in {folder}")
    best = max(movies, key=lambda p: p.stat().st_mtime)
    out_path = Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(best, out_path)
    print(f"[render] {out_path} ({out_path.stat().st_size / 1e6:.1f} MB)")
    return out_path
