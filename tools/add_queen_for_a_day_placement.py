"""Place `queen-for-a-day`.

`persona/presenter`, because that shelf's own definition names the case: "The
one who addresses you directly, by name, in second person. Newsreaders,
weathermen, **game show hosts**". Jack Bailey is the third of the three the
shelf lists by name, and the format's first move is a direct address to the
audience - "Would YOU like to be Queen for a Day?" - answered in chorus.

`other: made`. The object of the tie is a host performing a role the audience
knows is a role, which is `made`'s case rather than `played-role`'s: `made`'s
`not` excludes "a live person pretending to be fictional", and Bailey was
never pretending to be a fictional character - he was visibly an emcee, which
is exactly the transparency the member asks for.

`rec: simulated`, and the `why` distinguishes two different performances rather
than blurring them:
  - aimed at the AUDIENCE - the listeners believed their applause decided, and
    a needle decided instead. "Reciprocity performed rather than felt": the far
    end did something whose purpose was to produce the appearance that the
    audience's feelings were received, and nobody on the other side had an
    interior in the matter.
  - aimed at the SPONSOR - the crowned contestant performed gratitude for a
    commercial, which is `simulated` too but in the opposite direction, and the
    corpus has no axis for a bond that runs from the pitied party to the
    audience. **Recorded rather than modelled.**

Reads the committed file's indentation and key order from the committed bytes.
"""
import collections
import json
import pathlib
import subprocess
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ROOT = pathlib.Path(__file__).resolve().parent.parent
APPLY = "--apply" in sys.argv

EID = "queen-for-a-day"
VALUE = {
    "cat": "persona",
    "sub": "presenter",
    "other": "made",
    "rec": "simulated",
    "why": (
        "Filed `persona/presenter`, and that shelf's own definition names the "
        "case: \"The one who addresses you directly, by name, in second person. "
        "Newsreaders, weathermen, **game show hosts**.\" Jack Bailey is the third "
        "of the three the definition lists, and the format's first move is a "
        "direct address answered in chorus - \"Would YOU like to be Queen for a "
        "Day?\" / \"YES!!!!\" shouted the audience. **The show opens by asking "
        "the whole audience a question at once**, which is the most efficient "
        "parasocial address in this corpus and it does it with one word: YOU. "
        "`persona/creator` was the alternative and is wrong - that shelf is a "
        "person with \"a place in your week\" producing regular output, and the "
        "audience's attachment here is to being spoken to rather than to the "
        "work.\n\n"
        "`other: made`, and this is `made` rather than `played-role` for the "
        "reason `made`'s own `not` gives: it excludes \"a live person pretending "
        "to be fictional\", and **Bailey was never pretending to be a fictional "
        "character - he was visibly an emcee**, which is precisely the "
        "transparency the member asks for. Same distinction that "
        "`american-gothic` turns on, where Wood was continuously and publicly "
        "operating the thing.\n\n"
        "`rec: simulated`, and the reason distinguishes two performances rather "
        "than blurring them into one.\n"
        "- **Aimed at the audience.** The listeners believed their applause "
        "decided, and a needle decided instead - \"She who received the greatest "
        "amount of applause as registered by the 'applause meter' was Queen for "
        "a Day.\" That is the axis's test exactly: the far end did something "
        "**whose purpose was to produce the appearance of a bond** and nobody "
        "behind it had an interior in the matter. And the sharper version is on "
        "the entry: in radio the home listener could not applaud into the device "
        "at all, so the instrument was pointed at the studio, not at them.\n"
        "- **Aimed at the sponsor.** The crowned contestant was required to sit "
        "on a throne and \"listen to a five minute in-show commercial about all "
        "the consumer items that she'd just won, while pretending to be really "
        "excited and thankful\" - performed gratitude after having asked in "
        "public for surgery for her child. That is `simulated` too, but running "
        "the other way, and **the corpus has no axis for a bond that goes from "
        "the pitied party to the audience for it.** Recorded rather than modelled; "
        "the fourth axis was recovered from the author's own 2019 character "
        "chart and a fourth-fiftieth direction is not a thing a tool should "
        "invent.\n\n"
        "**Why this is the strongest `cog` case in the corpus and the register's "
        "second named instance.** `marvel-club` argues the structure - a cipher "
        "printed in the book the reader was holding. **This one has the "
        "mechanism in hardware**: a woman's hardship was narrated, a room's "
        "reaction was converted into a reading, and the reading decided. The "
        "register asks whether seeing the whole machine changes the attachment, "
        "and the answer here is available to every viewer for free on the "
        "network's own schedule - 30 to 45 minutes \"so they could sell more "
        "commercial time at the then astounding rate of $4000 per minute\". "
        "**The sorrow slot was sold by the minute, and the receipt is the "
        "running order.**"
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

if EID in pla["assignments"]:
    sys.exit(f"{EID} is already placed; refusing to overwrite a written reason")
if EID not in enc_ids:
    sys.exit(f"{EID} is not in the corpus; refusing")
if (VALUE["cat"], VALUE["sub"]) not in subs:
    sys.exit(f"refusing: {VALUE['cat']}/{VALUE['sub']} is not a sub-category")
if VALUE["other"] not in others:
    sys.exit("refusing: other is not an otherness member")
if VALUE["rec"] not in recs:
    sys.exit("refusing: rec is not a reciprocity member")

sim = sorted(k for k, v in pla["assignments"].items() if v.get("rec") == "simulated")
pres = sorted(k for k, v in pla["assignments"].items()
              if f"{v['cat']}/{v['sub']}" == "persona/presenter")
unplaced = sorted(e for e in enc_ids if e not in pla["assignments"])
print(f"  entry   : {EID}")
print(f"  shelf   : {VALUE['cat']}/{VALUE['sub']}   other={VALUE['other']}   rec={VALUE['rec']}")
print(f"  persona/presenter residents: {pres}")
print(f"  `simulated` after: {sorted(sim + [EID])}")
print(f"  unplaced right now: {unplaced}")
print(f"  assignments: {before} -> {before + 1}")

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
print("  radio is no longer two 1930 entries.")
