"""verify_landmarks.py - entry headings and contents rails must agree.

The first version of this check tested `id =~ /[a-z0-9]-[a-z]*$/`, which matches
every id in existence and reported 29 "cut mid-word" failures on correct data -
a gate crying wolf, which this project treats as worse than no gate. It happened
to be pointing at two REAL bugs inside the noise, which is the usual bargain:
a bad signal that still contained a true one.

So this version tests the property rather than the shape. Each heading carries
its own label, and the id must be exactly the slug of that label. If a slug was
truncated, entity-encoded or hand-edited, the two disagree and it is caught. No
heuristic, nothing to tune.
"""
import collections, pathlib, re, sys, html

ROOT = pathlib.Path(__file__).resolve().parent.parent
DIST = ROOT / "dist" / "encyclopedia"

RAIL = re.compile(r'<nav class="ent-toc".*?</nav>', re.S)
H2 = re.compile(r'<h2 class="ent-h" id="([^"]+)">(.*?)</h2>', re.S)
LINK = re.compile(r'href="#([^"]+)"')


def slug(text, limit=60):
    """The same rule build_cards._slug uses. Duplicated deliberately: a check that
    imports the code under test cannot catch that code being wrong."""
    s = re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")
    if len(s) <= limit:
        return s or "s"
    cut = s.rfind("-", 0, limit + 1)
    return (s[:cut] if cut > 0 else s[:limit]) or "s"


def main():
    if not DIST.exists():
        sys.exit(f"refusing: {DIST} does not exist. Run build_deploy.py first.")
    pages = sorted(p for p in DIST.glob("*.html") if p.name != "index.html")
    if not pages:
        sys.exit("refusing: found 0 entry pages")

    bad = 0
    with_heads = with_rail = total_h2 = 0
    for p in pages:
        t = p.read_text(encoding="utf-8", errors="replace")
        h2 = H2.findall(t)
        if h2:
            with_heads += 1
        total_h2 += len(h2)
        ids = []
        for hid, label in h2:
            label = html.unescape(re.sub(r"<[^>]+>", "", label)).strip()
            ids.append(hid)
            want = slug(label)
            if hid != want:
                bad += 1
                print(f"  FAIL {p.name}: id {hid!r} is not the slug of its own "
                      f"label {label[:50]!r} (expected {want!r})")
        for hid, c in collections.Counter(ids).items():
            if c > 1:
                bad += 1
                print(f"  FAIL {p.name}: duplicate heading id {hid!r} x{c}")
        rail = RAIL.search(t)
        if rail:
            with_rail += 1
            links = LINK.findall(rail.group(0))
            unresolved = [l for l in links if l not in ids]
            unlinked = [i for i in ids if i not in links]
            if unresolved:
                bad += 1
                print(f"  FAIL {p.name}: rail links to nothing: {unresolved}")
            if unlinked:
                bad += 1
                print(f"  FAIL {p.name}: headings missing from the rail: {unlinked}")
            if len(ids) < 3:
                bad += 1
                print(f"  FAIL {p.name}: a rail for {len(ids)} headings. Two "
                      f"links in a list is a menu, not a table of contents.")
        elif len(h2) >= 3:
            bad += 1
            print(f"  FAIL {p.name}: {len(h2)} headings and no contents rail")

    print(f"entry pages {len(pages)}   with headings {with_heads}   "
          f"with a rail {with_rail}   headings {total_h2}")
    print("ok" if not bad else f"{bad} problem(s)")
    return 1 if bad else 0


if __name__ == "__main__":
    raise SystemExit(main())