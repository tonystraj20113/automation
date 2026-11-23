# Gneef Shorts — Link Analysis + Low-Competition Niche Research

**Research only. No video was built, rendered, or published.**
Date of research: **2026-11-23**. Working folder: `C:\Users\WOLF\Documents\storyfacts-automation`.

---

## 0. TL;DR

- All 7 links are public Gneef Shorts, **151–166 s** long, uploaded **2026-11-22 / 2026-11-23**, with the same production DNA: first-person young narrator, a supernatural **world rule** stated in the first 3 seconds, a family-scale mystery, one physical clue, a rule-based loophole, and a cold final-line twist.
- Live YouTube numbers (yt-dlp, 2026-11-23) range **481,865–3,016,299 views** and **17,444–88,135 likes**. vidIQ public pages show the same titles/durations but **older, lower snapshots** for several videos (and the vidIQ channel list is older still). Both are reported separately below.
- Measured shot pacing: **88–133 hard cuts per video at scene-score >0.3**, i.e. **0.58–0.82 cuts/s**, median gap **1.07–1.33 s**. Narration is **262–290 words/min** in the auto-captions.
- The "In This Town / In This World" formula itself is now **saturated** (compilations, AI tutorials, thousands of clones). The opportunity is not to copy the ruleey horror formula; it is to move it into **underserved, non-scary, specific settings**.
- **Chosen first sample topic: "The Lost Property Office 🧸"** — a gentle mystery with a lost-and-found rule. Direct-search competition is near-zero (`post office` query: median 191 views, 0/15 results over 100k), while the adjacent `lost and found` query has median 77,040 views and 6/15 results over 100k. It is original, has no Roblox branding, no gore, no hate, no dangerous instruction, and scores **9.5/10 advertiser-friendly**.

---

## 1. Source ledger — exactly which numbers came from where

### 1.1 Sources used

| Source | What it provided | Access method |
|---|---|---|
| YouTube public video pages / player API via **yt-dlp** | Exact title, `view_count`, `like_count`, `comment_count`, `upload_date`, `duration`, `description`, tags, channel follower count | `yt-dlp --dump-single-json --skip-download` |
| YouTube auto-captions (`en-orig`) via **yt-dlp** | Full timed transcript, hooks, endings, caption cadence | `yt-dlp --write-auto-subs --sub-langs en-orig --sub-format vtt` |
| **vidIQ public video pages** (`vidiq.com/youtube-stats/channel/@gneef/videos/<ID>/`) | Views, VPH, likes, comments, engagement rate, outlier multiple, displayed duration, title/thumbnail change record | `webfetch` |
| **vidIQ public channel About / Videos pages** | Channel totals, growth, est. revenue, 48-upload sample median | `webfetch` |
| **ffmpeg scene-score analysis** of low-res copies of the 7 public videos | Hard-cut counts and cuts/sec | `ffmpeg -vf "select='gte(scene,0)',metadata=print:key=lavfi.scene_score"` |
| **YouTube public search** via `yt-dlp ytsearch` + `websearch` | Competition estimates for candidate topics | flat playlists, public result titles/views |

No logged-in accounts, no private analytics, no user credentials were used.

### 1.2 Live YouTube / yt-dlp numbers (as read 2026-11-23)

Channel cross-check: `channel_follower_count = 2,230,000` from yt-dlp; vidIQ also reports **2.23M** subscribers.

| # | ID | Exact title | Views (YouTube/yt-dlp) | Likes (YouTube/yt-dlp) | Comments | Duration | Upload date |
|---|---|---|---:|---:|---:|---:|---|
| 1 | YLexXtj0V6Q | Three Knocks 🚪 | 1,020,654 | 48,001 | 455 | 157 s (2:37) | 2026-11-23 |
| 2 | 8H-aT3Cbrko | The Perfect Town 🌈 | 1,937,449 | 69,705 | 540 | 152 s (2:32) | 2026-11-23 |
| 3 | -JV8En1ONuM | The Callers ⚠️ | 669,786 | 27,240 | 386 | 166 s (2:46) | 2026-11-23 |
| 4 | 0iBC3Q5CZQw | The Haven Method 🔥 | 846,483 | 38,445 | 537 | 162 s (2:42) | 2026-11-22 |
| 5 | JngwoSrXXvI | The Garden 🌸 | 1,744,861 | 66,240 | 608 | 153 s (2:33) | 2026-11-22 |
| 6 | pwipzRBq-WE | Mr. Giggles 🎟️ | 3,016,299 | 88,135 | 624 | 164 s (2:44) | 2026-11-22 |
| 7 | uwfAd08q_U0 | Mount Kaerazu ⛷️ | 481,865 | 17,444 | 321 | 151 s (2:31) | 2026-11-22 |

All seven have identical description text: `#shorts #roblox #entertainment #viral #relatable`.
All seven carry the same broad tag cluster: `relatable, rant, funny, comedy, commentary, roblox, robloxgameplay, robloxstory, meme, school, genz, drama, trending, viral, storytime, roblox rants, roblox animation, animated stories, interesting, in this world, his story`.
Category: **Gaming**. Availability: **public**.

