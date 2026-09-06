# Resonance Model — Parasocialize Hourly Hub

24 sweeps/day (every hour, minute :07 UTC). Stories don't expire by age — they linger by resonance.

## Score (0-100 per sweep)
- base: curator intensity 1-10 from radar md (×10), or 70-80 for auto-published finds.
- velocity: +2 per fresh independent source sighting in a sweep (cap 100).
- source_weight: allowlist tier sets the base (trusted outlet 80, otherwise 70).

## States
- FLASHING (age <24h, resonance ≥70): new heat, ticker lead.
- PRESENT (resonance 45-69, or young): normal grid order by resonance.
- LINGERING (resonance ≥55 and age >72h): "still resonating", stays mid-grid.
- FADING (resonance <45 and age >72h): leaves the grid, stays in archive.
- CLASSIC (curator shelf pins, max 2): never fades.

## Decay (applied every sweep, tuned for 24 sweeps/day)
- resonance −= 0.5 with no fresh sighting (a quiet story cools ~12 points/day).
- resonance += 2 per fresh independent sighting (cap 100).
- A story needs roughly one fresh link every 4 days to hold its score.

## Grid (rebuilt every sweep)
- FLASHING first, then resonance order; CLASSIC pins (max 2); auto-published max 2.
- FADING drops out; emptied slots refill from auto-publishes and curator md.

## Autopilot publishing (no human required)
- Sweeper promotes up to 2 fresh finds/sweep (max 3 auto-live): cleaned title,
  guessed lens, deduped at 55% word overlap, junk domains skipped.
- Auto cards arrive with lens art, real source attribution, and "take lands Friday".
- Curator md files are never touched; curator content always wins on slug conflicts.

## Ticker (auto-built, max 6 phrases)
FLASHING first, LINGERING marked, then top PRESENT. Never FADING.

## Index (weekly)
Top 5 by peak resonance that week — rewards lingerers, not just flash.

## Grand-curator role (~30 min/month, optional)
Glance at the grid. Upgrade a singing auto-card to a full md take. Kill-list a stinker
by slug. Write a Case File when moved to. Everything else runs itself.

## Files
- `data/signals.json`: ledger (slug, lens, base_intensity, resonance, sightings, first/last seen, state, card fields for auto entries).
- `tools/refresh_hourly.py`: the sweeper (fetch → match → autopublish → decay → rebuild).
- `tools/agents/`: role definitions (sweeper, drafter, ranker, publisher) executed by the runner.
- `radar.json`: derived grid view (built from md + ledger, never hand-edited).
- `radar/*.md`: curator takes (stable URLs; refresh never deletes these).
