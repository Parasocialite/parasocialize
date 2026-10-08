# -*- coding: utf-8 -*-
"""Add three encyclopedia entries: clara-bow, greta-garbo, edgic.

The thinnest places measured after the second media batch, three of them:

  clara-bow          film        1927   the reply counted: 45,000 fan letters in
                                        one month, and the audience dyeing its
                                        hair to match a surface a studio held
  greta-garbo        film        1932   the manufacture of distance, and the
                                        1955 correction the world declined to
                                        take - "let alone", not "alone"
  edgic              television_unscripted 2002  the audience writing an
                                        instrument to read the production by,
                                        kept as a self-governing body

1931 and 1932 held no entry before this file ran, and 2002 held none either.
The three relation targets were chosen from entries whose years are already
fixed in the corpus, and every chronological edge is asserted against those
years before anything is written - the failure mode this repo has hit seven
times is typing the verb from the way the sentence reads.

Every record below is `unverified`, not `retrievable`: the text was read
through a search index rather than fetched, the status reason is stated in
the claim of every record, and no locator carries a DOI, so no identity was
checked. That is the rule since the Met Museum pages returned 429.

Usage:  python tools/add_third_batch_entries.py            (dry run)
        python tools/add_third_batch_entries.py --apply
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

TARGET_IDS = ["clara-bow", "greta-garbo", "edgic"]

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
        "clara-bow",
        "The girl the studio built",
        "person", 1927, "Silent era",
        ["application", "manipulation"], ["idol"],
        "Paramount signed Clara Bow in 1926 and released six of her pictures "
        "in 1927, one of which - It - put a novelist's definition of 'It' "
        "onto a face and left the language with the phrase 'It Girl'. At the "
        "top of her fame she was the most-answered person in America: more "
        "than 45,000 fan letters arrived in January 1929 alone, and when "
        "fans found out she used henna, sales of the dye tripled.",
        [
            "**A novelist defined the quality, and the studio cast a woman "
            "to hold it.** Elinor Glyn wrote both the story and the "
            "screenplay of It (1927) and gave the age its definition of the "
            "thing - 'To have It, the fortunate possessor must have that "
            "strange magnetism which attracts both sexes' - and the picture "
            "gave Bow the phrase she has been known by ever since, the It "
            "Girl. Paramount had signed her to a five-year deal on 16 August "
            "1926, at $1,700 a week rising to $4,000 by the last year, and "
            "in 1927 alone it released six pictures with her in them, among "
            "them It and Wings. One account of her years at Paramount "
            "records her salary as the lowest of any major star, with her "
            "bonuses put in trust against the morals clause of that "
            "contract.",

            "**The reply came in at a scale the studio could count, and the "
            "audience copied her as well as writing to her.** In January "
            "1929 - the month she began filming her first talkie - she "
            "received more than 45,000 fan letters and stood as the number "
            "one star in America, with Colleen Moore a distant second. When "
            "fans found out she put henna in her red hair, sales of the dye "
            "tripled: the audience did not only write, it reproduced the "
            "surface. Her own rise had run through a public contest - at "
            "sixteen she won Motion Picture magazine's Fame and Fortune "
            "Contest from a line of auditioning rivals - so the "
            "correspondence was part of the industry's apparatus from the "
            "start. She was named the first box-office draw in 1928 and "
            "1929, and the second in 1927 and 1930.",

            "**The counter-argument is that she was simply the most alive "
            "person on the screen, and the record backs it.** Dorothy "
            "Arzner, who directed her in 1927, called her 'automatically a "
            "natural' and 'full of animation and projection of her thoughts "
            "and emotions', and no contract manufactures that. The claim "
            "here is narrower: what the letters were addressed to was "
            "assembled out of a novelist's definition, a five-year contract, "
            "a hair colour and a studio that kept the count - and the "
            "audience's half of it was unpaid work, writing and dyeing and "
            "copying, done at a distance the studio controlled. Whatever "
            "she was like in the room, the thing that drew more than "
            "forty-five thousand letters in one month was a surface, and "
            "surfaces are what this shelf exists to file.",
        ],
        ["film"],
        [
            {"to": "babe-ruth", "type": "contemporary"},
            {"to": "the-fan-magazine", "type": "succeeded"},
            {"to": "fan-mail", "type": "succeeded"},
        ],
        [
            src("Wikipedia, \"Clara Bow\"",
                "https://en.wikipedia.org/wiki/Clara_Bow",
                "The facts the entry rests on: the five-year Paramount "
                "deal signed 16 August 1926 at $1,700 a week rising to "
                "$4,000 by the last year; the six Paramount releases of "
                "1927 (It, Children of Divorce, Rough House Rosie, Wings, "
                "Hula, Get Your Man); It giving her the nickname the It "
                "Girl with Elinor Glyn writing the book and the "
                "screenplay; more than 45,000 fan letters in a single "
                "month, January 1929; the first box-office draw of 1928 "
                "and 1929 and the second of 1927 and 1930; and henna "
                "sales tripling when fans learned she used it."),
            src("PBS NewsHour, \"Who is Clara Bow from Taylor Swift's "
                "new album?\" (2024)",
                "https://www.pbs.org/newshour/arts/who-is-clara-bow-"
                "from-taylor-swifts-new-album",
                "The scale of the reply as PBS records it: by 1929 she "
                "was receiving 45,000 fan letters a month, and that same "
                "year sales of the reddish dye henna tripled as fans "
                "tried to mimic her look; plus the 1927 star turn in It."),
            src("Vogue, \"Happy Birthday, Clara Bow! Here, a Look back "
                "at the Original It Girl\" (L. Yaeger, 2017)",
                "https://www.vogue.com/article/clara-bow-birthday-curls",
                "The origin of the phrase and its definition: Bow as the "
                "world's first It girl after the 1927 film It, Elinor "
                "Glyn's written definition of It as a strange magnetism "
                "which attracts both sexes, the box-office ranking of "
                "1928 and 1929 against 1927 and 1930, and 45,000 fan "
                "letters in a single month at the height of her fame."),
            src("Moviediva, \"The Wild Party\" (2022)",
                "https://moviediva.com/reviewpages/mdwildparty/",
                "The studio side of the record: January 1929 as the "
                "month she began filming her first talkie, her standing "
                "as the number one star in America with 45,000 fan "
                "letters and Colleen Moore a distant second, the studio "
                "exploiting her fame, her salary as the lowest of any "
                "major star with bonuses held in trust against the "
                "morals clause, her win at sixteen in Motion Picture "
                "magazine's Fame and Fortune Contest, and Dorothy "
                "Arzner's on-set assessment of her as a natural full of "
                "animation and projection of her thoughts and emotions."),
            src("American Heritage, \"The It Girl\" (1995, Vol. 46 "
                "Issue 4)",
                "https://www.americanheritage.com/it-girl",
                "Independent corroboration of the month: 45,000 fan "
                "letters in January of 1929, with Glyn's It Girl "
                "declaration and Bow's standing alongside Garbo, Gish, "
                "Pickford and Swanson."),
        ],
    ),

    make(
        "greta-garbo",
        "Let alone, not alone",
        "person", 1932, "Cinema",
        ["manipulation", "consideration"], ["idol"],
        "In Grand Hotel (1932) Greta Garbo said 'I want to be alone', and "
        "the line became her biography: the press called her the Swedish "
        "Sphinx and MGM capitalised on the mystery. In LIFE in January "
        "1955 she corrected the record - she had wanted to be let alone, "
        "not alone, and there is all the difference - but the correction "
        "did not take, and the letters she wrote at the time read lonelier "
        "than the legend does.",
        [
            "**The line belonged to a ballerina, and then it belonged to "
            "her.** As Grusinskaya in Grand Hotel (1932) Garbo says 'I "
            "want to be alone' - once, then 'I just want to be alone', "
            "then again in conversation with the Baron - and the picture "
            "won that year's Academy Award for Best Picture. In 2005 the "
            "American Film Institute put the line thirtieth among a "
            "century's most memorable movie quotes. The press meanwhile "
            "called her the Swedish Sphinx, and the arrangement is plain "
            "in the record: she spurned Hollywood's publicity rules, MGM "
            "eventually capitalised on that, because it bolstered the "
            "image of the silent and reclusive woman of mystery, and her "
            "MGM contract expired after As You Desire Me later in 1932. "
            "So the surface had two maintainers - the woman who refused "
            "and the studio that found the refusal useful.",

            "**In January 1955 she corrected the sentence she is famous "
            "for saying.** LIFE's piece of that month has her: 'I never "
            "said, I want to be alone, she told a friend recently. I only "
            "said, I want to be let alone! There is all the difference.' "
            "The same article states how the myth was assembled: "
            "repeatedly, it reads, the myth of Garbo's aloneness was "
            "built up by her dogged defences of her personal privacy - "
            "her furtive comings and goings, her headlong flights from "
            "fans and reporters, her refusal to allow strangers or even "
            "strange technicians onto the sets of her movies. The "
            "audience's picture was therefore assembled out of refusals "
            "it could watch her make, while the private record runs the "
            "other way: writing to a friend in 1937 she said 'I go "
            "nowhere, see no one', and 'It is hard and sad to be alone, "
            "but sometimes it's even more difficult to be with someone.'",

            "**The counter-argument is that there was no myth at all, "
            "only a private woman who disliked the noise, and it is half "
            "right.** LIFE records periods of determined solitude and "
            "notes that she was seldom literally alone - she had friends, "
            "and the piece spends its length on dinners, a prince and a "
            "game of tennis. What this entry attaches to is narrower and "
            "sits on the audience's side: the finished surface of "
            "refusal, which she was not present to contradict and which "
            "went on working after she stopped making pictures - thirteen "
            "years of it by LIFE's count. Distance is this shelf's "
            "property, and it explains why the correction failed: a "
            "correction is itself a reply, and the legend did not need "
            "one. The accounts read for this entry in 2017 and 2019 both "
            "still open with the line she denied.",
        ],
        ["film"],
        [
            {"to": "clara-bow", "type": "succeeded"},
        ],
        [
            src("LIFE, January 1955 (press article, reprinted at "
                "GarboForever)",
                "http://www.garboforever.com/1955_Life-3.htm",
                "The correction and the mechanism, in the magazine's own "
                "words: 'I never said, I want to be alone ... I only said, "
                "I want to be let alone! There is all the difference'; "
                "the myth of Garbo's aloneness built up by her dogged "
                "defences of her personal privacy, her flights from fans "
                "and reporters and her refusal to allow strangers or "
                "technicians onto her sets; her periods of determined "
                "solitude and the fact that she was seldom literally "
                "alone; and the mystery of her thirteen-year absence from "
                "the screen."),
            src("Smithsonian, \"The Profound Loneliness of Greta Garbo\" "
                "(B. Katz, 2017)",
                "https://www.smithsonianmag.com/smart-news/profound-"
                "loneliness-greta-garbo-180967417/",
                "The legend as it was still being told in 2017 and the "
                "correction underneath it: 'I want to be alone' as the "
                "most famous quip attributed to her, her practice of "
                "shunning reporters, premieres and fan mail, and her "
                "claim that she was misquoted according to the 1955 LIFE "
                "piece."),
            src("The Guardian, \"'I go nowhere, I see no one': Garbo "
                "letters reveal lonely life of film icon\" (V. Thorpe, "
                "2019)",
                "https://www.theguardian.com/film/2019/oct/05/garbo-"
                "letters-for-sale-echo-lonely-life-of-film-icon",
                "The private record against the legend: the famous "
                "phrase as the line her character speaks in her 1932 hit "
                "Grand Hotel and how it fitted her image as a star who "
                "shunned Hollywood; her 1937 letter 'I go nowhere, see no "
                "one'; and 'It is hard and sad to be alone, but "
                "sometimes it's even more difficult to be with "
                "someone'."),
            src("Wikipedia, \"Greta Garbo\"",
                "https://en.wikipedia.org/wiki/Greta_Garbo",
                "The manufacture and its owners: MGM eventually "
                "capitalising on her aversion to publicity because it "
                "bolstered the image of the silent and reclusive woman of "
                "mystery, the press routinely calling her the Swedish "
                "Sphinx, Grand Hotel winning that year's Best Picture, "
                "her contract expiring after As You Desire Me (1932) and "
                "her return to Sweden, and the later LIFE explanation "
                "that she had said let alone rather than alone."),
            src("Wikipedia, \"Grand Hotel (1932 film)\"",
                "https://en.wikipedia.org/wiki/Grand_Hotel_(1932_film)",
                "The line itself in its setting: Garbo as Grusinskaya "
                "delivering 'I want to be alone' and repeating 'I just "
                "want to be alone', the AFI ranking of the line thirtieth "
                "among movie quotes, and her later insistence that she "
                "only said she wanted to be let alone."),
        ],
    ),

    make(
        "edgic",
        "The forum that scored the edit",
        "mechanism", 2002, "Reality television",
        ["consideration", "manipulation"], ["contest"],
        "Edgic - editing plus logic - is the practice of grading every "
        "contestant's screen presence week by week: a category (invisible, "
        "under the radar, middle of the road, complex personality, over "
        "the top), a tone and a visibility score, charted in public so a "
        "community can read what the production is doing and name the "
        "winner before the merge. It began on the Survivor Sucks forum "
        "during Survivor's fourth season in 2002.",
        [
            "**The instrument was written by forum users, in season four, "
            "and it has never been official.** Inside Survivor's glossary "
            "records the portmanteau - edit plus logic - as coined by "
            "members of the Survivor Sucks forum, and its introduction "
            "page describes the practice: a fan decided to apply media "
            "theory and statistical analysis to his favourite show to "
            "work out who the winner was from the editing, assigning each "
            "player a rating every episode from their portrayal, their "
            "share of screen time and other factors. The Ringer's history "
            "fixes the origin: Survivor Sucks, during season four, in "
            "2002, credited to a user called KernelQ, remembered by one "
            "of the community's organisers as part man and part myth, and "
            "by season nine many of its permanent principles and methods "
            "were in place. The board's own archive shows the machinery "
            "running: a 2005 thread lays out the guidelines - invisible, "
            "under the radar, middle of the road, complex personality, "
            "over the top, each with a tone and a visibility from one to "
            "five - a rating schedule with dates, and a roster of raters "
            "that includes KernelQ himself.",

            "**What makes it this site's subject is that the grade is "
            "written for somebody who will never read it, and the group "
            "that keeps it has a constitution.** Each week the community "
            "scores a real person's edited presence - not the programme "
            "but an individual's portrayal - and the work is collective "
            "and kept: the successor forum Unspoiled Edgicers Unite holds "
            "transcripts of confessionals, visibility charts for every "
            "episode and a complete set of colour-coded edgic charts for "
            "every season, early ones rewatched and rated after the fact, "
            "and it has grown past two thousand members. The board split "
            "over a rule rather than over a contestant: spoilers were "
            "leaking into the ratings, the original board's answer was "
            "that there is no such thing as unspoiled edgic, and a "
            "spoiler-free forum was founded in response - a membership "
            "boundary, enforced. The archive also settles arguments "
            "opinions cannot: its organisers report that the community's "
            "own records show female winners edited differently and "
            "talking about half as much as male winners.",

            "**The counter-argument is that this is analysis rather than "
            "attachment, and edgic's critics put it almost that way.** "
            "The Purple Rock podcast's complaint is that there is no "
            "official edgic at all - the consensus version is whatever "
            "Survivor Sucks runs it as - and that the charts are "
            "contaminated by spoilers, since the board that supplies them "
            "is the board that leaks them. That is the honest challenge, "
            "and it is why this entry is filed as an institution rather "
            "than as a tie: what attaches is the group's rule, not the "
            "contestant, and a grade written weekly for a person who will "
            "never see it can be described as data rather than as "
            "attention. The narrower claim stands anyway: a vocabulary "
            "the audience wrote for itself, a schedule its volunteers "
            "keep, and a boundary it expels people for crossing are the "
            "workings of a body rather than of a viewership - and the "
            "forum, not the show, is what holds it together.",
        ],
        ["television_unscripted"],
        [
            {"to": "forum-culture", "type": "succeeded"},
            {"to": "the-confessional-booth", "type": "succeeded"},
            {"to": "the-algorithm-decides", "type": "preceded"},
        ],
        [
            src("The Ringer, \"Edgic of Extinction: How Hardcore Edit "
                "Analysts Unravel the Mysteries of Reality TV\" (B. "
                "Lindbergh, 2020)",
                "https://www.theringer.com/2020/05/13/tv/survivor-edgic-"
                "analysis-winners-edit",
                "The origin and history as the article records it: "
                "edgic originating on the Survivor Sucks forum during "
                "Season 4 in 2002, created by the user KernelQ, its "
                "foundational community and record-keeping at Unspoiled "
                "Edgicers Unite with more than 2,000 members, the "
                "principles and methods in place by season nine, the goal "
                "of picking the winner before the merge, the spoiler "
                "crisis that drove the splinter site, and the archive "
                "showing female winners edited differently and talking "
                "about half as much as male winners."),
            src("Inside Survivor, \"Survivor Edgic - An Introduction\" "
                "(M. Holmes, 2015)",
                "https://insidesurvivor.com/survivor-edgic-an-"
                "introduction-3094",
                "The definition and the portmanteau: edgic combining "
                "editing and logic, a concept devised by members of the "
                "Survivor Sucks forums to determine each season's winner "
                "from the edit, assigning a rating to each player per "
                "episode based on portrayal, percentage of screen time and "
                "other factors, and also useful for mapping a character's "
                "story arc."),
            src("Survivor Sucks forum thread, \"S2 Edgic (Editing and "
                "Logic)\" (2005)",
                "https://www.tapatalk.com/groups/survivorsucks/s2-edgic-"
                "editing-and-logic-t10185.html",
                "The practice as the community ran it: written guidelines "
                "defining the ratings INV, UTR, MOR, CP and OTT with "
                "their tone categories and visibility measures from low "
                "to high, a dated season-long schedule for raters to post "
                "their scores, and a roster of participants that includes "
                "KernelQ."),
            src("The Purple Rock Survivor Podcast, \"The Problem with "
                "Edgic\" (2016)",
                "https://www.purplerockpodcast.com/the-problem-with-"
                "edgic/",
                "The critics' case and the governance: no official edgic "
                "with the consensus version existing on the Survivor "
                "Sucks forum, spoilers being baked into that version, a "
                "group of devotees breaking off before season 24 to form "
                "a spoiler-free site, and the original board's response "
                "that there is no such thing as unspoiled edgic."),
            src("Surviving Tribal, \"Survivor glossary: Does edgic truly "
                "predict winners?\" (2017)",
                "https://survivingtribal.com/2017/09/28/survivor-"
                "glossary-edgic-truly-predict-winners/",
                "The practice and its stated purpose as a fan glossary "
                "records it: edgic describing the logic behind what the "
                "editing team shows over an episode to predict the "
                "narrative and character arcs, the goal of a definitive "
                "winner pick after the merge episode, and the term's "
                "creation credited to Survivor Sucks."),
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
