"""4-hour resonance sweep. No dependencies, network-failure safe.
Usage: python tools/refresh_4h.py [--no-fetch]
- Fetches Google News RSS for rotating queries, matches sightings to ledger.
- Applies decay/boost, recomputes states, rebuilds radar.json order + data/ticker.json.
- Never creates new cards (candidates go to data/candidates.json for review).
- Curator md content (titles/deks/images/links) always wins; ledger only adds resonance/state.
"""
import json, pathlib, datetime, re, sys, urllib.request, urllib.parse, xml.etree.ElementTree as ET

ROOT = pathlib.Path(__file__).resolve().parents[1]
SIG = ROOT / "data" / "signals.json"
RADAR = ROOT / "radar.json"
TICKER = ROOT / "data" / "ticker.json"
CAND = ROOT / "data" / "candidates.json"
SRC = ROOT / "tools" / "sources.json"

TIER = {"apa.org":20,"explainx.ai":14,"groundy.com":14,"nngroup.com":14,"vice.com":14,"new-kpop.org":14,"netpsychology.org":14,"helpfulprofessor.com":8,"gstever.sunyempirefaculty.net":8,"voxbooster.com":8,"rollingstone.com":14,"nationalgeographic.com":14,"abc.net.au":14}
LENS_KEYS = {"idol":["idol","k-pop","kpop","swift","bts","bubble","weverse"],"companion":["ai companion","replika","character.ai","chatbot","ai girlfriend"],"creator":["streamer","youtuber","influencer","tiktok","twitch"],"character":["pennywise","horror","fandom","character"],"universe":["dream","lore","gta","npc","canon"],"brand":["brand","sponsor","cameo"]}

def load(p, default):
    try: return json.loads(p.read_text(encoding="utf-8"))
    except Exception: return default

def fetch_rss(query, limit=8):
    q = urllib.parse.quote(query)
    url = f"https://news.google.com/rss/search?q={q}%20when%3A30d&hl=en-US&gl=US&ceid=US%3Aen"
    req = urllib.request.Request(url, headers={"User-Agent":"parasocialize-sweeper/1.0"})
    with urllib.request.urlopen(req, timeout=15) as r:
        xml = r.read()
    root = ET.fromstring(xml)
    out = []
    for item in root.iter("item") :
        if len(out) >= limit: break
        t = (item.findtext("title") or "").strip()
        l = (item.findtext("link") or "").strip()
        s = (item.findtext("source") or "").strip()
        out.append({"title":t,"link":l,"source":s})
    return out

def guess_lens(text):
    t = text.lower()
    best, score = None, 0
    for lens, keys in LENS_KEYS.items():
        s = sum(1 for k in keys if k in t)
        if s > score: best, score = lens, s
    return best

