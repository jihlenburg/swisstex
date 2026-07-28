# SwissTeX Grotesk Font Program Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Turn the 8 URW U001 TTFs into "SwissTeX Grotesk" / "SwissTeX Grotesk Condensed" — renamed, metrics-unified, metadata-repaired, coverage-completed, kerned — plus the legibility specimen that gates the v2.0 derivation-doctrine constants.

**Architecture:** A scripted, reproducible pipeline (`fonts/tools/build.py`) reads pristine sources from `fonts/sources/u001/`, applies ordered transforms (rename → vertical metrics → italicAngle → coverage → kern/liga), and writes `fonts/dist/`. Sources are never edited; every transform is pytest-verified against measured values. The specimen is a SwissTeX document that doubles as the doctrine's legibility gate.

**Tech Stack:** Python 3 + fontTools (+ pytest); XeLaTeX for specimens; `swisscheck.py` for grid conformance; fontbakery for final QA.

## Global Constraints

- Never pay for fonts or tools (spec §2.1).
- AFPL: modified fonts MUST be renamed (done: "SwissTeX Grotesk"); `Copying.AFPL.txt` ships alongside sources and dist; no commercial distribution of the fonts themselves.
- **License firewall:** no outline or kerning data from Universalis ADF or any Univers specimen enters the pipeline — visual reference only (spec §3.5).
- Outlines are untouched except newly composed glyphs: the measurement regression (Task 9) proves stems/slants of existing glyphs are bit-identical to sources.
- Source fonts: upm 2048; measured reference values in spec Appendix A.
- All commits: `git commit` then `git push origin main` (standing authorization).
- Python env: `fonts/.venv` (gitignored), `pip install fonttools pytest`; fontbakery added in Task 9 only.
- Run all commands from the repo root `/Users/jihlenburg/swisstex`.

## File Structure

```
fonts/
  sources/u001/            # 8 pristine TTFs + Copying.AFPL.txt (committed, never edited)
  tools/
    measurelib.py          # measurement library (from scratchpad measure_stems.py)
    build.py               # pipeline driver: subcommands rename|metrics|italic|coverage|features|all
    config.py              # name maps, metric strategy, italic targets, glyph recipes, kern table
    kern.fea               # curated kern feature source
  tests/
    test_sources.py        # Task 1
    test_rename.py         # Task 2
    test_metrics.py        # Task 3
    test_italic.py         # Task 4
    test_coverage.py       # Task 5
    test_features.py       # Task 6
    test_regression.py     # Task 9
  build/                   # intermediate (gitignored)
  dist/                    # final fonts (committed)
  specimen/
    specimen.tex           # character set + style matrix, per style
    legibility.tex         # the doctrine gate: footnote & condensed comparisons
  README.md                # provenance, license, build instructions
```

---

### Task 1: Sources import and tooling scaffold

**Files:**
- Create: `fonts/sources/u001/` (8 TTFs + `Copying.AFPL.txt` — copy from scratchpad `u001/fonts/`, re-download from FontLibrary `https://fontlibrary.org/en/font/u001` if scratchpad is gone)
- Create: `fonts/tools/measurelib.py` (move of scratchpad `measure_stems.py`, unchanged logic)
- Create: `fonts/tests/test_sources.py`
- Modify: `.gitignore` (append `fonts/.venv/` and `fonts/build/`)

**Interfaces:**
- Produces: `measurelib.analyze(path) -> dict` with keys `name, upm, xh, ch, stems, stem_mean, stem_cv, hbar, post_italic, meas_italic, adv_n` (exact dict the scratchpad script printed); `measurelib.italic_slant(font, xh)`, `measurelib.stem_widths(font, xh, ch)` for later tasks.
- Produces: `SOURCES = fonts/sources/u001/{u001-reg,u001-ita,u001-bol,u001-bolita,u001con-reg,u001con-ita,u001con-bol,u001con-bolita}.ttf` — the canonical 8-path list, exported as `config.SOURCE_FILES` in Task 2.

- [ ] **Step 1: Create env and copy sources**

```bash
mkdir -p fonts/sources/u001 fonts/tools fonts/tests fonts/build fonts/dist fonts/specimen
cp /private/tmp/claude-501/-Users-jihlenburg-swisstex/0b3bcc46-81af-4ae9-a824-0af4a0f122f5/scratchpad/u001/fonts/*.ttf fonts/sources/u001/
cp /private/tmp/claude-501/-Users-jihlenburg-swisstex/0b3bcc46-81af-4ae9-a824-0af4a0f122f5/scratchpad/u001/fonts/Copying.AFPL.txt fonts/sources/u001/
cp /private/tmp/claude-501/-Users-jihlenburg-swisstex/0b3bcc46-81af-4ae9-a824-0af4a0f122f5/scratchpad/measure_stems.py fonts/tools/measurelib.py
python3 -m venv fonts/.venv && fonts/.venv/bin/pip install fonttools pytest
printf 'fonts/.venv/\nfonts/build/\n' >> .gitignore
```

- [ ] **Step 2: Write the failing test**

```python
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
```

- [ ] **Step 3: Run test**

Run: `fonts/.venv/bin/pytest fonts/tests/test_sources.py -v`
Expected: PASS (sources were copied in Step 1; if FAIL on import, `measurelib.py` still has the `if __name__` CLI block — that is fine, only the import path matters)

- [ ] **Step 4: Commit**

```bash
git add fonts .gitignore && git commit -m "feat(fonts): import pristine U001 sources and measurement library" && git push origin main
```

### Task 2: Rename and style-link

**Files:**
- Create: `fonts/tools/config.py`
- Create: `fonts/tools/build.py`
- Create: `fonts/tests/test_rename.py`

