"""image_audit.py - is an image record telling the truth about what it shows?

Found while trying to build the encyclopedia image layer, which has zero records.
The layer cannot be built on this pipeline, and the reason is a single line:

    tools/images.py:306    src, kind = None, "exact"

`kind` defaults to `"exact"` and is only downgraded to `"illustrative"` when the
query falls through to the Flickr topic fallback. **Nothing in that path ever
looks at the picture.** So `exact` - which means *the photograph shows the thing
itself* - was derived entirely from a must-term appearing somewhere in a
filename. Forty live records carried it.

Probing four encyclopedia subjects, every one of which passed the must-term
filter, and looking at the result rather than the title:

    elvis        "Elvis Presley, Bob Neal, and Sam Phillips in 1955"   correct
    prince       "Prince, People au Defile Channel, Printemps-Ete 2010" CORRECT -
                 judged wrong from the title, and looking corrected it. That
                 was the only one of four that was right.
    cobain       "Courtney Love Frances Bean Cobain 2015"   a photograph of
                 Courtney Love and Dave Grohl. "Cobain" is the daughter's name.
    nick-drake   "Drake1"                                    a churchyard
    p            "Pygmalion, Alan Thornhill"                 a Putney Sculpture
                 Trail plaque; a sculpture there happens to be named Pygmalion
    cervantes    "pila bautismal de Miguel de Cervantes"    his baptismal
                 font - a genuine artefact, but not a portrait

**Three of four wrong, after passing a filter whose stated job is to exclude
exactly that.** The must-term test is necessary and nowhere near sufficient: it
establishes that a word is in the filename, not that the file shows the subject.

This is the fourth instance of the family this site already knows by name - a
field that promises more than it keeps, after `verified: true` with no source,
`status: retrievable` with no URL, and an `anchored` key printed to readers as if
it were a citation. Each was found by reading a status field's own values, not
by a gate, because the gate was checking the field against itself.

So the honest order is the one already used for the 94 unopenable `retrievable`
records: **correct the false claim first, keep the debt visible.** Every record
is downgraded to `unchecked`, which promises nothing, and a record only becomes
`exact` or `illustrative` again once somebody has looked at the file and written
down the date. Nothing is deleted and no image is removed - the pictures are
mostly fine, the *claim* about them is what was false.

    python tools\\image_audit.py
"""
from __future__ import annotations

import json
import pathlib
import re
import sys
from collections import Counter

ROOT = pathlib.Path(__file__).resolve().parent.parent
MAN = ROOT / "data" / "images.json"
man = json.loads(MAN.read_text(encoding="utf-8"))
items = man.get("items", [])

VALID = {"exact", "illustrative", "unchecked"}

problems = []
for i in items:
    slug = i.get("slug") or "<no slug>"
    kind = i.get("kind")
    looked = i.get("looked")
    if kind not in VALID:
        problems.append(f"{slug}: kind={kind!r}, which is not one of {sorted(VALID)}")
        continue
    # The claim is the whole point of the field, so the field now requires the
    # evidence for the claim. `looked` is a date string written by whoever
    # opened the file.
    if kind in ("exact", "illustrative") and not looked:
        problems.append(f"{slug}: kind={kind!r} with no `looked` date - nobody "
                        f"has opened this file, so the claim is not yet earned")
    if i.get("local") and not (ROOT / i["local"]).exists():
        problems.append(f"{slug}: local={i['local']!r} is not on disk")
    src = i.get("src") or {}
    if i.get("local"):
        for k in ("licence", "page", "credit"):
            if not src.get(k):
                problems.append(f"{slug}: cached image with no src.{k} - a file "
                                f"with no licence and no source page is the "
                                f"unattributable case")
    # A caption describes what is IN THE FRAME. A caption that describes the
    # story instead is a caption the reader cannot check against the picture.
    if i.get("caption") and re.search(r"\b(parasocial|bond|attachment|one-sided)\b",
                                      i["caption"], re.I):
        problems.append(f"{slug}: caption appears to describe the story rather "
                        f"than the frame: {i['caption'][:60]!r}")

kinds = Counter(i.get("kind") for i in items)
fors = Counter(i.get("for") for i in items)
looked = sum(1 for i in items if i.get("looked"))

print("=" * 68)
print("IMAGE RECORD AUDIT")
print("=" * 68)
print(f"  {len(items)} records")
print(f"  by kind   : {dict(kinds)}")
print(f"  by subject: {dict(fors)}")
print(f"  with a `looked` date: {looked}")
print()
if problems:
    print(f"  {len(problems)} problem(s):")
    for p in problems[:40]:
        print("    PROBLEM:", p)
    if len(problems) > 40:
        print(f"    ... and {len(problems) - 40} more")
    raise SystemExit(f"image audit: {len(problems)} problems")
print("  every record that claims what a photograph shows has been opened and")
print("  dated, and every cached file has a licence and a source page.")
print()
print("  NOTE what this does not check: that the picture is a *good* picture,")
print("  or even that it is related to the subject. Those are judgements, and")
print("  they are recorded in `looked` by whoever made them. A gate can hold a")
print("  field to its promise; it cannot make the promise true.")