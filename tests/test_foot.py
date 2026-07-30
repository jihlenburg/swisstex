from conftest import build_doc, ROOT
import pdfplumber

def test_foot_line(tmp_path):
    r = build_doc(ROOT / "tests/fixtures/foot.tex", tmp_path)
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
    with pdfplumber.open(r.pdf) as p:
        page = p.pages[0]
        foot = [w["text"] for w in page.extract_words() if w["top"] > page.height - 60]
    # Classification mark must not appear for public classification
    foot_text = " ".join(foot)
    assert "ffentlich" not in foot_text and "Public" not in foot_text
    # But metadata line must still render
    assert any("D-77" in w for w in foot), foot
