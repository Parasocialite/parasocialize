"""Attach locators to 13 records whose work the corpus already locates - each
one decided by reading the sibling, not by a similarity score.

`find_citation_twins.py` uses exact/prefix string rules and found 3. Relaxing to
author+year+overlap finds **25 candidates**. Reading all 25 splits them cleanly,
and the split is the whole value of this file: **13 are the same work and 12 are
not**, and no score would have told them apart.

ATTACH (same work, named by the sibling unambiguously):
  - `Horton & Wohl (1956)` on `ai-companion` -> the DOI the corpus already holds
    for the founding citation of the whole site. Also the reverse case on
    `parasocial-interaction`, whose own record carries a *different title* for
    the same DOI - "Mass communication and para-social interaction" against
    "Mass Communication and Social Interaction". Same authors, same year, same
    DOI; the discrepancy is recorded rather than smoothed over, because item 20's
    rule is that author and year decide and the title corroborates.
  - the `Garcia v. Character Technologies` order, on two entries, from the fuller
    record on `characterai`.
  - `Rain & Mar (2021)` -> the full citation and PMC URL on the same entry.
  - `Malik & Haidar (2020)`, `Brubaker, Hargittai & Burgess (2013)`,
    `Marwick (2021)` x2, and `Stoking the Flames` -> DOIs already in the corpus.
  - `Staying at the Roach Motel (2024)` -> the arXiv record on the same entry.
  - the CBC News piece on `grief-extraction`, where the target adds "reporting
    Lachman and media lawyer Iain MacKinnon" - that names **interviewees inside
    one article**, not a second work.
  - `Seattle Times, 8 April 1994` x2 on `cobain`. **This is the one judgement
    call**, and it is allowed only because the URL itself settles it: the
    sibling is compound ("Seattle Times...; and Rolling Stone (Neil Strauss)")
    carrying one URL, and that URL is `archive.seattletimes.com/.../nirvanas-
    cobain-dead...`, so host and path both belong to the leading work. That is
    positive evidence of attribution, which is exactly what `prince` lacked -
    an `npr.org` URL on a CBS citation could not be resolved that way.

REFUSE, and why - each of these would have been a false attribution:
  - `cobain` "Tower Records' Chris Simmons, quoted in Billboard (2019)": the
    sibling Billboard URL is Borzillo's retrospective, not Tower Records'
    statement, and the dates differ (23 April 1994 against "April 1994").
  - `cobain` "Borzillo, Billboard (2019); Rolling Stone (1994)": compound, one
    Billboard URL, two outlets.
  - `prince` "Melody Chestler, interviewed by Minnesota Public Radio, reported
    in NPR (2016)": the sibling URL is a *different* NPR piece.
  - `live-commentary` Regelbrugge (2024): **no sibling mentions Regelbrugge at
    all**; the overlaps were on the words "parasocial relationships" only. This
    is what an author+year+overlap match looks like when it is wrong.

Every URL is COPIED from the sibling, never typed, and asserted to equal it.
"""
import json
import pathlib
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ROOT = pathlib.Path(__file__).resolve().parent.parent
APPLY = "--apply" in sys.argv
p = ROOT / "data" / "encyclopedia.json"
enc = json.loads(p.read_text(encoding="utf-8"))
by_id = {e["id"]: e for e in enc["entries"]}

before_entries = len(enc["entries"])
before_records = sum(len(e.get("sources", [])) for e in enc["entries"])
before_keys = sorted(enc)

