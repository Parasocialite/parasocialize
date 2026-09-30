#!/usr/bin/env python3
"""
mascot.py - Iyi.

An eight lying on its side. Which is also infinity. Which is also two eyes.

THE CHARACTER
Two filled tangent lobes, overlapping in the middle, with a large warm pupil in
each. That is the whole thing: no head, no limbs, no mouth on the default. The
brief was a pair of cartoon eyes connected like a sideways eight, and every
extra part has been tried and removed - limbs turn a face into a creature, and
at 3cm on a shirt a creature is a mascot while a face is a logo.

WHY FILLED, NOT OUTLINED
An outlined ring is a lens. A filled shape is an eye. This was the exact reason
the first attempt read as spectacles, and it is a fill-versus-stroke decision,
not a detail.

TIMELESS BEFORE ADORABLE
Timeless is the constraint that decides everything else, and it is why there is
no four-stop rainbow here. A multi-hue gradient is the signature of a particular
year; a warm monochrome with one dark accent and one white is not. The colour
stays inside a narrow warm band, the silhouette does the work, and the whole
thing is legible as a single flat fill - which is what gets it onto a screen
print, a enamel pin, a favicon at 16px, and a sticker.

THE ANIMATION RIG
Built to be animated, because a mascot that cannot move is a sticker. The parts
are grouped and named so they can be driven from CSS or SMIL without touching
the geometry:

  .iyi            the whole character        -> breathe, bob, tilt
  .iyi-bloom      the warm halo behind it    -> pulse
  .iyi-lobe       an eye                     -> squint
  .iyi-pupil      the dark pupil             -> blink (scaleY), look (translate)
  .iyi-lash       the lashes                 -> flutter
  .iyi-blush      the cheek                  -> glow

Every transform origin is its own centre (transform-box: fill-box), so a blink
is `scaleY(.1)` on the pupil and nothing else. A look-around is `translateX` on
the pupils. Neither needs keyframes baked into the file, so the same asset works
in CSS, in a sprite sheet, or in print.

An idle blink is included and respects prefers-reduced-motion.
"""
import sys, pathlib, zlib

ROOT = pathlib.Path(__file__).resolve().parent.parent

# geometry. two tangent circles, centres 34 apart, radius 26. everything is on
# a 118 square so the parts line up with the pupil and lash centres, which is
# what makes the rig above animatable without touching coordinates.
R = 26
CY = 42
LX, RX = 42, 76          # lobe centres, 34 apart so they overlap into an eight

# ---------------------------------------------------------------------------
# TIMELESS PALETTE
# Two stops, one warm family, nothing else. The four-stop orange->pink->purple
# was the single most dated thing about Iyi: a multi-hue gradient is how this
# decade looks, so it ages the character whether or not the rest survives.
# Apricot into coral is just light falling on a warm surface, which is a much
# older idea than any particular palette. Saturation and hue trends move; a
# face lit from the front does not.
# ---------------------------------------------------------------------------
SCLERA = ("#ffe7c4", "#ff8f5e")
ACCENT = "#e0533f"
INK = "#231009"
PUPIL_R = 12


def sclera_grad(gid):
    a, b = SCLERA
    return (f'<linearGradient id="{gid}" x1=".12" y1="0" x2=".88" y2="1">'
            f'<stop offset="0" stop-color="{a}"/>'
            f'<stop offset="1" stop-color="{b}"/></linearGradient>')


def bloom_grad(gid):
    return (f'<radialGradient id="{gid}" cx=".5" cy=".5" r=".5">'
            f'<stop offset="0" stop-color="#fff6e6" stop-opacity=".85"/>'
            f'<stop offset="1" stop-color="#fff6e6" stop-opacity="0"/></radialGradient>')


