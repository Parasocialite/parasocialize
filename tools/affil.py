#!/usr/bin/env python3
"""affil.py - a domain mark for a figure or entry with no free photograph.

WHY THIS EXISTS
A title plate inside a card that already has a frame reads as a placecard
inside a placecard. The plate belongs on the entry page, where it is the
entry's own title treatment; it is not a portrait and it is not an affiliation
image either. When a figure has no sourced photograph, the honest stand-in is
the domain: a baseball for a ballplayer, a microphone for a singer, a reel for
a film. It says "this is the kind of thing", not "this is the person".

WHAT THESE ARE
Author-drawn SVG marks, not photographs and not club logos. A generic baseball
is safe to publish; the Yankees mark is a trademark. The card carries
"AFFILIATION · NOT A PORTRAIT" on its face, so the stand-in never pretends to
be evidence. The figure card adds a caption; the way card adds a note.

USAGE
    python tools/affil.py            # write img/affil/*.svg
    python tools/affil.py --check    # compare, write nothing
"""
from __future__ import annotations

import pathlib
import sys
import xml.etree.ElementTree as ET

ROOT = pathlib.Path(__file__).resolve().parent.parent
OUT = ROOT / "img" / "affil"

# key: (label, inner SVG markup). The group is 640x480; the icon sits around
# (320, 210), the label at the bottom. Strokes are the site's hot orange.
MARKS = {
    "sport": ("SPORT", """
      <circle cx="300" cy="200" r="86"/>
      <path d="M244 140 Q300 190 356 140"/>
      <path d="M244 260 Q300 210 356 260"/>
      <line x1="386" y1="284" x2="470" y2="368"/>
      <line x1="470" y1="368" x2="486" y2="352"/>
    """),
    "music": ("MUSIC", """
      <rect x="288" y="92" width="64" height="132" rx="32"/>
      <path d="M258 196 Q258 260 320 260 Q382 260 382 196"/>
      <line x1="320" y1="260" x2="320" y2="330"/>
      <line x1="284" y1="330" x2="356" y2="330"/>
      <line x1="280" y1="122" x2="360" y2="122"/>
      <line x1="280" y1="150" x2="360" y2="150"/>
    """),
    "film": ("FILM", """
      <rect x="196" y="170" width="248" height="152" rx="10"/>
      <path d="M196 170 L444 118 L444 170 Z"/>
      <line x1="234" y1="158" x2="268" y2="146"/>
      <line x1="286" y1="146" x2="320" y2="134"/>
      <line x1="338" y1="134" x2="372" y2="122"/>
      <line x1="390" y1="122" x2="424" y2="110"/>
      <line x1="222" y1="206" x2="222" y2="294"/>
      <line x1="418" y1="206" x2="418" y2="294"/>
      <circle cx="320" cy="246" r="30"/>
    """),
    "television": ("TELEVISION", """
      <rect x="196" y="154" width="248" height="158" rx="14"/>
      <line x1="270" y1="106" x2="318" y2="154"/>
      <line x1="370" y1="106" x2="322" y2="154"/>
      <line x1="290" y1="312" x2="350" y2="312"/>
      <line x1="320" y1="312" x2="320" y2="346"/>
      <line x1="270" y1="346" x2="370" y2="346"/>
    """),
    "radio": ("RADIO", """
      <path d="M320 118 L252 330"/>
      <path d="M320 118 L388 330"/>
      <line x1="276" y1="270" x2="364" y2="270"/>
      <line x1="300" y1="218" x2="340" y2="218"/>
      <path d="M220 150 Q180 210 220 270"/>
      <path d="M420 150 Q460 210 420 270"/>
      <path d="M196 118 Q130 210 196 302"/>
      <path d="M444 118 Q510 210 444 302"/>
    """),
    "literature": ("LITERATURE", """
      <path d="M190 150 Q260 132 320 166 Q380 132 450 150 L450 316 Q380 298 320 332 Q260 298 190 316 Z"/>
      <line x1="320" y1="166" x2="320" y2="332"/>
      <path d="M216 186 Q268 174 306 198"/>
      <path d="M216 226 Q268 214 306 238"/>
      <path d="M334 198 Q372 174 424 186"/>
      <path d="M334 238 Q372 214 424 226"/>
    """),
    "comics": ("COMICS", """
      <path d="M196 132 H444 V300 H300 L250 348 V300 H196 Z"/>
      <line x1="236" y1="188" x2="404" y2="188"/>
      <line x1="236" y1="228" x2="404" y2="228"/>
      <line x1="236" y1="268" x2="344" y2="268"/>
      <line x1="360" y1="268" x2="404" y2="268"/>
    """),
    "games": ("GAMES", """
      <path d="M204 174 Q172 174 168 214 L150 302 Q146 336 184 336 Q206 336 220 316 L252 276 H388 L420 316 Q434 336 456 336 Q494 336 490 302 L472 214 Q468 174 436 174 Z"/>
      <line x1="220" y1="226" x2="220" y2="286"/>
      <line x1="190" y1="256" x2="250" y2="256"/>
      <circle cx="408" cy="232" r="12"/>
      <circle cx="438" cy="266" r="12"/>
      <circle cx="378" cy="266" r="12"/>
    """),
    "ai": ("AI", """
      <rect x="238" y="128" width="164" height="164" rx="12"/>
      <rect x="278" y="168" width="84" height="84" rx="8"/>
      <line x1="238" y1="168" x2="198" y2="168"/>
      <line x1="238" y1="212" x2="198" y2="212"/>
      <line x1="238" y1="256" x2="198" y2="256"/>
      <line x1="402" y1="168" x2="442" y2="168"/>
      <line x1="402" y1="212" x2="442" y2="212"/>
      <line x1="402" y1="256" x2="442" y2="256"/>
      <line x1="286" y1="128" x2="286" y2="88"/>
      <line x1="320" y1="128" x2="320" y2="88"/>
      <line x1="354" y1="128" x2="354" y2="88"/>
      <line x1="286" y1="292" x2="286" y2="332"/>
      <line x1="320" y1="292" x2="320" y2="332"/>
      <line x1="354" y1="292" x2="354" y2="332"/>
    """),
    "religion": ("RELIGION", """
      <path d="M236 334 V190 Q236 116 320 116 Q404 116 404 190 V334"/>
      <path d="M268 334 V198 Q268 156 320 156 Q372 156 372 198 V334"/>
      <line x1="320" y1="202" x2="320" y2="286"/>
      <path d="M320 202 Q340 224 320 248 Q300 224 320 202 Z"/>
      <line x1="286" y1="286" x2="354" y2="286"/>
    """),
    "stage": ("STAGE", """
      <path d="M182 128 H458 V330 H182 Z"/>
      <path d="M182 128 Q214 200 196 330"/>
      <path d="M458 128 Q426 200 444 330"/>
      <path d="M226 128 Q244 176 238 330"/>
      <path d="M414 128 Q396 176 402 330"/>
      <path d="M266 128 Q278 166 274 330"/>
      <path d="M374 128 Q362 166 366 330"/>
      <line x1="182" y1="128" x2="458" y2="128"/>
    """),
    "art": ("ART", """
      <rect x="194" y="118" width="252" height="196" rx="4"/>
      <rect x="222" y="146" width="196" height="140" rx="2"/>
      <circle cx="360" cy="182" r="18"/>
      <path d="M222 286 L286 220 L330 260 L366 224 L418 286"/>
    """),
    "tech": ("TECH", """
      <circle cx="320" cy="218" r="58"/>
      <circle cx="320" cy="218" r="18"/>
      <path d="M320 132 V164 M320 272 V304 M234 218 H266 M374 218 H406 M259 157 L282 180 M358 256 L381 279 M381 157 L358 180 M282 256 L259 279"/>
      <path d="M196 334 H444"/>
    """),
    "history": ("HISTORY", """
      <path d="M206 334 H434"/>
      <path d="M226 334 V178 H414 V334"/>
      <path d="M206 178 L320 106 L434 178 Z"/>
      <line x1="262" y1="196" x2="262" y2="316"/>
      <line x1="320" y1="196" x2="320" y2="316"/>
      <line x1="378" y1="196" x2="378" y2="316"/>
      <path d="M196 154 H444"/>
    """),
    "brand": ("BRAND", """
      <path d="M320 108 L438 160 V276 L320 328 L202 276 V160 Z"/>
      <circle cx="320" cy="218" r="44"/>
      <line x1="320" y1="174" x2="320" y2="262"/>
      <line x1="276" y1="218" x2="364" y2="218"/>
    """),
    "persona": ("PERSONA", """
      <path d="M210 132 L320 250 L430 132"/>
      <ellipse cx="320" cy="258" rx="66" ry="76"/>
      <circle cx="298" cy="246" r="9"/>
      <circle cx="342" cy="246" r="9"/>
      <path d="M298 286 Q320 302 342 286"/>
      <line x1="254" y1="258" x2="218" y2="258"/>
      <line x1="386" y1="258" x2="422" y2="258"/>
    """),
    "companion": ("COMPANION", """
      <circle cx="278" cy="212" r="62"/>
      <circle cx="362" cy="212" r="62"/>
      <path d="M320 290 C300 268 276 288 296 310 L320 334 L344 310 C364 288 340 268 320 290 Z"/>
      <path d="M234 330 Q278 298 318 330"/>
      <path d="M322 330 Q362 298 406 330"/>
    """),
    "officer": ("OFFICER", """
      <path d="M320 104 L432 148 V248 Q432 332 320 376 Q208 332 208 248 V148 Z"/>
      <path d="M320 174 L334 212 L374 212 L342 236 L354 274 L320 250 L286 274 L298 236 L266 212 L306 212 Z"/>
    """),
    "predator": ("PREDATOR", """
      <path d="M190 218 Q255 150 320 150 Q385 150 450 218 Q385 286 320 286 Q255 286 190 218 Z"/>
      <circle cx="320" cy="218" r="38"/>
      <circle cx="320" cy="218" r="14"/>
      <line x1="320" y1="120" x2="320" y2="90"/>
      <line x1="230" y1="140" x2="212" y2="112"/>
      <line x1="410" y1="140" x2="428" y2="112"/>
      <line x1="170" y1="218" x2="140" y2="218"/>
      <line x1="470" y1="218" x2="500" y2="218"/>
    """),
    "default": ("THE RECORD", """
      <circle cx="320" cy="218" r="100"/>
      <circle cx="320" cy="218" r="64"/>
      <circle cx="320" cy="218" r="16"/>
      <path d="M320 118 V80 M320 356 V318 M220 218 H182 M458 218 H420"/>
    """),
}


