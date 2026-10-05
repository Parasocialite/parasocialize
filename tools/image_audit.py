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
import struct
import sys
from collections import Counter

ROOT = pathlib.Path(__file__).resolve().parent.parent
MAN = ROOT / "data" / "images.json"
man = json.loads(MAN.read_text(encoding="utf-8"))
items = man.get("items", [])

# `withheld` joins the other three: the picture is real and licensed and must
# not be shown. It is checked separately below, because a refusal needs evidence
# of the refusal - a null `local` and a written reason - where the other three
# need evidence of the claim.
VALID = {"exact", "illustrative", "unchecked", "withheld"}

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
    # `withheld` is a fourth kind, and it is the only one whose meaning is a
    # refusal rather than a claim. The picture is real and freely licensed and
    # must not be shown - 8432d33b1d39ab is a Replika conversation in which the
    # bot returns an enumerated list of suicide methods, and it was rendering on
    # eleven pages as decoration. It earns its place by requiring all three
    # things a claim-kind requires and one more: `local` must be null, so
    # img_for() cannot return it, and the reason must be written down, so the
    # next person reads why instead of re-fetching it.
    if kind == "withheld":
        if i.get("local"):
            problems.append(f"{slug}: kind='withheld' but local="
                            f"{i['local']!r} is still set - a withheld image "
                            f"that a page can still reach is not withheld")
        if not (i.get("withdrawn_reason") or "").strip():
            problems.append(f"{slug}: kind='withheld' with no "
                            f"`withdrawn_reason` - a refusal nobody can read is "
                            f"indistinguishable from a mistake")
    if i.get("local") and not (ROOT / i["local"]).exists():
        problems.append(f"{slug}: local={i['local']!r} is not on disk")
    # generation.size is what the model emitted and stays that; generation.final
    # is the file a reader will actually open. Every generated file was
    # margin-trimmed after generation, so all 7 records said 1152x560 about a
    # 1084x528 file and only the-dog recorded the trim in `crop`. A recorded size
    # that does not describe the file is the same defect as `kind: exact`
    # derived from a filename - the field is not wrong, it is answering a
    # different question than the one a tool reading it will ask.
    gen = i.get("generation")
    if gen and i.get("local") and (ROOT / i["local"]).exists():
        f = ROOT / i["local"]
        raw = f.read_bytes()
        if raw[:8] == b"\x89PNG\r\n\x1a\n":
            actual = "%dx%d" % struct.unpack(">II", raw[16:24])
            if not gen.get("final"):
                problems.append(f"{slug}: generation has no `final` size - the "
                                f"file on disk is {actual}")
            elif gen["final"] != actual:
                problems.append(f"{slug}: generation.final={gen['final']!r} but "
                                f"the file is {actual}")
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

# ---- one picture, two records -------------------------------------------
#
# Invisible to every other check in this file. Both files exist, both carry a
# licence and a page and a credit, both captions can be individually true, and
# both can be opened and judged independently. What nobody can see is that the
# judgement was recorded twice for one image - so a caption corrected on one
# copy leaves the other still asserting the thing that was just corrected, and
# the next person opens a picture that has already been looked at and trusts a
# finding that is one version behind.
#
# That is not hypothetical. t8-6-powerrangers and moment-power-rangers are the
# same Camp Conival panel under two different Commons pages, byte-identical,
# both captioned "The cast of the Power Rangers film". The caption was corrected
# on the first and the second kept the false claim through the correction and
# through two commits. The two Taylor Swift records are the same picture the
# same way. Hashing the bytes is the only thing that sees it.
import hashlib

by_digest = {}
for i in items:
    loc = i.get("local")
    if not loc:
        continue
    f = ROOT / loc
    if not f.exists():
        continue
    digest = hashlib.sha256(f.read_bytes()).hexdigest()
    by_digest.setdefault(digest, []).append((i.get("slug"), loc))
dupes = {k: v for k, v in by_digest.items() if len(v) > 1}
duplicate_notes = []
for digest, group in sorted(dupes.items(), key=lambda kv: kv[1][0][0] or ""):
    slugs = ", ".join(s for s, _ in group)
    files = ", ".join(pathlib.Path(l).name for _, l in group)
    caps = {str(x.get("caption") or "") for x in items
            if x.get("slug") in {s for s, _ in group}}
    if len(caps) > 1:
        kinds_here = {x.get("kind") for x in items
                      if x.get("slug") in {s for s, _ in group}}
        # Two copies of one picture cannot both be `exact` if they disagree -
        # exact means pixels settled it, and there is one set of pixels. That
        # is a live false claim.
        #
        # Two copies that both cap at `illustrative` and word themselves
        # differently are NOT a defect, and this check was wrong about that for
        # one run. Naming a person in an illustrative caption is the site's own
        # convention: `kind: illustrative` is the field that says src did the
        # identifying rather than the frame, which is exactly the Taylor Swift
        # case in item 22. So differing detail between two illustrative copies
        # is allowed, and the only thing worth printing is that they differ.
        if "exact" in kinds_here:
            problems.append(f"{slugs}: one identical picture "
                            f"({files}, sha256 {digest[:12]}) described two "
                            f"different ways, and at least one record claims "
                            f"`exact` - exact means the frame settled it, and "
                            f"one set of pixels cannot settle two captions")
        else:
            duplicate_notes.append(f"{slugs}: one picture reused across two "
                                   f"subjects ({files}); captions differ in "
                                   f"detail but both cap at {sorted(kinds_here)}, "
                                   f"which is the site's convention for a name "
                                   f"the frame cannot establish")
    else:
        # Legitimate: one picture serving two subjects, described the same way
        # both times. Worth knowing, not a defect.
        duplicate_notes.append(f"{slugs}: one picture reused across two "
                               f"subjects ({files}), captions agree")

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
if duplicate_notes:
    print(f"  {len(duplicate_notes)} reused picture(s) - not defects, but the")
    print("  captions have to agree across copies and only hashing finds that:")
    for n in duplicate_notes[:10]:
        print(f"    NOTE: {n}")
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