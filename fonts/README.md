# SwissTeX Grotesk

Modified URW U001 (AFPL) — renamed as the license requires. Sources in
`sources/u001/` are pristine; every change is a scripted transform in
`tools/build.py`, tested in `tests/`.

Build: `python3 -m venv .venv && .venv/bin/pip install fonttools pytest`
then `.venv/bin/python tools/build.py` (dist) and `... build.py install`
(copies to ~/Library/Fonts for XeTeX/CoreText name lookup).

Fixes applied vs. U001: unified vertical metrics (USE_TYPO_METRICS),
italicAngle -17 (was wrong in 2 styles), conditional liga (fi/fl) with
GPOS/GDEF protected across the feaLib call (its delete-on-empty behavior
would otherwise drop them). URW's own GPOS kerning (~970-990 pair records
per style) is preserved unchanged — a hand-curated pair analysis is
retained as `tools/kern-reference.fea` for documentation but is NOT
compiled. Coverage audit: all target codepoints (incl. Euro) already
present in all 8 styles — no glyphs were added. tnum omitted: digits are
already tabular. Known accepted deviation: Bold Italic runs ~6.6% heavier
than Bold.

License: Aladdin Free Public License (see sources/u001/Copying.AFPL.txt).
NOT for commercial redistribution as a font. Univers specimens and
Universalis ADF were visual references only; no outline or kerning data
was copied from either.
