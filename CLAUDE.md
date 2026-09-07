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

## Publishing content (commits, GitHub issues, PRs)

Never publish content that identifies a specific machine the user
owns or uses.  This applies to anything that becomes part of a public
or shared record, including:

- Git commits (messages and staged file contents).
- GitHub issue titles, bodies, and comments.
- GitHub pull request titles, bodies, and review comments.
- Any other text destined for an external/shared system (gists,
  pastebins, Slack messages to non-private channels, etc.).

In all such content, redact or omit:

- Hostnames.
- IP addresses and MAC addresses.
- Absolute filesystem paths that include a username (e.g.
  `/home/cuihtlauac/...`) or that leak the local directory layout.

If a tool output (log, paste, error trace) contains such information,
redact before publishing — replace with `<host>`, `<ip>`,
`/path/to/...`, or similar.  If the content is integral to the work
(e.g. a script that genuinely needs an absolute path), pause and ask
before staging or posting.

Hardware fingerprints (CPU model, RAM size) and kernel/OS versions
are not covered by this rule — they are routinely recorded in lab
notebook provenance for reproducibility.
