#!/usr/bin/env python3
"""
plate.py - a designed title plate for every encyclopedia entry that has no
photograph it is entitled to use.

WHY A PLATE AND NOT A PHOTO
The database is 175 entries and it splits by age, not by difficulty:

    pre-1900        24   public domain, and the deepest well there is
    1900-1949       18   mostly public domain (the Library of Congress is
                        pre-1929)
    1950-1999       54   THIS is the hard band. The photograph a reader wants is
                        a frame of the show or the product, which is exactly
                        what is not licensed. Creative Commons here is thin and
                        generic: a stadium, a screen, a queue
    2000+           79   the existing pipeline serves this band already

A stock photograph is a lie of a different kind. A picture of a crowd that is
not the crowd, on a page about a specific show, teaches the reader that the site
does not know what the entry is about. The Top 8 already settled this: two of its
eight ranks are type plates, and they read as deliberate rather than as a missing
file. This makes that a first-class output rather than a fallback.

WHAT MAKES A PLATE GOOD
It has to be about the entry, not near it, and impossible to mistake for a
photograph. So every plate is composed from that entry's own record:

    the title   in the site's serif, as a title card would set it
    the year    large, because the timeline is the argument
    the lane    its own colour from enc.lanes, used consistently
    a mark      chosen by `kind`, so the plate says what sort of thing this is
                before you read a word - and the atlas is already coloured by
                kind, so the visual language is shared across the site

LAYOUT IS A GRID, NOT A COMPOSITION
The first version scattered a colour block by hash and set the title in whatever
space was left. Rendered, it overflowed the plate on eleven of the first twelve
entries and ran under the mark on most of them: the line budget assumed 11px per
character at 96px type, which is off by about four times.

So the plate is now a fixed two-column grid with a measured text column:

    88px margin, a rule at x=730
    LEFT  88..700   title, accent rule, lane, kind
    RIGHT 760..1112 the mark, the year under it

Nothing is placed by hash any more except the mark's internal geometry, which is
the one place variation is wanted. The texture is a faint grid and a soft radial
glow behind the mark in the lane colour - a deliberate element, rather than a
floating rectangle that happened to land over the title.

TEXT IS MEASURED, NOT GUESSED
Lines are wrapped with an advance-width table for Georgia bold rather than a
characters-per-line guess, and the font size steps down as the title gets longer
so a four-word title and a fourteen-word title both fill the column instead of
one overflowing and the other floating.

Fonts are declared as stacks, not as the webfonts. A plate loads through
`<img src>`, and an SVG in an `<img>` cannot fetch a stylesheet or a webfont, so
Fraunces would silently fall back to the system serif anyway. Declaring Georgia
and Consolas directly means the plate looks the same in every browser.

  python tools/plate.py            # write any plate that is missing
  python tools/plate.py --check    # report only, write nothing
  python tools/plate.py --only tay,grief
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
ENC = ROOT / "data" / "encyclopedia.json"
OUT = ROOT / "img" / "plate"

W, H = 1200, 675
PAD = 88
COL_RULE = 730
L_W = COL_RULE - PAD - 28          # 614 of usable width
R_X0, R_X1 = 780, W - PAD

INK = "#0b0b0d"
PAPER = "#f3ece2"
DIM = "#9a8672"
WARM = "#ffe7c4"
SERIF = 'Georgia,"Times New Roman",serif'
MONO = 'Consolas,"Courier New",monospace'

# ---------------------------------------------------------------- measurement
# Georgia Bold advance widths as a fraction of the em. Good to about 3%, which
# with a safety margin is enough to stop a plate overflowing.
_NARROW = set("iljtfrI.,;:'\"!|()[]`")
_WIDE = set("mwMW@%—")
_UPPER = set("ABCDEFGHJKLNOPQRSTUVXYZ&")


def _adv(ch: str) -> float:
    if ch == " ":
        return 0.27
    if ch in _NARROW:
        return 0.31
    if ch in _WIDE:
        return 0.90
    if ch in _UPPER:
        return 0.70
    if ch.isdigit():
        return 0.56
    return 0.53


def _measure(s: str, fs: float) -> float:
    return sum(_adv(c) for c in s) * fs


def _wrap(text: str, fs: float, width: float) -> list[str]:
    """Greedy wrap on measured width. Returns at least one line."""
    words = str(text).split()
    if not words:
        return [""]
    lines, cur = [], []
    for wd in words:
        trial = cur + [wd]
        if cur and _measure(" ".join(trial), fs) > width:
            lines.append(" ".join(cur))
            cur = [wd]
        else:
            cur = trial
    lines.append(" ".join(cur))
    return lines


def _fit(text: str, width: float, max_lines: int = 3, max_block: float = 190.0):
    """Step the size down until the title fits.

    Three constraints, and the third is the one that was missing. Bounding the
    line COUNT is not enough: a four-line title at 92px is 405px tall, legal by
    line count and enough to push the lane and kind lines off the bottom of the
    plate. So the block is bounded by height too.

    The size CEILING is deliberately low. Rendered into an entry page, the plate
    sits about fifty pixels below the page's own <h1>, and at 92px the title
    inside the image was larger than the heading above it - the reader read the
    same words twice and the second time was louder. Capping at 64px makes the
    plate subordinate to the heading on an entry page while still reading at
    about 21px on a 400px card, which is where it has to work hardest.
    """
    for fs in (64, 58, 52, 47, 42, 38):
        lines = _wrap(text, fs, width)
        if len(lines) <= max_lines and all(
                _measure(l, fs) <= width for l in lines) \
                and len(lines) * fs * 1.12 <= max_block:
            return fs, lines
    fs = 34
    return fs, _wrap(text, fs, width)[:max_lines]


def _esc(s) -> str:
    return (str(s).replace("&", "&amp;").replace("<", "&lt;")
            .replace(">", "&gt;").replace('"', "&quot;"))


def _seed(s: str) -> int:
    return int(hashlib.sha256(s.encode("utf-8")).hexdigest()[:12], 16)


# --------------------------------------------------------------------- marks
def mark_event(cx, cy, r, s):
    """An event radiates."""
    n = 9 + s % 5
    rot = (s >> 3) % 45
    o = [f'<circle cx="{cx}" cy="{cy}" r="{r*0.28:.1f}" fill="{MARK_INK}"/>']
    for i in range(n):
        a = 2 * math.pi * i / n + rot * math.pi / 180
        r0, r1 = r * 0.44, r * (0.80 + ((s >> (i % 7)) % 5) * 0.05)
        o.append(f'<line x1="{cx + r0*math.cos(a):.1f}" y1="{cy + r0*math.sin(a):.1f}" '
                 f'x2="{cx + r1*math.cos(a):.1f}" y2="{cy + r1*math.sin(a):.1f}" '
                 f'stroke="{MARK_INK}" stroke-width="{3 + i % 3}" stroke-linecap="round"/>')
    return "".join(o)


def mark_mechanism(cx, cy, r, s):
    """A mechanism is a diagram: nodes, and some of the edges between them."""
    n = 6 + s % 4
    pts = []
    for i in range(n):
        a = 2 * math.pi * i / n - math.pi / 2
        rr = r * (0.50 + ((s >> (i % 5)) % 4) * 0.12)
        pts.append((cx + rr * math.cos(a), cy + rr * math.sin(a)))
    e = []
    for i in range(n):
        for j in range(i + 2, n):
            if ((s >> ((i * 3 + j) % 11)) & 3) == 0:
                e.append(f'<line x1="{pts[i][0]:.1f}" y1="{pts[i][1]:.1f}" '
                         f'x2="{pts[j][0]:.1f}" y2="{pts[j][1]:.1f}" '
                         f'stroke="{MARK_INK}" stroke-width="1.7" opacity=".5"/>')
    d = "".join(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{5 if i % 3 else 7.5}" '
                f'fill="{INK}" stroke="{MARK_INK}" stroke-width="2.6"/>'
                for i, (x, y) in enumerate(pts))
    return "".join(e) + d


def mark_person(cx, cy, r, s):
    """A person, as a portrait frame. Never a face - a frame, which is honest."""
    w, h = r * 1.2, r * 1.55
    o = []
    for i, f in enumerate((1.0, 0.76, 0.52)):
        o.append(f'<rect x="{cx - w*f/2:.1f}" y="{cy - h*f/2:.1f}" '
                 f'width="{w*f:.1f}" height="{h*f:.1f}" fill="none" '
                 f'stroke="{MARK_INK}" stroke-width="{3.6 - i*0.8}" '
                 f'opacity="{1 - i*0.3:.2f}"/>')
    o.append(f'<rect x="{cx - w/2:.1f}" y="{cy - h/2:.1f}" width="{w:.1f}" '
             f'height="{h:.1f}" fill="none" stroke="{MARK_INK}" stroke-width="1.2" '
             f'stroke-dasharray="3 6" opacity=".45"/>')
    return "".join(o)


def mark_work(cx, cy, r, s):
    """A work: a spine and a title block, the way a book or a card reads."""
    w, h = r * 1.3, r * 1.5
    x, y = cx - w / 2, cy - h / 2
    o = [f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" '
         f'fill="none" stroke="{MARK_INK}" stroke-width="3.2"/>',
         f'<line x1="{x + w*0.24:.1f}" y1="{y:.1f}" x2="{x + w*0.24:.1f}" '
         f'y2="{y + h:.1f}" stroke="{MARK_INK}" stroke-width="2.6"/>']
    for i in range(5):
        ly = y + h * (0.26 + i * 0.135)
        o.append(f'<line x1="{x + w*0.34:.1f}" y1="{ly:.1f}" '
                 f'x2="{x + w*(0.94 if (s >> i) & 1 else 0.74):.1f}" y2="{ly:.1f}" '
                 f'stroke="{MARK_INK}" stroke-width="2.2" opacity="{0.95 - i*0.13:.2f}"/>')
    return "".join(o)


def mark_study(cx, cy, r, s):
    """A study or paper: a citation block, indented and ragged."""
    w, h = r * 1.42, r * 1.5
    x, y = cx - w / 2, cy - h / 2
    o = [f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" '
         f'fill="none" stroke="{MARK_INK}" stroke-width="3.2"/>']
    for i in range(7):
        ly = y + h * (0.15 + i * 0.105)
        o.append(f'<line x1="{x + w*0.12:.1f}" y1="{ly:.1f}" '
                 f'x2="{x + w*(0.46 if i == 0 else (0.9 if (s >> i) & 1 else 0.68)):.1f}" '
                 f'y2="{ly:.1f}" stroke="{MARK_INK}" '
                 f'stroke-width="{3.2 if i == 0 else 2.1}" opacity="{1 if i == 0 else 0.6}"/>')
    return "".join(o)


def mark_term(cx, cy, r, s):
    """A term: the word as a mark, set in a ring."""
    o = []
    for i in range(3):
        rr = r * (0.42 + i * 0.2)
        o.append(f'<circle cx="{cx}" cy="{cy}" r="{rr:.1f}" fill="none" '
                 f'stroke="{MARK_INK}" stroke-width="{3.4 - i*0.8}" '
                 f'opacity="{0.95 - i*0.27:.2f}"/>')
    for i in range(6):
        a = 2 * math.pi * i / 6 + (s % 30) * math.pi / 180
        o.append(f'<line x1="{cx + r*0.42*math.cos(a):.1f}" '
                 f'y1="{cy + r*0.42*math.sin(a):.1f}" '
                 f'x2="{cx + r*0.82*math.cos(a):.1f}" '
                 f'y2="{cy + r*0.82*math.sin(a):.1f}" '
                 f'stroke="{MARK_INK}" stroke-width="2.4"/>')
    return "".join(o)


def mark_case(cx, cy, r, s):
    """A case: a docket. A box, a seal, a record."""
    w, h = r * 1.3, r * 1.62
    x, y = cx - w / 2, cy - h / 2
    o = [f'<path d="M{x:.1f} {y+h*0.13:.1f} L{cx:.1f} {y:.1f} '
         f'L{x+w:.1f} {y+h*0.13:.1f} L{x+w:.1f} {y+h:.1f} L{x:.1f} {y+h:.1f} Z" '
         f'fill="none" stroke="{MARK_INK}" stroke-width="3.2" stroke-linejoin="round"/>']
    for i in range(3):
        ly = y + h * (0.44 + i * 0.145)
        o.append(f'<line x1="{x + w*0.16:.1f}" y1="{ly:.1f}" '
                 f'x2="{x + w*(0.84 if (s >> i) & 1 else 0.62):.1f}" y2="{ly:.1f}" '
                 f'stroke="{MARK_INK}" stroke-width="2.1" opacity=".6"/>')
    o.append(f'<circle cx="{x + w*0.78:.1f}" cy="{y + h*0.24:.1f}" r="{r*0.16:.1f}" '
             f'fill="none" stroke="{MARK_INK}" stroke-width="2.6"/>')
    return "".join(o)


def mark_institution(cx, cy, r, s):
    """An institution: a facade. Columns, a pediment, a step."""
    w = r * 1.7
    base = cy + r * 0.66
    o = [f'<path d="M{cx-w/2:.1f} {base-r*0.36:.1f} L{cx:.1f} {base-r*0.76:.1f} '
         f'L{cx+w/2:.1f} {base-r*0.36:.1f} Z" fill="none" stroke="{MARK_INK}" '
         f'stroke-width="3.2" stroke-linejoin="round"/>',
         f'<line x1="{cx-w/2:.1f}" y1="{base-r*0.31:.1f}" x2="{cx+w/2:.1f}" '
         f'y2="{base-r*0.31:.1f}" stroke="{MARK_INK}" stroke-width="2.4"/>']
    for i in range(5):
        x = cx - w * 0.38 + (w * 0.76) * i / 4
        o.append(f'<line x1="{x:.1f}" y1="{base-r*0.29:.1f}" x2="{x:.1f}" '
                 f'y2="{base:.1f}" stroke="{MARK_INK}" stroke-width="{3.2 + (i % 2)}"/>')
    o.append(f'<line x1="{cx-w/2:.1f}" y1="{base:.1f}" x2="{cx+w/2:.1f}" '
             f'y2="{base:.1f}" stroke="{MARK_INK}" stroke-width="3.6"/>')
    return "".join(o)


MARK_INK = "#f3ece2"
MARKS = {
    "event": mark_event, "mechanism": mark_mechanism, "person": mark_person,
    "work": mark_work, "study": mark_study, "term": mark_term,
    "case": mark_case, "institution": mark_institution,
}


# ------------------------------------------------------------------- the plate
def build(ent: dict, enc: dict) -> str:
    eid = ent["id"]
    s = _seed(eid)
    lanes = [l for l in (ent.get("lanes") or []) if l in enc["lanes"]]
    lane = lanes[0] if lanes else None
    accent = (enc["lanes"][lane]["colour"] if lane else WARM)
    lane_name = enc["lanes"][lane]["name"] if lane else "Unclassified"
    kind = ent.get("kind", "term")
    kind_name = enc["kinds"].get(kind, kind)

    yr = ent.get("year")
    year = None if yr is None else (f"{abs(yr)} BC" if yr < 0 else str(yr))

    # ---- left column: the title, measured, stepped down to fit
    # The year is the loudest thing on the plate, because the whole argument of
    # this site is that the same thing has been happening for a very long time.
    fs, lines = _fit(ent.get("title", eid), L_W, max_lines=3, max_block=190)
    lh = fs * 1.12
    block_h = len(lines) * lh
    ty = 176
    title = "".join(
        f'<text x="{PAD}" y="{ty + i*lh:.1f}" font-family=\'{SERIF}\' '
        f'font-size="{fs}" font-weight="700" fill="{PAPER}" '
        f'letter-spacing="{-fs*0.02:.1f}">{_esc(ln)}</text>'
        for i, ln in enumerate(lines))

    # the year, large, directly under the title, in the lane colour
    year_left = ""
    if year:
        yfs = 120 if len(year) <= 4 else (96 if len(year) <= 6 else 74)
        year_left = (
            f'<text x="{PAD}" y="{ty + block_h + 44 + yfs*0.74:.1f}" '
            f'font-family=\'{MONO}\' font-size="{yfs}" font-weight="700" '
            f'letter-spacing="{-yfs*0.03:.1f}" fill="{accent}">{_esc(year)}</text>')

    ry = ty + block_h + 44 + (128 if year else 40) + 26
    tail = [f'<line x1="{PAD}" y1="{ry:.1f}" x2="{PAD + 110 + (s % 4)*44:.1f}" '
            f'y2="{ry:.1f}" stroke="{accent}" stroke-width="4"/>']
    tail.append(
        f'<text x="{PAD}" y="{ry + 40:.1f}" font-family=\'{MONO}\' font-size="22" '
        f'letter-spacing="3.4" fill="{accent}">{_esc(lane_name.upper())}</text>')
    tail.append(
        f'<text x="{PAD}" y="{ry + 72:.1f}" font-family=\'{MONO}\' font-size="17" '
        f'letter-spacing="2.2" fill="{DIM}">{_esc(kind_name.upper())}'
        f'{"  ·  NOT CITATION-CHECKED" if not ent.get("verified") else "  ·  CITED"}'
        f'</text>')

    # ---- right column: the mark, filling its own column
    mr = 132
    mcy = H / 2 - 24
    mark = MARKS.get(kind, mark_term)((R_X0 + R_X1) / 2, mcy, mr, s)
    glow_r = mr * 2.5

    # ---- ground: dark, a faint grid, and a soft glow in the lane colour
    step = 50
    grid = "".join(
        [f'<line x1="{x}" y1="0" x2="{x}" y2="{H}" stroke="{PAPER}" stroke-width="1" '
         f'opacity=".045"/>' for x in range(0, W + 1, step)]
        + [f'<line x1="0" y1="{y}" x2="{W}" y2="{y}" stroke="{PAPER}" stroke-width="1" '
           f'opacity=".035"/>' for y in range(0, H + 1, step)])
    gcx = (R_X0 + R_X1) / 2
    glow = (f'<defs><radialGradient id="pg" cx=".5" cy=".5" r=".5">'
            f'<stop offset="0" stop-color="{accent}" stop-opacity=".22"/>'
            f'<stop offset="1" stop-color="{accent}" stop-opacity="0"/>'
            f'</radialGradient></defs>'
            f'<circle cx="{gcx:.0f}" cy="{mcy:.0f}" r="{glow_r:.0f}" fill="url(#pg)"/>')

    strip = (f'<text x="{PAD}" y="72" font-family=\'{MONO}\' font-size="18" '
             f'letter-spacing="4.5" fill="{DIM}">A TITLE PLATE, NOT A PHOTOGRAPH</text>'
             f'<line x1="{PAD}" y1="92" x2="{W - PAD}" y2="92" stroke="{PAPER}" '
             f'stroke-width="1" opacity=".14"/>'
             f'<line x1="{COL_RULE}" y1="128" x2="{COL_RULE}" y2="{H - 88}" '
             f'stroke="{PAPER}" stroke-width="1" opacity=".09"/>')

    alt = f"Title plate: {ent.get('title', eid)}"
    alt += f", {year}" if year else ""
    alt += f", {kind_name}, {lane_name}. Drawn from the entry's own record, not a photograph."

    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" \
width="{W}" height="{H}" role="img" aria-label="{_esc(alt)}">
<title>{_esc(ent.get('title', eid))}{' — ' + _esc(year) if year else ''}</title>
<rect width="{W}" height="{H}" fill="{INK}"/>
{grid}
{glow}
{mark}
{title}
{year_left}
{''.join(tail)}
{strip}
</svg>
"""


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--only")
    a = ap.parse_args()

    enc = json.loads(ENC.read_text(encoding="utf-8"))
    want = set(a.only.split(",")) if a.only else None
    OUT.mkdir(parents=True, exist_ok=True)

    made = same = 0
    for e in enc["entries"]:
        if want and e["id"] not in want:
            continue
        svg = build(e, enc)
        p = OUT / f"{e['id']}.svg"
        if p.exists() and p.read_text(encoding="utf-8") == svg:
            same += 1
            continue
        if not a.check:
            p.write_text(svg, encoding="utf-8")
        made += 1

    verb = "would write" if a.check else "wrote"
    files = list(OUT.glob("*.svg"))
    tot = sum(f.stat().st_size for f in files)
    print(f"{verb} {made} plate(s), {same} already current")
    print(f"  {len(files)} plates in img/plate/, {tot/1024:.0f}KB, "
          f"mean {tot/1024/max(1,len(files)):.1f}KB")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
