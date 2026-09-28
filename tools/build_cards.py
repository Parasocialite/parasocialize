#!/usr/bin/env python3
"""
build_cards.py - redraws the whole video store from data/shop.json.

  radar/<slug>.html      one page per story
  section/<aisle>/       a section front per aisle
  aisle/index.html       every aisle, searchable
  shelf/index.html       the clerk's own work, multi-door
  index.html             the front page
  radar.xml / sitemap.xml / data/index.json

Run:  python tools/build_cards.py
"""
import json, html, datetime, pathlib, urllib.parse, hashlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
SHOP = ROOT / "data" / "shop.json"
SITE = "https://www.parasocialize.com"

HEAD = """<link rel="canonical" href="{site}{path}">
<meta property="og:type" content="{otype}">
<meta property="og:title" content="{title}">
<meta property="og:description" content="{desc}">
<meta property="og:image" content="{site}/img/podcasts/parasocialize.jpg">
<link rel="alternate" type="application/rss+xml" title="Parasocialize" href="{site}/radar.xml">
<link rel="icon" type="image/svg+xml" href="{site}/favicon.svg">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Fraunces:ital,opsz,wght@0,9..144,600;0,9..144,700;0,9..144,900;1,9..144,600;1,9..144,700&family=IBM+Plex+Mono:wght@400;500&display=swap" rel="stylesheet">
<link rel="stylesheet" href="{root}css/styles.css">
<link rel="stylesheet" href="{root}css/mascot.css">"""

NAV = """<header class="topbar"><div class="topbar-in">
  <a class="wordmark" href="{root}index.html">{mk}<b>PARASOCIALIZE</b></a>
  <button class="menu-btn" aria-label="Menu" aria-expanded="false" aria-controls="nav"><span></span><span></span><span></span></button>
  <nav id="nav" class="nav" aria-label="Main">
    <a href="{root}index.html">Home</a>
    <a href="{root}aisle/index.html">All {total}</a>
    <a href="{root}top8/index.html">Top 8</a>
    <a href="{root}history/index.html">The history</a>
    <a href="{root}moments/index.html">Moments</a>
    <a href="{root}timeline/index.html">Timeline</a>
    <a href="{root}encyclopedia/index.html">Encyclopedia</a>
    <a href="{root}brand/index.html">Ayo</a>
    <a href="{root}membership/index.html" class="cta">Support</a>
  </nav>
</div></header>"""

FOOT = """<footer class="footer"><div class="foot-grid">
  <div>
    <p class="wordmark foot-mark"><img class="logo-img" src="{root}img/logo.svg" alt="" width="24" height="24">PARA<b>SOCIALIZE</b></p>
    <p class="foot-note">{sweep}<br>Kept by Enan Joe Heneghan - video store clerk, M.A., teacher in Australia.<br>
    Every card links to its sources. Every card is signed by a person.</p>
  </div>
  <nav class="foot-nav" aria-label="Footer">
    <a href="{root}index.html">LATEST</a><a href="{root}aisle/index.html">SECTIONS</a>
    <a href="{root}guide/index.html">FIELD GUIDE</a><a href="{root}atlas/index.html">THE ATLAS</a><a href="{root}quiz/index.html">QUIZ</a>
    <a href="{root}credits/index.html">CREDITS</a>
    <a href="{root}membership/index.html">SUPPORT</a><a href="{root}desk/index.html">CLERK'S DESK</a>
    <a href="{root}radar.xml">RSS</a>
  </nav>
  <p class="foot-tag">{motto}</p>
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
</script>
</body></html>"""

MESSY = ("No replies. The connection stays one-sided either way. "
         "Nobody here is going to tell you to log off.")


def esc(s):
    return html.escape(str(s if s is not None else ""), quote=True)


def root(depth):
    return "../" * depth


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
def poster(c, aisles, wide=False):
    a = next((x for x in aisles if x["id"] == c["aisle"]), {})
    col = a.get("colour", "#ffb454")
    h = sum(ord(ch) for ch in c["slug"])
    g = (c["headline"].strip() or "P")[0].upper()
    label = c.get("kicker") or ("DO NOT RETURN" if c.get("state") == "OVERDUE" else "")
    stripe = "#e63946" if c.get("state") == "OVERDUE" else col
    lab = (f'<span style="position:absolute;top:12px;left:9px;z-index:2;background:{esc(stripe)};'
           f'color:#fff;font-family:var(--label);font-size:.48rem;letter-spacing:.14em;'
           f'text-transform:uppercase;padding:3px 6px;border-radius:2px;font-weight:500">'
           f'{esc(label)}</span>') if label else ""
    return (f'<div class="poster{" wide" if wide else ""}">'
            f'<span class="stripe" style="background:{esc(stripe)}"></span>'
            f'<span class="glyph">{esc(g)}</span>{lab}'
            f'<span class="foot"><b>{esc(a.get("sign", c["aisle"].upper()))}</b>'
            f'<span>{esc(c["headline"][:30])}</span></span></div>')


def poster_bg(c, aisles):
    """inline gradient for a lead cover"""
    a = next((x for x in aisles if x["id"] == c["aisle"]), {})
    col = a.get("colour", "#ffb454")
    h = sum(ord(ch) for ch in c["slug"])
    return (f"background:linear-gradient(155deg,{esc(col)} 0%,"
            f"color-mix(in srgb,{esc(col)} 30%,#1b1410) 55%,#120d0a 100%)")


def cover(c, aisles, manifest=None, depth=1, big=False):
    """The picture on a card, or the lettered poster if there isn't one.

    The order is deliberate: this story's own photograph, then its section's
    photograph, then the generated poster. Twenty-two of the forty-seven stories
    have no photograph of their own after review - Commons has no freely-licensed
    still of a Hungarian Twitch partner meeting, and the ones it did return for
    those stories were wrong, so they were withdrawn rather than shipped. Those
    cards fall back to the section photograph, which is a real photograph of the
    subject matter, and only fall through to a letter if a section has no
    photograph either.

    No credit on the card face, for the same reason the homepage tiles have none:
    it is a licence obligation, not decoration, and it lives on the article page
    and on /credits/ where there is room to be read.
    """
    f = img_for(manifest or {}, c.get("slug"), depth) or \
        img_aisle(manifest or {}, c.get("aisle"), depth)
    if f:
        return (f'<div class="poster shot">'
                f'<img src="{esc(f["path"])}" alt="" loading="lazy">'
                f'<span class="veil" style="background:'
                f'linear-gradient(to top,rgba(12,8,5,.86) 0%,rgba(12,8,5,.12) 46%,'
                f'rgba(12,8,5,0) 72%)"></span></div>')
    return poster(c, aisles, wide=big)


