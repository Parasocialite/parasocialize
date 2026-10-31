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
import shutil
import socketserver
import subprocess
import sys
import tempfile
import threading

ROOT = pathlib.Path(__file__).resolve().parent.parent
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

# A page can be named as a directory ("/taxonomy/") or as a file ("/index.html").
# Both forms have to work: the front door is a file, and a gate that cannot
# check the most-visited page on the site has a hole shaped like it.
p = page.lstrip("/") or "index.html"
if p.endswith(".html"):
    rel_file = p
    owner = pathlib.Path(p).parent              # "." for the front door
else:
    if not p.endswith("/"):
        p += "/"
    rel_file = p + "index.html"
    owner = pathlib.Path(p.rstrip("/"))         # taxonomy/ or "." for /

target = DIST / rel_file
if not target.is_file():
    raise SystemExit(f"{page} is not in dist/ ({rel_file}). Run "
                     "tools\\build_deploy.py first - measuring the source "
                     "tree measures nothing.")

# The probe files go in the same directory as the page, so that a page's
# relative stylesheet URLs still resolve for the copy the iframe loads.
# as_posix() and not str(): on Windows, `owner / "x"` joins with a backslash,
# and the same string went to two Chrome subcommands that treat a backslash in
# a URL differently - dump-dom fetched `/top8\_narrow_probe.html` happily while
# --screenshot refused the identical URL with exit 21. One form for the disk
# AND the URL, and it is the URL's form.
wrapper_rel = (owner / "_narrow_probe.html").as_posix()
open_rel = (owner / "_narrow_open.html").as_posix()
if wrapper_rel.startswith("./"):
    wrapper_rel = wrapper_rel[2:]
if open_rel.startswith("./"):
    open_rel = open_rel[2:]
png = (ROOT / "episode" / ".chrome" / shot) if shot else None

