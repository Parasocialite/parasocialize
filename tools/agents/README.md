# Agents — chain of command

Every hour, minute :07 UTC (`.github/workflows/refresh-hourly.yml`):

SWEEPER → DRAFTER → RANKER → PUBLISHER

- SWEEPER finds. DRAFTER cleans. RANKER scores. PUBLISHER ships.
- No agent publishes without a source URL. No agent touches curator md files.
- `tools/refresh_hourly.py` executes all four stages in order; stage headers in
  the code name the responsible agent.
- Grand curator (Enan): upgrade singing auto-cards to full md takes, kill-list
  stinkers by slug, write Case Files when moved to. ~30 min/month, optional.
