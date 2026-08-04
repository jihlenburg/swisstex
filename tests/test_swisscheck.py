# tests/test_swisscheck.py -- Task 9: Kennzahlen-Sidecar + swisscheck A10-A13/A15/A16.
#
# Drei Tests nach dem Brief (Schritt 1), plus einige direkte Einheitentests
# für die Parser-/from_sidecar-Logik in swisscheck.py selbst (kein Build
# nötig, schnell, deckt Formatfehler ab, die ein reiner PDF-Roundtrip nicht
# unbedingt zeigen würde).

import re
import sys
from pathlib import Path

import pytest

from conftest import assert_clean_refs, build_doc, swisscheck, ROOT

sys.path.insert(0, str(ROOT))
import swisscheck as sc  # noqa: E402  (Modul, nicht die conftest-Hilfsfunktion)


# --- (a) Sidecar-Datei: existiert, enthält die eingefrorenen Werte ---------

def test_sidecar_written_with_frozen_values(tmp_path):
    r = build_doc(ROOT / "tests/fixtures/plain.tex", tmp_path)
    assert r.returncode == 0, r.log[-2000:]
    sidecar_pfad = tmp_path / "plain.swisscheck"
    assert sidecar_pfad.exists(), "keine .swisscheck-Sidecar-Datei geschrieben"
    d = r.sidecar
    assert d, "Sidecar-Datei ist leer oder wurde nicht geparst"
    # Kennzahlen, die aus der Klassenvorgabe (13.5pt-Raster) folgen und sich
    # nicht ändern dürfen, solange plain.tex keine Optionen setzt:
    assert d["gridunit"] == "13.5pt"
    assert d["bodysize"] == "9.5pt"
    assert d["annotationleading"] == "9.0pt"
    assert d["glossleading"] == "10.125pt"
    assert d["footnoteleading"] == "10.125pt"
    assert d["headsep"] == "27.0pt"
    assert d["footskip"] == "40.5pt"
    assert d["outermargin"] == "24mm"
    assert d["margincolumn"] == "30mm"
    assert d["gutter"] == "7mm"
    assert d["numberzone"] == "8mm"
    assert d["textcolumn"] == "105mm"
    assert d["topmargin"] == "26mm"
    assert d["gridlines"] == "51"
    assert d["accent"] == "255,55,37"
    # v2.0-Vorgabe: kein eigenes Band gesetzt -> Ein-Rot-System, band=accent
    # (siehe swisstex.cls Abschnitt 2b/4 -- nicht das RGB-Tripel selbst).
    assert d["band"] == "accent"
    assert d["paper"] == "234,232,208"
    assert d["ink"] == "26,26,26"
    assert d["mainfamily"] == "texgyreheros"
    assert d["condensedfamily"] == "texgyreheroscn"
    assert "TeXGyreDejaVuMath" in d["mathfont"]
    assert d["classification"] == "none"
    assert d["docid"] == ""


def test_identity_sidecar_carries_resolved_identity_values(tmp_path):
    # acme-demo.tex (identity=acme, classification=internal, docid gesetzt)
    # muss die DURCH DIE IDENTITÄT ersetzten Werte tragen, nicht die
    # Klassenvorgabe -- das ist der ganze Witz der Sidecar-Datei.
    r = build_doc(ROOT / "acme-demo.tex", tmp_path)
    assert r.returncode == 0, r.log[-3000:]
    d = r.sidecar
    assert d["accent"] == "200,16,46"
    assert d["band"] == "accent"          # keine eigene band=, Ein-Rot-Pfad
    assert d["mainfamily"] == "SwissTeXGrotesk"
    assert d["condensedfamily"] == "SwissTeXGroteskCondensed"
    assert d["classification"] == "internal"
    assert d["docid"] == "TR-2026-014"


# --- (b) acme-demo besteht ALLE Prüfungen inkl. A10-A16 --------------------

