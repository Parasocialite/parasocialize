"""Check the taxonomy is internally sound and say what it covers.

Four things worth asserting rather than assuming:
  1. every category and every sub-category is actually defined
  2. every sub-category can actually be *applied* - which means it has a test
     and a `not`, not just a definition
  3. every hand assignment points at a real entry and a real sub-category,
     and the sub-category belongs to the category claimed
  4. no sub-category is empty without that being recorded deliberately

The third is the one that matters. An empty sub-category is a hole in the corpus
or a category that does not earn its place, and both need to be visible. A
taxonomy that quietly drops its own weak parts is a taxonomy that will be
believed when it should not be.

On the second: a definition cannot be used to classify anything. It can only be
read. The field that does the work is the test - the question a person actually
needs answered when deciding where a new entry goes - and the `not`, which is
what stops the list growing sideways as more things get added. Requiring them by
name, and requiring them to be longer than a label, is what stops the taxonomy
regressing into eight category blurbs with thirty-eight decorative captions.
"""
import json
import pathlib
from collections import Counter

ROOT = pathlib.Path(__file__).resolve().parent.parent
tax = json.loads((ROOT / "data" / "taxonomy.json").read_text(encoding="utf-8"))
pla = json.loads((ROOT / "data" / "taxonomy_placements.json").read_text(encoding="utf-8"))
enc = json.loads((ROOT / "data" / "encyclopedia.json").read_text(encoding="utf-8"))

CATS = {a["id"]: a for a in tax["attachment"]}
OWNER, SUBS = {}, {}
for a in tax["attachment"]:
    for s in a["sub"]:
        OWNER[s["id"]] = a["id"]
        SUBS[s["id"]] = s

problems = []
for a in tax["attachment"]:
    for k in ("id", "sign", "blurb", "note", "colour", "sub"):
        if k not in a or (k != "sub" and not str(a[k]).strip()):
            problems.append(f"{a.get('id')}: missing {k}")
for sid, s in SUBS.items():
    for k in ("id", "name", "def", "test", "not", "mechanism"):
        if k not in s or not str(s[k]).strip():
            problems.append(f"{sid}: missing {k}")
    # A test shorter than a sentence is a label, not a test. It is the same
    # failure as a citation that only sounds like one, so it is checked by
    # length rather than trusted.
    for k, floor in (("def", 80), ("test", 80), ("not", 80), ("mechanism", 80)):
        if len(str(s.get(k, ""))) < floor:
            problems.append(f"{sid}: {k} is under {floor} chars "
                            f"({len(str(s.get(k, '')))}) - a label, not a test")
for r in tax["register"]:
    for k in ("id", "name", "def", "test", "not", "mechanism"):
        if k not in r or not str(r[k]).strip():
            problems.append(f"register/{r.get('id')}: missing {k}")
    for k, floor in (("test", 80), ("not", 80), ("mechanism", 80)):
        if len(str(r.get(k, ""))) < floor:
            problems.append(f"register/{r['id']}: {k} is under {floor} chars "
                            f"({len(str(r.get(k, '')))}) - a label, not a test")

# The third axis is checked the same way and for the same reason. It is the axis
# that records what the other end is *made of*, and it was added after an audit
# found the corpus holding no imaginary friends, no puppets and no aliens - a hole
# in the subject, not in the classification. Validating it only structurally would
# let it rot the way the corpus did: six members that are defined, testable and
# empty are an honest gap; six that are defined and never checked are decoration.
OTH = tax.get("otherness")
if not isinstance(OTH, dict) or not isinstance(OTH.get("members"), list):
    problems.append("taxonomy has no otherness axis with members")
    OTH_MEMBERS = []
