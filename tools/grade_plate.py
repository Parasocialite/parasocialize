"""Grade a generated Iyi plate onto the site palette.

An LTX render is never on-brand on arrival, and the drift is specific rather
than general. Two things are wrong:

  - the background is a COOL near-black. The render comes out on #0b0b0d, which
    is neutral-to-blue, while the site sits on --bg #130d0a. Side by side the
    plate reads as a foreign object rather than a mascot of this site.
  - the body is a desaturated pastel peach. Iyi is #ff8f5e, a saturated warm
    amber, with #ffe7c4 for the pale highlight and #231009 for the pupil.

The grade preserves the luminance ramp rather than flattening toward a target
colour, because the ramp is what carries the sense of volume. Flattening to
#ff8f5e would produce a sticker and throw away the shading the model earned.

Deliberately NOT done: sharpening the catchlights or restoring heart-shaped
pupils. Both are real drift from the SVG, but they are geometry, not colour,
and faking them with filters produces artefacts that read worse than the
original softness. That is a prompt or design fix, not a grade.

Writes a lossless animated webp, so the plate stays a first-class asset rather
than a recompressed derivative of one.
"""
from __future__ import annotations

import colorsys
import pathlib
import sys

import numpy as np
from PIL import Image, ImageSequence

# pulled from styles.css and tools/mascot.py - the actual tokens, not guesses
BG      = (0x13, 0x0d, 0x0a)   # --bg
BODY    = (0xff, 0x8f, 0x5e)   # Iyi amber
HILIGHT = (0xff, 0xe7, 0xc4)   # Iyi pale
PUPIL   = (0x23, 0x10, 0x09)   # Iyi warm near-black
GLOW    = (0xff, 0x5a, 0x1f)   # --hot

BODY_H, _, _ = colorsys.rgb_to_hsv(*(c / 255 for c in BODY))
SAT_GAIN = 1.16      # gentle: the raw body is already close to brand hue
HUE_PULL = 0.30      # nudge toward amber, do not drag
SUBJECT_L = 0.085    # luminance above which a pixel is character, not backdrop
BG_GAIN  = 0.55      # backdrop brightness modulation, keeps the vignette
BG_LIFT  = 0.72      # backdrop floor, so it stays a warm near-black
HI_START = 0.86      # only the very brightest pixels may shift toward HILIGHT


def _rgb(arr):
    return arr


def grade_frame(rgb_u8: np.ndarray) -> np.ndarray:
    """rgb_u8: HxWx3 uint8 -> HxWx3 uint8 graded.

    Kept deliberately minimal. A first pass tried to rebuild the body colour
    from the brand tokens outright and it was worse than doing nothing: the
    backdrop flooded to muddy brown, the lower body was forced to pupil black
    and read as a hard disc, and the body blew out to cream. The raw render is
    already within a few percent of the palette, so the only real defect is the
    COOL backdrop. Fix that, nudge saturation, change nothing else.
    """
    a = rgb_u8.astype(np.float32) / 255.0
    lum = a[..., 0] * 0.2126 + a[..., 1] * 0.7152 + a[..., 2] * 0.0722

    subject = lum > SUBJECT_L
    if not subject.any():
        return rgb_u8

    out = a.copy()

    # ---- backdrop: pure site bg, brightness-modulated to keep the glow falloff.
    # No hue mixing at all: mixing toward --hot at any real strength floods the
    # frame, because the backdrop is most of the pixels and has a wide range.
    bg = ~subject
    if bg.any():
        bl = lum[bg]
        hi_l = float(bl.max())
        rel = (bl / hi_l) if hi_l > 0 else bl
        base = np.array(BG, np.float32) / 255.0
        out[bg] = base * (BG_LIFT + BG_GAIN * rel)[:, None]

    # ---- subject: small saturation lift, small hue pull, ramp untouched
    sub = out[subject]
    hsv = np.array([colorsys.rgb_to_hsv(*p) for p in sub.reshape(-1, 3)])
    h, s, v = hsv[:, 0], hsv[:, 1], hsv[:, 2]
    d = (BODY_H - h + 0.5) % 1.0 - 0.5
    h = (h + d * HUE_PULL) % 1.0
    s = np.clip(s * SAT_GAIN, 0.0, 1.0)
    hi = np.clip((v - HI_START) / (1.0 - HI_START), 0.0, 1.0)
    hsv[:, 0], hsv[:, 1], hsv[:, 2] = h, s, v
    rebuilt = np.array([colorsys.hsv_to_rgb(*r) for r in hsv], np.float32)
    hil = np.array([c / 255 for c in HILIGHT], np.float32)
    # blend toward the pale highlight only at the extreme top of the ramp
    rebuilt = rebuilt * (1 - hi[:, None] * 0.5) + hil * (hi[:, None] * 0.5)
    out[subject] = rebuilt

    return np.clip(out * 255.0, 0, 255).astype(np.uint8)


def main():
    src = pathlib.Path(sys.argv[1])
    dst = pathlib.Path(sys.argv[2])
    frames = [np.asarray(f.convert("RGB"))
              for f in ImageSequence.Iterator(Image.open(src))]
    graded = [grade_frame(f) for f in frames]

    before = np.stack([f.astype(np.float32) for f in frames])
    after = np.stack([f.astype(np.float32) for f in graded])
    print(f"  frames={len(frames)}  size={frames[0].shape[1]}x{frames[0].shape[0]}")
    for i, lbl in ((0, "first"), (len(frames) // 2, "mid"), (len(frames) - 1, "last")):
        b, a = before[i], after[i]
        print(f"  {lbl:5} mean RGB  {tuple(round(float(x),1) for x in b.reshape(-1,3).mean(0))}"
              f"  ->  {tuple(round(float(x),1) for x in a.reshape(-1,3).mean(0))}")
    # warmth = R minus B. a cool cast shows up as this going negative.
    print(f"  warmth R-B: {round(float((before[...,0]-before[...,2]).mean()),2)}"
          f"  ->  {round(float((after[...,0]-after[...,2]).mean()),2)}")

    out = [Image.fromarray(f) for f in graded]
    out[0].save(dst, save_all=True, append_images=out[1:],
                duration=1000 / 24, loop=0, lossless=True, method=4)
    print(f"  wrote {dst}  {dst.stat().st_size/1e6:.2f} MB (lossless)")


if __name__ == "__main__":
    main()
