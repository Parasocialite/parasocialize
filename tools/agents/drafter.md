# Agent: DRAFTER
Runs: inside each hourly sweep, after SWEEPER.
Job: clean titles (strip outlet suffixes, normalize quotes), guess lens, dedupe at
55% word overlap against ledger + grid, skip junk domains (video reshares).
Inputs: raw hits. Outputs: sightings matched to ledger stories + `data/candidates.json`
for genuinely new finds.
Rules: no source URL = no draft. One story, one lens. Kind framing only.
Success: boosts filed, candidates queued with lens + outlet attribution.
