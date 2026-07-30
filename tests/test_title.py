import pdfplumber
from conftest import build_doc, swisscheck, ROOT

def _inject_logo(tmp_path, logo_pdf, name="title.tex"):
    src = (ROOT / "tests/fixtures" / name).read_text()
    src = src.replace("LOGOPATH", str(logo_pdf))
    fx = tmp_path / name
    fx.write_text(src)
    return fx

def _fill_rects(pdf_path):
    # \rule (mklogo.tex's logo content) draws a filled rectangle.
    with pdfplumber.open(pdf_path) as p:
        return [r for r in p.pages[0].rects if r["fill"]]

def _rule_lines(pdf_path):
    # \hrule (the title block's closing 1.2pt rule) draws a STROKED line,
    # not a filled rect -- unlike \rule/\colorbox, which fill.
    with pdfplumber.open(pdf_path) as p:
        return [l for l in p.pages[0].lines if l["stroke"]]

# --- Step 1 tests from the brief -------------------------------------------

def test_star_title_and_logo(tmp_path, logo_pdf):
    fx = _inject_logo(tmp_path, logo_pdf)
    r = build_doc(fx, tmp_path)
    assert r.returncode == 0, r.log[-2000:]
    with pdfplumber.open(r.pdf) as p:
        text = p.pages[0].extract_text() or ""
    assert "Titelprobe" in text

def test_missing_logo_errors(tmp_path):
    fx = tmp_path / "misslogo.tex"
    fx.write_text(r"""\documentclass{swisstex}
\begin{document}
\swisslogo{nosuch.pdf}
\end{document}
""")
    r = build_doc(fx, tmp_path)
    assert r.returncode != 0
    assert "logo" in r.log.lower()

def test_title_grid(tmp_path, logo_pdf):
    fx = _inject_logo(tmp_path, logo_pdf)
    r = build_doc(fx, tmp_path)
    assert r.returncode == 0, r.log[-2000:]
    code, out = swisscheck(r.pdf)
    assert code == 0, out

# --- Global constraint: invalid axis value is a hard error ------------------

def test_invalid_axis_errors(tmp_path):
    fx = tmp_path / "badaxis.tex"
    fx.write_text(r"""\documentclass{swisstex}
\begin{document}
\swisslogo[axis=cover]{nosuch.pdf}
\end{document}
""")
    r = build_doc(fx, tmp_path)
    assert r.returncode != 0
    assert "axis" in r.log.lower()

# --- axis=text vs axis=full: left edge really moves -------------------------

def test_logo_axis_full_extends_left_of_text_axis(tmp_path, logo_pdf):
    logo = str(logo_pdf)
    text_fx = tmp_path / "axistext.tex"
    text_fx.write_text(
        r"\documentclass{swisstex}\begin{document}"
        r"\swisslogo[lines=2, axis=text]{" + logo + r"}\end{document}\n")
    full_fx = tmp_path / "axisfull.tex"
    full_fx.write_text(
        r"\documentclass{swisstex}\begin{document}"
        r"\swisslogo[lines=2, axis=full]{" + logo + r"}\end{document}\n")
    r_text = build_doc(text_fx, tmp_path)
    r_full = build_doc(full_fx, tmp_path)
    assert r_text.returncode == 0, r_text.log[-2000:]
    assert r_full.returncode == 0, r_full.log[-2000:]
    rects_text = _fill_rects(r_text.pdf)
    rects_full = _fill_rects(r_full.pdf)
    assert rects_text and rects_full
    # axis=full breaks out over the margin column + gutter, so its left edge
    # sits strictly to the left of axis=text's left edge (I2's frame-element
    # exception).
    assert rects_full[0]["x0"] < rects_text[0]["x0"]

# --- Old 3-arg form is unchanged (deprecated but still working) -------------

def test_positional_swisstitle_still_works(tmp_path):
    fx = tmp_path / "pos.tex"
    fx.write_text(r"""\documentclass{swisstex}
\begin{document}
\swisstitle{Bericht}{Titelprobe}{Untertitel}

\section{Abschnitt}
Grundtext nach dem klassischen dreiargumentigen Titelblock, genug Woerter
fuer eine volle Zeile im Basisraster der Klasse.
\end{document}
""")
    r = build_doc(fx, tmp_path)
    assert r.returncode == 0, r.log[-2000:]
    with pdfplumber.open(r.pdf) as p:
        text = p.pages[0].extract_text() or ""
    assert "Titelprobe" in text

# --- Empty slots collapse: no reserved space for a missing subtitle --------

def test_empty_slot_collapses(tmp_path):
    full = tmp_path / "full.tex"
    full.write_text(r"""\documentclass{swisstex}
\begin{document}
\swisstitle*{kicker=Bericht, title=Titelprobe, subtitle=Untertitel}
\end{document}
""")
    empty = tmp_path / "empty.tex"
    empty.write_text(r"""\documentclass{swisstex}
\begin{document}
\swisstitle*{kicker=Bericht, title=Titelprobe}
\end{document}
""")
    r_full = build_doc(full, tmp_path)
    r_empty = build_doc(empty, tmp_path)
    assert r_full.returncode == 0, r_full.log[-2000:]
    assert r_empty.returncode == 0, r_empty.log[-2000:]
    lines_full = _rule_lines(r_full.pdf)
    lines_empty = _rule_lines(r_empty.pdf)
    assert len(lines_full) == 1 and len(lines_empty) == 1
    # No subtitle -> no reserved subtitle line/gap -> the closing rule sits
    # higher on the page (smaller distance from the top) than when a
    # subtitle is present.
    assert lines_empty[0]["top"] < lines_full[0]["top"]

# --- Defect 4: positional and starred forms must render identically --------

def test_both_forms_render_identically(tmp_path):
    pos = tmp_path / "bothpos.tex"
    pos.write_text(r"""\documentclass{swisstex}
\begin{document}
\swisstitle{Bericht}{Titelprobe}{Untertitel}
\end{document}
""")
    star = tmp_path / "bothstar.tex"
    star.write_text(r"""\documentclass{swisstex}
\begin{document}
\swisstitle*{kicker=Bericht, title=Titelprobe, subtitle=Untertitel}
\end{document}
""")
    r_pos = build_doc(pos, tmp_path)
    r_star = build_doc(star, tmp_path)
    assert r_pos.returncode == 0, r_pos.log[-2000:]
    assert r_star.returncode == 0, r_star.log[-2000:]
    with pdfplumber.open(r_pos.pdf) as pp, pdfplumber.open(r_star.pdf) as ps:
        wp = [w for w in pp.pages[0].extract_words() if w["text"] == "Titelprobe"]
        ws = [w for w in ps.pages[0].extract_words() if w["text"] == "Titelprobe"]
    assert wp and ws
    # Same page, same content, same rendering path (\swiss@titlebody) -> the
    # title word must land at the identical baseline position in both PDFs.
    assert abs(wp[0]["top"] - ws[0]["top"]) < 0.01
    assert abs(wp[0]["x0"] - ws[0]["x0"]) < 0.01
    lines_pos = _rule_lines(r_pos.pdf)
    lines_star = _rule_lines(r_star.pdf)
    assert len(lines_pos) == 1 and len(lines_star) == 1
    assert abs(lines_pos[0]["top"] - lines_star[0]["top"]) < 0.01
    assert abs(lines_pos[0]["x0"] - lines_star[0]["x0"]) < 0.01
    assert abs(lines_pos[0]["x1"] - lines_star[0]["x1"]) < 0.01
