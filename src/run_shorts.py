"""One Short: research -> script -> voice -> render -> schedule YouTube.
Instagram publish is a separate phase (--ig-only) that runs after the
rendered file has a public release URL.
"""
import argparse, json
from datetime import datetime, timedelta, timezone
from .utils import ROOT, ensure_dirs, write_json, env
from . import research, scripts, tts, render

TOPICS = [
    "a tiny decision that changed a whole city",
    "an animal with a strangely human habit",
    "a mystery object found in the ocean",
    "a scientific fact that sounds made up",
    "a historical rule that still affects your life",
    "a strange thing people once believed",
]

def _publish_instagram(release_url):
    """Publish the most recent generated Short to Instagram Reels."""
    from . import instagram_publish
    folder = ROOT / "data" / "shorts"
    files = sorted(folder.glob("*.json")) if folder.exists() else []
    if not files:
        print("[ig] no story metadata found; skipping")
        return
    latest = files[-1]
    meta = json.loads(latest.read_text(encoding="utf-8"))
    title = meta.get("script", {}).get("title", "StoryFacts")
    try:
        meta["instagram"] = instagram_publish.publish(release_url, title)
        print(f"[ig] published: {meta['instagram']}")
    except Exception as exc:
        print(f"[warn] Instagram publish failed: {exc}")
        meta["instagram_error"] = str(exc)
    write_json(latest, meta)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--topic", default="")
    ap.add_argument("--index", type=int, default=-1)
    ap.add_argument("--ig-only", action="store_true",
                    help="Publish the latest Short to Instagram using --release-url")
    ap.add_argument("--release-url", default="", help="Public URL for Instagram")
    args = ap.parse_args()
    ensure_dirs()

    if args.ig_only:
        if not args.release_url:
            raise SystemExit("--ig-only requires --release-url")
        _publish_instagram(args.release_url)
        return

    signals = research.collect_signals()
    idx = args.index if args.index >= 0 else datetime.now(timezone.utc).weekday()
    topic = args.topic or TOPICS[idx % len(TOPICS)]
    print(f"[1/5] signals + topic: {topic}")
    script = scripts.generate_short(topic, signals)
    print(f"[2/5] script: {script['title']}")

    stamp = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M")
    base = ROOT / "output" / f"short-{stamp}"
    audio = tts.synthesize([script["hook"], script["proof"], *script["beats"], script["ending"]],
                           str(base) + ".mp3")
    dur = tts.duration(audio)
    srt = tts.write_srt(script["captions"], dur, str(base) + ".srt")
    print(f"[3/5] audio {dur:.1f}s")

    video = render.render_video(script["captions"], audio, srt, str(base) + ".mp4",
                                style=script["story_style"], w=1080, h=1920,
                                title=script["title"], specs=script.get("scenes"))
    print(f"[4/5] rendered {video}")

    meta = {
        "date": datetime.now(timezone.utc).isoformat(),
        "topic": topic,
        "script": script,
        "video": str(video),
        "duration": dur,
    }
    write_json(ROOT / "data" / "shorts" / f"{stamp}.json", meta)

    if args.dry_run:
        print("[5/5] dry run - skipped publishing")
        return

    from . import youtube_upload
    publish_at = (datetime.now(timezone.utc) + timedelta(days=1)).strftime("%Y-%m-%dT%H:%M:%SZ")
    try:
        yid = youtube_upload.upload(
            video, script["title"],
            f"{script['hook']}\n\n{script['proof']}\n\nStoryFacts — true stories, told small.",
            ["storyfacts", "facts", "shorts", "storytelling"],
            publish_at=publish_at,
        )
        meta["youtube_id"] = yid
        print(f"[5/5] scheduled YouTube {yid} at {publish_at}")
    except Exception as exc:
        print(f"[warn] YouTube upload failed: {exc}")
    write_json(ROOT / "data" / "shorts" / f"{stamp}.json", meta)

if __name__ == "__main__":
    main()
