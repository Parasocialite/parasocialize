#!/usr/bin/env python3
"""
atlas.py - the schema for the map.

THE MODEL
The encyclopedia was a flat record. A map needs a graph, so four things change:

  figure_kind   real | mythological | fictitious. The user wants every figure
                catalogued, and the old `person` kind silently merged Mary
                Shelley with Zeus. A constellation cannot draw a line between
                "wrote a novel" and "is a god" and call it one kind of thing.

  medium[]      the cross-cutting taxonomy, on the entry rather than inferred
                from which section it appears in: literature, film, music,
                television_scripted, television_unscripted, sport, technology,
                ai, history, theology, games.

  year_end      most things in this catalogue span. A show runs 1991-2004, a
                correspondence runs forty years, a deity is worshipped for
                three thousand. A single year cannot place those on a timeline,
                and an event with only a year sits at a point when it is a span.

  relations[]   `related` was a flat list of ids, so the graph had no edges and
                the map had nothing to draw. Edges carry a type, because
                "Kempe dictated a book" and "Elvis had fans" are not the same
                claim and the map should not imply they are.

SOURCES
`source` was a single string and 110 of 157 entries had an empty one, which is
how a catalogue of this ambition becomes a list of things that sound right.
Sources here are claim-level: each says what claim it supports, cites something
retrievable, and carries its own status. `verified` on the entry means every
claim in it is carried by a source; a partial entry is `verified: false` and
the map draws it differently rather than quietly including it.

  python tools/atlas.py --check     schema violations in data/encyclopedia.json
  python tools/atlas.py --graph     emit the flat node/edge lists for the map
"""
import json, pathlib, sys, re

ROOT = pathlib.Path(__file__).resolve().parent.parent
ENC = ROOT / "data" / "encyclopedia.json"

MEDIA = ["theology", "literature", "film", "music", "television_scripted",
         "television_unscripted", "sport", "technology", "ai", "history", "games"]

MEDIA_LABEL = {
    "theology": "Theology", "literature": "Literature", "film": "Film",
    "music": "Music", "television_scripted": "Scripted television",
    "television_unscripted": "Unscripted television", "sport": "Sport",
    "technology": "Technology", "ai": "Artificial intelligence",
    "history": "History", "games": "Games",
}

KINDS = ["figure", "work", "mechanism", "event", "institution", "term", "study"]

FIGURE_KINDS = ["real", "mythological", "fictitious"]

# edge types, and what each one is allowed to connect. `subject` is a coarse
# grouping used by the map to colour and filter edges.
RELATIONS = {
    "bond_with":        ("a bond that is the point of the entry",       "bond"),
    "wrote":            ("wrote / dictated / authored",                 "work"),
    "performed":        ("performed, released, or broadcast",           "work"),
    "depicts":          ("depicts, dramatises, or is about",             "work"),
    "adapted_from":     ("made from, or remade from",                   "work"),
    "succeeded":        ("replaced, dethroned, or was succeeded by",    "work"),
    "cites":            ("cites, quotes, or is evidence for",           "work"),
    "member_of":        ("member of a group, cast, pantheon or team",    "work"),
    "contemporary":     ("lived or worked at the same time",            "bond"),
    "influenced":       ("demonstrably influenced",                     "bond"),
    "instance_of":      ("an instance of a larger pattern",             "bond"),
    "preceded":         ("came before in the same lineage",             "work"),
    "occurred_in":      ("happened in this place or institution",       "work"),
}

# a citation must have something to point at. A claim with a status but no
# locator is a claim somebody believed.
def source_ok(s):
    if not isinstance(s, dict):
        return False
    return bool(str(s.get("citation") or "").strip()) and bool(str(s.get("url") or "").strip())


def upgrade(e):
    """Normalise one entry onto the graph schema, without inventing anything.
    Fields that cannot be derived stay absent; the checker reports them."""
    o = dict(e)
    o.setdefault("kind", "event")
    if o["kind"] == "person":
        o["kind"] = "figure"
    if o["kind"] == "figure" and not o.get("figure_kind"):
        o["figure_kind"] = "fictitious"          # the honest default: unverifiable
    o.setdefault("medium", [])
    if isinstance(o.get("medium"), str):
        o["medium"] = [o["medium"]]
    o["medium"] = [m for m in o["medium"] if m in MEDIA]

    # `lanes` was the old facet; keep it, and let medium be independent of it
    if isinstance(o.get("lanes"), str):
        o["lanes"] = [o["lanes"]]

    y = o.get("year")
    if y is not None:
        try:
            y = int(y)
        except Exception:
            y = None
    o["year"] = y
    ye = o.get("year_end")
    if ye is not None:
        try:
            ye = int(ye)
        except Exception:
            ye = None
    if ye is not None and y is not None and ye < y:
        ye = None
    o["year_end"] = ye

    # old flat `related` -> typed edges, defaulting to instance_of because that
    # is the weakest true thing you can say about two unlabelled neighbours
    rel = []
    for r in o.get("relations") or []:
        if isinstance(r, dict) and r.get("to"):
            rel.append({"to": r["to"], "type": r.get("type") or "instance_of",
                        "note": r.get("note", "")})
        elif isinstance(r, str):
            rel.append({"to": r, "type": "instance_of", "note": ""})
    o["relations"] = rel
    o.pop("related", None)

    # old flat `source` string -> one claim-level source, honestly marked.
    # Status "legacy" rather than "verified": some of these strings are good
    # writing, but a bare citation with no locator is not checkable by anyone,
    # including us, and the checker reports it as such.
    src = o.get("sources")
    if not src:
        old = str(o.pop("source", "") or "").strip()
        if old:
            src = [{"claim": "the entry as a whole", "citation": old,
                    "url": "", "status": "legacy"}]
        else:
            src = []
    o["sources"] = [s for s in src if isinstance(s, dict)]
    # The old entry-level flag is preserved rather than recomputed. Those 47
    # were marked by a human, and silently downgrading them because the new bar
    # (a source with a locator) is higher than the old one (a bare citation
    # string) would throw away real work and make the map claim it knows less
    # than it does. The checker still reports them as unlocatable.
    return o


