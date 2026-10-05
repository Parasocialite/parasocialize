# AGENTS.md

Parasocialize: a source-honest encyclopedia and video channel about one-sided
relationships. 193 entries, 469 relations, 279 generated pages.

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
python tools\cull_audit.py    # does any entry claim the far side perceives the reader
python tools\image_audit.py   # does any image claim what its photograph shows, unopened
python tools\look.py --list    # the image queue; QUEUE IS 39, not 64
python tools\gen_atmosphere.py # encyclopedia atmosphere art. NEVER `exact`, never depiction
python tools\withdraw_image.py # reject a generated image: removes the record AND the file
python tools\record_image_size.py  # generation.final <- the PNG actually on disk
python tools\verify_doi.py --from-citations  # does every DOI resolve to the work cited
python tools\verify_taxonomy.py  # is the classification sound and complete
python tools\verify_narrow.py    # does a generated page overflow at 390px
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

**`link_audit.py` is a gate, not advice.** Read its output before committing.
Chaining it with `;` and committing anyway once put a failing commit in history.

**Run gates on their exit code, never through a pipe.** `| Select-String` on a
gate is how a red gate gets committed — see the `the-shadow` chronology item in
Traps for the round that actually happened. In PowerShell:

```powershell
foreach ($g in @('build_cards','build_deploy','citation_audit','cull_audit',
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

- `data/encyclopedia.json` — the single source of truth. 175 entries.
- `tools/build_cards.py` — all page generation, the citation board, section
  fronts, and the entry Watch block (renders only when a real `video` URL exists).
- `tools/build_deploy.py` — `dist/`, `/e/<id>` redirects for all 175 entries.
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
  categories (who or what is on the other end), six registers (what is happening
  in the tie), and — added 2026-10-03 — six **otherness** members (what the other
  end is *made of*), with 38 attachment sub-categories. This replaced the ten
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
180 sourced | 0 not yet stood behind | 13 thesis   = 193
edges landing on an entry with no source: COMPUTED - do not type this number here, tools/citation_audit.py prints it on every run
235 of 384 sources have a locator
0 of 380 claim to be openable without one   (ratcheted; was 94)
0 relations contradict the years they point at
0 relations point at themselves
0 relations claim an order neither end can support
0 citation strings are notes to self
0 entries assert the far side perceives the reader   (tools/cull_audit.py)
0 entries carry an unsourced claim                    (tools/add_source.py report)
39 attachment sub-categories, up from 38
6 otherness members, on a third axis
3 reciprocity members, on a fourth axis recovered from the 2019 chart
13 media values, up from 11 (radio and comics added)
```

Board must reconcile to 189. `add_source.py` is authoritative.

**Gate order matters.** `plate.py` draws from the data, so it must run *after*
`build_cards.py` and *before* `build_deploy.py`:

```powershell
python tools\build_cards.py; python tools\plate.py; python tools\build_deploy.py
```

Run the other way round and `build_deploy` reports 404s on plates that do not
exist yet, which is a true report of the tree it was given and a false report of
the project.

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
10. **The other 175 episodes.** All 177 entries carry `summary` and
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
      prints `QUEUE IS 39, not 64` so the number cannot drift back. **A queue
      that tells you to fetch work which cannot exist is worse than no queue,
      because it looks like progress and costs a pass to discover.**

## Deploy note

`dist/` must be re-uploaded after each build. It is routinely ahead of
production.

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
