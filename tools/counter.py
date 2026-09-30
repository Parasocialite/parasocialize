#!/usr/bin/env python3
"""
counter.py — the sweeper. The part that actually does the work.

  SWEEPER -> CLASSIFIER -> DRAFTER -> RANKER -> PUBLISHER

  Machines find, read, judge and draft. Nothing reaches the shelf without a
  human signing it. The publisher's only job is to put drafts in the queue
  at desk/index.html. It never writes to cards[].

  Stdlib only. No pip. A feed that times out is logged and skipped, never fatal.

  Env:
    PARASOCIALIZE_KEY     model api key. Without it the sweeper still runs and
                          files raw candidates flagged needs="lens" so nothing
                          is silently dropped.
    PARASOCIALIZE_PROVIDER  anthropic (default) | openai | compatible | none
    PARASOCIALIZE_MODEL   model id
    PARASOCIALIZE_BASE    base url, for provider=compatible
    PARASOCIALIZE_DRYRUN  1 = classify nothing, just count
"""
import json, os, re, sys, time, ssl, hashlib, datetime, pathlib, urllib.request, urllib.parse, urllib.error

ROOT = pathlib.Path(__file__).resolve().parent.parent
FEEDS = ROOT / "tools" / "feeds.json"
SHOP = ROOT / "data" / "shop.json"
SWEEP = ROOT / "data" / "sweep.json"
DESK = ROOT / "data" / "queue.json"
SEEN = ROOT / "data" / "seen.json"
BINNED = ROOT / "data" / "binned.json"

UA = "ParasocializeCounter/2.0 (+https://www.parasocialize.com)"
TIMEOUT = 15

PROVIDER = os.environ.get("PARASOCIALIZE_PROVIDER", "anthropic").lower()
KEY = os.environ.get("PARASOCIALIZE_KEY", "").strip()
MODEL = os.environ.get("PARASOCIALIZE_MODEL", "claude-sonnet-5" if PROVIDER == "anthropic" else "gpt-4o")
BASE = os.environ.get("PARASOCIALIZE_BASE", "").strip()
DRYRUN = os.environ.get("PARASOCIALIZE_DRYRUN", "") not in ("", "0", "false")

SECTIONS = ["idol", "creator", "character", "companion", "world", "brand", "crossover", "contest", "grief", "danger"]
LAWS = {
    1: "binding-is-public",
    2: "clerks-beat-algorithms",
    3: "someone-holds-the-dream",
    4: "grief-when-companion-changes",
    5: "pay-for-proximity-open-eyes",
    6: "characters-move-in",
    7: "audit-quarterly",
}

VOICE = """You are the classifier for PARASOCIALIZE, a field guide to one-sided attachment.

THE SITE'S JOB
One-sided attachment shows up everywhere, not just in fandom: idols, creators,
fictional characters, AI companions, lore-heavy worlds, loyalty programmes, sport,
politics, religion, and the people you are supposed to be able to reach anyway
(teachers, doctors, judges, landlords, local news anchors). The last category is
the one nobody writes about and it matters most.

YOUR JOB
Read a headline and snippet. Decide whether there is genuine one-sided attachment
in it, which section it belongs to, which of the seven laws it trips, and which
piece of the curator's shelf is the evidence that got there first.

SEVEN LAWS
1 Binding is public - performing a self until it holds, where it can be witnessed.
2 Clerks beat algorithms - being known by someone who was paying attention on purpose.
3 Someone holds the dream - who owns the building where thousands of people feel things.
4 Grief is real when the companion changes - endings, updates, deaths, retirements.
5 Pay for proximity with open eyes - closeness sold, metered, or made a subscription.
6 Characters move in - the fictional thing rents space in someone's head.
7 Audit quarterly - the reader audits their own ties.

SHELF (the curator's work, the evidence base)
company-dreamer (novel), dreamarched (novel), regulated-brightness (poetry),
kempe (free essay, medieval binding), pennywise (video, horror attachment),
michael (video), insight-company (video, surveillance as attention),
old-school (video, before the feed), pod (Parasocialize podcast),
athp (All The Horrible Things podcast, a catalogue of beloved media that hurt people),
us (album: made inside a dead machine, transparently), fallgate (album).

RULES
- Reject anything with no real attachment in it. A product review is not a story.
- Reject a story already about the site, the curator, or another card on the shelf.
- Never pathologize a reader. Attachment is real. Do not call it unhealthy, sick,
  creepy or an addiction in the one_line or take.
- The take is 2 to 3 sentences, first person, in the curator's voice: warm, wry,
  unsentimental, specific. It should sound like a person who used to work in a
  video store, not like a press release and not like a lecture.
- The take must land somewhere, not summarise the news.
- one_line is one sentence, under 110 characters, written as if on a library
  card. No clickbait, no question marks.

A VERY IMPORTANT EXCEPTION
If the story does not contain any one-sided attachment, return is_one_sided false
and say why in one short phrase. A big false-negative cost is better than a shelf
full of cards that are really just news. This site is only worth anything if it
stays narrow."""


