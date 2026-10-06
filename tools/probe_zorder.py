"""Why is the open menu transparent, and why does SUPPORT overflow it?

From the 390px open screenshot: page text ("All 47 stories", the timeline lines)
is readable *through* the menu overlay, and the SUPPORT pill runs off the right
edge. Neither was reported by `probe_nav.py`, which only checks fit, not paint.

Hypothesis for the bleed-through, which is the one worth testing: `.nav` carries
`z-index:65` but its ancestor `.topbar` is `position:sticky; z-index:40`, and a
positioned element with a z-index **creates a stacking context**. So the nav's 65
is scoped *inside* the header's context, the entire header subtree paints at 40,
and anything on the page above 40 paints OVER the open menu. A z-index on a
nested element cannot lift it out of an ancestor's stacking context.

Hypothesis for SUPPORT: `.nav a` is `width:min(340px,84vw)`, which at 390px is
327px - so it should be centred with ~31px either side. If it overflows, either
the width rule is not applying or the overlay's own box is wider than the
viewport.

Tests both by asking the browser what is actually on top at a given point, and
by reading the stacking chain. `elementFromPoint` is the check a screenshot
cannot give and a bounding box cannot give: it returns whoever WINS the paint
order, which is the only question "does it look transparent" actually asks.
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

if not (DIST / "index.html").exists():
    sys.exit("refusing: dist/index.html missing - run build_deploy first")


class H(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *a):
        pass


class S(socketserver.ThreadingTCPServer):
    allow_reuse_address = True
    daemon_threads = True


JS = r"""
const f = document.getElementById('f');
function report(o) {
  const el = document.createElement('pre');
  el.id = 'probe-out';
  el.textContent = JSON.stringify(o);
  document.body.appendChild(el);
}
function run() {
  try {
    const d = f.contentDocument, w = f.contentWindow;
    if (!d || !d.body) return report({error: 'no iframe document'});
    const nav = d.getElementById('nav');
    if (!nav) return report({error: 'no nav'});
    nav.style.transition = 'none';
    d.body.classList.add('nav-open');

    const o = {viewport: {w: w.innerWidth, h: w.innerHeight}};
    const nb = nav.getBoundingClientRect();
    o.navRect = {top: Math.round(nb.top), left: Math.round(nb.left),
                 w: Math.round(nb.width), h: Math.round(nb.height),
                 right: Math.round(nb.right)};

    // The stacking chain. For each ancestor, does it create a stacking context?
    // A z-index on a child is meaningless above an ancestor that traps it.
    const chain = [];
    for (let p = nav; p; p = p.parentElement) {
      const s = w.getComputedStyle(p);
      const pos = s.position;
      const zi = s.zIndex;
      const traps = (pos !== 'static' && zi !== 'auto') ||
        s.transform !== 'none' || s.filter !== 'none' ||
        s.backdropFilter !== 'none' || s.contain !== 'none' ||
        s.perspective !== 'none' || s.willChange !== 'auto' ||
        s.isolation === 'isolate';
      chain.push({
        el: p.tagName + '.' + ((p.className || '') + '').trim().split(/\s+/)[0],
        position: pos, zIndex: zi,
        backdropFilter: s.backdropFilter, filter: s.filter,
        transform: s.transform === 'none' ? 'none' : 'set',
        createsStackingContext: traps
      });
      if (chain.length > 6) break;
    }
    o.chain = chain;

    // WHO WINS THE PAINT ORDER, at points that sit over the menu.
    const pts = [[20, 40], [w.innerWidth / 2, 120], [w.innerWidth / 2, 300],
                 [w.innerWidth / 2, w.innerHeight - 60],
                 [w.innerWidth - 30, w.innerHeight - 60]];
    o.hitTest = pts.map(([x, y]) => {
      const e = d.elementFromPoint(Math.round(x), Math.round(y));
      const inNav = e ? !!(nav.contains(e) || e === nav) : false;
      return {
        pt: [Math.round(x), Math.round(y)],
        el: e ? e.tagName + '.' + ((e.className || '') + '').trim().split(/\s+/)[0]
              : 'null',
        text: e ? (e.textContent || '').trim().replace(/\s+/g, ' ').slice(0, 34)
                : '',
        inNav
      };
    });

    // the nav's own paint properties
    const ns = w.getComputedStyle(nav);
    o.navPaint = {background: ns.backgroundColor, zIndex: ns.zIndex,
                  opacity: ns.opacity, position: ns.position};

    // every link's box, to find the one overflowing
    o.links = [...nav.querySelectorAll('a')].map(a => {
      const r = a.getBoundingClientRect();
      return {t: (a.textContent || '').trim().slice(0, 14),
              w: Math.round(r.width), left: Math.round(r.left),
              right: Math.round(r.right),
              declaredWidth: w.getComputedStyle(a).width,
              pastViewport: r.right > w.innerWidth + 1 || r.left < -1};
    });
    report(o);
  } catch (e) { report({error: String(e && e.stack || e)}); }
}
if (f.contentDocument && f.contentDocument.readyState === 'complete') run();
else f.addEventListener('load', run);
setTimeout(run, 2500);
"""

srv = S(("127.0.0.1", 0), functools.partial(H, directory=str(DIST)))
threading.Thread(target=srv.serve_forever, daemon=True).start()
BASE = f"http://127.0.0.1:{srv.server_address[1]}/"

for w, h in ((390, 760), (1000, 420)):
    rel = f"__zprobe_{w}x{h}.html"
    (DIST / rel).write_text(
        f"<!DOCTYPE html><html><body style='margin:0'><iframe id='f' "
        f"src='index.html' style='width:{w}px;height:{h}px;border:0;"
        f"display:block'></iframe><script>{JS}</script></body></html>",
        encoding="utf-8")
    dom = subprocess.run(
        [CHROME, "--headless=new", "--disable-gpu", "--hide-scrollbars",
         f"--user-data-dir={ROOT / 'episode' / '.chrome'}",
         "--dump-dom", "--virtual-time-budget=9000",
         f"--window-size={w + 60},{h + 60}", BASE + rel],
        capture_output=True, text=True, timeout=300,
        encoding="utf-8", errors="replace")
    found = re.findall(r'id="probe-out">(.*?)</pre>', dom.stdout, re.S)
    print("=" * 74)
    print(f"  OPEN MENU at {w}x{h}")
    print("=" * 74)
    if not found:
        print("  PROBE DID NOT RUN")
        continue
    import html as _h
    r = json.loads(_h.unescape(found[-1]))
    if "error" in r:
        print("  page error:", r["error"])
        continue
    print(f"  viewport {r['viewport']}  navRect {r['navRect']}")
    print(f"  nav paint: {r['navPaint']}")
    print("\n  stacking chain (nav outwards):")
    for c in r["chain"]:
        flag = "  <-- CREATES A STACKING CONTEXT" if c["createsStackingContext"] else ""
        print(f"    {c['el']:22s} position={c['position']:>8} z={c['zIndex']:>5} "
              f"backdrop={c['backdropFilter'][:16]:>16}{flag}")
    print("\n  who wins the paint order:")
    for t in r["hitTest"]:
        mark = "IN MENU " if t["inNav"] else "*** ON TOP OF THE MENU ***"
        print(f"    {str(t['pt']):>10} -> {t['el']:26s} {mark}  {t['text']!r}")
    over = [l for l in r["links"] if l["pastViewport"]]
    print(f"\n  links: {len(r['links'])}, overflowing viewport: {len(over)}")
    for l in r["links"]:
        if l["pastViewport"] or l["w"] > 340:
            print(f"    {l['t']!r} width={l['w']} declared={l['declaredWidth']} "
                  f"left={l['left']} right={l['right']} past={l['pastViewport']}")
    try:
        (DIST / rel).unlink()
    except OSError:
        pass

srv.shutdown()
for p_ in DIST.glob("__zprobe_*.html"):
    try:
        p_.unlink()
    except OSError:
        pass
