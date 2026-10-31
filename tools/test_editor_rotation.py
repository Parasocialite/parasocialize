# -*- coding: utf-8 -*-
"""Prove tomorrow's edition cannot silently repeat today's.

The daily features are only meaningful if the next day differs. This exercises
the chooser directly for tomorrow, using the real history as the only state:

  * tomorrow's theme is not a theme used in the last 21 days, so today's theme
    is excluded;
  * tomorrow's figure is not today's figure;
  * tomorrow's eight entries are not the same eight (and with a different theme,
    normally share none).

It writes nothing and needs no network. It is in the source tier because it is
the contract that "new top 8 daily" actually means.
"""
import datetime
import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))
import editor  # noqa: E402

TODAY = datetime.datetime.now(datetime.timezone.utc).date()
TOMORROW = TODAY + datetime.timedelta(days=1)


def fail(msg):
    sys.exit("FAIL: " + msg)


def load(name, default):
    try:
        return json.loads((ROOT / "data" / name).read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return default


themes = load("top8_themes.json", {"themes": []})["themes"]
figures = load("parasocialite.json", {"members": []})["members"]
enc = load("encyclopedia.json", {"entries": []})["entries"]
plac = load("taxonomy_placements.json", {"assignments": {}})["assignments"]
days = load("top8_history.json", {"days": []})["days"]
pdays = load("parasocialite_history.json", {"days": []})["days"]
ed = load("editorial_today.json", {})

if str(ed.get("date")) != TODAY.isoformat():
    fail("today's edition is missing; run tools/editor.py --refresh first")
today_theme = (ed.get("theme") or {}).get("id")
today_figure = (ed.get("figure") or {}).get("id")
L = next((x for x in load("features.json", {"lists": []})["lists"]
          if str(x.get("released"))[:10] == TODAY.isoformat()), None)
if not L:
    fail("today's list is missing")
today_ids = [e.get("entry") for e in L.get("entries") or []]

theme, from_news = editor.choose_theme(themes, [], days, TOMORROW)
if not theme:
    fail("no theme for tomorrow")
if theme["id"] == today_theme:
    fail(f"tomorrow repeats today's theme {today_theme!r}")
print(f"  ok   tomorrow's theme: {theme['id']} (today {today_theme})")

fig = editor.choose_figure(figures, [], theme, pdays, TOMORROW)
if fig["id"] == today_figure:
    fail(f"tomorrow repeats today's figure {today_figure!r}")
if fig.get("kind") not in ("real", "fictional"):
    fail(f"tomorrow's figure is a {fig.get('kind')!r}")
print(f"  ok   tomorrow's figure: {fig['name']} ({fig['kind']})")

entries, _ = editor.choose_entries(enc, theme, plac, days, TOMORROW, 8)
if len(entries) != 8:
    fail(f"tomorrow's list has {len(entries)} entries")
ids = [e["id"] for e in entries]
if ids == today_ids:
    fail("tomorrow's eight are exactly today's eight")
if len(set(ids)) != 8:
    fail("tomorrow's list repeats an entry")
print(f"  ok   tomorrow's eight: {len(set(ids) - set(today_ids))} new, "
      f"{len(set(ids) & set(today_ids))} shared")
print("\n  tomorrow's edition is structurally different from today's")
