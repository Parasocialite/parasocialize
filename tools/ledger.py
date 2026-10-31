"""The figures the public ledger publishes.

Single source of truth for every number that appears on /ledger/.
`report_current_state.py` and `build_cards.py` both import this rather
than each counting for itself, because two definitions of "openable" on a site
whose entire argument is that it does not blur its own states would be the exact
defect the ledger exists to prevent. This is the `kind: exact` lesson at the
level of a measurement: a number copied into a template is a claim, and it goes
stale silently.

It also holds the settled wording for entry-level verification. That definition
was ambiguous in the data and was ruled on explicitly rather than picked by
default - see VERIFIED_DEF and `verified_note`.
"""
import collections
import datetime
import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent

SNAPSHOT_NOTE = (
    "A day-by-day record of the figures /ledger/ publishes, written by "
    "tools/ledger.py and only when one of them moved. The feed at /ledger/feed.xml "
    "is generated from this file: it is the only thing on the site that says the "
    "numbers changed rather than the numbers as they stand. Appended, never "
    "rewritten - the sequence of what the archive claimed over time is the point."
)

# The ruling. `verified: true` on an entry means the entry's core assertions
# were checked against at least one source a human opened. It does NOT mean every
# record on that entry was read, and the corpus has plenty of entries holding
# secondary records that remain unverified or needs-source. The two readings
# were in genuine conflict - the documentation said record-level while the data
# was entry-level - and the entry-level reading is what the editorial workflow
# actually does. Anything that publishes this number must print VERIFIED_DEF
# alongside it, because the alternative is the number promising more than the
# field keeps.
VERIFIED_DEF = (
    "Entry-level verification: an entry is marked verified once a person here "
    "has checked its central claims against source material they actually "
    "opened. Individual records on that entry keep their own states and are "
    "audited in their own time - a checked entry can still be carrying "
    "secondary references nobody has read."
)


def _records(entries):
    return [s for e in entries for s in (e.get("sources") or [])]


def ledger_metrics(enc):
    """Every figure the ledger shows. `enc` is the parsed encyclopedia.json."""
    entries = enc["entries"] if isinstance(enc, dict) else enc
    recs = _records(entries)
    by_status = collections.Counter(r.get("status") for r in recs)
    loc = sum(1 for r in recs if r.get("url"))
    return {
        "entries": len(entries),
        "records": len(recs),
        # LOCATOR, not readership. "Openable" answers exactly one question: can
        # a reader click this and find the work. It says nothing about whether
        # anybody did. Conflating the two is what produced the first draft of
        # the front-page copy, which would have printed "434 read" over a
        # figure that measures URLs.
        "openable": loc,
        "no_locator": len(recs) - loc,
        "status_retrievable": by_status.get("retrievable", 0),
        "status_unverified": by_status.get("unverified", 0),
        "status_needs_source": by_status.get("needs-source", 0),
        "verified_entries": sum(1 for e in entries if e.get("verified")),
        "unverified_entries": sum(1 for e in entries if not e.get("verified")),
        # thesis entries carry no citation by design - that is not a gap, and
        # the ledger says so rather than folding them into a deficit.
        "thesis": sum(1 for e in entries if e.get("provenance") == "thesis"),
        "no_records": sum(1 for e in entries if not (e.get("sources") or [])),
        "relations": sum(len(e.get("relations") or []) for e in entries),
    }


def verified_note(m):
    """The sentence that must accompany the verified figure wherever it appears."""
    return (f"{m['verified_entries']} of {m['entries']} entries are marked "
            f"verified, which means a person here read source material and "
            f"checked the entry's central claims against it. It does not mean "
            f"every reference on those entries has been read - "
            f"{m['records'] - m['openable']} of {m['records']} records still "
            f"have no locator at all.")


