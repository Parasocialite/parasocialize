"""What the twice-daily curation will put on the front page, and whether it
is doing what it claims.

`build_cards.pick_top` moves a section's tile on a schedule rather than
leaving the highest-`res` card up indefinitely. That is a claim about future
builds, which no single build can demonstrate, so this walks the slot ladder
instead: for each section it prints the pool, today's pick, and every pick
over the next N slots.

Two things are checked and can fail:

  1. a pool of more than one must actually produce more than one story. A
     pool of one is legitimate - the freshness gate suppressing a card too
     far behind the section's newest - and is reported rather than failed;
  2. no tile may reach back more than MAX_REACH days behind its own
     section's newest card while a newer card exists to show. MAX_REACH is
     deliberately not read out of build_cards - see the comment on it.

Usage:
    python tools/curate.py            # report
    python tools/curate.py --check    # report, exit 1 on a failure
"""
import datetime
import importlib.util
import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

SLOTS = 14  # one week, twice a day

# The expectation lives here, not in build_cards. Reading the module's own
# ROTATE_FRESH_DAYS as this check's threshold makes the check unfalsifiable:
# raising the constant raises the test with it, and mutation testing
# confirmed that the freshness failure could not be provoked at any value.
# Two independent claims is the point - if somebody widens the gate, this
# number is what says so.
MAX_REACH = 21


def load():
    spec = importlib.util.spec_from_file_location(
        "build_cards", ROOT / "tools" / "build_cards.py")
    bc = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(bc)
    data = json.loads((ROOT / "data" / "shop.json").read_text(encoding="utf-8"))
    return bc, data


def main(argv):
    check = "--check" in argv
    bc, data = load()
    cards, sections = data["cards"], data["sections"]
    feat = json.loads((ROOT / "data" / "features.json").read_text(encoding="utf-8"))

    start = datetime.datetime.now(datetime.timezone.utc)
    slots = [start + datetime.timedelta(hours=12 * i) for i in range(SLOTS)]
    today = start.date()

    print(f"curation slots: {SLOTS} over one week from "
          f"{start.strftime('%Y-%m-%d %H:%M')} UTC")
    print(f"today is slot {bc.cur_slot(start)}")
    print(f"top-8 list on show: {bc.pick_list(feat)['title']}")
    print()

    head = f"{'section':11s} {'cards':>5s} {'pool':>4s} {'now':>4s}  " \
           f"{'moves':>5s}  tile today"
    print(head)
    print("-" * len(head))

    failures = []
    held = []
    for sec in sections:
        sid = sec["id"]
        mine = [c for c in cards if c["section"] == sid]
        if not mine:
            continue
        pools = [len(bc.section_pool(cards, sid, now=n)) for n in slots]
        picks = [bc.pick_top(cards, sid, now=n) for n in slots]
        picks = [p for p in picks if p]
        if not picks:
            continue
        uniq = {p["slug"] for p in picks}
        here = bc.pick_top(cards, sid, now=start)
        age = (today - datetime.date.fromisoformat(here["filed"][:10])).days
        widest = max(pools)

        print(f"{sid:11s} {len(mine):5d} {widest:4d} {age:4d}  "
              f"{len(uniq):5d}  {here['headline'][:52]}")

        if widest > 1 and len(uniq) < 2:
            failures.append(f"{sid}: pool reaches {widest} but only "
                            f"{len(uniq)} story ever shows")
        elif widest < 2 and len(mine) > 1:
            held.append(f"{sid}: pool of {widest} out of {len(mine)} cards "
                        f"(freshness gate)")

        if len(mine) > 1:
            newest = max(datetime.date.fromisoformat(c["filed"][:10])
                         for c in mine)
            for p in picks:
                behind = (newest
                          - datetime.date.fromisoformat(p["filed"][:10])).days
                if behind > MAX_REACH:
                    failures.append(
                        f"{sid}: tile shows a card {behind}d behind the "
                        f"section's newest (expect {MAX_REACH}, build gate "
                        f"{bc.ROTATE_FRESH_DAYS})")
                    break

    print("-" * len(head))
    print(f"build gate reaches {bc.ROTATE_FRESH_DAYS} days behind the "
          f"section's newest; this check expects no more than {MAX_REACH}")

    if held:
        print("\nheld by the freshness gate (reported, not failed):")
        for h in held:
            print("   ", h)

    if failures:
        print("\nFAILURES:")
        for f in failures:
            print("  RED", f)
        if check:
            return 1
    elif check:
        print("\nOK: every multi-card pool rotates and no tile reaches past "
              "the freshness gate")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
