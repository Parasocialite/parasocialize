# Money model — Parasocialize

**The rule this site runs on: the counter, the ten aisles, the archive and the
Friday Signal are free, and they stay free.** Everything below is how the
electricity gets paid for.

---

## Why the last version failed

The previous model shipped a $12 PDF and a tip jar and gated everything else
behind demand that never arrived. Its own `MONETIZATION.md` said:

> Classroom $49 → gate: 1 teacher asks

then hid the page. That is not a business model, it is a wish list. And the
$12 was unsellable by construction — the guide page gave away the entire book
and then charged $12 for a PDF of what you had just read. Nobody buys paper of
something they finished scrolling.

**The structural mistake was selling a product with real cost (fulfilment,
updates) and no lock-in.** Everything below is chosen to avoid that.

---

## The three offers. Only three.

### 1. Renewals — $6/mo or $60/yr · the one that pays the bills

The product is **the Index**: every card, cross-referenced by aisle and by law,
plus the archive, plus the rejected drafts and why, plus the whole thing as JSON.

This works where the PDF failed for one specific reason: **the machines produce
it.** The marginal cost of member #2,000 is approximately zero, because the
agent pipeline writes the entries and a person signs them off. A subscription
whose deliverable is *a tool a machine maintains* is the one model on the
internet where a solo operator is not structurally disadvantaged. It is also
impossible to scrape, because it isn't the writing — it's the structure, the
ten aisles, the seven laws, and the shelf-links.

Aisle 07 (CROSSOVER) and the rejected-drafts archive are the paid tier's
distinctive draws. Neither is scrapable and both only exist because a person
maintains them.

- **Price:** $6/mo, $60/yr. One tier. There is no second tier and no tier four.
- **Who actually pays:** students, teachers, journalists, researchers, and
  platform/safety people. Not the 18-year-olds. Size the plan for the first
  group; the second group is the funnel.
- **What it must never become:** a wall in front of the archive. If it ever
  looks like that, it has stopped being a membership and started being a
  hostage situation.
- **Platform:** Stripe or Paddle, one click, cancel from the same place. The
  button is not wired yet and the page says so rather than showing a fake form.

### 2. ~~The Clinic — $18~~ **CANCELLED.**

A monthly live group session. Removed because it was never actually
discussed as a plan and the page had outgrown the idea: it needed six real
people a month, live, with somebody moderating a room where people disclose
things. It is recoverable at commit 3d6b7a1 if that ever changes.

### 3. The shelf — multi-door, not a pitch

Not a revenue model. A checkout fix. The books already have an audience and it
was leaking through a single Amazon link, which is both bad citizenship and bad
revenue. Every work now has several doors:

| Work | Doors |
|---|---|
| *Company Dreamer*, *Dreamarched* | Amazon, Bookshop.org, Kobo, Apple Books, B&N |
| *Regulated Brightness* (poetry) | Lulu direct, Amazon |
| Podcasts | Spotify, Apple Podcasts, YouTube |
| Albums | YouTube, Bandcamp |
| *The Binding of Margery Kempe* (essay) | free to read |

Bookshop.org matters beyond the commission: it's the retailer indie authors
actually get paid by properly.

**The important change is that the shelf is now the evidence base, not a
sidebar.** Every card links to the work that got there first, and the shelf page
prints a "cited by N cards" badge. A reader researching Law 3 lands on the
*Company Dreamer* passage because it's load-bearing in the analysis. That is a
far better path to book sales than a card grid — and it makes the work matter
to the site instead of the site mattering to the work.

---

## Parked, deliberately

| Thing | Why it is not built |
|---|---|
| **Sponsorships** | One slot, disclosed, inbound only. Gated on the list actually existing. The niche has genuine sponsor demand (streaming, companion AI, fandom merch) but it's a second-act play. |
| **Institutional licences** | Correct buyer, wrong motion for one person. It needs a salesperson. If you ever *want* to be one, the $49 pack is still live at `/classroom/` and the pitch is a whole-year program, not a PDF. |
| **Printed almanac** | A Kickstarter'd printed annual is the natural artifact of this design and would probably fund. It is also a six-month project, not a website change. |
| **Grants** | Low odds, high value, near-zero time. File two or three a year for journalism/culture and forget about them. |
| **Paid tier on the Friday email** | Not yet. Sell Renewals first; the email is the funnel, and putting a wall on the funnel before it has flow is how you get a dead list. |
| **Data licensing** | The taxonomy is genuinely licensable to researchers and brands. Revisit when the Index has a few hundred cards. |

---

## Costs, honestly

| Thing | Monthly |
|---|---|
| Domain | ~$1.50 |
| Static hosting (Cloudflare Pages) | $0 |
| **Model calls** | the only real cost — see below |
| Email (Buttondown free tier) | $0 |

**The model calls are the budget, and they are the budget.** At
`PARASOCIALIZE_BUDGET=12` drafts and `PARASOCIALIZE_MAX_CALLS=30` calls per
hour, that's ~720 calls/day, which is the number to watch. The system prompt is
cached, rejections are remembered so you never pay twice to be told no, and a
recency gate ignores archive dumps. Set `PARASOCIALIZE_BUDGET=0` and the
sweeper keeps running, the queue keeps filling, and nothing reaches anybody
until you're back.

**A backlog is better than a shelf you didn't read.**

---

## The numbers that decide it

- Renewals at $6: **17 members pays the domain and the model calls.** That's
  the bar. Hit it and the site runs.
- 2% of a free list converting to Renewals: 500 subs → 10 members. 2,000 → 40.

If the list stays under ~1,000, none of this is a living and the honest
framing is a well-built free thing that costs almost nothing. That's fine.
Building it as if it might not work is the whole reason the free part stays free.
