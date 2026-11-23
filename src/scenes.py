"""Procedural, story-specific scene art.

Builds rich, layered illustrations (two locked art directions) so videos look
like the reference channels instead of flat caption cards. Everything is drawn
in Pillow - no external image API, no key, fully free.
"""
import hashlib, math, random

from PIL import Image, ImageDraw, ImageFilter

PALETTES = {
    "ukiyo-e": {
        "sky_top": "#243A5E", "sky_bottom": "#7E9BB5",
        "paper": "#F3E5C8", "ink": "#231C17",
        "accent": "#C45436", "foam": "#F8F2E4",
        "hill_near": "#2A3F5C", "hill_far": "#647E96",
        "ground": "#D8C19A", "glow": "#F0D6A0",
    },
    "claymation": {
        "sky_top": "#6E93B8", "sky_bottom": "#F0D9BE",
        "paper": "#FBF4EA", "ink": "#3B2B23",
        "accent": "#D98650", "foam": "#FFF8EF",
        "hill_near": "#B98A68", "hill_far": "#D9B494",
        "ground": "#E7C7A6", "glow": "#FFE7BE",
    },
}

MOTIFS = ("ocean", "mountains", "forest", "city", "sky", "space",
          "room", "desert", "river", "night")
PROPS = ("jar", "key", "coin", "compass", "book", "clock", "bottle",
         "fish", "bird", "moon", "star", "door", "chest", "map",
         "flower", "ship", "lantern", "egg", "apple", "phone")


def _seed(*parts):
    h = hashlib.sha1("|".join(str(p) for p in parts).encode()).hexdigest()
    return int(h[:8], 16)


def _mix(c1, c2, t):
    c1 = c1.lstrip("#"); c2 = c2.lstrip("#")
    return tuple(
        int(int(c1[i:i+2], 16) * (1 - t) + int(c2[i:i+2], 16) * t)
        for i in (0, 2, 4)
    )


def _rgba(hexcolor, alpha=255):
    c = hexcolor.lstrip("#")
    return (int(c[0:2], 16), int(c[2:4], 16), int(c[4:6], 16), alpha)


def _gradient(w, h, top, bottom, vertical=True):
    img = Image.new("RGB", (w, h), top)
    d = ImageDraw.Draw(img)
    n = h if vertical else w
    for i in range(n):
        t = i / max(1, n - 1)
        c = _mix(top, bottom, t)
        if vertical:
            d.line((0, i, w, i), fill=c)
        else:
            d.line((i, 0, i, h), fill=c)
    return img


def _soft_shadow(base, box, blur, opacity=90):
    layer = Image.new("RGBA", base.size, (0, 0, 0, 0))
    ImageDraw.Draw(layer).ellipse(box, fill=(0, 0, 0, opacity))
    layer = layer.filter(ImageFilter.GaussianBlur(blur))
    base.alpha_composite(layer)


# ---------------------------------------------------------------------------
# Motif painters
# ---------------------------------------------------------------------------
def _waves(d, w, h, pal, rng, y0, layers=4):
    """Layered Hokusai-style wave bands with foam crests."""
    for k in range(layers):
        yy = y0 + k * h * 0.075
        amp = h * (0.035 - k * 0.004)
        col = _mix(pal["hill_near"], pal["hill_far"], k / max(1, layers - 1))
        pts = []
        for x in range(0, w + 20, 12):
            y = yy + math.sin(x / w * math.pi * (3 + k * 0.7) + k) * amp
            pts.append((x, y))
        d.polygon(pts + [(w, h), (0, h)], fill=col)
        # foam crest
        crest = [(x, y - 3) for x, y in pts]
        d.line(crest, fill=pal["foam"], width=max(2, int(w * 0.003)))
        for x, y in pts[::7]:
            r = max(2, int(w * 0.006 * (1 - k / layers)))
            d.arc((x - r, y - r, x + r, y + r), 190, 350,
                  fill=pal["foam"], width=max(1, int(w * 0.002)))


