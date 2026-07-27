import os, sys, math
sys.path.insert(0, os.path.dirname(__file__))
from fontTools.ttLib import TTFont
import config

def load(path):
    return TTFont(path)

def _set(name_table, nid, value):
    # Windows Unicode + Mac Roman, the two platforms real installers read
    name_table.setName(value, nid, 3, 1, 0x409)
    name_table.setName(value, nid, 1, 0, 0)

def step_rename(font, filename):
    fam, sub, out = config.STYLE_MAP[filename]
    n = font["name"]
    _set(n, 1, fam)
    _set(n, 2, sub)
    _set(n, 3, f"{config.VERSION};{out}")
    _set(n, 4, f"{fam} {sub}")
    _set(n, 5, config.VERSION)
    _set(n, 6, out)
    _set(n, 13, config.LICENSE_NOTE)
    # drop stale typographic-family overrides from the sources
    n.removeNames(nameID=16)
    n.removeNames(nameID=17)

def step_metrics(font, filename):
    t = config.metrics_targets()
    os2, hhea = font["OS/2"], font["hhea"]
    os2.sTypoAscender = t["typo_asc"]
    os2.sTypoDescender = t["typo_desc"]
    os2.sTypoLineGap = t["line_gap"]
    os2.usWinAscent = t["win_asc"]
    os2.usWinDescent = t["win_desc"]
    os2.fsSelection |= (1 << 7)          # USE_TYPO_METRICS
    hhea.ascent = t["typo_asc"]
    hhea.descent = t["typo_desc"]
    hhea.lineGap = t["line_gap"]

def step_italic(font, filename):
    if filename not in config.ITALIC_FILES:
        return
    font["post"].italicAngle = config.ITALIC_ANGLE
    hhea = font["hhea"]
    hhea.caretSlopeRise = 1000
    hhea.caretSlopeRun = round(math.tan(math.radians(-config.ITALIC_ANGLE)) * 1000)

def step_coverage(font, filename):
    """Verify config.REQUIRED_CODEPOINTS are covered; compose any genuine
    gap from the font's own parts via RECIPES (rule-based composites, no
    external outlines). Audit of the 8 u001 sources (2026-07-27) found
    every Unicode cmap subtable -- (0,3) and (3,1), format 4 -- already
    carries all 11 required codepoints, euro included; the (1,0) Mac Roman
    subtable "misses" them only because that single-byte encoding cannot
    represent them at all, which getBestCmap() correctly ignores. So
    RECIPES is empty for now: nothing to compose. The mechanism stays in
    place (recipe lookup + hard ValueError on an uncomposable gap) so a
    future source update that actually drops a glyph fails loudly instead
    of silently shipping a hole.
    """
    cmap_table = font["cmap"]
    cmap = font.getBestCmap()
    for cp, gname in config.REQUIRED_CODEPOINTS.items():
        if cp in cmap:
            continue
        if cp not in RECIPES:
            raise ValueError(f"{filename}: missing {hex(cp)} and no recipe")
        glyph, width = RECIPES[cp](font)
        font["glyf"][gname] = glyph
        font["hmtx"][gname] = (width, 60)
        order = font.getGlyphOrder()
        if gname not in order:
            font.setGlyphOrder(order + [gname])
        for table in cmap_table.tables:
            if table.isUnicode():
                table.cmap[cp] = gname

RECIPES = {}

STEPS = {"rename": step_rename, "metrics": step_metrics, "italic": step_italic,
         "coverage": step_coverage}
ORDER = ["rename", "metrics", "italic", "coverage"]   # later tasks append: features

def run(steps, out_dir):
    os.makedirs(out_dir, exist_ok=True)
    for path in config.SOURCE_FILES:
        filename = os.path.splitext(os.path.basename(path))[0]
        font = load(path)
        for s in [s for s in ORDER if s in steps]:
            STEPS[s](font, filename)
        _, _, out = config.STYLE_MAP[filename]
        font.save(os.path.join(out_dir, f"{out}.ttf"))

if __name__ == "__main__":
    run(sys.argv[1:] or ORDER, "fonts/build")
