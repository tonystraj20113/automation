"""Generate a sample Short with no API keys required - for quality review.

    python scripts/make_sample.py

Uses a hand-written story-fact script plus the free edge-tts voice and the
same renderer the automated pipeline uses, so what you see is the real thing.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src import tts, render
from src.utils import ROOT

LINES = [
    "In 1900, three lighthouse keepers vanished, and the light kept burning anyway.",
    "On the Flannan Isles, a relief ship found the lamp running and a meal left on the table.",
    "The logbook's last entry was December fifteenth. The clock had stopped.",
    "One keeper's coat was gone. The others' pipes were still lying out.",
    "A giant wave theory says all three were swept from the rock in seconds.",
    "But nobody saw it happen, only the light, turning for empty rooms.",
]

CAPTIONS = [
    "The light kept burning",
    "Three keepers vanished",
    "A meal on the table",
    "The clock had stopped",
    "Swept away in seconds?",
    "Turning for empty rooms",
]

SPECS = [
    {"motif": "ocean", "props": ["lantern"], "mood": "mystery"},
    {"motif": "room", "props": ["book", "clock"], "mood": "mystery"},
    {"motif": "night", "props": ["clock", "book"], "mood": "spooky"},
    {"motif": "room", "props": ["door", "jar"], "mood": "spooky"},
    {"motif": "ocean", "props": ["ship"], "mood": "spooky"},
    {"motif": "ocean", "props": ["lantern"], "mood": "mystery"},
]


def main():
    base = ROOT / "output" / "sample"
    audio = tts.synthesize(LINES, str(base) + ".mp3")
    dur = tts.duration(audio)
    srt = tts.write_srt(CAPTIONS, dur, str(base) + ".srt")
    video = render.render_video(
        CAPTIONS, audio, srt, str(base) + ".mp4",
        style="ukiyo-e", w=1080, h=1920,
        title="THE LIGHTHOUSE THAT KEPT BURNING", specs=SPECS,
    )
    print(f"Sample video: {video}  ({dur:.1f}s)")


if __name__ == "__main__":
    main()
