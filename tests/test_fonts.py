from conftest import build_doc, ROOT
import pdfplumber

def _fonts(pdf):
    with pdfplumber.open(pdf) as p:
        return {c["fontname"].split("+")[-1] for pg in p.pages for c in pg.chars}

def test_provider_override(tmp_path):
    r = build_doc(ROOT / "tests/fixtures/provider.tex", tmp_path)
    assert r.returncode == 0, r.log[-2000:]
    f = _fonts(r.pdf)
    assert any("SwissTeXGrotesk" in x for x in f), f
    assert not any("TeXGyreHeros" in x for x in f), f

def test_swisscode_no_latin_modern(tmp_path):
    fx = tmp_path / "code.tex"
    fx.write_text(r"""\documentclass{swisstex}
\begin{document}Vorher \swisscode{gridunit=13.5pt} nachher.\end{document}""")
    r = build_doc(fx, tmp_path)
    assert r.returncode == 0, r.log[-2000:]
    assert not any("LMMono" in x or "LMRoman" in x for x in _fonts(r.pdf))
