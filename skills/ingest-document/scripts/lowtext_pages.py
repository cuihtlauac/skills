#!/usr/bin/env python3
"""List pages of a pdftotext output with little or no text.

usage: lowtext_pages.py TEXT [--min CHARS]

TEXT is `pdftotext -layout` output, where a form feed ends each page.
Prints "page chars" for every page with fewer than CHARS non-blank
characters (default 200): candidates for a blank, scanned or figure page.
"""
import argparse

ap = argparse.ArgumentParser()
ap.add_argument("text")
ap.add_argument("--min", type=int, default=200)
a = ap.parse_args()

pages = open(a.text, encoding="utf-8").read().split("\f")
if pages and not pages[-1].strip():
    pages = pages[:-1]
low = [(i + 1, len("".join(p.split()))) for i, p in enumerate(pages)]
low = [(n, c) for n, c in low if c < a.min]
print(f"{len(pages)} pages, {len(low)} below {a.min} characters")
for n, c in low:
    print(f"{n:4d} {c:5d}")
