"""Place `krapp-last-tape`, and record that the nancy-drew hole is a PATTERN.

Placed `companion/anthropomorphised-tool`, otherness deliberately unplaced.

**The shelf.** That category is "a tool that accumulates a name, a history and a
tone, and becomes addressed as a person long before anybody designed it to be",
and its test ends "persistence after the purpose has gone is the test". A tape
recorder fits both halves: Krapp's ledger names the reels - one is "Farewell to
love" - so the machine has acquired titles and a chronology, and the purpose
that justified it (a yearly review of the year gone) has gone while the reels
remain and are played. `the-shadow` and `howdy-doody` already sit here, and
both are the same shape: a voice arriving through a device rather than a body.

**Why otherness is left empty, and why this is now a pattern rather than an
incident.** `made` was the obvious candidate and its own `mechanism` refuses
the case: "**The figure answers, and that is the whole appeal**, so every answer
is a small breach: the voice is pre-recorded, the mouth is somebody else's
hand." Krapp's far end **never answers** - that is the play. `mirrored` was the
other candidate and it half-fails: its test, "was it made by the person
attached to it?", answers yes, and its `not` insists "the mirrored case is
specifically the shape of a person who exists, attached to an ideal copy of
them", which Krapp is - but its `mechanism` says the copy is "assembled out
of memory and **never checked against the original**", and that is exactly
what goes wrong here. **The original is sitting in the chair listening.** The
tape is not an idealised self; it is a verbatim one, and its accuracy is the
problem.

**So the otherness axis now has two entries it cannot file, failing in
opposite directions, and both about the same absent thing:**
  - `nancy-drew` - a figure **written by an operator the audience is never
    shown** (`imagined` needs them to know; `made` needs them to see).
  - `krapp-last-tape` - a **recording of a real person as the far end of a
    one-sided tie**, where `made` presumes the figure answers and `mirrored`
    presumes the copy was never checked against the original.

One of them is a machine that cannot speak; the other is a machine that
speaks only in the past. **Both are the case the axis has no word for: the far
end is a recording.** That is a candidate ninth member and it is the author's
call, exactly as with `nancy-drew`. Recorded here, not filled.

Reads the committed file's indentation and key order from the committed bytes.
Asserts the assignment count, the key set and the top-level keys.
"""
import collections
import json
import pathlib
import subprocess
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ROOT = pathlib.Path(r"C:\Users\paras\Documents\Default Project\parasocialize"
                    )
APPLY = "--apply" in sys.argv

EID = "krapp-last-tape"
VALUE = {
    "cat": "companion",
    "sub": "anthropomorphised-tool",
    "why": (
        "Filed `companion/anthropomorphised-tool`: \"a tool that accumulates a "
        "name, a history and a tone, and becomes addressed as a person long "
        "before anybody designed it to be\", whose test ends \"persistence "
        "after the purpose has gone is the test\". A tape recorder fits both "
        "halves. Krapp's ledger **names the reels** - one is \"Farewell to "
        "love\" - so the machine has acquired titles and a chronology of its "
        "own, and the purpose that justified it, a yearly review of the year "
        "gone, has gone while the reels remain and get played. "
        "`the-shadow` and `howdy-doody` already sit on this shelf and both are "
        "the same shape: a voice arriving through a device rather than a body. "
        "`character/played-role` was the other candidate and is about the actor "
        "rather than the object of the tie, which here is the recording.\n\n"
        "**Deliberately unplaced on otherness, and this is the second entry the "
        "axis cannot file - failing in the opposite direction to "
        "`nancy-drew`, and about the same absent thing.** `made` is the "
        "obvious candidate and its own `mechanism` refuses the case: \"**The "
        "figure answers, and that is the whole appeal**, so every answer is a "
        "small breach: the voice is pre-recorded, the mouth is somebody else's "
        "hand.\" Krapp's far end never answers; that is the play. `mirrored` "
        "half-fits and then fails: its test \"was it made by the person "
        "attached to it?\" answers yes, and its `not` insists the mirrored "
        "case is \"specifically the shape of a person who exists, attached to "
        "an ideal copy of them\", which Krapp is - but its `mechanism` calls the "
        "copy one \"assembled out of memory and **never checked against the "
        "original**\", and the whole play is that **the original is sitting in "
        "the chair listening.** The tape is not an idealised self. It is a "
        "verbatim one, and its accuracy is the problem.\n\n"
        "So there are now two unplaceable cases and neither is a one-off:\n"
        "- `nancy-drew` - a figure **written by an operator the audience is "
        "never shown** (`imagined` needs them to know it; `made` needs them "
        "to see it).\n"
        "- `krapp-last-tape` - a **recording of a real person as the far end "
        "of a one-sided tie**, where `made` presumes the figure answers and "
        "`mirrored` presumes the copy was never checked against the original.\n"
        "One is a machine that cannot speak; the other is a machine that "
        "speaks only in the past. **The case the axis has no word for is the "
        "far end being a recording** - and the fourth Faber error sharpens it, "
        "because that recording is damaged in every edition, so it is not even "
        "a faithful copy of the past. Recorded rather than filled: a ninth "
        "otherness member is the author's call.\n\n"
        "Reciprocity left unset. The condition here is `directed`, which is the "
        "default across the whole corpus, and the axis exists to surface the "
        "exceptions."
    ),
}

