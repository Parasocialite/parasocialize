#!/usr/bin/env python3
"""verify_timeline.py - hold the master timeline to its own schema.

The timeline is the one page on this site that makes a claim about *when*
something happened, across seventy thousand years. A typo in a sort year moves
an entry to the wrong century and no link check can see it; a missing phase
makes an entry fall out of the master list; a citation with no URL is the
`retrievable` defect this repository has now met four times.

So the checks here are about the promises the fields make:

  * every entry has every required field, and the types are the types the
    builder renders;
  * domain and era are members of the lists the page filters on, and phase is
    one of the seven the page groups by;
  * sort_year agrees with the year string and is ordered inside its phase;
  * the user's seed list is still present - a master list that quietly drops a
    milestone is the failure this check exists to prevent;
  * every citation has a locator if it claims to be openable, and no citation
    is a note to self;
  * ids are unique, tags are non-empty, and no tag is a sentence;
  * the rendered page carries a card and a panel for every entry, and the
    corpus page links back.

It cannot check that a date is true. That is what the citations are for, and
what `--check-urls` is for: a separate, explicit network pass, never part of
the build.
"""
from __future__ import annotations

import json
import pathlib
import re
import sys
import urllib.request

ROOT = pathlib.Path(__file__).resolve().parent.parent
DATA = ROOT / "data" / "timeline.json"

DOMAINS = [
    "Myth & Legend",
    "Literature & Print",
    "Broadcast & Film",
    "Politics & News",
    "Music & Fan Culture",
    "Digital & Synthetic",
]
ERAS = [
    "Pre-Modern",
    "Early Mass Media",
    "The Broadcast Age",
    "Digital & Algorithmic",
    "Synthetic Era",
]
PHASE_NAMES = {
    1: "Antiquity, Ancient Ritual & Sacred Proxies",
    2: "Literature, Early Mass Print & Stage Magic",
    3: "Golden Age Radio, Early Cinema & Propaganda",
    4: "Modern Media, Psychoanalysis & Pop Idols",
    5: "Web 1.0, Digital Fandom & Creator Economies",
    6: "Post-Human, Algorithmic & Synthetic Frontiers",
    7: "Speculative Futures",
}
REQUIRED = [
    "id", "year", "sort_year", "title", "phase", "domain", "era", "summary",
    "parasocial_analysis", "primary_source_or_artifact", "tags", "citations",
]
STATUSES = {"retrievable", "verified", "unverified"}
PLACEHOLDERS = re.compile(r"\b(verify|todo|tbd|fixme|xxx|the entry as a whole)\b", re.I)
ID_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
# Positive years only; BCE is handled by comparing the absolute sort_year.
# A hyphen in "1830s-1850s" is a range separator, not a minus sign.
YEAR_RE = re.compile(r"(?<!\d)(\d{1,6})(?!\d)")

# The user's basic list, mapped to this file's ids. Every one must still be
# here. Growth is expected; disappearance is a defect.
CORE_IDS = {
    "neanderthal-burial", "paleolithic-figures", "narcissus-echo",
    "homeric-recitation", "roman-imagines", "the-priest", "the-icon",
    "canterbury-tales", "margery-kempe", "our-lady-of-guadalupe",
    "don-quixote", "pamela", "werther", "dickens-serial", "dickens-readings",
    "miss-havisham", "sarah-bernhardt", "yellow-kid", "pearl-white",
    "betty-crocker", "rin-tin-tin", "aimee-semple-mcpherson", "babe-ruth",
    "soap-opera", "fireside-chats", "war-of-the-worlds", "superman-comic",
    "sinatra-bobby-soxers", "murrow", "horton-wohl", "jfk-nixon-debate",
    "beatlemania", "elvis-death", "hinckley-foster", "rebecca-schaeffer",
    "diana-death", "truman-show", "eminem-stan", "facebook", "youtube-vlog",
    "kuwtk", "twitch-donations", "tiktok-fyp", "character-ai",
    "akhenaten-aten", "asclepius-dream-cure", "imitation-of-christ",
    "ikiryo-possession", "fox-sisters-spiritualism", "sherlock-final-problem",
    "lord-haw-haw", "candid-camera", "quiz-show-scandals",
    "manson-helter-skelter", "tamagotchi", "blair-witch", "her-film",
    "animal-crossing-new-horizons", "openai-voice-mode",
    "ka-statues", "thespis", "lucian-alexander", "john-dee-enochian",
    "clarissa-harlowe", "peppers-ghost", "jack-the-ripper",
    "mona-lisa-theft", "goldbergs", "edward-viii-abdication",
    "rear-window", "eliza", "rocky-horror", "calling-all-cars",
    "kyoko-date", "jennicam", "hatsune-miku", "neuro-sama",
    "synthetic-mourning",
}