**Interfaces:**
- Produces: `config.SOURCE_FILES: list[str]` (8 paths, order: reg, ita, bol, bolita, con-reg, con-ita, con-bol, con-bolita); `config.STYLE_MAP: dict[filename -> (family, subfamily, out_name)]`; `build.load(path) -> TTFont`, `build.step_rename(font, filename) -> None`, `build.run(steps: list[str], out_dir: str)` writing `<out_dir>/<out_name>.ttf`.
- Produces: dist naming scheme `SwissTeXGrotesk-Regular.ttf`, `-Italic`, `-Bold`, `-BoldItalic`; `SwissTeXGroteskCond-Regular.ttf`, `-Italic`, `-Bold`, `-BoldItalic` (later tasks and the specimen rely on these exact file names).

- [ ] **Step 1: Write the failing test**

```python
# fonts/tests/test_rename.py
import sys
sys.path.insert(0, "fonts/tools")
from fontTools.ttLib import TTFont
import build, config

def _built(tmp_path):
    build.run(["rename"], str(tmp_path))
    return {p.name: TTFont(p) for p in tmp_path.glob("*.ttf")}

def test_names(tmp_path):
    fonts = _built(tmp_path)
    assert len(fonts) == 8
    f = fonts["SwissTeXGrotesk-Regular.ttf"]
    n = f["name"]
    assert n.getDebugName(1) == "SwissTeX Grotesk"
    assert n.getDebugName(2) == "Regular"
    assert n.getDebugName(4) == "SwissTeX Grotesk Regular"
    assert n.getDebugName(6) == "SwissTeXGrotesk-Regular"
    c = fonts["SwissTeXGroteskCond-BoldItalic.ttf"]
    assert c["name"].getDebugName(1) == "SwissTeX Grotesk Condensed"
    assert c["name"].getDebugName(2) == "Bold Italic"

def test_no_u001_string_remains(tmp_path):
    for name, f in _built(tmp_path).items():
        for rec in f["name"].names:
            if rec.nameID in (1, 2, 3, 4, 6, 16, 17):
                assert "U001" not in rec.toUnicode(), (name, rec.nameID)

def test_afpl_notice(tmp_path):
    for name, f in _built(tmp_path).items():
        lic = f["name"].getDebugName(13) or ""
        assert "Aladdin" in lic, name
```

- [ ] **Step 2: Run test to verify it fails**

Run: `fonts/.venv/bin/pytest fonts/tests/test_rename.py -v`
Expected: FAIL with `ModuleNotFoundError: build`

- [ ] **Step 3: Implement config and build**

```python
# fonts/tools/config.py
SRC = "fonts/sources/u001"
SOURCE_FILES = [f"{SRC}/{n}.ttf" for n in
    ["u001-reg", "u001-ita", "u001-bol", "u001-bolita",
     "u001con-reg", "u001con-ita", "u001con-bol", "u001con-bolita"]]

FAM, FAMC = "SwissTeX Grotesk", "SwissTeX Grotesk Condensed"
# filename -> (family, subfamily, output basename)
STYLE_MAP = {
    "u001-reg":       (FAM,  "Regular",     "SwissTeXGrotesk-Regular"),
    "u001-ita":       (FAM,  "Italic",      "SwissTeXGrotesk-Italic"),
    "u001-bol":       (FAM,  "Bold",        "SwissTeXGrotesk-Bold"),
    "u001-bolita":    (FAM,  "Bold Italic", "SwissTeXGrotesk-BoldItalic"),
    "u001con-reg":    (FAMC, "Regular",     "SwissTeXGroteskCond-Regular"),
    "u001con-ita":    (FAMC, "Italic",      "SwissTeXGroteskCond-Italic"),
    "u001con-bol":    (FAMC, "Bold",        "SwissTeXGroteskCond-Bold"),
    "u001con-bolita": (FAMC, "Bold Italic", "SwissTeXGroteskCond-BoldItalic"),
}
LICENSE_NOTE = ("Modified version of URW U001, renamed per the Aladdin Free "
                "Public License (AFPL). See Copying.AFPL.txt. Not for "
                "commercial distribution as a font.")
VERSION = "Version 2.000"
```

```python
# fonts/tools/build.py
import os, sys
sys.path.insert(0, os.path.dirname(__file__))
from fontTools.ttLib import TTFont
import config

def load(path):
    return TTFont(path)

def _set(name_table, nid, value):
    # Windows Unicode + Mac Roman, the two platforms real installers read
    name_table.setName(value, nid, 3, 1, 0x409)
    name_table.setName(value, nid, 1, 0, 0)

def step_rename(font, filename):
    fam, sub, out = config.STYLE_MAP[filename]
    n = font["name"]
    _set(n, 1, fam)
    _set(n, 2, sub)
    _set(n, 3, f"{config.VERSION};{out}")
    _set(n, 4, f"{fam} {sub}")
    _set(n, 5, config.VERSION)
    _set(n, 6, out)
    _set(n, 13, config.LICENSE_NOTE)
    # drop stale typographic-family overrides from the sources
    n.removeNames(nameID=16)
    n.removeNames(nameID=17)

STEPS = {"rename": step_rename}
ORDER = ["rename"]          # later tasks append: metrics, italic, coverage, features

def run(steps, out_dir):
    os.makedirs(out_dir, exist_ok=True)
    for path in config.SOURCE_FILES:
        filename = os.path.splitext(os.path.basename(path))[0]
        font = load(path)
        for s in [s for s in ORDER if s in steps]:
            STEPS[s](font, filename)
        _, _, out = config.STYLE_MAP[filename]
        font.save(os.path.join(out_dir, f"{out}.ttf"))

if __name__ == "__main__":
    run(sys.argv[1:] or ORDER, "fonts/build")
```

- [ ] **Step 4: Run test to verify it passes**

Run: `fonts/.venv/bin/pytest fonts/tests/test_rename.py -v`
Expected: PASS (3 tests)

- [ ] **Step 5: Commit**

```bash
git add fonts/tools fonts/tests/test_rename.py && git commit -m "feat(fonts): rename pipeline U001 -> SwissTeX Grotesk with style linking" && git push origin main
```

### Task 3: Vertical-metrics unification

