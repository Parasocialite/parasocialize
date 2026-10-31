#!/usr/bin/env python3
"""
build_cards.py - redraws the whole video store from data/shop.json.

  radar/<slug>.html      one page per story
  section/<section>/    a section front per section
  sections/index.html       every section, searchable
  shelf/index.html       the clerk's own work, multi-door
  index.html             the front page
  radar.xml / sitemap.xml / data/index.json

Run:  python tools/build_cards.py
"""
import json, html, datetime, pathlib, re, urllib.parse, hashlib
from collections import Counter

ROOT = pathlib.Path(__file__).resolve().parent.parent
ENC_BY_ID = {}
SHOP = ROOT / "data" / "shop.json"
SITE = "https://www.parasocialize.com"

HEAD = """<link rel="canonical" href="{site}{path}">
<meta property="og:type" content="{otype}">
<meta property="og:title" content="{title}">
<meta property="og:description" content="{desc}">
<meta property="og:image" content="{site}/img/podcasts/parasocialize.jpg">
<link rel="alternate" type="application/rss+xml" title="Parasocialize" href="{site}/radar.xml">
<!-- Two feeds, deliberately. radar.xml is content; ledger/feed.xml is the
     archive's own figures changing. They serve different subscribers and a
     reader who wants both should be offered both rather than made to pick in a
     feed reader's settings. Titles differ so the two are distinguishable in a
     subscription list, which is the only place anybody will see them. -->
<link rel="alternate" type="application/rss+xml" title="Parasocialize — the open ledger" href="{site}/ledger/feed.xml">
<link rel="icon" type="image/svg+xml" href="{site}/favicon.svg">
<link rel="icon" type="image/x-icon" sizes="48x48" href="{site}/favicon.ico">
<link rel="icon" type="image/png" sizes="192x192" href="{site}/icon-192.png">
<link rel="icon" type="image/png" sizes="512x512" href="{site}/icon-512.png">
<link rel="apple-touch-icon" sizes="180x180" href="{site}/apple-touch-icon.png">
<link rel="manifest" href="{site}/site.webmanifest">
<meta name="theme-color" content="#0b0b0d">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Fraunces:ital,opsz,wght@0,9..144,600;0,9..144,700;0,9..144,900;1,9..144,600;1,9..144,700&family=IBM+Plex+Mono:wght@400;500&display=swap" rel="stylesheet">
<link rel="stylesheet" href="{root}css/styles.css">
<link rel="stylesheet" href="{root}css/mascot.css">"""

# THE NAV IS GROUPED BY PURPOSE, BECAUSE THE HOMEPAGE NOW SAYS SO.
#
# The masthead offers two doors - "to read" and "to look something up" - and then
# offered a flat row of ten unlabelled links, which undid the point on the first
# click. A reader who has just been told the site has two modes should not have
# to guess which link belongs to which.
#
# "Home" is gone as a separate item: the wordmark is the home link, it is larger
# and it is already in the position the eye goes to first. Carrying both is how
# a bar ends up with eleven things in it.
#
# The story count is deliberately NOT interpolated here, even though every caller
# passes a `total`. It reads "All {total} stories", and build_atlas.py passes
# len(enc["entries"]) - so the atlas shipped "All 193 stories" pointing at
# /sections/, which has 47. A shared template that interpolates a value has to
# have every caller mean the same thing by it, and "total" means cards on most
# call sites and encyclopedia entries on that one. The number belongs on the
# homepage, where it is read from the cards it counts. Here it is just a label.
#
# The iYi logotype is gone from before the title. It was injected as {mk} into
# the wordmark anchor, and it made the site's own name read as "iYi
# PARASOCIALIZE" - two brands in the top-left corner, with the mascot outranking
# the publication it belongs to. iYi still has its own page, linked below as
# before. The {mk} argument is still passed by every caller and is now ignored;
# twenty call sites were not worth churning to remove a keyword argument that
# str.format discards.
# The nav is grouped, but the grouping was costing more than it was worth.
# Measured at 1600px: thirteen runs and twelve gaps needing 1031px, of which the
# three group labels were 178px plus 48px of gap. Three labels in a 64px bar is
# not grouping, it is a second and third heading competing with the first, and
# "Elsewhere" was the worst of the three - two letters of meaning for 80px.
# So: two labels, not three, and the shortest word that still says it. Every
# destination is still in the bar; none was dropped, because a link removed to
# make a header fit is a page nobody finds.
# CLERK'S DESK used to be a link in this nav, on every deployed page. The link
# was the defect rather than the page: /desk/ is a real back office - noindex,
# and it says so in its own footer - but advertising it in the navigation of
# every page put "60 IN THE QUEUE", "56 WITH NO LENS (no model key set)" and
# "No model key set. Filed raw. Needs a human to point it at..." in front of
# every reader, on a site whose whole argument is that it does not put its own
# machinery on display. The page is untouched and still builds at /desk/.
#
# This note lives here rather than in the template because an earlier attempt
# put it in the nav as an HTML comment, which shipped the explanation to all
# 310 pages - the same internal messaging on the public surface, just in the
# markup instead of the rendered text. A check for the link missed it as well,
# because it searched for "CLERK&#x27;S DESK" and the comment carried a raw
# apostrophe. A source comment is not a place to talk to readers, and a check
# that only matches the encoded form is not a check.
NAV = """<header class="topbar"><div class="topbar-in">
  <a class="wordmark" href="{root}index.html"><b>PARASOCIALIZE</b></a>
  <button class="menu-btn" aria-label="Menu" aria-expanded="false" aria-controls="nav"><span></span><span></span><span></span></button>
  <nav id="nav" class="nav" aria-label="Main">
    <span class="nav-lab">Read</span>
    <a href="{root}sections/index.html">Stories</a>
    <a href="{root}top8/index.html">Top 8</a>
    <a href="{root}history/index.html">History</a>
    <a href="{root}shelf/index.html">Works</a>
    <span class="nav-lab">Look up</span>
    <a href="{root}encyclopedia/index.html">Encyclopedia</a>
    <a href="{root}atlas/index.html">Atlas</a>
    <a href="{root}timeline/index.html">Timeline</a>
    <a href="{root}citations/index.html">Citations</a>
    <a href="{root}quiz/index.html">Quiz</a>
    <a class="nav-iyi" href="{root}brand/index.html">iYi</a>
    <a href="{root}membership/index.html" class="cta-quiet">Membership</a>
    <a class="cta" href="https://ko-fi.com/parasocialing" target="_blank" rel="noopener nofollow" aria-label="Support the archive on Ko-fi">Support</a>
  </nav>
</div></header>"""

FOOT = """<footer class="footer"><div class="foot-grid">
  <div class="foot-brand">
    <p class="wordmark foot-mark"><img class="logo-img" src="{root}img/logo.svg" alt="" width="24" height="24">PARA<b>SOCIALIZE</b></p>
    <p class="foot-note">{sweep}<br>Kept by Enan Joe Heneghan - video store clerk, M.A., teacher in Australia.<br>
    Every card links to its sources. Every card is signed by a person.</p>
    <p class="foot-tag">{motto}</p>
  </div>
  <nav class="foot-nav" aria-label="Footer">
    <div class="foot-col">
      <p class="foot-head">Read</p>
      <a href="{root}index.html">Latest</a>
      <a href="{root}sections/index.html">Stories</a>
      <a href="{root}top8/index.html">Top 8</a>
      <a href="{root}history/index.html">History</a>
      <a href="{root}shelf/index.html">Works</a>
      <a href="{root}moments/index.html">Moments</a>
    </div>
    <div class="foot-col">
      <p class="foot-head">Look up</p>
      <a href="{root}encyclopedia/index.html">Encyclopedia</a>
      <a href="{root}atlas/index.html">Atlas</a>
      <a href="{root}timeline/index.html">Timeline</a>
      <a href="{root}taxonomy/index.html">Taxonomy</a>
      <a href="{root}citations/index.html">Citations</a>
      <a href="{root}quiz/index.html">Quiz</a>
    </div>
    <div class="foot-col">
      <p class="foot-head">The project</p>
      <a href="{root}credits/index.html">About</a>
      <a href="{root}tip/index.html">Contact</a>
      <a href="{root}top8/archive/index.html">Archive</a>
      <a href="{root}ledger/index.html">Ledger</a>
      <a href="{root}membership/index.html">Membership</a>
    </div>
    <div class="foot-col">
      <p class="foot-head">Follow</p>
      <a class="foot-support" href="https://ko-fi.com/parasocialing" target="_blank" rel="noopener nofollow">Support the archive</a>
      <a href="{root}signal/latest.html">The Signal</a>
      <a href="{root}radar.xml">RSS feed</a>
      <a href="{root}brand/index.html">iYi</a>
    </div>
  </nav>
</div></footer>
<script>
(function(){{
  var b=document.querySelector('.menu-btn'),n=document.getElementById('nav');
  if(b)b.addEventListener('click',function(){{
    var o=document.body.classList.toggle('nav-open');
    b.setAttribute('aria-expanded',String(o));
  }});
  var r=document.querySelectorAll('.reveal');
  if(r.length){{
    if(!('IntersectionObserver' in window)){{r.forEach(function(x){{x.classList.add('in')}})}}
    else{{var io=new IntersectionObserver(function(es){{es.forEach(function(en){{
      if(en.isIntersecting){{en.target.classList.add('in');io.unobserve(en.target)}}}})}});
      r.forEach(function(x){{io.observe(x)}})}}
  }}
  var y=document.getElementById('year');if(y)y.textContent=new Date().getFullYear();
}})();
</script>"""

MESSY = ("No replies. The connection stays one-sided either way. "
         "Nobody here is going to tell you to log off.")

# How to say an edge to a reader. The keys are the values in the `type` field of
# a relation, which is graph vocabulary, not English: "bond_with" is a Python
# identifier and it was being printed verbatim next to entry titles.
#
# Underscored types are joined with a space if they are missing here rather than
# left as-is, so a new edge type added to the data degrades to readable words
# instead of leaking a field name. That fallback is the reason this is a map and
# not a validation step: a new type should not be able to break the build.
RELWORD = {
    "cites": "cites",
    "depicts": "depicts",
    "contemporary": "of the same time as",
    "succeeded": "came after",
    "preceded": "came before",
    "member_of": "part of",
    "instance_of": "an example of",
    "wrote": "wrote",
    "bond_with": "a bond with",
    "occurred_in": "happened in",
    "related": "related to",
}


def esc(s):
    return html.escape(str(s if s is not None else ""), quote=True)


# --- inline emphasis and paragraph breaks -----------------------------------
# The corpus's prose fields are written in markdown and the renderer had no
# inline-formatting path at all, so the source reached the page as source:
# **709 literal `**` markers across 52 deployed pages**, and 33 entries ran as
# one unbroken wall because their `\n\n` collapsed to a space. Measured, not
# assumed:
#
#   significance   428 markers, 33 entries with blank-line breaks (96 total)
#   placement why   84 markers
#   summaries        0 - so no meta description or title attribute is affected,
#                     which is why `esc()` is NOT the place to fix this
#
# Two functions rather than one change to esc(): esc() is also used for
# `content="..."` and `title="..."`, and putting <strong> inside an attribute
# would be a new way for a field to promise something it does not keep. It stays
# a pure escape, and prose goes through these.
_EMPH = re.compile(r"\*\*(.+?)\*\*", re.S)
_ITAL = re.compile(r"(?<![\w*])\*([^*\n]{2,60})\*(?![\w*])")
_CODE = re.compile(r"`([^`\n]{1,60})`")


def emph(s):
    """Escape, then render the markdown the corpus is actually written in.

    Three constructs, in this order, and nothing else. Bold runs first so that
    `**A**` is never mistaken for two italics.

    - `**strong**` non-greedy, which is correct here: every marker pair in the
      corpus is balanced and the "nested" hits a naive regex flags are
      sequential spans - "**A.** middle. **B.**" - not spans inside spans.
    - `*emphasis*`, bounded to 60 chars and to a single line, with non-word
      neighbours. Measured over the corpus: 53 distinct spans, 80 uses, the
      great majority of them work titles (*Whiz Comics*, *The Scream*) and the
      rest genuine stress (*is*, *also*). **Zero** end in punctuation or exceed
      45 characters, so the pattern cannot eat a sentence.
    - `` `code` `` for the author's machine keys - `persona/idol`, `simulated`,
      `split_from` - 468 uses, 412 of them on /taxonomy/, none over 40 chars.

    Nothing else is attempted. Headings, links and list markers were measured
    at zero, and a converter that guesses is a converter that mangles prose.
    """
    t = esc(s)
    t = _EMPH.sub(r"<strong>\1</strong>", t)
    t = _ITAL.sub(r"<em>\1</em>", t)
    t = _CODE.sub(r"<code>\1</code>", t)
    return t


def prose(s, first_cls="lede2", heads=False):
    """Paragraphs from a field written with blank-line breaks.

    Only the FIRST paragraph carries `lede2`, because that class carries the
    drop cap (`.article .body p.lede2::first-letter`). Giving every paragraph
    the class would put a drop cap on each one. The plain <p> is already styled
    by `.article .body p`.

    `heads=True` promotes a paragraph's LEADING bold span to an `<h2>`, and
    returns the table of contents beside the html.

    It is a promotion, not an invention, and the measurements are what make it
    safe. Only **4 of the 227 entries are long enough to need a landmark at
    all** - the body is a median of 43 words and 171 entries are under 150 -
    and those 4 already open their paragraphs on the author's own bolded
    claim, 23 of them between them. So the structure being promoted is
    structure the author wrote; the script is only changing its rendering.

    The rules, and each is there because of a way this could go wrong:
      - the lead must be at the START of a paragraph, or a bold aside anywhere
        in the prose would become a heading;
      - it must be at most 90 characters, or a sentence becomes a heading -
        measured, 27 of the 96 leads are 91 characters or longer and they stay
        as bold, which is right;
      - it is never the first paragraph, which carries the drop cap and sits
        directly under the h1;
      - the paragraph must have text left after the lead, or an empty `<p>`
        would render.
    """
    parts = [p.strip() for p in str(s or "").split("\n\n") if p.strip()]
    if not parts:
        return "", []
    out, toc = [], []
    for i, p in enumerate(parts):
        # Match the lead on the RAW text, not on emph()'s output. Slugging the
        # escaped string put an HTML entity in the id - the tape's became
        # "the-tape-x27-s-own-contents" - because `&#x27;` slugifies to "x27".
        m = _LEAD.match(p) if heads else None
        if m and i > 0 and len(m.group(1)) <= 90:
            lead, rest = m.group(1), p[m.end():].strip()
            if rest:
                slug = _slug(lead)
                out.append(f'<h2 class="ent-h" id="{slug}">{emph(lead)}</h2>')
                out.append(f"<p>{emph(rest)}</p>")
                toc.append((slug, lead))
                continue
        cls = f' class="{first_cls}"' if i == 0 else ""
        out.append(f"<p{cls}>{emph(p)}</p>")
    return "".join(out), toc


_LEAD = re.compile(r"^\*\*(.+?)\*\*", re.S)


def _slug(text, limit=60):
    """A URL id from a heading, cut at a WORD boundary.

    A fixed-length slice produced "two-honesty-notes-because-the-entry-is-about-
    a-reading-rathe" - cut inside "rather", which is an id nobody can guess and
    a link nobody can read. Same lesson as the top-8 plate word: **a generated
    cut has to land where a person would have stopped.**
    """
    s = re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")
    if len(s) <= limit:
        return s or "s"
    cut = s.rfind("-", 0, limit + 1)
    return (s[:cut] if cut > 0 else s[:limit]) or "s"


def toc_html(toc):
    """A contents rail, only when there are enough headings to be worth one."""
    if len(toc) < 3:
        return ""
    items = "".join(f'<li><a href="#{slug}">{emph(label)}</a></li>'
                    for slug, label in toc)
    return (f'<nav class="ent-toc" aria-label="On this page">'
            f'<p class="ent-toc-h">On this page</p><ol>{items}</ol></nav>')


def root(depth):
    return "../" * depth


def rebuilt_tag(day) -> str:
    """The marker for a day that was computed after the fact.

    The three records are append-only evidence of what a page actually showed.
    tools/archive.py can close a gap only when the data feeding the rotation
    was frozen before the missed day, and when it does, the entry says so. A
    reader is entitled to tell an observed day from a recomputation of what
    would have happened, so every renderer prints this beside the date rather
    than letting a rebuilt entry look identical to a live one.
    """
    if not isinstance(day, dict) or not day.get("reconstructed"):
        return ""
    on = esc(str(day.get("reconstructed_on") or "an unrecorded date"))
    return (f' <span class="rec-rebuilt" title="No build ran on this day. '
            f'The rotation was recomputed on {on} from the same data and '
            f'recorded as rebuilt rather than observed.">rebuilt</span>')


def rebuilt_run_tag(run) -> str:
    """The same marker for a run that contains at least one rebuilt day."""
    if not run.get("recon"):
        return ""
    return (' <span class="rec-rebuilt" title="At least one day in this run '
            'was computed after the fact. The per-day record on '
            '/top8/record/ marks which.">includes rebuilt</span>')


def fmt_date(iso):
    if not iso:
        return "-"
    try:
        return datetime.date.fromisoformat(str(iso)[:10]).strftime("%d %b %Y").lstrip("0").upper()
    except Exception:
        return str(iso)


def rfc822(iso):
    try:
        return datetime.datetime.fromisoformat(str(iso)[:10]).strftime("%a, %d %b %Y 09:00:00 +0000")
    except Exception:
        return "Thu, 01 Jan 2026 09:00:00 +0000"


def rel_days(iso):
    if not iso:
        return ""
    try:
        n = (datetime.date.today() - datetime.date.fromisoformat(str(iso)[:10])).days
        return "today" if n <= 0 else f"{n}d ago"
    except Exception:
        return ""


# ------------------------------------------------------------------- posters
def poster_bg(c, sections):
    """inline gradient for a lead cover"""
    a = next((x for x in sections if x["id"] == c["section"]), {})
    col = a.get("colour", "#ffb454")
    h = sum(ord(ch) for ch in c["slug"])
    return (f"background:linear-gradient(155deg,{esc(col)} 0%,"
            f"color-mix(in srgb,{esc(col)} 30%,#1b1410) 55%,#120d0a 100%)")


def cover(c, sections, manifest=None, depth=1):
    """The picture on a card, or nothing at all.

    The order is deliberate: this story's own photograph, then its section's
    photograph, then no picture. Twenty-two of the forty-eight stories have no
    photograph of their own after review - Commons has no freely-licensed still
    of a Hungarian Twitch partner meeting, and the ones it did return for those
    stories were wrong, so they were withdrawn rather than shipped. Those cards
    fall back to the section photograph, which is a real photograph of the
    subject matter; where a section has no photograph either, the card is
    text-forward, with no art box.

    The third fallback used to be a generated lettered poster - the headline's
    first letter, a stripe, a slash of the headline. It was drawn from the slug
    and looked like nothing, and on a page about not pretending about pictures
    a lettered block reads as a missing image rather than a design. An entry
    with no source says so; a card with no free photograph now does the same.

    No credit on the card face, for the same reason the homepage tiles have none:
    it is a licence obligation, not decoration, and it lives on the article page
    and on /credits/ where there is room to be read.
    """
    f = img_for(manifest or {}, c.get("slug"), depth) or \
        img_aisle(manifest or {}, c.get("section"), depth)
    if not f:
        return ""
    return (f'<div class="poster shot">'
            f'<img src="{esc(f["path"])}" alt="" loading="lazy">'
            f'<span class="veil" style="background:'
            f'linear-gradient(to top,rgba(12,8,5,.86) 0%,rgba(12,8,5,.12) 46%,'
            f'rgba(12,8,5,0) 72%)"></span></div>')


def clip(text, n=150):
    """Truncate on a word boundary, with an ellipsis.

    `[:150]` was cutting mid-word in 74 places across dist/ — "that is prese",
    "produced to a gen", "lives. A rel". Every one read as a rendering fault
    rather than a deliberate teaser, because nothing signals that the text was
    cut rather than written that way. Cutting at the last space inside the
    budget and marking it costs four characters and removes the whole class.
    """
    s = " ".join(str(text or "").split())
    if len(s) <= n:
        return s
    cut = s[:n].rsplit(" ", 1)[0].rstrip(" ,;:-")
    return (cut or s[:n]) + "…"


def story(c, sections, laws, big=False, take=True, root_="", manifest=None, depth=1):
    a = next((x for x in sections if x["id"] == c["section"]), {})
    col = a.get("colour", "#ffb454")
    law = next((l for l in laws if l["n"] == c["law"]), {})
    src = (c.get("sources") or [{}])[0]
    tags = [f'<span class="tag tag-aisle">{esc(a.get("sign", c["section"].upper()))}</span>']
    # The kicker guard is here, not only in the article template, because these
    # cards render everywhere a story list appears - and 37 of 47 kickers are
    # empty, so an unguarded pill printed an empty chip across the whole site.
    if (c.get("kicker") or "").strip():
        tags.append(f'<span class="tag tag-kick">{esc(c["kicker"])}</span>')
    if c.get("state") == "OVERDUE":
        tags.append('<span class="tag tag-od">Do not return</span>')
    if law:
        tags.append(f'<span class="tag tag-law">LAW {c["law"]}</span>')
    tk = f'<p class="take">{esc(c["take"])}</p>' if take and c.get("take") else ""
    # A card with no photograph carries no cover at all - the anchor used to
    # render regardless, wrapping a lettered poster, and an empty link box is
    # worse than nothing. See cover() below for why the poster was dropped.
    art = cover(c, sections, manifest, depth)
    cov = (f'<a class="cover" href="{root_}radar/{esc(c["slug"])}.html" '
           f'tabindex="-1" aria-hidden="true">{art}</a>') if art else ""
    return (f'<article class="story{" story-lg" if big else ""}" style="--c:{esc(col)}">'
            f'{cov}'
            f'<div class="body"><div class="tags">{"".join(tags)}</div>'
            f'<h3><a href="{root_}radar/{esc(c["slug"])}.html">{esc(c["headline"])}</a></h3>'
            f'<p class="dek">{esc(c["one_line"])}</p>{tk}'
            f'<div class="foot"><span class="src">{esc(src.get("publisher", ""))}</span>'
            f'<a href="{root_}radar/{esc(c["slug"])}.html">Read →</a></div></div></article>')


# ------------------------------------------------------------------ article
def build_card(c, sections, laws, shelf, data, manifest=None):
    d = 1
    r = root(d)
    manifest = manifest or {"items": []}
    a = next((x for x in sections if x["id"] == c["section"]), {})
    law = next((l for l in laws if l["n"] == c["law"]), {})
    col = a.get("colour", "#ffb454")
    sh = next((x for x in shelf if x["id"] == c.get("shelf")), None)
    # id -> entry, for rendering the crosslinks. Loaded per card rather than at
    # module scope because the encyclopedia is read in four other places already
    # and one more global would mean a fifth read of a 460KB file on every import.
    global ENC_BY_ID
    if not ENC_BY_ID:
        _e = json.loads((ROOT / "data" / "encyclopedia.json").read_text(encoding="utf-8"))
        ENC_BY_ID = {x["id"]: x for x in _e["entries"]}

    rel = sorted([x for x in data["cards"] if x["slug"] != c["slug"]
                  and x["section"] == c["section"]], key=lambda x: -x.get("res", 0))[:4]
    # take=False: the related-story cards already print `one_line` as the dek
    # (median 99 chars). Passing the default through printed `take` underneath
    # it as well — median 393, longest 937 — so every card carried a second,
    # first-person paragraph that was never a teaser. That is the incoherent
    # text on the buttons: it read as a caption for the card and was an essay.
    rel_html = "".join(story(x, sections, laws, root_=r, manifest=manifest,
                             depth=d, take=False) for x in rel)

    src_rows = []
    for s in c.get("sources", []):
        # `via` names the host a reader will actually land on, when that is not
        # the organisation the credit names.
        #
        # The field existed on eight records, held the value "report" - which
        # means nothing to a reader - and was referenced by **no template at
        # all**. So a card could say "Phys.org · 23 SEP 2026", link to
        # www.msn.com, and a reader would click through to MSN having been told
        # they were reading Phys.org. MSN syndicates other outlets wholesale;
        # that is a real and legitimate route, but it is not the same as
        # reading the originating outlet, and the page should say which it is.
        # `via` was the field for exactly this and was doing nothing.
        via = str(s.get("via") or "").strip()
        show_via = via and via.lower() not in ("report", "", s.get("publisher", "").lower())
        credit = esc(s["publisher"])
        if show_via:
            credit += f', via {esc(via)}'
        if s.get("url"):
            src_rows.append(
                f'<div class="srcbox" style="padding:14px 0;border-bottom:1px solid var(--line2)">'
                f'<a href="{esc(s["url"])}" target="_blank" rel="noopener nofollow">{esc(s["title"])} ↗</a>'
                f'<p class="pub">{credit} · {fmt_date(s.get("at"))}</p></div>')
        else:
            src_rows.append(
                f'<div class="srcbox" style="padding:14px 0;border-bottom:1px solid var(--line2);opacity:.6">'
                f'<a>{esc(s["title"])}</a>'
                f'<p class="pub">{credit} · LINK NOT RESOLVED YET — TREAT WITH SUSPICION</p></div>')

    sh_html = ""
    # The way out. For the whole of this site's life a story page linked to
    # nothing but other stories: 47 of them here and 193 encyclopedia entries
    # that no story ever pointed at. The two halves were separate databases
    # joined by a nav link to an index, and the entries - which is where the
    # depth actually lives - were unreachable from the journalism.
    #
    # tools/crosslink.py computes the join from shared vocabulary weighted by
    # inverse document frequency within the aisle, so "fandom" and "audience"
    # cannot carry a match and two distinct words must overlap. The picks are
    # written into data/shop.json under `crosslinks`; this renders them.
    xl = ""
    xids = (data.get("crosslinks") or {}).get(c["slug"]) or []
    if xids:
        links = []
        for eid in xids:
            e = ENC_BY_ID.get(eid)
            if not e:
                continue
            links.append(
                f'<a class="xl" href="{r}encyclopedia/{esc(eid)}.html">'
                f'<b>{esc(e.get("title", eid))}</b>'
                f'<span>{esc(clip(e.get("summary"), 150))}</span></a>')
        if links:
            xl = (f'<p class="kicker" style="margin-top:40px">'
                  f'Where this sits in the encyclopedia</p>'
                  f'<div class="xlinks">{"".join(links)}</div>')
    if sh:
        img = (f'<img src="{sh["img"] if str(sh.get("img","")).startswith("http") else r + sh["img"]}" '
               f'alt="{esc(sh["title"])}" loading="lazy" style="width:84px;height:84px;object-fit:cover;'
               f'border-radius:8px;flex:none;box-shadow:0 8px 20px rgba(0,0,0,.5)">') if sh.get("img") else ""
        sh_html = (f'<p class="kicker" style="margin-top:40px">The clerk&apos;s shelf - how this got here first</p>'
                   f'<div class="note" style="display:flex;gap:18px;align-items:flex-start;'
                   f'font-family:var(--body);font-size:1rem;font-style:normal">'
                   f'{img}<div style="min-width:0"><p class="srcline" style="margin:0 0 4px">'
                   f'{esc(sh["kind"].upper())}</p>'
                   f'<b style="font-family:var(--serif);font-size:1.2rem;display:block;margin-bottom:5px">'
                   f'<a href="{esc(sh["href"])}" target="_blank" rel="noopener">{esc(sh["title"])} ↗</a></b>'
                   f'<span style="color:var(--dim)">{esc(sh["blurb"])}</span></div></div>')

    # ---- Filed under: one line, three real destinations ---------------------
    #
    # This row was three taxonomies in identical pills, and the one thing that
    # looked most like a link was the one that was broken:
    #
    #   <span>IDOL</span>                              a section page exists
    #   <span>The contrarian read</span>               not a category at all
    #   <a href="index.html#laws">LAW 1 · Binding…</a> no such anchor
    #
    # So the section was inert while its page sat unused, the law linked to a
    # fragment that does not exist, and 37 of 47 cards printed an empty kicker
    # pill. Three naming conventions in one row: a shouted sign, a sentence-case
    # editorial label, and a numbered principle, all styled as if they were the
    # same kind of thing.
    #
    # The rebuild separates the three by what they *are* rather than styling them
    # as one thing:
    #   FILED UNDER  -> the section, a real link, carrying its own blurb
    #   LAW          -> the principle, linked to its own card (#law-N exists)
    #   the kicker   -> dropped from this row. It is an editorial register note
    #                   ("The big one"), not a category, and it belongs beside the
    #                   headline where it can read as a note rather than a door.
    bits = []
    sec_href = f"{r}section/{esc(c['section'])}/index.html"
    blurb = a.get("blurb", "")
    bits.append(
        f'<a class="fu-filed" href="{sec_href}">'
        f'<span class="fu-k">Filed under</span>'
        f'<b>{esc(a.get("sign", c["section"].upper()))}</b>'
        f'<span class="fu-blurb">{esc(blurb)}</span></a>')
    if law:
        # /history/, not the homepage. The id="law-N" anchors are emitted by
        # build_history() into that page's .h-laws block; the homepage has no
        # #laws element and never has. Verified by reading dist/ for the ids
        # rather than by reading the template that emits them - the template
        # looks like it would justify pointing at index.html, which is how the
        # first version of this line shipped 46 dead anchors across 46 story
        # pages while every gate stayed green.
        bits.append(
            f'<a class="fu-law" href="{r}history/index.html#law-{esc(law["n"])}">'
            f'<span class="fu-k">Which law it tests</span>'
            f'<b>Law {esc(law["n"])} &middot; {esc(law["title"])}</b>'
            f'<span class="fu-blurb">{esc(law.get("one_line",""))}</span></a>')
    if c.get("state") == "OVERDUE":
        bits.append('<span class="fu-od">This one does not go back on the shelf</span>')
    filed = f'<nav class="fu" aria-label="Filed under">{chr(10).join(bits)}</nav>'

    due = ("No due date - kept deliberately" if c.get("state") == "OVERDUE"
           else (f"Due back {fmt_date(c['due'])}" if c.get("due") else "Kept on the shelf"))

    # The card face carries no credit, so this is where attribution for a story's
    # own photograph is discharged: same picture, at size, captioned with what is
    # actually in the frame, linked to wherever it came from. A story with no
    # photograph of its own borrows its section's, and says so by being marked.
    own = img_for(manifest, c.get("slug"), d)
    article_photo = ""
    if own:
        article_photo = fig(manifest, c.get("slug"), d, "article-photo")
    else:
        sec = f"aisle-{c.get('section')}"
        if img_for(manifest, sec, d):
            article_photo = fig(manifest, sec, d, "article-photo borrowed")
    if article_photo and not own:
        article_photo = article_photo.replace(
            "<figcaption>",
            "<figcaption><b>This is the section photograph, not a picture of this "
            "story.</b> ", 1)

    return f"""<!DOCTYPE html>
<html lang="en"><head><meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{esc(c['headline'])} - Parasocialize</title>
<meta name="description" content="{esc(c['one_line'])}">
{HEAD.format(site=SITE, path=f"/radar/{c['slug']}.html", otype="article",
             title=esc(c['headline']), desc=esc(c['one_line']), root=r)}
</head>
<body>
<a class="skip" href="#story">Skip to story</a>
<div class="grain" aria-hidden="true"></div>
{NAV.format(root=r, total=len(data["cards"]), mk=wordmark("nav"))}
<main class="article" id="story">
{filed}
{('<p class="regnote">' + esc(c["kicker"]) + '</p>') if c.get("kicker") else ''}
<h1>{esc(c['headline'])}</h1>
  <p class="dek">{esc(c['one_line'])}</p>
  <div class="byline">
    <span>FILED {fmt_date(c['filed'])} · {esc(rel_days(c['filed']))}</span>
    <span>·</span><span>{due}</span>
    <span>·</span><span>BY {esc((c.get('sources') or [{}])[0].get('publisher','the counter').upper())}</span>
  </div>

  {article_photo}

  <div class="body">
    <p class="lede2">{esc(c['take'])}</p>
  </div>

  <p class="pull">Notice, name, choose. That's the whole method.</p>

  {sh_html}

  <p class="kicker" style="margin-top:40px">Sources</p>
  {''.join(src_rows)}

  {xl}
  {f'<p class="kicker" style="margin-top:40px">More from {esc(a.get("sign",""))}</p><div class="front front-2">{rel_html}</div>' if rel_html else ''}
</main>
{FOOT.format(root=r, sweep=MESSY, motto='NO ALGORITHM CHOSE THIS.<br>THAT IS THE POINT.')}
</body></html>"""


# ------------------------------------------------------------------ section
def build_ledger(data, enc):
    """/ledger/ - the standard, stated, and the figures that meet it.

    This is the front-facing half of what /citations/ is the technical half of.
    /citations/ is the audit dump, ranked by how much of the atlas points at
    each entry. This page is the editorial position: two states rather than
    one, a definition printed next to the number that depends on it, and the
    entries that carry no citation at all counted separately so they are not
    read as a deficit.

    Every figure comes from tools/ledger.py. Nothing here is typed. That is the
    point of the page as much as the point of the module - a hand-written count
    on a page about not hand-writing counts would be the exact thing the page
    argues against.
    """
    r = root(1)
    m = ledger_metrics(enc)
    st = (m["status_retrievable"] + m["status_unverified"]
          + m["status_needs_source"])
    if st != m["records"]:
        raise SystemExit(
            f"REFUSING to build /ledger/: record statuses sum to {st} against "
            f"{m['records']} records. A record has a status nobody has defined, "
            f"so the breakdown below would not add up.")
    return f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>The open ledger - Parasocialize</title>
<meta name="description" content="{esc(verified_note(m))}">
<link rel="stylesheet" href="{r}css/styles.css">
<link rel="alternate" type="application/rss+xml" title="Parasocialize" href="{SITE}/radar.xml">
<link rel="alternate" type="application/rss+xml" title="Parasocialize - the open ledger" href="{SITE}/ledger/feed.xml">
<link rel="icon" type="image/svg+xml" href="{SITE}/favicon.svg">
<meta property="og:title" content="The open ledger - Parasocialize">
<meta property="og:type" content="website">
<meta property="og:description" content="{esc(verified_note(m))}">
</head>
<body>
<a class="skip" href="#figures">Skip to the figures</a>
<div class="grain" aria-hidden="true"></div>
{NAV.format(root=r, total=len(data['cards']), mk=wordmark("nav"))}
<main class="section">
  <p class="kicker">THE STANDARD</p>
  <h1 style="font-family:var(--serif);font-size:clamp(2rem,5.4vw,3.4rem);font-weight:900;
     letter-spacing:-.03em;line-height:1.02;margin:0 0 16px">The open ledger</h1>
  <p class="sec-lede" style="max-width:64ch;font-size:1.08rem">This is the
  standard every claim on this site is held to, and the tally of where the
  catalogue stands against it. A citation that nobody checked is worth less
  than one that is &mdash; but most of the web does not tell you which you are
  looking at. This site records two states and prints both.</p>

  <div id="figures" class="cit-stats">
    <div><b>{m['openable']}</b><span>of {m['records']} records openable</span></div>
    <div><b>{m['no_locator']}</b><span>records with no locator</span></div>
    <div><b>{m['verified_entries']}</b><span>of {m['entries']} entries verified</span></div>
    <div><b>{m['status_needs_source']}</b><span>records that are not citations</span></div>
  </div>

  <h2>What "verified" means here</h2>
  <p style="max-width:66ch">{esc(VERIFIED_DEF)}</p>
  <p style="max-width:66ch">{esc(verified_note(m))}</p>

  <h2>The three states a record is in</h2>
  <ul class="ledger-list">
    <li><b>{m['status_retrievable']}</b> retrievable &mdash; a reader can open the
    record and find the work named. This is <i>not</i> a claim that it was read.</li>
    <li><b>{m['status_unverified']}</b> unverified &mdash; the work has been looked
    at and is not yet locatable. The honest state of a citation still in progress.</li>
    <li><b>{m['status_needs_source']}</b> needs-source &mdash; not a citation at
    all. A string that was never a reference, recorded as such rather than dressed
    up as one.</li>
  </ul>

  <h2>What is not a deficit</h2>
  <p style="max-width:66ch">{m['thesis']} entries carry no citation at all, and
  that is not an omission. They are the site's own argument &mdash; claims with no
  external referent to attach a source to &mdash; and a claim of that kind is not an
  unsourced claim. They are counted separately here so they cannot be read as one.</p>

  <p class="countline" style="margin-top:30px"><a href="{r}citations/index.html">
  The full per-entry backlog &rarr;</a></p>
  <p class="countline"><a href="{r}ledger/feed.xml">Follow the ledger &mdash;
  one item per day the figures moved &rarr;</a></p>
  <p style="margin-top:22px"><a class="btn btn-solid" href="{r}index.html">
  Back to the front page</a></p>
