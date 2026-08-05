%% swisstex.cls
%% Dokumentklasse fuer Sachtexte nach der Neuen Schweizer Schule.
%%
%% Entwurfsprinzip: Der gesamte Satzspiegel wird aus wenigen Kennzahlen
%% abgeleitet. Es gibt keine handgesetzten Abstaende. Wer eine Kennzahl
%% aendert, aendert das ganze System konsistent mit.
%%
%% Grundinvarianten
%%   I1  Jeder vertikale Abstand ist ein ganzzahliges Vielfaches von \gridunit.
%%   I2  Jede Linie und jeder Satzblock steht auf der Textachse.
%%       Ausnahme sind ausdruecklich als Rahmen deklarierte Elemente
%%       (Titel, Kolophon), die ueber das volle Mass laufen.
%%   I3  Die Marginalspalte traegt nur Beschriftung, nie Satzmaterial.
%%   I4  Eine Schriftfamilie. Differenzierung ueber Schnitt, Grad, Weite.
%%   I5  Flattersatz mit Trennung und optischem Randausgleich.
%%   I6  Ueberschriften haengen am nachfolgenden Block, nie am Seitenfuss.
%%
%% Lizenz: MIT (siehe LICENSE)
%% ---------------------------------------------------------------------

\NeedsTeXFormat{LaTeX2e}
\ProvidesClass{swisstex}[2026/08/05 v2.1.0 Swiss typographic grid]

\RequirePackage{iftex}
\RequireXeTeX

% ---------------------------------------------------------------------
% 1  Kennzahlen
% ---------------------------------------------------------------------
\RequirePackage{kvoptions}
\SetupKeyvalOptions{family=swiss,prefix=swiss@}

\DeclareStringOption[13.5pt]{gridunit}     % Basislinienraster
\DeclareStringOption[9.5pt]{bodysize}      % Grundschriftgrad
\DeclareStringOption[210mm]{paperwidth}
\DeclareStringOption[297mm]{paperheight}
\DeclareStringOption[24mm]{outermargin}    % Steg links vom Raster
\DeclareStringOption[30mm]{margincolumn}   % Marginalspalte
\DeclareStringOption[7mm]{gutter}          % Bund zwischen den Spalten
\DeclareStringOption[8mm]{numberzone}      % rechte Zone; zwei Stellen brauchen 7mm
\DeclareStringOption[105mm]{textcolumn}    % Satzspiegel = Textachse
\DeclareStringOption[26mm]{topmargin}
\DeclareStringOption[51]{gridlines}        % Rasterzeilen je Seite
\DeclareStringOption[255,55,37]{accent}    % Signalfarbe, RGB-Tripel
% v2.0: Vorgabe jetzt leer statt 255,105,91 -- eine ausdruecklich gesetzte
% Option ueberschreibt weiterhin \swiss@bandvalue (siehe Abschnitt 2b,
% v1.3-Bruecke); leer heisst seither "band = accent" (eine Signalfarbe,
% M-B-Regel gegen ein zweites, unmotiviertes Rot).
\DeclareStringOption[]{band}              % leer = accent (eine Farbe)
\DeclareStringOption[234,232,208]{paper}  % Grundton der Seite
\DeclareStringOption[26,26,26]{ink}       % Textfarbe
\DeclareBoolOption[false]{tint}           % Grundton flaechig anlegen
\DeclareStringOption[german]{lang}
\DeclareBoolOption[false]{showgrid}        % Raster sichtbar machen
\DeclareBoolOption[true]{rules}            % Haarlinie vor Abschnitten
\DeclareStringOption[texgyreheros]{sans}          % Dateibasis
\DeclareStringOption[texgyreheroscn]{sanscondensed}
\DeclareStringOption[TeX Gyre Heros]{sansname}    % Familienname fuer Mathe
\DeclareStringOption[TeX Gyre Heros Italic]{sansnameitalic}
\DeclareStringOption[TeX Gyre DejaVu Math]{mathfont}
% Code-Begleiterschrift (I4, Nutzerentscheid 2026-07-31): siehe den
% ausfuehrlichen Kommentar bei \swisscodeface in Abschnitt 3. DejaVu Sans
% Mono ist frei, stammt aus demselben Projekt wie die Mathe-Schrift und
% traegt ein grotesk-verwandtes Skelett -- passender Vorgabewert fuer den
% zweiten deklarierten Begleiter neben der Mathe-Schrift.
\DeclareStringOption[DejaVu Sans Mono]{codeface}
\DeclareStringOption[]{annotationleading} % leer = 2/3 Rastermass
\DeclareStringOption[]{glossleading}      % leer = 3/4 Rastermass
\DeclareStringOption[]{footnoteleading}   % leer = 3/4 Rastermass
\DeclareStringOption[]{identity}          % Name der Identitaetsdatei (leer = keine)
\DeclareDefaultOption{\PassOptionsToClass{\CurrentOption}{article}}
\ProcessKeyvalOptions*

\LoadClass[10pt]{article}

% ---------------------------------------------------------------------
% 2  Abgeleitete Masse
% ---------------------------------------------------------------------
\RequirePackage{calc}

\newlength{\gridunit}     \setlength{\gridunit}{\swiss@gridunit}

% Nebenmasse: Durchschuss der Nebentexte als starke Rasterbrueche (3:2, 4:3).
% Ueberschreibbare Kennzahlen; leere Option leitet aus dem Raster ab.
\newlength{\annotationleading}
\ifx\swiss@annotationleading\@empty
  \setlength{\annotationleading}{\dimexpr2\gridunit/3\relax}
\else\setlength{\annotationleading}{\swiss@annotationleading}\fi
\newlength{\glossleading}
\ifx\swiss@glossleading\@empty
  \setlength{\glossleading}{\dimexpr3\gridunit/4\relax}
\else\setlength{\glossleading}{\swiss@glossleading}\fi
\newlength{\footnoteleading}
\ifx\swiss@footnoteleading\@empty
  \setlength{\footnoteleading}{\dimexpr3\gridunit/4\relax}
\else\setlength{\footnoteleading}{\swiss@footnoteleading}\fi
% Die swiss:*-Zeilen im Log sind eine reine Baubeobachtung fuer die
% Testsuite (tests/test_doctrine.py liest sie, weil sie schon vor
% \begin{document} feststehen). Kanonisch ist die Kennzahlen-Sidecar-Datei
% aus Abschnitt 14a -- sie traegt die AUFGELOESTEN Werte des fertigen
% Dokuments und ist das, was swisscheck liest. Wer eine Kennzahl nachtraegt,
% traegt sie dort ein; ein zusaetzliches \typeout ist optional.
\typeout{swiss:annotationleading=\the\annotationleading}
\typeout{swiss:glossleading=\the\glossleading}
\typeout{swiss:footnoteleading=\the\footnoteleading}

\newlength{\margincolumn} \setlength{\margincolumn}{\swiss@margincolumn}
\newlength{\gutter}       \setlength{\gutter}{\swiss@gutter}
\newlength{\numberzone}   \setlength{\numberzone}{\swiss@numberzone}
% Randglossen enden vor der Ziffernzone, damit sich beide nicht beruehren,
% falls sie doch einmal auf derselben Zeile stehen.
\newlength{\glosswidth}
\setlength{\glosswidth}{\margincolumn-\numberzone}
\newlength{\textcolumn}   \setlength{\textcolumn}{\swiss@textcolumn}

% Volles Mass: Marginalspalte + Bund + Satzspiegel. Nur fuer Rahmenelemente.
\newlength{\fullmeasure}
\setlength{\fullmeasure}{\margincolumn+\gutter+\textcolumn}
% Versatz, um von der Textachse auf das volle Mass auszubrechen.
\newlength{\measureshift}
\setlength{\measureshift}{-\margincolumn-\gutter}
% Innerer Steg bis zur Textachse.
\newlength{\innermargin}
\setlength{\innermargin}{\swiss@outermargin+\margincolumn+\gutter}
% Satzhoehe = Rasterzeilen mal Rastermass.
\newlength{\swiss@textheight}
\setlength{\swiss@textheight}{\swiss@gridlines\gridunit}

\RequirePackage{geometry}
\geometry{
  paperwidth  = \swiss@paperwidth,
  paperheight = \swiss@paperheight,
  left        = \innermargin,
  right       = \swiss@paperwidth-\innermargin-\textcolumn,
  top         = \swiss@topmargin,
  textheight  = \swiss@textheight,
  marginparwidth = \glosswidth,
  marginparsep   = \dimexpr\gutter+\numberzone\relax,
  headsep     = \dimexpr2\gridunit\relax,
  footskip    = \dimexpr3\gridunit\relax}
\typeout{swiss:headsep=\the\dimexpr2\gridunit\relax}
\typeout{swiss:footskip=\the\dimexpr3\gridunit\relax}
\reversemarginpar
% marginfix haelt Marginalien im Satzspiegel: ragt eine Glosse am Seitenende
% ueber die Unterkante hinaus, wird sie nach oben geschoben, bis ihre
% Unterkante auf der Satzspiegel-Unterkante liegt. Pruefung A18 misst das.
\RequirePackage{marginfix}

% ---------------------------------------------------------------------
% 2a  Sprachtabelle
% Alle sichtbaren Zeichenketten laufen ueber \swiss@str{key} statt ueber
% fest verdrahtete Woerter. Sprachen definieren sich ueber \swisssetstrings
% (oeffentliche Schnittstelle, in Praeambel oder Identitaetsdatei nutzbar,
% Wirkung global). Ein unbekannter Schluessel ist ein Fehler -- seit dieser
% Ueberarbeitung bereits zur DEFINITIONSZEIT in \swisssetstrings
% (Spezifikation 4.2), nicht erst beim Nachschlagen; die Schluesselmenge
% laesst sich mit \swissstringkeys erweitern. Eine unbekannte Sprache
% faellt mit Warnung auf english zurueck -- die Warnung erscheint EINMAL
% JE SPRACHE UND SCHLUESSEL (siehe \swiss@str@warn; der frueher hier
% stehende Kommentar "einmalig" traf nicht zu, die Warnung lief bei jeder
% Verwendungsstelle erneut).
%
% \swiss@defstr@i trennt am ERSTEN Gleichheitszeichen: #1 ist als
% getrenntes Argument angehaengt, sein Muster "=#2\@nil" liest darum nur
% bis zum ersten "=", der Rest (bis \@nil) wird als #2 uebernommen. Werte
% duerfen daher selbst "=" enthalten, ohne die Zerlegung zu verwirren.
% \@for haengt beim Aufsplitten der Kommaliste jedoch ein fuehrendes
% Leerzeichen an jeden Schluessel ausser dem ersten an (siehe Kommentar
% bei \swiss@defstr@i); \zap@space entfernt es. Schluessel sind stets
% leerzeichenfreie Bezeichner, darum ist das vollstaendige Entfernen aller
% Leerzeichen dort unschaedlich -- im Wert wird nichts angetastet, damit
% mehrwortige Werte wie "Streng vertraulich" intakt bleiben.

% \swiss@zapspace{<Text>}: wie \zap@space aus dem Kern, aber fuer den
% EXPANDIERTEN Wert eines Makros statt fuer eine rohe Parametersubstitution
% (\swiss@defstr@i unten wendet \zap@space direkt auf #1 an, weil #1 dort
% schon eine Parametersubstitution ist). Ein Kontrollwort (mehrbuchstabiger
% Befehlsname) verschluckt ein im Quelltext folgendes Leerzeichen bereits
% bei der Tokenisierung -- \zap@space\swiss@meta@classification LEERZEICHEN
% \@empty haette also nie ein Leerzeichen-Token zum Abgrenzen gefunden und
% wuerde ueber \@empty hinaus weiterlaufen (empirisch bestaetigt:
% "Paragraph ended before \zap@space was complete"). \swiss@zapspace nimmt
% den Wert daher als GEKLAMMERTES Argument #1 entgegen: das Leerzeichen im
% Definitionstext von \zap@space#1 LEERZEICHEN \@empty steht dort hinter
% einer Parameterreferenz, nicht hinter einem Kontrollwort, und bleibt
% darum ein echtes Token. Steht in Abschnitt 2a statt (wie bis v2.0) in 2b,
% weil \swissstringkeys unten es bereits braucht.
\def\swiss@zapspace#1{\zap@space#1 \@empty}

% -- Schluesselmenge (Spezifikation 4.2) --------------------------------
% Jeder gueltige Schluessel traegt eine Marke \swiss@strkey@<Schluessel>.
% \swiss@str@keys haelt dieselbe Menge zusaetzlich als lesbare Liste fuer
% Fehlermeldungen. \swissstringkeys erweitert beides -- eine Identitaet mit
% eigenem Klassifizierungsvokabular meldet damit ihre eigenen Schluessel an,
% BEVOR sie sie ueber \swisssetstrings definiert. Ohne diese Anmeldung
% waere ein Tippfehler ("tabel=...") eine stille, nie nachgeschlagene
% Definition; mit ihr ist er ein Fehler an der Stelle, an der er steht.
\def\swiss@str@keys{table,figure,page,classification-public,%
  classification-internal,classification-confidential,classification-strict}