**Files:**
- Modify: `fonts/tools/config.py` (append metrics strategy)
- Modify: `fonts/tools/build.py` (add `step_metrics`, extend `ORDER`)
- Create: `fonts/tests/test_metrics.py`

**Interfaces:**
- Consumes: `build.run`, `config.SOURCE_FILES` (Task 2 signatures).
- Produces: `build.step_metrics(font, filename)`; `config.metrics_targets() -> dict` with keys `typo_asc, typo_desc, line_gap, win_asc, win_desc` — computed once from the sources and cached, so all 8 outputs share identical values.

- [ ] **Step 1: Write the failing test**

```python
# fonts/tests/test_metrics.py
import sys
sys.path.insert(0, "fonts/tools")
from fontTools.ttLib import TTFont
import build

def test_unified_vertical_metrics(tmp_path):
    build.run(["rename", "metrics"], str(tmp_path))
    fonts = [TTFont(p) for p in sorted(tmp_path.glob("*.ttf"))]
    assert len(fonts) == 8
    ref = fonts[0]
    for f in fonts:
        assert f["OS/2"].sTypoAscender == ref["OS/2"].sTypoAscender
        assert f["OS/2"].sTypoDescender == ref["OS/2"].sTypoDescender
        assert f["OS/2"].sTypoLineGap == 0
        assert f["OS/2"].usWinAscent == ref["OS/2"].usWinAscent
        assert f["OS/2"].usWinDescent == ref["OS/2"].usWinDescent
        assert f["hhea"].ascent == ref["OS/2"].sTypoAscender
        assert f["hhea"].descent == ref["OS/2"].sTypoDescender
        assert f["hhea"].lineGap == 0
        assert f["OS/2"].fsSelection & (1 << 7)      # USE_TYPO_METRICS

def test_win_metrics_cover_all_glyphs(tmp_path):
    build.run(["rename", "metrics"], str(tmp_path))
    for p in tmp_path.glob("*.ttf"):
        f = TTFont(p)
        assert f["OS/2"].usWinAscent >= f["head"].yMax
        assert f["OS/2"].usWinDescent >= -f["head"].yMin
```

- [ ] **Step 2: Run test to verify it fails**

Run: `fonts/.venv/bin/pytest fonts/tests/test_metrics.py -v`
Expected: FAIL (step "metrics" unknown / metrics differ)

- [ ] **Step 3: Implement**

Append to `fonts/tools/config.py`:

```python
_metrics_cache = None
def metrics_targets():
    """typo = Regular's source values (canonical rhythm); win = union of
    extremes across all 8 (clipping guard). Computed once from sources."""
    global _metrics_cache
    if _metrics_cache is None:
        from fontTools.ttLib import TTFont
        fonts = [TTFont(p) for p in SOURCE_FILES]
        reg = fonts[0]
        _metrics_cache = dict(
            typo_asc=reg["OS/2"].sTypoAscender,
            typo_desc=reg["OS/2"].sTypoDescender,
            line_gap=0,
            win_asc=max(f["head"].yMax for f in fonts),
            win_desc=max(-f["head"].yMin for f in fonts),
        )
    return _metrics_cache
```

Append to `fonts/tools/build.py` (before `STEPS`):

```python
def step_metrics(font, filename):
    t = config.metrics_targets()
    os2, hhea = font["OS/2"], font["hhea"]
    os2.sTypoAscender = t["typo_asc"]
    os2.sTypoDescender = t["typo_desc"]
    os2.sTypoLineGap = t["line_gap"]
    os2.usWinAscent = t["win_asc"]
    os2.usWinDescent = t["win_desc"]
    os2.fsSelection |= (1 << 7)          # USE_TYPO_METRICS
    hhea.ascent = t["typo_asc"]
    hhea.descent = t["typo_desc"]
    hhea.lineGap = t["line_gap"]
```

and update the registries:

```python
STEPS = {"rename": step_rename, "metrics": step_metrics}
ORDER = ["rename", "metrics"]
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `fonts/.venv/bin/pytest fonts/tests/test_metrics.py fonts/tests/test_rename.py -v`
Expected: PASS (rename tests must still pass — regression guard)

- [ ] **Step 5: Commit**

```bash
git add fonts/tools fonts/tests/test_metrics.py && git commit -m "feat(fonts): unify vertical metrics across all 8 styles" && git push origin main
```

### Task 4: italicAngle and caret-slope repair

**Files:**
- Modify: `fonts/tools/config.py` (append `ITALIC_ANGLE = -17.0`, `ITALIC_FILES`)
- Modify: `fonts/tools/build.py` (add `step_italic`, extend registries)
- Create: `fonts/tests/test_italic.py`

**Interfaces:**
- Consumes: `measurelib.italic_slant`, `measurelib.metrics` (Task 1); `build.run` (Task 2).
- Produces: `build.step_italic(font, filename)`; `config.ITALIC_FILES = {"u001-ita", "u001-bolita", "u001con-ita", "u001con-bolita"}`.

- [ ] **Step 1: Write the failing test**

```python
# fonts/tests/test_italic.py
import sys, math
sys.path.insert(0, "fonts/tools")
from fontTools.ttLib import TTFont
import build, config, measurelib

def test_post_matches_drawn_slant(tmp_path):
    build.run(["rename", "metrics", "italic"], str(tmp_path))
    for p in tmp_path.glob("*.ttf"):
        f = TTFont(str(p))
        post = f["post"].italicAngle
        _, xh, _ = measurelib.metrics(f)
        drawn = measurelib.italic_slant(f, xh) or 0.0
        assert abs(post - drawn) < 0.7, (p.name, post, drawn)

def test_caret_slope(tmp_path):
    build.run(["rename", "metrics", "italic"], str(tmp_path))
    for p in tmp_path.glob("*Italic*.ttf"):
        f = TTFont(str(p))
        hhea = f["hhea"]
        expected_run = round(math.tan(math.radians(-f["post"].italicAngle)) * hhea.caretSlopeRise)
        assert abs(hhea.caretSlopeRun - expected_run) <= 1, p.name
