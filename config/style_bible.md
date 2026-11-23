# StoryFacts — Style Bible (locked)

## Voice
English, entertainment/facts. One fascinating true fact or "what if" told as a **mini-story** with a character, a turn, and a cliffhanger. Warm, curious, never lecture-y. No filler intro ("hey guys").

**Learned from the reference channels (see `research/FINDINGS.md`):**
- Open on a single vivid, specific image in medias res. Never "In 1900, X happened."
- Second sentence pivots with "You see," and grounds the world.
- Named people with a goal and a problem; concrete numbers, objects and sounds.
- Short sentences and fragments for pace: "No flag. No men. Nobody answered."
- Explain the cause *inside* the action, not in a separate lecture beat.
- End on an unresolved image, not a tidy moral.
- 200–260 words per Short (~55–80 s), 12–18 visual beats.

## Short structure (20–35 s)
1. **0–1 s hook** — payoff first: the strangest image or line up front.
2. **Proof beat** — the real fact / setup.
3. **3 fast beats** — escalation, twist, consequence.
4. **Loop ending** — final line ties back to the hook so viewers rewatch.
Burned-in captions, 3–6 words per card.

## Long structure (6–10 min)
Weekly compilation of the 5 Shorts, expanded with context, chapters, and a short "what we learned" closing.

## Visual system (rich, reference-channel detail)
- **Constant host:** clay-cat mascot (`assets/mascot.svg`) — 2D SVG, soft low-poly facets, two black dot eyes, muted terracotta/cream palette, warm rim light. Never change the core silhouette.
- **Every beat is a distinct, fully illustrated scene** — never a plain colour card. Each scene layers: gradient sky, celestial body, parallax terrain, clouds/particles, 1–2 story-specific props, the mascot with drop shadow + rim light, film grain, vignette.
- **Two art directions, switched by genre:**
  - history / folklore / nature / emotional → **ukiyo-e**: indigo + cream limited palette, bold ink outlines, Hokusai-style wave bands, mountains, birds, falling petals, paper grain.
  - funny / science / everyday / modern → **claymation**: soft blobby hills, tactile highlights and shadows, warm pastel palette, floating particles, clay texture.
- **Scene direction comes from the script:** each caption carries `motif` (ocean/river/mountains/forest/city/sky/space/night/desert/room), `props` (jar, key, coin, compass, book, clock, bottle, fish, bird, moon, star, door, chest, map, flower, ship, lantern, egg, apple, phone), and `mood` (curious/mystery/spooky/playful). The renderer auto-infers these if missing.
- **Motion:** gentle 3-step Ken Burns push per beat so frames never sit still.
- **Typography:** STORYFACTS brand chip, episode title on the opening beat, high-contrast caption card in the lower third with an accent bar, progress dots. Captions never cover the mascot's eyes.
- **Canvas:** 1080×1920 Shorts, 1920×1080 long. Safe margins 12%.

## Titles
Short phrase + one emoji. Prefer "You / Your / Everyone" hypotheticals when the story supports it. Never copy a competitor's title verbatim.

## Originality
Research the niche for signals, never lift scripts. Every script must be newly generated from the source fact and pass a similarity check against the competitor titles in `config/channels.json`.
