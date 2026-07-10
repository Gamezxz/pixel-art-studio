#!/usr/bin/env python3
"""study.py — analyze a pixel-art file so Claude can learn from it.

Usage:
    python3 study.py <image> [--out DIR] [--save-palette NAME] [--name SLUG]

Emits into <image>_study/ (or --out):
    report.json      machine-readable analysis
    swatch.png       palette swatches (indexed, sorted by usage)
    zoom.png         true-pixel view upscaled for inspection
    silhouette.png   silhouette test render
Prints a human report + a study-card skeleton to fill into
references/learned/NNN-<slug>.md.

--save-palette NAME stores the extracted palette into
references/learned/palettes.json, auto-loaded by pixelstudio as PALETTES[NAME].
"""
from __future__ import annotations

import argparse
import colorsys
import json
import math
import os
import sys
from collections import Counter, OrderedDict

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from PIL import Image, ImageDraw, ImageFont  # noqa: E402

from pixelstudio import NEAREST, detect_scale, rgba2hex  # noqa: E402

LEARNED_DIR = os.path.normpath(os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "..", "references", "learned"))


def luminance(c):
    return (0.299 * c[0] + 0.587 * c[1] + 0.114 * c[2]) / 255.0


def strip_checker(im):
    """Remove a baked-in light-gray checkerboard background."""
    px = im.load()
    for y in range(im.height):
        for x in range(im.width):
            r, g, b, a = px[x, y]
            if a > 0 and abs(r - g) < 14 and abs(g - b) < 26 and r > 185 and b > 160:
                px[x, y] = (0, 0, 0, 0)
    return im


