import pdfplumber
from conftest import build_doc, swisscheck, ROOT

# PDF-Punkt-Umrechnungen wie in swisscheck.py (dort MM/PT genannt) --
# eigenstaendig hier gehalten, damit dieser Test nicht von einem
# swisscheck-internen Importpfad abhaengt. PDF-Koordinaten stehen in
# DTP-Punkt (1/72 Zoll), TeX rechnet in TeX-Punkt (1/72,27 Zoll).
MM = 72 / 25.4
PT = 72 / 72.27
TOPMARGIN_MM = 26.0     # Klassenvorgabe (\DeclareStringOption[26mm]{topmargin})
GRIDUNIT_PT = 13.5      # Klassenvorgabe (\DeclareStringOption[13.5pt]{gridunit})


def _fullwidth_fill_rects(page, tol=0.5):
    return [r for r in (page.rects or [])
            if r["fill"] and abs((r["x1"] - r["x0"]) - page.width) < tol]


def _band_rect(page):
    r"""Das Farbband, nicht der volle Seitenhintergrund (tint=false zeichnet
    \swisscover selbst einen eigenen papierfarbenen Vollflaechen-Hintergrund,
    siehe swiss@coverbody -- der ist ebenfalls seitenbreit, aber seitenhoch)."""
    full = _fullwidth_fill_rects(page)
    bands = [r for r in full if (r["bottom"] - r["top"]) < page.height - 1]
    return bands[0] if bands else None


# --- Step 1 tests from the brief -------------------------------------------

def test_slot_cover_builds_and_band_on_grid(tmp_path):
    r = build_doc(ROOT / "tests/fixtures/cover.tex", tmp_path)
    assert r.returncode == 0, r.log[-2000:]
    with pdfplumber.open(r.pdf) as p:
        band = _band_rect(p.pages[0])
    assert band is not None, r.log[-2000:]
    expected_top = TOPMARGIN_MM * MM + 38 * GRIDUNIT_PT * PT
    expected_bottom = TOPMARGIN_MM * MM + 47 * GRIDUNIT_PT * PT
    assert abs(band["top"] - expected_top) < 0.5, \
        (band, expected_top, r.log[-2000:])
    assert abs(band["bottom"] - expected_bottom) < 0.5, \
        (band, expected_bottom, r.log[-2000:])


def test_no_glyph_by_default(tmp_path):
    r = build_doc(ROOT / "tests/fixtures/cover.tex", tmp_path)
    assert r.returncode == 0, r.log[-2000:]
    with pdfplumber.open(r.pdf) as p:
        sizes = [c["size"] for c in p.pages[0].chars]
    assert sizes, r.log[-2000:]
    assert all(s <= 100 for s in sizes), (sorted(set(sizes)), r.log[-2000:])


def test_positional_form_warns(tmp_path):
    fx = tmp_path / "poscover.tex"
    fx.write_text(r"""\documentclass{swisstex}
\begin{document}
\swisscover{Kennzeichnung}{Titel}{Untertitel}{Fusszeile}
\end{document}
""")
    r = build_doc(fx, tmp_path)
    assert r.returncode == 0, r.log[-2000:]
    assert "deprecated" in r.log, r.log[-2000:]
    with pdfplumber.open(r.pdf) as p:
        text = p.pages[0].extract_text() or ""
    assert "Titel" in text, (text, r.log[-2000:])


def test_autofill_from_meta(tmp_path):
    r = build_doc(ROOT / "tests/fixtures/cover.tex", tmp_path)
    assert r.returncode == 0, r.log[-2000:]
    with pdfplumber.open(r.pdf) as p:
        text = p.pages[0].extract_text() or ""
    assert "Q-9" in text, (text, r.log[-2000:])


# --- Weak spot 5 (brief): classification mark on the cover ------------------

def test_classification_mark_on_cover(tmp_path):
    # Same fixture as above: \swissmeta sets classification=internal, so
    # \swiss@classlevel>0 and the kicker line must carry the tracked mark.
    # Task 5's lesson (\swiss@str resolved BEFORE \tracked) is exercised by
    # construction here: "INTERN" (uppercase, from \tracked's \MakeUppercase)
    # must appear, not the raw string-table key "classification-internal".
    r = build_doc(ROOT / "tests/fixtures/cover.tex", tmp_path)
    assert r.returncode == 0, r.log[-2000:]
    with pdfplumber.open(r.pdf) as p:
        text = p.pages[0].extract_text() or ""
    assert "INTERN" in text, (text, r.log[-2000:])
    assert "classification" not in text.lower(), (text, r.log[-2000:])