def test_acme_demo_sidecar_checks_all_ok(tmp_path):
    r = build_doc(ROOT / "acme-demo.tex", tmp_path)
    assert r.returncode == 0, r.log[-3000:]
    assert (tmp_path / "acme-demo.swisscheck").exists()
    code, out = swisscheck(r.pdf)
    assert code == 0, out
    assert "Kennzahlen-Sidecar: gefunden" in out, out
    for kennung in ("A10", "A11", "A12", "A13", "A15", "A16", "A17"):
        zeile = next((z for z in out.splitlines() if z.strip().startswith(kennung)), None)
        assert zeile is not None, f"{kennung} fehlt in der Ausgabe:\n{out}"
        assert "ok" in zeile, f"{kennung} nicht 'ok':\n{zeile}\n\nVolle Ausgabe:\n{out}"
    # Alle sidecar-gebundenen Prüfungen sind an acme-demo tatsächlich
    # exercisiert, nicht nur vacuously "ok" durch 0 geprüfte Fälle: A10
    # (Fusszeile) über dessen klassifizierte Fusszeile, A11 (Kolumnentitel)
    # über Pagina, Kopfgrundlinie und Kopfzone jeder Inhaltsseite, A12
    # (Umschlag) über den eigenen Umschlag, A13 (Kommensurabilität) über die
    # drei deklarierten Verhältnisse UND die Randglosse, A15 (Farbrollen)
    # über die gemessene Füllfarbe des Umschlagbands -- vorher zählte A15
    # hier eine Prüfung, ohne etwas gemessen zu haben, A16
    # (Schriftinventar) über die eingebetteten SwissTeXGrotesk-/Mathe-
    # Schriftnamen, A17 (Glossenlänge) über Randglosse und Tabellenlegende.
    for kennung in ("A10", "A11", "A12", "A13", "A15", "A16", "A17"):
        zeile = next(z for z in out.splitlines() if z.strip().startswith(kennung))
        assert "(0 geprüft)" not in zeile, zeile


def test_manual_and_demo_sidecar_checks_all_ok(tmp_path):
    # Die beiden anderen Referenzdokumente (kein Identity-Pfad) -- derselbe
    # Vorgabe-Anbieter wie plain.tex, aber echte mehrseitige Inhalte mit
    # Kolumnentiteln, Randglossen, Tabellen, einem Umschlag (Manual) bzw.
    # einer Titelblock-Seite ohne Umschlag (Demo).
    for name in ("swisstex-manual.tex", "swisstex-demo.tex"):
        r = build_doc(ROOT / name, tmp_path, runs=2)
        assert r.returncode == 0, (name, r.log[-3000:])
        # The manual carries real \ref/\label cross-references (Identität,
        # Sprachen); a regression back to a single pass would leave
        # "Abschnitt??" in the PDF and pass build_doc's returncode check
        # anyway (xelatex still exits 0) -- this is the machine net for
        # exactly that (Task 5 fix round 1; conftest.assert_clean_refs).
        assert_clean_refs(r.log, context=name)
        code, out = swisscheck(r.pdf)
        assert code == 0, (name, out)


# --- (c) Bewusst gebrochene Vorlage: A11 schlägt fehl ----------------------

def test_broken_head_image_fails_A11(tmp_path):
    r = build_doc(ROOT / "tests/fixtures/broken-head-image.tex", tmp_path)
    assert r.returncode == 0, r.log[-2000:]
    assert (tmp_path / "broken-head-image.swisscheck").exists()
    code, out = swisscheck(r.pdf)
    assert code != 0, out
    a11 = next((z for z in out.splitlines() if z.strip().startswith("A11")), None)
    assert a11 is not None, out
    assert "FEHLER" in a11, out
    assert "Grafik in der Kopfzone" in out, out


# --- Parser-/from_sidecar-Einheitentests (kein Build nötig) ----------------

def test_parse_pt_and_mm():
    assert sc._parse_pt("13.5pt") == pytest.approx(13.5)
    assert sc._parse_pt("9.0pt") == pytest.approx(9.0)
    assert sc._parse_mm("24mm") == pytest.approx(24.0)
    assert sc._parse_mm("1cm") == pytest.approx(10.0)


def test_parse_rgb():
    assert sc._parse_rgb("255,55,37") == (255, 55, 37)
    assert sc._parse_rgb(" 200, 16 , 46 ") == (200, 16, 46)


def test_raster_from_sidecar_overrides_base():
    basis = sc.Raster()
    assert basis.has_sidecar is False
    d = {
        "outermargin": "20mm", "gridunit": "14pt", "accent": "10,20,30",
        "band": "accent", "mainfamily": "Foo Grotesk",
    }
    r = sc.Raster.from_sidecar(d, basis)
    assert r.has_sidecar is True
    assert r.outermargin == pytest.approx(20.0)
    assert r.gridunit_pt == pytest.approx(14.0)
    assert r.accent_rgb == (10, 20, 30)
    assert r.band_is_accent is True
    assert r.mainfamily == "Foo Grotesk"
    # unveränderte Felder bleiben bei der Kommandozeilen-Vorgabe (base):
    assert r.margincolumn == pytest.approx(basis.margincolumn)


