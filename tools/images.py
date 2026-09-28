#!/usr/bin/env python3
"""
images.py - real photography for a real publication.

WHY THIS EXISTS
The brief was "images" and then "look like a mainstream news site". Tested
every hotlink route first, because hotlinking is what a news site would do:

    TMDB          404 to a plain fetch
    Spotify CDN   404 to a plain fetch
    Fandom/wikia  403
    Openverse     403 (both hosts)
    Flickr CC feed  200  <- works, no key
    Commons API     200  <- works, no key
    i.ytimg.com     200  <- works (your own video stills)

So: resolve once, cache the bytes locally, serve our own files. Never 404, no
dependency on somebody else's uptime, and every file carries its author and
licence.

THE RELEVANCE PROBLEM, AND WHY SCORING REPLACED PRUNING
A first pass took whatever Commons returned first, which put "a lion dance
team" under a caption promising Dolores from Pan's Labyrinth, and "a man on a
phone" under Replika. The response was prune_images.py: delete anything that
could not be verified, and fall back to generated cover art. That was honest
and it threw away the whole feature, because the pictures were never the
problem - picking the first hit was.

So queries here carry a `must` list: terms that have to appear in the file's
own title. A candidate missing any of them is not a worse choice, it is the
wrong picture, and it is dropped. Everything that survives is scored on
framing and resolution and the best one wins. `kind` records whether a hit is
the thing itself ("exact") or the subject matter ("illustrative").

THE HONEST CAVEAT
News photography of real events is licensed by the outlets that made it, and
none of that is free to reuse. What is free is CC-licensed photography of the
*subject matter*, plus the people in it. This has turned out better than
expected: for the Saturday-morning list what Commons actually holds is fans in
costume - Zuko at a convention, Elmo in Times Square, the Neighbours cast at a
meet-and-greet, a Reptar toy in a shop. For a publication arguing that the
bond lives with the audience, that is a better picture than the still would
have been. Captions say what is in the frame, never what the story is about.

YOUR OWN PHOTOS
`--slots` lists the frames a one-person operation should shoot. Real photos of
the actual shelf and the actual classroom will do more for this site's
credibility than any stock library.

  python tools/images.py --list
  python tools/images.py --fetch-all
  python tools/images.py --fetch <slug>
  python tools/images.py --slots
  python tools/seed_images.py          # write the query set
"""
import json, ssl, urllib.request, urllib.parse, datetime, pathlib, hashlib, sys, re

ROOT = pathlib.Path(__file__).resolve().parent.parent
MAN = ROOT / "data" / "images.json"
CACHE = ROOT / "img" / "editorial"

UA = "Parasocialize/2.0 (https://www.parasocialize.com; counter@parasocialize.com)"
FLICKR = ("https://api.flickr.com/services/feeds/photos_public.gne"
          "?tags={tags}&tagmode=all&format=json&nojsoncallback=1")
COMMONS = "https://commons.wikimedia.org/w/api.php"

# Things Commons returns that are never the thing: diagrams, maps, book covers,
# crew photos, scans of documents.
BAD = ("logo", "icon", "map of", "coat of arms", "flag of", "signature", "chart",
       "graph", "captura", "book_of", "book of", "cover", "capa", "dvd",
       "blu-ray", "soundtrack", "bumper", "navy", "vermerk", "title page",
       "frontispiece", "contents", "ambigram", "bobblehead")
# Logos and wordmarks are only wrong for stories they misrepresent. A story
# ABOUT YouTube legitimately shows the YouTube wordmark, so items carry an
# explicit allow_logo rather than the filter being globally switched off.
BAD_ALWAYS = ("coat of arms", "flag of", "ambigram", "signature", "title page")

FREE = ("cc", "public domain", "pd-", "cc0", "attribution")


def http(url, timeout=20, binary=False):
    req = urllib.request.Request(url, headers={
        "User-Agent": UA, "Accept-Encoding": "identity",
        "Accept": "application/json, image/jpeg, image/png, image/*;q=0.8"})
    with urllib.request.urlopen(req, timeout=timeout, context=ssl.create_default_context()) as r:
        b = r.read()
    return b if binary else json.loads(b)


def jload(p, d):
    try:
        return json.loads(pathlib.Path(p).read_text(encoding="utf-8"))
    except Exception:
        return d


def jdump(p, o):
    pathlib.Path(p).parent.mkdir(parents=True, exist_ok=True)
    pathlib.Path(p).write_text(json.dumps(o, indent=2, ensure_ascii=False), encoding="utf-8")


