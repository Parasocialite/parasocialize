# -*- coding: utf-8 -*-
"""Add three encyclopedia entries: pamela, mister-rogers, betty-crocker.

The three subjects of the fifth batch, chosen by the agent rather than named by
a map, to widen the media the corpus actually carries (the bi-daily plan walks
the `medium` axis, and literature / television / radio are the homes each one
takes):

  pamela           work   1740   the reader put in the seat of the parents -
                                 a correspondence read from the far end, in the
                                 first English best-seller
  mister-rogers    work   1968   direct address to the youngest viewer, slow on
                                 purpose, offered as mutuality in the song and
                                 one-sided in fact
  betty-crocker    person 1921   a corporation given a name so that a customer
                                 relationship would have a subject; the reply
                                 was real labour, the correspondent was not

1740, 1968 and 1921 held no entry before this file ran. The relation targets
were chosen from entries whose years are already fixed in the corpus, and every
chronological edge is asserted against those years before anything is written.
Structural verbs (`instance_of`) are allowed and are not dated; only
preceded/succeeded/contemporary are checked, which is the direction
citation_audit.py enforces.

Every record below is `unverified`, not `retrievable`: the text was read through
a search index rather than fetched, the status reason is stated in the claim of
every record, and no locator carries a DOI, so no identity was checked.

Usage:  python tools/add_fifth_batch_entries.py            (dry run)
        python tools/add_fifth_batch_entries.py --apply
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

TARGET_IDS = ["pamela", "mister-rogers", "betty-crocker"]

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
STRUCTURAL = {"instance_of", "depicts", "cites", "wrote", "member_of",
              "bond_with", "occurred_in"}


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
        "pamela",
        "Virtue rewarded",
        "work", 1740, "Enlightenment",
        ["application", "consideration"], ["character", "companion"],
        "The novel that turned its readers into a correspondent. Pamela "
        "Andrews writes home about her master's pursuit, and the reader takes "
        "the seat of the parents - receiving every letter, sending none. "
        "Published anonymously in November 1740, it became the first English "
        "best-seller and the first novel whose readers wrote back demanding "
        "more of it.",
        [
            "**The form is a correspondence the reader reads from the far end "
            "of.** Richardson was a printer who took a commission in 1739 to "
            "compile a volume of model \"familiar letters\" for people too "
            "unskilled to write their own, and the germ of Pamela was a short "
            "run of letters from a servant daughter asking her father's "
            "advice about her master's advances. He kept the epistolary shape "
            "and changed its address: the letters are written not to a lover "
            "but to Pamela's parents, who are offstage, at a distance, and "
            "never answer inside the book. The reader is put in that seat - "
            "handed a life in letters addressed to somebody else, with no way "
            "to write back - which is this site's subject arriving in the "
            "first novel most of its readers ever meet.",

            "**The reception is a record of attachment, and it is unusually "
            "well documented.** The book is, on the Cambridge edition's own "
            "description, \"perhaps the most influential novel published in "
            "Britain in the eighteenth century\" and \"on its first "
            "publication in 1740 ... an immediate bestseller\"; it ran to five "
            "editions in its first year and produced what the University of "
            "Michigan project calls a \"'Pamela' rage,\" with Pamela motifs on "
            "teacups and fans. The world was said to divide into \"Pamelists "
            "and Antipamelists.\" A village blacksmith, the oft-repeated "
            "anecdote runs, read it aloud on his anvil through the summer "
            "evenings to an attentive crowd and set the parish bells ringing "
            "at the happy ending. And the readers did not stay passive: the "
            "unauthorized continuations and parodies - Fielding's Shamela, "
            "Haywood's Anti-Pamela, Kelly's Pamela's Conduct in High Life - "
            "drew a sequel from Richardson himself, Pamela in her Exalted "
            "Condition, in 1742. The audience's want bent the text.",

            "**The counter-argument is that Pamela belongs to the history of "
            "the novel, not to this site: its importance is form, consent and "
            "class, and the people who wrote back wrote to Richardson, not to "
            "a girl who never existed.** It is a fair objection and the "
            "entry's claim is narrower than it looks. What it files is a "
            "structure - a one-sided correspondence the reader reads from the "
            "parents' end - and a documented public that formed an attachment "
            "and then wrote to keep it going. The letters in the book are "
            "addressed to figures who cannot reply; the letters out of the "
            "book were addressed to a man who could, and did, and wrote two "
            "more volumes because of them. Both are this site's shape. "
            "Contestable, and recorded as such.",
        ],
        ["literature"],
        [
            {"to": "parasocial-interaction", "type": "instance_of"},
            {"to": "werther", "type": "preceded"},
            {"to": "nancy-drew", "type": "preceded"},
        ],
        [
            src("Richardson, S., \"Pamela; or, Virtue Rewarded\" (1740), "
                "Project Gutenberg ebook 6124",
                "https://www.gutenberg.org/ebooks/6124",
                "The work and its form as the record states them: an "
                "epistolary novel published in 1740 in which the fifteen-"
                "year-old maidservant Pamela Andrews recounts, through "
                "letters and journal entries, her employer Mr. B's persistent "
                "advances; and the Gutenberg introduction's account of "
                "Richardson the printer taking a commission to write a volume "
                "of model \"familiar letters,\" out of which the plot and the "
                "epistolary form came."),
            src("Introduction to Pamela, Project Gutenberg",
                "https://www.gutenberg.org/files/24860/24860-h/24860-h.htm",
                "The publication history the introduction sets out: "
                "Richardson's own editions running (1) November 6, 1740, "
                "(2) February 14, 1741, and onward; the first public "
                "reference to Pamela, an advertisement in The Weekly "
                "Miscellany on October 11, 1740; and the introductory letters "
                "written by Jean Baptiste de Freval, William Webster and "
                "Aaron Hill rather than by Richardson."),
            src("Cambridge University Press, \"Pamela: Or, Virtue Rewarded\" "
                "(critical edition)",
                "https://www.cambridge.org/core/books/pamela-or-virtue-"
                "rewarded/49FC58F01F61FF1FE4569A2532FE9168",
                "The two phrases this entry leans on: that Pamela is "
                "\"perhaps the most influential novel published in Britain in "
                "the eighteenth century,\" and that on its first publication "
                "in 1740 \"it became an immediate bestseller.\""),
            src("University of Michigan, \"Pamela, the novel\"",
                "https://websites.umich.edu/~ece/student_projects/"
                "pamela_illustrated/pamela.htm",
                "That Pamela was the first example of the best-seller "
                "phenomenon in English fiction; that there was a \"'Pamela' "
                "rage,\" with Pamela motifs on teacups and fans as Margaret "
                "Ann Doody reports; the germ of the novel in the model-letter "
                "commission; and the December 1741 sequel written in response "
                "to criticisms, parodies and spurious continuations."),
            src("The Telegraph, \"Rediscovering Pamela, the 1740 blockbuster\""
                " (17 January 2019)",
                "https://www.telegraph.co.uk/books/what-to-read/"
                "rediscovering-pamela-1740-blockbuster-pure-metoo/",
                "That Pamela ran to five editions in its first year of "
                "publication; that there was Pamela merchandise \"in the "
                "shape of fans, cups and pictures\"; and that there was talk "
                "\"of the world being divided into Pamelists and "
                "Antipamelists.\""),
            src("Wikipedia, \"Pamela; or, Virtue Rewarded\"",
                "https://en.wikipedia.org/wiki/Virtue_Rewarded",
                "The blacksmith anecdote \"repeated in varying forms since "
                "1777\" - the novel read aloud on an anvil to a village "
                "audience, the parish bells rung at the happy ending; the "
                "Pamela-themed artefacts (prints, paintings, waxworks, a fan, "
                "and a set of playing cards); the sequel Pamela in her "
                "Exalted Condition (1742); and the parodies Shamela and "
                "Anti-Pamela."),
        ],
    ),

    make(
        "mister-rogers",
        "Won't you be my neighbor?",
        "work", 1968, "Television",
        ["application", "consideration"], ["companion"],
        "Fred Rogers went national on public television on 19 February 1968 "
        "and spent thirty-three years talking, slowly, into the camera at "
        "children aged two to five. The show's offer is mutual in its own "
        "words - \"Won't you be my neighbor?\" - and its host insisted he was "
        "not acting a character, only sharing his real self. The bond was "
        "engineered, and returned by people who could not answer.",
        [
            "**The address was deliberate, slow and aimed at the youngest "
            "viewer, and the show's own research treats the screen as a "
            "face.** Rogers spoke directly into the lens and, as the show's "
            "article records, made a point of behaving \"naturally on camera "
            "rather than acting out a character\": \"One of the greatest gifts "
            "you can give anybody is the gift of your honest self. I also "
            "believe that kids can spot a phony a mile away.\" The pace was a "
            "design choice. Discussing it, Rogers quoted the program's own "
            "finding - \"the younger the child, the more interested they are "
            "in the program when my face is on the screen\" - and reached the "
            "comparison this entry is built on: \"the younger children might "
            "consider the television screen as another mother's face.\" The "
            "show went to hard places on purpose: in the summer of 1968, "
            "after Robert F. Kennedy was shot, it had the puppet Daniel "
            "Striped Tiger ask what assassination meant, because Rogers "
            "thought small children would feel the adults' fear and deserved "
            "to be spoken to.",

            "**The offer is mutual in the song and one-sided in fact.** "
            "\"Won't you be my neighbor?\" asks a question the viewer answers "
            "by watching, and the closing line reassures a child that "
            "\"there's only one person in the whole world that's like you, "
            "and that's you.\" That is the fourth wall stepped through on "
            "purpose - and unlike the fictional figures this site usually "
            "files, Rogers staked the whole thing on the speaker being a real "
            "man rather than a character. The attachment shows in what "
            "viewers did with it: families reported children donning a "
            "sweater and sneakers when the theme music began, and one of "
            "Rogers' cardigans now hangs in the Smithsonian. Thirty-three "
            "years, and the format stayed, in the same article's word, "
            "\"virtually unchanged.\"",

            "**The counter-argument is that this is ordinary children's "
            "television and Rogers would have refused the frame.** He spent "
            "his life insisting on honesty and would not have claimed his "
            "viewers had a relationship with him, only that he spoke to them "
            "truthfully. It loses on the structure rather than on the "
            "sentiment: the address runs one way, a child's reply - a shout "
            "at the screen, a sweater - does not reach the set, and the "
            "program's own research treats the young viewer's attention to "
            "the face as the thing being built. He is the honest ancestor of "
            "the engineered pause that arrives in children's television later "
            "in the century: the show came after howdy-doody and before "
            "Blue's Clues, and this shelf is the address, not the puppets. "
            "Contestable, and recorded as such.",
        ],
        ["television_scripted"],
        [
            {"to": "howdy-doody", "type": "succeeded"},
            {"to": "the-fourth-wall", "type": "succeeded"},
            {"to": "blues-clues", "type": "preceded"},
        ],
        [
            src("NPR / Fresh Air, \"It's A Beautiful 50th Birthday For "
                "'Mister Rogers' Neighborhood'\" (19 February 2018)",
                "https://www-s1.npr.org/2018/02/19/586180373/"
                "its-a-beautiful-50th-birthday-for-mister-rogers-neighborhood",
                "The premiere date as reported - Fred Rogers going national "
                "on public television on February 19, 1968 - and the "
                "quotations this entry uses: Rogers on honesty (\"Every one "
                "of us longs to be in touch with honesty\") and on the "
                "program's research (\"the younger the child, the more "
                "interested they are ... when my face is on the screen\"; "
                "\"the younger children might consider the television screen "
                "as another mother's face\"); the summer-1968 prime-time "
                "segment in which Daniel Striped Tiger asks the definition of "
                "\"assassination\" after Robert F. Kennedy was shot; and the "
                "sweater-and-sneakers routine children imitated."),
            src("Wikipedia, \"Mister Rogers' Neighborhood\"",
                "https://en.wikipedia.org/wiki/Mister_Rogers%27_Neighborhood",
                "That the American national debut was February 19, 1968; that "
                "during each segment Rogers \"spoke directly to the viewer\" "
                "and \"made a point simply to behave naturally on camera "
                "rather than acting out a character,\" with the quotation "
                "\"One of the greatest gifts you can give anybody is the gift "
                "of your honest self. I also believe that kids can spot a "
                "phony a mile away\"; the format remaining \"virtually "
                "unchanged\" for the whole run; the closing \"There's only "
                "one person in the whole world that's like you\" reassurance; "
                "and that one of Rogers' sweaters hangs in the Smithsonian."),
            src("Wikipedia, \"Fred Rogers\"",
                "https://en.wikipedia.org/wiki/Fred_Rogers",
                "The biographical frame: Fred McFeely Rogers (1928-2003), "
                "Presbyterian minister and host of Mister Rogers' "
                "Neighborhood, which began airing nationally in 1968 and ran "
                "for 895 episodes; and that a special segment dealing with "
                "the assassination of Robert F. Kennedy aired on June 7, "
                "1968, two days after the assassination."),
            src("The Mister Rogers' Neighborhood Archive, \"Episode 0001\"",
                "https://www.neighborhoodarchive.com/mrn/episodes/0001/",
                "The first episode's air date (February 19, 1968) and its "
                "contents: Rogers talking about learning to tie his shoes as "
                "he changes into his sneakers, and singing \"I Like You As "
                "You Are.\""),
        ],
    ),

    make(
        "betty-crocker",
        "Cordially yours, Betty Crocker",
        "person", 1921, "Marketing",
        ["application", "consideration"], ["brand", "character"],
        "In 1921 a flour company's advertising department needed one woman's "
        "name for the kitchen advice its all-female home-service staff was "
        "already writing. Betty Crocker was a signature and a persona, not a "
        "person: she answered letters, then took a radio voice in 1924, and "
        "gave millions a correspondent who signed herself \"Cordially "
        "yours.\"",
        [
            "**The reply existed before the name did.** In late October 1921 "
            "Gold Medal Flour ran a jigsaw-puzzle advertisement in The "
            "Saturday Evening Post; Washburn-Crosby received 30,000 completed "
            "puzzles and, with them, several hundred letters of cooking "
            "questions. The advertising department asked the board to create "
            "a personality that the women answering the letters could all "
            "sign, as the company's own account puts it. \"Crocker\" honoured "
            "a retired company director, William G. Crocker; \"Betty\" was "
            "chosen because it sounded friendly; employees competed to submit "
            "the signature and Florence Lindberg's was adopted, and is still "
            "in use. The replies, written by a home-service department of "
            "home economists, went out signed \"Cordially Yours, Betty "
            "Crocker\" - a real hand typing under a name no woman owned.",

            "**Then the persona was given a voice, which is what makes it a "
            "bond rather than a byline.** In 1924 the company helped a local "
            "radio station out of bankruptcy, renamed it WCCO, and put Betty "
            "Crocker on daytime radio's first cooking show, \"the Betty "
            "Crocker Cooking School of the Air\"; Blanche Ingersoll was its "
            "first voice, the program spread to thirteen regional stations, "
            "and from 1927 it ran on the fledgling NBC network for twenty-four "
            "years, with more than a million listeners enrolled. Each station "
            "had its own Betty Crocker reading the same scripts from "
            "Minneapolis, and letters - now from across the Midwest - kept "
            "arriving. General Mills' own description of the effect is this "
            "entry's best line: her voice on the air \"was like the woman next "
            "door dropping in for a morning visit to share a new recipe.\"",

            "**This is the brand-as-character mechanism at its founding, "
            "decades before the corpus had a name for it.** A corporation was "
            "given a face and a tone so that a customer relationship would "
            "have a subject, and the entry files it as an instance of that "
            "later mechanism with the practice dated to the year the "
            "signature was drawn. The tie is one-sided in the way that "
            "matters: the reader attached to a woman who did not exist, and "
            "the reply, however real the labour behind it, came from the "
            "persona rather than the person. The counter - that a home "
            "economist really did answer, so the bond was two-way - loses "
            "because the far end of the reader's attachment was Betty, and "
            "Betty could not answer as herself; the correspondence ran under "
            "a single invented name for exactly that purpose. Contestable, "
            "and recorded as such.",
        ],
        ["literature", "radio"],
        [
            {"to": "the-brand-as-character", "type": "instance_of"},
            {"to": "nancy-drew", "type": "preceded"},
            {"to": "the-figure-you-buy", "type": "preceded"},
        ],
        [
            src("General Mills, \"How Betty Crocker got its start\" (2024)",
                "https://www.generalmills.com/news-and-stories/stories/"
                "how-betty-crocker-got-its-start",
                "The origin as the company's account gives it: the late-"
                "October 1921 Saturday Evening Post Gold Medal Flour "
                "jigsaw-puzzle advertisement; 30,000 completed puzzles "
                "arriving with several hundred letters of cooking questions; "
                "the Advertising Department persuading the board to create a "
                "personality the women answering the letters could all use; "
                "the surname Crocker chosen for the retired executive William "
                "G. Crocker and Betty for its friendly sound; Florence "
                "Lindberg's signature chosen in an internal contest and still "
                "in use; and the home economists who tested and demonstrated "
                "the flour."),
            src("General Mills, \"The women who built Betty Crocker\" (2022)",
                "https://www.generalmills.com/news-and-stories/stories/"
                "the-women-who-built-betty-crocker",
                "The people behind the persona: Ruth Hayes Carpenter hired in "
                "1921 to create the Home Service Department and a team of 25 "
                "home economists; Blanche Ingersoll developing the first "
                "radio scripts and becoming, in early October 1924, the first "
                "voice of Betty Crocker; the doubt that women would listen to "
                "a radio program and the letters that quickly came in "
                "instead; and the description of the voice as \"like the "
                "woman next door dropping in for a morning visit to share a "
                "new recipe.\""),
            src("MNopedia (Minnesota Historical Society), \"Betty Crocker\"",
                "https://www.mnhs.org/mnopedia/search/index/person/"
                "betty-crocker",
                "That Betty Crocker began in the advertising department of "
                "Washburn-Crosby after the October 1921 contest; that Samuel "
                "Gale invented the persona because the advice should come "
                "from a woman; that the all-female home service department "
                "answered consumer questions signing each letter \"Cordially "
                "Yours, Betty Crocker\"; and that Marjorie Child Husted drove "
                "the persona and wrote its radio scripts."),
            src("Wikipedia, \"Betty Crocker\"",
                "https://en.wikipedia.org/wiki/Betty_Crocker",
                "That Betty Crocker is a brand and fictional character "
                "created by the Washburn-Crosby Company in 1921 \"to give a "
                "personalized response to consumer product questions\"; the "
                "Gold Medal Flour promotion in the Saturday Evening Post and "
                "the 30,000 puzzles and letters that produced the persona; "
                "and that the persona was made because housewives would want "
                "advice from a fellow woman."),
            src("JSTOR Daily, \"In Search of the Real Betty Crocker\" "
                "(29 June 2017)",
                "https://daily.jstor.org/in-search-of-the-real-betty-crocker/",
                "That Betty Crocker began as a signature in an all-male "
                "advertising department needing a trustworthy spokeswoman; "
                "that the autograph was a composite of handwriting samples "
                "from the women at Washburn-Crosby; the 1924 radio debut of "
                "the \"Betty Crocker Cooking School of the Air\"; and Laura "
                "Shapiro's reading of Marjorie Child Husted's Betty as \"the "
                "home-economist-in-chief.\""),
        ],
    ),
]


def main():
    raw = P.read_bytes()
    text = raw.decode("utf-8")

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

    full = {e["id"]: e for e in ent["entries"]}
    for e in ENTRIES:
        for r in e["relations"]:
            tgt = full[r["to"]]
            if r["to"] == e["id"]:
                sys.exit(f"refusing: {e['id']} relates to itself")
            if r["type"] in STRUCTURAL:
                print(f"  {r['type']:12s} {e['id']} -> {r['to']}  (structural)")
                continue
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
