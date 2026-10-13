"""Screenshot the top half of the front page, at the widths that matter.

Same harness discipline as `shoot_nav.py`: served over http from the source
tree, everything captured inside an IFRAME because Windows clamps Chrome's
`--window-size` to roughly 500px, and `--virtual-time-budget` long enough for
the Google fonts to land.

Usage:  python tools/shoot_front.py            (all cases)
        python tools/shoot_front.py --view     (all cases, then open the folder)
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
CHROME = r"C:\Program Files\Google\Chrome\Chrome\Application\chrome.exe"
if not pathlib.Path(CHROME).exists():
    CHROME = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
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

# (label, width, height)
CASES = [
    ("desktop-1440-top", 1440, 1150),
    ("laptop-1180-top", 1180, 1150),
    ("phone-390-top", 390, 1500),
    ("desktop-1440-full", 1440, 2600),
]


def main() -> int:
    ok = 0
    for label, w, h in CASES:
        shot = OUT / f"{label}.png"
        rel = f"__frontshot_{label}.html"
        (ROOT / rel).write_text(
            f"<!DOCTYPE html><html><head><meta charset='utf-8'>"
            f"<style>html,body{{margin:0;padding:0;background:#0b0b0d;"
            f"overflow:hidden}}iframe{{width:{w}px;height:{h}px;"
            f"border:0;display:block}}</style></head>"
            f"<body><iframe id='f' src='index.html'></iframe></body></html>",
            encoding="utf-8")
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
            print(f"  ok   {label:20s} {shot.stat().st_size:>8} bytes -> {shot}")
            ok += 1
        else:
            print(f"  FAIL {label:20s} no screenshot. "
                  f"stderr: {r.stderr.strip()[:200]}")
    srv.shutdown()
    print()
    if ok != len(CASES):
        sys.exit(f"refusing to call this a set: {ok}/{len(CASES)} shots taken")
    print(f"  {ok}/{len(CASES)} -> {OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