\newcommand{\swissstringkeys}[1]{%
  \@for\swiss@sk:=#1\do{%
    \ifx\swiss@sk\@empty\else
      \edef\swiss@sk@n{\expandafter\swiss@zapspace\expandafter{\swiss@sk}}%
      \global\expandafter\let\csname swiss@strkey@\swiss@sk@n\endcsname\@empty
    \fi}%
  % Reiner Anzeigetext fuer die Fehlermeldung; #1 wird dabei expandiert,
  % Schluessel sind aber definitionsgemaess reine Bezeichner ohne Makros.
  \xdef\swiss@str@keys{\swiss@str@keys,#1}}
\@for\swiss@sk:=table,figure,page,classification-public,%
  classification-internal,classification-confidential,%
  classification-strict\do{%
  \edef\swiss@sk@n{\expandafter\swiss@zapspace\expandafter{\swiss@sk}}%
  \global\expandafter\let\csname swiss@strkey@\swiss@sk@n\endcsname\@empty}

\newcommand{\swisssetstrings}[2]{%
  \begingroup
  \@for\swiss@pair:=#2\do{%
    \ifx\swiss@pair\@empty\else
      \expandafter\swiss@defstr\expandafter{\swiss@pair}{#1}%
    \fi}%
  \endgroup}
\def\swiss@defstr#1#2{\swiss@defstr@i#1\@nil{#2}}
\def\swiss@defstr@i#1=#2\@nil#3{%
  \edef\swiss@key{\zap@space#1 \@empty}%
  \ifcsname swiss@strkey@\swiss@key\endcsname
    \global\@namedef{swiss@str@#3@\swiss@key}{#2}%
  \else
    % Kein Rueckfall auf "trotzdem definieren": ein nicht angemeldeter
    % Schluessel wird nie nachgeschlagen, seine Definition waere tote Last.
    \ClassError{swisstex}{Unknown string key `\swiss@key'}%
      {Declared keys: \swiss@str@keys. Declare a new key first with
       \string\swissstringkeys{<key>,...}, then define it with
       \string\swisssetstrings.}%
  \fi}

% -- Nachschlagen: expandierbarer Kern, robuster Mantel -----------------
% Bis v2.0 gab es nur EINEN Befehl \swiss@str, der Nachschlag UND Diagnose
% (\ClassWarning/\ClassError) in einem Koerper vermischte. Das war an den
% beiden \edef-Aufrufstellen (Fusszeile Abschnitt 7, Umschlagkennzeichnung
% Abschnitt 10a) nicht tragfaehig, weil beide den Text VOR \tracked
% aufloesen muessen (sonst versalisiert \MakeUppercase den Tabellen-
% SCHLUESSEL) und dabei den gesamten Makrokoerper expandieren:
%   -- Rueckfallpfad: \ClassWarning expandierte mitten im \edef, seine
%      unexpandierbaren Bestandteile (\immediate, \write, ...) landeten als
%      Text im Ergebnis -- gesetzt wurde "IMMEDIATEINTERNAL", die Warnung
%      selbst verschwand (empirisch reproduziert).
%   -- Fehlerpfad: \ClassError expandierte ebenso und zerfiel in eine
%      Kaskade aus "Undefined control sequence" statt der einen gemeinten
%      Meldung -- genau der Fall "eigenes Vokabular ohne Zeichenketten".
% Die Aufteilung trennt darum sauber:
%   \swiss@str@x       reiner, EXPANDIERBARER Nachschlag, keine Diagnose
%   \swiss@str@in      dito, in einer ausdruecklich benannten Sprache
%   \swiss@str@resolve Aufloesung MIT Diagnose, aber ausserhalb des \edef
%   \swiss@str         robuster Satzbefehl fuer den gewoehnlichen Aufruf
% Wer eine Zeichenkette in einem Expansionskontext braucht, nimmt
% \swiss@str@x/\swiss@str@resolve, nie \swiss@str.
\def\swiss@str@x#1#2{%
  \ifcsname swiss@str@#1@#2\endcsname
    \expandafter\@firstoftwo
  \else
    \expandafter\@secondoftwo
  \fi
  {\csname swiss@str@#1@#2\endcsname}{}}

% \swiss@str@in{<Sprache>}{<Schluessel>}: Nachschlag in einer AUSDRUECKLICH
% benannten Sprache, mit demselben Rueckfall auf english wie \swiss@str,
% aber ohne Diagnose und ohne \swiss@lang anzutasten. Erweiterungspunkt fuer
% den zweisprachigen Satz (Plan 3, Pruefung A14): dort braucht die zweite
% Spalte die Zeichenketten einer anderen Sprache als die Dokumentsprache.
\def\swiss@str@in#1#2{%
  \ifcsname swiss@str@#1@#2\endcsname
    \expandafter\@firstoftwo
  \else
    \expandafter\@secondoftwo
  \fi
  {\swiss@str@x{#1}{#2}}{\swiss@str@x{english}{#2}}}

% Die EINE Warnung je Sprache und Schluessel. Die Marke ist global, damit
% sie eine Gruppe (Fusszeile, Umschlag) ueberlebt -- sonst waere "einmalig"
% erneut nur behauptet.
\def\swiss@str@warn#1#2{%
  \ifcsname swiss@str@warned@#1@#2\endcsname\else
    \global\expandafter\let\csname swiss@str@warned@#1@#2\endcsname\@empty
    \ClassWarning{swisstex}{No string `#2' for language `#1',
      falling back to english}%
  \fi}
\def\swiss@str@unknown#1{%
  \ClassError{swisstex}{Unknown string key `#1'}%
    {Declared keys: \swiss@str@keys. Declare a new key first with
     \string\swissstringkeys{<key>,...}, then define it with
     \string\swisssetstrings.}}

% \swiss@str@resolve{<Makro>}{<Schluessel>}: legt den fertigen TEXT in
% <Makro> ab und gibt die Diagnose dort aus, wo sie hingehoert -- im
% unexpandierten Satzkontext, nicht mitten in einem \edef. \protected@edef
% statt \edef: die Werte selbst duerfen robuste Befehle enthalten
% (german/classification-public = \"Offentlich), die unexpandiert bis zum
% \MakeUppercase in \tracked durchkommen muessen.
\newcommand{\swiss@str@resolve}[2]{%
  \ifcsname swiss@str@\swiss@lang @#2\endcsname
    \protected@edef#1{\swiss@str@x{\swiss@lang}{#2}}%
  \else
    \ifcsname swiss@str@english@#2\endcsname
      \swiss@str@warn{\swiss@lang}{#2}%
      \protected@edef#1{\swiss@str@x{english}{#2}}%
    \else
      \swiss@str@unknown{#2}%
      \def#1{}%
    \fi
  \fi}

\DeclareRobustCommand{\swiss@str}[1]{%
  \ifcsname swiss@str@\swiss@lang @#1\endcsname
    \csname swiss@str@\swiss@lang @#1\endcsname
  \else
    \ifcsname swiss@str@english@#1\endcsname
      \swiss@str@warn{\swiss@lang}{#1}%
      \csname swiss@str@english@#1\endcsname
    \else
      \swiss@str@unknown{#1}%
    \fi
  \fi}
% Grundausstattung Deutsch/Englisch. Weitere Sprachen (siehe Handbuch)
% werden ueber \swisssetstrings in der Praeambel oder einer eigenen
% Identitaetsdatei nachgetragen. Der Schluessel "page" ist ausgeliefert,
% aber von der Klasse selbst noch nirgends gesetzt: die Pagina im
% Kolumnentitel (Abschnitt 7) ist eine blosse Ziffer ohne Wort davor. Er
% bleibt fuer eine spaetere, wortfuehrende Paginierung reserviert und ist
% fuer eigene Konstruktionen ueber \swiss@str{page} abrufbar.
\swisssetstrings{german}{%
  table=Tabelle,
  figure=Abbildung,
  page=Seite,
  classification-public=\"Offentlich,
  classification-internal=Intern,
  classification-confidential=Vertraulich,
  classification-strict=Streng vertraulich}
\swisssetstrings{english}{%
  table=Table,
  figure=Figure,
  page=Page,
  classification-public=Public,
  classification-internal=Internal,
  classification-confidential=Confidential,
  classification-strict=Strictly confidential}

% ---------------------------------------------------------------------
% 2b  Identitaetsschnittstelle
% Oeffentliche Setzer fuer Farbrollen, Identitaetsmetadaten (Firma,
% Impressum, Web), Logo-Dateien, das Klassifizierungsvokabular und die
% Fusszeilenvorlage, dazu die dokumentseitigen Metadaten \swissmeta. Alle
% Setzer sind dieselben Befehle in der Praeambel UND in einer
% Identitaetsdatei -- der Aufrufort ist gleichgueltig, darum wirkt jeder
% \gdef statt \def: eine Identitaetsdatei laeuft zwar bereits ausserhalb
% jeder Gruppe (sie wird wie ein Paket geladen, kein \begingroup drumherum),
% ein \swissmeta-Aufruf mitten im Dokument kann aber in einer Gruppe stehen
% (z. B. innerhalb einer Umgebung), und dort MUSS die Wirkung ueber das
% Gruppenende hinaus bestehen bleiben. \define@key/\setkeys kommen bereits
% ueber kvoptions (Abschnitt 1) mit dem Kern-keyval-Paket herein; kein
% zusaetzliches \RequirePackage{keyval} noetig.
\def\swiss@bandvalue{}% leer = eine Farbe (Bandfeld = Signalfarbe, M-B-Regel)
% v1.3-Bruecke: Die Klassenoption "band" trug vor v2.0 einen festen
% Vorgabewert (255,105,91); ihr Vorgabewert ist seit v2.0 leer (Abschnitt 1),
% "band = accent" (eine Farbe) ist die neue Grundeinstellung. Ein
% AUSDRUECKLICH am \documentclass gesetzter Optionswert macht \swiss@band
% nicht-leer und wird hier uebernommen (v1.3-Verhalten bleibt erreichbar);
% eine Identitaetsdatei oder ein spaeteres \swisssetcolors{band=...} in der
% Praeambel ueberschreiben ihn danach erneut -- letzter Aufruf gewinnt, wie
% bei jedem anderen Setzer.
\ifx\swiss@band\@empty\else\global\let\swiss@bandvalue\swiss@band\fi
\define@key{swissid}{accent}{\gdef\swiss@accent{#1}}
\define@key{swissid}{band}{\gdef\swiss@bandvalue{#1}}
\define@key{swissid}{paper}{\gdef\swiss@paper{#1}}
\define@key{swissid}{ink}{\gdef\swiss@ink{#1}}
\newcommand{\swisssetcolors}[1]{\setkeys{swissid}{#1}}

\gdef\swiss@id@company{}\gdef\swiss@id@legal{}\gdef\swiss@id@web{}
\define@key{swissidm}{company}{\gdef\swiss@id@company{#1}}
\define@key{swissidm}{legal}{\gdef\swiss@id@legal{#1}}
\define@key{swissidm}{web}{\gdef\swiss@id@web{#1}}
\newcommand{\swissidentitymeta}[1]{\setkeys{swissidm}{#1}}

% Logo-Dateien und die Schriften, die IN ihnen stecken. cover= und
% colophon= benennen die Dateien (Umschlag, Kolophon); logofonts= benennt
% die Schriftfamilien, die eine eingebundene Logodatei mitbringt, als
% Kommaliste von Familiennamen. Grund: eine Logodatei ist fremdes Material
% -- ein als PDF gesetztes Logo bettet seine eigene Schrift ein, und
% swisscheck A16 (Schriftinventar) faende sie als undeklarierte Familie im
% fertigen Dokument. Ohne diesen Kanal blieben nur zwei schlechte
% Auswege: A16 aufweichen oder das Logo weglassen. logofonts= macht die
% Ausnahme statt dessen ausdruecklich und pruefbar -- die Identitaet
% ERKLAERT, welche fremde Schrift ihr Logo mitbringt, und A16 laesst genau
% diese zu, keine andere.
\gdef\swiss@logo@cover{}\gdef\swiss@logo@colophon{}\gdef\swiss@logo@fonts{}
\define@key{swisslogo}{cover}{\gdef\swiss@logo@cover{#1}}
\define@key{swisslogo}{colophon}{\gdef\swiss@logo@colophon{#1}}
\define@key{swisslogo}{logofonts}{\gdef\swiss@logo@fonts{#1}}
\newcommand{\swisslogofiles}[1]{\setkeys{swisslogo}{#1}}

% Klassifizierungsvokabular: geordnete Liste, der Index bestimmt die
% Rangfolge (0 = niedrigste Stufe). Die Vorgabe deckt sich mit den
% Sprachtabellenschluesseln classification-public/-internal/-confidential/
% -strict aus Abschnitt 2a; eine Identitaet mit eigenem Vokabular braucht
% passende \swisssetstrings-Eintraege fuer jeden neuen Namen.
% \swiss@checkclass am Ende: das Vokabular darf NACH einem \swissmeta
% wechseln (eine Identitaetsdatei laedt zwar vor der Praeambel, ein
% Dokument kann aber beides in beliebiger Reihenfolge aufrufen). Ohne die
% Nachpruefung bliebe ein \swiss@classlevel stehen, der auf das ALTE
% Vokabular zeigt -- die Fusszeile setzte dann die Marke einer Stufe, die
% es nicht mehr gibt, oder gar keine. Der Aufruf ist harmlos, solange noch
% keine Klassifizierung gesetzt ist: \swiss@checkclass prueft das selbst
% (\ifcsname swiss@meta@classification) und tut dann nichts.
\def\swiss@classifications{public,internal,confidential,strict}
\newcommand{\swissclassifications}[1]{%
  \gdef\swiss@classifications{#1}\swiss@checkclass}

% Fusszeilenvorlage: UNEXPANDIERT gespeichert (\gdef, kein \edef/\protected@edef
% -- Makroparametersubstitution expandiert #1 ohnehin nicht). \meta wird erst
% beim Fusssatz gebunden (spaeterer Abschnitt); ein
% \swissfootformat{\meta{docid}} darf an dieser Stelle also nicht scheitern,
% obwohl \meta hier noch gar nicht existiert -- es wird nie expandiert,
% nur als Tokenfolge abgelegt.
\def\swiss@footformat{}
\newcommand{\swissfootformat}[1]{\gdef\swiss@footformat{#1}}

% Dokumentseitige Metadaten (\swissmeta, oeffentlicher Dokumentbefehl).
% \swiss@meta{key} ist der Zugriff fuer spaetere Verwendungsstellen
% (Fusszeile, Umschlag, Kolophon): leer, wenn der Schluessel nie gesetzt
% wurde, statt eines "Undefined control sequence".
\def\swiss@meta#1{\ifcsname swiss@meta@#1\endcsname\csname swiss@meta@#1\endcsname\fi}
\define@key{swissmeta}{docid}{\gdef\swiss@meta@docid{#1}}
\define@key{swissmeta}{version}{\gdef\swiss@meta@version{#1}}
\define@key{swissmeta}{date}{\gdef\swiss@meta@date{#1}}
\define@key{swissmeta}{client}{\gdef\swiss@meta@client{#1}}
\define@key{swissmeta}{classification}{\gdef\swiss@meta@classification{#1}}
\gdef\swiss@meta@date{\today}% Vorgabe, ueberschreibbar wie jeder andere Schluessel
\newcommand{\swissmeta}[1]{\setkeys{swissmeta}{#1}\swiss@checkclass}

% \swiss@zapspace steht seit dieser Ueberarbeitung in Abschnitt 2a (dort
% braucht \swissstringkeys es bereits); der Kommentar zu seiner Bauform
% steht ebenfalls dort.
% \swiss@classlevel: 0-basierter Index von \swiss@meta@classification in
% \swiss@classifications, -1 wenn keine Klassifizierung gesetzt ist.
% \ifx vergleicht Bedeutung (Tokenfolge), nicht Textinhalt: \@for haengt beim
% Aufsplitten der Kommaliste \swiss@classifications ein fuehrendes
% Leerzeichen an jeden Eintrag ausser dem ersten an (derselbe Effekt wie bei
% \swisssetstrings, siehe Kommentar in Abschnitt 2a), und der Wert aus
% \setkeys (\swiss@meta@classification) kann seinerseits Leerraum um "="
% tragen. Ohne Normalisierung vergliche man ein Makro mit Leerzeichen gegen
% eines ohne und faende nie eine Uebereinstimmung. \swiss@zapspace entfernt
% -- wie \zap@space in Abschnitt 2a -- ALLE Leerzeichen, nicht nur
% Randleerzeichen; Klassifizierungsnamen sind wie Sprachschluessel stets
% leerzeichenfreie Bezeichner, das ist darum unschaedlich. Der doppelte
% \expandafter setzt \swiss@meta@classification bzw. \swiss@c VOR dem Aufruf
% von \swiss@zapspace in ein geklammertes Argument um (Standardidiom, um den
% Wert eines Makros an eine Parameterstelle zu bringen).
\gdef\swiss@classlevel{-1}
\def\swiss@checkclass{%
  \ifcsname swiss@meta@classification\endcsname
    \gdef\swiss@classlevel{-1}%
    \edef\swiss@cls@target{%
      \expandafter\swiss@zapspace\expandafter{\swiss@meta@classification}}%
    \@tempcnta=0
    \@for\swiss@c:=\swiss@classifications\do{%
      \edef\swiss@cls@c{\expandafter\swiss@zapspace\expandafter{\swiss@c}}%
      \ifx\swiss@cls@c\swiss@cls@target
        \xdef\swiss@classlevel{\the\@tempcnta}%
      \fi
      \advance\@tempcnta by 1}%
    \ifnum\swiss@classlevel<0
      \ClassError{swisstex}{Unknown classification
        '\swiss@meta@classification'}%
        {Declared vocabulary: \swiss@classifications. Set your own with
         \string\swissclassifications, or use one of these values.}%
    \fi
  \fi}

% \swisscovervariant{name}{Vorgaben}: hinterlegt eine Schluessel-Wert-Liste
% unter \swiss@cvar@name (global, wie jeder andere Identitaets-Setzer in
% diesem Abschnitt). Die ANWENDUNG der Liste beim Aufbau des Umschlags
% steht bei \swisscoverslots in Abschnitt 10a; hier nur die Registrierung.
%
% MUSS vor der Identitaetsladung stehen (naechster Block), nicht erst in
% Abschnitt 10a bei den uebrigen Umschlag-Bausteinen: \RequirePackage laedt
% eine Identitaetsdatei INLINE an ihrer Aufrufstelle, also mitten im
% linearen Durchlauf dieser Klassendatei -- jeder Setzer, den eine
% Identitaetsdatei direkt in ihrem Dateikoerper aufruft, muss daher bereits
% VOR diesem Punkt definiert sein. Bis Fix Round 1 (Task 8) stand
% \swisscovervariant erst in Abschnitt 10a, weit hinter diesem Block; eine
% Identitaetsdatei, die \swisscovervariant{...}{...} direkt in ihrem
% Dateikoerper aufruft, traf dort auf eine schlicht undefinierte
% Kontrollsequenz (empirisch reproduziert: swissidentity-acme.sty, siehe
% Task-8-Bericht). Der Befehl selbst braucht nichts aus den spaeteren
% Abschnitten -- er legt nur eine Zeichenkette unter einem aus dem Namen
% gebildeten \csname ab, ohne jede Umschlag-Maschinerie zu beruehren -- und
% laesst sich darum gefahrlos hierher vorziehen.
\newcommand{\swisscovervariant}[2]{\expandafter\gdef\csname swiss@cvar@#1\endcsname{#2}}

% Identitaet laden: nach den Optionen und der Sprachtabelle, VOR Schrift
% (Abschnitt 3) und Farbe (Abschnitt 4) -- beide Abschnitte lesen Werte
% (\swiss@accent, \swiss@bandvalue, \swissidentityfonts, ...), die eine
% Identitaetsdatei an dieser Stelle gerade erst setzt. \swisscovervariant
% (oben) ist aus demselben Grund vorgezogen: sie ist ein Setzer, den eine
% Identitaetsdatei ebenfalls direkt in ihrem Dateikoerper aufrufen koennen
% muss, nicht erst nach dessen Ende.
\ifx\swiss@identity\@empty\else
  \IfFileExists{swissidentity-\swiss@identity.sty}%
    {\RequirePackage{swissidentity-\swiss@identity}}%
    {\ClassError{swisstex}{Identity file
       'swissidentity-\swiss@identity.sty' not found}%
       {Provide a file named swissidentity-\swiss@identity.sty on the
        TeX search path, or remove the identity= class option.}}%
\fi

% ---------------------------------------------------------------------
% 3  Schrift  (I4)
% ---------------------------------------------------------------------
\RequirePackage{fontspec}
\RequirePackage{polyglossia}
\setdefaultlanguage{\swiss@lang}

\RequirePackage[fleqn]{amsmath}
\RequirePackage{unicode-math}
\setlength{\mathindent}{0pt}

% \condensed selbst -- die fontspec-Familie hinter \condensed -- wird HIER,
% einmalig und sofort (nicht ueber die Weiche unten), mit der Vorgabeschrift
% deklariert. Grund, empirisch geprueft: fontspec unterscheidet
% \newfontfamily (deklarieren, wie \newcommand) von \renewfontfamily
% (umdefinieren, wie \renewcommand -- verlangt eine bestehende Deklaration).
% Ein Identitaetsanbieter tauscht die Schrift hinter \condensed per
% \renewfontfamily aus (siehe tests/fixtures/provider.tex); liegt \condensed
% zu diesem Zeitpunkt noch NICHT vor, bricht \renewfontfamily mit
% "\RenewDocumentCommand with a command that was never defined" ab und
% \condensed bleibt danach spurlos undefiniert (xparse ignoriert die
% gesamte Definition, statt einen harten Fehler zu werfen -- kein
% Buildabbruch, aber ein spaeteres "Undefined control sequence" an jeder
% Aufrufstelle). Die Deklaration steht deshalb bewusst ausserhalb der
% Anbieter-Weiche, mit der Vorgabeschrift bestueckt: der Vorgabepfad
% braucht sie unveraendert, ein Identitaetsanbieter findet sie vor und
% ersetzt nur die Schrift dahinter.
\newfontfamily\condensed{\swiss@sanscondensed}[
  Extension = .otf, UprightFont = *-regular, ItalicFont = *-italic,
  BoldFont = *-bold, BoldItalicFont = *-bolditalic, Ligatures = TeX]

% \swisscodeface -- der ZWEITE deklarierte Anbieter-Begleiter neben der
% Mathe-Schrift. Nutzerentscheid vom 2026-07-31: I4 ("eine Schriftfamilie")
% liest sich seither als "eine Familie plus deklarierte Mathe- und
% Code-Begleiter" -- Monospace-Ausrichtung ist fuer Code so funktional wie
% Formelzeichen es fuer Mathe sind (Spaltentreue von Bezeichnern,
% Einrueckung, Tabellendarstellung; keine dieser Eigenschaften laesst sich
% in einer proportionalen Grotesk ausdruecken), keine zweite freihaendige
% Schriftfamilie im Sinn von I4.
%
% Geladen wie die Mathe-Schrift PER FAMILIENNAME (\swiss@codeface), nicht
% wie \swiss@sans/\swiss@sanscondensed per Dateiname ueber kpathsea --
% DejaVu Sans Mono ist eine Systemschrift, macOS loest sie wie jeden
% Familiennamen ueber CoreText auf (siehe CLAUDE.md-Eintrag zur
% Mathe-Schrift; dieselbe Eigenheit gilt hier: die vier Schnitte muessen
% zusaetzlich unter ~/Library/Fonts liegen). Vorgabe dieselbe Werkstatt wie
% die Mathe-Schrift (DejaVu-Projekt), grotesk im Skelett -- passt zur
% Anbieter-Grotesk der Klasse, ohne mit ihr verwechselt zu werden.
% Scale=MatchLowercase gleicht die x-Hoehe an den Grundtext an: eine
% Monospace-Schrift ohne diesen Abgleich laeuft im Grauwert leicht zu
% schwer oder zu leicht neben der umgebenden Grotesk.
%
% Deklaration HIER, unmittelbar wie \condensed oben (nicht ueber die
% Anbieter-Weiche unten) -- aus demselben Grund: \newfontfamily bei der
% Vorgabeschrift bestueckt, damit ein Identitaetsanbieter, der einen
% eigenen Code-Begleiter will, \renewfontfamily\swisscodeface{...} in
% seinem \swissidentityfonts aufrufen KANN (dieselbe Vollstaendigkeits-
% Mechanik wie bei \condensed, siehe Kommentar unten) -- anders als bei
% \condensed ist das Ueberschreiben aber nicht zwingend: die Vorgabe ist
% selbst schon ein deklarierter, von A16 geprueften Begleiter (wie die
% Mathe-Vorgabe), kein I4-Verstoss, wenn eine Identitaet sie unangetastet
% laesst.
\newfontfamily\swisscodeface{\swiss@codeface}[Scale=MatchLowercase]

% Anbieter-Weiche (I4): die Vorgabe ist die Grundschrift der Klasse
% (v1.3-Heros-Block, unveraendert); eine Identitaetsdatei kann sie im
% Ganzen ersetzen, indem sie \swissidentityfonts VOR diesem Punkt
% definiert (siehe Task 4). Keine Mischung -- der Anbieter ersetzt den
% Block vollstaendig, statt einzelne Zeilen zu ueberschreiben.
%
% Pflicht des Anbieters, NICHT automatisch durchgesetzt: definiert eine
% Identitaetsdatei \swissidentityfonts, MUSS sie darin neben \setmainfont
% auch \renewfontfamily\condensed{...} aufrufen (die Familie ist oben
% bereits deklariert, siehe Kommentar dort) -- sonst bleibt \condensed
% stillschweigend bei der Vorgabeschrift (Heros Condensed) haengen, waehrend
% \setmainfont die Grundschrift laengst ersetzt hat: eine unbemerkte
% Mischung zweier Familien, genau der I4-Verstoss, den diese Klasse
% eigentlich ausschliesst. Diese Weiche prueft nur, OB \swissidentityfonts
% definiert ist, nicht, ob es vollstaendig ist -- eine unvollstaendige
% Identitaet baut anstandslos, ohne Fehler oder Warnung. Ersetzt die
% Identitaet auch die Mathematik, gilt dieselbe Pflicht fuer einen eigenen
% \setmathfont-Aufruf, sonst bleibt die Vorgabe-Mathematik
% (\swiss@mathfont) aktiv. Ersetzt sie auch den Code-Begleiter, gilt
% dieselbe Renew-statt-New-Mechanik fuer \swisscodeface -- anders als bei
% \condensed/\setmathfont ist das aber eine ERLAUBNIS, keine Pflicht: die
% Vorgabe (DejaVu Sans Mono) bleibt ein vollwertiger, deklarierter
% Begleiter, wenn eine Identitaet sie nicht anfasst (siehe Kommentar bei
% \swisscodeface oben). Die durchgehende Pruefung dieser Vollstaendigkeit
% ist nicht Teil dieses Tasks -- sie kommt mit dem acme-Identitaetstest
% (Task 8) und swisscheck A16 (Task 9).
% range=\mathup/range=\mathit OHNE Teilmengenangabe uebernehmen unicode-maths
% eigene Vorgabe-Teilmengen fuer dieses Alphabet -- fuer \mathup
% {latin,Latin,greek,Greek,num,misc}, fuer \mathit
% {latin,Latin,greek,Greek,misc} (unicode-math-xetex.sty,
% \__um_default_mathalph:nnn-Tabelle). "misc" ist dabei keine Randgruppe:
% es enthaelt exakt jene "Symbol"-Zeichen aus dem Unicode-Block der
% mathematischen Alphanumerik, die neben den eigentlichen Buchstaben in
% derselben Zeile mitlaufen -- \partial (U+1D715 in der Italic-Auspraegung),
% \nabla und (nur bei \mathup) \dotlessi/\dotlessj. Ohne Einschraenkung
% beansprucht die Anbieter-Schrift (hier Heros, in Serifenschriften ohne
% Mathe-Gilde) also nicht nur die Buchstaben, sondern auch diese
% Symbolstellen -- und liefert fuer sie kein Glyph: leerer Output ohne
% Buildfehler (rc=0), im Log nur bei aktivem \tracinglostchars als
% "Missing character" sichtbar. Empirisch verifiziert (siehe
% tests/test_fonts.py::test_math_partial_glyph): $\partial$ fehlte in
% jedem Formelsatz mit \mathit-Bereich. Die Teilmengenangabe nach "/"
% (dieselbe Syntax, mit der unicode-math seine eigene Vorgabe definiert)
% grenzt auf reine Buchstaben-/Ziffernklassen ein und laesst "misc" bei der
% Vorgabe-Mathematik (\swiss@mathfont, TeX Gyre DejaVu Math -- volle
% Unicode-Abdeckung dieses Blocks) -- Buchstaben und Ziffern in der
% Grotesk, Symbole aus der Mathe-Schrift -- die Rollenteilung, die
% \swiss@sansname/\swiss@sansnameitalic im Manual (Optionstabelle,
% "Familienname/kursiver Schnitt fuer den Formelsatz") schon fuer Buchstaben
% dokumentiert, jetzt auch tatsaechlich nur fuer Buchstaben (und Ziffern)
% gilt. Eine Identitaet, die \setmathfont selbst aufruft, hat
% dieselbe Pflicht (siehe Kommentar oben) -- swissidentity-acme.sty spiegelt
% denselben Dreiklang mit derselben Einschraenkung.
\newcommand{\swiss@defaultfonts}{%
  \setmainfont{\swiss@sans}[
    Extension = .otf, UprightFont = *-regular, ItalicFont = *-italic,
    BoldFont = *-bold, BoldItalicFont = *-bolditalic, Ligatures = TeX]%
  \setmathfont{\swiss@mathfont}%
  \setmathfont[range=\mathup/{latin,Latin,greek,Greek,num}]{\swiss@sansname}%
  \setmathfont[range=\mathit/{latin,Latin,greek,Greek}]{\swiss@sansnameitalic}}

% Die Weiche selbst laeuft bei \AtBeginDocument statt sofort: fontspec
% traegt \setmainfont an dieser Stelle zuverlaessig mit, und erst am
% Beginndokument-Punkt steht sicher fest, ob eine Identitaetsdatei
% \swissidentityfonts definiert hat (sie wird zwischen \documentclass und
% \begin{document} eingebunden). Die Registrierung steht bewusst HIER in
% Abschnitt 3, VOR den \AtBeginDocument-Bloecken aus Abschnitt 4
% (\color{ink}) und Abschnitt 5 (\fontsize...\selectfont fuer den
% Grundtext). Auf diesem TeX-Live-Kern (2026) ist \AtBeginDocument selbst
% ueber das generische Hook-System des LaTeX2e-Kerns definiert:
% \DeclareRobustCommand\AtBeginDocument{\AddToHook{begindocument}} (siehe
% latex.ltx). Ohne eigene Prioritaet fuegt \AddToHook seinen Code in
% Deklarationsreihenfolge an; mehrere \AtBeginDocument-Aufrufe laufen also
% in der Reihenfolge, in der sie im Quelltext registriert wurden -- genau
% wie zuvor beim aelteren \g@addto@macro-Mechanismus. Empirisch bestaetigt,
% nicht nur aus der Kern-Definition geschlossen: drei
% \AtBeginDocument{\typeout{...}}-Marken in aufsteigender Deklarations-
% reihenfolge erscheinen im Log exakt in dieser Reihenfolge (Scratch-Test),
% und tests/test_fonts.py::test_provider_override sowie
% tests/test_doctrine.py::test_fixture_passes_swisscheck bauen beide
% erfolgreich mit der erwarteten Schrift. Liefe die Schriftweiche spaeter
% als Abschnitt 5, waere beim \selectfont des Grundtexts noch keine Schrift
% geladen, und der Grundtext griffe auf die vorherige
% (Latin-Modern-)Vorgabe zurueck.
\AtBeginDocument{%
  \ifcsname swissidentityfonts\endcsname\swissidentityfonts
  \else\swiss@defaultfonts\fi}

\RequirePackage[protrusion=true,expansion=false]{microtype}

% ---------------------------------------------------------------------
% 4  Farbe
% ---------------------------------------------------------------------
\RequirePackage{xcolor}
\definecolor{accent}{RGB}{\swiss@accent}
% band: leer (Vorgabe seit v2.0, siehe Abschnitt 2b) => dieselbe Farbe wie
% accent (M-B-Regel, eine Signalfarbe statt zwei Rottoene); \swiss@bandvalue
% ist zu diesem Zeitpunkt bereits final -- gesetzt aus der Klassenoption,
% einer geladenen Identitaet oder direktem \swisssetcolors in der Praeambel,
% je nachdem, welcher davon zuletzt lief (Abschnitt 2b). \colorlet statt
% \definecolor haelt "band" als lebendigen Alias auf "accent": aendert eine
% Identitaet accent nachtraeglich nochmals (sie sollte nicht, aber falls
% doch), zieht band mit -- \definecolor mit demselben RGB-Tripel wuerde das
% Tripel einfrieren.
\ifx\swiss@bandvalue\@empty
  \colorlet{band}{accent}%
  \typeout{swiss:band=accent}%
\else
  \definecolor{band}{RGB}{\swiss@bandvalue}%
  \typeout{swiss:band=own}%
\fi
\definecolor{paper}{RGB}{\swiss@paper}
\definecolor{ink}{RGB}{\swiss@ink}
\definecolor{quiet}{gray}{0.42}
\definecolor{hairline}{gray}{0.62}
\AtBeginDocument{\color{ink}}

% ---------------------------------------------------------------------
% 5  Grundsatz  (I1, I5)
% ---------------------------------------------------------------------
\RequirePackage{ragged2e}
\setlength{\parindent}{0pt}
\setlength{\parskip}{\gridunit}
\AtBeginDocument{%
  \fontsize{\swiss@bodysize}{\gridunit}\selectfont
  \RaggedRight
  \setlength{\RaggedRightRightskip}{0pt plus 3.2em}%
  \setlength{\abovedisplayskip}{\gridunit}%
  \setlength{\belowdisplayskip}{\gridunit}%
  \setlength{\abovedisplayshortskip}{\gridunit}%
  \setlength{\belowdisplayshortskip}{\gridunit}}
\raggedbottom
\setlength{\emergencystretch}{1em}
% Starrer \topskip fixiert die erste Grundlinie jeder Seite und macht
% das Raster seitenabsolut adressierbar.
\setlength{\topskip}{\gridunit}

% n Rasterzeilen vertikaler Raum
\newcommand{\gridskip}[1]{\par\vspace{\dimexpr#1\gridunit\relax}}

% ---------------------------------------------------------------------
% 5a  Rasterprimitive
% Beliebige Bloecke (Titel, Tabellen, Abbildungen, Formeln) haben keine
% Hoehe im Rastermass. \snaptogrid fuellt auf das naechste Vielfache auf und
% uebergibt das Raster unversehrt an den folgenden Satz. Das ersetzt jede
% handgesetzte Ausgleichskorrektur.
% ---------------------------------------------------------------------
\newsavebox{\swiss@gbox}
\newlength{\swiss@gh}

% Aufrunden ohne Modulo: ceil(a/g) = round((2a+g-2)/(2g))
\newcommand{\swiss@ceil}[1]{%
  \the\numexpr(2*\number#1+\number\gridunit-2)/(2*\number\gridunit)\relax}

% Blockplatzierung ohne Rasterbruch.
%
% Der Kern: ein Block wird so umgepackt, dass er sich wie eine Folge
% ganzer Zeilen verhaelt. Oberkante auf \ht\strutbox, Tiefe auf ein
% Vielfaches des Rastermasses aufgefuellt. Dann greift der normale
% Zeilenausgleich von TeX, und zwar mitten auf der Seite ebenso wie am
% Seitenanfang, wo statt dessen \topskip wirkt (deshalb \topskip =
% \gridunit, siehe Abschnitt 5).
%
% Abschliessend folgt eine unsichtbare Zeile mit Standardtiefe. Sie setzt
% \prevdepth dauerhaft auf den Wert, mit dem der Ausgleich der naechsten
% Grundlinie rechnet. Eine blosse Zuweisung an \prevdepth genuegt nicht,
% weil die Groesse gruppenlokal ist und das schliessende \endgroup der
% Umgebung sie zuruecksetzt.
%
% Bilanz von Grundlinie B0 bis zur naechsten Grundlinie B1:
%   B1 - B0 = \gridunit + n*\gridunit + \parskip + \gridunit = (n+3)*\gridunit
\newlength{\swiss@gd}
\newcommand{\swiss@placebox}[2]{%
  % #1 = Box, #2 = Linksversatz als Dimension
  \par
  \setbox#1=\hbox{\raise\dimexpr\ht\strutbox-\ht#1\relax\box#1}%
  \setlength{\swiss@gh}{\dp#1}%
  \ifdim\swiss@gh<\z@ \setlength{\swiss@gh}{\z@}\fi
  \edef\swiss@gn{\swiss@ceil{\swiss@gh}}%
  \dp#1=\dimexpr\swiss@gn\gridunit\relax
  \moveleft#2\box#1%
  \nointerlineskip
  \hbox{\vrule\@width\z@\@height\z@\@depth\dp\strutbox}%
  \relax}

% \snaptogrid{...}  setzt den Inhalt und stellt das Raster wieder her.
\newcommand{\snaptogrid}[1]{%
  \par\sbox{\swiss@gbox}{\begin{minipage}{\linewidth}#1\end{minipage}}%
  \swiss@placebox{\swiss@gbox}{\z@}}

% Umgebungsform, auch fuer abgesetzte Formeln geeignet.
\newenvironment{gridblock}
  {\par\begin{lrbox}{\swiss@gbox}\begin{minipage}{\linewidth}}
  {\end{minipage}\end{lrbox}\swiss@placebox{\swiss@gbox}{\z@}}



% ---------------------------------------------------------------------
% 5b  Anzeigengrade
% Auch Schaugroessen bleiben am Raster: der Durchschuss ist ein Vielfaches
% des Rastermasses, der Schriftgrad wird daraus abgeleitet. Grosse Grade
% bekommen negative Laufweite, wie im Schaugebrauch der Grotesk ueblich.
% \swissdisplay{n} setzt n Rasterzeilen Durchschuss.
% ---------------------------------------------------------------------
\newcommand{\swiss@displayratio}{0.80}
\newcommand{\swissdisplay}[1]{%
  \fontsize{\dimexpr\swiss@displayratio\dimexpr#1\gridunit\relax\relax}%
           {\dimexpr#1\gridunit\relax}\selectfont
  \ifnum#1>2\addfontfeature{LetterSpace=-1.6}\fi}

% Weiss auf Farbe, fuer Baender und Umschlaege
\newcommand{\reverse}[1]{\textcolor{white}{#1}}

% Codebeispiele und Bezeichner: Schmalschrift auf Rastermass, unabhaengig
% vom Schriftanbieter (nie Latin Modern, auch wenn \swisscode vor der
% Anbieterweiche im Text steht -- \condensed ist zu diesem Zeitpunkt
% bereits geladen, da \swisscode selbst erst beim Aufruf im Dokument
% expandiert, also nach \AtBeginDocument).
\newcommand{\swisscode}[1]{{\condensed\fontsize{8.5}{\gridunit}\selectfont #1}}

% Vorformatierter/wortwoertlicher Satz (verbatim-Umgebung UND \verb, beide
% haengen an \verbatim@font, siehe latex.ltx) laeuft auf dem ZWEITEN
% deklarierten Begleiter \swisscodeface statt auf \condensed -- derselbe
% Grad und Durchschuss wie \swisscode (8,5\,pt auf \gridunit), aber
% funktionale Spaltentreue statt Schmalschrift-Typografie. Die Unterscheidung
% ist bewusst, nicht nur ein Zufall der Umsetzung: \swisscode setzt
% BEZEICHNER MITTEN IM FLIESSTEXT, wo Farbe und Anschluss an die Grotesk
% zaehlen (inline, typografisch); verbatim/\verb setzen ABSCHNITTE
% wortwoertlichen Materials (Konfigurationsauszuege, Codebloecke), wo
% Zeichenbreite exakt und gleich sein muss, damit Einrueckung und
% Spaltenlage im Quelltext erhalten bleiben (Block, funktional) -- derselbe
% Unterschied wie zwischen Formelbuchstaben (\swiss@sansname, Grotesk) und
% Formelsymbolen (\swiss@mathfont, eigene Mathe-Schrift) in Abschnitt 3.
% \verbatim@font selbst ist ein LaTeX-Kern-Hook OHNE Argument
% (\def\verbatim@font{\normalfont\ttfamily} in latex.ltx); ein \def hier
% genuegt, \renewcommand waere nicht falsch, aber unueblich fuer einen
% Kern-Hook dieser Form. \gridsnapenv{verbatim} (Abschnitt 5c, per
% \AtBeginDocument registriert) bleibt davon unberuehrt: der Rasterfang
% haengt an \AfterEndEnvironment{verbatim}, einem reinen Umgebungs-Hook,
% nicht an der Schriftwahl innerhalb der Umgebung -- \gridsnap misst
% \pagetotal nach \par, unabhaengig davon, welche Schrift den Inhalt
% gesetzt hat (siehe tests/fixtures/stress.tex, das genau diesen Fall
% uebt: verbatim-Block mitten im Dokument, Rasterfang UND Schriftfamilie
% muessen beide stimmen).
\def\verbatim@font{\swisscodeface\fontsize{8.5}{\gridunit}\selectfont}


% ---------------------------------------------------------------------
% 5c  Rasterfang fuer fremde Umgebungen
% \swiss@placebox loest das Rasterproblem fuer selbst gebaute Bloecke.
% Umgebungen aus LaTeX und anderen Paketen bringen eigene Abstaende mit.
% \gridsnap stellt das Raster danach wieder her, ohne die Umgebung zu
% kennen: \pagetotal ist nach \par seitenrichtig, der Ausgleich fuellt auf
% die naechste Kongruenz \pagetotal = 0 (mod \gridunit) auf, und die
% unsichtbare Abschlusszeile setzt \prevdepth dauerhaft auf Standardtiefe.
% ---------------------------------------------------------------------
\newcommand{\gridsnap}{%
  \par
  \ifdim\pagetotal>\z@
    \setlength{\swiss@gh}{\pagetotal}%
    \edef\swiss@gn{\swiss@ceil{\swiss@gh}}%
    \vskip\dimexpr\swiss@gn\gridunit-\swiss@gh\relax
    \nointerlineskip
    \hbox{\vrule\@width\z@\@height\z@\@depth\dp\strutbox}%
  \fi
  \relax}

% Umgebungen, die eigene Abstaende mitbringen, werden automatisch gefangen.
\RequirePackage{etoolbox}
% \AtEndEnvironment liefe noch vor dem Schlusscode der Umgebung und damit
% vor deren eigenem Abstand. Der Fang muss danach greifen.
\newcommand{\gridsnapenv}[1]{\AfterEndEnvironment{#1}{\gridsnap}}
\AtBeginDocument{%
  \@for\swiss@e:={quote,quotation,verbatim,description,%
                  equation,displaymath,eqnarray,align,gather,multline}\do{%
    \expandafter\gridsnapenv\expandafter{\swiss@e}}%
  \@for\swiss@e:={equation*,align*,gather*,multline*}\do{%
    \expandafter\gridsnapenv\expandafter{\swiss@e}}}

% ---------------------------------------------------------------------
% 6  Umbruchsteuerung  (I6)
% ---------------------------------------------------------------------
\RequirePackage{needspace}
\widowpenalty=10000
\clubpenalty=10000
\displaywidowpenalty=10000
\predisplaypenalty=10000
\brokenpenalty=10000

% ---------------------------------------------------------------------
% 7  Kolumnentitel
% ---------------------------------------------------------------------
\RequirePackage{fancyhdr}
\newcommand{\runningtitle}{}
\newcommand{\setrunningtitle}[1]{\renewcommand{\runningtitle}{#1}}
\pagestyle{fancy}
\fancyhf{}
\renewcommand{\headrulewidth}{0pt}
% Kopfgrundlinie auf die verlaengerte Rasterzeile (Spezifikation 6:
% "the page number must always be aligned with a line of the text").
%
% Der Bezugspunkt, den LaTeX \headsep ueber dem Satzspiegel festnagelt, ist
% die Grundlinie der KOPFBOX, nicht die Grundlinie des Kopftextes. Beim Fuss
% fallen beide zusammen, beim Kopf nicht:
%   Fuss  \vbox{\footrule \vskip\footruleskip <Satz>}   -- <Satz> ist der
%         letzte Kasten, der Bezugspunkt eines \vbox ist die Grundlinie
%         seines letzten Kastens: Kopf- und Textgrundlinie sind identisch.
%   Kopf  \vbox{<Satz> \vskip\headruleskip \headrule}   -- der letzte Posten
%         ist eine LINIE; der Bezugspunkt rutscht damit an die Unterkante
%         des Stapels, also um die TIEFE von <Satz> unter dessen Grundlinie.
% fancyhdr haengt an jeden Kopf-/Fussinhalt zusaetzlich ein \strut an (siehe
% dort, \f@nch@def), die Tiefe von <Satz> ist also stets \dp\strutbox --
% unabhaengig davon, ob der eigene Inhalt ueberhaupt Unterlaengen hat. Ein
% blosses \smash um den Kopfinhalt aendert daran nichts (empirisch geprueft:
% Grundlinie unveraendert), weil der \strut NACH dem Inhalt steht.
% Gemessen ergab das 3,587 pt Versatz gegen die Rasterzeile in allen drei
% Referenzdokumenten.
%
% \headruleskip ist der einzige von fancyhdr selbst vorgesehene Abstand
% zwischen Satz und Linie. Auf -\dp\strutbox gesetzt, hebt er den
% Bezugspunkt exakt um die Tiefe wieder an, die der \strut erzeugt hat --
% keine Kennzahl, keine handgesetzte Korrektur, sondern die Gegenrechnung
% zum \strut in derselben Groesse, in derselben Zeile ausgewertet (\strut
% und diese Kompensation lesen beide \dp\strutbox im selben Moment und
% heben sich darum auch dann auf, wenn ein Seitenumbruch mitten in einem
% anderen Schriftgrad faellt). Die Kopflinie selbst ist mit
% \headrulewidth = 0pt ohnehin unsichtbar; verschieben kann diese Rechnung
% also nichts Sichtbares ausser dem Kopftext. Geprueft von swisscheck A11.
\renewcommand{\headruleskip}{-\dp\strutbox}
\fancyhead[L]{%
  \hspace*{\measureshift}%
  \makebox[0pt][l]{%
    \condensed\fontsize{7.5}{\annotationleading}\selectfont\color{quiet}%
    \makebox[\dimexpr\margincolumn+\gutter\relax][l]{%
      {\fontsize{\swiss@bodysize}{\annotationleading}\selectfont\textcolor{accent}{\thepage}}}%
    \runningtitle}}
% Fusszeile: links die Klassifizierungsmarke IN der Marginalspalte, rechts
% ab der Textachse die Metazeile. Der aeussere Kasten misst
% \margincolumn+\gutter, damit die Metazeile auf der Textachse beginnt; der
% INNERE misst \margincolumn und benennt damit die Zone, die die Marke nicht
% verlassen darf (swisscheck A10/A4 messen genau diese Kante). Da ein
% \makebox nicht beschneidet, haelt \swiss@trackedfit (Abschnitt 10) die
% Marke von sich aus in dieser Breite.
\fancyfoot[L]{%
  \hspace*{\measureshift}%
  \makebox[0pt][l]{%
    \condensed\fontsize{7.5}{\annotationleading}\selectfont
    \makebox[\dimexpr\margincolumn+\gutter\relax][l]{%
      \ifnum\swiss@classlevel>0
        \begingroup
        \swiss@str@resolve\swiss@classtext
          {classification-\swiss@meta@classification}%
        \makebox[\margincolumn][l]{%
          \textcolor{accent}{\swiss@trackedfit{\swiss@classtext}}}%
        \endgroup
      \fi}%
    \color{quiet}%
    \ifx\swiss@footformat\@empty\else
      {\let\meta\swiss@meta\swiss@footformat}\fi}}
\fancypagestyle{swisstitle}{\fancyhf{}\renewcommand{\headrulewidth}{0pt}}

% ---------------------------------------------------------------------
% 8  Gliederung  (I2, I3, I6)
% ---------------------------------------------------------------------
\RequirePackage{titlesec}
\setcounter{secnumdepth}{2}
\setcounter{tocdepth}{2}

% Beschriftung haengt links in der Marginalspalte, ausserhalb der Linien.
% \smash haelt die Ziffer aus der Zeilenhoehe heraus, damit ein grosser
% Grad in der Marginalspalte das Raster nicht anhebt.
\newcommand{\marginlabel}[1]{%
  \makebox[0pt][r]{\smash{\textcolor{accent}{#1}}\hspace*{\gutter}}}
% Grosse Ziffer in der Marginalspalte: das auffaelligste Mittel der
% Neuen Schweizer Schule, Gliederung ohne zusaetzliche Auszeichnung.
\newcommand{\sectionnumberstyle}{\condensed\swissdisplay{2}\bfseries}

% Haarlinie auf der Textachse, zwei Rasterzeilen Vorlauf.
% Die Haarlinie laeuft ueber dieselbe Blockplatzierung wie Tabellen und
% Titel. Ein roher \hbox mit \nointerlineskip wuerde \prevdepth auf null
% setzen und das Raster um die Tiefe der Vorzeile verschieben.
\newsavebox{\swiss@rbox}
\newcommand{\sectionrule}{%
  \par\Needspace*{12\gridunit}\penalty-150\vspace{\gridunit}%
  \ifswiss@rules
    \sbox{\swiss@rbox}{\color{hairline}%
      \vrule\@height0.4pt\@depth\z@\@width\textcolumn}%
    \swiss@placebox{\swiss@rbox}{\z@}%
  \else
    \vspace{\gridunit}%
  \fi}

\titleformat{\section}[hang]
  {\normalfont\swissdisplay{1}\bfseries}
  {\marginlabel{{\sectionnumberstyle\thesection}}}{0pt}{}
\titlespacing*{\section}{0pt}{0pt}{0pt}

\titleformat{\subsection}[hang]
  {\normalfont\fontsize{\swiss@bodysize}{\gridunit}\selectfont\bfseries}
  {\marginlabel{\normalfont\condensed\fontsize{9}{\gridunit}\selectfont
                \thesubsection}}{0pt}{}
\titlespacing*{\subsection}{0pt}{\gridunit}{-\gridunit}

% Dritte Ebene: unnummeriert, Auszeichnung nur ueber den Schnitt.
\titleformat{\subsubsection}[runin]
  {\normalfont\fontsize{\swiss@bodysize}{\gridunit}\selectfont\bfseries}
  {}{0pt}{}[\hspace{0.5em}]
\titlespacing*{\subsubsection}{0pt}{\gridunit}{0.5em}

% Die Linie wird automatisch gesetzt; kein manueller Aufruf noetig.
% Ein Unterabschnitt direkt nach einer Abschnittsueberschrift wird fest
% angebunden, sonst verlangt er selbst Anschluss.
\newif\if@aftersection
\let\swiss@section\section
\def\section{\@ifstar{\sectionrule\swiss@sec@star}{\sectionrule\swiss@sec@norm}}
\def\swiss@sec@norm#1{\swiss@section{#1}\global\@aftersectiontrue}
\def\swiss@sec@star#1{\swiss@section*{#1}\global\@aftersectiontrue}
\let\swiss@subsection\subsection
\def\swiss@subguard{%
  \if@aftersection\nopagebreak[4]\else\Needspace*{6\gridunit}\fi
  \global\@aftersectionfalse}
\def\subsection{\@ifstar{\swiss@subguard\swiss@subsection*}%
                        {\swiss@subguard\swiss@subsection}}

% ---------------------------------------------------------------------
% 9  Marginalie  (I3)
% ---------------------------------------------------------------------
% \leavevmode ist entscheidend: im vertikalen Modus setzt \marginpar die
% Glosse dorthin, wo der Satz gerade steht -- nach einer Ueberschrift also
% neben deren Ziffer. Mit \leavevmode beginnt zuerst der Absatz, und die
% Glosse haengt an dessen erster Zeile, eine Rasterzeile tiefer.
% \ignorespaces ist die Kehrseite von \leavevmode: im horizontalen Modus
% wird der Zeilenumbruch hinter dem Aufruf zum Wortabstand und ruecht das
% erste Wort des Absatzes ein. Im vertikalen Modus fiel er weg.
\newcommand{\marg}[1]{%
  \leavevmode
  \marginpar{\raggedright\normalfont\fontsize{7.5}{\glossleading}\selectfont
             \color{quiet}#1\par}%
  \ignorespaces}


% ---------------------------------------------------------------------
% 9a  Fussnoten
% Trennlinie auf der Textachse statt auf 40 Prozent der Spaltenbreite,
% Text in der Schmalschrift wie der Tabellenkoerper (Marginalien laufen seit
% v2.0 in der Grundschrift, siehe Abschnitt 9).
% ---------------------------------------------------------------------
\renewcommand{\footnoterule}{%
  \kern-.25\footnoteleading{\color{hairline}\hrule\@height0.4\p@\@width\textcolumn}\kern.2\footnoteleading}
\renewcommand{\@makefntext}[1]{%
  \parindent\z@\noindent
  \makebox[1.4em][l]{\textcolor{accent}{\@thefnmark}}#1}
\AtBeginDocument{%
  \renewcommand{\footnotesize}{\condensed\fontsize{8}{\footnoteleading}\selectfont}}

% Randnotiz mit Zaehler als Alternative zur Fussnote.
\newcounter{sidenote}
\newcommand{\sidenote}[1]{%
  \refstepcounter{sidenote}%
  \textsuperscript{\textcolor{accent}{\thesidenote}}%
  \marginpar{\raggedright\normalfont\fontsize{7.5}{\glossleading}\selectfont\color{quiet}%
    \textcolor{accent}{\thesidenote}\hspace{0.4em}#1\par}}

% ---------------------------------------------------------------------
% 9b  Logo als Satzblock
% \swisslogo[lines=n, axis=text|full]{Datei} setzt eine Bilddatei mit einer
% festen Hoehe von n Rasterzeilen ueber dieselbe Blockplatzierung wie Titel,
% Farbfelder und Abbildungen (\swiss@placebox, Abschnitt 5a). axis=text haelt
% die linke Kante auf der Textachse (Vorgabe, I2); axis=full bricht wie ein
% Rahmenelement auf das volle Mass aus (I2-Ausnahme, dasselbe Mass wie
% \swisstitle und \swissband). graphicx ist bereits durch die Klasse geladen
% (Abschnitt 11a); ein zweites \RequirePackage waere unschaedlich, aber
% ueberfluessig, da \includegraphics erst beim AUFRUF von \swisslogo im
% Dokument gebraucht wird, nicht bei dessen Definition hier.
%
% Eine fehlende Datei wird VOR jedem \sbox/\includegraphics-Zugriff geprueft
% (\IfFileExists), damit die Fehlermeldung den gesuchten Dateinamen selbst
% nennt statt einer graphicx-eigenen Meldung ohne Dateibezug -- und damit
% NUR diese eine Meldung erscheint (siehe Kommentar am \IfFileExists unten).
% ---------------------------------------------------------------------
\RequirePackage{ifthen}
\define@key{swisslg}{lines}{\def\swiss@lg@lines{#1}}
\define@key{swisslg}{axis}{\def\swiss@lg@axis{#1}}
\newcommand{\swisslogo}[2][]{%
  \def\swiss@lg@lines{2}\def\swiss@lg@axis{text}%
  \setkeys{swisslg}{#1}%
  \ifthenelse{\equal{\swiss@lg@axis}{text}\OR\equal{\swiss@lg@axis}{full}}{}%
    {\ClassError{swisstex}{Unknown axis '\swiss@lg@axis' for
       \string\swisslogo}%
       {Valid values: text, full.}}%
  % Der komplette Satzblock (\sbox/\includegraphics/\swiss@placebox) steht
  % im WAHR-Zweig von \IfFileExists, nicht danach: sonst liefe er auch bei
  % einer fehlenden Datei weiter und der \ClassError waere nur der ERSTE
  % einer Kaskade aus graphicx-eigenen Fehlern ("Unable to load picture",
  % "Division by 0"), weil \includegraphics dann versucht, eine
  % nichtexistente Datei zu vermessen.
  \IfFileExists{#2}%
    {\par\sbox{\swiss@gbox}{\includegraphics[height=\dimexpr\swiss@lg@lines\gridunit\relax]{#2}}%
     \ifthenelse{\equal{\swiss@lg@axis}{full}}%
       {\swiss@placebox{\swiss@gbox}{-\measureshift}}%
       {\swiss@placebox{\swiss@gbox}{\z@}}}%
    {\ClassError{swisstex}{Logo file '#2' not found}%
       {Check the path passed to \string\swisslogo.}}}

% ---------------------------------------------------------------------
% 10  Titelblock und Kolophon  (Rahmenelemente, volles Mass)
% ---------------------------------------------------------------------
\newcommand{\tracked}[1]{{\condensed\fontsize{7.5}{\annotationleading}\selectfont
  \addfontfeature{LetterSpace=16}\MakeUppercase{#1}}}

% -- Marke in fester Zonenbreite ----------------------------------------
% \swiss@trackedfit{<Text>}: dieselbe gesperrte Versalmarke wie \tracked,
% aber garantiert innerhalb von \margincolumn. Die Fusszeile setzt die
% Klassifizierungsmarke in die Marginalspalte (Abschnitt 7); ein \makebox
% beschneidet nicht, eine zu breite Marke liefe also in den Bund und
% verletzte die Spaltenregel (I3). Genau das war der Fall: die deutsche
% Stufe "Streng vertraulich" mass gesperrt 55,4 mm ab Papierkante, die
% englische "Strictly confidential" 58,6 mm -- beide ueber der Zonengrenze
% bei 54 mm (Steg 24 + Marginalspalte 30). swisscheck A10 und A4 melden das
% zu Recht als Verstoss.
%
% Die Regel ist eine feste, gemessene Leiter statt einer Rechnung: erst der
% Kennzeichnungsgrad in voller Sperrung, dann halbe Sperrung, dann derselbe
% Satz einen Grad kleiner, zuletzt ungesperrt klein. Gewaehlt wird die
% ERSTE Stufe, die in \margincolumn passt; gemessen wird mit \settowidth
% an genau der Konstruktion, die anschliessend gesetzt wird, also
% deterministisch und unabhaengig von der Schrift der Identitaet. Ein
% laengeres Vokabular als "Strictly confidential" faellt bis auf die letzte
% Stufe durch und meldet sich dann mit einer Warnung, statt stumm in den
% Bund zu laufen.
\newlength{\swiss@mkw}
\newif\ifswiss@markfits
\newcommand{\swiss@markset}[3]{{\condensed\fontsize{#1}{\annotationleading}%
  \selectfont\ifnum#2>0 \addfontfeature{LetterSpace=#2}\fi\MakeUppercase{#3}}}
\newcommand{\swiss@marktry}[3]{%
  \settowidth{\swiss@mkw}{\swiss@markset{#1}{#2}{#3}}%
  \ifdim\swiss@mkw>\margincolumn\swiss@markfitsfalse\else\swiss@markfitstrue\fi}
\newcommand{\swiss@trackedfit}[1]{%
  \swiss@marktry{7.5}{16}{#1}%
  \ifswiss@markfits\swiss@markset{7.5}{16}{#1}%
  \else
    \swiss@marktry{7.5}{8}{#1}%
    \ifswiss@markfits\swiss@markset{7.5}{8}{#1}%
    \else
      \swiss@marktry{6.5}{8}{#1}%
      \ifswiss@markfits\swiss@markset{6.5}{8}{#1}%
      \else
        \swiss@marktry{6.5}{0}{#1}%
        \ifswiss@markfits\else
          \ClassWarning{swisstex}{Classification mark `#1' is wider than
            \string\margincolumn\space even at the smallest grade; shorten
            the vocabulary entry or widen margincolumn}%
        \fi
        \swiss@markset{6.5}{0}{#1}%
      \fi
    \fi
  \fi}

% \swisstitle{Kennzeichnung}{Titel}{Untertitel} -- klassische Positionsform.
% \swisstitle*{kicker=..., title=..., subtitle=...} -- Slot-Form (seit 2.0):
% leere Slots lassen ihren eigenen Abstand entfallen, statt einen leeren
% Block zu reservieren. Beide Formen laufen durch DENSELBEN Kern
% \swiss@titlebody, der ausschliesslich \swiss@tt@k/\swiss@tt@t/\swiss@tt@s
% liest -- Positions- und Slot-Form koennen darum nicht auseinanderlaufen,
% weil es nur einen Renderpfad statt zweier parallel zu pflegender Koerper
% gibt. Dispatch ueber \@ifstar statt des in der Aufgabenskizze vorgesehenen
% suffix-Pakets: suffix.sty ist in dieser TeX-Distribution nicht installiert
% (kpsewhich findet es nicht); \@ifstar erfuellt denselben Zweck und ist
% bereits das Muster der Klasse selbst fuer \section (Abschnitt 8).
%
% Der Abstand nach der Kennzeichnung und vor dem Untertitel laeuft auf einer
% HALBEN Rasterzeile (\gridunit/2). Das verletzt I1 nicht: die Titelbox wird
% als Ganzes ueber \swiss@placebox auf ganze Rasterzeilen aufgefuellt
% (Abschnitt 5a) -- nur die GESAMThoehe des Blocks zaehlt nach aussen, ein
% Innenabstand veraendert lediglich, WIEVIEL \swiss@placebox am Blockende
% noch auffuellen muss. Das Argument braucht dafuer keine Paarung zweier
% Halbzeilen zu einer vollen Zeile: es gilt unveraendert, wenn nur EINE der
% beiden Halbzeilen ueberhaupt vorkommt (z. B. Kennzeichnung ohne
% Untertitel, also nur ein einzelner halber Rasterzeilenabstand statt
% zweier) -- die Rundung am Blockende faengt den Rest so oder so auf.
\newcommand{\swiss@titlebody}{%
  \thispagestyle{swisstitle}%
  \par\sbox{\swiss@gbox}{%
    \begin{minipage}{\fullmeasure}%
      \ifx\swiss@tt@k\@empty\else
        \tracked{\swiss@tt@k}\par\vspace{\dimexpr\gridunit/2\relax}%
      \fi
      \ifx\swiss@tt@t\@empty\else
        {\swissdisplay{2}\swiss@tt@t\par}%
      \fi
      \ifx\swiss@tt@s\@empty\else
        \vspace{\dimexpr\gridunit/2\relax}%
        {\fontsize{10.5}{\gridunit}\selectfont\color{quiet}\swiss@tt@s\par}%
      \fi
      \vspace{\gridunit}%
      % Farbrolle statt Rohfarbe: die Titellinie traegt die Textfarbe des
      % Dokuments (ink), nicht ein festes Schwarz -- eine Identitaet, die
      % ink= verschiebt, nimmt die Linie mit.
      {\color{ink}\hrule height 1.2pt}%
    \end{minipage}}%
  \swiss@placebox{\swiss@gbox}{-\measureshift}}

\newcommand{\swiss@titleargs}[3]{%
  \def\swiss@tt@k{#1}\def\swiss@tt@t{#2}\def\swiss@tt@s{#3}%
  \swiss@titlebody}

\define@key{swisstt}{kicker}{\def\swiss@tt@k{#1}}
\define@key{swisstt}{title}{\def\swiss@tt@t{#1}}
\define@key{swisstt}{subtitle}{\def\swiss@tt@s{#1}}
\newcommand{\swiss@titleslots}[1]{%
  \def\swiss@tt@k{}\def\swiss@tt@t{}\def\swiss@tt@s{}%
  \setkeys{swisstt}{#1}%
  \swiss@titlebody}

\newcommand{\swisstitle}{\@ifstar{\swiss@titleslots}{\swiss@titleargs}}

% Kolophon: Rahmenelement auf vollem Mass am Fuss der letzten Seite. Seit
% dieser Ueberarbeitung liest es die Identitaetsangaben mit -- bis dahin
% waren \swissidentitymeta (Firma/Impressum/Web) und der colophon=-Schluessel
% von \swisslogofiles zwar setzbar, aber von keiner Stelle der Klasse
% gelesen: tote Konfiguration, im Handbuch als offener Randfall vermerkt.
% Beides haengt jetzt hier, weil das Kolophon der Ort ist, an dem eine
% Herkunftsangabe hingehoert (der Kolumnentitel bleibt markenfrei, siehe
% Abschnitt 7).
%
% Reihenfolge: erst der Text des Dokuments (#1), dann -- leise, in derselben
% Groesse -- die Identitaetszeile, zuletzt die Marke rechtsbuendig auf dem
% vollen Mass. Alles innerhalb DERSELBEN minipage wie bisher; nach aussen
% bleibt das Kolophon damit genau ein Block, und die Rasterlage aendert sich
% durch die Erweiterung nicht.
\gdef\swiss@col@sep{}
\def\swiss@col@additem#1{%
  \ifx#1\@empty\else
    \swiss@col@sep#1\gdef\swiss@col@sep{ \textperiodcentered\ }%
  \fi}
% \parskip\z@: der Zusatz ist eine Fortsetzung desselben Kolophons, keine
% neue Aussage -- eine ganze Rasterzeile Abstand waere hier Betonung, die
% der Zeile nicht zusteht. Die Zuweisung wirkt gruppenlokal (der Aufrufer
% setzt sie innerhalb der Schriftgruppe des Kolophontextes).
\newcommand{\swiss@colophon@meta}{%
  \protected@edef\swiss@col@all{%
    \swiss@id@company\swiss@id@legal\swiss@id@web}%
  \ifx\swiss@col@all\@empty\else
    \par\parskip\z@\noindent
    \gdef\swiss@col@sep{}%
    \swiss@col@additem\swiss@id@company
    \swiss@col@additem\swiss@id@legal
    \swiss@col@additem\swiss@id@web
  \fi}
% Die Marke haengt an der Grundlinie des Kolophontextes und ist genau eine
% Rasterzeile hoch -- dasselbe Mass, das \swisslogo als kleinste Stufe
% kennt. \hfill im Absatz statt \makebox: die Zeile laeuft ohnehin ueber das
% volle Mass der minipage. \IfFileExists gilt hier wie bei \swisslogo
% (Abschnitt 9b): eine fehlende Datei darf keine graphicx-Kaskade ausloesen.
% Anders als dort ist sie aber nur eine Warnung -- ein Kolophon ist Beiwerk,
% eine fehlende Marke soll den Bau eines fertigen Dokuments nicht abbrechen.
\newcommand{\swiss@colophon@mark}{%
  \ifx\swiss@logo@colophon\@empty\else
    \IfFileExists{\swiss@logo@colophon}%
      {\par\begingroup\parskip\z@
       \vspace{\dimexpr\gridunit/2\relax}%
       \noindent\hfill
       \includegraphics[height=\gridunit]{\swiss@logo@colophon}%
       \par\endgroup}%
      {\ClassWarning{swisstex}{Colophon logo '\swiss@logo@colophon' not
         found; colophon mark omitted}}%
  \fi}
\newcommand{\colophon}[1]{%
  \par\vfill\noindent\hspace*{\measureshift}%
  \begin{minipage}{\fullmeasure}%
    % Blockinnenabstand, kein Aussenmass: die halbe Rasterzeile trennt
    % Linie und Satz INNERHALB des Kolophonblocks. Nach aussen zaehlt nur
    % die Gesamthoehe des Blocks (dieselbe Begruendung wie beim Titelblock,
    % Abschnitt 10) -- bis hierher stand an dieser Stelle ein rohes 6pt.
    {\color{hairline}\rule{\fullmeasure}{0.4pt}}\par
    \vspace{\dimexpr\gridunit/2\relax}
    {\condensed\fontsize{7}{\glossleading}\selectfont\color{quiet}%
     #1\swiss@colophon@meta\par}%
    \swiss@colophon@mark
  \end{minipage}\par}

\newenvironment{lead}
  {\par\begingroup\fontsize{10.5}{\gridunit}\selectfont}
  {\par\endgroup}


% ---------------------------------------------------------------------
% 10a  Umschlag und Farbfelder
%
% Farbfelder sind Rahmenelemente: sie laufen ueber das volle Mass oder
% randabfallend und sind von der Spaltenregel ausgenommen. Ihre Hoehe
% bleibt am Raster, weil sie ueber \swiss@placebox gesetzt werden.
% ---------------------------------------------------------------------

% \begin{swissband} ... \end{swissband}
% Farbfeld ueber das volle Mass, Satz in Weiss. KEIN Hoehenargument: die
% Hoehe ergibt sich aus dem Inhalt und wird ueber \swiss@ceil auf ganze
% Rasterzeilen aufgerundet (siehe unten) -- der frueher hier stehende
% Kommentar "\swissband[n]{Inhalt}" beschrieb eine Aufrufform, die es nie
% gab. Die Zahl der sichtbaren Blindzeilen darueber steuert
% \swissbandlead, den Innenabstand \swissbandpadding.
\newsavebox{\swiss@bbox}
\newcommand{\swissbandpadding}{\gridunit}   % Innenabstand des Feldes
\newcommand{\swissbandlead}{1}              % sichtbare Blindzeilen darueber
% Der Innenabstand laeuft ueber \leftskip und \rightskip, nicht ueber eine
% geschachtelte Box: eine ueber \begin und \end geteilte \hbox-Klammer
% liefe gegen die Gruppe, die LaTeX um jede Umgebung legt.
% Der Vorabstand steckt jetzt in \swiss@placeink, nicht in einem \vspace.
% Vorabstand: eine Rasterzeile geht fuer die Blockplatzierung drauf,
% \swissbandlead zaehlt die sichtbaren Blindzeilen darueber hinaus.
\newenvironment{swissband}
  {\par\nopagebreak[4]%
   \vspace{\dimexpr\swissbandlead\gridunit+\gridunit\relax}%
   \begin{lrbox}{\swiss@bbox}%
   \begin{minipage}{\fullmeasure}%
     \vspace{\swissbandpadding}%
     \color{white}\RaggedRight
     \setlength{\leftskip}{\gutter}%
     \advance\rightskip by \gutter\relax}
  {  \par\vspace{\swissbandpadding}%
   \end{minipage}\end{lrbox}%
   % Die Flaeche wird auf ganze Rasterzeilen zuzueglich der Strutoberlaenge
   % gefuellt. Dann geht die Rundung der Blockplatzierung glatt auf, und der
   % Weissraum unter dem Feld bleibt bei zwei Rasterzeilen statt bei drei.
   % Ganzzahlig ist damit nicht das Feld, sondern das Modul aus Blindzeile,
   % Feld und Blindzeile -- genau die Ordnung, die Mueller-Brockmann meint.
   % Die Flaeche wird auf k Rasterzeilen abzueglich der Strutunterlaenge
   % gefuellt. Damit ergibt der Verbund aus Blindzeile, Feld und Blindzeile
   % ganze Rasterzeilen, und unter dem Feld bleiben zwei Zeilen Luft.
   % Farbflaechen sind keine Satzbloecke. Ein Satzblock beginnt mit einer
   % Textzeile, deren Grundlinie ins Raster gehoert; eine Flaeche hat keine
   % Oberlaenge, ihre Kante ist die Kante. Nach Mueller-Brockmann liegt
   % zwischen Satz und Feld eine Blindzeile. Sie wird als transparente
   % Zeile in den Block gesetzt, damit die bewaehrte Platzierung greift.
   \setlength{\swiss@gh}{\dimexpr\ht\swiss@bbox+\dp\swiss@bbox\relax}%
   \edef\swiss@gn{\swiss@ceil{\swiss@gh}}%
   \sbox{\swiss@gbox}{\vbox{\offinterlineskip
     \hbox{\fboxsep\z@\colorbox{band}{%
       \vbox to\dimexpr\swiss@gn\gridunit+\ht\strutbox\relax{%
         \hbox{\usebox{\swiss@bbox}}\vfil}}}}}%
   \swiss@placebox{\swiss@gbox}{-\measureshift}}

% \swisscover*{kicker=..., title=..., subtitle=..., foot=..., client=...,
%   docid=..., date=..., glyph=..., glyphline=..., glyphlines=...,
%   logo=..., band=<start>/<lines>, variant=...}
% Randabfallende Umschlagseite, seit 2.0 vollstaendig auf dem Seitenraster
% verankert: KEINE Seitenanteilskoordinate mehr auf dem Umschlag, weder
% fuer das Farbband (v1.x: 0.13\paperheight) noch fuer das Ueberformat-
% zeichen (v1.x: \swisscoverglyphx/y als Bruchteile von \paperwidth/height).
% Das Farbband ist jetzt eine Rasterzeilenspanne, band=<start>/<lines>
% (Vorgabe 38/9); das Zeichen haengt seine Grundlinie an eine Rasterzeile
% (glyphline, Vorgabe 30) und seine linke Kante an die Textachse
% (\innermargin) statt an einen Seitenanteil. Anders als in 1.x hat das
% Zeichen KEINE Vorgabe mehr ("a") -- es erscheint nur, wenn glyph=
% ausdruecklich gesetzt wird.
%
% Alte Positionsform \swisscover{K}{T}{U}{F} bleibt nutzbar (mit
% \ClassWarning), siehe \swiss@coverlegacy am Ende dieses Abschnitts.
%
% -- Variantenmechanik --------------------------------------------------
% \swisscovervariant{name}{Vorgaben} hinterlegt eine Schluessel-Wert-Liste
% unter \swiss@cvar@name (global, wie jeder andere Identitaets-Setzer).
% \swisscoverslots verarbeitet seine Aufrufargumente in ZWEI Durchgaengen
% ueber ZWEI PARALLELE keyval-Familien mit denselben Schluesselnamen:
%   1. "swisscvscan": jeder Schluessel AUSSER "variant" ist dort ein
%      No-op; "variant" sucht \swiss@cvar@<name> und wendet dessen
%      gespeicherte Liste ueber die ECHTE Familie "swisscv" an -- das setzt
%      also die Vorgabewerte der Variante, mit echter Wirkung.
%   2. "swisscv": die echte Familie. "variant" ist HIER ein No-op (die
%      Anwendung geschah bereits in Durchgang 1). Alle vom Aufrufer
%      angegebenen Schluessel laufen hier ein zweites Mal, unabhaengig von
%      ihrer Position in der Liste -- ein expliziter Schluessel
%      ueberschreibt darum IMMER die Variante, gleich ob er vor oder nach
%      "variant=..." im Aufruf steht.
% Diese Zwei-Familien-Loesung kommt ohne xkeyval/kvsetkeys aus (die im
% Kern bereits ueber kvoptions geladene keyval-Maschinerie reicht). Sie
% vermeidet zugleich die Reihenfolgen-Falle der in der Aufgabenskizze
% vorgeschlagenen Alternative (\setkeys{swisscv} zweimal ueber DIESELBE
% Familie): dort wuerde ein zweiter Durchgang "variant=..." ERNEUT mit
% voller Wirkung anwenden und damit einen VOR "variant=..." stehenden
% expliziten Schluessel wieder ueberschreiben.
\newif\ifswiss@cv@baddigit
\newif\ifswiss@cv@showkicker
\newif\ifswiss@cv@showfoot
\newif\ifswiss@cv@sep

% \swiss@cv@checkdigits{<Text>}: setzt \ifswiss@cv@baddigit wahr, wenn
% <Text> leer ist oder ein Zeichen ausserhalb '0'-'9' enthaelt (Vergleich
% ueber den Zeichencode via der Backtick-Syntax `#1, Codes 48-57). Weder
% xstring (\IsInteger) noch l3regex sind in dieser Distribution als
% Abhaengigkeit zugesichert (per kpsewhich geprueft); diese Schleife kommt
% ohne beide aus. Empirisch gegen Grenzfaelle (leer, Buchstaben, Vorzeichen,
% mehrstellig) durchgetestet, siehe Task-7-Bericht.
\def\swiss@cv@checkdigits#1{%
  \edef\swiss@cv@cdval{#1}%
  \ifx\swiss@cv@cdval\@empty
    \swiss@cv@baddigittrue
  \else
    \swiss@cv@baddigitfalse
    \expandafter\swiss@cv@cdloop\swiss@cv@cdval\swiss@cv@cdend
  \fi}
\def\swiss@cv@cdloop#1{%
  \ifx#1\swiss@cv@cdend
  \else
    \ifnum`#1<48 \swiss@cv@baddigittrue\fi
    \ifnum`#1>57 \swiss@cv@baddigittrue\fi
    \expandafter\swiss@cv@cdloop
  \fi}
\let\swiss@cv@cdend\relax

% band=<start>/<lines>. \swiss@zapspace (Abschnitt 2b) normalisiert
% zuerst Leerraum. \in@ (LaTeX-Kern, ltfssdcl.dtx, ohne zusaetzliches
% Paket verfuegbar) prueft auf einen Schraegstrich, BEVOR das
% Trennmakro laeuft: \in@ braucht dafuer den bereits EXPANDIERTEN Wert
% (ein blosses \in@{/}{\swiss@cv@bandval} faende die rohe Kontrollsequenz
% niemals als Treffer -- empirisch geprueft, siehe Task-7-Bericht), daher
% der \edef+\noexpand-Umweg. Ohne diese Vorabpruefung liefe das
% Trennmakro bei einem Wert ganz ohne "/" gegen kein Trennzeichen und
% erzeugte einen rohen TeX-Fehler ("Runaway argument") statt eines
% sauberen \ClassError. Beide Haelften werden NUR bei Gueltigkeit beider
% als \swiss@cb@start/\swiss@cb@lines uebernommen -- bei einem Fehler
% bleiben die zuvor von \swiss@coverreset gesetzten Vorgaben (38/9) aktiv,
% und es folgt KEIN numerischer Vergleich auf einem ungueltigen Wert (das
% waere dieselbe Kaskadenfalle, die Task 6 bereits bei \swisslogo traf).
\def\swiss@cv@splitband#1/#2\@nil{%
  \swiss@cv@baddigitfalse
  \swiss@cv@checkdigits{#1}%
  \ifswiss@cv@baddigit
    \ClassError{swisstex}{Malformed band start '#1' in
      band=\swiss@cv@bandval}%
      {The start value in band=<start>/<lines> must be a nonnegative
       integer (grid line number), e.g. band=38/9.}%
  \else
    \swiss@cv@checkdigits{#2}%
    \ifswiss@cv@baddigit
      \ClassError{swisstex}{Malformed band lines '#2' in
        band=\swiss@cv@bandval}%
        {The lines value in band=<start>/<lines> must be a nonnegative
         integer (grid line count), e.g. band=38/9.}%
    \else
      \def\swiss@cb@start{#1}\def\swiss@cb@lines{#2}%
      \ifnum\numexpr\swiss@cb@start+\swiss@cb@lines\relax>\swiss@gridlines
        \ClassWarning{swisstex}{band=\swiss@cv@bandval reaches grid line
          \the\numexpr\swiss@cb@start+\swiss@cb@lines\relax, beyond the
          \swiss@gridlines-line page grid}%
      \fi
    \fi
  \fi}

% Alte Umschlag-Zeichen-Stellschrauben (v1.x: globaler Buchstabe plus
% Seitenanteilslage/-groesse). Sie werden von glyph=/glyphline=/glyphlines=
% auf \swisscover* ersetzt und bleiben als wirkungslose, warnende
% Rueckwaertskompatibilitaet bestehen -- ein "Command undefined" waere fuer
% ein altes Dokument haerter als eine Warnung, und die Makronamen bleiben
% fuer ein \renewcommand in altem Praeambelcode nutzbar.
\newcommand{\swisscoverglyph}{%
  \ClassWarning{swisstex}{\string\swisscoverglyph\space is deprecated and
    has no effect; use the glyph= key on \string\swisscover* instead}}
\newcommand{\swisscoverglyphx}{%
  \ClassWarning{swisstex}{\string\swisscoverglyphx\space is deprecated and
    has no effect (page-fraction cover glyph position); use the
    glyphline= key on \string\swisscover* instead (grid line, baseline)}}
\newcommand{\swisscoverglyphy}{%
  \ClassWarning{swisstex}{\string\swisscoverglyphy\space is deprecated and
    has no effect (page-fraction cover glyph position); use the
    glyphline= key on \string\swisscover* instead (grid line, baseline)}}
\newcommand{\swisscoverglyphsize}{%
  \ClassWarning{swisstex}{\string\swisscoverglyphsize\space is deprecated
    and has no effect; use the glyphlines= key on \string\swisscover*
    instead (size in grid lines)}}

% Variantenregister: \swisscovervariant selbst steht seit Fix Round 1
% (Task 8) in Abschnitt 2b, VOR der Identitaetsladung -- eine
% Identitaetsdatei kann den Setzer sonst nicht direkt in ihrem
% Dateikoerper aufrufen, siehe der dortige Kommentar. Er legt nur die
% Vorgaben ab (Schluessel-Wert-Text, unausgewertet), wendet nichts an;
% \gdef-artig global wie jeder andere Identitaets-Setzer, aus einer
% Identitaetsdatei ODER aus der Praeambel heraus registrierbar, in beiden
% Faellen unabhaengig vom Aufrufort wirksam. Die ANWENDUNG der Liste bleibt
% hier: \swisscoverslots (unten) sucht \swiss@cvar@<name> und wendet die
% gespeicherte Liste ueber die Familie "swisscv" an.
%
% -- Schluesselfamilien --------------------------------------------------
% Wartungshinweis: ein neuer Slot-Schluessel braucht einen Eintrag in BEIDEN
% Familien -- wirkend hier in "swisscv", wirkungslos in "swisscvscan" unten
% (Ausnahme: "variant" selbst) -- sonst bricht \setkeys mit einem
% "undefined key"-Fehler ab, sobald jemand den neuen Schluessel benutzt.
\define@key{swisscv}{kicker}{\def\swiss@cv@kicker{#1}}
\define@key{swisscv}{title}{\def\swiss@cv@title{#1}}
\define@key{swisscv}{subtitle}{\def\swiss@cv@subtitle{#1}}
\define@key{swisscv}{foot}{\def\swiss@cv@foot{#1}}
\define@key{swisscv}{client}{\def\swiss@cv@client{#1}}
\define@key{swisscv}{docid}{\def\swiss@cv@docid{#1}}
\define@key{swisscv}{date}{\def\swiss@cv@date{#1}}
\define@key{swisscv}{glyph}{\def\swiss@cg@glyph{#1}}
\define@key{swisscv}{glyphline}{\def\swiss@cg@line{#1}}
\define@key{swisscv}{glyphlines}{\def\swiss@cg@lines{#1}}
% glyphink (v2.1): Farbrolle des Ueberformatzeichens. Vorgabe accent
% (Ein-Rot-Pfad der v2.0); white stellt den Ton-in-Ton-Auftritt der
% 1.3-Linie wieder her, deren Zeichen hartkodiert weiss im
% Seitenhintergrund stand und den Titel darueberlaufen liess.
\define@key{swisscv}{glyphink}{\def\swiss@cg@ink{#1}}
\define@key{swisscv}{logo}{\def\swiss@cv@logo{#1}}
\define@key{swisscv}{band}{%
  \edef\swiss@cv@bandval{\swiss@zapspace{#1}}%
  \edef\swiss@cv@sbtmp{\noexpand\in@{/}{\swiss@cv@bandval}}\swiss@cv@sbtmp
  \ifin@
    \expandafter\swiss@cv@splitband\swiss@cv@bandval\@nil
  \else
    \ClassError{swisstex}{Malformed band value '#1'}%
      {Use band=<start>/<lines>, e.g. band=38/9 (grid lines).}%
  \fi}
\define@key{swisscv}{variant}{}% Wirkung laeuft ausschliesslich ueber die
                                % Vorabpruefung in "swisscvscan", siehe oben.

% Abtast-Familie: dieselben Namen, aber wirkungslos ausser "variant".
\define@key{swisscvscan}{kicker}{}
\define@key{swisscvscan}{title}{}
\define@key{swisscvscan}{subtitle}{}
\define@key{swisscvscan}{foot}{}
\define@key{swisscvscan}{client}{}
\define@key{swisscvscan}{docid}{}
\define@key{swisscvscan}{date}{}
\define@key{swisscvscan}{glyph}{}
\define@key{swisscvscan}{glyphline}{}
\define@key{swisscvscan}{glyphlines}{}
\define@key{swisscvscan}{glyphink}{}
\define@key{swisscvscan}{logo}{}
\define@key{swisscvscan}{band}{}
\define@key{swisscvscan}{variant}{%
  \@ifundefined{swiss@cvar@#1}%
    {\ClassError{swisstex}{Unknown cover variant '#1'}%
       {Declare it first with \string\swisscovervariant{#1}{...}
        (e.g. in an identity file), or fix the spelling.}}%
    {% \setkeys braucht die Vorgabenliste bereits als ECHTEN Text mit
     % echten Kommas/Gleichheitszeichen, nicht als unaufgeloeste
     % \csname...\endcsname-Tokenfolge -- sonst sieht der Kommaspalter von
     % \setkeys keine Trennstellen und uebergibt die GESAMTE Vorgabenliste
     % als einen einzigen (unbekannten) Schluesselnamen (empirisch
     % reproduziert: "Package keyval Error: kicker=...,title=... undefined").
     % \edef+\noexpand loest \csname...\endcsname UND die damit benannte
     % Kontrollsequenz vollstaendig auf, bevor \setkeys ueberhaupt laeuft --
     % derselbe Umweg wie oben bei \in@.
     \edef\swiss@cv@vartmp{\noexpand\setkeys{swisscv}%
       {\csname swiss@cvar@#1\endcsname}}%
     \swiss@cv@vartmp}}

% -- Vorgaben, Sammelbecken, Aufruf --------------------------------------
% docid/date/logo werden UNEXPANDIERT auf ihre Herkunftsquelle verwiesen
% (\swiss@meta{...}/\swiss@logo@cover) statt sofort ausgewertet: so bindet
% ein spaeteres \swissmeta/\swisslogofiles NACH \swisscoverreset, aber vor
% dem tatsaechlichen Satz des Umschlags, noch korrekt (kein veraltetes
% \edef-Abbild). Ein expliziter docid=/date=/logo=-Schluessel ueberschreibt
% diesen Verweis ohnehin vollstaendig (\def statt \edef in den obigen
% \define@key-Koerpern).
\newcommand{\swiss@coverreset}{%
  \def\swiss@cv@kicker{}\def\swiss@cv@title{}\def\swiss@cv@subtitle{}%
  \def\swiss@cv@foot{}\def\swiss@cv@client{}%
  \def\swiss@cv@docid{\swiss@meta{docid}}%
  \def\swiss@cv@date{\swiss@meta{date}}%
  \def\swiss@cg@glyph{}\def\swiss@cg@line{30}\def\swiss@cg@lines{34}%
  \def\swiss@cg@ink{accent}%
  \def\swiss@cv@logo{\swiss@logo@cover}%
  \def\swiss@cb@start{38}\def\swiss@cb@lines{9}}

\newcommand{\swisscoverslots}[1]{%
  \swiss@coverreset
  \setkeys{swisscvscan}{#1}%    % Durchgang 1: nur variant= wirkt
  \setkeys{swisscv}{#1}%        % Durchgang 2: explizite Schluessel gewinnen
  \swiss@coverbody}

% \swiss@cv@additem{<Makro>}: haengt den EXPANDIERTEN Wert von <Makro> an
% die Metazeile an, mit einem Trennzeichen vor jedem Folgeeintrag. Die
% \edef-Vorabaufloesung ist noetig, weil \swiss@cv@docid/\swiss@cv@date in
% \swiss@coverreset auf einen UNAUSGEWERTETEN \swiss@meta{...}-Aufruf
% zeigen (siehe oben): ein \ifx-Vergleich der rohen Kontrollsequenz gegen
% \@empty waere immer falsch, selbst wenn \swiss@meta{...} am Ende nichts
% liefert -- erst nach dem \edef ist der WERT vergleichbar.
\def\swiss@cv@additem#1{%
  \edef\swiss@cv@ai@val{#1}%
  \ifx\swiss@cv@ai@val\@empty\else
    \ifswiss@cv@sep\ \textbar\ \fi
    \swiss@cv@ai@val\swiss@cv@septrue
  \fi}
\newcommand{\swiss@cv@metaline}{%
  \swiss@cv@sepfalse
  \swiss@cv@additem{\swiss@cv@client}%
  \swiss@cv@additem{\swiss@cv@docid}%
  \swiss@cv@additem{\swiss@cv@date}}

\newcommand{\swiss@coverbody}{%
  \begingroup
  \thispagestyle{swisstitle}%
  \AddToShipoutPictureBG*{%
    \ifswiss@tint\else
      \AtPageLowerLeft{\color{paper}\rule{\paperwidth}{\paperheight}}%
    \fi
    % Ueberformat-Zeichen: NUR wenn glyph= gesetzt ist (keine Vorgabe
    % mehr). Grundlinie auf Rasterzeile \swiss@cg@line, linke Kante auf
    % der Textachse (\innermargin) -- dieselbe Koordinatenkonvention wie
    % das Rasterkontroll-Overlay in Abschnitt 13 (negatives y = abwaerts
    % ab der Seitenoberkante).
    \ifx\swiss@cg@glyph\@empty\else
      \AtPageUpperLeft{\put(\LenToUnit{\innermargin},%
          \LenToUnit{\dimexpr-\swiss@topmargin-\swiss@cg@line\gridunit\relax}){%
        \makebox[0pt][l]{\color{\swiss@cg@ink}%
          \fontsize{\dimexpr\swiss@cg@lines\gridunit\relax}%
                   {\dimexpr\swiss@cg@lines\gridunit\relax}%
          \selectfont\swiss@cg@glyph}}}%
    \fi
    % Farbband als Rasterzeilenspanne band=<start>/<lines>, volle
    % Seitenbreite.
    \AtPageUpperLeft{\put(0,%
        \LenToUnit{\dimexpr-\swiss@topmargin-\swiss@cb@start\gridunit\relax}){%
      \color{band}%
      \rule[-\dimexpr\swiss@cb@lines\gridunit\relax]{\paperwidth}%
        {\dimexpr\swiss@cb@lines\gridunit\relax}}}}%
  \null\vspace*{\dimexpr6\gridunit\relax}%
  \noindent\hspace*{\measureshift}%
  \begin{minipage}{\fullmeasure}%
    \color{ink}%
    \edef\swiss@cv@lg@val{\swiss@cv@logo}%
    \ifx\swiss@cv@lg@val\@empty\else
      \swisslogo{\swiss@cv@lg@val}\vspace{\gridunit}\par
    \fi
    % Kennzeichnungszeile: Kennzeichnung links, Klassifizierungsmarke
    % rechtsbuendig (ab internal aufwaerts). Die Zeile erscheint, sobald
    % EINE der beiden etwas zu zeigen hat -- eine leere Kennzeichnung ohne
    % Klassifizierung reserviert keinen Abstand (wie Abschnitt 10).
    \swiss@cv@showkickerfalse
    \ifx\swiss@cv@kicker\@empty\else\swiss@cv@showkickertrue\fi
    % \relax terminiert die Zahlenschau von \ifnum VOR dem Boolean-Setzer:
    % ohne ihn expandiert \ifnum beim Suchen weiterer Ziffern
    % \swiss@cv@showkickertrue selbst (es ist ein parameterloses \def-Makro
    % und damit expandierbar) und schleust dessen Ersetzungstext
    % "\let...=\iftrue" in den Suchlauf ein -- faellt der Vergleich dann
    % auf FALSCH, haelt die \fi-Suche das eingeschleuste "\iftrue" fuer eine
    % NEUE geschachtelte Bedingung und verbraucht das eigentliche
    % schliessende \fi dafuer ("Incomplete \ifnum", empirisch reproduziert
    % und mit \relax hier behoben, siehe Task-7-Bericht).
    \ifnum\swiss@classlevel>0\relax\swiss@cv@showkickertrue\fi
    \ifswiss@cv@showkicker
      \makebox[\fullmeasure]{%
        \ifx\swiss@cv@kicker\@empty\else\tracked{\swiss@cv@kicker}\fi
        \hfill
        \ifnum\swiss@classlevel>0
          \begingroup
          % Task 5: die Zeichenkette MUSS vor \tracked aufgeloest werden,
          % sonst versalisiert \MakeUppercase den Stringtabellen-SCHLUESSEL
          % statt des nachgeschlagenen Textes. \swiss@str@resolve statt
          % \edef\swiss@str: die Aufloesung ist expandierbar, die Diagnose
          % bleibt ausserhalb der Expansion (siehe Abschnitt 2a). Hier ohne
          % Breitenanpassung -- der Umschlag setzt die Marke rechtsbuendig
          % auf dem vollen Mass, nicht in der Marginalspalte.
          \swiss@str@resolve\swiss@cv@classtext
            {classification-\swiss@meta@classification}%
          \textcolor{accent}{\tracked{\swiss@cv@classtext}}%
          \endgroup
        \fi}%
      \par\vspace{\dimexpr2\gridunit\relax}%
    \fi
    \ifx\swiss@cv@title\@empty\else
      {\swissdisplay{4}\bfseries\swiss@cv@title\par}%
      \vspace{\dimexpr2\gridunit\relax}%
    \fi
    \ifx\swiss@cv@subtitle\@empty\else
      {\swissdisplay{1}\color{accent}\swiss@cv@subtitle\par}%
    \fi
  \end{minipage}%
  % Fusszeile: sitzt im Farbband, daher Weiss. foot= links, eine
  % Metazeile aus client/docid/date rechtsbuendig -- docid/date sind
  % Vorgaben aus \swissmeta (siehe \swiss@coverreset), client nur bei
  % ausdruecklicher Angabe. Erscheint nur, wenn mindestens eines der vier
  % etwas zu zeigen hat.
  \swiss@cv@showfootfalse
  % \meta MUSS vor den vier Proben gebunden sein, nicht erst beim Satz der
  % Fusszeile weiter unten: die Proben sind \edef-Vergleiche, und ein
  % foot=\meta{docid} (die dokumentierte Schreibweise, dieselbe wie in
  % \swissfootformat) traefe dort sonst auf eine noch undefinierte
  % Kontrollsequenz -- "Undefined control sequence \meta" mitten im
  % Umschlagaufbau, obwohl der Aufruf voellig regelkonform ist. Die Bindung
  % gilt bis zum \endgroup dieses Umschlags (\begingroup steht am Anfang von
  % \swiss@coverbody), sickert also nicht ins Dokument.
  \let\meta\swiss@meta
  \edef\swiss@cv@ft@val{\swiss@cv@foot}%
  \ifx\swiss@cv@ft@val\@empty\else\swiss@cv@showfoottrue\fi
  \edef\swiss@cv@ft@val{\swiss@cv@client}%
  \ifx\swiss@cv@ft@val\@empty\else\swiss@cv@showfoottrue\fi
  \edef\swiss@cv@ft@val{\swiss@cv@docid}%
  \ifx\swiss@cv@ft@val\@empty\else\swiss@cv@showfoottrue\fi
  \edef\swiss@cv@ft@val{\swiss@cv@date}%
  \ifx\swiss@cv@ft@val\@empty\else\swiss@cv@showfoottrue\fi
  \ifswiss@cv@showfoot
    \vfill
    \noindent\hspace*{\measureshift}%
    \begin{minipage}{\fullmeasure}%
      \condensed\fontsize{8}{\gridunit}\selectfont\color{white}%
      % \meta ist bereits vor den Proben oben gebunden (siehe dort) und
      % gilt in dieser Gruppe weiter -- \meta{...} innerhalb von foot=
      % funktioniert damit in BEIDEN Durchgaengen, Probe wie Satz.
      \makebox[\fullmeasure]{\swiss@cv@foot\hfill\swiss@cv@metaline}\par
    \end{minipage}%
    \vspace*{\dimexpr4\gridunit\relax}%
  \else
    \vfill\vspace*{\dimexpr4\gridunit\relax}%
  \fi
  \newpage\endgroup}

% Alte Positionsform: baut weiter, aber mit Abkuendigung. Jedes Argument
% wird GEKLAMMERT in die Schluessel-Wert-Liste eingesetzt (kicker={#1}, ...)
% -- ohne die Klammern wuerde ein Komma IM Argumentwert (die Handbuchseite
% selbst benutzt "Raster 13,5\,pt" als Fusszeile) faelschlich als
% Schluesseltrennzeichen gelesen.
\newcommand{\swiss@coverlegacy}[4]{%
  \ClassWarning{swisstex}{positional \string\swisscover\space is
    deprecated; use \string\swisscover*{key=value} instead}%
  \swisscoverslots{kicker={#1},title={#2},subtitle={#3},foot={#4}}}
\newcommand{\swisscover}{\@ifstar{\swisscoverslots}{\swiss@coverlegacy}}

% ---------------------------------------------------------------------
% 11  Tabellen  (I2, I3)
% Koerper auf der Textachse, Nummer und Titel in der Marginalspalte.
% Die Bindung an das Vorangehende verhindert verwaiste Ueberschriften.
% ---------------------------------------------------------------------
\RequirePackage{booktabs}
\RequirePackage{tabularx}
\RequirePackage{array}
\setlength{\aboverulesep}{0pt}
\setlength{\belowrulesep}{0pt}
\setlength{\heavyrulewidth}{0.5pt}
\setlength{\lightrulewidth}{0.4pt}
\renewcommand{\arraystretch}{1}

\newcolumntype{L}{>{\RaggedRight\arraybackslash}X}
\newcolumntype{S}[1]{>{\RaggedRight\arraybackslash}p{#1}}
\newcolumntype{R}[1]{>{\raggedleft\arraybackslash}p{#1}}
\newcommand{\tabhead}[1]{\condensed\bfseries #1}

\newcounter{swisstable}
\renewcommand{\theswisstable}{\arabic{swisstable}}
\newcommand{\tablecaptionprefix}{\swiss@str{table}}

% \begin{swisstable}{Legende}  ...  \end{swisstable}
% Die Tabelle darin muss \begin{tabularx}{\textcolumn}[t]{...} verwenden,
% damit Legende und Kopfzeile fluchten.
\newsavebox{\swiss@tbox}
\newenvironment{swisstable}[1]
  {\par\nopagebreak[4]\vspace{\gridunit}%
   \refstepcounter{swisstable}%
   \begin{lrbox}{\swiss@tbox}%
   \begin{minipage}[t]{\glosswidth}%
     \raggedright\normalfont\fontsize{7.5}{\glossleading}\selectfont\color{quiet}%
     \textcolor{accent}{\tablecaptionprefix~\theswisstable}\\[1pt]#1%
   \end{minipage}%
   \hspace{\dimexpr\gutter+\numberzone\relax}%
   \begin{minipage}[t]{\textcolumn}%
     \condensed\fontsize{8}{\footnoteleading}\selectfont}
  {\end{minipage}\end{lrbox}%
   \swiss@placebox{\swiss@tbox}{-\measureshift}}

% Hinweis: tabularx laesst sich nicht in eine eigene Umgebung wickeln,
% weil es seinen Rumpf bis zum woertlichen \end{tabularx} einliest.
% Innerhalb von swisstable daher direkt schreiben:
%   \begin{tabularx}{\textcolumn}[t]{@{}S{28mm}@{\hspace{4mm}}L@{}}
% Das [t] ist zwingend, sonst fluchtet die Legende auf die Tabellenmitte.


% ---------------------------------------------------------------------
% 11a  Abbildungen
% Gegenstueck zu swisstable: Bildkoerper auf der Textachse, Nummer und
% Legende in der Marginalspalte, Rasterfang ueber dieselbe Platzierung.
% Kein Gleitobjekt -- die Abbildung steht, wo sie geschrieben ist.
% ---------------------------------------------------------------------
\RequirePackage{graphicx}
\newcounter{swissfigure}
\renewcommand{\theswissfigure}{\arabic{swissfigure}}
\newcommand{\figurecaptionprefix}{\swiss@str{figure}}
\newsavebox{\swiss@fbox}
\newsavebox{\swiss@fcont}
\newsavebox{\swiss@fcap}
\newlength{\figcapdrop}\setlength{\figcapdrop}{0.76pt}
% Die Legende steht in der Marginalspalte NEBEN der Abbildung und fluchtet
% mit deren Oberkante. Dazu wird der Inhalt zuerst gemessen; die Legendenbox
% wird dann um (Inhaltshoehe - eigene Hoehe) gehoben. Eine [t]-Ausrichtung
% genuegt nicht, weil TikZ- und Bildboxen ihre Referenzlinie unten tragen
% und die Legende sonst an der Unterkante landet.
\newenvironment{swissfigure}[1]
  {\par\nopagebreak[4]\vspace{\gridunit}%
   \refstepcounter{swissfigure}%
   \sbox{\swiss@fcap}{\begin{minipage}[t]{\glosswidth}%
     \raggedright\normalfont\fontsize{7.5}{\glossleading}\selectfont\color{quiet}%
     \textcolor{accent}{\figurecaptionprefix~\theswissfigure}\\[1pt]#1%
   \end{minipage}}%
   \begin{lrbox}{\swiss@fcont}%
   \begin{minipage}[t]{\textcolumn}}
  {\end{minipage}\end{lrbox}%
   \sbox{\swiss@fbox}{%
     % \figcapdrop senkt die Legende um die Differenz zwischen Ascender und
     % Versalhoehe, damit die sichtbare Schriftoberkante mit der
     % Abbildungsoberkante fluchtet. Pruefung A9 misst die Fluchtung.
     \raisebox{\dimexpr\ht\swiss@fcont-\ht\swiss@fcap-\figcapdrop\relax}%
       {\usebox{\swiss@fcap}}%
     \hspace{\dimexpr\gutter+\numberzone\relax}%
     \usebox{\swiss@fcont}}%
   \swiss@placebox{\swiss@fbox}{-\measureshift}}

% Bild auf Satzspiegelbreite
\newcommand{\swissgraphic}[2][]{%
  \includegraphics[width=\textcolumn,#1]{#2}}

% ---------------------------------------------------------------------
% 12  Listen
% ---------------------------------------------------------------------
\RequirePackage{enumitem}
% labelindent=0pt haelt die Marke auf der Textachse; ohne das haengt sie
% in den Bund und verletzt die Spaltenregel.
\setlist{labelindent=0pt,align=left}
\setlist[itemize]{leftmargin=1.4em,labelwidth=1.4em,labelsep=0pt,
  itemsep=0pt,parsep=0pt,topsep=-\gridunit,partopsep=0pt,
  label=\textcolor{accent}{\textbf{--}}}
\setlist[enumerate]{leftmargin=1.6em,labelwidth=1.6em,labelsep=0pt,
  itemsep=0pt,parsep=0pt,topsep=-\gridunit,partopsep=0pt,
  label=\textcolor{accent}{\arabic*}}
\setlist[description]{leftmargin=0pt,itemsep=0pt,parsep=0pt,
  topsep=-\gridunit,partopsep=0pt,font=\normalfont\bfseries}

% Zitat: gleiche Abstandslogik wie die Listen, kein Kursivsatz.
\renewenvironment{quote}
  {\list{}{\leftmargin=1.4em\rightmargin=\z@
           \topsep=-\gridunit\parsep=\z@\partopsep=\z@\itemsep=\z@}%
   \item\relax}
  {\endlist}

% ---------------------------------------------------------------------
% 13  Rasterkontrolle
% Legt das Basislinienraster und die Spaltenkanten sichtbar unter den Satz.
% ---------------------------------------------------------------------
\RequirePackage{eso-pic}
\ifswiss@tint
  \AddToShipoutPictureBG*{\AtPageLowerLeft{%
    \color{paper}\rule{\paperwidth}{\paperheight}}}
\fi
\ifswiss@showgrid
  \AddToShipoutPictureBG{%
    \begingroup
    \color{accent!25}%
    \AtPageUpperLeft{%
      \put(\LenToUnit{\innermargin},\LenToUnit{-\swiss@topmargin}){%
        \begin{picture}(0,0)
          \multiput(0,0)(0,-\LenToUnit{\gridunit}){\swiss@gridlines}%
            {\line(1,0){\LenToUnit{\textcolumn}}}
        \end{picture}}%
      \put(\LenToUnit{\swiss@outermargin},\LenToUnit{-\swiss@topmargin}){%
        \color{accent!40}\line(0,-1){\LenToUnit{\swiss@textheight}}}%
      \put(\LenToUnit{\innermargin},\LenToUnit{-\swiss@topmargin}){%
        \color{accent!40}\line(0,-1){\LenToUnit{\swiss@textheight}}}%
      \put(\LenToUnit{\innermargin+\textcolumn},\LenToUnit{-\swiss@topmargin}){%
        \color{accent!40}\line(0,-1){\LenToUnit{\swiss@textheight}}}}%
    \endgroup}
\fi

% ---------------------------------------------------------------------
% 14  Metadaten
% ---------------------------------------------------------------------
\RequirePackage[hidelinks,bookmarks=true,bookmarksnumbered=true]{hyperref}

% ---------------------------------------------------------------------
% 14a  Kennzahlen-Sidecar (Task 9)
% \jobname.swisscheck: eine Zeile "schluessel=wert" je Kennzahl, geschrieben
% \AtEndDocument. swisscheck.py liest sie (--params oder Auto-Erkennung
% neben der PDF) und prueft damit gegen die DEKLARIERTEN Kennzahlen dieses
% Dokuments statt gegen feste Kommandozeilen-Annahmen -- ein Dokument mit
% eigenem outermargin= oder eine Identitaet mit eigenem accent= bleibt
% pruefbar, ohne dass swisscheck seine Werte erraten muss. Fehlt die Datei
% (aeltere, vor diesem Task gebaute PDFs), faellt swisscheck auf seine
% bisherigen Vorgaben zurueck -- siehe dort; diese Klasse selbst schreibt
% die Sidecar-Datei immer, ausnahmslos.
%
% -- Familiennamen (mainfamily/condensedfamily/codeface) ------------------
% \f@family (NFSS-Kern) nach \normalfont bzw. \condensed, in je einer
% LOKALEN Gruppe erfasst -- der Anbieter (Vorgabe oder Identitaet) bleibt
% dabei gleichgueltig: der Vorgabepfad liefert, was \swiss@defaultfonts
% tatsaechlich waehlt (empirisch: \f@family = "texgyreheros(0)"), eine
% Identitaet liefert, was ihr eigenes \swissidentityfonts tatsaechlich
% gesetzt hat (empirisch, swissidentity-acme.sty: \f@family =
% "SwissTeXGrotesk(0)" fuer \setmainfont{SwissTeX Grotesk}) -- ohne dass
% diese Klasse den Anbieter kennen oder dessen Optionswerte lesen muss.
% Fontspec haengt der Familien-ID stets ein Instanzkennzeichen "(n)" an;
% \swiss@sc@stripinst schneidet das am ERSTEN "(" ab (derselbe
% Delimiter-Aufruf wie \swiss@defstr@i/\swiss@cv@splitband). \in@ prueft
% zuvor, ob ueberhaupt ein "(" vorkommt (Abschnitt 10a-Idiom: der
% Heuhaufen muss ERST ueber \edef+\noexpand vorab expandiert werden, ein
% roher Verweis auf ein Makro faende darin nie einen Treffer) -- fehlt das
% "(" wider Erwarten, bleibt der volle \f@family-Wert stehen, statt einen
% rohen "Runaway argument"-Fehler zu riskieren. \swisscodeface (der zweite
% deklarierte Begleiter, Abschnitt 3) ist genau wie \condensed ein
% fontspec-\newfontfamily/\renewfontfamily-Ziel, also derselbe
% \f@family-Weg, dieselbe Instanzklammer, dasselbe Stripping -- kein Sonderfall.
%
% -- Mathe-Schrift ---------------------------------------------------------
% \fontname\textfont\symoperators (TeX-Primitiv) liefert den tatsaechlich
% GELADENEN Dateinamen der Basis-Mathe-Schrift (empirisch:
% "\"TeXGyreDejaVuMath-Regular/OT:script=math;language=dflt;\" at 9.5pt"),
% unabhaengig vom Anbieter und ohne NFSS-Umweg: unicode-math bindet die
% Mathe-Schrift nicht ueber \fontfamily/\f@family, sondern ueber die
% (LaTeX-)Mathe-Familiennummern \sym...; \symoperators ist die Basisfamilie,
% die jeder \setmathfont-Aufruf (Vorgabe wie Identitaet) unconditional
% besetzt. Der Dateiname bleibt dabei ROH stehen (Anfuehrungszeichen,
% "/OT:..."-Anhang, " at Ngrad"): swisscheck vergleicht ohnehin nur
% normalisierte TEILzeichenketten (Gross-/Kleinschreibung, Leerzeichen,
% Bindestriche entfernt), und der eigentliche Dateiname steht als PRAEFIX
% vor dem Anhang -- ein zusaetzlicher Bereinigungsschritt hier waere
% ueberfluessig.
\def\swiss@sc@stripinst#1(#2\@nil{#1}
\newwrite\swiss@sc@file
\AtEndDocument{%
  \begingroup
    \normalfont
    \xdef\swiss@sc@main{\f@family}%
  \endgroup
  \edef\swiss@sc@sbtmp{\noexpand\in@{(}{\swiss@sc@main}}\swiss@sc@sbtmp
  \ifin@\xdef\swiss@sc@main{\expandafter\swiss@sc@stripinst\swiss@sc@main\@nil}\fi
  \begingroup
    \condensed
    \xdef\swiss@sc@cond{\f@family}%
  \endgroup
  \edef\swiss@sc@sbtmp{\noexpand\in@{(}{\swiss@sc@cond}}\swiss@sc@sbtmp
  \ifin@\xdef\swiss@sc@cond{\expandafter\swiss@sc@stripinst\swiss@sc@cond\@nil}\fi
  \begingroup
    \swisscodeface
    \xdef\swiss@sc@code{\f@family}%
  \endgroup
  \edef\swiss@sc@sbtmp{\noexpand\in@{(}{\swiss@sc@code}}\swiss@sc@sbtmp
  \ifin@\xdef\swiss@sc@code{\expandafter\swiss@sc@stripinst\swiss@sc@code\@nil}\fi
  \xdef\swiss@sc@math{\fontname\textfont\symoperators}%
  \xdef\swiss@sc@class{\swiss@meta{classification}}%
  \ifx\swiss@sc@class\@empty\xdef\swiss@sc@class{none}\fi
  \immediate\openout\swiss@sc@file=\jobname.swisscheck
  \immediate\write\swiss@sc@file{gridunit=\the\gridunit}%
  \immediate\write\swiss@sc@file{bodysize=\the\dimexpr\swiss@bodysize\relax}%
  \immediate\write\swiss@sc@file{annotationleading=\the\annotationleading}%
  \immediate\write\swiss@sc@file{glossleading=\the\glossleading}%
  \immediate\write\swiss@sc@file{footnoteleading=\the\footnoteleading}%
  \immediate\write\swiss@sc@file{headsep=\the\headsep}%
  \immediate\write\swiss@sc@file{footskip=\the\footskip}%
  \immediate\write\swiss@sc@file{outermargin=\swiss@outermargin}%
  \immediate\write\swiss@sc@file{margincolumn=\swiss@margincolumn}%
  \immediate\write\swiss@sc@file{gutter=\swiss@gutter}%
  \immediate\write\swiss@sc@file{numberzone=\swiss@numberzone}%
  \immediate\write\swiss@sc@file{textcolumn=\swiss@textcolumn}%
  \immediate\write\swiss@sc@file{topmargin=\swiss@topmargin}%
  \immediate\write\swiss@sc@file{gridlines=\swiss@gridlines}%
  \immediate\write\swiss@sc@file{accent=\swiss@accent}%
  \ifx\swiss@bandvalue\@empty
    \immediate\write\swiss@sc@file{band=accent}%
  \else
    \immediate\write\swiss@sc@file{band=\swiss@bandvalue}%
  \fi
  \immediate\write\swiss@sc@file{paper=\swiss@paper}%
  \immediate\write\swiss@sc@file{ink=\swiss@ink}%
  \immediate\write\swiss@sc@file{mainfamily=\swiss@sc@main}%
  \immediate\write\swiss@sc@file{condensedfamily=\swiss@sc@cond}%
  \immediate\write\swiss@sc@file{mathfont=\swiss@sc@math}%
  % Zweiter deklarierter Begleiter (siehe \swisscodeface, Abschnitt 3):
  % treibt verbatim/\verb (\verbatim@font, Abschnitt 5b), Vorgabe DejaVu
  % Sans Mono. A16 nimmt diese Familie zusaetzlich zu mainfamily/
  % condensedfamily/mathfont in die erlaubte Menge auf -- derselbe
  % Mechanismus, der zuvor nur die Mathe-Schrift kannte.
  \immediate\write\swiss@sc@file{codeface=\swiss@sc@code}%
  % Fremde Schriften, die eine eingebundene Logodatei mitbringt -- von der
  % Identitaet ueber \swisslogofiles{logofonts=...} ERKLAERT, nicht
  % gemessen. A16 nimmt sie zusaetzlich zu mainfamily/condensedfamily/
  % mathfont/codeface in die erlaubte Menge auf; leer heisst "keine".
  \immediate\write\swiss@sc@file{logofonts=\swiss@logo@fonts}%
  \immediate\write\swiss@sc@file{classification=\swiss@sc@class}%
  \immediate\write\swiss@sc@file{docid=\swiss@meta{docid}}%
  \immediate\closeout\swiss@sc@file}

\endinput