# A profile of this run's own, deleted afterwards. The shared episode/.chrome
# profile was two traps in one: two Chrome-based checks started at the same
# time race for the singleton lock, and a persistent profile has already
# served a cached stylesheet to a probe once (see probe_hub_contrast's note in
# AGENTS). A fresh profile can do neither.
PROFILE = pathlib.Path(tempfile.mkdtemp(prefix="pn-chrome-"))


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
src_html = target.read_text(encoding="utf-8")
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
    // But a page is only excused for what it actually declared, and "declared"
    // means an ELEMENT. /ledger/ shipped with a missing `>` after its
    // description meta; the open tag ate the stylesheet link that followed, so
    // the DOM had no stylesheet while the source text still contained one.
    // A substring test - and the first draft of this check - read the text and
    // waved through an unstyled page. signal/latest.html is the one page that
    // truly declares none (it is an HTML email, inline-styled by necessity),
    // and it still has to prove it is styled: the background test below is
    // what separates "styles itself inline" from "no styles arrived at all".
    // Same-origin only: the page's own CSS is local and fingerprinted, and its
    // absence is what manufactures an unstyled pass; the Google Fonts sheet is
    // a third-party CDN that a cold profile can still be fetching at measure
    // time while both local sheets are applied - calling that "no CSS" made
    // this gate go red on a page whose stylesheet was demonstrably live.
    // Font loading is verify_measure.py's subject, not this file's.
    const links = [...d.querySelectorAll('link[rel~="stylesheet"]')];
    const here = new URL(location.href).origin;
    const sameLinks = links.filter(l => new URL(l.href).origin === here);
    const loadedSet = new Set([...d.styleSheets].map(s => s && s.href));
    const sameLoaded = sameLinks.filter(l => loadedSet.has(l.href)).length;
    const triad = d.querySelector('.tx-triad');
    const css = {{
      declared: links.length, loaded: d.styleSheets.length,
      sameOrigin: sameLinks.length, sameLoaded,
      selfContained: links.length === 0,
      triadDisplay: triad ? w.getComputedStyle(triad).display : 'n/a',
      bodyBg: w.getComputedStyle(d.body).backgroundColor
    }};
    const styled = css.triadDisplay === 'grid' ||
                   css.bodyBg !== 'rgba(0, 0, 0, 0)';
    const cssOK = sameLoaded >= sameLinks.length && styled;

    const doc = d.documentElement;
    // An element inside a horizontal scroll container is *allowed* to extend
    // past the viewport - that is what the container is for, and .dbwrap on
    // /encyclopedia/ is a 530px table in a 337px scroller by design. Flagging
    // those is how a layout gate ends up ignored. Only elements with no
    // scrolling ancestor count as overflow.
    const inScroller = e => {{
      for (let p = e.parentElement; p && p.tagName !== 'HTML'; p = p.parentElement) {{
        const o = w.getComputedStyle(p).overflowX;
        if (o === 'auto' || o === 'scroll') return true;
      }}
      return false;
    }};
    // skip links are positioned off-screen on purpose; that is not an overflow
    const over = [...d.querySelectorAll('body *')].filter(e => {{
      if (e.classList && e.classList.contains('skip')) return false;
      if (inScroller(e)) return false;
      const r = e.getBoundingClientRect();
      return r.width > 0 && r.height > 0 &&
             (r.right > w.innerWidth + 1 || r.left < -1);
    }}).slice(0, 10).map(e => e.tagName.toLowerCase() + '.' +
                   (e.className || '').toString().split(' ')[0] +
                   ' right=' + Math.round(e.getBoundingClientRect().right));
    // smallest element whose content is wider than it can show, and which is
    // not itself a scroller: getBoundingClientRect misses these, scrollWidth
    // does not, and a bare `1fr` grid track is exactly this bug.
    // overflow-x:hidden is excluded - clipping is a legitimate technique for a
    // decorative layer (.hub-art loses 10px of art on purpose), and a gate that
    // reports decoration as a defect is a gate whose output gets skimmed.
    const candidates = [...d.querySelectorAll('body *')].filter(e => {{
      const o = w.getComputedStyle(e).overflowX;
      return o === 'visible' && e.scrollWidth > e.clientWidth + 1;
    }});
    // Report only the INNERMOST offenders. Every wrapper of the real culprit
    // is also over-wide, so sorting by size names main and section rather than
    // the grid that caused it - a diagnostic that points at the wrapper is a
    // diagnostic that sends you to the wrong file.
    const inner = candidates.filter(e => !candidates.some(o => o !== e &&
        e.contains(o))).sort((a, b) => a.getBoundingClientRect().width -
        b.getBoundingClientRect().width).slice(0, 6).map(e => ({{
      tag: e.tagName.toLowerCase(),
      cls: (e.className || '').toString().split(' ').slice(0, 2).join('.'),
      over: e.scrollWidth - e.clientWidth,
      width: w.getComputedStyle(e).width,
      minWidth: w.getComputedStyle(e).minWidth,
      display: w.getComputedStyle(e).display,
      parentCls: (e.parentElement && e.parentElement.className || '')
        .toString().split(' ')[0],
      // the innermost offender is often a wrapper; show what is inside it
      text: (e.textContent || '').trim().replace(/\\s+/g, ' ').slice(0, 90)
    }}));

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
      overflowing: over, contentOverflowing: inner
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
note = ""
try:
    dom = subprocess.run([
        CHROME, "--headless=new", "--disable-gpu",
        f"--user-data-dir={PROFILE}",
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
        if not r["css"].get("declared"):
            bad.append("the page declares no stylesheet link ELEMENT and is "
                       "not styled by anything else - if its source has a "
                       "<link rel=stylesheet>, a tag before it is unclosed "
                       "and swallowing it (that is exactly how /ledger/ "
                       "shipped unstyled for every reader)")
        else:
            bad.append(f"stylesheet did not load {r['css']} - the page declared "
                       f"{r['css'].get('sameOrigin', r['css'].get('declared'))} "
                       f"same-origin stylesheet(s) and "
                       f"{r['css'].get('sameLoaded', r['css'].get('loaded'))} "
                       "arrived, so every measurement below would be of an "
                       "unstyled page, which reports no overflow for anything")
    elif r["got"] != width:
        bad.append(f"measured at {r['got']}px, asked for {width}px - the "
                   "harness is wrong, not the page")
    elif r["hOverflow"] and r["css"].get("selfContained"):
        bad.append(f"horizontal overflow: scrollWidth {r['docScrollW']} > "
                   f"viewport {r['got']} on a self-contained page (an HTML "
                   "email). Fixed-width tables in email are deliberate, but "
                   "this one is also served at a public URL - use "
                   "width:100%;max-width instead of a fixed width")
        hint = ""
        culprits = r.get("contentOverflowing") or []
        if culprits:
            hint = " - likely " + ", ".join(
                f"{c['tag']}.{c['cls']} (content {c['over']}px too wide, "
                f"width:{c.get('width')}, min-width:{c.get('minWidth')}, "
                f"in .{c.get('parentCls')}: {c.get('text','')[:60]!r})"
                for c in culprits[:2])
        bad.append(f"horizontal overflow: scrollWidth {r['docScrollW']} > "
                   f"viewport {r['got']}{hint}."
                   # The cause differs, so do not assert one cause. A grid
                   # track refuses to shrink below its widest child; a long
                   # token has no break opportunity in it at all; a table's
                   # automatic layout cannot go below the sum of its cells.
                   + (" A bare 1fr track has an automatic minimum of its "
                      "min-content, so it will not shrink below its widest "
                      "child - use minmax(0,1fr), or auto-fit with a floor."
                      if culprits and culprits[0].get("display") in ("grid", "flex")
                      else " If it is text, look for a token with no break "
                           "opportunity in it (a slash-separated list is one) "
                           "and add overflow-wrap:break-word."
                      if culprits and culprits[0]["tag"] in ("p", "li", "span", "td", "th")
                      else " A table with width:100% cannot shrink below the sum "
                           "of its cells' min-content widths - it needs a "
                           "horizontal scroll wrapper."))
    elif r["overflowing"]:
        bad.append("elements past the right edge: " + "; ".join(r["overflowing"]))
    elif r.get("contentOverflowing"):
        # Not causing document overflow, so not a failure - but it is the same
        # defect one change away from being one, so say so rather than swallow
        # it. Printed as a note, never as a problem: a gate that fails on
        # decoration is a gate whose output stops being read.
        note = ("note: content wider than its box (not causing page overflow): "
                + "; ".join(f"{c['tag']}.{c['cls']} +{c['over']}px"
                            for c in r["contentOverflowing"]))

    if png:
        png.parent.mkdir(parents=True, exist_ok=True)
        subprocess.run([
            CHROME, "--headless=new", "--disable-gpu", "--hide-scrollbars",
            "--force-device-scale-factor=1",
            f"--user-data-dir={PROFILE}",
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
    shutil.rmtree(PROFILE, ignore_errors=True)

print()
if note:
    print(" ", note)
if bad:
    for b in bad:
        print("  PROBLEM:", b)
    raise SystemExit(f"narrow layout: {len(bad)} problems")
print("  no horizontal overflow, stylesheet confirmed live, "
      "every element inside the viewport")