#!/usr/bin/env python3
"""
backfill_media.py - give the 150 legacy entries a medium.

THE ATLAS NEEDS A THIRD AXIS
`medium` is the cross-cutting taxonomy - theology, literature, film, film and
television, music, sport, technology, ai, history, games - and only 26 of 176
entries had one. A constellation with 150 unlabelled nodes clusters them all
into a single anonymous blob, which is the same failure as the original flat
`related` list: the map would have nothing to arrange itself by.

THE MAPPING IS FROM `era`, NOT FROM `lanes`
`lanes` reads application / consideration / manipulation. Those are editorial
stances - the argument the entry is making - and using them as a medium would
have put "grief" next to "ai" because both are concerns. `era` is already a
period-and-domain label the seeders wrote on purpose ("Cinema", "Sport", "AI",
"Fan mail", "Reality television"), so it maps onto medium almost directly.

WORD BOUNDARIES, NOT SUBSTRINGS. This is the whole reason the first version of
this file was wrong. It tested `if key in era` against a table whose first row
was ("ai", ["ai"]), and "ai" is a substring of f-ai-th, ret-ai-l, em-ai-l and
ch-ai-r. Every entry with an era of "Faith" or "Retail" was therefore tagged as
artificial intelligence: a congregation in 200 AD, a shop loyalty card in 1880
and a writer's fan mail all landed under AI, and the AI medium carried 38 entries
when it should have carried 20. Every pattern below is a compiled regex now, and
the one-word rows are anchored on both sides.

Two rows also changed meaning, not just matching:

  ("companion", ["ai"])  was wrong on its face. A Companion era is a category
                         of relationship, not a technology. It maps to history
                         now, which is what the era label is actually telling us.
  ("diagnos", ["ai"])    a diagnosis is a way of describing a bond, not a
                         medium. It maps to history.

This is inference, and it is recorded as such: every entry this script touches
gets a `media_inferred: true`, and nothing here overwrites a medium a human set
by hand. The encyclopedia index labels the medium layer as categorised rather
than sourced, because 151 of 175 entries are in this state and a reader is
entitled to know that before they filter by it.

  python tools/backfill_media.py          # fill in what is missing
  python tools/backfill_media.py --recheck  # re-derive every inferred medium
"""
import argparse
import json
import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parent.parent
ENC = ROOT / "data" / "encyclopedia.json"

# (regex matched against `era`, media) - first match wins, so specific first.
ERA_MEDIA = [
    # --- AI and the modern internet first, they are the most specific -------
    (r"\bai\b", ["ai"]),
    (r"first chatbot", ["ai"]),
    (r"\bcompanion app", ["ai"]),
    (r"\binternet\b", ["technology"]),
    (r"\bplatforms?\b", ["technology"]),
    (r"\bcontemporary\b", ["technology"]),
    (r"virtual world", ["technology", "games"]),
    (r"reachability", ["technology"]),
    (r"\bmerch", ["technology"]),
    (r"\bmarketing\b", ["technology"]),
    (r"idol economy", ["technology"]),

    # --- screen ---------------------------------------------------------------
    (r"reality television", ["television_unscripted"]),
    (r"\btelevision\b", ["television_scripted"]),
    (r"\blive\b", ["television_unscripted"]),
    (r"\bbroadcast\b", ["television_scripted"]),
    (r"\bcinema\b", ["film"]),
    (r"\btheat(?:re|re)s?\b", ["film"]),
    (r"\bfiction\b", ["film"]),
    (r"\bmodern\b", ["film"]),

    # --- music, sport, play ---------------------------------------------------
    (r"\bmusic\b", ["music"]),
    (r"\bconcert", ["music"]),
    (r"\bvoice\b", ["music"]),
    (r"\bsport", ["sport"]),
    (r"\bfandom\b", ["games"]),
    (r"assembled fandom", ["games"]),
    (r"korean fandom", ["music"]),
    (r"global fandom", ["games"]),
    (r"\bgaming\b", ["games"]),
    (r"\bvideo game", ["games"]),
    (r"\bgames?\b", ["games"]),

    # --- the book and the belief ---------------------------------------------
    (r"early modern", ["literature"]),
    (r"\benlightenment\b", ["literature"]),
    (r"\bmedieval\b", ["theology", "literature"]),
    (r"\bfaith\b", ["theology"]),
    (r"\btheology\b", ["theology"]),
    (r"\breligio", ["theology"]),
    (r"fan mail", ["literature"]),

    # --- everything the database is mostly made of ---------------------------
    (r"\bpress\b", ["history"]),
    (r"first contact", ["history"]),
    (r"\bantiquity\b", ["history"]),
    (r"\bearly theory\b", ["history"]),
    (r"\bresearch\b", ["history"]),
    (r"\bnaming\b", ["history"]),
    (r"\bpolitics\b", ["history"]),
    (r"\bcriticism\b", ["history"]),
    (r"\bgrief\b", ["history"]),
    (r"\bethics\b", ["history"]),
    (r"\blegislation\b", ["history"]),
    (r"\bhousing\b", ["history"]),
    (r"\bschool\b", ["history"]),
    (r"\bcrossover\b", ["history"]),
    (r"\btravel\b", ["history"]),
    (r"\bsuburbia\b", ["history"]),
    (r"\bdiagnos", ["history"]),
    (r"\bretail\b", ["history"]),
    (r"\bpractice\b", ["history"]),
    (r"\bconclusion\b", ["history"]),
    (r"\bcompanion\b", ["history"]),
]
COMPILED = [(re.compile(p, re.I), m) for p, m in ERA_MEDIA]


def media_for(entry):
    """The medium implied by this entry's era, or [] if the era says nothing."""
    era = str(entry.get("era") or "")
    if not era:
        return []
    for rx, meds in COMPILED:
        if rx.search(era):
            return meds
    return []


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--recheck", action="store_true",
                    help="re-derive every inferred medium instead of only "
                         "filling in blanks, and report what changed")
    a = ap.parse_args()

    d = json.loads(ENC.read_text(encoding="utf-8"))
    n = inf = blank = 0
    changed = []

    for e in d["entries"]:
        had = list(e.get("medium") or [])
        if had and not (a.recheck and e.get("media_inferred")):
            continue  # hand-set, or already fine
        got = media_for(e)
        if got == had:
            continue
        if got:
            e["medium"] = got
            e["media_inferred"] = True
            n += 1
            if had:
                changed.append((e["id"], e.get("era"), had, got))
        else:
            blank += 1
            if had:
                changed.append((e["id"], e.get("era"), had, []))
                e.pop("medium", None)
                e.pop("media_inferred", None)
        inf += 1

    ENC.write_text(json.dumps(d, indent=1, ensure_ascii=False), encoding="utf-8")

    if changed:
        print(f"corrected {len(changed)} inferred medium(s):")
        for i, era, was, now in changed:
            print(f"  {i:34} era={str(era):22} {was} -> {now or '(none)'}")
    tagged = sum(1 for e in d["entries"] if e.get("medium"))
    inferred = sum(1 for e in d["entries"] if e.get("media_inferred"))
    print(f"{n} entries given a medium from their era, {blank} could not be inferred")
    print(f"{tagged} of {len(d['entries'])} carry at least one medium "
          f"({inferred} of those inferred from the era, not sourced)")
    left = [e["id"] for e in d["entries"] if not e.get("medium")]
    if left:
        print("still unlabelled: " + ", ".join(left[:20]))


if __name__ == "__main__":
    main()
