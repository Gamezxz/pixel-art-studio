# Hybrid pipeline — from generated art to clean, editable pixels

The hybrid workflow pairs a **generator** (any image model — codex-imagegen, SD+LoRA, a FLUX
finetune, PixelLab's export, even a screenshot) with this skill as the deterministic
**cleanup + lock + animate** layer. The generator supplies composition and detail; we supply
the pixel-art discipline the model can't guarantee: true grid, no mixels, hard palette, no halos,
and a build script you keep editing.

This is where the skill *exceeds* raw model output: PixelLab fights its diffusion prior to avoid
mixels and palette drift; we never have them, by construction, and every asset is editable.

## The pipeline

```
generate (any model) ──► messy.png ──► pixelpipe ──► clean.png + build.py
                                          │
            recover true grid · strip bg · harden alpha · despeckle
            · dedupe colors · (dehalo) · palette lock / quantize
```

One command:

```bash
python3 scripts/pixelpipe.py messy.png --strip-checker --max-colors 24
# or lock to a shared game palette for cross-asset consistency:
python3 scripts/pixelpipe.py messy.png --palette my_game --display 6
# learn the style while you're at it:
python3 scripts/pixelpipe.py messy.png --strip-checker --study knight_style
```

Outputs to `<input>_pipe/`: `clean.png` (1x master), `clean@Nx.png`, `before_after.png`,
`palette.png`, `report.json`, and crucially **`build.py`** — a regenerable script importing
pixelstudio. Edit that and rerun to iterate; never hand-edit the PNG.

In code:

```python
from pixelstudio import Sprite
s = Sprite.from_png("gen.png", scale="auto", strip_bg=True)   # recover true pixels
s._orig = s.composite(1).copy()                                 # for before_after()
s.clean(palette="my_game", harden=True, despeckle_min=2, dedupe_tol=10)
s.before_after("ba.png", scale=6)
s.save_png("clean.png")
```

## What each cleanup step does (and when to tune it)

### Recover the true grid — `from_png(scale=, strip_bg=)`
- `scale="auto"`: detects an exact integer upscale (NEAREST recovery); if none, estimates the
  run-length and falls back to **block-center sampling** (handles sloppy/resampled model output
  that would otherwise produce mixels).
- Pass a **float** (e.g. `5.7`) to force block sampling at a non-integer scale.
- `strip_bg=True`: removes a baked-in light-gray checkerboard (very common in AI-gen exports).

### Harden alpha — `harden_alpha(threshold=128, steps=None)`
The single biggest quality lever for model output. Snaps semi-transparent pixels to 0/255,
killing AA fuzz and bg halos in one pass. Set `harden=False` in `clean()` only for intentionally
painterly alpha art. For a softer look, `steps=[0,80,160,255]` quantizes alpha to a few discrete
levels instead of going binary.

### Despeckle — `despeckle(min_cluster=2)`
Removes orphan pixel clusters (4-connected components smaller than `min_cluster`). Kills the
"static" models scatter without touching legitimate detail. Raise to 3–4 for noisier sources;
set 0 to disable.

### Dedupe colors — `dedupe_colors(tol=10)`
Merges colors within `tol` max-channel-distance into their most-used representative. Collapses
the near-duplicate explosion (hundreds of "almost-the-same" shades) before quantization. Raise
`tol` (12–16) for more aggressive merging.

### Dehalo — `dehalo()` (opt-in, conservative)
Detects opaque edge pixels that are low-saturation (color-contaminated by a former white/dark
background from AA) and snaps them toward their opaque neighbors' average. Off by default — it
can damage legit light edge shading. Turn on when you see a visible fringe ring.

### Palette lock — `clean(palette=NAME)` or `clean(max_colors=N)`
- **`palette=`**: remap every pixel onto a named/learned palette. This is the **cross-asset
  consistency** win: every cleaned asset shares the exact same color vocabulary, so a cast of
  characters looks like one game. Use a generous master palette (32–48 colors) to preserve nuance.
- **`max_colors=N`**: no palette given → reduce to N colors chosen adaptively from the art itself.

## Tuning by source type

| Source | Recommended `clean()` |
|---|---|
| clean PixelLab-style export (already gridded) | `max_colors=24, dedupe_tol=8` (light touch) |
| diffusion "pixel art" (fuzzy, many colors) | `harden=True, despeckle=3, dedupe_tol=14, max_colors=24` |
| screenshot with checker bg | `strip_bg=True` first, then defaults |
| scanned / photographed pixel art | `--scale FLOAT` forced + `dehalo=True` |
| painterly alpha art (soft edges intended) | `harden_steps=[0,80,160,255]`, `despeckle=0` |

## After cleaning: the skill's real advantage kicks in

Once you have `clean.png` + `build.py`, you're back in deterministic territory — the part where
this skill beats any generator:

- **Edit without re-rolling**: change the sword? edit one function in build.py, rerun. A generator
  makes you re-roll and pray the rest stays the same.
- **Animate deterministically**: split into part-layers, puppet with `shift()`/parametric redraw —
  the same character across every frame, guaranteed (see animation.md).
- **Palette-swap variants**: `replace()` per ramp step → enemy color variants in seconds.
- **Study it**: `--study NAME` extracts the style into a card + saved palette, so the *next*
  asset you generate matches.

## Honest limits

- A model can produce a 96×96 knight with 30 ornate armor segments in one shot. Cleaning preserves
  that richness, but if you then want to *redraw* such detail by hand via primitives, you hit the
  skill's detail ceiling (see sharp_edges.md). The hybrid's strength is **clean + lock + edit +
  animate** on generated bases, not replacing the generator for novel high-detail composition.
- Auto scale-detection is heuristic. When you know the source scale, pass `--scale N` for exact
  recovery.
