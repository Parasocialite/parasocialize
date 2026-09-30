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
}


def validate(rec: dict, where: str) -> list[str]:
    errs = []
    if not str(rec.get("citation") or "").strip():
        errs.append(f"{where}: citation text is empty")
    if rec.get("status") not in VALID_STATUS:
        errs.append(f"{where}: status {rec.get('status')!r} not in {sorted(VALID_STATUS)}")
    if not str(rec.get("claim") or "").strip():
        errs.append(f"{where}: claim is empty")
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
    return {
        "entries": len(e),
        "thesis (our own framework, not a gap)": len(thesis),
        "sourced": len(sourced),
        "still needing a source": len(todo),
        "source records": len(allrec),
        "records with a locator": sum(1 for s in allrec if has_locator(s)),
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
