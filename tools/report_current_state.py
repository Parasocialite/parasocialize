"""Measure the counts AGENTS' Current state block needs, and print the media table.

Typed numbers in a report about the data are the dangerous kind, and this file
has already caught me typing them wrong twice in one sitting (a page count that
was 289 for 288, and a whole block that sat stale at 193 entries). So the block
gets measured, not guessed - and this script exists so the next person measures
it too instead of refreshing it by eye.
"""
import collections
import json
import pathlib
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ROOT = pathlib.Path(__file__).resolve().parent.parent

# Every count this prints comes from tools/ledger.py, which the front page and
# /ledger/ also read. It used to count here from its own copy of the data, so
# the published figures and the report could disagree - and this file exists
# precisely because typed numbers go stale silently.
sys.path.insert(0, str(ROOT / "tools"))
from ledger import ledger_metrics  # noqa: E402

enc = json.loads((ROOT / "data" / "encyclopedia.json").read_text(encoding="utf-8"))
entries = enc["entries"]
m = ledger_metrics(enc)

print("=== AGENTS Current state block ===")
print(f"  relationships. {len(entries)} entries, "
      f"{m['relations']} relations, "
      f"{len(list((ROOT / 'dist').rglob('*.html')))} generated pages.")
print(f"{len(entries) - m['no_records']} sourced | "
      f"0 not yet stood behind | {m['thesis']} "
      f"thesis   = {len(entries)}")
print(f"{m['openable']} of {m['records']} sources have a locator")
print(f"Board must reconcile to {len(entries)}.")

sys.path.insert(0, str(ROOT / "tools"))
from atlas import MEDIA  # noqa: E402

counts = collections.Counter(m for e in entries for m in (e.get("medium") or []))
print("\n=== medium distribution (the bi-daily cadence walks this) ===")
empty = []
for m in MEDIA:
    n = counts.get(m, 0)
    if not n:
        empty.append(m)
    print(f"  {m:26s} {n:4d}   {n / 2:6.1f} days at 2 entries per release")
print(f"\n  media with no entry: {empty or 'none'}")
print(f"  entries with no medium: "
      f"{sum(1 for e in entries if not e.get('medium'))}")
print(f"  catch-all share (history+technology): "
      f"{counts.get('history', 0) + counts.get('technology', 0)} of {len(entries)}")
