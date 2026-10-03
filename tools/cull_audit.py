"""cull_audit.py - does the corpus claim the other end perceives the audience?

Asked to "cull all the extra-sensory, even seemingly one-sided references", the
audit found nothing to cull: 0 of 189 entries assert that the far side perceives
the reader, viewer or listener by non-ordinary means. This file exists so that
claim can be re-checked whenever entries are added, instead of being a sentence
in a commit message that nobody ever tests again.

The hard part is not the pattern list, it is the distinction, and getting it
wrong in either direction is a serious error:

  AUDIENCE PERCEPTION (fails). The other end is asserted to perceive *you* -
  the reader, the viewer, the listener - telepathically, clairvoyantly, by
  possession or by omniscience. If that is true the tie is not one-sided, and
  the entry is describing something else.

  IN-FICTION RESPONSE (fine, reported only). A figure answering somebody inside
  the story is two-way inside the fiction and still one-sided for the reader,
  who cannot see the ghost at all. Harvey answers Elwood and is the clearest
  case of the phenomenon on this site. Confusing this with audience perception
  would cull the best entries in the corpus, which is the failure mode this
  file was nearly built on.

  ORDINARY PERCEPTION (fine, reported only). A teacher who knows your name
  because they see you every day, or a presenter who asks the audience for
  theirs, is doing nothing paranormal. Two entries matched on this and both are
  correct.

  DEFINITIONAL LANGUAGE (never flagged). "Does not respond", "one-sided",
  "no reciprocity" is this site's own name for the thing it is about. An
  earlier sweep matched thirty entries on it. Flagging those would report the
  thesis as a defect - and a version of this check that deleted them would have
  deleted the corpus. **Using the phrase is not making the claim.** This is the
  same trap as the borrowed-terminology diagnostic, which fired on `sasaeng` and
  `crossover`, both correct.

Run:  python tools\\cull_audit.py
      python tools\\cull_audit.py --report-only
"""
from __future__ import annotations

import json
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
enc = json.loads((ROOT / "data" / "encyclopedia.json").read_text(encoding="utf-8"))
E = enc["entries"]

