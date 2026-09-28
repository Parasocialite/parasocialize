#!/usr/bin/env python3
"""
link_audit.py — catches the class of bug that killed the last version of this
site: a page that links fine, says nothing, and quietly goes stale.

Checks:
  1. every internal href resolves to a file that exists
  2. every card in data/shop.json has a rendered page
  3. the RSS links to each card, not to the homepage
  4. the last sweep is not stale
  5. nothing is advertising an offer that does not exist

Prints findings. Exit 1 on anything that would mislead a reader.
"""
import json, re, sys, datetime, pathlib, urllib.parse

ROOT = pathlib.Path(__file__).resolve().parent.parent
problems, warnings = [], []


def p(msg):
    problems.append(msg)


def w(msg):
    warnings.append(msg)


def main():
    shop = json.loads((ROOT / "data" / "shop.json").read_text(encoding="utf-8"))
    cards = shop.get("cards", [])
    slugs = {c["slug"] for c in cards}

    # 1. card pages exist
    for c in cards:
        p_ = ROOT / "radar" / f"{c['slug']}.html"
        if not p_.exists():
            p(f"card '{c['slug']}' has no page at radar/{c['slug']}.html")

    # 2. the feed points at cards, not at the homepage. this was the original
    #    sin: eight items all linking to /#radar
    rss_path = ROOT / "radar.xml"
    if not rss_path.exists():
        p("radar.xml is missing")
    else:
        rss = rss_path.read_text(encoding="utf-8")
        items = re.findall(r"<item>(.*?)</item>", rss, re.S)
        if not items:
            p("radar.xml has no items")
        for it in items:
            link = re.search(r"<link>(.*?)</link>", it, re.S)
            if not link:
                p("an rss item has no <link>")
                continue
            if "/#radar" in link.group(1) or link.group(1).rstrip("/").endswith("com"):
                p(f"rss item links to the homepage, not a card: {link.group(1)}")
        for c in cards:
            if f"/radar/{c['slug']}.html" not in rss:
                p(f"card '{c['slug']}' is not in the feed")
        if len(items) != len(cards):
            w(f"feed has {len(items)} items, shelf has {len(cards)} cards")

    # 3. internal links resolve
    checked = 0
    for html_file in ROOT.rglob("*.html"):
        if any(part in (".git", "node_modules") for part in html_file.parts):
            continue
        text = html_file.read_text(encoding="utf-8", errors="replace")
        # inline scripts build hrefs as strings; scanning them finds nonsense
        # like href="'+esc(d.url)+'" and calls it a 404.
        text = re.sub(r"<script\b[^>]*>.*?</script>", "", text, flags=re.S | re.I)
        for href in re.findall(r'(?:href|src)="([^"]+)"', text):
            if href.startswith(("http://", "https://", "mailto:", "#", "data:", "//")):
                continue
            checked += 1
            base, _, frag = href.partition("#")
            if not base:
                continue
            target = (html_file.parent / urllib.parse.unquote(base)).resolve()
            try:
                target.relative_to(ROOT.resolve())
            except ValueError:
                w(f"{html_file.name}: link escapes the site: {href}")
                continue
            if not target.exists():
                p(f"{html_file.relative_to(ROOT)} -> {href}  (404)")

    # 4. is the sweeper alive?
    sw_path = ROOT / "data" / "sweep.json"
    if not sw_path.exists():
        w("no sweep.json yet - the sweeper has never run")
    else:
        sw = json.loads(sw_path.read_text(encoding="utf-8"))
        try:
            age_h = (datetime.datetime.now(datetime.timezone.utc)
                     - datetime.datetime.fromisoformat(sw["last_run"])).total_seconds() / 3600
        except Exception:
            age_h = 999
        if age_h > 3:
            p(f"last sweep was {age_h:.0f}h ago. the site is advertising freshness "
              f"it does not have.")
        if sw.get("feeds_ok", 0) == 0:
            p("last sweep reached zero feeds")
        if sw.get("model", "").startswith("none"):
            w("no model key set - everything is being filed raw with no lens")

    # 5. queue growing unchecked?
    q_path = ROOT / "data" / "queue.json"
    if q_path.exists():
        q = json.loads(q_path.read_text(encoding="utf-8"))
        if len(q) > 40:
            w(f"{len(q)} drafts waiting for signoff. "
              f"set PARASOCIALIZE_BUDGET=0 or clear some.")

    print(f"link audit: {checked} internal links across "
          f"{len(list(ROOT.rglob('*.html')))} pages")
    for m in warnings:
        print(f"  warn  {m}")
    for m in problems:
        print(f"  FAIL  {m}")
    print("  all good." if not problems else f"  {len(problems)} problem(s).")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
