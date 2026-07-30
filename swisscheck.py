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
  A7  Marginalzonen    Glossen- und Ziffernzone der Marginalspalte trennen sich.
  A8  Zeilenanfang     Kein Absatz beginnt mit einem unbeabsichtigten Einzug.
  A9  Figurenlegende   Abbildungslegende fluchtet mit der Abbildungsoberkante.
  A10 Fusszeile        Grundlinie auf dem Rasterfusspunkt; Klassifizierung
                       und Metadaten bleiben in ihrer je eigenen Zone.
  A11 Kolumnentitel    Pagina im Grundschriftgrad, Grundlinie auf der
                       verlängerten Rasterzeile; keine Grafik in der Kopfzone.
  A12 Umschlag         Farbband auf Rasterzeilen; Schriftgrade aus der
                       Anzeigenskala oder grundschriftgrad-nah; ein
                       Überformatzeichen hängt an Rasterzeile und Textachse.
  A13 Kommensurabilität Die DEKLARIERTEN Nebentext-Durchschüsse sind kleine
                       Brüche des Rastermasses, und der in der Marginalspalte
                       GEMESSENE Durchschuss trifft einen davon.
  A15 Farbrollen       Ein eigenständiges Band unterscheidet sich deutlich
                       von der Signalfarbe; das gedruckte Band trägt den
                       deklarierten Ton.
  A16 Schriftinventar  Nur deklarierte Schriftfamilien sind eingebettet.
  A17 Glossenlänge     Die Glossenzone trägt Beschriftung, nicht Fliesstext
                       (I3): kein Glossenblock über sechs Zeilen.
  (A14, zweisprachiger Satz, ist für eine spätere Ausbaustufe vorgesehen und
  hier nicht implementiert.)

A10-A13/A15/A16/A17 lesen ihre Kennzahlen aus der Sidecar-Datei
<jobname>.swisscheck (siehe unten); ohne sie überspringen sie sich sauber
(0 geprüft, kein Fehler).

Aufruf:
    python3 swisscheck.py bericht.pdf [--tex bericht.tex]
    python3 swisscheck.py bericht.pdf --gridunit 13.5 --bodysize 9.5