</main>
{FOOT.format(root=r, sweep=MESSY, motto='TEN TO CALL IT A LIST.<br>ONE TO MAKE THE CASE.')}
</body></html>"""


def build_exceptions(data, enc, placements):
    """/exceptions/ - the reciprocal ties, counted, and the gap admitted.

    The pitch for this page was a three-bar chart: 3 reciprocated, 5 simulated,
    2 directed, out of 240. Measuring it first showed the chart would have been
    wrong in the direction that flatters. `directed` is not the default value in
    the data - it is simply unmarked on 230 entries - so a chart of the three
    members reads as an axis that is mostly unclassified rather than one that is
    deliberately sparse.

    So: two numbers and an admission. What is actually striking is the shape,
    and two of the three claims on this page are caveats against our own data -
    the seventy-year silence in `simulated`, and the fact that eight of the ten
    carry no value on the otherness axis either. Both are printed rather than
    smoothed, because a site whose argument is that it does not launder its
    uncertainty cannot open by rounding up its own.
    """
    r = root(1)
    m = exceptions_metrics(enc, placements)
    bid = m["_by_id"]

    def link(i):
        e = bid.get(i)
        if not e:
            return f"<i>{esc(i)}</i>"
        return (f'<a href="{r}encyclopedia/{esc(i)}.html" '
                f'style="color:var(--hot)">{esc(e.get("title", i))}</a>')

    def yearline(ids):
        out = []
        for i in sorted(ids, key=lambda x: (bid.get(x, {}).get("year") or 0)):
            e = bid.get(i, {})
            out.append(f"{link(i)} <span class=\"cit-y\">{e.get('year')}</span>")
        return " &middot; ".join(out)

    if m["max_gap"]:
        gap_txt = (f"{m['max_gap']} years with nothing in between")
    else:
        gap_txt = "no gap"
    media_list = ", ".join(f"<code>{esc(x)}</code>" for x in m["media_without"])

    return f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<link rel="alternate" type="application/rss+xml" title="Parasocialize" href="{SITE}/radar.xml">
<link rel="alternate" type="application/rss+xml" title="Parasocialize - the open ledger" href="{SITE}/ledger/feed.xml">
<link rel="icon" type="image/svg+xml" href="{SITE}/favicon.svg">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Exceptions - Parasocialize</title>
<meta name="description" content="Of {m['entries']} entries, {m['labelled']} carry
a value on the reciprocity axis - and eight of those carry none on the otherness
axis either.">
<link rel="stylesheet" href="{r}css/styles.css">
<meta property="og:title" content="Exceptions - Parasocialize">
<meta property="og:type" content="website">
<meta property="og:description" content="{esc(m['labelled'])} of {m['entries']}
entries carry a value on the reciprocity axis. The other {m['entries'] - m['labelled']}
are unlabelled on purpose.">
</head>
<body>
<a class="skip" href="#counted">Skip to the count</a>
<div class="grain" aria-hidden="true"></div>
{NAV.format(root=r, total=len(data['cards']), mk=wordmark("nav"))}
<main class="section">
  <p class="kicker">RECIPROCITY &mdash; THE EXCEPTIONS</p>
  <h1 style="font-family:var(--serif);font-size:clamp(2rem,5.4vw,3.4rem);font-weight:900;
     letter-spacing:-.03em;line-height:1.02;margin:0 0 16px">Exceptions</h1>
  <p class="sec-lede" style="max-width:64ch;font-size:1.08rem">This site is named
  after one-sided attachment. A corpus about that subject that could not count its
  own exceptions would not be measuring the thing it is named after. So here they
  are, including the two ways the count is probably wrong.</p>

  <div id="counted" class="cit-stats">
    <div><b>{m['labelled']}</b><span>of {m['entries']} entries carry a value</span></div>
    <div><b>{m['reciprocated']}</b><span>reciprocated</span></div>
    <div><b>{m['simulated']}</b><span>simulated</span></div>
    <div><b>{m['directed']}</b><span>marked directed</span></div>
  </div>

  <p style="max-width:66ch;margin-top:22px">The other {m['entries'] - m['labelled']}
  are unlabelled on purpose. <code>directed</code> is the default condition of
  everything collected here, and marking all of them would bury the ones worth
  naming. An earlier draft of this page was going to be a three-bar chart; it was
  measured first, and the chart read as an axis that was mostly unclassified
  rather than one that is deliberately sparse.</p>

  <h2>{m['reciprocated']} reciprocated</h2>
  <p style="max-width:66ch">The other end would be missed if it stopped. These
  three sit {thousands(m['rec_span'])} years apart &mdash; {yearline(m['reciprocated_ids'])}
  &mdash; which is the argument for the whole site in one line. The exceptions are
  not a modern artifact.</p>

  <h2>{m['simulated']} simulated</h2>
  <p style="max-width:66ch">Reciprocity manufactured on one side and sold as the
  product. They arrive in exactly two clusters:
  {yearline(m['simulated_ids'])}. Three in fifteen years, two in a single year, and
  <b>{gap_txt}</b>.</p>
  <div class="note"><p><b>We do not know why, and we are not going to guess.</b>
  It may be a real feature of how mediated audiences work. It may be that a
  century of entries has never been checked against this axis at all. We think it
  is the second one, and the next paragraph is the evidence rather than the
  assurance.</p></div>

  <h2>The admission</h2>
  <div class="note"><p><b>{m['without_other']} of these {m['labelled']} carry no
  value on the <code>otherness</code> axis either.</b> Only {m['with_other']} do.
  The reciprocity and otherness axes were filled independently and have largely
  not been reconciled with each other &mdash; so the silence above is at least as
  likely to be our bookkeeping as it is to be a feature of the world. We would
  rather say that here than let a clean-looking chart imply we know.</p></div>

  <h2>Where the exceptions are not</h2>
  <p style="max-width:66ch">{m['media_total'] - len(m['media_without'])}
  of our {m['media_total']} media hold at least one. The other
  {len(m['media_without'])} hold none: {media_list}. Artificial intelligence has
  twenty entries and not one exception on this axis.</p>

  <p class="countline" style="margin-top:30px"><a href="{r}taxonomy/index.html#tx-reciprocity">
  The reciprocity axis itself &rarr;</a></p>
  <p style="margin-top:22px"><a class="btn btn-solid" href="{r}index.html">
  Back to the front page</a></p>
</main>
{FOOT.format(root=r, sweep=MESSY, motto='TEN TO CALL IT A LIST.<br>ONE TO MAKE THE CASE.')}
</body></html>"""


def build_ledger_feed(m):
    """/ledger/feed.xml - an item per day the figures actually moved.

    A feed that republished today's numbers on every build would promise movement
    and deliver the same item forever, so this is generated from
    `data/ledger_history.json`, which only gains a day when a watched figure
    changed. Each item therefore says what moved, in a sentence built from the
    difference - never "updated".

    This is deliberately low-noise. It is not a growth mechanic: there is no
    streak, no count of how long you have subscribed, and nothing that rewards
    daily return. The reader who wants it is the one who cares that the archive
    says what it does not know, and an item on a day nothing changed would be the
    opposite of that.
    """
    from ledger import HISTORY, snapshot_sentence, WATCHED
    hist = (json.loads(HISTORY.read_text(encoding="utf-8"))
            if HISTORY.exists() else {"days": []})
    days = hist.get("days") or []
    if not days:
        # An empty feed is a broken promise, so say so in the channel itself
        # rather than serving zero items and letting the reader conclude the
        # archive stopped counting.
        return ('<?xml version="1.0" encoding="UTF-8"?>\n'
                '<rss version="2.0"><channel>'
                '<title>Parasocialize &mdash; the open ledger</title>'
                f'<link>{SITE}/ledger/</link>'
                '<description>No movement recorded yet.</description>'
                '</channel></rss>\n')
    items = []
    for d in reversed(days):
        prev = days[days.index(d) - 1]["figures"] if days.index(d) else {}
        sent = snapshot_sentence(prev, d["figures"]) if prev else \
            "first recorded snapshot"
        f = d["figures"]
        body = (
            f"<p>{esc(sent)}.</p>"
            f"<p>{f['entries']} entries &middot; {f['records']} source records "
            f"&middot; {f['openable']} openable &middot; {f['no_locator']} without "
            f"a locator &middot; {f['verified_entries']} entries verified "
            f"&middot; {f['status_needs_source']} records that are not "
            f"citations.</p>"
            f'<p><a href="{SITE}/ledger/">Open the ledger</a></p>')
        items.append(
            f'<item><title>{esc(sent)}</title>'
            f'<link>{SITE}/ledger/</link>'
            f'<guid isPermaLink="false">{SITE}/ledger/#d-{esc(d["date"])}</guid>'
            f'<pubDate>{rfc822(d["date"])}</pubDate>'
            f'<category>ledger</category>'
            f'<description><![CDATA[{body}]]></description></item>')
    return ('<?xml version="1.0" encoding="UTF-8"?>\n'
            '<rss version="2.0" xmlns:atom="http://www.w3.org/2005/Atom">\n'
            '<channel>\n<title>Parasocialize — the open ledger</title>\n'
            f'<link>{SITE}/ledger/</link>\n'
            f'<atom:link href="{SITE}/ledger/feed.xml" rel="self" '
            'type="application/rss+xml"/>\n'
            '<description>One item per day the archive\'s own figures moved. '
            'No streak, no count, no daily prompt: the reader who wants this is '
            'the one who cares that the archive says what it does not know.'
            '</description>\n<language>en</language>\n'
            + "\n".join(items) + "\n</channel>\n</rss>\n")


def build_citations(data, enc):
    """/citations/ - the backlog, in public.

    The footer has said THE UNVERIFIED ONES ARE MARKED. NOT HIDDEN. since the
    first build, and 122 of 176 entries are not sourced. That is a sentence,
    and a sentence is not accountability. This page is the number behind it,
    ranked by how much of the graph lands on each entry: grief has nineteen
    edges into it, so a reader reaches its citation status nineteen times more
    often than a leaf's, and the fix order should follow that rather than
    author order.

    tools/verify_atlas.py produces the same table. This is that table, rendered,
    with no sign-off and no filtering to the flattering subset."""
    r = root(1)
    entries = enc["entries"]
    deg = {e["id"]: 0 for e in entries}
    for e in entries:
        for rel in (e.get("relations") or []):
            if rel["to"] in deg:
                deg[e["id"]] += 1
                deg[rel["to"]] += 1
    edges = sum(deg.values()) // 2

    def what(e):
        srcs = e.get("sources") or []
        if not srcs:
            return "no source at all"
        bits = []
        n = sum(1 for s in srcs if not str(s.get("url") or "").strip())
        u = sum(1 for s in srcs if s.get("status") not in ("verified", "retrievable"))
        if n:
            bits.append(f"{n} with no locator")
        if u:
            bits.append(f"{u} unchecked")
        return ", ".join(bits) or "complete"

    # "done" is DERIVED from the data, not read from the stored `verified` flag.
    #
    # The flag was marking 54 entries as sourced when 42 of them carried no
    # source record whatsoever - it had drifted from the thing it claims to
    # describe. On a page whose entire purpose is to be the honest number, the
    # optimistic side being wrong is the one failure that destroys the point, and
    # a stored boolean can always drift again. Deriving it means the two can
    # never disagree.
    def is_sourced(e):
        return bool(e.get("sources"))

    def is_checked(e):
        srcs = e.get("sources") or []
        return bool(srcs) and all(
            s.get("status") in ("verified", "retrievable") for s in srcs)

    done = [e for e in entries if is_sourced(e)]
    # Thesis entries carry no sources BY DESIGN - they are the site's own
    # argument. is_sourced() is therefore False for them, which put all 13 into
    # the backlog and made "not yet stood behind" count our own arguments as
    # things awaiting a citation that could never exist. That is precisely what
    # the comment below says this number must not do, so they are excluded here
    # and counted separately instead. Board backlog now agrees with
    # tools/add_source.py: 140 + 22 + 13 = 175.
    thesis_n = sum(1 for e in entries if e.get("provenance") == "thesis")
    todo = sorted((e for e in entries
                   if not is_sourced(e) and e.get("provenance") != "thesis"),
                  key=lambda e: (-deg.get(e["id"], 0), str(e.get("year") or 0)))
    checked = sum(1 for e in entries if is_checked(e))
    # Entries that are the site's own framework rather than claims about the
    # world. Counted and shown so the backlog above is a queue of things that can
    # actually be done, not a queue of arguments waiting for a citation that
    # could never exist.
    reached = sum(1 for e in todo if deg.get(e["id"], 0))
    lands = sum(deg.get(e["id"], 0) for e in todo) // 2

    with_loc = sum(1 for e in entries for s in (e.get("sources") or [])
                   if str(s.get("url") or "").strip())
    all_src = sum(len(e.get("sources") or []) for e in entries)

    rows = []
    for e in todo:
        med = (e.get("medium") or ["unclassified"])[0]
        yr = "undated" if e.get("year") is None else (
            f"{e['year']}" if not e.get("year_end") else f"{e['year']}&ndash;{e['year_end']}")
        rows.append(
            f'<tr><td class="cit-d">{deg.get(e["id"], 0)}</td>'
            f'<td><a href="{r}encyclopedia/{esc(e["id"])}.html">{esc(e["title"])}</a>'
            f'<span class="cit-y">{yr} &middot; {esc(med.replace("_", " "))}</span></td>'
            f'<td class="cit-k">{esc(e.get("kind", ""))}</td>'
            f'<td class="cit-m">{esc(what(e))}</td></tr>')

    done_rows = []
    for e in done[:40]:
        med = (e.get("medium") or ["unclassified"])[0]
        yr = "undated" if e.get("year") is None else (
            f"{e['year']}" if not e.get("year_end") else f"{e['year']}&ndash;{e['year_end']}")
        done_rows.append(
            f'<tr><td class="cit-d">{deg.get(e["id"], 0)}</td>'
            f'<td><a href="{r}encyclopedia/{esc(e["id"])}.html">{esc(e["title"])}</a>'
            f'<span class="cit-y">{yr} &middot; {esc(med.replace("_", " "))}</span></td>'
            f'<td class="cit-k">{esc(e.get("kind", ""))}</td>'
            f'<td class="cit-ok">sourced</td></tr>')

    return f"""<!DOCTYPE html>
<html lang="en"><head><meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Citations - Parasocialize</title>
<meta name="description" content="Every entry in the catalogue, and which of them somebody has actually checked.">
{HEAD.format(site=SITE, path="/citations/", otype="website",
             title="Citations - Parasocialize",
             desc="What in this catalogue is sourced and what is not.", root=r)}
</head>
<body>
<a class="skip" href="#backlog">Skip to the backlog</a>
<div class="grain" aria-hidden="true"></div>
{NAV.format(root=r, total=len(data['cards']), mk=wordmark("nav"))}
<main class="section">
  <p class="kicker">ACCOUNTABILITY</p>
  <h1 style="font-family:var(--serif);font-size:clamp(2rem,5.4vw,3.4rem);font-weight:900;
     letter-spacing:-.03em;line-height:1.02;margin:0 0 16px">Citations</h1>
  <p class="sec-lede" style="max-width:64ch;font-size:1.08rem">This site argues that
  a claim nobody checked is worth less than one that is. Here is the state of the
  catalogue, in public, ranked by how much of the <a href="{r}atlas/index.html"
  style="color:var(--hot)">atlas</a> points at each entry. No sign-off and no
  filtering to the flattering subset.</p>

  <div class="cit-stats">
    <div><b>{checked}</b><span>citations actually checked</span></div>
    <div><b>{len(done)}</b><span>sourced</span></div>
    <div><b>{len(todo)}</b><span>not yet stood behind</span></div>
    <div><b>{thesis_n}</b><span>are our own argument, and take no source</span></div>
    <div><b>{lands}</b><span>of {edges} edges land on something unchecked</span></div>
    <div><b>{with_loc}</b><span>of {all_src} sources {'has' if with_loc == 1 else 'have'} a locator</span></div>
  </div>

  <p class="countline" style="margin-top:22px;max-width:62ch">{thesis_n} of these
  entries are not claims about the world and will never carry a citation. They are
  the framework this site argues from - the counter, the paradox, the clerk, the
  card. An argument is not sourced, it is defended, and attaching a reference to
  one would be decoration dressed as rigour. They are marked as this site's own argument and counted separately, so the
  number above is a real backlog rather than a queue of things that cannot be
  done.</p>

  <div class="note" style="margin:30px 0 8px"><p>Two words that are not the same
  thing. <b>Sourced</b> means a person read the citation and stood behind it.
  <b>Retrieved</b> means the link resolves, which is a statement about a URL and
  not about the world. Most of the gap above is the second kind of problem: the
  claim is written and the reference exists, but nobody has fetched the reference
  or checked it against the sentence.</p>
  <p style="margin-top:14px">This page is the technical audit, ranked by how much
  of the atlas points at each entry. The <a href="{r}ledger/index.html"
  style="color:var(--hot)">open ledger</a> is the same data stated as an editorial
  standard &mdash; what the two words mean, what counts as read, and what is
  deliberately not counted as a deficit.</p></div>

  <p class="kicker" style="margin-top:38px">{len(done)} SOURCED</p>
  <table class="cit">
    <thead><tr><th>Edges</th><th>Entry</th><th>Kind</th><th>State</th></tr></thead>
    <tbody>{''.join(done_rows) if done_rows else '<tr><td colspan="4">none</td></tr>'}</tbody>
  </table>
  {f'<p class="countline">and {len(done)-40} more, in the '
     f'<a href="{r}encyclopedia/index.html">full index</a>.</p>' if len(done) > 40 else ''}

  <p class="kicker" style="margin-top:44px" id="backlog">THE BACKLOG, WORST FIRST</p>
  <p class="sec-lede" style="max-width:64ch">Ranked by degree, not by age. An entry
  with nineteen edges into it is reached nineteen times as often, so its citation
  status matters nineteen times over. This is the order to fix them in.</p>
  <table class="cit">
    <thead><tr><th>Edges</th><th>Entry</th><th>Kind</th><th>What is missing</th></tr></thead>
    <tbody>{''.join(rows)}</tbody>
  </table>
</main>
{FOOT.format(root=r, sweep="", motto='THE UNVERIFIED ONES ARE MARKED.<br>NOT HIDDEN.')}
</body></html>"""


# ---------------------------------------------------------------------------
# /desk/ - the signoff queue, rendered at build time
#
# This page used to be hand-written and client-fetched: it asked for
# ../data/queue.json and ../data/sweep.json at runtime. `data/` is in
# EXCLUDE_NAMES and never deployed, so both requests 404'd, the .catch() on each
# swallowed the failure into [] and {}, and the page rendered as an empty room -
# dashes for every stat, no queue, no rejections. It is linked as CLERK'S DESK in
# the footer of every generated page, so this was a working link to nothing,
# and the membership page used to promise a reader that the queue was visible.
#
# It is generated now, from queue.json and sweep.json, with the cards written
# into the HTML rather than fetched. Three reasons that is the right shape:
#   - it works with JavaScript off, which is the only way to be sure it works
#   - the data cannot silently disappear into a failed fetch again; if the file
#     is missing the build says so instead of the page quietly going blank
#   - filtering and sorting become DOM operations over already-rendered nodes,
#     so there is no second copy of the queue to fall out of step
# ---------------------------------------------------------------------------

AISLES = ["idol", "creator", "character", "companion", "world", "brand",
          "crossover", "contest", "grief", "danger"]
LAWS = {1: "Binding is public", 2: "Clerks beat algorithms",
        3: "Someone holds the dream", 4: "Grief when the companion changes",
        5: "Pay for proximity with open eyes", 6: "Characters move in",
        7: "Audit quarterly"}


def _since(iso):
    """How long ago, by UTC day. Plain, because the page is read by one person.

    Day granularity on purpose. Minute-level output made every rebuild produce
    a different desk page - "5m ago" became "9m ago" with nothing else changed -
    and the daily job committed that no-op every run. The page answers "is the
    sweeper alive", which is a day-scale question; the exact timestamp is on the
    card's title attribute for anyone who needs it.
    """
    try:
        when = datetime.datetime.fromisoformat(str(iso))
        if when.tzinfo is None:
            when = when.replace(tzinfo=datetime.timezone.utc)
        days = (datetime.datetime.now(datetime.timezone.utc).date()
                - when.astimezone(datetime.timezone.utc).date()).days
    except Exception:
        return "at an unknown time"
    if days <= 0:
        return "today"
    if days == 1:
        return "yesterday"
    return f"{days}d ago"


def build_desk(data):
    qp = ROOT / "data" / "queue.json"
    sp = ROOT / "data" / "sweep.json"
    if not qp.exists():
        raise SystemExit("desk: data/queue.json is missing - the page would "
                         "render empty, which is the bug this replaced")
    queue = json.loads(qp.read_text(encoding="utf-8"))
    sweep = json.loads(sp.read_text(encoding="utf-8")) if sp.exists() else {}
    r = root(1)

    unlensed = sum(1 for d in queue if d.get("state") == "awaiting_lens")
    rejected = sweep.get("rejected", 0)

    cards = []
    for d in queue:
        conf = round((d.get("conf") or 0) * 100)
        hay = " ".join(str(d.get(k) or "") for k in
                       ("headline", "domain", "section", "feed", "why")).lower()
        tags = []
        if d.get("state") == "awaiting_lens":
            tags.append('<span class="tag tag-od">NO LENS</span>')
        else:
            tags.append(f'<span class="tag tag-aisle">{conf}% CONFIDENCE</span>')
        if d.get("domain"):
            tags.append(f'<span class="tag tag-law">SRC {esc(d["domain"])}</span>')
        if d.get("section") and d["section"] in AISLES:
            tags.append(f'<span class="tag tag-aisle">SECTION '
                        f'{AISLES.index(d["section"]) + 1} '
                        f'{esc(d["section"].upper())}</span>')
        if d.get("law"):
            tags.append(f'<span class="tag tag-law">LAW {d["law"]} &middot; '
                        f'{esc(LAWS.get(d["law"], ""))}</span>')
        if d.get("shelf"):
            tags.append(f'<span class="tag tag-law">SHELF '
                        f'{esc(str(d["shelf"]).upper())}</span>')
        link = (f'<a href="{esc(d["url"])}" target="_blank" rel="noopener">'
                f'Read the source &rarr;</a>' if d.get("url")
                else '<span class="src">no source url</span>')
        cards.append(
            f'<article class="story story-lg" data-hay="{esc(hay)}" '
            f'data-conf="{conf}" data-at="{esc(str(d.get("at") or ""))}" '
            f'data-section="{esc(str(d.get("section") or ""))}">'
            f'<div class="body"><div class="tags">{"".join(tags)}</div>'
            f'<h3>{esc(d.get("headline") or "(untitled)")}</h3>'
            + (f'<p class="dek">{emph(d["one_line"])}</p>' if d.get("one_line") else "")
            + (f'<p class="take">{emph(d["take"])}</p>' if d.get("take") else "")
            + f'<p class="dek" style="font-style:italic">{emph(d.get("why") or "")}</p>'
            f'<div class="foot">{link}<span class="src">'
            f'{esc(d.get("feed") or "")}</span></div></div></article>')

    if not cards:
        cards.append('<p class="countline">The queue is empty.</p>')

    # What the machine turned down. Rendered from the sweep's own
    # rejected_sample, and when that is empty the page says so - the old
    # version had a heading promising rejections the data has never contained.
    rej = []
    for row in (sweep.get("rejected_sample") or [])[:20]:
        rej.append(f'<div class="log-row"><span class="tick" style="--c:#e63946">'
                   f'</span><span><b>{esc(row.get("title"))}</b>'
                   f'<span class="meta">{emph(row.get("why"))}</span></span>'
                   f'<span class="tag tag-od">no</span></div>')
    if not rej:
        rej.append('<div class="log-row"><span class="tick" style="--c:#3d2e23">'
                   '</span><span><b style="color:var(--dimmer)">Nothing has been '
                   'rejected yet.</b><span class="meta">The filter files what it '
                   'finds and leaves the rest for a person. It has turned '
                   'nothing down in the history of this pipeline, so this '
                   'section is a promise rather than a record.</span></span></div>')

    # The measured work order. This is the desk's answer to "what should be
    # written next": tools/plan_next.py derives it from the corpus every daily
    # run, and printing it here is what turns a planner into a queue somebody
    # actually reads. A missing plan is said out loud rather than rendered as
    # an empty heading, the same rule the rejected list above follows.
    plan = {}
    pp = ROOT / "data" / "plan.json"
    if pp.exists():
        try:
            plan = json.loads(pp.read_text(encoding="utf-8"))
        except ValueError:
            plan = {}
    work = []
    for a in (plan.get("actions") or [])[:6]:
        why = esc(str(a.get("why") or ""))
        cmd = esc(str(a.get("command") or ""))
        work.append(
            f'<div class="log-row"><span class="tick" style="--c:var(--mint)">'
            f'</span><span><b>{esc(str(a.get("target") or ""))}</b>'
            f'<span class="meta">{why}'
            + (f'<br><code>{cmd}</code>' if cmd else "")
            + f'</span></span><span class="tag tag-law">'
              f'{esc(str(a.get("kind") or ""))}</span></div>')
    if not work:
        work.append('<div class="log-row"><span class="tick" style="--c:#3d2e23">'
                     '</span><span><b style="color:var(--dimmer)">No plan has '
                     'been measured yet.</b><span class="meta">Run '
                     '<code>python tools/plan_next.py</code>. A desk with no '
                     'work order is a desk guessing.</span></span></div>')

    return f"""<!DOCTYPE html>
<html lang="en"><head><meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<meta name="robots" content="noindex, nofollow">
<title>The clerk's desk - Parasocialize</title>
<meta name="description" content="The signoff queue. A filter files, a person signs.">
{HEAD.format(site=SITE, path="/desk/", otype="website",
             title="The clerk's desk - Parasocialize",
             desc="The signoff queue.", root=r)}
</head>
<body>
<a class="skip" href="#desk">Skip to the queue</a>
<div class="grain" aria-hidden="true"></div>
{NAV.format(root=r, total=len(data['cards']), mk=wordmark("nav"))}
<main>
<section class="section" id="desk">
  <p class="kicker" style="color:var(--neon)">Back office &middot; noindex &middot; swept {_since(sweep.get("last_run", ""))}</p>
  <div class="sec-head">
    <h1 style="color:var(--neon)">The desk</h1>
    <p class="sec-lede">A filter files. A person signs. <b style="color:var(--paper)">
    Nothing reaches the front page without a person deciding it should.</b> A
    model that gets this wrong is a nuisance. A model that gets this wrong
    <em>published</em> is why everyone stops trusting a site like this, and trust
    is the only thing here that matters.</p>
  </div>

  <div class="front front-3" style="margin-top:28px">
    <div class="price" style="gap:4px"><p class="flag">Last sweep</p>
      <div class="amt" style="font-size:1.4rem" title="last sweep {esc(str(sweep.get('last_run') or 'unknown'))}">{_since(sweep.get("last_run", ""))}</div>
      <p style="color:var(--dim);font-size:.84rem">{sweep.get("duration_s", 0)}s &middot;
      {sweep.get("candidates", 0)} candidates seen</p></div>
    <div class="price" style="gap:4px"><p class="flag">Feeds reached</p>
      <div class="amt" style="font-size:1.4rem">{sweep.get("feeds_ok", 0)} / {sweep.get("feeds_total", 0)}</div>
      <p style="color:var(--dim);font-size:.84rem">{esc(sweep.get("model") or "")}</p></div>
    <div class="price hot" style="gap:4px"><p class="flag">Waiting on a human</p>
      <div class="amt" style="font-size:1.4rem">{len(queue)}</div>
      <p style="color:var(--dim);font-size:.84rem">{rejected} turned down this sweep</p></div>
  </div>

  <p class="kicker" style="margin-top:44px">Next categorical work, measured {esc(plan.get("generated") or "never")}</p>
  <p class="sec-lede" style="margin-bottom:14px;font-size:.96rem">Not a mood
  board. <b>tools/plan_next.py</b> counts the corpus every daily run and ranks
  what is thinnest - the media, the categories, the decades and the pipeline
  itself. A gap is named, never filled by a script.</p>
  <div class="ledger">{"".join(work)}</div>

  <p class="kicker" style="margin-top:44px">The queue</p>
  <div class="bar">
    <input class="search" id="q" type="search" placeholder="Filter by headline, source or section&hellip;" aria-label="Filter the queue">
    <select id="sort" aria-label="Sort" style="padding:11px 14px;border-radius:99px;border:1px solid var(--line);background:var(--bg2);color:var(--paper);font-family:var(--label);font-size:.66rem">
      <option value="conf">Most confident first</option>
      <option value="date">Newest first</option>
      <option value="section">By section</option>
    </select>
  </div>
  <p class="countline" id="count" aria-live="polite">{len(queue)} IN THE QUEUE{(" &middot; %d WITH NO LENS (no model key set)" % unlensed) if unlensed else ""}</p>
  <div class="front front-2" style="margin-top:18px" id="queue">{"".join(cards)}</div>

  <p class="kicker" style="margin-top:44px">What the filter turned down, and why</p>
  <p class="sec-lede" style="margin-bottom:14px;font-size:.96rem">Kept on purpose. A
  filter that only shows you what it likes is a filter you cannot audit, and the
  entire claim of this site is that the line is deliberate.</p>
  <div class="ledger">{"".join(rej)}</div>

  <p class="kicker" style="margin-top:44px">Signing off</p>
  <div class="note">
    <p>To publish a draft: edit <b>data/queue.json</b> &mdash; set
    <b>"state":"signed"</b>, fill in <b>section</b>, <b>law</b> and <b>shelf</b>
    if the filter left them null &mdash; then run
    <b>python tools/build_cards.py</b>. <b>This page is generated from that
    file</b>, so it cannot be edited by hand; an edit here is overwritten on the
    next build.</p>
    <p>Give it a real <b>sources[0].url</b>. A card with an unresolved link is
    rendered with a <em>treat with suspicion</em> note on purpose, and that is a
    thing to fix rather than leave.</p>
    <p>Going away? Set <b>PARASOCIALIZE_BUDGET=0</b> and the queue stops
    growing. Note that <b>the filter is not running on a schedule</b> &mdash; it
    runs when it is run, and the last sweep was {_since(sweep.get("last_run", ""))}.
    Nothing here claims a cadence the site does not keep.</p>
  </div>
</section>
</main>
<footer class="footer"><div class="foot-grid foot-mini">
  <div>
    <p class="wordmark foot-mark"><img class="logo-img lg" src="{r}img/logo.svg" alt="">PARA<b>SOCIALIZE</b></p>
    <p class="foot-note">NOINDEX &middot; THIS PAGE IS NOT FOR READERS</p>
  </div>
  <nav class="foot-nav" aria-label="Footer">
    <a href="{r}index.html">FRONT PAGE</a><a href="{r}sections/index.html">SECTIONS</a><a href="{r}radar.xml">RSS</a>
  </nav>
</div></footer>
<script>
(function(){{
  // Filtering and sorting over cards the build already wrote. No fetch, no
  // embedded copy of the queue - the page and the data cannot disagree.
  var box=document.getElementById("queue"),
      q=document.getElementById("q"),
      sort=document.getElementById("sort"),
      count=document.getElementById("count"),
      all=Array.prototype.slice.call(box.querySelectorAll("article"));
  if(!all.length)return;
  var total=all.length, base=count.textContent.split(" IN THE QUEUE")[0];
  function apply(){{
    var t=(q.value||"").trim().toLowerCase(), shown=[];
    all.forEach(function(el){{
      var hit=!t||(el.getAttribute("data-hay")||"").indexOf(t)>-1;
      el.style.display=hit?"":"none";
      if(hit)shown.push(el);
    }});
    shown.sort(function(a,b){{
      var s=sort.value;
      if(s==="conf")return (+b.getAttribute("data-conf"))-(+a.getAttribute("data-conf"));
      if(s==="section")return (a.getAttribute("data-section")||"zz")
        .localeCompare(b.getAttribute("data-section")||"zz");
      return (b.getAttribute("data-at")||"").localeCompare(a.getAttribute("data-at")||"");
    }});
    shown.forEach(function(el){{box.appendChild(el);}});
    count.textContent=shown.length+" / "+total+" IN THE QUEUE";
  }}
  q.addEventListener("input",apply);
  sort.addEventListener("change",apply);
}})();
</script>
</body></html>"""


def build_credits(data, manifest):
    """Every photograph on the site, once, with who made it and under what terms.

    This page exists because the credit used to live stamped on the homepage
    tiles, which made the front page read like a stock library and made ten
    identical-looking strings do the work of ten different obligations. The
    obligation is real either way - these are CC BY and CC BY-SA photographs and
    attribution is a condition of use, not a courtesy - so it is discharged in
    one place, plus on the section front where each photograph appears at size.
    """
    r = root(1)
    rows = []
    for it in manifest.get("items", []):
        f = img_for(manifest, it.get("slug"), 1)
        if not f:
            continue
        src = it.get("src") or {}
        # Take the kind `img_for` already resolved rather than re-reading it.
        # This line read `src.get("kind", "")` and so always got "", which made
        # every badge ILLUSTRATION. Fixing `img_for` alone changed nothing here,
        # because this assignment overwrote its result - the tell was that the
        # built page did not move after a fix that should have. `kind` lives on
        # the record since the image claims were corrected; `src` is provenance
        # and never held a human judgement about a picture.
        kind = f.get("kind", "")
        badge = ("<span class=\"tag tag-law\">EXACT</span>" if kind == "exact"
                 else "<span class=\"tag\">ILLUSTRATION</span>")
        page = f.get("page", "#")
        link = (f'<a href="{esc(page)}" target="_blank" rel="noopener nofollow">'
                f'{esc(f["credit"])}</a>') if page != "#" else esc(f["credit"])
        rows.append(
            f'<li class="cr"><a class="cr-thumb" href="{esc(page)}" target="_blank" '
            f'rel="noopener nofollow"><img src="{esc(f["path"])}" alt="" loading="lazy"></a>'
            f'<div><p class="cr-cap">{esc(f["caption"])}</p>'
            f'<p class="cr-by">{link} &middot; used on {esc(it.get("for", "the site"))}'
            f' &middot; {badge}</p></div></li>')
    return f"""{HEAD.format(site=SITE, path="/credits/", otype="website",
              title="Credits - Parasocialize",
              desc="Every photograph on this site, who made it, and under what licence.",
              root=r)}
</head>
<body>
<a class="skip" href="#s">Skip to the credits</a>
<div class="grain" aria-hidden="true"></div>
{NAV.format(root=r, total=len(data["cards"]), mk=wordmark("nav"))}
<main>
<section class="section" id="s">
  <div class="sec-head">
    <p class="kicker">{len(rows)} PHOTOGRAPHS</p>
    <h1>Credits</h1>
    <p class="sec-lede">Every image on this site, who took it, and what it was
    licensed under. None of it was hotlinked: each file was resolved once
    through the Wikimedia Commons API or the Flickr public feed, cached here, and
    credited to the person who made it.</p>
  </div>
  <p class="take" style="margin:22px 0 30px">Where a photograph is of the
  <em>subject matter</em> rather than of the specific event in the story, it is
  marked <b>ILLUSTRATION</b> and captioned with what is actually in the frame. A
  photo of a stadium is never captioned as the night the thing happened. That
  distinction is the difference between a publication and a scraper, and it is
  the one place a licence claim has to be true.</p>
  <ul class="cr-list">{''.join(rows)}</ul>
</section>
</main>
{FOOT.format(root=r, sweep="", motto='THE UNVERIFIED ONES ARE MARKED.<br>NOT HIDDEN.')}
</body></html>"""


# Which expression iYi wears per section, and why.
#
# A mascot that is the same on every page is wallpaper. These ten sections are
# ten different relationships, and each blurb already says what the relationship
# feels like, so the expression is read off the section rather than picked to
# look decorative:
#
#   character  never real, fictional, played      -> nobody is home
#   world      you live inside and cannot reach   -> nobody is home
#   crossover  supposed to be reachable            -> nobody is home
#   brand      learned your name                  -> behind the counter
#   idol       performs at you                    -> showing off
#   contest    the one you are fighting about     -> the clock is red
#   danger     where it turned criminal           -> the clock is red
#   creator    shows up until you know the routine-> looking back, steady
#   companion  the one that answers back          -> looking back. this is us.
#   grief      the one who left                    -> grief
#
# love is deliberately absent. It belongs to a romantic beat and nothing else.
SECTION_MOOD = {
    "idol": "wink", "creator": "watch", "character": "hollow",
    "companion": "watch", "world": "hollow", "brand": "clerk",
    "crossover": "hollow", "contest": "panic", "grief": "sad",
    "danger": "panic",
}


