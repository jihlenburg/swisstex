# SwissTeX

Eine XeLaTeX-Dokumentklasse für Sachtexte nach der Neuen Schweizer Schule
(Müller-Brockmann): ein echtes Basislinienraster, eine Marginalspalte, die
nur Beschriftung trägt, ein Prüfskript, das die Einhaltung am fertigen PDF
misst, und -- seit 2.0 -- eine Identitätsschicht, über die ein Dokument
Farbe, Schrift, Logo und Klassifizierungsvokabular bezieht, ohne die Klasse
selbst zu ändern.

Version 2.1.0 · XeLaTeX · MIT (Klasse und Werkzeuge) + AFPL (Schrift, siehe
unten)

---

## Was das System leistet

Der gesamte Satzspiegel wird aus zehn Kennzahlen abgeleitet: Papierbreite
und -höhe, Steg, Marginalspalte, Bund, Ziffernzone, Satzspiegel, oberer
Steg, Rasterzeilenzahl und Rastermass (siehe `swisstex-manual.tex`,
Abschnitt "Invarianten"). Rechte und untere Stege sind berechnet, nicht
gesetzt. Wer eine Kennzahl ändert, ändert das System konsistent mit. Diese
zehn sind der geometrische Kern; die Klasse kennt insgesamt 29
Klassenoptionen (Kennzahlen plus Farbrollen, Schriftdateien, Sprache,
Verhalten -- siehe die Optionstabelle im Handbuch).

Sechs Invarianten:

| | Regel |
|---|---|
| I1 | Jeder vertikale Abstand ist ein ganzzahliges Vielfaches des Rastermasses |
| I2 | Linien und Satzblöcke stehen auf der Textachse; nur ausdrücklich als Rahmen deklarierte Elemente (Titel, Umschlag, Kolophon, Farbfelder) laufen über das volle Mass |
| I3 | Die Marginalspalte trägt nur Beschriftung, nie Satzmaterial; links die Glossen, rechts die Ziffern |
| I4 | Eine Schriftfamilie, Differenzierung über Schnitt, Grad und Weite (`\condensed`) |
| I5 | Flattersatz mit Trennung und optischem Randausgleich |
| I6 | Überschriften hängen am nachfolgenden Block, nie am Seitenfuss |

---

## Die Identitätsschicht

Seit Version 2.0 ist die Klasse nicht mehr die ganze Geschichte für sich:
Sie ist der alleinige *Durchsetzungspunkt* einer kleinen Identitätsschicht.
Ein Dokument fügt `identity=<name>` als Klassenoption hinzu und lädt damit
`swissidentity-<name>.sty` -- ein Paket, das Farbrollen, Schriften,
Logodateien, Klassifizierungsvokabular und die Fusszeilenvorlage
ausschliesslich über öffentliche Setzer bindet, nie durch Eingriffe in die
Klasse selbst:

| Setzer | Bindet |
|---|---|
| `\swissidentitymeta` | Firma, Impressum, Web |
| `\swisssetcolors` | `accent`/`paper`/`ink`, optional `band` (leer = Alias von `accent`, ein Signalfarben-System) |
| `\newcommand{\swissidentityfonts}{...}` | den Schriftlieferanten -- muss `\condensed` mit `\renewfontfamily` erneuern (I4); `\swisscodeface`, der Code-Begleiter, ist ebenso überschreibbar, aber optional |
| `\swisslogofiles` | `cover=`/`colophon=`-Logodateien plus `logofonts=` (Fremdschriften, die ein eingebundenes Logo mitbringt) |
| `\swissclassifications` | das geordnete Klassifizierungsvokabular |
| `\swissfootformat` | die Fusszeilenvorlage (`\meta{key}`-Platzhalter) |
| `\swisscovervariant` | benannte `\swisscover*`-Vorgaben |

`swissidentity-acme.sty` ist die Referenzidentität -- `acme` ist ein
neutraler Platzhalter, nie eine reale Firma -- und `acme-demo.tex`/`.pdf`
ihr durchexerziertes Beispiel, das jeden öffentlichen Setzer einmal benutzt.
Ein Dokument ohne `identity=` kann dieselben Setzer auch direkt in der
Präambel aufrufen; nur ist die Wirkung dann nicht für Wiederverwendung
verpackt.