def story(c, aisles, laws, big=False, take=True, root_="", manifest=None, depth=1):
    a = next((x for x in aisles if x["id"] == c["aisle"]), {})
    col = a.get("colour", "#ffb454")
    law = next((l for l in laws if l["n"] == c["law"]), {})
    src = (c.get("sources") or [{}])[0]
    tags = [f'<span class="tag tag-aisle">{esc(a.get("sign", c["aisle"].upper()))}</span>']
    if c.get("kicker"):
        tags.append(f'<span class="tag tag-kick">{esc(c["kicker"])}</span>')
    if c.get("state") == "OVERDUE":
        tags.append('<span class="tag tag-od">Do not return</span>')
    if law:
        tags.append(f'<span class="tag tag-law">LAW {c["law"]}</span>')
    tk = f'<p class="take">{esc(c["take"])}</p>' if take and c.get("take") else ""
    return (f'<article class="story{" story-lg" if big else ""}" style="--c:{esc(col)}">'
            f'<a class="cover" href="{root_}radar/{esc(c["slug"])}.html" tabindex="-1" aria-hidden="true">'
            f'{cover(c, aisles, manifest, depth, big)}</a>'
            f'<div class="body"><div class="tags">{"".join(tags)}</div>'
            f'<h3><a href="{root_}radar/{esc(c["slug"])}.html">{esc(c["headline"])}</a></h3>'
            f'<p class="dek">{esc(c["one_line"])}</p>{tk}'
            f'<div class="foot"><span class="src">{esc(src.get("publisher", ""))}</span>'
            f'<a href="{root_}radar/{esc(c["slug"])}.html">Read →</a></div></div></article>')


# ------------------------------------------------------------------ article
def build_card(c, aisles, laws, shelf, data, manifest=None):
    d = 1
    r = root(d)
    manifest = manifest or {"items": []}
    a = next((x for x in aisles if x["id"] == c["aisle"]), {})
    law = next((x for x in laws if x["n"] == c["law"]), {})
    col = a.get("colour", "#ffb454")
    sh = next((x for x in shelf if x["id"] == c.get("shelf")), None)

    rel = sorted([x for x in data["cards"] if x["slug"] != c["slug"]
                  and x["aisle"] == c["aisle"]], key=lambda x: -x.get("res", 0))[:4]
    rel_html = "".join(story(x, aisles, laws, root_=r, manifest=manifest, depth=d) for x in rel)

    src_rows = []
    for s in c.get("sources", []):
        if s.get("url"):
            src_rows.append(
                f'<div class="srcbox" style="padding:14px 0;border-bottom:1px solid var(--line2)">'
                f'<a href="{esc(s["url"])}" target="_blank" rel="noopener nofollow">{esc(s["title"])} ↗</a>'
                f'<p class="pub">{esc(s["publisher"])} · {fmt_date(s.get("at"))}</p></div>')
        else:
            src_rows.append(
                f'<div class="srcbox" style="padding:14px 0;border-bottom:1px solid var(--line2);opacity:.6">'
                f'<a>{esc(s["title"])}</a>'
                f'<p class="pub">{esc(s["publisher"])} · LINK NOT RESOLVED YET — TREAT WITH SUSPICION</p></div>')

    sh_html = ""
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

    tags = [f'<span class="tag tag-aisle">{esc(a.get("sign",""))}</span>']
    if c.get("kicker"):
        tags.append(f'<span class="tag tag-kick">{esc(c["kicker"])}</span>')
    if c.get("state") == "OVERDUE":
        tags.append('<span class="tag tag-od">This one does not go back on the shelf</span>')
    if law:
        tags.append(f'<a class="tag tag-law" href="{r}index.html#laws">LAW {c["law"]} · {esc(law["title"])}</a>')

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
        sec = f"aisle-{c.get('aisle')}"
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
{NAV.format(root=r, total=len(data["cards"]), mk=mascot(30, "wm-mascot"))}
<main class="article" id="story">
  <div style="margin-bottom:18px">{''.join(tags)}</div>
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

  {f'<p class="kicker" style="margin-top:40px">More from {esc(a.get("sign",""))}</p><div class="front front-2">{rel_html}</div>' if rel_html else ''}
</main>
{FOOT.format(root=r, sweep=MESSY, motto='NO ALGORITHM CHOSE THIS.<br>THAT IS THE POINT.')}
</body></html>"""


# ------------------------------------------------------------------ section
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
        kind = src.get("kind", "")
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
{NAV.format(root=r, total=len(data["cards"]), mk=mascot(30, "wm-mascot"))}
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


def build_section(a, data, manifest=None):
    r = root(2)
    col = a.get("colour", "#ffb454")
    manifest = manifest or {"items": []}
    mine = sorted([c for c in data["cards"] if c["aisle"] == a["id"]],
                  key=lambda c: str(c.get("filed", "")), reverse=True)
    if not mine:
        return ""
    lead, rest = mine[0], mine[1:]
    big = "".join(story(c, data["aisles"], data["laws"], big=True, root_=r,
                        manifest=manifest, depth=2) for c in rest[:6])
    rest2 = "".join(story(c, data["aisles"], data["laws"], root_=r,
                          manifest=manifest, depth=2) for c in rest[6:12])

    others = [x for x in data["aisles"] if x["id"] != a["id"]]
    nav = "".join(
        f'<a class="chip{" on" if x["id"]==a["id"] else ""}" '
        f'style="--c:{esc(x.get("colour","#ffb454"))}" href="{r}section/{esc(x["id"])}/index.html">'
        f'{esc(x["sign"])}</a>' for x in others)

    return f"""<!DOCTYPE html>
<html lang="en"><head><meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{esc(a['sign'])} - the {esc(a['sign'].lower())} aisle - Parasocialize</title>
<meta name="description" content="{esc(a['blurb'])}">
{HEAD.format(site=SITE, path=f"/section/{a['id']}/", otype="website",
             title=f"{a['sign']} - Parasocialize", desc=esc(a['blurb']), root=r)}
</head>
<body>
<a class="skip" href="#s">Skip to stories</a>
<div class="grain" aria-hidden="true"></div>
{NAV.format(root=r, total=len(data["cards"]), mk=mascot(30, "wm-mascot"))}
<div style="height:5px;background:{esc(col)}"></div>
<main>
<section class="section" id="s">
  <p class="kicker" style="color:{esc(col)}">{len(mine)} stor{"y" if len(mine)==1 else "ies"}</p>
  <div class="sec-head">
    <h1 style="color:{esc(col)}">{esc(a['sign'])}</h1>
    <p class="sec-lede">{esc(a['blurb'])} <em style="color:var(--dim)">{esc(a['note'])}</em></p>
  </div>

  {fig(manifest, f"aisle-{esc(a['id'])}", 2, "sec-mast")}

  <div class="lead" style="margin-top:28px">
    <a class="cover" href="{r}radar/{esc(lead['slug'])}.html" tabindex="-1" aria-hidden="true"
       style="{poster_bg(lead, data['aisles'])};border-radius:12px;overflow:hidden;box-shadow:0 18px 46px rgba(0,0,0,.6);aspect-ratio:2/3;display:flex;align-items:flex-end;padding:14px">
      <span style="position:relative;z-index:2">
        <b style="display:block;font-family:var(--label);font-size:.5rem;letter-spacing:.2em;color:rgba(255,255,255,.8)">MOST RECENT</b>
        <span style="display:block;font-family:var(--serif);font-size:.9rem;font-weight:700;color:#fff;line-height:1.15;text-shadow:0 2px 8px rgba(0,0,0,.6)">{esc(lead['headline'][:44])}</span>
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

  <p class="kicker" style="margin-top:48px">Other aisles</p>
  <div class="chips">{nav}</div>
  <p class="countline"><a href="{r}aisle/index.html">See everything, searchable →</a></p>
