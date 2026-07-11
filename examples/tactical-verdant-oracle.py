import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "scripts"))
from pixelstudio import Sprite

OUT = os.path.join(ROOT, "pixel-art", "tactical-verdant-oracle")

INK = "#1c1720"
INK_L = "#302638"
HOOD_D = "#244044"
HOOD = "#38625d"
HOOD_L = "#5e8a78"
TRIM_D = "#71502f"
TRIM = "#b48245"
TRIM_H = "#e2bd6c"
HAIR_D = "#713a32"
HAIR = "#aa5943"
HAIR_H = "#e18a63"
SKIN_D = "#a66e5b"
SKIN = "#d9a27f"
SKIN_H = "#f2cf9c"
BOOT_D = "#49342b"
BOOT = "#654035"
GEM = "#66b7ba"
GEM_H = "#c1eee0"
PAL = [INK, INK_L, HOOD_D, HOOD, HOOD_L, TRIM_D, TRIM, TRIM_H,
       HAIR_D, HAIR, HAIR_H, SKIN_D, SKIN, SKIN_H, BOOT_D, BOOT, GEM, GEM_H]


def staff(s, x, y, tilt=0):
    # Crooked ash staff with a turquoise oracle stone.
    s.line(x, y + 4, x + tilt, y + 31, INK)
    s.line(x - 1, y + 5, x + tilt - 1, y + 30, TRIM_D)
    s.line(x, y + 6, x + tilt, y + 29, TRIM)
    s.polygon([(x - 4, y + 4), (x - 3, y), (x, y - 3),
               (x + 4, y), (x + 5, y + 4), (x + 1, y + 7),
               (x - 3, y + 7)], INK)
    s.polygon([(x - 2, y + 3), (x - 1, y), (x + 1, y - 1),
               (x + 3, y + 2), (x + 2, y + 5), (x - 1, y + 5)], GEM)
    s.px(x, y, GEM_H)
    s.px(x - 1, y + 1, GEM_H)


