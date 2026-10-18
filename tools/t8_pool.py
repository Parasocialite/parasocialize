"""The Top 8 lists: the newest `released` is on show, former lists are kept.

Lists are released whole. The show is the list with the newest `released`
date that is not in the future - chosen by `build_cards.pick_list`, the one
selector the front page and /top8/ both use - and former lists stay in
`data/features.json` for the archive rather than being edited in place.
**8 is a motif**: a list that ships carries exactly eight entries, and
build_cards.py refuses to build a show with fewer.

An entry's stage records where that entry is in its list's life:

    candidate   drafted, not yet shipped
    featured    shipped with the list it sits in
    placed      has since been surfaced in a "way it shows up" shelf
    archived    has had its run; kept as history, never deleted

    tools\\t8_pool.py                     the show list by stage
    tools\\t8_pool.py --stage <id> <stage>
    tools\\t8_pool.py --promote [n]       move n candidates into featured
    tools\\t8_pool.py --place <id> <shelf> record where it landed
    tools\\t8_pool.py --archive <id>

`featured` is deliberately UNBOUNDED and SLOTS=8 is deliberately not enforced
here. Those two were fighting each other and the cap won: `--promote` refused
past eight, and `build_cards.py` picks its eight out of `featured` only when
there are MORE than eight - so with a cap in place the rotation branch was
unreachable and the front page showed the same eight moments every day for as
long as the cap held. The invariant that matters is **the page carries eight**,
and that is asserted where the page is built, in `build_cards.py`, where it can
be tested. A pool manager that refuses to hold more than the page shows is a
pool manager that has removed the rotation it exists to manage.
"""
import json, pathlib, re, sys

ROOT = pathlib.Path(__file__).resolve().parent
DATA = ROOT.parent / "data" / "features.json"
sys.path.insert(0, str(ROOT))
import build_cards as bc  # noqa: E402  (the shared list selector lives there)
sys.stdout.reconfigure(encoding="utf-8")

STAGES = ("candidate", "featured", "placed", "archived")
SLOTS = 8


def load():
    d = json.loads(DATA.read_text(encoding="utf-8"))
    return d, bc.pick_list(d)


def save(d, before_keys, before_slug, before_n):
    assert sorted(d) == before_keys, "top-level keys moved"
    L = next(x for x in d["lists"] if x["slug"] == before_slug)
    assert len(L["entries"]) == before_n, "entry count moved"
    DATA.write_text(json.dumps(d, ensure_ascii=False, indent=1) + "\n",
                    encoding="utf-8")


def eid(e):
    return e.get("id") or e.get("image") or e.get("show", "?")


def report(L):
    pool = L["entries"]
    by = {s: [e for e in pool if e.get("stage", "featured") == s]
          for s in STAGES}
    print(f"list: {L['slug']} "
          f"(released {L.get('released') or 'undated, sorts oldest'})\n")
    print(f"pool: {len(pool)} moment(s)\n")
    for s in STAGES:
        n = len(by[s])
        mark = "  <-- the eight on the page" if s == "featured" else ""
        print(f"  {s:<10} {n}{mark}")
        for e in by[s]:
            print(f"      {e.get('rank','-'):>2}. {e.get('show','?')[:34]:<36}"
                  f" {e.get('name','')[:44]}")
    if len(by["featured"]) != SLOTS:
        print(f"\n  NOTE: {len(by['featured'])} featured, page shows {SLOTS}. "
              f"Rotation only starts changing the page above {SLOTS}.")
    return by


def find(pool, ident):
    for e in pool:
        if eid(e) == ident or ident in (e.get("show", "") + e.get("name", "")):
            return e
    return None


def main():
    argv = sys.argv[1:]
    d, L = load()
    keys, slug, n = sorted(d), L["slug"], len(L["entries"])
    pool = L["entries"]

    if not argv or argv[0] in ("--list", "list"):
        by = report(L)
        return 0

    cmd = argv[0]

    if cmd == "--stage" and len(argv) >= 3:
        e = find(pool, argv[1])
        if not e:
            sys.exit(f"no moment matching {argv[1]!r}")
        if argv[2] not in STAGES:
            sys.exit(f"stage must be one of {STAGES}")
        was = e.get("stage", "featured")
        # No cap. See the module docstring: capping featured at SLOTS made the
        # rotation branch in build_cards.py unreachable.
        e["stage"] = argv[2]
        save(d, keys, slug, n)
        print(f"{eid(e)}: {was} -> {argv[2]}")
        return 0

    if cmd == "--promote":
        want = int(argv[1]) if len(argv) > 1 else 1
        cands = [e for e in pool if e.get("stage", "featured") == "candidate"]
        if not cands:
            print(f"no candidates in {slug}. add one to that list in "
                  f"features.json with \"stage\": \"candidate\"")
            return 1
        live = [e for e in pool if e.get("stage", "featured") == "featured"]
        # No cap on the pool. See the module docstring.
        take = cands[:want]
        for e in take:
            e["stage"] = "featured"
        save(d, keys, slug, n)
        for e in take:
            print(f"promoted: {eid(e)}  {e.get('show','')}")
        print(f"featured pool now {len(live) + len(take)} "
              f"(page shows {SLOTS})")
        return 0

    if cmd == "--place" and len(argv) >= 3:
        e = find(pool, argv[1])
        if not e:
            sys.exit(f"no moment matching {argv[1]!r}")
        e["shelf"] = argv[2]
        e["stage"] = "placed"
        save(d, keys, slug, n)
        print(f"{eid(e)}: placed -> {argv[2]}")
        return 0

    if cmd == "--archive" and len(argv) >= 2:
        e = find(pool, argv[1])
        if not e:
            sys.exit(f"no moment matching {argv[1]!r}")
        if e.get("stage", "featured") == "featured":
            live = [x for x in pool if x is not e
                    and x.get("stage", "featured") == "featured"]
            if not live:
                sys.exit(f"refusing: that is the only featured moment; the "
                         f"page must always show {SLOTS}.")
        e["stage"] = "archived"
        save(d, keys, slug, n)
        print(f"{eid(e)}: archived (kept, not deleted)")
        return 0

    sys.exit("usage: t8_pool.py [--list | --stage <id> <stage> | "
             "--promote [n] | --place <id> <shelf> | --archive <id>]")


if __name__ == "__main__":
    raise SystemExit(main())