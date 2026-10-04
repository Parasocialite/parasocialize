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
#
# This used to be two stops of warm apricot into coral, on the reasoning that a
# warm monochrome ages better than a multi-hue gradient. The gradient argument
# was right and the colour was catastrophically wrong.
#
# A warm mid-value ramp on two large round masses is a ramp on SKIN. Rendered,
# iYi read as a pair of breasts: the domes were flesh-coloured, the dark pupil
# sat low and centred like a nipple with a specular highlight above it, the
# bottom-weighted third stop gave the mass weight, and the blush ellipses were
# areola shading. Nothing about the geometry said body. The palette said it.
#
# So the fix is not a smaller tweak to the hue - it is to move the warmth
# INSIDE the eye and let the surface be what an eye surface is: bright, cool,
# low-saturation. Warmth now lives in the iris and the catchlight, which is
# where warmth reads as life in a face rather than as skin on a shape.
#
# Saturation and hue trends move; the fact that an eye is not a breast does not.
# ---------------------------------------------------------------------------
# Sclera. Cool and luminous, not warm and fleshy. #ffffff at the light, falling
# to a soft blue-grey at the shadowed edge - the same three-stop construction as
# before, but on the other side of neutral, so it reads as wet and lit.
SCLERA = ("#ffffff", "#dbe3ee")
# The dark rim of the eye. Every drawn eye has one and no lump of flesh does.
# Cool near-black rather than warm brown, so the ring belongs to the eye.
LIMBUS = "#141a24"
# Iris. The warm accent, relocated. An amber ring around the pupil is where a
# warm colour reads as somebody being there; the same warm on the sclera reads
# as a body.
# Amber, but a dark amber. The first attempt was #e08b1e / #8a4409, and the
# size ladder showed what that costs: the iris is only IRIS_RIM units wide, so
# a bright warm ring at 16px is four saturated pixels and the eye reads as
# brown all over - the old warm problem returning one layer down. Deepened so
# the warm survives as a ring at every size the site uses, and still reads as
# iris rather than as pupil. Verified at 16/24/34/48/96px.
IRIS = ("#d9a441", "#8a5a12")
# How wide the iris ring is, in units. Constant rather than proportional, so a
# bigger pupil eats the white instead of swallowing its own iris.
IRIS_RIM = 3.2
# The pupil has to leave room for the white. This is the number the redesign
# turned on: at pr=16 against a 25 lobe, minus a 3.2 iris and a 3-wide limbus
# stroke and a 3-wide lid, the white was left a 5-unit ring with three dark
# bands crowding it. A radial luminance profile showed the sclera's 90th
# percentile at 250 and its mean at 65 - i.e. the brightest thing in the eye was
# the lid, not the white, which is precisely the "dark mass with a shine on it"
# problem wearing a new costume. The white is what makes a shape read as an eye,
# so it gets the room. Pupil radii in the mood table are set against this.
PUPIL_R = 17.5
# Base eyelid. Every eye has an upper lid; without one a circle is just a circle.
LID_BASE = 4.4
ACCENT = "#e0533f"
INK = "#231009"
# The pupil is large on purpose. It used to be 12 against a 26 lobe, which left
# a thick ring of body colour around it and read as clip-art. Cute eyes are
# mostly pupil; the body is a rim, not a field. 17.5 against a 25 lobe fills it
# properly while still leaving enough margin that the lid has somewhere to crop.
PUPIL_R = 17.5


def sclera_grad(gid):
    """Light falling on a wet surface, in three stops.

    Same three-stop construction as the warm version it replaces - pale where
    the light lands, through the body, and a deeper tone at the far edge so the
    form turns away from the light instead of stopping flat. What changed is the
    side of neutral it sits on. A warm three-stop ramp made the lobes read as
    volume of flesh; a cool one reads as the wet convex surface of an eye,
    which is what it is supposed to be.
    """
    a, b = SCLERA
    deep = "#c2cddd"
    return (f'<linearGradient id="{gid}" x1=".22" y1=".06" x2=".8" y2=".96">'
            f'<stop offset="0" stop-color="{a}"/>'
            f'<stop offset=".5" stop-color="#eef2f8"/>'
            f'<stop offset="1" stop-color="{deep}"/>'
            f'</linearGradient>')