def oracle(s, x=28, ground=51, bob=0, hand=0, blink=False):
    y = ground - 43 + bob

    # Staff behind the near arm.
    staff(s, x + 15 + hand, y + 5, tilt=-hand)

    # Far cloak-tail and far boot: darker/smaller for 3/4 depth.
    s.polygon([(x - 9, y + 28), (x - 15, y + 37), (x - 12, y + 43),
               (x - 4, y + 39), (x, y + 31)], INK)
    s.polygon([(x - 9, y + 30), (x - 12, y + 37), (x - 9, y + 40),
               (x - 3, y + 37), (x - 1, y + 31)], HOOD_D)
    s.polygon([(x - 7, y + 37), (x - 9, ground - 4), (x - 13, ground - 3),
               (x - 14, ground - 1), (x - 7, ground - 1), (x - 3, y + 38)], INK)
    s.rect(x - 12, ground - 4, x - 7, ground - 2, BOOT_D)

    # Far arm must remain explicitly readable: smaller, darker, and behind the torso.
    far_hx, far_hy = x - 13 - hand, y + 29
    s.polygon([(x - 7, y + 23), (x - 12, y + 23), (far_hx - 3, far_hy),
               (far_hx - 2, far_hy + 5), (far_hx + 3, far_hy + 5),
               (x - 5, y + 28)], INK)
    s.polygon([(x - 8, y + 24), (x - 11, y + 25), (far_hx - 1, far_hy + 1),
               (far_hx, far_hy + 3), (far_hx + 2, far_hy + 3),
               (x - 5, y + 27)], HOOD_D)
    s.polygon([(far_hx - 2, far_hy + 2), (far_hx + 1, far_hy + 1),
               (far_hx + 3, far_hy + 3), (far_hx + 1, far_hy + 6),
               (far_hx - 2, far_hy + 5)], INK)
    s.rect(far_hx - 1, far_hy + 2, far_hx + 1, far_hy + 4, SKIN_D)

    # Main robe mass with tapered waist and broad lower hem.
    s.polygon([(x - 9, y + 23), (x + 7, y + 21), (x + 11, y + 33),
               (x + 8, y + 42), (x - 5, y + 42), (x - 11, y + 34)], INK)
    s.polygon([(x - 7, y + 24), (x + 5, y + 23), (x + 8, y + 32),
               (x + 6, y + 39), (x - 4, y + 39), (x - 8, y + 33)], HOOD)
    s.polygon([(x - 7, y + 24), (x - 1, y + 23), (x - 2, y + 36),
               (x - 6, y + 38), (x - 8, y + 32)], HOOD_L)
    s.polygon([(x + 3, y + 24), (x + 6, y + 25), (x + 8, y + 33),
               (x + 5, y + 39), (x + 2, y + 35)], HOOD_D)
    # Structural trim, not every seam.
    s.line(x - 7, y + 25, x + 5, y + 23, TRIM_H)
    s.line(x - 6, y + 26, x - 3, y + 38, TRIM)
    s.line(x - 4, y + 39, x + 6, y + 39, TRIM)
    s.rect(x - 2, y + 30, x + 1, y + 33, INK_L)
    s.px(x, y + 31, GEM_H)

    # Large near boot projects down-right.
    s.polygon([(x + 1, y + 37), (x + 8, y + 36), (x + 11, ground - 5),
               (x + 16, ground - 3), (x + 16, ground - 1), (x + 5, ground),
               (x + 2, ground - 3)], INK)
    s.polygon([(x + 5, y + 39), (x + 8, y + 39), (x + 9, ground - 5),
               (x + 14, ground - 4), (x + 14, ground - 2), (x + 6, ground - 2),
               (x + 4, ground - 4)], BOOT)
    s.rect(x + 8, ground - 4, x + 13, ground - 3, TRIM_D)

    # Hood silhouette: deep rear wedge, asymmetric crown and open face.
    s.polygon([(x - 13, y + 4), (x - 7, y - 1), (x + 3, y),
               (x + 11, y + 6), (x + 13, y + 15), (x + 9, y + 24),
               (x + 3, y + 28), (x - 8, y + 26), (x - 14, y + 18)], INK)
    s.polygon([(x - 11, y + 5), (x - 6, y + 1), (x + 2, y + 2),
               (x + 9, y + 7), (x + 10, y + 15), (x + 7, y + 22),
               (x + 2, y + 25), (x - 6, y + 24), (x - 11, y + 17)], HOOD)
    s.polygon([(x - 10, y + 5), (x - 5, y + 2), (x + 1, y + 3),
               (x - 2, y + 7), (x - 8, y + 12), (x - 11, y + 15)], HOOD_L)
    s.polygon([(x + 4, y + 4), (x + 8, y + 8), (x + 9, y + 16),
               (x + 6, y + 22), (x + 3, y + 20)], HOOD_D)
    # Selective golden hood rim.
    s.line(x - 9, y + 5, x - 12, y + 16, TRIM)
    s.line(x - 12, y + 17, x - 6, y + 24, TRIM_H)
    s.line(x - 5, y + 24, x + 3, y + 25, TRIM)

    # Face plane, warm and minimal.
    s.polygon([(x - 6, y + 10), (x + 4, y + 8), (x + 7, y + 13),
               (x + 5, y + 21), (x, y + 24), (x - 6, y + 20),
               (x - 8, y + 14)], INK)
    s.polygon([(x - 5, y + 11), (x + 3, y + 10), (x + 5, y + 14),
               (x + 3, y + 20), (x, y + 22), (x - 5, y + 19),
               (x - 6, y + 14)], SKIN)
    s.polygon([(x - 5, y + 11), (x + 1, y + 10), (x, y + 14),
               (x - 5, y + 16)], SKIN_H)
    s.px(x + 4, y + 19, SKIN_D)

    # Auburn side fringe, distinct from the silver-haired reference.
    s.polygon([(x - 7, y + 7), (x - 2, y + 4), (x + 4, y + 7),
               (x + 2, y + 12), (x - 1, y + 15), (x - 3, y + 10),
               (x - 7, y + 13)], INK)
    s.polygon([(x - 6, y + 8), (x - 2, y + 6), (x + 2, y + 8),
               (x + 1, y + 10), (x - 1, y + 13), (x - 2, y + 9),
               (x - 6, y + 11)], HAIR)
    s.rect(x - 4, y + 7, x - 1, y + 8, HAIR_H)

    # Repaint both eyes after the fringe so neither disappears under the hair layer.
    # The far eye is one pixel smaller/darker to preserve the three-quarter view.
    if blink:
        s.line(x - 2, y + 15, x, y + 15, INK)
        s.line(x + 2, y + 15, x + 3, y + 15, INK)
    else:
        s.rect(x - 2, y + 14, x - 1, y + 16, INK)
        s.px(x - 1, y + 14, GEM_H)
        s.rect(x + 2, y + 14, x + 3, y + 16, INK)
        s.px(x + 3, y + 14, GEM_H)

    # Oversized near sleeve and hand, brighter than far side.
    hx, hy = x + 11 + hand, y + 28
    s.polygon([(x + 5, y + 24), (x + 11, y + 23), (hx + 4, hy - 1),
               (hx + 2, hy + 6), (hx - 4, hy + 5), (x + 4, y + 29)], INK)
    s.polygon([(x + 7, y + 25), (x + 10, y + 25), (hx + 2, hy),
               (hx + 1, hy + 3), (hx - 2, hy + 3), (x + 5, y + 28)], HOOD_D)
    s.polygon([(hx, hy - 1), (hx + 4, hy), (hx + 4, hy + 4),
               (hx + 1, hy + 6), (hx - 2, hy + 3)], INK)
    s.polygon([(hx + 1, hy), (hx + 3, hy + 1), (hx + 3, hy + 3),
               (hx + 1, hy + 4), (hx - 1, hy + 3)], SKIN)
    s.px(hx + 1, hy, SKIN_H)


