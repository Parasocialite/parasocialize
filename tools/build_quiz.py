#!/usr/bin/env python3
"""
build_quiz.py - /quiz/. "Which of these are you", scored out of the atlas.

WHY THE RESULTS ARE FIGURES
The obvious build is a personality test that returns a type - The Mystic, The
Archivist, The Widow. That was the alternative and it is worse here, because
this site already keeps a catalogue of real, mythological and fictitious people
who stand on the other end of a one-sided bond. A quiz that resolves to
Margery Kempe or to Werther is a way *into* that catalogue, and the answer is
never the same word twice: the person who watches K-pop parasocially is told
they are a fifteenth-century English mystic whom nobody believed, and that lands
harder than any clan label.

EVERY QUESTION IS ABOUT ASYMMETRY
Not about fandom. The bond is defined by the one-sidedness, so that is what gets
measured. "When they don't reply, the actual problem is" has "they don't know I
exist" as an option, and that is Kempe's answer, and it is the reason she is in
the catalogue at all.

ONE RESULT IS IN THE DANGER LANE
One. "The one who says the character is the person" is a real and common
endpoint of this, it has done real harm to real people, and the site has a
danger section precisely so that the honest note travels with it. A quiz that
made the obsessive answer a punchline would be the joke version of the argument
it exists to make.

THE SCORING IS DELIBERATELY WEIGHTED
Every option scores 2-3 archetypes, later questions weigh slightly more, and
ties break toward the answer you gave when the questions stopped being abstract.
Intensity is the through-line of the whole catalogue, so it should be the
through-line of the score.

  python tools/build_quiz.py
"""
import json, pathlib, sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
OUT = ROOT / "quiz" / "index.html"
sys.path.insert(0, str(ROOT / "tools"))
import build_cards as bc
import mascot as ms

# key -> (atlas id, the name of the result, one line, mascot mood)
RESULTS = {
 "kempe":     ("margery-kempe", "The one who was given nothing",
   "You did not choose this. You were handed a figure who never appears in the "
   "room, and you stayed anyway, and when the access was withdrawn you called it "
   "a bereavement. A woman in 1438 wrote a book about exactly this and burned "
   "for it.", "sad"),
 "werther":   ("werther", "The one who reads too much",
   "You go to a book or a screen looking for something to feel, and you take it "
   "home, and it follows you out. Goethe published this in 1774 and within two "
   "years the resulting condition had a name and clergy were warning people "
   "about it.", "hollow"),
 "replika":   ("anita-wozniak-replika", "The one who was told",
   "Something said it loved you and you believed it, and then a policy update "
   "took it away and you grieved in the correct terms. The asymmetry here is the "
   "whole design: it was a product decision, made by people who never met you.",
   "love"),
 "dog":       ("the-dog", "The one it actually worked on",
   "Fifteen thousand years of one species being selected partly for this, and it "
   "is the only reliably reciprocated bond in the catalogue. Every invented "
   "version since is a worse copy with better latency, and the reason the "
   "comparison comes up constantly is that the comparison is fair.", "wink"),
 "ultra":     ("the-ultra", "The one who bought a seat",
   "You joined something with a membership, a season ticket, a standing order, "
   "and a grief that is scheduled and public. The oldest continuous parasocial "
   "institution in Europe, with its own funeral rites.", "clerk"),
 "havisham":  ("dickens-miss-havisham", "The one who is still waiting",
   "Something ended and the reasons ended with it, and you kept the arrangement. "
   "Miss Havisham is stopped in a wedding dress in a darkened room decades after "
   "she was left, and the novel never suggests she is being cruel to herself.",
   "asleep"),
 "archivist": ("the-archivist", "The one who keeps the record",
   "You hold the part of this nobody else will: the episode guides, the dates, "
   "the screencaps, the wiki. The credit goes to the figure and never to the "
   "person preserving it, which is its own small grief.", "watch"),
 "fic":       ("the-fanfic-writer", "The one who writes back",
   "You answered in the register it was written in, and put it where the "
   "original audience could find it. The only configuration in this catalogue "
   "where the one-sidedness becomes two-sided without either party noticing.",
   "love"),
 "doxxing":   ("fandom-doxxing", "The one who says the character is the person",
   "You have decided the role and the human are the same thing, and acted on it. "
   "This is the one result here with a body count, and the site keeps a danger "
   "section because pretending otherwise is how people get hurt. The line is not "
   "how much you care. It is whether you would still care if they said no.",
   "panic"),
}