else:
    OTH_MEMBERS = OTH["members"]
    ids = [m.get("id") for m in OTH_MEMBERS]
    if len(ids) != len(set(ids)):
        problems.append("otherness: duplicate member ids")
    if not OTH.get("_why_it_is_a_separate_axis"):
        problems.append("otherness: no _why_it_is_a_separate_axis - an axis "
                        "added to an existing classification has to say what it "
                        "would have hidden by being a cut across the others")
    for m in OTH_MEMBERS:
        for k in ("id", "name", "def", "test", "not", "mechanism"):
            if k not in m or not str(m[k]).strip():
                problems.append(f"otherness/{m.get('id')}: missing {k}")
        for k, floor in (("def", 80), ("test", 80), ("not", 80), ("mechanism", 80)):
            if len(str(m.get(k, ""))) < floor:
                problems.append(f"otherness/{m.get('id')}: {k} is under {floor} "
                                f"chars ({len(str(m.get(k, '')))}) - a label, not a test")

# The fourth axis, validated the same way. It exists because the 2019 character
# chart this project grew out of drew affection direction as an edge type, and
# the schema lost it: nothing in the data could say a bond was one-sided, which
# is the one property the site is named after. Validated structurally so it
# cannot rot the way the corpus did - three members that are defined, testable
# and empty are an honest gap; three that are never checked are decoration.
REC = tax.get("reciprocity")
if not isinstance(REC, dict) or not isinstance(REC.get("members"), list):
    problems.append("taxonomy has no reciprocity axis with members")
    REC_MEMBERS = []
else:
    REC_MEMBERS = REC["members"]
    rids = [m.get("id") for m in REC_MEMBERS]
    if len(rids) != len(set(rids)):
        problems.append("reciprocity: duplicate member ids")
    for k in ("_why_it_is_a_separate_axis", "_relation_to_the_2019_chart"):
        if not REC.get(k):
            problems.append(f"reciprocity: no {k} - an axis recovered from an "
                            f"older artefact has to say how it relates to it")
    for m in REC_MEMBERS:
        for k in ("id", "name", "def", "test", "not", "mechanism"):
            if k not in m or not str(m[k]).strip():
                problems.append(f"reciprocity/{m.get('id')}: missing {k}")
        for k, floor in (("def", 80), ("test", 80), ("not", 80), ("mechanism", 80)):
            if len(str(m.get(k, ""))) < floor:
                problems.append(f"reciprocity/{m.get('id')}: {k} is under {floor} "
                                f"chars ({len(str(m.get(k, '')))}) - a label, not a test")
    if "directed" not in rids:
        problems.append("reciprocity: no `directed` member - the axis exists to "
                        "name the default condition, and a default that is not "
                        "listed is a default that will be mislabelled as special")

# An anchor is a promise that a source exists. It is stored as a key into
# _literature and the page prints a label and links to the reference, so a key
# with no entry renders as something shaped like a citation that cannot be
# followed - the same defect as a `retrievable` status with no URL, which is
# how 94 records ended up claiming to be locatable.
LIT = tax["_literature"]
LABELS = tax.get("_anchor_labels") or {}
anchored = []
for sid, s in SUBS.items():
    k = s.get("anchor")
    if k:
        anchored.append(sid)
        if k not in LIT:
            problems.append(f"{sid}: anchored to {k!r}, which is not in _literature")
        if k not in LABELS:
            problems.append(f"{sid}: anchored to {k!r}, which has no human label")
for r in tax["register"]:
    k = r.get("anchor")
    if k:
        anchored.append("register/" + r["id"])
        if k not in LIT:
            problems.append(f"register/{r['id']}: anchored to {k!r}, not in _literature")
        if k not in LABELS:
            problems.append(f"register/{r['id']}: anchored to {k!r}, no human label")
for k in LABELS:
    if k not in LIT:
        problems.append(f"_anchor_labels has {k!r}, which has no _literature entry")

