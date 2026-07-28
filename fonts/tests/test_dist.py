# fonts/tests/test_dist.py
"""Keeps the committed fonts/dist/*.ttf verifiably in sync with the
pipeline in fonts/tools/build.py -- if a build.py/config.py change lands
without a `python fonts/tools/build.py` rebuild, this is the test that
catches the drift (dist would otherwise silently ship stale output)."""
import os, sys, glob
sys.path.insert(0, "fonts/tools")
from fontTools.ttLib import TTFont
import build

# 'head' carries two fields that legitimately differ between two builds of
# the same inputs: the save-time timestamp, and the whole-file checksum
# that timestamp change cascades into. Every other head field must match.
HEAD_VOLATILE_FIELDS = {"modified", "checkSumAdjustment"}


def test_dist_matches_fresh_build(tmp_path):
    build.run(build.ORDER, str(tmp_path))

    dist_paths = sorted(glob.glob("fonts/dist/*.ttf"))
    assert len(dist_paths) == 8

    for dist_path in dist_paths:
        name = os.path.basename(dist_path)
        fresh_path = tmp_path / name
        assert fresh_path.exists(), f"{name}: build.py did not produce this file"

        dist_font = TTFont(dist_path)
        fresh_font = TTFont(str(fresh_path))

        dist_tags = set(dist_font.keys()) - {"GlyphOrder"}
        fresh_tags = set(fresh_font.keys()) - {"GlyphOrder"}
        assert dist_tags == fresh_tags, (name, dist_tags ^ fresh_tags)

        for tag in sorted(dist_tags):
            if tag == "head":
                d_head, f_head = dist_font["head"], fresh_font["head"]
                for field in vars(d_head):
                    if field in HEAD_VOLATILE_FIELDS:
                        continue
                    assert getattr(d_head, field) == getattr(f_head, field), \
                        (name, "head." + field)
                continue
            d_bytes = dist_font[tag].compile(dist_font)
            f_bytes = fresh_font[tag].compile(fresh_font)
            assert d_bytes == f_bytes, (name, tag)