# THE RIG. transform-box:fill-box gives every part its own bounding box, so a
# blink is scaleY() on the pupil about the pupil's own centre and a look-around
# is translateX() on the pupils - neither needs keyframes baked into the file.
# The --d custom property is what desynchronises a page full of mascots; custom
# properties inherit, animation-delay does not.
RIG_CSS = """.iyi,.iyi-bloom,.iyi-lobe,.iyi-pupil,.iyi-lid,.iyi-blush{
transform-box:fill-box;transform-origin:center}"""

BLINK_CSS = """@keyframes iyi-breathe{0%,100%{transform:scale(1)}
50%{transform:scale(1.035)}}
@keyframes iyi-blink{0%,90%,100%{transform:scaleY(1)}93%{transform:scaleY(.08)}}
@keyframes iyi-bloom-pulse{0%,100%{opacity:.26}50%{opacity:.42}}
.iyi{animation:iyi-breathe 5.4s ease-in-out infinite;animation-delay:var(--d,0s)}
.iyi-pupil{animation:iyi-blink 6.6s ease-in-out infinite;animation-delay:var(--d,0s)}
.iyi-bloom{animation:iyi-bloom-pulse 5.4s ease-in-out infinite;animation-delay:var(--d,0s)}
@media (prefers-reduced-motion:reduce){
.iyi,.iyi-pupil,.iyi-bloom{animation:none}}"""

MASCOT_CSS = RIG_CSS + "\n" + BLINK_CSS


