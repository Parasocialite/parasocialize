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
python tools\citation_audit.py # are the status fields telling the truth
python tools\verify_taxonomy.py  # is the classification sound and complete
python tools\verify_narrow.py    # does a generated page overflow at 390px
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

`verify_narrow.py` is the **gate for anything touching CSS layout**. It measures
a generated page inside a 390px iframe and fails on horizontal overflow. Getting
that one number right took three attempts, each of which reported success while
measuring nothing (see Traps), which is why it asserts its own preconditions
before it will report anything at all. It needs `build_deploy.py` to have run,
because it measures `dist/` and measuring the source tree measures nothing. It
is deliberately not wired into `link_audit.py` — it needs a build and Chrome,
and a gate that runs on every commit is a gate that eventually gets disabled.

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
  twice before it was checked against the data. It was a misparse of my own
  verification regex; the arithmetic had been correct throughout.
- **A missing layer in a drawing ships, because nothing raises.** iYi's iris was
  defined, given a gradient, and never emitted — the argument was threaded
  through `pupil()` and then dropped on the floor when the iris moved out to its
  own group. The eye still rendered, the page still built, and the mood sheet
  still looked plausible: a bright sclera reads as "fine" whether or not there
  is an iris behind the pupil. It was found by printing the emitted SVG's
  circles in paint order, not by looking. `eyes_mkup()` now raises if a
  non-flat build is called without an iris. **In a character, verify the parts
  exist, not that the picture looks right.**
- **Look at the drawing; do not reason about the geometry.** Four successive
  attempts at the eyelid arc failed on angle direction, and one painted a dark
  bar across the pupil. Each was geometrically defensible and visually wrong.
  Render it and look. The same applies to the palette: the old sclera ramp was
  chosen for a stated reason (warm monochrome ages better than multi-hue) and
  the reason was sound while the outcome was a pair of breasts — warm mid-value
  on two large round masses with a low centred dark pupil and a specular above
  it. **A correct argument can still land on a wrong picture.**
- **A measurement can be right about the wrong layer.** The eye check failed
  five times before it was trustworthy, each time confidently: sampling the
  sclera as a percentile band of the whole eye (caught the lid), using the
  module's default pupil radius when the mood set its own, averaging a ring
  that clipped the pupil, treating the pupil as the iris, and reading the wrong
  tuple index so it printed `panic` six times. Every failure was a confident
  number about a layer it never sampled. **Print the profile, read the paint
  order, and confirm the check goes red before believing a green one.**
- **A status field is a promise. Check what it promises.** `retrievable` means
  "a reader can open this and find it" — so it requires a `url`. 94 of the 292
  records claimed it with an empty `url`, and because `build_cards.is_checked()`
  reads only `status`, they rendered as standing behind their entry. This is the
  `is_sourced()` thesis trap's twin and worse: those were inflated into the
  *backlog* (visible, if mislabelled); these were inflated into the *credits*.
  Same class of bug: a field that reads as a promise it does not keep.
  `tools/citation_audit.py` tracks it and is wired into `link_audit.py`;
  `add_source.py` now refuses a new one outright. **The 94 are an editorial
  decision, not a lint fix** — either find the URLs or downgrade them to
  `unverified`. Until then `sourced` means "has at least one record", not "every
  record is locatable".
- **`--ratchet`, not a hard failure, when a gate starts life behind.** 94
  records already violated the rule above. Failing every build until someone
  sourced 94 works is a laundry list, and it gets disabled inside a week. So the
  committed baseline is a ceiling that can only fall; raising it needs
  `--ratchet`, which puts it in a commit. `verify_measure.py` and the sampler
  check are the same shape.
- **A gate that cannot fail is decoration.** Before trusting any new check,
  break the input on purpose and confirm it goes red. Two of today's tools
  passed their first run while measuring the wrong thing.
- **A taxonomy built from your own corpus will break on the next thing you
  find.** The ten sections were reverse-engineered from 47 stories and could not
  hold 18 entries. Mix the object axis with the register axis and you get a list
  that cannot be extended, because three of its items are not the same kind of
  thing as the other seven. When a classification is failing, check whether it
  is failing on the material you already hold before writing a new category.
- **Do not fill a hole to make a chart look even.** Five sub-categories have no
  entry. They are reported as empty. Moving one entry into one of them would
  make the distribution tidier and the classification a lie, which is the same
  failure as a plausible-looking citation.
- **Do not deploy a backup.** `v1-oxalpha-backup.html` sat in the deploy tree
  for a while: nothing linked to it, and shipping it put a second, stale copy
  of the site's front page at a live URL. Two versions of the same content at
  two addresses is exactly what a reader and a search engine cannot tell apart.
  `build_deploy.wanted()` now refuses it by name.
