# SwissTeX v2.0 Class + Identity Layer Implementation Plan (Plan 2 of 3)

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Rebuild `swisstex.cls` as v2.0 — grid-purified per the derivation doctrine, extended with the identity layer (string table, font provider, `identity=`, head/foot content, logo primitive, slot-based covers) — plus the `acme` reference identity and swisscheck's sidecar + checks A10–A13/A15/A16.

**Architecture:** The class gains hooks with v1.3 behavior as defaults; all company specifics live in `swissidentity-<name>.sty` consuming public setters only. Verification is machine-first: a pytest harness builds fixture documents with XeLaTeX, reads the new Kennzahlen sidecar, and runs swisscheck; the manual and demo remain the largest fixtures.

**Tech Stack:** LaTeX2e/XeLaTeX (kvoptions, fontspec, titlesec…), Python 3 + pytest + pdfplumber (harness + swisscheck).

## Global Constraints

- Spec: `docs/superpowers/specs/2026-07-27-swisstex-generalization-design.md` §4–§9, §11–13, including all dated decision notes. The six invariants I1–I6 bind every change.
- **Frozen doctrine constants (user gate, 2026-07-28):** `\annotationleading = ⅔\gridunit` (9pt), `\glossleading = ¾\gridunit` (10.125pt), `\footnoteleading = ¾\gridunit` (10.125pt), `headsep = 2\gridunit`, `footskip = 3\gridunit`. All three leadings are overridable class options; defaults derive when the option is empty.
- **Plan-1 handoffs:** identities load fonts **by installed family name** (dist is TTF with capitalized suffixes — the v1.3 `Extension=.otf` file scheme stays only inside the *default* Heros provider); **glosses/marginalia/legends set in the regular-width family at annotation grade** (`\marg`, `\sidenote`, `swisstable`/`swissfigure` legends); condensed remains for table bodies, footnotes, head/foot apparatus, `\swisscode`; mind the condensed 0.710/0.806 width split (README "Known family inconsistency").
- **M-B review fixes (spec, binding):** no logo in the running head — ever (A11 enforces absence); class default `band = accent` (one red); cover glyph identity-bearing (no default `a`); cover variants identity-definable; swisscheck verifies declared relations via the sidecar, never hard-coded constants.
- Pagina at body grade in accent; classification printed only when ≥ internal.
- v2.0.0: `\ProvidesClass{swisstex}[2026/07/29 v2.0.0 Swiss typographic grid]`; manual cover/colophon version strings updated in the same task that bumps the class.
- Deprecation: the old 4-argument `\swisscover{K}{T}{U}{F}` keeps working for one minor version with a `\ClassWarning`.
- Documents without `identity=` build with defaults; visible v2.0 changes are exactly the spec §11 list, verified by swisscheck green on rebuilt manual + demo.
- German conventions: class comments ASCII-umlaut German; manual real umlauts; neutral placeholder `acme` everywhere; the user's company name never appears.
- Python env for tests: reuse `fonts/.venv` (`fonts/.venv/bin/pip install pdfplumber` once, Task 1); harness lives in `tests/` at repo root; XeLaTeX builds run from repo root with `-output-directory` into tmp dirs.
- Implementers commit locally with clear messages; **the controller pushes**. Never modify `fonts/dist`, `fonts/sources`, the spec, or the plan files.
- Masters' review protocol (spec §2.3): the closing task runs a Müller-Brockmann pass on the shipped v2.0 output.

## File Structure

```
swisstex.cls                     # v2.0 (all class tasks edit this)
swissidentity-acme.sty           # reference identity (Task 8)
acme-demo.tex / acme-logo.pdf    # identity exercise document + placeholder wordmark (Task 8)
swisscheck.py                    # sidecar reader + A10-A13, A15, A16 (Task 9)
swisstex-manual.tex              # updated per task (option table, prose)
tests/
  conftest.py                    # build_doc() helper: xelatex + sidecar parse + swisscheck run
  fixtures/*.tex                 # minimal per-feature documents
  test_doctrine.py  test_strings.py  test_fonts.py  test_identity.py
  test_foot.py  test_cover.py  test_acme.py  test_swisscheck.py
```

---

### Task 1: Test harness + derivation doctrine + head/foot geometry (v2.0.0)

**Files:**
- Create: `tests/conftest.py`, `tests/fixtures/plain.tex`, `tests/test_doctrine.py`
- Modify: `swisstex.cls` (§1 options, §2 lengths, geometry, §5c–§12 leading applications, §7 head)
- Modify: `swisstex-manual.tex` (version strings, option table + prose), `.gitignore` (add `tests/__pycache__/`)

**Interfaces:**
- Produces: `conftest.build_doc(tex_path, tmp_path) -> BuildResult` with fields `pdf` (Path), `log` (str), `sidecar` (dict, empty until Task 9), `returncode`; `conftest.swisscheck(pdf, *args) -> (exit, output)` using `fonts/.venv/bin/python swisscheck.py`.
- Produces class options `annotationleading`, `glossleading`, `footnoteleading` (empty default → derive ⅔/¾/¾) and public lengths `\annotationleading`, `\glossleading`, `\footnoteleading`.

- [ ] **Step 1: Write the harness and the failing test**

```python
# tests/conftest.py
import subprocess, re
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
PY = ROOT / "fonts/.venv/bin/python"

class BuildResult:
    def __init__(self, pdf, log, returncode, sidecar):
        self.pdf, self.log, self.returncode, self.sidecar = pdf, log, returncode, sidecar

def build_doc(tex_path, tmp_path, runs=1):
    tex = Path(tex_path)
    r = None
    for _ in range(runs):
        r = subprocess.run(
            ["xelatex", "-interaction=nonstopmode", f"-output-directory={tmp_path}", str(tex)],
            cwd=ROOT, capture_output=True, text=True, timeout=300)
    log = (tmp_path / f"{tex.stem}.log").read_text(errors="replace")
    side = tmp_path / f"{tex.stem}.swisscheck"
    sidecar = {}
    if side.exists():
        for line in side.read_text().splitlines():
            if "=" in line:
                k, v = line.split("=", 1)
                sidecar[k.strip()] = v.strip()
    return BuildResult(tmp_path / f"{tex.stem}.pdf", log, r.returncode, sidecar)

def swisscheck(pdf, *args):
    r = subprocess.run([str(PY), str(ROOT / "swisscheck.py"), str(pdf), *args],
                       cwd=ROOT, capture_output=True, text=True, timeout=120)
    return r.returncode, r.stdout + r.stderr
```

