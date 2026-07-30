from conftest import build_doc, ROOT
import pdfplumber

def _text(pdf):
    # x_tolerance=2: the caption prefix and number are joined with a non-
    # breaking space (\tablecaptionprefix~\theswisstable in swisstable), which
    # renders as a genuine ~2.07pt glyph gap (verified char-by-char: 0pt
    # between ordinary letters, ~2.07pt between the prefix and the digit) but
    # pdfplumber's default x_tolerance=3 does not treat that as a word break,
    # merging e.g. "Table" and "1" into "Table1". x_tolerance=2 matches the
    # real rendered gap without affecting ordinary (0pt-kerned) intra-word
    # joins.
    with pdfplumber.open(pdf) as p:
        return "\n".join(pg.extract_text(x_tolerance=2) or "" for pg in p.pages)

def test_english_captions(tmp_path):
    r = build_doc(ROOT / "tests/fixtures/lang-en.tex", tmp_path)
    assert r.returncode == 0, r.log[-2000:]
    t = _text(r.pdf)
    assert "Table 1" in t and "Tabelle" not in t

def test_custom_language_addable(tmp_path):
    fx = tmp_path / "fr.tex"
    fx.write_text(r"""\documentclass[lang=french]{swisstex}
\swisssetstrings{french}{table=Tableau, figure=Illustration, page=Page,
  classification-public=public, classification-internal=interne,
  classification-confidential=confidentiel, classification-strict=strict}
\begin{document}
\begin{swisstable}{Legende}\begin{tabularx}{\textcolumn}[t]{@{}L@{}}x\\\end{tabularx}\end{swisstable}
\end{document}""")
    r = build_doc(fx, tmp_path)
    assert r.returncode == 0, r.log[-2000:]
    assert "Tableau 1" in _text(r.pdf)

def test_unknown_language_falls_back(tmp_path):
    # NOTE (rough edge #4 in task-2-brief.md): verified empirically that
    # \setdefaultlanguage{latin} does NOT make polyglossia error in this TeX
    # Live install (latin ships hyphenation patterns and a gloss-latin.ldf,
    # build exits 0) -- so the brief's original premise holds and `latin` is
    # a valid choice: polyglossia accepts the language, but our DE/EN string
    # table has no "latin" entries, so \swiss@str falls back to english with
    # a warning. Kept as in the brief rather than switching to `dutch`.
    fx = tmp_path / "xx.tex"
    fx.write_text(r"""\documentclass[lang=latin]{swisstex}
\begin{document}
\begin{swisstable}{L}\begin{tabularx}{\textcolumn}[t]{@{}L@{}}x\\\end{tabularx}\end{swisstable}
\end{document}""")
    r = build_doc(fx, tmp_path)
    assert r.returncode == 0, r.log[-2000:]
    assert "Table 1" in _text(r.pdf)          # EN fallback
    assert "swisstex Warning" in r.log or "fallback" in r.log.lower()
