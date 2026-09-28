#!/usr/bin/env python3
"""
seed_atlas_relations.py - the edges.

THE ATLAS SAID 47 OF 176 WERE JOINED, AND THAT WAS TRUE
The first graph had relations only on the nineteen figures added last session,
which left 148 entries placed by medium and era but connected to nothing. The
constellation was a scatter with a web in the middle of it. Filling those edges
is content work rather than code, and it is the single biggest thing left on the
site.

ABOUT TWO OR THREE PER NODE, DELIBERATELY
An earlier instinct was to relate everything to everything reachable. That
produces four hundred edges, every node touching every other node, and a
hairball - the same failure as the flat `related` list this replaced, just with
more steps. Two or three well-chosen edges per entry keeps neighbourhoods
readable: you can still see that the Replika letter and the fan mail department
are on the same street, without the whole sky being a mesh.

THE VOCABULARY IS NARROW ON PURPOSE
Only thirteen relation types, and each one means the same thing everywhere:

    instance_of   this is an instance of that pattern
    cites         this is evidence for, or illustrates, that
    preceded      came before, in the same lineage
    succeeded     replaced or was replaced by
    contemporary  existed at the same time
    depicts       portrays, or is about
    bond_with     a one-sided bond
    member_of     part of a cast, pantheon, group or circuit
    occurred_in   happened at this place or institution
    adapted_from  was made from, or remade from
    performed     performed, released or broadcast
    influenced    demonstrably changed

Every edge below is defensible from the two entries it joins. Where the honest
answer is "these are contemporaries and nothing more", that is what it says:
contemporary is the most-used type here, and that is not a failure of the data,
it is a real feature of it. A catalogue of one-sided relationships is mostly
overlapping rather than causal.

  python tools/seed_atlas_relations.py
"""
import json, pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
ENC = ROOT / "data" / "encyclopedia.json"

