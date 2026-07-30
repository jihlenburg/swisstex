#!/usr/bin/env python3
"""sprachcheck — Lesbarkeitsprüfung für SwissTeX-Dokumente.

Herkunft: SwissTeX 1.3.1 (Produktionsfork), unverändert übernommen. S6
(Marginalien höchstens 22 Wörter) ergänzt swisscheck A17 (Glossenlänge):
A17 misst am gesetzten PDF, ob ein Glossenblock über sechs Zeilen läuft,
S6 misst dieselbe Anforderung an der Quelle, in Wörtern statt Zeilen.

Sechs Prüfungen S1 bis S6, analog zu den Typografieprüfungen A1 bis A8 in
swisscheck. Gemessen wird der Fliesstext; Tabellen, Formeln, Marginalien und
Codeblöcke sind ausgenommen (Marginalien werden separat mit S6 geprüft).

Die Schwellen sind auf technische Fachprosa ausgelegt, nicht auf leichte
Sprache: Ein LIX um 55 ist für Fachliteratur normal und kein Mangel. Hart ist
nur S1; alles andere warnt.

    S1  Kein Satz über 40 Wörter                          (hart)
    S2  Höchstens 8 % der Sätze über 30 Wörter            (weich)
    S3  LIX im Band 45 bis 62                             (weich)
    S4  Nominalisierungen unter 8 je 100 Wörter           (weich)
    S5  Satzlängen-Streuung mindestens 6 (Rhythmus)       (weich)
    S6  Marginalien höchstens 22 Wörter                   (weich)
    S7  Keine Geviertstriche (— oder ---)                 (hart)
    S8  Keine Semikola im Fliesstext                      (hart)
    S9  Höchstens 3 Klammerpaare je 1000 Wörter           (weich)
"""
import re, sys, statistics, argparse

def zaehle_geviert(pfad):
    t = open(pfad).read()
    t = t[t.index("\\begin{document}"):]
    t = "\n".join(l for l in t.split("\n") if not l.strip().startswith("%"))
    return t.count("—") + len(re.findall(r"(?<!-)---(?!-)", t))

def fliesstext_roh(pfad):
    t = open(pfad).read()
    t = t[t.index("\\begin{document}"):]
    t = "\n".join(l for l in t.split("\n") if not l.strip().startswith("%"))
    for env in ("swisstable", "tabularx", "gridblock", "tikzpicture",
                "swissfigure", "lead", "verbatim"):
        t = re.sub(r"\\begin\{" + env + r"\}.*?\\end\{" + env + r"\}", "",
                   t, flags=re.S)
    t = re.sub(r"\\colophon\{.*?\}", lambda m: m.group(0), t)  # Kolophon zählt mit
    t = re.sub(r"\$[^$]*\$", " F ", t)
    return t

def extrahiere(pfad):
    t = open(pfad).read()
    t = t[t.index("\\begin{document}"):]
    t = "\n".join(l for l in t.split("\n") if not l.strip().startswith("%"))
    for env in ("swisstable", "tabularx", "gridblock", "tikzpicture",
                "swissfigure", "lead", "verbatim"):
        t = re.sub(r"\\begin\{" + env + r"\}.*?\\end\{" + env + r"\}", "",
                   t, flags=re.S)
    marg = re.findall(r"\\marg\{([^{}]*)\}", t)
    t = re.sub(r"\\marg\{[^{}]*\}", "", t)
    t = re.sub(r"\\(sub)?section\*?\{[^}]*\}", "", t)
    t = re.sub(r"\\colophon\{.*?\}", "", t, flags=re.S)
    t = re.sub(r"\\swisscover(\{.*?\}\s*){4}", "", t, flags=re.S)
    t = re.sub(r"\$[^$]*\$", " FORMEL ", t)
    t = re.sub(r"\\[a-zA-Z]+\{([^{}]*)\}", r"\1", t)
    t = re.sub(r"\\[a-zA-Z]+", "", t)
    t = re.sub(r"[{}~]", " ", t)
    absaetze = [" ".join(a.split()) for a in t.split("\n\n") if len(a.split()) > 15]
    saetze = []
    for a in absaetze:
        for s in re.split(r"(?<=[.!?;])\s+", a):
            if len(s.split()) >= 4:
                saetze.append(s.strip())
    return saetze, marg

def pruefe(pfad, verbose=False):
    saetze, marg = extrahiere(pfad)
    woerter = [w.strip(".,;:—()»«\"") for s in saetze for w in s.split()]
    woerter = [w for w in woerter if w]
    sl = [len(s.split()) for s in saetze]
    lange_woerter = sum(1 for w in woerter if len(w) > 6)
    lix = statistics.mean(sl) + 100 * lange_woerter / len(woerter)
    nomi = sum(1 for w in woerter
               if re.search(r"(ung|heit|keit|tion|ismus|ität)(en)?$", w)
               and len(w) > 6)
    nomiq = 100 * nomi / len(woerter)
    streuung = statistics.pstdev(sl)
    ml = [len(m.split()) for m in marg] or [0]

    ergebnisse = [
        ("S1", "Kein Satz über 40 Wörter", max(sl) <= 40,
         f"längster {max(sl)} Wörter", True),
        ("S2", "Sätze über 30 Wörter unter 8 %",
         100 * sum(1 for x in sl if x > 30) / len(sl) <= 8,
         f"{100*sum(1 for x in sl if x>30)/len(sl):.0f} % "
         f"({sum(1 for x in sl if x>30)} von {len(sl)})", False),
        ("S3", "LIX zwischen 45 und 62", 45 <= lix <= 62,
         f"LIX {lix:.0f}", False),
        ("S4", "Nominalisierungen unter 8/100", nomiq < 8,
         f"{nomiq:.1f} je 100 Wörter", False),
        ("S5", "Satzlängen-Streuung über 6", streuung > 6,
         f"Streuung {streuung:.1f}, Median {statistics.median(sl):.0f}", False),
        ("S6", "Marginalien bis 22 Wörter", max(ml) <= 22,
         f"längste {max(ml)} Wörter", False),
        ("S7", "Keine Geviertstriche", zaehle_geviert(pfad) == 0,
         f"{zaehle_geviert(pfad)} gefunden", True),
        ("S8", "Keine Semikola im Fliesstext",
         fliesstext_roh(pfad).count(";") == 0,
         f"{fliesstext_roh(pfad).count(';')} gefunden", True),
        ("S9", "Klammern bis 3 je 1000 Wörter",
         1000 * fliesstext_roh(pfad).count("(") / len(woerter) <= 3,
         f"{fliesstext_roh(pfad).count('(')} Paare, "
         f"{1000*fliesstext_roh(pfad).count('(')/len(woerter):.1f} je 1000", False),
    ]
    hart_ok = True
    print(f"Sprachprüfung: {len(saetze)} Sätze, {len(woerter)} Wörter\n")
    for kuerzel, name, ok, wert, hart in ergebnisse:
        status = "ok  " if ok else ("FEHLER" if hart else "warnt")
        print(f"  {kuerzel}  {status:6s} {name:36s} {wert}")
        if hart and not ok:
            hart_ok = False
    if verbose:
        print("\n  Längste Sätze:")
        for s in sorted(saetze, key=lambda x: -len(x.split()))[:5]:
            print(f"    [{len(s.split()):3d}] {s[:96]}…")
    print("\n" + ("bestanden" if hart_ok else "nicht bestanden"))
    return hart_ok

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("tex")
    ap.add_argument("-v", "--verbose", action="store_true")
    a = ap.parse_args()
    sys.exit(0 if pruefe(a.tex, a.verbose) else 1)
