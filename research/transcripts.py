from youtube_transcript_api import YouTubeTranscriptApi

ids = ["7xS87iActkU", "QlDPMzGmYac", "5WtSJKCEnDs", "zJp0BTjm5oY"]
api = YouTubeTranscriptApi()
for vid in ids:
    try:
        t = api.fetch(vid)
        text = " ".join(snippet.text for snippet in t)
        print("=" * 70)
        print(vid, "words:", len(text.split()), "| snippets:", len(t))
        print(text[:1400])
    except Exception as e:
        print("=" * 70)
        print(vid, "ERROR", str(e)[:200])
