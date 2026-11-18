# Brief for the fact-extraction subagent

Send one subagent per repository with a brief built from this template.
Fill the angle-bracketed parts; keep the rules verbatim. If the project
has its own schema, add or replace keys, but keep the citation rules.

---

You are extracting facts from one git repository for a confidential
project dossier. Work locally; do not send any content to external
services; do not run code from the repository.

**Context.** <one paragraph: the dossier's purpose, whose point of view it
takes, why this repository matters to it, and the facts already
established, with the file they live in.>

**Inputs.**
- Clone: `repos/<slug>`, pinned at `<pin>`. Read the pinned state with
  `git -C repos/<slug> show <pin>:<path>`, `git -C repos/<slug> ls-tree
  <pin> <dir>/`, `git -C repos/<slug> log <pin> -- <path>` and
  `git -C repos/<slug> log -S'<text>' <pin>` (to find when something
  appeared). Never check out or modify the clone.
- `extracted/repos/<slug>/inventory.md`, `bulk.txt`, `architecture.md`.
- `extracted/repos/<slug>/history/*.csv` (contributor statistics, bots
  and generated files already excluded).

**Output 1: `facts/_raw/<slug>.yaml`.** Only facts the repository
supports; omit empty keys.

```yaml
project:       # key -> {value, source, quote?}: name, purpose, licence, first commit,
               # latest release, default branch, homepage, status (active/archived)
languages:     [{language, share, source}]
components:    [{name, path, purpose, depends_on, tested_by, source}]
interfaces:    [{kind, name, description, source, quote?}]   # api|cli|format|protocol|config|plugin
build:         [{topic, summary, source, quote?}]            # build|test|ci|packaging|platforms|release
dependencies:  [{name, version, scope, source}]              # scope: runtime|build|dev|test
releases:      [{tag, date, source}]
contributors:  [{person, commits, first, last, areas, affiliation?, affiliation_source?, source}]
activity:      [{period, commits, active_people, source}]
ownership:     [{area, bus_factor, top_owner, top_share, source}]
governance:    [{topic, summary, source, quote?}]            # licence|contributing|codeowners|security|coc
events:        [{date, what, who?, source, quote?}]          # milestones found in history: rewrites,
                                                             # moves, ports, removals, first use of X
observations:  [{topic, summary, source}]
notes:         [{text, source}]
```

Rules:
- Every fact has a `source` in one of these forms:
  `<slug>@<rev>:<path>#L<a>-<b>`, `<slug>@<rev>:<path>#L<a>`,
  `<slug>@<rev>:<path>`, `<slug>@<rev> msg`, `<slug>@<rev> diff`,
  `<slug>@<rev>`, or `<slug> history:<file.csv>` for a figure from the
  history CSVs (name the row in `value` or a comment).
- `<rev>` is a 12-digit commit hash, never a branch or tag name. State at
  the pin: cite the pin. When something happened and who did it: cite the
  commit that did it.
- Where wording matters (licence terms, documented guarantees, supported
  platforms, deprecations, a commit's own account of a change), add
  `quote:` copied verbatim from the cited lines, message or patch, ≤ 300
  characters. Use `…` to elide; each kept piece must be verbatim.
- Dates as ISO (`2025-01-01`), from author dates for "when written" and
  tag dates for releases; say which in a comment when it matters.
- Figures from the history CSVs are copied, not recomputed. Line counts
  exclude `bulk.txt`; say so where you use them.
- An affiliation needs its own source (a commit email at that date is
  one, weaker, kind: say so); never infer it from a name.
- No secrets, keys, tokens or personal contact details in facts, even
  quoted. Email addresses only in `identities.csv`, which stays local.
- Do not reconcile with other sources and do not correct the repository:
  record what it shows.

**Output 2: `summaries/<slug>.md`**, in English, ≤ 1.5 pages:
1. What the software is, its licence, its age and its state at the pin.
2. Key figures (size, languages, commits, people, releases), each with
   its source.
3. Who built it and who maintains it now; bus factor of the main areas.
4. What concerns us: <the dossier's questions about this repository>.
5. Map: which paths hold what.
6. Conflicts with the established facts in `<canonical facts file>`.

**Finish** by running `<checker command>` on your YAML and fixing every
failure (correct commit, path, lines or wording; never delete a fact to
pass). Report: number of facts and quotes, checker result, conflicts
found, and anything you could not read or decided not to open.