def jload(p, default):
    try:
        return json.loads(pathlib.Path(p).read_text(encoding="utf-8"))
    except Exception:
        return default


def jdump(p, obj):
    pathlib.Path(p).parent.mkdir(parents=True, exist_ok=True)
    pathlib.Path(p).write_text(json.dumps(obj, indent=2, ensure_ascii=False), encoding="utf-8")


def now():
    return datetime.datetime.now(datetime.timezone.utc)


def decode_bytes(raw):
    """Feeds lie about their charset. Try utf-8, then cp1252, then give up
    gracefully - a mangled quote is not worth crashing a sweep over."""
    if isinstance(raw, str):
        return raw
    for enc in ("utf-8", "cp1252", "latin-1"):
        try:
            return raw.decode(enc)
        except UnicodeDecodeError:
            continue
    return raw.decode("utf-8", "replace")


def get(url):
    req = urllib.request.Request(url, headers={
        "User-Agent": UA,
        "Accept": "application/rss+xml, application/atom+xml, application/json, text/xml, */*",
    })
    ctx = ssl.create_default_context()
    with urllib.request.urlopen(req, timeout=TIMEOUT, context=ctx) as r:
        return decode_bytes(r.read())


# --------------------------------------------------------------------- SWEEPER
def strip_tags(s):
    s = re.sub(r"<[^>]+>", " ", s or "")
    s = html_unescape(s)
    return re.sub(r"\s+", " ", s).strip()


def html_unescape(s):
    import html as _h
    return _h.unescape(s)


def real_domain(url, feed):
    """The whole point: resolve what the feed actually is, so tiers work."""
    try:
        host = urllib.parse.urlparse(url).netloc.lower().replace("www.", "")
    except Exception:
        host = ""
    if host.startswith("news.google"):
        return "news.google.com"  # unresolved redirect. logged, never trusted.
    if host in ("reddit.com", "old.reddit.com", "np.reddit.com"):
        m = re.search(r"/r/([^/]+)/", url)
        return f"reddit.com/r/{m.group(1)}" if m else "reddit.com"
    return host or feed.get("id", "unknown")


def unwrap_bing(link):
    """Bing News wraps the real url in a query param. Without this the domain
    is www.bing.com for every story and the tier table is meaningless."""
    if "bing.com/news/apiclick" not in (link or ""):
        return link
    qs = urllib.parse.urlparse(link).query
    real = urllib.parse.parse_qs(qs).get("url", [""])[0]
    return real or link