</section>
</main>
{FOOT.format(root=r, sweep=MESSY, motto='TEN AISLES.<br>SEVEN OF THEM ARE NEW HERE.')}
</body></html>"""


# ------------------------------------------------------------------ all aisles
def build_aisle(data, feat=None, manifest=None):
    r = root(1)
    aisles, cards = data["aisles"], data["cards"]
    feat = feat or {"lists": [], "moments": []}
    manifest = manifest or {"items": []}
    blocks = []
    for a in aisles:
        mine = [c for c in cards if c["aisle"] == a["id"]]
        col = a.get("colour", "#ffb454")
        n = len(mine)
        blocks.append(
            f'<a class="aisle" style="--c:{esc(col)}" href="{r}section/{esc(a["id"])}/index.html">'
            f'<b>{esc(a["sign"])}</b><p>{esc(a["blurb"])}</p>'
            f'<span class="count"><b>{n}</b> stor{"y" if n==1 else "ies"}</span></a>')
    latest = "".join(story(c, aisles, data["laws"], take=False, root_=r,
                             manifest=manifest, depth=1) for c in cards[:18])

    # feature doors at the top: the lists, the history, the moments
    fdoors = []
    for L in (feat.get("lists") or []):
        f = img_for(manifest, L.get("image"), 1)  # /aisle/ is depth 1
        im = f'<img src="{esc(f["path"])}" alt="" loading="lazy">' if f else ""
        fdoors.append(f'<a class="fdoor" href="{r}top8/index.html" style="--c:#ff5a1f">'
                      f'<span class="fdoor-art">{im}</span>'
                      f'<span class="fdoor-body"><b>{esc(L["kicker"])}</b>'
                      f'<strong>Top 8</strong><span>{esc(L["title"])}</span></span></a>')
    for slug, name, kick, blurb, imslug in [
            ("history", "The history", "A course in eight modules",
             "The whole documented history of one-sided attachment, free.", "history-macy-store"),
            ("moments", "The moments", "The ones that moved it",
             f"{len(feat.get('moments', []))} significant moments across every domain.", "moment-wojak")]:
        f = img_for(manifest, imslug, 1)  # aisle page: depth 1
        im = f'<img src="{esc(f["path"])}" alt="" loading="lazy">' if f else ""
        fdoors.append(f'<a class="fdoor" href="{r}{esc(slug)}/index.html" style="--c:#a04dff">'
                      f'<span class="fdoor-art">{im}</span>'
                      f'<span class="fdoor-body"><b>{esc(kick)}</b>'
                      f'<strong>{esc(name)}</strong><span>{esc(blurb)}</span></span></a>')

    return f"""<!DOCTYPE html>
<html lang="en"><head><meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>All sections - Parasocialize</title>
<meta name="description" content="Ten aisles of one-sided attachment: idols, creators, characters, companions, worlds, brands, crossers, contests, grief and the ones that turn criminal.">
{HEAD.format(site=SITE, path="/aisle/", otype="website",
             title="All sections - Parasocialize",
             desc="Ten aisles of one-sided attachment.", root=r)}
</head>
<body>
<a class="skip" href="#a">Skip to sections</a>
<div class="grain" aria-hidden="true"></div>
{NAV.format(root=r, total=len(data["cards"]), mk=mascot(30, "wm-mascot"))}
<main>
<section class="section" id="a">
  <p class="kicker">The whole shop · {len(cards)} stories · {len(aisles)} aisles</p>
  <div class="sec-head">
    <h1>Pick an aisle. Or don't.</h1>
    <p class="sec-lede">Parasocial is when you feel you know someone who has no idea you exist. It is not a genre - it is a
    shape, and it shows up in a stadium and in a court docket and in the teacher at the front of the room exactly as hard as
    it shows up in a fandom. Ten aisles. Seven of them a fandom site would never build.</p>
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
def pick_top(cards, aisle):
    """The one story that represents the aisle right now. Ranked by importance,
    with a nudge toward anything that just happened and anything deliberately
    kept as DO-NOT-RETURN."""
    mine = [c for c in cards if c["aisle"] == aisle]
    if not mine:
        return None
    def rank(c):
        s = c.get("res", 0)
        if c.get("state") == "OVERDUE":
            s += 12
        if c.get("state") == "OUT":
            s += 6
        try:
            age = (datetime.date.today()
                   - datetime.date.fromisoformat(str(c.get("filed"))[:10])).days
            s += max(0, 6 - age)
        except Exception:
            pass
        return s
    return sorted(mine, key=rank, reverse=True)[0]


