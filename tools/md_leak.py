r"""md_leak.py - is authored markdown reaching the deployed pages as source?

WHY THIS EXISTS
`build_cards.py` had no inline-formatting path at all, so `**bold**` written in
the corpus arrived on the page as literal asterisks: **709 occurrences across 52
deployed pages**, 43 entries and 7 placement reasons. The same field also used
blank-line paragraph breaks that collapsed to a space, so 33 entries - including
the 2,640-word `american-gothic` - ran as one unbroken wall. It was found by
reading an entry page, not by any gate: `link_audit` checks that links resolve
and says nothing about whether the prose is rendered.

`emph()` and `prose()` in build_cards.py fix that, and this holds it.

WHAT IT WILL AND WILL NOT CATCH
- It fails on a published page carrying `**`. That is the reader-facing defect.
- It REPORTS but does not fail on `/desk/`, because that page is the signoff
  queue and a draft nobody has signed is raw by design. There is currently one:
  an unbalanced `**` with no closing pair, which `emph()` correctly refuses to
  guess at. Rendering it literally is the desk doing its job - it is visible
  evidence the card is not ready to sign - so it is not a renderer defect and
  the gate must not go permanently red over it.
- It counts `code \`` and `italic *` and reports them, but does NOT fail. Those
  are the same class of defect and both are currently unfixed: 468 backticks,
  412 of them on /taxonomy/, where the author marks taxonomy keys as `persona/idol`.
  Rendering those as <code> restyles that whole page, so it is an editorial
  decision rather than a lint fix, and it is reported until somebody decides.

Usage: python tools/md_leak.py
"""
import collections, pathlib, re, sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
DIST = ROOT / "dist"

PATTERNS = {
    "bold **": re.compile(r"\*\*"),
    "code `": re.compile(r"`[^`\n]{1,60}`"),
    "italic *": re.compile(r"(?<![\w*])\*[^*\n]{2,60}\*(?![\w*])"),
}

# The signoff queue is unpublished by construction.
UNPUBLISHED = re.compile(r"^desk/")


def main():
    if not DIST.exists():
        sys.exit(f"refusing: {DIST} does not exist. Run build_deploy.py first.")
    pages = sorted(DIST.rglob("*.html"))
    if not pages:
        sys.exit("refusing: found 0 html pages in dist/. A zero here is a "
                 "broken path, not a finding.")

    clean = [re.sub(r"<(script|style)\b[^>]*>.*?</\1>", " ",
                    p.read_text(encoding="utf-8", errors="replace"),
                    flags=re.S | re.I) for p in pages]

    published, draft = [], []
    for p, c in zip(pages, clean):
        rel = p.relative_to(DIST).as_posix()
        (draft if UNPUBLISHED.match(rel) else published).append((rel, c))

    print(f"markdown audit: {len(published)} published pages, {len(draft)} unpublished\n")

    fails = 0
    for name, pat in PATTERNS.items():
        hits = [(len(pat.findall(c)), rel) for rel, c in published]
        hits = [(n, r) for n, r in hits if n]
        nhits = [(len(pat.findall(c)), rel) for rel, c in draft]
        nhits = [(n, r) for n, r in nhits if n]
        print(f"{name:<10} published: {sum(n for n, _ in hits):>4} in {len(hits):>3} page(s)"
              f"   unpublished: {sum(n for n, _ in nhits):>4} in {len(nhits)} page(s)")
        for n, rel in sorted(hits, reverse=True)[:6]:
            print(f"            {n:>4}x  {rel}")
        for n, rel in sorted(nhits, reverse=True)[:3]:
            print(f"      draft {n:>4}x  {rel}")
        if hits and name == "bold **":
            fails += len(hits)

    print()
    if "code `" in PATTERNS and sum(
            len(PATTERNS["code `"].findall(c)) for _, c in published):
        print("note: backticks are still unrendered. Same defect class, "
              "unfixed on purpose - see the module docstring.")

    if fails:
        print(f"FAIL literal '**' reaches {fails} published page(s). Emphasis "
              f"must render; emph() is applied per prose field, not inside "
              f"esc(), so a field rendered by a path that still calls esc() "
              f"will show this.")
        return 1
    print("ok - no literal ** reaches any published page")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())