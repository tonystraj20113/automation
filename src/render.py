"""Rich frame composition + ffmpeg encoding.

Every beat gets its own illustrated scene (see scenes.py) with the clay-cat
host, story props, tactile texture and burned-in typography. A gentle Ken
Burns move per beat keeps frames from feeling like a slideshow.
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
        import cairosvg  # fallback (needs libcairo on Linux)
        cairosvg.svg2png(url=str(svg), write_to=str(out), output_width=width)
    return out


def _auto_spec(caption, style, index):
    text = caption.lower()
    motif = "sky"
    groups = {
        "ocean": ("ocean", "sea", "wave", "ship", "fish", "water", "drown", "island"),
        "river": ("river", "stream", "lake", "flood"),
        "mountains": ("mountain", "cliff", "snow", "volcano", "peak"),
        "forest": ("forest", "tree", "wood", "jungle", "leaf"),
        "city": ("city", "street", "building", "town", "house", "train", "rail"),
        "space": ("space", "planet", "star", "moon", "rocket", "orbit", "galaxy"),
        "night": ("night", "dark", "midnight", "shadow", "dream"),
        "desert": ("desert", "sand", "dune", "cactus", "pyramid"),
        "room": ("room", "door", "window", "bed", "table", "key"),
    }
    for name, keys in groups.items():
        if any(k in text for k in keys):
            motif = name
            break
    props = [p for p in scenes.PROPS if p in text.split() or p in text][:2]
    mood = "curious"
    if any(k in text for k in ("strange", "weird", "mystery", "vanish", "secret")):
        mood = "mystery"
    elif any(k in text for k in ("scared", "dark", "ghost", "haunt")):
        mood = "spooky"
    elif any(k in text for k in ("laugh", "funny", "silly", "oops")):
        mood = "playful"
    return {"style": style, "motif": motif, "props": props, "mood": mood,
            "caption": caption, "index": index}


def _overlay(img, caption, title, index, total):
    """Brand, title, caption card and progress - all fixed while art moves."""
    w, h = img.size
    s = min(w, h)
    img = img.convert("RGBA")
    d = ImageDraw.Draw(img)

    # brand chip
    bw = int(s * 0.26)
    d.rounded_rectangle((int(s*.035), int(s*.035), int(s*.035)+bw, int(s*.035)+int(s*.075)),
                        radius=int(s*.02), fill=(20, 16, 14, 150))
    d.text((int(s*.055), int(s*.045)), "STORYFACTS",
           font=font(int(s*.032)), fill=(255, 246, 230, 255))

    # episode title on the opening beat
    if title and index == 0:
        tf = font(int(s * 0.072))
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
            tw = box[2] - box[0]
            x = (w - tw) // 2
            d.text((x+int(s*.005), y+int(s*.005)), line, font=tf, fill=(0, 0, 0, 150))
            d.text((x, y), line, font=tf, fill=(255, 250, 240, 255))
            y += int(s * 0.085)

    # caption card, lower third
    cf = font(int(s * 0.062))
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
    lh = int(s * 0.085)
    card_h = lh * len(lines) + int(s * 0.05)
    card_y = h - card_h - int(s * 0.09)
    d.rounded_rectangle((int(s*.06), card_y, w - int(s*.06), card_y + card_h),
                        radius=int(s*.028), fill=(18, 15, 13, 220))
    d.rounded_rectangle((int(s*.06), card_y, int(s*.075), card_y + card_h),
                        radius=int(s*.008), fill=(217, 164, 65, 255))
    ty = card_y + int(s*.025)
    for line in lines:
        box = d.textbbox((0, 0), line, font=cf)
        tw = box[2] - box[0]
        d.text(((w - tw)//2, ty), line, font=cf, fill=(255, 252, 245, 255))
        ty += lh

    # progress dots
    dot_r = max(3, int(s * 0.007))
    gap = dot_r * 3
    total = max(1, total)
    start_x = (w - gap * (total - 1)) // 2
    py = int(s * 0.055)
    for i in range(total):
        x = start_x + i * gap
        col = (217, 164, 65, 255) if i <= index else (255, 255, 255, 90)
        d.ellipse((x-dot_r, py-dot_r, x+dot_r, py+dot_r), fill=col)

    return img.convert("RGB")


def _ken_burns(base, zoom, dx, dy, w, h):
    iw, ih = base.size
    nw, nh = int(iw * zoom), int(ih * zoom)
    scaled = base.resize((nw, nh), Image.Resampling.LANCZOS)
    left = max(0, min(nw - w, int((nw - w) / 2 + dx * w)))
    top = max(0, min(nh - h, int((nh - h) / 2 + dy * h)))
    return scaled.crop((left, top, left + w, top + h))


def scene(caption, style, index, out_path, w=1080, h=1920,
          spec=None, title=None, total=1, mascot=None):
    spec = spec or _auto_spec(caption, style, index)
    spec = dict(spec)
    spec["style"] = style
    spec["caption"] = caption
    spec["index"] = index
    base = scenes.compose_scene(spec, w, h, mascot_img=mascot)
    framed = _overlay(base, caption, title, index, total)
    out_path = Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    framed.save(out_path)
    return out_path


def render_video(captions, audio, srt, out_path, style="claymation",
                 w=1080, h=1920, title=None, specs=None):
    from .tts import duration
    frames_dir = ROOT / "output" / "frames"
    frames_dir.mkdir(parents=True, exist_ok=True)
    for f in frames_dir.glob("*.png"):
        f.unlink()

    mascot = Image.open(mascot_png()).convert("RGBA")
    total = len(captions)
    step = duration(audio) / max(1, total)
    subframes = 3
    entries = []
    n = 0
    for i, cap in enumerate(captions):
        spec = specs[i] if specs and i < len(specs) else None
        base_spec = spec or _auto_spec(cap, style, i)
        base = scenes.compose_scene(base_spec, w, h, mascot_img=mascot)
        for j in range(subframes):
            t = j / max(1, subframes - 1)
            moved = _ken_burns(base, 1.0 + 0.035 * t, (t - 0.5) * 0.05,
                               (0.5 - t) * 0.04, w, h)
            framed = _overlay(moved, cap, title, i, total)
            p = frames_dir / f"frame_{n:04d}.png"
            framed.save(p)
            entries.append((p, step / subframes))
            n += 1

    listfile = frames_dir / "concat.txt"
    listfile.write_text(
        "".join(f"file '{p.as_posix()}'\nduration {d:.4f}\n" for p, d in entries)
        + f"file '{entries[-1][0].as_posix()}'\n",
        encoding="utf-8",
    )
    out_path = Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    cmd = [
        "ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", str(listfile),
        "-i", str(audio),
        "-c:v", "libx264", "-preset", "veryfast", "-crf", "22",
        "-pix_fmt", "yuv420p", "-r", "24", "-c:a", "aac", "-b:a", "128k",
        "-shortest", str(out_path),
    ]
    subprocess.run(cmd, check=True)
    return out_path
