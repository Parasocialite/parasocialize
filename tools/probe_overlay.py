"""Why is the mobile overlay 130px tall instead of filling the viewport?

`probe_nav.py` reported the opened overlay at 130px with scrollHeight 156 -
and 130px is exactly the *closed* height, which means the "opened" measurement
is not opening it. `position:fixed; inset:0` should fill the viewport.

Suspects, in order of how likely they are to be right:
  1. The CSS transition (`transform .36s`) means the measurement runs before
     the transform has been applied, so it reads the closed state. That should
     affect `top`, not `height` - so if height is also wrong, it is not this.
  2. `inset:0` is being overridden or not supported as written.
  3. The nav is `position:fixed` but still a flex *item* of `.topbar-in`, and
     something about that ancestor is constraining it.
  4. The class is not landing on the right element at all.

Reports computed style and rect for the overlay BEFORE and AFTER the class,
with the transition neutralised, at a tall and a short viewport.
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

ROOT = pathlib.Path(r"C:\Users\paras\Documents\Default Project\parasocialize"
                    )
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
    const bar = d.querySelector('.topbar-in');
    const top = d.querySelector('.topbar');
    const btn = d.querySelector('.menu-btn');
    if (!nav) return report({error: 'no nav'});

    const decl = [...d.querySelectorAll('link[rel~="stylesheet"]')].length;
    const o = {
      viewport: {w: w.innerWidth, h: w.innerHeight},
      cssOK: d.styleSheets.length >= decl &&
             w.getComputedStyle(d.body).backgroundColor !== 'rgba(0, 0, 0, 0)',
      bodyClass: d.body.className,
      btnDisplay: btn ? w.getComputedStyle(btn).display : 'none'
    };

    const snap = tag => {
      const s = w.getComputedStyle(nav), r = nav.getBoundingClientRect();
      return Object.assign({tag}, {
        position: s.position, top: s.top, bottom: s.bottom,
        left: s.left, right: s.right, height: s.height, width: s.width,
        inset: s.inset, transform: s.transform,
        rectTop: Math.round(r.top), rectH: Math.round(r.height),
        rectW: Math.round(r.width), scrollH: nav.scrollHeight,
        offsetH: nav.offsetHeight, clientH: nav.clientHeight,
        parentTag: nav.parentElement.tagName + '.' + nav.parentElement.className,
        parentPos: w.getComputedStyle(nav.parentElement).position,
        parentH: Math.round(nav.parentElement.getBoundingClientRect().height),
        topbarPos: top ? w.getComputedStyle(top).position : 'n/a',
        topbarH: top ? Math.round(top.getBoundingClientRect().height) : -1,
        // what would full-viewport actually be?
        innerH: w.innerHeight
      });
    };

    o.closed = snap('closed');
    // neutralise the transition so nothing is read mid-animation
    nav.style.transition = 'none';
    d.body.classList.add('nav-open');
    o.afterClass = snap('after-class');
    // also force transform off in case the transition/transform is the cause
    nav.style.transform = 'none';
    o.afterTransform = snap('after-transform-none');

    d.body.classList.remove('nav-open');
    nav.style.transform = '';
    nav.style.transition = '';
    o.restored = snap('restored');
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

for w, h in ((1000, 900), (1000, 700), (1000, 480), (390, 844)):
    rel = f"__ovprobe_{w}x{h}.html"
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
    print("=" * 72)
    print(f"  iframe {w}x{h}")
    print("=" * 72)
    if not found:
        print("  PROBE DID NOT RUN")
        continue
    import html as _h
    r = json.loads(_h.unescape(found[-1]))
    if "error" in r:
        print("  page error:", r["error"])
        continue
    print(f"  cssOK={r['cssOK']} viewport={r['viewport']} "
          f"menuBtn={r['btnDisplay']}")
    for tag in ("closed", "afterClass", "afterTransform", "restored"):
        s = r[tag]
        print(f"  {tag:>15}: position={s['position']:>8} height={s['height']:>7} "
              f"rectH={s['rectH']:>5} scrollH={s['scrollH']:>5} "
              f"top={s['top']:>9} transform={s['transform'][:24]!r}")
        print(f"  {'':>15}  parent={s['parentTag']} parentPos={s['parentPos']} "
              f"parentH={s['parentH']} topbarPos={s['topbarPos']} "
              f"topbarH={s['topbarH']} innerH={s['innerH']}")
    try:
        (DIST / rel).unlink()
    except OSError:
        pass

srv.shutdown()
for p_ in DIST.glob("__ovprobe_*.html"):
    try:
        p_.unlink()
    except OSError:
        pass
