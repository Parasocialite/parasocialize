#!/usr/bin/env python3
"""
apply_review.py - the result of looking at all 66 pictures.

The resolver's must-terms turned out to be necessary and nowhere near
sufficient. Reviewing them by eye, roughly a third are wrong, and they are
wrong in a specific way: the keyword appears somewhere in a long Commons
filename while the photograph is about something else entirely. A map of
Belarus came back for a story about Patreon memberships. An octopus plush
came back for a streamer whose best friend was robbed. A line graph of
Instagram use came back for a story about a parasocial relationship with an
Instagram personality. None of these fail the must-term test, which is exactly
the point: a keyword test cannot tell you what is in the frame.

So this file is the review, one line per image, with what is actually in it.
`keep: false` clears the file and the story falls back to its section
photograph, which is also a real photograph of the subject matter. A gap is
better than a wrong picture, and it is better still than a caption that lies
about what a reader is looking at.

  python tools/apply_review.py          # show the tally
  python tools/apply_review.py --apply  # write it
"""
import json, pathlib, sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
MAN = ROOT / "data" / "images.json"

# slug -> (keep, what is actually in the frame / why rejected)
R = {
 # ---- good: the person, the place, the thing itself
 "celebrity-death-feels-like-loss": (1, "Flowers and vigil candles outside the "
    "Embassy of the Netherlands in Tallinn"),
 "youtubetv-living-room": (1, "A person watching an analogue television set"),
 "vid-summit-bars-fans": (1, "Danny Philippou and Luke Kidgell at VidCon Australia 2017"),
 "dolly-parton-lowest-point": (1, "Dolly Parton, 1984"),
 "gloria-steinem-and-dolly": (1, "Gloria Steinem, 2019"),
 "aoc-and-parasocial-politics": (1, "Official portrait, 116th Congress"),
 "fearne-cotton-free-tv": (1, "Fearne Cotton, 2014"),
 "taylor-swift-red-knows-it": (1, "Taylor Swift at the 2019 American Music Awards"),
 "pygmalion-sculptor-illusion": (1, "Janette Steer as Galatea in Pygmalion and Galatea, "
    "as wax. The sculptor whose assistant caught fire is the historical case the "
    "myth was built from."),
 "sculptor-fell-in-love": (1, "A marble sculpture. Not Pygmalion, and captioned as "
    "such - the lane's own image carries the Pygmalion case."),
 "hugh-jackman-divorce": (1, "Hugh Jackman"),
 "podcast-listeners-study": (1, "A podcast host at a microphone"),
 "liam-payne-generation": (1, "Liam Payne, 2019"),
 "zubeen-garg-public-grief": (1, "Zubeen Garg at Edufest 2016"),
 "characters-we-keep": (1, "The reading room of the University of Graz library"),
 "t8-1-rugrats-nest": (1, "A Reptar toy. The NEST letter is about wanting proof that "
    "a toy shop is real, so a photograph of the toy is closer to the episode than a "
    "screenshot would have been."),
 "t8-3-grouch": (1, "A cosplayer as Oscar the Grouch, Hallowbaloo 2012. Fans in "
    "costume is what Commons actually holds, and on this site that is the better "
    "picture: the bond lives in the audience."),
 "t8-4-zuko": (1, "Cosplay of Zuko at AVA Expo 2013"),
 "t8-6-powerrangers": (1, "The cast of the Power Rangers film"),
 "t8-8-animaniacs": (1, "The Animaniacs at WonderCon, 2012"),
 "history-fan-letters": (1, "A typed letter, 1942. The reply is the whole point of "
    "the entry and the letter is the evidence."),
 "figure-peewee": (1, "Paul Reubens, with the David Hasselhoff Chalk painting, CalArts"),
 "figure-kozik": (1, "Charlie Kaufman, Fantastic Fest 2015"),
 "figure-tay": (1, "Taylor Swift, 2019"),
 "top8-cartoons-90s": (1, "A woman standing beside a television set"),
 "character-ai-settlement": (1, "The Austrian Constitutional Court. A real courtroom, "
    "standing in for a litigation that did not happen there - captioned as a "
    "courtroom and not as the hearing."),
 "aisle-world": (1, "A stadium. The oldest version of the thing."),
 "aisle-crossover": (1, "A Victorian schoolroom, Blists Hill"),
 "aisle-grief": (1, "A face in low light"),
 "aisle-danger": (1, "A mounted police officer"),

 # ---- keep, but the caption has to say what it really is
 "youtube-shorts-episodic": (1, "The YouTube Shorts upload player. A screenshot of "
    "the actual mechanism the story is about."),
 "companion-safety-controls": (1, "A mobile phone showing a message. Generic, and "
    "captioned as exactly that."),
 "idol-economy-four-dollars": (1, "A concert ticket. The unit of account in the entry."),
 "platforms-renting-reach": (0, "REJECT. The caption was 'Billboard-Krakow-Prokocim', "
    "which is a street name, not a billboard. The picture is electricity pylons. The "
    "must-term matched a toponym."),
 "swifties-power-record-sales": (0, "REJECT. A shopfront with a street billboard in "
    "the background, captioned as if the billboard were the subject."),
 "neuro-sama-tops-twitch": (0, "REJECT. A drawing tablet showing an artist's "
    "work-in-progress of a VTuber. It is a photograph of somebody drawing, which is "
    "not the story."),
 "worship-in-sports-politics-business": (0, "REJECT. A man bathing in the Ganges at "
    "the Kumbh Mela. Religious ritual, but nothing to do with the worship of idols in "
    "sport, politics and commerce, which is what the entry is about."),
 "sasaeng-jungkook-conviction": (0, "REJECT. A photograph of an exhibition "
    "installation, not of Jungkook. Using it on a story about a stalking conviction "
    "would lean on a person's fame to carry an allegation the picture does not show."),
 "t8-2-rugrats-gun": (0, "REJECT. A parade float. The must-term 'rugrats' appears in "
    "the filename but the photograph is a street procession."),

 # ---- wrong: keyword present, photograph unrelated
 "madeonyoutube-spending-on-scoreboard": (0, "REJECT. A software bug-report form "
    "asking for a maximum date. Nothing to do with YouTube or with spending; the word "
    "appeared in a German filename about a YouTube poll."),
 "youtube-patreon-membership-spaces": (0, "REJECT. A political map of Belarus with one "
    "region highlighted. The single worst result in the set and it passed the "
    "must-term test."),
 "grief-experts-three-of-them": (0, "REJECT. The flag-draped coffin of John Lewis. A "
    "specific real funeral, captioned as though it were three grief experts."),
 "house-of-the-dragon-backlash": (0, "REJECT. Three people at a Game of Thrones event. "
    "House of the Dragon is HBO property with no freely-licensed still, and using a "
    "GoT photograph implies it is the same show."),
 "yourrage-best-friend-stole": (0, "REJECT. An octopus plush toy."),
 "instagram-dominatrix": (0, "REJECT. A line graph of monthly Instagram users, "
    "2015-2019. It is a chart, which the filter is supposed to exclude."),
 "neighbours-kids-and-finale": (0, "REJECT. A D&D-style 'deep discussion for roles and "
    "characters' worksheet. The word 'neighbours' appears somewhere in the filename."),
 "research-shelf": (0, "REJECT. A hand-drawn diagram of a table with arrows."),
 "eu-kids-act-companion-chatbots": (0, "REJECT. The same file as i-tried-replika - a "
    "chatbot avatar render. A duplicate, and a weak picture for either story."),

 # ---- second pass over the images I saw but had not written a line for
 "i-tried-replika": (1, "A chatbot avatar. A render rather than a photograph, and "
    "captioned as a render."),
 "replika-users-lost-them": (1, "A screenshot of a conversation with a chatbot. The "
    "thing the entry is about, shown rather than described."),
 "agei-imaginary-friends": (1, "A child playing alone on a beach"),
 "peak-parasocial-vogue": (1, "A fashion show in Japan, 1953"),
 "ai-updates-feel-like-breakups": (1, "A broken laptop. Literally a broken thing, "
    "which the entry is about."),
 "darry-season-two": (1, "A giant puppet show"),
 "parasocial-problem-visibility": (1, "A forum thread. The entry is about a glimpse "
    "being mistaken for access, which is what a forum thread is."),
 "moment-power-rangers": (1, "The cast of the Power Rangers film"),
 "aisle-idol": (1, "A crowd watching a band perform"),
 "aisle-creator": (1, "A speaker addressing a room at a conference"),
 "aisle-brand": (1, "A shop window. A shop, which is also a version."),
 "aisle-character": (1, "A woman adjusting a vintage television set. Re-fetched: the "
    "first was a photograph of Saturn and the second a film-festival award badge."),
 "aisle-companion": (1, "A hand holding a smartphone, lit by its own screen. "
    "Re-fetched twice - the first attempt came back as a map of Belarus and the "
    "second as a cropped chatbot reply."),

 "oshi-katsu-half-century": (0, "REJECT. A line chart. The filter is supposed to "
    "exclude charts and this one got through; it is also useless as an illustration "
    "of a behavioural word coined in 2024."),
 "customer-obsession-model": (0, "REJECT. A performer in costume in a busy street. "
    "Nothing in the frame connects to customer obsession, and 'customer' matched a "
    "filename rather than the picture."),
 "meg-mason-writes-about-us": (0, "REJECT. A figure in a red costume. The query was "
    "for a typewriter; this is not one."),
 "kai-cenat-returns": (0, "REJECT. A Hungarian Twitch partner meeting. The story is "
    "about one named streamer ending nine months of silence, and borrowing a "
    "photograph of unrelated people to stand in for him is the substitution this "
    "file exists to prevent."),
 "aisle-character": (1, "A woman adjusting a vintage television set. Third attempt: "
    "the first was a photograph of Saturn captioned as 'a screen, and the person "
    "watching it', the second a film-festival award badge. Both passed the must-term "
    "test. The caption had been written before the picture was chosen, which is the "
    "failure this review exists to catch."),
 "aisle-contest": (1, "A climate protest in Washington DC, 2015. Re-fetched: the "
    "previous one was a pilgrimage site in the Philippines captioned as a public "
    "argument, which is the same class of error in the other direction."),
}


def main():
    man = json.loads(MAN.read_text(encoding="utf-8"))
    by = {i["slug"]: i for i in man["items"]}
    keep = sum(1 for v in R.values() if v[0])
    drop = len(R) - keep
    unknown = [s for s in R if s not in by]
    print(f"{len(R)} reviewed: {keep} keep, {drop} reject")
    print(f"{len(by) - len(R)} not in the review (untouched)")
    if unknown:
        print("review names a slug the manifest does not have: "
              + ", ".join(unknown))
    if "--apply" not in sys.argv:
        print("\nnothing written. re-run with --apply")
        return
    n = 0
    for slug, (ok, note) in R.items():
        it = by.get(slug)
        if not it:
            continue
        if not ok:
            for k in ("local", "src", "cached"):
                it.pop(k, None)
            it["caption"] = note.split("REJECT. ")[-1][:70]
            n += 1
        else:
            it["caption"] = note
    MAN.write_text(json.dumps(man, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"\napplied: {n} images withdrawn, {keep} kept with a true caption")


if __name__ == "__main__":
    main()
