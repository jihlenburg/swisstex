import os, sys, math
sys.path.insert(0, os.path.dirname(__file__))
from fontTools.ttLib import TTFont
from fontTools.feaLib.builder import addOpenTypeFeaturesFromString
from fontTools.otlLib.maxContextCalc import maxCtxFont
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
    _set(n, 14, config.LICENSE_URL)          # license info URL
    # drop stale typographic-family overrides from the sources
    n.removeNames(nameID=16)
    n.removeNames(nameID=17)
    # fontbakery opentype/font_version (Task 9): head.fontRevision must
    # match the nameID 5 version string above, or applications report
    # inconsistent version numbers. Sources ship an unrelated fontRevision
    # (~1.04999); align it to the single VERSION_NUM source of truth.
    font["head"].fontRevision = config.VERSION_NUM

# name IDs stamped by the webfont-generator pipeline the u001 sources were
# distributed through (Font Squirrel / ttfautohint), not by URW: they carry
# no license-relevant content and are noise in the shipped fonts.
WEBFONT_STAMP_NAME_IDS = (200, 201, 202, 203, 55555)
MODIFICATION_NOTICE = "; modified 2026-07-28 by the SwissTeX project."

def step_identity(font, filename):
    """Frutiger closing-review fixes (identity/provenance layer):
      - vendor ID SWTX (was URW's own, wrong once the font is modified)
      - fsType 0 (installable embedding -- coherent with the AFPL's
        redistribution freedoms; the sources shipped fsType 4)
      - name ID 0 rewritten to URW's original copyright text (read from the
        matching source font on disk, not hardcoded) plus a dated
        modification notice -- the AFPL requires retaining the original
        notice AND dating changes (Copying.AFPL.txt 2(c)(i))
      - the Font-Squirrel/ttfautohint webfont-generator stamps (name IDs
        200/201/202/203/55555, the 'webf' and 'FFTM' tables) removed: they
        describe a webfont-packaging step this pipeline does not perform
      - condensed styles only: usWidthClass 3 and PANOSE bProportion 6, so
        the metadata actually says "condensed" instead of "normal"
    """
    fam, sub, out = config.STYLE_MAP[filename]
    os2 = font["OS/2"]
    os2.achVendID = "SWTX"
    os2.fsType = 0

    src_path = os.path.join(config.SRC, f"{filename}.ttf")
    original_copyright = TTFont(src_path)["name"].getDebugName(0) or ""
    n = font["name"]
    _set(n, 0, original_copyright + MODIFICATION_NOTICE)

    for nid in WEBFONT_STAMP_NAME_IDS:
        n.removeNames(nameID=nid)
    for tag in ("webf", "FFTM"):
        if tag in font:
            del font[tag]

    if fam == config.FAMC:                    # the 4 condensed styles only
        os2.usWidthClass = 3
        os2.panose.bProportion = 6

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
    # fontbakery ttx_roundtrip (Task 9): fsSelection bits 7-9 (incl. the
    # USE_TYPO_METRICS bit set above) are only defined from OS/2 table
    # version 4 onward; the u001 sources ship version 1, so setting that
    # bit against a v1 table is a real spec-compliance gap this step
    # introduces. Bump to version 4 and populate the fields that version
    # requires beyond v1 (ulCodePageRange1/2 already present in v1).
    # sCapHeight/sxHeight are read straight from the untouched glyf bbox
    # of 'H'/'x' -- verified byte-identical, for all 8 sources, to
    # measurelib's own curve-sampled fallback (used whenever these OS/2
    # fields are absent/zero), so introducing them cannot perturb the
    # regression test's stem measurements. usDefaultChar/usBreakChar
    # follow the fontTools fontBuilder convention (0 / space). usMaxContext
    # is computed from this font's GSUB/GPOS as they stand right now; if
    # step_features later adds liga to this same font object, it
    # recomputes usMaxContext itself once GSUB reaches its final state.
    os2.version = 4
    os2.sCapHeight = font["glyf"]["H"].yMax
    os2.sxHeight = font["glyf"]["x"].yMax
    os2.usDefaultChar = 0
    os2.usBreakChar = 32
    os2.usMaxContext = maxCtxFont(font)
    # fontbakery opentype/xavgcharwidth (Task 9, self-inflicted by the
    # version bump above): OS/2 xAvgCharWidth's expected formula changes
    # at version 3 from a weighted lowercase-latin average to a plain mean
    # over every positive-width glyph in hmtx. The sources' inherited
    # xAvgCharWidth (958, sized for the old formula) doesn't satisfy the
    # new one once version >= 3, so recompute it the way version>=3 fonts
    # are expected to.
    widths = [w for w, _ in font["hmtx"].metrics.values() if w > 0]
    os2.xAvgCharWidth = round(sum(widths) / len(widths))
    # fontbakery opentype/family/underline_thickness (Task 9): sources
    # vary post.underlineThickness 104/105 by style; unify on Regular's
    # canonical value (post.underlinePosition is already uniform at -460
    # across all 8 sources, so it's left untouched).
    font["post"].underlineThickness = t["underline_thickness"]

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

