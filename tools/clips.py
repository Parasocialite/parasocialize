#!/usr/bin/env python3
"""clips.py - the Parasocial Clip of the Day: schema, resolver, queue.

WHY THIS FILE EXISTS
A clip card is three claims wearing one frame: that this video exists, that the
interesting thing happens at this second, and that the sentence beside it is what
is said or shown. A URL settles the first. Nothing but a person watching settles
the other two.

So the schema is built to make the other two hard to fake:

    watched            ISO date a person watched it. No date, no publication.
    quoteSnippet       nullable. A quote is never inferred from a title.
    quoteSource        required whenever quoteSnippet is present, so every
                       quote points at where it was read or heard.
    parasocialScore    nullable, and requires scoreMethod when it is not. A
                       number without a stated method is this project's oldest
                       defect - `kind: exact` derived from a filename.
    contextualAnalysis the site's own reading, so it is allowed to argue. It is
                       not allowed to describe a frame.

FALLBACK, IN ORDER
    1. a watched clip whose curationSource is "Agent Swarm", newest first
    2. a watched clip from the seed library, newest first
    3. nothing - the card is not rendered at all

Step 3 is deliberate. An empty glass frame beside the headline is a promise with
nothing behind it, and the front page does not need one.

Usage:
    python tools/clips.py --list
    python tools/clips.py --check
    python tools/clips.py --resolve            # what the front page would show
    python tools/clips.py --add <id> --url "https://youtu.be/ID?t=84s" \\
        --creator "Name" --analysis "..." [--quote "..." --quote-source URL] \\
        [--score 62 --score-method "chat messages per minute, 5-min window"] \\
        [--source "Agent Swarm"|"Community Nomination"|"Seed library"] \\
        [--seed] [--watched 2026-11-03]
    python tools/clips.py --nominate <id> --url ... --reason "..."   # queue only
    python tools/clips.py --retire <id>
"""
from __future__ import annotations

import argparse
import datetime
import hashlib
import json
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
CLIPS = ROOT / "data" / "clips.json"
SEEDS = ROOT / "data" / "clip_seeds.json"
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

PLATFORMS = {"YouTube", "Twitch", "TikTok", "Vimeo"}
SOURCES = {"Agent Swarm", "Community Nomination", "Seed library"}
SLUG = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
URLISH = re.compile(r"https?://|www\.", re.I)

HOSTS = {
    "YouTube": ("youtube.com", "youtu.be", "youtube-nocookie.com"),
    "Vimeo": ("vimeo.com",),
    "Twitch": ("twitch.tv",),
    "TikTok": ("tiktok.com",),
}


# ---------------------------------------------------------------- parsing
def parse_time(raw) -> int:
    """Seconds from 84, "84s", "1:24" or "1m24s". Returns -1 when unreadable."""
    s = str(raw or "").strip().lower()
    if not s:
        return 0
    if s.isdigit():
        return int(s)
    m = re.fullmatch(r"(?:(\d+)h)?(?:(\d+)m)?(?:(\d+)s)", s)
    if m and any(m.groups()):
        h, mi, se = (int(x or 0) for x in m.groups())
        return h * 3600 + mi * 60 + se
    m = re.fullmatch(r"(\d+):(\d{1,2})(?::(\d{1,2}))?", s)
    if m:
        a, b, c = m.groups()
        if c is None:
            return int(a) * 60 + int(b)
        return int(a) * 3600 + int(b) * 60 + int(c)
    return -1


def parse_source(url: str):
    """(platform, video id, start seconds) from a URL, or (None, None, -1)."""
    u = str(url or "").strip()
    if not u:
        return None, None, -1
    low = u.lower()
    start = 0
    m = re.search(r"[?&#]t=([0-9hms:]+)", low)
    if m:
        start = parse_time(m.group(1))
    else:
        m = re.search(r"[?&]start=(\d+)", low)
        if m:
            start = int(m.group(1))

    if "youtu.be/" in low:
        vid = re.search(r"youtu\.be/([\w-]{11})", u)
        return ("YouTube", vid.group(1), start) if vid else (None, None, -1)
    if "youtube" in low:
        vid = re.search(r"(?:v=|/embed/|/shorts/)([\w-]{11})", u)
        return ("YouTube", vid.group(1), start) if vid else (None, None, -1)
    if "vimeo.com" in low:
        vid = re.search(r"vimeo\.com/(?:video/)?(\d+)", u)
        return ("Vimeo", vid.group(1), start) if vid else (None, None, -1)
    if "clips.twitch.tv" in low:
        vid = re.search(r"clips\.twitch\.tv/([\w-]+)", u)
        return ("Twitch", vid.group(1), start) if vid else (None, None, -1)
    if "twitch.tv" in low:
        vid = re.search(r"twitch\.tv/videos/(\d+)", u)
        return ("Twitch", vid.group(1), start) if vid else (None, None, -1)
    if "tiktok.com" in low:
        vid = re.search(r"/video/(\d+)", u)
        return ("TikTok", vid.group(1) if vid else "", start)
    return None, None, -1


