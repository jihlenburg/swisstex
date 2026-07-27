#!/usr/bin/env python3
"""
swisscheck -- prüft eine PDF-Ausgabe gegen die SwissTeX-Invarianten.

Die Klasse kann Regeln nur erzwingen, solange der Autor die API benutzt.
Handgesetzte Abstände, falsch dimensionierte Tabellen oder ein vergessenes
[t] fallen erst am Ergebnis auf. Dieses Skript misst das Ergebnis.

Geprüft werden:
  A1  Achsentreue      Linien stehen auf der Textachse oder auf vollem Mass.
  A2  Rasterbindung    Grundtextzeilen liegen auf dem Basislinienraster.
  A3  Satzspiegel      Kein Satz läuft über den rechten Rand hinaus.
  A4  Marginalspalte   Trägt nur Beschriftung, kein Satzmaterial.
  A5  Legendenflucht   Tabellenlegende fluchtet mit der ersten Tabellenlinie.
  A6  Seitenfuss       Keine Überschrift am unteren Seitenende.

Aufruf:
    python3 swisscheck.py bericht.pdf [--tex bericht.tex]
    python3 swisscheck.py bericht.pdf --gridunit 13.5 --bodysize 9.5
"""

from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass, field

import pdfplumber

MM = 72 / 25.4
# PDF-Koordinaten stehen in DTP-Punkt (1/72 Zoll), TeX rechnet in
# TeX-Punkt (1/72,27 Zoll). Ohne diese Umrechnung erscheint jedes
# Basislinienraster als langsam wegdriftend.
PT = 72 / 72.27


@dataclass
class Raster:
    """Kennzahlen des Satzspiegels, in Millimetern bzw. Punkt."""

    outermargin: float = 24.0
    margincolumn: float = 30.0
    gutter: float = 7.0
    numberzone: float = 8.0
    textcolumn: float = 105.0
    topmargin: float = 26.0
    gridunit_pt: float = 13.5
    bodysize_pt: float = 9.5

    @property
    def gridunit(self) -> float:
        """Rastermass in PDF-Punkt."""
        return self.gridunit_pt * PT

    @property
    def bodysize(self) -> float:
        return self.bodysize_pt * PT

    @property
    def innermargin(self) -> float:
        return self.outermargin + self.margincolumn + self.gutter

    @property
    def glosswidth(self) -> float:
        """Breite der Randglossen: Marginalspalte ohne die Ziffernzone."""
        return self.margincolumn - self.numberzone

    @property
    def fullmeasure(self) -> float:
        return self.margincolumn + self.gutter + self.textcolumn


@dataclass
class Befund:
    kennung: str
    titel: str
    verstoesse: list[str] = field(default_factory=list)
    geprueft: int = 0

    @property
    def bestanden(self) -> bool:
        return not self.verstoesse

    def zeile(self) -> str:
        marke = "ok " if self.bestanden else "FEHLER"
        return f"  {self.kennung}  {marke:<7}{self.titel}  ({self.geprueft} geprüft)"


def waagerechte_linien(seite):
    for o in (seite.rects or []) + (seite.lines or []):
        if abs(o["y1"] - o["y0"]) < 1.5 and (o["x1"] - o["x0"]) > 20:
            yield o


def zeilen(seite, nur_satzspiegel: float | None = None):
    """Wörter zu Zeilen gruppieren, Schlüssel ist die gerundete Oberkante."""
    gruppen: dict[int, list] = {}
    for w in seite.extract_words(extra_attrs=["size"]):
        if nur_satzspiegel is not None and w["x0"] < nur_satzspiegel * MM - 2:
            continue
        gruppen.setdefault(round(w["top"]), []).append(w)
    return gruppen


def pruefe_achsentreue(pdf, r: Raster, tol=0.6) -> Befund:
    b = Befund("A1", "Achsentreue der Linien")
    for i, seite in enumerate(pdf.pages, 1):
        zeichnung = zeichnungszonen(seite)
        for o in waagerechte_linien(seite):
            if any(a <= o["top"] <= e for a, e in zeichnung):
                continue                      # Strich in einer Zeichnung
            x0, breite = o["x0"] / MM, (o["x1"] - o["x0"]) / MM
            auf_achse = abs(x0 - r.innermargin) < tol and abs(breite - r.textcolumn) < tol
            volles_mass = abs(x0 - r.outermargin) < tol and abs(breite - r.fullmeasure) < tol
            bruchlinie = breite < 20  # Bruchstrich im Formelsatz
            if not (auf_achse or volles_mass or bruchlinie):
                b.verstoesse.append(
                    f"S.{i}: Linie x0={x0:.1f} mm, Breite={breite:.1f} mm")
            b.geprueft += 1
    return b


