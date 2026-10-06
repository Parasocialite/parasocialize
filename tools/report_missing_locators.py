"""Where the 130 records with no locator actually are, and what shape they are.

AGENTS item 21 sets the order of work and it has not changed: **complete the
citation first - author, year, title, venue - and the locator then becomes
mechanically checkable.** Searching first produces candidates that cannot be
confirmed, and a candidate that cannot be confirmed is exactly how `kind: exact`
happened.

So before fetching anything, this reports the shape of the debt:
  - which entries carry the most locator-less records (where the effort is)
  - for each, the citation string as written, and whether it even names a work
  - which ones are book-length (publisher pages are the cheap win)
  - which have a DOI anywhere in the record already
  - which are exact/prefix twins of a record that DOES have a locator - those are
    mechanical and `attach_twin_locators.py` should have taken them, so any
    left are cases the twin rules refused, and the refusal reason matters
"""
import collections
import json
import pathlib
import re
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ROOT = pathlib.Path(__file__).resolve().parent.parent
enc = json.loads((ROOT / "data" / "encyclopedia.json").read_text(encoding="utf-8"))
entries = enc["entries"]

all_recs = [(e["id"], e["title"], r) for e in entries for r in e.get("sources", [])]
missing = [(i, t, r) for i, t, r in all_recs if not r.get("url")]

print(f"  records total        : {len(all_recs)}")
print(f"  with a locator (url) : {len(all_recs) - len(missing)}")
print(f"  WITHOUT              : {len(missing)}")
print(f"  entries affected     : {len({i for i, _, _ in missing})}")

by_entry = collections.Counter(i for i, _, _ in missing)
print(f"\n  top 20 entries by missing records:")
for eid, n in by_entry.most_common(20):
    print(f"    {n:>3}  {eid}")

print(f"\n  statuses among the {len(missing)}:")
for st, n in collections.Counter(r.get("status") for _, _, r in missing).most_common():
    print(f"    {st:>14}  {n}")

# Does the citation string name a work at all? No title and no author means
# there is nothing to look up, only something to go and find out.
print(f"\n  how many of the {len(missing)} name nothing checkable:")
no_year, no_author_paren, very_short, has_doi = 0, 0, 0, 0
for _, _, r in missing:
    c = r.get("citation", "")
    if not re.search(r"\b(19|20)\d\d\b", c):
        no_year += 1
    if not re.search(r"[A-Z][A-Za-z'\-]+,?\s", c):
        no_author_paren += 1
    if len(c) < 25:
        very_short += 1
    if "doi.org" in (r.get("url") or "") or "10." in c:
        has_doi += 1
print(f"    no 4-digit year in the string     : {no_year}")
print(f"    no 'Surname,' pattern             : {no_author_paren}")
print(f"    under 25 characters               : {very_short}")
print(f"    a DOI or '10.' already present    : {has_doi}")

# Book-length works: a publisher page or an ISBN is a locator a reader can open.
BOOKY = re.compile(r"\b(press|university|books?|publishing|unw|cornell|"
                   r"routledge|bloomsbury|harvard|chapel hill|palgrave|"
                   r"oxford|cambridge)\b", re.I)
bookish = [(i, r) for i, _, r in missing if BOOKY.search(r.get("citation", ""))]
print(f"\n  book-length / press-published strings: {len(bookish)}")

# Anything already carrying a locator_from is a twin this run attached; a
# missing record with locator_from would mean the attach tool wrote one field
# and not the other.
half = [(i, r) for i, _, r in missing if r.get("locator_from")]
print(f"  missing but carrying locator_from (should be 0): {len(half)}")
for i, r in half[:6]:
    print(f"    {i}: {r.get('citation', '')[:70]!r}")

print(f"\n  the 30 worst, verbatim, so they can be worked:")
seen = collections.Counter()
shown = 0
for eid, title, r in missing:
    if seen[eid] >= 2 or shown >= 30:
        continue
    seen[eid] += 1
    shown += 1
    print(f"  [{eid}] {r.get('citation', '')!r}")
    print(f"       status={r.get('status')} url={r.get('url')!r}")
