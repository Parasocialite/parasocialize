"""Measure the character advance of the episode typeface, per size.

Regenerate when the face, the weights, or the sizes the scenes use change:

    python tools/measure_type.py

WHY A TABLE, AND WHY THIS TOOL WAS WRONG THREE TIMES FIRST
The budget episode._wrap uses has to be per size. Fraunces is served with an
optical-size axis and its advance genuinely moves: 0.488em at 30px down to
0.410em at 116px. A single constant is wrong at both ends - set from the large
end it lets small type overrun, set from the small end it sets display type 19%
too small.

Three earlier measurements said the advance was flat, and all three were
measuring the wrong face:

  1. The @font-face URL was hardcoded to '../../brand/fonts/'. The pages are
     written to episode/.chrome/calib/, where ../../ is episode/ - and
     episode/brand/fonts does not exist. The font never loaded and Chrome fell
     back. The tell was weights 600 and 800 measuring identically (0.4309 both):
     two different files cannot have identical metrics. Now the URL is computed
     from the real path, and they measure 0.4232 and 0.4492.
  2. A sweep read the text out of a fixed y-band while the type grew, catching
     progressively more of the glyph tops. It returned a smooth, plausible,
     entirely fictional curve.
  3. A banded sweep let large rows wrap onto several visual lines, so wide sizes
     were measured as wrapped text and read as narrower - which cancelled the
     real optical-size trend and made the result look flat again. A flat table
     was the artefact.

The lesson is in the assertions below: if the two weights agree to four decimal
places, or if the spread is implausibly small, the font is not loading and the
numbers are scenery.

THE TWO CONFIGURATIONS
Weight 800 with -0.02em tracking (hook, card, pivot, end) and weight 600 with
normal tracking (beat, why). Tracking moves every advance, so these are two
tables and not one.

TWO PROBES
PROBE is the longest real scene string - lowercase-heavy, and text _wrap is
actually asked to fit. PROBE_WIDE is a caps-and-punctuation worst case. The
per-size value is the larger of the two, so neither kind of text can overrun.

MARGIN
Each value is an average over ~90 characters, so an individual line sits above
or below it. 1.5% on top. The binding check is tools/verify_measure.py, which
measures rendered pixels; this only decides the starting size.
"""
from __future__ import annotations

import json
import pathlib
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
CHROME = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
OUT = ROOT / "tools" / "type_metrics.json"
FONTS = ROOT / "brand" / "fonts"

PROBE = ("In 1966 a programmer called ELIZA asked a woman to type at a keyboard "
         "and talk to her.")
PROBE_WIDE = "ELIZA, 1966. Elizabeth?"

SIZES = [30, 40, 46, 52, 60, 66, 76, 92, 104, 116]

# 90 chars * 0.5em * 116px = 5220px at the largest size. Sized from the probe,
# because a canvas that is too narrow silently returns its own width as the
# advance and that is indistinguishable from a real measurement.
CANVAS_W = 5600
MARGIN = 0.015

CONFIGS = {
    "w800": (800, -0.02),
    "w600": (600, 0.0),
}


def font_base() -> str:
    """Absolute file:// URL for the typeface directory.

    Absolute and computed, deliberately. The hardcoded relative path is what
    made this tool measure a fallback face for a whole run - see the module
    docstring. Computed means the tool fails loudly if the files move instead of
    quietly measuring whatever the browser substituted.
    """
    for f in ("fraunces-600.woff2", "fraunces-800.woff2"):
        if not (FONTS / f).exists():
            raise SystemExit(f"missing {FONTS / f}")
    return (FONTS / "fraunces-600.woff2").as_uri().rsplit("/", 1)[0] + "/"