def test_public_classification_no_mark(tmp_path):
    fx = tmp_path / "pubcover.tex"
    fx.write_text(r"""\documentclass{swisstex}
\swissmeta{docid=Q-9, classification=public}
\begin{document}
\swisscover*{kicker=Angebot, title=Probe}
\end{document}
""")
    r = build_doc(fx, tmp_path)
    assert r.returncode == 0, r.log[-2000:]
    with pdfplumber.open(r.pdf) as p:
        text = p.pages[0].extract_text() or ""
    assert "INTERN" not in text and "ffentlich" not in text.upper(), \
        (text, r.log[-2000:])
    assert "Q-9" in text, (text, r.log[-2000:])


# --- Weak spot 1 (brief): variant mechanism ---------------------------------

def test_variant_defaults_then_explicit_wins(tmp_path):
    fx = tmp_path / "variant.tex"
    fx.write_text(r"""\documentclass{swisstex}
\makeatletter
\swisscovervariant{proposal}{kicker=Vorlage,title=VorlageTitel}
\makeatother
\begin{document}
\swisscover*{variant=proposal, title=Override}
\end{document}
""")
    r = build_doc(fx, tmp_path)
    assert r.returncode == 0, r.log[-2000:]
    with pdfplumber.open(r.pdf) as p:
        text = p.pages[0].extract_text() or ""
    # kicker comes from the variant's own defaults, uppercased by \tracked
    assert "VORLAGE" in text, (text, r.log[-2000:])
    # title is explicit on the call -> must win over the variant's own
    # default value ("VorlageTitel"), regardless of "variant=" appearing
    # BEFORE "title=" in the key list.
    assert "Override" in text, (text, r.log[-2000:])
    assert "VorlageTitel" not in text, (text, r.log[-2000:])


def test_variant_explicit_before_variant_key_still_wins(tmp_path):
    # Same as above but with the explicit key written BEFORE "variant=" in
    # the call -- the two-family design must be order-independent (see the
    # class comment on \swiss@coverbody / \swisscoverslots): a single
    # \setkeys pass over one shared family would let a second pass's
    # "variant=..." re-apply the variant's default and clobber an explicit
    # key that happened to precede it in the list.
    fx = tmp_path / "variant2.tex"
    fx.write_text(r"""\documentclass{swisstex}
\makeatletter
\swisscovervariant{proposal}{kicker=Vorlage,title=VorlageTitel}
\makeatother
\begin{document}
\swisscover*{title=Override, variant=proposal}
\end{document}
""")
    r = build_doc(fx, tmp_path)
    assert r.returncode == 0, r.log[-2000:]
    with pdfplumber.open(r.pdf) as p:
        text = p.pages[0].extract_text() or ""
    assert "Override" in text, (text, r.log[-2000:])
    assert "VorlageTitel" not in text, (text, r.log[-2000:])


def test_unknown_variant_errors(tmp_path):
    fx = tmp_path / "badvariant.tex"
    fx.write_text(r"""\documentclass{swisstex}
\begin{document}
\swisscover*{variant=nope}
\end{document}
""")
    r = build_doc(fx, tmp_path)
    assert r.returncode != 0, r.log[-2000:]
    assert "variant" in r.log.lower(), r.log[-2000:]


# --- Weak spot 2 (brief): band=<start>/<lines> parsing/validation ----------

def test_band_malformed_value_errors(tmp_path):
    fx = tmp_path / "badband.tex"
    fx.write_text(r"""\documentclass{swisstex}
\begin{document}
\swisscover*{band=abc}
\end{document}
""")
    r = build_doc(fx, tmp_path)
    assert r.returncode != 0, r.log[-2000:]
    assert "band" in r.log.lower(), r.log[-2000:]


