"""Measure the masthead rows. Screenshots show it; numbers say why.

The complaint is that the top half reads as janky, and the measurement that
matters is which column is the tall one - the clerk card being a hundred pixels
taller than the copy it sits beside is what moves the dead space rather than
removing it. Prints each width separately.
"""
import functools
import http.server
import json
import pathlib
import socketserver
import subprocess
import sys
import threading

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

ROOT = pathlib.Path(__file__).resolve().parent.parent
CHROME = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
UD = ROOT / "episode" / ".chrome" / "ud-probe"

JS = """() => {
  const q = s => document.querySelector(s);
  const b = e => { if (!e) return null; const r = e.getBoundingClientRect();
    return {t:Math.round(r.top), b:Math.round(r.bottom),
            w:Math.round(r.width), h:Math.round(r.height)}; };
  const o = {};
  for (const sel of ['.masthead', '.masthead-grid', '.masthead-copy', '.clerk',
                     '.clerk-face', '.mascot-hero', '.thesis', '.fdoors',
                     'h1', '.masthead .line']) {
    o[sel] = b(q(sel));
  }
  o.cols = getComputedStyle(q('.masthead-grid')).gridTemplateColumns;
  o.docW = document.documentElement.scrollWidth;
  o.winW = window.innerWidth;
  return o;
}"""


class H(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *a):
        pass


class S(socketserver.ThreadingTCPServer):
    allow_reuse_address = True
    daemon_threads = True


srv = S(("127.0.0.1", 0), functools.partial(H, directory=str(ROOT)))
threading.Thread(target=srv.serve_forever, daemon=True).start()
BASE = f"http://127.0.0.1:{srv.server_address[1]}/"

for w in (1440, 1180, 900, 390):
    rel = f"__probe{w}.html"
    (ROOT / rel).write_text(
        "<!DOCTYPE html><html><head><meta charset='utf-8'><style>"
        "html,body{margin:0;padding:0}"
        f"iframe{{width:{w}px;height:1500px;border:0;display:block}}"
        "</style></head><body><iframe id='f' src='index.html'></iframe>"
        "<script>var f=document.getElementById('f');"
        "function go(){try{var r=f.contentWindow.eval('(' + "
        + json.dumps(JS) + " + ')()');"
        "var p=document.createElement('pre');p.id='OUT';"
        "p.textContent=JSON.stringify(r);document.body.appendChild(p);}"
        "catch(e){var p=document.createElement('pre');p.id='OUT';"
        "p.textContent='ERR '+e;document.body.appendChild(p);}}"
        "f.addEventListener('load',function(){setTimeout(go,500)});"
        "</script></body></html>", encoding="utf-8")
    r = subprocess.run(
        [CHROME, "--headless=new", "--disable-gpu", "--dump-dom",
         f"--user-data-dir={UD}", f"--window-size={w + 140},1700",
         "--virtual-time-budget=9000", BASE + rel],
        capture_output=True, text=True, timeout=200,
        encoding="utf-8", errors="replace")
    (ROOT / rel).unlink(missing_ok=True)
    i = r.stdout.find('id="OUT">')
    print(f"--- {w}px")
    if i < 0:
        print("   NO MEASUREMENT (the dump did not carry the result)")
        continue
    blob = r.stdout[i + 9:].split("</pre>")[0]
    blob = blob.replace("&quot;", '"').replace("&amp;", "&").replace("&#x27;", "'")
    try:
        d = json.loads(blob)
    except Exception:
        print("   unparseable:", blob[:200])
        continue
    for k in ('.masthead', '.masthead-grid', '.masthead-copy', '.clerk',
              '.clerk-face', '.mascot-hero', '.thesis', '.fdoors'):
        v = d.get(k)
        print(f"   {k:20s} {v}")
    print(f"   cols {d.get('cols')}  docW={d.get('docW')} win={d.get('winW')}")

srv.shutdown()
