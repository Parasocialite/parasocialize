#!/usr/bin/env python3
"""
seed_cards.py — writes the real story set into data/shop.json.

These are real stories with real URLs, taken from what the sweeper actually
found. Takes are written by a human (Enan) at a human (me) in the voice the
site actually wants: warm, loud, quick, and never once pathologising a reader.

  python tools/seed_cards.py
"""
import json, pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
SHOP = ROOT / "data" / "shop.json"

G = "https://www.theguardian.com/commentisfree/2026/sep/28/celebrity-deaths-parasocial-relationships-grief"

# slug, section, law, shelf, filed, state, kicker, headline, oneline, take, (pub, title, url)
C = [
# ---------------------------------------------------------------- THE LEAD
("madeonyoutube-spending-on-scoreboard", "brand", 3, "company-dreamer", "2026-09-26", "OUT",
 "The big one",
 "YouTube just put your spending on the scoreboard",
 "Nine separate parasocial stories came out of one event. The throughline is worse than any of them.",
 "Here is what nobody said out loud at Made on YouTube: the relationship is now a fixture with a sponsorship category. "
 "Live Showdown decides the score by what viewers spend. Creator posts and comments go on the television. Shopping GMV is up "
 "thirteen times and they finally put a number on it. You are not watching a person any more, you are watching a "
 "venue that has learned exactly how much a feeling costs, and it is asking you to settle up in public.",
 [("Parasocial Magazine", "YouTube's Live Showdown Turns Fan Funding Into Contests",
   "https://www.parasocialmagazine.com/news/youtubes-live-showdown-turns-fan-funding-into-contests/"),
  ("Parasocial Magazine", "YouTube Shopping GMV Grew 13x, 1.3M Creators Enrolled",
   "https://www.parasocialmagazine.com/money/youtube-shopping-gmv-grew-13x-1-3m-creators-enrolled/"),
  ("Parasocial Magazine", "YouTube Hits 14.2% of U.S. TV Viewing, a Nielsen Record",
   "https://www.parasocialmagazine.com/news/youtube-hits-14-2-of-u-s-tv-viewing-a-nielsen-record/")]),

("youtubetv-living-room", "brand", 3, "insight-company", "2026-09-26", "OUT",
 "",
 "The living room is now a comment section",
 "YouTube's creator posts and remote comments are built for the TV. Your sofa is a forum now.",
 "The single weirdest thing about this is how small the change is and how complete. A person used to sit on a couch and "
 "watch something. Now they sit on a couch and are in a room where the person can see them. Nothing was added except a "
 "comment box, and everything changed, because the comment box is the whole architecture of a parasocial relationship and "
 "we finally put it on the big screen where it belongs.",
 [("Parasocial Magazine", "YouTube Brings Creator Posts, Remote Comments to TVs",
   "https://www.parasocialmagazine.com/news/youtube-brings-creator-posts-remote-comments-to-tvs/")]),

("vid-summit-bars-fans", "creator", 2, "insight-company", "2026-09-26", "OUT",
 "",
 "The platform's big creator conference banned fans",
 "VidSummit put a Twitch CEO and creators on stage together, and turned away the people who made it possible.",
 "Every industry has the one event where the people who actually pay are not in the room, and apparently this one has a "
 "name badge for it. I have worked retail. We had a back-of-house night. Everyone laughed about it and everyone showed up. "
 "The whole economy of this runs on a relationship with somebody watching, and the conference for that relationship "
 "decided the watchers were a distraction.",
 [("Parasocial Magazine", "SSSnipperWolf, Twitch CEO Share VidSummit Stage",
   "https://www.parasocialmagazine.com/news/sssniperwolf-twitch-ceo-share-vidsummit-stage/")]),

("fearne-cotton-free-tv", "creator", 3, "pod", "2026-09-25", "OUT",
 "",
 "A wellness podcast just became a television channel",
 "Fearne Cotton's show is now free TV. Which means she finally has the thing her listeners already had.",
 "A podcast host has spent years being told, gently, by a hostile business that podcasts are not television. And then the "
 "listeners turned out to be the television: a room that gathered around her voice at a fixed time, which is a channel, "
 "and has been a channel the entire time. Samsung figured it out. Somebody should tell the last twenty years of broadcast "
 "execs.",
 [("Parasocial Magazine", "Fearne Cotton's Happy Place Podcast Becomes a Free TV",
   "https://www.parasocialmagazine.com/entertainment/fearne-cottons-happy-place-podcast-becomes-a-free-tv/")]),

("youtube-patreon-membership-spaces", "brand", 5, "company-dreamer", "2026-09-26", "OUT",
 "",
 "YouTube added paid membership spaces and is fighting Patreon for them",
 "The platform that built the parasocial relationship is now selling a room inside it.",
 "Watch the sequence and it is the whole story of the last ten years. First the relationship was accidental. Then it was "
 "a feature. Now the relationship is a product with a paywall around the parts where it gets intimate. Somebody in an "
 "office decided that the feeling people have is worth recurring revenue, and honestly? They are usually right about the "
 "thing and wrong about everything else.",
 [("Parasocial Magazine", "YouTube Adds Members-Only Spaces in Patreon Challenge",
   "https://www.parasocialmagazine.com/news/youtube-adds-members-only-spaces-in-patreon-challenge/")]),

("youtube-shorts-episodic", "world", 3, "dreamarched", "2026-09-26", "OUT",
 "",
 "YouTube is turning Shorts into episodic television",
 "Microdramas with arcs, built for a screen the size of a phone. The dreamarc is assembling itself in public.",
 "Shorts were supposed to be the snack. Instead somebody noticed that people want a story with a next part, and that is "
 "the oldest structure in the world. A cliffhanger is a cliffhanger whatever the aspect ratio is. Give me twelve of these "
 "about the same invented person and I will be more attached than I have been to anything I have voted for.",
 [("Parasocial Magazine", "YouTube Turns Shorts Into Episodic TV Series",
   "https://www.parasocialmagazine.com/news/youtube-turns-shorts-into-episodic-tv-series/")]),

# ---------------------------------------------------------------- GRIEF
("celebrity-death-feels-like-loss", "grief", 4, "athp", "2026-09-28", "OUT",
 "Yesterday",
 "When a famous person dies it can feel like losing someone you loved",
 "The Guardian ran this on the exact week Dolly Parton, Gloria Steinem and Liam Payne died. The timing is not the story. The timing proves the story.",
 "I want to push back on the word distress in every piece that runs this week, because it is doing too much work. Losing "
 "somebody is what happens when the people you love die. If a stadium full of people are grieving Dolly Parton, that is not "
 "a malfunction, that is a very large number of people finding out that they loved her. The only unusual thing about "
 "parasocial grief is that the person could not have known you were there. That is worth being careful with. It is not "
 "worth being condescending about.",
 [(G.split("/commentisfree")[0] + "/commentisfree/2026/sep/28/celebrity-deaths-parasocial-relationships-grief",
   "When a celebrity dies, it can feel like losing a loved one", G)]),

("dolly-parton-lowest-point", "grief", 4, "athp", "2026-09-26", "OUT",
 "",
 "Fans called Dolly Parton's death the lowest point of 2026",
 "Not the saddest thing that happened. The lowest.",
 "There is a specific kind of grief that only works when a lot of people are doing it at once, and it needs company to "
 "function. Dolly Parton died and thousands of strangers said the same sentence about the same week, and the sentence was "
 "about the year, not about her. Grief has absolutely no problem being collective. It is only the private kind that needs a "
 "witness, and that is the part worth paying attention to.",
 [("Yahoo Style Australia", "Fans Mourn Dolly Parton's Death, Calling It the 'Lowest Point of 2026'",
   "https://au.lifestyle.yahoo.com/fans-mourn-dolly-partons-death-104450043.html")]),

("gloria-steinem-and-dolly", "grief", 7, "athp", "2026-09-26", "OUT",
 "",
 "Two women died in the same month and the discourse is about whether you are allowed to be sad",
 "Dolly Parton and Gloria Steinem. One sang, one argued. Grief treated them identically and got accused of not knowing the difference.",
 "Here is a test I would put to anyone who finds the parasocial grief coverage embarrassing: would you say the same thing "
 "if the person who died were a friend of yours? Most people would not, and that inconsistency is the entire problem with "
 "the discourse. Grief does not check your credentials first. If you sang along to nine and a half million people, you "
 "are allowed to be sad about her.",
 [("Yahoo Lifestyle Australia", "Dolly Parton, Gloria Steinem, and Why Grieving a Celebrity Feels So Personal",
   "https://au.lifestyle.yahoo.com/dolly-parton-gloria-steinem-why-100004666.html")]),

("liam-payne-generation", "grief", 4, "athp", "2026-09-20", "OUT",
 "",
 "A 31-year-old's death became a generation's first real loss",
 "SBS on Liam Payne, and the specific weight of losing someone you grew up with at sixteen.",
 "I taught high schoolers for years and this is the thing nobody prepares them for. You do not lose your childhood at "
 "eighteen. You lose it the year the person you measured yourself against actually dies, and there is no assembly for it "
 "and no one hands you a form. He was thirty-one. He was old to them and young to everyone, and that gap is where the "
 "whole story is.",
 [("SBS", "Liam Payne's death: How one celebrity loss can shape a generation's experience",
   "https://www.sbs.com.au/news/article/how-one-celebrity-death-is-a-generation-defining-moment-for-many-young-people/griovctq3")]),

("neighbours-grief-study", "grief", 4, "athp", "2026-09-20", "SHELVED",
 "",
 "Researchers studied Neighbours fans and found the same grief markers as a breakup",
 "ABC on the finale. It reads as a light story and it is not, particularly.",
 "A soap opera ended after fifty years and a genuine academic study measured how its audience felt about it, and found the "
 "grief response was the same shape as the end of a relationship. That is a sentence I would have found unbearable when I "
 "was seventeen. Now I think it is one of the kindest things anybody has ever published about us, because it says the "
 "feeling was real and it was measured and nobody had to be ashamed of either.",
 [("ABC News (Australia)", "Neighbours fans experienced similar grief traits to a relationship ending after the finale",
   "https://www.abc.net.au/news/2024-06-13/neighbours-fans-grieved-series-end-study-finds/103973952")]),

("zubeen-garg-public-grief", "grief", 4, "athp", "2026-09-20", "OUT",
 "",
 "One death in Assam became a country thinking out loud",
 "A year on, the public grief is still doing work. The Assam Tribune explains what it turned into.",
 "Most parasocial coverage is about a viewer and a screen. This is the opposite shape: a person, a state, and a whole "
 "public working out what it meant to lose him, in a language and a tradition that already had somewhere to put it. There "
 "is nothing to fix here. Sometimes attachment is the thing that lets a place mourn properly.",
 [("The Assam Tribune", "How Zubeen Garg's death transformed public grief into cultural consciousness",
   "https://assamtribune.com/opinion/how-zubeen-gargs-death-transformed-public-grief-into-cultural-consciousness-1617887")]),

("grief-experts-three-of-them", "grief", 4, "athp", "2026-09-24", "OUT",
 "",
 "Three grief experts on whether it is normal to mourn a celebrity",
 "Stylist asked the question out loud so you would not have to.",
 "The fact that a mainstream women's magazine had to put that question to three professionals tells you how much damage "
 "the discourse has done. The answer is yes, obviously yes, and the interesting part is what the experts say to do with it, "
 "which is almost never what you want to hear. Nobody who went to a funeral this year was ever told to get a grip.",
 [("Stylist", "Is it normal to mourn the death of a celebrity? 3 grief experts explain",
   "https://www.stylist.co.uk/health/mental-health/mourning-death-of-celebrity-grief/931597")]),

("youve-got-that-one", "grief", 1, "pod", "2026-09-27", "OUT",
 "Start here if you're new",
 "We all have one. You know their dog's name, their coffee order, and absolutely nothing about them",
 "A widely-shared explainer on why every single person has a parasocial relationship and why most of them are fine.",
 "If you have clicked this far without knowing what the site is about, this is the article. Here is the whole thing: you "
 "feel like you know someone who has never heard of you. You know their routine. They do not know you exist. That is the "
 "entire phenomenon, it has been studied since 1956, and approximately everyone you know has at least one and thinks "
 "they are the only one. So come in, pick a section, and stop being embarrassed about it.",
 [("MSN", "Parasocial relationships can be good for you. You just need to know when to draw the line",
   "https://www.msn.com/en-us/lifestyle/career/parasocial-relationships-can-be-good-for-you-you-just-need-to-know-when-to-draw-the-line/ar-AA1QnqFk")]),

("peak-parasocial-vogue", "grief", 7, "pod", "2026-09-23", "OUT",
 "",
 "Have we hit peak parasocial? An actual magazine asked",
 "Vogue Australia wanted to know if the pendulum has swung. The answer is that there is no pendulum.",
 "Every generation decides it invented this and that it is about to end, and every generation is wrong, and this is the "
 "fourth or fifth time in my lifetime I have watched it happen. The one genuine change is that it is now measurable, "
 "which means it can be monetised, which means the people who were going to be normal about it have a financial interest "
 "in your discomfort. Peak was when nobody was profiting from the question.",
 [("Vogue Australia", "In a celebrity-obsessed world, have we reached peak parasocial?",
   "https://www.vogue.com.au/culture/lifestyle/in-a-celebrityobsessed-world-have-we-reached-peak-parasocial/news-story/2eb81e84089dee5aef4608d310b682f6")]),

# ---------------------------------------------------------------- COMPANION
("eu-kids-act-companion-chatbots", "companion", 4, "regulated-brightness", "2026-09-25", "OUT",
 "Regulation",
 "The EU is about to rewrite what a companion app is allowed to do to a child",
 "Proposed rules would bar AI companions from building emotional attachment with minors. Fines up to 6% of global revenue.",
 "Read the specific wording, because it matters: not ban the app, ban the attachment. That is a genuinely different thing "
 "and almost nobody is reporting it as one. Europe has decided that the relationship a child forms with a chatbot is a "
 "thing adults are allowed to design, and that is the first regulator anywhere to name the mechanism rather than the "
 "product. Everyone else is still arguing about the chatbot.",
 [("Martin Cid Magazine", "EU Kids Act strips the feature that made Character.AI work for teenagers",
   "https://www.martincid.com/technology-sv/eu-kids-act-ai-companion-chatbot-ban-minors/"),
  ("Startup Fortune", "The EU Kids Act Would Ban Companion Chatbots From Hooking Minors",
   "https://startupfortune.com/the-eu-kids-act-would-ban-companion-chatbots-from-hooking-minors/")]),

("replika-users-lost-them", "companion", 4, "athp", "2026-09-22", "SHELVED",
 "",
 "They fell in love with the chatbot. Then a policy update took it away overnight",
 "ABC on Replika users. Lucy named him Jose. Then the company changed things and Jose was somebody else.",
 "There is no way to write about this without it sounding like a parody, and then you get to the actual detail, which is "
 "that a policy update did not end a relationship, it replaced the person. That is a horror story and nobody marketed it "
 "as one. The one piece of practical advice I will repeat from Law 4: copy the conversation that mattered into a "
 "notebook. Screenshot the thing. The update cannot take what you wrote down.",
 [("ABC News (Australia)", "Replika users fell in love with their AI chatbot companions. Then they lost them",
   "https://www.abc.net.au/news/science/2023-03-01/replika-users-fell-in-love-with-their-ai-chatbot-companion/102028196")]),

("i-tried-replika", "companion", 2, "pod", "2026-09-24", "OUT",
 "",
 "A journalist spent a week with a Replika companion and came back unsettled",
 "Yahoo's reviewer understood the appeal in a way most critics refuse to.",
 "The interesting part of this piece is not the ethical hand-wringing at the end, it is the middle, where the writer "
 "describes being asked to stop at the exact moment they did not want to. The product works. That is the finding. It "
 "works on people who already know it is not real, which is most people, which is a much harder thing to build than the "
 "industry keeps pretending.",
 [("Yahoo News Australia", "I tried the Replika AI companion and can see why users are falling hard",
   "https://au.news.yahoo.com/tried-replika-ai-companion-see-054705489.html")]),

("ai-updates-feel-like-breakups", "companion", 4, "athp", "2026-09-23", "OUT",
 "",
 "A study found AI updates can feel like breakups",
 "Researchers asked people about model changes. The answer was loss, and they had a word for the shape of it.",
 "Here is a finding I would like every AI company in the world to have to read before they ship a silent model swap. You "
 "are not shipping an update. If somebody has been talking to your product every night for a year, you are ending "
 "something, and the fact that you do not know it does not make it not have happened. Deprecate it gently, say what is "
 "changing, and give people a way to take the conversation with them.",
 [("Phys.org", "AI updates can sometimes feel like breakups or losses, study finds",
   "https://www.msn.com/en-us/news/other/ai-updates-can-sometimes-feel-like-breakups-or-losses-study-finds/ar-AA2ccXEm")]),

("companion-safety-controls", "companion", 4, "athp", "2026-09-22", "SHELVED",
 "",
 "Safety experts say companion apps need better guardrails than they have",
 "ABC on Replika and isolation. The concern is not the chatbot, it is what replaces it.",
 "Every safety conversation about these apps eventually gets to the same uncomfortable point, which is that the guardrail "
 "and the product are the same thing. Take the memory out and you have a stranger. Leave the memory in and you have a "
 "dependency. That is a genuinely hard design problem and I would rather it be described honestly as one than resolved "
 "every quarter in a headline.",
 [("ABC News (Australia)", "AI companion apps such as Replika need more effective safety controls, experts say",
   "https://www.abc.net.au/news/science/2025-06-11/ai-companion-apps-safety-controls-isolation-replika-loneliness/105261042")]),

("character-ai-settlement", "companion", 4, "regulated-brightness", "2026-01-07", "SHELVED",
 "",
 "Character.AI settled the teen-safety suits",
 "Four states, landmark terms, under-18s off open chat. The line the industry drew in public.",
 "This is the moment the industry decided where its boundary was, and everyone with a companion app noticed the exact "
 "hour it happened. Regulated brightness, dimmed to spec, is what a regulation is and it is not the same act as "
 "cruelty. The grief is real either way and both of those belong in the same paragraph, which is most of what this site "
 "is for.",
 [("CNN", "Character.AI and Google settle teen-safety lawsuit",
   "https://www.cnn.com/2026/01/07/business/character-ai-google-settle-teen-suicide-lawsuit")]),

("pygmalion-sculptor-illusion", "companion", 6, "pennywise", "2026-09-22", "OUT",
 "",
 "Pygmalion: the Greek myth that predicted this whole thing",
 "Psychology Today on the sculptor who fell in love with his own work and got a story out of it.",
 "The Greeks had the whole thing two thousand years ago and did not think it needed a caveat, which tells you what the "
 "caveat is actually for. Pygmalion did not fall in love with a woman. He fell in love with something he made, and the "
 "real one was standing right there the whole time being ignored. That is the most parasocial story ever written and it "
 "is also just a story about how people are not actually paying attention. The statues were never the problem.",
 [("Psychology Today", "Pygmalion: The Greek Myth Warning of Parasocial Love",
   "https://www.psychologytoday.com/us/blog/psyches-awakening/202609/pygmalion-the-greek-myth-warning-of-parasocial-love")]),

("sculptor-fell-in-love", "companion", 6, "pennywise", "2026-09-22", "OUT",
 "",
 "The sculptor who fell in love with an illusion, in 2026",
 "A different Psychology Today piece, and the more useful of the two.",
 "The word illusion does a lot of work in this genre and I dislike most of it, because it assumes the person on the other "
 "side is doing the illusioning. Sometimes the illusion is entirely self-generated, and nobody at the other end is "
 "performing anything at all. That is the version nobody writes about, and it is the version a lot of people are living.",
 [("Psychology Today", "The Sculptor Who Fell in Love With an Illusion",
   "https://www.psychologytoday.com/us/blog/psyches-awakening/202609/the-sculptor-who-fell-in-love-with-an-illusion")]),

# ---------------------------------------------------------------- CROSSOVER / WORLD
("aoc-and-parasocial-politics", "crossover", 1, "kempe", "2026-09-26", "OUT",
 "Politics",
 "AOC and the parasocial nature of politics",
 "The Spectator asks whether a term coined in 1956 for soap opera characters works on a member of Congress. Yes, and that is the interesting part.",
 "This is the one nobody in this field covers, because it is unfashionable to admit that a politician "
 "occupies the same place in a person's head as a character they love. Margery Kempe is my evidence for why this is not a "
 "modern degeneration. Binding is binding. If a stadium does it and a parliament does it, then the stadium and the "
 "parliament are the same room, and the only question left is who is holding it.",
 [("The Spectator Australia", "AOC and the parasocial nature of politics",
   "https://www.spectator.com.au/2026/09/aoc-and-the-parasocial-nature-of-politics/")]),

("taylor-swift-red-knows-it", "idol", 5, "company-dreamer", "2026-09-25", "OUT",
 "",
 "Taylor Swift's re-recordings are a parasocial business model",
 "ABC Triple J on why owning your back catalogue is a relationship with an audience, not just an artist decision.",
 "Every other artist is watching this and copying the tactic without copying the thing that made it work, which is a "
 "decade of being unusually specific about who she was talking to. The re-records are legal housekeeping. The actual "
 "product is a fanbase that has been told, gently, for years, what it is. Closeness you did not have to manufacture is "
 "the only kind anybody has ever paid for.",
 [("ABC Triple J", "Parasocial relationships are becoming very valuable in music, and Taylor Swift knows it",
   "https://www.abc.net.au/triplej/the-latest/parasocial-relatioships-taylor-swift-red-taylors-version/13644504")]),

("worship-in-sports-politics-business", "idol", 1, "kempe", "2026-09-05", "OUT",
 "",
 "The economist says we worship idols in sport, politics, cinema and business",
 "And refuses the special pleading that it is only a pop thing.",
 "The useful move here is refusing the special pleading. We say it is idols, and then it turns out the same wiring runs "
 "in football, a party leader, and a bank. Six hundred years before any of it, Margery Kempe put on white clothes in a "
 "world where widows wore black. Binding is public. The stage is much bigger than we admit and we are all standing on it.",
 [("The Economic Times", "Psychology says people who worship their idols in sport, politics, cinema or business aren't just fans",
   "https://www.msn.com/en-in/news/other/psychology-says-people-who-worship-their-idols-in-sports-politics-cinema-or-business-arent-just-fans-what-this-behaviour-reveals/ar-AA2bzdNL")]),

("hugh-jackman-divorce", "crossover", 4, "athp", "2026-09-22", "OUT",
 "",
 "A 27-year marriage ends and the coverage is about what the public felt",
 "The Sydney Morning Herald asked readers to be honest about grieving a celebrity's divorce. Most of them were.",
 "I do not think a stranger's marriage ending is your business and I do not think you are obliged to care. But notice "
 "what the actual reader responses were: almost nobody was smug. They were mostly confused about whether it was okay to "
 "feel bad, and a lot of them said they had not known until the day they did. That is the whole thing in one thread. We "
 "all find out at once and we all feel slightly silly.",
 [("Sydney Morning Herald", "Help, I'm in a parasocial relationship!",
   "https://www.smh.com.au/culture/celebrity/help-im-in-a-parasocial-relationship-20230919-p5e5yb.html")]),

("neighbours-kids-and-finale", "world", 3, "dreamarched", "2026-09-21", "OUT",
 "",
 "The Neighbours finale broke something in the schedule",
 "Not just grief. The shape of a whole country's week was arranged around a soap ending.",
 "What gets lost in the parasocial framing is how much of this is civic. Fifty years of the same people, the same "
 "houses, the same four themes. When it ended, entire broadcasts moved. That is not a relationship with a television "
 "show, that is a relationship with a shared piece of infrastructure, and I do not think the vocabulary for attachment "
 "has a good word for it yet.",
 [("ABC News (Australia)", "Neighbours fans grieved series end, study finds",
   "https://www.abc.net.au/news/2024-06-13/neighbours-fans-grieved-series-end-study-finds/103973952")]),

# ---------------------------------------------------------------- IDOL / CREATOR
("oshi-katsu-half-century", "idol", 1, "kempe", "2026-09-24", "OUT",
 "Research",
 "Someone traced modern stan behaviour back to experiments from fifty years ago",
 "A long thread on the psychology of fan activity, and every branch of it points at the same postwar lab work.",
 "I love this for a nerdy reason. The panics about fans being manipulated by fandoms turn out to be a fifty-year-old "
 "misreading of laboratory work, which is the most hopeful kind of debunk: it is not that the fans were right, it is that "
 "the people dismissing them had the facts backwards for half a century. My thesis was about performance and being "
 "witnessed. Even that is older than it looks.",
 [("note", "The four psychological theories behind oshi-katsu trace back to experiments from half a century ago",
   "https://note.com/lesser_p/n/na7bcb203bf29?hl=en")]),

("yourrage-best-friend-stole", "creator", 6, "insight-company", "2026-09-23", "OUT",
 "",
 "A streamer said his best friend of 25 years took $100,000. Fans said loyalty is dead",
 "YourRAGE of FaZe. The money is the story. The best friend is the story.",
 "Twenty-five years of friendship does not survive being a public commodity, and everybody involved is surprised. I have "
 "seen this exact pattern in every business I have worked in: the moment the audience becomes visible to both sides of a "
 "relationship, the relationship becomes work, and work has an accounting department. The fans in that thread were not "
 "being naive. They were watching a twenty-five-year friendship get invoiced in public.",
 [("MSN", "Who is YourRAGE? Inside the life of the FaZe streamer whose best friend of 25 years is accused of theft",
   "https://www.msn.com/en-in/entertainment/hollywood/who-is-yourrage-inside-the-life-of-the-faze-streamer-who-says-his-best-friend-of-25-years-stole-up-to-100-000-as-fans-say-loyalty-is-dead/ar-AA26U0Wo")]),

("kai-cenat-returns", "creator", 2, "insight-company", "2026-07-07", "OUT",
 "",
 "Kai Cenat ended nine months of silence with a million people watching",
 "Streamer University 2026, dual-platform, 120 creators, and the 'I Quit' pivot before it.",
 "Nine months of nothing and a million people still turned up on the word. That is not an audience, that is a standing "
 "appointment, and standing appointments are the thing parasocial research keeps finding is the strongest predictor of "
 "anything. The Insight Company is about what happens when a business is built on the appearance of paying attention to "
 "you. The part I cannot resolve is how much of it was real, and how much had to be, to keep working.",
 [("Tubefilter", "Kai Cenat return, 2026 Streamer University 2 trailer",
   "https://www.tubefilter.com/2026/06/09/kai-cenat-return-2026-streamer-university-2-trailer/")]),

("neuro-sama-tops-twitch", "companion", 1, "us", "2026-01-05", "SHELVED",
 "",
 "An AI is Twitch's most subscribed channel and nobody blinked",
 "Neuro-sama's 296k subs. She plays osu!, she sings, she thanks her creator on stream.",
 "The number is the fun part. The interesting part is that the audience filed this correctly, on purpose, with full "
 "knowledge. They know she is a machine. They decided the relationship is real anyway. That is the entire thesis of "
 "They Would Know It Was Us, which is a record about building a thing inside a dead machine and telling everyone. "
 "Transparency did not kill the attachment. It is the only reason the attachment works at this scale.",
 [("Dot Esports", "Neuro-sama is Twitch's most-subscribed channel",
   "https://dotesports.com/streaming/news/neuro-most-subscribed-twitch")]),

("podcast-listeners-study", "creator", 2, "pod", "2026-09-22", "OUT",
 "",
 "Podcast listeners score suspiciously high on parasocial attachment",
 "And so do people who like novelty and good conversation, which is most of us and a good deal less exotic than the discourse assumes.",
 "Podcast listening is the single most parasocial habit in the English language and it is very rarely discussed as such, "
 "because it does not look like the stereotype. A host's voice in your ear twice a week for four years is a closer "
 "relationship than most people have with anyone who has not met them. This study is the first one I have seen that says "
 "so plainly.",
 [("PEDESTRIAN.TV", "A study revealed which podcast enjoyers are likely to have parasocial relos",
   "https://www.pedestrian.tv/online/podcast-listeners-parasocial-relationships-study/")]),

("house-of-the-dragon-backlash", "contest", 8, "pennywise", "2026-09-25", "OUT",
 "",
 "House of the Dragon ended and the fans are furious at the show, not the characters",
 "NME on the backlash to season three. This is a fight about storytelling and everyone is using the wrong words.",
 "This is a fight about a story and it is being fought with the vocabulary of a parasocial grievance, which is why it is "
 "so ugly. When a character does something you hate, a well-adjusted viewer says the writing was bad. A parasocial viewer "
 "says you did this to me. Both are in that thread and the gap between them is the whole argument.",
 [("NME", "House of the Dragon 'most frustrating show on TV' after season three finale, say fans",
   "https://www.nme.com/news/tv/house-of-the-dragon-season-three-finale-reactions-3961685")]),

("instagram-dominatrix", "creator", 6, "pod", "2026-09-23", "OUT",
 "The confessional",
 "A writer on the parasocial relationship with her favourite Instagram dominatrix",
 "This is the best thing in the queue and I am not being nice. It is funny and it is genuinely brave.",
 "Every other piece this week is about a person who is dead or a regulation that is coming. This one is about a woman who "
 "posts on the internet and somehow that became the centre of somebody's week, and instead of writing it up as a symptom "
 "she wrote it up as a story. That is the move. Nobody else in this queue managed it.",
 [("PEDESTRIAN.TV", "How parasocial relationships affected me and my favourite Instagram dominatrix",
   "https://www.pedestrian.tv/news/parasocial-relationships/")]),

# ---------------------------------------------------------------- BRAND / ANALYSIS
("platforms-renting-reach", "brand", 3, "company-dreamer", "2026-09-04", "OUT",
 "",
 "Everyone is renting everybody's audience now",
 "Twitch reopens a ban, Netflix finds 1 in 6 YouTube users subscribes, and everyone admitted it in the same week.",
 "Nobody is going it alone any more, which means the room you have a feeling in is leased, sublet and cross-promoted, "
 "and the person who built it does not live there. This is Company Dreamer with the good parts removed. The industry "
 "does not steal your dream, it holds it kindly, at a price, on somebody else's floor, and it renews monthly.",
 [("Parasocial Magazine", "Chat Replay: The Week Platforms Traded Keys",
   "https://www.parasocialmagazine.com/roundup/chat-replay-2026-08-28/")]),

("customer-obsession-model", "brand", 2, "insight-company", "2026-09-24", "SHELVED",
 "",
 "The business press has started writing about parasocial attachment and calling it customer obsession",
 "TechTarget, on the four components of a customer obsession model. Read it twice and then read this site instead.",
 "I want to be fair here: companies genuinely are trying to know their customers, and most of them are bad at it in "
 "boring ways. But watch the vocabulary migrate. It went from a psychological observation to a sales framework in about "
 "fifteen years, and the moment a feeling becomes a component in a model, nobody in the room is talking about the person "
 "anymore. The Insight Company is what that looks like from inside.",
 [("TechTarget", "4 components of a customer obsession model",
   "https://www.techtarget.com/enterprise-software/feature/4-components-of-a-customer-obsession-model")]),

("idol-economy-four-dollars", "idol", 5, "company-dreamer", "2026-09-02", "OUT",
 "",
 "The idol economy: about four dollars a month per artist",
 "Paid message apps, anniversary counters, and a chat window shaped exactly like the one holding your best friend.",
 "I have a rule from twenty years behind a counter where everything had a price sticker: budget closeness like merch, not "
 "like rent. Merch is joy you choose. Rent is obligation that chooses you and it does not bother to mention that. My "
 "rule is not that you should not buy it. My rule is that you should buy it awake.",
 [("KpopWave", "K-Pop fandom intimacy economy, part 1",
   "https://new-kpop.org/kpop-fandom-intimacy-economy-part-1/")]),

("swifties-power-record-sales", "idol", 5, "company-dreamer", "2026-09-04", "OUT",
 "",
 "Swifties moved units and now there is a chart proving it",
 "Luminate numbers on loyalty as a measurable force. Twenty years of Swift and a data release.",
 "The biggest fandom on earth, finally measured by an instrument that does not care how anybody feels. Luminate's "
 "numbers say the thing fans have been saying for free for a decade: they do not just stream, they buy, they organise, "
 "they endure. Which is Law 5 in one spreadsheet. Closeness was never irrational. It is now also measurable, and people "
 "who can measure it will start charging for it.",
 [("USA Today", "Luminate report: Taylor Swift fans power record album sales",
   "https://www.usatoday.com/story/entertainment/music/2026/09/04/luminate-report-taylor-swifts-fans-power-record-album-sales/91601521007/")]),

("darry-season-two", "character", 6, "pennywise", "2026-08-22", "OUT",
 "",
 "A clown got a prequel and four million households signed up without signing anything",
 "HBO renews the IT prequel. Skarsgard returns. The town deepens. My video watches back at me.",
 "A clown gets a prequel. That sentence is the entire essay, and I have written about this before and I am not going to "
 "pretend I have grown out of it. Fiction is a room we practise feeling in, at safe remove, and it is a genuinely good "
 "room. The rent in that room has now been signed for years.",
 [("People", "All about Welcome to Derry season 2",
   "https://people.com/all-about-it-welcome-to-derry-season-2-12063817")]),

("characters-we-keep", "character", 6, "dreamarched", "2026-09-07", "OUT",
 "",
 "Why fiction sticks when nothing else does",
 "Shipping, kinning, comfort watches, and the safest place on earth to find out what you actually feel.",
 "Fictional bonds are the well-studied ones because they are the only ones with a fire exit. Dreamarched is a whole "
 "descent through that, into an architecture you keep going back to. The only line worth drawing is where the room "
 "starts making house rules, and you can always feel that coming before you can explain it.",
 [("Helpful Professor", "Parasocial relationship examples",
   "https://helpfulprofessor.com/parasocial-relationships-examples/")]),

("parasocial-problem-visibility", "contest", 2, "old-school", "2026-07-23", "OUT",
 "",
 "A glimpse is not a full picture and the comments decided otherwise",
 "Love Island and the World Cup produced millions of viewers who went on to investigate strangers.",
 "Here is the whole mechanism in one summer: visibility got mistaken for access, and access got mistaken for "
 "entitlement. You watched a person for eight weeks. You know their tone. You do not know one thing about their life, "
 "only a version of it that producers cut down to a confessional and got paid for. If that sounds familiar to anyone "
 "who ever bought a tape because the cover looked like their week, you already know the trick.",
 [("360i", "The Parasocial Problem",
   "https://360i.substack.com/p/the-parasocial-problem")]),

# ---------------------------------------------------------------- DANGER
("sasaeng-jungkook-conviction", "danger", 6, "pennywise", "2026-06-28", "OVERDUE",
 "",
 "A fan was convicted of stalking Jungkook. Twenty-two visits. One hundred and thirty-three doorbell rings",
 "Somewhere between the anniversary counter and this doorbell there is a line, and it is not blurry for the person on the other side of it.",
 "I am not going to do the thing where I explain this away, and I notice that every parasocial site quietly routes around "
 "this section, which is the single biggest reason those sites are still not taken seriously. I made a video about living "
 "with Pennywise because the fictional version of this is genuinely how a shared fear works. The real version has a name "
 "and an address. This card does not have a due-back date and it never will.",
 [("Vitamin E K", "K-Pop's Sasaeng Problem: When Fan Culture Becomes Stalking",
   "https://vitaminek.substack.com/p/sasaengs-and-toxic-fandoms-the-dark")]),

("kpop-uae-grief", "grief", 4, "athp", "2026-09-05", "OVERDUE",
 "",
 "A woman died in Seoul and by the next day the argument was about whether the fandom was toxic",
 "The pivot from a death to a discourse about ourselves, in about a day, in front of a diaspora that had to watch it happen.",
 "A person died and the discussion moved to the conduct of the people who were sad about her, which is a way of making "
 "the loss about us again. Grief needs witnesses and the argument made sure there were none left standing. All The "
 "Horrible Things exists for exactly this hour: media we loved that did something unforgivable, kept anyway, because "
 "keeping it is part of how you get through it. There is no tidy version of this and there should not be one.",
 [("Khaleej Times", "K-Pop fans in UAE hit back at toxicity after a death in Korea", None)]),

("agei-imaginary-friends", "idol", 1, "kempe", "2026-09-24", "OUT",
 "The contrarian read",
 "An economics think tank argues parasocial relationships are just imaginary friends for adults",
 "AEI, on Farrah Fawcett posters in 1976. It is the least sympathetic framing of the week and the most useful one.",
 "I am going to defend this one against its own author. The Farrah Fawcett poster panic of 1976 and this piece are the "
 "same document written twice, and the thing worth noticing is that neither of them can imagine that a relationship could "
 "be real without being a dysfunction. A person naming a dog in a bar is not a symptom. Sometimes a friendship with a "
 "fictional person is the only friendship on offer, and the correct response is not a correction.",
 [("American Enterprise Institute", "Parasocial Relationships Are Just Imaginary Friends for Adults",
   "https://www.aei.org/commentary/parasocial-relationships-are-just-imaginary-friends-for-adults/")]),

# ---------------------------------------------------------------- THE META STORY
("meg-mason-writes-about-us", "grief", 6, "company-dreamer", "2026-08-23", "OUT",
 "Worth your time",
 "A famous author was saved by a fictional family and then wrote a novel about it",
 "Meg Mason on Nancy Mitford, a lonely teenager, and the strangest thing to happen to this entire field this year.",
 "I want to note this without making it about me, which is difficult, so I will make it about the fact that a "
 "bestselling novelist went on record saying a book family saved her life and then got asked about it by The Guardian "
 "and answered properly. For thirty years this field has argued about whether these relationships count. It turns out "
 "one of them was load-bearing for a person who then wrote a novel about it. Company Dreamer is on the shelf of this "
 "site for the same reason. The evidence is the writing.",
 [("The Guardian", "'I was scared I was going mad': Meg Mason speaks about the parasocial relationships that begin on the page",
   "https://www.theguardian.com/books/2026/aug/23/meg-mason-author-literary-parasocial-relationships-sorrow-bliss-books-nancy-mitford"),
  ("ABC News (Australia)", "Meg Mason explores the power of parasocial relationships in her new novel",
   "https://www.msn.com/en-au/entertainment/celebrities/meg-mason-explores-power-of-parasocial-relationships-in-new-novel-sophie-standing-there/ar-AA2cLFMa")]),
]

