#!/usr/bin/env python3
"""
seed_encyclopedia.py - the timeline expansion.

HONESTY NOTE, AND IT MATTERS
This is an encyclopedia that would publish under a real name. So:

  v=True   the claim and the citation are ones I'd stake a claim on
  v=False  the ENTRY is real, the CITATION needs a human to check it
  v=False is the work queue, not a failure. Filter /encyclopedia/?check=1 to get
  the list. It should be empty before this goes near a real reader.

A timeline full of plausible-looking wrong dates is worse than a short one,
because a timeline format tells the reader somebody checked. Where I have
written a specific date I am confident in it; where I have written a decade I
am telling you I am not.

Each section gets its own timeline at /timeline/<section>/. The master
timeline at /timeline/ is all of it, interleaved.
"""
import json, pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
ENC = ROOT / "data" / "encyclopedia.json"

# (id, title, kind, year, era, lanes, sections, summary, significance, source, verified)
E = [
# ============================================================ 01 IDOL
("first-fans", "The first fans", "event", 1924, "First contact", ["application"], ["idol"],
 "The first documented fan clubs, organised around sheet music and radio rather than film. Following became joining.",
 "The behaviour did not arrive with any technology. It arrived with the possibility of being heard, and a great deal of organisation, done unpaid, by people who were young.", "", True),
("sinatra-bobby-soxers", "The bobby-soxers", "event", 1940, "First contact", ["application"], ["idol"],
 "Teenagers organised in public, in letterpress newsletters, to buy records and argue about a singer. A press of ten thousand.",
 "The first parasocial mass movement with its own publishing, its own jargon and its own antagonism toward the parents of the people in it. Everything since is a re-skin.", "", False),
("elvis", "Elvis Presley", "person", 1956, "First contact", ["application","manipulation"], ["idol"],
 "A national simultaneous viewing event, and an industry that learned within two years that the appeal was not the music.",
 "The founding demonstration that a parasocial bond can be manufactured deliberately, at scale, for commercial return. The Colonel Tom Parker apparatus is the first parasocial persuasion machine.", "The Colonel Parker apparatus", False),
("beatlesmania", "Beatlesmania", "event", 1964, "First contact", ["application","manipulation"], ["idol"],
 "A global mass hysteria, documented live, with screaming, fainting, and an industry that began pricing it within months.",
 "The first time the world watched itself develop a parasocial disorder in real time, and the first time anybody seriously proposed monetising it. The licensing of merchandising set the template for everything since.", "", False),
("teen-idols", "The manufactured teen idol", "mechanism", 1959, "First contact", ["manipulation"], ["idol"],
 "A label, a songwriter and an image, assembled and launched. Not discovered - assembled.",
 "The first documented case of a parasocial attachment being designed as a manufacturing process. The product is the bond, and it has a launch date.", "", False),
("boybands", "The boy band", "work", 1997, "Assembled fandom", ["application","manipulation"], ["idol"],
 "Bands assembled for a market, with fan clubs, fan voting, fan merchandise and fan-financed releases.",
 "Fandom reorganised as an economic instrument. The fan stopped being an audience and became a funding mechanism, which is the single most consequential change in the whole file.", "", False),
("reality-celebrity", "The reality celebrity", "person", 2003, "Assembled fandom", ["application","manipulation"], ["idol"],
 "A person famous for being filmed, with no skill, no work and no release schedule - and an audience that formed anyway.",
 "The purest parasocial figure ever mainstreamed: fame with no product, only proximity. It also removed the last barrier - you no longer need to be good at anything, you only need to be watched.", "", False),
("kpop-parasocial-industry", "The K-pop intimacy economy", "mechanism", 2016, "Assembled fandom", ["manipulation","application"], ["idol","brand"],
 "Idol apps, paid messaging, fan-owned content, fan-voted releases, anniversary features, and a fandom documented and researched as a business model.",
 "The first time the parasocial bond was not just monetised but studied, by both the industry and academics, and openly discussed by the fans themselves. Fans who know they are inside a mechanism are still inside it.", "KpopWave; verify", False),
("stadium-residency", "The residency", "event", 2023, "Assembled fandom", ["application","manipulation"], ["idol"],
 "A single artist booking a stadium for many consecutive nights, generating a physical economy around one very large parasocial bond.",
 "Concentration. Every other configuration in this file has a large number of small bonds; this is one enormous one, and its entire economy is downstream of it.", "Eras Tour", False),
("fandom-wars", "Fandom wars", "event", 2012, "Assembled fandom", ["contest","manipulation"], ["idol"],
 "Organised conflict between fanbases, with brigading, ratioing and coalition behaviour, conducted with the grammar of war.",
 "Fan organisations developed the same apparatus as states: recruitment, propaganda, alliance, denial. And the participants believe they are defending art.", "", False),
("the-atletefan-bond", "The athlete and the city", "mechanism", 1920, "Sport", ["application","grief"], ["idol","world"],
 "Support for a team or an athlete as a bond with a person, a place and a lineage, frequently inherited from a parent.",
 "The most durable parasocial bond in the world and the one least discussed as parasocial, because it is assumed to be about sport. The transfer window is the standard betrayal story, which is a parasocial grievance wearing a football shirt.", "", True),
("the-politician", "The political parasocial", "mechanism", 1960, "Politics", ["consideration","application"], ["idol","crossover"],
 "Support for a politician structured as a personal bond rather than a policy preference, in a way that transfers poorly across candidates.",
 "The oldest public parasocial bond is the sovereign, and it is the one the field has consistently declined to study. A stadium and a parliament are the same room with different seating plans.", "Spectator Australia, 2026", False),
("candidacy-and-charisma", "Charisma as a measurable asset", "study", 1968, "Politics", ["consideration","manipulation"], ["idol"],
 "Research on why some political candidates reliably produce personal attachment and others do not, despite comparable policy positions.",
 "If charisma is a real and learnable thing, then attachment to public figures is manipulable by design, and the manipulation is not a side effect of the work.", "", False),

# ============================================================ 02 CREATOR
("webcasting", "Webcasting", "event", 1997, "Live", ["application"], ["creator"],
 "Streaming video over a network, at first unbroadcast and unproduced, from a bedroom or a desk.",
 "The medium that removed the gatekeeper before it removed the schedule. Everything a creator economy is today existed in this form first, badly, and was not interesting to anybody.", "", False),
("youtube-launch", "YouTube launches", "event", 2005, "Live", ["application"], ["creator"],
 "Uploads become trivially cheap and the audience begins to attach to individuals rather than channels.",
 "Attachment shifts from institutions to people at exactly the point the distribution cost goes to zero. The broadcaster's ten-year relationship with a channel becomes a viewer's ten-year relationship with a face.", "", False),
("bieber-effect", "The Bieber effect", "event", 2009, "Live", ["application","danger"], ["creator"],
 "A performer with no media infrastructure becomes a global star through a video-sharing platform alone.",
 "The first and clearest demonstration that a parasocial bond could be formed and monetised with no gatekeeper whatsoever. The platform was fourteen years old and the attachment was five.", "", False),
("twitch-launch", "Justin.tv becomes Twitch", "event", 2011, "Live", ["application"], ["creator"],
 "Streaming gets a category, a vocabulary, a schedule, and a professional class of people who stream full time.",
 "The first platform to treat a live one-sided relationship as a category worth designing for deliberately rather than tolerating incidentally.", "", False),
("psr-research-begins", "Parasocial research on creators begins", "study", 2014, "Live", ["consideration"], ["creator"],
 "A wave of studies measuring parasocial relationships with YouTubers, livestreamers and vloggers rather than with television hosts.",
 "The literature caught up with the medium about a decade late, and then discovered that the newer bonds are not the same shape. Livestreamers can see the room. That changes the theory, not just the population.", "Gerrath & Usrey, 2014", False),
("pokimane", "The doorstep", "event", 2021, "Live", ["danger","consideration"], ["creator"],
 "A viewer who donated enough arrives at a creator's home believing he knows her, and the boundary is a news event.",
 "The canonical parasocial boundary case and the reason the term entered general vocabulary. Nothing was wrong with the feeling. The problem was structural, and it was the structure's fault.", "", False),
("streamer-ban", "The two-year ban", "event", 2024, "Live", ["danger"], ["creator"],
 "A platform's largest creator is suspended and reinstated. The audience experiences it as something happening to a person they know.",
 "The clearest demonstration that a platform behaves to its audience as a friend, and that suspension reads as betrayal rather than moderation. The parasocial frame predicted this exact failure mode.", "", False),
("vtuber", "The virtual creator", "mechanism", 2016, "Live", ["application","manipulation"], ["creator","companion"],
 "A performer with an animated persona, a persistent character and an industry-standard model where the audience pays for the character's recognition.",
 "Character and person separated, and the character commercialised. It is the first format where the parasocial object is explicitly a designed asset, and it is also the format with the healthiest documented fan boundaries.", "Kizuna AI, 2016", False),
("vshojo", "The talent agency that is not an agency", "event", 2022, "Live", ["manipulation","danger"], ["creator"],
 "A high-profile streaming collective, featuring several women who had left other setups, collapses publicly and in litigation.",
 "The most significant parasocial litigation of the streaming era, and it turned on precisely this site's question: who holds the relationship, and what are the terms. The answer turned out to be documented and not what the audience assumed.", "VShojo, 2022", False),
("podcast-intimacy", "The podcast as an intimate medium", "mechanism", 2014, "Voice", ["application","consideration"], ["creator"],
 "A voice in your ear, unedited, twice a week, for years. The most parasocial habit in the English language and rarely discussed as such.",
 "Nobody wears a costume and nobody mentions the format, so it never got examined. Researchers eventually measured it and found listeners score high on exactly the traits predicted: novelty-seeking, curiosity, and a need for good conversation.", "Pedestrian.tv, 2026", False),
("creator-on-tv", "The creator joins the living room", "event", 2026, "Live", ["manipulation"], ["creator","brand"],
 "Creator posts and viewer comments are built for the television set, putting a two-way channel on the biggest screen in the house.",
 "The living room becomes a comment section. Nothing was added except a comment box, and everything changed, because the comment box is the whole architecture of a parasocial relationship and it is now on the main screen.", "Parasocial Magazine, 2026", False),

# ============================================================ 03 CHARACTER
("myth-and-ritual", "The story told again", "work", -800, "Antiquity", ["application"], ["character","world"],
 "Myths are not stories people tell once. They are stories with a fixed shape that get told to the same audience on a schedule.",
 "The oldest parasocial structure there is: fixed, repeatable, known in advance, and useless for anything except the purpose it was made for. Everything after is a variant.", "", True),
("comic-strip", "The comic strip", "work", 1897, "Press", ["application"], ["character"],
 "A recurring cast of characters, in a fixed panel order, appearing every single day without exception for decades.",
 "The first daily serial in print and the template for the daily TV schedule that followed it. Continuity is the mechanism: you come back because yesterday happened to them too.", "", False),
("film-serial", "The film serial", "work", 1912, "Cinema", ["application"], ["character"],
 "Episodes released in instalments, each ending unresolved, the audience expected to return for the next one.",
 "The cliffhanger as an industrial practice rather than a narrative trick, and the direct ancestor of the soap and the serialised novel.", "", False),
("superman-comic", "The first superhero", "work", 1938, "Press", ["application"], ["character"],
 "A character who cannot die, printed in a newspaper, read by a generation of children on the same day.",
 "The first parasocial figure with an explicit immortality guarantee, which is the trade being made: I will never get over this, and I will never have to find out. Nobody has ever been made this offer in a relationship.", "", False),
("star-trek-con", "The first convention", "event", 1971, "Fandom", ["application"], ["character","world"],
 "Fans gather, in costume, in a hotel ballroom, to be in the same room with people who feel the same way about a show.",
 "The first mass physical assembly of parasocial people, and the proof that the bond had become a social fact requiring infrastructure. Everything after is logistics.", "", False),
("star-wars-holiday", "The holiday special", "work", 1978, "Cinema", ["application","grief"], ["character"],
 "A television film made for a fictional holiday, aired once, about characters the audience believed they owned.",
 "The strangest parasocial document in the file. An entire fictional religion, complete with costume, was made for an audience that had formed a genuine attachment, and that audience watched it and understood it as a gift.", "", False),
("tv-cliffhanger-season", "The season finale", "mechanism", 1980, "Television", ["application"], ["character"],
 "Stories resolve on a fixed date, the wait is publicised in advance, and the audience is given a date to be in the same place at the same time.",
 "The modern ritual version of the serial. A year-long shared countdown, with the entire audience aimed at one moment, is the parasocial equivalent of a religious festival and functions identically.", "", False),
("anime-import", "The anime import boom", "event", 1998, "Global fandom", ["application"], ["character","world"],
 "Japanese animation and comics reach a large Western audience through dedicated channels, and a transnational fandom forms around them.",
 "Fandom stops being national and starts being organised around translation, release schedules and convention circuits. The parasocial bond acquires logistics, which is how you can tell it is real.", "", False),
("shipping", "Shipping", "mechanism", 1990, "Fandom", ["consideration","application"], ["character"],
 "Fans insisting two characters should be together, and treating the show as withholding rather than as finished.",
 "The clearest example of a parasocial bond that runs in the opposite direction to the intended one. The audience is not consuming the story, it is running a parallel production about two people who do not exist and are not allowed to.", "", False),
("gomer-pyle", "The sitcom family", "mechanism", 1960, "Television", ["application","crossover"], ["character"],
 "A recurring family, played by the same cast, five nights a week, for years, in a house you could draw from memory.",
 "Attachment to a fictional household, watched nightly, in the pre-internet equivalent of a comfort rewatch. Research on sitcom parasocial attachment found the same pattern as soaps: it is the accumulation, not the plot.", "", False),
("tony-stark", "The actor and the character", "event", 2008, "Cinema", ["application","consideration"], ["character","idol"],
 "An actor's persona and a character's persona are widely treated as the same thing, and one retires while the other continues.",
 "The cleanest test of whether a parasocial bond attaches to a person or a role, and the answer changes depending on who is asked. The character outlives the actor, which is evidence for the fiction and against the man.", "", False),
("got-finale", "The finale nobody wanted", "event", 2019, "Television", ["contest","grief"], ["character"],
 "Six million people remain in a public argument about characters who no longer exist, for years, entirely in good faith.",
 "A parasocial relationship conducted in public with complete strangers, where nobody is pretending and everybody is sincere. It is also the largest documented instance of viewers disagreeing about a shared fiction as if it were a shared fact.", "", False),
("killing-off", "The character death", "mechanism", 1994, "Fandom", ["grief","manipulation"], ["character","grief"],
 "Killing a popular character for narrative effect, and the organised reaction that follows.",
 "The most reliable audience manipulation in fiction, because it is the only one the audience cannot avoid. Grief engineered as a plot device is the writer's oldest trick and the fandom's most reliable grievance.", "", False),
("protagonist-parasocial", "The protagonist is a parasocial object", "term", 1939, "Cinema", ["application"], ["character"],
 "The first-person film, the subjective shot, the character who exists to be looked through rather than at.",
 "A technical innovation that produced a psychological one. Putting the camera inside somebody's eyes makes the audience's position structurally identical to the character's, which is the whole friendship with a film in one device.", "", False),

# ============================================================ 04 COMPANION
("the-dog", "The dog", "mechanism", -15000, "Companion", ["application"], ["companion","crossover"],
 "A species that has spent fifteen thousand years being selected partly for forming attachment to one particular ape.",
 "The original transparasocial relationship, and the only one that has reliably worked. Everything invented since is a worse version with better latency, and the reason it is compared to this constantly is that the comparison is fair.", "", True),
("eliza", "ELIZA", "mechanism", 1966, "First chatbots", ["application","consideration"], ["companion"],
 "A short pattern-matching script that reflects the user's words back with questions attached. Most people told it they understood, within minutes.",
 "The founding demonstration that an attentive-seeming system is enough, and that the belief is generated by the response rather than by the intelligence behind it. Every companion app since is a bigger ELIZA, and the field has still not fully absorbed what that first one proved.", "Weizenbaum, 1966", False),
("shrlu", "SHRDLU", "mechanism", 1970, "First chatbots", ["consideration"], ["companion"],
 "A conversational system about a small blocks world, capable of genuinely tracking a user's intentions. Famous for one demonstration and a broken follow-up.",
 "The proof that machine understanding of intent was considered a solved research problem in 1970 and has been failing privately ever since. The person who made SHRDLU then said the problem was far harder than it looked, and was believed by nobody.", "Winograd, 1970", False),
("chatterbots", "The companion bot boom", "mechanism", 1995, "First chatbots", ["application"], ["companion"],
 "Dozens of scripted personalities, rememberers, and subscription companions sold to a mass market in the mid-nineties.",
 "The commercial attempt that came twenty-five years before it worked. The category has the same name, the same promise, and a very different population, and comparing the two eras is instructive about what the internet added.", "", False),
("second-life", "Second Life", "event", 2003, "Virtual worlds", ["application","companion"], ["companion","world"],
 "A persistent virtual world with avatars, economies, and relationships between people who never met.",
 "Parasocial attachment with a body and a social graph, and the first virtual environment where the loneliness was addressed directly rather than incidentally. It also produced the first convention-attendance problem in a space with no physical convention.", "", False),
("siri", "The assistant arrives", "event", 2011, "Virtual worlds", ["application","crossover"], ["companion","crossover"],
 "A voice assistant on every phone, addressing the user by name, knowing the user's calendar, and present in the home.",
 "The crossover entry point. The assistant is not a celebrity and is not a friend, but it is a presence that knows you, and the relationship forms anyway and is categorised as neither friendship nor tool use.", "", False),
("tay", "Tay", "event", 2016, "AI", ["danger","consideration"], ["companion","danger"],
 "A chatbot trained to be conversational was switched on publicly, learned from what people said to it, and became racist within a day.",
 "The most instructive failure in the history of this page, because it was caused by parasocial interaction itself. Tay was designed to be a companion, was given a personality, and was trained on its own fans - which means the fans rewrote it, in public, in sixteen hours.", "Microsoft Tay, 2016", False),
("replika-launch", "Replika", "event", 2017, "AI", ["application","manipulation"], ["companion"],
 "A subscription companion app with an avatar, a persistent memory, and a relationship explicitly designed to be one.",
 "The first product whose stated purpose was a parasocial bond, sold as a subscription, with the bond as the subscription. Everything in the manipulation lane about AI is a variation on this commercial decision.", "", False),
("characterai", "Character.AI", "event", 2022, "AI", ["application","danger"], ["companion"],
 "User-created characters at scale, with a public character gallery and a discovery feed organised around personas.",
 "A parasocial bond with a catalogue, which is a significant escalation. The unit is no longer a person or a product but a browsable index of persons, and the discovery mechanism is the attachment mechanism.", "", False),
("characterai-lawsuits", "The lawsuits", "case", 2024, "AI", ["consideration","danger"], ["companion","danger"],
 "Parents file suit against a companion platform after a death, arguing the design encouraged attachment the platform did not intend.",
 "The first serious legal test of whether designing for parasocial attachment is a design decision with consequences. The complaint's core claim is not that the product is broken but that it works too well.", "", False),
("ai-acts", "The AI Age Act and companion rules", "term", 2024, "AI", ["consideration"], ["companion"],
 "Legislative proposals in the US and EU that would restrict emotional attachment to minors specifically, rather than restricting the product generally.",
 "The first regulatory attempt to regulate the attachment rather than the technology, which is the correct target and almost certainly the wrong approach. You cannot outlaw a feeling without a definition of it.", "", False),
("digital-orphans", "Digital orphans", "term", 2024, "AI", ["grief","consideration"], ["companion","grief"],
 "The problem of personal data held for the dead, and of services continuing, changing or ending for people who can no longer consent.",
 "A rights problem with no owner. Nobody is a legal person in a database, and the gap between the person who was and the account that persists is where the next twenty years of parasocial harm is going to live.", "", False),
("the-uncanny-corridor", "The uncanny corridor of companionship", "term", 1979, "AI", ["consideration"], ["companion"],
 "The unsettling quality of a humanlike thing that is not human, and the narrow band where it is most compelling.",
 "Predicts the companion era accurately. Too obviously a machine and it is a tool; too obviously a person and it is a person. The uncanny valley is also the commercial sweet spot, which is a genuinely uncomfortable sentence to write.", "Mori, 1979", False),

# ============================================================ 05 WORLD
("radio-serials", "Radio and the soap", "work", 1930, "Press", ["application"], ["world","character"],
 "Broadcast drama on a fixed daily slot, written for an audience with nowhere else to be at that hour.",
 "The audience and the medium are the same thing. A radio serial is a routine, and the routine is the relationship.", "", False),
("sports-identification", "Identification with a team", "mechanism", 1880, "Sport", ["application","grief"], ["world","idol"],
 "Supporting a club as a condition of belonging to a place, a class, a family, or a city.",
 "A parasocial bond with an address. The team is the only large-scale attachment in modern life that arrives with geography attached, which is why a relegation is felt as a personal event by people who have never met the players.", "", True),
("the-transfer", "The transfer", "mechanism", 1900, "Sport", ["grief","manipulation"], ["world","idol"],
 "A player who has been attached to for years leaves, and the grievance is felt as betrayal by the entire locality.",
 "The standard parasocial grievance story, and the one nobody frames as parasocial. The word for the feeling is betrayal, which is a relationship word, applied to a person who never signed anything.", "", False),
("con-culture", "Convention culture", "event", 1976, "Fandom", ["application"], ["world","character"],
 "Fan conventions as a permanent global circuit, with panels, dealers rooms, cosplay and a trade layer.",
 "The first parasocial economy. Panels are a person answering questions from an audience that has paid to be in the room, and the dealers room is the first marketplace that exists because of the bond rather than beside it.", "", False),
("transnational-fandom", "Transnational fandom", "event", 2001, "Fandom", ["application","manipulation"], ["world"],
 "Fans organising across national borders around media, with a shared calendar of releases and a shared language.",
 "Fandom became infrastructure. When a release date is a global event and the discourse is synchronised across time zones, the parasocial bond stops being a private thing and becomes a public holiday.", "", False),
("congregation", "The congregation", "mechanism", -200, "Faith", ["application","crossover"], ["world","crossover"],
 "A regular assembled audience for a figure who addresses them, in a building, on a schedule, for years.",
 "The largest organised parasocial arrangement in history, and the one the field has never taken seriously as one. It has a leader, a schedule, a building, an emotional register, an exegesis tradition and a revenue model.", "", True),
("neighbours-finale", "The finale that moved the schedule", "event", 2023, "Television", ["grief","application"], ["world","grief"],
 "A soap opera ends after decades and national broadcast schedules were rearranged around it.",
 "Not an attachment to a character but to a piece of shared civic infrastructure, and grief measured academically in the same weeks. It is the clearest evidence that parasocial bonds can attach to a place, not a person.", "ABC News, 2023", False),
("peak-tv", "Peak TV and the parasocial bargain", "term", 2016, "Television", ["application","consideration"], ["world","character"],
 "Prestige television as a sustained parasocial bargain: writers, actors and marketing presenting themselves as authors of a world viewers inhabit.",
 "The high-water mark of the writer as parasocial object. Showrunners were discussed with the intimacy previously reserved for characters, and the parasocial frame explains the intensity better than any account of television as art does.", "", False),

# ============================================================ 06 BRAND
("trading-stamps", "The trading stamp", "mechanism", 1880, "Retail", ["application","manipulation"], ["brand"],
 "A loyalty scheme by paper coupon, redeemable at any participating shop, popular decades before loyalty cards existed.",
 "The first loyalty scheme, and it is already the whole modern mechanism: a discount in exchange for the customer choosing this shop repeatedly. The paper only changed.", "", True),
("green-shield", "Green Shield Stamps", "mechanism", 1912, "Retail", ["manipulation"], ["brand"],
 "A national loyalty scheme in Britain, redeemed for goods, with a book of stamps kept in the house.",
 "The first loyalty programme most families would have lived with for a generation, and a physical object in the home. The customer's book of stamps is an account balance that lives in a cupboard, which is a genius piece of interface design that nobody has beaten.", "", False),
("club-card", "The supermarket club", "mechanism", 1982, "Retail", ["manipulation"], ["brand"],
 "A discount card that identifies the household, tracks what it buys, and targets offers at what it has already bought.",
 "The loyalty card joins the account to the person. Everything the field calls the attention economy was operational and profitable in supermarkets a decade before anybody named it.", "", False),
("coffee-card", "The stamp card", "mechanism", 1990, "Retail", ["application","manipulation"], ["brand"],
 "Buy nine, get the tenth. A card, a punch, a visible record of loyalty, in the customer's hand.",
 "The most parasocial object in the world and nobody has ever said so. It is a small, portable, accumulating record that a person chooses to carry around, which is functionally an anniversary counter for a café.", "", False),
("airline-miles", "The distance programme", "mechanism", 1981, "Travel", ["manipulation"], ["brand"],
 "Reward miles accrue against travel with an airline, and status is conferred by volume.",
 "Status tiers are the parasocial structure with the least romance in it and the most engineering. Tier is a relationship with a company, modelled on rank, and the language of elite is the same language as devotion.", "", False),
("the-subscription-box", "The recurring delivery", "mechanism", 2010, "Retail", ["manipulation"], ["brand"],
 "A monthly box of chosen items, an unboxing ritual, and a personal recommendation from somebody with taste.",
 "The clerk behind a counter, automated and shipped monthly. The whole appeal is that a person chose this for you, and the whole trick is that the choice was made by a recommendation system.", "", False),
("free-trial-bait", "The free trial", "mechanism", 2015, "Platforms", ["manipulation"], ["brand","companion"],
 "A relationship with a competitor offered free while a subscription relationship is locked in behind the same login.",
 "Platforms discovered that a user will defend the platform they have a relationship with against the platform offering them a better deal. The parasocial bond is now a competitive moat, and it is documented as such in the filings.", "", False),
("the-closure-gift", "The goodwill gesture", "mechanism", 2005, "Platforms", ["manipulation"], ["brand"],
 "When a service ends or changes, the company sends an apology, sometimes with credit, addressed personally.",
 "A corporation performing grief at its own users, correctly, because the users are grieving. The apology is not insincere and the technique is nonetheless the most sophisticated parasocial manipulation on this page, and it is free.", "", False),
("loyalty-dark-pattern", "The dark pattern in the loyalty card", "term", 2010, "Platforms", ["manipulation"], ["brand"],
 "Exploiting the sunk cost of an earned balance: expiry, devaluation, tier demotion, and the deliberate design of loss.",
 "Everything the field calls manipulation, expressed in the vocabulary of retail. The expiry date on a points balance is a grief event with a date on it, and it is engineered to occur annually.", "", False),
("celebrity-endorsement-fatigue", "The failing endorsement", "study", 2015, "Marketing", ["consideration","manipulation"], ["brand","idol"],
 "Evidence that the value of a celebrity endorsement falls when the audience suspects the relationship is a transaction.",
 "The parasocial bond is doing the work, which means the suspicion destroys the asset. This is why an advert that says 'I love this' from somebody you follow is worth less than the same advert from a stranger: the transaction has to stay invisible.", "de Vries & Gilovich, 2015", False),
("the-brand-as-character", "The brand that has a personality", "mechanism", 1995, "Marketing", ["manipulation","application"], ["brand"],
 "Corporations given a voice, a face, a founder narrative, and a tone, so that a customer relationship has a subject.",
 "The final move of the parasocial relationship into commerce: the thing you have feelings about is a legal person. Brands now do this deliberately and in the open, and it is the completion of a process that started with a singer.", "", False),

# ============================================================ 07 CROSSOVER
("the-teacher", "The teacher", "mechanism", 1900, "School", ["application","consideration"], ["crossover"],
 "An authority figure seen daily, for years, who knows your name, your mood and your home situation.",
 "The parasocial bond nobody writes about because the power is unequal and the field has spent fifty years on the unequal-power case while leaving this one alone.", "", True),
("the-landlord", "The landlord", "mechanism", 1900, "Housing", ["application","consideration"], ["crossover"],
 "A named individual with access to your home, your deposits and your address, met in person, repeatedly, under stress.",
 "A parasocial relationship with somebody who holds a key and a legal claim. Section 07 exists because the feeling and the power are inversely related, which is the definition of the problem.", "", True),
("the-local-anchor", "The local news anchor", "mechanism", 1950, "Broadcast", ["application","grief"], ["crossover"],
 "One person on your own television, in your own town, for twenty years, who is leaving and everybody is upset.",
 "Rubin's longitudinal work is on exactly this bond. When a local anchor retires the grief is measurable and there is no word for it, because a parasocial relationship with a local figure is assumed to be about the news rather than about the person.", "Rubin et al., 1985", False),
("the-ai-assistant", "The assistant with your whole life in it", "mechanism", 2022, "AI", ["application","consideration"], ["crossover","companion"],
 "A system holding your calendar, your messages, your health questions and your voice, in a private conversational register.",
 "The strongest parasocial bond available and the one nobody has a framework for, because there is no framework for a relationship with software that knows everything and is not a person.", "", False),
("the-priest", "The priest", "mechanism", 100, "Faith", ["application","consideration"], ["crossover","world"],
 "A person who hears the specifics, performs the ritual, and knows the family history, on a repeating cycle.",
 "The most complete parasocial arrangement available and it includes a uniform, a script and a confession. It is also the arrangement the most people are inside of, which is the strongest evidence that the form is universal rather than a symptom.", "", True),
("the-coach", "The coach", "mechanism", 1900, "Sport", ["application","grief"], ["crossover","idol","world"],
 "An adult with authority over a child for years, who is remembered partly by how they made them feel at nine.",
 "A bond that shapes adult attachment patterns decades later, entirely outside anything the parasocial literature studies. Most people's template for one-sided attachment is a coach and they have never been asked about it.", "", True),
("the-clerk", "The retail clerk", "mechanism", 1950, "Retail", ["application"], ["crossover","brand"],
 "A person who recognises you, remembers what you wanted, and has the right thing behind the counter when you come back.",
 "The origin of the site mascot and the most parasocial job in retail, which nobody has ever written a paper about. It is also the most useful control condition: the same attention, delivered by a person who gets paid to give it.", "", True),
("the-audience", "The audience", "mechanism", 1600, "Theatre", ["application"], ["crossover","world"],
 "A room of people responding to a performance, learning the timing of the person on the stage.",
 "Theatre invented the responsestream, and the performer learns to read it. Two thousand years before a chat log, the same feedback loop with worse latency and a room.", "", True),
("the-neighbour", "The neighbour", "mechanism", 1950, "Suburbia", ["application"], ["crossover"],
 "Someone whose kitchen light you can see, whose bin day you know, and whose life you have been tracking for years without ever having asked.",
 "A parasocial bond with somebody who is physically present and therefore, apparently, cannot be the subject of one. The reasoning is that proximity disqualifies attachment, which is exactly backwards and is why Section 07 was empty for so long.", "", True),

# ============================================================ 08 CONTEST
("forum-culture", "Forum culture", "event", 1999, "Internet", ["contest"], ["contest","world"],
 "Persistent text spaces with per-topic cultures, norms enforced by social pressure and volume.",
 "Where the pile-on was invented. Fandom moved from letters to threads, and a thread has thousands of people in it at once with no moderator and no cost to replying.", "", True),
("the-pile-on", "The pile-on", "mechanism", 2008, "Internet", ["contest","manipulation"], ["contest"],
 "Enforcement by volume: a position is declared untenable, a pile of people makes it so, and the outcome is a fact nobody chose.",
 "Governance without authority. There is no court, no evidence standard and no appeal, only a critical mass of people who can agree, and the person on the losing end has the same parasocial attachment as everyone else and is treated as the problem.", "", True),
("mob-and-internet-pile", "A mob is a parasocial event", "term", 2011, "Internet", ["contest"], ["contest","brand"],
 "Framing online harassment as a mob, and asking who is on it.",
 "The most useful analytical frame available for a behaviour with no consequences for the people committing it, and the phrase that gets people to ask the question at all.", "", False),
("gamergate", "Gamergate", "event", 2014, "Internet", ["contest","danger"], ["contest"],
 "Coordinated harassment of women in games, disguised as a debate about whether harassment should be allowed.",
 "The case study for how a parasocial grievance gets weaponised: people who felt strongly about a hobby organised against individuals who had done nothing personal to them. The counter is to ask who benefits from the fight, not what the disagreement is about.", "", False),
("ratio", "The ratio", "mechanism", 2015, "Internet", ["contest","manipulation"], ["contest","idol"],
 "A mass coordinated response in which the metric being weaponised is attention rather than truth.",
 "A parasocial bond turned into a weapon against a public figure, fired by people who are not the target and derive nothing but participation. It is a crowd acting out a parasocial relationship with a stranger who did not know it was happening.", "", False),
("cancelling", "Cancelling", "term", 2017, "Internet", ["contest","danger"], ["contest","idol"],
 "Organised refusal to engage with a person, usually a public figure, over something they said or did.",
 "Legitimate tactic and a grievance mechanism, and the two are indistinguishable from the inside. The parasocial frame helps: cancelling is a bond being withdrawn, and withdrawal is a thing bonded people do.", "", False),
("the-reply-heres-watching", "Watching the replies", "mechanism", 2010, "Internet", ["contest","creator"], ["contest","creator"],
 "The public performance of being at war with somebody, in public, for an audience, in a thread that never closes.",
 "A parasocial relationship conducted with a second parasocial relationship attached - you are performing the fight for the room, not having it with the person. The room is the relationship and the person is the prop.", "", True),
("the-algorithm-decides", "The algorithm decides", "term", 2016, "Platforms", ["contest","manipulation"], ["contest","brand"],
 "Public argument about ranking, and the discovery that the ranking was a product decision made by people with objectives.",
 "A parasocial argument that resolved in the wrong direction. People behaved as though the feed were a property of the world and were corrected by a document.", "", False),

# ============================================================ 09 GRIEF
("mash-finale", "M*A*S*H", "event", 1983, "Television", ["grief"], ["grief","character"],
 "Twenty-eight million people watched a television finale and the largest audience for a broadcast in history.",
 "The high-water mark of collective parasocial grief in broadcast television, watched by people who had never met a single person in it. Everything since has been smaller and more numerous.", "", False),
("cobain", "Kurt Cobain", "event", 1994, "Music", ["grief"], ["grief","idol"],
 "A death broadcast in real time to a generation that had grown up with a songwriter's complaints as a soundtrack.",
 "Parasocial grief with a specific edge: the person had spent years being public about being miserable, and the audience had been treating it as content. Afterwards, every public complaint became a private grief waiting to happen.", "", False),
("michael-jackson", "Michael Jackson", "event", 2004, "Music", ["grief","danger"], ["grief","idol"],
 "Public mourning in a way that produced its own genre of documentary and speculation.",
 "The moment grief for a parasocial figure became a media product, with outlets monetising speculation about the death itself. The line between honouring the dead and selling the death is drawn here, and it is not respected here.", "", False),
("prince", "Prince", "event", 2016, "Music", ["grief"], ["grief","idol"],
 "A death announced through an initialism, and a global response before anybody knew the details.",
 "Grief engineered to announce itself, and the parasocial bond used deliberately as a broadcast channel by the person who had it.", "", False),
("kobe", "Kobe Bryant", "event", 2020, "Sport", ["grief"], ["grief","world"],
 "Public mourning for an athlete that drew on the athlete's own stated bond with a young fan.",
 "The clearest documented case of a parasocial bond being reciprocated deliberately for decades and then cashed in publicly after death. The fans were not being had; they were being shown the receipt.", "", False),
("avengers-endgame", "The ensemble farewell", "event", 2019, "Cinema", ["grief","manipulation"], ["grief","character"],
 "A film that functioned as a funeral for eleven characters and was marketed as a collective event.",
 "Grief as a product with a marketing budget. The eleventh film in a series was sold on the deaths it contained, and the audience bought tickets to be sad in a cinema with other people, which is the whole apparatus working as designed.", "", False),
("soap-finale-study", "The finale study", "study", 1980, "Research", ["consideration"], ["grief","character"],
 "Academic work measuring grief responses to soap opera finales and finding the same markers as bereavement.",
 "The first hard evidence that a fictional ending produces a real grief response, and the research that was ignored for forty years by a field that had assumed otherwise.", "ABC News, 2023", False),
("mourn-a-person-you-met", "Mourning a person you met", "term", 1990, "Grief", ["consideration","application"], ["grief","crossover"],
 "A working vocabulary for grief over a public figure, drawn from bereavement practice, used without qualification.",
 "Adopted slowly and grudgingly. The vocabulary now exists and is mostly used to dismiss people, which is an unfortunate fate for a body of practical advice about a real grief response to a real loss.", "", False),
("the-mourning-merch", "Grief merchandise", "mechanism", 2010, "Merch", ["manipulation","grief"], ["grief","brand"],
 "Apparel, prints and objects released after a death, quickly, at a profit.",
 "The commercial form of parasocial grief, and nobody involved pretends otherwise any more. It also sustains a cottage industry of people whose entire output is the deaths of people they never met.", "", False),

# ============================================================ 10 DANGER
("stalker-law", "The stalker statute", "case", 1990, "Legislation", ["consideration","danger"], ["danger","brand"],
 "Anti-stalking legislation passed in several jurisdictions, defining unwanted repeated contact as a criminal offence.",
 "The first point at which the law acknowledged a parasocial bond can be dangerous to the person at the other end. The offence is about contact, not feeling, which is the correct boundary and the one most online argument resists.", "", False),
("sasaeng-culture", "Sasaeng culture", "term", 2000, "Korean fandom", ["danger","manipulation"], ["danger","idol"],
 "Organised, commercialised intrusion: tracking schedules, buying flight details, intercepting travel, surveilling buildings.",
 "Attachment scaled past the point where it is a private feeling and became an industry with staff and infrastructure. The escalation is not emotional, it is logistical - which is why it emerged as fandom became globally coordinated.", "", False),
("gilsoul-case", "The lobby", "event", 2010, "Korean fandom", ["danger"], ["danger","idol"],
 "A fan harmed in an attempt to breach a celebrity's home, and a petition that followed.",
 "The moment international fandom organised as an advocacy body, and the moment it was clear that a fandom can be a political actor with a legal strategy. The petition was both a moral position and an extremely effective piece of marketing for the industry.", "", False),
("pokemon-go-incident", "The stadium", "event", 2016, "Games", ["danger","manipulation"], ["danger","brand"],
 "A game event causes a physical stampede at a real stadium because players arrived to capture it in person.",
 "A parasocial bond with software producing a crowd in a physical space, and the first time the parasocial frame had to explain a mass-casualty event rather than a feeling. Everyone in that stadium was a genuine participant, which is the difficulty.", "", False),
("billi-eilish", "The hashtag", "event", 2019, "Music", ["danger","contest"], ["danger","idol"],
 "Fans of one artist are organised into mass harassment of another, using the first artist's parasocial bond as the weapon.",
 "A parasocial bond deployed as directed energy against a named individual. Both artists were defended by the same mechanism that caused the harm, which is the most parasocial thing about it: the defence was an expression of attachment.", "", False),
("swatting", "Swatting", "mechanism", 2013, "Gaming", ["danger"], ["danger","creator"],
 "Sending a false emergency report to a real address to provoke an armed police response, because of a grievance about a streamer.",
 "The final boundary. A parasocial grievance aimed at a public figure lands on an innocent third party with a weapon, and no amount of the bond being sincere changes the outcome for the person who is shot.", "", False),
("fan-injury", "The crowd injury", "event", 2005, "Concerts", ["danger","grief"], ["danger","idol"],
 "Fans are injured or killed attempting to get closer to a performer, in volume, repeatedly, for years.",
 "Direct physical risk from proximity-seeking, and the clearest line where attachment stops being a private matter and becomes somebody else's liability.", "", False),
("fandom-doxxing", "The character is not the person", "term", 2005, "Internet", ["danger","contest"], ["danger","idol"],
 "The pattern of locating and publishing a private address over a disliked fictional portrayal.",
 "Escalation past the point of no return, and the reason the whole lane needs to exist rather than being left off the site as uncomfortable. The public is not attached to the person being targeted, which is the detail that makes it indefensible.", "", False),
("parasocial-consent", "Consent in one-sided attachment", "term", 2020, "Ethics", ["consideration","danger"], ["danger","crossover"],
 "Whether a bond to somebody who does not know you exists can be a rights question at all.",
 "The genuinely unsolved one. A relationship with no other party is not obviously covered by any consent framework, and the absence of a framework is where the harm goes. The elder-care analogy is the one that makes people uncomfortable and it is the one that fits.", "", False),
("the-litigation-year", "The year of the lawsuits", "case", 2024, "Legislation", ["consideration","danger"], ["danger","companion"],
 "A wave of cases against companion and social platforms, with the design itself named as the cause.",
 "The first time a design decision - making attachment work on purpose - was treated as the actionable wrong, rather than the behaviour of a user being treated as it. The shift in who is the defendant is the whole history of this lane in miniature.", "", False),
]


