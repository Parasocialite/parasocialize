"""Check a generated page at a narrow viewport, for real.

There is no CSS-based gate for layout in this repo, which means every layout
question gets answered by opening a page by hand - and a page that looks right
at 1280px can overflow at 390px without anyone noticing until a reader reports
it. This measures instead.

Three things have to be got right, and each one fails *silently and in the
direction that looks like success*:

  1. Chrome on Windows clamps `--window-size` to roughly 500px. Asking for 390
     does not error; it quietly measures 500. An iframe is used because a
     layout inside one responds to the iframe's width rather than to the
     window's, and the measured width is printed and asserted.

  2. `--virtual-time-budget` together with `--screenshot` returns a ~5KB blank
     PNG. The screenshot looks like it worked while showing nothing. Blank
     output is treated as failure.

  3. Serving a preview out of a subdirectory silently drops every stylesheet.
     Chrome normalises `../css/styles.css` to `/css/styles.css` *before
     sending*, so the request lands on the wrong root and 404s. The page then
     renders unstyled - and an unstyled page has no grid, so it reports "no
     overflow" for any content whatsoever. That is a passing result manufactured
     by a missing stylesheet, and it is the reason this tool refuses to report
     anything until it has read a computed style and confirmed the stylesheet
     is live.

So: serve `dist/` from the real root, prove the CSS loaded, then measure.

    python tools\\verify_narrow.py                     # /taxonomy/ at 390
    python tools\\verify_narrow.py --page /atlas/ --width 320
    python tools\\verify_narrow.py --shot atlas390.png
"""
import functools
import http.server
import json
import pathlib
import re
import socketserver
import subprocess
import sys
import threading

ROOT = pathlib.Path(r"C:\Users\paras\Documents\Default Project\parasocialize")
CHROME = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
DIST = ROOT / "dist"

page = "/taxonomy/"
width = 390
shot = None
argv = sys.argv[1:]
i = 0
while i < len(argv):
    if argv[i] == "--page":
        page = argv[i + 1]; i += 2
    elif argv[i] == "--width":
        width = int(argv[i + 1]); i += 2
    elif argv[i] == "--shot":
        shot = argv[i + 1]; i += 2
    else:
        raise SystemExit(__doc__)

if not (DIST / page.lstrip("/") / "index.html").exists():
    raise SystemExit(f"{page} is not in dist/. Run tools\\build_deploy.py first - "
                     "measuring the source tree measures nothing.")

rel = page.strip("/") + "/"                      # taxonomy/
wrapper_rel = rel + "_narrow_probe.html"
open_rel = rel + "_narrow_open.html"
png = (ROOT / "episode" / ".chrome" / shot) if shot else None


class Handler(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *a):
        pass


class Server(socketserver.ThreadingTCPServer):
    allow_reuse_address = True
    daemon_threads = True

    def handle_error(self, req, client_addr):
        pass


# the real root: dist/. Serving from dist/<subdir>/ 404s the stylesheet (see above).
srv = Server(("127.0.0.1", 0), functools.partial(Handler, directory=str(DIST)))
threading.Thread(target=srv.serve_forever, daemon=True).start()
BASE = f"http://127.0.0.1:{srv.server_address[1]}/"

# A copy with the <details> already open. The probe opens them from script, but
# --screenshot fires at load and captures them closed - and collapsed is the
# state nobody is reading, so a screenshot of it says nothing about the layout.
src_html = (DIST / rel / "index.html").read_text(encoding="utf-8")
opened_html = re.sub(r'<details class="([^"]+)" id="([^"]+)">',
                     lambda m: f'<details open class="{m.group(1)}" id="{m.group(2)}">',
                     src_html)
(DIST / open_rel).write_text(opened_html, encoding="utf-8")

