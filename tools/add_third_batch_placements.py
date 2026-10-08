# -*- coding: utf-8 -*-
"""Place the three entries added by `add_third_batch_entries.py`.

Placements are arguments, not labels. Each `why` below names the shelf, quotes
the part of its own definition that decides it, then states the counter-argument
and why it loses. `verify_taxonomy.py` can check that a category exists and that
a sub-category belongs to it; it cannot check that the placement is right, so
the contestable ones say so on purpose.

Three decisions worth recording up front:

  `clara-bow` (1927) is filed `persona/idol` against `character/played-role`,
  and the shelf's test contains the answer in its own second sentence: "If the
  work was assembled for them, they are still a persona but the manufacturing is
  the story - see the manufactured teen idol and the boy band." Paramount
  assembled the It Girl out of a novelist's definition, a five-year contract and
  a kept count of the reply, so the manufacturing is not a disqualifier here, it
  is the entry.

  `greta-garbo` (1932) is filed `persona/idol`, and the counter
  `character/played-role` is the strongest form it can take: the sentence
  everyone quotes belongs to Grusinskaya, and the AFI ranked the character's
  line, not the actress's. It loses because the split resolved onto the person
  - Garbo corrected the sentence herself in 1955 and the correction did not
  take, which is the idol mechanism ("a surface maintained by others") failing
  to need her presence in order to keep working.

  `edgic` (2002) is filed `institution/fandom-body` against
  `institution/platform`, and the fandom-body's test decides it: the rating key
  was written by forum members in threads and never by the software, and the
  community acts on outsiders - it split over the spoiler rule and founded a
  successor forum, which is "canons, rules, officers and schism" performed
  literally. The entry itself already argues why it is filed as an institution
  rather than as a tie; the contest left is which institution.

Usage:  python tools/add_third_batch_placements.py        (dry run)
        python tools/add_third_batch_placements.py --apply
"""

import json
import pathlib
import sys

APPLY = "--apply" in sys.argv
P = pathlib.Path("data/taxonomy_placements.json")
ENTRIES = pathlib.Path("data/encyclopedia.json")

