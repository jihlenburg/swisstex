import sys, math
sys.path.insert(0, "fonts/tools")
from fontTools.ttLib import TTFont
import build, config, measurelib

def test_post_matches_drawn_slant(tmp_path):
    build.run(["rename", "metrics", "italic"], str(tmp_path))
    for p in tmp_path.glob("*.ttf"):
        f = TTFont(str(p))
        post = f["post"].italicAngle
        _, xh, _ = measurelib.metrics(f)
        drawn = measurelib.italic_slant(f, xh) or 0.0
        assert abs(post - drawn) < 0.7, (p.name, post, drawn)

def test_caret_slope(tmp_path):
    build.run(["rename", "metrics", "italic"], str(tmp_path))
    for p in tmp_path.glob("*Italic*.ttf"):
        f = TTFont(str(p))
        hhea = f["hhea"]
        expected_run = round(math.tan(math.radians(-f["post"].italicAngle)) * hhea.caretSlopeRise)
        assert abs(hhea.caretSlopeRun - expected_run) <= 1, p.name
