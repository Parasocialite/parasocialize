# -*- coding: utf-8 -*-
"""Place the three entries added by `add_fifth_batch_entries.py`.

Placements are arguments, not labels. Each `why` below names the shelf, quotes
the part of its own definition that decides it, then states the counter-argument
and why it loses. `verify_taxonomy.py` can check that a category exists and that
a sub-category belongs to it; it cannot check that the placement is right, so
the contestable ones say so on purpose.

Three decisions worth recording up front:

  `pamela` (1740) is filed `character/fictional-protagonist` against
  `character/mascot` and `persona/creator`. The mascot counter is real because
  the reception left objects behind - the "Pamela rage" put her on teacups and
  fans - but the shelf's own test is whether the audience can be WRONG about the
  figure, and the decade spent arguing "Pamelists and Antipamelists" is a
  positive answer: the audience supplied an interior the author could not
  correct, which is what Richardson's own sequel tried and failed to do.

  `mister-rogers` (1968) is filed `persona/presenter` against
  `persona/creator` and `character/mascot`, and creator is the stronger
  counter because Rogers wrote and produced the show rather than being handed
  the address. It loses on that shelf's own test - the recurring slot attaches
  to the programme, not the person - and on the presenter's not, because the
  intimacy was "a job function with a shift behind it" that ran thirty-three
  years. The puppets are the character shelf and are not the tie.

  `betty-crocker` (1921) is filed `institution/brand`, the shelf the
  `the-brand-as-character` mechanism itself sits on, because this is that
  mechanism's founding instance. The natural counter, `character/`, loses on
  the one half of the written-character test no author can survive - the
  audience cannot be overridden - and General Mills overrode every part of
  Betty by decision.

Usage:  python tools/add_fifth_batch_placements.py        (dry run)
        python tools/add_fifth_batch_placements.py --apply
"""

import json
import pathlib
import sys

APPLY = "--apply" in sys.argv
P = pathlib.Path("data/taxonomy_placements.json")
ENTRIES = pathlib.Path("data/encyclopedia.json")

