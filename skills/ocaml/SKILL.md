---
name: ocaml
description: Use when running, building, or testing OCaml code, or invoking any opam/dune command. Enforces the rule that `opam exec -- <cmd>` is the only acceptable way to enter the opam environment — `eval $(opam env) && <cmd>` is forbidden because it mutates the surrounding shell. Also the home for OCaml conventions as they accrete (build, test, formatting, package and module documentation lookup).
---

# OCaml conventions

A working discipline for OCaml projects under this user's account. Build rules first; further conventions accumulate here as patterns emerge.

## Build, test, and run

Use `opam exec --` to run any command that needs the opam environment. Never use `eval $(opam env)`.

```
opam exec -- dune build @all
opam exec -- dune runtest
opam exec -- dune exec ./bin/main.exe
opam exec -- dune fmt
opam exec -- dune build @runtest --watch
```

The same form applies to any tool installed via opam (`utop`, `ocamlformat`, `merlin`, `odoc`, etc.) — wrap it with `opam exec --`.

### Why `opam exec --` and not `eval $(opam env)`

- `opam exec -- <cmd>` runs a single command in the opam environment and exits. Nothing leaks.
- `eval $(opam env) && <cmd>` mutates the calling shell's environment (`PATH`, `OCAML_TOPLEVEL_PATH`, `OPAM_SWITCH_PREFIX`, …). For Claude Code that shell is shared across tool calls in a session, so subsequent unrelated commands inherit a switch the user never asked for. The mutation is invisible in the transcript — it looks like everything is fine until something silently picks up the wrong compiler.
- The two are equivalent in effect for the one command you want to run; the difference is purely about scope.

If you genuinely need several commands in the same environment (e.g. a sequence in one bash invocation), still prefer `opam exec -- bash -c '<cmd1> && <cmd2>'` over `eval`.

## Looking up package and module docs

The `mcp__ocaml-docs__*` MCP tools are the preferred way to resolve OCaml documentation questions, in this order of usefulness:

- `ocaml_package_search` — find an opam package by keyword.
- `ocaml_package_meta` / `ocaml_package_versions` — package metadata, available versions.
- `ocaml_module_list` / `ocaml_module_doc` — list modules in a package and read their signatures.
- `ocaml_package_doc` — the package-level documentation page.
- `ocaml_deps_*` — inspect the local switch's installed packages, pins, repos, and vendored sources.
- `ocaml_search` — full-text search across the indexed corpus.

Prefer these over web searches for standard-library and opam-package questions: they return signatures and docstrings the same way `merlin`/`odoc` would, without the freshness and accuracy issues of a generic web result.

## What this skill is **not** for

- General OCaml tutoring or language-level explanations — those don't depend on this user's conventions.
- Project-specific build instructions — those belong in the project's own `CLAUDE.md` or README.
- Running `opam install`/`opam pin` against the user's switches without explicit authorisation — switches are user-owned state; ask first.

## Notes on the rules

- The reason `eval $(opam env)` is banned is not stylistic. In a long Claude Code session the mutation persists across tool calls and is invisible in subsequent transcripts, so a wrong compiler or missing package can be diagnosed only by re-reading the shell history. `opam exec --` makes the scope obvious at the point of use.
- This skill is intended to grow. As OCaml-specific conventions surface in the user's projects (formatting rules, preferred test runners, dune file layout, release workflows), add sections here rather than expanding the global `CLAUDE.md`.
