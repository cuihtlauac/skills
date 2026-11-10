#!/usr/bin/env python3
"""Check a page-anchored transcript against the PDF text layer.

usage: check_transcript.py TEXT TRANSCRIPT [--pages 3-5,20] [--min-coverage 0.8] [--ignore FILE]

TEXT: `pdftotext -layout` output (form feed = page break).
TRANSCRIPT: Markdown with one `<!-- page N -->` anchor per page section.

Reports pages with no section, duplicated anchors, and, for each page, the
share of distinct text-layer words (3+ letters, or numbers) that occur in
that page's section or in the preamble (recurring elements). Pages below
--min-coverage are flagged with their missing words, so you can tell an
omission from hidden template text. --ignore FILE: one phrase per line
whose words are not expected (e.g. a hidden template footer).
--pages: check only these pages (a partial run or one subagent's range).
Exit status 1 if a page is missing or flagged.
"""
import argparse
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from textnorm import norm, words  # noqa: E402

ap = argparse.ArgumentParser()
ap.add_argument("text")
ap.add_argument("transcript")
ap.add_argument("--min-coverage", type=float, default=0.8)
ap.add_argument("--ignore")
ap.add_argument("--pages", help="e.g. 3-5,20")
a = ap.parse_args()

pages = open(a.text, encoding="utf-8").read().split("\f")
if pages and not pages[-1].strip():
    pages = pages[:-1]
md = open(a.transcript, encoding="utf-8").read()

parts = re.split(r"<!--\s*page\s+(\d+)\s*-->", md)
preamble = parts[0]
sections: dict[int, str] = {}
dups = []
for i in range(1, len(parts), 2):
    n = int(parts[i])
    if n in sections:
        dups.append(n)
    sections[n] = sections.get(n, "") + parts[i + 1]

ignored = set()
if a.ignore:
    ignored = set(words(open(a.ignore, encoding="utf-8").read()))
pre_words = set(words(preamble))

wanted = range(1, len(pages) + 1)
if a.pages:
    wanted = sorted({n for part in a.pages.split(",") for n in
                     (range(int(part.split("-")[0]), int(part.split("-")[-1]) + 1))})
bad = 0
missing = [n for n in wanted if n not in sections]
extra = [n for n in sections if n > len(pages)]
print(f"{len(pages)} pages, {len(sections)} sections")
if missing:
    bad += 1
    print("missing pages:", " ".join(map(str, missing)))
if extra:
    bad += 1
    print("anchors beyond last page:", " ".join(map(str, extra)))
if dups:
    print("duplicate anchors (merged):", " ".join(map(str, sorted(set(dups)))))

total_have = total_need = 0
for n in wanted:
    if not 1 <= n <= len(pages):
        continue
    need = set(words(pages[n - 1])) - ignored - {str(n)}  # page number
    if not need:
        continue
    sec = norm(sections.get(n, ""))
    sec_words = set(words(sec)) | pre_words
    lost = sorted(w for w in need if w not in sec_words and w not in sec)
    cov = 1 - len(lost) / len(need)
    total_need += len(need)
    total_have += len(need) - len(lost)
    if cov < a.min_coverage:
        bad += 1
        shown = " ".join(lost[:25]) + (" …" if len(lost) > 25 else "")
        print(f"page {n:3d}: coverage {cov:.0%} ({len(need)} words) missing: {shown}")
if total_need:
    print(f"overall coverage {total_have / total_need:.1%}")
sys.exit(1 if bad else 0)
