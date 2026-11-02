# -*- coding: utf-8 -*-
"""Prove the copy rotation rotates, and that the generator picks it up.

This used to test a version that patched `index.html` in place. It was written
against a file that `build_cards.py` **regenerates on every run** - so the
masthead redesign and the ten rewritten teasers were both silently reverted by
the gate chain, with every gate green. A test that passes against a file the
build owns proves nothing.

Now the copy is data behind a pointer, and the test exercises the real path:
set the pointer, rebuild, grep the output, put it back, rebuild again.
"""
import html
import json
import pathlib
import re
import subprocess
import sys

sys.stdout.reconfigure(encoding="utf-8")
ROOT = pathlib.Path(__file__).resolve().parent.parent
DATA = ROOT / "data" / "front_copy.json"
PAGE = ROOT / "index.html"
sys.path.insert(0, str(ROOT / "tools"))
import build_cards as bc


def run(*args, tool="front_copy.py"):
    r = subprocess.run([sys.executable, "-X", "utf8", str(ROOT / "tools" / tool),
                        *args], capture_output=True, text=True, cwd=ROOT,
                       encoding="utf-8", errors="replace")
    if r.returncode != 0:
        sys.exit(f"FAIL: {tool} {' '.join(args)}\n{r.stdout}{r.stderr}")
    return r.stdout


def build():
    r = subprocess.run([sys.executable, "-X", "utf8",
                        str(ROOT / "tools" / "build_cards.py")],
                       capture_output=True, text=True, cwd=ROOT,
                       encoding="utf-8", errors="replace")
    if r.returncode != 0:
        sys.exit(f"FAIL: build_cards\n{r.stdout}{r.stderr}")


def page():
    return PAGE.read_text(encoding="utf-8")


def has(s):
    return s in page()


doc = json.loads(DATA.read_text(encoding="utf-8"))
seed = doc["_live"]
# Snapshot AFTER the first build, not before. Capturing it before meant the
# comparison at the end was against whatever happened to be on disk - so a page
# left in any unexpected state (a previous run that died mid-probe, say) made
# this test fail with "the page did not come back to where it started" while the
# teardown had in fact worked perfectly. That is a red gate about a green run.

# 1. the live edition reaches the generated page
build()
orig = PAGE.read_bytes()
# This used to assert `<div class="masthead-grid">` existed, which only checked
# that a class name was still in the file - it passed for any layout at all. The
# masthead is now one row holding the two doors AND the clerk, so assert that:
# pull the row out and check what is actually inside it. Renaming the assertion
# to the new class name would have kept the test exactly as blind as before.
doc_html = PAGE.read_text(encoding="utf-8")
if "ledger-band" in doc_html:
    sys.exit("FAIL: the open ledger band is back in the primary reader flow")
if ">Coffee</a>" in doc_html or "Buy me a coffee" in doc_html:
    sys.exit("FAIL: the old Coffee invitation is still on the front page")
if 'href="membership/index.html"' in doc_html:
    sys.exit("FAIL: the removed membership route is back on the front page")
if 'href="signal/latest.html"' in doc_html:
    sys.exit("FAIL: the removed Friday email route is back on the front page")
if 'signal-form' in doc_html:
    sys.exit("FAIL: the removed newsletter form is back on the front page")
if ('<a class="cta" href="https://ko-fi.com/parasocialing" target="_blank" '
        'rel="noopener nofollow" aria-label="Support the archive on Ko-fi">'
        'Support</a>') not in doc_html:
    sys.exit("FAIL: the Ko-fi route is not the labelled Support action")
for needle, label in (
    ('<a href="credits/index.html">About</a>', "About"),
    ('<a href="tip/index.html">Contact</a>', "Contact"),
    ('<a href="top8/archive/index.html">Archive</a>', "Archive"),
    ('<a href="ledger/index.html">Ledger</a>', "Ledger"),
    ('<a href="radar.xml">RSS feed</a>', "RSS"),
    ('class="foot-support"', "Support the archive"),
):
    if needle not in doc_html:
        sys.exit(f"FAIL: the footer has no {label} link")
if doc_html.count('<div class="foot-col">') != 4:
    sys.exit("FAIL: the footer is not the four-column grid")
if '<p class="hero-tag">One-Way Connected.</p>' not in doc_html:
    sys.exit("FAIL: the hero tagline is not exactly 'One-Way Connected.'")
