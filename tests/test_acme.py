# tests/test_acme.py -- Task 8: acme reference identity + demo document.
#
# acme-demo.tex lives at the repo ROOT (identity=acme, like the manual and
# swisstex-demo.tex before it), not under tests/fixtures/: it is a real,
# committed showcase artifact ("acme-demo.pdf"), not a throwaway fixture.
# build_doc always runs xelatex with cwd=ROOT (see conftest.py), so
# swissidentity-acme.sty and acme-logo.pdf -- both also at the repo root --
# resolve via kpathsea's implicit "." search without any TEXINPUTS change;
# tests/fixtures/swissidentity-test.sty needed the tests/fixtures// TEXINPUTS
# entry only because IT lives under tests/, not at ROOT.
#
# acme-demo.tex has no \ref/\label (verified by inspection: only \section,
# \swisstable, \marg, \footnote, \swisslogo, \colophon are used, none of
# which cross-reference anything), so one xelatex pass suffices -- confirmed
# below by asserting no "undefined"/"??" residue in the log rather than just
# assuming it.

from conftest import assert_clean_refs, build_doc, swisscheck, ROOT
import pdfplumber

DOC = ROOT / "acme-demo.tex"


def _fonts(pdf):
    with pdfplumber.open(pdf) as p:
        return {c["fontname"].split("+")[-1] for pg in p.pages for c in pg.chars}


def _bottom_words(page, margin=60):
    return [w["text"] for w in page.extract_words() if w["top"] > page.height - margin]


def test_acme_demo_builds(tmp_path):
    r = build_doc(DOC, tmp_path)
    assert r.returncode == 0, r.log[-3000:]
    assert "swissidentity-acme" in r.log, r.log[-3000:]


def test_acme_demo_no_undefined_or_division_errors(tmp_path):
    # The precise regression this task exists to catch (per the brief): the
    # reference identity exercises EVERY public setter end-to-end, so any
    # gap between the class's provider contract (I4) and what a real
    # identity file actually does would surface here as a raw TeX/graphicx
    # error, not just a class-level ClassError.
    r = build_doc(DOC, tmp_path)
    assert r.returncode == 0, r.log[-3000:]
    assert r.log.count("Division by 0") == 0, r.log[-3000:]
    assert r.log.count("Undefined control sequence") == 0, r.log[-3000:]
    # acme-demo.tex has no \ref/\label of its own (see module docstring), so
    # this single-pass build must also come out with no broken cross-
    # references -- the same machine net as the manual's two-pass build
    # (tests/test_swisscheck.py), wired in here too per the T10 brief.
    assert_clean_refs(r.log, context="acme-demo")


def test_acme_fonts_are_grotesk_only(tmp_path):
    # I4 end-to-end enforcement (the class comment at the provider switch in
    # swisstex.cls sec. 3 explicitly defers this to "the acme identity test,
    # Task 8"): swissidentity-acme.sty's \swissidentityfonts must replace
    # BOTH \setmainfont and \condensed (via \renewfontfamily, not
    # \newfontfamily -- \condensed is already declared by the class itself)
    # plus its own \setmathfont, or the default TeX Gyre Heros block would
    # leak into the PDF wherever the identity's replacement is incomplete.
    r = build_doc(DOC, tmp_path)
    assert r.returncode == 0, r.log[-3000:]
    fonts = _fonts(r.pdf)
    assert fonts, "no characters embedded at all"
    assert not any("Heros" in f for f in fonts), fonts
    assert not any("LMRoman" in f or "LMMono" in f or "LMSans" in f
                   for f in fonts), fonts
    allowed_prefixes = ("SwissTeXGrotesk", "TeXGyreDejaVuMath")
    assert all(f.startswith(allowed_prefixes) for f in fonts), fonts


