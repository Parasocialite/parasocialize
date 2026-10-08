# -*- coding: utf-8 -*-
"""Add three encyclopedia entries: blues-clues, guru-disciple,
unreliable-narrator.

The three places COVERAGE-MAP marks as holes in the subject rather than in the
classification, after the media and archaeology batches:

  blues-clues          work          1996   the direct address aimed at children,
                                             measured: the pause is engineered,
                                             the answer is not required to mean
                                             anything, and it works anyway
  guru-disciple        mechanism     1650   the oldest instruction in the
                                             corpus to attend to one person
                                             continuously - "think of nothing
                                             but the guru" - filed against the
                                             priest-congregation axis the
                                             domain sweep called a gap
  unreliable-narrator  term          1961   the voice whose account you supply
                                             yourself, Booth's coinage, and the
                                             shelf fight-club already sits on

1650, 1961 and 1996 held no entry before this file ran. The relation targets
were chosen from entries whose years are already fixed in the corpus, and every
chronological edge is asserted against those years before anything is written -
the failure mode this repo has hit repeatedly is typing the verb from the way
the sentence reads. The three relation types were derived from the dates, not
from how the sentences read: guru-disciple (1650) comes before
candidacy-and-charisma (1968) as `preceded`, unreliable-narrator (1961) comes
before fight-club (1999) as `preceded`, and everything older than each of the
new entries is `succeeded`.

Every record below is `unverified`, not `retrievable`: the text was read
through a search index rather than fetched, the status reason is stated in the
claim of every record, and no locator carries a DOI, so no identity was
checked. That is the rule since the Met Museum pages returned 429. The Capper
article and both UCalgary theses were recovered by title search this session
(Capper, D. S. (2004), Journal of Contemporary Religion 19(2), 137-153;
Emory-Moore 2012; Donovan 1986), so their citations are complete even though
none of the three was opened.

Usage:  python tools/add_fourth_batch_entries.py            (dry run)
        python tools/add_fourth_batch_entries.py --apply
"""

import json
import pathlib
import sys

APPLY = "--apply" in sys.argv
P = pathlib.Path("data/encyclopedia.json")

REASON = ("Read through a search index rather than fetched, so the record is "
          "unverified: a reader can open this page, this agent did not.")
IV = ("no DOI in this locator, so identity was NOT checked - the url was "
      "returned by a search index and was not opened")

TARGET_IDS = ["blues-clues", "guru-disciple", "unreliable-narrator"]

VALID_SECTIONS = {"brand", "character", "companion", "contest", "creator",
                  "crossover", "danger", "grief", "idol", "world"}
VALID_LANES = {"application", "consideration", "manipulation"}
VALID_KINDS = {"term", "person", "work", "study", "event", "mechanism",
               "case", "institution"}
VALID_MEDIA = {"ai", "comics", "film", "games", "history", "literature",
               "music", "radio", "sport", "stage", "technology",
               "television_scripted", "television_unscripted", "theology",
               "visual_art"}
CHRONO = {"preceded": lambda own, tgt: own < tgt,
          "succeeded": lambda own, tgt: tgt < own,
          "contemporary": lambda own, tgt: own == tgt}


def src(citation, url, claim):
    return {"citation": citation, "status": "unverified", "url": url,
            "claim": claim + " " + REASON, "locator": None,
            "identity_verified": IV}


def make(id_, title, kind, year, era, lanes, sections, summary, paras,
         medium, relations, sources, year_end=None):
    e = {"id": id_, "title": title, "kind": kind, "year": year}
    if year_end is not None:
        e["year_end"] = year_end
    e.update({"era": era, "lanes": lanes, "sections": sections,
              "summary": summary, "significance": "\n\n".join(paras),
              "verified": False, "medium": medium, "relations": relations,
              "sources": sources, "media_inferred": False,
              "provenance": "sourced"})
    return e


