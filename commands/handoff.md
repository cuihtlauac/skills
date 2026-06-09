---
description: Wrap up the current session before clearing context — verify the build, move the finished item from backlog.md to changelog.md, and commit.
---

Run **Phase 3 (Wrap)** of the `session-backlog` skill — this is the pre-`/clear` handoff that packages the session so the next one can pick it up cleanly.

Follow the skill's Phase 3 checklist exactly:

1. Build and test — the full suite must pass. If it doesn't, the task is not done; report and stop, do not move the item.
2. Sanity-check staleness (renamed modules, changed counts/examples cited in docs; consult the repo's `CLAUDE.md`).
3. Move the completed entry from `backlog.md` to the **top** of `changelog.md`, matching the project's dating/style convention.
4. Commit with a focused message naming what changed and why.

If the build or tests fail, stop after step 1 and report — do not move items or commit. Only commit once the work is verified.

When the handoff is complete, tell me it's safe to `/clear`.
