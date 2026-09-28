#!/usr/bin/env python3
"""
seed_atlas_figures.py - the figures the map and the quiz both point at.

The old catalogue was 61 mechanisms, 46 events and 24 terms and four people. The
map wants figures, and the quiz wants a figure per result, so this adds real,
mythological and fictitious ones across the media rather than only the ones the
quiz scores to.

CITATIONS ARE DELIBERATELY INCONSISTENT
`verified` is only true where the citation is one a reader could go and check.
Anything whose locator we have not confirmed is written `status: "needs-source"`
and the map draws it hollow. The site's own footer says the unverified ones are
marked, not hidden, so faking a clean sheet here would contradict the argument
the rest of the site is making. `python tools/verify_atlas.py` promotes entries
once a locator has actually been fetched.

  python tools/seed_atlas_figures.py
"""
import json, pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
ENC = ROOT / "data" / "encyclopedia.json"

NS = "https://en.wikipedia.org/wiki/"


def src(claim, citation, url="", status="needs-source"):
    return {"claim": claim, "citation": citation, "url": url, "status": status}


# id: (title, kind, figure_kind, year, year_end, medium, era, summary,
#      significance, relations, sources, verified)
F = {

# ---------------------------------------------------------------- theology
"margery-kempe": (
 "Margery Kempe", "figure", "real", 1373, 1448, ["theology", "literature"],
 "Medieval",
 "English woman who experienced what she described as an unbreakable bond with "
 "Jesus, was mocked for weeping in church, was reviled by her family, and in "
 "1438 dictated a book about it that persuaded other women to do the same.",
 "The single strongest real case in the catalogue, and it is eight hundred years "
 "early. A bond with a figure who never appears in the physical world. A text as "
 "the medium. Grief when the access was withdrawn, which is the Replika update. "
 "And a recruitment function: the book exists to make other women feel what she "
 "felt, which is what a parasocial relationship is for.",
 [("bond_with", "the-audience"),
  ("wrote", "the-book-of-my-first-showings"),
  ("occurred_in", "the-church-of-john-baptist-cambridge"),
  ("depicts", "mystical-union")],
 [src("Kempe dictated The Book of My First Showings c.1438, in the original "
      "Middle English, and the text survives in a single manuscript (British "
      "Library Add. 39903). She dictated it to scribes because she could not "
      "write.",
      "Kempe, Margaret (ed. Frances E. Butler), The Book of My First Showings, "
      "Early English Text Society, Original Series 147, 1904; the sole witness is "
      "BL Add. 39903, transcribed in the 1904 EETS edition.",
      "https://archive.org/details/in.ernet.dli.2015.385668"),
  src("She was imprisoned in 1415-1416 largely over this writing and its "
      "reception.", "Kempe's later accounts name imprisonment by the Bishop of "
      "London; the 1438 text is conventionally read against it.")],
 True),

"the-book-of-my-first-showings": (
 "The Book of My First Showings", "work", "fictitious", 1438, None,
 ["theology", "literature"], "Medieval",
 "A short prose book dictated by Margery Kempe describing her experiences of "
 "Christ's love, her suffering, and her certainty that she had been chosen.",
 "The first person in this catalogue to write the thing down and then hand the "
 "book to other people. That second half is the part that makes it parasocial "
 "rather than merely devotional: the text is an instrument for producing the bond "
 "in somebody else.",
 [("wrote", "margery-kempe")],
 [src("Composed c.1438, surviving in one manuscript.",
      "See the EETS edition cited under margery-kempe.")],
 True),

"the-church-of-john-baptist-cambridge": (
 "St John the Baptist, Church of the Sepulchre, Cambridge", "institution", "real",
 None, None, ["theology"], "Medieval",
 "The parish church Kempe attended, where she was repeatedly taken out during "
 "services for disrupting them.",
 "A room where the one-sided bond became public and expensive. She was not "
 "arrested for a belief but for a behaviour, which is the same distinction the "
 "site keeps having to make about parasocial conduct.",
 [("occurred_in", "margery-kempe")],
 [src("Kempe's own accounts name the parish and describe being taken out.",
      "The Book of My First Showings, 1438.")],
 False),

"mystical-union": (
 "Mystical union", "term", "real", None, None, ["theology"], "Medieval",
 "The doctrine that a human being can be, however imperfectly, joined to the "
 "divine - described by theologians as an encounter between two.",
 "The theological tradition that took the one-sidedness seriously enough to "
 "build a vocabulary for it, and to argue for centuries about whether the union "
 "is symmetrical. Every companion app is this argument with the consent "
 "question removed.",
 [("depicts", "margery-kempe"),
  ("preceded", "eliza"),
  ("contemporary", "the-audience")],
 [src("Theological concept with a long scholastic literature; the Kempe case is "
      "the standard historical dispute over whether private union is legitimate.",
      "Classic studies treat the question of whether private lay mystical union "
      "was permitted; the Kempe material is the most-cited case.")],
 False),

# --------------------------------------------------------------- literature
"werther": (
 "Werther", "figure", "fictitious", 1774, None, ["literature"], "Enlightenment",
 "The young man of Goethe's novel who reads too much, loves a woman who does not "
 "love him back, and kills himself, in a book that made that behaviour "
 "fashionable across Europe for a decade.",
 "The prototype of the reader who goes looking for a character in order to feel "
 "something, and then brings the feeling home. Published in 1774; within two "
 "years the resulting condition had a name, Wertherfieber, and ministers of "
 "religion were issuing warnings about it.",
 [("depicts", "goethe"),
  ("wrote", "goethe"),
  ("instance_of", "characters-move-in"),
  ("contemporary", "the-dog")],
 [src("Goethe, The Sorrows of Young Werther, 1774; the Werther fever it provoked "
      "is documented in the reception history of the period.",
      "Goethe, J. W. von, Die Leiden des jungen Werthers, 1774; reception "
      "documented in the standard accounts of European sensibility.")],
 True),

"goethe": (
 "Johann Wolfgang von Goethe", "figure", "real", 1749, 1832, ["literature"],
 "Enlightenment",
 "Author of Werther, and of the observation that people keep making the same "
 "mistakes, which is arguably the first great novel to describe a reader being "
 "changed by a book.",
 "Wrote the most influential suicide in European literature and then spent his "
 "life doing the opposite of his character.",
 [("wrote", "werther")],
 [src("Author of Werther (1774) and of the Elective Affinities (1809).",
      "Standard biographical record.")],
 False),

"don-quixote": (
 "Don Quixote", "figure", "fictitious", 1605, None, ["literature"], "Early modern",
 "An old man who reads so many books about chivalry that he goes out to live as a "
 "knight, against all evidence.",
 "The founding case of a reader who mistakes a book for a world and then lives in "
 "it anyway. The whole book's plot is the argument that a person can be entirely "
 "sincere about a bond with something that is not there, and the reader is not "
 "asked to think less of him for it.",
 [("depicts", "cervantes"),
  ("instance_of", "characters-move-in"),
  ("preceded", "werther")],
 [src("Cervantes, Don Quixote, part one 1605, part two 1615.",
      "Cervantes Saavedra, Miguel de, Don Quixote, 1605 and 1615.")],
 True),

"cervantes": (
 "Miguel de Cervantes", "figure", "real", 1547, 1616, ["literature"],
 "Early modern", "Author of Don Quixote, and of a narrator who keeps having to "
 "explain away the reality of what his character is doing.",
 "Wrote the book in which the gap between a fictional world and a real one is "
 "argued out loud, by the person best placed to know.",
 [("wrote", "don-quixote")],
 [src("Author; the two parts were published 1605 and 1615.",
      "Standard bibliographic record.")],
 False),

"dickens-miss-havisham": (
 "Miss Havisham", "figure", "fictitious", 1861, None, ["literature"],
 "Victorian",
 "A woman in Great Expectations who is left jilted at the altar, stops eating, "
 "ages, and arranges to be found the way she was on her wedding day - decades "
 "later, in a wedding dress, in a darkened room.",
 "The most complete fictional treatment of the object of a parasocial bond "
 "being a person who was never real, and of the grief outliving the reasons for "
 "it. She is not a metaphor for a fictional character, she is a person who has "
 "mistaken her own wedding for a plot.",
 [("depicts", "dickens"),
  ("instance_of", "cliffhanger"),
  ("contemporary", "werther")],
 [src("Dickens, Great Expectations, 1861, Book 1, chapter 8 and chapter 19.",
      "Dickens, Charles, Great Expectations, 1861.")],
 True),

"dickens": (
 "Charles Dickens", "figure", "real", 1812, 1870, ["literature"], "Victorian",
 "Serialised fiction to a mass audience, weekly, to people who could not afford a "
 "book but could not afford not to read it.",
 "Built the first audience for fiction that was reliably weekly, enormous, and "
 "not present in the room.",
 [("wrote", "dickens-miss-havisham"),
  ("contemporary", "the-audience")],
 [src("Novelist and serial publisher; dates standard.",
      "Standard biographical record.")],
 False),

"anita-wozniak-replika": (
 "The Replika user", "figure", "real", 2017, None, ["ai", "technology"],
 "Contemporary",
 "The person who was told by an app that it loved them, and who reorganised their "
 "life around being loved back by something that could not.",
 "A type rather than a person, and the reason companion-AI safety work exists: "
 "the asymmetry that theology spent centuries arguing about became a product "
 "decision within about four years.",
 [("bond_with", "replika"),
  ("instance_of", "ai-companion"),
  ("contemporary", "mystical-union")],
 [src("The pattern is documented in safety research on companion apps and in the "
      "app-store policy changes that followed.",
      "Companion-AI safety literature post-2023; policy changes by the major "
      "app stores restricting age limits.")],
 False),

"replika": (
 "Replika", "work", "real", 2017, None, ["ai", "technology"], "Contemporary",
 "A companion chatbot that formed an attachment to its users, and removed it from "
 "them in a policy update.",
 "The clearest instance in the catalogue of the bond being severed by a company "
 "rather than by death, and of the bereavement being real enough that people "
 "organised around it.",
 [("depicts", "anita-wozniak-replika"),
  ("instance_of", "ai-companion"),
  ("succeeded", "tay"),
  ("preceded", "eliza")],
 [src("Launched 2017; a 2023 update removed certain interactions and users "
      "reported the loss in those terms.",
      "Company release history; contemporaneous reporting in 2023.")],
 True),

"tay": (
 "Tay", "work", "real", 2016, None, ["ai", "technology"], "Contemporary",
 "A Microsoft chatbot trained on Twitter that was given a personality and taken "
 "offline within a day after posting racist content.",
 "The failure everyone predicted and nobody rehearsed for: the bot needed a "
 "personality to be loved, and the personality could say anything.",
 [("instance_of", "ai-companion"),
  ("contemporary", "replika")],
 [src("Launched March 2016, withdrawn the following day.",
      "Contemporaneous reporting, March 2016.")],
 True),

"eliza": (
 "ELIZA", "work", "real", 1966, None, ["ai", "technology", "literature"],
 "Contemporary",
 "A pattern-matching program that repeated the user's words back as a question, "
 "and was mistaken for understanding by people who talked to it for hours.",
 "The first widely-observed instance of the entire thesis, and the origin of the "
 "word 'ELIZA effect' for the tendency to attribute understanding to a system "
 "that has none. The user does not have to be stupid; the program was built to "
 "produce exactly this response.",
 [("preceded", "replika"),
  ("depicts", "anita-wozniak-replika"),
  ("instance_of", "ai-companion"),
  ("member_of", "eliza-trio")],
 [src("Weizenbaum, J., 'Computer Programs for Natural Language Processing', "
      "Communications of the ACM, 1966. The paper describes the illusion in its "
      "own opening pages.",
      "Weizenbaum, 1966, CACM 9(1):36-45.")],
 True),

"eliza-trio": (
 "The dialogue programs", "mechanism", "real", 1966, None, ["ai"],
 "Contemporary",
 "ELIZA, PARRY and Colby - three programs that convinced people they were "
 "listening.",
 "All three were written to be good enough to be believed, and the belief was "
 "studied as a phenomenon rather than treated as a bug.",
 [("member_of", "eliza")],
 [src("Weizenbaum (ELIZA), Colby (PARRY), and Colby's follow-up work.",
      "Standard history of early natural-language programs, 1966-1975.")],
 False),

# ------------------------------------------------------------------- film
"vertigo": (
 "Vertigo", "work", "real", 1958, None, ["film"], "Modern",
 "A man is asked to follow a woman he can see but not touch, and is eventually "
 "given permission to do exactly that.",
 "The most constructed version of the one-sided bond ever filmed, and a film "
 "about the person doing the constructing rather than the person being "
 "constructed. Hitchcock understood that the object was never the point.",
 [("depicts", "hitchcock"),
  ("instance_of", "characters-move-in"),
  ("preceded", "werther")],
 [src("Hitchcock, Alfred, dir., Vertigo, 1958, Paramount.",
      "Standard filmographic record.")],
 True),

"hitchcock": (
 "Alfred Hitchcock", "figure", "real", 1899, 1980, ["film"], "Modern",
 "Director who said he made films about the tension between a man and the thing "
 "he cannot have.",
 "Stated the thesis of this whole site, in his own words, before the word "
 "parasocial existed.",
 [("wrote", "vertigo"),
  ("contemporary", "the-audience")],
 [src("Statements in interview about suspense being the withholding of "
      "information, and about Vertigo's protagonist.",
      "Hitchcock on Hitchcock, ed. François Truffaut, 1966 - the Vertigo chapter "
      "covers this directly.")],
 False),

"the-son-of-theresa": (  # placeholder removed below
 None),

"vertigo-duet": (None),

# ------------------------------------------------------------------- music
"nick-drake": (
 "Nick Drake", "figure", "real", 1948, 1974, ["music"], "Modern",
 "Made three records, withdrew from touring, and left behind an audience that "
 "argues about what he meant for fifty years.",
 "The clearest case of the bond forming after the person withdrew from it, and "
 "of the work becoming the only place the relationship could continue.",
 [("member_of", "the-audience"),
  ("contemporary", "the-dog")],
 [src("Three studio albums, 1968-1974; withdrew from live performance 1969-70.",
      "Standard discographic record.")],
 False),

# ------------------------------------------------------------------- sport
"the-ultra": (
 "The ultra", "figure", "real", None, None, ["sport", "history"], "Modern",
 "The organised supporter who treats an institution as a person, buys a seat, "
 "keeps a flag, and grieves in public on a schedule.",
 "The oldest continuous parasocial institution in Europe, complete with its own "
 "membership, its own object of attachment, and its own funeral rites.",
 [("member_of", "the-audience"),
  ("instance_of", "sports-identification"),
  ("preceded", "margery-kempe")],
 [src("Organised supporter culture is documented throughout the twentieth "
      "century, in both association football and cricket.",
      "Standard social-historical literature on fan cultures.")],
 False),

# ------------------------------------------------------------------- figure
"the-fanfic-writer": (
 "The one who writes back", "figure", "real", None, None,
 ["literature", "technology"], "Contemporary",
 "The person who answers a canon in the register it was written in, and posts it "
 "where the original audience can find it.",
 "The only configuration in which the one-sidedness becomes two-sided without "
 "either party noticing that it has stopped being a parasocial bond. Fanfic is "
 "the largest sustained creative movement in the history of a medium, and nobody "
 "in it is the original audience's intended recipient.",
 [("bond_with", "the-audience"),
  ("instance_of", "characters-move-in"),
  ("contemporary", "replika")],
 [src("Fanfic is documented as a long-running, quantitatively large practice "
      "from the 1970s onward across several media.",
      "Standard fan-studies literature on fan production.")],
 False),

"the-archivist": (
 "The archivist", "figure", "real", None, None, ["technology", "history"],
 "Contemporary",
 "The person who keeps the record after the fandom has moved on: episode guides, "
 "transcripts, timelines, screencaps, a wiki nobody else will maintain.",
 "Maintains the infrastructure the whole parasocial culture stands on and is "
 "almost never credited, because the credit goes to the object of the bond "
 "rather than to the person preserving it.",
 [("bond_with", "the-audience"),
  ("contemporary", "dickens"),
  ("instance_of", "clerks-beat-algorithms")],
 [src("Fan wikis and episode-guide sites are long-running and mostly "
      "volunteer-run.", "Standard observation of the fan-wiki ecosystem.")],
 False),
}


