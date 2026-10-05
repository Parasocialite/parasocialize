"""Add the `undemanded` register, and name the entries that would fill it.

The author said the origin of this site is lived experience of fake connections,
and asked for **all significant one-sided relations, manipulative or otherwise**.
Measured: the prose is already balanced 18 harm to 18 warmth, so nothing needs
rebalancing in the content. The tilt is in the frame. The register axis has six
members and five of them describe the FORM of a one-sided tie; **Harm is the only
one that carries a verdict**, and its own `not` says so. So valence occurs once
in the whole classification and occurs only for harm.

Bond proves it. Its test is "Is there a history?" - a structural question, and a
sasaeng bond and a parish congregation are both Bonds. The form is identical and
the register cannot separate them, so the difference can only live in a category,
and the only category carrying it is Harm. **A corpus written by somebody who was
harmed produces exactly this: balanced prose over an unbalanced frame, because the
frame was inherited and never examined.**

This adds the missing register. It is added EMPTY on purpose. The rule against
filling a hole to make a chart look even applies to a new member exactly as it
applies to a sub-category, and an unfilled register is an honest hole.

It also prints the entries that would belong in it, because the harder question is
not the member's definition but whether the corpus already holds instances the
frame could not see. Nine candidates are named in the output; they are NOT placed,
because placing them is an editorial decision and verify_taxonomy.py prints a
reason for every placement on the page.

Asserts the register count and the top-level keys before and after.
"""
import json
import pathlib
import re
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ROOT = pathlib.Path(r"C:\Users\paras\Documents\Default Project\parasocialize")
APPLY = "--apply" in sys.argv

MEMBER = {
    "id": "undemanded",
    "name": "Undemanded",
    "def": ("The tie stayed one-sided, nobody was paid for it, and nothing was "
            "asked of the other end. The register most parasocial writing cannot "
            "see, because it has no incident to report."),
    "test": ("Did anybody want anything from the other end? If the answer is no, "
             "and the tie still mattered, this is it. The question is about "
             "wanting rather than about harm, because wanting is the only part of "
             "a one-sided tie that is never anybody's fault."),
    "not": ("Not reciprocity - the other end could not answer, by definition, and "
            "that is what creates the register rather than making it an error. "
            "Not Harm, and emphatically not the absence of cost: plenty of "
            "undemanded ties carry grief, and Archive is the right home for that. "
            "Not Bond's history, which every register can have."),
    "mechanism": ("One-sidedness without a bill. The near side is not deceived, "
                  "nobody is charged, and the only thing missing is a second "
                  "person - which is the one thing that could never have been "
                  "arranged."),
    "note": ("Added 2026-10-06, empty, and empty is the correct state for it. "
             "The prose of the corpus is already balanced - 18 entries about harm "
             "against 18 about warmth or reply - so this does not rebalance "
             "anything. It repairs the FRAME: of six registers, five describe the "
             "form of a one-sided tie and only Harm carried a verdict, so valence "
             "appeared exactly once in the classification and only for harm. A "
             "Bond's test is whether there is a history, which is structural: a "
             "sasaeng bond and a parish congregation are both Bonds, and this is "
             "the register that tells them apart. It will be the hardest member "
             "to evidence, and that is not an argument against it - nobody files a "
             "complaint about a tie that asked for nothing, so no archive exists "
             "for the absence of an event."),
}

p = ROOT / "data" / "taxonomy.json"
tax = json.loads(p.read_text(encoding="utf-8"))
before_reg = len(tax.get("register", []))
before_keys = sorted(tax)

if any(isinstance(m, dict) and m.get("id") == MEMBER["id"]
       for m in tax.get("register", [])):
    print(f"  register {MEMBER['id']!r} already present; nothing to do")
    raise SystemExit(0)

print(f"  register members: {before_reg} -> {before_reg + 1}")
print(f"  adding          : {MEMBER['name']}  ({MEMBER['id']})")
print(f"  carries         : {sorted(MEMBER)}")
print("\n  every existing member has: def / test / not / mechanism / name / id")
missing = {"def", "test", "not", "mechanism", "name", "id"} - set(MEMBER)
if missing:
    sys.exit(f"refusing: the new member is missing {sorted(missing)}, and "
             f"verify_taxonomy.py requires a test and a not of real length")

if not APPLY:
    print("\ndry run. re-run with --apply")
    raise SystemExit(0)

tax["register"].append(MEMBER)
tax["register"].sort(key=lambda m: (m.get("name") or "").lower())

if len(tax.get("register", [])) != before_reg + 1:
    sys.exit("refusing to write: register count moved unexpectedly")
if sorted(tax) != before_keys:
    sys.exit("refusing to write: top-level keys changed")

tmp = p.with_suffix(".json.tmp")
tmp.write_text(json.dumps(tax, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
re_parsed = json.loads(tmp.read_text(encoding="utf-8"))
if len(re_parsed.get("register", [])) != before_reg + 1:
    sys.exit("refusing to write: reparse did not reconcile")
tmp.replace(p)
print(f"\nwritten. register {before_reg} -> {before_reg + 1}. "
      f"It is EMPTY, and empty is correct.")

# ---- which existing entries would belong in it? ---------------------------
enc = json.loads((ROOT / "data" / "encyclopedia.json").read_text(encoding="utf-8"))
print("\n=== entries the frame could not see: warm, one-sided, nothing asked ===")
CAND = [
    ("gomer-pyle", "a fictional family, addressed to you nightly for years"),
    ("saturday-mornings", "a broadcast slot that asks for your name and never replies"),
    ("the-clay-army", "eight thousand faces made to face outward, for an absent man"),
    ("howdy-doody", "thirteen years of the same greeting, and a clown who never spoke"),
    ("casper", "a ghost built so a child would not be afraid of the dark"),
    ("the-deaf-beloved", "a beloved who cannot hear, and so never learns the terms"),
    ("characters-move-in", "a fictional character who moves in and stays"),
    ("comfort-watch", "rewatching for company rather than for the plot"),
    ("the-uncanny-corridor", "the narrow band where a not-person is most companionable"),
    ("the-fourth-wall", "the wall is a specification for invisibility"),
]
for eid, why in CAND:
    e = next((x for x in enc["entries"] if x["id"] == eid), None)
    if not e:
        print(f"  {eid:<24} (no such entry)")
        continue
    print(f"  {eid:<24} {why[:60]}")
print("\n  NOT placed. A placement is an editorial decision and every one carries")
print("  a written reason that verify_taxonomy.py prints on the page; nine entries")
print("  do not get filed on the strength of a regex.")
