import sys
sys.path.insert(0, "fonts/tools")
from fontTools.ttLib import TTFont
import build

def test_kern_feature_compiled(tmp_path):
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
    (explicit PairSet) which is what feaLib emits for the individual
    `pos A B -n;` statements in kern.fea."""
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


def test_av_pair_is_hand_curated_value_not_inherited(tmp_path):
    """kern.fea specifies A V -70 (2048upm). The u001 sources ship their
    own GPOS/kern (URW-authored, A-V = -138) which step_features must
    fully replace -- not merge with -- per the license-firewall
    constraint (no kerning data from any other font). This is the
    concrete RED->GREEN check: -138 (inherited, pre-step) vs -70
    (hand-curated, post-step)."""
    build.run(["rename", "metrics", "italic", "coverage", "features"], str(tmp_path))
    f = TTFont(str(next(tmp_path.glob("*Grotesk-Regular.ttf"))))
    assert _kern_value(f, "A", "V") == -70


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


def test_kern_pair_count_matches_curated_fea_exactly(tmp_path):
    """License firewall: kern.fea defines exactly 38 pairs. The u001
    sources ship their own 92-pair GPOS/kern (URW-authored, not part of
    the brief). If step_features ever started merging instead of
    replacing, this count would exceed 38 and this test would catch it."""
    build.run(["rename", "metrics", "italic", "coverage", "features"], str(tmp_path))
    for p in tmp_path.glob("*.ttf"):
        f = TTFont(str(p))
        assert _kern_pair_count(f) == 38, p.name


def test_liga_present_when_fi_fl_exist(tmp_path):
    build.run(["rename", "metrics", "italic", "coverage", "features"], str(tmp_path))
    for p in tmp_path.glob("*.ttf"):
        f = TTFont(str(p))
        glyphs = set(f.getGlyphOrder())
        if {"fi", "fl"} <= glyphs:
            assert "GSUB" in f, p.name
            feats = [fr.FeatureTag for fr in f["GSUB"].table.FeatureList.FeatureRecord]
            assert "liga" in feats, p.name
