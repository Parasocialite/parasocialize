# -*- coding: utf-8 -*-
"""Place the six entries added by `add_second_media_batch_entries.py`.

Placements are arguments, not labels. Each `why` below names the shelf, quotes
the part of its own definition that decides it, then states the counter-argument
and why it loses. `verify_taxonomy.py` can check that a category exists and that
a sub-category belongs to it; it cannot check that the placement is right, so
the contestable ones say so on purpose.

Three decisions worth recording up front:

  `the-icon` (787) is filed `divine/christ`, which is the shelf whose test is
  own-words identical to what the icon is for: "the relationship expressed by
  being addressed rather than by being watched, and the other end understood to
  hear." That is proskynesis. The icon was never a work encountered at a
  distance from an idol - it was a being kissed, carried in procession and
  argued about for a century, and the whole of the iconoclastic controversy is
  the `not` of the idol shelf ("a persona, who is addressed as a performer")
  refusing to let the image be one.

  `babe-ruth` (1927) is filed `persona/idol` against the obvious `sport-figure`
  alternative, and the reason is the shelf's own `not`: "an athlete is the one
  persona whose object is in motion." Ruth's 60 in 1927 is a finished body of
  work - the thing the papers built was already made before the audience
  arrived, and the ghostwritten bylined columns are the idol machinery (a
  publicist-printed reply) operating directly. Filed `persona/idol`,
  contestable, and the counter is argued in full.

  `the-confessional-booth` (1992) is filed `institution/platform` against
  `persona/presenter`, and the platform's `not` decides it: the booth "sits
  between you and the person you are attached to" the way a church or club
  does not. The present-tense address is real and points at the presenter
  reading; the reason it loses is that the entry is not about a speaker, it is
  about the machinery that manufactured the address.

Usage:  python tools/add_second_media_batch_placements.py        (dry run)
        python tools/add_second_media_batch_placements.py --apply
"""

import json
import pathlib
import sys

APPLY = "--apply" in sys.argv
P = pathlib.Path("data/taxonomy_placements.json")

