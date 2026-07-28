# SwissTeX Generalization — Identity Layer & Font Program

**Date:** 2026-07-27 · **Status:** approved section-by-section in design dialogue; pending final spec review
**Scope:** sub-projects #0 (font program) and #1 (identity + generalization layer) of the SwissTeX document family
**Version target:** SwissTeX v2.0 (deliberate, measured output changes; see §Compatibility)

---

## 1. Purpose and decomposition

SwissTeX serves company documents under a complete corporate identity. The full ambition is a
document family — reports/documentation, proposals, letters, slides — decomposed into sequenced
sub-projects, each with its own design cycle:

- **#0 Font program** (this spec, §3): U001 modernized → "SwissTeX Grotesk"
- **#1 Identity + generalization layer** (this spec, §4–§9): everything the family shares
- **#2 Proposals/offers**, **#3 Letters** (`swissletter`, DIN 5008 on the grid), **#4 Slides** — later specs, all consuming #1

**Architecture: Approach A (layered).** `swisstex.cls` stays the single enforcement point of the six
invariants and gains only *generic extension points* with today's behavior as defaults. All company
specifics live in one identity package. The class can later evolve into a core+classes family (KOMA
pattern) without reworking the identity contract.

## 2. Standing rules

1. **Never pay for fonts or tools.** Commercial licenses (e.g. Univers Next) permanently excluded.
2. **U001 as font base is a settled user decision**, made knowing AFPL is source-available, not
   OSI/FSF open source. In-house use is unrestricted; only public redistribution of the font itself
   would need re-examination. All other components use free licenses (GPL+FE, OFL, MIT, LPPL).
3. **Design process:** consult Müller-Brockmann, *Grid systems in graphic design* (user's scan in
   `~/Downloads/291c68bd945cf54840b603567f6d4135.pdf`) before asking the user; before committing a
   design decision, run masters' devil's-advocate passes (Müller-Brockmann for grid/layout/color,
   Frutiger for type) per the devils-advocate skill.
4. Neutral placeholders (`acme`) in all examples.

## 3. Sub-project #0 — Font program

**Base:** URW U001, 8 TTFs (Regular/Italic/Bold/BoldItalic + 4 Condensed), AFPL, sourced via
FontLibrary. Renamed **"SwissTeX Grotesk"** / **"SwissTeX Grotesk Condensed"** (AFPL requires
renaming modified versions; license text ships alongside).

**Measured verdict (2026-07-27 trial, fontTools scanline measurement, TeX Gyre Heros as
engineering baseline, Universalis ADF as structure benchmark):** U001's outlines are sound —
lowercase stems agree to 0.1 unit within styles; condensed cuts are genuinely drawn (stem retention
0.95 at width compression 0.71); design fidelity to Univers is the best of all free candidates
(drawn italic slant −17°, x-height/cap 0.69, bar/stem contrast 0.81). The Frutiger advocate's
DON'T-ADOPT flipped to adopt per its own falsifiability clause. Universalis measured *less*
Univers-faithful (mechanical obliques, −12°, x/cap 0.64, 10% bold `n` stem asymmetry); its
benchmark role is family structure only.

**Pipeline** (scripted, reproducible; Python + fontTools in `fonts/`; sources = pristine TTFs +
patch/feature files, never hand-edited binaries):

1. Rename + style-link (name IDs 1/2/4/6/16/17; R/I/B/BI linking; condensed as own linked family).
2. **Vertical-metrics unification** across all 8 styles (hhea/OS/2, `USE_TYPO_METRICS`) — the
   load-bearing fix; the class's strut arithmetic assumes it.
3. **Metadata repairs from the trial:** `post.italicAngle = −17°` in Italic and CondBoldItalic
   (currently −12/−11 vs drawn −17).
4. Kerning: class-based autokern floor + hand pass on display pairs (`AV Ta Wo`, digits vs
   punctuation for the foot line).
5. Coverage: `– — € „ “ ‚ ‘ … ‰` + DE/FR/EN punctuation completeness; new glyphs drawn to match;
   **license firewall:** Univers specimens and Universalis are visual references only — no outline
   or kerning data crosses in either direction.
6. Features: `kern`, `liga` (fi/fl), `tnum` if digits cooperate. Nothing else in v1.
7. QA gate: fontbakery; specimen sheets; a SwissTeX test document must pass swisscheck A2 in all 8
   styles.

**Known deviations, accepted:** Bold Italic runs +6.6% heavier than Bold (documented; correction
optional later — bold italic is rare in body text). **Open empirical question, gated:** the
condensed compression asymmetry (Regular-Cond 0.71 vs Bold-Cond 0.81). The legibility specimen
(§10) decides; if 0.71 is too narrow at annotation sizes, derive a gentler condensed by
interpolating within U001's own cuts (no license mixing).

