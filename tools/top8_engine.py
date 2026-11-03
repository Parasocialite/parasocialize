#!/usr/bin/env python3
"""top8_engine.py - the deterministic Daily Top 8.

WHAT THIS IS
One list per date, eight items, one from each attachment category, chosen by a
hash of the date. The same date produces the same eight on every machine, in
every build, for a reader and for a crawler - the strongest version of "SSR and
client agree" is that there is no client-side selection at all.

THE 30-DAY RULE, AND WHERE IT BREAKS
The brief asks for two rules that cannot both hold forever:

    eight items a day, one per category   -> 30 x 8 = 240 distinct items needed
    nothing repeated inside 30 days       -> per category, 30 distinct items

The corpus is 255 entries and `divine` holds 15, `officer` and `predator` 17,
`cosmology` 20. A category with 15 entries cannot supply 30 days without a
repeat. So the rule is enforced while the pool allows it, and when it does not
the engine takes the entry that has been absent longest and marks the item
`repeated: true` with the real gap. The shortfall is returned, printed by
`--check`, and shown on the archive page rather than hidden.

That is the difference between a rule that is true and a rule that is stated.

Usage:
    python tools/top8_engine.py --date 2026-11-04
    python tools/top8_engine.py --date 2026-11-04 --json
    python tools/top8_engine.py --check        # determinism, parity, gaps
"""
from __future__ import annotations

import argparse
import datetime
import hashlib
import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
TAX = ROOT / "data" / "taxonomy.json"
PLACE = ROOT / "data" / "taxonomy_placements.json"
ENC = ROOT / "data" / "encyclopedia.json"
HIST = ROOT / "data" / "top8_history.json"
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

WINDOW = 30


def _load(path, key=None):
    doc = json.loads(path.read_text(encoding="utf-8"))
    return doc[key] if key else doc


def categories() -> list[str]:
    return [a["id"] for a in _load(TAX)["attachment"]]


def _entries() -> dict:
    return {e["id"]: e for e in _load(ENC)["entries"]}


def _placements() -> dict:
    doc = json.loads(PLACE.read_text(encoding="utf-8"))
    return doc.get("assignments") or {}


def _history_days() -> list[dict]:
    try:
        return json.loads(HIST.read_text(encoding="utf-8")).get("days") or []
    except (OSError, ValueError):
        return []


def _d(day: str) -> datetime.date:
    return datetime.date.fromisoformat(str(day)[:10])


def last_used(history: list[dict], upto: datetime.date, window: int = WINDOW) -> dict:
    """entry id -> most recent date it appeared, inside the window."""
    out = {}
    for rec in history:
        try:
            when = _d(rec["date"])
        except (KeyError, ValueError):
            continue
        if when >= upto or (upto - when).days > window:
            continue
        for eid in rec.get("items") or []:
            if eid not in out or when > out[eid]:
                out[eid] = when
    return out


def _affinity(entry: dict, theme: dict | None) -> int:
    if not theme:
        return 0
    want = {str(t).lower() for t in
            (theme.get("tags") or []) + (theme.get("keywords") or [])}
    have = {str(t).lower() for t in (entry.get("tags") or [])}
    return len(want & have)


def _stable(date: str, cat: str, eid: str) -> str:
    return hashlib.sha256(f"{date}|{cat}|{eid}".encode()).hexdigest()


def get_daily_top8(date: str, theme: dict | None = None,
                   history: list[dict] | None = None,
                   window: int = WINDOW) -> dict:
    """The eight for a date. Pure: same inputs, same output, always."""
    day = _d(date)
    entries = _entries()
    place = _placements()
    hist = _history_days() if history is None else history
    used = last_used(hist, day, window)

    cats = categories()
    items, shortfall = [], []
    picked: set[str] = set()

    for cat in cats:
        pool = [eid for eid, rec in place.items()
                if rec.get("cat") == cat and eid in entries]
        if not pool:
            shortfall.append({"category": cat, "reason": "no entries filed here"})
            continue

        fresh = [eid for eid in pool if eid not in used and eid not in picked]
        repeated = False
        if fresh:
            ranked = sorted(fresh, key=lambda eid: (
                -_affinity(entries[eid], theme), _stable(date, cat, eid)))
            choice = ranked[0]
        else:
            # every candidate was used inside the window: take the one absent
            # longest, and say so rather than pretending the rule held
            repeated = True
            ranked = sorted(pool, key=lambda eid: (
                used.get(eid, datetime.date.min), _stable(date, cat, eid)))
            choice = ranked[0]
            shortfall.append({
                "category": cat,
                "reason": f"all {len(pool)} entries used within {window} days",
                "gap_days": (day - used[choice]).days if choice in used else None,
            })

        picked.add(choice)
        items.append({
            "id": choice,
            "category": cat,
            "repeated": repeated,
            "gap_days": (day - used[choice]).days if choice in used else None,
        })

    return {
        "date": day.isoformat(),
        "window": window,
        "seed": hashlib.sha256(day.isoformat().encode()).hexdigest()[:12],
        "theme": (theme or {}).get("id"),
        "items": items,
        "shortfall": shortfall,
    }


def check(days: int = 45) -> int:
    """Determinism, parity, and the 30-day rule, simulated as a sequence.

    The first version ran each date against the committed history and reported
    that the rule held on all forty, which was true and useless: no future date
    had a history yet, so every window was empty. A rule about what happens
    day after day has to be tested day after day, with each day's list added to
    the history the next one reads.
    """
    problems = []
    today = datetime.date.today()
    cats = categories()
    sim = list(_history_days())

    for offset in range(0, days):
        day = (today + datetime.timedelta(days=offset)).isoformat()
        a = get_daily_top8(day, history=sim)
        b = get_daily_top8(day, history=sim)
        if a != b:
            problems.append(f"{day}: not deterministic")
        ids = [i["id"] for i in a["items"]]
        if len(ids) != len(set(ids)):
            problems.append(f"{day}: duplicate entry in one list")
        if [i["category"] for i in a["items"]] != cats:
            problems.append(f"{day}: categories are not 1:1 with the taxonomy")
        if len(a["items"]) != 8:
            problems.append(f"{day}: {len(a['items'])} items, expected 8")
        sim.append({"date": day, "items": ids})

    # the rule that cannot always hold: count it, do not hide it
    worst = {}
    for offset in range(0, days):
        day = (today + datetime.timedelta(days=offset)).isoformat()
        for i in get_daily_top8(day, history=sim)["items"]:
            if i["repeated"]:
                worst[i["category"]] = worst.get(i["category"], 0) + 1

    if problems:
        print(f"{len(problems)} problem(s):")
        for p in problems[:20]:
            print("  " + p)
        return 1
    print(f"ok: {days} dates x 2 builds identical, 8 categories each, no duplicates")
    if worst:
        print("30-day rule could not hold on some days (pool smaller than the "
              "window), by category:")
        for cat, n in sorted(worst.items()):
            print(f"  {cat:<12} {n} repeated selection(s)")
    else:
        print("30-day rule held on every date checked")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--date")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--check", action="store_true")
    a = ap.parse_args()

    if a.check:
        return check()
    day = a.date or datetime.date.today().isoformat()
    out = get_daily_top8(day)
    if a.json:
        print(json.dumps(out, indent=1))
        return 0
    print(f"{out['date']}  seed {out['seed']}")
    for i in out["items"]:
        flag = " (repeat)" if i["repeated"] else ""
        print(f"  {i['category']:<12} {i['id']}{flag}")
    for s in out["shortfall"]:
        print(f"  ! {s['category']}: {s['reason']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
