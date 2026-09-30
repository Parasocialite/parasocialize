# The counter — how the site actually works

A rental shop at night. Dark room, one warm lamp, card stock. Machines read the
net and draft a card; a clerk signs them and they go on the shelf.

```
   SWEEPER  ->  CLASSIFIER  ->  RANKER  ->  QUEUE  ->  [ YOU ]  ->  SHELF
   finds     reads it,      dedupes    files     signs     published,
   ~100/hr   judges it,      scores     drafts    or bins
             names the      velocity
             section, the
             law, the
             shelf
```

**Nothing reaches the public shelf without a person deciding it should.** That
is the whole design. A model that gets this wrong is a nuisance. A model that
gets this wrong *published* is the reason everyone stops trusting the site, and
trust is the only asset that matters here.

---

## Why the last version of this was not an agent system

It looked like one. It was a keyword scraper wired to a hand-typed list:

- 6 Google News queries against 14 allowlisted domains. **Google News RSS
  returns `news.google.com` redirect URLs, so the allowlist never once
  matched.** Dead code.
- **No model anywhere.** "Resonance" was a hand-tuned formula, and the values
  in the ledger were too round to be computed.
- `data/candidates.json` was `[]`. The drafter had never produced a card in the
  entire life of the pipeline.
- The 8 cards on the homepage were hand-written. The sweeper's real output was
  raw headlines that got swept in and never became anything.
- `last_seen: 2026-09-06`. The hourly job had been dead for three weeks.
- The RSS linked all eight items to `/#radar` — the homepage.
- `MONETIZATION.md` gated every offer behind a demand that never arrived.

**And the deepest problem was structural, not a bug:** keyword search for
"parasocial" can only find pieces that already use the word parasocial. It can
never reach attachment in a World Cup, a court docket, a football club or a
classroom. That needs a model that can read the story.

---

## Sources, and why Bing

`tools/feeds.json` holds the verified-working set.

**Bing News RSS is the backbone, not Google News.** Bing wraps the real
publisher URL in a `url=` query param; unwrap it and you get the actual domain,
which is what makes the tier table mean anything. Google News gives you
`news.google.com` for every story, which is precisely the bug that killed the
old sweeper.

**One query per section.** This is the load-bearing idea:

```json
"crossover": "teacher students parasocial attachment school",
"danger":    "sasaeng stalking idol fan arrested doxxing",
"grief":     "celebrity death fans grief mourning public"
```

Each section is swept on its own terms instead of hoping one keyword finds
everything. It is also the only reason **Section 07 (CROSSOVER)** is not empty —
the attachment to a teacher, a landlord, a local news anchor, an AI assistant
that knows your name, or a sports coach you've watched for nine years is real,
happens constantly, and is invisible to a fandom site.

The query's section is passed to the model as a **hint**, turning a guess into a
check.

### Reddit is off, and here's why

Reddit blocks datacenter IPs, which is what GitHub Actions runs on. A plain
request gets `403`; the `.rss` endpoint returns an identical ~321KB anti-bot page
for every subreddit with zero entries, so it looks like it works and isn't.

To switch it on: create a free OAuth app at `reddit.com/prefs/apps` (type:
script), then add `REDDIT_CLIENT_ID` and `REDDIT_CLIENT_SECRET` as repo secrets.
Until then the sections lean on the Bing queries, which is why they're broader
than the old site was.

### Other feeds

`parasocialmagazine.com`, three Substacks, and optionally Hacker News via
Algolia (no key needed). Every one of these was verified returning 200 with
real items on 2026-09-28.

---

## Cost controls, in order of how much they save

1. **Recency gate** (`PARASOCIALIZE_RECENCY_DAYS=6`) — archive dumps are not
   news. Biggest single saving.
2. **Rejection memory** (`data/binned.json`) — a story the model already turned
   down is never paid for twice. Keyed on a hash of the title's significant
   words.
