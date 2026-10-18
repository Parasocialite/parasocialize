"""Repair placements whose `why` is the old tool-named to-do.

`expand.py` used to fall back to "Added by tools/expand.py; review the reason."
when a candidate carried no placement reason. That string is printed on the
page, so it reached readers: it names a tool nobody outside the repository has
heard of, and it is a to-do sitting where an argument should be - the same
shape as `claim: "the entry as a whole"` and the fourteen citation strings that
were literally the word "verify".

Every one of these entries already carries a `fits` field, which is the shelf-fit
reasoning and reads correctly as a placement reason. So this fills `why` from
`fits` rather than inventing prose, and refuses to touch anything that is not
the exact offending string - a placement someone wrote by hand is not this
tool's business.

Asserts the placement count, the entry count and the top-level keys before and
after, per the rule for hand-maintained corpus files.
"""
import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

BAD = "Added by tools/expand.py; review the reason."
P = ROOT / "data" / "taxonomy_placements.json"
E = ROOT / "data" / "encyclopedia.json"

raw = P.read_text(encoding="utf-8")
plc = json.loads(raw)
keys = sorted(plc)
assign = plc["assignments"]
n = len(assign)

fits = {e["id"]: e.get("fits") for e in
        json.loads(E.read_text(encoding="utf-8"))["entries"]}

bad = [k for k, v in assign.items() if (v or {}).get("why") == BAD]
print(f"placements: {n}")
print(f"carrying the tool-named to-do: {len(bad)}")

fixable, unfixable = [], []
for k in bad:
    if fits.get(k):
        fixable.append(k)
    else:
        unfixable.append(k)

for k in unfixable:
    print(f"  NO fits field, cannot fill: {k}")
if unfixable:
    print("REFUSING: these need a written reason, not a repair.")
    sys.exit(1)

for k in fixable:
    assign[k]["why"] = fits[k]
    print(f"  filled: {k}")

assert len(assign) == n, "placement count moved"
assert sorted(plc) == keys, "top-level keys moved"
P.write_text(json.dumps(plc, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

chk = json.loads(P.read_text(encoding="utf-8"))
assert len(chk["assignments"]) == n, "placement count moved on re-read"
assert sorted(chk) == keys, "top-level keys moved on re-read"
left = [k for k, v in chk["assignments"].items() if (v or {}).get("why") == BAD]
print()
print(f"repaired {len(fixable)}; still carrying the to-do: {len(left)}")
if left:
    sys.exit(1)
print("placements unchanged:", n)