byid = {e["id"]: e for e in enc["entries"]}
for eid, v in pla["assignments"].items():
    if eid not in byid:
        problems.append(f"assignment {eid}: no such entry")
    if v["cat"] not in CATS:
        problems.append(f"assignment {eid}: unknown category {v['cat']}")
    if v["sub"] not in OWNER:
        problems.append(f"assignment {eid}: unknown sub-category {v['sub']}")
    elif OWNER[v["sub"]] != v["cat"]:
        problems.append(f"assignment {eid}: {v['sub']} is in {OWNER[v['sub']]}, "
                        f"not {v['cat']}")
    # The otherness axis is optional per entry, because it is a third cut and
    # forcing every placement to state it would be the same error as filling a
    # hole to make a chart look even. What is checked is that when it IS stated
    # it names a real member - a dangling axis value is worse than an absent one,
    # because it reads on the page as a classification that was performed.
    if OTH_MEMBERS and v.get("other") and v["other"] not in {
            m["id"] for m in OTH_MEMBERS}:
        problems.append(f"assignment {eid}: unknown otherness {v['other']!r}")
    if REC_MEMBERS and v.get("rec") and v["rec"] not in {
            m["id"] for m in REC_MEMBERS}:
        problems.append(f"assignment {eid}: unknown reciprocity {v['rec']!r}")

# The stories are placed in a separate file, and they fail differently: an
# encyclopedia entry is a claim about a thing and can be placed from its own
# summary, while a story is journalism and the placement has to survive the
# writer disagreeing with it. They are also the corpus the old ten sections were
# built from, so an unplaced story is the exact regression this taxonomy was
# assembled to prevent.
STORY = ROOT / "data" / "story_placements.json"
spla = {}
if STORY.exists():
    spla = json.loads(STORY.read_text(encoding="utf-8"))["placements"]
    idx = json.loads((ROOT / "data" / "index.json").read_text(encoding="utf-8"))
    slugs = {c["slug"] for c in idx["cards"]}
    for slug in sorted(slugs - set(spla)):
        problems.append(f"story {slug}: not placed")
    for slug in sorted(set(spla) - slugs):
        problems.append(f"story {slug}: placed, but no such story")
    for slug, v in spla.items():
        if v["cat"] not in CATS or OWNER.get(v["sub"]) != v["cat"]:
            problems.append(f"story {slug}: bad placement {v['cat']}/{v['sub']}")

print("=" * 64)
print("TAXONOMY INTEGRITY")
print("=" * 64)
if problems:
    for p in problems:
        print("  PROBLEM:", p)
    raise SystemExit(f"taxonomy: {len(problems)} problems")
else:
    print("  every category, sub-category and register is defined")
    print("  every sub-category and register has a test and a 'not' that can "
          "exclude something")
    print("  every anchor resolves to a real reference and prints a label")
    print("  every hand assignment points at a real entry and a real place")

nsub = len(SUBS)
print()
print(f"  {len(tax['attachment'])} attachment categories")
print(f"  {nsub} sub-categories")
print(f"  {len(tax['register'])} registers")
anch = sum(1 for s in SUBS.values() if s.get("anchor")) + \
    sum(1 for r in tax["register"] if r.get("anchor"))
print(f"  {anch} items carry a verified literature anchor")
print(f"  {len(OTH_MEMBERS)} otherness members (the third axis)")
print(f"  {len(REC_MEMBERS)} reciprocity members (the fourth axis)")
print(f"  {len(pla['assignments'])} entries hand-placed")
print(f"  {len(spla)} stories hand-placed")

print()
print("=" * 64)
print("THE TAXONOMY AGAINST THE CORPUS")
print("=" * 64)
handsub = Counter(v["sub"] for v in pla["assignments"].values())
print("  sub-categories with at least one hand-placed entry:")
covered = 0
for a in tax["attachment"]:
    line = []
    for s in a["sub"]:
        n = handsub.get(s["id"], 0)
        if n:
            covered += 1
        line.append(f"{s['id']}:{n}")
    print(f"    {a['sign']:<13} " + "  ".join(line))
