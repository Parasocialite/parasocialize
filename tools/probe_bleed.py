"""Is the page text really bleeding through the open menu, or is the menu's own
background too transparent?

Three measurements and a screenshot have all failed to settle it:
  - the screenshot shows page text ("Parasocialize", "1956", "The word. Horton
    and Wohl coined parasocial to describe television.") legible through the
    overlay;
  - `probe_zorder.py` says `elementFromPoint` returns an element inside the nav
    at every point sampled, and the nav's rect is exactly the viewport;
  - the nav's computed background is `rgba(27, 20, 16, 0.99)` - at 99% opacity,
    white text behind it should land on rgb(29,26,25) against an rgb(27,20,16)
    background, i.e. invisible. The text in the screenshot is nothing like that
    faint.

Those three cannot all be true, so one of them is measuring something else.
Rather than pick the one I believe, this **breaks the input on purpose**: paint
the nav solid red and screenshot again. Whatever is still visible is painted
above the nav; whatever vanishes was under it all along. This is the "confirm
it can fail before believing a clean report" rule applied to a confusing
observation instead of to a gate.

Also dumps, for the record, the stacking values of everything that overlaps the
top of the screen - `.grain` and any `mix-blend-mode` in particular, since a
fixed decorative layer above the header would explain a haze that no z-index on
the nav could remove.
"""
import functools
import http.server
import pathlib
import re
import socketserver
import subprocess
import sys
import threading

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

ROOT = pathlib.Path(__file__).resolve().parent.parent
CHROME = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
DIST = ROOT / "dist"
OUT = ROOT / "episode" / ".chrome" / "navshots"
OUT.mkdir(parents=True, exist_ok=True)

if not (DIST / "index.html").exists():
    sys.exit("refusing: dist/index.html missing - run build_deploy")


class H(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *a):
        pass


class S(socketserver.ThreadingTCPServer):
    allow_reuse_address = True
    daemon_threads = True


srv = S(("127.0.0.1", 0), functools.partial(H, directory=str(DIST)))
threading.Thread(target=srv.serve_forever, daemon=True).start()
BASE = f"http://127.0.0.1:{srv.server_address[1]}/"

src = (DIST / "index.html").read_text(encoding="utf-8")

# --- the experiment: solid red nav, plus a dump of what overlaps --------------
red_page = re.sub(r"<body(\s|>)", r'<body class="nav-open"\1', src, count=1)
red_page = red_page.replace(
    "</head>",
    "<style>#nav{background:#ff0000 !important}"
    ".grain{display:none !important}</style></head>", 1)
(DIST / "__red.html").write_text(red_page, encoding="utf-8")

# control: nav-open, but leave .grain alone and do not touch the background
ctl_page = re.sub(r"<body(\s|>)", r'<body class="nav-open"\1', src, count=1)
(DIST / "__ctl.html").write_text(ctl_page, encoding="utf-8")

# third: nav-open with .grain hidden only, so grain is isolated as the culprit
grain_off = re.sub(r"<body(\s|>)", r'<body class="nav-open"\1', src, count=1)
grain_off = grain_off.replace("</head>",
                              "<style>.grain{display:none !important}</style></head>", 1)
(DIST / "__grainoff.html").write_text(grain_off, encoding="utf-8")

