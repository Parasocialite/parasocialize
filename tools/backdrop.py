#!/usr/bin/env python3
"""
backdrop.py - animated, topic-specific backgrounds for the episode frames.

THE BRIEF WAS "the background needs to be more dynamic and reflect the topic
compellingly". The old background was a dark ground, a faint static grid and a
radial glow in the lane colour. It was competent and it said nothing whatsoever
about the subject. Three identical episodes of three different topics would have
had the same background, which means the background was decoration.

So this is a set of generative systems, one per medium, each built from what the
entry actually is:

    ai / companion   a breathing particle field and drifting chat rectangles.
                     a bond made out of small signals that arrive one way only
    television      a CRT. scanlines rolling, a bright bar travelling down the
                     tube, barrel vignette, and a chromatic edge on everything
    games           an isometric grid in perspective, drifting toward the
                     viewer, with a low-resolution shimmer over it
    music           an equaliser: vertical bars whose heights ripple with a
                     travelling phase
    film            a strip. sprocket holes moving, and a projector flicker on
                     the whole frame
    literature      a page. faint text-lines drifting down under a lamp glow
    sport           a crowd. a dot field with a stadium ripple crossing it
    theology        stone. concentric arcs turning at different rates under a
                     low warm sun
    technology      traces. orthogonal paths with a pulse running along them

Colour is graded by era as well, because a 4th-century bust and a 2022 policy
update should not share a palette: sandstone, then paper and candle, then ink,
then warm CRT, then the cool of the first web, then neon on near-black.

MOTION IS REAL, NOT DESCRIBED
Each system is CSS animation, and a frame is captured at a chosen instant by
giving every animation a negative animation-delay of -t. That makes the whole
thing deterministic and reproducible: frame 3 of scene 5 is always frame 3 of
scene 5, on any machine, forever. (Chrome's --virtual-time-budget looks like the
obvious tool for this and is a trap: on an infinite animation it never returns,
and the render hangs until it is killed. The negative delay has no such problem
and needs no extra flag.)

Everything is slow. These sit behind 60-90px type on a phone held at arm's
length, and a background that competes with the words is worse than no
background. The brief was "stunning" and the way to that is depth and colour, not
speed.

  python -c "import sys; sys.path.insert(0,'tools'); import backdrop"
"""
from __future__ import annotations

import math
import random

# ------------------------------------------------------------------ the eras
def era_grade(year: int | None) -> dict:
    """A palette per period. Warm and low for the ancient world, cold and
    electric for now, with the middle passage through mid-century television."""
    y = year if year is not None else 2000
    if y < 1500:
        return dict(a="#3a2a18", b="#7a5a30", c="#c9a15a", light="#e8c98a",
                    name="sandstone")
    if y < 1900:
        return dict(a="#241c14", b="#6b5334", c="#c8a878", light="#f0dcae",
                    name="candle")
    if y < 1960:
        return dict(a="#16161a", b="#3d4450", c="#9aa6b4", light="#e6ecf2",
                    name="ink")
    if y < 2000:
        return dict(a="#1a1410", b="#4a2f1c", c="#d08a3c", light="#ffd9a0",
                    name="warm crt")
    if y < 2016:
        return dict(a="#0a0e14", b="#1b2c3f", c="#4a86c8", light="#cfe6ff",
                    name="first web")
    return dict(a="#0b0b0d", b="#141a2e", c="#5a4ad8", light="#b8c4ff",
                name="neon")


def _lerp_hex(a: str, b: str, t: float) -> str:
    def hx(c):
        c = c.lstrip("#")
        return tuple(int(c[i:i + 2], 16) for i in (0, 2, 4))
    A, B = hx(a), hx(b)
    return "#%02x%02x%02x" % tuple(int(A[i] + (B[i] - A[i]) * t) for i in range(3))