def build_section(a, data, manifest=None):
    r = root(2)
    col = a.get("colour", "#ffb454")
    manifest = manifest or {"items": []}
    mine = sorted([c for c in data["cards"] if c["section"] == a["id"]],
                  key=lambda c: str(c.get("filed", "")), reverse=True)
    if not mine:
        return ""
    lead, rest = mine[0], mine[1:]
    big = "".join(story(c, data["sections"], data["laws"], big=True, root_=r,
                        manifest=manifest, depth=2) for c in rest[:6])
    rest2 = "".join(story(c, data["sections"], data["laws"], root_=r,
                          manifest=manifest, depth=2) for c in rest[6:12])

    others = [x for x in data["sections"] if x["id"] != a["id"]]
    nav = "".join(
        f'<a class="chip{" on" if x["id"]==a["id"] else ""}" '
        f'style="--c:{esc(x.get("colour","#ffb454"))}" href="{r}section/{esc(x["id"])}/index.html">'
        f'{esc(x["sign"])}</a>' for x in others)

    return f"""<!DOCTYPE html>
<html lang="en"><head><meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{esc(a['sign'])} - the {esc(a['sign'].lower())} section - Parasocialize</title>
<meta name="description" content="{esc(a['blurb'])}">
{HEAD.format(site=SITE, path=f"/section/{a['id']}/", otype="website",
             title=f"{a['sign']} - Parasocialize", desc=esc(a['blurb']), root=r)}
</head>
<body>
<a class="skip" href="#s">Skip to stories</a>
<div class="grain" aria-hidden="true"></div>
{NAV.format(root=r, total=len(data["cards"]), mk=wordmark("nav"))}
<div style="height:5px;background:{esc(col)}"></div>
<main>
<section class="section" id="s">
  <p class="kicker" style="color:{esc(col)}">{len(mine)} stor{"y" if len(mine)==1 else "ies"}</p>
  <div class="sec-head">
    <div class="sec-head-txt">
      <h1 style="color:{esc(col)}">{esc(a['sign'])}</h1>
      <p class="sec-lede">{esc(a['blurb'])} <em style="color:var(--dim)">{esc(a['note'])}</em></p>
    </div>
    <div class="sec-head-iyi" title="iYi, in the expression this section is about">{mascot(104, "", SECTION_MOOD.get(a['id'], 'watch'))}</div>
  </div>

  {fig(manifest, f"aisle-{esc(a['id'])}", 2, "sec-mast")}

  <div class="lead" style="margin-top:28px">
    <a class="cover" href="{r}radar/{esc(lead['slug'])}.html" tabindex="-1" aria-hidden="true"
       style="{poster_bg(lead, data['sections'])};border-radius:12px;overflow:hidden;box-shadow:0 18px 46px rgba(0,0,0,.6);aspect-ratio:2/3;display:flex;align-items:flex-end;padding:14px">
      <span style="position:relative;z-index:2">
        <b style="display:block;font-family:var(--label);font-size:.6rem;letter-spacing:.16em;color:rgba(255,255,255,.8)">MOST RECENT</b>
        <span style="display:-webkit-box;-webkit-line-clamp:3;-webkit-box-orient:vertical;overflow:hidden;font-family:var(--serif);font-size:.9rem;font-weight:700;color:#fff;line-height:1.15;text-shadow:0 2px 8px rgba(0,0,0,.6)">{esc(lead['headline'])}</span>
      </span>
    </a>
    <div>
      <h2><a href="{r}radar/{esc(lead['slug'])}.html">{esc(lead['headline'])}</a></h2>
      <p class="dek">{esc(lead['one_line'])}</p>
      <p class="take">{esc(lead['take'])}</p>
      <a class="btn btn-solid" href="{r}radar/{esc(lead['slug'])}.html">Read the full thing</a>
    </div>
  </div>

  {f'<div class="front">{big}</div>' if big else ''}
  {f'<div class="front" style="margin-top:20px">{rest2}</div>' if rest2 else ''}

  <p class="kicker" style="margin-top:48px">Other sections</p>
  <div class="chips">{nav}</div>
  <p class="countline"><a href="{r}sections/index.html">See everything, searchable →</a></p>
</section>
</main>
{FOOT.format(root=r, sweep=MESSY, motto='TEN SECTIONS.<br>SEVEN OF THEM ARE NEW HERE.')}
</body></html>"""


# ------------------------------------------------------------------ the eight ways
WAY_MOOD = {
    "persona": "wink", "character": "hollow", "companion": "watch",
    "divine": "watch", "institution": "clerk", "cosmology": "hollow",
    "officer": "watch", "predator": "panic",
}


def build_way(a, tax, enc, data, manifest=None):
    """One of the eight ways it shows up, as a page.

    Built from the placements rather than written out, for the same reason
    /taxonomy/ is: a category page that can drift from the category is a
    second, wrong set of facts about the same subject, published. Every story
    and entry listed here was filed on this way in data/, and a shelf with
    nothing on it says so rather than disappearing.
    """
    r = root(2)
    col = a.get("colour", "#ffb454")
    manifest = manifest or {"items": []}
    pla = json.loads((ROOT / "data" / "taxonomy_placements.json")
                     .read_text(encoding="utf-8"))["assignments"]
    spl = story_placements()
    byid = {e["id"]: e for e in enc["entries"]}

    mine = sorted(cards_on_way(data["cards"], a["id"], spl),
                  key=lambda c: str(c.get("filed", "")), reverse=True)
    lead = pick_from_pool(ranked_pool(mine))

    # The daily pick for this way. The editor writes one per category per UTC
    # day; it is a story or an entry already filed on this shelf, so the block
    # adds a date and a reason rather than a new claim. If it is the same story
    # the lead poster chose, the block takes the lead's place instead of
    # printing the same headline twice.
    today_iso = datetime.datetime.now(datetime.timezone.utc).date().isoformat()
    ed = _editorial_today()
    if str(ed.get("date")) != today_iso:
        ed = {}
    pick = (ed.get("ways") or {}).get(a["id"]) if ed else None
    if pick and lead and pick.get("kind") == "story" and \
            pick.get("id") == lead.get("slug"):
        lead = None
    rest = [c for c in mine if lead is None or c["slug"] != lead["slug"]]

    def pick_href(p):
        if p.get("kind") == "story":
            return f'{r}radar/{esc(p.get("id"))}.html'
        return f'{r}encyclopedia/{esc(p.get("id"))}.html'

    def pick_art(p):
        """A real photograph for a story, or the entry's title plate.

        The daily case has to look like a front page, not a bibliography. A
        story with a sourced photograph uses it; an entry uses the plate that
        already belongs to that entry. If neither exists the card gets a colour
        panel with the way's name rather than an empty hole.
        """
        if p.get("kind") == "story":
            c = next((x for x in data["cards"] if x["slug"] == p.get("id")), None)
            if c:
                f = (img_for(manifest, p.get("id"), 2)
                     or img_aisle(manifest, c.get("section"), 2))
                if f:
                    return f["path"], f.get("caption", "")
        eid = str(p.get("id") or "")
        if (ROOT / "img" / "plate" / f"{eid}.svg").exists():
            return f'{r}img/plate/{eid}.svg', "Title plate for the entry"
        return "", ""

    today_html = ""
    if pick:
        art, art_cap = pick_art(pick)
        art_cls = " is-plate" if art.endswith(".svg") else ""
        art_html = (f'<a class="way-today-art{art_cls}" href="{pick_href(pick)}" '
                    f'tabindex="-1" aria-hidden="true"><img src="{esc(art)}" '
                    f'alt="" loading="lazy"></a>' if art else
                    f'<a class="way-today-art" style="display:flex;align-items:center;'
                    f'justify-content:center;background:linear-gradient(150deg,#2a1a10,'
                    f'#120d0a);color:var(--hot);font-family:var(--serif);font-weight:900;'
                    f'font-size:2rem;text-align:center;padding:18px" '
                    f'href="{pick_href(pick)}" tabindex="-1" aria-hidden="true">'
                    f'<span>{esc(a["sign"])}</span></a>')
        kind_label = "Today's story" if pick.get("kind") == "story" else "Today's entry"
        meta = str(pick.get("meta") or "")
        meta_p = f'<span class="way-today-meta">{esc(meta)}</span>' if meta else ""
        track = str(pick.get("track") or "")
        track_p = (f'<span class="way-today-track">{esc(track)}</span>'
                   if track else "")
        meta_sep = ('<span class="way-today-dot">&middot;</span>'
                    if meta_p and track_p else "")
        wires = pick.get("wires") or []
        wire_p = ""
        if wires:
            wire_links = " &middot; ".join(
                f'<a href="{esc(w.get("url"))}" target="_blank" rel="noopener">'
                f'{esc(w.get("title"))}</a>'
                + (f' <span>{esc(w.get("publisher"))}</span>' if w.get("publisher") else "")
                for w in wires[:2])
            wire_p = f'<p class="way-today-wires"><b>In the wires.</b> {wire_links}</p>'
        today_html = f"""<article class="way-today">
  {art_html}
  <div class="way-today-txt">
    <p class="kicker">Today on this way &middot; {fmt_date(today_iso)} &middot; {kind_label}</p>
    <h2><a href="{pick_href(pick)}">{esc(pick.get("title") or pick.get("id"))}</a></h2>
    <p class="way-today-dek">{esc(pick.get("why") or "")}</p>
    <p class="way-today-meta-line">{meta_p}{meta_sep}{track_p}</p>
    {wire_p}
    <a class="btn btn-solid" href="{pick_href(pick)}">Read the case</a>
  </div>
</article>"""
    else:
        today_html = ('<p class="countline">Today&rsquo;s pick has not been '
                      'measured yet. The rest of the shelf is below.</p>')

    try:
        wdays = json.loads((ROOT / "data" / "ways_history.json")
                           .read_text(encoding="utf-8")).get("days") or []
    except (OSError, ValueError):
        wdays = []
    recent = []
    for d in reversed(wdays):
        if str(d.get("date")) == today_iso:
            continue
        p = (d.get("picks") or {}).get(a["id"])
        if not p:
            continue
        art, _ = pick_art(p)
        art_cls = " is-plate" if art.endswith(".svg") else ""
        thumb = (f'<span class="way-day-thumb{art_cls}"><img src="{esc(art)}" alt="" '
                 f'loading="lazy"></span>' if art else
                 '<span class="way-day-thumb way-day-noart"></span>')
        recent.append(f'<li><a href="{pick_href(p)}">{thumb}'
                      f'<span class="way-day-copy"><span class="way-day-date">'
                      f'{fmt_date(d.get("date"))}</span>'
                      f'<b>{esc(p.get("title") or p.get("id"))}</b></span></a></li>')
        if len(recent) >= 5:
            break
    if recent:
        recent_html = (f'<details class="way-days"><summary>The last five days</summary>'
                       f'<ul>{"".join(recent)}</ul></details>')
    elif pick:
        art, _ = pick_art(pick)
        art_cls = " is-plate" if art.endswith(".svg") else ""
        thumb = (f'<span class="way-day-thumb{art_cls}"><img src="{esc(art)}" '
                 f'alt="" loading="lazy"></span>' if art else
                 '<span class="way-day-thumb way-day-noart"></span>')
        recent_html = (f'<details class="way-days"><summary>The last five days</summary>'
                       f'<ul><li><a href="{pick_href(pick)}">{thumb}'
                       f'<span class="way-day-copy"><span class="way-day-date">Today</span>'
                       f'<b>{esc(pick.get("title") or pick.get("id"))}</b></span>'
                       f'</a></li></ul></details>')
    else:
        recent_html = ('<details class="way-days"><summary>The last five days</summary>'
                       '<ul><li><span class="way-day-date">Today</span>'
                       f'<a href="{r}taxonomy/index.html">The daily record '
                       'begins here &rarr;</a></li></ul></details>')

    cat_n = sum(1 for v in pla.values() if v.get("cat") == a["id"])
    story_n = len(mine)
    story_word = f"{story_n} stor{'y' if story_n == 1 else 'ies'}"
    entry_word = f"{cat_n} entr{'y' if cat_n == 1 else 'ies'}"

    def entry_rows(sub):
        out = []
        for eid, v in sorted(pla.items()):
            if v.get("sub") != sub:
                continue
            e = byid.get(eid)
            if not e:
                continue
            out.append(
                f'<li><a href="{r}encyclopedia/{esc(eid)}.html">'
                f'<b>{esc(e.get("title"))}</b>'
                f'<span class="tx-why">{esc(e.get("year") or "")} · '
                f'{esc(enc["kinds"].get(e.get("kind", ""), ""))}</span>'
                f'<span class="tx-r">{emph(v.get("why") or "")}</span></a></li>')
        return "".join(out)

    subs = []
    for s in a["sub"]:
        in_sub = [c for c in rest
                  if (spl.get(c["slug"]) or {}).get("sub") == s["id"]]
        rows = entry_rows(s["id"])
        ns, ne = len(in_sub), sum(1 for v in pla.values()
                                  if v.get("sub") == s["id"])
        label = (f"{ns} stor{'y' if ns == 1 else 'ies'} · "
                 f"{ne} entr{'y' if ne == 1 else 'ies'}")
        if rows:
            body = f'<ul class="tx-entries">{rows}</ul>'
        else:
            body = ('<p class="tx-empty">Nothing is filed on this shelf yet. '
                    'The gap is recorded rather than hidden.</p>')
        cards_html = "".join(
            story(c, data["sections"], data["laws"], take=False, root_=r,
                  manifest=manifest, depth=2) for c in in_sub)
        if cards_html:
            body = f'<div class="front">{cards_html}</div>' + body
        subs.append(f"""<details class="tx-sub" id="w-{esc(s['id'])}">
  <summary><span class="tx-name">{esc(s['name'])}</span>
    <span class="tx-n">{esc(label)}</span></summary>
  <p class="tx-def">{emph(s['def'])}</p>
  {body}
</details>""")

    lead_html = ""
    if not mine:
        lead_html = ('<p class="countline">No story is filed on this way yet. '
                     'The entries below are what the way holds.</p>')
    if lead:
        lead_html = f"""<div class="lead" style="margin-top:28px">
  <a class="cover" href="{r}radar/{esc(lead['slug'])}.html" tabindex="-1" aria-hidden="true"
     style="{poster_bg(lead, data['sections'])};border-radius:12px;overflow:hidden;box-shadow:0 18px 46px rgba(0,0,0,.6);aspect-ratio:2/3;display:flex;align-items:flex-end;padding:14px">
    <span style="position:relative;z-index:2">
      <b style="display:block;font-family:var(--label);font-size:.6rem;letter-spacing:.16em;color:rgba(255,255,255,.8)">ON THIS WAY NOW</b>
      <span style="display:-webkit-box;-webkit-line-clamp:3;-webkit-box-orient:vertical;overflow:hidden;font-family:var(--serif);font-size:.9rem;font-weight:700;color:#fff;line-height:1.15;text-shadow:0 2px 8px rgba(0,0,0,.6)">{esc(lead['headline'])}</span>
    </span>
  </a>
  <div>
    <h2><a href="{r}radar/{esc(lead['slug'])}.html">{esc(lead['headline'])}</a></h2>
    <p class="dek">{esc(lead['one_line'])}</p>
    <p class="take">{esc(lead['take'])}</p>
    <a class="btn btn-solid" href="{r}radar/{esc(lead['slug'])}.html">Read the full thing</a>
  </div>
</div>"""

    others = [x for x in tax["attachment"] if x["id"] != a["id"]]
    nav = "".join(
        f'<a class="chip" style="--c:{esc(x.get("colour", "#ffb454"))}" '
        f'href="{r}ways/{esc(x["id"])}/index.html">{esc(x["sign"])}</a>'
        for x in others)

    return f"""<!DOCTYPE html>
<html lang="en"><head><meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{esc(a['sign'])} - one of the eight ways - Parasocialize</title>
<meta name="description" content="{esc(a['blurb'])}">
{HEAD.format(site=SITE, path=f"/ways/{a['id']}/", otype="website",
             title=f"{a['sign']} - Parasocialize", desc=esc(a['blurb']), root=r)}
</head>
<body>
<a class="skip" href="#w">Skip to the way</a>
<div class="grain" aria-hidden="true"></div>
{NAV.format(root=r, total=len(data["cards"]), mk=wordmark("nav"))}
<div style="height:5px;background:{esc(col)}"></div>
<main>
<section class="section" id="w">
  <p class="kicker" style="color:{esc(col)}">One of eight ways · {story_word} · {entry_word}</p>
  <div class="sec-head">
    <div class="sec-head-txt">
      <h1 style="color:{esc(col)}">{esc(a['sign'])}</h1>
      <p class="sec-lede">{esc(a['blurb'])} <em style="color:var(--dim)">{esc(a['note'])}</em></p>
    </div>
    <div class="sec-head-iyi" title="iYi, in the expression this way is about">{mascot(104, "", WAY_MOOD.get(a['id'], 'watch'))}</div>
  </div>

  <p class="countline"><a href="{r}taxonomy/index.html#tx-{esc(a['id'])}">The definition, the test and the boundary →</a></p>

  {today_html}
  {recent_html}

  {lead_html}

  {''.join(subs)}

  <p class="kicker" style="margin-top:48px">Other ways</p>
  <div class="chips">{nav}</div>
  <p class="countline"><a href="{r}taxonomy/index.html">All eight ways, and the registers underneath them →</a></p>
</section>
</main>
{FOOT.format(root=r, sweep=MESSY, motto='EIGHT WAYS IT SHOWS UP.<br>ONE WAY IN.')}
</body></html>"""


# ------------------------------------------------------------------ all sections
def build_aisle(data, feat=None, manifest=None):
    r = root(1)
    sections, cards = data["sections"], data["cards"]
    feat = feat or {"lists": [], "moments": []}
    manifest = manifest or {"items": []}
    blocks = []
    for a in sections:
        mine = [c for c in cards if c["section"] == a["id"]]
        col = a.get("colour", "#ffb454")
        n = len(mine)
        blocks.append(
            f'<a class="aisle" style="--c:{esc(col)}" href="{r}section/{esc(a["id"])}/index.html">'
            f'<b>{esc(a["sign"])}</b><p>{esc(a["blurb"])}</p>'
            f'<span class="count"><b>{n}</b> stor{"y" if n==1 else "ies"}</span></a>')
    latest = "".join(story(c, sections, data["laws"], take=False, root_=r,
                             manifest=manifest, depth=1) for c in cards[:18])

    # feature doors at the top: the lists, the history, the moments. A door
    # whose photograph is missing carries no art box at all - an empty 56px
    # rectangle reads as a broken image, and the door is a sentence anyway.
    fdoors = []
    for L in (feat.get("lists") or []):
        f = img_for(manifest, L.get("image"), 1)  # /sections/ is depth 1
        art = (f'<span class="fdoor-art"><img src="{esc(f["path"])}" alt="" '
               f'loading="lazy"></span>') if f else ""
        fdoors.append(f'<a class="fdoor" href="{r}top8/index.html" style="--c:#ff5a1f">'
                      f'{art}'
                      f'<span class="fdoor-body"><b>{esc(L["kicker"])}</b>'
                      f'<strong>Top 8</strong><span>{esc(L["title"])}</span></span></a>')
    for slug, name, kick, blurb, imslug in [
            ("history", "The history", "A course in eight modules",
             "The whole documented history of one-sided attachment, free.", "history-macy-store"),
            ("moments", "The moments", "The ones that moved it",
             f"{len(feat.get('moments', []))} significant moments across every domain.", "moment-power-rangers")]:
        f = img_for(manifest, imslug, 1)  # sections page: depth 1
        art = (f'<span class="fdoor-art"><img src="{esc(f["path"])}" alt="" '
               f'loading="lazy"></span>') if f else ""
        fdoors.append(f'<a class="fdoor" href="{r}{esc(slug)}/index.html" style="--c:#a04dff">'
                      f'{art}'
                      f'<span class="fdoor-body"><b>{esc(kick)}</b>'
                      f'<strong>{esc(name)}</strong><span>{esc(blurb)}</span></span></a>')

    return f"""<!DOCTYPE html>
<html lang="en"><head><meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>All sections - Parasocialize</title>
<meta name="description" content="Ten sections of one-sided attachment: idols, creators, characters, companions, worlds, brands, crossers, contests, grief and the ones that turn criminal.">
{HEAD.format(site=SITE, path="/sections/", otype="website",
             title="All sections - Parasocialize",
             desc="Ten sections of one-sided attachment.", root=r)}
</head>
<body>
<a class="skip" href="#a">Skip to sections</a>
<div class="grain" aria-hidden="true"></div>
{NAV.format(root=r, total=len(data["cards"]), mk=wordmark("nav"))}
<main>
<section class="section" id="a">
  <p class="kicker">The whole shop · {len(cards)} stories · {len(sections)} sections</p>
  <div class="sec-head">
    <h1>Pick a section. Or don't.</h1>
    <p class="sec-lede">Parasocial is a relationship where the other end cannot say it back. It is not a genre - it is a
    shape, and it shows up in a stadium and in a court docket and in the teacher at the front of the room exactly as hard as
    it shows up in a fandom. Ten sections. Seven of them a fandom site would never build.</p>
  </div>
  {f'<div class="fdoors" style="margin-top:24px">{"".join(fdoors)}</div>' if fdoors else ''}
  <div class="aisles" style="margin-top:16px">{''.join(blocks)}</div>

  <p class="kicker" style="margin-top:44px">Search all {len(cards)} stories</p>
  <div class="bar"><input class="search" id="q" type="search" placeholder="Try: grief, AI, football, landlords, Replika…"
      aria-label="Search all stories"></div>
  <p class="countline" id="count" aria-live="polite"></p>
  <div class="front" style="margin-top:20px" id="list">{latest}</div>
</section>
</main>
{FOOT.format(root=r, sweep=MESSY, motto='SEARCHABLE.<br>THAT IS THE POINT.')}
<script>
(function(){{
  var q=document.getElementById('q'),c=document.getElementById('count'),
      l=document.getElementById('list'),all=l.children.length;
  function run(){{
    var t=(q.value||'').trim().toLowerCase(),n=0;
    [].forEach.call(l.children,function(el){{
      var hit=!t||(el.textContent||'').toLowerCase().indexOf(t)>-1;
      el.style.display=hit?'':'none';if(hit)n++;
    }});
    c.textContent=n+' / '+all+' STORIES'+(t?' · "'+q.value.toUpperCase()+'"':'');
  }}
  q.addEventListener('input',run);run();
}})();
</script>
</body></html>"""


# ------------------------------------------------------------------ front page
# ---- curation ------------------------------------------------------------
# Both numbers are measured rather than picked. The corpus's median card age
# is 16 days and only one card in forty-eight is younger than six, so the
# six-day freshness window that used to sit here could never fire: every card
# scored 0 on it and the ranking was a permanent leaderboard of `res`, which
# is how a section's tile came to show a 46-day-old story with four newer
# ones underneath. A window nobody can enter is not a window.
FRESH_DAYS = 28          # the span over which this shelf files new material
FRESH_PTS = 16.0         # what a card filed today earns, to 0 at FRESH_DAYS
ROTATE_SPREAD = 18       # how far below the leader the rotation pool reaches
ROTATE_POOL = 4          # at most this many cards ever share one tile
ROTATE_FRESH_DAYS = 21   # how far behind the section's newest card a card may
                         # sit and still take the tile at all


def cur_slot(now=None):
    """The curation slot: twice a day, in UTC.

    UTC on purpose. A selection that depends on the builder's timezone is a
    selection nobody can reproduce - the front page would differ between a
    laptop in Australia and a runner in Virginia, and neither could say
    which one was right.
    """
    now = now or datetime.datetime.now(datetime.timezone.utc)
    day = (now.date() - datetime.date(2026, 1, 1)).days
    return day * 2 + (0 if now.hour < 12 else 1)


def live_lists(feat, today=None):
    """The lists that have been released, in file order.

    A list is live once its `released` date has arrived; a list with no date
    counts as the oldest and is always live, so a file holding a single
    undated list still builds. This is the one place that rule lives -
    pick_list, show_list, the archive and the front page's kicker all read it
    here - because two answers to "which lists exist yet" is the defect that
    once put `candidate` entries on /top8/: one of the answers is wrong, and
    nothing notices.
    """
    lists = (feat or {}).get("lists") or []
    today = today or datetime.datetime.now(datetime.timezone.utc).date().isoformat()
    return [L for L in lists if (L.get("released") or "") <= today]


def pick_list(feat, today=None):
    """The newest live list - the one the pool tools curate.

    See live_lists() for what live means. Lists are released whole, so "the
    newest" is a property of the data and the date rather than of the build
    clock: every reader and every build names the same list, and there is no
    state file to drift. Ties keep file order, so a new list becomes the
    newest by being dated later, not by being moved.

    This is NOT what the front page and /top8/ put on show - that is the list
    dated today, generated by tools/editor.py and returned by show_list()
    below. This answer is "which list is being worked on": it is the list
    tools/t8_pool.py edits and it carries the refusal for an empty live set.
    """
    lists = (feat or {}).get("lists") or []
    if not lists:
        raise ValueError("features.json holds no top-8 list to show")
    live = live_lists(feat, today)
    if not live:
        raise SystemExit(
            "REFUSING to build: every top-8 list in features.json is dated in "
            "the future, so there is nothing to show today.")
    return max(live, key=lambda L: L.get("released") or "")


def show_list(feat, today=None):
    """The list dated today - the daily edition, never a former list.

    tools/editor.py appends exactly one list per UTC day, with `released` set
    to that day. This returns it. It deliberately does not fall back to a
    former list: the old behaviour rotated across every live list, so the
    cartoons edition written once came round again every few days and the
    front page never showed a genuinely new list. A daily feature that can
    silently show a months-old edition is not a daily feature.

    If today's edition is missing the build refuses. That is the honest
    failure: a red build is better than a front page whose "today" is
    yesterday's list. `tools/daily.py` runs the editor before this, so the
    normal path always has one; a bare `build_cards.py` on a new day does not.

    The date is UTC and comes from the same clock as every other rotation, so
    the show, the record and the page cannot straddle midnight.
    """
    iso = (str(today)[:10] if today else
           datetime.datetime.now(datetime.timezone.utc).date().isoformat())
    lists = (feat or {}).get("lists") or []
    today_lists = [L for L in lists
                   if str(L.get("released") or "")[:10] == iso]
    if not today_lists:
        raise SystemExit(
            f"REFUSING to build: no top-8 list is dated {iso}. The daily "
            "edition is generated by tools/editor.py, which tools/daily.py "
            "runs before the build. Showing a former list instead is the "
            "defect this refusal exists to prevent.")
    # File order is stable. If a same-day refresh left two, the editor replaces
    # in place rather than appending, so this is defence rather than policy.
    return today_lists[-1]


def ranked_pool(mine, now=None):
    """The stories eligible for a tile, best first.

    Takes an already-filtered list, so the same ranking and rotation serve a
    section's tile and a category's. RANK - importance (`res`), the state
    bonuses, and a freshness window measured in weeks rather than days.

    ROTATE - the best-scoring card would otherwise hold the tile until
    something outranked it, and nothing does. So a pool forms and
    `pick_from_pool` picks one out of it by slot: ranked, so the pool is
    always the best stories, and rotating, so the tile moves twice a day
    instead of sitting for months.

    Two gates on the pool, each of which failed without the other. A score
    band alone let a 77-day-old card share a tile with a 13-day-old one,
    because the state bonuses are worth six points and swamp a fortnight of
    freshness - so "rotates" would have meant "alternates between fresh and
    stale". A freshness gate alone closed the band until the state tiers
    pulled it apart and a five-card section had a pool of one. So a card
    must be within ROTATE_SPREAD of the leader AND no more than
    ROTATE_FRESH_DAYS behind the set's own newest card.

    A set with one card has a pool of one and the rotation is silent.
    """
    if not mine:
        return []
    now = now or datetime.datetime.now(datetime.timezone.utc)
    today = now.date()

    def filed(c):
        try:
            return datetime.date.fromisoformat(str(c.get("filed"))[:10])
        except Exception:
            return None

    def rank(c):
        s = c.get("res") or 0
        if c.get("state") == "OVERDUE":
            s += 12
        if c.get("state") == "OUT":
            s += 6
        d = filed(c)
        if d:
            s += max(0, FRESH_DAYS - (today - d).days) * FRESH_PTS / FRESH_DAYS
        return s

    ranked = sorted(mine, key=rank, reverse=True)
    lead = rank(ranked[0])
    stamps = [d for d in (filed(c) for c in mine) if d]
    newest = max(stamps) if stamps else None

    def in_pool(c):
        if rank(c) < lead - ROTATE_SPREAD:
            return False
        d = filed(c)
        if newest is None or d is None:
            return True
        return (newest - d).days <= ROTATE_FRESH_DAYS

    return [c for c in ranked if in_pool(c)][:ROTATE_POOL] or ranked[:1]


def section_pool(cards, section, now=None):
    """The stories eligible for a section's tile, best first."""
    return ranked_pool([c for c in cards if c["section"] == section], now)


def pick_from_pool(pool, now=None):
    """The one story that represents the set right now: one out of the pool,
    chosen by the slot. See ranked_pool for why it is a pool rather than a
    sort.
    """
    if not pool:
        return None
    now = now or datetime.datetime.now(datetime.timezone.utc)
    return pool[cur_slot(now) % len(pool)]


def pick_top(cards, section, now=None):
    """The story that represents the section right now."""
    now = now or datetime.datetime.now(datetime.timezone.utc)
    return pick_from_pool(section_pool(cards, section, now=now), now)


def story_placements():
    """The story side of the classification: slug -> category placement."""
    p = ROOT / "data" / "story_placements.json"
    if not p.exists():
        return {}
    return json.loads(p.read_text(encoding="utf-8")).get("placements") or {}


def cards_on_way(cards, cat, spl=None):
    """The stories filed on one of the eight attachment ways."""
    spl = story_placements() if spl is None else spl
    return [c for c in cards if (spl.get(c["slug"]) or {}).get("cat") == cat]


def deck(take, words=20):
    """The front page's teaser for a story: whole sentences, never a mid-word cut.

    This used to be `" ".join(take.split()[:20]) + "..."`, which produced
    "The panics about fans being manipulated by fandoms turn out to be a..." -
    a sentence cut off at its own last word. Ten of those in one grid reads as
    a page of truncation bugs, and that is exactly what it was reported as.

    A `take` is 48 to 173 words, so it has to be cut. It is cut at sentence
    boundaries instead: whole sentences until the budget is spent, and if the
    first sentence alone is over budget it is kept whole rather than amputated.
    The only fallback is a clause boundary, and it never takes an ellipsis with
    it, because a teaser that never lands is not a teaser.
    """
    take = " ".join((take or "").split())
    if not take:
        return ""
    sentences = [s for s in re.split(r"(?<=[.!?])\s+", take) if s]
    out, n = [], 0
    for s in sentences:
        if out and n + len(s.split()) > words:
            break
        out.append(s)
        n += len(s.split())
    s = " ".join(out).strip()
    if s.endswith((".", "!", "?")):
        return s
    # one long sentence: fall back to its last clause, and end it properly
    for sep in (" - ", " — ", "; ", ", "):
        if sep in s:
            s = s.rsplit(sep, 1)[0].rstrip(" ,;-—")
            break
    return s.rstrip(" ,;-—") + ("." if s else "")