pla_p = ROOT / "data" / "taxonomy_placements.json"
tax_p = ROOT / "data" / "taxonomy.json"
enc_p = ROOT / "data" / "encyclopedia.json"

committed_text = subprocess.run(
    ["git", "show", "HEAD:data/taxonomy_placements.json"],
    capture_output=True, text=True, cwd=ROOT, check=True,
    encoding="utf-8").stdout
committed = json.loads(committed_text)
pla = json.loads(pla_p.read_text(encoding="utf-8"))
tax = json.loads(tax_p.read_text(encoding="utf-8"))
enc = json.loads(enc_p.read_text(encoding="utf-8"))

old_order = list(committed["assignments"])
before = len(pla["assignments"])
subs = {(a["id"], s["id"]) for a in tax["attachment"] for s in a.get("sub", [])}
unplaced = sorted(e["id"] for e in enc["entries"]
                   if e["id"] not in pla["assignments"])

if EID in pla["assignments"]:
    sys.exit(f"{EID} is already placed; refusing to overwrite a written reason")
if EID not in {e["id"] for e in enc["entries"]}:
    sys.exit(f"{EID} is not in the corpus; refusing")
if (VALUE["cat"], VALUE["sub"]) not in subs:
    sys.exit(f"refusing: {VALUE['cat']}/{VALUE['sub']} is not a sub-category")
if "other" in VALUE:
    sys.exit("refusing: this entry is deliberately unplaced on otherness")
if "rec" in VALUE:
    sys.exit("refusing: reciprocity is deliberately unset here")

siblings = sorted(k for k, v in pla["assignments"].items()
                  if f"{v['cat']}/{v['sub']}" == "companion/anthropomorphised-tool")
unplaced_other = sorted(k for k, v in pla["assignments"].items() if "other" not in v)
print(f"  entry   : {EID}")
print(f"  shelf   : {VALUE['cat']}/{VALUE['sub']}")
print(f"  other   : deliberately unplaced")
print(f"  rec     : deliberately unset (directed is the corpus default)")
print(f"  already unplaced in the corpus: {unplaced}")
print(f"  shelf residents: {siblings}")
print(f"  entries with no otherness value: {len(unplaced_other)}")
print(f"  assignments    : {before} -> {before + 1}")

if not APPLY:
    print("\ndry run. re-run with --apply")
    raise SystemExit(0)

rebuilt = collections.OrderedDict()
for k in old_order:
    rebuilt[k] = pla["assignments"][k]
rebuilt[EID] = VALUE

if set(rebuilt) != set(pla["assignments"]) | {EID}:
    sys.exit("refusing: key set changed by more than one addition")
if list(rebuilt)[:len(old_order)] != old_order:
    sys.exit("refusing: existing key order moved")

second = committed_text.split("\n")[1]
indent = len(second) - len(second.lstrip())
if not indent:
    sys.exit("refusing: could not read the committed indentation")

out = collections.OrderedDict()
for k in committed:
    out[k] = rebuilt if k == "assignments" else committed[k]

tmp = pla_p.with_suffix(".json.tmp")
tmp.write_text(json.dumps(out, ensure_ascii=False, indent=indent) + "\n",
               encoding="utf-8")
re_parsed = json.loads(tmp.read_text(encoding="utf-8"))
if len(re_parsed["assignments"]) != before + 1:
    sys.exit("refusing: reparse did not reconcile")
if list(re_parsed["assignments"]) != old_order + [EID]:
    sys.exit("refusing: order did not reconcile")
if re_parsed["assignments"][EID] != VALUE:
    sys.exit("refusing: the written reason did not survive the reparse")
tmp.replace(pla_p)
print(f"\nwritten at indent={indent}. assignments {before} -> {before + 1}.")
print("  Two entries now sit outside the otherness axis, failing in opposite")
print("  directions, and both are a recording. Recorded, not filled.")