"""

from __future__ import annotations

import argparse
import re
import sys
from collections import Counter
from dataclasses import dataclass, field, replace
from pathlib import Path

import pdfplumber

MM = 72 / 25.4
# PDF-Koordinaten stehen in DTP-Punkt (1/72 Zoll), TeX rechnet in
# TeX-Punkt (1/72,27 Zoll). Ohne diese Umrechnung erscheint jedes
# Basislinienraster als langsam wegdriftend.
PT = 72 / 72.27

# Zwei wiederkehrende Toleranzwerte, empirisch statt abgeleitet, deshalb als
# Parameter-Vorgabe an jeder einzelnen Stelle wiederholt statt als Konstante:
#   0.6pt  Positionstoleranz für Linien-/Kantenlagen und Zonengrenzen
#          (pruefe_achsentreue, pruefe_marginalzonen, pruefe_fusszeile,
#          pruefe_umschlag) -- deckt die Rundung ab, mit der pdfplumber
#          Vektorkoordinaten aus dem PDF-Content-Stream meldet.
#   1.0mm  "Wortkasten-Spielraum" für Prüfungen, die einen Wortkasten gegen
#          eine Kante stellen (pruefe_marginalspalte, pruefe_fusszeile,
#          farbfelder, _bandrechtecke) -- deckt die kleine Überlänge ab, die
#          pdfplumber Wortkästen an den seitlichen Glyphenkanten lässt.


@dataclass
class Raster:
    """Kennzahlen des Satzspiegels, in Millimetern bzw. Punkt.

    Die ersten acht Felder sind die ursprüngliche (v1) Kommandozeilen-
    Schnittstelle, unverändert in Reihenfolge und Vorgabe -- bestehende
    Aufrufer, die per Positionsargument konstruieren, bleiben lauffähig.
    Alle folgenden Felder gehören zur Kennzahlen-Sidecar-Datei: Optional
    (None), solange keine vorliegt -- die sieben sidecar-gebundenen
    Prüfungen A10-A13/A15/A16/A17 erkennen das an `has_sidecar` und
    überspringen sich dann sauber, statt eine geratene Vorgabe zu prüfen.
    """

    outermargin: float = 24.0
    margincolumn: float = 30.0
    gutter: float = 7.0
    numberzone: float = 8.0
    textcolumn: float = 105.0
    topmargin: float = 26.0
    gridunit_pt: float = 13.5
    bodysize_pt: float = 9.5

    # -- Task 9: aus der Sidecar-Datei, sonst grob aus dem Rastermass
    # abgeleitet (dieselben Verhältnisse wie die Klassenvorgabe: 2/3, 3/4,
    # 3/4, 2 und 3 Rastereinheiten) -- siehe die *_pt-Felder unten.
    gridlines: int = 51
    annotationleading_pt: float | None = None
    glossleading_pt: float | None = None
    footnoteleading_pt: float | None = None
    headsep_pt: float | None = None
    footskip_pt: float | None = None
    accent_rgb: tuple[int, int, int] = (255, 55, 37)
    band_is_accent: bool = True
    band_rgb: tuple[int, int, int] | None = None
    paper_rgb: tuple[int, int, int] | None = None
    ink_rgb: tuple[int, int, int] | None = None
    mainfamily: str | None = None
    condensedfamily: str | None = None
    mathfont: str | None = None
    # Von der Identität ERKLÄRTE Fremdschriften aus eingebundenen Logodateien
    # (\swisslogofiles{logofonts=...}); A16 lässt genau diese zusätzlich zu.
    logofonts: tuple[str, ...] = ()
    classification: str | None = None
    docid: str | None = None
    has_sidecar: bool = False

    @property
    def gridunit(self) -> float:
        """Rastermass in PDF-Punkt."""
        return self.gridunit_pt * PT

    @property
    def bodysize(self) -> float:
        return self.bodysize_pt * PT

    @property
    def annotationleading(self) -> float:
        v = self.annotationleading_pt
        if v is None:
            v = 2 * self.gridunit_pt / 3
        return v * PT

    @property
    def glossleading(self) -> float:
        v = self.glossleading_pt
        if v is None:
            v = 3 * self.gridunit_pt / 4
        return v * PT

    @property
    def footnoteleading(self) -> float:
        v = self.footnoteleading_pt
        if v is None:
            v = 3 * self.gridunit_pt / 4
        return v * PT

    @property
    def headsep(self) -> float:
        v = self.headsep_pt if self.headsep_pt is not None else 2 * self.gridunit_pt
        return v * PT

    @property
    def footskip(self) -> float:
        v = self.footskip_pt if self.footskip_pt is not None else 3 * self.gridunit_pt
        return v * PT

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

    @classmethod
    def from_sidecar(cls, d: dict[str, str], base: "Raster") -> "Raster":
        """Ueberlagert `base` (die Kommandozeilen-Vorgaben) mit den in der
        Sidecar-Datei DEKLARIERTEN Werten. Ein einzelner fehlender
        Schluessel (z. B. eine handgebaute, unvollstaendige Sidecar-Datei)
        laesst das entsprechende Feld unveraendert bei `base` stehen, statt
        die gesamte Datei zu verwerfen."""
        kw: dict = {}

        def mm(schluessel: str, feld: str) -> None:
            if schluessel in d:
                kw[feld] = _parse_mm(d[schluessel])

        def pt(schluessel: str, feld: str) -> None:
            if schluessel in d:
                kw[feld] = _parse_pt(d[schluessel])

        mm("outermargin", "outermargin")
        mm("margincolumn", "margincolumn")
        mm("gutter", "gutter")
        mm("numberzone", "numberzone")
        mm("textcolumn", "textcolumn")
        mm("topmargin", "topmargin")
        pt("gridunit", "gridunit_pt")
        pt("bodysize", "bodysize_pt")
        pt("annotationleading", "annotationleading_pt")
        pt("glossleading", "glossleading_pt")
        pt("footnoteleading", "footnoteleading_pt")
        pt("headsep", "headsep_pt")
        pt("footskip", "footskip_pt")
        if "gridlines" in d:
            kw["gridlines"] = int(d["gridlines"])
        if "accent" in d:
            kw["accent_rgb"] = _parse_rgb(d["accent"])
        if "band" in d:
            wert = d["band"].strip()
            kw["band_is_accent"] = wert == "accent"
            kw["band_rgb"] = None if wert == "accent" else _parse_rgb(wert)
        if "paper" in d:
            kw["paper_rgb"] = _parse_rgb(d["paper"])
        if "ink" in d:
            kw["ink_rgb"] = _parse_rgb(d["ink"])
        for schluessel in ("mainfamily", "condensedfamily", "mathfont",
                           "classification", "docid"):
            if schluessel in d:
                kw[schluessel] = d[schluessel]
        if "logofonts" in d:
            kw["logofonts"] = tuple(t.strip() for t in d["logofonts"].split(",")
                                     if t.strip())
        kw["has_sidecar"] = True
        return replace(base, **kw)


def _parse_pt(s: str) -> float:
    """TeX-Punkt-Literal aus der Sidecar-Datei, z. B. "13.5pt" -> 13.5
    (TeX-pt -- dieselbe Einheit, in der gridunit_pt/bodysize_pt bereits
    beide Kommandozeile UND Klassenvorgabe seit jeher verstehen)."""
    s = s.strip()
    if s.endswith("pt"):
        s = s[:-2]
    return float(s)


def _parse_mm(s: str) -> float:
    """Kennzahl, wie die Klassenoption sie hinterlegt (z. B. "24mm").
    Ein reiner Zahlwert ohne Einheit wird unveraendert als mm gelesen."""
    s = s.strip()
    for einheit, faktor in (("mm", 1.0), ("cm", 10.0), ("in", 25.4),
                             ("pt", 25.4 / 72.27)):
        if s.endswith(einheit):
            return float(s[: -len(einheit)]) * faktor
    return float(s)


def _parse_rgb(s: str) -> tuple[int, int, int]:
    teile = [int(t.strip()) for t in s.split(",")]
    return (teile[0], teile[1], teile[2])


def lade_sidecar(pfad: str | None, pdf_pfad: str) -> dict[str, str] | None:
    """--params <Datei>, sonst Auto-Erkennung von <pdf-stamm>.swisscheck
    neben der PDF. Keine Datei gefunden -> None (altes Verhalten, A1-A9
    unveraendert, A10-A13/A15/A16/A17 uebersprungen)."""
    p = Path(pfad) if pfad else Path(pdf_pfad).with_suffix(".swisscheck")
    if not p.exists():
        return None
    d: dict[str, str] = {}
    for zeile in p.read_text(encoding="utf-8").splitlines():
        if "=" in zeile:
            k, v = zeile.split("=", 1)
            d[k.strip()] = v.strip()
    return d


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
    Zeile landen.

    Gewertet wird nur der Satzspiegel-Streifen (topmargin bis topmargin +
    gridlines Rasterzeilen). Ober- und unterhalb davon gibt es weder Glossen
    noch Gliederungsziffern: Die Kopfzone trägt Pagina und Lauftitel, die
    Fusszone Klassifizierungsmarke und Metazeile -- beide mit einer eigenen
    Zonenordnung, die A11 bzw. A10 prüfen. Die Klassifizierungsmarke steht
    dort ausdrücklich über die GANZE Marginalspalte (Spezifikation 6:
    "margin zone"), nicht nur über deren Glossenhälfte; ohne diese
    Einschränkung meldete A7 sie als Zonenüberschreitung, obwohl sie genau
    dort steht, wo sie hingehört."""
    b = Befund("A7", "Zonen der Marginalspalte")
    glosse_bis = r.outermargin + r.glosswidth
    for i, seite in enumerate(pdf.pages, 1):
        if vollflaechig(seite):
            continue
        oben = r.topmargin * MM
        unten = oben + r.gridlines * r.gridunit
        zonen = rahmenzonen(seite, r)
        for w in seite.extract_words():
            x0, x1 = w["x0"] / MM, w["x1"] / MM
            if not (oben - 1 <= w["top"] <= unten + 1):
                continue                      # Kopf-/Fusszone, siehe A10/A11
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


