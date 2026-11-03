#!/usr/bin/env python3
"""check_top8_archive.py - does every recorded day have a page, and does the
calendar reach it?

WHY THIS EXISTS
The dated archive is generated from `data/top8_history.json`. A day can be in
that file and have no page, a page can be linked from nowhere, and the calendar
can drift from the history - three failures that look like a working archive
until somebody clicks. This checks the three against each other:

    every recorded day -> a page
    every page        -> eight items and a canonical URL
    every page        -> an inbound link from the archive index

A day in the history with no page is a broken promise; a page with no inbound
link is a page a reader cannot find, which this repository has already paid for
once (the classroom and the three Case Files).
"""
from __future__ import annotations

import json
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
HIST = ROOT / "data" / "top8_history.json"
ARCHIVE = ROOT / "top8" / "archive"
INDEX = ARCHIVE / "index.html"
sys.stdout.reconfigure(encoding="utf-8", errors="replace")


def main() -> int:
    try:
        days = json.loads(HIST.read_text(encoding="utf-8")).get("days") or []
    except (OSError, ValueError) as exc:
        print(f"FAIL: cannot read {HIST.name}: {exc}")
        return 1
    days = [d for d in days if d.get("items")]
    if not days:
        print("FAIL: no recorded days; refusing to call an empty archive correct")
        return 1

    if not INDEX.is_file():
        print("FAIL: top8/archive/index.html is missing")
        return 1
    index = INDEX.read_text(encoding="utf-8")

    problems = []
    for d in days:
        iso = str(d["date"])[:10]
        page = ARCHIVE / iso / "index.html"
        if not page.is_file():
            problems.append(f"{iso}: recorded but no page")
            continue
        html = page.read_text(encoding="utf-8")
        n = html.count('class="t8d-item"')
        if n != len(d["items"]):
            problems.append(f"{iso}: {n} items rendered, {len(d['items'])} recorded")
        if f'<link rel="canonical" href="https://www.parasocialize.com/top8/archive/{iso}/">' not in html:
            problems.append(f"{iso}: canonical URL does not point at its own date")
        if "Share / cite this list" not in html:
            problems.append(f"{iso}: no share/cite block")
        if f'href="{iso}/index.html"' not in index:
            problems.append(f"{iso}: no link from the archive index")

    if problems:
        print(f"{len(problems)} problem(s):")
        for p in problems[:20]:
            print("  " + p)
        return 1

    print(f"ok: {len(days)} recorded days, one page each, all linked from the index")
    return 0


if __name__ == "__main__":
    sys.exit(main())
