"""Place `nancy-drew`, and record the hole its placement exposed.

Placed `character/fictional-protagonist` and `rec: simulated`. **Otherness left
unplaced, and that is the finding.**

  `imagined` needs the audience to KNOW they made it - "does the audience know
  they made it? If yes and nothing else in the world supports it". The Nancy
  Drew readers did not know, and a published series of thirty-odd books is
  about as much support for a character's existence as there is.
  `made` needs the operator to be SHOWN - "the transparency is a design
  choice", and its `not` excludes the hidden case by pointing at `played-role`,
  which is a different thing again (an actor visible on a stage).

  **Mildred Wirt Benson wrote 23 of the first 30 books under a house pseudonym
  that was not a person, and her identity was not made public until 1991.** So
  for the whole life of the fan-mail subseries the figure was operated by
  somebody the audience was never shown and never knew about.

  That is a fourth state on the otherness axis that the axis does not have: a
  figure **written by an operator the audience is not shown**. It is not
  `imagined` because the audience believed in it and did not know, and it is
  not `made` because nobody saw the hand. `the-shadow` and `howdy-doody` are
  `made` with the transparency intact - a voice actor, an advertising agency,
  a writer-director - and this is the same machinery with the byline bolted
  shut.

  **The honest move is to leave the field empty and say so**, which is what the
  `other` key's absence records and what this `why` records in prose. Adding a
  ninth member is a real editorial decision and belongs to the author, not to a
  script that found an entry which happens to need one.

`simulated` is the first instance on this axis that is neither live nor
digital. `live-commentary` and `twitch-subs` both work by latency - a host
reads a comment aloud within seconds. A correspondence department works by
post: the distance between a child's letter and its reply is a postal system,
and the reply was a typed letter on Syndicate stationery signed with a name
that was a slot rather than a woman.

Reads the committed file's own indentation and key order rather than assuming
them, per the last commit's lesson. Asserts the assignment count, the key set
and the top-level keys, and refuses to write if any moved.
"""
import collections
import json
import pathlib
import subprocess
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ROOT = pathlib.Path(__file__).resolve().parent.parent
APPLY = "--apply" in sys.argv

EID = "nancy-drew"
VALUE = {
    "cat": "character",
    "sub": "fictional-protagonist",
    "rec": "simulated",
    "why": (
        "Filed `character/fictional-protagonist` because that shelf's definition "
        "is almost a transcription of the case: \"Somebody described in a book "
        "and therefore available to an unlimited number of people at once\". "
        "Nancy Drew is the unlimited part - a printed series addressed to "
        "children the Syndicate did not know and could not count, and fifty-four "
        "years of it. `companion/social-agent` was the other candidate and is "
        "wrong: that shelf is \"a streamer-shaped entity with a persistent "
        "identity, a viewer count and an audience that gathers\", and nobody in "
        "1930 could see a viewer count. The object of the tie is a written "
        "character, not a system on a platform.\n\n"
        "`rec: simulated`, and the value is doing real work here rather than "
        "being decorative. A reply genuinely arrived - letters were answered, "
        "and the collection holds audio letters and commercial dramatic "
        "readings of the series - so the tie was not merely one-sided in "
        "appearance. What the axis asks is whether anything was felt on the far "
        "side, and the answer is a departmental process with no interior: "
        "\"Carolyn Keene\" was a slot in a production system reused across "
        "series by writers who never met. **This is the first `simulated` "
        "instance that is neither live nor digital.** `live-commentary` and "
        "`twitch-subs` both work by latency - a host reads a comment aloud "
        "within seconds. A correspondence department works by post: the "
        "distance between a child's letter and its reply is a postal system, and "
        "the answer was typed on Syndicate stationery. Same structure, and a "
        "scale the other two do not have.\n\n"
        "**Deliberately left unplaced on otherness, and the axis has a hole "
        "here.** `imagined` requires the audience to know they made the thing - "
        "\"does the audience know they made it? If yes and nothing else in the "
        "world supports it\" - and the readers did not know, with thirty-odd "
        "published books standing behind the character. `made` requires the "
        "operator to be shown, and its own `not` sends the hidden case to "
        "`played-role`, which is a different thing again. **Mildred Wirt Benson "
        "wrote 23 of the first 30 books under a house pseudonym that was not a "
        "person, and her identity was not made public until 1991** - so for the "
        "entire life of the fan-mail subseries the figure was operated by "
        "somebody the audience was never shown and never knew about. That is a "
        "fourth state the axis does not have: **a figure written by an operator "
        "the audience is not shown.** `the-shadow` and `howdy-doody` are `made` "
        "with the transparency intact, because a voice actor, an advertising "
        "agency and a writer-director are all discoverable; this is the same "
        "machinery with the byline bolted shut. Leaving the field empty and "
        "saying so here is the honest move - adding a ninth otherness member is "
        "an editorial decision, and it belongs to the author rather than to a "
        "script that happened to find an entry which needs one."
    ),
}

