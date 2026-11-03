"""One command that says which gates run when, and why they are split.

Four checks added this session - `verify_findable.py`, `verify_landmarks.py`,
`md_leak.py` and the `--orphans` mode of `check_css.py` - all read `dist/`, so
none of them can run before `build_deploy.py`, and wiring them into
`link_audit.py` would put a build dependency inside the per-commit gate. AGENTS
records why that is the wrong shape twice: `verify_narrow.py` is "deliberately
not wired into `link_audit.py` - it needs a build and Chrome, and a gate that
runs on every commit is a gate that eventually gets disabled", and the same
argument is given for `probe_nav.py`.

So there are three tiers, and the split is by what a check NEEDS, not by how
important it feels:

  source   no build, no browser        link_audit, citation_audit, cull_audit,
                                      verify_taxonomy, card_audit, image_audit,
                                      check_css, archive, editor,
                                      test_front_copy,
                                      test_register_rotation,
                                      test_parasocialite_rotation
  post     needs dist/, no browser     build_cards, plate, build_deploy
                                      --no-build, then check_css --orphans,
                                      verify_findable, verify_landmarks,
                                      md_leak, check_heads
  visual   needs Chrome and pixels     verify_narrow, probe_nav --check,
                                      probe_hub_contrast

`post` is the default because that is the tier the new checks belong to: they
all read the deployed tree, which is what a reader actually gets. `visual` stays
manual on purpose - AGENTS item 65 records `probe_hub_contrast.py` needing a
fresh profile per render and refusing to report if it cannot find eight tiles,
which is the behaviour of a gate you run deliberately rather than one you inherit
on every commit.

Refuses to run `post` without a fresh `dist/`, because a check that reads a
stale build reports about the wrong tree - which is what made `verify_narrow`
measure an unstyled page and call it a pass.

Run on exit codes throughout. Nothing here filters or greps a gate's output:
`$LASTEXITCODE` after a pipeline measures the pipeline, and this file exists so
that mistake has one place to be avoided.
"""
import pathlib, subprocess, sys, time

ROOT = pathlib.Path(__file__).resolve().parent.parent
TOOLS = ROOT / "tools"
sys.stdout.reconfigure(encoding="utf-8")

SOURCE = [
    ("check_css", ["check_css.py"]),
    ("archive", ["archive.py", "--check"]),
    ("editor", ["editor.py", "--check"]),
    ("affil", ["affil.py", "--check"]),
    ("citation_audit", ["citation_audit.py"]),
    ("cull_audit", ["cull_audit.py"]),
    ("verify_taxonomy", ["verify_taxonomy.py"]),
    ("verify_timeline", ["verify_timeline.py"]),
    ("card_audit", ["card_audit.py"]),
    ("image_audit", ["image_audit.py"]),
    ("test_front_copy", ["test_front_copy.py"]),
    ("test_editor_rotation", ["test_editor_rotation.py"]),
    ("test_register_rotation", ["test_register_rotation.py"]),
    ("test_parasocialite_rotation", ["test_parasocialite_rotation.py"]),
    # A front-page video slot promises that a clip has been chosen and that
    # its timestamp is the moment. `watched` is what makes that true, and
    # this fails on a clip that asserts a timestamp nobody has checked.
    ("clips --check", ["clips.py", "--check"]),
    # The daily engine: same date, same eight; one per category;
    # and the 30-day rule where the pool can supply it.
    ("top8_engine --check", ["top8_engine.py", "--check"]),
    ("link_audit", ["link_audit.py"]),
]