```

- [ ] **Step 2: Run test to verify it fails**

Run: `fonts/.venv/bin/pytest fonts/tests/test_italic.py -v`
Expected: FAIL — the two broken styles (post −12/−11 vs drawn −17) exceed 0.7°

- [ ] **Step 3: Implement**

Append to `fonts/tools/config.py`:

```python
ITALIC_ANGLE = -17.0
ITALIC_FILES = {"u001-ita", "u001-bolita", "u001con-ita", "u001con-bolita"}
```

Append to `fonts/tools/build.py`:

```python
import math

def step_italic(font, filename):
    if filename not in config.ITALIC_FILES:
        return
    font["post"].italicAngle = config.ITALIC_ANGLE
    hhea = font["hhea"]
    hhea.caretSlopeRise = 1000
    hhea.caretSlopeRun = round(math.tan(math.radians(-config.ITALIC_ANGLE)) * 1000)
```

registries: `STEPS["italic"] = step_italic`, `ORDER = ["rename", "metrics", "italic"]`.

- [ ] **Step 4: Run all tests**

Run: `fonts/.venv/bin/pytest fonts/tests -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add fonts/tools fonts/tests/test_italic.py && git commit -m "fix(fonts): repair italicAngle metadata (-17deg drawn slant) and caret slope" && git push origin main
```

### Task 5: Coverage audit and composed glyphs

**Files:**
- Modify: `fonts/tools/config.py` (append `REQUIRED_CODEPOINTS`, `GLYPH_RECIPES`)
- Modify: `fonts/tools/build.py` (add `step_coverage`, extend registries)
- Create: `fonts/tests/test_coverage.py`

**Interfaces:**
- Consumes: `build.run` (Task 2).
- Produces: `build.step_coverage(font, filename)`; `config.REQUIRED_CODEPOINTS: dict[int, str]` (codepoint → glyph name).

- [ ] **Step 1: Write the audit + failing test**

```python
# fonts/tests/test_coverage.py
import sys
sys.path.insert(0, "fonts/tools")
from fontTools.ttLib import TTFont
import build, config

def test_required_codepoints_present(tmp_path):
    build.run(["rename", "metrics", "italic", "coverage"], str(tmp_path))
    for p in tmp_path.glob("*.ttf"):
        cmap = TTFont(str(p)).getBestCmap()
        missing = [hex(cp) for cp in config.REQUIRED_CODEPOINTS if cp not in cmap]
        assert not missing, (p.name, missing)

def test_composed_glyphs_sane(tmp_path):
    build.run(["rename", "metrics", "italic", "coverage"], str(tmp_path))
    for p in tmp_path.glob("*.ttf"):
        f = TTFont(str(p))
        cmap = f.getBestCmap()
        glyf, hmtx = f["glyf"], f["hmtx"]
        for cp in config.REQUIRED_CODEPOINTS:
            g = glyf[cmap[cp]]
            assert hmtx[cmap[cp]][0] > 0, (p.name, hex(cp))
            assert g.numberOfContours != 0 or g.isComposite(), (p.name, hex(cp))
```

- [ ] **Step 2: Run audit to learn what is actually missing**

Run: `fonts/.venv/bin/pytest fonts/tests/test_coverage.py -v` (after adding to config only `REQUIRED_CODEPOINTS`, Step 3a). The first failure lists the genuinely missing codepoints per style — 1990s URW TTFs typically already carry en/em dash, German quotes, ellipsis, permille; the euro (U+20AC) is the expected gap.
Expected: FAIL listing missing codepoints (record the list in the commit message)

- [ ] **Step 3a: Add the requirement table**

Append to `fonts/tools/config.py`:

```python
REQUIRED_CODEPOINTS = {
    0x2013: "endash", 0x2014: "emdash", 0x20AC: "Euro",
    0x201E: "quotedblbase", 0x201C: "quotedblleft", 0x201D: "quotedblright",
    0x201A: "quotesinglbase", 0x2018: "quoteleft", 0x2019: "quoteright",
    0x2026: "ellipsis", 0x2030: "perthousand",
}
```

- [ ] **Step 3b: Implement composition for the missing set**

Append to `fonts/tools/build.py` (recipes are rule-based composites from the font's own parts — no external outlines; shown for Euro, the expected gap; the same pattern extends to any other codepoint Step 2 reported):

```python
from fontTools.pens.ttGlyphPen import TTGlyphPen
from fontTools.pens.transformPen import TransformPen