def build_front(data, feat=None, manifest=None, hist=None):
    aisles, laws, shelf, cards = data["aisles"], data["laws"], data["shelf"], data["cards"]
    feat = feat or {"lists": [], "moments": [], "figures": []}
    manifest = manifest or {"items": []}
    hist = hist or {"modules": []}

    # ---- the rotating top 8 column. deterministic on the ISO week, so it
    # changes on a schedule and is the same for every reader that week.
    week = datetime.date.today().isocalendar()[1]
    t8 = feat.get("lists") or []
    if t8:
        L = t8[0]
        pick = rotate(L["entries"], f"top8-w{week}", 4, by="rank")
        rows = []
        for en in pick:
            f = img_for(manifest, en.get("image"), 0)  # front page: depth 0
            im = (f'<img src="{esc(f["path"])}" alt="" loading="lazy">' if f
                  else f'<span class="t8col-n">{esc(en["rank"])}</span>')
            rows.append(f'<a class="t8col" href="top8/index.html">'
                        f'<span class="t8col-art">{im}</span>'
                        f'<span class="t8col-body"><b>{esc(en["rank"])}. {esc(en["name"])}</b>'
                        f'<span>{esc(en["show"])}</span></span></a>')
        t8_block = f"""<div class="t8col-wrap">
  <p class="kicker">The top 8 · this week · rotating</p>
  <div class="t8col-list">{''.join(rows)}</div>
  <a class="btn btn-solid" href="top8/index.html">Read the whole list</a>
  <p class="countline">Rotates weekly. This week it is the {esc(L['title'].lower())}.</p>
</div>"""
    else:
        t8_block = ""

    # ---- the three feature doors: history / moments / figures
    feats = []
    if hist.get("modules"):
        feats.append(('history', 'The history', '',
                      f"A course in {len(hist['modules'])} modules, from a sculptor to a 2023 policy update. Free, printable.",
                      "history-macy-store"))
    if feat.get("moments"):
        feats.append(('moments', 'The moments', '',
                      f"{len(feat['moments'])} significant moments across television, music, the internet, games and AI.",
                      "moment-wojak"))
    if feat.get("figures"):
        feats.append(('figures', 'The figures', '',
                      f"{len(feat['figures'])} people and characters who keep the sphere turning, from Pygmalion to a Twitch emote.",
                      None))
    fcards = []
    for slug, name, kick, blurb, imslug in feats:
        f = img_for(manifest, imslug, 0)  # front page: depth 0
        im = f'<img src="{esc(f["path"])}" alt="" loading="lazy">' if f else ""
        fcards.append(f"""<a class="fdoor" href="{esc(slug)}/index.html" style="--c:{esc(next((a.get('colour','#ff5a1f') for a in aisles if a['id']=='history'), '#ff5a1f'))}">
  <span class="fdoor-art">{im}</span>
  <span class="fdoor-body"><strong>{esc(name)}</strong><span>{esc(blurb)}</span></span>
</a>""")

    # ten tiles, one per aisle, each showing that aisle's top story. nothing
    # else competes for the front page.
    tiles = []
    for a in aisles:
        col = a.get("colour", "#ff5a1f")
        top = pick_top(cards, a["id"])
        n = len([c for c in cards if c["aisle"] == a["id"]])
        if not top:
            continue
        glyph = (top["headline"].strip() or "P")[0].upper()
        take = top.get("take", "")
        short = " ".join(take.split()[:20]) + ("…" if len(take.split()) > 20 else "")
        f = img_aisle(manifest, a["id"], 0) or img_for(manifest, top.get("image"), 0)
        if f:
            # No caption and no credit on the tile. The credit is a licence
            # obligation, not decoration, so it cannot simply be dropped - but
            # stamping it on all ten faces made the homepage read like a stock
            # library. The same photograph appears at size on the section front,
            # which carries the credit, and every file is listed once on
            # /credits/. That satisfies attribution in a reasonable manner and
            # keeps the page a page.
            img = f'<img src="{esc(f["path"])}" alt="">'
        else:
            img = f'<span class="hub-glyph">{esc(glyph)}</span>'
        tiles.append(f"""<a class="hub" style="--c:{esc(col)}" href="section/{esc(a['id'])}/index.html">
  <span class="hub-art">{img}</span>
  <b class="hub-name">{esc(a['sign'])}</b>
  <h3>{esc(top['headline'])}</h3>
  <p>{esc(short)}</p>
  <span class="hub-go">{n} more →</span>
</a>""")

    total = len(cards)
    return f"""<!DOCTYPE html>
<html lang="en"><head><meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Parasocialize</title>
<meta name="description" content="Parasocial is when you feel you know someone who has no idea you exist. News, argument, research and the definitive history - idols, AI, sport, politics, grief. Free.">
<link rel="canonical" href="{SITE}/">
{HEAD.format(site=SITE, path="/", otype="website", title="Parasocialize",
             desc="News, argument, research and the definitive history. Free.", root="")}
</head>
<body>
<a class="skip" href="#hub">Skip to the sections</a>
<div class="grain" aria-hidden="true"></div>
{NAV.format(root="", total=total, mk=mascot(30, "wm-mascot"))}

<main>
<section class="masthead">
  <div class="wrap">
    <h1>Parasocialize.</h1>
    <p class="line">Parasocial is when you feel you know someone who has no idea you exist.
    This is the news, the argument, the research and the whole history of it — in {len(aisles)} places it turns up.</p>
    <p class="mono-s" style="margin-top:14px">{total} stories · swept hourly · free · signed by a person ·
    <a href="aisle/index.html">all of it, searchable →</a></p>
  </div>
</section>

<section class="section" style="padding-top:8px">
  {t8_block}
</section>

<section class="section" id="hub" style="padding-top:0">
  <p class="kicker">Ten ways it shows up · the top story in each</p>
  <div class="hubs">{''.join(tiles)}</div>
</section>

{''.join(fcards) and f"""<section class="section" style="padding-top:0">
  <p class="kicker">Go deeper · the definitive bits</p>
  <div class="fdoors">{''.join(fcards)}</div>
</section>"""}

<section class="section signal-sec">
  <p class="kicker" style="justify-content:center">One email · Fridays · free</p>
  <h2 class="serif" style="font-size:clamp(1.6rem,3.4vw,2.2rem);max-width:22ch;margin:0 auto 12px">Five stories and one argument, once a week.</h2>
  <p class="sec-lede" style="margin:0 auto;max-width:50ch">No algorithm chose it. It pays for the machine that finds the stories.</p>
  <form class="signal-form" action="https://formsubmit.co/iNNERdreamers@gmail.com" method="POST">
    <input type="hidden" name="_subject" value="New Signal subscriber">
    <input type="hidden" name="_captcha" value="false">
    <label class="sr-only" for="email">Email address</label>
    <input id="email" type="email" name="email" placeholder="you@anywhere.net" required autocomplete="email">
    <button class="btn btn-solid" type="submit">Send it</button>
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
    return {"path": p,
            "credit": f'{src.get("author", "unknown")} · {src.get("licence", "")}'.strip(" ·"),
            "page": page, "caption": it.get("caption", ""),
            "kind": src.get("kind", "illustrative")}


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


def mascot(size=40, cls="", mood="watch", dark=False):
    """The brand mark: an eight on its side. Which is also infinity, and also
    two eyes. The eyes are the audience, so the mascot looks back at the
    reader - which is the joke, and also the argument.

    mood:
      watch    pupils slightly off-axis, alert (default)
      wink     one pupil shut, for pull quotes
      sad      pupils low, for the grief aisle
      hollow   no pupils. the one-sided joke: nobody is home
    """
    pupils = {
        "watch": ('<circle cx="34" cy="26" r="8.5" fill="{f}"/><circle cx="72" cy="34" r="8.5" fill="{f}"/>'
                  '<circle cx="36.5" cy="23" r="2.9" fill="{b}"/><circle cx="74.5" cy="31" r="2.9" fill="{b}"/>'),
        "wink":  ('<circle cx="34" cy="26" r="8.5" fill="{f}"/><path d="M64 34a9 9 0 0 1 18 0" '
                  'fill="none" stroke="{f}" stroke-width="5" stroke-linecap="round"/>'
                  '<circle cx="36.5" cy="23" r="2.9" fill="{b}"/>'),
        "sad":   ('<circle cx="34" cy="33" r="8.5" fill="{f}"/><circle cx="72" cy="33" r="8.5" fill="{f}"/>'
                  '<path d="M22 14a16 16 0 0 1 24 0" fill="none" stroke="{f}" stroke-width="4" stroke-linecap="round"/>'
                  '<path d="M60 14a16 16 0 0 1 24 0" fill="none" stroke="{f}" stroke-width="4" stroke-linecap="round"/>'),
        "hollow": "",
    }
    f = "#130d0a" if not dark else "#fff6ea"
    b = "#fff6ea" if not dark else "#130d0a"
    p = pupils.get(mood, pupils["watch"]).format(f=f, b=b)
    return (f'<svg class="mascot {esc(cls)}" viewBox="0 0 106 60" width="{size}" height="{size*60/106:.0f}" '
            f'aria-hidden="true" focusable="false">'
            f'<g fill="none" stroke="url(#pzg)" stroke-width="9" stroke-linecap="round">'
            f'<path d="M38 30a24 24 0 1 0 0-48 24 24 0 1 0 0 48"/>'
            f'<path d="M68 30a24 24 0 1 0 0-48 24 24 0 1 0 0 48"/></g>{p}</svg>')



def mascot(size=34, cls="", mood="watch", dark=False):
    """Ayo, the brand mark. An eight on its side: also infinity, also two eyes.
    The lobes are the eyes - no head, so the silhouette survives at 3cm.
    See tools/mascot.py for the full expression set and the merch exports."""
    import sys as _s
    if str(ROOT) not in _s.path:
        _s.path.insert(0, str(ROOT))
    import mascot as _m
    return _m.inline(mood, size=size, cls=cls)



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
def build_top8(data, feat, manifest):
    r = root(1)
    L = feat["lists"][0]
    laws = {l["n"]: l for l in data["laws"]}
    shelf = {s["id"]: s for s in data["shelf"]}

    items = []
    for en in L["entries"]:
        law = laws.get(en.get("law"), {})
        sh = shelf.get(law.get("shelf")) if law.get("shelf") else None
        cite = ""
        if sh:
            # the work is a source for this entry, cited like any other source
            cite = (f'<div class="t8-cite"><p class="t8-cite-l">SOURCE</p>'
                    f'<a href="{esc(sh["href"])}" target="_blank" rel="noopener">'
                    f'{esc(sh["title"])}</a>'
                    f'<p>{esc(sh["blurb"])}</p></div>')
        f = img_for(manifest, en.get("image"), 2)
        im = (f'<img class="t8-art" src="{esc(f["path"])}" alt="{esc(f["caption"])}" loading="lazy">'
              if f else
              f'<div class="t8-art t8-art-none" style="--c:{"#ff5a1f"}"><span>{esc(en["rank"])}</span></div>')
        items.append(f"""<li class="t8-item">
  <div class="t8-head">
    <span class="t8-rank">{esc(en['rank'])}</span>
    {im}
    <div class="t8-titles">
      <h3>{esc(en['name'])}</h3>
      <p class="t8-show">{esc(en['show'])}</p>
      <a class="t8-law" href="../history/index.html#law-{esc(en.get('law',1))}">LAW {esc(en.get('law',1))} · {esc(law.get('title',''))}</a>
    </div>
  </div>
  <p class="t8-what"><b>What happens.</b> {esc(en['what'])}</p>
  <p class="t8-why"><b>Why it's on the list.</b> {esc(en['why'])}</p>
  {cite}
