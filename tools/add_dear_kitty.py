"""Add `dear-kitty`: the purest undemanded tie in the corpus, and a cog case too.

Anne Frank wrote letters to a listener who could not answer, for about two years,
and stated this site's entire definition in the first person while doing it:

    "Dear Kitty... I like writing to you most, you know that don't you,
     and I hope the feeling is mutual"

The hope for mutuality is the whole thing. She wanted it, said so, and there was
no circumstance in which it could be returned. That is a parasocial tie in one
sentence, written by somebody living it rather than describing it.

Four things the record carries that are better than the obvious reading.

  IT WAS NOT ONE LISTENER, IT WAS EIGHT. Anne addressed letters to Kitty, Pop,
  Phien, Conny, Lou, Marjan, Jettje and Emmy - a circle of correspondents, not a
  single imaginary friend. By 13 November 1942 she was writing to only Kitty, but
  the structure she had built was **a social network with no reciprocating nodes
  in it.** Every tie in it was one-sided and they were addressed to each other as
  though they might not be.

  THE LISTENERS WERE PARTLY MADE OF FICTION SHE WAS READING. Kitty, Pop, Phien,
  Conny and Lou come from the Joop ter Heul books of Cissy van Marxveldt, a real
  Dutch children's series Anne admired; Marjan, Jettje and Emmy she invented. So
  the far end is invented twice over - first the character, then the
  correspondence - which is the `imagined` shelf at its strongest and not the same
  thing as a companion who is silent.

  SHE ADDRESSED THE OBJECT AS WELL AS THE PERSON. "As long as this still exists,
  I cannot be sad" - she is speaking to the notebook about the notebook, so the
  tie is able to survive its own disappearance. That is `archive` running inside a
  `bond`, and the corpus has no other instance of it.

  AND THEN IT BECAME COLLECTIVE, WHICH IS THE COG. The diary was published in
  1947 after every member of the family but Otto Frank was dead, has sold around
  30 million copies and appears in more than 65 languages. **The most private
  one-sided conversation in the western canon turned into a mass reading
  relationship with a dead child.** Every reader is a tooth in one machine and
  none of them built it.

**And the machine got it wrong.** The most-quoted line in the world's most-read
diary is a truncation. It appears in the final notebook Anne wrote, and the United
States Holocaust Memorial Museum states plainly that it "has been taken out of
context" and that in full - about three paragraphs - "it is part of a quote about
a great deal of despair and longing." The sentence continues: "I simply can't
build up my hopes on a foundation consisting of confusion, misery, and death."

**So the most famous private sentence in the literature has been replaced by its
own opposite by people who were not there and never wrote back.** That is the
thesis of the site arriving from the one place it could not have been invented: a
one-sided text, published, and flattened into inspiration by a mass of readers for
whom it was never written. Otto Frank said he had two Annes, one his and one the
world's, and received thousands of letters afterwards - the far end acquired a
reply, addressed to a dead child, by strangers.

Asserts the entry count, the id set and the top-level keys before and after.
"""
import json
import pathlib
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ROOT = pathlib.Path(__file__).resolve().parent.parent
APPLY = "--apply" in sys.argv

