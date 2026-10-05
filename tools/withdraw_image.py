"""Withdraw a generated-image record the way neanderthal-burial was withdrawn.

Downgrading to `unchecked` is not withdrawal. It leaves `local` pointing at a
file nobody opened and approved, which is the same shape of defect as the 94
records that claimed `retrievable` with no URL: the record keeps asserting an
asset exists. A rejected image has no record and no file, and the entry falls
back to its generated SVG plate, which is honest.

AGENTS.md rule for hand-maintained corpus files: assert the count before and
after, and refuse to write if it fell.
"""
import json
import pathlib
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ROOT = pathlib.Path(r"C:\Users\paras\Documents\Default Project\parasocialize")
APPLY = "--apply" in sys.argv
TARGET = "paleolithic-figures"

p = ROOT / "data" / "images.json"
data = json.loads(p.read_text(encoding="utf-8"))
before = len(data["items"])

hits = [i for i in data["items"]
        if i.get("slug") == TARGET and "generated" in str(i.get("local", ""))]
if len(hits) != 1:
    sys.exit(f"expected exactly 1 generated record for {TARGET}, found {len(hits)}")
rec = hits[0]
f = ROOT / rec["local"]

print(f"record: kind={rec['kind']} local={rec['local']}")
print(f"file  : {'exists' if f.exists() else 'MISSING'}  "
      f"{f.stat().st_size/1024:.1f} KB" if f.exists() else "file  : MISSING")
print(f"reason on record: {str(rec.get('look_reason'))[:100]}...")

if not APPLY:
    print("\ndry run. re-run with --apply")
    raise SystemExit(0)

data["items"] = [i for i in data["items"] if i is not rec]
after = len(data["items"])
if after != before - 1:
    sys.exit(f"refusing to write: expected {before - 1} items, have {after}")

tmp = p.with_suffix(".json.tmp")
tmp.write_text(json.dumps(data, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
check = json.loads(tmp.read_text(encoding="utf-8"))
if len(check["items"]) != after or not check.get("items"):
    sys.exit("refusing to write: reparse did not reconcile")
tmp.replace(p)
print(f"\nitems {before} -> {after}")

if f.exists():
    f.unlink()
    print(f"deleted {f.name}")
else:
    print("file was already gone")
