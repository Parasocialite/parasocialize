"""Correct `dear-kitty` as written, and place the two entries that have none.

Three defects found by reading the entry against the corpus's own vocabulary
rather than against my memory of writing it. None would have been caught by a
build, and one of them is a lie a reader would read as a fact.

  1. TWO FALSE RELATIONS. I wrote `mourn-a-person-you-met` (1990) and
     `dickens` (1812) as `contemporary` with a 1942 entry. `contemporary`
     renders as "of the same time as", so both edges asserted a chronology that
     is 48 and 130 years wrong. This is the inverted-verb family AGENTS records
     seven times across three entries, and I repeated it by writing the verb
     from how the sentence read instead of from the dates.
     `dear-kitty` at 1942 is **the only entry in that year** - measured, not
     assumed - so there is no honest `contemporary` to have, and the correct
     result is fewer relations rather than invented ones.
  2. `kind: case`. Legal, but the three pre-existing `case` entries are all
     matters before a court: `stalker-law`, `characterai-lawsuits`,
     `the-litigation-year`. A published diary is not a case. Its peers by shape
     are `gigi` (1943) and `casper` (1945), both `work`.
  3. `sections` carried `brand`, which is a licence relationship and has
     nothing to do with a hiding child in Amsterdam. `grief` is the section that
     does fit, and the register's own `not` says undemanded ties may carry grief
     and that Archive is where it lives.

**No placement means no shelf.** `dear-kitty` and `the-figure-you-buy` were both
written without a `taxonomy_placements.json` row, so neither appeared in any
category count and neither had its reason printed anywhere. Placements are added
for both, and `reciprocity` is left unset on both on purpose: `directed` is the
default condition of the whole site, so setting it prints a label that says
nothing, and the axis exists to surface the exceptions.

Asserts the entry count, the assignment count, the sub-category, the otherness
member and the top-level keys before and after. Writes nothing if any fails.
"""
import json
import pathlib
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ROOT = pathlib.Path(__file__).resolve().parent.parent
APPLY = "--apply" in sys.argv

enc_p = ROOT / "data" / "encyclopedia.json"
pla_p = ROOT / "data" / "taxonomy_placements.json"
tax_p = ROOT / "data" / "taxonomy.json"

enc = json.loads(enc_p.read_text(encoding="utf-8"))
pla = json.loads(pla_p.read_text(encoding="utf-8"))
tax = json.loads(tax_p.read_text(encoding="utf-8"))

entries = enc["entries"]
by_id = {e["id"]: e for e in entries}
before_entries = len(entries)
before_asg = len(pla["assignments"])
before_keys = sorted(enc)
subs = {(a["id"], s["id"]) for a in tax["attachment"] for s in a.get("sub", [])}
others = {m["id"] for m in tax["otherness"]["members"]}

print(f"  entries {before_entries} | assignments {before_asg}")
print(f"  unplaced entries: {sorted(set(by_id) - set(pla['assignments']))}")
print()

# --- 1. dear-kitty -------------------------------------------------------------
e = by_id.get("dear-kitty")
if e is None:
    sys.exit("dear-kitty is not in the corpus; refusing")

print("== dear-kitty corrections ==")
print(f"  kind     {e['kind']!r} -> 'work'")
e["kind"] = "work"

old_sections = list(e["sections"])
e["sections"] = ["character", "companion", "grief"]
print(f"  sections {old_sections} -> {e['sections']}")

dropped = [r for r in e["relations"] if r["type"] == "contemporary"]
kept = [r for r in e["relations"] if r["type"] != "contemporary"]
for r in dropped:
    other = by_id[r["to"]]
    print(f"  DROPPED  {r['type']} -> {r['to']} ({other['year']} is not {e['year']})")
# `cites` is bibliographic and neither target is cited by this entry; `depicts`
# is how the corpus links a work to the phenomenon it stages - `beatlesmania
# depicts will-and-want`, `boybands depicts the-brand-as-character`. That is
# the honest remaining edge, and `instance_of` is the shelf it belongs on.
kept = [r for r in kept if r["type"] != "cites"]
kept.append({"to": "parasocial-interaction", "type": "depicts"})
e["relations"] = sorted(kept, key=lambda r: (r["type"], r["to"]))
for r in e["relations"]:
    print(f"  KEPT     {r['type']:12s} -> {r['to']} ({by_id[r['to']]['year']})")

