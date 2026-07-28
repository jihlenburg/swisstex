# fonts/tests/test_identity.py
"""Frutiger closing-review identity/provenance fixes (step_identity in
fonts/tools/build.py): vendor ID, embedding permission, webfont-generator
stamp removal, the AFPL-required modification notice, and the condensed
styles' width metadata. Checked directly against the shipped fonts/dist
files -- test_dist.py separately proves dist matches a fresh build."""
import glob, os, sys
sys.path.insert(0, "fonts/tools")
from fontTools.ttLib import TTFont
import config

WEBFONT_STAMP_NAME_IDS = {200, 201, 202, 203, 55555}
CONDENSED_OUT = {out for fam, sub, out in config.STYLE_MAP.values() if fam == config.FAMC}


def _dist_fonts():
    paths = sorted(glob.glob("fonts/dist/*.ttf"))
    assert len(paths) == 8
    return {os.path.splitext(os.path.basename(p))[0]: TTFont(p) for p in paths}


def test_vendor_id_and_embedding_permission():
    for base, f in _dist_fonts().items():
        os2 = f["OS/2"]
        assert os2.achVendID == "SWTX", base
        assert os2.fsType == 0, base


def test_webfont_generator_stamps_removed():
    for base, f in _dist_fonts().items():
        ids_present = {rec.nameID for rec in f["name"].names}
        assert not (ids_present & WEBFONT_STAMP_NAME_IDS), (base, ids_present & WEBFONT_STAMP_NAME_IDS)
        assert "webf" not in f, base
        assert "FFTM" not in f, base


def test_license_url_name_id_present():
    for base, f in _dist_fonts().items():
        url = f["name"].getDebugName(14)
        assert url == config.LICENSE_URL, (base, url)


def test_copyright_retains_original_notice_and_dates_the_change():
    for base, f in _dist_fonts().items():
        cp = f["name"].getDebugName(0) or ""
        assert "(URW)++" in cp, (base, cp)          # original notice retained
        assert "modified 2026-07-28" in cp, (base, cp)  # change dated
        assert "SwissTeX" in cp, (base, cp)


def test_condensed_styles_get_width_class_and_panose():
    for base, f in _dist_fonts().items():
        os2 = f["OS/2"]
        if base in CONDENSED_OUT:
            assert os2.usWidthClass == 3, base
            assert os2.panose.bProportion == 6, base
        else:
            # untouched by step_identity for non-condensed styles
            assert os2.usWidthClass != 3, base
            assert os2.panose.bProportion != 6, base
