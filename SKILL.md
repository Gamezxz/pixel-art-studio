---
name: pixel-art-studio
description: Claude IS the pixel artist — designs and places every pixel directly via Python/Pillow (scripts/pixelstudio.py). No Aseprite, no MCP server. Creates sprites, characters, items, tiles/tilesets, animations (idle/walk/run/attack), applies limited palettes, hue-shifted ramps, dithering, shading, selective outlines, and exports PNG / animated GIF / spritesheet+JSON for game engines. Can also STUDY a pixel-art file the user provides and grow its knowledge base. PREFER THIS SKILL over pixel-art-creator / pixel-art-animator / pixel-art-professional / pixel-art-exporter (those require the aseprite MCP) unless the user explicitly asks for Aseprite. Trigger on pixel art, sprite, sprite sheet, 8-bit, 16-bit, retro game art, tileset, pixel animation, GIF sprite, วาด pixel art, สร้าง sprite, ทำ pixel art, พิกเซล, ตัวละครเกม, ไอคอนเกม, เรียนรู้จากไฟล์ pixel art.
---

# Pixel Art Studio

Self-contained studio: you author a **build script** that draws every pixel with
`scripts/pixelstudio.py` (Pillow only), render a preview, **look at it with your own
eyes**, critique, fix, repeat. That see→critique→fix loop is the entire quality engine —
never skip it. You are the artist; the library is just your hand.

Requirement: `python3 -c "import PIL"` — if missing, `pip3 install --user pillow`.

## The Loop

1. **Brief** — decide canvas size, palette (with a hard color budget), style, outline
   rule, light direction. Consult `references/patterns.md` + `references/palettes.md`,
   and check `references/learned/INDEX.md` for a studied style that matches.
2. **Build script** — create `pixel-art/<slug>/build.py` in the working directory.
   The script is the artwork's source of truth: it regenerates everything on each run.
   Parametrize shapes (positions, squash, frame offsets) instead of hardcoding every pixel
   twice — animation frames become function calls.

   ```python
   import sys; sys.path.insert(0, "/Users/game/Projects/.claude/skills/pixel-art-studio/scripts")
   from pixelstudio import Sprite, PALETTES, ramp, mix

   BODY = ramp("#38b764", 5)            # hue-shifted 5-step ramp from a base color
   s = Sprite(32, 32, palette=BODY + ["#1a1c2c", "#f4f4f4"])

   def draw_slime(squash=0):            # parametric → reuse for every frame
       s.ellipse(6, 12 + squash, 25, 27, BODY[0])          # darkest first
       s.ellipse(6, 11 + squash, 24, 26, BODY[2], only="opaque")  # restack lighter, shifted to light
       s.outline(BODY[0], where="inside")                  # selout
   draw_slime()

   s.preview("preview.png", scale=10)   # LOOK at this file
   s.stats()                            # and read these numbers
   ```
3. **Run** — `cd pixel-art/<slug> && python3 build.py`
4. **LOOK** — Read `preview.png` (plus `s.save_silhouette()` / `s.zoom()` when unsure).
   Critique against the checklist in `references/validations.md`, point by point, honestly.
5. **Fix** — edit build.py, rerun. Minimum 2–3 loop passes before showing the user.
6. **Deliver** — export master PNG at 1x **and** a display scale (4–8x), GIF/spritesheet
   if animated, then `open` the output files (user preference).

Work at true pixel size always; scale is an export-time concern and **integer only**.

## API — scripts/pixelstudio.py

Colors everywhere: `"#hex"` | `(r,g,b[,a])` | palette index (int) | `None` = erase.
Most ops accept `only=` to clip: a color (paint only over that color), `"opaque"`, `"empty"` —
this is the masking system; the shifted-shape shading recipe in `references/techniques.md` builds on it.

