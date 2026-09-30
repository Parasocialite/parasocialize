import json, collections, pathlib
p = pathlib.Path(__file__).resolve().parent.parent
d = json.loads((p / "data" / "shop.json").read_text(encoding="utf-8"))
c = collections.Counter(x["section"] for x in d["cards"])
print(f"\n{len(d['cards'])} cards")
for a in d["sections"]:
    bar = "#" * c.get(a["id"], 0)
    print(f"  {a['glyph']} {a['sign']:<10} {c.get(a['id'],0):>2}  {bar}")
print()
print("  states    :", dict(collections.Counter(x["state"] for x in d["cards"])))
print("  laws      :", dict(sorted(collections.Counter(x["law"] for x in d["cards"]).items())))
print("  sources   :", sum(len(x["sources"]) for x in d["cards"]))
print("  need links:", sum(1 for x in d["cards"] if x.get("needs") == "link"))
print("  no shelf  :", sum(1 for x in d["cards"] if not x.get("shelf")))
print()
print("  newest 5:")
for x in d["cards"][:5]:
    print(f"    {x['filed']}  [{x['section']:<10}] {x['headline'][:62]}")
