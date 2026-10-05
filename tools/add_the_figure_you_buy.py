"""Add `the-figure-you-buy`: the character IS the product, and the corpus had it backwards.

The corpus held `the-brand-as-character` (1995): a corporation *given* a voice, a
face, a tone, so a customer relationship acquires a subject. That is the ordinary
case, and it is the weaker one, because the company was there first and the
personality was bolted on.

Wonka is the inverse and it is stronger. The figure came first, and the product
took the figure's NAME. Roald Dahl invented a chocolatier in 1964; in 1971 a
breakfast-cereal company with no film experience paid about $3 million to finance
an adaptation **in exchange for the right to sell a chocolate bar under the
character's name**, and the film was retitled from *Charlie and the Chocolate
Factory* to put the product in the title. The brand launched a month before the
film opened. Wikipedia's own phrase for the arrangement is "the greatest reverse
product placement ever".

So the parasocial object is engineered to be unfalsifiable. Everywhere else on
this site the far side can disappoint you: a performer cancels, dies, scandals,
sues. Wonka cannot do any of it, because he was never a person. **That is not a
side effect of the licensing - it is what the licensing is for.** Every risk that
makes a real attachment costly has been engineered out of the product.

And the 2026 Netflix competition series is where the engineering fails in public.
It restores Gene Wilder's dead voice with generative audio, made by ElevenLabs
with the approval of his estate and his widow, and the showrunner says plainly
that "the only person that could be Wonka is Gene Wilder". So a fictional
chocolatier and a dead actor are fused into one addressable figure. Audiences
hated it: Metacritic 29, no positive reviews, and the Los Angeles Times called
the voice "a lifeless voice not so much from beyond the grave as buried in it".

**That failure is the entry.** The bar cannot disappoint and therefore never
repays. The moment the substitution is visible - a dead man's reconstructed voice
in an invented man's mouth - the safety is over and the illusion has nothing
underneath it. The corpus had no way to say that, because it had only ever seen
the brand-as-character direction.

Two further things the sources carry and the site should not soften:

  - The book rewards Charlie for NOT being greedy. The show pays $3 million to
    contestants who are explicitly incentivised to scheme, and calls its
    eliminations "termination". The figure is now made to host the exact contest
    he was invented to punish.
  - Nestlé owned the brand from 1988 to 2015 and is a named defendant in the 2021
    International Rights Advocates case, in which eight Malian plaintiffs
    allege they were trafficked as children to harvest cocoa. **That is an
    allegation and the company disputes it, and it is recorded here as one.** It
    belongs in the entry because the point is structural, not accusatory: an
    invented figure's name is routinely used as the emblem for a real supply chain
    of real people, and a made-up person absorbs the charge.

Asserts the entry count, the id set and the top-level keys before and after.
"""
import json
import pathlib
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ROOT = pathlib.Path(r"C:\Users\paras\Documents\Default Project\parasocialize")
APPLY = "--apply" in sys.argv

NEW = {
    "id": "the-figure-you-buy",
    "title": "The figure you buy",
    "kind": "mechanism",
    "year": 1971,
    "era": "Marketing",
    "lanes": ["manipulation", "application"],
    "sections": ["brand", "character"],
    "summary": ("A fictional figure whose NAME is the product: the bond is with a "
                "person who was invented so that the relationship can never fail."),
    "significance": (
        "The inverse of `the-brand-as-character`, and the sharper version of it. "
        "There the company came first and was given a personality; here the "
        "personality came first and the company took the name. In 1971 a "
        "breakfast-cereal company with no film experience paid roughly $3m to "
        "finance an adaptation in exchange for the right to sell a bar under the "
        "character's name, and the film was retitled to put the product in the "
        "title. Wikipedia calls it the greatest reverse product placement ever. "
        "The point of the arrangement is not the pun: it is that the far side of "
        "the bond is manufactured to be unfalsifiable. A performer can cancel, "
        "die, scandalise or sue you. This one cannot do any of it, because he was "
        "never a person, and a bond that cannot be disappointed cannot repay "
        "either. That is why it lasts fifty-five years. "
        "The 2026 Netflix competition is where the engineering fails in public: it "
        "restores Gene Wilder's dead voice with generative audio, built by "
        "ElevenLabs with the approval of his estate and his widow, and the "
        "showrunner says the only person who could be Wonka is Gene Wilder - "
        "fusing a fictional chocolatier and a dead actor into one addressable "
        "figure. It was hated. Metacritic 29, no positive reviews, and the Los "
        "Angeles Times on the voice: lifeless, not so much from beyond the grave "
        "as buried in it. **The bar works because the mask never slips; the show "
        "fails because it made the mask visible.** The two things are the same "
        "mechanism. "
        "Two harder facts. The book rewards Charlie for refusing to be greedy; the "
        "show pays three million dollars to contestants who are incentivised to "
        "scheme and calls its eliminations termination, so the figure is made to "
        "host the contest he was invented to punish. And the name has been owned "
        "by a Swiss conglomerate and an Italian confectioner in turn, and now "
        "sits inside a streaming platform that bought the Dahl catalogue outright "
        "- one invented figure, four successive owners, none of whom have met. "
        "The transparency problem is also here, in its most literal form: the "
        "invented name is the standing emblem for a real and well-documented "
        "cocoa supply chain, and it absorbs the charge. That last point is "
        "recorded as an allegation where it is one, and it is here for its "
        "structure rather than as an accusation."
    ),
    "verified": False,
    "medium": ["literature", "television_unscripted"],
    "year_end": None,
    "relations": [
        {"to": "the-brand-as-character", "type": "cites"},
        {"to": "mickey-mouse", "type": "depicts"},
        {"to": "boybands", "type": "depicts"},
        {"to": "elvis-hologram", "type": "contemporary"},
        {"to": "deepfake-grief", "type": "contemporary"},
    ],
    "sources": [],
    "media_inferred": False,
    "provenance": "sourced",
}