def _mountains(d, w, h, pal, rng, y0):
    for layer, (col, height, base) in enumerate([
        (pal["hill_far"], h * 0.20, y0),
        (pal["hill_near"], h * 0.15, y0 + h * 0.06),
    ]):
        pts = [(0, h)]
        x = -w * 0.1
        while x < w * 1.1:
            peak = base - height * (0.6 + rng.random() * 0.6)
            half = w * (0.10 + rng.random() * 0.10)
            pts += [(x, base), (x + half, peak), (x + half * 2, base)]
            x += half * 2
        pts += [(w, h)]
        d.polygon(pts, fill=col)
        # snow caps / rim light
        for i in range(1, len(pts) - 1, 3):
            px, py = pts[i]
            if py < base - height * 0.5:
                s = w * 0.018
                d.polygon([(px, py), (px - s, py + s), (px, py + s * 0.6),
                           (px + s, py + s)], fill=pal["foam"])


def _forest(d, w, h, pal, rng, y0):
    for depth in range(3):
        col = _mix(pal["hill_far"], pal["hill_near"], depth / 2)
        base = y0 + depth * h * 0.06
        for x in range(-int(w * 0.05), w + int(w * 0.05), int(w * (0.05 - depth * 0.008))):
            th = h * (0.10 + rng.random() * 0.09) * (1 + depth * 0.25)
            tw = th * 0.16
            jx = x + rng.randint(-int(w * 0.01), int(w * 0.01))
            d.rectangle((jx - tw * 0.12, base, jx + tw * 0.12, base + th * 0.4), fill=pal["ink"])
            for t in range(3):
                cy = base - t * th * 0.22
                ww = tw * (1 + t * 0.45)
                d.polygon([(jx, cy - th * 0.30), (jx - ww, cy + th * 0.10),
                           (jx + ww, cy + th * 0.10)], fill=col)
    d.rectangle((0, y0 + h * 0.18, w, h), fill=pal["hill_near"])


def _city(d, w, h, pal, rng, y0):
    x = -w * 0.05
    while x < w * 1.05:
        bw = w * (0.06 + rng.random() * 0.07)
        bh = h * (0.10 + rng.random() * 0.22)
        top = y0 - bh
        col = _mix(pal["hill_far"], pal["hill_near"], rng.random())
        d.rectangle((x, top, x + bw, y0 + h * 0.2), fill=col)
        d.rectangle((x, top, x + bw, top + max(2, int(h * 0.006))), fill=pal["foam"])
        for wy in range(int(top + h * 0.02), int(y0), int(h * 0.035)):
            for wx in range(int(x + bw * 0.15), int(x + bw * 0.85), int(bw * 0.3)):
                if rng.random() > 0.45:
                    d.rectangle((wx, wy, wx + int(bw * 0.12), wy + int(h * 0.014)),
                                fill=pal["glow"])
        x += bw * 1.06


def _clouds(img, w, h, pal, rng, count=7):
    for _ in range(count):
        cx = rng.uniform(0, w); cy = rng.uniform(h * 0.05, h * 0.42)
        cw = w * rng.uniform(0.10, 0.26); ch = cw * rng.uniform(0.22, 0.36)
        col = _rgba(pal["foam"], rng.randint(45, 110))
        layer = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        ld = ImageDraw.Draw(layer)
        ld.ellipse((cx - cw/2, cy - ch/2, cx + cw*0.1, cy + ch/2), fill=col)
        ld.ellipse((cx - cw*0.1, cy - ch, cx + cw*0.5, cy + ch*0.6), fill=col)
        ld.ellipse((cx + cw*0.15, cy - ch*0.4, cx + cw/2, cy + ch*0.5), fill=col)
        layer = layer.filter(ImageFilter.GaussianBlur(int(w * 0.006)))
        img.alpha_composite(layer)