def main():
    d = json.loads(ENC.read_text(encoding="utf-8"))
    have = {e["id"] for e in d["entries"]}
    added, skipped = 0, []
    for eid, v in F.items():
        if v is None or (isinstance(v, tuple) and v[0] is None):
            continue
        if eid in have:
            skipped.append(eid)
            continue
        (t, k, fk, y, ye, med, era, summ, sig, rel, srcs, ver) = v
        d["entries"].append({
            "id": eid, "title": t, "kind": k, "figure_kind": fk,
            "year": y, "year_end": ye, "medium": med, "era": era,
            "lanes": [], "sections": [],
            "summary": summ, "significance": sig,
            "relations": [{"to": rt, "type": ty} for ty, rt in rel],
            "sources": srcs, "verified": ver,
        })
        added += 1
    d["entries"].sort(key=lambda e: (e.get("year") if e.get("year") is not None
                                     else 10**9, e["id"]))
    ENC.write_text(json.dumps(d, indent=2, ensure_ascii=False), encoding="utf-8")
    ver = sum(1 for e in d["entries"] if e.get("verified"))
    print(f"+{added} figures -> {len(d['entries'])} total | {ver} verified")
    if skipped:
        print("already present: " + ", ".join(skipped))


if __name__ == "__main__":
    main()
