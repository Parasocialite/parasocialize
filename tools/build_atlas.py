#!/usr/bin/env python3
"""
build_atlas.py - /atlas/. A flyable constellation of the catalogue.

WHY A CONSTELLATION
A catalogue of 176 things reads as a list, and a list of 176 things is a list
nobody scrolls. What the data actually has is structure: figures connected to
works by `wrote`, works connected to mechanisms by `instance_of`, and every
entry sitting in a medium and an era. A force layout draws that structure by
accident, which is the whole appeal - the clusters are not designed, they are
what falls out of the edges, so a lane nobody maintained still shows up as a
neighbourhood.

THE SIMULATION IS HANDWRITTEN
The site has no build step, no package.json and no framework, and that is
deliberate: it is a folder of static files that a person can open. So there is
no d3 here. Repulsion is brute force, which is fine at 176 nodes (about 15,000
pair tests a frame) and would not be fine at 15,000.

CLUSTERING IS A FORCE, NOT A LAYOUT
Nodes are pulled toward an anchor derived from their era and their first
medium, so the arrangement self-organises by domain and time without anyone
assigning an x and y. The anchors are placed on a golden-angle spiral scaled by
era bucket, which is the one bit of authored geometry in here.

HONESTY IS VISUAL
A node whose citations have not been checked is drawn hollow, and an inferred
medium tag is drawn with a dashed ring. The site's own footer says the
unverified ones are marked rather than hidden; a map that quietly rendered 122
unchecked entries as equal to 54 checked ones would be making exactly the
claim the rest of the site argues against.

  python tools/build_atlas.py
"""
import json, pathlib, sys, math

ROOT = pathlib.Path(__file__).resolve().parent.parent
OUT = ROOT / "atlas" / "index.html"

MEDIA_ORDER = ["theology", "literature", "film", "music", "television_scripted",
               "television_unscripted", "sport", "technology", "ai", "history",
               "games"]
MEDIA_LABEL = {
    "theology": "Theology", "literature": "Literature", "film": "Film",
    "music": "Music", "television_scripted": "Scripted television",
    "television_unscripted": "Unscripted television", "sport": "Sport",
    "technology": "Technology", "ai": "AI", "history": "History",
    "games": "Games"}
# eleven domains on a colour wheel, spaced evenly, because there are eleven of
# them and no one of these deserves to be the accent colour
def media_colour(i, n=11):
    h = (i / n)
    return f"hsl({int(h*360)} 76% 62%)"

REL_LABEL = {
    "bond_with": "a bond with", "wrote": "wrote", "performed": "performed",
    "depicts": "depicts", "adapted_from": "adapted from",
    "succeeded": "was succeeded by", "cites": "is evidence for",
    "member_of": "is a member of", "contemporary": "lived alongside",
    "influenced": "influenced", "instance_of": "is an instance of",
    "preceded": "came before", "occurred_in": "happened at",
}

