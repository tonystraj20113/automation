# StoryFacts — Roblox Studio cloud Shorts

Free, unattended YouTube + Instagram pipeline. The **world is built inside Roblox Studio** and the whole pipeline runs in **GitHub Actions cloud** — no local machine needed after setup, no card, no paid APIs.

## The cloud/Studio route (verified against Roblox's official CLI docs)

Roblox Studio is a Windows GUI app, but it ships an official headless task:

```text
RobloxStudioBeta.exe --task RunScript --runScriptFile build_place.luau \
  --outputFile studio.log --quitAfterExecution
```

`--task RunScript` runs Luau at command-bar permission level. Omitting `--placeId` opens the default Baseplate, so **no Roblox login is needed**. Our generated Luau script:

1. clears the Baseplate and builds every block, stickman and prop in the DataModel,
2. exports the editable `.rbxl` place into the run folder,
3. prints `SCENE_JSON:` with every part's transform/colour to `--outputFile`,
4. quits.

The cloud renderer reads that manifest and frames the **same parts** with cinematic camera cuts and captions. So art direction happens in Studio (add/move/colour parts), not by editing style code.

## Pipeline

`src/run_roblox_short.py`

1. `src/research.py` + `src/self_improve.py` — free public competitor/keyword signals and topic scoring.
2. `src/roblox_story.py` — Groq Free writes a 15-line Gneef-grammar world-rule story (JSON script + 15 Studio sets).
3. `src/kokoro_tts.py` — Kokoro voice, locally generated from free public model files (cached in Actions).
4. `src/roblox_audio.py` — original toy-box score/foley, `mix.wav`, SRT and the single `timeline.js` timing source.
5. `src/roblox_place.py` — builds the real Roblox place headlessly and exports `scene.json` + `.rbxl`.
6. `src/render_roblox.py` — headless Edge + three.js renders the Studio-built parts at 1080×1920, ffmpeg muxes audio.
7. YouTube Data API schedules the Short; a public GitHub Release URL feeds Instagram Reels.

Daily `src/self_improve.py` scans competitor Shorts with yt-dlp, scores our own videos, and writes new low-competition premises into `config/topics.json`. The next film automatically uses the best unused premise.

## Cadence

- Mon–Fri 06:00 UTC: one Roblox Studio Short (`roblox-cloud.yml`).
- Daily 04:30 UTC: self-analysis (`self-improve.yml`).

## One-time setup (all free)

1. Create an **empty public** GitHub repository (public = unlimited free Actions minutes).
2. Push this folder:
   ```bash
   git remote add origin https://github.com/<YOUR_USERNAME>/<REPO>.git
   git branch -M main
   git push -u origin main
   ```
3. Add Actions Secrets:
   - `GROQ_API_KEY` — https://console.groq.com (free)
   - `YOUTUBE_API_KEY` — YouTube Data API v3 key
   - `YOUTUBE_CLIENT_SECRET_B64` — base64 of `client_secret.json`
   - `YOUTUBE_TOKEN_B64` — base64 of an authorized `token.json`
   - `IG_ACCESS_TOKEN`, `IG_USER_ID` — Instagram Graph API (professional account)
   - `YT_PUBLISH_PRIVACY` — `private` while testing; `public` once approved
   - `YT_MADE_FOR_KIDS` — `false`
4. The workflow installs Roblox Studio and ffmpeg with `winget`, installs `puppeteer-core`, caches Kokoro, then runs everything. Nothing is installed on your PC.

## Manual test

In GitHub: **Actions → Roblox Studio cloud Shorts → Run workflow**. Leave the topic blank for auto-selection, or type an id from `config/topics.json`.

Locally (optional): `winget install --id Roblox.RobloxStudio`, then
`python -m src.run_roblox_short --dry-run --topic lost-property`.

## Monetisation and originality guardrails

- Original stories only; no Roblox logos/branding, no copied scripts, titles, characters or assets.
- Blocky toy look is built from primitives; no third-party models or music.
- No violence, gore, romance, hate, crime, danger, self-harm, profanity or sensitive news.
- The generator rejects scripts containing blocked words; `safety` is recorded in every story JSON.
- Videos are `Made for kids = false`, general audience.

## Cost

$0. GitHub Actions (public repo free tier), Groq Free, Kokoro/edge-free public models, YouTube Data API free quota, Instagram Graph API, GitHub Releases for media URLs.
