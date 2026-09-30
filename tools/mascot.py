#!/usr/bin/env python3
"""
mascot.py - iYi.

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
R = 25
CY = 42
# Lobe centres. They used to sit 34 apart, which overlapped them by 18 units and
# read as one wide blob with two eyes in it. That cost both readings at once: it
# was not cute, because a fused pair of eyes is not a face, and it was not two
# sides either, because the sides had merged. 44 apart leaves a 6-unit overlap,
# enough to still read as one continuous form and little enough that each lobe
# holds its own pupil.
LX, RX = 40, 84

# ---------------------------------------------------------------------------
# TIMELESS PALETTE
# Two stops, one warm family, nothing else. The four-stop orange->pink->purple
# was the single most dated thing about iYi: a multi-hue gradient is how this
# decade looks, so it ages the character whether or not the rest survives.
# Apricot into coral is just light falling on a warm surface, which is a much
# older idea than any particular palette. Saturation and hue trends move; a
# face lit from the front does not.
# ---------------------------------------------------------------------------
SCLERA = ("#ffe7c4", "#ff8f5e")
ACCENT = "#e0533f"
INK = "#231009"
# The pupil is large on purpose. It used to be 12 against a 26 lobe, which left
# a thick ring of body colour around it and read as clip-art. Cute eyes are
# mostly pupil; the body is a rim, not a field. 17.5 against a 25 lobe fills it
# properly while still leaving enough margin that the lid has somewhere to crop.
PUPIL_R = 17.5


def sclera_grad(gid):
    """Light falling on a warm surface, in three stops rather than two.

    The two-stop version was too shallow to read as a rounded form at small
    sizes - the lobes came out as flat discs, which is the difference between a
    character and a shape. The middle stop is what turns the gradient into a
    volume: pale where the light lands, saturated through the body, and a deeper
    coral at the bottom edge so the form turns away from the light instead of
    stopping flat.
    """
    a, b = SCLERA
    deep = "#f2703f"
    return (f'<linearGradient id="{gid}" x1=".18" y1="0" x2=".82" y2="1">'
            f'<stop offset="0" stop-color="{a}"/>'
            f'<stop offset=".52" stop-color="{b}"/>'
            f'<stop offset="1" stop-color="{deep}"/>'
            f'</linearGradient>')


def bloom_grad(gid):
    """The halo, warmed.

    It was near-white at .85, which over a dark ground read as a grey smudge
    behind the head rather than as light coming off it. Warm and a little
    weaker: the halo should suggest the body is giving off light, not that
    something pale is sitting behind it.
    """
    return (f'<radialGradient id="{gid}" cx=".5" cy=".5" r=".5">'
            f'<stop offset="0" stop-color="#ff8f5e" stop-opacity=".42"/>'
            f'<stop offset=".55" stop-color="#ff5a1f" stop-opacity=".14"/>'
            f'<stop offset="1" stop-color="#ff5a1f" stop-opacity="0"/>'
            f'</radialGradient>')


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


def star_d(cx, cy, r, waist=0.3):
    """A four-point sparkle.

    The single strongest cuteness signal available, and the thing the old
    highlights were missing. A plain white circle says 'shiny'. A four-point
    sparkle says 'alive' - it is the shape every kawaii and anime eye uses to
    signal that there is somebody in there, which is precisely the claim this
    character is making and also precisely what it must not oversell. The
    concave waist is what makes it read as a sparkle rather than a diamond.
    """
    w = r * waist
    return (f"M{cx} {cy - r}L{cx + w} {cy - w}L{cx + r} {cy}"
            f"L{cx + w} {cy + w}L{cx} {cy + r}L{cx - w} {cy + w}"
            f"L{cx - r} {cy}L{cx - w} {cy - w}Z")


def pupil(cx, cy, r, ink, hi=True, spark=1.0):
    """Big warm pupil. Deliberately not a tiny dot in a big pale lobe - that
    reads as a googly eye and looks startled. A large dark pupil with a soft
    highlight reads as warm, and warmth is the entire brief for this character.

    The highlights are a big round catchlight plus a small four-point sparkle
    plus a low rim light. The pairing is the point: a lone circle looks like a
    sticker, and the lower rim is what makes the eye read as wet rather than
    printed. spark scales all three, so a mood can fade one side's light out
    entirely - nobody home, without needing a lid to say it.
    """
    o = [f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="{ink}"/>']
    if hi and spark > 0.02:
        s = max(0.0, min(1.0, spark))
        o.append(f'<circle cx="{cx-r*0.3}" cy="{cy-r*0.34}" r="{r*0.29*s}" fill="#fffaf2"/>')
        o.append(f'<path d="{star_d(cx+r*0.27, cy+r*0.31, r*0.29*s)}" '
                 f'fill="#fffaf2" opacity="{round(0.92*s, 3)}"/>')
        o.append(f'<circle cx="{cx-r*0.14}" cy="{cy+r*0.5}" r="{r*0.09*s}" '
                 f'fill="#fffaf2" opacity="{round(0.5*s, 3)}"/>')
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
# size, catchlight strength, and whether a pupil is a heart. every one of them is
# a transform on a named group, which is why the rig animates without keyframes.
#
# WHO IYI IS. iYi is the conduit: the middle term in a connection that is not
# reciprocated. Not the reader and not the idol - the channel between them. The
# two pupils are the two sides of that connection, you and them, and they are
# NOT the same size, because the relationship is not symmetrical. That is the
# argument of the whole site drawn in one face.
#
# The name is the drawing. i-Y-i: two lowercase i for two selves, a Y for the
# fork where they diverge, and the dots on the i's are the catchlights. Write it
# iYi, always, with a lowercase i on both sides.
#
# The default is deliberately lopsided - bigger, brighter, more centred on the
# left; smaller, dimmer, turned away on the right. Symmetry here would render
# the exact thing the site argues against.
#
# But the gap has to stay NARROW. The first asymmetric pass used a big enough
# difference in size, lid and light that the right eye read as a lazy squint
# rather than as a choice, which is the opposite of cute: an eye that looks
# broken is not endearing, it is a fault in the drawing. The asymmetry now lives
# mostly in the light and a modest size difference, so the second eye is still
# round, still open and still catching some light. It is the dimmer side, not
# the damaged one.
#
# HEARTS ARE NOT A DEFAULT. love is the only mood with hearts, and it is the
# only one that means it. Hearts belong to a specific romantic or affectionate
# beat, never to the base character and never to a default state - a mascot
# wearing hearts by default stops reading as a mascot and starts reading as a
# sticker, and it spends the one expression that carries meaning.
MOODS = {
    "watch":  dict(lid=(0.0, 3.5), pr=(16, 13.5), blush=True, spark=(1.0, 0.62),
                   pupils=((0, 1.5), (3, 3.5)),
                   note="the default. the two sides, unequal. one of them is you."),
    "hollow": dict(lid=(15, 19), pupils=((0, 5), (3, 7)), pr=(12, 10), spark=(0.55, 0.0),
                   note="nobody is home. the joke of the whole site."),
    "wink":   dict(lid=0.0, pupils=((0, 2), (3, 3)), pr=(15, 13), blush=True,
                   spark=(1.0, 0.55), shut="r",
                   note="pull quotes."),
    "sad":    dict(lid=(13, 17), pupils=((0, 4), (2, 6)), pr=(14, 11.5), spark=(0.85, 0.28),
                   note="grief. the obituary cards."),
    "panic":  dict(lid=5,    pupils=((0, -4), (2, -5)), pr=(11.5, 9.5), spark=(1.0, 0.4),
                   note="the sweep is late and the clock is red."),
    "love":   dict(lid=0.0,  hearts=True, blush=True, note="the club. ONLY for a romantic beat."),
    "clerk":  dict(lid=4,    pupils=((0, 2), (2, 3)), pr=(15, 13), spark=(1.0, 0.5),
                   note="behind the counter. Enan's own tell."),
    "asleep": dict(shut=True, note="sweeping hourly, seven past."),
}


def per_pair(v, i, default=(0, 0)):
    """A value that is an (x, y) offset, optionally given per eye.

    Ambiguous by nature, so it is resolved by shape: a pair of PAIRS is per eye,
    a pair of NUMBERS is one shared offset. Those cannot be confused, and it
    means every existing mood that writes pupils=(0, 3) keeps working untouched.
    """
    if v is None:
        return default
    if isinstance(v, (tuple, list)) and len(v) == 2 \
            and all(isinstance(x, (tuple, list)) and len(x) == 2 for x in v):
        return tuple(v[i])
    return v


def per_num(v, i, default=0):
    """A value that is a plain number, optionally given per eye.

    A number is shared. A pair of numbers is per eye. The two cases are
    distinguishable because a shared scalar is never itself a pair.
    """
    if v is None:
        return default
    if isinstance(v, (tuple, list)) and len(v) == 2 \
            and not any(isinstance(x, (tuple, list)) for x in v):
        return v[i]
    return v


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
    prs = m.get("pr", pr_default)
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
        for i, (c, cp) in enumerate(((LX, clip_l), (RX, clip_r))):
            d = per_num(m["lid"], i, 0)
            if not d:
                continue
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
        po = m.get("pupils", (0, 0))
        spark = m.get("spark", 1.0)
        for i, c in enumerate((LX, RX)):
            dx, dy = per_pair(po, i)
            pr = per_num(prs, i, pr_default)
            sp = per_num(spark, i, 1.0)
            if flat:
                k.append(f'<circle cx="{c+dx}" cy="{CY+dy}" r="{pr+1.5}" fill="#000"/>')
            else:
                o.append(f'<g class="iyi-pupil">'
                         f'{pupil(c + dx, CY + dy, pr, ink, spark=sp)}</g>')
    return "".join(o), "".join(k)



def build(mood="watch", flat=None, ink=INK, grad=True):
    """A standalone iYi, with its own stylesheet so it still animates when the
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
            'width="118" height="118" role="img" aria-label="iYi">'
            f'<title>iYi - {mood}</title>{"".join(o)}</svg>')


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
    so a page full of iYi is not blinking in unison, which is the single
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
    # stays the single source of truth for how iYi moves
    css = ROOT / "css" / "mascot.css"
    css.parent.mkdir(parents=True, exist_ok=True)
    header = ("/* generated by tools/mascot.py - do not edit by hand.\n"
              "   iYi's animation rig. Each part is its own group, so a blink is\n"
              "   scaleY() on .iyi-pupil and a look-around is translateX() on it.\n"
              "   --d staggers the copies; it inherits, animation-delay does not. */\n")
    css.write_text(header + MASCOT_CSS + "\n", encoding="utf-8")

    for m in MOODS:
        (out / f"iyi-{m}.svg").write_text(build(m), encoding="utf-8")

    # The flat single-colour exports are committed assets, so they are written
    # unconditionally. They used to be behind a --flat flag, which meant a plain
    # run silently left them stale: the stamp and screen-print versions were
    # still carrying the previous geometry and the previous pupil radius while
    # the site showed the new face. Nothing failed, nothing looked wrong, the
    # files on disk were simply out of date - which is the worst way for an
    # asset to rot, because a merch export is the one thing nobody re-examines.
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