PAGE = """<!DOCTYPE html>
<html lang="en"><head><meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>The Atlas - Parasocialize</title>
<meta name="description" content="Every significant instance of the parasocial, as a graph. Drag it. It arranges itself.">
<link rel="canonical" href="{site}/atlas/">
<link rel="alternate" type="application/rss+xml" title="Parasocialize" href="{site}/radar.xml">
<link rel="icon" type="image/svg+xml" href="{site}/favicon.svg">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Fraunces:ital,opsz,wght@0,9..144,600;0,9..144,700;0,9..144,900;1,9..144,600&family=IBM+Plex+Mono:wght@400;500&display=swap" rel="stylesheet">
<link rel="stylesheet" href="../css/styles.css">
<link rel="stylesheet" href="../css/mascot.css">
<style>
.atlas-wrap{{position:relative;height:calc(100vh - 118px);min-height:520px;overflow:hidden}}
#sky{{position:absolute;inset:0;width:100%;height:100%;display:block;
  cursor:grab;background:
  radial-gradient(1200px 700px at 22% 12%,rgba(255,90,26,.10),transparent 62%),
  radial-gradient(1000px 620px at 82% 82%,rgba(180,92,255,.09),transparent 60%),
  #120c09}}
#sky.grabbing{{cursor:grabbing}}
.hud{{position:absolute;z-index:4;background:rgba(14,9,6,.82);
  border:1px solid var(--line);border-radius:10px;backdrop-filter:blur(7px)}}
.hud-tl{{top:14px;left:14px;padding:13px 15px;max-width:262px}}
.hud-tl h1{{margin:0 0 3px;font-size:1.5rem;line-height:1.05}}
.hud-tl p{{margin:0;font-size:.78rem;color:var(--dim);line-height:1.45}}
.hud-tr{{top:14px;right:14px;padding:11px 13px;width:196px}}
.hud-tr h2{{margin:0 0 7px;font-size:.52rem;letter-spacing:.18em;color:var(--dimmer);
  text-transform:uppercase;font-family:var(--label)}}
.filt{{display:flex;flex-wrap:wrap;gap:4px;margin-bottom:9px}}
.filt:last-of-type{{margin-bottom:0}}
.chip2{{font-family:var(--label);font-size:.5rem;letter-spacing:.08em;
  text-transform:uppercase;padding:4px 7px;border:1px solid var(--line2);
  border-radius:99px;cursor:pointer;color:var(--dim);background:transparent;
  user-select:none;line-height:1;white-space:nowrap}}
.chip2[aria-pressed="true"]{{background:currentColor;border-color:transparent}}
.chip2[aria-pressed="true"] span{{color:#120c09}}
.chip2:hover{{border-color:var(--hot)}}
.panel{{position:absolute;z-index:5;top:14px;bottom:14px;right:14px;width:min(392px,42vw);
  overflow-y:auto;padding:20px 22px 26px;display:none}}
.panel.on{{display:block}}
.panel .kicker{{margin:0 0 6px}}
.panel h2{{margin:0 0 3px;font-size:1.62rem;line-height:1.08}}
.panel .yrs{{font-family:var(--label);font-size:.58rem;letter-spacing:.14em;
  color:var(--hot);text-transform:uppercase;margin:0 0 11px}}
.panel p{{font-size:.9rem;line-height:1.55;margin:0 0 12px}}
.panel .sig{{border-left:2px solid var(--hot);padding-left:12px;color:#f0e4d4}}
.panel h3{{font-size:.5rem;letter-spacing:.18em;text-transform:uppercase;
  font-family:var(--label);color:var(--dimmer);margin:20px 0 8px}}
.panel .rel{{list-style:none;margin:0;padding:0;display:grid;gap:5px}}
.panel .rel a{{display:grid;grid-template-columns:1fr;gap:1px;text-decoration:none;
  border:1px solid var(--line);border-radius:6px;padding:7px 9px}}
.panel .rel a:hover{{border-color:var(--hot);background:rgba(255,90,26,.06)}}
.panel .rel em{{font-style:normal;font-size:.83rem;color:#f4e8d8}}
.panel .rel i{{font-style:normal;font-family:var(--label);font-size:.48rem;
  letter-spacing:.1em;text-transform:uppercase;color:var(--dimmer)}}
.panel .cite{{font-size:.74rem;color:var(--dim);line-height:1.5;margin:0 0 9px;
  padding-left:11px;border-left:1px solid var(--line2)}}
.panel .cite b{{display:block;color:var(--hot);font-size:.6rem;letter-spacing:.1em;
  text-transform:uppercase;font-family:var(--label);margin-bottom:2px}}
.panel .cite a{{color:var(--dim)}}
.x{{position:absolute;top:11px;right:13px;cursor:pointer;color:var(--dimmer);
  font-size:1.15rem;line-height:1;background:none;border:0;cursor:pointer}}
.x:hover{{color:var(--hot)}}
.tip{{position:absolute;z-index:6;pointer-events:none;opacity:0;transition:opacity .12s;
  background:rgba(10,6,4,.94);border:1px solid var(--line2);border-radius:6px;
  padding:5px 8px;font-size:.72rem;max-width:230px;line-height:1.35}}
.tip b{{color:#fff;font-weight:600}}
.legend{{position:absolute;left:14px;bottom:14px;z-index:4;padding:10px 13px;
  font-family:var(--label);font-size:.5rem;letter-spacing:.1em;color:var(--dimmer);
  text-transform:uppercase;line-height:1.9}}
.legend i{{display:inline-block;width:9px;height:9px;border-radius:50%;
  margin-right:6px;vertical-align:-1px}}
.legend .hollow{{background:transparent;border:1.5px solid #c9b39a}}
.legend .full{{background:#c9b39a}}
.hint{{position:absolute;left:50%;bottom:14px;transform:translateX(-50%);z-index:4;
  font-family:var(--label);font-size:.5rem;letter-spacing:.14em;color:var(--dimmer);
  text-transform:uppercase;pointer-events:none;transition:opacity .4s}}
@media (max-width:900px){{.hud-tr{{display:none}}.panel{{width:auto;left:14px}}}}
</style>
</head>
<body>
<a class="skip" href="#list">Skip the map, read the list</a>
<div class="grain" aria-hidden="true"></div>
{mk}
<main class="atlas-wrap" id="wrap">
  <canvas id="sky"></canvas>

  <div class="hud hud-tl">
    <h1>The Atlas</h1>
    <p>{n} entries in {e} connections. Drag to throw it, scroll to fly in, click
    anything to read it. It arranges itself by era and by medium - nobody
    placed these dots.</p>
  </div>

  <div class="hud hud-tr">
    <h2>Medium</h2><div class="filt" id="f-med"></div>
    <h2>Kind of thing</h2><div class="filt" id="f-kind"></div>
    <h2>Real, or not</h2><div class="filt" id="f-fk"></div>
    <h2>State</h2><div class="filt" id="f-state"></div>
  </div>

  <div class="hud legend">
    <div><i class="full"></i>sourced</div>
    <div><i class="hollow"></i>citation not yet checked</div>
  </div>

  <p class="hint" id="hint">drag the background &middot; scroll to zoom &middot; click a node</p>
  <div class="tip" id="tip"></div>
  <aside class="hud panel" id="panel" aria-live="polite"></aside>
</main>

<section id="list" style="padding:44px 5vw 60px">
  <p class="kicker">The same {n} entries, as a list</p>
  <h2 style="font-size:2rem;margin:0 0 6px">Because a map is no use to anybody
  who cannot use it.</h2>
  <p style="color:var(--dim);max-width:62ch;margin:0 0 26px">Every node in the
  constellation, with a link to its own page. Sorted by year, undated last.</p>
  <div style="display:grid;grid-template-columns:repeat(auto-fill,minmax(268px,1fr));gap:9px">
  {rows}
  </div>
</section>
{foot}
<!--ATLAS-SCRIPT-->
</body></html>"""


