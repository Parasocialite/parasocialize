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
ROOT = pathlib.Path(r"C:\Users\paras\Documents\Default Project\parasocialize")

enc = json.loads((ROOT / "data" / "encyclopedia.json").read_text(encoding="utf-8"))
entries = enc["entries"]
recs = [s for e in entries for s in e.get("sources", [])]
has_loc = sum(1 for s in recs if s.get("url"))

print("=== AGENTS Current state block ===")
print(f"  relationships. {len(entries)} entries, "
      f"{sum(len(e.get('relations', [])) for e in entries)} relations, "
      f"{len(list((ROOT / 'dist').rglob('*.html')))} generated pages.")
print(f"{sum(1 for e in entries if e.get('provenance') != 'thesis')} sourced | "
      f"{sum(1 for e in entries if not e.get('sources') and e.get('provenance') != 'thesis')} "
      f"not yet stood behind | {sum(1 for e in entries if e.get('provenance') == 'thesis')} "
      f"thesis   = {len(entries)}")
print(f"{has_loc} of {len(recs)} sources have a locator")
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
