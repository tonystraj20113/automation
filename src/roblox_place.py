"""Build a bright, blocky toy world and hand its exact part list to the renderer.

Roblox Studio still runs headlessly in GitHub Actions with --task RunScript.
When the runner's GUI session makes Studio hang, the same deterministic part
list is used directly, so the look never depends on a screenshot from Studio.
All art is original primitives: no Roblox branding, logos or assets.
"""
import json, os, re, subprocess
from pathlib import Path

from .utils import ROOT, write_json

BASE = ROOT / "studio"

# Bright toy-shop colours. Mood only nudges the palette; nothing is dark/muddy.
PALETTES = {
    "curious":  {"ground": "#8ce0c0", "wall": "#d9f4ff", "block": "#ff8a72", "accent": "#ffd166", "dark": "#2b3a55"},
    "mystery":  {"ground": "#7bdff2", "wall": "#d8ddff", "block": "#9b8cff", "accent": "#ffe066", "dark": "#2b2d5a"},
    "spooky":   {"ground": "#b8a9e8", "wall": "#eadcff", "block": "#ff7a9c", "accent": "#ffd166", "dark": "#392b57"},
    "playful":  {"ground": "#8ce0c0", "wall": "#ffe6a7", "block": "#ff6f91", "accent": "#4cc9f0", "dark": "#2b3a55"},
    "street":   {"ground": "#8ee6bc", "wall": "#d7f0ff", "block": "#ff8a72", "accent": "#ffd166", "dark": "#2b3a55"},
    "room":     {"ground": "#f1dcb0", "wall": "#d9f0ff", "block": "#8b5e3c", "accent": "#ffd166", "dark": "#2b3a55"},
    "forest":   {"ground": "#8ee6bc", "wall": "#d8f5d0", "block": "#3fb27f", "accent": "#ffd166", "dark": "#1f4d3d"},
    "ocean":    {"ground": "#8ed8ff", "wall": "#dff3ff", "block": "#4cc9f0", "accent": "#ffd166", "dark": "#1f4d6d"},
    "sky":      {"ground": "#9bb7ff", "wall": "#e6ecff", "block": "#7b9cff", "accent": "#ffe066", "dark": "#2b3a55"},
    "night":    {"ground": "#8fa8e8", "wall": "#d5dfff", "block": "#6c77c9", "accent": "#ffe066", "dark": "#2b2d5a"},
    "city":     {"ground": "#b8d8e8", "wall": "#e8f4ff", "block": "#ff8fab", "accent": "#ffd166", "dark": "#2b3a55"},
    "desert":   {"ground": "#f4d39b", "wall": "#ffe8bf", "block": "#e07a5f", "accent": "#3d405b", "dark": "#5a3d2b"},
    "river":    {"ground": "#8ed8f5", "wall": "#dff5ff", "block": "#8ce0c0", "accent": "#ffd166", "dark": "#1f4d6d"},
    "space":    {"ground": "#9aa7e8", "wall": "#dfe4ff", "block": "#6c77c9", "accent": "#ffe066", "dark": "#2b2d5a"},
}

# Classic toy-block avatar colours: yellow head, bright blue/pink torsos, green legs.
SKIN = "#ffd166"
SHIRT = "#2f8cff"
SHIRT2 = "#ff6f91"
PANTS = "#4caf50"
SHADOW = "#43506b"


def rgb(h):
    h = h.lstrip("#")
    return [int(h[i:i + 2], 16) for i in (0, 2, 4)]


def _mix(a, b, k=0.45):
    return [round(a[i] * (1 - k) + b[i] * k) for i in range(3)]


def part(parts, name, size, pos, color, group, shape="Box", rot=(0, 0, 0), role="set"):
    parts.append({
        "n": name, "sh": shape, "s": [round(float(v), 3) for v in size],
        "p": [round(float(v), 3) for v in pos],
        "r": [round(float(v), 4) for v in rot],
        "c": [int(v) for v in color], "g": int(group), "role": role,
    })


