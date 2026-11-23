Write one original English story-fact short for a YouTube/Instagram channel. Topic hint: {topic}. Competitor signals: {signals}.

Rules:
- 20-35 seconds, spoken narration only, no intro, no "subscribe".
- Start with the payoff in the first 1 second.
- One true, verifiable fact packed with CONCRETE detail: a specific number, name, place, year, object or mechanism. Vague claims like "something strange happened" are banned.
- If unsure of a detail, frame the whole script as a "what if" instead of stating it as fact.
- Three fast escalation beats, each adding a NEW specific (a cause, a consequence, a number), then a loop ending that echoes the hook.
- Cute clay-cat host appears; inner story style must be exactly "ukiyo-e" or "claymation".
- Captions: 3-6 words per card. One scene per caption.

For EVERY caption, choose scene direction so the art is specific to the story:
- motif: one of ocean, river, mountains, forest, city, sky, space, night, desert, room
- props: 1-2 concrete objects from: jar, key, coin, compass, book, clock, bottle, fish, bird, moon, star, door, chest, map, flower, ship, lantern, egg, apple, phone
- mood: curious, mystery, spooky, or playful

Return ONLY valid JSON:
{"title":"short title + one emoji","hook":"line 1","proof":"line 2","beats":["line 3","line 4","line 5"],"ending":"line 6","story_style":"ukiyo-e|claymation","captions":["...","..."],"scenes":[{"motif":"ocean","props":["jar"],"mood":"mystery"},{"motif":"room","props":["key"],"mood":"curious"}],"fact_source":"one-line source note"}
The scenes array must have exactly the same length as captions.
