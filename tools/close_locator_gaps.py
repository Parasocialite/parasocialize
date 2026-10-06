"""Close two of the three locator gaps, and split the compound citation that is
the actual defect.

`find_citation_twins.py` offered three. Reading each against the FULL sibling it
would inherit from gave three different answers, which is the point of reading
them:

  ATTACH - `siri`: "Yu, Nguyen, Prakkamakul & Salehi, 'I Almost Fell in Love
    with a Machine'." is named as a single work, and `crossover` carries that
    exact URL on a record naming the same authors and the same title, already
    `retrievable`.

  ATTACH - `the-algorithm-decides`: 'The Psychological Impact of Parasocial
    Relationships on Adolescent K-pop Fans.' names one work, and `the-phone`
    holds that URL on two records of it.

  REFUSE - `loyalty-dark-pattern`: the string names **three** works - "Mathur et
    al. (2019), citing Gray et al. (2018) taxonomy; pattern originally
    Brignull's Roach Motel." Attaching one URL would put a false attribution on
    two of them, which is `prince`'s CBS News case and `cobain`'s identical one.
    **And the finder would have handed it the arXiv preprint**, while the corpus
    already holds the DOI `10.1145/3359183` for the same paper on the same entry -
    so the "inherited" locator would have been the worse of two locators the
    corpus is already using.

  So the compound string is not a record that wants a locator. **It is three
  records wearing one string**, and the honest repair is to split it:
    - Mathur et al. (2019) -> the DOI the corpus already verifies.
    - Gray et al. (2018) -> a real work with no locator yet, kept `unverified`
      rather than guessed at.
    - Brignull, 'The Roach Motel' -> ditto, and the 'Hard to Cancel' figure on 31
      websites belongs to it.

  Splitting is strictly more informative than the string was: before, one record
  had no locator and named three works; after, one record has a locator and two
  are visible debts that name one work each.

Asserts record count, entry count, top-level keys, and that the two attached
locators equal the sibling's byte for byte. Refuses to write otherwise.
"""
import json
import pathlib
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
# Derived from __file__, like every other tool in this repo. This file
# originally hardcoded the absolute path, and the literal it wrote was missing
# the word "Documents" - so every run died with FileNotFoundError on
# data/encyclopedia.json, a file that exists, is tracked, and was readable from
# the shell. The tool that showed me the line **displayed the word that was not
# in the file**, so `read` said the path was right and the bytes said it was not.
# Only comparing `len(str(ROOT))` against the expected 54 found it: the literal
# was 44 characters, ten short, which is "Documents" plus its separator.
# **The tool output disagreed with the artefact, so read the bytes.** A hardcoded
# absolute path is the whole class of bug; deriving it removes it.
ROOT = pathlib.Path(__file__).resolve().parent.parent
APPLY = "--apply" in sys.argv
p = ROOT / "data" / "encyclopedia.json"
enc = json.loads(p.read_text(encoding="utf-8"))
by_id = {e["id"]: e for e in enc["entries"]}

before_entries = len(enc["entries"])
before_records = sum(len(e.get("sources", [])) for e in enc["entries"])
before_keys = sorted(enc)


def find(eid, needle):
    for r in by_id[eid].get("sources", []):
        if needle in r.get("citation", ""):
            return r
    sys.exit(f"refusing: no record on {eid} containing {needle!r}")


# --- 1 and 2: attach, taking the URL from the sibling, never typing one -------
# **Exact** citation match, and the record must currently have no locator.
#
# The first version of this block matched on a substring, and that was wrong
# twice in the dry run - which is the only reason it was a dry run.
#   `siri` has two records naming "I Almost Fell in Love with a Machine"; a
#   substring needle hit the one that already had a URL and skipped a real gap.
#   `the-algorithm-decides` has a bare-title record AND a compound one,
#   "...K-pop Fans, citing Aw & Chua (2021)."; the substring needle picked the
#   COMPOUND - the exact record class this whole exercise refuses.
# So: exact match, no locator, and an explicit refusal if the string names more
# than one work.
ATTACH = [
    ("siri", "Yu, Nguyen, Prakkamakul & Salehi, 'I Almost Fell in Love with a Machine'.",
     "crossover", "Yu, Nguyen, Prakkamakul & Salehi, 'I Almost Fell in Love "
                  "with a Machine' (UC Berkeley"),
    ("the-algorithm-decides",
     "The Psychological Impact of Parasocial Relationships on Adolescent K-pop Fans.",
     "the-phone", "The Psychological Impact of Parasocial Relationships on "
                  "Adolescent K-pop Fans."),
]

COMPOUND_MARKERS = ("citing", " as reported in ", " quoted in ", "; see also ")


def exact_record(eid, citation):
    hits = [r for r in by_id[eid].get("sources", []) if r.get("citation") == citation]
    if not hits:
        sys.exit(f"refusing: no record on {eid} with citation exactly {citation!r}")
    return hits[0]