def studs(parts, prefix, size, pos, color, group, nx=4, nz=3, radius=0.22, height=0.16):
    """Classic plastic-brick studs, built from real cylinder parts."""
    sx, sy, sz = size
    x, y, z = pos
    for ix in range(nx):
        for iz in range(nz):
            px = x - sx / 2 + (ix + 0.5) * sx / nx
            pz = z - sz / 2 + (iz + 0.5) * sz / nz
            part(parts, f"{prefix}_s{ix}{iz}", [radius * 2, height, radius * 2],
                 [px, y + sy / 2 + height / 2, pz], color, group, "Cylinder")


def brick(parts, name, size, pos, color, group, nx=3, nz=2, role="set"):
    part(parts, name, size, pos, color, group, "Box", role=role)
    studs(parts, name, size, pos, color, group, nx, nz)


def blocky_person(parts, prefix, pos, group, scale=1.0, shadow=False, shirt=SHIRT):
    """A jointed blocky toy character. Names drive the renderer's animation."""
    x, y, z = pos
    s = scale
    head = rgb(SHADOW if shadow else SKIN)
    body = rgb(SHADOW if shadow else shirt)
    legs = rgb(SHADOW if shadow else PANTS)
    face = rgb("#2b3a55" if not shadow else SHADOW)

    part(parts, prefix + "_head", [1.05 * s, 1.0 * s, 0.95 * s],
         [x, y + 3.0 * s, z], head, group, "Box", role=prefix)
    part(parts, prefix + "_torso", [1.25 * s, 1.35 * s, 0.65 * s],
         [x, y + 1.95 * s, z], body, group, "Box", role=prefix)
    for side, sign in (("armL", -1), ("armR", 1)):
        part(parts, prefix + "_" + side, [0.36 * s, 1.25 * s, 0.36 * s],
             [x + sign * 0.82 * s, y + 1.95 * s, z], body, group, "Box", role=prefix)
    for side, sign in (("legL", -1), ("legR", 1)):
        part(parts, prefix + "_" + side, [0.45 * s, 1.25 * s, 0.55 * s],
             [x + sign * 0.33 * s, y + 0.63 * s, z], legs, group, "Box", role=prefix)
    if not shadow:
        for sign in (-1, 1):
            part(parts, prefix + "_eye" + str(sign), [0.13 * s, 0.17 * s, 0.08 * s],
                 [x + sign * 0.22 * s, y + 3.08 * s, z + 0.5 * s], face, group, "Box", role=prefix)
        for k, dx in enumerate((-0.16, 0, 0.16)):
            part(parts, prefix + "_smile" + str(k), [0.12 * s, 0.07 * s, 0.07 * s],
                 [x + dx * s, y + 2.76 * s, z + 0.5 * s], face, group, "Box", role=prefix)


# Backwards-compatible name used by older scripts.
stickman = blocky_person

PROP_COLORS = {
    "door": "#7b4b2a", "key": "#ffd166", "coin": "#ffd166", "clock": "#f7fbff",
    "bottle": "#7bdff2", "fish": "#4cc9f0", "bird": "#ff8cc7", "moon": "#ffe066",
    "star": "#ffe066", "chest": "#b5651d", "map": "#fff7e6", "flower": "#ff6f91",
    "ship": "#8b5e3c", "lantern": "#ffb703", "egg": "#fff7e6", "apple": "#ff4d6d",
    "phone": "#1d2638", "jar": "#a8dadc", "book": "#6b6bd6", "compass": "#ffd166",
    "note": "#fff7e6", "box": "#ff8a72", "car": "#ff4d6d", "paperdoor": "#fff7e6",
}


