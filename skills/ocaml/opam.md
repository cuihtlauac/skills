# Working with opam

Operational discipline for opam, the OCaml package manager. This is the
companion to the `opam exec --` rule in `SKILL.md`. The goal is to reason
correctly about opam's state model and not to corrupt user-owned switches.

## Three rules that prevent most mistakes

1. **The active switch is global state — it is *not* implied by the directory.**
   Unlike npm/cargo/pip, "what is installed" is a function of the active switch,
   selected by environment variables, not of the project you are standing in.
   Before reasoning about what is installed or why a build fails, know which
   switch is active: `opam switch show` (and `opam exec -- ocaml -vnum` for the
   compiler).
2. **`command not found` / wrong-version errors are almost always the
   environment, not a missing package.** When the switch env is not loaded you
   get `command not found: dune`, a wrong library version, or an "inconsistent
   assumptions" link error — none of which name the real cause. Do not "fix" it
   by reinstalling; run the command through `opam exec --` instead.
3. **Switch-mutating commands touch user-owned state — ask first.** `install`,
   `remove`, `pin`, `upgrade`, `switch create`, `repository add/remove`, and
   `update` all change the user's switches or metadata. Inspect freely; mutate
   only with explicit authorisation.

## Switches: global vs local

- **Global switch**: lives in `~/.opam/<name>` (e.g. `5.2.0`, `default`), shared
  across every project. Good for general tooling.
- **Local switch**: lives in `<project>/_opam`, bound to a directory. Created
  with `opam switch create . <compiler>` (or `opam switch create . --deps-only`
  to also install the project's deps). It auto-selects when the cwd is inside
  the project *and* the env is loaded. Good for reproducibility and isolation.

**Rule:** the presence of an `_opam/` directory means a local switch is in play —
prefer it over any global switch for that project. Prefer local switches for
per-project isolation. Never create a switch unprompted (it downloads and
compiles a compiler — minutes of work and user state).

## Constraint solving (underpins everything below)

opam's solver finds **one** consistent set of package versions satisfying every
`depends`, `conflicts`, and `available` constraint at once. It ships multiple
backends — `mccs` (default), `aspcud`, `z3`, and `0install`/`builtin-0install` —
and `solver_preferences` / the `OPAMCRITERIA` env var bias which solution is
chosen (e.g. prefer newest vs fewest changes).

**Rules:**
- **Preview before any multi-minute action.** `opam install <pkg> --show` (or
  `--show-actions` / `--dry-run`) prints the plan without doing it. Use it before
  committing to a long solve+build.
- **"No solution" is a real conflict, not a transient error.** Retrying the same
  command will not help. Read the explanation to find the binding constraint,
  then relax a bound or add a pin (see below).
- When touching solver behaviour in the opam repo itself, remember backends
  differ — don't assume only `mccs` is exercised.

## Package conflicts and bounds

- Dependencies carry version bounds in `depends`: `>= < = & |`
  (e.g. `"dune" {>= "3.0"}`). Incompatibility is expressed with `conflicts`,
  optional deps with `depopts`, and mutual exclusion groups with
  `conflict-class`.
- A solver failure traces back to one of these. The skill of reading it is
  finding the *single* binding constraint in the wall of output.

**Rule:** bounds exist for a reason (see interface compatibility next). Widen or
remove a bound deliberately to resolve a real incompatibility — never blindly to
force a solve.

## Interface compatibility

OCaml has no stable cross-version ABI. A library is compiled against the exact
interfaces (`.cmi`, identified by hash) of its dependencies; mixing a consumer
built against one version of a dependency with a different version of that
dependency produces a link-time **"inconsistent assumptions over interface"**
error. This is *why* packages carry upper bounds and `available:` compiler
constraints.

**Rule:** a version bound that looks "too tight" is usually guarding against an
interface break. Treat removing it as a real (and likely wrong) change, not a
shortcut around the solver.

## Repos

Repositories supply package metadata. Manage them with
`opam repository list / add / remove / set-url`. The default is the community
opam-repository. Repos are **ranked** (priority order), and the selection can be
global or per-switch. Metadata is refreshed by `opam update` (see below), not
automatically.

**Rule:** the repo set is user state. `opam repository list` to inspect; add or
remove only on request.

## Pins (packages and repos)

`opam pin` makes opam use a specific source for a package, **overriding** repo
metadata. You can pin to:
- a version (`opam pin <pkg> <version>`),
- a local directory (development: opam reads the package's opam file from there),
- a git/http URL or git ref.

`opam install .` (or `opam install <dir>`) auto-pins the local project. The
`pin-depends` field in an opam file declares cross-pins needed for development.

**Rule:** pins mutate switch state and shadow repo versions, so a **stale pin** is
the classic cause of "why is the wrong version installed / why won't this
update". When versions surprise you, check `opam pin list` first.

## Dev and test dependencies

opam files mark non-default deps with filter variables:
- `{with-test}` — needed only to run the test suite,
- `{with-doc}` — needed only to build docs,
- `{with-dev-setup}` — developer tooling, not needed by consumers.

These are **not** installed for ordinary consumers. To set up a checkout for
development, install them explicitly:

```
opam install . --deps-only --with-test --with-doc
```

## Relationship with dune

opam and dune are complementary, not interchangeable:
- **opam** resolves and installs dependencies into the switch and manages the
  environment.
- **dune** is the build system. `dune build` compiles *against* what is already
  installed; it does **not** fetch dependencies.

`dune-project` can generate the package's opam files via
`(generate_opam_files true)` — when that is set, author `depends` through the
`dune-project` stanzas, not by hand-editing the generated `*.opam`. (The newer
`dune pkg` blurs this boundary by letting dune manage dependencies itself; the
classic opam-installs / dune-builds flow remains the default.)

**Rule:** a "missing module / library" error after `dune build` means a missing
*installed* dependency — install it with opam, do not hand-edit build files. And
always invoke dune through `opam exec --` so it sees the right switch.

## Updates vs upgrades (commonly confused)

- **`opam update`** refreshes repository and pin **metadata** only. It changes
  nothing that is installed. Relatively safe.
- **`opam upgrade`** re-runs the solver and **installs newer versions** of
  installed packages. It mutates the switch and can be disruptive (rebuilds,
  removed packages).

**Rule:** never conflate them. `update` then `upgrade` is the usual sequence, but
`upgrade` changes user state — ask before running it. Scope it
(`opam upgrade <pkg>`) when only one package is intended.

## What this page is not for

- General opam tutoring — only the conventions an agent needs to operate safely.
- Project-specific build/setup steps — those belong in the project's `CLAUDE.md`
  or README.
- The opam-MCP design work — that is a separate repo deliverable, not skill
  content.
