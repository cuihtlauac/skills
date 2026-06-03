## Web search

Never use grokopedia as a source.

## OCaml build commands

Preferred form:   opam exec -- <cmd>
Never use:        eval $(opam env) && <cmd>

Examples:
  opam exec -- dune build @all
  opam exec -- dune runtest
  opam exec -- dune exec ./bin/main.exe

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