</li>""")

    stand = fig(manifest, L.get("image"), 2, cls="t8-hero-fig")
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
{NAV.format(root=root(1), total=len(data['cards']), mk=mascot(30, 'wm-mascot'))}
<main>
<section class="section" style="padding-bottom:20px">
  <p class="kicker">{esc(L['kicker'])} · the top 8</p>
  <h1 style="font-family:var(--serif);font-size:clamp(2rem,5.4vw,3.6rem);font-weight:900;
     letter-spacing:-.03em;line-height:1.02;margin:0 0 16px;max-width:22ch">{esc(L['title'])}</h1>
  <p class="sec-lede" style="max-width:62ch;font-size:1.1rem">{esc(L['dek'])}</p>
  {stand}
  <div class="note" style="margin-top:26px"><p>{esc(L['standfirst'])}</p></div>
</section>

<section class="section" id="list" style="padding-top:8px">
  <ol class="t8">{''.join(items)}</ol>
  <p class="countline" style="margin-top:30px">More top 8s coming, rotated weekly.
  <a href="{r}index.html">Back to the ten aisles →</a></p>
</section>
</main>
{FOOT.format(root=root(1), sweep=MESSY, motto='TEN TO CALL IT A LIST.<br>ONE TO MAKE THE CASE.')}
</body></html>"""


# ------------------------------------------------------------------ history
def build_history(data, hist, manifest):
    r = root(1)
    laws = {l["n"]: l for l in data["laws"]}
    shelf = {s["id"]: s for s in data["shelf"]}

    law_bar = "".join(
        f'<a class="hlaw" href="#law-{esc(l["n"])}"><b>{esc(l["n"])}</b>'
        f'<span>{esc(l["title"])}</span></a>' for l in hist["laws"])

    mods = []
    for m in hist["modules"]:
        f = img_for(manifest, m.get("figure"), 1)
        im = (f'<figure class="fig h-fig"><img src="{esc(f["path"])}" alt="{esc(f["caption"])}" loading="lazy">'
              f'<figcaption>{esc(f["caption"])} · '
              f'<a href="{esc(f["page"])}" target="_blank" rel="noopener">'
              f'{esc(f["credit"])}</a></figcaption></figure>') if f else ""
        body = "".join(f"<p>{esc(p)}</p>" for p in m["body"])
        sh = shelf.get(laws.get(m.get("law"), {}).get("shelf"))
        cite = (f'<p class="h-cite">This module is law {esc(m.get("law"))} · '
                f'<a href="#law-{esc(m.get("law"))}">{esc(laws.get(m.get("law"),{}).get("title",""))}</a>'
                + (f' · which is a chapter of <a href="{r}shelf/index.html" target="_blank" rel="noopener">'
                   f'{esc(sh["title"])}</a>' if sh else "")
                + "</p>") if m.get("law") else ""
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
        sh = shelf.get(l.get("shelf"))
        cite = (f'<p class="h-cite">Also a chapter of '
                f'<a href="{r}shelf/index.html" target="_blank" rel="noopener">{esc(sh["title"])}</a></p>'
                if sh else "")
        laws_html.append(f"""<div class="hlaw-card" id="law-{esc(l['n'])}">
  <span class="hlaw-n">{esc(l['n'])}</span>
  <div><h3>{esc(l['title'])}</h3><p>{esc(l['one'])}</p>{cite}</div>
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
{NAV.format(root=root(1), total=len(data['cards']), mk=mascot(30, 'wm-mascot'))}
<main>
<section class="section" style="padding-bottom:24px">
  <p class="kicker">A course in eight modules · free · printable</p>
  <h1 class="h-title">The history of feeling things at people who can't feel it back</h1>
  <p class="sec-lede" style="font-size:1.12rem;max-width:64ch">{esc(hist['intro'])}</p>
  <p class="countline">Ctrl/Cmd+P to print the whole thing. It is a course, not a blog post — modules, claims, evidence.</p>
  <div class="h-outline">{law_bar}</div>
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
  <a href="../guide/index.html">the field guide</a>. Free.</p>
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
{NAV.format(root=root(1), total=len(data['cards']), mk=mascot(30, 'wm-mascot'))}
<main>
<section class="section" id="f">
  <p class="kicker">Figures · the people holding the sphere</p>
  <h1 class="h-title" style="font-size:clamp(1.9rem,4.6vw,3rem)">Who does the holding</h1>
  <p class="sec-lede" style="max-width:60ch">Every parasocial bond needs something on the other end, whether or
  not it can hold anything back. These are the ones that keep turning up, from a sculptor to a face on a webcam.</p>
  <div class="fcards" style="margin-top:28px">{''.join(figs)}</div>
  <p class="countline" style="margin-top:28px">Want the argument for the whole thing?
  <a href="{r}history/index.html">The history course →</a> · <a href="{r}index.html">The ten aisles →</a></p>
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
{NAV.format(root=root(1), total=len(data['cards']), mk=mascot(30, 'wm-mascot'))}
<main>
<section class="section" id="m">
  <p class="kicker">Moments · the ones that changed the shape of it</p>
  <h1 class="h-title" style="font-size:clamp(1.9rem,4.6vw,3rem)">The moments that moved it</h1>
  <p class="sec-lede" style="max-width:60ch">Not the news — the news is ten aisles away. These are the
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
    moods = [("watch", "The default. Ayo looking back at you, which is the whole "
                       "premise: the eyes belong to the audience."),
             ("hollow", "Nobody home. The one-sided joke, and the thesis of the site "
                        "in one expression."),
             ("wink", "For pull quotes and the Friday email."),
             ("sad", "Grief. Used on the obituary cards and the grief section."),
             ("love", "The club. Heart eyes, for when somebody has told you which "
                      "aisle they are in."),
             ("panic", "The sweep is late and the clock is red."),
             ("clerk", "Behind the counter. Ayo in the nametag."),
             ("asleep", "Sweeping hourly, seven past.")]
    cards = "".join(
        f'<figure class="mood"><div class="mood-art">{mascot(120, "", m)}</div>'
        f'<figcaption><b>{m}</b><span>{note}</span></figcaption></figure>'
        for m, note in moods)
    return f"""<!DOCTYPE html>
<html lang="en"><head><meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Ayo - the mascot - Parasocialize</title>
<meta name="description" content="Ayo is an eight lying on its side, which is also infinity, which is also two eyes. The brand mark of Parasocialize.">
{HEAD.format(site=SITE, path="/brand/", otype="website",
             title="Ayo - the Parasocialize mascot",
             desc="An eight on its side: also infinity, also two eyes.", root=root(1))}
</head>
<body>
<a class="skip" href="#moods">Skip to the expressions</a>
<div class="grain" aria-hidden="true"></div>
{NAV.format(root=root(1), total=len(data['cards']), mk=mascot(30, 'wm-mascot'))}
<main>
<section class="section" style="text-align:center">
  <div style="display:flex;justify-content:center;margin:10px 0 22px">{mascot(200, 'mascot-hero')}</div>
  <h1 class="h-title" style="font-size:clamp(2.4rem,7vw,4.4rem);margin:0 auto 14px">Ayo</h1>
  <p class="sec-lede" style="margin:0 auto;max-width:54ch">An eight lying on its side.
  Which is also infinity. Which is also two eyes. The lobes <em>are</em> the eyes —
  there is no head and no face, the whole glyph is doing the work, which is why it
  still reads at three centimetres on a shirt.</p>
</section>

<section class="section" style="padding-top:0">
  <div class="note" style="max-width:64ch;margin:0 auto">
    <p><b>The eyes are the audience.</b> Ayo watches somebody who does not know Ayo
    is there, which is the entire premise, so the mascot is not a decoration — it is
    the reader, caught in the act. The joke and the argument are the same thing.</p>
    <p><b>The name is from "eight".</b> Two letters, pronounceable, works on a
    shirt, and it sounds like a friend rather than a brand — which is the point,
    because a parasocial relationship is with somebody who feels like a friend.</p>
  </div>
</section>

<section class="section" id="moods" style="padding-top:0">
  <p class="kicker">Eight expressions</p>
  <div class="sec-head"><h2>One silhouette, so it reads as one character.</h2>
  <p class="sec-lede">The two lobes are identical in every expression. That is the
  constraint that makes it a character and not a set of stickers — you know it is
  Ayo at postage-stamp size because the shape never changes, only the face.</p></div>
  <div class="moods" style="margin-top:26px">{cards}</div>
</section>

<section class="section" style="padding-top:0">
  <p class="kicker">The lore, if you want it</p>
  <div class="note" style="max-width:64ch">
    <p>Ayo watched a character who was never real for thirty years. One day the
    character was retired from the show. Nobody told Ayo. Ayo found out the way
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


def _fmt_year(y):
    if y is None:
        return "—"
    if y < 0:
        return f"{abs(y)} BC"
    return str(y)


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


def build_timeline(enc, data, section=None):
    # /timeline/ is depth 1; /timeline/<section>/ is depth 2.
    r = root(2) if section else root(1)
    a = None
    if section:
        a = next((x for x in data["aisles"] if x["id"] == section), None)
    pool = [e for e in enc["entries"] if (not section or section in e.get("sections", []))]
    pool.sort(key=lambda e: (_y(e), e.get("title", "")))

    # group by century-ish bucket, oldest first
    buckets = {}
    for e in pool:
        buckets.setdefault(_era_bucket(_y(e)), []).append(e)
    order = ["Before 0", "0-499", "500-999", "1000-1499", "1500-1699", "1700-1799",
             "1800-1899", "1900-1949", "1950-1999", "2000-2009", "2010+"]
    groups = ""
    for b in order:
        if b not in buckets:
            continue
        items = "".join(_entry_row(e, enc, r) for e in buckets[b])
        groups += (f'<section class="tl-era" id="era-{esc(b.replace(" ","-").replace("+","plus"))}">'
                   f'<h2 class="tl-era-h">{esc(b)}<span>{len(buckets[b])}</span></h2>'
                   f'<ul class="tl-list">{items}</ul></section>')

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
        for x in data["aisles"])

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
{NAV.format(root=r, total=len(data['cards']), mk=mascot(30, 'wm-mascot'))}
<main>
<section class="section" id="tl" style="padding-bottom:20px">
  {head}
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


