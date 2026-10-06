"""Place `american-gothic`, and note where the shelf choice is contestable.

`character/historic-as-character` - "a real person who has been flattened into a
type" - over `character/fictional-protagonist`, and the choice is recorded as
contestable rather than settled, because the entry's own point is that the two
real people were painted AS a type on purpose.

The honest counter-argument, kept here so it can be argued with later: the tie
is to the painted pair, who are not real people, and the object is a painting
available to unlimited viewers, which is `fictional-protagonist`'s shape.
`historic-as-character` wins because Wood said outright that the pair were
"types of people I have known all my life" and deliberately lengthened a real
face until it was unrecognisable - the flattening is documented and intended,
which is the shelf's whole definition. But an entry about two models flattened
into a national type is a close enough fit that the alternative is defensible,
and this is the placement to revisit if the axis grows.

`other: made` is set, and this time it genuinely fits rather than being a
compromise. `made` is "an object with a face, a voice or an operator... a
character who is performed by somebody the audience can see if they look",
and its test is "is somebody working it?". Wood is visibly operating the thing:
he modelled his dentist on a chair in a dental office, costumed both figures in
a Sears order, painted his sister's face long on purpose, and then for fifty
years posed in overalls identical to the figure's. The transparency condition
holds.

**And this entry is `made` where `krapp-last-tape` could not be, which makes
the pair a controlled comparison rather than two more unplaceable cases.** Both
are figures with a person behind them. In American Gothic the person behind is
continuously, publicly visible - that is what makes it `made`. In Krapp the
person behind is a recording, thirty years old and four words short, and the
audience is not shown him. Same category, opposite conditions, and the axis
only has a word for one of them.

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

EID = "american-gothic"
VALUE = {
    "cat": "character",
    "sub": "historic-as-character",
    "other": "made",
    "why": (
        "Filed `character/historic-as-character` - \"a real person who has been "
        "flattened into a type\" - and **the placement is contestable, so it is "
        "recorded as contestable.** The honest counter-argument: the tie is to "
        "the *painted pair*, who are not real people, and the object is a "
        "painting available to unlimited viewers at once, which is "
        "`fictional-protagonist`'s shape. `historic-as-character` wins because "
        "Wood said outright that the pair were \"types of people I have known "
        "all my life\" and deliberately stretched a real face until it could not "
        "be recognised - **the flattening is documented and intended, which is "
        "that shelf's whole definition.** But an entry about two models "
        "flattened into a national type sits close enough to the boundary that "
        "the alternative is defensible. This is the placement to revisit if the "
        "axis grows.\n\n"
        "`other: made`, and this one genuinely fits rather than being a "
        "compromise. `made` is \"an object with a face, a voice or an operator: "
        "a puppet, a doll, an automaton, a character who is performed by "
        "somebody the audience can see if they look\", and its test is \"is "
        "somebody working it?\". **Wood is continuously, publicly operating the "
        "thing.** He modelled his dentist on a chair in a dental office, "
        "costumed both figures from a Sears mail-order order, painted his "
        "sister's face long on purpose so she could not be recognised, and then "
        "for the rest of his career posed for photographs in overalls identical "
        "to the figure's. The transparency condition `made` requires - the "
        "audience can see the person operating the thing - holds here, and it is "
        "the whole entry.\n\n"
        "**And this is what makes it the control for `krapp-last-tape` rather "
        "than a third unplaceable case.** Both are a figure with a person "
        "behind it. In `american-gothic` the person behind is visible and stays "
        "visible, which is what `made` is for. In `krapp-last-tape` the person "
        "behind is a recording thirty years old and four words short, and the "
        "audience is never shown him - so `made`'s mechanism refuses it, since "
        "it presumes the figure answers. **Same category, opposite conditions, "
        "and the axis has a word for exactly one of them.** That is the "
        "strongest form of the argument that a ninth member is needed, and it "
        "is now demonstrable from two adjacent entries rather than asserted.\n\n"
        "Reciprocity left unset. The condition here is `directed`, which is the "
        "corpus default. Worth noting that `undemanded` is *also* defensible - "
        "nothing was asked of the painted pair and the tie is one-sided - and is "
        "not set for the reason the entry itself gives: Wood drew a \"storm of "
        "protest from Iowa farm wives\", one of whom threatened to smash her "
        "head, and the dentist denied the tie for five years. **Undemanded is "
        "about nobody wanting anything; it is not about nobody objecting.**"
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

if EID in pla["assignments"]:
    sys.exit(f"{EID} is already placed; refusing to overwrite a written reason")
if EID not in enc_ids:
    sys.exit(f"{EID} is not in the corpus; refusing")
if (VALUE["cat"], VALUE["sub"]) not in subs:
    sys.exit(f"refusing: {VALUE['cat']}/{VALUE['sub']} is not a sub-category")
if VALUE.get("other") not in others:
    sys.exit(f"refusing: other={VALUE.get('other')!r} is not an otherness member")
if "rec" in VALUE:
    sys.exit("refusing: reciprocity is deliberately unset here")

print(f"  entry   : {EID}")
print(f"  shelf   : {VALUE['cat']}/{VALUE['sub']}   (contestable, recorded)")
print(f"  other   : {VALUE['other']}  <- fits, unlike krapp's")
print(f"  rec     : deliberately unset (undemanded also defensible; not set)")
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
print("  Every medium in MEDIA now has at least one entry behind it.")
