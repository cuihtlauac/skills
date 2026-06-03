# skills

My Claude Code global config and skills. Snapshot of how I run Claude
Code day-to-day — opinionated for OCaml work and empirical/lab-notebook
projects.

## What's in here

- `CLAUDE.md` — global instructions loaded for every project I open.
  Web-search rules, OCaml build conventions (`opam exec --`), and a
  redaction rule for any text destined for a public record (commits,
  PRs, issues, Slack to non-private channels).
- `skills/lab-notebook/` — discipline for projects that keep an
  append-only `lab/results/` notebook of experimental runs. Enforces
  "results files are never overwritten", "sweep drivers print, don't
  persist", "the human decides what to record".
- `skills/session-backlog/` — pattern for organizing work across
  Claude Code sessions via `backlog.md` (pending) and `changelog.md`
  (done). Three phases: start, mid-session, wrap.

## Layout

The repo is intended to be cloned directly as `~/.claude` (or copied
into an existing one). The published tree contains only the shareable
parts; the rest of `~/.claude` (sessions, caches, history) is excluded
by an allowlist `.gitignore`.

```
.
├── CLAUDE.md
├── README.md
├── LICENSE
└── skills/
    ├── lab-notebook/SKILL.md
    └── session-backlog/SKILL.md
```

## Install

If you do not yet have `~/.claude`:

```
git clone git@github.com:cuihtlauac/skills.git ~/.claude
```

If `~/.claude` already exists, clone elsewhere and copy what you want:

```
git clone git@github.com:cuihtlauac/skills.git /tmp/skills
cp /tmp/skills/CLAUDE.md ~/.claude/
cp -r /tmp/skills/skills ~/.claude/
```

## License

[CC0 1.0 Universal](LICENSE) — public domain dedication. Copy, adapt,
remix without attribution.
