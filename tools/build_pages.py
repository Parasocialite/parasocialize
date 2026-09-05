"""Build Tier 1 (radar/<slug>.html) + Tier 2 (cases/<slug>.html) pages. No dependencies.
Usage: python tools/build_pages.py   (run AFTER build_radar.py + refresh_4h.py)
Sources: radar/*.md bodies + radar.json (cards incl. auto) + cases/*.md + cases.json.
Every grid card links to a real story page; every case teaser links to a real file page.
"""
import re, json, pathlib, html

ROOT = pathlib.Path(__file__).resolve().parents[1]

def parse_md(p):
    text = p.read_text(encoding="utf-8")
    m = re.match(r"^---\s*\n(.*?)\n---\s*\n(.*)$", text, re.S)
    if not m: return {}, text
    fm, body = m.groups()
    d = {}
    for line in fm.splitlines():
        if ":" not in line: continue
        k, v = line.split(":", 1); k = k.strip(); v = v.strip().strip('"').strip("'")
        if v.startswith("["): d[k] = [x.strip().strip("\"'") for x in v.strip("[]").split(",") if x.strip()]
        elif v.lower() in ("true", "false"): d[k] = (v.lower() == "true")
        else:
            try: d[k] = float(v) if "." in v else int(v)
            except Exception: d[k] = v
    return d, body.strip()

def paras(body):
    out = []
    for chunk in re.split(r"\n\s*\n", body or ""):
        chunk = chunk.strip()
        if not chunk or chunk.startswith("---"): continue
        if re.match(r"^(TEASER|MEMBER FULL|AUDIO)\b", chunk): continue
        out.append(f"<p>{html.escape(chunk)}</p>")
    return "\n".join(out) or "<p>Fresh find — my full take lands in the Friday Signal.</p>"

def img_for(src):
    if not src: return ""
    if src.startswith("http"): return src
    return "../" + src

HEAD = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{title} — Parasocialize</title>
<meta name="description" content="{dek}">
<link rel="stylesheet" href="../css/styles.css">
<style>.page{{max-width:720px;margin:0 auto;padding:56px 28px}}.page p{{color:var(--dim);line-height:1.75;margin-bottom:1em}}.page p b{{color:var(--ink)}}.hero-img{{width:100%;border-radius:12px;margin:18px 0}}.srcbox{{border:1px solid var(--line);border-radius:12px;padding:18px;margin:18px 0;background:var(--bg2)}}.rel{{display:grid;gap:10px;margin-top:18px}}.rel a{{border:1px solid var(--line);border-radius:10px;padding:12px 16px}}</style>
</head>
<body>
<header class="topbar"><a class="wordmark" href="..">PARA<span>SOCIALIZE</span></a><nav class="nav"><a href="..#radar">Radar</a><a href="..#signal">Signal</a></nav></header>
<div class="page">
<p class="mono" style="font-size:.62rem;letter-spacing:.22em;color:var(--accent)">{kicker}</p>
<h1 class="serif" style="font-family:Georgia,serif;font-size:clamp(1.9rem,4.5vw,2.8rem);line-height:1.1">{title}</h1>
{img}
<p style="font-size:1.05rem">{dek}</p>
<div class="srcbox"><p class="mono" style="font-size:.62rem;letter-spacing:.16em;color:var(--dim)">READ THE SOURCE</p><p><a class="btn btn-ghost" href="{surl}" target="_blank" rel="noopener">{sname} ↗</a>{s2}</p></div>
<p class="mono" style="font-size:.62rem;letter-spacing:.22em;color:var(--accent)">MY TAKE</p>
{take}
<div class="srcbox"><p>Like this lens? <a href="..#signal" style="color:var(--teal)">Get the Friday Signal →</a> · <a href="../guide/" style="color:var(--gold)">Field Guide $12 →</a></p></div>
<p class="mono" style="font-size:.62rem;letter-spacing:.22em;color:var(--accent)">RELATED</p>
<div class="rel">{rel}</div>
</div>
<footer class="footer"><div class="foot-grid"><p class="mono foot-note">© 2026 PARASOCIAL PRODUCTIONS · <a href="..">← HOME</a></p></div></footer>
</body>
</html>"""

CASE_HEAD = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{title} — Case File {no} — Parasocialize</title>
<meta name="description" content="{teaser}">
<link rel="stylesheet" href="../css/styles.css">
<style>.page{{max-width:720px;margin:0 auto;padding:56px 28px}}.page p,.page li{{color:var(--dim);line-height:1.75}}.page p b{{color:var(--ink)}}.buybox{{border:1px solid var(--gold);border-radius:14px;padding:24px;margin:24px 0;background:rgba(255,207,92,.06)}}</style>
</head>
<body>
<header class="topbar"><a class="wordmark" href="..">PARA<span>SOCIALIZE</span></a><nav class="nav"><a href="..#cases">Files</a><a href="../guide/" class="cta-link">Guide $12</a></nav></header>
<div class="page">
<p class="mono" style="font-size:.62rem;letter-spacing:.22em;color:var(--accent)">CASE FILE {no} · {date}</p>
<h1 class="serif" style="font-family:Georgia,serif;font-size:clamp(1.9rem,4.5vw,2.8rem)">{title}</h1>
<p style="font-size:1.05rem">{teaser}</p>
{take}
<div class="buybox"><h3 class="serif">The essentials live in the Field Guide — $12</h3><p><a class="btn btn-solid" href="../guide/">Get the Guide →</a> <a class="btn btn-ghost" href="..#signal">Free Signal →</a></p></div>
</div>
<footer class="footer"><div class="foot-grid"><p class="mono foot-note">© 2026 PARASOCIAL PRODUCTIONS · <a href="..">← HOME</a></p></div></footer>
</body>
</html>"""

