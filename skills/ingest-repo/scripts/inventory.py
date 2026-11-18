#!/usr/bin/env python3
"""Inventory of a git repository at one commit, as Markdown.

usage: inventory.py CLONE REV [--slug SLUG] [--depth N] [--big LINES]

Prints: the commit and its dates, history size, tags; files and lines by
top-level directory (to --depth levels) and by extension; notable files
(readme, licence, build, packaging, CI, containers, docs); submodules; and
a triage list of files that look generated, vendored, minified or bulk
(by path pattern, by a "generated" marker in the first lines, or by size
over --big lines). Only reads the repository; every path is as of REV.
"""
import argparse
import collections
import fnmatch
import re
import subprocess

ap = argparse.ArgumentParser()
ap.add_argument("clone")
ap.add_argument("rev")
ap.add_argument("--slug", default="repo")
ap.add_argument("--depth", type=int, default=1)
ap.add_argument("--big", type=int, default=5000)
a = ap.parse_args()


def git(*args, binary=False):
    return subprocess.run(["git", "-C", a.clone, *args], capture_output=True,
                          check=True, text=not binary).stdout


sha = git("rev-parse", a.rev + "^{commit}").strip()
date = git("log", "-1", "--format=%cI", sha).strip()
first = git("log", "--reverse", "--format=%aI", sha).split("\n", 1)[0]
ncommits = git("rev-list", "--count", sha).strip()
nmerges = git("rev-list", "--count", "--merges", sha).strip()
tags = [t for t in git("tag", "--merged", sha, "--sort=-creatordate",
                       "--format=%(refname:short)\t%(creatordate:short)").splitlines() if t]

# ---- files and line counts at sha (one cat-file --batch pass)
entries = []  # (path, size)
for line in git("ls-tree", "-r", "-l", "--full-tree", sha).splitlines():
    meta, path = line.split("\t", 1)
    mode, kind, obj, size = meta.split()
    if kind == "blob":
        entries.append((path, obj, int(size) if size != "-" else 0))
    elif kind == "commit":
        entries.append((path, None, 0))  # submodule

p = subprocess.Popen(["git", "-C", a.clone, "cat-file", "--batch"],
                     stdin=subprocess.PIPE, stdout=subprocess.PIPE)
info = {}  # path -> (lines, binary, head)
for path, obj, size in entries:
    if obj is None:
        continue
    p.stdin.write((obj + "\n").encode())
    p.stdin.flush()
    header = p.stdout.readline().split()
    data = p.stdout.read(int(header[2]))
    p.stdout.read(1)
    binary = b"\0" in data[:8000]
    lines = 0 if binary else data.count(b"\n") + (1 if data and not data.endswith(b"\n") else 0)
    head = "" if binary else data[:2000].decode("utf-8", "replace").lower()
    info[path] = (lines, binary, head)
p.stdin.close()
p.wait()

submodules = [path for path, obj, _ in entries if obj is None]


def area(path):
    parts = path.split("/")
    if len(parts) == 1:
        return "(root)"
    return "/".join(parts[:min(a.depth, len(parts) - 1)])


def ext(path):
    name = path.rsplit("/", 1)[-1]
    if "." not in name.lstrip("."):
        return name if name in ("Makefile", "Dockerfile", "dune", "BUILD") else "(none)"
    return "." + name.rsplit(".", 1)[-1].lower()


by_area = collections.defaultdict(lambda: [0, 0])
by_ext = collections.defaultdict(lambda: [0, 0])
for path, (lines, binary, _) in info.items():
    for d, k in ((by_area, area(path)), (by_ext, "(binary)" if binary else ext(path))):
        d[k][0] += 1
        d[k][1] += lines

NOTABLE = [
    ("readme", ["readme*", "*/readme*"]),
    ("licence", ["license*", "licence*", "copying*", "notice*"]),
    ("contributing / governance", ["contributing*", "code_of_conduct*", "governance*",
                                   "maintainers*", "codeowners", "*/codeowners", "security*"]),
    ("changelog", ["changelog*", "changes*", "history*", "news*", "releases*"]),
    ("build / packaging", ["makefile", "*.mk", "dune-project", "*.opam", "package.json",
                           "pyproject.toml", "setup.py", "setup.cfg", "cargo.toml", "go.mod",
                           "pom.xml", "build.gradle*", "cmakelists.txt", "meson.build",
                           "*.cabal", "stack.yaml", "flake.nix", "default.nix", "build.ninja",
                           "*.csproj", "*.sln", "gemfile", "composer.json"]),
    ("CI", [".github/workflows/*", ".gitlab-ci.yml", ".woodpecker*", ".circleci/*",
            "azure-pipelines*", "jenkinsfile", ".travis.yml", ".buildkite/*"]),
    ("containers / deploy", ["dockerfile*", "*/dockerfile*", "docker-compose*", "*.dockerfile",
                             "k8s/*", "helm/*", "*.wxs", "*.ps1", "*.nsi"]),
    ("docs", ["doc/*", "docs/*", "*.md"]),
]