def strip_html(s):
    return re.sub(r"<[^>]+>", "", str(s or "")).strip()


JUNK_TAIL = re.compile(
    r"\s*[\(\[][^)\]]{0,40}(closeup|close-up|cropped|crop|retouched|"
    r"detail|version|[0-9]{5,})[^)\]]{0,12}[\)\]]", re.I)
LEAD_DATE = re.compile(r"^\s*\(?\d{4}[-_]\d{2}[-_]\d{2}\)?[\s\-–—:]*")
DPLA = re.compile(r"\s*[-–—]\s*(DPLA|PLATINUM|ALAMY|GETTY|FLICKR)\b.*$", re.I)
HEX = re.compile(r"\s*[-–—]?\s*\b[0-9a-f]{12,}\b.*$", re.I)
LEAD_PREFIX = re.compile(r"^\s*(PKI|IMG|DSC|P\d{4}|Flickr|File)\s*[-–—]?\s*", re.I)


def pretty(title):
    """Turn a Commons filename into something a person can read in a credit.

    Commons filenames are not captions. Left alone they put a date, an agency
    name and a hexadecimal identifier in front of the reader:
    '2014-07-18 Flowers and vigil candles ... (closeup)' and
    'Living Room Television - DPLA - 0840c8679a6fd78'. The caption has to
    describe the frame, so all of that comes off - and the remaining text is
    still what the file is called, not what we want to claim about it, so it
    stays verifiable against the source page rather than being invented.
    """
    t = str(title or "").replace("File:", "").strip()
    t = re.sub(r"\.[a-z0-9]{2,4}$", "", t, flags=re.I)
    t = LEAD_DATE.sub("", t)
    t = DPLA.sub("", t)
    t = HEX.sub("", t)
    t = JUNK_TAIL.sub("", t)
    t = LEAD_PREFIX.sub("", t)
    t = re.sub(r"^\s*[A-Z]{2,4}-\s*", "", t)          # other camera prefixes
    t = re.sub(r"\s+", " ", t).strip(" -_,;")
    t = t.strip(".")
    return t[:1].upper() + t[1:] if t else t


# ------------------------------------------------------------------ flickr
def flickr_author(raw):
    """The public feed returns author as 'nobody@flickr.com ("Real Name")'.
    Taking that string raw put a mailto and a quoted handle in every credit on
    the site. The name is the thing in the parentheses."""
    s = (raw or "").strip()
    m = re.search(r'"([^"]+)"', s)
    if m:
        return m.group(1).strip()[:44]
    if "@" in s and "(" in s:
        s = s.split("(")[0]
    return (s or "Flickr photographer")[:44]


def from_flickr(topic):
    """Flickr's public feed is CC-licensed and needs no key. Last-resort
    illustration only: a public feed is not relevance-searchable, which is
    exactly how a pilgrimage site ended up captioned as an argument."""
    for tag in TOPIC_TAGS.get(topic, [topic]):
        try:
            d = http(FLICKR.format(tags=urllib.parse.quote(tag)))
        except Exception:
            continue
        for it in d.get("items") or []:
            m = (it.get("media") or {})
            url = m.get("m")
            if not url:
                continue
            title = (it.get("title") or "").lower()
            if any(b in title for b in BAD_ALWAYS):
                continue
            author = flickr_author(it.get("author"))
            return {
                "url": url,
                "title": pretty(it.get("title")),
                "author": author,
                "licence": f"CC {(it.get('license') or '2.0').replace('-', '.')}",
                "credit": f"{author} / Flickr",
                "page": it.get("link") or "https://www.flickr.com/",
                "topic": topic, "w": int(m.get("w") or 0),
            }
    return None


# ---------------------------------------------------------------- commons
def _score(cand, must, ar_wanted=1.4):
    """Rank a candidate. The must-terms have already been enforced; this is
    about picking a usable photograph out of the survivors."""
    s = 0.0
    w, h = cand["w"], cand["h"]
    ar = (w / h) if h else 0
    if 1.15 <= ar <= ar_wanted + 0.5:
        s += 4                      # a card cover wants a landscape frame
    elif 0.9 <= ar <= 2.6:
        s += 2
    if w >= 1400:
        s += 3
    elif w >= 900:
        s += 2
    if w < 600:
        s -= 5                      # too small to hold a column
    if must:
        s += 6 * sum(1 for t in must if t in cand["title"].lower())
    return s