def build_entry(ent, enc, data):
    # NB: the module-level escape helper is also called esc(). Do not shadow it.
    r = root(2)
    kinds = enc["kinds"]
    back = next((s for s in data["aisles"] if s["id"] in ent.get("sections", [])), None)
    rel = [x for x in enc["entries"] if x["id"] in ent.get("related", [])]
    if not rel:
        rel = [x for x in enc["entries"]
               if x["id"] != ent["id"] and set(x.get("lanes", [])) & set(ent.get("lanes", []))][:6]
    rel_html = "".join(
        f'<a class="xref" href="{esc(x["id"])}.html"><b>{esc(x["title"])}</b>'
        f'<span>{esc(_fmt_year(x.get("year")))} · {esc(kinds.get(x.get("kind", ""), ""))}</span></a>'
        for x in rel)

    lane_html = "".join(
        f'<span class="lane" style="--c:{enc["lanes"][l]["colour"]}">'
        f'{esc(enc["lanes"][l]["name"])}</span>'
        for l in ent.get("lanes", []) if l in enc["lanes"])

    others = "".join(
        f'<a class="chip" style="--c:{esc(s.get("colour", "#ff5a1f"))}" '
        f'href="../../timeline/{esc(s["id"])}/index.html">{esc(s["sign"])}</a>'
        for s in data["aisles"] if s["id"] in ent.get("sections", []))

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
{NAV.format(root=r, total=len(data['cards']), mk=mascot(30, 'wm-mascot'))}
<main class="article">
  <p class="kicker">{esc(kinds.get(ent.get('kind',''),''))} · {_fmt_year(ent.get('year'))} · {esc(ent.get('era',''))}</p>
  <h1>{esc(ent['title'])}</h1>
  <p class="dek">{esc(ent.get('summary',''))}</p>
  <div class="byline" style="margin-bottom:26px">{lane_html}</div>

  <div class="body">
    <p class="lede2">{esc(ent.get('significance',''))}</p>
  </div>

  {f'<div class="srcbox" style="margin-top:26px;padding:14px 0;border-top:1px solid var(--line)">'
   f'<p class="srcline">SOURCE</p><a>{esc(ent.get("source") or "see the article")}</a></div>'
   if ent.get('source') else ''}
  {'' if ent.get('verified') else
   '<p class="checknote">This entry is real. The citation has not been checked by a human yet — '
   'treat the date as approximate until it is.</p>'}

  {f'<p class="kicker" style="margin-top:40px">Also in this section</p><div class="xrefs">{rel_html}</div>' if rel_html else ''}

  <p class="kicker" style="margin-top:40px">Timelines this appears in</p>
  <div class="chips">{others}</div>
  <p class="countline" style="margin-top:20px">
    <a href="../../timeline/index.html">The full timeline →</a> ·
    <a href="../../encyclopedia/index.html">The database →</a></p>