if 'class="btn btn-solid hero-cta" href="sections/index.html"' not in doc_html:
    sys.exit("FAIL: the hero has no single primary CTA")
if 'id="frameworks"' in doc_html or 'class="agent"' in doc_html:
    sys.exit("FAIL: the generation-modules section is back on the front page")
if '<dialog class="modal"' in doc_html:
    sys.exit("FAIL: the framework detail dialogs are back on the front page")
if 'class="fdoors masthead-row"' in doc_html:
    sys.exit("FAIL: the old two-door masthead row is back")
if 'class="clerk"' in doc_html or 'clerk-face' in doc_html:
    sys.exit("FAIL: the clerk card is back above the fold")
if 'class="clerk-note"' not in doc_html:
    sys.exit("FAIL: the closing clerk note is missing")
if '<div class="clerk-note-face"' not in doc_html:
    sys.exit("FAIL: the clerk note has no mascot in it")
if doc_html.find('class="clerk-note"') < doc_html.find('id="top8"'):
    sys.exit("FAIL: the clerk note is ahead of the top 8, so it is not secondary")
# the pair the masthead is removed - it should stay removed
if 'thesis-num' in doc_html:
    sys.exit("FAIL: the 1956/-70,000 pair is back on the front page")
if 'mood="clerk"' not in (ROOT / "tools" / "build_cards.py").read_text(
        encoding="utf-8"):
    sys.exit("FAIL: build_cards.py no longer asks for the clerk mood")
print("  ok   hero tagline, one CTA, no method section, the clerk as a later note")

# 1b. the top 8 band is the live list, and each card lands on its entry.
#     The band is generated from `top8_window`, so the test uses the same
#     function rather than a remembered title or a hardcoded day.
feat = json.loads((ROOT / "data" / "features.json").read_text(encoding="utf-8"))
shown = bc.top8_window(feat)
raw = next((L for L in (feat.get("lists") or [])
            if L.get("slug") == shown.get("slug")), shown)
want_title = shown.get("home_title") or shown.get("title") or "The Top 8"
want_hook = (shown.get("home_hook")
             or bc.deck(shown.get("dek"), 30)).strip()
want_meta = bc.esc(str(shown.get("kicker") or "").title())
span = bc.t8_year_span(raw)
if span:
    want_meta = f"{want_meta} &middot; {span}" if want_meta else span
if f'<h2 id="t8front-title">{bc.esc(want_title)}</h2>' not in doc_html:
    sys.exit(f"FAIL: the top 8 band does not carry the live title {want_title!r}")
if f'<span class="t8front-kick">{want_meta}</span>' not in doc_html:
    sys.exit(f"FAIL: the top 8 kicker is not {want_meta!r}")
if f'<p class="t8front-hook">{bc.esc(want_hook)}</p>' not in doc_html:
    sys.exit("FAIL: the top 8 band does not carry the live hook")
cta = ("View Full Top 8 Analysis &amp; Archive History &rarr;")
if f'href="top8/index.html">{cta}</a>' not in doc_html:
    sys.exit("FAIL: the full Top 8 CTA is missing")
cards = re.findall(r'<a class="t8card" href="top8/index\.html#([^"]+)">(.*?)</a>',
                   doc_html, re.S)
if len(cards) != 8:
    sys.exit(f"FAIL: the front page has {len(cards)} top 8 cards, expected 8")
want_anchors = [bc.t8_anchor(shown, en) for en in shown["entries"]]
if [a for a, _ in cards] != want_anchors:
    sys.exit("FAIL: the top 8 cards are not the live window, in order")
for i, (anchor, body) in enumerate(cards, 1):
    en = shown["entries"][i - 1]
    for needle, label in (
        (f'<span class="t8card-rank">{i:02d}</span>', "rank"),
        (f'<span class="t8card-tag">{bc.esc(en.get("show", ""))}</span>', "show"),
        (f'<b>{bc.esc(en["name"])}</b>', "name"),
        (f'<span class="t8card-hook">{bc.esc(bc.t8_hook(en))}</span>', "hook"),
        ('<span class="t8card-go">Read this entry &rarr;</span>', "read link"),
    ):
        if needle not in body:
            sys.exit(f"FAIL: card {i} has no {label}")
t8page = (ROOT / "top8" / "index.html").read_text(encoding="utf-8")
ids = set(re.findall(r'<li class="t8-item" id="([^"]+)"', t8page))
missing = [a for a in want_anchors if a not in ids]
if missing:
    sys.exit(f"FAIL: {len(missing)} front-page anchors are not on /top8/: {missing}")
