# -*- coding: utf-8 -*-
"""Place the six entries added by `add_media_entries.py` in the taxonomy.

Placements are arguments, not labels, and the six below are written the way
`american-gothic`, `queen-for-a-day` and the 1910s batch were: name the shelf,
quote the part of its own definition that decides it, then state the
counter-argument and why it loses. Four of the six are contestable on purpose
and each says so, because `verify_taxonomy.py` can check that a category exists
and that a sub-category belongs to it, and cannot check that the placement is
right.

Two decisions worth recording up front:

  The two vote entries (`edwin-drood` and `death-in-family`) are both filed
  `cosmology/canon`. Canon is where this corpus keeps the world that survives
  the people in it, and each `why` argues which half of the shelf's own
  `not` - "not a myth system, which has no canonical version" - the entry
  lands on. Filing them together is deliberate: they are the same manufactured
  consequence three years apart, and the pairing is what makes either readable.

  `marilyn-diptych` is filed `character/historic-as-character`, which is the
  shelf whose own note observes that the type is more common in the culture
  than in this corpus - the corporate pastel of a real woman wearing a role
  assigned after her death.

Usage:  python tools/add_media_placements.py            (dry run)
        python tools/add_media_placements.py --apply
"""

import json
import pathlib
import sys

APPLY = "--apply" in sys.argv
P = pathlib.Path("data/taxonomy_placements.json")

