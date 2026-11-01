#!/usr/bin/env python3
"""check_redirects.py - does `_redirects` actually fit in the budget it is given?

WHY THIS EXISTS
Cloudflare Pages reads `_redirects` from the deploy root and applies the rules in
order. It does not warn when the file is too long - it just stops applying rules,
so the tail of the file becomes decoration that looks exactly like a working
redirect in the source. On 2026-11-01 the file held 270 rules: `/aisle/` (rule 2)
redirected, `/e/krapp-last-tape` (rule 101) redirected, and `/e/marilyn-diptych`
(rule 110) returned 404 - verified against a live deployment, with `build_deploy`
green and every gate passing. 147 of the 255 `/e/` end-card links were dead for
however long the file had been that long.

Nothing in this repository could see it, because every other check asks whether
the RULES ARE WRITTEN, never whether they would be APPLIED. This one asks two
questions:

  1. Is the file inside the budget, counting static and dynamic rules the way
     the platform does?
  2. Does every URL the site hands a reader - every `/e/<id>` the encyclopedia
     prints, every renamed radar slug - have a rule that can serve it?

The budget number here is deliberately conservative. The documented limits are
2,000 static and 100 dynamic rules; the observed behaviour on this project was a
cutoff an order of magnitude below the static figure. A gate that waits for a
documented number while the platform fails earlier is a gate that reports on its
own paperwork. 100 total is the number held here, and the site now uses 16, so
the headroom is the point.

Exit 1 on a failure, with the rule that broke it.
"""
from __future__ import annotations

import json
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
DIST = ROOT / "dist"
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

BUDGET = 100          # total rules; documented 2,000 static + 100 dynamic
DYNAMIC_BUDGET = 100


def rules(path: pathlib.Path):
    out = []
    for n, raw in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        out.append((n, line))
    return out


def main() -> int:
    path = DIST / "_redirects"
    if not path.is_file():
        print("FAIL: dist/_redirects is missing")
        return 1

    parsed = []
    for n, line in rules(path):
        parts = line.split()
        if len(parts) not in (2, 3):
            print(f"FAIL: dist/_redirects line {n} is not `from to [code]`: {line!r}")
            return 1
        src, dst = parts[0], parts[1]
        parsed.append((n, src, dst))

    dynamic = [r for r in parsed if "*" in r[1] or ":" in r[2]]
    if len(parsed) > BUDGET:
        print(f"FAIL: dist/_redirects has {len(parsed)} rules; this project holds "
              f"{BUDGET} because Pages silently stops applying the tail. "
              f"Collapse the repeating set into a splat rule or move the mapping "
              f"into a generated page.")
        return 1
    if len(dynamic) > DYNAMIC_BUDGET:
        print(f"FAIL: {len(dynamic)} dynamic rules, budget {DYNAMIC_BUDGET}")
        return 1

    # ---- every /e/ URL the site prints must be served ---------------------
    def covers(url: str) -> bool:
        for _n, src, _dst in parsed:
            if src == url:
                return True
            if src.endswith("*") and url.startswith(src[:-1]):
                return True
        return False

    enc = ROOT / "data" / "encyclopedia.json"
    missing = []
    if enc.is_file():
        entries = json.loads(enc.read_text(encoding="utf-8")).get("entries", [])
        for e in entries:
            url = f"/e/{e['id']}"
            if not covers(url):
                missing.append(url)
    if missing:
        print(f"FAIL: {len(missing)} /e/ end-card links have no redirect "
              f"(first: {', '.join(missing[:5])})")
        return 1

    # ---- every renamed radar slug must be served --------------------------
    shop = ROOT / "data" / "shop.json"
    missing = []
    if shop.is_file():
        data = json.loads(shop.read_text(encoding="utf-8"))
        for r in data.get("_retired_sources", []):
            old = r.get("slug")
            if old and not covers(f"/radar/{old}.html"):
                missing.append(f"/radar/{old}.html")
    if missing:
        print(f"FAIL: {len(missing)} retired radar slugs have no redirect "
              f"(first: {', '.join(missing[:5])})")
        return 1

    print(f"ok: {len(parsed)} redirect rules ({len(dynamic)} dynamic) of "
          f"{BUDGET}; every /e/ end card and retired slug is served")
    return 0


if __name__ == "__main__":
    sys.exit(main())