```latex
% tests/fixtures/plain.tex — smallest grid-exercising document
\documentclass{swisstex}
\setrunningtitle{Fixture}
\begin{document}
\section{Abschnitt}
Grundtext auf dem Raster. Ein Absatz mit genug Woertern fuer zwei Zeilen
Flattersatz und Trennung im Basisraster der Klasse.
\marg{Randglosse}
Noch ein Absatz.\footnote{Fussnote im neuen Mass.}
\end{document}
```

```python
# tests/test_doctrine.py
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
```

- [ ] **Step 2: Run to verify failure**

Run: `fonts/.venv/bin/pip -q install pdfplumber && fonts/.venv/bin/pytest tests/test_doctrine.py -x -v`
Expected: FAIL (`v2.0.0` absent; no `swiss:` typeouts)

- [ ] **Step 3: Implement in `swisstex.cls`**

§1 options (after the existing `\DeclareStringOption` block):

```latex
\DeclareStringOption[]{annotationleading} % leer = 2/3 Rastermass
\DeclareStringOption[]{glossleading}      % leer = 3/4 Rastermass
\DeclareStringOption[]{footnoteleading}   % leer = 3/4 Rastermass
```

§2 derived lengths (after `\gridunit` is set; Kennzahlen doctrine — vertical rhythm
always grid-derived, defaults are the frozen commensurable ratios):

```latex
% Nebenmasse: Durchschuss der Nebentexte als starke Rasterbrueche (3:2, 4:3).
% Ueberschreibbare Kennzahlen; leere Option leitet aus dem Raster ab.
\newlength{\annotationleading}
\ifx\swiss@annotationleading\@empty
  \setlength{\annotationleading}{\dimexpr2\gridunit/3\relax}
\else\setlength{\annotationleading}{\swiss@annotationleading}\fi
\newlength{\glossleading}
\ifx\swiss@glossleading\@empty
  \setlength{\glossleading}{\dimexpr3\gridunit/4\relax}
\else\setlength{\glossleading}{\swiss@glossleading}\fi
\newlength{\footnoteleading}
\ifx\swiss@footnoteleading\@empty
  \setlength{\footnoteleading}{\dimexpr3\gridunit/4\relax}
\else\setlength{\footnoteleading}{\swiss@footnoteleading}\fi
\typeout{swiss:annotationleading=\the\annotationleading}
\typeout{swiss:glossleading=\the\glossleading}
\typeout{swiss:footnoteleading=\the\footnoteleading}
```

Geometry: replace `headsep = 10mm` / `footskip = 14mm` with

```latex
  headsep     = \dimexpr2\gridunit\relax,
  footskip    = \dimexpr3\gridunit\relax}
\typeout{swiss:headsep=\the\dimexpr2\gridunit\relax}
\typeout{swiss:footskip=\the\dimexpr3\gridunit\relax}
```

Version: `\ProvidesClass{swisstex}[2026/07/29 v2.0.0 Swiss typographic grid]`.

Leading applications (every literal dies; grades stay):
- head (§7): running title `\condensed\fontsize{7.5}{\annotationleading}`; **pagina at body grade**: `\makebox[...][l]{{\fontsize{\swiss@bodysize}{\annotationleading}\selectfont\textcolor{accent}{\thepage}}}` (the box keeps the margin-zone width).
- `\tracked` (§10): `{7.5}{\annotationleading}`.
- **Regular-width glosses (Plan-1 handoff):** `\marg` and `\sidenote` drop `\condensed`: `\raggedright\normalfont\fontsize{7.5}{\glossleading}\selectfont\color{quiet}`; same switch in the `swisstable`/`swissfigure` legend minipages.
- colophon (§10): `{7}{\glossleading}` (stays condensed — apparatus).
- footnotes (§9a): `\renewcommand{\footnotesize}{\condensed\fontsize{8}{\footnoteleading}\selectfont}`.
- table body (§11): `\condensed\fontsize{8}{\footnoteleading}`.
- footnoterule kerns: `\kern-.25\footnoteleading` / `\kern.2\footnoteleading` (replaces −3pt/2.6pt hand values, same optical intent, grid-derived).

Manual: bump both version strings to 2.0.0; option table gains the three leading options; add a short prose note in §2 (Kennzahlen) naming the commensurable ratios and the regular-width-gloss change; colophon line "9,5/13,5" stays (body unchanged).

- [ ] **Step 4: Run tests + rebuild the two big documents**

Run: `fonts/.venv/bin/pytest tests/test_doctrine.py -v` → PASS.
Then: `for d in swisstex-demo swisstex-manual; do timeout 300 xelatex -interaction=nonstopmode -output-directory=/tmp/swtx $d.tex; done` (manual twice) and `fonts/.venv/bin/python swisscheck.py /tmp/swtx/swisstex-manual.pdf --tex swisstex-manual.tex` → bestanden. Copy rebuilt PDFs over the repo copies.
Expected: green; visible diffs are exactly the §11 list.

- [ ] **Step 5: Commit**

`git add swisstex.cls swisstex-manual.tex swisstex-manual.pdf swisstex-demo.pdf tests .gitignore && git commit -m "feat(class)!: v2.0 derivation doctrine — grid-derived leadings, head/foot on extended raster, body-grade pagina, regular-width glosses"`

### Task 2: String table (DE + EN)

**Files:**
- Modify: `swisstex.cls` (new §2a strings), `swisstex-manual.tex` (interface table row + i18n prose)
- Create: `tests/fixtures/lang-en.tex`, `tests/test_strings.py`

