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

from conftest import build_doc, swisscheck, ROOT
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
    assert "??" not in r.log, r.log[-3000:]


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
