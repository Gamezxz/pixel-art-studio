#!/usr/bin/env python3
"""Cat mage on the LPC universal sheet — walk + slash, all four directions.

Chibi (~34px) from the anime cast, drawn per-view with pose tables, assembled
by scripts/lpc.py. Staff swings with a sparkle arc on the slash contact frames.
"""
import sys, os, math
sys.path.insert(0, "/Users/game/.claude/skills/pixel-art-studio/scripts")
from pixelstudio import Sprite, ramp
from lpc import LPCSheet
from PIL import Image

# All body/pose coordinates below are unchanged (same character size). We just
# draw them onto a bigger scratch canvas, translated by OFFX/OFFY, so a staff
# reaching far left/up/right never gets clipped by an undersized canvas. lpc.py
# then crops the tight bbox and centers it in the real 64px cell.
W = H = 40                      # logical coordinate space the poses were authored in
OFFX, OFFY = 28, 26
SCRATCH = 96
OUT = "#2b1e21"
HAT = ramp("#6b4f9e", 3)
CAT = ["#8b8f9c", "#c0c4cf", "#e3e6ee"]
STAR = "#f7d060"
WOOD = ["#6e4a2e", "#96683f"]
ORB = ["#2e8f88", "#59c8c0", "#b7ece6"]
PINK = "#e89a9a"


class Canvas:
    """Translates every draw call by (OFFX, OFFY) onto a larger scratch Sprite,
    so build code below can keep authoring in its original 0..40 coordinate
    space without any pose reaching a negative or off-canvas value."""
    def __init__(self, w, h):
        self.s = Sprite(w, h)

    def px(self, x, y, color, only=None):
        self.s.px(x + OFFX, y + OFFY, color, only=only)

    def line(self, x0, y0, x1, y1, color, only=None):
        self.s.line(x0 + OFFX, y0 + OFFY, x1 + OFFX, y1 + OFFY, color, only=only)

    def rect(self, x0, y0, x1, y1, color, fill=True, only=None):
        self.s.rect(x0 + OFFX, y0 + OFFY, x1 + OFFX, y1 + OFFY, color, fill=fill, only=only)

    def ellipse(self, x0, y0, x1, y1, color, fill=True, only=None):
        self.s.ellipse(x0 + OFFX, y0 + OFFY, x1 + OFFX, y1 + OFFY, color, fill=fill, only=only)

    def polygon(self, points, color, fill=True, only=None):
        self.s.polygon([(x + OFFX, y + OFFY) for x, y in points], color, fill=fill, only=only)

    def outline(self, color, where="outside", diagonals=False):
        self.s.outline(color, where=where, diagonals=diagonals)

    def composite(self, frame=None):
        return self.s.composite(frame)


def staff(s, x0, y0, x1, y1, spark=0):
    """staff from butt (x0,y0) to orb (x1,y1)"""
    s.line(x0, y0, x1, y1, WOOD[1])
    s.line(x0 + 1, y0, x1 + 1, y1, WOOD[0])
    s.ellipse(x1 - 2, y1 - 2, x1 + 2, y1 + 2, ORB[1])
    s.px(x1 - 1, y1 - 1, ORB[2])
    if spark:
        for i in range(3):
            a = math.radians(i * 120 + spark * 45)
            sx, sy = int(x1 + 5 * math.cos(a)), int(y1 + 5 * math.sin(a))
            s.px(sx, sy, ORB[2] if i % 2 else STAR)


