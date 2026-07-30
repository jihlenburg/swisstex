import pdfplumber
import pytest
from conftest import build_doc, swisscheck, ROOT

def test_foot_line(tmp_path):
    r = build_doc(ROOT / "tests/fixtures/foot.tex", tmp_path)
    assert r.returncode == 0, r.log[-2000:]
    with pdfplumber.open(r.pdf) as p:
        page = p.pages[0]
        foot = [w["text"] for w in page.extract_words() if w["top"] > page.height - 60]
    assert any("D-77" in w for w in foot), foot
    assert any("INTERN" in w for w in foot), foot

def test_public_prints_nothing(tmp_path):
    fx = tmp_path / "pub.tex"
    fx.write_text((ROOT / "tests/fixtures/foot.tex").read_text()
                  .replace("classification=internal", "classification=public"))
    r = build_doc(fx, tmp_path)
    assert r.returncode == 0, r.log[-2000:]
    with pdfplumber.open(r.pdf) as p:
        page = p.pages[0]
        foot = [w["text"] for w in page.extract_words() if w["top"] > page.height - 60]
    # Classification mark must not appear for public classification
    foot_text = " ".join(foot)
    assert "ffentlich" not in foot_text and "Public" not in foot_text
    # But metadata line must still render
    assert any("D-77" in w for w in foot), foot


# --- A2: die Klassifizierungsmarke bleibt in der Marginalspalte -------------
#
# "Streng vertraulich" / "Strictly confidential" sind die längsten Stufen des
# ausgelieferten Vokabulars. Gesperrt im Kennzeichnungsgrad massen sie 55,4 bzw.
# 58,6 mm ab Papierkante und liefen damit über die Zonengrenze bei 54 mm
# (outermargin 24 + margincolumn 30) in den Bund -- swisscheck A4 und A10
# meldeten das zu Recht (empirisch reproduziert gegen die Klasse vor dieser
# Änderung). Die Klasse hält die Marke jetzt selbst in \margincolumn, indem sie
# in festen Stufen erst die Sperrung, dann den Grad zurücknimmt.

MM = 72 / 25.4


def _mark_word(pdf_path, teil):
    with pdfplumber.open(pdf_path) as p:
        page = p.pages[0]
        for w in page.extract_words(extra_attrs=["size"]):
            if w["top"] > page.height - 60 and teil in w["text"]:
                return w
    return None


def test_strict_mark_stays_in_margin_column_de(tmp_path):
    r = build_doc(ROOT / "tests/fixtures/strict-de.tex", tmp_path)
    assert r.returncode == 0, r.log[-2000:]
    w = _mark_word(r.pdf, "STRENG")
    assert w is not None, "keine Klassifizierungsmarke in der Fusszeile"
    assert w["x0"] / MM == pytest.approx(24.0, abs=0.5)
    assert w["x1"] / MM <= 54.0, w


def test_strict_mark_stays_in_margin_column_en(tmp_path):
    r = build_doc(ROOT / "tests/fixtures/strict-en.tex", tmp_path)
    assert r.returncode == 0, r.log[-2000:]
    w = _mark_word(r.pdf, "STRICTLY")
    assert w is not None, "keine Klassifizierungsmarke in der Fusszeile"
    assert w["x1"] / MM <= 54.0, w
    # Die englische Stufe passt erst eine Stufe kleiner -- die Leiter muss
    # tatsächlich greifen, nicht bloss vorhanden sein.
    assert w["size"] < 7.0, w


def test_strict_fixtures_pass_swisscheck(tmp_path):
    for name in ("strict-de.tex", "strict-en.tex"):
        r = build_doc(ROOT / "tests/fixtures" / name, tmp_path)
        assert r.returncode == 0, (name, r.log[-2000:])
        code, out = swisscheck(r.pdf)
        assert code == 0, (name, out)


def test_short_mark_keeps_full_tracking(tmp_path):
    # Gegenprobe: "Intern" passt mühelos und darf darum NICHT verkleinert
    # werden -- die Anpassung ist eine Notbremse, keine Dauereinstellung.
    r = build_doc(ROOT / "tests/fixtures/foot.tex", tmp_path)
    assert r.returncode == 0, r.log[-2000:]
    w = _mark_word(r.pdf, "INTERN")
    assert w is not None
    assert w["size"] == pytest.approx(7.5 * 72 / 72.27, abs=0.1), w
