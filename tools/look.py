"""look.py - record that an image was actually opened, and what it showed.

`image_audit.py` downgraded all 73 records to `kind: "unchecked"` and said a record
becomes `exact` or `illustrative` again "once somebody has looked at the file and
written down the date". That was written as though looking required a person.

It does not. The agent doing this work can open an image and see it, which means
the largest remaining queue in the project was not blocked at all - it was
described as blocked because nobody tested the claim. (The stale "blocked on human
voice" note in AGENTS.md was the same mistake one file over.)

So this tool does what `add_source.py` does for citations: take the finding, record
it, keep it checkable.

    python tools\\look.py --list
    python tools\\look.py <slug> exact "<what the frame showed>"
    python tools\\look.py <slug> exact "<finding>" --note "the location rests on src"

Two rules it will not bend:

  * `exact` and `illustrative` require a written reason. A bare date would
    reproduce the original defect in a new key - `looked` promising a look that
    nothing records.
  * it records what the frame supported, never what the caption hoped for. Where
    the caption names a person, place or event that pixels cannot establish, the
    reason has to say so and the kind drops to `illustrative`.

That second rule is the one that matters. Looking at a portrait of a woman at an
awards backdrop does not tell you she is Taylor Swift, and no amount of staring
changes that; the name comes from the `src` record. A reason that reads "clearly
Taylor Swift" would be me performing recognition rather than looking.
"""
from __future__ import annotations

import json
import pathlib
import sys
from datetime import date

ROOT = pathlib.Path(__file__).resolve().parent.parent
MAN = ROOT / "data" / "images.json"

VALID = {"exact", "illustrative"}
ALL = VALID | {"unchecked"}

arg = sys.argv[1:]
LIST = "--list" in arg
APPLY = "--apply" in arg
NOTE = None
if "--note" in arg:
    i = arg.index("--note")
    NOTE = arg[i + 1]
    del arg[i:i + 2]
CAPTION = None
if "--caption" in arg:
    i = arg.index("--caption")
    CAPTION = arg[i + 1]
    del arg[i:i + 2]
# strip the flags only after reading them. Removing "--apply" first and then
# asking whether it is present makes the answer permanently no, which is how
# this printed "(dry run)" on a command that carried --apply.
arg = [a for a in arg if not a.startswith("--")]

man = json.loads(MAN.read_text(encoding="utf-8"))
items = man["items"]

if LIST or not arg:
    seen = [i for i in items if i.get("looked")]
    todo = [i for i in items if not i.get("looked")]
    openable = [i for i in todo if i.get("local")]
    # A withdrawn record has neither a cached file nor a source. Those are the
    # images a review rejected: `apply_review.py` strips local, src and cached
    # and leaves a stub caption. There is nothing to fetch and nothing to open,
    # so they are not outstanding work.
    #
    # Counting them as "needs fetching" overstated the queue by 39% - 64 records
    # reported against 39 that can actually be looked at. A queue that tells you
    # to go and fetch twenty-five images that were deliberately withdrawn is
    # worse than no queue, because it sends you to do work that cannot exist.
    withdrawn = [i for i in todo
                 if not i.get("local") and not i.get("src")]
    fetchable = [i for i in todo
                 if not i.get("local") and i.get("src")]
    print(f"looked: {len(seen)} of {len(items)}")
    for kind in sorted(VALID):
        print(f"   {kind:<13} {sum(1 for i in seen if i.get('kind') == kind)}")
    print(f"\nQUEUE IS {len(openable)}, not {len(todo)}.")
    print(f"   openable now (cached file)   {len(openable)}")
    print(f"   fetchable (source on record) {len(fetchable)}")
    print(f"   withdrawn, never to be opened {len(withdrawn)}  "
          f"- rejected by review, no image and no source")
    if fetchable:
        print("\nfetch first:")
        for i in fetchable:
            print(f"   {i['slug']}  {(i.get('src') or {}).get('page','')}")
    if openable:
        print("\nready to open:")
        for i in openable:
            print(f"   {i['local'].rsplit('/', 1)[-1][:14]}  {i.get('caption','')[:70]}")
    if withdrawn:
        print(f"\nwithdrawn and closed - do not fetch ({len(withdrawn)}):")
        print("   " + ", ".join(i["slug"] for i in withdrawn))
    sys.exit(0)

if len(arg) < 2:
    sys.exit("usage: look.py <slug> <exact|illustrative|unchecked> \"<finding>\" "
             "[--note \"...\"] [--apply]")

slug, kind = arg[0], arg[1]
reason = arg[2] if len(arg) > 2 else ""

if kind not in ALL:
    sys.exit(f"unknown kind {kind!r}; use one of {sorted(ALL)}")
if kind in VALID and not reason.strip():
    sys.exit("refusing: kind needs a written reason. A date with nothing behind "
             "it is `looked` promising a look that nothing records.")
if reason.strip() and len(reason) < 15:
    sys.exit("refusing: that reason is too short to be a finding. Say what the "
             "frame showed.")

rec = next((i for i in items if i["slug"] == slug), None)
if rec is None:
    ids = [i["slug"] for i in items]
    near = [s for s in ids if slug.split("-")[0] in s][:5]
    sys.exit(f"no record with slug {slug!r}." + (f" did you mean {near}?" if near else ""))

# You cannot look at an image that is not there.
#
# This guard exists because I wrote a finding against the wrong slug twice, and
# the second time the slug belonged to a *withdrawn* record - one with no cached
# file and no source - so the finding, a `looked` date and a rewritten caption
# all landed on a record that has no picture. Nothing caught it because the tool
# accepted whatever slug it was handed. Checking the file exists is the one test
# that would have caught it, and it is the definition of the operation: a lookup
# records the result of opening a file.
if not rec.get("local"):
    why = "no cached file" if not rec.get("src") else "no cached file yet (source only)"
    sys.exit(f"refusing: {slug!r} has {why}, so there is nothing to look at. "
             "This record is withdrawn or unfetched. If you meant a different "
             "record, read the slug off the manifest rather than typing it from "
             "memory - `python tools\\look.py --list` prints the openable ones "
             "with their local filenames.")

prev = (rec.get("kind"), rec.get("looked"), rec.get("note"))
print(f"{slug}")
print(f"   was     kind={prev[0]!r} looked={prev[1]}")
print(f"   reason  {reason}")
if NOTE:
    print(f"   note    {NOTE}")

rec["kind"] = kind
if kind == "unchecked":
    # Downgrading must not leave a `looked` date behind. A record that is
    # unchecked and dated says "somebody opened this and concluded nothing",
    # which is a different and weaker claim than "not yet examined", and it is
    # the kind of field that gets read as evidence by the next person. Clear it.
    rec.pop("looked", None)
    rec.pop("look_reason", None)
else:
    rec["looked"] = date.today().isoformat()
    rec["look_reason"] = reason
if NOTE:
    rec["note"] = NOTE
if kind == "unchecked":
    rec.pop("note", None)
if CAPTION:
    old = rec.get("caption")
    rec["caption"] = CAPTION
    if old and old != CAPTION:
        print(f"   caption WAS: {old}")
        print(f"   caption NOW: {CAPTION}")
        rec["caption_corrected"] = {
            "from": old,
            "date": date.today().isoformat(),
            "why": reason,
        }

if not APPLY:
    print("\n(dry run - pass --apply to write)")
    sys.exit(0)

MAN.write_text(json.dumps(man, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
n = sum(1 for i in items if i.get("looked"))
print(f"\nwritten. looked: {n} of {len(items)}")