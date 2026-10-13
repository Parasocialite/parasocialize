"""Screenshot one band of the front page, for checking detail at size.

`shoot_front.py` captures from the top, which is right for the masthead and
useless for the doors at the bottom - and a number rendered as a smudge at 8px
is exactly the kind of defect a full-width shot hides.
"""
import functools
import http.server
import pathlib
import socketserver
import subprocess
import sys
import threading

sys.stdout.reconfigure(encoding="utf-8")
ROOT = pathlib.Path(__file__).resolve().parent.parent
CHROME = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
OUT = ROOT / "episode" / ".chrome" / "frontshots"

# (label, width, height, scroll_y)
CASES = [("desktop-1440-doors", 1440, 320, 2430)]


class H(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *a):
        pass


class S(socketserver.ThreadingTCPServer):
    allow_reuse_address = True
    daemon_threads = True


srv = S(("127.0.0.1", 0), functools.partial(H, directory=str(ROOT)))
threading.Thread(target=srv.serve_forever, daemon=True).start()
BASE = f"http://127.0.0.1:{srv.server_address[1]}/"

for label, w, h, y in CASES:
    rel = f"__band_{label}.html"
    (ROOT / rel).write_text(
        f"<!DOCTYPE html><html><head><meta charset='utf-8'><style>"
        f"html,body{{margin:0;padding:0;background:#0b0b0d;overflow:hidden}}"
        f"#k{{width:{w}px;height:{h}px;overflow:hidden;position:relative}}"
        f"iframe{{width:{w}px;height:4000px;border:0;display:block;"
        f"transform:translateY(-{y}px)}}</style></head><body><div id='k'>"
        f"<iframe id='f' src='index.html'></iframe></div></body></html>",
        encoding="utf-8")
    shot = OUT / f"{label}.png"
    r = subprocess.run(
        [CHROME, "--headless=new", "--disable-gpu", "--hide-scrollbars",
         f"--user-data-dir={ROOT / 'episode' / '.chrome' / 'ud-band'}",
         f"--window-size={w + 120},{h + 120}", "--virtual-time-budget=12000",
         f"--screenshot={shot.as_posix()}", BASE + rel],
        capture_output=True, text=True, timeout=300,
        encoding="utf-8", errors="replace")
    (ROOT / rel).unlink(missing_ok=True)
    if shot.exists() and shot.stat().st_size > 4000:
        print(f"  ok   {label:22s} {shot.stat().st_size:>8} bytes")
    else:
        print(f"  FAIL {label}: {r.stderr.strip()[:160]}")
srv.shutdown()
