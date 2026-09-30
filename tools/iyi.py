#!/usr/bin/env python3
"""
iyi.py - Iyi as an actor, rather than a stamp in the corner.

THE ASK WAS "the brand character needs to be animated throughout in a manner
reflecting topic of video". Two halves to that, and the second is the harder
one.

"Animated throughout" is easy and was already half true: the mascot ships with
breathing, blinking and a bloom pulse baked into its own stylesheet. The problem
was that it appeared on one frame of eight, in a fixed mood, doing the same idle
loop whatever the episode was about. That is a logo with a heartbeat.

"Reflecting topic" is the part that makes it a character rather than an
ident, and it works because the entry already knows what it is. The motion is
driven off `medium`, so it is not a designer choosing a look per episode - the
episode's own subject chooses:

    ai / companion   the two pupils drift out of phase with each other and the
                     bloom pulses fast and unevenly. two signals, one direction
    television       the whole character flickers on the scanline period, and a
                     horizontal slice of it tears sideways. seen on a screen
    games            a stepped bob and a squash on the landing frame, on a
                     stepped timing curve so it moves in whole pixels
    music            scale locked to the equaliser's phase, so Iyi is on the
                     same beat as the bars behind it
    film             projector flicker: brief opacity dips and a small vertical
                     jump, irregular, the way a projector does
    literature       a very slow drift and a long pause between blinks, the
                     rhythm of somebody reading
    sport            a scale pop as the crowd ripple passes through it
    theology         a deep slow breath and a rare blink, with the stone arcs
                     turning behind
    technology       the pupils snap to follow the travelling pulse

AND FOUR BEHAVIOURS, keyed to the scene, which is what gives it an arc:

    hook     alert    pupils wide, bloom up, leaning in
    beats    idle     the default loop
    pivot    react    a wink. this is the turn in the argument, and a wink is
                      the closest a face with no mouth gets to saying "got it"
    why      reflect  still, square to camera, one slow deliberate blink

The pivot is the reason this module exists. A retention reset at the midpoint
only works if something visibly happens there, and a text card does not change;
a character reacting does. The turn and the brand identity land in the same
frame.

THE SVG IS NOT INLINED BLIND
mascot.build() is the geometry and it stays the single source of truth. What
comes back is a complete standalone SVG with its own <style>. Those selectors
are document-global (".iyi", ".iyi-pupil"), so they are rewritten to scope under
.act before being dropped into a page that has other things on it, and the topic
rules are appended to the same scoped block.
"""
from __future__ import annotations

import math
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))
import mascot as M  # noqa: E402

# scene kind -> (mood, behaviour)
BEHAVIOUR = {
    "hook":  ("watch", "alert"),
    "card":  ("watch", "idle"),
    "beat":  ("watch", "idle"),
    "pivot": ("wink",  "react"),
    "why":   ("watch", "reflect"),
    "end":   ("love",  "idle"),
}

# how hot the character runs, by lane. manipulation is twitchy, consideration
# is slow, application is calm. The lane is the argument the entry is making, so
# the character argues it with it.
LANE_TUNE = {
    "application":   dict(rate=1.0, bloom=1.0, wide=0.0, glitch=0.0),
    "consideration": dict(rate=0.82, bloom=0.86, wide=0.04, glitch=0.0),
    "manipulation":  dict(rate=1.28, bloom=1.3, wide=0.10, glitch=0.5),
}


def _system(entry: dict) -> str:
    media = entry.get("medium") or []
    for m in media:
        if m in ("ai",):
            return "ai"
        if m.startswith("television"):
            return "television"
        if m == "games":
            return "games"
        if m == "music":
            return "music"
        if m == "film":
            return "film"
        if m == "literature":
            return "literature"
        if m == "sport":
            return "sport"
        if m == "theology":
            return "theology"
        if m == "technology":
            return "technology"
    y = entry.get("year") or 2000
    return "theology" if y < 1900 else "technology"


