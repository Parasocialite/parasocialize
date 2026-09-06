# Agent: RANKER
Runs: inside each hourly sweep, after DRAFTER.
Job: apply decay (−0.5 quiet) and boosts (+2 fresh sighting, cap 100), recompute
states (FLASHING/PRESENT/LINGERING/FADING/CLASSIC), order the grid, rebuild
`data/ticker.json` (max 6 phrases, never FADING).
Inputs: ledger + sightings. Outputs: ordered slugs, ticker phrases.
Rules: classics pinned (max 2). A quiet story cools ~12 points/day. Scores only —
never words, never cards.
Success: grid order + ticker written, sweep counter incremented.