def svg(label: str, inner: str) -> str:
    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 640 480" role="img" aria-label="{label} affiliation mark">
  <rect width="640" height="480" fill="#17100b"/>
  <rect x="18" y="18" width="604" height="444" fill="none" stroke="#3a2a1e" stroke-width="2"/>
  <g fill="none" stroke="#ff5a1f" stroke-width="9" stroke-linecap="round" stroke-linejoin="round">
{inner}
  </g>
  <text x="40" y="414" fill="#fff6ea" font-family="'Courier New', monospace" font-size="28" letter-spacing="5">{label}</text>
  <text x="40" y="444" fill="#9a8672" font-family="'Courier New', monospace" font-size="13" letter-spacing="2">AFFILIATION &#183; NOT A PORTRAIT</text>
</svg>
"""


def main() -> int:
    check = "--check" in sys.argv
    OUT.mkdir(parents=True, exist_ok=True)
    made = same = 0
    for key, (label, inner) in MARKS.items():
        p = OUT / f"{key}.svg"
        text = svg(label, inner)
        if p.exists() and p.read_text(encoding="utf-8") == text:
            same += 1
            continue
        if not check:
            p.write_text(text, encoding="utf-8")
        made += 1
    verb = "would write" if check else "wrote"
    print(f"{verb} {made} affiliation mark(s), {same} current")
    files = sorted(OUT.glob("*.svg"))
    print(f"  {len(files)} marks in img/affil/")
    missing = [k for k in MARKS if not (OUT / f"{k}.svg").exists()]
    if missing:
        print(f"  MISSING {missing}")
        return 1
    # An <img> pointing at invalid XML renders as nothing at all, which is how
    # the first set shipped. Parse every file before the staleness check; a
    # mark that cannot render is a missing image with a plausible filename.
    for p in files:
        try:
            ET.parse(p)
        except ET.ParseError as exc:
            print(f"  INVALID {p.name}: {exc}")
            return 1
    if check and made:
        print("  STALE - run python tools/affil.py")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