def measure(weight: int, track: float, probe: str) -> dict[int, float]:
    """Advance per character at each size, one screenshot per size.

    Height scales with the type so a 116px row is never measured as wrapped
    text, and the ink is read from the band containing the line rather than from
    the whole page, so nothing else on the page can be mistaken for the type.
    """
    base = font_base()
    face = (f"@font-face{{font-family:'Fr';font-weight:600;"
            f"src:url('{base}fraunces-600.woff2') format('woff2')}}"
            f"@font-face{{font-family:'Fr';font-weight:800;"
            f"src:url('{base}fraunces-800.woff2') format('woff2')}}")
    tmp = ROOT / "episode" / ".chrome" / "calib"
    tmp.mkdir(parents=True, exist_ok=True)

    from PIL import Image
    import numpy as np

    out: dict[int, float] = {}
    for fs in SIZES:
        h = int(fs * 3) + 260
        ls = f"letter-spacing:{track * fs:.2f}px;" if track else ""
        baseline = fs + 150
        html = (f'<!DOCTYPE html><meta charset="utf-8"><style>*{{margin:0;padding:0}}'
                f'html,body{{width:{CANVAS_W}px;height:{h}px;background:#000}}'
                f'{face}text{{font-family:Fr;font-weight:{weight};white-space:pre;'
                f'fill:#fff}}</style>'
                f'<svg width="{CANVAS_W}" height="{h}">'
                f'<text x="30" y="{baseline}" font-size="{fs}" style="{ls}">'
                f'{probe}</text></svg>')
        hp = tmp / f"m{weight}_{len(probe)}_{fs}.html"
        hp.write_text(html, encoding="utf-8")
        png = tmp / f"m{weight}_{len(probe)}_{fs}.png"
        if png.exists():
            png.unlink()
        url = "file:///" + hp.resolve().as_posix().lstrip("/")
        subprocess.run([CHROME, "--headless=new", "--disable-gpu", "--hide-scrollbars",
                        "--no-sandbox", f"--screenshot={png.resolve()}",
                        f"--window-size={CANVAS_W},{h}",
                        f"--user-data-dir={ROOT / 'episode' / '.chrome'}", url],
                       check=False, capture_output=True, timeout=180)
        if not png.exists():
            raise SystemExit(f"chrome rendered nothing at fs={fs}")
        im = np.asarray(Image.open(png).convert("L")).astype(int)
        band = im[max(0, baseline - int(fs * 1.2)):baseline] > 100
        cols = np.where(band.any(axis=0))[0]
        if not len(cols):
            continue
        if int(cols.max()) >= CANVAS_W - 20:
            # Clipped: this row measures the canvas, not the text. Never keep
            # it - a clipped measurement cannot detect a typeface property.
            raise SystemExit(f"fs={fs}: probe overran {CANVAS_W}px; raise CANVAS_W")
        out[fs] = (int(cols.max() - cols.min())) / len(probe) / fs
    return out


def main() -> int:
    doc = {
        "_probe": PROBE,
        "_probe_wide": PROBE_WIDE,
        "_note": "em advance per character, per font size, measured from "
                 "brand/fonts/*.woff2 by tools/measure_type.py. Fraunces has an "
                 "optical-size axis so this genuinely varies with fs. Two "
                 "configurations because tracking shifts every advance. Each "
                 "entry is max(real prose probe, caps-and-punctuation probe) + "
                 "margin. Do not hand-edit; regenerate.",
    }
    tables = {}
    for label, (weight, track) in CONFIGS.items():
        real = measure(weight, track, PROBE)
        wide = measure(weight, track, PROBE_WIDE)
        if not real:
            raise SystemExit(f"{label}: nothing measured")
        per_size = {}
        for fs, v in real.items():
            per_size[fs] = round(max(v, wide.get(fs, v)) + MARGIN, 5)
        vals = list(per_size.values())
        spread = max(vals) - min(vals)
        print(f"  {label}: weight={weight} tracking={track:+.2f}em")
        print(f"     {len(per_size)} sizes, em {min(vals):.4f}..{max(vals):.4f}, "
              f"spread {spread:.4f}")
        tables[label] = per_size

    # THE ASSERTION THAT MATTERS. Identical advances across two different font
    # files means neither loaded. This is the check that would have caught the
    # broken path immediately.
    a = [tables["w800"][s] for s in sorted(tables["w800"])]
    b = [tables["w600"][s] for s in sorted(tables["w600"])]
    if all(abs(x - y) < 1e-4 for x, y in zip(a, b)):
        raise SystemExit(
            "w800 and w600 measured identically. The typeface is not loading - "
            "check font_base() and that brand/fonts/*.woff2 exist.")
    for label, t in tables.items():
        spread = max(t.values()) - min(t.values())
        if spread < 0.01:
            raise SystemExit(
                f"{label}: spread {spread:.4f} is implausibly small for a face "
                "with an optical-size axis. Expect ~0.08. Suspect the font is "
                "not loading rather than trusting a flat table.")
    doc["sizes"] = tables
    OUT.write_text(json.dumps(doc, indent=1), encoding="utf-8")
    print(f"\nwrote {OUT.relative_to(ROOT)}  ({OUT.stat().st_size} bytes)")
    print("  w800: " + "  ".join(f"{s}px={tables['w800'][s]:.4f}"
                                for s in sorted(tables['w800'])))
    print("  w600: " + "  ".join(f"{s}px={tables['w600'][s]:.4f}"
                                for s in sorted(tables['w600'])))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())