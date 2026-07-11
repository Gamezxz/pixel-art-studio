#!/usr/bin/env python3
"""Capybara 4-direction walk — chibi style from ref image #2.

Sprout on head, green swirl scarf, tan body with dark muzzle patch.
32x32 per frame, 4 dirs (down/left/right/up) x 4-frame walk.
"""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "scripts"))
from pixelstudio import Sprite
from PIL import Image

W = H = 32
GROUND = 29

# palette — every material 3 values, hue-shifted
OUT   = "#2e1f16"   # warm dark outline
FUR   = ["#8a5a35", "#c99a5f", "#e0b878"]   # shade / base / light
PATCH = ["#5c3a26", "#7a4e30"]              # dark head patch
SCARF = ["#3d5426", "#5a7a38", "#74975022"[:7]]  # shade / base / swirl-lite
SCARF[2] = "#749750"
SPROUT = ["#4c8b2e", "#7dc242"]
FOOT  = ["#4a3020", "#6b4630"]
CREAM = "#efdcb4"
PAL = [OUT] + FUR + PATCH + SCARF + SPROUT + FOOT + [CREAM]

# walk poses: (body_bob, front_leg_dx, back_leg_dx)  for side view
# and (body_bob, left_leg_dy, right_leg_dy) for down/up
POSES = [(0, 2, -2), (-1, 0, 0), (0, -2, 2), (-1, 0, 0)]


def sprout(s, cx, top):
    """curly sprout on head"""
    s.line(cx, top, cx, top + 3, SPROUT[0])
    # leaf loop
    s.px(cx - 1, top - 1, SPROUT[1]); s.px(cx - 2, top - 2, SPROUT[1])
    s.px(cx - 1, top - 3, SPROUT[1]); s.px(cx, top - 2, SPROUT[1])
    s.px(cx + 1, top - 1, SPROUT[1]); s.px(cx + 2, top - 2, SPROUT[1])
    s.px(cx + 1, top - 3, SPROUT[0])


def draw_down(s, pose, back=False):
    bob, lleg, rleg = POSES[pose][0], POSES[pose][1] // 2, POSES[pose][2] // 2
    y = bob
    # feet (draw first, behind body) — alternate stepping = dy
    s.rect(11, 25 + y - lleg, 14, 29, FOOT[1])
    s.rect(18, 25 + y - rleg, 21, 29, FOOT[1])
    # body+head one chibi blob
    s.ellipse(7, 5 + y, 24, 24 + y, FUR[1])
    # ears
    s.rect(9, 4 + y, 11, 6 + y, FUR[0])
    s.rect(20, 4 + y, 22, 6 + y, FUR[0])
    # top light
    s.ellipse(10, 7 + y, 21, 12 + y, FUR[2], only=FUR[1])
    if back:
        # back view: patch on back of head, no face
        s.ellipse(12, 8 + y, 19, 13 + y, PATCH[1], only="opaque")
    else:
        # dark patch over left brow (ref: patch on one side)
        s.ellipse(8, 6 + y, 14, 11 + y, PATCH[1], only="opaque")
        # eyes: sleepy dashes
        s.line(11, 12 + y, 13, 12 + y, OUT)
        s.line(18, 12 + y, 20, 12 + y, OUT)
        # muzzle
        s.ellipse(13, 14 + y, 18, 17 + y, CREAM)
        s.px(15, 15 + y, OUT); s.px(16, 15 + y, OUT)
    # scarf band
    s.rect(8, 18 + y, 23, 21 + y, SCARF[1])
    s.line(8, 21 + y, 23, 21 + y, SCARF[0])
    s.px(11, 19 + y, SCARF[2]); s.px(12, 19 + y, SCARF[2])
    s.px(19, 20 + y, SCARF[2]); s.px(20, 19 + y, SCARF[2])
    sprout(s, 16, 2 + y)
    s.outline(OUT, where="outside")


