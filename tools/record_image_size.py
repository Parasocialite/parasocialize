"""Record the size of the file on disk alongside the size the model produced.

`generation.size` is what ComfyUI emitted - 1152x560 - and it stays that, because
it is the honest answer to "what did you ask for". But every generated file was
then margin-trimmed to 1084x528, and only `the-dog` recorded that in `crop`.
So six records said 1152x560 about a file that is 1084x528 with no field
accounting for the difference.

That is the "a status field is a promise" family from AGENTS.md, one field over:
the value is not wrong, it just does not describe the thing a tool reading it
will open. `generation.final` now carries the dimensions of the PNG on disk, and
image_audit checks it against the PNG's own IHDR - because a recorded size that
drifts from the file is the same defect as `kind: exact` derived from a filename.

Asserts the item count before and after, and refuses to write if it moved.
"""
import json
import pathlib
import struct
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ROOT = pathlib.Path(r"C:\Users\paras\Documents\Default Project\parasocialize")
APPLY = "--apply" in sys.argv

p = ROOT / "data" / "images.json"
data = json.loads(p.read_text(encoding="utf-8"))
before = len(data["items"])


def png_size(path: pathlib.Path):
    raw = path.read_bytes()
    if raw[:8] != b"\x89PNG\r\n\x1a\n":
        return None
    return "%dx%d" % struct.unpack(">II", raw[16:24])


changed = []
for it in data["items"]:
    loc = it.get("local") or ""
    gen = it.get("generation")
    if not gen or "/generated/" not in loc:
        continue
    f = ROOT / loc
    if not f.exists():
        print(f"  SKIP {it['slug']}: {loc} is not on disk")
        continue
    actual = png_size(f)
    if actual is None:
        print(f"  SKIP {it['slug']}: not a PNG")
        continue
    if gen.get("final") == actual:
        continue
    print(f"  {it['slug']:<22} generated {gen.get('size'):<10} on disk {actual}")
    changed.append((it, actual))

print(f"\n{len(changed)} of "
      f"{sum(1 for i in data['items'] if (i.get('generation') or {}))} generated "
      f"records need final")
if not APPLY:
    print("dry run. re-run with --apply")
    raise SystemExit(0)

for it, actual in changed:
    it["generation"]["final"] = actual

after = len(data["items"])
if after != before:
    sys.exit(f"refusing to write: item count moved {before} -> {after}")

tmp = p.with_suffix(".json.tmp")
tmp.write_text(json.dumps(data, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
re_parsed = json.loads(tmp.read_text(encoding="utf-8"))
if len(re_parsed["items"]) != before:
    sys.exit("refusing to write: reparse did not reconcile")
tmp.replace(p)
print(f"written. items {before}, unchanged.")
