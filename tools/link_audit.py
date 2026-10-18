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
            # A query string is not part of the filename. `../encyclopedia/
            # index.html?m=film#db` is one existing page with a filter its own
            # script applies, and resolving the whole string as a path reported
            # the atlas's fifteen medium links as 404s on pages that exist.
            base = base.partition("?")[0]
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
                continue
            # 3a. the fragment, if there is one, has to exist in the target.
            #
            # `base, _, frag = href.partition("#")` used to end right there, so
            # the fragment was computed and thrown away. A cross-page fragment is
            # therefore checked exactly as well as nothing at all: the file
            # resolves, the gate is green, and the reader lands at the top of a
            # page instead of the thing they were sent to.
            #
            # It shipped 46 dead anchors on 46 story pages at once. Every story
            # page linked "LAW n - <title>" at index.html#law-n; the id="law-n"
            # anchors are emitted by build_history() into /history/, and the
            # homepage has never had a #laws element or a #law-n one. It passed
            # because the template that EMITS id="law-n" is right there in the
            # same file as the template that LINKS to it, and reading the emitter
            # is not the same as asking which page it writes into.
            #
            # "A link that looks right is not a link that goes somewhere" - and
            # the check that would have caught it costs one dict lookup.
            #
            # Excluded: fragments the target's own script handles. /atlas/ reads
            # `location.hash` and dispatches on `#n=<id>` to paint a panel - a
            # real navigation with no element to land on. 193 of these were
            # reported as 404 by the first version of this check, which is the
            # same error in the opposite direction: a gate that cannot tell a
            # missing anchor from a routed one is a gate that cries wolf, and a
            # crying wolf gets disabled. So it asks the page whether it routes.
            if frag and target.suffix.lower() == ".html":
                try:
                    dest = target.read_text(encoding="utf-8", errors="replace")
                except OSError:
                    continue
                if f'id="{frag}"' in dest or f"id='{frag}'" in dest:
                    continue
                scripts = "\n".join(re.findall(r"<script\b[^>]*>(.*?)</script>",
                                               dest, re.S | re.I))
                if ("location.hash" in scripts or "window.location.hash" in scripts
                        or "hashchange" in scripts) and (
                        "hash" in scripts and frag.split("=")[0] in scripts
                        or frag.split("=")[0] == ""):
                    continue
                p(f"{html_file.relative_to(ROOT)} -> {href}  (404: no element "
                  f"with id=\"{frag}\" in {target.name}, and that page does not "
                  f"route on its hash)")

    # 3b. runtime fetches resolve too
    #
    # The check above strips <script> and only looks at href/src in markup, so a
    # page that fetch()es its data was invisible to it. /desk/ did exactly that:
    # it asked for ../data/queue.json and ../data/sweep.json, `data/` is in
    # build_deploy.EXCLUDE_NAMES and is never deployed, so both requests 404'd,
    # each had a .catch() that quietly produced an empty result, and the page
    # rendered as an empty room - dashes for every stat, no queue. It was linked
    # as CLERK'S DESK in the footer of every generated page. Nothing failed,
    # because a page whose data never arrives is still a page.
    #
    # So: check what the scripts ask for, against what is actually deployed.
    # INCLUDE_DIRS mirrors build_deploy, so this fails on the same rule the
    # deploy uses rather than on a second, more forgiving copy of it.
    INCLUDE_DIRS = {"img", "js", "css", "encyclopedia", "radar", "section",
                    "sections", "taxonomy", "top8", "history", "figures",
                    "moments", "brand", "atlas", "quiz", "citations",
                    "credits", "shelf", "membership", "desk", "timeline", "tip",
                    "cases", "radar", "audit", "classroom", "desk"}
    fetched = 0
    for html_file in ROOT.rglob("*.html"):
        if any(part in (".git", "node_modules", "dist") for part in html_file.parts):
            continue
        text = html_file.read_text(encoding="utf-8", errors="replace")
        scripts = "\n".join(re.findall(r"<script\b[^>]*>(.*?)</script>", text,
                                      re.S | re.I))
        for m in re.finditer(r"""fetch\(\s*["'`]([^"'`]+)["'`]""", scripts):
            url = m.group(1)
            if url.startswith(("http://", "https://", "//")):
                continue
            fetched += 1
            base, _, _frag = url.partition("#")
            if not base:
                continue
            target = (html_file.parent / urllib.parse.unquote(base)).resolve()
            # the question is not "does this exist in the repo" but "will it be
            # served" - and data/, tools/ and episode/ are deliberately not
            if not target.exists():
                p(f"{html_file.relative_to(ROOT)} fetches {url} which does not "
                  f"exist")
            elif target.is_relative_to(ROOT / "data") and "dist" not in \
                    target.relative_to(ROOT).parts:
                p(f"{html_file.relative_to(ROOT)} fetches {url} from data/, which "
                  f"is excluded from the deploy - the request will 404 in "
                  f"production and any .catch() will hide it")
    if fetched == 0:
        w("no page fetches anything at runtime - all data is baked in at build "
          "time, which is the only shape that cannot silently arrive empty")

    # 4. does any page claim a freshness the site cannot deliver?
    #
    # This used to test whether the sweeper was alive and fail when it was stale.
    # That tested a pipeline state no reader can see, on a site that no longer
    # claims to be swept hourly, and it would have been red forever. It is now a
    # check on the copy, which is the part a reader can actually observe.
    # Two failure modes, not one. The original pattern only matched copy that
    # names a frequency outright ("swept hourly"), so it passed a site whose
    # mood notes read "the sweep is late and the clock is red" and "seven past,
    # and asleep on the job" - both of which promise a schedule just as clearly.
    # The implied-cadence group below catches claims that assume a running
    # process without ever stating an interval.
    #
    # What this check must NOT do is assert a fact about the sweeper. It used to
    # print "the sweeper has never run" in the clean case - and the sweep.json
    # check twenty lines below reads that same file and reported an age, so one
    # run printed both "has never run" and "last run 70h ago". A hardcoded belief
    # about the pipeline is wrong the moment the pipeline changes, and a gate
    # that states a falsehood is worse than no gate, because it gets relied on.
    # Say what was observed; let the reader of the output judge it.
    FRESH_CLAIM = re.compile(
        r"swept\s+hourly|sweep\w*\s+(?:hourly|every\s+(?:an\s+)?hour)|"
        r"updated\s+(?:hourly|every\s+hour)|refreshed\s+(?:hourly|every\s+hour)|"
        r"live\s+(?:news|feed|wire)|"
        # \b matters here: "seven past" must not match "seven pastors",
        # which is what it did until a citation describing seven clergy on
        # social media tripped it.
        #
        # The interval has to be paired with a process verb. A bare "every
        # hour" or "each hour" is ordinary English and fired on prose like
        # "each hour of the climb was harder"; what actually signals a
        # promise the site cannot keep is a *process* claiming that rate.
        r"seven\s+past\b|asleep\s+on\s+the\s+job|"
        r"sweep\s+is\s+(?:late|running|due|overdue)|"
        r"(?:runs?|reads?|scans?|checks?|polls?|files|filing|"
        r"updat\w+|refresh\w+)\s+(?:hourly|every\s+(?:an\s+)?hour)\b|"
        # ...and the same verb may be separated from the interval by a stated
        # quantity. Without this the check missed the site's own paid page,
        # which sells "a machine that reads a hundred sources an hour": the
        # verb and "an hour" are not adjacent, so the pattern above sailed
        # straight past the one sentence that most needed catching.
        #
        # Requiring a number-like token in the gap is what keeps this from
        # becoming another "seven pastors": "she reads to the child an hour
        # every evening" has a verb and an interval and is not a promise
        # about the site. Measured across all 534 published pages, this adds
        # exactly one flagged line - the membership claim - and no false
        # positives.
        r"(?:runs?|reads?|scans?|checks?|polls?|files|filing|updat\w+|"
        r"refresh\w+|pulls?|fetches?|collects?)\s+"
        r"(?:\d[\d,.]*|a\s+hundred|hundreds?|thousands?|scores?|millions?|"
        r"dozens?|two|three|four|five|six|seven|eight|nine|ten|couple|"
        r"hundred|thousand|dozen|score|\w+\s+sources?|\w+\s+feeds?|"
        r"\w+\s+items?|\w+\s+pages?|\w+\s+links?)\s+"
        r"(?:[\w-]+\s+){0,2}?an\s+hour\b|"
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
        w("no page claims a refresh schedule, so nothing published promises a "
          "cadence. The pipeline's own state is reported separately below and "
          "is not assumed here")

    sw_path = ROOT / "data" / "sweep.json"
    if not sw_path.exists():
        w("no data/sweep.json - no sweep has ever been recorded")
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

    # 6. does a published video state its own length?
    #
    # The Watch block used to call every episode "the fifty-second version".
    # The three that exist run 42.0s, 53.7s and 63.4s, so it was wrong for all
    # of them and nothing noticed, because the block only renders once a URL is
    # pasted into an entry and none had one. A published video that cannot say
    # how long it is is the same shape of problem: a label that is not tied to
    # the thing it describes.
    _enc = json.loads((ROOT / "data" / "encyclopedia.json").read_text(encoding="utf-8"))
    vids = [e for e in _enc["entries"] if (e.get("video") or "").strip()]
    nostated = [e["id"] for e in vids if not e.get("video_seconds")]
    for eid in nostated:
        p(f"{eid}: a published video with no video_seconds - the Watch block "
          "cannot say how long it is. Run tools\\set_video_seconds.py --apply")
    # and the reverse: a duration recorded against a video that does not exist
    orphan = [e["id"] for e in _enc["entries"]
              if e.get("video_seconds") and not (e.get("video") or "").strip()]
    if orphan:
        w(f"{len(orphan)} entries record a video_seconds but have no video url "
          f"({', '.join(orphan[:4])}) - the cut exists, it is just not published")

    # 7. queue growing unchecked?
    q_path = ROOT / "data" / "queue.json"
    if q_path.exists():
        q = json.loads(q_path.read_text(encoding="utf-8"))
        if len(q) > 40:
            w(f"{len(q)} drafts waiting for signoff. "
              f"set PARASOCIALIZE_BUDGET=0 or clear some.")

    # 6. does any source record mean what its status says?
    #
    # A record marked `retrievable` promises a reader can open it; one with no
    # URL cannot be opened. build_cards.is_checked() reads only `status`, so
    # these render as standing behind their entry - the gap is in the CREDITS
    # rather than the backlog, which is the one place this project's central
    # claim would do real damage. Run here rather than separately because this
    # is the gate AGENTS.md says to read before every commit, and a check
    # nobody runs is not a check.
    #
    # Fails only on a regression, not on the standing count - 94 records are
    # already in this state and failing the build until someone sourced 94
    # works is a laundry list, not a gate. See tools/citation_audit.py.
    import citation_audit
    res = citation_audit.audit(citation_audit.load())
    base_path = citation_audit.BASELINE
    base = 0
    if base_path.exists():
        base = json.loads(base_path.read_text(encoding="utf-8")).get(
            "max_unopenable_claiming_open", 0)
    got = res["unopenable_claiming_open"]
    if got > base:
        p(f"{got} source records claim retrievable/verified with no url, "
          f"baseline allows {base}. A citation was added or promoted without "
          f"somewhere to open it. See tools/citation_audit.py --list")
    else:
        w(f"{got} source records claim retrievable/verified with no url "
          f"(baseline {base}, can only fall). 'sourced' counts an entry with "
          f"at least one record; it does not mean every record is locatable")

    # Every entry has a title plate, and the plate is DRAWN FROM THE DATA - lane,
    # category colour, kind, and whether the entry is citation-checked. It is
    # therefore a rendered claim about the entry, generated into a committed
    # artefact. Nothing regenerated it, because `plate.py --check` was not a
    # gate, and 25 plates had drifted: kobe's data says lane `grief` while its
    # committed plate said APPLICATION. Same class as the desk that fetched
    # nothing - a generated page that quietly stopped describing its source.
    # Cheap to check: rebuild each plate in memory and compare.
    try:
        import plate
        stale = []
        for ent in _enc["entries"]:
            pth = plate.OUT / f"{ent['id']}.svg"
            try:
                want = plate.build(ent, _enc)
            except Exception:
                continue
            if not pth.exists():
                stale.append(f"{ent['id']} (missing)")
            elif pth.read_text(encoding="utf-8") != want:
                stale.append(ent["id"])
        if stale:
            p(f"{len(stale)} title plates no longer match their entry "
              f"(first: {', '.join(stale[:6])}). Run: python tools\\plate.py")
        else:
            w("every title plate matches its entry (regenerate with "
              "tools\\plate.py)")
    except Exception as exc:
        w(f"could not check title plates ({exc.__class__.__name__})")

    # ---- pages nothing links to -------------------------------------------
    # A page with no inbound internal link cannot be navigated to. Measured
    # across the deployed tree this found FIVE: 404.html (correct - a 404
    # handler should have no inbound link), three Case Files, and /classroom/.
    # All four of the rest were **indexable** - no robots meta - and absent
    # from sitemap.xml, so a crawler could index a page it had no way to reach.
    # That is a page existing and not being offered, which is a decision being
    # made by omission rather than a technical fault, and nothing else in this
    # audit could see it: every other check here asks whether a LINK WORKS,
    # never whether a page is REACHABLE.
    #
    # NOTE THE TWO TREES. Every other check in this file reads the SOURCE tree;
    # this one reads dist/. That is deliberate - "reachability" is a property of
    # what is deployed - but it means the two disagree by exactly one build, and
    # it is why the first version of this check's red test passed: it removed
    # the link from membership/index.html in the source while this block was
    # reading dist/, so it saw nothing wrong. **A gate that reads a different
    # file from the thing you edited is not testing your edit.**
    # The scan is over dist/ ONLY. The first version walked the whole repo and
    # reported 275 orphans, because it counted every page twice - once in the
    # source tree and once in dist/ - and swept up Chrome's scratch calibration
    # files under episode/.chrome/. **"Reachability" is a property of what is
    # deployed**, and a source page and its built twin are the same page.
    _DIST = ROOT / "dist"
    _inbound = {}
    if _DIST.exists():
        for _p in _DIST.rglob("*.html"):
            _raw = _p.read_text(encoding="utf-8", errors="replace")
            for _m in re.finditer(r'<a\b[^>]*\bhref="([^"]+)"', _raw, re.I):
                _t = _m.group(1).split("#")[0].strip()
                if not _t or _t.startswith(("http", "mailto:", "tel:", "javascript:")):
                    continue
                if _t.startswith("/"):
                    _t = _t.lstrip("/")
                else:
                    _base = _p.parent.relative_to(_DIST).as_posix()
                    if _base != ".":
                        _t = urllib.parse.urljoin(_base + "/", _t)
                    # A page at the ROOT resolves relative to the root, and
                    # `urljoin("/", "figures/index.html")` returns
                    # "/figures/index.html" - an absolute path that matches no
                    # key in the inbound table. That made every page linked only
                    # from the front page look orphaned, which is how `figures/`
                    # and `tip/` turned up as failures on correct data.
                    # **A resolver that is wrong for the most common case in the
                    # tree is a resolver, not a measurement.**
                _t = urllib.parse.unquote(_t)
                if _t.endswith(".html"):
                    _inbound[_t] = _inbound.get(_t, 0) + 1
        _orphans = []
        for _p in sorted(_DIST.rglob("*.html")):
            _rel = _p.relative_to(_DIST).as_posix()
            if _rel == "404.html" or _inbound.get(_rel):
                continue
            _raw = _p.read_text(encoding="utf-8", errors="replace")
            if re.search(r'<meta name="robots" content="[^"]*noindex', _raw, re.I):
                continue      # deliberately unpublished, which is a decision
            _orphans.append(_rel)
    else:
        _orphans = []
    if _orphans:
        p(f"{len(_orphans)} page(s) have no inbound internal link and are "
          f"indexable, so nothing can reach them: {', '.join(_orphans[:8])}"
          f"{' ...' if len(_orphans) > 8 else ''}. Link them from the page "
          f"they belong to, or mark them noindex if they are not ready.")
    else:
        w("every indexable page has at least one inbound internal link")

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
