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
import json
import pathlib
import re
import subprocess
import sys

sys.stdout.reconfigure(encoding="utf-8")
ROOT = pathlib.Path(__file__).resolve().parent.parent
DATA = ROOT / "data" / "front_copy.json"
PAGE = ROOT / "index.html"


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
row = re.search(r'<div class="fdoors masthead-row">(.*?)\n    </div>', doc_html,
                re.S)
if not row:
    sys.exit("FAIL: the generated page has no masthead row")
row = row.group(1)
doors = re.findall(r'<a class="fdoor" href="([^"]+)"', row)
if len(doors) != 2:
    sys.exit(f"FAIL: the masthead row holds {len(doors)} doors, expected 2 "
             f"(read + research). Found: {doors}")
if 'class="clerk"' not in row:
    sys.exit("FAIL: the clerk card is not in the masthead row beside the doors")
if '<div class="clerk-face"' not in row:
    sys.exit("FAIL: the clerk card has no mascot in it")
# the pair the masthead is removed - it should stay removed
if 'thesis-num' in doc_html:
    sys.exit("FAIL: the 1956/-70,000 pair is back on the front page")
if 'mood="clerk"' not in (ROOT / "tools" / "build_cards.py").read_text(
        encoding="utf-8"):
    sys.exit("FAIL: build_cards.py no longer asks for the clerk mood")
print("  ok   two doors and the clerk in one row, with the clerk mood")

# 2. a new edition's copy reaches it.
#    --save refuses to overwrite today's date, so the probe gets a date the
#    seed does not use. That is the tool's own rule, exercised rather than
#    worked around: the test dates the probe explicitly.
import datetime as _dt
probe_date = (_dt.date.today() + _dt.timedelta(days=1)).isoformat()
d0 = json.loads(DATA.read_text(encoding="utf-8"))

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
                     .replace("\n", "\r\n").encode("utf-8"))
    run("--stamp", probe_date)
    run("--set", "line", "PROBE-MARKER-LINE", "--to", probe_date)
    run("--set", "clerk_line", "PROBE-MARKER-CLERK", "--to", probe_date)
    build()
    if not (has("PROBE-MARKER-LINE") and has("PROBE-MARKER-CLERK")):
        sys.exit("FAIL: edition copy did not reach the page")
    print("  ok   a new edition's copy reaches the page through build_cards")
finally:
    # stamp back, drop the probe edition, rebuild - in that order, and assert
    # the file afterwards rather than trusting that we got here
    run("--stamp", seed)
    d2 = json.loads(DATA.read_text(encoding="utf-8"))
    d2["editions"] = [e for e in d2["editions"] if e["date"] != probe_date]
    d2["_live"] = seed
    DATA.write_bytes(json.dumps(d2, ensure_ascii=False, indent=2)
                     .replace("\n", "\r\n").encode("utf-8"))
    build()
    d3 = json.loads(DATA.read_text(encoding="utf-8"))
    if [e for e in d3["editions"] if e.get("note") == "rotation probe"]:
        sys.exit("FAIL: a probe edition survived the teardown")
    if d3["_live"] != seed:
        sys.exit(f"FAIL: _live is {d3['_live']!r}, expected {seed!r}")
    if set(d3) != {"_live", "_note", "editions"}:
        sys.exit(f"FAIL: top-level keys are {sorted(d3)}")
    kept = len(d3["editions"])

if has("PROBE-MARKER") or PAGE.read_bytes() != orig:
    sys.exit("FAIL: the page did not come back to where it started")
print("  ok   stamping the seed back restores the page byte for byte")
print(f"  ok   probe removed, {kept} edition(s), live {seed}")
print("\n  rotation verified end to end, through the generator")