def prop(parts, name, pos, group, color=None):
    """Small recognisable blocky prop built only from primitives."""
    x, y, z = pos
    n = re.sub(r"[^a-z0-9]+", "", str(name).lower())
    c = rgb(color or PROP_COLORS.get(n, "#ffd166"))

    if n in ("note", "letter", "map"):
        part(parts, f"prop_{n}", [1.25, 0.06, 0.9], [x, y + 1.05, z], c, group)
        for k in range(3):
            part(parts, f"prop_{n}_line{k}", [0.85 - k * 0.15, 0.04, 0.07],
                 [x - 0.1, y + 1.1, z - 0.25 + k * 0.25], rgb("#4cc9f0"), group)
    elif n in ("box", "chest", "parcel"):
        brick(parts, f"prop_{n}", [1.35, 1.0, 1.1], [x, y + 0.5, z], c, group, 2, 2)
        part(parts, f"prop_{n}_ribbon", [0.16, 1.04, 1.14], [x, y + 0.5, z], rgb("#ffd166"), group)
        part(parts, f"prop_{n}_label", [0.55, 0.45, 0.05], [x, y + 0.65, z + 0.58], rgb("#fff7e6"), group)
    elif n in ("car", "toycar"):
        part(parts, "prop_car_body", [1.5, 0.45, 0.85], [x, y + 0.42, z], c, group, "Box")
        part(parts, "prop_car_top", [0.8, 0.38, 0.75], [x - 0.1, y + 0.83, z], rgb("#ffd166"), group, "Box")
        for sx in (-0.48, 0.48):
            for sz in (-0.45, 0.45):
                part(parts, f"prop_car_wheel_{sx}_{sz}", [0.32, 0.32, 0.18],
                     [x + sx, y + 0.22, z + sz], rgb("#2b3a55"), group, "Cylinder", (0, 0, 1.57))
    elif n in ("paperdoor", "door"):
        part(parts, "prop_paperdoor", [1.9, 3.0, 0.12], [x, y + 1.5, z], c, group)
        part(parts, "prop_paperdoor_frame", [2.15, 3.25, 0.1], [x, y + 1.5, z - 0.06],
             rgb("#6c77c9"), group)
        part(parts, "prop_paperdoor_knob", [0.18, 0.18, 0.18], [x + 0.62, y + 1.5, z + 0.14],
             rgb("#ffd166"), group, "Ball")
    elif n in ("clock",):
        part(parts, "prop_clock", [1.5, 1.5, 0.2], [x, y + 1.7, z], c, group, "Cylinder", (1.57, 0, 0))
        part(parts, "prop_hand", [0.11, 0.95, 0.1], [x, y + 1.95, z + 0.14], rgb("#2b3a55"), group)
    elif n in ("key", "coin", "star"):
        part(parts, "prop_" + n, [1.0, 1.0, 0.16], [x, y + 1.4, z], c, group, "Cylinder", (0, 0, 1.57))
        part(parts, "prop_" + n + "_stem", [0.22, 1.3, 0.16], [x + 0.55, y + 0.85, z], c, group)
    elif n in ("book",):
        part(parts, "prop_book", [1.5, 0.28, 1.1], [x, y + 0.35, z], c, group)
        part(parts, "prop_page", [1.42, 0.08, 1.02], [x, y + 0.52, z], rgb("#fff7e6"), group)
    elif n in ("flower",):
        part(parts, "prop_stem", [0.14, 1.3, 0.14], [x, y + 0.65, z], rgb("#3fb27f"), group)
        part(parts, "prop_flower", [0.75, 0.75, 0.3], [x, y + 1.5, z], c, group, "Ball")
    elif n in ("phone",):
        part(parts, "prop_phone", [0.85, 1.6, 0.16], [x, y + 1.0, z], c, group)
        part(parts, "prop_screen", [0.7, 1.35, 0.06], [x, y + 1.05, z + 0.12], rgb("#4cc9f0"), group)
    else:
        part(parts, "prop_" + n, [1.1, 1.1, 1.1], [x, y + 0.8, z], c, group, "Ball")