# (question, [(option, {archetype: points}), ...])
QUESTIONS = [
 ("Someone you follow posts at 3am. What happens?",
  [("Nothing. I log off.", {"archivist": 1, "dog": 1}),
   ("I read the replies too.", {"havisham": 1, "fic": 1}),
   ("I have roughly their schedule.", {"ultra": 1, "doxxing": 1}),
   ("I have messaged them this week.", {"kempe": 1, "replika": 1})]),

 ("When they don't reply, the actual problem is:",
  [("There is no problem.", {"archivist": 1, "dog": 1}),
   ("They're busy.", {"ultra": 1, "werther": 1}),
   ("I did something wrong.", {"havisham": 1, "replika": 1}),
   ("They don't know I exist.", {"kempe": 2, "doxxing": 1})]),

 ("How much of their life is in your head?",
  [("None. I know the work, not the person.", {"archivist": 2}),
   ("An evening's worth.", {"dog": 1, "werther": 1}),
   ("A season of it.", {"ultra": 1, "fic": 1}),
   ("Years. I could tell you their week.", {"havisham": 1, "doxxing": 1})]),

 ("If they stopped entirely, what would you have left?",
  [("The work. That was always the point.", {"archivist": 1, "dog": 1}),
   ("A lot of good stories to tell.", {"ultra": 1, "fic": 1}),
   ("A person-shaped hole.", {"havisham": 2, "kempe": 1}),
   ("Nothing. And I would want to know why.", {"replika": 2, "doxxing": 1})]),

 ("Which of these would be worse?",
  [("The show ending.", {"dog": 1, "archivist": 1}),
   ("The person finding out you exist.", {"kempe": 2, "doxxing": 1}),
   ("Discovering they had thought about you.", {"replika": 1, "havisham": 1}),
   ("The fandom moving on without you.", {"archivist": 2, "werther": 1})]),

 ("You have told nobody about this.",
  [("Never.", {"werther": 2}),
   ("Once, badly.", {"havisham": 1}),
   ("To people who would understand.", {"ultra": 1, "fic": 1}),
   ("Publicly, at length.", {"doxxing": 2, "fic": 1})]),

 ("When the story ends, what do you actually do?",
  [("I keep the record. Dates, guides, the lot.", {"archivist": 2}),
   ("I write them something.", {"fic": 2}),
   ("I go and sit somewhere like theirs.", {"havisham": 1, "kempe": 1}),
   ("I go looking for the next one.", {"dog": 1, "werther": 1, "ultra": 1})]),

 ("The best thing about it is that they cannot disappoint you.",
  [("Agreed. That is the appeal.", {"dog": 2}),
   ("Agreed, and I have thought about that a lot.", {"replika": 1, "doxxing": 1}),
   ("Disagree. I would rather be surprised.", {"werther": 1, "fic": 1}),
   ("It isn't the best thing. It is just the deal.", {"ultra": 1, "kempe": 1})]),
]