---

## Dateien

| Datei | Zweck |
|---|---|
| `swisstex.cls` | die Dokumentklasse |
| `swisscheck.py` | typografische Konformitätsprüfung der PDF-Ausgabe (A1-A18) |
| `sprachcheck.py` | Lesbarkeitsprüfung der `.tex`-Quelle (S1-S9) |
| `swisstex-manual.tex/.pdf` | Dokumentation, mit der Klasse selbst gesetzt, zweifach durchlaufen |
| `swisstex-demo.tex/.pdf` | Minimalbeispiel mit sichtbar unterlegtem Raster |
| `swissidentity-acme.sty` | Referenzidentität |
| `acme-demo.tex/.pdf` | Beispieldokument der Identitätsschicht |
| `tests/` | pytest-Prüfbaum: baut jedes Referenzdokument und jede Regressionsvorlage und prüft PDF, Log und Sidecar |
| `tests/fixtures/stress.tex` | Regressionstest: Listen, Fussnoten, Zitat, Verbatim, Seitenumbruch |
| `tests/fixtures/figure.tex` | Regressionstest: Abbildungsblock |
| `tests/fixtures/display.tex` | Regressionstest: Umschlag (Slot-Form), Schaugrade, Farbfeld |
| `fonts/` | SwissTeX Grotesk (modifiziertes URW U001, AFPL) samt Bauwerkzeug |
| `Makefile` | `make all`, `make check`, `make report`, `make dist` |

---

## Installation