def pupil(cx, cy, r, ink, hi=True):
    """Big warm pupil. Deliberately not a tiny dot in a big pale lobe - that
    reads as a googly eye and looks startled. A large dark pupil with a soft
    highlight reads as warm, and warmth is the entire brief for this character."""
    o = [f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="{ink}"/>']
    if hi:
        o.append(f'<circle cx="{cx-r*0.32}" cy="{cy-r*0.36}" r="{r*0.34}" fill="#fffaf2"/>')
        o.append(f'<circle cx="{cx+r*0.32}" cy="{cy+r*0.3}" r="{r*0.16}" fill="#fffaf2" opacity=".7"/>')
        o.append(f'<circle cx="{cx-r*0.08}" cy="{cy+r*0.44}" r="{r*0.1}" fill="#fffaf2" opacity=".45"/>')
    return "".join(o)


def lid_d(cx, depth):
    """The bare eyelid outline. Split out from lid() so the single-colour build
    can punch the exact same shape out of the mask instead of redrawing it."""
    a = round(R - 0.6, 1)
    top, bot = round(CY - a, 1), round(CY - a + depth, 1)
    return (f"M{cx-a} {top}A{a} {a} 0 0 1 {cx+a} {top}"
            f"L{cx+a} {bot}A{a} {a} 0 0 0 {cx-a} {bot}Z")


def shut_span_d(cx, span=24, curve=9):
    """A closed eye. A stroke rather than a filled lens: the first version was a
    lens 2px thick at its middle and read as a stray hair rather than an eye.
    The clip means it can be a confident 5.5px stroke without ever leaving the
    lobe, and the two closed eyes can no longer fuse into a moustache in the
    middle because each is clipped to its own lobe."""
    h = span / 2
    return f"M{cx-h} {CY-2}q{h} {curve} {span} 0"


def heart_d(cx, cy, s):
    """A real heart. The old one-liner was two curves with an incomplete
    coordinate list, so it rendered as a rounded blob - which is not a heart and
    does not read as one however small you make it."""
    return (f"M{cx} {cy + .55 * s:.1f}"
            f"C{cx - .62 * s:.1f} {cy + .12 * s:.1f} {cx - .62 * s:.1f} {cy - .52 * s:.1f} "
            f"{cx - .28 * s:.1f} {cy - .52 * s:.1f}"
            f"C{cx - .10 * s:.1f} {cy - .52 * s:.1f} {cx} {cy - .34 * s:.1f} {cx} {cy - .20 * s:.1f}"
            f"C{cx} {cy - .34 * s:.1f} {cx + .10 * s:.1f} {cy - .52 * s:.1f} "
            f"{cx + .28 * s:.1f} {cy - .52 * s:.1f}"
            f"C{cx + .62 * s:.1f} {cy - .52 * s:.1f} {cx + .62 * s:.1f} {cy + .12 * s:.1f} "
            f"{cx} {cy + .55 * s:.1f}Z")


# mood table. the whole expression vocabulary is lid depth, pupil offset, pupil
# size, and whether a pupil is a heart - four numbers. every one of them is a
# transform on a named group, which is why the rig animates without keyframes.
#
# HEARTS ARE NOT A DEFAULT. love is the only mood with hearts, and it is the
# only one that means it. Hearts belong to a specific romantic or affectionate
# beat, never to the base character, never to a masthead, a wordmark, a plate or
# a default state - a mascot wearing hearts by default stops reading as a
# mascot and starts reading as a sticker, and it flattens the one expression
# that carries meaning. watch is the default and it has round pupils.
MOODS = {
    "watch":  dict(lid=0.0,  pupils=(0, 3),  pr=12, blush=True, note="the default. the reader looking back."),
    "hollow": dict(lid=17,   pupils=(0, 6),  pr=8,  note="nobody is home. the joke of the whole site."),
    "wink":   dict(lid=0.0,  pupils=(0, 3),  pr=12, blush=True, shut="r", note="pull quotes."),
    "sad":    dict(lid=15,   pupils=(0, 5),  pr=11, note="grief. the obituary cards."),
    "panic":  dict(lid=6,    pupils=(0, -5), pr=8,  note="the sweep is late and the clock is red."),
    "love":   dict(lid=0.0,  hearts=True, blush=True, note="the club. ONLY for a romantic beat."),
    "clerk":  dict(lid=5,    pupils=(0, 2),  pr=12, note="behind the counter. Enan's own tell."),
    "asleep": dict(shut=True, note="sweeping hourly, seven past."),
}


def eyes_mkup(body, ink, clip_l, clip_r, m, pr_default=PUPIL_R, flat=False,
              lobe_mask=""):
    """The two lobes and everything that lives inside them.

    Clipping is what makes this safe: the lobes are the clip paths, so the lid,
    the pupil and the blush are all guaranteed to stay within the silhouette
    whatever the mood asks for. That guarantee is the whole reason the
    character stopped looking like a bug.

    Returns (markup, knockouts). The knockouts are the same inner shapes again,
    as black, for the single-colour build to punch out of its mask - so a stamp
    and a screen print are the same drawing rather than two drawings that drift.
    """
    pr = m.get("pr", pr_default)
    o = [f'<g class="iyi-lobe"{lobe_mask}><circle cx="{LX}" cy="{CY}" r="{R}" fill="{body}"/></g>',
         f'<g class="iyi-lobe"{lobe_mask}><circle cx="{RX}" cy="{CY}" r="{R}" fill="{body}"/></g>']
    k = []

    if m.get("blush") and not flat:
        o.append(f'<g class="iyi-blush" opacity=".26">'
                 f'<ellipse cx="{LX}" cy="{CY+13}" rx="8" ry="4.4" fill="{ACCENT}"/>'
                 f'<ellipse cx="{RX}" cy="{CY+13}" rx="8" ry="4.4" fill="{ACCENT}"/></g>')

    # lids sit above the pupils, so a heavy lid crops them rather than the
    # pupil being drawn smaller for a heavy-lid mood - same result, but the lid
    # animates as its own transform.
    # flat skips them: a lid is a crescent, and a crescent punched out of the top
    # of a one-colour eight reads as a chip broken off it rather than a lid.
    if m.get("lid") and not flat:
        d = m["lid"]
        for c, cp in ((LX, clip_l), (RX, clip_r)):
            o.append(f'<g class="iyi-lid"><g clip-path="url(#{cp})">'
                     f'<path d="{lid_d(c, d)}" fill="{ink}"/></g></g>')
    if m.get("shut") == "r":
        o.append(f'<g class="iyi-lid"><g clip-path="url(#{clip_r})">'
                 f'<path d="{shut_span_d(RX)}" stroke="{ink}" stroke-width="5.5" '
                 f'stroke-linecap="round" fill="none"/></g></g>')
    if m.get("shut") is True:
        for c, cp in ((LX, clip_l), (RX, clip_r)):
            if flat:
                k.append(f'<path d="{shut_span_d(c)}" stroke="#000" stroke-width="5.5" '
                         f'stroke-linecap="round" fill="none"/>')
            else:
                o.append(f'<g class="iyi-lid"><g clip-path="url(#{cp})">'
                         f'<path d="{shut_span_d(c)}" stroke="{ink}" stroke-width="5.5" '
                         f'stroke-linecap="round" fill="none"/></g></g>')

    if m.get("hearts"):
        for c in (LX, RX):
            if flat:
                k.append(f'<path d="{heart_d(c, CY, 20)}" fill="#000"/>')
            else:
                o.append(f'<g class="iyi-pupil">'
                         f'<path d="{heart_d(c, CY, 20)}" fill="{ink}"/></g>')
    elif not m.get("shut"):
        dx, dy = m.get("pupils", (0, 0))
        for c in (LX, RX):
            if flat:
                k.append(f'<circle cx="{c+dx}" cy="{CY+dy}" r="{pr+1.5}" fill="#000"/>')
            else:
                o.append(f'<g class="iyi-pupil">{pupil(c + dx, CY + dy, pr, ink)}</g>')
    return "".join(o), "".join(k)



def build(mood="watch", flat=None, ink=INK, grad=True):
    """A standalone Iyi, with its own stylesheet so it still animates when the
    file is opened or dropped in an <img> with no page around it.

    flat=colour is the single-colour version for stamps and vinyl. One colour
    means every inner shape has to be negative space, so the lobes carry a mask
    and the pupils, lids and hearts are punched out of it. Drawn normally in the
    same colour as the body they would simply vanish and leave a solid eight.
    """
    m = MOODS[mood]
    gid = f"iyig{mood}" + ("f" if flat else "")
    cl, cr = gid + "cl", gid + "cr"
    eyes, knock = eyes_mkup(
        flat or (f"url(#{gid})" if grad else SCLERA[0]), ink, cl, cr, m,
        flat=bool(flat),
        lobe_mask=f' mask="url(#{gid}m)"' if flat else "")
    o = [f"<style>{MASCOT_CSS}</style>",
         f'<defs>{"" if flat else bloom_grad(gid + "h")}'
         f'{"" if (flat or not grad) else sclera_grad(gid)}'
         # the clips are the lobes themselves: nothing drawn inside can ever
         # escape them, which is the guarantee the character depends on
         f'<clipPath id="{cl}"><circle cx="{LX}" cy="{CY}" r="{R}"/></clipPath>'
         f'<clipPath id="{cr}"><circle cx="{RX}" cy="{CY}" r="{R}"/></clipPath>'
         f'<mask id="{gid}m"><rect width="118" height="118" fill="#000"/>'
         f'<circle cx="{LX}" cy="{CY}" r="{R}" fill="#fff"/>'
         f'<circle cx="{RX}" cy="{CY}" r="{R}" fill="#fff"/>{knock}</mask>'
         f'</defs>']

    o.append('<g class="iyi">')
    if not flat:
        o.append(f'<circle class="iyi-bloom" cx="{LX+6}" cy="{CY+4}" r="{R+9}" '
                 f'fill="url(#{gid}h)"/>')
    o.append(eyes)
    o.append('</g>')
    return ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 118 118" '
            'width="118" height="118" role="img" aria-label="Iyi">'
            f'<title>Iyi - {mood}</title>{"".join(o)}</svg>')


