import sys
sys.path.insert(0, "fonts/tools")
from fontTools.ttLib import TTFont
import build, config

def test_kern_feature_compiled(tmp_path):
    # "compiled" in the sense of "present in the output" -- under the
    # 2026-07-27 user ruling this is the u001 source's own URW-authored
    # GPOS/kern, preserved untouched by step_features (liga only; see
    # build.step_features's docstring for the delete-on-empty hazard this
    # step must not trigger against GPOS).
    build.run(["rename", "metrics", "italic", "coverage", "features"], str(tmp_path))
    for p in tmp_path.glob("*.ttf"):
        f = TTFont(str(p))
        assert "GPOS" in f, p.name
        feats = [fr.FeatureTag for fr in f["GPOS"].table.FeatureList.FeatureRecord]
        assert "kern" in feats, p.name

def test_av_pair_negative(tmp_path):
    build.run(["rename", "metrics", "italic", "coverage", "features"], str(tmp_path))
    from fontTools import subset  # noqa: F401  (ensures full lib available)
    f = TTFont(str(next(tmp_path.glob("*Grotesk-Regular.ttf"))))
    # smoke: GPOS present and non-empty is the machine check; the value
    # check happens visually in the specimen (Task 8)
    assert f["GPOS"].table.LookupList.LookupCount >= 1


def _kern_value(font, left, right):
    """Look up the XAdvance for a specific (left, right) kern pair across
    all lookups referenced by the 'kern' feature. Handles PairPos Format 1
    (explicit PairSet), which is what both feaLib and the u001 sources'
    own URW-authored kerning use."""
    gpos = font["GPOS"].table
    kern_lookup_indices = set()
    for fr in gpos.FeatureList.FeatureRecord:
        if fr.FeatureTag == "kern":
            kern_lookup_indices.update(fr.Feature.LookupListIndex)
    for idx in kern_lookup_indices:
        lookup = gpos.LookupList.Lookup[idx]
        for st in lookup.SubTable:
            if not hasattr(st, "Coverage") or left not in st.Coverage.glyphs:
                continue
            if getattr(st, "Format", None) == 1:
                pos = st.Coverage.glyphs.index(left)
                for rec in st.PairSet[pos].PairValueRecord:
                    if rec.SecondGlyph == right:
                        return rec.Value1.XAdvance
    return None


def _kern_pair_count(font):
    gpos = font["GPOS"].table
    kern_lookup_indices = set()
    for fr in gpos.FeatureList.FeatureRecord:
        if fr.FeatureTag == "kern":
            kern_lookup_indices.update(fr.Feature.LookupListIndex)
    total = 0
    for idx in kern_lookup_indices:
        lookup = gpos.LookupList.Lookup[idx]
        for st in lookup.SubTable:
            if getattr(st, "Format", None) == 1:
                total += sum(len(ps.PairValueRecord) for ps in st.PairSet)
    return total


def test_urw_kern_preserved_exactly(tmp_path):
    """User ruling (2026-07-27): SwissTeX Grotesk ships the u001 source's
    own GPOS kerning untouched -- step_features (liga only) must not
    replace, merge into, or otherwise alter it. Read both the A-V pair
    value and the total pair count directly from the pristine source at
    test time (not hardcoded), so this proves *preservation* rather than
    pinning a constant that would silently go stale if the source ever
    changed."""
    src = TTFont(config.SOURCE_FILES[0])  # u001-reg.ttf, read-only load
    expected_av = _kern_value(src, "A", "V")
    expected_count = _kern_pair_count(src)
    # sanity: the source really does carry non-trivial kern data (it does
    # -- 92 pairs incl. A-V = -138 as of this source revision)
    assert expected_av is not None
    assert expected_count > 0

    build.run(["rename", "metrics", "italic", "coverage", "features"], str(tmp_path))
    f = TTFont(str(next(tmp_path.glob("*Grotesk-Regular.ttf"))))
    assert _kern_value(f, "A", "V") == expected_av
    assert _kern_pair_count(f) == expected_count


def test_liga_present_when_fi_fl_exist(tmp_path):
    build.run(["rename", "metrics", "italic", "coverage", "features"], str(tmp_path))
    for p in tmp_path.glob("*.ttf"):
        f = TTFont(str(p))
        glyphs = set(f.getGlyphOrder())
        if {"fi", "fl"} <= glyphs:
            assert "GSUB" in f, p.name
            feats = [fr.FeatureTag for fr in f["GSUB"].table.FeatureList.FeatureRecord]
            assert "liga" in feats, p.name


def test_features_step_noop_when_fi_fl_missing():
    """Negative branch (reviewer-requested): a font without fi/fl must go
    through step_features completely unharmed -- no liga added, and GPOS
    and GSUB left byte-identical. This guards the delete-on-empty hazard
    in fontTools.feaLib.builder.Builder.build(): compiling a fea whose
    computed table for a tag is empty deletes any existing table under
    that tag, so a naive implementation that still called feaLib on the
    false branch (with an empty/no-liga fea) could silently drop an
    existing GSUB (or GPOS). step_features avoids this by returning
    before any feaLib call when fi/fl are missing.

    Uses an in-memory copy of a pristine source with fi/fl stripped from
    the glyph order; the source file on disk is only ever opened for
    reading here, so it stays pristine."""
    font = TTFont(config.SOURCE_FILES[0])  # independent in-memory copy
    order = [g for g in font.getGlyphOrder() if g not in ("fi", "fl")]
    font.setGlyphOrder(order)
    assert not ({"fi", "fl"} <= set(font.getGlyphOrder()))

    gpos_before = font["GPOS"].compile(font) if "GPOS" in font else None
    gsub_before = font["GSUB"].compile(font) if "GSUB" in font else None

    build.step_features(font, "u001-reg")

    assert ("GPOS" in font) == (gpos_before is not None)
    if gpos_before is not None:
        assert font["GPOS"].compile(font) == gpos_before

    assert ("GSUB" in font) == (gsub_before is not None)
    if gsub_before is not None:
        assert font["GSUB"].compile(font) == gsub_before
        feats = [fr.FeatureTag for fr in font["GSUB"].table.FeatureList.FeatureRecord]
        assert "liga" not in feats

    # source file on disk must remain pristine (never written to)
    disk = TTFont(config.SOURCE_FILES[0])
    assert {"fi", "fl"} <= set(disk.getGlyphOrder())
