---
name: redact-publish
description: Use before writing anything that becomes part of a public or shared record — git commits (messages and staged file contents), GitHub issue/PR titles, bodies, and comments, and any other text bound for an external or shared system (gists, pastebins, non-private Slack messages). Enforces the rule that content identifying a specific machine the user owns or uses must be redacted or omitted: hostnames, IP and MAC addresses, and absolute filesystem paths that include a username or leak the local directory layout. Also governs the exception: hardware fingerprints (CPU model, RAM) and kernel/OS versions are fine, since they belong in lab-notebook provenance.
---

# Redact machine-identifying content before publishing

Never publish content that identifies a specific machine the user owns or uses.
This applies to anything that becomes part of a public or shared record. Redact
before the content leaves the local session, not after.

## When this applies

Any text destined for an external or shared record:

- **Git commits** — commit messages *and* the contents of staged files.
- **GitHub issues** — titles, bodies, and comments.
- **GitHub pull requests** — titles, bodies, and review comments.
- **Any other external/shared system** — gists, pastebins, Slack messages to
  non-private channels, and similar.

If in doubt about whether a destination counts as "shared," treat it as shared
and redact.

## What to redact or omit

- **Hostnames.**
- **IP addresses and MAC addresses.**
- **Absolute filesystem paths that include a username** (e.g. `/home/<user>/…`)
  or that otherwise leak the local directory layout.

Replace with a neutral placeholder rather than deleting silently, so the text
still reads:

| Leaks | Replace with |
|-------|--------------|
| hostname | `<host>` |
| IP / MAC address | `<ip>` |
| `/home/alice/project/src/x.ml` | `/path/to/…` (or a repo-relative path like `src/x.ml`) |

## Tool output is a common source

Logs, pastes, and error traces frequently embed hostnames, IPs, and absolute
paths. When you lift such output into a commit message, issue, PR, or other
shared text, redact it first — do not paste it verbatim.

## When the identifier is integral

If the machine-identifying detail genuinely cannot be removed without breaking
the work — for example a script that legitimately needs an absolute path — do
**not** guess a substitute. Pause and ask the user before staging or posting.

## Explicit exception: provenance details are fine

Hardware fingerprints (CPU model, RAM size) and kernel/OS versions are **not**
covered by this rule. They are routinely recorded in lab notebook provenance for
reproducibility, so leave them in. See the `lab-notebook` skill for where such
provenance belongs.

## Quick checklist before publishing

1. Scan the text (and any staged diff) for hostnames, IPs/MACs, and
   username-bearing or layout-revealing absolute paths.
2. Replace each with `<host>` / `<ip>` / `/path/to/…` or a repo-relative path.
3. If an identifier is load-bearing and can't be redacted, stop and ask.
4. Leave hardware and kernel/OS version details as-is.
