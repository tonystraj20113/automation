# StoryFacts Automation

Free, unattended YouTube + Instagram pipeline: research competitors → write story-fact scripts → render Shorts and a weekly long video → publish/schedule.

**Cadence:** 5 Shorts/week (Mon–Fri) + 1 long video/week (Sunday).

**Stack (all free, no card):** public GitHub Actions, Groq Free API, edge-tts, ffmpeg, Python (Pillow + resvg-py), YouTube Data API, Instagram Graph API.

**Visuals:** every beat is a distinct illustrated scene — two locked art directions (ukiyo-e for history/folklore/nature, claymation for funny/science/modern), story-specific props, the clay-cat host, texture, vignette, caption cards and subtle Ken Burns motion.

## Repository layout
- `config/channels.json` — competitor list + brand settings
- `config/style_bible.md` — channel voice, visual rules, mascot spec
- `prompts/` — LLM prompt templates
- `src/` — pipeline code
- `assets/mascot.svg` — locked 2D clay-cat mascot (3D-look, softened)
- `.github/workflows/` — schedulers

## One-time setup
1. Create an **empty public** repository on GitHub (public = unlimited free Actions minutes).
2. Push this folder to it:
   ```bash
   git remote add origin https://github.com/<YOUR_USERNAME>/<REPO>.git
   git branch -M main
   git push -u origin main
   ```
3. Add these **Secrets** under Settings → Secrets → Actions:
   - `GROQ_API_KEY` — free key from https://console.groq.com
   - `YOUTUBE_CLIENT_SECRET_B64` — base64 of your OAuth client_secret.json
   - `YOUTUBE_TOKEN_B64` — base64 of the authorized token.json (generate once locally with `scripts/youtube_auth.py`)
   - `IG_ACCESS_TOKEN` — Meta Graph API token (IG professional account)
   - `IG_USER_ID` — Instagram professional account ID
   - `YT_PUBLISH_PRIVACY` — optional, default `private` (change to `public` after testing)
   - `YT_MADE_FOR_KIDS` — optional, default `false` (general audience)
3. Enable the YouTube Data API v3 in the same Google Cloud project as the OAuth client.
4. Meta app: Instagram Graph API with `instagram_content_publish` + `pages_read_engagement`. Token must be long-lived.
5. For Instagram, rendered videos must be at a **public URL**. The workflow uploads each render as a GitHub Release asset and passes that URL to the publisher.

## Local dry run
```bash
pip install -r requirements.txt
export GROQ_API_KEY=...
python -m src.run_shorts --dry-run
```
`--dry-run` writes the script, storyboard and audio but skips upload.

## Cost
$0. No paid APIs, no card, no laptop required after setup.