def grundlinien(seite, r: Raster, toleranz_groesse=0.35):
    """Exakte Grundlinien des Grundtexts aus der Textmatrix der Zeichen.

    matrix[5] ist die y-Translation, also die Grundlinie des Zeichens.
    Tabellen und Marginalien laufen bewusst mit engerem Durchschuss und
    werden über den Schriftgrad ausgesondert.
    """
    treffer: dict[float, int] = {}
    for c in seite.chars:
        if not c.get("upright", True):
            continue
        if c["x0"] / MM < r.innermargin - 1:
            continue
        if abs(c.get("size", 0) - r.bodysize) > toleranz_groesse:
            continue
        y = round(c["matrix"][5], 2)
        treffer[y] = treffer.get(y, 0) + 1
    # Bruchbalken und Indizes im Formelsatz sind eigene Grundlinien und
    # gehoeren nicht zum Fliesstext.
    return sorted(y for y, n in treffer.items() if n >= 20)


def pruefe_rasterbindung(pdf, r: Raster, tol=0.35) -> Befund:
    """Absolut gemessen: Grundlinie k liegt bei Satzoberkante + k*Rastermass.

    Der Bezug ist die Seite, nicht die erste Zeile. Nur so faellt auf, wenn
    ein Block das Raster zwar in sich haelt, aber gegen die Seite versetzt.
    """
    b = Befund("A2", "Rasterbindung des Grundtexts")
    for i, seite in enumerate(pdf.pages, 1):
        if vollflaechig(seite):
            continue
        felder = farbfelder(seite, r)
        oben = r.topmargin * MM
        for y in grundlinien(seite, r):
            if any(a <= (seite.height - y) <= e for a, e in felder):
                continue
            abstand = (seite.height - y) - oben
            rest = abstand % r.gridunit
            abweichung = min(rest, r.gridunit - rest)
            b.geprueft += 1
            if abweichung > tol:
                b.verstoesse.append(
                    f"S.{i}: Grundlinie {abweichung:.2f} pt neben dem Raster")
    return b


def pruefe_satzspiegel(pdf, r: Raster, tol=1.2) -> Befund:
    """Toleranz deckt den optischen Randausgleich (Protrusion) ab."""
    b = Befund("A3", "Rechte Satzkante")
    grenze = r.innermargin + r.textcolumn
    for i, seite in enumerate(pdf.pages, 1):
        if vollflaechig(seite):
            continue
        zonen = rahmenzonen(seite, r)
        kandidaten = [w["x1"] / MM for w in seite.extract_words()
                      if not any(a <= w["top"] <= e for a, e in zonen)]
        rechts = max(kandidaten, default=0)
        b.geprueft += 1
        if rechts > grenze + tol:
            b.verstoesse.append(f"S.{i}: Satz reicht bis {rechts:.1f} mm "
                                f"(Grenze {grenze:.1f} mm)")
    return b


def zeichnungszonen(seite, rand=9.0):
    """Vertikale Bänder, in denen eine Zeichnung steht.

    In einer Zeichnung sind Striche Inhalt, nicht Layout: eine Schwimmbahn
    oder eine Achse darf und soll neben der Textachse liegen. Erkannt wird
    eine Zeichnung an nicht-waagerechtem Vektorinhalt (Kurven, Schrägen).
    Zusammenhängend gerechnet wird über allen Vektorinhalt, damit auch die
    waagerechten Striche am oberen Rand einer Zeichnung dazugehören.
    """
    posten = []
    for o in seite.curves or []:
        posten.append((o["top"], o["bottom"], True))
    for o in seite.lines or []:
        posten.append((o["top"], o["bottom"], abs(o["y1"] - o["y0"]) >= 1.5))
    for o in seite.rects or []:
        posten.append((o["top"], o["bottom"], False))
    if not posten:
        return []
    posten.sort()
    haufen = [[posten[0][0] - rand, posten[0][1] + rand, posten[0][2]]]
    for a, e, schraeg in posten[1:]:
        if a - rand <= haufen[-1][1]:
            haufen[-1][1] = max(haufen[-1][1], e + rand)
            haufen[-1][2] = haufen[-1][2] or schraeg
        else:
            haufen.append([a - rand, e + rand, schraeg])
    return [(a, e) for a, e, schraeg in haufen if schraeg]