# ---------------------------------------------------------------- the systems
def _ai(p, W, H, rng):
    """A breathing particle field, plus rectangles that arrive and fade.

    The rectangles are the point: a parasocial relationship is a series of
    one-way signals, so they appear, sit for a moment, and leave without ever
    being answered.
    """
    parts = [f'<defs><radialGradient id="neb" cx=".5" cy=".45" r=".6">'
             f'<stop offset="0" stop-color="{p["c"]}" stop-opacity=".72"/>'
             f'<stop offset=".6" stop-color="{p["b"]}" stop-opacity=".30"/>'
             f'<stop offset="1" stop-color="{p["a"]}" stop-opacity="0"/>'
             f'</radialGradient>'
             f'<linearGradient id="fad" x1="0" y1="0" x2="0" y2="1">'
             f'<stop offset="0" stop-color="{p["a"]}" stop-opacity="0"/>'
             f'<stop offset=".45" stop-color="{p["a"]}" stop-opacity=".55"/>'
             f'<stop offset="1" stop-color="{p["a"]}" stop-opacity=".92"/>'
             f'</linearGradient></defs>']
    parts.append(f'<ellipse cx="{W*.5}" cy="{H*.45}" rx="{W*.75}" ry="{H*.5}" '
                 f'fill="url(#neb)"/>')
    # particles on slow independent orbits
    for i in range(58):
        cx, cy = rng.uniform(0, W), rng.uniform(H * .08, H * .92)
        r = rng.uniform(2.5, 8)
        dur = rng.uniform(13, 30)
        parts.append(
            f'<circle cx="{cx:.0f}" cy="{cy:.0f}" r="{r:.1f}" fill="{p["light"]}" '
            f'opacity="{rng.uniform(.34,.9):.2f}" class="pf" '
            f'style="animation:orb {dur:.1f}s ease-in-out infinite;'
            f'animation-delay:{-rng.uniform(0,dur):.1f}s"/>')
    # one-way messages, kept OUT of the type band. The type occupies roughly
    # 230..1310 of 1920, so a rectangle placed anywhere in 0.12H..0.68H cuts
    # straight across 60-90px of type - which is what the first render did, and
    # it read as noise rather than as a background.
    for i in range(7):
        x = rng.uniform(W * .42, W * .80)
        y = rng.uniform(H * .70, H * .93)
        w, h = rng.uniform(150, 330), rng.uniform(54, 96)
        dur = rng.uniform(11, 21)
        parts.append(
            f'<g class="msg" style="animation:arrive {dur:.1f}s ease-in-out infinite;'
            f'animation-delay:{-rng.uniform(0,dur):.1f}s">'
            f'<rect x="{x:.0f}" y="{y:.0f}" width="{w:.0f}" height="{h:.0f}" rx="16" '
            f'fill="{p["c"]}" opacity=".24" stroke="{p["c"]}" stroke-opacity=".5"/>'
            + "".join(f'<rect x="{x+26:.0f}" y="{y+20+i*15:.0f}" '
                      f'width="{w*rng.uniform(.35,.8):.0f}" height="6" rx="3" '
                      f'fill="{p["light"]}" opacity=".4"/>' for i in range(3))
            + "</g>")
    return ("".join(parts), ["@keyframes orb{0%,100%{transform:translate(0,0)}"
                             "50%{transform:translate(14px,-22px)}}",
                             "@keyframes arrive{0%{opacity:0;transform:translateX(-40px) "
                             "scale(.96)}18%{opacity:1;transform:none}"
                             "72%{opacity:1}100%{opacity:0;transform:translateX(50px)}}"])


