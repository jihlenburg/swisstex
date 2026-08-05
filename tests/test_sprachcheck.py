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


# --- Englisches Profil: --lang en, Swiss Technical English -----------------
# E1 (35 Woerter), E4 (Semikola), E5 (Em-Dashes) hart; E3 (Patter),
# E9 (schwache Auftakte) u.a. warnen. Profil-Definition:
# KIVAT-Repo, skill/swiss-technical-english/SKILL.md.

DIRTY_EN = r"""\documentclass{swisstex}
\begin{document}
\section{Probe}

There is a pipeline that leverages the framework in order to deliver the prediction of the drift of the athermalized system over the full temperature range of the automotive specification for every field angle of the modeled lens assembly. The mount compensates; the drift shrinks --- almost fully gone.

The second paragraph carries enough plain words to count as prose for
the extraction step of the checker and it stays deliberately short and
calm so only the first paragraph violates the hard rules.
\end{document}
"""

CLEAN_EN = r"""\documentclass{swisstex}
\begin{document}
% Sternform-Umschlag mit punktlosem foot: darf nicht als Fliesstext
% zaehlen (Extraktor-Regression der ersten englischen Ausgabe).
\swisscover*{kicker={Working Paper}, title={Probe},
  subtitle={A subtitle without any sentence marks at all},
  foot={AMX13 GmbH Luebs Germany with many plain words and no period
   marks anywhere in this deliberately long footer line of the cover},
  glyph={2}}
\section{Probe}

The pipeline predicts the drift of the athermalized system. The chain
is built from open tools and covers the span from material scatter to
image evaluation. Three mechanisms detune the compensation. The mount
holds the sensor, and the barrel carries the lenses through the range.

A second paragraph keeps the rhythm alive with a slightly longer
sentence that still stays well under the limit, followed by a short
one. The paragraph ends here with a calm closing statement.
\end{document}
"""


def _run_lang(tex, lang):
    r = subprocess.run([str(PY), str(ROOT / "sprachcheck.py"), str(tex),
                        "--lang", lang],
                       cwd=ROOT, capture_output=True, text=True, timeout=60)
    return r.returncode, r.stdout + r.stderr


def test_english_profile_flags_hard_violations(tmp_path):
    tex = tmp_path / "dirty-en.tex"
    tex.write_text(DIRTY_EN)
    code, out = _run_lang(tex, "en")
    assert code != 0, out
    for kuerzel in ("E1", "E4", "E5"):
        zeile = next(z for z in out.splitlines()
                     if z.strip().startswith(kuerzel + " "))
        assert "FEHLER" in zeile, out
    # Patter (leverages, in order to) und schwacher Auftakt (There is)
    # werden gefunden und warnen:
    e3 = next(z for z in out.splitlines() if z.strip().startswith("E3 "))
    e9 = next(z for z in out.splitlines() if z.strip().startswith("E9 "))
    assert "warnt" in e3 and "warnt" in e9, out


def test_english_profile_clean_passes(tmp_path):
    tex = tmp_path / "clean-en.tex"
    tex.write_text(CLEAN_EN)
    code, out = _run_lang(tex, "en")
    assert code == 0, out
    assert "bestanden" in out.splitlines()[-1], out