def test_band_non_integer_half_errors(tmp_path):
    fx = tmp_path / "badband2.tex"
    fx.write_text(r"""\documentclass{swisstex}
\begin{document}
\swisscover*{band=38/x}
\end{document}
""")
    r = build_doc(fx, tmp_path)
    assert r.returncode != 0, r.log[-2000:]
    assert "band" in r.log.lower(), r.log[-2000:]


def test_band_sanity_warning_beyond_grid(tmp_path):
    fx = tmp_path / "bandwarn.tex"
    fx.write_text(r"""\documentclass{swisstex}
\begin{document}
\swisscover*{kicker=A, title=B, band=45/10}
\end{document}
""")
    r = build_doc(fx, tmp_path)
    # Sanity check is a WARNING, not an error: the document must still build.
    assert r.returncode == 0, r.log[-2000:]
    assert "swisstex" in r.log and "grid" in r.log, r.log[-2000:]
    assert "Warning" in r.log, r.log[-2000:]


# --- Weak spot 4 (brief): glyph only when given, deprecated old knobs ------

def test_glyph_given_renders_large_character(tmp_path):
    fx = tmp_path / "glyphcover.tex"
    fx.write_text(r"""\documentclass{swisstex}
\begin{document}
\swisscover*{kicker=Angebot, title=Probe, glyph=A}
\end{document}
""")
    r = build_doc(fx, tmp_path)
    assert r.returncode == 0, r.log[-2000:]
    with pdfplumber.open(r.pdf) as p:
        sizes = [c["size"] for c in p.pages[0].chars]
    assert any(s > 100 for s in sizes), (sorted(set(sizes)), r.log[-2000:])


def test_deprecated_glyph_macros_warn(tmp_path):
    fx = tmp_path / "depmacro.tex"
    fx.write_text(r"""\documentclass{swisstex}
\begin{document}
\swisscoverglyphx\swisscoverglyphy\swisscoverglyphsize\swisscoverglyph
\end{document}
""")
    r = build_doc(fx, tmp_path)
    assert r.returncode == 0, r.log[-2000:]
    assert r.log.count("is deprecated") >= 4, r.log[-2000:]
    assert "swisscoverglyphx" in r.log, r.log[-2000:]
    assert "swisscoverglyphy" in r.log, r.log[-2000:]
    assert "swisscoverglyphsize" in r.log, r.log[-2000:]


# --- Auto-fill hierarchy: explicit key beats \swissmeta ---------------------

def test_explicit_docid_wins_over_meta(tmp_path):
    fx = tmp_path / "docidwin.tex"
    fx.write_text(r"""\documentclass{swisstex}
\swissmeta{docid=Q-9}
\begin{document}
\swisscover*{kicker=A, title=B, docid=EXPLICIT-1}
\end{document}
""")
    r = build_doc(fx, tmp_path)
    assert r.returncode == 0, r.log[-2000:]
    with pdfplumber.open(r.pdf) as p:
        text = p.pages[0].extract_text() or ""
    assert "EXPLICIT-1" in text, (text, r.log[-2000:])
    assert "Q-9" not in text, (text, r.log[-2000:])


# --- Legacy 4-arg form: comma-bearing argument must survive brace-wrapping -

def test_positional_form_foot_with_comma_survives(tmp_path):
    # The manual's own cover call has a literal comma in its 4th (foot)
    # argument ("Raster 13,5 pt | ..."). \swiss@coverlegacy must brace each
    # positional argument when building the key=value string it hands to
    # \swisscoverslots, or an internal comma gets misread as a key
    # separator by keyval's top-level comma split.
    fx = tmp_path / "commafoot.tex"
    fx.write_text(r"""\documentclass{swisstex}
\begin{document}
\swisscover{K}{T}{U}{Raster 13,5\,pt \textbar{} Version 2.0}
\end{document}
""")
    r = build_doc(fx, tmp_path)
    assert r.returncode == 0, r.log[-2000:]
    with pdfplumber.open(r.pdf) as p:
        text = p.pages[0].extract_text() or ""
    assert "13,5" in text, (text, r.log[-2000:])
    assert "Version2.0" in text.replace(" ", ""), (text, r.log[-2000:])


# --- swisscheck: cover on the new grid geometry passes the full check ------

