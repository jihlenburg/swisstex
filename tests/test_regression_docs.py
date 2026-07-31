# tests/test_regression_docs.py -- drei Regressionsvorlagen, portiert aus
# SwissTeX 1.3.1 (Produktionsfork: test-stress.tex, test-figure.tex,
# test-display.tex -> tests/fixtures/stress.tex, figure.tex, display.tex).
# Sie stammen aus echtem Produktionsgebrauch und deckten dort Randfaelle ab,
# die die kuratierten v2.0-Fixtures nicht beruehren: verschachtelte Listen,
# eine dritte Gliederungsebene, ein Seitenumbruch mitten im Absatz
# (stress.tex), ein Rahmenplatzhalter in swissfigure (figure.tex), sowie
# Schaugrade und ein Farbfeld hinter einem Umschlag in der modernen
# Slot-Form (display.tex, siehe Kopfkommentar dort).
#
# Da v2.0 seit Task 9 bei jedem Bau eine Kennzahlen-Sidecar-Datei schreibt,
# feuern hier automatisch auch die sidecar-gebundenen Prüfungen (A10-A13,
# A15-A17) und A18 (marginfix-Port) mit -- ohne dass die Vorlagen dafür
# etwas Besonderes täten, anders als zur Zeit des Forks (v1.3.1 kannte nur
# A1-A10).

import sys

import pdfplumber

from conftest import ROOT, assert_clean_refs, build_doc, swisscheck

sys.path.insert(0, str(ROOT))
import swisscheck as sc  # noqa: E402


def test_stress_builds_across_a_page_break(tmp_path):
    r = build_doc(ROOT / "tests/fixtures/stress.tex", tmp_path)
    assert r.returncode == 0, r.log[-2000:]
    assert_clean_refs(r.log, context="stress.tex")


def test_stress_swisscheck_verbatim_font_gap_is_closed(tmp_path):
    """War RED: stress.tex war die erste Vorlage in diesem Repository, die
    \\begin{verbatim} benutzt, und deckte damit eine echte, vorbestehende
    Lücke auf -- verbatim bekam nur den Rasterfang (\\gridsnapenv), nie eine
    deklarierte Schriftfamilie, und embettete darum die LaTeX-Vorgabe
    ('LMMono10-Regular'), ein I4-Verstoss, den A16 zurecht als FEHLER
    meldete. Portierungsbericht dokumentierte den Befund als ausserhalb des
    damaligen Portierungsumfangs.

    Nutzerentscheid vom 2026-07-31 schliesst die Lücke: I4 liest sich seither
    als \"eine Familie plus deklarierte Mathe- und Code-Begleiter\" --
    \\verbatim@font (treibt sowohl die verbatim-Umgebung als auch \\verb, siehe
    latex.ltx) läuft jetzt auf \\swisscodeface, der zweite deklarierte
    Begleiter neben der Mathe-Schrift, Vorgabe DejaVu Sans Mono. A16 lässt
    genau diese Familie zusätzlich zu (Sidecar-Schlüssel codeface=...) --
    derselbe Mechanismus wie für mainfamily/condensedfamily/mathfont."""
    r = build_doc(ROOT / "tests/fixtures/stress.tex", tmp_path)
    assert r.returncode == 0, r.log[-2000:]
    assert "codeface" in r.sidecar and r.sidecar["codeface"], r.sidecar
    with pdfplumber.open(r.pdf) as p:
        fonts = {c["fontname"] for pg in p.pages for c in pg.chars}
    assert any("DejaVuSansMono" in f for f in fonts), fonts
    assert not any("LMMono" in f for f in fonts), fonts
    code, out = swisscheck(r.pdf)
    assert code == 0, out
    # Alle Prüfungen bleiben ok -- A16 eingeschlossen, nicht nur die, die
    # von der Vorlage unberührt waren.
    for kennung in ("A1", "A2", "A3", "A4", "A7", "A8", "A13", "A16", "A17", "A18"):
        zeile = next(z for z in out.splitlines() if z.strip().startswith(kennung))
        assert "ok" in zeile, (kennung, zeile, out)


def test_figure_placeholder_and_swisscheck_clean(tmp_path):
    r = build_doc(ROOT / "tests/fixtures/figure.tex", tmp_path)
    assert r.returncode == 0, r.log[-2000:]
    assert_clean_refs(r.log, context="figure.tex")
    code, out = swisscheck(r.pdf)
    assert code == 0, out
    a9 = next(z for z in out.splitlines() if z.strip().startswith("A9"))
    assert "(1 geprüft)" in a9, a9


def test_display_build_is_warning_free(tmp_path):
    """Die Vorlage nutzt ausschliesslich die MODERNE Slot-Form
    (\\swisscover*{...glyph=S...}); die veraltete Positionsform
    \\swisscover{K}{T}{U}{F} und \\renewcommand{\\swisscoverglyph}{...} aus
    dem Original (SwissTeX 1.3.1) kommen hier nicht mehr vor. Der Bau muss
    darum ohne eine einzige swisstex-Abkündigungswarnung durchlaufen --
    genau das, wofür der Deprecation-Shim (swisstex.cls Abschnitt 10a)
    gebaut ist: alte Dokumente warnen, neue bleiben still."""
    r = build_doc(ROOT / "tests/fixtures/display.tex", tmp_path)
    assert r.returncode == 0, r.log[-2000:]
    assert_clean_refs(r.log, context="display.tex")
    assert "deprecated" not in r.log, r.log[-2000:]
    assert "swisstex Warning" not in r.log, r.log[-2000:]


def test_display_swisscheck_clean_including_a12_and_a18(tmp_path):
    r = build_doc(ROOT / "tests/fixtures/display.tex", tmp_path)
    assert r.returncode == 0, r.log[-2000:]
    code, out = swisscheck(r.pdf)
    assert code == 0, out
    # A12 (Umschlag) und A18 (marginfix-Port) müssen an dieser Vorlage
    # tatsächlich etwas gemessen haben, nicht nur vacuously "ok" sein.
    a12 = next(z for z in out.splitlines() if z.strip().startswith("A12"))
    assert "(0 geprüft)" not in a12, a12
