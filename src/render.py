"""Rich frame composition + ffmpeg encoding.

Competitor study (2026-11): Gneef cuts a new shot every ~1.2s; Ricks Clips
uses near-continuous dramatic camera movement instead of hard cuts. This
renderer combines both: a strong move per beat, fast cut flashes between
beats, animated art layers, and speech-synced captions.
"""
import subprocess
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

from .utils import ROOT, load_config
from . import scenes

FONT_CANDIDATES = [
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    "C:/Windows/Fonts/arialbd.ttf",
    "/usr/share/fonts/truetype/liberation2/LiberationSans-Bold.ttf",
]

# (start_zoom, end_zoom, pan_x, pan_y) - rotated through so consecutive beats
# never repeat the same move.
MOVES = [
    (1.00, 1.16, -0.07, 0.00),   # push in, drift left
    (1.14, 1.00, 0.06, 0.02),    # pull out, drift right
    (1.00, 1.10, 0.00, -0.06),   # tilt up
    (1.10, 1.00, 0.00, 0.06),    # tilt down
    (1.04, 1.22, -0.09, 0.03),   # dramatic push
    (1.18, 1.00, 0.08, -0.02),   # dramatic pull
]


def font(size):
    for p in FONT_CANDIDATES:
        if Path(p).exists():
            return ImageFont.truetype(p, size)
    return ImageFont.load_default()


def mascot_png(width=640):
    """Rasterize the locked SVG mascot. resvg-py needs no system libraries."""
    svg = ROOT / "assets" / "mascot.svg"
    out = ROOT / "output" / "mascot.png"
    out.parent.mkdir(parents=True, exist_ok=True)
    try:
        import resvg_py
        out.write_bytes(resvg_py.svg_to_bytes(svg_path=str(svg), width=width))
    except Exception:
        import cairosvg
        cairosvg.svg2png(url=str(svg), write_to=str(out), output_width=width)
    return out


def _auto_spec(caption, style, index):
    text = caption.lower()
    motif = "sky"
    groups = {
        "ocean": ("ocean", "sea", "wave", "ship", "fish", "water", "drown", "island", "lighthouse"),
        "river": ("river", "stream", "lake", "flood"),
        "mountains": ("mountain", "cliff", "snow", "volcano", "peak", "rock"),
        "forest": ("forest", "tree", "wood", "jungle", "leaf"),
        "city": ("city", "street", "building", "town", "house", "train", "rail", "carnival"),
        "space": ("space", "planet", "star", "moon", "rocket", "orbit", "galaxy"),
        "night": ("night", "dark", "midnight", "shadow", "dream", "lamp"),
        "desert": ("desert", "sand", "dune", "cactus", "pyramid"),
        "room": ("room", "door", "window", "bed", "table", "key", "clock", "logbook"),
    }
    for name, keys in groups.items():
        if any(k in text for k in keys):
            motif = name
            break
    props = [p for p in scenes.PROPS if p in text][:2]
    mood = "curious"
    if any(k in text for k in ("strange", "weird", "mystery", "vanish", "secret", "gone")):
        mood = "mystery"
    elif any(k in text for k in ("scared", "dark", "ghost", "haunt", "empty", "wave")):
        mood = "spooky"
    elif any(k in text for k in ("laugh", "funny", "silly", "oops")):
        mood = "playful"
    return {"style": style, "motif": motif, "props": props, "mood": mood,
            "caption": caption, "index": index}


