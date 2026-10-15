"""verify_findable.py - can a reader find an entry by the name they know it by?

WHY THIS EXISTS
The encyclopedia index has had a search box for a long time, and it searched
`title + summary + era`. Both of those are written the way they are on purpose:
they describe the *phenomenon* and refuse to name the *subject*. Measured
before this gate existed, **43 of 227 entries could not be found by any word of
their own name**:

    nancy-drew     "Fifty-four years of letters to a fictional detective"
    siri           "A voice assistant on every phone, addressing the user by name"
    dorian-gray    never says Dorian Gray
    superman-comic "A character who cannot die, printed in a newspaper"
    harvey, casper, alf, deadpool, charlie-chaplin, mary-pickford, siri,
    superman-comic, tony-stark, mona-lisa-theft, rudolph-valentino, fight-club,
    howdy-doody, gobekli-tepe, lugosi-burial, vtuber, shrlu, fight-club ...

That is good writing. It is also why a reader who knows who Nancy Drew is, and
types "nancy drew", gets nothing back. An encyclopedia that cannot be searched
by name is not an encyclopedia, and no gate here could see it: `link_audit`
checks that links resolve, not that they can be found, and the page was green.

THE FIX
The entry `id` IS the common name - `nancy-drew`, `dorian-gray`, `siri`. It goes
into the search index and nowhere else. It is deliberately NEVER printed: an
identifier shown to a reader reads as a citation, which is the trap AGENTS
records about `ANCHORED - HORTON-WOHL-1956`. A search index is not a page.

WHAT THIS CANNOT DO
It proves the words are IN the haystack. It does not prove the page ranks them
usefully, that the summary reads well, or that a reader who does not know the
name will find the right entry. It is a floor, not a search engine.
"""
import json, pathlib, re, sys, html

# `tools/verify_findable.py` -> parent is tools/, parent.parent is the repo.
# The first version used parent.parent.parent and died on a file that exists and
# reads fine from the shell, which is AGENTS item 53 exactly: a plausible path
# in an editor is not evidence the path is right.
ROOT = pathlib.Path(__file__).resolve().parent.parent
PAGE = ROOT / "dist" / "encyclopedia" / "index.html"

sys.stdout.reconfigure(encoding="utf-8")

# Read the id out of each row's own href. Pairing rows to entries positionally
# needs the generator's sort order, and re-deriving it is how the first version
# of this check reported 167 missing - including margery-kempe, whose title IS
# "Margery Kempe". The row carries its own identity; read that.
#
# The rows are split apart FIRST and each chunk parsed on its own. A single
# regex with `.*?` between the two <td>s will happily span a `</tr><tr>` and
# pair one row's haystack with another row's title - which is exactly what it
# did during the red test, reporting the neanderthal haystack for nancy-drew.
HAY = re.compile(r'data-hay="([^"]*)"')
IDENT = re.compile(r'<a href="[^"]*/encyclopedia/([^".]+)\.html">')


def rows_of(page):
    out = []
    for chunk in page.split("<tr ")[1:]:
        h = HAY.search(chunk)
        i = IDENT.search(chunk)
        if h and i:
            out.append((i.group(1), html.unescape(h.group(1)).lower()))
    return out


