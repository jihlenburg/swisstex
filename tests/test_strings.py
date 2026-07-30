from conftest import build_doc, ROOT
import pdfplumber

def _text(pdf):
    # x_tolerance=2: the caption prefix and number are joined with a non-
    # breaking space (\tablecaptionprefix~\theswisstable in swisstable), which
    # renders as a genuine ~2.07pt glyph gap (verified char-by-char: 0pt
    # between ordinary letters, ~2.07pt between the prefix and the digit) but
    # pdfplumber's default x_tolerance=3 does not treat that as a word break,
    # merging e.g. "Table" and "1" into "Table1". x_tolerance=2 matches the
    # real rendered gap without affecting ordinary (0pt-kerned) intra-word
    # joins.
    with pdfplumber.open(pdf) as p:
        return "\n".join(pg.extract_text(x_tolerance=2) or "" for pg in p.pages)

def test_english_captions(tmp_path):
    r = build_doc(ROOT / "tests/fixtures/lang-en.tex", tmp_path)
    assert r.returncode == 0, r.log[-2000:]
    t = _text(r.pdf)
    assert "Table 1" in t and "Tabelle" not in t

def test_custom_language_addable(tmp_path):
    fx = tmp_path / "fr.tex"
    fx.write_text(r"""\documentclass[lang=french]{swisstex}
\swisssetstrings{french}{table=Tableau, figure=Illustration, page=Page,
  classification-public=public, classification-internal=interne,
  classification-confidential=confidentiel, classification-strict=strict}
\begin{document}
\begin{swisstable}{Legende}\begin{tabularx}{\textcolumn}[t]{@{}L@{}}x\\\end{tabularx}\end{swisstable}
\end{document}""")
    r = build_doc(fx, tmp_path)
    assert r.returncode == 0, r.log[-2000:]
    assert "Tableau 1" in _text(r.pdf)

def test_unknown_language_falls_back(tmp_path):
    # NOTE (rough edge #4 in task-2-brief.md): verified empirically that
    # \setdefaultlanguage{latin} does NOT make polyglossia error in this TeX
    # Live install (latin ships hyphenation patterns and a gloss-latin.ldf,
    # build exits 0) -- so the brief's original premise holds and `latin` is
    # a valid choice: polyglossia accepts the language, but our DE/EN string
    # table has no "latin" entries, so \swiss@str falls back to english with
    # a warning. Kept as in the brief rather than switching to `dutch`.
    fx = tmp_path / "xx.tex"
    fx.write_text(r"""\documentclass[lang=latin]{swisstex}
\begin{document}
\begin{swisstable}{L}\begin{tabularx}{\textcolumn}[t]{@{}L@{}}x\\\end{tabularx}\end{swisstable}
\end{document}""")
    r = build_doc(fx, tmp_path)
    assert r.returncode == 0, r.log[-2000:]
    assert "Table 1" in _text(r.pdf)          # EN fallback
    assert "swisstex Warning" in r.log or "fallback" in r.log.lower()


# --- A1: Expansionssicherheit der Zeichenkettentabelle ---------------------
#
# \swiss@str vermischte bis zu dieser Änderung Nachschlag und Diagnose in einem
# Makrokörper. Die beiden \edef-Aufrufstellen (Fusszeile, Umschlagkennzeichnung)
# expandieren diesen Körper vollständig -- mit zwei reproduzierten Folgen:
#   * Rückfallpfad: \ClassWarning expandierte mit, gesetzt wurde
#     "IMMEDIATEINTERNAL", die Warnung selbst verschwand.
#   * Fehlerpfad: \ClassError zerfiel in eine Kaskade "Undefined control
#     sequence" statt der einen gemeinten Meldung.
# Beides ist hier festgenagelt.


def test_fallback_typesets_english_word_not_macro_debris(tmp_path):
    fx = tmp_path / "fbmark.tex"
    fx.write_text(r"""\documentclass[lang=latin]{swisstex}
\swissmeta{classification=internal}
\begin{document}
\section{Abschnitt}
Grundtext auf dem Raster mit genug Woertern fuer eine volle Zeile.
\end{document}""")
    r = build_doc(fx, tmp_path)
    assert r.returncode == 0, r.log[-2000:]
    t = _text(r.pdf)
    assert "INTERNAL" in t, t
    assert "IMMEDIATE" not in t, t
    # Und die Warnung erscheint wirklich -- vorher wurde sie mitexpandiert
    # und tauchte im Log nie auf.
    assert "falling back to english" in r.log, r.log[-3000:]


