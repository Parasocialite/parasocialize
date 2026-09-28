#!/usr/bin/env python3
"""
backfill_media.py - give the 150 legacy entries a medium.

THE ATLAS NEEDS A THIRD AXIS
`medium` is the cross-cutting taxonomy - theology, literature, film, music,
scripted and unscripted television, sport, technology, ai, history, games - and
only 26 of 176 entries had one. A constellation with 150 unlabelled nodes
clusters them all into a single anonymous blob, which is the same failure as
the original flat `related` list: the map would have nothing to arrange itself
by.

THE MAPPING IS FROM `era`, NOT FROM `lanes`
`lanes` reads application / consideration / manipulation / danger / grief /
contest. Those are editorial stances - the argument the entry is making - and
using them as a medium would have put "grief" next to "ai" because both are
concerns. `era` is already a period-and-domain label the seeders wrote on
purpose ("Cinema", "Sport", "AI", "Fan mail", "Reality television"), so it maps
onto medium almost directly.

This is inference, and it is recorded as such: every entry this script touches
gets a `media_inferred: true`, the map draws inferred labels in a different
weight, and nothing here overwrites a medium a human set by hand.

  python tools/backfill_media.py
"""
import json, pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
ENC = ROOT / "data" / "encyclopedia.json"

# era (lower-cased, substring match) -> media
ERA_MEDIA = [
    # exact-ish first
    ("ai", ["ai"]),
    ("first chatbot", ["ai"]),
    ("internet", ["technology"]),
    ("platform", ["technology"]),
    ("virtual world", ["technology", "games"]),
    ("retail", ["technology"]),
    ("reachability", ["technology"]),
    ("merch", ["technology"]),
    ("marketing", ["technology"]),
    ("idol economy", ["technology"]),
    ("diagnos", ["ai"]),
    ("television", ["television_scripted"]),
    ("reality television", ["television_unscripted"]),
    ("live", ["television_unscripted"]),
    ("broadcast", ["television_scripted"]),
    ("cinema", ["film"]),
    ("theatre", ["film"]),
    ("music", ["music"]),
    ("concert", ["music"]),
    ("voice", ["music"]),
    ("sport", ["sport"]),
    ("fandom", ["games"]),
    ("assembled fandom", ["games"]),
    ("korean fandom", ["music"]),
    ("global fandom", ["games"]),
    ("gaming", ["games"]),
    ("games", ["games"]),
    ("press", ["history"]),
    ("first contact", ["history"]),
    ("antiquity", ["history"]),
    ("medieval", ["theology", "literature"]),
    ("faith", ["theology"]),
    ("early modern", ["literature"]),
    ("enlightenment", ["literature"]),
    ("victorian", ["literature"]),
    ("modern", ["film"]),
    ("fiction", ["literature"]),
    ("contemporary", ["technology"]),
    ("research", ["history"]),
    ("early theory", ["history"]),
    ("naming", ["history"]),
    ("politics", ["history"]),
    ("criticism", ["history"]),
    ("grief", ["history"]),
    ("companion", ["ai"]),
    ("ethics", ["history"]),
    ("legislation", ["history"]),
    ("housing", ["history"]),
    ("school", ["history"]),
    ("crossover", ["history"]),
    ("travel", ["history"]),
    ("suburbia", ["history"]),
    ("fan mail", ["literature"]),
    ("practice", ["history"]),
    ("conclusion", ["history"]),
]


def media_for(entry):
    if entry.get("medium"):
        return None
    era = str(entry.get("era") or "").lower()
    if not era:
        return []
    for key, meds in ERA_MEDIA:
        if key in era:
            return meds
    return []


def main():
    d = json.loads(ENC.read_text(encoding="utf-8"))
    n = inf = blank = 0
    for e in d["entries"]:
        got = media_for(e)
        if got is None:
            continue
        if got:
            e["medium"] = got
            e["media_inferred"] = True
            n += 1
        else:
            blank += 1
    ENC.write_text(json.dumps(d, indent=2, ensure_ascii=False), encoding="utf-8")
    tagged = sum(1 for e in d["entries"] if e.get("medium"))
    print(f"{n} entries given a medium from their era, {blank} could not be inferred")
    print(f"{tagged} of {len(d['entries'])} now carry at least one medium")
    left = [e["id"] for e in d["entries"] if not e.get("medium")]
    if left:
        print("still unlabelled: " + ", ".join(left[:20]))


if __name__ == "__main__":
    main()
