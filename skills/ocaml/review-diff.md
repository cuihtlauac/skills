# Reviewing OCaml changes in VS Code with type information

Goal: a side-by-side diff of two versions of an OCaml file where hovering shows
types (and go-to-definition works) on **both** sides.

## Why the obvious views don't work

The OCaml extension only serves language features for files **on disk**. VS Code
diffs of commits — from *Source Control › Graph*, *Timeline*, or a pull request
— read both sides from git, so neither side gets tooltips. The *Changes* view
(unstaged working-tree changes) only puts the real file on the right; the left
side is still a git copy.

Comparing two real files does work, so check the base revision out into a second
directory with `git worktree` and diff the files directly.

## Setup

From the main checkout, with `<base>` the commit to compare against (e.g. the
PR author's commit, or the parent of yours):

```sh
git worktree add --detach ../<proj>-<base> <base>
cd ../<proj>-<base>
opam exec --switch=<main checkout> -- dune build @install
cd -
code --diff ../<proj>-<base>/<path/to/file.ml> <path/to/file.ml>
```

- Build the second checkout, or its side gets no types: the language server
  needs the `.cmt` files under `_build`. `@install` (or the project's own
  `--only-packages …` target) is enough; examples and tests aren't needed.
- `--switch=<main checkout>` matters when the main checkout uses a **local
  switch** (`_opam/`): the worktree has none, so plain `opam exec` there would
  pick the global switch.
- The left file lives outside the VS Code workspace; that's fine, the language
  server still finds its `dune-project` and `_build`.
- Repeat `code --diff` for each file worth reading.

## Cleanup

```sh
git worktree remove ../<proj>-<base>
```

This also deletes the worktree's `_build`. Your branch and commits are never
touched by any of the above.

## Prerequisites

- `ocaml-lsp-server` installed in the switch (`opam exec -- ocamllsp
  --version`). Installing it is a switch mutation: ask first.
- A current VS Code and OCaml Platform extension. VS Code 1.109.4 with extension
  2.0.1 showed no tooltips in any diff view; 1.145.2 with 2.4.0 works. If VS
  Code was installed from Microsoft's `.deb`, check that
  `/etc/apt/sources.list.d/` still has its repository, or `apt upgrade` silently
  stops updating it.
- The "Unable to find 'ocamlformat-rpc' binary" notice is harmless: hover types
  are just not pretty-printed.

## Quick alternative: the unstage trick

For a fast look at your own last commit without a second checkout:

```sh
git reset HEAD~1        # commit's changes become unstaged
# review in Source Control › Changes (right side has types)
git reset <sha>         # restore the commit exactly
```

Only the right side gets types, and do nothing else in git before restoring.
Use plain `git reset`, not `--soft`: with staged changes VS Code shows the git
copy on the right, which gets no tooltips either.
