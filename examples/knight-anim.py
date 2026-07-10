#!/usr/bin/env python3
"""Puppet the pixelpipe-cleaned knight into idle + walk GIFs — deterministic, no re-rolling.

Usage: python3 knight-anim.py <clean.png> <out_dir>

Layers are cut from the single cleaned sprite (plume / upper body / legs) and offset
per frame: breathing bob + plume sway for idle, march bob + plume trail for walk.
Also writes a spritesheet (knight_sheet.png + Aseprite-style knight_sheet.json).
"""
import json
import os
import sys
from collections import deque

from PIL import Image

SCALE = 4
BG = (244, 241, 234)


def strip_bg(im):
    """Flood-fill the baked navy background to transparency from the edges only,
    so navy-dark armor shading inside the silhouette survives."""
    im = im.convert("RGBA")
    px = im.load()
    w, h = im.size

    corner = px[0, 0]

    def is_bg(c):
        return c[3] > 0 and sum(abs(c[i] - corner[i]) for i in range(3)) < 60

    seen = set()
    q = deque((x, y) for x in range(w) for y in (0, h - 1) if is_bg(px[x, y]))
    q.extend((x, y) for y in range(h) for x in (0, w - 1) if is_bg(px[x, y]))
    while q:
        x, y = q.popleft()
        if (x, y) in seen or not (0 <= x < w and 0 <= y < h) or not is_bg(px[x, y]):
            continue
        seen.add((x, y))
        px[x, y] = (0, 0, 0, 0)
        q.extend(((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)))
    return im


def outline(im, color=(31, 33, 41, 255)):
    """1px dark outline so the sprite reads on light backgrounds."""
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


def cut(im, box):
    layer = Image.new("RGBA", im.size, (0, 0, 0, 0))
    layer.paste(im.crop(box), box[:2])
    return layer


def split_layers(im):
    """plume: red pixels in the top third; legs: bottom band; body: everything else."""
    w, h = im.size
    px = im.load()
    plume = Image.new("RGBA", im.size, (0, 0, 0, 0))
    ppx = plume.load()
    body = im.copy()
    bpx = body.load()
    for y in range(h // 3):
        for x in range(w):
            r, g, b, a = px[x, y]
            if a and r > 110 and r > g * 1.8 and r > b * 1.8:
                ppx[x, y] = px[x, y]
                bpx[x, y] = (0, 0, 0, 0)
    waist = int(h * 0.68)
    legs = cut(body, (0, waist, w, h))
    upper = cut(body, (0, 0, w, waist))
    return plume, upper, legs


def compose(size, parts):
    """parts: list of (layer, (dx, dy))."""
    out = Image.new("RGBA", size, (0, 0, 0, 0))
    for layer, (dx, dy) in parts:
        out.paste(layer, (dx, dy), layer)
    return out

def frame_to_gif(frames, path, durations):
    big = []
    for f in frames:
        bg = Image.new("RGBA", f.size, BG + (255,))
        bg.alpha_composite(f)
        big.append(bg.convert("RGB").resize(
            (f.width * SCALE, f.height * SCALE), Image.NEAREST))
    big[0].save(path, save_all=True, append_images=big[1:], loop=0,
                duration=durations, disposal=1)
    print("gif ->", path)


def spritesheet(frames, durations, out_png, out_json):
    n = len(frames)
    w, h = frames[0].size
    sheet = Image.new("RGBA", (n * (w + 1) + 1, h + 2), (0, 0, 0, 0))
    meta = []
    for i, f in enumerate(frames):
        x = 1 + i * (w + 1)
        sheet.paste(f, (x, 1))
        meta.append({
            "filename": "frame_%d" % i,
            "frame": {"x": x, "y": 1, "w": w, "h": h},
            "rotated": False, "trimmed": False,
            "spriteSourceSize": {"x": 0, "y": 0, "w": w, "h": h},
            "sourceSize": {"w": w, "h": h},
            "duration": durations[i],
        })
    sheet.save(out_png)
    with open(out_json, "w") as fp:
        json.dump({"frames": meta, "meta": {"size": {"w": sheet.width, "h": sheet.height},
                                            "scale": 1}}, fp, indent=1)
    print("sheet ->", out_png)


def main():
    src, out_dir = sys.argv[1], sys.argv[2]
    os.makedirs(out_dir, exist_ok=True)
    im = outline(strip_bg(Image.open(src)))
    plume, upper, legs = split_layers(im)

    # idle: breathing bob on the upper body, plume sways with it
    idle_specs = [((0, 0), (0, 0)), ((1, 0), (0, 1)), ((1, 1), (0, 1)), ((0, 0), (0, 0))]
    idle = [compose(im.size, [(legs, (0, 0)), (upper, u), (plume, p)])
            for p, u in idle_specs]
    frame_to_gif(idle, os.path.join(out_dir, "knight_idle.gif"), [320] * 4)

    # walk: march bob on the whole figure, plume trails a step behind
    bob = [0, -1, 0, 0, -1, 0]
    trail = [0, -1, -2, -1, 0, 1]
    walk = [compose(im.size, [(legs, (0, 0)), (upper, (0, bob[i])),
                              (plume, (trail[i], bob[i]))])
            for i in range(6)]
    frame_to_gif(walk, os.path.join(out_dir, "knight_walk.gif"), [110] * 6)
    spritesheet(walk, [110] * 6, os.path.join(out_dir, "knight_sheet.png"),
                os.path.join(out_dir, "knight_sheet.json"))

    im.save(os.path.join(out_dir, "knight.png"))
    print("sprite ->", os.path.join(out_dir, "knight.png"))


if __name__ == "__main__":
    main()
