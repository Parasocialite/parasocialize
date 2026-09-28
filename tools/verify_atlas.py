#!/usr/bin/env python3
"""
verify_atlas.py - the citation backlog, ranked by how much it matters.

WHY NOT A URL CHECKER
This was going to be a link checker. It cannot be, yet. Across 176 entries
there are 62 sources and exactly ONE of them has a locator; 61 are a bare
citation string with a status. A tool that fetches URLs has one URL to fetch.

And the tempting version - one that searches for a source per entry and writes
it in - is the single most dangerous thing in this repository. Auto-finding a
locator for a historical claim does not check the claim, it launders a guess
with a URL attached. A citation whose locator was machine-found and whose claim
was machine-recalled is a fabrication with better typography, and this site
argues against precisely that. So this tool will not invent a source. It does
not fill in a URL, and it never writes `verified: true`.

WHAT IT ACTUALLY DOES
    --report   the coverage gap, ranked so the fix order is obvious
    --check    fetch every locator that exists and record whether it resolves

THE RANKING IS THE POINT
The graph filled in last session changed what "unsourced" means. Grief has
nineteen edges, so a reader arrives at it from nineteen directions and the
citation status on that one entry is load-bearing nineteen times over. A leaf
with one edge is not. Fixing entries in author order fixes them in an order
that has nothing to do with whether anybody will read them. So the backlog is
ranked by degree: hubs first, leaves last.

THE TWO AXES ARE NOT THE SAME THING
    verified     a human stood behind the claim. Only a human sets this.
    retrieved    the locator resolves. This tool sets this, and it is a
                 statement about a URL and not about the world.

An entry with `retrieved: true` and `verified: false` has a working link to a
claim nobody has checked. That is a real and common state, it is not the same as
sourced, and keeping the two fields apart is the point.

  python tools/verify_atlas.py --report
  python tools/verify_atlas.py --check
  python tools/verify_atlas.py --report --kind figure --media theology
"""
import json, pathlib, sys, argparse, datetime, ssl, urllib.request, urllib.error, time

ROOT = pathlib.Path(__file__).resolve().parent.parent
ENC = ROOT / "data" / "encyclopedia.json"
UA = ("Parasocialize/2.0 (https://www.parasocialize.com; "
      "counter@parasocialize.com) link checker")

OK = (200, 203, 204)


def degree_map(d):
    deg = {e["id"]: 0 for e in d["entries"]}
    for e in d["entries"]:
        for r in e.get("relations") or []:
            if r["to"] in deg:
                deg[e["id"]] += 1
                deg[r["to"]] += 1
    return deg


def gap(e):
    """What exactly is missing from this entry's sourcing."""
    srcs = e.get("sources") or []
    if not srcs:
        return "no source at all"
    no_url = [s for s in srcs if not str(s.get("url") or "").strip()]
    unverified = [s for s in srcs
                  if s.get("status") not in ("verified", "retrievable")]
    bits = []
    if no_url:
        bits.append(f"{len(no_url)} source(s) with no locator")
    if unverified:
        bits.append(f"{len(unverified)} unchecked claim(s)")
    if e.get("verified"):
        bits.append("entry already stands behind a human")
    return "; ".join(bits) or "complete"


def report(d, kind=None, media=None, top=None):
    deg = degree_map(d)
    rows = []
    for e in d["entries"]:
        if kind and e.get("kind") != kind:
            continue
        if media and media not in (e.get("medium") or []):
            continue
        if e.get("verified"):
            continue
        rows.append((deg.get(e["id"], 0), e))
    rows.sort(key=lambda kv: (-kv[0], str(kv[1].get("year") or 0)))
    n = len(rows)
    total_edges = sum(deg.values()) // 2
    touched = sum(1 for dd, _ in rows if dd)
    print(f"{n} of {len(d['entries'])} entries have not been stood behind by a human")
    if kind:
        print(f"  filtered to kind={kind}" + (f" medium={media}" if media else ""))
    print(f"  {touched} of them are reached by an edge, so {touched} of {total_edges} "
          f"edges land on something unchecked")
    if top:
        rows = rows[:top]
    print()
    print(f"  {'deg':>4}  {'id':<34} {'kind':<11} what is missing")
    for dd, e in rows:
        print(f"  {dd:>4}  {e['id']:<34} {e.get('kind',''):<11} {gap(e)}")
    return rows


def check(d, timeout=15, pause=0.2):
    """Fetch every locator that exists and record whether it resolves.

    This is a statement about URLs. It is not a statement about whether the
    claims are true and it never writes `verified`."""
    urls = {}
    for e in d["entries"]:
        for s in e.get("sources") or []:
            u = str(s.get("url") or "").strip()
            if u:
                urls.setdefault(u, []).append((e["id"], s))
    if not urls:
        print("no locators to check - 61 of 62 sources have no url yet")
        return d
    print(f"checking {len(urls)} distinct locators")
    today = datetime.date.today().isoformat()
    res = {}
    for u, uses in urls.items():
        res[u] = probe(u, timeout)
        print(f"  {res[u]['code'] or 'ERR':>4}  {u[:74]}")
        time.sleep(pause)

    n_promote = 0
    for u, uses in urls.items():
        r = res[u]
        for eid, s in uses:
            s["retrieved"] = {"at": today, "code": r["code"],
                              "final": r["final"], "ok": r["ok"]}
    # recommend, do not decide
    for e in d["entries"]:
        srcs = e.get("sources") or []
        if not srcs or e.get("verified"):
            continue
        if all(s.get("retrieved", {}).get("ok") for s in srcs):
            n_promote += 1
    print()
    print(f"{sum(1 for r in res.values() if r['ok'])}/{len(res)} locators resolve")
    print(f"{n_promote} entries now have every locator resolving and are waiting "
          f"for a human to read them")
    if n_promote:
        print("  they are NOT verified. read them, then set verified by hand.")
    return d


def probe(url, timeout=15):
    req = urllib.request.Request(url, method="GET", headers={
        "User-Agent": UA, "Accept": "*/*", "Range": "bytes=0-2048"})
    try:
        with urllib.request.urlopen(req, timeout=timeout,
                                    context=ssl.create_default_context()) as r:
            r.read(512)
            return {"code": r.status, "final": r.geturl(), "ok": r.status in OK}
    except urllib.error.HTTPError as e:
        return {"code": e.code, "final": url, "ok": e.code in OK}
    except Exception as e:
        return {"code": None, "final": url, "ok": False,
                "err": str(e)[:70]}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--report", action="store_true")
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--kind")
    ap.add_argument("--media")
    ap.add_argument("--top", type=int)
    ap.add_argument("--write", action="store_true",
                    help="persist the retrieved: block to data/encyclopedia.json")
    a = ap.parse_args()
    d = json.loads(ENC.read_text(encoding="utf-8"))
    if not (a.report or a.check):
        a.report = True
    if a.report:
        report(d, a.kind, a.media, a.top)
    if a.check:
        d = check(d)
        if a.write:
            ENC.write_text(json.dumps(d, indent=2, ensure_ascii=False),
                           encoding="utf-8")
            print("written")
    if not a.check:
        print()
        print("next: python tools/verify_atlas.py --check   "
              "(1 locator today, so --report is the useful one)")


if __name__ == "__main__":
    main()
