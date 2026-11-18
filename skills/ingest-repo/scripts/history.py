#!/usr/bin/env python3
"""Contributor statistics from the history of a git repository.

usage: history.py CLONE REV OUTDIR [--exclude BULK] [--identities TSV]
                  [--bots TSV] [--area-depth N]

Reads `git log REV` (authors through .mailmap, co-authors from
Co-authored-by trailers) and writes CSVs to OUTDIR:

  contributors.csv   per person: commits, merges, co-authored, first/last
                     dates, active months, line changes (clean = excluding
                     BULK), top areas
  monthly.csv        per person and month: commits, clean line changes
  areas.csv          per person and area: commits, clean line changes
  area_ownership.csv per area: commits, clean churn, people, bus factor
                     (fewest people making >= 50% of clean churn), top owner
  years.csv          per year: commits, active people, newcomers
  identities.csv     every raw (name, email) seen, with its person and
                     count. It holds email addresses: keep it local.

"commits" are non-merge commits by humans. A file's area is its directory
to --area-depth levels ("(root)" for top-level files). BULK is a file of
glob patterns, one per line (`#` comments), for generated, vendored or
copied files: they count in raw line changes only. IDENTITIES maps a raw
email or name (case-insensitive) to a person: `raw<TAB>person`. BOTS lists
people (after mapping) that are bots, one per line; names ending in [bot]
are bots anyway. Possible duplicate people (same name once accents, case
and punctuation are removed) are reported on stderr; settle them in
IDENTITIES. Only reads the repository.
"""
import argparse
import collections
import csv
import fnmatch
import os
import re
import subprocess
import sys
import unicodedata
from datetime import date

ap = argparse.ArgumentParser()
ap.add_argument("clone")
ap.add_argument("rev")
ap.add_argument("outdir")
ap.add_argument("--exclude")
ap.add_argument("--identities")
ap.add_argument("--bots")
ap.add_argument("--area-depth", type=int, default=1)
a = ap.parse_args()


def lines_of(path):
    if not path:
        return []
    return [l.rstrip("\n") for l in open(path, encoding="utf-8")
            if l.strip() and not l.lstrip().startswith("#")]


bulk_globs = lines_of(a.exclude)
ident = {}
for l in lines_of(a.identities):
    raw, person = l.split("\t")[:2]
    ident[raw.strip().lower()] = person.strip()
bots = set(lines_of(a.bots))


def person(name, email):
    return ident.get(email.strip().lower()) or ident.get(name.strip().lower()) or name.strip()


def is_bot(p):
    return p in bots or p.endswith("[bot]")


def is_bulk(path):
    return any(fnmatch.fnmatch(path, g) for g in bulk_globs)


def area(path):
    parts = path.split("/")
    if len(parts) == 1:
        return "(root)"
    return "/".join(parts[:min(a.area_depth, len(parts) - 1)])


def unquote(p):
    if len(p) >= 2 and p[0] == p[-1] == '"':
        p = p[1:-1].encode("latin-1", "backslashreplace").decode("unicode_escape") \
            .encode("latin-1").decode("utf-8", "replace")
    return p


fmt = "%x1e%H%x1f%P%x1f%aN%x1f%aE%x1f%aI%x1f%(trailers:key=Co-authored-by,valueonly,separator=%x1d)"
out = subprocess.run(["git", "-C", a.clone, "-c", "core.quotePath=false", "log",
                      "--no-renames", "--numstat", "--format=" + fmt, a.rev],
                     capture_output=True, check=True).stdout.decode("utf-8", "replace")


def new():
    return {"commits": 0, "add": 0, "del": 0}


people = collections.defaultdict(lambda: {
    "commits": 0, "merges": 0, "coauthored": 0, "first": "9999", "last": "0000",
    "months": collections.defaultdict(new), "areas": collections.defaultdict(new),
    "add_raw": 0, "del_raw": 0, "add": 0, "del": 0})
