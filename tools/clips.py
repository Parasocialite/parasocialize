#!/usr/bin/env python3
"""clips.py - the Parasocial Clip of the Day queue.

WHY THIS EXISTS
The front page carries a video slot beside the header. The slot is a promise
that a clip has been chosen and that its timestamp is the moment, so the data
behind it has to hold the same standard as a citation: the claim is checkable,
and the absence of a check is visible.

Three fields carry that standard.

    start      seconds into the video. `?t=1m24s` is a claim that the thing
               happens at 1:24. A URL proves the video exists. It does not
               prove what is on screen at 1:24, and neither does an embed.
    note       one sentence on why the clip is the subject. Same rule: it is a
               claim about the frame.
    watched    the ISO date a person watched it. **A clip without `watched` is
               not published.** This mirrors `kind: exact` for images, which
               was derived from a filename until `looked` was added, and the
               94 `retrievable` records with no URL before that.

So the front page renders nothing but its empty state until a clip carries a
watch date, and this tool refuses to invent one.

WHY NO CANDIDATE STATE
A "candidate" clip that renders nowhere is a queue nobody sees, and this
repository has already paid for invisible queues (the 83 locators, the image
queue). The file is short and `--list` shows everything in it, published or
not, with the reason it is not published.

Usage:
    python tools/clips.py --list
    python tools/clips.py --check
    python tools/clips.py --add <id> --title "..." --platform youtube \\
        --video dQw4w9WgXcQ --start 84 --note "..." --entry queen-for-a-day \\
        --watched 2026-11-02
    python tools/clips.py --retire <id>

PLATFORMS
    youtube   embedded, privacy-enhanced host, cued with ?start=
    vimeo     embedded, cued with #t=..s
    twitch    embedded, cued with &time=..s
    tiktok    NOT embedded - TikTok's player needs their script and ignores a
              timestamp. A tiktok clip is a link out and says so on the card.
"""
from __future__ import annotations

import argparse
import datetime
import json
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
CLIPS = ROOT / "data" / "clips.json"
ENC = ROOT / "data" / "encyclopedia.json"
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

PLATFORMS = {"youtube", "vimeo", "twitch", "tiktok"}
EMBEDDED = {"youtube", "vimeo", "twitch"}
SLUG = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
URLISH = re.compile(r"https?://|www\.", re.I)


def load() -> dict:
    return json.loads(CLIPS.read_text(encoding="utf-8"))


def save(doc: dict) -> None:
    doc["clips"] = sorted(doc.get("clips") or [], key=lambda c: c["id"])
    CLIPS.write_text(json.dumps(doc, ensure_ascii=False, indent=1) + "\n",
                     encoding="utf-8")


def entries() -> set[str]:
    try:
        return {e["id"] for e in json.loads(
            ENC.read_text(encoding="utf-8"))["entries"]}
    except (OSError, ValueError, KeyError):
        return set()


def problems(c: dict, known: set[str]) -> list[str]:
    """Everything wrong with one record, each as a sentence naming the field."""
    out = []
    cid = str(c.get("id") or "")
    if not SLUG.match(cid):
        out.append(f"{cid or '<no id>'}: id must be a lowercase hyphen slug")

    title = str(c.get("title") or "").strip()
    if not 10 <= len(title) <= 90:
        out.append(f"{cid}: title must be 10-90 characters")

    plat = str(c.get("platform") or "")
    if plat not in PLATFORMS:
        out.append(f"{cid}: platform {plat!r} is not one of {sorted(PLATFORMS)}")

    video = str(c.get("video") or "")
    if plat == "youtube" and not re.fullmatch(r"[\w-]{11}", video):
        out.append(f"{cid}: a YouTube id is 11 characters, got {video!r}")
    if plat == "vimeo" and not video.isdigit():
        out.append(f"{cid}: a Vimeo id is numeric, got {video!r}")
    if plat == "twitch" and not re.fullmatch(r"[\w-]{3,}", video):
        out.append(f"{cid}: a Twitch video id is alphanumeric, got {video!r}")
    if plat == "tiktok":
        url = str(c.get("url") or "")
        if "tiktok.com/" not in url:
            out.append(f"{cid}: a TikTok clip needs `url` on tiktok.com "
                       f"(TikTok's player ignores timestamps, so it is a link)")

    start = c.get("start")
    if not isinstance(start, int) or start < 0:
        out.append(f"{cid}: start must be a whole number of seconds")
    elif start > 86_400:
        out.append(f"{cid}: start {start}s is over a day into the video")

    note = str(c.get("note") or "").strip()
    if not 40 <= len(note) <= 260:
        out.append(f"{cid}: note must be 40-260 characters "
                   f"(it is the reason the clip is the subject)")
    if URLISH.search(note):
        out.append(f"{cid}: the note carries a URL; the link belongs in `url`")
    if "**" in note or "`" in note:
        out.append(f"{cid}: the note carries markdown")

    entry = c.get("entry")
    if entry and known and entry not in known:
        out.append(f"{cid}: entry {entry!r} is not in the encyclopedia")

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