- **A JSON file containing half the categories is still valid JSON containing
  half the categories.** Expanding the 38 sub-categories was done by writing
  `data/taxonomy.json` wholesale from a template, which silently dropped four of
  the eight categories and 19 sub-categories. Nothing errored, the build would
  have gone green on a taxonomy page missing a third of itself, and the only
  reason it was caught is that the category count was checked against the
  previous value immediately afterwards. **Merge into the committed file; never
  regenerate it from a template.** Same family as the 94 unopenable records: the
  output looks right and means less than it appears to. When editing any
  hand-maintained corpus file, assert the count before and after and refuse to
  write if it fell.
- **Correct the false claims first, then restore the accuracy.** 94 records
  claimed `retrievable` — defined here as "a reader can open this" — with no
  URL. Resolving URLs before downgrading would have meant leaving 90 published
  falsehoods live while chasing locators. A citation with no locator *is*
  `unverified` by that definition, so the downgrade costs no information, and
  the baseline then ratchets to 0 and the class is closed for good. The 83
  sources still needing a locator became a work queue instead of a lie on the
  page. This is the `--ratchet` pattern applied to content rather than to a
  gate: fix the claim, keep the debt visible.
- **Measuring a page can fail in the direction that looks like a pass.** Three
  separate harness bugs produced clean "no overflow at 390px" results, and all
  three were wrong: Windows clamps Chrome's `--window-size` to ~500px so 390
  silently measured 500; `--virtual-time-budget` with `--screenshot` returns a
  blank 5KB PNG that looks like a successful capture; and serving the preview
  from `dist/<subdir>/` 404'd every stylesheet, because Chrome normalises
  `../css/styles.css` to `/css/styles.css` *before sending*. **An unstyled page
  has no grid, so it reports no overflow for arbitrary content** — a pass
  manufactured by a missing file. `tools/verify_narrow.py` therefore asserts its
  own preconditions before reporting: it prints the viewport it actually got and
  refuses to produce a result unless it has read a computed style proving the
  stylesheet is live. A measurement is only worth its preconditions.
- **Distinct vertical offsets are rows, not columns.** The narrow harness
  initially reported `colsPerTriad: 3` for a layout that was stacked in one
  column, because it was counting unique `top` offsets. The names were wrong in
  the direction that flattered the result. Read what a metric counts before
  believing what it says it counts.
- **`body{overflow-x:hidden}` does not remove a layout bug, it hides it.**
  Every overflow found on this site was *clipped*, not scrollable: the reader
  lost the end of a sentence and never found out, which is worse than a
  scrollbar. This also breaks the obvious diagnostic — an element inside any
  `overflow:hidden` ancestor looks fine to a walk that treats clipping as an
  escape hatch, so `/audit/` reported *zero* real offenders while the document
  still measured 17px too wide. Treat `hidden` on the page as the reason to
  look harder, not as an explanation.
- **Four layout bugs, one shape: something that refuses to shrink.** A bare
  `1fr` grid track has an automatic minimum of its min-content, so it will not
  go below its widest child (`repeat(3,1fr)` on `.lanecards` reached 412px
  inside a 339px column; `repeat(11,1fr)` on `.tl-density` reached 515px at a
  390px viewport). A slash-separated list is one unbreakable token
  (`(idol/character/creator/companion/brand/universe)`, 47 chars). A table with
  `width:100%` cannot go below the sum of its cells' min-content widths. None of
  them is a text problem and all of them read as one to a screenshot.
  `verify_narrow.py` reports the *innermost* offender and picks the advice to
  match — a diagnostic that names `main` instead of the grid sends you to the
  wrong file.
- **A flex row will happily lay out three paragraphs side by side.**
  `.sec-head` is a two-column row (text block + mascot), and six pages put
  block elements straight into it without the `.sec-head-txt` wrapper. Flex did
  what flex does: `/credits/` put its kicker, its heading and its standfirst
  shoulder to shoulder and overflowed a 320px viewport. It now stacks by
  default and only goes two-column when it actually contains a `.sec-head-txt`,
  so the mistake is survivable rather than silent — and a browser without
  `:has()` gets the stack, which is the right reading anyway. **The five pages
  that only had two children were wrong at desktop width too** and did not know
  it; fixing the narrow case revealed it. Check that a layout fix did not just
  move the problem, and check the width that was never broken as well.
