"""Derive ROOT from __file__ in the tools written in this session.

Twenty-seven tools in this repo hardcode the absolute path, so hardcoding is the
existing convention and this is not a deviation from it. The finding is that the
convention is a landmine: `close_locator_gaps.py` shipped with a literal missing
the word "Documents", so it raised FileNotFoundError on a file that exists, is
tracked and is readable from the shell - and the tool that displayed the line
**showed the word that was not in it**, so `read` said the path was right and the
bytes said it was not. Only `len(str(ROOT))` against the expected 54 found it.

Rewriting all twenty-seven working tools is unrequested churn with real risk, so
this converts only the nine written in this session and leaves the rest, with the
hazard recorded rather than acted on globally.

Asserts one replacement per file and that the file still compiles.
"""
import pathlib
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ROOT = pathlib.Path(__file__).resolve().parent.parent
TOOLS = ROOT / "tools"

# Only the ones this session authored.
TARGETS = [
    "add_dear_kitty.py", "correct_dear_kitty.py", "add_nancy_drew.py",
    "add_nancy_drew_placement.py", "add_krapp_last_tape.py",
    "add_krapp_placement.py", "add_american_gothic.py",
    "add_american_gothic_placement.py", "add_marvel_club.py",
    "add_marvel_club_placement.py", "add_queen_for_a_day.py",
    "add_queen_for_a_day_placement.py",
]

DERIVED = "ROOT = pathlib.Path(__file__).resolve().parent.parent"

changed, already, missing = [], [], []
for name in TARGETS:
    p = TOOLS / name
    if not p.exists():
        missing.append(name)
        continue
    src = p.read_text(encoding="utf-8")
    lines = src.splitlines(keepends=True)
    hits = [i for i, l in enumerate(lines) if "ROOT = pathlib.Path(r\"" in l]
    if not hits:
        already.append(name)
        continue
    if len(hits) != 1:
        sys.exit(f"refusing: {name} has {len(hits)} ROOT assignments, expected 1")
    i = hits[0]
    # Three shapes exist in this repo for the same assignment:
    #   ROOT = pathlib.Path(r"C:\...")          - one line, closed on the same line
    #   ROOT = pathlib.Path(r"C:\..."\n          - bare string, closing paren below
    #                     )
    # Anything else is not a form this script should guess at.
    end = i
    if lines[i].rstrip().endswith(")"):
        pass
    elif i + 1 < len(lines) and lines[i + 1].strip().startswith(")"):
        end = i + 1
    else:
        sys.exit(f"refusing: {name} line {i+1} is not a recognisable ROOT form: "
                 f"{lines[i].strip()!r}")
    new = DERIVED + "\n"
    lines[i:end + 1] = [new]
    out = "".join(lines)
    # the literal must be gone and the derived form present
    if 'ROOT = pathlib.Path(r"' in out:
        sys.exit(f"refusing: {name} still contains a hardcoded ROOT")
    if out.count(DERIVED) != 1:
        sys.exit(f"refusing: {name} now has {out.count(DERIVED)} derived ROOTs")
    compile(out, str(p), "exec")          # it must still parse
    p.write_text(out, encoding="utf-8")
    changed.append(name)

print(f"  converted to a derived ROOT : {len(changed)}")
for n in changed:
    print(f"    {n}")
if already:
    print(f"  already derived            : {len(already)}")
    for n in already:
        print(f"    {n}")
if missing:
    print(f"  NOT FOUND (refused silently would hide this): {missing}")

# Prove the repo-wide state rather than asserting it is fine.
hard = []
for p in sorted(TOOLS.glob("*.py")):
    if 'ROOT = pathlib.Path(r"' in p.read_text(encoding="utf-8", errors="replace"):
        hard.append(p.name)
print(f"\n  tools still hardcoding ROOT repo-wide: {len(hard)}")
print(f"    (pre-existing convention, not this session's; recorded, not rewritten)")