def test_cover_fixture_passes_swisscheck(tmp_path):
    r = build_doc(ROOT / "tests/fixtures/cover.tex", tmp_path)
    assert r.returncode == 0, r.log[-2000:]
    code, out = swisscheck(r.pdf)
    assert code == 0, out


# --- A3: Überformatzeichen ist kein Anzeigengrad ---------------------------

def test_glyph_cover_passes_swisscheck(tmp_path):
    # Das Zeichen misst 34 Rasterzeilen (459 pt) und fiel damit durch A12s
    # Grössenregel ("ausserhalb der Anzeigenskala"). Es ist aber gar kein
    # Anzeigengrad, sondern ein aus dem Raster abgeleitetes Überformat; A12
    # nimmt es von der Grössenregel aus und prüft statt dessen seine
    # Verankerung (Grundlinie auf Rasterzeile, linke Kante auf der Textachse).
    r = build_doc(ROOT / "tests/fixtures/glyph-cover.tex", tmp_path)
    assert r.returncode == 0, r.log[-2000:]
    code, out = swisscheck(r.pdf)
    assert code == 0, out
    a12 = next(z for z in out.splitlines() if z.strip().startswith("A12"))
    assert "ok" in a12, a12
    assert "(0 geprüft)" not in a12, a12


def test_glyph_anchor_measured_on_grid_and_axis(tmp_path):
    r = build_doc(ROOT / "tests/fixtures/glyph-cover.tex", tmp_path)
    assert r.returncode == 0, r.log[-2000:]
    with pdfplumber.open(r.pdf) as p:
        page = p.pages[0]
        gross = [c for c in page.chars if c["size"] > 8 * GRIDUNIT_PT * PT]
        assert len(gross) == 1, sorted({round(c["size"], 1) for c in page.chars})
        c = gross[0]
        grundlinie = page.height - c["matrix"][5]
    abstand = grundlinie - TOPMARGIN_MM * MM
    rest = abstand % (GRIDUNIT_PT * PT)
    assert min(rest, GRIDUNIT_PT * PT - rest) < 0.6, grundlinie
    innermargin = (24.0 + 30.0 + 7.0) * MM
    assert abs(c["x0"] - innermargin) < 0.6, c["x0"] / MM


def test_glyph_baseline_off_grid_is_caught(tmp_path):
    # Deckungstest für die neue Regel selbst: eine halbe Rasterzeile Versatz
    # gibt es über glyphline= nicht (ganzzahlig), wohl aber über einen
    # abweichenden topmargin bei sonst gleichem Aufruf -- das Zeichen hängt
    # dann zwar an derselben Rasterzeile wie zuvor, aber der Sidecar-Wert
    # topmargin verschiebt den Bezugspunkt. Geprüft wird also, dass A12 die
    # Verankerung wirklich MISST und nicht nur zählt.
    r = build_doc(ROOT / "tests/fixtures/glyph-cover.tex", tmp_path)
    assert r.returncode == 0, r.log[-2000:]
    side = tmp_path / "verschoben.swisscheck"
    quelle = (tmp_path / "glyph-cover.swisscheck").read_text()
    side.write_text(quelle.replace("topmargin=26mm", "topmargin=28mm"))
    code, out = swisscheck(r.pdf, "--params", str(side))
    assert code != 0, out
    assert "Zeichen-Grundlinie" in out or "Zeichen-Linkskante" in out, out


# --- C2: foot=\meta{...} auf \swisscover* ---------------------------------

def test_cover_foot_accepts_meta_placeholder(tmp_path):
    # Die vier \edef-Proben, die entscheiden, ob die Umschlag-Fusszeile
    # überhaupt gesetzt wird, laufen VOR dem Fusssatz. \meta war bis zu
    # dieser Änderung erst danach gebunden -- ein foot=\meta{docid} (die
    # dokumentierte Schreibweise, dieselbe wie in \swissfootformat) starb
    # dort an "Undefined control sequence".
    r = build_doc(ROOT / "tests/fixtures/covermeta.tex", tmp_path)
    assert r.returncode == 0, r.log[-3000:]
    assert "Undefined control sequence" not in r.log, r.log[-3000:]
    with pdfplumber.open(r.pdf) as p:
        text = (p.pages[0].extract_text() or "").replace(" ", "")
    assert "Q-42" in text, text
    assert "3.1" in text, text
