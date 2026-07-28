"""Interpolate a gentler-compression condensed style strictly between a
U001 Regular master and its native Condensed master (per weight/style).

Ruling context (2026-07-27 legibility gate, docs/superpowers/specs/
2026-07-27-swisstex-generalization-design.md §8/§12.2): the user judged the
native 0.71-compression condensed too narrow at gloss sizes and asked for
an interpolated ~0.8-compression condensed instead, built ONLY from U001's
own Regular/Condensed cuts (no outlines from any font outside U001's own
cuts -- license firewall, see fonts/README.md).

Step 1 of this module -- check_compatibility()/CRITICAL_GLYPHS -- is the
gate for the whole task: TrueType glyf-level linear interpolation
(new = (1-t)*reg + t*cond per point) is only valid when the two source
glyphs have the same number of contours and the same number of points per
contour (so point[i] in the Regular master and point[i] in the Condensed
master really are "the same" outline vertex, just moved). If that isn't
true, blending the raw coordinate arrays produces garbage geometry, not a
gentler condensed -- so incompatible glyphs must never be blended.

See fonts/tests/test_interpolate.py::test_masters_compatible and
.superpowers/sdd/2026-07-27-font-program/task-10-report.md for the actual
audit run against all 4 U001 upright/condensed pairs and its result.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
from fontTools.ttLib import TTFont

import config

# --- CRITICAL_GLYPHS ---------------------------------------------------
# Glyphs that MUST interpolate cleanly for the ruling to be implementable
# at all: A-Z, a-z, 0-9, ASCII punctuation, the Latin-1 letters German and
# French body text need (umlauts, ß, French accents, guillemets, OE/oe),
# and every glyph named in config.REQUIRED_CODEPOINTS (the em/en dash,
# curly quotes, ellipsis, per mille, and Euro sign the spec mandates).
# Resolved to glyph names via u001-reg's cmap (config.SOURCE_FILES[0]):
# a read-only load of the pristine Regular source, verified consistent
# (same glyph name per codepoint) across all 8 u001 sources -- see the
# audit script referenced in the task-10 report.
_CRITICAL_CODEPOINTS = (
    set(range(0x21, 0x7F))  # ASCII: digits, letters, punctuation
    | {0xA0, 0xAB, 0xBB}  # nbsp, guillemets (French quoting)
    | {
        0xC0, 0xC2, 0xC4, 0xC6, 0xC7, 0xC8, 0xC9, 0xCA, 0xCB, 0xCE, 0xCF,
        0xD4, 0xD9, 0xDB, 0xDC, 0xDF,
        0xE0, 0xE2, 0xE4, 0xE6, 0xE7, 0xE8, 0xE9, 0xEA, 0xEB, 0xEE, 0xEF,
        0xF4, 0xF9, 0xFB, 0xFC, 0xFF,
        0x152, 0x153,  # OE/oe ligature (French)
    }
    | set(config.REQUIRED_CODEPOINTS)
)


def _critical_glyph_names():
    ref = TTFont(config.SOURCE_FILES[0])  # read-only; pristine source
    cmap = ref.getBestCmap()
    names = {cmap[cp] for cp in _CRITICAL_CODEPOINTS if cp in cmap}
    names |= set(config.REQUIRED_CODEPOINTS.values())
    return frozenset(names)


CRITICAL_GLYPHS = _critical_glyph_names()


# --- Step 1: compatibility audit ---------------------------------------
def _points(font, gname):
    """Fully-decomposed (composites flattened) coordinates, contour end
    indices, and per-point flags for one glyph. TTGlyph.getCoordinates()
    already recurses through composite components and returns absolute,
    transformed points -- so this handles composite decomposition for
    free; no separate decomposing pen is needed."""
    glyf = font["glyf"]
    g = glyf[gname]
    coords, ends, flags = g.getCoordinates(glyf)
    return list(coords), list(ends), list(flags)


def check_compatibility(reg, cond):
    """Return the sorted list of glyph names (in the glyph sets common to
    both fonts) that are NOT point-compatible for linear interpolation:
    different contour count, different point count, or unreadable glyph
    data. Matches the brief's specified check exactly. Note this does not
    additionally compare per-point on/off-curve flags -- a glyph with
    matching contour/point counts but a different on/off-curve pattern
    would still blend into a garbage outline; an ad hoc probe during the
    Task 10 audit found such flag mismatches exist too (e.g. reg/cond 'm'),
    layered on top of -- never instead of -- the point-count
    incompatibilities below, so it does not change this task's BLOCKED
    verdict and isn't wired in here. See task-10-report.md."""
    bad = []
    common = set(reg.getGlyphOrder()) & set(cond.getGlyphOrder())
    for gname in sorted(common):
        try:
            rc, r_ends, _rf = _points(reg, gname)
            cc, c_ends, _cf = _points(cond, gname)
        except Exception:
            bad.append(gname)
            continue
        if r_ends != c_ends or len(rc) != len(cc):
            bad.append(gname)
    return bad
