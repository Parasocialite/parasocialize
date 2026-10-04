"""crosslink.py - join the two halves of the site, and look at the result first.

The site is 47 stories and 193 encyclopedia entries that do not touch. A story
page links to no entry; an entry links to no story. The only thing joining them
is a nav link to an index page. Everything else on the site is well-built - the
entry graph is genuinely good, `the-dog` reaching paleolithic-figures and
neanderthal-burial - and none of it connects to the journalism.

Both halves already carry the same vocabulary: the ten aisles and the seven laws.
The brand card about YouTube puttling spending reaches thirty-one entries by aisle
alone, and thirty-one is a list rather than a path. But among those thirty-one are
trading-stamps, fan-club, airline-miles, club-card and coffee-card - which is
precisely the argument the story makes. The join is real. It just needs
narrowing to something a reader will actually follow.

So: score by what the two texts are about, keep the best handful, and require a
score above a floor so a card never gets five links chosen for him.

    python tools\\crosslink.py --report      # show the picks, change nothing
    python tools\\crosslink.py --apply       # write them into the data
"""
from __future__ import annotations

import json
import pathlib
import re
import sys
from collections import defaultdict

ROOT = pathlib.Path(__file__).resolve().parent.parent
SHOP = ROOT / "data" / "shop.json"
ENC = ROOT / "data" / "encyclopedia.json"

MAX_PER_CARD = 5
# Below this the two texts are not demonstrably about the same thing, and the
# link is the reader's to find rather than ours to assert.
FLOOR = 3

# Words that are in every story on the site and therefore distinguish nothing.
STOP = {
    "the", "and", "that", "this", "with", "from", "they", "their", "them",
    "have", "has", "been", "were", "was", "were", "you", "your", "our",
    "not", "but", "for", "are", "its", "his", "her", "she", "him", "who",
    "what", "when", "where", "which", "about", "into", "over", "than",
    "then", "there", "here", "just", "like", "more", "most", "some", "one",
    "two", "now", "new", "said", "says", "say", "get", "got", "make",
    "made", "make", "even", "also", "back", "way", "thing", "things",
    "people", "person", "time", "year", "years", "day", "after", "because",
}


def words(s):
    return {w for w in re.findall(r"[a-z]{4,}", (s or "").lower()) if w not in STOP}


def card_text(c):
    return " ".join(str(c.get(k) or "") for k in ("headline", "one_line", "take"))


def entry_text(e):
    bits = [str(e.get(k) or "") for k in ("title", "summary", "claim")]
    return " ".join(bits)


def build_pairs(cards, entries):
    by_aisle = defaultdict(list)
    for e in entries:
        for s in (e.get("sections") or []):
            by_aisle[s].append(e)

    # entries that are well-connected in the entry graph read as more central,
    # and a reader is likelier to follow them onward
    deg = defaultdict(int)
    for e in entries:
        for r in (e.get("relations") or []):
            t = r.get("to") or r.get("target")
            if t:
                deg[t] += 1
                deg[e["id"]] += 1

    out = {}
    for c in cards:
        cw = words(card_text(c))
        pool = by_aisle.get(c.get("section"), []) or entries
        scored = []
        for e in pool:
            shared = cw & words(entry_text(e))
            if len(shared) < FLOOR:
                continue
            # a small nudge toward connected entries, never enough to outrank a
            # better lexical match on its own
            scored.append((len(shared) + min(deg[e["id"]], 3) * 0.25,
                           len(shared), e))
        scored.sort(key=lambda t: (-t[0], -t[1], t[2]["id"]))
        picks = [e for _, _, e in scored[:MAX_PER_CARD]]
        if picks:
            out[c["slug"]] = [e["id"] for e in picks]
    return out


def main():
    report = "--report" in sys.argv
    apply = "--apply" in sys.argv
    shop = json.loads(SHOP.read_text(encoding="utf-8"))
    enc = json.loads(ENC.read_text(encoding="utf-8"))
    pairs = build_pairs(shop["cards"], enc["entries"])

    print(f"{len(shop['cards'])} cards -> {sum(len(v) for v in pairs.values())} links "
          f"(max {MAX_PER_CARD} each, floor {FLOOR} shared words)\n")

    none = [c["slug"] for c in shop["cards"] if c["slug"] not in pairs]
    print(f"cards with no link above the floor: {len(none)}")
    for s in none:
        print(f"    {s}")

    byid = {e["id"]: e for e in enc["entries"]}
    for slug, ids in list(pairs.items())[:6]:
        c = next(x for x in shop["cards"] if x["slug"] == slug)
        print("=" * 74)
        print(f"[{c.get('section')}] {c['headline'][:66]}")
        for i in ids:
            e = byid[i]
            print(f"    {i:<24} {str(e.get('title'))[:52]}")
        print()

    if report or not apply:
        print("report only - nothing written. re-run with --apply")
        return 0

    # write both directions. one join, stored twice, so neither half has to be
    # recomputed at build time and the entry page can link back without the
    # story data being loaded there.
    rev = defaultdict(list)
    for slug, ids in pairs.items():
        for i in ids:
            rev[i].append(slug)
    shop["crosslinks"] = pairs
    enc["stories"] = {k: v for k, v in sorted(rev.items())}
    SHOP.write_text(json.dumps(shop, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    ENC.write_text(json.dumps(enc, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"written: {len(pairs)} cards linked, {len(rev)} entries now link back")
    return 0


if __name__ == "__main__":
    sys.exit(main())