### 1.3 vidIQ public-page numbers (separate snapshots, same date)

| # | Title | Views (vidIQ video page) | VPH | Likes (vidIQ) | Comments (vidIQ) | ER | Outlier multiple | Duration (vidIQ) |
|---|---|---:|---:|---:|---:|---:|---:|---|
| 1 | Three Knocks 🚪 | 1.02 M | 255.45 K | 48.11 K | 455 | 4.8% | 3.6x | 2:37 |
| 2 | The Perfect Town 🌈 | 1.96 M | 196.42 K | 70.18 K | 541 | 3.6% | 2.89x | 2:32 |
| 3 | The Callers ⚠️ | 674.42 K | 44.96 K | 27.29 K | 386 | 4.1% | — | 2:46 |
| 4 | The Haven Method 🔥 | 695.28 K | 43.46 K | 33.14 K | 482 | 4.8% | — | 2:42 |
| 5 | The Garden 🌸 | 1.1 M | 87.85 K | 42.97 K | 492 | 4.4% | 1.19x | 2:34 |
| 6 | Mr. Giggles 🎟️ | 2.41 M | 85.37 K | 77.24 K | 574 | 3.5% | 1.99x | 2:45 |
| 7 | Mount Kaerazu ⛷️ | 411.97 K | 19.62 K | 15.34 K | 300 | 3.8% | — | 2:31 |

**Discrepancy note (important).** The three newest uploads (#1–3) match closely between vidIQ and yt-dlp. The four Nov-22 uploads diverge: e.g. **Mr. Giggles: 3,016,299 (YouTube) vs 2.41 M (vidIQ video page) vs 1,618,496 (vidIQ channel video list)**; **The Haven Method: 846,483 vs 695.28 K vs 90,143**. Likes diverge similarly (88,135 vs 77.24 K). The vidIQ channel-list page also does not yet contain the three Nov-23 uploads and calls "The Haven Method" the latest upload. Conclusion: **vidIQ pages are cached snapshots taken at different times on 2026-11-23; live YouTube/yt-dlp counts are the more current figures.** Treat vidIQ's outlier multiples and ER as vidIQ-model outputs, not YouTube-reported analytics.

**vidIQ channel-level context (public About page):** 2.23 M subscribers, 1,897,179,867 total views, 297 videos, +600 K subs in 28 d, 28,389,522 views/day, est. ad revenue $87 K (down 62% vs prior 14 d), 89 uploads in 28 d. Its **Videos page** says 92 uploads in 28 d, 28,215,494 views/day, $78 K est. revenue — the two vidIQ pages disagree slightly, another sign of cached snapshots. Median views across vidIQ's listed 48 most recent uploads (Nov 8–22): **3,310,228**; most viewed "2nd Shadow 👤" at 8,391,633. Channel description says: "Help Me Reach 3M Subs! … Gneef we love making Roblox Animations! Topics ranging from funny fictional stories, entertaining mysteries, interesting what-if scenarios … All scripting, editing, and animations are done by my team and I." (vidIQ, via YouTube's public channel description.)

---

## 2. Per-video analysis

### Common measurement notes
- **Cut counts** below are from ffmpeg scene-score on 360p public copies. A hard cut usually produces one high-score frame. Reported primary figure uses **scene score > 0.30** after merging detections <0.35 s apart; thresholds 0.20/0.40 are shown as sensitivity checks. These are estimates of visual shot changes, not an editor's EDL.
- **Caption rhythm** is derived from de-duplicated YouTube `en-orig` auto-captions. WPM = words / caption span. These are close to, but not identical to, the final spoken script. Auto-captions on several videos end mid-sentence in the last cue.
- **On-screen text style:** not OCR-verified in this session. This environment has no image-input support for frame reading and no Tesseract/EasyOCR installed, so burned-in caption typography, colour, or placement cannot be asserted from evidence. What *is* verifiable: no manual subtitle track exists (only auto-captions), titles use exactly one emoji, and the description uses exactly five hashtags. Any claim about font, stroke, or position would be guesswork, so it is deliberately omitted.

### 2.1 Three Knocks 🚪 — YLexXtj0V6Q
- **Source:** YouTube/yt-dlp 1,020,654 views / 48,001 likes; vidIQ 1.02 M / 48.11 K / VPH 255.45 K / 4.8% ER / **3.6x outlier** — the strongest outlier of the seven.
- **Hook, first two sentences (auto-caption, verbatim):** "In this world, something knocks on doors at night using the voices of people you love. But it can only knock three times."
- **World rule:** A door-knocking entity imitates loved ones' voices; it can only knock three times; four knocks = safe. Rule explained by neighbour Ruth at ~25 s.
- **Narrative pattern:** New student in cheap apartment → learns the counting rule → two months of quiet → 2:14 a.m. three knocks in mother's voice → doesorbell-camera check → phone call to real mom fails → entity learns the fourth knock → phone and door speak in unison → call log is empty.
- **Escalation:** private dread → building-wide catastrophe in the final line.
- **Ending type:** cold cliffhanger / implied mass breach — "Because tonight, every door in this building heard four knocks."
- **Visible/measured pacing:** 94 cuts >0.30, **0.60 cuts/s**, median gap 1.23 s (0.20: 126; 0.40: 60). 98 caption cues, **267.7 WPM**.
- **Caption rhythm:** short 1–1.7 s cues; "You see, that's the rule" lands at 5.4 s; the rule is restated at 33–36 s.
- **Repeatable device:** a countable rule (3 vs 4) that the monster learns — a loophole that can be closed by the enemy.