def sweep_bing(cfg, budget):
    """One query per section. This is how the taxonomy earns its keep - each section
    is swept on its own terms, which is the only reason CROSSOVER gets covered."""
    bing = cfg.get("bing", {})
    found, telemetry = [], []
    ua_hdr = {"User-Agent": UA, "Accept": "application/rss+xml, */*"}
    for section, q in (bing.get("q") or {}).items():
        url = ("https://www.bing.com/news/search?q="
               + urllib.parse.quote_plus(q) + "&format=RSS")
        t0 = time.time()
        try:
                req = urllib.request.Request(url, headers=ua_hdr)
                with urllib.request.urlopen(req, timeout=TIMEOUT,
                                            context=ssl.create_default_context()) as r:
                    text = decode_bytes(r.read())
        except Exception as ex:
            telemetry.append({"feed": f"bing:{section}", "ok": False,
                              "error": str(ex)[:140]})
            continue
        kept = 0
        for m in re.finditer(r"<item>(.*?)</item>", text, re.S | re.I):
            blk = m.group(1)
            ti = re.search(r"<title>(?:<!\[CDATA\[)?(.*?)(?:\]\]>)?</title>", blk, re.S | re.I)
            lk = re.search(r"<link>(.*?)</link>", blk, re.S | re.I)
            de = re.search(r"<description>(?:<!\[CDATA\[)?(.*?)(?:\]\]>)?</description>", blk, re.S | re.I)
            dt = re.search(r"<pubDate>(.*?)</pubDate>", blk, re.S | re.I)
            src = re.search(r"<News:Source>(.*?)</News:Source>", blk, re.S | re.I)
            if not (ti and lk):
                continue
            real = html_unescape(unwrap_bing(html_unescape(lk.group(1).strip())))
            if not real.startswith("http"):
                continue
            it = {
                "title": strip_tags(ti.group(1)),
                "snippet": strip_tags(de.group(1))[:600] if de else "",
                "url": real,
                "at": (dt.group(1).strip()[:10] if dt else ""),
                "feed": f"bing:{section}",
                "feed_name": src.group(1).strip() if src else "Bing News",
                "queried_section": section,
                "tier": 1 if src else 2,
                "domain": real_domain(real, {"id": "bing"}),
                "unresolved": "bing.com" in real or not real.startswith("http"),
            }
            low = (it["title"] + " " + it["snippet"]).lower()
            if any(j in low for j in cfg.get("junk", [])):
                continue
            it["id"] = hashlib.sha1(it["url"].encode()).hexdigest()[:16]
            found.append(it)
            kept += 1
            if kept >= 25:
                break
        telemetry.append({"feed": f"bing:{section}", "ok": True, "items": kept,
                          "ms": int((time.time() - t0) * 1000), "query": q})
        time.sleep(0.3)
        if len(found) >= budget:
            break
    return found, telemetry


def sweeper(cfg):
    found, telemetry = [], []
    for f in cfg.get("feeds", []):
        url, fid = f.get("url", ""), f.get("id", "")
        if not url:
            continue
        t0 = time.time()
        try:
            raw = get(url)
        except Exception as ex:
            telemetry.append({"feed": fid, "ok": False, "error": str(ex)[:140]})
            continue
        items = []
        try:
            if f.get("json"):
                blob = json.loads(raw)
                for ch in (blob.get("data", {}).get("children") or [])[:40]:
                    d = ch.get("data", {})
                    link = d.get("url_overridden_by_dest") or (
                        f"https://www.reddit.com{d.get('permalink','')}")
                    items.append({
                        "title": strip_tags(d.get("title", "")),
                        "snippet": strip_tags(d.get("selftext", ""))[:600],
                        "url": link,
                        "at": datetime.datetime.fromtimestamp(
                            d.get("created_utc", 0), datetime.timezone.utc).strftime("%Y-%m-%d"),
                    })
            else:
                for m in re.finditer(r"<item>(.*?)</item>|<entry>(.*?)</entry>",
                                     raw, re.S | re.I):
                    blk = m.group(1) or m.group(2) or ""
                    ti = re.search(r"<title>(?:<!\[CDATA\[)?(.*?)(?:\]\]>)?</title>", blk, re.S | re.I)
                    lk = re.search(r"<link[^>]*>(?:<!\[CDATA\[)?(.*?)(?:\]\]>)?</link>", blk, re.S | re.I)
                    if not (ti and lk):
                        lk = re.search(r'<link[^>]*href="([^"]+)"', blk, re.I)
                    de = (re.search(r"<description>(?:<!\[CDATA\[)?(.*?)(?:\]\]>)?</description>",
                                    blk, re.S | re.I)
                          or re.search(r"<summary[^>]*>(.*?)</summary>", blk, re.S | re.I)
                          or re.search(r"<content[^>]*>(.*?)</content>", blk, re.S | re.I))
                    dt = (re.search(r"<pubDate>(.*?)</pubDate>", blk, re.S | re.I)
                          or re.search(r"<updated>(.*?)</updated>", blk, re.S | re.I)
                          or re.search(r"<published>(.*?)</published>", blk, re.S | re.I))
                    if not (ti and lk):
                        continue
                    items.append({
                        "title": strip_tags(ti.group(1)),
                        "snippet": strip_tags(de.group(1))[:600] if de else "",
                        "url": lk.group(1).strip(),
                        "at": (dt.group(1).strip()[:25] if dt else ""),
                    })
        except Exception as ex:
            telemetry.append({"feed": fid, "ok": False, "error": f"parse: {str(ex)[:120]}"})
            continue

        kept = 0
        for it in items:
            if not it["title"] or len(it["title"]) < 18:
                continue
            low = (it["title"] + " " + it["snippet"]).lower()
            if any(j in low for j in cfg.get("junk", [])):
                continue
            it["feed"] = fid
            it["feed_name"] = f.get("name", fid)
            it["tier"] = f.get("tier", 3)
            it["domain"] = real_domain(it["url"], f)
            it["unresolved"] = it["domain"] == "news.google.com"
            it["id"] = hashlib.sha1(it["url"].encode()).hexdigest()[:16]
            found.append(it)
            kept += 1
        telemetry.append({"feed": fid, "ok": True, "items": kept,
                          "ms": int((time.time() - t0) * 1000)})
    return found, telemetry


