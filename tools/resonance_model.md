# Resonance Model — Parasocialize 4-Hour Hub

6 sweeps/day (00/04/08/12/16/20 UTC). Stories don't expire by age — they linger by resonance.

## Score (0-100 per sweep)
resonance = 0.4*base_intensity*10 + 0.3*velocity + 0.2*source_weight + 0.1*discussion
- base_intensity: curator 1-10 from radar md (×10).
- velocity: sightings this 24h across feeds (0=unseen, 25=3+ hits, capped 30).
- source_weight: allowlist tier (expert/reportage 20, analysis 14, fandom press 8, aggregator 4).
- discussion: comments/posts evidence if present (0-10).

## States (badges on cards + ticker)
- FLASHING (sweep age <24h, resonance ≥70): new heat, top of grid, ticker lead.
- PRESENT (resonance 45-69 or age <72h): normal grid order by resonance.
- LINGERING (resonance ≥55 and age >72h): "still resonating" badge, stays pinned mid-grid.
- FADING (resonance <45 and age >72h): drops to archive, leaves ticker.
- CLASSIC (curator pins: Kempe, Blockbuster, Dream canon): never fades, max 2 slots.

## Decay (applied every sweep)
- resonance -= 3 if no new sighting (stories cool without fresh links).
- resonance += 8 per new independent source sighting (cap 100).
- base_intensity can be re-scored by curator anytime (overrides gradually: new_base blends 50%).

## Grid composition (6 slots, rebuilt each sweep)
1. Top FLASHING or highest resonance (outside voice preferred).
2. Highest AI/companion (fastest lens, always represented if ≥40).
3. Highest idol/creator (people beat).
4. Studio pick (Enan's shelf, rotates among books/music/pods; labeled FROM MY SHELF).
5-6. Next two by resonance (any lens; lingerers welcome).

## Ticker (auto-built, max 6 phrases)
Order: FLASHING first, then LINGERING marked "STILL RESONATING", then top PRESENT.
Format: `PHRASE ●` uppercase, ≤34 chars each. Never shows FADING.

## Index (weekly, Fridays)
Top 5 by peak resonance that week (not current) — rewards lingerers, not just flash.

## Human gates (keeps voice kind)
- Auto-sweeps may ADD sightings + adjust scores + rebuild grid/ticker/radar.json.
- Auto-sweeps may NOT publish new cards with new titles/images (those stay drafts in `radar/_drafts/` for Enan/agent review).
- New cards publish on Mon/Wed/Fri review (2 min): move draft → numbered md → rebuild.

## Files
- `data/signals.json`: ledger (one record per story: slug, title, lens, base_intensity, resonance, sightings[], first_seen, last_seen, state, source_url, image).
- `tools/refresh_4h.py`: sweep runner (fetch Google News RSS × queries, match allowlist, update ledger, rebuild radar.json top-6 + ticker).
- `radar.json`: derived view (never hand-edited; built from ledger + studio rotation).
- `radar/*.md`: curator takes (stable URLs for humans; refresh script never deletes these).