### 2.2 The Perfect Town 🌈 — 8H-aT3Cbrko
- **Source:** YouTube/yt-dlp 1,937,449 / 69,705; vidIQ 1.96 M / 70.18 K / VPH 196.42 K / 3.6% ER / **2.89x outlier**.
- **Hook:** "In this town, nobody has died in over 300 years. You see, our town sits on an island in the middle of a river."
- **World rule:** On Still Water island nobody can die; crossing the river makes you mortal; a dead forest across the river returns things that don't stay dead.
- **Narrative pattern:** idyllic town description → dead man found in the shallows in father's coat → mother confesses she held "the thing that came back wearing him" under → town exiles mother by boat (an unused 300-year-old rule) → narrator sees bark-and-sap back under the coat → swims out past the point where feet touch bottom and tows the boat back.
- **Escalation:** personal family secret → mob justice → physical rescue.
- **Ending type:** rescue + proof reveal; final caption truncates at "Mom climbed out, wrapped her arms around me, and wouldn't let…" (almost certainly "go"), i.e. emotional release rather than a twist.
- **Pacing:** 88 cuts >0.30, **0.58 cuts/s**, median 1.27 s (0.20: 104; 0.40: 69). 100 cues, **290.1 WPM** — the fastest narration in the set.
- **Caption rhythm:** dense "You see…" exposition at 3.9–11 s; rule + setting + protagonist's loss all inside 31 s.
- **Repeatable device:** a beautiful rule with a hidden cost; a childhood game ("who can wade furthest") becomes the climax skill.

### 2.3 The Callers ⚠️ — -JV8En1ONuM
- **Source:** YouTube/yt-dlp 669,786 / 27,240; vidIQ 674.42 K / 27.29 K / VPH 44.96 K / 4.1% ER.
- **Hook:** "In this world, something fell out of the sky into the forest. Where it landed, there's a room that grants any wish. But to reach it, you have to get past the callers."
- **World rule:** A sealed "zone" around a crash site; a wish room; "callers" are sheet-wrapped shapes that speak in the voices of the lost and lure you into traps. Stalkers throw metal bolts to test invisible hazards.
- **Narrative pattern:** narrator follows missing father's routes → hired by a man whose daughter is "sick" → bolt tests, sideways gravity, daughter-voice caller → footprint with cut heel matches dad → humming at night → the room → dad in doorway, but the man sees his dead daughter → realization: the room is the biggest caller.
- **Escalation:** expedition → dual revelation → the wish room consumes the client.
- **Ending type:** tragic loop / invitation to the viewer: the door reopens and "there he was, my dad, standing in the doorway, still waving me…" (caption ends mid-sentence).
- **Pacing:** 116 cuts >0.30, **0.70 cuts/s**, median 1.33 s (0.20: 130; 0.40: 82). 106 cues, **274.4 WPM**.
- **Caption rhythm:** rule stack delivered in ~39 s; every new hazard gets a one-sentence label before the action proves it.
- **Repeatable device:** the thing the protagonist wants most is the trap; two characters see different people in the same doorway.

### 2.4 The Haven Method 🔥 — 0iBC3Q5CZQw
- **Source:** YouTube/yt-dlp 846,483 / 38,445; vidIQ video page 695.28 K / 33.14 K / VPH 43.46 K / 4.8% ER; vidIQ video **list** only 90,143 (stale).
- **Hook:** "In this world, it won't stop snowing. The only warm place left on Earth is the generator."
- **World rule:** Frozen crater city in rings around a furnace; warmth depends on distance from the fire; the outer ring is being burned for fuel; "the Haven method" is the final step.
- **Narrative pattern:** coal sleds get lighter → boards from narrator's own street appear → engineers' map shows houses numbered for burning → old radio from "Haven" → narrator takes the frozen explorer's map and the mother's candle → trek to Haven → empty town, blue fire, human shapes burning but never consumed → realizes the radio loop is the method → returns too late → outer ring gone, smoke blue.
- **Escalation:** resource scarcity → conspiracy → rescue mission → failed homecoming.
- **Ending type:** bleak ironic twist in three words: "The smoke was blue."
- **Pacing:** 133 cuts >0.30, **0.82 cuts/s**, median 1.13 s — the fastest-cut video in the sample (0.20: 142; 0.40: 113). 101 cues, **272.5 WPM**.
- **Caption rhythm:** world-building in ring order (inner/middle/outer) = a visual ladder that can be cut on every sentence.
- **Repeatable device:** a colour-code rule (orange = safe, blue = wrong) that pays off in the final shot.