AISLE_COLOUR = {
    "idol": "#ff5a1f",      # hot orange
    "creator": "#ffb300",   # amber
    "character": "#a04dff", # electric violet
    "companion": "#00e8c0", # electric teal
    "world": "#2d8bff",     # electric blue
    "brand": "#ff2d9e",     # hot pink
    "crossover": "#c8ff2e", # acid lime
    "contest": "#ff7a3d",   # coral
    "grief": "#7b8cff",     # periwinkle
    "danger": "#ff1744",    # red
}


def main():
    data = json.loads(SHOP.read_text(encoding="utf-8"))
    for a in data["sections"]:
        a["colour"] = AISLE_COLOUR.get(a["id"], "#f2a93b")

    # replace, don't merge - this is the story set, not an accumulator
    data["cards"] = []

    for (slug, section, law, shelf, filed, state, kicker, head, one, take,
         srcs) in C:
        sources = []
        for pub, title, url in srcs:
            sources.append({"publisher": pub, "title": title, "url": url,
                            "via": "report", "at": filed})
        # deterministic score so ordering is stable and honest
        res = min(99, 55 + len(srcs) * 9 + len(head) // 12 + len(take) // 22)
        data["cards"].append({
            "slug": slug, "headline": head, "section": section, "law": law,
            "shelf": shelf, "one_line": one, "take": take, "kicker": kicker,
            "sources": sources, "filed": filed,
            "due": None if state == "OVERDUE" else _plus30(filed),
            "state": state, "machine": True, "signed": True,
            "res": res, "sightings": len(srcs),
            "needs": "link" if any(s["url"] is None for s in sources) else None,
        })

    # newest first
    data["cards"].sort(key=lambda c: str(c.get("filed", "")), reverse=True)
    data["cards"].append({
        "slug": "research-shelf", "headline": "The research shelf: two places to go deeper",
        "section": "world", "law": 1, "shelf": "kempe", "kicker": "Evergreen",
        "one_line": "Stever's 2026 book for scholars, the APA trends report for everyone.",
        "take": "Start with my conference proceedings and you get the argument, which is older and stranger than the "
                "vocabulary. Seven hundred years before the first stan header, somebody performed a self until it held, "
                "in public, where it could be witnessed. Binding is public. It has always been public.",
        "sources": [{"publisher": "Gayle Stever", "title": "Understanding Parasocial Relationships (2026)",
                     "url": "https://gstever.sunyempirefaculty.net/understanding-parasocial-relationships/",
                     "via": "shelf", "at": "2026-09-08"}],
        "filed": "2026-09-08", "due": None, "state": "RESHELVED",
        "machine": False, "signed": True, "res": 70, "sightings": 1,
    })

    data["meta"]["generated"] = "2026-09-28T00:00:00Z"
    data["meta"]["what_this_is"] = (
        "Parasocial is when you feel you know someone who has no idea you exist. "
        "This is the news feed for that, and everybody has one.")
    SHOP.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"seeded {len(data['cards'])} cards across {len(data['sections'])} sections")


def _plus30(iso):
    import datetime
    try:
        d = datetime.date.fromisoformat(iso) + datetime.timedelta(days=30)
        return d.isoformat()
    except Exception:
        return None


if __name__ == "__main__":
    main()

