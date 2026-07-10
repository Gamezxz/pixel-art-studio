#!/usr/bin/env python3
"""codex slime bounce sheet -> clean transparent GIF (+1x frames)."""
import sys, os
from PIL import Image

sys.path.insert(0, '/Users/game/Projects/pixel-art-studio/scripts')
from pixelstudio import Sprite

SRC, OUT, TARGET_H = sys.argv[1], sys.argv[2], int(sys.argv[3]) if len(sys.argv) > 3 else 64
os.makedirs(OUT, exist_ok=True)
N = 6

sheet = Image.open(SRC)
sp = Sprite.from_png(SRC, scale=sheet.height / TARGET_H)
sp.clean(max_colors=16, despeckle_min=2, dedupe_tol=6)
clean = sp.composite(1).convert('RGBA')

# global color-key on corner navy
px = clean.load(); w, h = clean.size
corner = px[0, 0]
for y in range(h):
    for x in range(w):
        c = px[x, y]
        if c[3] and ((sum(abs(c[i] - corner[i]) for i in range(3)) < 60)
                     or (c[2] > c[1] and c[0] < 80 and c[1] < 80)):
            px[x, y] = (0, 0, 0, 0)

# slice by empty column gaps
occ = [any(px[x, y][3] for y in range(h)) for x in range(w)]
runs = []; s = None
for x, o in enumerate(occ):
    if o and s is None: s = x
    if not o and s is not None: runs.append((s, x)); s = None
if s is not None: runs.append((s, w))
runs = [r for r in runs if r[1] - r[0] > 5][:N]
print('runs:', runs)

def outline(im, color=(20, 46, 26, 255)):
    im = im.copy(); p = im.load(); W, H = im.size
    edge = [(x, y) for y in range(H) for x in range(W)
            if p[x, y][3] == 0 and any(
                0 <= x+dx < W and 0 <= y+dy < H and p[x+dx, y+dy][3] > 0
                for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)))]
    for x, y in edge:
        p[x, y] = color
    return im

# uniform cells; keep each frame's own vertical placement (jump height is real),
# center horizontally only
cells = [clean.crop((x0, 0, x1, h)) for (x0, x1) in runs]
cw = max(c.width for c in cells) + 4
frames = []
for c in cells:
    f = Image.new('RGBA', (cw, h), (0, 0, 0, 0))
    f.paste(c, ((cw - c.width) // 2, 0), c)
    frames.append(outline(f))
ch = h

SCALE = 6
big = [f.resize((cw * SCALE, ch * SCALE), Image.NEAREST) for f in frames]
pal_frames = []
for f in big:
    q = f.convert('RGB').quantize(colors=255)
    pal = q.getpalette()
    alpha = f.getchannel('A').point(lambda a: 255 if a < 128 else 0)
    q.paste(255, mask=alpha)          # transparent index
    q.info['transparency'] = 255
    pal_frames.append(q)
gif = os.path.join(OUT, 'slime.gif')
pal_frames[0].save(gif, save_all=True, append_images=pal_frames[1:], loop=0,
                   duration=[130, 100, 90, 90, 90, 110], disposal=2,
                   transparency=255)
print('gif ->', gif)
frames[0].save(os.path.join(OUT, 'slime.png'))
