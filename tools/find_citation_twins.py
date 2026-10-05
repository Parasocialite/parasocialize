"""Find citation records that cite a work another record already locates.

148 records carry no locator, and the first honest look at them says they are not
148 missing research tasks. A large share are a *second claim from a work the
same entry already cites with a URL*: `free-trial-bait` cites Mathur et al. 2019
twice, once with the DOI and once as "Mathur et al. (2019)." with nothing;
`loyalty-dark-pattern` does it three times over. Those do not need a locator
found - they need the locator the corpus already verified, attached.

The matching has to be strict, because AGENTS records the failure of the loose
version. Letting author+year be enough made `keep-it-or-lose-it` MATCH a
different paper with the same first author and the same year, and that paper was
then accepted as the citation. **An author and a year are a pair of coordinates,
not a work.**

So this only matches on evidence that cannot coincide across two different
papers:

  exact      the two citation strings are identical after normalising whitespace
             and a trailing full stop
  prefix     one normalised string is the other plus a subtitle or a venue
             continuation - "Mathur et al. (2019)." inside "Mathur et al. (2019).
             Dark Patterns at Scale."
  id         the same DOI or the same arXiv id appears in both

Report only. Applying a locator to a citation is an editorial act and
add_source.py is the path for it; this prints candidates so a person can look.
"""
import json
import pathlib
import re
import sys
from collections import defaultdict

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ROOT = pathlib.Path(r"C:\Users\paras\Documents\Default Project\parasocialize")
APPLY = "--apply" in sys.argv

DOI = re.compile(r"\b(10\.\d{4,9}/[^\s,;)\]]+)", re.I)
ARXIV = re.compile(r"\b((?:arXiv:)?\d{4}\.\d{4,5}(?:v\d+)?)\b", re.I)


def norm(cit: str) -> str:
    c = re.sub(r"\s+", " ", str(cit or "")).strip()
    return c.rstrip(". ").lower()


def ids_in(text: str) -> set:
    out = set()
    out |= {"doi:" + m.rstrip(".,;)]").lower() for m in DOI.findall(text or "")}
    out |= {"arxiv:" + m.lower().lstrip("arxiv:") for m in ARXIV.findall(text or "")}
    return out


def same_work(a: str, b: str) -> str:
    """Return how we know they are the same work, or '' if we do not."""
    na, nb = norm(a), norm(b)
    if na and na == nb:
        return "exact"
    ia, ib = ids_in(a), ids_in(b)
    if ia & ib:
        return "id:" + sorted(ia & ib)[0]
    # prefix: one is the other plus a subtitle or a venue continuation -
    # "Mathur et al. (2019)." inside "Mathur et al. (2019). Dark Patterns at
    # Scale.".
    #
    # The boundary test has to allow the separator, not just a space. norm()
    # strips the trailing full stop, so after stripping the short form the
    # remainder begins ". dark patterns at scale" - testing `nxt[:1].isspace()`
    # therefore failed on every case of exactly the shape this class exists for,
    # and the first run reported 3 matches when there are more. **A filter that
    # only fires on the easy half of its own stated rule is a filter that looks
    # like it is working.**
    if na and nb:
        short, long_ = (na, nb) if len(na) <= len(nb) else (nb, na)
        if long_.startswith(short) and len(short) >= 12:
            nxt = long_[len(short):]
            if nxt[:1] in (" ", ".", ",", ":", ";", "-"):
                return "prefix"
    return ""


enc = json.loads((ROOT / "data" / "encyclopedia.json").read_text(encoding="utf-8"))
records = [(e["id"], s) for e in enc["entries"] for s in (e.get("sources") or [])]

located = [(eid, s) for eid, s in records if str(s.get("url") or "").strip()]
unlocated = [(eid, s) for eid, s in records if not str(s.get("url") or "").strip()]

print(f"{len(records)} records: {len(located)} with a locator, "
      f"{len(unlocated)} without\n")

# index located records by their normalised citation and by any id they carry
by_norm = defaultdict(list)
by_id = defaultdict(list)
for eid, s in located:
    c = str(s.get("citation") or "")
    by_norm[norm(c)].append((eid, s))
    for i in ids_in(c) | ids_in(str(s.get("url") or "")):
        by_id[i].append((eid, s))

matches = []
for eid, s in unlocated:
    cit = str(s.get("citation") or "")
    if not norm(cit):
        continue
    hits = []
    for teid, ts in by_norm.get(norm(cit), []):
        if teid != eid:
            hits.append(("exact", teid, ts))
    for i in (ids_in(cit)):
        for teid, ts in by_id.get(i, []):
            if teid != eid and all(h[1] != teid for h in hits):
                hits.append(("id", teid, ts))
    for teid, ts in located:
        if teid == eid or any(h[1] == teid for h in hits):
            continue
        if same_work(cit, str(ts.get("citation") or "")):
            hits.append(("prefix", teid, ts))
    if hits:
        matches.append((eid, s, hits))

print(f"=== {len(matches)} unlocated records cite a work the corpus locates ===\n")
by_entry = defaultdict(int)
for eid, s, hits in matches:
    by_entry[eid] += 1

for eid, s, hits in matches:
    cit = str(s.get("citation") or "")
    print(f"  {eid}  ({len(s.get('status') and [1] or [1])} record)")
    print(f"     citation : {cit[:96]}")
    print(f"     status   : {s.get('status')}")
    print(f"     claim    : {str(s.get('claim') or '')[:96]}")
    for how, teid, ts in hits[:3]:
        same = "SAME ENTRY" if teid == eid else f"on {teid}"
        print(f"     match by {how:<28} {same}")
        print(f"        url : {str(ts.get('url'))[:92]}")
    print()

print(f"across {len(by_entry)} entries:")
for k, v in sorted(by_entry.items(), key=lambda kv: -kv[1])[:14]:
    print(f"  {k:<28} {v}")

if APPLY:
    print("\n--apply does nothing on purpose: attaching a locator to a citation is")
    print("an editorial act and tools/add_source.py is the path for it. This tool")
    print("exists to make the candidates visible, not to write them.")