def _stars(d, w, h, pal, rng, count=60):
    for _ in range(count):
        x, y = rng.uniform(0, w), rng.uniform(0, h * 0.6)
        r = w * rng.uniform(0.0015, 0.005)
        a = rng.randint(120, 255)
        d.ellipse((x-r, y-r, x+r, y+r), fill=_rgba(pal["foam"], a))
        if r > w * 0.003:
            d.line((x-r*3, y, x+r*3, y), fill=_rgba(pal["foam"], a//2), width=1)
            d.line((x, y-r*3, x, y+r*3), fill=_rgba(pal["foam"], a//2), width=1)


def _disk(d, w, h, pal, cx, cy, r, color=None, ring=True):
    color = color or pal["accent"]
    d.ellipse((cx-r, cy-r, cx+r, cy+r), fill=color)
    if ring:
        d.ellipse((cx-r*1.12, cy-r*1.12, cx+r*1.12, cy+r*1.12),
                  outline=_rgba(pal["foam"], 110), width=max(2, int(w*0.003)))


def _petals(d, w, h, pal, rng, count=26):
    for _ in range(count):
        x, y = rng.uniform(0, w), rng.uniform(0, h)
        s = w * rng.uniform(0.005, 0.013)
        a = rng.uniform(0, math.pi)
        d.ellipse((x-s, y-s*0.5, x+s, y+s*0.5),
                  fill=_rgba(pal["accent"], rng.randint(90, 190)), outline=None)


def _birds(d, w, h, pal, rng, count=5):
    for _ in range(count):
        x, y = rng.uniform(w*0.1, w*0.9), rng.uniform(h*0.06, h*0.30)
        s = w * rng.uniform(0.008, 0.018)
        d.arc((x-s, y-s*0.5, x, y+s*0.3), 200, 340,
              fill=pal["ink"], width=max(1, int(w*0.002)))
        d.arc((x, y-s*0.5, x+s, y+s*0.3), 200, 340,
              fill=pal["ink"], width=max(1, int(w*0.002)))


def _foreground(d, w, h, pal, rng, style):
    """Break up the lower third so it never reads as a flat empty template."""
    if style == "ukiyo-e":
        for i in range(10):
            y = h * (0.76 + i * 0.024)
            amp = h * 0.011
            pts = [(x, y + math.sin(x / w * math.pi * 6 + i) * amp)
                   for x in range(0, w + 20, 14)]
            d.line(pts, fill=_rgba(pal["foam"], 55 + i * 7),
                   width=max(1, int(w * 0.002)))
        for _ in range(60):
            x, y = rng.uniform(0, w), rng.uniform(h * 0.74, h)
            r = w * rng.uniform(0.002, 0.006)
            d.ellipse((x-r, y-r, x+r, y+r),
                      fill=_rgba(pal["foam"], rng.randint(35, 110)))
    else:
        for _ in range(55):
            x, y = rng.uniform(0, w), rng.uniform(h * 0.72, h)
            rw = w * rng.uniform(0.008, 0.026)
            rh = rw * rng.uniform(0.35, 0.8)
            col = _mix(pal["ground"], pal["hill_near"], rng.random() * 0.55)
            d.ellipse((x-rw, y-rh, x+rw, y+rh), fill=col)
        for _ in range(35):
            x, y = rng.uniform(0, w), rng.uniform(h * 0.70, h * 0.95)
            gh = h * rng.uniform(0.008, 0.026)
            d.line((x, y, x + rng.uniform(-w*.012, w*.012), y - gh),
                   fill=_rgba(pal["hill_near"], 110), width=max(1, int(w*0.003)))


# ---------------------------------------------------------------------------
# Prop painter - recognizable objects tied to the story
# ---------------------------------------------------------------------------
def draw_prop(d, name, cx, cy, size, pal):
    s = size
    ink = pal["ink"]
    if name == "jar":
        d.ellipse((cx-s*.5, cy-s*.35, cx+s*.5, cy+s*.55), fill=pal["accent"])
        d.rectangle((cx-s*.45, cy, cx+s*.45, cy+s*.5), fill=pal["accent"])
        d.ellipse((cx-s*.45, cy-s*.45, cx+s*.45, cy-s*.1), fill=pal["foam"])
        d.rectangle((cx-s*.5, cy-s*.2, cx+s*.5, cy-s*.05), fill=ink)
        d.arc((cx-s*.3, cy-s*.3, cx-s*.1, cy+s*.3), 100, 260, fill=pal["foam"], width=max(1,int(s*.05)))
    elif name == "key":
        d.ellipse((cx-s*.55, cy-s*.55, cx-s*.05, cy-s*.05), outline=ink, width=max(2,int(s*.10)))
        d.line((cx-s*.1, cy-s*.1, cx+s*.5, cy+s*.5), fill=ink, width=max(3,int(s*.13)))
        d.line((cx+s*.25, cy+s*.25, cx+s*.45, cy+s*.05), fill=ink, width=max(2,int(s*.10)))
    elif name == "coin":
        d.ellipse((cx-s*.5, cy-s*.5, cx+s*.5, cy+s*.5), fill="#D9A441", outline=ink, width=max(2,int(s*.05)))
        d.ellipse((cx-s*.35, cy-s*.35, cx+s*.35, cy+s*.35), outline=ink, width=max(1,int(s*.03)))
    elif name == "compass":
        d.ellipse((cx-s*.5, cy-s*.5, cx+s*.5, cy+s*.5), fill=pal["foam"], outline=ink, width=max(2,int(s*.05)))
        d.polygon([(cx,cy-s*.35),(cx+s*.13,cy),(cx,cy+s*.35),(cx-s*.13,cy)], fill=pal["accent"])
        d.line((cx,cy-s*.5,cx,cy-s*.35), fill=ink, width=2)
    elif name == "book":
        d.rectangle((cx-s*.55, cy-s*.38, cx, cy+s*.42), fill=pal["foam"], outline=ink, width=2)
        d.rectangle((cx, cy-s*.38, cx+s*.55, cy+s*.42), fill=pal["paper"], outline=ink, width=2)
        d.line((cx, cy-s*.38, cx, cy+s*.42), fill=ink, width=max(2,int(s*.04)))
        for i in range(3):
            yy = cy-s*.2+i*s*.18
            d.line((cx-s*.42,yy,cx-s*.08,yy), fill=ink, width=1)
            d.line((cx+s*.08,yy,cx+s*.42,yy), fill=ink, width=1)
    elif name == "clock":
        d.ellipse((cx-s*.5,cy-s*.5,cx+s*.5,cy+s*.5), fill=pal["foam"], outline=ink, width=max(2,int(s*.05)))
        d.line((cx,cy,cx,cy-s*.32), fill=ink, width=max(2,int(s*.05)))
        d.line((cx,cy,cx+s*.26,cy+s*.1), fill=ink, width=max(2,int(s*.05)))
        d.ellipse((cx-s*.04,cy-s*.04,cx+s*.04,cy+s*.04), fill=ink)
    elif name == "bottle":
        d.rectangle((cx-s*.22,cy-s*.1,cx+s*.22,cy+s*.5), fill=pal["accent"], outline=ink, width=2)
        d.rectangle((cx-s*.09,cy-s*.45,cx+s*.09,cy-s*.1), fill=pal["accent"], outline=ink, width=2)
        d.rectangle((cx-s*.12,cy-s*.5,cx+s*.12,cy-s*.42), fill=ink)
        d.line((cx-s*.14,cy+s*.05,cx-s*.14,cy+s*.35), fill=pal["foam"], width=max(1,int(s*.04)))
    elif name == "fish":
        d.ellipse((cx-s*.45,cy-s*.25,cx+s*.35,cy+s*.25), fill=pal["accent"], outline=ink, width=2)
        d.polygon([(cx+s*.3,cy),(cx+s*.55,cy-s*.25),(cx+s*.55,cy+s*.25)], fill=pal["accent"])
        d.ellipse((cx-s*.28,cy-s*.08,cx-s*.18,cy+s*.02), fill=ink)
    elif name == "bird":
        d.ellipse((cx-s*.35,cy-s*.2,cx+s*.25,cy+s*.2), fill=pal["foam"], outline=ink, width=2)
        d.polygon([(cx+s*.2,cy),(cx+s*.5,cy-s*.12),(cx+s*.2,cy+s*.12)], fill=pal["accent"])
        d.ellipse((cx-s*.22,cy-s*.08,cx-s*.12,cy+s*.02), fill=ink)
    elif name == "moon":
        d.ellipse((cx-s*.5,cy-s*.5,cx+s*.5,cy+s*.5), fill=pal["foam"])
        d.ellipse((cx-s*.2,cy-s*.35,cx+s*.35,cy+s*.25), fill=pal["sky_bottom"])
    elif name == "star":
        pts=[]
        for i in range(10):
            a=-math.pi/2+i*math.pi/5
            r=s*.5 if i%2==0 else s*.2
            pts.append((cx+math.cos(a)*r, cy+math.sin(a)*r))
        d.polygon(pts, fill="#D9A441", outline=ink, width=2)
    elif name == "door":
        d.rectangle((cx-s*.4,cy-s*.55,cx+s*.4,cy+s*.55), fill=pal["accent"], outline=ink, width=3)
        d.rectangle((cx-s*.3,cy-s*.45,cx+s*.3,cy+s*.3), outline=ink, width=2)
        d.ellipse((cx+s*.18,cy,cx+s*.25,cy+s*.07), fill=ink)
    elif name == "chest":
        d.rectangle((cx-s*.5,cy-s*.1,cx+s*.5,cy+s*.45), fill="#8C5A34", outline=ink, width=2)
        d.pieslice((cx-s*.5,cy-s*.5,cx+s*.5,cy+s*.1), 180, 360, fill="#A66C3E", outline=ink, width=2)
        d.rectangle((cx-s*.08,cy-s*.1,cx+s*.08,cy+s*.2), fill="#D9A441", outline=ink, width=2)
    elif name == "map":
        d.polygon([(cx-s*.55,cy-s*.35),(cx+s*.55,cy-s*.45),(cx+s*.5,cy+s*.4),(cx-s*.5,cy+s*.35)],
                  fill=pal["foam"], outline=ink, width=2)
        d.line((cx-s*.55,cy-s*.35,cx+s*.5,cy+s*.4), fill=pal["hill_far"], width=2)
        d.line((cx+s*.55,cy-s*.45,cx-s*.5,cy+s*.35), fill=pal["hill_far"], width=2)
    elif name == "flower":
        for i in range(6):
            a=i*math.pi/3
            d.ellipse((cx+math.cos(a)*s*.28-s*.16, cy+math.sin(a)*s*.28-s*.16,
                       cx+math.cos(a)*s*.28+s*.16, cy+math.sin(a)*s*.28+s*.16),
                      fill=pal["accent"])
        d.ellipse((cx-s*.14,cy-s*.14,cx+s*.14,cy+s*.14), fill="#D9A441", outline=ink, width=2)
    elif name == "ship":
        d.polygon([(cx-s*.55,cy+s*.1),(cx+s*.55,cy+s*.1),(cx+s*.35,cy+s*.4),(cx-s*.35,cy+s*.4)],
                  fill="#8C5A34", outline=ink, width=2)
        d.line((cx,cy+s*.1,cx,cy-s*.6), fill=ink, width=max(2,int(s*.05)))
        d.polygon([(cx,cy-s*.58),(cx+s*.45,cy-s*.1),(cx,cy-s*.1)], fill=pal["foam"], outline=ink, width=2)
    elif name == "lantern":
        d.rectangle((cx-s*.2,cy-s*.35,cx+s*.2,cy+s*.35), fill="#D9A441", outline=ink, width=2)
        d.line((cx,cy-s*.35,cx,cy-s*.55), fill=ink, width=2)
        d.rectangle((cx-s*.25,cy-s*.4,cx+s*.25,cy-s*.32), fill=ink)
        d.rectangle((cx-s*.25,cy+s*.32,cx+s*.25,cy+s*.4), fill=ink)
    elif name == "egg":
        d.ellipse((cx-s*.35,cy-s*.5,cx+s*.35,cy+s*.5), fill=pal["foam"], outline=ink, width=2)
    elif name == "apple":
        d.ellipse((cx-s*.42,cy-s*.3,cx+s*.42,cy+s*.5), fill=pal["accent"], outline=ink, width=2)
        d.line((cx,cy-s*.3,cx+s*.05,cy-s*.55), fill=ink, width=3)
        d.ellipse((cx+s*.05,cy-s*.6,cx+s*.3,cy-s*.4), fill=pal["hill_far"])
    elif name == "phone":
        d.rounded_rectangle((cx-s*.28,cy-s*.5,cx+s*.28,cy+s*.5), radius=int(s*.08),
                            fill=ink, outline=ink, width=2)
        d.rounded_rectangle((cx-s*.22,cy-s*.42,cx+s*.22,cy+s*.4), radius=int(s*.04),
                            fill=pal["sky_bottom"])
        d.ellipse((cx-s*.05,cy+s*.42,cx+s*.05,cy+s*.47), fill=pal["foam"])
    else:  # generic glowing orb
        d.ellipse((cx-s*.4,cy-s*.4,cx+s*.4,cy+s*.4), fill=pal["accent"])
        d.ellipse((cx-s*.15,cy-s*.15,cx+s*.15,cy+s*.15), fill=pal["foam"])


# ---------------------------------------------------------------------------
# Scene composer
# ---------------------------------------------------------------------------
def compose_scene(spec, w, h, mascot_img=None, index=0):
    """Return a richly illustrated RGB frame for one story beat."""
    style = spec.get("style", "claymation")
    if style not in PALETTES:
        style = "claymation"
    pal = PALETTES[style]
    motif = spec.get("motif", "sky")
    if motif not in MOTIFS:
        motif = "sky"
    props = [p for p in spec.get("props", []) if p in PROPS][:2]
    mood = spec.get("mood", "curious")
    seed = _seed(style, motif, spec.get("caption", ""), index)
    rng = random.Random(seed)

    # base sky
    if motif == "space" or (motif == "night") or mood in ("mystery", "spooky"):
        top, bottom = "#101A33", "#33405E" if style == "ukiyo-e" else "#2C3556"
    else:
        top, bottom = pal["sky_top"], pal["sky_bottom"]
    img = _gradient(w, h, top, bottom).convert("RGBA")
    d = ImageDraw.Draw(img)

    # celestial body
    if motif in ("night", "space", "ocean"):
        _disk(d, w, h, pal, w * 0.72, h * 0.18, w * 0.075,
              color=pal["foam"] if motif != "ocean" else pal["accent"])

    if style == "ukiyo-e":
        _stars(d, w, h, pal, rng, 40) if motif in ("space", "night") else _birds(d, w, h, pal, rng, 5)
        if motif in ("ocean", "river"):
            _waves(d, w, h, pal, rng, h * 0.42, layers=5)
        elif motif in ("mountains", "forest"):
            _mountains(d, w, h, pal, rng, h * 0.50)
            if motif == "forest":
                _forest(d, w, h, pal, rng, h * 0.52)
        elif motif == "city":
            _city(d, w, h, pal, rng, h * 0.62)
        else:
            _clouds(img, w, h, pal, rng, 6)
            d = ImageDraw.Draw(img)
            d.rectangle((0, h * 0.72, w, h), fill=pal["ground"])
        _petals(d, w, h, pal, rng, 22)
    else:  # claymation
        # soft parallax hills
        for j, (col, y) in enumerate([(pal["hill_far"], 0.52), (pal["hill_near"], 0.64)]):
            pts = [(0, h)]
            for x in range(0, w + 40, 30):
                yy = h * y + math.sin(x / w * math.pi * 2 + j * 1.7) * h * 0.035
                pts.append((x, yy))
            pts.append((w, h))
            d.polygon(pts, fill=col)
        if motif in ("ocean", "river"):
            d.rectangle((0, h * 0.66, w, h), fill=_mix(pal["sky_bottom"], pal["hill_near"], .5))
            for i in range(6):
                y = h * (0.70 + i * 0.045)
                d.arc((w*0.1, y-h*0.02, w*0.9, y+h*0.02), 10, 170,
                      fill=_rgba(pal["foam"], 120), width=max(2, int(w*0.003)))
        elif motif == "city":
            _city(d, w, h, pal, rng, h * 0.66)
        elif motif in ("mountains", "forest"):
            _mountains(d, w, h, pal, rng, h * 0.58)
        if motif in ("sky", "night", "space"):
            _stars(d, w, h, pal, rng, 50)
        _clouds(img, w, h, pal, rng, 5)

    # foreground texture so the lower third is never a flat empty block
    d = ImageDraw.Draw(img)
    _foreground(d, w, h, pal, rng, style)

    # props float in the mid-ground with a soft shadow
    if props:
        positions = [(w * 0.24, h * 0.40), (w * 0.76, h * 0.46)]
        for p, (px, py) in zip(props, positions):
            ps = w * 0.13
            _soft_shadow(img, (px-ps*.6, py+ps*.5, px+ps*.6, py+ps*.75), int(w*0.02), 70)
            d = ImageDraw.Draw(img)
            draw_prop(d, p, px, py, ps, pal)

    # mascot host with drop shadow + warm rim light
    if mascot_img is not None:
        m = mascot_img.copy().convert("RGBA")
        mw = int(min(w, h) * 0.40)
        m = m.resize((mw, mw), Image.Resampling.LANCZOS)
        if w > h:
            mx, my = int(w - mw - w*0.05), int(h - mw - h*0.02)
        else:
            mx, my = int((w - mw) / 2), int(h * 0.55)
        _soft_shadow(img, (mx+mw*.1, my+mw*.88, mx+mw*.9, my+mw*1.02),
                     int(w*0.02), 110)
        rim = Image.new("RGBA", img.size, (0, 0, 0, 0))
        rim.paste(Image.new("RGBA", m.size, _rgba(pal["glow"], 90)),
                  (mx+int(w*.004), my-int(w*.004)), m.getchannel("A"))
        rim = rim.filter(ImageFilter.GaussianBlur(int(w*0.006)))
        img.alpha_composite(rim)
        img.alpha_composite(m, (mx, my))

    # film grain + vignette for a tactile, finished look
    grain = Image.effect_noise((w, h), 14).convert("L").convert("RGBA")
    grain.putalpha(26)
    img.alpha_composite(grain)
    vig = Image.new("L", (w, h), 0)
    vd = ImageDraw.Draw(vig)
    vd.ellipse((-w*0.25, -h*0.25, w*1.25, h*1.25), fill=255)
    vig = vig.filter(ImageFilter.GaussianBlur(int(min(w, h)*0.12)))
    dark = Image.new("RGBA", (w, h), (12, 10, 8, 0))
    dark.putalpha(Image.eval(vig, lambda v: int((255 - v) * 0.38)))
    img.alpha_composite(dark)

    return img.convert("RGB")
