#!/usr/bin/env python3
"""pixelpipe — the hybrid pipeline: generated/messy PNG → clean, palette-locked pixel art.

    python3 pixelpipe.py <input.png> [options]

It is the deterministic "cleanup + lock" layer that turns AI-generated (or sloppy/scanned)
pixel art into real, game-ready sprites: recovers the true grid, strips baked-in backgrounds,
hardens alpha, kills orphan noise, collapses the color explosion, and locks everything onto
a shared palette for cross-asset consistency — then leaves you a build script you can keep editing.

Outputs go to <input>_pipe/:
    clean.png          the cleaned, palette-locked sprite (1x master)
    clean@Nx.png       display-scale copy
    before_after.png   input vs cleaned, side by side
    palette.png        swatch of the final palette
    report.json        before/after stats (colors, semi-alpha, scale, method)
    build.py           a regenerable build script importing pixelstudio — edit this to iterate

Options:
    --scale N|auto|FLOAT   upscale factor to recover (default auto; float = forced block sampling)
    --strip-checker        remove baked-in light-gray checkerboard background
    --palette NAME         lock to a named/learned palette (PALETTES[NAME])
    --max-colors N         if no --palette, reduce to N colors chosen from the art (default 24)
    --display N            display upscale for previews (default 6)
    --no-harden            keep painterly alpha (don't snap alpha to 0/255)
    --harden-steps A,B,C   quantize alpha to discrete levels instead of binary
    --despeckle N          remove opaque clusters smaller than N px (default 2; 0 = off)
    --dedupe N             merge colors within channel distance N (default 10; 0 = off)
    --dehalo               also wash out low-saturation edge contamination
    --study NAME           additionally run a study card + save palette as NAME

Generate step (the other half of the hybrid): produce the input PNG with any image model
(the codex-imagegen skill, SD+LoRA, FLUX finetune, or PixelLab's own export), then point
pixelpipe at it. Keep generation prompts coarse; pixelpipe supplies the pixel-art discipline.
"""
from __future__ import annotations

import argparse
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from pixelstudio import Sprite, PALETTES  # noqa: E402

_BUILD_TPL = '''#!/usr/bin/env python3
"""Regenerable build for {name} — produced by pixelpipe. Edit and rerun to iterate."""
import sys
sys.path.insert(0, {skill!r})
from pixelstudio import Sprite

s = Sprite.from_png({input!r}, scale={scale!r}, strip_bg={strip})
s.clean(palette={palette!r}, max_colors={maxc}, harden={harden}, harden_steps={hsteps!r},
        despeckle_min={desp}, dedupe_tol={dedupe}, dehalo={dehalo})
s.preview("preview.png", scale={disp})
s.save_png("clean.png")
s.save_png("clean@{disp}x.png", scale={disp})
s.stats()
'''


def _parse_steps(s):
    if not s:
        return None
    return [int(v) for v in s.split(",")]