ENTRIES = [
    make(
        "blues-clues",
        "Will you help me?",
        "work", 1996, "Television",
        ["application", "consideration"], ["companion", "character"],
        "Blue's Clues premiered in 1996 and built its method out of a pause: "
        "the host looks into the camera, asks the child a question, waits "
        "through a silence written into the script, and then behaves as "
        "though an answer arrived. Children answered anyway, watched the "
        "same episodes repeatedly, and the period's research recorded their "
        "interaction and comprehension rising with every repeat.",
        [
            "**The pause is the product, and the research of the period says "
            "so in its own terms.** Carter, Hyde and Hodgins record that the "
            "introduction of Blue's Clues in 1996 ushered in an expansion of "
            "pseudo-interaction in children's programming: the show builds a "
            "two-second pause into the exchange, asks the viewer a question "
            "into it, and behaves as though the answer landed - and the same "
            "work records three-to-five-year-olds engaging more with "
            "programmes built on waiting and repeating than with programmes "
            "that supplied feedback. That last result is the sharp edge of "
            "this entry, because it removes the thing a conversation would "
            "need: the reply did not have to be a reply. The host is not "
            "doing what a presenter does by accident either. The shelf this "
            "entry is filed under describes second-person grammar aimed at a "
            "large audience as a machine for manufacturing the feeling of "
            "being singled out, and Blue's Clues aimed that machine at "
            "children who had not yet learned there was one. The New York "
            "Times caught it running in 1997: a Monday-to-Friday schedule on "
            "which the same question arrives five days a week, a mother "
            "muddled that her young son had begun answering the television, "
            "and the programme's appeal written down in its own phrase, "
            "\"Will you help me?\".",

            "**What the audience did with it is measured, and the "
            "measurement is why the format spread.** Crawley and colleagues "
            "found that children repeatedly exposed to the show interacted "
            "with it more and comprehended more as their exposure grew, so "
            "the pause rewarded the return rather than the single viewing - "
            "and the five-day week made the return the structure of the "
            "week rather than a request. The show's own research literature "
            "states what it was measuring in its title, Researching Blue's "
            "Clues: Viewing Behavior and Impact, and this entry records "
            "that identity rather than the paper's findings, which were not "
            "read here; every number above comes from Crawley. The corpus "
            "already holds the format's ancestor: howdy-doody asked \"Say, "
            "kids, what time is it?\" to a chorus of children who could not "
            "see the clock, with the voice usually recorded before the "
            "broadcast went out, thirteen years of it. What Blue's Clues "
            "added was not the address but its object: not a catchphrase "
            "spoken to everybody, a question posed to you and held open "
            "long enough that a three-year-old could fill it in.",

            "**The counter-argument is that the mother in the 1997 piece "
            "was right to be muddled: a child answering a screen is a "
            "child being fooled, and the show is a machine for producing "
            "that mistake.** It is a real objection and it was in the "
            "papers before anyone had measured anything. The deeper "
            "version comes from the same research that supplies this "
            "entry's numbers: if feedback did not matter, there is no "
            "conversation here at all, only a timing choice the child "
            "completes - and the counter is correct about the mechanism "
            "and wrong about what it defeats. Nobody in the arrangement "
            "is claiming the far side keeps a record; the entry's claim is "
            "narrower, that the speaking-into-a-pause is itself the "
            "attachment, engineered on schedule and answered anyway, "
            "which is the condition the rest of this site documents in "
            "less deliberate settings. The afterlife settles it: the man "
            "who asked the question was still explaining it to a "
            "graduating class in 2024, decades past the run - the "
            "question outlived the format, and children are still the "
            "ones who answered it.",
        ],
        ["television_scripted"],
        [
            {"to": "saturday-mornings", "type": "succeeded"},
            {"to": "the-fourth-wall", "type": "succeeded"},
            {"to": "howdy-doody", "type": "succeeded"},
        ],
        [
            src("The New York Times, \"The Joy of Repetition, Repetition, "
                "Repetition\" (1997)",
                "https://www.nytimes.com/1997/08/03/tv/"
                "the-joy-of-repetition-repetition-repetition.html",
                "The show as the article records it: a Monday-to-Friday "
                "run on which the question arrives to the same children "
                "five days a week; a mother muddled that her young son had "
                "begun answering the television; and the programme's own "
                "appeal in the words \"Will you help me?\"."),
            src("Anderson et al. (2000), \"Researching Blue's Clues: "
                "Viewing Behavior and Impact\", Media Psychology 2(2), "
                "179-194",
                "https://doi.org/10.1207/s1532785xmep0202_4",
                "The bibliographic identity of the study of the show's "
                "viewing behaviour and impact, recorded from its record "
                "rather than from its text: the findings were not read for "
                "this entry, so every number the entry states comes from "
                "the Crawley record instead."),
            src("Crawley et al. (1999), Journal of Educational Psychology "
                "91(4)",
                "https://doi.org/10.1037/0022-0663.91.4.630",
                "That children repeatedly exposed to the show interacted "
                "with it more and comprehended more as exposure grew, "
                "recorded here from the paper's record: Journal of "
                "Educational Psychology 91(4), doi "
                "10.1037/0022-0663.91.4.630."),
            src("Carter, Hyde & Hodgins (2017), \"Investigating the Use of "
                "Interactive Features for Children's Television "
                "Programming\", ACM IDC",
                "https://dl.acm.org/doi/10.1145/3078072.3079717",
                "The interactive machinery as the study records it: the "
                "introduction of Blue's Clues in 1996 ushered in an "
                "expansion of pseudo-interaction in children's "
                "programming; the two-second pause that asks the viewer to "
                "answer is among the features it examines; and "
                "three-to-five-year-olds engage more with programmes built "
                "on waiting and repeating than with programmes that "
                "supplied feedback."),
            src("Today, \"Steve Burns Blue's Clues commencement speech\" "
                "(2024)",
                "https://www.today.com/popculture/news/"
                "steve-burns-blues-clues-commencement-speech-rcna153314",
                "The commencement address of 2024 as reported: Steve "
                "Burns, decades after the programme, still recounting the "
                "question that made it - \"Will you help me?\" - to a "
                "graduating class."),
        ],
    ),

    make(
        "guru-disciple",
        "Think of nothing but the guru",
        "mechanism", 1650, "Faith",
        ["application", "consideration"], ["world", "crossover"],
        "Guru devotion asks a disciple to hold one teacher in mind without "
        "pause - moving, walking, sleeping, sitting, happy or miserable - "
        "and the Tibetan tradition makes it indispensable to the path "
        "rather than optional. The Gelug-pa school's principal guru-puja "
        "was compiled in the mid-seventeenth century, which is the date "
        "this entry carries; the practice it regularises is older than the "
        "book.",
        [
            "**The oldest instruction in this corpus to attend to one "
            "person continuously, and it has a library behind it.** Capper "
            "records the tradition's own formula in full: \"Moving, "
            "walking, sleeping, sitting, happy or miserable, continuously "
            "think of nothing but the guru!\" - the sentence this entry's "
            "title takes its words from. What looks from outside like "
            "reverence is recorded inside as infrastructure: \"Personal "
            "devotion to a guru in Tibetan Buddhism is, in contradistinction "
            "to some other forms of Buddhism, essential for traversing the "
            "liberative path to nirvana\", the tradition's social text is "
            "the Fifty Verses of Guru-Devotion attributed to Asvaghosa, and "
            "at the field site Capper studied \"All Buddhist practices at "
            "Siddha Gompa revolve around this devotion.\" The relationship "
            "is, in his words, \"inherently hierarchical\" - and the entry "
            "takes its date from the same tradition's book rather than from "
            "the practice, because the book can be dated and the practice "
            "cannot. Emory-Moore's structural analysis gives the Gelug-pa "
            "school's principal ritual text the Bla-ma mchod-pa, "
            "\"Offering to the Spiritual Guide\", \"compiled by Losang "
            "Chokyi Gyaltsan (1570-1662) in the mid-seventeenth century\", "
            "which is where 1650 comes from. The honesty note is on the "
            "entry rather than hidden: the practice is older than its "
            "text - Tsongkhapa's own instruction on how to rely on the "
            "teacher predates it, and Donovan's survey of all four Tibetan "
            "schools rests on guru-devotion rituals whose documented "
            "lineage runs back to Gling-ras-pa Pad-ma-rdo-rje "
            "(1128-1188), four and a half centuries before this entry's "
            "date. A dated text is an anchor, not a birth.",

            "**The tradition's own account refuses the reading that turns "
            "the disciple into a prop.** Capper is explicit that the "
            "hierarchy is instrumental rather than terminal: \"in Tibetan "
            "Buddhist theory, enchantment exploits hierarchical "
            "relationships as a means, not an end\", and \"Lamas tirelessly "
            "reiterate that the goal of the practice is to become a lama "
            "oneself.\" His ethnography states the finding against the "
            "expected one: \"Rather than being automatons for a "
            "charismatic leader, many of these Buddhists critically employ "
            "submission to their lama to attempt their own personal and "
            "religious empowerment\" - and his record of what the "
            "hierarchy did to them is that it \"aided, not stifled, their "
            "development of a sense of personal empowerment\". "
            "Emory-Moore's structural reading supplies the mechanism "
            "underneath: guru yoga is \"a system of exchange defined by a "
            "distinct logic: the binary of guru/disciple mediated by the "
            "gift (offerings given, blessings received)\", inside a "
            "relation in which \"the guru is seen to have subjugated that "
            "to which the disciple's identity remains subject\". So the "
            "near side gives, asks and receives in a relationship it "
            "entered, and the asymmetry that remains is the one the entry "
            "is about: devotion sustained in one direction, by instruction, "
            "for life.",

            "**The counter-argument is that the relationship is unhealthy "
            "by design, and Capper records the critique without "
            "softening it.** Critics of the arrangement describe the "
            "dynamic as \"inherently unhealthy for supposedly "
            "independence-minded Americans\", and he notes that academic "
            "studies of it have often \"arrive[d] at their conclusions by "
            "understanding submission to the guru as the goal\" - the "
            "submission read as the point rather than as the means his "
            "fieldwork found. That is a real dispute about the "
            "arrangement's value and this entry does not settle it; what "
            "it attaches to is narrower and is present whichever side of "
            "the dispute is right. The instruction itself - continuous "
            "attention to one person who owes you nothing - is the most "
            "total demand for one-sided attention anywhere in this "
            "corpus: it does not ask for a reply, because the practice is "
            "the holding of the thought, and it is dated here from the "
            "book that first wrote the discipline down. The priest entry "
            "is the arrangement's neighbour and its contrast: \"The most "
            "complete parasocial arrangement available and it includes a "
            "uniform, a script and a confession\" - the guru has no "
            "uniform and no parish, which is precisely why the tie sits "
            "on the shelf for standing rather than for office.",
        ],
        ["theology"],
        [
            {"to": "the-priest", "type": "succeeded"},
            {"to": "congregation", "type": "succeeded"},
            {"to": "candidacy-and-charisma", "type": "preceded"},
        ],
        [
            src("Capper, D. S. (2004), \"Enchantment with Tibetan Lamas in "
                "the United States\", Journal of Contemporary Religion "
                "19(2), 137-153",
                "https://aquila.usm.edu/cgi/viewcontent.cgi?article=16183"
                "&context=fac_pubs",
                "Guru devotion in the Tibetan tradition as this essay "
                "records it: personal devotion to a guru \"essential for "
                "traversing the liberative path to nirvana\" and "
                "distinguished on that point from other forms of "
                "Buddhism; the instruction \"Moving, walking, sleeping, "
                "sitting, happy or miserable, continuously think of "
                "nothing but the guru!\"; the tradition's social text as "
                "Fifty Verses of Guru-Devotion attributed to Asvaghosa; "
                "the lama-disciple relationship \"inherently "
                "hierarchical\"; \"All Buddhist practices at Siddha Gompa "
                "revolve around this devotion\"; the tradition's "
                "insistence that \"the goal of the practice is to become a "
                "lama oneself\"; the finding that the hierarchy \"aided, "
                "not stifled\" disciples' personal empowerment; and the "
                "record of disciples who \"critically employ submission "
                "to their lama to attempt their own personal and "
                "religious empowerment\" rather than serving as automatons."),
            src("Emory-Moore, C. (2012), \"The Systematic Dynamics of Guru "
                "Yoga in Euro-North American Gelug-pa Formations\", "
                "master's thesis, University of Calgary",
                "https://ucalgary.scholaris.ca/bitstreams/"
                "6b9d1286-1cf3-41f8-94f5-86e3ed2ec258/download",
                "The dating this entry rests on: the Gelug-pa school's "
                "principal ritual text, the Bla-ma mchod-pa "
                "(\"Offering to the Spiritual Guide\"), \"compiled by "
                "Losang Chokyi Gyaltsan (1570-1662) in the mid-seventeenth "
                "century\"; plus the structural reading of guru yoga as \"a "
                "system of exchange defined by a distinct logic: the "
                "binary of guru/disciple mediated by the gift (offerings "
                "given, blessings received)\" and the relation of standing "
                "recorded as \"the guru is seen to have subjugated that to "
                "which the disciple's identity remains subject\"."),
            src("Donovan, M. A. (1986), \"Guru devotion in Tibetan "
                "Buddhism\", master's thesis, University of Calgary",
                "https://ucalgary.scholaris.ca/items/"
                "30908cdd-3d93-4add-a522-caee9a9f5bf3",
                "That devotion to the guru is a central feature of Tibetan "
                "Buddhism across the schools surveyed, that the guru held "
                "an exalted position in Hinduism and Indian Buddhism "
                "before it, and that the thesis's third chapter is the "
                "first complete translation of a ritual of guru devotion "
                "by Gling-ras-pa Pad-ma-rdo-rje (1128-1188) - the record "
                "that the practice's textual lineage runs to the twelfth "
                "century, well before this entry's date."),
            src("CJBS, \"Structural Analysis: Losang Chokyi Gyaltsan's Guru "
                "Puja\" (2017)",
                "https://cjbuddhist.wordpress.com/2017/07/27/"
                "structural-analysis-losang-chokyi-gyaltsan-guru-puja/",
                "A structural analysis of the same guru-puja text this "
                "entry dates from, recorded for the reading it gives of "
                "the disciple's part in the ritual: what the disciple "
                "gives, asks for and receives from the guru."),
        ],
    ),

    make(
        "unreliable-narrator",
        "The voice you distrust",
        "term", 1961, "Criticism",
        ["application", "consideration"], ["character"],
        "Wayne C. Booth coined unreliable narrator in The Rhetoric of "
        "Fiction in 1961: a narrator who does not speak for the norms of "
        "the work, judged against an implied author the reader constructs. "
        "Sixty years of argument later the term still describes the "
        "situation plainly - you are inside a voice you cannot verify, and "
        "nobody will correct you.",
        [
            "**The term was coined in 1961 and spent the decades since "
            "being argued with, including by its author.** Booth's "
            "definition is one line and it decides by reference to "
            "somebody who is never on the page: \"I have called a "
            "narrator reliable when he speaks for or acts in accordance "
            "with the norms of the work (that is, the implied author's "
            "norms), unreliable when he does not.\" The reliable "
            "distinction is therefore not a property the reader can "
            "check in the story; it is a verdict reconstructed from the "
            "shape of the telling, by a reader standing alone with it. "
            "The essay read for this entry opens by recording the "
            "distance the term has travelled - sixty years have passed "
            "since Wayne C. Booth conceptualized narrative unreliability - "
            "and traces Booth's own 1983 return to it as well as the "
            "expansions the concept has received since, which is the "
            "honest state of the word: coined once, revised by its "
            "coiner, extended by everyone else. The corpus keeps the "
            "coinage and its date, because the year is checkable and the "
            "boundaries are not.",

            "**Why it belongs on this site rather than in a craft "
            "manual: the reliability of a narrator is maintained entirely "
            "by the reader, which is this site's structure applied to a "
            "voice.** No character in a story can be persuaded to "
            "reconsider; no implied author can be reached for "
            "clarification; and as the fictional-protagonist shelf's "
            "mechanism has it, \"because the text never closes the "
            "account the audience is never caught being wrong\" - the "
            "unreliable case is that mechanism with the volume up, "
            "because now the audience is not merely filling in an "
            "interior but auditing one, from outside, forever. The "
            "corpus's instance is fight-club, whose Narrator the entry "
            "quotes directly: \"The Narrator, an unreliable narrator, is "
            "not immediately aware that he is mentally projecting "
            "Tyler\" - a speaker whose account is the only account there "
            "is, contradicted by nobody, believed by the reader for two "
            "hours on the strength of nothing but the telling. Booth's "
            "own 1961 framing suits this reading: the judgement falls to "
            "the implied author, and the implied author is a thing the "
            "reader builds to have somebody to trust.",

            "**The counter-argument is that unreliability is a property "
            "of texts rather than of relationships, and that filing it "
            "here confuses a narrative device with a bond.** It is the "
            "strongest objection available and it is half right: there "
            "is no far side scheming to be believed, and every other "
            "entry on this site has at least a figure on the other end. "
            "It loses on what the reader is actually doing. Distrust "
            "spent on a narrator has the same anatomy as every tie this "
            "site files - attention paid unilaterally, an account "
            "supplied without the far side's knowledge or consent, and a "
            "correction that never arrives - and the term itself names "
            "the reader's half of it rather than the writer's. The "
            "fourth-wall entry, dated to Diderot in 1758, describes the "
            "arrangement from the outside: the wall is the fiction's "
            "silence. The unreliable narrator is the voice inside that "
            "silence the listener cannot audit, and the audience's "
            "response is the same in both cases - it keeps attending. "
            "Filed beside fight-club on the written-character shelf, "
            "where the account that never closes is the shelf's own "
            "mechanism; the counter `character/played-role` loses "
            "because the doubt here is aimed at a narrator rather than "
            "at a performer, and the reader has no actor to hold. "
            "Contestable, and recorded as such.",
        ],
        ["literature"],
        [
            {"to": "the-fourth-wall", "type": "succeeded"},
            {"to": "fight-club", "type": "preceded"},
        ],
        [
            src("Alvarez-Amoros, A. (2021), Poetica 52, 361-386",
                "https://personal.ua.es/jalvarez/texts/article_revisiting."
                "pdf",
                "The essay's record: sixty years have passed since Wayne "
                "C. Booth conceptualized narrative unreliability; the 1961 "
                "coinage in The Rhetoric of Fiction; Booth's own 1983 "
                "return to the term; and the expansions of the concept "
                "since."),
            src("Wikipedia, \"Unreliable narrator\"",
                "https://en.wikipedia.org/wiki/Unreliable_narrator",
                "Booth's definition as the article records it - \"I have "
                "called a narrator reliable when he speaks for or acts in "
                "accordance with the norms of the work (that is, the "
                "implied author's norms), unreliable when he does not\" - "
                "the coinage attributed to The Rhetoric of Fiction (1961), "
                "and the later taxonomies of the concept (Phelan, "
                "Nunning) the article sets out."),
            src("Wiktionary, \"unreliable narrator\"",
                "https://en.wiktionary.org/wiki/unreliable_narrator",
                "The primary quotation the dictionary records for the "
                "phrase: Booth's reliable/unreliable definition from The "
                "Rhetoric of Fiction with its page numbers, 158-159."),
        ],
    ),
]


