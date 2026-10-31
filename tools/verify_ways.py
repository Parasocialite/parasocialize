#!/usr/bin/env python3
"""The eight ways on the front page, and the pages behind them.

WHY THIS EXISTS
The front page's hub used to be ten section tiles, and the classification that
the site actually argues with is the eight attachment categories. Moving the
front page onto that axis makes two claims that can silently stop being true:
that all eight ways are on the page, and that a reader can get from a tile to
everything filed on that way. Neither is visible from any other gate.

So this reads the deployed tree, not the source:
  - the front page carries eight `.hub` tiles, one per attachment category,
    and each links to its way;
  - each ways page links every story and every entry placed on that category,
    plus the taxonomy definition and the other seven ways;
  - a category with no story says so, and its front-page tile counts entries
    rather than claiming stories it does not have;
  - the sitemap lists every ways page.

A category that gains its first story changes the tile copy from entries to
stories; a placement that moves must move on the page. Both are checked here.
"""
import json, pathlib, re, sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
DIST = ROOT / "dist"
sys.stdout.reconfigure(encoding="utf-8")


def read(p):
    return p.read_text(encoding="utf-8", errors="replace")


def main():
    tax = json.loads(read(ROOT / "data" / "taxonomy.json"))
    cats = tax["attachment"]
    spl = json.loads(read(ROOT / "data" / "story_placements.json"))["placements"]
    pla = json.loads(read(ROOT / "data" / "taxonomy_placements.json"))["assignments"]
    if not DIST.exists():
        sys.exit("REFUSING: dist/ is missing. build_deploy.py must run first.")
    pages = list(DIST.rglob("*.html"))
    if len(pages) < 100:
        sys.exit(f"REFUSING: dist/ holds {len(pages)} pages. Measuring a tree "
                 f"this small is measuring the wrong tree.")

    failures = []
    index = read(DIST / "index.html")
    if "Eight ways it shows up" not in index:
        failures.append("front page does not carry the eight-ways kicker")
    tiles = re.findall(
        r'<a class="hub"[^>]*href="ways/([a-z-]+)/index\.html"(.*?)</a>',
        index, re.S)
    n_tiles = len(re.findall(r'<a class="hub"', index))
    if n_tiles != 8:
        failures.append(f"front page carries {n_tiles} hub tiles, expected 8")
    got = [c for c, _ in tiles]
    for a in cats:
        if a["id"] not in got:
            failures.append(f"{a['id']}: not a front-page tile")
    if sorted(got) != sorted(a["id"] for a in cats):
        failures.append(f"front-page tiles are {sorted(got)}, expected "
                        f"{sorted(a['id'] for a in cats)}")

    sitemap = read(DIST / "sitemap.xml")
    for a in cats:
        cid = a["id"]
        page = DIST / "ways" / cid / "index.html"
        if not page.exists():
            failures.append(f"{cid}: ways page missing")
            continue
        body = read(page)
        page_tile = next((seg for c, seg in tiles if c == cid), "")
        mine = [s for s, v in spl.items() if v.get("cat") == cid]
        entries = [e for e, v in pla.items() if v.get("cat") == cid]
        for slug in mine:
            if f"../../radar/{slug}.html" not in body:
                failures.append(f"{cid}: story {slug} is not on its way page")
        for eid in entries:
            if f"../../encyclopedia/{eid}.html" not in body:
                failures.append(f"{cid}: entry {eid} is not on its way page")
        if f"../../taxonomy/index.html#tx-{cid}" not in body:
            failures.append(f"{cid}: no link to its definition")
        for b in cats:
            if b["id"] != cid and f"../../ways/{b['id']}/index.html" not in body:
                failures.append(f"{cid}: does not link the way {b['id']}")
        if not mine:
            if "No story is filed on this way yet." not in body:
                failures.append(f"{cid}: no stories and no honest empty state")
            if "entries →" not in page_tile:
                failures.append(f"{cid}: no stories but the tile does not "
                                f"count entries")
            if "stories →" in page_tile or "story →" in page_tile:
                failures.append(f"{cid}: no stories but the tile claims one")
        else:
            if not ("stories →" in page_tile or "story →" in page_tile):
                failures.append(f"{cid}: has {len(mine)} stories but the tile "
                                f"does not count them")
        if f"/ways/{cid}/" not in sitemap:
            failures.append(f"{cid}: missing from sitemap.xml")

    if failures:
        print("FAIL")
        for f in failures:
            print(" ", f)
        return 1
    print(f"ok · {len(cats)} ways · {len(spl)} placed stories · "
          f"{len(pla)} placed entries · 8 front-page tiles")
    return 0


if __name__ == "__main__":
    sys.exit(main())