# order matters and is not alphabetical: build_cards generates, plate draws
# from the data, build_deploy copies - running build_deploy before plate makes
# it report 404s on plates that do not exist yet, which is a true report of the
# tree it was given and a false report of the project.
#
# build_deploy now runs those two steps itself, because a packaging command
# that only copies ships whatever day the pages were last generated. This tier
# passes --no-build because it has just run them in this exact order; without
# the flag the post tier would build the site twice, and the second build would
# be the one that appended the day's history.
#
# BUILD and CHECK are separate because the freshness assertion cannot run before
# the build: the first version of this file refused the whole tier because dist/
# was stale, and since the tier's first step is the build that made it
# impossible to ever run - a precondition that can only be satisfied by a step
# the precondition prevented.
POST_BUILD = [
    ("build_cards", ["build_cards.py"]),
    ("plate", ["plate.py"]),
    ("build_deploy", ["build_deploy.py", "--no-build"]),
]
POST_CHECK = [
    ("plate --check", ["plate.py", "--check"]),
    ("check_css --orphans", ["check_css.py", "--orphans"]),
    # Cloudflare Pages stops applying `_redirects` past a threshold that is much
    # lower than its documentation suggests, and does it silently. On 2026-11-01
    # 147 of 255 `/e/` end-card links were 404s live while every gate was green.
    # This asks whether the rules would be APPLIED, not merely written.
    ("check_redirects", ["check_redirects.py"]),
    # Every indexable page the deploy holds must be in sitemap.xml, and every
    # sitemap URL must exist. Two reader pages were missing and nothing noticed,
    # because the sitemap is built from a hand-written list of remembered URLs.
    ("check_sitemap", ["check_sitemap.py"]),
    # Every recorded day must have a dated page, eight items, a
    # canonical URL and a link from the calendar.
    ("check_top8_archive", ["check_top8_archive.py"]),
    ("verify_findable", ["verify_findable.py"]),
    ("verify_landmarks", ["verify_landmarks.py"]),
    ("verify_ways", ["verify_ways.py"]),
    ("md_leak", ["md_leak.py"]),
    # Internal vocabulary in reader-visible prose. Added after /ledger/ shipped
    # reading "...and AGENTS is explicit that this is not a gap" - AGENTS.md is
    # a working file for whoever maintains the repo, and a reader has never
    # heard of it. Same class as the CLERK'S DESK link and the "no free frame
    # exists" note: process vocabulary in front of somebody who cannot follow it.
    # It got past every existing gate because they check links, selectors and
    # counts, and none of them reads prose for words that mean nothing.
    ("internal_leaks", ["check_internal_leaks.py"]),
    # Both feeds must parse as XML. /ledger/feed.xml shipped with an HTML
    # entity in its title, which no RSS reader can resolve, and nothing in
    # this repository was looking at either feed.
    ("feeds", ["check_feeds.py"]),
    # Every deployed page must offer both feeds and the favicon in its head.
    # Eleven pages did not, because unify_heads.py only ever patched
    # build_cards.py - build_atlas.py, build_quiz.py and the 404's own
    # template were never covered, and the hand-written `tip/` page has no
    # generator, so nothing regenerates or checks it. This reads dist/ for
    # that reason: the deployed tree is what a reader actually gets.
    ("check_heads", ["check_heads.py"]),
]

VISUAL = [
    ("verify_narrow", ["verify_narrow.py"]),
    ("probe_nav --check", ["probe_nav.py", "--check"]),
    ("probe_hub_contrast", ["probe_hub_contrast.py"]),
]

TIERS = {"source": SOURCE, "post": POST_CHECK, "visual": VISUAL}
# the steps that must run before the freshness assertion can mean anything
BUILDERS = {"post": POST_BUILD}


def newest_mtime(paths):
    newest = 0.0
    for p in paths:
        try:
            newest = max(newest, p.stat().st_mtime)
        except OSError:
            pass
    return newest


def dist_is_fresh():
    """A gate that reads dist/ must not read a stale build.

    Compared against data/, css/ and js/ - the inputs a human edits - and NOT
    against the generated .html. The first version used the source html and
    refused every time: `test_front_copy.py` "exercises the generator" and
    rewrites index.html and its siblings on every source-tier run, so the tree
    is always seconds newer than dist/ even when the two are byte-identical. A
    precondition that fires on normal operation is a precondition that gets
    deleted. Generated html is not an input signal here because this runner
    rebuilds before it asserts.
    """
    dist = ROOT / "dist"
    if not dist.is_dir():
        return False, "dist/ does not exist - run build_deploy.py"
    d = newest_mtime(dist.rglob("*.html"))
    if not d:
        return False, "dist/ contains no html"
    src = []
    for sub in ("data", "css", "js"):
        p = ROOT / sub
        if p.is_dir():
            src += [f for f in p.rglob("*") if f.is_file()]
    newest = max(src, key=lambda f: f.stat().st_mtime)
    s = newest.stat().st_mtime
    if s > d:
        # Report the file, not the last directory in the loop. Naming `sub`
        # here used the leaked loop variable and pointed at js/ for a file in
        # data/, which sent the reader to the wrong tree entirely.
        return False, (f"{newest.relative_to(ROOT).as_posix()} was changed at "
                       f"{time.strftime('%H:%M:%S', time.localtime(s))}, after "
                       f"dist/ was built at "
                       f"{time.strftime('%H:%M:%S', time.localtime(d))}")
    return True, "dist/ is newer than data/, css/ and js/"


