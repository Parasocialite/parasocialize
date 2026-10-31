"""Contrast of the eight hub tiles on the front page, measured off the pixels.

The tiles are the one place on the front page where body copy is set on a
saturated background rather than on the dark page colour, and the copy used to
be carried by ALPHA - `rgba(18,10,5,.72)` for the deck and `.6` for the "N MORE"
link - over eight different colours. Measured, seven of ten tiles had the deck
below WCAG AA 4.5:1 and nine had the link below it, worst 2.64:1.

**Alpha is not a way to express hierarchy on a variable background.** The site
already had the counter-example on the same tile: `.hub h3` is solid `#120a05`
and was the only text that cleared the large-text threshold on every tile.

WHY IT SAMPLES PIXELS, and the two probes that got it wrong first
  1. Reading `backgroundColor` returned the PAGE colour for every tile at
     1.02:1, because `.hub` paints with a `background` gradient and never sets a
     background-colour. Obviously wrong, and still a confident number.
  2. Computing the gradient arithmetically would need `color-mix(--c 70%,
     transparent)` composited over a photograph at 62% opacity - so the
     arithmetic needs the picture, not the colour.
  3. The third attempt composited the translucent TEXT into the sampled
     background and then compared the RAW text colour against the composite,
     which is text-against-itself. It reported 1.31:1 on tiles that are plainly
     legible in a screenshot.

So: render twice, once as shipped and once with the tile text hidden, sample
the pixels the text sits on, and composite the text colour over them. That is
`getComputedStyle` for what is DECLARED versus the paint for what a reader
SEES, and this check is only about the second.

NOT WIRED INTO link_audit, for the reason verify_narrow and probe_nav are not:
it needs a build, Chrome and PIL, and a gate that runs on every commit is a gate
that eventually gets disabled.

Usage:  python tools/probe_hub_contrast.py     (exits 1 if any ratio < 4.5)
"""
import functools, http.server, pathlib, re, shutil, socketserver, subprocess, sys
import tempfile, threading, html
import numpy as np
from PIL import Image

ROOT = pathlib.Path(__file__).resolve().parent.parent
CHROME = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
if not pathlib.Path(CHROME).exists():
    CHROME = r"C:\Program Files\Google\Chrome\Chrome\Application\chrome.exe"
OUT = ROOT / "episode" / ".chrome" / "frontshots"
OUT.mkdir(parents=True, exist_ok=True)

AA_BODY = 4.5      # WCAG AA for body copy
AA_LARGE = 3.0     # WCAG AA for >=18.66px bold / >=24px


class H(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *a):
        pass


class S(socketserver.ThreadingTCPServer):
    allow_reuse_address = True
    daemon_threads = True


srv = S(("127.0.0.1", 0), functools.partial(H, directory=str(ROOT)))
threading.Thread(target=srv.serve_forever, daemon=True).start()
BASE = f"http://127.0.0.1:{srv.server_address[1]}/"

# Two renders of the same page: one as shipped, one with the hub text removed,
# so the tile can be sampled where the text was.
JS_BOXES = r"""
var out=[];
[].slice.call(document.querySelectorAll('.hub')).forEach(function(t,i){
  var r=t.getBoundingClientRect();
    out.push([i,(t.querySelector('.hub-name')||{}).textContent||'?',
            Math.round(r.left),Math.round(r.top),Math.round(r.width),Math.round(r.height),
            getComputedStyle(t.querySelector('h3')).color,
            getComputedStyle(t.querySelector('p')).color,
            getComputedStyle(t.querySelector('.hub-go')).color].join('|'));
});
var pre=document.createElement('pre'); pre.id='boxes'; pre.textContent=out.join('\n');
document.body.appendChild(pre);
"""

HIDE = "<style>.hub-name,.hub h3,.hub p,.hub-go{visibility:hidden !important}</style>"


def render(extra_head, script, shot, w=1440, h=2600):
    (ROOT / "__hubshot.html").write_text(
        f"<!DOCTYPE html><html><head><meta charset='utf-8'>"
        f"<style>html,body{{margin:0;background:#0b0b0d;overflow:hidden}}"
        f"iframe{{width:{w}px;height:{h}px;border:0;display:block}}</style>"
        f"{extra_head}</head><body><iframe src='index.html'></iframe>"
        f"<script>document.getElementById('f')"
        f"{'' if not script else ''}</script></body></html>", encoding="utf-8")
    # A FRESH profile for every render. This check silently measures a cached
    # stylesheet otherwise: the red test put the translucent deck colour back,
    # confirmed the file changed, and got numbers identical to two decimals on
    # all ten tiles. A gate that cannot see the change it is gating is the
    # "a measurement that cannot see its own subject" trap, in a new costume.
    profile = tempfile.mkdtemp(prefix="hubcr-")
    r = subprocess.run(
        [CHROME, "--headless=new", "--disable-gpu", "--hide-scrollbars",
         "--disable-application-cache", "--disk-cache-size=1",
         "--incognito", f"--user-data-dir={profile}",
         f"--window-size={w + 120},{h + 120}", "--virtual-time-budget=12000",
         f"--screenshot={shot.as_posix()}", BASE + "__hubshot.html"],
        capture_output=True, text=True, timeout=300,
        encoding="utf-8", errors="replace")
    shutil.rmtree(profile, ignore_errors=True)
    if not shot.exists() or shot.stat().st_size < 4000:
        sys.exit(f"no screenshot for {shot.name}: {r.stderr[:200]}")
    try:
        (ROOT / "__hubshot.html").unlink()
    except OSError:
        pass


