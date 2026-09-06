# Agent: SWEEPER
Runs: every hour (cron), first stage of `tools/refresh_hourly.py`.
Job: fetch Google News RSS for 3 rotating queries (from `tools/sources.json`).
Inputs: queries, allowlist tiers. Outputs: raw hits (title/link/source) handed to DRAFTER.
Rules: 15s timeout per feed; a missed feed is logged, never fatal. Never writes cards.
Success: ≥1 feed hit, or clean decay-only sweep when the net is quiet.