def _topic_css(system: str, lane: str) -> tuple[list[str], str]:
    """(extra keyframes, extra rules) for one topic+lane combination.

    Durations are written as calc() against --r so the lane can speed the whole
    character up or down by changing one number, rather than by editing six
    timings and hoping they stay in proportion.
    """
    t = LANE_TUNE.get(lane, LANE_TUNE["application"])
    r = t["rate"]
    bloom = t["bloom"]
    wide = t["wide"]
    gl = t["glitch"]

    k: list[str] = []
    c: list[str] = []

    # --- the behaviours, common to every topic -------------------------------
    k += [
        "@keyframes iy-alert{0%,100%{transform:scale(1)}50%{transform:scale(1.06)}}",
        "@keyframes iy-lean{0%,100%{transform:translate(0,0)}"
        "50%{transform:translate(0,7px)}}",
        "@keyframes iy-wide{0%,100%{transform:scale(1)}50%{transform:scale(1.16)}}",
        "@keyframes iy-recoil{0%{transform:scale(1)}18%{transform:scale(1.1) "
        "translateY(-6px)}42%{transform:scale(.97)}70%{transform:scale(1.02)}"
        "100%{transform:scale(1)}}",
        "@keyframes iy-still{0%,100%{transform:none}}",
        "@keyframes iy-blink-once{0%,42%{transform:scaleY(1)}46%{transform:scaleY(.06)}"
        "50%,100%{transform:scaleY(1)}}",
    ]
    c += [
        # alert: the bloom comes up and the whole glyph leans in
        f'.act.b-alert .iyi{{animation:iyi-breathe calc(4.2s/{r}) ease-in-out infinite,'
        f"iy-alert calc(3.1s/{r}) ease-in-out infinite}}",
        f'.act.b-alert .iyi-bloom{{animation:iyi-bloom-pulse calc(2.4s/{r}) '
        f"ease-in-out infinite}}",
        f".act.b-alert .act-body{{animation:iy-lean calc(5s/{r}) ease-in-out infinite}}",
        # react: the wink carries it, plus a small recoil on the whole character
        f'.act.b-react .iyi{{animation:iyi-breathe calc(4s/{r}) ease-in-out infinite,'
        f"iy-recoil 1.15s cubic-bezier(.2,1.5,.4,1) infinite}}",
        f".act.b-react .act-body{{animation:iy-recoil 1.15s "
        f"cubic-bezier(.2,1.5,.4,1) infinite}}",
        f'.act.b-react .iyi-bloom{{animation:iyi-bloom-pulse .8s ease-in-out infinite}}',
        # reflect: everything stops except one deliberate blink
        ".act.b-reflect .act-body{animation:iy-still 6s linear infinite}",
        ".act.b-reflect .iyi-pupil{animation:iyi-blink calc(7.4s) linear infinite}",
    ]

    # --- the topic ------------------------------------------------------------
    if system == "ai":
        k += [
            "@keyframes iy-drift-a{0%,100%{transform:translate(0,0)}"
            "50%{transform:translate(-7px,4px)}}",
            "@keyframes iy-drift-b{0%,100%{transform:translate(0,0)}"
            "50%{transform:translate(6px,-5px)}}",
            "@keyframes iy-irregular{0%,100%{opacity:.3}20%{opacity:.55}"
            "45%{opacity:.34}70%{opacity:.62}88%{opacity:.3}}",
        ]
        c += [
            # the two eyes out of phase: one system, two signals, one direction
            ".act.t-ai .iyi-pupil:first-of-type{animation:iyi-blink 5.2s linear infinite,"
            "iy-drift-a 6.1s ease-in-out infinite}",
            ".act.t-ai .iyi-pupil:last-of-type{animation:iyi-blink 6.7s linear infinite,"
            "iy-drift-b 7.3s ease-in-out infinite}",
            f".act.t-ai .iyi-bloom{{animation:iy-irregular calc(1.5s/{r}) "
            "ease-in-out infinite}}",
        ]
    elif system == "television":
        k += [
            "@keyframes iy-flicker{0%,100%{opacity:1}3%{opacity:.72}6%{opacity:1}"
            "17%{opacity:.86}23%{opacity:1}51%{opacity:.7}57%{opacity:1}"
            "79%{opacity:.88}84%{opacity:1}}",
            "@keyframes iy-tear{0%,100%{transform:translate(0,0)}"
            "28%{transform:translate(-5px,0)}31%{transform:translate(6px,0)}"
            "64%{transform:translate(3px,0)}67%{transform:translate(0,0)}}",
        ]
        c += [
            # on the scanline period, and a slice of it torn sideways
            ".act.t-television .act-body{animation:iy-flicker 7s steps(1,end) infinite,"
            "iy-tear 11s steps(1,end) infinite}",
        ]
    elif system == "games":
        k += [
            "@keyframes iy-hop{0%,100%{transform:translateY(0)}"
            "25%{transform:translateY(-16px)}50%{transform:translateY(0)}"
            "75%{transform:translateY(-8px)}}",
            "@keyframes iy-squash{0%,100%{transform:scale(1,1)}"
            "12%{transform:scale(1.14,.84)}30%{transform:scale(.94,1.08)}"
            "44%{transform:scale(1,1)}}",
        ]
        c += [
            # stepped timing: it moves in whole pixels, like a sprite
            ".act.t-games .act-body{animation:iy-hop 1.1s steps(4,end) infinite}",
            ".act.t-games .iyi{animation:iy-squash 1.1s steps(4,end) infinite}",
        ]
    elif system == "music":
        k += ["@keyframes iy-beat{0%,100%{transform:scale(1)}"
              "18%{transform:scale(1.07)}34%{transform:scale(.98)}"
              "50%{transform:scale(1.05)}70%{transform:scale(1)}}"]
        c += [".act.t-music .iyi{animation:iy-beat 2.6s ease-in-out infinite}",
              ".act.t-music .iyi-bloom{animation:iyi-bloom-pulse 1.3s "
              "ease-in-out infinite}"]
    elif system == "film":
        k += ["@keyframes iy-proj{0%,100%{opacity:1;transform:translateY(0)}"
              "4%{opacity:.7}8%{opacity:1;transform:translateY(-3px)}"
              "11%{transform:translateY(0)}37%{opacity:.82}"
              "41%{opacity:1;transform:translateY(2px)}44%{transform:translateY(0)}"
              "79%{opacity:.88;transform:translateY(-2px)}83%{transform:translateY(0)}"]
        c += [".act.t-film .act-body{animation:iy-proj 6.5s steps(1,end) infinite}"]
    elif system == "literature":
        k += ["@keyframes iy-slow{0%,100%{transform:translate(0,0)}"
              "50%{transform:translate(3px,-6px)}}",
              "@keyframes iy-read{0%,86%{transform:scaleY(1)}89%{transform:scaleY(.1)}"
              "92%,100%{transform:scaleY(1)}}"]
        c += [".act.t-literature .act-body{animation:iy-slow 13s ease-in-out infinite}",
              ".act.t-literature .iyi-pupil{animation:iy-read 9.5s linear infinite}"]
    elif system == "sport":
        k += ["@keyframes iy-ripple{0%,100%{transform:scale(1)}"
              "30%{transform:scale(1.12)}55%{transform:scale(.97)}"
              "75%{transform:scale(1.04)}}"]
        c += [".act.t-sport .iyi{animation:iy-ripple 2.8s ease-in-out infinite}",
              ".act.t-sport .act-body{animation:iy-ripple 2.8s ease-in-out infinite}"]
    elif system == "theology":
        k += ["@keyframes iy-deep{0%,100%{transform:scale(1)}"
              "50%{transform:scale(1.045)}}"]
        c += [".act.t-theology .iyi{animation:iy-deep 11s ease-in-out infinite}",
              ".act.t-theology .iyi-pupil{animation:iyi-blink 13s linear infinite}",
              ".act.t-theology .iyi-bloom{animation:iyi-bloom-pulse 8s "
              "ease-in-out infinite}"]
    else:  # technology
        k += ["@keyframes iy-track{0%,100%{transform:translate(0,0)}"
              "50%{transform:translate(9px,-3px)}}",
              "@keyframes iy-ping{0%{opacity:0;transform:scale(1)}"
              "12%{opacity:.5}100%{opacity:0;transform:scale(1.7)}}"]
        c += [".act.t-technology .iyi-pupil{animation:iyi-blink 4.6s linear infinite,"
              "iy-track 3.2s cubic-bezier(.7,0,.3,1) infinite}",
              ".act.t-technology .act-ping{animation:iy-ping 2.4s ease-out infinite}"]

    if wide:
        c.append(f".act .iyi-pupil{{--wide:{wide:.2f}}}")
    if gl:
        c.append(f".act{{--glitch:{gl:.2f}}}")
    return k, c