def test_acme_math_partial_glyph(tmp_path):
    # Mirrors tests/test_fonts.py::test_math_partial_glyph for the acme
    # identity's OWN \setmathfont triad (swissidentity-acme.sty), which
    # unlike the class's default provider selects the italic shape by full
    # name ("SwissTeX Grotesk Italic") rather than a second family name --
    # a genuinely different code path that could regress independently of
    # the class fix. Same bug shape: an unrestricted range=\mathit would
    # claim U+1D715 (\partial) for SwissTeX Grotesk Italic, which has no
    # math glyph there.
    fx = tmp_path / "acmemathpartial.tex"
    fx.write_text(r"""\documentclass[identity=acme]{swisstex}
\begin{document}
\tracinglostchars=2
$\partial f = ax^2 + \beta y$
\end{document}""")
    r = build_doc(fx, tmp_path)
    assert r.returncode == 0, r.log[-2000:]
    assert "Missing character" not in r.log, r.log[-2000:]
    with pdfplumber.open(r.pdf) as p:
        chars = {c["text"]: c["fontname"] for pg in p.pages for c in pg.chars}
    assert "\U0001d715" in chars, chars
    assert "SwissTeXGrotesk" not in chars["\U0001d715"], chars
    for letter in ("f", "a", "x", "y"):
        assert "SwissTeXGrotesk" in chars[letter], (letter, chars)


def test_acme_docid_in_foot_region(tmp_path):
    # swissidentity-acme.sty's \swissfootformat is
    # "\meta{docid} . \meta{version} . \meta{date}"; acme-demo.tex sets
    # docid=TR-2026-014 via \swissmeta. The cover page uses
    # \thispagestyle{swisstitle} (empty foot), so this must be checked on a
    # CONTENT page, not page 1.
    r = build_doc(DOC, tmp_path)
    assert r.returncode == 0, r.log[-3000:]
    with pdfplumber.open(r.pdf) as p:
        assert len(p.pages) >= 2, "expected a cover page plus content"
        content_foot_words = [w for pg in p.pages[1:] for w in _bottom_words(pg)]
    joined = " ".join(content_foot_words)
    assert "TR-2026-014" in joined, content_foot_words


def test_acme_classification_mark_intern_on_content_page(tmp_path):
    # classification=internal -> \swiss@classlevel>0 -> the foot's
    # classification mark renders via \tracked (\MakeUppercase + letter-
    # spacing) on every content page, mirroring tests/test_foot.py's own
    # "INTERN" assertion for the identity-free case.
    r = build_doc(DOC, tmp_path)
    assert r.returncode == 0, r.log[-3000:]
    with pdfplumber.open(r.pdf) as p:
        content_foot_words = [w for pg in p.pages[1:] for w in _bottom_words(pg)]
    assert any("INTERN" in w for w in content_foot_words), content_foot_words


def test_acme_demo_passes_swisscheck(tmp_path):
    r = build_doc(DOC, tmp_path)
    assert r.returncode == 0, r.log[-3000:]
    code, out = swisscheck(r.pdf)
    assert code == 0, out


def test_acme_logo_pdf_exists_and_is_single_page():
    # Committed build artifact (like acme-demo.pdf itself) -- not rebuilt by
    # this test, just sanity-checked so a stale/corrupt commit fails loudly.
    logo = ROOT / "acme-logo.pdf"
    assert logo.exists(), logo
    with pdfplumber.open(logo) as p:
        assert len(p.pages) == 1


# --- C4: \swissidentitymeta und der colophon=-Slot sind keine tote Konfiguration ---

def test_acme_colophon_carries_identity_line(tmp_path):
    # \swissidentitymeta (company/legal/web) und der colophon=-Schlüssel von
    # \swisslogofiles waren bis zu dieser Änderung zwar setzbar, aber von
    # keiner Stelle der Klasse gelesen. Das Kolophon liest jetzt beides --
    # acme-demo ist der End-zu-End-Beleg, weil seine Identität beide setzt.
    r = build_doc(DOC, tmp_path)
    assert r.returncode == 0, r.log[-3000:]
    with pdfplumber.open(r.pdf) as p:
        letzte = (p.pages[-1].extract_text() or "").replace(" ", "")
    assert "AcmeAG" in letzte, letzte
    assert "HRB12345" in letzte, letzte
    assert "acme.example" in letzte, letzte