# --- 2. placements for both unplaced entries ---------------------------------
NEW_ASG = {
    "dear-kitty": {
        "cat": "companion",
        "sub": "social-agent",
        "other": "imagined",
        "why": (
            "Filed `companion/social-agent` because the shelf it belongs on was "
            "opened by `the-imaginary-friend`, and this is that entry's oldest "
            "named instance rather than a variant of it. `other: imagined` is "
            "the clean case on that axis rather than a debatable one: Anne "
            "invented Kitty, and knew she had. The child in "
            "`the-imaginary-friend` also knows, and the distinction the axis "
            "cannot make - a companion who is silent versus a listener who is "
            "written TO - is why this is filed as a social agent rather than "
            "an anthropomorphised object. It is the corpus's only example of a "
            "one-sided tie documented from the near side in the near side's own "
            "handwriting, and the only one where the near side states the "
            "condition in words: 'I hope the feeling is mutual', which is the "
            "definition of this site given by somebody living inside it. "
            "Reciprocity is left unset on purpose - `directed` is the default "
            "condition of the whole corpus and the axis exists to surface the "
            "exceptions, and this is not one."
        ),
    },
    "the-figure-you-buy": {
        "cat": "persona",
        "sub": "creator",
        "why": (
            "Filed `persona/creator` and NOT `brand`, which is the placement "
            "this entry exists to invert. `the-brand-as-character` at "
            "companion/brand is the ordinary direction: a company acquires a "
            "voice, a face and a founder narrative so that a customer "
            "relationship has a subject. Here the figure came first - Roald "
            "Dahl invented a chocolatier in 1964 - and the product took the "
            "figure's NAME, with the film retitled to carry it and the bar "
            "launching a month before the film opened. The shelf is the one "
            "that holds people who authored something, because a chocolatier "
            "written in 1964 is a created character first and a brand only "
            "once somebody bought the rights to his name. Deliberately left "
            "unplaced on otherness: the six members describe what the far end "
            "is MADE OF, and a figure that is simultaneously invented by an "
            "author, licensed by four successive owners and printed on "
            "packaging does not reduce to one of them without losing the "
            "licensing, which is the entry's actual argument."
        ),
    },
}

print("\n== placements ==")
for eid, val in NEW_ASG.items():
    if eid in pla["assignments"]:
        sys.exit(f"{eid} is already placed; refusing to overwrite a written reason")
    if eid not in by_id:
        sys.exit(f"{eid} is not in the corpus; refusing")
    if (val["cat"], val["sub"]) not in subs:
        sys.exit(f"{eid}: {val['cat']}/{val['sub']} is not a sub-category")
    if "other" in val and val["other"] not in others:
        sys.exit(f"{eid}: other={val['other']!r} is not an otherness member")
    print(f"  + {eid}: {val['cat']}/{val['sub']}"
          + (f"  other={val['other']}" if "other" in val else ""))
    for s in sorted(subs):
        if s[0] == val["cat"]:
            print(f"      sibling shelves: {s[1]!r}")

if not APPLY:
    print("\ndry run. re-run with --apply")
    raise SystemExit(0)

for eid, val in NEW_ASG.items():
    pla["assignments"][eid] = val
pla["assignments"] = dict(sorted(pla["assignments"].items()))

# --- guards -------------------------------------------------------------------
if len(entries) != before_entries:
    sys.exit(f"refusing: entry count moved {before_entries} -> {len(entries)}")
if sorted(enc) != before_keys:
    sys.exit("refusing: top-level keys changed")
if len(pla["assignments"]) != before_asg + 2:
    sys.exit(f"refusing: assignment count {before_asg} -> {len(pla['assignments'])}")
if set(by_id) != {k for k in by_id} | set(pla["assignments"]):
    pass
missing = set(by_id) - set(pla["assignments"])
if missing:
    sys.exit(f"refusing: still unplaced: {sorted(missing)}")

for eid, val in NEW_ASG.items():
    enc_p.write_text(json.dumps(enc, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    break
tmp = enc_p.with_suffix(".json.tmp")
tmp.write_text(json.dumps(enc, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
re_enc = json.loads(tmp.read_text(encoding="utf-8"))
if len(re_enc["entries"]) != before_entries:
    sys.exit("refusing: reparse of encyclopedia did not reconcile")
k = by_id["dear-kitty"]
if k["kind"] != "work" or k["sections"] != ["character", "companion", "grief"]:
    sys.exit("refusing: corrections did not survive the reparse")
if any(r["type"] == "contemporary" for r in k["relations"]):
    sys.exit("refusing: a false contemporary edge survived")
tmp.replace(enc_p)

tmp2 = pla_p.with_suffix(".json.tmp")
tmp2.write_text(json.dumps(pla, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
re_pla = json.loads(tmp2.read_text(encoding="utf-8"))
if len(re_pla["assignments"]) != before_asg + 2:
    sys.exit("refusing: reparse of placements did not reconcile")
tmp2.replace(pla_p)

print(f"\nwritten. entries {before_entries} (unchanged), "
      f"assignments {before_asg} -> {before_asg + 2}. 0 unplaced.")
print(f"  dear-kitty: kind=work, sections={k['sections']}, {len(k['relations'])} relations.")