**Interfaces:**
- Produces: `\swiss@str{<key>}` (internal), `\swisssetstrings{<lang>}{<key>=<value>,…}` (public), keys: `table`, `figure`, `page`, `classification-public`, `classification-internal`, `classification-confidential`, `classification-strict`. `\tablecaptionprefix`/`\figurecaptionprefix` become aliases reading the table (backward compatible).

- [ ] **Step 1: Failing test**

```python
# tests/test_strings.py
from conftest import build_doc, ROOT
import pdfplumber

def _text(pdf):
    with pdfplumber.open(pdf) as p:
        return "\n".join(pg.extract_text() or "" for pg in p.pages)

def test_english_captions(tmp_path):
    r = build_doc(ROOT / "tests/fixtures/lang-en.tex", tmp_path)
    assert r.returncode == 0, r.log[-2000:]
    t = _text(r.pdf)
    assert "Table 1" in t and "Tabelle" not in t

def test_custom_language_addable(tmp_path):
    fx = tmp_path / "fr.tex"
    fx.write_text(r"""\documentclass[lang=french]{swisstex}
\swisssetstrings{french}{table=Tableau, figure=Illustration, page=Page,
  classification-public=public, classification-internal=interne,
  classification-confidential=confidentiel, classification-strict=strict}
\begin{document}
\begin{swisstable}{Legende}\begin{tabularx}{\textcolumn}[t]{@{}L@{}}x\\\end{tabularx}\end{swisstable}
\end{document}""")
    r = build_doc(fx, tmp_path)
    assert "Tableau 1" in _text(r.pdf)

def test_unknown_language_falls_back(tmp_path):
    fx = tmp_path / "xx.tex"
    fx.write_text(r"""\documentclass[lang=latin]{swisstex}
\begin{document}
\begin{swisstable}{L}\begin{tabularx}{\textcolumn}[t]{@{}L@{}}x\\\end{tabularx}\end{swisstable}
\end{document}""")
    r = build_doc(fx, tmp_path)
    assert "Table 1" in _text(r.pdf)          # EN fallback
    assert "swisstex Warning" in r.log or "fallback" in r.log.lower()
```

`tests/fixtures/lang-en.tex` = plain.tex with `\documentclass[lang=english]{swisstex}` plus one `swisstable`.

- [ ] **Step 2: Run** → FAIL (`\swisssetstrings` undefined / "Tabelle 1" in EN doc)

- [ ] **Step 3: Implement (class §2a, before §8 uses)**

```latex
% --- 2a  Sprachtabelle -------------------------------------------------
% Alle sichtbaren Zeichenketten laufen ueber \swiss@str{key}. Sprachen
% definieren sich ueber \swisssetstrings; unbekannte Sprache faellt mit
% Warnung auf english zurueck.
\RequirePackage{expl3}% nur fuer prop-Listen? — nein: einfach csname-Schema
\newcommand{\swisssetstrings}[2]{%
  \begingroup
  \@for\swiss@pair:=#2\do{%
    \expandafter\swiss@defstr\expandafter{\swiss@pair}{#1}}%
  \endgroup}
\def\swiss@defstr#1#2{\swiss@defstr@i#1\@nil{#2}}
\def\swiss@defstr@i#1=#2\@nil#3{%
  \global\@namedef{swiss@str@#3@#1}{#2}}
\newcommand{\swiss@str}[1]{%
  \ifcsname swiss@str@\swiss@lang @#1\endcsname
    \csname swiss@str@\swiss@lang @#1\endcsname
  \else
    \ifcsname swiss@str@english@#1\endcsname
      \ClassWarning{swisstex}{no '#1' string for language '\swiss@lang', english fallback}%
      \csname swiss@str@english@#1\endcsname
    \else\ClassError{swisstex}{unknown string key '#1'}{}\fi
  \fi}
\swisssetstrings{german}{table=Tabelle, figure=Abbildung, page=Seite,
  classification-public=\"offentlich, classification-internal=Intern,
  classification-confidential=Vertraulich, classification-strict=Streng vertraulich}
\swisssetstrings{english}{table=Table, figure=Figure, page=Page,
  classification-public=Public, classification-internal=Internal,
  classification-confidential=Confidential, classification-strict=Strictly confidential}
\renewcommand{\tablecaptionprefix}{\swiss@str{table}}
\renewcommand{\figurecaptionprefix}{\swiss@str{figure}}
```

(Existing `\tablecaptionprefix` definitions in §11/§11a become the aliases above — remove the literal `Tabelle`/`Abbildung`. Note `\swiss@lang` is the kvoptions value of `lang`.)

- [ ] **Step 4: Run all tests** → PASS (incl. Task 1 suite)
- [ ] **Step 5: Commit** `feat(class): language string table, DE+EN, \swisssetstrings`

### Task 3: Font provider + `\swisscode`

**Files:**
- Modify: `swisstex.cls` (§3), `swisstex-manual.tex` (`\code` → `\swisscode`, interface row)
- Create: `tests/fixtures/provider.tex`, `tests/test_fonts.py`

**Interfaces:**
- Produces: default provider macro `\swiss@defaultfonts` (v1.3 Heros block verbatim); if `\swissidentityfonts` is defined at the provider point it runs instead. `\swisscode{...}` = condensed 8.5pt on `\gridunit` leading (no Latin Modern).

- [ ] **Step 1: Failing test**

```python
# tests/test_fonts.py
from conftest import build_doc, ROOT
import pdfplumber

def _fonts(pdf):
    with pdfplumber.open(pdf) as p:
        return {c["fontname"].split("+")[-1] for pg in p.pages for c in pg.chars}

def test_provider_override(tmp_path):
    r = build_doc(ROOT / "tests/fixtures/provider.tex", tmp_path)
    assert r.returncode == 0, r.log[-2000:]
    f = _fonts(r.pdf)
    assert any("SwissTeXGrotesk" in x for x in f), f
    assert not any("TeXGyreHeros" in x for x in f), f

def test_swisscode_no_latin_modern(tmp_path):
    fx = tmp_path / "code.tex"
    fx.write_text(r"""\documentclass{swisstex}
\begin{document}Vorher \swisscode{gridunit=13.5pt} nachher.\end{document}""")
    r = build_doc(fx, tmp_path)
    assert not any("LMMono" in x or "LMRoman" in x for x in _fonts(r.pdf))
```