def esc(s):
    return (str(s or "").replace("&", "&amp;").replace("<", "&lt;")
            .replace(">", "&gt;").replace('"', "&quot;"))


def main():
    sys.path.insert(0, str(ROOT / "tools"))
    import build_cards as bc

    graph = json.loads((ROOT / "data" / "atlas.json").read_text(encoding="utf-8"))
    nodes, edges = graph["nodes"], graph["edges"]
    enc = json.loads((ROOT / "data" / "encyclopedia.json").read_text(encoding="utf-8"))

    mk = bc.NAV.format(root="../", total=len(enc["entries"]), mk=bc.mascot(30, "wm-mascot"))
    foot = bc.FOOT.format(root="../", sweep=bc.MESSY,
                          motto='THE UNVERIFIED ONES ARE MARKED.<br>NOT HIDDEN.')

    # --- anchors: a golden-angle spiral, one bay per medium, radius by era
    anchors = {}
    for i, m in enumerate(MEDIA_ORDER):
        a = i * 2.39996323
        r = 150 + 62 * i
        anchors[m] = (r * math.cos(a), r * math.sin(a) * 0.62)

    payload = []
    for nd in nodes:
        m = nd["m"][0] if nd["m"] else "history"
        ax, ay = anchors.get(m, (0.0, 0.0))
        era = nd.get("y")
        era_push = 0.0 if era is None else max(-1.0, min(1.0, (era or 0) / 2020.0))
        payload.append({
            "i": nd["id"], "t": nd["t"], "k": nd["k"], "fk": nd["fk"],
            "y": nd["y"], "ye": nd.get("ye"), "m": nd["m"],
            "mi": nd.get("mi", 0), "v": nd["v"],
            "s": nd.get("s", ""), "g": nd.get("g", ""), "era": nd.get("era", ""),
            "src": nd.get("src", []),
            "ax": round(ax + era_push * 190, 1), "ay": round(ay + era_push * 96, 1),
        })

    colours = {m: media_colour(i) for i, m in enumerate(MEDIA_ORDER)}
    kinds = sorted({n["k"] for n in nodes})
    fks = ["real", "mythological", "fictitious"]

    byid = {n["id"]: n for n in nodes}
    # `note`, not `s`: the client builds each edge as {s: sourceNode, t: targetNode,
    # ...rest}, and a key called `s` in the payload overwrote the source node with
    # a string. Then `e.s.on` was undefined, every edge took the `continue`, and
    # the graph drew 176 dots and not one line between them.
    out_edges = [{"a": e["s"], "b": e["t"], "y": e["ty"], "l": REL_LABEL.get(e["ty"], e["ty"]),
                  "note": e.get("n", "")} for e in edges
                 if e["s"] in byid and e["t"] in byid]

    # --- the accessible list
    rows = []
    for nd in sorted(nodes, key=lambda x: (x["y"] is None, x["y"] or 0, x["t"])):
        yr = "undated" if nd["y"] is None else (
            f"{nd['y']}" if nd.get("ye") is None else f"{nd['y']}&ndash;{nd['ye']}")
        dot = "&#9679;" if nd["v"] else "&#9675;"
        rows.append(
            f'<a href="../encyclopedia/{esc(nd["id"])}.html" data-atlas="{esc(nd["id"])}" '
            f'style="display:block;border:1px solid var(--line);border-radius:8px;'
            f'padding:11px 13px;text-decoration:none">'
            f'<span style="font-family:var(--label);font-size:.5rem;letter-spacing:.1em;'
            f'color:{colours.get((nd["m"] or ["history"])[0], "#ccc")};text-transform:uppercase">'
            f'{dot} {esc((nd["m"] or [""])[0].replace("_", " "))}</span>'
            f'<b style="display:block;font-family:var(--serif);font-size:.95rem;'
            f'color:#f4e8d8;margin:3px 0 2px;line-height:1.2">{esc(nd["t"])}</b>'
            f'<span style="font-size:.72rem;color:var(--dimmer)">{yr}</span></a>')

    # The state sentence, computed here so it cannot describe a graph that no
    # longer exists.
    deg = {n["i"]: 0 for n in payload}
    for e in out_edges:
        deg[e["a"]] = deg.get(e["a"], 0) + 1
        deg[e["b"]] = deg.get(e["b"], 0) + 1
    joined = sum(1 for v in deg.values() if v)
    lone = len(payload) - joined
    hubs = sorted(deg.items(), key=lambda kv: -kv[1])[:3]
    hub_names = [t for t, _ in [(n["t"], n["i"]) for n in payload
                                if n["i"] in dict(hubs)]]
    if lone == 0:
        state = (f"Every one of the {len(payload)} is joined to something. "
                 f"The best connected are {hub_names[0].lower()}, "
                 f"{hub_names[1].lower()} and {hub_names[2].lower()}, and they "
                 f"are the shape of the thing.")
    else:
        state = (f"{joined} of the {len(payload)} are joined to something. "
                 f"The other {lone} are here because they belong here, and the "
                 f"edges are the work still to do.")

    data = {"nodes": payload, "edges": out_edges,
            "media": MEDIA_LABEL, "colours": colours, "kinds": kinds,
            "fk": fks, "rel": REL_LABEL, "site": bc.SITE}

    OUT.parent.mkdir(exist_ok=True)
    # The client script is inlined and the graph handed to it as a literal, so
    # /atlas/ is one file with no fetch and no build step.
    # The doubled braces are unescaped on the TEMPLATE only. Doing it after the
    # data was spliced in ate every `}}` at the end of a nested object in the
    # JSON literal, the client script failed to parse, and the canvas came up
    # empty behind a perfectly good-looking HUD.
    #
    # The script is spliced at a sentinel, not at `</body>`, because
    # str.replace() replaces every occurrence and `</body>` was not unique in
    # the assembled template. The script went in twice, the second `const E` and
    # `const N` re-declared in the same scope, the whole block died on that line,
    # and the page showed 176 dots and zero edges with no error anywhere.
    tmpl = PAGE.replace("{{", "{").replace("}}", "}")
    if tmpl.count("<!--ATLAS-SCRIPT-->") != 1:
        raise SystemExit("atlas: the script sentinel is missing or duplicated")
    js = JS.replace("__DATA__", json.dumps(data, ensure_ascii=False)
                    .replace("</", "<\\/"))
    js = js.replace("__STATE__", json.dumps(state))
    html = (tmpl
            .replace("{site}", bc.SITE)
            .replace("{n}", str(len(nodes)))
            .replace("{e}", str(len(out_edges)))
            .replace("{mk}", mk).replace("{foot}", foot)
            .replace("{rows}", "".join(rows))
            .replace("<!--ATLAS-SCRIPT-->", "<script>" + js + "</script>"))
    if html.count("const E = D.edges") != 1:
        raise SystemExit("atlas: the client script was emitted more than once")
    OUT.write_text(html, encoding="utf-8")
    print(f"atlas: {len(payload)} nodes, {len(out_edges)} edges, "
          f"{len(rows)} list rows -> {OUT}")