def test_fallback_warning_is_deduplicated(tmp_path):
    # "einmalig" war bis hierher nur behauptet: die Warnung lief bei jeder
    # Verwendungsstelle erneut. Die Vorlage setzt die Marke auf zwei Seiten,
    # die Warnung darf trotzdem nur einmal im Log stehen.
    fx = tmp_path / "fbdedup.tex"
    fx.write_text(r"""\documentclass[lang=latin]{swisstex}
\swissmeta{classification=internal}
\begin{document}
\section{Abschnitt}
Grundtext auf dem Raster mit genug Woertern fuer eine volle Zeile.
\newpage
Zweite Seite mit derselben Marke in der Fusszeile.
\end{document}""")
    r = build_doc(fx, tmp_path)
    assert r.returncode == 0, r.log[-2000:]
    assert r.log.count("falling back to english") == 1, r.log[-3000:]


def test_custom_vocabulary_without_strings_errors_intelligibly(tmp_path):
    # Der eigentliche Auslöser: ein eigenes Klassifizierungsvokabular ohne
    # passende Zeichenketten. Vorher gab es vier "Undefined control sequence"
    # aus dem zerfallenen \ClassError und keinen Hinweis auf die Ursache.
    fx = tmp_path / "vocab.tex"
    fx.write_text(r"""\documentclass{swisstex}
\swissclassifications{open,restricted}
\swissmeta{classification=restricted}
\begin{document}
\section{Abschnitt}
Grundtext auf dem Raster mit genug Woertern fuer eine volle Zeile.
\end{document}""")
    r = build_doc(fx, tmp_path)
    assert r.returncode != 0, r.log[-2000:]
    assert "Unknown string key" in r.log, r.log[-3000:]
    assert "classification-restricted" in r.log, r.log[-3000:]
    assert "Undefined control sequence" not in r.log, r.log[-3000:]


def test_custom_vocabulary_with_declared_strings_builds(tmp_path):
    # Gegenprobe und zugleich der dokumentierte Ausweg (C7): Schlüssel
    # anmelden, dann definieren.
    fx = tmp_path / "vocabok.tex"
    fx.write_text(r"""\documentclass{swisstex}
\swissstringkeys{classification-open, classification-restricted}
\swisssetstrings{german}{classification-open=Offen,
  classification-restricted=Gesperrt}
\swissclassifications{open,restricted}
\swissmeta{classification=restricted}
\begin{document}
\section{Abschnitt}
Grundtext auf dem Raster mit genug Woertern fuer eine volle Zeile.
\end{document}""")
    r = build_doc(fx, tmp_path)
    assert r.returncode == 0, r.log[-3000:]
    assert "GESPERRT" in _text(r.pdf), _text(r.pdf)


# --- C7: Schlüsselprüfung zur Definitionszeit ------------------------------

def test_unknown_string_key_errors_at_definition_time(tmp_path):
    fx = tmp_path / "typo.tex"
    fx.write_text(r"""\documentclass{swisstex}
\swisssetstrings{german}{tabel=Falsch}
\begin{document}x\end{document}""")
    r = build_doc(fx, tmp_path)
    assert r.returncode != 0, r.log[-2000:]
    assert "Unknown string key" in r.log, r.log[-3000:]
    assert "tabel" in r.log, r.log[-3000:]


def test_declared_custom_key_is_accepted(tmp_path):
    fx = tmp_path / "extkey.tex"
    fx.write_text(r"""\documentclass{swisstex}
\swissstringkeys{imprint}
\swisssetstrings{german}{imprint=Impressum}
\makeatletter
\begin{document}
\swiss@str{imprint}
\end{document}""")
    r = build_doc(fx, tmp_path)
    assert r.returncode == 0, r.log[-3000:]
    assert "Impressum" in _text(r.pdf)


def test_named_language_lookup_is_expandable(tmp_path):
    # \swiss@str@in ist der Erweiterungspunkt für den zweisprachigen Satz
    # (Plan 3): Nachschlag in einer ausdrücklich benannten Sprache, ohne
    # \swiss@lang anzutasten -- und expandierbar, also \edef-tauglich.
    fx = tmp_path / "inlang.tex"
    fx.write_text(r"""\documentclass{swisstex}
\makeatletter
\edef\swiss@probe{\swiss@str@in{english}{table}/\swiss@str@in{german}{table}}
\typeout{PROBE=\swiss@probe}
\makeatother
\begin{document}x\end{document}""")
    r = build_doc(fx, tmp_path)
    assert r.returncode == 0, r.log[-3000:]
    assert "PROBE=Table/Tabelle" in r.log, r.log[-3000:]
