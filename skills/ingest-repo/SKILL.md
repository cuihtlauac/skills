---
name: ingest-repo
description: Ingest a git repository into a local, text-first project dossier, the way ingest-document does for a PDF. The repository is pinned at one commit and registered; an inventory (files, languages, build, CI, tags, generated or vendored content) and contributor statistics (people, activity over time, areas, bus factor) are produced; its architecture is mapped with path citations; and its facts are extracted with citations to a commit, file and line range, whose verbatim quotes are machine-checked against git. Use when a codebase becomes evidence in a dossier (due diligence, a bid or tender, an audit, a takeover, a partner's or a competitor's project), when the user asks to "ingest", "map", "survey" or "extract the facts from" a repository, or when the project has an INGEST.md-style procedure for repositories. Not for working on the code itself, nor for one-off questions about a repository.
---

# Ingest a git repository into a dossier

A dossier is a repository of sources plus everything derived from them:
text, facts and summaries. Ingesting a git repository turns it into those
derived files so that later questions are answered from cited code, docs
and history, not from memory of a browse. It is the counterpart of
`ingest-document`: same dossier, same registry, same facts tree, different
anchors. Where a PDF fact cites `<slug> p.N`, a repository fact cites a
commit, and optionally a file and lines at that commit.

## Before you start

1. **Read the project's own procedure first.** If the dossier has an
   `INGEST.md`, a `CLAUDE.md` section on ingestion, a sources registry,
   scripts or a fact checker, they win over this skill wherever they
   differ. This skill is the default when the project says nothing.
2. **Confidentiality.** A private repository is a confidential source; a
   public one may still be ingested for a confidential purpose. Work
   locally: no hosted code-analysis service, no upload. Reading the
   project's issue tracker or pull requests through `gh` or an API is
   fine for a public repository and needs the user's go-ahead for a
   private one. Derived files inherit the source's confidentiality.
   `identities.csv` holds email addresses: keep it out of anything shared.
3. **Never modify the clone.** No commits, no checkout of another branch
   in a clone that the user also works in, no hooks run. Everything
   derived must be rebuildable from the URL and the pinned commit.

## Citations

A repository is identified by a slug, like a document. A fact's `source`
is one of:

| form | cites | a `quote` must occur in |
|---|---|---|
| `<slug>@<rev>:<path>#L<a>-<b>` | lines a..b of a file | those lines (± 3) |
| `<slug>@<rev>:<path>#L<a>` | one line | that line (± 3) |
| `<slug>@<rev>:<path>` | a file or directory | the whole file |
| `<slug>@<rev> msg` | a commit message | the message |
| `<slug>@<rev> diff` | a commit's patch | the patch |
| `<slug>@<rev>` | a commit | (no quote) |
| `<slug> history:<file.csv>` | a figure computed by `history.py` | (no quote; name the row) |

`<rev>` is a commit hash abbreviated to 12 hex digits, never a branch
or tag name, which move. Use the pinned commit for anything about the
current state, and the commit that introduced something for anything
about when or by whom. The checker accepts the pinned commit and its
ancestors, so citations stay valid when the pin later moves forward.

## Pipeline

Run from the dossier root. Each step lists the files it produces.
`<skill-dir>` is this skill's directory; the scripts need only Python 3,
PyYAML and git.

### 1. Clone, pin, register

```sh
git clone --no-checkout <url> repos/<slug>        # or `git -C repos/<slug> fetch`
git -C repos/<slug> rev-parse origin/HEAD          # the default branch's tip: the pin
```

Add `repos/` to the dossier's `.gitignore`: clones are rebuildable and are
not part of the record. Add one line to the sources registry:
`<slug>\trepo\t<url>\t<pinned sha>` (full 40-digit hash). Choose the
`slug` as for a document: short, lowercase, hyphenated, stable. When the
user supplies a local clone or a bundle instead of a URL, record where it
came from in a comment line (`# <slug>: bundle received 2026-03-02`), never
an absolute path that names a user or a machine.

Re-ingesting later means fetching, choosing a new pin and updating that
registry line; older citations keep checking because the old pin is an
ancestor. If history was rewritten (the old pin is no longer an ancestor),
register the new state under a new slug (`<slug>-2`).

### 2. Inventory and triage

```sh
python3 -I <skill-dir>/scripts/inventory.py repos/<slug> <pin> --slug <slug> \
  > extracted/repos/<slug>/inventory.md
```

