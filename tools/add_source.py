"""Add source records to encyclopedia entries, and separate argument from claim.

TWO PROBLEMS WERE BEING COUNTED AS ONE.

Half the unsourced backlog is `kind: mechanism` - macy-paradox, the-clerk,
club-card, parasocial-consent. Those are the site's own analytical framework:
propositions argued from the evidence rather than facts asserted about the
world. "The relationship has an employer" cannot be cited to a source, because
the argument IS the source. Attaching a citation to one would be decoration
dressed as rigour, which is the exact failure this site exists to avoid, and it
would also make the citation count meaningless by inflating it with
unciteable entries marked as cited.

So provenance is now explicit:

  thesis    the site's own framework. Not a gap. Shown as argued, not sourced.
  sourced   a claim about the world, carrying at least one source record.

The citations page counts the second and stops pretending the first is a
to-do. The distinction is stored on the entry rather than inferred at build
time, because whether something is the site's argument or a fact about the
world is an editorial judgement made once, deliberately, not something a
template should re-guess on every build.

Source records are validated on the way in: a citation with no locator is
allowed but marked, because a bare citation is still evidence of having looked,
and pretending otherwise would lose that signal. What is refused is a record
with no citation text at all, which is just an empty box.
"""
from __future__ import annotations

import json
import pathlib
import re

ENC = pathlib.Path("data/encyclopedia.json")
VALID_STATUS = {"verified", "retrievable", "unverified", "needs-source"}
VALID_PROV = {"thesis", "sourced", ""}

# Entries that are the site's own framework rather than claims about the world.
# Keyed by id so the judgement is explicit and reviewable, not a heuristic.
THESIS = {
    "macy", "macy-paradox", "the-clerk", "club-card",
    "parasocial-consent", "protagonist-parasocial", "the-audience",
    "will-and-want", "the-counter", "counter",
    # Added after reading the 30 remaining entries in full rather than
    # judging by title. Each of these states our own claim with no
    # external referent to attach a citation to: the entry IS the
    # argument. Reclassifying them is the honest outcome - it removes
    # them from the gap list rather than inventing a source for them.
    "scale-change",          # "nothing about the bond is new... those are new"
    "clerks-beat-algorithms", # our claim about attention vs. a model of your history
    "quarterly-audit",       # the site's own exercise, for the reader to do
    "the-reply-heres-watching", # our framing of fan conflict as public performance
    "ratio",                 # our characterisation, not a documented incident
}


def validate(rec: dict, where: str) -> list[str]:
    errs = []
    if not str(rec.get("citation") or "").strip():
        errs.append(f"{where}: citation text is empty")
    if rec.get("status") not in VALID_STATUS:
        errs.append(f"{where}: status {rec.get('status')!r} not in {sorted(VALID_STATUS)}")
    if not str(rec.get("claim") or "").strip():
        errs.append(f"{where}: claim is empty")
    # A record that claims a reader can open it has to carry somewhere to open.
    # "retrievable" is defined as exactly that, so claiming it without a URL is
    # a false statement about the source rather than a missing nicety - and it is
    # the field a reader would most reasonably act on.
    #
    # 94 records in the encyclopedia are already in this state, which is why
    # this is refused on the way IN rather than enforced across the file. Adding
    # a 95th is a decision; this is where to stop it being a decision by accident.
    # The existing ones are an editorial question for the site to settle, and
    # tools/citation_audit.py tracks the count so it can only fall.
    if rec.get("status") in ("retrievable", "verified") and not has_locator(rec):
        errs.append(f"{where}: status {rec.get('status')!r} claims a reader can "
                    "open this, but there is no url. Add the url, or use "
                    "'unverified' - which means looked at, not yet locatable.")
    return errs


def has_locator(rec: dict) -> bool:
    return bool(str(rec.get("url") or "").strip())


def load():
    return json.loads(ENC.read_text(encoding="utf-8"))


def save(d):
    ENC.write_text(json.dumps(d, indent=2, ensure_ascii=False), encoding="utf-8")


def apply_provenance(d) -> dict:
    """Mark thesis entries. Idempotent."""
    changed = 0
    for e in d["entries"]:
        want = "thesis" if e["id"] in THESIS else (
            "sourced" if (e.get("sources") or []) else "")
        if e.get("provenance") != want:
            e["provenance"] = want
            changed += 1
    return {"provenance set on": changed}


def add(d, entry_id: str, records: list[dict]) -> dict:
    e = next((x for x in d["entries"] if x["id"] == entry_id), None)
    if e is None:
        return {"error": f"no such entry: {entry_id}"}
    errs = []
    for i, r in enumerate(records):
        errs += validate(r, f"{entry_id}[{i}]")
    if errs:
        return {"error": errs}
    have = e.setdefault("sources", [])
    # de-duplicate on citation text so a re-run does not double up
    seen = {str(s.get("citation", "")).strip() for s in have}
    added, skipped = 0, 0
    for r in records:
        key = str(r["citation"]).strip()
        if key in seen:
            skipped += 1
            continue
        have.append(r)
        seen.add(key)
        added += 1
    if e["id"] in THESIS:
        return {"error": f"{entry_id} is marked thesis - it takes no citation"}
    e["provenance"] = "sourced" if have else ""
    return {"added": added, "skipped_duplicate": skipped,
            "with_locator": sum(1 for s in have if has_locator(s)),
            "total": len(have)}


def report(d) -> dict:
    e = d["entries"]
    thesis = [x for x in e if x.get("provenance") == "thesis"]
    sourced = [x for x in e if x.get("provenance") == "sourced"]
    todo = [x for x in e if not x.get("provenance")]
    allrec = [s for x in e for s in (x.get("sources") or [])]
    # "sourced" here counts entries carrying at least one record, which is what
    # provenance means. It is NOT a claim that those records are all locatable,
    # and the two numbers below are why that distinction matters: 140 entries are
    # counted as sourced while 94 records in that set claim to be openable and
    # are not. tools/citation_audit.py tracks that gap.
    unopenable = sum(1 for s in allrec
                     if s.get("status") in ("retrievable", "verified")
                     and not has_locator(s))
    return {
        "entries": len(e),
        "thesis (our own framework, not a gap)": len(thesis),
        "sourced": len(sourced),
        "still needing a source": len(todo),
        "source records": len(allrec),
        "records with a locator": sum(1 for s in allrec if has_locator(s)),
        "claiming openable but has no url": unopenable,
    }


if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "report":
        for k, v in report(load()).items():
            print(f"  {k:44} {v}")
    else:
        d = load()
        print(" ", apply_provenance(d))
        save(d)
        for k, v in report(d).items():
            print(f"  {k:44} {v}")
