# -*- coding: utf-8 -*-
"""Prove the daily figure is a figure, the edition is today's, and the record holds.

The old test guarded a fixed eight-member rotation. That rotation included a
game show, which is exactly the defect the daily editor replaced: a
parasocialite must be a real person or a fictional character. This test guards
the new contract instead:

  1. every selectable bank member is a figure with a real entry page;
  2. today's edition is stored, dated today and valid;
  3. the top 8 shown today is the list dated today, never the old cartoons list;
  4. the eight way pages each have a pick filed on that way;
  5. the record appends, no-ops and replaces on temp files;
  6. the front page carries the figure, its kind and its reason, through the
     generator rather than against the data.
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

BANK = ROOT / "data" / "parasocialite.json"
HISTORY = ROOT / "data" / "parasocialite_history.json"
FEATURES = ROOT / "data" / "features.json"
EDITORIAL = ROOT / "data" / "editorial_today.json"
ENC = json.loads((ROOT / "data" / "encyclopedia.json").read_text(encoding="utf-8"))
BYID = {e["id"]: e for e in ENC["entries"]}
TODAY = datetime.datetime.now(datetime.timezone.utc).date().isoformat()
VALENCES = {"harmonious", "manipulative", "obsessive"}


def fail(msg):
    sys.exit("FAIL: " + msg)


bank = json.loads(BANK.read_text(encoding="utf-8"))
members = bank.get("members") or []
selectable = [m for m in members if m.get("selectable")]
if len(members) < 20:
    fail(f"the figure bank holds {len(members)} members, expected a daily pool")
if len(selectable) < 20:
    fail(f"only {len(selectable)} members are selectable")
for m in selectable:
    if m.get("kind") not in ("real", "fictional"):
        fail(f"{m.get('id')} is a {m.get('kind')!r}, not a real or fictional figure")
    if m.get("entry") not in BYID:
        fail(f"{m.get('id')} links to {m.get('entry')!r}, which is not an entry")
    if not m.get("aliases"):
        fail(f"{m.get('id')} has no wire aliases")
    if m.get("valence") not in VALENCES:
        fail(f"{m.get('id')} has valence {m.get('valence')!r}")
nonfig = [m for m in members if not m.get("selectable")]
if not nonfig or any(m["kind"] != "format" for m in nonfig):
    fail("the only non-selectable bank member should be the historical format")
if any(m.get("id") == "queen-for-a-day" and m.get("selectable")
       for m in members):
    fail("Queen for a Day is a format and must not be selectable")
print(f"  ok   {len(selectable)} figures, all real or fictional, all with entries")

# 2. today's stored edition is valid
ed = json.loads(EDITORIAL.read_text(encoding="utf-8"))
if str(ed.get("date")) != TODAY:
    fail(f"editorial_today.json is dated {ed.get('date')}, not {TODAY}")
fig = ed.get("figure") or {}
if fig.get("id") not in {m["id"] for m in selectable}:
    fail(f"today's figure {fig.get('id')!r} is not a selectable bank member")
if fig.get("kind") not in ("real", "fictional"):
    fail(f"today's figure {fig.get('id')!r} is a {fig.get('kind')!r}")
if not fig.get("why_today"):
    fail("today's figure has no reason")
if fig.get("entry") not in BYID:
    fail("today's figure links to no entry")
print(f"  ok   today's figure: {fig.get('name')} ({fig.get('kind')})")

# 3. today's list is the show, and the cartoons list is archive-only
feat = json.loads(FEATURES.read_text(encoding="utf-8"))
shown = bc.show_list(feat, TODAY)
today_lists = [L for L in feat.get("lists") or []
               if str(L.get("released") or "")[:10] == TODAY]
if len(today_lists) != 1:
    fail(f"features.json holds {len(today_lists)} lists dated today")
L = today_lists[0]
if shown.get("slug") != L.get("slug"):
    fail("show_list does not return today's list")
if shown.get("slug") == "top8-cartoons-90s":
    fail("the cartoons list is still the show; it belongs in the archive")
if not any(x.get("slug") == "top8-cartoons-90s"
           for x in feat.get("lists") or []):
    fail("the cartoons list was deleted rather than archived")
if len(L.get("entries") or []) != 8:
    fail(f"today's list has {len(L.get('entries') or [])} entries, expected 8")
ids = [e.get("entry") for e in L["entries"]]
if len(set(ids)) != 8:
    fail("today's list repeats an entry")
for e in L["entries"]:
    if e.get("entry") not in BYID:
        fail(f"{e.get('name')!r} names no encyclopedia entry")
    if not e.get("what") or not e.get("why"):
        fail(f"{e.get('name')!r} has no what/why")
    if "**" in (e.get("what") or "") + (e.get("why") or ""):
        fail(f"{e.get('name')!r} still carries markdown")
if not L.get("theme"):
    fail("today's list names no theme")
print(f"  ok   show is {L.get('slug')} - eight ranked entries, cartoons archived")

# 4. every way has a pick filed on it
tax = json.loads((ROOT / "data" / "taxonomy.json").read_text(encoding="utf-8"))
plac = json.loads((ROOT / "data" / "taxonomy_placements.json")
                  .read_text(encoding="utf-8"))["assignments"]
stories = json.loads((ROOT / "data" / "story_placements.json")
                     .read_text(encoding="utf-8"))["placements"]
ways = ed.get("ways") or {}
for cat in tax["attachment"]:
    p = ways.get(cat["id"])
    if not p:
        fail(f"no way pick for {cat['id']}")
    if p.get("kind") == "entry":
        if p.get("id") not in plac or plac[p["id"]].get("cat") != cat["id"]:
            fail(f"{cat['id']} entry {p.get('id')!r} is not filed there")
    elif p.get("kind") == "story":
        if p.get("id") not in stories or stories[p["id"]].get("cat") != cat["id"]:
            fail(f"{cat['id']} story {p.get('id')!r} is not filed there")
    else:
        fail(f"{cat['id']} pick has unknown kind {p.get('kind')!r}")
print(f"  ok   {len(ways)} ways, every pick filed on its own shelf")

# 5. the fallback is a figure and is deterministic; the record still appends,
#    no-ops and replaces, on temp files so the committed sequence is untouched.
real_bank = bc.PARASOCIALITE
real_hist = bc.PARASOCIALITE_HISTORY
tmp = pathlib.Path(tempfile.mkdtemp(prefix="psotd-daily-"))
bc.PARASOCIALITE_HISTORY = tmp / "history.json"
d0 = datetime.date(2026, 10, 19)
a = bc.parasocialite_of_day(bank, d0)
b = bc.parasocialite_of_day(bank, d0)
if a is None or a.get("id") != b.get("id"):
    fail("the fallback is not deterministic")
if a.get("kind") not in ("real", "fictional"):
    fail(f"the fallback chose a {a.get('kind')!r}")
if bc.parasocialite_of_day({"members": []}, d0) is not None:
    fail("an empty bank should select nothing")

changed, entry = bc.record_parasocialite_day(d0)
if not changed:
    fail("the first record was not written")
again, _ = bc.record_parasocialite_day(d0)
if again:
    fail("a same-day rebuild was not a no-op")
# A mid-day change of the stored figure replaces the day, not appends it.
now = datetime.datetime.now(datetime.timezone.utc).date().isoformat()
orig = bc.parasocialite_of_day
bc.parasocialite_of_day = lambda roster=None, today=None: {
    "id": "dionne-warwick", "name": "Dionne Warwick", "kind": "real",
    "entry": "dionne-warwick", "valence": "harmonious",
    "breakdown": "test", "why_today": "test"}
changed, entry = bc.record_parasocialite_day(now)
if not changed or entry.get("member") != "dionne-warwick":
    fail("a mid-day figure change did not replace the day")
bc.parasocialite_of_day = orig
days = json.loads(bc.PARASOCIALITE_HISTORY.read_text(encoding="utf-8"))["days"]
if len(days) != 2 or days[-1]["member"] != "dionne-warwick":
    fail(f"the record holds {days}, expected two days with the replacement last")
bc.PARASOCIALITE_HISTORY = real_hist
print("  ok   fallback is a figure; record appends, no-ops and replaces")

# 6. the record renders names and the front page carries the block, through the
#    generator. The committed history is compared before and after.
before = HISTORY.read_bytes() if HISTORY.exists() else None
r = subprocess.run([sys.executable, "-X", "utf8",
                    str(ROOT / "tools" / "build_cards.py")],
                   capture_output=True, text=True, cwd=ROOT,
                   encoding="utf-8", errors="replace")
if r.returncode != 0:
    fail(f"build_cards failed\n{r.stdout}{r.stderr}")
page = (ROOT / "index.html").read_text(encoding="utf-8")
fig2 = bc.parasocialite_of_day()
if f'encyclopedia/{fig2.get("entry")}.html' not in page:
    fail("the spotlight does not link to today's figure's entry")
if 'class="psotd-kind"' not in page:
    fail("the spotlight does not state whether the figure is real or fictional")
if 'class="psotd-why"' not in page:
    fail("the spotlight does not state why the figure is today's")
if 'id="psotd-record"' not in page:
    fail("the record is not under the spotlight")
if 'class="t8card"' not in page:
    fail("the daily top 8 did not reach the front page")
t8 = (ROOT / "top8" / "index.html").read_text(encoding="utf-8")
if "Read the entry" not in t8:
    fail("the top 8 does not link to the entries it is drawn from")
hist = json.loads(HISTORY.read_text(encoding="utf-8"))["days"]
if hist[-1]["date"] != TODAY or hist[-1]["member"] != fig2.get("id"):
    fail(f"the record says {hist[-1]}, the page names {fig2.get('id')}")
after = HISTORY.read_bytes()
if before is not None and after != before:
    b0 = json.loads(before.decode("utf-8"))["days"]
    if b0 and b0[-1]["date"] == TODAY:
        fail("a same-day rebuild rewrote the committed figure record")
print("  ok   figure, kind, reason, record and daily top 8 reach the page")
print("\n  daily edition verified end to end, through the generator")
