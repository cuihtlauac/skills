---
name: session-backlog
description: Run a project that organizes work across sessions via a `backlog.md` of pending items and a `changelog.md` of completed ones. Invoke at the start of a working session to orient (read both files, identify the current task), throughout the session to enforce single-task focus (append unrelated ideas to the backlog, don't pursue them), and at session wrap-up to verify the build, move the finished item from backlog to the top of changelog, and commit. Also use when the user mentions "backlog", "changelog", "starting a session", "wrapping up", "before context clear", or asks how to organize work across context resets.
---

# Session-backlog workflow

A working discipline for projects that use a `backlog.md` (ordered pending work, current task first) and a `changelog.md` (completed work, most recent at top) at the repository root. The pattern exists because Claude Code conversations have finite context: long sessions either get summarized or hit a hard limit. Treating each session as a single focused unit, with the next task already chosen and the previous one recorded, lets work continue cleanly across context resets without losing track of what's done and what's next.

You do not need both files to exist already; if either is missing the user is starting the convention from scratch and you can create them.

## Phases

A session has three phases. The user may invoke this skill at any of them — read what they're asking for and jump to the right phase.

### Phase 1: Start (orient)

When the user opens a session and wants to know what to work on, or asks you to "start" / "begin" / "orient" / "what's next", do this:

1. Read `backlog.md` and `changelog.md` from the repository root.
2. Report the current task — the first item in `backlog.md`. Read its body, not just its header: backlog headers are often too terse to convey what the work is (e.g. "Refactor choice path as explicit zipper" says nothing about *which* path or *why*). Summarise in one sentence using the first paragraph of the body for context.
3. Report what was last shipped — the top entry in `changelog.md`, one sentence, same approach.
4. If `backlog.md` is empty, ask the user what to work on. Do not pick a task from elsewhere on your own.

**Then stop and wait.** Do not begin the task yet. Phase 1 is for orientation: the user may have invoked the skill just to see where things stand, or to confirm the next task before committing to a working session. Begin work only after the user explicitly confirms ("yes, let's do that" / "go ahead" / "start"). Once they confirm, do not start any work that isn't the first backlog item.

### Phase 2: Mid-session (focus)

Throughout the session, enforce these rules:

- **One backlog item per session.** Do not start a second item, even if the first finishes quickly. A fresh task wants a fresh session with cleanly-seeded context.
- **Capture, don't pursue.** If unrelated ideas come up — bug reports, refactoring opportunities, new features — append them to the **end** of `backlog.md` and keep going on the current task. Do not chase them mid-session.
- **No reordering without the user.** The current task is the first backlog item. If the user wants to swap priorities, they will say so.

### Phase 3: Wrap (close out cleanly)

When the user signals the session is done — "wrap up", "before context clear", "I'm clearing context", "let's end this" — run this checklist before any commit:

1. **Build and test.** Run the project's standard build and full test suite. They must pass. If they don't, the task is not done; do not move it from the backlog.
2. **Sanity-check staleness.** If the work renamed modules, added/removed examples, or changed counts cited in docs, search for stale references and fix them. The repository's `CLAUDE.md` often lists which docs and counts to keep in sync — read it.
3. **Move the item.** Remove the completed entry from `backlog.md` and add it to the **top** of `changelog.md`. Date the changelog entry if dating is the project's convention; otherwise match the existing style.
4. **Commit.** Use a focused commit message that names what changed and why. Only commit if the user has asked you to, per general Claude Code defaults.

If the user only asked for a status update and not a wrap, stop after step 1 and report; do not move items or commit without confirmation.

## What this skill is **not** for

- One-off tasks the user wants done immediately without ceremony — they aren't running a session.
- Projects that don't have (and don't want) a backlog/changelog discipline.
- Tracking work *within* a session — use the task tool for that, not the backlog.

## Notes on the rules

- The reason for "one item per session" is that a context-summarized or context-cleared agent picks up much more reliably when the next task has been pre-thought and written down than when it has to reconstruct intent from a partial transcript.
- The reason for append-only idea capture is the same: switching tasks mid-session is the most reliable way to leave both half-done.
- The reason the changelog goes most-recent-at-top is so the user can read the latest few entries without scrolling — it functions as a short-term memory aid for what just shipped.
