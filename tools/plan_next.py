#!/usr/bin/env python3
"""plan_next.py - the next categorical work, measured instead of remembered.

WHY THIS EXISTS
The editorial queue was being chosen from memory. Lists were grown in hand-
written batches, the thinnest medium was noticed when somebody happened to
count it, and the counter's own pipeline went 32 days without a sweep while
the front page still described it as running. None of that is a content
problem; it is a planning problem. A corpus cannot report its own blind spots,
so the gaps have to be measured on every run and written down where the next
agent will find them.

This tool reads the corpus and emits a ranked, reproducible work order:

  * which medium runs out first under the bi-daily cadence;
  * which attachment category has no story behind it;
  * which decade is thinnest;
  * how much of the corpus sits in the `history` / `technology` catch-alls;
  * whether a top-8 pool has too few distinct windows to rotate;
  * whether the sweeper that is supposed to find new material has actually run.

Two rules keep it honest. It generates NO sourced material - it names the gap
and the exact next action, and leaves the reading to a person. And it never
fills an empty sub-category to make a distribution look even; those are
reported as `leave_empty`, because a plausible-looking entry is the defect
this project exists to avoid.

Output: data/plan.json, overwritten each run with `generated` set to today, so
a stale plan is visible as a stale plan. The human-readable form is printed.

Usage:
    python tools/plan_next.py
    python tools/plan_next.py --check   # invariant check only, no write
"""
from __future__ import annotations

import argparse
import datetime
import json
import math
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
TOOLS = ROOT / "tools"
sys.path.insert(0, str(TOOLS))

import build_cards as bc  # noqa: E402
import atlas  # noqa: E402  (MEDIA and its labels are the axis, not a copy)

sys.stdout.reconfigure(encoding="utf-8")
OUT = ROOT / "data" / "plan.json"