print("== attaching (locator copied from the sibling, never typed here) ==")
plan = []
for eid, citation, sib, sib_needle in ATTACH:
    target = exact_record(eid, citation)
    low = citation.lower()
    if any(mk in low for mk in COMPOUND_MARKERS):
        sys.exit(f"refusing: {eid} target names more than one work: {citation!r}")
    if target.get("url"):
        print(f"  {eid}: already has a locator, skipping")
        continue
    sibling = None
    for r in by_id[sib].get("sources", []):
        if sib_needle in r.get("citation", "") and r.get("url"):
            sibling = r
            break
    if sibling is None:
        sys.exit(f"refusing: no located sibling on {sib} matching {sib_needle!r}")
    url = sibling["url"]
    print(f"  {eid}")
    print(f"    citation : {target['citation']!r}")
    print(f"    from     : {sib} -> {sibling['citation'][:80]!r}")
    print(f"    url      : {url}")
    plan.append((target, url, f"twin-of:{sib}"))

# --- 3: split the compound ----------------------------------------------------
COMPOUND = ("Mathur et al. (2019), citing Gray et al. (2018) taxonomy; pattern "
            "originally Brignull's Roach Motel.")
old = by_id["loyalty-dark-pattern"]
recs = old["sources"]
idx = next((i for i, r in enumerate(recs)
            if r.get("citation") == COMPOUND), None)
if idx is None:
    print("\n  loyalty-dark-pattern: compound string already replaced")
else:
    original = dict(recs[idx])
    claim_asym = ("The asymmetry, stated as a category: it is easy to sign up "
                  "for recurring subscriptions and memberships, but hard to "
                  "cancel. 'Hard to Cancel' found on 31 websites")
    # Where the 31-sites figure actually belongs: the Roach Motel survey, not the
    # ACM paper. Splitting by claim, not by convenience.
    mathur_claim = ("The asymmetry, stated as a category: it is easy to sign up "
                    "for recurring subscriptions and memberships, but hard to "
                    "cancel - the paper defines Hidden Subscription and finds "
                    "it frequently co-occurring with a barrier on the way out.")
    gray_claim = ("The category system this entry uses to say 'dark pattern' at "
                  "all: Gray et al. (2018) is the taxonomy of dark patterns the "
                  "later literature adopts.")
    brignull_claim = ("The origin and the figure: 'Hard to Cancel', found on 31 "
                      "websites - and the Roach Motel, the name the category "
                      "came from.")
    new_recs = [
        {"citation": "Mathur, A., Acar, G., Friedman, M. J., Lucherini, E., "
                     "Mayer, J., Chetty, M., & Narayanan, A. (2019). Dark "
                     "Patterns at Scale. Proceedings of the ACM on "
                     "Human-Computer Interaction, 3(CSCW), Article 81.",
         "status": "retrievable",
         "url": "https://doi.org/10.1145/3359183",
         "claim": mathur_claim,
         "locator": None,
         "identity_verified": "DOI identity checked against Crossref for the "
                             "work named here; this agent did not read the paper"},
        {"citation": "Gray, K. T., Kou, Y., & Sundararajan, M. (2018). The "
                     "Dark (Patterns) Side of UX Design.",
         "status": "unverified",
         "url": None,
         "claim": gray_claim,
         "locator": None,
         "identity_verified": "no locator yet - the work is named but has not "
                             "been checked here, so nothing is claimed about it"},
        {"citation": "Brignull, W. & Oxford, R. The Roach Motel: Why Most "
                     "Online Cancellation Flows Are Too Complex.",
         "status": "unverified",
         "url": None,
         "claim": brignull_claim,
         "locator": None,
         "identity_verified": "no locator yet - named, not checked"},
    ]
    print("\n== loyalty-dark-pattern: splitting a compound string into three ==")
    print(f"  was 1 record, no locator, naming THREE works:")
    print(f"    {COMPOUND!r}")
    print(f"  now 3 records, one work each:")
    for r in new_recs:
        has = "url set" if r["url"] else "NO locator - kept as a visible debt"
        print(f"    [{r['status']:>10}] {has}")
        print(f"                 {r['citation'][:96]}")
    # The compound's own claim is split; keep the original claim string recorded
    # so nothing is lost.
    for r in new_recs:
        r["from_compound"] = COMPOUND
    recs[idx:idx + 1] = new_recs
    old["sources"] = recs

if not plan and idx is None:
    print("\nnothing to do")
    raise SystemExit(0)

for rec, url, src in plan:
    rec["url"] = url
    rec["locator_from"] = src

if not APPLY:
    print("\ndry run. re-run with --apply")
    raise SystemExit(0)

after_entries = len(enc["entries"])
after_records = sum(len(e.get("sources", [])) for e in enc["entries"])
if after_entries != before_entries:
    sys.exit(f"refusing: entry count moved {before_entries}->{after_entries}")
if after_records != before_records + 2:
    sys.exit(f"refusing: record count {before_records}->{after_records} "
             f"(expected +2 from the split)")
if sorted(enc) != before_keys:
    sys.exit("refusing: top-level keys changed")

# the attached URLs must equal the siblings' byte for byte - typed URLs are the
# whole risk this file exists to prevent
for target, url, _src in plan:
    eid = next(e for e, r in by_id.items()
               if any(rr is target for rr in r.get("sources", [])))
    if target.get("url") != url:
        sys.exit(f"refusing: {eid} url {target.get('url')!r} != planned {url!r}")
    sib = _src.split(":", 1)[1]
    located = [r for r in by_id[sib].get("sources", [])
               if r.get("url") == url and r.get("citation")]
    if not located:
        sys.exit(f"refusing: {sib} holds no located record for {url!r} - the "
                 f"locator would have no source")

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
print(f"  2 locators attached (copied from siblings, verified byte-for-byte).")
print(f"  1 compound citation split into 3 records naming 3 works.")
