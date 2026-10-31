#!/usr/bin/env python3
"""archive.py - the three daily records, and whether the sequence has holes.

WHY THIS EXISTS
The three rotations - the top 8, the register of the day, the parasocialite -
each append one record per UTC day. All three stopped at 2026-10-21 and were
not noticed for ten days: the pages were internally consistent, every gate was
green, and nothing in the project asked whether yesterday had been recorded.
The record is the only part of a rotation that cannot be recomputed from the
date by a later reader; a gap in it is permanent evidence that nobody was
there.

So this tool does the two things that were missing:

  --check        say out loud which days have no record, and fail on the ones
                 that are not declared. A silent gap is the defect; a reported
                 one is a work queue.

  --reconcile    close a gap that is PROVABLE, or declare it. The register is
                 still a deterministic rotation, so a missed day can be
                 recomputed when its inputs were frozen before it. The top 8
                 and the parasocialite are selected from that day's wires and
                 theme; a later build cannot know what the page would have
                 shown, so those gaps are written into data/archive_gaps.json
                 as declared, unrecoverable days rather than invented.

A reconstructed day is marked, never passed off as observed. The entry carries
`reconstructed: true`, `reconstructed_on` and `inputs_sha256`, and every page
that prints the record prints a `rebuilt` tag beside it. A declared day is not
a reconstruction: it is a permanent, visible gap, and the site keeps publishing
the next day's edition instead of stopping forever on a hole it cannot fill.
That distinction is the point: what the site showed, what it could recompute,
and what it never had are three different claims, and a reader is entitled to
tell them apart.

WHAT THIS DOES NOT DO
It does not regenerate the files, reorder existing days, or rewrite a record
that is already there. Existing entries are compared before and after every
write. `_note` is refreshed from build_cards because that note now has to
describe the reconstructed state; nothing else about a past day moves.

Usage:
    python tools/archive.py --check
    python tools/archive.py --reconcile
    python tools/archive.py --reconcile --dry-run

Exit codes: --check is 1 when a day has no record and no declaration, or when
a file is duplicated, out of order, dated in the future or outside its own
epoch. --reconcile exits 0 after reconstructing or declaring; a declaration is
not a success at filling a hole, it is a success at naming one without lying.
"""
from __future__ import annotations

import argparse
import datetime
import hashlib
import json
import pathlib
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
TOOLS = ROOT / "tools"
sys.path.insert(0, str(TOOLS))

import build_cards as bc  # noqa: E402  (the rotations live there)

sys.stdout.reconfigure(encoding="utf-8")

# The day record_top8_day() shipped and the top-8 record began. This is a
# constant rather than `first recorded date` on purpose: deriving the start
# from the file would make a deleted first day invisible, and catching a
# sequence with a hole at its beginning is exactly what this tool is for. The
# register and parasocialite epochs live in build_cards because their pages
# compute from them.
TOP8_EPOCH = datetime.date(2026, 10, 19)
# A gap that cannot be reconstructed is declared here rather than fabricated or
# allowed to stop every future edition. The archive check reads it; the record
# pages still show the sequence, and a declared day is a fact about the record
# (no edition was generated) rather than a silent hole.
GAPS = ROOT / "data" / "archive_gaps.json"
GAPS_NOTE = ("Declared, unrecoverable days in the three daily records. The "
             "daily top 8 and the parasocialite are selected from that day's "
             "wires and theme, so a later build cannot know what the page "
             "would have shown. tools/archive.py --reconcile writes one of "
             "these instead of inventing a day; --check accepts the day as a "
             "visible gap. Do not delete a declaration to make a report look "
             "clean.")


