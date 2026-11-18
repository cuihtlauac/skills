# Architecture map

The map is to a repository what the transcript is to a slide deck: a
readable text that later work cites instead of re-reading the source. It
describes what is at the pinned commit, in the dossier's language, and
every claim in it points at a path.

## Inputs

- The clone (`repos/<slug>`) and the pin. Read files with
  `git -C repos/<slug> show <pin>:<path>` and list them with
  `git -C repos/<slug> ls-tree --name-only <pin> <dir>/`, so you read the
  pinned state even if the clone's checkout differs. Never check out.
- `inventory.md` (where the lines are, notable files, triage) and
  `bulk.txt` (what is generated or vendored: describe it in one line, do
  not map it).
- The history CSVs, for "who" and "since when" (cite them, do not
  recompute).

## Outline

```markdown
# Architecture: <slug> @ <pin, 12 digits>

## Overview
What the software is for, who uses it, how it is delivered (library,
service, CLI, app, plugin), in a few sentences. Main languages with their
share of lines (inventory.md).

## Components
### <component name> (`<path>/`)
Purpose, entry points, main modules or types, what it depends on inside
the repository and outside (packages), how it is tested. 3–10 lines.
(one subsection per top-level area that holds hand-written code)

## Build, test, release
Build system and commands, test suites and how they run, CI jobs and
platforms, packaging and release channels, versioning (tags).

## Interfaces
Public APIs, CLIs, file formats, protocols, configuration, extension
points: what another system would touch.

## Data and external services
Databases, network services, credentials or secrets handling (say where
they are configured, never copy a secret), telemetry.

## Generated and vendored content
One line per bulk.txt pattern: what it is, what generates it.

## Docs and governance
Where the docs live and what they cover; licence; contribution rules;
code owners; security policy.

## Observations
Things a reader would want flagged: dead or duplicated code, TODO/FIXME
density, missing tests for a component, unusual build steps, platform
specifics. Each with a path.
```

## Rules

- **Cite every claim** with a path at the pin, inline, in backticks:
  `` `src/server/main.ts` ``, or with lines for a specific point:
  `` `src/server/main.ts#L40-62` ``. A claim you cannot point at does not
  go in.
- **Describe, do not judge,** except under Observations, and there only
  with the evidence.
- **Read before describing.** A directory name is not evidence of what is
  in it. Open at least the entry point and one representative file per
  component.
- **Quote names exactly:** modules, functions, commands, options, file
  formats, as spelled in the code.
- **Never run code from the repository** (builds, tests, scripts,
  installers) unless the user asks: it executes with your session's
  access. Reading is enough for a map.
- **Never copy secrets, tokens, keys or personal data** found in the code
  or its history; note that they exist and where, and tell the user.
- **Say what you skipped:** a component you only skimmed is marked
  "(skimmed)", one you did not open is not described.
- Long repositories: one subagent per group of areas, each writing its
  `### Components` subsections with the same rules; you write the
  Overview, Build, Interfaces and Observations from their parts.
