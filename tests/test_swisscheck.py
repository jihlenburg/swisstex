# tests/test_swisscheck.py -- Task 9: Kennzahlen-Sidecar + swisscheck A10-A13/A15/A16.
#
# Drei Tests nach dem Brief (Schritt 1), plus einige direkte Einheitentests
# für die Parser-/from_sidecar-Logik in swisscheck.py selbst (kein Build
# nötig, schnell, deckt Formatfehler ab, die ein reiner PDF-Roundtrip nicht
# unbedingt zeigen würde).

import sys
from pathlib import Path

import pytest

from conftest import build_doc, swisscheck, ROOT

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
    for kennung in ("A10", "A11", "A12", "A13", "A15", "A16"):
        zeile = next((z for z in out.splitlines() if z.strip().startswith(kennung)), None)
        assert zeile is not None, f"{kennung} fehlt in der Ausgabe:\n{out}"
        assert "ok" in zeile, f"{kennung} nicht 'ok':\n{zeile}\n\nVolle Ausgabe:\n{out}"
    # A12 (Umschlag) wird über acme-demos eigenen Umschlag exercisiert, A10
    # (Fusszeile) über dessen klassifizierte Fusszeile -- beide also mit
    # geprüft > 0, nicht nur vacuously "ok" durch 0 geprüfte Fälle.
    a10 = next(z for z in out.splitlines() if z.strip().startswith("A10"))
    a12 = next(z for z in out.splitlines() if z.strip().startswith("A12"))
    assert "(0 geprüft)" not in a10, a10
    assert "(0 geprüft)" not in a12, a12


def test_manual_and_demo_sidecar_checks_all_ok(tmp_path):
    # Die beiden anderen Referenzdokumente (kein Identity-Pfad) -- derselbe
    # Vorgabe-Anbieter wie plain.tex, aber echte mehrseitige Inhalte mit
    # Kolumnentiteln, Randglossen, Tabellen, einem Umschlag (Manual) bzw.
    # einer Titelblock-Seite ohne Umschlag (Demo).
    for name in ("swisstex-manual.tex", "swisstex-demo.tex"):
        r = build_doc(ROOT / name, tmp_path, runs=2)
        assert r.returncode == 0, (name, r.log[-3000:])
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
               sc.pruefe_schriftinventar):
        befund = fn(pdf=None, r=r)
        assert befund.geprueft == 0, befund.kennung
        assert befund.bestanden, befund.kennung
        assert "übersprungen" in befund.titel, befund.kennung
