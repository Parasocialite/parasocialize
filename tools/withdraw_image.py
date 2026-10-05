"""Withdraw an image, keeping the reason.

Two shapes of withdrawal, and the difference matters:

  reject   the picture was the wrong picture. Record and file both go. Nothing
           is learned by keeping a row that points at a deleted asset.

  withhold the picture is real, freely licensed, and must not be shown. The
           citation survives - the corpus should still be able to say a
           screenshot of this kind exists and is openable - and the file goes.

`8432d33b1d39ab` is the second kind and the reason it exists: a Replika
conversation in which a user asks for methods and the bot returns an enumerated
list of them, rendering on eleven pages as decoration. Deleting the row would
have hidden the defect and lost the finding. This keeps it, with `local: null`
and the reason in `withdrawn_reason`, so the next person to pick this entry up
reads why rather than re-fetching it.

Asserts the count before and after, and refuses to write if it moved.
"""
import json
import pathlib
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ROOT = pathlib.Path(r"C:\Users\paras\Documents\Default Project\parasocialize")
APPLY = "--apply" in sys.argv
KEEP = "--keep-record" in sys.argv

args = [a for a in sys.argv[1:] if not a.startswith("--")]
if not args:
    sys.exit("usage: withdraw_image.py <slug-or-hash> \"<reason>\" "
             "[--keep-record] [--apply]")
TARGET = args[0]
REASON = args[1] if len(args) > 1 else "withdrawn on review, reason not recorded"

p = ROOT / "data" / "images.json"
data = json.loads(p.read_text(encoding="utf-8"))
before = len(data["items"])

hits = [i for i in data["items"]
        if TARGET in str(i.get("local", "")) or TARGET == i.get("slug")]
if len(hits) != 1:
    sys.exit(f"expected exactly 1 record matching {TARGET!r}, found {len(hits)}")
rec = hits[0]
f = ROOT / rec["local"] if rec.get("local") else None

print(f"record: {rec.get('slug')}  kind={rec.get('kind')}  "
      f"local={rec.get('local')}")
print(f"file  : {'exists' if f and f.exists() else 'MISSING'}")
print(f"reason: {REASON[:100]}...")
print(f"mode  : {'keep the record, null the file' if KEEP else 'delete both'}")

if not APPLY:
    print("\ndry run. re-run with --apply")
    raise SystemExit(0)

if KEEP:
    rec["local"] = None
    rec["kind"] = "withheld"
    rec["withdrawn"] = True
    rec["looked"] = "2026-10-05"
    rec["withdrawn_reason"] = REASON
    rec["look_reason"] = REASON
    if isinstance(rec.get("src"), dict):
        # the citation is still true and still worth having; only its use as an
        # image is refused, and saying so beats deleting the evidence
        rec["src"]["usable_as_image"] = False
        rec["src"]["withheld_note"] = (
            "Openable and freely licensed, but not used as an image. See "
            "withdrawn_reason.")
else:
    data["items"] = [i for i in data["items"] if i is not rec]

after = len(data["items"])
if after != before and after != before - 1:
    sys.exit(f"refusing to write: item count moved {before} -> {after}")

tmp = p.with_suffix(".json.tmp")
tmp.write_text(json.dumps(data, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
check = json.loads(tmp.read_text(encoding="utf-8"))
if len(check["items"]) != after or not check.get("items"):
    sys.exit("refusing to write: reparse did not reconcile")
tmp.replace(p)
print(f"\nitems {before} -> {after}")

if f and f.exists():
    size = f.stat().st_size
    f.unlink()
    print(f"deleted {f.name} ({size/1024:.0f} KB)")
elif f:
    print("file was already gone")
else:
    print("no file to delete")