def step_features(font, filename):
    """liga only. User ruling (2026-07-27): SwissTeX Grotesk ships the u001
    sources' own URW-authored GPOS kerning as-is, not the curated
    kern-reference.fea (retired to documentation; see that file's header).
    liga (fi/fl) is added only when both ligature glyphs exist in this
    font's glyph order; when they don't, this is a true no-op -- return
    before calling feaLib at all.

    Hazard (delete-on-empty): fontTools.feaLib.builder.Builder.build()
    computes a fresh GPOS and a fresh GSUB from the fea source and, for
    each tag, either installs the computed table or -- if the computed
    table is empty (ScriptCount == FeatureCount == LookupCount == 0) AND
    the font already has a table under that tag -- deletes it outright
    (see fontTools/feaLib/builder.py:217-231). GDEF gets the identical
    treatment a few lines later (builder.py:233-238): buildGDEF() returns
    falsy when the fea defines no glyph classes/anchors/ligature carets,
    and if the font already has a GDEF, it's deleted. A liga-only fea has
    no GPOS statements and defines no GDEF-relevant data, so both its
    computed GPOS and its computed GDEF are empty; compiling it against a
    font that already has GPOS and/or GDEF (every u001 source has both)
    would silently delete them as an unwanted side effect. Confirmed
    empirically (isolated repro): compiling the liga-only fea against
    u001-reg.ttf with no guard leaves both 'GPOS' in font and
    'GDEF' in font False afterward. Guarded two ways:
      - fi/fl missing: return before any feaLib call -- nothing (GPOS,
        GDEF, or GSUB) can be touched, so the empty-GSUB variant of the
        same hazard can't trigger either.
      - fi/fl present: snapshot font["GPOS"] and font["GDEF"] before the
        call and restore both after. GSUB is exactly what should be
        (re)built here (non-empty, contains liga), so it's left alone.
    """
    glyphs = set(font.getGlyphOrder())
    if not ({"fi", "fl"} <= glyphs):
        return
    # the source GSUB carries DFLT+latn script coverage; without declaring
    # the same languagesystems here, feaLib would build a GSUB scoped to
    # DFLT only, narrowing script coverage relative to the source (a
    # regression the fontbakery/regression suite must catch).
    fea = ("languagesystem DFLT dflt;\n"
           "languagesystem latn dflt;\n"
           "feature liga { sub f i by fi; sub f l by fl; } liga;\n")
    gpos = font.get("GPOS")
    gdef = font.get("GDEF")
    addOpenTypeFeaturesFromString(font, fea)
    if gpos is not None:
        font["GPOS"] = gpos
    if gdef is not None:
        font["GDEF"] = gdef
    # fontbakery ttx_roundtrip / OS-2 usMaxContext (Task 9): step_metrics
    # already sets usMaxContext from GSUB/GPOS as they stood before this
    # step ran; recompute now that GSUB may carry the new liga lookup, so
    # the field reflects the font's final OpenType Layout content. Guarded
    # on OS/2 version >=2 (the field doesn't exist below that) so this is
    # a true no-op when step_metrics hasn't run in this build (e.g. a test
    # that calls step_features directly against a raw v1 source).
    os2 = font.get("OS/2")
    if os2 is not None and os2.version >= 2:
        os2.usMaxContext = maxCtxFont(font)

STEPS = {"rename": step_rename, "identity": step_identity, "metrics": step_metrics,
         "italic": step_italic, "coverage": step_coverage, "features": step_features}
ORDER = ["rename", "identity", "metrics", "italic", "coverage", "features"]

def run(steps, out_dir):
    unknown = [s for s in steps if s not in STEPS]
    if unknown:
        raise ValueError(f"unknown step(s): {', '.join(unknown)}")
    os.makedirs(out_dir, exist_ok=True)
    for path in config.SOURCE_FILES:
        filename = os.path.splitext(os.path.basename(path))[0]
        font = load(path)
        for s in [s for s in ORDER if s in steps]:
            STEPS[s](font, filename)
        _, _, out = config.STYLE_MAP[filename]
        font.save(os.path.join(out_dir, f"{out}.ttf"))

def install():
    """Copy the 8 dist TTFs plus the AFPL license text to ~/Library/Fonts,
    the macOS font directory XeTeX/CoreText resolves family names from
    (see fonts/README.md). Verifies exactly 8 TTFs were found/copied."""
    import shutil, glob as _glob
    dest = os.path.expanduser("~/Library/Fonts")
    os.makedirs(dest, exist_ok=True)
    ttfs = sorted(_glob.glob(os.path.join(config.DIST, "*.ttf")))
    if len(ttfs) != 8:
        raise ValueError(f"expected 8 TTFs in {config.DIST}, found {len(ttfs)}")
    for p in ttfs + [os.path.join(config.DIST, "Copying.AFPL.txt")]:
        shutil.copy(p, dest)
        print("copied", p, "->", dest)
    print("installed", len(ttfs), "TTFs to", dest)

if __name__ == "__main__":
    args = sys.argv[1:]
    if args[:1] == ["install"]:
        install()
    elif not args or args == ["all"]:
        run(ORDER, config.DIST)
    else:
        run(args, config.BUILD)
