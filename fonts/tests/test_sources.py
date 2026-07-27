# fonts/tests/test_sources.py
import glob, sys
sys.path.insert(0, "fonts/tools")
from measurelib import analyze

EXPECTED = 8

def test_sources_present_and_parseable():
    paths = sorted(glob.glob("fonts/sources/u001/*.ttf"))
    assert len(paths) == EXPECTED
    for p in paths:
        r = analyze(p)
        assert r["upm"] == 2048

def test_license_present():
    assert open("fonts/sources/u001/Copying.AFPL.txt").read().strip()