enc_p = ROOT / "data" / "encyclopedia.json"
pla_p = ROOT / "data" / "taxonomy_placements.json"
tax_p = ROOT / "data" / "taxonomy.json"

committed_text = subprocess.run(
    ["git", "show", "HEAD:data/taxonomy_placements.json"],
    capture_output=True, text=True, cwd=ROOT, check=True,
    encoding="utf-8").stdout
committed = json.loads(committed_text)
pla = json.loads(pla_p.read_text(encoding="utf-8"))
tax = json.loads(tax_p.read_text(encoding="utf-8"))
enc_ids = {e["id"] for e in json.loads(enc_p.read_text(encoding="utf-8"))["entries"]}

old_order = list(committed["assignments"])
before = len(pla["assignments"])

subs = {(a["id"], s["id"]) for a in tax["attachment"] for s in a.get("sub", [])}
recs = {m["id"] for m in tax["reciprocity"]["members"]}

if EID in pla["assignments"]:
    sys.exit(f"{EID} is already placed; refusing to overwrite a written reason")
if EID not in enc_ids:
    sys.exit(f"{EID} is not in the corpus; refusing")
if (VALUE["cat"], VALUE["sub"]) not in subs:
    sys.exit(f"refusing: {VALUE['cat']}/{VALUE['sub']} is not a sub-category")
if VALUE["rec"] not in recs:
    sys.exit(f"refusing: rec={VALUE['rec']!r} is not a reciprocity member")
if "other" in VALUE:
    sys.exit("refusing: this entry is deliberately unplaced on otherness")

# Who else carries `simulated`, so the "third instance" claim in the prose is
# checked rather than asserted.
carrying = {k: v["rec"] for k, v in pla["assignments"].items() if "rec" in v}
sim = sorted(k for k, v in carrying.items() if v == "simulated")
print(f"  entry       : {EID}")
print(f"  placement   : {VALUE['cat']}/{VALUE['sub']}  rec={VALUE['rec']}")
print(f"  other       : deliberately unplaced ({VALUE['why'].count('otherness')} refs in why)")
print(f"  currently `simulated`: {sim}")
print(f"  after this commit    : {sorted(sim + [EID])}")
print(f"  assignment count     : {before} -> {before + 1}")

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

txt = json.dumps(out, ensure_ascii=False, indent=indent) + "\n"
tmp = pla_p.with_suffix(".json.tmp")
tmp.write_text(txt, encoding="utf-8")
re_parsed = json.loads(tmp.read_text(encoding="utf-8"))
if len(re_parsed["assignments"]) != before + 1:
    sys.exit("refusing: reparse did not reconcile")
if list(re_parsed["assignments"]) != old_order + [EID]:
    sys.exit("refusing: order did not reconcile")
if re_parsed["assignments"][EID] != VALUE:
    sys.exit("refusing: the written reason did not survive the reparse")
tmp.replace(pla_p)
print(f"\nwritten at indent={indent}. assignments {before} -> {before + 1}.")
print("  The otherness axis now has one state it cannot file: a figure written")
print("  by an operator the audience is never shown. Recorded, not filled.")