- **`link_audit` only read markup, so a page could fetch nothing and pass.**
  `/desk/` fetched `../data/queue.json` and `../data/sweep.json`; `data/` is
  excluded from the deploy; both 404'd; each had a `.catch()` that returned an
  empty value; and the page rendered as an empty room behind a footer link on
  every page. The audit stripped `<script>` before checking hrefs, so the
  requests were invisible to it. **A page whose data never arrives is still a
  page, and a `.catch()` converts a 404 into silence.** The audit now checks
  `fetch()` targets against what is actually served, and notes when no page
  fetches anything at all — baking data in at build time is the only shape that
  cannot silently arrive empty. Confirmed red on the original defect
  reintroduced verbatim.
- **A filter that has nothing to filter still works.** The old desk's sort and
  search ran correctly over an empty array, so the script was never broken and
  never wrong-looking. Rewritten JS has to be driven against the real generated
  page — typing a term, reading back the visible count, and checking that a
  no-match term shows zero and that clearing restores all 60 — or it has only
  been proven to run.
- **An identifier printed where a reference belongs reads as a citation.** The
  anchors were keys into `_literature` — `horton-wohl-1956` — and the page
  uppercased them, so readers saw `ANCHORED · HORTON-WOHL-1956`: shaped exactly
  like a source, impossible to follow. `_anchor_labels` now gives each one a
  human label and links to the full reference, and `verify_taxonomy.py` refuses
  an anchor that does not resolve. **Whenever a key is shown to a reader, ask
  what it would mean to somebody who has never seen the database.** Third
  instance of the "field that promises more than it keeps" family.
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
  at both ends. Two earlier sweeps reported it as flat; both were artifacts —
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
- `tools/citation_audit.py` — status fields vs what they promise. Ratcheted, and
  wired into `link_audit.py`.
- `data/taxonomy.json` — **the classification, on two axes.** Eight attachment
  categories (who or what is on the other end) and six registers (what is
  happening in the tie), with 38 sub-categories. This replaced the ten sections,
  which were reverse-engineered from the 47 stories and could not hold 18 of the
  175 entries, including Margery Kempe. Three of the ten were never attachment
  targets at all — contest, grief and danger are register — which is precisely
  why they could not be extended.
- `data/taxonomy_placements.json` / `data/story_placements.json` — all 175
  entries and all 47 stories placed, each with a written reason. The reason is
  printed on the page rather than kept in a commit message, so a placement can
  be argued with instead of merely trusted.
- `tools/verify_taxonomy.py` — asserts the structure and reports sub-categories
  with no entry in them. It also requires every sub-category to carry a `test`
  and a `not` of real length, and every anchor to resolve to a labelled
  reference: a definition can be read but cannot be used to classify anything,
  so the field that does the work is the question a person asks at 2am when
  deciding where a new entry goes. Five of 38 are empty and are reported rather
  than filled: forcing an entry in to make a distribution look even is the same
  move as inventing a plausible-looking source.
- The ten sections still exist and are **not** to be renumbered. A section is a
  place to look; a category is a thing to think about. `/taxonomy/` publishes the
  mapping between them.
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

**The eye must never read as flesh.** The lobes are *sclera*, not skin: cool,
luminous, low-saturation (`SCLERA` is white into a blue-grey). The warmth lives
*inside* the eye as the iris (`IRIS`, a deep amber ring at a constant
`IRIS_RIM`) and in the catchlight, never on the surface. Four cues carry it, and
all four are load-bearing: the **limbal ring** (`LIMBUS`, the dark rim of the
eye), the **eyelid arc** (`lid_arc`, stroked not filled — a crescent hugging the
rim merges into the limbus and the eye has no opening), the **iris**, and the
**white itself**, which is why `WHITE_MIN` clamps every mood's pupil radius
against what the 25-unit lobe can actually spare. Blush is gone: ACCENT ellipses
inside the eye were areola shading. The life is in the pupil, the light and the
movement — `.iyi-gaze` drifts the gaze (added here; the comment above the rig
had claimed a look-around for years without implementing one).

Video strategy: the bond comes from **continuity, not surveillance**. iYi is
"the clerk", admits it has a job, carries state across episodes, and must never
claim to remember an individual viewer. No synthetic depictions of real people.
Human voice only; no dataset sale.

## Current state

