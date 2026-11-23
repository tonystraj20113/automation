"""Generate a sample Short with no API keys required - for quality review.

    python scripts/make_sample.py

The script structure follows what actually works on the reference channels:
a vivid opening image, "You see," named people, concrete numbers, a turn,
and a cliffhanger. Uses the exact same renderer as the automated pipeline.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src import tts, render, audio_mix
from src.utils import ROOT

LINES = [
    "The lamp was still turning when the rescue boat arrived. Three keepers, gone.",
    "You see, on a rock called Flannan Isle, that lighthouse was the only thing between ships and the cliffs.",
    "Every night, three men kept that light alive. Then one December morning, it stopped being enough.",
    "A supply ship pulled up in January. No flag. No men on the landing. Nobody answered the horn.",
    "Inside, the clock had stopped. A meal sat half eaten on the table. One coat was missing.",
    "The logbook's last line was December fifteenth. After that, nothing.",
    "The lamp, though, was still burning. Fuel in the tank. Wound and ready, like someone had just left the room.",
    "Here's the part that gets me. The keepers' pipes were still lying out. Nobody leaves without their pipe.",
    "So where did they go?",
    "The official story blames a rogue wave, a wall of water that swept the rock clean in seconds.",
    "But the boat was gone too. And a man doesn't launch a boat in a storm unless he sees something.",
    "Maybe they spotted a ship in trouble and rowed out to save it.",
    "Maybe the sea took all four before anyone could light a flare.",
    "Either way, the light kept turning for empty rooms.",
    "And for a whole month, every ship that passed believed someone was still watching over them.",
]

CAPTIONS = [
    "The lamp was still turning",
    "Three keepers, gone",
    "One rock. One light.",
    "Nobody answered the horn",
    "The clock had stopped",
    "Last entry: December 15",
    "Still burning. Still wound.",
    "Nobody leaves their pipe",
    "Where did they go?",
    "A rogue wave?",
    "But the boat was gone",
    "A ship in trouble?",
    "The sea took all four",
    "Turning for empty rooms",
    "Someone was watching",
]

SPECS = [
    {"motif": "night", "props": ["lantern"], "mood": "mystery"},
    {"motif": "ocean", "props": ["lantern"], "mood": "mystery"},
    {"motif": "ocean", "props": ["lantern"], "mood": "mystery"},
    {"motif": "ocean", "props": ["ship"], "mood": "spooky"},
    {"motif": "room", "props": ["clock", "jar"], "mood": "spooky"},
    {"motif": "room", "props": ["book"], "mood": "spooky"},
    {"motif": "room", "props": ["lantern"], "mood": "mystery"},
    {"motif": "room", "props": ["jar"], "mood": "mystery"},
    {"motif": "night", "props": ["star"], "mood": "spooky"},
    {"motif": "ocean", "props": ["ship"], "mood": "spooky"},
    {"motif": "ocean", "props": ["ship"], "mood": "mystery"},
    {"motif": "night", "props": ["ship"], "mood": "mystery"},
    {"motif": "ocean", "props": ["star"], "mood": "spooky"},
    {"motif": "ocean", "props": ["lantern"], "mood": "mystery"},
    {"motif": "ocean", "props": ["lantern"], "mood": "mystery"},
]


def main():
    base = ROOT / "output" / "sample2"
    voice, durs = tts.synthesize_lines(LINES, str(base) + "_voice.mp3")
    total = sum(durs)
    boundaries, t = [], 0.0
    for d in durs[:-1]:
        t += d
        boundaries.append(t)

    mixed = audio_mix.add_bed(voice, str(base) + "_mix.mp3",
                              boundaries=boundaries, total_duration=total)
    srt = tts.write_srt_timed(CAPTIONS, durs, str(base) + ".srt")
    video = render.render_video(
        CAPTIONS, mixed, srt, str(base) + ".mp4",
        style="ukiyo-e", w=1080, h=1920,
        title="THE LIGHTHOUSE THAT KEPT BURNING", specs=SPECS,
        durations=durs, subframes=8, sfx=True,
    )
    print(f"Sample video: {video}  ({total:.1f}s)")


if __name__ == "__main__":
    main()
