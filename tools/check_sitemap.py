#!/usr/bin/env python3
"""check_sitemap.py - does the sitemap describe the site that was deployed?

WHY THIS EXISTS
The sitemap was built by a hand-maintained list of URLs plus loops over the data
files. That is a list of everything somebody remembered. On 2026-11-01 the
deployed tree held 356 pages and the sitemap listed 355, and the five that were
missing included two `noindex` pages (correct) and `exceptions/` and `ledger/`
(not correct). Both are ordinary reader pages: `/ledger/` is linked from the
footer of all 354 other pages and publishes its own feed, and `/exceptions/` is
linked from `/taxonomy/`. Neither carried a `noindex`, so both were indexable
and neither was offered to a crawler.

The site already states the rule this check enforces, in `build_sitemap`:
"a page a reader can reach but a crawler cannot is only half published". The
rule was written down and then enforced by nobody, which is how it drifted.

Two directions, because one alone is not enough:
  - a page that is deployed, indexable and absent from the sitemap is one the
    crawler is not told about;
  - a URL in the sitemap with no file behind it is a 404 handed to the crawler
    on purpose, which is worse.

`noindex` pages are exempt in the first direction, and `/desk/` is the reason:
it is a signoff queue for whoever maintains the site, not a reader page, and it
says so in its own head.

Exit 1 on a failure, naming the page.
"""
from __future__ import annotations

import json
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
DIST = ROOT / "dist"
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

SITE = "https://www.parasocialize.com"
LOC = re.compile(r"<loc>([^<]+)</loc>")
NOINDEX = re.compile(r'<meta[^>]+name="robots"[^>]+content="[^"]*noindex', re.I)
# A 404 handler is served by the platform at whatever URL failed; it is not a
# page somebody navigates to and it must not be offered for indexing.
EXEMPT = {"404.html"}


def to_file(loc: str) -> str:
    path = loc[len(SITE):] if loc.startswith(SITE) else loc
    path = path.split("#")[0].split("?")[0].strip("/")
    if path == "":
        return "index.html"
    if path.endswith("/"):
        return path + "/index.html"
    if not path.endswith(".html"):
        return path + "/index.html"
    return path


def main() -> int:
    path = ROOT / "sitemap.xml"
    if not path.is_file():
        print("FAIL: sitemap.xml is missing")
        return 1
    if not DIST.is_dir():
        print("FAIL: dist/ is missing - build the deploy tree first")
        return 1

    locs = [to_file(u) for u in LOC.findall(path.read_text(encoding="utf-8"))]
    listed = set(locs)
    seen = set()
    duplicates = []
    for u in locs:
        if u in seen:
            duplicates.append(u)
        seen.add(u)

    deployed = {}
    for p in DIST.rglob("*.html"):
        rel = p.relative_to(DIST).as_posix()
        deployed[rel] = p

    missing = []
    for rel, p in sorted(deployed.items()):
        if rel in EXEMPT:
            continue
        head = p.read_text(encoding="utf-8", errors="replace")[:4000]
        if NOINDEX.search(head):
            continue
        if rel not in listed:
            missing.append(rel)

    ghost = sorted(u for u in listed if u not in deployed)

    problems = 0
    if duplicates:
        problems += len(duplicates)
        print(f"FAIL: {len(duplicates)} duplicate sitemap entr(ies): "
              f"{', '.join(sorted(set(duplicates))[:8])}")
    if missing:
        problems += len(missing)
        print(f"FAIL: {len(missing)} indexable deployed page(s) are not in the "
              f"sitemap: {', '.join(missing[:8])}")
    if ghost:
        problems += len(ghost)
        print(f"FAIL: {len(ghost)} sitemap URL(s) have no deployed file: "
              f"{', '.join(ghost[:8])}")
    if problems:
        print("Add them to build_sitemap(), or mark the page noindex if it is "
              "not for readers.")
        return 1

    print(f"ok: sitemap lists {len(listed)} URLs; every indexable page is in it "
          f"and every entry resolves")
    return 0


if __name__ == "__main__":
    sys.exit(main())