def fail(errors, msg):
    errors.append(msg)


def main() -> int:
    if not DATA.exists():
        print(f"MISSING {DATA}")
        return 1
    try:
        doc = json.loads(DATA.read_text(encoding="utf-8"))
    except ValueError as exc:
        print(f"INVALID JSON: {exc}")
        return 1

    errors: list[str] = []
    notes: list[str] = []

    for key in ("_note", "phases", "domains", "eras", "entries"):
        if key not in doc:
            fail(errors, f"top-level key missing: {key}")
    if errors:
        print("\n".join(errors))
        return 1

    if doc["domains"] != DOMAINS:
        fail(errors, "domains list is not the six the page filters on")
    if doc["eras"] != ERAS:
        fail(errors, "eras list is not the five the schema defines")

    phases = doc["phases"]
    if not isinstance(phases, list) or len(phases) != 7:
        fail(errors, "phases is not the seven-part list the page groups by")
    else:
        seen_phases = set()
        for p in phases:
            for key in ("id", "name", "range", "note"):
                if key not in p:
                    fail(errors, f"phase missing {key}: {p!r}")
            if p.get("id") not in PHASE_NAMES:
                fail(errors, f"unknown phase id: {p.get('id')!r}")
            elif p.get("name") != PHASE_NAMES[p["id"]]:
                fail(errors, f"phase {p['id']} name is not the one the page expects")
            seen_phases.add(p.get("id"))
        if seen_phases != set(PHASE_NAMES):
            fail(errors, f"phase ids are {sorted(seen_phases)}, not 1-7")

    entries = doc["entries"]
    if not isinstance(entries, list) or not entries:
        fail(errors, "entries is not a non-empty list")
        print("\n".join(errors))
        return 1
    if len(entries) < len(CORE_IDS):
        fail(errors, f"{len(entries)} entries cannot hold the {len(CORE_IDS)} "
                     f"seed milestones")

    seen_ids: set[str] = set()
    seen_titles: set[str] = set()
    last_by_phase: dict[int, int] = {}
    phase_counts: dict[int, int] = {}
    for n, e in enumerate(entries, 1):
        where = f"entry {n} ({e.get('id', 'no id')})"
        for key in REQUIRED:
            if key not in e:
                fail(errors, f"{where}: missing {key}")
        if any(x.startswith(where) for x in errors):
            continue

        eid = str(e["id"])
        if not ID_RE.match(eid):
            fail(errors, f"{where}: id is not a lowercase slug")
        if eid in seen_ids:
            fail(errors, f"{where}: duplicate id")
        seen_ids.add(eid)

        title = str(e["title"]).strip()
        if len(title) < 8:
            fail(errors, f"{where}: title is too short")
        if title.lower() in seen_titles:
            fail(errors, f"{where}: duplicate title")
        seen_titles.add(title.lower())

        if e["domain"] not in DOMAINS:
            fail(errors, f"{where}: domain {e['domain']!r} is not in the list")
        if e["era"] not in ERAS:
            fail(errors, f"{where}: era {e['era']!r} is not in the list")
        if e["phase"] not in PHASE_NAMES:
            fail(errors, f"{where}: phase {e['phase']!r} is not 1-7")
            continue
        phase_counts[e["phase"]] = phase_counts.get(e["phase"], 0) + 1
        prov = str(e.get("provenance") or "sourced")
        if prov not in ("sourced", "pdf"):
            fail(errors, f"{where}: provenance {prov!r} is not sourced or pdf")
        if e["phase"] == 7 and not e.get("speculative"):
            fail(errors, f"{where}: phase 7 entry is not marked speculative")
        if e["phase"] != 7 and e.get("speculative"):
            fail(errors, f"{where}: speculative entry is not in phase 7")

        try:
            sort = int(e["sort_year"])
        except (TypeError, ValueError):
            fail(errors, f"{where}: sort_year is not an integer")
            sort = None
        if sort is not None:
            prev = last_by_phase.get(e["phase"])
            if prev is not None and sort < prev:
                fail(errors, f"{where}: sort_year {sort} runs backwards "
                             f"after {prev} inside phase {e['phase']}")
            last_by_phase[e["phase"]] = sort
            years = [int(y) for y in YEAR_RE.findall(str(e["year"]).replace(",", ""))]
            if not years:
                fail(errors, f"{where}: year {e['year']!r} contains no year")
            else:
                probe = abs(sort)
                if probe not in years and not (
                    len(years) > 1 and min(years) <= probe <= max(years)
                ):
                    fail(errors, f"{where}: sort_year {sort} is not in year "
                                 f"{e['year']!r}")

        for field, low in (("summary", 80),
                           ("parasocial_analysis", 250 if prov == "pdf" else 300)):
            text = str(e[field]).strip()
            if len(text) < low:
                fail(errors, f"{where}: {field} is {len(text)} chars, "
                             f"under the {low} minimum")
        if "date_note" in e and len(str(e["date_note"]).strip()) < 20:
            fail(errors, f"{where}: date_note is too short to explain anything")

        tags = e["tags"]
        if not isinstance(tags, list) or not tags:
            fail(errors, f"{where}: tags is not a non-empty list")
        else:
            if len(set(tags)) != len(tags):
                fail(errors, f"{where}: duplicate tag")
            for t in tags:
                if not isinstance(t, str) or not re.match(r"^[a-z0-9]+(?:-[a-z0-9]+)*$", t):
                    fail(errors, f"{where}: tag {t!r} is not a lowercase slug")

        cits = e["citations"]
        if not isinstance(cits, list) or not cits:
            fail(errors, f"{where}: citations is not a non-empty list")
        else:
            for c in cits:
                for key in ("citation", "url", "status", "note"):
                    if key not in c:
                        fail(errors, f"{where}: citation missing {key}")
                status = str(c.get("status", ""))
                if status not in STATUSES:
                    fail(errors, f"{where}: citation status {status!r} is not "
                                 f"one of {sorted(STATUSES)}")
                if status == "retrievable" and not str(c.get("url", "")).startswith("http"):
                    fail(errors, f"{where}: retrievable citation has no URL")
                if not str(c.get("url", "")).startswith("https://"):
                    fail(errors, f"{where}: citation URL is not https")
                for key in ("citation", "note"):
                    if PLACEHOLDERS.search(str(c.get(key, ""))):
                        fail(errors, f"{where}: citation {key} contains a "
                                     f"note-to-self")
                if len(str(c.get("citation", "")).strip()) < 8:
                    fail(errors, f"{where}: citation string is too short")
                if len(str(c.get("note", "")).strip()) < 8:
                    fail(errors, f"{where}: citation note is too short")

    missing_core = sorted(CORE_IDS - seen_ids)
    if missing_core:
        fail(errors, "seed milestones missing from the master list: "
                     + ", ".join(missing_core))
    for pid in PHASE_NAMES:
        if not phase_counts.get(pid):
            fail(errors, f"phase {pid} has no entries")
    if not errors and set(phase_counts) != set(PHASE_NAMES):
        notes.append("phase counts " + ", ".join(
            f"{k}:{phase_counts.get(k, 0)}" for k in sorted(PHASE_NAMES)))

    # The data can be perfect while the page renders nothing. The source tier
    # runs after build_cards, so check the artefact as well as the file it was
    # built from: every card must have a panel, and every panel must have a
    # card. A slide-over whose :target id is missing is a link to nowhere that
    # no link checker treats as broken, because the fragment is on the page.
    master = [e for e in entries if not e.get("speculative")]
    future = [e for e in entries if e.get("speculative")]
    page = ROOT / "timeline" / "index.html"
    fpage = ROOT / "timeline" / "future" / "index.html"
    corpus = ROOT / "timeline" / "corpus" / "index.html"
    if page.exists() and fpage.exists():
        mhtml = page.read_text(encoding="utf-8")
        fhtml = fpage.read_text(encoding="utf-8")
        n_cards = mhtml.count('class="tlc-card"')
        n_panels = mhtml.count('class="tlc-panel"')
        if n_cards != len(master):
            fail(errors, f"rendered master cards: {n_cards} for {len(master)} entries")
        if n_panels != len(master):
            fail(errors, f"rendered master panels: {n_panels} for {len(master)} entries")
        f_cards = fhtml.count('class="tlc-card"')
        f_panels = fhtml.count('class="tlc-panel"')
        if f_cards != len(future):
            fail(errors, f"rendered future cards: {f_cards} for {len(future)} entries")
        if f_panels != len(future):
            fail(errors, f"rendered future panels: {f_panels} for {len(future)} entries")
        for e in master:
            if f'id="tl-{e["id"]}"' not in mhtml:
                fail(errors, f"panel id missing from the master page: tl-{e['id']}")
            if f'href="#tl-{e["id"]}"' not in mhtml:
                fail(errors, f"card link missing from the master page: tl-{e['id']}")
        for e in future:
            if f'id="tl-{e["id"]}"' not in fhtml:
                fail(errors, f"panel id missing from the future page: tl-{e['id']}")
            if f'href="#tl-{e["id"]}"' not in fhtml:
                fail(errors, f"card link missing from the future page: tl-{e['id']}")
        if not corpus.exists():
            fail(errors, "the corpus page is missing at timeline/corpus/")
        elif 'href="../index.html"' not in corpus.read_text(encoding="utf-8"):
            fail(errors, "the corpus page does not link back to the master page")
    else:
        notes.append("timeline pages not built; artefact checks skipped")

    if errors:
        print(f"timeline: {len(errors)} problem(s)")
        for x in errors:
            print("  " + x)
        return 1

    print(f"timeline: {len(entries)} entries, "
          f"{len(seen_ids)} ids, "
          f"{sum(len(e['citations']) for e in entries)} citation records")
    print(f"  phases:  {', '.join(f'{k}:{phase_counts.get(k, 0)}' for k in sorted(PHASE_NAMES))}")
    print(f"  domains: {len(set(e['domain'] for e in entries))} of {len(DOMAINS)}")
    print(f"  eras:    {len(set(e['era'] for e in entries))} of {len(ERAS)}")
    print(f"  tags:    {len(set(t for e in entries for t in e['tags']))} distinct")
    print(f"  seed:    {len(CORE_IDS)} of {len(CORE_IDS)} present")
    for note in notes:
        print("  note: " + note)

    if "--check-urls" in sys.argv:
        for e in entries:
            for c in e["citations"]:
                url = c["url"]
                try:
                    req = urllib.request.Request(
                        url, headers={"User-Agent": "ParasocializeAudit/1.0"})
                    with urllib.request.urlopen(req, timeout=25) as r:
                        print(f"  {r.status} {e['id']}: {url}")
                except Exception as exc:  # noqa: BLE001 - report the real failure
                    print(f"  ERR {e['id']}: {type(exc).__name__} {url}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