def test_new_checks_skip_cleanly_without_sidecar():
    # Kernanforderung: ohne Sidecar-Datei (ältere PDFs) 0 geprüft, kein
    # Verstoss -- die sechs neuen Prüfungen dürfen niemals FEHLER melden,
    # nur weil Kennzahlen fehlen.
    r = sc.Raster()  # has_sidecar=False, wie main() es ohne --params baut
    for fn in (sc.pruefe_fusszeile, sc.pruefe_kolumnentitel, sc.pruefe_umschlag,
               sc.pruefe_kommensurabilitaet, sc.pruefe_farbrollen,
               sc.pruefe_schriftinventar, sc.pruefe_glossenlaenge):
        befund = fn(pdf=None, r=r)
        assert befund.geprueft == 0, befund.kennung
        assert befund.bestanden, befund.kennung
        assert "übersprungen" in befund.titel, befund.kennung


# --- B2: A13 prüft auch die DEKLARIERTEN Verhältnisse ----------------------

def test_kleiner_bruch_erkennt_rastermassbrueche():
    assert sc._kleiner_bruch(2 / 3) == (2, 3)
    assert sc._kleiner_bruch(3 / 4) == (3, 4)
    assert sc._kleiner_bruch(1.0) == (1, 1)
    # 0,84375 = 10.125/12 -- der Fall aus dem Bericht: in sich stimmig, aber
    # kein Bruch mit kleinem Nenner.
    assert sc._kleiner_bruch(10.125 / 12) is None
    assert sc._kleiner_bruch(11 / 13.5) is None


def test_a13_flags_incommensurable_declaration():
    # Genau die Sidecar-Datei, die die alte Fassung durchwinkte: gridunit=12
    # mit den Durchschüssen eines 13,5-pt-Rasters.
    basis = sc.Raster()
    r = sc.Raster.from_sidecar({
        "gridunit": "12pt", "bodysize": "9.5pt",
        "annotationleading": "9.0pt", "glossleading": "10.125pt",
        "footnoteleading": "10.125pt",
    }, basis)
    b = sc.Befund("A13", "probe")
    sc._pruefe_deklarierte_verhaeltnisse(r, b)
    assert b.geprueft == 3
    assert not b.bestanden
    assert any("10.125" in v and "Verhältnis" in v for v in b.verstoesse), b.verstoesse
    # 9/12 = 3/4 ist sehr wohl kommensurabel und darf nicht mitgemeldet werden.
    assert sum("annotationleading" in v for v in b.verstoesse) == 0, b.verstoesse


def test_a13_accepts_class_defaults():
    r = sc.Raster.from_sidecar({
        "gridunit": "13.5pt", "annotationleading": "9.0pt",
        "glossleading": "10.125pt", "footnoteleading": "10.125pt",
    }, sc.Raster())
    b = sc.Befund("A13", "probe")
    sc._pruefe_deklarierte_verhaeltnisse(r, b)
    assert b.geprueft == 3 and b.bestanden, b.verstoesse


def test_a13_end_to_end_with_mutated_sidecar(tmp_path):
    r = build_doc(ROOT / "tests/fixtures/plain.tex", tmp_path)
    assert r.returncode == 0, r.log[-2000:]
    side = tmp_path / "mutiert.swisscheck"
    side.write_text((tmp_path / "plain.swisscheck").read_text()
                    .replace("glossleading=10.125pt", "glossleading=10.0pt"))
    code, out = swisscheck(r.pdf, "--params", str(side))
    assert code != 0, out
    a13 = next(z for z in out.splitlines() if z.strip().startswith("A13"))
    assert "FEHLER" in a13, out
    assert "Verhältnis" in out, out


