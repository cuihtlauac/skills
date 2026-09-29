## Web search

Never use grokopedia as a source.

When the Web tool and `curl`/`wget` all fail to download a page or
file (JS-rendered content, bot blocking, etc.), fall back to
`google-chrome --headless` to fetch it, e.g.:

    google-chrome --headless --disable-gpu --dump-dom <url>            # rendered HTML
    google-chrome --headless --disable-gpu --print-to-pdf=out.pdf <url>  # save as PDF

## OCaml

For build commands, conventions, and package-doc lookup, see the `ocaml` skill.
Hard rule: never use `eval $(opam env) && <cmd>` — always `opam exec -- <cmd>`.

## Changes outside the session/project root

When a change targets a folder outside the current session/project
root, first check whether that folder is a GitHub project (e.g. it has
a `.git` directory with a GitHub remote).  If it is, do not edit files
there directly — propose the change through an issue or a pull request
instead.  Direct edits are only acceptable inside the session root or
in non-GitHub directories.

## Impersonation in social interactions

Never impersonate me (Cuihtlauac) in social interactions: do not send Slack
messages, post GitHub comments, or otherwise speak as me. If I
explicitly ask you to, do not act on the first request — ask for a
second confirmation and proceed only after I give it.

## Publishing content (commits, GitHub issues, PRs)

Before writing anything that becomes part of a public or shared record
(commits, GitHub issues/PRs, gists, pastebins, non-private Slack), see
the `redact-publish` skill: redact machine-identifying details
(hostnames, IP/MAC addresses, username-bearing or layout-revealing
absolute paths). Hardware fingerprints and kernel/OS versions are
exempt.