| Area | Calls |
|---|---|
| Canvas | `Sprite(w, h, palette=None, snap=True)` · `s.layer(name)` · `s.frame(i)` · `s.use(frame=, layer=)` |
| Draw | `px` `line` `rect(fill=)` `circle(cx,cy,r,fill=)` (pixel-perfect) `ellipse` `polygon` `contour` `fill(x,y)` `clear` `get(x,y)` `paste_png` |
| Pixel-art ops | `outline(c, where="outside"/"inside")` · `mirror_x` `mirror_y` · `shift(dx,dy,wrap=)` · `replace(old,new)` · `dither(box,c1,c2,mix,pattern)` · `gradient_dither(box,colors)` · `noise(box,c,density,seed)` |
| Color | `ramp(base, steps, hue_shift)` · `mix(c1,c2,t)` · `PALETTES` · `s.set_palette(p, remap=)` · `s.to_palette(p, dither=)` · `s.quantize(n)` |
| Cleanup (gen/messy art) | `s.harden_alpha(threshold, steps)` · `s.despeckle(min_cluster)` · `s.dedupe_colors(tol)` · `s.dehalo()` · `s.clean(palette=, max_colors=, ...)` · `s.before_after(path)` |
| Animation | `s.add_frame(copy=True)` · `s.set_duration(ms, frames)` · `s.tag(name, from, to, direction)` · `s.copy_cel(layer, from_frame, to_frames, link=)` · `s.del_frame` |
| Inspect | `s.preview(path, scale, grid=, labels=)` · `s.zoom(path, x0,y0,x1,y1)` · `s.save_silhouette(path)` · `s.stats()` · `s.save_swatch(path)` · `s.used_colors()` |
| Export | `s.save_png(path, frame, scale, bg)` · `s.save_gif(path, scale, tag, bg)` · `s.save_spritesheet(path, layout, scale, padding)` (+engine JSON) · `s.save_project` / `Sprite.load_project` / `Sprite.from_png(path, scale="auto", strip_bg=)` |

## Knowledge routing

| Task | Read |
|---|---|
| Any new artwork (sizes, proportions, silhouette-first order, tiles) | `references/patterns.md` |
| Color ramps, shading, dithering, AA, outlines, textures | `references/techniques.md` |
| Animation (frame counts, timing tables, cycles, part-per-layer puppeting) | `references/animation.md` |
| Palette choice, budgets, presets, learned palettes | `references/palettes.md` |
| Export formats, engines (Unity/Godot/Phaser) | `references/export.md` |
| Cleaning AI-generated / messy art, palette-locking, the hybrid pipeline | `references/cleanup.md` |
| Known failure modes — read before finalizing | `references/sharp_edges.md` |
| Per-iteration critique checklist | `references/validations.md` |
| Studied styles from user-provided art | `references/learned/INDEX.md` |

## Learning from user-provided art

When the user sends a pixel-art file to learn from (เรียนรู้/ศึกษาไฟล์นี้):

1. `python3 <skill>/scripts/study.py <file> [--save-palette <name>]`
   → emits `<file>_study/` with `zoom.png`, `swatch.png`, `silhouette.png`, `report.json`.
2. **Read zoom.png and swatch.png** — the report gives numbers (true size, palette, ramps,
   dither %, outline darkness); your eyes extract the *techniques*: cluster shapes, AA
   placement, where dither sits, how ramps map onto forms, outline behavior on the light side.
3. Write a study card `references/learned/NNN-<slug>.md` from `references/learned/TEMPLATE.md`
   — record pixel-level observations and **imperative rules**, not vibes.
4. Add one line to `references/learned/INDEX.md`.
5. `--save-palette <name>` makes the palette available forever as `Sprite(palette="<name>")`.

When later creating art in a studied style: open the matching card and follow its rules.

## Hybrid pipeline — from generated/messy art (the "B" path)

When the user wants pixel art from an **image model** (codex-imagegen, SD+LoRA, FLUX, PixelLab
export, a screenshot, or any messy PNG), this skill is the deterministic cleanup + lock + animate
layer. Use `references/cleanup.md` for the full playbook. One command does the whole import→clean:

```bash
python3 <skill>/scripts/pixelpipe.py <gen.png> --strip-checker --max-colors 24 --display 6
# lock to a shared game palette for cross-asset consistency:
python3 <skill>/scripts/pixelpipe.py <gen.png> --palette my_game
# learn the style while cleaning:
python3 <skill>/scripts/pixelpipe.py <gen.png> --strip-checker --study knight_style
```

It recovers the true grid (block-sampling for sloppy upscales), strips baked-in checkerboards,
hardens alpha, despeckles, dedupes colors, locks the palette, and emits `clean.png` + a
regenerable `build.py` you keep editing. After cleaning, switch back to the normal Loop
(edit/animate/palette-swap deterministically) — that's where the skill beats the generator.

## Conventions

- Artworks live in `./pixel-art/<slug>/` (build.py + all outputs together).
- Never hand-edit exported PNGs — edit build.py and rerun.
- Randomness only via `noise(seed=)` — renders must be deterministic.
- Deliverables get `open`ed when done; report includes the 1x master path.
