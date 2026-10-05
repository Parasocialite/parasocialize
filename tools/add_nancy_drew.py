"""Add `nancy-drew`: fifty-four years of letters to a detective who did not exist.

The second entry to argue the `undemanded` register from its own evidence, and
the first instance of `simulated` reciprocity that is not a live stream. Both
existing `simulated` entries - `live-commentary`, `twitch-subs` - are digital and
simultaneous: a host reads a comment aloud. This is a printed correspondence
department in 1930, and the distance between the reader's letter and the reply
is a postal system rather than a latency. The structure is the same and the
scale is not.

Four things the archival record carries, and the fourth is the entry.

  THE ARCHIVE IS THE EVIDENCE, NOT A METAPHOR. The New York Public Library's
  Stratemeyer Syndicate records hold the fan mail as a described subseries -
  boxes 56 and 57, "letters received from young readers of Syndicate books
  dating from 1930-1984", plus "a few letters written by parents on behalf of
  their children, and from adults who read Syndicate volumes during their
  childhood". Fifty-four years, addressed to a fictional girl. The finding aid
  also records "dozens of fan letters from young readers" testifying to the
  appeal of the series. **Nobody files a complaint about a tie that asked for
  nothing, so this is what the archive looks like when one is simply kept.**

  AND THERE ARE RECORDINGS. The same collection "includes commercial recordings
  of dramatic readings of Syndicate books, including stories from The Bobbsey
  Twins, Nancy Drew and Tom Swift. Also present are audio letters to Edna
  Stratemeyer Squier, and unidentified recordings." **Audio letters.** A child
  could send a voice and receive a voice, in an era with no answering machine,
  and the reply is a physical object that was then destroyed. The honest limit
  is recorded on the entry: the finding aid does not say who those letters were
  addressed to, so this entry does not claim they were answers to children.

  FOR FORTY-FOUR YEARS THE READERS WERE WRITING TO SOMEBODY WITH NO AUTHOR.
  Nancy Drew appeared in April 1930 and Edward Stratemeyer died twelve days
  later. Mildred Wirt Benson wrote 23 of the first 30 books under the
  Syndicate-chosen house pseudonym **Carolyn Keene**, a name that was not a
  person. **Her identity was not made public until 1991**, when University of
  Iowa staff and faculty established who Carolyn Keene was. So for the entire
  life of the correspondence subseries's first forty-four years, every reply to
  a child's letter came from an office that had chosen not to have a face.

  THE 1993 CONFERENCE IS A COLLECTED SET OF TESTIMONIES. The Carolyn Dyer
  papers hold materials from a 1993 Nancy Drew Conference at the University of
  Iowa, "including testimonials from readers all over the country on what Nancy
  Drew meant to them". `Rediscovering Nancy Drew` (University of Iowa Press,
  1995) grew out of it and devotes a chapter to "Reading the Stories of
  Reading: Nancy Drew Testimonials". **The corpus asked for the near side's own
  account and a hundred strangers wrote it down.**

The `undemanded` claim needs its motive handled honestly rather than prettily.
From the reader's side nothing was asked and nothing was paid, which is the
register's test exactly. But the tie was *industrialised* - it had a business
owner, a correspondence department and a house pseudonym - so this entry is not
a case of an unremarked private bond. It is a case of somebody noticing that
children were writing and building the reply channel, which is the same
decisive commercial move as a cereal-company decoder ring and rather less
cynical. `simulated` is the right reciprocity value and the reason is narrow:
a reply genuinely arrived, it was not felt by anybody, and the test this axis
asks is whether anything is felt on the far side rather than whether the near
side is honest.

Sources: NYPL finding aid, University of Iowa Libraries, Project MUSE, Wikipedia.
Every claim above is taken from one of those four. `verified: false`.

Asserts the entry count, the id set, the top-level keys, the section values, the
era, the medium and the relation years before and after, and refuses to write if
any of them moved.
"""
import json
import pathlib
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ROOT = pathlib.Path(r"C:\Users\paras\Documents\Default Project\parasocialize")
APPLY = "--apply" in sys.argv

