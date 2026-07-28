import sys

import pytest

sys.path.insert(0, "fonts/tools")
from fontTools.ttLib import TTFont

import config
import interpolate

PAIRS = [(0, 4), (1, 5), (2, 6), (3, 7)]  # indices into SOURCE_FILES: (upright, condensed)


def test_critical_glyphs_nonempty_and_sane():
    """Sanity check on the CRITICAL_GLYPHS set itself (not the audit
    verdict): it must actually contain the basics -- this is what would
    catch a broken codepoint->glyph-name resolution independently of
    whether the masters turn out compatible."""
    assert len(interpolate.CRITICAL_GLYPHS) > 90
    for must_have in ("A", "a", "zero", "period", "comma", "adieresis",
                       "germandbls", "endash", "Euro"):
        assert must_have in interpolate.CRITICAL_GLYPHS, must_have


def test_check_compatibility_returns_list_of_str():
    reg = TTFont(config.SOURCE_FILES[0])
    cond = TTFont(config.SOURCE_FILES[4])
    bad = interpolate.check_compatibility(reg, cond)
    assert isinstance(bad, list)
    assert all(isinstance(g, str) for g in bad)


@pytest.mark.xfail(
    strict=True,
    reason=(
        "BLOCKED per task-10 audit (see "
        ".superpowers/sdd/2026-07-27-font-program/task-10-report.md): "
        "U001's Condensed masters are NOT point-compatible with their "
        "Regular counterparts for the large majority of critical glyphs "
        "(86 of 142 CRITICAL_GLYPHS incompatible, union across all 4 "
        "style pairs -- essentially every round/curved letterform, most "
        "digits, and several required punctuation glyphs including "
        "Euro). Linear glyf-point interpolation between these masters is "
        "not implementable without improvising outlines, which is out of "
        "scope. Kept as strict xfail (not deleted) so that if a future "
        "U001 source revision redraws the masters to be point-compatible, "
        "this test starts unexpectedly passing (XPASS) and loudly fails "
        "the suite, flagging that the ruling should be revisited."
    ),
)
def test_masters_compatible():
    for r, c in PAIRS:
        reg, cond = TTFont(config.SOURCE_FILES[r]), TTFont(config.SOURCE_FILES[c])
        bad = interpolate.check_compatibility(reg, cond)
        # ASCII + Latin-1 + required punctuation must interpolate; report full list
        assert not [g for g in bad if g in interpolate.CRITICAL_GLYPHS], bad