def iris_grad(gid):
    """The iris ring: warm, and small.

    The warmth the lobes used to carry, moved to the one place it reads as life
    rather than skin. It is an annulus around the pupil, so it is also the layer
    that gives the eye its four-step depth - white, iris, pupil, glint - which
    is what a flat disc with a dark middle does not have.
    """
    a, b = IRIS
    return (f'<radialGradient id="{gid}" cx=".42" cy=".36" r=".68">'
            f'<stop offset="0" stop-color="{a}"/>'
            f'<stop offset="1" stop-color="{b}"/>'
            f'</radialGradient>')


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
RIG_CSS = """.iyi,.iyi-bloom,.iyi-lobe,.iyi-pupil,.iyi-gaze,.iyi-lid,.iyi-iris{
 transform-box:fill-box;transform-origin:center}"""

# The life is in the pupil, the light and the movement. Breathing and blinking
# were there; a gaze was not, even though the comment above claimed one - so a
# character whose whole argument is about attention never moved its attention.
#
# A separate .iyi-gaze wrapper rather than a second animation on .iyi-pupil:
# two animations both writing `transform` means the last one wins, so the blink
# would have eaten the look. Nested groups, one transform each.
#
# THE PERIODS MUST SHARE A FACTOR. These ran at 5.4s, 5.4s, 6.6s and 13s, and
# 5.4, 6.6 and 13 have no common factor beyond 2 - so the character's whole
# combined pose only returned to its starting state every
# lcm(54,66,130)/10 = 3861 seconds, about 64 minutes. Nothing that aperiodic ever
# settles: a viewer cannot learn it, and it was reported as "the pink is moving
# erratically". The mascot is the pink, via --hot on the wordmark's i. Four
# unrelated periods is not life, it is drift.
#
# Everything is now built from a 5s base: breath, bloom and blink on 5s, gaze on
# 15s (three base units), so the composite returns to identical every 15 seconds
# - short enough to learn, long enough not to be metronomic. The per-copy --d
# stagger still desynchronises a page full of mascots, so nothing blinks in
# unison; each individual character is simply coherent now.
#
# The bloom is deliberately in phase with the breath. It is the light behind the
# eye, so it should brighten as the character draws breath - one gesture, not two.
GAZE_CSS = """@keyframes iyi-look{0%,18%{transform:translate(0,0)}
 38%{transform:translate(2.4px,-.6px)}
 58%{transform:translate(2.4px,-.6px)}
 78%{transform:translate(-.9px,.4px)}
 90%,100%{transform:translate(0,0)}}"""

BLINK_CSS = """@keyframes iyi-breathe{0%,100%{transform:scale(1)}
 50%{transform:scale(1.035)}}
@keyframes iyi-blink{0%,90%,100%{transform:scaleY(1)}93%{transform:scaleY(.08)}}
@keyframes iyi-bloom-pulse{0%,100%{opacity:.26}50%{opacity:.42}}
.iyi{animation:iyi-breathe 5s ease-in-out infinite;animation-delay:var(--d,0s)}
.iyi-pupil{animation:iyi-blink 5s ease-in-out infinite;animation-delay:var(--d,0s)}
.iyi-gaze{animation:iyi-look 15s ease-in-out infinite;animation-delay:var(--d,0s)}
.iyi-bloom{animation:iyi-bloom-pulse 5s ease-in-out infinite;animation-delay:var(--d,0s)}
@media (prefers-reduced-motion:reduce){
 .iyi,.iyi-pupil,.iyi-gaze,.iyi-bloom{animation:none}}"""

