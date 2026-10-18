"""expand.py - validate and place entries drafted into a work queue.

The research and writing are done by an agent; this is the half that has to be
right, because it touches a hand-maintained corpus and the mistakes it prevents
are the ones this repo has already paid for:

  - an entry that does not fit the shelf it claims. Each sub-category carries a
    `test` and a `not`, and `apply` refuses a candidate whose `fits` line is
    empty or unverified, because "move it in to make the distribution look even"
    is the move this project refuses.
  - a relation whose verb contradicts its dates. Seven wrong edges came from
    writing `preceded` because the sentence reads that way rather than because
    the numbers do, so `apply` refuses any chronological relation it cannot
    derive from the two years.
  - a source-less claim. An entry with no citation record reads as sourced to
    `is_sourced()`, which is how four unsourced claims about named living people
    got in. `apply` refuses to place an entry with no records at all.
  - a regenerated corpus file. `taxonomy.json` lost 4 categories and 19
    sub-categories once to a script that rewrote it from a template, and
    `encyclopedia.json` lost `_note`/`lanes`/`kinds` the same way. So every write
    asserts the top-level keys and the counts before and after, and refuses.

Nothing here publishes. An entry that passes lands with `verified: false` and
its records `needs-source`; promoting it is a separate, human decision.

    python tools\\expand.py --check data/expand-queue.json
    python tools\\expand.py --apply data/expand-queue.json
"""
import json, pathlib, re, sys, datetime

ROOT = pathlib.Path(__file__).resolve().parent.parent
ENC = ROOT / "data" / "encyclopedia.json"
TAX = ROOT / "data" / "taxonomy.json"
PLACES = ROOT / "data" / "taxonomy_placements.json"
sys.stdout.reconfigure(encoding="utf-8")

CHRONOLOGICAL = {"preceded", "succeeded"}
REQUIRED_ENTRY = ("id", "title", "year", "summary", "significance", "kind",
                  "medium", "provenance")


def shelf_parent(tax, sub_id):
    """The parent category of an attachment sub-category, read from the file."""
    stack = list(tax.get("attachment") or [])
    while stack:
        c = stack.pop()
        if not isinstance(c, dict):
            continue
        for s in (c.get("sub") or c.get("subcategories") or []):
            if isinstance(s, dict) and s.get("id") == sub_id:
                return c.get("id")
            stack.append(s)
    return None


def otherness_ids(tax):
    """The otherness members, which are a SEPARATE axis from attachment.

    `animate`, `mirrored` and `imagined` are otherness, not attachment shelves,
    and they live on the entry as `other` rather than in the placements file.
    The first batch queue put three entries on them and the shelf check caught
    it, which is the check earning its keep.
    """
    o = tax.get("otherness") or {}
    out = set()
    members = o.get("members") if isinstance(o, dict) else o
    for m in (members or []):
        if isinstance(m, dict) and m.get("id"):
            out.add(m["id"])
        elif isinstance(m, str):
            out.add(m)
    return out


def load(p):
    return json.loads(p.read_text(encoding="utf-8"))


def entries_of(d):
    return d["entries"] if isinstance(d, dict) and "entries" in d else d


def by_id(E):
    return {e.get("id"): e for e in E}


def shelf_tests(tax):
    """id -> (test, not) for every attachment sub-category."""
    out = {}
    cats = tax.get("attachment") or []
    stack = list(cats)
    while stack:
        c = stack.pop()
        if not isinstance(c, dict):
            continue
        if c.get("id"):
            out[c["id"]] = (c.get("test", ""), c.get("not", ""),
                            c.get("name", c["id"]))
        for s in (c.get("sub") or c.get("subcategories") or []):
            stack.append(s)
    return out


