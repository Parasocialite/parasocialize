"""Add the `cog` register. Named by the author, from their Uncle Pat.

"We are all just a cog in the machine as my Uncle Pat used to say."

That is a better name than anything in a thesaurus because it came from inside the
thing. A cog is a working part of a mechanism: it transmits force, it receives
it, it does not choose the shape of the machine, and the machine runs fine
without any one tooth. Which is the parasocial condition exactly - except that the
person holding the tie usually cannot see the machine.

**Two ways this name misreads, and the definition is where both are managed.**

  A cog is defined by FUNCTION, not by feeling. Attachments are defined by
  feeling. Left alone, "cog" implies role-fulfilment - machinery rather than
  meaning - which is the flattening this project exists to refuse. So the `not`
  rules that out in terms: being a part is a claim about SCALE, not about
  importance.

  A cog does not know it is a cog. The line's irony is usually that the machine is
  invisible, and this site's whole method is seeing it - identifying and
  reflecting on purpose. Read literally, "cog" would be nearly the opposite of
  what the author is doing. So the mechanism carries the correction: a cog that
  can see the machine is still a cog, and that is the register rather than the
  problem.

Provenance is recorded because the file's method is to record where things come
from, and this one has a person attached to it rather than a citation.

Added EMPTY on purpose, like `undemanded`. verify_taxonomy.py reports it as a
deliberate hole, which is the correct state for a member with no instance yet.

Asserts the register count, the id set and the top-level keys before and after.
"""
import json
import pathlib
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ROOT = pathlib.Path(r"C:\Users\paras\Documents\Default Project\parasocialize")
APPLY = "--apply" in sys.argv

MEMBER = {
    "id": "cog",
    "name": "Cog",
    "def": ("You are one working part of something that turns whether or not you "
            "are watching it. The far end has its own machinery; so does every "
            "other viewer, and you are all meshing with each other in a device "
            "none of you built. Wry rather than diminished, which is the whole "
            "difference between this register and a complaint."),
    "test": ("Would you call it the same if you could see the whole machine? If "
             "seeing it changes nothing about the attachment, it is Cog. If "
             "seeing it would break it, the problem is somewhere else - a harm, "
             "or a contest, or a channel that permits a reply."),
    "not": ("Not a reduction. Being a part is a claim about SCALE, not about "
            "importance, and a cog is not diminished by being small - the "
            "mechanism does not work without it. Not Harm: nothing is paid and "
            "nobody is charged. Not the Reciprocal Edge: the reply is not "
            "available here at all, which is the definition rather than the "
            "trouble. And emphatically not anonymity or insignificance: the "
            "question is never whether the tooth matters."),
    "mechanism": ("Scale, and the fact that the machine is the shared one. Every "
                  "viewer is turning against every other viewer and none of them "
                  "designed it, so the attachment is simultaneously private and a "
                  "collective artefact. **A cog that can see the machine is still "
                  "a cog** - which is the register, and not the problem."),
    "note": ("Named by the author, after their Uncle Pat: 'we are all just a cog in "
             "the machine'. Provenance is recorded here rather than in a citation "
             "field because this one has a person attached to it. Added EMPTY on "
             "purpose, like `undemanded`, and the emptiness is reported rather "
             "than filled. The name carries two misreadings - that a cog is "
             "defined by function rather than feeling, and that a cog does not know "
             "it is a cog - and both are handled in the definition rather than by "
             "softening the word, because the word is the good part."),
}

p = ROOT / "data" / "taxonomy.json"
tax = json.loads(p.read_text(encoding="utf-8"))
before = len(tax.get("register", []))
before_ids = sorted(m.get("id") for m in tax.get("register", []) if isinstance(m, dict))
before_keys = sorted(tax)

if any(isinstance(m, dict) and m.get("id") == MEMBER["id"]
       for m in tax.get("register", [])):
    print(f"  register {MEMBER['id']!r} already present; nothing to do")
    raise SystemExit(0)

print(f"  register members: {before} -> {before + 1}")
print(f"  adding          : {MEMBER['name']}  ({MEMBER['id']})")
for k in ("def", "test", "not", "mechanism"):
    print(f"  {k:<10} {MEMBER[k][:96]}...")

missing = {"def", "test", "not", "mechanism", "name", "id"} - set(MEMBER)
if missing:
    sys.exit(f"refusing: missing {sorted(missing)} - verify_taxonomy.py requires "
             f"a test and a not of real length")
if len(MEMBER["test"]) < 40 or len(MEMBER["not"]) < 40:
    sys.exit("refusing: the test or the not is too short to exclude anything")

if not APPLY:
    print("\ndry run. re-run with --apply")
    raise SystemExit(0)

tax["register"].append(MEMBER)
tax["register"].sort(key=lambda m: (m.get("name") or "").lower())

after_ids = sorted(m.get("id") for m in tax.get("register", []) if isinstance(m, dict))
if len(tax.get("register", [])) != before + 1:
    sys.exit(f"refusing to write: register count {before} -> {len(tax['register'])}")
if set(before_ids) - set(after_ids):
    sys.exit("refusing to write: an existing register id was lost")
if set(after_ids) != set(before_ids) | {MEMBER["id"]}:
    sys.exit("refusing to write: the id set changed by more than one addition")
if sorted(tax) != before_keys:
    sys.exit("refusing to write: top-level keys changed")

tmp = p.with_suffix(".json.tmp")
tmp.write_text(json.dumps(tax, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
re_parsed = json.loads(tmp.read_text(encoding="utf-8"))
if len(re_parsed.get("register", [])) != before + 1:
    sys.exit("refusing to write: reparse did not reconcile")
tmp.replace(p)
print(f"\nwritten. register {before} -> {before + 1}. Empty, and empty is correct.")
print("  Cog is the second register with no instance. A register axis with two")
print("  empty members and four filled ones is honest about what the corpus")
print("  does not have, which is more than it was.")
