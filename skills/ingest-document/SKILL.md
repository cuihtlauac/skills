---
name: ingest-document
description: Ingest a source document (PDF, slide deck, Word file, spreadsheet) into a local, text-first project dossier. The document is registered, its text extracted, image-only pages, slides, figures and Gantt charts transcribed by vision into page-anchored Markdown, and its facts extracted with page citations and verbatim quotes that are machine-checked against the text layer. Use when a new document arrives in a dossier/knowledge repository (contract, amendment, specification, deliverable, proposal, slide deck, paper), when the user asks to "ingest", "transcribe", "extract the facts from" or "add this document", when a deck or scanned/figure-heavy PDF has to become searchable text, or when the project has an INGEST.md-style procedure. Not for code repositories or one-off questions about a PDF.
---

# Ingest a document into a dossier

A dossier is a repository of source documents plus everything derived from
them: text, transcriptions, facts and summaries. Ingestion turns one new
source into those derived files so that later questions are answered from
cited text, not from memory of a PDF.

## Before you start

1. **Read the project's own procedure first.** If the repository has an
   `INGEST.md`, a `CLAUDE.md` section on ingestion, a sources registry
   (`sources.tsv` or similar), extraction scripts or a fact checker, they win
   over this skill wherever they differ (paths, schema keys, checker
   command). This skill is the default when the project says nothing.
2. **Confidentiality.** Treat every source as confidential unless the user
   says otherwise. Convert locally only: no hosted OCR/conversion service, no
   upload, no pasting into external tools. Claude reading the pages is the
   only exposure. Derived files inherit the source's confidentiality.
3. **Never modify the original.** Keep the source file under its original
   name; everything else must be rebuildable from it.

## Pipeline

Run from the repository root. Each step lists the files it produces.

### 1. Register

Add one line to the sources registry: `<slug>\t<kind>\t<file name>`.

- `slug`: short, lowercase, hyphenated, stable (`ec1-report`, `avenant-1`).
  It is what citations use.
- `kind`: `prose` (text PDF), `slides` (PDF exported from a deck), `sheet`
  (spreadsheet).
- `.docx`/`.pptx`/`.odt`: convert to PDF first and keep both files:
  `soffice --headless -env:UserInstallation=file:///tmp/lo-ingest --convert-to pdf <file>`
  (the separate profile avoids clashing with a running LibreOffice).
- Badly named files (`main (3).pdf`): rename to something descriptive
  before registering, and say so in the commit.

### 2. Mechanical extraction

```sh
pdfinfo <file> | grep Pages
pdftotext -layout <file> extracted/text/<slug>.txt   # form feed = page break
```

Check that the number of form feeds equals the page count. Then, by kind:

- `prose`: also produce Markdown with headings and tables, with
  `<!-- page N -->` anchors (Docling with OCR off works well; run it in a
  local venv). Spot-check a few tables against page images.
- `sheet`: one CSV per sheet (`ssconvert -S --export-type=Gnumeric_stf:stf_csv <file> 'extracted/<slug>/%n-%s.csv'`).
- `slides`: the text layer alone is not enough; go to step 3 for every page.

Triage pages with little text:

```sh
python3 -I <skill-dir>/scripts/lowtext_pages.py extracted/text/<slug>.txt
```

Render each flagged page (`pdftoppm -r 80 -png -f N -l N <file> <scratch>/p`)
and look at it: blank → note it and move on; scanned text → `ocrmypdf
--pages N -l <lang>` locally; figure, chart, Gantt, diagram → step 3.

### 3. Transcription (vision pass)

For slide decks (all pages) and for the figure/Gantt/diagram pages of prose
documents. Produces `extracted/slides/<slug>.md` (or the project's
equivalent).

Follow **[transcription.md](transcription.md)** exactly: it fixes the page
rendering, the section format, how to use the text layer for exact wording,
how to describe figures and transcribe Gantt charts, and what never to do.
Then measure coverage:

```sh
python3 -I <skill-dir>/scripts/check_transcript.py extracted/text/<slug>.txt extracted/slides/<slug>.md
```

It checks that every page has a section and reports, per page, the share of
text-layer words found in that page's section. Investigate every page it
flags; low coverage is acceptable only for text that is hidden in the
render (template footers, off-slide text) and you then say so in the
transcript.

Long decks: split the pages among parallel subagents (≈ 10–15 pages each),
each briefed with transcription.md, the PDF path, the text path and its page
range; each checks its range with `check_transcript.py --pages`. Then
concatenate. Keep page images out of the main context.

### 4. Facts and summary

Delegate one subagent per document so page dumps stay out of the main
context. Brief it with **[facts.md](facts.md)**: the project context, the
document and text paths, the YAML schema and citation rules, and the summary
outline. Outputs: `facts/_raw/<slug>.yaml` and `summaries/<slug>.md`.

### 5. Verify

Run the project's fact checker if it has one; otherwise:

```sh
python3 -I <skill-dir>/scripts/check_quotes.py --sources sources.tsv facts/_raw/<slug>.yaml
```

Every cited page must exist and every quote must appear on its page (± 1)
in the `-layout` or `-raw` text layer (tables split quotes in layout mode).
Fix or justify each failure: correct the page, copy the wording exactly, or
mark a quote read from an image with `quote_from_image: true`. **Never
delete a fact just to make the check pass.**

### 6. Reconcile

Update the canonical, hand-maintained fact files from the raw extraction,
keeping the sources. Binding documents (signed contracts, amendments)
override planning documents (proposals, decks, drafts). When two sources
disagree, record both values with their sources in a `conflicts` list;
never resolve a conflict silently.

### 7. Propagate and commit

Update whatever the project keeps around the facts: the document index
(mark the document as local, add documents it mentions), open questions
(answer, close or add, keeping IDs stable), the dossier/overview, the
backlog for new work, the changelog. Log the run (date, slug, pages,
special handling, quotes checked) in the project's ingestion log if it has
one. Commit; if anything leaves the machine, apply `redact-publish`.

## Done when

- the source is registered and its text extracted, page count matching;
- every slide/figure page has a transcript section and `check_transcript.py`
  flags nothing unexplained;
- `facts/_raw/<slug>.yaml` and `summaries/<slug>.md` exist and the quote
  check passes;
- conflicts are recorded, propagation is done, and the work is committed.