def main():
    no_fetch = "--no-fetch" in sys.argv
    now = datetime.datetime.now(datetime.timezone.utc)
    ledger = load(SIG, {"meta":{},"items":[]})
    radar = load(RADAR, [])
    sources = load(SRC, {})
    queries = sources.get("queries", ["parasocial relationships fandom news"])
    meta = ledger.get("meta", {})
    sweep = int(meta.get("sweep_count", 0))
    # rotate 3 queries per sweep
    rot = [queries[(sweep+i) % len(queries)] for i in range(min(3, len(queries)))]
    hits, new_sightings, candidates = [], {}, load(CAND, [])
    if not no_fetch:
        for q in rot:
            try:
                for e in fetch_rss(q):
                    hits.append((q, e))
            except Exception as ex:
                print(f"feed miss ({q}): {type(ex).__name__}")
    by_slug = {it["slug"]: it for it in ledger.get("items", [])}
    for q, e in hits:
        title = e["title"]
        dom = ""
        m = re.search(r"https?://([^/]+)", e["link"])
        if m: dom = m.group(1).lower().replace("www.","")
        lens = guess_lens(title + " " + q)
        # match existing signal by lens (boost strongest same-lens story, not all)
        cands = [it for it in by_slug.values() if it.get("lens")==lens and not it.get("classic")]
        target = max(cands, key=lambda x: x.get("resonance",0)) if cands else None
        if target and lens:
            s = target.setdefault("sightings", [])
            key = f"{dom or 'news'}-{now.date().isoformat()}-{len(s)}"
            if sum(1 for x in s if str(x).startswith(dom or 'news')) < 2:
                s.append({"at":now.isoformat(),"domain":dom,"title":title[:120],"via":q})
                target["resonance"] = min(100, float(target.get("resonance",60)) + 8)
                target["last_seen"] = now.date().isoformat()
                new_sightings[target["slug"]] = new_sightings.get(target["slug"],0)+1
        else:
            if title and not any(c.get("title")==title for c in candidates):
                candidates.append({"at":now.isoformat(),"query":q,"title":title,"link":e["link"],"lens":lens})
    # decay + states
    for it in by_slug.values():
        if it["slug"] not in new_sightings and not it.get("classic"):
            it["resonance"] = max(20, float(it.get("resonance",60)) - 3)
        r = float(it.get("resonance",60))
        try: age = (now.date() - datetime.date.fromisoformat(it.get("first_seen", now.date().isoformat()))).days
        except Exception: age = 0
        if it.get("classic"): it["state"] = "CLASSIC"
        elif age < 1 and r >= 70: it["state"] = "FLASHING"
        elif r >= 55 and age > 3: it["state"] = "LINGERING"
        elif r < 45 and age > 3: it["state"] = "FADING"
        else: it["state"] = "PRESENT"
    # order: flashing first, then resonance desc; classics pinned max 2; fading dropped from grid
    items = sorted(by_slug.values(), key=lambda x: (0 if x.get("state")=="FLASHING" else 1, -float(x.get("resonance",0))))
    classics = [x for x in items if x.get("classic")][:2]
    rest = [x for x in items if not x.get("classic") and x.get("state")!="FADING"][:4]
    order = [x["slug"] for x in items if x.get("state")=="FLASHING"][:1]
    for x in sorted(classics+rest, key=lambda v: -float(v.get("resonance",0))):
        if x["slug"] not in order: order.append(x["slug"])
    order = order[:6]
    # rebuild radar.json order + inject resonance/state (curator fields untouched)
    rmap = {str(d.get("slug")): d for d in radar} if isinstance(radar, list) else {}
    out = []
    for slug in order:
        base = rmap.get(slug, {"slug":slug})
        sig = by_slug.get(slug, {})
        base = dict(base)
        base["resonance"] = round(float(sig.get("resonance", base.get("intensity",7)*10)),1)
        base["state"] = sig.get("state","PRESENT")
        base["last_seen"] = sig.get("last_seen")
        out.append(base)
    # keep any radar entries not in ledger (safety) appended
    for d in (radar if isinstance(radar,list) else []):
        if d.get("slug") not in order: out.append(d)
    RADAR.write_text(json.dumps(out, indent=2), encoding="utf-8")
    # ticker
    def phrase(d):
        t = re.sub(r"^(the|when|living with|company) ","", d.get("title",""), flags=re.I).strip().upper()
        t = (t[:32] + "…") if len(t) > 33 else t
        if d.get("state")=="LINGERING": t += " ☆ STILL RESONATING"
        return t
    phrases = [phrase(d) for d in out[:6]]
    TICKER.write_text(json.dumps({"updated":now.isoformat(),"sweep":sweep+1,"phrases":phrases}, indent=2), encoding="utf-8")
    CAND.write_text(json.dumps(candidates[-40:], indent=2), encoding="utf-8")
    meta["last_sweep"] = now.isoformat(); meta["sweep_count"] = sweep+1
    ledger["meta"] = meta
    ledger["items"] = list(by_slug.values())
    SIG.write_text(json.dumps(ledger, indent=2), encoding="utf-8")
    print(f"sweep {sweep+1}: feeds={len(hits)} boosts={new_sightings} order={order}")

if __name__ == "__main__":
    main()
