# tests/test_sprachcheck.py -- sprachcheck.py (Port aus SwissTeX 1.3.1,
# siehe Kopfkommentar dort) gegen die beiden Referenzdokumente ohne
# Produktionsinhalt: acme-demo.tex und swisstex-manual.tex. swisstex-demo.tex
# bleibt hier aussen vor -- es ist eine kurze Rastervorfuehrung ohne echten
# Fliesstext (siehe CLAUDE.md), zu kurz für eine sinnvolle Lesbarkeitsprüfung.
#
# Nur die drei harten Prüfungen (S1 kein Satz über 40 Wörter, S7 keine
# Geviertstriche, S8 keine Semikola im Fliesstext) müssen bestehen -- die
# weichen (S2..S6, S9) dürfen warnen, das ist beabsichtigt (siehe
# sprachcheck.py Kopfkommentar: "Hart ist nur S1, S7, S8; alles andere
# warnt", auf technische Fachprosa ausgelegte Schwellen). Beide Dokumente
# scheiterten beim ersten Lauf an echten Inhaltsverstössen (lange Sätze,
# Semikola in laufendem Text) -- das war ein echter Befund, kein
# Werkzeugfehler, und wurde im Dokumenttext minimal behoben (Sätze geteilt,
# Semikola durch Punkte ersetzt), nicht durch Aufweichen der Schwellen.

import subprocess
import sys

import pytest

from conftest import ROOT

PY = ROOT / "fonts/.venv/bin/python"
HART = ("S1", "S7", "S8")


def _run(tex):
    r = subprocess.run([str(PY), str(ROOT / "sprachcheck.py"), str(tex), "-v"],
                        cwd=ROOT, capture_output=True, text=True, timeout=60)
    return r.returncode, r.stdout + r.stderr


@pytest.mark.parametrize("tex", ["acme-demo.tex", "swisstex-manual.tex"])
def test_hard_checks_pass(tex):
    code, out = _run(tex)
    assert code == 0, out
    assert "bestanden" in out.splitlines()[-1], out
    for kuerzel in HART:
        zeile = next(z for z in out.splitlines() if z.strip().startswith(f"{kuerzel}  "))
        assert "FEHLER" not in zeile, (tex, zeile, out)
        assert "ok" in zeile, (tex, zeile, out)


@pytest.mark.parametrize("tex", ["acme-demo.tex", "swisstex-manual.tex"])
def test_exit_code_matches_hard_check_state(tex):
    # sys.exit(0 if pruefe(...) else 1) -- Rueckgabewert und Konsolentext
    # muessen konsistent sein.
    code, out = _run(tex)
    letzte = out.strip().splitlines()[-1]
    if code == 0:
        assert letzte == "bestanden", out
    else:
        assert letzte == "nicht bestanden", out


def test_swisstex_manual_is_not_vacuous():
    # Nichtleerheit: das Handbuch ist das textreichste Dokument des Projekts.
    code, out = _run("swisstex-manual.tex")
    kopf = out.splitlines()[0]
    assert "Sprachprüfung:" in kopf, out
    saetze = int(kopf.split(":")[1].split("Sätze")[0].strip())
    assert saetze > 100, kopf
