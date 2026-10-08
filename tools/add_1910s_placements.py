# -*- coding: utf-8 -*-
"""Place the six entries added by `add_1910s_entries.py` in the taxonomy.

Placements are arguments, not labels, and the six below are written the way
`american-gothic`, `queen-for-a-day` and `nancy-drew` were: name the shelf,
quote the part of its own definition that decides it, then state the
counter-argument and why it loses. Three of the six are contestable on purpose
(`mona-lisa-theft`, `the-fan-magazine`, `war-of-the-worlds`, plus
`fireside-chats`, which has two defensible shelves) and each says so, because
`verify_taxonomy.py` can check that a category exists and that a sub-category
belongs to it, and cannot check that the placement is right.

Two decisions worth recording:

  the-fan-magazine is filed `institution/platform` rather than `persona/idol`,
  which is where `fan-mail` sits. Filed by the target, the two would be the
  same placement twice; filed by what the magazine *was* - the party holding
  the address, the rationing and the printing while neither the reader nor the
  performer was in the room - it is the earliest instance of the structure
  YouTube now runs. The alternative is named in the `why`.

  fireside-chats is filed `persona/presenter` rather than `persona/sovereign`
  or `cosmology/scheduling`. `sovereign` fails its own test: the form did not
  transfer to the next office-holder. `scheduling` needs the slot to outlast
  the content, and here the content is the entry.

Usage:  python tools/add_1910s_placements.py            (dry run)
        python tools/add_1910s_placements.py --apply
"""

import json
import pathlib
import sys

APPLY = "--apply" in sys.argv
P = pathlib.Path("data/taxonomy_placements.json")