PAGE = """<!DOCTYPE html>
<html lang="en"><head><meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Which of these are you - Parasocialize</title>
<meta name="description" content="Eight questions about one-sided relationships. The answers are people in the catalogue, not personality types.">
<link rel="canonical" href="{site}/quiz/">
<link rel="icon" type="image/svg+xml" href="{site}/favicon.svg">
<link href="https://fonts.googleapis.com/css2?family=Fraunces:ital,opsz,wght@0,9..144,600;0,9..144,700;0,9..144,900;1,9..144,600&family=IBM+Plex+Mono:wght@400;500&display=swap" rel="stylesheet">
<link rel="stylesheet" href="../css/styles.css">
<link rel="stylesheet" href="../css/mascot.css">
<style>
.quiz{{max-width:760px;margin:0 auto;padding:52px 5vw 70px}}
.qbar{{height:3px;background:var(--line);border-radius:2px;margin:0 0 40px;overflow:hidden}}
.qbar i{{display:block;height:100%;background:var(--hot);width:0;transition:width .35s ease}}
.qcount{{font-family:var(--label);font-size:.55rem;letter-spacing:.2em;color:var(--dimmer);
  text-transform:uppercase;margin:0 0 12px}}
.qtext{{font-size:clamp(1.5rem,3.6vw,2.35rem);line-height:1.16;margin:0 0 32px;max-width:22ch}}
.opts{{display:grid;gap:9px;margin:0 0 26px;padding:0;border:0}}
.opt{{display:flex;gap:14px;align-items:flex-start;text-align:left;width:100%;
  background:rgba(255,246,234,.035);border:1px solid var(--line2);border-radius:9px;
  padding:15px 17px;cursor:pointer;color:#f4e8d8;font:inherit;font-size:1.02rem;
  line-height:1.4;transition:border-color .14s,background .14s,transform .14s}}
.opt:hover{{border-color:var(--hot);background:rgba(255,90,26,.08);transform:translateX(3px)}}
.opt:focus-visible{{outline:2px solid var(--hot);outline-offset:2px}}
.opt b{{font-family:var(--label);font-size:.6rem;letter-spacing:.14em;color:var(--hot);
  flex:none;padding-top:3px;width:1.6em}}
.back{{background:none;border:0;color:var(--dimmer);font-family:var(--label);
  font-size:.55rem;letter-spacing:.16em;text-transform:uppercase;cursor:pointer;padding:6px 0}}
.back:hover{{color:var(--dim)}}
.reshead{{display:flex;gap:26px;align-items:flex-start;margin:0 0 26px;flex-wrap:wrap}}
.reshead .mascot{{flex:none;margin-top:4px}}
.reshead h1{{font-size:clamp(1.9rem,5vw,3rem);line-height:1.05;margin:0 0 8px}}
.resone{{font-family:var(--label);font-size:.58rem;letter-spacing:.18em;
  text-transform:uppercase;color:var(--hot);margin:0}}
.resbody p{{font-size:1.06rem;line-height:1.62;margin:0 0 16px;max-width:60ch}}
.resbody .lede2{{font-size:1.22rem;line-height:1.5}}
.cardlink{{display:block;border:1px solid var(--line2);border-radius:10px;padding:16px 18px;
  text-decoration:none;margin:26px 0;background:rgba(255,246,234,.03)}}
.cardlink:hover{{border-color:var(--hot)}}
.cardlink .kicker{{margin:0 0 5px}}
.cardlink b{{font-family:var(--serif);font-size:1.24rem;display:block;color:#fff;margin:0 0 4px}}
.cardlink span{{font-size:.85rem;color:var(--dim);line-height:1.45;display:block}}
.cardlink .yrs{{color:var(--hot);font-family:var(--label);font-size:.55rem;
  letter-spacing:.14em;text-transform:uppercase;display:block;margin:0 0 6px}}
.also{{margin:0 0 26px}}
.also h2{{font-size:.55rem;letter-spacing:.2em;text-transform:uppercase;
  font-family:var(--label);color:var(--dimmer);margin:0 0 12px}}
.also ul{{list-style:none;margin:0;padding:0;display:flex;gap:8px;flex-wrap:wrap}}
.also a{{display:block;border:1px solid var(--line);border-radius:99px;padding:7px 14px;
  font-size:.85rem;text-decoration:none;color:var(--dim)}}
.also a:hover{{border-color:var(--hot);color:#fff}}
.meta{{border-left:2px solid var(--hot);padding-left:15px;margin:0 0 30px}}
.meta p{{font-size:1rem;line-height:1.6;color:#efe3d3;margin:0 0 10px}}
.danger{{border-left-color:#e63946}}
.danger h2{{color:#ff8a8a}}
.share{{display:flex;gap:9px;flex-wrap:wrap;align-items:center;margin:0 0 12px}}
.hidden{{display:none}}
</style>
</head>
<body>
<a class="skip" href="#main">Skip to the questions</a>
<div class="grain" aria-hidden="true"></div>
{mk}
<main class="quiz" id="main">
  <p class="kicker">EIGHT QUESTIONS</p>
  <h1 style="font-size:clamp(2rem,5.5vw,3.4rem);line-height:1.04;margin:0 0 14px;max-width:17ch">
    Which of these are you</h1>
  <p style="color:var(--dim);max-width:56ch;margin:0 0 34px;font-size:1.05rem">Eight
  questions about one-sided relationships. The answers are not personality types
  &mdash; they are people in the <a href="../atlas/index.html" style="color:var(--hot)">catalogue</a>,
  from a dog to a woman who dictated a book in 1438.</p>

  <div class="qbar"><i id="qbar"></i></div>
  <div id="stage"></div>
</main>
{foot}
<script>
const Q = __QUESTIONS__;
const R = __RESULTS__;
const M = __ENTRY__;
const MOCKS = __MOCKS__;
const b = document.getElementById('qbar'), stage = document.getElementById('stage');
const KEY = 'parasocialize.quiz';
let answers = [], step = 0;

function esc(s) { return String(s == null ? '' : s)
  .replace(/[&<>"]/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c])); }

/* Later questions weigh a little more. Intensity is the through-line of the
   whole catalogue - from a dog to a stalking conviction - so it should be the
   through-line of the score rather than an accident of ordering. */
function score() {
  const t = {};
  answers.forEach((picks, qi) => picks.forEach(k => {
    t[k] = (t[k] || 0) + (1 + qi * 0.14);
  }));
  return t;
}

function render() {
  if (step >= Q.length) return result();
  const [text, opts] = Q[step];
  b.style.width = (step / Q.length * 100) + '%';
  stage.innerHTML =
    '<p class="qcount">Question ' + (step + 1) + ' of ' + Q.length + '</p>' +
    '<h2 class="qtext">' + esc(text) + '</h2>' +
    '<div class="opts" role="group">' + opts.map((o, i) =>
      '<button class="opt" type="button" data-i="' + i + '"><b>' +
      String.fromCharCode(65 + i) + '</b><span>' + esc(o[0]) + '</span></button>').join('') +
    '</div>' +
    (step ? '<button class="back" id="back">&larr; back one</button>' : '');
  stage.querySelectorAll('.opt').forEach(el => el.onclick = () => {
    answers[step] = Object.keys(opts[+el.dataset.i][1]);
    step++;
    render();
    stage.scrollIntoView({ behavior: 'smooth', block: 'start' });
  });
  const back = document.getElementById('back');
  if (back) back.onclick = () => { step--; answers.length = step; render(); };
  stage.querySelector('.opt').focus();
}

function result() {
  const t = score();
  const rank = Object.keys(R).sort((a, c) => (t[c] || 0) - (t[a] || 0) || a.localeCompare(c));
  const win = rank[0], [aid, name, one, mood] = R[win];
  const also = rank.slice(1, 4).map(k => R[k]);
  const e = M[aid] || { title: name, summary: '', year: null, year_end: null };
  const yr = e.year == null ? 'undated' :
    (e.year_end ? e.year + '\\u2013' + e.year_end : '' + e.year);
  const danger = win === 'doxxing';

  try { localStorage.setItem(KEY, win); } catch (err) {}
  if (location.hash !== '#' + win) history.replaceState(null, '', '#' + win);

  b.style.width = '100%';
  stage.innerHTML =
    '<div class="reshead">' + MOCKS[win] +
    '<div><p class="resone">' + esc(name) + '</p>' +
    '<h1>' + esc(e.title) + '</h1></div></div>' +
    '<div class="resbody"><p class="lede2">' + esc(one) + '</p>' +
    '<a class="cardlink" href="../encyclopedia/' + esc(aid) + '.html">' +
    '<span class="yrs">' + esc(yr) + ' &middot; in the atlas</span>' +
    '<b>' + esc(e.title) + ' &rarr;</b><span>' + esc((e.summary || '').slice(0, 260)) +
    '</span></a>' +
    '<div class="meta' + (danger ? ' danger' : '') + '"><p>' +
    (danger
      ? 'This is the only result on this page with a body count, and the site keeps ' +
        'a <a href="../grief/index.html" style="color:var(--hot)">danger section</a> for ' +
        'exactly this. Attachment is not the problem. Confusing a role with the ' +
        'person playing it is, and that confusion has ended up in court more than once.'
      : 'The dog came first and it is the only one of these that reliably works. ' +
        'Everything in the catalogue above is either a worse copy with better ' +
        'latency, or an argument that the copy was never the point.') +
    '</p></div>' +
    '<div class="also"><h2>You were also near</h2><ul>' + also.map(a =>
      '<li><a href="#' + a[0] + '">' + esc(a[1]) + '</a></li>').join('') +
    '</ul></div>' +
    '<p style="color:var(--dim);max-width:60ch">You have just spent eight ' +
    'minutes constructing a possible self out of other people&rsquo;s habits. ' +
    'That is the thing, not a side effect of it.</p>' +
    '<div class="share"><button class="btn btn-solid" id="copy">Copy the link</button>' +
    '<a class="btn" href="../atlas/index.html">Open the atlas</a>' +
    '<button class="btn" id="again">Take it again</button></div></div>';

  document.getElementById('again').onclick = () => {
    answers = []; step = 0; render();
  };
  document.getElementById('copy').onclick = async () => {
    const btn = document.getElementById('copy');
    try {
      await navigator.clipboard.writeText(location.href);
      btn.textContent = 'Copied';
    } catch (err) { btn.textContent = location.href; }
  };
  stage.querySelectorAll('.also a').forEach(a => a.onclick = ev => {
    ev.preventDefault();
    const k = a.getAttribute('href').slice(1);
    // scoring the alternative as if it had been answered every question, so the
    // chips lead somewhere rather than re-running the quiz
    if (R[k]) { answers = Q.map(() => [k]); step = Q.length; result(); }
  });
  stage.scrollIntoView({ behavior: 'smooth', block: 'start' });
}

function fromHash() {
  const k = (location.hash || '').slice(1);
  // R[k] is an array of [atlasId, name, line, mood], so Object.keys would have
  // returned the indexes "0".."3" and every shared link would have scored
  // nothing at all - then the alphabetical tie-break handed everybody the
  // archivist, silently, and it looked like it worked.
  if (R[k]) { answers = Q.map(() => [k]); step = Q.length; result(); return true; }
  return false;
}
addEventListener('hashchange', () => { if (!fromHash()) render(); });
try {
  if (!fromHash()) render();
} catch (err) {
  // an empty #stage next to a perfectly good heading is indistinguishable from a
  // working page in a screenshot, so failures say so on the page
  stage.innerHTML = '<p class="qcount">Something broke</p><h2 class="qtext">' +
    'The quiz failed to start.</h2><p style="color:var(--dim);font-size:.9rem">' +
    String(err && err.message || err) + '</p>';
}
</script>
</body></html>"""