def _television(p, W, H, rng):
    """A lit tube in a dark room.

    The first version put scanlines straight onto the near-black ground and
    nothing appeared, because scanlines are black: the pattern only exists if
    there is light behind it to interrupt. A CRT is not a texture, it is a
    glowing rectangle in an unlit room, and the room falling away from it is
    what makes it read as a screen at a glance.

    So the room is nearly black, the tube is the only light source in the frame,
    the scanlines and the roll bar are clipped to inside the tube, and a large
    soft halo bleeds off its edges into the dark.
    """
    tx, ty, tw, th = W * .07, H * .17, W * .86, H * .56
    cx, cy = tx + tw / 2, ty + th / 2
    parts = [
        '<defs>',
        f'<linearGradient id="room" x1="0" y1="0" x2="0" y2="1">'
        f'<stop offset="0" stop-color="{p["a"]}"/>'
        f'<stop offset=".62" stop-color="{p["a"]}"/>'
        f'<stop offset="1" stop-color="#050506"/></linearGradient>',
        f'<linearGradient id="tube" x1=".1" y1="0" x2=".9" y2="1">'
        f'<stop offset="0" stop-color="{p["light"]}" stop-opacity=".6"/>'
        f'<stop offset=".42" stop-color="{p["c"]}" stop-opacity=".44"/>'
        f'<stop offset="1" stop-color="{p["b"]}" stop-opacity=".5"/>'
        f'</linearGradient>',
        f'<radialGradient id="halo" cx=".5" cy=".5" r=".5">'
        f'<stop offset="0" stop-color="{p["c"]}" stop-opacity=".46"/>'
        f'<stop offset=".5" stop-color="{p["c"]}" stop-opacity=".13"/>'
        f'<stop offset="1" stop-color="{p["c"]}" stop-opacity="0"/>'
        f'</radialGradient>',
        f'<linearGradient id="roll" x1="0" y1="0" x2="0" y2="1">'
        f'<stop offset="0" stop-color="#fff" stop-opacity="0"/>'
        f'<stop offset=".5" stop-color="#fff" stop-opacity=".2"/>'
        f'<stop offset="1" stop-color="#fff" stop-opacity="0"/>'
        f'</linearGradient>',
        f'<radialGradient id="vig" cx=".5" cy=".5" r=".68">'
        f'<stop offset=".45" stop-color="#000" stop-opacity="0"/>'
        f'<stop offset="1" stop-color="#000" stop-opacity=".9"/>'
        f'</radialGradient>',
        f'<clipPath id="glass"><rect x="{tx:.0f}" y="{ty:.0f}" width="{tw:.0f}" '
        f'height="{th:.0f}" rx="46"/></clipPath>',
        '</defs>',
        f'<rect x="0" y="0" width="{W}" height="{H}" fill="url(#room)"/>',
        f'<ellipse cx="{cx:.0f}" cy="{cy:.0f}" rx="{tw*0.95:.0f}" ry="{th*1.15:.0f}" '
        f'fill="url(#halo)"/>',
        f'<rect x="{tx:.0f}" y="{ty:.0f}" width="{tw:.0f}" height="{th:.0f}" rx="46" '
        f'fill="url(#tube)"/>',
    ]

    inner = []
    y = 0
    while y < th:
        inner.append(f'<line x1="0" y1="{y}" x2="{W}" y2="{y}" stroke="#000" '
                     f'stroke-width="3" opacity=".24"/>')
        y += 9
    inner.append(f'<rect x="{tx:.0f}" y="{ty:.0f}" width="{tw:.0f}" height="{th:.0f}" '
                 f'fill="url(#roll)" class="rollbar"/>')
    fx, fw = tx + tw * .08, tw * .84
    for i in range(3):
        fy = ty + th * (.1 + i * .29)
        fh = th * .21
        dur = rng.uniform(15, 26)
        inner.append(
            f'<rect x="{fx:.0f}" y="{fy:.0f}" width="{fw:.0f}" height="{fh:.0f}" '
            f'fill="#000" opacity=".22" stroke="{p["light"]}" stroke-opacity=".42" '
            f'class="gh" style="animation:gh {dur:.1f}s ease-in-out infinite;'
            f'animation-delay:{-rng.uniform(0,dur):.1f}s"/>')
    parts.append(f'<g clip-path="url(#glass)"><g class="scan">{"".join(inner)}</g></g>')
    parts.append(
        f'<rect x="{tx:.0f}" y="{ty:.0f}" width="{tw:.0f}" height="{th:.0f}" rx="46" '
        f'fill="none" stroke="{p["light"]}" stroke-opacity=".3" stroke-width="3"/>')
    parts.append(f'<rect x="0" y="0" width="{W}" height="{H}" fill="url(#vig)"/>')
    return ("".join(parts),
            ["@keyframes rollbar{0%{transform:translateY(-420px)}"
             "100%{transform:translateY(2000px)}}",
             "@keyframes scan{0%{transform:translateY(0)}"
             "100%{transform:translateY(9px)}}",
             "@keyframes gh{0%,100%{opacity:.55}50%{opacity:1}}"])


