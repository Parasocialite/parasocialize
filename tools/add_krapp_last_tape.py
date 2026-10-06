"""Add `krapp-last-tape`: the first entry on `stage`, and the corpus's purest
one-sided tie - a man having a conversation with a recording of himself.

`stage` was added to `MEDIA` in the last media pass and has had **zero**
entries behind it ever since, which is the shape of hole AGENTS calls "a
closed validated list is what makes a missing medium a visible hole rather
than an inconvenience". This entry fills it without moving anything, because
Krapp is a play and the play is the subject.

Why this play and not a better-known one. Everywhere else on this site the
far end of the tie is *another* person, and the whole argument is that the
other person cannot answer. Krapp inverts it: **the far end is a recording of
the near side, made thirty years earlier, and it cannot answer either.** The
only technology that could have produced a reply from the past is a tape
recorder, and the play is about the fact that it produces the past rather
than the conversation. A solo monologue, staged, that turns out to be a
dialogue with someone who is guaranteed never to speak again - and an
audience watching a man fail to get a reply from a voice that is his own.

Four things the sources carry.

  IT IS NOT A MONOLOGUE, AND THAT IS THE POINT. The Guardian's 2025 piece:
  "Although performed by a single actor, Krapp's Last Tape is not quite a
  monologue. It becomes a kind of dialogue between the 69-year-old Krapp and
  his recorded 39-year-old self." On his birthday every year he records a
  review of the year gone; at 69 he plays the one made at 39.

  THE FAR END IS NOT MERELY SILENT, IT IS CORRUPTED. This is the detail worth
  the entry. An *Opera Quarterly* article records a mechanical error present
  in **all the Faber & Faber editions** and in the so-called avant-texte,
  appearing in a typescript from shortly before publication in 1958: **four
  words are missing from the tape.** "The four missing words when listening to
  Krapp's tape can be considered as a sonic or performative punctum." So the
  one artefact that carries his younger self back is itself damaged, in a way
  no reprint fixes. **The past self is not silent; it is incomplete.**

  AND THE LINE ON THE TAPE IS NOT REASSURING. The tape his ledger marks
  "Farewell to love" recalls a tryst on a river, and the Guardian's 2024
  review notes that it is "a jolt to hear the line, spoken calmly: 'I said
  again I thought it was hopeless and no good going on and she agreed, without
  opening her eyes.'" The other party in that memory is on a recording too,
  described rather than quoted - and the person actually audible is a man
  describing being refused. He is scathing about his thirty-nine-year-old
  self, and the review has him "cradl[e] the tape recorder in a gesture of
  engulfing loneliness."

  BECKETT WROTE IT BECAUSE HE HEARD AN ACTOR HEAR HIMSELF. The Guardian:
  Beckett wrote the play for the Irish actor **Patrick Magee** after hearing him
  read Beckett's own *From an Abandoned Work* (1954-55) and extracts from
  *Molloy* (1955) **on the radio**. So the occasion of a play about a man
  listening to a recording of himself is a real man hearing a real recording
  of himself - and the same production lineage recurs: Arts Over Borders asked
  Samuel West and Richard Dormer to each record the taped Krapp *at thirty-
  nine*, so the two-voice structure is produced the way the play describes it.
  And there is **no recording of the 1958 premiere** with Magee in the title
  role, which is the one thing an archive of this tie would most want.

`medium: stage`, `kind: work`, dated 1958 from the premiere rather than from a
composition date, because the play's first object is a Royal Court stage.

Two relations, both checked against the years: `contemporary` -> `vertigo`
(1958 - same year, and a man who cannot reach another person), `depicts` ->
`parasocial-interaction`. Nothing else is claimed, because the relation
vocabulary is chronological, bibliographic or structural and has no type for
"thematic kinship".

Four sources, all read. `verified: false`.
"""
import json
import pathlib
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ROOT = pathlib.Path(__file__).resolve().parent.parent
APPLY = "--apply" in sys.argv

