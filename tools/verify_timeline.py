#!/usr/bin/env python3
"""verify_timeline.py - hold the curated timeline to its own schema.

The timeline is the one page on this site that makes a claim about *when*
something happened, across three thousand years. A typo in a sort year moves an
entry to the wrong century and no link check can see it; a missing domain makes
an entry unfilterable; a citation with no URL is the `retrievable` defect this
repository has now met four times.

So the checks here are about the promises the fields make:

  * every entry has every required field, and the types are the types the
    builder renders;
  * domain and era are members of the lists the page filters on;
  * sort_year agrees with the year string, and the file is in sort order;
  * every citation has a locator if it claims to be openable, and no citation
    is a note to self;
  * ids are unique, tags are non-empty, and no tag is a sentence.

It cannot check that a date is true. That is what the citations are for, and
what `--check-urls` is for: a separate, explicit network pass, never part of
the build.
"""
from __future__ import annotations

import json
import pathlib
import re
import sys
import urllib.request

ROOT = pathlib.Path(__file__).resolve().parent.parent
DATA = ROOT / "data" / "timeline.json"

DOMAINS = [
    "Myth & Legend",
    "Literature & Print",
    "Broadcast & Film",
    "Politics & News",
    "Music & Fan Culture",
    "Digital & Synthetic",
]
ERAS = [
    "Pre-Modern",
    "Early Mass Media",
    "The Broadcast Age",
    "Digital & Algorithmic",
    "Synthetic Era",
]
REQUIRED = [
    "id", "year", "sort_year", "title", "domain", "era", "summary",
    "parasocial_analysis", "primary_source_or_artifact", "tags", "citations",
]
STATUSES = {"retrievable", "verified", "unverified"}
PLACEHOLDERS = re.compile(r"\b(verify|todo|tbd|fixme|xxx|the entry as a whole)\b", re.I)
ID_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
# CE only, deliberately. A hyphen in "1830s-1850s" is a range separator, not a
# minus sign; treating it as one made 1836 fall outside its own year. If a BCE
# entry is ever added, sort_year is still authoritative and this check has to
# learn the sign rather than guess it from punctuation.
YEAR_RE = re.compile(r"(?<!\d)(\d{1,4})(?!\d)")


def fail(errors, msg):
    errors.append(msg)


