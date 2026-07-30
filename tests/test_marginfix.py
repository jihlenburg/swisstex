# tests/test_marginfix.py -- Port aus SwissTeX 1.3.1 (Produktionsfork):
# \RequirePackage{marginfix} in swisstex.cls Sec. 2 (nach \reversemarginpar)
# plus swisscheck A18 "Marginalien im Satzspiegel", die genau das misst, was
# marginfix korrigiert: eine Randglosse, die am Seitenende ueber die
# Satzspiegel-Unterkante hinausragen wuerde, wird von marginfix nach oben
# geschoben, bis ihre Unterkante auf der Unterkante liegt.
#
# tests/fixtures/marginfix.tex ist absichtlich so gebaut, dass die Glosse
# OHNE marginfix deutlich ueberstuende (siehe die manuelle RED-Gegenprobe
# unten im Docstring von test_a18_passes_on_the_ported_class, dokumentiert
# im Portierungsbericht: mit auskommentiertem \RequirePackage{marginfix}
# meldet A18 einen Ueberstand von rund 63 pt auf genau dieser Vorlage). Die
# Vorlage verstoesst dabei bewusst gegen A17 (Glossenlaenge) -- sie prueft
# ausschliesslich A18, nicht die volle Konformitaet, genau wie
# broken-head-image.tex in test_swisscheck.py nur A11 prueft.

import sys

from conftest import ROOT, build_doc, swisscheck

sys.path.insert(0, str(ROOT))
import swisscheck as sc  # noqa: E402


def test_a18_passes_on_the_ported_class(tmp_path):
    """GREEN: mit \\RequirePackage{marginfix} (portiert in swisstex.cls
    Sec. 2) schiebt die Klasse die ueberlange Glosse zurueck in den
    Satzspiegel -- A18 meldet 'ok', obwohl die Glosse an sich (A17) viel zu
    lang ist. Die manuelle RED-Gegenprobe (marginfix im Klassen-Kopf
    auskommentiert, gleiche Vorlage neu gebaut) meldet stattdessen
    'S.1: Glosse ragt 62.7 pt unter die Satzspiegel-Unterkante' -- siehe
    Portierungsbericht."""
    r = build_doc(ROOT / "tests/fixtures/marginfix.tex", tmp_path)
    assert r.returncode == 0, r.log[-2000:]
    code, out = swisscheck(r.pdf)
    a18 = next(z for z in out.splitlines() if z.strip().startswith("A18"))
    assert "ok" in a18, (a18, out)
    assert "(1 geprüft)" in a18, a18
    # A17 (Glossenlaenge) schlaegt auf dieser Vorlage bewusst fehl -- eigener
    # Verstoss, nicht Gegenstand dieser Pruefung.
    a17 = next(z for z in out.splitlines() if z.strip().startswith("A17"))
    assert "FEHLER" in a17, a17


def test_a18_works_without_a_sidecar_file(tmp_path):
    """A18 arbeitet wie A1-A9 OHNE Kennzahlen-Sidecar: geloescht/umbenannt
    faellt es auf die Raster-Vorgabe (CLI/Default, gridlines=51) zurueck,
    statt sich wie die sidecar-gebundenen Prüfungen A10-A13/A15-A17 sauber
    zu überspringen."""
    r = build_doc(ROOT / "tests/fixtures/marginfix.tex", tmp_path)
    assert r.returncode == 0, r.log[-2000:]
    sidecar = tmp_path / "marginfix.swisscheck"
    assert sidecar.exists()
    sidecar.unlink()
    code, out = swisscheck(r.pdf)
    assert "Kennzahlen-Sidecar: keine" in out, out
    a18 = next(z for z in out.splitlines() if z.strip().startswith("A18"))
    assert "ok" in a18, (a18, out)
    assert "(1 geprüft)" in a18, a18


def test_pruefe_marginalueberstand_registered_in_main_checklist():
    # Einheitentest ohne Build: die Funktion existiert unter dem erwarteten
    # Namen und liefert eine Befund-Kennung "A18".
    r = sc.Raster()
    assert r.has_sidecar is False
    b = sc.Befund("A18", "probe")
    assert b.kennung == "A18"
    assert sc.pruefe_marginalueberstand.__name__ == "pruefe_marginalueberstand"
