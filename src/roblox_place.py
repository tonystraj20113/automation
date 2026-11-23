"""Build the Roblox place and an exact scene manifest, headlessly, in Studio.

The real Roblox Studio executable runs ``--task RunScript`` on a generated Luau
file. That script builds every part in the DataModel, exports the editable
.rbxl place, and prints a JSON manifest to --outputFile. The cloud renderer
reads the manifest, so art direction happens in Studio and not in JS.
"""
import json, os, re, subprocess, time
from pathlib import Path

from .utils import ROOT, write_json

BASE = ROOT / "studio"

# Flat, toy-shop colours. Everything is original: no Roblox logos or assets.
PALETTES = {
    "curious":  {"ground": "#6ed6a5", "wall": "#bfe9f2", "block": "#ff8a72", "accent": "#ffd166", "dark": "#28405c"},
    "mystery":  {"ground": "#3e5c78", "wall": "#263b57", "block": "#6b6bd6", "accent": "#ffd166", "dark": "#121c30"},
    "spooky":   {"ground": "#39334f", "wall": "#241f36", "block": "#7b5bb5", "accent": "#ff7a9c", "dark": "#0d0b18"},
    "playful":  {"ground": "#8ce0c0", "wall": "#ffe6a7", "block": "#ff6f91", "accent": "#4cc9f0", "dark": "#2b3a55"},
    "street":   {"ground": "#63d29a", "wall": "#b9d0d8", "block": "#ff7a6e", "accent": "#ffd166", "dark": "#1d2638"},
    "room":     {"ground": "#d9c7a3", "wall": "#bfe3f5", "block": "#8b5e3c", "accent": "#ffd166", "dark": "#243040"},
    "forest":   {"ground": "#4fbf8b", "wall": "#1d6b5a", "block": "#2e8b57", "accent": "#ffd166", "dark": "#17332e"},
    "ocean":    {"ground": "#3a86ff", "wall": "#1b3a6b", "block": "#7bdff2", "accent": "#ffd166", "dark": "#12213d"},
    "sky":      {"ground": "#5b6ee1", "wall": "#16224a", "block": "#9bb7ff", "accent": "#ffe066", "dark": "#0b1230"},
    "night":    {"ground": "#2c3563", "wall": "#171d3c", "block": "#4c5aa8", "accent": "#ffe066", "dark": "#0a0e22"},
    "city":     {"ground": "#7b8fa8", "wall": "#40556f", "block": "#ff8fab", "accent": "#ffd166", "dark": "#1c2736"},
    "desert":   {"ground": "#efc27b", "wall": "#d99a4e", "block": "#e07a5f", "accent": "#3d405b", "dark": "#5a3d2b"},
    "river":    {"ground": "#4fb3d9", "wall": "#2176a8", "block": "#8ce0c0", "accent": "#ffd166", "dark": "#143a55"},
    "space":    {"ground": "#202649", "wall": "#10142d", "block": "#6c77c9", "accent": "#ffe066", "dark": "#080a1a"},
}


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


def stickman(parts, prefix, pos, group, color, scale=1.0, shadow=False):
    """A jointed blocky 3D stickman. Names let the renderer animate it."""
    x, y, z = pos
    dark = [5, 7, 12] if shadow else color
    face = [8, 12, 22] if shadow else [247, 251, 255]
    s = scale
    part(parts, prefix + "_head", [0.92 * s, 0.92 * s, 0.92 * s],
         [x, y + 3.0 * s, z], dark, group, "Ball", role=prefix)
    part(parts, prefix + "_torso", [0.34 * s, 1.5 * s, 0.34 * s],
         [x, y + 2.0 * s, z], dark, group, "Cylinder", role=prefix)
    for side, sign in (("armL", -1), ("armR", 1)):
        part(parts, prefix + "_" + side, [0.22 * s, 1.3 * s, 0.22 * s],
             [x + sign * 0.42 * s, y + 2.1 * s, z], dark, group, "Cylinder",
             (0, 0, sign * 0.42), prefix)
    for side, sign in (("legL", -1), ("legR", 1)):
        part(parts, prefix + "_" + side, [0.26 * s, 1.5 * s, 0.26 * s],
             [x + sign * 0.24 * s, y + 0.72 * s, z], dark, group, "Cylinder",
             (0, 0, -sign * 0.1), prefix)
    if not shadow:
        for sign in (-1, 1):
            part(parts, prefix + "_eye" + str(sign), [0.13 * s, 0.13 * s, 0.08 * s],
                 [x + sign * 0.16 * s, y + 3.08 * s, z + 0.44 * s], face, group,
                 "Ball", role=prefix)