It lists, at the pinned commit: history size and tags; files and lines by
directory and by extension; notable files (readme, licence, governance,
changelog, build and packaging, CI, containers, docs); submodules; and a
triage of files that look generated, vendored, minified or bulk, both at
the pin and, by line churn, over the whole history (bulk files are often
deleted later but still dominate line counts).

Go through the triage and decide, for each flagged file or pattern,
whether it is hand-written. Open a few: a "generated" marker can be a
comment about something else; a large file can be hand-written law, data
or tests. Write the excluded ones as globs, one per line with a comment
giving the reason, to `extracted/repos/<slug>/bulk.txt`. When unsure,
leave a file in and say so in a comment: excluding hand-written work
understates someone's contribution.

### 3. History

```sh
python3 -I <skill-dir>/scripts/history.py repos/<slug> <pin> extracted/repos/<slug>/history \
  --exclude extracted/repos/<slug>/bulk.txt \
  [--identities extracted/repos/<slug>/identities.tsv] [--bots extracted/repos/<slug>/bots.txt] \
  [--area-depth 2]
```

It writes `contributors.csv`, `monthly.csv`, `areas.csv`,
`area_ownership.csv` (with the bus factor: the fewest people who together
made half of an area's hand-written line changes), `years.csv` and
`identities.csv`. Authors go through the repository's `.mailmap`.

Then settle identities, which git does not:

- Read `identities.csv` and the "possible duplicate" lines on stderr. The
  same person often commits under several names (a handle, a full name,
  a name in capitals) and emails (work, personal, `noreply`). Merge only
  on evidence: same email, same handle, a `.mailmap` elsewhere, a profile
  page. Write `raw<TAB>person` lines (raw = an email or a name, case
  ignored) to `identities.tsv`, with a comment per merge giving the
  evidence, and rerun.
- List bots that do not end in `[bot]` (release automation, dependency
  updaters, mirror scripts) in `bots.txt`.
- Pick `--area-depth` so that areas mean something (1 for a small
  project, 2 when the top level is `src/`, `packages/` or `lib/`).

Affiliations (who worked for whom, when) are facts about people, not
about the repository: an email domain is a hint, not evidence. Record an
affiliation only with a source (a profile, a staff page, a paper, a
commit email at that date) and say which kind of source it is.

### 4. Architecture map

The counterpart of the PDF vision pass. Produces
`extracted/repos/<slug>/architecture.md`. Follow
**[architecture.md](architecture.md)**: it fixes the outline, the citation
of every claim to a path at the pin, and what never to do. Large
repositories: split the top-level areas among parallel subagents, each
briefed with architecture.md, the clone path, the pin and its areas; then
assemble and write the overview yourself.

### 5. Facts and summary

Delegate to one subagent per repository so file dumps stay out of the
main context. Brief it with **[facts.md](facts.md)**: the dossier's
context, the clone and pin, the inventory, history and architecture files,
the YAML schema and citation rules, and the summary outline. Outputs:
`facts/_raw/<slug>.yaml` and `summaries/<slug>.md`.

### 6. Verify

Run the project's checker if it has one; otherwise:

```sh
python3 -I <skill-dir>/scripts/check_refs.py --sources sources.tsv facts/_raw/<slug>.yaml
```

Every cited commit must exist and be the pin or an ancestor, every path
and line range must exist at that commit, and every quote must occur in
what is cited. Sources that are not registered repositories (PDF pages,
meetings) are skipped, so the same YAML can mix both; run the document
checker on it too. Fix or justify each failure: correct the commit, path
or lines, or copy the wording exactly. **Never delete a fact just to make
the check pass.**

### 7. Reconcile, propagate, commit

As for a document. Update the canonical fact files from the raw
extraction, keeping the sources. What a repository shows (code, history)
and what documents claim about it (a proposal, a deck, a website) can
disagree: record both in a `conflicts` list with their sources; never
resolve one silently. A repository is evidence of what exists at the pin,
not of what is planned. Then update the document index, open questions,
the overview, the backlog and the changelog; log the run (date, slug,
pin, commits, files, bulk patterns, identities merged, facts and quotes
checked) in the ingestion log if there is one. Commit; if anything leaves
the machine, apply `redact-publish`.

## Done when

- the repository is cloned outside the record, pinned and registered;
- `inventory.md` exists and every triage entry is decided in `bulk.txt`;
- the history CSVs exist, identities are settled with evidence and bots
  are listed;
- `architecture.md` covers every top-level area, each claim with a path;
- `facts/_raw/<slug>.yaml` and `summaries/<slug>.md` exist and
  `check_refs.py` passes;
- conflicts are recorded, propagation is done, and the work is committed.