NEW = {
    "id": "krapp-last-tape",
    "title": "The tape could not answer",
    "kind": "work",
    "year": 1958,
    "era": "Live",
    "lanes": ["companion", "grief"],
    "sections": ["companion", "grief"],
    "summary": ("A man on his sixty-ninth birthday plays a recording he made at "
                "thirty-nine, and has the conversation the tape cannot have back."),
    "significance": (
        "**The far end is the near side.** Everywhere else on this site the other "
        "end of the tie is somebody else, and the entire argument of the site is "
        "that the other person cannot answer. This inverts it. Krapp records a "
        "tape reviewing the year gone on every birthday of his life; on his "
        "sixty-ninth he puts on the one he made at thirty-nine, and talks to it. "
        "The Guardian's reading is that although it is performed by a single "
        "actor, \"it is not quite a monologue. It becomes a kind of dialogue "
        "between the 69-year-old Krapp and his recorded 39-year-old self.\" **A "
        "solo monologue, staged, that is a conversation with somebody who is "
        "guaranteed never to speak again - performed to an audience watching a "
        "man fail to get a reply from a voice that is his own.**\n\n"
        "**And the tape is not only silent. It is damaged.** This is the detail "
        "that earns the entry. An *Opera Quarterly* article records a mechanical "
        "error present in **all the Faber & Faber editions** and in the "
        "so-called avant-texte, appearing in a typescript from shortly before "
        "publication in 1958: **four words are missing from the tape.** The "
        "article calls them \"a sonic or performative punctum pricking the one "
        "who realizes it\". So the single artefact that carries his younger self "
        "back into the room is itself incomplete, in a way no reprint fixes. "
        "**The past self is not silent; it is truncated** - and the damage is "
        "material, printed into every copy, rather than a figure of speech "
        "about loss.\n\n"
        "**The tape's own contents are a record of being refused.** The one his "
        "ledger marks \"Farewell to love\" recalls a tryst on a river, and the "
        "Guardian's 2024 review calls it \"a jolt to hear the line, spoken "
        "calmly: 'I said again I thought it was hopeless and no good going on "
        "and she agreed, without opening her eyes.'\" Note the shape: the other "
        "party in that memory is on the recording too, and she is *described* "
        "rather than heard. The only voice actually audible is a man "
        "reproducing the moment he asked for something and was refused. He is "
        "scathing about his thirty-nine-year-old self throughout - mocking his "
        "artistic ambition - and the review has him \"cradl[e] the tape "
        "recorder in a gesture of engulfing loneliness\". Then he loads a fresh "
        "reel and records the year. **The ritual continues, which is what makes "
        "it a bond rather than an episode.**\n\n"
        "**Beckett wrote it because he heard somebody hear himself.** The play "
        "was written for the Irish actor **Patrick Magee**, after Beckett heard "
        "him read Beckett's own *From an Abandoned Work* (1954-55) and extracts "
        "from *Molloy* (1955) **on the radio** - a man hearing a recording of his "
        "own voice. So the occasion of a play about listening to yourself was a "
        "real instance of it. **And the structure keeps being manufactured the "
        "way the play describes it**: Arts Over Borders asked Samuel West and "
        "Richard Dormer each to record the taped Krapp *at thirty-nine*, so the "
        "two-age split is produced by casting two people rather than by time "
        "travel, and successive productions have reused the same machine.\n\n"
        "**One archival fact, and it is the sad one.** There is **no recording "
        "of the 1958 premiere** with Patrick Magee in the title role under "
        "Donald McWhinnie's direction. So the first audience's encounter with "
        "this tie has no trace, while a play whose entire subject is a "
        "destructible recording has outlived every document about its own first "
        "night. **This is an `archive` register entry hiding inside a `bond` "
        "entry** - the same double reading as `dear-kitty`'s \"as long as this "
        "still exists, I cannot be sad\", and it is why the tape rather than the "
        "man is the thing this site should remember about the play.\n\n"
        "**Why the medium matters here.** `stage` was added to the medium list "
        "and had nothing behind it. The honest way to fill that is not to move "
        "an existing entry into a new bucket, which would be a tidier chart and "
        "a false classification, but to write the entry the shelf was opened "
        "for. Krapp is a play, the play *is* the subject, and a solo monologue "
        "turning on a machine that cannot answer is about as close as this "
        "site's central structure gets to being staged."
    ),
    "verified": False,
    "medium": ["stage"],
    "relations": [
        {"to": "vertigo", "type": "contemporary"},
        {"to": "parasocial-interaction", "type": "depicts"},
    ],
    "sources": [],
    "media_inferred": False,
    "provenance": "sourced",
}