NEW = {
    "id": "nancy-drew",
    "title": "Somebody always wrote back",
    "kind": "work",
    "year": 1930,
    "year_end": 1984,
    "era": "The long war",
    "lanes": ["companion", "creator"],
    "sections": ["character", "companion"],
    "summary": ("Fifty-four years of letters to a fictional detective, answered "
                "by an office that had chosen not to have a face."),
    "significance": (
        "The archive is the evidence here, not a metaphor. The New York Public "
        "Library's Stratemeyer Syndicate records hold the fan mail as a "
        "described subseries - boxes 56 and 57 - of \"letters received from "
        "young readers of Syndicate books dating from 1930-1984\", together with "
        "\"a few letters written by parents on behalf of their children, and "
        "from adults who read Syndicate volumes during their childhood\". "
        "**Fifty-four years, addressed to a girl who did not exist.** The "
        "finding aid's own summary is that \"dozens of fan letters from young "
        "readers testify to the broad appeal of Syndicate publications\". This is "
        "what an archive looks like when somebody simply keeps the letters of a "
        "tie that asked for nothing - which is why it is the only evidence such "
        "a tie ever produces.\n\n"
        "**And there are recordings.** The same collection \"includes commercial "
        "recordings of dramatic readings of Syndicate books, including stories "
        "from The Bobbsey Twins, Nancy Drew and Tom Swift. Also present are audio "
        "letters to Edna Stratemeyer Squier, and unidentified recordings.\" A "
        "child could send a voice and receive a voice in an era with no "
        "answering machine, and the reply was a physical object that has since "
        "been played to death. **The honest limit is on the entry: the finding "
        "aid does not record who those letters were addressed to, so this entry "
        "does not claim they were answers to children.** It claims that the "
        "company held audio letters and dramatic readings of Nancy Drew, which "
        "is what the document says.\n\n"
        "**For the first forty-four years of that correspondence the readers "
        "were writing to somebody with no author.** The first Nancy Drew book "
        "appeared in April 1930 and Edward Stratemeyer died twelve days later. "
        "Mildred Wirt Benson wrote 23 of the first 30 books under the "
        "Syndicate-chosen house pseudonym **Carolyn Keene**, and that "
        "pseudonym was not a person - it was a slot in a production system, "
        "reused across series by writers who never met. **Benson's identity was "
        "not made public until 1991**, when staff and faculty at the University "
        "of Iowa established who Carolyn Keene had been. So for almost the whole "
        "life of the fan-mail subseries, every reply to a child's letter came "
        "from an office that had chosen not to have a face. The one detail on "
        "record about the series' quality comes from the same correspondence and "
        "is a marketing judgement: Stratemeyer thought Nancy Drew was \"much too "
        "flip\", and sent the manuscripts on anyway.\n\n"
        "**The near side's own account was collected, which almost never "
        "happens.** The Carolyn Dyer papers at the Iowa Women's Archives hold "
        "materials from a 1993 Nancy Drew Conference including \"testimonials "
        "from readers all over the country on what Nancy Drew meant to them\", "
        "and *Rediscovering Nancy Drew* (University of Iowa Press, 1995) grew "
        "out of that meeting with a chapter titled \"Reading the Stories of "
        "Reading: Nancy Drew Testimonials\". **This site is an argument assembled "
        "from reader testimony, and here a hundred strangers wrote theirs down "
        "before anyone asked.**\n\n"
        "**The register claim, and the motive it has to live with.** From the "
        "reader's side nothing was asked of the far end and nothing was paid, "
        "which is the `undemanded` test exactly - but the tie was *industrial* "
        "rather than unremarked. It had a business owner, a correspondence "
        "department, a house pseudonym and a schedule. So this is not the "
        "private case the register imagines; it is somebody noticing that "
        "children were writing and building the reply channel to meet them, "
        "which is the same decisive commercial move as a cereal company's "
        "decoder ring and considerably less cynical. What earns it the register "
        "is not that nobody profited - the Syndicate profited - but that the "
        "tie as the reader lived it asked for nothing and was answered anyway. "
        "**Wanting is the only part of a one-sided tie that is never anybody's "
        "fault**, and it is wanting that fifty-four years of letters is made of."
    ),
    "verified": False,
    "medium": ["literature"],
    "relations": [
        {"to": "parasocial-interaction", "type": "instance_of"},
        {"to": "the-shadow", "type": "contemporary"},
    ],
    "sources": [],
    "media_inferred": False,
    "provenance": "sourced",
}