def validate(q, enc, tax):
    """Return (ok, problems) for one candidate. No writes."""
    problems = []
    E = entries_of(enc)
    have = by_id(E)
    shelves = shelf_tests(tax)

    for cand in q.get("entries", []):
        cid = cand.get("id", "<no id>")
        for k in REQUIRED_ENTRY:
            if not cand.get(k):
                problems.append(f"{cid}: missing required field {k!r}")
        if cid in have:
            problems.append(f"{cid}: already exists - expand adds, it does not "
                            f"rewrite")
        shelf = cand.get("shelf")
        if not shelf:
            problems.append(f"{cid}: no shelf given")
        elif shelf not in shelves:
            problems.append(f"{cid}: shelf {shelf!r} is not an attachment "
                            f"sub-category")
        else:
            test, nott, name = shelves[shelf]
            if not cand.get("fits"):
                problems.append(
                    f"{cid}: shelf {shelf!r} ({name}) has no `fits` line. The "
                    f"test is: {test[:120]!r} ... An entry that cannot say why "
                    f"it belongs is how a chart gets made to look even.")
            elif not cand.get("fits_verified"):
                problems.append(f"{cid}: `fits` must be set true by a human who "
                                f"read the shelf test and the `not`")
        # relations must agree with the years
        years = {have[r["to"]]["year"] for r in cand.get("relations", [])
                 if isinstance(r, dict) and r.get("to") in have}
        for r in cand.get("relations", []):
            if not isinstance(r, dict):
                problems.append(f"{cid}: relation is not an object")
                continue
            if r.get("type") in CHRONOLOGICAL:
                to = r.get("to")
                if to not in have:
                    problems.append(f"{cid}: relation points at unknown entry "
                                    f"{to!r}")
                    continue
                a, b = cand.get("year"), have[to].get("year")
                if isinstance(a, int) and isinstance(b, int):
                    if a == b:
                        problems.append(
                            f"{cid} -> {to}: both are {a}. Equal years silently "
                            f"became 'succeeded' in seven wrong edges; "
                            f"`contemporary` is the honest relation for a tie.")
                    else:
                        want = "preceded" if a < b else "succeeded"
                        if r["type"] != want:
                            problems.append(
                                f"{cid} ({a}) -> {to} ({b}): says "
                                f"{r['type']!r}, the years say {want!r}")
        # a claim with no citation record reads as sourced
        if not cand.get("sources") and cand.get("provenance") != "thesis":
            problems.append(
                f"{cid}: no sources and not provenance:thesis. `is_sourced()` "
                f"is `bool(sources)`, so this entry would render as standing "
                f"behind its claims.")
        # otherness is optional and is a different axis from the shelf
        o = cand.get("other")
        if o and o not in otherness_ids(tax):
            problems.append(f"{cid}: other={o!r} is not an otherness member "
                            f"(have: {sorted(otherness_ids(tax))})")
        # provenance must agree with whether records exist. This corpus has
        # exactly two values, `sourced` and `thesis`, and thesis means "takes no
        # citation at all - that is not a gap". So an entry carrying records
        # while claiming to be a thesis is claiming both. Seven were in that
        # state before this check existed.
        n_src = len(cand.get("sources") or [])
        prov = cand.get("provenance")
        if n_src and prov == "thesis":
            problems.append(
                f"{cid}: carries {n_src} citation record(s) but declares "
                f"provenance:thesis. Thesis entries take no citation at all. "
                f"Set provenance to 'sourced' - or drop the records if this "
                f"really is the site's own argument.")
        if not n_src and prov != "thesis":
            problems.append(f"{cid}: provenance={prov!r} but no citation "
                            f"records")
    return problems