wrapper = f"""<!DOCTYPE html><html><body style="margin:0;background:#0b0b0d">
<iframe id="f" src="{pathlib.Path(open_rel).name}" style="width:{width}px;height:1600px;
        border:0;display:block"></iframe>
<script>
const f = document.getElementById('f');
function report(o) {{
  const el = document.createElement('pre');
  el.id = 'probe-out';
  el.textContent = JSON.stringify(o);
  document.body.appendChild(el);
}}
function run() {{
  try {{
    const d = f.contentDocument, w = f.contentWindow;
    if (!d || !d.body) return report({{error: 'no iframe document'}});
    d.querySelectorAll('details').forEach(x => {{ x.open = true; }});

    // Prove the stylesheet is live BEFORE measuring. Unstyled reports no
    // overflow for everything, so a clean result without this check is void.
    const triad = d.querySelector('.tx-triad');
    const css = {{
      sheets: d.styleSheets.length,
      triadDisplay: triad ? w.getComputedStyle(triad).display : 'n/a',
      bodyBg: w.getComputedStyle(d.body).backgroundColor
    }};
    const cssOK = css.sheets >= 2 &&
                  (triad ? css.triadDisplay === 'grid' : css.bodyBg !== 'rgba(0, 0, 0, 0)');

    const doc = d.documentElement;
    // skip links are positioned off-screen on purpose; that is not an overflow
    const over = [...d.querySelectorAll('body *')].filter(e => {{
      if (e.classList && e.classList.contains('skip')) return false;
      const r = e.getBoundingClientRect();
      return r.width > 0 && r.height > 0 &&
             (r.right > w.innerWidth + 1 || r.left < -1);
    }}).slice(0, 10).map(e => e.tagName.toLowerCase() + '.' +
                   (e.className || '').toString().split(' ')[0] +
                   ' right=' + Math.round(e.getBoundingClientRect().right));

    const triads = [...d.querySelectorAll('.tx-triad')];
    const cells = [...d.querySelectorAll('.tx-triad-c')];
    const widths = cells.map(c => Math.round(c.getBoundingClientRect().width));
    // rows = distinct vertical offsets. cols = most cells sharing a top.
    // Reporting rows as "columns" makes a stacked layout look three-wide.
    const shape = triads.map(t => {{
      const byTop = {{}};
      [...t.children].forEach(c => {{
        const k = Math.round(c.getBoundingClientRect().top);
        byTop[k] = (byTop[k] || 0) + 1;
      }});
      return {{rows: Object.keys(byTop).length, cols: Math.max(...Object.values(byTop))}};
    }});
    const uniq = k => [...new Set(shape.map(s => s[k]))].sort((a, b) => a - b);

    report({{
      wanted: {width}, got: w.innerWidth, cssOK, css,
      docScrollW: doc.scrollWidth,
      hOverflow: doc.scrollWidth > w.innerWidth + 1,
      triads: triads.length, cells: cells.length,
      minCellW: widths.length ? Math.min(...widths) : 0,
      maxCellW: widths.length ? Math.max(...widths) : 0,
      rowsPerTriad: uniq('rows'), colsPerTriad: uniq('cols'),
      overflowing: over
    }});
  }} catch (e) {{ report({{error: String(e && e.stack || e)}}); }}
}}
if (f.contentDocument && f.contentDocument.readyState === 'complete') run();
else f.addEventListener('load', run);
setTimeout(run, 2000);
</script></body></html>"""

(DIST / wrapper_rel).write_text(wrapper, encoding="utf-8")
url = BASE + wrapper_rel

bad = []
try:
    dom = subprocess.run([
        CHROME, "--headless=new", "--disable-gpu",
        f"--user-data-dir={ROOT / 'episode' / '.chrome'}",
        "--dump-dom", "--virtual-time-budget=8000",
        "--window-size=900,1700", url,
    ], check=True, capture_output=True, timeout=300, text=True,
        encoding="utf-8", errors="replace")
    found = re.findall(r'id="probe-out">(.*?)</pre>', dom.stdout, re.S)
    if not found:
        raise SystemExit("PROBE DID NOT RUN - the harness is broken, not the page")
    r = json.loads(found[-1])

    print("=" * 64)
    print(f"NARROW LAYOUT  {page}  at {width}px")
    print("=" * 64)
    print(json.dumps(r, indent=1))

    if "error" in r:
        bad.append(f"harness error: {r['error']}")
    elif not r["cssOK"]:
        bad.append(f"stylesheet did not load {r['css']} - every measurement "
                   "below would be of an unstyled page, which reports no "
                   "overflow for anything")
    elif r["got"] != width:
        bad.append(f"measured at {r['got']}px, asked for {width}px - the "
                   "harness is wrong, not the page")
    elif r["hOverflow"]:
        bad.append(f"horizontal overflow: scrollWidth {r['docScrollW']} > "
                   f"viewport {r['got']}")
    elif r["overflowing"]:
        bad.append("elements past the right edge: " + "; ".join(r["overflowing"]))

    if png:
        png.parent.mkdir(parents=True, exist_ok=True)
        subprocess.run([
            CHROME, "--headless=new", "--disable-gpu", "--hide-scrollbars",
            "--force-device-scale-factor=1",
            f"--user-data-dir={ROOT / 'episode' / '.chrome'}",
            f"--screenshot={png}", f"--window-size={width + 40},1600", url,
        ], check=True, capture_output=True, timeout=240)
        sz = png.stat().st_size
        print(f"\n  {png}  {sz/1024:.0f} KB")
        if sz < 20000:
            bad.append("screenshot is blank - --virtual-time-budget and "
                       "--screenshot together do not work here")
finally:
    (DIST / wrapper_rel).unlink(missing_ok=True)
    (DIST / open_rel).unlink(missing_ok=True)
    srv.shutdown()

print()
if bad:
    for b in bad:
        print("  PROBLEM:", b)
    raise SystemExit(f"narrow layout: {len(bad)} problems")
print("  no horizontal overflow, stylesheet confirmed live, "
      "every element inside the viewport")