def _games(p, W, H, rng):
    """An isometric floor, drifting toward the viewer."""
    parts = ['<defs><linearGradient id="iso" x1="0" y1="0" x2="0" y2="1">'
             f'<stop offset="0" stop-color="{p["a"]}" stop-opacity="0"/>'
             f'<stop offset=".5" stop-color="{p["c"]}" stop-opacity=".34"/>'
             f'<stop offset="1" stop-color="{p["a"]}" stop-opacity=".7"/>'
             '</linearGradient></defs>',
             f'<rect x="0" y="{H*.42:.0f}" width="{W}" height="{H*.58:.0f}" fill="url(#iso)"/>']
    hz = H * .42
    for i in range(-9, 19):
        x = i * (W / 9)
        parts.append(f'<line x1="{W/2 + (x - W/2)*0.28:.0f}" y1="{hz:.0f}" '
                     f'x2="{x:.0f}" y2="{H}" stroke="{p["c"]}" stroke-opacity=".36" '
                     f'stroke-width="1.6"/>')
    yy = hz
    step = 7
    while yy < H:
        t = (yy - hz) / (H - hz)
        parts.append(f'<line x1="0" y1="{yy:.0f}" x2="{W}" y2="{yy:.0f}" '
                     f'stroke="{p["c"]}" stroke-opacity="{0.1 + t*0.16:.2f}" '
                     f'stroke-width="{1.2 + t*2.4:.1f}"/>')
        step *= 1.20
        yy += step
    for i in range(16):
        x, y2 = rng.uniform(0, W), rng.uniform(hz * .5, H * .95)
        s = rng.uniform(6, 22)
        dur = rng.uniform(7, 16)
        parts.append(
            f'<rect x="{x:.0f}" y="{y2:.0f}" width="{s:.0f}" height="{s:.0f}" '
            f'fill="{p["light"]}" opacity=".38" class="px" '
            f'style="animation:rise {dur:.1f}s linear infinite;'
            f'animation-delay:{-rng.uniform(0,dur):.1f}s"/>')
    return ("".join(parts),
            ["@keyframes rise{0%{transform:translateY(140px);opacity:0}"
             "16%{opacity:.6}100%{transform:translateY(-260px);opacity:0}}"])


def _music(p, W, H, rng):
    """An equaliser with a travelling phase, so the bars ripple rather than
    jumping."""
    bars = []
    n = 46
    for i in range(n):
        x = W * .06 + i * (W * .88 / n)
        dur = rng.uniform(2.4, 5.2)
        h0 = rng.uniform(.18, .8)
        bars.append(
            f'<rect x="{x:.1f}" y="{H*.5 - H*.3:.0f}" width="{W*.88/n*.55:.1f}" '
            f'height="{H*.6:.0f}" rx="6" fill="{p["c"]}" opacity=".8" class="bar" '
            f'style="animation:eq {dur:.2f}s ease-in-out infinite;'
            f'animation-delay:{-rng.uniform(0,dur):.2f}s;--h:{h0:.2f}"/>')
    return (f'<defs><radialGradient id="mg" cx=".5" cy=".5" r=".62">'
            f'<stop offset="0" stop-color="{p["c"]}" stop-opacity=".5"/>'
            f'<stop offset="1" stop-color="{p["a"]}" stop-opacity=".8"/>'
            f'</radialGradient></defs>'
            f'<ellipse cx="{W*.5}" cy="{H*.46}" rx="{W*.7}" ry="{H*.4}" fill="url(#mg)"/>'
            + "".join(bars),
            ["@keyframes eq{0%,100%{transform:scaleY(.22)}"
             "50%{transform:scaleY(1)}}"])


