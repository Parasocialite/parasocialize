"""Add `queen-for-a-day`: radio's first entry after 1930, and the applause meter.

`radio` had two entries and **both were 1930** - `radio-serials` and
`the-shadow` - so the medium was not only thin but historically narrow, pinned
to the year its two entries happened to sit in. This is 1945.

**I arrived at this subject with a wrong memory and the sources corrected it.**
I expected a letter-writing show: listeners writing in with their misfortunes.
That is not the format that ran. In the version that broadcast, contestants were
interviewed **in the studio, one at a time**, each telling her troubles aloud,
and **the audience chose the winner by applauding** - "She who received the
greatest amount of applause **as registered by the 'applause meter'** was Queen
for a Day." Recorded on the entry, because a correction that arrives from a
source is worth more in the record than a memory that happened to be right.

**The applause meter is the find, and it is the `cog` register in hardware.**
The register asks whether seeing the whole machine changes the attachment, and
says the far end has its own machinery, every other viewer has theirs, and you
are all meshing in a device none of you built. Here the device is literal and it
is in the chain: a woman's misfortune was told aloud, a crowd's reaction was
converted into a number, and the number chose. **A machine returned the verdict
on somebody's life.** Every other `cog` case in the corpus argues the point
structurally; this one has a box on a wall with a needle in it.

**And the honesty note that makes it sharper rather than weaker.** In radio the
home listener could not participate. The audience the meter registered was the
**studio** crowd - "the live audience, mostly women, cheered" - while the
millions listening at home could not applaud into the device at all. So the
applause meter was not a proxy for the audience's feeling; **it measured a
different and much smaller audience than the one listening.** The far end was
not merely unseen. Its measuring instrument was pointed at the wrong room.

Three more things the sources carry, and all three are the site:

  THE PRIZE WAS A FICTIONAL FIGURE BUILT OUT OF A REAL WOMAN'S MISFORTUNE.
  The OTRCAT record of the format: "It starred their friends and neighbors,
  and **turned them into fabulous Cinderellas**" - "a roll down the red carpet
  at a movie studio, a beauty analysis, Hollywood makeup and hairdo, escort
  through the Boulevard". A contestant asked for "an operation for her sick cat".
  The object of the public's attachment is a **Cinderella**, and she is
  assembled weekly out of a neighbour's hardship. **The parasocial figure is
  manufactured from real grief and then the grief is explained as a
  commercial.**

  WHICH IS WHAT THE THRONE WAS FOR. Documented as mood dissonance: after being
  crowned, "the contestant was expected to sit on a throne and listen to a five
  minute in-show commercial about all the consumer items that she'd just won,
  **while pretending to be really excited and thankful about the benefits of
  things like aluminum cookware and dog treats**." A woman who has just asked
  publicly for surgery for her child is required to perform gratitude for a
  sponsor, on air, for five minutes. **That is `simulated` reciprocity aimed at
  the person being pitied rather than at the audience** - and it is the most
  uncomfortable mechanism in the corpus, because the performance is compulsory
  and the person performing it is the one with least power to refuse.

  THE SPONSOR PAID FOR EVERY SECOND OF IT. "Sponsored by Malted Milk." And the
  network's own arithmetic: the show was so popular it was extended from 30 to
  45 minutes "so they could sell more commercial time at the then astounding
  rate of $4000 per minute" - **the sorrow slot was sold by the minute.**

Relations: `contemporary` -> `casper` (1945, the only other entry in that year),
`instance_of` -> `parasocial-interaction`. `medium: radio`, `kind: mechanism`.

Five sources, all read, and the three weakest are named as weakest on the entry:
the applause-meter wording comes from Simple English Wikipedia, the studio/
commercial behaviour from TV Tropes (user-edited), and the price-per-minute from
a fan site. The publication and format facts are corroborated across the
Television Academy's own archive and two catalogues.

Asserts entry count, id set, top-level keys, section values, kind, medium and
relation years, and the file's own indentation, before and after.
"""
import json
import pathlib
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ROOT = pathlib.Path(__file__).resolve().parent.parent
APPLY = "--apply" in sys.argv

