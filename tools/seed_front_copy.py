# -*- coding: utf-8 -*-
"""Seed data/front_copy.json with the copy the front page is carrying right now.

The initial edition is spelled out here, once. After this, `data/front_copy.json`
is the authority and `build_cards.py` reads it - so there is only ever one copy
of the front page's words, and it is not inside a Python template where it is
invisible next to the counts.
"""
import json
import pathlib
import sys
from datetime import date

sys.stdout.reconfigure(encoding="utf-8")
ROOT = pathlib.Path(__file__).resolve().parent.parent
DATA = ROOT / "data" / "front_copy.json"

COPY = {
    "kicker": "iYi &middot; behind the counter",
    "line": ("You feel like you know somebody who has no idea you exist. "
             "<b>Everybody has one.</b> This is the news feed for that."),
    "thesis_word": "Horton and Wohl coined <i>parasocial</i> to describe television.",
    "thesis_thing": ("Somebody carried their dead into a cave and set a stone "
                     "under her head."),
    "clerk_line": ("<b>I keep the record.</b> Every claim here carries its "
                   "source, and the ones nobody has opened say so. I do not "
                   "remember you, and nothing here pretends to."),
    "door_stories": "One a day, each one signed by a person. 48 so far.",
    "door_encyclopedia": "248 entries, every claim cited.",
}

if DATA.exists():
    sys.exit(f"refusing: {DATA} exists. Append with "
             f"`python tools/front_copy.py --save --note '...'` instead.")

# the two counts are the only numbers in the copy, and they are read from the
# data rather than typed - so the seed records what the data says today
DOC = {
    "_note": (
        "Front page copy, one edition per bi-daily release. `front_copy.py "
        "--stamp <date>` sets which one is live and `build_cards.py` renders "
        "it - the copy used to be written into build_cards.py's template, which "
        "made it impossible to rotate without editing a generator, and it was "
        "invisible there next to the counts. Appended, never rewritten: the "
        "sequence of what the front page said is the record. The hub teasers "
        "are NOT here - they come from each story's own `take`, cut at "
        "sentence boundaries by `deck()` in build_cards.py, so they change when "
        "the stories do."),
    "_live": date.today().isoformat(),
    "editions": [
        {"date": date.today().isoformat(),
         "note": ("the masthead lockup: iYi in the clerk mood beside the line "
                  "and the thesis, with the doors as their own row"),
         "copy": COPY},
    ],
}

DATA.write_bytes(json.dumps(DOC, ensure_ascii=False, indent=2)
                 .replace("\n", "\r\n").encode("utf-8"))
print(f"  wrote {DATA} ({DATA.stat().st_size} bytes), "
      f"{len(DOC['editions'])} edition, live {DOC['_live']}")
for k, v in COPY.items():
    print(f"    {k:18s} {v[:78]}")
