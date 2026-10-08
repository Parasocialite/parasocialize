# -*- coding: utf-8 -*-
"""Add six encyclopedia entries covering the 1910s, 1933 and 1938.

The 1910s are the thinnest decade in the corpus and the only one where the
machine the rest of the site describes is still being assembled in public.
`film-serial` (1912) is the only entry with a year below 1920. Four of the six
below sit between 1911 and 1914, and they are chosen to be structural rather
than biographical: two events, one mechanism, two people who were the first to
have their reach counted.

  mona-lisa-theft    the first crowd gathered around an absence, and the first
                     mass image made by a theft rather than by a painter
  the-fan-magazine   the first institution that rationed a reply, and the third
                     rule - the studios' addresses will not be given - is the
                     whole business model
  mary-pickford      the first performer whose fan worship shows up inside a
                     contract rather than inside a review
  charlie-chaplin    a likeness used as an address, a costume and a disguise:
                     a picture other people start using as an instruction
  war-of-the-worlds  the consideration case for broadcast fiction, filed as
                     myth against reality with both halves kept
  fireside-chats     the application case: informality written into the text on
                     purpose, by an office holding the whole schedule

Every record below is `unverified`, not `retrievable`. Nothing here was
fetched - the text was read through a search index - and `retrievable` means a
reader can open it *and that was checked*. The status reason is stated in the
claim of every record, which is the rule this corpus has used since the Met
Museum pages returned 429 twice and were left unverified rather than promoted.

Relations follow the direction `citation_audit.py` enforces: `preceded` means
this entry's year is the smaller, `succeeded` means the target's is. The inline
assertion in `add_nancy_drew.py` states that rule backwards and never fired
because `nancy-drew` has only `instance_of` and `contemporary`; do not copy it.

Usage:  python tools/add_1910s_entries.py            (dry run)
        python tools/add_1910s_entries.py --apply
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

TARGET_IDS = ["mona-lisa-theft", "the-fan-magazine", "mary-pickford",
              "charlie-chaplin", "war-of-the-worlds", "fireside-chats"]

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
        "mona-lisa-theft",
        "Thousands came to gawk at the empty wall",
        "event", 1911, "Press",
        ["application"], ["idol", "world"],
        "An Italian workman walked out of the Louvre with the painting under "
        "his coat, and the wall it had hung on went on drawing a crowd: four "
        "iron hooks, no picture, and thousands of people come to look at the "
        "hooks anyway. The papers printed the absence, and when she came back "
        "she had become public property - the first mass art icon, made by a "
        "thief rather than by a painter.",
        [
            "**A crowd stood in front of an empty wall, and that is the whole "
            "entry.** The four hooks were still there and people came to look "
            "at them - \"thousands of people came to gawk at the empty wall "
            "where the painting had once hung\". L'Illustration printed the "
            "question the absence had raised for it: \"What audacious "
            "criminal, what mystifier, what maniac collector, what insane "
            "lover, has committed this abduction?\" A picture nobody could "
            "see was being discussed in the language reserved for a "
            "kidnapping, which is the correct language for the situation and "
            "is also the first time in this corpus that a crowd's attention "
            "is described as a taking rather than as a looking.",

            "The scale is recorded twice and the two records do not agree. One "
            "has \"more than 100,000 people viewed it\" after the return; the "
            "other has \"at least 120,000 people went to see the painting in "
            "the first two days after it was returned\". Both are kept, "
            "because the disagreement is the evidence - numbers that size are "
            "what a public looks like once an object has become a story. The "
            "record also disagrees about the theft itself: one man, or three. "
            "That disagreement is kept too, and neither version changes a "
            "word of the entry, which is about the wall rather than about "
            "who carried her out of it.",

            "What the theft produced is the sentence worth having. As the "
            "account the entry leans on puts it, \"The Mona Lisa had left the "
            "Louvre a work of art. She returned as public property, the first "
            "mass art icon.\" Satirical postcards, a short film and cabaret "
            "songs followed, and \"popular culture seized upon the theft and "
            "turned high art into mass art.\" **The image went on doing the "
            "work the canvas used to do, and the canvas came back as "
            "something people queued to be near.**",

            "Peruggia is the one attachment in the record that answers "
            "itself. He said he had fallen \"a victim to her smile\" and "
            "feasted his eyes on his treasure every evening, which is a "
            "one-sided tie describing itself out loud and in a courtroom's "
            "vocabulary. The crowd had the same tie and no sentence for it, "
            "which is what the queue in front of the hooks was. **She was "
            "not there for either of them, and being not-there is the whole "
            "of the arrangement.**",
        ],
        ["visual_art"],
        [{"to": "the-fan-magazine", "type": "contemporary"},
         {"to": "parasocial-interaction", "type": "depicts"}],
        [
            src("History.com, \"The Heist That Made the Mona Lisa Famous\"",
                "https://www.history.com/articles/the-heist-that-made-the-mona-lisa-famous",
                "The entry's spine, and the source of its title. That \"The "
                "Mona Lisa is gone\"; that \"thousands of people came to gawk "
                "at the empty wall where the painting had once hung\"; the "
                "question L'Illustration printed, \"What audacious criminal, "
                "what mystifier, what maniac collector, what insane lover, "
                "has committed this abduction?\"; Peruggia, \"I fell a victim "
                "to her smile and feasted my eyes on my treasure every "
                "evening\"; the article's own summary, \"The Mona Lisa had "
                "left the Louvre a work of art. She returned as public "
                "property, the first mass art icon.\"; and \"At least 120,000 "
                "people went to see the painting in the first two days after "
                "it was returned\". Also the account of the theft and of the "
                "recovery, which is what the entry's year rests on."),
            src("Smithsonian Magazine, \"What Happened When the Mona Lisa "
                "Was Stolen\"",
                "https://www.smithsonianmag.com/smart-news/happened-when-mona-lisa-was-stolen-180977488/",
                "The thieves, the wall, and the mass image - and the count "
                "that disagrees with the record above. That \"Vincenzo "
                "Perugia and the brothers Lancelotti, Vincenzo and Michele, "
                "young Italian handymen\" took her, which is the three-man "
                "version the entry keeps beside the one-man version; the "
                "\"empty wall with its four lonely iron hooks\"; that "
                "satirical postcards, a short film and cabaret songs "
                "followed, and that \"popular culture seized upon the theft "
                "and turned high art into mass art\"; and \"more than 100,000 "
                "people viewed it\"."),
            src("The Guardian, 5 August 2011 - report on the centenary of the "
                "1911 theft of the Mona Lisa from the Louvre",
                "https://www.theguardian.com/artanddesign/2011/aug/05/mona-lisa-theft-louvre-leonardo",
                "The dating and the caveat the entry depends on. \"It was 24 "
                "hours before anyone noticed she was missing.\"; and \"the "
                "Mona Lisa certainly wasn't universally known in 1911\", "
                "which is why the theft rather than the painting made her "
                "famous."),
        ],
    ),

    make(
        "the-fan-magazine",
        "Thousands of letters, and a handful printed",
        "mechanism", 1911, "Press",
        ["application", "manipulation"], ["idol"],
        "The first movie fan magazine appeared in February 1911, because by "
        "1910 the letters were arriving faster than the studios could absorb "
        "them. What it invented was not the letter but the reply - a "
        "department, a set of rules, a Chicago address, and a flat refusal to "
        "publish studio addresses. Thousands of letters went in. A handful "
        "were printed.",
        [
            "**The valve is the product.** Readers wrote to the magazines "
            "because a face on a screen had no other address, and the "
            "magazines gave them one that deliberately was not the studio's. "
            "Three rules do the work in the correspondence department the "
            "entry quotes: address your letters to Questions and Answers at "
            "the magazine in Chicago; \"Players will answer your letters when "
            "they have time if you send a stamped envelope\"; and \"Studio "
            "addresses will not be given in this Department.\" The third rule "
            "is the whole business. A column that passed every address "
            "through would have been a directory, and a directory is not a "
            "magazine.",

            "The rationing is stated by the people who counted it: \"Of the "
            "thousands of letters that reached the magazine, a handful were "
            "printed.\" The handful was chosen for flavour - a reader calling "
            "herself Juliet who had to know about a man in the movies was "
            "told, \"Well, we will hope for you, Juliet!\" The judgement "
            "worth keeping is Slide's: these magazines were published *for* "
            "fans rather than by them. **The fan supplied the demand and the "
            "letter; the magazine supplied the voice, and the voice was "
            "rationed on purpose.**",

            "It scaled the way the attachment scaled. In February 1911 J. "
            "Stuart Blackton of Vitagraph organised Motion Picture Story "
            "Magazine, \"the first movie fan magazine\"; it was shortened to "
            "Motion Picture Magazine in 1914 and ran monthly until 1977, with "
            "circulation around 248,845 in 1919 and 400,000 three years "
            "later. The reason it could scale sits in the same record: \"As "
            "thousands of letters flooded movie studios\", the public "
            "relations departments tried to accommodate the interest. The "
            "Henry Ford's account of the arrangement is blunt - the stories "
            "\"were carefully controlled by the studios' public relations "
            "staff\", and it was \"a strange marriage between the studios, "
            "which needed the support of the magazines, and the magazines, "
            "whose existence depended on the success and goodwill of the "
            "industry.\" **The channel that rationed the reply on the "
            "reader's behalf was rationed on the studio's.**",

            "The origin is in the same register. Hutchinson's history of "
            "Photoplay opens with the studio boss's cynical wheeze: Carl "
            "Laemmle spread a rumour that the Biograph Girl had been killed "
            "in a traffic accident, then advertised that the story was a lie "
            "and that she was alive and about to star in his company's "
            "picture. Star worship, in her phrase, \"like almost everything "
            "else in Hollywood, was born as a studio boss's cynical "
            "wheeze.\" The fan magazine did not create the attachment - it "
            "arrived when the letters did - but it was the first institution "
            "to find that the attachment could be rationed, printed and "
            "sold.",
        ],
        ["film"],
        [{"to": "mona-lisa-theft", "type": "contemporary"},
         {"to": "fan-mail", "type": "preceded"},
         {"to": "first-fans", "type": "preceded"}],
        [
            src("The Henry Ford, \"Going Hollywood: Movie Fan Magazines\"",
                "https://www.thehenryford.org/collections/explore/articles/going-hollywood-movie-fan-magazines",
                "The date the entry's year rests on, the founder, and the "
                "arrangement the `manipulation` half of the entry is about. "
                "\"In February 1911, J. Stuart Blackton, head of Vitagraph "
                "Studios, helped to organize Motion Picture Story Magazine, "
                "soon shortened to Motion Picture Magazine - the first movie "
                "fan magazine.\"; \"By 1910, the demand for information was "
                "out of control.\"; \"As thousands of letters flooded movie "
                "studios, public relations departments tried to accommodate "
                "fans' interest.\"; \"The stories that appeared were "
                "carefully controlled by the studios' public relations "
                "staff.\"; and \"It was a strange marriage between the "
                "studios, which needed the support of the magazines, and the "
                "magazines, whose existence depended on the success and "
                "goodwill of the industry.\""),
            src("Pamela Hutchinson, \"Photoplay magazine: the birth of "
                "celebrity culture\", The Guardian, 26 January 2016",
                "https://www.theguardian.com/film/filmblog/2016/jan/26/photoplay-magazine-hollywood-film-studios-stars-celebrity-culture",
                "The manufacture at the origin of the form, and the reading "
                "the entry's last paragraph turns on. That \"Star worship, "
                "like almost everything else in Hollywood, was born as a "
                "studio boss's cynical wheeze.\"; and the 1910 Carl Laemmle "
                "episode, in which a rumour that the Biograph Girl had been "
                "killed in a traffic accident was spread before adverts "
                "declared it a lie and announced her alive and about to play "
                "the lead in his company's film."),
            src("Lanckman, L. (2020). Fans, community, and conflict in the "
                "pages of 'Picture Play'. Transformative Works and Culture.",
                "https://journal.transformativeworks.org/index.php/twc/article/view/1745/2203",
                "The three rules the entry's first paragraph quotes, and the "
                "rationing its second is built on: \"Address your letters to "
                "'Questions and Answers, PHOTOPLAY MAGAZINE, Chicago'\"; "
                "\"Players will answer your letters when they have time if "
                "you send a stamped envelope\"; \"Studio addresses will not "
                "be given in this Department\"; Sequeira, \"Of the thousands "
                "of letters that reached the magazine, a handful were "
                "printed\"; the Juliet exchange, \"I have a romantic reason! "
                "... There is a man in the movies I simply must know. No, it "
                "isn't Bushman!\" answered by \"Well, we will hope for you, "
                "Juliet!\"; and Slide (2010) on magazines \"published for, "
                "not by, fans\". The same citation is already recorded on "
                "`first-fans` and `radio-serials` as retrievable; this copy "
                "was read through the search index rather than opened, so it "
                "carries the lower status."),
            src("Wikipedia, \"Motion Picture Magazine\"",
                "https://en.wikipedia.org/wiki/Motion_Picture_Magazine",
                "The run and the circulation, which are the entry's evidence "
                "that the form scaled. That the magazine ran from 1911 to "
                "1977; and that circulation rose from 248,845 in 1919 to "
                "400,000 in 1922. Corroboration of the shape rather than the "
                "authority for it - the first issue and the founder are "
                "Henry Ford's."),
            src("Internet Archive, \"Photoplay Magazine, February 1912\"",
                "https://archive.org/details/Photoplay0212",
                "The other half of the founding date, kept as a disagreement "
                "rather than resolved. That \"Photoplay began in August 1911 "
                "as a movie theater program in Chicago. In February 1912 it "
                "expanded to full magazine size with larger distribution.\"; "
                "that \"Photoplay was patterned after Motion Picture Story "
                "Magazine\"; and that the February 1912 issue is scanned "
                "from microfilm. The entry dates itself to the February 1911 "
                "title, not to Photoplay, and this record is what makes that "
                "choice explicit rather than silent."),
        ],
    ),

    make(
        "mary-pickford",
        "Known to more people than any other woman in history",
        "person", 1914, "Silent era",
        ["application"], ["idol"],
        "The first film performer whose value could be counted instead of "
        "guessed. She was on the cover of the New York Dramatic Mirror in "
        "1911, an honour then kept for theatrical stars; by 1916 her fan "
        "following had become ten thousand dollars a week, half her film "
        "profits and a production company of her own. The audience was never "
        "asked for any of it, and every line of the contract exists because "
        "of it.",
        [
            "**The fan worship is in the contract.** St. John's line, as the "
            "American Experience page quotes it, is the scale the entry works "
            "from: Pickford was \"known to more people and loved by more "
            "people than any other woman that has been in all history.\" "
            "Reach was the asset, and reach was countable. In 1911 she was "
            "the first movie star to adorn the cover of the New York Dramatic "
            "Mirror, an honour \"previously bestowed only on theatrical "
            "stars\" - the trade press had already decided that a "
            "moving-picture player could carry a cover, and the sentence that "
            "records it is careful to say what the honour used to be worth.",

            "Then 1914 and Tess of the Storm Country. The record says the "
            "picture \"caused a sensation\", that it \"created fan worship "
            "that had never before been witnessed\", and that the success "
            "\"gave Mary Pickford incredible bargaining power\"; by 1916 she "
            "had \"a $10,000 a week salary, 50% of her film profits, and her "
            "own production company.\" The chronology is kept rather than "
            "resolved: her foundation dates the renegotiation to May 1916, "
            "another account dates a contract at 24 June 1916 with a "
            "guarantee of $1.04 million. Both are here, because a date and a "
            "number that disagree are the ordinary state of a contract "
            "nobody was meant to read. United Artists followed in February "
            "1919, with Fairbanks, Chaplin, Griffith and Hart.",

            "The other side of it is why this is not a portrait. When the "
            "company she co-founded had its way, it would \"pressure "
            "Pickford to limit herself artistically, playing roles she knew "
            "her fans would love.\" **Nobody voted and the studio obeyed "
            "anyway.** That is the shape of the whole period: an audience "
            "made sovereign and unaware of it, consulted through a contract "
            "clause rather than through a question. By 1927 the highs were "
            "over, and what the constraint had been buying was visible from "
            "the outside.",
        ],
        ["film"],
        [{"to": "charlie-chaplin", "type": "contemporary"},
         {"to": "rudolph-valentino", "type": "preceded"}],
        [
            src("Women Film Pioneers Project, Columbia University, \"Mary "
                "Pickford\"",
                "https://wfpp.columbia.edu/pioneer/ccp-mary-pickford/",
                "The cover, the sensation and the bargaining power, which is "
                "the entry's whole argument in one paragraph. \"In 1911, "
                "'Moving Picture Mary' was the first movie star to adorn the "
                "cover of the New York Dramatic Mirror, an honor previously "
                "bestowed only on theatrical stars.\"; of the 1914 Tess of "
                "the Storm Country, that it \"caused a sensation ... created "
                "fan worship that had never before been witnessed. In turn, "
                "this success gave Mary Pickford incredible bargaining "
                "power. In 1916, Pickford had negotiated a contract that gave "
                "her a $10,000 a week salary, 50% of her film profits, and "
                "her own production company.\""),
            src("PBS American Experience, \"Mary Pickford: 1892-1979\"",
                "https://www.pbs.org/wgbh/americanexperience/features/pickford-1892-1979/",
                "The scale sentence the title takes, the names the audience "
                "used, and the constraint on the other side of it. St. John: "
                "\"known to more people and loved by more people than any "
                "other woman that has been in all history.\"; \"America's "
                "Sweetheart\"; \"our Mary\"; that the highs ran \"until "
                "1927\"; and that United Artists would \"pressure Pickford to "
                "limit herself artistically, playing roles she knew her fans "
                "would love.\""),
            src("The Mary Pickford Foundation, \"Mary Pickford Chronology\"",
                "https://marypickford.org/mary-pickford-chronology/",
                "The dates that disagree with the WFPP paragraph, recorded "
                "rather than settled. That in May 1916 she renegotiated for "
                "$10,000 a week and the choosing of her own roles; a letter "
                "of intention dated 15 January 1919 signed by Pickford, "
                "Fairbanks, Chaplin, Griffith and W. S. Hart; and United "
                "Artists incorporated on 5 February 1919."),
            src("Wikipedia, \"Mary Pickford\"",
                "https://en.wikipedia.org/wiki/Mary_Pickford",
                "The competing contract date and the biographical frame. "
                "That the contract of 24 June 1916 carried a guarantee of "
                "$1.04 million, which is the account that puts the "
                "renegotiation a month after the Foundation does - both are "
                "kept; that she was born Gladys Louise Smith on 8 April 1892 "
                "and died on 29 May 1979; and that she was one of the thirty-"
                "six founders of the Academy of Motion Picture Arts and "
                "Sciences. Corroboration of dates, not the authority for the "
                "fan worship, which is WFPP's and PBS's."),
        ],
    ),

    make(
        "charlie-chaplin",
        "A doodle of you used as your address",
        "person", 1914, "Silent era",
        ["application", "manipulation"], ["idol", "contest"],
        "By 1917 nine out of ten men at a costume ball came as him, a hold-up "
        "man in Cincinnati borrowed his costume as a disguise, and in 1916 "
        "somebody was paging him in more than eight hundred hotels at the "
        "same moment. Later, fans sent letters with a doodle of his face "
        "where the address should have been. The likeness had stopped being a "
        "picture and started being an instruction.",
        [
            "**The silhouette was usable.** That is the entry. The Tramp "
            "first appears in Kid Auto Races at Venice, filmed on 11 January "
            "1914 and released on 7 February; by 1917 the costume was common "
            "enough to be a costume of record - \"most of the girls came as "
            "Annette Kellerman, the swimming star, and nine out of ten men "
            "came as Charlie Chaplin.\" In February 1917 the same costume "
            "was used as a disguise by a hold-up man in Cincinnati. A "
            "likeness that exists only on a screen cannot be worn by a "
            "robber. This one could, and that is the difference between being "
            "famous and being an instruction.",

            "The same period that produced the robbers produced the "
            "diagnosis. About 12 November 1916 the Boston Society for "
            "Psychical Research was investigating \"certain phenomena "
            "connected with the simultaneous paging of Mr Charles Chaplin, "
            "motion picture comedian, in more than 800 large hotels of the "
            "United States\" - one man being asked for in eight hundred "
            "hotels at once, from the Atlantic to the Pacific and the "
            "Canadian boundary to the Gulf - and the Kansas City Star asked "
            "the next day whether readers had had \"the Chaplin-itis?\" "
            "Robinson's account of the period has theatres \"promoting the "
            "Chaplin vogue by sponsoring amateur Charlie look-alike "
            "contests\"; Chaplin himself said he was \"tempted to give "
            "lessons in the Chaplin walk.\"",

            "The contest story is told two ways and both are here. The "
            "Chaplin archive's own press clippings from 1918 record Mary "
            "Pickford telling a dinner in London that he had entered a "
            "Chaplin walk contest at a fair in the United States and came in "
            "twentieth; the version everybody repeats has him coming in "
            "third, which Snopes rates Unproven and traces to a magazine "
            "post from December 2022. **The famous version is the one that "
            "needed no source, and the documented one is second-hand from a "
            "friend.** Neither number changes what the contests were for: an "
            "audience competing to be the nearest copy of a man who was not "
            "there to judge it.",

            "The mail is where the likeness becomes infrastructure. In a 1932 "
            "feature on \"Hollywood's Funny Fan Mail\", Clara Bow was "
            "receiving about 35,000 letters a month; Maurice Chevalier's "
            "arrived with no address whatever, just his picture on the "
            "envelope; Clark Gable's were addressed to \"Valentino the "
            "Second\". **An address that works without a street is a "
            "likeness doing a job**, and by the 1950s a doodle of Chaplin's "
            "face was being used as the address on letters sent to him at the "
            "Savoy Hotel. This entry does not claim what became of that post; "
            "the point is only that it was thought to be enough to send.",
        ],
        ["film"],
        [{"to": "mary-pickford", "type": "contemporary"},
         {"to": "fan-mail", "type": "depicts"}],
        [
            src("CharlieChaplin.com, \"Did Charlie Chaplin Once Lose His Own "
                "Lookalike Contest?\"",
                "https://www.charliechaplin.com/en/articles/334-Did-Charlie-Chaplin-Once-Lose-His-Own-Lookalike-Contest-?category=biography",
                "The strongest record in the entry, and it carries the "
                "quotations. Robinson (2001, pp. 223-224, first published "
                "1985) quoted in full: that \"Costume balls were in great "
                "vogue in 1917 ... most of the girls came as Annette "
                "Kellerman, the swimming star, and nine out of ten men came "
                "as Charlie Chaplin\"; that \"In February 1917 Charlie "
                "Chaplin costume was used as a disguise by a hold-up man in "
                "Cincinnati\"; that \"About the same time the Boston Society "
                "for Psychical Research was investigating 'certain phenomena "
                "connected with the simultaneous paging of Mr Charles "
                "Chaplin, motion picture comedian, in more than 800 large "
                "hotels of the United States'\", observed on 12 November "
                "1916; and the Article's reading that Chaplin was "
                "\"tempted to give lessons in the Chaplin walk\". Also the "
                "1918 press clippings in which Mary Pickford told Lord "
                "Desborough, who repeated it to the press, that Chaplin had "
                "entered a Chaplin walk contest at a fair in the US and came "
                "in 20th."),
            src("CharlieChaplin.com, \"Kid Auto Races at Venice\"",
                "https://www.charliechaplin.com/en/films/47-Kid-Auto-Races-at-Venice",
                "The entry's year, and the moment the likeness began. That "
                "the Tramp was first filmed on Sunday 11 January 1914 and "
                "released on 7 February 1914; and that Mabel's Strange "
                "Predicament, in which the character also appears, was "
                "released on 9 February 1914."),
            src("Snopes, check of the Charlie Chaplin look-alike contest "
                "anecdote (rated Unproven)",
                "https://www.snopes.com/fact-check/charlie-chaplin-look-alike-contest/",
                "The version the entry does not stand behind, and the reason "
                "it is recorded rather than repeated. That the check rates "
                "the story Unproven; that its tracing puts the modern form of "
                "the anecdote in a Far Out Magazine post of December 2022; "
                "and that the supporting history it assembles includes Joyce "
                "Milton's Tramp, which has theatres \"promoting the Chaplin "
                "vogue by sponsoring amateur Charlie look-alike contests.\""),
            src("The Evening Star, \"Hollywood's Funny Fan Mail\", 25 "
                "December 1932, page 44",
                "https://www.historyworm.com/gazete/evening_star/1932-12-25/44",
                "The comparison that shows the phenomenon was not his alone, "
                "and the two details the entry's last paragraph turns on. "
                "That Clara Bow received about 35,000 letters a month; that "
                "Maurice Chevalier's mail carried no address whatever, just "
                "his picture on the envelope; and that Clark Gable's was "
                "addressed to \"Valentino the Second\"."),
            src("Scoop (Upworthy), on the letters fans sent Chaplin in the "
                "1950s",
                "https://scoop.upworthy.com/fans-sent-charlie-chaplin-letters-in-1950-with-address-as-his-doodles",
                "This is the weakest record in the entry - a syndicated "
                "human-interest piece rather than a documentary source - so "
                "it is flagged rather than leaned on, and nothing in the "
                "entry rests on it. That \"Imagine being so famous that a "
                "doodle of you could be used as your address.\"; that the "
                "letters were sent in the 1950s to him at the Savoy Hotel; "
                "and what the entry does *not* take from it, which is any "
                "claim about what happened to the post."),
        ],
    ),

    make(
        "war-of-the-worlds",
        "Nine to twelve million heard it",
        "event", 1938, "Broadcast",
        ["consideration"], ["world", "character"],
        "Orson Welles presented a novel as a news bulletin on 30 October "
        "1938, and CBS identified it as a dramatic performance four times "
        "during the hour. An estimated nine to twelve million Americans "
        "heard it, and at least a million of them were scared into some sort "
        "of action. By the next morning the newspapers had a story about the "
        "listeners, which is the one that has been retold ever since.",
        [
            "The technique is on the record because Welles explained it "
            "himself: \"The Mercury Theatre's own radio version of dressing "
            "up in a sheet and jumping out of a bush and saying Boo!\" The "
            "hour was built to be believed - a performance interrupted by "
            "periodic news bulletins, Martians landing in a town listeners "
            "could drive to - and CBS made four announcements during the "
            "broadcast identifying it as a dramatic performance. **A "
            "listener who came in after the opening could not be given the "
            "sentence that would have told them**, and the arrangements of "
            "the evening were such that a great many did.",

            "The apparatus of belief is documented at the National "
            "Archives. Four announcements, and still: more than two thousand "
            "calls reached the New York police headquarters within a "
            "fifteen-minute span; the New York Times switchboard counted 875 "
            "calls; more than six hundred people contacted the newly formed "
            "Federal Communications Commission, one of them hoping it would "
            "\"lawfully prevent such broadcasts in the future and, if "
            "possible, severely discipline all participants\"; a man in "
            "Meadville wired that the programme was \"not only in bad taste "
            "but dangerous\" and that his wife and several other women were "
            "\"confined to beds from shock and hysteria\"; the city manager "
            "of Trenton reported that it had \"completely crippled "
            "communication facilities of our Police Department for about "
            "three hours.\" The headlines did the rest: \"Mars Invasion in "
            "Radio Skit Terrifies U.S.\", \"Radio Fake Scares Nation\".",

            "And then the argument. The nine-to-twelve million in the title "
            "is the Archives' own estimate and it is kept as an estimate: "
            "later figures for the audience are roughly half of it, a "
            "ratings service put only two percent of national respondents "
            "on the programme that night, and CBS's Frank Stanton concluded "
            "that most Americans had not heard it and that those who did "
            "\"looked at it as a prank and accepted it that way.\" Students "
            "of the episode argue that Cantril's 1940 study - the source of "
            "the canonical panic numbers - put the audience at more than "
            "twice the estimate of any other survey of that night, and that "
            "treating a listener who was frightened, disturbed or excited as "
            "one who was panicked is a categorical error rather than a "
            "measurement. Meanwhile no hospital record ties an admission to "
            "the broadcast, no suicide is conclusively attributed to it, and "
            "a fifty-thousand-dollar suit over it was dismissed.",

            "**Both halves are kept, and neither is the story the industry "
            "tells.** The calls are documented and so is the national panic "
            "built on top of them. What the hour actually establishes is "
            "narrower and harder to argue with: some listeners believed it "
            "briefly, the FCC investigated and found no law broken, and in "
            "the aftermath the Mercury Theatre had corporate sponsorship "
            "from the Campbell Soup Company. The entry treats the episode as "
            "the moment a question about a medium's effect on an audience "
            "became a research programme, a regulatory problem and an "
            "industry talking point in the same week - which is why it "
            "belongs with the arguments rather than with the entertainments.",
        ],
        ["radio"],
        [{"to": "radio-serials", "type": "succeeded"},
         {"to": "the-shadow", "type": "succeeded"},
         {"to": "superman-comic", "type": "contemporary"}],
        [
            src("National Archives, \"'Jitterbugs' and 'Crack-pots': "
                "Responses in 1938 to 'War of the Worlds'\"",
                "https://www.archives.gov/publications/prologue/2003/fall/war-of-worlds.html",
                "The entry's title and its spine, from the government's own "
                "record of the response. That on October 30, 1938 the "
                "Mercury Theatre on the Air, led by twenty-three-year-old "
                "Orson Welles, presented the adaptation on CBS; Welles' own "
                "closing description, \"The Mercury Theatre's own radio "
                "version of dressing up in a sheet and jumping out of a bush "
                "and saying Boo!\"; \"But although CBS made four "
                "announcements during the broadcast identifying it as a "
                "dramatic performance, at least one million of the estimated "
                "nine to twelve million Americans who heard it were deeply "
                "scared by that 'Boo'-scared into some sort of action.\" "
                "Also the response records the entry's second paragraph "
                "quotes - the two thousand calls to New York police "
                "headquarters in a fifteen-minute span, the 875 calls to the "
                "New York Times switchboard, the six hundred to the FCC, the "
                "Chicago complaint that it hoped the Commission would "
                "\"lawfully prevent such broadcasts in the future and, if "
                "possible, severely discipline all participants\", the "
                "Meadville telegram, the Trenton letter, and the headlines "
                "\"Mars Invasion in Radio Skit Terrifies U.S.\" and \"Radio "
                "Fake Scares Nation\" - with letters and telegrams cited to "
                "Record Group 173, Records of the Federal Communications "
                "Commission, at the National Archives at College Park. These "
                "figures were read through the search index rather than "
                "opened in the article, and the title sentence above was "
                "confirmed against the article's own text."),
            src("Wikipedia, \"The War of the Worlds (1938 radio drama)\"",
                "https://en.wikipedia.org/wiki/The_War_of_the_Worlds_(1938_radio_drama)",
                "The audience figures that disagree with the Archives', kept "
                "beside them. That the usual figures are six million who "
                "heard the broadcast, 1.7 million who believed it and 1.2 "
                "million who were frightened; and Pooley and Socolow's "
                "conclusion that \"Cantril's study had serious flaws. Its "
                "estimate of the program's audience is more than twice as "
                "high as any other at the time.\""),
            src("Snopes, check of the War of the Worlds panic story",
                "https://www.snopes.com/fact-check/war-of-the-worlds/",
                "The half of the record that deflates the myth, with its "
                "documents. That WABC's statement an hour after the "
                "broadcast repeated the fact \"which was made clear four "
                "times on the program\"; that the C.E. Hooper ratings "
                "service reported only two percent of national respondents "
                "tuned in; Stanton's conclusion that most Americans did not "
                "hear it and that those who did \"looked at it as a prank "
                "and accepted it that way\"; that hospitals contacted "
                "recorded no admissions on account of the broadcast; that no "
                "suicide is conclusively attributed to it; and that a "
                "$50,000 suit over the programme was dismissed."),
            src("Slate, October 2013, on the War of the Worlds panic myth",
                "https://slate.com/culture/2013/10/orson-welles-war-of-the-worlds-panic-myth-the-infamous-radio-broadcast-did-not-cause-a-nationwide-hysteria.html",
                "The distinction the entry's third paragraph leans on, stated "
                "as a methodological objection rather than as scepticism. "
                "That \"Cantril committed an obvious categorical error by "
                "conflating being 'frightened,' 'disturbed,' or 'excited' by "
                "the program with being 'panicked.'\""),
            src("BBC Culture (2023), Orson Welles on the War of the Worlds "
                "broadcast",
                "https://www.bbc.com/culture/article/20231027-behind-the-broadcast-orson-welles-on-the-mass-hysteria-of-the-war-of-the-worlds",
                "Welles' own account of the evening and the official "
                "aftermath. \"I had no idea that I had suddenly become some "
                "sort of national event.\"; that at 8pm Eastern Time the "
                "broadcast began with Welles introducing the drama and "
                "clarifying that it was fiction, and that listeners who "
                "tuned in late missed the disclaimer; that police arrived at "
                "the CBS studio during the performance; that there were "
                "threats of lawsuits and calls for censorship; and that the "
                "FCC investigated and found no law had been broken, though "
                "networks agreed to be more cautious with future "
                "programming."),
        ],
    ),

    make(
        "fireside-chats",
        "As if he had joined them in their living rooms",
        "mechanism", 1933, "Broadcast",
        ["application"], ["world", "idol"],
        "Franklin Roosevelt talked to the radio as if the listener were "
        "already in the room, and he did it often enough between March 1933 "
        "and June 1944 that the habit became a form - one he did not name. "
        "There is no solid definition of what counted as a chat; the "
        "estimates run from twenty-seven to thirty-one. The count does not "
        "matter. The sitting next to a fireplace does.",
        [
            "**The informality was written into the text, which is the thing "
            "to keep.** Roosevelt did not happen to sound relaxed; the "
            "speeches were built so that he would. The Library of Congress's "
            "account of the recordings puts it plainly: \"their informality "
            "of wording and phrase was built into the text\", and \"The "
            "President appeared to talk with his listeners rather than "
            "lecturing at them.\" The first talk, on 12 March 1933, was "
            "delivered from the Diplomatic Reception Room with the President "
            "actually sitting next to a fireplace. The room is the argument: "
            "he is somewhere specific, you are somewhere specific, and the "
            "distance between them is being described rather than hidden.",

            "The name came later and from somebody else. The Library of "
            "Congress credits Washington broadcast executive Harry Butcher "
            "with it \"on the occasion of the second one\"; the Roosevelt "
            "library says the term \"was not coined by FDR\" but by a "
            "reporter describing the speech of 7 May 1933. Both are kept, "
            "because both are compatible and because neither makes it his. "
            "**The form is famous under a name its author did not choose**, "
            "which is the correct outcome for a form built out of other "
            "people's living rooms.",

            "The count is honestly open and says so: \"There was no solid "
            "definition as to what constituted a Fireside Chat. As a result, "
            "there is some dispute as to the total number of Fireside Chats "
            "that FDR delivered.\" The Library of Congress has the range at "
            "between twenty-seven and thirty-one, the last in June 1944. "
            "**A form people recognise before a committee defines it is a "
            "form, and a form with a number attached is a list.** The "
            "dispute is not a defect in the record; it is the record of "
            "something that was defined by being listened to.",

            "What it was for is in the mechanics. All the national radio "
            "networks carried them - hundreds of stations nationwide - "
            "opening with \"my friends\" and, the first time, with \"I want "
            "to talk for a few minutes with the people of the United States "
            "about banking...\". That sentence assumes you are already "
            "there and already listening; \"my friends\" is not a form of "
            "address but a claim about the relationship, made by an office "
            "that held the whole schedule. The first talk \"was credited "
            "with averting widespread panic.\" **Nobody in the audience "
            "could answer, and that is not a flaw in the design.** It is "
            "the design, applied on purpose, by a government that had "
            "decided the thing to do next was to be in the room with "
            "you.",
        ],
        ["radio"],
        [{"to": "radio-serials", "type": "succeeded"},
         {"to": "soap-opera", "type": "contemporary"},
         {"to": "war-of-the-worlds", "type": "preceded"},
         {"to": "parasocial-interaction", "type": "instance_of"}],
        [
            src("Christopher H. Sterling, essay on the fireside chats, "
                "National Recording Preservation Board, Library of Congress "
                "(PDF)",
                "https://www.loc.gov/static/programs/national-recording-preservation-board/documents/FiresideChats.pdf",
                "The naming, the first talk, and the three quotations the "
                "entry is built on. That \"These 'Fireside Chats' (so named "
                "by Washington broadcast executive Harry Butcher on the "
                "occasion of the second one) were planned as conversations "
                "rather than stiff public speeches.\"; that they were "
                "carried by all the national radio networks, meaning "
                "hundreds of stations nationwide; that \"most agree that "
                "between 27 and 31 were broadcast by the time of the last "
                "one in June, 1944\"; that the first chat was delivered on "
                "March 12, 1933 from the Diplomatic Reception Room \"with "
                "the President actually sitting next to a fireplace\"; that "
                "\"The talk was credited with averting widespread panic.\"; "
                "that \"their informality of wording and phrase was built "
                "into the text\"; and that \"The President appeared to talk "
                "with his listeners rather than lecturing at them.\" Also "
                "the opening of the first talk, \"I want to talk for a few "
                "minutes with the people of the United States about "
                "banking...\", and the customary opening, \"my friends\"."),
            src("Franklin D. Roosevelt Presidential Library and Museum, "
                "\"Franklin D. Roosevelt's Presidency\"",
                "https://www.fdrlibrary.org/fdr-presidency",
                "The purpose in the President's own terms, the attribution "
                "of the name, and the honest gap in the count. \"He "
                "considered it most effective to talk to the people as if he "
                "had joined them in their living rooms or kitchens for a "
                "relaxed, informal conversation about one or two specific "
                "topics.\"; \"The term 'Fireside Chat' was not coined by "
                "FDR, but rather was used by a reporter to describe FDR's "
                "speech of May 7, 1933.\"; and \"There was no solid "
                "definition as to what constituted a Fireside Chat. As a "
                "result, there is some dispute as to the total number of "
                "Fireside Chats that FDR delivered.\" The library's "
                "attribution to \"a reporter\" and the Library of Congress's "
                "to Harry Butcher are compatible and both are kept."),
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
