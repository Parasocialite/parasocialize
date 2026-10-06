"""Place `marvel-club`, and give the `cog` register its first named instance.

`character/fictional-protagonist` - "somebody described in a book and therefore
available to an unlimited number of people at once" - which is also where
`nancy-drew` sits, and the pairing is deliberate: one written character reached
by letter, one reached by club.

`other: made`, and this is the case that proves the nancy-drew hole is a hole
rather than a rule. `made` needs the operator to be visible - "the transparency
is a design choice", the audience can see the person operating the thing. Here
they can: C. C. Beck drew the cover, Bill Parker wrote the script, Wilford H.
Fawcett was the executive editor, and all three are credited on the book.
`nancy-drew`'s ghostwriter was hidden behind a house pseudonym for 44 years and
`made` correctly refuses it. **Same category, one with the byline and one
without** - so the axis's `not` clause is doing real work and the nancy-drew
case is a genuine gap rather than a misfiling.

`rec: simulated`, and this is now the fourth `simulated` entry and the most
distinctive: `live-commentary` and `twitch-subs` are latency, `nancy-drew` is a
correspondence department, and this is a **physical artefact** - a card, a
certificate, a plastic ring - signed by a character who does not exist, issued
to a child who decoded the message himself. It is also the only one where the
performer of the reciprocity is *named on the artefact*.

Reads the committed file's indentation and key order from the committed bytes.
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

EID = "marvel-club"
VALUE = {
    "cat": "character",
    "sub": "fictional-protagonist",
    "other": "made",
    "rec": "simulated",
    "why": (
        "Filed `character/fictional-protagonist` - \"somebody described in a "
        "book and therefore available to an unlimited number of people at "
        "once\" - which is where `nancy-drew` also sits, and the pairing is "
        "deliberate: one written character reached by letter for fifty-four "
        "years, one reached by club membership. **Captain Marvel was reached by "
        "a code printed in the book the reader was holding**, which is the same "
        "unlimited-addressability with a transaction bolted to it.\n\n"
        "`other: made`, and **this is the case that proves the `nancy-drew` "
        "hole is a hole rather than a misfiling.** `made` requires the operator "
        "to be visible - \"the transparency is a design choice\", the audience "
        "can see the person operating the thing. Here they can: **C. C. Beck "
        "drew the cover, Bill Parker wrote the script, Wilford H. Fawcett was "
        "the executive editor, and all three are credited on the book.** "
        "`nancy-drew`'s ghostwriter was hidden behind a house pseudonym for 44 "
        "years and `made` correctly refuses it. **Same category, one with the "
        "byline and one without** - so the axis's `not` clause is doing real "
        "work and item 40's missing case is a genuine gap rather than a "
        "misfiling. That distinction matters, because it is the difference "
        "between \"the axis is wrong\" and \"the axis has one state it does not "
        "have\", and only the second is worth adding a member for.\n\n"
        "`rec: simulated`, and this is now the fourth `simulated` entry and the "
        "least like the other three. `live-commentary` and `twitch-subs` work "
        "by **latency** - a host reads a comment aloud within seconds. "
        "`nancy-drew` works by **post** - a correspondence department, weeks "
        "apart. **This one is a physical artefact**: a membership card, a "
        "certificate, a plastic ring, issued to a child who decoded the message "
        "himself. It is also **the only one where the performer of the "
        "reciprocity is named on the artefact** - \"issued under the actual "
        "authority of Benj J. Grimm, Grand Marshal (pro tem)\", a character, "
        "signing for an institution. The Dell club's certificate two doors down "
        "was authorised by G.T. Delacorte Jr., an actual person. **Two "
        "neighbouring children's clubs made the same promise and one of them "
        "kept the human out of it**, and that contrast is the evidence that the "
        "signature was a choice rather than a constraint.\n\n"
        "**And this is the entry that gives the `cog` register a named "
        "instance.** The register asks whether seeing the whole machine would "
        "change the attachment - \"if seeing it changes nothing about the "
        "attachment, it is Cog\" - and that test is satisfied here by the "
        "cheapest possible evidence: **the cipher was printed in the comic the "
        "reader was holding.** A reader who knows exactly how the private "
        "channel works is not thereby a different kind of reader. \"A cog that "
        "can see the machine is still a cog.\" The far end has its own "
        "machinery (a premium scheme - \"a color picture of Spy Smasher for a "
        "quarter\"), every member has their own (the decoding), and no child in "
        "any of the four adjacent clubs built any of them. **Until this entry "
        "the register had a definition, a test, a `not` and no instance**, which "
        "is the same state `undemanded` was in before `dear-kitty`, and a "
        "register with nothing behind it prints on the taxonomy page as though "
        "it were a finding."
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
enc_ids = {e["id"] for e in json.loads(enc_p.read_text(encoding="utf-8"))["entries"]}

old_order = list(committed["assignments"])
before = len(pla["assignments"])
subs = {(a["id"], s["id"]) for a in tax["attachment"] for s in a.get("sub", [])}
others = {m["id"] for m in tax["otherness"]["members"]}
recs = {m["id"] for m in tax["reciprocity"]["members"]}
unplaced = sorted(e for e in enc_ids if e not in pla["assignments"])

if EID in pla["assignments"]:
    sys.exit(f"{EID} is already placed; refusing to overwrite a written reason")
if EID not in enc_ids:
    sys.exit(f"{EID} is not in the corpus; refusing")
if (VALUE["cat"], VALUE["sub"]) not in subs:
    sys.exit(f"refusing: {VALUE['cat']}/{VALUE['sub']} is not a sub-category")
if VALUE["other"] not in others:
    sys.exit(f"refusing: other is not an otherness member")
if VALUE["rec"] not in recs:
    sys.exit(f"refusing: rec is not a reciprocity member")

sim = sorted(k for k, v in pla["assignments"].items() if v.get("rec") == "simulated")
print(f"  entry   : {EID}")
print(f"  shelf   : {VALUE['cat']}/{VALUE['sub']}   other={VALUE['other']}   rec={VALUE['rec']}")
print(f"  unplaced in corpus right now: {unplaced}")
print(f"  `simulated` before: {sim}")
print(f"  `simulated` after : {sorted(sim + [EID])}")
print(f"  assignments      : {before} -> {before + 1}")

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
print("  Both new registers now have a named instance argued in prose:")
print("  undemanded -> dear-kitty, nancy-drew   cog -> marvel-club,")
print("  american-gothic")
