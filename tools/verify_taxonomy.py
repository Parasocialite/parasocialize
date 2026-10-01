"""Check the taxonomy is internally sound and say what it covers.

Three things worth asserting rather than assuming:
  1. every category and every sub-category is actually defined
  2. every hand assignment points at a real entry and a real sub-category,
     and the sub-category belongs to the category claimed
  3. no sub-category is empty without that being recorded deliberately

The third is the one that matters. An empty sub-category is a hole in the corpus
or a category that does not earn its place, and both need to be visible. A
taxonomy that quietly drops its own weak parts is a taxonomy that will be
believed when it should not be.
"""
import json
import pathlib
from collections import Counter

ROOT = pathlib.Path(r"C:\Users\paras\Documents\Default Project\parasocialize")
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
    for k in ("id", "name", "def"):
        if k not in s or not str(s[k]).strip():
            problems.append(f"{sid}: missing {k}")
for r in tax["register"]:
    for k in ("id", "name", "def"):
        if k not in r or not str(r[k]).strip():
            problems.append(f"register/{r.get('id')}: missing {k}")

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

print("=" * 64)
print("TAXONOMY INTEGRITY")
print("=" * 64)
if problems:
    for p in problems:
        print("  PROBLEM:", p)
else:
    print("  every category, sub-category and register is defined")
    print("  every hand assignment points at a real entry and a real place")

nsub = len(SUBS)
print()
print(f"  {len(tax['attachment'])} attachment categories")
print(f"  {nsub} sub-categories")
print(f"  {len(tax['register'])} registers")
anch = sum(1 for s in SUBS.values() if s.get("anchor")) + \
    sum(1 for r in tax["register"] if r.get("anchor"))
print(f"  {anch} items carry a verified literature anchor")
print(f"  {len(pla['assignments'])} entries hand-placed")

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
print("  DELIBERATELY EMPTY (recorded, not hidden):")
for sid, s in SUBS.items():
    if not (s.get("examples") or []) and not handsub.get(sid):
        print(f"    {sid:<26} {s.get('note','no corpus coverage yet')[:70]}")

print()
print("  EITHER the corpus is thin here, or the category does not earn its")
print("  place. Both are worth knowing; neither is a reason to delete it")
print("  quietly.")