def build_front(data, feat=None, manifest=None, hist=None):
    sections, laws, shelf, cards = data["sections"], data["laws"], data["shelf"], data["cards"]
    feat = feat or {"lists": [], "moments": [], "figures": []}
    manifest = manifest or {"items": []}
    hist = hist or {"modules": []}
    tax = json.loads((ROOT / "data" / "taxonomy.json").read_text(encoding="utf-8"))
    spl = story_placements()
    pla = json.loads((ROOT / "data" / "taxonomy_placements.json")
                     .read_text(encoding="utf-8"))["assignments"]
    cat_entries = Counter(v.get("cat") for v in pla.values())

    # ---- the rotating top 8 column. Which list is on show is today's pick
    # in the daily rotation (show_list): the live lists take turns, one per
    # UTC day, anchored on the newest `released`, so this and /top8/ name the
    # same one; the lists not up today are at /top8/archive/. Which EIGHT of
    # that list are on show is decided in top8_window(), by the date, so the
    # page always carries eight.
    # ---- the top 8. `entries` is the list as released, in rank order. Each
    # still carries a stage: candidate while drafted for a future list,
    # featured once the list ships. A former list is never edited to archive
    # it - it is superseded by a newer `released`, so the history of what this
    # site showed stays on disk.
    #
    # 8 is a motif on this site, so the page must never show fewer than eight and
    # must never show more. Which eight, and the stage filter and the floor
    # assertion, all live in top8_window() - shared with build_top8, which used
    # to read the raw pool and so published the candidates.
    L = top8_window(feat)
    if L["entries"]:
        # All eight, in rank order.
        #
        # This used to sample four of the eight, picked by rank, which produced
        # exactly what a reader reported as broken: a block headed "The top 8"
        # showing four items numbered 1, 3, 5 and 7. Not a rendering fault - the
        # code asked rotate() for 4 on purpose - but a heading that promises
        # eight and delivers four, with the numbering visibly skipping, reads as
        # an error even when it is a decision.
        #
        # Two honest ways out: show all eight, or stop calling it the top 8. The
        # list IS a top 8, the front page is where it should be readable, and
        # there is room. So: all eight, sequentially, and the rotation now
        # chooses *which* list rather than trimming this one.
        _raw = next((x for x in (feat.get("lists") or [])
                     if x.get("slug") == L.get("slug")), L)
        _span = t8_year_span(_raw)
        _home_title = L.get("home_title") or L.get("title") or "The Top 8"
        _home_hook = (L.get("home_hook") or deck(L.get("dek"), 30)).strip()
        rows = []
        # In the order the rotation window handed over, which is pool order.
        # This used to re-sort by the stored `rank`, which had two costs: a
        # promoted candidate has none and raised KeyError, and sorting a
        # window that was deliberately built in rotation order threw that
        # order away and restored pool order. Numeral comes from the position.
        for _i, en in enumerate(L["entries"], 1):
            _anchor = t8_anchor(L, en)
            _hook = t8_hook(en)
            rows.append(
                f'<a class="t8card" href="top8/index.html#{_anchor}">'
                f'<span class="t8card-rank">{_i:02d}</span>'
                f'<span class="t8card-body">'
                f'<span class="t8card-tag">{esc(en.get("show", ""))}</span>'
                f'<b>{esc(en["name"])}</b>'
                f'<span class="t8card-hook">{esc(_hook)}</span>'
                f'<span class="t8card-go">Read this entry &rarr;</span>'
                f'</span></a>')
        # one line, on the front page, because the photographs are of the fans
        # rather than of the cartoons and that is worth saying before somebody
        # wonders why a list about cartoons is illustrated with a toy
        # ---- why there are no cartoon frames in this list
        #
        # This used to read: "Not one frame of these cartoons is freely
        # licensed, so every picture above is of the audience instead - which is
        # the list." First clause true, second false for half the pictures.
        # Opening all six records settled it:
        #
        #   t8-1  a roller coaster with green tubular supports   (an amusement ride)
        #   t8-2  Rugrats-themed baby shower decor                (merchandise)
        #   t8-3  a cosplayer as Oscar the Grouch                 (the audience)
        #   t8-4  cosplay of Zuko at AVA Expo                    (the audience)
        #   t8-6  the cast on a Comic-Con panel, audience in frame (both)
        #   t8-8  the Animaniacs at WonderCon                    (the audience)
        #
        # Three of six are the audience. **A blanket claim about a set, written
        # before anybody opened the set** - the same shape as the must term,
        # which also passed on metadata rather than on the picture.
        #
        # The fix is a sentence true of all six, and it turns out to be the
        # better one: what the six share is not that they are all audience shots
        # but that the cartoons left the screen and became objects. That is more
        # or less what this site is about, so the honest sentence is also the
        # sharper one.
        #
        # ---- and then the set changed size under the sentence
        #
        # The sentence above was fixed when the list was six photographs. It is
        # eight entries now, and **two of them have no photograph at all**:
        # `t8-5-dragontales` and `t8-7-doug` were withdrawn at review, with no
        # image and no source. So the corrected sentence - "what is up there is
        # what the cartoons turned into", "the pictures are of the audience" -
        # was a claim about every member of a set, written when every member
        # was a picture, and nobody re-checked it when two stopped being one.
        #
        # **This is item 25 arriving from the other side.** That item was a
        # blanket sentence about six pictures, false for three of them, and the
        # lesson recorded was "a summary sentence is not a shorter citation, and
        # it is checked the same way: by looking at every member." Here the
        # sentence is true of the six and false for the two, which is the same
        # defect with the numbers inverted, and it survived because the *style*
        # had been fixed once already and the fix is what made it look settled.
        #
        # So the sentence now counts, and says why two are blank. Saying so is
        # not an apology: it is the same standard the /top8/ page already states
        # per entry ("no free frame exists"), and a page that shows eight things
        # and claims about all of them has to account for the two it is not
        # showing.
        # The "not one frame of these cartoons is freely licensed..." caption used
        # to sit under this grid on the front page. Removed: it is six lines of
        # licensing detail in the middle of a page whose next block is the
        # sections, and it restated on every release what the page changes.
        # The disclosure is not lost - /top8/ prints "no free frame exists" on
        # each of the two plates that have no photograph, which is the only place
        # a reader can act on it, since that page shows them at size. The front
        # page keeps the designed plate, so a blank one still reads as a
        # deliberate state rather than a broken image.
        # "One list so far: the top 8 parasocial moments in saturday morning
        # cartoons of the 1990s" used to sit under the grid, and it was the
        # clearest case yet of a line written for the author and shipped to the
        # reader. It counts what the data file happens to hold, which a reader
        # cannot check, cannot act on, and has no reason to care about - and it
        # lowercased the list's own proper title to get there, so it was wrong
        # about the corpus as well as unnecessary. "Rotates weekly" was the same
        # class of claim and went with it: with one list in the file nothing
        # rotates, so the front page was promising a schedule the build does not
        # keep. The kicker below is the reader-facing part and stays.
        # Two facts decide the kicker, and both come from the same place the
        # block is built from. With more than one live list the honest label
        # is which list is on show - today's pick in the daily rotation,
        # through show_list - because "this week"/"rotating" claimed a
        # schedule the build never had. Within one list, a pool larger than
        # eight does rotate, and that claim comes from top8_window() itself
        # rather than being re-derived here: the last time this sentence and
        # the behaviour were measured in two places, they disagreed.
        _live_n = len(live_lists(feat))
        _meta = esc(str(L.get("kicker") or "").title())
        if _span:
            _meta = f"{_meta} &middot; {_span}" if _meta else _span
        # The archive link appears only when there is an archive to read: the
        # page is built from the former lists, so before a second list is
        # dated it is a placeholder. A door to a placeholder is a promise the
        # data cannot keep yet.
        _ghost = ('<a class="t8front-archive" '
                  'href="top8/archive/index.html">Browse every list &rarr;</a>'
                  if _live_n > 1 else "")
        _raw_n = len(_raw.get("entries") or L["entries"])
        t8_block = f"""<section class="section t8front" id="top8" aria-labelledby="t8front-title">
  <div class="t8front-head">
    <p class="kicker">Today's top 8 <span class="t8front-kick">{_meta}</span></p>
    <h2 id="t8front-title">{esc(_home_title)}</h2>
    <p class="t8front-hook">{esc(_home_hook)}</p>
  </div>
  <div class="t8cards">{''.join(rows)}</div>
  <div class="t8front-foot">
    <a class="btn btn-solid t8front-cta" href="top8/index.html">View Full Top 8 Analysis &amp; Archive History &rarr;</a>
    {_ghost}
  </div>
  <p class="t8front-note">Eight of {_raw_n} from this list, chosen for today. The full list and the day record are on the Top 8 page.</p>
</section>"""
    else:
        t8_block = ""

    # ---- the three feature doors: history / moments / figures
    feats = []
    if hist.get("modules"):
        feats.append(('history', 'The history', '',
                      f"A course in {len(hist['modules'])} modules, from a sculptor to a 2023 policy update. Free, printable.",
                      "history-macy-store", len(hist['modules'])))
    if feat.get("moments"):
        feats.append(('moments', 'The moments', '',
                      f"{len(feat['moments'])} significant moments across television, music, the internet, games and AI.",
                      "moment-power-rangers", len(feat['moments'])))
    if feat.get("figures"):
        feats.append(('figures', 'The figures', '',
                      f"{len(feat['figures'])} people and characters who keep the sphere turning, from Pygmalion to a Twitch emote.",
                      None, len(feat['figures'])))
    fcards = []
    for slug, name, kick, blurb, imslug, count in feats:
        f = img_for(manifest, imslug, 0)  # front page: depth 0
        im = f'<img src="{esc(f["path"])}" alt="" loading="lazy">' if f else ""
        if not im:
            # The art box used to be left empty whenever a door had no cached
            # photograph, which renders as a dark 56px rectangle with nothing
            # in it - a hole that reads as a missing image, on a page whose
            # whole argument is that it does not pretend about pictures. The
            # box is styled for a label, so it carries the number its own
            # blurb states: modules, moments, figures.
            im = f"<b>{count:02d}</b>"
        fcards.append(f"""<a class="fdoor" href="{esc(slug)}/index.html" style="--c:{esc(next((a.get('colour','#ff5a1f') for a in sections if a['id']=='history'), '#ff5a1f'))}">
  <span class="fdoor-art">{im}</span>
  <span class="fdoor-body"><strong>{esc(name)}</strong><span>{esc(blurb)}</span></span>
</a>""")

    # eight tiles, one per attachment category, each showing the story that
    # represents that way now. A category with no story filed yet carries its
    # definition and its entry count instead of borrowing a story from
    # somewhere else - the gap is true, and a tile that pretended otherwise
    # would be the one thing this page cannot do.
    tiles = []
    for a in tax["attachment"]:
        col = a.get("colour", "#ff5a1f")
        mine = cards_on_way(cards, a["id"], spl)
        top = pick_from_pool(ranked_pool(mine))
        if top:
            n = len(mine)
            body = (f"<h3>{esc(top['headline'])}</h3>"
                    f"<p>{esc(deck(top.get('take', '')))}</p>")
            go = f"{n} stor{'y' if n == 1 else 'ies'} →"
            # No caption and no credit on the tile. The credit is a licence
            # obligation, not decoration, so it cannot simply be dropped - but
            # stamping it on every face made the homepage read like a stock
            # library. The same photograph appears at size on the story page,
            # which carries the credit, and every file is listed once on
            # /credits/. That satisfies attribution in a reasonable manner and
            # keeps the page a page.
            f = (img_for(manifest, top.get("image"), 0)
                 or img_for(manifest, top.get("slug"), 0)
                 or img_aisle(manifest, top.get("section"), 0))
            img = f'<img src="{esc(f["path"])}" alt="">' if f else ""
        else:
            ne = cat_entries.get(a["id"], 0)
            body = (f"<h3>{esc(a['blurb'])}</h3>"
                    f"<p>{esc(a['note'])}</p>")
            go = f"{ne} entr{'y' if ne == 1 else 'ies'} →"
            img = ""
        tiles.append(f"""<a class="hub" style="--c:{esc(col)}" href="ways/{esc(a['id'])}/index.html">
  <span class="hub-art">{img}</span>
  <b class="hub-name">{esc(a['sign'])}</b>
  {body}
  <span class="hub-go">{go}</span>
</a>""")

    total = len(cards)
    # The encyclopedia's size is read, not typed. A number written into a
    # template is a number that goes stale silently and reads as true until
    # someone checks - the `kind: exact` from a filename, in a different place.
    # The loaded file is kept rather than discarded: the parasocialite block
    # below resolves its figure against this same copy, so the page cannot
    # describe an entry set the count was not measured against.
    _enc = json.loads((ROOT / "data" / "encyclopedia.json").read_text(encoding="utf-8"))
    nent = len(_enc["entries"])
    # ---- the masthead's words. They live in data/front_copy.json, one edition
    # per bi-daily release, and are built from there rather than from the
    # template - a number or a sentence written into a template is a claim that
    # goes stale silently and reads as true until somebody checks. The door
    # lines are the one place a count hides inside a sentence, so they carry
    # {total} and {nent} tokens substituted HERE, at render, from the numbers
    # measured above: the edition of 2026-10-18 read "248 entries, every claim
    # cited." while the corpus held 255, which is this defect live on the front
    # page. An edition written before the tokens existed carries its literal
    # number and is left exactly as it is - the sequence of what the page
    # actually said is the record, and the substitution is a no-op there.
    # See tools/front_copy.py.
    ed = dict(front_copy_edition())
    ed["door_stories"] = (ed.get("door_stories") or "").replace(
        "{total}", str(total))
    ed["door_encyclopedia"] = (ed.get("door_encyclopedia") or "").replace(
        "{nent}", str(nent))

    # ---- the parasocialite of the day, above the fold: one figure taking
    # turns, one per UTC day, chosen by date from data/parasocialite.json -
    # the same arithmetic as the register rotation, and the same rule as the
    # top 8: what is on show is a property of the date; what is stored is the
    # day it happened on. The block resolves its entry from the copy loaded
    # above, so medium, era and the link come from the data rather than the
    # roster, and record_parasocialite_day() in main() runs before this page
    # renders, so the record under the block and the block itself cannot name
    # different figures.
    _psotd = parasocialite_of_day(parasocialite_roster())
    psotd_block = ""
    if _psotd:
        _pse = next((e for e in _enc["entries"]
                     if e.get("id") == (_psotd.get("entry") or _psotd.get("id"))),
                    None)
        if _pse:
            _phref = f'encyclopedia/{esc(_pse["id"])}.html'
            # The block names the medium family, not the chip values: "television
            # scripted, television unscripted" is right on the entry page and
            # reads like a database on a front-page line. First segment,
            # deduplicated, order kept.
            _pfam = []
            for m in (_pse.get("medium") or []):
                fam = str(m).split("_")[0]
                if fam and fam not in _pfam:
                    _pfam.append(fam)
            _pmed = " &middot; ".join(esc(m) for m in _pfam)
            _pmeta = (f'{_pmed} &middot; {esc(_fmt_span(_pse))}' if _pmed
                      else esc(_fmt_span(_pse)))
        else:
            # A roster entry whose encyclopedia record is gone degrades to the
            # hub rather than printing a dead link with a name on it.
            _phref = "encyclopedia/index.html"
            _pmeta = ""
        _pmline = f'<p class="psotd-meta">{_pmeta}</p>' if _pmeta else ""
        _plabel = esc(_psotd.get("name") or _psotd.get("id") or "")
        _pval = esc(_psotd.get("valence") or "")
        _pkind = str(_psotd.get("kind") or "figure").lower()
        _pkind_label = (f"{_pkind.title()} figure"
                        if _pkind in ("real", "fictional") else "Figure")
        _src = _psotd.get("source") or {}
        _srcline = ""
        if isinstance(_src, dict) and str(_src.get("url") or "").startswith("http"):
            _srcline = (f' <a href="{esc(_src["url"])}" target="_blank" '
                        f'rel="noopener">{esc(_src.get("publisher") or "the wire")}</a>')
        _pwhy = ""
        if _psotd.get("why_today"):
            _pwhy = (f'<p class="psotd-why"><b>Why today.</b> '
                     f'{esc(_psotd["why_today"])}{_srcline}</p>')
        _pplate = ""
        if _pse and (ROOT / "img" / "plate" / f"{_pse['id']}.svg").exists():
            _pplate = (f'<img class="psotd-plate" src="img/plate/'
                       f'{esc(_pse["id"])}.svg" alt="" loading="lazy">')
        _ptell = _psotd.get("tell") or _figure_detail(_pse)
        _ptell_html = (f'<p class="psotd-tell"><b>The detail.</b> '
                       f'{esc(_ptell)}</p>' if _ptell else "")
        _plock = "psotd-lockup" + ("" if _pplate else " psotd-noart")
        psotd_block = f"""<section class="section psotd-sec" aria-labelledby="psotd-kick">
  <p class="kicker" id="psotd-kick">Parasocialite of the day
    <span class="psotd-kind">{esc(_pkind_label)}</span>
    <span class="psotd-val psotd-val-{_pval}">{_pval}</span></p>
  <div class="psotd-card">
    <div class="{_plock}">
      {_pplate}
      <div class="psotd-copy">
        <h2 class="psotd-name"><a href="{_phref}">{_plabel}</a></h2>
        {_pmline}
        <p class="psotd-break">{esc(_psotd.get("breakdown") or "")}</p>
        {_pwhy}
        {_ptell_html}
        <p class="psotd-more"><a href="{_phref}">The whole entry &rarr;</a></p>
      </div>
    </div>
  </div>
  {parasocialite_record()}
</section>"""

    return f"""<!DOCTYPE html>
<html lang="en"><head><meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Parasocialize</title>
<meta name="description" content="Parasocial is a real relationship with somebody who cannot say it back. News, argument, research and the definitive history - idols, AI, sport, politics, grief. Free.">
{HEAD.format(site=SITE, path="/", otype="website", title="Parasocialize",
             desc="News, argument, research and the definitive history. Free.", root="")}
</head>
<body>
<a class="skip" href="#hub">Skip to the eight ways</a>
<div class="grain" aria-hidden="true"></div>
{NAV.format(root="", total=total, mk=wordmark("nav"))}

<main>
<section class="masthead">
  <div class="wrap">
    <h1>Parasocialize.</h1>

    <p class="line">{ed.get("line")}</p>

    <!-- One row: the two doors the masthead promises, then the clerk. These
         three used to be split across two grid columns with the 1956/-70,000
         block between them, so the two doors were not adjacent to the thing
         that introduced them and the clerk floated beside a pair of numerals
         that had nothing to do with it. A reader is told the site has two modes
         and then has to hunt for them. -->

    <div class="fdoors masthead-row">
      <a class="fdoor" href="sections/index.html" style="--c:var(--hot)">
        <span class="fdoor-body"><b>To read</b><strong>The stories</strong>
        <span>{ed.get("door_stories")}</span></span></a>
      <a class="fdoor" href="encyclopedia/index.html" style="--c:var(--mint)">
        <span class="fdoor-body"><b>To research</b>
        <strong>The encyclopedia</strong>
        <span>{ed.get("door_encyclopedia")}</span></span></a>

      <aside class="clerk" aria-labelledby="clerk-kick">
        <div class="clerk-face" role="img" aria-label="iYi, the Parasocialize mascot, behind the counter">{mascot(88, "mascot-hero", mood="clerk")}</div>
        <p class="clerk-kick" id="clerk-kick">{ed.get("kicker")}</p>
        <p class="clerk-line">{ed.get("clerk_line")}</p>
        <a class="clerk-more" href="brand/index.html">What the mascot is for &rarr;</a>
      </aside>
    </div>
  </div>
</section>

{psotd_block}

{t8_block}

<section class="section hub-band" id="hub">
  <div class="band-head">
    <div>
      <p class="kicker">One way in to each</p>
      <h2>Eight ways it shows up.</h2>
    </div>
    <a class="band-link" href="taxonomy/index.html">All eight, defined &rarr;</a>
  </div>
  <div class="hubs">{''.join(tiles)}</div>
</section>

{''.join(fcards) and f"""<section class="section" style="padding-top:18px">
  <p class="kicker">Go deeper · the definitive bits</p>
  <div class="fdoors">{''.join(fcards)}</div>
</section>"""}

<section class="section signal-sec">
  <form class="signal-form" action="https://formsubmit.co/iNNERdreamers@gmail.com" method="POST">
    <input type="hidden" name="_subject" value="New Signal subscriber">
    <input type="hidden" name="_captcha" value="false">
    <label class="sr-only" for="email">Email address</label>
    <input id="email" type="email" name="email" placeholder="you@anywhere.net" required autocomplete="email">
    <button class="btn btn-solid" type="submit">Join</button>
  </form>
  <p class="fineprint">+ <a href="tip/index.html">spot something we missed? 60-sec tip →</a> ·
    <a href="signal/latest.html">read last friday →</a> · <a href="radar.xml">rss →</a></p>
</section>
</main>
{FOOT.format(root="", sweep=MESSY, motto='BE KIND. REWIND.<br>THERE IS NO RETURN PATH HERE.')}
</body></html>"""


# ------------------------------------------------------------------ images
def img_for(manifest, slug, depth=1):
    """Return local path + credit for a cached editorial image, or None.
    Every image on this site was resolved once through the Wikimedia Commons
    API and cached into img/editorial/ - hotlinking was tested and refused."""
    if not slug:
        return None
    r = root(depth)
    it = next((i for i in manifest.get("items", []) if i["slug"] == slug), None)
    if not it or not it.get("local"):
        return None
    p = it["local"] if str(it["local"]).startswith("http") else r + it["local"]
    if not (ROOT / it["local"]).exists():
        return None
    src = it.get("src") or {}
    page = src.get("page", "#")
    # `kind` moved OUT of `src` and onto the record when the image claims were
    # corrected, because a human judgement about a picture was sitting in the
    # provenance block and reading as though the source had supplied it. This line
    # was never updated, so `src.get("kind", ...)` matched nothing and every
    # badge on the site fell through to the default: 48 ILLUSTRATION tags and
    # zero EXACT, including for records that are now genuinely exact. The
    # over-disclosure is the safe direction, which is exactly why nothing
    # complained - a stale read path and a conservative default look identical
    # from the outside. Read the record, then fall back to the old location so
    # an older manifest cannot silently lose the distinction.
    kind = it.get("kind") or src.get("kind") or "illustrative"
    return {"path": p,
            "credit": f'{src.get("author", "unknown")} · {src.get("licence", "")}'.strip(" ·"),
            "page": page, "caption": it.get("caption", ""),
            "kind": kind}


def img_aisle(manifest, aisle_id, depth=1):
    """The photograph standing in for a whole section. This is what stops the
    front page being ten gradients: every section has a real photograph of its
    subject matter, resolved once and credited."""
    return img_for(manifest, f"aisle-{aisle_id}", depth)


def fig(manifest, slug, depth=1, cls="", wide=False):
    """A figure: the image, and an honest credit line."""
    f = img_for(manifest, slug, depth)
    if not f:
        return ""
    return (f'<figure class="fig {esc(cls)}">'
            f'<img src="{esc(f["path"])}" alt="{esc(f["caption"])}" loading="lazy">'
            f'<figcaption>{esc(f["caption"])} · '
            f'<a href="{esc(f["page"])}" target="_blank" rel="noopener nofollow noopener">'
            f'{esc(f["credit"])}</a></figcaption></figure>')


def wordmark(size="nav", label=True):
    """The iYi logotype: i-Y-i, the two i's unequal and the Y as the fork.

    Late import for the same reason mascot() does one - the repo root is not on
    sys.path when this module is loaded, only by the time a page is being built.
    See tools/wordmark.py for why this replaced the mascot in the nav."""
    import sys as _s
    if str(ROOT) not in _s.path:
        _s.path.insert(0, str(ROOT))
    import wordmark as _w
    return _w.wordmark(size=size, label=label)


def mascot(size=34, cls="", mood="watch", dark=False):
    """iYi, the brand mark. An eight on its side: also infinity, also two eyes.
    The lobes are the eyes - no head, so the silhouette survives at 3cm.
    See tools/mascot.py for the full expression set and the merch exports."""
    import sys as _s
    if str(ROOT) not in _s.path:
        _s.path.insert(0, str(ROOT))
    import mascot as _m
    return _m.inline(mood, size=size, cls=cls)



def front_copy_edition():
    """The front page's live copy edition, out of data/front_copy.json.

    The masthead's words used to be written into this template, which made them
    impossible to rotate without editing a Python file - and indistinguishable,
    once written, from the counts. The copy is data now: `front_copy.py
    --stamp <date>` sets which edition is live and `build_front` reads it here.

    Falls back to the template's own constants if the file is missing, so a
    fresh clone still builds. A missing key in a live edition is refused rather
    than rendered empty: an empty `<p class="line">` is a hole nobody sees until
    it is on the page.
    """
    import pathlib as _p
    import json as _j
    f = ROOT / "data" / "front_copy.json"
    if not f.exists():
        return {"kicker": "iYi &middot; behind the counter",
"line": ("Keeping you comfortably connected to the worldwide "
                         "one-sided web."),
                 "clerk_line": ("<b>I keep the record.</b> Every claim here "
                               "carries its source, and the ones nobody has "
                               "opened say so. I do not remember you, and "
                               "nothing here pretends to."),
                 "door_stories": ("One a day, each one signed by a person. "
                                  "{total} so far."),
                 "door_encyclopedia": "{nent} entries, every claim cited."}
    d = _j.loads(f.read_text(encoding="utf-8"))
    eds = d.get("editions") or []
    live = d.get("_live") or (eds[-1]["date"] if eds else None)
    ed = next((e for e in eds if e["date"] == live), None)
    if ed is None:
        raise SystemExit(f"data/front_copy.json: live edition {live!r} is not "
                         f"in the file. Run tools/front_copy.py --list")
    # thesis_word / thesis_thing / thesis_pair are gone from this list because
    # the 1956 / -70,000 pair was removed from the page. Leaving them required
    # would make every new edition carry copy that has nowhere to render, and
    # the guard that refuses an empty slot would then refuse an edition for
    # three slots no reader ever sees.
    missing = [k for k in ("kicker", "line", "clerk_line", "door_stories",
                           "door_encyclopedia")
               if not ed.get("copy", {}).get(k)]
    if missing:
        raise SystemExit(f"data/front_copy.json: edition {live} has no value "
                         f"for {missing}. A slot rendered empty is a hole.")
    return ed["copy"]


def rotate(seq, key, n=8, by="rank"):
    """A 'reliably rotating' column: deterministic on the week number, so it
    changes on a schedule and is identical for everybody that week.

    Picks WHICH entries to feature by shuffling, then re-sorts them for display
    so the column always reads 8 -> 5 -> 2 -> 1 rather than in random order.
    Randomising the display order made the numbers look like a bug."""
    if not seq:
        return []
    items = list(range(len(seq)))
    seed = int(hashlib.md5(key.encode()).hexdigest()[:8], 16)
    for i in range(len(items) - 1, 0, -1):
        seed = (seed * 1103515245 + 12345) & 0x7FFFFFFF
        j = seed % (i + 1)
        items[i], items[j] = items[j], items[i]
    picked = [seq[i] for i in items[:min(n, len(seq))]]
    if by and all(by in x for x in picked):
        picked.sort(key=lambda x: x[by])
    return picked


# ------------------------------------------------------------------ top 8
TOP8_SLOTS = 8


def top8_window(feat, today=None):
    """The eight moments the site shows today, chosen from the eligible pool.

    Shared by build_front and build_top8. They each derived their own list
    before, and they disagreed: the front page applied the stage filter and the
    date rotation, while build_top8 took the raw pool - so /top8/ rendered
    every entry including `candidate` ones, which is exactly what the candidate
    stage exists to keep off the page. Two copies of "which eight" is the
    `kind: exact` class: one of them is wrong and nothing notices.

    The list itself is today's show, chosen through show_list() - the live
    lists take turns one per UTC day, anchored on the newest release - so the
    front page and /top8/ cannot name different ones.     Above eight eligible
    moments in a list, the eight also rotate on a fixed cycle rather than by
    hash - a hash reshuffles all eight whenever the pool grows, which reads as
    churn, and two consecutive days must never repeat the same page. The cycle
    advances once per SHOWING of that list, not once per calendar day: the
    live lists take turns, so each one is on show every k-th day, and a stride
    measured in calendar days returns to the same window every time that list's
    day comes round - with two lists and sixteen moments, (day * 8) % 16 is
    constant for each list, which would have looked exactly like rotation while
    showing the same eight every time. Counting the showings is what makes the
    pool grow mean something.

    `today` is an ISO date and overrides the UTC clock, so record_top8_day()
    can be exercised across days; production callers omit it.
    """
    lists = feat.get("lists") or []
    if not lists:
        return {"title": "", "kicker": "", "dek": "", "standfirst": "",
                "entries": []}
    # One date, read once: show_list and the window below must agree about
    # which day it is, and two separate clock reads can straddle midnight.
    iso = (str(today)[:10] if today else
           datetime.datetime.now(datetime.timezone.utc).date().isoformat())
    # show_list hands back the list's own dict with every key intact - image,
    # law, slug and the rest are read by build_top8 as well as the window
    # below, and a refactor that rebuilt the dict field by field once dropped
    # them. That is how /top8/ lost its hero photograph and how .t8-hero-fig
    # img became an orphan rule; the only thing that noticed was the dead-CSS
    # check reporting a selector that matched nothing.
    L = dict(show_list(feat, iso))
    featured = [e for e in L["entries"]
                if e.get("stage", "featured") == "featured"]
    # Rotation is a property of the whole list, so it is measured before the
    # window narrows it, and it rides on L because the front page's kicker
    # asks the same question. One answer, in one place.
    L["rotating"] = len(featured) > TOP8_SLOTS
    if L["rotating"]:
        n = len(featured)
        d = datetime.date.fromisoformat(iso)
        # The count of times this list has been put on show since the newest
        # release, not the calendar day. See the docstring: the lists take
        # turns, so a per-day stride is constant for each list and the window
        # would never move while looking exactly like a rotation. A file with
        # one live list (or no anchor date) keeps the per-day stride, which is
        # the same thing there - the list is on show every day.
        anchor = pick_list(feat, iso).get("released") or ""
        if len(live_lists(feat, iso)) < 2 or not anchor:
            showing = d.toordinal()
        else:
            ordered = sorted(live_lists(feat, iso),
                             key=lambda x: x.get("released") or "",
                             reverse=True)
            index = next(i for i, x in enumerate(ordered)
                         if x.get("slug") == L.get("slug"))
            steps = (d - datetime.date.fromisoformat(str(anchor)[:10])).days
            showing = (steps - index) // len(ordered)
        start = (showing * TOP8_SLOTS) % n
        # a window that wraps, so consecutive days overlap rather than
        # replacing themselves wholesale
        order = sorted(range(n), key=lambda i: (i - start) % n)
        featured = [featured[i] for i in order[:TOP8_SLOTS]]
    if len(featured) < TOP8_SLOTS:
        raise SystemExit(
            f"REFUSING to build: the featured pool holds {len(featured)} "
            f"moment(s) and the page must show {TOP8_SLOTS}. Promote a "
            f"candidate with tools\\t8_pool.py --promote, or restore a moment "
            f"from stage archived/featured.")
    L["entries"] = featured
    return L


# --------------------------------------------------------------- the record
# Which list is on show is a property of the date and is not stored. What is
# stored is which day it happened on, because a date is not recomputable: no
# rebuild can reconstruct a show from a day nobody built on.
TOP8_HISTORY = ROOT / "data" / "top8_history.json"
TOP8_HISTORY_NOTE = (
    "STATEFUL. One record per day: which top-8 list was on show and the eight "
    "moments it carried, appended by build_cards.record_top8_day() and never "
    "rewritten. Do not regenerate this file and do not delete it to clean up "
    "- the sequence of what was on show is the thing it holds, and a rebuild "
    "from scratch cannot reconstruct a day nobody was there for. A day that "
    "tools/archive.py had to close after the fact carries `reconstructed: "
    "true` with the date and input hash that made the recomputation provable, "
    "and the record pages print it as rebuilt rather than observed. Rendered "
    "as the day record on /top8/ by build_cards.t8_record().")


def t8_eid(en):
    """A moment's durable identity in the record, mirroring t8_pool.eid().

    id, then the linked entry, then image, then show - never rank or name,
    which are display fields and move. A generated daily list has no image and
    no stored id, but it always names the encyclopedia entry it is drawn from,
    so `entry` is the identity that survives a rename of the display fields.
    """
    return (en.get("id") or en.get("entry") or en.get("image")
            or en.get("show", "?"))


def t8_anchor(L, en):
    """A stable fragment for one moment on /top8/.

    Derived from the list slug and the moment's name, never from its window
    position: the position changes with the daily window and a fragment that
    moves is not an address. The list slug is part of it so the archive can
    carry two lists with a same-named moment without a duplicate id.
    """
    base = (f"{L.get('slug') or 'top8'}-"
            f"{en.get('name') or en.get('show') or 'moment'}")
    slug = re.sub(r"[^a-z0-9]+", "-", base.lower()).strip("-")
    return f"t8-{slug or 'moment'}"


def t8_year_span(L):
    """The years named by a list's `show` fields, as a range or one year.

    Reads the list as released rather than the eight-entry window, so the
    kicker describes the list and does not change shape as the window moves.
    Returns "" when the data names no four-digit year, rather than guessing.
    """
    years = []
    for en in L.get("entries") or []:
        years.extend(int(y) for y in
                     re.findall(r"(?<!\d)(\d{4})(?!\d)",
                                str(en.get("show") or "")))
    if not years:
        return ""
    lo, hi = min(years), max(years)
    return str(lo) if lo == hi else f"{lo}&ndash;{hi}"


def t8_hook(en, words=24, chars=118):
    """One sentence from `what` that can stand as a card's hook.

    `deck` keeps a first sentence whole even when it is twice the budget, which
    is right for a story teaser and wrong for a card: the Sherlock entry ran to
    46 words and became a paragraph. This prefers the first sentence when it
    fits two lines at the card's measure, otherwise the shortest later sentence
    that does, and falls back to a clause of the first before it is truncated
    mid-phrase. It also balances a quote left open by a split at the question
    mark inside it.
    """
    take = " ".join((en.get("what") or "").split())
    if not take:
        return ""
    sentences = [s.strip() for s in
                 re.split(r'(?<=[.!?][”"\'])\s+|(?<=[.!?])\s+', take)
                 if s.strip()]
    first = sentences[0] if sentences else ""
    if len(first.split()) <= words and len(first) <= chars:
        hook = first
    else:
        short = [s for s in sentences[1:]
                 if 8 <= len(s.split()) <= words and len(s) <= chars]
        if short:
            hook = min(short, key=lambda s: len(s.split()))
        else:
            hook = first
            cut = ""
            for m in re.finditer(r":\s| - |;\s|,\s", first):
                if m.start() > chars:
                    break
                cut = first[:m.start()].rstrip()
            if len(cut.split()) >= 8:
                hook = cut + "."
    if hook.count("“") != hook.count("”"):
        hook = hook.replace("“", "").replace("”", "")
    return hook


def record_top8_day(feat, today=None):
    """Record which list and which eight moments are on show today.

    Called from main() before the pages are written, so the record and the
    render read the same top8_window() and cannot describe different shows.
    The entry is {date, list, items} - the list by slug, the items by the
    identities t8_eid() keeps, because a slug and an id outlive renames of
    the display fields.

    Idempotent within a day: running the build five times appends one record.
    If the selection changes later the same day - a pool edited mid-day - the
    day's entry is replaced rather than duplicated, because one date with two
    shows in it is a record that cannot be read. Across days it is append
    only, never rewritten, and there is deliberately no cap: the whole point
    of the file is that it is the sequence.

    Returns (appended, entry) so the caller can say what happened.
    """
    today = today or datetime.datetime.now(
        datetime.timezone.utc).date().isoformat()
    L = top8_window(feat, today)   # the same window the pages render
    entry = {"date": today, "list": L.get("slug") or "",
             "theme": L.get("theme") or "",
             "items": [t8_eid(en) for en in L["entries"]]}
    hist = (json.loads(TOP8_HISTORY.read_text(encoding="utf-8"))
            if TOP8_HISTORY.exists()
            else {"_note": TOP8_HISTORY_NOTE, "days": []})
    days = hist.setdefault("days", [])
    if days and str(days[-1].get("date")) == today:
        if (days[-1].get("list"), days[-1].get("items"),
                days[-1].get("theme")) == \
                (entry["list"], entry["items"], entry["theme"]):
            return False, days[-1]
        days.pop()
    days.append(entry)
    hist.setdefault("_note", TOP8_HISTORY_NOTE)
    TOP8_HISTORY.parent.mkdir(exist_ok=True)
    TOP8_HISTORY.write_text(
        json.dumps(hist, ensure_ascii=False, indent=1) + "\n",
        encoding="utf-8")
    return True, entry


def _t8_day_before(day_iso, candidate_iso):
    """Whether candidate_iso is the calendar day before day_iso."""
    try:
        a = datetime.date.fromisoformat(candidate_iso)
        b = datetime.date.fromisoformat(day_iso)
    except ValueError:
        return False
    return (b - a).days == 1


def t8_runs(days):
    """The recorded days, newest run first, contiguous same-show days merged.

    A run only grows across days that are actually consecutive: a day with no
    build is a day this record claims nothing about, so a gap breaks the run
    rather than being spanned by it. The record is what happened, not what
    would have been true if somebody had built.
    """
    runs = []
    for d in reversed(days):
        date = str(d.get("date") or "")
        recon = bool(d.get("reconstructed"))
        key = (str(d.get("list") or ""), tuple(d.get("items") or []))
        if runs and runs[-1]["key"] == key and \
                _t8_day_before(runs[-1]["lo"], date):
            runs[-1]["lo"] = date
            runs[-1]["recon"] = runs[-1]["recon"] or recon
        else:
            runs.append({"key": key, "lo": date, "hi": date, "recon": recon})
    return runs


def t8_record(feat, today=None):
    """/top8/'s day record: every day this site chose a show, newest first.

    The show is a property of the date and is not stored; what is stored is
    the day it happened on - data/top8_history.json, written by
    record_top8_day() from the same window() that renders the page. This
    renders that file, so the record and the page cannot disagree.

    Names are resolved from the current data at render time: the record
    stores identities, and a moment's id or image outlives any rename of its
    display fields. A day whose list is missing from the file, or whose
    moments no longer resolve, degrades in place rather than printing a
    slug or an id at a reader.

    Consecutive days with the same selection collapse into one run, but only
    when the days are contiguous - see t8_runs - and the run that includes
    today says so.
    """
    if not TOP8_HISTORY.exists():
        return ""
    hist = json.loads(TOP8_HISTORY.read_text(encoding="utf-8"))
    days = hist.get("days") or []
    if not days:
        return ""
    lists = feat.get("lists") or []
    by_slug = {L.get("slug"): L for L in lists}
    by_eid = {}
    for L in lists:
        for en in L.get("entries") or []:
            for key in ("id", "entry", "image", "show"):
                v = en.get(key)
                if v and v not in by_eid:
                    by_eid[v] = en
    show = show_list(feat, today).get("slug")
    today = today or datetime.datetime.now(
        datetime.timezone.utc).date().isoformat()
    rows = []
    for run in t8_runs(days):
        slug, items = run["key"]
        L = by_slug.get(slug)
        span = (fmt_date(run["lo"]) if run["lo"] == run["hi"]
                else f'{fmt_date(run["lo"])} &rarr; {fmt_date(run["hi"])}')
        if L and L.get("title"):
            href = "#list" if slug == show else \
                f'archive/index.html#{esc(slug)}'
            title = (f'<a class="t8rec-list" href="{href}">'
                     f'{esc(L["title"])}</a>')
        else:
            title = ('<span class="t8rec-list">A list that is no longer in '
                     'the file</span>')
        head = [f'<span class="t8rec-date">{span}</span>', title]
        if L and L.get("kicker"):
            head.append(f'<span class="t8rec-cat">{esc(L["kicker"])}</span>')
        if run.get("recon"):
            head.append(rebuilt_run_tag(run))
        if slug == show and run["hi"] == today:
            head.append('<span class="t8rec-now">on show today</span>')
        names = [by_eid[v].get("name") for v in items
                 if v in by_eid and by_eid[v].get("name")]
        names_p = ('<p class="t8rec-names">'
                   + " &middot; ".join(esc(n) for n in names) + '</p>'
                   ) if names else ""
        rows.append(f'<li class="t8rec-run">'
                    f'<p class="t8rec-head">{" ".join(head)}</p>'
                    f'{names_p}</li>')
    if not rows:
        return ""
    return f'<ol class="t8rec">{"".join(rows)}</ol>'


def t8_entry(en, i, laws, manifest, depth, one_law, anchor=""):
    """One moment of a top-8 list, as markup. Shared by /top8/ and the archive.

    A former list renders exactly what it rendered the day it was on show -
    the entry's own words, its law, and its photograph when one is sourced -
    so archiving is a change of address rather than an edit. The numeral is
    the position on the page, taken at render time: a stored rank describes
    the pool it was written for, and a promoted candidate carries none at all.
    """
    law = laws.get(en.get("law"), {})
    f = img_for(manifest, en.get("image"), depth)
    if f:
        im = (f'<figure class="t8-fig"><img src="{esc(f["path"])}" alt="" loading="lazy">'
              f'<figcaption>{esc(f["caption"])} &middot; '
              f'<a href="{esc(f["page"])}" target="_blank" rel="noopener nofollow">'
              f'{esc(f["credit"])}</a></figcaption></figure>')
    else:
        im = ""
    _id = f' id="{esc(anchor)}"' if anchor else ""
    _entry = (f'<p class="t8-read"><a href="{root(depth)}encyclopedia/'
              f'{esc(en["entry"])}.html">Read the entry &rarr;</a></p>'
              if en.get("entry") else "")
    return f"""<li class="t8-item"{_id} data-rank="{i}">
  <div class="t8-head">
    <span class="t8-rank">{i}</span>
    {im}
    <div class="t8-titles">
      <h3>{esc(en['name'])}</h3>
      <p class="t8-show">{esc(en['show'])}</p>
      <a class="t8-law" href="{root(depth)}history/index.html#law-{esc(en.get('law',1))}">LAW {esc(en.get('law',1))} &middot; {esc(law.get('title',''))}</a>
    </div>
  </div>
  <p class="t8-what"><b>What happens.</b> {esc(en['what'])}</p>
  <p class="t8-why"><b>Why it is on the list.</b> {esc(en['why'])}</p>
  {_entry}
</li>"""


def t8_shared_law(one_law, laws):
    """The list's one law, stated once, when the whole list shares it.

    A list whose entries are all instances of one law says so once above the
    list, rather than repeating the same label eight times.
    """
    if one_law is None:
        return ""
    l = laws.get(one_law, {})
    return (f'<p class="t8-sharedlaw"><span class="t8-sharedlaw-n">'
            f'LAW {esc(one_law)}</span> Every entry here is an instance of '
            f'<b>{esc(l.get("title", ""))}</b>, which is the reason they are '
            f'on one list.</p>')


def t8_frame_note(L, entries, manifest):
    """The list's own note above the list, rendered from its data, counted.

    Optional per list, and it lives in the data rather than in the renderer:
    the previous version was hardcoded and claimed that every picture in a set
    of six was of the audience, which three of them were not - all six were
    opened to check it, and the sentence survived its own correction because
    the fix left it in the template. Part one carries one; Part two has no
    photographs at all, so a note about frames would be a note about nothing.

    The note carries two tokens, {blank} and {total}, filled from `entries` -
    the set the caller is actually rendering, which is the eight the window
    put on /top8/ or the whole pool in the archive. They exist because the
    first version typed the count ("Two of the eight have no photograph at
    all") and the pool grew underneath it: a number inside a paragraph is not
    obviously a claim, which is what makes it the dangerous kind. The test
    for a blank is the same one t8_entry renders the plate from, so the
    sentence and the plates cannot describe different sets.
    """
    body = (L.get("frame_note") or "").strip()
    if not body:
        return ""
    if "{blank}" in body or "{total}" in body:
        n_blank = sum(1 for en in entries
                      if not img_for(manifest, en.get("image"), 1))
        body = (body.replace("{blank}", str(n_blank))
                    .replace("{total}", str(len(entries))))
    paras = "".join(f"<p>{emph(p)}</p>" for p in body.split("\n\n")
                    if p.strip())
    return ('<aside class="t8-frame">\n  <p class="kicker">Read this '
            f'before the list</p>\n  {paras}\n</aside>')


