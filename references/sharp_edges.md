# Sharp Edges — known failure modes (check before finalizing)

1. **Non-integer scaling** (CRITICAL) — 1.5x/2.3x = blurred, uneven pixels. Integer only,
   nearest-neighbor only. Applies to exports AND engine display settings.

2. **Pillow shading** — all edges darkened uniformly → balloon sprite. Shading follows the
   light source, not the outline. Test: is the darkest shade hugging the outline everywhere? Redo.

3. **Banding** — ramp bands parallel to the outline, 1px per shade → staircase gradient.
   Vary band widths; let bands cut across forms.

4. **AA halos** — anti-aliasing premixed against an assumed background → fringe on any
   other bg. AA only between color regions; edges to transparency stay hard (or alpha-steps).
   `stats()` semi_alpha_px > 0 without intent = bug.

5. **Orphan pixels** — stray single px reads as dirt at 1x. `stats()` lists isolated px;
   each must be justified (eye glint, sparkle) or deleted.

6. **Jaggies & line doubles** — curves whose pixel steps jump (1,3,1) look broken; hand-drawn
   `px()` sequences that double at corners look thick. `line()` (Bresenham) never doubles;
   for curves check step progression, fix shape before AA.

7. **Palette bloat** — “one more shade” until 40 colors. Set the budget in the brief;
   `stats()` colors_used vs palette_size every iteration; near-duplicates get merged.

8. **Mixed pixel density** — rotating/scaling a part, or pasting art of another scale →
   some “pixels” bigger than others. Everything is drawn at 1x on the same grid, full stop.

9. **Banding²: dither everywhere** — dither as texture wallpaper. Dither is a gradient/texture
   tool; on <24px sprites or moving parts it's shimmer noise.

10. **GIF transparency misuse** — semi-alpha edges become crunchy (binary alpha). For social
    posts composite onto a bg color; keep transparent GIFs to hard-edged art.

11. **Editing exports instead of the build script** — the PNG is a compile target. All
    changes go into build.py, or they're lost on the next render.

12. **Delivering the preview** — contact sheets/grids/labels are working documents.
    Deliver `save_png`/`save_gif`/`save_spritesheet` outputs only.

## Library-specific gotchas

- `ellipse()`/`polygon()` are PIL-backed: fine ≥12px, lopsided smaller — use `circle()`
  (midpoint, pixel-perfect) or hand-place px for small round things.
- `fill()` flood-fills 4-way; it leaks through diagonal-only gaps by design (they're connected
  visually too — close the gap).
- `outline(where="outside")` needs a 1px transparent margin; sprites touching the canvas
  edge get clipped outlines.
- Drawing after `quantize()`/`to_palette()` uses the NEW palette; `set_palette(..., remap=True)`
  if old colors linger.
- Canvases >256px: per-pixel Python ops get slow — prefer rect/ellipse/dither area ops,
  avoid px() in triple loops.
- `add_frame(copy=True)` copies cels; `copy_cel(link=True)` SHARES the image (edit hits all
  linked frames) — powerful for static bg, surprising if forgotten.
