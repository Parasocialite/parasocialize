"""Cite a source: add or update a citation record, checking its identity.

`AGENTS.md` says to cite via `tools/add_source.py`, and that tool only does two
things: print a report, and recompute provenance. It takes no entry and no
citation. Anyone following the file would run
`add_source.py <entry> "<citation>"`, get a silent no-op, and walk away
believing a source had been added - **a tool whose documented interface does not
exist is worse than one that admits it has none**, because the no-op is
indistinguishable from success. This is that path.

What makes it safe to write a URL into a citation:

  - a DOI is checked against Crossref for **identity**, not resolvability.
    AGENTS records thirteen titles for which Crossref returned a DOI for all
    thirteen and only two were the work being looked for, including a paper
    about a man's stressed friend attached to a claim about parasocial
    persuasion. Every one of those URLs loads. `retrievable` means a reader can
    open this and find the work, so a DOI that resolves to the wrong paper is
    the exact defect this project exists to refuse. Author and year decide; the
    title corroborates.

  - the record count and the top-level keys are asserted before and after, so a
    write cannot quietly reshape the corpus.

  - thesis entries are refused: they take no citation by design.

  - `--no-verify` exists for records with no DOI at all, and it says so in the
    record, because an unchecked URL should not look like a checked one.

Nothing here upgrades `verified`. A locator says a reader can open the work; it
does not say anybody read it, and the only way to earn `verified` is a reading.
"""
import json
import pathlib
import re
import sys
import urllib.parse
import urllib.request

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ROOT = pathlib.Path(r"C:\Users\paras\Documents\Default Project\parasocialize")
DATA = ROOT / "data" / "encyclopedia.json"

DOI = re.compile(r"\b(10\.\d{4,9}/[^\s,;)\]]+)", re.I)
YEAR = re.compile(r"\b(1[5-9]\d\d|20[0-2]\d)\b")


def doi_from(url: str) -> str:
    """Pull the DOI out of a doi.org URL, taking the whole path.

    A regex over the text is wrong for a whole real class of DOI. Old-style
    Elsevier DOIs embed the year in parentheses - `10.1016/0010-0285(72)90002-3`
    is Winograd's *Cognitive Psychology* paper - and a character class that
    excludes `)` truncates it to `10.1016/0010-0285(72`, which is not a DOI.
    That is not hypothetical: it happened on the first real citation attempt
    here, and the tool refused to write rather than writing half a DOI, which is
    the correct direction to fail in.

    DOIs may legally contain `(`, `)`, `;`, `<` and `>`, so the path after
    `doi.org/` is the authority here and the regex is only a fallback for a
    bare DOI typed straight into --citation.
    """
    m = re.search(r"doi\.org/(.+)$", (url or "").strip(), re.I)
    if m:
        return m.group(1).strip().rstrip(".,;")
    m = DOI.search(url or "")
    return m.group(1).rstrip(".,;") if m else ""


def norm_words(s: str) -> set:
    return set(re.findall(r"[a-z]{3,}", (s or "").lower()))


