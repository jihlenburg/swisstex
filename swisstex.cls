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
\ProvidesClass{swisstex}[2026/07/29 v2.0.0 Swiss typographic grid]

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

% ---------------------------------------------------------------------
% 2a  Sprachtabelle
% Alle sichtbaren Zeichenketten laufen ueber \swiss@str{key} statt ueber
% fest verdrahtete Woerter. Sprachen definieren sich ueber \swisssetstrings
% (oeffentliche Schnittstelle, in Praeambel oder Identitaetsdatei nutzbar,
% Wirkung global). Unbekannter Schluessel ist ein Fehler; unbekannte
% Sprache faellt mit einmaliger Warnung auf english zurueck.
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
  \global\@namedef{swiss@str@#3@\swiss@key}{#2}}
\DeclareRobustCommand{\swiss@str}[1]{%
  \ifcsname swiss@str@\swiss@lang @#1\endcsname
    \csname swiss@str@\swiss@lang @#1\endcsname
  \else
    \ifcsname swiss@str@english@#1\endcsname
      \ClassWarning{swisstex}{No string `#1' for language
        `\swiss@lang', falling back to english}%
      \csname swiss@str@english@#1\endcsname
    \else
      \ClassError{swisstex}{Unknown string key `#1'}%
        {Valid keys: table, figure, page, classification-public,
         classification-internal, classification-confidential,
         classification-strict. Define custom keys with
         \string\swisssetstrings.}%
    \fi
  \fi}
% Grundausstattung Deutsch/Englisch. Weitere Sprachen (siehe Handbuch)
% werden ueber \swisssetstrings in der Praeambel oder einer eigenen
% Identitaetsdatei nachgetragen.
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

\gdef\swiss@logo@cover{}\gdef\swiss@logo@colophon{}
\define@key{swisslogo}{cover}{\gdef\swiss@logo@cover{#1}}
\define@key{swisslogo}{colophon}{\gdef\swiss@logo@colophon{#1}}
\newcommand{\swisslogofiles}[1]{\setkeys{swisslogo}{#1}}

% Klassifizierungsvokabular: geordnete Liste, der Index bestimmt die
% Rangfolge (0 = niedrigste Stufe). Die Vorgabe deckt sich mit den
% Sprachtabellenschluesseln classification-public/-internal/-confidential/
% -strict aus Abschnitt 2a; eine Identitaet mit eigenem Vokabular braucht
% passende \swisssetstrings-Eintraege fuer jeden neuen Namen.
\def\swiss@classifications{public,internal,confidential,strict}
\newcommand{\swissclassifications}[1]{\gdef\swiss@classifications{#1}}

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

% \swiss@zapspace{<Text>}: wie \zap@space aus dem Kern, aber fuer den
% EXPANDIERTEN Wert eines Makros statt fuer eine rohe Parametersubstitution
% (Abschnitt 2a wendet \zap@space direkt auf #1 an, weil #1 dort schon eine
% Parametersubstitution ist). Ein Kontrollwort (mehrbuchstabiger Befehlsname)
% verschluckt ein im Quelltext folgendes Leerzeichen bereits bei der
% Tokenisierung -- \zap@space\swiss@meta@classification LEERZEICHEN\@empty
% haette also nie ein Leerzeichen-Token zum Abgrenzen gefunden und wuerde
% ueber \@empty hinaus weiterlaufen (empirisch bestaetigt: "Paragraph ended
% before \zap@space was complete"). \swiss@zapspace nimmt den Wert daher als
% GEKLAMMERTES Argument #1 entgegen: das Leerzeichen im Definitionstext von
% \zap@space#1 LEERZEICHEN \@empty steht dort hinter einer Parameterreferenz,
% nicht hinter einem Kontrollwort, und bleibt darum ein echtes Token.
\def\swiss@zapspace#1{\zap@space#1 \@empty}
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

% Identitaet laden: nach den Optionen und der Sprachtabelle, VOR Schrift
% (Abschnitt 3) und Farbe (Abschnitt 4) -- beide Abschnitte lesen Werte
% (\swiss@accent, \swiss@bandvalue, \swissidentityfonts, ...), die eine
% Identitaetsdatei an dieser Stelle gerade erst setzt.
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
% (\swiss@mathfont) aktiv. Die durchgehende Pruefung dieser Vollstaendigkeit
% ist nicht Teil dieses Tasks -- sie kommt mit dem acme-Identitaetstest
% (Task 8) und swisscheck A16 (Task 9).
\newcommand{\swiss@defaultfonts}{%
  \setmainfont{\swiss@sans}[
    Extension = .otf, UprightFont = *-regular, ItalicFont = *-italic,
    BoldFont = *-bold, BoldItalicFont = *-bolditalic, Ligatures = TeX]%
  \setmathfont{\swiss@mathfont}%
  \setmathfont[range=\mathup]{\swiss@sansname}%
  \setmathfont[range=\mathit]{\swiss@sansnameitalic}}

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
% Beliebige Blöcke (Titel, Tabellen, Abbildungen, Formeln) haben keine
% Höhe im Rastermass. \snaptogrid füllt auf das nächste Vielfache auf und
% übergibt das Raster unversehrt an den folgenden Satz. Das ersetzt jede
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

% Umgebungsform, auch für abgesetzte Formeln geeignet.
\newenvironment{gridblock}
  {\par\begin{lrbox}{\swiss@gbox}\begin{minipage}{\linewidth}}
  {\end{minipage}\end{lrbox}\swiss@placebox{\swiss@gbox}{\z@}}



% ---------------------------------------------------------------------
% 5c  Anzeigengrade
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


% ---------------------------------------------------------------------
% 5b  Rasterfang fuer fremde Umgebungen
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
\fancyhead[L]{%
  \hspace*{\measureshift}%
  \makebox[0pt][l]{%
    \condensed\fontsize{7.5}{\annotationleading}\selectfont\color{quiet}%
    \makebox[\dimexpr\margincolumn+\gutter\relax][l]{%
      {\fontsize{\swiss@bodysize}{\annotationleading}\selectfont\textcolor{accent}{\thepage}}}%
    \runningtitle}}
\fancyfoot[L]{%
  \hspace*{\measureshift}%
  \makebox[0pt][l]{%
    \condensed\fontsize{7.5}{\annotationleading}\selectfont
    \makebox[\dimexpr\margincolumn+\gutter\relax][l]{%
      \ifnum\swiss@classlevel>0
        \begingroup
        \edef\swiss@classtext{\swiss@str{classification-\swiss@meta@classification}}%
        \textcolor{accent}{\tracked{\swiss@classtext}}%
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
% Eine fehlende Datei bricht VOR dem \sbox/\includegraphics-Aufruf ab, damit
% die Fehlermeldung den gesuchten Dateinamen selbst nennt statt einer
% graphicx-eigenen Meldung ohne Dateibezug.
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
  \IfFileExists{#2}{}%
    {\ClassError{swisstex}{Logo file '#2' not found}%
       {Check the path passed to \string\swisslogo.}}%
  \par\sbox{\swiss@gbox}{\includegraphics[height=\dimexpr\swiss@lg@lines\gridunit\relax]{#2}}%
  \ifthenelse{\equal{\swiss@lg@axis}{full}}%
    {\swiss@placebox{\swiss@gbox}{-\measureshift}}%
    {\swiss@placebox{\swiss@gbox}{\z@}}}

% ---------------------------------------------------------------------
% 10  Titelblock und Kolophon  (Rahmenelemente, volles Mass)
% ---------------------------------------------------------------------
\newcommand{\tracked}[1]{{\condensed\fontsize{7.5}{\annotationleading}\selectfont
  \addfontfeature{LetterSpace=16}\MakeUppercase{#1}}}

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
% (Abschnitt 5a), nur die SUMME zaehlt nach aussen, nicht jeder
% Einzelabstand innerhalb des Blocks. Zwei halbe Zeilen sind zudem selbst
% wieder ein kommensurabler Rasterbruch (Modul aus zwei Halbzeilen = eine
% Zeile) -- dieselbe Rechtfertigung wie die Blindzeile ueber dem Farbfeld
% (Abschnitt 10a), die ebenfalls innerhalb eines auf ganze Zeilen
% aufgefuellten Blocks mit einem Halbzeilenmass rechnet.
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
      {\color{black}\hrule height 1.2pt}%
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

\newcommand{\colophon}[1]{%
  \par\vfill\noindent\hspace*{\measureshift}%
  \begin{minipage}{\fullmeasure}%
    {\color{hairline}\rule{\fullmeasure}{0.4pt}}\par\vspace{6pt}
    {\condensed\fontsize{7}{\glossleading}\selectfont\color{quiet}#1\par}%
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

% \swissband[n]{Inhalt}
% Farbfeld ueber das volle Mass, n Rasterzeilen hoch, Satz in Weiss.
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

% \swisscover{Kennzeichnung}{Titel}{Untertitel}{Fusszeile}
% Randabfallende Umschlagseite. Der Titel laeuft auf vier Rasterzeilen
% Durchschuss, das Farbfeld sitzt auf dem Raster des Satzspiegels.
% Ueberformat-Zeichen: Groesse in Rasterzeilen, Lage in Seitenanteilen.
\newcommand{\swisscoverglyph}{a}
\newcommand{\swisscoverglyphsize}{34}
\newcommand{\swisscoverglyphx}{0.52}
\newcommand{\swisscoverglyphy}{0.60}
\newcommand{\swisscover}[4]{%
  \begingroup
  \thispagestyle{swisstitle}%
  \AddToShipoutPictureBG*{%
    \ifswiss@tint\else
      \AtPageLowerLeft{\color{paper}\rule{\paperwidth}{\paperheight}}%
    \fi
    % Ueberformat: Zeichen randabfallend rechts, im Ton des Grundes
    \AtPageUpperLeft{\put(\LenToUnit{\swisscoverglyphx\paperwidth},%
                          \LenToUnit{-\swisscoverglyphy\paperheight}){%
      \makebox[0pt][l]{\color{white}%
        \fontsize{\dimexpr\swisscoverglyphsize\gridunit\relax}%
                 {\dimexpr\swisscoverglyphsize\gridunit\relax}%
        \selectfont\swisscoverglyph}}}%
    % Farbband ueber die untere Seitenbreite
    \AtPageLowerLeft{\put(0,\LenToUnit{0.13\paperheight}){%
      \color{band}\rule{\paperwidth}{\dimexpr9\gridunit\relax}}}}%
  \null\vspace*{\dimexpr6\gridunit\relax}%
  \noindent\hspace*{\measureshift}%
  \begin{minipage}{\fullmeasure}%
    \color{ink}%
    \tracked{#1}\par\vspace{\dimexpr2\gridunit\relax}
    {\swissdisplay{4}\bfseries #2\par}%
    \vspace{\dimexpr2\gridunit\relax}
    {\swissdisplay{1}\color{accent}#3\par}%
  \end{minipage}%
  \vfill
  % Die Fusszeile sitzt im Farbband und laeuft deshalb in Weiss.
  \noindent\hspace*{\measureshift}%
  \begin{minipage}{\fullmeasure}%
    \condensed\fontsize{8}{\gridunit}\selectfont\color{white}#4\par
  \end{minipage}%
  \vspace*{\dimexpr4\gridunit\relax}%
  \newpage\endgroup}

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

\endinput