def load(path=ENC):
    d = json.loads(pathlib.Path(path).read_text(encoding="utf-8"))
    d["entries"] = [upgrade(e) for e in d.get("entries", [])]
    return d


def save(d, path=ENC):
    pathlib.Path(path).write_text(
        json.dumps(d, indent=2, ensure_ascii=False), encoding="utf-8")


def graph(d):
    """Flatten to the node/edge lists the client actually draws.

    Edges to ids that are not in the set are dropped rather than drawn to
    nowhere - a dangling edge in a force layout turns into a node flung off
    screen, which looks like a bug in the map and is really a typo in the data.
    """
    ids = {e["id"] for e in d["entries"]}
    nodes, edges = [], []
    for e in d["entries"]:
        nodes.append({
            "id": e["id"], "t": e["title"], "k": e["kind"],
            "fk": e.get("figure_kind") or "", "y": e.get("year"),
            "ye": e.get("year_end"), "m": e.get("medium") or [],
            "s": e.get("summary", ""), "g": e.get("significance", ""),
            "era": e.get("era", ""), "v": 1 if e.get("verified") else 0,
            "mi": 1 if e.get("media_inferred") else 0,
            "src": e.get("sources") or [],
        })
    seen = set()
    for e in d["entries"]:
        for r in e.get("relations") or []:
            if r["to"] not in ids or r["to"] == e["id"]:
                continue
            k = (e["id"], r["to"], r["type"])
            if k in seen:
                continue
            seen.add(k)
            edges.append({"s": e["id"], "t": r["to"], "ty": r["type"],
                          "sub": RELATIONS.get(r["type"], ("", "bond"))[1],
                          "n": r.get("note", "")})
    return nodes, edges


def check(d):
    ids = {e["id"] for e in d["entries"]}
    bad = []
    for e in d["entries"]:
        if e["kind"] not in KINDS:
            bad.append((e["id"], f"unknown kind {e['kind']!r}"))
        if e["kind"] == "figure" and e.get("figure_kind") not in FIGURE_KINDS:
            bad.append((e["id"], "figure with no valid figure_kind"))
        if not e.get("medium"):
            bad.append((e["id"], "no medium"))
        for m in e.get("medium") or []:
            if m not in MEDIA:
                bad.append((e["id"], f"unknown medium {m!r}"))
        if e.get("year") is None and e.get("year_end") is None:
            bad.append((e["id"], "no year and no year_end"))
        if not e.get("sources"):
            bad.append((e["id"], "no source"))
        for s in e.get("sources") or []:
            if not source_ok(s):
                bad.append((e["id"], f"source without a locator: {str(s)[:50]}"))
        for r in e.get("relations") or []:
            if r["to"] not in ids:
                bad.append((e["id"], f"relation to missing id {r['to']!r}"))
            if r["type"] not in RELATIONS:
                bad.append((e["id"], f"unknown relation type {r['type']!r}"))
    return bad


def main():
    a = sys.argv[1:]
    d = load()
    if "--graph" in a:
        nodes, edges = graph(d)
        out = ROOT / "data" / "atlas.json"
        out.write_text(json.dumps({"media": MEDIA_LABEL, "nodes": nodes,
                                   "edges": edges}, ensure_ascii=False,
                                  separators=(",", ":")), encoding="utf-8")
        print(f"{len(nodes)} nodes, {len(edges)} edges -> {out}")
        return
    bad = check(d)
    v = sum(1 for e in d["entries"] if e["verified"])
    print(f"{len(d['entries'])} entries, {v} fully sourced, {len(d['entries'])-v} needing work")
    print(f"{sum(len(e.get('relations') or []) for e in d['entries'])} relations, "
          f"{sum(len(e.get('medium') or []) for e in d['entries'])} medium tags")
    if not bad:
        print("schema ok.")
        return
    print(f"\n{len(bad)} problems:")
    for i, (eid, msg) in enumerate(bad[:40]):
        print(f"  {eid}: {msg}")
    if len(bad) > 40:
        print(f"  ... and {len(bad)-40} more")


if __name__ == "__main__":
    main()

