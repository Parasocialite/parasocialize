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
import re
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


def placeholder_citations(enc: dict) -> list[dict]:
    """Citation strings that are notes-to-self rather than citations.

    The `transparasocial` entry carried exactly this: the citation text was
    "Schramm, P., & Hartmann, D. (1997).  verify" with an empty URL, and the
    entry still counted as `provenance: sourced` - so the credits rendered a
    to-do as though it were a reference. A string containing one of these words
    is not a citation, whatever status it carries.
    """
    words = ("verify", "todo", "tbd", "fixme", "xxx", "???", "placeholder")
    out = []
    for eid, s in records(enc):
        cit = str(s.get("citation") or "")
        low = cit.lower()
        if any(re.search(rf"\b{re.escape(w)}\b", low) for w in words):
            out.append({"entry": eid, "citation": cit[:90],
                        "status": s.get("status")})
    return out


def contradictory_relations(enc: dict) -> list[dict]:
    """Relations whose chronology contradicts the years they point at.

    build_cards.py renders `preceded` as "came before" and `succeeded` as
    "came after", so these are chronological claims shown to the reader. Fourteen
    of them disagreed with the `year` fields, including a pair that was inverted
    in both directions at once, so the site told the reader that club cards came
    before trading stamps and, on the other page, that trading stamps came after
    club cards. A self-relation is the same defect with the dates removed.

    Checked rather than assumed: the semantics were read out of the renderer
    before any verb was flipped, because "preceded" could have meant lineage
    rather than order and the fix would have been 13 new falsehoods.
    """
    by = {e["id"]: e for e in enc["entries"]}
    out = []
    for e in enc["entries"]:
        for r in (e.get("relations") or []):
            t, tgt = r.get("type"), r.get("to")
            if t not in ("preceded", "succeeded"):
                continue
            if tgt == e["id"]:
                out.append({"entry": e["id"], "rel": t, "to": tgt,
                            "detail": "self-relation"})
                continue
            o = by.get(tgt)
            if not o:
                continue
            a, b = e.get("year"), o.get("year")
            if not isinstance(a, int) or not isinstance(b, int):
                continue
            if t == "preceded" and a >= b:
                out.append({"entry": e["id"], "rel": t, "to": tgt,
                            "detail": f"{a} cannot come before {b}"})
            elif t == "succeeded" and b >= a:
                out.append({"entry": e["id"], "rel": t, "to": tgt,
                            "detail": f"{a} cannot come after {b}"})
    return out


def borrowed_terminology(enc: dict) -> list[dict]:
    """Terms used on an entry other than the one that defines them.

    `the-dog` called itself "the original transparasocial relationship" while
    this site's own `transparasocial` entry defines the term as live people who
    can hear you. A dog cannot read a comment, and its bond reciprocates, so the
    phrase was wrong twice over - and it was invisible, because both entries were
    individually plausible and nothing compared them.

    The rule is narrow on purpose: each defined term may appear in the body of
    the entry that defines it, and nowhere else in entry text.
    """
    defined = {}
    for e in enc["entries"]:
        if e.get("kind") == "term" and e.get("id"):
            defined[e["id"]] = e["id"]
    out = []
    for e in enc["entries"]:
        eid = e.get("id")
        if eid not in defined:
            continue
        term = re.compile(rf"\b{re.escape(eid)}\b", re.I)
        for other in enc["entries"]:
            if other["id"] == eid:
                continue
            for f in ("title", "summary", "significance", "hook"):
                v = other.get(f)
                if isinstance(v, str) and term.search(v):
                    out.append({"entry": other["id"], "field": f,
                                "term": eid})
    return out