# ---------------------------------------------------------------------
# A10-A13, A15-A17 -- geprüft werden DEKLARIERTE Kennzahlen aus der
# Sidecar-Datei, nicht mehr feste Annahmen. Fehlt die Sidecar-Datei (ältere
# PDFs), degradieren alle sieben Prüfungen sauber: 0 geprüft, eine Notiz im
# Titel, kein Verstoss -- exakt das v1-Verhalten bleibt für PDFs ohne
# Sidecar erhalten.
# ---------------------------------------------------------------------

def _ohne_sidecar(b: Befund) -> Befund:
    b.titel += "  [übersprungen, keine Kennzahlen-Sidecar]"
    return b


def pruefe_fusszeile(pdf, r: Raster, tol=0.6, postol=1.0) -> Befund:
    """A10: Die Grundlinie der Fusszeile liegt auf topmargin + gridlines
    Rasterzeilen + footskip. Klassifizierungswörter (links, in der
    Marginalspalte) verlassen diese nicht in den Bund; Metadatenwörter
    (rechts, ab dem Bund) beginnen nicht früher als am Steg."""
    b = Befund("A10", "Fusszeile auf dem Rasterfusspunkt")
    if not r.has_sidecar:
        return _ohne_sidecar(b)
    satzspiegel_unten = r.topmargin * MM + r.gridlines * r.gridunit
    soll = satzspiegel_unten + r.footskip
    for i, seite in enumerate(pdf.pages, 1):
        if vollflaechig(seite):
            continue                      # Umschlag: eigene Fusszeilenordnung
        fusszeichen = [c for c in seite.chars
                       if c.get("upright", True) and c["top"] > satzspiegel_unten + 2]
        if not fusszeichen:
            continue                      # keine Fusszeile auf dieser Seite
        grundlinien_pdf = Counter(round(c["matrix"][5], 1) for c in fusszeichen)
        grundlinie = seite.height - grundlinien_pdf.most_common(1)[0][0]
        b.geprueft += 1
        abweichung = abs(grundlinie - soll)
        if abweichung > tol:
            b.verstoesse.append(
                f"S.{i}: Fusszeile {abweichung:.2f} pt neben dem Rasterfusspunkt")
        for w in seite.extract_words():
            if w["top"] <= satzspiegel_unten + 2:
                continue
            x0, x1 = w["x0"] / MM, w["x1"] / MM
            if x0 < r.outermargin + r.margincolumn:
                if x1 > r.outermargin + r.margincolumn + postol:
                    b.verstoesse.append(
                        f"S.{i}: '{w['text'][:20]}' verlässt die Marginalspalte "
                        f"in der Fusszeile ({x1:.1f} mm)")
            elif x0 < r.innermargin - postol:
                b.verstoesse.append(
                    f"S.{i}: '{w['text'][:20]}' beginnt im Bund der Fusszeile "
                    f"({x0:.1f} mm)")
    return b