def _film(p, W, H, rng):
    """A strip, moving, with a projector flicker on everything."""
    holes, hx = [], 0
    while hx < W:
        holes.append(f'<rect x="{hx}" y="0" width="46" height="{H*.06:.0f}" rx="7" '
                     f'fill="{p["light"]}" opacity=".1"/>')
        holes.append(f'<rect x="{hx}" y="{H*.94:.0f}" width="46" height="{H*.06:.0f}" '
                     f'rx="7" fill="{p["a"]}"/>')
        hx += 128
    parts = ['<defs><linearGradient id="fr" x1="0" y1="0" x2="1" y2="0">'
             f'<stop offset="0" stop-color="{p["light"]}" stop-opacity=".13"/>'
             f'<stop offset=".5" stop-color="{p["light"]}" stop-opacity=".05"/>'
             f'<stop offset="1" stop-color="{p["light"]}" stop-opacity=".13"/>'
             '</linearGradient>'
             '<radialGradient id="fv" cx=".5" cy=".5" r=".7">'
             '<stop offset=".5" stop-color="#000" stop-opacity="0"/>'
             '<stop offset="1" stop-color="#000" stop-opacity=".8"/>'
             '</radialGradient></defs>',
             f'<rect x="0" y="0" width="{W}" height="{H}" fill="url(#fr)"/>',
             f'<g class="strip">{"".join(holes)}</g>',
             f'<rect x="0" y="0" width="{W}" height="{H}" fill="url(#fv)"/>',
             f'<rect class="flick" x="0" y="0" width="{W}" height="{H}" fill="#fff" '
             f'opacity="0"/>']
    return ("".join(parts),
            ["@keyframes strip{0%{transform:translateY(0)}"
             "100%{transform:translateY(128px)}}",
             "@keyframes flick{0%,100%{opacity:0}7%{opacity:.045}"
             "13%{opacity:0}47%{opacity:.03}53%{opacity:0}}"])


def _literature(p, W, H, rng):
    """A page under a lamp, with the text drifting very slowly."""
    lines = []
    y = 0
    while y < H:
        w = W * rng.uniform(.42, .84)
        x = W * .08 + (W * .8 - w) * rng.random()
        lines.append(f'<rect x="{x:.0f}" y="{y:.0f}" width="{w:.0f}" '
                     f'height="{rng.uniform(9,17):.0f}" rx="5" fill="{p["light"]}" '
                     f'opacity="{rng.uniform(.1,.3):.2f}"/>')
        y += rng.uniform(34, 62)
    return (f'<defs><radialGradient id="lamp" cx=".34" cy=".26" r=".7">'
            f'<stop offset="0" stop-color="{p["light"]}" stop-opacity=".42"/>'
            f'<stop offset=".55" stop-color="{p["b"]}" stop-opacity=".08"/>'
            f'<stop offset="1" stop-color="{p["a"]}" stop-opacity=".85"/>'
            f'</radialGradient></defs>'
            f'<rect x="0" y="0" width="{W}" height="{H}" fill="url(#lamp)"/>'
            f'<g class="pg">{"".join(lines)}</g>',
            ["@keyframes pg{0%{transform:translateY(0)}"
             "100%{transform:translateY(-190px)}}"])


def _sport(p, W, H, rng):
    """A crowd, with a ripple crossing it. The ripple is the whole idea: one
    gesture propagating through a room of people who cannot be in the room."""
    dots = []
    for r in range(13):
        for c in range(24):
            x = W * .04 + c * (W * .92 / 23) + rng.uniform(-5, 5)
            y = H * .5 + r * (H * .036) + rng.uniform(-4, 4)
            dur = rng.uniform(3.4, 6.5)
            dots.append(
                f'<circle cx="{x:.0f}" cy="{y:.0f}" r="{rng.uniform(3,7):.1f}" '
                f'fill="{p["light"]}" opacity=".42" class="cd" '
                f'style="animation:crowd {dur:.2f}s ease-in-out infinite;'
                f'animation-delay:{-rng.uniform(0,dur):.2f}s"/>')
    return (f'<defs><radialGradient id="sg" cx=".5" cy=".62" r=".6">'
            f'<stop offset="0" stop-color="{p["c"]}" stop-opacity=".52"/>'
            f'<stop offset="1" stop-color="{p["a"]}" stop-opacity=".85"/>'
            f'</radialGradient></defs>'
            f'<rect x="0" y="{H*.44:.0f}" width="{W}" height="{H*.56:.0f}" '
            f'fill="url(#sg)"/>' + "".join(dots),
            ["@keyframes crowd{0%,100%{transform:translateY(0) scale(1)}"
             "50%{transform:translateY(-9px) scale(1.14)}}"])


