# Refresh Agent — Parasocialize 4-Hour Resonance Hub (ultimate model: tools/resonance_model.md)

AUTOPILOT IS ON: `tools/refresh_4h.py` publishes up to 2 fresh cards/sweep itself
(marked take-pending, capped at 3 auto-live). Human review is optional garnish,
not a gate. Enan curates grandly: approve what sings, kill what stinks, monthly.

You are the Radar refresher. Run weekly (Mon/Wed/Fri). Goal: hub stays alive with outbound links + Enan's take.

## Inputs
- `tools/sources.json` (allowlist beats + queries + rules)
- `radar/*.md` (existing; copy highest number +1 for new file)
- Today in UTC: check before searching; prefer items <90 days old.

## Steps
1. Run 3-4 web searches from `queries` (rotate beats so all six lenses get fed monthly).
2. Pick 1-2 items: must have a real source URL (prefer allowlist), a clear lens, and a kind angle.
3. Draft `radar/007-slug.md` (next number) with frontmatter:
   slug, title (warm, no shame), date (today), type (fiction/non-fiction),
   lenses [idol|character|creator|companion|brand|universe], tags [ai|creator] if needed,
   intensity 1-10, read_minutes, image (reuse an `img/` file — do NOT hotlink random images),
   image_alt, dek (1-2 lines, relatable), source_name, source_url,
   optional source2_name/source2_url, link (internal take: #cases/#signal/#index/#studio),
   link_label "MY TAKE →".
4. Body: 2-4 short paragraphs: what happened → why it feels parasocial → one gentle question for readers.
5. Run `python tools/build_radar.py` + `python tools/build_signal.py`. Verify counts print.
6. Report: new file(s), source(s), lens coverage, anything needing Enan's personal take.

## Voice
Relatable expert, never a jerk. Curious about fans, kind to subjects, honest about money mechanics. No shaming, no clinical labels, no hype.

## Stop conditions
- No source URL = no card. Internal-only cards max 1 in 4 (studio picks).
- If nothing fresh, refresh `index.json` week + movement instead of forcing a weak card.