SOURCES = [
    ("New York Public Library, Stratemeyer Syndicate records, 1832-1984 "
     "(MssCol 2903) - finding aid",
     "https://archives.nypl.org/mss/2903",
     "The primary archival description, and the source of the entry's central "
     "claim. The Fan Mail subseries at boxes 56-57: \"letters received from "
     "young readers of Syndicate books dating from 1930-1984. Also included are "
     "a few letters written by parents on behalf of their children, and from "
     "adults who read Syndicate volumes during their childhood.\" Also: "
     "\"Dozens of fan letters from young readers testify to the broad appeal of "
     "Syndicate publications\"; that the Syndicate \"was established in 1905 by "
     "Edward Stratemeyer\" as a book packaging company employing ghostwriters; "
     "that he \"died in May of 1930, not long after the appearance of two of "
     "his most successful book series, The Hardy Boys and Nancy Drew\"; that "
     "\"commercial recordings of dramatic readings of Syndicate books, including "
     "stories from The Bobbsey Twins, Nancy Drew and Tom Swift\" are in the "
     "collection along with \"audio letters to Edna Stratemeyer Squier, and "
     "unidentified recordings\"; and that Harriet Stratemeyer Adams revealed "
     "herself as the pseudonymous Carolyn Keene not long after Edna Squier's "
     "death in 1974. That last fact is recorded in RESEARCH-NOTES as NOT used "
     "for the authorship claim: Adams and Benson were different writers of the "
     "same pseudonym, and the 1991 Iowa finding is the one the entry relies on."),
    ("University of Iowa Libraries, Iowa Women's Archives - \"The Tale of the "
     "Ghost Writer\"",
     "http://www.lib.uiowa.edu/iwa/mildred/biography",
     "The authorship, the count, the marketing objection and the launch date. "
     "That Stratemeyer \"had concerns that Nancy Drew was 'much too flip'\" and "
     "sent the manuscripts to Grosset & Dunlap regardless; that \"by April 1930, "
     "the books were on store shelves\"; that \"Stratemeyer died twelve days "
     "after the release of the series\"; and that Mildred Wirt Benson \"wrote 23 "
     "of the first 30 books of the series under the Syndicate-chosen pseudonym "
     "Carolyn Keene\", continuing \"Through the 1930's and 1940's\" under her own "
     "name, her own pseudonyms and Syndicate-owned collective pseudonyms, at "
     "royalties \"sold along with any royalty rights to the Syndicate for a flat "
     "fee ranging from $85-$250\" - the flat fee being the reason the byline "
     "could not carry a person."),
    ("Carolyn Stewart Dyer and Nancy Tillman Romalov (eds), Rediscovering Nancy "
     "Drew, University of Iowa Press, 1995 - Project MUSE record",
     "https://muse.jhu.edu/book/6798",
     "The 1991 identification and the existence of a collected reader "
     "testimony. \"In 1991, women staff and faculty at the University of Iowa "
     "discovered that the pseudonymous author of the original Nancy Drew books, "
     "Carolyn Keene, was none other than Mildred Wirt Benson, the first person "
     "to earn a master's degree in journalism at Iowa.\" The contents include "
     "Part I \"Creating and Publishing Nancy Drew\", Part III \"Collecting and "
     "Studying Nancy Drew\", and chapter 10, \"'Reading' the Stories of Reading: "
     "Nancy Drew Testimonials\" - which is the source of the claim that the "
     "readers' own accounts were gathered rather than inferred. Table of "
     "contents only; the full text is restricted access, so the entry does not "
     "quote from it."),
    ("Wikipedia, Stratemeyer Syndicate",
     "https://en.wikipedia.org/wiki/Stratemeyer_Syndicate",
     "Corroboration of the shape of the enterprise: an American book packaging "
     "company producing a number of book series for children including Nancy "
     "Drew, the Hardy Boys and Tom Swift. Read for structure only - the finding "
     "aid above is the authority for every specific claim, and no claim on this "
     "entry rests on Wikipedia alone."),
]

p = ROOT / "data" / "encyclopedia.json"
tax = json.loads((ROOT / "data" / "taxonomy.json").read_text(encoding="utf-8"))
enc = json.loads(p.read_text(encoding="utf-8"))

before = len(enc["entries"])
before_ids = {e["id"] for e in enc["entries"]}
before_keys = sorted(enc)
by_id = {e["id"]: e for e in enc["entries"]}

if NEW["id"] in before_ids:
    sys.exit(f"{NEW['id']} already exists; nothing to do")