SOURCES = [
    ("Wikipedia, The Willy Wonka Candy Company",
     "https://en.wikipedia.org/wiki/The_Willy_Wonka_Candy_Company",
     "The mechanism's whole shape in one record: Dahl licensed the Wonka name to "
     "the director, the producer David L. Wolper convinced Quaker Oats - a "
     "porridge company with no film experience - to advance $3 million for the "
     "right to sell a Wonka bar, and the film was retitled for promotional "
     "purposes. Brand launched 17 May 1971, a month before the film opened on 30 "
     "June 1971. Ownership ran Quaker -> Sunmark -> Rowntree Mackintosh (1986) -> "
     "Nestle (1988) -> renamed Nestle Candy Shop in 2015, the Wonka name dropped -> "
     "sold to Ferrero 2018."),
    ("Wikipedia, Willy Wonka",
     "https://en.wikipedia.org/wiki/Willy_Wonka",
     "That the fictional chocolatier was made the mascot of a real confectionery "
     "brand, that real Everlasting Gobstoppers and Wonka Bars were produced, and "
     "the franchise's cast across 1971, 2005 and 2023."),
    ("Nestle UK & Ireland press release, 'Nestle Confectionery to bring the World "
     "of Wonder back to chocolate with Wonka'",
     "https://www.nestle.co.uk/en-gb/media/pressreleases/wonka",
     "The unfalsifiable figure in a press release. A GBP 3.6m media campaign in "
     "which the quoted speaker is 'Mr Willy Wonka' - 'I am sure the public will "
     "love our scrumdiddlyumptious new chocolate bars' - and a Nestle spokesperson "
     "adding 'Willy Wonka is one of the nation\'s best known characters and we "
     "wanted to do him proud.' Consumer testing found 80 per cent would probably "
     "or definitely buy against a 60 per cent product norm. There is no endorser "
     "because there is no person: the character issues the quote."),
    ("Netflix Tudum, 'Wonka's The Golden Ticket: Release Date'",
     "https://www.netflix.com/tudum/articles/the-golden-ticket-season-1-release-date-news",
     "The recursion: 12 golden-ticket winners and a partner each step through the "
     "factory gates, one series, and the series features the re-created voice of "
     "Gene Wilder as Willy Wonka with the consent of his estate."),
    ("NBC News, 'Netflix turns Willy Wonka's chocolate factory into a real-life "
     "social experiment'",
     "https://www.nbcnews.com/pop-culture/pop-culture-news/netflix-willy-wonka-golden-ticket-reality-show-ai-gene-wilder-rcna598920",
     "The two facts that make the entry. First, the moral is inverted: Dahl's "
     "Charlie is rewarded for humility and an absence of greed, while Netflix's "
     "series 'incentivizes contestants to scheme and strategize to win a $3 "
     "million prize'. Second, the production reasoning for the dead voice - "
     "Holloway: 'What would Wonka do at this point? What would Wonka say? I.e. "
     "What would Gene Wilder say?' - and that it was done with explicit approval "
     "and encouragement from his estate and wife, using ElevenLabs. Also that "
     "contestants qualified by finding a ticket hidden inside a Wonka chocolate "
     "bar, so the purchase is the entry token."),
    ("Los Angeles Times, Robert Lloyd, 'Wonka's the Golden Ticket review: Gene "
     "Wilder's AI voice is lifeless'",
     "https://www.latimes.com/entertainment-arts/tv/story/2026-09-23/wonkas-the-golden-ticket-review-netflix",
     "The reception that makes the mechanism legible. 'A lifeless voice not so "
     "much from beyond the grave as buried in it.' The critic also notes the show "
     "is a re-dressed Survivor and that the 1971 film, not a success in its own "
     "time, is what lodged in several generations' childhood memories."),
    ("Metacritic, 'Wonka's The Golden Ticket'",
     "https://www.metacritic.com/tv/wonkas-the-golden-ticket",
     "29 from 7 critic reviews, 0 per cent positive. The audience verdict on an "
     "unfalsifiable figure when the substitution was made audible."),
    ("Washington Post, 'Hershey, Nestle and Mars broke their pledges to end child "
     "labor in chocolate production'",
     "https://www.washingtonpost.com/graphics/2019/business/hershey-nestle-mars-chocolate-child-labor-west-africa",
     "The supply chain the invented name is made to stand for. More than 2m "
     "children in cocoa-growing regions per a 2015 US Labor Department report; "
     "industry deadlines in 2005, 2008, 2010 and 2015 all missed; and executives "
     "at Hershey, Mars and Nestle could not guarantee their chocolate was made "
     "without child labour - one said 'I'm not going to make those claims.' Nestle "
     "owned the Wonka brand from 1988 to 2015."),
    ("Business & Human Rights Centre / International Rights Advocates, press "
     "release of 12 February 2021",
     "https://www.business-humanrights.org/en/latest-news/usa-victims-of-child-trafficking-slavery-sue-major-chocolate-brands-incl-nestle-cargill-hershey-mars-alleging-they-knowingly-profited-from-the-forced-labor-of-children-harvesting-their-cocoa-beans",
     "RECORDED AS AN ALLEGATION. Eight Malian plaintiffs, trafficked as children "
     "to harvest cocoa in Cote d'Ivoire, sued Nestle, Cargill, Hershey, Mars, "
     "Mondelez, Barry Callebaut and Olam. Nestle owned the Wonka brand through "
     "most of that period. The companies dispute the claims and say there is no "
     "legal basis; nothing here asserts otherwise, and it is in the entry for its "
     "structure - an invented name used as the emblem for real people - rather "
     "than as an accusation about any one firm."),
]

