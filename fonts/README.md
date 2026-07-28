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

## QA (2026-07-28)

**Regression:** `tests/test_regression.py` — PASS. All 8 dist styles have
outlines (stems, H-bar, advance widths) bit-identical to their sources;
Appendix A values hold for Regular (stem_mean 94.4, xh/ch 0.69). The
pipeline touches only name/OS2/hhea/post/glyf-header-bbox metadata and
GSUB liga (GPOS/GDEF preserved); no glyf point data was ever written.

**fontbakery** (`check-universal`, all 8 dist TTFs; 0 ERROR/FATAL
throughout): started at 52 FAIL / 73 WARN. Fixed 3 metadata-level FAIL
checks by extending `step_rename`/`step_metrics` in `tools/build.py`, then
rebuilt dist and reran the full suite (still 20 passed + 1 xfailed):
- `opentype/font_version` (8): `head.fontRevision` (~1.04999, inherited)
  now matches the nameID 5 version string (2.0).
- `opentype/family/underline_thickness` (1): `post.underlineThickness`
  varied 104/105 by style, inherited from the sources; unified on
  Regular's value (105) — a `post` table scalar, not an outline edit.
- `ttx_roundtrip` (8): sources ship OS/2 version 1, which doesn't define
  fsSelection bits 7-9 (incl. USE_TYPO_METRICS, set since Task 3). Bumped
  OS/2 to version 4 and populated the newly-required fields; sCapHeight/
  sxHeight are read from the untouched glyf bbox of 'H'/'x', verified
  byte-identical to measurelib's own fallback measurement for all 8
  sources, so this cannot and does not perturb the regression numbers.
  Side effect (not a defect): loading `font["glyf"]` here caused
  `font.save()` to recompile glyf headers via fontTools' own
  `recalcBounds()` instead of passing the table through as raw source
  bytes; this corrected a handful of stale/imprecise bbox headers
  inherited from the source (fixed the `points_out_of_bounds` and `ots`
  WARNs below as a bonus) while leaving every point coordinate untouched
  — confirmed by the regression test, which reads points, not headers.
- `opentype/xavgcharwidth` WARN (8, self-inflicted by the version 4 bump:
  the expected-value formula changes at OS/2 v3): recomputed
  `xAvgCharWidth` as the mean of all positive-width glyphs, the formula
  version>=3 fonts are held to.

After fixes: 35 FAIL / 57 WARN. Two of the remaining FAIL check-types
(`opentype/family/consistent_family_name`, `typographic_family_name`, 1
each) are not real defects: SwissTeX Grotesk and SwissTeX Grotesk
Condensed are two deliberately distinct typographic families, and these
checks only fire because both families' dist files are checked in one
`check-universal` invocation; verified 0 FAILs for both when each family
is checked on its own. The remaining 32 FAILs need outline/kerning
changes or reverse a documented product decision, so per scope they were
**not** fixed — reported here for the controller:
- `case_mapping` (8): Greek lowercase glyphs present without uppercase
  counterparts — would require drawing new glyphs.
- `no_mac_entries` (8): wants Mac-platform (1,0,0) name-table entries
  removed. These exist by deliberate design (Task 2 brief, `_set()` in
  `build.py`) for XeTeX/CoreText name lookup on macOS per this repo's
  CLAUDE.md — removing them would undo that requirement, not fix a bug.
- `tabular_kerning` (8): kerning, explicitly out of scope; URW's kerning
  ships unmodified per the Task 6 user ruling.
- `valid_glyphnames` (8): box-drawing glyphs use bare-hex names
  (`2500`, `250c`, ...) inherited from the pristine U001 source — fixing
  means renaming glyph identities across all 8 fonts, out of scope for a
  metadata pass.
- `opentype/STAT/ital_axis` (1): wants a STAT table with an `ital` axis.
  These are 8 static instances, not variable fonts; adding a STAT table
  is a new-table addition, not a metadata field patch.

WARN-level findings (57, recorded per instructions, not chased):
`alt_caron`\*8, `contour_count`\*8, `ligature_carets`\*8,
`math_signs_width`\*8, `soft_hyphen`\*8, `typoascender_exceeds_Agrave`\*8,
`unreachable_glyphs`\*8, `overlapping_path_segments`\*1 — all inherited
source-design characteristics (contour counts, missing ligature carets,
a soft-hyphen glyph present, typoAscender vs. /Agrave headroom, a few
glyphs unreachable by cmap/GSUB, one overlapping-path glyph), none
touching name/metadata.

Full detail (fontbakery FAIL/WARN tallies with check IDs, self-review):
`.superpowers/sdd/2026-07-27-font-program/task-9-report.md`.
