---
name: ocaml
description: Use when running, building, or testing OCaml code, or invoking any opam/dune command. Enforces the rule that `opam exec -- <cmd>` is the only acceptable way to enter the opam environment — `eval $(opam env) && <cmd>` is forbidden because it mutates the surrounding shell. Also the home for OCaml conventions as they accrete (build, test, formatting, package and module documentation lookup) and for opam know-how — switches (global vs local), pins, repos, dependency bounds and conflicts, constraint solving, dev/test deps, the dune relationship, and update vs upgrade (see opam.md).
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

## Working with opam

opam's state model is the thing agents get wrong, because it differs from
npm/cargo/pip. Keep three rules in mind:

1. **The active switch is global state — not implied by the directory.** "What
   is installed" depends on the active switch (selected by env vars), not on the
   project you are in. Check it with `opam switch show` before reasoning about a
   build. An `_opam/` directory in the project means a local switch is in play.
2. **`command not found` / wrong-version errors are usually the environment, not
   a missing package** — run the command through `opam exec --` rather than
   reinstalling.
3. **Switch-mutating commands (`install`, `pin`, `upgrade`, `switch create`,
   `repository add`, `update`) touch user-owned state — ask first.** Inspecting
   is always fine.

For the full operational reference — global vs local switches, constraint
solving, conflicts and version bounds, interface compatibility, repos, pins, dev
and test dependencies, the dune relationship, and the update-vs-upgrade
distinction — see [`opam.md`](opam.md) in this skill directory.

## FFI performance: do not port the Python kernel pattern

When binding OCaml to a native library, the dominant way Python reaches native
speed is an **anti-pattern in OCaml**. Recognise it and refuse it.

The Python pattern: make the high-level language fast by shipping a **closed
catalogue of precompiled C kernels selected from the high-level side** — NumPy
ufuncs, pandas `agg`, torch ops. A Python-level loop or lambda stays at
interpreter speed; you reach C speed only by routing through the kernel
catalogue. "Vectorise it" *means* "use the kernels."

Why it is idiomatic in Python but wrong in OCaml:

- Python needs it because the **CPython interpreter loop is slow**, so any hot
  loop *must* escape to C. OCaml is natively compiled and already close to C;
  the only residual cost over an FFI is the **boundary itself** (per-element
  `caml_callback` + marshalling / tag-untag), **not** the loop. The correct fix
  is to eliminate the *boundary crossing*, not to reimplement the *loop* in C.
- A closed per-operation C kernel is **not user-extensible**: it makes the
  *library* fast at a fixed operation set while leaving *user* code (any novel
  computation) at callback speed. The user must edit and rebuild the binding in
  C to go fast — the opposite of what an OCaml binding is for.
- In a benchmark it is **circular**: a hand-written C kernel reaching C speed
  measures C, not the binding. (A real failure: per-query C kernels reintroduced
  under the name "fused stubs" and timed as the result.)

The OCaml way instead:

- Expose `[@@noalloc]` scalar accessors and let the user write their computation
  with ordinary `fold`/`iter`/`map` combinators — *their* OCaml, compiled to
  native, is the fast path.
- Close the residual boundary cost with **compiler/inlining** techniques: gated
  FFI-boundary fusion, flambda2, OxCaml unboxed externals — i.e. make the user's
  own code compile better, not ship a kernel catalogue. Gated FFI-boundary
  fusion is the **`ffi-inline` skill**: a *client-side* post-processing phase
  that emits gated, tested portable assembly (LLVM IR) at the call site — it
  tweaks the client's own assembly and **never** bakes a kernel into the API.
  Its shipped artifact is always the gated object, never a hand-written native
  kernel (that substitution is this same anti-pattern; `ffi-inline` declines
  such sites).
- If a closed-kernel number is ever shown, it is a separate, clearly-labelled
  *ceiling*, never the user-facing figure.

Heuristic: if a proposed "fast path" is *a C reimplementation of a specific
operation, selected from OCaml*, it is this anti-pattern — regardless of what it
is called. The pull toward it is strong because it is the most-attested "fast
high-level language" idiom in training data; that does not make it right for
OCaml.

## `Obj.magic`: if you think you need it, you're probably wrong

`Obj.magic` (and the rest of `Obj`) bypasses the type system: it can silently
produce the wrong runtime representation, and the failure surfaces far away as a
segfault or corrupted read, not a type error. Treat reaching for it as a signal
that the design is off, not as a tool in the normal kit.

- **Default to "no".** Before writing `Obj.magic`, find the typed construct that
  does the job. The standard library almost always already has it. The rule of
  thumb from the OCaml community: every `Obj.magic` needs a *theorem* that it is
  safe — if you cannot state that theorem precisely, you do not get to write it.
- **Do not describe `Obj.magic` as "common" or "idiomatic."** It is the opposite:
  a documented anti-pattern. If you catch yourself justifying one that way, stop
  and verify against the stdlib source — it will show you the typed alternative.
- **The classic trap — seeding an array with a dummy.** `Array.make n (Obj.magic
  0)` to build a polymorphic array "you'll fill in later" is *wrong*, not merely
  ugly: `Array.make` fixes the array's runtime layout from its seed, so an
  immediate `0` forces the generic boxed layout even when the element type is
  `float`, yielding a `float array` with tag `0` instead of `Double_array_tag`
  (254). Reads corrupt once it is consumed monomorphically (and flambda can trip
  on the discrepancy). The stdlib never does this — `Array.init`, `Array.of_list`,
  and `Array.fold_left_map` all seed `create`/`make` with the **first real
  element** (`create l (f 0)`, `create len hd`). Do the same: compute the first
  element and seed with it, or use `Array.init`.
- **The handful of legitimate uses are low-level and proven.** The stdlib's only
  `Obj.magic`+array uses live in `camlinternalOO.ml` (object-system runtime
  plumbing with a carefully-reasoned invariant). That is the bar: internal,
  performance-critical, and accompanied by a real correctness argument — not
  "the types are getting in my way."

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
