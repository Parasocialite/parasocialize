#!/usr/bin/env python3
"""editor.py - the daily edition: a figure, a new top 8, and eight ways forward.

WHAT THIS IS FOR
The site had three daily features that were not actually daily. The
parasocialite rotated through a fixed roster that included a game show; the
top 8 alternated two lists written months apart, so the cartoons list came
round again; and the eight "ways it shows up" pages changed only when somebody
edited a placement. The result was a site that was correct and not current.

This is the agent that produces one edition per UTC day:

  * a **figure** - a real person or a fictional character, never a format, a
    show or an institution - preferably named in today's wires, otherwise the
    record's case for today's theme;
  * a **new top 8** - eight ranked entries drawn from the encyclopedia, so
    every claim is already sourced on its own page, framed by a theme chosen
    from the news when one fits and by rotation when none does;
  * a **daily pick for each of the eight ways** - one story or entry per
    attachment category, with the placement reason printed and the previous
    week's picks visible under it.

WHAT IT WILL NOT DO
It does not write a new fact. It does not invent a citation, a date, a name or
a quotation. The prose on a generated top 8 is the entry's own summary and
significance, cleaned and clipped; the list's framing is hand-written in
data/top8_themes.json; the figure's breakdown is the entry's summary unless the
old roster already had a better line. The only new sentences are connective:
the date, the theme's stated argument, and a headline and link from a real
wire item. That is the boundary this site exists to keep.

NEWS
Primary source is Google News RSS, queried for the last three to fourteen
days. It is public, current and returns a publisher link. The queue built by
tools/counter.py is the fallback when the fetch fails. A day with no wire
match is still a day: the theme rotates and the figure is chosen from the
record, and the page says which happened.

USAGE
    python tools/editor.py              # build today's edition if absent
    python tools/editor.py --refresh    # rebuild today's edition in place
    python tools/editor.py --dry-run    # print selections, write nothing
    python tools/editor.py --check      # validate today's edition, write nothing
"""
from __future__ import annotations

import argparse
import datetime
import email.utils
import hashlib
import html
import json
import pathlib
import re
import sys
import urllib.parse
import urllib.request

ROOT = pathlib.Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
TOOLS = ROOT / "tools"
sys.path.insert(0, str(TOOLS))
import atlas  # noqa: E402  (the closed medium list)

EDITORIAL = DATA / "editorial_today.json"
WAYS_HISTORY = DATA / "ways_history.json"
FIGURES = DATA / "parasocialite.json"
THEMES = DATA / "top8_themes.json"
FEATURES = DATA / "features.json"
TOP8_HISTORY = DATA / "top8_history.json"
PSOTD_HISTORY = DATA / "parasocialite_history.json"

UA = "Mozilla/5.0 (compatible; ParasocializeEditor/1.0)"
QUERIES = (
    ("parasocial", "when:3d"),
    ("celebrity fandom", "when:3d"),
    ("AI companion", "when:7d"),
    ("celebrity death", "when:3d"),
    ("K-pop fandom", "when:7d"),
    ("reality TV fandom", "when:7d"),
    ("virtual influencer", "when:14d"),
    ("fan mail", "when:14d"),
    ("sports fans", "when:3d"),
    ("theatre fandom", "when:14d"),
)
MONTHS = ("JAN", "FEB", "MAR", "APR", "MAY", "JUN",
          "JUL", "AUG", "SEP", "OCT", "NOV", "DEC")


def utc_today() -> datetime.date:
    return datetime.datetime.now(datetime.timezone.utc).date()


def fmt_date(iso: str) -> str:
    d = datetime.date.fromisoformat(str(iso)[:10])
    return f"{d.day:02d} {MONTHS[d.month - 1]} {d.year}"


def load(path: pathlib.Path, default):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return default


def save(path: pathlib.Path, obj) -> None:
    path.write_text(json.dumps(obj, ensure_ascii=False, indent=1) + "\n",
                    encoding="utf-8")


def plain(s) -> str:
    s = html.unescape(str(s or ""))
    s = re.sub(r"<[^>]+>", " ", s)
    s = s.replace("**", "").replace("*", "").replace("`", "")
    return " ".join(s.split())


