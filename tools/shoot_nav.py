"""Screenshot the header at the widths that matter and look at it.

AGENTS: "Look at the drawing; do not reason about the geometry." Every number in
`probe_nav.py` could be right and the header still look wrong - and the reverse
is the failure that costs the most time, because a passing gate with an ugly
header gets "fixed" back to something broken.

Four cases, each of which has been broken at some point in this session:
  1440  the desktop row at a width where it has plenty of room
  1180  the narrowest width that still gets the desktop row
  1024  the exact breakpoint edge, where a rule either applies or does not
   900  overlay mode, menu CLOSED - the state every previous check saw
   390  a phone, closed
   390  a phone, menu OPEN - the state no previous check ever saw, and the one
        where the 130px overlay bug lived

The open case injects `body.nav-open`, because pressing the button is the only
way to see the thing a reader sees. If a screenshot cannot be produced it says
so rather than writing a file that is not a screenshot.
"""
import functools
import http.server
import pathlib
import socketserver
import subprocess
import sys
import threading

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

ROOT = pathlib.Path(r"C:\Users\paras\Documents\Default Project\parasocialize"
                    )
CHROME = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
DIST = ROOT / "dist"
OUT = ROOT / "episode" / ".chrome" / "navshots"
OUT.mkdir(parents=True, exist_ok=True)

if not (DIST / "index.html").exists():
    sys.exit("refusing: dist/index.html missing - run build_deploy first")


class H(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *a):
        pass


class S(socketserver.ThreadingTCPServer):
    allow_reuse_address = True
    daemon_threads = True


srv = S(("127.0.0.1", 0), functools.partial(H, directory=str(DIST)))
threading.Thread(target=srv.serve_forever, daemon=True).start()
BASE = f"http://127.0.0.1:{srv.server_address[1]}/"

# (label, width, height, open_the_menu)
CASES = [
    ("desktop-1440", 1440, 620, False),
    ("desktop-1180", 1180, 620, False),
    ("edge-1024", 1024, 620, False),
    ("overlay-900-closed", 900, 620, False),
    ("phone-390-closed", 390, 760, False),
    ("phone-390-open", 390, 760, True),
    ("short-1000x420-open", 1000, 420, True),
]

ok = 0
import re as _re
for label, w, h, opened in CASES:
    shot = OUT / f"{label}.png"
    # Everything is measured and shot inside an IFRAME, never with
    # `--window-size=w` directly.
    #
    # AGENTS records this trap for this exact machine: **Windows clamps Chrome's
    # `--window-size` to roughly 500px**, so asking for 390 silently renders 500
    # and then crops the capture to 390. At 500 the menu's
    # `width:min(340px,84vw)` computes 340 centred in 500 - left edge at 80px -
    # and the 390px crop sliced it, so SUPPORT appeared to run off the right edge
    # in two consecutive screenshots while `probe_zorder.py` measured **zero**
    # overflowing links at a true 390px. The screenshot was wrong and the page
    # was right, which is the opposite of the usual direction and just as
    # expensive. The iframe is immune: `style="width:390px"` really is 390.
    if opened:
        src = (DIST / "index.html").read_text(encoding="utf-8")
        patched, n = _re.subn(r"<body(\s|>)", r'<body class="nav-open"\1',
                              src, count=1)
        if n != 1:
            print(f"  FAIL {label:24s} could not add nav-open to <body> "
                  f"(matched {n} times)")
            continue
        (DIST / f"__src_{label}.html").write_text(patched, encoding="utf-8")
        inner = f"__src_{label}.html"
    else:
        inner = "index.html"

    rel = f"__navshot_{label}.html"
    (DIST / rel).write_text(
        f"<!DOCTYPE html><html><head><meta charset='utf-8'>"
        f"<style>html,body{{margin:0;padding:0;background:#0b0b0d;overflow:hidden}}"
        f"iframe{{width:{w}px;height:{h}px;border:0;display:block}}</style></head>"
        f"<body><iframe id='f' src='{inner}'></iframe></body></html>",
        encoding="utf-8")
    r = subprocess.run(
        [CHROME, "--headless=new", "--disable-gpu", "--hide-scrollbars",
         f"--user-data-dir={ROOT / 'episode' / '.chrome'}",
         # window generously larger than the iframe; the IFRAME sets the viewport
         f"--window-size={w + 120},{h + 120}", "--virtual-time-budget=9000",
         f"--screenshot={shot.as_posix()}", BASE + rel],
        capture_output=True, text=True, timeout=300,
        encoding="utf-8", errors="replace")
    for tmp in (rel, f"__src_{label}.html"):
        try:
            (DIST / tmp).unlink()
        except OSError:
            pass
    if shot.exists() and shot.stat().st_size > 4000:
        print(f"  ok   {label:24s} {shot.stat().st_size:>7} bytes  -> {shot}")
        ok += 1
    else:
        print(f"  FAIL {label:24s} no screenshot "
              f"({'too small' if shot.exists() else 'missing'}). "
              f"stderr: {r.stderr.strip()[:120]}")

srv.shutdown()
print()
if ok != len(CASES):
    sys.exit(f"refusing to call this a full set: {ok}/{len(CASES)} shots taken. "
             f"A missing screenshot is not evidence the layout is fine.")
print(f"  {ok}/{len(CASES)} screenshots written to {OUT}")
