"""crosslink.py - join the two halves of the site.

47 stories and 193 encyclopedia entries that do not touch. A story page links to
no entry; an entry links to no story. The only thing joining them is a nav link
to an index page.

The first version of this scored entries by counting shared words and needed three
shared words to count at all. That is the wrong measure. Inside a single aisle
almost every entry contains "fan", "audience", "relationship" and "parasocial" -
words that distinguish the aisle from the other nine and nothing at all within
it. So the floor rejected good matches on generic vocabulary and the ranking was
decided by whichever pair happened to share an uncommon noun.

This weights by inverse document frequency within the candidate pool instead: a
word that appears in 40 of 42 candidates in an aisle is worth almost nothing, and
one that appears in 2 is worth a great deal. Common words stop counting without
being banned, which is what the floor was trying to achieve by brute force.

Three sets of text are compared, because a story and an entry say the same thing
in different vocabularies: the card's headline, one_line and take; the titles of
the reporting it cites; and the entry's title, summary and claim. The reporting
titles matter more than they look - a card sourced from six articles about
consumer-obsession language is *about* that vocabulary even when the card's own
prose avoids it.

    python tools\\crosslink.py --report    # show the picks, change nothing
    python tools\\crosslink.py --apply     # write them into shop.json/encyclopedia.json
"""
from __future__ import annotations

import json
import math
import pathlib
import re
import sys
from collections import defaultdict

ROOT = pathlib.Path(__file__).resolve().parent.parent
SHOP = ROOT / "data" / "shop.json"
ENC = ROOT / "data" / "encyclopedia.json"

MAX_PER_CARD = 6
MIN_IDF = 1.15     # below this a word is too common in the pool to be evidence
MIN_SHARED = 2     # weighted score a pair needs before it is shown at all
# At least this many DISTINCTIVE words in common. A weighted score alone is not
# enough: "the living room is now a comment section" reached mickey-mouse on the
# single word "room", which cleared the score bar only because "room" is rare in
# the brand pool. One uncommon word is a coincidence; two is a subject.
MIN_DISTINCT = 2

# Entries that are about this site rather than about the subject. Excluded by
# name, not by keyword: a keyword filter for site-ish words swept up fan-club,
# the-clerk, macy, the-politician and twitch-500m, all of which are real
# subjects and two of which are exactly the entries a reader wants to be sent to.
SITE_META = {"quarterly-audit"}

STOP = {
    "the", "and", "that", "this", "with", "from", "they", "their", "them",
    "have", "has", "been", "were", "was", "you", "your", "our", "not", "but",
    "for", "are", "its", "his", "her", "she", "him", "who", "what", "when",
    "where", "which", "about", "into", "over", "than", "then", "there", "here",
    "just", "like", "more", "most", "some", "one", "two", "now", "new", "said",
    "says", "say", "get", "got", "make", "made", "even", "also", "back", "way",
    "thing", "things", "people", "person", "time", "year", "years", "day",
    "after", "because", "been", "will", "would", "could", "should", "every",
    "other", "same", "first", "last", "very", "much", "many", "only", "just",
    "does", "did", "was", "were", "has", "had", "its", "out", "off", "own",
    "under", "while", "where", "always", "never", "often", "still", "yet",
}


def words(s):
    return {w for w in re.findall(r"[a-z]{4,}", (s or "").lower()) if w not in STOP}


def card_text(c):
    bits = [str(c.get(k) or "") for k in ("headline", "one_line", "take")]
    # the titles of the reporting are strong evidence of subject matter
    for s in (c.get("sources") or []):
        bits.append(str(s.get("title") or ""))
        bits.append(str(s.get("publisher") or ""))
    return " ".join(bits)


def entry_text(e):
    return " ".join(str(e.get(k) or "") for k in ("title", "summary", "claim"))


def build(cards, entries):
    by_aisle = defaultdict(list)
    for e in entries:
        if e["id"] in SITE_META:
            continue
        for s in (e.get("sections") or []):
            by_aisle[s].append(e)

    # how connected an entry is inside the entry graph; a reader is likelier to
    # follow onward from something well connected. Capped so it can break a tie
    # but never outrank a better textual match.
    deg = defaultdict(int)
    for e in entries:
        for r in (e.get("relations") or []):
            t = r.get("to") or r.get("target")
            if t:
                deg[t] += 1
                deg[e["id"]] += 1

    out, detail = {}, {}
    for c in cards:
        pool = by_aisle.get(c.get("section")) or entries
        if not pool:
            continue
        cw = words(card_text(c))
        if not cw:
            continue
        ews = [words(entry_text(e)) for e in pool]
        # document frequency within the pool decides which of the card's words
        # are actually evidence
        df = defaultdict(int)
        for w in cw:
            for ew in ews:
                if w in ew:
                    df[w] += 1
        n = len(pool)
        idf = {w: math.log(n / df[w]) for w in cw if df[w] > 0}
        idf = {w: v for w, v in idf.items() if v >= MIN_IDF}
        scored = []
        for e, ew in zip(pool, ews):
            shared = cw & ew
            if not shared:
                continue
            distinctive = shared & set(idf)
            if len(distinctive) < MIN_DISTINCT:
                continue
            score = sum(idf.get(w, 0.0) for w in distinctive)
            score += min(deg[e["id"]], 4) * 0.3
            scored.append((score, len(distinctive), e))
        scored.sort(key=lambda t: (-t[0], t[2]["id"]))
        picks = [e for s, _, e in scored[:MAX_PER_CARD] if s >= MIN_SHARED]
        if picks:
            out[c["slug"]] = [e["id"] for e in picks]
            detail[c["slug"]] = {
                "aisle": c.get("section"),
                "distinctive_terms": sorted(idf, key=lambda w: -idf[w])[:8],
                "pool": len(pool),
            }
    return out, detail


def main():
    report = "--report" in sys.argv
    apply = "--apply" in sys.argv
    shop = json.loads(SHOP.read_text(encoding="utf-8"))
    enc = json.loads(ENC.read_text(encoding="utf-8"))
    pairs, detail = build(shop["cards"], enc["entries"])
    byid = {e["id"]: e for e in enc["entries"]}

    cards = shop["cards"]
    print(f"{len(cards)} cards -> {sum(len(v) for v in pairs.values())} links "
          f"(max {MAX_PER_CARD}, min weighted score {MIN_SHARED})\n")
    none = [c["slug"] for c in cards if c["slug"] not in pairs]
    print(f"cards with no link above the floor: {len(none)}")
    for s in none:
        print(f"    {s}")

    import collections
    print("\nlinks per card:",
          dict(collections.Counter(len(v) for v in pairs.values())))

    for slug in list(pairs)[:5]:
        c = next(x for x in cards if x["slug"] == slug)
        d = detail[slug]
        print("=" * 76)
        print(f"[{d['aisle']}] pool of {d['pool']}")
        print(f"  {c['headline'][:70]}")
        print(f"  distinctive: {', '.join(d['distinctive_terms'][:7])}")
        for i in pairs[slug]:
            print(f"    {i:<24} {str(byid[i].get('title'))[:46]}")

    if report or not apply:
        print("\nreport only - nothing written. re-run with --apply")
        return 0

    rev = defaultdict(list)
    for slug, ids in pairs.items():
        for i in ids:
            rev[i].append(slug)
    shop["crosslinks"] = pairs
    enc["stories"] = dict(sorted(rev.items()))
    SHOP.write_text(json.dumps(shop, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    ENC.write_text(json.dumps(enc, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"\nwritten: {len(pairs)} cards linked, {len(rev)} entries link back")
    return 0


if __name__ == "__main__":
    sys.exit(main())