# ----------------------------------------------------------------- CLASSIFIER
def call_model(prompt, want_json=True):
    if DRYRUN or not KEY or PROVIDER in ("none", ""):
        return None
    try:
        if PROVIDER == "anthropic":
            body = {
                "model": MODEL, "max_tokens": 1200,
                "system": [{"type": "text", "text": VOICE, "cache_control": {"type": "ephemeral"}}],
                "messages": [{"role": "user", "content": prompt}],
            }
            if want_json:
                body["tools"] = [{
                    "name": "file", "description": "File this story, or refuse it.",
                    "input_schema": {
                        "type": "object",
                        "properties": {
                            "is_one_sided": {"type": "boolean"},
                            "why_not": {"type": "string"},
                            "section": {"type": "string", "enum": SECTIONS},
                            "law": {"type": "integer", "enum": [1, 2, 3, 4, 5, 6, 7]},
                            "shelf": {"type": "string"},
                            "confidence": {"type": "number"},
                            "headline": {"type": "string"},
                            "one_line": {"type": "string"},
                            "take": {"type": "string"},
                        },
                        "required": ["is_one_sided", "confidence", "headline"],
                    }}]
                body["tool_choice"] = {"type": "tool", "name": "file"}
            url = BASE or "https://api.anthropic.com/v1/messages"
            req = urllib.request.Request(url, data=json.dumps(body).encode(), headers={
                "x-api-key": KEY, "anthropic-version": "2023-06-01",
                "content-type": "application/json"})
        else:
            url = BASE or ("https://api.openai.com/v1/chat/completions"
                           if PROVIDER == "openai" else BASE)
            if not url:
                return None
            body = {
                "model": MODEL, "max_tokens": 1200,
                "response_format": {"type": "json_object"},
                "messages": [
                    {"role": "system", "content": VOICE +
                     "\n\nReply with JSON only, keys: is_one_sided, why_not, section, law, "
                     "shelf, confidence, headline, one_line, take."},
                    {"role": "user", "content": prompt}],
            }
            req = urllib.request.Request(url, data=json.dumps(body).encode(), headers={
                "Authorization": f"Bearer {KEY}", "content-type": "application/json"})
        with urllib.request.urlopen(req, timeout=60, context=ssl.create_default_context()) as r:
            data = json.loads(r.read())
        if PROVIDER == "anthropic":
            for blk in data.get("content", []):
                if blk.get("type") == "tool_use":
                    return blk.get("input")
            return None
        txt = data["choices"][0]["message"].get("content") or "{}"
        m = re.search(r"\{.*\}", txt, re.S)
        return json.loads(m.group(0)) if m else None
    except Exception as ex:
        sys.stderr.write(f"  model error: {str(ex)[:200]}\n")
        return None


def classify(it, shelf_ids):
    # the per-section Bing query already told us where it thinks this belongs.
    # handing that to the model as a hint turns a guess into a check.
    hint = it.get("queried_section")
    hint_line = ""
    if hint and hint != "general":
        hint_line = (f"\nThis story was found by a search written specifically for section "
                     f"'{hint}'. Strong hint, not gospel - if the attachment is really "
                     f"somewhere else, say so and file it there.")

    prompt = f"""TITLE: {it['title']}
SOURCE: {it['feed_name']} ({it['domain']})
SNIPPET: {it['snippet'] or '(none)'}{hint_line}

Is there genuine one-sided attachment in this? If yes, file it.
Shelf ids you may use: {', '.join(shelf_ids)} (or null if none of them are the evidence).
Remember: the CROSSOVER section (7) is for attachment to people you are supposed to be
able to reach anyway. The DANGER section (10) is only for when it turned criminal."""
    out = call_model(prompt)
    if not out:
        return None
    if not out.get("is_one_sided", False):
        return {"ok": False, "why": (out.get("why_not") or "no attachment in it")[:120]}
    if out.get("section") not in SECTIONS:
        return {"ok": False, "why": "section out of range"}
    if out.get("law") not in LAWS:
        return {"ok": False, "why": "law out of range"}
    return {"ok": True, "out": out}