def _overlay(img, caption, title, index, total, appear=1.0):
    w, h = img.size
    s = min(w, h)
    img = img.convert("RGBA")
    d = ImageDraw.Draw(img)

    def A(v):
        return int(v * max(0.0, min(1.0, appear)))

    bw = int(s * 0.26)
    d.rounded_rectangle((int(s*.035), int(s*.035), int(s*.035)+bw, int(s*.035)+int(s*.075)),
                        radius=int(s*.02), fill=(20, 16, 14, A(150)))
    d.text((int(s*.055), int(s*.045)), "STORYFACTS",
           font=font(int(s*.032)), fill=(255, 246, 230, A(255)))

    if title and index == 0:
        tf = font(int(s * 0.066))
        max_w = w - int(s * 0.16)
        words, lines, cur = title.split(), [], ""
        for word in words:
            trial = (cur + " " + word).strip()
            if d.textbbox((0, 0), trial, font=tf)[2] > max_w and cur:
                lines.append(cur); cur = word
            else:
                cur = trial
        if cur:
            lines.append(cur)
        y = int(h * 0.10)
        for line in lines:
            box = d.textbbox((0, 0), line, font=tf)
            x = (w - (box[2] - box[0])) // 2
            d.text((x+int(s*.005), y+int(s*.005)), line, font=tf, fill=(0, 0, 0, A(160)))
            d.text((x, y), line, font=tf, fill=(255, 250, 240, A(255)))
            y += int(s * 0.078)

    cf = font(int(s * 0.058))
    max_w = w - int(s * 0.16)
    words, lines, cur = caption.split(), [], ""
    for word in words:
        trial = (cur + " " + word).strip()
        if d.textbbox((0, 0), trial, font=cf)[2] > max_w and cur:
            lines.append(cur); cur = word
        else:
            cur = trial
    if cur:
        lines.append(cur)
    lh = int(s * 0.078)
    card_h = lh * len(lines) + int(s * 0.05)
    card_y = h - card_h - int(s * 0.09)
    d.rounded_rectangle((int(s*.06), card_y, w - int(s*.06), card_y + card_h),
                        radius=int(s*.028), fill=(18, 15, 13, A(225)))
    d.rounded_rectangle((int(s*.06), card_y, int(s*.075), card_y + card_h),
                        radius=int(s*.008), fill=(217, 164, 65, A(255)))
    ty = card_y + int(s*.025)
    for line in lines:
        box = d.textbbox((0, 0), line, font=cf)
        d.text(((w - (box[2]-box[0]))//2, ty), line, font=cf,
               fill=(255, 252, 245, A(255)))
        ty += lh

    d.text((int(s * 0.06), h - int(s * 0.055)), "TRUE STORIES, TOLD SMALL",
           font=font(int(s * 0.022)), fill=(255, 250, 240, A(130)))

    dot_r = max(3, int(s * 0.007))
    gap = dot_r * 3
    start_x = (w - gap * (max(1, total) - 1)) // 2
    py = int(s * 0.055)
    for i in range(max(1, total)):
        x = start_x + i * gap
        col = (217, 164, 65, A(255)) if i <= index else (255, 255, 255, A(90))
        d.ellipse((x-dot_r, py-dot_r, x+dot_r, py+dot_r), fill=col)
    return img.convert("RGB")


def _ken_burns(base, z0, z1, px, py, t, w, h):
    zoom = z0 + (z1 - z0) * t
    iw, ih = base.size
    nw, nh = int(iw * zoom), int(ih * zoom)
    scaled = base.resize((nw, nh), Image.Resampling.LANCZOS)
    left = max(0, min(nw - w, int((nw - w) / 2 + px * w * t)))
    top = max(0, min(nh - h, int((nh - h) / 2 + py * h * t)))
    return scaled.crop((left, top, left + w, top + h))


def scene(caption, style, index, out_path, w=1080, h=1920,
          spec=None, title=None, total=1, mascot=None, phase=0.0):
    spec = dict(spec or {})
    spec["style"] = style
    spec["caption"] = caption
    spec["index"] = index
    base = scenes.compose_scene(spec, w, h, mascot_img=mascot, phase=phase)
    framed = _overlay(base, caption, title, index, total)
    out_path = Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    framed.save(out_path)
    return out_path


def render_video(captions, audio, srt, out_path, style="claymation",
                 w=1080, h=1920, title=None, specs=None, durations=None,
                 subframes=8, sfx=False):
    frames_dir = ROOT / "output" / "frames"
    frames_dir.mkdir(parents=True, exist_ok=True)
    for f in frames_dir.glob("*.png"):
        f.unlink()

    total = len(captions)
    from .tts import duration
    audio_dur = duration(audio)
    if not durations or len(durations) != total:
        durations = [audio_dur / max(1, total)] * total

    mascot = Image.open(mascot_png()).convert("RGBA")
    entries = []
    n = 0
    for i, cap in enumerate(captions):
        spec = dict(specs[i]) if specs and i < len(specs) else {}
        spec = dict(spec, style=style, caption=cap, index=i) if spec else _auto_spec(cap, style, i)
        z0, z1, px, py = MOVES[i % len(MOVES)]
        scene_dur = durations[i]
        for j in range(subframes):
            t = j / max(1, subframes - 1)
            base = scenes.compose_scene(spec, w, h, mascot_img=mascot, phase=t)
            moved = _ken_burns(base, z0, z1, px, py, t, w, h)
            appear = min(1.0, 0.25 + j * 0.75)
            framed = _overlay(moved, cap, title, i, total, appear=appear)
            # fast cut flash on the first frame of every beat after the first
            if sfx and j == 0 and i > 0:
                flash = Image.new("RGBA", (w, h), (255, 244, 220, 70))
                framed = Image.alpha_composite(framed.convert("RGBA"), flash).convert("RGB")
            p = frames_dir / f"frame_{n:04d}.png"
            framed.save(p)
            entries.append((p, scene_dur / subframes))
            n += 1

    listfile = frames_dir / "concat.txt"
    listfile.write_text(
        "".join(f"file '{p.as_posix()}'\nduration {d:.4f}\n" for p, d in entries)
        + f"file '{entries[-1][0].as_posix()}'\n", encoding="utf-8")

    out_path = Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    cmd = ["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", str(listfile),
           "-i", str(audio),
           "-c:v", "libx264", "-preset", "veryfast", "-crf", "22",
           "-pix_fmt", "yuv420p", "-r", "30", "-c:a", "aac", "-b:a", "128k",
           "-shortest", str(out_path)]
    subprocess.run(cmd, check=True, capture_output=True)
    return out_path