def clip_sentences(s, limit: int) -> str:
    """A sentence boundary, or a clause, but never half a word."""
    s = plain(s)
    if len(s) <= limit:
        return s
    out = ""
    for part in re.split(r"(?<=[.!?])\s+", s):
        if not out:
            out = part
            continue
        if len(out) + 1 + len(part) <= limit:
            out += " " + part
        else:
            break
    if len(out) > limit:
        cut = out[:limit]
        m = None
        for m in re.finditer(r"[,;:]\s", cut):
            pass
        if m and m.start() > max(80, limit // 2):
            cut = cut[:m.start()]
        out = cut.rstrip(" ,;:") + "."
    return out.strip()


def year_label(e) -> str:
    y = e.get("year")
    ye = e.get("year_end")
    if y is None:
        return ""
    y = int(y)
    ye = int(ye) if ye not in (None, "") else None

    def one(n):
        return f"{abs(n)} BC" if n < 0 else str(n)

    if ye and ye != y:
        return f"{one(y)}–{one(ye)}"
    return one(y)


def entry_show(e) -> str:
    media = e.get("medium") or []
    if isinstance(media, str):
        media = [media]
    labels = []
    for m in media:
        label = atlas.MEDIA_LABEL.get(m, str(m).replace("_", " "))
        if label and label not in labels:
            labels.append(label)
    span = year_label(e)
    if labels and span:
        return f"{' / '.join(labels[:2])} · {span}"
    return " / ".join(labels[:2]) or span or "the record"


def stable(*parts) -> float:
    h = hashlib.sha1("|".join(str(p) for p in parts).encode("utf-8")).hexdigest()
    return int(h[:10], 16) / float(0xFFFFFFFFFF)


# ------------------------------------------------------------------ the wires
def parse_pubdate(s):
    try:
        d = email.utils.parsedate_to_datetime(s)
        if d.tzinfo is None:
            d = d.replace(tzinfo=datetime.timezone.utc)
        return d.astimezone(datetime.timezone.utc)
    except Exception:
        return None


def fetch_google_news() -> list[dict]:
    out = []
    for query, window in QUERIES:
        url = ("https://news.google.com/rss/search?q="
               + urllib.parse.quote(f"{query} {window}")
               + "&hl=en-US&gl=US&ceid=US:en")
        try:
            req = urllib.request.Request(url, headers={"User-Agent": UA})
            raw = urllib.request.urlopen(req, timeout=15).read()
            text = raw.decode("utf-8", "replace")
        except Exception:
            continue
        for block in re.findall(r"<item>(.*?)</item>", text, re.S):
            t = re.search(r"<title>(.*?)</title>", block, re.S)
            l = re.search(r"<link>(.*?)</link>", block, re.S)
            p = re.search(r"<pubDate>(.*?)</pubDate>", block, re.S)
            src = re.search(
                r"<source[^>]*>(.*?)</source>", block, re.S)
            if not (t and l):
                continue
            title = plain(t.group(1))
            link = html.unescape(l.group(1).strip())
            publisher = plain(src.group(1)) if src else ""
            if publisher:
                for sep in (" - ", " – ", " — "):
                    suffix = sep + publisher
                    if title.endswith(suffix):
                        title = title[:-len(suffix)].strip()
                        break
            if not title or not link.startswith("http"):
                continue
            when = parse_pubdate(p.group(1)) if p else None
            out.append({"title": title, "url": link,
                        "publisher": publisher,
                        "at": when.isoformat() if when else "",
                        "query": query})
    # Dedupe by title; newest first.
    seen, uniq = set(), []
    for n in sorted(out, key=lambda x: x["at"], reverse=True):
        key = re.sub(r"\W+", "", n["title"].lower())[:80]
        if key in seen:
            continue
        seen.add(key)
        uniq.append(n)
    return uniq


def queue_news() -> list[dict]:
    q = load(DATA / "queue.json", [])
    out = []
    for x in q:
        title = plain(x.get("headline"))
        url = str(x.get("url") or "").strip()
        if not title or not url or title.lower().startswith("draft:"):
            continue
        out.append({"title": title, "url": url,
                    "publisher": plain(x.get("domain") or x.get("feed") or ""),
                    "at": "", "query": "queue"})
    return out


def gather_news() -> tuple[list[dict], str]:
    live = fetch_google_news()
    if len(live) >= 8:
        # Keep the freshest 40; the edition only cites a handful.
        return live[:40], "google-news-rss"
    fallback = queue_news()
    return (live + fallback)[:40], ("google-news-rss+queue" if live
                                    else "queue-fallback")


def news_age_days(n) -> float:
    if not n.get("at"):
        return 30.0
    try:
        d = datetime.datetime.fromisoformat(n["at"])
        if d.tzinfo is None:
            d = d.replace(tzinfo=datetime.timezone.utc)
        return max(0.0, (datetime.datetime.now(datetime.timezone.utc)
                         - d).total_seconds() / 86400)
    except ValueError:
        return 30.0


def recency_weight(n) -> float:
    a = news_age_days(n)
    if a <= 2:
        return 1.0
    if a <= 7:
        return 0.8
    if a <= 14:
        return 0.5
    return 0.2


# ---------------------------------------------------------------- selection
def history_days(path):
    return load(path, {"days": []}).get("days") or []


def used_entries(days, window=14, today=None):
    """Entry ids the top 8 carried recently, so a daily list is actually new."""
    cutoff = (today or utc_today()) - datetime.timedelta(days=window)
    used = set()
    for d in days:
        try:
            if datetime.date.fromisoformat(str(d.get("date"))[:10]) < cutoff:
                continue
        except ValueError:
            continue
        for item in d.get("items") or []:
            used.add(str(item))
    return used


def last_used_theme(days) -> dict:
    last = {}
    for d in days:
        t = d.get("theme")
        if t:
            last[t] = max(last.get(t, ""), str(d.get("date") or ""))
    return last


def theme_match(theme, e, placement) -> tuple[bool, float, int]:
    text = " ".join(str(e.get(k) or "") for k in
                    ("title", "summary", "significance", "era")).lower()
    media = e.get("medium") or []
    if isinstance(media, str):
        media = [media]
    sections = e.get("sections") or []
    if isinstance(sections, str):
        sections = [sections]
    kw = [k.lower() for k in theme.get("keywords") or []]
    hits = sum(1 for k in kw if k in text)
    med = 1 if any(m in media for m in (theme.get("media") or [])) else 0
    cat = 1 if placement and placement.get("cat") in (theme.get("cats") or []) else 0
    sec = 1 if any(s in sections for s in (theme.get("sections") or [])) else 0
    yr = e.get("year")
    in_years = True
    if theme.get("year_min") is not None:
        in_years = in_years and yr is not None and int(yr) >= theme["year_min"]
    if theme.get("year_max") is not None:
        in_years = in_years and yr is not None and int(yr) <= theme["year_max"]
    year_filter = (theme.get("year_min") is not None or
                   theme.get("year_max") is not None)
    structural = any(theme.get(k) for k in ("media", "cats", "sections")) or year_filter
    if structural:
        # A medium, category, section or year is the theme's spine. One
        # keyword hit is not enough to join a sport list; two are evidence
        # that the entry is about the thing rather than merely containing
        # the word.
        matched = bool(med or cat or sec or (year_filter and in_years)
                       or hits >= 2)
    else:
        matched = hits >= 1
    score = hits * 2 + med * 5 + cat * 4 + sec * 3
    if year_filter and in_years:
        score += 1
    return matched, score, hits


def choose_theme(themes, news, days, today):
    active = [t for t in themes if not t.get("retired")]
    last = last_used_theme(days)
    recent = {t for t, d in last.items()
              if d and d != today.isoformat()
              and (today - datetime.date.fromisoformat(d[:10])).days < 21}
    pool = [t for t in active if t["id"] not in recent] or active
    scored = []
    for t in pool:
        s = 0.0
        words = [str(k).lower() for k in
                 (t.get("keywords") or []) + (t.get("tags") or [])]
        for n in news:
            text = (n["title"] + " " + n.get("publisher", "")).lower()
            if any(w and w in text for w in words):
                s += recency_weight(n)
        # A theme never used is preferred at equal score; the hash breaks ties
        # so two quiet days do not pick the same theme.
        used = last.get(t["id"], "")
        scored.append((s, used == "", used, stable(today, t["id"]), t))
    scored.sort(key=lambda x: (-x[0], not x[1], x[2], x[3]))
    best = scored[0][4]
    matched = scored[0][0] > 0
    return best, matched


def choose_figure(figures, news, theme, days, today):
    psotd = [m for m in figures if m.get("selectable")]
    used = {str(d.get("member")) for d in days
            if d.get("date") and
            (today - datetime.date.fromisoformat(str(d["date"])[:10])).days < 10}
    yesterday = ""
    for d in reversed(days):
        if str(d.get("date"))[:10] == (today - datetime.timedelta(days=1)).isoformat():
            yesterday = str(d.get("member"))
            break

    best = None
    for m in psotd:
        direct, source = 0, None
        for n in news:
            text = (n["title"] + " " + n.get("publisher", "")).lower()
            for alias in m.get("aliases") or []:
                a = str(alias).lower().strip()
                if len(a) < 3 or not re.search(r"\b" + re.escape(a) + r"\b", text):
                    continue
                ctx = [c.lower() for c in m.get("context") or []]
                if ctx and not any(c in text for c in ctx):
                    continue
                direct += 1
                if source is None:
                    source = n
                break
        theme_hits = len(set(m.get("tags") or []) &
                         set((theme.get("tags") or []) + (theme.get("keywords") or [])))
        score = direct * 12 + theme_hits * 1.5
        if m["id"] in used:
            score -= 4
        if m["id"] == yesterday:
            score -= 2
        score += stable(today, m["id"]) * 0.01
        if best is None or score > best[0]:
            best = (score, m, direct, source)
    _, m, direct, source = best

    fig = dict(m)
    if direct and source:
        fig["why_today"] = (f"Named in today's news: “{clip_sentences(source['title'], 150)}”.")
        fig["source"] = source
    elif theme:
        wire = next((n for n in news
                     if any(k.lower() in n["title"].lower()
                            for k in (theme.get("keywords") or []) +
                            (theme.get("tags") or []))), None)
        if wire:
            fig["why_today"] = (
                f"Today's edition: {theme['home_title']}, set by "
                f"“{clip_sentences(wire['title'], 130)}”. This figure is the "
                f"record's case for it.")
            fig["source"] = wire
        else:
            fig["why_today"] = (f"Today's edition: {theme['home_title']}. "
                                f"This figure is the record's case for it.")
            fig["source"] = None
    else:
        fig["why_today"] = "No headline today set the edition; the record's turn."
        fig["source"] = None
    return fig


def choose_entries(entries, theme, placements, days, today, n=8):
    used = used_entries(days, 14, today)
    candidates, used_candidates, all_entries = [], [], []
    for e in entries:
        if not concrete(e):
            continue
        p = placements.get(e["id"])
        ok, score, hits = theme_match(theme, e, p)
        if not ok:
            continue
        rank = score + stable(today, e["id"]) * 0.05
        row = (rank, e)
        all_entries.append(row)
        if e["id"] in used:
            used_candidates.append(row)
        else:
            candidates.append(row)
    candidates.sort(key=lambda x: -x[0])
    used_candidates.sort(key=lambda x: -x[0])
    all_entries.sort(key=lambda x: -x[0])

    picked = [e for _, e in candidates[:n]]
    for _, e in used_candidates:
        if len(picked) >= n:
            break
        if e not in picked:
            picked.append(e)
    for _, e in all_entries:
        if len(picked) >= n:
            break
        if e not in picked:
            picked.append(e)
    if len(picked) < n:
        for e in [x for x in entries if concrete(x)]:
            if e not in picked:
                picked.append(e)
            if len(picked) >= n:
                break
    return picked[:n], bool(candidates)


def entry_item(e, theme, i):
    why = clip_sentences(e.get("significance"), 360) or \
        clip_sentences(e.get("summary"), 240) or \
        "The entry's own page carries the argument."
    what = clip_sentences(e.get("summary"), 240) or plain(e.get("title"))
    return {"rank": i + 1,
            "name": plain(e.get("title")),
            "show": entry_show(e),
            "what": what,
            "why": why,
            "law": theme.get("law", 6),
            "entry": e["id"],
            "stage": "featured"}


def clean_why(s):
    """Placement prose without the editorial annotations in brackets."""
    s = re.sub(r"\[[^\]]*\]", " ", str(s or ""))
    return clip_sentences(s, 300)


def concrete(e) -> bool:
    """A concrete application, not the site's own argument or a definition.

    Thesis entries are the site's editorial position; terms and studies are
    the vocabulary and the evidence. A daily list or a way pick is supposed to
    show the thing happening, so those are excluded even when a keyword
    matches. The list still has 200+ concrete entries to draw from.
    """
    return (e.get("provenance") != "thesis"
            and e.get("kind") not in ("term", "study"))


def best_detail(s, limit: int = 240) -> str:
    """A concrete sentence from an entry's significance, for the daily figure.

    The summary is the block's two-sentence breakdown; this is the detail that
    makes a reader want the entry - a year, a quote, a specific thing that
    happened. It prefers a later sentence in the budget, because the first is
    usually the thesis and the later one is the evidence.
    """
    text = plain(s)
    parts = [p for p in re.split(r"(?<=[.!?])\s+", text) if p.strip()]
    later = [p for p in parts[1:] if 70 <= len(p) <= limit]
    if later:
        return max(later, key=len)
    anyp = [p for p in parts if 70 <= len(p) <= limit]
    if anyp:
        return max(anyp, key=len)
    return clip_sentences(text, limit)


GENERIC_NEWS = {
    "social", "media", "public", "people", "online", "internet",
    "relationship", "parasocial", "politics", "political", "story",
    "stories", "world", "today", "comments", "comment", "content",
    "celebrity", "famous", "culture", "cultural", "screen", "series",
}


def news_words(s) -> set:
    return {w for w in re.findall(r"[a-z]{6,}", str(s or "").lower())
            if w not in GENERIC_NEWS}


def wire_matches(title, text: str, news: list[dict], limit: int = 2) -> list[dict]:
    """Current wire items that share the pick's own title, not just its topic.

    Body words alone matched "Our Lady of Guadalupe" to a Survivor AI story on
    "others" and "recognize". A wire needs at least one distinctive word from
    the pick's title and one more shared subject word; a title is the shortest
    honest statement of what the pick is about.
    """
    tw_title = news_words(title)
    tw_all = tw_title | news_words(text)
    out = []
    for n in news:
        nw = news_words(n["title"])
        if len(tw_title & nw) >= 1 and len(tw_all & nw) >= 2:
            out.append(n)
        if len(out) >= limit:
            break
    return out


def choose_ways(tax, entries, cards, placements, story_places, news, theme,
                days, today, figure=None, top8_ids=None, image_slugs=None):
    byid = {e["id"]: e for e in entries}
    byslug = {c["slug"]: c for c in cards}
    used = set()
    for d in days:
        try:
            if (today - datetime.date.fromisoformat(str(d.get("date"))[:10])).days > 7:
                continue
        except ValueError:
            continue
        for p in (d.get("picks") or {}).values():
            used.add(str(p.get("id")))
    news_by_cat = {}
    picks = {}
    for cat in tax.get("attachment") or []:
        cid = cat["id"]
        rows = []
        for eid, p in placements.items():
            if p.get("cat") != cid:
                continue
            e = byid.get(eid)
            if not e or not concrete(e):
                continue
            text = " ".join(str(e.get(k) or "") for k in
                            ("title", "summary", "significance")).lower()
            s = len(set((theme.get("tags") or []) +
                        (theme.get("keywords") or [])) &
                    set(re.findall(r"[a-z]{4,}", text))) * 0.5
            # news overlap: entry text shares a distinctive word with a headline
            ttl = news_words(e.get("title"))
            tw = ttl | news_words(text)
            for n in news:
                nw = news_words(n["title"])
                if len(ttl & nw) >= 1 and len(tw & nw) >= 2:
                    s += recency_weight(n) * 2
                    break
            why = str((placements.get(eid) or {}).get("why") or "")
            if figure and eid == figure.get("entry"):
                s -= 6
            if top8_ids and eid in top8_ids:
                s -= 4
            if eid == "crossover" or "definition of the" in why.lower() or \
                    "category-defining" in why.lower():
                s -= 10
            if eid in used:
                s -= 3
            s += stable(today, "way", eid) * 0.02
            rows.append((s, "entry", eid, e))
        for slug, p in story_places.items():
            if p.get("cat") != cid:
                continue
            c = byslug.get(slug)
            if not c:
                continue
            text = " ".join(str(c.get(k) or "") for k in
                            ("headline", "one_line", "take", "section")).lower()
            s = len(set((theme.get("tags") or []) +
                        (theme.get("keywords") or [])) &
                    set(re.findall(r"[a-z]{4,}", text))) * 0.5
            if image_slugs and slug in image_slugs:
                # A real photograph is what makes a daily case look like a
                # front page rather than a bibliography entry. The editorial
                # reason still decides between photographed stories, but a
                # photographed story outranks an imageless one at equal prose.
                s += 4
            ttl = news_words(c.get("headline"))
            tw = ttl | news_words(text)
            for n in news:
                nw = news_words(n["title"])
                if len(ttl & nw) >= 1 and len(tw & nw) >= 2:
                    s += recency_weight(n) * 2
                    break
            if slug in used:
                s -= 3
            s += stable(today, "way", slug) * 0.02
            rows.append((s, "story", slug, c))
        if not rows:
            continue
        rows.sort(key=lambda x: -x[0])
        for s, kind, rid, obj in rows:
            if rid in used:
                continue
            if kind == "entry":
                p = placements.get(rid) or {}
                picks[cid] = {
                    "kind": "entry", "id": rid,
                    "title": plain(obj.get("title")),
                    "why": clean_why(p.get("why")),
                    "href": f"encyclopedia/{rid}.html",
                    "meta": entry_show(obj),
                }
            else:
                p = story_places.get(rid) or {}
                picks[cid] = {
                    "kind": "story", "id": rid,
                    "title": plain(obj.get("headline")),
                    "why": clean_why(p.get("why") or obj.get("one_line")),
                    "href": f"radar/{rid}.html",
                    "meta": f"Story · {obj.get('section') or ''}".strip(" ·"),
                }
            text = " ".join(str(obj.get(k) or "") for k in
                            ("title", "summary", "significance", "headline",
                             "one_line", "take")).lower()
            wires = wire_matches(picks[cid]["title"], text, news)
            story_n = sum(1 for q in story_places.values()
                          if q.get("cat") == cid)
            entry_n = sum(1 for q in placements.values()
                          if q.get("cat") == cid)
            days_n = 1 + sum(1 for d in days
                             if cid in (d.get("picks") or {}))
            picks[cid].update({
                "story_count": story_n,
                "entry_count": entry_n,
                "days_recorded": days_n,
                "wire_count": len(wires),
                "wires": [{"title": w["title"], "url": w["url"],
                           "publisher": w.get("publisher", "")}
                          for w in wires],
                "track": (f"{story_n} stories · {entry_n} entries · "
                          f"{days_n} daily case"
                          + ("s" if days_n != 1 else "")),
            })
            used.add(rid)
            break
    return picks


# -------------------------------------------------------------------- writes
def upsert_feature_list(feat, new_list, today):
    before_keys = sorted(feat)
    lists = feat.setdefault("lists", [])
    before_n = len(lists)
    replaced = None
    for i, L in enumerate(lists):
        if str(L.get("released") or "")[:10] == today or \
                L.get("slug") == new_list["slug"]:
            replaced = i
            break
    if replaced is None:
        lists.append(new_list)
    else:
        lists[replaced] = new_list
    assert sorted(feat) == before_keys, "features.json top-level keys moved"
    assert len(lists) in (before_n, before_n + 1), "list count moved unexpectedly"
    FEATURES.write_text(json.dumps(feat, ensure_ascii=False, indent=1) + "\n",
                        encoding="utf-8")


def upsert_ways_day(hist, day):
    days = hist.setdefault("days", [])
    if days and str(days[-1].get("date")) == day["date"]:
        days[-1] = day
    else:
        days.append(day)


def build(today, refresh=False, dry=False):
    figures = load(FIGURES, {"members": []}).get("members") or []
    themes = load(THEMES, {"themes": []}).get("themes") or []
    feat = load(FEATURES, {"lists": []})
    enc = load(DATA / "encyclopedia.json", {"entries": []})
    tax = load(DATA / "taxonomy.json", {"attachment": []})
    placements = load(DATA / "taxonomy_placements.json",
                      {"assignments": {}})["assignments"]
    stories = load(DATA / "story_placements.json",
                   {"placements": {}})["placements"]
    shop = load(DATA / "shop.json", {"cards": []})
    image_slugs = {i["slug"] for i in
                   (load(DATA / "images.json", {"items": []}).get("items") or [])
                   if i.get("local")}
    days = history_days(TOP8_HISTORY)
    pdays = history_days(PSOTD_HISTORY)
    wdays = history_days(WAYS_HISTORY)

    existing = load(EDITORIAL, {})
    if not refresh and str(existing.get("date")) == today.isoformat():
        print(f"editor: {today} already has an edition; use --refresh to "
              f"rebuild it")
        return 0

    news, source = gather_news()
    # A refresh of today's edition must be stable: the day being replaced is
    # not "the past" and must not push the chooser away from the selection it
    # made earlier today. Previous days still count.
    before_today = lambda rows: [d for d in rows
                                 if str(d.get("date")) != today.isoformat()]
    theme, theme_from_news = choose_theme(themes, news, before_today(days), today)
    figure = choose_figure(figures, news, theme, before_today(pdays), today)
    byid = {e["id"]: e for e in enc["entries"]}
    fe = byid.get(figure.get("entry") or "")
    figure["tell"] = (best_detail((fe or {}).get("significance"), 240)
                      or best_detail((fe or {}).get("summary"), 240))
    entries, enough = choose_entries(enc["entries"], theme, placements,
                                     before_today(days), today, 8)
    if len(entries) < 8:
        raise SystemExit("editor: could not assemble eight entries")

    items = [entry_item(e, theme, i) for i, e in enumerate(entries)]
    slug = f"top8-{today.isoformat()}-{theme['id']}"
    matched_news = [n for n in news
                    if any(k.lower() in n["title"].lower()
                           for k in (theme.get("keywords") or []) +
                           (theme.get("tags") or []))][:3]
    new_list = {
        "slug": slug,
        "title": theme["title"],
        "home_title": theme["home_title"],
        "home_hook": theme["home_hook"],
        "dek": theme["dek"],
        "kicker": (f"Daily edition · {fmt_date(today.isoformat())}"
                   + (f" · {theme['domain']}" if theme.get("domain") else "")),
        "image": None,
        "law": theme.get("law", 6),
        "standfirst": theme["standfirst"],
        "frame_note": ("The eight are drawn from entries already in the record; "
                       "each links to its own page and that page's sources. "
                       "{blank} of the {total} have no photograph, so their "
                       "entries carry text only. The absence is part of the "
                       "record."),
        "entries": items,
        "theme": theme["id"],
        "released": today.isoformat(),
        "generated_by": "tools/editor.py",
        "news": [{"title": n["title"], "url": n["url"],
                  "publisher": n.get("publisher", ""),
                  "at": n.get("at", "")} for n in matched_news],
        "stage_doc": ("A list is released whole, one per UTC day. The list "
                      "dated today is the show; every earlier list is archived "
                      "at /top8/archive/ and is never shown again."),
        "pool_note": ("Generated from the encyclopedia by tools/editor.py. "
                      "The eight are ranked by relevance to the theme and the "
                      "day, then by a stable tie-break; the numeral on the page "
                      "is the position in this list."),
    }
    ways = choose_ways(tax, enc["entries"], shop.get("cards") or [],
                       placements, stories, news, theme, before_today(wdays),
                       today, figure, {e["id"] for e in entries},
                       image_slugs)
    if len(ways) != len(tax.get("attachment") or []):
        raise SystemExit(f"editor: ways produced {len(ways)} of "
                         f"{len(tax.get('attachment') or [])} categories")

    edition = {
        "_note": ("GENERATED by tools/editor.py. Today's figure, top 8 and "
                  "eight way picks. The figure is a real person or a fictional "
                  "character; the top 8 is eight existing encyclopedia entries "
                  "under a hand-written theme; every way pick is an existing "
                  "entry or story. Rebuilt only when the date changes or "
                  "--refresh is passed, so a day has one edition."),
        "date": today.isoformat(),
        "news_source": source,
        "news": [{"title": n["title"], "url": n["url"],
                  "publisher": n.get("publisher", ""),
                  "at": n.get("at", "")} for n in news[:12]],
        "theme": {"id": theme["id"], "title": theme["title"],
                  "home_title": theme["home_title"],
                  "domain": theme.get("domain", ""),
                  "from_news": theme_from_news},
        "figure": figure,
        "top8": {"slug": slug, "title": theme["title"],
                 "entries": [e["id"] for e in entries]},
        "ways": ways,
    }
    way_day = {"date": today.isoformat(), "picks": ways}

    print(f"editor: {today} · theme {theme['id']} "
          f"({'news' if theme_from_news else 'rotation'}) · "
          f"figure {figure['name']} ({figure['kind']}) · "
          f"{len(ways)} ways · news {source} ({len(news)})")
    if dry:
        for i, it in enumerate(items, 1):
            print(f"  {i}. {it['name']} — {it['show']}")
        print(f"  why today: {figure.get('why_today')}")
        return 0

    upsert_feature_list(feat, new_list, today.isoformat())
    save(EDITORIAL, edition)
    hist = load(WAYS_HISTORY, {"_note": ("STATEFUL. One record per UTC day: "
                                         "the top 8 theme and the eight way "
                                         "picks as they were shown. Written by "
                                         "tools/editor.py; do not regenerate "
                                         "or delete - the sequence is the "
                                         "record."), "days": []})
    hist.setdefault("days", [])
    upsert_ways_day(hist, way_day)
    save(WAYS_HISTORY,
         {"_note": "STATEFUL. One record per UTC day: the top 8 theme and the "
                   "eight way picks as they were shown. Written by "
                   "tools/editor.py; do not regenerate or delete - the "
                   "sequence is the record.",
          "days": hist["days"]})
    print(f"editor: wrote {EDITORIAL.relative_to(ROOT).as_posix()}, "
          f"{new_list['slug']} and {WAYS_HISTORY.relative_to(ROOT).as_posix()}")
    return 0


# --------------------------------------------------------------------- check
def check(today) -> int:
    ed = load(EDITORIAL, {})
    feat = load(FEATURES, {"lists": []})
    figures = {m["id"]: m for m in
               (load(FIGURES, {"members": []}).get("members") or [])}
    enc = {e["id"]: e for e in
           (load(DATA / "encyclopedia.json", {"entries": []}).get("entries") or [])}
    tax = load(DATA / "taxonomy.json", {"attachment": []})
    placements = load(DATA / "taxonomy_placements.json",
                      {"assignments": {}})["assignments"]
    stories = load(DATA / "story_placements.json",
                   {"placements": {}})["placements"]
    bad = []
    if str(ed.get("date")) != today.isoformat():
        bad.append(f"editorial_today.json is dated {ed.get('date')}, not "
                   f"{today.isoformat()}")
    fig = ed.get("figure") or {}
    bank = figures.get(fig.get("id"))
    if not bank:
        bad.append(f"today's figure {fig.get('id')!r} is not in the bank")
    else:
        if not bank.get("selectable"):
            bad.append(f"today's figure {fig.get('id')!r} is not selectable")
        if bank.get("kind") not in ("real", "fictional"):
            bad.append(f"today's figure {fig.get('id')!r} is a "
                       f"{bank.get('kind')!r}, not a real or fictional figure")
        if not bank.get("entry") or bank["entry"] not in enc:
            bad.append(f"{fig.get('id')!r} links to no encyclopedia entry")

    pushed = [L for L in feat.get("lists") or []
              if str(L.get("released") or "")[:10] == today.isoformat()]
    if len(pushed) != 1:
        bad.append(f"features.json holds {len(pushed)} lists dated today, "
                   f"expected 1")
    else:
        L = pushed[0]
        entries = L.get("entries") or []
        if len(entries) != 8:
            bad.append(f"today's list carries {len(entries)} entries, expected 8")
        if len({e.get("entry") for e in entries}) != len(entries):
            bad.append("today's list repeats an entry")
        for e in entries:
            if e.get("entry") not in enc:
                bad.append(f"list entry {e.get('name')!r} has no encyclopedia "
                           f"page ({e.get('entry')!r})")
            if not e.get("what") or not e.get("why"):
                bad.append(f"list entry {e.get('name')!r} has no what/why")
            if "**" in str(e.get("what")) + str(e.get("why")):
                bad.append(f"list entry {e.get('name')!r} still carries markdown")
        if not L.get("theme"):
            bad.append("today's list names no theme")
        if not L.get("kicker", "").startswith("Daily edition"):
            bad.append("today's list is not marked as a daily edition")
        news = L.get("news") or []
        for n in news:
            if not str(n.get("url", "")).startswith("http"):
                bad.append(f"list news item {n.get('title')!r} has no live URL")

    ways = ed.get("ways") or {}
    cats = [c["id"] for c in tax.get("attachment") or []]
    for cid in cats:
        p = ways.get(cid)
        if not p:
            bad.append(f"no way pick for {cid}")
            continue
        if p.get("kind") == "entry" and p.get("id") not in placements:
            bad.append(f"way {cid}: entry {p.get('id')!r} is not placed")
        elif p.get("kind") == "entry" and placements[p["id"]].get("cat") != cid:
            bad.append(f"way {cid}: entry {p.get('id')!r} is filed under "
                       f"{placements[p['id']].get('cat')}")
        elif p.get("kind") == "story" and p.get("id") not in stories:
            bad.append(f"way {cid}: story {p.get('id')!r} is not placed")
        elif p.get("kind") == "story" and stories[p["id"]].get("cat") != cid:
            bad.append(f"way {cid}: story {p.get('id')!r} is filed under "
                       f"{stories[p['id']].get('cat')}")

    wh = load(WAYS_HISTORY, {"days": []}).get("days") or []
    today_way = [d for d in wh if str(d.get("date")) == today.isoformat()]
    if len(today_way) != 1:
        bad.append(f"ways_history.json holds {len(today_way)} records for "
                   f"today, expected 1")
    else:
        rec = today_way[0].get("picks") or {}
        if len(rec) != len(cats):
            bad.append(f"ways_history today holds {len(rec)} picks, expected "
                       f"{len(cats)}")
        for cid in cats:
            if (rec.get(cid) or {}).get("id") != (ways.get(cid) or {}).get("id"):
                bad.append(f"ways_history disagrees with editorial_today for "
                           f"{cid}")

    # The page's own selector must name this list. This is the one check that
    # connects the generated data to what a reader will actually see.
    try:
        import build_cards as bc
        shown = bc.show_list(feat, today.isoformat())
        if pushed and shown.get("slug") != pushed[0].get("slug"):
            bad.append(f"show_list returns {shown.get('slug')!r}, not today's "
                       f"{pushed[0].get('slug')!r}")
    except Exception as exc:  # noqa: BLE001 - the message is the diagnosis
        bad.append(f"show_list cannot name today's list: {exc}")

    for b in bad:
        print(f"FAIL {b}")
    if bad:
        print(f"\neditor: RED ({len(bad)} problem(s))")
        return 1
    print(f"editor: green · {today} · figure {fig.get('name')} "
          f"({bank.get('kind') if bank else '?'}) · "
          f"{len(pushed[0].get('entries') or [])} ranked entries · "
          f"{len(ways)} ways")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--refresh", action="store_true")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--check", action="store_true")
    a = ap.parse_args()
    today = utc_today()
    if a.check:
        return check(today)
    return build(today, refresh=a.refresh, dry=a.dry_run)


if __name__ == "__main__":
    raise SystemExit(main())