def embed_url(c: dict) -> str:
    """The iframe source, cued. Empty for a platform that cannot be cued."""
    plat, vid = c.get("platform"), c.get("video")
    start = int(c.get("start") or 0)
    if plat == "youtube":
        return (f"https://www.youtube-nocookie.com/embed/{vid}"
                f"?start={start}&autoplay=1&rel=0&modestbranding=1")
    if plat == "vimeo":
        return f"https://player.vimeo.com/video/{vid}?autoplay=1#t={start}s"
    if plat == "twitch":
        return (f"https://player.twitch.tv/?video={vid}"
                f"&parent=www.parasocialize.com&autoplay=true&time={start}s")
    return ""


def published(c: dict) -> bool:
    return bool(c.get("watched"))


def cmd_list() -> int:
    clips = load().get("clips") or []
    if not clips:
        print("no clips. The front page renders its empty state until one is "
              "added with --watched, which only a person who watched it can set.")
        return 0
    for c in clips:
        state = f"published {c['watched']}" if published(c) else "unwatched"
        print(f"  {c['id']:<28} {c['platform']:<8} {c.get('start', 0):>6}s  {state}")
    print(f"\n{sum(1 for c in clips if published(c))} of {len(clips)} published")
    return 0


def cmd_check() -> int:
    doc = load()
    clips = doc.get("clips") or []
    known = entries()
    bad = []
    seen = set()
    for c in clips:
        if c.get("id") in seen:
            bad.append(f"{c.get('id')}: duplicate id")
        seen.add(c.get("id"))
        bad += problems(c, known)
    if bad:
        print(f"{len(bad)} problem(s):")
        for b in bad:
            print("  " + b)
        return 1
    n = sum(1 for c in clips if published(c))
    print(f"ok: {n} published clip(s), {len(clips) - n} unwatched")
    return 0


def cmd_add(a: argparse.Namespace) -> int:
    doc = load()
    known = entries()
    clip = {"id": a.id, "title": a.title.strip(), "platform": a.platform,
            "video": a.video or "", "start": a.start, "note": a.note.strip()}
    if a.platform == "tiktok":
        clip["url"] = a.url or ""
    if a.entry:
        clip["entry"] = a.entry
    if a.watched:
        clip["watched"] = a.watched
    if a.url and a.platform != "tiktok":
        clip["url"] = a.url

    bad = problems(clip, known)
    if bad:
        print("refused:")
        for b in bad:
            print("  " + b)
        return 1

    clips = doc.get("clips") or []
    if any(c.get("id") == clip["id"] for c in clips):
        print(f"refused: {clip['id']} is already in the file")
        return 1

    before = len(clips)
    clips.append(clip)
    doc["clips"] = clips
    save(doc)
    after = len(load().get("clips") or [])
    if after != before + 1:
        raise SystemExit("count assertion failed; the file was not written")
    state = (f"published, watched {clip['watched']}" if published(clip)
             else "added UNPUBLISHED - set --watched only after watching it")
    print(f"added {clip['id']} ({state})")
    return 0


def cmd_retire(cid: str) -> int:
    doc = load()
    clips = doc.get("clips") or []
    keep = [c for c in clips if c.get("id") != cid]
    if len(keep) == len(clips):
        print(f"no clip with id {cid!r}")
        return 1
    doc["clips"] = keep
    save(doc)
    print(f"retired {cid}")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--list", action="store_true")
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--add", metavar="ID")
    ap.add_argument("--retire", metavar="ID")
    ap.add_argument("--title")
    ap.add_argument("--platform", choices=sorted(PLATFORMS))
    ap.add_argument("--video")
    ap.add_argument("--start", type=int, default=0)
    ap.add_argument("--note")
    ap.add_argument("--entry")
    ap.add_argument("--watched", help="ISO date a person watched it")
    ap.add_argument("--url")
    a = ap.parse_args()

    if a.list:
        return cmd_list()
    if a.check:
        return cmd_check()
    if a.retire:
        return cmd_retire(a.retire)
    if a.add:
        missing = [f for f in ("title", "platform", "note") if not getattr(a, f)]
        if missing:
            ap.error("--add needs " + ", ".join("--" + m for m in missing))
        return cmd_add(a)
    ap.print_help()
    return 0


if __name__ == "__main__":
    sys.exit(main())
