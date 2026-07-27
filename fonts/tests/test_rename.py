import sys
sys.path.insert(0, "fonts/tools")
from fontTools.ttLib import TTFont
import build, config

def _built(tmp_path):
    build.run(["rename"], str(tmp_path))
    return {p.name: TTFont(p) for p in tmp_path.glob("*.ttf")}

def test_names(tmp_path):
    fonts = _built(tmp_path)
    assert len(fonts) == 8
    f = fonts["SwissTeXGrotesk-Regular.ttf"]
    n = f["name"]
    assert n.getDebugName(1) == "SwissTeX Grotesk"
    assert n.getDebugName(2) == "Regular"
    assert n.getDebugName(4) == "SwissTeX Grotesk Regular"
    assert n.getDebugName(6) == "SwissTeXGrotesk-Regular"
    c = fonts["SwissTeXGroteskCond-BoldItalic.ttf"]
    assert c["name"].getDebugName(1) == "SwissTeX Grotesk Condensed"
    assert c["name"].getDebugName(2) == "Bold Italic"

def test_no_u001_string_remains(tmp_path):
    for name, f in _built(tmp_path).items():
        for rec in f["name"].names:
            if rec.nameID in (1, 2, 3, 4, 6, 16, 17):
                assert "U001" not in rec.toUnicode(), (name, rec.nameID)

def test_afpl_notice(tmp_path):
    for name, f in _built(tmp_path).items():
        lic = f["name"].getDebugName(13) or ""
        assert "Aladdin" in lic, name