p = ROOT / "data" / "encyclopedia.json"
enc = json.loads(p.read_text(encoding="utf-8"))
before = len(enc["entries"])
before_ids = sorted(e["id"] for e in enc["entries"])
before_keys = sorted(enc)

if any(e["id"] == NEW["id"] for e in enc["entries"]):
    print(f"  {NEW['id']} already exists; nothing to do")
    raise SystemExit(0)

print(f"  entry   : {NEW['id']}  ({NEW['title']})")
print(f"  medium  : {NEW['medium']}")
print(f"  sources : {len(SOURCES)}")
for c, u, _ in SOURCES:
    print(f"    + {c[:66]}")
    print(f"      {u[:88]}")
print(f"  relations to: {[r['to'] for r in NEW['relations']]}")

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

if len(enc["entries"]) != before + 1:
    sys.exit(f"refusing to write: entry count {before} -> {len(enc['entries'])}")
# The real question is whether anything that existed before still exists, not
# whether the first N ids are unchanged: the list is re-sorted, so an id inserted
# in the middle shifts every later one. Comparing a PREFIX to the old list is
# wrong, and it refused a correct write - an assertion that is wrong in the safe
# direction still costs a pass and teaches the reader to distrust the tool.
after_ids = {e["id"] for e in enc["entries"]}
lost = set(before_ids) - after_ids
if lost:
    sys.exit(f"refusing to write: {len(lost)} existing id(s) lost, e.g. "
             f"{sorted(lost)[:5]}")
if after_ids != set(before_ids) | {NEW["id"]}:
    sys.exit("refusing to write: the id set changed by more than one addition")
if sorted(enc) != before_keys:
    sys.exit("refusing to write: top-level keys changed")

tmp = p.with_suffix(".json.tmp")
tmp.write_text(json.dumps(enc, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
re_parsed = json.loads(tmp.read_text(encoding="utf-8"))
if len(re_parsed["entries"]) != before + 1:
    sys.exit("refusing to write: reparse did not reconcile")
if not any(e["id"] == NEW["id"] for e in re_parsed["entries"]):
    sys.exit("refusing to write: the entry is not in the reparse")
tmp.replace(p)
print(f"\nwritten. entries {before} -> {before + 1}. "
      f"verified={NEW['verified']} (nobody has stood behind these sources yet).")