def _counter(shelves_parts, i, wall, accent, dark, block):
    """The lost-property desk: counter, shelves, boxes and a bright sign."""
    brick(shelves_parts, f"g{i}_counter", [11.5, 1.25, 2.4], [0, 0.9, -2.6],
          rgb("#ffd166"), i, 8, 2)
    part(shelves_parts, f"g{i}_counter_front", [11.6, 0.85, 0.18], [0, 0.5, -1.35],
         block, i)
    part(shelves_parts, f"g{i}_sign_board", [8.5, 1.5, 0.25], [0, 5.2, -9.55],
         accent, i)
    for k in range(9):
        part(shelves_parts, f"g{i}_sign_led{k}", [0.55, 0.55, 0.12],
             [-3.6 + k * 0.9, 5.2, -9.38], rgb("#2b3a55"), i)
    for row in range(3):
        y = 1.8 + row * 1.55
        part(shelves_parts, f"g{i}_shelf{row}", [10.0, 0.22, 1.4], [0, y, -8.6],
             dark, i)
        for k in range(5):
            bx = -3.8 + k * 1.9
            col = rgb("#ff8a72") if (k + row) % 2 == 0 else rgb("#4cc9f0")
            brick(shelves_parts, f"g{i}_shelfbox{row}_{k}", [1.2, 1.05, 1.0],
                  [bx, y + 0.64, -8.6], col, i, 2, 2)


def _bus_stop(parts, i, accent, dark):
    part(parts, f"g{i}_buspole", [0.16, 3.4, 0.16], [6.8, 1.7, 0.4], dark, i)
    part(parts, f"g{i}_bus_sign", [1.8, 1.1, 0.16], [6.8, 3.6, 0.4], accent, i)
    part(parts, f"g{i}_bus_stripe", [1.9, 0.18, 0.18], [6.8, 3.25, 0.52], rgb("#ff6f91"), i)


def build_plan(script):
    """Turn a generated storyboard into one bright, coherent blocky world."""
    groups, parts = [], []
    captions = script.get("captions") or []
    scenes = script.get("scenes") or []
    for i, cap in enumerate(captions):
        sc = scenes[i] if i < len(scenes) else {}
        mood = str(sc.get("mood") or "curious").lower()
        motif = str(sc.get("motif") or "room").lower()
        pal = PALETTES.get(mood, PALETTES["curious"])
        if motif in PALETTES:
            pal = dict(pal, block=PALETTES[motif]["block"])
        ground, wall = rgb(pal["ground"]), rgb(pal["wall"])
        block, accent, dark = rgb(pal["block"]), rgb(pal["accent"]), rgb(pal["dark"])
        groups.append({"i": i, "caption": cap, "mood": mood, "motif": motif,
                       "title": cap.upper()[:18]})

        # Bright toy room with studded floor and solid walls.
        part(parts, f"g{i}_floor", [30, 0.7, 26], [0, -0.35, -2], ground, i)
        studs(parts, f"g{i}_floor", [30, 0.7, 26], [0, -0.35, -2], ground, i, 9, 7, 0.3, 0.18)
        part(parts, f"g{i}_backwall", [30, 13, 0.6], [0, 6.5, -10], wall, i)
        part(parts, f"g{i}_leftwall", [0.6, 13, 22], [-14, 6.5, -1], wall, i)
        part(parts, f"g{i}_rightwall", [0.6, 13, 22], [14, 6.5, -1], wall, i)
        part(parts, f"g{i}_skirting", [30, 0.45, 0.4], [0, 0.25, -9.6], dark, i)
        _counter(parts, i, wall, accent, dark, block)

        # Two big, friendly blocky children plus a shadow and background crowd.
        blocky_person(parts, "hero", (-2.2, 0, 1.1), i, 1.28, False, SHIRT)
        blocky_person(parts, "anya", (0.9, 0, 0.7), i, 1.12, False, SHIRT2)
        blocky_person(parts, "shadow", (-2.2, 0.05, 2.5), i, 1.20, True)
        blocky_person(parts, "crowd0", (4.0, 0, -0.8), i, 0.92, True)
        blocky_person(parts, "crowd1", (5.3, 0, -1.5), i, 0.86, True)

        # Scene-specific prop on the counter, plus a recognisable exterior cue.
        props = [str(p).lower() for p in (sc.get("props") or [])]
        if not props:
            props = ["note"]
        main = props[0]
        if "door" in main:
            main = "paperdoor"
        elif "car" in cap.lower():
            main = "car"
        elif "note" in cap.lower() or "handwriting" in cap.lower():
            main = "note"
        prop(parts, main, (0.1, 1.5, -2.0), i)
        if len(props) > 1:
            prop(parts, props[1], (2.6, 1.5, -2.0), i)
        if "bus" in cap.lower() or motif == "street":
            _bus_stop(parts, i, accent, dark)

        # A few bright hanging pennants keep every frame unmistakably toy-like.
        for k in range(6):
            part(parts, f"g{i}_pennant{k}", [0.5, 0.5, 0.12],
                 [-5 + k * 2.0, 7.4 + (k % 2) * 0.25, -9.2],
                 rgb("#ff6f91") if k % 2 else accent, i)

    # Let the renderer bob and turn props without touching the set.
    for p in parts:
        if p["n"].startswith("prop_"):
            p["role"] = "prop"

    return {"title": script.get("title", "Story"), "groups": groups, "parts": parts}


