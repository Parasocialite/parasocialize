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
- `code \`` and `italic *` were fixed the same way and are now zero on every
  published page. They were left unrendered for a while first - 468 backticks,
  412 of them on /taxonomy/, where the author marks taxonomy keys as
  `persona/idol`. The reason was that `<code>` had no stylesheet at all, so
  introducing the element without one would have dropped 412 keys into the
  browser's default monospace on the one page whose whole job is teaching the
  vocabulary. `css/styles.css` now styles `code` in `--label`, the face this
  site already uses whenever a machine speaks.
- **This gate found two of its own misses.** The first pass converted two of the
  four triad renderers on the taxonomy page, because two of them print the same
  line and a text search for `esc(m[key])` returned them as one match. The
  remaining 12 backticks were the tell. **A converter applied by search finds
  the sites you searched for, which is not the same as the sites that exist.**

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
        if hits:
            fails += len(hits)

    print()
    if fails:
        print(f"FAIL authored markdown reaches {fails} published page(s). "
              f"emph() is applied per prose field, not inside esc(), so a field "
              f"rendered by a path that still calls esc() shows up here - which "
              f"is how two of the four taxonomy triad renderers were missed the "
              f"first time.")
        return 1
    print("ok - no authored markdown reaches any published page")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())