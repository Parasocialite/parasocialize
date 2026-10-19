# -*- coding: utf-8 -*-
"""Prove the register rotation rotates, records, and reaches the page.

A register is a definition rather than a member list (AGENTS items 35 and
45), so there is nothing to pick members from - the rotation runs on the
eight definitions in file order. This checks the four things that would each
fail silently: the date-to-register mapping, the record's append/no-op/replace
rules, the record's rendering, and the section as a reader receives it -
spotlight, today marker, and the days under the list - through the generator,
not against it.
"""
import datetime
import json
import pathlib
import subprocess
import sys
import tempfile

sys.stdout.reconfigure(encoding="utf-8")
ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))
import build_cards as bc  # noqa: E402

REAL_HISTORY = ROOT / "data" / "register_history.json"
PAGE = ROOT / "taxonomy" / "index.html"


def fail(msg):
    sys.exit("FAIL: " + msg)


tax = json.loads((ROOT / "data" / "taxonomy.json").read_text(encoding="utf-8"))
regs = tax["register"]
ids = [r["id"] for r in regs]
if len(regs) != 8:
    fail(f"the register axis holds {len(regs)} definitions, expected 8")

# 1. deterministic cycle, anchored on the epoch. The history file's meaning
#    depends on this anchor, so a move is a failure rather than a curiosity.
if bc.REGISTER_EPOCH.isoformat() != "2026-10-19":
    fail(f"REGISTER_EPOCH is {bc.REGISTER_EPOCH}, and the recorded days name "
         f"registers under the 2026-10-19 anchor")
for i in range(8):
    got = bc.register_of_day(tax, bc.REGISTER_EPOCH + datetime.timedelta(days=i))
    if got["id"] != ids[i]:
        fail(f"day {i} of the cycle gives {got['id']}, expected {ids[i]}")
wrapped = bc.register_of_day(tax, bc.REGISTER_EPOCH + datetime.timedelta(days=8))
if wrapped["id"] != ids[0]:
    fail("day 8 does not wrap to the first definition")
back = bc.register_of_day(tax, bc.REGISTER_EPOCH - datetime.timedelta(days=1))
if back["id"] != ids[-1]:
    fail(f"the day before the epoch gives {back['id']}, expected {ids[-1]}")
if bc.register_of_day({"register": []}) is not None:
    fail("an empty register axis should rotate nothing rather than raise")
print("  ok   8-day cycle, wrap, and dates before the epoch")

# 2. the record: append / same-day no-op / mid-day replace, on a temp file so
#    the committed history is never the thing under test.
tmp = pathlib.Path(tempfile.mkdtemp(prefix="register-rot-")) / "register_history.json"
bc.REGISTER_HISTORY = tmp
changed, entry = bc.record_register_day(tax, bc.REGISTER_EPOCH)
if not changed or entry != {"date": "2026-10-19", "register": ids[0]}:
    fail(f"the first record was {changed}, {entry}")
if "_note" not in json.loads(tmp.read_text(encoding="utf-8")):
    fail("the record carries no _note")
changed, entry = bc.record_register_day(tax, bc.REGISTER_EPOCH)
if changed:
    fail("a same-day rebuild was not a no-op")
if len(json.loads(tmp.read_text(encoding="utf-8"))["days"]) != 1:
    fail("the no-op day was written a second time")
rotated = {"register": list(reversed(tax["register"]))}
changed, entry = bc.record_register_day(rotated, bc.REGISTER_EPOCH)
if not changed or entry["register"] != ids[-1]:
    fail(f"a mid-day change did not replace the day: {changed}, {entry}")
days = json.loads(tmp.read_text(encoding="utf-8"))["days"]
if len(days) != 1 or days[0]["register"] != ids[-1]:
    fail(f"the mid-day replace left {days}")
print("  ok   append, same-day no-op, and mid-day replace")

# 3. the record renders, names a register it no longer knows, and degrades
#    to nothing when the file is missing.
html = bc.register_record(tax, "2026-10-19")
if "<b>The record</b>" not in html or "19 OCT 2026" not in html:
    fail(f"the record does not render the day: {html[:160]}")
if "A register no longer defined" not in bc.register_record({"register": []},
                                                            "2026-10-19"):
    fail("an unknown register id is dropped instead of named")
missing = pathlib.Path(tempfile.mkdtemp(prefix="register-none-")) / "nope.json"
bc.REGISTER_HISTORY = missing
if bc.register_record(tax, "2026-10-19") != "":
    fail("a missing history file should render nothing")
print("  ok   the record renders, names the unknown, and survives a miss")

# 4. the page, through the generator.
real_before = REAL_HISTORY.read_bytes() if REAL_HISTORY.exists() else None
r = subprocess.run([sys.executable, "-X", "utf8",
                    str(ROOT / "tools" / "build_cards.py")],
                   capture_output=True, text=True, cwd=ROOT,
                   encoding="utf-8", errors="replace")
if r.returncode != 0:
    fail(f"build_cards failed\n{r.stdout}{r.stderr}")
page = PAGE.read_text(encoding="utf-8")
today = bc.register_of_day(tax)
today_iso = datetime.datetime.now(datetime.timezone.utc).date().isoformat()
if page.count('class="tx-day"') != 1:
    fail("the register section should carry exactly one spotlight")
if f'id="tx-{today["id"]}"' not in page:
    fail("today's register has no definition card")
if '<span class="tx-today-tag">today</span>' not in page:
    fail("today is not marked in the list or the record")
if 'id="tx-reg-record"' not in page:
    fail("the record is not under the register list")
if f'encyclopedia/index.html?q={today["id"].split("-")[0]}#db' not in page:
    fail("the spotlight search link does not carry the register term")
if page.count("Register · what is happening in the tie") != 1:
    fail("the register section is duplicated on the page")
if page.count("Attachment · who or what is on the other end") != 1:
    fail("the attachment section is duplicated on the page")
hist = json.loads(REAL_HISTORY.read_text(encoding="utf-8"))["days"]
if hist[-1]["date"] != today_iso or hist[-1]["register"] != today["id"]:
    fail(f"the record says {hist[-1]}, the page names {today['id']} on {today_iso}")
after = REAL_HISTORY.read_bytes()
if real_before is not None:
    b = json.loads(real_before.decode("utf-8"))["days"]
    if b and b[-1]["date"] == today_iso and after != real_before:
        fail("a same-day rebuild rewrote the committed history instead of "
             "being a no-op")
print("  ok   spotlight, today marker and record reach the page, once each")
print("\n  register rotation verified end to end, through the generator")