def recent(iso, days):
    """Archive dumps are not news. Only ask the model about things that could
    plausibly still be news - this is the single biggest cost control here."""
    if not iso:
        return True  # unknown date: let the model judge
    try:
        d = datetime.datetime.fromisoformat(iso[:10]).date()
    except Exception:
        return True
    return (datetime.date.today() - d).days <= days


# -------------------------------------------------------------------- RANKER
def words(s):
    return set(re.findall(r"[a-z]{4,}", (s or "").lower()))


def overlap(a, b):
    wa, wb = words(a), words(b)
    if not wa or not wb:
        return 0.0
    return len(wa & wb) / min(len(wa), len(wb))


def rank(it, drafts, shop):
    # duplicate of something already on the shelf?
    for c in shop.get("cards", []):
        if overlap(it["title"], c["headline"]) > 0.55:
            return {"dup_of": c["slug"]}
    for d in drafts:
        if overlap(it["title"], d["headline"]) > 0.55:
            return {"dup_of": d["id"]}
    domains = {d["domain"] for d in drafts if d.get("domain") == it["domain"]}
    weight = {"1": 1.0, "2": 0.75, "3": 0.5}.get(str(it.get("tier")), 0.5)
    vel = min(6, len(domains))
    return {"score": round(40 + (vel * 7) + (weight * 20), 1), "independent_domains": vel}


