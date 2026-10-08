# -*- coding: utf-8 -*-
"""Add six encyclopedia entries answering the thinnest media.

Item 32 (the media-supply finding) is recorded in `tools/atlas.py`: stage,
comics, visual_art and radio carry so little that a cadence walking the axis
would have exhausted them in under a week. These six lift them together:

  rocky-horror       stage+film   1976  the audience performs its own side of a
                                       one-sided tie: the midnight run began in
                                       a single cinema and the callback came
                                       from the seats
  edwin-drood        stage        1985  the audience votes the ending into being,
                                       inside a band the production has already
                                       guaranteed
  death-in-family    comics       1988  Robin died by 72 votes on a premium-rate
                                       phone line - the vote that priced a
                                       character's life at fifty cents a call
  marilyn-diptych    visual_art   1962  fifty identical Monroes: the dead person
                                       turned into a pattern you can look at
                                       without her
  amos-n-andy        radio        1928  forty million listeners a night, and the
                                       audience they caricatured organized
  marvel-letters-page comics      1962  the printed reply that made the exception
                                       into a schedule, and the prize that was
                                       nothing

Every record below is `unverified`, not `retrievable`. Nothing here was fetched
- the text was read through a search index - and `retrievable` means a reader
can open it *and that was checked*. The status reason is stated in the claim of
every record, which is the rule this corpus has used since the Met Museum pages
returned 429 twice and were left unverified rather than promoted.

Relations follow the direction `citation_audit.py` enforces: `preceded` means
this entry's year is the smaller, `succeeded` means the target's is, and a tie
is `contemporary`. The inline assertion in `add_nancy_drew.py` states that rule
backwards and never fired because `nancy-drew` has only `instance_of` and
`contemporary`; do not copy it. `cites`, `depicts` and `instance_of` are not
chronological claims and are free of that constraint.

The two vote entries (`edwin-drood`, `death-in-family`) are filed as a pair on
purpose: same manufactured consequence, one in a theatre and one on a telephone
line, three years apart, and each entry declares the relation to the other.

Usage:  python tools/add_media_entries.py            (dry run)
        python tools/add_media_entries.py --apply
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

TARGET_IDS = ["rocky-horror", "edwin-drood", "death-in-family",
              "marilyn-diptych", "amos-n-andy", "marvel-letters-page"]

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
        "rocky-horror",
        "The audience became the show",
        "event", 1976, "Live",
        ["application"], ["crossover", "world"],
        "Launched as a small London stage musical in 1973, filmed in 1975, "
        "and from 1976 screened at midnight before a room that shouted back: "
        "The Rocky Horror Picture Show ran while its audience performed it, "
        "wearing the costumes, speaking the lines, improvising replies. The "
        "screen never answered a single shout. The room was the show.",
        [
            "**The subject here is not the film; it is the room it ran in.** "
            "The Rocky Horror Show that Richard O'Brien wrote opened at the "
            "Royal Court Theatre Upstairs in London on 19 June 1973, and the "
            "remembered film version arrived in 1975. Then, in 1976, one "
            "Manhattan cinema, the Waverly, began showing it after midnight. "
            "The fan-run history kept in the records credits an advertising "
            "man, Tim Deegan, with persuading Bill Quigley of the Walter "
            "Reade organisation to book it, and the theatre's manager, Denise "
            "Borden, with the nightly fight that followed. It is kept as "
            "unverified rather than promoted, because this corpus does not "
            "promote a page it did not open.",

            "What happened in the room is the entry. The first documented "
            "callback came on Labor Day weekend 1976, an audience member's "
            "shout about an umbrella aimed at the screen, and the shouting "
            "hardened into a repertoire: lines the audience said, props it "
            "threw, clothes it wore, rules about when talking was allowed at "
            "all. Sal Piro, who saw the film more than a thousand times and "
            "wrote the book this culture kept, became its chronicler. The "
            "film was the same film every night; nothing in the fiction ever "
            "answered. **The audience built the reply end of a one-sided "
            "tie, in public, together, on a schedule.**",

            "Rocky Horror is the largest early case in this corpus of an "
            "audience performing its own side of a one-sided relationship: "
            "wearing the characters, speaking their lines back, improvising "
            "responses to a text that cannot hear them. What the evening "
            "offered was not a chance to change the film but a chance to be "
            "the change. **Participation here never touches the fiction, and "
            "that is exactly why it works.** The contemporary entry in the "
            "corpus that shares its year is the convention itself; this one "
            "is the screening that turned the convention into a habit."
        ],
        ["stage", "film"],
        [
            {"to": "con-culture", "type": "contemporary"},
            {"to": "star-trek-con", "type": "succeeded"},
            {"to": "parasocial-interaction", "type": "depicts"},
        ],
        [
            src("Wikipedia, \"The Rocky Horror Show\"",
                "https://en.wikipedia.org/wiki/The_Rocky_Horror_Show",
                "The musical Richard O'Brien wrote opened at the Royal Court "
                "Theatre Upstairs in London on 19 June 1973 and is the "
                "predecessor the film remembered; the writer credit, the "
                "venue, the date and the director all come from here."),
            src("Wikipedia, \"The Rocky Horror Picture Show\"",
                "https://en.wikipedia.org/wiki/The_Rocky_Horror_Picture_Show",
                "The 1975 Westwood premiere of the film, the beginning of "
                "the midnight screenings in 1976, the growth of the cult "
                "following, the callbacks and the prop rituals: what the "
                "films section of the record rests on."),
            src("Rocky Horror official fan history, \"How It All Began\"",
                "https://www.rockyhorror.com/history/howapbegan.php",
                "The Waverly origin as the site tells it: the midnight "
                "experiment beginning around April 1976, arranged by the ad "
                "man Tim Deegan with Bill Quigley of the Walter Reade "
                "organisation and the theatre manager Denise Borden, the "
                "first documented callback during Labor Day weekend 1976, "
                "and Sal Piro's early role. A fan-run account, recorded as "
                "unverified."),
        ],
    ),

    make(
        "edwin-drood",
        "Vote for the murderer",
        "work", 1985, "Theatre",
        ["application", "manipulation"], ["contest", "world"],
        "A musical of Dickens' unfinished novel that stops where the novel "
        "stops and turns the cliffhanger over to the seats: the audience "
        "votes who murdered Edwin Drood, who the disguised Dick Datchery is "
        "and which two characters end up together, and the cast performs the "
        "chosen ending that night. The house was promised 1,200 possible "
        "endings and that it 'won't be rigged in any way'.",
        [
            "**A show sells the feeling of authorship and the feeling is the "
            "product.** The Mystery of Edwin Drood is the musical Rupert "
            "Holmes built out of the novel Charles Dickens left unfinished "
            "at his death in 1870. It premiered at the Delacorte Theater in "
            "Central Park on 21 August 1985, moved to Broadway in December, "
            "and won five Tonys including Best Musical. When Dickens's plot "
            "runs out, the cast asks the audience to vote: who killed "
            "Drood, who the disguised Dick Datchery is, and which two "
            "characters the show will reward with each other. The "
            "director's own framing is in the records - \"the last 40 "
            "minutes will be up for grabs every night\", 1,200 possible "
            "endings, \"it won't be rigged in any way\".",

            "The freedom had a border, and the border is the interesting "
            "half. A production that cannot guarantee a shape cannot "
            "guarantee an ending, so the industry hedges: the reference "
            "account records that some smaller companies fix the results to "
            "keep the number of performable endings manageable, and that "
            "some houses refuse to count votes for the obvious culprit so "
            "the reveal keeps its twist. The vote is tallied by applause "
            "and by seating area while the actors wait. **The audience is "
            "deciding inside a band the production has already guaranteed, "
            "and the decision is scored as a vote rather than as an "
            "experiment.**",

            "Drood tells the audience the fiction's ending is theirs, and "
            "everything that makes that true - the tallying, the hedging, "
            "the rehearsed alternatives - happens where they are not. "
            "Three years later the same device ran on a telephone line, "
            "which is the relation to the comics entry this page points at: "
            "the manufactured consequence is identical, the room is "
            "different. **What the audience got to do felt like control "
            "over the characters, and the vote was the machine that made "
            "the feeling.**"
        ],
        ["stage"],
        [
            {"to": "queen-for-a-day", "type": "succeeded"},
            {"to": "dickens", "type": "cites"},
            {"to": "death-in-family", "type": "preceded"},
        ],
        [
            src("Wikipedia, \"The Mystery of Edwin Drood (musical)\"",
                "https://en.wikipedia.org/wiki/The_Mystery_of_Edwin_Drood_"
                "(musical)",
                "The show as a whole: the first Broadway musical with "
                "multiple endings determined by audience vote, the five "
                "Tonys, the writer Rupert Holmes, the vote covering the "
                "murderer, Dick Datchery's identity and the romantic "
                "pairing, and the ways the industry bounds the freedom "
                "(fixed results in some smaller companies, uncounted votes "
                "for the obvious culprit in some houses)."),
            src("The New York Times, 3 May 1985, \"Broadway\"",
                "https://www.nytimes.com/1985/05/03/theater/broadway.html",
                "Director Wilford Leach's own framing of the mechanism: "
                "\"The last 40 minutes will be up for grabs every night\", "
                "the 1,200 possible endings, and \"it won't be rigged in "
                "any way\"; previews were to begin at the Delacorte in "
                "August 1985."),
            src("The New York Times, 23 August 1985, \"STAGE: 'DROOD,' A "
                "MUSICAL IN THE PARK\"",
                "https://www.nytimes.com/1985/08/23/theater/stage-drood-a-"
                "musical-in-the-park.html",
                "The contemporary review's description of the vote: the "
                "audience \"solves, resolves and concludes the mystery\" by "
                "voice and hand to a series of multiple-choice propositions, "
                "an election led by the evening's master of ceremonies."),
            src("Betty Buckley, official stage history of \"Drood\"",
                "https://www.bettybuckley.com/biography/stage/drood/",
                "The premiere dates the section uses: a first performance at "
                "the Delacorte Theater in Central Park on 21 August 1985 as "
                "a New York Shakespeare Festival production, the vote by "
                "seating districts, and the mechanism it calls \"an "
                "intricate parlor game\"."),
        ],
    ),

    make(
        "death-in-family",
        "Robin died by 72 votes",
        "event", 1988, "Fandom",
        ["consideration", "manipulation"], ["contest", "danger"],
        "In September 1988 Batman's readers called a premium-rate number, "
        "fifty cents a call, to decide whether the Joker's beaten Robin "
        "lived or died. The poll ran for about a day and a half and came "
        "down to 72 votes: 5,343 killed him, 5,271 spared him, and the "
        "issue that revealed the verdict had been prepared both ways.",
        [
            "**The audience's attachment to a fictional child was measured "
            "in change taken out of pockets, and it was a coin flip.** In "
            "September 1988 DC Comics asked its readers to settle the "
            "lives of the Joker's beaten sidekick by telephone. On the back "
            "cover of Batman #427 an advertisement showed Batman carrying "
            "the injured Robin and warned that readers could yet \"prevent "
            "it with a telephone call\"; two 900 numbers were printed, one "
            "for each verdict. The lines were open for about a day and a "
            "half from 9 a.m. Eastern on 15 September, and each call cost "
            "fifty cents.",

            "The numbers are the story. 10,614 calls were counted: 5,343 "
            "for the death, 5,271 against, a margin of 72. The result was "
            "kept secret, and the issue that carried the outcome was "
            "prepared two ways and finished in secrecy because the ending "
            "could not be known until the tally closed. The editor's own "
            "framing is in the records: the telephone poll was an extension "
            "of the policy of heeding what fans said in letters and at "
            "conventions, and the publisher did not want to waste the "
            "technology on whether Firestorm's boots should be red or "
            "yellow. \"This had to be important stuff. Life-and-death.\"",

            "The sources disagree about the window, and the disagreement is "
            "kept: the publisher's own account says 36 hours, the reference "
            "account says 35, from 9 a.m. Eastern on 15 September. The "
            "closeness is the point. One account discloses that, with "
            "fifteen minutes left, survival was ahead by 38 votes before "
            "the final tally swung; a swing of a few dozen calls changed "
            "canon for decades. **A character's death was decided by "
            "whoever had a telephone and a dollar, and the margin is why "
            "the device keeps being retold.**",

            "Three years earlier a Broadway musical had shown an audience "
            "how a vote over a story feels - the relation this page points "
            "to - but that vote was free and stayed in the room. Here the "
            "vote left the room, priced itself, and could not be repeated "
            "once the lines closed. The pair is the same manufactured "
            "consequence, one in a theatre and one on a telephone line: "
            "both let the audience feel like co-authors of a fiction that "
            "never read any of the replies."
        ],
        ["comics"],
        [
            {"to": "edwin-drood", "type": "succeeded"},
            {"to": "protagonist-parasocial", "type": "instance_of"},
            {"to": "killing-off", "type": "preceded"},
        ],
        [
            src("Wikipedia, \"A Death in the Family (comics)\"",
                "https://en.wikipedia.org/wiki/A_Death_in_the_Family_(comics)",
                "The vote as recorded: two 900 numbers (one per verdict), "
                "the lines open about 35 hours from 9 a.m. Eastern on "
                "September 15 1988, 10,614 votes with 5,343 for death and "
                "5,271 against - a margin of 72 - the back-cover \"prevent "
                "it with a telephone call\" appeal, the dual-preparation of "
                "the revealing issue, and the unproven hearsay that a "
                "lawyer programmed a Macintosh to redial the killing number."),
            src("DC, \"How 'A Death in the Family' Shook the World\" "
                "(J. Lapin-Bertone, 12 October 2020)",
                "https://www.dc.com/blog/2020/10/12/how-a-death-in-the-"
                "family-shook-the-world",
                "The publisher's account: the poll as an extension of "
                "heeding fans' letters and convention talk, the editor's "
                "\"This had to be important stuff. Life-and-death.\", the "
                "36-hour window, 10,614 calls and the 72-vote margin, and "
                "the claim that 72 more votes would have changed Batman "
                "history."),
            src("How to Love Comics, \"A Death in The Family: The Batman "
                "Comic That Killed Robin\" (12 October 2020)",
                "https://www.howtolovecomics.com/2020/10/12/batman-a-death-"
                "in-the-family/",
                "The ad on the back of Batman #427 inviting the call "
                "appears here as a reproduction, along with the 36-hour "
                "window, the 72-vote margin, and the editor's disclosure "
                "revealed in the back of #429 that survival was ahead by "
                "38 votes with fifteen minutes left."),
        ],
    ),

    make(
        "marilyn-diptych",
        "Fifty copies of a face",
        "work", 1962, "Modern",
        ["consideration"], ["idol", "grief"],
        "Warhol's 1962 double panel repeats one publicity still of Marilyn "
        "Monroe fifty times: colour on the left, draining to monochrome on "
        "the right, taken from Gene Kornman's Niagara photograph. Monroe "
        "died in August of that year, and the silkscreen turns her into a "
        "pattern a person can look at without her.",
        [
            "**The diptych is a piece of mourning with the mourner "
            "deleted.** Andy Warhol's two-panel silkscreen is made of fifty "
            "copies of one publicity photograph - taken by Gene Kornman "
            "for the 1953 film Niagara - twenty-five in colour on the left "
            "and twenty-five fading to a grey ghost on the right. Monroe "
            "died in August 1962. The museum that holds the work records "
            "Warhol's own timing: he got the idea to make screens of her "
            "face the month she died.",

            "The repetition is the meaning, and it is the opposite of a "
            "portrait. Fifty identical faces are not fifty chances to look "
            "at her; they are a pattern to be looked at without answering. "
            "The process is manufacture by design - silkscreen is the "
            "reproduction of a reproduction, and Warhol made a whole series "
            "of her that year, of which this double panel is the best "
            "known. The difference between a portrait and a product is "
            "exactly what the paint process erases.",

            "What the pattern makes is the kind of image this corpus has "
            "already met once: the empty-wall entry records the first crowd "
            "gathered around a painted absence, thousands coming to look at "
            "hooks. The diptych makes the absence portable and repeatable - "
            "a public image the person is not required to maintain for you, "
            "because the person died and the manufacture went on. It is "
            "filed under the shelf for the historic-as-character: the real "
            "woman flattened into a type the silkscreen imposes, and every "
            "accurate fact about her in tension with the attachment the "
            "picture invites."
        ],
        ["visual_art"],
        [
            {"to": "rudolph-valentino", "type": "succeeded"},
            {"to": "gazing-at-celebrities", "type": "depicts"},
            {"to": "mona-lisa-theft", "type": "cites"},
        ],
        [
            src("Tate, \"Andy Warhol, Marilyn Diptych 1962\"",
                "https://www.tate.org.uk/art/artworks/warhol-marilyn-"
                "diptych-t03093",
                "The work as the museum presents it: the 1962 date, the "
                "fifty repeated images from a publicity still photographed "
                "by Gene Kornman for Niagara, the colour-then-monochrome "
                "arrangement, Monroe's death in August 1962, Warhol's "
                "recollection of getting the idea to make screens of her "
                "face that month, and the work's passage from Emily and "
                "Burton Tremaine to the Tate in 1980."),
            src("Wikipedia, \"Marilyn Diptych\"",
                "https://en.wikipedia.org/wiki/Marilyn_Diptych",
                "The description the entry's numbers rest on: fifty "
                "repetitions of the single 1953 publicity still, twenty-five "
                "in colour at the left and twenty-five in black and white "
                "drained to the right, in the context of the series of "
                "Monroes Warhol made that year."),
        ],
    ),

    make(
        "amos-n-andy",
        "The audience organised against the show",
        "work", 1928, "Radio",
        ["consideration"], ["idol", "world"],
        "Two white broadcasters voiced two fictional black men from March "
        "1928, and at its peak about forty million listeners a night "
        "followed their fortunes - half the nation's radios, by one "
        "estimate. The audience the show loved most was also the one it "
        "caricatured, and from 1931 that audience organised.",
        [
            "**The audience that loved the show most was the one it "
            "caricatured, and that audience organised.** Amos 'n' Andy "
            "began on WMAQ in Chicago on 19 March 1928, created, written "
            "and voiced by two white performers, Freeman Gosden and Charles "
            "Correll, playing two fictional black men. It grew out of Sam "
            "'n' Henry, which had itself begun as the pair's attempt to "
            "adapt a comic strip for radio - the broadcast history in the "
            "records calls the show a \"radio comic strip\". By the 1930-31 "
            "peak the audience was enormous: roughly forty million "
            "listeners a night, half the nation's radios by the "
            "Smithsonian's count, listening to a nightly serial that the "
            "record calls the fountainhead of both the situation comedy "
            "and the soap opera.",

            "The complaint ran through the same machinery the fandom ran. "
            "After a December 1930 attack in Abbott's Monthly by Bishop "
            "W. J. Walls, the Pittsburgh Courier pushed a six-month "
            "campaign, and the reference account records that more than "
            "700,000 African-Americans petitioned the Federal Radio "
            "Commission about the show's stereotyping in 1931. The "
            "television version, with an all-Black cast told to keep its "
            "voices close to the white originals, drew the NAACP's formal "
            "protest within days of its June 1951 premiere: its bulletin "
            "on why the show should be taken off the air itemised the "
            "stock figures - \"every character is either a clown or a "
            "crook\". CBS cancelled the show in 1953; the sponsor had "
            "discontinued its advertising the same June.",

            "This is the corpus's diagnostic for an audience that exists "
            "as an institution rather than a screen: its machinery is its "
            "own. A newspaper campaign, a petition to a regulator, a "
            "sponsor's boycott notice - each acted on people who were not "
            "members of anything the audience owned. **The attachment to "
            "the characters was real enough to make the complaint precise, "
            "and the complaint was that the images were not theirs to "
            "love.**"
        ],
        ["radio"],
        [
            {"to": "comic-strip", "type": "succeeded"},
            {"to": "mickey-mouse", "type": "contemporary"},
        ],
        [
            src("Wikipedia, \"Amos 'n' Andy\"",
                "https://en.wikipedia.org/wiki/Amos_%27n%27_Andy",
                "The premiere on 19 March 1928 on WMAQ, the Gosden and "
                "Correll credits, the 40-million peak audience of 1930-31, "
                "the 1931 petition by more than 700,000 African-Americans "
                "to the Federal Radio Commission, the 1951-53 television "
                "series and the NAACP bulletin with its itemised "
                "characterizations, Blatz withdrawing sponsorship in June "
                "1953, and syndication until 1966."),
            src("Museum of Broadcast Communications, \"Amos 'n' Andy\" "
                "(radio encyclopedia)",
                "https://www.museum.tv/radio-encyclopedia/amos-n-andy",
                "The serial's shape as the industry recorded it: the "
                "\"radio comic strip\" framing and the WGN origins around "
                "adapting The Gumps, the January 1926 start of Sam 'n' "
                "Henry, the move to WMAQ with disc syndication - the "
                "\"chainless chain\" - the claim that it was the "
                "fountainhead of the situation comedy and the soap opera, "
                "and the 1930-31 audience that exceeded 40 million."),
            src("Television Academy (interview archive), \"Amos 'n' Andy\"",
                "https://interviews.televisionacademy.com/shows/amos-n-andy",
                "The broadcast records the entry leans on: origin on WMAQ "
                "on 19 March 1928, claim to be the longest-running radio "
                "program in broadcast history, the 1951-53 television "
                "version as the first series with an all-Black cast, the "
                "NAACP's attempted injunction against its premiere, and the "
                "advertising trade's reported \"No Negro performers "
                "allowed\"."),
            src("Smithsonian Magazine, \"The Long, Unfortunate History of "
                "Racial Parody in America\" (G. DuBois Shaw, 2016)",
                "https://www.smithsonianmag.com/smithsonian-institution/"
                "long-unfortunate-history-racial-parody-america-180960947/",
                "The scale claim in one line: \"As many as 40 million "
                "people - over half of the nation's radios - tuned in each "
                "week\"; the show's roots in 19th-century blackface "
                "minstrelsy and the way radio let the performers stress "
                "the oral side of the form."),
        ],
    ),

    make(
        "marvel-letters-page",
        "The reply that was printed",
        "mechanism", 1962, "Fandom",
        ["application"], ["companion", "creator"],
        "From 1962 Stan Lee ran fan mail in the back of The Fantastic Four "
        "and answered it in print in his own voice, so a reader could see "
        "their name answered on a page. The letters page became Marvel's "
        "institutional address to its readership, and its regular trophy, "
        "the No-Prize, was deliberately nothing.",
        [
            "**The corpus keeps the datum that a reply used to be the "
            "exception. This is the same object with the exception "
            "removed.** From the early issues of The Fantastic Four, "
            "cover-dated 1962, Stan Lee printed readers' letters and "
            "answered them on the page. Lee's own 1992 account traces the "
            "habit to the Jerry Todd books, which printed readers' letters "
            "and the author's informal answers, and he concluded that "
            "\"talking to the readers informally and indirectly seemed "
            "like the natural thing to do.\" The page ran polls - whether "
            "the Invisible Girl should leave the team - and offered five "
            "dollars for the best explanation of a continuity error.",

            "The reply became a scheduled product. A contest whose prize "
            "was nothing got a name when its winner was announced, and the "
            "name stuck: the No-Prize. By the end of 1965 the letters "
            "section had grown into the house page, and from 1967 a "
            "regular column made the reply a fixture. The trophy became a "
            "posted ritual: winners were mailed a pre-printed empty "
            "envelope reading \"this envelope contains a genuine Marvel "
            "Comics No-Prize which you have just won!\", and some readers "
            "wrote back to ask where the prize had fallen out. **The award "
            "was the reply; the envelope was the receipt.**",

            "The voice outlived the man: the page passed to the editors "
            "who followed Lee, which is the tell that the intimacy was "
            "institutional rather than personal. It belongs in this corpus "
            "where the intermediary that is also the relationship sits - "
            "the infrastructure for somebody else's attachment. A reader's "
            "name printed next to an answer is the demonstration of being "
            "seen while nothing on the other side was made available, and "
            "the demonstration was mass-produced on a schedule."
        ],
        ["comics"],
        [
            {"to": "fan-mail", "type": "succeeded"},
            {"to": "marvel-club", "type": "succeeded"},
        ],
        [
            src("Wikipedia, \"Bullpen Bulletins\"",
                "https://en.wikipedia.org/wiki/Bullpen_Bulletins",
                "The institutional history: Lee's 1992 account of the Jerry "
                "Todd books and the naturalness of replying to readers "
                "informally, the letters section of Fantastic Four as the "
                "start, the Special Announcements section and the Mighty "
                "Marvel Checklist in the issue dated December 1964, the "
                "first standalone house page in the issues dated December "
                "1965, and the regular column first appearing in June "
                "1967."),
            src("Wikipedia, \"Marvel No-Prize\"",
                "https://en.wikipedia.org/wiki/Marvel_No-Prize",
                "The prize's history: the five-dollar offer on the "
                "Fantastic Four letters page for the best explanation of a "
                "continuity error, the contest whose prize was nothing "
                "becoming named when its winner was announced, and the "
                "practice, beginning 1967, of mailing pre-printed empty "
                "envelopes \"containing\" the No-Prize, with readers asking "
                "where their prize had fallen out."),
            src("Comic Book Resources, \"The History of Marvel's No-Prize\" "
                "(Brian Cronin, 2016)",
                "https://www.cbr.com/knowledge-waits-the-history-of-marvels-"
                "no-prize/",
                "The chronology the entry follows: the letters section "
                "beginning with Fantastic Four #3 (cover-dated March 1962, "
                "on sale in late 1961), Lee's reader polls on the page, and "
                "the largest-collection contest (issue #22) whose winner "
                "announcement (issue #25) gave the No-Prize its name."),
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
        sys.exit("refusing: id set changed by more than the six additions")
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
        print(f"    {e['id']:20s} {e['kind']:10s} {e['year']}"
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