"""The iYi logotype.

The name is the drawing. i-Y-i: two lowercase i for the two selves, a Y for the
fork where they diverge, and the dots on the i's are the catchlights. The
wordmark is asymmetric for the same reason the face is - the left i is the side
that is fully present, the right i is the side that is smaller and dimmer - so
the mark and the mascot say the same thing in two registers.

This exists because of a measurement, not a preference. At 30px the mascot
collapses: the two lobes merge, the pupils merge with them, and the asymmetry
that carries the entire concept stops being visible. Type does not have that
problem, so the nav carries the name instead of a smudge, and the mascot is
only used where it is big enough to be a character rather than a texture.

Built from spans rather than outlined paths on purpose. Outlining a logotype
means shipping glyph data and losing the font stack; spans keep it live text, so
it stays selectable, searchable, scalable and screen-reader legible for free.
"""
from __future__ import annotations

# size: "nav" for the wordmark strip, "hero" for the masthead
SIZES = {
    "nav":  dict(fs="1.02rem", gap="0", y_col="var(--hot)", op_r=".52", sc_r=".86"),
    "hero": dict(fs="clamp(4.2rem,17vw,10.5rem)", gap="0", y_col="var(--hot)", op_r=".5", sc_r=".84"),
}


def wordmark(size: str = "nav", label: bool = True) -> str:
    """The iYi logotype as inline markup.

    The two i's are separate elements so they can differ, which is the entire
    point. The right-hand i is scaled down and dimmed; the Y between them is the
    conduit and takes the accent colour. Screen readers get the whole word once
    rather than as three letters, and the visible glyphs are hidden from them.
    """
    s = SIZES.get(size, SIZES["nav"])
    aria = ' aria-label="iYi"' if label else ""
    return (
        f'<span class="iyiw iyiw-{size}"{aria}>'
        f'<span class="iyiw-l" aria-hidden="true">i</span>'
        f'<span class="iyiw-y" aria-hidden="true">Y</span>'
        f'<span class="iyiw-r" aria-hidden="true">i</span>'
        f"</span>"
    )