# (entry, exact target citation, sibling entry, substring of the sibling's
#  citation, why this sibling is the same work)
ALLOW = [
    ("ai-companion", "Horton & Wohl (1956).", "parasocial-interaction",
     "Horton, D., & Wohl, R. R. (1956)",
     "both authors and the year, and it is the only Horton & Wohl record in "
     "the corpus; the DOI is the founding citation of the term this site is "
     "named for"),
    ("parasocial-interaction",
     "Horton, D., & Wohl, R. R. (1956). Mass communication and para-social "
     "interaction: Observations on intimacy at a distance. Psychiatry, 19(3), "
     "215-229.",
     "parasocial-interaction", "Horton, D., & Wohl, R. R. (1956)",
     "SAME authors, SAME year and the SAME DOI as the sibling, but the two "
     "records carry DIFFERENT TITLES for it - 'Mass communication and "
     "para-social interaction' against 'Mass Communication and Social "
     "Interaction'. Item 20's rule applies: author and year decide, the title "
     "corroborates, and a registry and a citation routinely disagree about "
     "titles. The discrepancy is recorded on the record, not smoothed away."),
    ("characterai",
     "Garcia v. Character Technologies, Inc., Order on Motions to Dismiss "
     "(M.D. Fla. 2025).",
     "characterai", "Garcia v. Character Technologies, Inc., Order on Motions",
     "same case, same court, same order; the sibling adds the docket date"),
    ("characterai-lawsuits",
     "Garcia v. Character Technologies, Inc., Order on Motions to Dismiss "
     "(M.D. Fla. 2025), First Amendment discussion.",
     "characterai", "Garcia v. Character Technologies, Inc., Order on Motions",
     "same case and same order; 'First Amendment discussion' names a section "
     "of that order, not a second work"),
    ("characters-move-in", "Rain & Mar (2021).", "characters-move-in",
     "Rain, M., & Mar, R. A. (2021)",
     "same two authors and the same year, on the same entry; the sibling has "
     "the full title and a PMC locator"),
    ("congregation",
     "Malik, Z., & Haidar, S. (2020). Interactive Learning Environments, "
     "31(2).", "congregation",
     "Malik, Z., & Haidar, S. (2020). Online community development",
     "same two authors, same year, same journal - the target is the short form "
     "of the sibling and is on the same entry"),
    ("digital-bereavement", "Brubaker, Hargittai & Burgess (2013).",
     "digital-bereavement", "Brubaker, J. R., Hargittai, E., & Burgess, J. (2013)",
     "all three surnames and the same year, on the same entry; the sibling "
     "carries the full title and a DOI"),
    ("loyalty-dark-pattern", "Staying at the Roach Motel (2024).",
     "loyalty-dark-pattern", "Staying at the Roach Motel",
     "identical title on the same entry; the sibling has the arXiv locator"),
    ("mob-and-internet-pile", "Marwick, A. E. (2021). Social Media Society, "
     "7(2).", "mob-and-internet-pile",
     "Marwick, A. E. (2021). Morally Motivated Networked Harassment",
     "same author, same year, same journal and volume; the sibling has the "
     "title and a DOI"),
    ("mob-and-internet-pile", "Marwick, A. E. (2021), Social Media Society, "
     "7(2).", "mob-and-internet-pile",
     "Marwick, A. E. (2021). Morally Motivated Networked Harassment",
     "as above - a second short-form record of the same paper on the same "
     "entry"),
    ("mob-and-internet-pile",
     "Stoking the Flames: Understanding Escalation in an Online Harassment "
     "Community (ACM CSCW 2024), analysis of 100 takedown request threads.",
     "mob-and-internet-pile", "Stoking the Flames: Understanding Escalation",
     "identical title and year; the sibling carries the CSCW proceedings and a "
     "DOI"),
    ("grief-extraction",
     "Dead celebrities are being digitally resurrected. CBC News (2021), "
     "reporting Lachman and media lawyer Iain MacKinnon.",
     "grief-extraction", "Dead celebrities are being digitally resurrected. "
     "CBC News (2021).",
     "the same article: 'reporting Lachman and media lawyer Iain MacKinnon' "
     "names INTERVIEWEES inside one piece, not a second work. This is the "
     "case a compound detector must not split."),
    ("cobain", "Seattle Times, 8 April 1994.", "cobain",
     "Seattle Times, 8 April 1994; and Rolling Stone (Neil Strauss)",
     "JUDGEMENT CALL, allowed on positive evidence: the sibling is compound and "
     "carries ONE url, but that url is archive.seattletimes.com/.../nirvanas-"
     "cobain-dead... so both its host and its path belong to the leading work. "
     "That is attribution evidence of a kind `prince` did not have - there, "
     "an npr.org url on a CBS citation could not be resolved this way."),
    ("cobain", "Seattle Times, 8 April 1994, reporting Laura Mitchell.",
     "cobain", "Seattle Times, 8 April 1994; and Rolling Stone (Neil Strauss)",
     "as above; 'reporting Laura Mitchell' names a source inside the same "
     "article"),
]