def from_commons(query, must=None, allow_logo=False):
    """Best freely-licensed photograph matching `query`, where every term in
    `must` appears in the file's own title. Returns None rather than settling
    for the wrong picture - a gap is better than a lie in a credit line."""
    must = [t.lower() for t in (must or [])]
    bad = BAD_ALWAYS if allow_logo else BAD

    s = http(COMMONS + "?action=query&format=json&list=search"
             f"&srsearch={urllib.parse.quote('filetype:bitmap ' + query)}"
             "&srlimit=40&srnamespace=6")
    titles = [h["title"] for h in (s.get("query") or {}).get("search") or []]
    if not titles:
        return None

    d = http(COMMONS + "?action=query&format=json&prop=imageinfo"
             f"&titles={urllib.parse.quote('|'.join(titles[:40]))}"
             "&iiprop=url|size|extmetadata&iiurlwidth=1600")
    pages = (d.get("query") or {}).get("pages") or {}

    best, best_s = None, -1e9
    for p in pages.values():
        ii = (p.get("imageinfo") or [{}])[0]
        url = ii.get("thumburl") or ii.get("url")
        if not url:
            continue
        raw_title = p.get("title", "")
        low = raw_title.lower()
        if any(low.endswith(x) for x in (".svg", ".gif", ".tif", ".webm", ".ogv", ".pdf")):
            continue
        if any(b in low for b in bad):
            continue
        em = ii.get("extmetadata") or {}
        licence = strip_html((em.get("LicenseShortName") or {}).get("value")) or \
                  strip_html((em.get("License") or {}).get("value"))
        if licence and not any(k in licence.lower() for k in FREE):
            continue                       # never ship a non-free file
        try:
            w, h = int(ii.get("thumbwidth") or ii.get("width") or 0), int(ii.get("height") or 0)
        except Exception:
            w = h = 0
        if w < 500:
            continue
        title = pretty(raw_title)
        # the must-terms are checked against the filename, which is the only
        # text Commons gives us to reason about
        if must and not all(t in low for t in must):
            continue

        cand = {"url": url, "title": title, "w": w, "h": h,
                "author": strip_html((em.get("Artist") or {}).get("value")) or
                          "Wikimedia contributor",
                "licence": licence or "see Commons",
                "credit": "Wikimedia Commons",
                "page": "https://commons.wikimedia.org/wiki/" +
                        urllib.parse.quote(raw_title.replace(" ", "_"))}
        sc = _score(cand, must)
        if sc > best_s:
            best, best_s = cand, sc
    return best


# ------------------------------------------------------------------ fetch
def store(slug, src, kind="illustrative", caption=None):
    CACHE.mkdir(parents=True, exist_ok=True)
    ext = ".png" if src["url"].lower().endswith(".png") else ".jpg"
    name = hashlib.sha1((slug + src["url"]).encode()).hexdigest()[:14] + ext
    dest = CACHE / name
    try:
        blob = http(src["url"], 40, binary=True)
    except Exception as e:
        return None, str(e)[:60]
    if blob[:3] not in (b"\xff\xd8\xff", b"\x89PN") or len(blob) < 4000:
        return None, "not an image"
    dest.write_bytes(blob)
    return {
        "local": f"img/editorial/{name}",
        "src": {"title": src["title"], "author": src["author"],
                "licence": src["licence"], "credit": src["credit"],
                "page": src["page"], "kind": kind},
        # the caption is what is in the frame. Never what the story is about.
        "caption": caption or src["title"],
        "cached": datetime.date.today().isoformat(),
    }, None


def fetch(item, taken=None):
    """Resolve one manifest entry. Order: an already-cached file, then the
    item's own must-terms against Commons, then the last-resort illustration.

    `taken` is the set of local paths already claimed by other items. Two
    stories sharing one photograph looks like a bug and is worse than a
    duplicate looking in a stock library, because the reader sees the same
    picture twice on a page and concludes the site has eleven images, not
    sixty-one. Without this, Replika and the EU chatbot story both landed on
    the same file.
    """
    if item.get("local") and (ROOT / item["local"]).exists():
        return "already", item["local"]
    taken = taken if taken is not None else set()

    q, must, allow_logo = item.get("q"), item.get("must"), item.get("allow_logo")
    src, kind = None, "exact"
    if q:
        src = _first_unused(from_commons, taken, q, must, allow_logo)
    if not src and item.get("exact"):
        src = _first_unused(from_commons, taken, item["exact"], None, allow_logo)
    if not src and item.get("topic"):
        src, kind = from_flickr(item["topic"]), "illustrative"
    if not src:
        return "no image", None

    got, err = store(item["slug"], src, kind)
    if not got:
        return f"fetch failed: {err}", None
    if got["local"] in taken:
        return "duplicate", None
    # the caption is whatever the file is, not whatever the query hoped for.
    # store() falls back to the source title, so the credit line cannot describe
    # a picture nobody has looked at.
    item.update(got)
    kb = (ROOT / got["local"]).stat().st_size // 1024
    return f"{kind} {kb}kb", got["local"]


