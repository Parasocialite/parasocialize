"""Measure the front page after the masthead rewrite.

Three claims to check, none of which a passing build proves:
  1. the thesis numbers stayed two-tone after becoming links (`.masthead a`
     has higher specificity than `.thesis-num`, so the fix must be live);
  2. the iYi character sits where the giant name was, inside its box, without
     overlapping the doors below it;
  3. nothing overflows horizontally, at desktop or on a phone.

Fails the run if the stylesheet is not live - an unstyled page reports no
overflow for anything at all.
"""
import functools, http.server, json, pathlib, socketserver, subprocess, sys, threading

ROOT = pathlib.Path(__file__).resolve().parent.parent
CHROME = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
DIST = ROOT / "dist"
OUT = ROOT / "episode" / ".chrome"
OUT.mkdir(parents=True, exist_ok=True)
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
<iframe id="f" src="index.html" style="width:{w}px;height:1500px;border:0;display:block"></iframe>
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
    const declared = [...d.querySelectorAll('link[rel~="stylesheet"]')].length;
    const bodyBg = w.getComputedStyle(d.body).backgroundColor;
    const cssOK = d.styleSheets.length >= declared && bodyBg !== 'rgba(0, 0, 0, 0)';
    if (!cssOK) return report({{wanted: {w}, cssOK, declared,
                                loaded: d.styleSheets.length, bodyBg}});

    const doc = d.documentElement;
    const num = [...d.querySelectorAll('.thesis-num')];
    const txt = [...d.querySelectorAll('.thesis-txt')];
    const sides = [...d.querySelectorAll('.thesis-side')];
    const line = d.querySelector('.masthead .line');
    const mark = d.querySelector('.masthead-mark');
    const svg = mark ? mark.querySelector('svg') : null;
    const doors = [...d.querySelectorAll('.fdoor')];
    const th = d.querySelector('.thesis');

    const R = e => {{ const r = e.getBoundingClientRect();
      return {{t: Math.round(r.top), b: Math.round(r.bottom),
               l: Math.round(r.left), r: Math.round(r.right),
               w: Math.round(r.width), h: Math.round(r.height)}}; }};

    const o = {{
      wanted: {w}, inner: w.innerWidth, cssOK,
      hOverflow: doc.scrollWidth - w.innerWidth,
      thesisColor: num.map(e => w.getComputedStyle(e).color),
      thesisDecor: num.map(e => w.getComputedStyle(e).textDecorationLine),
      thesisRects: num.map(R),
      sideRects: sides.map(R),
      txtRects: txt.map(R),
      lineRect: line ? R(line) : null,
      lineH: line ? Math.round(line.getBoundingClientRect().height) : null,
      markRect: mark ? R(mark) : null,
      svgRect: svg ? {{w: Math.round(svg.getBoundingClientRect().width),
                       h: Math.round(svg.getBoundingClientRect().height)}} : null,
      doorRects: doors.map(R),
      thesisRows: (() => {{
        const tops = sides.map(e => Math.round(e.getBoundingClientRect().top));
        const rows = [];
        tops.forEach(t => {{ if (!rows.length || t - rows[rows.length-1] > 6) rows.push(t); }});
        return rows.length;
      }})(),
    }};

    // does the mascot collide with whatever FOLLOWS the masthead? The thesis
    // doors sit above it in the DOM, so comparing against doors[0] reports a
    // 268px "overlap" that is just document order.
    if (mark) {{
      const after = mark.closest('section').nextElementSibling;
      if (after) {{
        const m = mark.getBoundingClientRect(), a = after.getBoundingClientRect();
        o.markGap = Math.round(a.top - m.bottom);
        o.afterTag = after.className || after.tagName;
      }}
    }}
    // does any thesis text spill out of its own side?
    o.txtSpill = sides.map((s, i) => {{
      const a = s.getBoundingClientRect(), b = txt[i].getBoundingClientRect();
      return Math.round(b.bottom - a.bottom);
    }});
    // the numbers must not sit on top of the text beside them
    o.numTextGap = sides.map((s, i) => {{
      const a = num[i].getBoundingClientRect(), b = txt[i].getBoundingClientRect();
      return Math.round(b.left - a.right);
    }});
    report(o);
  }} catch (e) {{ report({{wanted: {w}, error: String(e)}}); }}
}}
if (document.readyState === 'complete') run();
else window.addEventListener('load', run);
setTimeout(run, 3000);
</script></body></html>"""

BAD = 0
for width in LADDER:
    rel = f"__front_{width}.html"
    (DIST / rel).write_text(WRAPPER.replace("{w}", str(width)).replace("{{", "\x00").replace("}}", "\x01").replace("\x00", "{").replace("\x01", "}"), encoding="utf-8")
    shot = OUT / f"front-{width}.png"
    r = subprocess.run(
        [CHROME, "--headless=new", "--disable-gpu", "--hide-scrollbars",
         f"--user-data-dir={OUT}",
         f"--window-size={width + 140},1700", "--virtual-time-budget=9000",
         "--dump-dom", BASE + rel],
        capture_output=True, text=True, timeout=300,
        encoding="utf-8", errors="replace")
    try:
        (DIST / rel).unlink()
    except OSError:
        pass
    mm = __import__("re").search(r'<pre id="probe-out">(\{.*?\})</pre>',
                                 r.stdout, __import__("re").S)
    if not mm:
        print("=" * 72); print(width, "px"); print("   RED no probe output")
        print("   dom head:", r.stdout[:300].replace("\n", " "))
        BAD += 1; continue
    m = json.loads(__import__("html").unescape(mm.group(1)))
    print("=" * 72)
    print(width, "px")
    if not m.get("cssOK"):
        print("   RED stylesheet not live:", m); BAD += 1; continue
    if m.get("error"):
        print("   RED probe error:", m["error"]); BAD += 1; continue
    probs = []
    if m["hOverflow"] > 1: probs.append(f"horizontal overflow {m['hOverflow']}px")
    cols = m["thesisColor"]
    if len(cols) == 2:
        if cols[0] == cols[1]: probs.append(f"thesis numbers same colour {cols[0]}")
    else: probs.append(f"expected 2 thesis numbers, got {len(cols)}")
    if m["svgRect"] and (m["svgRect"]["w"] < 40 or m["svgRect"]["w"] > 200):
        probs.append(f"svg size odd {m['svgRect']}")
    if m.get("markGap") is not None and m["markGap"] < 0:
        probs.append(f"mascot overlaps doors by {-m['markGap']}px")
    if any(s > 2 for s in m["txtSpill"]): probs.append(f"text spills {m['txtSpill']}")
    if any(g < 0 for g in m["numTextGap"]): probs.append(f"num/text collide {m['numTextGap']}")
    if m["hOverflow"] <= 1 and m["thesisRows"] not in (1, 2): probs.append("odd thesis rows")
    print(f"   rows={m['thesisRows']} lineH={m['lineH']} "
          f"mark={m['markRect']} svg={m['svgRect']} markGap={m.get('markGap')}")
    print(f"   colors={cols}")
    print(f"   txtSpill={m['txtSpill']} numTextGap={m['numTextGap']} hOverflow={m['hOverflow']}")
    print(f"   doors={m['doorRects']}")
    if probs:
        BAD += 1
        for p in probs: print("   RED", p)
    else:
        print("   OK nothing wrong")
print("=" * 72)
sys.exit(1 if BAD else 0)
