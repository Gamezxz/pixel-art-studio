import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "scripts"))
from pixelstudio import Sprite

OUT = os.path.join(ROOT, "pixel-art", "tall-iron-man-repulsor")

INK = "#1b1722"
RED_D = "#641d2a"
RED = "#a52b2f"
RED_L = "#df4938"
RED_H = "#ff7650"
GOLD_D = "#8c542c"
GOLD = "#d18a38"
GOLD_L = "#f4c85a"
GOLD_H = "#fff09a"
METAL_D = "#354657"
METAL = "#668096"
CYAN_D = "#277d8c"
CYAN = "#55d6d0"
CYAN_H = "#d8fff3"
WHITE = "#fffbe8"
PAL = [INK, RED_D, RED, RED_L, RED_H, GOLD_D, GOLD, GOLD_L, GOLD_H,
       METAL_D, METAL, CYAN_D, CYAN, CYAN_H, WHITE]


def beam(s, palm, length, phase):
    """Connected repulsor beam clusters with a bright core and tapered endpoint."""
    px, py = palm
    if length <= 0:
        s.polygon([(px - 2, py - 2), (px + 2, py - 2), (px + 3, py),
                   (px + 2, py + 2), (px - 2, py + 2), (px - 3, py)], CYAN)
        s.rect(px - 1, py - 1, px + 1, py + 1, WHITE)
        return
    end = px + length
    # Outer glow uses staggered solid clusters rather than alpha.
    s.polygon([(px, py - 4), (end - 5, py - 3), (end, py),
               (end - 5, py + 3), (px, py + 4)], CYAN_D)
    s.polygon([(px, py - 2), (end - 3, py - 2), (end + 2, py),
               (end - 3, py + 2), (px, py + 2)], CYAN)
    s.rect(px, py - 1, end - 1, py + 1, CYAN_H)
    s.line(px + 2, py, end + 1, py, WHITE)
    # Traveling energy ticks make motion visible without dither shimmer.
    tick = px + 7 + (phase * 7) % max(8, length - 7)
    if tick < end - 2:
        s.rect(tick, py - 3, tick + 2, py + 3, CYAN_H)
        s.line(tick + 1, py - 2, tick + 1, py + 2, WHITE)


def armor_segment(s, a, b, inner, half_width=3):
    """A filled armored limb segment; never use a 1px line for anatomy."""
    ax, ay = a
    bx, by = b
    dx, dy = bx - ax, by - ay
    mag = max(1, (dx * dx + dy * dy) ** 0.5)
    px = round(-dy / mag * half_width)
    py = round(dx / mag * half_width)
    s.polygon([(ax + px, ay + py), (bx + px, by + py),
               (bx - px, by - py), (ax - px, ay - py)], INK)
    iw = max(1, half_width - 1)
    qx = round(-dy / mag * iw)
    qy = round(dx / mag * iw)
    s.polygon([(ax + qx, ay + qy), (bx + qx, by + qy),
               (bx - qx, by - qy), (ax - qx, ay - qy)], inner)


