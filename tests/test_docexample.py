# tests/test_docexample.py -- C5: das Handbuch-Beispiel wird wirklich übersetzt.
#
# Das Handbuch zeigt in Abschnitt "Beispiel: die Referenzidentität acme" einen
# Auszug aus swissidentity-acme.sty. Der Auszug war bis zu dieser Änderung
# nicht übersetzbar: die RGB-Tripel standen ohne Klammern
# (accent=200,16,46 statt accent={200,16,46}), womit keyval die "16" und die
# "46" als eigene, unbekannte Schlüssel gelesen hätte. Ein Leser, der das
# Beispiel abtippt, wäre gegen einen Fehler gelaufen, den das Handbuch selbst
# erzeugt hat.
#
# Dieser Test schliesst die Lücke maschinell: er liest den markierten Block
# aus swisstex-manual.tex, übersetzt die Handbuch-Schreibweise (\code{...} mit
# escaptem \textbackslash/\{/\}) zurück in echtes LaTeX und übersetzt das
# Ergebnis als Präambel eines Wegwerf-Dokuments. Alle Setzer des Auszugs sind
# aus der Präambel heraus genauso aufrufbar wie aus einer Identitätsdatei
# (swisstex.cls Abschnitt 2b: sie wirken global, der Aufrufort ist
# gleichgültig) -- der Auszug wird also genau so ausgeführt, wie er dasteht.

import re

from conftest import build_doc, ROOT

MANUAL = ROOT / "swisstex-manual.tex"
BLOCK = re.compile(r"% BEGIN acme-excerpt[^\n]*\n(.*?)% END acme-excerpt", re.S)


def extract_excerpt(quelle: str) -> str:
    """Handbuch-Schreibweise -> echtes LaTeX.

    Je Zeile: führendes ``\\code{`` und schliessende ``}`` weg, das
    Zeilenende-``\\\\`` weg, ``\\hspace{1.5em}`` (reine Satzeinrückung) weg,
    dann die drei Escapes zurücksetzen. Zeilen werden mit Zeilenumbruch
    verbunden -- ein über zwei Handbuchzeilen umbrochener Aufruf setzt sich
    dabei von selbst wieder zusammen.
    """
    m = BLOCK.search(quelle)
    assert m, "Markierung 'BEGIN acme-excerpt' im Handbuch nicht gefunden"
    zeilen = []
    for roh in m.group(1).splitlines():
        roh = roh.strip()
        if not roh or roh.startswith(("\\begin{", "\\end{", "%")):
            continue
        if roh.endswith("\\\\"):
            roh = roh[:-2].rstrip()
        assert roh.startswith("\\code{") and roh.endswith("}"), roh
        roh = roh[len("\\code{"):-1]
        roh = roh.replace("\\hspace{1.5em}", "")
        roh = roh.replace("\\textbackslash ", "\\").replace("\\textbackslash", "\\")
        roh = roh.replace("\\{", "{").replace("\\}", "}")
        zeilen.append(roh)
    assert zeilen, "Auszug ist leer"
    return "\n".join(zeilen)


def test_excerpt_extraction_recovers_real_latex():
    text = extract_excerpt(MANUAL.read_text(encoding="utf-8"))
    # Die Stelle, an der das Beispiel falsch war: das RGB-Tripel MUSS
    # geklammert sein, sonst zerlegt keyval es in drei Schlüssel.
    assert "accent={200,16,46}" in text, text
    assert "\\swissidentitymeta{" in text, text
    assert "\\renewfontfamily\\condensed{" in text, text
    assert "\\textbackslash" not in text, text


def test_manual_acme_excerpt_compiles(tmp_path):
    text = extract_excerpt(MANUAL.read_text(encoding="utf-8"))
    fx = tmp_path / "docexample.tex"
    fx.write_text("\\documentclass{swisstex}\n"
                  + text
                  + "\n\\swissmeta{docid=TR-2026-014, version=1.2,"
                    " classification=internal}\n"
                    "\\begin{document}\n"
                    "\\swisscover*{kicker=Probe, title=Auszug}\n"
                    "\\section{Abschnitt}\n"
                    "Grundtext auf dem Raster mit genug Woertern fuer eine\n"
                    "volle Zeile Flattersatz im Basisraster der Klasse.\n"
                    "\\colophon{Aus dem Handbuchauszug gebaut.}\n"
                    "\\end{document}\n",
                  encoding="utf-8")
    r = build_doc(fx, tmp_path)
    assert r.returncode == 0, r.log[-4000:]
    assert "undefined" not in r.log.lower() or "Reference" not in r.log, r.log[-4000:]
    # Die Farbrolle des Auszugs muss auch wirklich angekommen sein.
    assert r.sidecar["accent"] == "200,16,46", r.sidecar
    assert r.sidecar["mainfamily"] == "SwissTeXGrotesk", r.sidecar