def embed_url(c: dict) -> str:
    """The iframe source cued at `start`. Empty for TikTok, which cannot be."""
    plat = c.get("platform")
    vid = c.get("video")
    start = int(c.get("start") or 0)
    if plat == "YouTube":
        return (f"https://www.youtube-nocookie.com/embed/{vid}"
                f"?start={start}&autoplay=1&rel=0&modestbranding=1")
    if plat == "Vimeo":
        return f"https://player.vimeo.com/video/{vid}?autoplay=1#t={start}s"
    if plat == "Twitch":
        return (f"https://player.twitch.tv/?video={vid}"
                f"&parent=www.parasocialize.com&autoplay=true&time={start}s")
    return ""


def stamp(sec: int) -> str:
    return f"{sec // 60}:{sec % 60:02d}"


# ---------------------------------------------------------------- storage
def load(path: pathlib.Path) -> dict:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {"_note": "", "clips": []}


def save(path: pathlib.Path, doc: dict) -> None:
    doc["clips"] = sorted(doc.get("clips") or [], key=lambda c: c["id"])
    path.write_text(json.dumps(doc, ensure_ascii=False, indent=1) + "\n",
                    encoding="utf-8")


def all_records():
    for doc, path, seed in ((load(CLIPS), CLIPS, False),
                            (load(SEEDS), SEEDS, True)):
        for c in doc.get("clips") or []:
            yield c, path, seed


# ---------------------------------------------------------------- validate
def problems(c: dict) -> list[str]:
    out = []
    cid = str(c.get("id") or "")
    if not SLUG.match(cid):
        out.append(f"{cid or '<no id>'}: id must be a lowercase hyphen slug")

    plat = str(c.get("platform") or "")
    if plat not in PLATFORMS:
        out.append(f"{cid}: platform {plat!r} is not one of {sorted(PLATFORMS)}")
    else:
        parsed_plat, vid, start = parse_source(c.get("sourceUrl") or "")
        if not parse_source(c.get("sourceUrl") or "")[0]:
            out.append(f"{cid}: sourceUrl does not parse as a video link")
        elif parsed_plat != plat:
            out.append(f"{cid}: sourceUrl is {parsed_plat} but platform is {plat}")
        elif not vid:
            out.append(f"{cid}: sourceUrl carries no video id")
        if int(c.get("start") if c.get("start") is not None else -1) < 0:
            out.append(f"{cid}: start must be a whole number of seconds")

    if not str(c.get("creatorName") or "").strip():
        out.append(f"{cid}: creatorName is required")

    src = str(c.get("curationSource") or "")
    if src not in SOURCES:
        out.append(f"{cid}: curationSource {src!r} is not one of {sorted(SOURCES)}")

    score = c.get("parasocialScore")
    if score is not None:
        if not isinstance(score, int) or not 0 <= score <= 100:
            out.append(f"{cid}: parasocialScore must be an integer 0-100 or null")
        if not str(c.get("scoreMethod") or "").strip():
            out.append(f"{cid}: parasocialScore needs scoreMethod - a number "
                       f"with no stated method is the defect this project "
                       f"keeps finding")

    quote = c.get("quoteSnippet")
    if quote is not None:
        q = str(quote).strip()
        if not 4 <= len(q) <= 160 or "\n" in q:
            out.append(f"{cid}: quoteSnippet must be one line, 4-160 characters")
        if not str(c.get("quoteSource") or "").strip():
            out.append(f"{cid}: quoteSnippet needs quoteSource, so a reader can "
                       f"check where it was said")

    analysis = str(c.get("contextualAnalysis") or "").strip()
    if not 80 <= len(analysis) <= 420:
        out.append(f"{cid}: contextualAnalysis must be 80-420 characters")
    if URLISH.search(analysis):
        out.append(f"{cid}: contextualAnalysis carries a URL")

    watched = c.get("watched")
    if watched:
        try:
            d = datetime.date.fromisoformat(str(watched)[:10])
        except ValueError:
            out.append(f"{cid}: watched must be an ISO date")
        else:
            if d > datetime.date.today():
                out.append(f"{cid}: watched is in the future ({watched})")
    return out


