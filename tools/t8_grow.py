"""Add authored moments to a top-8 list's pool, interleaved among the originals.

The pool is what the daily window moves over: `build_cards.top8_window()` takes
a list's `featured` entries in file order and slides an eight-wide window
across them, starting at `(day * 8) % n`. So the position of a new moment in
the pool is a rendering decision, not bookkeeping. Appended wholesale, a pool
grown eight-over-eight would hand the window one whole day of the new entries
and one whole day of the old - and because some moments have photographs and
some do not, that is a day with no photographs on the page at all. New moments
are therefore inserted *among* the old ones, as evenly as the counts allow, so
every day's eight mixes old and new the way the list was always meant to.

    tools\\t8_grow.py <batch.json>            check, print what would change
    tools\\t8_grow.py <batch.json> --apply    write

The batch is `{"list": "<slug>", "entries": [...]}`. Every entry is checked
before anything is written, because this edits a tracked corpus file: the
required keys (name, show, what, why, law), no unknown keys (the typo guard),
`law` present in data/shop.json, and identity against every entry of every
list - a new moment has no image, so its eid is its `show` line, which must
not collide with another moment's identity anywhere. Names must be unique
within the list. Counts and top-level keys are asserted before and after, and
the file is written at its own format (indent=1, ensure_ascii=False, trailing
newline).
"""
import json, pathlib, sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
FEATURES = ROOT / "data" / "features.json"
SHOP = ROOT / "data" / "shop.json"

REQUIRED = ("name", "show", "what", "why", "law")
ALLOWED = set(REQUIRED) | {"stage"}
sys.stdout.reconfigure(encoding="utf-8")


def eid(en):
    return en.get("id") or en.get("image") or en.get("show", "?")


def interleave(old, new):
    """Insert new[j] after old[floor(j * len(old) / len(new))].

    For eight over eight this gives o0,n0,o1,n1,... so both eight-wide windows
    carry four photographs; for a smaller batch it spreads the new moments as
    widely as their count allows. Order of the old entries never changes.
    """
    if not old:
        return list(new)
    nold, nnew = len(old), len(new)
    out, j = [], 0
    for i, en in enumerate(old):
        out.append(en)
        while j < nnew and (j * nold) // nnew == i:
            out.append(new[j])
            j += 1
    if j != nnew:
        raise SystemExit(f"interleave placed {j} of {nnew} new moments")
    return out


def main():
    argv = [a for a in sys.argv[1:]]
    apply = "--apply" in argv
    argv = [a for a in argv if a != "--apply"]
    if len(argv) != 1:
        sys.exit("usage: t8_grow.py <batch.json> [--apply]")
    batch_path = pathlib.Path(argv[0])
    if not batch_path.is_file():
        sys.exit(f"no batch file at {batch_path}")

    data = json.loads(FEATURES.read_text(encoding="utf-8"))
    shop = json.loads(SHOP.read_text(encoding="utf-8"))
    laws = {l["n"] for l in shop["laws"]}

    batch = json.loads(batch_path.read_text(encoding="utf-8"))
    if not isinstance(batch, dict) or set(batch) != {"list", "entries"}:
        sys.exit('batch must be {"list": <slug>, "entries": [...]}')
    slug, new = batch["list"], batch["entries"]
    if not isinstance(new, list) or not new:
        sys.exit("batch carries no entries")

    L = next((x for x in data["lists"] if x["slug"] == slug), None)
    if L is None:
        sys.exit(f"no list with slug {slug!r}")

    for n, en in enumerate(new, 1):
        unknown = set(en) - ALLOWED
        if unknown:
            sys.exit(f"entry {n}: unknown key(s) {sorted(unknown)}; "
                     f"allowed: {sorted(ALLOWED)}")
        missing = [k for k in REQUIRED if not en.get(k)]
        if missing:
            sys.exit(f"entry {n}: missing {missing}")
        if not isinstance(en["law"], int) or en["law"] not in laws:
            sys.exit(f"entry {n}: law {en['law']!r} is not one of {sorted(laws)}")
        if en.get("stage", "featured") != "featured":
            sys.exit(f"entry {n}: stage {en['stage']!r} - a new moment "
                     f"arrives featured")

    seen_eid = {}
    for other in data["lists"]:
        for en in other["entries"]:
            seen_eid.setdefault(eid(en), f"list {other['slug']}")
    for n, en in enumerate(new, 1):
        if eid(en) in seen_eid:
            sys.exit(f"entry {n}: identity {eid(en)!r} already exists "
                     f"({seen_eid[eid(en)]})")
        seen_eid[eid(en)] = f"this batch, entry {n}"
    names = {en["name"] for en in L["entries"]}
    for n, en in enumerate(new, 1):
        if en["name"] in names:
            sys.exit(f"entry {n}: name {en['name']!r} already on {slug}")
        names.add(en["name"])

    before_keys, before_n = sorted(data), len(L["entries"])
    added = [{k: en[k] for k in REQUIRED}
             | ({"stage": "featured"} if "stage" in en else {})
             for en in new]
    merged = interleave(L["entries"], added)

    if len(merged) != before_n + len(added):
        sys.exit("merged count does not add up")

    print(f"list: {slug}")
    print(f"pool: {before_n} -> {len(merged)} moment(s)\n")
    new_ids = {id(en) for en in added}
    for i, en in enumerate(merged, 1):
        mark = "new " if id(en) in new_ids else "    "
        print(f"  {i:>3}. {mark}{en['name']}")
        print(f"       {en['show']}  (law {en['law']})")

    if not apply:
        print("\ndry run - nothing written; add --apply to keep this order")
        return 0

    L["entries"] = merged
    assert sorted(data) == before_keys, "top-level keys moved"
    assert len(L["entries"]) == before_n + len(added), "entry count moved"
    FEATURES.write_text(json.dumps(data, ensure_ascii=False, indent=1) + "\n",
                        encoding="utf-8")
    print(f"\nwrote {len(merged)} moments to {FEATURES.name}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
