#!/usr/bin/env python3
"""pixelstudio — Claude's direct pixel-art engine. Pillow only, no MCP, no Aseprite.

The artwork's source of truth is a build script that imports this module,
draws every pixel, and exports preview/PNG/GIF/spritesheet. Claude then LOOKS
at the preview, critiques, edits the script, and reruns.

Python 3.9+, Pillow 9+.
"""
from __future__ import annotations

import base64
import colorsys
import io
import json
import math
import os
import random as _random
from collections import Counter

from PIL import Image, ImageChops, ImageDraw, ImageFont

__version__ = "1.0.0"

_R = getattr(Image, "Resampling", Image)
NEAREST = _R.NEAREST
_D = getattr(Image, "Dither", Image)
DITHER_FS = _D.FLOYDSTEINBERG
DITHER_NONE = _D.NONE
_T = getattr(Image, "Transpose", Image)
FLIP_LR = _T.FLIP_LEFT_RIGHT
FLIP_TB = _T.FLIP_TOP_BOTTOM

# --------------------------------------------------------------------------
# Palettes
# --------------------------------------------------------------------------

PALETTES = {
    "onebit": ["#000000", "#ffffff"],
    "gameboy": ["#0f380f", "#306230", "#8bac0f", "#9bbc0f"],
    "pico8": ["#000000", "#1d2b53", "#7e2553", "#008751",
              "#ab5236", "#5f574f", "#c2c3c7", "#fff1e8",
              "#ff004d", "#ffa300", "#ffec27", "#00e436",
              "#29adff", "#83769c", "#ff77a8", "#ffccaa"],
    "sweetie16": ["#1a1c2c", "#5d275d", "#b13e53", "#ef7d57",
                  "#ffcd75", "#a7f070", "#38b764", "#257179",
                  "#29366f", "#3b5dc9", "#41a6f6", "#73eff7",
                  "#f4f4f4", "#94b0c2", "#566c86", "#333c57"],
    "c64": ["#000000", "#ffffff", "#68372b", "#70a4b2",
            "#6f3d86", "#588d43", "#352879", "#b8c76f",
            "#6f4f25", "#433900", "#9a6759", "#444444",
            "#6c6c6c", "#9ad284", "#6c5eb5", "#959595"],
    "endesga32": ["#be4a2f", "#d77643", "#ead4aa", "#e4a672", "#b86f50",
                  "#733e39", "#3e2731", "#a22633", "#e43b44", "#f77622",
                  "#feae34", "#fee761", "#63c74d", "#3e8948", "#265c42",
                  "#193c3e", "#124e89", "#0099db", "#2ce8f5", "#ffffff",
                  "#c0cbdc", "#8b9bb4", "#5a6988", "#3a4466", "#262b44",
                  "#181425", "#ff0044", "#68386c", "#b55088", "#f6757a",
                  "#e8b796", "#c28569"],
}

_LEARNED_PALETTES = os.path.normpath(os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "..", "references", "learned", "palettes.json"))


def _load_learned():
    try:
        with open(_LEARNED_PALETTES, "r") as f:
            data = json.load(f)
        for k, v in data.items():
            if isinstance(v, list) and v:
                PALETTES[k] = v
    except (OSError, ValueError):
        pass


_load_learned()

# --------------------------------------------------------------------------
# Color helpers
# --------------------------------------------------------------------------


def hex2rgba(c):
    """'#RGB' / '#RRGGBB' / '#RRGGBBAA' / (r,g,b[,a]) / None(=transparent) -> rgba tuple."""
    if c is None:
        return (0, 0, 0, 0)
    if isinstance(c, (tuple, list)):
        t = tuple(int(v) for v in c)
        return t if len(t) == 4 else t + (255,)
    s = str(c).strip().lstrip("#")
    if len(s) == 3:
        s = "".join(ch * 2 for ch in s)
    if len(s) == 6:
        s += "ff"
    return (int(s[0:2], 16), int(s[2:4], 16), int(s[4:6], 16), int(s[6:8], 16))


def rgba2hex(t):
    return "#%02x%02x%02x" % (t[0], t[1], t[2])


def _dist2(a, b):
    dr, dg, db = a[0] - b[0], a[1] - b[1], a[2] - b[2]
    return 30 * dr * dr + 59 * dg * dg + 11 * db * db


def _rgb_to_hsv(r, g, b):
    return colorsys.rgb_to_hsv(r / 255.0, g / 255.0, b / 255.0)


def nearest(color, palette_rgba):
    return min(palette_rgba, key=lambda p: _dist2(color, p))


def mix(c1, c2, t=0.5):
    """Blend two colors, returns hex."""
    a, b = hex2rgba(c1), hex2rgba(c2)
    return rgba2hex(tuple(round(a[i] + (b[i] - a[i]) * t) for i in range(3)) + (255,))


def _toward(h, target, amount):
    """Rotate hue h toward target by up to `amount` degrees (all in degrees)."""
    diff = ((target - h + 180.0) % 360.0) - 180.0
    step = max(-amount, min(amount, diff))
    return (h + step) % 360.0


