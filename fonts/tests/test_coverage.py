import sys
sys.path.insert(0, "fonts/tools")
from fontTools.ttLib import TTFont
import build, config

def test_required_codepoints_present(tmp_path):
    build.run(["rename", "metrics", "italic", "coverage"], str(tmp_path))
    for p in tmp_path.glob("*.ttf"):
        cmap = TTFont(str(p)).getBestCmap()
        missing = [hex(cp) for cp in config.REQUIRED_CODEPOINTS if cp not in cmap]
        assert not missing, (p.name, missing)

def test_composed_glyphs_sane(tmp_path):
    build.run(["rename", "metrics", "italic", "coverage"], str(tmp_path))
    for p in tmp_path.glob("*.ttf"):
        f = TTFont(str(p))
        cmap = f.getBestCmap()
        glyf, hmtx = f["glyf"], f["hmtx"]
        for cp in config.REQUIRED_CODEPOINTS:
            g = glyf[cmap[cp]]
            assert hmtx[cmap[cp]][0] > 0, (p.name, hex(cp))
            assert g.numberOfContours != 0 or g.isComposite(), (p.name, hex(cp))
