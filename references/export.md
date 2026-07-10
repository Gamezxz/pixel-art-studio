# Export — formats, scaling, engines

## Golden rules

- **PNG for stills, always.** Never JPEG/lossy-WebP — compression artifacts destroy pixels.
- **Integer scaling only** (1x, 2x, 4x, 8x — never 1.5x). `save_png(scale=)` enforces this.
- Always deliver the **1x master** alongside any display-scaled copy. The 1x file is the artwork.
- The preview contact-sheet is a working document, never a deliverable.

## What to export per use case

| Use | Call |
|---|---|
| still sprite, modern use | `save_png("name.png")` + `save_png("name@8x.png", scale=8)` |
| social/chat showing | `save_png(..., scale=8, bg="#e8e4da")` (or keep transparent) |
| animation for web/social | `save_gif("name.gif", scale=6, bg="#e8e4da")` — solid bg avoids GIF edge artifacts |
| animation, transparent | `save_gif("name.gif", scale=4)` — binary alpha only; edges must be crisp (no alpha-AA) |
| game engine | `save_spritesheet("sheet.png", layout="grid", padding=1)` → PNG + JSON |
| resumable work file | `save_project("name.pxproj.json")` |

## GIF caveats

256 colors max, alpha is on/off (semi-alpha px land on whichever side of 128).
Frame durations come from `set_duration`. Browsers clamp <20ms frames — stay ≥40ms.

## Spritesheet + JSON

Layouts: `horizontal` (CSS strips), `vertical`, `grid` (engines; near-square).
`padding=1..2` prevents texture bleeding in engines. JSON is Aseprite-compatible
(`frames[].frame/duration`, `meta.frameTags`) so any Aseprite importer works.

- **Unity**: grid layout, padding 1–2. Import → Sprite Mode: Multiple → slice by JSON coords (or Grid By Cell Size = frame size). Filter Mode: Point, Compression: None.
- **Godot**: grid/horizontal. AnimatedSprite2D + SpriteFrames, FPS = 1000/duration. Texture filter: Nearest.
- **Phaser**: `this.load.atlas('hero', 'sheet.png', 'sheet.json')`; frame names `frame_0`…; set `pixelArt: true` in game config.
- Engine display: nearest-neighbor filtering + integer camera zoom, or art goes blurry regardless of assets.

## File size sanity

16x16 indexed PNG ≈ 0.5–2 KB · 32x32 ≈ 1–4 KB · 256px sheet ≈ 10–30 KB.
A 32x32 PNG weighing 200 KB means something is wrong (saved at display scale? RGBA noise?).
GIF > 2 MB for a 4-frame loop → lower scale or frame count.
