"""Measure the front page's card geometry, before and after the resize.

The report: the three masthead modules ("To read", "To research", the clerk)
are oversized and the eight hub tiles are chunky. This prints box heights and
the font sizes that drive them at every ladder width, so the change is sized
against numbers rather than impressions - and so "less chunky" cannot quietly
become "worse at 760px".

The stylesheet precondition is the strict one verify_narrow.py learned the
hard way: a page that declares no stylesheet element and is not styled by
anything else reports comfortable geometry for a page nobody can read.
"""
import functools, html as _html, http.server, json, pathlib, re, socketserver
import subprocess, sys, tempfile, threading

ROOT = pathlib.Path(__file__).resolve().parent.parent
CHROME = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
DIST = ROOT / "dist"
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

LADDER = (1440, 1180, 1024, 900, 760, 390)

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


srv = Server(("127.0.0.1", 0), functools.partial(Handler, directory=str(DIST)))
threading.Thread(target=srv.serve_forever, daemon=True).start()
BASE = f"http://127.0.0.1:{srv.server_address[1]}/"

WRAPPER = """<!DOCTYPE html><html><body style="margin:0;background:#0b0b0d">
<iframe id="f" src="index.html" style="width:{w}px;height:3200px;border:0;display:block"></iframe>
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
    const links = [...d.querySelectorAll('link[rel~="stylesheet"]')];
    const here = new URL(location.href).origin;
    const sameLinks = links.filter(l => new URL(l.href).origin === here);
    const loadedSet = new Set([...d.styleSheets].map(s => s && s.href));
    const sameLoaded = sameLinks.filter(l => loadedSet.has(l.href)).length;
    const bodyBg = w.getComputedStyle(d.body).backgroundColor;
    const styled = bodyBg !== 'rgba(0, 0, 0, 0)';
    const cssOK = sameLoaded >= sameLinks.length && styled && links.length > 0;
    if (!cssOK) return report({{wanted: {w}, cssOK, declared: links.length,
                                sameLoaded, bodyBg}});

    const R = e => {{ const r = e.getBoundingClientRect();
      return {{w: Math.round(r.width), h: Math.round(r.height)}}; }};
    const px = (e, p) => Math.round(parseFloat(w.getComputedStyle(e)[p]));
    const doors = [...d.querySelectorAll('.masthead-row .fdoor')];
    const clerk = d.querySelector('.masthead-row .clerk');
    const hubs = [...d.querySelectorAll('.hub')];
    const o = {{
      wanted: {w}, cssOK,
      doorH: doors.map(e => R(e).h),
      doorBodyH: doors.map(e => e.querySelector('.fdoor-body')
                                ? R(e.querySelector('.fdoor-body')).h : null),
      doorTitle: doors.length ? px(doors[0].querySelector('strong'), 'fontSize') : null,
      clerkH: clerk ? R(clerk).h : null,
      clerkLine: clerk ? px(clerk.querySelector('.clerk-line'), 'fontSize') : null,
      hubH: hubs.map(e => R(e).h),
      hubName: hubs.length ? px(hubs[0].querySelector('.hub-name'), 'fontSize') : null,
      hubTitle: hubs.length ? px(hubs[0].querySelector('h3'), 'fontSize') : null,
      hubGo: hubs.length ? px(hubs[0].querySelector('.hub-go'), 'fontSize') : null,
      hOverflow: d.documentElement.scrollWidth - w.innerWidth,
    }};
    report(o);
  }} catch (e) {{ report({{wanted: {w}, error: String(e)}}); }}
}}
if (document.readyState === 'complete') run();
else window.addEventListener('load', run);
setTimeout(run, 3000);
</script></body></html>"""

PROFILE = pathlib.Path(tempfile.mkdtemp(prefix="pc-chrome-"))
BAD = 0
try:
    for width in LADDER:
        rel = f"__cards_{width}.html"
        body = (WRAPPER.replace("{w}", str(width))
                .replace("{{", "\x00").replace("}}", "\x01")
                .replace("\x00", "{").replace("\x01", "}"))
        (DIST / rel).write_text(body, encoding="utf-8")
        r = subprocess.run(
            [CHROME, "--headless=new", "--disable-gpu", "--hide-scrollbars",
             f"--user-data-dir={PROFILE}",
             f"--window-size={width + 140},3300", "--virtual-time-budget=9000",
             "--dump-dom", BASE + rel],
            capture_output=True, text=True, timeout=300,
            encoding="utf-8", errors="replace")
        try:
            (DIST / rel).unlink()
        except OSError:
            pass
        mm = re.search(r'<pre id="probe-out">(\{.*?\})</pre>', r.stdout, re.S)
        if not mm:
            print(width, "px  RED no probe output")
            BAD += 1
            continue
        m = json.loads(_html.unescape(mm.group(1)))
        if m.get("error"):
            print(width, "px  RED", m["error"])
            BAD += 1
            continue
        if not m.get("cssOK"):
            print(width, "px  RED stylesheet not live:", m)
            BAD += 1
            continue
        hub = m["hubH"]
        print(f"{width:>5}px  cssOK  "
              f"doors h={m['doorH']} body={m['doorBodyH']} "
              f"clerk={m['clerkH']} | "
              f"hubs n={len(hub)} min={min(hub)} max={max(hub)} | "
              f"sizes door-title={m['doorTitle']} clerk-line={m['clerkLine']} "
              f"hub-name={m['hubName']} hub-h3={m['hubTitle']} "
              f"hub-go={m['hubGo']} | overflow={m['hOverflow']}")
        if m["hOverflow"] > 1:
            BAD += 1
            print(f"        RED horizontal overflow {m['hOverflow']}px")
finally:
    import shutil
    shutil.rmtree(PROFILE, ignore_errors=True)
print("probe_cards done", "BAD" if BAD else "clean")
sys.exit(1 if BAD else 0)
