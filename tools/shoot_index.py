"""Screenshot the encyclopedia index filter area, before and after a chip click.

Same harness discipline as shoot_front.py: served over http, captured inside an
IFRAME because Windows clamps Chrome's --window-size to roughly 500px, so a
`--window-size=390` capture measures 500 and reports a page that is not there.

The second shot has the filter actually applied, because a filter that renders
and filters nothing is the failure this project has hit twice.

Usage:  python tools/shoot_index.py
"""
import functools
import http.server
import pathlib
import socketserver
import subprocess
import sys
import threading

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

ROOT = pathlib.Path(__file__).resolve().parent.parent
CHROME = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
if not pathlib.Path(CHROME).exists():
    CHROME = r"C:\Program Files\Google\Chrome\Chrome\Application\chrome.exe"
OUT = ROOT / "episode" / ".chrome" / "frontshots"
OUT.mkdir(parents=True, exist_ok=True)


class H(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *a):
        pass


class S(socketserver.ThreadingTCPServer):
    allow_reuse_address = True
    daemon_threads = True


srv = S(("127.0.0.1", 0), functools.partial(H, directory=str(ROOT)))
threading.Thread(target=srv.serve_forever, daemon=True).start()
BASE = f"http://127.0.0.1:{srv.server_address[1]}/"

# (label, width, height, js to run inside the frame before capture)
CASES = [
    ("index-1440-filters", 1440, 1250, ""),
    ("index-1440-filtered", 1440, 1250,
     "var c=document.querySelector('#recips [data-rec=\"simulated\"]');"
     "if(c)c.click();"),
    ("index-390-filters", 390, 1700, ""),
]


def main() -> int:
    ok = 0
    for label, w, h, js in CASES:
        shot = OUT / f"{label}.png"
        rel = f"__indexshot_{label}.html"
        (ROOT / rel).write_text(
            f"<!DOCTYPE html><html><head><meta charset='utf-8'>"
            f"<style>html,body{{margin:0;padding:0;background:#0b0b0d;"
            f"overflow:hidden}}iframe{{width:{w}px;height:{h}px;"
            f"border:0;display:block}}</style></head>"
            f"<body><iframe id='f' src='encyclopedia/index.html'></iframe>"
            + (f"<script>document.getElementById('f').addEventListener("
               f"'load',function(){{try{{var d=this.contentDocument;"
               f"{js}}}catch(e){{}}}});</script>" if js else "")
            + "</body></html>", encoding="utf-8")
        r = subprocess.run(
            [CHROME, "--headless=new", "--disable-gpu", "--hide-scrollbars",
             f"--user-data-dir={ROOT / 'episode' / '.chrome'}",
             f"--window-size={w + 120},{h + 120}", "--virtual-time-budget=12000",
             f"--screenshot={shot.as_posix()}", BASE + rel],
            capture_output=True, text=True, timeout=300,
            encoding="utf-8", errors="replace")
        try:
            (ROOT / rel).unlink()
        except OSError:
            pass
        if shot.exists() and shot.stat().st_size > 4000:
            print(f"  ok   {label:22s} {shot.stat().st_size:>8} bytes -> {shot}")
            ok += 1
        else:
            print(f"  FAIL {label:22s} no screenshot. "
                  f"stderr: {r.stderr.strip()[:200]}")
    srv.shutdown()
    print()
    if ok != len(CASES):
        sys.exit(f"refusing to call this a set: {ok}/{len(CASES)} shots taken")
    print(f"  {ok}/{len(CASES)} -> {OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
