"""Measure the real header at real widths, and find where it stops fitting.

The report is that the nav "doesn't fit" - too many tabs, and the group labels
("Look up", "Elsewhere") mess up the design. A previous fix made `.nav` wrap,
so the likely failure is **not** clipping but **overflow**: `.topbar-in` is a
fixed `height:64px` flex row, so a nav that wraps to two lines either exceeds
that box or gets overlapped by whatever follows. `verify_narrow.py` cannot see
any of this - it only measures at 390px, where `.nav` is the fixed full-screen
mobile overlay, so **the desktop nav is measured nowhere in this project.**

Reports per width: lines the nav occupies, whether it exceeds the 64px bar,
horizontal overflow, the width it needs with no wrapping at all, the widest
single item, and any `overflow:hidden` ancestor clipping it.

**Two harness failures, both mine, and both the shape AGENTS keeps predicting.**

  1. The first version put a multi-line JSON string in `document.title`, and
     every one of ten widths came back "unparseable". Ten confident failures.
  2. The second version built its own iframe + http.server and every field came
     back `None` - yet **the verdict logic still printed "fits" for all ten
     widths**, because it read `o.get("lines", 1)` and a missing key defaulted
     to 1 line, 0 overflow and 0 document width. **A measurement harness that
     fails open reports a clean layout it never observed**, which is the same
     defect as the `<` that fails open in the relation-derivation script, and
     the same defect as `verify_narrow`'s unstyled-page pass. `misses` now fails
     the run rather than defaulting.

This harness follows `verify_narrow.py`'s proven shape exactly - a wrapper page
written **into `dist/`** so relative stylesheet paths resolve the same way they
do in production, an iframe, an in-thread server, a `<pre id="probe-out">`, and
the same "prove the stylesheet is live before measuring" precondition. Reusing a
harness that already works beats inventing a second one.
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

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

ROOT = pathlib.Path(__file__).resolve().parent.parent
CHROME = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
DIST = ROOT / "dist"
TARGET_PAGES = ("index.html", "encyclopedia/american-gothic.html")
LADDER = (1600, 1440, 1366, 1280, 1180, 1100, 1024, 980, 940, 900, 820, 768)

if not (DIST / "index.html").exists():
    sys.exit("refusing: dist/index.html missing - run build_deploy first")
if not pathlib.Path(CHROME).exists():
    sys.exit(f"refusing: no chrome at {CHROME}")


class Handler(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *a):
        pass

    def handle_error(self, req, addr):
        pass


class Server(socketserver.ThreadingTCPServer):
    allow_reuse_address = True
    daemon_threads = True


WRAPPER = """<!DOCTYPE html><html><body style="margin:0;background:#0b0b0d">
<iframe id="f" src="{src}" style="width:{w}px;height:1500px;border:0;display:block"></iframe>
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
    const doc = d.documentElement;

    // PRECONDITION: the stylesheet must be live, or every number below is of an
    // unstyled page - which reports no overflow for anything at all.
    const declared = [...d.querySelectorAll('link[rel~="stylesheet"]')].length;
    const nav = d.getElementById('nav');
    const bar = d.querySelector('.topbar-in');
    const wm = d.querySelector('.wordmark');
    const cs = nav ? w.getComputedStyle(nav) : null;
    const bodyBg = w.getComputedStyle(d.body).backgroundColor;
    const css = {{declared, loaded: d.styleSheets.length,
                 bodyBg, navDisplay: cs ? cs.display : 'n/a',
                 gap: cs ? cs.gap : 'n/a', wrap: cs ? cs.flexWrap : 'n/a',
                 barH: bar ? getComputedStyle(bar).height : 'n/a'}};
    const cssOK = css.loaded >= css.declared && css.bodyBg !== 'rgba(0, 0, 0, 0)';

    if (!nav || !bar) return report({{wanted: {w}, got: w.innerWidth,
      cssOK, css, error: 'nav or .topbar-in missing'}});

    const items = [...nav.children];
    const labs = [...nav.querySelectorAll('.nav-lab')];
    // How many LINES, which is not how many distinct `top` offsets. The group
    // labels are a smaller font and the row is `align-items:center`, so a label
    // sits at a different top than the links **on the same line** - counting
    // offsets reported a one-line nav as three lines at every width, which is
    // the "distinct vertical offsets are rows, not columns" trap in reverse.
    // Cluster tops with a tolerance of a third of the tallest item instead.
    const rects = items.map(e => e.getBoundingClientRect());
    const itemH = Math.max(...rects.map(r => r.height));
    const tol = Math.max(4, itemH / 3);
    const rows = [];
    rects.map(r => r.top).sort((a, b) => a - b).forEach(t => {{
      if (!rows.length || t - rows[rows.length - 1] > tol) rows.push(t);
    }});
    const lines = rows.length;

    // getBoundingClientRect off the IFRAME'S window, not this one. Called on
    // `nav` it works by luck, because these are same-origin; called on the
    // element it returned a plain object and every width failed with
    // "nb.getBoundingClientRect is not a function" - twenty-four confident
    // failures, none of which named the line. Use the element's own method.
    const nb = nav.getBoundingClientRect();
    const bb = bar.getBoundingClientRect();
    // what it would need with no wrapping: the honest width of the problem.
    // Measure the CLONE, not `nav` - appending it to the live bar would reflow
    // the page being measured.
    const pr = nav.cloneNode(true);
    pr.style.flexWrap = 'nowrap';
    pr.style.position = 'absolute';
    pr.style.visibility = 'hidden';
    pr.style.width = 'max-content';
    pr.style.left = '0';
    pr.style.top = '0';
    nav.parentNode.appendChild(pr);
    const need = Math.round(pr.getBoundingClientRect().width);
    pr.remove();

    // widest single item - `white-space:nowrap` + `flex:none` means one long
    // label can be the thing that refuses to shrink
    let widest = {{t: '', w: 0}};
    items.forEach(e => {{
      const x = Math.round(e.getBoundingClientRect().width);
      if (x > widest.w) widest = {{t: (e.textContent || '').trim().slice(0, 26), w: x}};
    }});

    // Is anything actually CUTTING the nav? `overflow:hidden` on the page hides a
    // layout bug rather than fixing it, so one is worth finding - but only when
    // it removes pixels. The first version walked to any ancestor with a
    // non-visible overflow and printed "clipped by BODY, clips -3267px" on every
    // page: `body` always has non-visible overflow, and the number was negative
    // because the body is thousands of pixels TALLER than the nav. A clip that
    // removes nothing is not a clip.
    let clip = '';
    for (let p = nav.parentElement; p; p = p.parentElement) {{
      const s = w.getComputedStyle(p);
      const cuts = s.overflow === 'hidden' || s.overflowY === 'hidden' ||
                   s.overflowX === 'hidden';
      if (!cuts) continue;
      const pr = p.getBoundingClientRect();
      const cutR = Math.round(nb.right - pr.right);
      const cutB = Math.round(nb.bottom - pr.bottom);
      if (cutR > 1 || cutB > 1) {{
        clip = p.tagName + '.' + (p.className || '') +
          ' cuts ' + Math.max(cutR, cutB) + 'px';
        break;
      }}
    }}

    // what is under the nav, and is a second nav line landing on it?
    // `nb` is already a rect, so it is read directly. Calling
    // nb.getBoundingClientRect() here was the leftover that broke all twenty-four
    // widths, and it survived a "fixed" version of itself three lines earlier -
    // the same bug in two places at once, which is what happens when a
    // measurement is written without running it.
    const next = bar.nextElementSibling;
    const overlap = next ? Math.max(0,
      Math.round(nb.bottom - next.getBoundingClientRect().top)) : 0;

    report({{
      wanted: {w}, got: w.innerWidth, cssOK, css,
      items: items.length, labs: labs.length, lines,
      navH: Math.round(nb.height), barH: Math.round(bb.height),
      navW: Math.round(nb.width), ovfX: nav.scrollWidth - Math.round(nb.width),
      need, docW: doc.scrollWidth, docH: doc.scrollHeight,
      wmW: Math.round(wm.getBoundingClientRect().width),
      availW: Math.round(bb.width - wm.getBoundingClientRect().width - 22),
      widest, clip, overlap,
      nextTag: next ? next.tagName + '.' +
        ((next.className || '').toString().split(' ')[0]) : '',
      labText: labs.map(e => e.textContent.trim()),
      labW: labs.map(e => Math.round(e.getBoundingClientRect().width)),
      labBorder: labs.map(e => getComputedStyle(e).borderLeftWidth),
      menuVisible: (() => {{
        const b = d.querySelector('.menu-btn');
        if (!b) return 'no menu button';
        return getComputedStyle(b).display;
      }})(),
      // WHICH LAYOUT IS THIS. Below the breakpoint the nav is a fixed overlay
      // translated off-screen, so its 2500px of "horizontal overflow" is a menu
      // that is deliberately not on the page - measuring it as overflow is the
      // wrong layer, and the first version of this harness did exactly that and
      // reported 2527px of h-overflow on six perfectly good widths.
      mode: (() => {{
        const s = w.getComputedStyle(nav);
        const b = d.querySelector('.menu-btn');
        const btn = b ? w.getComputedStyle(b).display : 'none';
        return (s.position === 'fixed' || btn !== 'none') ? 'overlay' : 'row';
      }})(),
      // With the overlay actually OPEN, does it fit? An off-screen menu proves
      // nothing about whether it is usable when you press the button.
      opened: (() => {{
        const isOverlay = w.getComputedStyle(nav).position === 'fixed';
        if (!isOverlay) return null;
        d.body.classList.add('nav-open');
        const ob = nav.getBoundingClientRect();
        const out = {{
          h: Math.round(ob.height), top: Math.round(ob.top),
          bottom: Math.round(ob.bottom),
          fitsH: ob.height <= w.innerHeight + 1,
          scrolls: nav.scrollHeight > Math.round(ob.height) + 1,
          scrollH: nav.scrollHeight,
          children: nav.children.length,
          // a link wider than the overlay is a real defect: the overlay sets
          // `width:min(340px,84vw)` on links, so check it against 84vw
          tooWide: [...nav.querySelectorAll('a')].map(a => Math.round(
            a.getBoundingClientRect().width)).reduce(
            (m, x) => Math.max(m, x), 0)
        }};
        d.body.classList.remove('nav-open');
        return out;
      }})()
    }});
  }} catch (e) {{ report({{error: String(e && e.stack || e)}}); }}
}}
if (f.contentDocument && f.contentDocument.readyState === 'complete') run();
else f.addEventListener('load', run);
setTimeout(run, 2500);
</script></body></html>"""


def probe(page, w, srv_base, tmpname):
    rel = f"__navprobe_{w}.html"
    (DIST / rel).write_text(
        WRAPPER.format(src=page, w=w), encoding="utf-8")
    dom = subprocess.run(
        [CHROME, "--headless=new", "--disable-gpu", "--hide-scrollbars",
         f"--user-data-dir={ROOT / 'episode' / '.chrome'}",
         "--dump-dom", "--virtual-time-budget=9000",
         f"--window-size={w + 80},1600", srv_base + rel],
        check=True, capture_output=True, timeout=300, text=True,
        encoding="utf-8", errors="replace")
    found = re.findall(r'id="probe-out">(.*?)</pre>', dom.stdout, re.S)
    if not found:
        return {"_error": "PROBE DID NOT RUN - harness broken, not the page"}
    import html as _h
    try:
        r = json.loads(_h.unescape(found[-1]))
    except Exception as e:
        return {"_error": f"unparseable: {found[-1][:80]!r} ({e})"}
    # The page reports its own failure under `error`, not `_error`. Mapping it
    # matters: a page-side exception arrived as a dict with one key, sailed past
    # every `in` test for a real measurement, and printed as "INCOMPLETE"
    # rather than as the actual fault - which is why twenty-four widths failed
    # without once saying why.
    if "error" in r:
        return {"_error": f"page reported: {r['error']}"}
    r["_w"] = w
    return r


srv = Server(("127.0.0.1", 0), functools.partial(Handler, directory=str(DIST)))
threading.Thread(target=srv.serve_forever, daemon=True).start()
BASE = f"http://127.0.0.1:{srv.server_address[1]}/"

missing = 0
failed = []
for page in TARGET_PAGES:
    print("=" * 78)
    print(f"HEADER MEASUREMENT  {page}")
    print("=" * 78)
    rows = []
    for w in LADDER:
        r = probe(page, w, BASE, w)
        if "_error" in r:
            print(f"  {w:>5}: {r['_error']}")
            missing += 1
            continue
        rows.append(r)
        try:
            (DIST / f"__navprobe_{w}.html").unlink()
        except OSError:
            pass
    if not rows:
        print("  no width measured - refusing to draw a conclusion")
        continue

    # A row missing its own keys is a failed measurement, not a zero. Asserting
    # this is the whole point of the `misses` counter: the first two versions of
    # this harness defaulted every missing key to a harmless value and printed
    # "fits" for all ten widths.
    NEEDED = ("css", "lines", "navH", "ovfX", "overlap", "docW", "cssOK",
              "got", "need", "availW", "widest", "labW", "items", "labs",
              "labText", "clip", "labBorder", "mode", "menuVisible", "opened")
    for r in rows:
        gaps = [k for k in NEEDED if k not in r]
        if gaps:
            print(f"  {r['_w']:>5}: INCOMPLETE, missing {gaps} - void")
            missing += 1
    rows = [r for r in rows if not [k for k in NEEDED if k not in r]]
    if not rows:
        print("  no complete row - refusing to draw a conclusion")
        continue

    f = rows[0]
    print("\n  preconditions (measured, not assumed):")
    print(f"    stylesheet declared={f['css']['declared']} loaded={f['css']['loaded']} "
          f"bodyBg={f['css']['bodyBg']!r} -> cssOK={f['cssOK']}")
    print(f"    nav display={f['css']['navDisplay']!r} gap={f['css']['gap']!r} "
          f"wrap={f['css']['wrap']!r}  .topbar-in height={f['css']['barH']!r}")
    print(f"    nav position={f['mode']!r}  menu button={f['menuVisible']}")
    print(f"    {f['items']} nav children, {f['labs']} group labels "
          f"{f['labText']} at {f['labW']}px, borders {f['labBorder']}")

    print(f"\n  {'width':>5} {'mode':>8} {'lines':>5} {'navH':>5} {'ovfX':>5} "
          f"{'need':>5} {'avail':>5} {'ovl':>4} {'docW':>5} {'css':>5} {'got':>5}")
    for r in rows:
        print(f"  {r['_w']:>5} {r['mode']:>8} {r['lines']:>5} {r['navH']:>5} "
              f"{r['ovfX']:>5} {r['need']:>5} {r['availW']:>5} {r['overlap']:>4} "
              f"{r['docW']:>5} {str(r['cssOK']):>5} {r['got']:>5}")

    print(f"\n  overlay-opened check (must be a real measurement, not a skip):")
    ov = [r for r in rows if r["mode"] == "overlay"]
    if not ov:
        print("    no overlay width in the ladder - the overlay is UNTESTED")
        missing += 1
    for r in ov:
        o = r.get("opened")
        if not o:
            print(f"    {r['_w']:>5}: opened=None - the overlay was never "
                  f"measured open. Untested is not passing.")
            missing += 1
            continue
        print(f"    {r['_w']:>5}: {o['h']}px tall, fits viewport height="
              f"{o['fitsH']}, scrolls={o['scrolls']} "
              f"(scrollHeight {o['scrollH']}), widest link {o['tooWide']}px "
              f"({o['children']} children)")

    print("\n  per-width verdict:")
    bad_widths, good = [], []
    for r in rows:
        bad = []
        if not r["cssOK"]:
            bad.append("STYLESHEET NOT LIVE - measurement void")
        if r["got"] != r["_w"]:
            bad.append(f"harness got {r['got']}px, asked {r['_w']}px")
        # These only mean something in the desktop ROW. In overlay mode the nav is
        # translated off-screen on purpose, so its width and overflow are not
        # defects - measuring them there is the wrong layer.
        if r["mode"] == "row":
            if r["lines"] > 1:
                bad.append(f"WRAPS TO {r['lines']} LINES")
            if r["navH"] > 70:
                bad.append(f"nav {r['navH']}px EXCEEDS the 64px bar")
            if r["ovfX"] > 0:
                bad.append(f"h-overflow {r['ovfX']}px")
            if r["overlap"] > 0:
                bad.append(f"OVERLAPS the next element by {r['overlap']}px")
        else:
            if r["menuVisible"] in ("none", None):
                bad.append("overlay mode but the menu button is not shown - "
                           "the nav cannot be reached at all")
            op = r.get("opened")
            if op:
                if not op["fitsH"]:
                    bad.append(f"OPEN overlay {op['h']}px does not fit "
                               f"{r['_w']}px-wide viewport height")
                if op["tooWide"] > 340:
                    bad.append(f"overlay link {op['tooWide']}px > 340px cap")
        if r["docW"] > r["_w"] + 1:
            bad.append(f"document {r['docW']}px > viewport {r['_w']}px")
        if r["clip"]:
            bad.append(f"clipped by {r['clip']}")
        print(f"    {r['_w']:>5} [{r['mode']}]: " + ("; ".join(bad) if bad else "fits"))
        (bad_widths if bad else good).append(r["_w"])
        if bad:
            failed.append((r["_w"], f"{page}: " + "; ".join(bad)))
    if not good:
        print("\n  NO WIDTH FITS CLEANLY - the nav is broken at every width")
    else:
        print(f"\n  clean widths: {min(good)}-{max(good)}px "
              f"({len(good)}/{len(rows)} measured)")
    print(f"  widest nav that fits: {max(good) if good else 'none'}")
    if bad_widths:
        print(f"  broken at: {bad_widths}")
    print(f"  no-wrap width needed at {rows[0]['_w']}px: {rows[0]['need']}px "
          f"(avail {rows[0]['availW']}px)")
    print(f"  widest single item at {rows[0]['_w']}px: {rows[0]['widest']}")
    print(f"  group labels cost: {sum(rows[0]['labW'])}px + 3 gaps of 16px "
          f"= {sum(rows[0]['labW']) + 48}px of a {rows[0]['_w']}px row")

srv.shutdown()
for f_ in DIST.glob("__navprobe_*.html"):
    try:
        f_.unlink()
    except OSError:
        pass

print()
if missing:
    sys.exit(f"refusing to call this a clean run: {missing} width(s) produced "
             f"no measurement. A harness that measures nothing must not report.")

# --- gate mode --------------------------------------------------------------
# `--check` is for link_audit.py / the commit loop. It exits non-zero if ANY
# width on ANY page failed, and prints only the failing widths, because a gate
# whose output is a screenful of green is a gate nobody reads. Kept separate from
# the report because the report's job is to show the working, and a gate that
# prints the working is a gate whose failure is invisible in the noise.
if "--check" in sys.argv:
    if failed:
        print("RED: header does not fit:")
        for w_, why_ in sorted(failed):
            print(f"    {w_}: {why_}")
        sys.exit(1)
    print("ok: header fits at every width measured, on every page.")
    raise SystemExit(0)

print("  every width measured on every page. verdict above is real.")