def load(path, default):
    try:
        return json.loads((ROOT / "data" / path).read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return default


def decade_of(year) -> str:
    try:
        y = int(year)
    except (TypeError, ValueError):
        return "unknown"
    if y < 1000:
        return "before 1000"
    return f"{(y // 10) * 10}s"


def measure(today: datetime.date) -> dict:
    enc = load("encyclopedia.json", {"entries": []})
    tax = load("taxonomy.json", {"attachment": []})
    tp = load("taxonomy_placements.json", {"assignments": {}})["assignments"]
    sp = load("story_placements.json", {"placements": {}})["placements"]
    shop = load("shop.json", {"cards": []})
    feat = load("features.json", {"lists": []})
    queue = load("queue.json", [])
    sweep = load("sweep.json", {})

    entries = enc.get("entries") or []
    cards = shop.get("cards") or []

    # --- the medium axis -------------------------------------------------
    media = {}
    for m in atlas.MEDIA:
        media[m] = 0
    for e in entries:
        vals = e.get("medium")
        if isinstance(vals, str):
            vals = [vals]
        for v in vals or []:
            if v in media:
                media[v] += 1
    media_rows = sorted(media.items(), key=lambda kv: (kv[1], kv[0]))
    catch_all = media.get("history", 0) + media.get("technology", 0)

    # --- the attachment axis --------------------------------------------
    cats, subs = {}, {}
    for c in tax.get("attachment") or []:
        cats[c["id"]] = {"name": c.get("sign") or c["id"], "entries": 0,
                         "stories": 0}
        for s in c.get("sub") or []:
            subs[(c["id"], s["id"])] = {"name": s.get("name") or s["id"],
                                        "entries": 0, "stories": 0}
    for _, v in tp.items():
        if v.get("cat") in cats:
            cats[v["cat"]]["entries"] += 1
            if (v["cat"], v.get("sub")) in subs:
                subs[(v["cat"], v.get("sub"))]["entries"] += 1
    for _, v in sp.items():
        if v.get("cat") in cats:
            cats[v["cat"]]["stories"] += 1
            if (v["cat"], v.get("sub")) in subs:
                subs[(v["cat"], v.get("sub"))]["stories"] += 1

    empty_subs = sorted(f"{c}/{s}" for (c, s), v in subs.items()
                        if v["entries"] == 0)
    storyless = sorted(((c, v) for c, v in cats.items() if v["stories"] == 0),
                       key=lambda kv: (-kv[1]["entries"], kv[0]))

    # --- chronology ------------------------------------------------------
    decades = {}
    for e in entries:
        decades[decade_of(e.get("year"))] = \
            decades.get(decade_of(e.get("year")), 0) + 1
    dated = sorted(((k, v) for k, v in decades.items()
                    if k not in ("unknown", "before 1000")),
                   key=lambda kv: kv[0])
    thin_decades = sorted(dated, key=lambda kv: (kv[1], kv[0]))[:5]

    # --- top 8 ------------------------------------------------------------
    top8 = []
    for L in bc.live_lists(feat, today.isoformat()):
        featured = [e for e in L.get("entries") or []
                    if e.get("stage", "featured") == "featured"]
        n = len(featured)
        # Distinct windows the stride-8 cycle can reach. gcd(8, n) windows
        # collapse into one, which is how a pool of 24 produced three windows
        # while looking like a 24-moment rotation.
        windows = (n // math.gcd(bc.TOP8_SLOTS, n)) if n > bc.TOP8_SLOTS else 1
        top8.append({"slug": L.get("slug"), "title": L.get("title"),
                     "pool": n, "windows": windows})

    # --- the sweeper ------------------------------------------------------
    sweep_age = None
    if sweep.get("last_run"):
        try:
            when = datetime.datetime.fromisoformat(
                str(sweep["last_run"]).replace("Z", "+00:00"))
            if when.tzinfo is None:
                when = when.replace(tzinfo=datetime.timezone.utc)
            sweep_age = (datetime.datetime.now(datetime.timezone.utc)
                         - when).days
        except ValueError:
            sweep_age = None

    awaiting = sum(1 for q in queue if q.get("state") == "awaiting")

    return {"today": today.isoformat(), "entries": len(entries),
            "stories": len(cards), "media": media_rows, "catch_all": catch_all,
            "categories": cats, "empty_subs": empty_subs,
            "storyless": storyless, "decades": decades,
            "thin_decades": thin_decades, "top8": top8,
            "sweep_age": sweep_age, "queue_awaiting": awaiting,
            "queue_total": len(queue)}


def actions(m: dict) -> list[dict]:
    """A ranked work order. Scores are editorial weight, not a promise."""
    out = []

    def add(score, kind, target, why, command):
        out.append({"rank": 0, "score": round(score, 1), "kind": kind,
                    "target": target, "why": why, "command": command})

    # The generation pipeline being dead is the biggest deficiency, because
    # nothing downstream can be chosen from material that is never found.
    if m["sweep_age"] is None or m["sweep_age"] > 2:
        age = "never" if m["sweep_age"] is None else f"{m['sweep_age']} days"
        add(100, "pipeline", "the sweeper",
            f"The counter has not run for {age}; its queue cannot grow while "
            f"it is asleep.",
            "python tools/counter.py && python tools/build_cards.py")

    for cid, v in m["storyless"]:
        add(96, "story", cid,
            f"{v['name']} holds {v['entries']} entries and 0 stories. The "
            f"category exists on the front page with nothing journalistic "
            f"behind it.",
            "write one story for this category, or say on /ways/ that the "
            "entries are the whole of it")

    # Thin media: days of bi-daily cadence left if the axis walked it alone.
    for name, n in m["media"][:4]:
        days = n / 2
        add(90 - days, "medium", name,
            f"{name}: {n} entries, {days:.1f} days at two entries per release.",
            f"find and source the next {name} entry; the atlas filter is "
            f"already live for it")

    catch_share = (m["catch_all"] / m["entries"] * 100) if m["entries"] else 0
    if catch_share >= 30:
        add(72, "axis", "history + technology",
            f"{m['catch_all']} of {m['entries']} entries "
            f"({catch_share:.0f}%) sit in the two catch-alls that name no "
            f"medium.",
            "re-file an entry only where its own medium is stated; do not move "
            "one to make the distribution look even")

    for name, n in m["thin_decades"]:
        add(64 - n, "decade", name,
            f"{name} holds {n} entries.",
            "source one dated entry for this decade, or record it as a gap")

    for t in m["top8"]:
        if t["windows"] < 3:
            add(84, "top8", t["slug"],
                f"{t['pool']} moments produce only {t['windows']} distinct "
                f"window(s) at a stride of {bc.TOP8_SLOTS}; the page will "
                f"repeat sooner than readers expect.",
                "grow the pool with tools/t8_grow.py, checking the show string "
                "as well as the eid")

    if m["empty_subs"]:
        add(40, "taxonomy", f"{len(m['empty_subs'])} empty sub-categories",
            "Empty sub-categories are reported, not filled: "
            + ", ".join(m["empty_subs"][:6]),
            "leave them empty until an entry actually belongs there")

    if m["queue_awaiting"] >= 3:
        add(50, "queue", f"{m['queue_awaiting']} drafts awaiting signoff",
            "Nothing reaches the shelf without a person signing it.",
            "python tools/build_cards.py  # then read /desk/")

    out.sort(key=lambda a: (-a["score"], a["kind"], a["target"]))
    for i, a in enumerate(out, 1):
        a["rank"] = i
    return out


def render(m: dict) -> str:
    lines = [f"plan for {m['today']}: {m['entries']} entries, "
             f"{m['stories']} stories",
             "",
             "media, thinnest first (days at 2 entries/release):"]
    for name, n in m["media"]:
        lines.append(f"  {name:<22} {n:>3}   {n/2:>4.1f} days")
    lines.append(f"  catch-all share: {m['catch_all']}/{m['entries']} "
                 f"({m['catch_all']/max(1,m['entries'])*100:.0f}%)")
    lines.append("")
    lines.append("attachment categories:")
    for cid, v in sorted(m["categories"].items()):
        lines.append(f"  {cid:<12} {v['entries']:>3} entries "
                     f"{v['stories']:>3} stories")
    lines.append("")
    lines.append("top 8 pools:")
    for t in m["top8"]:
        lines.append(f"  {t['slug']:<28} pool {t['pool']:>3}  "
                     f"windows {t['windows']}")
    lines.append("")
    return "\n".join(lines)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true",
                    help="assert the coverage invariants; write nothing")
    a = ap.parse_args()
    today = datetime.datetime.now(datetime.timezone.utc).date()
    m = measure(today)

    if a.check:
        bad = []
        zero_media = [k for k, v in m["media"] if v == 0]
        if zero_media:
            bad.append(f"medium with no entry: {zero_media}")
        for cid, v in m["categories"].items():
            if v["entries"] == 0:
                bad.append(f"category with no entry: {cid}")
        if bad:
            for b in bad:
                print(f"FAIL {b}")
            return 1
        print(f"plan invariants ok: {len(m['media'])} media, "
              f"{len(m['categories'])} categories, all populated")
        return 0

    plan = {"_note": (
                "GENERATED by tools/plan_next.py. A ranked work order measured "
                "from the corpus, rewritten each run; `generated` is the date "
                "the measurement was taken, so a stale plan is visible as one. "
                "It names gaps and next actions, and never authors a source."),
            "generated": m["today"],
            "entries": m["entries"], "stories": m["stories"],
            "media": [{"medium": k, "entries": v, "days": v / 2}
                      for k, v in m["media"]],
            "catch_all": {"entries": m["catch_all"],
                          "share": round(m["catch_all"] / max(1, m["entries"]), 3)},
            "categories": m["categories"],
            "empty_sub_categories": m["empty_subs"],
            "thin_decades": [{"decade": k, "entries": v}
                             for k, v in m["thin_decades"]],
            "top8": m["top8"],
            "sweep_age_days": m["sweep_age"],
            "queue_awaiting": m["queue_awaiting"],
            "actions": actions(m)}
    OUT.write_text(json.dumps(plan, ensure_ascii=False, indent=1) + "\n",
                   encoding="utf-8")

    print(render(m))
    print("next, highest first:")
    for a in plan["actions"][:8]:
        print(f"  {a['rank']}. [{a['kind']}] {a['target']}")
        print(f"     {a['why']}")
    print(f"\nwrote {OUT.relative_to(ROOT).as_posix()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