def pruefe_kolumnentitel(pdf, r: Raster, tol=0.35, tol_pos=0.6) -> Befund:
    """A11: Die Pagina in der Kopfzone hat den Grundschriftgrad und ihre
    Grundlinie liegt auf der VERLÄNGERTEN Rasterzeile (Spiegelbild der
    A10-Formel für die Fusszeile: dort Satzunterkante + footskip, hier
    Satzoberkante − headsep); keine Grafik ragt in die Kopfzone (Oberkante
    oberhalb von topmargin) hinein -- der Kolumnentitel der Klasse setzt
    dort ausschliesslich Pagina und Kolumnentitel-Text, nie Vektor- oder
    Rastergrafik.

    Die Grundlinienprüfung ist nicht akademisch: sie fand 3,587 pt Versatz
    in allen drei Referenzdokumenten (fancyhdr hängt an jeden Kopfinhalt
    einen \\strut, und weil auf den Kopfsatz noch die -- unsichtbare --
    Kopflinie folgt, rutscht der Bezugspunkt der Kopfbox um dessen Tiefe
    unter die Textgrundlinie; siehe swisstex.cls Abschnitt 7).

    Geprüft werden `page.images` (Rastergrafik) UND `page.rects`/`lines`/
    `curves` (Vektorgrafik): ein per \\includegraphics eingebundenes PDF-
    Logo landet in einer PDF NICHT zwingend als Bild-XObject -- ist die
    Quelle selbst Vektorgrafik (z. B. ein mit LaTeX gesetztes Logo wie
    acme-logo.pdf), bettet XeTeX es als Form-XObject ein, dessen Inhalt
    pdfplumber als gewöhnliche Linien/Flächen/Zeichen aufschlüsselt, nicht
    als `image`. Empirisch bestätigt (siehe Bericht): ein
    `\\includegraphics[height=5pt]{acme-logo.pdf}` in `\\fancyhead[R]`
    erscheint in `page.images` als LEERE Liste, obwohl die eingebettete
    Regel als `page.lines`-Eintrag und der Text als `page.chars` klar
    sichtbar sind -- die reine `page.images`-Prüfung hätte diesen Fall
    verfehlt."""
    b = Befund("A11", "Kolumnentitel: Pagina und Kopfzone")
    if not r.has_sidecar:
        return _ohne_sidecar(b)
    kopfgrenze = r.topmargin * MM
    soll = kopfgrenze - r.headsep
    for i, seite in enumerate(pdf.pages, 1):
        if vollflaechig(seite):
            continue                      # Umschlag hat keinen Kolumnentitel
        paginas = [w for w in seite.extract_words(extra_attrs=["size"])
                   if w["top"] < kopfgrenze - 1 and re.fullmatch(r"\d+", w["text"])]
        if paginas:
            pagina = min(paginas, key=lambda w: w["x0"])
            b.geprueft += 1
            if abs(pagina["size"] - r.bodysize) > tol:
                b.verstoesse.append(
                    f"S.{i}: Pagina {pagina['size']:.2f} pt statt "
                    f"{r.bodysize:.2f} pt")
            # Grundlinie der Pagina, aus der Textmatrix ihrer Zeichen (wie
            # A2/A10) -- die Wortoberkante allein trüge die Glyphenhöhe mit.
            paginazeichen = [c for c in seite.chars
                             if c.get("upright", True)
                             and c["top"] < kopfgrenze - 1
                             and abs(c["x0"] - pagina["x0"]) < 1.0]
            if paginazeichen:
                grundlinie = seite.height - Counter(
                    round(c["matrix"][5], 1)
                    for c in paginazeichen).most_common(1)[0][0]
                b.geprueft += 1
                abweichung = abs(grundlinie - soll)
                if abweichung > tol_pos:
                    b.verstoesse.append(
                        f"S.{i}: Kopfgrundlinie {abweichung:.2f} pt neben der "
                        f"verlängerten Rasterzeile")
        # Bildfreiheit der Kopfzone: EINE Prüfung je Seite (die Abwesenheit
        # ist der geprüfte Sachverhalt). Vorher zählte `geprueft` nur die
        # Verstösse mit -- eine saubere Seite blieb ungezählt, und die
        # Prüfung sah in der Ausgabe leerer aus, als sie ist.
        b.geprueft += 1
        grafik = ((seite.images or []) + (seite.rects or []) +
                  (seite.lines or []) + (seite.curves or []))
        for o in grafik:
            if o["top"] < kopfgrenze:
                b.verstoesse.append(
                    f"S.{i}: Grafik in der Kopfzone (Oberkante {o['top']:.1f} pt)")
    return b


def _bandrechtecke(seite, tol=1.0):
    """Volle Seitenbreite, aber NICHT die randabfallende Grundfläche des
    Umschlags selbst (die läuft über die volle SeitenHÖHE, ein Farbband
    dagegen nur über wenige Rasterzeilen)."""
    for o in (seite.rects or []):
        breite = o["x1"] - o["x0"]
        hoehe = o["y1"] - o["y0"]
        if abs(breite - seite.width) < tol and hoehe < 0.9 * seite.height:
            yield o


def _umschlag_schriftgrad_ok(size: float, r: Raster, tol=0.5) -> bool:
    # Eine fruehere dritte Bedingung "size <= 8 + tol" ist entfernt: sie war
    # fuer jeden realistischen Grundschriftgrad toter Code, weil ihre
    # Schwelle (8 + tol) erst unterhalb von bodysize <~ 7.7pt ueber die
    # folgende Bedingung (r.bodysize + 0.35 + tol) hinausreicht -- kleiner
    # als jede in diesem Projekt oder sonst ueblich gesetzte
    # Fliesstextgroesse (Vorgabe 9.5pt). Verifiziert an allen drei
    # Referenzdokumenten: keine Umschlag-Schriftgroesse dort haengt an dieser
    # Bedingung, alle laufen ueber die erste oder die Anzeigenskala.
    if size <= r.bodysize + 0.35 + tol:
        return True
    return any(abs(size - 0.8 * n * r.gridunit) <= tol for n in range(1, 7))


def _glyphzeichen(seite, r: Raster, faktor=8.0):
    """Das Überformatzeichen einer Umschlagseite: EIN einzelnes Zeichen im
    Grad von mindestens `faktor` Rasterzeilen.

    Es ist kein Anzeigengrad und darf darum nicht an der Anzeigenskala
    gemessen werden. Die Klasse leitet seinen Grad aus `glyphlines` ab
    (Vorgabe 34 Rasterzeilen = 459 pt) -- ein Ueberformat, das aus dem
    Raster stammt, nicht aus \\swissdisplay. Spezifikation 9 verlangt für
    das Zeichen etwas anderes als eine Grössenregel: Grundlinie auf einer
    Rasterzeile, linke Kante auf der Textachse. Genau das prüft A12
    stattdessen (siehe unten).

    Die Einzahl ist Teil der Erkennung: ein Zeichen ist ein Zeichen. Stehen
    mehrere Zeichen in diesem Grad, ist es Satz und keine Ausnahme -- dann
    greift die gewöhnliche Grössenregel wieder."""
    gross = [c for c in seite.chars if c.get("size", 0) >= faktor * r.gridunit]
    return gross if len(gross) == 1 else []


