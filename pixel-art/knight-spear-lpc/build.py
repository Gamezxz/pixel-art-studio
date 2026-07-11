#!/usr/bin/env python3
"""Knight with a spear on the LPC universal sheet — walk + slash, 4 directions.

Same recipe as the cat mage: per-view draw functions + pose tables, assembled
onto the LPC grid by scripts/lpc.py. Steel armor ramp, spear thrust-swung as
the "slash" action (windup -> jab -> recover).
"""
import sys, os, math
sys.path.insert(0, "/Users/game/.claude/skills/pixel-art-studio/scripts")
from pixelstudio import Sprite, ramp
from lpc import LPCSheet
from PIL import Image

W = H = 40
OUT = "#231d1a"
STEEL = ramp("#7c8896", 3)          # dark..light armor
TRIM = ["#8a6a2e", "#c99a3e"]       # gold trim
SKIN = ["#c98a5e", "#e0aa7e"]
PLUME = ramp("#b5342e", 3)
WOOD = ["#6e4a2e", "#96683f"]
SPEARHEAD = ["#8f97a0", "#d3dbe2"]
SPARK = "#f2e6a8"


def spear(s, x0, y0, x1, y1, glint=0):
    """shaft (x0,y0) to tip (x1,y1); triangular head at the tip."""
    s.line(x0, y0, x1, y1, WOOD[1])
    s.line(x0 + 1, y0, x1 + 1, y1, WOOD[0])
    dx, dy = x1 - x0, y1 - y0
    L = max(1, math.hypot(dx, dy))
    ux, uy = dx / L, dy / L
    px_, py_ = -uy, ux
    tip = (x1 + ux * 8, y1 + uy * 8)
    base_l = (x1 + px_ * 3, y1 + py_ * 3)
    base_r = (x1 - px_ * 3, y1 - py_ * 3)
    s.polygon([tip, base_l, base_r], SPEARHEAD[0])
    s.polygon([tip, base_l, (x1, y1)], SPEARHEAD[1])
    if glint:
        gx, gy = int(x1 + ux * 4), int(y1 + uy * 4)
        if 0 <= gx < W and 0 <= gy < H:
            s.px(gx, gy, SPARK)


def helm_plume(s, hx, hy, wag=0):
    s.polygon([(hx - 2, hy - 6), (hx + 2, hy - 6), (hx + wag, hy - 14)], PLUME[1])
    s.polygon([(hx - 1, hy - 8), (hx + 1, hy - 8), (hx + wag, hy - 14)], PLUME[2])


def body_down(s, y, back=False, arm_l=(14, 26), arm_r=(26, 26)):
    # legs/boots
    s.rect(15, 32 + y, 18, 38, STEEL[0])
    s.rect(22, 32 + y, 25, 38, STEEL[0])
    # torso armor
    s.polygon([(13, 22 + y), (27, 22 + y), (29, 34), (11, 34)], STEEL[1])
    s.ellipse(15, 23 + y, 25, 30 + y, STEEL[2], only=STEEL[1])
    s.line(20, 22 + y, 20, 33, TRIM[0])
    for ty in (25, 29):
        s.px(15, ty + y, TRIM[1]); s.px(24, ty + y, TRIM[1])
    # pauldrons
    for ax, ay in (arm_l, arm_r):
        s.ellipse(ax - 3, ay + y - 3, ax + 3, ay + y + 3, STEEL[1])
        s.ellipse(ax - 3, ay + y - 3, ax + 1, ay + y + 1, STEEL[2], only=STEEL[1])
    # helm
    s.ellipse(13, 12 + y, 27, 24 + y, STEEL[1])
    s.ellipse(13, 12 + y, 21, 18 + y, STEEL[2], only=STEEL[1])
    helm_plume(s, 20, 13 + y)
    if not back:
        s.rect(14, 16 + y, 26, 19 + y, OUT)     # visor slit
        s.px(17, 17 + y, SKIN[1]); s.px(23, 17 + y, SKIN[1])
        s.line(17, 21 + y, 23, 21 + y, STEEL[0])
    else:
        s.line(15, 14 + y, 25, 14 + y, TRIM[0])  # back plate seam


def feet_down(s, lf, rf):
    s.rect(15, 36 - lf, 18, 38 - lf, STEEL[0])
    s.rect(22, 36 - rf, 25, 38 - rf, STEEL[0])


def frame_down(s, pose, back=False):
    y = pose["bob"]
    sp = pose.get("spear")
    feet_down(s, pose.get("lf", 0), pose.get("rf", 0))
    if back and sp:
        spear(s, *sp, glint=pose.get("glint", 0))
    body_down(s, y, back=back,
              arm_l=pose.get("arm_l", (14, 26)), arm_r=pose.get("arm_r", (26, 26)))
    if not back:
        if sp:
            spear(s, *sp, glint=pose.get("glint", 0))
        else:
            spear(s, 29, 36 + y, 30, 8 + y)
    elif not sp:
        spear(s, 11, 36 + y, 10, 8 + y)
    s.outline(OUT, where="outside")


