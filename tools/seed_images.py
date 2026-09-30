#!/usr/bin/env python3
"""
seed_images.py - the query set.

One hand-picked query per story, with the terms that MUST appear in the file's
own title. A candidate that misses any of them is not a worse choice, it is the
wrong picture, so it is dropped rather than ranked. `None` for a story that
genuinely has no freely-licensed photograph is a real answer and is recorded as
one, so the build can fall back deliberately instead of quietly reusing a
mismatched picture.

  python tools/seed_images.py          # rewrite data/images.json
  python tools/images.py --fetch-all  # resolve
  python tools/images.py --list       # what each one actually became
"""
import json, pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
MAN = ROOT / "data" / "images.json"

# slug -> (query, must-terms, caption, allow_logo)
# caption = what is IN THE FRAME. not what the story is about.
STORIES = {
 "celebrity-death-feels-like-loss": ("candle vigil memorial", ["vigil"],
    "A candlelit vigil", False),
 "youve-got-that-one": ("autograph signed photograph", ["autograph"],
    "A signed photograph", False),
 "madeonyoutube-spending-on-scoreboard": ("YouTube", ["youtube"],
    "The YouTube wordmark", True),
 "youtubetv-living-room": ("television living room", ["television"],
    "A television in a living room", False),
 "vid-summit-bars-fans": ("VidCon", ["vidcon"],
    "VidCon", False),
 "youtube-patreon-membership-spaces": ("Patreon", ["patreon"],
    "The Patreon wordmark", True),
 "youtube-shorts-episodic": ("YouTube Shorts", ["youtube", "short"],
    "The YouTube Shorts wordmark", True),
 "dolly-parton-lowest-point": ("Dolly Parton", ["parton"],
    "Dolly Parton", False),
 "gloria-steinem-and-dolly": ("Gloria Steinem", ["steinem"],
    "Gloria Steinem", False),
 "aoc-and-parasocial-politics": ("Alexandria Ocasio-Cortez", ["ocasio"],
    "Alexandria Ocasio-Cortez", False),
 "fearne-cotton-free-tv": ("Fearne Cotton", ["fearne", "cotton"],
    "Fearne Cotton", False),
 # "eliza" alone matched "ELIZA ARCHARD CONNER Woman of the Century", a
 # nineteenth-century portrait of a woman with that first name. The must-term
 # has to name the thing, not a person who happens to share a given name.
 "eu-kids-act-companion-chatbots": ("chatbot", ["chatbot"],
    "A chatbot", False),
 "taylor-swift-red-knows-it": ("Taylor Swift", ["swift"],
    "Taylor Swift", False),
 "house-of-the-dragon-backlash": ("Game of Thrones", ["thrones"],
    "Game of Thrones. House of the Dragon is HBO and has no freely-licensed still.",
    False),
 "grief-experts-three-of-them": ("funeral", ["funeral"],
    "A funeral", False),
 "i-tried-replika": ("chatbot", ["chatbot"],
    "A chatbot", False),
 "oshi-katsu-half-century": ("focus group", ["focus"],
    "A focus group. Oshi-katsu is a word from 2024, this behaviour is from 1974.",
    False),
 "customer-obsession-model": ("customer service", ["customer"],
    "Customer service", False),
 "agei-imaginary-friends": ("child playing", ["child"],
    "A child playing alone", False),
 "peak-parasocial-vogue": ("fashion show", ["fashion"],
    "A fashion show", False),
 "ai-updates-feel-like-breakups": ("laptop computer", ["laptop"],
    "A laptop", False),
 "yourrage-best-friend-stole": ("livestream streaming", ["stream"],
    "Livestreaming", False),
 "instagram-dominatrix": ("Instagram", ["instagram"],
    "The Instagram wordmark", True),
 "replika-users-lost-them": ("chatbot conversation computer", ["chatbot"],
    "A chatbot conversation", False),
 "companion-safety-controls": ("mobile phone", ["phone"],
    "A mobile phone", False),
 "pygmalion-sculptor-illusion": ("Pygmalion and Galatea", ["pygmalion"],
    "Pygmalion and Galatea, by Falconet. The story is older than the website.",
    False),
 "sculptor-fell-in-love": ("marble sculpture statue", ["marble", "sculpt"],
    "Marble sculpture", False),
 "hugh-jackman-divorce": ("Hugh Jackman", ["jackman"],
    "Hugh Jackman", False),
 "podcast-listeners-study": ("podcast", ["podcast"],
    "Podcasting", False),
 "neighbours-kids-and-finale": ("Neighbours cast", ["neighbours"],
    "The Neighbours cast at a meet-and-greet", False),
 "liam-payne-generation": ("Liam Payne", ["payne"],
    "Liam Payne", False),
 "neighbours-grief-study": ("soap opera television studio", ["opera"],
    "A soap opera studio", False),
 "zubeen-garg-public-grief": ("Zubeen Garg", ["zubeen"],
    "Zubeen Garg", False),
 "characters-we-keep": ("library reading room", ["library"],
    "A library reading room", False),
 "worship-in-sports-politics-business": ("worship", ["worship"],
    "Worship", False),
 "kpop-uae-grief": ("K-pop concert Seoul", ["k-pop", "seoul"],
    "A K-pop concert", False),
 "platforms-renting-reach": ("billboard advertising", ["billboard"],
    "A billboard", False),
 "swifties-power-record-sales": ("Billboard", ["billboard"],
    "A Billboard chart", False),
 "idol-economy-four-dollars": ("concert ticket", ["ticket"],
    "A concert ticket", False),
 "meg-mason-writes-about-us": ("typewriter manuscript", ["typewriter"],
    "A typewriter", False),
 "darry-season-two": ("puppet", ["puppet"],
    "A puppet", False),
 "parasocial-problem-visibility": ("internet forum discussion", ["forum"],
    "An internet forum", False),
 "kai-cenat-returns": ("Twitch", ["twitch"],
    "The Twitch wordmark", True),
 "sasaeng-jungkook-conviction": ("Jungkook", ["jungkook"],
    "Jungkook", False),
 "character-ai-settlement": ("courtroom judge", ["court"],
    "A courtroom", False),
 "neuro-sama-tops-twitch": ("VTuber", ["vtuber"],
    "A VTuber at a convention", False),
 "research-shelf": ("bookshelf", ["shelf"],
    "A bookshelf", False),
}

