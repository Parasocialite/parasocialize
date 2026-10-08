# -*- coding: utf-8 -*-
"""Place the three entries added by `add_fourth_batch_entries.py`.

Placements are arguments, not labels. Each `why` below names the shelf, quotes
the part of its own definition that decides it, then states the counter-argument
and why it loses. `verify_taxonomy.py` can check that a category exists and that
a sub-category belongs to it; it cannot check that the placement is right, so
the contestable ones say so on purpose.

Three decisions worth recording up front:

  `blues-clues` (1996) is filed `persona/presenter` against
  `cosmology/scheduling` and `character/mascot`, and the evidence genuinely
  cuts both ways: The New York Times caught the show running "a
  Monday-to-Friday schedule on which the same question arrives five days a
  week", which is scheduling's own test in the entry's own words. It loses
  because what the research measured is the addressed pause rather than the
  appointment - comprehension rising with every repeat of the same question
  is the address surviving the slot, and the question outlived the format.

  `guru-disciple` (1650) is filed `officer/senior` against
  `officer/teacher` and `institution/faith-body`, and faith-body is the
  stronger counter: Capper's field site has a building, a schedule and a
  sangha. It loses on that shelf's own def - "A parish you are in rather
  than a figure you follow" - because the instruction this entry carries
  addresses a figure followed by one person in private, and on its
  mechanism, attendance, which the formula abolishes: attention is demanded
  while "moving, walking, sleeping, sitting", which is attendance replaced
  by continuous private thought.

  `unreliable-narrator` (1961) is filed `character/fictional-protagonist`
  against `character/played-role`, and the counter takes the strongest form
  available here - The Narrator is played and the split is on screen. It
  loses on that shelf's own `not`, because the term needs no performer at
  all: a narrator in a novel has none, and Booth's verdict is made against
  "the implied author's norms", a reference no casting choice can supply.

Usage:  python tools/add_fourth_batch_placements.py        (dry run)
        python tools/add_fourth_batch_placements.py --apply
"""

import json
import pathlib
import sys

APPLY = "--apply" in sys.argv
P = pathlib.Path("data/taxonomy_placements.json")
ENTRIES = pathlib.Path("data/encyclopedia.json")

