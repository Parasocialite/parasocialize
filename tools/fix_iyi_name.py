"""Normalise the name to iYi.

The rule is lowercase i, uppercase Y, lowercase i, always - it is a name, so it
does not take sentence capitalisation either. The build currently emits "Iyi"
241 times against 236 "iYi", which means the wrong form is very slightly the
majority and nobody would notice by sampling.

Deliberately narrow. Only a standalone capital-I "Iyi" is touched, and only
where it is not part of a slug, a path, a CSS class or a generated id:

    iyi-love.svg      untouched  (asset path)
    id="iyig97197"    untouched  (gradient id)
    class="iyi-pupil" untouched  (rig class)
    <p>Iyi is...</p>  ->  <p>iYi is...</p>
    title="About Iyi" ->  title="About iYi"

Run with --dry to see the inventory first.
"""
from __future__ import annotations

import pathlib
import re
import sys

DRY = "--dry" in sys.argv

# A capital-I "Iyi" that is not glued to a hyphen, underscore, or word character.
# The lookarounds are what keep asset paths and css classes out of it.
PAT = re.compile(r"(?<![\w\-])Iyi(?![\w\-])")

TARGETS = sorted(
    [p for p in pathlib.Path("tools").glob("*.py") if p.name != "fix_iyi_name.py"]
    + [p for p in pathlib.Path("data").glob("*.json")]
    + [p for p in pathlib.Path(".").glob("*.html")]
)

total = 0
rows = []
for p in TARGETS:
    try:
        t = p.read_text(encoding="utf-8")
    except Exception:
        continue
    n = len(PAT.findall(t))
    if n:
        rows.append((str(p), n))
        total += n
        if not DRY:
            p.write_text(PAT.sub("iYi", t), encoding="utf-8")

print(f"  {'DRY RUN - nothing written' if DRY else 'applied'}")
print(f"  files touched : {len(rows)}")
print(f"  replacements  : {total}")
for f, n in sorted(rows, key=lambda r: -r[1])[:18]:
    print(f"    {n:4}  {f}")

# what must NOT have changed
print("\n  guard checks (these should be untouched):")
for probe, label in ((r"iyi-love\.svg", "asset slug"),
                     (r'id="iyig', "gradient id"),
                     (r"iyi-pupil", "rig class"),
                     (r"iyi-blush", "rig class")):
    hits = 0
    for p in TARGETS:
        try:
            hits += len(re.findall(probe, p.read_text(encoding="utf-8")))
        except Exception:
            pass
    print(f"    {label:12} {probe:16} {hits} occurrences still present")