PROP_COLORS = {
    "door": "#7b4b2a", "key": "#ffd166", "coin": "#ffd166", "clock": "#f7fbff",
    "bottle": "#7bdff2", "fish": "#4cc9f0", "bird": "#ff8cc7", "moon": "#ffe066",
    "star": "#ffe066", "chest": "#b5651d", "map": "#fff7e6", "flower": "#ff6f91",
    "ship": "#8b5e3c", "lantern": "#ffb703", "egg": "#fff7e6", "apple": "#ff4d6d",
    "phone": "#1d2638", "jar": "#a8dadc", "book": "#6b6bd6", "compass": "#ffd166",
}


def prop(parts, name, pos, group, color=None):
    """Small recognisable blocky prop built only from primitives."""
    x, y, z = pos
    c = rgb(color or PROP_COLORS.get(name.lower(), "#ffd166"))
    n = name.lower()
    if n == "door":
        part(parts, "prop_door", [2.2, 3.6, 0.25], [x, y + 1.8, z], c, group)
        part(parts, "prop_knob", [0.18, 0.18, 0.18], [x + 0.7, y + 1.7, z + 0.2],
             rgb("#ffd166"), group, "Ball")
    elif n in ("key", "coin", "star"):
        part(parts, "prop_" + n, [1.1, 1.1, 0.16], [x, y + 1.4, z], c, group, "Cylinder", (0, 0, 1.57))
        part(parts, "prop_" + n + "_stem", [0.22, 1.4, 0.16], [x + 0.6, y + 0.8, z], c, group)
    elif n == "clock":
        part(parts, "prop_clock", [1.8, 1.8, 0.2], [x, y + 1.6, z], rgb("#f7fbff"), group, "Cylinder", (1.57, 0, 0))
        part(parts, "prop_hand", [0.12, 1.1, 0.1], [x, y + 1.9, z + 0.15], rgb("#1d2638"), group)
    elif n in ("bottle", "jar"):
        part(parts, "prop_" + n, [0.9, 1.7, 0.9], [x, y + 0.9, z], c, group, "Cylinder")
        part(parts, "prop_" + n + "_lid", [0.5, 0.3, 0.5], [x, y + 1.9, z], rgb("#f7fbff"), group)
    elif n == "flower":
        part(parts, "prop_stem", [0.14, 1.4, 0.14], [x, y + 0.7, z], rgb("#2e8b57"), group)
        part(parts, "prop_flower", [0.8, 0.8, 0.3], [x, y + 1.6, z], c, group, "Ball")
    elif n == "book":
        part(parts, "prop_book", [1.6, 0.25, 1.2], [x, y + 0.4, z], c, group)
        part(parts, "prop_page", [1.5, 0.08, 1.1], [x, y + 0.55, z], rgb("#fff7e6"), group)
    elif n == "chest":
        part(parts, "prop_chest", [1.8, 1.0, 1.2], [x, y + 0.5, z], c, group)
        part(parts, "prop_lid", [1.9, 0.35, 1.3], [x, y + 1.15, z], rgb("#ffd166"), group)
    elif n == "phone":
        part(parts, "prop_phone", [0.9, 1.7, 0.16], [x, y + 1.0, z], c, group)
        part(parts, "prop_screen", [0.75, 1.4, 0.05], [x, y + 1.05, z + 0.11], rgb("#4cc9f0"), group)
    elif n == "ship":
        part(parts, "prop_ship", [2.6, 0.5, 1.4], [x, y + 0.4, z], c, group)
        part(parts, "prop_mast", [0.15, 2.4, 0.15], [x, y + 1.7, z], rgb("#8b5e3c"), group)
    else:
        part(parts, "prop_" + re.sub(r"[^a-z0-9]+", "_", n), [1.2, 1.2, 1.2],
             [x, y + 0.8, z], c, group, "Ball")