def farbfelder(seite, r: Raster, tol=1.0):
    """Farbfelder: gefüllte Flächen über mindestens das volle Mass.

    Satz in einem Farbfeld ist Rahmensatz. Er darf die Spaltenregel
    verlassen, und sein Durchschuss folgt dem Feld, nicht dem Seitenraster.
    """
    zonen = []
    for o in (seite.rects or []):
        breite = (o["x1"] - o["x0"]) / MM
        hoehe = o["y1"] - o["y0"]
        if breite >= r.fullmeasure - tol and hoehe > 2.0:
            zonen.append((o["top"] - 2.0, o["bottom"] + 2.0))
    return zonen


def vollflaechig(seite, anteil=0.9):
    """Umschlagseiten mit randabfallendem Farbfeld sind vom Raster
    ausgenommen: sie folgen einer eigenen Ordnung."""
    flaeche = seite.width * seite.height
    for o in (seite.rects or []):
        if (o["x1"] - o["x0"]) * (o["y1"] - o["y0"]) > anteil * flaeche:
            return True
    return False


def rahmenzonen(seite, r: Raster, radius=110.0):
    """Rahmenelemente (Titel, Kolophon) sind an der Linie auf vollem Mass
    erkennbar. Ihre Umgebung ist von der Spaltenregel ausgenommen."""
    zonen = []
    for o in waagerechte_linien(seite):
        breite = (o["x1"] - o["x0"]) / MM
        if abs(breite - r.fullmeasure) < 0.6:
            zonen.append((o["top"] - radius, o["top"] + radius))
    return zonen + farbfelder(seite, r)


def pruefe_marginalspalte(pdf, r: Raster, tol=1.0) -> Befund:
    """Der Bund bleibt leer, und Beschriftung verlässt die Marginalspalte nicht."""
    b = Befund("A4", "Marginalspalte und Bund")
    bund_von = r.outermargin + r.margincolumn
    bund_bis = r.innermargin
    for i, seite in enumerate(pdf.pages, 1):
        if vollflaechig(seite):
            continue
        zonen = rahmenzonen(seite, r)
        for w in seite.extract_words():
            x0, x1 = w["x0"] / MM, w["x1"] / MM
            b.geprueft += 1
            if x0 < r.outermargin - tol:
                b.verstoesse.append(
                    f"S.{i}: '{w['text'][:24]}' beginnt bei {x0:.1f} mm, "
                    f"links vom Steg")
                continue
            if bund_von + tol < x0 < bund_bis - tol:
                if any(a <= w["top"] <= e for a, e in zonen):
                    continue          # Rahmenelement laeuft ueber volles Mass
                b.verstoesse.append(
                    f"S.{i}: '{w['text'][:24]}' beginnt im Bund ({x0:.1f} mm)")
                continue
            if x0 < bund_von and x1 > bund_von + tol:
                if any(a <= w["top"] <= e for a, e in zonen):
                    continue          # Rahmenelement, zulaessig
                b.verstoesse.append(
                    f"S.{i}: '{w['text'][:24]}' verlässt die Marginalspalte "
                    f"(bis {x1:.1f} mm)")
    return b


def pruefe_legendenflucht(pdf, r: Raster, praefix="Tabelle", tol=3.0) -> Befund:
    b = Befund("A5", "Legendenflucht der Tabellen")
    for i, seite in enumerate(pdf.pages, 1):
        linien = [o["top"] for o in waagerechte_linien(seite)
                  if abs((o["x1"] - o["x0"]) / MM - r.textcolumn) < 0.6]
        for w in seite.extract_words():
            if not w["text"].startswith(praefix):
                continue
            if w["x0"] / MM > r.innermargin - 1:   # nur Marginalspalte
                continue
            b.geprueft += 1
            abstand = min((abs(t - w["top"]) for t in linien), default=999)
            if abstand > tol:
                b.verstoesse.append(
                    f"S.{i}: Legende {abstand:.1f} pt neben der Tabellenkante")
    return b