seen = collections.Counter()
total = merges = 0
for rec in out.split("\x1e")[1:]:
    head, _, body = rec.partition("\n")
    sha, parents, an, ae, ad, trailers = head.split("\x1f")
    total += 1
    who = person(an, ae)
    seen[(who, an, ae)] += 1
    p = people[who]
    if len(parents.split()) > 1:
        p["merges"] += 1
        merges += 1
        continue
    day, month = ad[:10], ad[:7]
    p["commits"] += 1
    p["first"], p["last"] = min(p["first"], day), max(p["last"], day)
    m = p["months"][month]
    m["commits"] += 1
    touched = set()
    for line in body.splitlines():
        f = line.split("\t")
        if len(f) != 3:
            continue
        add, dele = (0 if x == "-" else int(x) for x in f[:2])
        path = unquote(f[2])
        p["add_raw"] += add
        p["del_raw"] += dele
        if is_bulk(path):
            continue
        ar = p["areas"][area(path)]
        if area(path) not in touched:
            touched.add(area(path))
            ar["commits"] += 1
        for d in (p, m, ar):
            d["add"] += add
            d["del"] += dele
    for t in trailers.split("\x1d"):
        if "<" in t:
            n, e = t.split("<", 1)
            co = person(n, e.rstrip("> "))
            if co != who:
                people[co]["coauthored"] += 1

os.makedirs(a.outdir, exist_ok=True)


def write(name, header, rows):
    with open(os.path.join(a.outdir, name), "w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(header)
        w.writerows(rows)


ranked = sorted(people.items(), key=lambda kv: (-kv[1]["commits"], kv[0]))
humans = [(k, v) for k, v in ranked if not is_bot(k) and v["commits"] > 0]


def churn(d):
    return d["add"] + d["del"]


def top_areas(v, n=3):
    tot = churn(v) or 1
    best = sorted(((k, churn(x)) for k, x in v["areas"].items() if churn(x)), key=lambda x: -x[1])[:n]
    return "; ".join(f"{k} {100 * c / tot:.0f}%" for k, c in best)


write("contributors.csv",
      ["person", "bot", "commits", "merges", "coauthored", "first", "last", "active_months",
       "added_raw", "deleted_raw", "added_clean", "deleted_clean", "top_areas"],
      [[k, int(is_bot(k)), v["commits"], v["merges"], v["coauthored"],
        v["first"] if v["commits"] else "", v["last"] if v["commits"] else "",
        len(v["months"]), v["add_raw"], v["del_raw"], v["add"], v["del"], top_areas(v)]
       for k, v in ranked])
write("monthly.csv", ["person", "month", "commits", "added_clean", "deleted_clean"],
      [[k, mo, x["commits"], x["add"], x["del"]]
       for k, v in humans for mo, x in sorted(v["months"].items())])
write("areas.csv", ["person", "area", "commits", "added_clean", "deleted_clean"],
      [[k, ar, x["commits"], x["add"], x["del"]]
       for k, v in humans for ar, x in sorted(v["areas"].items())])

own = []
for ar in sorted({ar for _, v in humans for ar in v["areas"]}):
    rows = sorted(((k, v["areas"][ar]) for k, v in humans if ar in v["areas"]),
                  key=lambda kv: -churn(kv[1]))
    tot = sum(churn(x) for _, x in rows)
    if not tot:
        continue
    acc = bus = 0
    for _, x in rows:
        acc += churn(x)
        bus += 1
        if 2 * acc >= tot:
            break
    own.append([ar, sum(x["commits"] for _, x in rows), tot, len(rows), bus,
                rows[0][0], f"{churn(rows[0][1]) / tot:.3f}"])
write("area_ownership.csv",
      ["area", "commits", "clean_churn", "contributors", "bus_factor", "top_owner", "top_share"],
      sorted(own, key=lambda r: -r[2]))

years = collections.defaultdict(lambda: [0, set(), set()])
for k, v in humans:
    for mo, x in v["months"].items():
        y = years[mo[:4]]
        y[0] += x["commits"]
        y[1].add(k)
    years[v["first"][:4]][2].add(k)
write("years.csv", ["year", "commits", "active", "newcomers", "returning"],
      [[y, c, len(act), len(nw), len(act) - len(nw)] for y, (c, act, nw) in sorted(years.items())])
write("identities.csv", ["person", "name", "email", "commits"],
      [[w, n, e, c] for (w, n, e), c in sorted(seen.items())])


def key(s):
    s = unicodedata.normalize("NFKD", s)
    s = "".join(ch for ch in s if not unicodedata.combining(ch)).lower()
    return " ".join(sorted(re.findall(r"[a-z0-9]+", s)))


groups = collections.defaultdict(set)
for k in people:
    groups[key(k)].add(k)
dups = [sorted(g) for g in groups.values() if len(g) > 1]
for g in dups:
    print("possible duplicate: " + " | ".join(g), file=sys.stderr)

ncommits = sum(v["commits"] for _, v in humans)
print(f"ok: {total} commits ({merges} merges), {ncommits} human non-merge commits, "
      f"{len(humans)} people, {len(own)} areas, {len(dups)} possible duplicates")
