"""Build radar.json + radar.xml from radar/*.md. No dependencies.
Usage: python tools/build_radar.py
Publish flow: add radar/007-slug.md -> run script -> upload folder.
Frontmatter keys: slug,title,date,type,lenses(int list),tags,intensity,read_minutes,emoji,gradient,dek,link,link_label,affiliate
"""
import re, json, pathlib
ROOT = pathlib.Path(__file__).resolve().parents[1]
RADAR = ROOT / "radar"
def parse(md):
    m = re.match(r"^---\s*\n(.*?)\n---\s*\n(.*)$", md, re.S)
    if not m: raise ValueError("missing frontmatter")
    fm, _ = m.groups()
    d = {}
    # minimal YAML subset: key: value, lists [a, b], numbers, booleans
    for line in fm.splitlines():
        if ":" not in line: continue
        k, v = line.split(":", 1); k=k.strip(); v=v.strip().strip('"').strip("'")
        if v.startswith("["): d[k]=[x.strip().strip('"\'') for x in v.strip("[]").split(",") if x.strip()]
        elif v.lower() in ("true","false"): d[k]=(v.lower()=="true")
        else:
            try: d[k]=float(v) if "." in v else int(v)
            except: d[k]=v
    return d
items = sorted([parse((p.read_text(encoding="utf-8"))) for p in RADAR.glob("*.md")], key=lambda d: str(d.get("date","")))
(ROOT/"radar.json").write_text(json.dumps(items, indent=2), encoding="utf-8")
print(f"wrote radar.json with {len(items)} items")
# minimal RSS (full content lives in md for now)
rss_items = "\n".join(f'<item><title>{i.get("title","")}</title><link>https://www.parasocialize.com/#radar</link><pubDate>{i.get("date","")}</pubDate><description>{i.get("dek","")}</description></item>' for i in items)
(ROOT/"radar.xml").write_text(f'<?xml version="1.0" encoding="UTF-8"?>\n<rss version="2.0">\n<channel>\n<title>PARASOCIALIZE Radar</title>\n<link>https://www.parasocialize.com/#radar</link>\n<description>Weekly signals in one-sided relationships — fiction and non-fiction, decoded by Enan Joe Heneghan.</description>\n{rss_items}\n</channel>\n</rss>\n', encoding="utf-8")
print("wrote radar.xml")