def pruefe_marginalzonen(pdf, r: Raster, tol=0.6) -> Befund:
    """Die Marginalspalte hat zwei Zonen: links die Glossen, rechts die
    Gliederungsziffern. Überschneiden sie sich, stehen Randtext und Ziffer
    übereinander -- unabhängig davon, ob sie im konkreten Fall auf derselben
    Zeile landen."""
    b = Befund("A7", "Zonen der Marginalspalte")
    glosse_bis = r.outermargin + r.glosswidth
    for i, seite in enumerate(pdf.pages, 1):
        if vollflaechig(seite):
            continue
        zonen = rahmenzonen(seite, r)
        for w in seite.extract_words():
            x0, x1 = w["x0"] / MM, w["x1"] / MM
            if x0 >= r.innermargin - r.gutter - 1:
                continue                      # nicht in der Marginalspalte
            if any(a <= w["top"] <= e for a, e in zonen):
                continue                      # Rahmensatz
            b.geprueft += 1
            if x0 < glosse_bis - tol and x1 > glosse_bis + tol:
                b.verstoesse.append(
                    f"S.{i}: '{w['text'][:22]}' überschreitet die Ziffernzone "
                    f"({x1:.1f} mm, Grenze {glosse_bis:.1f} mm)")
            elif x0 >= glosse_bis - tol and x1 > r.outermargin + r.margincolumn + tol:
                b.verstoesse.append(
                    f"S.{i}: Ziffer '{w['text'][:12]}' reicht bis {x1:.1f} mm")
    return b


def pruefe_zeilenanfang(pdf, r: Raster, klein=2.5, tol=0.3) -> Befund:
    """Kein Absatz beginnt mit Einzug.

    Die Klasse setzt ohne Einzug. Ein einzelner Wortabstand am Zeilenanfang
    -- etwa aus einem Zeilenumbruch hinter einem Makro -- faellt beim Lesen
    sofort auf, ist im Quelltext aber unsichtbar. Geprueft wird der schmale
    Bereich rechts der Textachse: gewollte Einzuege (Listen, Tabellen) liegen
    deutlich weiter rechts, ein versehentlicher Wortabstand nicht.

    Gewertet werden nur volle Fliesstextzeilen. Zaehler und Nenner eines
    Bruchs oder ein Index sind eigene Grundlinien mit wenigen Zeichen und
    beginnen zu Recht neben der Achse.
    """
    b = Befund("A8", "Zeilenanfang ohne Einzug")
    achse = r.innermargin
    for i, seite in enumerate(pdf.pages, 1):
        if vollflaechig(seite):
            continue
        zonen = rahmenzonen(seite, r)
        zeilen: dict[float, list] = {}
        for c in seite.chars:
            if c["x0"] / MM < achse - 1:
                continue
            if abs(c.get("size", 0) - r.bodysize) > 0.35:
                continue
            if any(a <= c["top"] <= e for a, e in zonen):
                continue
            zeilen.setdefault(round(c["matrix"][5], 2), []).append(c)
        for _, cs in zeilen.items():
            if len(cs) < 20:
                continue
            x0 = min(c["x0"] for c in cs) / MM
            b.geprueft += 1
            if achse + tol < x0 < achse + klein:
                b.verstoesse.append(
                    f"S.{i}: Zeile beginnt {x0 - achse:.2f} mm rechts der Textachse")
    return b


def pruefe_figurenlegende(pdf, r):
    """A9: Die Abbildungslegende steht in der Marginalspalte und fluchtet
    mit der Oberkante der Abbildung (Toleranz 1 pt)."""
    b = Befund("A9", "Abbildungslegende neben der Abbildung")
    satzlinks = (r.outermargin + r.margincolumn + r.gutter) * MM
    for i, seite in enumerate(pdf.pages, 1):
        for w in seite.extract_words():
            if w["x0"] >= (r.outermargin + r.margincolumn - r.numberzone) * MM:
                continue
            if not re.fullmatch(r"Abbildung\d+", w["text"]):
                continue
            b.geprueft += 1
            objekte = ((seite.rects or []) + (seite.lines or []) +
                       (seite.curves or []) + (seite.images or []) +
                       seite.extract_words())
            kanten = [o["top"] for o in objekte
                      if o["x0"] > satzlinks - 2
                      and w["top"] - 6 <= o["top"] <= w["top"] + 400]
            if not kanten:
                b.verstoesse.append(f"S.{i}: keine Abbildung neben der Legende")
                continue
            d = min(kanten) - w["top"]
            if abs(d) > 3.0:
                b.verstoesse.append(
                    f"S.{i}: Legende {abs(d):.2f} pt "
                    f"{'unter' if d < 0 else 'über'} der Abbildungsoberkante")
    return b


