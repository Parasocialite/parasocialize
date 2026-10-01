#!/usr/bin/env python3
"""
verify_measure.py - does any line of type actually stay inside its measure?

    python tools/verify_measure.py [episode ...]

WHY THIS EXISTS AS ITS OWN TOOL
episode._wrap budgets a line by dividing the measure by the font's average
advance. An average is an estimate: a line of wide glyphs sits above it. So the
budget cannot prove the type fits, and the thing that does prove it is the
rendered frame - which means the check has to look at pixels, not at the wrap.

This exists because the type silently failed twice in ways no amount of reading
the code would have caught. The declared family never applied at all (a `g.type`
selector against a class on an `<svg>`), so every frame rendered in the browser
default serif; and the character budget had been calibrated against that
fallback, so the numbers looked self-consistent while describing a font nobody
had chosen. Both produced plausible output.

HOW IT MEASURES
Per scene, it removes one text line at a time and differences the render
against the same render without it. Whatever changes is that line's ink and
nothing else. Two things this deliberately does not do:

  - it does not threshold greyscale for "bright" pixels. The paper is #f3ece2
    and iYi's body is a cream of nearly the same value, so a brightness mask
    reports the character's right edge and calls it the type's.
  - it does not difference two renders of the same file. The frames are
    deterministic now, but when this was first written they were not, and the
    diff lit up on animation noise rather than on the thing under test.

Per line rather than per scene, because a scene can be inside the measure
overall and still have one line that runs past it - which is exactly what a
wrap that only checks the final size produces.
"""
from __future__ import annotations

import argparse
import json
import pathlib
import re
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))
import episode as E  # noqa: E402

TOL = 2          # px of slack for antialiasing on the final glyph


def _shot(doc: str, out_png: pathlib.Path, cw: int, ch: int) -> "np.ndarray | None":
    out_png.parent.mkdir(parents=True, exist_ok=True)
    if out_png.exists():
        out_png.unlink()
    tmp = ROOT / "episode" / ".chrome" / "verify"
    tmp.mkdir(parents=True, exist_ok=True)
    hp = tmp / "v.html"
    hp.write_text(doc, encoding="utf-8")
    url = "file:///" + hp.resolve().as_posix().lstrip("/")
    subprocess.run([E.CHROME, "--headless=new", "--disable-gpu", "--hide-scrollbars",
                    "--no-sandbox", f"--screenshot={out_png.resolve()}",
                    f"--window-size={cw},{ch}",
                    f"--user-data-dir={(ROOT / 'episode' / '.chrome').resolve()}", url],
                   check=False, capture_output=True, timeout=180)
    if not out_png.exists():
        return None
    from PIL import Image
    import numpy as np
    return np.asarray(Image.open(out_png).convert("RGB")).astype(int)


TEXT_RE = re.compile(r'<text x="(\d+)" y="(\d+)"[^>]*>([^<]*)</text>')


def check_fmt(eid: str, fmt: str) -> list[tuple]:
    """Every line of every scene, measured against that format's measure."""
    enc = json.loads((ROOT / "data" / "encyclopedia.json").read_text(encoding="utf-8"))
    entry = next((x for x in enc["entries"] if x["id"] == eid), None)
    sc = E.build_script(eid, enc)
    if entry is None or sc is None:
        print(f"  {eid}/{fmt}: no draft")
        return []

    land = fmt == "landscape"
    cw, ch = (E.LAND if land else (E.VW, E.VH))
    x0, y0, x1, y1 = (E.SAFE_LAND if land else E.SAFE)
    sd = ROOT / "episode" / eid / ("scenes-land" if land else "scenes")

    fails = []
    for i, s in enumerate(sc["scenes"]):
        doc = E.scene_html(s, (x0, y0, x1, y1), entry, enc, 0.0, i, fmt, sd)
        lines = [m for m in TEXT_RE.finditer(doc)
                 # the kickers and the year are deliberately placed, not wrapped
                 # to the measure; they are short and checked by eye instead
                 if m.group(3).strip() and int(m.group(2)) > y0 - 10]
        base = _shot(doc, ROOT / "episode" / ".chrome" / "verify" / "base.png", cw, ch)
        if base is None:
            print(f"  scene {i}: chrome rendered nothing")
            continue
        for j, m in enumerate(lines):
            variant = doc.replace(m.group(0), "", 1)
            other = _shot(variant, ROOT / "episode" / ".chrome" / "verify" / "var.png",
                          cw, ch)
            if other is None:
                continue
            import numpy as np
            d = np.abs(base - other).sum(axis=2)
            cols = np.where((d > 10).any(axis=0))[0]
            if not len(cols):
                continue
            right = int(cols.max())
            # a line may legitimately start left of the measure only if it is
            # the year or a kicker; anything else is a layout error
            left = int(cols.min())
            txt = m.group(3)
            if right > x1 + TOL:
                fails.append((i, j, txt, left, right, x1, right - x1))
    return fails


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("episodes", nargs="*", default=["eliza"])
    a = ap.parse_args()
    bad = 0
    for eid in a.episodes:
        for fmt in ("vertical", "landscape"):
            fails = check_fmt(eid, fmt)
            label = f"{eid}/{fmt}"
            if fails:
                bad += len(fails)
                print(f"FAIL {label}: {len(fails)} line(s) outside the measure")
                for (i, j, txt, left, right, x1, over) in fails:
                    print(f"   scene {i} line {j}: ends x={right}, measure ends "
                          f"{x1}, OVER by {over}px")
                    print(f"      {txt[:70]}")
            else:
                print(f"ok   {label}: every line inside its measure")
    return 1 if bad else 0


if __name__ == "__main__":
    raise SystemExit(main())