def pruefe_umschlag(pdf, r: Raster, tol_pos=0.6, tol_size=0.5) -> Befund:
    """A12: Auf Umschlagseiten (randabfallendes Farbfeld über die ganze
    Seite) liegen Ober-/Unterkante jedes Farbbands auf topmargin + k
    Rasterzeilen; alle Schriftgrade stammen aus der Anzeigenskala, sind
    grundschriftgrad-nah oder ausgezeichnet/Marginalien-klein. Das
    Überformatzeichen ist von der Grössenregel ausgenommen und wird
    stattdessen an seiner Verankerung gemessen (siehe _glyphzeichen)."""
    b = Befund("A12", "Umschlag: Farbband, Anzeigengrade, Zeichenanker")
    if not r.has_sidecar:
        return _ohne_sidecar(b)
    for i, seite in enumerate(pdf.pages, 1):
        if not vollflaechig(seite):
            continue
        for o in _bandrechtecke(seite):
            for kante, name in ((o["top"], "Oberkante"), (o["bottom"], "Unterkante")):
                b.geprueft += 1
                abstand = kante - r.topmargin * MM
                rest = abstand % r.gridunit
                abweichung = min(rest, r.gridunit - rest)
                if abweichung > tol_pos:
                    b.verstoesse.append(
                        f"S.{i}: Band-{name} {abweichung:.2f} pt neben dem Raster")
        glyphen = _glyphzeichen(seite, r)
        glyphgroessen = {round(c["size"], 2) for c in glyphen}
        groessen = {round(c["size"], 2) for c in seite.chars if c.get("size")}
        for g in sorted(groessen):
            if g in glyphgroessen:
                continue                  # Überformatzeichen, eigene Regel
            b.geprueft += 1
            if not _umschlag_schriftgrad_ok(g, r, tol_size):
                b.verstoesse.append(
                    f"S.{i}: Schriftgrad {g:.2f} pt ausserhalb der Anzeigenskala")
        for c in glyphen:
            grundlinie = seite.height - c["matrix"][5]
            abstand = grundlinie - r.topmargin * MM
            rest = abstand % r.gridunit
            abweichung = min(rest, r.gridunit - rest)
            b.geprueft += 1
            if abweichung > tol_pos:
                b.verstoesse.append(
                    f"S.{i}: Zeichen-Grundlinie {abweichung:.2f} pt neben "
                    f"dem Raster")
            b.geprueft += 1
            kante = abs(c["x0"] - r.innermargin * MM)
            if kante > tol_pos:
                b.verstoesse.append(
                    f"S.{i}: Zeichen-Linkskante {kante:.2f} pt neben der "
                    f"Textachse")
    return b


def _kleiner_bruch(verhaeltnis: float, maxnenner: int = 4,
                    tol: float = 1e-3) -> tuple[int, int] | None:
    """Kleinster Bruch n/m mit m <= maxnenner, der `verhaeltnis` trifft;
    None, wenn keiner passt. "Klein" heisst hier: ein Verhältnis, das man
    beim Lesen noch als Verhältnis erkennt (2/3, 3/4, 1/2, 5/4), nicht eine
    beliebige Dezimalzahl, die zufällig aufgeht."""
    for m in range(1, maxnenner + 1):
        n = round(verhaeltnis * m)
        if n >= 1 and abs(verhaeltnis - n / m) <= tol:
            return (n, m)
    return None


def _pruefe_deklarierte_verhaeltnisse(r: Raster, b: Befund,
                                       maxnenner: int = 4) -> None:
    """A13, erster Teil: die DEKLARIERTEN Nebentext-Durchschüsse selbst
    müssen kleine Brüche des deklarierten Rastermasses sein.

    Ohne diesen Teil prüfte A13 nur das Gemessene gegen das Deklarierte und
    hätte damit jede in sich stimmige, aber unkommensurable Erklärung
    durchgewinkt: eine Sidecar-Datei mit gridunit=12pt und den Durchschüssen
    9/10.125 pt bestand die alte Fassung, obwohl 10.125/12 kein Bruch mit
    kleinem Nenner ist (die Klasse leitet 10.125 aus einem 13,5-pt-Raster
    ab -- die Zahlen gehören zu zwei verschiedenen Systemen). Die Doktrin
    (Spezifikation 8) verlangt beides: das Ergebnis trifft die Erklärung,
    UND die Erklärung ist rastergebunden."""
    for name, wert in (("annotationleading", r.annotationleading_pt),
                       ("glossleading", r.glossleading_pt),
                       ("footnoteleading", r.footnoteleading_pt)):
        if wert is None:
            continue          # nicht deklariert -> Klassenvorgabe, per Bau 2/3, 3/4
        b.geprueft += 1
        verhaeltnis = wert / r.gridunit_pt
        bruch = _kleiner_bruch(verhaeltnis, maxnenner)
        if bruch is None:
            b.verstoesse.append(
                f"deklariert: {name} {wert:g} pt zu gridunit "
                f"{r.gridunit_pt:g} pt ist Verhältnis {verhaeltnis:.4f} -- "
                f"kein Bruch mit Nenner bis {maxnenner}")


