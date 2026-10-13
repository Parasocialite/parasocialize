"""Cluster helpers for the encyclopedia index.

The index had one way in: 175 rows in date order, plus two filters. Two thousand
years of one-sided attachment, filed by year, is a list, and a list does not tell
a reader that this database is organised. It is organised three other ways and
neither of them was on the page:

  medium   11 values, 186 tags. "the AI ones", "the television ones", "the sport
           ones" - the fastest way for most readers to find their own subject.
  subject  the same story split across several entries. Replika was four rows
           in date order and read as four unrelated things; grouped, it is one
           company and one bereavement.
"""
from __future__ import annotations

MEDIUM_NAME = {
    "ai": "AI and chatbots", "games": "Games", "television_scripted": "Scripted TV",
    "television_unscripted": "Unscripted TV", "literature": "Books",
    "film": "Film", "music": "Music", "sport": "Sport",
    "technology": "Technology", "theology": "Theology and religion",
    "history": "History",
    "radio": "Radio", "comics": "Comics",
    # stage and visual_art were added to the medium list in items 39 and 42 and
    # were never added here, so they fell through to `m.replace("_", " ")`. On
    # the encyclopedia index that rendered as "visual art" and "stage" in lower
    # case in a grid where the other fourteen tiles are Title Case - a reader
    # could see the drift on the page, which is the whole subject of item 33.
    "stage": "Stage", "visual_art": "Visual art",
}
MEDIUM_ORDER = ["ai", "television_scripted", "television_unscripted", "music",
                "film", "literature", "games", "sport", "technology",
                "theology", "history", "radio", "comics", "stage", "visual_art"]


def _assert_covers_the_medium_axis():
    """Every medium the atlas validates against needs a reader-facing label here.

    This is a second copy of a list that already exists in atlas.py, and copies
    drift: build_atlas.py had eleven media where atlas.py had fifteen, so two
    were invisible from the map for two releases. Then this file had thirteen,
    and the two it was missing printed in the wrong case on a public page.

    Importing atlas.MEDIA_LABEL is not the fix - its wording is deliberately
    different ("Scripted television" against "Scripted TV", "Artificial
    intelligence" against "AI and chatbots"), because this one is page copy and
    that one is an atlas chip. So the two stay separate and the drift is made
    impossible instead: a medium with no label here is a build error, not a
    lowercase tile.
    """
    import sys, pathlib
    sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
    from atlas import MEDIA
    missing_name = [m for m in MEDIA if m not in MEDIUM_NAME]
    missing_order = [m for m in MEDIA if m not in MEDIUM_ORDER]
    if missing_name or missing_order:
        raise SystemExit(
            f"tools/clusters.py has drifted from tools/atlas.py's MEDIA list.\n"
            f"  no MEDIUM_NAME label for: {missing_name}\n"
            f"  not in MEDIUM_ORDER:      {missing_order}\n"
            f"Add a reader-facing label for each. Without one the medium prints "
            f"as its raw key, which is how 'stage' and 'visual art' reached a "
            f"public page in lower case beside fourteen Title Case tiles.")


_assert_covers_the_medium_axis()

# A subject cluster is a word that appears in three or more entry ids. The word
# is the cluster's name because it is the thing the reader is looking for, and
# the entries are ordered by year so the group reads as a sequence.
_CLUSTER_STOP = {"the", "a", "of", "and", "to", "in", "on", "for", "is", "it",
                 "no", "my", "of", "that", "who", "why", "how"}

_CLUSTER_LABEL = {
    "replika": "One app, four entries, one bereavement",
    "twitch": "The stream that became a membership",
    "finale": "Endings, and what people do about them",
    "parasocial": "The vocabulary itself",
    "grief": "Grief, and the business built around it",
    "fandom": "Fandom as a crowd with a memory",
    "culture": "Culture as the unit of attachment",
    "launch": "The moment it arrived",
    "sasaeng": "When it turns criminal",
    "doxxing": "Naming, and the cost of it",
    "intimacy": "Intimacy for money",
    "p": "The pronoun, and who it is for",
    "companion": "Companions",
}


def _fmt_year(y) -> str:
    """Mirror of build_cards._fmt_year. Duplicated rather than imported because
    build_cards imports this module, so the import would be circular."""
    if y is None:
        return "-"
    return f"{abs(y)} BC" if y < 0 else str(y)


def _span(yrs) -> str:
    ys = sorted(y for y in yrs if y is not None)
    if not ys:
        return ""
    if ys[0] == ys[-1]:
        return _fmt_year(ys[0])
    return f"{_fmt_year(ys[0])}-{_fmt_year(ys[-1])}"


def _words(eid: str) -> set[str]:
    out = set()
    for w in eid.replace("_", "-").split("-"):
        if len(w) > 3 and w not in _CLUSTER_STOP:
            out.add(w)
    return out


def subject_clusters(entries, limit=14):
    """Entries that share a content word in their id, >=3 of them."""
    from collections import defaultdict
    g = defaultdict(list)
    wmap = {}
    for e in entries:
        w = _words(e["id"])
        wmap[e["id"]] = w
        for x in w:
            g[x].append(e)
    out = []
    for word, es in g.items():
        if len(es) < 3:
            continue
        es = sorted(es, key=lambda x: (x.get("year") or 0))
        yrs = [x.get("year") for x in es if x.get("year") is not None]
        out.append({
            "word": word,
            "label": _CLUSTER_LABEL.get(word, word.replace("-", " ")),
            "entries": es,
            "n": len(es),
            "span": _span(yrs),
        })
    # biggest first, then widest time span, so the meaty ones lead
    out.sort(key=lambda c: (-c["n"], c["word"]))
    return out[:limit]


def medium_clusters(entries):
    """The 11 media, with counts and the year range each one covers."""
    from collections import defaultdict
    g = defaultdict(list)
    for e in entries:
        for m in e.get("medium") or []:
            g[m].append(e)
    out = []
    for m, es in g.items():
        yrs = sorted(x.get("year") for x in es if x.get("year") is not None)
        out.append({
            "key": m,
            "name": MEDIUM_NAME.get(m, m.replace("_", " ")),
            "n": len(es),
            "es": sorted(es, key=lambda x: (x.get("year") or 0)),
            "span": _span(yrs),
        })
    out.sort(key=lambda c: (-c["n"]))
    return out
