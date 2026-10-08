# -*- coding: utf-8 -*-
"""Add six encyclopedia entries answering the thinnest media after the first
media batch.

Item 32's measured cadence still stands after `add_media_entries.py`: comics,
radio, stage and visual_art exhaust a bi-daily creator inside a week. The first
batch gave each of the four a name. These six push the thin end further into
the historical record:

  the-icon               visual_art+theology  787     the Second Council of
                                                     Nicaea ends the first
                                                     iconoclasm and defines
                                                     what an icon is for -
                                                     honour passing to a
                                                     figure who is not there
  sarah-bernhardt         stage+film         1891     the theatre's first
                                                     systematic idol: a woman
                                                     toured like a head of
                                                     state at distances only
                                                     print could bridge
  aimee-semple-mcpherson  radio+theology      1924     her church on the air,
                                                     and the letters coming
                                                     back from other states
                                                     and other countries
  peanuts                 comics             1950     the strip built from
                                                     affection that cannot be
                                                     returned, in the year the
                                                     fan club got its entry
  babe-ruth               sport              1927     the printed athlete: a
                                                     syndicated byline mostly
                                                     ghostwritten, heard on
                                                     the new radio
  the-confessional-booth  television_unscripted 1992  the Real World device
                                                     that became global
                                                     reality TV's least
                                                     questioned convention

Every record below is `unverified`, not `retrievable`. The text was read through
a search index, not fetched, and `retrievable` means a reader can open it and
that was checked. The status reason is stated in the claim of every record,
which is the rule this corpus has used since the Met Museum pages returned 429.

Relations follow the direction `citation_audit.py` enforces: `preceded` means
this entry's year is the smaller, `succeeded` means the target's is, and a tie
is `contemporary`. The inline assertion in `add_nancy_drew.py` states that rule
backwards and never fired; do not copy it. Every chronological edge below is
asserted against the years before save.

Usage:  python tools/add_second_media_batch_entries.py            (dry run)
        python tools/add_second_media_batch_entries.py --apply
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

TARGET_IDS = ["the-icon", "sarah-bernhardt", "aimee-semple-mcpherson",
              "peanuts", "babe-ruth", "the-confessional-booth"]

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
          "succeeded": lambda own, tgt: tgt < own}


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
        "the-icon",
        "The icon answers nothing",
        "work", 787, "Medieval",
        ["application"], ["idol"],
        "In 787 the Second Council of Nicaea ended the first phase of the "
        "Byzantine iconoclastic dispute and defined what an icon was for: the "
        "honour paid to the image passes to the figure it shows. Icons were "
        "lawful because in Christ the invisible God had been seen. The panel "
        "itself never answered anyone.",
        [
            "**The council drew a line only the second phase of iconoclasm "
            "would redraw.** The Byzantine dispute over images ran from the "
            "reign of the emperor Leo III in the 730s; the Second Council of "
            "Nicaea, summoned in 787, closed the first phase by declaring the "
            "veneration of icons lawful and orthodox. Its formula rests on a "
            "distinction the church still repeats: relative veneration "
            "(proskynesis - the honour, the greeting) was owed to the image, "
            "while true worship (latreia) belonged to God alone. The classical "
            "backing was Basil of Caesarea's sentence that the honour paid to "
            "the image passes to the prototype - the figure the image shows.",

            "**What the icon is for makes this site's subject in paint.** The "
            "devotee stands before a panel understood, in the argument of John "
            "of Damascus and later the Studite writers, to participate in the "
            "figure it shows, so that a prayer said 'through' the image is "
            "addressed to somebody who is not in the room. The venerated "
            "panel cannot answer, and nobody expects it to; the whole doctrine "
            "runs on the reply being withheld here and heard elsewhere. The "
            "icon is a face in a church that speaks to nobody back - the "
            "painted absence this corpus already records in the empty-wall "
            "entry, arriving as an official theology rather than a habit.",

            "**The counter-argument is the one the council had to defeat, and "
            "it is kept on the entry rather than resolved.** The iconoclasts "
            "charged the practice as idolatry; the council's answer was that "
            "honour directed through an image is not the worship of wood and "
            "pigment, and the plain reading of the ban on graven images was "
            "set against the Incarnation - the unseeable God had been seen in "
            "Christ. The settlement did not hold: the icons were banned again "
            "in 815 and restored for good only in 843. One political parallel "
            "the same argument used is worth keeping - the imperial portrait "
            "honoured an absent emperor exactly as an icon honours an absent "
            "Christ, which is the civic version of the same structure."
        ],
        ["visual_art", "theology"],
        [
            {"to": "margery-kempe", "type": "preceded"},
            {"to": "lewis-chessmen", "type": "preceded"},
        ],
        [
            src("Brunel University research archive (thesis full text)",
                "https://bura.brunel.ac.uk/bitstream/2438/5323/1/"
                "FulltextThesis.pdf",
                "The iconoclasm dispute and its doctrinal mechanism as the "
                "thesis treats it: the Second Council of Nicaea in 787 ending "
                "the first phase, the proskynesis/latreia distinction, Basil's "
                "honour-passes-to-the-prototype formula, John of Damascus and "
                "the hypostasis argument of the Studites, the imperial-portrait "
                "parallel, and the second phase running to the final "
                "restoration of the icons in 843."),
            src("Wikipedia, \"Byzantine Iconoclasm\"",
                "https://en.wikipedia.org/wiki/Byzantine_Iconoclasm",
                "The two periods of the dispute and their dates: the council "
                "at Nicaea in 787 ending the first Iconoclastic period, and "
                "the final restoration of the icons at the orthodox synod of "
                "843."),
        ],
    ),

    make(
        "sarah-bernhardt",
        "The Divine Sarah",
        "person", 1891, "Theatre",
        ["consideration"], ["idol"],
        "Sarah Bernhardt toured more like a head of state than a player: when "
        "she sailed for New York in 1891 the crossing was covered the way a "
        "royal visit is, and 'Divine Sarah' was by then the whole public's "
        "phrase for her. Mark Twain's note put it exactly - there were five "
        "kinds of actresses, and Sarah Bernhardt. An idol built at distance.",
        [
            "**The most famous face the pre-cinema stage could make.** Born "
            "in Paris in 1844, Bernhardt was by the 1870s the figure the "
            "international press called Divine Sarah - Oscar Wilde's 1879 "
            "poem of that name had her crowned with lilies at the feet of "
            "audiences who would never see her act in a room, and a French "
            "paper called her a national institution. Her motto was 'Quand "
            "Même' - 'in spite of everything' - which the torments of a "
            "career turned into a legend of refusal.",

            "**The 1891 tour was the idol arriving.** In 1891 she left Le "
            "Havre on 15 October aboard the L'Amérique on her way to "
            "America, and the arrival was covered in the register of a state "
            "visit: one account of these tours records the homage shown her "
            "as the kind 'usually reserved for royalty', applause and press "
            "for a woman most of the auditorium had only met through prints, "
            "reviews and playbills. Distance is the mechanism - the audience "
            "knew the surface better than the woman, and a finished public "
            "surface is exactly what a parasocial idol is made of.",

            "**She stood at the seam between the printed and the cinematic "
            "star.** Mark Twain's tribute, written for a tour programme, "
            "ranked her apart from every other class of actress, and the "
            "cinema that arrived within a generation inherited the structure: "
            "the same manufactured distance, the same schedule of "
            "manufactured encounters, the same audience that never arrived in "
            "time for the making. The counter-argument - that she was "
            "simply the greatest actress of her age and the devotion was "
            "earned on stage - is kept on the entry. The claim here is "
            "narrower: her fame was distributed by the print machinery this "
            "corpus files everywhere else under the idol, which makes her the "
            "theatre's first systematic case of it."
        ],
        ["stage", "film"],
        [
            {"to": "charlie-chaplin", "type": "preceded"},
            {"to": "mary-pickford", "type": "preceded"},
        ],
        [
            src("American Heritage, \"Bernhardt in America\"",
                "https://www.americanheritage.com/bernhardt-america",
                "The American tours and their register as the article "
                "records it: the 1891 departure from Le Havre aboard the "
                "L'Amérique, homage usually reserved for royalty, and Mark "
                "Twain's programme tribute ranking her apart from every class "
                "of actress."),
        ],
    ),

    make(
        "aimee-semple-mcpherson",
        "The radio church of Sister Aimee",
        "person", 1924, "Radio",
        ["consideration"], ["idol"],
        "Her church went on the air on 6 February 1924: KFSG - 'Kall "
        "Foursquare Gospel' - broadcasting at 500 watts from Angelus Temple, "
        "listener-supported one day at a time. She is credited by her own "
        "church as the first woman to preach a sermon on radio (1922), and "
        "after the first broadcast the letters came from other states and "
        "other countries, cataloguing where the signal had been heard.",
        [
            "**A church built to be heard at a distance.** Aimee Semple "
            "McPherson had preached on Los Angeles radio before owning a "
            "station, and her church's history credits her as the first woman "
            "to preach a sermon over the radio, on the Rockridge station in "
            "Oakland in April 1922. In February 1924 KFSG went on the air "
            "from Angelus Temple - a 500-watt Western Electric transmitter "
            "whose dedication named its reach, 'the people of the United "
            "States, Canada, Alaska, Mexico, Panama, Hawaii, South Sea "
            "Islands'. The congregation had raised the roughly $25,000 to "
            "build it.",

            "**The letters were the reply channel, and they were the "
            "audience.** In the early 1920s a station learned who was "
            "listening from the mail: cards, telegrams and letters reporting "
            "where the signal was received. The record kept for KFSG includes "
            "letters from Illinois, Indiana, Pennsylvania and New Zealand "
            "describing when the broadcast was heard and what it meant - "
            "'We do hope to hear you soon again', one wrote, and a listener "
            "in Indiana asked who the woman preacher had been. The station "
            "answered its mail through volunteer church members, and it was "
            "sponsored day by day by listeners through the Radio Missionary "
            "Society, with patrons booked months ahead.",

            "**The mechanism is a congregational 'you' at a distance.** The "
            "church addressed the radio congregation as assembled even "
            "though the far end could not answer: in Angelus Temple the "
            "pastor asked 'Do you pledge to live clean Christian lives for "
            "God?' and the answer - 'We do' - came back from a room the radio "
            "listeners could not join. That is the presenter mechanism with a "
            "congregation in it: second-person grammar aimed at an unseen "
            "audience, engineered on a schedule. The competing placement, the "
            "idol, fails because the sermons were live and ongoing - an "
            "address from somebody who believed herself perceived, not a "
            "finished body of work. One honesty note is kept: the famous "
            "'minions of Satan' telegram to Secretary Hoover over a "
            "wavelength dispute is recorded by radio historians as legend "
            "rather than fact, and KFSG was never actually taken off the air."
        ],
        ["radio", "theology"],
        [
            {"to": "fireside-chats", "type": "preceded"},
            {"to": "queen-for-a-day", "type": "preceded"},
        ],
        [
            src("Radio Heritage Foundation, \"KFSG Los Angeles - The Aimee "
                "Semple McPherson Station\" (J. Hilliker)",
                "https://www.radioheritage.com/story51/",
                "The station as its history records it: the February 1924 "
                "dedication, the 500-watt Western Electric transmitter, the "
                "church's claim that she was the first woman to preach a "
                "sermon over the radio (the Rockridge station, KZY, in "
                "Oakland, April 1922), the reception letters from other "
                "states and from New Zealand, the Radio Missionary Society's "
                "day-by-day sponsorship, and the volunteer staff that "
                "answered the mail."),
            src("International Church of the Foursquare Gospel resources, "
                "\"Sister Aimee's astounding radio impact\" (adapted from R. "
                "L. Power, Radio in the Home, January 1925)",
                "https://resources.foursquare.org/sister_aimees_astounding_"
                "radio_impact/",
                "The broadcast mechanism from inside the church: the "
                "congregation's 'Do you pledge... We do' exchange, the "
                "hundreds of thousands the broadcast reached in homes, the "
                "voluntary financing of the station's upkeep, and the "
                "shut-in and sunshine-hour programming."),
            src("Wikipedia, \"KFSG (Los Angeles)\"",
                "https://en.wikipedia.org/wiki/KFSG_(Los_Angeles)",
                "The licence facts: KFSG first licensed in January 1924 to "
                "the Echo Park Evangelistic Association at 500 watts, the "
                "call letters standing for 'Kall Foursquare Gospel', and the "
                "non-commercial religious programming."),
            src("The Radio Historian, \"The alleged Hoover telegram\" "
                "(J. Schneider)",
                "https://theradiohistorian.org/lax/hoover-telegram.html",
                "The caution on the 'minions of Satan' telegram to Secretary "
                "of Commerce Hoover: no period record of it exists, the "
                "Department of Commerce files show no action against KFSG, "
                "and the incident is recorded here as legend rather than "
                "fact."),
        ],
    ),

    make(
        "peanuts",
        "The strip about unrequited love",
        "work", 1950, "Fandom",
        ["consideration"], ["character"],
        "Peanuts began on 2 October 1950 with a strip whose first line - "
        "'Good ol' CharlieBrown... How I hate him!' - announced the subject: "
        "affection that cannot be returned. A round-headed boy who loses "
        "everything, a dog who does not answer, a cartoon world that kept 350 "
        "million readers. Schulz maintained the loser's world on purpose.",
        [
            "**The first strip made the subject legal tender.** Peanuts "
            "debuted on 2 October 1950, syndicated by United Feature, and the "
            "opening panel was a small boy walking past Charlie Brown with "
            "the line 'Good ol' CharlieBrown... How I hate him!' - unrequited "
            "feeling in the form of a neighbour who cannot be placated, which "
            "is where the strip stayed for fifty years.",

            "**The world is an economy of unanswered want.** Charlie Brown's "
            "love for the Little Red-Haired Girl is offered to a girl who is "
            "never on panel; Snoopy's silence keeps the one close bond in the "
            "strip without a reply; and the habit of the boy losing - the "
            "game, the spelling bee, the object of affection - is presented "
            "as the ordinary condition rather than the exception. The "
            "reader's caring-for-a-boy-who-loses is the tie the strip runs "
            "on: the audience's side of an attachment the strip itself never "
            "completes. Nothing in the fiction ever answered any of it.",

            "**The maker defended the loss as a structure.** Schulz returned "
            "repeatedly to why Charlie Brown has to keep losing, describing "
            "the round-headed boy as the strip's conscience - the one who "
            "carries hope in a world designed to disappoint him. The "
            "counter-argument, that affection for Peanuts is really affection "
            "for a remembered world rather than for a character, is kept on "
            "the entry; the placement lands on the character because the "
            "whole strip is written from one figure who cannot be answered."
        ],
        ["comics"],
        [
            {"to": "fan-club", "type": "contemporary"},
        ],
        [
            src("TIME, anniversary essay on Peanuts and the villain of "
                "unrequited love (L. Rothman, 2014)",
                "https://time.com/3445127/peanuts/",
                "The 2 October 1950 first strip and its opening line about "
                "Charlie Brown, the strip's themes of unrequited love and "
                "the character of the loser, and the scale of the strip's "
                "peak readership."),
            src("Encyclopaedia Britannica, \"Peanuts\"",
                "https://www.britannica.com/topic/Peanuts",
                "The strip's 1950 debut, Schulz's authorship, the "
                "unrequited-love and loser themes, the roughly 18,000 strips "
                "of its run, and the readership measured across its country "
                "and audience counts."),
        ],
    ),

    make(
        "babe-ruth",
        "The baseball the papers built",
        "person", 1927, "Radio",
        ["consideration"], ["idol"],
        "In 1927 Babe Ruth hit sixty home runs and became the most replayed "
        "figure in a game most fans knew through print. His bylined column "
        "ran in syndication, much of it ghostwritten, and radio was beginning "
        "to carry him into rooms the stadium never reached. The 1920s press "
        "manufactured a 'hot romance' and he was its star.",
        [
            "**The season the man and the persona arrived together.** Ruth's "
            "1927 season - sixty home runs in a 154-game schedule, a "
            "single-season record that stood until Roger Maris hit sixty-one "
            "in 1961, with the Yankees' Murderers' Row around him - is the "
            "on-field anchor this entry leans on without being about. The "
            "subject is the parallel figure the press built, because most of "
            "the people who loved him never saw him play.",

            "**The printed voice was another man's.** Through the 1920s "
            "Ruth's byline ran across the country in syndicated columns and "
            "serials, and much of that copy was ghostwritten - the "
            "'Babe Ruth' column was substantially the work of Christy Walsh, "
            "his agent, who organised the ghosted pieces under Ruth's name. "
            "A reader opening the sports page met a voice signed 'Babe Ruth' "
            "that Babe Ruth had not written, which is the manufactured reply "
            "end of a one-sided tie arriving in sports journalism: the "
            "attention felt answered, and the answer was an agency.",

            "**Radio and the syndicated page made the tie work at "
            "distance.** Baseball went on the air in the 1920s, and Ruth's "
            "name travelled ahead of him by broadcast and by print - this "
            "entry records the 1920 film 'Headin' Home' as the star's "
            "celluloid echo of the same reach. The deeper claim, read from "
            "the thesis this entry draws on, is that the newspapers of the "
            "1920s manufactured what one account calls a 'hot romance between "
            "sport and the public'. The counter-argument - that Ruth's fame "
            "was earned by a bat, not by columns - is real and kept on the "
            "entry; the point is narrower, that the relationship hundreds of "
            "thousands had with him ran through contributed copy and "
            "broadcast names rather than through a seat in a ballpark."
        ],
        ["sport"],
        [
            {"to": "the-atletefan-bond", "type": "succeeded"},
            {"to": "kobe", "type": "preceded"},
        ],
        [
            src("J. C. Trimble, \"Babe Ruth: The Media Construction of a "
                "1920's Sport Personality\" (Colby College senior thesis",
                "https://digitalcommons.colby.edu/cgi/viewcontent.cgi?"
                "article=3102&context=cq",
                "The thesis treats the press and radio construction of Ruth "
                "across the 1920s: the ghostwriting of his bylined columns, "
                "syndication, the early radio broadcasts of baseball, and the "
                "claim that the newspapers of that decade manufactured a 'hot "
                "romance between sport and the public'."),
            src("Encyclopaedia Britannica, \"Babe Ruth\"",
                "https://www.britannica.com/topic/Babe-Ruth",
                "The baseball facts the entry rests on: the 1927 season's "
                "sixty home runs in a 154-game schedule, the single-season "
                "record until Maris's sixty-one in 1961, Murderers' Row, and "
                "the 1920 motion picture 'Headin' Home'."),
        ],
    ),

    make(
        "the-confessional-booth",
        "The confessional that became a convention",
        "mechanism", 1992, "Reality television",
        ["consideration"], ["contest"],
        "In 1992 MTV's The Real World gave reality television its "
        "least-questioned convention: a person alone in a room, speaking to "
        "a camera about what everyone just saw. The confessional was adopted "
        "by Survivor, Big Brother and the Housewives, and it endures because "
        "it is an interview dressed as a private thought, in a public space "
        "everyone pretends is private.",
        [
            "**A soap opera that could not afford writers invented a "
            "confidante instead.** The Real World began as MTV's attempt at "
            "a scripted show for a younger audience; without a writers' "
            "budget, the plan became gathering seven strangers in one house "
            "and editing the resulting footage. The series premiered on 21 "
            "May 1992, and from the start its stock included the "
            "confessional - alone time in which a cast member could 'speak "
            "directly to a camera about the happenings in the house'. One "
            "reference account calls the confessional 'a Real World invention "
            "that dozens of other reality shows, including Survivor, Boot "
            "Camp, Making of the Band, Big Brother and Road Rules, have "
            "adopted'.",

            "**The confession is a manufactured private address.** The "
            "producers interviewed cast members on a schedule - in the first "
            "season in hallways, stairways, on a roof and once in a bathtub - "
            "and trained them to look straight into the lens and tell the "
            "story in the present tense, so the audio could work as "
            "narration. Later seasons installed a closet with a sofa and a "
            "fixed camera; a producer's description, recorded in the press, "
            "is the sharpest sentence on the format: 'a public space that "
            "everyone pretended was a private space'. The viewer is not a "
            "confidante; the viewer is the intended addressee of a scene the "
            "crew staged and the editors selected.",

            "**The booth is infrastructure for somebody else's "
            "attachment.** The confessional is the compact through which a "
            "reality participant becomes a figure you can feel alone with: it "
            "manufactures the feeling of being spoken to directly - 'this "
            "person is talking directly to me', as one account of the format "
            "puts it - and the far side of that conversation is edited by "
            "people the viewer never meets. The competing placement, the "
            "presenter, fails because the speaker is not an employee assigned "
            "the second person on someone else's schedule; the machinery "
            "between viewer and figure - who is chosen, when they speak, what "
            "the editor keeps - is the platform's property, which is the "
            "shelf this entry is filed on. The booth's later children on "
            "this site are the reality celebrity and the live stream that "
            "inherits the address."
        ],
        ["television_unscripted"],
        [
            {"to": "reality-celebrity", "type": "preceded"},
            {"to": "twitch-launch", "type": "preceded"},
        ],
        [
            src("The Encyclopedia of Television, \"Real World, The\" "
                "(tvencyclopedia.org)",
                "https://www.tvencyclopedia.org/tv-encyclopedia13/"
                "real-world-the",
                "The spring-1992 origin of the format, the confessionals "
                "allowing cast members 'in solitude, to directly address a "
                "video camera in a manner similar to a video diary', and the "
                "claim that the confessional is 'a Real World invention' "
                "adopted by Survivor, Boot Camp, Making of the Band, Big "
                "Brother and Road Rules."),
            src("The New Yorker, \"How 'The Real World' Created Modern "
                "Reality TV\" (E. Nussbaum, 2024)",
                "https://www.newyorker.com/culture/the-weekend-essay/"
                "how-the-real-world-created-modern-reality-tv",
                "The confessional as a defining trope: intimate interviews "
                "repurposed as narration, the present-tense looking-into-the-"
                "lens training, the interview locations of the first season, "
                "and the later closet-with-camera set-up described as 'a "
                "public space that everyone pretended was a private space'."),
            src("The Cut, \"How the Reality TV Confessional Shaped Our "
                "Digital Lives\" (L. Staples, 2022)",
                "https://www.thecut.com/2022/10/reality-tv-confessional-"
                "interview-history-evolution-digital.html",
                "The confessional as the moment reality television became a "
                "cohesive medium, its function as cast 'thought bubbles', the "
                "breaking of the fourth wall, and the direct-address effect "
                "described as 'this person is talking directly to me'."),
            src("New York Post, \"How 'The Real World: New York' found its "
                "cast - and its success\" (C. Hirsch, 2021)",
                "https://nypost.com/2021/03/04/how-the-real-world-new-york-"
                "found-its-cast-and-its-success/",
                "The first-season facts: seven cast members in the Soho loft "
                "from February to May 1992, thirteen episodes, and the "
                "premiere on 21 May 1992."),
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
                continue
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