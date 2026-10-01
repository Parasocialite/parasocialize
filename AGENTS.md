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
python tools\verify_measure.py eliza shipping vshojo   # type vs its measure
python tools\measure_type.py    # regenerate tools/type_metrics.json
```

`verify_measure.py` is a **gate for anything touching typography**. It renders
each scene twice, once with a given line removed, and measures the ink of that
line by differencing the two — so it reads pixels, not the wrap arithmetic. It
diffs within one document on purpose: differencing two renders of the same file
lights up on animation noise and measures the wrong thing. Confirm it can still
fail before believing a clean report.

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
- **Naming a font in CSS is not evidence the font loaded.** This bit three
  times in one session, each time producing numbers that looked fine. The
  @font-face pointed at `../../brand/fonts/` from a directory where `../../` is
  `episode/`, so the path did not exist, Chrome fell back, and the metric tool
  measured the fallback for a whole run. **The tell was weights 600 and 800
  measuring identically to four decimals — two different files cannot have
  identical metrics.** `tools/measure_type.py` now asserts against that, and
  computes its path rather than hardcoding it. If a measurement ever looks
  suspiciously clean, the font did not load.
- **A line count cannot detect an unbreakable word.** `parasocialize.com/e/
  shipping` is one token, so `_wrap` returns one line at *every* size and any
  maxlines test passes at every size — including the ones that overflowed by
  26px. `_fit` now checks line width as well as line count.
- **Only the weights you have files for.** The end card asked for `font-weight:
  700`, which is not one of the two declared faces. Chrome *synthesises* it, and
  synthesised Fraunces measures 3.2% wider than either real weight — so the
  budget under-estimated, which is the direction that clips. `TYPE_WEIGHTS`
  records what exists.
- **Fraunces has an optical-size axis**, so the advance genuinely varies with
  size: 0.512em at 30px down to 0.448em at 116px. One constant cannot be right
  at both ends. Two earlier sweeps reported it as flat; both were artefacts —
  one read a fixed y-band while the type grew, one let large rows wrap and so
  cancelled the real trend.
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
2. **Landscape type and backdrop: fixed.** Both were real and both are closed.
   - `backdrop.py` took the canvas size and now fills whatever frame it is
     given; the hard `x=1080` seam is gone (column means run 37.9/38.3/38.2
     across x=1078–1082, where before it dropped 20.9→10.4 and stayed flat).
   - The type was never the declared face. `scene_html` wrote
     `g.type{font-family:...}` with `class="type"` on the `<svg>`, so the rule
     matched nothing and every line fell back to the browser's default serif.
     The "clipping" was coincidence: the narrow fallback ended each line near
     the backdrop's edge. Fraunces is now committed under `brand/fonts/` and
     referenced by relative URL, because a headless Chrome screenshotting a
     `file://` page cannot be trusted to have completed a network fetch.
   - `tools/verify_measure.py` is the gate for all of it, and it is a *pixel*
     check, not a wrap check. Run it before trusting any typography change.
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