def pruefe_kommensurabilitaet(pdf, r: Raster, tol=0.35) -> Befund:
    """A13: Grundlinienabstände kleiner Schrift in der Marginalspalte
    (Randglossen, Fussnoten-artige Randnotizen, Tabellen-/Abbildungs-
    legenden -- Grad < Grundschriftgrad-0,5) bilden je Seite Cluster; jedes
    Cluster muss im Mittel einem der drei deklarierten Nebentext-
    Durchschüsse (Anmerkung/Glosse/Fussnote) entsprechen. Abstände über
    zwei Rastereinheiten trennen unabhängige Blöcke und zählen nicht als
    Durchschuss; ein einzelner (nicht wiederholter) Abstand bildet kein
    Cluster und wird nicht gewertet.

    Eingeschränkter Geltungsbereich (dokumentiert, siehe Bericht -- eine
    bewusste Vereinfachung, nachdem die ungefilterte, seitenweite Fassung
    sich an echten Dokumenten als zu störanfällig erwies):

    1. NUR die Marginalspalte (x0 < innermargin) wird betrachtet, nicht der
       Satzspiegel. Grund, empirisch an acme-demo.pdf gefunden: kleine
       Schriftgrade im Satzspiegel stammen dort nicht nur aus echten
       Nebentext-Blöcken, sondern auch aus \\swisscode-Einsprengseln MITTEN
       in einer normalen Grundtextzeile (deren Grundlinie dem Grundtext-
       Rastermass folgt, nicht \\footnoteleading) und aus
       Tabellenkörperzeilen, deren Zeilenabstand über booktabs/tabularx
       läuft und NICHT zuverlässig exakt \\footnoteleading trifft. Beides
       erzeugte Falschbefunde ohne Bezug zu einer deklarierten Kennzahl.
       Die Marginalspalte dagegen wird ausschliesslich von \\marg/
       \\sidenote und den Legendenzeilen von \\swisstable/\\swissfigure
       bestueckt -- allesamt direkte \\fontsize{...}{...}-Aufrufe der
       Klasse selbst, ohne Fremdpaket-Zeilenabstand dazwischen.
    2. Ein Cluster mit nur EINEM Beleg wird ignoriert, kein Verstoss.
       Grund, ebenfalls empirisch gefunden: \\swisstable haengt zwischen
       Legendenkopf ("Tabelle N") und Legendentext ein festes "\\\\[1pt]"
       an -- ein einzelner, bewusst gesetzter Zusatzabstand, keine
       Kennzahlen-Abweichung. Ein echter, durchgaengiger Verstoss wiederholt
       sich dagegen ueber mehrere Zeilen und bildet ein Cluster mit
       mindestens zwei Belegen.

    Nicht mehr abgedeckt: Fussnoten im Satzspiegel selbst (dort mit
    Tabellenkoerpern ununterscheidbar, siehe Punkt 1) -- keines der
    Referenzdokumente dieses Projekts hat eine mehrzeilige Fussnote, die
    Einschraenkung kostet also auf dem aktuellen Textkorpus keine reale
    Abdeckung.
    """
    b = Befund("A13", "Kommensurabilität der Nebentexte")
    if not r.has_sidecar:
        return _ohne_sidecar(b)
    _pruefe_deklarierte_verhaeltnisse(r, b)
    sollwerte = (r.annotationleading, r.glossleading, r.footnoteleading)
    schwelle = r.bodysize - 0.5
    for i, seite in enumerate(pdf.pages, 1):
        if vollflaechig(seite):
            continue                      # Umschlag: eigene Grössenskala
        zaehler: dict[float, int] = {}
        for c in seite.chars:
            if not c.get("upright", True):
                continue
            if c.get("size", 99) >= schwelle:
                continue
            if c["x0"] >= r.innermargin * MM - 1:  # nur Marginalspalte
                continue
            y = round(seite.height - c["matrix"][5], 2)
            zaehler[y] = zaehler.get(y, 0) + 1
        # Nur Grundlinien mit genug Zeichen zählen als echte Textzeile,
        # nicht einzelne verirrte Glyphen (Trennstriche, Fussnotenmarken).
        baselinien = sorted(y for y, n in zaehler.items() if n >= 3)
        if len(baselinien) < 2:
            continue
        luecken = [y1 - y0 for y0, y1 in zip(baselinien, baselinien[1:])
                   if y1 - y0 <= 2 * r.gridunit]
        if not luecken:
            continue
        cluster: dict[float, list[float]] = {}
        for g in luecken:
            cluster.setdefault(round(g, 1), []).append(g)
        for werte in cluster.values():
            if len(werte) < 2:
                continue                  # kein Cluster, nur ein Einzelbeleg
            mittel = sum(werte) / len(werte)
            b.geprueft += 1
            if not any(abs(mittel - soll) <= tol for soll in sollwerte):
                b.verstoesse.append(
                    f"S.{i}: Durchschuss {mittel:.2f} pt passt zu keinem "
                    f"deklarierten Nebentext-Durchschuss")
    return b


def _fuellfarbe(o) -> tuple[int, int, int] | None:
    """Füllfarbe eines Rechtecks als 0-255-Tripel. pdfplumber meldet sie im
    Farbraum des PDF-Inhaltsstroms: ein Wert (Grau), drei (RGB), vier
    (CMYK). Alles andere (kein Wert, benannter Farbraum) ist nicht
    vergleichbar und wird als "nicht messbar" gemeldet, nicht geraten."""
    f = o.get("non_stroking_color")
    if not f:
        return None
    try:
        werte = [float(x) for x in f]
    except (TypeError, ValueError):
        return None
    if len(werte) == 1:
        g = werte[0]
        return (round(g * 255),) * 3
    if len(werte) == 3:
        return tuple(round(max(0.0, min(1.0, x)) * 255) for x in werte)
    if len(werte) == 4:
        c, m, y, k = werte
        return tuple(round(255 * (1 - min(1.0, x + k))) for x in (c, m, y))
    return None


def pruefe_farbrollen(pdf, r: Raster, tol_kanal=2) -> Befund:
    """A15: Farbrollen, deklariert UND gedruckt.

    Zwei Teile, beide messend:

    1. Erklärung. Ist das Farbband nicht die Signalfarbe selbst
       (band != accent), muss es sich im euklidischen RGB-Abstand deutlich
       davon unterscheiden (>= 30) -- zwei kaum unterscheidbare Rottöne sind
       keine zwei Rollen, sondern ein Fehler (M-B-Regel).
    2. Ergebnis. Jedes Farbband auf einer Umschlagseite muss den
       deklarierten Ton wirklich TRAGEN: band=accent -> die Signalfarbe,
       ein eigenes band= -> genau dieses Tripel, je Kanal auf 2/255 genau.

    Teil 2 ist der eigentliche Zugewinn dieser Fassung. Vorher zählte A15
    auf dem Ein-Rot-Pfad (dem Vorgabepfad, also dem Normalfall) eine
    Prüfung, ohne irgendetwas gemessen zu haben, und meldete "ok" -- die
    Prüfung war dort vakuum. `geprueft` zählt jetzt ausschliesslich echte
    Messungen; ein Dokument ohne Umschlag hat kein Band und darum 0."""
    b = Befund("A15", "Farbrollen: Band gegen Signalfarbe")
    if not r.has_sidecar:
        return _ohne_sidecar(b)
    eigenes_band = not (r.band_is_accent or r.band_rgb is None)
    soll = r.band_rgb if eigenes_band else r.accent_rgb
    if eigenes_band:
        b.geprueft += 1
        abstand = sum((a - c) ** 2
                      for a, c in zip(r.accent_rgb, r.band_rgb)) ** 0.5
        if abstand < 30:
            b.verstoesse.append(
                f"Band {r.band_rgb} liegt nur {abstand:.1f} von der Signalfarbe "
                f"{r.accent_rgb} entfernt (Mindestabstand 30)")
    for i, seite in enumerate(pdf.pages, 1):
        if not vollflaechig(seite):
            continue                      # Farbband gibt es nur auf dem Umschlag
        for o in _bandrechtecke(seite):
            rgb = _fuellfarbe(o)
            b.geprueft += 1
            if rgb is None:
                b.verstoesse.append(
                    f"S.{i}: Farbband ohne lesbare Füllfarbe")
                continue
            if any(abs(a - c) > tol_kanal for a, c in zip(rgb, soll)):
                b.verstoesse.append(
                    f"S.{i}: Farbband gedruckt {rgb}, deklariert {soll} "
                    f"({'band' if eigenes_band else 'band=accent'})")
    return b


