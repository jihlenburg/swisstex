#!/usr/bin/env python3
"""Outline-quality trial per the Frutiger falsifiability test.

Measures, for each font style:
  - vertical stem widths ('l', 'I', 'n' both stems, 'H' both stems)
    at mid x-height / mid cap-height, via scanline intersection
  - 'H' crossbar thickness (vertical scanline at glyph mid-x)
  - within-style stem coefficient of variation (wobble)
  - italic: post.italicAngle vs measured 'l' stem slant
  - condensed: v-stem retention vs width compression
    (mechanical scaling => stem ratio ~= width ratio; drawn => stem ratio >> width ratio)
All lengths normalized to units/em = 1000.
"""
import sys, math
from fontTools.ttLib import TTFont
from fontTools.pens.basePen import BasePen


class PolyPen(BasePen):
    """Flattens all contours into polylines (curve sampling)."""
    SAMPLES = 64

    def __init__(self, glyphSet):
        super().__init__(glyphSet)
        self.contours = []
        self._cur = None

    def _moveTo(self, pt):
        self._cur = [pt]

    def _lineTo(self, pt):
        self._cur.append(pt)

    def _curveToOne(self, p1, p2, p3):
        p0 = self._cur[-1]
        for i in range(1, self.SAMPLES + 1):
            t = i / self.SAMPLES
            mt = 1 - t
            x = mt**3*p0[0] + 3*mt**2*t*p1[0] + 3*mt*t**2*p2[0] + t**3*p3[0]
            y = mt**3*p0[1] + 3*mt**2*t*p1[1] + 3*mt*t**2*p2[1] + t**3*p3[1]
            self._cur.append((x, y))

    def _qCurveToOne(self, p1, p2):
        p0 = self._cur[-1]
        for i in range(1, self.SAMPLES + 1):
            t = i / self.SAMPLES
            mt = 1 - t
            x = mt**2*p0[0] + 2*mt*t*p1[0] + t**2*p2[0]
            y = mt**2*p0[1] + 2*mt*t*p1[1] + t**2*p2[1]
            self._cur.append((x, y))

    def _closePath(self):
        self.contours.append(self._cur)
        self._cur = None


def crossings(contours, axis, value):
    """Sorted coordinates where polygon edges cross axis ('y'->x list, 'x'->y list)."""
    hits = []
    for c in contours:
        n = len(c)
        for i in range(n):
            x1, y1 = c[i]
            x2, y2 = c[(i + 1) % n]
            a1, a2 = (y1, y2) if axis == 'y' else (x1, x2)
            b1, b2 = (x1, x2) if axis == 'y' else (y1, y2)
            if (a1 <= value < a2) or (a2 <= value < a1):
                t = (value - a1) / (a2 - a1)
                hits.append(b1 + t * (b2 - b1))
    return sorted(hits)


def segments(contours, axis, value):
    """Filled spans (pairs of crossings)."""
    xs = crossings(contours, axis, value)
    return [(xs[i], xs[i+1]) for i in range(0, len(xs) - 1, 2)]


def glyph_contours(font, name):
    gs = font.getGlyphSet()
    if name not in gs:
        return None
    pen = PolyPen(gs)
    gs[name].draw(pen)
    return pen.contours


def metrics(font):
    upm = font['head'].unitsPerEm
    os2 = font['OS/2']
    xh = getattr(os2, 'sxHeight', 0) or 0
    ch = getattr(os2, 'sCapHeight', 0) or 0
    if not xh:  # fall back to measuring 'x'
        c = glyph_contours(font, 'x')
        xh = max(p[1] for cont in c for p in cont) if c else upm * 0.5
    if not ch:
        c = glyph_contours(font, 'H')
        ch = max(p[1] for cont in c for p in cont) if c else upm * 0.7
    return upm, xh, ch


def stem_widths(font, xh, ch):
    """Vertical stem widths in font units at mid-heights."""
    stems = {}
    for name, y in (('l', xh*0.5), ('I', ch*0.5)):
        c = glyph_contours(font, name)
        if c:
            segs = segments(c, 'y', y)
            if len(segs) == 1:
                stems[name] = [segs[0][1] - segs[0][0]]
    for name, y in (('n', xh*0.5), ('H', ch*0.5)):
        c = glyph_contours(font, name)
        if c:
            segs = segments(c, 'y', y)
            if len(segs) == 2:
                stems[name] = [s[1] - s[0] for s in segs]
    return stems


def hbar(font, ch):
    """'H' crossbar thickness via vertical scanline at mid-x."""
    c = glyph_contours(font, 'H')
    if not c:
        return None
    xs = [p[0] for cont in c for p in cont]
    mid = (min(xs) + max(xs)) / 2
    segs = segments(c, 'x', mid)
    # the crossbar is the span not touching baseline/cap
    inner = [s for s in segs if s[0] > 1 and s[1] < ch - 1]
    if len(inner) == 1:
        return inner[0][1] - inner[0][0]
    return None


def italic_slant(font, xh):
    """Measured slant of 'l' stem, degrees (negative = leans right)."""
    c = glyph_contours(font, 'l')
    if not c:
        return None
    y1, y2 = xh * 0.3, xh * 0.9
    s1, s2 = segments(c, 'y', y1), segments(c, 'y', y2)
    if len(s1) != 1 or len(s2) != 1:
        return None
    c1 = (s1[0][0] + s1[0][1]) / 2
    c2 = (s2[0][0] + s2[0][1]) / 2
    return -math.degrees(math.atan2(c2 - c1, y2 - y1))


def advance(font, name):
    return font['hmtx'][name][0] if name in font.getGlyphOrder() else None


def analyze(path):
    f = TTFont(path)
    upm, xh, ch = metrics(f)
    scale = 1000.0 / upm
    stems = stem_widths(f, xh, ch)
    flat = [w * scale for ws in stems.values() for w in ws]
    mean = sum(flat) / len(flat) if flat else 0
    # normalize x-height stems vs cap stems separately? report raw CV over all
    cv = (math.sqrt(sum((w - mean)**2 for w in flat) / len(flat)) / mean * 100) if flat else 0
    bar = hbar(f, ch)
    post_it = f['post'].italicAngle
    meas_it = italic_slant(f, xh)
    return {
        'name': f['name'].getDebugName(4) or path,
        'upm': upm,
        'xh': xh * scale, 'ch': ch * scale,
        'stems': {k: [round(w * scale, 1) for w in v] for k, v in stems.items()},
        'stem_mean': round(mean, 1), 'stem_cv': round(cv, 1),
        'hbar': round(bar * scale, 1) if bar else None,
        'post_italic': post_it, 'meas_italic': round(meas_it, 2) if meas_it is not None else None,
        'adv_n': round(advance(f, 'n') * scale, 1),
    }


if __name__ == '__main__':
    results = [analyze(p) for p in sys.argv[1:]]
    for r in results:
        print(f"\n{r['name']}  (upm {r['upm']})")
        print(f"  x-height {r['xh']:.0f}  cap {r['ch']:.0f}  adv(n) {r['adv_n']}")
        print(f"  stems {r['stems']}  mean {r['stem_mean']}  CV {r['stem_cv']}%")
        print(f"  H-bar {r['hbar']}  italic post {r['post_italic']}  measured {r['meas_italic']}")
