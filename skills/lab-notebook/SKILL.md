---
name: lab-notebook
description: Record results from benchmarks, parametric sweeps, or other empirical experiments into an append-only lab notebook (typically `lab/results/` plus a `lab/notebook.md` index). Use when the user has run a sweep or experiment driver and wants to capture the findings, when they ask to "record this run", "log a result", "add to the notebook", or when they discuss whether a particular run is worth keeping. Enforces the rules that results files are never overwritten, that redundant deterministic re-runs are discarded rather than logged (while replications of stochastic experiments are kept as data), and that the human — not the model — decides what is worth recording.
---

# Lab notebook discipline

A working discipline for projects that maintain an append-only record of experimental runs — benchmarks, parametric sweeps, comparisons, ablations — under a conventional layout:

```
lab/
├── notebook.md           # index — one line per recorded experiment, with link
├── results/              # one file per experiment, append-only
│   ├── 2026-04-13-exp-004-cache-stride.md
│   ├── 2026-04-15-exp-005-...
│   └── ...
├── run_<sweep>.ml        # sweep drivers — print to stdout, persist nothing
└── ...
```

The pattern exists because empirical work generates a lot of noise — half the runs are redundant, exploratory, or just sanity checks. Persisting every one would drown out the few results that actually changed your understanding of the system. The notebook is a curated scientific record, not a log of every invocation.

## The rules

These are non-negotiable. Violating them silently corrupts the record.

### 1. Results files are append-only

Once a file in `lab/results/` exists, never overwrite it. A lab notebook is a log: re-running an experiment and replacing the file would erase the original observation. If a finding changes, write a *new* file that supersedes the old one, and link to the old one from the new one's preamble.

This includes "small fixes" — typo corrections in prose are fine, but raw data, parameters, and conclusions are frozen at the moment of recording.

### 2. Sweep drivers print, they do not persist

The sweep/benchmark drivers (e.g. `lab/run_pipeline.ml`, `lab/run_cache_sweep.ml`) print to stdout only. They never write into `lab/results/`. Persistence is a human decision, not an automatic side effect of running a sweep.

When the user runs a sweep, your job is to **show them the output**, not to file it. Wait for them to say "record this" before creating a results file.

### 3. The human decides what to record

Not every run is worth recording. A re-run that produces results consistent with an existing recorded experiment is **irrelevant** — its output is discarded. Only record runs that:

- establish a new baseline,
- reveal a surprise or contradict a prior finding,
- close out an open question in the backlog,
- or were explicitly requested as part of an experiment plan.

If the user asks you to "save this" but the output looks like a confirmation of an existing entry, gently flag this before writing — they may have forgotten the prior result, or they may genuinely want the second data point. Either is fine; the point is to be honest about what the file represents.

**Exception — stochastic experiments.** The "discard confirming re-runs" rule above assumes a *deterministic* measurement: a benchmark whose number is fixed given the inputs, where a second identical run is genuinely redundant. When the outcome is **sampled** — LLM completions, Monte-Carlo runs, anything with run-to-run variance — repeated runs are not redundant; they *are* the data. Replication is what quantifies variance and establishes that an effect is real rather than a lucky draw. For these experiments:

- Record repeated runs (or additional seeds/batches) as further data points rather than discarding them; a "confirmation" here is signal worth keeping, not noise.
- Report the outcome as a **distribution with an interval** (confidence interval, error bars, or a spread across seeds), never a single value, and record the **sample size** and **seed(s)**.
- Treat a result that *fails* to replicate as one of the most important things to record, not a run to quietly drop.

When in doubt about whether a measurement is deterministic, ask — the decision changes whether a re-run is clutter or data.

### 4. `notebook.md` is an index, not a memory

`lab/notebook.md` contains one line per recorded experiment — a date, a one-line description, and a link to the corresponding `results/` file. It is *not* where analysis lives. All raw data, parameters, plots, and prose belong in the per-experiment file. When you add a recorded experiment, you add one row to the index and one new file to `results/`.

## When the user asks to record a result

Follow this procedure:

1. **Confirm it's worth recording.** Quickly check `lab/notebook.md` for a similar prior entry. If one exists, mention it and ask whether this run is a new finding or a confirmation. If a confirmation, propose to discard rather than file — unless the user wants the data point preserved.

2. **Choose a filename.** Always look at filenames already in `lab/results/` first and match their shape exactly — separator (hyphen vs. underscore), where the experiment ID lives (in the filename or only inside the file's H1 title), date format. Conventions vary: `2026-04-13-exp-004-cache-stride.md`, `2026-04-13_cache_calibrated.md`, and `exp004-cache.md` are all in use across projects. Don't invent a shape if one already exists.

3. **Structure the file.** A useful results file answers five questions, roughly in this order:
   - **What** — one-paragraph summary of the experiment.
   - **Why** — motivation. What question did this run answer, what prior experiment does it build on, what was at stake? This is the most load-bearing section: a year from now, raw numbers without motivation are unreadable.
   - **Provenance** — git commit, machine, kernel, toolchain (compiler + exact version + optimisation mode — e.g. OCaml 5.2.1 stock vs flambda, the C/C++ compiler, key build flags), who ran it, exact command line, duration, exit status. Anything needed to reproduce — for performance experiments the compiler and its optimisation mode are first-order determinants of the numbers, so never omit them.
   - **Parameters and raw data** — every input that varied (config values, seeds, sweep ranges) and the resulting numbers. Tables or blocks the user can re-parse. Don't summarise away the data. (Some projects collapse parameters into provenance; that's fine.)
   - **Analysis and open questions** — what the data means, what was surprising, what changed in your understanding, and what this run could not settle (optionally with a pointer to the backlog item that will follow up). Be honest about uncertainty.

   If the project has a prior file to imitate, follow its shape — the sections, headings, and ordering used there override this generic template.

4. **Update the index.** Add a single entry to `lab/notebook.md` that matches the existing index format — it may be a bullet, a markdown table row (`| date | experiment | tool | finding | link |`), or something else. Read the file first to see what shape entries take. One entry, link to the new results file, no inline contents.

5. **Do not commit silently.** Show the file and the index update; let the user decide when to commit.

## What this skill is **not** for

- Drafting hypotheses or designing experiments — that belongs in the backlog or a planning conversation.
- Persisting *every* run automatically — see rule 2.
- Replacing or "cleaning up" old entries — see rule 1.
- Producing summary documents that synthesize across experiments. The notebook is raw record; summaries belong elsewhere (a docs page, a paper draft, a report).

## Notes on the rules

- The reason results are append-only is that empirical work routinely uncovers earlier mistakes. The value of an append-only log is precisely that you can see what you used to believe, when, and why you changed your mind. Overwriting destroys that.
- The reason sweep drivers don't persist is that most sweep invocations are exploratory — you're checking that something parses, that a parameter range is reasonable, that the harness works. Auto-persisting all of those would clog the record. Persistence is a deliberate act.
- The reason the human chooses is that the model often cannot tell, from output alone, whether a run is a confirmation or a new finding — that judgment depends on context the user holds.