def _theology(p, W, H, rng):
    """Stone. Concentric arcs turning at different rates under a low sun."""
    cx, cy = W * .5, H * .44
    arcs = []
    for i in range(9):
        r = 150 + i * 78
        dur = 120 + i * 34
        arcs.append(
            f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="none" '
            f'stroke="{p["c"]}" stroke-opacity="{0.5 - i*0.042:.2f}" '
            f'stroke-width="{3.2 - i*0.22:.1f}" stroke-dasharray="{60+i*34} {34+i*20}" '
            f'class="arc" style="animation:spin {dur}s linear infinite;'
            f'animation-delay:{-i*7}s;transform-origin:{cx}px {cy}px"/>')
    for i in range(30):
        a = rng.uniform(0, 2 * math.pi)
        r = rng.uniform(200, 780)
        x, y = cx + r * math.cos(a), cy + r * math.sin(a) * .82
        s = rng.uniform(3, 11)
        dur = rng.uniform(18, 40)
        arcs.append(
            f'<circle cx="{x:.0f}" cy="{y:.0f}" r="{s:.1f}" fill="{p["light"]}" '
            f'opacity="{rng.uniform(.22,.6):.2f}" class="pf" '
            f'style="animation:orb {dur:.1f}s ease-in-out infinite;'
            f'animation-delay:{-rng.uniform(0,dur):.1f}s"/>')
    return (f'<defs><radialGradient id="sun" cx=".5" cy=".44" r=".5">'
            f'<stop offset="0" stop-color="{p["light"]}" stop-opacity=".55"/>'
            f'<stop offset=".5" stop-color="{p["c"]}" stop-opacity=".1"/>'
            f'<stop offset="1" stop-color="{p["a"]}" stop-opacity=".9"/>'
            f'</radialGradient></defs>'
            f'<ellipse cx="{cx}" cy="{cy}" rx="{W*.8}" ry="{H*.5}" fill="url(#sun)"/>'
            + "".join(arcs),
            ["@keyframes spin{0%{transform:rotate(0)}100%{transform:rotate(360deg)}}",
             "@keyframes orb{0%,100%{transform:translate(0,0)}"
             "50%{transform:translate(16px,-18px)}}"])


def _technology(p, W, H, rng):
    """Traces, with a pulse running along them."""
    paths = []
    for i in range(13):
        x = rng.uniform(0, W)
        y = rng.uniform(0, H)
        pts = [f"M{x:.0f} {y:.0f}"]
        for _ in range(rng.randint(2, 4)):
            if rng.random() < .5:
                x += rng.choice([-1, 1]) * rng.uniform(60, 220)
            else:
                y += rng.choice([-1, 1]) * rng.uniform(60, 220)
            pts.append(f"L{x:.0f} {y:.0f}")
        d = " ".join(pts)
        dur = rng.uniform(3.6, 8)
        paths.append(
            f'<path d="{d}" fill="none" stroke="{p["c"]}" stroke-opacity=".36" '
            f'stroke-width="2" class="tr" style="animation:tr {dur}s linear infinite;'
            f'animation-delay:{-rng.uniform(0,dur):.2f}s"/>')
    return (f'<defs><linearGradient id="tg" x1="0" y1="0" x2="1" y2="1">'
            f'<stop offset="0" stop-color="{p["b"]}" stop-opacity=".7"/>'
            f'<stop offset="1" stop-color="{p["a"]}" stop-opacity=".9"/>'
            f'</linearGradient></defs>'
            f'<rect x="0" y="0" width="{W}" height="{H}" fill="url(#tg)"/>'
            + "".join(paths),
            ["@keyframes tr{0%,100%{stroke-opacity:.18}50%{stroke-opacity:.7}}"])


