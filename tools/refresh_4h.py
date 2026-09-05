"""4-hour resonance sweep. No dependencies, network-failure safe.
Usage: python tools/refresh_4h.py [--no-fetch]
AUTOPILOT: finds stories, boosts ledger, AUTO-PUBLISHES up to 2 fresh cards
per sweep straight to radar.json (marked take-pending). No human required.
Curator md files are never deleted; auto cards live in the ledger + radar.json.
"""
import json, pathlib, datetime, re, sys, urllib.request, urllib.parse, xml.etree.ElementTree as ET
import json, pathlib, datetime, re, sys, urllib.request, urllib.parse, xml.etree.ElementTree as ET

ROOT = pathlib.Path(__file__).resolve().parents[1]
SIG = ROOT / "data" / "signals.json"
RADAR = ROOT / "radar.json"
TICKER = ROOT / "data" / "ticker.json"
CAND = ROOT / "data" / "candidates.json"
SRC = ROOT / "tools" / "sources.json"

TIER = {"apa.org":20,"explainx.ai":14,"groundy.com":14,"nngroup.com":14,"vice.com":14,"new-kpop.org":14,"netpsychology.org":14,"helpfulprofessor.com":8,"gstever.sunyempirefaculty.net":8,"voxbooster.com":8,"rollingstone.com":14,"nationalgeographic.com":14,"abc.net.au":14}
LENS_KEYS = {"idol":["idol","k-pop","kpop","swift","bts","army","bubble","weverse","celebrity","stan","actor","singer","concert","tour","stans"],"companion":["ai companion","replika","character.ai","chatbot","ai girlfriend","ai boyfriend"],"creator":["streamer","youtuber","influencer","tiktok","twitch","podcast","creator","gamer"],"character":["pennywise","horror","fandom","character","movie","show","series","episode","season"],"universe":["dream","lore","gta","npc","canon","author","novel","book","writer","memoir","fiction"],"brand":["brand","sponsor","cameo","merch","subscription"]}

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
        src_el = item.find("source")
        s = (src_el.text or "").strip() if src_el is not None else ""
        su = (src_el.get("url") or "").strip() if src_el is not None else ""
        out.append({"title":t,"link":l,"source":s,"source_url":su})
    return out

def guess_lens(text):
    t = text.lower()
    best, score = None, 0
    for lens, keys in LENS_KEYS.items():
        s = sum(1 for k in keys if k in t)
        if s > score: best, score = lens, s
    return best

GRAD = {"idol":"linear-gradient(135deg,#101a3a,#0a0714)","character":"linear-gradient(135deg,#4a1420,#160409)","creator":"linear-gradient(135deg,#30103a,#120414)","companion":"linear-gradient(135deg,#0e3038,#041214)","universe":"linear-gradient(135deg,#22242a,#0c0d10)","brand":"linear-gradient(135deg,#3a2410,#140a04)"}
EMOJI = {"idol":"♆","character":"🎈","creator":"▶","companion":"♥","universe":"∞","brand":"⬣"}

def clean_title(t):
    t = (t or "").strip()
    t = t.replace("“","\"").replace("”","\"").replace("‘","'").replace("’","'").replace("–","-").replace("—","-")
    t = re.sub(r"[\x00-\x08\x0b\x0c\x0e-\x1f�]", "", t)
    if " - " in t:
        head, tail = t.rsplit(" - ", 1)
        if len(tail) < 40 and head: return head.strip()
    return t

def slugify(t):
    words = re.sub(r"[^a-z0-9 ]", "", t.lower()).split()[:6]
    return "-".join(words) or "story"

