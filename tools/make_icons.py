#!/usr/bin/env python3
"""Build the site's icons from the Ayo geometry in tools/mascot.py.

The tab was still carrying a purple-and-orange swoosh-and-play-button mark that
predated the current design: a dark warm palette, an editorial serif, and a
mascot that is two connected warm eyes. Nothing about that icon belonged to the
site it was sitting in.

Rather than export the mascot (it is 118 units of animation, masks and CSS),
this redraws the same geometry at icon scale, where the animation and the
gradients that read as a face at 118px turn to mud:

  * flat warm fill instead of a gradient, because a 16px gradient is one colour
  * the bloom, the blush and the small highlights are dropped for the same
    reason, but the big highlight survives - it is what makes the eyes read as
    eyes rather than as two dots
  * pupils stay, slightly enlarged, because the pupils are the mark

The mascot geometry is not hardcoded twice on purpose: it is read out of
mascot.py's EYE/PALETTE constants if they are importable, and falls back to the
same numbers if they are not, so a change to the mascot shows up here.
"""
from __future__ import annotations

import pathlib
import sys

from PIL import Image, ImageDraw

ROOT = pathlib.Path(__file__).resolve().parent.parent
SS = 4  # supersample factor; downsampling is what antialiases the edges

# The mascot's own constants. Overridden from tools/mascot.py when importable.
BG = "#0b0b0d"          # --ink, the page ground
WARM_HI = "#ffe7c4"     # gradient top, kept flat at icon scale
WARM_LO = "#ff8f5e"     # gradient bottom
PUPIL = "#231009"       # the pupil
EYES = ((42, 42, 26), (76, 42, 26))    # (cx, cy, r) the two lobes
PUPILS = ((42, 45, 12.5), (76, 45, 12.5))
GLINTS = ((38.2, 40.7, 4.1), (45.8, 48.6, 1.9))
BLUSH = ((42, 55, 8, 4.4), (76, 55, 8, 4.4))

try:  # keep the icons honest if the mascot changes
    sys.path.insert(0, str(ROOT / "tools"))
    import mascot as _m  # type: ignore
    BG = getattr(_m, "BG", BG)
    EYES = tuple(getattr(_m, "EYES", EYES))
    PUPILS = tuple(getattr(_m, "PUPILS", PUPILS))
except Exception:
    pass


def _lerp(a, b, t: float) -> tuple[int, int, int]:
    """Mix two colours. Accepts '#rrggbb' or an already-parsed (r, g, b)."""
    def hx(c):
        return tuple(c) if not isinstance(c, str) else tuple(
            int(c.lstrip("#")[i:i + 2], 16) for i in (0, 2, 4))
    ca, cb = hx(a), hx(b)
    return tuple(int(round(ca[i] + (cb[i] - ca[i]) * t)) for i in range(3))


def _bounds():
    xs, ys = [], []
    for cx, cy, r in EYES:
        xs += [cx - r, cx + r]
        ys += [cy - r, cy + r]
    return min(xs), min(ys), max(xs), max(ys)


def render(n: int, bleed: float = 0.88) -> Image.Image:
    """Ayo at n x n. `bleed` is how much of the frame the eye pair fills.

    The mascot artboard is 118 wide but the eye pair only occupies 52 of those
    units vertically, so a naive crop is mostly empty. The pair is re-centred
    and scaled to `bleed` of the frame instead, with a floor so the 16px version
    still has a pixel of margin.
    """
    pad = int(round(n * (1 - bleed) / 2))
    box = max(6, n - pad * 2)
    x0, y0, x1, y1 = _bounds()
    ew, eh = x1 - x0, y1 - y0
    scale = box / max(ew, eh)
    dx = (n - ew * scale) / 2 - x0 * scale
    dy = (n - eh * scale) / 2 - y0 * scale

    def P(cx, cy):
        return ((cx * scale + dx), (cy * scale + dy))

    big = n * SS
    img = Image.new("RGB", (big, big), BG)
    d = ImageDraw.Draw(img)

    def PS(cx, cy):
        x, y = P(cx, cy)
        return (x * SS, y * SS)

    # warm body: one flat fill, the midpoint of the mascot gradient
    warm = _lerp(WARM_HI, WARM_LO, 0.45)
    for cx, cy, r in EYES:
        x, y = PS(cx, cy)
        d.ellipse([x - r * scale * SS, y - r * scale * SS,
                   x + r * scale * SS, y + r * scale * SS], fill=warm)

    # blush, kept very faint: it warms the shape without muddying it
    blush = _lerp(warm, (224, 83, 63), 0.30)
    for cx, cy, rx, ry in BLUSH:
        x, y = PS(cx, cy)
        d.ellipse([x - rx * scale * SS, y - ry * scale * SS,
                   x + rx * scale * SS, y + ry * scale * SS], fill=blush)

    for cx, cy, r in PUPILS:
        x, y = PS(cx, cy)
        d.ellipse([x - r * scale * SS, y - r * scale * SS,
                   x + r * scale * SS, y + r * scale * SS], fill=PUPIL)

    # the one highlight that survives: at 16px this is the difference between
    # "two eyes" and "two dots"
    for cx, cy, r in GLINTS:
        if n >= 32 or r >= 4:
            x, y = PS(cx, cy)
            rr = r * scale * SS * (1.0 if n >= 32 else 1.25)
            d.ellipse([x - rr, y - rr, x + rr, y + rr], fill="#fffaf2")

    return img.resize((n, n), Image.LANCZOS)