def exceptions_metrics(enc, placements):
    """The reciprocity-axis figures, and the admission about the other axis.

    Read from `taxonomy_placements.json`, which carries a real `rec` field per
    entry. An earlier plan was to recover this from the placement prose by
    regex, because the axis has no field on the entries themselves - that would
    have been a number about the wrong layer, and this file exists to stop
    those.

    Returns both the counts and the shape. The shape matters as much as the
    count: a flat "10 of 240" hides that the reciprocated three span thirty-five
    thousand years, that the simulated five arrive in two clusters seventy years
    apart, and that most media hold none at all. Publishing the count without
    the shape is the thing this site keeps refusing to do elsewhere.
    """
    entries = enc["entries"] if isinstance(enc, dict) else enc
    by_id = {e["id"]: e for e in entries}
    assign = placements.get("assignments") or placements
    labelled = [(i, v.get("rec")) for i, v in assign.items() if (v or {}).get("rec")]
    members = ("reciprocated", "simulated", "directed")
    groups = {m: sorted(i for i, r in labelled if r == m) for m in members}

    def years(ids):
        return sorted((by_id[i].get("year") or 0) for i in ids if i in by_id)

    rec_years = years(groups["reciprocated"])
    sim_years = years(groups["simulated"])
    # the longest silence between consecutive simulated instances - the number
    # that is doing the arguing on the page, so it is derived rather than typed
    gaps = [b - a for a, b in zip(sim_years, sim_years[1:])]
    max_gap = max(gaps) if gaps else 0

    all_med = {mm for e in entries for mm in (e.get("medium") or [])}
    exc_med = {mm for i, _ in labelled for mm in (by_id.get(i, {}).get("medium") or [])}
    with_other = sum(1 for i, _ in labelled if (assign.get(i) or {}).get("other"))

    return {
        "entries": len(entries),
        "labelled": len(labelled),
        "reciprocated": len(groups["reciprocated"]),
        "simulated": len(groups["simulated"]),
        "directed": len(groups["directed"]),
        "reciprocated_ids": groups["reciprocated"],
        "simulated_ids": groups["simulated"],
        "reciprocated_years": rec_years,
        "simulated_years": sim_years,
        "rec_span": (max(rec_years) - min(rec_years)) if rec_years else 0,
        "max_gap": max_gap,
        "media_total": len(all_med),
        "media_without": sorted(all_med - exc_med),
        "with_other": with_other,
        "without_other": len(labelled) - with_other,
        "_by_id": by_id,
    }


def thousands(n):
    """Format a span the way the page states it. 35020 -> '35,020'."""
    return f"{n:,}"


# ---------------------------------------------------------------- ledger feed
HISTORY = ROOT / "data" / "ledger_history.json"

# The fields worth watching. A snapshot is only recorded when one of these moves,
# so the feed says "the numbers changed" and is silent otherwise. Watching all of
# them would publish an item every time a title was edited.
WATCHED = ("entries", "records", "openable", "no_locator", "verified_entries",
           "status_needs_source", "thesis")


def record_snapshot(m, today=None):
    """Append today's figures to the ledger history, if they moved.

    A feed that republishes the same numbers on every build is worse than no
    feed: it promises movement and delivers the same item forever. So this only
    writes when a watched figure actually changed, and it collapses repeated
    builds on one day into a single entry.

    Returns (appended, entry).
    """
    today = today or datetime.date.today().isoformat()
    fig = {k: m[k] for k in WATCHED}
    hist = (json.loads(HISTORY.read_text(encoding="utf-8"))
            if HISTORY.exists() else {"_note": SNAPSHOT_NOTE, "days": []})
    days = hist.setdefault("days", [])
    last = days[-1] if days else None
    if last and last["date"] == today:
        if last["figures"] == fig:
            return False, last
        days.pop()          # rebuild today's entry rather than duplicate it
    if last and last["figures"] == fig:
        return False, last  # nothing moved since the last recorded day
    entry = {"date": today, "figures": fig}
    days.append(entry)
    # Keep it bounded but long enough to be a record: a build a day for two years.
    del days[:-800]
    HISTORY.parent.mkdir(parents=True, exist_ok=True)
    HISTORY.write_text(json.dumps(hist, ensure_ascii=False, indent=1) + "\n",
                       encoding="utf-8")
    return True, entry


def snapshot_sentence(prev, cur):
    """What moved between two figures, as a sentence. Never a vague 'updated'."""
    parts = []
    for k in WATCHED:
        a, b = prev.get(k), cur.get(k)
        if a == b:
            continue
        if k == "entries":
            parts.append(f"{b - a:+d} entries" if b != a else "entries unchanged")
        elif k == "records":
            parts.append(f"{b - a:+d} source records")
        elif k == "openable":
            parts.append(f"{b - a:+d} records became openable")
        elif k == "no_locator":
            parts.append(f"{b - a:+d} records without a locator")
        elif k == "verified_entries":
            parts.append(f"{b - a:+d} entries verified")
        elif k == "status_needs_source":
            parts.append(f"{b - a:+d} records that are not citations")
        elif k == "thesis":
            parts.append(f"{b - a:+d} thesis entries")
    return "; ".join(parts) if parts else "figures unchanged"


def main():
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    enc = json.loads((ROOT / "data" / "encyclopedia.json").read_text(encoding="utf-8"))
    m = ledger_metrics(enc)
    # Every status must reconcile to the record total, or a record has a status
    # nobody has defined and the ledger is publishing a breakdown that does not
    # add up. Fail loudly rather than render a partial bar.
    st = (m["status_retrievable"] + m["status_unverified"]
          + m["status_needs_source"])
    if st != m["records"]:
        print(f"REFUSING: statuses sum to {st}, records are {m['records']}. "
              f"An unknown status is present.", file=sys.stderr)
        return 1
    assert m["openable"] + m["no_locator"] == m["records"]
    assert m["verified_entries"] + m["unverified_entries"] == m["entries"]
    print(json.dumps(m, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
