"""Do the feeds actually parse?

`/ledger/feed.xml` shipped with `&mdash;` in its channel title. That is an HTML
entity; XML knows five entities and a numeric reference, and `&mdash;` is not
among them. Every reader would have shown a parse error and an empty feed, and
**no gate in this repository looked at it** - the same shape as the generated
pages that quietly stopped describing their data.

So this parses every `.xml` in `dist/` that claims to be a feed, and refuses to
report on an empty directory for the reason item 76 records: a measurement that
cannot see its own subject will pass any test you give it.

It also checks the two things a feed needs beyond validity: at least one item,
and a self link. A feed that is valid, empty and self-referential is a promise
with nothing behind it.
"""
import pathlib
import sys
import xml.etree.ElementTree as ET

ROOT = pathlib.Path(__file__).resolve().parent.parent
DIST = ROOT / "dist"
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

FEEDS = ["radar.xml", "ledger/feed.xml"]

if not DIST.is_dir():
    print(f"REFUSING: {DIST} does not exist. Run build_deploy.py first.")
    sys.exit(1)

bad = 0
for rel in FEEDS:
    p = DIST / rel
    if not p.exists():
        print(f"  MISSING  {rel} - the footer or a page links to it")
        bad += 1
        continue
    try:
        root = ET.fromstring(p.read_text(encoding="utf-8"))
    except ET.ParseError as e:
        print(f"  UNPARSEABLE  {rel}: {e}")
        bad += 1
        continue
    ch = root.find("channel")
    if ch is None:
        print(f"  NO CHANNEL  {rel}")
        bad += 1
        continue
    items = ch.findall("item")
    title = (ch.findtext("title") or "").strip()
    self_link = any(
        e.get("rel") == "self" for e in ch.iter() if e.get("rel"))
    ok = bool(items) and self_link
    if not ok and rel == "ledger/feed.xml" and not items:
        # A first build legitimately has one item; zero means the history file
        # and the feed disagree, which is a real fault.
        ok = False
    print(f"  {'ok ' if ok else 'BAD'}      {rel}: {len(items)} item(s), "
          f"self-link={self_link}")
    print(f"            title: {title}")
    if not ok:
        bad += 1

print()
if bad:
    print(f"FAIL: {bad} feed problem(s).")
    sys.exit(1)
print(f"clean: {len(FEEDS)} feed(s) parse, carry items, and self-link.")