DUMP = r"""
const f=document.getElementById('f');
function rep(o){const e=document.createElement('pre');e.id='probe-out';
e.textContent=JSON.stringify(o);document.body.appendChild(e);}
function run(){
 try{
  const d=f.contentDocument,w=f.contentWindow;
  const nav=d.getElementById('nav');
  nav.style.transition='none';
  d.body.classList.add('nav-open');
  const o={layers:[]};
  for(const e of d.querySelectorAll('body *')){
    const s=w.getComputedStyle(e);
    if(s.position!=='fixed'&&s.position!=='sticky'&&s.position!=='absolute') continue;
    const r=e.getBoundingClientRect();
    if(r.height<20||r.width<20) continue;
    if(r.bottom<10||r.top>w.innerHeight) continue;
    o.layers.push({el:e.tagName+'.'+((e.className||'')+'').trim().split(/\s+/)[0],
      pos:s.position,z:s.zIndex,blend:s.mixBlendMode,
      filter:s.filter==='none'?'-':s.filter.slice(0,18),
      backdrop:s.backdropFilter==='none'?'-':s.backdropFilter.slice(0,18),
      bg:s.backgroundColor,top:Math.round(r.top),h:Math.round(r.height),
      opacity:s.opacity, text:(e.textContent||'').trim().replace(/\s+/g,' ').slice(0,26)});
  }
  o.navBg=w.getComputedStyle(nav).backgroundColor;
  // who paints at a point where text is showing through?
  const pts=[[120,75],[120,285],[120,380]];
  o.hit=pts.map(([x,y])=>{const el=d.elementFromPoint(x,y);
    return {pt:[x,y],el:el?el.tagName+'.'+((el.className||'')+'').trim().split(/\s+/)[0]:'null',
      text:el?(el.textContent||'').trim().replace(/\s+/g,' ').slice(0,30):''};});
  rep(o);
 }catch(e){rep({error:String(e&&e.stack||e)});}
}
if(f.contentDocument&&f.contentDocument.readyState==='complete')run();
else f.addEventListener('load',run);
setTimeout(run,2500);
"""
(DIST / "__dump.html").write_text(
    f"<!DOCTYPE html><html><body style='margin:0'><iframe id='f' src='__ctl.html' "
    f"style='width:1000px;height:420px;border:0;display:block'></iframe>"
    f"<script>{DUMP}</script></body></html>", encoding="utf-8")

for name, note in (("__red.html", "nav painted SOLID RED, .grain hidden"),
                   ("__ctl.html", "control: nav-open, nothing changed"),
                   ("__grainoff.html", ".grain hidden only")):
    shot = OUT / f"probe-{name.strip('_').replace('.html', '')}.png"
    subprocess.run(
        [CHROME, "--headless=new", "--disable-gpu", "--hide-scrollbars",
         f"--user-data-dir={ROOT / 'episode' / '.chrome'}",
         "--window-size=1000,420", "--virtual-time-budget=9000",
         f"--screenshot={shot.as_posix()}", BASE + name],
        capture_output=True, text=True, timeout=300,
        encoding="utf-8", errors="replace")
    print(f"  shot {shot.name:26s} {shot.stat().st_size if shot.exists() else 0:>7} bytes"
          f"   ({note})")

dom = subprocess.run(
    [CHROME, "--headless=new", "--disable-gpu", "--hide-scrollbars",
     f"--user-data-dir={ROOT / 'episode' / '.chrome'}",
     "--dump-dom", "--virtual-time-budget=9000",
     "--window-size=1060,480", BASE + "__dump.html"],
    capture_output=True, text=True, timeout=300,
    encoding="utf-8", errors="replace")
found = re.findall(r'id="probe-out">(.*?)</pre>', dom.stdout, re.S)
if found:
    import html as _h
    import json
    r = json.loads(_h.unescape(found[-1]))
    print(f"\n  nav computed background: {r.get('navBg')}")
    print("\n  every positioned layer overlapping the viewport, in DOM order:")
    for L in r["layers"]:
        print(f"    {L['el']:24s} {L['pos']:>8} z={L['z']:>5} blend={L['blend']:>10} "
              f"filter={L['filter']:>8} backdrop={L['backdrop']:>8} "
              f"op={L['opacity']:>5} bg={L['bg']:>22}")
        if L["text"]:
            print(f"    {'':24s} text: {L['text']!r}")
    print("\n  elementFromPoint where text shows through:")
    for h in r["hit"]:
        print(f"    {str(h['pt']):>10} -> {h['el']:22s} {h['text']!r}")
else:
    print("  dump probe did not run")

for f_ in ("__red.html", "__ctl.html", "__grainoff.html", "__dump.html"):
    try:
        (DIST / f_).unlink()
    except OSError:
        pass
srv.shutdown()