def build_top8(data, feat, manifest):
    r = root(1)
    L = top8_window(feat)
    # The outro used to promise "rotated weekly", which is a promise about a
    # schedule the build does not keep. The rotation now is the lists
    # themselves, one per UTC day through show_list - so what is true to say
    # is that the lists not on show today are in the archive. "Earlier" went
    # with the old wording: the lists that are not up today are not
    # necessarily older, they are the ones this day did not land on.
    outro = ('The lists not on show today are in the '
             '<a href="archive/index.html">archive</a>.'
             if len(live_lists(feat)) > 1 else "More top 8s to come.")
    laws = {l["n"]: l for l in data["laws"]}

    # When the whole list shares one law - which is the point of Part one
    # rather than a tagging accident - the law is stated once above the list.
    shared = {en.get("law") for en in L["entries"]}
    one_law = next(iter(shared)) if len(shared) == 1 else None
    anchors = [t8_anchor(L, en) for en in L["entries"]]
    if len(set(anchors)) != len(anchors):
        raise SystemExit("REFUSING to build: two top-8 moments share an anchor")
    items = "".join(t8_entry(en, i, laws, manifest, 1, one_law,
                             anchor=t8_anchor(L, en))
                    for i, en in enumerate(L["entries"], 1))

    shared_law = t8_shared_law(one_law, laws)
    frame_note = t8_frame_note(L, L["entries"], manifest)
    news_html = ""
    if L.get("news"):
        rows = "".join(
            f'<li><a href="{esc(n.get("url"))}" target="_blank" '
            f'rel="noopener">{esc(n.get("title"))}</a>'
            + (f' <span>{esc(n.get("publisher"))}</span>' if n.get("publisher") else "")
            + '</li>'
            for n in L["news"][:3])
        news_html = (f'<div class="t8-wires"><p class="kicker">From today\'s '
                     f'wires</p><ul>{rows}</ul></div>')
    # The day record, under the list. Absent on a first build (nothing
    # recorded yet) and rendered from data/top8_history.json otherwise - see
    # t8_record for why the dates are stored rather than recomputed.
    record = t8_record(feat)
    record_html = f"""
<section class="section" id="record" style="padding-top:8px">
  <p class="kicker">The record</p>
  <h2 style="font-family:var(--serif);font-size:clamp(1.6rem,4vw,2.6rem);font-weight:900;
     letter-spacing:-.03em;line-height:1.05;margin:0 0 14px;max-width:24ch">Every day, one new list</h2>
  <p class="sec-lede" style="max-width:62ch">One list is released each UTC day and
  that day's list takes this page. Every earlier list is in the <a
  href="archive/index.html">archive</a> and is never shown again. This is what was
  on show, recorded as it happened; the <a href="record/index.html">whole
  record</a> is one line per day.</p>
  {record}
</section>""" if record else ""
    return f"""<!DOCTYPE html>
<html lang="en"><head><meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{esc(L['title'])} — Parasocialize</title>
<meta name="description" content="{esc(L['dek'])}">
{HEAD.format(site=SITE, path="/top8/", otype="website",
             title=esc(L['title']), desc=esc(L['dek']), root=root(1))}
</head>
<body>
<a class="skip" href="#list">Skip to the list</a>
<div class="grain" aria-hidden="true"></div>
{NAV.format(root=root(1), total=len(data['cards']), mk=wordmark("nav"))}
<main>
<section class="section" style="padding-bottom:20px">
  <p class="kicker">{esc(L['kicker'])} · the top 8</p>
  <h1 style="font-family:var(--serif);font-size:clamp(2rem,5.4vw,3.6rem);font-weight:900;
     letter-spacing:-.03em;line-height:1.02;margin:0 0 16px;max-width:22ch">{esc(L['title'])}</h1>
  <p class="sec-lede" style="max-width:62ch;font-size:1.1rem">{esc(L['dek'])}</p>
  <div class="note" style="margin-top:26px"><p>{esc(L['standfirst'])}</p></div>
  {frame_note}
  {news_html}
  <p style="margin-top:30px;max-width:62ch"><a class="btn btn-solid" href="../quiz/index.html">Which of these are you?</a>
  <span style="font-size:.92rem;color:var(--dim)">&nbsp;Eight questions, and the answers are people in the
  <a href="../atlas/index.html" style="color:var(--hot)">catalogue</a> rather than personality types.</span></p>
</section>

<section class="section" id="list" style="padding-top:8px">
  {shared_law}
  <ol class="t8">{''.join(items)}</ol>
  <p class="countline" style="margin-top:30px">{outro}
  <a href="{r}index.html">Back to the ten sections →</a></p>
</section>
{record_html}
</main>
    {FOOT.format(root=root(1), sweep=MESSY, motto='TEN TO CALL IT A LIST.<br>ONE TO MAKE THE CASE.')}
</body></html>"""


def build_top8_archive(data, feat, manifest):
    """Every top-8 list that is not today's show, rendered in full, newest first.

    The show is today's pick in the daily rotation (show_list), so a list
    lands on this page by the calendar rather than by an edit: it is still in
    data/features.json exactly as it shipped, and this page renders it with
    the same entry renderer the show page uses. An archive that prints a
    different version of the thing than the one that ran is a second,
    conflicting record of it, so there is deliberately no trimmed or
    summarised mode here.

    A list dated in the future is neither the show nor archived - it is not
    live yet, so it is not anywhere on the site.
    """
    r = root(2)
    laws = {l["n"]: l for l in data["laws"]}
    show = show_list(feat)
    former = sorted((L for L in live_lists(feat)
                     if L.get("slug") != show.get("slug")),
                    key=lambda L: L.get("released") or "", reverse=True)

    chunks = []
    for L in former:
        # Only `featured` entries are ever rendered: `candidate` is the stage
        # that keeps a moment off the page until its list ships, and the
        # archive is a page.
        entries = [en for en in L["entries"]
                   if en.get("stage", "featured") == "featured"]
        shared = {en.get("law") for en in entries}
        one_law = next(iter(shared)) if len(shared) == 1 else None
        anchors = [t8_anchor(L, en) for en in entries]
        if len(set(anchors)) != len(anchors):
            raise SystemExit("REFUSING to build: two archive moments share an anchor")
        items = "".join(t8_entry(en, i, laws, manifest, 2, one_law,
                                 anchor=t8_anchor(L, en))
                        for i, en in enumerate(entries, 1))
        chunks.append(f"""<section class="section" id="{esc(L['slug'])}">
  <p class="kicker">{esc(L['kicker'])} &middot; the top 8</p>
  <h2 style="font-family:var(--serif);font-size:clamp(1.6rem,4vw,2.6rem);font-weight:900;
     letter-spacing:-.03em;line-height:1.05;margin:0 0 14px;max-width:24ch">{esc(L['title'])}</h2>
  <p class="sec-lede" style="max-width:62ch">{esc(L['dek'])}</p>
  <div class="note" style="margin-top:24px"><p>{esc(L['standfirst'])}</p></div>
  {t8_frame_note(L, entries, manifest)}
  {t8_shared_law(one_law, laws)}
  <ol class="t8">{items}</ol>
</section>""")

    if not chunks:
        chunks.append("""<section class="section">
  <p class="sec-lede" style="max-width:62ch">Nothing is put aside yet - one list
  is live, so it is also the one always on show, and this page fills in when a
  second list is dated. From then on the lists not on show that day sit
  here.</p>
</section>""")

    return f"""<!DOCTYPE html>
<html lang="en"><head><meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Top 8 archive — Parasocialize</title>
<meta name="description" content="Every top 8 this site has run, in full, newest first.">
{HEAD.format(site=SITE, path="/top8/archive/", otype="website",
             title="Top 8 archive",
             desc="Every top 8 this site has run, in full, newest first.",
             root=root(2))}
</head>
<body>
<a class="skip" href="#lists">Skip to the lists</a>
<div class="grain" aria-hidden="true"></div>
{NAV.format(root=root(2), total=len(data['cards']), mk=wordmark("nav"))}
<main id="lists">
<section class="section" style="padding-bottom:6px">
  <p class="kicker">The top 8 &middot; archive</p>
  <h1 style="font-family:var(--serif);font-size:clamp(2rem,5.4vw,3.6rem);font-weight:900;
     letter-spacing:-.03em;line-height:1.02;margin:0 0 16px;max-width:22ch">Every top 8 this site has run</h1>
  <p class="sec-lede" style="max-width:62ch;font-size:1.1rem">A list that is not
  up today is not trimmed or summarised here - it is the list exactly as it was
  on show. The one on show now is at <a href="../index.html" style="color:var(--hot)">the
  top 8</a>.</p>
</section>
{''.join(chunks)}
<section class="section" style="padding-top:8px">
  <p class="countline">The lists here are kept exactly as they shipped.
  <a href="{r}index.html">Back to the ten sections →</a></p>
</section>
</main>
{FOOT.format(root=root(2), sweep=MESSY, motto='TEN TO CALL IT A LIST.<br>ONE TO MAKE THE CASE.')}
</body></html>"""


def build_top8_record(data, feat, manifest):
    """The day-by-day record, at full length, as a page of its own.

    /top8/ folds the record into runs under the list, because there the reader
    wants the shape of what happened. This page is the other reading: one line
    per recorded day, newest first, with the eight it carried - rendered from
    data/top8_history.json exactly as record_top8_day() wrote it, so the page
    and the list cannot describe different shows. Nothing is filled in for a
    day with no record: the sequence is what happened, and a gap stays a gap.
    Names resolve from the current data at render time, the same way /top8/
    resolves them, and a list or a moment that is no longer in the file
    degrades in place rather than printing a slug at a reader.
    """
    days = []
    if TOP8_HISTORY.exists():
        try:
            days = (json.loads(TOP8_HISTORY.read_text(encoding="utf-8"))
                    .get("days") or [])
        except ValueError:
            days = []
    lists = feat.get("lists") or []
    by_slug = {L.get("slug"): L for L in lists}
    by_eid = {}
    for L in lists:
        for en in L.get("entries") or []:
            for key in ("id", "entry", "image", "show"):
                v = en.get(key)
                if v and v not in by_eid:
                    by_eid[v] = en
    show = show_list(feat).get("slug")
    today = datetime.datetime.now(datetime.timezone.utc).date().isoformat()
    rows = []
    for d in reversed(days):
        date = str(d.get("date") or "")
        slug = str(d.get("list") or "")
        L = by_slug.get(slug)
        if L and L.get("title"):
            href = ("../index.html#list" if slug == show
                    else f'../archive/index.html#{esc(slug)}')
            title = (f'<a class="t8rec-list" href="{href}">'
                     f'{esc(L["title"])}</a>')
        else:
            title = ('<span class="t8rec-list">A list that is no longer in '
                     'the file</span>')
        head = [f'<span class="t8rec-date">{fmt_date(date)}</span>', title]
        if L and L.get("kicker"):
            head.append(f'<span class="t8rec-cat">{esc(L["kicker"])}</span>')
        if slug and slug == show and date == today:
            head.append('<span class="t8rec-now">on show today</span>')
        if d.get("reconstructed"):
            head.append(rebuilt_tag(d))
        names = [by_eid[v].get("name") for v in (d.get("items") or [])
                 if v in by_eid and by_eid[v].get("name")]
        names_p = ('<p class="t8rec-names">'
                   + " &middot; ".join(esc(n) for n in names) + '</p>'
                   ) if names else ""
        rows.append(f'<li class="t8rec-run">'
                    f'<p class="t8rec-head">{" ".join(head)}</p>'
                    f'{names_p}</li>')
    if rows:
        body = f'<ol class="t8rec">{"".join(rows)}</ol>'
    else:
        body = ('<p class="sec-lede" style="max-width:62ch">Nothing has been '
                'recorded yet. The record begins the first day a list is on '
                'show, and after that each day is appended as it happens '
                'rather than reconstructed.</p>')
    count = len(days)
    day_count = f"{count} day" + ("" if count == 1 else "s")
    return f"""<!DOCTYPE html>
<html lang="en"><head><meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>The top 8 record — Parasocialize</title>
<meta name="description" content="Every day this site has chosen a top 8, one line per day, with the eight it carried.">
{HEAD.format(site=SITE, path="/top8/record/", otype="website",
             title="The top 8 record",
             desc="Every day this site has chosen a top 8, one line per day.",
             root=root(2))}
</head>
<body>
<a class="skip" href="#record">Skip to the record</a>
<div class="grain" aria-hidden="true"></div>
{NAV.format(root=root(2), total=len(data['cards']), mk=wordmark("nav"))}
<main id="record">
<section class="section" style="padding-bottom:6px">
  <p class="kicker">The top 8 &middot; record &middot; {day_count} recorded</p>
  <h1 style="font-family:var(--serif);font-size:clamp(2rem,5.4vw,3.6rem);font-weight:900;
     letter-spacing:-.03em;line-height:1.02;margin:0 0 16px;max-width:22ch">Every day, one of the lists</h1>
  <p class="sec-lede" style="max-width:62ch;font-size:1.1rem">The show is decided
  by the date rather than by hand: the newest list takes the page on its release
  day, and from there the live lists take turns, one per UTC day. This is that
  sequence, one line per day, with the eight it carried.</p>
</section>
<section class="section" style="padding-top:8px">
  {body}
  <p class="countline" style="margin-top:30px">A day with no line is a day with
  no record rather than a day rebuilt after the fact.
  <a href="../index.html">Today's list →</a></p>
</section>
</main>
{FOOT.format(root=root(2), sweep=MESSY, motto='TEN TO CALL IT A LIST.<br>ONE TO MAKE THE CASE.')}
</body></html>"""


# ------------------------------------------------------------------ history
def build_history(data, hist, manifest):
    r = root(1)
    laws = {l["n"]: l for l in data["laws"]}

    mod_bar = "".join(
        f'<a class="hlaw" href="#m{esc(m["n"])}"><b>{esc(m["n"])}</b>'
        f'<span>{esc(m["title"])}<i class="hlaw-y">{esc(m["years"])}</i></span></a>'
        for m in hist["modules"])

    mods = []
    for m in hist["modules"]:
        f = img_for(manifest, m.get("figure"), 1)
        im = (f'<figure class="fig h-fig"><img src="{esc(f["path"])}" alt="{esc(f["caption"])}" loading="lazy">'
              f'<figcaption>{esc(f["caption"])} · '
              f'<a href="{esc(f["page"])}" target="_blank" rel="noopener">'
              f'{esc(f["credit"])}</a></figcaption></figure>') if f else ""
        body = "".join(f"<p>{esc(p)}</p>" for p in m["body"])
        cite = (f'<p class="h-cite">This module is law {esc(m.get("law"))} · '
                f'<a href="#law-{esc(m.get("law"))}">{esc(laws.get(m.get("law"),{}).get("title",""))}</a>'
                f'</p>') if m.get("law") else ""
        mods.append(f"""<article class="hmod" id="m{esc(m['n'])}">
  <header class="hmod-head">
    <span class="hmod-n">{esc(m['n'])}</span>
    <div class="hmod-titles">
      <p class="hmod-years">{esc(m['years'])}</p>
      <h2>{esc(m['title'])}</h2>
      <p class="hmod-claim">{esc(m['claim'])}</p>
    </div>
  </header>
  {f'<div class="hmod-prose">{body}{cite}</div>'}
  {im}
</article>""")

    laws_html = []
    for l in hist["laws"]:
        laws_html.append(f"""<div class="hlaw-card" id="law-{esc(l['n'])}">
  <span class="hlaw-n">{esc(l['n'])}</span>
  <div><h3>{esc(l['title'])}</h3><p>{esc(l['one'])}</p></div>
</div>""")

    return f"""<!DOCTYPE html>
<html lang="en"><head><meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>The history of parasocial relationships — a course — Parasocialize</title>
<meta name="description" content="Eight modules, from Pygmalion to a 2023 policy update. The complete history of one-sided attachment, free to read and free to print.">
{HEAD.format(site=SITE, path="/history/", otype="website",
             title="The history of parasocial relationships - a course",
             desc="Eight modules, from Pygmalion to a 2023 policy update. Free and complete.",
             root=root(1))}
</head>
<body>
<a class="skip" href="#course">Skip to the course</a>
<div class="grain" aria-hidden="true"></div>
{NAV.format(root=root(1), total=len(data['cards']), mk=wordmark("nav"))}
<main>
<section class="section" style="padding-bottom:24px">
  <p class="kicker">A course in eight modules · free · printable</p>
  <h1 class="h-title">The history of feeling things at people who can't feel it back</h1>
  <p class="sec-lede" style="font-size:1.12rem;max-width:64ch">{esc(hist['intro'])}</p>
  <p class="countline">Ctrl/Cmd+P to print the whole thing. It is a course, not a blog post — modules, claims, evidence.</p>
  <div class="h-outline">{mod_bar}</div>
</section>

<section class="section" id="course" style="padding-top:0">
  {''.join(mods)}
</section>

<section class="section" style="padding-top:0">
  <p class="kicker">The seven laws, which is what all of this adds up to</p>
  <div class="sec-head"><h2>Eight modules, seven patterns, one method.</h2>
  <p class="sec-lede">The history tells you where the feeling came from. The laws tell you what to do about it
  now, which is a different job and the more useful one. Notice, name, choose.</p></div>
  <div class="h-laws">{''.join(laws_html)}</div>
  <p class="countline" style="margin-top:26px">The full versions, with the worksheet, are in
  <a href="{r}classroom/index.html">the classroom</a>.</p>
</section>
</main>
{FOOT.format(root=root(1), sweep=MESSY, motto='SIX HUNDRED YEARS, EIGHT MODULES,<br>ONE UNCOMFORTABLE QUESTION.')}
</body></html>"""


# ------------------------------------------------------------------ figures + moments
def build_figures(data, feat, manifest):
    r = root(1)
    figs = []
    for f in feat["figures"]:
        figs.append(f"""<article class="fcard">
  <p class="fcard-when">{esc(f['when'])}</p>
  <h3>{esc(f['name'])}</h3>
  <p class="fcard-lane">{esc(f['lane'].upper())}</p>
  <p class="fcard-what">{esc(f['what'])}</p>
</article>""")
    return f"""<!DOCTYPE html>
<html lang="en"><head><meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Figures in the parasocial sphere — Parasocialize</title>
<meta name="description" content="The people and characters who hold the parasocial sphere: from Pygmalion to a Twitch emote.">
{HEAD.format(site=SITE, path="/figures/", otype="website",
             title="Figures in the parasocial sphere",
             desc="From Pygmalion to a Twitch emote.", root=root(1))}
</head>
<body>
<a class="skip" href="#f">Skip to the figures</a>
<div class="grain" aria-hidden="true"></div>
{NAV.format(root=root(1), total=len(data['cards']), mk=wordmark("nav"))}
<main>
<section class="section" id="f">
  <p class="kicker">Figures · the people holding the sphere</p>
  <h1 class="h-title" style="font-size:clamp(1.9rem,4.6vw,3rem)">Who does the holding</h1>
  <p class="sec-lede" style="max-width:60ch">Every parasocial bond needs something on the other end, whether or
  not it can hold anything back. These are the ones that keep turning up, from a sculptor to a face on a webcam.</p>
  <div class="fcards" style="margin-top:28px">{''.join(figs)}</div>
  <p class="countline" style="margin-top:28px">Want the argument for the whole thing?
  <a href="{r}history/index.html">The history course →</a> · <a href="{r}index.html">The ten sections →</a></p>
</section>
</main>
{FOOT.format(root=root(1), sweep=MESSY, motto='ONE-SIDED.<br>NOTHING HAS CHANGED SINCE 600 BC.')}
</body></html>"""


def build_moments(data, feat, manifest):
    r = root(1)
    ms = []
    for m in feat["moments"]:
        f = img_for(manifest, m.get("image"), 1)
        im = (f'<img src="{esc(f["path"])}" alt="{esc(f["caption"])}" loading="lazy">' if f else "")
        ms.append(f"""<article class="moment" id="{esc(m['slug'])}">
  {f'<div class="moment-art">{im}</div>' if im else ''}
  <div class="moment-body">
    <p class="moment-meta"><span class="moment-year">{esc(m['year'])}</span>
      <span class="moment-dom">{esc(m['domain'].upper())}</span></p>
    <h3>{esc(m['title'])}</h3>
    <p class="moment-what">{esc(m['what'])}</p>
    {f'<p class="moment-credit">Image: <a href="{esc(f["page"])}" target="_blank" rel="noopener">{esc(f["credit"])}</a></p>' if f else ''}
  </div>
</article>""")
    return f"""<!DOCTYPE html>
<html lang="en"><head><meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Featured parasocial moments — Parasocialize</title>
<meta name="description" content="The significant parasocial moments across news, television, music, games, internet and AI.">
{HEAD.format(site=SITE, path="/moments/", otype="website",
             title="Featured parasocial moments",
             desc="The significant moments, across every domain.", root=root(1))}
</head>
<body>
<a class="skip" href="#m">Skip to the moments</a>
<div class="grain" aria-hidden="true"></div>
{NAV.format(root=root(1), total=len(data['cards']), mk=wordmark("nav"))}
<main>
<section class="section" id="m">
  <p class="kicker">Moments · the ones that changed the shape of it</p>
  <h1 class="h-title" style="font-size:clamp(1.9rem,4.6vw,3rem)">The moments that moved it</h1>
  <p class="sec-lede" style="max-width:60ch">Not the news — the news is ten sections away. These are the
  parasocial events that changed what the thing was, across television, music, the internet, games and AI.</p>
  <div class="moments" style="margin-top:28px">{''.join(ms)}</div>
  <p class="countline" style="margin-top:28px">Still a Saturday morning problem?
  <a href="{r}top8/index.html">Top 8 in 90s cartoons →</a></p>
</section>
</main>
{FOOT.format(root=root(1), sweep=MESSY, motto='THE FEELING IS OLD.<br>THE SCALE IS NOT.')}
</body></html>"""


def build_brand(data, feat):
    """The mascot page. A 30px mark in a masthead is not somewhere anybody
    reviews a character, so here it is at size, with the expressions and the
    lore."""
    moods = [("watch", "The default. iYi looking back at you, which is the whole "
                       "premise: the eyes belong to the audience."),
             ("hollow", "Nobody home. The one-sided joke, and the thesis of the site "
                        "in one expression."),
             ("wink", "For pull quotes and the Friday email."),
             ("sad", "Grief. Used on the obituary cards and the grief section."),
             ("love", "The club. Heart eyes, for when somebody has told you which "
                      "section they are in."),
              ("panic", "Wide eyes. Held back for the day the site has to admit "
                        "something is wrong."),
              ("clerk", "Behind the counter. iYi in the nametag."),
              ("asleep", "Eyes shut, for the long stretches when there is nothing "
                         "new. Which is most of them.")]
    cards = "".join(
        f'<figure class="mood"><div class="mood-art">{mascot(120, "", m)}</div>'
        f'<figcaption><b>{m}</b><span>{note}</span></figcaption></figure>'
        for m, note in moods)
    return f"""<!DOCTYPE html>
<html lang="en"><head><meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>iYi - the mascot - Parasocialize</title>
<meta name="description" content="iYi is an eight lying on its side, which is also infinity, which is also two eyes. The brand mark of Parasocialize.">
{HEAD.format(site=SITE, path="/brand/", otype="website",
             title="iYi - the Parasocialize mascot",
             desc="An eight on its side: also infinity, also two eyes.", root=root(1))}
</head>
<body>
<a class="skip" href="#moods">Skip to the expressions</a>
<div class="grain" aria-hidden="true"></div>
{NAV.format(root=root(1), total=len(data['cards']), mk=wordmark("nav"))}
<main>
<section class="section" style="text-align:center">
  <div style="display:flex;justify-content:center;margin:10px 0 22px">{mascot(200, 'mascot-hero')}</div>
  <h1 class="h-title" style="font-size:clamp(2.4rem,7vw,4.4rem);margin:0 auto 14px">iYi</h1>
  <p class="sec-lede" style="margin:0 auto;max-width:54ch">An eight lying on its side.
  Which is also infinity. Which is also two eyes. The lobes <em>are</em> the eyes —
  there is no head and no face, the whole glyph is doing the work, which is why it
  still reads at three centimetres on a shirt.</p>
</section>

<section class="section" style="padding-top:0">
  <div class="note" style="max-width:64ch;margin:0 auto">
    <p><b>The eyes are the audience.</b> iYi watches somebody who does not know iYi
    is there, which is the entire premise, so the mascot is not a decoration — it is
    the reader, caught in the act. The joke and the argument are the same thing.</p>
    <p><b>The name is the drawing.</b> i-Y-i. Two lowercase i for the two
    selves, the left one fully present and the right one smaller and dimmer,
    with a Y between them for the fork where the two sides diverge. The dots on
    the i's are the catchlights. It says iYi because it sounds like somebody you
    know rather than something you are sold, which is the point, because a
    parasocial relationship is with somebody who feels like a friend.</p>
  </div>
</section>

<section class="section" id="moods" style="padding-top:0">
  <p class="kicker">Eight expressions</p>
  <div class="sec-head"><h2>One silhouette, so it reads as one character.</h2>
  <p class="sec-lede">The two lobes are identical in every expression. That is the
  constraint that makes it a character and not a set of stickers — you know it is
  iYi at postage-stamp size because the shape never changes, only the face.</p></div>
  <div class="moods" style="margin-top:26px">{cards}</div>
</section>

<section class="section" style="padding-top:0">
  <p class="kicker">The lore, if you want it</p>
  <div class="note" style="max-width:64ch">
    <p>iYi watched a character who was never real for thirty years. One day the
    character was retired from the show. Nobody told iYi. iYi found out the way
    everybody finds out.</p>
    <p style="margin-top:14px">That is the origin, it is genuinely the thesis of
    this site, and it leaves about forty years of adventures in it. It is also the
    most useful thing about a mascot: it is not a decoration on the brand, it is
    the brand's argument with a face on it.</p>
  </div>
  <p class="countline" style="margin-top:22px">Merch files — every expression as
  clean vector, plus single-colour flat versions for stamps and vinyl — are in
  <b>img/mascot/</b>. Regenerate with <b>python tools/mascot.py --sheet</b>.</p>
</section>
</main>
{FOOT.format(root=root(1), sweep=MESSY, motto='AN EIGHT ON ITS SIDE.<br>THAT IS THE WHOLE BRAND.')}
</body></html>"""


# ------------------------------------------------------------------ encyclopedia
# Undated is a real state in this catalogue, not a missing value: a support
# culture or a practice like fanfic has no start date. `year: None` therefore
# has to sort, and the old `.get("year", 0)` only ever defaulted when the key was
# absent, so the first undated figure added to the graph took the whole build
# down with a TypeError. Undated entries sort last, which is also the honest
# presentation: put them where they are not pretending to be early.
UNDATED = 10 ** 9


def _y(e):
    """Sort key for a year that may be None."""
    if isinstance(e, dict):
        y = e.get("year")
    else:
        y = e
    return UNDATED if y is None else y


def _era_key(e):
    return _y(e)


# ------------------------------------------------------------------ taxonomy
# --------------------------------------------------- the register of the day
#
# A register is a definition and not a shelf: data/taxonomy.json's register
# list has no `members` key, no placement carries a register value, and the
# entry schema has no field for one - a field nothing counts is this project's
# own "promises more than it keeps" family. So the one editorial action that
# does not need the membership question answered is the day: the eight
# registers take turns, one per UTC day, and the page puts the day's one
# forward as itself - its definition, its anchor when it has one, and the
# search that finds every entry whose own prose mentions it (the search route
# is what item 73 of AGENTS.md sanctions, and _register_check asserts it).
#
# The membership question was measured before this was built, because "which
# entries are in register X" is the natural thing to want and it was worth
# knowing whether the corpus could answer it. Grepping placement reasons and
# entry prose for each register's name: `bond` 26 hits and 0 register
# assertions (all ordinary bond-talk - the site's own subject word);
# `encounter` 1 hit and 0 assertions; `contest` 4 hits of which 2 are real
# ("contestable" and literal contests inflated the rest); `harm` 4 plausible
# and none explicit; `cog` and `reciprocal-edge` and `archive` mostly real
# because their names are technical. A member list built by word matching
# would file generic sentences under a register, which is how a register
# becomes confident noise. The search hands the reader the set and says what
# it is.
REGISTER_HISTORY = ROOT / "data" / "register_history.json"
REGISTER_HISTORY_NOTE = (
    "STATEFUL. One record per UTC day: which register was put forward on "
    "/taxonomy/, appended by build_cards.record_register_day() and never "
    "rewritten. Do not regenerate this file and do not delete it to clean up - "
    "the rotation is recomputable from the date and the register order, and "
    "that recomputability is exactly why the file exists: if either changes, "
    "only this sequence shows what the page actually said. A day that "
    "tools/archive.py had to close after the fact carries `reconstructed: "
    "true` with the date and input hash that made the recomputation provable, "
    "and the record pages print it as rebuilt rather than observed. Rendered "
    "under the register list by build_cards.register_record()."
)
# The day the rotation shipped. The registers have no release dates to anchor
# on the way the top-8 lists do, so the anchor is the day this went live;
# dates before it cycle backward through the same order and are not claimed
# to have shown anything.
REGISTER_EPOCH = datetime.date(2026, 10, 19)


def register_of_day(tax, today=None):
    """The register the taxonomy page puts forward on a given UTC day.

    One register per UTC day, taking turns in the order they are defined in
    data/taxonomy.json, anchored on REGISTER_EPOCH. Deterministic and
    stateless: the same date always gives the same register, which is what
    lets the record and the page be checked against each other. Python's
    modulo makes dates before the epoch cycle backward rather than error.
    """
    regs = tax.get("register") or []
    if not regs:
        return None
    iso = today or datetime.datetime.now(datetime.timezone.utc).date().isoformat()
    try:
        d = datetime.date.fromisoformat(str(iso)[:10])
    except ValueError:
        d = datetime.datetime.now(datetime.timezone.utc).date()
    return regs[(d - REGISTER_EPOCH).days % len(regs)]


