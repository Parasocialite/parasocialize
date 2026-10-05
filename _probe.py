import json
import pathlib
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ROOT = pathlib.Path(r"C:\Users\paras\Documents\Default Project\parasocialize")
enc = json.loads((ROOT / "data" / "encyclopedia.json").read_text(encoding="utf-8"))["entries"]
recs = [s for e in enc for s in e.get("sources", [])]
print("  entries   :", len(enc))
print("  relations :", sum(len(e.get("relations", [])) for e in enc))
print("  records   :", len(recs))
print("  with url  :", sum(1 for s in recs if s.get("url")))
print("  thesis    :", sum(1 for e in enc if e.get("provenance") == "thesis"))
print("  dist html :", len(list((ROOT / "dist").rglob("*.html"))))
import collections
c = collections.Counter(m for e in enc for m in (e.get("medium") or []))
print("\n  medium distribution:")
for m, n in c.most_common():
    print(f"    {m:26s} {n}")