</main>
{FOOT.format(root=r, sweep=MESSY, motto='A DATABASE, NOT A POST.<br>EVERY ENTRY IS LINKED.')}
</body></html>"""


def build_encyclopedia(enc, data):
    r = root(1)
    rows = []
    for e in sorted(enc["entries"], key=lambda x: (_y(x), x.get("title", ""))):
        dots = "".join(
            f'<i class="lane-dot" style="--c:{enc["lanes"][l]["colour"]}" '
            f'title="{esc(enc["lanes"][l]["name"])}"></i>'
            for l in e.get("lanes", []) if l in enc["lanes"])
        rows.append(
            f'<tr data-lanes="{esc(" ".join(e.get("lanes", [])))}" '
            f'data-kind="{esc(e.get("kind", ""))}" '
            f'data-verified="{esc(str(bool(e.get("verified"))).lower())}" '
            f'data-hay="{esc((e.get("title", "") + " " + e.get("summary", "") + " " + e.get("era", "")).lower())}">'
            f'<td class="db-y">{esc(_fmt_year(e.get("year")))}</td>'
            f'<td><a href="{r}encyclopedia/{esc(e["id"])}.html">{esc(e["title"])}</a></td>'
            f'<td class="db-k">{esc(enc["kinds"].get(e.get("kind", ""), ""))}</td>'
            f'<td class="db-l">{dots}</td>'
            f'<td class="db-v">{"" if e.get("verified") else "?"}</td></tr>')
    lanes = "".join(f'<button class="chip" data-lane="{esc(l)}">{esc(v["name"])}</button>'
                    for l, v in enc["lanes"].items())
    kinds = "".join(f'<button class="chip" data-kind="{esc(k)}">{esc(v)}</button>'
                    for k, v in enc["kinds"].items())
    n = len(enc["entries"])
    unv = sum(1 for e in enc["entries"] if not e.get("verified"))

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
{NAV.format(root=r, total=len(data['cards']), mk=mascot(30, 'wm-mascot'))}
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
  <div class="lanecards" style="margin-top:24px">
    {''.join(f'<div class="lanecard" style="--c:{esc(v["colour"])}"><b>{esc(v["name"])}</b>'
             f'<p>{esc(v["blurb"])}</p></div>' for v in enc['lanes'].values())}
  </div>

  <div class="bar" style="margin-top:26px">
    <input class="search" id="q" type="search" placeholder="Search {n} entries…" aria-label="Search">
    <label class="tog"><input type="checkbox" id="onlyunv"> citation check only</label>
  </div>
  <p class="kicker" style="margin-top:16px">Lane</p>
  <div class="chips" id="lanes">{lanes}</div>
  <p class="kicker" style="margin-top:12px">Kind</p>
  <div class="chips" id="kinds">{kinds}</div>
  <p class="countline" id="count" aria-live="polite"></p>

  <div class="dbwrap"><table class="db"><tbody>{''.join(rows)}</tbody></table></div>
  <p class="countline" style="margin-top:18px">{unv} of {n} entries are flagged
  <b>?</b> for a citation check. That is the work queue, not a failure: a timeline
  format tells the reader somebody checked, so unverified dates are marked rather than hidden.
  <a href="{r}timeline/index.html">Read it as a timeline →</a></p>
</section>
</main>
{FOOT.format(root=r, sweep=MESSY, motto='THE UNVERIFIED ONES ARE MARKED.<br>NOT HIDDEN.')}
<script>
(function(){{
  var q=document.getElementById('q'),c=document.getElementById('count'),
      rows=[].slice.call(document.querySelectorAll('tr[data-lanes]')),
      lb=[].slice.call(document.querySelectorAll('#lanes .chip')),
      kb=[].slice.call(document.querySelectorAll('#kinds .chip')),
      unv=document.getElementById('onlyunv'),
      lane=null,kind=null,total=rows.length;
  function run(){{
    var t=(q.value||'').trim().toLowerCase(),n=0;
    rows.forEach(function(r){{
      var okL=!lane||(' '+r.dataset.lanes+' ').indexOf(' '+lane+' ')>-1,
          okK=!kind||r.dataset.kind===kind,
          okV=!unv.checked||r.dataset.verified==='false',
          okT=!t||r.dataset.hay.indexOf(t)>-1,
          on=okL&&okK&&okV&&okT;
      r.style.display=on?'':'none';if(on)n++;
    }});
    c.textContent=n+' / '+total+' ENTRIES'+(lane?' · '+lane.toUpperCase():'')
      +(kind?' · '+kind.toUpperCase():'')+(unv.checked?' · CITATION CHECK':'')
      +(t?' · "'+q.value.toUpperCase()+'"':'');
  }}
  lb.forEach(function(b){{b.addEventListener('click',function(){{
    lane=(lane===b.dataset.lane?null:b.dataset.lane);
    lb.forEach(function(x){{x.classList.toggle('on',x.dataset.lane===lane);}});run();}});}});
  kb.forEach(function(b){{b.addEventListener('click',function(){{
    kind=(kind===b.dataset.kind?null:b.dataset.kind);
    kb.forEach(function(x){{x.classList.toggle('on',x.dataset.kind===kind);}});run();}});}});
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
                f'<a class="btn btn-ghost" style="padding:6px 11px;font-size:.52rem" href="{esc(u)}" '
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
    return f"""<!DOCTYPE html>
<html lang="en"><head><meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>The shelf - Parasocialize</title>
<meta name="description" content="The novels, poetry, albums, podcasts and videos the stories lean on.">
{HEAD.format(site=SITE, path="/shelf/", otype="website",
             title="The shelf - Parasocialize",
             desc="The work behind the argument.", root=r)}
