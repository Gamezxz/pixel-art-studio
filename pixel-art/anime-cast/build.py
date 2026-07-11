#!/usr/bin/env python3
"""Anime cast — 10 diverse 32x32 characters, each with a 3-frame idle loop.

One script, one shared discipline: selout outline, 3-step hue-shifted ramps,
no dither, silhouette-first. Every character is a draw(s, f) function.
"""
import sys, os
sys.path.insert(0, "/Users/game/.claude/skills/pixel-art-studio/scripts")
from pixelstudio import Sprite, ramp
from PIL import Image

OUT = "#2b1e21"
BOB = [0, -1, 0]           # standard idle bob per frame


# --- 1. ghost -------------------------------------------------------------
def ghost(s, f):
    B = ["#7e93c9", "#c3d3f0", "#eef4ff"]
    y = BOB[f]
    s.ellipse(8, 5 + y, 23, 22 + y, B[2])
    # wavy skirt
    for i, x in enumerate(range(8, 24, 3)):
        dy = (1 if (i + f) % 2 else 3)
        s.rect(x, 20 + y, x + 2, 24 + y + dy, B[2])
    s.ellipse(8, 14 + y, 14, 24 + y, B[1], only=B[2])
    s.ellipse(9, 6 + y, 18, 12 + y, "#ffffff", only=B[2])
    # face
    s.rect(12, 11 + y, 13, 14 + y, OUT); s.rect(18, 11 + y, 19, 14 + y, OUT)
    s.ellipse(14, 16 + y, 17, 18 + y, B[0])
    s.px(10, 15 + y, "#f4b8c4"); s.px(11, 15 + y, "#f4b8c4")
    s.outline(OUT, where="outside")


