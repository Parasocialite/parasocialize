"""Give every hand-rolled <head> the same feed and icon links.

Twelve pages were missing one or both feeds, and the reason was structural:
`build_cards.py` has eighteen hand-written `<head>` blocks alongside the `HEAD`
template, and a `<head>` that is written out longhand is a head that quietly
omits whatever the template grew last. `radar.xml` was in most of them by
accumulation; `ledger/feed.xml` is new and only appears where it was typed.

Patching twelve pages would have fixed twelve pages and left the eighteenth
longhand head free to forget the next thing added. So this inserts the links
into every hand-rolled head that lacks them, and the shared block is defined
once. Uniformity becomes the default rather than a thing to remember.

It only touches `<head>` blocks, asserts how many it changed, and writes the
file once at the end - and it is idempotent, because a head that already
carries `radar.xml` is skipped.
"""
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

P = ROOT / "tools" / "build_cards.py"
raw = P.read_text(encoding="utf-8")
lines = raw.split("\n")

BLOCK = [
    '<link rel="alternate" type="application/rss+xml" title="Parasocialize" '
    'href="{SITE}/radar.xml">',
    '<link rel="alternate" type="application/rss+xml" title="Parasocialize - '
    'the open ledger" href="{SITE}/ledger/feed.xml">',
    '<link rel="icon" type="image/svg+xml" href="{SITE}/favicon.svg">',
]

HEADS = re.compile(r"<head>", re.I)
# Matched on `<head>` alone. The first version required an `<html lang="en">`
# prefix and a lowercase charset, so it reached only half the pages: the rest
# open with a bare `<head><meta charset="UTF-8">` and were never considered at
# all. A regex written against the shape you happen to be looking at is a regex
# that misses the other half of the corpus - which is the same defect as
# `kind: exact` derived from a filename, one level up.
WIN = 22          # lines to look ahead for an existing feed link
dry = "--apply" not in sys.argv

changed, skipped = 0, 0
out = []
i = 0
while i < len(lines):
    ln = lines[i]
    out.append(ln)
    if HEADS.search(ln):
        # Look ahead in the SOURCE, past anything already inserted, so a head
        # that carries the links is skipped rather than given a second copy.
        # Skip only a head that already carries BOTH feeds. Testing for
        # radar.xml alone looked right and was not: most heads have carried
        # radar.xml since it was the only feed, so the check passed over
        # seventeen heads that were missing the new one. The run reported
        # "3 already carrying" and changed 17, and still left 11 pages without
        # ledger/feed.xml - the dist scan is what caught it, not the dry run.
        window = "\n".join(lines[i:i + WIN])
        if "ledger/feed.xml" in window and "radar.xml" in window:
            skipped += 1
        else:
            out.extend(BLOCK)
            changed += 1
            print(f"  line {i + 1}: head gained {len(BLOCK)} links")
        # skip past the block we just consumed so it is not re-examined
        i += 1
        while i < len(lines) and lines[i] in BLOCK:
            i += 1
        continue
    i += 1
lines = out

print()
print(f"heads already carrying the links: {skipped}")
print(f"heads that would gain them:       {changed}")
if dry:
    print("\ndry run. re-run with --apply to write.")
    sys.exit(0)

P.write_text("\n".join(lines), encoding="utf-8")
print("\nwritten.")