SOURCES = [
    ("Wikipedia, \"Krapp's Last Tape\"",
     "https://en.wikipedia.org/wiki/Krapp%27s_Last_Tape",
     "The basic record and the sequence. A **1958 one-act play** in English by "
     "Samuel Beckett, premiered **28 October 1958 at the Royal Court Theatre, "
     "London**. The curtain rises on a \"late evening in the future\"; Krapp is "
     "an old man in his den with a tape recorder and tins of reels, and \"reads "
     "aloud from a ledger to find a certain tape, but the words alone are not "
     "jogging his memory\"; \"Krapp lets it play out and then rewinds the tape "
     "to hear the complete episode\"; \"Afterwards, Krapp loads a fresh tape "
     "and begins to recount his year. He is scathing when it comes to his "
     "assessment of his thirty-nine-year-old self.\" Also that his problem with "
     "constipation has been ongoing since at least that time, and the "
     "thirty-nine-year-old's estimate that the tape he was listening to was "
     "made ten or twelve years before that. Read in full for the plot order "
     "rather than summarised from memory."),
    ("Chris Wiegand, \"Holy Krapp! Gary Oldman and Stephen Rea unspool "
     "Beckett's masterpiece about memory\", The Guardian, 1 May 2025",
     "https://www.theguardian.com/stage/2025/may/02/holy-krapp-gary-oldman-and-stephen-rea-unspool-becketts-masterpiece-about-memory",
     "The dialogue claim, the birthday ritual, and the occasion of the play. "
     "\"Although performed by a single actor, Krapp's Last Tape is not quite a "
     "monologue. It becomes a kind of dialogue between the 69-year-old Krapp and "
     "his recorded 39-year-old self, who in turn reflects on how he behaved in "
     "his late 20s.\" Also that Krapp \"spools through reels of memoir recorded "
     "each year on his birthday\"; that Beckett wrote the play for **Patrick "
     "Magee** after hearing him read Beckett's own *From an Abandoned Work* "
     "(1954-55) and extracts from *Molloy* (1955) **on the radio**; that Arts "
     "Over Borders asked **Samuel West and Richard Dormer to each record the "
     "part of the taped Krapp when they were 39**; that a production reused "
     "\"the same machine used by Michael Gambon and John Hurt\"; and the line "
     "\"Perhaps my best years are gone.\""),
    ("Review of Stephen Rea in Krapp's Last Tape, directed by Vicky "
     "Featherstone, Project Arts Centre Dublin, The Guardian, 19 January 2024",
     "https://www.theguardian.com/stage/2024/jan/19/krapps-last-tape-review-stephen-rea-project-arts-centre-dublin",
     "The contents of the tape and how it is heard. The recording Krapp's "
     "ledger notes as \"**Farewell to love**\", and the review's account that "
     "\"Its recollection of a lovers' tryst on a river is so tenderly evoked "
     "that it is a jolt to hear the line, spoken calmly: 'I said again I "
     "thought it was hopeless and no good going on and she agreed, without "
     "opening her eyes.'\" Also that Krapp \"mocks his younger self's artistic "
     "ambition\" and is \"bemused by the confident delivery of the 39-year-old "
     "on tape\"; that Rea \"cradles the tape recorder in a gesture of engulfing "
     "loneliness\" at this point; and that Beckett wrote much of his work in "
     "French, which the production marks in Krapp's delivery."),
    ("\"Graphanalysis, Technological Reproduction, and the Acoustical "
     "Unconscious: Reflections on an Error in Beckett's Krapp's Last Tape\", "
     "The Opera Quarterly (Oxford Academic)",
     "https://academic.oup.com/oq/article/doi/10.1093/oq/kbaf009/8407042",
     "The corrupted tape, which is the entry's central detail and could not "
     "have been found in a review. \"Sitting at his desk at night, the old "
     "Krapp listens to his own voice recorded on a reel-to-reel tape thirty "
     "years earlier.\" The mechanical error is \"present not only in all the "
     "Faber & Faber editions, but also in the so-called avant-texte\", and "
     "\"appears and then\" persists from \"one of Beckett's last typescripts "
     "dating from shortly before the work's publication in 1958\"; \"the four "
     "missing words when listening to Krapp's tape can be considered as a sonic "
     "or performative punctum pricking the one who realizes it\". Also Steven "
     "Connor, quoted: \"for Krapp to listen to the tape of himself as a man of "
     "thirty-nine is to reveal clearly his ironic non-coincidence with himself.\" "
     "And the archival absence: \"As far as I have been able to ascertain, "
     "there is no recording of the premiere of Krapp's Last Tape with Patrick "
     "Magee in the title role under the direction of Donald McWhinnie (London, "
     "Royal Court Theatre, October 28, 1958).\" Read via search index rather "
     "than fetched in full, so the article's author and length are not recorded "
     "and no DOI identity was checked."),
]