def main():
    raw = P.read_bytes()
    text = raw.decode("utf-8")

    # The byte format is the gate on this script. Re-serialising the file we
    # have just read must reproduce it exactly, or the rewrite below is a
    # reformat rather than an addition.
    ent = json.loads(text)
    rebuilt = json.dumps(ent, ensure_ascii=False, indent=2)
    if rebuilt.replace("\n", "\r\n").encode("utf-8") != raw:
        sys.exit("refusing: data/encyclopedia.json is not the CRLF/indent-2 "
                 "form this script round-trips; nothing written")
    if not raw.endswith(b"}"):
        sys.exit("refusing: file does not end at the closing brace")

    before_keys = sorted(ent)
    before_ids = [e["id"] for e in ent["entries"]]
    before = len(ent["entries"])
    by_id = {e["id"]: e for e in ent["entries"]}
    missing = sorted({r["to"] for e in ENTRIES for r in e["relations"]}
                     - set(by_id) - set(TARGET_IDS))
    if missing:
        sys.exit(f"refusing: relation target(s) not in the corpus: {missing}")

    # Idempotent: drop anything we are about to replace, then append.
    already = len(set(before_ids) & set(TARGET_IDS))
    ent["entries"] = [e for e in ent["entries"] if e["id"] not in TARGET_IDS]

    for e in ENTRIES:
        if e["id"] not in TARGET_IDS:
            sys.exit(f"refusing: {e['id']} is not an intended target")
        if e["sections"] and not set(e["sections"]) <= VALID_SECTIONS:
            sys.exit(f"refusing: {e['id']} has an unknown section")
        if not set(e["lanes"]) <= VALID_LANES:
            sys.exit(f"refusing: {e['id']} has an unknown lane")
        if e["kind"] not in VALID_KINDS:
            sys.exit(f"refusing: {e['id']} has an unknown kind")
        if not set(e["medium"]) <= VALID_MEDIA:
            sys.exit(f"refusing: {e['id']} has an unknown medium")
        if e["verified"] or e["media_inferred"] or e["provenance"] != "sourced":
            sys.exit(f"refusing: {e['id']} claims a reading it does not have")
        if not e["sources"]:
            sys.exit(f"refusing: {e['id']} has no source records")
        if e["significance"].strip() == "" or len(e["summary"]) > 420:
            sys.exit(f"refusing: {e['id']} is empty or over-long")
        if any(s["status"] != "unverified" for s in e["sources"]):
            sys.exit(f"refusing: {e['id']} claims a reading it does not have")
        if any("reason" in s["claim"].lower() for s in e["sources"]):
            sys.exit(f"refusing: {e['id']} has a placeholder claim")

    ent["entries"].extend(ENTRIES)
    ent["entries"].sort(key=lambda e: e["id"])
    after = {e["id"] for e in ent["entries"]}

    if len(ent["entries"]) != before - already + len(TARGET_IDS):
        sys.exit(f"refusing: entry count {before} -> {len(ent['entries'])}")
    if set(before_ids) - after:
        sys.exit("refusing: an existing id was lost")
    if after != set(before_ids) | set(TARGET_IDS):
        sys.exit("refusing: id set changed by more than the additions")
    if sorted(ent) != before_keys:
        sys.exit("refusing: top-level keys changed")

    # Chronology, in the direction citation_audit.py enforces.
    full = {e["id"]: e for e in ent["entries"]}
    for e in ENTRIES:
        for r in e["relations"]:
            tgt = full[r["to"]]
            if r["to"] == e["id"]:
                sys.exit(f"refusing: {e['id']} relates to itself")
            if r["type"] not in CHRONO:
                sys.exit(f"refusing: {e['id']} uses unknown type {r['type']}")
            own_y, tgt_y = e["year"], tgt["year"]
            if not isinstance(own_y, int) or not isinstance(tgt_y, int):
                sys.exit(f"refusing: {e['id']} -> {r['to']} has no year")
            if not CHRONO[r["type"]](own_y, tgt_y):
                sys.exit(f"refusing: {e['id']} ({own_y}) {r['type']} "
                         f"{r['to']} ({tgt_y}) is false of the dates")
            print(f"  {r['type']:12s} {e['id']} ({own_y}) -> {r['to']} "
                  f"({tgt_y})  ok")

    print(f"\n  {'APPLY' if APPLY else 'DRY RUN'}: {before} -> "
          f"{len(ent['entries'])} entries")
    for e in ENTRIES:
        print(f"    {e['id']:24s} {e['kind']:10s} {e['year']}"
              f"{'-' + str(e['year_end']) if e.get('year_end') else ''}  "
              f"era={e['era']!r} media={e['medium']} sec={e['sections']} "
              f"lanes={e['lanes']}")
        print(f"      title {e['title']!r}")
        print(f"      summary {len(e['summary'])}ch  "
              f"significance {len(e['significance'])}ch  "
              f"sources {len(e['sources'])} "
              f"(all unverified: {all(s['status'] == 'unverified' for s in e['sources'])})")

    if not APPLY:
        print("\ndry run. re-run with --apply")
        return

    out = json.dumps(ent, ensure_ascii=False, indent=2).replace("\n", "\r\n")
    P.write_bytes(out.encode("utf-8"))

    # Round-trip the bytes we just wrote, and re-parse them.
    again = P.read_bytes()
    if again.endswith(b"\r\n") or again.endswith(b"\n"):
        sys.exit("refusing: wrote a trailing newline the source did not have")
    reparsed = json.loads(again.decode("utf-8"))
    if len(reparsed["entries"]) != len(ent["entries"]):
        sys.exit("refusing: re-parse disagrees with what was written")
    if sorted(reparsed) != before_keys:
        sys.exit("refusing: top-level keys changed after write")
    print(f"\nwrote {P} ({len(again)} bytes, {before} -> "
          f"{len(reparsed['entries'])} entries)")


if __name__ == "__main__":
    main()