def body_down(s, y, hx=20, back=False, arm_l=(16, 26), arm_r=(24, 26)):
    """front/back torso: robe, head, hat. arms = sleeve端 (x, y)."""
    # robe
    s.polygon([(14, 24 + y), (26, 24 + y), (29, 36), (11, 36)], HAT[1])
    s.polygon([(14, 24 + y), (17, 24 + y), (15, 36), (11, 36)], HAT[0])
    # sleeves
    for ax, ay in (arm_l, arm_r):
        s.ellipse(ax - 2, ay + y - 2, ax + 2, ay + y + 2, HAT[1])
    # head
    s.ellipse(13, 13 + y, 27, 25 + y, CAT[1])
    s.polygon([(13, 14 + y), (12, 8 + y), (17, 12 + y)], CAT[1])
    s.polygon([(27, 14 + y), (28, 8 + y), (23, 12 + y)], CAT[1])
    # hat
    s.ellipse(10, 11 + y, 30, 15 + y, HAT[1])
    s.polygon([(14, 12 + y), (25, 12 + y), (21, 2 + y)], HAT[1])
    s.polygon([(16, 12 + y), (23, 12 + y), (21, 4 + y)], HAT[2])
    s.px(21, 1 + y, STAR)
    s.line(11, 14 + y, 29, 14 + y, HAT[0])
    if not back:
        s.rect(16, 17 + y, 17, 19 + y, OUT); s.rect(22, 17 + y, 23, 19 + y, OUT)
        s.px(19, 20 + y, PINK); s.px(20, 20 + y, PINK)
        s.line(14, 20 + y, 15, 20 + y, CAT[0]); s.line(24, 20 + y, 25, 20 + y, CAT[0])
    else:
        s.ellipse(16, 16 + y, 24, 22 + y, CAT[0], only=CAT[1])   # back of head shading


def feet_down(s, lf, rf):
    s.rect(15, 36 - lf, 18, 38 - lf, CAT[1])
    s.rect(22, 36 - rf, 25, 38 - rf, CAT[1])


def frame_down(s, pose, back=False):
    y = pose["bob"]
    st = pose.get("staff")          # (x0,y0,x1,y1) or None -> held at side
    feet_down(s, pose.get("lf", 0), pose.get("rf", 0))
    if back and st:
        staff(s, *st, spark=pose.get("spark", 0))
    body_down(s, y, back=back,
              arm_l=pose.get("arm_l", (14, 26)), arm_r=pose.get("arm_r", (26, 26)))
    if not back:
        if st:
            staff(s, *st, spark=pose.get("spark", 0))
        else:
            staff(s, 30, 34 + y, 31, 16 + y)
    elif not st:
        staff(s, 10, 34 + y, 9, 16 + y)
    s.outline(OUT, where="outside")


def frame_side(s, pose):
    """faces RIGHT"""
    y = pose["bob"]
    fl, bl = pose.get("fl", 0), pose.get("bl", 0)    # front/back leg dx
    st = pose.get("staff")
    # far leg
    s.rect(17 + bl, 34, 20 + bl, 38, CAT[0])
    # robe (slight forward lean while slashing)
    lean = pose.get("lean", 0)
    s.polygon([(15 + lean, 24 + y), (25 + lean, 24 + y), (28, 36), (13, 36)], HAT[1])
    s.polygon([(15 + lean, 24 + y), (18 + lean, 24 + y), (16, 36), (13, 36)], HAT[0])
    # near leg
    s.rect(20 + fl, 34, 23 + fl, 38, CAT[1])
    # head
    s.ellipse(13 + lean, 13 + y, 27 + lean, 25 + y, CAT[1])
    s.polygon([(15 + lean, 14 + y), (14 + lean, 8 + y), (19 + lean, 12 + y)], CAT[1])
    # hat
    s.ellipse(10 + lean, 11 + y, 30 + lean, 15 + y, HAT[1])
    s.polygon([(14 + lean, 12 + y), (25 + lean, 12 + y), (18 + lean, 2 + y)], HAT[1])
    s.polygon([(16 + lean, 12 + y), (23 + lean, 12 + y), (18 + lean, 4 + y)], HAT[2])
    s.px(17 + lean, 1 + y, STAR)
    s.line(11 + lean, 14 + y, 29 + lean, 14 + y, HAT[0])
    # face (right side)
    s.rect(22 + lean, 17 + y, 23 + lean, 19 + y, OUT)
    s.px(25 + lean, 20 + y, PINK)
    s.line(26 + lean, 21 + y, 27 + lean, 21 + y, CAT[0])
    # sleeve + staff
    ax, ay = pose.get("arm", (24 + lean, 27))
    if st:
        staff(s, *st, spark=pose.get("spark", 0))
    else:
        staff(s, ax + 6, ay + y + 8, ax + 8, ay + y - 9)
    s.ellipse(ax - 2, ay + y - 2, ax + 3, ay + y + 3, HAT[1])
    s.outline(OUT, where="outside")


