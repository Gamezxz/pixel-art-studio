#!/usr/bin/env python3
"""Demo/test: 32x32 green slime, 4-frame idle bounce — exercises the full pixelstudio API."""
import sys

sys.path.insert(0, "/Users/game/Projects/.claude/skills/pixel-art-studio/scripts")
from pixelstudio import Sprite, ramp

BODY = ramp("#38b764", 5, hue_shift=18)   # dark -> light greens
DARK = BODY[0]
INK = "#16202c"
WHITE = "#f4f8f0"
SHADOW = "#26402e"

s = Sprite(32, 32, palette=BODY + [INK, WHITE, SHADOW])


def draw_slime(dy=0, squash=0):
    """dy = vertical offset (negative = up). squash widens body & shortens it."""
    # ground shadow (independent of dy; shrinks when slime jumps up)
    s.layer("shadow")
    sh = max(0, 2 + dy)  # dy<=0; higher jump -> smaller shadow
    s.ellipse(9 - sh // 2, 27, 22 + sh // 2, 29, SHADOW)
    s.dither(6, 26, 26, 30, "keep", None, mix=0.5, only=SHADOW)  # checker the shadow

    # body: shifted-shape cel shading (darkest first, lighter shades toward light)
    s.layer("body")
    x0, y0 = 7 - squash, 12 + dy + squash
    x1, y1 = 24 + squash, 27 + dy
    s.ellipse(x0, y0, x1, y1, DARK)
    s.ellipse(x0 - 1, y0 - 1, x1 - 2, y1 - 1, BODY[1], only="opaque")
    s.ellipse(x0 - 1, y0 - 2, x1 - 4, y1 - 3, BODY[2], only="opaque")
    s.ellipse(x0, y0 - 2, x1 - 8, y1 - 8, BODY[3], only="opaque")
    s.circle(x0 + 4, y0 + 3, 2, BODY[4], fill=True, only="opaque")  # specular
    s.px(x0 + 7, y0 + 2, BODY[4], only="opaque")
    s.outline(DARK, where="inside")  # selout

    # face
    s.layer("face")
    ey = 19 + dy + squash // 2
    s.rect(12, ey, 13, ey + 2, INK)
    s.rect(19, ey, 20, ey + 2, INK)
    s.px(12, ey, WHITE)
    s.px(19, ey, WHITE)
    s.line(15, ey + 4, 17, ey + 4, INK)


def clear_all():
    for name in ("shadow", "body", "face"):
        s.layer(name)
        s.clear()


# frame 1: rest
draw_slime(dy=0, squash=0)

# frames 2-4: bounce cycle  (rest -> squash -> stretch-up -> falling)
poses = [(0, 1), (-3, 0), (-1, 0)]  # (dy, squash)
for dy, squash in poses:
    s.add_frame(copy=True)
    clear_all()
    draw_slime(dy=dy, squash=squash)

s.set_duration(160, frames=[1])
s.set_duration(90, frames=[2])
s.set_duration(120, frames=[3])
s.set_duration(90, frames=[4])
s.tag("idle", 1, 4, direction="forward")

# inspect
s.preview("preview.png", scale=8, labels=True)
s.save_silhouette("silhouette.png", frame=1)
s.save_swatch("swatch.png")
s.stats()

# deliver
s.save_png("slime.png", frame=1)
s.save_png("slime@8x.png", frame=1, scale=8)
s.save_gif("slime.gif", scale=6, bg="#e8e4da")
s.save_gif("slime_transparent.gif", scale=6)
s.save_spritesheet("slime_sheet.png", layout="horizontal", padding=1)
s.save_project("slime.pxproj.json")
print("OK")