def perform(entry: dict, kind: str) -> str:
    """A complete, self-contained, topic-tuned Iyi for one scene. Returns HTML.

    Sized and positioned by the caller, so the same fragment works in a 1080x1920
    episode frame and in a smaller preview without a second implementation.
    """
    mood, beh = BEHAVIOUR.get(kind, ("watch", "idle"))
    system = _system(entry)
    lane = (entry.get("lanes") or ["application"])[0]

    svg = M.build(mood)
    # mascot.build emits a standalone document with a global <style>; rewrite the
    # selectors so they cannot reach anything else on the page, then append the
    # topic rules to the same block.
    def scope(m):
        return ".act " + m.group(0)
    svg = re.sub(r"(?<![\w-])\.(iyi[\w-]*)", scope, svg)

    k, c = _topic_css(system, lane)
    style = ("<style>"
             + "".join(k) + "".join(c) +
             ".act{--r:1}"
             "</style>")
    svg = svg.replace("</defs>", "</defs>" + style, 1) if "</defs>" in svg else \
        style + svg
    # a ping ring for the technology topic only
    ping = ('<div class="act-ping"></div>' if system == "technology" else "")
    return (f'<div class="act b-{beh} t-{system}">'
            f'<div class="act-body">{ping}{svg}</div></div>')
