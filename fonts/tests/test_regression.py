# fonts/tests/test_regression.py
"""Closing regression proof for the font program (Task 9).

Context (superseding the Task-10 interpolation premise): dist ships the
u001 sources' NATIVE condensed cuts, not an interpolated instance. The
regression contract therefore applies to ALL 8 styles unchanged: dist
outlines (stems, H-bar, advance widths) must be bit-identical to the
matching source, because no pipeline step in fonts/tools/build.py touches
glyf/hmtx data -- only name/OS2/hhea/post metadata and (conditionally)
GSUB liga, with GPOS/GDEF snapshot-restored around that call (Task 6).
"""
import sys, glob
sys.path.insert(0, "fonts/tools")
from measurelib import analyze
import config

def test_outlines_unchanged_vs_sources():
    src = {c[2]: analyze(p) for p, c in
           zip(config.SOURCE_FILES, config.STYLE_MAP.values())}
    dist_paths = glob.glob("fonts/dist/*.ttf")
    assert len(dist_paths) == 8
    for p in dist_paths:
        base = p.split("/")[-1][:-4]
        d, s = analyze(p), src[base]
        assert d["stems"] == s["stems"], base          # bit-identical stems
        assert d["hbar"] == s["hbar"], base
        assert d["adv_n"] == s["adv_n"], base

def test_appendix_a_values_hold():
    r = analyze("fonts/dist/SwissTeXGrotesk-Regular.ttf")
    assert abs(r["stem_mean"] - 94.4) < 0.5
    assert abs(r["xh"] / r["ch"] - 0.69) < 0.02