def iron_man(s, x=34, ground=67, bob=0, pose="charge", recoil=0):
    """Tall tactical 3/4 armored hero: ~4.4 heads high, stable foot pivot."""
    y = ground - 60 + bob
    x -= recoil

    # Far leg first: smaller/darker but explicitly present.
    s.polygon([(x - 7, y + 39), (x - 1, y + 38), (x, y + 51),
               (x - 2, ground - 4), (x - 9, ground - 4), (x - 10, y + 49)], INK)
    s.polygon([(x - 6, y + 40), (x - 2, y + 40), (x - 2, y + 50),
               (x - 4, ground - 6), (x - 8, ground - 6), (x - 8, y + 48)], RED_D)
    s.polygon([(x - 8, ground - 7), (x - 3, ground - 7), (x - 1, ground - 3),
               (x - 3, ground - 1), (x - 11, ground - 1), (x - 11, ground - 4)], INK)
    s.rect(x - 9, ground - 6, x - 3, ground - 3, RED)
    s.line(x - 8, ground - 6, x - 4, ground - 6, RED_L)
    s.rect(x - 10, ground - 5, x - 7, ground - 3, GOLD)
    s.px(x - 9, ground - 5, GOLD_H)

    # Pelvis and narrow armored waist.
    s.polygon([(x - 9, y + 33), (x + 7, y + 32), (x + 10, y + 40),
               (x + 5, y + 44), (x - 6, y + 43), (x - 11, y + 39)], INK)
    s.polygon([(x - 7, y + 34), (x + 5, y + 34), (x + 7, y + 39),
               (x + 3, y + 41), (x - 5, y + 41), (x - 8, y + 38)], GOLD_D)
    s.polygon([(x - 5, y + 34), (x + 3, y + 34), (x + 4, y + 37),
               (x + 1, y + 39), (x - 4, y + 38)], GOLD)
    s.rect(x - 4, y + 31, x + 4, y + 34, RED_D)

    # Near leg: longer, brighter, knee and boot separated.
    s.polygon([(x + 1, y + 40), (x + 9, y + 38), (x + 12, y + 51),
               (x + 15, ground - 6), (x + 13, ground - 2), (x + 4, ground - 1),
               (x + 1, y + 51)], INK)
    s.polygon([(x + 3, y + 41), (x + 8, y + 40), (x + 9, y + 49),
               (x + 12, ground - 7), (x + 10, ground - 5), (x + 5, ground - 5),
               (x + 3, y + 50)], RED)
    s.polygon([(x + 5, y + 42), (x + 8, y + 41), (x + 9, y + 47),
               (x + 5, y + 47)], RED_L)
    s.polygon([(x + 9, ground - 8), (x + 14, ground - 7), (x + 17, ground - 4),
               (x + 16, ground - 1), (x + 6, ground - 1), (x + 5, ground - 4)], INK)
    s.polygon([(x + 10, ground - 7), (x + 13, ground - 6), (x + 15, ground - 4),
               (x + 14, ground - 3), (x + 7, ground - 3), (x + 7, ground - 5)], RED)
    s.polygon([(x + 12, ground - 6), (x + 15, ground - 4), (x + 14, ground - 3),
               (x + 11, ground - 3), (x + 10, ground - 5)], GOLD)
    s.line(x + 12, ground - 6, x + 14, ground - 4, GOLD_H)

    # Torso: broad shoulders, narrow waist, layered red/gold plates.
    s.polygon([(x - 12, y + 18), (x - 7, y + 13), (x + 7, y + 12),
               (x + 14, y + 18), (x + 12, y + 31), (x + 6, y + 36),
               (x - 7, y + 35), (x - 13, y + 29)], INK)
    s.polygon([(x - 9, y + 18), (x - 5, y + 15), (x + 5, y + 14),
               (x + 10, y + 19), (x + 8, y + 29), (x + 4, y + 33),
               (x - 5, y + 32), (x - 10, y + 28)], RED)
    s.polygon([(x - 7, y + 17), (x - 3, y + 15), (x + 3, y + 15),
               (x + 1, y + 22), (x - 4, y + 25), (x - 8, y + 22)], RED_L)
    s.polygon([(x + 5, y + 16), (x + 9, y + 20), (x + 8, y + 28),
               (x + 4, y + 31), (x + 2, y + 25)], RED_D)
    s.line(x - 7, y + 29, x + 6, y + 29, GOLD)
    s.rect(x - 5, y + 31, x + 5, y + 33, GOLD_D)
    # Arc reactor centerpiece.
    s.polygon([(x - 3, y + 20), (x, y + 18), (x + 3, y + 20),
               (x + 2, y + 24), (x, y + 26), (x - 3, y + 23)], INK)
    s.polygon([(x - 1, y + 20), (x + 1, y + 20), (x + 2, y + 22),
               (x, y + 24), (x - 2, y + 22)], CYAN)
    s.px(x, y + 21, WHITE)

    # Far arm bent beside torso: never allowed to disappear.
    s.polygon([(x - 10, y + 18), (x - 15, y + 20), (x - 17, y + 31),
               (x - 13, y + 36), (x - 8, y + 32), (x - 7, y + 22)], INK)
    s.polygon([(x - 11, y + 20), (x - 14, y + 22), (x - 15, y + 29),
               (x - 12, y + 33), (x - 10, y + 31), (x - 9, y + 22)], RED_D)
    s.polygon([(x - 14, y + 30), (x - 10, y + 31), (x - 9, y + 35),
               (x - 12, y + 38), (x - 16, y + 35)], INK)
    s.rect(x - 13, y + 32, x - 10, y + 35, GOLD_D)
    s.px(x - 11, y + 33, CYAN)

    # Near firing arm changes from charge to full extension.
    if pose == "charge":
        shoulder, elbow, palm = (x + 10, y + 18), (x + 16, y + 25), (x + 17, y + 33)
    elif pose == "aim":
        shoulder, elbow, palm = (x + 10, y + 18), (x + 17, y + 20), (x + 23, y + 23)
    else:
        shoulder, elbow, palm = (x + 10, y + 18), (x + 19, y + 18), (x + 28, y + 20)
    armor_segment(s, shoulder, elbow, RED_L, half_width=4)
    armor_segment(s, elbow, (palm[0] - 2, palm[1]), RED, half_width=3)
    # Gold elbow joint separates the two armor plates.
    s.rect(elbow[0] - 2, elbow[1] - 2, elbow[0] + 2, elbow[1] + 2, GOLD_D)
    s.rect(elbow[0] - 1, elbow[1] - 1, elbow[0] + 1, elbow[1] + 1, GOLD)
    s.polygon([(palm[0] - 3, palm[1] - 3), (palm[0] + 2, palm[1] - 3),
               (palm[0] + 4, palm[1]), (palm[0] + 2, palm[1] + 3),
               (palm[0] - 3, palm[1] + 3), (palm[0] - 4, palm[1])], INK)
    s.polygon([(palm[0] - 2, palm[1] - 2), (palm[0] + 1, palm[1] - 2),
               (palm[0] + 2, palm[1]), (palm[0] + 1, palm[1] + 2),
               (palm[0] - 2, palm[1] + 2)], GOLD)
    s.px(palm[0] + 1, palm[1], CYAN_H)

    # Helmet last: compact head, readable twin eyes and jaw plate.
    s.polygon([(x - 7, y + 1), (x - 3, y - 2), (x + 5, y - 1),
               (x + 9, y + 4), (x + 8, y + 13), (x + 4, y + 17),
               (x - 4, y + 16), (x - 8, y + 11)], INK)
    s.polygon([(x - 5, y + 2), (x - 2, y), (x + 4, y + 1),
               (x + 7, y + 5), (x + 6, y + 11), (x + 3, y + 14),
               (x - 3, y + 14), (x - 6, y + 10)], RED)
    s.polygon([(x - 3, y + 2), (x + 3, y + 2), (x + 5, y + 6),
               (x + 3, y + 12), (x - 2, y + 12), (x - 4, y + 8)], GOLD)
    s.polygon([(x - 2, y + 2), (x + 2, y + 2), (x + 4, y + 5),
               (x, y + 5), (x - 3, y + 6)], GOLD_L)
    s.line(x - 3, y + 9, x - 1, y + 9, CYAN_H)
    s.line(x + 2, y + 9, x + 4, y + 9, CYAN_H)
    s.line(x - 1, y + 13, x + 3, y + 13, RED_D)
    return palm