NEW = {
    "id": "queen-for-a-day",
    "title": "Registered by the applause meter",
    "kind": "mechanism",
    "year": 1945,
    "era": "Fandom",
    "lanes": ["companion", "idol"],
    "sections": ["companion", "contest"],
    "summary": ("A woman's misfortune told aloud, a crowd's reaction converted "
                "into a number, and the number chose her."),
    "significance": (
        "**A machine returned the verdict on somebody's life.** The format that "
        "actually broadcast is not the one most people remember. The host "
        "interviewed four or five women one at a time, each telling her "
        "personal troubles - a terminally sick child at home, a disabled husband "
        "out of work, the need for a hearing aid, a washing machine, a "
        "refrigerator - and then **the audience chose the winner by "
        "applauding**. The source is exact about the instrument: she \"who "
        "received the greatest amount of applause **as registered by the "
        "'applause meter'** was Queen for a Day.\" So a woman's hardship was "
        "narrated aloud, a room's reaction was converted into a reading, and the "
        "reading decided. **Every other `cog` case in this corpus argues the "
        "point structurally; this one has a box on a wall with a needle in it.** "
        "The register asks whether seeing the whole machine changes the "
        "attachment - and here the machine is not a metaphor for a set of "
        "relations, it is the thing that did the choosing.\n\n"
        "**And the instrument was pointed at the wrong room, which is the "
        "honesty note that makes it sharper rather than weaker.** In radio the "
        "home listener could not participate at all. The crowd the meter "
        "registered was the **studio** audience - as the format has it, the "
        "audience was asked \"Would you like to be Queen for a Day?\", \"YES!!!!\" "
        "shouted the audience, and \"the audience cheered to pick their "
        "favorite one\" - while the millions listening at home could not "
        "applaud into the device. **So the applause meter was not a proxy for "
        "the audience's feeling. It measured a different and much smaller "
        "audience than the one listening.** The far end was not merely unseen; "
        "its measuring instrument was aimed elsewhere. That is a sharper claim "
        "than \"the audience picked the winner\", and it is the one the sources "
        "support.\n\n"
        "**The prize was a fictional figure assembled out of a real woman's "
        "misfortune.** The prize list is a Cinderella transformation in full: "
        "\"It starred their friends and neighbors, and **turned them into "
        "fabulous Cinderellas** with such prizes as a charming five-star "
        "luncheon with a friend, a roll down the red carpet at a movie studio, a "
        "beauty analysis, Hollywood makeup and hairdo, escort through the "
        "Boulevard, dining on the finest steaks and tropical fruits, then "
        "dancing at the finest star-studded clubs.\" **The object of the public's "
        "attachment is a Queen, and she is built weekly out of a neighbour's "
        "hardship** - one contestant asked for \"an operation for her sick "
        "cat\". So the parasocial figure is manufactured from real grief, and "
        "the grief is then explained as a commercial. Jack Bailey's sign-off is "
        "the thesis of the format in eight words: **\"Make every woman a queen, "
        "for every single day!\"**\n\n"
        "**And the throne was where the performance was compulsory.** Documented "
        "as mood dissonance: after being crowned, the contestant \"was expected "
        "to sit on a throne and listen to a five minute in-show commercial about "
        "all the consumer items that she'd just won, **while pretending to be "
        "really excited and thankful about the benefits of things like aluminum "
        "cookware and dog treats**.\" **A woman who has just asked in public for "
        "surgery for her child is then required to perform gratitude to a "
        "sponsor, on air, for five minutes.** That is `simulated` reciprocity "
        "aimed at the person being pitied rather than at the audience, and it is "
        "the most uncomfortable mechanism in this corpus - because the "
        "performance is compulsory and the person performing it has the least "
        "power in the room to refuse it. The audience's attachment is real; the "
        "contestant's half of it is a sponsorship read.\n\n"
        "**The sorrow slot was sold by the minute.** Sponsored by Malted Milk, "
        "and the network's own arithmetic is the record: the show was so popular "
        "that the network extended it from 30 to 45 minutes \"so they could sell "
        "more commercial time at the then astounding rate of **$4000 per "
        "minute**\". So the position of the contestant with the worst story was "
        "worth money to somebody, and the schedule is the receipt.\n\n"
        "**The shape of the thing, briefly, because it is genuinely a forerunner "
        "and the corpus should say so on its own terms.** Created by John "
        "Masterson, debuting on the Mutual network on **30 April 1945** as "
        "*Queen for Today*, hosted first by Ken Murray; a few months in it moved "
        "to Los Angeles, took the name *Queen for a Day*, and Jack Bailey - a "
        "former vaudeville musician and World's Fair barker - took over, "
        "simulcasting on television from 1948 through a DuMont affiliate whose "
        "owner also owned Mutual's Los Angeles radio station. Radio ran to 1957; "
        "it went to NBC television in 1956 and ABC in 1960. **The transition that "
        "made the device possible is in its own dates**: the applause meter "
        "needs a room, and the room arrived on schedule alongside the contest.\n\n"
        "**Two honesty notes on this entry's own sourcing**, because the weakest "
        "records are also the most load-bearing. The applause-meter wording - the "
        "entry's title and its central claim - comes from Simple English "
        "Wikipedia, which is a wiki and should be stood behind. The throne "
        "behaviour and the mood-dissonance description come from TV Tropes, which "
        "is user-edited and is the weakest source here. The $4000-per-minute "
        "figure comes from a fan site and is **not** corroborated anywhere in "
        "what was read, so it is the first thing to check. The publication and "
        "format facts - creator, host, dates, networks, prizes, running time - "
        "are corroborated across the Television Academy's own archive and two "
        "independent catalogues, and those can be relied on."
    ),
    "verified": False,
    "medium": ["radio"],
    "relations": [
        {"to": "parasocial-interaction", "type": "instance_of"},
        {"to": "casper", "type": "contemporary"},
    ],
    "sources": [],
    "media_inferred": False,
    "provenance": "sourced",
}