def run(args):
    src = os.path.abspath(args.input)
    out_dir = args.out or (os.path.splitext(src)[0] + "_pipe")
    os.makedirs(out_dir, exist_ok=True)
    name = os.path.basename(os.path.splitext(src)[0])

    sp = Sprite.from_png(src, scale=args.scale, strip_bg=args.strip_checker)
    before = sp.composite(1).copy()
    b_colors = len(sp.used_colors())
    b_semi = sum(1 for *_, a in before.getdata() if 0 < a < 255)
    sp._orig = before

    palette = args.palette
    if palette and palette not in PALETTES:
        print("WARNING: palette %r not in PALETTES (have: %s) — falling back to max_colors"
              % (palette, ", ".join(sorted(PALETTES)) or "none"))
        palette = None

    sp.clean(palette=palette, max_colors=args.max_colors, harden=not args.no_harden,
             harden_steps=_parse_steps(args.harden_steps), despeckle_min=args.despeckle,
             dedupe_tol=args.dedupe, dehalo=args.dehalo)

    after_colors = len(sp.used_colors())
    a_semi = sum(1 for *_, a in sp.composite(1).getdata() if 0 < a < 255)

    clean_path = os.path.join(out_dir, "clean.png")
    disp_path = os.path.join(out_dir, "clean@%dx.png" % args.display)
    ba_path = os.path.join(out_dir, "before_after.png")
    pal_path = os.path.join(out_dir, "palette.png")
    rep_path = os.path.join(out_dir, "report.json")
    build_path = os.path.join(out_dir, "build.py")

    sp.save_png(clean_path)
    sp.save_png(disp_path, scale=args.display)
    sp.before_after(ba_path, scale=args.display)
    sp.save_swatch(pal_path)

    report = {
        "input": src, "name": name, "out_dir": out_dir,
        "true_size": [sp.w, sp.h], "detected_scale": sp.detected_scale,
        "import_method": sp.import_method, "strip_checker": args.strip_checker,
        "palette": palette, "max_colors": args.max_colors,
        "before": {"colors": b_colors, "semi_alpha_px": b_semi},
        "after": {"colors": after_colors, "semi_alpha_px": a_semi},
    }
    with open(rep_path, "w") as f:
        json.dump(report, f, indent=2)

    skill = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) + "/scripts"
    with open(build_path, "w") as f:
        f.write(_BUILD_TPL.format(
            name=name, skill=skill, input=src, scale=args.scale, strip=args.strip_checker,
            palette=palette, maxc=(args.max_colors if not palette else None),
            harden=not args.no_harden, hsteps=_parse_steps(args.harden_steps),
            desp=args.despeckle, dedupe=args.dedupe, dehalo=args.dehalo, disp=args.display))

    if args.study:
        _run_study(src, sp, args.study, out_dir)

    print("\n=== pixelpipe report ===")
    print("  input      %s" % src)
    print("  recovered  %dx%d (scale %sx, %s)%s" % (
        sp.w, sp.h, sp.detected_scale, sp.import_method,
        " +checker-stripped" if args.strip_checker else ""))
    print("  colors     %d -> %d%s" % (b_colors, after_colors,
        (" on palette %r" % palette) if palette else " (max %d)" % args.max_colors))
    print("  semi-alpha %d -> %d px" % (b_semi, a_semi))
    print("  outputs    %s/" % out_dir)
    print("             clean.png · clean@%dx.png · before_after.png · palette.png · report.json · build.py"
          % args.display)
    if args.study:
        print("             + study card + palette saved as %r" % args.study)


def _run_study(src, sp, name, out_dir):
    """Write a study card + save the cleaned palette, reusing study.analyze."""
    try:
        import study  # sibling module
    except ImportError:
        print("  (study.py not found alongside pixelpipe — skipping study card)")
        return
    cleaned = os.path.join(out_dir, "clean.png")
    _, _, report = study.analyze(cleaned)
    study.render_outputs(sp.composite(1), report, os.path.join(out_dir, "study"))
    learned_dir = os.path.normpath(os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "..", "references", "learned"))
    pal_path = study.save_palette(name, report) if hasattr(study, "save_palette") else None
    card = os.path.join(learned_dir, "%s-%s.md" % (
        _next_idx(learned_dir), name.replace(" ", "-")))
    study.print_report(report, os.path.join(out_dir, "study"), name)
    print("  study card skeleton printed above — save observations to %s" % card)


def _next_idx(learned_dir):
    try:
        files = [f for f in os.listdir(learned_dir) if f[:3].isdigit()]
    except OSError:
        return "001"
    return "%03d" % (max([int(f[:3]) for f in files] + [0]) + 1)


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("input", help="input PNG (generated/sloppy/scanned pixel art)")
    ap.add_argument("--out", default=None, help="output directory (default <input>_pipe)")
    ap.add_argument("--scale", default="auto",
                    help="auto | int | float (float = forced block sampling)")
    ap.add_argument("--strip-checker", action="store_true", help="remove baked-in checkerboard bg")
    ap.add_argument("--palette", default=None, help="lock to PALETTES[NAME]")
    ap.add_argument("--max-colors", type=int, default=24, help="color budget if no --palette")
    ap.add_argument("--display", type=int, default=6, help="display upscale for previews")
    ap.add_argument("--no-harden", action="store_true", help="keep painterly alpha")
    ap.add_argument("--harden-steps", default=None, help="e.g. 0,64,160,255")
    ap.add_argument("--despeckle", type=int, default=2, help="min cluster size (0=off)")
    ap.add_argument("--dedupe", type=int, default=10, help="color merge tolerance (0=off)")
    ap.add_argument("--dehalo", action="store_true", help="wash low-sat edge contamination")
    ap.add_argument("--study", default=None, help="also write a study card + save palette as NAME")
    args = ap.parse_args()
    if args.scale != "auto":
        try:
            float(args.scale)
        except ValueError:
            ap.error("--scale must be 'auto', an int, or a float")
    run(args)


if __name__ == "__main__":
    main()
