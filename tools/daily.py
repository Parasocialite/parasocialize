#!/usr/bin/env python3
"""daily.py - one command that leaves the site current, checked and packaged.

WHY THIS EXISTS
The site has three date-seeded rotations, three history files, a coverage
planner and a deploy tree, and until now each of them was somebody's separate
step. That failed in a way worth naming precisely: the rotations were correct,
the gates were green, and the front page sat on 21 October for ten days
because the command that packages a deploy never ran the generator. A later
audit found the scheduled workflows had never run either - `origin` points at
`YOUR-USER`, so the cron was decoration - and the daily records had six holes
that nothing reported.

A process that depends on remembering five commands in the right order is not
a process. This file is the one command:

    reconcile the archive -> plan the next categorical work -> rebuild ->
    draw plates -> package -> run the post and source gates -> package the
    deploy -> write the run record -> package again (the run record is data,
    and the freshness gate reads data) -> prove today is on the page.

`--check` is the same contract without any writes, and it is the thing a
scheduled job, a CI step or a returning agent should run first. It fails on a
missing day, a stale plan, a deploy tree that does not carry today's rotation,
or a record that was rebuilt today rather than observed.

WHAT IT DELIBERATELY DOES NOT DO
It does not invent content, promote drafts, or sign anything at /desk/. The
sweeper and the planner propose; a person signs. It also does not push or
upload: the remote is currently a placeholder, and publishing remains a
manual action. What it does do is make sure that when somebody does publish,
the tree is today's and the gates have already seen it.

Usage:
    python tools/daily.py                 # full daily cycle, zip to Desktop
    python tools/daily.py --check         # report only, exit 1 on a deficiency
    python tools/daily.py --no-zip
    python tools/daily.py --zip out/site.zip
    python tools/daily.py --visual        # include the Chrome layout tier
    python tools/daily.py --skip-gates    # build and package only
"""
from __future__ import annotations

import argparse
import datetime
import json
import pathlib
import re
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
TOOLS = ROOT / "tools"
sys.path.insert(0, str(TOOLS))

import build_cards as bc  # noqa: E402

sys.stdout.reconfigure(encoding="utf-8")

RUN_LOG = ROOT / "data" / "daily.json"
PLAN = ROOT / "data" / "plan.json"
HISTORIES = {
    "top8": bc.TOP8_HISTORY,
    "register": bc.REGISTER_HISTORY,
    "parasocialite": bc.PARASOCIALITE_HISTORY,
}


def utc_today() -> datetime.date:
    return datetime.datetime.now(datetime.timezone.utc).date()


def run(name: str, argv: list[str], capture: bool = False):
    # flush=True because CI redirects stdout to a file: without it the section
    # headers arrive after the child output they introduce, which made the
    # first CI failure read as if `package` had run after the traceback.
    print(f"\n=== {name} ===", flush=True)
    cmd = [sys.executable, "-X", "utf8", str(TOOLS / argv[0])] + argv[1:]
    proc = subprocess.run(cmd, cwd=ROOT, text=True,
                          stdout=subprocess.PIPE if capture else None,
                          stderr=subprocess.STDOUT if capture else None)
    if proc.returncode:
        if capture and proc.stdout:
            print(proc.stdout)
        raise SystemExit(f"{name} failed with exit {proc.returncode}; "
                         "nothing after this step ran")
    return proc.stdout or ""


def history_days(path: pathlib.Path) -> list[dict]:
    try:
        return json.loads(path.read_text(encoding="utf-8")).get("days") or []
    except (OSError, ValueError):
        return []


def origin_is_placeholder() -> bool:
    """The scheduled workflows are only real if origin is a real repository."""
    cfg = ROOT / ".git" / "config"
    if not cfg.exists():
        return True
    text = cfg.read_text(encoding="utf-8", errors="replace")
    m = re.search(r"^\s*url\s*=\s*(\S+)", text, re.M)
    return not m or "YOUR-USER" in m.group(1)