def find_exact(eid, citation):
    hits = [r for r in by_id[eid].get("sources", []) if r.get("citation") == citation]
    if not hits:
        sys.exit(f"refusing: no record on {eid} exactly {citation[:70]!r}")
    return hits[0]


print(f"== attaching {len(ALLOW)} locators, each from a read sibling ==\n")
plan = []
for eid, cit, sib, sib_needle, why in ALLOW:
    target = find_exact(eid, cit)
    if target.get("url"):
        print(f"  [{eid}] already located, skipping")
        continue
    sibs = [r for r in by_id[sib].get("sources", [])
            if sib_needle in r.get("citation", "") and r.get("url")]
    if not sibs:
        sys.exit(f"refusing: no located sibling on {sib} matching {sib_needle!r}")
    if len({r["url"] for r in sibs}) > 1:
        sys.exit(f"refusing: siblings on {sib} disagree about the url for "
                 f"{sib_needle!r} - cannot pick one")
    url = sibs[0]["url"]
    print(f"  [{eid}] {cit[:74]!r}")
    print(f"      url  : {url}")
    print(f"      why  : {why[:150]}")
    plan.append((target, url, f"sibling-read:{sib}", why))

print(f"\n== refused, and these would each have been a false attribution ==")
for eid, cit, why in (
    ("cobain", "Tower Records' Chris Simmons, quoted in Billboard (2019), April 1994.",
     "the sibling Billboard url is Borzillo's retrospective, not Tower Records' "
     "statement, and the dates differ (23 April 1994 against 'April 1994')"),
    ("cobain", "Borzillo, Billboard (2019); Rolling Stone (1994).",
     "compound: two outlets named, one Billboard url carried"),
    ("prince", "Melody Chestler, interviewed by Minnesota Public Radio, "
     "reported in NPR (2016).",
     "the sibling url is a DIFFERENT NPR piece ('Music Legend Prince Dies')"),
    ("live-commentary",
     "Correlations between Twitch's interaction features and parasocial "
     "relationships and streamer influence (Regelbrugge, 2024).",
     "NO sibling mentions Regelbrugge at all - the overlap was on the words "
     "'parasocial relationships' only. This is what an author+year+overlap "
     "match looks like when it is wrong."),
):
    r = find_exact(eid, cit) if cit in {x.get("citation") for x in by_id[eid].get("sources", [])} else None
    status = "already located" if (r and r.get("url")) else "left locator-less"
    print(f"  [{eid}] {status}: {why}")

if not APPLY:
    print("\ndry run. re-run with --apply")
    raise SystemExit(0)

for target, url, src, why in plan:
    target["url"] = url
    target["locator_from"] = src
    target["identity_verified"] = (
        f"URL COPIED from a record already in the corpus, not typed here. "
        f"{why}. Identity was NOT independently re-checked against Crossref or "
        f"the publisher - the basis is that the sibling names the same work.")

if len(enc["entries"]) != before_entries:
    sys.exit(f"refusing: entry count moved {before_entries}->{len(enc['entries'])}")
if sum(len(e.get("sources", [])) for e in enc["entries"]) != before_records:
    sys.exit("refusing: record count moved")
if sorted(enc) != before_keys:
    sys.exit("refusing: top-level keys changed")

second = p.read_text(encoding="utf-8").split("\n")[1]
indent = len(second) - len(second.lstrip()) or 1
tmp = p.with_suffix(".json.tmp")
tmp.write_text(json.dumps(enc, ensure_ascii=False, indent=indent) + "\n",
               encoding="utf-8")
re_parsed = json.loads(tmp.read_text(encoding="utf-8"))
if sum(len(e.get("sources", [])) for e in re_parsed["entries"]) != before_records:
    sys.exit("refusing: reparse did not reconcile")
tmp.replace(p)
print(f"\nwritten at indent={indent}. {len(plan)} locators attached; "
      f"entries and record count unchanged.")