**Math font:** TeX Gyre DejaVu Math, unchanged.

**2026-07-27 decisions from implementation:** coverage audit found zero missing codepoints (incl.
Euro) — RECIPES empty; sources ship URW-authored GPOS kerning (≈970–990 pair records per style;
Regular has 92 distinct first-glyph pair sets) — preserved by user ruling; curated kern.fea
retired to reference.

**2026-07-28 legibility-gate rulings (user, specimen-judged):** footnote/table leading frozen at
¾\gridunit = 10.125pt (strong 3:4 ratio ships; §8.1 gate passed); the native 0.71-compression
condensed judged too narrow at gloss sizes — a gentler ≈0.8 condensed is interpolated strictly
within U001's own cuts (Regular↔Condensed masters, no license mixing) and ships as "SwissTeX
Grotesk Condensed"; the native compressed cuts are not shipped.

## 4. Class extension points (`swisstex.cls`)

1. **`identity=<name>` class option** loads `swissidentity-<name>.sty` after option processing,
   before the font/color sections. Missing file → class error naming the search path. No identity →
   today's defaults.
2. **String table:** all user-visible strings via `\swiss@str{<key>}`; per-language definition
   `\swisssetstrings{<lang>}{table=…, figure=…, page=…, confidential-internal=…, …}`. Ships DE + EN;
   selection follows `lang`; unknown key → error at definition time, unknown language at use time →
   fallback EN + warning.
3. **Font provider:** the current `\setmainfont` block becomes the default provider; an identity
   defining `\swissidentityfonts` replaces it wholesale (dissolves the `Extension=.otf` /
   `*-regular` filename rigidity). Mixing families across one document remains impossible by
   construction ("no Helvetica with a Univers").
4. **Head/foot zones** (see §6) with empty-foot default.
5. **Logo primitive:** `\swisslogo[<grid lines>]{<file>}` — a block like any other, height in whole
   grid lines, placed via `\swiss@placebox`, horizontal anchor restricted to the existing axes
   (margin axis / text axis / full-measure edge). Missing file → error, not a dropped box.
6. **Cover slots** (§7).

## 5. Identity file contract

One file = one identity; **public setters only**, never internal patching — invariants remain
enforceable by the class alone.

```latex
% swissidentity-acme.sty
\swissidentitymeta{company={Acme AG}, legal={Sitz Musterstadt · HRB 12345}, web={acme.example}}
\swisssetcolors{accent={200,16,46}, paper={245,244,238}, ink={26,26,26}}
  % band: omitted -> band = accent (one red). An identity may set band ONLY as a
  % perceptually distinct value with a documented semantic role (checked by A15).
\newcommand{\swissidentityfonts}{%
  \setmainfont{SwissTeX Grotesk}[...]%
  \newfontfamily\condensed{SwissTeX Grotesk Condensed}[...]}
\swisslogofiles{cover=acme-logo.pdf, colophon=acme-mark.pdf}   % no head slot — see §6
\swissclassifications{public, internal, confidential, strict}  % localized via string table
\swissfootformat{\meta{docid} · \meta{version} · \meta{date}}
```

Documents carry only their own facts:

```latex
\documentclass[identity=acme]{swisstex}
\swissmeta{docid=TR-2026-014, version=1.2, classification=internal}
```

`\swissmeta` feeds foot line, cover slots, classification mark, and hyperref PDF metadata.
Color roles form a **closed set** (accent/band/paper/ink + fixed quiet/hairline); CI values map
into roles; no new roles without a class change.

## 6. Heads, feet, logo (Müller-Brockmann review outcomes applied)