PLACEMENTS = {
    "the-icon": {
        "cat": "divine",
        "sub": "christ",
        "why": (
            "Filed `divine/christ`, on the shelf's own test: \"Is the "
            "relationship expressed by being addressed rather than by being "
            "watched, and is the other end understood to hear?\" The icon is "
            "not watched; it is venerated, kissed, carried in procession and "
            "censed, and the Second Council of Nicaea's own formula - \"the "
            "honour paid to the image passes to the prototype\" - states "
            "outright that the address is aimed through the panel at a being "
            "understood to hear it. That is the shelf, not a metaphor. The "
            "counter is `persona/idol`: an image encountered at a distance, "
            "whose defining property is exactly the one the iconoclasm "
            "controversy was fought over. The idol's `not` says \"a persona, "
            "who is addressed as a performer and could be anywhere else\", and "
            "that is precisely what ninety years of argument denied about the "
            "icon - it could not be anywhere else, because the point of it "
            "was that it was not a performer but a window onto a hearer. The "
            "paint alone was not the attachment and the dismissal of the "
            "image as merely painted timber invaded by no god is recorded as "
            "the losing argument, because the controversy's own outcome "
            "confirmed the addressed-behind-the-panel reading. Contestable, "
            "and recorded as such."
        ),
    },

    "sarah-bernhardt": {
        "cat": "persona",
        "sub": "idol",
        "why": (
            "Filed `persona/idol`, on the shelf's test: \"Did they make the "
            "thing, and is there a version of them that exists whether or not "
            "anyone is watching?\" Bernhardt made the performances, but the "
            "attachment documented in the entry is to the Divine Sarah, the "
            "figure who was met at the dock with homage \"usually reserved "
            "for royalty\" and whose name travelled ahead of her in a way no "
            "individual performance could. The shelf's mechanism is the "
            "entry's whole subject: \"a surface maintained by others - a "
            "label, a publicist, a tour\" - and the 1891 American tour is "
            "the surface moving. The counter is `character/played-role`: an "
            "actress and audiences attaching to the roles. It loses on the "
            "shelf's own `not`, which asks whether an actor can leave the "
            "costume and be noticed as themselves - and that is the test "
            "Bernhardt passes in the documented direction no one else on the "
            "site does: the audience's mourning would not have stopped if a "
            "different actress had played Camille, because the attachment "
            "was to the woman the papers called Divine, not to the character "
            "she held that night. The role was a plank on a larger surface. "
            "Contestable, and recorded as such."
        ),
    },

    "aimee-semple-mcpherson": {
        "cat": "persona",
        "sub": "presenter",
        "why": (
            "Filed `persona/presenter`, on the shelf's test: \"Did an "
            "institution put them there, and do they speak in the second "
            "person on a schedule?\" KFSG was owned and licensed to her "
            "Foursquare church, and the broadcast was the schedule; the "
            "\"Do you pledge\" exchange is the direct-address form the shelf "
            "names, aimed wholesale at listeners who could not answer. The "
            "contested line is the shelf's own `not`: \"Not a cleric, who "
            "addresses an assembly in person rather than an audience at a "
            "distance.\" Aimee was a cleric, and that is the counter-argument "
            "in full: `persona/idol` reads her as the celebrity evangelist, "
            "a figure at enough distance that the work precedes you. It loses "
            "precisely on the distinction the shelf draws - her ministry was "
            "performed to an audience a wavelength away, through an "
            "institution's transmitter, on a schedule, and the letters from "
            "other states documented in the entry are the reply side of a "
            "presenter's address, which a cleric addressing an assembly in "
            "person cannot collect. Her photograph with a headset was the "
            "foursquare era's newsroom portrait; the broadcaster is the "
            "presenter reading second-person grammar into a microphone. "
            "Contestable - the church itself would file her under shepherding "
            "rather than presenting - and that is the point of recording it."
        ),
    },

    "peanuts": {
        "cat": "character",
        "sub": "fictional-protagonist",
        "why": (
            "Filed `character/fictional-protagonist`, on the shelf's test: "
            "\"Is the figure available in more than one place at the same "
            "time, to people who have never met?\" Charlie Brown was in "
            "hundreds of newspapers at once, read by readers who had never "
            "met any of each other, and the strip's own argument is that the "
            "unrequited love is the figure's interior - \"the reader fills it "
            "in and cannot be corrected\", which is the shelf's mechanism and "
            "the entry's point about a character defined by a repeated "
            "failure to be answered. The counter is `persona/idol`: a made "
            "figure at a distance, image maintained by others. It loses on "
            "the idol's own `not`, which says \"Not a fiction\" - and the "
            "attachment here is unambiguously to a fiction, one whose "
            "specific claim (unrequited love as the shape of the strip) only "
            "a written character can carry, because a performer offers a "
            "version of themselves while Charlie Brown has no performer to "
            "leave the costume. The second half of the shelf's test is what "
            "separates him from a controlled property: Schulz died in 2000 "
            "and the audience's picture of Charlie Brown was not overridable "
            "by the estate's continuity strips, which is the pointed end of "
            "the entry."
        ),
    },

    "babe-ruth": {
        "cat": "persona",
        "sub": "idol",
        "why": (
            "Filed `persona/idol`, against the obvious `persona/sport-figure` "
            "reading, and the shelf's own `not` is the line: \"The athlete's "
            "object is in motion.\" Ruth's 60-home-run season in 1927 is a "
            "finished body of work - the record stood until Maris in 1961 and "
            "the attachment resolved onto a number and a legend, not onto a "
            "man currently playing. The test asks \"did they make the thing, "
            "and is there a version of them that exists whether or not anyone "
            "is watching\", and the entry's evidence is the ghostwritten "
            "bylined newspaper columns manufactured for him - a reply the "
            "paper-printed idol gave that the man never typed, which is the "
            "idol mechanism (\"a surface maintained by others\") operating at "
            "full power. The sport-figure counter is genuinely strong: the "
            "baseball audience does grieve the role, and transfer, retirement "
            "and injury are its recurring breaks. It loses here because the "
            "recorded attachment in the entry survived and stabilised on the "
            "finished achievement rather than on weekly performance - the 60 "
            "did not need Ruth to keep playing in order to keep being the "
            "object, and the papers built a persona that outlived his "
            "playing. Contestable, and the counter is recorded rather than "
            "hidden."
        ),
    },

    "the-confessional-booth": {
        "cat": "institution",
        "sub": "platform",
        "why": (
            "Filed `institution/platform`, on the shelf's test: \"Is somebody "
            "other than you and the performer in a position to change what "
            "happens between you?\" In the confessional, the production sits "
            "between cast member and viewer: editors choose which takes reach "
            "you, the confessional itself is a built room with a camera, and "
            "the \"looking straight into the lens\" convention is the "
            "platform's own ranking - deciding which fragments of the "
            "performer you see and which are buried. The shelf's `not` is "
            "verbatim the case: \"not a club, a church, which does not sit "
            "between you and the person you are attached to\" - the booth "
            "literally does, which is why it is `institution` and not the "
            "persona reading. The counter is `persona/presenter`: a speaker "
            "addressing you in the second person on a schedule. It loses "
            "because the entry is not about a presenter - the cast member "
            "does not speak because an institution assigned them the slot, "
            "they speak because the machinery extracts it - and the "
            "presenter's own defining constraint (\"the intimacy is a job "
            "function with a shift behind it\") attaches to the operators, "
            "not to the cast. The booth is infrastructure for somebody "
            "else's attachment, which is the platform mechanism, and the "
            "genre adopted the room as a convention across shows precisely "
            "because the machinery was the product."
        ),
    },
}