JS = r"""
/* THE NAMESPACE RULE, AND WHY IT IS HERE
   The payload keys are single letters - i, t, s, y, m, v, k, g - because the
   file is 350KB of JSON and they add up. That was a mistake with a body count.
   The simulation also wants x, y, vx, vy, and the selection wanted s and t to
   mean "neighbour ids". So the layout wrote the year 1970 into the node's y
   coordinate and the panel printed 288.857117859941, and selecting a node
   overwrote its own summary with a comma list of its neighbours' ids, so the
   second entry you opened showed the first one's neighbours as its prose.

   Both bugs were silent, both looked like content problems, and both came from
   one habit. So: the payload lives under `d` and is never written to. Every
   simulation field is owned by the simulation. */
const D = __DATA__;
const cv = document.getElementById('sky'), cx = cv.getContext('2d');
const panel = document.getElementById('panel'), tip = document.getElementById('tip');
const hint = document.getElementById('hint');
const reduce = matchMedia('(prefers-reduced-motion: reduce)').matches;
let W = 0, H = 0, DPR = Math.min(devicePixelRatio || 1, 2);

const KIND_R = {figure: 7.5, work: 6.5, study: 6, institution: 6,
                event: 5.5, term: 5, mechanism: 5, case: 5.5};
const fkR = {real: 2.6, mythological: 3.2, fictitious: 2.2};

const st = { med: new Set(), kind: new Set(), fk: new Set(), onlyVerified: false };
D.mediaOrder = Object.keys(D.colours);

const N = D.nodes.map((d, idx) => ({
  d, idx, deg: 0, on: true, vx: 0, vy: 0,
  x: d.ax + (Math.random() - 0.5) * 90,
  y: d.ay + (Math.random() - 0.5) * 90,
  r: (KIND_R[d.k] || 5) + (d.fk ? (fkR[d.fk] || 0) : 0)
}));
const byId = {};
N.forEach(n => { byId[n.d.i] = n; });

// spread first, then the resolved endpoints, so no payload key can shadow them
const E = D.edges
  .filter(e => byId[e.a] && byId[e.b])
  .map(e => ({ ...e, s: byId[e.a], t: byId[e.b] }));
for (const e of E) { e.s.deg++; e.t.deg++; }
// hubs read as hubs rather than as one more dot
for (const n of N) {
  if (n.deg >= 8) n.r += 2.2;
  else if (n.deg >= 5) n.r += 1.1;
}

let cam = { x: 0, y: 0, k: 1 }, drag = null, hover = null;
// the selection's neighbours live here, NOT on the node, for the reason above
let sel = null, selNb = { s: [], t: [] };

function resize() {
  const r = cv.getBoundingClientRect();
  W = r.width; H = r.height;
  cv.width = W * DPR; cv.height = H * DPR;
  cx.setTransform(DPR, 0, 0, DPR, 0, 0);
}
addEventListener('resize', resize);

/* ---- forces. repulsion is brute force: 176 nodes is about 15k pair tests a
   frame, which is nothing, and it would be nothing at 1,500 too. */
function tick() {
  const A = 2100;
  for (let i = 0; i < N.length; i++) {
    const a = N[i];
    for (let j = i + 1; j < N.length; j++) {
      const b = N[j];
      let dx = a.x - b.x, dy = a.y - b.y;
      let d2 = dx * dx + dy * dy;
      if (d2 < 1) { dx = (Math.random() - .5) * 2; dy = (Math.random() - .5) * 2; d2 = 4; }
      const f = A / d2;
      const d = Math.sqrt(d2);
      const fx = (dx / d) * f, fy = (dy / d) * f;
      a.vx += fx; a.vy += fy; b.vx -= fx; b.vy -= fy;
    }
  }
  for (const e of E) {
    const dx = e.t.x - e.s.x, dy = e.t.y - e.s.y;
    const d = Math.max(1, Math.hypot(dx, dy));
    // Weak, long rest length. At 47 edges the springs could be stiff; at 417
    // they beat the anchors and every bay collapsed into one ball with a few
    // nodes flung off the side of the screen on long cross-medium edges.
    const f = (d - 120) * 0.0055;
    const fx = (dx / d) * f, fy = (dy / d) * f;
    e.s.vx += fx; e.s.vy += fy; e.t.vx -= fx; e.t.vy -= fy;
  }
  for (const n of N) {
    // The anchor pull scales with degree. A node with nineteen edges feels
    // nineteen times the spring pull of a leaf, so a flat anchor force drags
    // the well-connected hub out of its own neighbourhood - which is the one
    // node a reader most wants to see in context.
    const hold = 0.055 * (1 + n.deg / 7);
    n.vx += (n.d.ax - n.x) * hold;
    n.vy += (n.d.ay - n.y) * hold;
    n.vx -= n.x * 0.0011; n.vy -= n.y * 0.0011;
    n.vx *= 0.84; n.vy *= 0.84;
    if (!drag || drag.n !== n) { n.x += n.vx; n.y += n.vy; }
  }
}

function draw() {
  cx.clearRect(0, 0, W, H);
  cx.save();
  cx.translate(W / 2 + cam.x, H / 2 + cam.y);
  cx.scale(cam.k, cam.k);

  cx.lineWidth = 1.1 / cam.k;
  for (const e of E) {
    if (!e.s.on || !e.t.on) continue;
    const touching = sel && (e.s === sel || e.t === sel);
    const near = touching || (hover && (e.s === hover || e.t === hover));
    cx.strokeStyle = touching ? 'rgba(255,90,26,.9)'
      : near ? 'rgba(255,214,160,.75)'
      : 'rgba(226,208,188,.11)';
    cx.beginPath(); cx.moveTo(e.s.x, e.s.y); cx.lineTo(e.t.x, e.t.y); cx.stroke();
  }

  const anyOn = N.some(n => n.on);
  for (const n of N) {
    if (!n.on) continue;
    const d = n.d;
    const c = D.colours[(d.m && d.m[0]) || 'history'] || '#ccc';
    const near = sel && (selNb.s.indexOf(d.i) >= 0 || selNb.t.indexOf(d.i) >= 0);
    cx.fillStyle = d.v ? c : 'rgba(18,12,9,.9)';
    cx.globalAlpha = (anyOn && (sel || hover) && !(near || n === sel)) ? 0.22 : 1;
    cx.beginPath(); cx.arc(n.x, n.y, n.r, 0, 6.2832); cx.fill();
    if (!d.v) {
      cx.globalAlpha = 1; cx.strokeStyle = c;
      cx.lineWidth = 1.3 / cam.k; cx.stroke();
    }
    // an inferred medium tag gets a dashed ring: the map is saying which parts
    // of itself are inference rather than authored
    if (d.mi && (n === sel || n === hover)) {
      cx.setLineDash([2 / cam.k, 2.5 / cam.k]);
      cx.strokeStyle = 'rgba(255,255,255,.6)'; cx.lineWidth = 1 / cam.k;
      cx.beginPath(); cx.arc(n.x, n.y, n.r + 3.6, 0, 6.2832); cx.stroke();
      cx.setLineDash([]);
    }
    cx.globalAlpha = 1;
  }

  if (sel) {
    cx.strokeStyle = '#ff5a1a'; cx.lineWidth = 1.8 / cam.k;
    cx.beginPath(); cx.arc(sel.x, sel.y, sel.r + 6, 0, 6.2832); cx.stroke();
    // 13/cam.k is 13 screen pixels whatever the zoom. The original was
    // 600/cam.k, which at cam.k 1.35 painted a 444px label across the canvas.
    cx.fillStyle = '#fff';
    cx.font = (13 / cam.k) + 'px "IBM Plex Mono", monospace';
    cx.textAlign = 'center';
    cx.fillText(sel.d.t, sel.x, sel.y - sel.r - 10 / cam.k);
  }
  cx.restore();
}

function frame() {
  if (!reduce) tick();
  applyFilters();
  draw();
  requestAnimationFrame(frame);
}

function applyFilters() {
  const anyMed = st.med.size, anyK = st.kind.size, anyFk = st.fk.size;
  for (const n of N) {
    const d = n.d;
    n.on = (!anyMed || d.m.some(m => st.med.has(m)))
        && (!anyK || st.kind.has(d.k))
        && (!anyFk || !d.fk || st.fk.has(d.fk))
        && (!st.onlyVerified || d.v);
  }
}

/* ---- interaction */
function toWorld(px, py) {
  return { x: (px - W / 2 - cam.x) / cam.k, y: (py - H / 2 - cam.y) / cam.k };
}
function pick(px, py) {
  const p = toWorld(px, py);
  let best = null, bd = 1e9;
  for (const n of N) {
    if (!n.on) continue;
    const d = Math.hypot(n.x - p.x, n.y - p.y);
    if (d < n.r + 7 && d < bd) { best = n; bd = d; }
  }
  return best;
}
cv.addEventListener('pointerdown', e => {
  cv.setPointerCapture(e.pointerId);
  const n = pick(e.offsetX, e.offsetY);
  drag = n ? { n, moved: false } : { sx: e.offsetX, sy: e.offsetY, cx: cam.x, cy: cam.y };
  cv.classList.toggle('grabbing', !n);
  hint.style.opacity = 0;
});
cv.addEventListener('pointermove', e => {
  if (drag && drag.n) {
    const p = toWorld(e.offsetX, e.offsetY);
    drag.n.x = p.x; drag.n.y = p.y; drag.n.vx = drag.n.vy = 0; drag.moved = true;
    return;
  }
  if (drag) {
    cam.x = drag.cx + (e.offsetX - drag.sx);
    cam.y = drag.cy + (e.offsetY - drag.sy);
    return;
  }
  const n = pick(e.offsetX, e.offsetY);
  if (n !== hover) {
    hover = n;
    if (n) {
      tip.innerHTML = '<b>' + esc(n.d.t) + '</b><br>' + esc((n.d.m || []).join(', '));
      tip.style.opacity = 1;
    } else tip.style.opacity = 0;
  }
  if (n) {
    const r = cv.getBoundingClientRect();
    tip.style.left = Math.min(r.width - 240, e.offsetX + 14) + 'px';
    tip.style.top = (e.offsetY + 16) + 'px';
  }
});
addEventListener('pointerup', () => {
  if (drag && drag.n && !drag.moved) open(drag.n);
  drag = null; cv.classList.remove('grabbing');
});
cv.addEventListener('pointerleave', () => { tip.style.opacity = 0; hover = null; });
cv.addEventListener('wheel', e => {
  e.preventDefault();
  const p = toWorld(e.offsetX, e.offsetY);
  const f = Math.exp(-e.deltaY * 0.0016);
  const nk = Math.max(0.22, Math.min(7, cam.k * f));
  cam.x = e.offsetX - W / 2 - (p.x * nk);
  cam.y = e.offsetY - H / 2 - (p.y * nk);
  cam.k = nk;
}, { passive: false });
addEventListener('keydown', e => { if (e.key === 'Escape') close(); });

function esc(s) {
  return String(s == null ? '' : s).replace(/[&<>"]/g, c =>
    ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]));
}
function yr(d) {
  if (d.y == null) return 'undated';
  return d.ye ? d.y + '\u2013' + d.ye : '' + d.y;
}

function open(n) {
  sel = n;
  const d = n.d;
  const inc = E.filter(e => e.b === n.d.i), out = E.filter(e => e.a === n.d.i);
  selNb = { s: inc.map(e => e.a), t: out.map(e => e.b) };
  const seen = new Set(), rel = [];
  for (const e of [...inc, ...out]) {
    const o = e.a === n.d.i ? e.t : e.s;
    if (seen.has(o.d.i)) continue;
    seen.add(o.d.i);
    rel.push({ o, l: e.a === n.d.i ? e.l : (D.rel[e.y] || e.y) });
  }
  rel.sort((a, b) => a.o.d.t.localeCompare(b.o.d.t));
  const cites = (d.src || []).map(s =>
    '<p class="cite"><b>' + esc(s.status || 'unchecked') + '</b>' +
    esc(s.claim || '') + '<br>' + esc(s.citation || '') +
    (s.url ? ' <a href="' + esc(s.url) + '" target="_blank" rel="noopener">source</a>' : '') +
    '</p>').join('');
  panel.innerHTML =
    '<button class="x" id="cx" aria-label="Close">&times;</button>' +
    '<p class="kicker">' + esc((d.m || []).join(' \u00b7 ') || 'unclassified') + '</p>' +
    '<h2>' + esc(d.t) + '</h2>' +
    '<p class="yrs">' + esc(d.k) + (d.fk ? ' \u00b7 ' + d.fk : '') + ' \u00b7 ' + yr(d) +
    (d.era ? ' \u00b7 ' + esc(d.era) : '') + (d.v ? '' : ' \u00b7 citation not yet checked') + '</p>' +
    (d.s ? '<p>' + esc(d.s) + '</p>' : '') +
    (d.g ? '<p class="sig">' + esc(d.g) + '</p>' : '') +
    (rel.length ? '<h3>Connected to</h3><ul class="rel">' + rel.map(r =>
      '<li><a href="#" data-go="' + esc(r.o.d.i) + '"><em>' + esc(r.o.d.t) +
      '</em><i>' + esc(r.l) + '</i></a></li>').join('') + '</ul>' : '') +
    (cites ? '<h3>Sources</h3>' + cites : '<h3>Sources</h3><p class="cite">none recorded</p>') +
    '<h3>Full entry</h3><p><a href="../encyclopedia/' + esc(d.i) +
    '.html" style="color:var(--hot)">' + esc(d.t) + ' &rarr;</a></p>';
  panel.classList.add('on');
  panel.scrollTop = 0;
  document.getElementById('cx').onclick = close;
  panel.querySelectorAll('[data-go]').forEach(a => a.onclick = ev => {
    ev.preventDefault();
    const t = byId[a.dataset.go];
    if (t) { open(t); focus(t); }
  });
  if (!/[#&]n=/.test(location.hash)) history.replaceState(null, '', '#n=' + d.i);
}
function close() { sel = null; selNb = { s: [], t: [] }; panel.classList.remove('on'); }

/* ---- filters */
function chip(parent, label, colour, fn) {
  const b = document.createElement('button');
  b.className = 'chip2'; b.type = 'button';
  b.setAttribute('aria-pressed', 'false');
  b.style.color = colour || '';
  b.innerHTML = '<span>' + esc(label) + '</span>';
  b.onclick = () => {
    const now = b.getAttribute('aria-pressed') !== 'true';
    b.setAttribute('aria-pressed', String(now));
    fn(now);
  };
  parent.appendChild(b);
  return b;
}
const fm = document.getElementById('f-med');
D.mediaOrder.forEach(m => chip(fm, D.media[m] || m, D.colours[m], v => {
  v ? st.med.add(m) : st.med.delete(m);
}));
const fkEl = document.getElementById('f-kind');
D.kinds.forEach(k => chip(fkEl, k, null, v => { v ? st.kind.add(k) : st.kind.delete(k); }));
const ff = document.getElementById('f-fk');
D.fk.forEach(k => chip(ff, k, null, v => { v ? st.fk.add(k) : st.fk.delete(k); }));
chip(document.getElementById('f-state'), 'sourced only', null, v => st.onlyVerified = v);

/* ---- framing */
function fit() {
  let x0 = 1e9, y0 = 1e9, x1 = -1e9, y1 = -1e9;
  for (const n of N) {
    if (!n.on) continue;
    x0 = Math.min(x0, n.x); y0 = Math.min(y0, n.y);
    x1 = Math.max(x1, n.x); y1 = Math.max(y1, n.y);
  }
  if (x0 > x1) return;
  // The HUD panels sit over the canvas, so framing to the full width parks two
  // clusters behind them. Fit the area the reader can see and shift the camera
  // to its centre, which is not the canvas centre.
  const wide = W > 900;
  const iL = wide ? 296 : 16, iR = wide ? 224 : 16, iT = 16, iB = 52;
  const aw = Math.max(120, W - iL - iR), ah = Math.max(120, H - iT - iB);
  const ax = iL + aw / 2, ay = iT + ah / 2;
  const k = Math.min(3, Math.max(0.16,
    Math.min(aw / Math.max(1, x1 - x0 + 80), ah / Math.max(1, y1 - y0 + 80))));
  cam.k = k;
  cam.x = (ax - W / 2) - ((x0 + x1) / 2) * k;
  cam.y = (ay - H / 2) - ((y0 + y1) / 2) * k;
}
function focus(n) {
  cam.k = Math.max(cam.k, 1.35);
  cam.x = -n.x * cam.k;
  cam.y = -n.y * cam.k;
}
addEventListener('keydown', e => { if (e.key === 'f' || e.key === 'F') fit(); });

/* Deep links. /atlas/#n=grief opens on that node with its neighbourhood lit
   and the camera framed on it, which makes a position in the catalogue
   shareable - the map is only useful to somebody else if you can point at it. */
function fromHash() {
  const m = /(?:^|[#&])n=([a-z0-9-]+)/i.exec(location.hash || '');
  if (!m) return false;
  const n = byId[m[1]];
  if (!n) return false;
  open(n); focus(n);
  return true;
}
addEventListener('hashchange', () => { if (!fromHash() && !drag) hint.style.opacity = .6; });

/* Everything above is wrapped so a failure reports itself on <body> instead of
   leaving a good-looking HUD over an empty canvas, which is what happened twice
   while this was being built. */
try {
  resize();
  if (reduce) { for (let i = 0; i < 500; i++) tick(); }
  fit();
  frame();
  const deep = fromHash();
  setTimeout(() => hint.style.opacity = 0, 9000);
  // the list under the map is a second way in: clicking a title opens the node
  // on the graph rather than leaving for the entry page
  document.querySelectorAll('[data-atlas]').forEach(a => a.addEventListener('click', ev => {
    if (!ev.metaKey && !ev.ctrlKey && !ev.shiftKey) {
      ev.preventDefault();
      location.hash = '#n=' + a.dataset.atlas;
      document.querySelector('.atlas-wrap').scrollIntoView({ behavior: 'smooth' });
    }
  }));
  document.body.dataset.ok = '1';
  // The counts are computed in Python, not here. The first version of this line
  // was written when the graph had 47 edges and said "N of the 176 are joined to
  // something" - and after the graph was filled it cheerfully reported "417 of
  // the 176", with a second sentence about entries still to do when there were
  // none. A sentence about the data belongs next to the data.
  const hud = document.querySelector('.hud-tl p');
  if (hud) hud.textContent += ' ' + __STATE__;
} catch (err) {
  document.body.dataset.ok = '0';
  const hud = document.querySelector('.hud-tl p');
  if (hud) hud.textContent += ' [ERROR: ' + (err && err.message || err) + ']';
  const t = document.getElementById('tip');
  if (t) { t.style.opacity = 1; t.textContent = 'atlas error: ' + (err && err.message || err); }
}
"""

if __name__ == "__main__":
    main()


