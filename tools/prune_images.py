#!/usr/bin/env python3
"""
prune_images.py - keep only the images that are actually about the thing.

Commons search returns a photograph of a person who happened to be in frame
near a search term, not the thing itself. Cached set had "a camera operator",
"a man on a phone" and "a lion dance team" sitting under captions that promised
Dolores from Pan's Labyrinth, Replika, and MTV respectively. That is a lie in
the credit line, which is the one place a licence claim has to be true.

So: an allowlist of verified slugs with hand-written captions that describe
what is actually in the frame. Anything not on the list gets dropped, and the
page falls back to the generated cover art rather than showing a wrong picture.
"""
import json, pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
MAN = ROOT / "data" / "images.json"

# slug -> caption that is true of the actual file
VERIFIED = {
    "history-dionne-warwick":
        "Dionne Warwick with Anthony Newley and Sammy Cahn, 1960s",
    "history-fan-letters":
        "Rodgers' letter to a fan, 1942 - the reply is the whole point",
    "history-macy-store":
        "A soap opera studio, 1940s - the form the 1956 study was about",
    "figure-peewee":
        "Paul Reubens, 1988",
    "figure-kozik":
        "Charlie Kaufman, 2015",
    "figure-tay":
        "Taylor Swift recording a spoken-word entry, 2023",
    "moment-power-rangers":
        "Power Rangers, 1990s",
    "top8-cartoons-90s":
        "Children watching television together, Burkina Faso 2006",
}

# the ones the pages reference. if a referenced slug is missing, the builder
# already falls back to generated art - so removing is safe.
DROP = {
    "history-margery-kempe",   # only book photos and benches on Commons
    "figure-dolores",          # only crew photos, not the character
    "moment-rugrats-mask",     # duplicated the top8 image anyway
    "moment-mtv",              # a lion dance team at a studio
    "moment-replika-update",   # a stock photo of a phone
    "moment-tay-tour",         # a photographer, not the tour
    "moment-ashers-grief",     # someone's phone on a windscreen
    "moment-wojak",            # a person at a protest holding one
    "moment-got-ending",       # a logo
    "moment-fortnite-dance",   # a logo
}


def main():
    d = json.loads(MAN.read_text(encoding="utf-8"))
    kept, dropped = [], []
    for i in d["items"]:
        if i["slug"] in DROP:
            dropped.append(i["slug"])
            continue
        if i["slug"] in VERIFIED:
            i["caption"] = VERIFIED[i["slug"]]
            i["verified"] = True
        kept.append(i)
    d["items"] = kept
    d["_note"] = ("Editorial images, resolved via the Wikimedia Commons API and "
                  "cached to img/editorial/. Hotlinking was tested and refused by "
                  "TMDB/Spotify/Fandom, so caching is the only reliable route. "
                  "Captions are hand-written and describe the actual file - see "
                  "tools/prune_images.py, because Commons search returns "
                  "near-misses and a wrong caption under a CC credit is a lie.")
    MAN.write_text(json.dumps(d, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"kept {len(kept)}, dropped {len(dropped)}")
    for s in dropped:
        print(f"  dropped {s}")


if __name__ == "__main__":
    main()
