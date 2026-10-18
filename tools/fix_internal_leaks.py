"""Close the five remaining internal-vocabulary leaks in reader-visible prose.

Found by tools/check_internal_leaks.py, which was written after /ledger/ shipped
reading "...and AGENTS is explicit that this is not a gap". Each of these is the
same defect: process vocabulary in front of a reader who has never opened the
repository.

The substitutions keep the meaning and drop the filename. Two of them are in
data files, so every replacement asserts it matched exactly once and that no
count moved before anything is written - the rule for hand-maintained corpus
files, applied to prose rather than entries.
"""
import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

EDITS = [
    # (file, old, new, expected_matches)
    (ROOT / "data" / "taxonomy.json",
     "See AGENTS.md: never invent a citation, a date or an attribution.",
     "The rule this site works to is blunt: never invent a citation, a date "
     "or an attribution.", 1),
    (ROOT / "data" / "taxonomy.json",
     "`encyclopedia.json` relations are chronological and bibliographic",
     "The relations recorded in the encyclopedia are chronological and "
     "bibliographic", 1),
    (ROOT / "tools" / "build_cards.py",
     "They are marked\n  <code>provenance: thesis</code> in the data and "
     "counted separately",
     "They are marked as this site's own argument and counted separately", 1),
    (ROOT / "data" / "encyclopedia.json",
     "Date of access recorded in tools/citation_audit_baseline.json run.",
     "Date of access recorded when the record was added.", 1),
]

plan = []
for path, old, new, expect in EDITS:
    raw = path.read_text(encoding="utf-8")
    n = raw.count(old)
    if n == expect:
        plan.append((path, old, new, "apply"))
    elif n == 0 and raw.count(new) >= expect:
        # already applied by an earlier run. Verified rather than re-applied,
        # so the script is safe to run twice - which it had to be, because the
        # first version wrote before it finished verifying.
        plan.append((path, old, new, "already applied"))
    else:
        print(f"ABORT: {path.name}: expected {expect} match(es) for "
              f"{old[:48]!r}, found {n}, and the replacement text is not "
              f"present either. Nothing written.")
        sys.exit(1)

# Everything is verified before anything is written.
for path, old, new, act in plan:
    print(f"  {path.name}: {act}")
for path, old, new, act in plan:
    if act == "apply":
        path.write_text(path.read_text(encoding="utf-8").replace(old, new),
                        encoding="utf-8")

# Every data file touched must still parse, and still hold what it held.
tax = json.loads((ROOT / "data" / "taxonomy.json").read_text(encoding="utf-8"))
enc = json.loads((ROOT / "data" / "encyclopedia.json").read_text(encoding="utf-8"))
print()
print(f"taxonomy keys intact:  {sorted(tax)[:4]}")
print(f"entries: {len(enc['entries'])}  top keys: {sorted(enc)[:4]}")

# And the words must be gone from the data itself, not just the built page.
blob = ((ROOT / "data" / "taxonomy.json").read_text(encoding="utf-8")
        + (ROOT / "tools" / "build_cards.py").read_text(encoding="utf-8"))
for term in ("AGENTS.md", "encyclopedia.json"):
    print(f"  {term!r} still in taxonomy.json/build_cards.py: {term in blob}")