def _normalisiere_schriftname(s: str) -> str:
    return re.sub(r"[^a-z0-9]", "", s.lower())


# Bekannte Namensspaltung: die Dateibasis, mit der die Klasse eine Familie
# LÄDT, und der PostScript-Name, den dieselbe Familie EINGEBETTET trägt,
# sind bei TeX Gyre nicht dieselbe Zeichenkette. "texgyreheroscn" (Datei-
# basis, Klassenoption `sanscondensed`) heisst eingebettet
# "TeXGyreHerosCondensed-Regular". Ohne diese Tabelle passte die Schmal-
# schrift NIE auf ihre eigene Deklaration -- sie kam bisher nur deshalb
# durch, weil "texgyreheros" (die Grundschrift!) als Teilzeichenkette in
# "texgyreheroscondensedregular" steckt: die Prüfung war zufällig grün, nicht
# richtig. Die Tabelle ist bewusst statisch und kurz: sie deckt die Fälle
# ab, die dieses Projekt tatsächlich ausliefert, statt Namensregeln zu raten.
_SCHRIFT_ALIAS = {
    "texgyreheroscn": "texgyreheroscondensed",
}
# Weitenangaben schreiben sich je nach Hersteller "Condensed", "Cond" oder
# "Cn"; alle drei meinen dieselbe Weite und werden auf eine Form gebracht.
_WEITE_SUFFIXE = ("condensed", "cond", "cn")


def _schriftbasis(s: str) -> str:
    """Familienname in Vergleichsform: ohne Subset-Präfix (XXXXXX+), ohne
    den \\fontname-Anhang der Mathe-Schrift ("..." /OT:... at 9.5pt), ohne
    Schnittangabe (alles ab dem ersten Bindestrich), normalisiert und mit
    vereinheitlichter Weitenangabe.

    Die Trennung am ersten Bindestrich ist die PostScript-Konvention
    "Familie-Schnitt". Ein Familienname, der selbst einen Bindestrich trägt,
    würde hier zu kurz geraten -- das fängt die Teilzeichenketten-Prüfung in
    pruefe_schriftinventar als zweiten Weg wieder auf."""
    s = re.sub(r"^[A-Z]{6}\+", "", s.strip())
    s = s.replace('"', "").split("/")[0].split(" at ")[0]
    s = s.split("-")[0]
    n = _normalisiere_schriftname(s)
    n = _SCHRIFT_ALIAS.get(n, n)
    for suffix in _WEITE_SUFFIXE:
        if n.endswith(suffix) and n != suffix:
            return n[: -len(suffix)] + "condensed"
    return n


def pruefe_schriftinventar(pdf, r: Raster) -> Befund:
    """A16: Jede eingebettete Schrift muss zu einer deklarierten Familie
    passen -- mainfamily, condensedfamily, der Mathe-Schrift oder einer über
    \\swisslogofiles{logofonts=...} ausdrücklich erklärten Logo-Schrift.
    v2.0-Dokumente müssen sauber sein -- keine Legacy-Erlaubnis für TeX
    Gyre/Latin Modern, auch nicht für ältere \\swisscode-freie Dokumente.

    Verglichen wird auf zwei Wegen, in dieser Reihenfolge:

    1. Basisvergleich (_schriftbasis): Familienname gegen Familienname,
       Schnitt und Namensspaltung herausgerechnet. Das ist der genaue Weg --
       "texgyreheroscn" trifft damit "TeXGyreHerosCondensed-Regular", und
       zwar über die condensedfamily-Deklaration, nicht mehr zufällig über
       die Grundschrift.
    2. Teilzeichenkette in BEIDEN Richtungen auf den roh normalisierten
       Namen, als Auffangnetz für Familiennamen, die die Basisbildung nicht
       trifft (Bindestrich im Familiennamen, ungewöhnliche Anhänge).

    "nullfont": unicode-math lädt die Mathe-Schrift LAZY -- \\textfont
    \\symoperators bleibt TeXs eigener Platzhalter "nullfont", solange im
    ganzen Dokument nie tatsächlich Mathe gesetzt wurde (empirisch
    bestätigt: eine leere Fussnotenmarke allein genügt bereits, um die
    Schrift zu laden; ein Dokument ganz ohne jede Mathe-Berührung dagegen
    nicht). "nullfont" ist dann kein echter Schriftname und wird aus der
    erlaubten Liste entfernt, statt als (nie zutreffende) Familie
    mitgeführt zu werden."""
    b = Befund("A16", "Schriftinventar")
    if not r.has_sidecar:
        return _ohne_sidecar(b)
    erlaubt = [x for x in (r.mainfamily, r.condensedfamily, r.mathfont)
               + tuple(r.logofonts) if x and x != "nullfont"]
    erlaubt_basen = {_schriftbasis(x) for x in erlaubt}
    erlaubt_norm = [_normalisiere_schriftname(x) for x in erlaubt]
    gefunden = {c["fontname"] for seite in pdf.pages for c in seite.chars
                if c.get("fontname")}
    for fn in sorted(gefunden):
        basis = re.sub(r"^[A-Z]{6}\+", "", fn)
        basis_norm = _normalisiere_schriftname(basis)
        b.geprueft += 1
        if _schriftbasis(fn) in erlaubt_basen:
            continue
        if any(basis_norm in e or e in basis_norm for e in erlaubt_norm):
            continue
        b.verstoesse.append(
            f"Eingebettete Schrift '{fn}' passt zu keiner deklarierten "
            f"Familie ({', '.join(erlaubt) if erlaubt else 'keine erlaubt'})")
    return b