```
140 sourced | 22 not yet stood behind | 13 thesis   = 175
34 of 417 edges land on something unchecked
141 of 292 sources have a locator
0 of 292 claim to be openable without one   (ratcheted; was 94)
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
   episodes. Make it data-driven or duration-neutral before publishing. Note the
   block still renders nowhere: **no entry has a `video` field**, and `episode/`
   is in `build_deploy.EXCLUDE_NAMES`, so nothing serves video. Uploads go to
   YouTube by hand from the local drive; the channel is **@Parasocialdude**
   (long-standing, keep it) while the site is Parasocialize and IG/TikTok are
   parasocialite. **No social links exist anywhere** — not in `index.html`, not
   in `build_cards.py`, not in `build_deploy.py`.
4. **Tier 1 citations**, resting on inference rather than evidence: `dere`
   (Dionne Warwick, reciprocal fan mail — the counter-example the site needs),
   `the-neighbour`, `the-transfer`, `the-coach`, `the-dog`.
5. **The 94 unopenable `retrievable` records — closed, with a queue.** The
   false claims are gone: 4 records reused a URL that a sibling record in the
   same corpus already carried for the identical citation (verifiable by
   construction — accepted here, not found by search), and the remaining **90
   were downgraded to `unverified`**, which is what that status means: looked
   at, not yet locatable. `citation_audit.py --ratchet` has moved the baseline
   from 94 to **0**, so this can never regress, and the gate is confirmed red
   on a single false claim.
   - The remaining work is **83 unique sources with no locator** — the 94
     records were only 83 sources, because the same paper is cited on several
     entries. Notable clusters: the McCormick dissertation, Witzel, Marwick
     2021, Ahn/Lelkes/Levendusky 2024, Higgs & McInstash 2008, the
     `characters-move-in` Werther trio, the `prince` NPR cluster, and the
     `cobain` 1994 newspaper cluster. Book-length works with publisher pages
     and anything with a DOI are the cheap wins; the student papers, the
     1994 newspaper items and the paywalled dissertations are not.
   - Note `exa.ai` is already an accepted locator class here (6 records,
     against 29 doi.org). That is a separate editorial question about what a
     stable locator is, and it was not widened here.
6. **Lane re-seed — the analysis does not exist.** "30 additions, 17
   corrections, 0 removals" is recorded here and in `COVERAGE-MAP.md` as
   analysed and unapplied, but there is no script, no data file and no commit
   in the whole history containing it — only those sentences. `lanes` is also a
   legacy facet (9128ece dropped "aisle" for "section"). **Not reconstructed**,
   because inventing 30 additions to a curated editorial list is worse than
   the gap. Either redo it and commit the diff, or delete the claim.
7. **~~`trading-stamps` dated 1880~~ — resolved.** It is now 1890–1891. Every
   source the entry carried said so, including its own first citation, whose
   title spans *1891–2008*; the sources genuinely split between 1890
   (Encyclopedia.com) and 1891 (Clapp, *Ohio State Law Journal* 23(1), 1962),
   which is the case where a single year would be a precision nobody has. The
   entry had also had a review note written **over** that citation's `claim`,
   so the entry no longer said what its own source supported — the reason the
   wrong date survived review. `citation_audit.py` counts did not move: the
   empty URL on that record is one of the 94 in item 5.
8. **Membership tier** has no payment processor and no authentication. The page
   says so itself and is right to. Two claims on it were not true and have been
   corrected against `data/`: it sold "a machine that reads a hundred sources
   an hour and throws out ninety-four of them" (the last sweep was 70h ago,
   15 feeds, 88 candidates, **0 rejected**) and "every rejected draft, and why
   it was rejected" (`data/binned.json` is empty `{}` — nothing has ever been
   rejected). Now it sells the queue that does exist: 60 items awaiting
   signoff. Note the premise in the old version of this item was wrong — the
   sweeper *has* run; `data/sweep.json` records it, and `link_audit.py` was
   asserting "the sweeper has never run" in its own output while reading that
   file.
9. **~~`/desk/` is an empty room~~ — built.** It was a hand-written page that
   fetched `../data/queue.json` and `../data/sweep.json` at runtime;
   `data/` is in `build_deploy.EXCLUDE_NAMES` and never deployed, so both
   requests 404'd, each `.catch()` quietly produced an empty result, and the
   page rendered as dashes and nothing — behind a **CLERK'S DESK** link in the
   footer of every generated page. It is generated now from `queue.json` +
   `sweep.json`, with the 60 cards written into the HTML. Two further unkept
   claims lived on it and are gone: "the hourly job picks the commit up" and
   "the sweeper keeps running and the queue keeps filling" — it runs when it is
   run, and the page now says how long ago that was.
   `link_audit.py` now checks what scripts `fetch()` against what is actually
   deployed, which is the general form of this bug.
10. **The other 172 episodes.** All 175 entries carry `summary` and
   `significance`, so an episode exists for each and only the hand-written
   `hook` is missing. `tools/episode.py DRAFTS` has 3. Mechanically derivable,
   but a hook is the one line that makes a stranger stop scrolling, so it wants
   editorial judgement per entry rather than a template.

## Deploy note

`dist/` must be re-uploaded after each build. It is routinely ahead of
production.