def test_a13_tolerates_caption_head_gap_repeated_per_page(tmp_path):
    # \swisstable haengt zwischen Legendenkopf ("Tabelle N") und
    # Legendentext ein festes "\\[1pt]" an. Mit EINER Legende je Seite
    # deckte die Einzelbeleg-Regel den Sollwert+1pt-Abstand ab; ZWEI
    # Tabellen auf derselben Seite erzeugten zwei gleiche Luecken, die
    # faelschlich als Cluster galten (gefunden an den tabellenreichen
    # Produktionsdokumenten des KIVAT-Forks, 2026-08-05).
    r = build_doc(ROOT / "tests/fixtures/legendenpaar.tex", tmp_path)
    assert r.returncode == 0, r.log[-2000:]
    code, out = swisscheck(r.pdf)
    a13 = next(z for z in out.splitlines() if z.strip().startswith("A13"))
    assert "ok" in a13, out
    # Die mehrzeiligen Legendentexte selbst bleiben Pruefgut: ihre
    # glossleading-Cluster duerfen nicht mit herausgefiltert werden.
    assert "(0 geprüft)" not in a13, a13


# --- B3: A15 misst wirklich ------------------------------------------------

def test_a15_measures_the_printed_band(tmp_path):
    # Auf dem Ein-Rot-Vorgabepfad zählte A15 vorher eine Prüfung, ohne
    # irgendetwas gemessen zu haben. Jetzt vergleicht sie die Füllfarbe des
    # gedruckten Bands gegen den deklarierten Ton.
    r = build_doc(ROOT / "tests/fixtures/cover.tex", tmp_path)
    assert r.returncode == 0, r.log[-2000:]
    code, out = swisscheck(r.pdf)
    assert code == 0, out
    a15 = next(z for z in out.splitlines() if z.strip().startswith("A15"))
    assert "(1 geprüft)" in a15, a15


def test_a15_catches_a_band_that_is_not_the_declared_colour(tmp_path):
    r = build_doc(ROOT / "tests/fixtures/cover.tex", tmp_path)
    assert r.returncode == 0, r.log[-2000:]
    side = tmp_path / "falschesband.swisscheck"
    side.write_text((tmp_path / "cover.swisscheck").read_text()
                    .replace("band=accent", "band=0,120,255"))
    code, out = swisscheck(r.pdf, "--params", str(side))
    assert code != 0, out
    assert "Farbband gedruckt" in out, out


def test_fuellfarbe_konvertiert_graustufe_und_rgb():
    assert sc._fuellfarbe({"non_stroking_color": (1, 0, 0)}) == (255, 0, 0)
    assert sc._fuellfarbe({"non_stroking_color": (0.5,)}) == (128, 128, 128)
    assert sc._fuellfarbe({"non_stroking_color": None}) is None


# --- C1: die Kopfgrundlinie liegt auf der verlängerten Rasterzeile ---------

def test_head_baseline_sits_on_the_extended_raster(tmp_path):
    # Unabhängig von swisscheck gemessen. Vor dieser Änderung lag die
    # Kopfgrundlinie in ALLEN drei Referenzdokumenten 3,587 pt daneben
    # (fancyhdr hängt einen \strut an den Kopfinhalt, und die nachfolgende --
    # unsichtbare -- Kopflinie schiebt den Bezugspunkt der Kopfbox um dessen
    # Tiefe unter die Textgrundlinie).
    import pdfplumber
    MM, PT = 72 / 25.4, 72 / 72.27
    r = build_doc(ROOT / "tests/fixtures/plain.tex", tmp_path)
    assert r.returncode == 0, r.log[-2000:]
    with pdfplumber.open(r.pdf) as p:
        page = p.pages[0]
        kopf = [c for c in page.chars if c["top"] < 26.0 * MM - 1]
        assert kopf, "keine Kopfzeile gefunden"
        grundlinien = {round(page.height - c["matrix"][5], 3) for c in kopf}
    assert len(grundlinien) == 1, grundlinien
    soll = 26.0 * MM - 2 * 13.5 * PT
    assert abs(grundlinien.pop() - soll) < 0.05, (grundlinien, soll)


def test_a11_catches_an_off_grid_head_baseline(tmp_path):
    # Deckungstest für die Prüfung selbst: der alte Zustand wird durch
    # Zurücksetzen von \headruleskip wiederhergestellt.
    fx = tmp_path / "schiefkopf.tex"
    fx.write_text(r"""\documentclass{swisstex}
\setrunningtitle{Probe}
\renewcommand{\headruleskip}{0pt}
\begin{document}
\section{Abschnitt}
Grundtext auf dem Raster mit genug Woertern fuer eine volle Zeile.
\end{document}""")
    r = build_doc(fx, tmp_path)
    assert r.returncode == 0, r.log[-2000:]
    code, out = swisscheck(r.pdf)
    assert code != 0, out
    assert "Kopfgrundlinie" in out, out


# --- C6: A16 kennt Logo-Schriften und die TeX-Gyre-Namensspaltung ---------

