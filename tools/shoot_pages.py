"""Screenshot arbitrary pages of the site, at desktop width, inside an iframe.

Same harness discipline as shoot_front.py: served over http, captured in an
IFRAME because Windows clamps Chrome's --window-size to roughly 500px.

Usage: python tools/shoot_pages.py <rel-path> [<rel-path> ...]
"""
import functools, http.server, pathlib, socketserver, subprocess, sys, threading

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

W, HGT = 1440, 2400
for rel in sys.argv[1:]:
    label = rel.replace("/", "_").replace(".html", "")
    shot = OUT / f"page-{label}.png"
    (ROOT / "__pg.html").write_text(
        f"<!DOCTYPE html><html><head><meta charset='utf-8'>"
        f"<style>html,body{{margin:0;background:#0b0b0d;overflow:hidden}}"
        f"iframe{{width:{W}px;height:{HGT}px;border:0;display:block}}</style></head>"
        f"<body><iframe src='{rel}'></iframe></body></html>", encoding="utf-8")
    subprocess.run(
        [CHROME, "--headless=new", "--disable-gpu", "--hide-scrollbars",
         f"--user-data-dir={ROOT / 'episode' / '.chrome'}",
         f"--window-size={W + 120},{HGT + 120}", "--virtual-time-budget=12000",
         f"--screenshot={shot.as_posix()}", BASE + "__pg.html"],
        capture_output=True, text=True, timeout=300,
        encoding="utf-8", errors="replace")
    try:
        (ROOT / "__pg.html").unlink()
    except OSError:
        pass
    ok = shot.exists() and shot.stat().st_size > 4000
    print(f"  {'ok  ' if ok else 'FAIL'} {rel:44} -> {shot.name}")
srv.shutdown()