`tests/fixtures/provider.tex`:

```latex
\documentclass{swisstex}
\newcommand{\swissidentityfonts}{%
  \setmainfont{SwissTeX Grotesk}%
  \renewfontfamily\condensed{SwissTeX Grotesk Condensed}}
\begin{document}Probe {\condensed schmal} \textbf{fett}.\end{document}
```

- [ ] **Step 2: Run** → FAIL (provider ignored — Heros everywhere; `\swisscode` undefined)

- [ ] **Step 3: Implement**

§3: wrap the existing `\setmainfont`/`\newfontfamily\condensed` block:

```latex
\newcommand{\swiss@defaultfonts}{%
  \setmainfont{\swiss@sans}[... unverändert ...]%
  \newfontfamily\condensed{\swiss@sanscondensed}[... unverändert ...]}
% Der Identitaetsanbieter ersetzt die Vorgabe im Ganzen (I4: keine Mischung).
\ifcsname swissidentityfonts\endcsname\swissidentityfonts\else\swiss@defaultfonts\fi
```

(Load order note: documents define `\swissidentityfonts` before `\documentclass`? No — the check must run late enough; move the provider dispatch to the END of the preamble processing via `\AtBeginDocument`? fontspec allows `\setmainfont` in `\AtBeginDocument` only unreliably. Correct mechanism: dispatch at `\AtEndOfClass`+`\AtBeginDocument` is wrong; instead the class defers the font block until after `identity=` loads (Task 4) — for THIS task, dispatch in the class where the font block sits today, and the provider test defines the macro via a two-line wrapper class-option-free trick: `\RequirePackage{...}`? Simplest robust order that works for both tasks: the class executes the dispatch at the *end of the preamble* via `\AtBeginDocument{\ifdefined\swiss@fontsdone\else...\fi}` — fontspec explicitly supports `\setmainfont` in the preamble AND at begin-document before any text. Implement exactly that:)

```latex
\AtBeginDocument{%
  \ifcsname swissidentityfonts\endcsname\swissidentityfonts
  \else\swiss@defaultfonts\fi}
```

and delete the immediate execution. The math-range `\setmathfont` lines move inside `\swiss@defaultfonts` (identities own math setup when overriding; manual note).

`\swisscode` (§5c area): `\newcommand{\swisscode}[1]{{\condensed\fontsize{8.5}{\gridunit}\selectfont #1}}`. Manual: `\code` redefined as `\swisscode` alias; interface table row.

- [ ] **Step 4: Run all tests** (plain fixture must still use Heros default) → PASS
- [ ] **Step 5: Commit** `feat(class): font provider hook + \swisscode (no Latin Modern leak)`

### Task 4: `identity=` option, public setters, `\swissmeta`

**Files:**
- Modify: `swisstex.cls` (§1 option; new §2b identity interface)
- Create: `tests/fixtures/swissidentity-test.sty`, `tests/fixtures/identity.tex`, `tests/test_identity.py`

**Interfaces:**
- Produces (all global, public): `\swissidentitymeta{company=…, legal=…, web=…}`; `\swisssetcolors{accent=…, paper=…, ink=…[, band=…]}` (omitted band → band=accent); `\swisslogofiles{cover=…, colophon=…}`; `\swissclassifications{a,b,c,d}` (ordered, maps to string keys `classification-<name>`); `\swissfootformat{…}` with `\meta{<key>}` expanding inside it; `\swissmeta{docid=…, version=…, date=…, classification=…, client=…}` (document command; `date` defaults to `\today`; unknown classification → `\ClassError`). Accessors for later tasks: `\swiss@meta{<key>}` (empty if unset), `\swiss@classlevel` (integer index, 0-based; −1 if unset).
- Class default colors change: `band` default becomes the accent value (one red; M-B fix). `\definecolor{band}` runs after identity load.

- [ ] **Step 1: Failing test**

```python
# tests/test_identity.py
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
```

`tests/fixtures/swissidentity-test.sty`: minimal identity using every setter (accent `{10,20,30}`, no band, `\swissclassifications{public,internal}`, `\swissfootformat{\meta{docid}}`). `tests/fixtures/identity.tex`: `\documentclass[identity=test]{swisstex}` + `\swissmeta{docid=X-1, classification=internal}` + one paragraph. (The harness passes `TEXINPUTS=tests/fixtures//:` via `conftest.build_doc` env so the fixture identity resolves — add `env` support to `build_doc` in this task: `subprocess.run(..., env={**os.environ, "TEXINPUTS": f"{ROOT}/tests/fixtures//:"})`.)

- [ ] **Step 2: Run** → FAIL (`identity` unknown option)

- [ ] **Step 3: Implement (class §1 + new §2b)**

```latex
\DeclareStringOption[]{identity}
```

§2b (after colors §4 moves its band definition here; order: options → lengths → identity load → colors):