def lum(rgb):
    def f(v):
        v = v / 255.0
        return v / 12.92 if v <= 0.03928 else ((v + 0.055) / 1.055) ** 2.4
    return 0.2126 * f(rgb[0]) + 0.7152 * f(rgb[1]) + 0.0722 * f(rgb[2])


def ratio(a, b):
    la, lb = lum(a), lum(b)
    hi, lo = max(la, lb), min(la, lb)
    return (hi + 0.05) / (lo + 0.05)


def parse_css(s):
    m = re.findall(r"[\d.]+", s)
    return np.array([float(x) for x in m[:3]] + ([float(m[3])] if len(m) > 3 else [1.0]))


# geometry + text colours straight out of the live page
page = ROOT / "index.html"
src = page.read_text(encoding="utf-8")
page.write_text(src.replace("</body>", f"<script>{JS_BOXES}</script></body>"), encoding="utf-8")
_profile = tempfile.mkdtemp(prefix="hubcr-")
r = subprocess.run(
    [CHROME, "--headless=new", "--disable-gpu", "--hide-scrollbars",
     "--disable-application-cache", "--disk-cache-size=1", "--incognito",
     f"--user-data-dir={_profile}",
     "--dump-dom", "--virtual-time-budget=9000", "--window-size=1440,2600",
     BASE + "index.html"], capture_output=True, text=True, encoding="utf-8", errors="replace")
shutil.rmtree(_profile, ignore_errors=True)
page.write_text(src, encoding="utf-8")
m = re.search(r'<pre id="boxes">(.*?)</pre>', r.stdout, re.S)
if not m:
    sys.exit("NO GEOMETRY - refusing to report contrast from a probe that read nothing")
boxes = [ln.split("|") for ln in html.unescape(m.group(1)).strip().split("\n")]
worst = 99.0
if len(boxes) != 8:
    sys.exit(f"refusing: found {len(boxes)} hub tiles, expected 8. A changed "
             f"tile count means the geometry below is measuring something else.")

render("", None, OUT / "hub-text.png")
render(HIDE, None, OUT / "hub-notext.png")
srv.shutdown()

a = np.asarray(Image.open(OUT / "hub-text.png").convert("RGB")).astype(float)
b = np.asarray(Image.open(OUT / "hub-notext.png").convert("RGB")).astype(float)
print(f"{'tile':<11}{'h3':>7}{'deck':>8}{'link':>8}   WCAG AA: "
      f"{AA_BODY} body, {AA_LARGE} large")
fails = 0
for row in boxes:
    idx, name, L, T, W, H = int(row[0]), row[1], int(row[2]), int(row[3]), int(row[4]), int(row[5])
    h3 = parse_css(row[6])
    deck = parse_css(row[7])
    go = parse_css(row[8])
    # where the text lives: the left 60% of the tile, below the name line
    x0, x1 = L + 20, L + int(W * 0.62)
    y0, y1 = T + 60, T + H - 24
    patch = b[y0:y1, x0:x1].reshape(-1, 3)
    med = np.median(patch, axis=0)
    # The deck is set in a near-black that may still be translucent. The colour a
    # reader actually sees is that text composited over the tile, so the
    # effective colour is the composite and the ratio is against the tile.
    da = deck[3] if len(deck) > 3 else 1.0
    deck_eff = deck[:3] * da + med * (1 - da)
    ga = go[3] if len(go) > 3 else 1.0
    go_eff = go[:3] * ga + med * (1 - ga)
    r3, rd, rg = ratio(h3[:3], med), ratio(deck_eff, med), ratio(go_eff, med)
    worst = min(worst, r3, rd, rg)
    flag = ""
    if rd < AA_BODY:
        flag += "  deck<4.5"
        fails += 1
    if rg < AA_BODY:
        flag += "  link<4.5"
        fails += 1
    if r3 < AA_LARGE:
        flag += "  h3<3.0"
        fails += 1
    print(f"{name:<11}{r3:>7.2f}{rd:>8.2f}{rg:>8.2f}{flag}")

print(f"\nworst ratio across all {len(boxes)} tiles: {worst:.2f}")
if fails:
    print(f"FAIL {fails} measurement(s) below WCAG AA. The tiles put body copy "
          f"on a saturated background; the copy has to be solid, not "
          f"translucent, or the pale tiles fail.")
    sys.exit(1)
print("ok")
