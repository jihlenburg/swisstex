# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this is

`swisstex.cls` is a single-file XeLaTeX document class for non-fiction texts set to the
typographic rules of the Neue Schweizer Schule (Müller-Brockmann): a baseline grid, one type
family, a margin column that carries only labels. `swisstex-manual.tex` is both the reference
documentation and the largest test case — it is typeset with the class itself. `swisstex-demo.tex`
is a short conformance sample with the grid overlay switched on. `swisscheck.py` measures a built
PDF against the invariants (see Verify below).

There is no build system or package manager — just the class, the two documents, their built PDFs,
and the check script. Note that only `LICENSE` is tracked in git so far — the sources and PDFs are
still untracked in the working tree.

## Build

```bash
xelatex -interaction=nonstopmode swisstex-manual.tex   # run twice: hyperref bookmarks settle on pass 2
xelatex -interaction=nonstopmode swisstex-demo.tex
```

XeLaTeX is mandatory — the class calls `\RequireXeTeX` and uses `fontspec`/`unicode-math`. pdflatex
and lualatex will not work.

## Verify

```bash
python3 swisscheck.py swisstex-manual.pdf --tex swisstex-manual.tex
```

`swisscheck.py` (requires `pdfplumber`) measures the finished PDF against the invariants: axis
fidelity of rules (A1), baseline-grid binding measured absolutely from the page top (A2), right
text edge (A3), margin column and gutter kept clean (A4), table-legend alignment (A5), no heading
at the page foot (A6, needs `--tex`), the two margin zones (A7), no accidental indent at line
starts (A8), figure-legend alignment (A9). Exit code 0 = clean, 1 = violations. Non-default grids
are passed with `--gridunit`, `--textcolumn`, etc. Run it after any change that touches spacing or
placement — hand-set spacing and a forgotten `[t]` only show up in the output, never in the source.
`showgrid=true` remains the quick visual check.

Prerequisites beyond a base TeX Live: `tex-gyre` (the TeX Gyre Heros text fonts, used as the Univers
analogue), `tex-gyre-math` (supplies `texgyredejavu-math.otf`, family name `TeX Gyre DejaVu Math`),
plus `titlesec`, `needspace`, `enumitem`. Install with
`tlmgr install tex-gyre tex-gyre-math titlesec needspace enumitem` (append `--usermode` after
`tlmgr init-usertree` if the system tree is not writable). The `dejavu-otf` package is *not* needed —
it contains only legacy `.sty` support, not the math font.

macOS quirk: the class loads the body fonts by *filename* (resolved through kpathsea, works from any
texmf tree), but the math fonts by *family name* (`\setmathfont`), and XeTeX on macOS resolves names
through CoreText, which cannot see texmf trees. The name-looked-up fonts — `texgyreheros-*.otf` (for
the `range=\mathup`/`\mathit` loads) and `texgyredejavu-math.otf` — must therefore also be copied to
`~/Library/Fonts/`. Without that, the build dies at `\setmathfont` with fontspec's "font cannot be
found" even though `kpsewhich` resolves the files.

Build artefacts (`.aux`, `.log`, `.out`) are not gitignored — build in a scratch directory, or clean
up afterwards.

## The design contract: six invariants

The header of `swisstex.cls` states six invariants (I1–I6); `swisstex-manual.tex` §1 tabulates each
one against the mechanism that enforces it. They are the review criteria for any change:

- **I1** every vertical measure is an integer multiple of `\gridunit`
- **I2** rules and text blocks sit on the text axis; only declared *frame elements* (title, cover,
  colophon, colour bands) run to the full measure
- **I3** the margin column carries labels only, never running text
- **I4** one type family — differentiate by weight, size, width (`\condensed`), not by a second face
- **I5** ragged right with hyphenation and optical margin alignment
- **I6** headings bind to the block that follows them, never to the page foot

Concretely this means: **never write a hand-tuned `\vspace` or a bare length in points.** Express
vertical space as `\gridskip{n}` or `n\gridunit`, and horizontal measures in terms of the derived
lengths below.

## Architecture

The class file is organised in numbered sections (1–14) that follow the derivation order; read them
in sequence rather than jumping to a command definition.

### 1. Everything derives from the key–value options (§1–2)

Options are declared with `kvoptions` (`family=swiss`, `prefix=swiss@`) and the page is computed from
them with `calc`, never set literally:

```
\glosswidth      = \margincolumn - \numberzone      % left (gloss) zone of the margin column
\innermargin     = outermargin + margincolumn + gutter
\fullmeasure     = margincolumn + gutter + textcolumn
\measureshift    = -(margincolumn + gutter)         % text axis -> full measure
\swiss@textheight = gridlines x gridunit
geometry right   = paperwidth - innermargin - textcolumn
```

The consequence: to change the page, change a class option — do not adjust `\geometry` or individual
lengths. Adding a new option means adding the `\DeclareStringOption`, deriving from it in §2, *and*
updating the option table in the manual (§2 "Klassenoptionen").

### 2. The grid primitive `\swiss@placebox` (§5a)