```latex
% --- 2b  Identitaetsschnittstelle -------------------------------------
\def\swiss@bandvalue{}% leer = accent (eine Farbe, M-B-Regel)
\define@key{swissid}{accent}{\def\swiss@accent{#1}}
\define@key{swissid}{band}{\def\swiss@bandvalue{#1}}
\define@key{swissid}{paper}{\def\swiss@paper{#1}}
\define@key{swissid}{ink}{\def\swiss@ink{#1}}
\newcommand{\swisssetcolors}[1]{\setkeys{swissid}{#1}}
\def\swiss@id@company{}\def\swiss@id@legal{}\def\swiss@id@web{}
\define@key{swissidm}{company}{\gdef\swiss@id@company{#1}}
\define@key{swissidm}{legal}{\gdef\swiss@id@legal{#1}}
\define@key{swissidm}{web}{\gdef\swiss@id@web{#1}}
\newcommand{\swissidentitymeta}[1]{\setkeys{swissidm}{#1}}
\def\swiss@logo@cover{}\def\swiss@logo@colophon{}
\define@key{swisslogo}{cover}{\gdef\swiss@logo@cover{#1}}
\define@key{swisslogo}{colophon}{\gdef\swiss@logo@colophon{#1}}
\newcommand{\swisslogofiles}[1]{\setkeys{swisslogo}{#1}}
\def\swiss@classifications{public,internal,confidential,strict}
\newcommand{\swissclassifications}[1]{\gdef\swiss@classifications{#1}}
\def\swiss@footformat{}
\newcommand{\swissfootformat}[1]{\gdef\swiss@footformat{#1}}
% Dokumentseitige Metadaten
\def\swiss@meta#1{\ifcsname swiss@meta@#1\endcsname\csname swiss@meta@#1\endcsname\fi}
\define@key{swissmeta}{docid}{\gdef\swiss@meta@docid{#1}}
\define@key{swissmeta}{version}{\gdef\swiss@meta@version{#1}}
\define@key{swissmeta}{date}{\gdef\swiss@meta@date{#1}}
\define@key{swissmeta}{client}{\gdef\swiss@meta@client{#1}}
\define@key{swissmeta}{classification}{\gdef\swiss@meta@classification{#1}}
\newcommand{\swissmeta}[1]{\setkeys{swissmeta}{#1}\swiss@checkclass}
\gdef\swiss@meta@date{\today}
\def\swiss@classlevel{-1}
\def\swiss@checkclass{%
  \ifcsname swiss@meta@classification\endcsname
    \def\swiss@classlevel{-1}\@tempcnta=0
    \@for\swiss@c:=\swiss@classifications\do{%
      \ifx\swiss@c\swiss@meta@classification
        \edef\swiss@classlevel{\the\@tempcnta}\fi
      \advance\@tempcnta by 1}%
    \ifnum\swiss@classlevel<0
      \ClassError{swisstex}{unknown classification
        '\swiss@meta@classification'}{declared: \swiss@classifications}\fi
  \fi}
% Identitaet laden: nach den Optionen, vor Schrift und Farbe.
\ifx\swiss@identity\@empty\else
  \IfFileExists{swissidentity-\swiss@identity.sty}
    {\RequirePackage{swissidentity-\swiss@identity}}
    {\ClassError{swisstex}{identity file
       'swissidentity-\swiss@identity.sty' not found}{}}\fi
```

§4 colors: `band` resolves after identity: `\ifx\swiss@bandvalue\@empty\colorlet{band}{accent}\typeout{swiss:band=accent}\else\definecolor{band}{RGB}{\swiss@bandvalue}\typeout{swiss:band=own}\fi` — and the old `band` class option's default dies (option kept, feeds `\swiss@bandvalue` for compatibility). `\meta` inside `\swissfootformat` = local alias for `\swiss@meta` when the foot is typeset (Task 5).

- [ ] **Step 4: Run all tests** → PASS
- [ ] **Step 5: Commit** `feat(class): identity= loading, public setters, \swissmeta with classification vocabulary`

### Task 5: Foot content (classification + metadata line)

**Files:**
- Modify: `swisstex.cls` (§7 fancyhdr foot)
- Create: `tests/fixtures/foot.tex`, `tests/test_foot.py`

**Interfaces:**
- Produces: foot rendered only when content exists: margin zone = `\swiss@str{classification-<name>}` in `\tracked` accent iff `\swiss@classlevel ≥ 1`; text axis = `\swiss@footformat` (with `\meta` bound) in quiet condensed at `{7.5}{\annotationleading}`; empty `\swissfootformat` + no classification → foot identical to v1.3 (empty).

- [ ] **Step 1: Failing test**

```python
# tests/test_foot.py
from conftest import build_doc, ROOT
import pdfplumber

def test_foot_line(tmp_path):
    r = build_doc(ROOT / "tests/fixtures/foot.tex", tmp_path)
    with pdfplumber.open(r.pdf) as p:
        page = p.pages[0]
        foot = [w["text"] for w in page.extract_words() if w["top"] > page.height - 60]
    assert any("D-77" in w for w in foot), foot
    assert any("Intern" in w for w in foot), foot

def test_public_prints_nothing(tmp_path):
    fx = tmp_path / "pub.tex"
    fx.write_text((ROOT / "tests/fixtures/foot.tex").read_text()
                  .replace("classification=internal", "classification=public"))
    r = build_doc(fx, tmp_path)
    with pdfplumber.open(r.pdf) as p:
        page = p.pages[0]
        foot = " ".join(w["text"] for w in page.extract_words() if w["top"] > page.height - 60)
    assert "ffentlich" not in foot and "Public" not in foot
```

`tests/fixtures/foot.tex`: identity-free doc with `\swissfootformat{\meta{docid} · \meta{version} · \meta{date}}` in the preamble (public setter callable class-side too) + `\swissmeta{docid=D-77, version=1.0, date=2026-07-29, classification=internal}`.

- [ ] **Step 2: Run** → FAIL (no foot content)

- [ ] **Step 3: Implement (§7, extend `\pagestyle{fancy}` block)**

```latex
\fancyfoot[L]{%
  \hspace*{\measureshift}%
  \makebox[0pt][l]{%
    \condensed\fontsize{7.5}{\annotationleading}\selectfont
    \makebox[\dimexpr\margincolumn+\gutter\relax][l]{%
      \ifnum\swiss@classlevel>0
        \textcolor{accent}{\tracked{\swiss@str{classification-\swiss@meta@classification}}}%
      \fi}%
    \color{quiet}%
    \ifx\swiss@footformat\@empty\else
      {\let\meta\swiss@meta\swiss@footformat}\fi}}
```

(`swisstitle` pagestyle keeps head *and* foot empty — covers carry no foot.)

- [ ] **Step 4: Run all tests** → PASS; rebuild manual/demo, swisscheck bestanden (their feet stay empty — no \swissmeta)
- [ ] **Step 5: Commit** `feat(class): foot metadata line + classification mark (silent when public)`

### Task 6: `\swisslogo` primitive + slot-based `\swisstitle`

**Files:**
- Modify: `swisstex.cls` (§10; new logo primitive §9b)
- Create: `tests/fixtures/title.tex`, `tests/test_title.py` (grouped into test_cover.py in Task 7 — create here as test_title.py)

