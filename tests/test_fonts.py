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

def test_math_partial_glyph(tmp_path):
    # Regression test: U+1D715 (MATHEMATICAL ITALIC PARTIAL DIFFERENTIAL,
    # what \partial produces under unicode-math) was rendering as a missing
    # glyph -- \setmathfont[range=\mathit]{...} (and range=\mathup) claim
    # unicode-math's full default alphabet, which includes the "misc"
    # subset (\partial, \nabla, ...) alongside plain letters. That maps
    # U+1D715 onto the sans italic font (no math glyph there) instead of
    # leaving it on the main math font. Fix narrows the range to
    # {latin,Latin,greek,Greek,num} (mathup) / {latin,Latin,greek,Greek}
    # (mathit) so symbol slots stay with the math font while letters and
    # digits still carry the sans family (I4).
    fx = tmp_path / "mathpartial.tex"
    fx.write_text(r"""\documentclass{swisstex}
\begin{document}
\tracinglostchars=2
$\partial f = ax^2 + \beta y$
\end{document}""")
    r = build_doc(fx, tmp_path)
    assert r.returncode == 0, r.log[-2000:]
    assert "Missing character" not in r.log, r.log[-2000:]
    with pdfplumber.open(r.pdf) as p:
        chars = {c["text"]: c["fontname"] for pg in p.pages for c in pg.chars}
    # (a) the glyph extracts as U+1D715 and is backed by a real (math) font,
    # not a sans font lacking the glyph.
    assert "\U0001d715" in chars, chars
    assert "TeXGyreHeros" not in chars["\U0001d715"], chars
    # (b) letters in the formula still carry the sans family (I4).
    for letter in ("f", "a", "x", "y"):
        assert "TeXGyreHeros" in chars[letter], (letter, chars)
