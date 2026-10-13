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
orig = PAGE.read_bytes()

# 1. the live edition reaches the generated page
build()
if not has('<div class="masthead-grid">') or not has('class="clerk"'):
    sys.exit("FAIL: the generated page has no masthead lockup")
if not has('<div class="clerk-face"'):
    sys.exit("FAIL: the clerk card has no mascot in it")
if 'mood="clerk"' not in (ROOT / "tools" / "build_cards.py").read_text(
        encoding="utf-8"):
    sys.exit("FAIL: build_cards.py no longer asks for the clerk mood")
print("  ok   the live edition is on the generated page, with the clerk mood")

# 2. a new edition's copy reaches it.
#    --save refuses to overwrite today's date, so the probe gets a date the
#    seed does not use. That is the tool's own rule, exercised rather than
#    worked around: the test dates the probe explicitly.
import datetime as _dt
probe_date = (_dt.date.today() + _dt.timedelta(days=1)).isoformat()
d0 = json.loads(DATA.read_text(encoding="utf-8"))
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

# 3. stamping the seed back restores it byte for byte
run("--stamp", seed)
build()
if has("PROBE-MARKER") or PAGE.read_bytes() != orig:
    sys.exit("FAIL: the page did not come back to where it started")
print("  ok   stamping the seed back restores the page byte for byte")

# 4. drop the probe edition
d2 = json.loads(DATA.read_text(encoding="utf-8"))
d2["editions"] = [e for e in d2["editions"] if e["date"] != probe_date]
d2["_live"] = seed
DATA.write_bytes(json.dumps(d2, ensure_ascii=False, indent=2)
                 .replace("\n", "\r\n").encode("utf-8"))
if PAGE.read_bytes() != orig:
    sys.exit("FAIL: page changed while cleaning up")
print(f"  ok   probe removed, {len(d2['editions'])} edition(s), live {seed}")
print("\n  rotation verified end to end, through the generator")
