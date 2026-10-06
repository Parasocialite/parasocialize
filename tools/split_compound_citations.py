"""Split the compound citations in the locator-less backlog, with a guard that
exists because AGENTS already records what happens without it.

Measured first, not assumed: of the 130 records with no locator, **20 are
compound** - one string naming two or three works - and **110 are single-work**.
Of the 20, 13 have a fuller form of their leading work already on the same entry.

**So the split is mostly a deletion of duplication.** In almost every case the
leading work is *already cited separately, with its own locator*, so the compound
is not missing a locator for its first work - it is missing the *other* works,
which have none anywhere. Replacing it with one record per tail work turns "a
record that names three things and locates none" into "N records that each name
one thing and locate none", which is honest and independently workable.

**THE GUARD, and why it is not optional.** `prince` has
`'CBS News (2016), citing The Associated Press.'` with no locator, and on the same
entry `'CBS News (2016), citing photographs and CBS Minnesota; NPR, Music Legend
Prince Dies At Paisley Park'` - **carrying one URL, the NPR one.** AGENTS item 28
records exactly this: a compound sibling's single URL belongs to ONE of the works
it names, and handing it to a record naming a different one is "a fresh false
attribution, worse than the honest gap the tool exists to close". So:

  - a parent that is ITSELF compound is refused, because its one URL cannot be
    attributed to the leading work;
  - a child work gets a locator only if the corpus already holds a record naming
    it under an author-and-year match, and then the URL is COPIED, never typed;
  - every child that cannot be located is written `needs-source` with a claim
    saying it is named but not identified - which is what that status means.

**A second guard, from the same item: an author and a year are a pair of
coordinates, not a work.** So a child match needs a surname AND the year, and
the match is reported rather than trusted blindly. Item 21's `keep-it-or-lose-it`
incident is what that rule exists to prevent.

Asserts entry count, that the record count cannot fall, and the top-level keys.
"""
import json
import pathlib
import re
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ROOT = pathlib.Path(__file__).resolve().parent.parent
APPLY = "--apply" in sys.argv
p = ROOT / "data" / "encyclopedia.json"
enc = json.loads(p.read_text(encoding="utf-8"))

before_entries = len(enc["entries"])
before_records = sum(len(e.get("sources", [])) for e in enc["entries"])
before_keys = sorted(enc)

CUT = re.compile(r"[,;]?\s*citing\s|,?\s*quoted in\s|;\s*see also\s", re.I)
COMPOUNDISH = re.compile(r"\bciting\b|\bquoted in\b|;\s*NPR\b", re.I)


def norm(c):
    return re.sub(r"\s+", " ", c).strip().rstrip(".").lower()


# Editorial tails that rode along inside the citation string. Stripped
# deliberately and listed explicitly rather than by pattern, because a
# hand-written list is auditable and a heuristic is not - and the untouched
# original is preserved in each child's `split_from`, so nothing is lost.
TAILS = (
    "taxonomy", "on perceived one-way interaction", "on perceived one-way",
    "pattern originally", "originally", "and its afterlives",
)
# The same editorial words appear at the START of a child after the split, where
# they read as part of the citation: "pattern originally Brignull's Roach Motel."
# `clean()` stripped them only from the end, so this list is the leading case.
LEADING = ("pattern originally", "quoting", "originally", "cited as",
           "taxonomy")
# Stray brackets left by cutting mid-parenthetical.
BRACKETS = re.compile(r"[\[\]()]+")


def clean(work):
    """A child citation stripped of the editorial tail it inherited."""
    w = work.strip().rstrip(".;,")
    low = w.lower()
    for t in LEADING:
        if low.startswith(t):
            w = w[len(t):].strip().lstrip(",; ").strip()
            low = w.lower()
    for t in TAILS:
        if low.endswith(t):
            w = w[:len(w) - len(t)].strip()
            low = w.lower()
    w = w.strip().rstrip(",;")
    # a trailing unbalanced paren is an artefact of the cut, not part of a name
    while w.endswith(")") and w.count(")") > w.count("("):
        w = w[:-1].rstrip()
    return w


def child_cites(tail):
    t = re.sub(r"^citing\s+", "", tail.strip().rstrip(".").strip(), flags=re.I)
    out = []
    for x in re.split(r"\s+and\s+|;\s*", t):
        c = clean(x)
        if len(c) > 3 and not BRACKETS.fullmatch(c):
            out.append(c)
    return out


# No auto-location. AGENTS item 28 records that an author and a year are "a pair
# of coordinates, not a work", and `verify_doi.py` was changed to refuse a match
# without title evidence for exactly this reason. The first version of this block
# substring-matched surname and year, and reported 'Aw & Chua (2021)' as
# `retrievable` because some record contained both characters anywhere - and
# 'Horton & Wohl (1956)' likewise. A child string with no title in it cannot be
# matched against a title, so every child is `needs-source`. That is the honest
# state, and it is still a large improvement: one string naming three works
# becomes three strings each naming one, so each can be worked.
def locate(work):
    return None, ("no title or DOI in the child citation, so the work cannot be "
                  "distinguished from its neighbours - and an author-and-year "
                  "match is a pair of coordinates, not a work")