def record_register_day(tax=None, today=None):
    """Append today's register to data/register_history.json.

    Called before /taxonomy/ renders - the ledger's snapshot-before-feed
    ordering, the same reason record_top8_day runs before the front page - so
    the record and the page cannot describe different days. It loads the
    taxonomy itself because main() has not loaded it yet at that point.

    One entry per date, {date, register} by id; names resolve at render time
    so renaming a register does not rewrite history. A same-day rebuild is a
    no-op; if the day's register changes mid-day - the register list edited,
    or the epoch moved - the day's entry is replaced rather than appended,
    because one date with two registers is a record nobody can read.
    Returns (changed, entry).
    """
    if tax is None:
        tax = json.loads((ROOT / "data" / "taxonomy.json")
                         .read_text(encoding="utf-8"))
    reg = register_of_day(tax, today)
    if not reg:
        return False, {}
    iso = str(today or
              datetime.datetime.now(datetime.timezone.utc).date().isoformat())[:10]
    entry = {"date": iso, "register": reg["id"]}
    if REGISTER_HISTORY.exists():
        hist = json.loads(REGISTER_HISTORY.read_text(encoding="utf-8"))
    else:
        hist = {"_note": REGISTER_HISTORY_NOTE, "days": []}
    days = hist.setdefault("days", [])
    if days and str(days[-1].get("date")) == iso:
        if days[-1].get("register") == entry["register"]:
            return False, days[-1]
        days.pop()
    days.append(entry)
    hist.setdefault("_note", REGISTER_HISTORY_NOTE)
    REGISTER_HISTORY.parent.mkdir(exist_ok=True)
    REGISTER_HISTORY.write_text(
        json.dumps(hist, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    return True, entry


def register_record(tax, today=None):
    """The day record under the register list, newest first.

    A plain dated list rather than the run-collapsed shape /top8/ uses: the
    rotation is a cycle of eight, so no two consecutive days can share a
    register and there are no runs to collapse. A register that is no longer
    defined is shown as such rather than dropped, because a day that happened
    is a fact even when the thing it showed is gone. Degrades to nothing if
    the file is missing, unreadable or empty.
    """
    if not REGISTER_HISTORY.exists():
        return ""
    try:
        hist = json.loads(REGISTER_HISTORY.read_text(encoding="utf-8"))
    except ValueError:
        return ""
    days = hist.get("days") or []
    if not days:
        return ""
    names = {r["id"]: r.get("name", r["id"]) for r in tax.get("register", [])}
    iso = str(today or
              datetime.datetime.now(datetime.timezone.utc).date().isoformat())[:10]
    rows = []
    for d in reversed(days):
        name = names.get(d.get("register"))
        label = (f'<b>{esc(name)}</b>' if name
                 else '<b>A register no longer defined</b>')
        now = (' <span class="tx-today-tag">today</span>'
               if str(d.get("date")) == iso else "")
        rows.append(f'<li><span class="tx-day-date">{esc(fmt_date(d.get("date")))}</span>'
                    f'{label}{rebuilt_tag(d)}{now}</li>')
    return (f'<details class="tx-reg tx-dayrec" id="tx-reg-record">'
            f'<summary><b>The record</b>'
            f'<span class="tx-count">{len(days)}</span></summary>'
            f'<ul class="tx-days">{"".join(rows)}</ul></details>')


# --------------------------------------------------- the parasocialite of the day
# The front page's daily spotlight: one figure taking turns, one per UTC day,
# chosen by date rather than stored. Same contract as the register rotation -
# what is on show is computable, what is recorded is the day it happened on -
# and the same epoch day, because both shipped together.
PARASOCIALITE = ROOT / "data" / "parasocialite.json"
PARASOCIALITE_HISTORY = ROOT / "data" / "parasocialite_history.json"
PARASOCIALITE_HISTORY_NOTE = (
    "STATEFUL. One record per UTC day: which figure was put forward on the "
    "front page, appended by build_cards.record_parasocialite_day() and never "
    "rewritten. Do not regenerate this file and do not delete it to clean up "
    "- only this sequence shows what the page actually said. Today's choice "
    "is data/editorial_today.json, written by tools/editor.py; the bank in "
    "data/parasocialite.json is the fallback and the source of names. A "
    "selectable member is always a real person or a fictional character, "
    "never a show or a format. A day that tools/archive.py had to close after "
    "the fact carries `reconstructed: true` with the date and input hash that "
    "made the recomputation provable, and the record pages print it as "
    "rebuilt rather than observed. Rendered under the front-page block by "
    "build_cards.parasocialite_record()."
)
# The day the original rotation shipped. It is kept because the committed
# history names figures under it; the daily editor now selects from
# data/parasocialite.json and stores the day's choice in editorial_today.json.
PARASOCIALITE_EPOCH = datetime.date(2026, 10, 19)


def parasocialite_roster():
    """The roster file, or an empty roster if it is missing or unreadable.

    A missing roster degrades the front page to no block rather than a crash:
    the block is a spotlight, not the site's spine, and a build that refused
    over it would take every other page down with it.
    """
    try:
        return json.loads(PARASOCIALITE.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {"members": []}


def _figure_detail(e):
    """A concrete sentence for the front page's 'The detail' line."""
    if not e:
        return ""
    s = " ".join(str(e.get(k) or "") for k in ("significance", "summary"))
    s = re.sub(r"<[^>]+>", " ", s).replace("**", "").replace("*", "").replace("`", "")
    s = " ".join(s.split())
    parts = [p for p in re.split(r"(?<=[.!?])\s+", s) if p.strip()]
    later = [p for p in parts[1:] if 70 <= len(p) <= 240]
    if later:
        return max(later, key=len)
    anyp = [p for p in parts if 70 <= len(p) <= 240]
    return max(anyp, key=len) if anyp else parts[0] if parts else ""


def _editorial_today():
    """Today's generated edition, or {} if the editor has not run."""
    try:
        return json.loads((ROOT / "data" / "editorial_today.json")
                          .read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {}


def parasocialite_of_day(roster=None, today=None):
    """The figure the front page puts forward on a given UTC day.

    Today's edition comes from data/editorial_today.json, written by
    tools/editor.py: a real person or a fictional character, chosen against
    the day's wires when one names them and against the day's theme when none
    does. The bank in data/parasocialite.json is the fallback for a date with
    no edition - a test, a backfill, or a build that ran before the editor -
    and even the fallback only considers `selectable` members, so a show or a
    format can never reach the front page.

    Deterministic for a fixed date and history: the fallback walks the
    selectable bank by ordinal and skips figures used in the last ten days.
    The edition itself is deterministic too, because it is a stored selection
    rather than a clock read.
    """
    iso = str(today or
              datetime.datetime.now(datetime.timezone.utc).date().isoformat())[:10]
    ed = _editorial_today()
    if str(ed.get("date")) == iso and isinstance(ed.get("figure"), dict):
        return ed["figure"]

    bank = (roster or parasocialite_roster()).get("members") or []
    # A day already in the record names its figure. A rebuild must no-op, not
    # rotate away from the day the page actually showed - the same rule the
    # history's same-day replacement enforces from the other side.
    try:
        for d in json.loads(PARASOCIALITE_HISTORY.read_text(encoding="utf-8")).get("days", []):
            if str(d.get("date"))[:10] == iso:
                mid = str(d.get("member"))
                for m in bank:
                    if m.get("id") == mid:
                        return m
    except (OSError, ValueError):
        pass

    members = [m for m in bank if m.get("selectable", True)]
    if not members:
        return None
    try:
        recent = {str(d.get("member")) for d in
                  json.loads(PARASOCIALITE_HISTORY.read_text(encoding="utf-8"))
                  .get("days", [])[-10:]}
    except (OSError, ValueError):
        recent = set()
    pool = [m for m in members if m.get("id") not in recent] or members
    try:
        d = datetime.date.fromisoformat(iso)
    except ValueError:
        d = datetime.datetime.now(datetime.timezone.utc).date()
    return pool[d.toordinal() % len(pool)]


def record_parasocialite_day(today=None):
    """Append today's parasocialite to data/parasocialite_history.json.

    Called from main() before the front page renders - the ledger's
    snapshot-before-feed ordering, the same reason record_top8_day and
    record_register_day run before their pages - so the record and the page
    cannot describe different days.

    One entry per date, {date, member} by id; names resolve at render time so
    renaming a member does not rewrite history. A same-day rebuild is a
    no-op; if the day's figure changes mid-day - the roster edited, or the
    epoch moved - the day's entry is replaced rather than appended, because
    one date with two figures is a record nobody can read.
    Returns (changed, entry).
    """
    member = parasocialite_of_day(parasocialite_roster(), today)
    if not member:
        return False, {}
    iso = str(today or
              datetime.datetime.now(datetime.timezone.utc).date().isoformat())[:10]
    entry = {"date": iso, "member": member.get("id", "")}
    if PARASOCIALITE_HISTORY.exists():
        hist = json.loads(PARASOCIALITE_HISTORY.read_text(encoding="utf-8"))
    else:
        hist = {"_note": PARASOCIALITE_HISTORY_NOTE, "days": []}
    days = hist.setdefault("days", [])
    if days and str(days[-1].get("date")) == iso:
        if days[-1].get("member") == entry["member"]:
            return False, days[-1]
        days.pop()
    days.append(entry)
    hist.setdefault("_note", PARASOCIALITE_HISTORY_NOTE)
    PARASOCIALITE_HISTORY.parent.mkdir(exist_ok=True)
    PARASOCIALITE_HISTORY.write_text(
        json.dumps(hist, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    return True, entry


def parasocialite_record(today=None):
    """The day record under the front-page block, newest first.

    A plain dated list rather than a run-collapsed shape: the rotation is a
    cycle of eight, so no two consecutive days can share a figure and there
    are no runs to collapse. A member no longer in the roster is shown as
    such rather than dropped, because a day that happened is a fact even when
    the thing it showed is gone. Degrades to nothing if the file is missing,
    unreadable or empty.
    """
    if not PARASOCIALITE_HISTORY.exists():
        return ""
    try:
        hist = json.loads(PARASOCIALITE_HISTORY.read_text(encoding="utf-8"))
    except ValueError:
        return ""
    days = hist.get("days") or []
    if not days:
        return ""
    names = {m.get("id"): m.get("name", m.get("id"))
             for m in (parasocialite_roster().get("members") or [])}
    iso = str(today or
              datetime.datetime.now(datetime.timezone.utc).date().isoformat())[:10]
    rows = []
    for d in reversed(days):
        name = names.get(d.get("member"))
        label = (f'<b>{esc(name)}</b>' if name
                 else '<b>A figure no longer in the roster</b>')
        now = (' <span class="psotd-today">today</span>'
               if str(d.get("date")) == iso else "")
        rows.append(f'<li><span class="psotd-day-date">{esc(fmt_date(d.get("date")))}</span>'
                    f'{label}{rebuilt_tag(d)}{now}</li>')
    return (f'<details class="psotd-dayrec" id="psotd-record">'
            f'<summary><b>The record</b>'
            f'<span class="psotd-count">{len(days)}</span></summary>'
            f'<ul class="psotd-days">{"".join(rows)}</ul></details>')


def build_taxonomy_record(data):
    """The register rotation's whole sequence, as a page of its own.

    The spotlight on /taxonomy/ names today's register and the record under
    the list holds the sequence in summary; this page is the same sequence at
    full length, one line per recorded day, newest first, rendered from
    data/register_history.json exactly as record_register_day() wrote it. The
    rotation is recomputable from the date, and that recomputability is
    exactly why the file exists: a rebuild can say what the page would show
    today, not what it showed on a day nobody was there for - so nothing is
    filled in for a day with no record, and a gap stays a gap. Names resolve
    from the current taxonomy at render time, so a register that is no longer
    defined is shown as such rather than dropped.
    """
    tax = json.loads((ROOT / "data" / "taxonomy.json")
                     .read_text(encoding="utf-8"))
    days = []
    if REGISTER_HISTORY.exists():
        try:
            days = (json.loads(REGISTER_HISTORY.read_text(encoding="utf-8"))
                    .get("days") or [])
        except ValueError:
            days = []
    names = {g["id"]: g.get("name", g["id"]) for g in tax.get("register", [])}
    today = datetime.datetime.now(datetime.timezone.utc).date().isoformat()
    rows = []
    for d in reversed(days):
        iso = str(d.get("date") or "")
        rid = str(d.get("register") or "")
        name = names.get(rid)
        if name:
            label = (f'<a href="../index.html#tx-{esc(rid)}">'
                     f'<b>{esc(name)}</b></a>')
        else:
            label = '<b>A register no longer defined</b>'
        now = (' <span class="tx-today-tag">today</span>'
               if iso == today else "")
        rows.append(f'<li><span class="tx-day-date">{fmt_date(iso)}</span>'
                    f'{label}{rebuilt_tag(d)}{now}</li>')
    if rows:
        body = f'<ul class="tx-days">{"".join(rows)}</ul>'
    else:
        body = ('<p class="sec-lede" style="max-width:62ch">Nothing has been '
                'recorded yet. The record begins the first day the rotation '
                'runs, and after that each day is appended as it happens '
                'rather than reconstructed.</p>')
    count = len(days)
    day_count = f"{count} day" + ("" if count == 1 else "s")
    return f"""<!DOCTYPE html>
<html lang="en"><head><meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>The register record — Parasocialize</title>
<meta name="description" content="Every day the eight registers have taken their turn, one line per day, as recorded.">
{HEAD.format(site=SITE, path="/taxonomy/record/", otype="website",
             title="The register record",
             desc="Every day the eight registers have taken their turn, one line per day.",
             root=root(2))}
</head>
<body>
<a class="skip" href="#record">Skip to the record</a>
<div class="grain" aria-hidden="true"></div>
{NAV.format(root=root(2), total=len(data['cards']), mk=wordmark("nav"))}
<main id="record">
<section class="section" style="padding-bottom:6px">
  <p class="kicker">The taxonomy &middot; register record &middot; {day_count} recorded</p>
  <h1 style="font-family:var(--serif);font-size:clamp(2rem,5.4vw,3.6rem);font-weight:900;
     letter-spacing:-.03em;line-height:1.02;margin:0 0 16px;max-width:22ch">Every day, one of the eight</h1>
  <p class="sec-lede" style="max-width:62ch;font-size:1.1rem">The eight registers
  take turns, one per UTC day, and the turn is decided by the date rather than
  by hand. This is the sequence as it was recorded: one line per day, naming
  the register that was put forward.</p>
</section>
<section class="section" style="padding-top:8px">
  {body}
  <p class="countline" style="margin-top:30px">A register that is no longer
  defined is shown as such, and a day with no line is a day with no record
  rather than a day reconstructed.
  <a href="../index.html">Today's register →</a></p>
</section>
</main>
{FOOT.format(root=root(2), sweep=MESSY, motto='ONE-SIDED.<br>NOTHING HAS CHANGED SINCE 600 BC.')}
</body></html>"""


def build_taxonomy(enc, data):
    """The classification itself, as a page.

    Built from data/taxonomy.json and data/taxonomy_placements.json rather than
    written out, because a taxonomy page that can drift from the taxonomy is
    worse than no page: it would be a second, wrong set of facts about the same
    subject, published. Every count on this page is counted from the placements
    that exist, and every entry listed is one somebody placed by reading it.

    A sub-category with no entry is shown empty and says so. It is not hidden,
    because the gap is the useful part - it is the list of writing still owed,
    and a taxonomy that quietly prunes itself is one that can be believed when
    it should not be.
    """
    tax = json.loads((ROOT / "data" / "taxonomy.json").read_text(encoding="utf-8"))
    pla = json.loads((ROOT / "data" / "taxonomy_placements.json")
                     .read_text(encoding="utf-8"))["assignments"]
    byid = {e["id"]: e for e in enc["entries"]}
    r = root(1)

    # counts, from the placements rather than from anything declared
    cat_n, sub_n = Counter(), Counter()
    for v in pla.values():
        cat_n[v["cat"]] += 1
        sub_n[v["sub"]] += 1

    # the stories, counted against the same taxonomy. Separate file because the
    # two corpora fail differently: an entry is a claim about a thing, a story
    # is journalism and the placement has to survive the writer disagreeing.
    splace = {}
    sp = ROOT / "data" / "story_placements.json"
    if sp.exists():
        splace = json.loads(sp.read_text(encoding="utf-8"))["placements"]
    story_n = Counter(v["cat"] for v in splace.values())
    story_total = len(splace)

    def entry_rows(sub):
        out = []
        for eid, v in sorted(pla.items()):
            if v["sub"] != sub:
                continue
            e = byid.get(eid)
            if not e:
                continue
            out.append(
                f'<li><a href="{r}encyclopedia/{esc(eid)}.html">'
                f'<b>{esc(e.get("title"))}</b>'
                f'<span class="tx-why">{esc(e.get("year") or "")} · '
                f'{esc(enc["kinds"].get(e.get("kind", ""), ""))}</span>'
                f'<span class="tx-r">{emph(v["why"])}</span></a></li>')
        return "".join(out)

    # The anchor was stored as a key into _literature and the page was printing
    # the key, so the reader saw "ANCHORED - HORTON-WOHL-1956": something shaped
    # like a citation that cannot be followed. It now prints a human label and
    # links to the full reference in the Sources section.
    labels = tax.get("_anchor_labels") or {}

    def anchor_span(key, cls="tx-anchor"):
        if not key:
            return ""
        label = labels.get(key, key)
        return (f'<span class="{cls}">anchored · '
                f'<a href="#tx-src-{esc(key)}">{esc(label)}</a></span>')

    blocks = []
    for a in tax["attachment"]:
        subs = []
        for s in a["sub"]:
            n = sub_n.get(s["id"], 0)
            anchor = anchor_span(s.get("anchor"))
            note = f'<p class="tx-note">{esc(s["note"])}</p>' if s.get("note") else ""
            empty = ""
            if n == 0:
                empty = ('<p class="tx-empty">Nothing in the corpus sits here '
                         'yet. Recorded rather than hidden: it is either a hole '
                         'in the encyclopedia or a category that does not earn '
                         'its place, and both are worth knowing.</p>')
            rows = entry_rows(s["id"])
            body = (f'<ul class="tx-entries">{rows}</ul>' if rows else "")
            # The four fields are the classification doing work, not a
            # gloss on it. A definition cannot be applied to anything; the
            # test is what a person needs at 2am deciding where a new entry
            # goes, and `not` is what stops the list growing sideways.
            triad = ""
            if s.get("test") or s.get("not") or s.get("mechanism"):
                cells = ""
                for label, key, cls in (("Test", "test", "tx-test"),
                                        ("Not", "not", "tx-not"),
                                        ("Mechanism", "mechanism", "tx-mech")):
                    if s.get(key):
                        cells += (f'<div class="tx-triad-c {cls}">'
                                  f'<span class="tx-triad-k">{label}</span>'
                                  f'<p>{emph(s[key])}</p></div>')
                triad = f'<div class="tx-triad">{cells}</div>'
            subs.append(f"""<details class="tx-sub" id="tx-{esc(s['id'])}">
      <summary><span class="tx-name">{esc(s['name'])}</span>
        <span class="tx-n">{n}</span></summary>
      <p class="tx-def">{emph(s['def'])}</p>{triad}{note}{anchor}{empty}{body}
    </details>""")
        n = cat_n.get(a["id"], 0)
        sn = story_n.get(a["id"], 0)
        blocks.append(f"""<section class="tx-cat" id="tx-{esc(a['id'])}" style="--c:{esc(a['colour'])}">
  <p class="kicker">{esc(a['sign'])} · {n} entries · {sn} stories</p>
  <h2>{esc(a['blurb'])}</h2>
  <p class="tx-note-big">{esc(a['note'])}</p>
  <p class="countline"><a href="{r}ways/{esc(a['id'])}/index.html">Read the stories and entries filed on this way →</a></p>
  {''.join(subs)}
</section>""")

    day_reg = register_of_day(tax)
    day_term = day_reg["id"].split("-")[0] if day_reg else ""
    regs = []
    for g in tax["register"]:
        note = f'<p class="tx-note">{emph(g["note"])}</p>' if g.get("note") else ""
        # same four fields as the attachment axis: a register you cannot test
        # is a heading, and a heading cannot be assigned to
        cells = ""
        if g.get("test") or g.get("not") or g.get("mechanism"):
            for label, key, cls in (("Test", "test", "tx-test"),
                                    ("Not", "not", "tx-not"),
                                    ("Mechanism", "mechanism", "tx-mech")):
                if g.get(key):
                    cells += (f'<div class="tx-triad-c {cls}">'
                              f'<span class="tx-triad-k">{label}</span>'
                              f'<p>{emph(g[key])}</p></div>')
        triad = f'<div class="tx-triad">{cells}</div>' if cells else ""
        is_today = bool(day_reg) and g["id"] == day_reg["id"]
        regs.append(f"""<details class="tx-reg{' tx-today' if is_today else ''}" id="tx-{esc(g['id'])}"{' open' if is_today else ''}>
  <summary><b>{emph(g['name'])}</b>{'<span class="tx-today-tag">today</span>' if is_today else ''}</summary>
  <p class="tx-def">{emph(g['def'])}</p>{triad}{note}{anchor_span(g.get('anchor'))}
</details>""")

    # The register of the day, on the page rather than in a comment. The term
    # is the id's first segment (reciprocal-edge -> "reciprocal") because the
    # corpus uses both the spaced and the hyphenated form; a substring of the
    # id is a superset of either, so no entry naming the register is missed.
    today_iso = datetime.datetime.now(datetime.timezone.utc).date().isoformat()
    if day_reg:
        day_html = f"""<div class="tx-day">
    <p class="kicker">Register of the day · {esc(fmt_date(today_iso))}</p>
    <p class="tx-day-line"><b>{esc(day_reg['name'])}</b>
      <a href="#tx-{esc(day_reg['id'])}">Read the definition</a>
      <a href="{r}encyclopedia/index.html?q={esc(day_term)}#db">Everything that mentions it</a>
      {anchor_span(day_reg.get('anchor'))}</p>
    <p class="tx-note">The eight registers take turns, one per UTC day. Today's is
    marked in the list below, opened on arrival, and the days behind it are
    recorded under the list. The <a href="record/index.html">whole record</a> is
    one line per day.</p>
  </div>"""
    else:
        day_html = ""
    reg_rec_html = register_record(tax, today_iso)

    # The third axis is rendered with the same four fields as the other two, for
    # the same reason: a member you cannot test is a heading. It carries a count
    # of placements, and a member with none says so on the page rather than
    # printing as though it were populated - a shelf shown to a reader with
    # nothing on it has to admit it, or the axis is a promise the page does not
    # keep.
    others = []
    oth_counts = Counter(v["other"] for v in pla.values() if v.get("other"))
    OTH = tax.get("otherness") or {}
    for m in OTH.get("members", []):
        n = oth_counts.get(m["id"], 0)
        cells = ""
        for label, key, cls in (("Test", "test", "tx-test"),
                                ("Not", "not", "tx-not"),
                                ("Mechanism", "mechanism", "tx-mech")):
            if m.get(key):
                cells += (f'<div class="tx-triad-c {cls}">'
                          f'<span class="tx-triad-k">{label}</span>'
                          f'<p>{emph(m[key])}</p></div>')
        # Counted from the placements, never typed. Zero is printed as a gap.
        tally = (f'<span class="tx-count">{n}</span>' if n else
                 '<span class="tx-count tx-count-0">nothing placed yet</span>')
        others.append(f"""<details class="tx-reg" id="tx-o-{esc(m['id'])}">
  <summary><b>{esc(m['name'])}</b>{tally}</summary>
  <p class="tx-def">{emph(m['def'])}</p><div class="tx-triad">{cells}</div>
</details>""")
    oth_html = "".join(others)
    n_oth = len(OTH.get("members", []))
    n_oth_stated = sum(1 for v in pla.values() if v.get("other"))

    # The fourth axis, rendered identically. Recovered from the 2019 character
    # chart, which drew affection direction as an edge type (Directed Affection
    # against Mutual Love) - a distinction the schema could not express, since
    # every relation in `encyclopedia.json` is chronological or bibliographic.
    # It has three members rather than the chart's two, because the corpus found
    # a third the chart could not have: reciprocity that is performed rather than
    # felt. Counted from the placements, never typed.
    recs = []
    rec_counts = Counter(v["rec"] for v in pla.values() if v.get("rec"))
    REC = tax.get("reciprocity") or {}
    for m in REC.get("members", []):
        n = rec_counts.get(m["id"], 0)
        cells = ""
        for label, key, cls in (("Test", "test", "tx-test"),
                                ("Not", "not", "tx-not"),
                                ("Mechanism", "mechanism", "tx-mech")):
            if m.get(key):
                cells += (f'<div class="tx-triad-c {cls}">'
                          f'<span class="tx-triad-k">{label}</span>'
                          f'<p>{emph(m[key])}</p></div>')
        tally = (f'<span class="tx-count">{n}</span>' if n else
                 '<span class="tx-count tx-count-0">nothing placed yet</span>')
        recs.append(f"""<details class="tx-reg" id="tx-r-{esc(m['id'])}">
  <summary><b>{esc(m['name'])}</b>{tally}</summary>
  <p class="tx-def">{emph(m['def'])}</p><div class="tx-triad">{cells}</div>
</details>""")
    rec_html = "".join(recs)
    n_rec = len(REC.get("members", []))
    n_rec_stated = sum(1 for v in pla.values() if v.get("rec"))

    lit = "".join(f'<li id="tx-src-{esc(k)}"><b>{esc(labels.get(k, k))}</b> '
                  f'<span class="tx-lit-full">{esc(v)}</span></li>'
                  for k, v in tax["_literature"].items()
                  if k != "note")
    lit_note = esc(tax["_literature"]["note"])

    # the migration table: how the ten sections map onto the new axes, so a
    # reader comparing the front page to this one is given the mapping rather
    # than left to infer it
    mig = tax.get("migration") or {}
    migrows = ""
    for m in mig.get("map", []):
        tos = ", ".join(m["to"])
        migrows += (f'<details class="tx-migr"><summary><b>{esc(m["from"])}</b>'
                   f'<span class="tx-arrow">→</span><span>{esc(tos)}</span>'
                   f'</summary><p class="tx-def">{emph(m["why"])}</p></details>')

    total = len(pla)
    # Counted from the taxonomy, never typed in. The meta description used to
    # say "thirty-eight sub-categories and six registers" as literals, which is
    # a claim about the data that goes stale the moment a sub-category is added
    # and is invisible when it does. Same defect as a hardcoded count in a
    # chart legend.
    n_cat = len(tax["attachment"])
    n_sub = sum(len(a["sub"]) for a in tax["attachment"])
    n_reg = len(tax["register"])
    n_oth_meta = len((tax.get("otherness") or {}).get("members", []))
    n_rec_meta = len((tax.get("reciprocity") or {}).get("members", []))
    WORDS = {3: "three", 4: "four", 5: "five", 6: "six", 7: "seven", 8: "eight",
             9: "nine", 10: "ten", 11: "eleven", 12: "twelve", 13: "thirteen",
             14: "fourteen", 15: "fifteen", 16: "sixteen", 17: "seventeen",
             18: "eighteen", 19: "nineteen", 20: "twenty", 30: "thirty",
             38: "thirty-eight", 40: "forty"}
    words = lambda n: WORDS.get(n, str(n))
    shape = (f"{words(n_cat)} kinds of object, "
             f"{words(n_sub)} sub-categories, {words(n_reg)} registers, "
             f"{words(n_oth_meta)} kinds of otherness and "
             f"{words(n_rec_meta)} states of reciprocity")
    return f"""<!DOCTYPE html>
<html lang="en"><head><meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>The taxonomy - Parasocialize</title>
<meta name="description" content="How one-sided attachment is classified: {shape}, with every entry placed and the reasoning shown.">
<link rel="canonical" href="https://www.parasocialize.com/taxonomy/">
<meta property="og:type" content="website">
<meta property="og:title" content="The taxonomy - Parasocialize">
<meta property="og:description" content="{words(n_cat).capitalize()} kinds of object, {n_sub} sub-categories, {n_reg} registers, {n_oth_meta} kinds of otherness. {total} entries placed.">
{HEAD.format(site=SITE, path="/taxonomy/", otype="website",
             title="The taxonomy - Parasocialize",
             desc="How one-sided attachment is classified.", root=r)}
</head>
<body>
<a class="skip" href="#tx-attachment">Skip to the categories</a>
<div class="grain" aria-hidden="true"></div>
{NAV.format(root=r, total=len(data['cards']), mk=wordmark("nav"))}

<main>
<section class="section" id="tx-attachment">
  <p class="kicker">The taxonomy · {total} entries and {story_total} stories placed</p>
  <h1 class="h-title" style="font-size:clamp(1.9rem,4.6vw,3rem)">What is on the other end</h1>
  <p class="sec-lede" style="max-width:66ch">A parasocial bond is defined by
  what is on the far side of it. This is that list: {words(n_cat)} kinds of
  object, {words(n_sub)} sub-categories beneath them, {words(n_reg)} registers for
  what is <em>happening</em> in the tie, and {words(n_oth_meta)} kinds of
  <em>otherness</em> for what the far side is made of. All {total}
  encyclopedia entries and all {story_total} stories are placed on it, and the
  reason for each placement is printed rather than kept in a commit message.</p>
  <p class="sec-lede" style="max-width:66ch;margin-top:18px">The previous
  classification was ten sections built from whatever stories existed at the
  time, and it could not hold eighteen of the encyclopedia's own entries —
  including the founding document of this site. Three of the ten were not
  objects at all. That is why this is more than two axes.</p>
</section>

<section class="section" style="padding-top:0">
  <p class="kicker">Register · what is happening in the tie · {n_reg}</p>
  {day_html}
  <div class="tx-regs">{''.join(regs)}</div>
  {reg_rec_html}
</section>

<section class="section" style="padding-top:0">
  <p class="kicker">Attachment · who or what is on the other end · {n_cat}</p>
  {''.join(blocks)}
</section>

<section class="section" style="padding-top:0" id="tx-otherness">
  <p class="kicker">Otherness · what the other end is made of · {n_oth}</p>
  <p class="sec-lede" style="max-width:66ch">{emph(OTH.get("_note", ""))}</p>
  <p class="sec-lede" style="max-width:66ch;margin-top:16px">{emph(OTH.get("_why_it_is_a_separate_axis", ""))}</p>
  <div class="tx-regs" style="margin-top:22px">{oth_html}</div>
  <p class="countline" style="max-width:66ch;margin-top:20px">{n_oth_stated} of
  {total} entries carry a kind of otherness. It is optional, because it is a
  third cut rather than a requirement: forcing every entry to state one would be
  the same move as filling a hole to make a chart look even. A member with
  nothing placed against it is printed as an empty shelf on purpose — that list
  is the writing still owed.</p>
</section>

<section class="section" style="padding-top:0" id="tx-reciprocity">
  <p class="kicker">Reciprocity · whether the other end attaches back · {n_rec}</p>
  <p class="sec-lede" style="max-width:66ch">{emph(REC.get("_note", ""))}</p>
  <p class="sec-lede" style="max-width:66ch;margin-top:16px">{emph(REC.get("_why_it_is_a_separate_axis", ""))}</p>
  <p class="sec-lede" style="max-width:66ch;margin-top:16px">{emph(REC.get("_relation_to_the_2019_chart", ""))}</p>
  <div class="tx-regs" style="margin-top:22px">{rec_html}</div>
  <p class="countline" style="max-width:66ch;margin-top:20px">{n_rec_stated} of
  {total} entries state whether the bond attaches back, and the number is
  small on purpose. <em>Directed</em> is the default condition of the entire
  site, so stating it everywhere would print a hundred and eighty identical
  labels and bury the handful that are not. The two worth watching are
  <em>reciprocated</em> and <em>simulated</em>: a corpus named after
  one-sided attachment that cannot count its own exceptions is not measuring
  the thing it is named after.</p>
  <p class="countline" style="max-width:66ch;margin-top:20px"><a href="{r}exceptions/index.html">
  The {n_rec} exceptions, counted &mdash; including where this count is probably wrong &rarr;</a></p>
</section>

<section class="section" style="padding-top:0">
  <p class="kicker">From the ten sections to the {words(n_cat)} categories</p>
  <p class="sec-lede" style="max-width:66ch">{emph(mig["headline"])}</p>
  <div class="tx-mig">{migrows}</div>
  <p class="countline" style="max-width:66ch;margin-top:18px">{esc(mig["counts"])}</p>
</section>

<section class="section" style="padding-top:0">
  <p class="kicker">Sources</p>
  <p class="countline" style="max-width:66ch">{lit_note}</p>
  <ul class="tx-lit">{lit}</ul>
</section>
</main>
<footer class="footer"><div class="foot-grid">
  <div class="foot-brand">
    <p class="wordmark foot-mark"><img class="logo-img" src="{r}img/logo.svg" alt="" width="24" height="24">PARA<b>SOCIALIZE</b></p>
    <p class="foot-note">{MESSY}<br>Kept by Enan Joe Heneghan - video store clerk, M.A., teacher in Australia.</p>
    <p class="foot-tag">ONE-SIDED.<br>NOTHING HAS CHANGED SINCE 600 BC.</p>
  </div>
  <nav class="foot-nav" aria-label="Footer">
    <div class="foot-col">
      <p class="foot-head">Read</p>
      <a href="{r}index.html">Latest</a>
      <a href="{r}sections/index.html">Stories</a>
      <a href="{r}top8/index.html">Top 8</a>
      <a href="{r}history/index.html">History</a>
      <a href="{r}shelf/index.html">Works</a>
      <a href="{r}moments/index.html">Moments</a>
    </div>
    <div class="foot-col">
      <p class="foot-head">Look up</p>
      <a href="{r}encyclopedia/index.html">Encyclopedia</a>
      <a href="{r}atlas/index.html">Atlas</a>
      <a href="{r}timeline/index.html">Timeline</a>
      <a href="{r}taxonomy/index.html">Taxonomy</a>
      <a href="{r}citations/index.html">Citations</a>
      <a href="{r}quiz/index.html">Quiz</a>
    </div>
    <div class="foot-col">
      <p class="foot-head">The project</p>
      <a href="{r}credits/index.html">About</a>
      <a href="{r}tip/index.html">Contact</a>
      <a href="{r}top8/archive/index.html">Archive</a>
      <a href="{r}ledger/index.html">Ledger</a>
      <a href="{r}membership/index.html">Membership</a>
    </div>
    <div class="foot-col">
      <p class="foot-head">Follow</p>
      <a class="foot-support" href="https://ko-fi.com/parasocialing" target="_blank" rel="noopener nofollow">Support the archive</a>
      <a href="{r}signal/latest.html">The Signal</a>
      <a href="{r}radar.xml">RSS feed</a>
      <a href="{r}brand/index.html">iYi</a>
    </div>
  </nav>
</div></footer>
<script>
(function(){{
  var b=document.querySelector('.menu-btn'),n=document.getElementById('nav');
  if(b)b.addEventListener('click',function(){{
    var o=document.body.classList.toggle('nav-open');
    b.setAttribute('aria-expanded',String(o));
  }});
}})();
</script>
</body></html>"""


def _fmt_year(y):
    if y is None:
        return "—"
    if y < 0:
        return f"{abs(y)} BC"
    return str(y)


def _fmt_span(ent):
    """Formatted date for an entry, including the end when it has one.

    `roman-imagines` runs from 250 BC into the 6th century AD. Its kicker used to
    print the start year alone, so the page head said "250 BC" while the summary
    directly beneath it said the practice continued into the fourth and sixth
    centuries AD - the entry disagreeing with itself on its own front page.
    A range the reader can see is the fix; inventing an AD marker for bare
    positive years is not, because the era label already carries that and 178
    entries would change.
    """
    y = ent.get("year")
    if y is None:
        return ""
    if not ent.get("year_end"):
        return _fmt_year(y)
    return f"{_fmt_year(y)}\u2013{_fmt_year(ent['year_end'])}"


def _era_bucket(y):
    if y < 0:
        return "Before 0"
    if y < 500:
        return "0-499"
    if y < 1000:
        return "500-999"
    if y < 1500:
        return "1000-1499"
    if y < 1700:
        return "1500-1699"
    if y < 1800:
        return "1700-1799"
    if y < 1900:
        return "1800-1899"
    if y < 1950:
        return "1900-1949"
    if y < 2000:
        return "1950-1999"
    if y < 2010:
        return "2000-2009"
    return "2010+"


def _entry_row(x, enc, depth):
    """One entry as a timeline row. Used by both the master timeline and the
    per-section ones, so they can never drift apart. NB: parameter is x, not e -
    esc() is the escape helper at module scope."""
    kinds = enc["kinds"]
    lanes = enc["lanes"]
    dots = "".join(
        f'<i class="lane-dot" style="--c:{lanes[l]["colour"]}" '
        f'title="{esc(lanes[l]["name"])}"></i>'
        for l in x.get("lanes", []) if l in lanes)
    flag = "" if x.get("verified") else '<span class="check" title="citation needs checking">?</span>'
    return (f'<li class="tl-item" data-lanes="{esc(" ".join(x.get("lanes", [])))}" '
            f'data-kind="{esc(x.get("kind", ""))}" data-era="{esc(_era_bucket(_y(x)))}" '
            f'data-hay="{esc((x.get("title", "") + " " + x.get("summary", "")).lower())}">'
            f'<span class="tl-year">{esc(_fmt_year(x.get("year")))}</span>'
            f'<span class="tl-body">'
            f'<a class="tl-title" href="{depth}encyclopedia/{esc(x["id"])}.html">{esc(x["title"])}</a>'
            f'<span class="tl-kind">{esc(kinds.get(x.get("kind", ""), ""))}</span>'
            f'<span class="tl-dots">{dots}</span>{flag}'
            f'<p class="tl-sum">{esc(x.get("summary", ""))}</p>'
            f'</span></li>')


# The declared `kinds` values are sentences ("A mechanism or tactic"), which
# is fine in a filter list and wrong in a count. These are the nouns for the
# sentence the timeline builds about each era.
_KIND_NOUN = {
    "term": "terms", "person": "people", "work": "works", "study": "studies",
    "event": "events", "mechanism": "mechanisms", "case": "cases",
    "institution": "institutions",
}
_KIND_NOUN_ONE = {
    "term": "term", "person": "person", "work": "work", "study": "study",
    "event": "event", "mechanism": "mechanism", "case": "case",
    "institution": "institution",
}


def _plural(n, one, many):
    return f"{n} {one if n == 1 else many}"


def _join(parts):
    if len(parts) == 1:
        return parts[0]
    if len(parts) == 2:
        return f"{parts[0]} and {parts[1]}"
    return ", ".join(parts[:-1]) + f" and {parts[-1]}"


def build_timeline(enc, data, section=None):
    # /timeline/ is depth 1; /timeline/<section>/ is depth 2.
    r = root(2) if section else root(1)
    a = None
    if section:
        a = next((x for x in data["sections"] if x["id"] == section), None)
    pool = [e for e in enc["entries"] if (not section or section in e.get("sections", []))]
    pool.sort(key=lambda e: (_y(e), e.get("title", "")))

    # group by century-ish bucket, oldest first
    buckets = {}
    for e in pool:
        buckets.setdefault(_era_bucket(_y(e)), []).append(e)
    order = ["Before 0", "0-499", "500-999", "1000-1499", "1500-1699", "1700-1799",
             "1800-1899", "1900-1949", "1950-1999", "2000-2009", "2010+"]
    # what each era is actually made of in this database
    def shape_of(bs):
        """What this band is actually made of. Counted, not asserted: it is a
        description of what this database holds for the period, not a claim
        about the period."""
        from collections import Counter
        kc = Counter(str(x.get("kind", "")) for x in bs)
        lc = Counter(l for x in bs for l in (x.get("lanes") or []))
        bits = []
        if kc:
            top = kc.most_common(3)
            nouns = [_KIND_NOUN.get(k, k) for k, _ in top]
            if len(kc) == 1:
                k, kn = top[0]
                one, many = _KIND_NOUN_ONE.get(k, k), _KIND_NOUN.get(k, k)
                bits.append(f"it is a {one}" if kn == 1
                            else f"all {kn} of them are {many}")
            else:
                lead = nouns[0] if top[0][1] == 1 else nouns[0]
                bits.append("mostly " + _join([f"{kn} {nm}" if kn > 1 else nm
                                              for (k, kn), nm in zip(top, nouns)]))
        if lc:
            ln = lc.most_common(1)[0][0]
            bits.append("filed as " + enc["lanes"].get(ln, {}).get("name", ln).lower())
        return ". ".join(bits)

    groups = ""
    for b in order:
        if b not in buckets:
            continue
        bs = buckets[b]
        items = "".join(_entry_row(e, enc, r) for e in bs)
        sh = shape_of(bs)
        groups += (f'<section class="tl-era" id="era-{esc(b.replace(" ","-").replace("+","plus"))}">'
                   f'<h2 class="tl-era-h">{esc(b)}<span>{len(bs)}</span></h2>'
                   + (f'<span class="tl-era-note">{sh}.</span>' if sh else "")
                   + f'<ul class="tl-list">{items}</ul></section>')

    # the density strip: how thick the record is, to scale
    if not section:
        peak = max((len(buckets.get(b, [])) for b in order), default=1) or 1
        dens = "".join(
            f'<a class="tl-den" href="#era-{esc(b.replace(" ","-").replace("+","plus"))}" '
            f'title="{esc(b)}: {len(buckets.get(b, []))} entries">'
            f'<em>{len(buckets[b]) if b in buckets else ""}</em>'
            f'<i style="height:{len(buckets.get(b, [])) / peak * 100:.0f}%"></i>'
            f'<b>{esc(b.replace("-", "\u2013"))}</b></a>'
            for b in order)
        density = (f'<div class="tl-density" role="img" '
                   f'aria-label="Entries per era, from antiquity to now">{dens}</div>'
                   f'<p class="countline" style="margin-top:2px">Entries per era, to scale. '
                   f'The thin parts are thin because the record is thin, not because '
                   f'nobody was doing this \u2014 an antiquity entry is a sculpture somebody '
                   f'wrote down.</p>')
    else:
        density = ""

    lane_filters = "".join(
        f'<button class="chip" data-lane="{esc(l)}">{esc(v["name"])}</button>'
        for l, v in enc["lanes"].items())
    kind_filters = "".join(
        f'<button class="chip" data-kind="{esc(k)}">{esc(v)}</button>'
        for k, v in enc["kinds"].items())

    if a:
        col = a.get("colour", "#ff5a1f")
        head = (f'<p class="kicker" style="color:{esc(col)}">Timeline · {len(pool)} entries</p>'
                f'<h1 style="color:{esc(col)}">{esc(a["sign"])}</h1>'
                f'<p class="sec-lede">{esc(a["blurb"])}</p>')
        title = f"{a['sign']} timeline - Parasocialize"
    else:
        head = ('<p class="kicker">The whole thing, oldest first</p>'
                '<h1 class="h-title">The parasocial timeline</h1>'
                f'<p class="sec-lede" style="max-width:64ch">Every entry in the encyclopedia, in order. '
                f'{len(pool)} of them, from a sculptor in antiquity to a policy update in 2023. '
                f'Each one links to its own page, and most pages link to their neighbours.</p>')
        title = "The parasocial timeline - Parasocialize"

    others = "".join(
        f'<a class="chip" style="--c:{esc(x.get("colour","#ff5a1f"))}" '
        f'href="{r}timeline/{esc(x["id"])}/index.html">{esc(x["sign"])}</a>'
        for x in data["sections"])

    return f"""<!DOCTYPE html>
<html lang="en"><head><meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{esc(title)}</title>
<meta name="description" content="The parasocial timeline, {len(pool)} entries, oldest first.">
{HEAD.format(site=SITE, path=f"/timeline/{section or ''}", otype="website",
             title=esc(title), desc="The parasocial timeline, oldest first.", root=r)}
</head>
<body>
<a class="skip" href="#tl">Skip to the timeline</a>
<div class="grain" aria-hidden="true"></div>
{NAV.format(root=r, total=len(data['cards']), mk=wordmark("nav"))}
<main>
<section class="section" id="tl" style="padding-bottom:20px">
  {head}
  {density}
</section>
<section class="section" style="padding-top:0">
  <div class="bar">
    <input class="search" id="q" type="search" placeholder="Search {len(pool)} entries…"
      aria-label="Search the timeline">
  </div>
  <p class="kicker" style="margin-top:18px">Lanes — what it does</p>
  <div class="chips" id="lanes">{lane_filters}</div>
  <p class="kicker" style="margin-top:14px">Kinds — what it is</p>
  <div class="chips" id="kinds">{kind_filters}</div>
  <p class="countline" id="count" aria-live="polite"></p>

  <div class="tl" id="list">{groups}</div>

  <p class="kicker" style="margin-top:44px">Per-section timelines</p>
  <div class="chips">{others}</div>
  <p class="countline" style="margin-top:18px">
    <b>{sum(1 for e in enc['entries'] if not e.get('verified'))}</b> of
    {len(enc['entries'])} entries are flagged for a citation check.
    That is the work queue, not a failure — see <a href="{r}encyclopedia/">the database</a>.</p>
</section>
</main>
{FOOT.format(root=r, sweep=MESSY, motto='OLDEST FIRST.<br>THAT IS THE ONLY HONEST ORDER.')}
<script>
(function(){{
  var q=document.getElementById('q'),c=document.getElementById('count'),
      items=[].slice.call(document.querySelectorAll('.tl-item')),
      laneBtns=[].slice.call(document.querySelectorAll('[data-lane]')),
      kindBtns=[].slice.call(document.querySelectorAll('[data-kind]')),
      lane=null,kind=null,total=items.length;
  function run(){{
    var t=(q.value||'').trim().toLowerCase(),n=0;
    items.forEach(function(el){{
      var okL=!lane||(' '+el.dataset.lanes+' ').indexOf(' '+lane+' ')>-1,
          okK=!kind||el.dataset.kind===kind,
          okT=!t||el.dataset.hay.indexOf(t)>-1,
          on=okL&&okK&&okT;
      el.style.display=on?'':'none';if(on)n++;
    }});
    [].forEach.call(document.querySelectorAll('.tl-era'),function(sec){{
      var any=[].some.call(sec.querySelectorAll('.tl-item'),function(x){{return x.style.display!=='none'}});
      sec.style.display=any?'':'none';}});
    c.textContent=n+' / '+total+' ENTRIES'+(lane?' · '+lane.toUpperCase():'')
      +(kind?' · '+kind.toUpperCase():'')+(t?' · "'+q.value.toUpperCase()+'"':'');
  }}
  function toggle(btns,attr,set){{
    return function(ev){{
      var v=ev.currentTarget.dataset[attr];
      set=(set===v?null:v);
      btns.forEach(function(b){{b.classList.toggle('on',b.dataset[attr]===set);}});
      run();
    }};
  }}
  laneBtns.forEach(function(b){{b.addEventListener('click',toggle(laneBtns,'lane',null));}});
  kindBtns.forEach(function(b){{b.addEventListener('click',toggle(kindBtns,'kind',null));}});
  q.addEventListener('input',run);run();
}})();
</script>
</body></html>"""


def entry_hero(ent, manifest, depth=1):
    """The picture at the top of an entry page.

    A reviewed photograph wins; otherwise the entry's own title plate. The
    plate is drawn from the record rather than fetched, so it is always about
    the entry and never carries a licence, which is the only reason it can
    stand in for a photograph of a show at all.
    """
    slug = ent.get("id")
    photo = img_for(manifest, slug, depth)
    if photo:
        # `photo` is the DICT img_for returns - path, credit, page, caption,
        # kind. This line escaped the whole dict and put it in the src
        # attribute, so the built page carried
        #   <img src="{'path': '../img/...', 'credit': '...'}" >
        # and link_audit failed on a 404 whose target was a stringified dict.
        #
        # It is invisible until an entry actually has an image: img_for returns
        # None, the plate branch runs instead, and the encyclopedia had no image
        # record at all until 2026-10-04. So this is the first encyclopedia image
        # in the project's history, and it walked straight into a bug that had
        # been sitting here the whole time. The plate branch is why nothing
        # caught it - a dormant path is not a checked path.
        src = esc(photo.get("path", ""))
        cap = next((i.get("caption") for i in manifest.get("items", [])
                    if i.get("slug") == slug and i.get("caption")), "")
        source = next((i.get("src") for i in manifest.get("items", [])
                       if i.get("slug") == slug), None)
        by = ""
        if isinstance(source, dict) and source.get("author"):
            label = (f'{source.get("author", "")}'
                     + (f' · {source.get("licence", "")}'
                        if source.get("licence") else ""))
            page = source.get("page", "#")
            if page and page != "#":
                by = (f'<span class="ent-by"><a href="{esc(page)}" target="_blank" '
                      f'rel="noopener nofollow">{esc(label)}</a></span>')
            else:
                by = f'<span class="ent-by">{esc(label)}</span>'
        alt = cap or ent["title"]
        return (f'<figure class="ent-hero"><img src="{src}" alt="{esc(alt)}" '
                f'loading="lazy" decoding="async">'
                + (f'<figcaption>{esc(cap)} {by}</figcaption>' if cap else "")
                + "</figure>")
    plate = f"img/plate/{esc(slug)}.svg"
    return (f'<figure class="ent-hero plate"><img src="{root(depth)}{plate}" '
            f'alt="A title plate for {esc(ent["title"])}: the name, the year and '
            f'a mark drawn from the entry. It is not a photograph." '
            f'loading="lazy" decoding="async"></figure>')


def _runtime_words(secs):
    """Describe a video's length truthfully, or admit it is not known.

    The old Watch block called every episode "the fifty-second version". The
    three that exist run 42.0s, 53.7s and 63.4s, so the label was wrong for all
    of them - it was a string that only executes once somebody pastes in a
    YouTube URL, which is precisely why nobody had caught it. AGENTS had recorded
    it as "wrong for 53-64s episodes", which forgot the short one.

    Rounds to something a reader can hold in their head rather than to the
    second: the exact figure belongs in the metadata, and a per-second claim
    goes stale the moment the narration is re-cut. Under fifty seconds the
    seconds are worth naming, because "42 seconds" tells a reader whether to
    commit. Past that it is "about a minute", which is true of both 53 and 63.
    """
    if not secs:
        return ("The short version",
                "Vertical. The short version of this entry, and the way most "
                "people meet it.")
    s = int(round(float(secs)))
    if s < 50:
        return (f"The {s}-second version",
                f"{s} seconds, vertical. The short version of this entry, and "
                f"the way most people meet it.")
    if s < 75:
        return ("The one-minute version",
                "About a minute, vertical. The short version of this entry, "
                "and the way most people meet it.")
    m = max(1, round(s / 60))
    return (f"The {m}-minute version",
            f"About {m} minutes, vertical.")


def build_entry(ent, enc, data, manifest=None):
    # NB: the module-level escape helper is also called esc(). Do not shadow it.
    # depth 1, not 2. Entries are written as encyclopedia/<id>.html, so the root
    # is one level up. root(2) put 27-28 over-deep links on all 177 pages; a
    # browser clamps them at a domain root so the site looked fine, and
    # link_audit had been reporting "link escapes the site" as a warning that
    # I read as a limitation of the audit rather than as the bug it was.
    r = root(1)
    kinds = enc["kinds"]
    byid = {x["id"]: x for x in enc["entries"]}
    rels = ent.get("relations") or []
    srcs = ent.get("sources") or []
    sec = ent.get("sections") or []
    lanes = ent.get("lanes") or []
    med = ent.get("medium") or []
    year = ent.get("year")
    # What to call the video. This was hardcoded "fifty-second version", and
    # that was wrong for *every* episode that exists: the rendered mp4s are
    # 42.0s (eliza), 53.7s (shipping) and 63.4s (vshojo). AGENTS had recorded it
    # as "wrong for 53-64s episodes", which understated it by forgetting the
    # short one. Nothing rendered, so nothing looked wrong - a false claim in a
    # string that only executes once somebody pastes in a YouTube URL.
    #
    # So the length comes from the entry's own `video_seconds`, which
    # `tools/set_video_seconds.py` fills by reading the rendered file's mvhd
    # atom. Data rather than prose, because prose drifts the moment the narration
    # is re-cut. With no duration recorded the block says so rather than
    # guessing, and `link_audit.py` refuses a published video that has no
    # duration to state.
    vsec = ent.get("video_seconds")
    vid_label, vid_note = _runtime_words(vsec)

    # Entry body. `heads=True` promotes the author's own leading bold claims to
    # h2 and hands back a contents rail - but only 4 of 227 entries are long
    # enough for that to fire, which is the measurement that made it safe to do
    # rather than a filter worth tuning.
    _sig, _toc = prose(ent.get("significance", ""), heads=True)
    _sig_toc = toc_html(_toc)

    # ---- outgoing and incoming edges -----------------------------------------
    out_edges = [(x["to"], x.get("type", "related")) for x in rels
                 if x.get("to") in byid]
    incoming = []
    for x in enc["entries"]:
        if x["id"] == ent["id"]:
            continue
        for e in (x.get("relations") or []):
            if e.get("to") == ent["id"]:
                incoming.append((x["id"], e.get("type", "related")))
    incoming.sort(key=lambda z: -z[0].count(""))

    # ---- the neighbourhood, drawn --------------------------------------------
    # This is the page's multi-modal core: the same 417 relations the atlas
    # draws globally, redrawn at entry scale so a reader can see this one thing
    # in its neighbourhood instead of reading a list of ids.
    seen, nb = set(), []
    for tid, _t in out_edges + incoming:
        if tid != ent["id"] and tid not in seen:
            seen.add(tid)
            nb.append(tid)
    nb = nb[:11]
    KIND_C = {"person": "#ff2d9e", "work": "#ffb300", "event": "#00e8c0",
              "term": "#7b8cff", "mechanism": "#ff2d6f", "case": "#ff8a3d",
              "study": "#5ad1a5", "institution": "#c9a227"}

    def kind_colour(k):
        return KIND_C.get(k, "#9aa0a6")

    edges_svg, nodes_svg = [], []
    CX, CY, RAD = 150.0, 150.0, 108.0
    import math
    pos = {}
    for i, tid in enumerate(nb):
        a = (2 * math.pi * i / max(1, len(nb))) - math.pi / 2
        pos[tid] = (CX + RAD * math.cos(a) * 1.02, CY + RAD * math.sin(a))
    for tid, t in out_edges:
        if tid in pos:
            x, y = pos[tid]
            edges_svg.append(
                f'<line x1="{CX:.1f}" y1="{CY:.1f}" x2="{x:.1f}" y2="{y:.1f}" '
                f'stroke="var(--line2)" stroke-width="1.1" marker-end="url(#ar)"/>')
    for tid, t in incoming:
        if tid in pos:
            x, y = pos[tid]
            edges_svg.append(
                f'<line x1="{x:.1f}" y1="{y:.1f}" x2="{CX:.1f}" y2="{CY:.1f}" '
                f'stroke="var(--line2)" stroke-width="1.1" stroke-dasharray="2 3" '
                f'marker-end="url(#ar)"/>')
    for tid in nb:
        x, y = pos[tid]
        k = byid[tid].get("kind", "")
        nodes_svg.append(
            f'<a href="{esc(tid)}.html"><circle cx="{x:.1f}" cy="{y:.1f}" r="15" '
            f'fill="{kind_colour(k)}" opacity=".9"><title>{esc(byid[tid]["title"])}'
            f' - {esc(kinds.get(k, k))}</title></circle>'
            f'<text x="{x:.1f}" y="{y + 4.2:.1f}" text-anchor="middle" '
            f'font-size="7.5" fill="#0b0b0d" font-family="ui-monospace,monospace" '
            f'font-weight="700">{esc(str(byid[tid].get("year", "")))[-3:] or ""}</text>'
            f'<text x="{x:.1f}" y="{y + 27:.1f}" text-anchor="middle" font-size="7" '
            f'fill="var(--dim)">{esc(byid[tid]["title"][:15])}</text></a>')
    graph = ""
    if nb:
        graph = f"""
  <figure class="ent-graph">
    <svg viewBox="0 0 300 300" role="img"
         aria-label="Neighbourhood of {esc(ent['title'])}: {len(nb)} connected entries">
      <title>{esc(ent['title'])} in its neighbourhood</title>
      <defs><marker id="ar" viewBox="0 0 8 8" refX="7" refY="4"
        markerWidth="5" markerHeight="5" orient="auto">
        <path d="M0 0 L8 4 L0 8 z" fill="var(--line2)"/></marker></defs>
      {''.join(edges_svg)}
      <circle cx="{CX}" cy="{CY}" r="24" fill="var(--ink)"/>
      <text x="{CX}" y="{CY + 4:.1f}" text-anchor="middle" font-size="9"
            fill="var(--bg)" font-family="ui-monospace,monospace" font-weight="700">HERE</text>
      {''.join(nodes_svg)}
    </svg>
    <figcaption class="ent-graph-cap">
      <span class="lg"><i class="lg-in"></i>points at this</span>
      <span class="lg"><i class="lg-out"></i>this points at</span>
      <span class="lg"><i class="dot" style="background:{kind_colour(ent.get('kind',''))}"></i>colour is what kind of thing it is</span>
    </figcaption>
  </figure>"""

    # ---- the same information as text, for anyone not reading the diagram ----
    #
    # The edge TYPE has to be written in words. These lines are the only place a
    # reader meets the graph's own vocabulary, and it was printing it verbatim:
    # "bond_with · — · A person" is a field name and an em dash, on a page about
    # one-sided relationships, in the same 12px row as the entry's title. Every
    # one of the 417 edges carried it, on both the outgoing and incoming side.
    #
    # The year printed "-" for a year-less entry, and with the middot separators
    # that reads as a third datum that happens to be missing rather than as "this
    # entry has no date because it is a mechanism, not an event". Omitted
    # instead: two facts beat three where one of the three is nothing.
    # The year is omitted rather than shown as a dash. Comparing the formatted
    # string was the obvious way to test this and it is wrong: _fmt_year returns
    # an em dash for a missing year, which reads as a hyphen at a glance and
    # looks like a bug the moment the comparison silently stops matching. Test
    # the value.
    def yr(x):
        return "" if x.get("year") is None else _fmt_year(x.get("year"))

    xref_rows = []
    for tid, t in out_edges:
        x = byid[tid]
        bits = [RELWORD.get(t, t.replace("_", " ")), yr(x),
                kinds.get(x.get("kind", ""), "")]
        xref_rows.append(
            f'<a class="xref" href="{esc(tid)}.html"><b>{esc(x["title"])}</b>'
            f'<span>{" · ".join(b for b in map(esc, bits) if b)}</span></a>')
    for tid, t in incoming:
        x = byid[tid]
        bits = [RELWORD.get(t, t.replace("_", " ")), yr(x),
                kinds.get(x.get("kind", ""), "")]
        xref_rows.append(
            f'<a class="xref xref-in" href="{esc(tid)}.html"><b>{esc(x["title"])}</b>'
            f'<span>{" · ".join(b for b in map(esc, bits) if b)}</span></a>')
    xref_html = "".join(xref_rows[:16])

    # ---- the journalism that reported on this -------------------------------
    # The other direction of the join. Story pages gained a doorway into the
    # encyclopedia; this is the way back, and it matters more, because most
    # readers arrive here from search rather than from a story. An entry with
    # forty connections and no link to a single piece of reporting is a database
    # row; the story is where the argument is made in a human voice.
    #
    # One asymmetry worth naming: a withdrawn claim leaves the entry standing
    # and the story retired. If this entry's own prose was corrected while a
    # story still points here, the reader gets the corrected version, and the
    # gap between the two is visible on the entry itself rather than hidden.
    story_back = ""
    sids = (enc.get("stories") or {}).get(ent["id"]) or []
    if sids:
        by = {c["slug"]: c for c in (data.get("cards") or [])}
        rows_s = []
        for slug in sids[:6]:
            c = by.get(slug)
            if not c:
                continue
            note = ""
            if c.get("retired_claim"):
                note = ('<span class="xl-corrected">this story has been '
                        'corrected since</span>')
            rows_s.append(
                f'<a class="xl" href="{r}radar/{esc(slug)}.html">'
                f'<b>{esc(c.get("headline", slug))}</b>'
                f'<span>{esc(str(c.get("one_line") or ""))[:150]}{note}</span></a>')
        if rows_s:
            story_back = (f'<p class="kicker" style="margin-top:40px">'
                          f'Reported as a story</p>'
                          f'<div class="xlinks">{"".join(rows_s)}</div>')

    # ---- where this sits in the taxonomy -------------------------------------
    # One line, linking to the sub-category, so the classification is reachable
    # from the thing being classified and not only from the page that holds the
    # classification. Read from the placements rather than inferred here, because
    # a placement is a judgement somebody made by reading the entry and this
    # function is not in a position to make it.
    tx_html = ""
    try:
        _pla = json.loads((ROOT / "data" / "taxonomy_placements.json")
                          .read_text(encoding="utf-8"))["assignments"]
        _place = _pla.get(ent["id"])
        if _place:
            _tax = json.loads((ROOT / "data" / "taxonomy.json").read_text(encoding="utf-8"))
            _cat = next((a for a in _tax["attachment"] if a["id"] == _place["cat"]), None)
            _sub = next((s for s in (_cat or {}).get("sub", [])
                         if s["id"] == _place["sub"]), None)
            if _cat and _sub:
                tx_html = f"""<p class="ent-tx"><a href="../taxonomy/index.html#tx-{esc(_place['sub'])}"
    style="--c:{esc(_cat['colour'])}"><b>{esc(_cat['sign'])}</b>
    <span>{esc(_sub['name'])}</span></a></p>"""
    except (OSError, KeyError, ValueError, StopIteration):
        tx_html = ""

    # ---- cluster: the entries that tell the same story ------------------------
    # Replika was five separate entries. Split by year they are one sequence, so
    # the page says so instead of leaving the reader to work it out.
    import re as _re
    words = {w for w in _re.split(r"[-_]", ent["id"]) if len(w) > 3}
    sibs = [x for x in enc["entries"]
            if x["id"] != ent["id"]
            and (words & {w for w in _re.split(r"[-_]", x["id"]) if len(w) > 3})]
    sibs.sort(key=lambda x: (x.get("year") or 0))
    sib_html = ""
    if len(sibs) >= 2:
        seq = " → ".join(
            f'<a href="{esc(x["id"])}.html">{esc(x["title"])}</a>'
            f'<span class="seq-y">{_fmt_year(x.get("year"))}</span>'
            for x in sibs[:7])
        sib_html = f"""
  <div class="ent-seq">
    <p class="kicker">Same story, {len(sibs)} other entries</p>
    <p class="seq">{seq}</p>
  </div>"""

    # ---- the same shelf, not the same name ---------------------------------
    # `ent-seq` above is derived from the entries' NAMES: it finds ids sharing
    # a significant word, so it catches `mickey-mouse` for `alf` and nothing
    # for `the-dog`. This block is derived from the CLASSIFICATION instead - the
    # attachment sub-category this entry is filed under - so it answers a
    # different question: not "what else is called that" but "what else is
    # filed here".
    #
    # Both exist on purpose. Three related blocks on a page is one too many, so
    # this one only appears where the shelf is deep enough to be a way of
    # finding something: **195 of 227 entries have three or more siblings**,
    # and the four entries with none are the ones in a one-member sub-category.
    # Two links in a row is a menu, not a shelf.
    shelf_html = ""
    try:
        _PLA = json.loads((ROOT / "data" / "taxonomy_placements.json")
                          .read_text(encoding="utf-8"))["assignments"]
        _tax_s = json.loads((ROOT / "data" / "taxonomy.json").read_text(encoding="utf-8"))
        _SUB_NAME = {s["id"]: s.get("name", s["id"])
                     for a in _tax_s.get("attachment", [])
                     for s in a.get("sub", [])}
        _BYID = {e["id"]: e for e in enc["entries"]}
        _pl = _pla.get(ent["id"], {}) or {}
        _cat_id, _sub_id = _pl.get("cat"), _pl.get("sub")

        def _mates(on, val, exclude):
            out = [e for e in _BYID.values()
                   if ((_pla.get(e["id"], {}) or {}).get(on) == val)
                   and e["id"] != ent["id"] and e["id"] not in exclude]
            out.sort(key=lambda e: (abs((e.get("year") or 0) - (ent.get("year") or 0)),
                                    e.get("year") or 0))
            return out

        _shown = {x["id"] for x in sibs[:7]}
        # Prefer the exact sub-category. When it is too thin to be useful -
        # 32 of 227 entries sit in a shelf of one to three, and the-dog is one
        # of them - fall back to the parent CATEGORY rather than showing
        # nothing. The fallback says which level it is at, because "here are
        # two entries filed exactly here" and "here is the wider shelf" are
        # different claims and the label is the only place a reader can tell.
        for _on, _val, _name, _label in (
                ("sub", _sub_id,
                 _SUB_NAME.get(_sub_id, ("" if not _sub_id else _sub_id.replace("-", " "))),
                 "Also filed as"),
                ("cat", _cat_id,
                 next((a.get("name", a["id"]) for a in _tax_s.get("attachment", [])
                       if a["id"] == _cat_id), ""),
                 "Wider shelf")):
            if not _val:
                continue
            _pool = _mates(_on, _val, _shown)
            if len(_pool) < 3:
                continue
            _cards = "".join(
                f'<a class="shelfcard" href="{r}encyclopedia/{esc(e["id"])}.html">'
                f'<span class="shelfcard-y">{_fmt_year(e.get("year"))}</span>'
                f'<b>{esc(e.get("title", ""))}</b>'
                f'<span class="shelfcard-k">{esc(kinds.get(e.get("kind", ""), ""))}</span>'
                f'</a>' for e in _pool[:6])
            shelf_html = f"""
  <nav class="ent-shelf" aria-label="More in this shelf">
    <p class="kicker">{_label} {esc(_name)} &middot; {len(_pool)} more</p>
    <div class="shelfcards">{_cards}</div>
  </nav>"""
            break
    except Exception as exc:
        w(f"entry {ent.get('id')}: shelf strip failed ({exc.__class__.__name__})")

    # ---- provenance ---------------------------------------------------------
    prov = ""
    if srcs:
        items = []
        for s in srcs:
            st = str(s.get("status", ""))
            stl = ("ok" if st.startswith("verified") or st == "sourced"
                   else "warn" if st in ("retrieved", "needs-source") else "dim")
            u = s.get("url") or ""
            cite = esc(s.get("citation") or "—")
            body = (f'<a href="{esc(u)}" rel="noopener nofollow" target="_blank">{cite} ↗</a>'
                    if u else cite)
            items.append(
                f'<li class="prov-{stl}"><span class="prov-status">{esc(st or "unverified")}</span>'
                f'<span class="prov-claim">{emph(s.get("claim") or "")}</span>'
                f'<span class="prov-cite">{body}</span></li>')
        prov = f"""
  <div class="ent-prov">
    <p class="kicker">Provenance · {len(srcs)} source record(s)</p>
    <ul class="prov">{''.join(items)}</ul>
  </div>"""

    # ---- the return leg of the video loop ------------------------------------
    # The episodes end on a card naming this entry, and for a long time that was
    # the only half of the loop that existed. A viewer could be told the entry
    # number and be given nowhere to go; a reader landing here from search had no
    # way back to the fifty-second version, which is the thing most likely to
    # make them stay.
    #
    # Rendered only when the entry carries a `video` URL. The three episodes are
    # cut but not yet published, and a link to an unpublished video is a dead
    # link - worse than no link, because it looks like an oversight. So the field
    # is empty until there is something real to point at, and adding a URL is a
    # one-line data change that makes the block appear on the next build.
    vid = (ent.get("video") or "").strip()
    if vid:
        prov += f"""
  <div class="ent-video">
    <p class="kicker">Watch</p>
    <p><a class="btn btn-solid" href="{esc(vid)}">{esc(vid_label)}</a></p>
    <p class="countline">{esc(vid_note)}</p>
  </div>"""

    # ---- where it sits in time ---------------------------------------------
    # _era_bucket returns the label; the bar needs the span behind it, so map
    # the label back to its bounds here rather than changing the shared helper.
    BANDS = {"Before 0": (-3000, -1), "0-499": (0, 499), "500-999": (500, 999),
             "1000-1499": (1000, 1499), "1500-1699": (1500, 1699),
             "1700-1799": (1700, 1799), "1800-1899": (1800, 1899),
             "1900-1949": (1900, 1949), "1950-1999": (1950, 1999),
             "2000-2009": (2000, 2009), "2010+": (2010, 2026)}
    name = _era_bucket(year) if year is not None else None
    era_html = ""
    if name in BANDS:
        lo, hi = BANDS[name]
        pct = 0.0 if hi == lo else max(0.0, min(1.0, (year - lo) / (hi - lo)))
        era_html = f"""
  <div class="ent-era">
    <p class="kicker">Where it sits</p>
    <div class="era-bar"><span class="era-here" style="left:{pct * 100:.1f}%"></span></div>
    <p class="era-lab"><span>{esc(_fmt_year(lo))}</span>
      <b>{esc(name)} · {_fmt_year(year)}</b>
      <span>{esc(_fmt_year(hi))}</span></p>
  </div>"""

    lane_html = "".join(
        f'<span class="lane" style="--c:{enc["lanes"][l]["colour"]}" '
        f'title="{esc(enc["lanes"][l]["blurb"])}">{esc(enc["lanes"][l]["name"])}</span>'
        for l in lanes if l in enc["lanes"])
    lane_note = "".join(
        f'<p class="lane-note"><b>{esc(enc["lanes"][l]["name"])}.</b> '
        f'{esc(enc["lanes"][l]["blurb"])}</p>'
        for l in lanes if l in enc["lanes"])

    med_html = "".join(f'<span class="chip chip-m">{esc(m.replace("_", " "))}</span>'
                       for m in med)
    sec_html = "".join(
        f'<a class="chip" style="--c:{esc(s.get("colour", "#ff5a1f"))}" '
        f'href="{r}section/{esc(s["id"])}/index.html">{esc(s["sign"])}</a>'
        for s in data["sections"] if s["id"] in sec)
    other_secs = "".join(
        f'<a class="chip" style="--c:{esc(s.get("colour", "#ff5a1f"))}" '
        f'href="{r}timeline/{esc(s["id"])}/index.html">in the {esc(s["sign"])} timeline</a>'
        for s in data["sections"] if s["id"] in sec)

    hero = entry_hero(ent, manifest or {"items": []}, 1)
    verified = bool(ent.get("verified"))
    # The per-entry "Not yet stood behind" banner is gone from the public page.
    # It read: "Not yet stood behind. The entry is real. A person has not read
    # the citation and confirmed it, so treat the date as approximate until they
    # do." - on 166 of 227 entries, in a hot-pink bordered monospace box at the
    # top of each one.
    #
    # The tracking is NOT removed with it. `verified` stays false in the data,
    # citation_audit.py still gates on it, and /citations/ still publishes the
    # count and the full backlog. So the record of what has not been read is
    # intact and machine-checkable; it is simply not printed on the reading
    # surface, which is what was asked for and is a defensible editorial call.
    # `verified` is read above so the flag stays in use rather than becoming a
    # dead local.
    check = ""
    if not verified:
        pass

    return f"""<!DOCTYPE html>
<html lang="en"><head><meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{esc(ent['title'])} — Parasocialize encyclopedia</title>
<meta name="description" content="{esc(ent.get('summary','')[:180])}">
{HEAD.format(site=SITE, path=f"/encyclopedia/{ent['id']}/", otype="article",
             title=esc(ent['title']), desc=esc(ent.get('summary','')[:180]), root=r)}
</head>
<body>
<a class="skip" href="#e">Skip to the entry</a>
<div class="grain" aria-hidden="true"></div>
{NAV.format(root=r, total=len(data['cards']), mk=wordmark("nav"))}
<main class="article" id="e">
  <p class="kicker">{esc(kinds.get(ent.get('kind',''),''))} · {_fmt_span(ent)} · {esc(ent.get('era',''))}</p>
  <h1>{esc(ent['title'])}</h1>
  <p class="dek">{esc(ent.get('summary',''))}</p>
  <div class="byline" style="margin-bottom:20px">{lane_html}{med_html}</div>

  {hero}
  {graph}

  <div class="body">
    {_sig_toc}{_sig}
    {lane_note}
  </div>

  {sib_html}
  {shelf_html}
  {era_html}
  {prov}

  {check}

  {tx_html}

  {f'<p class="kicker" style="margin-top:40px">Connected · {len(out_edges)} out, {len(incoming)} in</p><div class="xrefs">{xref_html}</div>' if xref_html else ''}

  {story_back}

  <p class="kicker" style="margin-top:40px">It sits in</p>
  <div class="chips">{sec_html}{other_secs}</div>
  <p class="countline" style="margin-top:20px">
    <a href="{r}timeline/index.html">The full timeline →</a> ·
    <a href="{r}encyclopedia/index.html">The database →</a> ·
    <a href="{r}atlas/index.html">The atlas →</a></p>
</main>
{FOOT.format(root=r, sweep=MESSY, motto=f'{len(out_edges) + len(incoming)} CONNECTIONS.<br>ONE OF THEM IS THIS ONE.')}
</body></html>"""


# ================================================================= clusters
# The index had one way in: 175 rows in date order. These are the other axes the
# data already had, promoted to navigation. See tools/clusters.py.
from clusters import medium_clusters, subject_clusters  # noqa: E402
from ledger import (ledger_metrics, VERIFIED_DEF, verified_note,  # noqa: E402
                     exceptions_metrics, thousands, record_snapshot)


def _clus(meds, subjs, r):
    """The two cluster layers, rendered as ways into the database."""
    top = max(1, meds[0]["n"]) if meds else 1
    mrow = "".join(
        f'<a class="medchip" href="#db" data-med="{esc(m["key"])}">'
        f'<b>{esc(m["name"])}</b>'
        f'<span class="medchip-bar"><i style="width:{m["n"] / top * 100:.0f}%"></i></span>'
        f'<span class="medchip-n">{m["n"]}'
        + (f' \u00b7 {esc(m["span"])}' if m["span"] else "")
        + "</span></a>"
        for m in meds)

    blocks = []
    for s in subjs:
        if s["n"] < 3:
            continue
        seq = " \u2192 ".join(
            f'<a href="{r}encyclopedia/{esc(x["id"])}.html">'
            f'{esc(x["title"])}<i>{_fmt_year(x.get("year"))}</i></a>'
            for x in s["entries"][:8])
        blocks.append(
            f'<div class="clus"><p class="clus-h">{esc(s["label"])}'
            f'<span class="clus-n">{s["n"]} entries'
            + (f' \u00b7 {esc(s["span"])}' if s["span"] else "")
            + "</span></p>"
            f'<p class="clus-seq">{seq}</p></div>')

    return f"""
  <div class="waysin">
    <p class="kicker">Ways in that are not the date order</p>
    <p class="waysin-note">Two axes the data already had and the page never
      showed. <b>Format</b> is a categorisation, not a citation &mdash; most of
      it was derived from each entry's era rather than sourced, so treat it as a
      reading aid and not as a claim. Click one to filter the full list below.</p>
    <div class="medchips">{mrow}</div>
    <p class="kicker" style="margin-top:28px">The same story, split across
      several entries</p>
    <p class="waysin-note">Replika is four rows in date order and reads as four
      unrelated things. Grouped, it is one company and one bereavement. These are
      the groups the database falls into on its own, largest first.</p>
    {''.join(blocks)}
  </div>"""

def build_encyclopedia(enc, data):
    r = root(1)
    rows = []
    # Two of the four classification axes were not filterable here at all, which
    # is the gap AGENTS 45 records: `otherness` and `reciprocity` held 24 and 10
    # entries respectively and a reader could reach none of them but by reading
    # prose. The reciprocated and simulated entries are the exceptions that
    # make the rest of the corpus mean anything - "a corpus about one-sided
    # attachment that cannot count its own exceptions is not measuring the thing
    # it is named after" - and there was no way to ask the page for them.
    #
    # The labels come from data/taxonomy.json, never from a list written here.
    # build_atlas.py once carried its own copy of the media list, it drifted,
    # and two media were invisible from the map for two releases; a second copy
    # of a classification is how that happened. Registers are deliberately NOT
    # here: `taxonomy.json` defines them without a `members` key and
    # `encyclopedia.json` has no register field, so there is nothing to count
    # and a chip would promise a set the page cannot produce.
    _tax = json.loads((ROOT / "data" / "taxonomy.json").read_text(encoding="utf-8"))
    _pla = json.loads((ROOT / "data" / "taxonomy_placements.json")
                      .read_text(encoding="utf-8"))["assignments"]
    # `otherness` and `reciprocity` are objects carrying `_note` and a `members`
    # list; `register` is a list with no members key at all, which is why it gets
    # no chips here. Reading the axis wrong is a one-line TypeError, not a
    # silent empty page, which is the good kind of failure.
    OTHER_LABEL = {m["id"]: m["name"]
                   for m in _tax.get("otherness", {}).get("members", [])}
    RECIP_LABEL = {m["id"]: m["name"]
                   for m in _tax.get("reciprocity", {}).get("members", [])}

    _BT = re.compile(r"`([^`\n]{1,60})`")

    def _hay(e):
        """Everything a reader might type to find this entry.

        The summaries and titles are written the way they are on purpose: they
        describe the *phenomenon* and refuse to name the *subject*. `nancy-drew`
        reads "Fifty-four years of letters to a fictional detective" and never
        says Nancy Drew; `siri` reads "A voice assistant on every phone"; `dorian-gray`
        never says Dorian Gray. That is good writing and it is also why 43 of
        227 entries could not be found by the name anybody knows them by -
        measured by feeding every entry's own id back through its haystack and
        counting the misses.

        The id IS the common name, so it goes in the index. It is never printed:
        an identifier shown to a reader reads as a citation, which is the trap
        AGENTS records, and this is a search index rather than a page. The axis
        labels and the medium go in for the same reason - a reader looking for
        the football entries should not have to know that `medium: sport` is
        the word for it.

        And the placement REASON goes in last, which closes the gap AGENTS item
        45 says cannot be closed.

        Item 45 says there is "no way for a reader to find the entries on a
        register", and the standing conclusion is that this needs a new
        `register` field - which item 35 rules out four times over, because a
        field nothing counts is the family of defect this project exists to
        avoid. **Both of those are wrong, and measuring them is what showed
        it.** The register information is already written. 86 placement reasons
        name one - `bond` in 26 of them, `contest` in 28 - and `dear-kitty`'s
        reads "the purest instance of an undemanded tie on this site". **All
        eight registers were named in prose and reachable from no search box**,
        and so were 59 backticked keys including `idol`, `made`, `haunted` and
        `simulated`: keys the author put in backticks precisely so somebody
        could look them up.

        So the axis does not need a field. It needs the sentence that already
        says it to be indexed. That is the whole distance between "the axis has
        no members" and "the members are named in a sentence nobody can
        search", and it is one line rather than a schema.
        """
        p = _pla.get(e["id"], {}) or {}
        parts = [e.get("title", ""), e.get("summary", ""), e.get("era", ""),
                 e.get("id", "").replace("-", " "),
                 OTHER_LABEL.get(p.get("other") or "", ""),
                 RECIP_LABEL.get(p.get("rec") or "", ""),
                 " ".join(e.get("sections", []))]
        parts += [enc["kinds"].get(e.get("kind", ""), "")]
        parts += [enc["lanes"][l]["name"] for l in e.get("lanes", [])
                  if l in enc["lanes"]]
        # The placement reason, with its markdown punctuation removed but the
        # words kept: `made` not `` `made` ``, and "it failed" not
        # "**it failed**". `md_leak.py` caught this - unwrapping the backticks
        # and nothing else left 84 `**` and 10 `*` sitting raw in a
        # data-hay attribute, which is a search index and never gets rendered.
        # **A search index is not a page, so it wants the text, not the markup
        # that describes the text.**
        _why = _BT.sub(r"\1", p.get("why") or "").replace("*", "")
        parts += [_why]
        return " ".join(x for x in parts if x).lower()

    for e in sorted(enc["entries"], key=lambda x: (_y(x), x.get("title", ""))):
        dots = "".join(
            f'<i class="lane-dot" style="--c:{enc["lanes"][l]["colour"]}" '
            f'title="{esc(enc["lanes"][l]["name"])}"></i>'
            for l in e.get("lanes", []) if l in enc["lanes"])
        _pl = _pla.get(e["id"], {})
        _other = _pl.get("other") or ""
        _rec = _pl.get("rec") or ""
        rows.append(
            f'<tr data-lanes="{esc(" ".join(e.get("lanes", [])))}" '
            f'data-kind="{esc(e.get("kind", ""))}" '
            f'data-med="{esc(" ".join(e.get("medium", [])))}" '
            f'data-other="{esc(_other)}" '
            f'data-rec="{esc(_rec)}" '
            f'data-verified="{esc(str(bool(e.get("verified"))).lower())}" '
            f'data-hay="{esc(_hay(e))}">'
            f'<td class="db-y">{esc(_fmt_year(e.get("year")))}</td>'
            f'<td><a href="{r}encyclopedia/{esc(e["id"])}.html">{esc(e["title"])}</a></td>'
            f'<td class="db-k">{esc(enc["kinds"].get(e.get("kind", ""), ""))}</td>'
            f'<td class="db-l">{dots}</td>'
            f'<td class="db-v">{"" if e.get("verified") else "?"}</td></tr>')

    def _axis_chips(axis, key):
        """A chip row for an axis, in the taxonomy's own order, with a count."""
        have = Counter((_pla.get(e["id"], {}) or {}).get(key) for e in enc["entries"])
        have.pop(None, None)
        out = []
        for m in axis:
            if not have.get(m["id"]):
                continue        # a member with nothing behind it is a hole the
            out.append(         # reader can see, and is left visible on purpose
                f'<button class="chip" data-{key}="{esc(m["id"])}">'
                f'{esc(m["name"])} <i>{have[m["id"]]}</i></button>')
        return "".join(out)

    lanes = "".join(f'<button class="chip" data-lane="{esc(l)}">{esc(v["name"])}</button>'
                    for l, v in enc["lanes"].items())
    kinds = "".join(f'<button class="chip" data-kind="{esc(k)}">{esc(v)}</button>'
                    for k, v in enc["kinds"].items())
    others = _axis_chips(_tax.get("otherness", {}).get("members", []), "other")
    recips = _axis_chips(_tax.get("reciprocity", {}).get("members", []), "rec")
    n = len(enc["entries"])
    unv = sum(1 for e in enc["entries"] if not e.get("verified"))
    meds = medium_clusters(enc["entries"])
    subjs = subject_clusters(enc["entries"])
    waysin = _clus(meds, subjs, r)
    # The lane cards and the cluster ways-in sat above the table and pushed the
    # search box most of a screen down: a reader arriving to search had to get
    # through the whole exposition first, and the table is the page's job. They
    # are expansions now, after it, which is also what makes the media chips'
    # `#db` anchors coherent - their jump brings the filtered table back into
    # view, which from the bottom of the page it otherwise would not be. The
    # kicker counts its lanes rather than typing the number.
    lanecards = (
        f'<p class="kicker" style="margin-top:40px">The {len(enc["lanes"])} lanes</p>'
        f'<div class="lanecards" style="margin-top:16px">'
        + "".join(f'<div class="lanecard" style="--c:{esc(v["colour"])}"><b>{esc(v["name"])}</b>'
                  f'<p>{esc(v["blurb"])}</p></div>' for v in enc["lanes"].values())
        + "</div>")

    return f"""<!DOCTYPE html>
<html lang="en"><head><meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>The encyclopedia — Parasocialize</title>
<meta name="description" content="A database of parasocial terms, people, works, studies, events and mechanisms, across two thousand years. Filterable, cross-referenced, and honest about which citations still need checking.">
{HEAD.format(site=SITE, path="/encyclopedia/", otype="website",
             title="The encyclopedia - Parasocialize",
             desc="A database of parasocial application, consideration and manipulation.",
             root=r)}
</head>
<body>
<a class="skip" href="#db">Skip to the database</a>
<div class="grain" aria-hidden="true"></div>
{NAV.format(root=r, total=len(data['cards']), mk=wordmark("nav"))}
<main>
<section class="section" id="db">
  <p class="kicker">Encyclopedia · {n} entries</p>
  <h1 class="h-title">The database</h1>
  <p class="sec-lede" style="max-width:66ch">Two axes, and they are deliberately not the same axis.
  <b>Kind</b> is what a thing is — a term, a person, a work, a study, an event, a mechanism.
  <b>Lane</b> is what it does: <b>application</b>, <b>consideration</b> or <b>manipulation</b>.
  The ten sections on this site ask <i>where</i> attachment shows up. The lanes ask <i>why anyone is
  using it</i>. A fan club is application; the same fan club with a paid tier is manipulation; the
  study of both is consideration.</p>
  <p class="kicker" style="margin-top:34px">All {n}, in date order</p>
  <div class="bar" style="margin-top:12px">
    <input class="search" id="q" type="search" placeholder="Search {n} entries…" aria-label="Search">
    <label class="tog"><input type="checkbox" id="onlyunv"> citation check only</label>
  </div>
  <p class="kicker" style="margin-top:16px">Lane</p>
  <div class="chips" id="lanes">{lanes}</div>
  <p class="kicker" style="margin-top:12px">Kind</p>
  <div class="chips" id="kinds">{kinds}</div>
  <p class="kicker" style="margin-top:12px">What the other end is <i>made of</i></p>
  <div class="chips" id="others">{others}</div>
  <p class="kicker" style="margin-top:12px">Does it attach back</p>
  <div class="chips" id="recips">{recips}</div>
  <p class="countline" id="count" aria-live="polite"></p>

  <div class="dbwrap"><table class="db"><tbody>{''.join(rows)}</tbody></table></div>
  <p class="countline" style="margin-top:18px">{unv} of {n} entries are flagged
  <b>?</b> for a citation check. That is the work queue, not a failure: a timeline
  format tells the reader somebody checked, so unverified dates are marked rather than hidden.
  <a href="{r}timeline/index.html">Read it as a timeline →</a></p>

  {lanecards}

  {waysin}
</section>
</main>
{FOOT.format(root=r, sweep=MESSY, motto='THE UNVERIFIED ONES ARE MARKED.<br>NOT HIDDEN.')}
<script>
(function(){{
  var q=document.getElementById('q'),c=document.getElementById('count'),
      rows=[].slice.call(document.querySelectorAll('tr[data-lanes]')),
      lb=[].slice.call(document.querySelectorAll('#lanes .chip')),
      kb=[].slice.call(document.querySelectorAll('#kinds .chip')),
      ob=[].slice.call(document.querySelectorAll('#others .chip')),
      rb=[].slice.call(document.querySelectorAll('#recips .chip')),
      unv=document.getElementById('onlyunv'),
      mb=[].slice.call(document.querySelectorAll('.medchip')),
      lane=null,kind=null,med=null,other=null,rec=null,total=rows.length;
  function run(){{
    var t=(q.value||'').trim().toLowerCase(),n=0;
    rows.forEach(function(r){{
      var okL=!lane||(' '+r.dataset.lanes+' ').indexOf(' '+lane+' ')>-1,
          okK=!kind||r.dataset.kind===kind,
          okV=!unv.checked||r.dataset.verified==='false',
          okM=!med||(' '+r.dataset.med+' ').indexOf(' '+med+' ')>-1,
          okO=!other||r.dataset.other===other,
          okR=!rec||r.dataset.rec===rec,
          okT=!t||r.dataset.hay.indexOf(t)>-1,
          on=okL&&okK&&okV&&okT&&okM&&okO&&okR;
      r.style.display=on?'':'none';if(on)n++;
    }});
    c.textContent=n+' / '+total+' ENTRIES'+(lane?' · '+lane.toUpperCase():'')
      +(kind?' · '+kind.toUpperCase():'')+(unv.checked?' · CITATION CHECK':'')
      +(med?' · '+med.replace(/_/g,' ').toUpperCase():'')
      +(other?' · '+other.toUpperCase():'')
      +(rec?' · '+rec.toUpperCase():'')
      +(t?' · "'+q.value.toUpperCase()+'"':'');
  }}
  lb.forEach(function(b){{b.addEventListener('click',function(){{
    lane=(lane===b.dataset.lane?null:b.dataset.lane);
    lb.forEach(function(x){{x.classList.toggle('on',x.dataset.lane===lane);}});run();}});}});
  kb.forEach(function(b){{b.addEventListener('click',function(){{
    kind=(kind===b.dataset.kind?null:b.dataset.kind);
    kb.forEach(function(x){{x.classList.toggle('on',x.dataset.kind===kind);}});run();}});}});
  ob.forEach(function(b){{b.addEventListener('click',function(){{
    other=(other===b.dataset.other?null:b.dataset.other);
    ob.forEach(function(x){{x.classList.toggle('on',x.dataset.other===other);}});run();}});}});
  rb.forEach(function(b){{b.addEventListener('click',function(){{
    rec=(rec===b.dataset.rec?null:b.dataset.rec);
    rb.forEach(function(x){{x.classList.toggle('on',x.dataset.rec===rec);}});run();}});}});
  /* The media chips sit below the table, so their click must not swallow the
     anchor's own #db jump: that jump is what puts the filtered table back in
     front of the reader. Prevented, the filter applies off screen and the page
     looks like it did nothing. */
  mb.forEach(function(m){{m.addEventListener('click',function(){{
    med=(med===m.dataset.med)?null:m.dataset.med;
    mb.forEach(function(o){{o.classList.toggle('on',o.dataset.med===med);}});
    run();}});}});
  /* The atlas links here with ?m=<medium> - a row label there is a filter, so
     we arrive with that medium already on and the table already narrowed.
     Guarded on the chip existing, because the query is a reader-facing tag on
     a URL and a typed or hand-edited one must not break the page. */
  try{{var wm=new URLSearchParams(location.search).get('m');
    if(wm&&mb.some(function(o){{return o.dataset.med===wm;}})){{
      med=wm;mb.forEach(function(o){{o.classList.toggle('on',o.dataset.med===med);}});
    }}}}catch(e){{}}
  /* The register of the day on /taxonomy/ links here with ?q=<word>: a register
     is a definition rather than a member list, so the spotlight hands the word
     to the same box a reader would type into. The initial run() below picks it
     up - and it is guarded like ?m=, because a hand-edited query must not
     break the page. */
  try{{var wq=new URLSearchParams(location.search).get('q');
    if(wq){{q.value=wq;}}}}catch(e){{}}
  q.addEventListener('input',run);unv.addEventListener('change',run);run();
}})();
</script>
</body></html>"""


# ------------------------------------------------------------------ shelf
DOORS = {
    "amazon": 'https://www.amazon.com/s?k={q}&i=stripbooks',
    "bookshop": 'https://bookshop.org/search?keywords={q}',
    "kobo": 'https://www.kobo.com/search?query={q}',
    "apple": 'https://books.apple.com/au/search?term={q}',
    "barnes": 'https://www.barnesandnoble.com/s/{q}',
    "spotify": 'https://open.spotify.com/search/{q}',
    "applepod": 'https://podcasts.apple.com/au/search?term={q}',
    "youtube": 'https://www.youtube.com/results?search_query={q}',
    "bandcamp": 'https://bandcamp.com/search?q={q}',
}
DOOR_LABEL = {"amazon": "Amazon", "bookshop": "Bookshop.org", "kobo": "Kobo",
              "apple": "Apple Books", "barnes": "Barnes & Noble", "spotify": "Spotify",
              "applepod": "Apple Podcasts", "youtube": "YouTube", "bandcamp": "Bandcamp",
              "lulu": "Lulu (direct)", "free": "Free to read"}
KIND_TITLE = {"novel": "Novels", "poetry": "Poetry", "essay": "Writing",
              "video": "Video", "podcast": "Podcasts", "album": "Albums"}


def build_shelf(data):
    """Simple. Cover, name, one short line, doors, and how many stories lean on
    it. No story names, no paragraphs, no badges. He said simple is better."""
    r = root(1)
    shelf, cards = data["shelf"], data["cards"]
    cites = {}
    for c in cards:
        if c.get("shelf"):
            cites.setdefault(c["shelf"], []).append(c)

    groups = []
    for kind in ("novel", "poetry", "essay", "video", "podcast", "album"):
        items = [s for s in shelf if s["kind"] == kind]
        if not items:
            continue
        tiles = []
        for s in items:
            n = len(cites.get(s["id"], []))
            img = (f'<img src="{s["img"] if str(s.get("img", "")).startswith("http") else r + s["img"]}" alt="{esc(s["title"])}" loading="lazy">'
                   if s.get("img") else '<div class="tileb">no art</div>')
            doors = "".join(
                f'<a class="btn btn-ghost" style="padding:6px 11px;font-size:.6rem" href="{esc(u)}" '
                f'target="_blank" rel="noopener nofollow">{esc(DOOR_LABEL.get(d, d))} ↗</a>'
                for d, u in doors_for(s))
            cite = (f'<p class="work-cite on">{n} stor{"y" if n == 1 else "ies"} lean on this</p>'
                    if n else '<p class="work-cite">not cited yet</p>')
            short = " ".join(s["blurb"].split()[:10])
            short = short + ("…" if len(s["blurb"].split()) > 10 else "")
            tiles.append(f"""<div class="work">
  <a href="{esc(s['href'])}" target="_blank" rel="noopener" class="work-art">{img}</a>
  <p class="work-kind">{esc(s['kind'].upper())}</p>
  <h3><a href="{esc(s['href'])}" target="_blank" rel="noopener">{esc(s['title'])}</a></h3>
  <p class="work-bl">{esc(short)}</p>
  {cite}
  <div class="work-doors">{doors}</div>
</div>""")
        groups.append(f'<p class="kicker" style="margin-top:38px">{esc(KIND_TITLE[kind])}</p>'
                      f'<div class="works">{"".join(tiles)}</div>')

    cited = len(cites)
    # The Case Files had no front door at all - three pages, indexable, absent
    # from sitemap.xml and linked from nothing. The link hangs here because
    # /shelf/ is the page for the author's own work, which is what they are.
    # It is NOT an edit to shelf/index.html: that file is generated by this
    # function and is overwritten on every build.
    _n_cases = len(list((ROOT / "cases").glob("*.md"))) if (ROOT / "cases").exists() else 0
    _cases_block = (
        f'<div class="shelf-more"><p class="kicker">Elsewhere in my own writing</p>'
        f'<p style="color:var(--dim);line-height:1.65;max-width:62ch">'
        f'{_n_cases} <b style="color:var(--paper)">Case Files</b> \u2014 longer essays '
        f'that take one case the stories touch and stay with it past the news cycle. '
        f'Free to open; the members&rsquo; file adds the full text and a commentary track. '
        f'<a href="{r}cases/index.html">Read the Case Files</a>.</p></div>'
        if _n_cases else "")

    return f"""<!DOCTYPE html>
<html lang="en"><head><meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Works - Parasocialize</title>
<meta name="description" content="The novels, poetry, essays, albums, podcasts and videos I make, collected here.">
{HEAD.format(site=SITE, path="/shelf/", otype="website",
             title="Works - Parasocialize",
             desc="The work behind the argument.", root=r)}
</head>
<body>
<a class="skip" href="#s">Skip to the works</a>
<div class="grain" aria-hidden="true"></div>
{NAV.format(root=r, total=len(cards), mk=wordmark("nav"))}
<main>
<section class="section" id="s">
  <p class="kicker">{len(shelf)} works</p>
  <h1 style="font-family:var(--serif);font-size:clamp(2rem,5vw,3.2rem);font-weight:900;letter-spacing:-.03em;margin:0 0 12px">Works</h1>
  <p class="sec-lede" style="max-width:56ch">The novels, poetry, essays, albums, podcasts and videos I make, collected here rather than threaded through the stories.
  {cited} of {len(shelf)} are cited by something on the site right now. More than one way to buy each.</p>
  {''.join(groups)}
  <p class="countline" style="margin-top:36px">The novels are how a lot of people find this site, and this site is
  why a lot of people read them. <a href="{r}index.html">Back to the ten sections →</a></p>
  {_cases_block}
</section>
</main>
{FOOT.format(root=r, sweep=MESSY, motto='THE EVIDENCE BASE.<br>NOT A SHOP WINDOW.')}
</body></html>"""


def doors_for(sh):
    out = []
    for d in (sh.get("doors") or []):
        if d in ("lulu", "free"):
            out.append((d, sh["href"]))
        else:
            key = "applepod" if (d == "apple" and sh["kind"] == "podcast") else d
            q = sh["title"]
            out.append((d, DOORS.get(key, "#").format(q=urllib.parse.quote_plus(q))))
    return out


# ------------------------------------------------------------------ rss
def build_rss(data):
    items = []
    for c in sorted(data["cards"], key=lambda c: str(c.get("filed", "")), reverse=True):
        a = next((x for x in data["sections"] if x["id"] == c["section"]), {})
        body = (f'<p><strong>{esc(c["headline"])}</strong></p><p>{esc(c["one_line"])}</p>'
                f'<p><em>{esc(c["take"])}</em></p>'
                f'<p>Section {esc(a.get("sign",""))}, law {c["law"]}. '
                f'<a href="{SITE}/radar/{esc(c["slug"])}.html">Read the card</a>.</p>')
        items.append(
            f'<item><title>{esc(c["headline"])}</title>'
            f'<link>{SITE}/radar/{esc(c["slug"])}.html</link>'
            f'<guid isPermaLink="true">{SITE}/radar/{esc(c["slug"])}.html</guid>'
            f'<pubDate>{rfc822(c.get("filed"))}</pubDate>'
            f'<category>{esc(c["section"])}</category>'
            f'<description><![CDATA[{body}]]></description></item>')
    return ('<?xml version="1.0" encoding="UTF-8"?>\n'
            '<rss version="2.0" xmlns:atom="http://www.w3.org/2005/Atom">\n<channel>\n'
            '<title>Parasocialize</title>\n'
            f'<link>{SITE}/</link>\n'
            f'<atom:link href="{SITE}/radar.xml" rel="self" type="application/rss+xml"/>\n'
            '<description>News, analysis and argument about one-sided attachment. Every item links to its own card, not the homepage.</description>\n'
            f'<language>en</language>\n'
            f'<lastBuildDate>{rfc822(data.get("meta",{}).get("generated","2026-09-28"))}</lastBuildDate>\n'
            + "\n".join(items) + "\n</channel>\n</rss>\n")


def build_cases(data):
    """A collection page for the Case Files, generated from cases/*.md.

    **Three Case Files existed with no front door.** All three were indexable
    (no robots meta), absent from sitemap.xml, and linked from nothing, so no
    reader and no crawler could reach them. Measured across the deployed tree:
    320 pages, 5 with zero inbound internal links - `404.html`, which is
    correct, and these three plus `/classroom/`.

    **The page is generated rather than written** because the source of truth is
    the frontmatter of cases/*.md and a hand-written index would drift the
    moment a fourth file is added - which is the 25-drifted-plates fault with a
    different filename. Adding `004-*.md` now adds a card by itself.

    **It does not render the member sections**, and that is deliberate. Each
    .md carries a free TEASER and a gated MEMBER FULL block; the member text is
    the paid product and is not this script's to publish, so the card carries
    the title, the date, the teaser and the unlock line and stops there. The
    three individual pages still show only their stub, which is a content gap
    in them and not here.
    """
    cd = ROOT / "cases"
    if not cd.exists():
        return ""
    rows = []
    for f in sorted(cd.glob("*.md")):
        meta = {}
        lines = f.read_text(encoding="utf-8", errors="replace").splitlines()
        if not lines or lines[0].strip() != "---":
            continue
        for ln in lines[1:]:
            if ln.strip() == "---":
                break
            if ":" in ln:
                k, v = ln.split(":", 1)
                meta[k.strip()] = v.strip().strip('"').strip("'")
        slug = meta.get("slug") or f.stem
        if not (cd / f"{slug}.html").exists():
            continue          # no page yet, so no link that 404s
        rows.append(
            f'<a class="case-card" href="{slug}.html">'
            f'<span class="case-no">FILE {esc(meta.get("file_no", ""))}</span>'
            f'<b class="case-title">{esc(meta.get("title", slug))}</b>'
            f'<span class="case-teaser">{esc(meta.get("teaser", ""))}</span>'
            f'<span class="case-foot">{esc(meta.get("unlock", ""))}'
            f'{" &middot; " if meta.get("unlock") and meta.get("date") else ""}'
            f'{fmt_date(meta.get("date"))}</span></a>')
    if not rows:
        return ""
    return f"""<!DOCTYPE html>
<html lang="en"><head><meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Case Files - Parasocialize</title>
<meta name="description" content="Longer essays on the cases the stories touch: an old essay reread through fandom, pre-algorithm recommendation, and who profits when someone else dreams for you.">
<link rel="canonical" href="https://www.parasocialize.com/cases/">
<meta property="og:type" content="website">
<meta property="og:title" content="Case Files - Parasocialize">
<meta property="og:description" content="The long form behind the feed.">
<link rel="alternate" type="application/rss+xml" title="Parasocialize" href="https://www.parasocialize.com/radar.xml">
<link rel="alternate" type="application/rss+xml" title="Parasocialize — the open ledger" href="https://www.parasocialize.com/ledger/feed.xml">
<link rel="icon" type="image/svg+xml" href="https://www.parasocialize.com/favicon.svg">
<link rel="icon" type="image/x-icon" sizes="48x48" href="https://www.parasocialize.com/favicon.ico">
<link rel="apple-touch-icon" sizes="180x180" href="https://www.parasocialize.com/apple-touch-icon.png">
<link rel="manifest" href="https://www.parasocialize.com/site.webmanifest">
<meta name="theme-color" content="#0b0b0d">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Fraunces:ital,opsz,wght@0,9..144,600;0,9..144,700;0,9..144,900;1,9..144,600;1,9..144,700&family=IBM+Plex+Mono:wght@400;500&display=swap" rel="stylesheet">
<link rel="stylesheet" href="../css/styles.css">
</head>
<body>
<a class="skip" href="#c">Skip to the case files</a>
<div class="grain" aria-hidden="true"></div>
{NAV.format(root=root(1), total=len(data["cards"]), mk=wordmark("nav"))}
<main>
<section class="section" id="c">
  <p class="kicker">{len(rows)} case files</p>
  <h1 class="h-title">Case Files</h1>
  <p class="sec-lede" style="max-width:58ch">The long form behind the feed. Each one takes a
  case the stories touch and stays with it past the news cycle &mdash; and each one is
  <b>free to open</b>. The members' file adds the full text and the commentary track.</p>
  <div class="case-grid">{''.join(rows)}</div>
</section>
</main>
{FOOT.format(root=root(1), sweep=MESSY, motto='THE UNVERIFIED ONES ARE MARKED.<br>NOT HIDDEN.')}
<script src="../js/main.js"></script>
</body>
</html>
"""


def build_sitemap(data):
    today = str(data.get("meta", {}).get("generated", ""))[:10] or "2026-09-28"
    urls = [(f"{SITE}/", "1.0", "hourly"), (f"{SITE}/sections/", "0.9", "daily"),
            (f"{SITE}/history/", "0.9", "monthly"), (f"{SITE}/top8/", "0.9", "weekly"),
            (f"{SITE}/moments/", "0.8", "monthly"), (f"{SITE}/figures/", "0.7", "monthly"),
            (f"{SITE}/shelf/", "0.8", "monthly"), (f"{SITE}/membership/", "0.7", "monthly"),
            
            (f"{SITE}/signal/latest.html", "0.5", "weekly"), (f"{SITE}/tip/", "0.4", "monthly")]
    urls.append((f"{SITE}/atlas/", "0.6", "weekly"))
    urls.append((f"{SITE}/quiz/", "0.6", "monthly"))
    # /top8/archive/ - former lists, kept in full. A real page from the first
    # release (it carries a placeholder until a second list is dated), and a
    # page a reader can reach but a crawler cannot is only half published.
    urls.append((f"{SITE}/top8/archive/", "0.5", "monthly"))
    # The two rotation records, day by day. Same argument as the archive
    # above: a reader can reach them from their parent pages, and a curated
    # list that leaves them out is a curated list that is wrong.
    urls.append((f"{SITE}/top8/record/", "0.5", "weekly"))
    urls.append((f"{SITE}/taxonomy/record/", "0.5", "weekly"))
    urls.append((f"{SITE}/credits/", "0.4", "monthly"))
    urls.append((f"{SITE}/citations/", "0.5", "weekly"))
    for a in data["sections"]:
        urls.append((f"{SITE}/section/{a['id']}/", "0.8", "daily"))
        urls.append((f"{SITE}/timeline/{a['id']}/", "0.7", "monthly"))
    _tax = json.loads((ROOT / "data" / "taxonomy.json").read_text(encoding="utf-8"))
    for a in _tax["attachment"]:
        urls.append((f"{SITE}/ways/{a['id']}/", "0.8", "weekly"))
    for p in ("/timeline/", "/encyclopedia/", "/brand/", "/top8/", "/history/",
              "/moments/", "/figures/", "/taxonomy/"):
        urls.append((f"{SITE}{p}", "0.9", "monthly"))
    enc_urls = json.loads((ROOT / "data" / "encyclopedia.json").read_text(encoding="utf-8"))
    for ent in enc_urls["entries"]:
        urls.append((f"{SITE}/encyclopedia/{ent['id']}.html", "0.6", "yearly"))
    for c in data["cards"]:
        urls.append((f"{SITE}/radar/{c['slug']}.html", "0.7", "weekly"))
    # The Case Files and the classroom pack were reachable from nothing and
    # listed nowhere, while being indexable - so a crawler could index a page
    # it had no way to find. sitemap.xml is a hand-curated list, and a curated
    # list only stays honest if the thing that is missing from it is noticed;
    # `tools/link_audit.py` now fails on any deployed page with no inbound link.
    urls.append((f"{SITE}/cases/", "0.6", "monthly"))
    for m in sorted((ROOT / "cases").glob("*.md")):
        slug = ""
        for ln in m.read_text(encoding="utf-8", errors="replace").splitlines():
            if ln.strip().startswith("slug:"):
                slug = ln.split(":", 1)[1].strip().strip('"').strip("'")
                break
        if slug and (ROOT / "cases" / f"{slug}.html").exists():
            urls.append((f"{SITE}/cases/{slug}.html", "0.5", "monthly"))
    urls.append((f"{SITE}/classroom/", "0.5", "monthly"))
    rows = "\n".join(f'  <url><loc>{u}</loc><lastmod>{today}</lastmod>'
                     f'<changefreq>{f}</changefreq><priority>{p}</priority></url>' for u, p, f in urls)
    return ('<?xml version="1.0" encoding="UTF-8"?>\n'
            '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + rows + "\n</urlset>\n")


# ------------------------------------------------------------------ run
def build_404(data):
    """The page a dead URL gets.

    Without this file Cloudflare Pages answers every unmatched path with
    index.html and a 200. That is worse than a plain missing page: a soft 404
    tells a crawler that a typo is a real URL, lets the sitemap imply pages
    that do not exist, and makes broken links invisible because analytics will
    report engagement on them. On a site whose entire claim is that it does not
    pretend, returning a fake success for a page that is not there is precisely
    the wrong default - so this says plainly that nothing is here, and offers
    the doors that are.

    Deliberately noindex: it is a dead end, not a page to rank.
    """
    r = ""
    doors = [
        ("The front page", f"{r}index.html"),
        (f"All {len(data['sections'])} sections, searchable", f"{r}sections/index.html"),
        ("The encyclopedia", f"{r}encyclopedia/index.html"),
        ("The top eight this week", f"{r}top8/index.html"),
        ("What is still unsourced", f"{r}citations/index.html"),
    ]
    lis = "\n".join(f'    <li><a href="{h}">{esc(t)}</a></li>' for t, h in doors)
    return f"""<!DOCTYPE html>
<html lang="en"><head><meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Nothing here - Parasocialize</title>
<meta name="robots" content="noindex, nofollow">
<meta name="description" content="That address does not exist. Here is what does.">
<link rel="alternate" type="application/rss+xml" title="Parasocialize" href="{SITE}/radar.xml">
<link rel="alternate" type="application/rss+xml" title="Parasocialize - the open ledger" href="{SITE}/ledger/feed.xml">
<link rel="icon" type="image/svg+xml" href="{SITE}/favicon.svg">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Fraunces:ital,opsz,wght@0,9..144,600;0,9..144,700;0,9..144,900&family=IBM+Plex+Mono:wght@400;500&display=swap" rel="stylesheet">
<link rel="stylesheet" href="{r}css/styles.css">
</head>
<body>
<div class="grain" aria-hidden="true"></div>
{NAV.format(root=r, total=len(data["cards"]), mk=wordmark("nav"))}
<main class="wrap" style="padding:64px 0 90px">
  <p class="kicker">404</p>
  <h1>Nothing here.</h1>
  <p class="line">That address does not exist. It never moved and it is not coming
  back, so pretending otherwise would be the one dishonest thing this site does.
  Here is what does exist.</p>
  <ul style="list-style:none;padding:0;margin:28px 0 0;display:grid;gap:9px;max-width:32rem">
{lis}
  </ul>
</main>
</body>
</html>"""


def main():
    data = json.loads(SHOP.read_text(encoding="utf-8"))
    sections, laws, shelf, cards = data["sections"], data["laws"], data["shelf"], data["cards"]
    # loaded up here because the section fronts and /credits/ both need it, and
    # they are written before the encyclopedia block further down
    manifest = json.loads((ROOT / "data" / "images.json").read_text(encoding="utf-8"))

    for p in ROOT.rglob("*.html"):
        pass
    (ROOT / "radar").mkdir(exist_ok=True)
    for old in (ROOT / "radar").glob("*.html"):
        if old.stem not in {c["slug"] for c in cards}:
            old.unlink()
    for c in cards:
        (ROOT / "radar" / f"{c['slug']}.html").write_text(
            build_card(c, sections, laws, shelf, data, manifest), encoding="utf-8")

    (ROOT / "section").mkdir(exist_ok=True)
    made = []
    for a in sections:
        html_ = build_section(a, data, manifest)
        if not html_:
            continue
        d = ROOT / "section" / a["id"]
        d.mkdir(exist_ok=True)
        (d / "index.html").write_text(html_, encoding="utf-8")
        made.append(a["id"])

    (ROOT / "sections").mkdir(exist_ok=True)
    (ROOT / "sections" / "index.html").write_text(build_aisle(data), encoding="utf-8")
    (ROOT / "shelf").mkdir(exist_ok=True)
    (ROOT / "shelf" / "index.html").write_text(build_shelf(data), encoding="utf-8")
    (ROOT / "index.html").write_text(build_front(data), encoding="utf-8")

    # the feature pages: top8, history, figures, moments
    feat = json.loads((ROOT / "data" / "features.json").read_text(encoding="utf-8"))
    hist = json.loads((ROOT / "data" / "history.json").read_text(encoding="utf-8"))
    # Record which list and which eight are on show BEFORE /top8/ renders so
    # the day record includes today - the same ordering as the ledger's
    # snapshot before its feed. record_top8_day() reads the same
    # top8_window() the page does, so the record and the render cannot
    # describe different shows, and a second build on the same day is a no-op.
    record_top8_day(feat)
    (ROOT / "top8").mkdir(exist_ok=True)
    (ROOT / "top8" / "index.html").write_text(build_top8(data, feat, manifest), encoding="utf-8")
    (ROOT / "top8" / "archive").mkdir(exist_ok=True)
    (ROOT / "top8" / "archive" / "index.html").write_text(
        build_top8_archive(data, feat, manifest), encoding="utf-8")
    # The day-by-day record at full length, beside the run-collapsed one under
    # the list. Reads the same data/top8_history.json the record under /top8/
    # does, so there is one sequence and two readings of it.
    (ROOT / "top8" / "record").mkdir(exist_ok=True)
    (ROOT / "top8" / "record" / "index.html").write_text(
        build_top8_record(data, feat, manifest), encoding="utf-8")
    (ROOT / "history").mkdir(exist_ok=True)
    (ROOT / "history" / "index.html").write_text(build_history(data, hist, manifest), encoding="utf-8")
    (ROOT / "figures").mkdir(exist_ok=True)
    (ROOT / "figures" / "index.html").write_text(build_figures(data, feat, manifest), encoding="utf-8")
    (ROOT / "moments").mkdir(exist_ok=True)
    (ROOT / "brand").mkdir(exist_ok=True)
    (ROOT / "brand" / "index.html").write_text(build_brand(data, feat), encoding="utf-8")

    # /atlas/ - the era x medium grid, rebuilt from data/atlas.json, and
    # /quiz/ behind it, which is scored out of the atlas.
    import subprocess as _sp
    _sp.run(["python", str(ROOT / "tools" / "atlas.py"), "--graph"], check=True,
           capture_output=True)
    _sp.run(["python", str(ROOT / "tools" / "build_atlas.py")], check=True,
           capture_output=True)
    _sp.run(["python", str(ROOT / "tools" / "build_quiz.py")], check=True,
           capture_output=True)

    # /citations/ - the sourcing backlog, ranked, in public
    _enc2 = json.loads((ROOT / "data" / "encyclopedia.json").read_text(encoding="utf-8"))
    (ROOT / "citations").mkdir(exist_ok=True)
    (ROOT / "citations" / "index.html").write_text(
        build_citations(data, _enc2), encoding="utf-8")

    # /ledger/ - the editorial half of what /citations/ audits. Distinct page,
    # distinct purpose: that one is ranked by how much the atlas points at each
    # entry, this one states the standard and prints the figures against it.
    # Both read tools/ledger.py, so they cannot disagree.
    (ROOT / "ledger").mkdir(exist_ok=True)
    (ROOT / "ledger" / "index.html").write_text(
        build_ledger(data, _enc2), encoding="utf-8")
    # Record today's figures BEFORE the feed reads them, so the first build
    # publishes a snapshot rather than an empty channel.
    record_snapshot(_lm2 := ledger_metrics(_enc2))
    (ROOT / "ledger" / "feed.xml").write_text(
        build_ledger_feed(_lm2), encoding="utf-8")

    # /exceptions/ - the reciprocity axis counted, with the two ways the count
    # is probably wrong printed on the page. Reads taxonomy_placements.rec, the
    # same field the axis chips count.
    _plc = json.loads(
        (ROOT / "data" / "taxonomy_placements.json").read_text(encoding="utf-8"))
    (ROOT / "exceptions").mkdir(exist_ok=True)
    (ROOT / "exceptions" / "index.html").write_text(
        build_exceptions(data, _enc2, _plc), encoding="utf-8")

    # /credits/ - every photograph, once, with its author and licence
    (ROOT / "credits").mkdir(exist_ok=True)
    (ROOT / "credits" / "index.html").write_text(
        build_credits(data, manifest), encoding="utf-8")

    # /desk/ - the signoff queue, from queue.json + sweep.json. Was a
    # client-fetched page pointed at a data/ directory that is never deployed,
    # so it rendered as an empty room behind a footer link on every page.
    (ROOT / "desk").mkdir(exist_ok=True)
    (ROOT / "desk" / "index.html").write_text(build_desk(data), encoding="utf-8")

    # /404.html - without it every unmatched path returns the homepage with a
    # 200, which is a soft 404: invisible to crawlers as an error, and wrong for
    # a site that trades on not making things up.
    (ROOT / "404.html").write_text(build_404(data), encoding="utf-8")

    # the encyclopedia: database, entry pages, master timeline, one timeline per section
    enc = json.loads((ROOT / "data" / "encyclopedia.json").read_text(encoding="utf-8"))

    # Record which register is on today BEFORE /taxonomy/ renders, from the
    # same date and order the page uses - the ledger's snapshot-before-feed
    # ordering, and the same reason the top-8 day is recorded before the front
    # page builds. Loads the taxonomy itself because main() has not loaded it
    # yet at this point.
    record_register_day()

    # /taxonomy/ - the classification itself, generated from the data so the
    # page cannot drift from the taxonomy it describes. After the encyclopedia is
    # loaded, because it counts the placements against the real entry set.
    (ROOT / "taxonomy").mkdir(exist_ok=True)
    (ROOT / "taxonomy" / "index.html").write_text(
        build_taxonomy(enc, data), encoding="utf-8")
    # The register rotation at full length, beside the record under the list.
    (ROOT / "taxonomy" / "record").mkdir(exist_ok=True)
    (ROOT / "taxonomy" / "record" / "index.html").write_text(
        build_taxonomy_record(data), encoding="utf-8")

    _tax = json.loads((ROOT / "data" / "taxonomy.json").read_text(encoding="utf-8"))
    (ROOT / "ways").mkdir(exist_ok=True)
    for a in _tax["attachment"]:
        d = ROOT / "ways" / a["id"]
        d.mkdir(exist_ok=True)
        (d / "index.html").write_text(
            build_way(a, _tax, enc, data, manifest), encoding="utf-8")

    edir = ROOT / "encyclopedia"
    edir.mkdir(exist_ok=True)
    for old in edir.glob("*.html"):
        if old.name != "index.html":
            old.unlink()
    for ent in enc["entries"]:
        (edir / f"{ent['id']}.html").write_text(
            build_entry(ent, enc, data, manifest), encoding="utf-8")
    (edir / "index.html").write_text(build_encyclopedia(enc, data), encoding="utf-8")
    tdir = ROOT / "timeline"
    tdir.mkdir(exist_ok=True)
    (tdir / "index.html").write_text(build_timeline(enc, data, None), encoding="utf-8")
    for a in data["sections"]:
        t = build_timeline(enc, data, a["id"])
        if not t:
            continue
        (tdir / a["id"]).mkdir(exist_ok=True)
        (tdir / a["id"] / "index.html").write_text(t, encoding="utf-8")
    (ROOT / "moments" / "index.html").write_text(build_moments(data, feat, manifest), encoding="utf-8")
    # expose the features to the front page and section index
    (ROOT / "data" / "features-index.json").write_text(json.dumps(
        {"lists": [{"slug": l["slug"], "title": l["title"], "dek": l["dek"],
                    "kicker": l["kicker"]} for l in feat["lists"]],
         "figures": len(feat["figures"]), "moments": len(feat["moments"])},
        indent=2, ensure_ascii=False), encoding="utf-8")
    # Record which parasocialite is on today's front page BEFORE it renders -
    # the ledger's snapshot-before-feed ordering, the same reason the top-8
    # day and the register are recorded before their pages - so the record
    # under the block and the block itself cannot describe different figures.
    record_parasocialite_day()
    # rebuild the front page with the features in
    (ROOT / "index.html").write_text(build_front(data, feat, manifest, hist), encoding="utf-8")
    # the section index gets the moments + top8 teasers too
    (ROOT / "sections" / "index.html").write_text(build_aisle(data, feat, manifest), encoding="utf-8")
    (ROOT / "radar.xml").write_text(build_rss(data), encoding="utf-8")
    _cases = build_cases(data)
    if _cases:
        (ROOT / "cases" / "index.html").write_text(_cases, encoding="utf-8")
    (ROOT / "sitemap.xml").write_text(build_sitemap(data), encoding="utf-8")

    (ROOT / "data" / "index.json").write_text(json.dumps({
        "meta": data.get("meta", {}), "sections": sections, "laws": laws,
        "shelf": shelf, "cards": [{
            "slug": c["slug"], "headline": c["headline"], "section": c["section"],
            "law": c["law"], "shelf": c.get("shelf"), "kicker": c.get("kicker"),
            "one_line": c["one_line"], "take": c["take"],
            "sources": c.get("sources", []), "filed": c.get("filed"),
            "due": c.get("due"), "state": c.get("state"),
            "url": f"{SITE}/radar/{c['slug']}.html"} for c in cards],
        "queue": data.get("queue", []),
    }, indent=2, ensure_ascii=False), encoding="utf-8")

    print(f"{len(cards)} stories · {len(made)} section fronts ({', '.join(made)}) · "
          f"{len(shelf)} works on the shelf · {sum(len(c['sources']) for c in cards)} sources cited")


if __name__ == "__main__":
    main()




