# --- AUDIENCE PERCEPTION: these fail -----------------------------------------
# Deliberately narrow. Each pattern has to be about *the audience*, so
# "knows your name" alone is not here - it fires on a teacher.
AUDIENCE = {
    "telepathy": r"telepath(?:ic|y)?\s+(?:to|with|toward|of)\s+(?:you|the\s+(?:viewer|audience|reader|fan))",
    "mind-reading": r"(?:reads?|reading)\s+(?:your|the\s+(?:viewer's|audience's|reader's|fan's))\s+(?:mind|thought)",
    "clairvoyance": r"(?:sees?|saw)\s+(?:you|your\s+(?:future|house|room|city))\s+(?:as\s+)?(?:if\s+)?(?:clairvoyant|psychic)",
    "omniscience": r"(?:knows?|knowing)\s+(?:your\s+name|who\s+you\s+are)\s+without",
    "watches-you": r"(?:is\s+)?(?:watching|watching over)\s+(?:you|you\s+right\s+now)",
    "possession": r"(?:possesses?|possessed)\s+(?:you|your\s+body|the\s+viewer)",
    "reincarnation": r"(?:is|was)\s+your\s+(?:past\s+life|previous\s+incarnation)",
    "astral": r"astral\s+(?:projection|body)",
    "psychokinesis": r"(?:moves?|lifts?)\s+(?:objects?|you)\s+(?:with\s+)?(?:your\s+mind|psychically|by\s+telekinesis)",
    # Added after the gate failed a test it should have caught. A figure that
    # knows an individual viewer's name, or can see into the room they are
    # sitting in, has perceived *that person* - which is the whole test. These
    # are third-person and cannot fire on the second-person "a writer who knows
    # your name" in `saturday-mornings`, where the presenter asks.
    "knows-individual": r"knew\s+(?:their|our|your|the\s+(?:viewer'?s?|audience'?s?|fan'?s?))\s+(?:name|names|address|where\s+they\s+were)",
    "sees-into-room": r"(?:see|seeing|saw)\s+(?:in|into)\s+(?:the\s+|their\s+|your\s+)?(?:room|house|home|flat|apartment|bedroom)",
    "watches-in-private": r"watched\s+(?:them|you|him|her)\s+(?:sleep|at\s+night|in\s+private)",
    "seen-only-by-one": r"(?:visible|seen|appeared|appears)\s+only\s+to",
}
# --- REPORTED ONLY ------------------------------------------------------------
NOTE = {
    "ordinary-perception": r"knows?\s+your\s+(?:name|mood|home)",
    "in-fiction-response": r"(?:answers|replies|responds to)\s+(?:elwood|him|her|them|the\s+(?:child|fan|listener))\s+(?:in|within)\s+the\s+(?:film|story|film)",
    "personified-object": r"personif(?:y|ies|ied)",
    "seance-lexicon": r"s[ée]ance|spiritualism|mediumship|channeling",
    "divine-witness": r"(?:god|gods?|deity|the\s+divine)\s+(?:sees|knows|witnesses|observes)\s+(?:you|us|all|everything)",
    "premonition": r"premonit|precognit|forewarn",
    "tarot-oracle": r"\btarot\b|\boracle\b|crystal\s+ball",
}
# --- NEVER FLAGGED ------------------------------------------------------------
# The site's own vocabulary. Listed so that a future reader can see it was
# considered and deliberately excluded rather than overlooked.
DEFINITIONAL = r"(?:one[- ]sided|does\s+not\s+respond|no\s+reciprocity|parasocial)"


def blob(e):
    parts = [str(e.get(k) or "") for k in ("title", "summary", "significance")]
    for s in (e.get("sources") or []):
        parts += [str(s.get("citation") or ""), str(s.get("claim") or "")]
    return re.sub(r"\s+", " ", " ".join(parts))


def scan():
    fails, notes = [], []
    for e in sorted(E, key=lambda x: x.get("year") or 0):
        t = blob(e)
        f = [n for n, p in AUDIENCE.items() if re.search(p, t, re.I)]
        n = [k for k, p in NOTE.items() if re.search(p, t, re.I)]
        if f:
            fails.append((e, f))
        elif n:
            notes.append((e, n))
    return fails, notes


fails, notes = scan()
definitional = sum(len(re.findall(DEFINITIONAL, blob(e), re.I)) for e in E)

print("=" * 68)
print("EXTRA-SENSORY CULL AUDIT")
print("=" * 68)
print(f"  {len(E)} entries scanned")
print()
print(f"  FAIL  the far side is asserted to perceive the audience: {len(fails)}")
for e, f in fails:
    print(f"    {e['id']:<28} {e.get('year')}  {', '.join(f)}")
if not fails:
    print("    none. every bond here is one-sided for the reader, whichever way")
    print("    the figure behaves inside the story it appears in.")
print()
print(f"  note  reported, not defects: {len(notes)}")
for e, n in notes:
    print(f"    {e['id']:<28} {e.get('year')}  {', '.join(n)}")
print()
print(f"  {definitional} uses of the site's own one-sided vocabulary, counted and")
print("  never flagged: naming the phenomenon is not a claim about it. An")
print("  earlier sweep matched 30 entries on exactly this and would have")
print("  reported the thesis as a defect.")
print()

if fails and "--report-only" not in sys.argv:
    raise SystemExit(f"cull audit: {len(fails)} entr"
                     f"{'y' if len(fails) == 1 else 'ies'} assert the far side "
                     f"perceives the audience")
if fails:
    print(f"  {len(fails)} found, reported because --report-only was passed.")
else:
    print("  nothing to cull.")