# ---- pose tables ----------------------------------------------------------
def walk_poses():
    """9 poses (idle + 8-frame cycle) for down/up and side views."""
    dn = [dict(bob=0)]
    side = [dict(bob=0)]
    # cycle: contacts f1/f5, passing f3/f7
    lf_seq = [2, 1, 0, 0, 0, 0, 0, 1]     # left foot lift (down view)
    rf_seq = [0, 0, 0, 1, 2, 1, 0, 0]
    bob_sq = [0, -1, -1, 0, 0, -1, -1, 0]
    fl_seq = [3, 2, 0, -2, -3, -2, 0, 2]  # side view near-leg swing
    for f in range(8):
        dn.append(dict(bob=bob_sq[f], lf=lf_seq[f], rf=rf_seq[f]))
        side.append(dict(bob=bob_sq[f], fl=fl_seq[f], bl=-fl_seq[f]))
    return dn, side


def slash_poses():
    """6 poses: windup 0-1, swing 2-3 (spark), follow 4-5."""
    # down view: staff sweeps right->left across the front
    dn = [
        dict(bob=0,  staff=(28, 30, 33, 10), arm_r=(27, 26)),
        dict(bob=1,  staff=(29, 28, 36, 14), arm_r=(28, 25)),
        dict(bob=0,  staff=(24, 26, 20, 4),  arm_r=(24, 24), spark=1),
        dict(bob=0,  staff=(18, 26, 6, 10),  arm_l=(16, 24), spark=2),
        dict(bob=1,  staff=(16, 28, 5, 18),  arm_l=(14, 25)),
        dict(bob=0,  staff=(16, 30, 6, 24),  arm_l=(14, 26)),
    ]
    # side view: big forward arc
    side = [
        dict(bob=0, lean=-1, staff=(22, 28, 10, 12), arm=(20, 26)),
        dict(bob=1, lean=-2, staff=(22, 29, 8, 16),  arm=(19, 27)),
        dict(bob=0, lean=1,  staff=(24, 24, 30, 4),  arm=(25, 25), spark=1),
        dict(bob=0, lean=2,  staff=(26, 26, 38, 18), arm=(27, 26), spark=2),
        dict(bob=1, lean=1,  staff=(26, 28, 37, 26), arm=(26, 27)),
        dict(bob=0, lean=0,  staff=(25, 29, 34, 30), arm=(25, 27)),
    ]
    return dn, side


def render(kind, pose):
    s = Canvas(SCRATCH, SCRATCH)
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
sheet.save("catmage_lpc.png")
for a, d in (("walk", "down"), ("walk", "right"), ("slash", "right"), ("slash", "down")):
    sheet.gif(f"catmage_{a}_{d}.gif", a, d, scale=3, skip_idle=True)

# QA sheet: walk rows + slash rows cropped @2x
im = Image.open("catmage_lpc.png")
qa = Image.new("RGBA", (13 * 64, 8 * 64), (240, 236, 225, 255))
qa.paste(im.crop((0, 8 * 64, 13 * 64, 12 * 64)), (0, 0))          # walk rows
qa.paste(im.crop((0, 12 * 64, 13 * 64, 16 * 64)), (0, 4 * 64))    # slash rows
qa.resize((qa.width * 2, qa.height * 2), Image.NEAREST).save("qa.png")
print("done")