PLACEMENTS = {
    "mona-lisa-theft": {
        "cat": "persona",
        "sub": "idol",
        "why": (
            "Filed `persona/idol`, and the shelf's own definition carries the "
            "reason: a figure \"at enough distance that the work is mostly "
            "finished before you arrive\" holding \"a public image that the "
            "person is not required to maintain for you.\" The painting was "
            "finished four centuries before this entry opens and is required "
            "to maintain nothing for anybody, which is maximum distance "
            "rather than a special case. **The placement is contestable and "
            "is recorded as contestable.** The strongest counter is "
            "`companion/object` - \"attachment to a thing with no agency at "
            "all\" - and that shelf's own note records that it is empty and "
            "asks whether the site has simply not been looking: a crowd "
            "queued in front of four iron hooks is close to exactly that. "
            "`idol` wins because the queue was not for an object with no "
            "agency but for a face. What the crowd had was a public image, "
            "and the whole effect of the theft was to turn a painting into "
            "something a century could recognise and queue for. The second "
            "counter, `character/historic-as-character`, is the weaker one: "
            "Lisa Gherardini was certainly flattened into a type, but this "
            "entry is about the crowd rather than about the flattening, and "
            "the shelf's test asks whether the real biography would survive "
            "contact with the type, which is not the question the theft "
            "raises. Reciprocity left unset - `directed` is the site default "
            "and applies here without argument, since a painting attaches "
            "back to nobody in either direction."
        ),
    },

    "the-fan-magazine": {
        "cat": "institution",
        "sub": "platform",
        "why": (
            "Filed `institution/platform` - \"the intermediary that is also "
            "the relationship\" - on the test the shelf states: \"Is somebody "
            "other than you and the performer in a position to change what "
            "happens between you?\" The magazine held the address, the "
            "rationing and the printing, and the performer was never in the "
            "exchange at all. The shelf's `not` separates platform from club "
            "and from brand precisely by saying the platform's "
            "distinguishing property is that it is \"infrastructure for "
            "somebody else's attachment\", which is what a correspondence "
            "department with a published Chicago address and a refused studio "
            "list is. **This is the earliest platform in the corpus: the "
            "structure YouTube now runs, run by a monthly with a rate card "
            "and a stamped-envelope rule.** Contestable and recorded as "
            "such. `persona/idol` is how `fan-mail` is filed - by the target "
            "rather than by the channel - and that is the consistent "
            "alternative if the shelf is read narrowly; it is rejected here "
            "because filing the channel by its target is what hides the "
            "channel, and the channel is the whole entry. "
            "`institution/fandom-body` is the third candidate and fails the "
            "shelf's own test: the magazine made no rule a reader could be "
            "held in good standing under. Reciprocity left unset, though "
            "`simulated` is defensible for a department whose replies were "
            "designed to read as conversation."
        ),
    },

    "mary-pickford": {
        "cat": "persona",
        "sub": "idol",
        "why": (
            "Filed `persona/idol`, which is the shelf built for this case: "
            "\"Musicians, film stars, athletes... The tie is to a body of "
            "work and a public image that the person is not required to "
            "maintain for you.\" Pickford is the earliest performer in the "
            "corpus whose public image is demonstrably converted into "
            "contract terms, and the entry's argument is that the tie was "
            "priced rather than merely felt. The shelf's test - did they make "
            "the thing, and is there a version of them that exists whether or "
            "not anyone is watching - passes on both halves: she made the "
            "pictures, and the version of her circulating through covers and "
            "fan worship existed independently of any audience present. "
            "`persona/sport-figure` fails because the tie is not to a role "
            "that transfers between holders; `persona/sovereign` fails its "
            "own test, since there is no office here and nothing passed to a "
            "successor. Reciprocity left unset: `directed` holds, and the "
            "reply the entry quotes was written by a studio rather than "
            "attached back to anybody."
        ),
    },

    "charlie-chaplin": {
        "cat": "persona",
        "sub": "idol",
        "why": (
            "Filed `persona/idol` for the reason Pickford is, with the "
            "difference the entry exists to state: the work here is not only "
            "finished before you arrive, it is *reusable* - a costume, a "
            "disguise, an address and a contest category, all of them "
            "operated by other people without him. The shelf's test asks "
            "whether there is a version of the person that exists whether or "
            "not anyone is watching; by 1917 his was being worn by strangers "
            "he had never met, which is the idol case with the distance "
            "turned into infrastructure. `persona/creator` fails - there is "
            "no recurring slot of his own making. `character/played-role` "
            "fails, and the look-alike contests are the evidence: that shelf "
            "needs the audience to hold the actor and the character as two "
            "attachments of different weight, and an audience paying to look "
            "like him was holding exactly one. Contest is the section rather "
            "than a category here, and it is the right one - the contests and "
            "the disputed anecdote are public argument about a person not in "
            "the room. Reciprocity left unset; `directed` holds."
        ),
    },

    "war-of-the-worlds": {
        "cat": "cosmology",
        "sub": "scheduling",
        "why": (
            "Filed `cosmology/scheduling` - \"a repeated slot that becomes a "
            "container for the tie\" - because what this entry argues is a "
            "property of the hour rather than of the script. The Mercury "
            "Theatre was a weekly Sunday slot, and everything the entry "
            "claims follows from when it aired: listeners arrived by turning "
            "the dial away from the most popular programme of the week, they "
            "arrived late enough to miss the sentence that would have told "
            "them, and the consequence was assembled by the schedule. "
            "`radio-serials`, `soap-opera` and `film-serial` sit on this "
            "shelf for the same reason - the container is the finding - and "
            "this is the same case with a one-hour payload. Contestable and "
            "recorded as such. `persona/presenter` is the sharper reading of "
            "a fake bulletin, since that shelf is \"the purest case of "
            "Horton's direct address: the illusion is engineered, and it "
            "works because it is engineered\"; it fails only because its test "
            "asks that an institution put a *person* there and that the "
            "person speak in the second person on a schedule, and the "
            "audience was never given a name to address. "
            "`character/fictional-protagonist` is the third and fails the "
            "shelf's own promise: that one is available to unlimited people "
            "at once and cannot be contradicted, and this text was "
            "contradicted on air four times."
        ),
    },

    "fireside-chats": {
        "cat": "persona",
        "sub": "presenter",
        "why": (
            "Filed `persona/presenter`: \"The one who addresses you "
            "directly... in second person... The purest case of Horton's "
            "direct address: the illusion is engineered, and it works because "
            "it is engineered.\" This entry's whole spine is that the "
            "informality was written into the text rather than felt by the "
            "speaker, which is that shelf's thesis stated as evidence. The "
            "test passes on both halves - an institution put him on the air, "
            "and the address is second person on a schedule - and the shelf's "
            "distinction from `persona/creator` is the one that matters: he "
            "did not generate this address, he was assigned it. Contestable, "
            "and recorded as such, because two other shelves are defensible. "
            "`persona/sovereign` is the counter worth taking seriously - he "
            "is a head of state and the shelf is built for exactly that - but "
            "it fails sovereign's own test, \"Does the attachment survive an "
            "election?\": this form was not inherited by the next "
            "office-holder and is not running now, so the object was the "
            "voice rather than the office, which is the idol/presenter side "
            "of the line the taxonomy itself draws. `cosmology/scheduling` "
            "is the third and the weakest: that shelf needs the slot to "
            "outlast the content, and here the content is the entry. "
            "Reciprocity left unset; `directed` holds, and the entry's "
            "argument is that nobody in the audience could answer."
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