def load_gaps() -> dict:
    try:
        d = json.loads(GAPS.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        d = {"_note": GAPS_NOTE, "gaps": []}
    d.setdefault("_note", GAPS_NOTE)
    d.setdefault("gaps", [])
    return d


def gap_reason(gaps: dict, history: str, iso: str) -> str:
    for g in gaps.get("gaps") or []:
        if g.get("history") == history and \
                str(g.get("from", "")) <= iso <= str(g.get("to", "")):
            return str(g.get("reason") or "")
    return ""


def declare_gap(gaps: dict, history: str, dates: list[str], reason: str,
                today: datetime.date) -> bool:
    """Merge a range into the declaration file. Returns whether it changed."""
    if not dates:
        return False
    lo, hi = min(dates), max(dates)
    for g in gaps["gaps"]:
        if g.get("history") != history:
            continue
        if str(g.get("to", "")) < lo or str(g.get("from", "")) > hi:
            continue
        before = (g.get("from"), g.get("to"), g.get("reason"), g.get("declared"))
        g["from"] = min(str(g.get("from") or lo), lo)
        g["to"] = max(str(g.get("to") or hi), hi)
        g["reason"] = reason or g.get("reason") or ""
        g["declared"] = today.isoformat()
        return before != (g["from"], g["to"], g["reason"], g["declared"])
    gaps["gaps"].append({"history": history, "from": lo, "to": hi,
                         "reason": reason, "declared": today.isoformat()})
    return True


def save_gaps(gaps: dict) -> None:
    gaps["_note"] = GAPS_NOTE
    gaps["gaps"].sort(key=lambda g: (g.get("history", ""), g.get("from", "")))
    GAPS.write_text(json.dumps(gaps, ensure_ascii=False, indent=1) + "\n",
                    encoding="utf-8")


def utc_today() -> datetime.date:
    return datetime.datetime.now(datetime.timezone.utc).date()


def load(path: pathlib.Path, note: str) -> dict:
    if not path.exists():
        return {"_note": note, "days": []}
    data = json.loads(path.read_text(encoding="utf-8"))
    data.setdefault("_note", note)
    data.setdefault("days", [])
    return data


def input_date(path: pathlib.Path) -> datetime.date:
    """When the bytes that feed a rotation last changed.

    File mtimes do not survive a git clone: a fresh CI checkout writes every
    file at checkout time, which would make every gap look unprovable exactly
    when the scheduler needs the repair path most. So a clean tracked file is
    dated by the commit that last touched it, and only an uncommitted change
    uses the filesystem time. The comparison is `git status --porcelain` for
    this one path: empty means the bytes on disk are the committed bytes.
    """
    rel = path.relative_to(ROOT).as_posix()

    def git(*args):
        try:
            p = subprocess.run(["git", "-C", str(ROOT), *args],
                               capture_output=True, text=True, timeout=15)
        except (OSError, subprocess.SubprocessError):
            return None
        return p.stdout.strip() if p.returncode == 0 else None

    committed = git("log", "-1", "--format=%cI", "--", rel)
    dirty = git("status", "--porcelain", "--", rel)
    if committed and dirty == "":
        try:
            when = datetime.datetime.fromisoformat(
                committed.replace("Z", "+00:00"))
            if when.tzinfo is None:
                when = when.replace(tzinfo=datetime.timezone.utc)
            return when.astimezone(datetime.timezone.utc).date()
        except ValueError:
            pass
    return datetime.datetime.fromtimestamp(
        path.stat().st_mtime, datetime.timezone.utc).date()


def input_digest(paths) -> str:
    h = hashlib.sha256()
    for p in paths:
        h.update(p.name.encode("utf-8"))
        h.update(p.read_bytes())
    return h.hexdigest()[:12]


def specs() -> list[dict]:
    """The three daily records, each with the rotation that produces a day.

    The builder is called with an ISO date and returns exactly the entry the
    live record writer would have appended, minus the reconstructed marker.
    """
    feat = json.loads((ROOT / "data" / "features.json").read_text(encoding="utf-8"))
    tax = json.loads((ROOT / "data" / "taxonomy.json").read_text(encoding="utf-8"))
    roster = json.loads((ROOT / "data" / "parasocialite.json")
                        .read_text(encoding="utf-8"))

    def top8(iso: str) -> dict | None:
        L = bc.top8_window(feat, iso)
        return {"date": iso, "list": L.get("slug") or "",
                "items": [bc.t8_eid(en) for en in L.get("entries") or []]}

    def register(iso: str) -> dict | None:
        r = bc.register_of_day(tax, iso)
        return {"date": iso, "register": r["id"]} if r else None

    def parasocialite(iso: str) -> dict | None:
        m = bc.parasocialite_of_day(roster, iso)
        return {"date": iso, "member": m.get("id", "")} if m else None

    return [
        {"name": "top8", "path": bc.TOP8_HISTORY, "note": bc.TOP8_HISTORY_NOTE,
         "start": TOP8_EPOCH, "build": None, "reconstructable": False,
         "inputs": [ROOT / "data" / "features.json",
                    ROOT / "data" / "editorial_today.json"]},
        {"name": "register", "path": bc.REGISTER_HISTORY,
         "note": bc.REGISTER_HISTORY_NOTE, "start": bc.REGISTER_EPOCH,
         "build": register, "reconstructable": True,
         "inputs": [ROOT / "data" / "taxonomy.json"]},
        {"name": "parasocialite", "path": bc.PARASOCIALITE_HISTORY,
         "note": bc.PARASOCIALITE_HISTORY_NOTE, "start": bc.PARASOCIALITE_EPOCH,
         "build": None, "reconstructable": False,
         "inputs": [ROOT / "data" / "parasocialite.json",
                    ROOT / "data" / "editorial_today.json"]},
    ]


def audit(spec: dict, today: datetime.date) -> dict:
    """Everything wrong with one record file, measured rather than assumed."""
    data = load(spec["path"], spec["note"])
    days = data.get("days") or []
    dates = [str(d.get("date") or "") for d in days]
    problems = []

    seen = set()
    for d in dates:
        if d in seen:
            problems.append(f"{d} is recorded more than once")
        seen.add(d)
    if dates != sorted(dates):
        problems.append("days are not in ascending date order")

    start = spec["start"]
    for d in dates:
        try:
            day = datetime.date.fromisoformat(d)
        except ValueError:
            problems.append(f"{d!r} is not an ISO date")
            continue
        if day < start:
            problems.append(f"{d} predates the rotation's own epoch {start}")
        if day > today:
            problems.append(f"{d} is in the future")

    # A gap is a day between the rotation's first possible day and today that
    # has no record at all. Today counts: before the build it is legitimately
    # missing, and --check is how the daily loop discovers that it has not run.
    present = set(dates)
    missing = []
    day = start
    while day <= today:
        if day.isoformat() not in present:
            missing.append(day.isoformat())
        day += datetime.timedelta(days=1)

    reconstructed = [str(d.get("date")) for d in days if d.get("reconstructed")]
    unmarked = []
    for d in days:
        if d.get("reconstructed") and not (
                d.get("reconstructed_on") and d.get("inputs_sha256")):
            unmarked.append(str(d.get("date")))

    gaps = load_gaps()
    declared = [d for d in missing if gap_reason(gaps, spec["name"], d)]
    unexplained = [d for d in missing if d not in declared]

    return {"name": spec["name"], "path": spec["path"], "days": days,
            "dates": dates, "problems": problems, "missing": missing,
            "unexplained": unexplained, "declared": declared,
            "reconstructed": reconstructed, "unmarked": unmarked,
            "data": data}


def check(specs_list, today: datetime.date) -> int:
    failed = False
    for spec in specs_list:
        a = audit(spec, today)
        rel = a["path"].relative_to(ROOT).as_posix()
        print(f"{a['name']}: {len(a['dates'])} day(s), "
              f"{len(a['reconstructed'])} rebuilt, {rel}")
        if a["dates"]:
            print(f"  spans {a['dates'][0]} -> {a['dates'][-1]}")
        if a["problems"]:
            failed = True
            for p in a["problems"]:
                print(f"  FAIL {p}")
        if a["unmarked"]:
            failed = True
            print("  FAIL rebuilt day(s) with no provenance: "
                  f"{a['unmarked']} - a rebuilt record must carry "
                  "reconstructed_on and inputs_sha256")
        if a["unexplained"]:
            failed = True
            print(f"  FAIL {len(a['unexplained'])} day(s) have no record: "
                  f"{a['unexplained'][0]} -> {a['unexplained'][-1]}")
            print("       run `python tools/archive.py --reconcile` (it will "
                  "reconstruct a provable register day and declare what it "
                  "cannot know), then rebuild so today is recorded live")
        else:
            print("  ok   every day from the epoch to today has a record"
                  + (f", except {len(a['declared'])} declared gap(s)"
                     if a["declared"] else ""))
        if a["declared"]:
            print(f"  note {len(a['declared'])} declared day(s): "
                  f"{a['declared'][0]} -> {a['declared'][-1]} - the edition "
                  f"cannot be reconstructed, so the gap stays visible")
    print("\n" + ("archive: RED" if failed else "archive: green"))
    return 1 if failed else 0


def reconcile(specs_list, today: datetime.date, dry: bool) -> int:
    """Reconstruct what is provable; declare what is not. Never invents a day."""
    changed = False
    gaps = load_gaps()
    for spec in specs_list:
        a = audit(spec, today)
        # Today is deliberately excluded: it is written live by the build that
        # follows this step. Reconstructing it here would put a computed record
        # where an observed one belongs, which is the defect this tool marks.
        target = [d for d in a["missing"] if d < today.isoformat()]
        if not target:
            print(f"{a['name']}: nothing to close "
                  f"({len(a['missing'])} open day(s), today excluded)")
            continue
        if not spec.get("reconstructable", True):
            reason = ("No daily edition was generated on this day. The top 8 "
                      "and the parasocialite are selected from that day's "
                      "wires and theme, so a later build cannot know what the "
                      "page would have shown.")
            if declare_gap(gaps, spec["name"], target, reason, today):
                changed = True
            verb = "would declare" if dry else "declared"
            print(f"{spec['name']}: {verb} {len(target)} unrecoverable day(s) "
                  f"({target[0]} -> {target[-1]})")
            continue
        newest = max(input_date(p) for p in spec["inputs"])
        sha = input_digest(spec["inputs"])
        added, refused = [], []
        for iso in target:
            day = datetime.date.fromisoformat(iso)
            if newest >= day:
                refused.append(
                    (iso, f"{spec['inputs'][0].name} was last changed "
                           f"{newest}, on or after this day, so the state a "
                           f"build would have seen is not knowable"))
                continue
            entry = spec["build"](iso)
            if not entry:
                refused.append((iso, "the rotation produced no entry"))
                continue
            entry["reconstructed"] = True
            entry["reconstructed_on"] = today.isoformat()
            entry["inputs_sha256"] = sha
            added.append(entry)

        if added:
            before = {str(d.get("date")): d for d in a["days"]
                      if not d.get("reconstructed")}
            days = list(a["days"])
            days.extend(added)
            days.sort(key=lambda d: str(d.get("date")))
            # The one transformation this tool is not allowed to make: moving
            # or rewriting a day that already existed. Assert it before write.
            after = {str(d.get("date")): d for d in days
                     if not d.get("reconstructed")}
            assert before == after, "an existing record changed while closing a gap"
            data = a["data"]
            data["days"] = days
            data["_note"] = spec["note"]
            if not dry:
                spec["path"].write_text(
                    json.dumps(data, ensure_ascii=False, indent=1) + "\n",
                    encoding="utf-8")
            verb = "would close" if dry else "closed"
            print(f"{a['name']}: {verb} {len(added)} day(s) as rebuilt "
                  f"({added[0]['date']} -> {added[-1]['date']})")
        for iso, why in refused:
            if declare_gap(gaps, spec["name"], [iso], why, today):
                changed = True
            verb = "would declare" if dry else "declared"
            print(f"{a['name']}: {verb} {iso} - {why}")

    if changed and not dry:
        save_gaps(gaps)
        print(f"\narchive: declared unrecoverable day(s) in "
              f"{GAPS.relative_to(ROOT).as_posix()}; they stay visible")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--reconcile", action="store_true")
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()
    today = utc_today()
    s = specs()

    if a.reconcile:
        rc = reconcile(s, today, a.dry_run)
        print()
        # After a real reconcile the audit is the proof it worked. Today is
        # deliberately not counted here: it is the one day a live build fills,
        # and reconcile refuses to compute it. A dry run must not claim a green
        # archive it did not produce.
        if not a.dry_run:
            open_gaps, bad = [], []
            for spec in s:
                a2 = audit(spec, today)
                open_gaps += [d for d in a2["unexplained"]
                              if d < today.isoformat()]
                bad += a2["problems"]
            if bad or open_gaps:
                rc = 1
                for b in bad:
                    print(f"FAIL {b}")
                if open_gaps:
                    print(f"FAIL {len(open_gaps)} day(s) before today still "
                          f"have no record: {open_gaps}")
            else:
                print("archive: every day before today has a record; today "
                      "is left for the live build")
        return rc

    # Default and --check are the same read-only audit. Making the default a
    # write would be the same trap as a packaging step that rebuilds: a command
    # run "just to look" would change tracked history.
    return check(s, today)


if __name__ == "__main__":
    raise SystemExit(main())
