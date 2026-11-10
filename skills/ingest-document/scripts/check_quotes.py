#!/usr/bin/env python3
"""Check that cited facts point at real pages and quotes appear there.

usage: check_quotes.py --sources sources.tsv [--text-dir extracted/text] YAML...

Walks every mapping in the YAML files. A mapping with `source: "<slug> p.N"`
(or `p.N-M`) must cite an existing page of a registered PDF; if it also has
a `quote`, every piece of the quote (split on ellipses, pieces > 3 chars)
must occur, after normalisation, on pages N-1..M+1 of the `-layout` text in
TEXT-DIR or of `pdftotext -raw`. `quote_from_image: true` skips the quote.
Sources whose slug is not registered (e.g. "meeting 2026-01-05") are
counted and skipped. Exit status 1 on any bad page or missing quote.
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
ap.add_argument("--text-dir", default="extracted/text")
ap.add_argument("yaml", nargs="+")
a = ap.parse_args()

pdfs = {}
for line in open(a.sources, encoding="utf-8"):
    if not line.strip() or line.startswith("#"):
        continue
    slug, _kind, file = line.rstrip("\n").split("\t")[:3]
    if file.lower().endswith(".pdf"):
        pdfs[slug] = os.path.join(os.path.dirname(a.sources) or ".", file)


@lru_cache(None)
def layout_pages(slug):
    p = os.path.join(a.text_dir, slug + ".txt")
    pages = open(p, encoding="utf-8").read().split("\f")
    if pages and not pages[-1].strip():
        pages = pages[:-1]
    return [norm(x) for x in pages]


@lru_cache(None)
def raw_page(slug, n):
    out = subprocess.run(["pdftotext", "-raw", "-f", str(n), "-l", str(n), pdfs[slug], "-"],
                         capture_output=True, text=True).stdout
    return norm(out)


SRC = re.compile(r"^\s*([\w.-]+)\s+p+\.\s*(\d+)(?:\s*[-–]\s*(\d+))?")
stats = dict(facts=0, unregistered=0, quotes=0, from_image=0, bad_page=0, quote_missing=0)
problems = []


def check(node, where):
    stats["facts"] += 1
    m = SRC.match(str(node.get("source", "")))
    if not m or m.group(1) not in pdfs:
        stats["unregistered"] += 1
        return
    slug, lo, hi = m.group(1), int(m.group(2)), int(m.group(3) or m.group(2))
    pages = layout_pages(slug)
    if not (1 <= lo <= hi <= len(pages)):
        stats["bad_page"] += 1
        problems.append(f"{where}: page out of range {node['source']!r}")
        return
    if node.get("quote_from_image"):
        stats["from_image"] += 1
        return
    q = node.get("quote")
    if not isinstance(q, str) or not q.strip():
        return
    stats["quotes"] += 1
    nq = norm(q).strip('"').rstrip(".… ")
    lo, hi = max(1, lo - 1), min(len(pages), hi + 1)
    hay = " ".join(pages[lo - 1:hi] + [raw_page(slug, n) for n in range(lo, hi + 1)])
    hay_flat = re.sub(r"[\W_]", "", hay)
    pieces = [p for p in split_ellipsis(nq) if len(p) > 3]
    if not all(p in hay or flat(p) in hay_flat for p in pieces):
        stats["quote_missing"] += 1
        problems.append(f"{where}: quote not found in {node['source']}: {q[:90]!r}")


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
sys.exit(1 if stats["bad_page"] or stats["quote_missing"] else 0)