def main():
    raw = P.read_bytes()
    ent = json.loads(raw.decode("utf-8"))

    rebuilt = (json.dumps(ent, ensure_ascii=False, indent=2)
               .replace("\n", "\r\n") + "\r\n").encode("utf-8")
    if rebuilt != raw:
        sys.exit("refusing: data/taxonomy_placements.json is not the "
                 "CRLF/indent-2 form with a trailing newline this script "
                 "round-trips; nothing written")

    before_keys = sorted(ent)
    asg = ent["assignments"]
    was_sorted = list(asg) == sorted(asg)
    before_n = len(asg)
    present = [k for k in PLACEMENTS if k in asg]
    if present:
        print(f"  (replacing {len(present)} assignment(s) already present)")

    tax = json.loads(pathlib.Path("data/taxonomy.json").read_text(
        encoding="utf-8"))
    subs = {a["id"]: {s["id"] for s in (a.get("sub") or [])}
            for a in tax["attachment"]}

    for eid, rec in PLACEMENTS.items():
        if rec["cat"] not in subs:
            sys.exit(f"refusing: {eid} names an unknown category {rec['cat']!r}")
        if rec["sub"] not in subs[rec["cat"]]:
            sys.exit(f"refusing: {eid} - {rec['sub']!r} is not a sub-category "
                     f"of {rec['cat']!r}")
        if list(rec) != ["cat", "sub", "why"]:
            sys.exit(f"refusing: {eid} has keys {list(rec)}")
        if not rec["why"].strip() or len(rec["why"]) < 200:
            sys.exit(f"refusing: {eid} has no argument in its why")

    asg.update({k: dict(v) for k, v in PLACEMENTS.items()})
    if was_sorted:
        ent["assignments"] = dict(sorted(asg.items()))

    if sorted(ent) != before_keys:
        sys.exit("refusing: top-level keys changed")
    if len(ent["assignments"]) != before_n + len(PLACEMENTS) - len(present):
        sys.exit("refusing: assignment count moved by more than the additions")

    print(f"\n  {'APPLY' if APPLY else 'DRY RUN'}: {before_n} -> "
          f"{len(ent['assignments'])} assignments"
          f"{' (kept alphabetical order)' if was_sorted else ' (order kept)'}")
    for eid in PLACEMENTS:
        r = ent["assignments"][eid]
        print(f"    {eid:20s} {r['cat']}/{r['sub']:<24s} why {len(r['why'])}ch")

    if not APPLY:
        print("\ndry run. re-run with --apply")
        return

    out = json.dumps(ent, ensure_ascii=False, indent=2).replace("\n", "\r\n")
    P.write_bytes(out.encode("utf-8") + b"\r\n")

    again = P.read_bytes()
    if not again.endswith(b"\r\n"):
        sys.exit("refusing: lost the trailing newline")
    reparsed = json.loads(again.decode("utf-8"))
    if sorted(reparsed) != before_keys:
        sys.exit("refusing: top-level keys changed after write")
    print(f"\nwrote {P} ({len(again)} bytes, {before_n} -> "
          f"{len(reparsed['assignments'])} assignments)")


if __name__ == "__main__":
    main()