PLACEMENTS = {
    "clara-bow": {
        "cat": "persona",
        "sub": "idol",
        "why": (
            "Filed `persona/idol`, on the shelf's test: \"Did they make the "
            "thing, and is there a version of them that exists whether or not "
            "anyone is watching?\" Bow made the performances, and the entry's "
            "whole subject is the version that outlasts them: Paramount signed "
            "her in 1926, cast a novelist's definition onto her face in 1927 "
            "and released six pictures with her that year, so the It Girl was "
            "finished business before any member of the audience arrived - "
            "which is the idol's `not` word for word, \"the work is finished "
            "before you get there, so you are never present for the making.\" "
            "The shelf's test anticipates the objection this entry is built "
            "on: \"If the work was assembled for them, they are still a "
            "persona but the manufacturing is the story - see the "
            "manufactured teen idol and the boy band.\" That is Clara Bow, "
            "manufacturing and all - a five-year deal signed 16 August 1926 "
            "with bonuses held in trust against a morals clause, a label in "
            "the novelist's word 'It', and a publicist in the studio that "
            "kept the count of a reply it could sell against, which is the "
            "shelf's mechanism (\"a surface maintained by others\") running "
            "on schedule. The counter is `character/played-role`: an actress, "
            "and a 1927 audience attaching to the flapper on the screen, with "
            "Dorothy Arzner's \"automatically a natural\" as the case that "
            "the thing was in the woman rather than in the apparatus. It "
            "loses on that shelf's own `not`, which asks whether the "
            "performer is \"legible as a person\" apart from the costume - "
            "and every recorded act of attachment in this entry clears her "
            "costume: forty-five thousand letters were addressed to her in "
            "one month, the henna was copied off her body rather than off a "
            "role, and the nickname stuck to Bow rather than to any character "
            "she played. The role was a plank on a larger surface, and the "
            "surface was the thing the studio counted. Contestable, and "
            "recorded as such."
        ),
    },

    "greta-garbo": {
        "cat": "persona",
        "sub": "idol",
        "why": (
            "Filed `persona/idol`, on the shelf's test: \"Did they make the "
            "thing, and is there a version of them that exists whether or not "
            "anyone is watching?\" Garbo made the pictures, and the version "
            "that exists when nobody is watching is this entry's subject: in "
            "1955 LIFE could only describe it in her absence, thirteen years "
            "past her last film, assembled out of \"furtive comings and "
            "goings\" and refusals the audience had been allowed to watch her "
            "make. The idol's mechanism is \"a surface maintained by others - "
            "a label, a publicist, a tour\", and this record names both "
            "maintainers in one sentence: a press that coined the Swedish "
            "Sphinx and a studio that, in the entry's words, \"eventually "
            "capitalised\" on the refusal because it bolstered the image. The "
            "counter is `character/played-role`, and it takes the strongest "
            "form available - the sentence everyone quotes belongs to "
            "Grusinskaya in a picture that won Best Picture, and the AFI "
            "ranked the line thirtieth among a century's quotes in 2005, so "
            "the split between actress and part is real and documented. It "
            "loses because the split resolved, in the documented direction, "
            "onto the person: Garbo corrected the sentence in 1955 (\"I only "
            "said, I want to be let alone! There is all the difference\") and "
            "the correction did not take - the accounts read for this entry "
            "in 2017 and 2019 both still open with the line she denied, and "
            "the press kept attaching the Sphinx to the woman rather than to "
            "any role she held. The idol's `not` - \"the work is finished "
            "before you get there, so you are never present for the making\" "
            "- is why the correction could not land: by 1955 she was exactly "
            "what the shelf describes, a surface that no longer needed her "
            "presence in order to go on working. Contestable, and recorded "
            "as such."
        ),
    },

    "edgic": {
        "cat": "institution",
        "sub": "fandom-body",
        "why": (
            "Filed `institution/fandom-body`, on the shelf's test: \"Does the "
            "group have rules that are not the platform's, and can it act on "
            "somebody who is not a member?\" Edgic answers both halves from "
            "the entry: the rating key - invisible, under the radar, middle "
            "of the road, complex personality, over the top, each with a tone "
            "and a visibility from one to five - was written by forum members "
            "in threads (the 2005 guidelines post still carries a roster of "
            "raters, KernelQ among them) and never by the software that "
            "carried it, so the rules are not the platform's; and the "
            "community acts outward constantly, scoring contestants who are "
            "not members and splitting its own membership over the spoiler "
            "rule, with a spoiler-free forum founded in response - which is "
            "the shelf's \"canons, rules, officers and schism\" performed "
            "literally rather than analogised. Its mechanism is an edge "
            "\"produced by the fans rather than the performer\", and edgic "
            "has no edge to the performer at all: the "
            "grade is written weekly for a person who will never read it, "
            "while the kept work - transcripts, visibility charts, a "
            "colour-coded chart for every season - is unpaid infrastructure "
            "for a relationship among the archivists themselves. The counter "
            "is `institution/platform`: the practice lives in the forum, the "
            "threads and moderation are the platform's, and the spoiler leaks "
            "that broke the unspoiled rule are a boundary no membership can "
            "enforce, which answers the platform's own test - \"Is somebody "
            "other than you and the performer in a position to change what "
            "happens between you?\" It loses on the platform's `not`, which "
            "keeps \"an institution in the older sense - a club, a church\" "
            "precisely because it \"does not sit between you and the person "
            "you are attached to\" - and here there is no performer on the "
            "far side to intermediate, because what attaches is the group's "
            "own rule and the table its volunteers keep. You do not migrate "
            "a platform; you migrate a membership, and the successor forum "
            "that rebuilt the archive past two thousand members did exactly "
            "that. Contestable, and recorded as such."
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

    enc = json.loads(ENTRIES.read_text(encoding="utf-8"))
    have = {e["id"] for e in (enc["entries"]
                              if isinstance(enc, dict) else enc)}
    missing = [k for k in PLACEMENTS if k not in have]
    if missing:
        sys.exit(f"refusing: {missing} not in data/encyclopedia.json")

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
        print(f"    {eid:20s} {r['cat']}/{r['sub']:<16s} why {len(r['why'])}ch")

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
    if len(reparsed["assignments"]) != len(PLACEMENTS) + before_n - len(present):
        sys.exit("refusing: assignment count wrong after write")
    print(f"\nwrote {P} ({len(again)} bytes, {before_n} -> "
          f"{len(reparsed['assignments'])} assignments)")


if __name__ == "__main__":
    main()
