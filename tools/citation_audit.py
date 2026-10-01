#!/usr/bin/env python3
"""
citation_audit.py - does every source record mean what its status field says?

    python tools/citation_audit.py           # report, non-zero if worse than baseline
    python tools/citation_audit.py --ratchet # accept the current count as baseline
    python tools/citation_audit.py --strict  # zero tolerance, nothing allowed

THE INVARIANT
AGENTS.md defines the statuses:

    verified      the source was read
    retrievable   a reader can open this and find it

"retrievable" is a claim about a URL. A record with an empty `url` cannot be
opened by anyone, so it cannot be retrievable, whatever its status field says.
94 of the 292 records were in exactly that state: `status: retrievable` with no
URL. They rendered as standing behind their entry, because
build_cards.is_checked() only reads `status` and never looks at the URL.

This is the same class of defect as the `is_sourced()` thesis trap already in
AGENTS.md: a field that reads as a promise it does not keep. And it is worse in
kind, because thesis entries were inflated into the *backlog* - visible, if
mislabelled - whereas these are inflated into the *credit*. The site's central
claim is that it never invents a citation; the one place that claim would do most
damage is the citation list, not the gap list.

WHY A RATCHET AND NOT A HARD FAILURE
94 records already break the rule. A gate that fails on the first violation
would block every build until someone manually sourced 94 works, which is a
laundry list, not a gate - and it would get disabled within a week.

So the baseline is explicit and committed, and the gate fails only when the
count goes ABOVE it. New violations cannot be added; existing ones stay visible
and can only shrink. `--ratchet` lowers the bar deliberately and is the only
way to add capacity back, which means accepting a worse board has to be a
deliberate act in a commit rather than a drift nobody notices.

This does NOT change any status. Downgrading 94 records to `unverified` is an
editorial decision about what the site claims, not a lint fix, and it is not
this tool's to make.
"""
from __future__ import annotations

import argparse
import json
import pathlib
import sys
from collections import Counter

ROOT = pathlib.Path(__file__).resolve().parent.parent
ENC = ROOT / "data" / "encyclopedia.json"
BASELINE = ROOT / "tools" / "citation_audit_baseline.json"

OPENING_STATUSES = {"retrievable", "verified"}


def load() -> dict:
    return json.loads(ENC.read_text(encoding="utf-8"))


def records(enc: dict) -> list[tuple[str, dict]]:
    return [(e["id"], s) for e in enc["entries"] for s in (e.get("sources") or [])]


def has_url(rec: dict) -> bool:
    return bool(str(rec.get("url") or "").strip())


def audit(enc: dict) -> dict:
    """Every record whose status claims it can be opened, and cannot be."""
    recs = records(enc)
    bad = []
    for eid, s in recs:
        if s.get("status") in OPENING_STATUSES and not has_url(s):
            bad.append({"entry": eid, "status": s.get("status"),
                        "citation": str(s.get("citation", ""))[:90]})
    by_entry = Counter(b["entry"] for b in bad)
    statuses = Counter(s.get("status") for _, s in recs)
    return {
        "records": len(recs),
        "with_url": sum(1 for _, s in recs if has_url(s)),
        "unopenable_claiming_open": len(bad),
        "entries_affected": len(by_entry),
        "worst_entries": by_entry.most_common(8),
        "status_counts": dict(statuses),
        "violations": bad,
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--ratchet", action="store_true",
                    help="record the current violation count as the new baseline")
    ap.add_argument("--strict", action="store_true",
                    help="require zero violations, whatever the baseline")
    ap.add_argument("--list", action="store_true",
                    help="print every offending record")
    a = ap.parse_args()

    enc = load()
    res = audit(enc)

    if a.ratchet:
        BASELINE.write_text(json.dumps({
            "_note": "Ceiling on records claiming retrievable/verified with no "
                     "URL. Lower tools/citation_audit_baseline.json by hand, or "
                     "with --ratchet, only when the count genuinely falls. Do "
                     "not raise it to silence a failure - that is the one move "
                     "that makes this tool useless.",
            "max_unopenable_claiming_open": res["unopenable_claiming_open"],
        }, indent=1), encoding="utf-8")
        print(f"  baseline set to {res['unopenable_claiming_open']}")
        return 0

    print()
    print(f"  records                          {res['records']}")
    print(f"  with a URL                       {res['with_url']}")
    print(f"  statuses                         {res['status_counts']}")
    print()
    print(f"  claiming retrievable/verified with no URL   "
          f"{res['unopenable_claiming_open']}")
    print(f"  entries affected                          "
          f"{res['entries_affected']}")
    print()

    if not res["violations"]:
        print("  none. every record that claims to be openable carries a URL.")
        return 0

    if a.list:
        for v in res["violations"]:
            print(f"    {v['status']:12} {v['entry']:26} {v['citation']}")

    worst = ", ".join(f"{e}({n})" for e, n in res["worst_entries"])
    print(f"  worst affected: {worst}")

    if a.strict:
        print()
        print(f"  FAIL --strict: {res['unopenable_claiming_open']} violation(s) "
              "is not zero")
        return 1

    base = 0
    if BASELINE.exists():
        base = json.loads(BASELINE.read_text(encoding="utf-8")).get(
            "max_unopenable_claiming_open", 0)
    got = res["unopenable_claiming_open"]
    print(f"  baseline allows {base}")
    if got > base:
        print()
        print(f"  FAIL {got} > baseline {base}. A record was added or promoted to")
        print("  retrievable/verified without a URL. Add the URL, or accept the")
        print("  new count on purpose with --ratchet.")
        return 1
    if got < base:
        print(f"  improved: {got} < baseline {base}. Lower the baseline in "
              f"{BASELINE.name} so the gain cannot be lost.")
    print("  ok. no new violations. (lower the baseline as these get fixed)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())