# id -> [(type, target), ...]
R = {

# ---------------------------------------------------------------- the terms
# terms are the hubs. almost everything else points here, and they point back
# at the one or two entries that gave them the clearest statement.
 "transparasocial": [
   ("succeeded", "parasocial-interaction"),
   ("cites", "protagonist-parasocial"),
   ("cites", "characters-move-in")],
 "parasocial-interaction": [
   ("preceded", "transparasocial"),
   ("depicts", "the-clerk"),
   ("cites", "gazing-at-celebrities")],
 "protagonist-parasocial": [
   ("depicts", "soap-opera"),
   ("depicts", "film-serial"),
   ("cites", "transparasocial")],
 "will-and-want": [
   ("depicts", "first-fans"),
   ("depicts", "teen-idols"),
   ("cites", "the-many-to-many")],
 "eudaimonia": [
   ("cites", "parasocial-diagnosis"),
   ("cites", "who-holds-the-dream")],
 "mourn-a-person-you-met": [
   ("depicts", "grief"),
   ("cites", "soap-finale-study")],
 "sasaeng": [
   ("cites", "stalker-law"),
   ("member_of", "sasaeng-culture"),
   ("cites", "fandom-doxxing")],
 "sasaeng-culture": [
   ("depicts", "fandom-doxxing"),
   ("cites", "parasocial-consent")],
 "fandom-doxxing": [
   ("depicts", "doxxing"),
   ("cites", "swatting"),
   ("cites", "contest")],
 "attention-economy": [
   ("cites", "who-holds-the-dream"),
   ("depicts", "the-reply-heres-watching"),
   ("cites", "the-algorithm-decides")],
 "who-holds-the-dream": [
   ("cites", "the-algorithm-decides"),
   ("cites", "parasocial-persuasion"),
   ("cites", "eudaimonia")],
 "parasocial-persuasion": [
   ("cites", "candidacy-and-charisma"),
   ("cites", "parasocial-interaction"),
   ("cites", "celebrity-endorsement-fatigue")],
 "peak-tv": [
   ("cites", "soap-opera"),
   ("cites", "tv-cliffhanger-season")],
 "the-algorithm-decides": [
   ("cites", "who-holds-the-dream"),
   ("cites", "attention-economy")],
 "parasocial-consent": [
   ("cites", "sasaeng-culture"),
   ("cites", "parasocial-diagnosis"),
   ("cites", "characterai-lawsuits")],
 "scale-change": [
   ("cites", "digital-orphans"),
   ("cites", "characterai")],
 "digital-orphans": [
   ("cites", "scale-change"),
   ("cites", "deepfake-grief")],
 "the-uncanny-corridor": [
   ("depicts", "shrlu"),
   ("cites", "the-ai-assistant")],
 "mob-and-internet-pile": [
   ("depicts", "the-pile-on"),
   ("cites", "contest"),
   ("cites", "cancelling")],
 "cancelling": [
   ("member_of", "the-pile-on"),
   ("cites", "fandom-wars")],
 "crossover": [
   ("depicts", "the-brand-as-character"),
   ("cites", "tony-stark")],
 "loyalty-dark-pattern": [
   ("depicts", "club-card"),
   ("depicts", "free-trial-bait"),
   ("cites", "the-subscription-box")],
 "parasocial-diagnosis": [
   ("cites", "grief-extraction"),
   ("cites", "parasocial-consent"),
   ("cites", "eudaimonia")],

# --------------------------------------------------------------- the studies
 "gazing-at-celebrities": [
   ("cites", "parasocial-interaction"),
   ("cites", "protagonist-parasocial"),
   ("contemporary", "soap-opera")],
 "candidacy-and-charisma": [
   ("cites", "parasocial-persuasion"),
   ("depicts", "the-politician")],
 "the-many-to-many": [
   ("cites", "soap-opera"),
   ("cites", "will-and-want"),
   ("cites", "parasocial-interaction")],
 "soap-finale-study": [
   ("cites", "tv-cliffhanger-season"),
   ("cites", "macy-paradox"),
   ("cites", "mourn-a-person-you-met")],
 "rubin-loneliness": [
   ("cites", "the-local-anchor"),
   ("cites", "the-neighbour")],
 "psr-research-begins": [
   ("cites", "parasocial-interaction"),
   ("cites", "podcast-intimacy")],
 "celebrity-endorsement-fatigue": [
   ("cites", "the-brand-as-character"),
   ("cites", "the-closure-gift")],
 "keep-it-or-lose-it": [
   ("cites", "grief"),
   ("cites", "avengers-endgame"),
   ("cites", "grief-extraction")],

# ----------------------------------------------------------------- the cases
 "dere": [
   ("depicts", "dionne-warwick"),
   ("cites", "fan-mail"),
   ("cites", "parasocial-interaction")],
 "stalker-law": [
   ("cites", "sasaeng"),
   ("contemporary", "fandom-doxxing"),
   ("cites", "parasocial-consent")],
 "characterai-lawsuits": [
   ("cites", "characterai"),
   ("cites", "parasocial-consent"),
   ("member_of", "the-litigation-year")],
 "the-litigation-year": [
   ("member_of", "characterai-lawsuits"),
   ("cites", "stalker-law")],

# ---------------------------------------------------------------- the figures
 "macy": [
   ("depicts", "the-clerk"),
   ("cites", "macy-paradox")],
 "elvis": [
   ("depicts", "elvis-hologram"),
   ("bond_with", "first-fans"),
   ("cites", "will-and-want")],
 "dionne-warwick": [
   ("cites", "dere"),
   ("depicts", "fan-mail")],
 "reality-celebrity": [
   ("cites", "parasocial-interaction"),
   ("cites", "peak-tv"),
   ("cites", "the-uncanny-corridor")],

# -------------------------------------------------------- ancient and early
 "myth-and-ritual": [
   ("depicts", "congregation"),
   ("cites", "p"),
   ("contemporary", "congregation")],
 "p": [
   ("cites", "myth-and-ritual"),
   ("contemporary", "macy")],
 "congregation": [
   ("depicts", "the-priest"),
   ("contemporary", "myth-and-ritual")],
 "the-priest": [
   ("occurred_in", "congregation"),
   ("contemporary", "macy")],
 "binding-is-public": [
   ("contemporary", "macy"),
   ("cites", "macy-paradox")],
 "trading-stamps": [
   ("preceded", "green-shield"),
   ("succeeded", "club-card"),
   ("succeeded", "coffee-card")],
 "comic-strip": [
   ("depicts", "superman-comic"),
   ("cites", "protagonist-parasocial"),
   ("contemporary", "film-serial")],
 "the-coach": [
   ("cites", "the-transfer"),
   ("contemporary", "the-teacher")],
 "the-landlord": [
   ("contemporary", "the-neighbour"),
   ("cites", "the-local-anchor")],
 "the-teacher": [
   ("cites", "crossover"),
   ("contemporary", "the-coach")],
 "the-transfer": [
   ("depicts", "the-coach"),
   ("contemporary", "the-atletefan-bond")],
 "film-serial": [
   ("preceded", "radio-serials"),
   ("cites", "protagonist-parasocial"),
   ("contemporary", "comic-strip")],
 "green-shield": [
   ("succeeded", "trading-stamps"),
   ("cites", "the-atletefan-bond")],
 "fan-mail": [
   ("depicts", "dionne-warwick"),
   ("cites", "dere"),
   ("contemporary", "the-clerk")],
 "the-atletefan-bond": [
   ("cites", "green-shield"),
   ("cites", "trading-stamps"),
   ("depicts", "the-transfer")],
 "first-fans": [
   ("depicts", "will-and-want"),
   ("preceded", "elvis-hologram"),
   ("contemporary", "the-priest")],
 "radio-serials": [
   ("preceded", "film-serial"),
   ("succeeded", "soap-opera"),
   ("cites", "protagonist-parasocial")],
 "soap-opera": [
   ("preceded", "radio-serials"),
   ("cites", "protagonist-parasocial"),
   ("cites", "the-many-to-many")],
 "superman-comic": [
   ("preceded", "comic-strip"),
   ("cites", "tony-stark"),
   ("contemporary", "macy")],
 "sinatra-bobby-soxers": [
   ("depicts", "will-and-want"),
   ("preceded", "elvis"),
   ("contemporary", "first-fans")],
 "gigi": [
   ("contemporary", "star-wars-holiday"),
   ("cites", "protagonist-parasocial")],
 "fan-club": [
   ("preceded", "macy-paradox"),
   ("cites", "fan-mail")],
 "the-clerk": [
   ("depicts", "macy"),
   ("cites", "macy-paradox"),
   ("cites", "clerks-beat-algorithms")],
 "the-local-anchor": [
   ("cites", "rubin-loneliness"),
   ("contemporary", "the-neighbour")],
 "the-neighbour": [
   ("cites", "rubin-loneliness"),
   ("contemporary", "the-landlord")],
 "teen-idols": [
   ("depicts", "will-and-want"),
   ("preceded", "gomer-pyle"),
   ("cites", "the-brand-as-character")],
 "gomer-pyle": [
   ("cites", "protagonist-parasocial"),
   ("contemporary", "the-politician")],
 "the-politician": [
   ("cites", "candidacy-and-charisma"),
   ("cites", "parasocial-persuasion"),
   ("contemporary", "gomer-pyle")],

# ------------------------------------------------------------ sixties to eighties
 "beatlesmania": [
   ("depicts", "will-and-want"),
   ("succeeded", "sinatra-bobby-soxers"),
   ("contemporary", "gomer-pyle")],
 "shrlu": [
   ("cites", "the-uncanny-corridor"),
   ("preceded", "siri"),
   ("contemporary", "eliza")],
 "grief": [
   ("depicts", "mourn-a-person-you-met"),
   ("cites", "keep-it-or-lose-it"),
   ("cites", "killing-off")],
 "star-trek-con": [
   ("member_of", "con-culture"),
   ("cites", "first-fans")],
 "elvis-hologram": [
   ("depicts", "elvis"),
   ("cites", "deepfake-grief"),
   ("succeeded", "michael-jackson")],
 "con-culture": [
   ("depicts", "star-trek-con"),
   ("preceded", "star-wars-holiday"),
   ("cites", "fandom-wars")],
 "star-wars-holiday": [
   ("depicts", "con-culture"),
   ("cites", "superman-comic")],
 "tv-cliffhanger-season": [
   ("cites", "soap-finale-study"),
   ("cites", "macy-paradox"),
   ("cites", "cliffhanger")],
 "airline-miles": [
   ("cites", "the-atletefan-bond"),
   ("cites", "club-card")],
 "club-card": [
   ("preceded", "trading-stamps"),
   ("depicts", "loyalty-dark-pattern"),
   ("cites", "coffee-card")],
 "mash-finale": [
   ("depicts", "gomer-pyle"),
   ("cites", "tv-cliffhanger-season")],
 "macy-paradox": [
   ("depicts", "the-clerk"),
   ("cites", "tv-cliffhanger-season"),
   ("cites", "macy")],
 "coffee-card": [
   ("succeeded", "trading-stamps"),
   ("cites", "club-card")],
 "comfort-watch": [
   ("cites", "mourn-a-person-you-met"),
   ("cites", "grief")],
 "shipping": [
   ("cites", "the-fanfic-writer"),
   ("cites", "parasocial-interaction")],
 "killing-off": [
   ("depicts", "grief"),
   ("cites", "avengers-endgame"),
   ("cites", "got-finale")],

# ------------------------------------------------------------ nineties onward
 "saturday-cartoons-top8": [
   ("member_of", "saturday-mornings"),
   ("cites", "grief")],
 "power-rangers-handover": [
   ("member_of", "saturday-mornings"),
   ("cites", "sasaeng-culture")],
 "saturday-mornings": [
   ("depicts", "saturday-cartoons-top8"),
   ("depicts", "power-rangers-handover"),
   ("cites", "peak-tv")],
 "cobain": [
   ("depicts", "grief"),
   ("cites", "michael-jackson"),
   ("contemporary", "prince")],
 "chatterbots": [
   ("preceded", "second-life"),
   ("cites", "the-ai-assistant"),
   ("contemporary", "replika")],
 "loyalty-counter": [
   ("cites", "club-card"),
   ("cites", "twitch-subs")],
 "the-brand-as-character": [
   ("cites", "celebrity-endorsement-fatigue"),
   ("cites", "crossover"),
   ("depicts", "boybands")],
 "boybands": [
   ("depicts", "the-brand-as-character"),
   ("contemporary", "kpop-parasocial-industry")],
 "webcasting": [
   ("preceded", "twitch-launch"),
   ("cites", "podcast-intimacy")],
 "anime-import": [
   ("cites", "kpop-parasocial-industry"),
   ("contemporary", "transnational-fandom")],
 "forum-culture": [
   ("depicts", "the-pile-on"),
   ("cites", "contest"),
   ("succeeded", "fandom-wars")],
 "transnational-fandom": [
   ("depicts", "anime-import"),
   ("depicts", "kpop-parasocial-industry"),
   ("cites", "second-life")],
 "second-life": [
   ("depicts", "the-uncanny-corridor"),
   ("cites", "vtuber"),
   ("contemporary", "forum-culture")],
 "michael-jackson": [
   ("succeeded", "elvis-hologram"),
   ("cites", "grief")],
 "contest": [
   ("depicts", "the-pile-on"),
   ("cites", "fandom-doxxing"),
   ("cites", "mob-and-internet-pile")],
 "doxxing": [
   ("depicts", "fandom-doxxing"),
   ("cites", "sasaeng")],
 "fan-injury": [
   ("cites", "sasaeng-culture"),
   ("cites", "pokemon-go-incident")],
 "the-closure-gift": [
   ("cites", "celebrity-endorsement-fatigue"),
   ("cites", "paid-intimacy")],
 "youtube-launch": [
   ("succeeded", "webcasting"),
   ("cites", "the-algorithm-decides"),
   ("contemporary", "twitch-launch")],
 "the-phone": [
   ("depicts", "the-ai-assistant"),
   ("cites", "siri"),
   ("cites", "paid-intimacy")],
 "the-pile-on": [
   ("depicts", "mob-and-internet-pile"),
   ("cites", "contest"),
   ("cites", "cancelling")],
 "tony-stark": [
   ("depicts", "superman-comic"),
   ("cites", "crossover")],
 "bieber-effect": [
   ("cites", "grief"),
   ("contemporary", "cobain")],
 "gilsoul-case": [
   ("cites", "the-pile-on"),
   ("cites", "parasocial-consent")],
 "paid-intimacy": [
   ("cites", "the-closure-gift"),
   ("cites", "the-subscription-box"),
   ("cites", "the-phone")],
 "quarterly-audit": [
   ("cites", "macy-paradox"),
   ("cites", "parasocial-consent")],
 "the-mourning-merch": [
   ("depicts", "grief-extraction"),
   ("cites", "grief")],
 "the-reply-heres-watching": [
   ("cites", "attention-economy"),
   ("cites", "live-commentary"),
   ("cites", "forum-culture")],
 "the-subscription-box": [
   ("cites", "loyalty-dark-pattern"),
   ("cites", "paid-intimacy")],
 "continuity": [
   ("cites", "mourn-a-person-you-met"),
   ("cites", "grief")],
 "siri": [
   ("succeeded", "shrlu"),
   ("depicts", "the-phone"),
   ("cites", "eliza")],
 "twitch-launch": [
   ("succeeded", "webcasting"),
   ("succeeded", "youtube-launch"),
   ("cites", "twitch-subs")],
 "fandom-wars": [
   ("succeeded", "forum-culture"),
   ("cites", "contest"),
   ("cites", "gamergate")],
 "swatting": [
   ("cites", "fandom-doxxing"),
   ("cites", "sasaeng-culture")],
 "gamergate": [
   ("member_of", "fandom-wars"),
   ("cites", "contest"),
   ("cites", "parasocial-persuasion")],
 "podcast-intimacy": [
   ("cites", "psr-research-begins"),
   ("cites", "parasocial-interaction"),
   ("preceded", "live-commentary")],
 "free-trial-bait": [
   ("depicts", "loyalty-dark-pattern"),
   ("cites", "the-subscription-box")],
 "live-commentary": [
   ("cites", "the-reply-heres-watching"),
   ("succeeded", "podcast-intimacy"),
   ("depicts", "ratio")],
 "ratio": [
   ("cites", "live-commentary"),
   ("cites", "the-pile-on")],
 "twitch-subs": [
   ("depicts", "loyalty-counter"),
   ("cites", "paid-intimacy"),
   ("cites", "twitch-launch")],
 "kpop-parasocial-industry": [
   ("cites", "transnational-fandom"),
   ("cites", "boybands"),
   ("contemporary", "anime-import")],
 "pokemon-go-incident": [
   ("cites", "fan-injury"),
   ("cites", "the-atletefan-bond")],
 "prince": [
   ("cites", "grief"),
   ("contemporary", "cobain")],
 "vtuber": [
   ("succeeded", "second-life"),
   ("cites", "twitch-launch"),
   ("cites", "vshojo")],
 "replika-launch": [
   ("preceded", "chatterbots"),
   ("succeeded", "replika-update"),
   ("cites", "eliza")],
 "avengers-endgame": [
   ("depicts", "killing-off"),
   ("cites", "keep-it-or-lose-it")],
 "billi-eilish": [
   ("member_of", "the-pile-on"),
   ("cites", "contest")],
 "got-finale": [
   ("cites", "killing-off"),
   ("cites", "tv-cliffhanger-season")],
 "grief-extraction": [
   ("depicts", "the-mourning-merch"),
   ("cites", "parasocial-diagnosis"),
   ("cites", "grief")],
 "kobe": [
   ("depicts", "grief"),
   ("contemporary", "prince")],
 "pokimane": [
   ("cites", "doxxing"),
   ("cites", "fandom-doxxing")],
 "characterai": [
   ("cites", "characterai-lawsuits"),
   ("cites", "scale-change"),
   ("cites", "eliza")],
 "the-ai-assistant": [
   ("succeeded", "siri"),
   ("cites", "the-phone"),
   ("cites", "the-uncanny-corridor")],
 "vshojo": [
   ("cites", "vtuber"),
   ("cites", "paid-intimacy")],
 "digital-bereavement": [
   ("depicts", "replika-closure"),
   ("cites", "grief")],
 "neighbours-finale": [
   ("cites", "soap-finale-study"),
   ("cites", "mourn-a-person-you-met")],
 "replika-closure": [
   ("succeeded", "replika-update"),
   ("depicts", "digital-bereavement"),
   ("cites", "grief")],
 "replika-update": [
   ("succeeded", "replika-launch"),
   ("depicts", "replika-closure"),
   ("cites", "digital-bereavement")],
 "stadium-residency": [
   ("cites", "the-atletefan-bond"),
   ("contemporary", "pokemon-go-incident")],
 "ai-acts": [
   ("cites", "characterai"),
   ("cites", "parasocial-consent")],
 "deepfake-grief": [
   ("succeeded", "elvis-hologram"),
   ("cites", "digital-orphans"),
   ("depicts", "grief")],
 "streamer-ban": [
   ("cites", "twitch-launch"),
   ("cites", "parasocial-consent")],
 "creator-on-tv": [
   ("cites", "gomer-pyle"),
   ("cites", "tv-cliffhanger-season")],
 "parasocial-problem": [
   ("cites", "fandom-doxxing"),
   ("cites", "the-uncanny-corridor")],
 "twitch-500m": [
   ("cites", "twitch-launch"),
   ("cites", "twitch-subs")],
}