def extra_checks(enc: dict) -> int:
    """The contradictions between entries, which no single record can detect.

    Every check so far looks at one record. These look at pairs, and they exist
    because the site's worst errors have all been of the shape "each of these is
    plausible on its own page": two entries claiming the same primacy, a term
    used on an entry other than the one defining it, a relation whose verb
    disagrees with the years it points at, and a to-do string sitting in the
    credits where a citation should be.

    Returns 1 if any of them fires.
    """
    rc = 0
    ph = placeholder_citations(enc)
    print()
    print("  citation strings that are notes to self, not citations:")
    if not ph:
        print("    none. every citation string is a citation.")
    else:
        for p in ph:
            print(f"    FAIL {p['entry']:<26} {p['citation']!r}")
        print(f"\n  FAIL {len(ph)} placeholder(s) rendered in the credits.")
        rc = 1

    cr = contradictory_relations(enc)
    print()
    print("  relations whose chronology contradicts the years:")
    if not cr:
        print("    none. every 'came before' and 'came after' is true of the dates.")
    else:
        for c in cr:
            print(f"    FAIL {c['entry']:<24} {c['rel']:<10} {c['to']:<22} "
                  f"{c['detail']}")
        print(f"\n  FAIL {len(cr)} relation(s) tell the reader a false order.")
        rc = 1

    bt = borrowed_terminology(enc)
    print()
    print("  terms used on an entry other than the one defining them:")
    if not bt:
        print("    none. each defined term is only used on its own entry.")
    else:
        for b in bt:
            print(f"    note {b['entry']:<24} {b['field']:<12} uses "
                  f"'{b['term']}' - by hand, not by gate")
        print("    (report only: using a defined word in prose is not claiming "
              "to define it. This fired on `sasaeng-culture` and `siri`, both "
              "of which are correct. The defect it was built for - the-dog "
              "calling itself 'the original transparasocial relationship' - was "
              "found by reading two entries side by side, and no regex can "
              "tell misapplying a term from using it.)")
    # Reported, not gated. AGENTS.md carried "34 of 423 edges land on something
    # unchecked" for weeks while the true figure was 59, because it was a typed
    # number rather than a computed one and nobody recomputed it. The quantity
    # matters: it is how much of the corpus's connective tissue runs through
    # entries with no citation behind them. Printed on every run so it cannot go
    # stale silently, and never hand-copied into the state block.
    by_id = {e["id"]: e for e in enc["entries"]}
    edges = sum(len(e.get("relations") or []) for e in enc["entries"])
    unsourced_targets = sum(
        1 for e in enc["entries"] for r in (e.get("relations") or [])
        if r.get("to") in by_id and not (by_id[r["to"]].get("sources") or []))
    print()
    print(f"  {unsourced_targets} of {edges} edges land on an entry with no "
          f"citation record")
    return rc


def unverified_claiming_verified(enc: dict) -> list[dict]:
    """Entries whose `verified` flag promises a reading, with nothing to have read.

    `verified: true` is what suppresses the "Not yet stood behind" notice on an
    entry page. It is read as "a person read the citation and confirmed it" -
    which is a claim about a source. Six entries set it while carrying no
    citation records at all, so the page asserted that somebody had read a
    reference that does not exist, and the only visible consequence was that the
    honest notice disappeared.

    This is the third instance of the same defect in this repo - the first
    inflated the backlog by counting thesis entries, the second inflated the
    credits with records whose status was read but whose URL was not. This one
    removes a gap from the page rather than adding a number to a chart, which
    makes it the only instance a reader is directly misled by.

    Thesis entries are exempt: they carry no sources by design, and `verified`
    is not a meaningful field for them - which is precisely why they are counted
    separately rather than waved through.
    """
    out = []
    for e in enc["entries"]:
        if e.get("provenance") == "thesis":
            continue
        if e.get("verified") and not (e.get("sources") or []):
            out.append({"entry": e["id"],
                        "summary": str(e.get("summary", ""))[:90]})
    return out


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
        # NOT an early return. The record-level check being clean used to end
        # the run, which meant the entry-level check below it never executed on
        # a clean build - a gate placed after the one exit that is always taken
        # is decoration.
        fv = unverified_claiming_verified(enc)
        print()
        print("  entries claiming verified with no source to have read:")
        if not fv:
            print("    none. every entry that claims a reading has something to "
                  "have read it from.")
        else:
            for f in fv:
                print(f"    FAIL {f['entry']:<26} {f['summary'][:60]}")
            print(f"\n  FAIL {len(fv)} entr(ies) set verified: true with no "
                  "citation records, which removes the 'not yet stood behind' "
                  "notice from the page. Either add a source or set "
                  "verified: false.")
            return 1
        return extra_checks(enc)

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

    # Not ratcheted. This one is not a pre-existing debt to be tolerated and
    # improved against - it is a boolean that is currently asserting something
    # false on six pages, and the fix is a one-word data change, so there is
    # nothing to be gained by starting life behind it.
    fv = unverified_claiming_verified(enc)
    print()
    print("  entries claiming verified with no source to have read:")
    if not fv:
        print("    none. every entry that claims a reading has something to have "
              "read it from.")
    else:
        for f in fv:
            print(f"    FAIL {f['entry']:<26} {f['summary'][:60]}")
        print(f"\n  FAIL {len(fv)} entr(ies) set verified: true with no citation "
              "records, which removes the 'not yet stood behind' notice from "
              "the page. Either add a source or set verified: false.")
        return 1
    return extra_checks(enc)


if __name__ == "__main__":
    raise SystemExit(main())