SYSTEMS = {
    "ai": _ai, "companion": _ai, "technology": _technology,
    "television_scripted": _television, "television_unscripted": _television,
    "games": _games, "music": _music, "film": _film,
    "literature": _literature, "sport": _sport, "theology": _theology,
    "history": _theology,
}

# grain, shared by every system: the thing that stops a gradient reading as
# vector art
GRAIN = (
    "grain{position:absolute;inset:0;opacity:.05;mix-blend-mode:overlay;"
    "background-image:url(\"data:image/svg+xml;utf8,"
    "<svg xmlns='http://www.w3.org/2000/svg' width='140' height='140'>"
    "<filter id='n'><feTurbulence type='fractalNoise' baseFrequency='.85' "
    "numOctaves='3'/></filter>"
    "<rect width='140' height='140' filter='url(%23n)' opacity='.6'/>"
    "</svg>\");}"
)


def backdrop(entry: dict, enc: dict, extra_rules: list[str] | None = None,
             size: tuple[int, int] = (1080, 1920)
             ) -> tuple[str, str, str]:
    """(css, svg markup, system name) for one entry.

    Keyed on `medium` first, because that is what the entry actually is, and
    falls back to the era's own character for the ones with no medium. The
    system name is returned because it is worth knowing which one you got, and
    worth being able to assert on: two entries of the same medium should share
    a system, and two entries of different media should not.

    `size` is the canvas the backdrop has to fill. It was hardcoded to 1080x1920,
    which is the vertical master, and the landscape master inherited that
    without asking: the CSS pinned .bg svg to width:1080px, so in a 1920x1080
    frame the backdrop covered the left 56% and stopped at a hard vertical edge
    at x=1080 - visible as a straight seam down the middle of every horizontal
    frame. Passing the real size is the whole fix; each system is written
    against W and H already, so they compose to whatever canvas they are given.

    The era palette is then pulled toward the entry's LANE colour. Without that
    the backdrops are era-accurate and brand-blind: ELIZA is 1966 so it comes
    out in 1960s ink and grey, and three episodes in three different decades look
    like three different companies. The lane is what makes them one channel.
    """
    p = era_grade(entry.get("year"))
    lanes = entry.get("lanes") or []
    lane = lanes[0] if lanes else None
    if lane and lane in enc.get("lanes", {}):
        ac = enc["lanes"][lane].get("colour")
        if ac:
            for k in ("b", "c"):
                p[k] = _lerp_hex(p[k], ac, 0.34)
            p["light"] = _lerp_hex(p["light"], ac, 0.20)
    media = entry.get("medium") or []
    system = next((m for m in media if m in SYSTEMS), None)
    if system is None:
        y = entry.get("year") or 2000
        system = "theology" if y < 1900 else "technology"
    W, H = int(size[0]), int(size[1])
    rng = random.Random(f"{entry['id']}-{system}-{W}x{H}")
    body, keys = SYSTEMS[system](p, W, H, rng)
    rules = list(extra_rules or []) + keys
    # The svg is sized to the canvas with no viewBox, rather than a viewBox with
    # preserveAspectRatio="slice". Slice would scale the portrait composition to
    # cover a landscape frame and crop the middle away, which is the guillotining
    # this was meant to avoid - and it is how the systems can stay written
    # against W and H at all. Drawing at the frame's own size means the systems
    # lay out for the shape they are actually in.
    css = (f".bg{{position:absolute;inset:0;overflow:hidden}}"
           f".bg svg{{position:absolute;inset:0;width:{W}px;height:{H}px;display:block}}"
           + "".join(rules) + GRAIN)
    svg = (f'<svg width="{W}" height="{H}" viewBox="0 0 {W} {H}">{body}</svg>')
    return css, svg, f"{system} / {p['name']}"