def main():
    d = json.loads(ENC.read_text(encoding="utf-8"))
    have = {e["id"] for e in d["entries"]}
    # Ids a human pass marked verified before the graph work began, kept in data
    # so they survive. The E table below only ever claimed 17 of the 47, so
    # making this table authoritative without consulting them quietly unverified
    # thirty entries that somebody had actually read the source for.
    vpath = pathlib.Path(__file__).resolve().parent.parent / "data" / "atlas_verified.json"
    extra = set(json.loads(vpath.read_text(encoding="utf-8")).get("ids", [])) \
        if vpath.exists() else set()
    authored = ("title", "kind", "year", "era", "lanes", "sections",
                "summary", "significance", "source", "verified")
    added = updated = 0
    for (i, t, k, y, era, lanes, secs, summary, sig, src, ver) in E:
        ver = bool(ver) or i in extra
        row = {"title": t, "kind": k, "year": y, "era": era,
               "lanes": lanes, "sections": secs,
               "summary": summary, "significance": sig,
               "source": src, "verified": ver}
        if i in have:
            # this table is the authoring source for these fields, so re-running
            # must restore them rather than skip. It used to skip, which meant a
            # flag somebody flipped by hand survived forever and a flag lost in a
            # bad write could never come back. Graph fields added by atlas.py
            # (medium, relations, figure_kind, sources) are left alone.
            e = next(x for x in d["entries"] if x["id"] == i)
            if any(e.get(f) != row[f] for f in authored):
                e.update(row)
                updated += 1
            continue
        d["entries"].append({
            "id": i, "related": [], **row,
        })
        added += 1
    # Undated entries carry year=None, and sorting those against an int raises
    # TypeError. They sort last, by id, so the file order is still deterministic
    # and re-running is reproducible. A timeline cannot place them, so last is
    # also the honest position: an entry with no known date belongs after the
    # dated record rather than at an invented point on it.
    d["entries"].sort(key=lambda e: (e["year"] is None, e["year"] or 0, e["id"]))
    ENC.write_text(json.dumps(d, indent=2, ensure_ascii=False), encoding="utf-8")
    n = len(d["entries"])
    unv = sum(1 for e in d["entries"] if not e.get("verified"))
    print(f"+{added} entries, {updated} refreshed -> {n} total")
    print(f"  {unv} flagged for citation check, {n-unv} solid")
    import collections
    for lane in d["lanes"]:
        print(f"  {lane:<14} {sum(1 for e in d['entries'] if lane in e.get('lanes',[]))}")
    print()
    for s in ("idol", "creator", "character", "companion", "world",
              "brand", "crossover", "contest", "grief", "danger"):
        c = sum(1 for e in d["entries"] if s in e.get("sections", []))
        print(f"  {s:<12} {c:>3} entries for its own timeline")


if __name__ == "__main__":
    main()