def estimate_scale(im):
    """Median run-length of similar colors — for non-integer/resampled upscales."""
    p = im.load()
    out = []
    for y in range(0, im.height, 7):
        run = 1
        for x in range(1, im.width):
            a, b = p[x - 1, y], p[x, y]
            if max(abs(a[i] - b[i]) for i in range(3)) < 24:
                run += 1
            else:
                if run < 40:
                    out.append(run)
                run = 1
    out.sort()
    return out[len(out) // 2] if out else 1


def block_downscale(im, s):
    """Sample block centers (survives sloppy/resampled upscales, unlike NEAREST resize)."""
    w, h = im.size
    tw, th = round(w / s), round(h / s)
    small = Image.new("RGBA", (tw, th))
    sp, px = small.load(), im.load()
    for ty in range(th):
        for tx in range(tw):
            sp[tx, ty] = px[min(w - 1, int((tx + 0.5) * s)), min(h - 1, int((ty + 0.5) * s))]
    return small


def analyze(path, force_scale=None, do_strip=False):
    im = Image.open(path).convert("RGBA")
    if do_strip:
        strip_checker(im)
    if force_scale:
        scale = force_scale
        true = block_downscale(im, scale) if scale > 1 else im
    else:
        scale = detect_scale(im)
        true = im.resize((im.width // scale, im.height // scale), NEAREST) if scale > 1 else im
        if scale == 1:
            approx = len(set(true.getdata()))
            est = estimate_scale(im)
            if approx > 400 and est > 1:
                print("NOTE: %d colors + no exact scale — likely a resampled ~%dx upscale." % (approx, est))
                print("      Rerun with:  --scale %d  (and --strip-checker if bg is baked in)" % est)
    w, h = true.size
    data = list(true.getdata())

    opaque = [(r, g, b) for r, g, b, a in data if a >= 128]
    semi = sum(1 for r, g, b, a in data if 0 < a < 255)
    transparent = sum(1 for *_, a in data if a == 0)
    cnt = Counter(opaque)
    colors = cnt.most_common()

    # ---- ramps: group colors by hue bucket, sort by value
    buckets = {}
    for (r, g, b), n in colors:
        hh, ss, vv = colorsys.rgb_to_hsv(r / 255.0, g / 255.0, b / 255.0)
        key = "neutral" if (ss < 0.13 or vv < 0.10) else "hue-%03d" % (int(hh * 360) // 30 * 30)
        buckets.setdefault(key, []).append(((r, g, b), vv))
    ramps = {k: [rgba2hex(c + (255,)) for c, _ in sorted(v, key=lambda t: t[1])]
             for k, v in sorted(buckets.items())}

    # ---- dithering score: 2x2 checkerboard patterns among opaque px
    px = true.load()
    checks = 0
    pairs = 0
    for y in range(h - 1):
        for x in range(w - 1):
            q = [px[x, y], px[x + 1, y], px[x, y + 1], px[x + 1, y + 1]]
            if all(c[3] >= 128 for c in q):
                pairs += 1
                a, b, c, d = [cc[:3] for cc in q]
                if a == d and b == c and a != b:
                    checks += 1
    dither_pct = round(100.0 * checks / pairs, 2) if pairs else 0.0

    # ---- outline: darkness of silhouette-edge pixels
    edge = []
    for y in range(h):
        for x in range(w):
            if px[x, y][3] >= 128:
                nbs = [(x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)]
                if any(not (0 <= nx < w and 0 <= ny < h) or px[nx, ny][3] < 128
                       for nx, ny in nbs):
                    edge.append(px[x, y][:3])
    if edge:
        dark_edge_pct = round(100.0 * sum(1 for c in edge if luminance(c) < 0.25) / len(edge), 1)
        edge_colors = Counter(edge).most_common(3)
    else:
        dark_edge_pct, edge_colors = None, []

    lums = [luminance(c) for c, _ in colors]
    report = {
        "file": os.path.abspath(path),
        "loaded_size": list(im.size),
        "detected_scale": scale,
        "true_size": [w, h],
        "opaque_px": len(opaque),
        "transparent_px": transparent,
        "semi_alpha_px": semi,
        "color_count": len(colors),
        "palette": [{"hex": rgba2hex(c + (255,)), "count": n,
                     "pct": round(100.0 * n / max(1, len(opaque)), 2)}
                    for c, n in colors],
        "value_range": [round(min(lums), 3), round(max(lums), 3)] if lums else None,
        "ramps_by_hue": ramps,
        "dither_checker_pct": dither_pct,
        "edge_dark_pct": dark_edge_pct,
        "edge_top_colors": [rgba2hex(c + (255,)) for c, _ in edge_colors],
    }
    return im, true, report


def render_outputs(true, report, out_dir):
    os.makedirs(out_dir, exist_ok=True)
    w, h = true.size

    # zoom: upscale to <= 1024 px on the long side
    z = max(1, min(16, 1024 // max(w, h)))
    true.resize((w * z, h * z), NEAREST).save(os.path.join(out_dir, "zoom.png"))

    # silhouette
    sil = Image.new("RGB", (w, h), (232, 228, 218))
    sp = sil.load()
    tp = true.load()
    for y in range(h):
        for x in range(w):
            if tp[x, y][3] >= 128:
                sp[x, y] = (34, 36, 46)
    sil.resize((w * z, h * z), NEAREST).save(os.path.join(out_dir, "silhouette.png"))

    # swatch (top 64)
    pal = report["palette"][:64]
    cell = 28
    cols = min(16, max(1, len(pal)))
    rows = math.ceil(len(pal) / cols)
    img = Image.new("RGB", (cols * cell, rows * (cell + 14)), (250, 250, 250))
    d = ImageDraw.Draw(img)
    font = ImageFont.load_default()
    for i, item in enumerate(pal):
        r, c = divmod(i, cols)
        x, y = c * cell, r * (cell + 14)
        d.text((x + 2, y + 1), str(i), fill=(60, 60, 60), font=font)
        rgb = tuple(int(item["hex"][j:j + 2], 16) for j in (1, 3, 5))
        d.rectangle([x, y + 14, x + cell - 1, y + 14 + cell - 1], fill=rgb)
    img.save(os.path.join(out_dir, "swatch.png"))

    with open(os.path.join(out_dir, "report.json"), "w") as f:
        json.dump(report, f, indent=1)


def save_palette(name, report):
    os.makedirs(LEARNED_DIR, exist_ok=True)
    path = os.path.join(LEARNED_DIR, "palettes.json")
    data = OrderedDict()
    if os.path.exists(path):
        with open(path) as f:
            data = json.load(f, object_pairs_hook=OrderedDict)
    ordered = sorted(report["palette"],
                     key=lambda it: luminance(tuple(int(it["hex"][j:j + 2], 16) for j in (1, 3, 5))))
    data[name] = [it["hex"] for it in ordered]
    with open(path, "w") as f:
        json.dump(data, f, indent=1)
    return path


def print_report(report, out_dir, pal_name):
    print("study ==========================================")
    print(" file           %s" % report["file"])
    print(" loaded %dx%d -> true %dx%d (detected scale %dx)" % (
        tuple(report["loaded_size"]) + tuple(report["true_size"]) + (report["detected_scale"],)))
    print(" colors         %d | semi-alpha px %d | value range %s" % (
        report["color_count"], report["semi_alpha_px"], report["value_range"]))
    print(" dither(checker) %.2f%% of 2x2 blocks | dark-edge %s%% (outline colors %s)" % (
        report["dither_checker_pct"],
        report["edge_dark_pct"], ",".join(report["edge_top_colors"]) or "-"))
    print(" ramps by hue:")
    for k, v in report["ramps_by_hue"].items():
        print("   %-8s %s" % (k, " ".join(v[:8])))
    print(" top colors:    %s" % "  ".join(
        "%s %.1f%%" % (it["hex"], it["pct"]) for it in report["palette"][:10]))
    print(" outputs -> %s/ (zoom.png, swatch.png, silhouette.png, report.json)" % out_dir)
    print("================================================")
    print()
    print("Study-card skeleton (fill observations by LOOKING at zoom.png, then save to")
    print("references/learned/NNN-<slug>.md and add a line to INDEX.md):")
    print("---")
    print("# Study: <name>")
    print("- source: %s" % report["file"])
    print("- true size: %dx%d (scale %dx) | colors: %d%s" % (
        report["true_size"][0], report["true_size"][1], report["detected_scale"],
        report["color_count"], " | palette saved: %s" % pal_name if pal_name else ""))
    print("- ramps: <which hue ramps exist, how many steps, hue-shift direction>")
    print("- outline: <none / selout / black %s%% dark edge>" % report["edge_dark_pct"])
    print("- dithering: <where used; checker score %.2f%%>" % report["dither_checker_pct"])
    print("- shading: <light direction, band count, AA spots>")
    print("## Rules to apply")
    print("- <imperative, pixel-level rules extracted from this piece>")
    print("## Do NOT copy")
    print("- <weaknesses or style quirks to avoid>")


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("input")
    ap.add_argument("--out", default=None)
    ap.add_argument("--save-palette", dest="save_palette", default=None,
                    help="store extracted palette as PALETTES[NAME]")
    ap.add_argument("--scale", type=int, default=None,
                    help="force upscale factor (for resampled/non-integer upscales)")
    ap.add_argument("--strip-checker", action="store_true",
                    help="remove baked-in light-gray checkerboard background")
    args = ap.parse_args()

    im, true, report = analyze(args.input, force_scale=args.scale, do_strip=args.strip_checker)
    out_dir = args.out or (os.path.splitext(os.path.abspath(args.input))[0] + "_study")
    render_outputs(true, report, out_dir)
    pal = None
    if args.save_palette:
        p = save_palette(args.save_palette, report)
        pal = args.save_palette
        print("palette '%s' saved -> %s (usable as Sprite(palette=%r))" % (pal, p, pal))
    print_report(report, out_dir, pal)


if __name__ == "__main__":
    main()