3. **Dedup before any tokens** — 55% word-overlap against the shelf and the
   current queue.
4. **`PARASOCIALIZE_BUDGET`** — caps *drafts* (12/hr default).
5. **`PARASOCIALIZE_MAX_CALLS`** — caps *total* calls including rejections
   (30/hr default). This is the real ceiling on the bill.
6. **Cached system prompt** — the voice brief and the schema are cacheable, so
   repeat calls are cheap.

**Without a key the sweeper still runs.** It files candidates raw and
un-lensed, flagged `no lens` on the desk, so nothing is silently dropped. The
site stays up and the queue keeps filling.

---

## Files

| Path | What it is |
|---|---|
| `data/shop.json` | **The single source of truth.** sections, laws, shelf, cards, queue. Hand-edit here. |
| `data/queue.json` | Drafts awaiting signoff. Written by the sweeper, read by `/desk/`. |
| `data/sweep.json` | Run telemetry: feeds ok/failed, candidates, drafted, rejected, model. |
| `data/seen.json` | URL memory. **Must be written or every run re-does everything.** |
| `data/binned.json` | Rejection memory. Same reason. |
| `tools/feeds.json` | Sources, tiers, junk filter, per-section Bing queries. Edit here, not in code. |
| `tools/counter.py` | The sweeper. Stdlib only, no pip. |
| `tools/build_cards.py` | Renders `radar/*.html`, `section/`, `shelf/`, `radar.xml`, `sitemap.xml`, `data/index.json`. |
| `tools/link_audit.py` | Fails on 404s, a feed pointing at the homepage, a stale sweep, or a queue nobody is clearing. |
| `tools/check_css.py` | Catches classes used in HTML that the stylesheet never defines. |
| `desk/index.html` | The signoff queue. `noindex`. |

### Run it

```bash
python tools/counter.py        # sweep, classify, file drafts
python tools/build_cards.py    # redraw every page
python tools/link_audit.py     # should say "all good"
```

---

## Signing off a draft

1. Open `/desk/`.
2. Edit the object in `data/queue.json`: set `"state": "signed"`, fill in
   `section`, `law`, and `shelf` if the model left them null.
3. Move it into `cards` in `data/shop.json` with a `slug`, `filed`, `due`
   (≈30 days out), and `state`. Give it a real `sources[0].url` — a card with
   an unresolved link is rendered with a `NEEDS LINK` stamp on purpose, and
   that's a thing to fix, not to leave.
4. `python tools/build_cards.py`.

### States

| State | Meaning |
|---|---|
| `OUT` | On the rack, `due` date live. |
| `SHELVED` | Aged out of the rack, still on the shelf. |
| `RESHELVED` | Evergreen. Case Files, the laws, the research shelf. |
| `OVERDUE` | **Never decays.** Section 10 and hard grief. No due date, big red stamp, torn left edge. |

`OVERDUE` is used deliberately and sparingly. The counter's job is partly to
remember the things that got worse, and a shelf that quietly ages out a sasaeng
conviction is a shelf with a convenient memory.

---

## The tone rules, enforced in the prompt

- **Never pathologize a reader.** No "unhealthy", "creepy", "addiction",
  "obsessed" in a `one_line` or a `take`. Attachment is real. A lot of it is
  just love with a bad angle on it.
- The take is 2–3 sentences, first person, and must **land somewhere** rather
  than summarise the news.
- `one_line` reads like a library card. No clickbait, no question marks.
- A big false-negative is better than a shelf of cards that are really just
  news. The site is only worth anything if it stays narrow.

---

## The shelf is the evidence

Every card carries a `shelf` id — the novel, essay, album, podcast or video
that got there first — and the card page prints *why*. That is the second
purpose of the site doing actual work: the work isn't merchandise, it's the
first draft. A reader following Law 3 lands on the *Company Dreamer* passage
because it's load-bearing in the argument.