def published(c: dict) -> bool:
    return bool(c.get("watched"))


# ---------------------------------------------------------------- resolve
def resolve(today: datetime.date | None = None):
    """What the front page shows: agent clip, then seed, then nothing."""
    today = today or datetime.date.today()
    agent, seeded = [], []
    for c in (load(CLIPS).get("clips") or []):
        if published(c) and c.get("curationSource") == "Agent Swarm":
            agent.append(c)
    for c in (load(SEEDS).get("clips") or []):
        if published(c):
            seeded.append(c)

    def newest(rows):
        return sorted(rows, key=lambda c: str(c.get("watched") or ""),
                      reverse=True)

    if newest(agent):
        return newest(agent)[0], "agent"
    if newest(seeded):
        return newest(seeded)[0], "seed"
    return None, "none"


# ---------------------------------------------------------------- commands
def cmd_list() -> int:
    rows = list(all_records())
    if not rows:
        print("no clips in either file")
        return 0
    for c, _p, seed in rows:
        state = f"published {c['watched']}" if published(c) else "unwatched"
        where = "seed" if seed else "queue"
        print(f"  {c['id']:<30} {where:<5} {c.get('platform',''):<8} "
              f"{stamp(int(c.get('start') or 0)):>6}  {state}")
    chosen, route = resolve()
    print(f"\nfront page would show: "
          f"{chosen['id'] if chosen else '(nothing)'} via {route}")
    return 0


def cmd_check() -> int:
    bad, seen = [], set()
    total = 0
    for c, _p, _s in all_records():
        total += 1
        if c.get("id") in seen:
            bad.append(f"{c.get('id')}: duplicate id across the two files")
        seen.add(c.get("id"))
        bad += problems(c)
    # A record has to sit in the file that can actually show it. A "Seed
    # library" clip left in the queue never resolves, because the fallback
    # only reads clip_seeds.json - and a clip in the seed file that is not a
    # seed would be published as the fallback without being one.
    for c in (load(SEEDS).get("clips") or []):
        if not published(c):
            bad.append(f"{c.get('id')}: in the seed library but not watched, "
                       f"so it can never be the fallback it exists to be")
        if c.get("curationSource") != "Seed library":
            bad.append(f"{c.get('id')}: in clip_seeds.json but curationSource "
                       f"is {c.get('curationSource')!r}")
    for c in (load(CLIPS).get("clips") or []):
        if c.get("curationSource") == "Seed library":
            bad.append(f"{c.get('id')}: curationSource is 'Seed library' but it "
                       f"is in the queue - a seed in clips.json never resolves; "
                       f"move it with --seed")
    if bad:
        print(f"{len(bad)} problem(s):")
        for b in bad:
            print("  " + b)
        return 1
    print(f"ok: {total} clip(s); front page route: {resolve()[1]}")
    return 0


def cmd_resolve() -> int:
    c, route = resolve()
    if not c:
        print("nothing - the card is not rendered")
        return 0
    print(f"{c['id']} via {route}: {c['sourceUrl']} at {stamp(c['start'])}")
    return 0


