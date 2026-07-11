#!/usr/bin/env python3
"""lpc.py — LPC (Liberated Pixel Cup) universal spritesheet contract.

The LAYOUT adapter for humanoid characters (2 arms, 2 legs): assemble frames
drawn with pixelstudio into an LPC-compatible universal sheet, so the result
drops into every LPC-aware engine/template (Godot, Phaser, ULPC viewers).

Only the grid convention comes from LPC — your art stays yours. (Imported LPC
*assets* are CC-BY-SA 3.0 / GPL 3.0 and need per-artist credits; this module
ships none.)

Usage:
    from lpc import LPCSheet, ACTIONS, DIRS

    sheet = LPCSheet()
    for action, direction, frame in sheet.slots():        # every cell to fill
        img = draw(action, direction, frame)               # your PIL/Sprite render
        sheet.place(action, direction, frame, img)
    sheet.save("hero_lpc.png")                             # + hero_lpc.json meta
    sheet.gif("walk_left.gif", "walk", "left", scale=2)    # preview any row
"""
import json
from collections import OrderedDict
from PIL import Image

CELL = 64                    # LPC cell is 64x64; smaller art is centered inside
FEET = 58                    # baseline: bottom-most opaque row sits here
DIRS = ["up", "left", "down", "right"]          # LPC row order within an action

# Universal sheet, classic ULPC row order. walk frame 0 = standing idle.
ACTIONS = OrderedDict([
    ("spellcast", {"frames": 7,  "dirs": 4, "ms": 100}),
    ("thrust",    {"frames": 8,  "dirs": 4, "ms": 90}),
    ("walk",      {"frames": 9,  "dirs": 4, "ms": 90}),
    ("slash",     {"frames": 6,  "dirs": 4, "ms": 80}),
    ("shoot",     {"frames": 13, "dirs": 4, "ms": 70}),
    ("hurt",      {"frames": 6,  "dirs": 1, "ms": 110}),   # down-facing only
])
COLS = max(a["frames"] for a in ACTIONS.values())          # 13
ROWS = sum(a["dirs"] for a in ACTIONS.values())            # 21


def row_of(action, direction="down"):
    """Absolute sheet row for an action+direction."""
    if action not in ACTIONS:
        raise KeyError(f"unknown action {action!r}; have {list(ACTIONS)}")
    r = 0
    for name, a in ACTIONS.items():
        if name == action:
            if a["dirs"] == 1:
                return r
            if direction not in DIRS:
                raise KeyError(f"unknown direction {direction!r}")
            return r + DIRS.index(direction)
        r += a["dirs"]
    raise AssertionError


class LPCSheet:
    def __init__(self):
        self.im = Image.new("RGBA", (COLS * CELL, ROWS * CELL), (0, 0, 0, 0))

    def slots(self):
        """Yield every (action, direction, frame) cell in sheet order."""
        for action, a in ACTIONS.items():
            dirs = DIRS if a["dirs"] == 4 else ["down"]
            for d in dirs:
                for f in range(a["frames"]):
                    yield action, d, f

    def place(self, action, direction, frame, img, feet=FEET):
        """Paste one frame into its cell: centered on x, feet on the baseline.

        img: PIL RGBA (any size <= CELL) or a pixelstudio Sprite (frame 1 used —
        pass sprite.composite(n) to pick another).
        """
        if hasattr(img, "composite"):                      # pixelstudio Sprite
            img = img.composite(1)
        img = img.convert("RGBA")
        a = ACTIONS[action]
        if frame >= a["frames"]:
            raise ValueError(f"{action} has {a['frames']} frames, got index {frame}")
        bbox = img.getbbox()
        if bbox is None:
            return self
        x0, y0, x1, y1 = bbox
        crop = img.crop(bbox)
        if crop.width > CELL or crop.height > CELL:
            raise ValueError(f"art {crop.width}x{crop.height} exceeds {CELL}px cell")
        dx = (CELL - crop.width) // 2
        dy = min(feet - crop.height, CELL - crop.height)
        cx = frame * CELL
        cy = row_of(action, direction) * CELL
        self.im.paste(crop, (cx + dx, cy + max(dy, 0)), crop)
        return self

    def cell(self, action, direction, frame):
        x, y = frame * CELL, row_of(action, direction) * CELL
        return self.im.crop((x, y, x + CELL, y + CELL))

    def save(self, path):
        self.im.save(path)
        meta = {
            "cell": CELL, "cols": COLS, "rows": ROWS, "feet_baseline": FEET,
            "direction_order": DIRS,
            "actions": {n: {"frames": a["frames"],
                            "row": row_of(n, "up" if a["dirs"] == 4 else "down"),
                            "dirs": (DIRS if a["dirs"] == 4 else ["down"]),
                            "ms_per_frame": a["ms"]}
                        for n, a in ACTIONS.items()},
        }
        jpath = str(path).rsplit(".", 1)[0] + ".json"
        with open(jpath, "w") as f:
            json.dump(meta, f, indent=2)
        print(f"lpc sheet -> {path} ({self.im.width}x{self.im.height}) + {jpath}")
        return self

    def gif(self, path, action, direction="down", scale=2, skip_idle=False):
        """Render one action row as an animated GIF preview."""
        a = ACTIONS[action]
        start = 1 if (skip_idle and action == "walk") else 0
        frames = []
        for f in range(start, a["frames"]):
            c = self.cell(action, direction, f)
            c = c.resize((CELL * scale, CELL * scale), Image.NEAREST)
            bg = Image.new("RGBA", c.size, (0, 0, 0, 0))
            bg.paste(c, (0, 0), c)
            frames.append(bg)
        frames[0].save(path, save_all=True, append_images=frames[1:],
                       duration=a["ms"], loop=0, disposal=2)
        print(f"gif -> {path} ({len(frames)} frames)")
        return self