def frame_side(s, pose):
    """faces RIGHT"""
    y = pose["bob"]
    fl, bl = pose.get("fl", 0), pose.get("bl", 0)
    sp = pose.get("spear")
    lean = pose.get("lean", 0)
    # far leg
    s.rect(17 + bl, 32, 20 + bl, 38, STEEL[0])
    # torso
    s.polygon([(14 + lean, 22 + y), (26 + lean, 22 + y), (28, 34), (13, 34)], STEEL[1])
    s.ellipse(16 + lean, 23 + y, 25 + lean, 30 + y, STEEL[2], only=STEEL[1])
    s.line(21 + lean, 22 + y, 20, 34, TRIM[0])
    # near leg
    s.rect(20 + fl, 32, 23 + fl, 38, STEEL[1])
    # helm
    s.ellipse(13 + lean, 12 + y, 27 + lean, 24 + y, STEEL[1])
    s.ellipse(13 + lean, 12 + y, 21 + lean, 18 + y, STEEL[2], only=STEEL[1])
    helm_plume(s, 20 + lean, 13 + y, wag=pose.get("wag", 0))
    s.rect(21 + lean, 16 + y, 26 + lean, 19 + y, OUT)
    s.px(25 + lean, 17 + y, SKIN[1])
    # arm + spear
    ax, ay = pose.get("arm", (24 + lean, 27))
    s.ellipse(ax - 3, ay + y - 3, ax + 3, ay + y + 3, STEEL[1])
    if sp:
        spear(s, *sp, glint=pose.get("glint", 0))
    else:
        spear(s, ax + 3, ay + y + 10, ax + 4, ay + y - 14)
    s.outline(OUT, where="outside")


# ---- pose tables ----------------------------------------------------------
def walk_poses():
    dn = [dict(bob=0)]
    side = [dict(bob=0)]
    lf_seq = [2, 1, 0, 0, 0, 0, 0, 1]
    rf_seq = [0, 0, 0, 1, 2, 1, 0, 0]
    bob_sq = [0, -1, -1, 0, 0, -1, -1, 0]
    fl_seq = [3, 2, 0, -2, -3, -2, 0, 2]
    for f in range(8):
        dn.append(dict(bob=bob_sq[f], lf=lf_seq[f], rf=rf_seq[f]))
        side.append(dict(bob=bob_sq[f], fl=fl_seq[f], bl=-fl_seq[f], wag=fl_seq[f] // 3))
    return dn, side


def slash_poses():
    """spear jab: windup 0-1 (pull back), thrust 2-3 (glint on contact), recover 4-5."""
    dn = [
        dict(bob=0, spear=(24, 36, 30, 10), arm_r=(27, 24)),
        dict(bob=1, spear=(22, 38, 32, 14), arm_r=(28, 22)),
        dict(bob=0, spear=(20, 18, 14, 34), arm_r=(24, 22), glint=1),
        dict(bob=0, spear=(18, 16, 11, 33), arm_r=(23, 21), glint=1),
        dict(bob=1, spear=(21, 22, 20, 35), arm_r=(26, 23)),
        dict(bob=0, spear=(23, 30, 28, 20), arm_r=(27, 24)),
    ]
    side = [
        dict(bob=0, lean=-1, spear=(14, 34, 4, 30), arm=(18, 27)),
        dict(bob=1, lean=-2, spear=(12, 32, -2, 30), arm=(17, 28)),
        dict(bob=0, lean=2, spear=(24, 27, 40, 27), arm=(26, 26), glint=1),
        dict(bob=0, lean=3, spear=(26, 27, 42, 27), arm=(27, 26), glint=1),
        dict(bob=1, lean=1, spear=(22, 28, 34, 28), arm=(25, 27)),
        dict(bob=0, lean=0, spear=(20, 29, 30, 29), arm=(24, 27)),
    ]
    return dn, side


def render(kind, pose):
    s = Sprite(W, H)
    if kind == "down":
        frame_down(s, pose)
    elif kind == "up":
        frame_down(s, pose, back=True)
    else:
        frame_side(s, pose)
    im = s.composite(1)
    if kind == "left":
        im = im.transpose(Image.FLIP_LEFT_RIGHT)
    return im


here = os.path.dirname(os.path.abspath(__file__))
os.chdir(here)

wd, ws = walk_poses()
sd, ss = slash_poses()
POSES = {"walk": {"down": wd, "up": wd, "left": ws, "right": ws},
         "slash": {"down": sd, "up": sd, "left": ss, "right": ss}}

sheet = LPCSheet()
for action, per_dir in POSES.items():
    for d, poses in per_dir.items():
        for f, pose in enumerate(poses):
            sheet.place(action, d, f, render(d, pose))
sheet.save("knight_spear_lpc.png")
for a, d in (("walk", "down"), ("walk", "right"), ("slash", "right"), ("slash", "down")):
    sheet.gif(f"knight_{a}_{d}.gif", a, d, scale=3, skip_idle=True)

im = Image.open("knight_spear_lpc.png")
qa = Image.new("RGBA", (13 * 64, 8 * 64), (240, 236, 225, 255))
qa.paste(im.crop((0, 8 * 64, 13 * 64, 12 * 64)), (0, 0))
qa.paste(im.crop((0, 12 * 64, 13 * 64, 16 * 64)), (0, 4 * 64))
qa.resize((qa.width * 2, qa.height * 2), Image.NEAREST).save("qa.png")
print("done")