def main() -> int:
    if not DATA.exists():
        print(f"MISSING {DATA}")
        return 1
    try:
        doc = json.loads(DATA.read_text(encoding="utf-8"))
    except ValueError as exc:
        print(f"INVALID JSON: {exc}")
        return 1

    errors: list[str] = []
    notes: list[str] = []

    for key in ("_note", "domains", "eras", "entries"):
        if key not in doc:
            fail(errors, f"top-level key missing: {key}")
    if errors:
        print("\n".join(errors))
        return 1

    if doc["domains"] != DOMAINS:
        fail(errors, "domains list is not the six the page filters on")
    if doc["eras"] != ERAS:
        fail(errors, "eras list is not the five the schema defines")

    entries = doc["entries"]
    if not isinstance(entries, list) or not entries:
        fail(errors, "entries is not a non-empty list")
        print("\n".join(errors))
        return 1
    if len(entries) != 22:
        notes.append(f"{len(entries)} entries (the seed is 22; growth is allowed)")

    seen_ids: set[str] = set()
    seen_titles: set[str] = set()
    last_sort = None
    for n, e in enumerate(entries, 1):
        where = f"entry {n} ({e.get('id', 'no id')})"
        for key in REQUIRED:
            if key not in e:
                fail(errors, f"{where}: missing {key}")
        if errors and any(x.startswith(where) for x in errors):
            continue

        eid = str(e["id"])
        if not ID_RE.match(eid):
            fail(errors, f"{where}: id is not a lowercase slug")
        if eid in seen_ids:
            fail(errors, f"{where}: duplicate id")
        seen_ids.add(eid)

        title = str(e["title"]).strip()
        if len(title) < 8:
            fail(errors, f"{where}: title is too short")
        if title.lower() in seen_titles:
            fail(errors, f"{where}: duplicate title")
        seen_titles.add(title.lower())

        if e["domain"] not in DOMAINS:
            fail(errors, f"{where}: domain {e['domain']!r} is not in the list")
        if e["era"] not in ERAS:
            fail(errors, f"{where}: era {e['era']!r} is not in the list")

        try:
            sort = int(e["sort_year"])
        except (TypeError, ValueError):
            fail(errors, f"{where}: sort_year is not an integer")
            sort = None
        if sort is not None:
            if last_sort is not None and sort < last_sort:
                fail(errors, f"{where}: sort_year {sort} runs backwards "
                             f"after {last_sort}")
            last_sort = sort
            years = [int(y) for y in YEAR_RE.findall(str(e["year"]))]
            if not years:
                fail(errors, f"{where}: year {e['year']!r} contains no year")
            elif sort not in years and not (
                len(years) > 1 and min(years) <= sort <= max(years)
            ):
                fail(errors, f"{where}: sort_year {sort} is not in year "
                             f"{e['year']!r}")

        for field, low in (("summary", 80), ("parasocial_analysis", 300)):
            text = str(e[field]).strip()
            if len(text) < low:
                fail(errors, f"{where}: {field} is {len(text)} chars, "
                             f"under the {low} minimum")

        tags = e["tags"]
        if not isinstance(tags, list) or not tags:
            fail(errors, f"{where}: tags is not a non-empty list")
        else:
            if len(set(tags)) != len(tags):
                fail(errors, f"{where}: duplicate tag")
            for t in tags:
                if not isinstance(t, str) or not re.match(r"^[a-z0-9]+(?:-[a-z0-9]+)*$", t):
                    fail(errors, f"{where}: tag {t!r} is not a lowercase slug")

        cits = e["citations"]
        if not isinstance(cits, list) or not cits:
            fail(errors, f"{where}: citations is not a non-empty list")
        else:
            for c in cits:
                for key in ("citation", "url", "status", "note"):
                    if key not in c:
                        fail(errors, f"{where}: citation missing {key}")
                status = str(c.get("status", ""))
                if status not in STATUSES:
                    fail(errors, f"{where}: citation status {status!r} is not "
                                 f"one of {sorted(STATUSES)}")
                if status == "retrievable" and not str(c.get("url", "")).startswith("http"):
                    fail(errors, f"{where}: retrievable citation has no URL")
                if not str(c.get("url", "")).startswith("https://"):
                    fail(errors, f"{where}: citation URL is not https")
                for key in ("citation", "note"):
                    if PLACEHOLDERS.search(str(c.get(key, ""))):
                        fail(errors, f"{where}: citation {key} contains a "
                                     f"note-to-self")
                if len(str(c.get("citation", "")).strip()) < 8:
                    fail(errors, f"{where}: citation string is too short")
                if len(str(c.get("note", "")).strip()) < 8:
                    fail(errors, f"{where}: citation note is too short")

    # The three UI era buckets must cover all five data eras. If a new era is
    # added to the schema and not mapped, the entry exists and is invisible.
    ui_era = {
        "Pre-Modern": "pre",
        "Early Mass Media": "modern",
        "The Broadcast Age": "modern",
        "Digital & Algorithmic": "digital",
        "Synthetic Era": "digital",
    }
    for era in ERAS:
        if era not in ui_era:
            fail(errors, f"era {era!r} has no UI bucket")

    if errors:
        print(f"timeline: {len(errors)} problem(s)")
        for x in errors:
            print("  " + x)
        return 1

    # The data can be perfect while the page renders nothing. The source tier
    # runs after build_cards, so check the artefact as well as the file it was
    # built from: every card must have a panel, and every panel must have a
    # card. A slide-over whose :target id is missing is a link to nowhere that
    # no link checker treats as broken, because the fragment is on the page.
    page = ROOT / "timeline" / "index.html"
    corpus = ROOT / "timeline" / "corpus" / "index.html"
    if page.exists():
        html = page.read_text(encoding="utf-8")
        n_cards = html.count('class="tlc-card"')
        n_panels = html.count('class="tlc-panel"')
        if n_cards != len(entries):
            fail(errors, f"rendered cards: {n_cards} for {len(entries)} entries")
        if n_panels != len(entries):
            fail(errors, f"rendered panels: {n_panels} for {len(entries)} entries")
        for e in entries:
            if f'id="tl-{e["id"]}"' not in html:
                fail(errors, f"panel id missing from the page: tl-{e['id']}")
            if f'href="#tl-{e["id"]}"' not in html:
                fail(errors, f"card link missing from the page: tl-{e['id']}")
        if not corpus.exists():
            fail(errors, "the corpus page is missing at timeline/corpus/")
        elif 'href="../index.html"' not in corpus.read_text(encoding="utf-8"):
            fail(errors, "the corpus page does not link back to the curated page")
    else:
        notes.append("timeline/index.html not built; artefact checks skipped")

    if errors:
        print(f"timeline: {len(errors)} problem(s)")
        for x in errors:
            print("  " + x)
        return 1

    print(f"timeline: {len(entries)} entries, "
          f"{len(seen_ids)} ids, "
          f"{sum(len(e['citations']) for e in entries)} citation records")
    print(f"  domains: {len(set(e['domain'] for e in entries))} of {len(DOMAINS)}")
    print(f"  eras:    {len(set(e['era'] for e in entries))} of {len(ERAS)}")
    print(f"  tags:    {len(set(t for e in entries for t in e['tags']))} distinct")
    for note in notes:
        print("  note: " + note)

    if "--check-urls" in sys.argv:
        for e in entries:
            for c in e["citations"]:
                url = c["url"]
                try:
                    req = urllib.request.Request(
                        url, headers={"User-Agent": "ParasocializeAudit/1.0"})
                    with urllib.request.urlopen(req, timeout=25) as r:
                        print(f"  {r.status} {e['id']}: {url}")
                except Exception as exc:  # noqa: BLE001 - report the real failure
                    print(f"  ERR {e['id']}: {type(exc).__name__} {url}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