PLACEMENTS = {
    "rocky-horror": {
        "cat": "cosmology",
        "sub": "myth-system",
        "why": (
            "Filed `cosmology/myth-system`, on the shelf's own test: \"Is "
            "the story collective, and is it retold rather than read? If the "
            "corpus is carried by the community and there is no author to "
            "hold responsible for it.\" The film is a fixed text - one "
            "version somebody could be faithful to - but the thing this entry "
            "is about is not the film, it is the delivery, which is carried "
            "by the crowd that turns up and has no owner. The callbacks are a "
            "vernacular no script owns: the first documented one entered the "
            "repertoire as a stranger's shout at the Waverly in 1976, and the "
            "crowd enforces its own etiquette over newcomers. That is myth "
            "told in a room rather than read, and the shelf's `not` - \"a "
            "canon has one version somebody can be faithful to\" - names the "
            "counter-argument, which is the film, and thereby lands the "
            "entry on the myth side of the line the taxonomy itself draws. "
            "Contestable and recorded as such: `institution/fandom-body` has "
            "the stronger claim on the *organisation* - a regular audience "
            "with rules that are not the screen's - but it fails the shelf's "
            "own diagnostic, which requires the group to act on somebody who "
            "is not a member, and the midnight crowd polices the room, not "
            "the industry. Reciprocity left unset; directed is the site "
            "default, and a shout the screen cannot answer is the whole "
            "finding."
        ),
    },

    "edwin-drood": {
        "cat": "cosmology",
        "sub": "canon",
        "why": (
            "Filed `cosmology/canon`, on the shelf's test: \"Would the "
            "attachment survive losing everybody in it?\" Drood is the rare "
            "case where the answer is on the poster: the story's end is not "
            "carried by a fixed text but is created nightly by the audience's "
            "vote, and the production exists to keep a world standing no "
            "matter which characters are awarded which ending. The shelf's "
            "`not` about its neighbour - \"a canon has one version somebody "
            "can be faithful to\" - is exactly what the show manufactures: "
            "once the tally closes, that night's ending is a recorded version "
            "the cast must perform, and the industry's hedges (fixed results "
            "in some smaller companies, votes for the obvious culprit thrown "
            "out in some houses) exist to guarantee that each night produces "
            "exactly one canonical version. The counter-argument is that the "
            "ending changes every night and the thing therefore drifts, "
            "which is the myth-system account; it loses because the whole "
            "machinery - the tallying, the hedging, the rehearsed "
            "alternatives - exists to guarantee single versions, not to let "
            "the story wander. This is the deliberate partner of the "
            "telephone vote filed in the same shelf, the same manufactured "
            "consequence three years later. Contestable, and recorded as "
            "such."
        ),
    },

    "death-in-family": {
        "cat": "cosmology",
        "sub": "canon",
        "why": (
            "Filed `cosmology/canon`, on the shelf's test: \"Would the "
            "attachment survive losing everybody in it?\" The world here is "
            "the DC franchise, which outlasts every participant: the poll "
            "decided not a plot point but the permanent standing of a "
            "character inside a canon that predates and outlives the voters, "
            "and the editors prepared two versions so that whichever verdict "
            "won would be canonical from the moment the tally closed. The "
            "shelf's `not` decides it against its neighbour: \"a myth system "
            "has no canonical version\" - there is nothing mythic here, there "
            "is one authoritative text and an editor who knows what it says, "
            "which is precisely why the result had to be kept secret until "
            "the chosen issue shipped. The counter worth taking seriously is "
            "`institution/platform`: someone other than reader and character "
            "controlled the exchange and priced the vote at fifty cents. It "
            "fails because the platform's distinguishing property - "
            "\"infrastructure for somebody else's attachment\" - describes "
            "the telephone line, not the object of the attachment, which was "
            "a character in a canon; the entry's weight falls on a 72-vote "
            "alteration of what is officially true, not on the medium the "
            "calls ran through. Contestable, recorded as such, and "
            "deliberately paired with the stage vote filed beside it."
        ),
    },

    "marilyn-diptych": {
        "cat": "character",
        "sub": "historic-as-character",
        "why": (
            "Filed `character/historic-as-character`, on the shelf's test: "
            "\"Do you know the type, and would the real biography survive "
            "contact with it?\" The painted Marilyn is a type imposed on a "
            "dead woman - fifty copies of one publicity still, drained of "
            "colour - encountered through a role the silkscreen assigned "
            "after her death, and every accurate fact about the person is in "
            "tension with the pattern, which deletes the biography rather "
            "than surviving contact with it. The shelf's `not` speaks the "
            "entry's sentence: \"the person existed and the type was "
            "imposed, so every accurate detail is in tension with the "
            "attachment.\" The counter is `persona/idol`, where this corpus "
            "filed the empty-wall painting - a public image the person is "
            "not required to maintain. It loses on the shelf's own "
            "distinction: an idol is encountered through *the person's* "
            "image however distant, whereas here the manufacture went on "
            "after the person died and the imposition of the type is the "
            "subject rather than an incident. The deeper contest is "
            "`companion/object` - attachment to a thing with no agency at "
            "all - whose own note records that it is empty; fifty identical "
            "faces brush against it, but the object here is an image *of "
            "someone*, which is the historic-as-character test, not the "
            "object test. Contestable, and recorded as such."
        ),
    },

    "amos-n-andy": {
        "cat": "institution",
        "sub": "fandom-body",
        "why": (
            "Filed `institution/fandom-body`, on the shelf's test: \"Does "
            "the group have rules that are not the platform's, and can it act "
            "on somebody who is not a member?\" The audience that loved the "
            "show built its own machinery - a six-month newspaper campaign, a "
            "petition of more than 700,000 names to a regulator, an "
            "injunction attempt, a sponsor's boycott - and each act reached "
            "someone who was not a member of anything the audience owned, "
            "which is the shelf's criterion rather than a mere audience "
            "complaining. Opposition is not an objection to the placement: "
            "this is an organised public acting on the figure it is attached "
            "to, the fandom relationship in its political register. The "
            "counter that carries weight is `persona/idol`, because the "
            "attachment is to *voices*; and the `not` of that shelf - \"the "
            "idol's distinguishing property is distance\" - is exactly what "
            "the counter would claim, but the entry is not about the two "
            "performers, it is about the organised audience that answered the "
            "fiction they voiced. The `not` of this shelf - \"a fandom can "
            "hold a member in good standing, and a pile-on cannot\" - is "
            "decided by the petition and the boycott being durable and "
            "rules-bound rather than spontaneous. Contestable, recorded as "
            "such."
        ),
    },

    "marvel-letters-page": {
        "cat": "institution",
        "sub": "platform",
        "why": (
            "Filed `institution/platform`, on the shelf's test: \"Is "
            "somebody other than you and the performer in a position to "
            "change what happens between you?\" The letters page was the "
            "machinery between reader and writer: an office chose which "
            "letters to print, an editor wrote the answers, and a reader's "
            "name appeared beside a reply the performer never gave - the "
            "exchange could be rationed, delayed or cancelled somewhere the "
            "reader could not reach, which is the platform diagnostic. The "
            "shelf's `not` decides it against `persona/creator`: \"the "
            "moment the attachment is to the platform rather than the person, "
            "it moves to INSTITUTION\" - and the tell that the attachment "
            "was to the page is that the voice outlived its creator, passing "
            "to editors who were not the man who made it sound personal. "
            "Contestable, and recorded as such: filing by target "
            "(`persona/idol`, where the corpus sits `fan-mail`) is the "
            "consistent alternative and loses the way the 1911 fan-magazine "
            "placement lost it - filing the channel by its target is what "
            "hides the channel, and the channel is the entry. Same shelf, "
            "same argument, forty years later; the reply moved from a "
            "monthly with a stamped-envelope rule to a letters column with a "
            "No-Prize that was deliberately nothing."
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
    for eid in sorted(PLACEMENTS):
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