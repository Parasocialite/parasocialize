import json
import pathlib
import shutil

root = pathlib.Path("top8/archive")
hist = json.loads(pathlib.Path("data/top8_history.json").read_text(encoding="utf-8"))
days = {str(d["date"])[:10] for d in hist.get("days") or []}
feat = json.loads(pathlib.Path("data/features.json").read_text(encoding="utf-8"))
slugs = {L.get("slug") for L in feat.get("lists") or [] if L.get("slug")}

removed = []
for p in sorted(root.iterdir()):
    if not p.is_dir():
        continue
    n = p.name
    if len(n) == 10 and n[:2] == "20" and n not in days:
        shutil.rmtree(p)
        removed.append(n)
    elif n.startswith("top8-") and n not in slugs:
        shutil.rmtree(p)
        removed.append(n)
print("pruned:", removed or "none")