### 2.5 The Garden 🌸 — JngwoSrXXvI
- **Source:** YouTube/yt-dlp 1,744,861 / 66,240; vidIQ 1.1 M / 42.97 K / VPH 87.85 K / 4.4% ER / 1.19x outlier.
- **Hook:** "In this world, everyone is raised alone in a tiny white room. You see, from the day you're born, you never see another person."
- **World rule:** Children are isolated until 18, then given a "wife"; the walled Garden pairs one real person with one copy; white-suited, white-masked men replace anyone who asks questions.
- **Narrative pattern:** perfect first weeks → neighbour repeats the same greeting at exactly 8:00 → narrator spies a neighbour being swapped → deduction that every couple is one real + one copy → fear that the wife is a copy → her cut finger bleeds → narrator's own knife test shows white plastic → box of three wedding rings: "You're my fourth" → masked men come → narrator draws them away so she can escape through the always-open metal door.
- **Escalation:** domestic idyll → forensic doubt → identity reveal → sacrificial escape.
- **Ending type:** bittersweet self-sacrifice with a visual confirmation: "she was running along the wall through the open metal door, and she didn't look back."
- **Pacing:** 119 cuts >0.30, **0.78 cuts/s**, median 1.10 s (0.20: 132; 0.40: 92). 98 cues, **280.7 WPM**.
- **Caption rhythm:** the "You see," clause at 3.4 s; the 18th-birthday rule lands at 16–20 s; protagonist appears at 22 s.
- **Repeatable device:** physical proof object (three rings, a cut that doesn't bleed) converts an abstract rule into a visual clue.

### 2.6 Mr. Giggles 🎟️ — pwipzRBq-WE
- **Source:** YouTube/yt-dlp **3,016,299 / 88,135** — highest views, likes and comments in the sample; vidIQ video page 2.41 M / 77.24 K / VPH 85.37 K / 3.5% ER / **1.99x outlier**; vidIQ list 1,618,496 (stale).
- **Hook:** "In this town, the luckiest thing that can ever happen to you is meeting Mr. Giggles. You see, every Friday at sunset, his black van rolls down one street and he steps out."
- **World rule:** A mime hands out pink cards; attendees come home "better" but silent, smiling and bowing; his painted tricks become real; anyone who makes a sound at the show stays at the show; rain keeps him home.
- **Narrative pattern:** father loses his job and goes to the show → returns "perfect" but wrong (doesn't eat, too clean, crack in hand shows white) → bowing at 3 a.m. → narrator follows the van to the striped tent → rows of painted, chained audience; real dad in front row → rule painted above stage → mime lassos and chains narrator → only the right hand is free → remembers rain is the one weakness → cuts the ordinary rope holding the roof flap → rain washes the paint mime away → copies melt at home → dad burns the pancakes again.
- **Escalation:** curiosity → abduction → global town reveal → tidy victory.
- **Ending type:** cathartic resolution with a small humanising coda ("Dad doesn't make star pancakes anymore. He burns them…") and an image of the empty rusting van.
- **Pacing:** 130 cuts >0.30, **0.79 cuts/s**, median 1.17 s (0.20: 141; 0.40: 111). 100 cues, **261.9 WPM**.
- **Caption rhythm:** benefit-first hook (luckiest thing), then rule, then a 17-year-old protagonist at 29 s; "You see," at 3.0 s.
- **Repeatable device:** the magic has one mundane, pre-established countermeasure — rain. This is the cleanest brand-safe template in the sample.

### 2.7 Mount Kaerazu ⛷️ — uwfAd08q_U0
- **Source:** YouTube/yt-dlp 481,865 / 17,444 — lowest views and likes in the sample; vidIQ 411.97 K / 15.34 K / VPH 19.62 K / 3.8% ER; vidIQ list 374,066.
- **Hook (note: the only non-"In this world/town" opener):** "On Mount Kayazu, if anyone leaves your group, something comes back in their place. You see, last winter, 10 of us, classmates from the same school, set out on skis to cross the frozen mountains of northern Japan."
- **World rule:** If someone leaves the group on the mountain, the mountain fills the empty place; the old man's warning is explicitly stated at 39–44 s.
- **Narrative pattern:** ten skiers → Danny turns back sick → nine continue → Danny returns to the tent → ski tracks come *down from the peak*, not up the trail → no breath fog → group cuts the back of the tent and flees barefoot → counts nine at the fire → breath test: fog, fog, fog — but narrator's own breath produces nothing.
- **Escalation:** expedition → impossible return → group paranoia → self-revelation.
- **Ending type:** identity-horror twist, single-word proof: "Nothing."
- **Pacing:** 124 cuts >0.30, **0.82 cuts/s**, median 1.17 s (0.20: 127; 0.40: 106). 94 cues, **263.0 WPM**.
- **Caption rhythm:** rule in sentence one; "You see," at 3.2 s; the warning is delivered by an elder at 39 s, then proven at 77–95 s.
- **Repeatable device:** a sensory test (breath fog) that the audience can check along with the narrator.

### 2.8 Pacing summary table

| ID | Title | Cuts >0.30 | Cuts/s | Median gap | Cues | WPM | Ending |
|---|---|---:|---:|---:|---:|---:|---|
| YLexXtj0V6Q | Three Knocks 🚪 | 94 | 0.60 | 1.23 s | 98 | 267.7 | cliffhanger |
| 8H-aT3Cbrko | The Perfect Town 🌈 | 88 | 0.58 | 1.27 s | 100 | 290.1 | rescue + proof |
| -JV8En1ONuM | The Callers ⚠️ | 116 | 0.70 | 1.33 s | 106 | 274.4 | tragic loop |
| 0iBC3Q5CZQw | The Haven Method 🔥 | 133 | 0.82 | 1.13 s | 101 | 272.5 | bleak twist |
| JngwoSrXXvI | The Garden 🌸 | 119 | 0.78 | 1.10 s | 98 | 280.7 | sacrifice |
| pwipzRBq-WE | Mr. Giggles 🎟️ | 130 | 0.79 | 1.17 s | 100 | 261.9 | clean victory |
| uwfAd08q_U0 | Mount Kaerazu ⛷️ | 124 | 0.82 | 1.17 s | 94 | 263.0 | identity twist |
| **Average** |  | **115** | **0.73** | **1.20 s** | **100** | **272.9** | 6/7 twist-shaped |

---

## 3. The repeatable Gneef formula

### 3.1 Title patterns
- Definite article + concrete noun or proper name: *The Perfect Town, The Callers, The Haven Method, The Garden, Mount Kaerazu*. The outlier is a countable event: *Three Knocks*.
- **Exactly one emoji**, placed at the end: 🚪 🌈 ⚠️ 🔥 🌸 🎟️ ⛷️. No question marks, no "you won't believe", no numbers except the rule itself ("Three").
- Description is identical across all seven: five hashtags. Title and description do no SEO work — the hook does it.

### 3.2 First-line hooks
Five of seven open with **"In this world…"** or **"In this town…"**; one opens with a proper-name location (**"On Mount Kayazu…"**); one opens with **"In this town, the luckiest thing…"** — a benefit-first inversion.
Structural rule: **the supernatural constraint arrives in sentence 1; a complicating "But…" or "You see…" arrives by 3–5 s.** No character name, no backstory, no greeting. The viewer is told the rules of the game before they are asked to care about a person.

### 3.3 World rules
Every story is a single-sentence rule that a child could repeat:
- 3 knocks = danger, 4 = safe.
- Nobody can die on the island.
- The wish room grants anything — if you survive the callers.
- Warmth = proximity to the furnace.
- At 18 you are given your lifelong partner; half of each couple is a copy.
- Whatever the mime pretends becomes real; make a sound and you stay.
- Leave the group on the mountain and something takes your place.

Rules are **countable, testable and visual** — which is what makes them animatable with simple blocky geometry.

### 3.4 Conflict structure
1. Rule announced (0–5 s).
2. "You see," world tour with concrete sensory details (5–25 s).
3. A personal loss is planted — missing dad, dead father, silent dad, mother's candle (20–40 s).
4. Protagonist is 16–18, ordinary, slightly sceptical.
5. An elder/neighbour/parent states the rule again in practical terms (25–45 s).
6. Small anomaly appears in daily life (a sign, muddy boots, a cut heel, a cracked hand, three rings, no breath fog).
7. Protagonist tests the anomaly; the test confirms the rule is literally true.
8. The institution (town, facility, engineers, show, mountain) moves against them.
9. Protagonist exploits a **pre-established loophole** — count to four, throw a bolt, take the map, cut the rope, cut the tent, test the breath.
10. Final line reclassifies everything.

### 3.5 Escalation
Personal → family → whole town/world, usually in the last 15–25 s. The scale jump is delivered by one sentence, not a montage: "Because tonight, every door in this building heard four knocks"; "The smoke was blue"; "Nothing."

### 3.6 Ending types
Six of seven end on a twist, not a moral. The twist is always **a short declarative line** of 2–12 words, often with the last word alone on its own beat. The two non-twist endings still close on an image (rusting van, mother's arms). There is no "like and follow" call inside the narration.

### 3.7 Caption rhythm
- Auto-caption cues average ~100 per 150–166 s = **0.6 cues/s**, roughly one new cue every 1.5–1.7 s.
- Spoken delivery averages **~273 WPM**, far above conversational speed; clues arrive every 8–15 s.
- "You see," is a hard reset button used at ~3–5 s in five of seven videos, followed by rapid world detail.
- Rule restatements occur at ~30–45 s, roughly the 20–30% mark — the same position the public "how to make these shorts" tutorials describe for the hero who breaks the rule.

### 3.8 Shot pacing
With hard cuts at >0.30 scene score: **0.58–0.82 cuts/s**, median 1.07–1.33 s per shot. The two fastest-cut videos (Haven Method 0.82, Mount Kaerazu 0.82) are also the two most dread-heavy; the gentler Perfect Town is slowest (0.58). So pacing is a **genre dial**: dread → cut faster, wonder → hold shots longer. The reliable baseline is **one visual idea per 1.2 seconds**.

### 3.9 What is *not* part of the formula
No on-screen logo, no public figure, no news event, no explicit gore, no hate, no instructional danger. The scary material is implied by narration and simple shapes — which is why most of these are monetisable despite the horror framing (the Garden and Callers are the closest to the line).

---

## 4. Independent niche research: where competition is actually low

Method: public YouTube search through `yt-dlp --flat-playlist ytsearch`, plus `websearch`. Queries were run on 2026-11-23. "Median views" and "≥100k" describe the top 12–15 public results returned by that query on that day; they are a competition proxy, not a guarantee of demand. Raw data: `research/raw/niche_competition.json`, `research/raw/niche_search.json`.

| Query (competition proxy) | Results | Median views | Results ≥100k | Reading |
|---|---:|---:|---:|---|
| `roblox animation "in this town" short` (core formula) | 15 | 61,512 | 4 | Core formula is crowded but still has a few big compilations. |
| `roblox animation "lost and found" story short` | 15 | 77,040 | 6 | Adjacent demand is proven; moderate competition. |
| `roblox animation "library" "in this town"` | 14 | **521** | **0** | Almost no direct competition; demand unproven but adjacent. |
| `roblox animation "post office" story short` | 15 | **191** | **0** | Effectively empty niche. |
| `roblox animation "umbrella" "in this town"` | 10 | **285** | 1 | Empty niche with a simple visual prop. |
| `roblox animation "lighthouse" story short` | 15 | 436 | 3 | Empty long tail, but one 4.9 M-view outlier proves upside. |
| `roblox animation "bus stop" story short` | 15 | 525 | 4 | Sparse direct results, strong non-Roblox outliers (4.86 M, 2.45 M). |
| `roblox animation "laundromat" story short` | 15 | 1,593 | 3 | Sparse; top result 12.6 M (broad, not exact match). |
| `roblox animation "clock" "in this town"` | 15 | 923 | 2 | Sparse. |
| `roblox animation "shoes" "in this town" story` | 12 | 260 | 1 | Very sparse. |
| `roblox story animation short wholesome mystery` | 11 | 60 | 0 | Almost no one is explicitly serving the non-scary lane. |
| `roblox storytime shorts scary rules` | 15 | 386,437 | 9 | Scary-rule lane is crowded — avoid. |
| `roblox animation "copy" "in this town" short` | 15 | 2,455 | 3 | Copy/replacement trope is heavily used by Gneef and others; avoid as a first sample. |

Supporting web findings:
- Public search surfaces many **compilation channels** ("In This Town / In This World Roblox Stories Compilation" at 306 K, 2.53 M, 1.04 M views) and a whole **tutorial economy** ("How to Make Viral Roblox 'In This Town' 3D Animations…" at 197 K, 92 K, 59 K views). That confirms the generic formula is mature and being mass-produced.
- One public tutorial transcript describes the pattern from the outside: "It opens on the rule… At about 20%, the hero shows up and he's the worst at the rule." This corroborates the structural reading in §3 from an independent source.
- Direct search for the Gneef titles themselves mostly returns reaction/compilation channels, not original rule-story competitors in the gentle settings above.
- `websearch` also surfaced "In This World, Everyone Follows One Rule 🧐" and a Short at 1.8 M views ("In This World, Nobody Has Ever Escaped The Maze…"), showing the *format* still travels when the setting is fresh — the differentiator is premise, not the opener.

**Strategic conclusion:** do not compete on "creepy rule horror" (crowded, and the least brand-safe). Compete on **specific, kindly, object-centred worlds** (post office, lost property, library, umbrella stand) where the rule is emotional rather than lethal. Those queries show almost no direct competition while the adjacent lost-and-found and wholesome-mystery signals show an audience.

---

## 5. Ten concrete low-competition topic/premise ideas

Potentials are directional estimates from the search evidence above, not forecasts.

| Rank | Title | First 2 hook sentences | Why low competition (evidence) | Est. potential | Brand safety |
|---:|---|---|---|---|---|
| 1 | **The Lost Property Office 🧸** | "In this town, the lost-and-found office is never empty. Whatever you leave there comes back the next morning with a note in someone else's handwriting." | `post office` median 191 views, 0/15 ≥100k; `lost and found` median 77,040 with 6/15 ≥100k — empty setting, proven adjacent demand. | **High** | **9.5/10** |
| 2 | The Library of Unfinished Letters 💌 | "In this town, the library only lends out letters you never wrote. Every book on the return cart is still warm." | `library` median 521 views, 0/15 ≥100k; physical prop is cheap to build. | Medium-high | 9.5/10 |
| 3 | The Umbrella Stand ☂️ | "In this town, it only rains on people who told a lie that morning. The umbrella stand outside the school is always full by noon." | `umbrella` median 285 views, 1/15 ≥100k; weather is a strong visual hook and an easy animation trick. | Medium-high | 9.5/10 |
| 4 | The Last Lighthouse 🔦 | "In this town, the lighthouse turns on by itself — but only when somebody out at sea is lost. Tonight it lit up three times." | `lighthouse` median 436, but 3/15 ≥100k including 4.95 M — sparse with proven upside. Keep peril offshore and non-graphic. | High | 8.5/10 |
| 5 | The Clock That Runs Backwards ⏰ | "In this town, one clock in the square runs backwards, and everybody sets their watch by it. Nobody says why." | `clock` median 923 views, 2/15 ≥100k; visual rule is instantly legible. | Medium | 9/10 |
| 6 | The Shoe Repair Shop 👟 | "In this town, the cobbler fixes shoes and the paths they walked. He has a shelf of roads he took back." | `shoes` median 260 views, 1/15 ≥100k; wholly unclaimed setting. | Medium | 9/10 |
| 7 | The Number Nine Bus 🚌 | "In this town, the number nine bus stops only for people who have nowhere else to go. Nobody who rides it ever gets off at the same stop." | `bus stop` median 525, 4/15 ≥100k (non-Roblox outliers to 4.86 M). Keep it hopeful, never mock homelessness. | Medium-high | 8/10 |
| 8 | The Laundromat of Second Chances 🧺 | "In this town, the last machine in the laundromat washes the stains out of your past. It only takes one coin — and one true story." | `laundromat` median 1,593 views, 3/15 ≥100k; intimate setting, strong reveal object. | Medium | 9/10 |
| 9 | The Borrowed Name 🪪 | "In this town, if you say your own name out loud, somebody else gets it for a day. Today my name is on somebody else's door." | Identity trope is proven for Gneef (Garden, Kaerazu) but generic search median is only 2,455; keep it light, not body-horror. | Medium | 8/10 |
| 10 | The Kindness Ledger 📖 | "In this town, every good deed gets written in a book at the post office. This morning the book started writing back." | `gentle mystery` median 60 views, 0/15 ≥100k — essentially unserved; `post office` also empty. | Medium (untested) | 10/10 |

---

## 6. Top 3 — ranking and advertiser-friendliness scoring

Score components (each 0–2, total 10): **originality/IP**, **violence/scare intensity**, **sensitive-subject risk**, **language**, **advertiser fit**. Higher = safer.

| Rank | Idea | Originality | Violence/scare | Sensitive topics | Language | Advertiser fit | **Total** | Verdict |
|---:|---|:--:|:--:|:--:|:--:|:--:|:--:|---|
| 1 | The Lost Property Office 🧸 | 2 | 2 | 2 | 2 | 1.5 | **9.5** | Best overall: gentle, object-led, emotionally positive, no IP. |
| 2 | The Library of Unfinished Letters 💌 | 2 | 2 | 2 | 2 | 1.5 | **9.5** | Equally safe; slightly weaker visual variety than a parcel office. |
| 3 | The Umbrella Stand ☂️ | 2 | 2 | 1.5 | 2 | 1.5 | **9.0** | "Lying" rule is fine, but weather-driven colour/peril reads slightly more dramatic. |

Why not the higher-view horror premises:
- **Three Knocks / The Callers / Mount Kaerazu / The Garden** rely on stalking, abduction, body-replacement horror and self-harm-adjacent proof (knife test) — advertiser-risky by comparison.
- **The Perfect Town** includes a dead body and drowning; **The Haven Method** implies people being burned as fuel. Both are narratively strong but not the safest first sample.
- **Mr. Giggles 🎟️** is the safest of the seven actual Gneef videos (magic, no gore, rain defeat), but its copy/identity premise is already well trodden by the channel and by clone channels.

Monetization guardrails for the chosen lane:
- Original story and characters; **no Roblox name, logo, avatar assets, block-avatar catalog items, game names, or UI** on screen. Generic blocky geometry only.
- No graphic injury, no death, no self-harm, no stalking imagery, no hatred or harassment, no real-world tragedy or news, no dangerous instructions, no swearing.
- Conflict is emotional (lost object, unsent letter), resolved by kindness and a simple rule-based trick.
- Clean description with no engagement-bait or "routine" language.

---

## 7. Chosen first sample topic — full ready spec (research only, not built)

### 7.1 Core
- **Title:** `The Lost Property Office 🧸`
- **Format target:** 150–158 s vertical (9:16), matching the sample's 151–166 s band.
- **First two hook sentences (spoken, verbatim):**
  1. "In this town, the lost-and-found office is never empty."
  2. "Whatever you leave there comes back the next morning — with a note in someone else's handwriting."
- **On-screen text for the first 2 s (different words from the spoken line, unverified style in source videos — this is a design recommendation, not a finding):** `NOTHING STAYS LOST`.
- **Description:** `#shorts #animation #story #mystery #kindness` — no `#roblox`, no copyrighted asset references.
- **Ending line:** "And the box was empty. For the first time ever."

### 7.2 Ten-beat outline (~15 s per beat, 150 s total)

| Beat | Time | Story action | Visual (blocky 3D, no paid assets) |
|---:|---|---|---|
| 1 | 0–12 s | Rule + hook sentences; "You see," by 5 s. | A small grey counter with a wooden box; one toy block sits in it. |
| 2 | 12–25 s | World tour: the office has three rules — leave one thing, take one thing, never read the note out loud. | Three simple wall signs built from cubes, one rule per shot. |
| 3 | 25–38 s | Protagonist (teen) is introduced: they lost their mother's old key years ago and want it back. | Stickman figure at the counter, one small brass-coloured key shape in memory flash. |
| 4 | 38–52 s | Clerk says every returned item already belongs to somebody else by morning; the notes are never in the owner's handwriting. | Clerk behind counter, stack of paper notes, close-up on a note. |
| 5 | 52–66 s | Protagonist leaves a plain button from their mother's coat. Waits all night on the steps. | Button drop; time-lapse of the empty office, single light cube glowing. |
| 6 | 66–80 s | Morning: the button is gone; in its place is a folded note in familiar handwriting: "I kept it safe for you." | Note slides out of box; handwriting shown as simple blocky strokes. |
| 7 | 80–95 s | Next note appears in the protagonist's *own* handwriting — describing the mother's key, which nobody knows about. | Close-up of the note; key silhouette appears behind the counter. |
| 8 | 95–112 s | Rule twist: the office doesn't return what you lost. It returns what someone else was **afraid to lose** — and keeps the rest. | Rows of small objects on shelves, each lit for half a second. |
| 9 | 112–132 s | Protagonist chooses to leave the one thing they still had — the note itself — to free whatever it was holding. Simple, non-dangerous loophole: **the office takes only one object at a time**. | Note dropped into the box; lights go out one shelf at a time. |
| 10 | 132–150 s | The mother's key is on the counter with a fresh note: "You can keep it now." The box is empty for the first time ever. Final line delivered over a static shot of the open box. | Empty wooden box, key in a stickman hand, slow zoom out. |

### 7.3 Why it should retain viewers
- The rule is stated in sentence 1 and is **countable** (one thing in, one thing out, no reading the note) — same cognitive hook as 3-vs-4 knocks.
- A personal loss (the mother's key) is planted by 25–38 s, the same 20–30% position where Gneef plants family stakes.
- Every beat has a **physical prop** (box, button, notes, key) — cheap to build in blocky 3D and easy to cut on, matching the measured 1.2 s median shot gap.
- Escalation is emotional rather than violent: personal keepsake → other people's fears → the narrator's own sacrifice → release.
- The ending is a short declarative twist line over a static image, the same closing shape as "The smoke was blue" and "Nothing."
- It is loop-friendly: the last image (empty box) answers the first line ("the office is never empty").

### 7.4 Production constraints (for the eventual build, not executed here)
- Code-built blocky 3D stickman world; primitives only — boxes, cylinders, simple extruded text for signs/notes.
- No Roblox branding, logos, avatar packages, game UI, or third-party character designs.
- Palette: warm greys, one amber light, one blue note accent — the colour-rule trick from *Haven Method* without the dread.
- Target pacing from §2.8: ~115 shots, 0.7–0.8 cuts/s, narration ~270 WPM, one cue every ~1.5 s.
- Music: original/royalty-free bed, no copyrighted tracks.

---

## 8. Caveats and honest limits

1. **vidIQ snapshots conflict.** The channel About page, Videos page and individual video pages were fetched on the same date but show different totals and view counts; the vidIQ Videos page omits the three Nov-23 uploads entirely. All vidIQ figures are labelled as such; live YouTube/yt-dlp figures are labelled separately.
2. **Freshness.** These videos were 0–1 days old when measured. View and like counts will keep moving; VPH and outlier multiples are early-life figures.
3. **Outlier multiples are gated.** vidIQ displays the multiple but hides the derivation behind signup; treat them as vidIQ's model, not YouTube data.
4. **Auto-captions truncate.** Several endings end mid-sentence; ending descriptions above mark the inferred completion where obvious.
5. **Cut counts are algorithmic estimates.** Scene-score thresholds 0.20/0.30/0.40 are reported together; no editor project files were available.
6. **No on-screen-text verification.** This session could not OCR or visually inspect frames (no image input support, no OCR package), so typography/colour/placement claims are intentionally absent. The "on-screen text" field is recommendation-only where marked.
7. **Niche search is a proxy.** YouTube search results are personalised/volatile and include compilations and tutorials that are not exact competitors. The median/≥100k figures indicate how crowded a *query* is, not guaranteed demand for a new upload.
8. **Nothing was rendered, published, or uploaded.** All artifacts are raw research files under `research/raw/` and this report.

### Raw artifacts
- `research/raw/gneef_meta.json` — YouTube/yt-dlp metadata for all 7.
- `research/raw/subs/*.en-orig.vtt` — original auto-captions.
- `research/raw/transcripts/*.txt` — de-duplicated timed transcripts; `summary.json` — cue/WPM stats.
- `research/raw/cut_analysis.json` + `cuts_*.txt` — ffmpeg scene scores and cut statistics.
- `research/raw/niche_search.json`, `research/raw/niche_competition.json` — public search samples.
- Helper scripts: `research/_collect_gneef.py`, `_collect_subs.py`, `_parse_subs.py`, `_cut_analysis.py`, `_niche_search.py`, `_niche_competition.py`.
