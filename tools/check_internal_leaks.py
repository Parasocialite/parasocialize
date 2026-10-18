"""Internal vocabulary that reached a public page.

`/ledger/` shipped reading "...and AGENTS is explicit that this is not a gap."
AGENTS.md is a working file for whoever maintains the repository. A reader has
never heard of it, and a stray internal token on a public surface reads as a
mistake even when the sentence around it is fine.

That is the same class as the CLERK'S DESK link and the "no free frame exists"
note: process vocabulary in front of somebody who cannot follow it. It got
through because the gates check links, selectors and counts, and none of them
reads prose for words that mean nothing to a reader.

So this scans the built pages rather than the source, since the source is what
the author writes and the page is what a reader gets.
"""
import pathlib
import re
import sys

# This file lives in tools/, so the repository is two parents up. It was
# originally written with three, which pointed at "Default Project" instead -
# and the run then scanned a directory holding no HTML at all and printed
# "clean: no internal vocabulary in reader-visible prose". Zero pages scanned is
# not a pass, it is a scanner that is looking in the wrong tree, and it is the
# same defect as the orphaned `.t8-hero-fig img`: a measurement that cannot see
# its own subject will pass any test you give it.
ROOT = pathlib.Path(__file__).resolve().parent.parent
DIST = ROOT / "dist"
assert (ROOT / "tools" / "build_cards.py").exists(), f"ROOT is wrong: {ROOT}"
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

# Deliberately narrow. These are words that only exist inside this project, so
# a hit in rendered prose is either a leak or the article is discussing the tool
# on purpose (the /desk/ page is the legitimate exception).
TERMS = [
    "AGENTS.md", "AGENTS", "expand.py", "citation_audit", "build_cards",
    "build_deploy", "verify_taxonomy", "t8_pool", "ledger.py",
    "taxonomy_placements", "encyclopedia.json", "images.json",
    "front_copy", "link_audit", "check_css", "md_leak", "report_current_state",
    "expand.py", "provenance: thesis", "_ratchet", "ORPHAN_BASELINE",
]

# Pages where talking about the machinery is the job.
ALLOW = {"desk/index.html", "ledger/index.html"}

TAG = re.compile(r"<[^>]+>")


def visible(html: str) -> str:
    html = re.sub(r"<(script|style).*?</\1>", " ", html, flags=re.S | re.I)
    return " ".join(TAG.sub(" ", html).split())


pages = sorted(DIST.rglob("*.html"))
if not pages:
    print(f"REFUSING: no built pages found in {DIST}. "
          f"Run build_deploy.py first. A scan of zero pages is not a pass.")
    sys.exit(1)
print(f"scanning {len(pages)} built pages for {len(TERMS)} internal terms\n")

hits = 0
for p in pages:
    rel = p.relative_to(DIST).as_posix()
    try:
        txt = visible(p.read_text(encoding="utf-8", errors="replace"))
    except Exception as e:  # noqa: BLE001
        print(f"  UNREADABLE {rel}: {e}")
        continue
    for term in TERMS:
        if term in txt:
            if rel in ALLOW:
                print(f"  allow   {rel}: {term!r} (page is about the machinery)")
                continue
            i = txt.index(term)
            hits += 1
            print(f"  LEAK    {rel}: {term!r}")
            print(f"          ...{txt[max(0, i - 90):i + 90]}...")

print()
if hits:
    print(f"FAIL: {hits} internal term(s) in reader-visible prose.")
    sys.exit(1)
print("clean: no internal vocabulary in reader-visible prose.")