SOURCES = [
    ("Simple English Wikipedia, \"Queen for a Day\"",
     "https://simple.wikipedia.org/wiki/Queen_for_a_Day",
     "The format and the instrument, which is the entry's title and its central "
     "claim. That host Jack Bailey \"interviewed four women contestants\" and "
     "that \"Each told of her personal troubles. These troubles might involve a "
     "terminally sick child at home, a husband disabled and out of work, or the "
     "need for a hearing aid or a new washing machine\"; that **\"The audience "
     "chose the winner by applauding their favorite. She who received the "
     "greatest amount of applause as registered by the 'applause meter' was "
     "Queen for a Day\"**; that the winner \"was crowned, escorted by attendants "
     "to a throne, and given not only what she wanted, but juicy prizes like "
     "high-end appliances, upscale fashions, and exotic vacation trips as "
     "well\"; that the show launched on radio on 30 April 1945 and ran there "
     "until 1957, then NBC television 1956 to 1964; that \"The program is "
     "something of an early 'reality show'\"; and that \"the show was so popular "
     "that NBC increased its running time from 30 minutes to 45 minutes.\" "
     "**A wiki, and the load-bearing claim for the title - the first thing to "
     "stand behind.**"),
    ("Television Academy Interviews, \"Queen for a Day\"",
     "https://interviews.televisionacademy.com/shows/queen-for-a-day",
     "Creator, hosts and the request structure, from an institutional archive "
     "rather than a fan page. That the show was \"Created by John Masterson\"; "
     "that Ken Murray presented the 1945-1957 radio version and Jack Bailey "
     "1956-1964 on television; that it \"helped to usher in American listeners' "
     "and viewers' fascination with big-prize giveaway shows when it was born on "
     "radio (1945-1957), before moving to television (1956-1964)\" and is "
     "\"considered a forerunner of modern-day 'reality television'\"; that "
     "\"The show opened with host Bailey asking the audience - mostly women - "
     "'Would YOU like to be Queen for a day?'\"; that \"The interview would "
     "climbax with Bailey asking the contestant what she needed most and why she "
     "wanted to win the title of Queen for a Day. Often the request was for "
     "medical care or therapeutic equipment to help a chronically ill child, but "
     "sometimes it was as simple as the need for a hearing aid, a new washing "
     "machine, or a refrigerator\"; and Bailey's sign-off, **\"Make every woman "
     "a queen, for every single day!\"** Running time \"30 min, later 45.\""),
    ("OTRCAT (Old Time Radio Catalog), \"Queen for a Day\"",
     "https://www.otrcat.com/p/queen-for-a-day",
     "The audience's own voice and the sponsor, plus the Cinderella framing and "
     "one named request. That \"'Would you like to be Queen for a Day?' asked "
     "the host, Jack Bailey. 'YES!!!!' shouted the audience.\"; that the show "
     "was **\"Sponsored by Malted Milk\"** and \"was a popular one among "
     "housewives\"; that \"It starred their friends and neighbors, and **turned "
     "them into fabulous Cinderellas** with such prizes as a charming five-star "
     "luncheon with a friend, a roll down the red carpet at a movie studio, a "
     "beauty analysis, Hollywood makeup and hairdo, escort through the "
     "Boulevard, dining on the finest steaks and tropical fruits, then dancing "
     "at the finest star-studded clubs\"; that \"After the host interviewed the "
     "five contestants, who made requests for items of their eye (one asked for "
     "an operation for her sick cat), **the audience cheered to pick their "
     "favorite one. The winner won the item she requested**, as well as some "
     "dreamy prizes and her time in the sun as 'Queen for a Day'\"; and the "
     "genre description \"Contest and Audience Participation Show (1945-1957)\"."),
    ("TV Tropes, \"QueenForADay\"",
     "https://tvtropes.org/pmwiki/pmwiki.php/Series/QueenForADay",
     "The debut details and the throne behaviour - and **this is the weakest "
     "record in the entry, user-edited, so it is flagged rather than leaned on.** "
     "That the show debuted \"on the radio on April 30, 1945 as *Queen for "
     "Today* on the Mutual Broadcasting System with Ken Murray as host and with "
     "John Masterson producing the show\"; that \"A few months into the run, the "
     "show moved to Los Angeles and was given the more familiar title; Murray "
     "was replaced by Jack Bailey\"; that from 1948 it was simulcast on "
     "television through DuMont affiliate KTSL-TV, \"whose owner, the Don Lee "
     "Network, also owned KHJ-AM, Mutual's Los Angeles affiliate\"; and the mood "
     "dissonance note: **\"After being crowned Queen for a Day, the contestant "
     "was expected to sit on a throne and listen to a five minute in-show "
     "commercial about all the consumer items that she'd just won, while "
     "pretending to be really excited and thankful about the benefits of things "
     "like aluminum cookware and dog treats.\"**"),
    ("Queen for a Day Classic, queenforaday.com",
     "https://queenforaday.com/classic.php",
     "The commercial arithmetic, and the single least corroborated number in the "
     "entry - recorded as such. That \"Queen For A Day literally invented reality "
     "television and product integration\"; and that the show \"was so popular "
     "the Network actually increased its running time from 30 minutes to 45 "
     "minutes so they could sell more commercial time at the then astounding "
     "rate of **$4000 per minute**\". A fan site, and **the $4000 figure is not "
     "corroborated by any other record read here**, so it is flagged on the entry "
     "as the first claim to check. The 30-to-45-minute extension itself *is* "
     "independently supported by Simple English Wikipedia and by the Television "
     "Academy."),
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
    sys.exit(f"refusing: {set(NEW['medium']) - set(MEDIA)} not in validated MEDIA")

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

print(f"  entry   : {NEW['id']}")
print(f"  title   : {NEW['title']}")
print(f"  medium  : {NEW['medium']}  <- first radio entry since 1930")
print(f"  kind    : {NEW['kind']}   year {NEW['year']}")
print(f"  sections: {NEW['sections']}")
print(f"  sources : {len(SOURCES)}  (2 flagged as weak on the entry)")
for c, u, _ in SOURCES:
    print(f"    + {c[:76]}")
for r in NEW["relations"]:
    tag = "  [years agree]" if r["type"] in CHRONO else ""
    print(f"    rel {r['type']:12s} -> {r['to']} ({by_id[r['to']]['year']}){tag}")

from collections import Counter
counts = Counter(m for e in enc["entries"] for m in (e.get("medium") or []))
rad = sorted((e["year"], e["id"]) for e in enc["entries"]
             if "radio" in (e.get("medium") or []) and isinstance(e["year"], int))
print(f"\n  radio before: {counts.get('radio', 0)} entries")
print(f"  radio before, by year: {rad}")
print(f"  radio years after this write: "
      f"{sorted(rad + [(1945, NEW['id'])])}")

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
