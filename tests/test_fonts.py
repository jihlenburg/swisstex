from conftest import build_doc, swisscheck, ROOT
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

def test_codeface_default_dejavu_sans_mono_swisscode_stays_condensed(tmp_path):
    # User ruling 2026-07-31: code blocks get a DECLARED code face (I4 reads
    # "one family plus declared math and code companions", mirroring the
    # existing math-font companion). \verbatim@font (which also drives
    # \verb, see latex.ltx) is restyled onto \swisscodeface -- a SECOND
    # declared companion, family-name-loaded like the math font, default
    # "DejaVu Sans Mono" (free, DejaVu project, same family as the math
    # font). \swisscode itself is UNCHANGED: inline code stays on
    # \condensed (typographic, part of the one-family grotesque), only
    # block code (verbatim/\verb) is functional monospace.
    # Markers use disjoint letters (no shared letters between the three
    # groups, and none of them collide with any other glyph the class itself
    # emits on this otherwise-empty page, e.g. the pagina digit) so filtering
    # pdfplumber's flat per-glyph char list by exact character membership
    # cannot cross-contaminate one group's font set with another's.
    fx = tmp_path / "codeface.tex"
    fx.write_text(r"""\documentclass{swisstex}
\begin{document}
\swisscode{QZQ}

\begin{verbatim}
XKX
\end{verbatim}

\verb|WJW|
\end{document}""")
    r = build_doc(fx, tmp_path)
    assert r.returncode == 0, r.log[-2000:]
    with pdfplumber.open(r.pdf) as p:
        chars = [(c["text"], c["fontname"]) for pg in p.pages for c in pg.chars]
    swisscode_fonts = {fn for ch, fn in chars if ch in "QZ"}
    verbatim_fonts = {fn for ch, fn in chars if ch in "XK"}
    verb_fonts = {fn for ch, fn in chars if ch in "WJ"}
    assert swisscode_fonts, chars
    assert verbatim_fonts, chars
    assert verb_fonts, chars
    assert all("HerosCondensed" in f or "HerosCn" in f for f in swisscode_fonts), swisscode_fonts
    assert not any("DejaVuSansMono" in f for f in swisscode_fonts), swisscode_fonts
    assert all("DejaVuSansMono" in f for f in verbatim_fonts), verbatim_fonts
    assert all("DejaVuSansMono" in f for f in verb_fonts), verb_fonts
    # A16 (Schriftinventar) must now pass: the sidecar declares codeface=...
    # and the class allows exactly that family for the verbatim/\verb glyphs.
    assert r.sidecar.get("codeface"), r.sidecar
    assert "DejaVuSansMono" in r.sidecar["codeface"].replace(" ", ""), r.sidecar
    code, out = swisscheck(r.pdf)
    assert code == 0, out
    a16 = next(z for z in out.splitlines() if z.strip().startswith("A16"))
    assert "ok" in a16, out


def test_codeface_option_override(tmp_path):
    # The Kennzahl option itself: an identity or document that sets
    # codeface= replaces \swisscodeface's default (same override channel a
    # future identity would use via \renewfontfamily\swisscodeface{...} in
    # \swissidentityfonts, see the I4-completeness comment in swisstex.cls
    # Sec. 3). TeX Gyre Heros is already installed/resolvable in this repo
    # (the class's own default sans), so it doubles as a convenient
    # non-default probe family here without any extra font install.
    fx = tmp_path / "codefaceopt.tex"
    fx.write_text(r"""\documentclass[codeface={TeX Gyre Heros}]{swisstex}
\begin{document}
\begin{verbatim}
XKX
\end{verbatim}
\end{document}""")
    r = build_doc(fx, tmp_path)
    assert r.returncode == 0, r.log[-2000:]
    with pdfplumber.open(r.pdf) as p:
        chars = [(c["text"], c["fontname"]) for pg in p.pages for c in pg.chars]
    verbatim_fonts = {fn for ch, fn in chars if ch in "XK"}
    assert verbatim_fonts, chars
    assert all("TeXGyreHeros" in f for f in verbatim_fonts), verbatim_fonts
    assert not any("DejaVuSansMono" in f for f in verbatim_fonts), verbatim_fonts
    assert "codeface" in r.sidecar
    assert "TeXGyreHeros" in r.sidecar["codeface"].replace(" ", ""), r.sidecar


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

def test_swisscodeface_shape_variants(tmp_path):
    # Assert that \swisscodeface resolves shape variants (bold, italic/oblique)
    # correctly. The test uses character markers to isolate each shape's font.
    fx = tmp_path / "codeface_variants.tex"
    fx.write_text(r"""\documentclass{swisstex}
\begin{document}
{\swisscodeface abc {\bfseries bold} {\itshape obl}}
\end{document}""")
    r = build_doc(fx, tmp_path)
    assert r.returncode == 0, r.log[-2000:]
    with pdfplumber.open(r.pdf) as p:
        fonts = {c["fontname"].split("+")[-1] for pg in p.pages for c in pg.chars}
    assert any("DejaVuSansMono-Bold" in f for f in fonts), fonts
    assert any("DejaVuSansMono-Oblique" in f for f in fonts), fonts