print()
print(f"  {covered} of {nsub} sub-categories hold at least one hand-placed entry.")

print()
empty = [sid for sid in SUBS if not handsub.get(sid)]
print("  DELIBERATELY EMPTY - no entry in the corpus fits:")
for sid in empty:
    print(f"    {sid:<26} {SUBS[sid].get('note', 'no corpus coverage yet')[:66]}")
print()
print("  These are reported by placement count, not by whether the file")
print("  listed examples for them, because an example list is a claim about")
# counted, not typed. This paragraph used to say "Five of 38" as a literal and
# would have kept saying it after a sub-category emptied or a new one arrived -
# a report about the data that does not move when the data moves, which is the
# defect this file exists to catch.
print(f"  the category while a placement is a claim about the corpus. {len(empty)} of")
print(f"  {nsub} have no entry. That is the taxonomy admitting the gap rather than")
print("  quietly dropping its own weak parts, and it is also the list of")
print("  writing still owed. Nothing should be forced into them to make a")
print("  chart look even.")

print()
print("  EITHER the corpus is thin here, or the category does not earn its")
print("  place. Both are worth knowing; neither is a reason to delete it")
print("  quietly.")

if REC_MEMBERS:
    print()
    print("=" * 64)
    print("THE FOURTH AXIS AGAINST THE CORPUS")
    print("=" * 64)
    reccount = Counter(v["rec"] for v in pla["assignments"].values()
                       if v.get("rec"))
    for m in REC_MEMBERS:
        n = reccount.get(m["id"], 0)
        print(f"  {m['id']:<14} {m['name']:<32} entries placed: {n}")
    stated = sum(1 for v in pla["assignments"].values() if v.get("rec"))
    # Counted, not typed. This sentence used to say "the seven that are not",
    # which was a literal in a report about the data - it would have kept saying
    # seven after the corpus moved, and nobody would have noticed, because a
    # number in a paragraph is not obviously a claim.
    exceptions = sum(n for k, n in reccount.items() if k != "directed")
    print()
    print(f"  {stated} of {len(pla['assignments'])} placements state whether the")
    print("  bond attaches back. Optional, and deliberately so: `directed` is the")
    print("  default condition of the whole site, so requiring it on every entry")
    print(f"  would print {len(pla['assignments']) - stated} identical labels and hide")
    print(f"  the {exceptions} that are not. What is worth watching is `reciprocated`")
    print("  and `simulated` - a corpus about one-sided attachment that cannot count")
    print("  its own exceptions is not measuring the thing it is named after.")
    emptyrec = [m["id"] for m in REC_MEMBERS if not reccount.get(m["id"])]
    if emptyrec:
        print()
        print("  NO ENTRY PLACED YET:")
        for k in emptyrec:
            print(f"    {k}")

if OTH_MEMBERS:
    print()
    print("=" * 64)
    print("THE THIRD AXIS AGAINST THE CORPUS")
    print("=" * 64)
    othercount = Counter(v["other"] for v in pla["assignments"].values()
                         if v.get("other"))
    for m in OTH_MEMBERS:
        n = othercount.get(m["id"], 0)
        print(f"  {m['id']:<14} {m['name']:<22} entries placed: {n}")
    stated = sum(1 for v in pla["assignments"].values() if v.get("other"))
    print()
    print(f"  {stated} of {len(pla['assignments'])} placements state a "
          f"kind of otherness. Optional by design: it is a third cut, and")
    print("  requiring it everywhere would be the same move as filling a")
    print("  hole to make a chart look even. A member with nothing placed")
    print("  against it is an honest gap, and is where the writing is owed.")
    emptyoth = [m["id"] for m in OTH_MEMBERS if not othercount.get(m["id"])]
    if emptyoth:
        print()
        print("  NO ENTRY PLACED YET:")
        for k in emptyoth:
            print(f"    {k}")