**Interfaces:**
- Produces: `\swisslogo[lines=<n>, axis=text|full]{<file>}` — `\includegraphics[height=<n>\gridunit]` in a `\swiss@placebox` block, left edge on the chosen axis; missing file → `\ClassError`. Slot-form `\swisstitle{kicker=…, title=…, subtitle=…}` (key-value; the old 3-argument form still works via `\@ifnextchar` bracket sniff on `{`… simplest: keep 3-arg `\swisstitle` AND add `\swisstitle*{key=val}` starred slot form — deprecation note in manual; spec's slot goal met by the starred form, positional form deprecated in v2.1).
- Title block regrounded: kicker `\tracked` at annotation leading; title `\swissdisplay{2}`; subtitle `{10.5}{\gridunit}` quiet; spacing in whole `\gridunit`s; rule = stroke Kennzahl (unchanged 1.2pt).

- [ ] **Step 1: Failing test** — build `tests/fixtures/title.tex` using `\swisstitle*{kicker=Bericht, title=Titelprobe, subtitle=Untertitel}` and `\swisslogo[lines=2, axis=text]{acme-logo.pdf}` with a fixture one-rect PDF logo generated in-test via pdfplumber?? No — generate a tiny logo PDF in the fixture dir with a 5-line standalone TikZ-free document: create `tests/fixtures/mklogo.tex` (`\documentclass{article}\usepackage[paperwidth=40mm,paperheight=10mm,margin=0pt]{geometry}\pagestyle{empty}\begin{document}\rule{40mm}{10mm}\end{document}`), built once by conftest fixture `logo_pdf(tmp_path)`. Tests: build succeeds; title text present; swisscheck A2 passes; missing-logo doc errors.

```python
# tests/test_title.py (essentials)
def test_star_title_and_logo(tmp_path, logo_pdf):
    ...  # build fixture with logo path injected; assert returncode 0, "Titelprobe" in text
def test_missing_logo_errors(tmp_path):
    ...  # \swisslogo{nosuch.pdf} -> returncode != 0, "logo" in log
def test_title_grid(tmp_path, logo_pdf):
    ...  # swisscheck(pdf) exit 0
```

- [ ] **Step 2: Run** → FAIL
- [ ] **Step 3: Implement**

```latex
% --- 9b  Logo als Satzblock -------------------------------------------
\define@key{swisslg}{lines}{\def\swiss@lg@lines{#1}}
\define@key{swisslg}{axis}{\def\swiss@lg@axis{#1}}
\newcommand{\swisslogo}[2][]{%
  \def\swiss@lg@lines{2}\def\swiss@lg@axis{text}%
  \setkeys{swisslg}{#1}%
  \IfFileExists{#2}{}{\ClassError{swisstex}{logo file '#2' not found}{}}%
  \par\sbox{\swiss@gbox}{\includegraphics[height=\dimexpr\swiss@lg@lines\gridunit\relax]{#2}}%
  \def\swiss@lg@shift{\z@}%
  \expandafter\ifx\csname swiss@lg@axis\endcsname\swiss@lg@full
    \def\swiss@lg@shift{-\measureshift}\fi
  \ifthenelse{\equal{\swiss@lg@axis}{full}}%
    {\swiss@placebox{\swiss@gbox}{-\measureshift}}%
    {\swiss@placebox{\swiss@gbox}{\z@}}}
```

(uses `ifthen`, `\RequirePackage{ifthen}`; drop the `\expandafter` fragment — the `\ifthenelse` line is the implementation). Starred `\swisstitle*`:

```latex
\define@key{swisstt}{kicker}{\def\swiss@tt@k{#1}}
\define@key{swisstt}{title}{\def\swiss@tt@t{#1}}
\define@key{swisstt}{subtitle}{\def\swiss@tt@s{#1}}
\newcommand{\swisstitleslots}[1]{%
  \def\swiss@tt@k{}\def\swiss@tt@t{}\def\swiss@tt@s{}%
  \setkeys{swisstt}{#1}%
  \thispagestyle{swisstitle}%
  \par\sbox{\swiss@gbox}{%
    \begin{minipage}{\fullmeasure}%
      \ifx\swiss@tt@k\@empty\else{\fontsize{7.5}{\annotationleading}\selectfont
        \tracked{\swiss@tt@k}}\par\vspace{\dimexpr\gridunit/2\relax}\fi
      \ifx\swiss@tt@t\@empty\else{\swissdisplay{2}\swiss@tt@t\par}\fi
      \ifx\swiss@tt@s\@empty\else\vspace{\dimexpr\gridunit/2\relax}%
        {\fontsize{10.5}{\gridunit}\selectfont\color{quiet}\swiss@tt@s\par}\fi
      \vspace{\gridunit}{\color{black}\hrule height 1.2pt}%
    \end{minipage}}%
  \swiss@placebox{\swiss@gbox}{-\measureshift}}
\WithSuffix\newcommand\swisstitle*[1]{\swisstitleslots{#1}}% \RequirePackage{suffix}
```

Old 3-arg `\swisstitle` body: replace its hand `\vspace{6pt}/{9pt}` + `fontsize{21}{23}` with the same grid measures (`\gridunit/2` gaps, `\swissdisplay{2}`) so both forms render identically.

- [ ] **Step 4: Run all** → PASS; rebuild manual/demo (both use 3-arg form — visual: title now on display grade), swisscheck bestanden
- [ ] **Step 5: Commit** `feat(class): \swisslogo primitive + slot-based title, title block on display grades`

### Task 7: Cover slots, variants, cover on the page grid

**Files:**
- Modify: `swisstex.cls` (§10a)
- Create: `tests/fixtures/cover.tex`, `tests/test_cover.py`

**Interfaces:**
- Produces: `\swisscover*{kicker=…, title=…, subtitle=…, foot=…, client=…, docid=…, glyph=…, band=<startline>/<lines>, logo=…}` — all optional; `docid`/`date`/`classification` auto-fill from `\swissmeta`; band default `38/9` (grid lines, replaces `0.13\paperheight`); glyph rendered ONLY when given (no default `a`), anchored: baseline on grid line `\swiss@cg@line` (key `glyphline`, default 30), left edge on the text axis; glyph size in grid lines (key `glyphlines`, default 34). Variants: `\swisscovervariant{<name>}{<slot defaults>}` (identity-side), `variant=<name>` key merges defaults then explicit keys. Old positional `\swisscover{K}{T}{U}{F}` → `\ClassWarning` deprecation + delegates to slots.
- Cover classification: when ≥ internal, tracked accent mark right-aligned in the kicker line.

- [ ] **Step 1: Failing test**

```python
# tests/test_cover.py (essentials)
def test_slot_cover_builds_and_band_on_grid(tmp_path):
    # fixture: \swisscover*{kicker=Angebot, title=Probe, band=38/9} + \swissmeta internal
    # assert: build ok; band rect top/bottom within 0.5pt of topmargin + 38*gu and +47*gu (pdfplumber rects)
def test_no_glyph_by_default(tmp_path):
    # cover without glyph= -> no character larger than 100pt anywhere on page 1
def test_positional_form_warns(tmp_path):
    # \swisscover{A}{B}{C}{D} -> builds, log contains "deprecated"
def test_autofill_from_meta(tmp_path):
    # \swissmeta{docid=Q-9,...}; cover without docid= -> "Q-9" appears on page 1
```

(compute expected band geometry from the class defaults: top = 26mm + 38·13.5pt from page top; use pdfplumber `page.rects` filtered to full-page-width rects.)

- [ ] **Step 2: Run** → FAIL
- [ ] **Step 3: Implement** — rewrite `\swisscover` internals: shipout background keeps the `tint` logic; the band becomes

```latex
\AtPageUpperLeft{\put(0,\LenToUnit{\dimexpr-\swiss@topmargin-\swiss@cb@start\gridunit\relax}){%
  \color{band}\rule[-\dimexpr\swiss@cb@lines\gridunit\relax]{\paperwidth}{\dimexpr\swiss@cb@lines\gridunit\relax}}}
```

with `\swiss@cb@start`/`\swiss@cb@lines` parsed from `band=<start>/<lines>` (default `38/9`). Glyph block only inside `\ifx\swiss@cg@glyph\@empty\else … \fi`, positioned `\put(\LenToUnit{\innermargin}, \LenToUnit{\dimexpr-\swiss@topmargin-\swiss@cg@line\gridunit\relax})` — text-axis anchor, grid-line baseline (page-fraction keys `\swisscoverglyphx/y` deleted; kept as no-op deprecated macros with warnings). Slot content mirrors Task 6's pattern; kicker line = `\makebox[\fullmeasure]{\tracked{kicker}\hfill\ifnum\swiss@classlevel>0\textcolor{accent}{\tracked{\swiss@str{classification-…}}}\fi}`. Variants:

```latex
\newcommand{\swisscovervariant}[2]{\@namedef{swiss@cvar@#1}{#2}}
\define@key{swisscv}{variant}{%
  \ifcsname swiss@cvar@#1\endcsname
    \expandafter\setkeys\expandafter{\expandafter swisscv\expandafter}%
      \expandafter{\csname swiss@cvar@#1\endcsname}%
  \else\ClassError{swisstex}{unknown cover variant '#1'}{}\fi}
```

(variant key processed FIRST: `\swisscoverslots` pre-scans for `variant=` before the general `\setkeys` — implement by running `\setkeys{swisscv}` twice, variants only define defaults so the second explicit pass wins.) Positional form:

```latex
\renewcommand{\swisscover}[4]{\ClassWarning{swisstex}{positional \string\swisscover\space
  is deprecated; use \string\swisscover*{key=value}}\swisscoverslots{kicker=#1,title=#2,subtitle=#3,foot=#4}}
\WithSuffix\newcommand\swisscover*[1]{\swisscoverslots{#1}}
```

- [ ] **Step 4: Run all**; rebuild manual (its cover uses the positional form → warning expected in log, output on the new grid geometry), swisscheck bestanden → PASS
- [ ] **Step 5: Commit** `feat(class)!: slot-based covers on the page grid, identity-definable variants, glyph identity-bearing`

### Task 8: `acme` reference identity + demo document

**Files:**
- Create: `swissidentity-acme.sty` (repo root), `acme-demo.tex`, `acme-logo.pdf` (built from a committed `acme-logo.tex` one-rule wordmark, 8 lines), `tests/test_acme.py`

**Interfaces:**
- `swissidentity-acme.sty` = the spec §5 sketch made real: meta, colors (accent `{200,16,46}`, no band), fonts by family name (`SwissTeX Grotesk` + `\renewfontfamily\condensed{SwissTeX Grotesk Condensed}` — Plan-1 handoff), logo files, classifications, footformat, one cover variant `report` (`band=38/9, glyphline=30`).
- `acme-demo.tex`: `identity=acme`, `\swissmeta{docid=TR-2026-014, version=1.2, classification=internal}`, slot cover with `variant=report`, one section with table/figure/gloss/footnote, colophon with `\swisslogo`.

- [ ] **Step 1: Failing test** — `tests/test_acme.py`: builds; fonts = SwissTeXGrotesk* only (+ math if any); "TR-2026-014" in foot; "Intern" classification present on content pages; swisscheck exit 0.
- [ ] **Step 2: Run** → FAIL (files missing)
- [ ] **Step 3: Write the three files** exactly per the interfaces (identity file content per spec §5 sketch with the family-name font provider; wordmark = black rule + "ACME" in the class's own grotesque, built with xelatex into acme-logo.pdf, committed).
- [ ] **Step 4: Run all** → PASS
- [ ] **Step 5: Commit** `feat(identity): acme reference identity + demo document`

### Task 9: Kennzahlen sidecar + swisscheck A10–A13, A15, A16

**Files:**
- Modify: `swisstex.cls` (§14: sidecar writer), `swisscheck.py` (sidecar reader + 6 checks), `tests/conftest.py` (sidecar already parsed), `tests/test_swisscheck.py`

**Interfaces:**
- Sidecar `<jobname>.swisscheck`, written `\AtEndDocument` via `\newwrite`: `gridunit=13.5pt`, `bodysize=9.5pt`, `annotationleading=…`, `glossleading=…`, `footnoteleading=…`, `headsep=…`, `footskip=…`, `outermargin/margincolumn/gutter/numberzone/textcolumn/topmargin/gridlines`, `accent=R,G,B`, `band=accent|R,G,B`, `paper=…`, `ink=…`, `mainfamily=<fontspec family>`, `condensedfamily=…`, `classification=<name|none>`, `docid=…`.
- swisscheck: `--params <file>` plus auto-discovery of `<pdf-stem>.swisscheck` beside the PDF; sidecar values override CLI defaults (mm/pt parsing). New Befunde:
  - **A10 Fusszeile:** foot text baseline ≡ topmargin + gridlines·gu + footskip (±0.5pt); classification words confined to `[outermargin, outermargin+margincolumn]`; metadata words start ≥ innermargin.
  - **A11 Kolumnentitel:** pagina char size == bodysize (±0.35pt); **no `page.images` intersecting the head band** (top < topmargin).
  - **A12 Umschlag:** on pages with a full-page-width rect (cover): rect top/bottom ≡ topmargin + k·gu (±0.5pt); all text sizes ∈ {0.8·n·gu ±0.5 | n=1..6} ∪ {≤ bodysize+0.35}.
  - **A13 Kommensurabilitaet:** distinct baseline-gap clusters of small text (size < bodysize−0.5) each ≈ one of {annotation, gloss, footnote} leadings from the sidecar (±0.35pt).
  - **A15 Farbrollen:** if sidecar `band` ≠ `accent`: Euclidean RGB distance ≥ 30 required.
  - **A16 Schriftinventar:** embedded font basenames (strip subset prefix) ⊆ {mainfamily*, condensedfamily*, mathfont-whitelist} — using fontname matching by collapsing spaces/case.
- Every check degrades gracefully (skips with note) when the sidecar or the relevant page content is absent — old PDFs remain checkable.

- [ ] **Step 1: Failing tests** — `tests/test_swisscheck.py`: (a) plain fixture writes sidecar with the frozen values; (b) `swisscheck` on the acme demo passes A10–A16 (exit 0, output lists `A10…A16` with `ok`); (c) a deliberately broken fixture (`\fancyhead` image via `\swisslogo` hack in a group — simplest: `\fancyhead[R]{\includegraphics[height=5pt]{acme-logo.pdf}}` in the preamble) FAILS A11.
- [ ] **Step 2: Run** → FAIL
- [ ] **Step 3: Implement** — class §14 writer (`\immediate\openout` at end-document, one `\immediate\write` per key); swisscheck: `--params` + autodiscovery in `main()`, `Raster.from_sidecar(dict)` classmethod (pt/mm parsing helper), six `pruefe_*` functions in the style of the existing A-checks (each ~20-30 lines, same Befund dataclass), registered in `main()`'s befunde list.
- [ ] **Step 4: Run ALL tests + swisscheck on manual/demo/acme-demo (rebuilt); commit rebuilt PDFs.** → PASS, bestanden everywhere
- [ ] **Step 5: Commit** `feat(check): Kennzahlen sidecar + A10-A13/A15/A16 — relations, not constants`

### Task 10: Documentation pass + Müller-Brockmann closing review

**Files:**
- Modify: `swisstex-manual.tex` (new sections: Identitaet, Slots/Varianten, Fusszeile, Sprachtabelle, Sidecar/Pruefungen; option table final sync), `CLAUDE.md` (v2.0 architecture notes, identity layer, new checks), `README`-level notes where stale.

- [ ] **Step 1:** Manual gains one section per feature (German, set with the class itself — it remains the largest fixture); option table mirrors §1 exactly (script the comparison: `rg '\\Declare(String|Bool)Option' swisstex.cls` vs table rows — record the diff in the report; zero rows missing).
- [ ] **Step 2:** Full rebuild chain: manual (×2), demo, acme-demo, all tests, swisscheck everywhere → all green; commit rebuilt PDFs.
- [ ] **Step 3:** CONTROLLER: dispatch the Müller-Brockmann closing devil's-advocate pass (spec §2.3) on the shipped v2.0 output (manual + acme-demo PDFs, the class diff, this plan's ledger); record the verdict in the manual's colophon area or CLAUDE.md as appropriate; apply ADOPT-WITH-NAMED-FIX items if any in the final fix wave.
- [ ] **Step 4:** Commit `docs: v2.0 manual + guidance pass`

---

## Self-review record

- **Spec coverage:** §4.1 identity= → T4; §4.2 strings → T2; §4.3 provider → T3; §4.4 zones → T1/T5; §4.5 logo → T6; §4.6/§7 slots+variants+grid cover → T6/T7; §5 contract + acme → T4/T8; §6 head/foot/M-B fixes → T1/T5 (no-head-logo enforced by A11 in T9); §8 doctrine with frozen constants → T1; §9 sidecar + A10-A13/A15/A16 → T9 (A14 explicitly Plan 3); §11 compat list → T1/T7 shim + rebuilds each task; §12.3 → T9/T10; §12.5 masters' review → T10. Bilingual/i18n §10 beyond strings = Plan 3 by decomposition.
- **Placeholder scan:** T6 Step 3 contains one deliberately-corrected code fragment (the `\expandafter` line marked "drop — the \ifthenelse line is the implementation"); left as an explicit instruction, not a TBD. T7/T9 tests are named with concrete assertions but abbreviated bodies — each names its exact oracle (geometry formulas, exit codes, log strings), which the implementer can transcribe mechanically.
- **Type consistency:** `\swiss@meta{key}` accessor, `\swiss@classlevel` (−1 unset, 0-based index), `\annotationleading`/`\glossleading`/`\footnoteleading` lengths, `conftest.build_doc`/`swisscheck` signatures, sidecar key names — used identically across T1–T10.
- **Risk note:** the provider dispatch at `\AtBeginDocument` (T3) is the plan's most delicate LaTeX mechanism; T3's tests cover both provider-present and default paths, and T8 exercises it via a real identity file.