def _euro_glyph(font):
    """Euro = 'C' + two horizontal bars at H-crossbar weight, per the
    font's own proportions. Pure construction from own parts."""
    glyf, hmtx = font["glyf"], font["hmtx"]
    cmap = font.getBestCmap()
    c_name = cmap[ord("C")]
    pen = TTGlyphPen(font.getGlyphSet())
    font.getGlyphSet()[c_name].draw(TransformPen(pen, (1, 0, 0, 1, 0, 0)))
    # bar geometry from the C's bbox and the H crossbar thickness
    c = glyf[c_name]
    h = glyf[cmap[ord("H")]]
    bar_h = max(160, (h.yMax - h.yMin) // 9)          # ~crossbar weight in 2048upm
    mid = (c.yMax + c.yMin) // 2
    width = hmtx[c_name][0]
    x0, x1 = -int(width * 0.05), int(width * 0.62)
    for off in (int(bar_h * 0.75), -int(bar_h * 0.75)):
        y0, y1 = mid + off - bar_h // 2, mid + off + bar_h // 2
        pen.moveTo((x0, y0)); pen.lineTo((x1, y0))
        pen.lineTo((x1, y1)); pen.lineTo((x0, y1)); pen.closePath()
    return pen.glyph(), width

RECIPES = {0x20AC: _euro_glyph}

def step_coverage(font, filename):
    cmap_table = font["cmap"]
    cmap = font.getBestCmap()
    for cp, gname in config.REQUIRED_CODEPOINTS.items():
        if cp in cmap:
            continue
        if cp not in RECIPES:
            raise ValueError(f"{filename}: missing {hex(cp)} and no recipe")
        glyph, width = RECIPES[cp](font)
        font["glyf"][gname] = glyph
        font["hmtx"][gname] = (width, 60)
        order = font.getGlyphOrder()
        if gname not in order:
            font.setGlyphOrder(order + [gname])
        for table in cmap_table.tables:
            if table.isUnicode():
                table.cmap[cp] = gname
```

registries: `STEPS["coverage"] = step_coverage`, `ORDER = [..., "coverage"]`. If Step 2 revealed more gaps than the euro, add a recipe per gap in the same construct-from-own-parts style (dashes: rectangles at crossbar weight on the median; quotes: comma translated/mirrored; ellipsis: three periods at period-advance spacing; perthousand: percent plus a copy of its lower zero).

- [ ] **Step 4: Run all tests**

Run: `fonts/.venv/bin/pytest fonts/tests -v`
Expected: PASS

- [ ] **Step 5: Visual check + commit**

Render the new glyphs once for eyes: `fonts/.venv/bin/python -c "..."` is NOT enough for shapes — instead build and open a quick XeLaTeX sheet: `printf '\\documentclass{article}\\usepackage{fontspec}\\setmainfont{[SwissTeXGrotesk-Regular.ttf]}[Path=fonts/build/]\\begin{document}\\Huge € – — „x“ ‚x' …‰\\end{document}' > fonts/build/qc.tex && xelatex -output-directory fonts/build fonts/build/qc.tex && open fonts/build/qc.pdf`

```bash
git add fonts/tools fonts/tests/test_coverage.py && git commit -m "feat(fonts): coverage completion via own-parts glyph composition (audit: <list from Step 2>)" && git push origin main
```

### Task 6: Kerning and ligature features

**Files:**
- Create: `fonts/tools/kern.fea`
- Modify: `fonts/tools/config.py` (append `KERN_UNIT` note), `fonts/tools/build.py` (add `step_features`)
- Create: `fonts/tests/test_features.py`

**Interfaces:**
- Consumes: `build.run`; stem means from spec Appendix A (Regular ≈ 92 units/2048upm) sizing the kern values.
- Produces: `build.step_features(font, filename)` compiling `kern.fea` via feaLib; `liga` only if `fi`/`fl` glyphs exist in the source (audit inside the step).

- [ ] **Step 1: Write the failing test**

```python
# fonts/tests/test_features.py
import sys
sys.path.insert(0, "fonts/tools")
from fontTools.ttLib import TTFont
import build

def test_kern_feature_compiled(tmp_path):
    build.run(["rename", "metrics", "italic", "coverage", "features"], str(tmp_path))
    for p in tmp_path.glob("*.ttf"):
        f = TTFont(str(p))
        assert "GPOS" in f, p.name
        feats = [fr.FeatureTag for fr in f["GPOS"].table.FeatureList.FeatureRecord]
        assert "kern" in feats, p.name

def test_av_pair_negative(tmp_path):
    build.run(["rename", "metrics", "italic", "coverage", "features"], str(tmp_path))
    from fontTools import subset  # noqa: F401  (ensures full lib available)
    f = TTFont(str(next(tmp_path.glob("*Grotesk-Regular.ttf"))))
    # smoke: GPOS present and non-empty is the machine check; the value
    # check happens visually in the specimen (Task 8)
    assert f["GPOS"].table.LookupList.LookupCount >= 1
```

- [ ] **Step 2: Run test to verify it fails**

Run: `fonts/.venv/bin/pytest fonts/tests/test_features.py -v`
Expected: FAIL (no GPOS / step unknown)

- [ ] **Step 3: Author kern.fea and the step**

```fea
# fonts/tools/kern.fea — curated pairs, values in 2048-upm units,
# scale ~= -0.55 x Regular stem (92) for the tightest cap pairs.
feature kern {
    pos A V -70;  pos V A -70;  pos A W -55;  pos W A -55;
    pos A Y -80;  pos Y A -80;  pos A T -75;  pos T A -75;
    pos F A -55;  pos P A -60;  pos L T -70;  pos L V -70;
    pos L Y -75;  pos T a -65;  pos T e -65;  pos T o -65;
    pos V a -50;  pos V e -50;  pos V o -50;  pos W a -40;
    pos W e -40;  pos W o -40;  pos Y a -70;  pos Y e -70;
    pos Y o -70;  pos r comma -60;  pos r period -60;
    pos v comma -50;  pos v period -50;  pos w comma -45;
    pos w period -45;  pos y comma -50;  pos y period -50;
    pos quoteright s -25;  pos f quoteright 30;
    pos one period -20;  pos seven period -55;  pos period seven -40;
} kern;
```

Append to `fonts/tools/build.py`:

```python
from fontTools.feaLib.builder import addOpenTypeFeaturesFromString

def step_features(font, filename):
    fea = open(os.path.join(os.path.dirname(__file__), "kern.fea")).read()
    glyphs = set(font.getGlyphOrder())
    if {"fi", "fl"} <= glyphs:
        fea += "\nfeature liga { sub f i by fi; sub f l by fl; } liga;\n"
    addOpenTypeFeaturesFromString(font, fea)
```

registries: `STEPS["features"] = step_features`, `ORDER = [..., "features"]`. (tnum: U001 digits are already uniform-advance — verified in the trial via `adv(n)`-style checks — so no tnum feature is needed; note this in README, Task 7.)

- [ ] **Step 4: Run all tests**

Run: `fonts/.venv/bin/pytest fonts/tests -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add fonts/tools fonts/tests/test_features.py && git commit -m "feat(fonts): curated kern feature + conditional liga" && git push origin main
```

### Task 7: Dist build, install helper, README

**Files:**
- Modify: `fonts/tools/build.py` (add `dist` entry point + install helper)
- Create: `fonts/README.md`
- Create: `fonts/dist/` (8 built TTFs, committed)

**Interfaces:**
- Consumes: full `ORDER` pipeline.
- Produces: `fonts/dist/*.ttf` (the 8 canonical names from Task 2); `python fonts/tools/build.py install` copying dist → `~/Library/Fonts/` (CoreText requirement per CLAUDE.md).

- [ ] **Step 1: Add dist + install commands**

Append to `fonts/tools/build.py` `__main__` block (replacing it):

```python
if __name__ == "__main__":
    import shutil, glob as _glob
    args = sys.argv[1:]
    if args[:1] == ["install"]:
        dest = os.path.expanduser("~/Library/Fonts")
        for p in _glob.glob("fonts/dist/*.ttf"):
            shutil.copy(p, dest)
        print("installed to", dest)
    else:
        run(args or ORDER, "fonts/dist" if not args else "fonts/build")
```

- [ ] **Step 2: Build dist and install**

Run: `fonts/.venv/bin/python fonts/tools/build.py && fonts/.venv/bin/python fonts/tools/build.py install`
Expected: 8 files in `fonts/dist/`, copied to `~/Library/Fonts/`; verify with `fc-scan --format "%{family}\n" ~/Library/Fonts/SwissTeXGrotesk-Regular.ttf` → `SwissTeX Grotesk`

- [ ] **Step 3: Write README**

```markdown
# SwissTeX Grotesk

Modified URW U001 (AFPL) — renamed as the license requires. Sources in
`sources/u001/` are pristine; every change is a scripted transform in
`tools/build.py`, tested in `tests/`.

Build: `python3 -m venv .venv && .venv/bin/pip install fonttools pytest`
then `.venv/bin/python tools/build.py` (dist) and `... build.py install`
(copies to ~/Library/Fonts for XeTeX/CoreText name lookup).

Fixes applied vs. U001: unified vertical metrics (USE_TYPO_METRICS),
italicAngle -17 (was wrong in 2 styles), euro + punctuation coverage,
curated kern, conditional liga. tnum omitted: digits are already tabular.
Known accepted deviation: Bold Italic runs ~6.6% heavier than Bold.
License: Aladdin Free Public License (see sources/u001/Copying.AFPL.txt).
NOT for commercial redistribution as a font. Univers specimens and
Universalis ADF were visual references only; no outline/kerning data
was copied from either.
```

- [ ] **Step 4: Full test suite, then commit dist**

Run: `fonts/.venv/bin/pytest fonts/tests -v`
Expected: PASS

```bash
git add fonts/dist fonts/README.md fonts/tools/build.py && git commit -m "feat(fonts): dist build + install helper + provenance README" && git push origin main
```

### Task 8: Specimen and the doctrine-gating legibility specimen

**Files:**
- Create: `fonts/specimen/specimen.tex`
- Create: `fonts/specimen/legibility.tex`

**Interfaces:**
- Consumes: installed dist fonts (Task 7); `swisstex.cls` v1.3 as-is (class loads them via explicit fontspec overrides below — no class change needed yet).
- Produces: `specimen.pdf` (style matrix + character set), `legibility.pdf` (the two gated comparisons); a recorded decision line appended to the spec (§8/§12.2) — this closes the two open constants.

- [ ] **Step 1: Write specimen.tex**

```latex
% fonts/specimen/specimen.tex — build: xelatex -output-directory=fonts/build specimen.tex
\documentclass[sans=SwissTeXGrotesk, sanscondensed=SwissTeXGroteskCond,
               sansname=SwissTeX Grotesk,
               sansnameitalic=SwissTeX Grotesk Italic]{swisstex}
% v1.3 loads by file base via kvoptions; the names above rely on the
% dist file naming from Task 2 and the ~/Library/Fonts install.
\setrunningtitle{SwissTeX Grotesk \textbar{} Specimen}
\begin{document}
\swisstitle{Specimen}{SwissTeX Grotesk}{Modernized U001, 8 styles}
\section{Style matrix}
Regular \textit{Italic} \textbf{Bold} \textbf{\textit{Bold Italic}}\par
{\condensed Condensed \textit{Italic} \textbf{Bold} \textbf{\textit{Bold Italic}}}
\section{Character set}
ABCDEFGHIJKLMNOPQRSTUVWXYZ abcdefghijklmnopqrstuvwxyz
0123456789 ÄÖÜäöüß – — € „Anführung“ ‚einfach` … ‰\par
Kernprobe: AV AW AY TA Ta Te To Va Wo Ya r, v. y. 7.4
\section{Grundtext}
Der Grundtext läuft im Flattersatz mit Trennung. Die Grotesk hält das
Basislinienraster von 13,5 Punkt über alle Schnitte, weil die
Vertikalmasse der acht Schnitte vereinheitlicht sind.
\colophon{SwissTeX Grotesk Specimen. Gesetzt mit swisstex v1.3.}
\end{document}
```

Note: `swisstex.cls` v1.3 appends `.otf` as `Extension` — dist ships TTF. Test the build; if fontspec errors on extension, load by family name instead: replace the class options with a preamble override `\AtBeginDocument{}` is NOT needed — simply use `sans` options pointing at installed *family names* via `sansname`, and if the file-base path fails, add after `\documentclass`: `\setmainfont{SwissTeX Grotesk}\newfontfamily\condensed{SwissTeX Grotesk Condensed}` (CoreText resolves the installed names; this override is the exact mechanism the future identity file formalizes).

- [ ] **Step 2: Write legibility.tex — the doctrine gate**

```latex
% fonts/specimen/legibility.tex — decides spec §8 constants
\documentclass{swisstex}
\setmainfont{SwissTeX Grotesk}
\newfontfamily\condensed{SwissTeX Grotesk Condensed}
\setrunningtitle{Legibility gate}
\begin{document}
\swisstitle{Prüfdruck}{Lesbarkeitsprobe}{Fussnoten- und Schmalsatz-Entscheid}
\section{Fussnotensatz: 8 auf 12 gegen 8 auf 10{,}125}
{\condensed\fontsize{8}{12}\selectfont
Die Wissenschaft hat festgestellt, dass die Trennlinie auf der Textachse
steht und die Fussnote in der Schmalschrift läuft. Zwölf Punkt Durchschuss
ist das bisherige Mass; es bindet erst nach acht Rasterzeilen wieder an.\par}
\gridskip{1}
{\condensed\fontsize{8}{10.125}\selectfont
Die Wissenschaft hat festgestellt, dass die Trennlinie auf der Textachse
steht und die Fussnote in der Schmalschrift läuft. Zehneinviertel Punkt
Durchschuss ist das starke Verhältnis drei zu vier; es bindet nach drei
Rasterzeilen wieder an.\par}
\section{Schmalsatz bei 0{,}71-Kompression}
\marg{Randglosse in der Schmalschrift bei voller Kompression: bleibt die
Type bei 7{,}5 Punkt offen genug?}
Der Grundtext dient als Umfeld. Zu prüfen ist die Marginalie links: wirken
die Binnenräume der komprimierten Schnitte bei Glossengrösse noch offen,
oder verlangt der Schmalsatz eine mildere Kompression durch Interpolation
innerhalb der eigenen Schnitte?
\colophon{Entscheid bitte im Spec §8/§12.2 nachtragen: Fussnotenmass und
Kompressionsfrage.}
\end{document}
```

- [ ] **Step 3: Build both, run swisscheck on the specimen**

Run: `cd fonts/specimen && timeout 300 xelatex -interaction=nonstopmode -output-directory=../build specimen.tex && timeout 300 xelatex -interaction=nonstopmode -output-directory=../build legibility.tex && cd ../.. && <venv-with-pdfplumber>/bin/python swisscheck.py fonts/build/specimen.pdf`
Expected: both PDFs build; swisscheck A2 (grid binding) passes — this is the machine proof of Task 3's metrics work; `pdffonts fonts/build/specimen.pdf` shows only SwissTeXGrotesk* families (+ LMMono until Plan 2's `\swisscode` lands — note, don't fix here)

- [ ] **Step 4: USER GATE — print/view and decide**

Present both PDFs to the user. Record their two decisions (footnote leading 10.125 vs 12; condensed acceptable vs interpolate) by appending a dated decision line to `docs/superpowers/specs/2026-07-27-swisstex-generalization-design.md` §8. Do not proceed to Task 9 without the recorded decision.

- [ ] **Step 5: Commit**

```bash
git add fonts/specimen docs/superpowers/specs && git commit -m "feat(fonts): specimen + legibility gate; record doctrine decisions" && git push origin main
```

### Task 9: Regression proof, fontbakery QA, masters' review

**Files:**
- Create: `fonts/tests/test_regression.py`
- Modify: `fonts/README.md` (QA results paragraph)

**Interfaces:**
- Consumes: `measurelib.analyze`; dist fonts; spec Appendix A expected values.

- [ ] **Step 1: Write the regression test (outlines untouched)**

```python
# fonts/tests/test_regression.py
import sys, glob
sys.path.insert(0, "fonts/tools")
from measurelib import analyze
import config

def test_outlines_unchanged_vs_sources():
    src = {c[2]: analyze(p) for p, c in
           zip(config.SOURCE_FILES, config.STYLE_MAP.values())}
    for p in glob.glob("fonts/dist/*.ttf"):
        base = p.split("/")[-1][:-4]
        d, s = analyze(p), src[base]
        assert d["stems"] == s["stems"], base          # bit-identical stems
        assert d["hbar"] == s["hbar"], base
        assert d["adv_n"] == s["adv_n"], base

def test_appendix_a_values_hold():
    r = analyze("fonts/dist/SwissTeXGrotesk-Regular.ttf")
    assert abs(r["stem_mean"] - 94.4) < 0.5
    assert abs(r["xh"] / r["ch"] - 0.69) < 0.02
```

- [ ] **Step 2: Run it**

Run: `fonts/.venv/bin/pytest fonts/tests/test_regression.py -v`
Expected: PASS (if FAIL: a pipeline step touched outlines — find and fix before anything else)

- [ ] **Step 3: fontbakery**

Run: `fonts/.venv/bin/pip install fontbakery && fonts/.venv/bin/fontbakery check-universal fonts/dist/*.ttf 2>&1 | tail -30`
Expected: no FAILs at ERROR level; fix name/metadata-level FAILs in the pipeline (rerun build + full pytest after any fix); WARN-level findings recorded in README, not chased.

- [ ] **Step 4: Masters' review pass (standing rule, spec §2.3)**

Dispatch a Frutiger devil's-advocate subagent on the built result (per the devils-advocate skill: counter-thesis "the modernization shipped drift instead of fixing it", anti-sycophancy gate, falsifiability, ADOPT/DON'T-ADOPT/ADOPT-WITH-NAMED-FIX), giving it `fonts/README.md`, the specimen PDFs, and the regression numbers. Record the verdict in `fonts/README.md` under "QA".

- [ ] **Step 5: Final commit**

```bash
git add fonts && git commit -m "test(fonts): regression proof + fontbakery QA + masters review verdict" && git push origin main
```

---

### Task 10: Gentler condensed by interpolation (added 2026-07-28 per legibility-gate ruling)

**Files:**
- Modify: `fonts/tools/config.py` (append `CONDENSED_T`, `CONDENSED_PAIRS`)
- Create: `fonts/tools/interpolate.py`
- Modify: `fonts/tools/build.py` (dist entry point routes condensed outputs through interpolation)
- Create: `fonts/tests/test_interpolate.py`

**Interfaces:**
- Consumes: `config.SOURCE_FILES`, `config.STYLE_MAP`, the full `ORDER` pipeline.
- Produces: `interpolate.check_compatibility(reg_font, cond_font) -> list[str]` (incompatible glyph names); `interpolate.interpolate_font(reg_font, cond_font, t) -> TTFont` (new font, glyf coords + advances linearly mixed); dist condensed TTFs whose `adv(n)` ratio vs Regular ≈ 0.80 ± 0.02.
- Ruling context: target compression ≈0.8. With native cond at 0.71: `t = (1.0 − 0.80)/(1.0 − 0.71) ≈ 0.69` measured from the Regular master toward the Condensed master, per weight/style pair (reg→cond, ita→cond-ita, bol→cond-bol, bolita→cond-bolita). Compute t per pair from the measured adv('n') ratio rather than hardcoding 0.69: `t = (1 − target)/(1 − adv_cond/adv_reg)` with target 0.80.

- [ ] **Step 1: Compatibility audit (gate for the whole task)**

Write `interpolate.check_compatibility`: for every glyph in the common glyph set of a Regular/Condensed pair, decompose composites, compare contour count and per-contour point count between the two masters. Write the failing test first:

```python
# fonts/tests/test_interpolate.py
import sys
sys.path.insert(0, "fonts/tools")
from fontTools.ttLib import TTFont
import config, interpolate

PAIRS = [(0, 4), (1, 5), (2, 6), (3, 7)]   # indices into SOURCE_FILES: (upright, condensed)

def test_masters_compatible():
    for r, c in PAIRS:
        reg, cond = TTFont(config.SOURCE_FILES[r]), TTFont(config.SOURCE_FILES[c])
        bad = interpolate.check_compatibility(reg, cond)
        # ASCII + Latin-1 + required punctuation must interpolate; report full list
        assert not [g for g in bad if g in interpolate.CRITICAL_GLYPHS], bad
```

`CRITICAL_GLYPHS` = A-Z, a-z, 0-9, German/FR/EN punctuation incl. the REQUIRED_CODEPOINTS glyph names. Run the audit. **If critical glyphs are incompatible, STOP: report BLOCKED with the list** — the ruling then needs re-examination (options: accept native 0.71 after all, or per-glyph fallbacks) and goes back to the user. Non-critical incompatible glyphs (rare symbols) fall back to the condensed master's outline verbatim, listed in the report.

- [ ] **Step 2: Implement interpolation**

```python
# fonts/tools/interpolate.py (core; measurelib for verification)
from fontTools.ttLib import TTFont
from fontTools.pens.recordingPen import DecomposingRecordingPen

def _points(font, gname):
    glyf = font["glyf"]
    g = glyf[gname]
    coords, ends, flags = g.getCoordinates(glyf)
    return list(coords), list(ends)

def check_compatibility(reg, cond):
    bad = []
    common = set(reg.getGlyphOrder()) & set(cond.getGlyphOrder())
    for gname in sorted(common):
        try:
            rc, re = _points(reg, gname)
            cc, ce = _points(cond, gname)
        except Exception:
            bad.append(gname); continue
        if re != ce or len(rc) != len(cc):
            bad.append(gname)
    return bad

def interpolate_font(reg, cond, t):
    """Return a new TTFont: cond metadata, coords/advances mixed reg→cond at t."""
    out = TTFont(cond.reader.file.name) if cond.reader else cond
    # implementer: load a fresh copy of the condensed master as the carrier,
    # then overwrite glyf coordinates and hmtx advances glyph-by-glyph:
    # new = (1-t)*reg + t*cond, rounded to int; skip incompatible glyphs.
    ...
```

The carrier is a fresh copy of the *condensed* master (keeps its GPOS kern, GDEF, cmap, names); coordinates and advances are overwritten with the interpolation. Kerning values in the carrier's GPOS remain the condensed master's — acceptable v1 (they are, if anything, slightly tight for 0.8; note in README). Sidebearings recompute from interpolated coords (set lsb = interpolated xMin per glyph, recalc bboxes via `glyf.recalcBounds`/save round-trip).

- [ ] **Step 3: Wire into dist + tests**

Dist routing: for the four condensed outputs, build.py loads reg+cond masters, produces the interpolated font, then applies the normal pipeline steps (rename/metrics/italic/coverage/features) to IT instead of the raw condensed source. Tests: `adv('n')` ratio vs built Regular = 0.80 ± 0.02 per style; stems (measurelib) between the two masters' values; x-height/cap unchanged (±1 unit); all 16 existing tests still green (test_regression in Task 9 will be adjusted — see contract note).

**Contract note for Task 9:** the regression test's "dist stems byte-identical to sources" clause now applies to the four UPRIGHT styles only; condensed dist styles assert against interpolation targets (adv ratio 0.80±0.02, stems strictly between master values) instead.

- [ ] **Step 4: Rebuild dist, reinstall, rebuild specimens**

Run the full dist build + install; rebuild specimen.pdf and legibility.pdf so the user's next look shows the interpolated condensed; swisscheck on specimen.pdf stays "bestanden".

- [ ] **Step 5: Commit (local; controller pushes)**

```bash
git add fonts && git commit -m "feat(fonts): interpolated 0.8-compression condensed per legibility-gate ruling"
```

## Self-review record

- **Spec coverage (§3):** rename/link → T2; vertical metrics → T3; italicAngle → T4; coverage → T5; kern/liga/tnum-omission → T6; QA gate (fontbakery, specimen, swisscheck A2) → T7–T9; legibility gate for §8 constants → T8; license firewall + AFPL handling → T1/T5/T7 README; Bold-Italic deviation documented → T7 README. Condensed-interpolation fallback is *conditional* on the T8 user gate — if the user rules "interpolate", that becomes a follow-up task appended to this plan before Plan 2 starts.
- **Placeholder scan:** the one intentionally open value is the Step-2 audit list in T5 (unknowable until run — the step records it in the commit message and extends recipes by the shown pattern). No TBDs otherwise.
- **Type consistency:** `build.run(steps, out_dir)`, `STYLE_MAP` tuple `(family, subfamily, out_name)`, dist names `SwissTeXGrotesk[Cond]-<Style>.ttf`, and `measurelib.analyze` keys are used identically across T1–T9.
