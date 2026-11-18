"""Text normalisation shared by the checkers.

NFKC, lower case, typographic quotes made ASCII, whitespace collapsed.
`flat` keeps only letters and digits, to match across table splits.
"""
import re
import unicodedata

_QUOTES = str.maketrans({"’": "'", "‘": "'", "«": '"', "»": '"',
                         "“": '"', "”": '"'})


def norm(s: str) -> str:
    s = unicodedata.normalize("NFKC", s).lower().translate(_QUOTES)
    return re.sub(r"[\s\x1c-\x1f]+", " ", s).strip()


def flat(s: str) -> str:
    return re.sub(r"[\W_]", "", norm(s))


def words(s: str) -> list[str]:
    return [w for w in re.findall(r"\w+", norm(s)) if len(w) > 2 and not w.isdigit()] \
        + [w for w in re.findall(r"\d+", norm(s))]


def split_ellipsis(s: str) -> list[str]:
    return re.split(r"\s*(?:\.\.\.|…|\[…\]|\[\.\.\.\])\s*", s)
