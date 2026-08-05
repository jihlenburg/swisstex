#!/usr/bin/env python3
"""sprachcheck — Lesbarkeitsprüfung für SwissTeX-Dokumente.

Herkunft: SwissTeX 1.3.1 (Produktionsfork), unverändert übernommen. S6
(Marginalien höchstens 22 Wörter) ergänzt swisscheck A17 (Glossenlänge):
A17 misst am gesetzten PDF, ob ein Glossenblock über sechs Zeilen läuft,
S6 misst dieselbe Anforderung an der Quelle, in Wörtern statt Zeilen.

Neun Prüfungen S1 bis S9, analog zu den Typografieprüfungen A1 bis A8 in
swisscheck. Gemessen wird der Fliesstext; Tabellen, Formeln, Marginalien und
Codeblöcke sind ausgenommen (Marginalien werden separat mit S6 geprüft).

Die Schwellen sind auf technische Fachprosa ausgelegt, nicht auf leichte
Sprache: Ein LIX um 55 ist für Fachliteratur normal und kein Mangel. Hart
sind S1, S7 und S8; alles andere warnt.

    S1  Kein Satz über 40 Wörter                          (hart)
    S2  Höchstens 8 % der Sätze über 30 Wörter            (weich)
    S3  LIX im Band 45 bis 62                             (weich)
    S4  Nominalisierungen unter 8 je 100 Wörter           (weich)
    S5  Satzlängen-Streuung mindestens 6 (Rhythmus)       (weich)
    S6  Marginalien höchstens 22 Wörter                   (weich)
    S7  Keine Geviertstriche (— oder ---)                 (hart)
    S8  Keine Semikola im Fliesstext                      (hart)
    S9  Höchstens 3 Klammerpaare je 1000 Wörter           (weich)

Seit 2026-08-05 zusätzlich --lang en: das Profil Swiss Technical English
(Definition im KIVAT-Repo, skill/swiss-technical-english/SKILL.md). Hart
sind E1 (35 Wörter), E4 (Semikola) und E5 (Em-Dashes), dazu warnende
Messungen für Patter und Hedges (E3), Passivanteil (E6, grobe Heuristik,
wird am ersten Übersetzungskorpus geeicht), schwache Satzauftakte (E9)
und britische Schreibformen (E10). LIX-Band englisch 40 bis 55.
"""
import re, sys, statistics, argparse

PATTER = re.compile(
    r"\b(delve|leverag\w*|seamless\w*|cutting-edge|holistic|rather|quite"
    r"|fairly|arguably|essentially)\b"
    r"|it is important to note|in order to|robust framework"
    r"|state-of-the-art", re.I)
OPENER = re.compile(r"^(there (is|are|was|were)|it (is|was))\b", re.I)
UKFORM = re.compile(
    r"\b\w+isations?\b|\bcolour|\bbehaviour|\bneighbour"
    r"|\banalys(e|ed|ing)\b|\boptimis(e|ed|ing)\b", re.I)
PASSIV = re.compile(
    r"\b(is|are|was|were|been|being|be)\s+"
    r"(\w+ed|born|built|done|found|given|held|kept|known|left|made"
    r"|seen|set|shown|taken|used)\b", re.I)

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
    # Sternform: keyval-Werte mit geschachtelten Klammern, der Aufruf endet
    # an der Leerzeile -- sonst zaehlen kicker/title/foot als Fliesstext
    # (aufgefallen an der ersten englischen Ausgabe, deren foot ohne
    # Satzpunkte einen 41-Wort-Pseudosatz bildete).
    t = re.sub(r"\\swisscover\*\{.*?\n\n", "", t, flags=re.S)
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

