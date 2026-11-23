"""Narration with edge-tts (free), per-line prosody, and duration probing."""
import asyncio, json, subprocess, time
from pathlib import Path

# Warm, conversational narration voice - closer to a real storyteller than a
# flat news voice. Line-level rate changes keep the delivery from sounding AI.
VOICE = "en-US-AndrewNeural"
RATES = ["-8%", "+0%", "+4%", "-4%", "+0%", "+6%", "-6%", "+0%", "+3%", "-5%",
         "+0%", "+5%", "-7%", "+0%", "+2%"]
PAUSE = 0.12  # seconds of silence between lines, like a human breathing


async def _save(text, out, voice, rate):
    """edge-tts occasionally returns no audio; retry before giving up."""
    import edge_tts
    last = None
    for attempt in range(6):
        try:
            await edge_tts.Communicate(text, voice, rate=rate).save(str(out))
            if Path(out).exists() and Path(out).stat().st_size > 1000:
                return
        except Exception as exc:
            last = exc
        await asyncio.sleep(0.5 + attempt * 0.5)
    raise RuntimeError(f"edge-tts failed after retries: {last}")


def synthesize_lines(lines, out_path, voice=VOICE):
    """Synthesize each line with its own pacing; return (path, line_durations).

    line_durations includes the pause after each line so captions and scenes
    line up exactly with the speech.
    """
    out_path = Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    tmp = out_path.parent / (out_path.stem + "_parts")
    tmp.mkdir(parents=True, exist_ok=True)
    paths, durs = [], []
    for i, line in enumerate(lines):
        part = tmp / f"line_{i:03d}.mp3"
        asyncio.run(_save(line, part, voice, RATES[i % len(RATES)]))
        paths.append(part)
        durs.append(duration(part) + (PAUSE if i < len(lines) - 1 else 0))
        if i < len(lines) - 1:
            sil = tmp / f"sil_{i:03d}.mp3"
            subprocess.run([
                "ffmpeg", "-y", "-f", "lavfi", "-i",
                f"anullsrc=r=24000:cl=mono", "-t", str(PAUSE),
                "-q:a", "9", str(sil),
            ], check=True, capture_output=True)
            paths.append(sil)
    listfile = tmp / "concat.txt"
    listfile.write_text("".join(f"file '{p.as_posix()}'\n" for p in paths), encoding="utf-8")
    subprocess.run(["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", str(listfile),
                    "-c", "copy", str(out_path)], check=True, capture_output=True)
    return out_path, durs


def synthesize(lines, out_path, voice=VOICE):
    """Backwards-compatible: one audio file from a list of lines."""
    return synthesize_lines(lines, out_path, voice)[0]


def duration(path):
    r = subprocess.run([
        "ffprobe", "-v", "error", "-show_entries", "format=duration",
        "-of", "json", str(path),
    ], check=True, capture_output=True, text=True)
    return float(json.loads(r.stdout)["format"]["duration"])


def write_srt(captions, audio_duration, out_path):
    n = max(1, len(captions))
    step = audio_duration / n
    lines = []
    for i, cap in enumerate(captions):
        lines.append(f"{i+1}\n{fmt(i*step)} --> {fmt((i+1)*step)}\n{cap}\n")
    Path(out_path).write_text("\n".join(lines), encoding="utf-8")
    return out_path


def write_srt_timed(captions, durations, out_path):
    lines, t = [], 0.0
    for i, (cap, d) in enumerate(zip(captions, durations)):
        lines.append(f"{i+1}\n{fmt(t)} --> {fmt(t+d)}\n{cap}\n")
        t += d
    Path(out_path).write_text("\n".join(lines), encoding="utf-8")
    return out_path


def fmt(sec):
    h = int(sec // 3600); m = int((sec % 3600) // 60); s = sec % 60
    return f"{h:02d}:{m:02d}:{s:06.3f}".replace(".", ",")