def write_svg(path: pathlib.Path) -> None:
    """A hand-written favicon.svg so vector-capable browsers skip the PNGs.

    No animation and no gradients: an icon is a static mark, and the same
    reasoning as the PNGs applies.
    """
    x0, y0, x1, y1 = _bounds()
    ew, eh = x1 - x0, y1 - y0
    s = 100.0 / max(ew, eh)
    dx = (100 - ew * s) / 2 - x0 * s
    dy = (100 - eh * s) / 2 - y0 * s

    def T(cx, cy):
        return cx * s + dx, cy * s + dy

    warm = "#%02x%02x%02x" % _lerp(WARM_HI, WARM_LO, 0.45)
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100" '
        f'width="100" height="100" role="img" aria-label="Parasocialize">',
        f"<title>Parasocialize</title>",
        f'<rect width="100" height="100" rx="20" fill="{BG}"/>',
    ]
    for cx, cy, r in EYES:
        x, y = T(cx, cy)
        parts.append(f'<circle cx="{x:.2f}" cy="{y:.2f}" r="{r * s:.2f}" fill="{warm}"/>')
    for cx, cy, rx, ry in BLUSH:
        x, y = T(cx, cy)
        parts.append(f'<ellipse cx="{x:.2f}" cy="{y:.2f}" rx="{rx * s:.2f}" '
                     f'ry="{ry * s:.2f}" fill="#e0533f" opacity=".3"/>')
    for cx, cy, r in PUPILS:
        x, y = T(cx, cy)
        parts.append(f'<circle cx="{x:.2f}" cy="{y:.2f}" r="{r * s:.2f}" fill="{PUPIL}"/>')
    x, y = T(*GLINTS[0][:2])
    parts.append(f'<circle cx="{x:.2f}" cy="{y:.2f}" r="{GLINTS[0][2] * s * 1.25:.2f}" '
                 f'fill="#fffaf2"/>')
    parts.append("</svg>")
    path.write_text("\n".join(parts) + "\n", encoding="utf-8")


def _save_png(img: Image.Image, path: pathlib.Path) -> None:
    """Flat art, so a small palette costs nothing visually and halves the file.

    The icons are circles on a ground: there is no gradient left in them and
    no photograph, so 256 colours is indistinguishable from 24-bit and takes the
    512px icon from ~23KB to a few KB. Dithering is off deliberately - it would
    put noise into the pupil edge, which is the one edge that matters at 16px.
    """
    q = img.convert("RGB").quantize(colors=256, method=Image.MEDIANCUT, dither=0)
    q.save(path, format="PNG", optimize=True)


def main() -> int:
    out = ROOT
    pngs = {}
    for n in (16, 32, 48, 64, 128, 180, 192, 256, 512):
        pngs[n] = render(n)

    # The legacy ICO, still what some bookmarks and older Windows ask for.
    # Save it from the 256px render: Pillow builds the size ladder by
    # downsampling the source, so handing it the 16px one yields a 1-entry ICO
    # that quietly loses its 32 and 48.
    ico = out / "favicon.ico"
    pngs[256].save(ico, format="ICO", sizes=[(16, 16), (32, 32), (48, 48)])
    print(f"  favicon.ico            {ico.stat().st_size:>7,} bytes  16/32/48")

    write_svg(out / "favicon.svg")
    print(f"  favicon.svg            "
          f"{(out / 'favicon.svg').stat().st_size:>7,} bytes  vector, no animation")

    for n, name in ((180, "apple-touch-icon.png"), (192, "icon-192.png"),
                    (512, "icon-512.png")):
        p = out / name
        _save_png(pngs[n], p)
        print(f"  {name:<22} {p.stat().st_size:>7,} bytes  {n}x{n}")

    # a maskable icon needs its art inside the safe circle, so re-render wide
    m = render(512, bleed=0.62)
    p = out / "icon-maskable.png"
    _save_png(m, p)
    print(f"  {p.name:<22} {p.stat().st_size:>7,} bytes  512x512, safe-circle")

    (out / "site.webmanifest").write_text(
        '{\n'
        '  "name": "Parasocialize",\n'
        '  "short_name": "Parasocialize",\n'
        '  "description": "One-sided relationships are just easier.",\n'
        f'  "start_url": "https://www.parasocialize.com/",\n'
        f'  "scope": "https://www.parasocialize.com/",\n'
        f'  "display": "standalone",\n'
        f'  "background_color": "{BG}",\n'
        f'  "theme_color": "{BG}",\n'
        f'  "icons": [\n'
        f'    {{"src": "/icon-192.png", "sizes": "192x192", "type": "image/png"}},\n'
        f'    {{"src": "/icon-512.png", "sizes": "512x512", "type": "image/png"}},\n'
        f'    {{"src": "/icon-maskable.png", "sizes": "512x512", '
        f'"type": "image/png", "purpose": "maskable"}}\n'
        f'  ]\n'
        '}\n', encoding="utf-8")
    print("  site.webmanifest       written")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