# The Saturday-morning eight. Commons holds fans in costume, a costume shop and
# a toy rather than any actual still, because the actual stills are Nickelodeon
# and HBO property. For this list that is the better picture: the point of the
# site is that the bond lives in the audience, and here the audience is what
# Commons photographed.
TOP8 = {
 "t8-1-rugrats-nest":   ("Rugrats", ["reptar"],
    "A Reptar toy in a shop. The NEST letter is about wanting proof a toy is real.",
    False),
 "t8-2-rugrats-gun":   ("Rugrats", ["rugrats"],
    "Rugrats at Universal Studios, Florida", False),
 "t8-3-grouch":        ("Oscar the Grouch", ["grouch"],
    "Caroll Spinney with Oscar the Grouch, 2014", False),
 "t8-4-zuko":          ("Cosplay Zuko", ["zuko"],
    "Cosplay of Zuko and Toph", False),
 "t8-5-dragontales":   (None, None,
    "No freely-licensed image of Dragon Tales exists.", False),
 "t8-6-powerrangers":  ("Power Rangers", ["rangers"],
    "The cast of the Power Rangers film", False),
 "t8-7-doug":          (None, None,
    "No freely-licensed image of Doug exists.", False),
 "t8-8-animaniacs":    ("Animaniacs", ["animaniacs"],
    "Animaniacs cosplay", False),
}

# the feature pages that already had queries, rewritten with must-terms
FEATURES = {
 "top8-cartoons-90s": ("children watching television", ["television"],
    "Children watching television together", False),
 "history-macy-store": ("soap opera studio set", ["opera"],
    "A soap opera studio, 1940s", False),
 "history-dionne-warwick": ("Dionne Warwick", ["warwick"],
    "Dionne Warwick", False),
 "history-fan-letters": ("Rodgers Hammerstein letter", ["letter"],
    "A letter from the 1940s, the reply is the whole point", False),
 "figure-peewee": ("Paul Reubens", ["reubens"], "Paul Reubens", False),
 "figure-kozik": ("Charlie Kaufman", ["kaufman"], "Charlie Kaufman", False),
 "figure-tay": ("Taylor Swift", ["swift"], "Taylor Swift", False),
 "moment-power-rangers": ("Power Rangers", ["rangers"],
    "The cast of the Power Rangers film", False),
}


def build():
    man = json.loads(MAN.read_text(encoding="utf-8")) if MAN.exists() else {}
    man.setdefault("_note", "")
    man["_note"] = (
        "Editorial images. Wikimedia Commons, cached locally. Each entry carries a "
        "query plus `must` terms that have to appear in the file's own title - a "
        "candidate missing one is the wrong picture, not a worse choice. `caption` "
        "describes what is IN THE FRAME and never what the story is about. "
        "`kind` is exact (the thing itself) or illustrative (the subject matter). "
        "An entry with local:null and no available photograph is a real answer.")
    items, seen = [], set()

    def add(slug, for_, spec, **extra):
        if slug in seen:
            return
        seen.add(slug)
        q, must, caption, logo = spec
        it = {"slug": slug, "for": for_, "caption": caption}
        if q:
            it["q"] = q
        if must:
            it["must"] = must
        if logo:
            it["allow_logo"] = True
        it.update(extra)
        it.update(old.get(slug, {}).get("resolved", {}))
        items.append(it)

    old = {i["slug"]: i for i in (man.get("items") or [])}
    old = {k: {"resolved": {f: v for f, v in v.items()
                            if f in ("local", "src", "cached", "topic")} if v else {}}
           for k, v in old.items()}

    for slug, spec in STORIES.items():
        add(slug, "story", spec)
    for slug, spec in TOP8.items():
        add(slug, "top8", spec)
    for slug, spec in FEATURES.items():
        add(slug, "feature", spec)
    for slug, a in (man.get("sections") or {}).items():
        add("section-" + slug, "section",
            (a.get("topic"), None, a.get("caption"), False), section=slug,
            topic=a.get("topic"))

    man["items"] = items
    MAN.write_text(json.dumps(man, indent=2, ensure_ascii=False), encoding="utf-8")
    n_null = sum(1 for i in items if not i.get("local"))
    print(f"{len(items)} entries written ({len(STORIES)} stories, {len(TOP8)} top-8, "
          f"{len(FEATURES)} features, {len(man.get('sections') or {})} sections), "
          f"{n_null} still to resolve")


if __name__ == "__main__":
    build()