- **Head:** pagina at **body grade (9.5pt)** in accent — per the book's rule (pagina aligned to a
  text line, sized as the body); running title stays condensed at annotation grade. **No logo in
  the running head** (review fix #1, accepted): a repeated mark informs once, then is advertising.
  The logo lives on cover and colophon.
- **Foot** (mirrors head geometry): classification mark, `\tracked` in accent, margin zone, printed
  only when ≥ internal (silence is the public state) · metadata line from `\swissfootformat` on the
  text axis in quiet — empty without `\swissmeta`.
- **Grid derivation:** `headsep = 2\gridunit`, `footskip = 3\gridunit`; head and foot baselines sit
  on the extended raster ("the page number must always be aligned with a line of the text").

## 7. Title block and covers

- **Named slots** replace positional arguments in `\swisstitle` and `\swisscover`: `kicker · title ·
  subtitle · client · date · docid · classification · logo`. Empty slots collapse; docid/date/
  classification auto-fill from `\swissmeta`, locally overridable.
- **Grid composition:** in-page title block rebuilt on `\swissdisplay` grades + whole-grid-line
  spacing (hand-set `21/23` and `6pt/9pt` die). Kicker/foot lines at annotation grade;
  classification as tracked accent mark in the kicker zone when ≥ internal.
- **The cover joins the page grid** (book pp.134–135: same grid, same type sizes as inside): band =
  grid-line span (default lines 38–46 of 51); glyph anchored to grid line + axis; **no
  page-fraction coordinates anywhere**; cover grades from the shared `\swissdisplay` scale.
- **Glyph is identity-bearing** (review fix #3): set deliberately by identity or document — no free
  default `a`.
- **Variants fix positions, documents fill content** (book rule (a)): an identity may define named
  variants (`report`, `proposal`, `manual`) — slot arrangement + band span + glyph on/off, all in
  grid units. Variant set is identity-definable, not closed.
- **Logo placement constrained:** grid line (vertical) × existing axis (horizontal), height in whole
  grid lines.

## 8. Derivation doctrine (v2.0)

Every measure belongs to exactly one class:

1. **Vertical rhythm — always grid-derived.** All skips/seps/kerns and *every leading* are
   `\gridunit` expressions. Ancillary leadings are **overridable Kennzahlen** whose defaults are
   commensurable strong ratios (review fix #2): `\annotationleading = ⅔\gridunit` (9pt: head, foot,
   legends, tracked) · `\glossleading = ¾\gridunit` (10.125pt: glosses, sidenotes, colophon) ·
   `\footnoteleading = ¾\gridunit` (10.125pt: footnotes, table bodies — tightened from 12pt/9:8 per
   the book's strong-ratio preference, **gated on the legibility specimen**, §10).
2. **Grades — role Kennzahlen**, never grid functions (the book chooses sizes for unmistakable
   contrast).
3. **Stroke weights — named Kennzahlen** (`0.4pt` hairline, `1.2pt` title rule), never grid-derived.

Small-grade block interiors keep their own tighter measure (manual §"Grenzen"); block exteriors
stay rastertreu. `\swisscode` (condensed) replaces raw `\texttt` so no Latin Modern leaks (§9 A16).

## 9. Verification (`swisscheck`) extensions

**Kennzahlen sidecar:** at end of document the class writes its *resolved* system — gridunit,
leading fractions, zones, color roles, font families — to `<jobname>.swisscheck`; the tool reads it
and verifies **declared relations, never hard-coded constants** (review fix #2, structurally).

New checks: **A10** foot (baseline on extended raster; classification confined to margin zone;
metadata on text axis) · **A11** head (pagina at body grade; *absence* of images in head zone) ·
**A12** cover (band edges + glyph anchor on grid lines; display sizes from shared scale; no
page-fraction residue) · **A13** commensurability (measured ancillary leadings = declared
fractions of the document's gridunit) · **A14** bilingual (both columns on one raster; pair tops
aligned; widths as declared; clean gutter) · **A15** color roles (embedded colors match declaration;
roles closer than a perceptual threshold flagged) · **A16** font inventory (only identity-declared
families + math font may be embedded).

## 10. Internationalization and bilingual setting

- **Localization:** string table DE + EN shipped; any language addable via `\swisssetstrings`;
  dates and PDF metadata follow `lang`.
- **Bilingual geometry** (book-derived): margin column *suspended* on bilingual pages; two columns
  of `(\fullmeasure − \gutter)/2` (≈67.5mm) — the book's ~10-words norm with its demonstrated
  ~7-word floor; the keep-margin alternative (49mm) violates it. Primary language left, fixed per
  document: `bilingual={german,english}`; per-column hyphenation via polyglossia.
- **Pairing, not streams:** `\bipar{<primary>}{<secondary>}` and `\bisection{}{}`  set translation
  units side-by-side as one grid block via `\swiss@placebox` — pair tops share a grid line; the
  taller member determines the next pair's start (rounded to the raster). Book rule (n) holds by
  construction. Tables/figures stay single with optional bilingual legend. A pair whose member
  overflows a page breaks *between* pairs, never inside one.
- **Script profiles** (approved extension): each language carries {font companion, size factor,
  justification policy, line-breaking engine, direction, density norm}. Consequences: I4 becomes
  *one family per script, harmonized* (EN/ZH companion: Noto Sans CJK SC, OFL, size factor 0.95 as
  default — specimen-tunable — via xeCJK); I5 becomes *per-script canonical policy* (Latin ragged; CJK justified with kinsoku);
  column widths optionally asymmetric per the pair's density norms (book p.31 sanctions width ∝
  amount of text); the raster is untouched because leading belongs to the grid, not the font.
  **Order:** DE/EN implements first; EN/ZH is the abstraction's validation target; RTL pairs
  deferred to their own design round (profile fields reserved; bidi correctness is not attempted
  in v1).

## 11. Compatibility, migration, error handling

- **v2.0 visible changes** (all measured, all deliberate): head/foot baselines onto the extended
  raster (sub-mm), gloss leading 10→10.125pt, footnote/table leading 12→10.125pt (specimen-gated),
  pagina 7.5→9.5pt, title block regrounded on display grades, one-red default (band=accent unless
  identity distinguishes), `\swisscover` positional syntax replaced by slots (compat shim for the
  old 4-argument form emits a deprecation warning for one minor version).
- Documents without `identity=` keep default palette/fonts/strings — output identical except the
  v2.0 changes above, verified by swisscheck green + visual diff of manual and demo.
- Errors are loud: missing identity file, missing logo file, unknown classification, unknown
  string key, missing script companion font → class errors with actionable messages, never silent
  degradation.

## 12. Verification plan (definition of done per stage)

1. **Font program:** fontbakery clean; all 8 styles' verticals identical; italicAngle fixed;
   specimen sheets rendered; SwissTeX test doc passes swisscheck A2 in every style.
2. **Legibility specimen** (gates two decisions): footnote/table matter at 8pt on 10.125pt vs
   12pt, and condensed annotations at the 0.71 compression — printed, judged, decision recorded in
   the spec before the doctrine constants freeze.
3. **Class v2.0:** manual + demo rebuild; swisscheck (all checks incl. new A10–A16) green on both;
   manual updated (option table mirrors class; new sections for identity, slots, bilingual).
4. **Bilingual:** a DE/EN and an EN/ZH test document pass A14; pair-break behavior demonstrated
   across a page boundary.
5. Every stage closes with a masters' review pass (rule §2.3) before its constants freeze.

## 13. Implementation order

1. Font program (#0) — unblocks everything visual
2. Legibility specimen → freeze doctrine constants
3. Class extension points + derivation doctrine (v2.0 core)
4. Identity file mechanism + `swissidentity-acme.sty` reference implementation
5. Head/foot + title/cover slots
6. swisscheck sidecar + A10–A13, A15–A16
7. i18n strings; bilingual DE/EN + A14; script profiles + EN/ZH validation
8. Documentation pass (manual, CLAUDE.md), final masters' review

## Appendix A — Trial measurements (2026-07-27)

| Measure | U001 | Universalis | Heros | Univers target |
|---|---|---|---|---|
| Lowercase stem discipline | exact (92.3×3) | reg exact; Bold `n` ±10% | exact | exact |
| Condensed stems @ compression | 0.95 @ 0.71 (drawn) | 0.96 @ 0.89 | 0.87 @ 0.82 | drawn |
| Drawn italic slant | −17° | −12° (mechanical oblique) | −12° | ≈ −16° |
| x-height / cap | 0.69 | 0.64 | 0.72 | ≈ 0.68–0.70 |
| H-bar / stem | 0.81 | 0.96 | 0.96 | ≈ 0.8 |
| italicAngle metadata | wrong in 2/4 | correct | correct | — |
| Bold↔BoldItalic weight | +6.6% drift | exact | exact | exact |
| Condensed compression logic | 0.71 / 0.81 asymmetric | uniform 0.89 | uniform 0.82 | uniform |

Method: horizontal/vertical scanline intersection on flattened outlines at mid-x-height /
mid-cap-height; `l`/`I`/`n`/`H` stems, `H` crossbar; slant from stem centers at 0.3/0.9 x-height.
Script: scratchpad `measure_stems.py` (to be moved into `fonts/tools/` in stage 1).

## Appendix B — Masters' review verdicts applied

- **M-B / corporate-vanity axis:** ADOPT-WITH-FIX → head logo struck (accepted by user).
- **M-B / template-thinking axis:** ADOPT-WITH-FIX → leadings as overridable Kennzahlen with
  specimen-justified defaults; swisscheck checks relations; variants identity-definable.
- **M-B / ornament axis:** ADOPT-WITH-FIX → one red by default; band only as documented distinct
  role; glyph identity-bearing; cover raster-share checked (A12).
- **Frutiger / clone axis:** DON'T-ADOPT → flipped to adopt by measurement (Appendix A) per its
  own falsifiability clause; named fixes folded into §3.