def pruefe_glossenlaenge(pdf, r: Raster, maxzeilen=6) -> Befund:
    """A17: Die Glossenzone trägt Beschriftung, nicht Fliesstext (I3).

    Gemessen wird der Sachverhalt, den I3 meint, und nicht der, den man
    gerne hätte: eine Glosse ist eine BESCHRIFTUNG, also von Etikettenlänge.
    Ein Glossenblock, der über sechs aufeinanderfolgende Zeilen läuft, ist
    kein Etikett mehr, sondern eine zweite Textspalte in einer Spalte, die
    dafür nicht gebaut ist -- 22 mm Glossenbreite tragen bei jedem
    realistischen Grad rund ein Dutzend Zeichen je Zeile.

    Erkannt wird an Ort und Grad, nicht am Befehl: alles links der Grenze
    zwischen Glossen- und Ziffernzone, unterhalb des Grundschriftgrads.
    Das erfasst \\marg und \\sidenote ebenso wie die Legenden von
    \\swisstable/\\swissfigure -- für alle gilt dieselbe Regel.
    Rahmenelemente (Titelblock, Kolophon) sind ausgenommen wie bei A7: sie
    laufen ausdrücklich über das volle Mass und ragen damit zwangsläufig in
    die Glossenzone hinein, ohne Glossen zu sein.

    Zusammenhängend heisst: der nächste Glossen-Grundlinie folgt höchstens
    zwei Rasterzeilen später (dieselbe Blocktrennung wie A13). Zwei kurze
    Glossen weit auseinander auf derselben Seite sind zwei Blöcke, kein
    langer."""
    b = Befund("A17", "Glossenlänge: Beschriftung statt Fliesstext")
    if not r.has_sidecar:
        return _ohne_sidecar(b)
    grenze = (r.outermargin + r.glosswidth) * MM
    schwelle = r.bodysize - 0.5
    for i, seite in enumerate(pdf.pages, 1):
        if vollflaechig(seite):
            continue
        zonen = rahmenzonen(seite, r)
        zaehler: dict[float, int] = {}
        for c in seite.chars:
            if not c.get("upright", True):
                continue
            if c.get("size", 99) >= schwelle:
                continue
            if c["x0"] >= grenze:
                continue
            if any(a <= c["top"] <= e for a, e in zonen):
                continue
            y = round(seite.height - c["matrix"][5], 2)
            zaehler[y] = zaehler.get(y, 0) + 1
        # Wie bei A13: nur Grundlinien mit genug Zeichen sind echte
        # Textzeilen, nicht einzelne verirrte Glyphen.
        baselinien = sorted(y for y, n in zaehler.items() if n >= 3)
        if not baselinien:
            continue
        block = [baselinien[0]]
        bloecke = [block]
        for y in baselinien[1:]:
            if y - block[-1] <= 2 * r.gridunit:
                block.append(y)
            else:
                block = [y]
                bloecke.append(block)
        for blk in bloecke:
            b.geprueft += 1
            if len(blk) > maxzeilen:
                b.verstoesse.append(
                    f"S.{i}: Glossenblock über {len(blk)} Zeilen "
                    f"(höchstens {maxzeilen}) -- Beschriftung kürzen oder "
                    f"in den Fliesstext verschieben")
    return b


def main() -> int:
    ap = argparse.ArgumentParser(description="SwissTeX-Konformitätsprüfung")
    ap.add_argument("pdf")
    ap.add_argument("--tex", help="Quelle, für die Prüfung A6")
    ap.add_argument("--params",
                     help="Kennzahlen-Sidecar-Datei (sonst automatisch als "
                          "<pdf-Stamm>.swisscheck neben der PDF gesucht); "
                          "aktiviert A10-A13/A15/A16/A17")
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

    basis = Raster(a.outermargin, a.margincolumn, a.gutter, a.numberzone,
                    a.textcolumn, a.topmargin, a.gridunit, a.bodysize)
    sidecar = lade_sidecar(a.params, a.pdf)
    r = Raster.from_sidecar(sidecar, basis) if sidecar is not None else basis

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
            pruefe_fusszeile(pdf, r),
            pruefe_kolumnentitel(pdf, r),
            pruefe_umschlag(pdf, r),
            pruefe_kommensurabilitaet(pdf, r),
            pruefe_farbrollen(pdf, r),
            pruefe_schriftinventar(pdf, r),
            pruefe_glossenlaenge(pdf, r),
        ]
        seiten = len(pdf.pages)

    print(f"\nswisscheck  {a.pdf}  ({seiten} Seiten)")
    print(f"Raster: Steg {r.outermargin:g} + Marginalie {r.margincolumn:g} + "
          f"Bund {r.gutter:g} + Satz {r.textcolumn:g} mm, "
          f"Zeile {r.gridunit_pt:g} pt")
    print(f"Kennzahlen-Sidecar: {'gefunden' if sidecar is not None else 'keine (A10-A13/A15/A16/A17 übersprungen)'}\n")
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