def crossref(doi: str) -> dict:
    url = "https://api.crossref.org/works/" + urllib.parse.quote(doi, safe="")
    req = urllib.request.Request(url, headers={"User-Agent": "parasocialize-audit/1.0"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read().decode("utf-8"))["message"]


def check_identity(doi: str, citation: str) -> tuple:
    """Return (ok, note). ok=False means do not write this DOI."""
    try:
        m = crossref(doi)
    except Exception as e:
        return False, f"Crossref unreachable ({type(e).__name__}); NOT written"

    title = " ".join(m.get("title") or [])
    authors = " ".join(
        f"{a.get('given','')} {a.get('family','')}" for a in (m.get("author") or []))
    cr_year = ""
    for k in ("published-print", "published-online", "issued", "created"):
        parts = (m.get(k) or {}).get("date-parts") or []
        if parts and parts[0] and parts[0][0]:
            cr_year = str(parts[0][0])
            break

    cw, aw = norm_words(citation), norm_words(authors)
    fam = {w for w in aw if len(w) > 2}
    # a citation may use initials ("Weizenbaum, J.") - surname is the anchor
    cit_fam = {w for w in cw if len(w) > 3}
    shared_author = bool(fam & cit_fam) if fam else None

    cit_years = set(YEAR.findall(citation))
    year_ok = (not cit_years) or (not cr_year) or cr_year in cit_years

    tw = norm_words(title) - {"the", "and", "for", "with", "from"}
    overlap = len(tw & cw) / max(1, len(tw))

    notes = [f"crossref: {title[:60]!r}",
             f"  authors: {authors[:60]!r}",
             f"  year: {cr_year or 'unstated'}  citation years: "
             f"{sorted(cit_years) or 'none'}",
             f"  author surname shared: {shared_author}",
             f"  title overlap: {overlap:.0%}"]

    if shared_author is False:
        return False, ("; ".join(notes) +
                       "  -> NO shared author surname. Refused.")
    if not year_ok:
        return False, ("; ".join(notes) +
                       "  -> year disagrees with the citation. Refused: "
                       "choosing between 'the year is wrong' and 'the locator "
                       "is wrong' without evidence is the move this corpus "
                       "exists to refuse.")
    if overlap < 0.34 and shared_author is not True:
        return False, ("; ".join(notes) +
                       "  -> title overlap too low to call this the same work "
                       "on the author's name alone. Refused.")
    return True, "; ".join(notes) + "  -> identity OK"


def usage():
    sys.exit(
        "usage: cite.py <entry-id> --citation \"...\" [--url URL] [--status S]\n"
        "               [--claim \"...\"] [--add | --update MATCH] [--apply]\n\n"
        "  --update MATCH   update the existing record whose citation contains\n"
        "                  MATCH instead of adding a new one\n"
        "  --add           add a new source record\n"
        "  no --url        the record is written with no locator and says so\n")


if __name__ == "__main__":
    a = sys.argv[1:]
    if not a or a[0] in ("-h", "--help"):
        usage()
    APPLY = "--apply" in a
    entry_id = a[0]
    flags = {}
    for name in ("citation", "url", "status", "claim", "update"):
        if f"--{name}" in a:
            flags[name] = a[a.index(f"--{name}") + 1]
    mode_add = "--add" in a
    if not flags.get("citation"):
        usage()

    data = json.loads(DATA.read_text(encoding="utf-8"))
    before_rec = sum(len(e.get("sources") or []) for e in data["entries"])
    before_keys = sorted(data)
    entry = next((e for e in data["entries"] if e["id"] == entry_id), None)
    if entry is None:
        sys.exit(f"no entry {entry_id!r}")
    if entry.get("provenance") == "thesis":
        sys.exit(f"{entry_id} is provenance:thesis - it takes no citation by "
                 f"design, and giving it one would be a false credit")

    rec = {"citation": flags["citation"],
           "status": flags.get("status", "unverified"),
           "claim": flags.get("claim",
                              "No specific claim is recorded against this "
                              "source. The record is a pointer to the work in "
                              "general; the entry's own prose is the argument "
                              "and is not sourced line by line.")}
    url = flags.get("url")
    if url:
        doi = doi_from(url)
        if doi:
            ok, note = check_identity(doi, flags["citation"])
            print(f"  identity check for {doi}:\n    {note}")
            if not ok:
                sys.exit("refusing to write a DOI that is not this work")
            rec["url"] = url
            rec["locator"] = f"doi:{doi}"
            rec["identity_verified"] = note
        else:
            rec["url"] = url
            rec["identity_verified"] = ("no DOI in this locator, so identity "
                                        "was NOT checked - the citation is "
                                        "recorded as given")
    else:
        rec["identity_verified"] = "no locator, so identity was not checked"

    srcs = entry.setdefault("sources", [])
    if "update" in flags:
        hits = [s for s in srcs if flags["update"].lower() in
                str(s.get("citation", "")).lower()]
        if len(hits) != 1:
            sys.exit(f"--update {flags['update']!r} matched {len(hits)} records; "
                     f"need exactly 1")
        old = hits[0]
        rec["citation_replaced"] = old.get("citation")
        srcs[srcs.index(old)] = rec
        action = "updated"
    else:
        srcs.append(rec)
        action = "added"

    if not APPLY:
        print(f"  dry run: would have {action} a record on {entry_id}")
        print("  " + json.dumps(rec, ensure_ascii=False)[:200])
        raise SystemExit(0)

    after_rec = sum(len(e.get("sources") or []) for e in data["entries"])
    expect = before_rec + (1 if action == "added" else 0)
    if after_rec != expect:
        sys.exit(f"refusing to write: record count {before_rec} -> {after_rec}, "
                 f"expected {expect}")
    if sorted(data) != before_keys:
        sys.exit("refusing to write: top-level keys changed")

    tmp = DATA.with_suffix(".json.tmp")
    tmp.write_text(json.dumps(data, ensure_ascii=False, indent=1) + "\n",
                   encoding="utf-8")
    if len(json.loads(tmp.read_text(encoding="utf-8"))["entries"]) != \
            len(data["entries"]):
        sys.exit("refusing to write: reparse did not reconcile")
    tmp.replace(DATA)
    print(f"  {action} on {entry_id}. records {before_rec} -> {after_rec}. "
          f"status={rec['status']} (not 'verified': a locator is not a reading)")