"""Local Kokoro voice for the cloud pipeline (no paid TTS, no edge-tts).

Model files are free, public and cached between Actions runs:
  kokoro-v1.0.onnx  ~325 MB
  voices-v1.0.bin   ~28 MB
"""
import json, os
from pathlib import Path

import numpy as np
import requests
import soundfile as sf

MODEL_URL = "https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.1/kokoro-v1.0.onnx"
VOICES_URL = "https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.1/voices-v1.0.bin"
CACHE = Path(os.environ.get("KOKORO_CACHE", str(Path.home() / ".cache" / "storyfacts-kokoro")))
VOICE = os.environ.get("KOKORO_VOICE", "am_michael")
SPEED = float(os.environ.get("KOKORO_SPEED", "0.94"))


def _download(url, dest, minimum):
    if dest.exists() and dest.stat().st_size > minimum:
        return dest
    dest.parent.mkdir(parents=True, exist_ok=True)
    print(f"[kokoro] downloading {dest.name} ({url})", flush=True)
    with requests.get(url, stream=True, timeout=(20, 180)) as r:
        r.raise_for_status()
        tmp = dest.with_suffix(dest.suffix + ".part")
        with open(tmp, "wb") as f:
            for chunk in r.iter_content(1024 * 1024):
                if chunk:
                    f.write(chunk)
        if tmp.stat().st_size <= minimum:
            tmp.unlink(missing_ok=True)
            raise RuntimeError(f"Kokoro download too small: {dest.name}")
        tmp.replace(dest)
    return dest


def _engine():
    model = _download(MODEL_URL, CACHE / "kokoro-v1.0.onnx", 100_000_000)
    voices = _download(VOICES_URL, CACHE / "voices-v1.0.bin", 10_000_000)
    from kokoro_onnx import Kokoro
    return Kokoro(str(model), str(voices))


def synthesize(lines, out_dir, voice=VOICE, speed=SPEED):
    """Write out_dir/00.wav… and out_dir/dur.json. Return the duration dict."""
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    engine = _engine()
    available = set(engine.get_voices())
    chosen = voice if voice in available else "af_bella"
    if chosen != voice:
        print(f"[kokoro] voice {voice} unavailable; using {chosen}")
    durations = {}
    for i, text in enumerate(lines):
        audio, sr = engine.create(text, voice=chosen, speed=speed, lang="en-us")
        a = np.asarray(audio, dtype=np.float32)
        peak = float(np.abs(a).max()) if len(a) else 0.0
        if peak > 0:
            nz = np.where(np.abs(a) > peak * 0.02)[0]
            if len(nz):
                a = a[max(0, nz[0] - int(0.03 * sr)): nz[-1] + int(0.08 * sr)]
        key = f"{i:02d}"
        path = out / f"{key}.wav"
        sf.write(str(path), a, sr, subtype="PCM_16")
        durations[key] = round(len(a) / sr, 3)
        print(f"[kokoro] {key} {durations[key]}s", flush=True)
    (out / "dur.json").write_text(json.dumps(durations, indent=1), encoding="utf-8")
    (out / "lines.json").write_text(json.dumps(
        [{"id": f"{i:02d}", "text": t, "voice": chosen, "speed": speed, "lang": "en-us"}
         for i, t in enumerate(lines)], indent=1), encoding="utf-8")
    return durations