</head>
<body>
<a class="skip" href="#s">Skip to the shelf</a>
<div class="grain" aria-hidden="true"></div>
{NAV.format(root=r, total=len(cards), mk=mascot(30, "wm-mascot"))}
<main>
<section class="section" id="s">
  <p class="kicker">{len(shelf)} works</p>
  <h1 style="font-family:var(--serif);font-size:clamp(2rem,5vw,3.2rem);font-weight:900;letter-spacing:-.03em;margin:0 0 12px">The shelf</h1>
  <p class="sec-lede" style="max-width:56ch">The novels, albums, podcasts and videos the stories lean on.
  {cited} of {len(shelf)} are cited by something on the site right now. More than one way to buy each.</p>
  {''.join(groups)}
  <p class="countline" style="margin-top:36px">The novels are how a lot of people find this site, and this site is
  why a lot of people read them. <a href="{r}index.html">Back to the ten aisles →</a></p>
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
        a = next((x for x in data["aisles"] if x["id"] == c["aisle"]), {})
        body = (f'<p><strong>{esc(c["headline"])}</strong></p><p>{esc(c["one_line"])}</p>'
                f'<p><em>{esc(c["take"])}</em></p>'
                f'<p>Aisle {esc(a.get("sign",""))}, law {c["law"]}. '
                f'<a href="{SITE}/radar/{esc(c["slug"])}.html">Read the card</a>.</p>')
        items.append(
            f'<item><title>{esc(c["headline"])}</title>'
            f'<link>{SITE}/radar/{esc(c["slug"])}.html</link>'
            f'<guid isPermaLink="true">{SITE}/radar/{esc(c["slug"])}.html</guid>'
            f'<pubDate>{rfc822(c.get("filed"))}</pubDate>'
            f'<category>{esc(c["aisle"])}</category>'
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


def build_sitemap(data):
    today = str(data.get("meta", {}).get("generated", ""))[:10] or "2026-09-28"
    urls = [(f"{SITE}/", "1.0", "hourly"), (f"{SITE}/aisle/", "0.9", "daily"),
            (f"{SITE}/history/", "0.9", "monthly"), (f"{SITE}/top8/", "0.9", "weekly"),
            (f"{SITE}/moments/", "0.8", "monthly"), (f"{SITE}/figures/", "0.7", "monthly"),
            (f"{SITE}/shelf/", "0.8", "monthly"), (f"{SITE}/membership/", "0.7", "monthly"),
            (f"{SITE}/clinic/", "0.6", "monthly"), (f"{SITE}/guide/", "0.8", "monthly"),
            (f"{SITE}/signal/latest.html", "0.5", "weekly"), (f"{SITE}/tip/", "0.4", "monthly")]
    urls.append((f"{SITE}/atlas/", "0.6", "weekly"))
    urls.append((f"{SITE}/quiz/", "0.6", "monthly"))
    urls.append((f"{SITE}/credits/", "0.4", "monthly"))
    for a in data["aisles"]:
        urls.append((f"{SITE}/section/{a['id']}/", "0.8", "daily"))
        urls.append((f"{SITE}/timeline/{a['id']}/", "0.7", "monthly"))
    for p in ("/timeline/", "/encyclopedia/", "/brand/", "/top8/", "/history/",
              "/moments/", "/figures/"):
        urls.append((f"{SITE}{p}", "0.9", "monthly"))
    enc_urls = json.loads((ROOT / "data" / "encyclopedia.json").read_text(encoding="utf-8"))
    for ent in enc_urls["entries"]:
        urls.append((f"{SITE}/encyclopedia/{ent['id']}.html", "0.6", "yearly"))
    for c in data["cards"]:
        urls.append((f"{SITE}/radar/{c['slug']}.html", "0.7", "weekly"))
    rows = "\n".join(f'  <url><loc>{u}</loc><lastmod>{today}</lastmod>'
                     f'<changefreq>{f}</changefreq><priority>{p}</priority></url>' for u, p, f in urls)
    return ('<?xml version="1.0" encoding="UTF-8"?>\n'
            '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + rows + "\n</urlset>\n")


# ------------------------------------------------------------------ run
def main():
    data = json.loads(SHOP.read_text(encoding="utf-8"))
    aisles, laws, shelf, cards = data["aisles"], data["laws"], data["shelf"], data["cards"]
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
            build_card(c, aisles, laws, shelf, data, manifest), encoding="utf-8")

    (ROOT / "section").mkdir(exist_ok=True)
    made = []
    for a in aisles:
        html_ = build_section(a, data, manifest)
        if not html_:
            continue
        d = ROOT / "section" / a["id"]
        d.mkdir(exist_ok=True)
        (d / "index.html").write_text(html_, encoding="utf-8")
        made.append(a["id"])

    (ROOT / "aisle").mkdir(exist_ok=True)
    (ROOT / "aisle" / "index.html").write_text(build_aisle(data), encoding="utf-8")
    (ROOT / "shelf").mkdir(exist_ok=True)
    (ROOT / "shelf" / "index.html").write_text(build_shelf(data), encoding="utf-8")
    (ROOT / "index.html").write_text(build_front(data), encoding="utf-8")

    # the feature pages: top8, history, figures, moments
    feat = json.loads((ROOT / "data" / "features.json").read_text(encoding="utf-8"))
    hist = json.loads((ROOT / "data" / "history.json").read_text(encoding="utf-8"))
    (ROOT / "top8").mkdir(exist_ok=True)
    (ROOT / "top8" / "index.html").write_text(build_top8(data, feat, manifest), encoding="utf-8")
    (ROOT / "history").mkdir(exist_ok=True)
    (ROOT / "history" / "index.html").write_text(build_history(data, hist, manifest), encoding="utf-8")
    (ROOT / "figures").mkdir(exist_ok=True)
    (ROOT / "figures" / "index.html").write_text(build_figures(data, feat, manifest), encoding="utf-8")
    (ROOT / "moments").mkdir(exist_ok=True)
    (ROOT / "brand").mkdir(exist_ok=True)
    (ROOT / "brand" / "index.html").write_text(build_brand(data, feat), encoding="utf-8")

    # /atlas/ - the constellation, rebuilt from data/atlas.json
    import subprocess as _sp
    _sp.run(["python", str(ROOT / "tools" / "atlas.py"), "--graph"], check=True,
           capture_output=True)
    _sp.run(["python", str(ROOT / "tools" / "build_atlas.py")], check=True,
           capture_output=True)
    _sp.run(["python", str(ROOT / "tools" / "build_quiz.py")], check=True,
           capture_output=True)

    # /credits/ - every photograph, once, with its author and licence
    (ROOT / "credits").mkdir(exist_ok=True)
    (ROOT / "credits" / "index.html").write_text(
        build_credits(data, manifest), encoding="utf-8")

    # the encyclopedia: database, entry pages, master timeline, one timeline per section
    enc = json.loads((ROOT / "data" / "encyclopedia.json").read_text(encoding="utf-8"))
    edir = ROOT / "encyclopedia"
    edir.mkdir(exist_ok=True)
    for old in edir.glob("*.html"):
        if old.name != "index.html":
            old.unlink()
    for ent in enc["entries"]:
        (edir / f"{ent['id']}.html").write_text(build_entry(ent, enc, data), encoding="utf-8")
    (edir / "index.html").write_text(build_encyclopedia(enc, data), encoding="utf-8")
    tdir = ROOT / "timeline"
    tdir.mkdir(exist_ok=True)
    (tdir / "index.html").write_text(build_timeline(enc, data, None), encoding="utf-8")
    for a in data["aisles"]:
        t = build_timeline(enc, data, a["id"])
        if not t:
            continue
        (tdir / a["id"]).mkdir(exist_ok=True)
        (tdir / a["id"] / "index.html").write_text(t, encoding="utf-8")
    (ROOT / "moments" / "index.html").write_text(build_moments(data, feat, manifest), encoding="utf-8")
    # expose the features to the front page and aisle index
    (ROOT / "data" / "features-index.json").write_text(json.dumps(
        {"lists": [{"slug": l["slug"], "title": l["title"], "dek": l["dek"],
                    "kicker": l["kicker"]} for l in feat["lists"]],
         "figures": len(feat["figures"]), "moments": len(feat["moments"])},
        indent=2, ensure_ascii=False), encoding="utf-8")
    # rebuild the front page with the features in
    (ROOT / "index.html").write_text(build_front(data, feat, manifest, hist), encoding="utf-8")
    # the aisle index gets the moments + top8 teasers too
    (ROOT / "aisle" / "index.html").write_text(build_aisle(data, feat, manifest), encoding="utf-8")
    (ROOT / "radar.xml").write_text(build_rss(data), encoding="utf-8")
    (ROOT / "sitemap.xml").write_text(build_sitemap(data), encoding="utf-8")

    (ROOT / "data" / "index.json").write_text(json.dumps({
        "meta": data.get("meta", {}), "aisles": aisles, "laws": laws,
        "shelf": shelf, "cards": [{
            "slug": c["slug"], "headline": c["headline"], "aisle": c["aisle"],
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




