def build():
    s = Sprite(120, 72, palette=PAL)
    # windup → aim → flash → beam grow → beam hold → recovery
    poses = [
        ("charge", 0, 0, 0, 150),
        ("aim", -1, 0, 0, 90),
        ("fire", 0, 1, 0, 55),
        ("fire", 0, 1, 25, 60),
        ("fire", 0, 2, 48, 95),
        ("aim", 1, 0, 0, 140),
    ]
    for i, (pose, bob, recoil, beam_len, duration) in enumerate(poses):
        if i:
            s.add_frame(copy=False)
        palm = iron_man(s, x=37, ground=68, bob=bob, pose=pose, recoil=recoil)
        if i >= 2:
            beam(s, palm, beam_len, i)
        s.set_duration(duration)
    s.tag("repulsor", 1, 6)
    s.preview(os.path.join(OUT, "tall_iron_man_beam_preview.png"), scale=4, cols=3)
    s.save_silhouette(os.path.join(OUT, "tall_iron_man_beam_silhouette.png"))
    s.save_png(os.path.join(OUT, "tall_iron_man_master.png"), frame=5)
    s.save_png(os.path.join(OUT, "tall_iron_man_display.png"), frame=5, scale=7, bg="#202832")
    s.save_gif(os.path.join(OUT, "tall_iron_man_beam.gif"), scale=6, tag="repulsor")
    s.save_gif(os.path.join(OUT, "tall_iron_man_beam_display.gif"), scale=6, tag="repulsor", bg="#202832")
    s.save_spritesheet(os.path.join(OUT, "tall_iron_man_beam_sheet.png"), layout="horizontal", padding=2)
    return s


def validate(s):
    boxes, edge = [], []
    for f in range(1, s.n_frames + 1):
        box = s.composite(f).getbbox()
        boxes.append(box)
        if box and (box[0] < 2 or box[1] < 2 or box[2] > s.w - 2 or box[3] > s.h - 2):
            edge.append(f)
    return {"canvas": [s.w, s.h], "pivot": [37, 68], "bounds": boxes,
            "edge_failures": edge, "palette_budget": len(PAL)}


s = build()
s.stats()
report = validate(s)
with open(os.path.join(OUT, "tall_iron_man_validation.json"), "w", encoding="utf-8") as f:
    json.dump(report, f, indent=2)
print(json.dumps(report, indent=2))
