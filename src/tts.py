"""Narration with edge-tts (free, no key) and duration probing with ffprobe."""
import json, subprocess
from pathlib import Path

VOICE = "en-US-AvaNeural"

def synthesize(lines, out_path, voice=VOICE):
    out_path = Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    text = " ".join(lines)
    subprocess.run([
        "edge-tts", "--voice", voice, "--text", text, "--write-media", str(out_path)
    ], check=True)
    return out_path

def duration(path):
    r = subprocess.run([
        "ffprobe", "-v", "error", "-show_entries", "format=duration",
        "-of", "json", str(path)
    ], check=True, capture_output=True, text=True)
    return float(json.loads(r.stdout)["format"]["duration"])

def write_srt(captions, audio_duration, out_path):
    """Spread captions evenly across the audio."""
    n = max(1, len(captions))
    step = audio_duration / n
    lines = []
    for i, cap in enumerate(captions):
        a = i * step
        b = (i + 1) * step
        lines.append(f"{i+1}\n{fmt(a)} --> {fmt(b)}\n{cap}\n")
    Path(out_path).write_text("\n".join(lines), encoding="utf-8")
    return out_path

def fmt(sec):
    h = int(sec // 3600); m = int((sec % 3600) // 60); s = sec % 60
    return f"{h:02d}:{m:02d}:{s:06.3f}".replace(".", ",")