def run(tier, only=None, skip=None):
    failures = []

    def steps_for(label, steps):
        print(f"=== {tier} tier: {label} ===")
        for name, argv in steps:
            if only and name not in only:
                continue
            if skip and name in skip:
                print(f"  skip  {name}")
                continue
            proc = subprocess.run(
                [sys.executable, str(TOOLS / argv[0])] + argv[1:],
                cwd=ROOT, capture_output=True, text=True, errors="replace")
            if proc.returncode == 0:
                print(f"  green {name}")
            else:
                print(f"  RED   {name}  (exit {proc.returncode})")
                # A red gate that prints only its name is a red gate whose
                # reason is in a variable nobody reads. The first CI run of
                # tools/daily.py failed on verify_taxonomy and the log said
                # exactly that and nothing else, which cost a round trip to
                # discover a one-line difference.
                for stream in (proc.stdout, proc.stderr):
                    for line in (stream or "").splitlines():
                        print(f"        {line}")
                failures.append(name)
        print()

    # build first, so the freshness assertion below can be trusted
    if tier in BUILDERS:
        steps_for("build", BUILDERS[tier])

    if tier in ("post", "visual"):
        ok, why = dist_is_fresh()
        if not ok:
            print(f"REFUSING to run the {tier!r} tier: {why}")
            print("The checks in this tier read the deployed tree, and a stale")
            print("build makes them report about a page nobody is shipping.")
            return 2
        print(f"precondition ok: {why}\n")

    steps_for("checks", TIERS[tier])

    if failures:
        print(f"FAIL: {len(failures)} in the {tier} tier: "
              f"{', '.join(failures)}")
        return 1
    print(f"all green: {tier} tier")
    return 0


def main():
    args = sys.argv[1:]
    tier = "post"
    for t in TIERS:
        if f"--{t}" in args:
            tier = t
            args.remove(f"--{t}")
    only, skip = None, []
    i = 0
    while i < len(args):
        a = args[i]
        if a in ("--only", "--skip") and i + 1 < len(args):
            target = args[i + 1]
            if a == "--only":
                only = (only or set()) | {target}
            else:
                skip.append(target)
            args = args[:i] + args[i + 2:]
            continue
        i += 1

    # `--only` is a filter, and a filter that matches nothing must not report
    # success. The first version took one value, so `--only check_css` silently
    # matched nothing against the step named `check_css --orphans` and printed
    # "all green" having run no gate at all - the same fail-open shape as a
    # probe that reports nothing it measured.
    if only:
        known = {n for n, _ in BUILDERS.get(tier, []) + TIERS[tier]}
        unknown = only - known
        if unknown:
            print(f"no step in the {tier!r} tier is named {sorted(unknown)}")
            print(f"available: {sorted(known)}")
            return 2
        print(f"running only: {sorted(only)}\n")

    if "--all" in args:
        # Build FIRST, and run the visual tier before the source tier.
        # `gates.py --all` used to run source -> post -> visual, which meant the
        # source tier checked pages that did not exist yet: any batch that added
        # entries went red on link_audit ("every indexable page has at least one
        # inbound internal link") while the build that would have created them
        # was still three steps away. Same defect as running build_deploy before
        # plate - a true report of the tree it was handed and a false report of
        # the project.
        #
        # The source tier goes last for a second reason: test_front_copy
        # "exercises the generator" and rewrites data/front_copy.json, which
        # legitimately makes data/ newer than dist/ and trips the freshness
        # precondition the visual tier asserts. Asking the browser tier a
        # question after the test has touched the corpus was ordering the same
        # mistake twice.
        rc = 0
        rc = run("post", skip=skip) or rc      # builds, then its own checks
        rc = run("visual", skip=skip) or rc
        rc = run("source", skip=skip) or rc
        return rc
    if "--list" in args:
        for t, steps in TIERS.items():
            print(f"{t}:")
            for n, _ in BUILDERS.get(t, []) + steps:
                print(f"  {n}")
        return 0
    return run(tier, only, skip or None)


if __name__ == "__main__":
    raise SystemExit(main())