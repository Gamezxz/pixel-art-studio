# Palettes — choice, budgets, presets

## Philosophy

Fewer colors force better design. Every color must earn its slot: if two colors are
within ~12 RGB of each other (`stats()` flags near-duplicates), merge them.

## Budgets (hard limits)

| Subject | Colors |
|---|---|
| small props / icons | 4–6 |
| characters | 8–12 |
| bosses / large sprites | 12–16 |
| tileset (one biome) | 8–16 |
| full scene | 16–32 |

Materials share the darkest shade (also the selout color) — biggest palette saver.

## Presets (`PALETTES[name]`, use as `Sprite(palette="name")`)

| Name | n | Character |
|---|---|---|
| `onebit` | 2 | black/white, brutal clarity |
| `gameboy` | 4 | DMG green LCD nostalgia |
| `pico8` | 16 | punchy, warm, fantasy-console standard |
| `sweetie16` | 16 | balanced modern all-rounder, soft |
| `c64` | 16 | muted retro computer (Pepto) |
| `endesga32` | 32 | the modern indie standard, full range |
| *(learned)* | — | anything saved via `study.py --save-palette` |

NES note: the NES generated colors in analog — there is no single canonical RGB table.
For "NES style" use a 16-color subset of `endesga32` or a learned palette, cap at
3 colors + transparent per sprite for authenticity.

## Building custom ramps

```python
SKIN  = ramp("#e4a672", 4, hue_shift=16)
CLOTH = ramp("#3b5dc9", 5, hue_shift=20)
DARK  = "#1a1c2c"                      # shared darkest + outline
s = Sprite(32, 32, palette=SKIN + CLOTH + [DARK])
```

`snap=True` (default) snaps any drawn color to the palette — discipline is automatic.
Check with `s.save_swatch("swatch.png")` — a good palette's swatch already looks harmonious.

## Retro conversion / reduction

- `s.to_palette("gameboy", dither=True)` — remap finished art to a preset (proper remap;
  never just swap the palette table).
- `s.quantize(12)` — reduce to the 12 best colors chosen from the art itself.

## Palette swaps (enemy variants)

Keep ramps positionally consistent, then `s.replace(old, new, frames="all", layers="all")`
per ramp step — a red slime from the green one in 5 lines. Design palettes so materials
occupy fixed index ranges (e.g. 0–4 body, 5–7 accent) to make swaps mechanical.

## Learned palettes

`study.py <file> --save-palette <name>` → stored in `references/learned/palettes.json`,
auto-loaded by pixelstudio at import. List available: `python3 -c "from pixelstudio import PALETTES; print(sorted(PALETTES))"`.