def main():
    enc = json.loads((ROOT / "data" / "encyclopedia.json").read_text(encoding="utf-8"))
    titles = {e["id"]: e.get("title", "") for e in enc["entries"]}

    if not PAGE.exists():
        sys.exit(f"refusing: {PAGE} does not exist. Run build_deploy.py first - "
                 f"this gate reads the built tree, because the built tree is "
                 f"what a reader gets.")
    page = PAGE.read_text(encoding="utf-8")
    rows = rows_of(page)

    if not rows:
        sys.exit("refusing: parsed 0 rows. The markup changed shape, and "
                 "reporting 'every entry is findable' from a check that read "
                 "nothing is exactly how this project ships a falsehood.")

    bad = 0
    if len(rows) != len(enc["entries"]):
        bad += 1
        print(f"  FAIL  {len(rows)} rows on the page, {len(enc['entries'])} in "
              f"the corpus. A reader sees a different number than the data holds.")

    miss = []
    for eid, hay in rows:
        toks = [w for w in re.split(r"[^a-z0-9]+", eid.lower()) if len(w) > 2]
        if toks and not any(t in hay for t in toks):
            miss.append((eid, titles.get(eid, "?")))

    print()
    print(f"findable: {len(rows) - len(miss)} / {len(rows)} entries answer to "
          f"a word of their own name")
    if miss:
        bad += 1
        print(f"  FAIL  {len(miss)} entry/entries a reader cannot look up by name:")
        for eid, t in miss:
            print(f"    {eid:28} -> {t!r}")

    # The two axes that were invisible on this page. A chip row that renders but
    # filters nothing is the "a filter that has nothing to filter still works"
    # failure, so check the attribute is actually on the rows.
    pla = json.loads((ROOT / "data" / "taxonomy_placements.json")
                     .read_text(encoding="utf-8"))["assignments"]
    tax = json.loads((ROOT / "data" / "taxonomy.json").read_text(encoding="utf-8"))
    for key, axis in (("data-other", "otherness"), ("data-rec", "reciprocity")):
        want = sum(1 for v in pla.values() if v.get(key.split("-")[1]))
        if not want:
            print(f"  note  no entry carries {key[5:]} - the axis is empty, so "
                  f"there is nothing to filter and that is a hole, not a bug")
            continue
        if key not in page:
            bad += 1
            print(f"  FAIL  {axis}: {want} entries are placed but the index "
                  f"carries no {key}, so a reader cannot reach any of them")
        else:
            print(f"  {axis}: {want} entries placed and filterable")

    print()
    bad += _register_check(dict(rows))

    print("ok" if not bad else f"{bad} problem(s).")
    return 1 if bad else 0


def _register_check(hay):
    """Every register named in a placement reason must be searchable.

    AGENTS item 45 records "there is no way for a reader to find the entries on
    a register", and item 35 rules out the fix everybody reaches for - a
    `register` field - because a field nothing counts is the family of defect
    this project exists to avoid.

    **Both were wrong, and measuring them is what showed it.** The register
    information was already written: 86 placement reasons name one, `bond` in
    26 and `contest` in 28, and `dear-kitty`'s reads "the purest instance of an
    undemanded tie on this site". All eight registers were named in prose and
    reachable from no search box, along with 59 backticked keys including
    `idol`, `made`, `haunted` and `simulated` - keys the author put in backticks
    precisely so somebody could look them up.

    So the axis never needed a field. It needed the sentence that already says
    it to be indexed, which is what `build_cards._hay()` now does. The check is
    the SET rather than the count: a search can return the right number for the
    wrong reasons - `cog` matched 3 entries before this, on the ordinary
    English word - so what is asserted is that every entry naming a register is
    inside the results for it.
    """
    pla = json.loads((ROOT / "data" / "taxonomy_placements.json")
                     .read_text(encoding="utf-8"))["assignments"]
    tax = json.loads((ROOT / "data" / "taxonomy.json").read_text(encoding="utf-8"))
    regs = [r["id"] for r in tax.get("register", []) if isinstance(r, dict)]
    if not regs:
        print("  note no registers defined; nothing to check")
        return 0

    def search(term):
        t = term.lower()
        return {eid for eid, h in hay.items() if t in h}

    bad = 0
    total_named = 0
    for reg in regs:
        named = {e for e, v in pla.items()
                 if reg in str(v.get("why", "")).lower()}
        total_named += len(named)
        missing = sorted(named - search(reg))
        if missing:
            bad += 1
            print(f"  FAIL register {reg!r} is named by {len(named)} placement "
                  f"reason(s) but {len(missing)} of those entries are not "
                  f"searchable by it: {missing[:5]}")
    if not bad:
        print(f"  all {len(regs)} registers searchable; "
              f"{total_named} placement reasons name one")

    # the backticked keys. The author marks them so they can be looked up, so a
    # key nobody can find is a promise the page does not keep.
    keys = set()
    for v in pla.values():
        for k in re.findall(r"`([^`\n]{1,60})`", str(v.get("why", ""))):
            keys.add(k.strip())
    lost = sorted(k for k in keys if not search(k))
    if lost:
        bad += 1
        print(f"  FAIL {len(lost)} of {len(keys)} backticked key(s) in the "
              f"placement reasons are not searchable: {lost[:8]}")
    else:
        print(f"  all {len(keys)} backticked keys searchable")
    return bad


if __name__ == "__main__":
    raise SystemExit(main())
