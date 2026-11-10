# Transcribing pages by vision

Goal: a Markdown file from which someone who never opens the PDF can answer
any question the pages answer, quote any visible text, and know what each
figure shows. Fidelity first: transcribe, don't summarize, don't interpret.

## Inputs

- the PDF;
- its text layer, `pdftotext -layout`, form feed = page break (page N is
  the N-th chunk); `pdftotext -raw -f N -l N` when columns are interleaved;
- page images: `pdftoppm -r 110 -png -f N -l N <pdf> <scratch>/p`. Use a
  higher resolution (150–200) or crop for dense tables, Gantt charts and
  small labels; 80 is enough for triage only.

Read **every** page image. The image decides what is on the page and how it
is laid out; the text layer gives the exact spelling of what you see.
Copy wording from the text layer whenever it matches what is visible, so
quotes later match the checker.

## File layout

```markdown
# <Document title> — transcription

Source: `<file name>` (<N> pages, <origin, e.g. PowerPoint export>, <date if stated>).
Recurring elements omitted below: <footer, logos, confidentiality banner,
page numbers, template text present in the text layer but not visible>.

## Slide 1 — <title as written>
<!-- page 1 -->

<content>

## Slide 2 — <title>
<!-- page 2 -->
...
```

- One section per page, in page order, none skipped. For prose documents
  use `## Page N — <heading>`. A page with no title: use a short
  descriptive title in brackets, `## Slide 7 — [photo page]`.
- The `<!-- page N -->` anchor is mandatory: tools and citations rely on it.
- **Match the project first.** If the project already has transcripts,
  copy their conventions (language of descriptions and labels, column
  layout of Gantt tables, abbreviations) so files stay consistent.
  Otherwise write the preamble, labels (`Recurring elements`, `Figure`,
  `Note`) and figure descriptions in the language of the document. Never
  translate the document's own text.
- Recurring elements are described once in the preamble, with the pages
  they cover (`p. 2–23`), then omitted. A title page usually differs:
  transcribe it fully. Mention recurring elements again only where a page
  differs (e.g. a different banner). Template text present only in the
  text layer (hidden footers, legal notices) is listed in the preamble
  once, verbatim if short, so readers know it exists.
- Section/agenda markers on the page (breadcrumb, chapter tag): one line
  `*Section: <text>*` under the anchor.

## Text

- Keep the document's wording, spelling, accents, capitalization, typos and
  typographic quotes/arrows (« », 🡺, →) as they appear.
- Reproduce structure: headings as `**bold**` lines, bullets as `-` with
  nesting by indentation, numbered lists as `1.`, emphasis as visible
  (`*italic*`, `**bold**`, `<u>underlined</u>`).
- Glyphs: when the render shows a missing-glyph box but the text layer has
  a character (🡺, ✓), use the text layer's character.
- Order: reading order of the slide (title, then top-to-bottom,
  left-to-right by visual block). Text inside a figure belongs to the
  figure description, not to the body.
- Callouts, stamps, footnotes (`*en prenant pour …`), sources and
  speaker-visible dates are content: keep them.
- Text in the text layer but not visible in the render (hidden boxes,
  off-canvas notes): do not mix it into the body; if it matters, add one
  line `Text layer only: « … »`.

## Tables

Markdown tables with the header row as printed. One table row per printed
row; merged cells → repeat the value or leave the continuation cell empty
(be consistent within a table). Numbers exactly as printed, units kept
(`81 M€`, `1 000+`). A table rendered as an image is still a table.
When cell colour carries meaning (traffic lights, ✓/✗ shading), add a
tag in the cell, `[vert]`/`[rouge]` (in the document's language), and one
`Note:` line under the table giving the legend if the page states it.

## Figures

Each figure is a block quote starting with `> Figure:`, placed where the
figure sits relative to the text.

- Say what kind of figure it is (architecture diagram, flow chart, photo,
  map, bar chart, Gantt, logo wall, org chart…), then its content.
- Diagrams: name every box with its label in quotes « … », its colour or
  shape when it carries meaning, and every arrow with its direction and
  label (`A → B`, `A ↔ B`). For complex diagrams use a nested list inside
  the block quote, one line per component.
- Charts: axes, units, series, and the values you can read (approximate
  values prefixed with `≈`).
- Photos and logos: identify only what is evident (labels, legible names);
  do not guess unnamed objects.
- Repeated figure: "Same <x> as slide N, with …" and only the differences.

## Gantt charts and plans

Transcribe them as a table, not a sentence:

```markdown
> Figure: Monthly Gantt chart "<title>", columns <first month> → <last month>.
> Milestone lines at <…>. Bars (read from the chart):

| Lot | Tâche | Début | Fin |
|---|---|---|---|
| Lot 1 - … | … | mai 2024 | juil. 2024 |
|  | … | août 2024 | mai 2025 |
```

- One row per bar, with separate start and end columns; month
  granularity, both inclusive. Spell months as the chart's own axis does;
  if the axis gives no model, use the usual abbreviation of the language
  (French: janv. févr. mars avr. mai juin juil. août sept. oct. nov. déc.).
  State any reference such as `T0 = …`.
- Discontinuous bars: all segments in the start cell, separated by ` ; `,
  ranges with `–` (`mai–juil. 2024 ; mai 2025 ; févr.–août 2026`), end
  cell empty. Milestones (diamonds, flags) and one-month bars: same start
  and end.
- Reading dates: Gantt bars are usually drawn shapes with no text layer.
  Render at 150–200 dpi, locate the month column boundaries on the axis
  (pixel x of each label/gridline), and map each bar's left and right edge
  to a column; a bar edge within a few pixels of a boundary is ambiguous —
  zoom on it, and if still unsure write `≈` before the date. Put "read
  from the chart" caveats in the figure line, not in each row.
- Callouts and labels attached to the chart (« Livraison … », `*T0 = …`)
  go on their own lines above the table.

## Never

- Never invent text, values, names or arrows you cannot see. Write
  `[illegible]` for unreadable parts and `[cut off]` for text truncated by
  the slide edge.
- Never summarize several bullets into one, or drop a bullet because it
  seems unimportant.
- Never "fix" the document (wrong dates, inconsistent numbers): transcribe,
  and note an evident inconsistency in an `Note:` line if useful.
- Never paste the raw text layer as the transcript: its order and line
  breaks follow the PDF objects, not the page.

## Diagrams with unlabelled parts

Unlabelled elements (identical boards, icons) are described by position
and appearance (« carte 1, vert foncé, à gauche »). If the slide text or a
later slide names them, say so (`= carte de contrôle, cf. légende`);
otherwise do not guess.

## Self-check per page

Before moving on: every visible text block is in the section (or in a
figure description, or declared recurring); every figure has a description;
numbers and dates match the image; the anchor is right. After the whole
document (or your page range, with `--pages`), run
`scripts/check_transcript.py` and review the flagged pages.