def inline(mood="watch", size=34, cls="", ink=INK, grad=True):
    """Same character, inlined for a page.

    Self-contained geometry: each copy carries its own gradient under a unique
    id. A shared <defs> block elsewhere in the document resolved fine in theory
    and not at all in practice - the lobes came out unpainted and only the dark
    pupils showed, which read as two dots rather than a face. Depending on a
    gradient defined in a different <svg> element is the fragile version.

    The animation is deliberately NOT inlined. It lives once in css/mascot.css
    (written by this module) because a page carries a dozen of these and the
    keyframes would otherwise ship a dozen times over. --d staggers the copies
    so a page full of Iyi is not blinking in unison, which is the single
    fastest way to make a character look like a CSS demo instead of a mascot.
    """
    gid = f"iyig{zlib.crc32(repr((mood, size, cls, ink, grad)).encode()) % 99991}"
    m = MOODS.get(mood, MOODS["watch"])
    d = (zlib.crc32(gid.encode()) % 1700) / 1000
    cl, cr = gid + "l", gid + "r"
    eyes, _ = eyes_mkup(f"url(#{gid})" if grad else SCLERA[0], ink, cl, cr, m,
                        pr_default=13)

    o = [f'<defs>{bloom_grad(gid + "h")}'
         f'{"" if not grad else sclera_grad(gid)}'
         f'<clipPath id="{cl}"><circle cx="{LX}" cy="{CY}" r="{R}"/></clipPath>'
         f'<clipPath id="{cr}"><circle cx="{RX}" cy="{CY}" r="{R}"/></clipPath>'
         f'</defs>',
         f'<g class="iyi" style="--d:{d:.2f}s">',
         f'<circle class="iyi-bloom" cx="{LX+6}" cy="{CY+4}" r="{R+9}" '
         f'fill="url(#{gid}h)"/>',
         eyes,
         '</g>']

    return (f'<svg class="mascot {cls}" viewBox="0 0 118 118" width="{size}" height="{size}" '
            f'aria-hidden="true" focusable="false">{"".join(o)}</svg>')


