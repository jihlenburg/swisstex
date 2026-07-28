# SwissTeX Grotesk

Modified URW U001 (AFPL) — renamed to distinguish the modified fonts from
URW's originals. Sources in `sources/u001/` are pristine; every change is a
scripted transform in `tools/build.py`, tested in `tests/`.

## Provenance

Source: [FontLibrary](https://fontlibrary.org/en/font/u001), U001, URW's
Nimbus-Sans-alike released under the Aladdin Free Public License.
Downloaded 2026-07-27. The 8 source TTFs in `sources/u001/` are pristine
(byte-for-byte as downloaded); SHA-256 manifest:

```
8638bd5edeba39c9669694a227a6a2a7227fe8f9807b7e92e378dfd1a3c795b1  u001-bol.ttf
8744db3275f22059a5a3cc7a228c8185a3c5ec45f779b532520ce24e4558c1fe  u001-bolita.ttf
ff3c9390f6a5e9202a43d8e8ceca237afab58f7da055b73dffba705930285edd  u001-ita.ttf
8328ce80a73f6d62650269a22ed75ca1e1bb8491d6d9373d64a4c2734a42aeac  u001-reg.ttf
1cde63b214be59eadabad176047ee0a429b33748b1f5a5e8ead5a417205c73b5  u001con-bol.ttf
1536c2b92cd068e27f6bb768c88171aff7ad0e2b9d190d858cf434c1f1e71322  u001con-bolita.ttf
0dbab08ac974ce4895edf49db0f35e57a730d25a9fb9373bc686d2c897dc0906  u001con-ita.ttf
b288f9d7f0ca6985f79f010395d4187258c793674f033d7590cfd4efa7fd704c  u001con-reg.ttf
```

Recompute with `shasum -a 256 fonts/sources/u001/*.ttf` and diff against
this list if source integrity is ever in doubt.

## Build

Run from the **repo root** (paths in `tools/config.py` are anchored to it
via `os.path.dirname(__file__)`, so this also works from any CWD once the
venv exists):

```
python3 -m venv fonts/.venv && fonts/.venv/bin/pip install fonttools pytest
fonts/.venv/bin/python fonts/tools/build.py           # -> fonts/dist (all 8 styles)
fonts/.venv/bin/python fonts/tools/build.py install    # -> ~/Library/Fonts
```

`install` targets **macOS** (`~/Library/Fonts`) specifically — CoreText is
what XeTeX resolves family names through on this platform (see the root
`CLAUDE.md`). It copies the 8 dist TTFs plus `Copying.AFPL.txt`, asserts
exactly 8 TTFs were found before copying, and prints each file copied.

Fixes applied vs. U001: unified vertical metrics (USE_TYPO_METRICS),
italicAngle -17 (was wrong in 2 styles), conditional liga (fi/fl) with
GPOS/GDEF protected across the feaLib call (its delete-on-empty behavior
would otherwise drop them; the liga fea also declares `DFLT`/`latn`
languagesystems to match the source GSUB's script coverage). Identity
metadata (`step_identity`): vendor ID `SWTX`, `fsType` 0 (installable
embedding), name ID 0 rewritten to URW's original copyright text plus a
dated modification notice, the Font Squirrel/ttfautohint webfont-generator
stamps removed (name IDs 200/201/202/203/55555, the `webf`/`FFTM` tables),
and the 4 condensed styles get `usWidthClass` 3 / PANOSE `bProportion` 6.
URW's own GPOS kerning (968–993 pair records per style) is preserved
unchanged — a hand-curated pair analysis is retained as
`tools/kern-reference.fea` for documentation but is NOT compiled. Coverage
audit: all target codepoints (incl. Euro) already present in all 8 styles
— no glyphs were added. tnum omitted: digits are already tabular. Known
accepted deviation: Bold Italic runs 7.1% heavier than Bold; in the
condensed family the sign flips — CondBoldItalic runs 2.3% *lighter* than
CondBold.

License: Aladdin Free Public License (see sources/u001/Copying.AFPL.txt,
also shipped as dist/Copying.AFPL.txt). NOT for commercial redistribution
as a font — and NOT MIT (see the repo-root `LICENSE`'s "Third-party
components" section). Univers specimens and Universalis ADF were visual
references only; no outline or kerning data was copied from either.

## Known family inconsistency

Condensed compression (advance width of `n`, condensed vs. regular-width)
is **0.710** for Regular/Italic but **0.806** for Bold/BoldItalic — the
condensed bold cuts were drawn relatively wider by URW than the condensed
regular/italic cuts, so the two style pairs compress by different amounts.
This is a source-design characteristic, not a pipeline bug (dist ships the
native condensed cuts unchanged; see the interpolation-audit addendum in
`docs/superpowers/specs/2026-07-27-swisstex-generalization-design.md`).
The table heads still use the condensed bold cuts at their native
(wider-than-Regular's-condensed) width; the class layer works around the
narrower Regular/Italic condensed by moving glosses and marginalia to the
**regular-width** family at annotation grade instead of condensed, per the
spec addendum — condensed stays reserved for tables and the head/foot
apparatus, where the 0.806 pair is close enough to spec.

## Handoff to the class (v2.0)

`swisstex.cls` v1.3 loads the body fonts **by filename** inside
`\setmainfont`/`\newfontfamily\condensed` (`Extension = .otf`,
`UprightFont = *-regular`, lowercase `-italic`/`-bold`/`-bolditalic`
suffixes). `fonts/dist` ships **TTF**, not OTF, with **capitalized**
suffixes (`-Regular`, `-Italic`, `-Bold`, `-BoldItalic`) and no
`Extension = .otf` match. The class as shipped therefore cannot resolve
SwissTeX Grotesk by filename against this dist output. Both
`fonts/specimen/specimen.tex` and `fonts/specimen/legibility.tex` work
around this today by loading the **installed family name** instead
(`\setmainfont{SwissTeX Grotesk}`, `\renewfontfamily\condensed{SwissTeX
Grotesk Condensed}` after `fonts/tools/build.py install`) — that pattern,
or a generalization of the class's font-loading block to accept either
convention, is the outstanding integration work before the class can
default to SwissTeX Grotesk itself.

Separately, the `STEPS`/`ORDER` registry in `fonts/tools/build.py` is
built around single-font transforms — every step has the signature
`fn(font, filename)` and touches exactly one `TTFont` at a time. That
covers everything shipped so far (rename, identity, metrics, italic,
coverage, features), but it has no entry point for an operation that needs
**two masters at once**, such as the interpolation this program considered
and shelved (`fonts/tools/interpolate.py`, blocked — see
`.superpowers/sdd/2026-07-27-font-program/task-10-report.md`) or a future
harmonization pass across the Regular/Condensed compression asymmetry
above. That would need a second registry (or a step signature extended to
take a tuple of fonts) rather than fitting into `STEPS` as it stands.

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

**Masters' review (Frutiger axis, 2026-07-28): ADOPT-WITH-NAMED-FIX** —
outlines and kerning verified bit-faithful; named fixes (vendor ID,
webfont-stamp removal, modification notice, condensed width-class) applied
in this wave. Full report:
`.superpowers/sdd/2026-07-27-font-program/final-fix-report.md`.
