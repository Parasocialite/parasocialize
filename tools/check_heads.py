"""Does every deployed page offer the feeds and the favicon in its head?

Eleven pages shipped without the block. `unify_heads.py` gave every longhand
head in `tools/build_cards.py` the same three links, but it only ever knew that
one file: `build_atlas.py` and `build_quiz.py` are separate generators, the
404 comes from `build_cards.build_404()`'s own template, and
`membership/`, `tip/`, `signal/latest.html`, `audit/`, `classroom/` and the
three `cases/*.html` have no generator at all - they are hand-written files
that nothing rebuilds, which is exactly why nothing noticed. `signal/latest.html`
had no `<head>` whatsoever; it is replaced by hand every Friday, so a future
replacement can silently drop the block again.

So this reads the deployed tree, which is what a reader actually gets - the
same reason `check_internal_leaks.py` and `md_leak.py` read `dist/` - and it
refuses to report on a tree too small to be the site, because a measurement
that cannot see its own subject will pass any test you give it.

It counts `<link>` ELEMENTS, not substrings, for a reason this check met the
hard way: the shared `HEAD` constant carries an HTML comment explaining the
two feeds, and that comment contains the words "radar.xml" and
"ledger/feed.xml". A substring test is satisfied by the explanation - a
comment is not an offer - so the check parses actual link tags and requires
exactly one of each. Exactly one, not at least one: `exceptions/index.html`
shipped with the radar and favicon links twice, once from the block
`unify_heads.py` inserted and once from a pair the page already had, and a
duplicated autodiscovery link is a feed every reader's reader lists twice.
The duplicate scan that first "found" it on 323 pages was itself wrong the
other way - it counted substrings, so every page whose head carried the
comment false-positived. Count the element, not the word.

What it cannot do: it checks that the three elements are present exactly
once, not that their titles or hrefs are uniform across pages. Variants
exist on purpose (the em dash in the shared `HEAD` constant against the hyphen
in `unify_heads.BLOCK`), and a gate that rejected them would be restyling
rather than checking.

It also asks whether each page is styled at all, element-parsed for the same
reason. /ledger/ shipped unstyled: a missing `>` after its description meta
left the tag open and it ate the stylesheet link that followed. The link was
still there as text inside an attribute, so every substring test - including
this file's own href scan - read it as present, while browsers had no
stylesheet at all. Two rules catch that class: a parser sweep for an element
carrying attributes named like tags (the fingerprint of an unclosed tag that
swallowed its neighbour), and a requirement that a page either carries a real
stylesheet link or styles itself inline. signal/latest.html is the one page
allowed to declare no stylesheet - it is an HTML email, styled entirely with
style attributes by necessity - and it is named here rather than detected,
so a second page joining it is a decision, not an accident.
"""
import pathlib
import re
import sys
from html.parser import HTMLParser

ROOT = pathlib.Path(__file__).resolve().parent.parent
DIST = ROOT / "dist"
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

LINK = re.compile(r"<link[^>]+href=\"([^\"]*)\"", re.I)

NEEDLES = {
    "radar.xml": "radar.xml",
    "ledger/feed.xml": "ledger/feed.xml",
    "favicon.svg": "favicon.svg",
}

INLINE_ONLY = {"signal/latest.html"}


class Styled(HTMLParser):
    """Element counts, not substrings.

    `links` counts real <link rel=stylesheet> elements and `style` counts
    <style> elements - and counts them on startEND tags too, because
    `<link ... />` is a startendtag and a scan that misses half the spellings
    will some day read zero on a styled page. `swallowed` records an element
    whose attributes include a name that is not an attribute but a tag
    ("link", "meta"): that is the fingerprint of an unclosed tag, which stays
    in "before attribute name" state and eats whatever follows.
    """
    TAGLIKE = {"link", "meta"}

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.links = 0
        self.style = 0
        self.swallowed = []

    def _count(self, tag, attrs):
        names = dict(attrs)
        eaten = sorted(k for k in names if k in self.TAGLIKE)
        if eaten:
            self.swallowed.append((tag, eaten))
        if tag == "link" and "stylesheet" in (names.get("rel") or "").lower():
            self.links += 1
        elif tag == "style":
            self.style += 1

    def handle_starttag(self, tag, attrs):
        self._count(tag, attrs)

    def handle_startendtag(self, tag, attrs):
        self._count(tag, attrs)

if not DIST.is_dir():
    print(f"REFUSING: {DIST} does not exist. Run build_deploy.py first.")
    sys.exit(1)

files = sorted(DIST.rglob("*.html"))
if len(files) < 100:
    print(f"REFUSING: found {len(files)} html files under {DIST}; "
          "that is not the site, and a report on it would mean nothing.")
    sys.exit(1)

missing = []
for p in files:
    rel = p.relative_to(DIST).as_posix()
    text = p.read_text(encoding="utf-8", errors="replace")
    head, sep, _ = text.partition("</head>")
    if not sep:
        missing.append((rel, ["no </head> at all"]))
        continue
    hrefs = [m.group(1).lower() for m in LINK.finditer(head)]
    faults = []
    for name, needle in NEEDLES.items():
        count = sum(1 for h in hrefs if needle in h)
        if count == 0:
            faults.append(f"MISSING {name}")
        elif count > 1:
            faults.append(f"DUPLICATE {name} x{count}")
    probe = Styled()
    probe.feed(text)
    for tag, eaten in probe.swallowed[:1]:
        faults.append(
            f"<{tag}> carries attribute(s) named {', '.join(eaten)} - a tag "
            "before it is unclosed and swallowed what followed")
    if probe.links == 0 and probe.style == 0 and rel not in INLINE_ONLY:
        faults.append("NO STYLESHEET: no <link rel=stylesheet> element and "
                      "no <style>; this page would render unstyled")
    if faults:
        missing.append((rel, faults))

print(f"{len(files)} deployed pages checked for radar.xml, "
      f"ledger/feed.xml and favicon.svg links, and a stylesheet, in the head")
if missing:
    for rel, faults in missing:
        print(f"  {rel:48} {'; '.join(faults)}")
    print(f"\nFAIL: {len(missing)} page(s) do not offer the feeds or the icon "
          "exactly once, or would render unstyled.")
    sys.exit(1)
print("clean: every deployed page offers both feeds and the SVG favicon, "
      "each exactly once.")