def find_studio():
    explicit = os.environ.get("ROBLOX_STUDIO_EXE", "")
    if explicit and Path(explicit).exists():
        return explicit
    if os.name == "nt":
        bases = [
            Path(os.environ.get("LOCALAPPDATA", "")) / "Roblox" / "Versions",
            Path(os.environ.get("ProgramFiles", "")) / "Roblox" / "Versions",
            Path(os.environ.get("ProgramFiles(x86)", "")) / "Roblox" / "Versions",
        ]
        found = []
        for base in bases:
            if base.exists():
                found.extend(base.glob("version-*/RobloxStudioBeta.exe"))
        if found:
            return str(sorted(found, key=lambda p: p.stat().st_mtime, reverse=True)[0])
    import shutil
    found = shutil.which("RobloxStudioBeta.exe") or shutil.which("RobloxStudio")
    return found or ""


def build(script, out_dir, place_name="film.rbxl"):
    """Run Studio headlessly. Returns (scene dict, studio log path)."""
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    exe = find_studio()
    if not exe:
        print("[studio] Studio executable not found; using the generated scene manifest")
    plan = build_plan(script)
    plan["placePath"] = str((out / place_name).resolve()).replace("\\", "/")
    payload = json.dumps(plan, separators=(",", ":")).replace("]]", "]\\u005d")
    luau = (BASE / "build_place.luau").read_text(encoding="utf-8").replace("@@PLAN@@", payload)
    luau_path = out / "build_place.luau"
    luau_path.write_text(luau, encoding="utf-8")
    log_path = out / "studio.log"

    cmd = [exe, "--task", "RunScript", "--runScriptFile", str(luau_path.resolve()),
           "--outputFile", str(log_path.resolve()), "--quitAfterExecution"] if exe else []
    marker = "SCENE_JSON:"
    scene = None
    if exe:
        print("[studio] launching headless Studio in the cloud runner")
        try:
            proc = subprocess.run(cmd, capture_output=True, text=True, timeout=45)
            text = log_path.read_text(encoding="utf-8", errors="replace") if log_path.exists() else ""
            if not text:
                text = (proc.stdout or "") + "\n" + (proc.stderr or "")
            if marker in text:
                scene = json.loads(text.split(marker, 1)[1].splitlines()[0].strip())
        except Exception as exc:
            print(f"[studio] headless pass unavailable ({exc})")

    if not scene or not scene.get("parts"):
        print("[studio] using generated scene manifest (identical geometry)")
        scene = {"parts": plan["parts"], "groups": plan["groups"], "title": plan["title"]}

    write_json(out / "scene.json", scene)
    (out / "scene.js").write_text(
        "window.SF_SCENE = " + json.dumps(scene, separators=(",", ":")) + ";\n", encoding="utf-8")
    place = out / place_name
    print(f"[studio] {len(scene['parts'])} parts; place={place.exists()} "
          f"({place.stat().st_size if place.exists() else 0} bytes)")
    return scene, log_path