# --- 2. mushroom kid ------------------------------------------------------
def mushroom(s, f):
    CAP = ramp("#c94f43", 3); STEM = ["#d9c39a", "#f2e3c0"]
    sq = [0, 2, 0][f]
    s.ellipse(4, 6 + sq, 27, 18 + sq, CAP[1])
    s.ellipse(6, 6 + sq, 21, 11 + sq, CAP[2], only=CAP[1])
    s.line(5, 17 + sq, 26, 17 + sq, CAP[0])
    for x, y in ((9, 9), (17, 7), (22, 12)):
        s.ellipse(x, y + sq, x + 3, y + 2 + sq, "#f7efdd")
    # stem face
    s.rect(11, 18 + sq, 20, 27, STEM[1])
    s.ellipse(11, 24, 20, 27, STEM[0], only=STEM[1])
    s.rect(13, 20 + sq, 14, 22 + sq, OUT); s.rect(17, 20 + sq, 18, 22 + sq, OUT)
    s.line(15, 24 + sq // 2, 16, 24 + sq // 2, OUT)
    # feet
    s.rect(11, 27, 14, 29, STEM[0]); s.rect(17, 27, 20, 29, STEM[0])
    s.outline(OUT, where="outside")


# --- 3. robot -------------------------------------------------------------
def robot(s, f):
    M = ["#5d6b78", "#93a5b3", "#c5d3dc"]; T = "#59c8c0"
    y = BOB[f]
    # antenna
    s.line(16, 3 + y, 16, 6 + y, M[0]); s.px(16, 2 + y, T if f == 1 else "#f2f2f2")
    # head
    s.rect(9, 6 + y, 22, 15 + y, M[1])
    s.rect(10, 7 + y, 21, 9 + y, M[2])
    # visor eye: blink on f2
    if f == 2:
        s.rect(11, 11 + y, 20, 12 + y, OUT)
    else:
        s.rect(11, 10 + y, 20, 13 + y, OUT)
        s.rect(13, 11 + y, 15, 12 + y, T)
    # torso
    s.rect(11, 16 + y, 20, 24 + y, M[1])
    s.rect(11, 16 + y, 13, 24 + y, M[0])
    s.px(17, 18 + y, T); s.px(18, 18 + y, T)
    # arms
    s.rect(7, 17 + y, 9, 22 + y, M[0]); s.rect(22, 17 + y, 24, 22 + y, M[0])
    # hover thrusters instead of legs
    s.rect(12, 25 + y, 14, 26 + y, M[0]); s.rect(17, 25 + y, 19, 26 + y, M[0])
    for x in (13, 18):
        s.px(x, 27 + y + (f % 2), "#f2a341"); s.px(x, 28 + y + (f % 2), "#f7d060")
    s.outline(OUT, where="outside")


# --- 4. cat mage ----------------------------------------------------------
def catmage(s, f):
    HAT = ramp("#6b4f9e", 3); CAT = ["#8b8f9c", "#c0c4cf"]
    y = BOB[f]; tip = [0, 1, 0][f]
    # cat head
    s.ellipse(9, 14 + y, 22, 25 + y, CAT[1])
    # ears poking through
    s.polygon([(9, 15 + y), (8, 9 + y), (13, 13 + y)], CAT[1])
    s.polygon([(22, 15 + y), (23, 9 + y), (18, 13 + y)], CAT[1])
    # hat: brim + bent cone
    s.ellipse(6, 12 + y, 25, 16 + y, HAT[1])
    s.polygon([(10, 13 + y), (21, 13 + y), (17 + tip, 3 + y)], HAT[1])
    s.polygon([(12, 13 + y), (19, 13 + y), (17 + tip, 5 + y)], HAT[2])
    s.px(17 + tip, 2 + y, "#f7d060")  # star on tip
    s.line(7, 15 + y, 24, 15 + y, HAT[0])
    # face
    s.rect(12, 18 + y, 13, 20 + y, OUT); s.rect(18, 18 + y, 19, 20 + y, OUT)
    s.px(15, 21 + y, "#e89a9a"); s.px(16, 21 + y, "#e89a9a")
    s.line(10, 21 + y, 11, 21 + y, CAT[0]); s.line(20, 21 + y, 21, 21 + y, CAT[0])
    # robe
    s.polygon([(11, 25 + y), (20, 25 + y), (23, 30), (8, 30)], HAT[1])
    s.polygon([(11, 25 + y), (14, 25 + y), (12, 30), (8, 30)], HAT[0])
    s.outline(OUT, where="outside")


# --- 5. skeleton ----------------------------------------------------------
def skeleton(s, f):
    BONE = ["#a99e8d", "#ded4c2", "#f4eee0"]
    y = BOB[f]; tilt = [0, 0, 1][f]
    # skull: boxy cranium + narrower jaw
    s.ellipse(10 + tilt, 3 + y, 21 + tilt, 12 + y, BONE[2])
    s.rect(12 + tilt, 11 + y, 19 + tilt, 14 + y, BONE[1])   # jaw
    s.rect(11 + tilt, 7 + y, 13 + tilt, 9 + y, OUT)
    s.rect(18 + tilt, 7 + y, 20 + tilt, 9 + y, OUT)
    s.px(12 + tilt, 7 + y, "#f2a341"); s.px(19 + tilt, 7 + y, "#f2a341")  # ember eyes
    for x in (13, 15, 17):
        s.px(x + tilt, 12 + y, BONE[0])   # teeth gaps
    # ribcage: wide barrel with dark gaps between ribs
    s.ellipse(9, 15 + y, 22, 24 + y, BONE[1])
    for ry in (17, 19, 21):
        s.line(10, ry + y, 21, ry + y, OUT)
    s.line(15, 15 + y, 16, 24 + y, BONE[2])   # sternum
    # pelvis
    s.rect(11, 25 + y, 20, 26 + y, BONE[1])
    s.px(15, 26 + y, OUT); s.px(16, 26 + y, OUT)
    # arms: shoulder ball + hanging bone
    for ax in (7, 23):
        s.ellipse(ax - 1, 15 + y, ax + 1, 17 + y, BONE[2])
        s.rect(ax, 17 + y, ax + 1, 23 + y, BONE[1])
    # legs: two shin bones with knee balls
    for lx in (12, 18):
        s.rect(lx, 27, lx + 1, 29, BONE[1])
        s.px(lx, 27, BONE[2]); s.px(lx + 1, 27, BONE[2])
    s.outline(OUT, where="outside")


# --- 6. flame spirit --------------------------------------------------------
def flame(s, f):
    FI = ["#c93e2e", "#f2712e", "#f7b32e", "#fce97e"]
    lick = [0, 2, 1][f]
    s.polygon([(16, 3 + lick), (24, 14), (22, 25), (10, 25), (8, 14)], FI[1])
    s.polygon([(16, 8 + lick), (21, 16), (19, 24), (13, 24), (11, 16)], FI[2])
    s.polygon([(16, 13 + lick), (19, 18), (17, 23), (15, 23), (13, 18)], FI[3])
    # side licks
    s.px(9, 10 + lick * 2, FI[1]); s.px(8, 8 + lick * 2, FI[1])
    s.px(23, 9 - lick, FI[1]); s.px(24, 7 - lick, FI[1])
    # face
    s.rect(12, 15, 13, 17, OUT); s.rect(18, 15, 19, 17, OUT)
    s.line(15, 19, 16, 19, OUT)
    s.ellipse(12, 25, 20, 28, FI[0])   # ember base
    s.outline(FI[0], where="inside")


# --- 7. frog --------------------------------------------------------------
def frog(s, f):
    G = ramp("#5a9e3c", 3); TH = "#f2d9a4"
    puff = [0, 2, 0][f]
    # body squat
    s.ellipse(6, 12 - puff // 2, 25, 27, G[1])
    s.ellipse(8, 12, 23, 18, G[2], only=G[1])
    # eyes on top
    s.ellipse(7, 7, 13, 13, G[1]); s.ellipse(18, 7, 24, 13, G[1])
    s.ellipse(9, 9, 11, 11, OUT); s.ellipse(20, 9, 22, 11, OUT)
    s.px(9, 9, "#ffffff"); s.px(20, 9, "#ffffff")
    # throat puff grows on f2
    s.ellipse(11 - puff, 19 - puff, 20 + puff, 26 + puff // 2, TH)
    # mouth
    s.line(12, 16, 19, 16, G[0])
    # legs folded
    s.ellipse(4, 21, 10, 27, G[0]); s.ellipse(21, 21, 27, 27, G[0])
    s.rect(8, 27, 12, 29, G[1]); s.rect(19, 27, 23, 29, G[1])
    s.outline(OUT, where="outside")


# --- 8. penguin -----------------------------------------------------------
def penguin(s, f):
    K = ["#23303c", "#3c4f61"]; OR_ = "#f2913c"
    lean = [-1, 0, 1][f]
    s.ellipse(8 + lean, 5, 23 + lean, 28, K[1])
    s.ellipse(8 + lean, 5, 18 + lean, 24, K[0], only=K[1])
    # belly
    s.ellipse(12 + lean, 12, 22 + lean, 27, "#f0f4f7")
    # face
    s.rect(12 + lean, 8, 13 + lean, 10, OUT); s.rect(17 + lean, 8, 18 + lean, 10, OUT)
    s.px(12 + lean, 8, "#ffffff"); s.px(17 + lean, 8, "#ffffff")
    s.polygon([(14 + lean, 11), (17 + lean, 11), (15 + lean, 14)], OR_)
    # flippers
    s.ellipse(6 + lean, 13, 9 + lean, 22, K[0])
    s.ellipse(22 + lean, 13, 25 + lean, 22, K[0])
    # feet
    s.rect(11 + lean, 28, 14 + lean, 29, OR_); s.rect(17 + lean, 28, 20 + lean, 29, OR_)
    s.outline(OUT, where="outside")


# --- 9. bee ---------------------------------------------------------------
def bee(s, f):
    Y = ["#c98a2e", "#f2b93c", "#f7d060"]
    y = BOB[f]; wing = f % 2
    # wings
    wc = "#dcecf4"
    if wing:
        s.ellipse(8, 4 + y, 15, 10 + y, wc); s.ellipse(17, 4 + y, 24, 10 + y, wc)
    else:
        s.ellipse(6, 7 + y, 14, 11 + y, wc); s.ellipse(18, 7 + y, 26, 11 + y, wc)
    # body
    s.ellipse(7, 10 + y, 26, 24 + y, Y[1])
    s.ellipse(9, 11 + y, 20, 16 + y, Y[2], only=Y[1])
    for x0 in (11, 17, 23):
        s.rect(x0, 10 + y, x0 + 2, 24 + y, OUT, only=Y[1])
        s.rect(x0, 10 + y, x0 + 2, 24 + y, OUT, only=Y[2])
    # face
    s.rect(9, 15 + y, 10, 17 + y, OUT)
    s.px(12, 19 + y, "#e89a9a")
    # stinger + antennae
    s.polygon([(26, 16 + y), (29, 17 + y), (26, 19 + y)], OUT)
    s.line(10, 10 + y, 8, 7 + y, OUT); s.px(7, 6 + y, OUT)
    s.outline(OUT, where="outside")


# --- 10. moss golem ---------------------------------------------------------
def golem(s, f):
    R = ["#5a5f66", "#84898f", "#a8adb2"]; MOSS = "#6b9e4a"
    br = [0, 1, 0][f]
    # body boulder
    s.ellipse(5, 10 - br, 26, 28, R[1])
    s.ellipse(7, 10 - br, 20, 17, R[2], only=R[1])
    s.ellipse(5, 20, 14, 28, R[0], only=R[1])
    # moss cap + patches
    s.ellipse(8, 8 - br, 21, 12 - br, MOSS)
    s.px(22, 14 - br, MOSS); s.px(23, 15 - br, MOSS); s.px(8, 18, MOSS)
    # glow eyes (brighter mid-breath)
    ec = "#8fe0d0" if f == 1 else "#59c8c0"
    s.rect(11, 14 - br, 13, 16 - br, ec); s.rect(18, 14 - br, 20, 16 - br, ec)
    # crack + arm boulders
    s.line(15, 19, 17, 22, R[0]); s.px(16, 23, R[0])
    s.ellipse(2, 15 - br, 7, 24, R[1]); s.ellipse(24, 15 - br, 29, 24, R[1])
    # feet stubs
    s.rect(9, 28, 13, 29, R[0]); s.rect(19, 28, 23, 29, R[0])
    s.outline(OUT, where="outside")


CAST = [("ghost", ghost), ("mushroom", mushroom), ("robot", robot),
        ("catmage", catmage), ("skeleton", skeleton), ("flame", flame),
        ("frog", frog), ("penguin", penguin), ("bee", bee), ("golem", golem)]

here = os.path.dirname(os.path.abspath(__file__))
os.chdir(here)

sprites = {}
for name, fn in CAST:
    s = Sprite(32, 32)
    for f in range(3):
        if f:
            s.add_frame(copy=False)
            s.use(frame=f + 1)
        fn(s, f)
    s.set_duration(200, frames="all")
    s.save_gif(f"{name}.gif", scale=6)
    sprites[name] = s

# QA contact sheet: 5 cols x 2 rows, each cell = 3 frames side by side @4x
SC, FW = 4, 32
cell_w, cell_h = FW * 3 * SC + 12, FW * SC + 22
sheet = Image.new("RGBA", (cell_w * 5, cell_h * 2), (240, 236, 225, 255))
for i, (name, _) in enumerate(CAST):
    cx, cy = (i % 5) * cell_w, (i // 5) * cell_h
    for f in range(3):
        im = sprites[name].composite(f + 1).resize((FW * SC, FW * SC), Image.NEAREST)
        sheet.paste(im, (cx + f * FW * SC + 6, cy + 4), im)
sheet.save("cast_preview.png")
print("cast done:", ", ".join(n for n, _ in CAST))
