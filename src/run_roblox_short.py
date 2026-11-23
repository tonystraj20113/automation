"""One unattended Short: research -> script -> Kokoro -> Studio -> render -> publish."""
import argparse, json
from datetime import datetime, timedelta, timezone

from . import research, roblox_story, kokoro_tts, roblox_audio, roblox_place, render_roblox
from .utils import ROOT, ensure_dirs, write_json, read_json


def publish_instagram(release_url):
    from . import instagram_publish
    files = sorted((ROOT / "data" / "shorts").glob("*.json"))
    if not files:
        print("[ig] no story metadata; skipping")
        return
    latest = files[-1]
    meta = json.loads(latest.read_text(encoding="utf-8"))
    title = meta.get("script", {}).get("title", "StoryFacts")
    try:
        meta["instagram"] = instagram_publish.publish(release_url, title)
    except Exception as exc:
        meta["instagram_error"] = str(exc)
    write_json(latest, meta)


def mark_topic_done(topic_id):
    cfg_path = ROOT / "config" / "topics.json"
    cfg = read_json(cfg_path, {})
    for t in cfg.get("topics", []):
        if t.get("id") == topic_id:
            t["status"] = "done"
    write_json(cfg_path, cfg)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--preview", action="store_true", help="half-size quick render")
    ap.add_argument("--topic", default="")
    ap.add_argument("--ig-only", action="store_true")
    ap.add_argument("--release-url", default="")
    args = ap.parse_args()
    ensure_dirs()

    if args.ig_only:
        if not args.release_url:
            raise SystemExit("--ig-only needs --release-url")
        publish_instagram(args.release_url)
        return

    signals = research.collect_signals()
    topic = roblox_story.next_topic(args.topic)
    print(f"[1/6] topic: {topic['title'].encode('ascii', 'replace').decode()}")
    script = roblox_story.generate(topic, signals)
    print(f"[2/6] script: {script['title'].encode('ascii', 'replace').decode()}")

    stamp = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")
    base = ROOT / "output" / f"roblox-{stamp}"
    base.mkdir(parents=True, exist_ok=True)

    durs = kokoro_tts.synthesize(script["lines"], base / "voice")
    dur, _ = roblox_audio.build(script, base / "voice", base)
    print(f"[3/6] audio: {dur:.1f}s")

    scene, _ = roblox_place.build(script, base)
    print(f"[4/6] Roblox place: {len(scene['parts'])} parts")

    video = render_roblox.render(base, dur, base / "final.mp4", preview=args.preview)
    print(f"[5/6] rendered: {video}")

    meta = {
        "date": datetime.now(timezone.utc).isoformat(),
        "pipeline": "roblox-studio-cloud",
        "topic": topic, "script": script,
        "parts": len(scene["parts"]), "duration": dur,
        "video": str(video), "voice": "kokoro",
    }
    write_json(ROOT / "data" / "shorts" / f"{stamp}.json", meta)

    if args.dry_run or args.preview:
        print("[6/6] dry run - publishing skipped")
        return

    from . import youtube_upload
    publish_at = (datetime.now(timezone.utc) + timedelta(days=1)).strftime("%Y-%m-%dT%H:%M:%SZ")
    try:
        description = (script.get("hook", "") + "\n\n" + script["lines"][0] + "\n\n"
                       "Original blocky 3D story. Made entirely in code and Roblox Studio. "
                       "No real-world claims.")
        yid = youtube_upload.upload(video, script["title"], description,
                                    script.get("tags", ["shorts", "story"]),
                                    publish_at=publish_at)
        meta["youtube_id"] = yid
        meta["youtube_publish_at"] = publish_at
        print(f"[6/6] scheduled YouTube {yid}")
        mark_topic_done(topic.get("id"))
    except Exception as exc:
        print(f"[warn] YouTube upload failed: {exc}")
        meta["youtube_error"] = str(exc)
    write_json(ROOT / "data" / "shorts" / f"{stamp}.json", meta)


if __name__ == "__main__":
    main()
