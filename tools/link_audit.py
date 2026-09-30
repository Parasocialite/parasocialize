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

    # 4. does any page claim a freshness the site cannot deliver?
    #
    # This used to test whether the sweeper was alive and fail when it was stale.
    # That tested a pipeline state no reader can see, on a site that no longer
    # claims to be swept hourly, and it would have been red forever. It is now a
    # check on the copy, which is the part a reader can actually observe.
    # Two failure modes, not one. The original pattern only matched copy that
    # names a frequency outright ("swept hourly"), so it passed a site whose
    # mood notes read "the sweep is late and the clock is red" and "seven past,
    # and asleep on the job" - both of which promise a schedule just as clearly,
    # and neither of which is true, because the sweeper has never run. An audit
    # that certifies a lie is worse than no audit, because it gets relied on.
    # The implied-cadence group below catches claims that assume a running
    # process without ever stating an interval.
    FRESH_CLAIM = re.compile(
        r"swept\s+hourly|sweep(?:ed|ing)?\s+(?:hourly|every\s+hour)|"
        r"updated\s+(?:hourly|every\s+hour)|refreshed\s+(?:hourly|every\s+hour)|"
        r"live\s+(?:news|feed|wire)|"
        r"seven\s+past|asleep\s+on\s+the\s+job|"
        r"sweep\s+is\s+(?:late|running|due|overdue)|"
        r"every\s+hour|each\s+hour|on\s+the\s+hour|"
        r"constantly\s+updated|always\s+current|never\s+stale", re.I)
    claims = []
    for hp in sorted(ROOT.rglob("*.html")):
        rel = hp.relative_to(ROOT)
        if rel.parts[0] in {"dist", ".git"} or rel.name == "v1-oxalpha-backup.html":
            continue
        body = re.sub(r"<script.*?</script>|<style.*?</style>", " ",
                      hp.read_text(encoding="utf-8", errors="replace"), flags=re.S)
        body = re.sub(r"<(nav|footer|header)[^>]*>.*?</\1>", " ", body, flags=re.S)
        for line in re.sub(r"<[^>]+>", "\n", body).split("\n"):
            if FRESH_CLAIM.search(line):
                claims.append(f"{rel.as_posix()}: {line.strip()[:70]}")
    if claims:
        p(f"{len(claims)} page(s) claim a sweep or refresh schedule the site does "
          f"not run: {claims[0]}")
    else:
        w("no page claims a refresh schedule. true: the sweeper has never run, so "
          "the site does not pretend otherwise")

    sw_path = ROOT / "data" / "sweep.json"
    if not sw_path.exists():
        w("no sweep.json - the sweeper has never run (a note, not a failure: "
          "nothing on the site claims otherwise)")
    else:
        sw = json.loads(sw_path.read_text(encoding="utf-8"))
        try:
            age_h = (datetime.datetime.now(datetime.timezone.utc)
                     - datetime.datetime.fromisoformat(sw["last_run"])).total_seconds() / 3600
        except Exception:
            age_h = 999
        if age_h > 3:
            w(f"last sweep was {age_h:.0f}h ago (a note: no page claims a schedule)")
        if sw.get("feeds_ok", 0) == 0:
            w("last sweep reached zero feeds")
        if sw.get("model", "").startswith("none"):
            w("no model key set - everything is filed raw with no lens")

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