PLACEMENTS = {
    "blues-clues": {
        "cat": "persona",
        "sub": "presenter",
        "why": (
            "Filed `persona/presenter`, on the shelf's test: \"Did an "
            "institution put them there, and do they speak in the second "
            "person on a schedule? Direct address plus an employer is the "
            "test.\" The entry answers both halves from its own method - a "
            "host placed in front of a camera to work a schedule, and a "
            "script that supplies the second person: \"the host looks into "
            "the camera, asks the child a question, waits through a silence "
            "written into the script, and then behaves as though an answer "
            "arrived\", which is the mechanism's \"Second-person grammar "
            "aimed at a large audience is a machine for manufacturing the "
            "feeling of being singled out\" aimed at children who had not "
            "yet learned there was one. The research of the period calls it "
            "what it is: \"the introduction of Blue's Clues in 1996 ushered "
            "in an expansion of pseudo-interaction in children's "
            "programming\", and the entry's sharpest line records what the "
            "expansion removed - \"the reply did not have to be a reply\". "
            "The `not` holds as well: \"The presenter's defining constraint "
            "is that the intimacy is a job function with a shift behind it\" "
            "- a host reading a scripted pause is the duty-free version of "
            "the cleric's assembly address, which is what this shelf exists "
            "to distinguish. The counter is `cosmology/scheduling`, and the "
            "evidence genuinely cuts both ways: The New York Times caught "
            "\"a Monday-to-Friday schedule on which the same question "
            "arrives five days a week\", and that shelf asks \"Is the "
            "recurring time doing more work than the content?\" It loses "
            "because the measurement in this entry is of the addressed pause "
            "rather than the appointment - comprehension rising with every "
            "repeat of the same question is the address surviving the slot, "
            "and \"the question outlived the format, and children are still "
            "the ones who answered it\". The second counter is "
            "`character/mascot`, since Blue is a drawn figure specified "
            "entirely by others, and that shelf's test is \"Does the figure "
            "have an interior anybody could get wrong, or is it specified "
            "entirely by others?\" It loses because the attachment this "
            "entry documents runs to the person in the chair - \"The host "
            "is not doing what a presenter does by accident either.\" "
            "Contestable, and recorded as such."
        ),
    },

    "guru-disciple": {
        "cat": "officer",
        "sub": "senior",
        "why": (
            "Filed `officer/senior`, on the shelf's test: \"Do they hold a "
            "role, or do they hold standing?\" and its second half, \"If "
            "they hold only standing, the relationship runs on age, "
            "seniority or reputation, and this is the shelf.\" The lama "
            "holds no office over this disciple - the entry's instruction "
            "does not assign a post, it assigns an object of attention, "
            "\"Moving, walking, sleeping, sitting, happy or miserable, "
            "continuously think of nothing but the guru!\" - and the shelf's "
            "def is what that describes: \"There is no office, no "
            "institution and no duty of care, which is precisely what makes "
            "the tie unprotected.\" The relation is, in the field site's own "
            "words, \"inherently hierarchical\", and the senior's asymmetry "
            "is the mechanism's: \"No institution stands behind the tie, so "
            "nothing constrains it\", which is why the tradition carries "
            "fifty verses of instruction rather than a contract. The "
            "counter is `officer/teacher`, whose test asks \"Could the "
            "person have declined to know you?\" It loses on the teacher's "
            "own `not`: \"The teacher's attachment is the only one on this "
            "site that is legally compulsory, and that is what distinguishes "
            "it and what makes it difficult to discuss.\" Nothing here is "
            "compulsory: no law requires the attention, and this shelf "
            "defines itself as the one where \"nothing obliges this person "
            "to treat the attachment at all\" - the tie runs on standing and "
            "can be met with silence. The second counter is "
            "`institution/faith-body`, and it is the stronger of the two, "
            "because Capper's field site has a building, a schedule and a "
            "sangha: \"All Buddhist practices at Siddha Gompa revolve around "
            "this devotion.\" It loses on that shelf's own def, \"A parish "
            "you are in rather than a figure you follow\", for what the "
            "entry's instruction addresses is a figure, followed by one "
            "person in private; and on its mechanism, \"Attendance as the "
            "substrate. A relationship sustained by physical presence on a "
            "schedule, with witnesses\", which is precisely what the formula "
            "refuses - attention is demanded while \"moving, walking, "
            "sleeping, sitting\", attendance abolished and replaced by "
            "continuous private thought. The tradition \"makes it "
            "indispensable to the path rather than optional\", and the path "
            "is walked alone. Contestable, and recorded as such."
        ),
    },

    "unreliable-narrator": {
        "cat": "character",
        "sub": "fictional-protagonist",
        "why": (
            "Filed `character/fictional-protagonist`, on the shelf's test: "
            "\"Is the figure available in more than one place at the same "
            "time, to people who have never met?\" A narrator is available "
            "to every reader holding the book at once and to none of them in "
            "person, which is the shelf's def exactly: \"Somebody described "
            "in a book and therefore available to an unlimited number of "
            "people at once, none of whom can be contradicted.\" The entry's "
            "own condition is the mechanism's first half, \"A fictional "
            "interior is an invitation with no host present\", sharpened by "
            "the summary into what the reader actually stands in: \"you are "
            "inside a voice you cannot verify, and nobody will correct "
            "you.\" Booth's test puts the verdict where the shelf puts it - "
            "the norms are \"the implied author's norms\", an entity nobody "
            "on the page can produce - so \"it is a verdict reconstructed "
            "from the shape of the telling, by a reader standing alone with "
            "it\", and the text never closes the account: sixty years on the "
            "term is still \"coined once, revised by its coiner, extended by "
            "everyone else\", which is the audience-supplied continuity the "
            "shelf describes running faster than any author can correct it. "
            "The counter is `character/played-role`, and it takes the "
            "strongest form available on this site: The Narrator is played "
            "on screen and the split is visible, with \"The Narrator, an "
            "unreliable narrator, is not immediately aware that he is "
            "mentally projecting Tyler\" as the case an audience holds. It "
            "loses on that shelf's own `not`, \"The played role requires "
            "the performer to be legible as a person\" - the term needs no "
            "performer at all, since a narrator in a novel has none, and "
            "where there is one the unreliability does not sit in him: "
            "Booth's definition decides against norms the actor cannot play, "
            "and the corpus records the mechanism as \"An unreliable "
            "narrator is a person who knows and maintains anyway\", a state "
            "of knowing held by a voice rather than by a casting choice. "
            "Contestable, and recorded as such."
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