def test_schriftbasis_bridges_the_texgyre_name_split():
    # "texgyreheroscn" ist die Dateibasis, "TeXGyreHerosCondensed-*" der
    # eingebettete Name. Vorher passte die Schmalschrift NIE auf ihre eigene
    # Deklaration -- sie kam nur durch, weil "texgyreheros" (die
    # Grundschrift) als Teilzeichenkette darin steckt.
    assert (sc._schriftbasis("texgyreheroscn")
            == sc._schriftbasis("OIEMYB+TeXGyreHerosCondensed-Regular"))
    assert (sc._schriftbasis("SwissTeXGroteskCondensed")
            == sc._schriftbasis("ZONZWQ+SwissTeXGroteskCond-Regular"))
    assert (sc._schriftbasis('"TeXGyreDejaVuMath-Regular/OT:script=math;'
                             'language=dflt;" at 9.5pt')
            == sc._schriftbasis("ABCDEF+TeXGyreDejaVuMath-Regular"))
    assert sc._schriftbasis("texgyreheros") != sc._schriftbasis("texgyreheroscn")


def test_logofonts_declaration_lets_a_foreign_logo_font_pass(tmp_path):
    r = build_doc(ROOT / "tests/fixtures/logofont.tex", tmp_path)
    assert r.returncode == 0, r.log[-3000:]
    assert r.sidecar["logofonts"] == "SwissTeX Grotesk", r.sidecar
    code, out = swisscheck(r.pdf)
    assert code == 0, out


def test_without_logofonts_the_same_document_fails_a16(tmp_path):
    r = build_doc(ROOT / "tests/fixtures/logofont.tex", tmp_path)
    assert r.returncode == 0, r.log[-3000:]
    side = tmp_path / "ohnelogofonts.swisscheck"
    side.write_text((tmp_path / "logofont.swisscheck").read_text()
                    .replace("logofonts=SwissTeX Grotesk", "logofonts="))
    code, out = swisscheck(r.pdf, "--params", str(side))
    assert code != 0, out
    a16 = next(z for z in out.splitlines() if z.strip().startswith("A16"))
    assert "FEHLER" in a16, out
    assert "SwissTeXGrotesk" in out, out


# --- B1: A17 Glossenlänge --------------------------------------------------

def test_a17_flags_a_running_text_gloss(tmp_path):
    fx = tmp_path / "langglosse.tex"
    fx.write_text(r"""\documentclass{swisstex}
\begin{document}
\section{Abschnitt}
\marg{Diese Randglosse ist bewusst als laufender Text geschrieben und
laeuft darum ueber deutlich mehr als sechs Zeilen in der schmalen
Glossenzone, was genau der Verstoss gegen I3 ist, den A17 messen soll,
und zwar unabhaengig davon, mit welchem Befehl der Satz dort landet.}
Grundtext auf dem Raster mit genug Woertern fuer eine volle Zeile und
noch etwas mehr, damit die Glosse ueberhaupt Platz zum Laufen hat.
\end{document}""")
    r = build_doc(fx, tmp_path)
    assert r.returncode == 0, r.log[-2000:]
    code, out = swisscheck(r.pdf)
    assert code != 0, out
    a17 = next(z for z in out.splitlines() if z.strip().startswith("A17"))
    assert "FEHLER" in a17, out
    assert "Glossenblock" in out, out


def test_a17_accepts_a_label_length_gloss(tmp_path):
    r = build_doc(ROOT / "tests/fixtures/plain.tex", tmp_path)
    assert r.returncode == 0, r.log[-2000:]
    code, out = swisscheck(r.pdf)
    assert code == 0, out


def test_a17_is_not_vacuous_on_the_manual(tmp_path):
    # Nichtleerheit: das Handbuch ist das glossenreichste Dokument des
    # Projekts; A17 muss dort viele Blöcke tatsächlich vermessen haben.
    r = build_doc(ROOT / "swisstex-manual.tex", tmp_path, runs=2)
    assert r.returncode == 0, r.log[-3000:]
    assert_clean_refs(r.log, context="swisstex-manual.tex")
    code, out = swisscheck(r.pdf)
    assert code == 0, out
    a17 = next(z for z in out.splitlines() if z.strip().startswith("A17"))
    assert "ok" in a17, a17
    geprueft = int(re.search(r"\((\d+) geprüft\)", a17).group(1))
    assert geprueft >= 15, a17
