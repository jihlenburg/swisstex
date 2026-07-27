import sys
sys.path.insert(0, "fonts/tools")
from fontTools.ttLib import TTFont
import build

def test_unified_vertical_metrics(tmp_path):
    build.run(["rename", "metrics"], str(tmp_path))
    fonts = [TTFont(p) for p in sorted(tmp_path.glob("*.ttf"))]
    assert len(fonts) == 8
    ref = fonts[0]
    for f in fonts:
        assert f["OS/2"].sTypoAscender == ref["OS/2"].sTypoAscender
        assert f["OS/2"].sTypoDescender == ref["OS/2"].sTypoDescender
        assert f["OS/2"].sTypoLineGap == 0
        assert f["OS/2"].usWinAscent == ref["OS/2"].usWinAscent
        assert f["OS/2"].usWinDescent == ref["OS/2"].usWinDescent
        assert f["hhea"].ascent == ref["OS/2"].sTypoAscender
        assert f["hhea"].descent == ref["OS/2"].sTypoDescender
        assert f["hhea"].lineGap == 0
        assert f["OS/2"].fsSelection & (1 << 7)      # USE_TYPO_METRICS

def test_win_metrics_cover_all_glyphs(tmp_path):
    build.run(["rename", "metrics"], str(tmp_path))
    for p in tmp_path.glob("*.ttf"):
        f = TTFont(p)
        assert f["OS/2"].usWinAscent >= f["head"].yMax
        assert f["OS/2"].usWinDescent >= -f["head"].yMin
