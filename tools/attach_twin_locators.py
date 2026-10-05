"""Attach an in-corpus locator to a short-form duplicate of a work already located.

`free-trial-bait` cites Mathur et al. 2019 twice: once in full with
10.1145/3359183, and once as "Mathur et al. (2019)." with nothing. `crossover`,
`siri`, `the-priest`, `congregation`, `the-phone`, `killing-off` and
`gomer-pyle` all do the same thing. That is not a research backlog - the work is
already cited, with a URL, sometimes on the very same entry - so the second
record is asserting a citation whose locator the site has already verified.

Attaching it is not inventing a locator. It is noticing that two records name one
work, which is a judgement about identity, and AGENTS is blunt about what
evidence that judgement needs: letting author plus year be enough made
`keep-it-or-lose-it` MATCH a different paper by the same first author in the same
year, and that paper was then accepted as the citation. **An author and a year
are a pair of coordinates, not a work.**

So only two classes are allowed to write:

  exact   the two citation strings are identical once whitespace and a trailing
          full stop are normalised
  prefix  one is the other plus a subtitle or venue - "Mathur et al. (2019)."
          inside "Mathur et al. (2019). Dark Patterns at Scale."

Anything matched on surname and year alone is printed and left alone.
"""
import json
import pathlib
import re
import sys
from collections import defaultdict

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ROOT = pathlib.Path(r"C:\Users\paras\Documents\Default Project\parasocialize")
APPLY = "--apply" in sys.argv


def norm(c):
    return re.sub(r"\s+", " ", str(c or "")).strip().rstrip(". ").lower()


COMPOUND = re.compile(r";\s|\s&\s|\sand\s+[A-Z]")


def same_work(a, b, url=""):
    na, nb = norm(a), norm(b)
    if not na or not nb:
        return ""
    if na == nb:
        return "exact"
    # A compound citation names more than one work. "CBS News (2016), citing
    # photographs and CBS Minnesota; NPR, Music Legend Prince Dies At Paisley
    # Park" is two sources, and it carries ONE url - the NPR one. A short form
    # that is a prefix of it, "CBS News (2016).", would therefore be handed the
    # wrong outlet's link: a fresh false attribution, which is a worse defect
    # than the honest gap this tool exists to close.
    #
    # That one passed the prefix test on the first run and was caught by reading
    # the pair rather than the match. `cobain` has the same shape - "Seattle
    # Times, 8 April 1994; and Rolling Stone (Neil Strauss)..." - and is only
    # correct by luck, because that url happens to be the Seattle Times one.
    # **Luck is not a rule.**
    if COMPOUND.search(nb):
        return ""
    short, long_ = (na, nb) if len(na) <= len(nb) else (nb, na)
    if len(short) >= 12 and long_.startswith(short):
        if long_[len(short):][:1] in (" ", ".", ",", ":", ";", "-"):
            return "prefix"
    return ""


p = ROOT / "data" / "encyclopedia.json"
enc = json.loads(p.read_text(encoding="utf-8"))
before_records = sum(len(e.get("sources") or []) for e in enc["entries"])
before_entries = len(enc["entries"])
top_keys = sorted(enc)

records = [(e, s) for e in enc["entries"] for s in (e.get("sources") or [])]
located = [(e, s) for e, s in records if str(s.get("url") or "").strip()]

plan = []
for e, s in records:
    if str(s.get("url") or "").strip():
        continue
    cit = str(s.get("citation") or "")
    for te, ts in located:
        how = same_work(cit, ts.get("citation"))
        if not how:
            continue
        same_entry = te["id"] == e["id"]
        # never attach from a record that would become self-referential
        if ts is s:
            continue
        plan.append((e, s, te, ts, how, same_entry))
        break

print(f"{before_records} records; {sum(1 for _, s in records if not str(s.get('url') or '').strip())}"
      f" without a locator")
print(f"{len(plan)} attachable on exact/prefix evidence\n")
for e, s, te, ts, how, same in sorted(plan, key=lambda x: x[0]["id"]):
    where = "SAME ENTRY" if same else f"located on {te['id']}"
    print(f"  {e['id']:<26} {how:<7} {where}")
    print(f"     was : {str(s.get('citation'))[:88]}")
    print(f"     from: {str(ts.get('citation'))[:88]}")
    print(f"     url : {str(ts.get('url'))[:88]}")
    print(f"     claim: {str(s.get('claim') or '')[:84]}")
    print()

if not APPLY:
    print("dry run. re-run with --apply")
    raise SystemExit(0)

touched = 0
for e, s, te, ts, how, same in plan:
    s["url"] = ts["url"]
    # provenance, not invention: say where the locator came from
    s["locator_from"] = (f"{how} match on record citing {str(ts.get('citation'))[:70]!r} "
                         f"on {te['id']}")
    # a locator is not a reading. If the short form said less than the record it
    # is being merged with, it does not become verified by acquiring a URL.
    touched += 1

after_records = sum(len(e.get("sources") or []) for e in enc["entries"])
if after_records != before_records or len(enc["entries"]) != before_entries:
    sys.exit(f"refusing to write: shape changed {before_records}->{after_records}")
if sorted(enc) != top_keys:
    sys.exit("refusing to write: top-level keys changed")

tmp = p.with_suffix(".json.tmp")
tmp.write_text(json.dumps(enc, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
re_parsed = json.loads(tmp.read_text(encoding="utf-8"))
if len(re_parsed["entries"]) != before_entries:
    sys.exit("refusing to write: reparse did not reconcile")
tmp.replace(p)
print(f"attached {touched} locators. records {before_records} unchanged, "
      f"entries {before_entries} unchanged.")