The core of the class. An arbitrary block (title, table, figure, rule, colour band) has no height in
grid units and would shift all following text. `\swiss@placebox{<box>}{<left shift>}` repacks it so
it behaves like a sequence of whole lines: height raised to `\ht\strutbox`, depth padded up to a
multiple of `\gridunit` via `\swiss@ceil` (integer ceiling computed without modulo), then an
invisible strut-depth `\hbox` so `\prevdepth` survives the enclosing group. `\topskip` is pinned to
`\gridunit` (§5) so the same arithmetic holds at a page top, where `\topskip` replaces the normal
baseline skip.

Everything that places a block goes through it: `\snaptogrid`, the `gridblock` environment,
`\swisstitle`, `\sectionrule`, `swisstable`, `swissfigure`, `swissband`. Passing `-\measureshift` as
the second argument is what makes an element a *frame element* running to `\fullmeasure`; passing
`\z@` keeps it on the text axis.

If you build a new block-level element, wrap it in `\swiss@placebox` rather than adding vertical
space around it.

### 3. The grid catch `\gridsnap` (§5b)

The complement for environments the class does not own. It reads `\pagetotal` after `\par`, pads to
the next multiple of `\gridunit`, and fixes `\prevdepth` the same way. `\gridsnapenv{<name>}`
registers an environment via etoolbox's `\AfterEndEnvironment` — deliberately *not*
`\AtEndEnvironment`, which fires before the environment emits its own trailing space. A list of LaTeX
and amsmath environments is registered at `\AtBeginDocument`; add to that list rather than patching
individual call sites.

### 4. Two columns with distinct roles (§7–11a)

`\textcolumn` is the only reference width for body content — it is the text axis, and `\reversemarginpar`
places margin material to its left. The margin column is split: `\glosswidth` on the left for glosses
and captions (`\marg`, `\sidenote`, table/figure legends), `\numberzone` on the right for section and
page numbers, so the two can never collide on a shared line.

Section numbers are set at display size in the margin via `\marginlabel` + `\sectionnumberstyle`, and
`\smash`ed so a large numeral cannot lift the grid.

### 5. Sectioning is wrapped, not just formatted (§8)

`\section` and `\subsection` are captured with `\let` and re-defined through `\@ifstar` to inject
behaviour titlesec cannot express: `\section` prepends `\sectionrule` (the hairline, itself placed via
`\swiss@placebox`) and raises an `@aftersection` flag; `\subsection` consumes that flag to bind tightly
to a preceding section (`\nopagebreak[4]`) or otherwise demand `\Needspace*{6\gridunit}`. If you touch
sectioning, preserve this star-form dispatch — a plain `\titleformat` change will silently drop it.

### 6. Type scale derives from the grid too (§5c)

`\swissdisplay{n}` sets leading to `n\gridunit` and size to `0.80` of that, with negative tracking
above two lines. Display sizes are therefore grid-locked by construction; do not introduce a literal
`\fontsize` for headings.

### 7. Tables and figures are not floats (§11, §11a)

`swisstable` and `swissfigure` place the body on the text axis and the number plus legend in the
margin column, as one `\swiss@placebox`ed unit at the point of writing. Floats are deliberately
unsupported — they do not combine with a baseline grid plus margin column.

Two traps documented in the source and the manual:
- `tabularx` cannot be wrapped in a custom environment (it reads its body up to the literal
  `\end{tabularx}`), so it must be written out inside `swisstable`.
- The `[t]` in `\begin{tabularx}{\textcolumn}[t]{...}` is mandatory; without it the margin legend
  aligns to the table's vertical centre instead of its head row.
- `swissfigure` measures its content and raises the caption box by the height difference, with
  `\figcapdrop` compensating ascender vs. cap height — a plain `[t]` alignment fails because graphics
  and TikZ boxes carry their reference line at the bottom.

## Conventions

- **Language is German** throughout: class comments, manual, and user-visible strings
  (`\tablecaptionprefix`, `\figurecaptionprefix`). Comments in `swisstex.cls` transliterate umlauts to
  ASCII (`Abstaende`, `Ueberschriften`); the `.tex` documents use real umlauts. Keep both conventions.
- Comments in the class explain *why* a construction is necessary (which TeX mechanism would otherwise
  break the grid), not what it does. Match that when adding code — those comments are the class's real
  documentation.
- The version appears in two places and must be bumped in both: `\ProvidesClass` in `swisstex.cls:22`
  and the cover plus colophon strings in `swisstex-manual.tex` (lines 11 and 275).

## Pitfalls

- The licence is MIT everywhere (`LICENSE` and the `swisstex.cls` header). Do not reintroduce LPPL.
- The manual's option table (§2 "Klassenoptionen") mirrors `swisstex.cls` §1. `swisstex.cls` is the
  source of truth; update the table in the same change whenever an option or default changes.
- If you measure a PDF yourself, convert between TeX points (1/72.27 in) and DTP points (1/72 in) —
  `swisscheck.py` does this via its `PT` constant. Skipping the factor makes a correct grid look
  like it drifts by about 0.05 pt per line.
