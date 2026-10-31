# -*- coding: utf-8 -*-
"""Prove the parasocialite rotation rotates, records, and reaches the page.

The front page puts one figure forward per UTC day, taking turns in the
roster's file order and anchored on PARASOCIALITE_EPOCH. This checks the five
things that would each fail silently: the date-to-figure mapping, the
alternation contract (a warm case and a costly case never swap places
unnoticed), the record's append/no-op/replace rules, the record's rendering,
and the block as a reader receives it - name, valence, entry link, and the days
under it - through the generator, not against it.
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

REAL_ROSTER = ROOT / "data" / "parasocialite.json"
REAL_HISTORY = ROOT / "data" / "parasocialite_history.json"
PAGE = ROOT / "index.html"
VALENCES = {"harmonious", "manipulative", "obsessive"}


def fail(msg):
    sys.exit("FAIL: " + msg)


roster = json.loads(REAL_ROSTER.read_text(encoding="utf-8"))
members = roster.get("members") or []
ids = [m["id"] for m in members]
if len(members) != 8:
    fail(f"the roster holds {len(members)} members, expected 8")
for m in members:
    if m.get("valence") not in VALENCES:
        fail(f"{m.get('id')} carries valence {m.get('valence')!r}, not one of "
             f"{sorted(VALENCES)}")
    if not m.get("breakdown"):
        fail(f"{m.get('id')} has no breakdown copy for the front-page line")

# 1. deterministic cycle, anchored on the epoch. The history file's meaning
#    depends on this anchor, so a move is a failure rather than a curiosity.
if bc.PARASOCIALITE_EPOCH.isoformat() != "2026-10-19":
    fail(f"PARASOCIALITE_EPOCH is {bc.PARASOCIALITE_EPOCH}, and the recorded "
         f"days name figures under the 2026-10-19 anchor")
for i in range(8):
    got = bc.parasocialite_of_day(roster,
                                  bc.PARASOCIALITE_EPOCH + datetime.timedelta(days=i))
    if got["id"] != ids[i]:
        fail(f"day {i} of the cycle gives {got['id']}, expected {ids[i]}")
wrapped = bc.parasocialite_of_day(roster,
                                  bc.PARASOCIALITE_EPOCH + datetime.timedelta(days=8))
if wrapped["id"] != ids[0]:
    fail("day 8 does not wrap to the first member")
back = bc.parasocialite_of_day(roster,
                               bc.PARASOCIALITE_EPOCH - datetime.timedelta(days=1))
if back["id"] != ids[-1]:
    fail(f"the day before the epoch gives {back['id']}, expected {ids[-1]}")
if bc.parasocialite_of_day({"members": []}) is not None:
    fail("an empty roster should rotate nothing rather than raise")
if bc.parasocialite_of_day(None) is not None:
    fail("a missing roster should rotate nothing rather than raise")
print("  ok   8-day cycle, wrap, and dates before the epoch")

# 2. the alternation contract: a warm case and a costly case every other day,
#    warm on odd indices. If the roster is reordered without keeping this, the
#    front page starts opening on two bleak days in a row.
for i, m in enumerate(members):
    if (m["valence"] == "harmonious") != (i % 2 == 1):
        fail(f"member {i} ({m['id']}, {m['valence']}) breaks the alternation "
             f"contract: harmonious must sit on odd indices")
print("  ok   the roster alternates warm and costly, warm on odd days")

# 3. the record: append / same-day no-op / mid-day replace, on temp files so
#    the committed history is never the thing under test.
tmpdir = pathlib.Path(tempfile.mkdtemp(prefix="psotd-rot-"))
tmp_roster = tmpdir / "parasocialite.json"
tmp_roster.write_text(json.dumps(roster), encoding="utf-8")
tmp_hist = tmpdir / "parasocialite_history.json"
bc.PARASOCIALITE = tmp_roster
bc.PARASOCIALITE_HISTORY = tmp_hist
changed, entry = bc.record_parasocialite_day(bc.PARASOCIALITE_EPOCH)
if not changed or entry != {"date": "2026-10-19", "member": ids[0]}:
    fail(f"the first record was {changed}, {entry}")
if "_note" not in json.loads(tmp_hist.read_text(encoding="utf-8")):
    fail("the record carries no _note")
changed, entry = bc.record_parasocialite_day(bc.PARASOCIALITE_EPOCH)
if changed:
    fail("a same-day rebuild was not a no-op")
if len(json.loads(tmp_hist.read_text(encoding="utf-8"))["days"]) != 1:
    fail("the no-op day was written a second time")
reversed_roster = {"members": list(reversed(members))}
tmp_roster.write_text(json.dumps(reversed_roster), encoding="utf-8")
changed, entry = bc.record_parasocialite_day(bc.PARASOCIALITE_EPOCH)
if not changed or entry["member"] != ids[-1]:
    fail(f"a mid-day change did not replace the day: {changed}, {entry}")
days = json.loads(tmp_hist.read_text(encoding="utf-8"))["days"]
if len(days) != 1 or days[0]["member"] != ids[-1]:
    fail(f"the mid-day replace left {days}")
print("  ok   append, same-day no-op, and mid-day replace")

# 4. the record renders, names a figure it no longer knows, and degrades to
#    nothing when the file is missing.
tmp_roster.write_text(json.dumps(roster), encoding="utf-8")
tmp_hist.write_text(json.dumps({
    "_note": "(test)",
    "days": [{"date": "2026-10-18", "member": "the-grouch"},
             {"date": "2026-10-19", "member": ids[0]}]},
    ensure_ascii=False), encoding="utf-8")
html = bc.parasocialite_record("2026-10-19")
if "<b>The record</b>" not in html or "19 OCT 2026" not in html:
    fail(f"the record does not render the day: {html[:160]}")
if f'<b>{members[0]["name"]}</b>' not in html:
    fail("the record does not resolve today's member's name")
if '<span class="psotd-today">today</span>' not in html:
    fail("today is not marked in the record")
if "A figure no longer in the roster" not in html:
    fail("an unknown member id is dropped instead of named")
missing = tmpdir / "nope.json"
bc.PARASOCIALITE_HISTORY = missing
if bc.parasocialite_record("2026-10-19") != "":
    fail("a missing history file should render nothing")
print("  ok   the record renders, names the unknown, and survives a miss")

# 5. the page, through the generator.
real_before = REAL_HISTORY.read_bytes() if REAL_HISTORY.exists() else None
r = subprocess.run([sys.executable, "-X", "utf8",
                    str(ROOT / "tools" / "build_cards.py")],
                   capture_output=True, text=True, cwd=ROOT,
                   encoding="utf-8", errors="replace")
if r.returncode != 0:
    fail(f"build_cards failed\n{r.stdout}{r.stderr}")
page = PAGE.read_text(encoding="utf-8")
today = bc.parasocialite_of_day(roster)
today_iso = datetime.datetime.now(datetime.timezone.utc).date().isoformat()
card_count = page.count('class="psotd-card"')
if card_count != 1:
    fail(f"the front page should carry exactly one spotlight, it carries "
         f"{card_count}")
if f'encyclopedia/{today["id"]}.html' not in page:
    fail("the spotlight does not link to today's entry")
if f'psotd-val-{today["valence"]}' not in page:
    fail("the spotlight does not carry today's valence")
if 'id="psotd-record"' not in page:
    fail("the record is not under the spotlight")
if '<span class="psotd-today">today</span>' not in page:
    fail("today is not marked on the front page")
t8_pos = page.find("t8col-wrap")
if t8_pos != -1 and page.find("psotd-sec") > t8_pos:
    fail("the spotlight renders below the top 8 rather than above it")
hist = json.loads(REAL_HISTORY.read_text(encoding="utf-8"))["days"]
if hist[-1]["date"] != today_iso or hist[-1]["member"] != today["id"]:
    fail(f"the record says {hist[-1]}, the page names {today['id']} on {today_iso}")
after = REAL_HISTORY.read_bytes()
if real_before is not None:
    b = json.loads(real_before.decode("utf-8"))["days"]
    if b and b[-1]["date"] == today_iso and after != real_before:
        fail("a same-day rebuild rewrote the committed history instead of "
             "being a no-op")
print("  ok   spotlight, valence and record reach the page, once each")
print("\n  parasocialite rotation verified end to end, through the generator")
