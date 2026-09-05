"""One-off link audit: every internal href/src in html must resolve. Prints failures."""
import re, pathlib
ROOT = pathlib.Path(__file__).resolve().parents[1]
pages = list(ROOT.glob("*.html")) + list((ROOT / "radar").glob("*.html")) + list((ROOT / "cases").glob("*.html"))
pages += [ROOT / "guide" / "index.html", ROOT / "tip" / "index.html", ROOT / "audit" / "index.html", ROOT / "classroom" / "index.html", ROOT / "signal" / "latest.html"]
fails = []
ids_cache = {}
def ids_of(p):
    if p not in ids_cache:
        try: ids_cache[p] = set(re.findall(r'id="([^"]+)"', p.read_text(encoding="utf-8")))
        except Exception: ids_cache[p] = set()
    return ids_cache[p]
for pg in pages:
    if not pg.exists():
        fails.append(f"MISSING PAGE {pg.relative_to(ROOT)}"); continue
    base = pg.parent
    text = pg.read_text(encoding="utf-8")
    for m in re.finditer(r'(?:href|src)="([^"#]+)(#[^"]*)?"', text):
        url, frag = m.group(1), m.group(2) or ""
        if url.startswith(("http", "mailto:", "data:")) or not url: continue
        target = (base / url)
        if url.startswith("/"): target = ROOT / url.lstrip("/")
        if not target.exists():
            fails.append(f"{pg.relative_to(ROOT)} -> {url} MISSING"); continue
        if frag and target.suffix == ".html":
            if frag[1:] not in ids_of(target):
                fails.append(f"{pg.relative_to(ROOT)} -> {url}{frag} NO SUCH ID")
print(f"checked {len(pages)} pages")
if fails:
    print("\n".join(fails))
    raise SystemExit(1)
print("ALL LINKS RESOLVE")