def build_plan(script):
    """Turn a generated storyboard into one original blocky Roblox world."""
    groups, parts = [], []
    captions = script.get("captions") or []
    scenes = script.get("scenes") or []
    for i, cap in enumerate(captions):
        sc = scenes[i] if i < len(scenes) else {}
        mood = str(sc.get("mood") or "curious").lower()
        motif = str(sc.get("motif") or "city").lower()
        pal = PALETTES.get(mood, PALETTES["curious"])
        if motif in PALETTES:
            pal = dict(pal, block=PALETTES[motif]["block"])
        ground, wall = rgb(pal["ground"]), rgb(pal["wall"])
        block, accent, dark = rgb(pal["block"]), rgb(pal["accent"]), rgb(pal["dark"])
        groups.append({"i": i, "caption": cap, "mood": mood, "motif": motif,
                       "title": cap.upper()[:18]})

        part(parts, f"g{i}_ground", [46, 0.8, 46], [0, -0.4, 0], ground, i)
        part(parts, f"g{i}_back", [40, 18, 0.6], [0, 8, -14], wall, i)
        part(parts, f"g{i}_floor", [9, 0.12, 34], [0, 0.06, 0], _mix(ground, [255, 255, 255], 0.3), i)

        for k in range(6):
            bx = -17 + k * 6.6
            h = 3.2 + ((i * 7 + k * 5) % 6) * 1.05
            part(parts, f"g{i}_building{k}", [5.2, h, 5.0], [bx, h / 2, -9.5],
                 _mix(block, dark, 0.12 * (k % 3)), i)
            part(parts, f"g{i}_window{k}", [1.5, 1.5, 0.12], [bx, h * 0.62, -6.95],
                 accent, i)
            part(parts, f"g{i}_roof{k}", [5.6, 0.4, 5.4], [bx, h + 0.2, -9.5], dark, i)

        # Framing blocks keep every shot deep and parallax-rich.
        for k, sx in enumerate((-1, 1)):
            part(parts, f"g{i}_frame{k}", [2.4, 8 + (i % 3), 2.4],
                 [sx * 12, 4, 4.5], _mix(dark, block, 0.3), i)

        stickman(parts, "hero", (-1.9, 0, 4.2), i, rgb("#273249"), 0.98)
        stickman(parts, "shadow", (-0.5, 0.03, 3.1), i, [5, 7, 12], 0.92, True)
        for k in range(4):
            stickman(parts, f"crowd{k}", (2.4 + k * 1.5, 0.03, 1.4 - k * 0.4),
                     i, [7, 10, 18], 0.78, True)

        props = sc.get("props") or []
        for k, nm in enumerate(props[:3]):
            prop(parts, str(nm), (4.2 + k * 2.2, 0, -1.5 - k * 0.5), i)
        if not props:
            prop(parts, "door", (5.0, 0, -2.0), i)

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
           "--outputFile", str(log_path.resolve()), "--quitAfterExecution"]
    marker = "SCENE_JSON:"
    scene = None
    if exe:
        print("[studio] launching headless Studio in the cloud runner")
        try:
            proc = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
            text = log_path.read_text(encoding="utf-8", errors="replace") if log_path.exists() else ""
            if not text:
                text = (proc.stdout or "") + "\n" + (proc.stderr or "")
            if marker in text:
                scene = json.loads(text.split(marker, 1)[1].splitlines()[0].strip())
        except Exception as exc:
            print(f"[studio] headless pass unavailable ({exc})")

    # Cloud-safe fallback: the same part list the Luau script builds is emitted
    # directly, so a render never depends on a GUI/desktop quirk of the runner.
    if not scene or not scene.get("parts"):
        print("[studio] using generated scene manifest (identical geometry)")
        scene = {"parts": plan["parts"], "groups": plan["groups"], "title": plan["title"]}

    write_json(out / "scene.json", scene)
    scene_js = out / "scene.js"
    scene_js.write_text("window.SF_SCENE = " + json.dumps(scene, separators=(",", ":")) + ";\n",
                        encoding="utf-8")
    place = out / place_name
    print(f"[studio] {len(scene['parts'])} parts; place={place.exists()} ({place.stat().st_size if place.exists() else 0} bytes)")
    return scene, log_path