def draw_side(s, pose):
    """faces RIGHT; left = mirror"""
    bob, f_dx, b_dx = POSES[pose]
    y = bob
    # legs first (behind): back leg + front leg, swing +-2
    s.rect(9 + b_dx, 23, 12 + b_dx, 29, FOOT[1])
    s.rect(20 + f_dx, 23, 23 + f_dx, 29, FOOT[1])
    # one chibi capsule: rump left, big head right
    s.ellipse(4, 11 + y, 22, 26 + y, FUR[1])
    s.ellipse(12, 5 + y, 28, 21 + y, FUR[1])
    # soft rump shade (thin crescent, not a blob)
    s.ellipse(4, 13 + y, 10, 25 + y, FUR[0], only=FUR[1])
    s.ellipse(6, 13 + y, 11, 24 + y, FUR[1], only=FUR[0])
    # top light on head
    s.ellipse(15, 6 + y, 25, 10 + y, FUR[2], only=FUR[1])
    # ear nub on top of head
    s.rect(17, 4 + y, 19, 5 + y, FUR[0])
    # small brow patch behind the eye (ref: one dark patch)
    s.ellipse(14, 7 + y, 18, 11 + y, PATCH[1], only=FUR[2])
    s.ellipse(14, 8 + y, 17, 11 + y, PATCH[1], only=FUR[1])
    # eye: sleepy dash, clear of the patch
    s.line(22, 10 + y, 24, 10 + y, OUT)
    # muzzle: cream front of face + nose
    s.ellipse(24, 11 + y, 28, 16 + y, CREAM, only=FUR[1])
    s.ellipse(24, 11 + y, 28, 16 + y, CREAM, only=FUR[2])
    s.px(28, 12 + y, OUT); s.px(27, 12 + y, OUT)
    # scarf: band under the chin, wrapping the chest
    s.rect(10, 17 + y, 23, 20 + y, SCARF[1])
    s.line(10, 20 + y, 23, 20 + y, SCARF[0])
    s.px(13, 18 + y, SCARF[2]); s.px(14, 18 + y, SCARF[2]); s.px(19, 19 + y, SCARF[2])
    sprout(s, 19, 4 + y)
    s.outline(OUT, where="outside")


def build_dir(kind):
    s = Sprite(W, H, palette=PAL)
    for f in range(4):
        if f:
            s.add_frame(copy=False)
            s.use(frame=f + 1)
        if kind == "down":
            draw_down(s, f)
        elif kind == "up":
            draw_down(s, f, back=True)
        else:
            draw_side(s, f)
            if kind == "left":
                im = s._img()
                im.paste(im.transpose(Image.FLIP_LEFT_RIGHT), (0, 0))
    s.set_duration(140, frames="all")
    return s


# outputs land in the current working directory

dirs = {}
for kind in ("down", "left", "right", "up"):
    sp = build_dir(kind)
    dirs[kind] = sp
    sp.save_gif(f"capy_walk_{kind}.gif", scale=6)

# contact sheet preview: 4 rows x 4 frames
sheet = Image.new("RGBA", (W * 4, H * 4), (0, 0, 0, 0))
for r, kind in enumerate(("down", "left", "right", "up")):
    for f in range(4):
        sheet.paste(dirs[kind].composite(f + 1), (f * W, r * H))
sheet.save("spritesheet.png")
sheet.resize((sheet.width * 6, sheet.height * 6), Image.NEAREST).save("preview.png")
sheet.resize((sheet.width * 6, sheet.height * 6), Image.NEAREST).save("spritesheet@6x.png")

# engine metadata: rows = down/left/right/up, 4 frames each, 140ms
import json
meta = {"frame": {"w": W, "h": H}, "ms_per_frame": 140,
        "rows": {k: i for i, k in enumerate(("down", "left", "right", "up"))},
        "frames_per_row": 4}
with open("spritesheet.json", "w") as f:
    json.dump(meta, f, indent=2)
dirs["down"].stats()
print("ok")
