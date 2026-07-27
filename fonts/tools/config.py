SRC = "fonts/sources/u001"
SOURCE_FILES = [f"{SRC}/{n}.ttf" for n in
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
LICENSE_NOTE = ("Modified version of URW U001, renamed per the Aladdin Free "
                "Public License (AFPL). See Copying.AFPL.txt. Not for "
                "commercial distribution as a font.")
VERSION = "Version 2.000"

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
        )
    return _metrics_cache