def ramp(base, steps=5, hue_shift=14.0, dark=0.40, light=0.80):
    """Shading ramp (dark -> light) with proper hue shifting.

    Shadows rotate toward blue (240deg), highlights toward yellow (60deg).
    Saturation peaks at midtone. `dark`/`light` control how far value drops/rises.
    Middle color == base when steps is odd.
    """
    r, g, b, _ = hex2rgba(base)
    h, s, v = colorsys.rgb_to_hsv(r / 255.0, g / 255.0, b / 255.0)
    hdeg = h * 360.0
    v_dark = max(0.06, v * (1.0 - dark))
    v_light = min(1.0, v + (1.0 - v) * light)
    out = []
    for i in range(steps):
        t = i / (steps - 1) if steps > 1 else 0.5
        vv = v_dark + (v_light - v_dark) * t
        if t < 0.5:
            hh = _toward(hdeg, 240.0, (0.5 - t) * 2.0 * hue_shift)
            ss = min(1.0, s * (1.0 + 0.25 * (0.5 - t) * 2.0))
        else:
            hh = _toward(hdeg, 60.0, (t - 0.5) * 2.0 * hue_shift)
            ss = s * (1.0 - 0.45 * (t - 0.5) * 2.0)
        rr, gg, bb = colorsys.hsv_to_rgb(hh / 360.0, max(0.0, ss), max(0.0, min(1.0, vv)))
        out.append(rgba2hex((round(rr * 255), round(gg * 255), round(bb * 255), 255)))
    if steps % 2 == 1:
        out[steps // 2] = rgba2hex(hex2rgba(base))
    return out


# --------------------------------------------------------------------------
# Dither matrices
# --------------------------------------------------------------------------


def _expand(m):
    n = len(m)
    r = [[0] * (2 * n) for _ in range(2 * n)]
    for y in range(n):
        for x in range(n):
            v = 4 * m[y][x]
            r[y][x] = v
            r[y][x + n] = v + 2
            r[y + n][x] = v + 3
            r[y + n][x + n] = v + 1
    return r


BAYER2 = [[0, 2], [3, 1]]
BAYER4 = _expand(BAYER2)
BAYER8 = _expand(BAYER4)
_PATTERNS = {"bayer2": BAYER2, "bayer4": BAYER4, "bayer8": BAYER8, "checker": BAYER2}


# --------------------------------------------------------------------------
# Sprite
# --------------------------------------------------------------------------


class _Frame:
    __slots__ = ("duration", "cels")

    def __init__(self, duration=100):
        self.duration = duration
        self.cels = {}


class Sprite:
    """Frames x layers of RGBA cels. Frames and coordinates are what you expect:
    frames are 1-indexed, (0,0) is top-left, x right, y down. Drawing ops hit the
    *current* frame+layer. color = '#hex' | (r,g,b[,a]) | palette index | None=erase.
    """

    def __init__(self, width, height, palette=None, snap=True):
        self.w, self.h = int(width), int(height)
        self.snap = snap
        self.palette = None
        self._pal_rgb = set()
        if palette is not None:
            self.set_palette(palette, snap=snap)
        self.layer_order = ["main"]
        self.frames = [_Frame()]
        self.frames[0].cels["main"] = self._blank()
        self._f = 0
        self._l = "main"
        self.tags = {}

    # ---------------- internals ----------------

    def _blank(self):
        return Image.new("RGBA", (self.w, self.h), (0, 0, 0, 0))

    def _img(self):
        fr = self.frames[self._f]
        if self._l not in fr.cels:
            fr.cels[self._l] = self._blank()
        return fr.cels[self._l]

    def _c(self, color):
        if isinstance(color, bool):
            raise ValueError("color must not be a bool")
        if isinstance(color, int):
            if not self.palette:
                raise ValueError("palette index used but sprite has no palette")
            return self.palette[color % len(self.palette)]
        c = hex2rgba(color)
        if c[3] == 0:
            return (0, 0, 0, 0)
        if self.palette and self.snap and c[:3] not in self._pal_rgb:
            p = nearest(c, self.palette)
            return (p[0], p[1], p[2], c[3])
        return c

    def _only_ok(self, im, x, y, only):
        if only is None:
            return True
        cur = im.getpixel((x, y))
        if only == "opaque":
            return cur[3] > 0
        if only == "empty":
            return cur[3] == 0
        oc = hex2rgba(only) if not isinstance(only, int) else self.palette[only % len(self.palette)]
        return cur[3] > 0 and cur[:3] == oc[:3]

    def _put(self, im, x, y, c, only=None):
        if 0 <= x < self.w and 0 <= y < self.h:
            if self._only_ok(im, x, y, only):
                im.putpixel((x, y), c)

    # ---------------- selection / structure ----------------

    @property
    def n_frames(self):
        return len(self.frames)

    @property
    def current_frame(self):
        return self._f + 1

    @property
    def current_layer(self):
        return self._l

    def frame(self, i):
        if not 1 <= i <= len(self.frames):
            raise IndexError("frame %d of %d" % (i, len(self.frames)))
        self._f = i - 1
        return self

    def layer(self, name, above=None):
        """Create (if missing) and select a layer. New layers go on top, or above `above`."""
        if name not in self.layer_order:
            if above is not None and above in self.layer_order:
                self.layer_order.insert(self.layer_order.index(above) + 1, name)
            else:
                self.layer_order.append(name)
            for fr in self.frames:
                fr.cels.setdefault(name, self._blank())
        self._l = name
        return self

    def use(self, frame=None, layer=None):
        if frame is not None:
            self.frame(frame)
        if layer is not None:
            self.layer(layer)
        return self

    def add_frame(self, copy=True, duration=None, after=None):
        """Append a frame (or insert after frame index `after`). Copies current frame's cels
        by default. Selects the new frame. Returns its 1-based index."""
        src = self.frames[self._f]
        fr = _Frame(duration if duration is not None else src.duration)
        for name in self.layer_order:
            cel = src.cels.get(name)
            fr.cels[name] = cel.copy() if (copy and cel is not None) else self._blank()
        pos = len(self.frames) if after is None else int(after)
        self.frames.insert(pos, fr)
        self._f = pos
        return pos + 1

    def del_frame(self, i):
        if len(self.frames) <= 1:
            raise ValueError("cannot delete the last frame")
        self.frames.pop(i - 1)
        self._f = min(self._f, len(self.frames) - 1)

    def del_layer(self, name):
        if len(self.layer_order) <= 1:
            raise ValueError("cannot delete the last layer")
        self.layer_order.remove(name)
        for fr in self.frames:
            fr.cels.pop(name, None)
        if self._l == name:
            self._l = self.layer_order[-1]

    def copy_cel(self, layer=None, from_frame=None, to_frames="rest", link=False):
        """Copy one layer's cel to other frames (static background pattern).
        link=True shares the same image object: editing one edits all."""
        layer = layer or self._l
        from_frame = from_frame or self.current_frame
        src = self.frames[from_frame - 1].cels.get(layer)
        if src is None:
            return self
        if to_frames == "rest":
            targets = [i for i in range(1, len(self.frames) + 1) if i != from_frame]
        else:
            targets = list(to_frames)
        for i in targets:
            self.frames[i - 1].cels[layer] = src if link else src.copy()
        return self

    # ---------------- palette ----------------

    def set_palette(self, palette, snap=True, remap=False):
        cols = PALETTES[palette] if isinstance(palette, str) else palette
        self.palette = [hex2rgba(c) for c in cols]
        self._pal_rgb = set(p[:3] for p in self.palette)
        self.snap = snap
        if remap:
            for fr in getattr(self, "frames", []):
                for name, cel in fr.cels.items():
                    px = cel.load()
                    for y in range(self.h):
                        for x in range(self.w):
                            r, g, b, a = px[x, y]
                            if a > 0 and (r, g, b) not in self._pal_rgb:
                                n = nearest((r, g, b), self.palette)
                                px[x, y] = (n[0], n[1], n[2], a)
        return self

    def to_palette(self, palette, dither=False):
        """Remap every pixel to the given palette (retro conversion). Keeps layers/alpha."""
        cols = PALETTES[palette] if isinstance(palette, str) else palette
        triples = [hex2rgba(c)[:3] for c in cols]
        palimg = _pal_image(triples)
        for fr in self.frames:
            for name, cel in fr.cels.items():
                rgb = cel.convert("RGB")
                q = rgb.quantize(palette=palimg, dither=DITHER_FS if dither else DITHER_NONE)
                out = q.convert("RGB")
                out.putalpha(cel.split()[3])
                fr.cels[name] = out.convert("RGBA")
        self.set_palette(cols, snap=self.snap)
        return self

    def quantize(self, n, dither=True):
        """Flatten and reduce to n colors chosen adaptively from the art itself."""
        self.flatten()
        strip = Image.new("RGBA", (self.w, self.h * len(self.frames)), (0, 0, 0, 0))
        for i, fr in enumerate(self.frames):
            strip.paste(fr.cels["main"], (0, i * self.h))
        pal_src = strip.convert("RGB").quantize(colors=n)
        flat = pal_src.getpalette()[: n * 3]
        triples = [tuple(flat[i:i + 3]) for i in range(0, len(flat), 3)]
        self.to_palette([rgba2hex(t + (255,)) for t in triples], dither=dither)
        return self

    def flatten(self):
        for fr in self.frames:
            out = self._blank()
            for name in self.layer_order:
                cel = fr.cels.get(name)
                if cel is not None:
                    out = Image.alpha_composite(out, cel)
            fr.cels = {"main": out}
        self.layer_order = ["main"]
        self._l = "main"
        return self

    # ---------------- drawing primitives ----------------

    def px(self, x, y, color, only=None):
        self._put(self._img(), int(x), int(y), self._c(color), only)
        return self

    def get(self, x, y, composite=False):
        """RGBA tuple at (x,y) — None if transparent. composite=True reads merged layers."""
        if not (0 <= x < self.w and 0 <= y < self.h):
            return None
        im = self.composite(self.current_frame) if composite else self._img()
        c = im.getpixel((int(x), int(y)))
        return None if c[3] == 0 else c

    def line(self, x0, y0, x1, y1, color, only=None):
        """Bresenham line — one pixel per step, no doubles."""
        im, c = self._img(), self._c(color)
        x0, y0, x1, y1 = int(x0), int(y0), int(x1), int(y1)
        dx, dy = abs(x1 - x0), -abs(y1 - y0)
        sx, sy = (1 if x0 < x1 else -1), (1 if y0 < y1 else -1)
        err = dx + dy
        while True:
            self._put(im, x0, y0, c, only)
            if x0 == x1 and y0 == y1:
                break
            e2 = 2 * err
            if e2 >= dy:
                err += dy
                x0 += sx
            if e2 <= dx:
                err += dx
                y0 += sy
        return self

    def rect(self, x0, y0, x1, y1, color, fill=True, only=None):
        im, c = self._img(), self._c(color)
        x0, x1 = sorted((int(x0), int(x1)))
        y0, y1 = sorted((int(y0), int(y1)))
        for y in range(y0, y1 + 1):
            for x in range(x0, x1 + 1):
                if fill or x in (x0, x1) or y in (y0, y1):
                    self._put(im, x, y, c, only)
        return self

    def circle(self, cx, cy, r, color, fill=False, only=None):
        """Pixel-perfect midpoint circle (odd diameter 2r+1). Use this, not ellipse(),
        for small round shapes — PIL's ellipse is lopsided at small sizes."""
        im, c = self._img(), self._c(color)
        cx, cy, r = int(cx), int(cy), int(r)
        pts = set()
        x, y, d = r, 0, 3 - 2 * r
        while y <= x:
            for px_, py_ in ((x, y), (y, x), (-x, y), (-y, x),
                             (x, -y), (y, -x), (-x, -y), (-y, -x)):
                pts.add((cx + px_, cy + py_))
            if d <= 0:
                d += 4 * y + 6
            else:
                d += 4 * (y - x) + 10
                x -= 1
            y += 1
        if fill:
            rows = {}
            for px_, py_ in pts:
                lo, hi = rows.get(py_, (px_, px_))
                rows[py_] = (min(lo, px_), max(hi, px_))
            for py_, (lo, hi) in rows.items():
                for px_ in range(lo, hi + 1):
                    self._put(im, px_, py_, c, only)
        else:
            for px_, py_ in pts:
                self._put(im, px_, py_, c, only)
        return self

    def ellipse(self, x0, y0, x1, y1, color, fill=True, only=None):
        """PIL-backed ellipse — fine for blobs >= ~12px; for small circles use circle()."""
        c = self._c(color)
        tmp = Image.new("RGBA", (self.w, self.h), (0, 0, 0, 0))
        d = ImageDraw.Draw(tmp)
        d.ellipse([int(x0), int(y0), int(x1), int(y1)],
                  fill=c if fill else None, outline=None if fill else c, width=1)
        self._stamp(tmp, only)
        return self

    def polygon(self, points, color, fill=True, only=None):
        c = self._c(color)
        tmp = Image.new("RGBA", (self.w, self.h), (0, 0, 0, 0))
        d = ImageDraw.Draw(tmp)
        pts = [(int(x), int(y)) for x, y in points]
        if fill:
            d.polygon(pts, fill=c)
        else:
            d.line(pts + [pts[0]], fill=c, width=1)
        self._stamp(tmp, only)
        return self

    def _stamp(self, tmp, only):
        im = self._img()
        tp = tmp.load()
        for y in range(self.h):
            for x in range(self.w):
                c = tp[x, y]
                if c[3] > 0:
                    self._put(im, x, y, c, only)

    def contour(self, points, color, close=True, only=None):
        pts = [(int(x), int(y)) for x, y in points]
        for i in range(len(pts) - 1):
            self.line(pts[i][0], pts[i][1], pts[i + 1][0], pts[i + 1][1], color, only)
        if close and len(pts) > 2:
            self.line(pts[-1][0], pts[-1][1], pts[0][0], pts[0][1], color, only)
        return self

    def fill(self, x, y, color):
        """Flood fill from (x,y). Leaks through diagonal gaps only if truly connected 4-way."""
        if 0 <= x < self.w and 0 <= y < self.h:
            ImageDraw.floodfill(self._img(), (int(x), int(y)), self._c(color))
        return self

    def clear(self, color=None):
        c = self._c(color)
        self.frames[self._f].cels[self._l] = Image.new("RGBA", (self.w, self.h), c)
        return self

    # ---------------- pixel-art operations ----------------

    def dither(self, x0, y0, x1, y1, c1, c2, mix=0.5, pattern="bayer4", only=None):
        """Ordered dither over a rect: each px becomes c2 where mix > threshold, else c1.
        c1 or c2 = "keep" leaves the pixel untouched; None erases. only= clips (color,
        "opaque", "empty")."""
        im = self._img()
        m = _PATTERNS[pattern]
        n = len(m)
        n2 = n * n
        cc1 = None if c1 == "keep" else self._c(c1)
        cc2 = None if c2 == "keep" else self._c(c2)
        x0, x1 = sorted((int(x0), int(x1)))
        y0, y1 = sorted((int(y0), int(y1)))
        for y in range(y0, y1 + 1):
            for x in range(x0, x1 + 1):
                thr = (m[y % n][x % n] + 0.5) / n2
                c = cc2 if mix > thr else cc1
                if c is not None:
                    self._put(im, x, y, c, only)
        return self

    def gradient_dither(self, x0, y0, x1, y1, colors, axis="v", pattern="bayer4", only=None):
        """Banded gradient with dithered transitions across a rect. colors = dark->light list."""
        im = self._img()
        m = _PATTERNS[pattern]
        n = len(m)
        n2 = n * n
        cols = [self._c(c) for c in colors]
        k = len(cols)
        x0, x1 = sorted((int(x0), int(x1)))
        y0, y1 = sorted((int(y0), int(y1)))
        span = max(1, (y1 - y0) if axis == "v" else (x1 - x0))
        for y in range(y0, y1 + 1):
            for x in range(x0, x1 + 1):
                t = ((y - y0) if axis == "v" else (x - x0)) / span
                pos = t * (k - 1)
                i = min(int(pos), k - 2) if k > 1 else 0
                f = pos - i
                thr = (m[y % n][x % n] + 0.5) / n2
                c = cols[i + 1] if (k > 1 and f > thr) else cols[i]
                self._put(im, x, y, c, only)
        return self

    def noise(self, x0, y0, x1, y1, color, density=0.12, seed=0, only=None):
        """Deterministic speckle (stone/grain). Same seed -> same result every render."""
        im, c = self._img(), self._c(color)
        rng = _random.Random(seed)
        x0, x1 = sorted((int(x0), int(x1)))
        y0, y1 = sorted((int(y0), int(y1)))
        for y in range(y0, y1 + 1):
            for x in range(x0, x1 + 1):
                if rng.random() < density:
                    self._put(im, x, y, c, only)
        return self

    def outline(self, color, where="outside", diagonals=False):
        """Outline the current cel's silhouette. outside = new px on transparent neighbors
        (leave a 1px margin in the canvas!); inside = recolor the border px (selout)."""
        im = self._img()
        c = self._c(color)
        src = im.load()
        alpha = [[src[x, y][3] > 0 for x in range(self.w)] for y in range(self.h)]
        nb = [(1, 0), (-1, 0), (0, 1), (0, -1)]
        if diagonals:
            nb += [(1, 1), (1, -1), (-1, 1), (-1, -1)]
        todo = []
        for y in range(self.h):
            for x in range(self.w):
                if where == "outside" and not alpha[y][x]:
                    if any(0 <= x + dx < self.w and 0 <= y + dy < self.h and alpha[y + dy][x + dx]
                           for dx, dy in nb):
                        todo.append((x, y))
                elif where == "inside" and alpha[y][x]:
                    if any(not (0 <= x + dx < self.w and 0 <= y + dy < self.h)
                           or not alpha[y + dy][x + dx] for dx, dy in nb):
                        todo.append((x, y))
        for x, y in todo:
            src[x, y] = c
        return self

    def replace(self, old, new, frames=None, layers=None):
        """Swap a color. frames: None=current | 'all' | list. layers: None=current | 'all' | list."""
        oc = self._c(old) if isinstance(old, int) else hex2rgba(old)
        nc = self._c(new)
        fidx = ([self._f] if frames is None else
                range(len(self.frames)) if frames == "all" else [i - 1 for i in frames])
        lnames = ([self._l] if layers is None else
                  self.layer_order if layers == "all" else list(layers))
        for fi in fidx:
            for ln in lnames:
                cel = self.frames[fi].cels.get(ln)
                if cel is None:
                    continue
                p = cel.load()
                for y in range(self.h):
                    for x in range(self.w):
                        r, g, b, a = p[x, y]
                        if a > 0 and (r, g, b) == oc[:3]:
                            p[x, y] = (nc[0], nc[1], nc[2], a if nc[3] == 255 else nc[3])
        return self

    def mirror_x(self, source="left"):
        """Copy one half onto the other, flipped (symmetric characters). Odd width keeps
        the middle column. Then BREAK the symmetry a little — perfect mirror reads robotic."""
        im = self._img()
        half = self.w // 2
        if source == "left":
            part = im.crop((0, 0, half, self.h)).transpose(FLIP_LR)
            im.paste(part, (self.w - half, 0))
        else:
            part = im.crop((self.w - half, 0, self.w, self.h)).transpose(FLIP_LR)
            im.paste(part, (0, 0))
        return self

    def mirror_y(self, source="top"):
        im = self._img()
        half = self.h // 2
        if source == "top":
            part = im.crop((0, 0, self.w, half)).transpose(FLIP_TB)
            im.paste(part, (0, self.h - half))
        else:
            part = im.crop((0, self.h - half, self.w, self.h)).transpose(FLIP_TB)
            im.paste(part, (0, 0))
        return self

    def shift(self, dx, dy, wrap=False):
        """Move the current cel. wrap=True scrolls (seamless-tile inspection!)."""
        im = self._img()
        if wrap:
            self.frames[self._f].cels[self._l] = ImageChops.offset(im, int(dx), int(dy))
        else:
            out = self._blank()
            out.paste(im, (int(dx), int(dy)))
            self.frames[self._f].cels[self._l] = out
        return self

    def paste_png(self, path, x=0, y=0):
        """Stamp an external PNG onto the current cel (alpha-respecting)."""
        im = self._img()
        stamp = Image.open(path).convert("RGBA")
        im.alpha_composite(stamp, (int(x), int(y)))
        return self

    # ---------------- pixel-grid cleanup (for imported/generated art) ----------------

    def _iter_cels(self, frames, layers):
        fidx = ([self._f] if frames is None else
                range(len(self.frames)) if frames == "all" else [i - 1 for i in frames])
        lnames = ([self._l] if layers is None else
                  self.layer_order if layers == "all" else list(layers))
        for fi in fidx:
            for ln in lnames:
                cel = self.frames[fi].cels.get(ln)
                if cel is not None:
                    yield fi, ln, cel

    def harden_alpha(self, threshold=128, steps=None, frames=None, layers=None):
        """Snap semi-transparent pixels. threshold: alpha<threshold -> 0, else 255 (kills AA
        fuzz + bg halos). steps: e.g. [0,64,160,255] quantizes alpha to discrete levels
        (preserve painterly AA edges as a few alpha steps instead of binary)."""
        for fi, ln, cel in self._iter_cels(frames, layers):
            px = cel.load()
            for y in range(self.h):
                for x in range(self.w):
                    r, g, b, a = px[x, y]
                    if a == 0 or a == 255:
                        continue
                    if steps:
                        nv = min(steps, key=lambda v: abs(v - a))
                        px[x, y] = (r, g, b, nv)
                    else:
                        px[x, y] = (r, g, b, 255 if a >= threshold else 0)
        return self

    def despeckle(self, min_cluster=2, frames=None, layers=None):
        """Remove isolated pixel clusters: connected components (4-way) of opaque pixels
        smaller than min_cluster become transparent. Kills orphan noise from model output
        without touching legitimate detail."""
        for fi, ln, cel in self._iter_cels(frames, layers):
            px = cel.load()
            seen = [[False] * self.w for _ in range(self.h)]
            kill = []
            for sy in range(self.h):
                for sx in range(self.w):
                    if seen[sy][sx] or px[sx, sy][3] == 0:
                        continue
                    stack, comp = [(sx, sy)], []
                    while stack:
                        cx, cy = stack.pop()
                        if cx < 0 or cy < 0 or cx >= self.w or cy >= self.h:
                            continue
                        if seen[cy][cx] or px[cx, cy][3] == 0:
                            continue
                        seen[cy][cx] = True
                        comp.append((cx, cy))
                        stack.extend([(cx + 1, cy), (cx - 1, cy), (cx, cy + 1), (cx, cy - 1)])
                    if len(comp) < min_cluster:
                        kill.extend(comp)
            for cx, cy in kill:
                px[cx, cy] = (0, 0, 0, 0)
        return self

    def dedupe_colors(self, tol=12, frames=None, layers=None):
        """Merge colors within `tol` (max channel distance) into their most-used
        representative. Collapses the near-duplicate color explosion typical of model output."""
        reps = {}
        for fi, ln, cel in self._iter_cels(frames, layers):
            px = cel.load()
            for y in range(self.h):
                for x in range(self.w):
                    r, g, b, a = px[x, y]
                    if a == 0:
                        continue
                    key = (r, g, b)
                    if key in reps:
                        continue
                    rep = None
                    for cand in reps:
                        if max(abs(cand[k] - key[k]) for k in range(3)) <= tol:
                            rep = cand
                            break
                    reps[key] = rep if rep is not None else key
            for y in range(self.h):
                for x in range(self.w):
                    r, g, b, a = px[x, y]
                    if a == 0:
                        continue
                    rep = reps[(r, g, b)]
                    if rep != (r, g, b):
                        px[x, y] = (rep[0], rep[1], rep[2], a)
        if self.palette:
            self._pal_rgb = set(p[:3] for p in self.palette)
        return self

    def dehalo(self, sat_floor=0.10, val_floor=0.15, frames=None, layers=None):
        """Detect opaque edge pixels that are color-contaminated by a former background
        (low-saturation ring from AA against white/dark bg) and snap them toward the
        average of their opaque neighbors. Conservative: only touches low-saturation edge px."""
        for fi, ln, cel in self._iter_cels(frames, layers):
            px = cel.load()
            todo = []
            for y in range(self.h):
                for x in range(self.w):
                    r, g, b, a = px[x, y]
                    if a < 255:
                        continue
                    is_edge = False
                    nab = []
                    for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                        nx, ny = x + dx, y + dy
                        if 0 <= nx < self.w and 0 <= ny < self.h:
                            nr, ng, nb, na = px[nx, ny]
                            if na == 0:
                                is_edge = True
                            else:
                                nab.append((nr, ng, nb))
                        else:
                            is_edge = True
                    if not is_edge or not nab:
                        continue
                    hh, ss, vv = _rgb_to_hsv(r, g, b)
                    if ss > sat_floor or vv < val_floor or vv > (1 - val_floor):
                        continue   # only wash out low-sat edge contamination
                    avg = tuple(sum(c[i] for c in nab) // len(nab) for i in range(3))
                    todo.append((x, y, avg))
            for x, y, avg in todo:
                _, _, _, a = px[x, y]
                px[x, y] = (avg[0], avg[1], avg[2], a)
        return self

    def clean(self, palette=None, max_colors=None, dither=False,
              harden=True, harden_steps=None, despeckle_min=2, dedupe_tol=10,
              dehalo=False, flatten=True):
        """Full cleanup pipeline for imported/generated art. Order matters:

            flatten → harden alpha → despeckle → dedupe colors → dehalo → palette lock

        - harden: kill AA fuzz + bg halos (set False only for painterly alpha art).
        - despeckle_min: remove orphan clusters smaller than this (2 = single pixels).
        - dedupe_tol: merge near-duplicate colors within this channel distance.
        - palette: lock to a named/learned palette (cross-asset consistency). Needs >=1 frame.
        - max_colors: if no palette, reduce to N colors chosen from the art itself.
        Run stats() before/after to see colors_used + semi_alpha collapse."""
        if flatten:
            self.flatten()
        if harden:
            self.harden_alpha(steps=harden_steps)
        if despeckle_min and despeckle_min > 1:
            self.despeckle(min_cluster=despeckle_min)
        if dedupe_tol:
            self.dedupe_colors(tol=dedupe_tol)
        if dehalo:
            self.dehalo()
        if palette:
            self.to_palette(palette, dither=dither)
        elif max_colors:
            self.quantize(max_colors, dither=dither)
        return self

    def before_after(self, path, scale=6, bg="checker"):
        """Side-by-side contact sheet: requires the sprite to carry a ._orig snapshot
        (set by pixelpipe). Falls back to current-only if absent."""
        orig = getattr(self, "_orig", None)
        cur = self.composite(self.current_frame)
        arts = [("input", orig), ("cleaned", cur)] if orig is not None else [("frame", cur)]
        n = len(arts)
        cw, chh = self.w * scale, self.h * scale
        sep = 6
        W = n * cw + (n + 1) * sep
        H = chh + 16 + 2 * sep
        sheet = Image.new("RGB", (W, H), (90, 90, 90))
        font = ImageFont.load_default()
        for i, (label, im) in enumerate(arts):
            ox = sep + i * (cw + sep)
            ImageDraw.Draw(sheet).text((ox + 3, 2), label, fill=(240, 240, 240), font=font)
            cbg = (self._checker_bg(cw, chh) if bg == "checker"
                   else Image.new("RGB", (cw, chh), hex2rgba(bg)[:3])).convert("RGBA")
            cbg.alpha_composite(self._scaled(im, scale))
            sheet.paste(cbg.convert("RGB"), (ox, 16))
        _mkdirs(path)
        sheet.save(path)
        print("before/after -> %s" % path)
        return self

    # ---------------- animation ----------------

    def set_duration(self, ms, frames=None):
        """frames: None=current | 'all' | list of 1-based indices."""
        if frames is None:
            self.frames[self._f].duration = int(ms)
        elif frames == "all":
            for fr in self.frames:
                fr.duration = int(ms)
        else:
            for i in frames:
                self.frames[i - 1].duration = int(ms)
        return self

    def tag(self, name, from_frame, to_frame, direction="forward"):
        if not (1 <= from_frame <= to_frame <= len(self.frames)):
            raise ValueError("bad tag range %d-%d" % (from_frame, to_frame))
        self.tags[name] = {"from": from_frame, "to": to_frame, "direction": direction}
        return self

    def _tag_frames(self, tag):
        if tag is None:
            return list(range(len(self.frames)))
        t = self.tags[tag]
        idx = list(range(t["from"] - 1, t["to"]))
        if t["direction"] == "reverse":
            idx = idx[::-1]
        elif t["direction"] in ("pingpong", "ping-pong"):
            idx = idx + idx[-2:0:-1]
        return idx

    # ---------------- inspection ----------------

    def composite(self, frame=None):
        fr = self.frames[(frame or self.current_frame) - 1]
        out = self._blank()
        for name in self.layer_order:
            cel = fr.cels.get(name)
            if cel is not None:
                out = Image.alpha_composite(out, cel)
        return out

    def used_colors(self, frame=None, all_frames=False):
        cnt = Counter()
        targets = range(1, len(self.frames) + 1) if all_frames else [frame or self.current_frame]
        for i in targets:
            for r, g, b, a in self.composite(i).getdata():
                if a > 0:
                    cnt[(r, g, b)] += 1
        return cnt

    def stats(self, print_=True):
        cnt = self.used_colors(all_frames=True)
        semi = 0
        for i in range(1, len(self.frames) + 1):
            for _, _, _, a in self.composite(i).getdata():
                if 0 < a < 255:
                    semi += 1
        iso = []
        im = self.composite(self.current_frame)
        p = im.load()
        for y in range(self.h):
            for x in range(self.w):
                if p[x, y][3] > 0:
                    if not any(0 <= x + dx < self.w and 0 <= y + dy < self.h
                               and p[x + dx, y + dy][3] > 0
                               for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1))):
                        iso.append((x, y))
        cols = list(cnt.keys())
        dups = []
        for i in range(len(cols)):
            for j in range(i + 1, len(cols)):
                if max(abs(cols[i][k] - cols[j][k]) for k in range(3)) <= 12:
                    dups.append((rgba2hex(cols[i] + (255,)), rgba2hex(cols[j] + (255,))))
        info = {
            "size": (self.w, self.h),
            "frames": len(self.frames),
            "layers": list(self.layer_order),
            "durations": [fr.duration for fr in self.frames],
            "tags": dict(self.tags),
            "colors_used": len(cnt),
            "palette_size": len(self.palette) if self.palette else None,
            "top_colors": [(rgba2hex(c + (255,)), n) for c, n in cnt.most_common(24)],
            "semi_alpha_px": semi,
            "isolated_px": iso[:20],
            "near_duplicate_colors": dups[:10],
        }
        if print_:
            print("pixelstudio stats -----------------------------")
            print(" size %dx%d | frames %d | layers %s" % (self.w, self.h, info["frames"], ",".join(info["layers"])))
            print(" durations %s | tags %s" % (info["durations"], list(self.tags.keys()) or "-"))
            print(" colors used %d%s" % (info["colors_used"],
                  " / palette %d" % info["palette_size"] if info["palette_size"] else ""))
            print("  " + "  ".join("%s x%d" % cn for cn in info["top_colors"][:12]))
            print(" semi-alpha px: %d | isolated px: %s | near-dup colors: %s" % (
                semi, iso[:8] or "none", dups[:4] or "none"))
            print("-----------------------------------------------")
        return info

    # ---------------- preview / export ----------------

    def _scaled(self, im, scale):
        scale = int(scale)
        if scale < 1:
            raise ValueError("scale must be integer >= 1 (integer scaling only!)")
        if scale == 1:
            return im
        return im.resize((im.width * scale, im.height * scale), NEAREST)

    def _grid_overlay(self, wpx, hpx, scale):
        ov = Image.new("RGBA", (wpx, hpx), (0, 0, 0, 0))
        d = ImageDraw.Draw(ov)
        for gx in range(1, wpx // scale):
            a = 90 if gx % 8 == 0 else 36
            d.line([(gx * scale, 0), (gx * scale, hpx)], fill=(0, 0, 0, a))
        for gy in range(1, hpx // scale):
            a = 90 if gy % 8 == 0 else 36
            d.line([(0, gy * scale), (wpx, gy * scale)], fill=(0, 0, 0, a))
        return ov

    @staticmethod
    def _checker_bg(wpx, hpx, sq=8):
        bg = Image.new("RGB", (wpx, hpx), (232, 232, 232))
        d = ImageDraw.Draw(bg)
        for y in range(0, hpx, sq):
            for x in range(0, wpx, sq):
                if (x // sq + y // sq) % 2:
                    d.rectangle([x, y, x + sq - 1, y + sq - 1], fill=(203, 203, 203))
        return bg

    def preview(self, path, scale=8, bg="checker", grid=False, labels=True, cols=8, frames=None):
        """Contact sheet of frames, upscaled — THE image to Read and critique."""
        idx = [f - 1 for f in frames] if frames else list(range(len(self.frames)))
        n = len(idx)
        cols = max(1, min(cols, n))
        rows = math.ceil(n / cols)
        cw, chh = self.w * scale, self.h * scale
        lh = 16 if labels else 0
        sep = 2
        W = cols * cw + (cols + 1) * sep
        H = rows * (chh + lh) + (rows + 1) * sep
        sheet = Image.new("RGB", (W, H), (90, 90, 90))
        font = ImageFont.load_default()
        for k, fi in enumerate(idx):
            r, c = divmod(k, cols)
            ox = sep + c * (cw + sep)
            oy = sep + r * (chh + lh + sep)
            if labels:
                ImageDraw.Draw(sheet).rectangle([ox, oy, ox + cw - 1, oy + lh - 1], fill=(240, 240, 240))
                ImageDraw.Draw(sheet).text((ox + 3, oy + 2), "%d  %dms" % (fi + 1, self.frames[fi].duration),
                                           fill=(60, 60, 60), font=font)
            cell_bg = self._checker_bg(cw, chh) if bg == "checker" else Image.new(
                "RGB", (cw, chh), hex2rgba(bg)[:3])
            art = self._scaled(self.composite(fi + 1), scale)
            cell = cell_bg.convert("RGBA")
            cell.alpha_composite(art)
            if grid and scale >= 4:
                cell.alpha_composite(self._grid_overlay(cw, chh, scale))
            sheet.paste(cell.convert("RGB"), (ox, oy + lh))
        _mkdirs(path)
        sheet.save(path)
        print("preview -> %s  (%d frame%s @%dx)" % (path, n, "s" if n > 1 else "", scale))
        return self

    def zoom(self, path, x0, y0, x1, y1, frame=None, scale=16, grid=True, bg="checker"):
        """Magnified crop for detailed inspection. Box is inclusive pixel coords."""
        x0, x1 = sorted((max(0, int(x0)), min(self.w - 1, int(x1))))
        y0, y1 = sorted((max(0, int(y0)), min(self.h - 1, int(y1))))
        crop = self.composite(frame).crop((x0, y0, x1 + 1, y1 + 1))
        art = self._scaled(crop, scale)
        base = (self._checker_bg(art.width, art.height) if bg == "checker"
                else Image.new("RGB", (art.width, art.height), hex2rgba(bg)[:3])).convert("RGBA")
        base.alpha_composite(art)
        if grid:
            base.alpha_composite(self._grid_overlay(art.width, art.height, scale))
        _mkdirs(path)
        base.convert("RGB").save(path)
        print("zoom (%d,%d)-(%d,%d) -> %s" % (x0, y0, x1, y1, path))
        return self

    def save_silhouette(self, path, frame=None, scale=8, fg="#22242e", bg="#e8e4da"):
        """Silhouette test image: if the subject doesn't read here, redesign the shape."""
        im = self.composite(frame)
        f, b = hex2rgba(fg), hex2rgba(bg)
        out = Image.new("RGB", (self.w, self.h), b[:3])
        p = out.load()
        src = im.load()
        for y in range(self.h):
            for x in range(self.w):
                if src[x, y][3] > 0:
                    p[x, y] = f[:3]
        _mkdirs(path)
        self._scaled(out, scale).save(path)
        print("silhouette -> %s" % path)
        return self

    def save_swatch(self, path, cell=28):
        cols = self.palette or [c + (255,) for c, _ in self.used_colors().most_common()]
        n = len(cols)
        img = Image.new("RGB", (n * cell, cell + 14), (250, 250, 250))
        d = ImageDraw.Draw(img)
        font = ImageFont.load_default()
        for i, c in enumerate(cols):
            d.rectangle([i * cell, 14, (i + 1) * cell - 1, cell + 13], fill=c[:3])
            d.text((i * cell + 2, 1), str(i), fill=(60, 60, 60), font=font)
        _mkdirs(path)
        img.save(path)
        print("swatch -> %s  (%s)" % (path, " ".join(rgba2hex(c) for c in cols)))
        return self

    def save_png(self, path, frame=None, scale=1, bg=None, layer=None):
        if layer:
            im = self.frames[(frame or self.current_frame) - 1].cels.get(layer, self._blank()).copy()
        else:
            im = self.composite(frame)
        if bg is not None:
            base = Image.new("RGBA", im.size, hex2rgba(bg))
            base.alpha_composite(im)
            im = base
        _mkdirs(path)
        self._scaled(im, scale).save(path)
        print("png -> %s (%dx%d @%dx)" % (path, self.w, self.h, scale))
        return self

    def save_gif(self, path, scale=4, tag=None, loop=0, bg=None):
        """Animated GIF. bg=None keeps binary transparency; give a bg color for social posts."""
        idx = self._tag_frames(tag)
        imgs = [self._scaled(self.composite(i + 1), scale) for i in idx]
        durs = [self.frames[i].duration for i in idx]
        if bg is not None:
            b = hex2rgba(bg)
            merged = []
            for im in imgs:
                base = Image.new("RGBA", im.size, b)
                base.alpha_composite(im)
                merged.append(base)
            imgs = merged
        transparent = bg is None and any(px[3] < 128 for im in imgs for px in im.getdata())
        limit = 254 if transparent else 255
        cnt = Counter()
        for im in imgs:
            for r, g, b2, a in im.getdata():
                if a >= 128:
                    cnt[(r, g, b2)] += 1
        colors = [c for c, _ in cnt.most_common()]
        if len(colors) > limit:
            strip = Image.new("RGB", (imgs[0].width, imgs[0].height * len(imgs)),
                              colors[0] if colors else (0, 0, 0))
            for i, im in enumerate(imgs):
                strip.paste(im.convert("RGB"), (0, i * im.height), im.split()[3])
            q = strip.quantize(colors=limit)
            flat = q.getpalette()[: limit * 3]
            colors = [tuple(flat[i:i + 3]) for i in range(0, len(flat), 3)]
            palimg = _pal_image(colors)
            remapped = []
            for im in imgs:
                rgbq = im.convert("RGB").quantize(palette=palimg, dither=DITHER_NONE).convert("RGB")
                out = rgbq.convert("RGBA")
                out.putalpha(im.split()[3])
                remapped.append(out)
            imgs = remapped
        lut = {c: i for i, c in enumerate(colors)}
        tindex = len(colors) if transparent else None
        flat = []
        for c in colors:
            flat.extend(c)
        if tindex is not None:
            flat.extend((255, 0, 255))
        while len(flat) < 768:
            flat.extend((0, 0, 0))
        frames_p = []
        for im in imgs:
            data = []
            for r, g, b2, a in im.getdata():
                if transparent and a < 128:
                    data.append(tindex)
                else:
                    data.append(lut.get((r, g, b2), 0))
            p = Image.new("P", im.size)
            p.putpalette(flat)
            p.putdata(data)
            frames_p.append(p)
        _mkdirs(path)
        kw = dict(save_all=True, append_images=frames_p[1:], duration=durs, loop=loop,
                  disposal=2, optimize=False)
        if tindex is not None:
            kw["transparency"] = tindex
        frames_p[0].save(path, **kw)
        print("gif -> %s (%d frames @%dx, %s)" % (
            path, len(frames_p), scale, "transparent" if transparent else "opaque"))
        return self

    def save_spritesheet(self, path, layout="grid", scale=1, padding=0, json_path="auto",
                         tag=None, bg=None):
        """PNG sheet + Aseprite-compatible JSON (frames, durations, frameTags)."""
        idx = self._tag_frames(tag)
        if tag and self.tags[tag]["direction"] != "forward":
            idx = list(range(self.tags[tag]["from"] - 1, self.tags[tag]["to"]))
        n = len(idx)
        fw, fh = self.w * scale, self.h * scale
        if layout == "horizontal":
            cols, rows = n, 1
        elif layout == "vertical":
            cols, rows = 1, n
        else:
            cols = math.ceil(math.sqrt(n))
            rows = math.ceil(n / cols)
        W = cols * fw + (cols + 1) * padding
        H = rows * fh + (rows + 1) * padding
        sheet = Image.new("RGBA", (W, H), hex2rgba(bg) if bg else (0, 0, 0, 0))
        frames_meta = []
        for k, fi in enumerate(idx):
            r, c = divmod(k, cols)
            x = padding + c * (fw + padding)
            y = padding + r * (fh + padding)
            sheet.alpha_composite(self._scaled(self.composite(fi + 1), scale), (x, y))
            frames_meta.append({
                "filename": "frame_%d" % k,
                "frame": {"x": x, "y": y, "w": fw, "h": fh},
                "rotated": False, "trimmed": False,
                "spriteSourceSize": {"x": 0, "y": 0, "w": fw, "h": fh},
                "sourceSize": {"w": fw, "h": fh},
                "duration": self.frames[fi].duration,
            })
        _mkdirs(path)
        sheet.save(path)
        meta = {
            "frames": frames_meta,
            "meta": {
                "app": "pixelstudio", "version": __version__,
                "image": os.path.basename(path), "format": "RGBA8888",
                "size": {"w": W, "h": H}, "scale": str(scale),
                "frameTags": [
                    {"name": name, "from": t["from"] - 1, "to": t["to"] - 1,
                     "direction": t["direction"]}
                    for name, t in self.tags.items()
                ] if tag is None else [
                    {"name": tag, "from": 0, "to": n - 1,
                     "direction": self.tags[tag]["direction"]}
                ],
            },
        }
        if json_path == "auto":
            json_path = os.path.splitext(path)[0] + ".json"
        if json_path:
            with open(json_path, "w") as f:
                json.dump(meta, f, indent=1)
        print("spritesheet -> %s (%dx%d, %d frames, %s)%s" % (
            path, W, H, n, layout, " + json" if json_path else ""))
        return self

    # ---------------- project io ----------------

    def save_project(self, path):
        data = {
            "pixelstudio": __version__,
            "w": self.w, "h": self.h,
            "snap": self.snap,
            "palette": [rgba2hex(c) for c in self.palette] if self.palette else None,
            "layer_order": self.layer_order,
            "tags": self.tags,
            "frames": [],
        }
        for fr in self.frames:
            cels = {}
            for name, cel in fr.cels.items():
                buf = io.BytesIO()
                cel.save(buf, "PNG")
                cels[name] = base64.b64encode(buf.getvalue()).decode()
            data["frames"].append({"duration": fr.duration, "cels": cels})
        _mkdirs(path)
        with open(path, "w") as f:
            json.dump(data, f)
        print("project -> %s" % path)
        return self

    @classmethod
    def load_project(cls, path):
        with open(path) as f:
            data = json.load(f)
        sp = cls(data["w"], data["h"],
                 palette=data.get("palette"), snap=data.get("snap", True))
        sp.layer_order = list(data["layer_order"])
        sp.tags = {k: dict(v) for k, v in data.get("tags", {}).items()}
        sp.frames = []
        for frd in data["frames"]:
            fr = _Frame(frd.get("duration", 100))
            for name, b64 in frd["cels"].items():
                fr.cels[name] = Image.open(io.BytesIO(base64.b64decode(b64))).convert("RGBA")
            sp.frames.append(fr)
        sp._f, sp._l = 0, sp.layer_order[0]
        return sp

    @classmethod
    def from_png(cls, path, scale="auto", max_colors=None, strip_bg=False):
        """Import art and recover true pixels.

        scale: 'auto' (detect; falls back to run-length estimate for sloppy upscales),
        an int, or a float (forced block sampling — best for resampled model output).
        strip_bg: remove baked-in checkerboard before processing.
        max_colors: quantize to N colors after import.
        """
        im = Image.open(path).convert("RGBA")
        if strip_bg:
            im = strip_checker(im)
        if scale == "auto":
            s = detect_scale(im)
            method = "nearest"
            if s == 1:
                est = estimate_scale(im)
                if est > 1:
                    s = est
                    method = "block"   # non-integer / resampled -> block-center recovery
        else:
            s = float(scale)
            method = "block" if not s.is_integer() else "nearest"
            s = max(1, int(round(s)))
        if s > 1:
            im = (im.resize((im.width // s, im.height // s), NEAREST) if method == "nearest"
                  else block_downscale(im, s))
        sp = cls(im.width, im.height)
        sp.frames[0].cels["main"] = im
        sp.detected_scale = s
        sp.import_method = method
        if max_colors:
            sp.quantize(max_colors, dither=False)
        return sp


# --------------------------------------------------------------------------
# module helpers
# --------------------------------------------------------------------------


def _mkdirs(path):
    d = os.path.dirname(os.path.abspath(path))
    if d:
        os.makedirs(d, exist_ok=True)


def _pal_image(triples):
    """P-mode palette image, cyclically padded to 256 so no stray black entries attract pixels."""
    flat = []
    i = 0
    while len(flat) < 768:
        t = triples[i % len(triples)]
        flat.extend(t)
        i += 1
    img = Image.new("P", (1, 1))
    img.putpalette(flat[:768])
    return img


def detect_scale(im):
    """Largest integer s such that the image is exact s x s pixel blocks."""
    w, h = im.size
    g = math.gcd(w, h)
    divs = sorted({d for d in range(2, g + 1) if g % d == 0}, reverse=True)
    raw = im.tobytes()
    for s in divs:
        if w // s < 4 or h // s < 4:
            continue
        small = im.resize((w // s, h // s), NEAREST)
        if small.resize((w, h), NEAREST).tobytes() == raw:
            return s
    return 1


def estimate_scale(im):
    """Median run-length of similar colors — for sloppy/resampled upscales where
    detect_scale() gives up (returns 1). Robust to non-integer scales and AA blur."""
    p = im.load()
    out = []
    for y in range(0, im.height, 7):
        run = 1
        for x in range(1, im.width):
            a, b = p[x - 1, y], p[x, y]
            if max(abs(a[i] - b[i]) for i in range(3)) < 24:
                run += 1
            else:
                if 1 < run < 40:
                    out.append(run)
                run = 1
    out.sort()
    return out[len(out) // 2] if out else 1


def block_downscale(im, s):
    """Sample block centers at scale s (survives sloppy/resampled upscales, unlike NEAREST
    resize which produces mixels on non-integer scales)."""
    w, h = im.size
    tw, th = round(w / s), round(h / s)
    small = Image.new("RGBA", (tw, th))
    sp, px = small.load(), im.load()
    for ty in range(th):
        for tx in range(tw):
            sp[tx, ty] = px[min(w - 1, int((tx + 0.5) * s)), min(h - 1, int((ty + 0.5) * s))]
    return small


def strip_checker(im):
    """Remove a baked-in light-gray checkerboard background (common in AI-gen exports).
    Returns a new image."""
    out = im.convert("RGBA").copy()
    px = out.load()
    for y in range(out.height):
        for x in range(out.width):
            r, g, b, a = px[x, y]
            if a > 0 and abs(r - g) < 14 and abs(g - b) < 26 and r > 185 and b > 160:
                px[x, y] = (0, 0, 0, 0)
    return out


def upscale_png(src, dst, scale):
    """Integer-upscale an existing PNG (nearest neighbor)."""
    im = Image.open(src)
    im.resize((im.width * int(scale), im.height * int(scale)), NEAREST).save(dst)
    print("upscaled %s -> %s @%dx" % (src, dst, int(scale)))


__all__ = ["Sprite", "PALETTES", "ramp", "mix", "hex2rgba", "rgba2hex",
           "nearest", "detect_scale", "estimate_scale", "block_downscale",
           "strip_checker", "upscale_png", "BAYER2", "BAYER4", "BAYER8"]
