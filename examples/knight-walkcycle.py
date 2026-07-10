#!/usr/bin/env python3
"""Turn a codex-generated walk-cycle sheet (6 cells in a row) into a clean walk GIF.

Usage: python3 knight-walkcycle.py <sheet.png> <out_dir> [target_h]

The whole sheet goes through pixelpipe-style cleanup ONCE (one shared palette for
every frame), then is sliced into cells, background-stripped, aligned (feet to a
common ground line, body centered per cell), outlined, and written as
knight_walk.gif + spritesheet.
"""
import json
import os
import sys
from PIL import Image

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                "..", "scripts"))
from pixelstudio import Sprite  # noqa: E402

SCALE = 4
BG = (244, 241, 234)
N_FRAMES = 6


def strip_bg(im):
    im = im.convert("RGBA")
    px = im.load()
    w, h = im.size
    corner = px[0, 0]

    def is_bg(c):
        return c[3] > 0 and sum(abs(c[i] - corner[i]) for i in range(3)) < 60

    # global color-key: also clears bg pockets enclosed by the sprite (plume loops)
    for y in range(h):
        for x in range(w):
            if is_bg(px[x, y]):
                px[x, y] = (0, 0, 0, 0)
    return im


def outline(im, color=(31, 33, 41, 255)):
    im = im.copy()
    px = im.load()
    w, h = im.size
    edge = [(x, y) for y in range(h) for x in range(w)
            if px[x, y][3] == 0 and any(
                0 <= x + dx < w and 0 <= y + dy < h and px[x + dx, y + dy][3] > 0
                for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)))]
    for x, y in edge:
        px[x, y] = color
    return im


def bbox(im):
    return im.getbbox()


def main():
    src, out_dir = sys.argv[1], sys.argv[2]
    target_h = int(sys.argv[3]) if len(sys.argv) > 3 else 128
    os.makedirs(out_dir, exist_ok=True)

    sheet = Image.open(src)
    scale = sheet.height / target_h
    sp = Sprite.from_png(src, scale=scale)
    sp.clean(max_colors=28, despeckle_min=2, dedupe_tol=6)
    clean = sp.composite(1)

    cw = clean.width // N_FRAMES
    cells = [strip_bg(clean.crop((i * cw, 0, (i + 1) * cw, clean.height)))
             for i in range(N_FRAMES)]

    # align: feet to the deepest common ground line, body centered in the cell
    boxes = [bbox(c) for c in cells]
    ground = max(b[3] for b in boxes)
    frames = []
    for c, b in zip(cells, boxes):
        f = Image.new("RGBA", c.size, (0, 0, 0, 0))
        dx = (c.width - (b[2] - b[0])) // 2 - b[0]
        f.paste(c, (dx, ground - b[3]), c)
        frames.append(outline(f))

    big = []
    for f in frames:
        bg = Image.new("RGBA", f.size, BG + (255,))
        bg.alpha_composite(f)
        big.append(bg.convert("RGB").resize(
            (f.width * SCALE, f.height * SCALE), Image.NEAREST))
    gif = os.path.join(out_dir, "knight_walk.gif")
    big[0].save(gif, save_all=True, append_images=big[1:], loop=0,
                duration=[110] * N_FRAMES, disposal=1)
    print("gif ->", gif)

    w, h = frames[0].size
    out_sheet = Image.new("RGBA", (N_FRAMES * (w + 1) + 1, h + 2), (0, 0, 0, 0))
    meta = []
    for i, f in enumerate(frames):
        x = 1 + i * (w + 1)
        out_sheet.paste(f, (x, 1))
        meta.append({
            "filename": "frame_%d" % i,
            "frame": {"x": x, "y": 1, "w": w, "h": h},
            "rotated": False, "trimmed": False,
            "spriteSourceSize": {"x": 0, "y": 0, "w": w, "h": h},
            "sourceSize": {"w": w, "h": h},
            "duration": 110,
        })
    out_sheet.save(os.path.join(out_dir, "knight_sheet.png"))
    with open(os.path.join(out_dir, "knight_sheet.json"), "w") as fp:
        json.dump({"frames": meta,
                   "meta": {"size": {"w": out_sheet.width, "h": out_sheet.height},
                            "scale": 1}}, fp, indent=1)
    print("sheet ->", os.path.join(out_dir, "knight_sheet.png"))


if __name__ == "__main__":
    main()