NEW = {
    "id": "dear-kitty",
    "title": "I hope the feeling is mutual",
    "kind": "case",
    "year": 1942,
    "era": "The long war",
    "lanes": ["companion", "archive"],
    "sections": ["character", "companion", "brand"],
    "summary": ("Two years of letters to a listener who could not answer, written "
                "by a thirteen-year-old who said out loud that she hoped the "
                "feeling was mutual."),
    "significance": (
        "The purest instance of an undemanded tie on this site, and the only "
        "place in the corpus where somebody living inside a parasocial "
        "relationship states its definition. Anne Frank wrote to Kitty - \"Dear "
        "Kitty... I like writing to you most, you know that don't you, and I hope "
        "the feeling is mutual\" - and there was no circumstance in which it could "
        "be returned. The hoping is the whole of it, and she named it herself "
        "before anybody had a word for it.\n\n"
        "**It was a network, not a friend.** She addressed letters to eight "
        "imaginary correspondents - Kitty, Pop, Phien, Conny, Lou, Marjan, Jettje "
        "and Emmy - and by November 1942 she was writing only to Kitty, but what "
        "she had built was a social circle with **no reciprocating nodes in it**. "
        "Every tie inside it was one-sided and the correspondents were addressed "
        "as though they might yet answer. That is a structure the corpus had not "
        "described, because a single imaginary friend is the version everybody "
        "writes about.\n\n"
        "**The listeners were invented twice over.** Kitty, Pop, Phien, Conny and "
        "Lou are drawn from the Joop ter Heul books of Cissy van Marxveldt, a "
        "real Dutch children's series Anne admired; Marjan, Jettje and Emmy she "
        "made up herself. The far end is fabricated at two removes - first the "
        "character, then the correspondence - which is `imagined` at its "
        "strongest and not the same object as a companion who happens to be "
        "silent.\n\n"
        "**She addressed the object as well as the person.** \"As long as this "
        "still exists, I cannot be sad\" - she is speaking to the notebook about "
        "the notebook, so the tie survives the removal of everything it was "
        "attached to. That is `archive` operating inside a `bond`, and there is no "
        "other instance of it here.\n\n"
        "**And then it became collective, which is the other half of the entry.** "
        "The diary was published in 1947, after every member of the family but "
        "Otto Frank was dead, and has since sold something like thirty million "
        "copies in more than sixty-five languages. The most private one-sided "
        "conversation in the western canon became a mass reading relationship with "
        "a dead child. Every reader is a tooth in one machine, none of them built "
        "it, and the thing they all turn against is a notebook a teenager "
        "addressed to someone who could not write back.\n\n"
        "**And the machine got it wrong, and the error is the argument.** The most "
        "quoted line in the world's most-read diary is a truncation. It does sit "
        "in the final notebook Anne wrote, but the United States Holocaust Memorial "
        "Museum records that it \"has been taken out of context\" and that read in "
        "full - about three paragraphs - \"it is part of a quote about a great "
        "deal of despair and longing.\" What follows the famous line is: \"I simply "
        "can't build up my hopes on a foundation consisting of confusion, misery, "
        "and death.\" **The optimism is the misquotation.** The most famous "
        "private sentence in the literature has been replaced by its opposite by "
        "people who were not there and never wrote back - which is what happens "
        "when a one-sided text goes public, and it is the whole argument of this "
        "site arriving from the one place it could not have been constructed.\n\n"
        "Otto Frank said he had two Annes, one that belonged to him and one that "
        "belonged to the world, and received thousands of letters once it was "
        "published. The far end of the tie eventually acquired a reply - addressed "
        "to a dead child, in enormous volume, by strangers."
    ),
    "verified": False,
    "medium": ["literature"],
    "year_end": 1947,
    "relations": [
        {"to": "the-imaginary-friend", "type": "instance_of"},
        {"to": "mourn-a-person-you-met", "type": "contemporary"},
        {"to": "the-fourth-wall", "type": "cites"},
        {"to": "dickens", "type": "contemporary"},
        {"to": "parasocial-interaction", "type": "cites"},
    ],
    "sources": [],
    "media_inferred": False,
    "provenance": "sourced",
}