def build():
    s = Sprite(64, 58, palette=PAL)
    poses = [(0, 0, False, 260), (-1, 1, False, 220), (0, 0, True, 90), (-1, -1, False, 220)]
    for i, (bob, hand, blink, duration) in enumerate(poses):
        if i:
            s.add_frame(copy=False)
        oracle(s, x=29, ground=53, bob=bob, hand=hand, blink=blink)
        s.set_duration(duration)
    s.tag("idle", 1, 4, "pingpong")
    s.preview(os.path.join(OUT, "tactical_oracle_preview.png"), scale=7, cols=4)
    s.save_silhouette(os.path.join(OUT, "tactical_oracle_silhouette.png"))
    s.save_png(os.path.join(OUT, "tactical_oracle_master.png"), frame=1)
    s.save_png(os.path.join(OUT, "tactical_oracle_display.png"), frame=1, scale=8, bg="#ece6d8")
    s.save_gif(os.path.join(OUT, "tactical_oracle_idle.gif"), scale=8, tag="idle")
    s.save_gif(os.path.join(OUT, "tactical_oracle_idle_display.gif"), scale=8, tag="idle", bg="#ece6d8")
    s.save_spritesheet(os.path.join(OUT, "tactical_oracle_sheet.png"), layout="horizontal", padding=2)
    return s


def validate(s):
    boxes, edge = [], []
    for f in range(1, s.n_frames + 1):
        box = s.composite(f).getbbox()
        boxes.append(box)
        if box and (box[0] < 2 or box[1] < 2 or box[2] > s.w - 2 or box[3] > s.h - 2):
            edge.append(f)
    return {"canvas": [s.w, s.h], "pivot": [29, 53], "bounds": boxes,
            "edge_failures": edge, "palette_budget": len(PAL)}


s = build()
s.stats()
report = validate(s)
with open(os.path.join(OUT, "tactical_oracle_validation.json"), "w", encoding="utf-8") as f:
    json.dump(report, f, indent=2)
print(json.dumps(report, indent=2))