Voraussetzungen über eine Basis-TeX-Live-Installation hinaus: `tex-gyre`
(TeX Gyre Heros als Univers-Analogon), `tex-gyre-math` (liefert
`texgyredejavu-math.otf`, Familienname "TeX Gyre DejaVu Math"), `dejavu`
(liefert `DejaVuSansMono.ttf` in vier Schnitten, Familienname "DejaVu Sans
Mono" -- Vorgabe für `codeface`, den Code-Begleiter), `titlesec`,
`needspace`, `enumitem`, `marginfix` (hält Marginalien im Satzspiegel,
siehe Abschnitt "Marginalien" unten), deutsche Trennmuster
(`texlive-lang-german`), Python 3 mit `pdfplumber` für `swisscheck.py`.

```
tlmgr install tex-gyre tex-gyre-math dejavu titlesec needspace enumitem marginfix
```

An `tlmgr init-usertree` und `--usermode` anhängen, falls der Systembaum
nicht beschreibbar ist. Das Paket `dejavu-otf` wird NICHT gebraucht -- es
enthält nur die alte `.sty`-Unterstützung, nicht die Mathematikschrift; das
hier installierte Paket heisst `dejavu` (ohne `-otf`) und liefert die
TrueType-Dateien, die `codeface` per Familienname lädt.

**macOS-Eigenheit:** Die Klasse lädt die Grundschrift über den Dateinamen
(über kpathsea, funktioniert aus jedem texmf-Baum), die Mathematik- und
die Code-Begleiterschrift aber über den Familiennamen (`\setmathfont` bzw.
`\swisscodeface`, siehe `codeface`), und XeTeX löst Familiennamen unter
macOS über CoreText auf, das texmf-Bäume nicht sieht. Die namentlich
geladenen Schriften -- `texgyreheros-*.otf` (für die
`range=\mathup`/`\mathit`-Ladungen), `texgyredejavu-math.otf` und die vier
Schnitte von `DejaVuSansMono*.ttf` -- müssen darum zusätzlich nach
`~/Library/Fonts/` kopiert werden, sonst bricht der Bau bei `\setmathfont`
bzw. beim ersten `\swisscodeface`-Aufruf (verbatim/`\verb`) ab, obwohl
`kpsewhich` die Dateien findet. In dieser Umgebung reichte das blosse
Kopieren nicht sofort: CoreTexts Schriftregistrierung (`fontd`) hatte die
frisch kopierten DejaVu-Sans-Mono-Dateien zunächst nicht gesehen, obwohl
`fc-list`/`mdls` sie bereits kannten -- `killall fontd` gefolgt von
`mdimport -r` auf jede `.ttf`-Datei hat das Zwischenspeicherproblem
behoben. Dieselbe Eigenheit trifft eine Identität, deren
`\swissidentityfonts` ebenfalls über den Familiennamen statt über den
Dateinamen lädt -- `swissidentity-acme.sty` ruft `\setmainfont{SwissTeX
Grotesk}` auf, darum muss auch `fonts/dist/SwissTeXGrotesk*.ttf` dort
liegen (siehe unten, `make install` im Bau der Schrift).

```
cp swisstex.cls <projektverzeichnis>/
xelatex dokument.tex
```

Zwei Durchläufe, sobald Querverweise oder Lesezeichen verwendet werden.

### SwissTeX Grotesk bauen

Die Referenzidentität `acme` braucht die klasseneigene Schrift SwissTeX
Grotesk -- ein modifiziertes URW U001 (AFPL-lizenziert, siehe Lizenzabschnitt
unten), nicht in `swisstex.cls` selbst voreingestellt (die lädt vorgabemässig
TeX Gyre Heros, MIT-frei). Gebaut wird aus `fonts/`:

```
python3 -m venv fonts/.venv && fonts/.venv/bin/pip install fonttools pytest pdfplumber
fonts/.venv/bin/python fonts/tools/build.py            # -> fonts/dist, alle acht Schnitte
fonts/.venv/bin/python fonts/tools/build.py install    # -> ~/Library/Fonts (macOS)
```

Details zur Herkunft und den angewendeten Korrekturen: `fonts/README.md`.

---

## Kennzahlen

```latex
\documentclass[gridunit=13.5pt, bodysize=9.5pt, textcolumn=105mm]{swisstex}
```

| Option | Vorgabe | Wirkung |
|---|---|---|
| `gridunit` | 13.5pt | Basislinienraster und Durchschuss |
| `bodysize` | 9.5pt | Grundschriftgrad |
| `outermargin` | 24mm | Steg links des Rasters |
| `margincolumn` | 30mm | Marginalspalte |
| `gutter` | 7mm | Bund zwischen den Spalten |
| `numberzone` | 8mm | rechte Zone der Marginalspalte, den Gliederungsziffern vorbehalten |
| `textcolumn` | 105mm | Satzspiegel, zugleich Textachse |
| `topmargin` | 26mm | oberer Steg |
| `gridlines` | 51 | Rasterzeilen je Seite, bestimmt die Satzhöhe |
| `annotationleading`, `glossleading`, `footnoteleading` | leer (2/3, 3/4, 3/4 Rastermass) | Nebentext-Durchschüsse, einzeln überschreibbar |
| `accent` | 255,55,37 | Signalfarbe als RGB-Tripel |
| `band` | leer (= `accent`) | Farbe der Farbfelder; ein eigener Wert bricht mit dem Ein-Signalfarben-System |
| `paper` | 234,232,208 | Grundton der Seite |
| `ink` | 26,26,26 | Textfarbe |
| `tint` | false | Grundton flächig über alle Seiten anlegen |
| `lang` | german | Sprache für Trennung und Zeichenketten |
| `showgrid` | false | Raster und Spaltenkanten sichtbar unterlegen |
| `rules` | true | Haarlinie vor Abschnitten |
| `sans`, `sanscondensed` | texgyreheros, texgyreheroscn | Schriftdateien |
| `sansname`, `sansnameitalic` | TeX Gyre Heros | Familiennamen für den Formelsatz |
| `mathfont` | TeX Gyre DejaVu Math | Mathematikschrift |
| `codeface` | DejaVu Sans Mono | Code-Begleiterschrift für `verbatim`/`\verb` (I4, siehe unten) |
| `identity` | leer | lädt `swissidentity-<name>.sty` (siehe oben) |

Die vollständige Tabelle aller 29 Optionen steht in `swisstex-manual.tex`,
Abschnitt "Klassenoptionen" -- `swisstex.cls` Abschnitt 1 ist die
Quelle der Wahrheit, die Tabelle folgt ihr.

---

## Schnittstelle

```latex
\documentclass{swisstex}
\setrunningtitle{Kurztitel für den Kolumnentitel}

\begin{document}
\swisstitle*{kicker=Kennzeichnung, title=Titel, subtitle=Untertitel}

\begin{lead}
Vorspann, ein Grad grösser als der Grundtext.
\end{lead}

\section{Abschnitt}          % Haarlinie wird automatisch gesetzt
\subsection{Unterabschnitt}

Fliesstext. \marg{Randglosse in der Marginalspalte}

\begin{swisstable}{Legende der Tabelle}
\begin{tabularx}{\textcolumn}[t]{@{}S{30mm}@{\hspace{4mm}}L@{}}
\toprule
\tabhead{Merkmal} & \tabhead{Beschreibung} \\
\midrule
Erstes & Text \\
\bottomrule
\end{tabularx}
\end{swisstable}

\begin{gridblock}            % alles, was keine Rasterhöhe hat
\begin{equation*}
  \gamma = \frac{\mathrm{d}n/\mathrm{d}T}{n-1} - \alpha .
\end{equation*}
\end{gridblock}

\colophon{Angaben zum Satz.}
\end{document}
```

Kräftige Ebene: `\swisscover*{kicker=..., title=..., subtitle=..., foot=...,
client=..., docid=..., date=..., glyph=..., glyphink=..., glyphline=..., glyphlines=...,
logo=..., band=<start>/<lines>, variant=...}` für eine randabfallende Umschlagseite,
vollständig rastergebunden -- kein Seitenanteil mehr, weder für das
Farbband noch für ein Überformatzeichen. Die alte Positionsform
`\swisscover{K}{T}{U}{F}` bleibt nutzbar, meldet aber eine
Abkündigungswarnung (`\ClassWarning`); dieselbe Rückwärtskompatibilität
gilt für `\swisscoverglyph`, `\swisscoverglyphx`, `\swisscoverglyphy`,
`\swisscoverglyphsize` (wirkungslos, warnen beim Aufruf). `swissband` für
ein Farbfeld über das volle Mass mit weissem Satz, `\swissdisplay{n}` für
einen Schaugrad mit n Rasterzeilen Durchschuss, `\sectionnumberstyle`,
`\swissbandpadding` (Innenabstand des Feldes) und `\swissbandlead`
(Blindzeilen über dem Feld, voreingestellt eine).

Weitere Bausteine: `swissfigure{Legende}` als Gegenstück zu `swisstable`,
`\swisslogo[lines=n, axis=text|full]{datei}` für ein Bild als Satzblock,
`\sidenote{...}` als nummerierte Randnotiz statt Fussnote, `\gridskip{n}`
für n Rasterzeilen Raum, `\snaptogrid{...}` als Befehlsform von
`gridblock`, `\tracked{...}` für gesperrte Versalien, `\marginlabel{...}`
für hängende Beschriftung sowie die Längen `\textcolumn`, `\fullmeasure`,
`\measureshift` und `\gridunit`.

Für `quote`, `quotation`, `verbatim`, `description` und die abgesetzten
Formelumgebungen von `amsmath` setzt die Klasse den Rasterfang automatisch
dahinter; abgesetzte Formeln brauchen also kein `gridblock` mehr. Eigene
oder fremde Umgebungen lassen sich mit `\gridsnapenv{name}` nachtragen oder
mit einem `\gridsnap` dahinter behandeln.

Spaltentypen für Tabellen: `L` dehnbar im Flattersatz, `S{Breite}` fest im
Flattersatz, `R{Breite}` fest rechtsbündig. Senkrechte Linien sind nicht
vorgesehen.

**Das `[t]` in `tabularx` ist zwingend**, sonst fluchtet die Legende auf die
Tabellenmitte statt auf die Kopfzeile. `tabularx` lässt sich nicht in eine
eigene Umgebung wickeln, weil es seinen Rumpf bis zum wörtlichen
`\end{tabularx}` einliest.

### Marginalien im Satzspiegel

`marginfix` (siehe Installation) hält Randglossen dort, wo sie hingehören:
Ragt eine mit `\marg`/`\sidenote` gesetzte Glosse am Seitenende über die
Satzspiegel-Unterkante hinaus, schiebt marginfix sie nach oben, bis ihre
Unterkante auf der Unterkante liegt. `swisscheck` A18 misst genau das im
fertigen PDF.

---

## Typografische Prüfung: `swisscheck.py`

```
python3 swisscheck.py dokument.pdf --tex dokument.tex
make check                      # alle Referenzdokumente, Fixtures, pytest, sprachcheck
```

| | Prüfung |
|---|---|
| A1 | Achsentreue: Linien stehen auf der Textachse oder auf vollem Mass |
| A2 | Rasterbindung: Grundtextzeilen liegen auf dem Basislinienraster |
| A3 | Satzspiegel: kein Satz läuft über den rechten Rand hinaus |
| A4 | Marginalspalte: trägt nur Beschriftung, kein Satzmaterial |
| A5 | Legendenflucht: Tabellenlegende fluchtet mit der ersten Tabellenlinie |
| A6 | Seitenfuss: keine Überschrift am unteren Seitenende |
| A7 | Marginalzonen: Glossen- und Ziffernzone der Marginalspalte trennen sich |
| A8 | Zeilenanfang: kein Absatz beginnt mit unbeabsichtigtem Einzug |
| A9 | Figurenlegende: Abbildungslegende fluchtet mit der Abbildungsoberkante |
| A10 | Fusszeile: Grundlinie auf dem Rasterfusspunkt, Klassifizierung und Metadaten je in eigener Zone |
| A11 | Kolumnentitel: Pagina im Grundschriftgrad, Grundlinie auf der verlängerten Rasterzeile, bildfreie Kopfzone |
| A12 | Umschlag: Farbband auf Rasterzeilen, Schriftgrade aus der Anzeigenskala, Überformatzeichen an Rasterzeile und Textachse |
| A13 | Kommensurabilität: die deklarierten Nebentext-Durchschüsse sind kleine Brüche des Rastermasses, der gemessene Durchschuss trifft einen davon |
| A15 | Farbrollen: ein eigenständiges Band unterscheidet sich von der Signalfarbe, das gedruckte Band trägt den deklarierten Ton |
| A16 | Schriftinventar: nur deklarierte Schriftfamilien sind eingebettet |
| A17 | Glossenlänge: die Glossenzone trägt Beschriftung, nicht Fliesstext (I3) -- kein Glossenblock über sechs Zeilen |
| A18 | Marginalien im Satzspiegel: keine Glosse ragt unter die Satzspiegel-Unterkante (marginfix, siehe oben) |

(A14, zweisprachiger Satz, ist für eine spätere Ausbaustufe vorgesehen und
noch nicht implementiert.)

A1 nimmt Zeichnungen aus: ein Band mit nicht-waagerechtem Vektorinhalt
(Kurven, Schrägen) gilt als Zeichnung, dort sind Striche Inhalt statt
Layout. Eine Schwimmbahn oder Diagrammachse darf also neben der Textachse
liegen.

Seit Version 2.0 schreibt die Klasse bei jedem Bau eine
Kennzahlen-Sidecar-Datei (`<jobname>.swisscheck`, `\AtEndDocument`) mit den
*deklarierten* Werten des Dokuments -- Raster, die drei
Nebentext-Durchschüsse, Kopf-/Fusszonen, Farbrollen, Schriftfamilien,
Klassifizierung, Dokumentkennung. `swisscheck.py` findet sie automatisch
neben der geprüften PDF (`--params` für einen abweichenden Pfad) und prüft
dann A1-A18 gegen diese deklarierten Werte statt gegen feste
Kommandozeilen-Annahmen. Fehlt die Sidecar-Datei (ältere PDFs), fallen A1-A9
und A18 auf die Kommandozeilen-Vorgabe zurück, A10-A13/A15-A17 überspringen
sich sauber (0 geprüft, kein Fehler). Abweichende Rastervorgaben über
Schalter: `--gridunit`, `--textcolumn`, `--margincolumn`, `--gutter`,
`--numberzone`, `--outermargin`, `--topmargin`, `--bodysize`.

Rückgabewert 0 bei bestandener Prüfung, sonst 1, damit sich der Aufruf in
eine Bauautomatik einhängen lässt.

---

## Lesbarkeitsprüfung: `sprachcheck.py`

Seit 2026-08-05 prüft `--lang en` englische Quellen nach dem Profil
Swiss Technical English (hart: 35-Wort-Satz, Semikola, Em-Dashes, dazu
warnende Messungen für Patter, Passivanteil, schwache Auftakte und
UK-Schreibformen). Vorgabe bleibt das deutsche Profil S1 bis S9.

```
python3 sprachcheck.py dokument.tex -v
```

Neun Prüfungen S1 bis S9, analog zu den Typografieprüfungen. Gemessen wird
der Fliesstext; Tabellen, Formeln, Marginalien und Codeblöcke sind
ausgenommen (Marginalien werden separat mit S6 geprüft -- S6 ergänzt
`swisscheck` A17: A17 misst am gesetzten PDF, ob ein Glossenblock über
sechs Zeilen läuft, S6 misst dieselbe Anforderung an der Quelle, in Wörtern
statt Zeilen). Hart sind S1, S7, S8, alles andere warnt; die Schwellen sind
auf technische Fachprosa ausgelegt, nicht auf leichte Sprache.

| | Prüfung | |
|---|---|---|
| S1 | Kein Satz über 40 Wörter | hart |
| S2 | Höchstens 8 % der Sätze über 30 Wörter | weich |
| S3 | LIX im Band 45 bis 62 | weich |
| S4 | Nominalisierungen unter 8 je 100 Wörter | weich |
| S5 | Satzlängen-Streuung mindestens 6 (Rhythmus) | weich |
| S6 | Marginalien höchstens 22 Wörter | weich |
| S7 | Keine Geviertstriche (— oder ---) | hart |
| S8 | Keine Semikola im Fliesstext | hart |
| S9 | Höchstens 3 Klammerpaare je 1000 Wörter | weich |

Rückgabewert 0, wenn alle harten Prüfungen bestehen, sonst 1.

---

## Prüfbaum: `tests/`

```
fonts/.venv/bin/pytest tests/ -q
```

Die venv unter `fonts/.venv` trägt `pdfplumber`; ein blosses System-`pytest`
hat es nicht. Der Baum baut jedes Referenzdokument und jede
Regressionsvorlage mit `xelatex` und prüft PDF, Log und Sidecar --
Fehlerpfade, Schriftersatz, Zeichenketten-Rückfall und mehr, nicht nur, was
`swisscheck.py` misst. `tests/fixtures/` enthält die Bauvorlagen:
kuratierte v2.0-Fixtures für einzelne Merkmale sowie drei aus
Produktionsgebrauch portierte Regressionsvorlagen (`stress.tex`,
`figure.tex`, `display.tex`), die Randfälle abdecken, die die kuratierten
Fixtures nicht berühren -- verschachtelte Listen, ein Seitenumbruch mitten
im Absatz, ein Rahmenplatzhalter, ein Umschlag in der modernen Slot-Form.
Es dauert (ein echter `xelatex`-Bau je Test, keine Attrappe), etwa zwei
Minuten für den ganzen Baum.

---

## `make`-Ziele

| Ziel | Wirkung |
|---|---|
| `make all` | baut alle Referenzdokumente und Regressionsvorlagen (zweifach, für Querverweise) |
| `make check` | `all`, dann `swisscheck.py` je Dokument, `pytest tests/ -q`, `sprachcheck.py` je Referenzdokument -- Rückgabewert 1, sobald irgendetwas scheitert |
| `make report` | `all`, dann die volle `swisscheck.py`-/`sprachcheck.py`-Ausgabe je Dokument |
| `make clean` | löscht Baureste (`.aux`/`.log`/`.out`/`.toc`, Fixture-PDFs und -Sidecars) |
| `make dist` | `check`, `clean`, dann ein Archiv aus Klasse, Prüfwerkzeugen, den drei Referenzdokumenten samt PDF und der Referenzidentität `acme` -- kein Produktionsinhalt |

---

## Zur Umsetzung des Rasters

Das eigentliche Problem ist nicht das Setzen der Abstände, sondern das
Zurückgeben des Rasters nach einem Block, dessen Höhe kein Vielfaches des
Rastermasses hat. Blosses Aufrunden der Blockhöhe genügt nicht: TeX fügt
beim Anhängen einer Box Zeilenausgleich ein, dessen Betrag von der Tiefe der
Vorzeile abhängt, und beim Seitenumbruch greift statt dessen `\topskip`.
`\prevdepth` lässt sich nicht dauerhaft zuweisen, weil die Grösse
gruppenlokal ist und das schliessende `\endgroup` der Umgebung sie
zurücksetzt.

SwissTeX packt Blöcke deshalb so um (`\swiss@placebox`), dass sie sich wie
ganze Zeilen verhalten: Oberkante auf Struthöhe, Tiefe auf ein Vielfaches
des Rastermasses aufgefüllt, dahinter eine unsichtbare Zeile mit
Standardtiefe. Damit rechnet der normale Zeilenausgleich mitten auf der
Seite genauso wie am Seitenanfang, wo `\topskip` auf genau eine Rasterzeile
gesetzt ist. Alle Blöcke laufen über denselben Weg, auch die Haarlinie vor
Abschnitten.

Wer eigene Messungen anstellt, muss zwischen TeX-Punkt (1/72,27 Zoll) und
DTP-Punkt (1/72 Zoll) umrechnen. Ohne diesen Faktor erscheint jedes korrekte
Raster als wegdriftend, mit etwa 0,05 pt je Zeile.

---

## Grenzen

- Die Rasterbindung gilt für den Grundtext. Tabellenkörper, Fussnoten und
  Randglossen laufen bewusst auf eigenem Durchschuss und stehen innerhalb
  ihres Blocks auf eigenem Mass; nach aussen bleibt der Block rastertreu.
- Die Marginalspalte trägt Beschriftung, nicht Fliesstext (I3): 22 mm
  Glossenbreite tragen rund zwölf Zeichen je Zeile, weit unter der
  Lesbarkeitsschwelle für laufenden Satz. `swisscheck` A17 hält das fest.
- Gleitobjekte sind nicht vorgesehen: sie vertragen sich weder mit dem
  Basislinienraster noch mit der Marginalspalte. Abbildungen stehen dort,
  wo sie geschrieben sind.
- Der Fussnotenbereich am Seitenfuss folgt einem eigenen Mass.
- Satz in Farbfeldern ist Rahmensatz: er folgt dem Feld, nicht dem
  Seitenraster, und die Spaltenregel gilt in ihm nicht. `swisscheck` nimmt
  Farbfelder und randabfallende Umschlagseiten entsprechend aus.
- `verbatim` und `\verb` laufen auf `\swisscodeface`, dem zweiten
  deklarierten Begleiter neben der Mathe-Schrift (I4, Vorgabe `codeface` =
  DejaVu Sans Mono); `\swisscode` bleibt für Bezeichner mitten im Fliesstext
  auf `\condensed`. Nicht erfasste Fremdumgebungen können das Raster
  verschieben, bis sie über `\gridsnapenv` nachgetragen sind.
- Die Klasse setzt XeLaTeX voraus (OpenType, `fontspec`, `unicode-math`).
- Univers selbst ist nicht frei. TeX Gyre Heros (MIT-verwandt, siehe unten)
  steht vorgabemässig als Analogon aus der Nimbus-Sans-Linie an seiner
  Stelle; SwissTeX Grotesk (AFPL) ist die klasseneigene Alternative.

---

## Lizenz

Gemischt, nicht einheitlich: **MIT** deckt Code und Dokumentation --
`LICENSE`, den Kopf von `swisstex.cls`, `swisscheck.py`, `sprachcheck.py`,
`fonts/tools/`, `fonts/tests/`, dieses Dokument, die Vorlagen von Handbuch
und Beispielen. Die Schriftbinärdateien unter `fonts/`
(`fonts/sources/u001/`, `fonts/dist/`) sind von URW U001 abgeleitet und
**AFPL**-lizenziert (siehe `fonts/sources/u001/Copying.AFPL.txt`) -- nie
MIT. TeX Gyre Heros, die vorgabemässige Grundschrift, ist über das
GUST-Font-License-Projekt frei (LPPL-verwandt, ausserhalb dieses
Repositoriums gepflegt).