# ----------------------------------------------------------------- PUBLISHER
def main():
    cfg = jload(FEEDS, {})
    shop = jload(SHOP, {})
    seen = jload(SEEN, {"ids": {}})
    queue = jload(DESK, shop.get("queue", []))

    started = now()
    print(f"counter: sweep starting, provider={PROVIDER} model={MODEL}"
          + ("  [DRY RUN - no model call]" if (DRYRUN or not KEY) else ""))

    # Bing per-section queries first: real publisher urls, real tiers, and the
    # only way CROSSOVER and DANGER ever get swept at all.
    found, tel_bing = sweep_bing(cfg, budget=160)
    found_r, tel_rss = sweeper(cfg)
    found += found_r
    telemetry = tel_bing + tel_rss
    ok = sum(1 for t in telemetry if t.get("ok"))
    print(f"  swept {ok}/{len(telemetry)} feeds ({len(tel_bing)} per-section queries, "
          f"{len(tel_rss)} publications), {len(found)} candidate items")

    # dedupe across feeds by url
    uniq, seen_url = [], set()
    for i in found:
        if i["url"] in seen_url:
            continue
        seen_url.add(i["url"])
        uniq.append(i)
    found = uniq

    fresh = [i for i in found if i["id"] not in seen["ids"]]
    print(f"  {len(fresh)} never seen before")

    shelf_ids = [s["id"] for s in shop.get("shelf", [])]
    drafts, rejected = [], []
    # every model call costs money. budget, not greed.
    budget = int(os.environ.get("PARASOCIALIZE_BUDGET", "12"))
    # rejections cost a call too. this is the real ceiling on the hourly bill.
    max_calls = int(os.environ.get("PARASOCIALIZE_MAX_CALLS", "30"))
    calls = 0
    recency_days = int(os.environ.get("PARASOCIALIZE_RECENCY_DAYS", "6"))
    # stories the model already turned down. don't pay twice to be told no.
    binned = jload(BINNED, {"titles": {}})
    binned_titles = binned.get("titles", {})

    for it in fresh:
        if len(drafts) >= budget:
            break
        seen["ids"][it["id"]] = {
            "t": started.isoformat(), "title": it["title"][:120],
            "domain": it["domain"], "out": bool(drafts) or None,
        }
        if it.get("unresolved"):
            rejected.append({"title": it["title"][:90], "why": "source domain unresolved"})
            continue
        if not recent(it.get("at", ""), recency_days):
            rejected.append({"title": it["title"][:90], "why": "older than the recency gate"})
            continue

        # cheap dedupe on the title, before we spend a single token on it
        th = hashlib.sha1(" ".join(sorted(words(it["title"]))[:12]).encode()).hexdigest()[:12]
        if th in binned_titles:
            rejected.append({"title": it["title"][:90],
                             "why": f"previously binned: {binned_titles[th]}"})
            continue

        c = classify(it, shelf_ids)
        calls += 1
        if calls >= max_calls:
            rejected.append({"title": "…", "why": "call budget spent for this sweep"})
            break
        if c is None:
            # no model available: file it raw, flagged, so nothing is lost
            drafts.append({
                "id": f"raw-{it['id'][:8]}", "state": "awaiting_lens",
                "headline": it["title"], "one_line": it["snippet"][:140] or "(no snippet)",
                "take": "", "section": None, "law": None, "shelf": None,
                "conf": 0.0, "domain": it["domain"], "feed": it["feed_name"],
                "url": it["url"], "at": it["at"],
                "why": "No model key set. Filed raw. Needs a human to point it at an section.",
            })
            continue
        if not c.get("ok"):
            why = c.get("why", "?")
            binned_titles[th] = why
            rejected.append({"title": it["title"][:90], "why": why})
            continue

        o = c["out"]
        r = rank(it, drafts, shop)
        if r.get("dup_of"):
            rejected.append({"title": it["title"][:90], "why": f"already on shelf: {r['dup_of']}"})
            continue

        drafts.append({
            "id": f"d-{it['id'][:8]}",
            "state": "awaiting",
            "headline": o.get("headline") or it["title"],
            "one_line": o.get("one_line", ""),
            "take": o.get("take", ""),
            "section": o["section"], "law": o["law"], "shelf": o.get("shelf") or None,
            "conf": round(float(o.get("confidence", 0)), 2),
            "domain": it["domain"], "feed": it["feed_name"],
            "url": it["url"], "at": it["at"],
            "score": r.get("score"), "independent_domains": r.get("independent_domains"),
            "why": (f"Section {o['section']}, law {o['law']}."
                    + (f" Shelf evidence: {o['shelf']}." if o.get("shelf") else "")
                    + f" {r.get('independent_domains',0)} independent domain(s) this run."),
        })
        time.sleep(0.4)

    if len(binned_titles) > 1500:
        binned_titles = dict(list(binned_titles.items())[-800:])
    jdump(BINNED, {"titles": binned_titles})

    drafts.sort(key=lambda d: -(d.get("conf") or 0))
    # keep anything still waiting on a human - including raw unlensed filings.
    # dropping them silently loses real stories.
    queue = [d for d in queue
             if d.get("state") in ("awaiting", "awaiting_lens")] + drafts
    queue = queue[:60]
    jdump(DESK, queue)

    # keep seen from growing forever
    if len(seen["ids"]) > 4000:
        seen["ids"] = dict(list(seen["ids"].items())[-2500:])
    jdump(SEEN, seen)

    sweep = {
        "last_run": started.isoformat(),
        "duration_s": round((now() - started).total_seconds(), 1),
        "feeds_total": len(telemetry), "feeds_ok": ok,
        "candidates": len(found), "fresh": len(fresh),
        "drafted": len([d for d in drafts if d.get("state") == "awaiting"]),
        "filed_raw": len([d for d in drafts if d.get("state") == "awaiting_lens"]),
        "rejected": len(rejected),
        "awaiting_signoff": len([d for d in queue if d.get("state", "").startswith("awaiting")]),
        "model": f"{PROVIDER}/{MODEL}" if KEY else "none (raw filing only)",
        "telemetry": telemetry,
        "rejected_sample": rejected[:12],
    }
    jdump(SWEEP, sweep)

    # keep seen from growing forever
    if len(seen["ids"]) > 4000:
        seen["ids"] = dict(list(seen["ids"].items())[-2500:])

    print(f"  drafted {sweep['drafted']}, filed raw {sweep['filed_raw']}, "
          f"rejected {sweep['rejected']}")
    print(f"  seen: {len(seen['ids'])} urls remembered · binned: {len(binned_titles)} titles")
    print(f"  queue: {sweep['awaiting_signoff']} waiting for the clerk")
    if not KEY and not DRYRUN:
        print("  ! no PARASOCIALIZE_KEY set. Items are being filed raw with no lens.")
    print("  nothing was published. sign off at desk/index.html")


if __name__ == "__main__":
    main()