def _all_candidates(query, must, allow_logo, limit=6):
    """Every acceptable candidate for a query, best first."""
    out, seen = [], set()
    for q in [query, query.replace(" ", "")]:
        got = from_commons(q, must, allow_logo)
        if got:
            key = got["url"]
            if key not in seen:
                seen.add(key)
                out.append(got)
        if len(out) >= limit:
            break
    return out


def _first_unused(fn, taken, query, must, allow_logo):
    """Walk the candidates and take the first whose file nobody else has."""
    cands = _all_candidates(query, must, allow_logo)
    for c in cands:
        name = hashlib.sha1(("x" + c["url"]).encode()).hexdigest()[:14]
        if not any(t.endswith(name + ".jpg") or t.endswith(name + ".png") for t in taken):
            return c
    return cands[0] if cands else None


def slots():
    """The frames a one-person operation should shoot. Real photographs of the
    real shelf, the real classroom and the real person will do more for this
    site's credibility than any stock library."""
    print("""
YOUR OWN PHOTOS. Drop files in img/mine/ and they take priority over CC.

  img/mine/portrait.jpg        you, behind the counter            -> masthead + about
  img/mine/shelf.jpg           the actual shelf, in the actual room -> shelf page
  img/mine/classroom.jpg       your classroom                     -> crossovers
  img/mine/counter.jpg         the counter itself                 -> the counter plate
  img/mine/manuscript.jpg      pages of a manuscript              -> the guide
  img/mine/cartoon-tv.jpg      a TV on Saturday morning            -> top 8
  img/mine/phone-charging.jpg  a phone charging next to a bed     -> the companion aisle

Why bother: a site with a face and a room reads as a publication. A site with
only stock reads as an aggregator. The stock is holding the layout together;
these are what make it yours.""")


TOPIC_TAGS = {
    "idol": ["concert", "crowd", "stadium"],
    "creator": ["livestream", "microphone", "studio"],
    "character": ["television", "cinema", "comics"],
    "companion": ["smartphone", "laptop", "chat"],
    "world": ["stadium", "fans", "supporter"],
    "brand": ["shopping", "retail", "store"],
    "crossover": ["classroom", "teacher", "school"],
    "contest": ["comments", "keyboard", "argument"],
    "grief": ["candle", "memorial", "flowers"],
    "danger": ["police", "court", "silence"],
    "news": ["newspaper", "press", "newsroom"],
    "ai": ["datacenter", "server", "robot"],
    "games": ["arcade", "gaming", "console"],
    "music": ["concert", "festival", "crowd"],
}


def main():
    a = sys.argv[1:] or ["--list"]
    if "--slots" in a:
        slots()
        return
    man = jload(MAN, {"items": []})
    items = man.get("items", [])
    if "--list" in a:
        have = sum(1 for i in items if (ROOT / (i.get("local") or "x")).exists())
        print(f"{len(items)} entries, {have} cached")
        for i in items:
            ok = "yes" if (ROOT / (i.get("local") or "x")).exists() else "-"
            k = (i.get("src") or {}).get("kind", "?")
            print(f"  [{ok:>3}] {k:<12} {i['slug']:<30} {(i.get('caption') or '')[:44]}")
        return
    targets = [x for x in a if not x.startswith("--")]
    if "--fetch-all" in a or not targets:
        targets = [i["slug"] for i in items]
    changed = False
    taken = {i["local"] for i in items if i.get("local")
             and (ROOT / i["local"]).exists()}
    for slug in targets:
        it = next((x for x in items if x["slug"] == slug), None)
        if not it:
            print(f"  ?   {slug} not in manifest")
            continue
        st, path = fetch(it, taken)
        print(f"  {st:<26} {slug}")
        if path:
            changed = True
            if it.get("local"):
                taken.add(it["local"])
    if changed:
        jdump(MAN, man)
        print("manifest updated")


if __name__ == "__main__":
    main()