def notable(cat_globs):
    out = []
    for path in sorted(info):
        low = path.lower()
        name = low.rsplit("/", 1)[-1]
        if any(fnmatch.fnmatch(low, g) or ("/" not in g and fnmatch.fnmatch(name, g))
               for g in cat_globs):
            out.append(path)
    return out


BULK_PATH = ["vendor/*", "*/vendor/*", "third_party/*", "*/third_party/*", "node_modules/*",
             "*/node_modules/*", "deps/*", "*.min.js", "*.min.css", "*.map", "*.lock",
             "*-lock.json", "*-lock.yaml", "*.locked", "*/generated/*", "generated/*",
             "*_pb2.py", "*.pb.go", "dist/*", "*/dist/*", "build/*"]
GEN_MARK = re.compile(r"(automatically generated|auto-generated|autogenerated|"
                      r"generated by|do not edit|@generated)")
bulk = []
for path, (lines, binary, head) in sorted(info.items()):
    why = []
    low = path.lower()
    if any(fnmatch.fnmatch(low, g) for g in BULK_PATH):
        why.append("path")
    if GEN_MARK.search(head):
        why.append("generated marker")
    if lines > a.big:
        why.append(f"{lines} lines")
    if why and not binary:
        bulk.append((path, lines, ", ".join(why)))

# ---- line churn over the whole history: catches bulk files deleted since
churn = collections.Counter()
log = subprocess.run(["git", "-C", a.clone, "-c", "core.quotePath=false", "log", "--no-renames",
                      "--numstat", "--format=", sha], capture_output=True, check=True).stdout
for line in log.decode("utf-8", "replace").splitlines():
    f = line.split("\t")
    if len(f) == 3 and f[0] != "-":
        churn[f[2]] += int(f[0]) + int(f[1])
total_churn = sum(churn.values()) or 1

# ---- print
pr = print
pr(f"# Inventory: {a.slug}\n")
pr(f"- Commit: `{sha}` ({date})")
pr(f"- History: {ncommits} commits ({nmerges} merges), first authored {first[:10]}")
pr(f"- Files: {len(info)} ({sum(1 for v in info.values() if v[1])} binary), "
   f"{sum(v[0] for v in info.values())} text lines")
if submodules:
    pr(f"- Submodules: {', '.join(f'`{s}`' for s in submodules)}")
pr(f"- Tags reachable: {len(tags)}" + (f"; latest: {', '.join(t.replace(chr(9), ' (') + ')' for t in tags[:5])}" if tags else ""))
pr("\n## By directory\n\n| directory | files | lines |\n|---|---:|---:|")
for k, (n, l) in sorted(by_area.items(), key=lambda x: -x[1][1]):
    pr(f"| `{k}` | {n} | {l} |")
pr("\n## By extension\n\n| extension | files | lines |\n|---|---:|---:|")
for k, (n, l) in sorted(by_ext.items(), key=lambda x: -x[1][1])[:25]:
    pr(f"| `{k}` | {n} | {l} |")
pr("\n## Notable files\n")
for cat, globs in NOTABLE:
    files = notable(globs)
    if files:
        shown = ", ".join(f"`{f}`" for f in files[:15])
        more = f" and {len(files) - 15} more" if len(files) > 15 else ""
        pr(f"- **{cat}**: {shown}{more}")
pr("\n## Triage: possibly generated, vendored or bulk\n")
pr("Decide for each pattern whether it is hand-written; list the excluded ones "
   "as globs in the bulk file passed to `history.py --exclude`.\n")
pr("At the pinned commit:\n")
if bulk:
    pr("| path | lines | why |\n|---|---:|---|")
    for path, lines, why in bulk[:60]:
        pr(f"| `{path}` | {lines} | {why} |")
    if len(bulk) > 60:
        pr(f"\n…and {len(bulk) - 60} more.")
else:
    pr("Nothing flagged.")
pr(f"\nLargest line churn (added + deleted) over the whole history, deleted files "
   f"included; a few files holding a large share are usually generated or vendored:\n")
pr("| path | churn | share | at pinned commit |\n|---|---:|---:|---|")
for path, c in churn.most_common(20):
    pr(f"| `{path}` | {c} | {100 * c / total_churn:.1f}% | {'yes' if path in info else 'deleted'} |")