def cmd_add(a: argparse.Namespace) -> int:
    path = SEEDS if a.seed else CLIPS
    doc = load(path)
    plat, vid, url_start = parse_source(a.url)
    start = a.start if a.start is not None else url_start
    if start is None or start < 0:
        print("refused: start could not be read from --start or the URL")
        return 1
    cid = a.add or hashlib.sha256(
        f"{a.url}|{start}".encode()).hexdigest()[:10]
    clip = {
        "id": cid,
        "sourceUrl": a.url.strip(),
        "creatorName": (a.creator or "").strip(),
        "platform": plat or "",
        "parasocialScore": a.score,
        "scoreMethod": a.score_method if a.score is not None else None,
        "curationSource": a.source,
        "quoteSnippet": a.quote,
        "quoteSource": a.quote_source,
        "contextualAnalysis": (a.analysis or "").strip(),
        "start": start,
        "video": vid or "",
    }
    if a.watched:
        clip["watched"] = a.watched
    bad = problems(clip)
    if not plat:
        bad.insert(0, "refused: --url is not a recognised video link")
    if bad:
        print("refused:")
        for b in bad:
            print("  " + b)
        return 1
    clips = doc.get("clips") or []
    if any(c.get("id") == cid for c in clips):
        print(f"refused: {cid} is already in {path.name}")
        return 1
    before = len(clips)
    clips.append(clip)
    doc["clips"] = clips
    save(path, doc)
    if len(load(path).get("clips") or []) != before + 1:
        raise SystemExit("count assertion failed; the file was not written")
    print(f"added {cid} to {path.name} "
          f"({'published' if published(clip) else 'UNPUBLISHED - set --watched only after watching'})")
    return 0


def cmd_nominate(a: argparse.Namespace) -> int:
    """A community nomination lands in the queue, never on the page."""
    path = CLIPS
    doc = load(path)
    plat, vid, url_start = parse_source(a.url)
    if not plat:
        print("refused: --url is not a recognised video link")
        return 1
    start = a.start if a.start is not None else url_start
    if start is None or start < 0:
        print("refused: start could not be read")
        return 1
    reason = (a.reason or "").strip()
    if len(reason) < 20:
        print("refused: a nomination needs a sentence saying why it is one")
        return 1
    cid = hashlib.sha256(f"{a.url}|{start}".encode()).hexdigest()[:10]
    clips = doc.get("clips") or []
    if any(c.get("id") == cid for c in clips):
        print(f"already nominated: {cid}")
        return 0
    clips.append({
        "id": cid, "sourceUrl": a.url.strip(), "creatorName": "",
        "platform": plat, "parasocialScore": None, "scoreMethod": None,
        "curationSource": "Community Nomination", "quoteSnippet": None,
        "quoteSource": None, "contextualAnalysis": reason, "start": start,
        "video": vid or "",
    })
    doc["clips"] = clips
    save(path, doc)
    print(f"queued {cid} - unwatched, so it is not rendered")
    return 0


def cmd_retire(cid: str) -> int:
    for path in (CLIPS, SEEDS):
        doc = load(path)
        clips = doc.get("clips") or []
        keep = [c for c in clips if c.get("id") != cid]
        if len(keep) != len(clips):
            doc["clips"] = keep
            save(path, doc)
            print(f"retired {cid} from {path.name}")
            return 0
    print(f"no clip with id {cid!r}")
    return 1


def main() -> int:
    ap = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--list", action="store_true")
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--resolve", action="store_true")
    ap.add_argument("--add", metavar="ID", nargs="?", const="")
    ap.add_argument("--nominate", action="store_true")
    ap.add_argument("--retire", metavar="ID")
    ap.add_argument("--seed", action="store_true",
                    help="write to data/clip_seeds.json instead of the queue")
    ap.add_argument("--url")
    ap.add_argument("--creator")
    ap.add_argument("--start", type=int, default=None)
    ap.add_argument("--analysis")
    ap.add_argument("--reason")
    ap.add_argument("--quote")
    ap.add_argument("--quote-source")
    ap.add_argument("--score", type=int, default=None)
    ap.add_argument("--score-method")
    ap.add_argument("--source", default="Agent Swarm", choices=sorted(SOURCES))
    ap.add_argument("--watched")
    a = ap.parse_args()

    if a.list:
        return cmd_list()
    if a.check:
        return cmd_check()
    if a.resolve:
        return cmd_resolve()
    if a.retire:
        return cmd_retire(a.retire)
    if a.nominate:
        if not a.url or not a.reason:
            ap.error("--nominate needs --url and --reason")
        return cmd_nominate(a)
    if a.add is not None:
        if not a.url or not a.analysis:
            ap.error("--add needs --url and --analysis")
        return cmd_add(a)
    ap.print_help()
    return 0


if __name__ == "__main__":
    sys.exit(main())
