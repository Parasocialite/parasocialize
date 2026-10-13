"""Render iYi's mood sheet to a PNG and look at it.

`sheet.svg` is an SVG, so it cannot be looked at directly - and AGENTS' own rule
is that a picture is only evidence once somebody has opened it. Served over http
because Chrome normalises a relative stylesheet path out of a `file://` page,
captured at 2x so the smallest cell is still legible.
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
OUT = ROOT / "episode" / ".chrome" / "moodsheet.png"


class H(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *a):
        pass


class S(socketserver.ThreadingTCPServer):
    allow_reuse_address = True
    daemon_threads = True


srv = S(("127.0.0.1", 0), functools.partial(H, directory=str(ROOT)))
threading.Thread(target=srv.serve_forever, daemon=True).start()
BASE = f"http://127.0.0.1:{srv.server_address[1]}/"

rel = "__moodsheet.html"
(ROOT / rel).write_text(
    "<!DOCTYPE html><html><head><meta charset='utf-8'><style>"
    "html,body{margin:0;padding:0;background:#130d0a}"
    "img{width:1200px;height:600px;display:block}</style></head>"
    "<body><img src='img/mascot/sheet.svg'></body></html>",
    encoding="utf-8")
r = subprocess.run(
    [CHROME, "--headless=new", "--disable-gpu", "--hide-scrollbars",
     f"--user-data-dir={ROOT / 'episode' / '.chrome'}",
     "--window-size=1320,760", "--virtual-time-budget=10000",
     f"--screenshot={OUT.as_posix()}", BASE + rel],
    capture_output=True, text=True, timeout=200, encoding="utf-8",
    errors="replace")
(ROOT / rel).unlink(missing_ok=True)
srv.shutdown()
if OUT.exists() and OUT.stat().st_size > 4000:
    print(f"  ok  {OUT.stat().st_size} bytes -> {OUT}")
else:
    sys.exit(f"no screenshot. stderr: {r.stderr.strip()[:200]}")
