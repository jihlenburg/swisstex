import re
from conftest import build_doc, swisscheck, ROOT

def test_class_is_v2(tmp_path):
    r = build_doc(ROOT / "tests/fixtures/plain.tex", tmp_path)
    assert r.returncode == 0, r.log[-2000:]
    assert "v2.0.0" in r.log

def test_doctrine_lengths_in_log(tmp_path):
    # class \typeout's the derived lengths (added this task) for machine checking
    r = build_doc(ROOT / "tests/fixtures/plain.tex", tmp_path)
    assert re.search(r"swiss:annotationleading=9\.0pt", r.log)
    assert re.search(r"swiss:glossleading=10\.125pt", r.log)
    assert re.search(r"swiss:footnoteleading=10\.125pt", r.log)
    assert re.search(r"swiss:headsep=27\.0pt", r.log)
    assert re.search(r"swiss:footskip=40\.5pt", r.log)

def test_override_option(tmp_path):
    fx = tmp_path / "ov.tex"
    fx.write_text(r"""\documentclass[glossleading=11pt]{swisstex}
\begin{document}x\marg{g}\end{document}""")
    r = build_doc(fx, tmp_path)
    assert re.search(r"swiss:glossleading=11\.0pt", r.log)

def test_fixture_passes_swisscheck(tmp_path):
    r = build_doc(ROOT / "tests/fixtures/plain.tex", tmp_path)
    code, out = swisscheck(r.pdf)
    assert code == 0, out
