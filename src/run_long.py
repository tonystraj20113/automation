"""Weekly long video from the five Shorts made this week."""
import json
from datetime import datetime, timedelta, timezone
from .utils import ROOT, ensure_dirs, write_json, env
from . import scripts, tts, render, audio_mix

def main():
    ensure_dirs()
    folder = ROOT / "data" / "shorts"
    files = sorted(folder.glob("*.json"))[-5:] if folder.exists() else []
    if not files:
        print("No Shorts found; nothing to compile.")
        return
    stories = []
    for f in files:
        d = json.loads(f.read_text(encoding="utf-8"))
        s = d["script"]
        stories.append({"title": s["title"], "lines": s["lines"],
                        "story_style": s["story_style"]})
    print(f"[1/4] compiling {len(stories)} stories")
    script = scripts.generate_long(stories)
    print(f"[2/4] long script: {script['title']}")

    stamp = datetime.now(timezone.utc).strftime("%Y%m%d")
    base = ROOT / "output" / f"long-{stamp}"
    lines = []
    captions = []
    for ch in script["chapters"]:
        lines.append(ch["narration"])
        captions.append(ch["title"])
    lines.append(script["closing"])
    captions.append("What we learned")
    voice, durs = tts.synthesize_lines(lines, str(base) + "_voice.mp3")
    dur = sum(durs)
    boundaries, t = [], 0.0
    for d in durs[:-1]:
        t += d
        boundaries.append(t)
    audio = audio_mix.add_bed(voice, str(base) + ".mp3",
                              boundaries=boundaries, total_duration=dur)
    srt = tts.write_srt_timed(captions, durs, str(base) + ".srt")
    video = render.render_video(captions, audio, srt, str(base) + ".mp4",
                                style="claymation", w=1920, h=1080,
                                title=script["title"], durations=durs,
                                subframes=8, sfx=True)
    print(f"[3/4] rendered {video} ({dur/60:.1f} min)")

    meta = {"date": datetime.now(timezone.utc).isoformat(), "script": script,
            "video": str(video), "duration": dur, "source_count": len(stories)}
    write_json(ROOT / "data" / "longs" / f"{stamp}.json", meta)

    if env("DRY_RUN", "false").lower() == "true":
        print("[4/4] dry run - skipped publishing")
        return
    try:
        from . import youtube_upload
        publish_at = (datetime.now(timezone.utc) + timedelta(days=1)).strftime("%Y-%m-%dT%H:%M:%SZ")
        yid = youtube_upload.upload(video, script["title"],
            "The week's strangest true stories, told small.\n\nChapters:\n" +
            "\n".join(f"{i+1}. {c['title']}" for i, c in enumerate(script["chapters"])),
            ["storyfacts", "facts", "compilation", "storytelling"], publish_at=publish_at)
        meta["youtube_id"] = yid
        write_json(ROOT / "data" / "longs" / f"{stamp}.json", meta)
        print(f"[4/4] scheduled YouTube {yid}")
    except Exception as exc:
        print(f"[warn] upload failed: {exc}")

if __name__ == "__main__":
    main()
