# Brief for the fact-extraction subagent

Send one subagent per document with a brief built from this template. Fill
the angle-bracketed parts; keep the rules verbatim. If the project has its
own schema (e.g. a spec-specific key list), add or replace keys, but keep
the citation rules.

---

You are extracting facts from one document of a confidential project
dossier. Work locally; do not send any content to external services.

**Context.** <one paragraph: the project, the parties, whose point of view
the dossier takes (e.g. "we are partner X, responsible for Y"), the
reference dates and amounts already established, with the file they live
in.>

**Inputs.**
- Document: `<path to PDF>` (<N> pages).
- Text layer: `<extracted/text/slug.txt>`; form feed = page break, so page
  N is the N-th chunk. `pdftotext -raw -f N -l N <pdf> -` helps when table
  columns are interleaved.
- Transcript (if any): `<extracted/slides/slug.md>`, with `<!-- page N -->`
  anchors, for slides and figures.

Read the whole document. Render a page
(`pdftoppm -r 110 -png -f N -l N <pdf> <scratch>/p`) only when the layout
is unclear or the content is a figure.

**Output 1: `facts/_raw/<slug>.yaml`.** Only facts present in the
document; omit empty keys.

```yaml
project:      # key -> {value, source, quote?}  dates, duration, amounts, references
partners:     [{name, role, source}]
workpackages: [{id, title, leader, partners, our_role, start, end,
                person_months: {ours, total}, tasks: [{id, title, owner}], source}]
deliverables: [{id, title, wp, owner, due, type, source, quote}]
milestones:   [{id, title, due, criteria, payment_eur, deliverables, source}]
budget:       [{partner, item, amount_eur, aid_eur, source}]
obligations:  [{topic, summary, deadline, source, quote}]
              # topic: reporting|ip|confidentiality|publication|exploitation|
              #        repayment|governance|withdrawal|liability|other
risks:        [{risk, mitigation, owner, source}]
notes:        [{text, source}]
```

Rules:
- Every fact has `source: "<slug> p.N"` (PDF page, 1-based; `p.N-M` for a
  range). Use the PDF page index, not the printed page number.
- Where wording matters (dates, amounts, obligations, definitions), add
  `quote:` copied verbatim from the text layer, in the original language,
  ≤ 300 characters. Use `…` to elide; each kept piece must be verbatim.
- A quote read from an image (absent from the text layer) gets
  `quote_from_image: true`.
- Dates as ISO (`2025-01-01`, `2025-01` for month precision). Relative
  dates (`T0+12`) are kept as written in `value` and resolved in a note
  only when the document itself fixes T0.
- Values read by eye from a chart: say so in a YAML comment.
- Do not reconcile with other documents and do not correct the document:
  record what it says.

**Output 2: `summaries/<slug>.md`**, in English, ≤ 1.5 pages:
1. Purpose, author, date, parties.
2. Key dates and numbers, each with `(p.N)`.
3. What concerns us: tasks, deliverables, dates, money, obligations.
4. Page map: which pages hold what.
5. Conflicts with the established facts in `<canonical facts file>`.

**Finish** by running `<checker command>` on your YAML and fixing every
failure (correct page or wording; never delete a fact to pass). Report:
number of facts and quotes, checker result, conflicts found, pages you
could not read.
