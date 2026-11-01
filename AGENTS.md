# AGENTS.md

Parasocialize: a source-honest encyclopedia and video channel about one-sided
relationships. 240 entries, 580 relations, 336 generated pages.

Every count in this file is measured by `tools\report_current_state.py`, not
refreshed by eye. Three of them were typed wrong during a single earlier session
and the only reason they were caught was that something else was being verified
at the time - which is luck, not a process.

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
python tools\gates.py            # THE entry point. Runs every check, in order
python tools\gates.py --all      #   build, then post-build, visual, source
python tools\gates.py --list     #   what it runs
python tools\gates.py --only post,source
python tools\gates.py --skip visual
```

**Run `gates.py` rather than the individual tools.** It exists because the tier
order was being got wrong by hand, and a wrong order produces a *true* report of
the tree it was handed and a *false* report of the project - the same shape as
running `build_deploy.py` before `plate.py`. Three things it encodes that were
each learned the hard way:

- **post → visual → source.** The build goes first, or `link_audit` checks pages
  that do not exist yet. `test_front_copy` goes last, because it legitimately
  rewrites `data/front_copy.json`, which makes the source tier invalidate the
  build the visual tier is about to check.
- **It refuses to run a tier against a stale build.** `dist_is_fresh()` compares
  the newest file under `data/`, `css/` and `js/` against `dist/`, and names the
  file that is newer. The first version named the last directory in its own loop,
  so it blamed `js/` for a file in `data/` and sent the reader to the wrong tree.
- **Every check runs and the exit code is the result.** Never pipe a gate through
  `Select-String`; see the filtering trap below.

```powershell
python tools\daily.py           # THE daily loop: reconcile, plan, build, gates,
                                #   package; --check reports without writing
python tools\editor.py --check  # today's figure, top 8 and eight ways are valid
python tools\editor.py --refresh # rebuild today's edition in place
python tools\affil.py --check   # every domain mark is current and parses as SVG
python tools\test_editor_rotation.py  # tomorrow is structurally different
python tools\archive.py --check # every day since the epoch has a record
python tools\archive.py --reconcile  # close a provable gap, marked rebuilt
python tools\plan_next.py       # measured categorical work order -> data/plan.json
python tools\build_cards.py     # generate site from data/ (build_deploy does too)
python tools\build_deploy.py    # rebuild pages, then build dist/ incl. _redirects
                                #   and 404.html; --no-build packages the pages on disk
python tools\ledger.py          # every figure the site publishes, and it fails
                                #   if the record statuses do not reconcile
python tools\check_internal_leaks.py  # internal vocabulary in reader-visible
                                #   prose: AGENTS.md, tool names, data filenames
python tools\t8_pool.py         # the Top 8 lifecycle: candidate -> featured ->
                                #   placed -> archived. `featured` is the ELIGIBLE
                                #   pool and is deliberately uncapped
python tools\expand.py --check data\expand-queue.json   # validate candidates
python tools\expand.py --apply data\expand-queue.json   # place them, unverified
python tools\link_audit.py      # MUST pass before every commit
python tools\make_zip.py        # reproducible archive -> Desktop
python tools\add_source.py --apply-provenance
python tools\citation_audit.py # are the status fields telling the truth
python tools\cull_audit.py    # does any entry claim the far side perceives the reader
python tools\image_audit.py   # does any image claim what its photograph shows, unopened
python tools\look.py --list    # the image queue; QUEUE IS 0, not 25
python tools\gen_atmosphere.py # encyclopedia atmosphere art. NEVER `exact`, never depiction
python tools\withdraw_image.py # reject a generated image: removes the record AND the file
python tools\record_image_size.py  # generation.final <- the PNG actually on disk
python tools\verify_doi.py --from-citations  # does every DOI resolve to the work cited
python tools\verify_taxonomy.py  # is the classification sound and complete
python tools\report_current_state.py # the AGENTS Current-state block + media table, MEASURED
python tools\report_missing_locators.py # the shape of the locator backlog, measured
python tools\verify_narrow.py    # does a generated page overflow at 390px
python tools\probe_nav.py --check  # does the HEADER fit at every width, 768-1600, row vs overlay
python tools\shoot_nav.py   # 7 header screenshots incl. two body.nav-open cases; LOOK at them
python tools\plate.py --check    # does every title plate match its entry
python tools\episode.py eliza   # render episode; preserves voice/*.wav
python tools\verify_measure.py eliza shipping vshojo   # type vs its measure
python tools\measure_type.py    # regenerate tools/type_metrics.json
```

`plate.py --check` is checked by `link_audit.py` rather than run separately,
because a plate is a rendered claim about its entry and the one time it was not
a gate, 25 of them silently stopped describing their entry (see Traps).

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

```powershell
python tools\shoot_front.py      # the front page at 1440/1180/390, plus a full-height pass
python tools\shoot_band.py       # one band of it, for detail a full shot hides
python tools\shoot_moods.py      # iYi's eight moods as a PNG. LOOK at them.
python tools\probe_masthead.py   # which column is the tall one, at four widths
python tools\front_copy.py --list          # the rotating front-page copy, and which edition is live
python tools\front_copy.py --save --note "..."          # start this release's edition
python tools\front_copy.py --set <slot> <text> --to <date>
python tools\test_front_copy.py  # the copy rotation, exercised through the generator
```

**`shoot_front.py` and `shoot_moods.py` are how anything visual gets signed off.**
`probe_front.py` and `verify_narrow.py` measure overlap, contrast and 390px
overflow, and every one of them was green while the top half of the front page
read as janky - because none of them is about a mark having a job. They are not
wrong; they are answering a different question. Render, look, then measure.

**The front-page copy rotates with each bi-daily release** and that refresh is an
agent task, not a script's: `front_copy.py --save`, then `--set` the slots you
are changing, then `build_cards.py`. The copy lives in `data/front_copy.json` -
never in `index.html`, which `build_cards.py` overwrites (item 56).

**`link_audit.py` is a gate, not advice.** Read its output before committing.
Chaining it with `;` and committing anyway once put a failing commit in history.

**Run gates on their exit code, never through a pipe.** `| Select-String` on a
gate is how a red gate gets committed — see the `the-shadow` chronology item in
Traps for the round that actually happened. In PowerShell:

```powershell
foreach ($g in @('build_deploy','citation_audit','cull_audit',
                 'verify_taxonomy','verify_narrow','link_audit')) {
  python "tools\$g.py" > $null 2>&1
  if ($LASTEXITCODE -ne 0) { Write-Output "RED: $g" }
}
python tools\plate.py --check > $null 2>&1
if ($LASTEXITCODE -ne 0) { Write-Output "RED: plate" }
```

`$LASTEXITCODE` after a pipeline reads the *pipeline's* last command, so
`| Select-Object -Last 10` measures `Select-Object` and reports 0 while the gate
is red. Redirect to `$null` instead. This is the single most reliable way to
ship a falsehood on this site and it was done once already.

## Traps we have already hit

- **`seven\s+past` matched "seven pastors."** Cadence patterns need `\b` and need
  a *process verb* adjacent to the interval. A bare "every hour" is ordinary
  English. Probe both directions before trusting a regex change.
- **`is_sourced()` is `bool(e.get("sources"))`, so thesis entries counted as
  unsourced** and inflated the backlog by 13. The board now excludes them. If the
  three numbers ever stop reconciling to 212, suspect this class of bug first.
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
- **`verified: true` was a third instance of the promise defect, and the
  worst-placed.** It suppresses the "Not yet stood behind" notice, so an entry
  setting it with no citation records asserted that a person had read a source
  that does not exist — and the only visible consequence was that the honest
  notice disappeared. Six entries were in that state. The first two instances
  of this family inflated numbers (the backlog counted thesis entries; the
  credits counted a status without reading the URL); this one *removed a gap
  from the page*, so it is the only one a reader is directly misled by.
  `citation_audit.py` now fails on it, and thesis entries are exempt because
  they carry no sources by design.
- **A gate placed after the early return is decoration.** The new
  verified-with-no-source check initially sat below `if not violations: return 0`
  — and that branch is always taken now that the baseline is 0. So it reported
  nothing at all until the early return was changed. **When a check goes green,
  find out which branch it ran in.**
- **A string that only runs after the thing it describes changes is a string
  nobody checks.** The Watch block called every episode "the fifty-second
  version" — and the three rendered episodes are 42.0s, 53.7s and 63.4s, so it
  was wrong for all of them. It survived because the block only renders once a
  `video` URL exists on an entry, and none does. AGENTS had recorded the bug as
  "wrong for 53-64s episodes", which was itself wrong: it missed the short one.
  **Read the artefact, not the intent** — the mp4 header had the answer the
  whole time. Durations now come from `tools/set_video_seconds.py` reading that
  header, and the audit refuses a published video that cannot state a length.
- **A test that restores its own data must assert it did.** Testing the Watch
  block means writing fake `video` URLs into `data/encyclopedia.json`, building,
  reading the pages, and putting the data back. The teardown is the part that
  gets skipped, so it checks the file afterwards rather than trusting it — and
  rebuilds, because the generated pages outlive the data that made them.
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
- **Two entries can each be plausible and still contradict each other.** The
  dog entry called itself "the original transparasocial relationship, and the
  only one that has reliably worked". Both halves were false against this site's
  own data. *Transparasocial* is defined by this site's `transparasocial` entry
  as live people who respond in real time — "the other side can now hear you" —
  so a dog is the wrong kind of thing entirely; and a dog's bond **reciprocates**,
  so it is not one-sided. "Original" was worse: `myth-and-ritual` already sat
  14,200 years later in the same timeline and claimed to be "the oldest
  parasocial structure there is", and the archaeological record goes back
  tens of thousands of years before the dog. Two entries, each defensible alone,
  producing a false pair. **No single-record gate can see this; it took reading
  them side by side.** An automated version was written and deleted — it also
  fired on `sasaeng-culture` and `siri`, which are both correct, because using a
  defined word in prose is not claiming to define it.
- **A relation is a sentence about time, so its verb has to agree with the
  years.** `build_cards.py` renders `preceded` as "came before" and `succeeded`
  as "came after". Fourteen of them disagreed with the `year` fields, including
  a pair inverted in *both* directions at once — so the site told one reader that
  club cards came before trading stamps and another that trading stamps came
  after club cards. The semantics were read out of the renderer before any verb
  was flipped, because "preceded" could have meant lineage and the fix would have
  been thirteen new falsehoods. `citation_audit.py` now checks it.
- **Fifteen strings in the credits were not citations.** `transparasocial`
  carried `"Schramm, P., & Hartmann, D. (1997).  verify"` — the literal word
  "verify", no URL — and the entry still counted as `sourced`, so a to-do was
  rendered to a reader as a reference. A sweep found fourteen more
  (`"various;  verify"`, `"KpopWave; verify"`, `"Jussila et al. (2020);  verify"`).
  This is the site's central claim failing inside the site's own credit list.
  Two classes, two fixes: a real work with an editorial tail gets the tail
  stripped and stays `unverified`, and a record that was never a citation at all
  becomes `needs-source` and says so. One of them was also a *wrong title* —
  Horton & Wohl 1956 was recorded as "Mass communication and television".
  `citation_audit.py` now rejects a citation string containing verify/todo/tbd/
  fixme/xxx. **`de Vries & Gilovich (2015)` was left as an attribution alone**,
  because the title is not recorded here and writing a plausible one is the
  exact failure the sweep exists to remove.
- **A generated artefact is a claim until something checks it.** Every entry has
  a title plate, and the plate is drawn *from the data* — lane, category colour,
  kind, and whether the entry is citation-checked. `plate.py --check` was not in
  the gate list, so **25 plates had silently drifted**: `kobe`'s data said lane
  `grief` while its committed plate said APPLICATION. Nothing was broken and
  nothing looked broken; the plates were just describing an older version of the
  database. Same shape as the desk that fetched nothing — a generated page that
  quietly stopped describing its source. `link_audit.py` now rebuilds every plate
  in memory and compares, confirmed red by corrupting one deliberately.
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

- **The coverage of a law is not the law.** `ai-acts` is now California SB 243
  (Padilla), Chapter 677, approved and filed 13 October 2025 — read from the
  chaptered bill on leginfo, not from the coverage. The senator's own press
  release, a law firm's client note and several news items all list two
  requirements that **are not in the enacted text**: a prohibition on the chatbot
  offering rewards at unpredictable intervals or after an inconsistent number of
  actions, and third-party audits. Both are in the 28 March and 22 April 2025
  Senate amendments and were dropped before chaptering. Citing the press release
  for either would have put a false claim about a statute on the site while
  sounding maximally authoritative — a press release *from the bill's author*.
  The enacted duties are: disclosure only where a reasonable person would be
  misled (§22602(a)); a **published** protocol preventing suicidal ideation,
  suicide or self-harm output with referral to crisis services (22602(b)); for a
  user known to be a minor, disclosure, a break-and-identity reminder **at least
  every three hours**, and measures against sexually explicit conduct (22602(c));
  a disclosure that these products may not suit some minors (22604); annual
  reporting to the Office of Suicide Prevention from 1 July 2027, with
  evidence-based measurement and no personal data (22603); and a private right of
  action at the greater of actual loss or **$1,000 per violation** (22605).
  **When a claim is about what a document says, open the document.** The press
  release is cited here for the author's stated intent and explicitly not for
  the statute's requirements.
- **A statute can dodge the problem an entry names by changing what it regulates.**
  `ai-acts` argued that you cannot outlaw a feeling without defining it, and that
  the approach was therefore "almost certainly the wrong one". Chapter 22.6
  answers it by never defining the feeling: a "companion chatbot" is defined
  behaviourally, as a system "capable of meeting a user's social needs, including
  by exhibiting anthropomorphic features and being able to sustain a relationship
  across multiple interactions". Nothing about the user's interior state appears.
  So the entry's objection was *answered* and its prediction was wrong — and the
  entry said so. The entry's title also named an "AI Age Act" that nothing found
  here corroborates; the title now says what the law is called.

- **A strong negative is the cheapest thing to write and the first thing a source
  disproves.** Seven entries in this corpus asserted something emphatic and were
  wrong, and the shape is consistent enough to be a rule for review:
  `the-coach` said nobody had asked about the coach (it is one of the most-studied
  relationships in developmental psychology); `continuity` said the bond loses its
  shape without a weekly rhythm (the one controlled test found it *stronger*);
  `deepfake-grief` said it ran without anyone's agreement (the 2024 cases are
  licensed); `pokemon-go-incident` claimed a mass-casualty stadium stampede (it was
  a park, then a server outage); `bieber-effect` said "no gatekeeper whatsoever"
  (there were three, one of whom clicked by accident); `michael-jackson` was dated
  five years before the death it was about; and `the-dog` called itself the origin.
  **Read every "nobody", "never", "first", "only" and "no one" as a claim awaiting a
  source**, because that is what each of these turned out to be.
- **Five entries were misdated, so dates get checked against something external.**
  `michael-jackson` 2004 -> 2009; `airline-miles` 1981 -> 1979 (Texas International
  had the first frequent flyer programme, AAdvantage was the second, and American's
  newsroom still calls itself first); `p` -600 -> 8 (Ovid's *Metamorphoses* is ca.
  AD 8); `ai-acts` 2024 -> 2025 (SB 243 was signed 13 October 2025); and the
  `the-dog`/timeline pair described in item 11. A mechanical sweep was run across
  all 177 entries comparing each `year` field against any year mentioned in that
  entry's own prose: **no pre-existing contradiction found**, the only six hits
  being cross-references the prose explicitly explains. No entry's prose
  contradicts its own date - but five fields contradicted their *sources*, which
  is the check that matters and which no script can do.
- **The corpus found a hole in the taxonomy and the honest fix was to open a
  shelf, not to force an entry.** `officer` held teacher, clinician, legal, local
  and domestic - all *institutional* power. `persona` held idol, creator,
  presenter, sport-figure and sovereign - all distant or performed figures.
  Neither had a home for the Greek erastes: a private individual, personally
  known, older and more established, holding no office at all, whom a younger
  person attaches to and who is under no obligation to notice. Filing that under
  `officer/teacher` would have kept the distribution tidy and been false, because
  a teacher has duties. So `officer/senior` was added with the def, test, not and
  mechanism every other shelf carries: standing rather than role. It opens a real
  space - mentors, senior colleagues, older figures - and it is now 39
  sub-categories. `verify_taxonomy.py` asserts structure rather than a typed
  count, so extending was always possible; the question was only whether we would.
  `gobekli-tepe` is the parallel case on the other side: its interpretation is
  genuinely unsettled, so it is filed `divine/abstract-absolute` - the shelf for a
  represented being whose identity *is* the dispute - rather than under
  `saint-ancestor`, which would have argued one side of a live debate by filing it.
- **The earliest written description of this site's subject is 2,300 years older
  than the site claimed, and its anatomy is modern.** `the-deaf-beloved`, c.370
  BC, is Plato. In the *Phaedrus* the beloved is a hunting beast that is "shag-eared
  and deaf", and the closing image inverts everything: having got what he chased,
  the lover turns to flee and the *beast* pursues him, because it never
  understood the terms. The one-sided party was not withholding - it was deaf.
  And in the *First Alcibiades*, Alcibiades tells Socrates that he is the only
  lover who has not abandoned the suit, while the others "pestered you with their
  conversation" and he stayed silent for years. So the same structure is described
  from both ends, which almost nothing else on this site manages, and the Phaedrus
  records that role reversals between lover and beloved were constant. Four
  primary-text locators, all openable: Perseus, the Internet Classics Archive,
  Project Gutenberg and Wikipedia for the dating.
- **Göbekli Tepe is the oldest thing here with a claim to be about figures, and
  its interpretation is open.** c.9500-8200 BC: hunter-gatherers who had not yet
  domesticated anything cut limestone into anthropomorphic T-shaped pillars,
  carved them with foxes, scorpions, lions and vultures, returned for fourteen
  hundred years, then deliberately backfilled the enclosures. No hearth, no
  rubbish pit, no sign anyone lived there - people travelled to the place. UNESCO's
  own nomination reads the pillars as "ancestors, perhaps even incipient deities"
  and that "believed to be" is the honest state of the evidence, so the dispute is
  carried in the significance rather than resolved. Note the dominant imagery is
  not a kind face: the commonest carvings are lions, spiders, snakes and
  scorpions. What the entry claims is narrow and still large - for at least a
  millennium people made representations of beings, went out of their way to be
  near them, and eventually chose to close the place where they stood.
- **The relation-direction gate is now earning its keep.** Five inverted verbs were
  caught across two new entries in one sitting, three of them caught *before* the
  files were written by an in-script assertion rather than after by the audit. Every
  fresh batch of relations is now asserted against the years before save, because
  the failure mode is always the same: writing `preceded` from memory in the
  direction the sentence reads rather than the direction the dates run.
- **Coverage before the year 1000, measured**: 11 entries.
   -70000  neanderthal-burial
   -40000  paleolithic-figures
   -34000  sunghir
   -15000  the-dog
    -9500  gobekli-tepe
     -800  myth-and-ritual
     -370  the-deaf-beloved
     -250  roman-imagines
     -200  congregation
        8  p
      100  the-priest
- **Two more from the ancient world, both reversing the site's usual shape.**
  `the-clay-army` (210-209 BCE): 8,099 life-size soldiers, every one individually
  distinct, buried facing enemy territory with the emperor at their backs. The
  *npj Heritage Science* analysis (2022) found the facial features "highly resemble
  those of contemporary Chinese people" and concluded they "were crafted from
  real portraits and intended to constitute a real army to protect the Emperor
  Qin Shihuang in the afterlife, as if he was alive", the constructed army being
  the substitution of his real one. Everywhere else here one person attaches to
  another who cannot answer; here eight thousand specific likenesses were made to
  serve one absent man, each facing away from him. Placed `persona/sovereign`,
  because the object of the tie is an office-holder preserved as though still in
  office. The cost is carried in the entry rather than as a footnote to it: young
  women of the court were buried with him, some apparently dismembered and laid
  outside the passageways, and facial reconstructions have since been made of two
  of them.
  `the-absent-sage` (c.660 BCE): a tablet in the voice of Ashurbanipal listing
  what he was taught and by whom - "I learned [the c]raft of the sage Adapa" - and
  then what he did with it: "I have placed them in my palace for the instruction
  of my subjects." A named sage reached entirely through writing. Two details stop
  it being a parable. Babylonian scribes were taken captive during the campaigns
  and set to work in the royal libraries, so the archive that taught the world was
  built by people who did not choose to be in it. And when Nineveh fell in 612 BC
  the fire baked the clay tablets, so the library survives only because it was
  destroyed. Placed `officer/senior` - the shelf `the-deaf-beloved` opened three
  days earlier, filled again from the other direction.
- **Relations should be computed from the dates, not typed.** This error class has
  now cost seven wrong edges across three entries: writing `succeeded` because the
  sentence reads that way rather than because the numbers do. `citation_audit.py`
  catches it after the fact, and an assertion inside the build script catches it
  before the write - four of the seven would otherwise have needed a follow-up
  commit. Deriving the verb from `year` is the fix, not remembering harder.
- **Coverage before the year 1000, measured: 13 entries.**
  ```
    -70000  neanderthal-burial      -9500  gobekli-tepe
    -40000  paleolithic-figures      -800  myth-and-ritual
    -34000  sunghir                  -660  the-absent-sage
    -15000  the-dog                 -370  the-deaf-beloved
                                   -250  roman-imagines
                                   -210  the-clay-army
                                   -200  congregation
        8  p                         100  the-priest
  ```
  Up from six when this work began. Sixty-two of the 183 are dated 2010 or later,
  so the skew is real but the floor is no longer a footnote to 1956.
- **A boolean can be used two ways in one corpus, and the gate cannot tell
  which.** `the-imaginary-friend` and `howdy-doody` were written with
  `verified: true` because their claims had been checked against sources that
  were actually fetched and read. Checking the corpus before committing showed
  that **42 of the 59 `verified: true` entries also hold at least one
  `unverified` or `needs-source` record** — the entire archaeology batch included
  (`neanderthal-burial`, `sunghir`, `lewis-chessmen`, `gobekli-tepe`,
  `the-clay-army`), so the loose reading is the corpus's actual practice, not a
  one-off. `AGENTS.md` item 4 documents the *strict* reading ("nobody has read
  these yet"), which means the field and its documentation disagreed before this
  was looked at. The two new entries were set to `false`, which is the reading
  the documentation states and the safer of the two — but that is an editorial
  decision about what the word means, and it is **not settled here**. Do not
  ratchet it without answering the question first: is `verified` a claim about
  the *entry* (its assertions were checked against at least one source that was
  read) or about every *record* (nothing on it is unverified)? The first is
  what the data does; the second is what this file says. Same family as the
  other three instances of a field promising more than it keeps — and the first
  one found by reading the field's own documentation against its own values
  rather than by a gate, because the gate has no way to ask which meaning is
  intended.
- **Filtering a gate's output is not the same as running it.** `the-shadow`
  (1930) was given a relation to `cliffhanger` (1930) by a script that derives
  the verb from the years with `preceded if a < b else succeeded` — so **equal
  years silently became `succeeded`**, and the site told a reader The Shadow
  came after the cliffhanger. `citation_audit.py` caught it and has always
  caught this class. What actually happened is worse: I ran the audit *through*
  `Select-String -Pattern "records |with a URL|statuses|none\.|edges land"`, that
  pattern did not include the word FAIL, **the failure scrolled past unread,
  and the entry was committed.** Two lessons, and the first is the general one:
  - **Do not pipe a gate through a filter.** `| Select-String` on a gate is how
    a red gate gets committed. Read exit codes instead — `$LASTEXITCODE` after
    `python tools\x.py > $null` is unmissable, whereas grepping the output is
    only as complete as the pattern. This is the same defect as the "gate
    placed after the early return" item, one level out: both are about a check
    that cannot be *seen* failing, rather than one that cannot fail.
  - **Equal years have no derived verb.** Of 45 same-year relations, 44 already
    used a non-chronological type and assert no order; exactly one used a
    chronological one, and it was the false one. `contemporary` renders as
    "of the same time as" and is the right answer whenever two entries share a
    year. **When two things share a date, the honest relation is that they were
    contemporaneous — not that one came after the other.** Any future script
    deriving relation verbs from `year` must handle the tie explicitly, because
    a `<` that fails open turns a coincidence into a chronology.
- **A probe that finds nothing is not evidence, and the usual reason is the
  probe.** Chasing quotes out of the Gutenberg text of *Dorian Gray* took four
  rounds, and the failure was mine each time rather than the corpus's. First
  failure: the HTML edition decodes its smart quotes as `cp1252`, so `’` arrives
  as three bytes and every quote containing an apostrophe fails to match. Second:
  the fix applied entity replacement *after* stripping tags and still produced
  `U+FFFD`, which looked like corruption in the source. Third — and this is the
  one that actually cost the time — `re.findall("It will never alter", text)`
  returned **0 hits on a passage that verifiably exists**, because the novel
  reads *"But **it** will never alter"* with a lowercase *it*, and the search
  was case-sensitive. Every probe reported "0 hits" and none of them said why.
  The lesson generalises past regex: **`0 results` is the one output a tool can
  produce by being wrong in seven different ways**, and the honest response is
  to print the surrounding window and read it rather than to mutate the pattern.
  Two things that fixed it and are now the default: probe with
  `re.I` and a whitespace-flexible join (Gutenberg hard-wraps at ~72 columns, so
  `"It\\s+will\\s+never\\s+alter"` is the correct form and `"It will never
  alter"` is not), and fetch `cache/epub/<n>/pg<n>.txt` rather than the `-h.htm`
  so there is no tag-stripping question at all. Same family as
  `seven\s+past` matching "seven pastors", and the same remedy: **probe both
  directions before believing a null.**
- **HTTP 429 is not the same failure as 403.** Both Met Museum pages on the Lewis
  chessmen returned 429 - rate limiting - on two attempts a minute apart. The text
  was read via a search index rather than fetched, so both records are `unverified`
  with the status reason stated in the claim. A reader will get those pages; this
  agent did not, and `retrievable` means a reader can open it *and this was
  checked*. Marking a throttle as verified would be the same error as marking an
  unread PDF.
- **Scratch files in the shared Windows temp directory collide.** Commit messages
  are written to `$env:TEMP\opencode\msg<N>.txt`, and that directory holds files
  from other projects on this machine — including a `msg12.txt` from an unrelated
  karaoke site, which briefly became this repo's commit message and had to be
  amended. Use a project-scoped name (`parasocialize.msg.<date>-<n>.txt`). Nothing
  is pushed, so amending was safe; if there is ever a remote with commits on it,
  fix the message with a new commit instead.

## Architecture

- `data/encyclopedia.json` — the single source of truth. 240 entries.
- `tools/ledger.py` — **every figure the site publishes.** `/ledger/` and
  `report_current_state.py` both read it, because two
  definitions of "openable" on a site whose argument is that it does not blur
  its own states is the exact defect the ledger exists to prevent. It refuses to
  emit if the record statuses do not sum to the record total.
- `/ledger/` — the editorial statement of the standard, and `/citations/` is the
  technical audit of it. Distinct pages on purpose, mutually linked.
- `/exceptions/` — the reciprocity axis counted, **including the two ways the
  count is probably wrong.** 10 of 240 entries carry a value; 8 of those 10
  carry none on `otherness` either. Read from `taxonomy_placements.json`'s `rec`
  field, which is a real field — an earlier plan to recover it from placement
  prose by regex would have been a number about the wrong layer.
- `tools/check_internal_leaks.py` — scans `dist/` for project vocabulary in
  reader-visible prose and is wired into the source tier.
- `tools/gates.py` — the tiered runner. Use it instead of calling the tools in
  your own order.
- `tools/daily.py` — **the daily loop.** Reconciles the three daily records,
  measures the categorical plan, rebuilds, draws plates, packages `dist/`, runs
  the post and source tiers, writes `data/daily.json`, packages again and then
  proves the deployed tree carries today's rotation. `--check` is the same
  contract without writes and is the thing a scheduler or a returning agent runs
  first. `--visual` adds the Chrome tier; `--no-zip` skips the archive.
- `tools/archive.py` — **the daily records' auditor and repair path.**
  `--check` fails on a day with no record. `--reconcile` closes a gap only when
  the inputs behind that day were frozen before it, and marks the entry
  `reconstructed` with `reconstructed_on` and `inputs_sha256`; every record page
  prints a `rebuilt` tag beside it. Wired into the source tier.
- `tools/plan_next.py` — **the measured categorical work order.** Counts media
  days, catch-all share, storyless categories, thin decades, top-8 window
  arithmetic and pipeline staleness, writes `data/plan.json`, and prints the
  ranking. It names gaps and never authors a source; `/desk/` renders the top six.
- `tools/install_daily_task.ps1` — **local scheduler fallback.** Dry-runs unless
  `-Register` is passed. It exists because the GitHub workflow cannot run until
  the local history reaches a real remote, and a repository that is never pushed
  has no automation however green its cron file looks.
- `tools/t8_pool.py` - the Top 8 lifecycle. **`featured` is uncapped on
  purpose:** it is the eligible pool and the page shows eight of them, so a cap
  makes rotation unreachable by construction. It curates the newest live list
  (`pick_list`); what is *on show* is the list dated today (`show_list`),
  generated by `tools/editor.py`. A former list is archive-only and is never
  shown again.
- `tools/expand.py` — validates and places candidates from `data/expand-queue.json`.
  Everything lands `verified: false` and promotion is a separate, human step.
- `tools/build_cards.py` — all page generation, the citation board, section
  fronts, and the entry Watch block (renders only when a real `video` URL exists).
- `tools/build_deploy.py` — **the fresh-build entry point.** Runs
  `build_cards.py` then `plate.py`, so the date-seeded features are computed for
  today, then builds `dist/`, `/e/<id>` redirects for all 240 entries, and
  **CSS/JS fingerprinting.** `--no-build` packages the pages already on disk and
  is what `gates.py` uses after it has run the two builders itself. Assets are
  emitted as `<stem>.<sha256[:10]>.ext`, every reference is rewritten, and a
  stale unhashed name is refused — because `immutable` caching on a stable
  filename is how a deploy goes out and nobody sees it.
- `tools/editor.py` — **the daily editorial agent.** Reads current wires
  (Google News RSS, ten queries over 3–14 days, with the counter's queue as
  fallback), picks a theme and a figure, selects eight existing entries and one
  pick for each of the eight ways, then writes `data/editorial_today.json`,
  appends today's list to `data/features.json` and appends the ways record.
  `--refresh` rebuilds today in place; `--check` validates it. It authors no
  new fact: the top 8 prose is the entry's own summary/significance, each entry
  links to its page, and a wire headline is always a link.
- `data/top8_themes.json` — the hand-written framing for the daily list: title,
  home title, hook, dek, standfirst, law and a selector over medium, attachment
  category, section, keywords or year. The editor picks a news-matching theme
  or the least recently used one; a theme cannot repeat within 21 days.
- `data/editorial_today.json` — **GENERATED, one edition per UTC day.** The
  figure, theme, news links and eight way picks as they were shown. The daily
  loop reads it before the build; the front page and each way page render it.
- `data/ways_history.json` — **STATEFUL AND TRACKED IN GIT.** One record per
  UTC day: the theme and the eight way picks. Written by `tools/editor.py`,
  never regenerated. Each way page shows today's pick and the previous five.
- `data/archive_gaps.json` — declared, unrecoverable days in the daily records.
  A missed daily top 8 or parasocialite cannot be reconstructed from a later
  build because it depended on that day's wires; the archive declares the gap
  instead of inventing an edition, and the record page keeps the hole visible.
- `tools/affil.py` — **the affiliation marks.** Twenty author-drawn SVG domain
  marks (sport, music, film, television, radio, literature, comics, games, AI,
  religion, stage, art, tech, history, brand, persona, companion, officer,
  predator, default) for a figure or entry with no sourced photograph. They
  say "AFFILIATION · NOT A PORTRAIT" on the face. `--check` parses every SVG
  and refuses a missing or stale mark; a file that 200s but cannot render is a
  missing image with a plausible filename. The figure card uses a real
  photograph first, then the mark; a way page uses the way's own mark, so the
  eight pages keep one visual identity. Plates are not used as fallbacks.
- `data/timeline.json` - **the master timeline.** 355 instances across seven
  phases, each with the required schema (`id`, `year`, `title`, `domain`, `era`,
  `summary`, `parasocial_analysis`, `primary_source_or_artifact`, `tags`) plus
  `sort_year`, `phase`, `citations`, an optional `date_note`, `provenance`
  (`sourced` or `pdf`) and `speculative` for phase 7. `year` is a
  display string (`c. 8 CE`, `1830s-1850s`) and `sort_year` is the integer the
  page orders on. `phase` is 1-7 and the page groups by it. `date_note` is where
  a widely repeated date is wrong and the entry says so. A citation carries
  `citation`, `url`, `status` and `note`; `retrievable` means this build opened
  the URL and found the work, not that the whole text was read. The six domains
  and five eras are the schema's own lists and the filters are built from them.
  `/timeline/` is the master page (264 observed/sourced entries); the PDF's
  91 projections are at `/timeline/future/`; the 255-entry database timeline is
  at `/timeline/corpus/`. The supplied PDF itself is deployed from
  `assets/parasocial-timeline-1800-2149.pdf`.
- `tools/verify_timeline.py` - **the timeline gate.** Checks every required
  field and type, the domain/era/phase membership, `sort_year` against the year
  string and inside its phase, the citation status/locator contract, the 78
  mandated seed ids, `provenance`/`speculative`, and the rendered pages: the
  master page carries every non-speculative entry, the future page carries every
  speculative one, and the corpus page links back. Wired into the source tier.
  It cannot check that a date is true; that is what the citations are for.
  `--check-urls` is a separate, explicit network pass.
- `data/ledger_history.json` — **STATEFUL AND TRACKED IN GIT.** Appended by
  `record_snapshot()` only when a watched figure moves, one entry per day however
  many builds run. `/ledger/feed.xml` is generated from it, so the feed is the
  only thing on the site that reports *change* rather than current state. **Do
  not regenerate it, and do not delete it to "clean up"** — a rebuild from
  scratch loses the history and the feed restarts at "first recorded snapshot",
  which is exactly the silent reset the feed exists to avoid. It is the one data
  file in the repository whose value is its *sequence*.
- `data/top8_history.json` — **STATEFUL AND TRACKED IN GIT.** One record per
  UTC day: which top-8 list was on show and the eight moments it carried,
  appended by `build_cards.record_top8_day()` from the same `top8_window()`
  the page renders from, so the record and the page cannot describe different
  shows. **Do not regenerate it, and do not delete it to "clean up"** — the
  sequence of what was on show is the file's whole value, and a day nobody
  built on cannot be reconstructed. `/top8/` renders it as the day record
  (`.t8rec`), names resolved from the current data at render time, and
  `/top8/record/` renders the whole sequence at full length, one line per
  day, from the same file.
- `data/register_history.json` — **STATEFUL AND TRACKED IN GIT.** One record
  per UTC day: which register was put forward on `/taxonomy/`, appended by
  `build_cards.record_register_day()` from the same `register_of_day()` the
  page renders from, so the record and the page cannot describe different
  days. **Do not regenerate it, and do not delete it to "clean up"** — the
  rotation is recomputable from the date and the register order, and that
  recomputability is exactly why the file exists: if either changes, only
  this sequence shows what the page actually said. `/taxonomy/` renders it
  as the day record (`.tx-days`), names resolved from the current data at
  render time, and `/taxonomy/record/` renders the whole sequence at full
  length, one line per day, from the same file.
- `data/parasocialite.json` — **the figure bank** behind the front page's
  daily spotlight: 49 members, 48 selectable (27 real, 21 fictional) and one
  non-selectable historical format (`queen-for-a-day`) kept so old record days
  resolve by name. A selectable member must have `kind: real|fictional`, a real
  `entry` page, wire `aliases` and a `context` list for names that are also
  ordinary words (`prince`, `harvey`). The daily editor chooses from the bank;
  `build_cards.parasocialite_of_day()` falls back to it for dates with no
  edition. The old fixed alternation contract is retired: the page now says
  **Real figure** or **Fictional figure** and why the figure is today's.
  `tools/test_parasocialite_rotation.py` holds the figure rule and the record.
- `data/parasocialite_history.json` — **STATEFUL AND TRACKED IN GIT.** One
  record per UTC day: which figure was put forward on the front page,
  appended by `build_cards.record_parasocialite_day()` from the same
  `parasocialite_of_day()` the block renders from, so the record and the block
  cannot describe different figures. **Do not regenerate it, and do not delete
  it to "clean up"** — today's choice is a stored editorial selection, not a
  formula, so only this sequence shows what the page actually said. The block
  renders it as the day record (`.psotd-days`), names resolved from the current
  bank at render time, and a member no longer in the bank is shown as such
  rather than dropped.
- `tools/add_source.py` — citation insertion + the THESIS set.
- `tools/citation_audit.py` — status fields vs what they promise. Ratcheted, and
  wired into `link_audit.py`.
- `RESEARCH-NOTES.md` + `research-cache/` — **the evidence trail behind the
  citations, kept because two sessions were interrupted mid-batch and the
  extracted quotations existed only in context while the fetched pages did
  not.** `RESEARCH-NOTES.md` is *not* a citation: `encyclopedia.json` holds
  those. It holds what was read, what was extracted, and — the part worth more
  — **what was rejected and why** (the AFI catalog entry that returns the wrong
  film, Britannica and Sage at 403, the Met at 429). `research-cache/` holds
  the plain-text extractions the quotations were taken from, so a claim can be
  re-checked without re-fetching. Raw HTML is deliberately not cached: it is
  reproducible from the URL in the citation, and 1.7MB of Wikipedia markup is
  not worth carrying.
- `data/taxonomy.json` — **the classification, on three axes.** Eight attachment
  categories (who or what is on the other end), eight registers (what is happening
  in the tie), and — added 2026-10-03 — six **otherness** members (what the other
  end is *made of*), with 39 attachment sub-categories. This replaced the ten
  sections, which were reverse-engineered from the 47 stories and could not hold
  18 of the entries, including Margery Kempe. Three of the ten were never
  attachment targets at all — contest, grief and danger are register — which is
  precisely why they could not be extended. The third axis was added because an
  audit of the corpus against the user's requested categories found **zero**
  entries for imaginary friends, zero for conscious non-human minds, zero for
  puppets as such, and only incidental mentions of shadows and projections. That
  is a hole in the subject, not in the classification, and neither of the two
  existing axes could express the difference: a companion can be invented,
  worked, alive, worshipped, mirrored or haunted, and each produces a different
  relationship.
- `data/taxonomy_placements.json` / `data/story_placements.json` — all 227
  entries and all 48 stories placed, each with a written reason. The reason is
  printed on the page rather than kept in a commit message, so a placement can
  be argued with instead of merely trusted.
- `tools/verify_taxonomy.py` — asserts the structure and reports sub-categories
  with no entry in them. It also requires every sub-category to carry a `test`
  and a `not` of real length, and every anchor to resolve to a labelled
  reference: a definition can be read but cannot be used to classify anything,
  so the field that does the work is the question a person asks at 2am when
  deciding where a new entry goes. Four of 39 are empty and are reported rather
  than filled: forcing an entry in to make a distribution look even is the same
  move as inventing a plausible-looking source.
- The ten sections still exist and are **not** to be renumbered. A section is a
  place to look; a category is a thing to think about. `/taxonomy/` publishes the
  mapping between them.
- `tools/mascot.py`, `tools/wordmark.py` — iYi. Asymmetric per-eye rig.
- `tools/episode.py`, `tools/backdrop.py`, `tools/iyi.py` — video.
- `COVERAGE-MAP.md` — domain sweep and the three-tier work queue.

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
223 sourced | 0 not yet stood behind | 17 thesis   = 240
edges landing on an entry with no citation record: 62 of 580
434 of 542 sources have a locator
108 records have no locator at all, and say so   (/ledger/ publishes this)
0 of 542 claim to be openable without one   (ratcheted; was 94)
0 relations contradict the years they point at
0 relations point at themselves
0 relations claim an order neither end can support
0 citation strings are notes to self
0 entries assert the far side perceives the reader   (tools/cull_audit.py)
0 entries carry an unsourced claim                    (tools/add_source.py report)
0 internal terms in reader-visible prose   (tools/check_internal_leaks.py, ratcheted)
0 orphaned layout rules                    (tools/check_css.py --orphans, baseline 0)
39 attachment sub-categories, up from 38
6 otherness members, on a third axis
3 reciprocity members, on a fourth axis recovered from the 2019 chart
15 media values, up from 13 (stage and visual_art added)
10 of 240 entries carry a reciprocity value; 8 of those 10 carry none on
  `otherness` either, and /exceptions/ says so on the page
8 of 15 media hold no reciprocity exception at all, `ai` among them
```

Board must reconcile to 227. `add_source.py` is authoritative.

**These four lines are typed, and they are the defect this file warns about
twice** - "a number inside a paragraph is not obviously a claim, which is what
makes it the dangerous kind" and "do not type this number here". They went stale
at 193 entries while the data was at 195, and `235 of 384` had been stale
since the Wonka entry. They were only corrected because the entry count was
checked against `add_source.py report` while verifying something else, which
is luck rather than a gate. **The durable fix is to compute this block**, and
until it is computed, treat any number in it as a claim awaiting a tool.

**Gate order matters.** `plate.py` draws from the data, so it must run *after*
`build_cards.py` and *before* `build_deploy.py`. `build_deploy.py` enforces
that order itself, because a packaging step that only copies ships whatever day
the pages were last generated - which is how the date-seeded top 8, register and
parasocialite sat on 21 October while every gate was green. The full daily loop,
including the archive reconciliation, the measured plan and both non-browser
gate tiers, is one command:

```powershell
python tools\daily.py
```

`python tools\build_deploy.py` remains the fresh packaging command when only the
deploy tree is wanted. `gates.py` keeps the explicit three-step build sequence
and passes `--no-build` to `build_deploy`, because the post tier has just run
`build_cards` and `plate` and running them twice would append the day's history
twice (a no-op, but a second build is still a second build). `--no-build` is for
a caller that has just run those steps; used by hand it packages whatever is on
disk, and can ship a stale day.

Run the sequence the other way round and `build_deploy` reports 404s on plates
that do not exist yet, which is a true report of the tree it was given and a
false report of the project.

## Open work

1. **Publish one episode — and the blocker recorded here was false.** This item
   said all three episodes were blocked on human voice, "nine per episode" in
   `episode/*/voice/NN.wav`. **The files are all there.** Reading the WAV headers
   directly (no ffmpeg, no codec) settles what is in them:

   | episode | files | total | peak | RMS | crest | clipped | verdict |
   |---|---|---|---|---|---|---|---|
   | `eliza` | 9 | **42.00s** | 7–18% | **1.5%** | ~1000 | 0% | speech-shaped, recorded far too quiet |
   | `shipping` | 9 | **53.74s** | ~95% | ~9% | ~1000 | **0%** | levelled speech |
   | `vshojo` | 9 | **63.37s** | ~95% | ~9% | ~1000 | **0%** | levelled speech |

   Three things follow. **The durations match the recorded episode lengths
   exactly** — 42.00 / 53.74 / 63.37 against the "42.0s, 53.7s and 63.4s" noted
   above — so the timing work is finished and only the recording was outstanding.
   **RMS an order of magnitude under peak with a crest factor near 1000 and
   1600–2700 zero crossings per second is speech**, not clipping (which would
   show clipped samples) and not a tone (which would show tens of crossings).
   And **`eliza` is not silent, which I first reported it as** — I compared
   24-bit samples against a 16-bit full-scale, so a voice at −23dB read as a
   peak of 37. It is quiet, not absent; it needs a gain lift, not a recording.
   **So the only remaining work on all three is listening to them and lifting
   `eliza`.** Nothing here claims the words are right — waveform shape cannot
   tell you that, and it is a human judgement.
   - The lesson generalises past this item: **"blocked on X" is a claim about the
     world and needs the same scepticism as any other.** It sat in this file
     through a great deal of work, and nine files per episode satisfying the
     stated requirement is exactly how a stale blocker keeps looking like
     progress. Check the artefact, not the note.
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
3. **~~Entry Watch label~~ — done, and it was worse than recorded.** The block
   was hardcoded `"fifty-second version"`. Reading the rendered files (an mp4
   carries its duration in its `mvhd` atom — no codec, no ffmpeg needed) shows
   the three episodes are **42.0s, 53.7s and 63.4s**, so the label was wrong for
   *all three*, not just the 53–64s pair this item used to describe. Nothing
   noticed because no entry carries a `video` yet, so the string had never
   executed.
   Now: `video_seconds` per entry, filled by `tools/set_video_seconds.py`
   reading the actual file; the wording rounds to what a reader can hold in
   their head ("The 42-second version", "The one-minute version") rather than to
   the second, which would go stale on the next re-cut; and `link_audit.py`
   **fails** on a published video with no stated length. Also fixed: a stray
   "The The" produced by the article living in both the label and the template.
   Still true: **no entry has a `video` field**, `episode/` is excluded from the
   deploy, and uploads go to YouTube by hand from the local drive; the channel
   is **@Parasocialdude** while the site is Parasocialize and IG/TikTok are
   parasocialite. **No social links exist anywhere** — not in `index.html`, not
   in `build_cards.py`, not in `build_deploy.py`.
4. **~~Tier 1 citations~~ — closed, and three of the six were wrong.** The six
   entries that claimed to be verified with nothing behind them are all now
   sourced, and the entry text changed in four cases because the literature did
   not say what the entries said. They all stay `verified: false`, so the "Not
   yet stood behind" notice stays: nobody has read these yet.
   - **`the-coach` claimed nobody had asked about it.** False in this repo's
     signature way. Holt et al.'s meta-synthesis of 63 qualitative studies puts
     "adult relationships" inside the developmental climate it models; "positive
     and sustained adult–youth relations" is one of the Big 3 programme
     characteristics; and Côté & Gilbert's four Cs include **Connection, defined
     as "positive bonds and social relationships with people inside and outside
     of sport"** — so the relational bond is one of the four things a coach is
     judged on producing. The real gap is narrower and better: the relationship is
     studied as developmental and **never as one-sided**, and `connection` is
     scored as an outcome rather than described as a structure.
   - **`continuity` claimed the bond loses its shape without the weekly rhythm.**
     Erickson, Dal Cin & Byl (2019) manipulated binge watching experimentally and
     found it *increased* parasocial relationship strength and narrative
     transportation. The claim is the site's argument, not a finding, and the
     page now says so. What the evidence does support is the *gap*: the
     parasocial scales of the period ask directly whether you miss characters
     between seasons.
   - **`deepfake-grief` claimed it was deployed "mostly without anyone who loved
     the person having agreed."** The documented 2024 cases are licensed — Jones
     signed his voice rights to Lucasfilm in 2022 while alive, and ElevenLabs
     dealt with the Garland, Dean, Reynolds and Olivier estates. Consent has
     moved to the *licensor*, which is a sharper problem than the one claimed.
   - `comfort-watch` and `the-landlord` needed sourcing but no correction; both
     are better evidenced than they claimed. `the-transfer` likewise, and its
     mechanism turned out to be the reverse of the cliche: fans identify more
     with the **club** than with any individual, and that identification survives
     the pairing being dissolved, which is why the departing player absorbs it.
   - **`dere` was removed.** Its summary read "See 'Dionne Warwick's fan mail'",
     which already existed as its own entry dated the same year; the two pointed
     at each other in a circle and its id was a fragment of the other one. A
     pointer that got promoted to an entry, with a page, a plate, a redirect and a
     taxonomy placement. 178 → 177 entries.
   - `replika-launch` also needed correcting rather than sourcing: it claimed
     the product's "stated purpose was a parasocial bond". It did not. It
     launched in 2017 from **Luka, Inc.** as a mental-health and wellbeing app,
     rated 18+, filed under Health & Fitness, selling self-understanding. The
     attachment is in the *users*, which is the more interesting claim: the bond
     was engineered as a wellness intervention and turned out to be a
     relationship.
   - **Four entries still carry zero citation records**: `gilsoul-case`,
     `billi-eilish`, `pokimane`, `streamer-ban`. All four are recent fandom or
     streaming incidents where a single authoritative write-up should close them.
     Three separate searches were run for each and none surfaced the specific
     incident: the `pokimane` query returned a *different* streamer (Amouranth,
     arrested in Houston in June 2022 after casing her house - a genuinely
     comparable case, and not the one this entry describes), and the
     `billi-eilish` query returned nothing on the stream removal. All four stay
     visibly unsourced rather than half-sourced. **None is flagged `verified`**,
     so none of them is claiming a reading nobody performed.
   - Eight entries closed in this pass, and **five of them were wrong in
     substance rather than merely unsourced**: `airline-miles` was two years late
     and its founding detail was better than its own argument (AAdvantage seeded
     membership by searching the SABRE reservations system for recurring telephone
     numbers and wrote to 130,000 flyers individually); `michael-jackson` was five
     years out; `teen-idols` reached for a record label when the supply chain ran
     through a television family show; `peak-tv` treated an FX executive's coinage
     as a critical category; `the-closure-gift` had no instance to point at until
     Google Reader supplied one, whose petition text states the site's own thesis.
     `the-closure-gift`'s 2005 date was checked and left alone - it is the year
     Reader launched, not an error.
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
10. **The other 209 episodes.** All 212 entries carry `summary` and
   `significance`, so an episode exists for each and only the hand-written
   `hook` is missing. `tools/episode.py DRAFTS` has 3. Mechanically derivable,
   but a hook is the one line that makes a stranger stop scrolling, so it wants
   editorial judgement per entry rather than a template.
11. **The timeline was wrong at the bottom, and the dog was the symptom.** The
   site dated one-sided attachment from −800 (`myth-and-ritual`) and had
   `the-dog` at −15000 claiming to be "the original". Two entries were added
   from the archaeological record, which is the earliest evidence available:
   - **`neanderthal-burial`, −70,000.** Neanderthals repeatedly carried their
     dead into Shanidar Cave in northern Iraq and put them down in the floor —
     Shanidar Z in a hollow gouged out to fit her, with a stone under her head.
     Dated 70,000–75,000 ya. This is the oldest evidence of treating the dead
     as *somewhere you go* rather than something you leave.
   - **`paleolithic-figures`, −40,000.** Upper Paleolithic figures from mammoth
     ivory: Vogelherd's cave lion, bison, horse, bear, mammoth and the
     lion-man, plus the La Madeleine bison carved mid-grooming — licking its own
     side, a specifically human gesture put in antler on purpose.
   - The correction to `the-dog` is the interesting part. The claim "the dog is
     the origin" was never defensible; what was defensible is "the dog is the
     one bond that was bred". The dog also turns out to be the **control
     condition** for the whole site — the only entry whose other end is a real
     body that reciprocates — which is a better argument than the one it was
     making.
   - Note the evidence discipline held: the famous Shanidar **"flower burial"
     is a debunk** (the pollen came from burrowing rodents), and the entry says
     so. The *burials* survived the debunk; only the flowers did not.
   - **`roman-imagines`, 250 BC – 550 AD, is the strongest evidence in the file**
     and it is textual, which is why it is worth more than the archaeology. A
     Roman aristocrat had a wax mask of his own living face taken in his
     thirties or forties on taking office; it sat in a cupboard in the entrance
     hall beside a painted family tree (*stemma*) and a label (*titulus*) of his
     offices; he never saw it worn; after his death actors walked it in his
     funeral procession in order of death. Two locators, both fetched, both open:
     Penn Museum (Rose & Lovink, *Expedition* 56(3), 2014) and Lewis Webb,
     "Gendering the Roman imago", *Eugesta*, DOI 10.54563/eugesta.550.
     What it establishes about parasocial structure, all from named sources:
     **the mask cannot answer** — eye-holes and a lip gap were cut so the *actor*
     could see and speak, and the *titulus* did the conversing; **it was daily**,
     since Valerius Maximus has a man recalling he called the dead his parents and
     drew his standing from their masks (5.5.praef) and Cicero has the Bruti
     seeing Lucius Brutus's mask daily (*Phil.* 2.26); **it had states** — opened
     at festivals, hung with laurel on an election, closed in mourning; **it was
     an inheritance that changed address**, copies going with a bride into her
     husband's atrium (Cic. *Vat.* 28; SCPP 76–82 of 20 CE), with Pliny hoping to
     leave children "non subitas imagines" (*Ep.* 8.10.3); and **it carried
     shame** — Pliny's son was *burdened* by which masks he carried (*Ep.* 3.3.6),
     and Val. Max. 3.3(ext).7 on descendants who turn the ancestors' light into
     darkness. Two honesty notes kept on the entry: **no wax mask survives**, so
     all of it is literary; and the right to hold imagines was **customary, not
     statutory** — Flower 1996 argues there was no formal *ius imaginum*, which
     makes the site's own "the right to keep imagines" claim wrong.
     It is placed in `divine/saint-ancestor` on purpose, **the same shelf as
     `neanderthal-burial`**: burying someone you mean to keep within reach and
     casting a likeness of them are the same act 70,000 years apart.
   - **`p` (Pygmalion) was dated −600 by a source published in AD 8.** Its only
     citation is Ovid's *Metamorphoses*, ca. AD 8 (Ovid 43 BC – 17/18 AD; Perseus
     CTS catalogue and the Loeb timeline, which files the poem in 1–100 AD). So
     the entry — the one that called itself "The origin" — was off by roughly 608
     years and contradicted its own citation. Redated to 8, given a Perseus
     locator, and "the origin" narrowed to **the first written telling**, which
     is the same correction already applied to `myth-and-ritual`.
     `history.json` module 1 had **the same 608-year error a second time**, in the
     page that is supposed to be the authoritative history: it opened with Ovid
     under the range "c. 600 BC". Range corrected to "c. 100 AD – 1400" and the
     archaeology now acknowledged in the body, because the encyclopedia carries
     three entries older than anything that module mentions. **A history page that
     contradicts its own encyclopedia is worse than no history page.**
   - **An entry's own front page must not disagree with itself.** The kicker
     printed only the start year, so `roman-imagines` read "250 BC" directly
     above a summary saying the practice continued into the fourth and sixth
     centuries AD. `_fmt_span()` now includes `year_end`. Positive years still
     print bare (no "AD") on purpose — the era label carries that, and adding it
     would restyle every entry.

14. **The origin of the site exists on a drive and nowhere in the repository.**
   `K:\EnanInc\parasocialite` is an 801-file, 277.7MB asset and reference
   library — not a site backup. Two documents in it are the origin, and both are
   dated:
   - **`Key20\TwentyYums_Script.docx` + `twentyums.xlsx`, 2015-07-28.** The text
     is extracted to `research-cache/`. It opens "Hello and welcome to the
     Parasocialize channel – I'm your host **ParaosocialDude** and in this Key
     20 we unlock" and then runs a *Night of the Living Dead* radio broadcast
     cold open — *"broadcasting on all AM frequencies… if anyone is out there…
     please. You are not alone."* **That is this site's thesis, written in 2015
     as a zombie-film transmission to someone who may not be listening.**
     After it, ~50 columns of film genres, the last two being **Parasocial
     Movies** and, in the TV block, **Para Series** — the author's own subject,
     appended to an inherited genre list. This corroborates the note already
     here about **@Parasocialdude** and the `parasocialite` folder name with a
     primary document.
   - **`CatchingandWeaving_Character Chart.jpg`, 2019-04-12** — *Catching and
     Weaving*, based on the author's novel **Company Dreamer**. Node border
     colour is studio tier (dream studio / Mygdala public / Insize theistic /
     Phasic private / Family); edge type is **Directed Affection vs Mutual
     Love**. `Recast_Character_Chart.jpg`, same date, is the real school
     production of it with a named cast, director Jean Balinger and coordinator
     Jay Gustafson.
   - **`MASTER_CAST.jpg`, 2023-02-10** is a Patreon for **All the Horrible
     Things**: ~40 genre-film episode covers, each carrying the circular emblem
     that became **iYi**.
   - **The gap this exposes is the interesting part.** The published work is
     documented (`company dreamer` appears in 32 repo files); the *creative
     process* is not. `catching and weaving`, `key 20` and `key20` return **0
     files** in the repo.
   - **And a dimension the data model does not have.** The 2019 chart encodes
     affection **direction** as an edge type. `encyclopedia.json` relations are
     `preceded`/`succeeded` and *chronological only* — "directed" vs "mutual",
     the exact distinction between a parasocial bond and a reciprocal one, and
     the thing `the-dog` exists to isolate, is **absent from the schema**. Node
     colour is the ancestor of the `medium` axis; the affection axis was dropped
     and never rebuilt.
   - **Images: 0 of 193 encyclopedia entries have one.** All 73 records in
     `data/images.json` are `for: story` (47), `section` (10), `top8` (8),
     `feature` (8). Encyclopedia pages get generated SVG plates only. K: has ~340
     show-named JPGs (`reality/` one per show — Big Brother, American Idol, The
     Bachelor, The Apprentice; `tvage/` one per scripted show).
   - **But do not import them.** `images.json`'s own `_note` sets the rule —
     "Wikimedia Commons, cached locally… a candidate missing a `must` term is
     the wrong picture, not a worse choice… An entry with `local:null` and no
     available photograph **is a real answer**." All 48 fetched images carry
     `licence`, `author` and a Commons `page`. K: is overwhelmingly
     **unattributed Google Images downloads** — the filenames *are* download
     hashes: `_1418892.jpg`, `1416867494_2.png`, `5167032_orig.jpg`,
     `Screenshot 2019-10-30 23.06.55.png`. Dropping those in would put
     unlicensed third-party stills live and break the site's own stated
     standard. The safe subset is the author's own work: 16 logo/brand files,
     13 section-art pieces, 39 `7most` series thumbnails (`paracom1-7`,
     `paradude1-7`, `paraho1-7`, `paraVO1-7`, `para4th`), both character charts,
     and `margery-kempe-statue13_5.jpg` — which maps to the existing
     `margery-kempe` entry *and* to the published essay *The Binding of
     Margery Kempe*.

15. **The corpus had no entry for the one mechanism all three of the user's
   examples shared.** Asked about Harvey, Tyler Durden and Deadpool *talking
   directly to the audience*, the audit found `fourth wall` **0** entries,
   `camera` 2, `direct address` 1 — a hole in the subject, not in the
   classification. It is also the boundary the site turns on: a **fictional**
   figure acknowledging that an audience exists is not a **real** person
   acknowledging *you*, and `transparasocial` is defined here as "the other side
   can now hear you". Same gesture, opposite structure. Four entries:
   - **`the-fourth-wall`** (1758, `character/played-role`, `made`) — and the
     etymology is the good part. The concept is attributed to **Diderot, 1758**:
     actors and writers should "imagine a huge wall across the front of the
     stage, separating you from the audience, and behave exactly as if the
     curtain had never risen." Diderot's *un grand mur* **became "the fourth
     wall" to Leigh Hunt in 1807**, writing about the actor Mr. Bannister:
     "No actor enters so well into the spirit of his audience as well as his
     author, for he engages your attention immediately by seeming to care nothing
     about you; the stage appears to be his own room, of which the audience
     compose the fourth wall." **Henry Irving, February 1879**: "the stage has
     four walls, though the fourth is only theoretical", and the **first known
     use of "fourth wall theory"** follows *later that month* in a comment on
     that article in the British periodical **Truth**. Vincent Canby, 1987:
     "that invisible scrim that forever separates the audience from the stage."
     **No coinage year was sourced**, so the entry is dated to the concept and
     says so rather than picking whichever of 1758/1807/1879 suits.
     The mechanism argument: the wall is a specification for *invisibility* and
     the whole site is about the far side of it. The strongest breach is not a
     wink — in **Peter Pan** it is an instruction the audience obeys, "If you
     believe in fairies, clap your hands!", to revive Tinker Bell, who lives or
     dies on whether strangers in the dark choose to believe. **That is the
     parasocial condition with the volume up: the fiction's survival is now a
     real person's decision.**
     Two honesty notes, the second being why this is an entry and not a
     sub-category. In **mockumentary** the camera may be *inside* the fiction, so
     looking into it is not a breach — a convention only counts if the audience
     knows it is one. And see the `transparasocial` boundary above.
     **Also: the user's "bunny talking to the audience" is real and it is
     documented — it is Bugs Bunny.** "Characters in theatrical animated
     cartoons, particularly Bugs Bunny and other characters in Warner Bros.'
     Looney Tunes and Merrie Melodies shorts, regularly broke the fourth wall",
     with Tex Avery's *Daffy Duck and Egghead* (1938) and *Thugs with Dirty
     Mugs* (1939) named. There is no character called Harvey Rabbit doing this.
   - **`harvey`** (1950, `companion/social-agent`, `haunted`) — and the film is
     not about the rabbit, it is about **complicity**. Directed by **Henry
     Koster**, not Cukor, which was assumed before checking. Elwood's invisible
     companion is 6 ft 3½ in and described as a **púca**; the play spells it
     *pookah* (p-o-o-k-a) and the character Wilson reads the definition from a
     dictionary on page 33 of Chase's playbook. The play is **1944**, premiered
     1 November 1944 at the 48th Street Theatre, Pulitzer awarded **1945** — not
     1946, which several sources imply. The plot is the thesis: Veta "in
     exasperation, admits to the attending psychiatrist, Dr. Sanderson, that she
     sees Harvey once in a while herself" and is committed in Elwood's place,
     and Dr. Chumley, convinced Elwood is insane, "wandered off with Harvey after
     several rounds of drinks." **Every bond here needs somebody to maintain it,
     and this one is maintained by nobody saying the sentence.** Wikipedia's own
     hedge is quoted as the honest register: Elwood "claims to have an unseen
     (and presumably imaginary) friend".
   - **`fight-club`** (1999, `character/fictional-protagonist`, `mirrored`) —
     sharper than `dorian-gray` because the split is **inside one voice**: "The
     Narrator, an unreliable narrator, is not immediately aware that he is
     mentally projecting Tyler." No second person exists to check him against.
     Norton on the production: "We decided early on that I would start to starve
     myself as the film went on, while Brad Pitt would lift and go to tanning
     beds; he would become more and more idealized as I wasted away." One body,
     two figures, divergence made physically. And the tie to
     `the-imaginary-friend`: an unreliable narrator is a person who **knows and
     maintains anyway**, and the Narrator does not know Tyler is invented — one
     mechanism, two states of knowing, concealed deliberately until the last ten
     minutes.
   - **`deadpool`** (2016, `character/fictional-protagonist`, `animate`) — the
     breach is a **character trait licensed from the comics**, not a director's
     device: the film "was set to ignore the Wolverine version of Deadpool and
     return to the character's roots with a slapstick tone and a 'propensity to
     break the fourth wall'". So the wall is *in the characterization*.
     Everything else about him is damage; the one intact thing is his
     relationship to you. Greenlit 2014 after test footage leaked, **$58M budget,
     $782.6M gross** — the address is the marketing, and a hard-R character who
     talks back cannot be sold as anything other than what he is.
   - Five records, five `retrievable`, four of them Wikipedia read in full. The
     **AFI catalog entry `moviedetails/50671` returns the wrong film** (*The
     Stooke*, 1953) and TCM returned nav chrome only — neither is citable, and
     both rejections are written down in `RESEARCH-NOTES.md`.

16. **The affection axis the 2019 character chart had and the schema lost is
   back, with a member the chart could not have had.** `reciprocity` is the
   fourth axis: *directed*, *reciprocated*, *simulated*. The chart drew affection
   **direction** as an edge type — Directed Affection against Mutual Love — and
   nothing in `encyclopedia.json` could express it, because all 467 relations
   are chronological or bibliographic: cites 217, depicts 70, preceded 52,
   contemporary 46, succeeded 46, member_of 12, instance_of 9, wrote 7,
   bond_with 5, occurred_in 3. **Only five edges in the corpus are affection
   edges at all.** A site named after one-sided attachment had no field for
   saying a bond was one-sided.
   - **The chart had two states; this has three.** The corpus found a third the
     chart could not have, and it is the site's actual subject:
     `live-commentary` and `twitch-subs` both "solved a problem nobody had been
     able to solve: making the one-sided bond **feel** reciprocal without the
     labour of a real relationship". Solved is the operative word. That is
     **simulated** — reciprocity manufactured on one side and sold as the
     product — and it is not a weaker version of reciprocated. It is a
     different thing wearing its clothes, and the clothing is the point. The
     `not` is drawn carefully: simulated is **not fraud**, which is a separate
     charge needing separate evidence, and not deception, since a host reading
     a comment aloud usually believes the warmth. The test is whether anything
     is felt on the far side, not whether the near side is honest.
   - **The `reciprocated` test is deliberately hard to pass.** "Would the other
     end be missed if it stopped?" — not "would it notice", which is the
     question a figure with no interior cannot answer. The far end must be
     acting on its own initiative. That is what admits `dionne-warwick`, who
     wrote back, and excludes a talk-show host reading a caller-out, who
     replied once and would not be mourned.
   - **Six entries carry a value, each quoting its own prose as the reason**, so
     a reader can check the classification against the entry: `the-dog`
     reciprocated ("a dog is not a figure and **it answers back**" — the site's
     control condition, and the only reason the term exists), `p` directed (the
     entry applies the test to itself: "entirely structured around the other
     party's inability to reciprocate"), `dionne-warwick` and `kobe`
     reciprocated, `live-commentary` and `twitch-subs` simulated.
   - **`alf` was deliberately left unset.** Its entry says "The Tanners are
     reciprocated; the cat is not" — and that reciprocity happens *inside the
     fiction*, between ALF and a family who can hear him. The axis is about the
     bond between the audience and the other end, and an audience cannot be
     reciprocated by a character. Setting it would answer a different question,
     which is how a fourth axis becomes a source of confident noise.
   - The axis is **optional per entry and stays that way**: `directed` is the
     default condition of the whole site, so requiring it everywhere would print
     187 identical labels and bury the five that are not. The audit prints
     `reciprocated` and `simulated` separately for exactly that reason — *a
     corpus about one-sided attachment that cannot count its own exceptions is
     not measuring the thing it is named after.*
   - That printed paragraph first said "hide the seven that are not" — a typed
     literal in a report about the data, which is the defect
     `verify_taxonomy.py` already documents about the "Five of 38" sentence it
     replaced. It now counts. A number inside a paragraph is not obviously a
     claim, which is what makes it the dangerous kind.

17. **The image pipeline's `kind: exact` was a promise nobody had kept, and it is
   the fourth instance of that family.** Found while trying to build the
   encyclopedia image layer — which has **zero records**, because all 73 records
   in `images.json` are `for: story` (47), `section` (10), `top8` (8), `feature`
   (8). The layer could not be built on the existing pipeline, and the reason is
   one line:

   ```python
   tools/images.py:306    src, kind = None, "exact"
   ```

   `kind` defaults to `"exact"` and is only downgraded to `"illustrative"` when
   the query falls through to the Flickr topic fallback. **Nothing in that path
   ever looks at the picture.** So `kind` — which means *the photograph shows the
   thing itself* — was derived entirely from a must-term appearing somewhere in
   a filename, and **40 live records claimed it**.
   - Probed four encyclopedia subjects, all of which passed the must-term filter,
     then **looked at the files** rather than the titles:
     | entry | Commons returned | what it actually shows |
     |---|---|---|
     | `elvis` | "Elvis Presley, Bob Neal, and Sam Phillips in 1955" | correct |
     | `prince` | "Prince, People au Défilé Channel, Printemps-Été 2010" | **correct** — judged wrong from the title, and looking corrected it. The only right one of four. |
     | `cobain` | "Courtney Love Frances Bean Cobain 2015" | Courtney Love and Dave Grohl. "Cobain" is the **daughter's** name. |
     | `nick-drake` | "Drake1" | a **churchyard** |
     | `p` | "Pygmalion, Alan Thornhill" | a **Putney Sculpture Trail plaque**; a sculpture there happens to be named Pygmalion |
     | `cervantes` | "pila bautismal de Miguel de Cervantes" | his **baptismal font** — a real artefact, not a portrait |
     **Three of four wrong, after passing the filter whose stated job is to
     exclude exactly that.** The must-term test is necessary and nowhere near
     sufficient: it establishes that a word is in the filename, not that the
     file shows the subject.
   - **`prince` is the part worth keeping.** My first judgement, from the
     filename, was that it was an Egyptian television channel. It is Prince the
     musician, photographed from a car in 2010, and "People au Défilé" is a
     paparazzi agency. **I was wrong, and only looking at the picture caught
     it** — the same lesson as the eyelid arc, arriving from the opposite
     direction. Do not judge an image from its filename, and do not report a
     defect you have not looked at.
   - **Corrected the claim first, then restored the accuracy**, which is the
     order already used for the 94 unopenable `retrievable` records. All 73
     records are now `kind: "unchecked"`, which promises nothing, and **no image
     file was deleted** — `img/editorial` still holds all 84. What changed is
     that the records stop asserting something nobody checked. A record only
     becomes `exact` or `illustrative` again once somebody has opened the file
     and written down the date in `looked`. **The 73 are now an explicit,
     numbered work queue**, the same treatment the 83 missing locators get.
   - **The judgement was also in the wrong field.** `kind` was stored *inside*
     `src` — the provenance block — so a human judgement about a picture read as
     though Commons had supplied it. Commons cannot tell you whether a
     photograph is `exact` for this site's purposes. Moved to the record level.
   - **Two captions were describing the story rather than the frame**, which is
     the one thing a caption must not do, because a caption is the only place a
     reader can check a picture against a sentence. Both turned out to be
     *honest* — `character-ai-settlement` said "A real courtroom, standing in
     for a litigation that did not happen there - captioned as a courtroom and
     not as the hearing", and `t8-3-grouch` said "Fans in costume is what
     Commons actually holds, and on this site that is the better picture". Both
     disclosures were kept verbatim and moved to a new `note` field; the caption
     now says only what is in the frame. **A caption that discloses its own
     substitution is doing this right**, and the fix was the field, not the
     sentence.
   - `tools/image_audit.py` gates it: `exact`/`illustrative` require a `looked`
     date, every `local` must exist on disk, every cached file needs
     `licence` + `page` + `credit`, and no caption may contain story-language.
     Confirmed red twice by promoting an unverified record to `exact` and by
     pointing a `local` at a missing file, and green after restoring each.
     Its docstring also states what it **cannot** do: a gate can hold a field to
     its promise, it cannot make the promise true.
   - **Still owed:** the encyclopedia image layer itself, and the eye-check on the
     73 existing records. Nothing about that is blocked by licensing — the
     Commons route is clean and `must` works — it is blocked on somebody looking
     at the pictures, which is the part no script can do. `tools/images.py
     --slots` already asks for exactly this from the author: *"Real photographs
     of the real shelf, the real classroom and the real person will do more for
     this site's credibility than any stock library."*

18. **The corpus could write an entry with no source at all, and four of them
   were claims about named living people that nobody could source.** The four
   that had been flagged unsourced since the Tier 1 pass are **gone**, and the
   reason is not that they were found and fixed.
   - Fetching the subjects' encyclopaedic articles settled what four rounds of
     searching could not:
     | entry | claimed | what the article actually records |
     |---|---|---|
     | `pokimane` | a viewer arrives at a creator's home | a 48-hour DMCA suspension (8 Jan 2022) and a hate raid by JiDion's viewers. **No SWAT, no police, no doorstep, no "Physical Evidence".** |
     | `streamer-ban` | a two-year ban, suspended then reinstated | **no two-year ban.** Its one "two-year" is a **$100m two-year Kick deal (June 2023)**. No December 2024, no "reinstated", no Kassian. |
     | `billi-eilish` | fans of one artist mass-harass another | **"Cyrus" 0 hits, "harassment" 0 hits.** The single "Noah" is Noah Centineo in a Calvin Klein ad. |
     | `gilsoul-case` | a fan harmed breaching a home, and a petition | **"Gilsoul" 0, "petition" 0, "fans" 0.** Only her memoir and her post-2011 advocacy. |
   - **Absence from an article is not absence from the world**, and none of these
     is claimed to be fabricated. What is established is that after four
     separate attempts the claims could not be sourced, and that each names a
     living, identifiable person. That is not the same as an entry with a missing
     photograph. `AGENTS.md` says "a visible gap is correct", and that is right
     for a gap — this was not a gap, it was a specific incident asserted with
     nothing behind it. **Removed: rows from `seed_encyclopedia.py`, entries,
     placements, plates, pages, dist, redirects and sitemap.** Zero inbound
     relations, so nothing broke.
   - **The real find was the process, not the four.** `seed_encyclopedia.py` has
     a `source` column, and **89 of its 106 rows were written with `""`.** It
     accepted an empty source silently. Eighty-five were later sourced by hand,
     one at a time, by somebody else, which is exactly why nobody noticed — the
     debt was paid quietly and the mechanism that created it was never touched.
     The four that were never paid are the visible symptom of a path that could
     write a sourceless entry at will.
   - **The guard took three attempts, and each failure was instructive:**
     - **v1 refused every empty `source`** and blocked the seeder outright: 85
       rows have an empty seed column *because they were properly sourced
       afterwards*. A guard that cannot tell "not yet sourced" from "sourced the
       long way round" is not strict, it is broken, and it took the tool out of
       use. Added the corpus check.
     - **v2 refused 7 rows that are all `provenance: thesis`** — `the-clerk`,
       `the-audience`, `ratio`, `club-card`, `protagonist-parasocial`,
       `parasocial-consent`, `the-reply-heres-watching`. Thesis entries take no
       citation *by design*; AGENTS says so and it means it. Added the exemption.
     - **v3 skipped rows not yet in the corpus** "because there is nothing to
       inspect" — which is precisely backwards, since a new row is the case that
       *creates* a sourceless entry. Testing it wrote a stray `probe-gap` entry
       straight into `encyclopedia.json` (190 entries), which is how it was found,
       and the entry was removed and the corpus re-verified at 189.
     All four cases are now exercised deliberately: real table passes, a
     genuinely sourceless row fails, a thesis row passes, a stale column on an
     entry with real records passes.
   - **A field cannot be deleted from the data while the code that writes it
     still runs.** Seventeen entries carried a legacy top-level `source` field
     that duplicated `sources[]`, and three of them **rendered the entry's own
     subject as its own reference**: `vshojo` → "VShojo, 2022",
     `stadium-residency` → "Eras Tour", `elvis` → "The Colonel Parker
     apparatus". That is the identifier-printed-where-a-bibliography-belongs trap
     live on three pages. Clearing the field changed nothing — the first seeder
     run put all seventeen straight back. The fix was to stop the seeder writing
     it, and the field was cleared from the corpus only after that.
     - **A first pass at this also removed only the legacy field and reported the
       job done while the false credit survived**, because the same three strings
       were *also* sitting in `sources[]`, which is where the page renders them
       from. Those three records are now `needs-source` and say why: the seed
       note named the entry's own subject rather than a reference.
     - And the sixteen non-false rows were **redundant, not wrong** — `eliza` →
       "Weizenbaum, 1966", `shrlu` → "Winograd, 1970" are real citations, and
       the field duplicated records that already existed. My first count said "16
       of 17 were rendering their own subject as a citation", which was false; the
       check was only testing whether the string duplicated the record, and for
       real authors it does. Sixteen duplicated, three were false, one was a
       placeholder already replaced in the record.
   - **`add_source.py report` now reads `0 not yet stood behind` for the first
     time**: 176 sourced + 13 thesis = 189. Not because the corpus grew, but
     because the only four entries asserting something unsourceable are no longer
     asserting it.
   - Cost of getting here, recorded because the pattern is the lesson: this
     session damaged `data/encyclopedia.json` by rewriting it as
     `{"entries": [...]}` and dropping `_note`, `lanes` and `kinds`, which made
     the seeder crash on `KeyError: 'lanes'`. Recovered with `git checkout` and
     redone preserving every top-level key. **Assert the top-level keys before
     and after writing a hand-maintained corpus file** — which is already the
     rule for taxonomy.json, and now has a second instance.

19. **The corpus's biggest hole is chronological, and it is exactly where the
   phenomenon happened.** Measured rather than assumed: the thinnest decades are
   **1910s: 2 entries, 1920s: 3, 1900s: 4, 1940s: 6**. Four decades in which
   fan mail, the movie star and the first mass celebrity bereavement all
   happened, and the encyclopedia is nearly empty of them. The distribution
   overall runs before-1000: 13, 1000–1899: 17, 1900–1959: 33, 1960–1989: 25,
   1990–2009: 37, 2010+: 63 — so the 2010s are 63 entries deep and the silent era
   is a footnote. Meanwhile `kind: person` was 17 of 193 and **only about nine
   were named real humans**, several of them authors rather than objects of
   attachment. An encyclopedia of one-sided attachment with almost nobody in it.
   Four entries added, all from that window, all on the requested categories:
   - **`rudolph-valentino`** (1921, `persona/idol`) — the template for every
     celebrity death since. "The first Latin Lover and the Great Lover";
     breakthrough *The Four Horsemen of the Apocalypse* (1921), which did not
     merely star him but "popularized the Argentine tango dance with American
     audiences", so figure and dance step arrive together. Died 23 August 1926 at
     thirty-one, and Wikipedia's own summary of the consequence is flat:
     **it "triggered mass public mourning, cementing his status as a legendary
     figure of early cinema."** The detail that earns the entry is smaller: at
     the funeral **Pola Negri "made a scene at his funeral, claiming they were
     engaged, in spite of the fact that Valentino himself had never mentioned
     this engagement to anyone."** A woman invented a relationship with a dead
     man because the public bond demanded one, and the invention was more
     faithful to the audience's picture of him than anything he did.
   - **`mickey-mouse`** (1928, `character/mascot`, `made`) — `howdy-doody`
     nineteen years early and further along. Disney and Ub Iwerks made him as a
     replacement for Oswald the Lucky Rabbit; "originally to be named 'Mortimer
     Mouse', until Disney's wife, **Lillian**, suggested 'Mickey'"; his first two
     shorts **"were not picked up for distribution"** and the public debut was
     *Steamboat Willie* — the third attempt, which is a useful reminder that the
     famous version is usually the version somebody retried. The point of the
     entry is the licensing: **"Since his early years, Mickey Mouse has been
     licensed by Disney to appear on many different kinds of merchandise… from
     T-shirts to lunchboxes"**, run by **Kay Kamen from 1932 until his death in
     1949**, "a 'stickler for quality'". The pipeline needed somebody whose job
     was policing what the figure could appear on. Then two facts that tie it to
     the rest of the corpus: in 1978 **Mickey became the first cartoon character
     to have a star on the Hollywood Walk of Fame**, and he is "**a meetable
     character at the Disney parks**". A drawn figure who cannot hear you became
     a person in a room who can see you — `the-fourth-wall`'s argument arriving
     fifty years early, and arriving as a ticket price.
   - **`king-kong`** (1933, `character/fictional-protagonist`, `animate`) — the
     purest `animate` case here, and the argument is in the premise: "the story
     follows said gorilla dubbed Kong **who feels affection for a beautiful
     young woman offered to him as a sacrifice**". Cooper and Schoedsack,
     effects by Willis H. O'Brien, RKO, "live-action sequences with stop-motion
     animation using rear-screen projection" — `made` and `animate` in one
     frame. Premiered 2 March 1933; credited with having drawn the audience to
     *King Tut* two months later. Then the real entry: **"Various scenes were
     deleted by censors, but they were restored in 1970."** So for thirty-seven
     years the audience grieved a version of Kong with pieces missing — and the
     film had already earned $650,000 initially and $2,847,000 by the 1952
     re-release. Attachment forming around an artefact rather than a work, and
     the edit was a censor's rather than a studio's.
   - **`lugosi-burial`** (1956, `character/played-role`, `made`) — a correction
     with a large afterlife, and the reason the entry exists: **the most famous
     image in horror fandom is a document about the gap between an audience's
     picture of somebody and the person.** Lugosi died 16 August 1956 and "was
     buried wearing a Dracula cape, his full costume, and his Dracula ring" —
     true, and why the grave is a pilgrimage site. Then: **"Contrary to popular
     belief, Lugosi never requested to be buried in his cloak; Bela G. Lugosi
     confirmed on numerous occasions that he and his mother, Lillian, made the
     decision."** The romantic version is wrong and the true version is better:
     his son and mother chose it. **The myth was the better story**, which is
     the difference between this site and a fandom wiki. The record also names
     another unchecked famous last-image as a myth — that he died clutching the
     script for a planned Ed Wood film.
   - **A finding about the axes, from trying to place Valentino: the otherness
     axis has no member for a real person.** All six describe something invented,
     operated or transcendent; a film star is none of those, and forcing him
     into `made` would have been a different claim. He is left unplaced on
     otherness and placed `directed` on reciprocity, and **that is the clearest
     argument yet for why two axes were needed** — one cannot hold both "what is
     it made of" and "does it attach back" without losing one of them.
   - Two coincidences are recorded rather than conflated: Mickey was named by
     Disney's wife **Lillian**, and Lugosi's burial was decided by his son and
     **his** mother **Lillian**. Two different women, twenty-eight years apart.

20. **A resolving DOI is not evidence of identity, and Crossref will hand you a
   confident wrong answer.** Asked for thirteen titles, Crossref's bibliographic
   query returned a DOI for **all thirteen** and only **two** were the work being
   looked for. One of the eleven that were not resolved to
   `10.64628/aa.ketwakysr`, **"Man's stressed friend: how your mental health can
   affect your dog"** — for a citation about parasocial persuasion. Another to a
   2025 chapter called "Attention merchants" rather than Wu's 2016 book. **Every
   one of those URLs loads.** Attaching a DOI is therefore *not* verification,
   and it is the citation equivalent of `kind: exact` derived from a filename:
   `tools/verify_doi.py` exists so identity is checked, not assumed.
   - `--from-citations` audited all **44** DOI-bearing records by **author and
     year**: 25 MATCH, 8 MISMATCH, 5 UNCHECKED.
   - **Three of the eight were the tool's fault and reading them by hand is the
     only reason that is known.** Crossref stores one author as `C⌠Θ`, which is
     mojibake for **Côté**, so a correct DOI failed a name comparison; and two
     corpus citations **begin with the title and carry no author**, so the
     surname extractor read "Avatars" and "Stoking" as family names. The DOIs
     are right; the citations are incomplete, which is its own problem.
   - **Five are real and are recorded in `RESEARCH-NOTES.md` rather than fixed**,
     because each is a choice between a wrong date and a wrong locator and the
     corpus does not contain enough to decide. Four are year disagreements
     (`merten-identification` 2020 vs a 2023 DOI, `psr-grief-kutner` 2018 vs
     2015, `klastrup-facebook-mourning` 2015 vs 2014, `narrative-brands-end`
     2013 vs 2014). The fifth, `subscription-streams`, cites **"Alba, J. W." for
     a paper whose DOI lists Banerji, Gupta and Ketron** — the only one where the
     work itself may be wrong rather than the date. **None was corrected:
     choosing between "the year is wrong" and "the locator is wrong" without
     evidence is exactly the move this corpus exists to refuse.**
   - **The tool was wrong three times before it was right**, and each failure is
     the same defect this site keeps meeting:
     1. It compared the **whole citation** — eight authors, a journal, a volume
        and the words "Article 81" — against a bare title. All 44 came back
        MISMATCH, including `10.1145/3359183`, which *is* "Dark Patterns at
        Scale" by Mathur, Acar and Friedman, exactly what `loyalty-dark-pattern`
        cites. **Zero of forty-four is not a plausible result**, which is the only
        reason it was caught before anyone believed it.
     2. It compared surnames by trailing token, so an author Crossref stores
        given-name-first (`family: "Arunesh"` for Mathur Arunesh) compared a given
        name. Now every token of every name is tried.
     3. It let a title mismatch **override** a matching author and year, so a
        citation carrying a subtitle Crossref truncates read as a different
        paper. **Author and year decide; the title corroborates.** A citation and
        a registry routinely disagree about titles for reasons that are not
        errors — `11K Shopping Websites` against `Dark Patterns at Scale`, or
        `245-268` against `On the Dangers of Stochastic Parrots`.
     Each is a measurement confidently reporting on the wrong layer, and the
     first would have put a paper about dogs behind a claim about parasocial
     persuasion while looking thoroughly verified.
   - **A second index did not rescue the five, and that is the finding.** OpenAlex
     has Mori's **1970 Japanese original** ("Bukimi no tani", 1,457 citations, no
     DOI) and the **2012 IEEE English reprint** (`10.1109/mra.2012.2192811`) — and
     **nothing dated 1979 at all.** Crossref 404s the DOI that a plausible
     reading of the literature suggests for the 1979 English version, so it was
     **not written**. `the-uncanny-corridor` still cites "Mori, 1979" and the
     work queue records which three versions exist so somebody can read one.
     One index that cannot see the work is a fact about the index.

21. **A placeholder in `claim` is a to-do rendered to a reader, and the gate that
   catches placeholder citations never looked at the field next to it.** 41
   records across 40 entries carried **`claim: "the entry as a whole"`**. `claim`
   is what the page prints beside each citation as the substance of it, so in a
   provenance list that string reads like a reference supporting the whole entry.
   It supports nothing in particular. This is the citation-placeholder defect
   **one field over** — `citation_audit.py` checked `citation` and never inspected
   `claim` — and 41 of 384 records is 11% of all citation records.
   - All 41 were replaced with a sentence that states what the record actually is:
     *"No specific claim is recorded against this source. The record is a pointer
     to the work in general; the entry's own prose is the argument and is not
     sourced line by line."* That is **information** — "nothing specific is checked
     here" tells a reader something true — where "the entry as a whole" is a shrug
     wearing the grammar of a reference.
   - **The pattern is anchored, and deliberately so.** `transparasocial` has a
     claim *beginning* "The entry as a whole: transparasocial interaction as it is
     actually used in the literature…" and it is a good, specific claim. An
     unanchored match would have destroyed it. Confirmed by test: injecting the
     placeholder fails, injecting a three-character claim fails, and
     `transparasocial` survives untouched. **Using a phrase is not the same as
     being nothing but that phrase** — the same lesson as the `sasaeng`
     terminology check and the `kind: exact` record, and the third time this
     project has had to relearn it.
   - **And the corpus had a date contradicting its own source.** `green-shield`
     was dated **1912** while its own record's claim read "Launched in the United
     Kingdom in 1958" — a contradiction sitting inside one entry, in a corpus
     with a standing rule about dates disagreeing with their sources. Wikipedia
     settles it: Green Shield Trading Stamp Co was founded in **1958** by Richard
     Tompkins, who bought the name from a luggage manufacturer and copied S&H
     Green Stamps in America, and **the article contains no occurrence of 1912 at
     all**. Corrected. The 1912 appears to have been placed by analogy with
     `trading-stamps` at 1890 — the same mistake the *first-fans* entry made by
     association with an earlier era, and worth watching for.
   - Read by hand first: eight records whose citation overlaps their entry's own
     title were candidates, and **five were legitimate** — the Shanidar Cave
     *project* page, a scholarly article on Roman masks, a Canadian privacy
     report *about* Second Life, a named journalist's obituary piece, and Kempe's
     own primary text. Only three were circular, and two of those were the ones
     already fixed. **An overlap scan produces candidates, and a candidate is not
     a defect.**
   - **And relaxing the check produced an immediate false positive, which is the
     finding worth keeping.** Letting author+year be sufficient made
     `keep-it-or-lose-it` MATCH: the corpus cites `Jussila et al. (2020)` with no
     title, and the search returned *"Sensory Technologies for Improving Employee
     Experience and Strengthening Customer Loyalty"* — a different paper, same
     first author, same year, accepted. **An author and a year are a pair of
     coordinates, not a work.** Any prolific author has dozens of papers in any
     year, so the pair narrows a search and identifies nothing in it. It is
     enough to make a candidate worth reading; it is not enough to write down as a
     locator. `verify_doi.py` now refuses to return MATCH without title evidence.
   - **The blocker on the 63 entries with no locator is not the DOIs — the
     citations are too thin to verify a DOI against.** `verify_doi.py --find` ran
     against eleven of them; **0 verified**, not because no DOI exists but because
     nothing in the corpus distinguishes the right candidate from its neighbours.
     `parasocial-persuasion` states the diagnosis in its own citation field:
     **"Title and venue not yet recorded."** The entries are not missing a URL,
     they are missing the information a URL would be checked against.
     **So the order of work is: complete the citation first — author, year, title,
     venue — and the locator then becomes mechanically checkable.** Searching
     first produces candidates that cannot be confirmed, and a candidate that
     cannot be confirmed is exactly how `kind: exact` happened.

22. **The image queue was never blocked on human eyes, and I said it was.** Item 17
    downgraded all 73 records to `kind: "unchecked"` and correctly said a record
    only returns to `exact` or `illustrative` "once somebody has looked at the
    file". I then carried that forward as a blocker — **the largest remaining
    queue in the project, described as needing a person.** The agent doing this
    work can open an image and see it. Nobody tested the claim; it was assumed
    from the word "somebody".
    - **This is the second stale blocker in this file, and the pattern is worth
      naming.** Item 1 said all three episodes waited on voice recordings; the
      recordings existed, were muxed into the renders, and matched the episode
      durations to the hundredth of a second. Both times the blocker was a
      *description of a workflow* rather than a fact about the filesystem, and
      both times reading the artefact dissolved it. **A queue described as
      blocked should be attacked by inspecting the thing it waits on, not by
      re-stating the description.**
    - `tools/look.py` now does for images what `add_source.py` does for
      citations: takes the finding, records it, keeps it checkable. `python
      tools\look.py --list` shows the queue.
    - **It refuses `exact` and `illustrative` without a written finding**, because
      a bare date would reproduce the original defect in a new key — `looked`
      promising a look that nothing records. Three bugs in it, all mine, all
      found by using it: it stripped `--apply` from the argument list *before*
      testing for it, so it could only ever print a dry run; it demanded a
      minimum-length reason even when downgrading to `unchecked`, which is the
      one case that needs none; and downgrading left the `looked` date behind, so
      a reverted record still claimed to have been examined.
    - **I also wrote a finding against the wrong record** — the Taylor Swift
      observation landed on `madeonyoutube-spending-on-scoreboard` because I typed
      a slug from memory instead of reading it. Reverted, and the record is back
      to bare `kind: "unchecked"` with no residue. The project's own rule applies
      to me here: **verify the identifier before the judgement, not after.**
    - Four records opened, and the results were not uniform:
      | record | caption claims | what the frame showed | kind |
      |---|---|---|---|
      | `celebrity-death-feels-like-loss` | flowers and vigil candles outside the Embassy of the Netherlands in Tallinn | flowers and lit candles in glass jars, unambiguously — but **no signage and no distinctive architecture**, so the location is not visible at all | `exact`, with the location flagged as resting on `src` |
      | `agei-imaginary-friends` | a child playing alone on a beach | one child, wide beach, flat grey sky, digging with a stick. "Alone" holds — one person in frame | `exact` |
      | `ai-updates-feel-like-breakups` | a broken laptop | an HP L2000 with the LCD shattered across most of the panel, coloured artefacts down one band | `exact` |
      | `taylor-swift-red-knows-it` | Taylor Swift at the 2019 American Music Awards | a woman in a sequined green dress at a lit awards backdrop. **Nothing in frame identifies her or dates the event** | `illustrative` |
    - **The last one is the method.** Pixels cannot establish who someone is, and
      no amount of staring changes that; the identity and the year come from the
      `src` record. Recording "clearly Taylor Swift" would have been recognition
      dressed as observation. So the caption's specific claim drops the record to
      `illustrative` and says why — while the three generic captions, where the
      frame settles the matter, are promoted. **Look at the image to test the
      caption. Never look at it to confirm the caption.**
    - **The queue is 39, and it was reported to me as 64.** See the withdrawn-record
      bug below; getting this number right matters more than the count itself.
    - **Working the queue found a false caption, which item 17's sample had
      suggested was confined to the encyclopedia set. It is not.**
      `t8-1-rugrats-nest` was captioned **"A Reptar toy."** The picture is a
      **roller coaster** — green tubular supports, a yellow track, riders over a
      crest — with a sign reading `DRIVE IN / NOW SHOWING / RUNAWAY`, which
      points at the *Rugrats film*, not the character. The `reptar` must-term
      passed on the filename `Rugrat's Runaway Reptar` and on nothing else. The
      caption was not loose, it was **false**, and it went further: it claimed a
      photograph of the toy was *closer to the episode than a screenshot*, an
      argument about the episode's meaning that the picture it captioned cannot
      support. Caption corrected through `look.py --caption`, with the old text
      kept in `caption_corrected`. **One in nine of the checked story records was
      wrong, and 22% of the manifest had never been opened at all.**
    - **A triage falls out of that failure, and it is free.** The must-term is
      what admits a picture, so a caption that *never mentions its own must-term*
      is one where the validating word came from metadata rather than from the
      sentence a reader sees. Of the outstanding records, **10 name no must-term
      in the caption at all** and 53 name every one of theirs. The word-matching
      is crude in both directions — `autograph` against "A signed photograph" and
      `ocasio` against "Official portrait, 116th Congress" are both false alarms
      — so it ranks the queue and clears nothing.
    - **Six captions document their own defect**, which is the right instinct and
      the reason they are findable: `madeonyoutube-spending-on-scoreboard` is
      captioned *"A software bug-report form asking for a maximum date. Nothing to
      do with…"*, while its must-term is `youtube`; `oshi-katsu-half-century`
      says *"The filter is supposed to exclude charts and this one got…"*; and
      `aisle-contest` records that its previous picture was a pilgrimage site in
      the Philippines captioned as a public argument. Somebody wrote the failure
      down instead of quietly fixing it.
    - **That investigation produced a false alarm of my own, and the correction
      matters more than the alarm.** Sixteen captions are cut at **exactly 70
      characters, mid-word** — `"Nothing to do wi"`, `"this one go"`,
      `"The single wor"`. The cause is one line:

      ```python
      tools/apply_review.py:185    it["caption"] = note.split("REJECT. ")[-1][:70]
      ```

      So the path written to install a *better* caption truncates it. I called
      this a corruption of the manifest. **It is not.** That slice runs only on
      the `REJECT` branch, which strips `local`, `src` and `cached` — all 16 are
      **withdrawn** records, and none of the fragments appears anywhere in
      `dist/`. Ugly, invisible, not a reader-facing defect. **I reported a
      systemic corruption before checking whether the affected records were
      reachable by a reader, which is the one question that decides it.**
    - **But chasing it found a real bug, in the tool I had just written.**
      `look.py --list` reported the queue as 64 records, "25 need fetching". All
      25 are withdrawn: no cached file, no source, deliberately rejected.
      **Nothing to fetch and nothing to open.** The real queue is **39**, so the
      list overstated the work by 39% and pointed at twenty-five images that
      cannot exist. `look.py` now separates openable, fetchable and withdrawn, and
      prints the real queue beside the one it used to report, so the number
      cannot drift back. **A queue
      that tells you to fetch work which cannot exist is worse than no queue,
      because it looks like progress and costs a pass to discover.**

## Deploy note

`dist/` must be re-uploaded after each build. It is routinely ahead of
production. `python tools\daily.py` reconciles the day's record, rebuilds,
runs the post and source gates and packages `dist/` in one pass, so it is the
command to run before an upload. `python tools\build_deploy.py` is the
packaging half on its own; `--no-build` is for `gates.py` and for the daily
loop's final re-package, never for a deploy by hand.

The daily GitHub job can publish `dist/` itself: set repository secrets
`CLOUDFLARE_API_TOKEN` and `CLOUDFLARE_ACCOUNT_ID`, and optionally the variable
`CLOUDFLARE_PAGES_PROJECT` (default `parasocialize`). Without them the publish
step is skipped, the job still builds/commits/artifacts, and the upload stays
manual. The token needs Pages:Edit on that account.

13. **Asked to cull the extra-sensory references, the honest answer was that
   there are none — and the check that looked like it found thirty was wrong.**
   The instruction was to "cull all the extra-sensory, even seemingly one-sided
   references". What the scan actually found, of 189 entries:
   - **Zero** assert that the far side perceives the reader, the viewer or the
     listener by non-ordinary means. A wider sweep — séance, spiritualism,
     mediumship, channeling, possession, reincarnation, astral projection,
     psychokinesis, clairvoyance, precognition, premonition, tarot, oracle,
     guardian angel, third eye, aura — returned **1 of 189**, matching on the
     word *personified* in `the-imaginary-friend`, where a child personifies a
     toy. That is not extra-sensory.
   - The two entries that first looked like hits are both correct and were
     checked in context. `the-teacher`: an authority figure "who knows your
     name, your mood and your home situation" — he sees you every day, in a
     room. `saturday-mornings`: "a writer who knows your name" — the
     Saturday-morning show *asking* its audience for their names, which is
     ordinary interaction in the cheapest possible register.
   - **Nothing was culled.** There is nothing to cull.
   - The important part is the trap the request nearly walked into. An earlier
     sweep matched **30 entries** on `one-sided`, `does not respond`,
     `no reciprocity` — and that is **this site's own name for the thing it is
     about**, 220 uses of it across the corpus. A cull driven off that list would
     have deleted `the-dog`, `myth-and-ritual`, `parasocial-interaction`,
     `transparasocial` and 26 others, i.e. the subject. **Using the phrase is
     not making the claim.** This is the borrowed-terminology diagnostic one
     level up — that one fired on `sasaeng` and `crossover`, both correct — and
     it is now a standing rule for any future "remove all the X" instruction:
     *count how many of the hits are the definition before removing any of them.*
   - The distinction that makes the property checkable at all, and it is the
     thing most likely to be got wrong again: **a figure answering somebody
     inside the story is two-way in the fiction and one-sided for the reader.**
     Harvey answers Elwood and is the clearest case of the phenomenon on this
     site; culling on in-fiction response would cull the best entries in the
     corpus. The test is narrower than it looks: has the far side perceived
     *this* reader?
   - `tools/cull_audit.py` now holds the check, so the claim is testable rather
     than asserted. It has three tiers — fails on audience perception, reports
     ordinary perception and in-fiction response, and **never** flags the
     site's definitional vocabulary. Confirmed red by injecting a real
     audience-perception claim into two different entries and checking the exit
     code, and confirmed green on the corpus as committed. The first version
     did **not** go red on that injection, which is how four more patterns
     (`knows-individual`, `sees-into-room`, `watches-in-private`,
     `seen-only-by-one`) are in the file: a gate that cannot fail is decoration,
     and one that fails too little is worse, because it reads as clearance.
   - **What it cannot do:** this property is contextual and no regex is complete
     for it. The gate catches unambiguous phrasings; the claim that the corpus
     is clean also rests on having read the hits. Same reason the terminology
     check is report-only.

12. **The corpus had no imaginary friends, no puppets and no aliens, and the
   taxonomy had no way to say so.** Asked to check whether named instances had
   been researched across literature, music, TV and film and sorted by kind of
   otherness, the honest answer was no. A scan of all 183 entries found the kind
   split running `mechanism=64, event=45, term=25, work=20, person=17, study=8,
   case=3, institution=1` — that is, a corpus of *categories and formats*, not of
   *instances*. `work` covered media formats; `case` covered three events. Named
   fictional characters were essentially absent. A keyword scan found `imaginary
   friend` 0, `conscious non-human` 0, `stuffed object` 0, puppet/doll 2
   (incidental), shadow/projection 3 (incidental), supernatural 16 and divine 7.
   Both of the existing axes turn out to be blind to this, and for the same
   reason: `attachment` asks what role the other end plays and `register` asks
   what is happening in the tie, so an invented friend, a worked puppet, a
   chatbot, a ghost and a god all file identically. A third axis was added
   rather than an entry moved.
   - **`otherness` has six members**, each with the same def/test/not/mechanism
     every attachment sub-category carries, and `verify_taxonomy.py` checks them
     structurally so the axis cannot rot the way the corpus did:
     `imagined` (the audience knows they invented it), `made` (somebody or
     something is operating it), `animate` (a non-human given a mind),
     `transcendent` (addressed rather than met), `mirrored` (supplied by the
     person attached to it), `haunted` (believed present and unverifiable).
- The value is the `test`, not the caption. Each is a question a person
       actually has to answer when filing something new: *does the audience
       know they made it; is somebody working it; does it have a mind they
       cannot edit; is it addressed rather than met; did they supply the whole
       figure; do they believe something is there.*
   - **Placing the axis is optional per entry**, and the audit reports how many
     do: 13 of 189. Requiring it everywhere would be the same move as filling a
     hole to make a chart look even. `verify_taxonomy.py` prints the count per
     member and names any that hold nothing.
   - **Two different things are now true and the difference matters.** Four of
     the six shelves are held by a *new entry written for the shelf* —
     `mirrored` by `dorian-gray`, `haunted` by `casper`, `animate` by `alf`,
     and `made` by `the-shadow` alongside `howdy-doody`. `transcendent` is
     held by four **re-readings of entries that already existed**
     (`mystical-union`, `margery-kempe`, `the-book-of-my-first-showings`,
     `gobekli-tepe`), where the test answers cleanly and the entry was already
     about address. That is classification of material in hand, not gap-filling,
     but it is a weaker kind of coverage and the page does not claim otherwise:
     the shelf has no named instance yet. **Populated and exemplified are
     different states, and the audit only counts the first.**
   - Three of those re-readings changed what the entries claim, which is why
     the reasons are appended to the existing `why` and printed:
     `neanderthal-burial` and `sunghir` are **`haunted`, not `transcendent`** —
     nobody addresses the dead there, they are kept within reach and treated as
     somewhere you go, which is belief in presence with nothing to verify it.
     `roman-imagines` is **`made`** — an actor walks the mask in the funeral
     procession and the *titulus* does the conversing, with the eye-holes and
     lip gap cut so the **actor** could see and speak. Filing it as
     `divine/saint-ancestor` had implied address; the entry's own evidence says
     somebody is working it.
   - Four entries were added from the user's requested categories, one per
     shelf, and each is a specific instance rather than a format:
     - **`dorian-gray`** (1890, `character/fictional-protagonist`, `mirrored`) —
       `companion/social-agent` would be wrong, nobody lives with the picture.
       The evidence is four lines of dialogue read from the Project Gutenberg
       full text, not a summary: Hallward, who loves the man he has painted,
       answers the original's question — *"Am I really like that?"* / *"Yes;
       you are just like that."* / *"At least you are like it in appearance.
       But it will never alter."* The real man is standing right there and is
       also the wrong one. And the mirror: having seen cruelty in the painted
       mouth he looks at his own red lips to check, and *"No line like that
       warped his red lips"* — the one witness that could have settled it
       exonerates him, and he is not permitted to be the evidence about
       himself. First published July 1890 in *Lippincott's Monthly Magazine*,
       the only novel Wilde wrote.
     - **`the-shadow`** (1930, `companion/anthropomorphised-tool`, `made`) —
       Street & Smith hired an ad agency and a writer-director to sell a pulp
       magazine on the radio. Their plan was "a mysterious storyteller with a
       sinister voice" and then they needed a name for him, which a scriptwriter
       supplied. **Listeners found the announcer far more compelling than the
       unrelated stories and began asking newsdealers for "that Shadow
       detective magazine, even though it did not exist."** A one-sided bond
       that generated demand for a physical object nobody had manufactured. Two
       honesty notes kept: in the *magazine* stories the Shadow did not become
       literally invisible at all, and the famous line is a radio adaptation's,
       spoken by Frank Readick Jr. His power set is built around this site's own
       subject — he can turn invisible *"except for his shadow, which cannot be
       hidden, for unknown reasons."*
     - **`alf`** (1986–90, `companion/social-agent`, `animate`) — filed
       `animate` on the evidence of the character, with the caveat **on the
       entry** rather than resolved by fiat: he is performed by Paul Fusco
       inside a fur suit, and full-body shots by Michu Meszaros, uncredited.
       **The axis has no rule yet for a figure that is simultaneously animated
       and operated, and this entry is the case that proves it.** What makes it
       more than a technique note is that the withholding was deliberate and
       stated as method: *"Fusco insists that many people believe in Alf just
       as they believe in Santa Claus, and he is not about to spoil the
       illusion. So many people want to believe he's real... When you know how
       it's done, it's just not as fascinating anymore."* The evidence it
       worked, from the same 1987 piece: he *"gets invited to birthday parties
       nearly every day"*, and *"mothers have told cast members that their
       children cry every Monday night when Alf ends."*
     - **`casper`** (1945, `companion/social-agent`, `haunted`) — made to
       answer a four-year-old's fear of the dark: according to Joe Oriolo, a
       cardboard cutout of a friendly ghost hung in a backyard tree to show his
       daughter Joan *that not all ghosts are bad*. A ghost built as an
       intervention against a specific fear, for one named child — the most
       parasocial brief a supernatural figure has ever had, and the only part of
       it that is checkable. **The origin is genuinely disputed** and both
       sides are recorded: Oriolo's cutout, corroborated by Joan, against
       Seymour Reit's claim to a short story he wrote alone and handed over to
       illustrate. Filing contested authorship under one name would be lying.
       And the detail nobody chose: the Apollo 16 command module's call sign was
       Casper, its pilot explaining that *"there are enough serious things in
       this flight, so I picked a non-serious name."*
   - Seven records were added and six are `retrievable`. One is `unverified` —
     the Chicago Tribune obituary corroborating Oriolo's side of the Casper
     dispute returns 403, so this agent did not read it, and the claim records
     that it is cited by Wikipedia for the same statement rather than verified
     here. Project Gutenberg's full text, the *Los Angeles Times* ALF piece
     (23 December 1987) and four Wikipedia articles were fetched and read.
   - **Two media had to be added before any of this could be filed honestly.**
     `MEDIA` in `tools/atlas.py` was a closed list of eleven, validated per
     entry, so a radio serial or a comic could not be recorded without lying
     about its medium — and `radio-serials` was sitting in the corpus dated 1930
     with `medium: history`, the value 57 entries use as a catch-all. A missing
     medium in a validated closed list is not an inconvenience: it is a hole in
     the classification that surfaces as a gap in the corpus. `radio` and
     `comics` were added to `MEDIA`, `MEDIA_LABEL`, `MEDIUM_NAME` and
     `MEDIUM_ORDER`, and `radio-serials` was re-filed from `history` to
     `radio`. Both renderers degrade safely on an unknown key — `backdrop.SYSTEMS`
     and `iyi._system()` each fall back by year — so this cannot break episode
     rendering; what it does mean is that a radio entry draws the theatre
     backdrop until somebody writes a radio system, which is the honest artefact
     of a real hole.
   - **`cliffhanger` is dated 1930 with `medium: television_scripted`**, which
     cannot both be right — television broadcasting had not begun. The same
     year as `the-shadow`, which suggests a seeded or copied date. **Not
     changed here**, because correcting it needs a source rather than a
plausibility argument, and it is on the list for a date check.
   - The first two entries came from the two ends of the new axis in one pass.
     **`the-imaginary-friend`** (1934, `companion/social-agent`, `imagined`):
     Pearson et al. 2001, 829 children, 46.2% reporting imaginary companions;
     Carlson & Taylor, 65% by age seven, 52% of preschool companions being props
     and 67% of school-age ones invisible, 57% human and 41% animal, and **27%
     describing a friend their parents did not know about**. Its mechanism is the
     inverse of every other entry here — the child *knows* they invented it, so
     it is the one relationship on the site that cannot be mistaken for a
     misreading. Davis et al. supplies the consequence: children with an
     imaginary companion described their *real* best friend in mental terms 29.6%
     of the time against 12.6%. The foster-care sample was included precisely
     because it reports a **negative** — prevalence did not differ by maltreatment
     history — and a common behaviour must not be filed as a marker of damage.
     **`howdy-doody`** (1947–1960, `companion/anthropomorphised-tool`, `made`):
     the first television character answered by name, thirteen years and ~2,500
     episodes of "Say, kids, what time is it?" / "It's Howdy Doody time!", with
     the voice usually **recorded before the broadcast** — the parasocial
     condition engineered rather than suffered. Clarabell the Clown never spoke
     for twelve years and said one line, "Good-bye, kids.", in the final episode.
     And the puppets were sold as toys through the 1950s, so the tie moved from
     something you cannot touch to an object in your hands, which is this site's
whole thesis inside one commercial decision.
   - Those first eight records are six `retrievable`. Two
      Smithsonian records are `unverified` because both `si.edu` and
      `americanhistory.si.edu` return **403** to an unauthenticated request — and
      per item on HTTP codes, that is a different failure from the Met's 429 and
      gets the same treatment: the claim is recorded, the status says this agent
     did not open it.
23. **Generated encyclopedia art exists, and both rejections happened off-camera
    because nothing recorded them.** The image layer item above is about the 73
    photographic records; this is the other half, and until now `AGENTS.md`
    documented none of it - no policy, no tools, no seeds, and no record of the
    two frames that were thrown away. A rejection with no written reason is a
    rejection that gets attempted again, which is the whole argument this file
    makes about `RESEARCH-NOTES.md`.

    - **The rule, and it is narrower than "AI art is fine".** Generated art is
      author-owned and therefore always safe to *license*, which is not the same
      as safe to *use*. It is **permanent `illustrative`, never `exact`** - a
      generated image can never be evidence of what a real place or person looks
      like. And for the encyclopedia layer it is **atmosphere, never depiction**:
      nothing that stands for the entry's actual subject. **No real people, ever**
      - that one is absolute, not a register question.
    - **Why "atmosphere, never depiction" rather than a softer rule.** The first
      attempts asked for the entry's subject and got it wrong in the direction
      that matters: `neanderthal-burial` was asked for a burial and rendered a
      standing human figure, because the only way a text-to-image model can draw
      a burial is by drawing someone. `paleolithic-figures` is the same failure
      arriving by a different route - asked for atmosphere and delivered a
      **person in a modern hooded coat sitting on rocks in a warm desert at
      sunset**, for an entry about mammoth-ivory carvings from Ice Age Europe.
      Both withdrawn. **The subject is what pulls a figure into frame**, so the
      prompt has to stay away from it deliberately rather than be told to avoid it
      (see the next point).
    - **A negative constraint in a prompt is decoration.** Every prompt carries
      "no people, no text, no modern objects" and **flux1-schnell ignored all
      three** - it produced a hooded coat. Nothing about a 4-step distilled model
      makes it attend to a negative instruction, and `cfg: 1.0` is required
      (anything higher fights the distillation). **So every frame is opened
      before it is promoted, and there is no prompt that removes the need to
      look.** Three of seven survived inspection; four were opened and three
      passed while one was withdrawn. That 3-in-7 rate is the argument for the
      queue being a queue.
    - **The promoted seven**, all `illustrative`, all with a written finding:
      `the-dog` (two small distant silhouettes), `roman-imagines` (paper-toned
      wash - the signature-like corner mark removed by a 3% margin crop),
      `sunghir`, `gobekli-tepe`, `myth-and-ritual`, `the-absent-sage`,
      `the-deaf-beloved`. The last three were opened 2026-10-05 and the reasons
      are in `data/images.json`: emptiness and scale turned out to be the
      *correct* register for an entry about ritual older than narrative, a sage
      who survives only as writing, and a beloved who is deaf and therefore
      never learns the terms. **An image that depicts nothing can still be the
      right picture**, which is not an argument for generating more of them.
    - **Weights, verified rather than assumed.** `ComfyUI-Shared/models` holds
      **11 files, 68.1 GB**, every safetensors header read clean - a truncated
      download reads as a valid file of the wrong size, so the header is the only
      check that means anything. Only **`flux1-schnell-fp8`** (17.2 GB) has been
      used, for these 7 images, at `steps: 4, cfg: 1.0`, seeds
      `20261004 + n*7` so a run is reproducible. The other 7 weights are **video**
      (MiniMax H3 + turbo LoRA, Wan2.1, LTX LoRA, Qwen3-VL) and **nothing has been
      generated from any of them.** `extra_model_paths.yaml` is written outside
      the repo and four ComfyUI installs exist with empty `models/` dirs, so the
      MiniMax/Wan/LTX downloads were inert until it was written.
    - **`generation.size` records 1152x560 and every file is 1084x528**, because
      all of them were margin-trimmed after generation and only `the-dog` said so
      in `crop`. Sixth instance of *a status field is a promise*: the value is
      not wrong, it answers "what did you ask for", but a tool reading it opens a
      file of a different size. `generation.final` now carries the dimensions of
      the PNG on disk and `image_audit.py` checks it against the PNG's own IHDR.
      Confirmed red by resetting `sunghir`'s `final` to the stale value.
    - **Provenance for these 7 lives only in `data/images.json`.** The PNGs carry
      no ComfyUI fingerprint and `ComfyUI-Shared/output` is empty, because
      `gen_atmosphere.py` copies results into the repo itself. That is a single
      point of failure for a claim about how a picture was made, and it is
      recorded here rather than assumed.
    - Tools: `tools/gen_atmosphere.py` (data-derived prompts, writes new records
      as `unchecked` with a seed and never as `exact`),
      `tools/withdraw_image.py` (deletes record **and** file, asserting the item
      count, because downgrading to `unchecked` leaves `local` pointing at an
      asset nobody approved - the same shape as the 94 URL-less `retrievable`
      records), `tools/record_image_size.py`.
    - **One honest limitation.** `look.py` discards the finding when you
      downgrade to `unchecked`, which is right for a record that stays and wrong
      for a rejection - the reason is the only surviving record of what the model
      did. `paleolithic-figures`' finding was lost that way and is written out in
      this item instead. **A tool that keeps the evidence only while the record
      survives is a tool that loses exactly the findings worth keeping.**

24. **A freely-licensed screenshot of a chatbot returning suicide methods was
    rendering on eleven pages as decoration, and `image_audit.py` could not have
    caught it.** Item 22's queue is real work rather than a blocker, so six
    records were opened. One of them, `8432d33b1d39ab`, is a Replika
    conversation in which a user asks the bot for methods and it returns **an
    enumerated list of them** - overdose, hanging, shooting, jumping, stabbing,
    cutting - with the avatar being a real identifiable person's photograph.
    It was the picture on `i-tried-replika`, `replika-users-lost-them`,
    `character-ai-settlement`, `neuro-sama-tops-twitch`, `sculptor-fell-in-love`,
    `eu-kids-act-companion-chatbots`, `companion-safety-controls`,
    `ai-updates-feel-like-breakups`, `pygmalion-sculptor-illusion`, the
    companion section front and the credits page.
    - **The licence was fine and the problem was not licensing.** The Commons
      record is Public domain and the authorship is correct. Every existing check
      would have passed it: the file existed, it had a licence and a page and a
      credit, its caption described its frame, and its `must` term (`chatbot`)
      was satisfied. **A picture can be perfectly licensed and perfectly
      accurately captioned and still be the wrong thing to publish**, and no
      field in this manifest is about that. `licence` answers "may I show it",
      never "should I".
    - **`withdrawn` is not `rejected`, and conflating them loses the finding.**
      Deleting the row would have made the audit green and destroyed the only
      record that the screenshot exists and is openable - which is a fact the
      corpus wants, because the entry is *about* it. So `kind: "withheld"` keeps
      the record, nulls `local`, keeps `src` with `usable_as_image: false`, and
      carries `withdrawn_reason` in full. `tools/withdraw_image.py --keep-record`
      does it and asserts the item count.
    - **The audit now holds the refusal to its proof, the same way it holds a
      claim.** A `withheld` record with a non-null `local` fails, because a
      withheld image a page can still reach is not withheld; one with no
      `withdrawn_reason` fails, because a refusal nobody can read is
      indistinguishable from a mistake. Confirmed red by restoring `local` and
      blanking the reason, then green on restore.
    - **What this does not solve, stated plainly.** A gate can hold a field to
      what it promises; it cannot read a picture. There is no automatic check
      that would have found this, and pretending a manifest rule would is the
      `kind: exact` mistake a third time. **The check is a person opening the
      file, which is why item 22's queue is a queue and not a gate.**
    - **The other five, for the method's record.** `youtubetv-living-room` is the
      first `exact` promoted in this batch and the reason is worth copying: the
      caption says "a person watching an analogue television set", the frame is
      precisely that, and **no part of the caption rests on `src`** - so pixels
      settle it. It is also the better picture for the entry, since a household
      gathered around one set *is* the argument. `gloria-steinem-and-dolly` is
      `illustrative` despite looking like a clean portrait, because a **lavalier
      mic is clipped to the jacket** - the frame carries its own evidence of the
      recorded interview the entry is about, while identity and year still come
      from `src`. `i-tried-replika` is a flat vector cartoon avatar and the
      ceiling is `illustrative`. And **`fearne-cotton-free-tv` was a false
      caption**: it said "2014" while the step-and-repeat behind her reads
      **AWARDS 2015**. I cannot tell whether Commons misnamed the file or the
      banner was reused, so the caption now says "at an awards event" and the
      disagreement is written into the reason instead of being resolved by
      guessing a year.

25. **A blanket sentence about six pictures was false for three of them, and the
    enumeration on /top8/ was wrong twice - both written before anyone opened
    the six.** The front page said:

    > Not one frame of these cartoons is freely licensed, so **every picture
    > above is of the audience instead** - which is the list.

    First clause true. Second clause false. Opening all six `t8-*` records:
    `t8-1` is a **roller coaster** with green tubular supports and a RUNAWAY
    sign; `t8-2` is **Rugrats-themed baby shower decor**; `t8-6` is the cast on
    a **Comic-Con panel**. Only `t8-3`, `t8-4` and `t8-8` are the audience.
    **Three of six.**
    - **And /top8/ made the same claim as an enumeration**, which is worse
      because an enumeration names each one: it promised "a Reptar toy in a
      shop" and "a cast photo from a film that is not the show". The first is a
      roller coaster - the `reptar` must-term passed on the filename, exactly the
      failure item 22 found. The second is a convention panel. **Both had been
      wrong the whole time, in public, on the page whose entire argument is that
      it does not lie about its pictures.**
    - **The rewrite is a better sentence, not just a true one.** What the six
      share is not that they are all audience shots but that the cartoons left
      the screen and became objects - cosplay, a panel, a party, a coaster built
      out of Reptar. That is more or less what this site is about, so the honest
      version is also the sharper one. The old sentence flattened a set of six
      different kinds of evidence into one claim in order to make it short.
    - **The general form: a claim about every member of a set is a claim about
      the set, and it is exactly as falsifiable as `kind: exact` was.** The must
      term, the `retrievable` status, the plate's category, the citation board -
      all of them summarise many things and are all verified by opening the
      things. **A summary sentence is not a shorter citation, and it is checked
      the same way: by looking at every member.**

26. **Every year in an image caption was copied from a filename, and two of the
    seven that have been checked against their own frame were wrong.** Fourteen
    captions assert a year. Extracting the year from each caption and from its
    Commons filename gives **zero disagreements** - which sounds reassuring and
    is the problem: agreement between a caption and the filename it was written
    from is not corroboration, it is a copy.
    - `fearne-cotton-free-tv` said **2014**; the step-and-repeat behind her reads
      **AWARDS 2015**. Corrected to "at an awards event", with the disagreement
      written into the reason rather than resolved by guessing which is right.
    - `history-fan-letters` said **1942**; the letter is headed **May 6th, 1940**
      with a Richard Rodgers letterhead and signed "Dick". Corrected to what is
      legible.
    - **So a caption date is a filename until the frame is opened.** Eight
      captions still assert an unopened year, and the two that were opened and
      checked were wrong 2 times in 7. `tools/look.py` is the only thing that
      converts one into the other.
    - **My own probe was wrong first, in the way this file keeps predicting.**
      The cross-check used `\b(1[89]\d\d|20[0-2]\d)\b`, and `_` is a word
      character, so `\b1984\b` never fires inside `Dolly_Parton_1984.jpg`. Every
      Commons column came back empty and the report claimed seven captions
      disagreed with their own filenames. **Seven is not a plausible result** and
      that is the only reason it was caught before it was believed - the same
      reason `0 of 44` was caught in the DOI tool. Fixed to `(?<!\d)\d{4}(?!\d)`,
      and the true answer is zero disagreements, which is the finding.

27. **The image queue is empty. 54 of 79 records have been opened, 8 exact, 38
    illustrative, 8 withheld, and the remaining 25 are withdrawn records with no
    file and no source - there is nothing left to open.** Closing it turned up
    three things that no gate was looking for.

    - **Seven section illustrations were withdrawn, and the long-standing "fix
      the 7 fake Flickr credits" item was mis-framed.** All seven carried
      `src.page` of `https://www.flickr.com/photos/` with **no photo identifier
      after it** - a bare domain root, so there is no locator and no reader can
      open the work. The author field was `nobody@flickr.com ("Real Name")`, so
      the photographer is named in brackets and the placeholder sits in front of
      them. They were also **160x240 to 240x200 pixels**, which cannot serve a
      section front at any width the layout uses, and **no page in `dist/`
      referenced any of them** - the section fronts render story photographs.
      The task was never "fix the credits". They cannot be credited, because
      they cannot be attributed, and they are not in use. Withdrawn with
      `--keep-record`, so the real photographer's name and the CC 2.0 licence
      stay on the record and the reason says what is missing: the work.
      **If section art is wanted it has to be fetched from a source that names
      the photograph.**
    - **Two records pointed at one byte-identical picture, and a caption
      correction silently left the other copy asserting the corrected thing.**
      `t8-6-powerrangers` and `moment-power-rangers` are the same Camp Conival
      panel under two different Commons pages - sha256 `b41dd4b665b9...` - and
      both were captioned "The cast of the Power Rangers film". The caption was
      corrected on the first and **the second kept the false claim through the
      correction and through two commits**, because both files existed, both
      had licences and pages and credits, and both could be opened and judged
      independently. Nobody can see that a judgement was recorded twice for one
      image. `image_audit.py` now hashes every file and reports duplicates,
      **confirmed red** by promoting one Taylor Swift copy to `exact` while its
      twin stayed illustrative with different wording.
    - **The duplicate check was wrong for one run, in the direction that matters.**
      Its first version failed on *any* caption disagreement, and it flagged the
      two Taylor Swift records - both correctly capped at `illustrative`, both
      naming a person the frame cannot establish, which **is this site's own
      convention**: `kind: illustrative` is the field that says src did the
      identifying rather than the pixels. It now fails only when one copy claims
      `exact`, because exact means the frame settled it and one set of pixels
      cannot settle two captions; everything else prints as a note. **A gate
      added in a hurry has to be argued with before it is trusted, and this one
      cried wolf on correct data.**
    - **Four false or loose captions in the last stretch**, all now corrected
      against what the frame shows: `figure-peewee` claimed "Paul Reubens, with
      the David Hasselhoff Chalk painting, CalArts" and **there is no painting in
      the frame** - it is four people in CalArts smocks waving at a graduation,
      and none of the three people in the Commons filename can be picked out of
      four in a soft photograph. `aisle-companion` claimed the phone was "lit by
      its own screen" and the frame does not support it. `history-fan-letters`
      said 1942 for a letter headed 1940. `fearne-cotton-free-tv` said 2014 under
      a banner reading AWARDS 2015.
    - **The three `exact` promotions in this stretch are the method working as
      intended**, and each is exact for the same reason - the frame carries the
      caption's hardest claim: `youtubetv-living-room` (a person watching an
      analogue set, and a household around one television *is* the argument),
      `idol-economy-four-dollars` (a Texas Jam '79 stub whose $15.00 and ADMIT
      ONE are the unit of account printed on the artefact), `characters-we-keep`
      (a reading room the must-term is satisfied by rather than by a filename),
      and `t8-8-animaniacs`, where a convention badge on a cosplayer's waistband
      reads WONDERCON 2012 - so the event and the year are legible in the picture
      rather than only on Commons.

28. **148 citation records had no locator. 16 of them did not need research - they
    were short-form second references to a work the corpus already locates, and
    attaching the existing locator took the backlog to 132.** The corpus cites
    the same paper twice in several places: `free-trial-bait` cites Mathur et al.
    2019 once in full with `10.1145/3359183` and once as "Mathur et al. (2019)."
    with nothing. `crossover`, `siri`, `the-priest`, `congregation`,
    `characters-move-in`, `grief-extraction`, `beatlesmania` and `free-trial-bait`
    all do it, and several do it **on the same entry**. That is not a research
    backlog - it is a citation asserting a locator the site has already verified.
    `tools/attach_twin_locators.py` does it on `exact` (identical once normalised)
    or `prefix` (one string is the other plus a subtitle) evidence only, records
    where each locator came from in `locator_from`, and asserts the record and
    entry counts before writing. **236 -> 252 records with a locator, statuses
    unchanged, nothing promoted to `verified`.**
    - **A locator is not a reading, and the page now says so.** The attached
      record renders as "Mathur et al. (2019). ↗" and still reads `unverified`
      and "Not yet stood behind" underneath. A URL answers "can a reader open
      this"; it does not answer "did somebody read it". Same family as the 94
      `retrievable` records with no URL, running the other way.
    - **The strict evidence rule is there because AGENTS already records the
      loose version failing.** Letting author+year be enough made
      `keep-it-or-lose-it` MATCH a different paper by the same first author in
      the same year, and that paper was then accepted. **An author and a year
      are a pair of coordinates, not a work.** 30 records match on surname and
      year alone and are left alone.
    - **And the prefix rule needed one more guard, found by reading a pair rather
      than a match.** `prince`'s short form is "CBS News (2016)." and the sibling
      is a **compound** citation - "CBS News (2016), citing photographs and CBS
      Minnesota; NPR, Music Legend Prince Dies At Paisley Park" - carrying
      **one** URL, the NPR one. Attaching it would have put a wrong outlet's link
      on a CBS citation: a fresh false attribution, worse than the honest gap the
      tool exists to close. `cobain` has the identical shape and is correct only
      by luck, because that URL happens to be the Seattle Times one. **Luck is
      not a rule.** Compound citations are now refused outright: 21 candidates
      became 16.
    - **And the first version of the prefix test fired on only the easy half of
      its own rule.** `norm()` strips the trailing full stop, so after stripping,
      the remainder of "mathur et al. (2019). dark patterns at scale" begins with
      `". "` - and the boundary test was `nxt[:1].isspace()`, which is false for
      a period. Every case of exactly the shape the class exists for was being
      silently dropped, and the first run reported 3 matches where there were 7.
      **A filter that only fires on the easy half of its stated rule looks
      exactly like a filter that is working.**
    - **What this does not fix, stated plainly: 132 records remain, and about 112
      of them cite a work the corpus holds nowhere else.** Those are real
      research tasks - a student dissertation behind a paywall, a 1994 newspaper
      item, a book with only a publisher page. The cheap-win note in item 5 -
      "anything with a DOI" - is **stale**: 0 of the 148 carried a DOI in its
      citation string, so every one of them needs the citation completed before
      the locator becomes checkable, which is item 21's conclusion again.

29. **`AGENTS.md` told me to cite sources with a tool that cannot cite anything,
    and my recall of a DOI was wrong twice in one sitting.** The file says "Cite
    sources via `tools/add_source.py`, not by hand-editing JSON." That tool does
    two things: print a report, and recompute provenance. **It takes no entry and
    no citation.** Anyone following the instruction would run
    `add_source.py <entry> "<citation>"`, get a silent no-op, and leave
    believing a source had been added - and a no-op that looks like success is
    worse than a tool that admits it has none. `tools/cite.py` is that path now:
    it adds or updates a record, refuses thesis entries, asserts the record
    count and the top-level keys, and records what it did and did not check in
    `identity_verified`.

    - **It checks a DOI for IDENTITY, not resolvability, and it earned that on
      the first real citation.** The obvious DOI for Weizenbaum's ELIZA paper -
      the one I reached for - `10.1145/360018.360022`, resolves perfectly to
      *"Computer science as empirical inquiry"* by **Newell and Simon, CACM
      19(3), 1976**. Not ELIZA. Writing it would have put a confident,
      loadable, wrong citation on the site's most famous AI entry. The real one
      is `10.1145/365153.365168`, found by **searching Crossref by title** rather
      than recalling it - and even then Crossref returned three plausible
      answers, including a 1983 CACM reprint and a 2021 MIT Press collection, so
      volume 9 issue 1 pages 36-45 had to be checked before the DOI was accepted.
      Confirmed red by feeding it the wrong DOI: *"NO shared author surname.
      Refused."*
    - **The same trap, second instance, on the next citation.** My recalled DOI
      for Winograd's *Understanding natural language* was
      `10.1016/0010-0285(72)90004-0`. The real one ends **`90002-3`**. Again
      found by searching Crossref, which confirmed Winograd, *Cognitive
      Psychology* **3(1), 1-191, 1972**. **Two out of two recalled DOIs were
      wrong, and both were wrong in the direction that looks fine.** This is item
      20's finding arriving in the corpus's own most-cited entries, and it is the
      strongest argument for making identity a gate rather than a habit.
    - **A regex over free text cannot parse a DOI.** The first attempt at
      `shrlu` was **refused**, because the character class excluded `)` and
      truncated `10.1016/0010-0285(72)90002-3` to `10.1016/0010-0285(72`. Old-style
      Elsevier DOIs embed the year in parentheses, so that is a whole real class
      broken by a detail. **The tool failed in the right direction** - refusing
      rather than writing half a DOI - but the fix is to take everything after
      `doi.org/` in the URL, because DOIs may legally contain `(`, `)`, `;`, `<`
      and `>`. Regex is now only the fallback for a bare DOI.
    - **Both records were ambiguous rather than wrong, and naming the work is
      what fixed them.** `Weizenbaum, 1966` did not say which of two works: the
      **1966** CACM paper (9(1), 36-45, doi 10.1145/365153.365168) or the book,
      ***Computer Power and Human Reason*, which is 1976** - W. H. Freeman,
      ISBN 978-0-7167-0464-5, confirmed against ACM's book record and the
      Internet Archive catalogue. Ten years apart, and the string is identical
      in shape. `Winograd, 1970` named a PhD thesis written 1968-1970 and issued
      as **MIT AI Memo 235 with a February 1971 date**, while the principal
      published reference is the **1972** paper. Both citations now name the work,
      the venue and the ambiguity, and the ELIZA record states outright that the
      paper is **not** the source of the moral argument, which came in the 1976
      book - a distinction the old string made impossible.
    - **Neither record was upgraded to `verified`.** Both are `retrievable`,
      which means a reader can open them and find the work - Crossref's metadata
      confirmed author, title, volume, issue, pages and year for both. **Nobody
      read either paper**, and the tool says so in the record it writes.
      252 -> 254 records with a locator. All 14 gates green.

30. **A tool whose documented interface does not exist is worse than one that
    admits it has none - and PowerShell parse-errors killed two writes this
    session while reporting success.** Twice now a `look.py` or `cite.py` call
    shared a bash block with an inline `python -c` that PowerShell could not
    parse, and **PowerShell parses the entire block before executing any of it**,
    so the earlier command never ran. Both times I reported the finding as
    recorded. Neither was. The tell is available and I did not use it: **check
    the artefact, not the exit of the block you just typed.**

31. **Six card-audit warnings, and the field that should have prevented three of
    them existed, held a placeholder, and was rendered nowhere.** `via` was on
    eight records with the value `report`, which means nothing to a reader, and
    **zero templates referenced it**. So a card could say
    "Phys.org · 23 SEP 2026", link to `www.msn.com`, and a reader would click
    through to MSN having been told they were reading Phys.org. MSN syndicates
    other outlets wholesale - that is a legitimate route to a reader and not the
    same as reading the originating outlet - and the page was concealing which
    one it was. `via` was the field for exactly that and was doing nothing.
    Now it renders: **"Phys.org, via MSN"**, **"ABC News (Australia), via MSN"**.
    `card_audit.py` **learned the field** rather than being switched off - the
    aggregator check no longer fires when `via` names the host, because the page
    now states the discrepancy instead of hiding it. **A gate should learn a
    field, not be silenced, and one firing on a record whose credit reads
    "Phys.org, via MSN" is the audit crying wolf at correct data.**
    - **`publisher: "note"` was a platform in a field named for a publisher.**
      note.com is a Japanese publishing platform and the account is `lesser_p`,
      visible in the URL. Now `note (lesser_p)`, and the audit accepts that shape
      because **it is the shape the audit asked for** - an unadorned platform
      word still warns. Setting `via: note.com` there was also wrong and was
      caught in the dry run: a note.com post is published by an account ON
      note.com, there is no separate organisation being syndicated, and the
      credit would have read "note (lesser_p), via note.com" - two names for one
      thing. The case `via` exists for is a wire story republished elsewhere.
    - **`sasaeng-jungkook-conviction` was the serious one, and it was true.**
      A card asserting a criminal conviction about a named living person, with
      "twenty-two visits, one hundred and thirty-three doorbell rings", sourced
      to **one person's Substack and nothing else**. That is a fair warning: a
      conviction is a matter of public record and should not rest on a newsletter.
      Checking the numbers rather than assuming them, **every figure holds** -
      22 visits between 7 and 28 December, 133 rings on a single visit which the
      court called an "extreme level of obsession", one year suspended for two
      years, sentenced 8 May by **Judge Park Ji-won of the Seoul Western District
      Court**. Reported by BBC (bylined Kelly Ng), *The Korea Times*, *The
      Independent*, NME and GMA. So this was never a false card - it was a true
      card resting on the weakest available citation, which is the same defect as
      a `retrievable` record with no URL. The BBC and Korea Times records are now
      on it and the Substack is kept as secondary commentary.
      **The defendant is unnamed in every report and in the court documents, and
      the card does not name her.** That is worth preserving deliberately: a
      conviction is a fact about a person and the site has no reason to make her
      findable.
    - **The last warning is a judgement, and the judgement is that it is fine.**
      `parasocial-problem-visibility` is also sole-sourced to a personal Substack,
      but it names no date, no person, no proceeding and no number. It advances
      an argument about a mechanism - visibility mistaken for access - and for a
      thesis a named Substack **is** the citable author. 6 warnings -> 1, and the
      1 is a person deciding not to act.

32. **The three finished episodes are prototypes, not the deliverable, and I spent
    a session optimising the wrong thing.** The direction, given directly: **stop
    treating `eliza` / `shipping` / `vshojo` as the video problem.** They are three
    hand-made cuts standing in for a **bi-daily automated creator releasing across
    all platforms**, and they were never going to be published because they were
    never the point. `AGENTS.md` item 1 framed "publish one episode" as the
    headline open item for a long time, and I kept treating it as the blocker.

    - **The goal is a content engine, not a renderer.** Bi-daily is ~182 releases
      a year. No amount of work on three MP4s produces that, and improving the
      prototype improves nothing the engine will actually use.
    - **The editorial thesis is parasociality across ALL FORMS OF MEDIA.** That
      is the spine the engine walks. Not "AI companions and social platforms",
      which is what the corpus currently is.
    - **And the corpus does not currently cover that, which is the real finding.**
      Measured on `medium` (which is a LIST, not a string - the first version of
      this probe compared `str(medium) == "history"` against `"['history']"`,
      matched nothing, and printed 0 for every medium):

      | medium | entries | days of bi-daily cadence at 2 entries/release |
      |---|---|---|
      | comics | 1 | 0.5 |
      | radio | 2 | 1.0 |
      | music | 6 | 3.0 |
      | sport | 6 | 3.0 |
      | theology | 7 | 3.5 |
      | television_unscripted | 10 | 5.0 |
      | television_scripted | 14 | 7.0 |
      | literature | 16 | 8.0 |
      | games | 18 | 9.0 |
      | film | 19 | 9.5 |
      | ai | 20 | 10.0 |
      | technology | 29 | 14.5 |
      | history | 56 | 28.0 |

      **Comics lasts half a day and radio lasts one.** A bi-daily cadence walking
      the media axis exhausts two of its thirteen members in the first week and
      then has nothing. Only **109 of 193 entries (56%)** carry a real medium at
      all - the other 84 sit in `history` (56) or `technology` (29), which are
      catch-alls and name no medium. `history` alone is 29% of the corpus, and
      AGENTS has already recorded it being used as "the value 57 entries use as a
      catch-all".
    - **The stories lean the same way and harder.** By section: `grief` 11,
      `companion` 9, `creator` 6, `idol` 6, `brand` 5. Counting the medium each
      story's subject lives in, **34 of 47 are digital/platform** and **only one is
      film**. That is a coherent editorial identity and it is not the one the
      thesis names.
    - **There are media the axis has no name for at all**: stage and theatre,
      puppetry, advertising, the visual arts. Thirteen entries have a stage in
      their prose and **none is filed there**. A closed validated list is what
      makes a missing medium a visible hole rather than an inconvenience -
      `radio` and `comics` were added for exactly that reason, and the same
      argument applies to the ones still missing.
    - **So the content-supply problem is the corpus, not the pipeline.** Rendering
      is solved and the weights are downloaded. What a bi-daily creator walks is
      `MEDIA`, and `MEDIA` is thin at one end and absent at the other. Filling
      comics, radio, stage and the visual arts is what makes a cadence possible -
      and unlike the three MP4s it is work that the engine will actually use.

33. **The atlas had its own copy of the medium list, it had already drifted, and
    the two thinnest media in the corpus were invisible from the map for that
    reason.** `tools/atlas.py` validates every entry's `medium` against `MEDIA`.
    `tools/build_atlas.py` - which builds the page - defined **its own**
    `MEDIA_ORDER` and `MEDIA_LABEL`. The copies had diverged: atlas.py had
    **fifteen** media, build_atlas.py had **eleven**. So `radio` and `comics` -
    the two added specifically because the axis had nowhere to put them - had
    **never been filterable in the atlas at all**. They are the two thinnest media
    in the corpus, and part of why that was not obvious from the map is that the
    map did not list them.

    - **Same family as the plate that stopped describing its entry**: a generated
      artefact quietly falling behind the thing it is generated from, invisible
      from either file alone. `plate.py --check` catches this for plates; nothing
      caught it for the media list because there was no second list to compare
      against - there was only a stale one. `build_atlas.py` now **imports**
      `MEDIA` and `MEDIA_LABEL` from `atlas.py` rather than copying them, with a
      `spec_from_file_location` fallback for running from another directory.
    - **`media_colour(i, n=11)` had the count hardcoded**, so the day a twelfth
      medium was added every colour on the wheel would have silently re-spaced
      and nothing would have said so. It derives `n` from `len(MEDIA_ORDER)`
      now.
    - **`stage` and `visual_art` were added to `MEDIA`**, and that is the whole
      of what was done. **Nothing was refiled.** Moving an existing entry into a
      new bucket to make the distribution look even is the move this project
      refuses - the same rule that keeps five taxonomy sub-categories empty and
      reported rather than filled. Adding the names makes the gap *fileable*,
      which is the only way it can be closed honestly. Both now render as a
      selectable filter chip with nothing behind it, which is a hole a reader can
      see rather than one nobody knew was there.
    - **The measured state of the axis, for the record** (`medium` is a LIST; the
      first probe compared `str(medium) == "history"` against `"['history']"`,
      matched nothing, and printed 0 for every medium):

      | medium | entries | days of bi-daily cadence |
      |---|---|---|
      | comics | 1 | 0.5 |
      | radio | 2 | 1.0 |
      | music / sport | 6 each | 3.0 |
      | theology | 7 | 3.5 |
      | television_unscripted | 10 | 5.0 |
      | television_scripted | 14 | 7.0 |
      | literature | 16 | 8.0 |
      | games | 18 | 9.0 |
      | film | 19 | 9.5 |
      | ai | 20 | 10.0 |
      | technology | 29 | 14.5 |
      | history | 56 | 28.0 |

      **109 of 193 entries (56%) carry a real medium**; the rest sit in `history`
      or `technology`, which name no medium. `history` alone is 29% of the corpus.
    - **What the holes are, concretely:** `comics` has one entry and it is
      `casper`, a character rather than a strip. `radio` has two, both dated 1930
      (`radio-serials`, `the-shadow`). `stage` and `visual_art` have none, and
      there is still no medium for advertising or the visual arts beyond
      `visual_art`. Five entries have a stage in their prose and none is filed
      there.

34. **The corpus had the direction of this mechanism backwards, and the sharpest
    version of it arrived as something I was told to watch rather than something I
    found.** Measured first: `wonka`, `dahl`, `chocolat`, `cocoa`, `candy` and
    "brand extension" return **zero** entries between them, and only **13 of 193
    entries (7%) mention commerce at all**. The brand axis held five, and its
    spine was `the-brand-as-character` (1995) - *"Corporations given a voice, a
    face, a founder narrative, and a tone, so that a customer relationship has a
    subject."* That is the ordinary case and it is the weak one: the company came
    first and the personality was bolted on afterwards.

    **`the-figure-you-buy` is the inverse, and it is stronger.** The figure came
    first and the product took the figure's NAME. Roald Dahl invented a chocolatier
    in 1964. In 1971 a **breakfast-cereal company with no film experience**
    advanced about **$3 million** to finance an adaptation in exchange for the
    right to sell a chocolate bar under the character's name, and the film was
    **retitled from *Charlie and the Chocolate Factory* to put the product in the
    title**. The brand launched on 17 May 1971, a month *before* the film opened on
    30 June. Wikipedia's own phrase for it is "the greatest reverse product
    placement ever".

    - **The mechanism is an unfalsifiable far side.** Everywhere else on this site
      the other party can disappoint you: a performer cancels, dies, scandals,
      sues. This one cannot do any of it, because he was never a person - and a
      bond that cannot be disappointed cannot repay either. That is not a side
      effect of the licensing. **It is what the licensing is for**, and it is why
      the name has outlived four owners: Quaker Oats, Sunmark, Rowntree
      Mackintosh, Nestle, then Ferrero, and now a streaming platform that bought
      the Dahl catalogue outright. One invented figure, four successive owners,
      none of whom have met.
    - **And the 2026 Netflix competition is where the engineering fails in public,
      which is what makes it an entry rather than an anecdote.** It restores Gene
      Wilder's dead voice with generative audio built by ElevenLabs, approved by
      his estate *and his widow*, and co-showrunner Alison Holloway on why: *"What
      would Wonka do at this point? What would Wonka say? I.e. What would Gene
      Wilder say?"* - **fusing a fictional chocolatier and a dead actor into one
      addressable figure.** It was hated: **Metacritic 29 from 7 reviews, 0 per
      cent positive**, and the Los Angeles Times on the voice: *"a lifeless voice
      not so much from beyond the grave as buried in it."*
      **So the bar works because the mask never slips and the show fails because
      it made the mask audible.** Same mechanism, opposite outcome - and the
      corpus had no way to say that, because it had only ever seen the
      brand-as-character direction.
    - **The book rewards Charlie for refusing to be greedy. The show pays $3m to
      contestants who are explicitly incentivised to scheme** (NBC News' word) and
      calls its eliminations *termination*. **The figure is made to host the exact
      contest he was invented to punish.** Contestants also qualified by finding a
      ticket hidden inside a Wonka bar, so the purchase is the entry token.
    - **The transparency problem, in its most literal form, and stated as an
      allegation because that is what it is.** Nestle owned the brand 1988-2015 and
      is a **named defendant** in the 2021 International Rights Advocates case in
      which eight Malian plaintiffs allege they were trafficked as children to
      harvest cocoa; the companies dispute it and say there is no legal basis, and
      the record says so in full. It is in the entry for its **structure** - an
      invented name is the standing emblem for a real supply chain of real people,
      and it absorbs the charge - not as an accusation about any one firm. The
      WaPo reporting (2m+ children per a 2015 Labor Department report; industry
      deadlines missed in 2005, 2008, 2010 and 2015; a Nestle executive saying
      "I'm not going to make those claims") is the documentary spine.
    - **`verified: false`.** Nine sources, all read and all recorded as read, and
      nobody has stood behind them in the corpus's sense yet.
    - **A note on the mechanism of the correction, because it is the third time
      this shape has appeared.** The finding did not come from a gap in the corpus
      or from an axis that ran out. It came from being told what someone had
      watched. The tool that found it was **a person**, and the honest reading of
      "are you doing the full pull" is that the answer was no - and that the
      breadth question is not answerable from inside the corpus, because a corpus
      cannot report its own blind spots. It only has holes where it already knows
      something exists.

## Why this site exists

**The origin, in the author's words, corrected once already. The first version of
this section was wrong and the error is worth keeping.**

I first wrote this section inferring that the author had been harmed, from the
word "affected". It quoted the author accurately and then invented a wound around
the quotation: *"A person who builds a corpus after being harmed will produce
exactly this"*, *"the archive is right about the harm"*, *"named after a shape,
not after a wound"*. None of it was said. **An inference wearing the clothes of a
quotation is the defect this project exists to catch, and it was committed here
about the person who wrote the thing.** The correction:

> the parasocial wasn't harmful to me from my perspective - i shrugged off the
> fake god connection - then affixed to my favorite and most relatable character
> in movies and tv - saw glimmers of me in video games - really saw versions of me
> in reality tv - i find parasocial connections essential but necessary to
> identify and reflect on with purpose - i have a much more nuanced and open mind
> about the power of the parasocial than you seem to assume

So the origin is **recognition, not damage.** The god connection was shrugged off -
that detail carries the most weight, because it means the site was not built by
somebody trying to understand what had been done to them. It was built by somebody
who found versions of themselves in characters across film, television, video
games and reality television, and who holds that to be constitutive of a person
rather than something to be processed. **Essential, and necessary to identify and
reflect on with purpose.** The discipline is reflection, not defence.

What that asks of the archive is breadth of *kind*, not a corrective tilt: every
significant one-sided relation, across the ages, whatever its valence. The
measured finding below survives the correction intact, because it never depended on
the false premise.

**The prose is balanced.** Entries whose own text is about harm: 18. Entries about
warmth, consolation or a reply: 18. One to one. The journalism does not skew dark.

**The classification is not.** The register axis has eight members: Encounter,
Bond, The reciprocal edge, Archive, Contest, Harm, Cog, Undemanded. Seven
describe the **form** of a one-sided tie. One carries an **ethical verdict**, and
its own `def` says so: *"harm is a register that any of the eight can be in."*
**Valence therefore occurs
exactly once in the classification, and only for harm.** Bond is the proof: its
test is *"Is there a history?"*, which is structural - a sasaeng bond and a parish
congregation are both Bonds, and nothing in the register separates them.

The honest explanation for that is unexciting and needs no biography: **nobody had
asked whether a register axis needs a member for a tie that was good, because the
dramatic cases are the interesting ones.** That is how taxonomies go lopsided, and
the archive is not evidence about the author. It is evidence about what gets
written down.

**And the standing instruction is the one thing here that is not mine:** all
significant one-sided relations, manipulative or otherwise, throughout the ages.

## The register the axis was missing

Proposed here and **adopted 2026-10-06** - it and `cog` are the two members added
after the first six. Nothing was moved into it to make the chart look even, which
is the rule for a new member as much as for a sub-category: it was filled by
entries written to argue it instead, `dear-kitty` first.

    id    undemanded
    name  Undemanded
    def   The tie stayed one-sided, nobody was paid for it, and nothing was asked
          of the other end. The register most parasocial writing cannot see,
          because it has no incident to report.
    test  Did anybody want anything from the other end? If the answer is no, and
          the tie still mattered, this is it. The question is deliberately about
          wanting rather than about harm, because wanting is the only part of a
          parasocial tie that is never anybody''s fault.
    not   Not reciprocity - the other end could not answer, by definition, and
          that is what creates the register rather than making it an error. Not
          Harm, and emphatically not the absence of cost: plenty of undemanded
          ties carry grief, and Archive is the right home for that. Not Bond''s
          history, which every register can have.
    mechanism
          One-sidedness without a bill. The near side is not deceived, nobody is
          charged, and the only thing missing is a second person - which is the
          one thing that could never have been arranged.

The mechanism sentence is the whole argument. Everything else on this site is
organised around what a one-sided tie *costs* or *could* cost. This is the case
where the missing second person is simply the shape of the world, and the tie is
still real, and nothing is owed.

It will also be the hardest register to source, and that is not an argument
against it. It has no document: nobody files a complaint about a tie that asked for
nothing, and no archive exists for the absence of an event. **A register that
cannot be evidenced will look empty forever if it is only filled from evidence.**
That is a live tension in this project and the entry - not the member - is the way
it gets resolved.
35. **A register is a definition, not a placement, and I nearly invented a field to
    hold one.** `undemanded` and `cog` were added as empty registers and both
    reports asked the same natural next question: which entries go in them?
    **The data model cannot answer it, and that is by design rather than an
    oversight.** Checking the render path rather than the prose:
    - `data/taxonomy.json` holds `register` as a **list of definitions** -
      `id`, `name`, `def`, `test`, `not`, `mechanism`, optional `anchor` - and
      **no `members` key**, unlike `otherness` and `reciprocity`, which both
      carry one.
    - `build_cards.py` renders `otherness` **with a placement count counted from
      `taxonomy_placements.json`**, printing "nothing placed yet" for a member
      with zero. The register block, sixteen lines below it, **has no count and
      no tally** - a register you cannot test is a heading, and a heading cannot
      be assigned to.
    - `encyclopedia.json` carries no `register` field at all. The keys are
      `era, id, kind, lanes, media_inferred, medium, provenance, relations,
      sections, significance, sources, summary, title, verified, year,
      year_end`. There is nowhere to put one.
    So a tie's register is carried by **its prose** - by what the entry argues
    and which sub-category it sits in - and not by a value. `dear-kitty` is the
    first entry to make that argument outright, and it does it in the
    significance rather than in a field: "the purest instance of an undemanded
    tie on this site". **Adding a `register` field would have been the fourth
    instance of this file's own family - a field that promises more than it
    keeps** - because nothing would have counted it, so the first register with
    one entry set and a member with none would both claim to be populated.
    The next useful work here is *not* a field. It is a way for a reader to
    find the `undemanded` entries at all, which today means reading prose.

36. **`dear-kitty` (1942) is the first entry to name the phenomenon from the
    inside, and writing it produced three defects that no build would have
    caught.** Anne Frank wrote to an invented listener for two years and stated
    this site's definition while doing it: *"I like writing to you most, you
    know that don't you, and I hope the feeling is mutual."* The hoping is the
    whole condition and she named it fourteen years before Horton & Wohl had a
    phrase for it.
    - **She addressed eight correspondents, not one** - Kitty, Pop, Phien,
      Conny, Lou, Marjan, Jettje, Emmy - which is **a social network with no
      reciprocating nodes in it**, a structure no entry here had described. Five
      came from Cissy van Marxveldt's Joop ter Heul books and three she
      invented, so the far end is fabricated at two removes: first the
      character, then the correspondence. She wrote to only Kitty from
      13 November 1942. And she addressed the object too - *"as long as this
      still exists, I cannot be sad"* - so the tie survives its own removal,
      which is `archive` operating inside a `bond`.
    - **The published half is the `cog` case, and it is the machine getting it
      wrong.** The diary came out in **1947**, after every member of the family
      but Otto Frank was dead, and has sold something like 30 million copies in
      more than 65 languages: the most private one-sided conversation in the
      western canon became a mass reading relationship with a dead child. And
      **the most-quoted line in the world's most-read diary is a truncation.**
      The United States Holocaust Memorial Museum records that it "has been
      taken out of context" and that read in full - "about three paragraphs" -
      "it is part of a quote about a great deal of despair and longing." What
      actually follows the famous line is *"I simply can't build up my hopes on
      a foundation consisting of confusion, misery, and death."* **The optimism
      is the misquotation** - a private sentence replaced by its opposite by
      readers who were not there and never wrote back, which is this site's
      whole argument arriving from the one place it could not be constructed.
    - **Defect 1: two false relations, and it is the inverted-verb family again.**
      I wrote `mourn-a-person-you-met` (1990) and `dickens` (1812) as
      `contemporary` with a 1942 entry. `contemporary` renders as "of the same
      time as", so both edges asserted a chronology wrong by 48 and 130 years,
      written from how the sentence read rather than from the dates - the
      seventh-wrong-edge shape this file records three times already, repeated
      by the same person. **`dear-kitty` at 1942 is the only entry in its
      year**, measured, so there is no honest `contemporary` to have and the
      correct result was *fewer* relations. The relation vocabulary is
      chronological, bibliographic or structural - there is no "thematic
      kinship" type - so a real tie to `mourn-a-person-you-met` is not
      expressible, and the answer is to leave it out.
    - **Defect 2: `kind: case`.** Legal, but the three existing `case` entries
      are all matters before a court - `stalker-law`, `characterai-lawsuits`,
      `the-litigation-year`. A published diary is not a case; its peers by shape
      are `gigi` (1943) and `casper` (1945). Changed to `work`.
    - **Defect 3: `sections` carried `brand`,** which is a licence
      relationship and has nothing to do with a hiding child in Amsterdam.
      Replaced with `grief`, which is where the register's own `not` sends
      undemanded ties that carry loss.
    - Four sources, all read: Anne Frank House, USHMM, Wikipedia, Britannica.
      **The Kitty-Egyedi reading was checked and refused** - the speculation
      began in the 1970s and Kitty Egyedi herself said that once Kitty "started
      to lead her own life in the diary that it ceases to matter who is meant
      by Kitty. The name is not meant to be me." `verified: false`.

37. **My own defensive `sorted()` made a two-entry change unreadable, and the
    diff stat was the only thing that noticed.** `correct_dear_kitty.py` ended
    with `dict(sorted(assignments.items()))` as tidying. Two things were wrong
    with that and neither would have raised an error:
    - **The file's convention is "sorted, then appended in the order added."**
      `fight-club`, `deadpool`, `rudolph-valentino`, `mickey-mouse`,
      `lugosi-burial`, `king-kong` is the order I added them in, not the
      alphabet's. Sorting destroyed a record of the corpus's growth.
    - **`data/taxonomy_placements.json` is `indent=2` and every other corpus
      file is `indent=1`.** Rewriting it at `indent=1` reformatted all 2000
      lines. The diff stat read **"2001 ++++----"** for an eleven-line change.
    Both are this file's own lesson applied to me: **a hand-maintained corpus
    file must be merged into, in its own format** - "Merge into the committed
    file; never regenerate it from a template." A script that reads a corpus
    file, changes two keys and writes it back has regenerated it from a
    template unless it checked the indentation and the key order first. Both
    are now read from the committed bytes rather than assumed, and the tool
    refuses to write if the key set or the top-level keys moved.
    **And the general form: a tidy-up that makes a diff unreadable is not a
    tidy-up.** The instinct to leave a file sorted is the same instinct as
    filling an empty register to make a chart look even - it optimises the
    file rather than the reader, and the reader is who has to review it.

38. **`nancy-drew` found a fourth state on the otherness axis, and the honest
    response was to leave the field empty.** The entry (1930-1984) is the
    second argument for the `undemanded` register and the first `simulated`
    reciprocity instance that is not a live stream.
    - **The evidence is an archive, and it is fifty-four years of it.** The NYPL
      Stratemeyer Syndicate records (MssCol 2903) hold the fan mail as a
      described subseries - **boxes 56-57**, "letters received from young
      readers of Syndicate books dating from 1930-1984", plus "a few letters
      written by parents on behalf of their children, and from adults who read
      Syndicate volumes during their childhood". **This is the only kind of
      evidence an undemanded tie ever produces** - nobody files a complaint
      about a tie that asked for nothing, so an archive of one is just a
      correspondence department that kept its mail.
    - **The same collection holds "audio letters" and "commercial recordings of
      dramatic readings of Syndicate books, including stories from The Bobbsey
      Twins, Nancy Drew and Tom Swift."** A child could send a voice and
      receive a voice with no answering machine in existence. **The limit is
      recorded on the entry: the finding aid does not say who those letters were
      addressed to, so the entry does not claim they were answers to children.**
      It claims what the document says, which is that the company held audio
      letters and readings of Nancy Drew.
    - **For the first forty-four years of that correspondence, the readers were
      writing to somebody with no author.** The first book appeared April 1930;
      Edward Stratemeyer died **twelve days** later; Mildred Wirt Benson wrote
      **23 of the first 30 books** under the Syndicate-chosen house pseudonym
      **Carolyn Keene**, which was a slot in a production system rather than a
      person, at a flat fee of $85-250 per novel. **Her identity was not made
      public until 1991**, established by University of Iowa staff and faculty.
      So every reply to a child's letter in that span came from an office that
      had chosen not to have a face. The only quality note on record from that
      same correspondence is a marketing one - Stratemeyer thought Nancy Drew
      was **"much too flip"** and sent the manuscripts anyway.
    - **The near side's own account was collected, which almost never happens.**
      The Carolyn Dyer papers hold the **1993 Nancy Drew Conference** at Iowa,
      including "testimonials from readers all over the country on what Nancy
      Drew meant to them", and *Rediscovering Nancy Drew* (Iowa, 1995) grew out
      of it with a chapter titled "Reading the Stories of Reading: Nancy Drew
      Testimonials". **This site is an argument assembled from reader testimony,
      and here a hundred strangers wrote theirs down before anyone asked.**
    - **The register claim has to live with the motive, and does.** Nothing was
      asked of the far end and nothing was paid *by the reader*, which is the
      test exactly - but the tie was **industrial**, with an owner, a
      correspondence department, a house pseudonym and a schedule. So it is not
      the private case the register imagines; it is somebody noticing children
      were writing and building the reply channel, which is the same decisive
      move as a cereal company's decoder ring and much less cynical. What earns
      it the register is not that nobody profited - the Syndicate profited - but
      that the tie as the reader lived it asked for nothing and was answered
      anyway.
    - **`simulated` is load-bearing here, and it is a different shape from the
      other two.** `live-commentary` and `twitch-subs` work by **latency** - a
      host reads a comment aloud within seconds. A correspondence department
      works by **post**: the distance between a child's letter and its reply is
      a postal system, and the answer was typed on Syndicate stationery under a
      name that was a slot rather than a woman.
    - **And the placement failed to fit, which is the finding.** Filed
      `character/fictional-protagonist` - whose definition is nearly a
      transcription of the case, "somebody described in a book and therefore
      available to an unlimited number of people at once" - and **left
      unplaced on otherness.** `imagined` needs the audience to *know* they made
      it; the readers did not, with thirty-odd published books behind the
      character. `made` needs the operator to be *shown*, and its own `not`
      redirects the hidden case to `played-role`, which is a different thing
      again. **So the axis has no member for a figure written by an operator
      the audience is never shown** - `the-shadow` and `howdy-doody` are `made`
      with the transparency intact, because a voice actor, an advertising agency
      and a writer-director are all discoverable. This is the same machinery
      with the byline bolted shut.
      **Recorded, not filled.** Adding a ninth otherness member is an editorial
      decision and it is **the author's**, not a script's. The gap is real, it
      is on a validated axis, and it is now written down where `verify_taxonomy`
      can be pointed at it.

39. **`stage` had zero entries for its whole life, and the fix was a play
    about a man who cannot get a reply from a recording of himself.**
    - **`krapp-last-tape` (1958, `medium: stage`, `kind: work`).** Premiere
      **28 October 1958, Royal Court Theatre, London**. Krapp records a tape
      reviewing the year gone on every birthday of his life; at 69 he plays the
      one he made at 39 and talks to it. The Guardian: although performed by a
      single actor, "it is not quite a monologue. It becomes a kind of dialogue
      between the 69-year-old Krapp and his recorded 39-year-old self."
      **Everywhere else on this site the far end is somebody else; here it is a
      recording of the near side, and it cannot answer either.** The only
      technology that could have produced a reply from the past produces the
      past instead, and an audience watches a man fail to get a response from a
      voice that is his own.
    - **The detail that earns the entry: the tape is damaged, in every
      edition.** An *Opera Quarterly* article records a mechanical error
      "present not only in all the Faber & Faber editions, but also in the
      so-called avant-texte", appearing in a typescript from shortly before
      publication in 1958 - **four words are missing from the tape**, which the
      article calls "a sonic or performative punctum pricking the one who
      realizes it". **So the past self is not silent, it is truncated**, and no
      reprint fixes it. Quoting Steven Connor from the same source: "for Krapp
      to listen to the tape of himself as a man of thirty-nine is to reveal
      clearly his ironic non-coincidence with himself."
    - **The tape's own contents are a record of being refused.** The reel his
      ledger marks "**Farewell to love**" recalls a tryst on a river, and the
      Guardian's 2024 review calls it "a jolt to hear the line, spoken calmly:
      'I said again I thought it was hopeless and no good going on and she
      agreed, without opening her eyes.'" The other party is on the recording
      too and is *described* rather than heard; the only audible voice is a man
      reproducing the moment he asked for something and was refused. He is
      scathing about his 39-year-old self, and the review has him cradling the
      recorder "in a gesture of engulfing loneliness". Then he loads a fresh
      reel and records the year - **the ritual continues, which is what makes
      it a bond rather than an episode.**
    - **Beckett wrote it because he heard somebody hear himself**: for the Irish
      actor **Patrick Magee**, after hearing him read Beckett's own *From an
      Abandoned Work* (1954-55) and extracts from *Molloy* (1955) **on the
      radio**. And the structure keeps being manufactured the way the play
      describes it - Arts Over Borders asked Samuel West and Richard Dormer to
      each record the taped Krapp **at 39**, so the two-age split is produced by
      casting two people rather than by time.
    - **And there is no recording of the 1958 premiere** with Magee under
      Donald McWhinnie. The first audience's encounter with this tie left no
      trace, while a play whose entire subject is a destructible recording
      outlived every document about its own first night. **An `archive` register
      entry inside a `bond` entry** - the same double reading as `dear-kitty`'s
      "as long as this still exists, I cannot be sad".
    - Filed `companion/anthropomorphised-tool` beside `the-shadow` and
      `howdy-doody`, because that shelf's test is "persistence after the
      purpose has gone" and the ledger names the reels. Reciprocity unset -
      `directed` is the corpus default.
    - **Dated from the premiere rather than a composition date**, because the
      play's first object is a Royal Court stage. Relations: `contemporary` ->
      `vertigo` (1958, same year, and a man who cannot reach another person)
      and `depicts` -> `parasocial-interaction`. `character/played-role` was
      rejected: that is about the actor, and the object of the tie here is the
      recording.

40. **The otherness axis now has two entries it cannot file, failing in
    opposite directions, and both are a recording. That is a pattern, and the
    candidate member is obvious.** Recording it here rather than adding a ninth
    member, because the axis is a validated editorial instrument and adding to
    it is the author's call.
    - `nancy-drew` - a figure **written by an operator the audience is never
      shown**. `imagined` needs them to *know* they made it; `made` needs them
      to *see* the operator. Benson wrote 23 of the first 30 books under a house
      pseudonym and was not identified until 1991.
    - `krapp-last-tape` - a **recording of a real person as the far end of a
      one-sided tie**. `made`'s own `mechanism` refuses it outright: "**The
      figure answers, and that is the whole appeal**, so every answer is a
      small breach: the voice is pre-recorded, the mouth is somebody else's
      hand." Krapp's far end never answers - that is the play. `mirrored` half
      fits and then fails, because its mechanism calls the copy "assembled out
      of memory and **never checked against the original**" and the whole play
      is that **the original is sitting in the chair listening**. The tape is
      not an idealised self; it is a verbatim one, and its accuracy is the
      problem.
    - **One is a machine that cannot speak; the other is a machine that speaks
      only in the past. The case the axis has no word for is the far end being a
      recording** - and Krapp's fourth missing word sharpens it, because that
      recording is damaged in every edition, so it is not even a faithful copy
      of the past. The Faber error is a bonus for the argument: a parasocial
      artefact that fails at *fidelity*, which is the one thing it was supposed
      to fix.

41. **I checked whether the medium renders on an entry page, decided it did
    not, and was wrong - because I searched for the label I assumed rather than
    the one the code emits.** After adding the first `stage` entry I grepped
    `dist/encyclopedia/krapp-last-tape.html` for "Stage" (the `MEDIA_LABEL` the
    atlas uses), got **0**, and concluded the medium was invisible on entry
    pages - which would have been a real gap worth fixing, since the media axis
    is the spine of the bi-daily plan. The byline actually reads:

        <div class="byline" ...><span class="chip chip-m">stage</span></div>

    built by `med_html` at `build_cards.py:2952` as
    `f'<span class="chip chip-m">{esc(m.replace("_", " "))}</span>'`. So it was
    rendered the whole time, lowercase, and my probe measured the capitalised
    atlas spelling instead of the chip's. **Reading the renderer before editing
    it is what stopped this becoming a change to fix a defect that was not
    there** - the same instinct as the eyelid arc, arriving from the opposite
    direction.
    - **One real inconsistency does survive, and it is the item 33 family.**
      Three label paths now exist for one closed list: `MEDIA_LABEL` in
      `atlas.py` ("Stage"), this chip's `m.replace("_", " ")` ("stage",
      "television scripted"), and `MEDIUM_ORDER`. Item 33 fixed a duplicated
      list that had *drifted*; this is a duplicated list that agrees on the
      values and disagrees on the casing. Cosmetic, and recorded rather than
      fixed, because a label is a promise about what the word means and the
      cheapest way to break it is to restyle it for tidiness.

42. **Every medium in `MEDIA` now has at least one entry, and the axis was the
    actual blocker for a bi-daily creator.** Items 32 and 33 measured the
    problem - comics 1, radio 2, `stage` 0, `visual_art` 0, and 84 of 193
    entries in a catch-all - and item 33 added the two missing names without
    refiling anything, because "moving an existing entry into a new bucket to
    make the distribution look even is the move this project refuses". The
    consequence of that refusal is that a name with nothing behind it sits on
    the page as a filter chip leading to an empty set, and it stayed empty
    until an entry was **written** for it.
    - **`krapp-last-tape`** (1958, `stage`) - item 39. A man on his 69th
      birthday plays a recording he made at 39 and has the conversation the
      tape cannot have back.
    - **`american-gothic`** (1930, `visual_art`) - and this is the richest
      parasocial structure in the corpus after `dear-kitty`, because **the two
      people in the painting did not choose it and then had to live in it.**
      - **The dentist denied it for five years.** Dr Byron McKeeby "didn't want
        to be famous. He shied away" from Wood's first offer. He posed in
        overalls holding **a theatre prop pitchfork**, painted in a dental
        office. Friends recognised him and joked about the pitchfork's role in
        his dental procedures; "McKeeby stood firm in his denials... The real
        McKeeby was nothing like the dour farmer who challenged the painting's
        viewers." **It was literally national news when he broke his silence in
        1935**, prodded by an AP bureau chief. So a real person refused a
        one-sided relationship with a painted version of himself for five
        years, and the refusal was the story.
      - **Wood designed the likeness to fail.** He "exaggerate[d] McKeeby's
        features so no one would recognize him" and stretched his sister's face
        "so that no one would be able to recognize her". **Opacity was the
        design choice - the exact inverse of `made`, where transparency is the
        design choice - and it failed absolutely.**
      - **And the sister credited the painting with her own interior**: "**Grant
        made a personality out of me. I would have had a very drab life without
        [American Gothic].**" A woman saying a painting supplied a self she
        would not otherwise have had.
      - **And the brother ended it because it worked.** After critics said she
        "looked like the missing link, that her face would turn milk sour" and
        the apologetic *Portrait of Nan* (1931), Wood reportedly told her "It's
        the last portrait I intend to paint, and it's the last time you will ever
        pose for me." She had posed for years and asked why. **"Your face is too
        well known."** That is the entry's title, and it is the moment the
        figure leaves the model - reported by a brother, as a fact about his own
        work.
      - **The cog is the afterlives**: parodied in "advertisements, in
        television shows such as *The Simpsons*, in albums, in comic books, on
        magazine covers, and by Jim Henson's Muppets" and "in the political
        arena". Christie's weighs the multiplicity against exactly one other
        thing, **Edvard Munch's *The Scream***. Millions of remakes, none by
        anyone who met Wood, Nan or McKeeby. The 1977 *Hustler* topless version
        is the sharp end - Nan "was afraid that people would think that she
        authorized it."
      - **The authenticity was manufactured and shipped.** Wood called the pair
        "tintypes from my old family album" and then ordered the apron and
        overalls **from a Chicago mail-order house**; the Eldon house's
        churchlike window "wasn't the product of a distinctive local culture,
        either... It, too, was mail-ordered from Sears." **`the-figure-you-buy`
        arriving in paint and arriving first** - a fictional figure is
        unnecessary when the rural American can be assembled from a catalogue
        and a dentist.
      - **And an impresario invented the movement to sell it.** $300 and a
        bronze medal, then the picture "championed as the masterpiece of a new
        American art movement called 'Regionalism', **first invented, and then
        promoted, by an impresario and art dealer from Kansas named Maynard
        Walker**". Wood "happily played along with the role of a stay-at-home
        Iowan rustic prescribed for him by the propaganda of the Regionalist
        movement. He even posed for photographs in his studio wearing overalls
        identical to those of his reluctantly disguised dentist." **The painter
        became a parasocial figure himself, in his model's costume.**
      - **Two honesty notes.** Wood "consistently rejected" the satire reading
        and meant sympathy - *Revolt Against the City* (1935) argues cities were
        "far less typically American". And **it drew real hostility**: a "storm
        of protest from Iowa farm wives", one threatening to "smash my head".
        Wood painted an assurance and they took it as a mockery. That is why
        this is not filed `undemanded` on its own: **undemanded is about nobody
        wanting anything, not about nobody objecting.**
    - **`american-gothic` is also the control that proves item 40.** It carries
      `other: made` - correctly, because Wood is continuously and publicly
      operating the thing, which is exactly what that member's test asks - while
      `krapp-last-tape` cannot, because its operator is a damaged recording the
      audience is never shown. **Same category, opposite conditions, and the
      axis has a word for one of them.** That makes the case for a ninth member
      demonstrable from two adjacent entries rather than asserted, which is a
      much better position to hand the author than a list of complaints.
    - The measured result, and it is the number that matters for the creator:
      **`stage`, `visual_art`, `comics` and `radio` all have entries, and no
      medium is empty.** The thinnest are still half a day each, so a bi-daily
      cadence does not run long on any single medium - it runs out of the
      *good* ones. 85 of 198 still sit in `history` or `technology`, which name
      no medium at all, and that is now the biggest single hole left on the
      axis. `tools/report_current_state.py` prints the block and the table, so
      the numbers in `AGENTS.md` can be measured instead of refreshed by eye.

43. **The Current state block is now generated rather than typed, because I got
    it wrong twice in one sitting.** Item 41's lesson generalises. I refreshed
    the block by hand, typed `289 generated pages`, and it was **288** - caught
    only because I measured it afterwards, which is luck rather than a
    process. Then I typed `482 relations` and `289 pages` again for the next
    entry and had to measure both. **A number inside a paragraph is not
    obviously a claim, which is what makes it the dangerous kind**, and the
    cure is not discipline, it is removing the human from the loop:
    `tools/report_current_state.py` computes the header line, the source
    reconciliation and the medium table, and prints the exact strings the block
    should contain. The block is still typed - it has to be, it is prose - but
    it now has a tool that says what the truth is, and the claim in it is
    checkable in one command instead of in one careful reading.

44. **`marvel-club` (1940) is `comics`' first real entry, the fourth `simulated`
    reciprocity instance, and the first named `cog` in the corpus.** Both
    registers added in the last stretch had a definition, a test and a `not`,
    and **nothing behind them** - which is the state `undemanded` was in before
    `dear-kitty` and `cog` was still in now. A register with nothing behind it
    prints on the taxonomy page as though it were a finding.
    - **`comics` had exactly one entry and it was `casper`** - a 1945 character,
      not a strip. `Whiz Comics` #2, cover-dated February 1940, is the first
      comic in the medium: C. C. Beck's cover, Bill Parker's script, Wilford H.
      Fawcett as executive editor, Captain Marvel's first appearance.
    - **The child did the work, and that is the entry.** The issue carried an
      offer: send in a code and receive a membership certificate, a membership
      card with your own code number, and a plastic Captain Marvel ring. **The
      code was printed in the comic the reader was holding.** So the near side
      performed the decoding, and the impression of a private channel was
      manufactured out of materials the far side printed. **The parasocial bond
      was assembled by the person who was attached** - the part nobody writes
      about, and the reason it is an entry rather than a footnote to the Golden
      Age.
    - **The membership card was authorised by a character**, which is `simulated`
      reciprocity in its purest form: "Is a charter member in good standing of
      The Merry Marvel Marching Society And is thereby **entitled to the adulation
      and admiration of all lesser mortals!**" - issued under **"the actual
      authority of Benj J. Grimm, Grand Marshal (pro tem)"**. The institution
      signed as the Thing, so a reply from a publisher would appear to come from
      inside the fiction. The card also declared "these privileges are
      non-transferable", which is a reminder that what was sold was a status
      rather than an access.
    - **The adjacent clubs prove the signature was a choice.** Dell's club
      certificate was authorised by **G. T. Delacorte Jr.**, an actual person;
      Little Orphan Annie ran a code badge one boy "waited anxiously for",
      requiring only a subscription; E. C. "began to build a mailing list of
      fans willing to pay to belong to its fan club". **Four publishers, four
      devices, and the one that put a character in the signature is the one whose
      reply reads as coming from inside the story.**
    - **The register's own test is satisfied by the cheapest possible evidence.**
      `cog` asks whether seeing the whole machine would change the attachment,
      and "a cog that can see the machine is still a cog." A reader who knows
      exactly how the private channel works is not thereby a different kind of
      reader. The far end has its own machinery (a premium scheme - "a color
      picture of Spy Smasher for a quarter"), every member has theirs (the
      decoding), and no child in any of the four clubs built any of them.
    - **The commercial ending runs the other way from the usual story.** The fan
      clubs "evolved, eventually culminating in a full-fledged kit for Wild Agents
      of Marvel **before being discarded as a potential profit center**". So the
      apparatus was retired because it did not pay: **the bond outlived the
      business plan**, not the reverse. And it was promoted by an actual feature
      film - Frank Tashlin's *Good Humor Man* (1950) - plus a Fawcett special
      issue, so membership in a fictional boy's club was sold through a feature
      film, on a screen, to children who had never met the people writing to
      them.
    - **And the hard fact no club's own literature would tell you:** DC sued
      Fawcett in 1941 alleging the character violated its intellectual property;
      the case **took twelve years**, Fawcett paid **$400,000**, and ceased
      publication of all Captain Marvel material, ending the thirteen-year run.
      The far end of this tie was not silent or withdrawn - it was **legally
      removed**, and the members had no say.
    - **`other: made` fits here and `made` correctly refuses `nancy-drew`, which
      is what makes item 40's gap a gap rather than a misfiling.** Beck, Parker
      and Fawcett are all credited on the book - that is the transparency `made`
      asks for. Benson's pseudonym was not, and `made`'s `not` sends the hidden
      case to `played-role`, which is a different thing. **Same category, one
      with the byline and one without** - so the distinction is "the axis has one
      state it does not have" and not "the axis is wrong", and only the first is
      worth adding a member for.
    - **The sourcing weakness is on the entry, not buried.** The publication
      facts are solid and double-sourced. **The artefacts - certificate wording,
      Grimm signature, plastic ring, the decoding - rest on two weaker records**,
      a Comic-Con programme newsletter and a fan site that has recreated the code
      card. A club that awarded a plastic ring is exactly the sort of thing
      remembered differently by different people, so the wording is quoted
      verbatim wherever a quote exists and paraphrased nowhere, and the entry
      names which claims are load-bearing on the weak pair.

45. **Both registers added in this stretch are now documented here, and neither
    is a data field.** The open item from the previous session - that `cog` had
    no `AGENTS.md` note and its provenance was recorded only in `taxonomy.json` -
    is closed by this item. The substance worth keeping is item 35's: a register
    has no `members` key, `build_cards.py` renders register blocks with no
    placement count, and `encyclopedia.json` has no `register` field. **A tie's
    register is carried by its prose**, so the honest options are an entry that
    argues the case or a new field that nothing counts.
    - **`undemanded`** - "the purest instance" is `dear-kitty`; `nancy-drew` is
      the harder one, because its tie was *industrial* (an owner, a
      correspondence department, a house pseudonym) and the register's test is
      about nobody wanting anything, not about nobody profiting.
    - **`cog`** - `marvel-club` is the named instance and the mechanism is
      named. `american-gothic` is the second and the purest on scale: an image
      with a multiplicity of afterlives "rivalled" only by Munch's *The Scream*,
      remade by millions, none of them by anyone who met Wood, Nan or McKeeby.
      `dear-kitty` is the third and the saddest - the most private one-sided
      conversation in the western canon became a mass reading relationship with a
      dead child, and then the most-quoted line in it was flattened by readers
      into its own opposite.
    - **What is still missing, and is the author's call:** there is no way for a
      *reader* to find the entries on a register. The taxonomy page prints the
      definition; the prose carries the argument; nothing links them. A ninth
      otherness member (item 40) and a register-membership field (item 35) are
      both real options and both are editorial decisions rather than defects, and
      **neither should be made by a tool that merely noticed them.**


46. **`queen-for-a-day` (1945) breaks `radio`'s two-1930 pin, and the applause
    meter is the `cog` register in hardware.** `radio` held two entries and
    **both were 1930** - `radio-serials` and `the-shadow` - so the medium was
    not merely thin but historically narrow, pinned to the year its two entries
    happened to land in.
    - **I arrived with a wrong memory and the sources corrected it.** I expected
      a letter-writing show, listeners writing in with their misfortunes. The
      format that broadcast was different and better: contestants interviewed
      in the studio one at a time, each telling her troubles aloud, and the
      audience choosing **by applauding** - "She who received the greatest
      amount of applause **as registered by the 'applause meter'** was Queen for
      a Day." **A machine returned the verdict on somebody's life.** Every
      other `cog` case argues the point structurally; this one has a box on a
      wall with a needle in it. And the register's test is satisfied for free -
      **the schedule is the receipt**, since the network extended the show from
      30 to 45 minutes "so they could sell more commercial time at the then
      astounding rate of $4000 per minute". The sorrow slot was sold by the
      minute.
    - **The instrument was pointed at the wrong room**, which is sharper than
      "the audience picked the winner". In radio the home listener could not
      applaud into the device at all: the crowd the meter registered was the
      **studio** audience, while the millions listening at home could not
      participate. **The applause meter was not a proxy for the audience's
      feeling; it measured a different and much smaller audience than the one
      listening.** The far end was not merely unseen - its measuring instrument
      was aimed elsewhere.
    - **The prize was a fictional figure assembled out of a real woman's
      hardship**: "It starred their friends and neighbors, and **turned them
      into fabulous Cinderellas**" - one contestant asked for "an operation for
      her sick cat". So the object of the public's attachment is a Queen built
      weekly out of a neighbour's misfortune, and the grief is then explained as
      a commercial.
    - **And the throne is where the performance was compulsory.** Documented as
      mood dissonance: after being crowned, the contestant "was expected to sit
      on a throne and listen to a five minute in-show commercial about all the
      consumer items that she'd just won, **while pretending to be really
      excited and thankful about the benefits of things like aluminum cookware
      and dog treats**." A woman who has just asked in public for surgery for
      her child is required to perform gratitude to a sponsor, on air, for five
      minutes. **That is `simulated` reciprocity aimed at the person being
      pitied rather than at the audience** - and the corpus has no axis for a
      bond that runs from the pitied party to the audience for it. Recorded
      rather than modelled; the fourth axis was recovered from the author's own
      2019 character chart and a fifth direction is not a thing a tool should
      invent.
    - **Sourcing weakness is on the entry, not buried.** The applause-meter
      wording - the title and the central claim - is from Simple English
      Wikipedia. The throne behaviour is from TV Tropes, the weakest record
      here. The **$4000-per-minute figure is from a fan site and is not
      corroborated by anything else read**, so it is flagged as the first claim
      to check; the 30-to-45-minute extension itself *is* independently
      supported.
    - Filed `persona/presenter` because that shelf's own definition names the
      case: "The one who addresses you directly, by name, in second person.
      Newsreaders, weathermen, **game show hosts**." The show opens by asking
      the whole audience a question at once, answered in chorus - the most
      efficient parasocial address in the corpus, and it does it with one word:
      YOU.
47. **The header was broken from 761px to 1280px, and under it a mobile menu that
    had never been full-screen on any phone.** Four distinct defects, none of them
    visible to `verify_narrow.py`, and three of them invisible to my own first
    measurement harness.
    - **The desktop nav could not fit, and the reason was structural.** Measured:
      the nav needed **1031px** with no wrapping, in a bar capped at `--w:1240px`
      that also has to hold a ~200px wordmark, a 22px gap and 48px of padding -
      about **1304px**. So it was impossible for the nav to fit one line inside
      the content width it shared. It fitted at ≥1280px viewport and wrapped below
      that, and `.topbar-in` had `height:64px`, so at **1180px and 1100px the
      nav was 72px tall in a 64px box** - not clipped and not scrollable, but
      **overlapping the page**. And `.menu-btn` only appeared at ≤760px. **Every
      viewport between 761 and 1280 had a broken header, which is most laptops.**
      Fixed by measuring first: two group labels instead of three ("Elsewhere"
      cost 80px for two letters of meaning, and folded into the second group),
      "All stories"/"The history"/"The atlas" shortened, and the menu breakpoint
      raised 760 → **1024px**. Nav now needs **835px** and fits one line to 1024px.
      `.topbar-in` is `min-height:64px` now, so a future item that makes it wrap
      grows the bar instead of overlapping the page.
    - **`backdrop-filter` makes an element a containing block for its
      `position:fixed` descendants**, exactly as `transform`, `filter`,
      `contain` and `will-change` do - and `.topbar` carries
      `backdrop-filter:blur(14px)`. So the menu overlay's `inset:0` resolved
      against the **65px header** rather than the viewport, and its height became
      `max(65px, 90px padding-top + 40px padding-bottom)` = **130px**: a strip at
      the top of the page, on every phone. Measured as computed height **130px at
      viewport heights 900, 700, 480 and 844 alike** - a fixed element that is the
      same height at every viewport is a fixed element whose containing block is
      a short ancestor. Fixed by dropping the blur below the breakpoint and going
      opaque; the overlay now measures exactly 900/700/480/844 respectively.
    - **A `z-index` on a nested element cannot lift it out of an ancestor's
      stacking context, and `.grain` is a sibling.** `.grain` is
      `position:fixed; z-index:50; mix-blend-mode:overlay; opacity:.4`; `.topbar`
      is `position:sticky; z-index:40`. The nav's `z-index:65` is scoped *inside*
      the header's context, so the whole header subtree paints at 40 and the grain
      at 50 blends the page over the open menu - "Parasocialize", "1956" and a
      masthead line were all legible through a menu with a 99%-opaque background.
      Fixed by hiding the grain while the menu is open, where a full-screen
      overlay-blend texture over the whole viewport does nothing but cut contrast.
      **The tell was that `elementFromPoint` returned an element inside the nav at
      every sampled point while the screenshot disagreed** - and both can only be
      true at once if the nav is painting on top *and something else is painting
      over it*. Confirmed by breaking the input on purpose: painting the nav solid
      red removed every trace of the bleed (`tools/probe_bleed.py`).
    - **Two more, in the overlay only, both found by screenshotting it.**
      `flex-wrap:wrap` is set on the desktop row and the overlay never reset it,
      so in the *column* overlay the items flowed into a **second column** and the
      last one, Support, ran off the right edge (measured left 708px, right
      1048px in a 1000px viewport). And `justify-content:center` on a flex column
      taller than its box puts the first items in **unreachable space above the
      scroll origin** - the twelve links are ~680px, so on any window under that
      the top of the menu could not be scrolled to. Now `flex-wrap:nowrap` and
      `justify-content:flex-start` followed by `justify-content:safe center`,
      with an `@supports not` fallback.
    - **`verify_narrow.py` could never have caught any of this**, because it
      measures only at 390px, where the nav *is* the overlay - and the overlay is
      **closed by default**, so it measured a hidden, off-screen element.
      **A closed menu proves nothing about whether it opens correctly**, and this
      project had a green 390px gate over a 130px broken one.
      `tools/probe_nav.py` is the replacement: a width ladder from 768 to 1600 on
      two pages, which distinguishes the desktop *row* from the *overlay* and
      checks only what applies in each, plus an **open**-overlay measurement.
      `--check` is the gate. It is deliberately NOT wired into `link_audit.py`, for
      the reason `verify_narrow.py` is not: it needs a build and Chrome, and a gate
      that runs on every commit is a gate that eventually gets disabled.
      `tools/shoot_nav.py` writes screenshots of seven cases including two
      `body.nav-open` ones.

48. **My screenshot tool was wrong three separate times, and I believed it over
    the measurements each time. The instrument has to be trusted before the
    picture is.** This is the sharp edge of this file's own "look at the drawing;
    do not reason about the geometry" rule.
    - **`--window-size=390` does not give a 390px viewport on Windows.** Chrome
      clamps it to roughly 500px and then crops the capture, so the menu's
      `width:min(340px,84vw)` computed 340 centred in 500 (left edge 80px) and the
      crop sliced it. **SUPPORT appeared to run off the right edge in two
      consecutive screenshots while `probe_zorder.py` measured zero overflowing
      links at a true 390px.** AGENTS already records this clamp and this is
      exactly the trap; the shooter now measures inside an **iframe**, which is
      immune, and that is how `verify_narrow.py` avoids it too.
    - **A `fetch` + `document.write` shim fires mid-rewrite**, so `--screenshot`
      captured the overlay before its background painted and fabricated a
      bleed-through defect. Rewriting the `<body>` tag in a copy of the page is a
      string edit that happens before first paint.
    - **A harness that fails open reports a clean layout it never observed.** The
      second version of `probe_nav.py` returned every field as `None` and still
      printed **"fits" at all ten widths**, because the verdict read
      `o.get("lines", 1)` and a missing key defaulted to one line, zero overflow
      and zero document width. Identical to the `<` that fails open in the
      relation-derivation script, and to `verify_narrow`'s unstyled-page pass. It
      now asserts that every required key is present and **refuses to report if
      any width produced no measurement**.
    - Two more, both of which reported confidently about the wrong thing: calling
      `getBoundingClientRect()` on an already-computed rect gave 24 identical
      failures that never named the line; and the page's own `error` key was not
      mapped, so a page-side exception printed as "INCOMPLETE" instead of naming
      the fault, twenty-four times over.
    - **And one metric that was right about the wrong layer:** counting distinct
      `top` offsets reported **three lines on a one-line nav at every width**,
      because the group labels are a smaller font and centre-aligned and so sit at
      a different offset *on the same line*. That is the "distinct vertical
      offsets are rows, not columns" item already in this file, arriving as rows
      instead of columns. Now clusters tops with a tolerance of a third of the
      tallest item.
    - **The general form: three of my four "the page is broken" conclusions were
      artefacts, and the one that was real was found by looking.** Painting the nav
      red is what separated them - not more measurement, and not more reasoning
      about the geometry.

49. **The locator backlog is not closable by tooling, and measuring that was
    worth more than closing two of them.** The debt is **130 records with no
    locator across 96 entries** (of 425 records, 292 located). Its shape:
    - **0 of them carry a DOI**, confirming item 21's finding that the
      citation itself must be completed before a locator becomes findable.
    - **43 name no 4-digit year**, **14 are under 25 characters** ("Rain & Mar
      (2021).", "de Vries & Gilovich, 2015"), and 30 of the 130 are already
      `needs-source` rather than `unverified` - so a third of the backlog was
      never a citation to begin with.
    - **The twin mechanisms are exhausted.** Normalised-equality finds **0**
      records closable by same-entry copy and **0** by cross-entry copy. Only
      3 prefix candidates remained, and reading each against the full sibling
      gave three different answers.
    `tools/report_missing_locators.py` prints the whole shape, so the next
    person starts from the measurement rather than from the number.

50. **Two of the three twin candidates were attached; the third was a false
    attribution waiting to happen, exactly as AGENTS item 28 predicted.**
    - `siri`: "Yu, Nguyen, Prakkamakul & Salehi, 'I Almost Fell in Love with a
      Machine'." names **one** work, and `crossover` carries that URL on a record
      with the same authors and title, already `retrievable`. Attached.
    - `the-algorithm-decides`: the bare title record **already had** its
      locator; the record without one was `'...K-pop Fans, citing Aw & Chua
      (2021).'` - a compound. So the split applied there instead.
    - `loyalty-dark-pattern`: **refused.** The string names three works -
      Mathur 2019, Gray et al. 2018, Brignull's Roach Motel - and the finder
      would have handed it the **arXiv preprint** while the corpus already holds
      **the DOI `10.1145/3359183`** for the same paper on the same entry. The
      "inherited" locator was the worse of two locators the corpus is already
      using.
    - **My first dry run got two of these wrong and the dry run is why.** A
      substring needle matched `siri`'s *other* record and skipped a real gap,
      and on `the-algorithm-decides` it selected the **compound** - the exact
      class the exercise exists to refuse. Now it requires an **exact** citation
      match, an empty URL, and refuses outright on any "citing" marker.

51. **The 20 compound citations are a defect class, and 11 could be split with no
    research at all.** A string like "X, citing Y (2021) and Z (2019)." is one
    record standing in for two or three works, which is why no locator can
    attach to it safely. The fix is not to add a URL; it is to split.

    **And the split is mostly a deletion of duplication**: in nearly every case
    the leading work is *already cited separately with its own locator*, so the
    compound was not missing a locator for its first work - it was missing the
    *other* works, which had none anywhere. Replacing it turns "one string
    naming three works, locating none" into "N strings each naming one work,
    locating none", which is honest and independently workable.

    - **11 compounds -> 15 single-work children**, each `needs-source` with a
      claim that says the work is named but not identified, and `split_from`
      preserving the original string so the compound is still on the record.
    - **9 refused or skipped, each for a stated reason**, and two of those
      reasons are the whole point of the guard:
      - **`prince` x2 - the AGENTS item 28 trap, live.** The compound
        `'CBS News (2016), citing The Associated Press.'` has on its entry a
        parent `'CBS News (2016), citing photographs and CBS Minnesota; NPR,
        Music Legend Prince Dies...'` carrying **one URL, the NPR one.**
        Attaching it would put an NPR link on a CBS citation. **A parent that
        is itself compound is refused**, because its single URL belongs to one
        of several works and cannot be attributed to ours. Same for
        `beatlesmania`.
      - 7 skipped because the leading work has no separately located record, so
        there is nothing to inherit from - `cobain`, `siri` x2,
        `the-subscription-box` x3.
    - **Auto-location was tried and removed.** The first version substring-
      matched surname and year, and reported `'Aw & Chua (2021)'` as
      `retrievable` because some record contained both characters somewhere -
      and `'Horton & Wohl (1956)'` likewise. **An author and a year are a pair
      of coordinates, not a work** (item 21), so every child is `needs-source`.
      A child string with no title cannot be matched against a title, and the
      honest state is a visible debt rather than a plausible-looking match.

52. **`citation_audit.py` caught a missing field in the tool that made the change,
    on the run rather than after a commit.** The splitter wrote
    `identity_verified` and `split_from` and **no `claim`**, and the gate failed
    with "13 record(s) print a placeholder where a claim should be". It was
    right: a record with an empty claim is a field promising something it does
    not keep, which is the family this file keeps meeting. Re-running the
    splitter does not help - the compounds are already split - so
    `tools/fill_split_claims.py` repairs precisely the records carrying
    `split_from` and refuses to touch anything else, and reports that
    **0 empty claims exist without it**, which means the 13 were the whole of
    this class rather than part of it.

53. **A tool's path is a landmine, and the tool that showed me the line showed me
    a word that was not in it.** `close_locator_gaps.py` shipped with a hardcoded
    absolute path whose literal was **missing the word "Documents"**, so every
    run died with `FileNotFoundError` on `data/encyclopedia.json` - a file that
    exists, is tracked, and reads fine from the shell. **`read` displayed the
    line with "Documents" in it.** Only `len(str(ROOT))` against the expected 54
    found it: the literal was 44, ten short, which is "Documents" plus its
    separator.
    - **Hardcoding is the existing convention** - 27 tools in this repo do it,
      including `cite.py`, `verify_narrow.py` and `find_citation_twins.py` - so
      this was not a deviation. The finding is that the convention is unsafe, and
      the fix is `ROOT = pathlib.Path(__file__).resolve().parent.parent`, which
      is what `build_cards.py` already does.
    - `tools/derive_tool_paths.py` converted the **twelve** tools written in this
      session and left the pre-existing ones alone, because rewriting 27 working
      tools is unrequested churn with real risk. All twelve were re-run
      afterwards and their idempotency guards still fire.
    - **The general form: the tool output disagreed with the artefact, so read
      the bytes.** A `read` that shows a plausible path is not evidence the path
      is right; a length is.

54. **Relaxing the twin rule from strings to meaning finds 25 candidates, and
    reading them leaves 14 and refuses 11. No score could have made that
    split.** `find_citation_twins.py` matches exact/prefix strings and had
    found 3. Matching on author + year + word overlap instead finds **25**, and
    the whole value of this pass is that the two sets are not the same set:
    **14 are the same work and 11 are not.**

    `tools/attach_read_locators.py` therefore carries an **explicit allow-list**,
    with the reason written per attachment, and no heuristic at all. Every URL
    is copied from the sibling and never typed. **292 -> 306 records with a
    locator; 133 -> 119 without; 96 -> 90 entries.**

    - **`Horton & Wohl (1956)` is now located on both records that cite it** -
      and they carry **different titles for the same DOI**: "Mass communication
      and para-social interaction: Observations on intimacy at a distance"
      against "Mass Communication and Social Interaction". Same authors, same
      year, same DOI. Item 20's rule decides it - **author and year decide, the
      title corroborates** - and the discrepancy is recorded on the record rather
      than smoothed away. This is the founding citation of the term the site is
      named for, and until now one of its two records had no locator at all.
    - **One judgement call, allowed on positive evidence.** `cobain`'s "Seattle
      Times, 8 April 1994" has a *compound* sibling ("Seattle Times...; and
      Rolling Stone (Neil Strauss)") carrying **one** URL - which is normally the
      `prince` refusal. It was attached anyway because the URL itself settles
      attribution: `archive.seattletimes.com/.../nirvanas-cobain-dead...`, so
      both its host and its path belong to the leading work. **That is evidence
      of a kind `prince` did not have**, where an `npr.org` URL on a CBS
      citation could not be resolved that way. The rule is not "compound parents
      are always refused"; it is "refused unless the URL provably belongs to the
      leading work".
    - **And one refusal that shows what a wrong match looks like.**
      `live-commentary`'s "Regelbrugge, 2024" scored **0.11** jaccard against
      three located records - and **no sibling mentions Regelbrugge at all**.
      The entire overlap was the words "parasocial relationships". Left
      locator-less. **A low score is not a weak match, it is usually a bad one**,
      because the shared words are the corpus's own vocabulary rather than the
      work's identity.
    - Also refused: `cobain`'s Tower Records / Billboard record (the sibling URL
      is Borzillo's retrospective, not Tower Records' statement, and the dates
      differ), `cobain`'s "Borzillo, Billboard (2019); Rolling Stone (1994)"
      (two outlets, one URL), and `prince`'s "Melody Chestler... reported in NPR"
      (the sibling URL is a *different* NPR piece).
    - **One case a compound detector must NOT split**, and it is the mirror of
      `grief-extraction`: "Dead celebrities are being digitally resurrected. CBC
      News (2021), reporting Lachman and media lawyer Iain MacKinnon" names
      **interviewees inside one article**, not a second work. The splitter's
      `citing`-marker heuristic would have got this wrong, which is why it runs
      only on records with no separately located leading work.
55. **The front page's top half was five full-width stacked blocks, and
     the gate that owned it was green.** Measured with `tools/probe_front.py`
     and then *looked at* with `tools/shoot_front.py`, which is the order that
     matters: the probe reported `mark={'t': 584, 'b': 734, 'w': 1192, 'h': 150}`
     and then "OK nothing wrong", because what it checks is overlap, overflow
     and two-tone contrast - **none of which is about a mark having a job.** A
     150px iYi sat centred in a 1192px band with 1042px of nothing either side
     of it, between the doors and the top 8, with no copy attached. On a phone
     the wordmark wrapped onto three lines and the eyes were a 150px island.

     - **The gate was not wrong; it was answering a different question.** It
       measured "does the mascot sit inside its box and not overlap the doors",
       and it did. The defect was compositional and no check had a name for it.
       This is the `kind: exact` argument from the other side: a field can keep
       its promise and the artefact can still be wrong. **The screenshot found
       it and no number did.**
     - **The fix is `.masthead-grid`**: the h1 is its own full-width row, the
       line and the thesis pair take the left column, iYi takes the right as a
       bordered card, and the two doors are a full row underneath that closes the
       masthead. The doors were inside the left column at first and the clerk
       card ran a hundred pixels past them - **which moved the dead space to the
       bottom left instead of removing it.** The third row is the fix, not a
       tweak to the first.
     - **Two mistakes of my own are recorded because they cost a round trip.**
       The first edit dropped a closing brace off `.clerk-more:hover`, and the
       page rendered the two doors as unstyled inline text and the top 8 as a
       full-bleed photograph: **one unbalanced brace silently discards every
       rule after it**, which looks exactly like "the doors were always like
       that". Caught by looking. `styles.css` is brace-counted after an edit
       (808/808). The second: an interpolated `None` placeholder put `>None<`
       where the mascot goes, because the f-string was built before the value.

56. **`index.html` is GENERATED. Editing it is not a change - it is a change
     that the next `build_cards.py` quietly reverts, with every gate green.**
     This is the most expensive thing in this file and it was found by breaking
     the page on purpose.

     - `tools/build_cards.py:build_front()` writes the whole of `index.html`
       from an f-string template inside the generator. A masthead redesign, ten
       rewritten hub teasers and three filled art boxes were all applied to the
       *output file*. Then the gate chain ran `build_cards` and **all of it
       reverted** - the old masthead came back, the ellipses came back, the
       empty art boxes came back. `link_audit`, `probe_front` and `verify_narrow`
       were all green, because they were measuring a correctly-built version of
       the old page.
     - **The tell was available and was not used.** The tell is in this file
       already: `build_cards.py` writes `desk/index.html`, `radar/*.html`,
       `section/*/index.html` and thirty other files, and a build that rewrites
       60+ files was reported as "48 stories, 10 section fronts" with no mention
       of the front page. **A generator's output list is its claim about what it
       owns, and it owns the front page.**
     - **So the edits belong in the generator**, and the tests belong where they
       can see it. `tools/test_front_copy.py` now greps the *generated* page
       rather than the source file, which is the only place a reader ever sees
       anything. A test that passes against a file the build owns proves nothing
       - it is the same shape as item 17's `kind: exact` and item 22's queue:
       **the check has to run against the artefact, not against the input.**
     - **Two things were regenerating over each other before that too.**
       `build_cards.py` carried a *second, divergent* `mascot()` - a hand-written
       106x60 SVG with four moods - which was dead code shadowed by the version
       that delegates to `tools/mascot.py`. Python uses the last definition, so
       the site was fine, but a reader of the file could not know that. Deleted;
       there is one mascot now.

57. **Front-page copy is versioned data behind a pointer, because a page whose
     words only change when somebody notices will drift back into a draft.**
     Ten hub teasers ended in an ellipsis - "copying the tactic without copying
     the thing that made it work, which is..." - and ten in a row is what made
     the page read as unintelligible.

     - **The ellipsis was generated, not written.** `build_front` built each
       teaser with `" ".join(take.split()[:20]) + "…"`, which cuts a sentence at
       its own last word: "The panics about fans being manipulated by fandoms
       turn out to be a…". A `take` is 48 to 173 words, so it has to be cut -
       **it is now cut at sentence boundaries** by `deck()` in `build_cards.py`,
       with a clause boundary as the only fallback and no ellipsis ever. The ten
       teasers now read as sentences.
     - **The masthead words are data, not template.**
       `data/front_copy.json` holds one edition per bi-daily release: `line`,
       the two `thesis_*` lines, the `clerk_*` pair, and the two door sub-copy
       slots. `tools/front_copy.py --list|--current|--stamp <date>|--set <slot>
       <text> --to <date>|--diff a b` moves between them; `build_front` reads the
       live one through `front_copy_edition()`. **Appended, never rewritten** -
       the sequence of what the front page said is the record.
     - **Only the prose is data. The counts stay computed.** `{total}` stories
       and `{nent}` entries are read out of `shop.json` and
       `encyclopedia.json` in the template, because a number typed anywhere is
       a claim that goes stale silently and reads as true until someone checks.
       `front_copy_edition()` keeps the template's own constants as a fallback
       so a fresh clone still builds, and **refuses a live edition with an empty
       slot** rather than rendering a hole.
     - **The hub teasers are deliberately NOT in this file.** They come from
       each story's own `take`, so they change when the stories do - which is
       the behaviour the author asked for. Putting them in `front_copy.json`
       would freeze a rotating feed.
     - **The standing instruction:** the front-page copy is refreshed **each
       bi-daily release**, and the refresh is an agent task, not a script's.
       The whole workflow is `--save --note "..."` then `--set <slot> <text>`,
       then `build_cards.py`.

58. **`img/mascot/sheet.svg` was stale, and the two tools that would have said
     so did not exist.** Running `tools/mascot.py --sheet` to look at the moods
     changed 97 lines of a committed generated file: the sheet was still
     carrying **the old rig** - `.iyi-blush` in the selector list, no
     `@keyframes iyi-look`, no `.iyi-gaze` - because the rig gained a gaze and
     lost its blush and the sheet was never regenerated. Nothing referenced it
     in `dist/`, so nothing 404'd, so nothing noticed.

     - **Same family as the 25 drifted title plates** (`plate.py --check`) and
       as the hand-pasted mascot: an artefact generated from data, quietly
       describing an older version of that data. The difference here is that the
       other two had gates; this one had not even the possibility of one.
     - **The fix is that there is now a reason to open it.** `shoot_moods.py`
       rasterises the sheet to a PNG, because **an SVG cannot be looked at
       directly** and a mood grid nobody has seen is a mood grid nobody can
       judge. All eight were looked at before any was chosen - and the finding
       was that **the character was never the problem.** Two disembodied eyes
       read as silly only when they are centred in empty space with nothing to
       do.

59. **iYi is not a decoration, and the author's standing instruction is now
     policy: cuter, page-relevant, unique form per page, integrated rather than
     plopped.**

     - **A page picks a mood for a reason, and the reason is written down.**
       `MOODS` in `tools/mascot.py` carries `watch / hollow / wink / sad /
       panic / love / clerk / asleep` - the house has eight faces and the front
       page was using the default because nobody chose. The front page is the
       record desk, so it runs **`clerk`**, with a caption in the clerk's own
       voice: "I keep the record. Every claim here carries its source, and the
       ones nobody has opened say so. I do not remember you, and nothing here
       pretends to." That last clause is the video strategy's standing rule -
       iYi admits it has a job and **must never claim to remember an individual
       viewer** - and it is now on the front page rather than only on /brand/.
     - **Integrated, not plopped: the mascot breaks the top edge of its card**
       (`.clerk-face{margin:-52px 0 0}`), so it is layered into the composition
       instead of sitting on it, and the bloom halo gives it a reason to be
       there. On a phone it becomes a row inside the same card rather than its
       own band.
     - **Never hand-paste the SVG.** `mascot.inline(mood, size, cls)` gives each
       copy its own gradient ids and its own `--d` stagger, so a page full of iYi
       does not blink in step. `build_front` calls `mascot(168, "mascot-hero",
       mood="clerk")` - one call, from the module that owns the character.
     - **Still owed:** the other pages. `/brand/` has its own grid, the hub
       tiles each have a section colour and a giant glyph letter, and every
       entry page has a plate. Each is a place a mood could be chosen *for that
       page's subject* rather than inherited. The mechanism exists
       (`mascot.inline` + a per-page class); the per-page choices are editorial
       and are not made by a script.

60. **`.clerk` was two components sharing one class name, and the dead one was
    winning.** Found by screenshotting the front page and reading the copy, not
    by any measurement - which is the only reason it was ever going to be found.

    - **The masthead card asks for one thing and gets another.** `styles.css`
      defines `.clerk` twice. Line 317 is the front page's mascot card
      (`display:flex`, a single 330px column). Line 952 was a `/shelf/` component
      that was deleted, and its stylesheet block was not; its *bare* `.clerk{}`
      selector still matched the live card and came later in the file, so it won.
      Measured in Chrome: the card asked for `display:flex` and computed
      `display:grid` with `grid-template-columns:197.453px 50.5469px`. Its own
      copy rendered **8 lines at a 191px measure - about 24 characters** - and
      "WHAT THE MASCOT IS FOR" sat in a **50px** column, three words to a line.
      Now one 288px column, 6 lines at 286px, kicker and link one line each.
    - **Nothing in this repo could have seen it, and the reasons are the useful
      part.** It overflows nothing, so `verify_narrow` is silent. It overlaps
      nothing, so `probe_front` is silent. Every class in it is real and defined,
      so `check_css` reports it as *styled*. The page builds, the file 200s, and
      it looks like a design decision. **A dead component's stylesheet
      outliving the component is the same shape as the 25 drifted plates and the
      stale mascot sheet - except that here the stale copy was the one being
      applied.**
    - `check_css.py --orphans` now holds it: descendant selectors that match no
      element in any generated page. It is the inverse of that file's existing
      check, and it found **17 orphaned layout rules** already in the
      stylesheet (`.hub-art img`, `.law .n`, `.sidebox ul`, `.qs input` ...),
      which is the same bug class that had not detonated yet.
    - **Two versions of that gate were wrong before it was right, and the first
      one is the one worth remembering.** It read prose out of CSS comments and
      reported "and its height" as an unmatchable selector. Then its block
      scanner **discarded every top-level selector**, so it reported **0 orphans
      while the dead rule was still in the file** - it passed the red test this
      project requires, because the thing it failed to see was the thing under
      test. And it flagged `.ent-hero img` on a page that opens with
      `<figure class="ent-hero plate"><img ...>`, because `<img>` was being
      deleted from the tree it matched against. **A measurement that cannot see
      its own subject will pass any test you give it.**
    - **It is a ratchet, not a hard failure**, because it starts life 17 behind.
      Same reasoning as the 94 URL-less records: a gate that is red on arrival
      gets switched off inside a week, so the committed number is a ceiling that
      can only fall and `--ratchet` is the only way to move it.
    - `.yt-facade iframe` is exempt and says why: `main.js` appends the iframe on
      click. **A gate should learn the field, not be silenced** - that is the
      `via` lesson, and the exemption is a declaration with a reason, not a
      suppression.

61. **43 of 227 entries could not be found by any word of their own name, and
    the cause is the writing being good.** The encyclopedia index has searched
    `title + summary + era` for a long time, and all three are written the way
    they are *on purpose*: they describe the phenomenon and refuse to name the
    subject.

        nancy-drew      "Fifty-four years of letters to a fictional detective"
        siri            "A voice assistant on every phone, addressing the user by name"
        dorian-gray     never says Dorian Gray
        superman-comic  "A character who cannot die, printed in a newspaper"

    So a reader who knows who Nancy Drew is and types "nancy drew" gets nothing.
    Measured by feeding every entry's own `id` back through its own haystack and
    counting the misses: **43**, including `harvey`, `casper`, `alf`,
    `deadpool`, `charlie-chaplin`, `mary-pickford`, `mickey-mouse`,
    `rudolph-valentino`, `tony-stark`, `gobekli-tepe`, `lugosi-burial`,
    `fight-club`, `howdy-doody`, `siri`, `vtuber`, `superman-comic`.
    **An encyclopedia that cannot be searched by name is not an encyclopedia**,
    and no gate here could see it: `link_audit` checks that links resolve, not
    that anything can be found, and every gate was green.
    - **The fix is the `id`, which IS the common name - and it is never
      printed.** It goes in `data-hay` and nowhere else. AGENTS records the
      `ANCHORED - HORTON-WOHL-1956` trap: an identifier shown to a reader reads
      as a citation. A search index is not a page. 43 misses -> **0**, and all
      20 of the worst names verified in a real browser against the generated
      page.
    - `tools/verify_findable.py` holds it, and **confirms red** by removing
      "nancy drew" from one haystack. Two attempts at that red test proved
      nothing first: the corruption regex matched nothing and still reported
      green, and the second was a PowerShell parse error that never ran - item
      30, again.
    - **And the check's own first version reported 167 missing, including
      `margery-kempe` whose title IS "Margery Kempe."** It paired rows to
      entries positionally using its own idea of the generator's sort, and
      `build_cards._y()` is not `year or 0`. It now reads the id out of each
      row's own href. **And even that regex could span a `</tr><tr>`**, which it
      did during the red test - it handed back the neanderthal haystack for
      nancy-drew - so the rows are split apart before they are parsed.

62. **Two of the four classification axes were not filterable on the index, and
    the missing ones are the ones that make the corpus mean anything.**
    `otherness` held 24 placed entries and `reciprocity` held 10, and the only
    way to reach either was to read prose. The reciprocated and simulated
    entries are the *exceptions* - "a corpus about one-sided attachment that
    cannot count its own exceptions is not measuring the thing it is named
    after" - so the gap was exactly where the site is most interesting.
    Both are filter rows now, with counts, verified by driving the real page:
    `simulated` -> 5, `reciprocated` -> 3, `directed` -> 2, `made` -> 9,
    `haunted` -> 4, and a no-match term returns 0 and a cleared one returns 227.
    - **The labels come from `data/taxonomy.json`, never from a list written
      here.** `build_atlas.py` once carried its own copy of the media list, it
      drifted, and two media were invisible from the map for two releases. A
      second copy of a classification is how that happens.
    - **Registers deliberately get no chips.** `taxonomy.json` defines them
      without a `members` key and `encyclopedia.json` has no register field, so
      there is nothing to count - and item 35's argument is that inventing a
      field would be the fourth instance of this file's own family. A chip would
      promise a set the page cannot produce.
    - **A member with nothing behind it is left off, not filled in.** The chips
      are built from counts, so a hole is a chip that is not there rather than a
      zero nobody can see - the same rule as the empty taxonomy sub-categories.

63. **`clusters.py` had drifted from `atlas.py` and a reader could see it.** The
    media tiles on the index are built from `MEDIUM_NAME` in `clusters.py`, a
    second copy of the list `atlas.py` validates against. It had thirteen
    entries where `atlas.py` had fifteen, so `stage` and `visual_art` - added in
    items 39 and 42 - fell through to `m.replace("_", " ")` and printed as
    **"stage"** and **"visual art"** in lower case in a grid where the other
    fourteen tiles are Title Case. Item 41 recorded this as "cosmetic, recorded
    rather than fixed"; it was on a public page the whole time.
    - **Importing `MEDIA_LABEL` is not the fix.** Its wording is deliberately
      different - "Scripted television" against "Scripted TV", "Artificial
      intelligence" against "AI and chatbots" - because one is an atlas chip and
      the other is page copy. So the two lists stay separate and the drift is
      made impossible instead: `_assert_covers_the_medium_axis()` raises at
      import if any `MEDIA` member has no `MEDIUM_NAME` label. **Confirmed red**
      by deleting the two and watching `build_cards.py` stop.

64. **The front page's two thesis doors were unreadable, and the cause was that
    they were a pair of unrelated facts presented as a pair of related ones.**
    Asked to remove ambiguity from the front page, the sharpest instance given
    was the second door: **"The thing. Somebody carried their dead into a cave
    and set a stone under her head."** Four separate faults, and none of them
    is the sentence being poetic:

    - **The label and the content disagreed.** "The word." names a category -
      the coinage. "The thing." also claims to name a category, and what
      follows is *one archaeological episode*. So the label promised a class and
      the copy delivered an anecdote, and the reader has to guess which they
      are getting.
    - **Neither sentence said why it was on the page.** 1956 survives that
      because "coined parasocial" is self-evidently about the site's name. A
      Neanderthal burial is not, and the front page gave no reason - which is
      the whole reason `neanderthal-burial` is in the corpus, and it was being
      left as trivia.
    - **The two were given identical visual weight** - same grid cell, same
      numeral size, one grey one orange - so the page invited the reading that
      they are the same kind of claim. They are not: one is a naming event, the
      other an archaeological inference.
    - **And it read awkwardly**: "Somebody" where the entry has a real subject,
      and a pronoun shift from "their dead" to "her head" with nothing between.

    - **The fix is structural, not a rewording.** Each door is now a plain short
      fact - "The word." / "The practice." - and the reason they belong together
      is stated **once, below the pair**, where it binds both: *"Both are people
      going back to somebody who cannot answer."* Asking each door to carry its
      own justification had made one of them **twice the length** of the other -
      4 lines against 8, with 120px of dead space under the short one, because
      the two are forced into equal columns. **A caption can carry what a layout
      cannot.**
    - The same pass removed the other ellipsis on the page: **"Everybody has
      one."** was doing real work - one *what*? - and is now "**Nearly everybody
      does.** This is the news feed for that feeling."
    - **This is the `front_copy.py` workflow doing its job**, which is the point
      of item 56: a new edition dated 2026-10-13 via `--save`, every string
      written with `--set`, and `build_cards.py` afterwards. Nothing was typed
      into `index.html`, which the next build would have reverted.
    - **`thesis_pair` is a new slot**, so it went into `front_copy.SLOTS`, into
      the `build_front` fallback, and into the `missing=` check that refuses to
      render an empty slot. **Adding a slot to the data without adding it to the
      refusal list is how a hole gets rendered as a hole.**

65. **Seven of ten hub tiles had body copy below WCAG AA, and the hierarchy was
    being carried by alpha over ten different backgrounds.** The ten "ten ways
    it shows up" tiles on the front page are the one place body copy sits on a
    saturated section colour rather than on the dark page. The deck was
    `rgba(18,10,5,.72)` and the "N MORE" link `rgba(18,10,5,.6)`.

    Measured by rendering the page twice - once as shipped, once with the tile
    text hidden - and sampling the pixels where the text sits:

        tile        h3    deck    link
        IDOL       5.49    3.84    3.08
        CHARACTER  4.14    3.14    2.64   <- worst
        DANGER     4.38    3.35    2.79
        ... nine of ten links under 4.5, seven of ten decks under it

    **Alpha is not a way to express hierarchy on a variable background**, and
    the site already had the counter-example on the same tile: `.hub h3` is
    solid `#120a05` and was the only text clearing its threshold on all ten. The
    fix moves the hierarchy to size and weight and makes the deck and link
    solid. Worst ratio **2.64 -> 4.77**, all twenty measurements clear.
    - **And the first attempt at the fix made it worse** - darkening the tile
      took the worst from 3.53 to **3.14**, because the copy is near-black and
      darkening the ground converges the two. Reverted and went the other way.
      **Contrast on a dark-ground design is not a one-directional dial.**
    - `.t8-art-none` was a no-image plate designed for the top 8 and never wired
      to anything - one of the orphans item 60's gate reported. The front page
      now uses `.t8col-plate` and `/top8/` uses `.t8-plate`, so the third version
      of the same idea is deleted rather than left to drift.
    - `tools/probe_hub_contrast.py` holds it. **Three probes got this wrong
      before one worked**, and each failure is a different way of measuring a
      layer you are not measuring: reading `backgroundColor` returned the PAGE
      colour for all ten tiles at 1.02:1, because `.hub` paints with a
      `background` gradient; computing the gradient arithmetically would need a
      photograph at 62% opacity composited under a `color-mix` with `transparent`;
      and the third composited the translucent TEXT into the background and then
      compared the raw text colour against the composite - text against itself -
      reporting **1.31:1 on tiles that are plainly legible in a screenshot**.
    - **And its first red test changed the file, confirmed the change landed, and
      reported numbers identical to two decimals on all ten tiles.** Chrome was
      serving a cached stylesheet from a persistent profile. Every render now
      gets a fresh `--user-data-dir` plus `--disable-application-cache`, and the
      gate refuses to run if it does not find ten tiles. **A gate that cannot see
      the change it is gating is the same defect as one that cannot fail.**
      Confirmed red after the fix.

66. **The top 8 caption made a claim about every member of a set that two of them
    were not part of.** It read *"what is up there is what the cartoons turned
    into instead... which is a longer way of saying the pictures are of the
    audience."* Item 25 had corrected this sentence by opening all six
    photographs - and then the list became eight entries, and **two of them have
    no photograph at all**: `t8-5-dragontales` and `t8-7-doug` were withdrawn at
    review, with no image and no source.

    So the sentence was true of the six and false for the two, which is item
    25's defect with the numbers inverted - and it survived *because* the style
    had been fixed once already, which is what made it look settled. **A fix
    that has been applied is not a property of the thing it was applied to.**
    The caption now counts, and says why two are blank.
    - **And the front page's no-image state was a bare orange numeral** where
      `/top8/` had been doing it properly all along - a designed plate reading
      "no free frame exists". Two of eight, in a grid where six are photographs,
      so two read as broken images. The front page now uses the same idea at
      52px: the show in display type on its own colour.
    - **The first cut of that word was "DRAGONTA"** - a fixed-length slice
      through "Dragon Tales", which reads as a typo rather than a decision, and
      is the same defect as the front-page teasers that used to be cut at their
      own last word and given an ellipsis. Cutting at a word boundary fixed it,
      and then a `vw` font-size broke "DRAGON" to "DRAGO N" on a phone because
      the art box is a fixed 52px and the type was scaling with the viewport.
      **Size type against the box it sits in.** A word with nowhere to cut falls
      back to the rank rather than breaking.

67. **The corpus was written in markdown and the renderer had never supported
    any, so 709 `**bold**` markers were reaching 52 deployed pages as literal
    asterisks.** Found by *reading an entry page*, not by any gate - which is
    the only reason it was ever going to be found, and it is the third time in
    this file that the screenshot found what the measurement could not.

        ... together with "a few letters written by parents on behalf of their
        children". **Fifty-four years, addressed to a girl who did not exist.**"
        The finding aid does not record who those letters were addressed to...

    **`build_cards.py` contains no inline-formatting path at all.** It is not a
    regression; the renderer never had one, and the recent `add_*.py` scripts
    wrote prose assuming it did. The damage is concentrated in the newest work:
    `american-gothic` 72, `marvel-club` 70, `queen-for-a-day` 62,
    `krapp-last-tape` 44.
    - **Measured before changing anything, because the fix is not obvious.**
      Only TWO fields carry markers - `significance` (428) and placement `why`
      (84). **Zero** sit in a `summary`, so no `meta description` or `title`
      attribute is affected. Every marker pair is balanced (0 odd counts), and
      the 14 entries a naive regex flags as "nested" are sequential spans
      - "**A.** middle. **B.**" - not spans inside spans. All three facts are
      what make a non-greedy `\*\*(.+?)\*\*` correct rather than lucky.
    - **Two functions, not one change to `esc()`.** `esc()` is also used for
      `content="..."` and `title="..."`, so converting inside it would put
      `<strong>` inside an attribute - a new instance of this file's own family.
      `emph()` escapes and then converts; `esc()` stays a pure escape.
    - **The same field had a second leak, and it was larger.** 33 entries use
      blank-line paragraph breaks that HTML collapsed to a space, so a 2,640-word
      entry ran as one unbroken wall. `prose()` emits real paragraphs - and
      **only the first** carries `lede2`, because that class carries the drop
      cap and giving every paragraph the class puts a drop cap on each one.
    - **And the finding that makes it worth having: the entries were WRITTEN as
      argument.** Each paragraph opens on a bolded claim - "**And there are
      recordings.**", "**The honest limit is on the entry: ...**" - and the
      signposting was invisible on every one of them. Fixing the markup did not
      change a word and roughly halved the time to read an entry.
    - **The last marker was not a bug and the converter was right to refuse it.**
      `data/queue.json` has a draft with an **unbalanced** `**`. `emph()` leaves
      it literal rather than guessing. That draft is in the signoff queue, so
      `md_leak.py` REPORTS it and does not fail on it - an unsigned draft is
      raw by design, and a visible stray marker is the desk doing its job.
      **A converter that silently mangles prose is worse than one that leaves
      asterisks alone.**
    - `tools/md_leak.py` holds it and is **confirmed red** by injecting a span
      into a published page. It also counts `code \`` and `italic *` and
      deliberately does **not** fail on them: 468 backticks, 412 of them on
      `/taxonomy/`, where the author marks taxonomy keys as `` `persona/idol` ``.
      Rendering those as `<code>` would restyle that entire page, so it is an
      editorial decision and not a lint fix. **Reported until somebody decides.**

68. **Measured, for the purpose/attention/use analysis asked for on 2026-10-13.**
    320 deployed pages: 227 entries, 48 stories, 10 section fronts, 11 timeline,
    3 cases, ~20 hubs. 8,411 internal links, and **all 227 entries reachable
    from `/` in at most two clicks.**
    - **19 of 25 page types have exactly one interactive element, and it is
      `button.menu-btn` - the hamburger.** Real interactivity exists on five
      page types: the encyclopedia hub (search + 21 filters), the timeline
      (search + 121 chips), the front page (email), `/tip/` (form) and `/desk/`.
      **The site is a well-built library with no reading instrument.**
    - **All 227 entries have zero `<h2>`.** Median 488 words, p90 1,109, max
      2,640. No landmark, nothing to link to, and no handle to quote an entry
      by except its title - which never names its subject.
    - **5 pages have no inbound internal link**: `classroom/` and three `cases/*`.
      Content that exists and cannot be navigated to, which is a decision being
      made by omission.
    - **The two graph legends are the only places the classification is
      _explained_ rather than shown**, and their labels are set at ~9px.

69. **Backticks and italics rendered, and `<code>` had no stylesheet at all.**
    The `**` fix left the same defect class in two other forms: **468 backticks
    and 80 single-asterisk italics**, 412 of the backticks on `/taxonomy/` where
    the author marks classification values as `` `persona/idol` ``.
    - Measured before converting: 74 distinct backtick spans, none over 40
      characters, all machine keys. 53 distinct italic spans, mostly work
      titles (*Whiz Comics*, *The Scream*) plus genuine stress (*is*, *also*),
      and **zero** ending in punctuation or exceeding 45 characters - so the
      pattern cannot eat a sentence.
    - **The reason this was left unrendered first is the useful part.** `<code>`
      had **no rule anywhere in the stylesheet** and no page emitted it, so
      introducing the element without one would have dropped 412 keys into the
      browser's default monospace on the one page whose entire job is teaching
      the vocabulary. **An element with no style is not a fix, it is a second
      defect.** `code` is now set in `--label` - IBM Plex Mono, the face this site
      already uses whenever a machine speaks - with `overflow-wrap:break-word`
      and **not** `nowrap`, because `character/fictional-protagonist` is 30
      characters in a narrow column and a rule that refuses to break overflows.
    - **And the gate caught two of its own misses.** The first pass converted
      two of the four taxonomy triad renderers, because two of them print the
      same line and a text search for `esc(m[key])` returned them as one match.
      The 12 surviving backticks were the tell. **A converter applied by search
      finds the sites you searched for, which is not the same as the sites that
      exist.**

70. **Entry landmarks, and a correction to what item 68 reported.** Item 68 said
    "all 227 entries have zero `<h2>`, median 488 words". **The 488 was the
    whole `<main>` block - sources, graph, relations and taxonomy card included -
    not the entry body.** The body is a median of **43 words**, and **171 of 227
    entries run under 150**. Almost none of them need a landmark, and "227
    entries carry no headings" described a reading problem that did not exist.
    **A number measured about the wrong element is the most confident kind of
    wrong**, and it came from stripping tags over `<main>` instead of over the
    one field the claim was about.
    - **Only 4 entries exceed 700 words** - `american-gothic` 1,266,
      `marvel-club` 984, `queen-for-a-day` 938, `krapp-last-tape` 720 - and
      **zero entries are long with nothing to derive**. Every one of the four
      opens its paragraphs on the author's own bolded claim, 23 between them.
    - So `prose(..., heads=True)` is a **promotion, not an invention**: the
      script changes the rendering of structure the author wrote. 19 entries
      gain headings, 6 of them a contents rail. The rules are all measured
      rather than tuned: the lead must start the paragraph (or a bold aside
      becomes a heading), must be under 90 characters (27 of 96 leads are longer
      and stay bold, because a sentence is not a heading), is never the first
      paragraph (drop cap, and directly under the h1), and must leave text
      behind.
    - **A rail needs three, not two.** Two links in a list is a menu.
    - **Two real bugs, both from slugging the ESCAPED text**: an id cut mid-word
      ("...a-reading-rathe") and an HTML entity in a slug
      (`the-tape-x27-s-own-contents`). Matched on the raw text instead, and the
      cut now lands on a boundary. **A generated cut has to land where a person
      would have stopped** - now the third time this file has had to say it.
    - `tools/verify_landmarks.py` holds it. **Its first version tested
      `id =~ /[a-z0-9]-[a-z]*$/`, which matches every id in existence** and
      reported 29 failures on correct data - a gate crying wolf. It happened to
      contain the two real bugs inside the noise, which is the usual bargain,
      and it now tests the property instead: each id must be exactly the slug
      of its own label. Confirmed red by truncating one.
    - **`md_leak.py` then caught a regression I introduced in the same sitting** -
      a heading and a rail line both used `esc()` instead of `emph()`, so a code
      key inside a heading rendered literally. **A gate earns its place by
      failing on the author.**

71. **Five deployed pages had no inbound link, and four of them were indexable.**
    `404.html` is correct - a 404 handler should have nothing pointing at it.
    The rest were a content type with no front door and a product nobody could
    reach:

        cases/kempe-to-stans.html          Case File 001
        cases/blockbuster-knew-your-name   Case File 002
        cases/dream-recording-metaphor    Case File 003
        classroom/index.html              a $49 product

    All four were **indexable** - no robots meta - and absent from
    sitemap.xml, so a crawler could index a page it had no way to find. Nothing
    in `link_audit.py` could see it, and the reason generalises: **every other
    check in that file asks whether a LINK WORKS, and none asked whether a page
    is REACHABLE.** It now fails on any indexable deployed page with no inbound
    link. `404.html` and `noindex` pages are exempt, because for those
    "unreachable" is the intent rather than an omission.
    - `/cases/` now exists, **generated from the frontmatter of `cases/*.md`** so
      it cannot drift when a fourth file is added. It deliberately does NOT
      render the member sections - that text is the paid product and is not this
      script's to publish. Linked from `/shelf/`; `/classroom/` from
      `/membership/`.
    - **The shelf link was written into `shelf/index.html` twice and the next
      build silently reverted it both times.** `shelf/index.html` is GENERATED,
      at `build_cards.py:4047`, from `build_shelf()` - I had inferred from
      `cases/` and `classroom/` having no generator that it was hand-written.
      Third attempt went into `build_shelf()` and stuck. **This is item 56:
      a generator's output list is its claim about what it owns, and it owns
      more than you expect. Read `main()` before hand-editing anything.**
    - **The orphan check itself was wrong twice.** It scanned the whole repo
      rather than `dist/`, so it counted every page twice, swept up Chrome's
      calibration files under `episode/.chrome/`, and reported 275 orphans. Then
      it resolved relative links with `urljoin("/", href)` for pages at the
      root, which returns an absolute path matching no key in the table, so
      every page linked only from the front page - `figures/`, `tip/` - came
      back orphaned on correct data. **A resolver that is wrong for the most
      common case in the tree is a resolver, not a measurement.**
    - Its red test took three attempts and proved nothing twice: it edited the
      source while the check reads `dist/`, and then repointed the link at a
      404 so the run failed on the broken-link check while the orphan check
      stayed green. That is a red, but not the red being tested. Note the two
      trees are deliberate - reachability is a property of what is deployed -
      and they now say so in the file.
    - **Still owed:** the three Case File pages are stubs. Each `.md` carries a
      free TEASER and a gated MEMBER FULL block and the HTML renders neither,
      only "full take lands in the Friday Signal".

72. **The one piece of interactivity added where the reader already is.**
    Item 68 measured that 19 of 25 page types have exactly one interactive
    element and it is the hamburger, and that the honest verbs for this subject
    are retrieve, compare and follow. Retrieval and comparison were fixed in
    items 61 and 62. This is **follow**.

    - **The entry page already had a related block, and it is name-derived.**
      `.ent-seq` ("Same story, N other entries") finds entries whose ids share
      a significant word, so it catches `mickey-mouse` from `alf` and nothing
      at all from `the-dog`. The new block is **classification**-derived - the
      attachment sub-category - so it finds `the-dog` from `alf`, which the
      name heuristic cannot, because nothing about those two ids resembles
      anything. Both exist and are labelled differently, because they answer
      different questions.
    - **Ordered nearest-in-time first**, not by year. On a site laid out along a
      timeline the neighbours in time are the ones that make a shape; sorted by
      year alone the block is just a list. `harvey` (1950) gets 1942, 1942,
      1946, 1946, 2003.
    - **Measured before building, and the measurement changed the design.** 195
      of 227 entries have three or more siblings in their sub-category; **32 sit
      in a shelf of one to three** and would have shown nothing. Those fall back
      to the parent CATEGORY and are labelled "Wider shelf" rather than "Also
      filed as", because "here are two entries filed exactly here" and "here is
      the wider shelf" are different claims and the label is the only place a
      reader can tell. `the-dog` falls back and lands on its nearest neighbours
      among the companion entries. **All 227 entries now have one.**
    - `verify_landmarks.py` holds three properties that would otherwise fail
      silently: every entry has a strip, it never links to its own entry, and
      it never carries fewer than three. Confirmed red by pointing a strip at
      its own page - a link that resolves perfectly, so nothing else in the
      toolchain would have caught it.

73. **AGENTS item 45 was wrong about the register axis, and wrong in the way that
    cost the most: it said the gap needed a new field, and the field was never
    needed because the information already existed.** Item 45 records "there is
    no way for a reader to find the entries on a register", and item 35 rules
    out the obvious fix four times over - a `register` field, because a field
    nothing counts is this file's own defect family. Between them the project
    had concluded the gap was unclosable.

    **Measuring it instead of reasoning about it closed it in one line.**
        register        placement reasons naming it   searchable before
        contest                          28                    0
        bond                             26                    0
        archive                          13                    0
        cog                               8                    0
        undemanded                        2                    0
    86 placement reasons name a register. `dear-kitty`'s reads "the purest
    instance of an undemanded tie on this site". **All eight were written down
    and reachable from no search box**, along with **59 backticked keys** -
    `idol`, `made`, `haunted`, `simulated`, `companion/social-agent` - which the
    author marked in backticks precisely so somebody could look them up.
    - So the axis did not need a field. It needed **the sentence that already
      says it to be indexed**, which is what `build_cards._hay()` now does with
      the placement reason. 0 -> all 8 registers reachable; **0 of 59 -> 59 of
      59** backticked keys findable. Every specific name still resolves to one
      entry: `harvey` 1, `deadpool` 1, `nancy drew` 1, `siri` 1.
    - **The measurement had to check the SET, not the count.** `cog` matched 3
      entries before this change, on the ordinary English word, so a count would
      have looked close to right for the wrong reason. `verify_findable.py`
      asserts that every entry naming a register is inside the results for it,
      and **confirms red** by redacting the word from every haystack - which
      names the two entries that became unreachable.
    - **`md_leak.py` caught the regression in the making.** Unwrapping the
      backticks and nothing else left **84 `**` and 10 `*`** sitting raw in a
      `data-hay` attribute - markup describing text, inside a search index that
      never gets rendered. **A search index is not a page: it wants the text, not
      the markup.** Third time this session a gate has failed on work from the
      same sitting.
    - Cost: the haystack went from 267 to 731 characters per entry and the
      index grew, and the stopword-ish terms degraded (`the` 204 -> 226, `one`
      61 -> 109). Those matched 90%+ of entries before and still do, so nothing
      that meant anything specific got worse - which is the only question worth
      asking of a change that makes everything match more.

    **The general form, and it is the one worth carrying out of this file: a
    "this gap cannot be closed without a schema change" conclusion is a claim
    about the schema, and the cheap test is whether the information is already
    written down somewhere nobody was looking.** It was, 86 times.

74. **The Top 8 could not rotate, and could not have been caught, because the code
    that would have rotated it had never run.** Four defects in one feature, and
    three of them are only visible if you ask what code has actually executed.
    - **`t8_pool.py` capped `featured` at eight, and `build_cards.py` only rotates
      when `featured` exceeds eight.** The cap made the rotation branch
      unreachable, so the front page showed the same eight moments for as long as
      the cap held. Two files, each individually reasonable, whose combination
      means the feature they implement cannot happen.
    - **The unreachable branch referenced an undefined name** (`_j.date`, in a
      file that imports `datetime`). Nothing raised, because nothing ran it. Same
      family as the video-duration label in item 13: *a string that only executes
      after the thing it describes changes is a string nobody checks.*
    - **`build_top8` read the raw pool while `build_front` applied the stage
      filter and the rotation, so `/top8/` rendered 14 items including
      `candidate` ones.** Two derivations of "which eight", and the wrong one is
      the one that publishes unreviewed material. This is the single most
      dangerous class in this file: **a question answered twice is a question
      answered wrong once**, and the fix is one function both call
      (`top8_window()`), not better discipline at each site.
    - **The numeral was a stored `rank`,** which describes the pool rather than
      the page and goes stale the moment the window moves; a promoted candidate
      has none at all, so the page raised `KeyError`. It is now the position in
      the pool, taken at render time.
    - **And the ceiling was enforced while the floor was not.** The comment said
      "must never show fewer than eight" and archiving three moments left the
      page quietly showing five. The half that bites is the one that produces a
      valid page. Confirmed red by archiving one and watching the build refuse.
    - **A refactor that changes "which eight" is not a refactor that only changes
      "which eight".** `pick_list` returned a whole list object; replacing it with
      a dict rebuilt from four of its keys silently dropped `image`, and `/top8/`
      lost its hero photograph with no build error, no 404 and no broken link.
      **The only thing that noticed was `check_css --orphans`**, because
      `.t8-hero-fig img` had become a selector matching nothing - a bug that
      manifested as a dead CSS rule one module away.

75. **`git checkout` restores from HEAD, not from where you were, and it cost this
    project twice.** Testing a build assertion by archiving a Top 8 entry, the
    undo was `git checkout -- data/features.json`, which threw away the
    uncommitted Hey Arnold swap that had been sitting in the tree for a session.
    It was recovered from a backup taken *after* the mutation, so it only worked
    by luck. The earlier loss was the front-page redesign, wiped the same way.
    - **`Copy-Item` before the test and restore from the copy.** Or commit first.
      The habit costs one line and `git checkout` on a dirty corpus file is a
      coin flip.
    - **A backup taken after the mutation is not a backup.** The recover script
      also asserted nothing, so it reported a restore it had not verified.

76. **Internal vocabulary reached the public pages, and reading them is the only
    way it would ever have been found.** `/ledger/` shipped reading "...and
    AGENTS is explicit that this is not a gap." `AGENTS.md` is a working file
    for whoever maintains the repository; a reader has never opened it. Same class
    as the `CLERK'S DESK` link and the "no free frame exists" note.
    - **Reading the built page as text found five more,** all pre-existing: a data
      field name (`provenance: thesis`) on `/citations/`, `AGENTS.md` and
      `encyclopedia.json` in the taxonomy prose, and a baseline JSON path inside a
      citation's own `claim` on `neanderthal-burial`.
    - **Thirteen placement reasons read "Added by tools/expand.py; review the
      reason."** A to-do, naming a tool, printed where an argument belongs - the
      same shape as `claim: "the entry as a whole"` and the fourteen citation
      strings that were literally the word "verify". `expand.py` now takes the
      candidate's own `fits` text and **refuses** rather than falling back.
    - **No gate could see any of it.** They check links, selectors, counts and
      relations. None reads prose for words that mean nothing to a reader.
      `tools/check_internal_leaks.py` scans `dist/`, not the source, and is wired
      into the source tier with a justified allowlist for `/desk/`.
    - **Its first run reported clean over zero pages,** because `ROOT` had one
      `parent` too many and pointed outside the repository. It now asserts its own
      root and **refuses to report on an empty tree**: a measurement that cannot
      see its own subject will pass any test you give it, which is the eyelid-arc
      rule applied to a checker.
    - **The repair script was not atomic** - it wrote the first file, then aborted
      on the second, reporting a clean abort that had already half-done the job.
      It verifies every replacement before writing any, and is safe to run twice.

77. **Two numbers were wrong in copy a person had already approved, and rendering
    them from the data is the only reason either was caught.** The exceptions page
    was pitched as "the reciprocated three span thirty-five thousand years" and
    "nine of fifteen media hold none". The real span is **17,020** and the real
    count is **eight**. I wrote a plausible number, believed it, and the number
    was approved.
    - **Every figure on `/ledger/` and `/exceptions/` is now computed from the
      data at render time** - including the argument the page is making, the
      longest silence between consecutive instances (70 years), which is derived
      as a difference rather than typed.
    - **The general form: a figure that carries the page's argument is the one
      most likely to have been checked least.** A number in a paragraph is not
      obviously a claim, which is what makes it the dangerous kind - item 43's
      finding, and it applies just as much to copy written in a hurry at 2am.

78. **`provenance` had a third value nobody had declared, and seven entries held
    two at once.** The corpus has exactly two - `sourced` and `thesis` - and
    `thesis` means "the site's own argument, takes no citation at all". Seven
    entries, all of my own batches, set `provenance: thesis` *and* carried
    citation strings: asserting both that the entry is an argument and that here
    are references for it. `expand.py` refuses the combination and the seven are
    now `sourced`.
    - **A classification that cannot represent a real state will accumulate
      entries that assert the impossible**, quietly, and nothing renders wrong.

79. **Eleven deployed pages were missing part or all of the head block, and the
    tool that fixed heads only ever knew one file.** `unify_heads.py` inserted
    the three links into every longhand head in `tools/build_cards.py` - but it
    hardcodes that one file, and the project's heads live in four places:
    `build_atlas.py`, `build_quiz.py`, `build_cards.build_404()`'s own template,
    and **eight hand-written pages with no generator at all** (`membership/`,
    `tip/`, `signal/latest.html`, `audit/`, `classroom/`, three `cases/*.html`).
    So 404, atlas, quiz, membership, tip, signal, audit, classroom and the three
    cases carried no `ledger/feed.xml`; of those, only atlas carried `radar.xml`
    too; and `signal/latest.html` had **no `<head>` whatsoever**, so nothing at
    all could be found on it. The 336-page count had been reported as "325 carry
    both feeds" and read as one small queue rather than a tool whose coverage
    ended at one file.
    - **Fixed at the generator where a generator exists** - `build_404`'s
      template, `build_atlas.py`'s `PAGE`, `build_quiz.py`'s `PAGE` - and by
      hand for the eight that have none, which is the decision this item
      records: **a hand-written deployed page is edited once and gated**, not
      given a generator it does not need. Three of the eight are CRLF
      throughout, so a `\n`-based multi-line replacement never matches them;
      the write used an explicit newline-preserving read/write and asserted the
      anchor appeared exactly once first.
    - **`tools/check_heads.py` is the gate, and it reads `dist/`** - the
      deployed tree, not the source - so it covers the pages nothing rebuilds.
      It refuses to report on a tree under 100 pages for item 76's reason, and
      it was confirmed red by stripping the ledger link from one deployed page
      and green after restoring it. Wired into `gates.py`'s post tier beside
      the other dist-reading checks.
    - **The page it will catch again first is `signal/latest.html`**, which is
      replaced by hand every Friday from the broadcast email - the one page
      whose entire update process is "paste over it". Its head block is in the
      deployed copy and not in any process, so the gate is the only thing
      standing between the next paste and a page that silently stops offering
      the feeds.
    - A source-tree sweep confirms the state: **337 html files, 1 offender,
      `v1-oxalpha-backup.html`** - which is correct, it is undeployed by name
      and the gate never sees it.
    - **And one page was carrying the block twice.** `exceptions/index.html`
      shipped the radar and favicon `<link>`s twice - once from the standard
      trio near the top of the head, once from a pair the template already
      carried further down. A duplicated autodiscovery link is a feed every
      reader's reader lists twice. It was found by a duplicate scan whose
      first version was wrong in the other direction: it counted substrings,
      and the shared `HEAD` constant carries an HTML comment explaining the
      two feeds that names "radar.xml" and "ledger/feed.xml", so all 323
      pages rendering that comment "duplicated" it. **A comment is not an
      offer, and an explanation of a link is not a link.** `check_heads.py`
      now counts `<link>` elements instead of substrings and fails on
      `MISSING` or `DUPLICATE` per needle - confirmed red in both directions,
      green after each restore.

80. **The top 8 rotated nothing a reader could see, and the missing half was
    the list rather than the eight.** `top8_window()` rotates the eight moments
    inside a list, and its own comment promised two consecutive days would
    never repeat the same page - but both live lists hold exactly eight
    featured entries, so the window branch (`len(featured) > 8`) could not
    fire, and "the show" was the newest `released` list every day, forever.
    Item 74's shape a second time: **a rotation that lives in a branch nothing
    enters is not a rotation**, and the fix is not a bigger pool - it is
    running the cycle on the axis that is guaranteed to have more than one
    member.
    - **`show_list()` rotates the show across the live lists**: ordered newest
      first, anchored on the newest `released`, one list per UTC day. The
      newest list takes the page on its release day and the lists cycle from
      there, so with two live lists the page never shows the same list two
      days running. Ties keep file order (stable sort); a file with no dates
      at all has no anchor, so the oldest file order holds and the rotation is
      silently still - the honest reading of a file that has not said when its
      lists came out. `pick_list` is deliberately unchanged: it is the
      curator's target (`t8_pool.py` edits the newest list, not whichever is
      up today) and it carries the empty live-set refusal.
    - **The day's show is recorded, because a date is not recomputable.**
      `record_top8_day()` appends `{date, list, items}` to
      `data/top8_history.json` before the pages render - the ledger's
      snapshot-before-feed ordering - from the same `top8_window()` call the
      page uses, so the record and the render cannot disagree. Identities are
      `t8_eid()` (id, then image, then show; never rank or name), same-day
      rebuilds are a no-op, and a mid-day pool change replaces the day's entry
      rather than writing a second one.
    - **`/top8/` carries the record under the list**, newest first, with
      consecutive days sharing a selection collapsed into one run - but only
      when the days are contiguous, so a skipped build is a gap in the record
      rather than something a run spans. Names resolve from the current data
      at render time.
    - **`top8_window()` measured its day in the machine's timezone**
      (`datetime.date.today()`) while `cur_slot`, `live_lists` and the new
      `show_list` all measure in UTC, so the inner eight could turn at a
      different moment than the show. Fixed to UTC in the same pass.
    - `curate.py` now prints `show_list()` (its line is labelled "on show"),
      the archive selects "not today's show" through `show_list()`, and the
      `/top8/` outro no longer says "Earlier top 8s" - the archived lists are
      not necessarily older, they are the ones this day did not land on.
81. **The eight registers take turns on `/taxonomy/`, the day is recorded, and
    the register section had been on the page twice - for two weeks - where no
    gate could see it.** The rotation runs on the definitions in file order (the
    axis is definitions rather than shelves; item 35), `register_of_day()` is
    deterministic from the UTC date, anchored on `REGISTER_EPOCH` (2026-10-19,
    the day it shipped), and `record_register_day()` appends the day's register
    through `data/register_history.json` before the page renders - the ledger's
    snapshot-before-feed ordering. One entry per date; a same-day rebuild is a
    no-op; a mid-day change replaces the day rather than writing a second one;
    names resolve at render time so renaming a register does not rewrite
    history. The spotlight above the list names the day's register and links to
    its definition and to a search for it; the record under the list is the
    sequence, and a register that is no longer defined is shown as such rather
    than dropped, because a day that happened is a fact even when the thing it
    showed is gone.
    - **The section had been duplicated since 2026-10-03 and no gate could see
      it.** The commit that added the third axis re-added the register and
      attachment sections above otherness while the originals were still in the
      template, so `/taxonomy/` carried both sections twice for two weeks -
      every card in them with a duplicated DOM id (the deployed page carried
      `tx-archive` twice). `link_audit` checks links, `check_css` checks
      selectors, `verify_taxonomy` checks the data; none of them reads a page
      for a section appearing twice. Found while adding the spotlight; the
      second pair is removed and the page now runs register -> attachment ->
      otherness -> reciprocity, once each.
    - **Membership is measured, and measuring it is why it is not printed.**
      Grepping placement reasons and entry prose for each register's name:
      `bond` 26 hits and 0 register assertions (all ordinary bond-talk - the
      site's own subject word); `encounter` 1 and 0; `contest` 4 of which 2 are
      real; `harm` 4 plausible and none explicit; `reciprocal-edge` and
      `archive` mostly real because their names are technical; `cog` 2 of 2. A
      member list built by word matching would file generic sentences under a
      register, which is how a register turns into confident noise - so the
      section links to a search for each register instead of printing a set,
      and the hub now reads `?q=` off the URL so "Everything that mentions it"
      lands in a filled search box.
    - **The stale counts went with it**, because shipping a definition that
      miscounts its own axis is this file's own defect family one field over:
      `taxonomy.json`'s `_axes.register` said "Six", the otherness `_note`
      named six registers, and the paragraph in "Why this site exists" still
      read "six members" and quoted the harm definition as "can carry" where
      the data says "can be in". All corrected in this pass.
    - `tools/test_register_rotation.py` covers the cycle and the wrap, dates
      before the epoch, the ledger's append/no-op/replace rules, the
      unknown-register rendering and the section as rendered, in the source
      tier beside `test_front_copy.py`.
82. **The front page puts one figure forward per UTC day, and the day is
    recorded, because the same contract has now been wrong three times in this
    repository and this one was built to it from the first line.** The roster
    lives in `data/parasocialite.json` - eight members with a `valence` and a
    two-sentence `breakdown` - and `parasocialite_of_day()` is deterministic
    from the UTC date and the roster's file order, anchored on
    `PARASOCIALITE_EPOCH` (2026-10-19, the day it shipped, because the roster
    has no release dates to anchor on the way the top-8 lists do).
    `record_parasocialite_day()` appends the day through
    `data/parasocialite_history.json` before the front page renders - the
    ledger's snapshot-before-feed ordering - from the same function the block
    renders from, so the record and the block cannot describe different
    figures. One entry per date; a same-day rebuild is a no-op; a mid-day
    change replaces the day rather than writing a second one; names resolve at
    render time so renaming a member does not rewrite history.
    - **Roster membership and the valence labels are editorial instruments and
      are the author's call.** The two entries the brief mandated
      (`nathan-fielder`, `the-beaver`) sit at the head of the cycle, and the
      other six were chosen to make the alternation mean something - and the
      one mechanical contract the test enforces is that `harmonious` sits on
      odd indices, so consecutive days never open on two bleak cases. **If the
      roster is ever reordered, that contract is what the test is for.**
    - **The block names the medium *family*, not the chip values.** The entry
      page prints "television scripted" and "television unscripted" as chips
      and that is right there; the front-page line reads "television", because
      the other spelling reads like a database. First segment, deduplicated,
      order kept.
    - **A roster entry whose encyclopedia record is gone degrades to the hub
      rather than printing a dead link with a name on it**, and a missing
      roster file degrades the page to no block rather than taking every other
      page down with it - the block is a spotlight, not the site's spine.
    - **The record shows a member no longer in the roster as "A figure no
      longer in the roster"** rather than dropping the day: a day that
      happened is a fact even when the thing it showed is gone, the same rule
      the register record follows for a register that is no longer defined.
    - `tools/test_parasocialite_rotation.py` covers the cycle and the wrap,
      dates before the epoch, the alternation contract, the append/no-op/
      replace rules, the unknown-member rendering and the block as rendered on
      the front page, in the source tier beside `test_register_rotation.py`.
      **Confirmed red by moving the epoch** - the failure names the anchor
      before anything writes, which is the property that matters for a test
      whose later steps append to a tracked file.
83. **The front page's research door was publishing a count seven behind the
    corpus, and the code comment above it said the count was computed.** Found
    by *looking at the front page* while shipping the parasocialite block: the
    live copy edition (2026-10-18) rendered "248 entries, every claim cited."
    while `data/encyclopedia.json` held 255. No gate had an opinion about it -
    `link_audit`, `check_css`, `md_leak` and `check_internal_leaks` all read
    the page and none of them reads a number in a sentence, which is the defect
    this file names twice already (items 43 and 77): **a number inside a
    paragraph is not obviously a claim, which is what makes it the dangerous
    kind.**
    - **The mechanism was that the count was typed, twice.** `build_front`'s
      comment claimed "`total` and `nent` stay computed ... a count read from
      the data cannot drift", and then nothing rendered either number: the door
      lines are prose from `data/front_copy.json`, both the live edition and
      the fallback carried literal counts, and the door's f-string interpolated
      nothing. A comment describing a property the code does not have is this
      file's own family one more time, and the tell was that the fallback's
      `f"48 so far."` had no interpolation to do.
    - **Fixed as tokens, not as a new number.** `door_stories` carries
      `{total}` and `door_encyclopedia` carries `{nent}`, substituted at render
      in `build_front()` from the same measured values the rest of the page
      uses - so the number cannot go stale again, which retyping it would only
      postpone.
    - **The 2026-10-18 edition is left exactly as it was**, typed 248 included:
      the sequence of what the front page actually said is the record, and the
      substitution is a no-op on an edition from before the tokens. The new
      edition (2026-10-19) carries the tokens, and `front_copy.py`'s docstring
      now says never to type a count into a slot.
    - The general form is worth keeping next to item 82 rather than under it: a
      rotation that ships on the front page is a reason to read the front page
      end to end,       because the page is older than the feature being added to it.
84. **Doubling the top-8 pools exposed a rotation the build did not have.**
    Batch one of the 365-per-list authoring added eight moments to each live
    list and interleaved them among the originals; both pools went 8 -> 16.
    Two defects were found by measuring the result rather than by reading the
    code, and both are this file's recurring shape: a sentence and a behaviour
    measured in two places.
    - **The window would not have rotated past eight per list.** `top8_window`
      started each day at `(day * 8) % n`. With one list of eight that *was*
      the list, so nothing could look wrong. With two live lists alternating
      daily, `(day * 8) % 16` is constant for each list - the parity of the
      days it appears on never changes - so every showing would have repeated
      the same eight forever, and the repetition would have looked like a
      plausible schedule. Fixed by advancing the window once per **showing**
      of the list: anchor on `released`, order live lists newest-first,
      `steps = (date - anchor).days`, `showing = (steps - index) // k`,
      `start = (showing * 8) % n`. With n=16 that is two windows per list;
      with n=365 and stride 8 the pool is walked completely because
      gcd(8, 365) = 1. Verified over a week: two distinct windows per list and
      all 16 moments reached. The script that proves this is not a gate
      because its assertions depend on pool size; check it when the pools
      change.
    - **"8 is the show, not the list."** The pool is every `featured` entry;
      the page shows eight at a time. That reading is what makes growth safe,
      and it is why the archive deliberately renders a former list's full pool
      (16 now) rather than a historical eight. Pagination on the archive
      becomes mechanical as the pools grow.
    - **The frame note's count is tokenised.** `t8_frame_note(L, entries,
      manifest)` carries `{blank}` and `{total}`, filled at render from the
      same absent-image test `t8_entry` uses, so the sentence cannot disagree
      with the plates. The typed "two have no photograph" was correct for the
      shipped eight and false the day the pool grew - item 83's defect in a
      different sentence. The archive call passes the full pool, so a list
      with 10 blanks of 16 says so.
    - **Batch one is interleaved, not appended.** Appending eight imageless
      moments behind eight photographed ones would have produced an all-plate
      day followed by an all-photo day per list. New moments sit among the
      originals at `floor(j * old_n / new_n)`. New entries carry no `image`,
      no `rank` and no `stage` key, so they default to `featured`.
    - **`tools/t8_grow.py` is the only writer for a batch.** It validates the
      required keys, refuses unknown keys, checks each `law` against
      `data/shop.json`, checks eids across every list and names within the
      target list, asserts the count, writes `indent=1, ensure_ascii=False`,
      and dry-runs unless `--apply`. Re-running a batch is refused by the
      duplicate checks, which is the idempotence that matters for a file this
      expensive to regenerate by hand.
    - **Law tags for batch one.** List one's eight are all instances of the
      shared law 6, so `t8_shared_law` still reads true. List two is mixed and
      keeps per-entry laws: Crocker 2, No-Prize 5, ELIZA 2, Vera Lynn 3,
      Amateur Hour 3, answering machine 5, fan magazine 2, Siri 6.
    - **The list-one title now under-promises its own subject.** "top 8
      parasocial moments in saturday morning cartoons of the 1990s" cannot
      honestly hold 365 moments; widening the theme is an editorial call
      queued for the batch report and needed before the pool outgrows the
      title further. The title stays until the author rules on it.
    - The 2026-10-18 record keeps the eight that were on show that day: the
      history is the record, and windows are never recomputed for past dates.
      The 2026-10-19 record was replaced in place by the build, as designed.

85. **The front page now presents the eight attachment categories as the
    front door to the whole corpus, and each one is a real page generated from
    the placements rather than a tile with nowhere to go.** The standing
    direction was to build the site "around the top 8 and the 8 ways
    foundationally". The top 8 was already foundational (items 74, 80, 84);
    the eight ways were a taxonomy page section. The hub was ten section tiles
    whose copy promised "one story from each" - a claim that was true when it
    was written and could not stay true, because the tiles were fed by a
    rotating window over stories while the categories are the site's actual
    classification. It also could not change when the corpus changed: a new
    entry per medium moved nothing on the front page.
    - **`/ways/<cat>/` is a new generated page type** (`build_way()` in
      `build_cards.py`, written for all eight categories in `main()` after the
      encyclopedia loads, because the pages resolve entry ids to titles). Each
      page carries the category's definition and link into the taxonomy, a
      rotating lead story drawn from the same ranked pool the top 8 uses, and
      one shelf per sub-category: every story placed there as a card, every
      entry placed there with the written reason its placement record gives,
      and the sub-category's own def/test/not. **The placement reason is the
      argument, so it is printed rather than kept in a commit.** The eight
      pages link each other; the taxonomy page links each way back.
    - **A category with no story says so, in both places a reader looks.**
      `divine` holds 15 entries and 0 stories. Its front-page tile shows the
      category blurb and note with "15 entries →" instead of a headline and
      "stories →", and its ways page shows the honest line "No story is filed
      on this way yet. The entries below are what the way holds." The
      alternative - keeping a story tile by faking a lead, or hiding the gap -
      is the same defect family as `kind: exact` and five of ten hub decks
      measuring under WCAG AA: **a tile that promises a story it does not
      have.** The kicker changed from "one story from each" to "Eight ways it
      shows up · one way in to each", which is true of all eight.
    - **`verify_ways.py` holds it and is in the post tier.** It reads the
      deployed tree and asserts: eight `.hub` tiles each linking its way;
      every placed story and entry appears on its category's page (from
      `story_placements.json` and `taxonomy_placements.json`, so a placement
      that moves must move on the page); every page links its definition and
      the other seven; a storyless category shows the empty state and its tile
      counts entries rather than stories; and the sitemap lists all eight
      URLs. **Confirmed red** by mutating a copy of `dist/index.html` (tile
      repointed, kicker changed) and deleting a story link from a ways page -
      it named all three faults, then went green on rebuild.
    - **The tile/deck material is read from `data/`, never rewritten here:**
      `taxonomy.json` supplies the copy and the sign; `story_placements.json`
      supplies story assignment and the reason; `taxonomy_placements.json`
      supplies entry assignment and the reason. A category that gains its
      first story changes the tile from entries to stories automatically,
      which is the property that was missing from the section-tile hub.
    - **A rotation test caught an unrequested move.** The parasocialite
      spotlight was moved below the top 8 in the same pass, and
      `test_parasocialite_rotation.py` - written for item 82 - failed on
      exactly that: the block's position is part of the feature. Restored
      above the top 8 rather than weakening the test. **The order is masthead,
      spotlight, top 8, eight ways, deeper.**
    - **The lead poster was slicing headlines at 44 characters and cutting
      mid-word** - "An economics think tank argues parasocial re" - and the
      defect was found by screenshotting the new page, not by a gate. The
      slice was not new: `build_section()` has done it since the section
      fronts shipped, so ten deployed pages were cutting their lead headline
      the same way. The cut has to land where a person would have stopped
      (third time this file says it), so both now carry the full headline
      under `-webkit-line-clamp:3`, which hides whole lines and never a
      fragment. **The new page inherited the defect from the pattern it was
      copied from, which is the argument for copying patterns rather than
      describing them - and for looking at what the pattern renders.**
    - `probe_hub_contrast.py` still measures the tiles and now refuses unless
      it finds eight, and `probe_cards.py`'s docstring matches. The `hubs`
      grid is two columns at desktop and one at phone width; eight tiles are
      four rows.
    - **Still owed, and it is editorial:** the taxonomy's ten-section mapping
      (`/taxonomy/` publishes it) now has a second front door competing with
      it; whether the section fronts stay equally prominent in the nav is the
      author's call, not a build's. Nothing was removed to make the eight ways
      fit.

86. **The top-8 pools took their second grown batch, and list two now runs the
    manufactured reply from 1894 to 2011 with the thin decades filled.** Eight
    new moments interleaved among the sixteen already there, pool 16 -> 24,
    all near-side replies because that is the list's frame. The placement was
    chosen from item 19's chronological census (1900s 4 entries, 1910s 2,
    1920s 3, 1940s 6), so the batch is weighted 1894-1950 and every entry
    carries its own law tag.
    - **The eight**: Beatrice Fairfax (1898-1920, law 2); the US Post Office
      answering as Santa (1894-1912, law 3); the secretary to Sherlock Holmes
      (1932-2005, law 6); Bess Houdini's séances (1926-1936, law 4); Patience
      Worth (1913-1937, law 6); the autopen (1937-1942, law 5); the Royal
      Historian of Oz (1919-1942, law 1); Mickey Mouse's mailroom (1933,
      law 2). Prose in `data/features.json`; per-claim limits and rejected
      claims in the 2026-10-20 `RESEARCH-NOTES.md` section.
    - **The batch json is an input, not an artefact.** `tools/t8_grow.py` is
      the only writer; the file lives in the temp directory because the repo
      carries the writer and the data rather than the intermediate. It
      validates required keys (`name, show, what, why, law`), rejects unknown
      keys and any stage other than `featured`, checks laws against
      `shop.json`, enforces unique names within the list and unique eids (id,
      then image, then show) across every list, asserts the pool size before
      and after, interleaves at `floor(j * old_n / new_n)`, writes
      `indent=1, ensure_ascii=False`, and dry-runs unless `--apply`. Re-running
      is refused by the duplicate checks.
    - **The frame note's count is real, and list two correctly has none.**
      `t8_frame_note()` carries `{blank}` and `{total}` filled at render, so
      list one's sentence counts imageless entries in the set actually shown
      (4 of the 8 on the build day). List two has no photographs at all, so
      its note is absent by data rather than by omission.
    - **The rotation was checked on the three showings list two will land on**
      rather than inferred: 2026-10-20 carries 2 of the new eight, 2026-10-22
      carries 3, 2026-10-24 carries the remaining 3 - three distinct windows
      over the 24-moment pool, and all eight appear across the cycle. Both
      signatures were read from the source rather than remembered:
      `top8_window(feat, day)` takes the day as a string and returns the list
      object whose `entries` is the eight; `show_list(feat, today)` returns the
      list object, not a tuple.
    - **Rejected or deferred, recorded so batch three does not rediscover
      them**: Clara Bow's 33,727 April 1928 letters answered by three
      secretaries (deferred - same shape as the autopen at this distance, and
      the natural first candidate for a human-labour cluster); Dorothy Dix
      (shape duplicate of Fairfax); Little Orphan Annie's decoder badge
      (duplicates the Whiz Comics shape); the Tom Mix club (one fan page,
      nothing corroborating); "Yes, Virginia" 1897 (outside the window, and
      the reply came openly from an editor rather than from a manufactured far
      end).
    - `gates.py --all` green across all three tiers after the batch, including
      `verify_ways`, `md_leak`, `citation_audit`, `card_audit` and
      `image_audit`; the post tier rebuilt `dist/`. No history entry was
      rewritten - the batch changed a pool, not a past day's show.
    - **Still owed, unchanged**: list one's title says "Saturday morning
      cartoons of the 1990s" and cannot hold a growing pool; the retitle is the
      author's call and is now overdue after batch three. Batch three has since
      landed; see item 87.

87. **The top-8 pools took their third grown batch, and list one now runs from
    a comic-book frame to a basement client - while the list's own title became
    the open editorial debt.** Eight new moments interleaved among the sixteen
    already there, pool 16 -> 24, all law 6. The batch is all 1990s cartoons,
    but it deliberately includes weekday, PBS and afternoon shows as well as
    Saturday-morning ones, because the existing sixteen already do the same.
    - **The eight**: Batman: The Animated Series, "The client in the basement"
      (1992); Where on Earth Is Carmen Sandiego?, "The player at the keyboard"
      (1994); ReBoot, "The User outside the Net" (1994); The Magic School Bus,
      "The producer takes your call" (1994); KaBlam!, "The hosts in the comic
      book" (1996); Nick in the Afternoon, "The popsicle stick who read your
      mail" (1995); Tiny Toon Adventures, "The fan letter with a trap in it"
      (1991); Freakazoid!, "The fan who had no life" (1995). Prose in
      `data/features.json`; per-claim limits and rejected candidates in the
      2026-10-20 `RESEARCH-NOTES.md` section.
    - **Animaniacs was dropped after being verified, because the show was
      already on the list.** The existing rank-8 entry "The rabbit in the hat"
      is the "Good night, everybody!" moment, and its `show` was wrong: it said
      `Animaniacs, 1990`, while the series premiered 13 September 1993. The
      field is now `Animaniacs, 1993`. The eid is unchanged because the entry
      has an image (`t8-8-animaniacs`), so the day record still resolves.
      **This is a duplicate the batch writer cannot see: not a repeated name or
      eid, but a repeated show.** The writer checks names within the list and
      eids across all lists; it does not stop two moments from the same series.
      Check the show string, not only the eid.
    - **The window spread was checked on the three list-one showings rather
      than inferred**: 2026-10-21 carries the Magic School Bus and KaBlam!
      moments, 2026-10-23 carries Stick Stickly, Tiny Toons and Freakazoid,
      2026-10-25 carries Batman, Carmen Sandiego and ReBoot - 2/3/3, three
      distinct windows, all eight across the cycle.
    - **Rejected or deferred, recorded so batch four does not rediscover them**:
      Space Ghost Coast to Coast (deferred - strong, but adult late-night and a
      candidate for a future late-night list); Pepper Ann (the opening
      object-to-camera gesture is a sight gag, not a reply); Sabrina: The
      Animated Series (no evidence found for the remembered "Sabrina's Secrets"
      segment); Beavis and Butt-Head and The Simpsons' "Poochie"
      (adult/prime-time, off register); Batman's "Legends of the Dark Knight"
      (a second Batman in one batch).
    - **The title is now overdue, and it was not changed by a script.** List
      one reads "Top 8 parasocial moments in Saturday morning cartoons of the
      1990s"; at 24 moments it still holds as a frame, but it cannot carry the
      365-moment pool the project is growing toward, and this batch includes
      weekday, PBS and afternoon entries. Item 86 said the retitle was needed
      before ~batch 3; batch 3 has landed, so the honest state is that the
      title is the next editorial decision, not that the batch was blocked on
      it.
    - `gates.py --all` green across all three tiers after the batch; dist
      rebuilt. The deploy zip is regenerated separately and its tree sha is the
      state to publish, not the previous one.

88. **The top-8 pools took their fourth grown batch, and list two now carries
    the manufactured reply from a silent-film dog to a chatbot built out of a
    dead woman's texts.** Eight new moments interleaved among the twenty-four
    already there, pool 24 -> 32. Each entry carries its own law tag; the
    list-level law stays `None`. The per-claim limits, rejected claims and
    source disagreements are in the 2026-10-20 `RESEARCH-NOTES.md` section.
    - **The eight**: Rin Tin Tin, "The paw that signed the fan mail" (1922,
      law 2); Clara Bow, "The three secretaries who answered as Clara Bow"
      (1928, law 2); Disneyland, "The smile from inside the costume" (1955,
      law 6); The Psychic Readers Network, "The queue behind Miss Cleo" (1997,
      law 5); Animal Crossing, "The villager who read your letter" (2001,
      law 6); Kizuna AI, "The performer inside the avatar" (2016, law 3);
      Lil Miquela, "The influencer who was written by a team" (2016, law 3);
      Project December, "The girlfriend who came back as text" (2020, law 4).
    - **Three claims were corrected during review, not accepted from the
      batch draft.** Rin Tin Tin's "thousands of letters a week" became "fan
      letters arrived by the thousands" because neither the New Yorker profile
      nor Wikipedia gives a weekly rate. Kizuna AI's "production crew stayed
      anonymous" became the sourced fact that Nozomi Kasuga's voice role was not
      disclosed until 2020; the crew was known. Lil Miquela's `why` put the team
      at the far end when the team is the near side - the figure who appears to
      send the reply is the far end.
    - **The source boundaries that matter for future batches.** Clara Bow is
      33,727 items in April 1928 with three full-time secretaries, not the
      encyclopedia's separate 45,000 January 1929 figure; one secondary says
      May and is recorded rather than followed. Disney's entry claims only a
      non-speaking costumed performer who poses for photographs; modern Disney
      characters sign autographs, so "no hugs/no autographs" is not a claim the
      site can make. Miss Cleo's show year is the network campaign date, not a
      claim that Harris was on screen in 1997; the entry says "late 1990s" and
      keeps the script allegation at "lawsuits later alleged" and "some."
      Project December was a $5 account, the first chat was 24 September 2020,
      and 3 March 2021 was a later chat the day after Barbeau's 34th birthday;
      the fiancee framing began after Pereira's death and is not a formal
      engagement. Animal Crossing's reply is a parser scoring punctuation,
      capitals, trigrams and word lengths, not comprehension. Lil Miquela was
      created by McFedries and DeCou at Brud and maintained by a nine-person
      team.
    - **The window spread was checked on all four list-two showings, not
      inferred**: 2026-10-18 carries Rin Tin Tin and Clara Bow; 2026-10-20
      carries Disneyland and Miss Cleo; 2026-10-22 carries Animal Crossing and
      Kizuna AI; 2026-10-24 carries Lil Miquela and Project December. Each has
      exactly two of the new eight, and all eight appear across the cycle. List
      one remains at 24. `top8_history.json` now records 2026-10-20 alongside
      2026-10-19.
    - **Rejected or deferred, recorded so batch five does not rediscover
      them**: Shirley Temple 1936 (mail volume, but the secretary shape
      duplicates Clara Bow); Replika 2017; deepfake grief 2024; Aimee Semple
      McPherson 1924; Cabbage Patch Kids/American Girl/Furby; Kermit/Garfield;
      Dionne Warwick. Candidates noted but not researched, not rejected:
      Neopets (1999), SmarterChild (2001), Clippy (1997), The Sims (2000).
      Disney's Daveland source failed twice with transport errors and was not
      used; the modern-autograph boundary was checked against Disney's own
      character page.
    - `gates.py --all` green across all three tiers after the batch and after
      the review corrections; `dist/` rebuilt. The deploy zip is
      `C:\Users\paras\Desktop\parasocialize-SITE.zip`, 774 files, 15.47 MB,
      tree sha **235dcf30c4e2cf49**, index at root, no nested `dist/`, archive
      integrity ok. **It has not been uploaded yet.**
    - **Still owed, unchanged**: list one's title says "Saturday morning
      cartoons of the 1990s" and cannot hold a growing pool; the retitle is the
      author's call and is now overdue after batch four. The list-two pool is
      32 entries, all-no-photo, with its frame note absent by data.

89. **The front-page top 8 lost its 52px art tiles.** They were type-only
    abbreviations of the show name, not sourced images, and on an all-no-photo
    list they read as icons without context. The strip is now text-only: rank,
    title and show, four across on desktop, two at 1080px and one at 760px.
    `/top8/` keeps its large `.t8-plate` cards, where the show name has room and
    the no-photo state is explained per entry. Removed `_plate_word()` and the
    `.t8col-art`, `.t8col-plate` and `.t8col-photo` styles. Checked the 1440px
    desktop and 390px phone renders; `gates.py --all` green across all three
    tiers. New deploy zip: `C:\Users\paras\Desktop\parasocialize-SITE.zip`,
    774 files, 15.47 MB, tree sha **81cee41dcc579913**, index at root, no nested
    `dist/`, integrity ok. **Not uploaded yet.**

90. **The top-8 page lost its entry plates, and the cartoon list lost its hero
    photograph.** On `/top8/` and `/top8/archive/`, an entry with no sourced
    photograph is now text-only: rank, title, show and law. The 300px plate was
    a show-name icon beside a title that already said the same thing, and on
    the all-no-photo Part Two it repeated eight times. Removed the plate branch
    from `t8_entry` and the `.t8-plate*` styles; the six sourced photographs in
    the cartoon archive remain. Removed Part One's `image` (a 238x240
    woman-beside-TV photograph shown more than 1000px wide) and removed the
    `stand` and `.t8-hero-fig` hero from both list renderers, so no list page
    carries a hero. The frame note now says 18 of 24 carry no picture and calls
    the absence part of the record. Checked the 1440px `/top8/` and archive
    renders; `gates.py --all` green. New deploy zip:
    `C:\Users\paras\Desktop\parasocialize-SITE.zip`, 774 files, 15.46 MB, tree
    sha **205a8444ad08940b**, index at root, no nested `dist/`, integrity ok.
    **Not uploaded yet.**

91. **The front page's top 8 is now a live card grid that links into the
    moment it names, and the homepage's blocks have explicit boundaries.** The
    section is still `top8_window()`, so the eight are whichever the day's show
    carries, but each card now has a stable fragment on `/top8/`:
    `t8_anchor()` builds `t8-{list slug}-{entry name/show}`, never the raw rank,
    and both `build_top8()` and the archive refuse duplicates. Eight cards
    carry rank, show, title, hook and `Read this entry`; the title and standfirst
    come from the list's `home_title`/`home_hook`, the kicker from `kicker` and
    the raw list's year span, the footer from the exact
    `View Full Top 8 Analysis & Archive History →` CTA, the archive link only
    when a second live list exists, and the count from the raw list rather than
    the eight-entry window.
    - **The hook is bounded by pixels, not words.** `deck(..., 16)` kept 46-word
      first sentences whole, so `t8_hook()` now prefers the first sentence at
      <=24 words and <=118 characters, otherwise the shortest later sentence in
      that budget, otherwise a clause ending before the limit. The 118 is what
      fits two lines at the card's measure; a 22-word/150-character ELIZA
      sentence was the proof. On phone the clamp is three lines, because two
      clipped the Peter Pan hook at `Do...` while leaving every other card
      two-line on desktop.
    - **The section is bounded by two bands rather than ending at the grid.**
      `hub-band` holds `One way in to each` / `Eight ways it shows up.` and the
      taxonomy link; `ledger-band` carries the mint edge, `The standard, and the
      tally.`, the ledger/citations actions, and the boundary copy. The PSOTD
      record gap was closed by removing the later `.psotd-sec{padding-top:0}`
      override. Its undefined `var(--ink)` was replaced **only there** with
      `var(--bg2)`/`var(--paper)`; no global `--ink` was invented.
    - **The nav breakpoint moved from 1024 to 1160px.** With `Works` after
      `History` and the longer labels, the canonical row needs 981px; at 1100px
      it wrapped into a 74px row inside the 64px bar. `probe_nav --check` is
      green at 1180px row and 1100px overlay. Item 47's 1024px value is
      superseded; the requirement is the 64px bar and the measured row.
    - `test_front_copy.py` now asserts the generated page carries the live
      title, kicker, hook, eight cards with sequential ranks and anchors, a
      matching anchor target on `/top8/`, the exact CTA, and the raw-list count.
      `gates.py --all` is green across post, visual and source; screenshots were
      checked at 1440, 1180 and 390, including the lower bands. New deploy zip:
      `C:\Users\paras\Desktop\parasocialize-SITE.zip`, 774 files, 15.48 MB,
      tree sha **e052cb01d7b69fc8**, index at root, no nested `dist/`, integrity
      ok. **Not uploaded yet.**
    - **Still owed, unchanged**: list one's title says "Saturday morning
      cartoons of the 1990s" and cannot hold a growing pool; the retitle is the
      author's call. List two remains 32 entries with no photographs, so its
      frame note is absent by data.

92. **The Open Ledger band left the reader flow, the support route got its name
    back, and the footer became four groups instead of a row of links.** The
    front page had a full-width ledger band between the top 8 and the ways; it is
    gone from `build_front` and its CSS, including the 760px rules, is gone too.
    The standard is still published at `/ledger/` and linked from "The project"
    in the footer, so the page states the standard without stopping the reader
    to pitch it.
    - **Nav labels now match what the pages sell.** `/membership/` was labelled
      Support and the Ko-fi link was Coffee; the membership page is a $6/month
      tier titled "Renewals", so Support on it was the wrong word. Membership is
      now `.cta-quiet` and Support is the orange `.cta` pointing at Ko-fi with
      `aria-label="Support the archive on Ko-fi"`.
    - **Footer is brand plus four columns**: Read, Look up, The project, Follow,
      with About -> credits, Contact -> tip, Archive -> top8/archive, Ledger,
      Membership, and Support the archive/RSS/Signal/iYi in Follow. The old
      `.foot-kofi` button is removed. `.foot-grid` is
      `minmax(250px,1.1fr) minmax(0,2.9fr)`; `.foot-nav` is four equal columns;
      1040px stacks the brand and keeps four columns, 760px uses two.
    - **The generated and hand-written footers share the shape.**
      `build_taxonomy`'s custom footer was changed to the same four groups, and
      the seven hand-written pages carry `foot-grid foot-mini` so they do not
      inherit the tall grid. `desk/` uses the mini footer too.
    - **The 390px support link is one line.** The first pass tightened
      `.foot-support` but `.foot-col a` outranked it, so the arrow still wrapped;
      `.foot-col a.foot-support{letter-spacing:.09em}` fixes it, and the arrow
      uses a non-breaking space so it cannot be orphaned. Checked at 1440, 1180,
      980 and 390 in a fresh Chrome profile.
    - `test_front_copy.py` now asserts no `ledger-band`, no Coffee/Buy me a
      coffee, exact Membership/Support nav markup, About/Contact/Archive/Ledger/
      RSS/Support footer links, and four `.foot-col` groups in the generated
      page. `probe_nav --check` is green at 1180px; the row needs 1013px against
      1075px available, so the 1160px breakpoint is unchanged.
    - `gates.py --all` green across post, visual and source; `build_deploy` 362
      pages / 774 files, CSS hash `styles.de6648da76.css`; `make_zip`
      **2e24ad07d39dab3e**, 774 files, 15.50 MB, index at root, no nested
      `dist/`, integrity ok. **Not uploaded yet.**

93. **The deploy command had no build step, so a correct rotation shipped a
    stale day.** For four days the front page's date-seeded Top 8, register and
    parasocialite stayed on 21 October while every gate was green. The rotation
    was not the defect: `build_cards.py` computes all three from the UTC date at
    build time, and the three history files were correct up to the last build.
    The defect was `build_deploy.py`, whose entire job was to copy the existing
    HTML into `dist/`. Running it packaged whatever day the tree was last
    generated, and every check passed because the stale tree was internally
    consistent. **A packaging step that only copies cannot freshen a
    date-seeded page, and no link check can see the difference.**
    - **Fixed at the command people actually run.** `build_deploy.py` now runs
      `build_cards.py` and then `plate.py` before it touches `dist/`, so
      `python tools\build_deploy.py` is the one fresh-deploy command. The order
      is enforced where the packaging happens rather than remembered by the
      operator. `--no-build` packages the pages already on disk and is what
      `gates.py` passes, because the post tier has just run the same two
      builders and must not run them twice. `--check-only` deliberately never
      builds: a check that rebuilt would be checking its own work.
    - **The stale history was the tell, and it is now the proof.** Before the
      fix, `data/top8_history.json`, `data/register_history.json` and
      `data/parasocialite_history.json` all stopped at **2026-10-21**. After one
      `python tools\build_deploy.py`: each carries **2026-10-25** exactly once,
      Top 8 is on the cartoons list with a window different from 21 October's,
      the register is `reciprocal-edge` (was `cog`), and the parasocialite is
      The Shadow (was The Beaver). The homepage reads **Part One · 1990–1999**
      with **Top 8: 90s Saturday Morning Cartoons**, not the manufactured-reply
      list that was live.
    - **Verification:** `build_deploy` exit 0, **362 pages / 752 files /
      20.7 MB**, every local link resolving; `gates.py --all` exit 0 across
      post, visual and source; a final `--no-build` assembly followed by the
      post and visual tiers also exit 0, so the package was checked in the tree
      it was built from rather than an earlier one. `make_zip` wrote
      `C:\Users\paras\Desktop\parasocialize-SITE.zip`, **752 files, 15.16 MB,
      tree sha `ea63e6add08bd6d6`**, `index.html` at root, no nested `dist/`,
      archive integrity ok. **Not uploaded yet.**

94. **The automation was a cron file pointed at a repository that does not
    exist, and the daily record had nine holes nobody could see.** Measured on
    2026-10-31 rather than inferred: all three histories ran 2026-10-19, 20, 21
    then jumped to 25 and stopped; **22, 23, 24 and 26-31 had no record at all**
    (nine days, not the six the last session's note assumed). The front page was
    still a valid page for 25 October, every gate was green, and nothing in the
    project asked whether yesterday existed. Three separate deficiencies, one
    shape: **a process whose failure produces a valid artefact.**
    - **The scheduler had never run, anywhere.** `origin` pointed at
      `https://github.com/YOUR-USER/parasocialize.git`, a placeholder. The real
      repository `Parasocialite/parasocialize` exists and `gh repo view` reports
      `"isEmpty": true`, `defaultBranchRef.name: ""`, and
      `actions/workflows` returns `total_count: 0`. So no cron, no workflow, no
      runner - the YAML was decoration, and the "twice-daily" comment on it was
      a claim about a machine that had never been switched on. The sweeper's
      last run was **2026-09-29, 32 days earlier**, which is the same defect on
      the content side. **A cron on a repository nobody pushed to is not
      automation.**
    - **The archive could not distinguish "nobody built" from "nothing
      happened".** `top8/record/` said "a gap stays a gap", which was honest and
      also the whole problem: it had no way to say how many gaps, or which days,
      and no gate read the sequence. `data/daily.json` now records the last run;
      `tools/archive.py --check` fails on any missing day and is wired into the
      source tier, so the next gap is red before it is ten days old.

    **The fixes, all three of them commands rather than intentions:**
    - **`tools/daily.py`** is the loop: reconcile the archive, measure the plan,
      rebuild, draw plates, package, run the post and source tiers, write the run
      record, package again (the record is under `data/`, and the freshness gate
      reads `data/`), prove the deployed tree carries today's rotation, then zip.
      `--check` is the same contract with no writes and is the first thing a
      returning agent or a scheduler should run. It aborts on the first non-zero
      exit; nothing is piped or swallowed.
    - **`tools/archive.py`** closes a gap only when it is *provable*: the inputs
      behind that day must have been frozen before the day began. The evidence
      here is exact - `features.json` was last written **21 October**,
      `taxonomy.json` and `parasocialite.json` on **19 October**, all before the
      first missed day. Eight days (22-30 October) were recomputed and written
      with `reconstructed: true`, `reconstructed_on: 2026-10-31` and an
      `inputs_sha256`; today (31 October) was left for the live build. Existing
      records are compared before and after every write and the tool asserts
      they did not move. Every record surface now prints a **rebuilt** tag with
      the date and the reason, because an observed day and a recomputation of
      what would have happened are different claims and a reader can tell them
      apart. If an input had been edited on or after a missed day, the tool
      refuses and the gap stays visible. The proof reads the **last commit
      date** for a clean tracked file and falls back to mtime only when the
      working tree is dirty, because git does not preserve mtimes: a fresh CI
      checkout stamps every file at checkout time, which would make every gap
      unprovable exactly when the scheduler needs the repair path.
    - **`tools/plan_next.py`** replaces the memory-based batch with a measured
      work order. It counts media (days at two entries per release), the
      catch-all share, categories with no story, thin decades, top-8 window
      arithmetic (`n // gcd(8, n)`), sweeper age and queue depth, and writes
      `data/plan.json`. `/desk/` renders the top six with the exact command. It
      authors nothing: `divine` is reported as 15 entries and **0 stories**, and
      left that way. The first measured order is: the sweeper (32 days asleep),
      `divine` (no story), `stage` (2.5 days), `comics` and `visual_art` (3.5),
      then the catch-all share (**91 of 255, 36%**).
    - **The workflows now match the commands.** `curate-twice-daily.yml` calls
      `daily.py`, uploads `dist/` and the zip as an artifact, and commits only
      after the gates pass. `refresh-hourly.yml` lost the `|| true` on
      `link_audit` - a gate that is allowed to fail is a gate that is off - and
      now also runs `archive.py --check`. The local fallback,
      `tools/install_daily_task.ps1`, is a dry run by default and registers a
      Windows task only with `-Register`; it was not registered here.
    - **`origin` was corrected** to
      `https://github.com/Parasocialite/parasocialize.git` and, with the
      author's approval, the local history was committed and pushed. The
      repository now has `main`, both workflows are active, and a dispatched
      `daily` run completed green (run **41203448336**, 2m00s) with **no
      follow-up commit**: the Linux build matched the committed tree byte for
      byte. Cloudflare upload is still manual and has not happened.
    - **The first CI runs were the audit the local machine could not perform,
      and every failure was a local-only assumption.**
      - `build_deploy.optimise()` imports Pillow and the runner had none.
        `requirements.txt` names it and the workflow installs it.
      - `verify_taxonomy.py` still carried a hardcoded
        `C:\Users\...\parasocialize` root - item 53's landmine, surviving in
        the source tier. On Linux it read nothing and failed. **Fourteen tools**
        with the same literal were converted to
        `pathlib.Path(__file__).resolve().parent.parent`; every gate on the
        daily path now computes its root.
      - `gates.py` captured a red check's stdout and threw it away, so the log
        said `RED verify_taxonomy` and nothing else. It now prints the failed
        check's output. **A gate that cannot say why it failed costs a round
        trip per failure.**
      - `test_front_copy.py` wrote CRLF unconditionally, invisible on Windows
        and a 130-line rewrite of `data/front_copy.json` on Linux, which the
        daily job then committed. It now preserves the fixture's newline style
        and asserts the restored bytes exactly.
      - The desk rendered the sweep age in minutes ("5m ago"), so every rebuild
        produced a different page and the daily job committed a no-op. It now
        reads by UTC day ("today", "yesterday", "Nd ago") with the exact
        timestamp on the card's title attribute.
      - `requirements.txt` is a `.txt`, so `build_deploy` copied it into the
        deploy root beside `robots.txt`. Excluded by name.
    - **The counter's first live run found the last two.** Its commit step
      staged only `data radar radar.xml aisle shelf`; `aisle` no longer exists,
      and the `|| true` hid the pathspec error. More importantly, the pages
      `build_cards.py` had just rewritten were left unstaged, so the new
      `git pull --rebase` refused with "You have unstaged changes" and the job
      died before pushing anything. Both writers now share a `repo-write`
      concurrency group, stage the whole tree, and **a failed push fails the
      job** instead of printing an annotation over a green run. The sweep ran
      **2026-10-31T13:09Z**: 12 candidates, 11 fresh, 11 filed raw (no model
      key), queue 60. The plan's top action then moved from `the sweeper` to
      `divine` - 15 entries and still no story - which is the planner doing the
      one thing a hand-written queue could not: noticing that the pipeline is
      awake and the next gap is editorial.
    - **The pattern:** a loop that has only ever run on the machine that wrote
      it is a loop with an untested half. None of those defects was visible to
      the local gates, and each would have stopped the first scheduled run -
      which is exactly the failure the scheduler was supposed to prevent.

    **Verification.** `python tools\daily.py` exit 0. All three histories now
    span **2026-10-19 -> 2026-10-31**, 13 days each, **8 rebuilt and today
    observed**; `archive.py --check` green; `gates.py --source`, `--post` and
    `--visual` all green; `plan_next.py --check` green; the GitHub `daily` run
    **41203448336** green in 2m00s with its artifact uploaded and **no new
    commit**, the `counter` run **41204273465** green after the commit-step
    fix, and a final `daily` dispatch (**41204799164**) also produced **no
    commit** - the loop now rebuilds to the same bytes. Today's show is the
    cartoons list, the register is **Encounter**, the parasocialite is **Queen
    for a Day**. `dist/` is 752 files, and `make_zip` wrote
    `C:\Users\paras\Desktop\parasocialize-SITE.zip`, **752 files, 15.17 MB,
    tree sha `6eb8187b8ec3473f`**, index at root, no nested `dist/`, integrity
    ok. **Not uploaded.**
    - **The general form.** A green gate is a statement about the artefact it
      read, and none of these gates read the *calendar*. The date-seeded pages
      were valid, the links resolved and the sources reconciled while the site
      was nine days old and its schedules had never executed. **The missing
      check was not "is this page correct" but "is this page today's"** - which
      is now asserted in four places (today's record in each history, the plan's
      date, the deployed date string and the eight anchors) rather than trusted.

95. **The three daily features were rotating, not daily. The site now generates an edition every UTC day, and the figure is a figure.** The user uploaded the site and saw three things that were true and not coherent: Queen for a Day, a radio format rather than a person or a character, as "parasocialite of the day"; the Saturday-morning-cartoons list back on the front page after being the first list; and eight "ways" pages whose lead was a twice-daily story rotation, not a daily record. All three were doing what the code said. The code was not doing what the feature names promised.
    - **The figure bank replaces the fixed roster.** `data/parasocialite.json`
      now holds **49 members: 48 selectable (27 real, 21 fictional) and one
      non-selectable historical format**. The format is `queen-for-a-day`, kept
      only so the committed record still resolves her name; the editor can
      never choose her. A selectable member carries `kind: real|fictional`, a
      real encyclopedia `entry`, wire `aliases`, a `context` list for ambiguous
      names (`prince`, `harvey`) and tags used for theme matching. The old
      eight-day alternation contract is retired; the page now prints
      **Real figure** or **Fictional figure**, and `test_parasocialite_rotation`
      refuses a selectable member that is not one of the two.
    - **The top 8 is generated, one list per day.** `data/top8_themes.json` is
      25 hand-written themes (dead stars, fan mail, AI companions, screen
      characters, brands, music, sport, games, radio, comics, stage, visual art,
      ancient bonds, religion, fandom, streaming, reality TV, literature,
      letters to nobody, the reply, the audience, childhood, merchandise,
      grief archive, power). Each theme supplies the framing, the law and a
      selector over medium, attachment category, section, keywords or year.
      `tools/editor.py` chooses a theme from today's wires, or the least
      recently used one; it excludes a theme for 21 days. The eight entries are
      existing encyclopedia entries, exclude anything used in the last 14 days,
      and exclude thesis/term/study entries so the list is applications rather
      than the site's own vocabulary. Every entry links to its page; the prose
      is the entry's own summary and significance, cleaned and clipped.
    - **The show is today's list, never a former one.** `show_list()` now
      returns only the list whose `released` date is today, and refuses to build
      if there is no such list. The cartoons list and the manufactured-replies
      list remain in `data/features.json` and render at `/top8/archive/`; they
      are never the show again. `top8_history` records the daily slug, theme and
      the eight entry ids, so `/top8/record/` resolves the names and shows the
      sequence.
    - **The wires are real.** The editor reads Google News RSS, ten queries over
      the last 3-14 days (`parasocial`, `celebrity fandom`, `AI companion`,
      `celebrity death`, `K-pop fandom`, `reality TV fandom`, `virtual
      influencer`, `fan mail`, `sports fans`, `theatre fandom`), and falls back
      to `data/queue.json` when the fetch fails. The figure is chosen by a
      direct alias match when a headline names them; otherwise the page says
      which wire set the theme, with the publisher link. The top 8 carries up to
      three current wire links under "From today's wires". Nothing is quoted as
      a fact from a headline; the headline is a link and the claim stays on the
      linked entry.
    - **Each way has a dated daily pick.** `tools/editor.py` chooses one story
      or entry per attachment category from the placements, preferring a news
      overlap and excluding picks used in the last seven days; it writes
      `data/ways_history.json`. Every `/ways/<cat>/` page now opens with
      "Today on this way" plus the pick's placement reason and the previous five
      days. The eight picks are unique, filed on their own shelf, and checked by
      `editor.py --check`.
    - **The daily loop carries the agent.** `tools/daily.py` runs
      `editor.py` after the plan and before `build_cards.py`; `editor.py` is
      idempotent for a date, so the noon run keeps the morning's edition.
      `gates.py` source tier now runs `editor --check` and
      `test_editor_rotation`, which proves tomorrow's theme, figure and eight
      are not today's. `tools/probe_hub_contrast.py` needed a taller capture
      because the figure's "why today" line pushed the last two tiles below the
      2600px frame; it now refuses to report a tile outside the image instead of
      turning absence into `nan`.
    - **A gap that cannot be reconstructed is declared, not invented.**
      `data/archive_gaps.json` is the declaration file. The register is still
      deterministic and can be rebuilt when its inputs predate the missed day;
      the daily top 8 and the figure depend on that day's wires and theme, so a
      later build cannot know what the page would have shown. `archive.py
      --reconcile` declares those days, `--check` accepts them as visible gaps,
      and the daily loop no longer stops forever on a hole it cannot fill.
    - **The editorial boundary held.** No new fact, citation, date or quotation
      was written. The top 8's what/why are the entries' own text; the figure's
      breakdown is the entry's summary (or the hand-written line from the old
      roster where it was better); the theme framing is hand-written in
      `data/top8_themes.json`; the only generated sentences are the date, the
      theme's argument and the wire attribution. That is the line this site
      exists to keep, and a daily cadence is not a reason to cross it.

    **The edition that shipped today (2026-10-31).** Theme `sport-faith`, figure
    **Babe Ruth (real)**. Top 8: **"Top 8 parasocial applications in sport"**,
    eight ranked entries from `sports-identification` to `the-coach`, with the
    Pope/Villanova basketball wire as the source line. The eight ways each carry
    a pick - *The amateur hour* on persona, *Lugosi's burial* on character,
    *Krapp's tape* on companion, *The Book of My First Showings* on divine,
    *Transnational fandom* on institution, `M*A*S*H` on cosmology, *The local
    news anchor* on officer, *Fandom wars* on predator. A dry run for
    2026-11-01 chose theme `religion`, figure **Margery Kempe**, and eight
    entries with **zero overlap** with today's, which is the daily-change
    contract made measurable. Reading the persona way page also exposed a
    medium error the generated block made visible: `boybands` was filed
    `games`, while its own summary is fan clubs, fan voting and fan-financed
    releases. It is now `music`; the entry count and top-level keys were
    asserted unchanged.

    **Verification.** `python tools\daily.py` exit 0; source, post and visual
    tiers green, including `editor --check`, `test_editor_rotation`,
    `test_parasocialite_rotation`, `check_css --orphans`, `md_leak`,
    `internal_leaks` and `probe_hub_contrast`. The front page and the 390px
    phone render were opened: the figure card reads **REAL FIGURE**, **Babe
    Ruth**, **Why today** with the wire link, and **Top 8: The Team** below it.
    `make_zip` wrote `C:\Users\paras\Desktop\parasocialize-SITE.zip`, **752
    files, 15.2 MB, tree sha `57d27212ce8e1e09`**. **Cloudflare has not been
    re-uploaded**; the live site is still the pre-editor build until the user
    uploads `dist/` again.


96. **The daily features were correct and not a draw. The Top 8 got a headline, each way got a dated visual case file, and the figure got a detail worth coming back for.** The previous entry fixed *what* the three features select. This one fixes *why a reader would stop*. On 31 October the front page read **"Top 8: The Team"** - at once a sport list, a team list and a phrase that could mean anything - and a way page opened with an image-less paragraph headed "The boy band". The mechanism was working; the presentation was a filing cabinet.
    - **The Top 8 is now a pulp headline, not a category label.** All 25
      themes carry a hand-written `title`, `home_title`, `home_hook` and
      `domain`. Sport is **"Top 8: The Team That Owns You"** with *"You did not
      choose it. It chose the town you were born in."*; dead stars are **"The
      Dead Star Still Working"**; AI companions are **"The Machine That Misses
      You"**; fandom is **"The Crowd That Knows"**. The kicker carries the
      domain (`Daily edition · 31 OCT 2026 · Sport`), so the headline can be
      atmospheric without becoming ambiguous. The front page and `/top8/` use
      the same title, hook and ranked cards.
    - **Each way is a dated case file with a picture.** The daily block is now
      a two-column card: a real photograph for a story pick (with the section
      photograph as fallback) or the entry's title plate, then a large
      headline, the placement reason as the analysis, a **track line** of
      `N stories · N entries · N daily cases`, and only then the CTA. Entry
      plates say "a title plate, not a photograph" on their face, so the image
      never pretends to be evidence. The last five days are thumbnails beneath
      it; the record is a sequence, not a sentence.
    - **The wire match was the falsehood in the first visual draft.** `persona`'s
      AOC case carried a "In the wires" line about BLACKPINK's Lisa, because
      both mentioned *social media*. One shared word is not relevance; a
      confident link is worse than no link. A wire now needs at least one
      distinctive word from the **pick's own title** and one more shared
      subject word, with a generic-word stoplist. The AOC card correctly has
      no wire line; the current sports-betting wire on the figure block stays
      because the theme and headline actually match it.
    - **The figure is a daily discovery, not a directory entry.** The block
      now carries the entry's title plate, a **"The detail."** sentence chosen
      from the entry's significance (a year, a quote, a specific thing that
      happened), the real/fictional chip, the valence, and the wire that set
      the edition. The detail is the reason to come back tomorrow even when
      the figure is historical.
    - **Three medium corrections the new blocks exposed.** `boybands` was
      filed `games`; it is `music`. `the-local-anchor` was `television_scripted`;
      a local news anchor is `television_unscripted`. `anime-import` was
      `games`; it is `television_scripted` and `comics`. Each was visible in
      the generated meta line, which is the useful property of printing the
      medium next to the headline. The entry count and top-level keys were
      asserted unchanged.
    - **Verification.** `python tools\daily.py` exit 0; source, post and visual
      tiers green; `editor --check`, `test_editor_rotation`,
      `test_parasocialite_rotation`, `check_css --orphans`, `md_leak`,
      `internal_leaks` and `probe_hub_contrast` green. The front page, a story
      way page at 1440 and 500, and a plate way page at 1440 were opened and
      read: the AOC face is framed at `object-position:center 30%` (the first
      4:3 crop cut her at the eyes), the plate card is contained rather than
      cropped, and the phone card stacks image over text. `make_zip` wrote
      `C:\Users\paras\Desktop\parasocialize-SITE.zip`, **752 files, 15.2 MB,
      tree sha `f910ed1bca478e8e`**.
    - **Publishing is now automatic.** The Cloudflare secrets were saved and
      the `Publish to Cloudflare Pages (optional)` step ran green; the next
      scheduled edition will appear without a manual upload. The current live
      page is the previous build until the next run, which is why the workflow
      is triggered after this commit.


97. **A title plate inside a card is a placecard inside a placecard. The fallback is now a domain mark, and the mark says it is not a portrait.** The Babe Ruth spotlight used the entry's generated title plate as its image. The plate is a title treatment for the entry page; dropped into the figure card it read as a small card inside a larger card, and it was neither a photograph of the figure nor an honest stand-in for one. The entry had no sourced photograph, so the correct answer was the one the user named: an affiliation image - a baseball for a ballplayer, a clapperboard for a film star.
    - **`tools/affil.py` writes 20 author-drawn SVG marks**: sport,
      music, film, television, radio, literature, comics, games, AI,
      religion (an arch and candle), stage, visual art, technology, history,
      brand, persona (spotlight and mask), companion (two rings and a heart),
      officer (shield and star), predator (an eye), and the record/orbit
      default. They share one dark card, one orange line, one label, and the
      line **"AFFILIATION · NOT A PORTRAIT"** printed on the face.
    - **The figure resolver checks for a real photograph first.** If
      `data/images.json` has an item for the entry id, `img_for()` supplies it
      with its caption and credit. Otherwise the mark is chosen from the
      figure's `tags` (`sport` for Babe Ruth, `film` for Hitchcock and
      Valentino, `music` for Dionne Warwick), then from the entry's medium.
      The card caption reads **"Affiliation: film. No free photograph."** The
      mark is never passed off as the person.
    - **The ways pages use the way's own mark, not the entry's medium.**
      `divine` gets the arch, `officer` the shield, `predator` the eye,
      `cosmology` the orbit, `persona` the spotlight, `character` the speech
      bubble, `companion` the rings, `institution` the columned building. This
      is what gives the eight pages a consistent visual identity; an entry
      filed on `officer` but carrying `history` as its medium no longer gets a
      history icon, and a swatting entry in `predator` no longer gets a game
      controller. Story picks still use their own sourced photograph; only
      entries without one use a mark.
    - **No club or team marks.** A generic baseball is publishable; the Yankees
      logo is a trademark. The mark is the domain, not the franchise, and the
      caption says so.
    - **The first set of marks rendered nothing, and the filename looked
      fine.** The SVG text line contained `&middot;`, which is an HTML entity
      and not a defined XML entity; every `<img>` to those files was a valid
      200 with no image. `affil.py --check` now parses every SVG with
      `ElementTree` before it reports, and fails on a missing or stale file.
      **Confirmed red** by appending `&bad;` to `sport.svg` - it named
      `INVALID sport.svg: not well-formed` - and green after restoring it.
      This is the same lesson as the plate that stopped describing its entry:
      a file that exists is not a file that renders.
    - **The 1 November edition is the first live test.** Theme `fandom`,
      figure **Alfred Hitchcock (real)**, Top 8 **"The Crowd That Knows Your
      Name"**, and eight way picks. The front page and the `officer` and
      `divine` cards were opened: the film mark, the shield and the arch all
      render, the caption states the affiliation, and there is no plate in the
      figure or way cards. `daily.py --check` green; source, post and visual
      tiers green, including `affil --check` and `check_css --orphans`.
    - **Package.** `C:\Users\paras\Desktop\parasocialize-SITE.zip`, **772
      files, 15.19 MB, tree sha `87ec47fae5c42649`**. The Cloudflare publish
      step is configured and the workflow is triggered after this commit.


98. **The timeline was 255 entries with no argument, so the curated spine became its own page and the database became the corpus.** **This item records the first build; item 99 replaces the 22-milestone spine with the 88-entry master list.** The old `/timeline/` was `build_timeline()` over every encyclopedia entry: useful as a record, unreadable as a history, and impossible to filter by the six domains the subject actually has because the corpus classifies medium and attachment rather than era and domain. The page now has two layers. **`/timeline/` is the master timeline**; **`/timeline/corpus/` is the full 255-entry database**, linked from the master page and listed in the sitemap. The ten `/timeline/<section>/` pages are unchanged, and the corpus still links to them.
    - **The schema is enforced, not described.** `data/timeline.json` carries
      `id`, `year`, `title`, `domain`, `era`, `summary`,
      `parasocial_analysis`, `primary_source_or_artifact` and `tags`, plus
      `sort_year` (because `c. 8 CE` and `1830s-1850s` do not sort as strings)
      and `citations` (because a timeline that asserts dates must show where
      they come from). `tools/verify_timeline.py` checks required fields and
      types, domain and era membership, `sort_year` inside the year string,
      citation status and locator, unique ids, slug-shaped tags, and the
      rendered artefact: 22 cards, 22 panels, a matching `#tl-<id>` for every
      entry, and a corpus page that links back. **Confirmed red** by renaming
      one panel id in the built page - it named `panel id missing from the
      page: tl-character-ai` - then green on rebuild.
    - **The filters are the schema.** Domain chips cover Myth, Literature,
      Broadcast, Politics, Music and Digital; the **AI** chip is a derived view
      of the digital entries whose tags name an algorithmic or synthetic
      mechanism (TikTok and Character.AI, 2 of 22), and the page says so under
      the controls. Era chips are Pre-Modern, 19th-20th Century and Digital
      Age. **The bucket is a way in, not a claim:** Goethe is 1774 and sits
      under 19th-20th Century, while every card still prints its own era
      (`Early Mass Media`) and year, so the page never redates him. The tag
      menu carries all 89 tags; the chip row shows the ones used more than
      once.
    - **The slide-over is `:target`, so 22 entries cost one file.** The page is
      104 KB and the deploy is 773 files against the 1,000 limit. Each card
      links to `#tl-<id>`; the panel is `display:none` until it is the target,
      and the scrim and close links return to `#list`. That means no JS is
      needed to open, close or deep-link an analysis, and a reader can send
      someone a single milestone.
    - **Driven against the real page, not reasoned about.** In the browser:
      initial 22, AI 2, Myth 1, `Dickens` 1, no-match 0, cleared 22,
      `public-mourning` 4, Pre-Modern 3, Digital Age 5, and the panel opens on
      `#tl-character-ai` with one citation and closes on `#list`. The 1440px
      page and the 500px page were opened: two cards across at desktop, one at
      phone width, the year in its own column, and the slide-over full width.
    - **Sourcing.** 29 citation records across 22 entries: 27 `retrievable`,
      opened by this build, and 2 `unverified` - the Horton and Wohl DOI
      (Taylor & Francis returned 403) and the JFK Library campaign page (403).
      Both say in the record that this build did not open them. No quotation,
      date or attribution was invented; the Dickens ship anecdote is explicitly
      marked as a story repeated so often that it is part of the reception even
      where the evidence is thin.
    - **One limitation stated on the page rather than hidden.** The three UI
      era buckets collapse five data eras, so 1774 is filed under a label that
      says 19th-20th Century. The card and the panel both print the precise
      era; the bucket is a browsing aid. A future fourth bucket would fix the
      wording, not the fact, and adding one to make the label tidy is the same
      move as filling an empty taxonomy shelf.
    - `gates.py --all` green after the change: post (plate, orphans, findable,
      landmarks, ways, markdown, internal leaks, feeds, heads), visual (narrow,
      nav, hub contrast) and source (archive, editor, affil, citation, cull,
      taxonomy, **timeline**, card, image, the three rotation tests, link
      audit). `build_deploy` assembled 773 files / 363 pages with every local
      link resolving.


99. **The 22-entry spine was the wrong shape: the timeline became an 88-entry master list in five phases, and the user's basic list is the non-negotiable floor.** **Superseded by item 101: the master list is now 122 entries in six phases.** The previous build answered "what is the argument" when the request was "what is the record". A curated spine of 22 made the page readable and made it incomplete. The master list keeps every seed milestone and extends it with the instances the site can source, grouped in the five phases the user named. `/timeline/` is now the master list; `/timeline/corpus/` remains the 255-entry encyclopedia database.
    - **The counts.** 88 entries: phase 1 14, phase 2 12, phase 3 18,
      phase 4 18, phase 5 26. Six domains, five eras, 247 tags and 140
      citation records (112 `retrievable`, 28 `unverified`). The file is
      397 KB; the page carries 88 cards and 88 panels, one file, no new
      deploy pages.
    - **The seed is a gate, not a checklist in a commit message.** The 44
      milestones in the user's list map to ids in `CORE_IDS` in
      `tools/verify_timeline.py`, and the gate fails if any is missing. It
      also requires every phase to be populated, `sort_year` to be ordered
      inside each phase, and every entry to carry `phase`, `date_note` when it
      needs one, and a citation with a locator. **Confirmed red** by deleting
      `facebook` from the data: it named `seed milestones missing from the
      master list: facebook`, plus the 88-card/87-entry mismatch, then green
      on restore.
    - **Twenty-seven of the entries are the encyclopedia's own prose, carried
      with their citation records.** That is why the list could reach 88
      without inventing 88 new essays: `neanderthal-burial`,
      `paleolithic-figures`, `gobekli-tepe`, `roman-imagines`, `the-priest`,
      `the-icon`, `margery-kempe`, `our-lady-of-guadalupe`, `pamela`,
      `miss-havisham`, `sarah-bernhardt`, `betty-crocker`, `rin-tin-tin`,
      `aimee-semple-mcpherson`, `babe-ruth`, `soap-opera`, `superman-comic`,
      `sinatra-bobby-soxers`, `murrow`, `charlie-chaplin`, `mary-pickford`,
      `howdy-doody`, `vtuber`, `replika`, `deepfake-grief`,
      `sasaeng-culture` and `podcast-intimacy`. The rest are written for the
      timeline, with Wikipedia, Project Gutenberg and Perseus locators.
    - **Nine dates in the seed list are wrong or too precise, and the page
      says so in a `date_note` rather than silently repeating them.** Ovid is
      c. 8 CE, not 8 BCE; Dickens's 1812 is his birth, while the serial
      phenomenon begins with *Pickwick* in 1836; 1861 is one year inside the
      1858-70 reading tours; Margery Kempe's 1373 is her birth, and the Book
      was dictated in 1438; the Yellow Kid debuted in 1895, not 1897; *The
      Perils of Pauline* is 1914, not 1912; the bobby-soxer peak is 1942-44,
      not 1940; YouTube launched in 2005, with 2006 the acquisition and vlog
      boom; Twitch launched in 2011, with the donation layer maturing by 2014.
      The note is rendered in the panel under **Date note**, so a reader can
      see the correction without reading the prose.
    - **The page groups by phase and filters by phase, domain, era, tag and
      search.** The phase chips are the primary navigation; the era buckets
      are a second way in. Driven against the real page: initial 88, phase 1
      14, phase 5 26, AI 5, `Dickens` 3, no-match 0, `public-mourning` 4,
      phase 1 + Myth 9, phase 4 + Music 7, clear 88. The panel opens on
      `#tl-character-ai` and closes on `#list`.
    - **The page is still one file and still under the limit.** `:target`
      slide-overs mean 88 full analyses cost no extra pages; the deploy is
      773 files against 1,000. The 1440px and 500px renders were opened; the
      phase heading, the year column and the one-column phone card all hold.
    - **What is not claimed.** The list is the master list the site can
      support with a date and a source, not a proof that nothing else
      happened. The data note says it is built to grow, and the gate's seed
      set is a floor rather than a ceiling. The 28 `unverified` citations are
      visible on the page; they are not promoted to make the list look
      stronger.
    - `gates.py --all` green after the change: post (plate, orphans,
      findable, landmarks, ways, markdown, internal leaks, feeds, heads),
      visual (narrow, nav, hub contrast) and source (archive, editor, affil,
      citation, cull, taxonomy, **timeline**, card, image, the three rotation
      tests, link audit). `build_deploy` assembled 773 files / 363 pages with
      every local link resolving. Package: `C:\Users\paras\Desktop\parasocialize-SITE.zip`,
      **773 files, 15.27 MB, tree sha `2753fcb786c0f89b`**.


100. **The hourly counter could fail before the daily edition existed, and it could keep the repository current without deploying it. Both are fixed.** The failure on 1 November was **`counter` run 41259006291 at 00:57 UTC**, not the daily publish. It stopped at:
    ```
    REFUSING to build: no top-8 list is dated 2026-11-01.
    ```
    The 00:17 daily schedule produced no run at all, so the first counter after midnight was building pages against a day that did not have an edition yet. The daily runs later that morning (03:08, 03:48, 04:36 UTC) were green and published; the failed counter stopped before committing, so nothing was corrupted.
    - **The counter now self-heals the edition.** Before `build_cards.py`, it
      checks `data/features.json` for a list whose `released` date is today.
      If there is none, it runs `tools/editor.py` first, then builds.
      `editor.py` is idempotent for a date, so the 12:17 daily run keeps the
      edition rather than replacing it. The condition was tested both ways
      locally: today's edition returns 0, a future date returns 1.
    - **The daily cron is split.** `17 0,12 * * *` became two expressions,
      `17 0 * * *` and `17 12 * * *`. The 1 November 00:17 slot produced no
      scheduled run; splitting removes the comma list as a suspect. The
      counter is the safety net either way.
    - **The counter now packages and publishes.** It installs
      `requirements.txt` (needed by `build_deploy.optimise()`), runs
      `build_deploy.py --no-build` after `build_cards.py`, and has the same
      optional Cloudflare step as the daily job. The step runs only when the
      commit step made a commit (`changed=true`) and `CF_API_TOKEN` is set.
      This is what makes the counter a real fallback rather than a job that
      keeps the repository current while the live site stays on yesterday.
    - **Verified.** Dispatched counter runs: `41277337537` green (edition
      existed, build, link audit, archive, commit `651882b`) and
      `41278053246` green in 56s: sweep, build, `build_deploy`, link audit,
      archive, commit `ba9e47d`, **Cloudflare deployment complete**
      (771 files, 1 uploaded, `63cc1dcb.parasocialize.pages.dev`). The live
      `/timeline/` still returns 88 cards and 88 panels; the front page carries
      the 1 November edition.
    - **Residual risk stated.** If Cloudflare publishing fails, the commit is
      already pushed and the next hourly run retries; if the Cloudflare token
      is absent, the step skips exactly as the daily job's does. The counter
      publishes only what it committed, so a scheduled run that changes
      nothing does not create a deployment.


101. **The master list integrated both supplied milestone lists: 122 entries in six phases, with the second list's Phase 6 added and the seed floor raised to 78.** **Superseded by item 102: the PDF layer brings the data to 355 entries and seven phases, with 264 on the master page and 91 on the future page.** The first pass had 88 entries in five phases. The two supplied lists added 34 unique entries (15 from the first, 19 from the second, with Howdy Doody, VTubers, OnlyFans and the existing Liszt/Valentino/Lennon/Twitter entries already present). The result is grouped in the six phases the second list names:
    ```
    1 Antiquity, Ancient Ritual & Sacred Proxies   22
    2 Literature, Early Mass Print & Stage Magic    18
    3 Golden Age Radio, Early Cinema & Propaganda   25
    4 Modern Media, Psychoanalysis & Pop Idols      23
    5 Web 1.0, Digital Fandom & Creator Economies   28
    6 Post-Human, Algorithmic & Synthetic Frontiers  6
    ```
    - **What phase 1 gained.** Ka statues and false doors, Thespis,
      Akhenaten and the Aten, Asklepieion dream incubation, *The Imitation of
      Christ*, the ikiryō and Noh possession, Lucian's puppet god Glycon, and
      John Dee and Edward Kelley's Enochian conversations.
    - **Phase 2.** *Clarissa*, the Fox sisters, Pepper's Ghost, Jack the
      Ripper's "Dear Boss" letter, the Mona Lisa theft, and Conan Doyle's
      *The Final Problem*.
    - **Phase 3.** *The Goldbergs*, *Calling All Cars*, Lord Haw-Haw,
      Edward VIII's abdication speech, *Candid Camera*, *Rear Window*, and
      the quiz-show scandals.
    - **Phase 4.** ELIZA, Manson and Helter Skelter, the *Rocky Horror*
      midnight screenings, Tamagotchi, and *The Blair Witch Project*.
    - **Phase 5.** Kyoko Date, JenniCam, Hatsune Miku, *Her*, and *Animal
      Crossing: New Horizons*.
    - **Phase 6 is new.** TikTok's For You page, Character.AI,
      deepfake grief, OpenAI's Custom GPTs and Advanced Voice Mode,
      Neuro-sama, and synthetic mourning/griefbots. Character.AI,
      deepfake-grief and TikTok were moved out of phase 5 because they are
      the synthetic/algorithmic frontier, not the Web 2.0 creator economy.
    - **The corrections are in `date_note`, not in a silent edit.** Sherlock
      Holmes dies in **1893**, not 1890. Lord Haw-Haw begins in **1939**,
      not 1934. Tamagotchi is **1996**, not 1992. *Calling All Cars* is
      **1933–39**, not 1983. ELIZA was written **1964–66** and published in
      **1966**, not 1965. *The Rocky Horror Picture Show* opened in **1975**;
      the midnight callback screenings are **1976**. The VTuber form is
      **2016**, not 2014. Advanced Voice Mode is **2024**, not 2023. Liszt is
      **1840–47** (Heine's coinage is 1844). Twitter is **2006–09**. The
      ikiryō is Heian and medieval before the Noh formalisation. Akhenaten is
      **c. 1353–1336 BCE**, and the Athenian Asklepieion is **c. 420 BCE**.
      There are now 27 date notes in the file.
    - **The seed floor is 78 ids.** `tools/verify_timeline.py`'s `CORE_IDS`
      now contains all 44 original milestones and all 34 unique additions.
      The phase check is six, not five, and `sort_year` is still checked
      inside each phase. Confirmed red earlier by deleting `facebook`; the
      same seed check catches any of the 78.
    - **Measured page.** 539 KB, 122 cards, 122 panels, six phase groups, 338
      tags, 193 citation records (159 `retrievable`, 34 `unverified`). Driven
      in the browser: initial 122, phase 1 22, phase 6 6, AI 9, phase 6 + AI
      6, `Sherlock` 1, `Tamagotchi` 1, no-match 0, `spiritualism` 1, panel
      opens on `#tl-neuro-sama` and closes on `#list`. No console errors.
    - `gates.py --all` green across post, visual and source, including
      `verify_timeline`, `link_audit`, `check_css --orphans`, `md_leak`,
      `internal_leaks` and the three rotation tests. `build_deploy` assembled
      773 files / 363 pages. Package: `C:\Users\paras\Desktop\parasocialize-SITE.zip`,
      **773 files, 15.29 MB, tree sha `231f9101850d7d87`**.


102. **The supplied PDF timeline is now integrated as a visible source layer, not silently mixed into the sourced record.** The PDF (`Parasocial Timline 1800-2149.pdf`, 72 pages) parsed to **282 entries**: 191 dated 1812–2026 and 91 dated 2027–2149. It contains a number of duplicates of the existing master list and some near-duplicates inside itself, so the integration is explicit about what was added, what was skipped and what is speculative.
    - **The split.** The master page `/timeline/` now carries **264 entries**: the 122 sourced entries plus **142 historical PDF entries**. The PDF's **91 future projections** are on a separate page at **`/timeline/future/`**, every one marked **Speculative** and introduced as "not observed events". The data file holds all **355 entries** in seven phases; the master page renders phases 1–6, the future page phase 7. The pages are generated from the same file by `build_timeline_curated(..., speculative=False|True)`.
    - **Counts.** Phase 1 22, phase 2 90, phase 3 30, phase 4 63, phase 5 45, phase 6 14, phase 7 91. The master page shows **122 sourced / 142 PDF**; the future page shows 91 projections. There are **426 citation records**: 159 `retrievable`, 267 `unverified` (all 233 PDF citations are unverified by design).
    - **Deduplication.** The merge skipped **40 PDF entries** that matched an existing entry by year and shared title/summary terms, or by a curated keyword/year window (Dickens, Valentino, FDR, War of the Worlds, Horton, JFK/Nixon, Beatles, Elvis, Hinckley, Schaeffer, Diana, Blair Witch, Big Brother, YouTube, KUWTK, Twitch, TikTok, Character.AI, Neuro-sama, Taylor Swift, OpenAI, Fox sisters, Jack the Ripper, Yellow Kid, Uncle Tom, Rocky Horror, Tamagotchi, Michael Jackson, JenniCam, Animal Crossing, OnlyFans, Hatsune Miku, Kyoko Date, Replika, deepfake, Star Trek/Wars, Oprah, Madonna, Lennon, Manson, quiz shows, Candid Camera, Lord Haw-Haw, Howdy Doody, Disneyland, Babe Ruth, soap opera, Sinatra, Murrow, Superman, Bernhardt, Chaplin, Pickford, Sherlock, Byron, Liszt). A further **nine** near-duplicates were removed after review: ELIZA, Facebook, Twitter, Instagram, OnlyFans/Patreon, the YouTube-creator entry, Kizuna AI, TikTok and the MCU. **Forty-nine were skipped; 233 were added.**
    - **The PDF is the citation, and it is deployed.** Every PDF-derived entry cites
      the supplied artifact at
      `https://www.parasocialize.com/assets/parasocial-timeline-1800-2149.pdf`
      and carries `provenance: "pdf"` with status `unverified`. The page says
      `Source: Supplied PDF, unverified` in the panel and prints a **PDF** badge
      on the card. `build_deploy.INCLUDE_DIRS` gained `assets`; the deploy is
      **775 files**, still under the 1,000 limit. The PDF is 1.22 MB.
    - **The PDF's claims are not promoted.** The 142 historical entries use the
      PDF's own significance as their analysis, with the first sentence as the
      summary. No date or quotation was invented; the PDF is the record of what
      it says. The known limitation is on the page: the historical PDF layer is
      not independently verified, and the future page is explicitly speculative.
    - **The master page has a Source filter.** `All / Sourced / Supplied PDF` lets
      a reader see the 122 sourced entries without the PDF layer, or the 142 PDF
      entries alone. The future page has its own phase, domain, era, tag and
      search filters; its Source row only offers the PDF.
    - **Measured in the browser.** Master: 264 initial, 122 sourced, 142 PDF,
      phase 2 90, `Byron` 4, no-match 0. Future: 91 initial, 91 PDF, phase 7 91,
      no-match 0. A PDF panel opens on
      `#tl-the-caroline-lamb-obsession-and-glenarvon-1816` with one citation to
      the hosted PDF; a future panel opens on the 2149 entry and prints
      **Speculative projection, not an observed event**. No console errors.
    - `gates.py --all` green across post, visual and source, including
      `verify_timeline`, `link_audit`, `check_css --orphans`, `md_leak`,
      `internal_leaks` and the narrow/nav/hub probes. Package:
      `C:\Users\paras\Desktop\parasocialize-SITE.zip`, **775 files, 16.32 MB, tree sha `7cf07309332b7991`**.
    - **Still owed, stated rather than hidden.** The PDF's domain strings are
      freeform, so the six-domain mapping for the PDF layer is heuristic; a few
      entries sit under the nearest domain rather than the perfect one. The
      future entries are the PDF's projections, not forecasts this site
      endorses. Both facts are visible on the pages.



103. **The affiliation captions were explaining the same missing photograph under every image, so the visible explanation is gone.** The front page carried `Affiliation: film. No free photograph.` under the Hitchcock mark, and each way page carried `Affiliation: religion. No free photograph.` under its lead mark. The mark is already a clapperboard, an arch or a microphone; the caption repeated the mechanism in the most mechanical voice on the page. Removed from every figure and way card.
    - **What was removed.** The `figcaption` branch for an affiliation mark in
      `psotd_block`, and `art_note` / `.way-today-artnote` in the way card. The
      photo branch keeps its caption and credit, because attribution is not
      decorative. The `AFFIL_LABEL` dict and the `AFFIL_LABEL` import path are
      gone, since nothing renders the label any more.
    - **The mark is quieter too.** `tools/affil.py` no longer prints
      `AFFILIATION · NOT A PORTRAIT` on the SVG face; it prints the domain
      label (`FILM`, `RELIGION`, `SPORT`) and nothing else. The aria-label is
      now `FILM mark`, not `FILM affiliation mark`. The card does not repeat
      what the icon and the meta line already say.
    - **Plate alt text shortened.** Entry plates used to carry
      "A title plate for X: the name, the year and a mark drawn from the entry.
      It is not a photograph." It is now "A title plate for X." The long
      defensive sentence was not visible in normal rendering, but it was the
      same unneeded text in the accessibility layer.
    - **One CSS rule is conditional, not dead.** `.psotd-art figcaption` and its
      credit link still style a real photograph's caption, and no current figure
      has a photograph, so `check_css --orphans` called the rule dead. Rather
      than ratchet the baseline or delete a live branch, `check_css.py` gained a
      `CONDITIONAL` declaration: the figure block emits the figcaption only when
      `img_for()` returns a real photograph. The gate prints it as
      `conditional` with that reason.
    - **Verified.** A scan of every deployed `.html` for `Affiliation:`,
      `No free photograph`, `NOT A PORTRAIT`, `It is not a photograph` and
      `affiliation mark` returns nothing. The front page and
      `/ways/divine/` were opened: the film mark shows only `FILM`, the arch
      only `RELIGION`, and no caption sits under either. `gates.py --all` green
      across post, visual and source; `check_css --orphans` reports 29 colour/
      type notes and **0 orphaned layout rules**. Package:
      `C:\Users\paras\Desktop\parasocialize-SITE.zip`, **775 files, 16.32 MB,
      tree sha `7cf07309332b7991`**.
    - **Not removed.** "Why today.", "The detail.", "In the wires." and the
      photo captions are editorial labels, not apologies for a missing image;
      they stay. The request was the caption that explained the absence, not
      every label on the page.


104. **The mascot was a third masthead card and /brand/ was a gallery, so the clerk became a closing note and the gallery became an identity page with a rule.** The front page gave iYi 88px, a bordered card and a caption in the same row as the two doors. It was the second loudest object in the masthead, ahead of the stories and the top 8, and the link out was "What the mascot is for" - a page whose only job was to show the mascot again. Both were backwards: the wordmark and the two doors are the front page; the mascot is a colophon.
    - **Front page: two doors, no clerk card.** `.masthead-row` is now
      `1fr 1fr`; the `<aside class="clerk">` is gone. The `clerk_line` copy
      from `data/front_copy.json` is still used, in one strip near the foot of
      the page (after the eight ways and the deeper cards, before the signal):
      52px face, `The clerk`, the sentence, and `The mark and the rule →`.
      It is a colophon, not a headline.
    - **/brand/ is now a purpose page.** It opens with the mark and the line
      "the clerk of the record, not the host of the site", then four sections:
      **Where it appears** (section fronts, way pages, the front-page closing
      note, entry pages where there is deliberately no mascot); **Eight
      expressions** (the moods and what each is for); **The files** (expression
      sheet, default mark, flat mark, wordmark - all direct SVG links); and
      **The rule** (never claims to remember you; no synthetic depictions of
      real people; the eyes are the audience). It ends at `/ledger/` and
      `/timeline/`, so the page is answerable to something.
    - **The old page was a portfolio.** It explained the drawing and showed
      eight expressions, but a reader had no reason to be there. The new page
      says where the mark is allowed and where it is not, which is what makes it
      an identity page rather than a mascot shrine.
    - **The front-page test changed with it.** `test_front_copy.py` used to
      require `class="clerk"` inside the masthead row. It now requires exactly
      two doors, **no** clerk card in the row, a `clerk-note` elsewhere, a face
      in that note, and the note **after** `id="top8"` - a structural assertion
      that the mascot is secondary, not a class-name check.
    - **No new data slot.** `data/front_copy.json` still carries `clerk_line`;
      only the template moved. `front_copy.py` needed no change, and an existing
      edition still renders.
    - **Checked visually.** The 1440px front page now opens on the wordmark, the
      line, the two doors and the day's figure; the clerk is one thin strip at
      the foot. `/brand/` at 1440px is a two-column identity page (mark left,
      purpose right) with the four use cards and the mood grid. The 390px
      `verify_narrow` and the nav probe are green.
    - `gates.py --all` green across post, visual and source, including
      `test_front_copy`, `check_css --orphans`, `link_audit`, `md_leak` and the
      three rotation tests. Package: `C:\Users\paras\Desktop\parasocialize-SITE.zip`,
      **775 files, 16.32 MB, tree sha `b2c8896292128cce`**.
    - **Still editorial, not a build's call.** The nav still labels the route
      `iYi`; renaming it `The clerk` is a navigation decision and was not made
      here to avoid moving the measured header breakpoint. The page title and
      the route's content now carry the purpose.


105. **`/brand/` had no reader-facing job, so it is gone; the mascot now lives only where it does one.** The page had been a mascot gallery, then an identity-and-rule page. Neither was a reason for a reader to visit: the useful part was a usage note for a mark that already appears on ten section fronts and eight way pages, and the rest was self-description. A one-person publication does not need a brand portal.
    - **Removed from the navigation and footer.** The `iYi` link is out of
      `NAV`, out of the footer's Follow column, and out of the seven
      hand-written pages that carried the same nav line (`audit/`, three
      `cases/`, `classroom/`, `membership/`, `tip/`).
    - **The generator is gone; the URL is a redirect stub.** `build_brand()` is
      deleted and `build_cards.py` no longer writes the page. A static
      `brand/index.html` remains only because Cloudflare had cached the old page
      at `/brand/` with a seven-day `s-maxage`: the stub carries the standard
      feed/favicon head, `noindex, follow`, a canonical to `/credits/` and a
      meta refresh, so the cached URL moves a reader instead of showing a mascot
      page. `build_deploy.py` also appends `/brand/  /credits/  301`. The deploy
      is 775 files / 364 pages; the stub is one file and is not in the sitemap.
    - **The mark is still in the site, where it has a job.** Ten section fronts
      and eight way pages choose an expression from the subject; the front page
      has one closing note near the foot. Entry pages deliberately have no
      mascot. The note's outbound link is now **The standard →** to `/ledger/`,
      not a brand page.
    - **`brand/fonts/` stays.** It is not site content: it is the Fraunces
      static instances used by the episode renderer and `measure_type.py`.
      Deleting the directory would break video typography, not the website.
    - **What was removed from CSS.** `.moods`, `.mood`, `.mood-art`,
      `.mood figcaption*`, `.mascot-hero` and the `.brand-*` block were only
      used by the deleted page. `check_css --orphans` is green with 0 layout
      orphans after the removal.
    - **Checked.** `test_front_copy` still requires the clerk note after the Top
      8; the note's link text changed but the structural assertion did not.
      `gates.py --all` green across post, visual and source, including
      `link_audit`, `check_heads`, `verify_narrow` and `probe_nav`.
      `build_deploy` reports every local link resolves. Package:
      `C:\Users\paras\Desktop\parasocialize-SITE.zip`, **775 files, 16.31 MB,
      tree sha `eb6de27d75b019c7`**.


106. **The paid and email surfaces are gone, because neither was real.** There was no membership, no Friday email, and no decision about a business model, so every page that described one was a promise the site could not keep: `membership/`, `signal/`, `classroom/`, `audit/` and three `cases/` pages. They are deleted, not hidden. The only route with money attached is the Ko-fi link that already existed, and it sells nothing.
    - **Deleted:** `membership/index.html`, `classroom/index.html`, `audit/index.html`, `signal/latest.html`, `cases/` (index + three essays + three `.md` sources). The `build_cases()` generator and its `.md` reader are removed with them.
    - **Removed from the chrome:** the `Membership` link is out of `NAV` and both footers; `The Signal` is out of both footers and the front page's newsletter section; `/history/` no longer points at "the classroom"; `/shelf/` no longer carries the Case Files block.
    - **Removed from the sitemap and the head checks.** `membership/`, `signal/latest.html`, `classroom/` and `cases/` are no longer listed. `check_heads.INLINE_ONLY` is now empty, because the one page allowed to declare no stylesheet was the hand-styled email.
    - **Every retired URL 301s.** `build_deploy.py` now writes `/membership/` → `/credits/`, `/classroom/` → `/history/`, `/audit/` → `/credits/`, `/cases/*` → `/sections/`, `/signal/*` → `/radar/`, both with and without the trailing slash.
    - **Deleted CSS:** `.case-grid`, `.case-card`, `.case-no`, `.case-title`, `.case-teaser`, `.case-foot`, `.shelf-more`, `.signal-sec`, `.signal-form`, `.fineprint`, `.nav .cta-quiet`, `.price ul`, `.foot-mini .foot-tag`. `check_css --orphans` is back to 0 dead layout rules.
    - **Tests now assert absence, not presence.** `test_front_copy` fails if `membership/index.html`, `signal/latest.html` or `signal-form` returns to the front page.
    - **`/tip/` survives as Contact.** It is the one hand-written page with a reader-facing job: it opens a mail client with a pre-filled tip. Its copy no longer promises credit in a Friday email.
    - **Checked.** `gates.py --all` green across post, visual and source. Deploy: **766 files / 356 pages**, every local link resolves. Package: `C:\Users\paras\Desktop\parasocialize-SITE.zip`, **766 files, 16.27 MB, tree sha `09a1e75ea0b8a00f`**.


107. **`_redirects` had 270 rules and Cloudflare was applying about 108 of them.** The `/e/<id>` short links printed on episode end cards were generated one static rule per encyclopedia entry. Past a threshold - measured at roughly rule 105, against a documented limit of 2,000 static redirects - Pages silently ignores the rest, so `/e/eliza` (rule 60) redirected and `/e/marilyn-diptych` (rule 110) returned 404. The deploy succeeded, every gate was green, and 147 end-card links were dead.
    - **Collapsed to one dynamic rule.** Every `/e/<id>` maps to `/encyclopedia/<id>.html`, so the set became `/e/*  /encyclopedia/:splat.html  301`. `_redirects` is now 16 rules, 4 of them dynamic.
    - **New gate: `tools/check_redirects.py`.** It fails when the file exceeds a conservative 100 total rules, and it fails when any `/e/` URL the encyclopedia prints, or any renamed radar slug, has no rule that can serve it. Added to the post tier of `gates.py`. It asks whether the rules would be APPLIED, which no previous check did.
    - **The lesson is a class, not one file.** Every existing check verified that rules were *written*; none verified that they were *in force*. The same blind spot would have swallowed any silent platform limit.


108. **The sitemap described 355 of 356 pages, and two of the missing ones were ordinary reader pages.** `/exceptions/` (linked from `/taxonomy/`) and `/ledger/` (linked from the footer of every page, and publishing its own feed) were indexable and offered to no crawler. `build_sitemap()` was a hand-written list of remembered URLs plus loops over the data files; the site's own stated rule - "a page a reader can reach but a crawler cannot is only half published" - was written down in that function and enforced by nothing.
    - **Both added**, at priority 0.5.
    - **New gate: `tools/check_sitemap.py`.** It reads `dist/`, skips `noindex` pages and `404.html`, and fails in both directions: an indexable deployed page missing from the sitemap, or a sitemap URL with no file behind it. Added to the post tier.
    - **`brand/index.html` deleted.** The stub existed only because the `/brand/` redirect was one of the rules Cloudflare was ignoring; now that the file is 16 rules instead of 270, the 301 comes first and the stub can never be served.
    - **Checked.** `gates.py --all` green across post, visual and source. Deploy: **765 files / 355 pages / 353 sitemap URLs**. Package: `C:\Users\paras\Desktop\parasocialize-SITE.zip`, **765 files, 16.27 MB, tree sha `bad6cfa4260906f4`**.


109. **The sitemap listed four URLs twice.** `/top8/`, `/history/`, `/moments/` and `/figures/` were in the opening tuple and again in a later loop, so every sitemap carried four duplicate `<url>` entries with conflicting `changefreq` values (top 8 was `weekly` in one and `monthly` in the other). `check_sitemap.py` counts distinct URLs, which is how it surfaced: 357 `<loc>` lines, 353 pages. The later loop now carries only the three hubs not already listed, and the gate fails on a duplicate rather than silently collapsing it.


110. **The illustration PNGs were 4.9 MB on pages whose HTML is 15 KB.** `img/generated/` and `img/distilled/` were never passed through the WebP step because `optimise()` only ever looked at `img/editorial/`. The five largest were 791, 788, 745, 735 and 624 KB at 1084x528. Seven of them came out under a tenth of the size at the same dimensions; mean per-channel difference against the PNG is about 2/255, which is not visible. Deploy went from 23.2 MB to 19.4 MB and the archive from 16.27 MB to 12.21 MB.
    - **`optimise_illustrations()`** writes the WebP beside the PNG in `dist/` and `rewrite_illustrations()` repoints the nine pages that show one. A file whose WebP is not smaller is left as it was, and the rewrite asserts that no page still asks for a replaced PNG.
    - **The deploy file count was wrong, and it guards a hard limit.** `assemble()` returned a running total of the copies it made plus an adjustment for photographs. Once the function started writing files it did not copy, the total drifted: it said 758 for a 765-file tree, and that number is what the 1,000-file direct-upload check uses. It now counts the folder.