def sweep_age() -> int | None:
    try:
        s = json.loads((ROOT / "data" / "sweep.json").read_text(encoding="utf-8"))
        when = datetime.datetime.fromisoformat(
            str(s["last_run"]).replace("Z", "+00:00"))
        if when.tzinfo is None:
            when = when.replace(tzinfo=datetime.timezone.utc)
        return (datetime.datetime.now(datetime.timezone.utc) - when).days
    except (OSError, ValueError, KeyError):
        return None


def check() -> int:
    today = utc_today().isoformat()
    hard, warn = [], []

    # 1. the archive: every day from the epoch to today has a record
    print(f"daily check {today}")
    rc = subprocess.run([sys.executable, "-X", "utf8",
                         str(TOOLS / "archive.py"), "--check"],
                        cwd=ROOT, text=True, capture_output=True)
    for line in (rc.stdout or "").splitlines():
        if line.startswith(("  FAIL", "archive:")):
            print("  " + line.strip())
    if rc.returncode:
        hard.append("the archive has missing or malformed days")

    # 2. today is recorded live in all three, not reconstructed
    for name, path in HISTORIES.items():
        days = history_days(path)
        last = days[-1] if days else {}
        if str(last.get("date")) != today:
            hard.append(f"{name}: today is not recorded (last is "
                        f"{last.get('date') or 'nothing'})")
        elif last.get("reconstructed"):
            hard.append(f"{name}: today is marked rebuilt, not observed")
        else:
            print(f"  ok   {name}: {today} recorded live")

    # 3. the categorical plan was measured today
    try:
        plan = json.loads(PLAN.read_text(encoding="utf-8"))
        if plan.get("generated") != today:
            hard.append(f"the categorical plan is dated {plan.get('generated')}"
                        f", not {today}")
        else:
            print(f"  ok   plan: measured {today}, "
                  f"{len(plan.get('actions') or [])} action(s)")
    except (OSError, ValueError):
        hard.append("data/plan.json is missing or unreadable")

    # 4. the deploy tree carries today's rotation, not merely a valid page
    dist_top = ROOT / "dist" / "top8" / "index.html"
    dist_front = ROOT / "dist" / "index.html"
    dist_tax = ROOT / "dist" / "taxonomy" / "index.html"
    if not (dist_top.exists() and dist_front.exists() and dist_tax.exists()):
        hard.append("dist/ is missing - package it before checking")
    else:
        stamp = bc.fmt_date(today)
        top = dist_top.read_text(encoding="utf-8")
        if stamp not in top:
            hard.append(f"dist/top8 does not carry {stamp}")
        else:
            print(f"  ok   dist/top8 carries {stamp}")

        feat = json.loads((ROOT / "data" / "features.json")
                          .read_text(encoding="utf-8"))
        L = bc.top8_window(feat, today)
        missing = [bc.t8_eid(en) for en in L["entries"]
                   if bc.t8_anchor(L, en) not in top]
        if missing:
            hard.append("dist/top8 is missing today's anchors: "
                        f"{missing[:4]}")
        else:
            print("  ok   dist/top8 carries all eight of today's anchors")

        tax = json.loads((ROOT / "data" / "taxonomy.json")
                         .read_text(encoding="utf-8"))
        reg = bc.register_of_day(tax, today)
        if reg and reg.get("name") and reg["name"] not in \
                dist_tax.read_text(encoding="utf-8"):
            hard.append(f"dist/taxonomy does not name today's register "
                        f"({reg['name']})")
        else:
            print("  ok   dist/taxonomy names today's register")

        pso = bc.parasocialite_of_day(bc.parasocialite_roster(), today)
        front = dist_front.read_text(encoding="utf-8")
        if pso and pso.get("name") and pso["name"] not in front:
            hard.append(f"dist/ does not name today's parasocialite "
                        f"({pso['name']})")
        else:
            print("  ok   dist/ names today's parasocialite")

    # 5. what is alive, and what only looks alive
    if origin_is_placeholder():
        warn.append("git origin is the placeholder YOUR-USER/parasocialize - "
                    "the scheduled workflows cannot run until it is a real "
                    "repository")
    age = sweep_age()
    if age is None or age > 2:
        warn.append("the sweeper last ran "
                    f"{'never' if age is None else str(age) + ' days ago'}; "
                    "the material pipeline is asleep")

    for w in warn:
        print(f"  warn {w}")
    if hard:
        for h in hard:
            print(f"  FAIL {h}")
        print(f"\ndaily: RED ({len(hard)} problem(s))")
        return 1
    print("\ndaily: green")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--no-zip", action="store_true")
    ap.add_argument("--zip", default=str(pathlib.Path.home() / "Desktop" /
                                         "parasocialize-SITE.zip"))
    ap.add_argument("--visual", action="store_true")
    ap.add_argument("--skip-gates", action="store_true")
    a = ap.parse_args()

    if a.check:
        return check()

    today = utc_today().isoformat()

    before = sum(len(history_days(p)) for p in HISTORIES.values())
    run("archive", ["archive.py", "--reconcile"])
    after = sum(len(history_days(p)) for p in HISTORIES.values())
    closed = after - before

    run("plan", ["plan_next.py"])
    run("build_cards", ["build_cards.py"])
    run("plate", ["plate.py"])
    run("package", ["build_deploy.py", "--no-build"])

    if not a.skip_gates:
        run("gates: post", ["gates.py", "--post", "--skip", "build_cards",
                            "--skip", "plate", "--skip", "build_deploy"])
        run("gates: source", ["gates.py", "--source"])
        # test_front_copy legitimately rewrites data/front_copy.json, which
        # makes the tree newer than dist/. Re-package before asserting again.
        run("repackage", ["build_deploy.py", "--no-build"])
        if a.visual:
            run("gates: visual", ["gates.py", "--visual"])

    zip_info = {"path": None, "sha": None, "files": None}
    if not a.no_zip:
        out = run("zip", ["make_zip.py", a.zip], capture=True)
        print(out.rstrip())
        m = re.search(r"(\d+) files ->", out)
        s = re.search(r"tree sha256 ([0-9a-f]+)", out)
        zip_info = {"path": a.zip,
                    "sha": s.group(1) if s else None,
                    "files": int(m.group(1)) if m else None}

    files = sum(1 for p in (ROOT / "dist").rglob("*") if p.is_file())
    record = {"_note": (
                  "OPERATIONAL, not editorial history. Overwritten by "
                  "tools/daily.py so the next run can tell whether the loop "
                  "actually ran and what it produced. The archival record is "
                  "data/top8_history.json, data/register_history.json and "
                  "data/parasocialite_history.json - never this file."),
              "last": {"date": today,
                       "at": datetime.datetime.now(
                           datetime.timezone.utc).isoformat(timespec="seconds"),
                       "archive_days_closed": closed,
                       "dist_files": files,
                       "zip": zip_info,
                       "plan_actions": len(json.loads(
                           PLAN.read_text(encoding="utf-8")).get("actions") or [])}}
    RUN_LOG.write_text(json.dumps(record, ensure_ascii=False, indent=1) + "\n",
                       encoding="utf-8")

    # The run record is under data/, and dist_is_fresh() compares data/ mtimes.
    # Package after writing it, or the next gate run would correctly report a
    # stale deploy tree.
    run("final package", ["build_deploy.py", "--no-build"])
    if not a.skip_gates:
        run("final freshness", ["gates.py", "--post", "--skip", "build_cards",
                                "--skip", "plate", "--skip", "build_deploy"])

    rc = check()
    print(f"\ndist: {files} files"
          + (f", zip {zip_info['files']} files, sha {zip_info['sha']}"
             if zip_info["sha"] else ""))
    if closed:
        print(f"archive: closed {closed} missed day(s) as rebuilt, marked on "
              "the record pages")
    return rc


if __name__ == "__main__":
    raise SystemExit(main())