def apply(q):
    enc, tax = load(ENC), load(TAX)
    problems = validate(q, enc, tax)
    if problems:
        print(f"REFUSING to apply. {len(problems)} problem(s):\n")
        for p in problems:
            print(f"  - {p}")
        return 1

    keys_before = sorted(enc) if isinstance(enc, dict) else None
    n_before = len(entries_of(enc))
    # data/taxonomy_placements.json is indented 2 while encyclopedia.json is
    # indented 1. Writing every corpus file at one space reformatted this file
    # whole once - a two-key change arrived as a two-thousand-line diff (item
    # 37 in AGENTS.md). Match what the committed file uses instead.
    places_text = PLACES.read_text(encoding="utf-8")
    places = json.loads(places_text)
    pindent = 2 if places_text.split("\n", 2)[1].startswith("  ") else 1
    pkeys = sorted(places)
    shelves = shelf_tests(tax)

    E = entries_of(enc)
    if isinstance(enc, dict):
        enc["entries"] = E
    added = 0
    for cand in q["entries"]:
        # nothing becomes `verified` by being written
        cand["verified"] = False
        cand.setdefault("sources", [])
        for rec in cand["sources"]:
            rec.setdefault("status", "needs-source")
        E.append(cand)
        shelf = cand["shelf"]
        a = places.setdefault("assignments", {})
        # The placement schema is `cat` / `sub` / `why`, NOT `attachment`.
        # Guessing the key names put four entries in with the wrong shape and
        # build_cards died on `KeyError: 'cat'` - the shape is only discoverable
        # by reading a committed sample, which is what this now does.
        if shelf not in shelves:
            sys.exit(f"{cand['id']}: shelf {shelf!r} vanished between check "
                     f"and apply")
        parent = shelf_parent(tax, shelf)
        # The placement reason is PRINTED on the page - it is not a commit
        # message. This used to fall back to "Added by tools/expand.py; review
        # the reason.", which is two defects in one string: it names a tool a
        # reader has never heard of, and it is a to-do rendered where an
        # argument should be. The same shape as claim: "the entry as a whole".
        # The candidate's own `fits` text IS the shelf-fit reasoning and reads
        # correctly here, so use it, and refuse if there is nothing.
        why = cand.get("placement_why") or cand.get("fits")
        if not why:
            sys.exit(f"{cand['id']}: needs placement_why or fits. The reason "
                     f"is printed on the page, so a to-do is not acceptable "
                     f"and an empty cell would render a blank.")
        placement = {"cat": parent, "sub": shelf, "why": why}
        # `other` is a placement field on the page: build_cards, ledger and
        # verify_taxonomy all read it from this file, and every `made` /
        # `haunted` entry carries it here. The death batch left it on the
        # entry only, where nothing counts it, so carry it across.
        if cand.get("other"):
            placement["other"] = cand["other"]
        a[cand["id"]] = placement
        added += 1

    assert len(entries_of(enc)) == n_before + added, "entry count wrong"
    if keys_before:
        assert sorted(enc) == keys_before, "encyclopedia top-level keys moved"
    assert sorted(places) == pkeys, "placements top-level keys moved"

    ENC.write_text(json.dumps(enc, ensure_ascii=False, indent=1) + "\n",
                   encoding="utf-8")
    PLACES.write_text(json.dumps(places, ensure_ascii=False, indent=pindent) + "\n",
                      encoding="utf-8")
    print(f"added {added} entry/entries. encyclopedia {n_before} -> "
          f"{n_before + added}. All land verified=false / needs-source.")
    print("promotion to live is a separate, human step.")
    return 0


def main():
    a = sys.argv[1:]
    path = None
    for i, x in enumerate(a):
        if x.endswith(".json"):
            path = pathlib.Path(x) if pathlib.Path(x).is_absolute() else ROOT / x
            break
    if not path or not path.is_file():
        sys.exit("usage: expand.py --check|--apply <queue.json>")
    q = load(path)
    if "--apply" in a:
        return apply(q)
    problems = validate(q, load(ENC), load(TAX))
    print(f"queue: {path.name}   {len(q.get('entries', []))} candidate(s)")
    if not problems:
        print("ok - every candidate passes. Nothing written by --check.")
        return 0
    print(f"\n{len(problems)} problem(s):\n")
    for p in problems:
        print(f"  - {p}")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())