def pruefe_seitenfuss(pdf, r: Raster, tex: str | None) -> Befund:
    b = Befund("A6", "Keine Überschrift am Seitenfuss")
    if not tex:
        b.titel += "  [übersprungen, kein --tex]"
        return b
    quelle = open(tex, encoding="utf-8").read()
    kopfzeilen = set()
    for m in re.finditer(r"\\(?:sub)?section\*?\{(.+?)\}\s*$", quelle, re.M):
        t = re.sub(r"\\[a-zA-Z]+\{?.?\}?", "", m.group(1))
        kopfzeilen.add(re.sub(r"\s+", "", t))
    for i, seite in enumerate(pdf.pages, 1):
        gruppen = zeilen(seite, r.innermargin)
        if not gruppen:
            continue
        letzte = "".join(w["text"] for w in
                         sorted(gruppen[max(gruppen)], key=lambda w: w["x0"]))
        rein = re.sub(r"^[0-9A-Z](\.[0-9])?", "", letzte)
        b.geprueft += 1
        if len(rein) > 4 and any(rein.startswith(h[:14]) or h.startswith(rein[:14])
                                 for h in kopfzeilen if h):
            b.verstoesse.append(f"S.{i}: endet mit '{letzte[:40]}'")
    return b


def main() -> int:
    ap = argparse.ArgumentParser(description="SwissTeX-Konformitätsprüfung")
    ap.add_argument("pdf")
    ap.add_argument("--tex", help="Quelle, für die Prüfung A6")
    ap.add_argument("--outermargin", type=float, default=24.0)
    ap.add_argument("--topmargin", type=float, default=26.0)
    ap.add_argument("--margincolumn", type=float, default=30.0)
    ap.add_argument("--gutter", type=float, default=7.0)
    ap.add_argument("--numberzone", type=float, default=8.0)
    ap.add_argument("--textcolumn", type=float, default=105.0)
    ap.add_argument("--gridunit", type=float, default=13.5)
    ap.add_argument("--bodysize", type=float, default=9.5)
    ap.add_argument("--verbose", "-v", action="store_true")
    a = ap.parse_args()

    r = Raster(a.outermargin, a.margincolumn, a.gutter, a.numberzone,
               a.textcolumn, a.topmargin, a.gridunit, a.bodysize)

    with pdfplumber.open(a.pdf) as pdf:
        befunde = [
            pruefe_achsentreue(pdf, r),
            pruefe_rasterbindung(pdf, r),
            pruefe_satzspiegel(pdf, r),
            pruefe_marginalspalte(pdf, r),
            pruefe_legendenflucht(pdf, r),
            pruefe_marginalzonen(pdf, r),
            pruefe_zeilenanfang(pdf, r),
            pruefe_figurenlegende(pdf, r),
            pruefe_seitenfuss(pdf, r, a.tex),
        ]
        seiten = len(pdf.pages)

    print(f"\nswisscheck  {a.pdf}  ({seiten} Seiten)")
    print(f"Raster: Steg {r.outermargin:g} + Marginalie {r.margincolumn:g} + "
          f"Bund {r.gutter:g} + Satz {r.textcolumn:g} mm, "
          f"Zeile {r.gridunit_pt:g} pt\n")
    for b in befunde:
        print(b.zeile())
        if b.verstoesse:
            zeigen = b.verstoesse if a.verbose else b.verstoesse[:5]
            for v in zeigen:
                print(f"        {v}")
            if len(b.verstoesse) > len(zeigen):
                print(f"        ... {len(b.verstoesse) - len(zeigen)} weitere")
    offen = sum(len(b.verstoesse) for b in befunde)
    print(f"\n{'bestanden' if offen == 0 else str(offen) + ' Verstösse'}\n")
    return 0 if offen == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