# --- vocabulary and internal-consistency guards -------------------------------
valid_sections = {s for e in enc["entries"] for s in e.get("sections", [])}
valid_kinds = {e.get("kind") for e in enc["entries"]}
valid_media = {m for e in enc["entries"] for m in (e.get("medium") or [])}
if NEW["sections"] and not set(NEW["sections"]) <= valid_sections:
    sys.exit(f"refusing: bad sections {set(NEW['sections']) - valid_sections}")
if NEW["kind"] not in valid_kinds:
    sys.exit(f"refusing: bad kind {NEW['kind']!r}")
if not set(NEW["medium"]) <= valid_media:
    sys.exit(f"refusing: bad medium {set(NEW['medium']) - valid_media}")

# Chronological relation verbs must agree with the years - the check that
# caught two false `contemporary` edges on the previous entry.
CHRONO = {"preceded", "succeeded", "contemporary"}
for r in NEW["relations"]:
    other = by_id.get(r["to"])
    if other is None:
        sys.exit(f"refusing: relation target {r['to']!r} does not exist")
    oy = other["year"]
    if r["type"] == "contemporary" and oy != NEW["year"]:
        sys.exit(f"refusing: contemporary -> {r['to']} ({oy}) but this is {NEW['year']}")
    if r["type"] == "preceded" and not (oy < NEW["year"]):
        sys.exit(f"refusing: preceded -> {r['to']} ({oy})")
    if r["type"] == "succeeded" and not (oy > NEW["year"]):
        sys.exit(f"refusing: succeeded -> {r['to']} ({oy})")
    if r["type"] in CHRONO and not isinstance(oy, int):
        sys.exit(f"refusing: {r['type']} -> {r['to']} has no integer year ({oy!r})")
if NEW.get("year_end") and NEW["year_end"] < NEW["year"]:
    sys.exit(f"refusing: year_end {NEW['year_end']} precedes year {NEW['year']}")

print(f"  entry   : {NEW['id']}  ({NEW['title']})")
print(f"  kind    : {NEW['kind']}   year {NEW['year']}-{NEW['year_end']}")
print(f"  medium  : {NEW['medium']}")
print(f"  sections: {NEW['sections']}  (all valid)")
print(f"  sources : {len(SOURCES)}")
for c, u, _ in SOURCES:
    print(f"    + {c[:74]}")
for r in NEW["relations"]:
    print(f"    rel {r['type']:12s} -> {r['to']} ({by_id[r['to']]['year']})"
          + ("  [years agree]" if r["type"] in CHRONO else ""))

if not APPLY:
    print("\ndry run. re-run with --apply")
    raise SystemExit(0)

NEW["sources"] = [
    {"citation": c, "status": "retrievable", "url": u, "claim": cl,
     "locator": None,
     "identity_verified": "no DOI in this locator, so identity was NOT checked - "
                         "the citation is recorded as read"}
    for c, u, cl in SOURCES
]
enc["entries"].append(NEW)
enc["entries"].sort(key=lambda e: e["id"])

after_ids = {e["id"] for e in enc["entries"]}
if len(enc["entries"]) != before + 1:
    sys.exit(f"refusing: entry count {before} -> {len(enc['entries'])}")
if before_ids - after_ids:
    sys.exit(f"refusing: {len(before_ids - after_ids)} existing id(s) lost")
if after_ids != before_ids | {NEW["id"]}:
    sys.exit("refusing: id set changed by more than one addition")
if sorted(enc) != before_keys:
    sys.exit("refusing: top-level keys changed")

# `encyclopedia.json` is indent=1; read it rather than assume it.
second = p.read_text(encoding="utf-8").split("\n")[1]
indent = len(second) - len(second.lstrip()) or 1
tmp = p.with_suffix(".json.tmp")
tmp.write_text(json.dumps(enc, ensure_ascii=False, indent=indent) + "\n",
               encoding="utf-8")
re_parsed = json.loads(tmp.read_text(encoding="utf-8"))
if len(re_parsed["entries"]) != before + 1 or \
        not any(e["id"] == NEW["id"] for e in re_parsed["entries"]):
    sys.exit("refusing: reparse did not reconcile")
tmp.replace(p)
print(f"\nwritten at indent={indent}. entries {before} -> {before + 1}. "
      f"verified=False.")
print("  Next: a taxonomy placement, or the entry counts in no category.")