def test_acme_colophon_carries_the_mark(tmp_path):
    # Die Marke steht rechtsbündig auf dem vollen Mass, eine Rasterzeile
    # hoch. acme-logo.pdf ist Vektorgrafik und landet als Form-XObject, dessen
    # Inhalt pdfplumber als gewöhnliche Zeichen aufschlüsselt (siehe die
    # Begründung in swisscheck.py bei A11) -- geprüft wird darum die Lage des
    # Markentexts, nicht ein image-Eintrag.
    r = build_doc(DOC, tmp_path)
    assert r.returncode == 0, r.log[-3000:]
    mm, pt = 72 / 25.4, 72 / 72.27
    rechte_kante = (24.0 + 30.0 + 7.0 + 105.0) * mm      # volles Mass
    # Die Logodatei hat rechts von ihrem Satz einen eigenen Rand. Rechts-
    # bündig heisst: die rechte Kante der DATEI liegt auf dem vollen Mass --
    # der Markentext endet um genau diesen (mitskalierten) Dateirand davor.
    # Der Erwartungswert wird darum aus der Quelldatei berechnet, statt eine
    # grosszügige Toleranz zu raten.
    with pdfplumber.open(ROOT / "acme-logo.pdf") as q:
        quelle = q.pages[0]
        breit = [w for w in quelle.extract_words()
                 if w["text"].upper().startswith("ACME")]
        assert breit, "acme-logo.pdf enthaelt keinen Markentext"
        rand_quelle = quelle.width - max(w["x1"] for w in breit)
        hoehe_quelle = quelle.height
    skala = (13.5 * pt) / hoehe_quelle                   # Zielhöhe = 1 Rasterzeile
    with pdfplumber.open(r.pdf) as p:
        seite = p.pages[-1]
        marken = [w for w in seite.extract_words()
                  if w["text"].upper().startswith("ACME")
                  and w["top"] > seite.height / 2]
    assert marken, "keine Kolophonmarke auf der letzten Seite"
    unterste = max(marken, key=lambda w: w["top"])
    erwartet = rechte_kante - rand_quelle * skala
    assert abs(unterste["x1"] - erwartet) < 1.0, (unterste, erwartet, rechte_kante)


def test_colophon_without_identity_stays_unchanged(tmp_path):
    # Gegenprobe: ohne Identität gibt es weder Identitätszeile noch Marke --
    # die Erweiterung darf ein Dokument ohne identity= nicht verändern.
    fx = tmp_path / "plaincolo.tex"
    fx.write_text(r"""\documentclass{swisstex}
\begin{document}
\section{Abschnitt}
Grundtext auf dem Raster mit genug Woertern fuer eine volle Zeile.
\colophon{Nur der eigene Text.}
\end{document}""")
    r = build_doc(fx, tmp_path)
    assert r.returncode == 0, r.log[-3000:]
    with pdfplumber.open(r.pdf) as p:
        # 7 pt Schmalschrift: der Wortabstand liegt unter pdfplumbers
        # Vorgabetoleranz, extract_text klebt die Wörter zusammen. Verglichen
        # wird darum die leerzeichenfreie Form (wie in tests/test_strings.py).
        text = (p.pages[-1].extract_text() or "").replace(" ", "")
    assert "NurdereigeneText." in text, text
    schwanz = text.split("NurdereigeneText.")[-1]
    assert "·" not in schwanz, schwanz
    assert "ACME" not in schwanz, schwanz


def test_missing_colophon_logo_warns_but_builds(tmp_path):
    # Ein Kolophon ist Beiwerk: eine fehlende Markendatei darf den Bau eines
    # fertigen Dokuments nicht abbrechen (anders als bei \swisslogo, wo die
    # Datei ausdrücklich angefordert wurde).
    fx = tmp_path / "nomark.tex"
    fx.write_text(r"""\documentclass{swisstex}
\swisslogofiles{colophon=gibtsnicht.pdf}
\begin{document}
\section{Abschnitt}
Grundtext auf dem Raster mit genug Woertern fuer eine volle Zeile.
\colophon{Text ohne Marke.}
\end{document}""")
    r = build_doc(fx, tmp_path)
    assert r.returncode == 0, r.log[-3000:]
    assert "Colophon logo" in r.log, r.log[-3000:]
    assert "Division by 0" not in r.log, r.log[-3000:]