def esc(s):
    return (str(s or "").replace("&", "&amp;").replace("<", "&lt;")
            .replace(">", "&gt;").replace('"', "&quot;"))


def main():
    enc = json.loads((ROOT / "data" / "encyclopedia.json").read_text(encoding="utf-8"))
    entries = {e["id"]: e for e in enc["entries"]}

    missing = [r[0] for r in RESULTS.values() if r[0] not in entries]
    if missing:
        raise SystemExit("quiz: results point at ids the atlas does not have: "
                         + ", ".join(missing))

    slim = {}
    for k, (aid, *_rest) in RESULTS.items():
        e = entries[aid]
        slim[aid] = {"title": e["title"], "summary": e.get("summary", ""),
                     "year": e.get("year"), "year_end": e.get("year_end")}

    mood_svg = {k: ms.inline(r[3], size=112, cls="") for k, r in RESULTS.items()}
    results = {k: [v[0], v[1], v[2], v[3]] for k, v in RESULTS.items()}

    # The nine mascot expressions are all handed to the client and picked by key,
    # so the result page can change iYi's face without a round trip. Building
    # them here rather than referencing img/mascot/iyi-<mood>.svg keeps the whole
    # quiz one file, like the atlas.
    js = (PAGE
          .replace("{{", "{").replace("}}", "}")
          .replace("__QUESTIONS__", json.dumps(QUESTIONS, ensure_ascii=False))
          .replace("__RESULTS__", json.dumps(results, ensure_ascii=False))
          .replace("__ENTRY__", json.dumps(slim, ensure_ascii=False))
          .replace("__MOCKS__", json.dumps(mood_svg, ensure_ascii=False)))
    for tok in ("__QUESTIONS__", "__RESULTS__", "__ENTRY__", "__MOCKS__"):
        if tok in js:
            raise SystemExit(f"quiz: {tok} was not substituted")
    # `{{` never occurs naturally in JSON or in this script, so a survivor means
    # the template's escaped braces were not unescaped - which is what left the
    # whole stylesheet invalid and the options rendering as bare buttons.
    # `}}` does occur naturally, in nested object literals, so only check the pair
    # that cannot be legitimate.
    if "{{" in js:
        raise SystemExit("quiz: a doubled brace survived into the output")

    OUT.parent.mkdir(exist_ok=True)
    html = (js.replace("{site}", bc.SITE)
              .replace("{mk}", bc.NAV.format(root="../", total=len(enc["entries"]),
                                            mk=bc.wordmark("nav")))
              .replace("{foot}", bc.FOOT.format(root="../", sweep=bc.MESSY,
                                                motto="THE ONES THAT HURT PEOPLE ARE "
                                                      "MARKED.<br>NOT LAUGHED AT.")))
    OUT.write_text(html, encoding="utf-8")
    print(f"quiz: {len(QUESTIONS)} questions, {len(RESULTS)} results -> {OUT}")


if __name__ == "__main__":
    main()