def main():
    d = json.loads(ENC.read_text(encoding="utf-8"))
    by = {e["id"] for e in d["entries"]}
    byid = {e["id"]: e for e in d["entries"]}

    added = kept = 0
    dropped = []
    for e in d["entries"]:
        want = R.get(e["id"])
        if want is None:
            continue
        have = {(r["type"], r["to"]) for r in (e.get("relations") or [])}
        for typ, to in want:
            if to not in by:
                dropped.append((e["id"], typ, to))
                continue
            if (typ, to) in have:
                continue
            e.setdefault("relations", []).append({"to": to, "type": typ})
            added += 1
        kept += 1

    # dedupe, keep first
    for e in d["entries"]:
        seen, out = set(), []
        for r in e.get("relations") or []:
            k = (r["type"], r["to"])
            if k in seen:
                continue
            seen.add(k)
            out.append(r)
        e["relations"] = out

    ENC.write_text(json.dumps(d, indent=2, ensure_ascii=False), encoding="utf-8")

    n = len(d["entries"])
    edges = sum(len(e.get("relations") or []) for e in d["entries"])
    touched = sum(1 for e in d["entries"] if e.get("relations"))
    iso = [e["id"] for e in d["entries"] if not e.get("relations")
           and not any(r["to"] == e["id"] for x in d["entries"]
                       for r in (x.get("relations") or []))]
    print(f"{kept} entries given edges, {added} new, {edges} total")
    print(f"{touched} of {n} entries are connected; {len(iso)} still isolated")
    if iso:
        print("  isolated: " + ", ".join(iso))
    if dropped:
        print("  DROPPED (target does not exist):")
        for i, t, to in dropped:
            print(f"    {i} -{t}-> {to}")


if __name__ == "__main__":
    main()