SOURCES = [
    ("Anne Frank House, \"So, who is 'Dear Kitty'?\"",
     "https://www.annefrank.org/en/anne-frank/diary/so-who-is-dear-kitty",
     "The primary institutional account and the source of the structural "
     "claims. That Kitty is the fictional character Anne addressed many letters "
     "to, first appearing 22 September 1942. That Anne wrote she wanted 'to "
     "correspond with someone' and invented EIGHT characters to do so - Kitty, "
     "Pop, Phien, Conny, Lou, Marjan, Jettje and Emmy - who in her imagination "
     "formed a circle of friends. That five came from the books of Cissy van "
     "Marxveldt and three were her own invention. That the letter form beat the "
     "conventional diary in strength by November 1942. And the line the entry is "
     "titled on: 'I like writing to you most, you know that don't you, and I hope "
     "the feeling is mutual'."),
    ("United States Holocaust Memorial Museum, Anne Frank the Writer: Interviews "
     "- Sara J. Bloomfield on the 'good at heart' quote",
     "https://www.ushmm.org/exhibition/anne-frank/htmlsite/interviews.html",
     "The misquotation, from the institution that holds the notebooks. 'That "
     "quote, you see everywhere... you see it on posters and t-shirts, and it "
     "gives the perception that in spite of it all, this woman had a very rosy "
     "view of the world.' It is in the final notebook Anne wrote, and: 'that "
     "quote has been taken out of context, and when it is read in the full "
     "context - about three paragraphs worth - one realizes that it is part of a "
     "quote about a great deal of despair and longing.' Also the episode in which "
     "Otto Frank is quoted saying he had two Annes, one that belonged to him and "
     "one that belonged to the world, and that after publication he received "
     "thousands and thousands of letters."),
    ("Wikipedia, The Diary of a Young Girl",
     "https://en.wikipedia.org/wiki/The_Diary_of_a_Young_Girl",
     "The shape of the change and the death of the biographical reading. That "
     "she begins in conventional notes and after two months switches to letters "
     "to imaginary friends, and that by 13 November 1942 she writes to Kitty "
     "alone through to her last entry in August 1944. And that the Kitty-Egyedi "
     "speculation began in the 1970s and was never supported: Kitty Egyedi "
     "herself said that once Kitty 'started to lead her own life in the diary "
     "that it ceases to matter who is meant by Kitty. The name is not meant to "
     "be me.'"),
    ("Encyclopaedia Britannica, 'Today in History: June 14 - The Day Anne Frank "
     "Started Her Diary'",
     "https://www.britannica.com/today-in-history/June-14-The-Day-Anne-Frank-Started-Her-Diary",
     "The ordinary dates and the scale of the outcome. Her first full entry to "
     "Kitty on 14 June 1942, two days after turning thirteen; two years of "
     "entries; Otto Frank publishing it in 1947 as Het Achterhuis; and the book "
     "in more than sixty-five languages."),
]

p = ROOT / "data" / "encyclopedia.json"
enc = json.loads(p.read_text(encoding="utf-8"))
before = len(enc["entries"])
before_ids = {e["id"] for e in enc["entries"]}
before_keys = sorted(enc)

if NEW["id"] in before_ids:
    print(f"  {NEW['id']} already exists; nothing to do")
    raise SystemExit(0)

print(f"  entry   : {NEW['id']}  ({NEW['title']})")
print(f"  kind    : {NEW['kind']}   year {NEW['year']}-{NEW['year_end']}")
print(f"  medium  : {NEW['medium']}")
print(f"  sources : {len(SOURCES)}")
for c, u, _ in SOURCES:
    print(f"    + {c[:70]}")
    print(f"      {u[:90]}")
print(f"  relations to: {[r['to'] for r in NEW['relations']]}")
missing = [r["to"] for r in NEW["relations"] if r["to"] not in before_ids]
if missing:
    sys.exit(f"refusing: relations point at entries that do not exist: {missing}")

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
    sys.exit(f"refusing to write: entry count {before} -> {len(enc['entries'])}")
if before_ids - after_ids:
    sys.exit(f"refusing to write: {len(before_ids - after_ids)} existing id(s) lost")
if after_ids != before_ids | {NEW["id"]}:
    sys.exit("refusing to write: the id set changed by more than one addition")
if sorted(enc) != before_keys:
    sys.exit("refusing to write: top-level keys changed")

tmp = p.with_suffix(".json.tmp")
tmp.write_text(json.dumps(enc, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
re_parsed = json.loads(tmp.read_text(encoding="utf-8"))
if len(re_parsed["entries"]) != before + 1 or \
        not any(e["id"] == NEW["id"] for e in re_parsed["entries"]):
    sys.exit("refusing to write: reparse did not reconcile")
tmp.replace(p)
print(f"\nwritten. entries {before} -> {before + 1}. verified=False.")
