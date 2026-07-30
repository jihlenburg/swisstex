from conftest import build_doc, ROOT

def test_identity_loads(tmp_path):
    r = build_doc(ROOT / "tests/fixtures/identity.tex", tmp_path)
    assert r.returncode == 0, r.log[-2000:]
    assert "swissidentity-test" in r.log          # package load line

def test_missing_identity_errors(tmp_path):
    fx = tmp_path / "miss.tex"
    fx.write_text(r"\documentclass[identity=nosuch]{swisstex}\begin{document}x\end{document}")
    r = build_doc(fx, tmp_path)
    assert r.returncode != 0
    assert "swissidentity-nosuch" in r.log

def test_unknown_classification_errors(tmp_path):
    fx = tmp_path / "cls.tex"
    fx.write_text(r"""\documentclass{swisstex}
\swissmeta{classification=topsecret}
\begin{document}x\end{document}""")
    r = build_doc(fx, tmp_path)
    assert r.returncode != 0 and "classification" in r.log

def test_band_defaults_to_accent(tmp_path):
    r = build_doc(ROOT / "tests/fixtures/plain.tex", tmp_path)
    assert r.returncode == 0
    # sidecar carries colors from Task 9; until then assert via log typeout
    assert "swiss:band=accent" in r.log

def test_band_own_when_identity_leaves_it_unset(tmp_path):
    # swissidentity-test.sty (used by identity.tex) sets accent but never
    # band -- the one-red rule must still apply with an identity loaded,
    # not just in the identity-free default case covered above.
    r = build_doc(ROOT / "tests/fixtures/identity.tex", tmp_path)
    assert r.returncode == 0, r.log[-2000:]
    assert "swiss:band=accent" in r.log

def test_band_option_bridges_to_own(tmp_path):
    # v1.3 compatibility: an explicit band= class option still wins over the
    # one-red default (rough edge #1 -- the option's OWN default changed
    # from 255,105,91 to empty, but passing it explicitly must still work).
    fx = tmp_path / "ownband.tex"
    fx.write_text(r"""\documentclass[band={255,105,91}]{swisstex}
\begin{document}x\end{document}""")
    r = build_doc(fx, tmp_path)
    assert r.returncode == 0, r.log[-2000:]
    assert "swiss:band=own" in r.log

def test_classlevel_index_and_meta_accessor(tmp_path):
    # \swiss@classlevel is a 0-based index into \swiss@classifications;
    # swissidentity-test.sty declares "public,internal", so "internal" is
    # index 1. \swiss@meta{client} was never set by identity.tex and must
    # expand to nothing rather than erroring.
    r = build_doc(ROOT / "tests/fixtures/identity.tex", tmp_path)
    assert r.returncode == 0, r.log[-2000:]
    assert "test:classlevel=1" in r.log
    assert "test:client=[]" in r.log

def test_footformat_stored_unexpanded(tmp_path):
    # swissidentity-test.sty calls \swissfootformat{\meta{docid}} although
    # \meta is not defined by Task 4 (it is bound at foot-typesetting time,
    # a later task) -- storing must not force expansion. identity_loads
    # already covers this via returncode==0, but this test names the
    # rough edge explicitly and would fail loudly ("Undefined control
    # sequence \meta") if \swissfootformat ever switched from \gdef to
    # \edef/\protected@edef.
    r = build_doc(ROOT / "tests/fixtures/identity.tex", tmp_path)
    assert r.returncode == 0, r.log[-2000:]
    assert "Undefined control sequence" not in r.log


def test_classifications_after_meta_revalidate(tmp_path):
    # D5: \swissclassifications darf eine bereits gesetzte Klassifizierung
    # nicht stehen lassen, die auf das ALTE Vokabular zeigt -- sonst trüge
    # die Fusszeile die Marke einer Stufe, die es nicht mehr gibt.
    fx = tmp_path / "stale.tex"
    fx.write_text(r"""\documentclass{swisstex}
\swissmeta{classification=confidential}
\swissclassifications{public,internal}
\begin{document}x\end{document}""")
    r = build_doc(fx, tmp_path)
    assert r.returncode != 0, r.log[-2000:]
    assert "Unknown classification" in r.log, r.log[-3000:]


def test_classifications_before_meta_still_works(tmp_path):
    # Gegenprobe: die übliche Reihenfolge (Vokabular zuerst) darf durch die
    # Nachprüfung nicht kaputtgehen -- und ohne gesetzte Klassifizierung ist
    # der zusätzliche Aufruf ein No-op.
    fx = tmp_path / "order.tex"
    fx.write_text(r"""\documentclass{swisstex}
\swissclassifications{open,restricted}
\swissstringkeys{classification-open, classification-restricted}
\swisssetstrings{german}{classification-open=Offen,
  classification-restricted=Gesperrt}
\swissmeta{classification=restricted}
\begin{document}x\end{document}""")
    r = build_doc(fx, tmp_path)
    assert r.returncode == 0, r.log[-3000:]
