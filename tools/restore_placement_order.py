"""Restore `taxonomy_placements.json`'s own key order after a defensive sort.

`correct_dear_kitty.py` ended with `dict(sorted(pla["assignments"].items()))`,
which was meant to be harmless tidying. It was not harmless: the file's actual
convention is **sorted up to a point, then appended in the order entries were
added** - `fight-club`, `deadpool`, `rudolph-valentino`, `mickey-mouse`,
`lugosi-burial`, `king-kong` is the order I added them in, not the alphabet's.
Sorting rewrote every line and turned a two-entry change into a 2001-line diff,
which is the exact failure `AGENTS.md` records as "a JSON file containing half
the categories is still valid JSON containing half the categories": the output
looked correct and the diff could no longer be read.

The two new assignments are preserved; only the ordering of the older keys is
put back. Asserts that the key SET is unchanged and that the two additions are
present, so this cannot quietly drop or invent a placement.
"""
import collections
import json
import pathlib
import subprocess
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ROOT = pathlib.Path(r"C:\Users\paras\Documents\Default Project\parasocialize")
p = ROOT / "data" / "taxonomy_placements.json"
ADDED = ["dear-kitty", "the-figure-you-buy"]

committed_text = subprocess.run(
    ["git", "show", "HEAD:data/taxonomy_placements.json"],
    capture_output=True, text=True, cwd=ROOT, check=True,
    encoding="utf-8").stdout
committed = json.loads(committed_text)
current = json.loads(p.read_text(encoding="utf-8"))

old_order = list(committed["assignments"])
now = current["assignments"]

print(f"  committed assignments : {len(old_order)}")
print(f"  on disk              : {len(now)}")
print(f"  keys added           : {sorted(set(now) - set(old_order))}")

if sorted(set(now) - set(old_order)) != sorted(ADDED):
    sys.exit(f"refusing: unexpected additions {sorted(set(now) - set(old_order))}")
if set(old_order) - set(now):
    sys.exit(f"refusing: keys lost {set(old_order) - set(now)}")

# Rebuild: every pre-existing key in its committed order, then the additions in
# the order they were made.
rebuilt = collections.OrderedDict()
for k in old_order:
    rebuilt[k] = now[k]
for k in ADDED:
    rebuilt[k] = now[k]

if list(rebuilt) != old_order + ADDED:
    sys.exit("refusing: rebuilt order is not committed order plus the additions")
if set(rebuilt) != set(now):
    sys.exit("refusing: key set changed")

out = {"_method": committed["_method"], "assignments": rebuilt}
if "_note" in committed:
    out = {"_note": committed["_note"], "_method": committed["_method"],
           "assignments": rebuilt}
if set(out) != set(committed):
    sys.exit(f"refusing: top-level keys changed: {set(out)} vs {set(committed)}")

# **This file is indent=2 while every other corpus file is indent=1.** Writing it
# at indent=1 reformats all 2000 lines and turns a two-entry change into an
# unreadable diff. Read the committed file's own indentation rather than
# assuming it matches its siblings - the earlier attempt assumed, and the diff
# stat was the only thing that noticed.
committed_indent = 2
second = committed_text.split("\n")[1]
committed_indent = len(second) - len(second.lstrip())
if not committed_indent:
    sys.exit("refusing: could not read the committed indentation")
print(f"  committed indentation : {committed_indent}")

text = json.dumps(out, ensure_ascii=False, indent=committed_indent) + "\n"
p.write_text(text, encoding="utf-8")
re_parsed = json.loads(p.read_text(encoding="utf-8"))
if list(re_parsed["assignments"]) != old_order + ADDED:
    sys.exit("refusing: reparse did not reconcile")

print(f"\nwritten at indent={committed_indent}. key order restored; "
      f"{len(ADDED)} additions appended at the end.")
