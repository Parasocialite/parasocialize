"""Fill the empty `claim` on the records `split_compound_citations.py` wrote.

The splitter ran before `citation_audit.py` noticed that the children it
created had no `claim` field at all - 13 of them, and the gate said so:
"13 record(s) print a placeholder where a claim should be". **The gate was
right and the tool was wrong**, and it caught it on the run rather than after a
commit, which is the whole point of having it.

Re-running the splitter does not help: the compounds are already split, so it
finds nothing to do. The affected records are identifiable exactly - they are the
ones carrying `split_from`, which only this splitter writes - so this repairs
precisely those and nothing else. It refuses to touch a record without that
field, because a hand-written record with an empty claim is a different problem
and deserves a different fix.

Asserts the record count, the entry count and the top-level keys before writing,
and prints each claim it writes so the text can be read rather than trusted.
"""
import json
import pathlib
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ROOT = pathlib.Path(__file__).resolve().parent.parent
APPLY = "--apply" in sys.argv
p = ROOT / "data" / "encyclopedia.json"
enc = json.loads(p.read_text(encoding="utf-8"))

before_entries = len(enc["entries"])
before_records = sum(len(e.get("sources", [])) for e in enc["entries"])
before_keys = sorted(enc)

CLAIM = (
    "Named inside a compound citation that also named the work cited "
    "separately on this entry, which carries its own locator. This one is "
    "recorded on its own so that a single string is not standing in for "
    "several works. **It has not been identified here - no title, no venue, no "
    "locator - and nothing is claimed about what it says.** The string it came "
    "from is kept in `split_from` so the compound is still on the record."
)

targets = []
for e in enc["entries"]:
    for r in e.get("sources", []):
        if "split_from" not in r:
            continue
        if r.get("claim"):
            continue
        targets.append((e["id"], r))

print(f"  records carrying split_from with NO claim: {len(targets)}")
for eid, r in targets:
    print(f"    [{eid}] {r.get('citation', '')[:70]!r} "
          f"status={r.get('status')}")

# Report what else is empty, so this repair cannot quietly leave the class behind
stray = [(e["id"], r.get("citation", "")[:60])
         for e in enc["entries"] for r in e.get("sources", [])
         if not r.get("claim") and "split_from" not in r]
print(f"\n  empty claims WITHOUT split_from (NOT this tool's business): {len(stray)}")
for eid, c in stray:
    print(f"    [{eid}] {c!r}")

if not targets:
    print("\nnothing to do")
    raise SystemExit(0)

if not APPLY:
    print("\ndry run. re-run with --apply")
    raise SystemExit(0)

for _eid, r in targets:
    r["claim"] = CLAIM

if len(enc["entries"]) != before_entries:
    sys.exit(f"refusing: entry count moved {before_entries}->{len(enc['entries'])}")
if sum(len(e.get("sources", [])) for e in enc["entries"]) != before_records:
    sys.exit("refusing: record count moved")
if sorted(enc) != before_keys:
    sys.exit("refusing: top-level keys changed")

second = p.read_text(encoding="utf-8").split("\n")[1]
indent = len(second) - len(second.lstrip()) or 1
tmp = p.with_suffix(".json.tmp")
tmp.write_text(json.dumps(enc, ensure_ascii=False, indent=indent) + "\n",
               encoding="utf-8")
re_parsed = json.loads(tmp.read_text(encoding="utf-8"))
still = [1 for e in re_parsed["entries"] for r in e.get("sources", [])
         if "split_from" in r and not r.get("claim")]
if still:
    sys.exit(f"refusing: {len(still)} split record(s) still have no claim after "
             f"the reparse")
tmp.replace(p)

print(f"\nwritten at indent={indent}. {len(targets)} claims filled. "
      f"entries and record count unchanged.")
if stray:
    print(f"  NOTE: {len(stray)} record(s) elsewhere have an empty claim and no "
          f"split_from. They are not mine and are not touched - a hand-written "
          f"record with no claim is a different defect.")