def main():
    radar = json.loads((ROOT / "radar.json").read_text(encoding="utf-8"))
    md_by_slug = {}
    for p in (ROOT / "radar").glob("*.md"):
        fm, body = parse_md(p)
        if fm.get("slug"): md_by_slug[fm["slug"]] = (fm, body)
    n_story = 0
    for d in radar:
        slug = re.sub(r"[^a-z0-9-]", "", str(d.get("slug", ""))) or "story"
        fm, body = md_by_slug.get(slug, ({}, ""))
        title = d.get("title", slug)
        dek = d.get("dek", "")
        lenses = d.get("lenses", []) or []
        kicker = " · ".join([str(d.get("type", "")).upper()] + [str(x).upper() for x in lenses] + [str(d.get("date", ""))]).strip(" · ")
        img = f'<img class="hero-img" src="{html.escape(img_for(d.get("image","")))}" alt="{html.escape(d.get("image_alt", title))}" loading="lazy">' if d.get("image") else ""
        s2 = ""
        if d.get("source2_url"):
            s2 = f' <a class="btn btn-ghost" href="{html.escape(d["source2_url"])}" target="_blank" rel="noopener">{html.escape(d.get("source2_name","Related"))} ↗</a>'
        take = paras(body)
        if d.get("auto"):
            take += "<p><i>Found by the 4-hour sweeper. My full take lands in Friday's Signal.</i></p>"
        rel = []
        for o in radar:
            if o.get("slug") == slug: continue
            ol = set(str(x).lower() for x in (o.get("lenses", []) or []))
            if ol & set(str(x).lower() for x in lenses):
                rel.append(f'<a href="{html.escape(re.sub(r"[^a-z0-9-]", "", str(o.get("slug",""))))}.html"><b>{html.escape(o.get("title",""))}</b><br><span class="mono" style="font-size:.62rem;color:var(--dim)">{html.escape(o.get("dek","")[:90])}</span></a>')
            if len(rel) >= 3: break
        page = HEAD.format(title=html.escape(title), dek=html.escape(dek), kicker=html.escape(kicker),
            img=img, sname=html.escape(d.get("source_name", "Source")),
            surl=html.escape(d.get("source_url", "#")), s2=s2, take=take,
            rel="\n".join(rel) or "<p>More lenses land every sweep.</p>")
        (ROOT / "radar" / f"{slug}.html").write_text(page, encoding="utf-8")
        n_story += 1
    # cases
    cases = json.loads((ROOT / "cases.json").read_text(encoding="utf-8"))
    n_case = 0
    for c in cases:
        slug = c.get("slug", "")
        p = ROOT / "cases" / f"{slug}.md"
        _, body = parse_md(p) if p.exists() else ({}, "")
        page = CASE_HEAD.format(title=html.escape(c.get("title", slug)), no=html.escape(str(c.get("file_no", ""))),
            date=html.escape(str(c.get("date", ""))), teaser=html.escape(c.get("teaser", "")), take=paras(body))
        (ROOT / "cases" / f"{slug}.html").write_text(page, encoding="utf-8")
        n_case += 1
    print(f"built {n_story} story pages + {n_case} case pages")

if __name__ == "__main__":
    main()
