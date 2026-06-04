---
description: List the backlog items from ./backlog.md (or ./BACKLOG.md), one per line, numbered.
---

Find the backlog file at the repository root — either `backlog.md` (lowercase) or `BACKLOG.md` (all-caps), whichever exists. Then print every backlog item on its own line, numbered starting at 1, in the order they appear.

- Items are the top-level entries in the backlog file. In most projects these are Markdown headings (`# `, `## `, or `### ` — whichever level the file uses for items); occasionally they are `-` / `*` bullets. Pick the level that yields the project's actual item list, not sub-sections under one item.
- Use the heading or bullet text verbatim as the label. Strip the leading marker (`## `, `- `, etc.) but keep the rest as-is.
- Output only the numbered list. No preamble, no trailing summary, no commentary. If neither `backlog.md` nor `BACKLOG.md` exists, say so in one line. If the file exists but has no items, say so in one line.