def overlap(a, b):
    wa, wb = set(a.lower().split()), set(b.lower().split())
    if not wa or not wb: return 0
    return len(wa & wb) / max(len(wa), len(wb))

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
                candidates.append({"at":now.isoformat(),"query":q,"title":title,"link":e["link"],"lens":lens,"source":e.get("source",""),"source_url":e.get("source_url","")})
    # AUTOPILOT: promote best fresh finds straight to the grid (max 2/sweep,
    # max 3 auto-live). Quality bar: cleaned title, guessed lens, deduped.
    known_titles = [it.get("title","") for it in by_slug.values()] + [d.get("title","") for d in (radar if isinstance(radar,list) else [])]
    auto_live = sum(1 for it in by_slug.values() if it.get("auto") and it.get("state") != "FADING")
    promoted = []
    if not no_fetch:
        scored = []
        for c in candidates:
            t = clean_title(c.get("title",""))
            if len(t) < 25 or len(t) > 140: continue
            if any(overlap(t, k) > 0.55 for k in known_titles): continue
            dom = ""
            m = re.search(r"https?://([^/]+)", c.get("link",""))
            if m: dom = m.group(1).lower().replace("www.","")
            if dom.endswith("youtube.com") or dom.endswith("tiktok.com"): continue
            lens = c.get("lens") or guess_lens(t + " " + c.get("query",""))
            if not lens: continue
            trusted = any(dom.endswith(k) for k in TIER) if dom else False
            scored.append((0 if trusted else 1, c, t, dom, lens))
        scored.sort(key=lambda x: x[0])
        for _, c, t, dom, lens in scored:
            if len(promoted) >= 2 or auto_live >= 3: break
            slug = slugify(t)
            if slug in by_slug: continue
            base = 8.0 if (dom and any(dom.endswith(k) for k in TIER)) else 7.0
            outlet = (c.get("source_url") or c.get("link") or "").strip()
            src_name = (c.get("source") or "").strip() or (re.search(r"https?://([^/]+)", outlet).group(1) if re.search(r"https?://([^/]+)", outlet) else "Source")
            src_name = re.sub(r"^www\.", "", src_name)
            entry = {"slug":slug,"lens":lens,"base_intensity":base,
                "resonance":round(base*10 - 8, 1),"first_seen":now.date().isoformat(),
                "last_seen":now.date().isoformat(),"sightings":[{"at":now.isoformat(),"domain":dom or "news","title":t[:120],"via":"auto"}],
                "state":"FLASHING","classic":False,"auto":True,
                "title":t,"dek":f"Fresh via {src_name} - take lands Friday.",
                "type":"non-fiction","lenses":[lens],"tags":["ai"] if lens=="companion" else [],
                "intensity":base,"read_minutes":3,"emoji":EMOJI.get(lens,"●"),"gradient":GRAD.get(lens,"#222"),
                "link":"#signal","link_label":"Take pending",
                "source_url":outlet,"source_name":src_name or "Source"}
            by_slug[slug] = entry
            known_titles.append(t)
            promoted.append(slug)
            auto_live += 1
        # promoted leave the pending queue
        candidates = [c for c in candidates if slugify(clean_title(c.get("title",""))) not in set(promoted)]
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
    # order: flashing first, then resonance desc; classics pinned max 2; fading dropped; auto max 2
    items = sorted(by_slug.values(), key=lambda x: (0 if x.get("state")=="FLASHING" else 1, -float(x.get("resonance",0))))
    classics = [x for x in items if x.get("classic")][:2]
    rest = [x for x in items if not x.get("classic") and x.get("state")!="FADING"]
    rest_auto = [x for x in rest if x.get("auto")][:2]
    rest = [x for x in rest if not x.get("auto")][:4] + rest_auto
    order = [x["slug"] for x in items if x.get("state")=="FLASHING"][:1]
    for x in sorted(classics+rest, key=lambda v: -float(v.get("resonance",0))):
        if x["slug"] not in order: order.append(x["slug"])
    order = order[:6]
    # rebuild radar.json order + inject resonance/state (curator md fields win when present;
    # auto cards carry their own card fields from the ledger)
    rmap = {str(d.get("slug")): d for d in radar} if isinstance(radar, list) else {}
    out = []
    for slug in order:
        sig = by_slug.get(slug, {})
        if slug in rmap and not sig.get("auto"):
            base = dict(rmap[slug])
        else:
            base = {"slug":slug,"title":sig.get("title",slug),"dek":sig.get("dek",""),
                "type":sig.get("type","non-fiction"),"lenses":sig.get("lenses",[sig.get("lens","universe")] if sig.get("lens") else []),
                "tags":sig.get("tags",[]),"intensity":sig.get("intensity",7.0),"read_minutes":sig.get("read_minutes",3),
                "emoji":sig.get("emoji","●"),"gradient":sig.get("gradient","#222"),
                "link":sig.get("link","#signal"),"link_label":sig.get("link_label","Take pending"),
                "source_url":sig.get("source_url",""),"source_name":sig.get("source_name","Source")}
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
    print(f"sweep {sweep+1}: feeds={len(hits)} boosts={new_sightings} promoted={promoted} order={order}")

if __name__ == "__main__":
    main()