print("== compound records: what happens to each ==")
plan, refused = [], []

for e in enc["entries"]:
    eid = e["id"]
    for r in list(e["sources"]):
        c = r.get("citation", "")
        if r.get("url"):
            continue
        if not re.search(r"\bciting\b|\bquoted in\b|;\s*see also\b", c, re.I):
            continue
        head = CUT.split(c, maxsplit=1)
        if len(head) != 2:
            refused.append((eid, c, "no clean cut point"))
            print(f"  [{eid}] SKIP  - no clean cut point")
            continue
        lead, tail = head[0].strip(), head[1].strip()

        parent = None
        for other in e["sources"]:
            if other is r:
                continue
            if norm(other.get("citation", "")).startswith(norm(lead)[:26]):
                parent = other
                break
        if parent is None or not parent.get("url"):
            refused.append((eid, c, "leading work is not separately located"))
            print(f"  [{eid}] SKIP  - leading work has no separate locator")
            continue

        if COMPOUNDISH.search(parent.get("citation", "")):
            refused.append((eid, c, "parent is itself compound; its one URL "
                                   "belongs to a different work"))
            print(f"  [{eid}] REFUSE - parent is compound")
            print(f"       parent    : {parent.get('citation', '')[:86]!r}")
            print(f"       parent url: {parent.get('url')!r}")
            print(f"       ours      : {c[:86]!r}")
            continue

        children = []
        for w in child_cites(tail):
            url, why = locate(w)
            rec = {
                "citation": w + ".",
                "status": "retrievable" if url else "needs-source",
                "url": url,
                "locator": None,
                # `citation_audit.py` caught this: the first version of this
                # block wrote `identity_verified` and `split_from` and no
                # `claim`, and the gate failed with "13 record(s) print a
                # placeholder where a claim should be". Correct - a record with
                # an empty claim is a field promising something it does not
                # keep, which is the family this project keeps meeting.
                "claim": (
                    f"Named inside a compound citation that also named "
                    f"{lead[:70]!r}, which is cited separately on this entry "
                    f"and carries its own locator. This work is recorded on its "
                    f"own so that one string is not standing in for several. "
                    f"It has NOT been identified here - no title, no venue, no "
                    f"locator - and nothing is claimed about what it says."
                ),
                "split_from": c,
            }
            if url:
                rec["locator_from"] = "split-of-compound:same-work"
                rec["identity_verified"] = (
                    "URL copied from a record already in the corpus naming this "
                    "work under an author-and-year match; identity NOT "
                    "re-checked here")
            else:
                rec["identity_verified"] = (
                    f"NO locator, work not identified: {why}. This record "
                    f"exists because the compound string it came from named a "
                    f"second work inside one citation, which is a defect by "
                    f"itself")
            children.append(rec)
        if not children:
            refused.append((eid, c, "tail yielded no parseable child work"))
            print(f"  [{eid}] SKIP  - tail yielded nothing parseable")
            continue
        plan.append((eid, c, children))
        print(f"  [{eid}] SPLIT into {len(children)}")
        print(f"       leading : {lead[:64]!r}, already located as")
        print(f"                {parent.get('citation', '')[:78]!r}")
        for ch in children:
            print(f"       child   : [{ch['status']:>12}] {ch['citation'][:58]!r}")

added = sum(len(ch) for _, _, ch in plan)
print(f"\n  {len(plan)} compounds -> {added} single-work children")
print(f"  refused or skipped: {len(refused)}")
for eid, c, why in refused:
    print(f"    [{eid}] {why}")
    print(f"       {c[:86]!r}")

if not APPLY:
    print("\ndry run. re-run with --apply")
    raise SystemExit(0)

by_eid = {e["id"]: e for e in enc["entries"]}
for eid, c, children in plan:
    recs = by_eid[eid]["sources"]
    j = next(k for k, r in enumerate(recs)
             if r.get("citation") == c and not r.get("url"))
    recs[j:j + 1] = children
    by_eid[eid]["sources"] = recs

after_records = sum(len(e.get("sources", [])) for e in enc["entries"])
if len(enc["entries"]) != before_entries:
    sys.exit(f"refusing: entry count moved {before_entries}->{len(enc['entries'])}")
if after_records < before_records:
    sys.exit(f"refusing: record count fell {before_records}->{after_records}")
if sorted(enc) != before_keys:
    sys.exit("refusing: top-level keys changed")

second = p.read_text(encoding="utf-8").split("\n")[1]
indent = len(second) - len(second.lstrip()) or 1
tmp = p.with_suffix(".json.tmp")
tmp.write_text(json.dumps(enc, ensure_ascii=False, indent=indent) + "\n",
               encoding="utf-8")
re_parsed = json.loads(tmp.read_text(encoding="utf-8"))
if sum(len(e.get("sources", [])) for e in re_parsed["entries"]) != after_records:
    sys.exit("refusing: reparse did not reconcile")
tmp.replace(p)

print(f"\nwritten at indent={indent}. entries {before_entries} (unchanged), "
      f"records {before_records} -> {after_records}.")