PLACEMENTS = {
    "pamela": {
        "cat": "character",
        "sub": "fictional-protagonist",
        "why": (
            "Filed `character/fictional-protagonist`, on the shelf's test: "
            "\"Is the figure available in more than one place at the same "
            "time, to people who have never met?\" - and the second half of "
            "that test is what settles it, \"if no author can override what "
            "the audience says they feel\". Pamela is the rare case where the "
            "author tried and lost: the entry records that \"The audience's "
            "want bent the text.\" - the unauthorized continuations and "
            "parodies \"drew a sequel from Richardson himself, Pamela in her "
            "Exalted Condition, in 1742\". The def fits the form rather than "
            "the sales, \"Somebody described in a book and therefore "
            "available to an unlimited number of people at once, none of whom "
            "can be contradicted\", and the mechanism's first clause is the "
            "entry's whole structure, \"A fictional interior is an invitation "
            "with no host present\": the letters \"are written not to a lover "
            "but to Pamela's parents, who are offstage, at a distance, and "
            "never answer inside the book\", which hands the reader \"the "
            "seat of the parents - receiving every letter, sending none\". "
            "The counter is `character/mascot`, and it is real because the "
            "reception left objects behind - Pamela motifs on teacups and "
            "fans are a shop-shelf reading of the tie. It loses on that "
            "shelf's own test, \"Does the figure have an interior anybody "
            "could get wrong, or is it specified entirely by others?\" - the "
            "audience spent the decade disagreeing about her interior, "
            "dividing into \"Pamelists and Antipamelists\", and a figure a "
            "crowd can be wrong about is exactly the one \"with enough "
            "interior life that the audience fills it in and cannot be "
            "corrected\" - the mascot's `not` stated positively. The second "
            "counter is "
            "`persona/creator`, since the letters out of the book went to "
            "Richardson. It loses because what the book manufactures is "
            "\"a one-sided correspondence the reader reads from the parents' "
            "end\", and Richardson's sequel was an answer to Pamela's public "
            "rather than a creator's output being followed. Contestable, and "
            "recorded as such."
        ),
    },

    "mister-rogers": {
        "cat": "persona",
        "sub": "presenter",
        "why": (
            "Filed `persona/presenter`, on the shelf's test: \"Did an "
            "institution put them there, and do they speak in the second "
            "person on a schedule? Direct address plus an employer is the "
            "test.\" The def names the register outright - \"The one who "
            "addresses you directly, by name, in second person.\" - and here "
            "the second person is the show's title: \"Won't you be my "
            "neighbor?\" is a question the viewer answers by watching, on a "
            "public-television schedule, from a host the institution placed "
            "at the camera. The mechanism is the fit, because this was "
            "engineering knowingly rather than an accident, \"Second-person "
            "grammar aimed at a large audience is a machine for manufacturing "
            "the feeling of being singled out\", and the programme's own "
            "research is the receipt - \"the younger the child, the more "
            "interested they are in the program when my face is on the "
            "screen\" and \"the younger children might consider the "
            "television screen as another mother's face.\" That is Horton and "
            "Wohl's condition met exactly, \"triggered when a performer "
            "acknowledges the audience's presence\", except the audience was "
            "two years old. The counter is `persona/creator`, and it is the "
            "strong one, because Rogers wrote and produced the show rather "
            "than being handed his address by strangers. It loses on that "
            "shelf's own test, \"If the attachment has a recurring slot "
            "attached to a person rather than to a programme, this is a "
            "creator\" - the slot here was the programme, and the second-"
            "person address was its apparatus rather than a personality's "
            "output. The presenter's `not` still holds, because the intimacy "
            "\"is a job function with a shift behind it\", and the shift ran "
            "thirty-three years. The second counter is `character/mascot`, "
            "which the show supplies, since Daniel Striped Tiger and the "
            "puppets are the character shelf a reader might file the whole "
            "programme under. It loses on that shelf's def, \"A figure with "
            "no body, no biography and no intention\", because the puppets "
            "are not the tie this entry documents: \"the address runs one "
            "way, a child's reply - a shout at the screen, a sweater - does "
            "not reach the set\", and the reply was aimed at the man. "
            "Contestable, and recorded as such."
        ),
    },

    "betty-crocker": {
        "cat": "institution",
        "sub": "brand",
        "why": (
            "Filed `institution/brand`, on the shelf's def: \"A tie to a "
            "commercial entity that behaves recognisably like a person\" - "
            "and its `not` is this case almost verbatim, \"A brand is the "
            "case where the relationship is the asset and the person on the "
            "counter is employed by it.\" Betty Crocker is a home-service "
            "department's output, \"the reader attached to a woman who did "
            "not exist, and the reply, however real the labour behind it, "
            "came from the persona rather than the person\", typed by "
            "employed home economists under a name the company owned, which "
            "is \"a real hand typing under a name no woman owned\". The test "
            "answers cleanly: the far end is a commercial entity, and a "
            "competitor cannot take the attachment because the attachment is "
            "the brand. The entry's own framing is that this is \"the "
            "brand-as-character mechanism at its founding\" - the instance "
            "the mechanism entry names - and that mechanism already sits on "
            "this same shelf, so filing the instance beside it is the "
            "consistent reading rather than the tidy one. The counter is "
            "`character/fictional-protagonist`, and it is the natural first "
            "move, because Betty has an interior and a voice - \"she answered "
            "letters, then took a radio voice in 1924\". It loses on the one "
            "half of that shelf's test no author can survive, \"if no author "
            "can override what the audience says they feel\", because the "
            "fictional-protagonist is only where nobody can correct the "
            "audience, and here the author could and did correct everything: "
            "the name, the signature and the radio scripts were all chosen, "
            "and the persona \"was given a voice\" by decision rather than "
            "supplied by readers. The second counter is `character/mascot`, "
            "whose def sounds like her, \"A figure with no body, no biography "
            "and no intention\". It loses on that shelf's own `not`, \"Not a "
            "written character, who can contradict you\", because Betty's "
            "whole utility was that she carried a biography and a household "
            "voice - \"was like the woman next door dropping in for a morning "
            "visit to share a new recipe\" - which is a surface with an author "
            "rather than an inert logo. Contestable, and recorded as such."
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
        print(f"    {eid:20s} {r['cat']}/{r['sub']:<22s} why {len(r['why'])}ch")

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