MASCOT_CSS = RIG_CSS + "\n" + GAZE_CSS + "\n" + BLINK_CSS


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
    """The dark pupil, its iris, and the light on it.

    Deliberately not a tiny dot in a big pale lobe - that reads as a googly eye
    and looks startled. A large dark pupil with a soft highlight reads as warm,
    and warmth is the brief for this character.

    The life the brief asks for lives in three layers here, and in the rig:

      - the iris annulus around the pupil, warm, which is the warmth moved off
        the sclera and into the eye
      - the big round catchlight, which is a reflection of a light source and
        not a highlight painted on
      - the four-point sparkle, which is the shape every eye animation uses to
        say somebody is in there, and the concave waist is what makes it read
        as a sparkle rather than a diamond

    The pairing is the point: a lone circle looks like a sticker. The lower rim
    is what makes the eye read as wet rather than printed, and spark scales all
    three so a mood can fade one side's light out entirely - nobody home,
    without needing a lid to say it.
    """
    o = [f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="{ink}"/>']
    if hi and spark > 0.02:
        s = max(0.0, min(1.0, spark))
        o.append(f'<circle cx="{cx-r*0.3}" cy="{cy-r*0.34}" r="{r*0.29*s}" fill="#ffffff"/>')
        o.append(f'<path d="{star_d(cx+r*0.27, cy+r*0.31, r*0.29*s)}" '
                 f'fill="#ffffff" opacity="{round(0.92*s, 3)}"/>')
        o.append(f'<circle cx="{cx-r*0.14}" cy="{cy+r*0.5}" r="{r*0.09*s}" '
                 f'fill="#ffffff" opacity="{round(0.5*s, 3)}"/>')
    return "".join(o)


def lid_arc(cx, inset=4.2, width=3.0, a0=154, a1=26):
    """The upper eyelid: a thick stroke arcing over the top of the eye.

    Drawn as a stroke rather than the filled crescent below because a crescent
    hugging the rim is indistinguishable from the limbal ring - the two merge
    into one grey edge and the eye has no opening.

    Angles are degrees measured from twelve o'clock, so `a0` is how far round
    the LEFT the stroke starts and `a1` how far round the right it ends. Getting
    these the wrong way round is not a subtle error: a stroke that runs from 12
    degrees round to 168 crosses straight over the middle of the eye and paints
    a dark bar across the pupil. It did, and the mood sheet is what showed it -
    which is the argument for looking at the drawing rather than reasoning about
    the geometry.

    Swept 168 to 12 means it wraps the whole top and dies just past the widest
    point of the eye on each side, which is where a real upper lid ends.
    """
    import math
    r = R - inset
    pt = lambda a: (cx + r * math.sin(math.radians(a)),
                    CY - r * math.cos(math.radians(a)))
    x0, y0 = pt(a0)
    x1, y1 = pt(a1)
    large = 1 if (a1 - a0) % 360 > 180 else 0
    return (f"M{x0:.2f} {y0:.2f}"
            f"A{r:.2f} {r:.2f} 0 {large} 1 {x1:.2f} {y1:.2f}")


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
    "watch":  dict(lid=(0.0, 3.5), pr=(12.5, 10.5), spark=(1.0, 0.62),
                   pupils=((0, 1.5), (3, 3.5)),
                   note="the default. the two sides, unequal. one of them is you."),
    "hollow": dict(lid=(15, 19), pupils=((0, 5), (3, 7)), pr=(9.5, 8), spark=(0.55, 0.0),
                   note="nobody is home. the joke of the whole site."),
    "wink":   dict(lid=0.0, pupils=((0, 2), (3, 3)), pr=(12, 10),
                   spark=(1.0, 0.55), shut="r",
                   note="pull quotes."),
    "sad":    dict(lid=(13, 17), pupils=((0, 4), (2, 6)), pr=(11, 9), spark=(0.85, 0.28),
                   note="grief. the obituary cards."),
    "panic":  dict(lid=5,    pupils=((0, -4), (2, -5)), pr=(9, 7.5), spark=(1.0, 0.4),
                   note="the sweep is late and the clock is red."),
    "love":   dict(lid=0.0,  hearts=True, note="the club. ONLY for a romantic beat."),
    "clerk":  dict(lid=4,    pupils=((0, 2), (2, 3)), pr=(12, 10), spark=(1.0, 0.5),
                   note="behind the counter. Enan's own tell."),
    # "asleep" is eyes-closed, and the note has to be true as well as funny. It
    # used to read "sweeping hourly, seven past" - a claim about the sweeper,
    # rendered in the mood grid on a page whose footer says the site does not
    # pretend about freshness, when the sweeper has never run once. The honest
    # version is also the better joke: it is asleep because nothing is sweeping.
    "asleep": dict(shut=True, note="asleep at the counter. the sweep has not run."),
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
              lobe_mask="", iris="none"):
    """The two lobes and everything that lives inside them.

    Clipping is what makes this safe: the lobes are the clip paths, so the lid,
    the iris and the pupil are all guaranteed to stay within the silhouette
    whatever the mood asks for. That guarantee is the whole reason the
    character stopped looking like a bug.

    Returns (markup, knockouts). The knockouts are the same inner shapes again,
    as black, for the single-colour build to punch out of its mask - so a stamp
    and a screen print are the same drawing rather than two drawings that drift.
    """
    prs = m.get("pr", pr_default)
    # The pupil has to leave room for the white, and this is a geometric floor
    # rather than a taste call: the iris needs IRIS_RIM, the limbal stroke needs
    # 1.5, and whatever is left over is the white that makes the shape read as an
    # eye. At pr=16 against a 25 lobe the white was 5.4 units with three dark
    # bands crowding it - the sclera's 90th percentile was 250 while its mean was
    # 65, which means the brightest thing in the eye was the lid, not the white.
    #
    # Moods that ask for a pupil big enough to swallow the white get clamped to
    # the largest that leaves WHITE_MIN of it, so the geometry cannot be undone
    # by editing the mood table.
    WHITE_MIN = 5.0
    max_pr = R - 1.5 - IRIS_RIM - WHITE_MIN
    # Defensive: the iris has silently not been drawn once already, and a
    # missing layer is invisible in every aggregate - the eye still renders, the
    # page still builds, the mood sheet still looks plausible. Assert the caller
    # actually supplied one when this is not the flat build.
    if not flat and iris == "none":
        raise ValueError(
            "eyes_mkup called without an iris. Pass iris=..., or flat=... - a "
            "missing layer in a character is the kind of defect that ships "
            "because nothing raises.")
    # The limbal ring and the sclera, in that order: the ring is the dark rim of
    # the eye, drawn as a stroke on the lobe itself so it cannot drift outside
    # the silhouette. It is the single strongest cue that a circle is an eye -
    # a lump of flesh has no rim, and the drawing read as flesh until it had one.
    lobe = (f'<g class="iyi-lobe"{lobe_mask}>'
            f'<circle cx="{{c}}" cy="{CY}" r="{R}" fill="{{body}}"/>'
            + ("" if flat else
               f'<circle cx="{{c}}" cy="{CY}" r="{R - 1.5}" fill="none" '
               f'stroke="{LIMBUS}" stroke-width="3" stroke-opacity=".92"/>')
            + '</g>')
    o = [lobe.format(c=LX, body=body), lobe.format(c=RX, body=body)]
    k = []

    # Blush is gone. It was ACCENT-coloured ellipses sitting on the lower part of
    # each lobe, which on a warm ramp read as areola shading and was most of why
    # the whole thing read as a body. Expression now comes from where it should:
    # lid depth, pupil offset, iris size and the light on the pupil.

    # A permanent eyelid line on both eyes, so every circle has an upper lid and
    # reads as an opening rather than a disc. Mood depth is drawn on top of it
    # as a filled crescent, which is what crops the pupil - the stroke says
    # "eye", the crescent says "how much of it is showing".
    if not flat:
        for c, cp in ((LX, clip_l), (RX, clip_r)):
            o.append(f'<g class="iyi-lid"><g clip-path="url(#{cp})">'
                     f'<path d="{lid_arc(c)}" stroke="{ink}" stroke-width="3" '
                     f'stroke-linecap="round" fill="none"/></g></g>')
        for i, (c, cp) in enumerate(((LX, clip_l), (RX, clip_r))):
            d = per_num(m.get("lid"), i, 0)
            if not d:
                continue
            o.append(f'<g class="iyi-lid"><g clip-path="url(#{cp})">'
                     f'<path d="{lid_d(c, d)}" fill="{ink}"/></g></g>')
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
    elif not m.get("shut") or m.get("shut") == "r":
        po = m.get("pupils", (0, 0))
        spark = m.get("spark", 1.0)
        for i, c in enumerate((LX, RX)):
            # shut="r" means shut the RIGHT eye. The guard used to be
            # `elif not m.get("shut")`, and "r" is truthy - so both eyes skipped
            # the pupil and wink, the mood used for pull quotes, shipped with a
            # blank white disc where its open eye should have been. Verified in
            # the committed module, not introduced here.
            if m.get("shut") == "r" and c == RX:
                continue
            dx, dy = per_pair(po, i)
            pr = min(float(per_num(prs, i, pr_default)), max_pr)
            sp = per_num(spark, i, 1.0)
            if flat:
                # The pupil and the iris both get knocked out of the mask, and
                # they are drawn pupil-last in the real build, so the knockout
                # has to punch the larger iris first or the two would fight over
                # the same ring. Painted order is the same as the site.
                if iris != "none":
                    k.append(f'<circle cx="{c+dx}" cy="{CY+dy}" '
                             f'r="{pr + IRIS_RIM:.2f}" fill="#000"/>')
                k.append(f'<circle cx="{c+dx}" cy="{CY+dy}" r="{pr}" fill="#000"/>')
            else:
                # The iris is its own group, OUTSIDE .iyi-gaze and .iyi-pupil, so
                # the gaze drift and the blink cannot carry it off the eye with
                # the pupil. It had been drawn inside .iyi-pupil as the pupil's
                # first child, which meant a blink scaleY() squashed the iris
                # too - and a gaze translate slid the iris bodily off the sclera.
                # Both were invisible in a still and obvious in motion, which is
                # the reason the rig draws these parts separately at all.
                # .iyi-gaze wraps .iyi-pupil: one transform each, so the blink
                # and the look cannot cancel out
                if iris != "none":
                    o.append(f'<circle class="iyi-iris" cx="{c+dx}" '
                             f'cy="{CY+dy}" r="{pr + IRIS_RIM:.2f}" '
                             f'fill="{iris}" stroke="{ink}" '
                             f'stroke-width="1.1"/>')
                o.append(f'<g class="iyi-gaze"><g class="iyi-pupil">'
                         f'{pupil(c + dx, CY + dy, pr, ink, spark=sp)}'
                         f'</g></g>')
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
    iris = "none" if flat else (f"url(#{gid}i)" if grad else IRIS[0])
    eyes, knock = eyes_mkup(
        flat or (f"url(#{gid})" if grad else SCLERA[0]), ink, cl, cr, m,
        flat=bool(flat), iris=iris,
        lobe_mask=f' mask="url(#{gid}m)"' if flat else "")
    o = [f"<style>{MASCOT_CSS}</style>",
         f'<defs>{"" if flat else bloom_grad(gid + "h")}'
         f'{"" if (flat or not grad) else sclera_grad(gid)}'
         f'{"" if (flat or not grad) else iris_grad(gid + "i")}'
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
                        pr_default=13,
                        iris=(f"url(#{gid}i)" if grad else IRIS[0]))

    o = [f'<defs>{bloom_grad(gid + "h")}'
         f'{"" if not grad else sclera_grad(gid)}'
         f'{"" if not grad else iris_grad(gid + "i")}'
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



