#!/usr/bin/env python3
"""Check that facts cited to git repositories point at real things and
that their quotes appear there.

usage: check_refs.py --sources sources.tsv [--repos-dir repos]
                     [--history-dir extracted/repos/{slug}/history] YAML...

The registry lists repositories as `<slug>\trepo\t<url>\t<pinned sha>`;
each one is cloned at <repos-dir>/<slug>. Other registry lines (PDFs and
so on) are ignored, so this checker and a document checker can share one
registry and one facts tree.

Walks every mapping in the YAML files. A mapping whose `source` names a
registered repository must use one of these forms:

  <slug>@<rev>:<path>#L<a>-<b>   lines a..b of a file at that revision
  <slug>@<rev>:<path>#L<a>       one line
  <slug>@<rev>:<path>            a whole file (or a directory, without quote)
  <slug>@<rev> msg               the commit message of <rev>
  <slug>@<rev> diff              the patch of <rev>
  <slug>@<rev>                   the commit itself (no quote)
  <slug> history:<file.csv>      a figure computed by history.py (no quote);
                                 the file must exist in --history-dir

<rev> is a commit hash (7-40 hex digits) that must exist and be the pinned
commit or one of its ancestors, so citations stay valid when the pin moves
forward. Paths and line ranges must exist at <rev>. A `quote` must occur,
after normalisation and split on ellipses, in the cited text: the line
range widened by 3 lines on each side, the whole file, the message or the
patch. Sources whose slug is not a registered repository (a PDF page, a
meeting) are counted and skipped. Exit status 1 on any bad reference or
missing quote.
"""
import argparse
import os
import re
import subprocess
import sys
from functools import lru_cache

import yaml

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from textnorm import norm, flat, split_ellipsis  # noqa: E402

ap = argparse.ArgumentParser()
ap.add_argument("--sources", required=True)
ap.add_argument("--repos-dir", default="repos")
ap.add_argument("--history-dir", default="extracted/repos/{slug}/history")
ap.add_argument("yaml", nargs="+")
a = ap.parse_args()

repos = {}  # slug -> (clone path, pinned sha)
base = os.path.dirname(a.sources) or "."
for line in open(a.sources, encoding="utf-8"):
    if not line.strip() or line.startswith("#"):
        continue
    f = line.rstrip("\n").split("\t")
    if len(f) >= 4 and f[1] == "repo":
        repos[f[0]] = (os.path.join(base, a.repos_dir, f[0]), f[3].strip())

for slug, (path, pin) in repos.items():
    if not os.path.isdir(path):
        sys.exit(f"{slug}: no clone at {path}")


def git(slug, *args, check=True):
    r = subprocess.run(["git", "-C", repos[slug][0], *args],
                       capture_output=True, text=True, errors="replace")
    if check and r.returncode != 0:
        return None
    return r.stdout


@lru_cache(None)
def rev_ok(slug, rev):
    full = git(slug, "rev-parse", "--verify", "--quiet", rev + "^{commit}")
    if not full:
        return "unknown revision"
    pin = repos[slug][1]
    r = subprocess.run(["git", "-C", repos[slug][0], "merge-base", "--is-ancestor",
                        full.strip(), pin], capture_output=True)
    return None if r.returncode == 0 else f"not the pinned commit {pin[:12]} or an ancestor"


@lru_cache(None)
def blob(slug, rev, path):
    kind = git(slug, "cat-file", "-t", f"{rev}:{path}")
    if kind is None:
        return None
    if kind.strip() == "tree":
        return ""
    return git(slug, "show", f"{rev}:{path}")


@lru_cache(None)
def message(slug, rev):
    return git(slug, "log", "-1", "--format=%B", rev) or ""


@lru_cache(None)
def patch(slug, rev):
    return git(slug, "show", "--format=", "--no-color", rev) or ""


SRC = re.compile(r"^\s*([\w.-]+)@([0-9a-fA-F]{7,40})"
                 r"(?::(\S+?)(?:#L(\d+)(?:-L?(\d+))?)?)?"
                 r"(?:\s+(msg|diff))?\s*$")
HIST = re.compile(r"^\s*([\w.-]+)\s+history:(\S+\.csv)\s*$")
stats = dict(facts=0, other_sources=0, quotes=0, bad_ref=0, quote_missing=0)
problems = []


def found(q, text):
    hay = norm(text)
    hay_flat = re.sub(r"[\W_]", "", hay)
    pieces = [p for p in split_ellipsis(norm(q).strip('"').rstrip(".… ")) if len(p) > 3]
    return all(p in hay or flat(p) in hay_flat for p in pieces)


def check(node, where):
    stats["facts"] += 1
    src = str(node.get("source", ""))
    slug = re.match(r"\s*([\w.-]+)", src)
    if not slug or slug.group(1) not in repos:
        stats["other_sources"] += 1
        return
    h = HIST.match(src)
    if h:
        f = os.path.join(base, a.history_dir.format(slug=h.group(1)), h.group(2))
        if not os.path.isfile(f):
            stats["bad_ref"] += 1
            problems.append(f"{where}: {src!r}: no file {f}")
        return
    m = SRC.match(src)
    if not m:
        stats["bad_ref"] += 1
        problems.append(f"{where}: unreadable repository citation {src!r}")
        return
    slug, rev, path, lo, hi, part = m.groups()
    err = rev_ok(slug, rev)
    if err:
        stats["bad_ref"] += 1
        problems.append(f"{where}: {src!r}: {err}")
        return
    q = node.get("quote")
    if path:
        text = blob(slug, rev, path)
        if text is None:
            stats["bad_ref"] += 1
            problems.append(f"{where}: {src!r}: no such path at {rev}")
            return
        if lo:
            lines = text.split("\n")
            lo, hi = int(lo), int(hi or lo)
            if not (1 <= lo <= hi <= len(lines)):
                stats["bad_ref"] += 1
                problems.append(f"{where}: {src!r}: lines out of range (file has {len(lines)})")
                return
            text = "\n".join(lines[max(0, lo - 4):hi + 3])
    elif part == "msg":
        text = message(slug, rev)
    elif part == "diff":
        text = patch(slug, rev)
    else:
        text = None
    if not isinstance(q, str) or not q.strip():
        return
    stats["quotes"] += 1
    if text is None or not found(q, text):
        stats["quote_missing"] += 1
        problems.append(f"{where}: quote not found in {src}: {q[:90]!r}")


def walk(node, where):
    if isinstance(node, dict):
        if "source" in node or "quote" in node:
            check(node, where)
        for k, v in node.items():
            walk(v, f"{where}.{k}")
    elif isinstance(node, list):
        for i, v in enumerate(node):
            walk(v, f"{where}[{i}]")


for f in a.yaml:
    with open(f, encoding="utf-8") as fh:
        for doc in yaml.safe_load_all(fh):
            walk(doc, f)
print(" ".join(f"{k}={v}" for k, v in stats.items()))
for p in problems:
    print(" -", p)
sys.exit(1 if stats["bad_ref"] or stats["quote_missing"] else 0)