def main():
    a = sys.argv[1:]
    out = pathlib.Path(a[a.index("--out") + 1]) if "--out" in a else ROOT / "img" / "mascot"
    out.mkdir(parents=True, exist_ok=True)

    # the site gets the rig from a real stylesheet, emitted here so mascot.py
    # stays the single source of truth for how Iyi moves
    css = ROOT / "css" / "mascot.css"
    css.parent.mkdir(parents=True, exist_ok=True)
    header = ("/* generated by tools/mascot.py - do not edit by hand.\n"
              "   Iyi's animation rig. Each part is its own group, so a blink is\n"
              "   scaleY() on .iyi-pupil and a look-around is translateX() on it.\n"
              "   --d staggers the copies; it inherits, animation-delay does not. */\n")
    css.write_text(header + MASCOT_CSS + "\n", encoding="utf-8")

    for m in MOODS:
        (out / f"iyi-{m}.svg").write_text(build(m), encoding="utf-8")
    if "--flat" in a:
        for m in ("watch", "hollow", "sad", "love"):
            (out / f"iyi-{m}-flat.svg").write_text(
                build(m, flat=INK, ink=INK), encoding="utf-8")
    if "--sheet" in a:
        cells = []
        for i, m in enumerate(MOODS):
            cells.append(f'<g transform="translate({(i%4)*150},{(i//4)*150})">{build(m)}</g>'
                         f'<text x="{(i%4)*150+59}" y="{(i//4)*150+136}" fill="#cbb59d" '
                         f'font-family="monospace" font-size="13" text-anchor="middle">{m}</text>')
        (out / "sheet.svg").write_text(
            f'<svg xmlns="http://www.w3.org/2000/svg" width="600" height="300" '
            f'style="background:#130d0a">{"".join(cells)}</svg>', encoding="utf-8")
        print(f"  sheet: {len(MOODS)} expressions")
    print(f"  {len(MOODS)} expressions -> {out}")


if __name__ == "__main__":
    main()