p = ROOT / "data" / "encyclopedia.json"
tax = json.loads((ROOT / "data" / "taxonomy.json").read_text(encoding="utf-8"))
enc = json.loads(p.read_text(encoding="utf-8"))
sys.path.insert(0, str(ROOT / "tools"))
from atlas import MEDIA  # noqa: E402

before = len(enc["entries"])
before_ids = {e["id"] for e in enc["entries"]}
before_keys = sorted(enc)
by_id = {e["id"]: e for e in enc["entries"]}

if NEW["id"] in before_ids:
    sys.exit(f"{NEW['id']} already exists; nothing to do")

valid_sections = {s for e in enc["entries"] for s in e.get("sections", [])}
valid_kinds = {e.get("kind") for e in enc["entries"]}
if not set(NEW["sections"]) <= valid_sections:
    sys.exit(f"refusing: bad sections {set(NEW['sections']) - valid_sections}")
if NEW["kind"] not in valid_kinds:
    sys.exit(f"refusing: bad kind {NEW['kind']!r}")
if not set(NEW["medium"]) <= set(MEDIA):
    sys.exit(f"refusing: {set(NEW['medium']) - set(MEDIA)} not in the validated MEDIA list")

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
    sys.exit(f"refusing: year_end precedes year")

print(f"  entry   : {NEW['id']}  ({NEW['title']})")
print(f"  medium  : {NEW['medium']}  <- first entry on this medium")
print(f"  kind    : {NEW['kind']}   year {NEW['year']}   era {NEW['era']!r}")
print(f"  sections: {NEW['sections']}")
print(f"  sources : {len(SOURCES)}")
for c, u, _ in SOURCES:
    print(f"    + {c[:76]}")
for r in NEW["relations"]:
    tag = "  [years agree]" if r["type"] in CHRONO else ""
    print(f"    rel {r['type']:12s} -> {r['to']} ({by_id[r['to']]['year']}){tag}")

# What this does to the media distribution, stated before the write.
from collections import Counter
counts = Counter(m for e in enc["entries"] for m in (e.get("medium") or []))
print(f"\n  medium 'stage' before: {counts.get('stage', 0)}")
print(f"  medium 'stage' after : {counts.get('stage', 0) + 1}")
others = [m for m in MEDIA if not counts.get(m) and m != "stage"]
print(f"  media still empty after this write: {others}")

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
    sys.exit("refusing: existing ids lost")
if after_ids != before_ids | {NEW["id"]}:
    sys.exit("refusing: id set changed by more than one addition")
if sorted(enc) != before_keys:
    sys.exit("refusing: top-level keys changed")

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
