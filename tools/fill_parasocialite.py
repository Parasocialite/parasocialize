#!/usr/bin/env python3
"""fill_parasocialite.py - close missed days in the figure record.

WHY THIS EXISTS
The parasocialite is one figure a day, and the record only gains a day when a
build runs. When the scheduler misses a day there is no record, and the archive
used to declare that hole unrecoverable on the grounds that the figure was
chosen against that day's wires.

That is only half true. The editor's pick depends on the wires; the fallback
does not. The fallback is a deterministic walk of the selectable bank, seeded by
the date and excluding the last 30 days, and it is what the page would have
shown on any day with no edition. So a missed day CAN be reopened - as a
reconstruction, marked, never passed off as observed.

This runs before the build on every daily cycle, so the record heals itself and
"a new figure a day" stops depending on the scheduler being punctual.

Usage:
    python tools/fill_parasocialite.py            # fill to today
    python tools/fill_parasocialite.py --dry-run
"""
from __future__ import annotations

import argparse
import datetime
import hashlib
import json
import pathlib
import sys
import tempfile

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))
import build_cards as bc  # noqa: E402

HIST = ROOT / "data" / "parasocialite_history.json"
sys.stdout.reconfigure(encoding="utf-8", errors="replace")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--until", default=None, help="ISO date, default today (UTC)")
    a = ap.parse_args()

    if not HIST.is_file():
        print("no record to fill")
        return 0
    doc = json.loads(HIST.read_text(encoding="utf-8"))
    days = sorted(doc.get("days") or [], key=lambda d: str(d["date"]))
    if not days:
        print("no record to fill")
        return 0

    until = a.until or datetime.datetime.now(datetime.timezone.utc).date().isoformat()
    end = datetime.date.fromisoformat(until[:10])
    have = {str(d["date"])[:10] for d in days}
    start = datetime.date.fromisoformat(str(days[0]["date"])[:10])
    roster = bc.parasocialite_roster()

    tmp = pathlib.Path(tempfile.gettempdir()) / "fill_parasocialite.json"
    tmp.write_text(json.dumps({"days": days}, ensure_ascii=False), encoding="utf-8")
    original = bc.PARASOCIALITE_HISTORY
    bc.PARASOCIALITE_HISTORY = tmp

    added = []
    try:
        d = start
        while d <= end:
            iso = d.isoformat()
            if iso not in have:
                m = bc.parasocialite_of_day(roster=roster, today=iso)
                if m:
                    days.append({"date": iso, "member": m["id"],
                                 "reconstructed": True,
                                 "reconstructed_on": end.isoformat(),
                                 "inputs_sha256": hashlib.sha256(
                                     (ROOT / "data" / "parasocialite.json")
                                     .read_bytes()).hexdigest()})
                    have.add(iso)
                    added.append((iso, m["id"]))
                    tmp.write_text(json.dumps({"days": days}, ensure_ascii=False),
                                   encoding="utf-8")
            d += datetime.timedelta(days=1)
    finally:
        bc.PARASOCIALITE_HISTORY = original

    if not added:
        print("record complete: no missed days")
        return 0

    if a.dry_run:
        for iso, mid in added:
            print("would add", iso, mid)
        return 0

    days.sort(key=lambda r: str(r["date"]))
    doc["days"] = days
    note = doc.get("_note", "")
    if "reconstructed" not in note:
        doc["_note"] = (note + " Days marked `reconstructed` had no build; the "
                        "figure is what the date-seeded rule would have put "
                        "forward, not an observed editorial choice.")
    HIST.write_text(json.dumps(doc, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"filled {len(added)} missed day(s)")
    for iso, mid in added[:8]:
        print(" ", iso, mid)
    if len(added) > 8:
        print(f"  ... and {len(added) - 8} more")
    return 0


if __name__ == "__main__":
    sys.exit(main())
