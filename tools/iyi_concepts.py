"""Render asymmetric iYi candidates for review.

iYi is the conduit in a relationship that is not reciprocated, and its two
pupils are the two sides - you, and them. The rig could not express that: pupil
offset and radius were single shared values applied to both eyes, so every
version rendered the symmetry the site argues against. eyes_mkup now takes
those per eye.

These are concepts, not moods. The point is to choose the asymmetry by looking
rather than by reading a description of it, because "asymmetric" can mean gaze,
scale, light, or some combination, and the difference is entirely visual.
"""
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import mascot as M

OUT = pathlib.Path(r"C:\Users\paras\Documents\Default Project\parasocialize\img\mascot")

# name, mood dict, what it is testing
CANDIDATES = [
    ("asym-gaze", dict(lid=0.0, pr=12, blush=True,
                       pupils=((0, 2), (5, 6))),
     "gaze split - one pupil looks at you, one looks off"),
    ("asym-scale", dict(lid=0.0, pr=(14, 8), blush=True,
                        pupils=(0, 3)),
     "scale split - one side engaged, one side distant"),
    ("asym-spark", dict(lid=0.0, pr=12, blush=True, spark=(1.0, 0.18),
                        pupils=(0, 3)),
     "light split - same pupils, only one catches the light"),
    ("asym-both", dict(lid=(0.0, 6.0), pr=(13, 9), blush=True, spark=(1.0, 0.3),
                       pupils=((0, 2), (4, 5))),
     "combined - gaze, scale and light together"),
    ("asym-flat", dict(lid=0.0, pr=(14, 9), blush=True, spark=(1.0, 0.2),
                       pupils=((0, 2), (4, 4))),
     "one side present, one side barely there"),
]

cards = []
for name, mood, why in CANDIDATES:
    mood = dict(mood)
    mood.setdefault("_why", why)
    # inline() resolves through MOODS, so register the candidate temporarily
    M.MOODS[name] = mood
    svg = M.inline(190, "", name)
    cards.append(f'<figure><div class="art">{svg}</div>'
                 f'<figcaption><b>{name}</b><span>{why}</span></figcaption></figure>')
    # a small stamp at nav scale, to check it survives being tiny
    small = M.inline(34, "", name)
    cards.append(f'<figure class="tiny"><div class="art">{small}</div>'
                 f'<figcaption><b>{name} @34px</b><span>does it read small?</span></figcaption></figure>')

html = f"""<!DOCTYPE html><meta charset="utf-8"><style>
*{{margin:0;padding:0;box-sizing:border-box}}
body{{background:#130d0a;color:#fff6ea;font:15px/1.45 system-ui,sans-serif;padding:34px}}
h1{{font-size:19px;letter-spacing:.16em;text-transform:uppercase;color:#ff5a1f;margin-bottom:6px}}
p.sub{{color:#cbb59d;margin-bottom:26px;max-width:76ch}}
.grid{{display:grid;grid-template-columns:repeat(auto-fill,minmax(232px,1fr));gap:20px}}
figure{{background:#1d1512;border:1px solid rgba(255,246,234,.1);border-radius:12px;padding:16px}}
.tiny .art svg{{width:34px;height:34px}}
.art{{display:flex;align-items:center;justify-content:center;min-height:200px;margin-bottom:12px}}
.tiny .art{{min-height:70px}}
figcaption b{{display:block;font-family:ui-monospace,monospace;font-size:12px;color:#ffa64d}}
figcaption span{{display:block;font-size:12.5px;color:#9a8672;margin-top:3px}}
</style>
<h1>iYi &mdash; the two sides</h1>
<p class="sub">Each pupil is one side of a relationship that is not reciprocated.
The rig previously applied one offset and one radius to both eyes, so every
version was symmetric. These test four ways to break that symmetry, plus a
nav-scale stamp of each to see whether it survives at 34px.</p>
<div class="grid">{''.join(cards)}</div>"""

p = pathlib.Path(r"C:\Users\paras\AppData\Local\Temp\opencode\asym.html")
p.write_text(html, encoding="utf-8")
print(f"  wrote {p}")
for name, _, why in CANDIDATES:
    print(f"    {name:12} {why}")