def pruefe(pfad, verbose=False, lang="de"):
    saetze, marg = extrahiere(pfad)
    woerter = [w.strip(".,;:—()»«\"") for s in saetze for w in s.split()]
    woerter = [w for w in woerter if w]
    sl = [len(s.split()) for s in saetze]
    lange_woerter = sum(1 for w in woerter if len(w) > 6)
    lix = statistics.mean(sl) + 100 * lange_woerter / len(woerter)
    streuung = statistics.pstdev(sl)
    ml = [len(m.split()) for m in marg] or [0]
    semikola = fliesstext_roh(pfad).count(";")
    klammern = fliesstext_roh(pfad).count("(")

    if lang == "de":
        nomi = sum(1 for w in woerter
                   if re.search(r"(ung|heit|keit|tion|ismus|ität)(en)?$", w)
                   and len(w) > 6)
        nomiq = 100 * nomi / len(woerter)
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
            ("S8", "Keine Semikola im Fliesstext", semikola == 0,
             f"{semikola} gefunden", True),
            ("S9", "Klammern bis 3 je 1000 Wörter",
             1000 * klammern / len(woerter) <= 3,
             f"{klammern} Paare, {1000*klammern/len(woerter):.1f} je 1000", False),
        ]
    else:
        text_roh = fliesstext_roh(pfad)
        nomi = sum(1 for w in woerter
                   if re.search(r"(tion|ment|ance|ence|ity|ness)s?$", w)
                   and len(w) > 6)
        nomiq = 100 * nomi / len(woerter)
        patter = len(PATTER.findall(text_roh))
        opener = sum(1 for s in saetze if OPENER.match(s))
        ukform = len(UKFORM.findall(text_roh))
        passiv = 100 * sum(1 for s in saetze if PASSIV.search(s)) / len(saetze)
        ergebnisse = [
            ("E1", "No sentence over 35 words", max(sl) <= 35,
             f"longest {max(sl)} words", True),
            ("E2", "Sentences over 30 words under 8 %",
             100 * sum(1 for x in sl if x > 30) / len(sl) <= 8,
             f"{100*sum(1 for x in sl if x>30)/len(sl):.0f} % "
             f"({sum(1 for x in sl if x>30)} of {len(sl)})", False),
            ("E3", "No patter or hedges", patter == 0,
             f"{patter} found", False),
            ("E4", "No semicolons in running text", semikola == 0,
             f"{semikola} found", True),
            ("E5", "No em dashes", zaehle_geviert(pfad) == 0,
             f"{zaehle_geviert(pfad)} found", True),
            ("E6", "Passive share under 25 %", passiv <= 25,
             f"{passiv:.0f} % of sentences (rough heuristic)", False),
            ("E9", "No weak openers (there is, it is)", opener == 0,
             f"{opener} found", False),
            ("E10", "US spelling", ukform == 0,
             f"{ukform} UK forms found", False),
            ("LIX", "Readability band 40 to 55", 40 <= lix <= 55,
             f"LIX {lix:.0f}", False),
            ("NOM", "Nominal density under 8/100", nomiq < 8,
             f"{nomiq:.1f} per 100 words", False),
            ("RHY", "Sentence-length spread over 6", streuung > 6,
             f"spread {streuung:.1f}, median {statistics.median(sl):.0f}", False),
            ("MRG", "Marginal notes up to 22 words", max(ml) <= 22,
             f"longest {max(ml)} words", False),
            ("PAR", "Parentheses up to 3 per 1000",
             1000 * klammern / len(woerter) <= 3,
             f"{klammern} pairs, {1000*klammern/len(woerter):.1f} per 1000", False),
        ]

    hart_ok = True
    profil = "" if lang == "de" else f" ({lang})"
    print(f"Sprachprüfung{profil}: {len(saetze)} Sätze, {len(woerter)} Wörter\n")
    for kuerzel, name, ok, wert, hart in ergebnisse:
        status = "ok  " if ok else ("FEHLER" if hart else "warnt")
        print(f"  {kuerzel:<4s} {status:6s} {name:36s} {wert}")
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
    ap.add_argument("--lang", choices=("de", "en"), default="de")
    a = ap.parse_args()
    sys.exit(0 if pruefe(a.tex, a.verbose, a.lang) else 1)
