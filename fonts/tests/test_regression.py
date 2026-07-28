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
import os, sys, glob
sys.path.insert(0, "fonts/tools")
from fontTools.ttLib import TTFont
from measurelib import analyze
import config

def test_outlines_unchanged_vs_sources():
    # key source measurements by OUTPUT basename via config.STYLE_MAP,
    # looked up explicitly per source path -- not a positional zip(), which
    # would silently mismatch source and dist if either list's order ever
    # changed independently of the other.
    src = {}
    for path in config.SOURCE_FILES:
        filename = os.path.splitext(os.path.basename(path))[0]
        _, _, out = config.STYLE_MAP[filename]
        src[out] = analyze(path)
    dist_paths = glob.glob("fonts/dist/*.ttf")
    assert len(dist_paths) == 8
    for p in dist_paths:
        base = os.path.splitext(os.path.basename(p))[0]
        d, s = analyze(p), src[base]
        assert d["stems"] == s["stems"], base          # bit-identical stems
        assert d["hbar"] == s["hbar"], base
        assert d["adv_n"] == s["adv_n"], base

def test_appendix_a_values_hold():
    r = analyze("fonts/dist/SwissTeXGrotesk-Regular.ttf")
    assert abs(r["stem_mean"] - 94.4) < 0.5
    assert abs(r["xh"] / r["ch"] - 0.69) < 0.02

def test_built_regular_typo_ascender_traces_to_source():
    """Regular-traceability: the built Regular's OS/2.sTypoAscender is not
    just internally consistent across the 8 dist styles (test_metrics.py)
    but is actually the SOURCE Regular's own value -- config.metrics_targets()
    is documented to derive typo_asc from SOURCE_FILES[0] (u001-reg), and
    this pins that claim against the real files rather than trusting the
    docstring."""
    filename = next(fn for fn, (fam, sub, out) in config.STYLE_MAP.items()
                     if out == "SwissTeXGrotesk-Regular")
    src = TTFont(os.path.join(config.SRC, f"{filename}.ttf"))
    dist = TTFont("fonts/dist/SwissTeXGrotesk-Regular.ttf")
    assert dist["OS/2"].sTypoAscender == src["OS/2"].sTypoAscender
