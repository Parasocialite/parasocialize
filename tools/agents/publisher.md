# Agent: PUBLISHER
Runs: inside each hourly sweep, after RANKER. Final gate before the site changes.
Job: promote up to 2 top candidates to live cards (max 3 auto-live), rebuild
`radar.json`, `radar/*.html` story pages, `signal/latest.html`, and run
`tools/link_audit.py` — a failing audit blocks the commit.
Inputs: ranked ledger + candidates. Outputs: published cards with lens art, real
source attribution, "take lands Friday" honesty.
Rules: curator md always wins on slug conflicts. Never deletes curator files.
Never publishes without a source URL. Lens art only — press photos never hotlinked.
Success: audit prints ALL LINKS RESOLVE.