if len(ids) != 8:
    sys.exit(f"FAIL: /top8/ carries {len(ids)} anchored entries, expected 8")
if f"Eight of {len(raw.get('entries') or shown['entries'])} from this list" not in doc_html:
    sys.exit("FAIL: the top 8 count note does not match the list")
print("  ok   live top 8 title, hook, eight anchored cards and the full-list CTA")

# 2. a new edition's copy reaches it.
#    --save refuses to overwrite today's date, so the probe gets a date the
#    seed does not use. That is the tool's own rule, exercised rather than
#    worked around: the test dates the probe explicitly.
import datetime as _dt
probe_date = (_dt.date.today() + _dt.timedelta(days=1)).isoformat()
orig_bytes = DATA.read_bytes()
# Preserve the file's own newline convention. This test used to write CRLF
# unconditionally, which was invisible on Windows and made every CI run rewrite
# the committed file from CRLF to LF - one 130-line diff per day, committed by
# the daily job, for a file whose bytes had not changed. The same defect the
# restore assertion exists to catch, one layer down.
nl = "\r\n" if b"\r\n" in orig_bytes[:400] else "\n"
d0 = json.loads(orig_bytes.decode("utf-8"))

# The teardown has to run whatever happens above, including on a failure. It
# used to be a step AFTER the byte-comparison, so the assertion's sys.exit
# skipped it: two failed runs left two "rotation probe" editions in
# data/front_copy.json and left `_live` stamped at the probe, which put
# "PROBE-MARKER-LINE" in the masthead of the real site. This file already
# records the lesson - a test that restores its own data must assert it did -
# and the assertion was right; the ordering was what was broken.
try:
    d0["editions"].append({"date": probe_date, "note": "rotation probe",
                           "copy": dict(d0["editions"][-1]["copy"])})
    DATA.write_bytes(json.dumps(d0, ensure_ascii=False, indent=2)
                     .replace("\n", nl).encode("utf-8"))
    run("--stamp", probe_date)
    run("--set", "line", "PROBE-MARKER-LINE", "--to", probe_date)
    run("--set", "clerk_line", "PROBE-MARKER-CLERK", "--to", probe_date)
    build()
    if "PROBE-MARKER-CLERK" not in page():
        sys.exit("FAIL: the edition's clerk line did not reach the page")
    # The hero no longer prints the edition's `line` slot - it was the second
    # paragraph under the tagline and it went with the rest of the masthead
    # copy. The rotation now reaches the reader through the clerk's note, so
    # this asserts the slot is still carried in the data and deliberately not
    # rendered, which is the difference between "retired" and "forgotten".
    if has("PROBE-MARKER-LINE"):
        sys.exit("FAIL: the retired hero sub-line is rendering again")
    print("  ok   a new edition's copy reaches the page through build_cards")
finally:
    # stamp back, drop the probe edition, rebuild - in that order, and assert
    # the file afterwards rather than trusting that we got here
    run("--stamp", seed)
    d2 = json.loads(DATA.read_text(encoding="utf-8"))
    d2["editions"] = [e for e in d2["editions"] if e["date"] != probe_date]
    d2["_live"] = seed
    DATA.write_bytes(json.dumps(d2, ensure_ascii=False, indent=2)
                     .replace("\n", nl).encode("utf-8"))
    build()
    d3 = json.loads(DATA.read_text(encoding="utf-8"))
    if [e for e in d3["editions"] if e.get("note") == "rotation probe"]:
        sys.exit("FAIL: a probe edition survived the teardown")
    if d3["_live"] != seed:
        sys.exit(f"FAIL: _live is {d3['_live']!r}, expected {seed!r}")
    if set(d3) != {"_live", "_note", "editions"}:
        sys.exit(f"FAIL: top-level keys are {sorted(d3)}")
    if DATA.read_bytes() != orig_bytes:
        sys.exit("FAIL: the teardown did not restore data/front_copy.json "
                 "byte for byte - a test that reformats its own fixture turns "
                 "every daily run into a commit")
    kept = len(d3["editions"])

if has("PROBE-MARKER") or PAGE.read_bytes() != orig:
    sys.exit("FAIL: the page did not come back to where it started")
print("  ok   stamping the seed back restores the page byte for byte")
print(f"  ok   probe removed, {kept} edition(s), live {seed}")
print("\n  rotation verified end to end, through the generator")

