# AGENTS.md

Parasocialize: a source-honest encyclopedia and video channel about one-sided
relationships. 175 entries, 417 relations, 267 generated pages.

## The rule that outranks everything

**Never invent a citation, a date, an attribution or a quotation.** A visible gap
is correct; a plausible-looking source is a defect. Every source carries
`status: retrievable | verified`. `retrievable` means "a reader can open this and
find it" — NOT "the full text was read". Do not upgrade a status without reading
the source. If an entry cannot be sourced, leave it unsourced and say so.

Entries that are **the site's own argument** carry `provenance: thesis` and take
no citation at all. That is not a gap. Currently 13 of these. Adding one is
legitimate; the test is whether the claim has any external referent to attach a
source to.

## Commands

```powershell
python tools\build_cards.py     # generate site from data/
python tools\build_deploy.py    # build dist/ incl. _redirects and 404.html
python tools\link_audit.py      # MUST pass before every commit
python tools\make_zip.py        # reproducible archive -> Desktop
python tools\add_source.py --apply-provenance
python tools\episode.py eliza   # render episode; preserves voice/*.wav
```

Cite sources via `tools\add_source.py`, not by hand-editing JSON. It validates,
de-duplicates, refuses thesis entries, and recomputes provenance. One entry per
call is fine; batches of 8-20 are normal.

**`link_audit.py` is a gate, not advice.** Read its output before committing.
Chaining it with `;` and committing anyway once put a failing commit in history.

## Traps we have already hit

- **`seven\s+past` matched "seven pastors."** Cadence patterns need `\b` and need
  a *process verb* adjacent to the interval. A bare "every hour" is ordinary
  English. Probe both directions before trusting a regex change.
- **`is_sourced()` is `bool(e.get("sources"))`, so thesis entries counted as
  unsourced** and inflated the backlog by 13. The board now excludes them. If the
  three numbers ever stop reconciling to 175, suspect this class of bug first.
- **Report a defect once, verified.** A claimed arithmetic mismatch was reported
  twice before being checked against the data. It was a misparse of my own
  verification regex; the arithmetic had been correct throughout.
- `tools/episode.py` writes `ffmpeg.txt` with the `-vsync` note inline on the
  command line, so literal copy-paste truncates the command. Use `HOWTO.txt`.
- **The frame sampler was a no-op, and it was silent.** `render_scenes` captures
  four instants per scene by shifting `animation-delay` by `-t`, but it was
  shifting only the backdrop's CSS string — which contains no `animation-delay`
  at all. `backdrop.py` puts all 65 of its delays in inline `style=""`
  attributes on SVG elements, and `iyi.py` emits three more in its own `<style>`.
  The regex matched nothing, so all four HTML files per scene hashed *identical*:
  36 "motion frames" were 9 images. A second, quieter half: a negative delay
  leaves the animation *running*, so frames drifted by whatever the compositor
  clock did — ~10,000px between renders of one file. The freeze needs both the
  offset **and** `animation-play-state:paused`. Verify any change here by
  hashing the generated HTML, not by looking at the storyboard: the storyboard
  reads one frame per scene and cannot show this.

## Architecture

- `data/encyclopedia.json` — the single source of truth. 175 entries.
- `tools/build_cards.py` — all page generation, the citation board, section
  fronts, and the entry Watch block (renders only when a real `video` URL exists).
- `tools/build_deploy.py` — `dist/`, `/e/<id>` redirects for all 175 entries.
- `tools/add_source.py` — citation insertion + the THESIS set.
- `tools/mascot.py`, `tools/wordmark.py` — iYi. Asymmetric per-eye rig.
- `tools/episode.py`, `tools/backdrop.py`, `tools/iyi.py` — video.
- `COVERAGE-MAP.md` — domain sweep and the 22-entry work queue in three tiers.

Deploy by uploading `dist/` **directly** to Cloudflare Pages. Do not upload the
extracted Desktop folder, and do not extract the archive. `episode/` is
deliberately excluded from the deploy tree.

## iYi

Always **iYi**, lowercase `i` on both sides. Cute first. Reactive but restrained.
No text bubbles. Heart eyes only for an affectionate beat, never the base
character — this is why the episode end card uses `watch`, not `love`.

Video strategy: the bond comes from **continuity, not surveillance**. iYi is
"the clerk", admits it has a job, carries state across episodes, and must never
claim to remember an individual viewer. No synthetic depictions of real people.
Human voice only; no dataset sale.

## Current state

```
140 sourced | 22 not yet stood behind | 13 thesis   = 175
34 of 417 edges land on something unchecked
137 of 292 sources have a locator
```

Board must reconcile to 175. `add_source.py` is authoritative.

## Open work

1. **Publish one episode.** Nothing links anywhere until a video is live. Three
   episodes are rendered but unpublished. Blocked on human voice in
   `episode/*/voice/NN.wav` (nine per episode).
2. **Landscape defects**, both confirmed by measurement, neither yet fixed.
   - The backdrop stops at x=1080: `backdrop.py` hardcodes `W, H = 1080, 1920`
     and the CSS pins `.bg svg` to `width:1080px`, so in a 1920x1080 frame it
     covers the left half and leaves a hard vertical edge.
   - The type does **not** currently overflow — it *under*-fills. `scene_html`
     writes `g.type{font-family:...}` but puts `class="type"` on the `<svg>`,
     so the rule matches nothing and every line renders in the browser's default
     serif. Measured on one 34-char landscape line: as shipped the ink ends at
     x=1079; with `g.type`→`.type` it ends at x=1272, i.e. **92px past** the
     1180 measure. The perceived "clipping" was coincidence — the narrow
     fallback face happens to end each line where the backdrop edge is. Fixing
     the selector is what *creates* the overflow, and `_fit` will need
     re-measuring too: it assumes 0.47em per character and the real face
     measures 0.523em. Do both in one change, or the landscape gets worse.
3. **Entry Watch label** is hardcoded "fifty-second version" — wrong for 53-64s
   episodes. Make it data-driven or duration-neutral before publishing.
4. **Tier 1 citations**, resting on inference rather than evidence: `dere`
   (Dionne Warwick, reciprocal fan mail — the counter-example the site needs),
   `the-neighbour`, `the-transfer`, `the-coach`, `the-dog`.
5. **Lane re-seed** analysed, unapplied: 30 additions, 17 corrections, 0 removals.
   Needs approval.
6. **`trading-stamps`** dated 1880; sources give first use 1890-91. Needs a
   decision.
7. **Membership tier** has no payment processor and no authentication. Do not
   describe it as an automated service — the sweeper has never run.

## Deploy note

`dist/` must be re-uploaded after each build. It is routinely ahead of
production.