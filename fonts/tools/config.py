import os

# config.py lives at fonts/tools/config.py -- the repo root is two levels up.
# Anchoring every path here means build.py and the tests work from any CWD,
# not just when invoked from the repo root.
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SRC = os.path.join(ROOT, "fonts", "sources", "u001")
DIST = os.path.join(ROOT, "fonts", "dist")
BUILD = os.path.join(ROOT, "fonts", "build")
SOURCE_FILES = [os.path.join(SRC, f"{n}.ttf") for n in
    ["u001-reg", "u001-ita", "u001-bol", "u001-bolita",
     "u001con-reg", "u001con-ita", "u001con-bol", "u001con-bolita"]]

FAM, FAMC = "SwissTeX Grotesk", "SwissTeX Grotesk Condensed"
# filename -> (family, subfamily, output basename)
STYLE_MAP = {
    "u001-reg":       (FAM,  "Regular",     "SwissTeXGrotesk-Regular"),
    "u001-ita":       (FAM,  "Italic",      "SwissTeXGrotesk-Italic"),
    "u001-bol":       (FAM,  "Bold",        "SwissTeXGrotesk-Bold"),
    "u001-bolita":    (FAM,  "Bold Italic", "SwissTeXGrotesk-BoldItalic"),
    "u001con-reg":    (FAMC, "Regular",     "SwissTeXGroteskCond-Regular"),
    "u001con-ita":    (FAMC, "Italic",      "SwissTeXGroteskCond-Italic"),
    "u001con-bol":    (FAMC, "Bold",        "SwissTeXGroteskCond-Bold"),
    "u001con-bolita": (FAMC, "Bold Italic", "SwissTeXGroteskCond-BoldItalic"),
}
LICENSE_NOTE = ("Modified from URW U001 on 2026-07-28; renamed to distinguish "
                "it from the original. Distributed under the Aladdin Free "
                "Public License; see Copying.AFPL.txt.")
LICENSE_URL = "https://fontlibrary.org/en/font/u001"
VERSION_NUM = 2.0
VERSION = f"Version {VERSION_NUM:.3f}"

ITALIC_ANGLE = -17.0
ITALIC_FILES = {"u001-ita", "u001-bolita", "u001con-ita", "u001con-bolita"}

REQUIRED_CODEPOINTS = {
    0x2013: "endash", 0x2014: "emdash", 0x20AC: "Euro",
    0x201E: "quotedblbase", 0x201C: "quotedblleft", 0x201D: "quotedblright",
    0x201A: "quotesinglbase", 0x2018: "quoteleft", 0x2019: "quoteright",
    0x2026: "ellipsis", 0x2030: "perthousand",
}

# kern-reference.fea's pair values are authored in font design units at
# this unitsPerEm (all 8 u001 sources share unitsPerEm == KERN_UNIT,
# verified in Task 6). Not currently load-bearing: kern-reference.fea is
# reference-only and is not compiled (user ruling 2026-07-27 -- SwissTeX
# Grotesk ships the sources' own URW GPOS kerning). Kept for the day a
# curated kern feature is reinstated.
KERN_UNIT = 2048

_metrics_cache = None
def metrics_targets():
    """typo = Regular's source values (canonical rhythm); win = union of
    extremes across all 8 (clipping guard). Computed once from sources."""
    global _metrics_cache
    if _metrics_cache is None:
        from fontTools.ttLib import TTFont
        fonts = [TTFont(p) for p in SOURCE_FILES]
        reg = fonts[0]
        _metrics_cache = dict(
            typo_asc=reg["OS/2"].sTypoAscender,
            typo_desc=reg["OS/2"].sTypoDescender,
            line_gap=0,
            win_asc=max(f["head"].yMax for f in fonts),
            win_desc=max(-f["head"].yMin for f in fonts),
            underline_thickness=reg["post"].underlineThickness,
        )
    return _metrics_cache
