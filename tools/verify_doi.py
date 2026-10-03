"""verify_doi.py - does this DOI resolve to the work the citation names?

Written after Crossref was asked for thirteen titles by the corpus and returned a
DOI for all thirteen. **Two were the work being looked for.** The rest resolved
perfectly well to something else:

    parasocial-persuasion   -> 10.64628/aa.ketwakysr   "Man's stressed friend:
                               how your mental health can affect your dog"
    keep-it-or-lose-it      -> 10.22215/etd/2008-07541 a thesis about sports
    psr-research-begins     -> 10.1145/3462204.3481763 a 2021 conference paper
    attention-economy       -> 10.5040/9781350376267.ch-004  a 2025 chapter
                               called "Attention merchants", not Wu's 2016 book
    the-uncanny-corridor    -> 10.1201/b17830-5        a 2014 book *about* the
                               uncanny valley, not Mori's 1979 article

Every one of those URLs loads. That is the point: **a resolving DOI is not
evidence of identity**, and Crossref's bibliographic query is a fuzzy search that
always returns something. A DOI attached to the wrong paper is worse than no
locator, because it looks like verification - it is the citation equivalent of a
`kind: exact` derived from a filename, and this file is the `looked` date.

So the check is not "does it resolve". It is **does what it resolve to match the
thing being cited**. That comparison is mechanical where it can be - words, year,
author, container - and is reported as a verdict rather than decided silently:

    MATCH      every token in `expect` appears in the returned title
    MISMATCH   it resolves, and it is a different work
    UNCHECKED  it resolves, and the comparison needs a person

Usage:
    python tools\\verify_doi.py 10.1111/j.1468-2958.1985.tb00071.x \\
        --expect "loneliness, parasocial interaction"
    python tools\\verify_doi.py --from-citations   # check every DOI in the corpus
"""
from __future__ import annotations

import json
import pathlib
import re
import sys
import time
import urllib.parse
import urllib.request

ROOT = pathlib.Path(__file__).resolve().parent.parent
UA = {"User-Agent": "parasocialize-source-check/1.0 (identity check, not a crawler)"}

# Crossref rate-limited a batch of eleven queries with HTTP 429 partway through,
# which lost a result silently - the job printed an ERR and moved on, so the
# batch looked like "nothing found" rather than "not all of it ran". One request
# every 400ms and three retries with a real backoff.
_LAST = [0.0]


def _get(url, tries=3):
    for attempt in range(tries):
        gap = time.time() - _LAST[0]
        if gap < 0.4:
            time.sleep(0.4 - gap)
        try:
            body = urllib.request.urlopen(
                urllib.request.Request(url, headers=UA), timeout=45).read()
            _LAST[0] = time.time()
            return body
        except urllib.error.HTTPError as e:
            _LAST[0] = time.time()
            if e.code == 429 and attempt < tries - 1:
                time.sleep(2.0 * (attempt + 1))
                continue
            raise
        except Exception:
            _LAST[0] = time.time()
            raise
    raise RuntimeError("unreachable")

STOP = {"the", "a", "an", "of", "and", "in", "on", "for", "to", "is", "as",
        "with", "from", "at", "by", "its", "their", "his", "her",
        # Added after the dog paper scored 3 of 9 instead of 1 of 7: "how" and
        # "your" are stopwords that survived, and they inflated the overlap on
        # exactly the comparison that was supposed to catch it.
        "how", "your", "what", "when", "where", "which", "who", "why",
        "can", "does", "do", "was", "were", "are", "been", "have", "has",
        "had", "but", "not", "no", "than", "then", "there", "these", "those"}


def clean(s):
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", "", s or "")).strip()


def fetch(doi):
    u = "https://api.crossref.org/works/" + urllib.parse.quote(doi)
    d = json.loads(_get(u))
    m = d.get("message") or {}
    auth = m.get("author") or []
    return {
        "doi": m.get("DOI"),
        "title": clean((m.get("title") or [""])[0]),
        "authors": [clean(f"{a.get('family','')} {a.get('given','')}").strip()
                    for a in auth],
        "container": clean((m.get("container-title") or [""])[0]),
        "year": ((m.get("issued") or {}).get("date-parts") or [[None]])[0][0],
        "type": m.get("type"),
        "publisher": m.get("publisher"),
    }


def tokens(s):
    return {t for t in re.findall(r"[a-z0-9]+", (s or "").lower())
            if t not in STOP and len(t) > 2}


def parse_citation(cit):
    """Pull the parts of a citation that can be compared against Crossref.

    A citation is `Authors (Year). Title. Journal, vol(issue), pp. pages.` and
    only the middle of that is a title. The first version of this tool handed
    the **whole string** to the comparison, so eight author names, a journal, a
    volume and the words "Article 81" were all treated as expected title words
    and every single record came back MISMATCH - including `10.1145/3359183`,
    which resolves to "Dark Patterns at Scale" by Mathur, Acar and Friedman,
    which is precisely what `loyalty-dark-pattern` cites. **Forty-four records
    reported as wrong citations, all of them correct, because the measurement
    was on the wrong layer.** That is the "a measurement can be right about the
    wrong layer" trap and the only reason it was caught is that zero of forty-four
    is not a plausible result.
    """
    cit = clean(cit)
    year = None
    m = re.search(r"\((?:[^)]*?\b)?(1[89]\d\d|20\d\d)\b[^)]*\)", cit) \
        or re.search(r"\b(1[89]\d\d|20\d\d)\b", cit)
    if m:
        year = m.group(1)
    # Surnames from the leading author block: "Mathur, A., Acar, G., ..."
    surnames = set()
    head = cit.split("(")[0] if "(" in cit else cit[:120]
    for chunk in re.split(r",\s*(?=[A-Z][a-z]+\s*,)", head):
        name = re.match(r"\s*([A-Z][A-Za-z'\-]+)", chunk)
        if name and len(name.group(1)) > 2:
            surnames.add(name.group(1).lower())
    # Title: after the year parenthesis, up to a period before the journal.
    title = ""
    if "(" in cit:
        after = cit.split(")", 1)[1].lstrip(". ").strip()
        title = after.split(". ")[0] if ". " in after else after
    else:
        parts = cit.split(". ")
        title = parts[1] if len(parts) > 1 else cit
    return {"year": year, "surnames": surnames, "title": title.strip(" .")}


def verdict(meta, expect=None, expect_year=None):
    """MATCH, MISMATCH, or UNCHECKED - in that order of confidence.

    Author and year are the strong signals, because Crossref states them
    authoritatively and a wrong paper does not usually share both. Title overlap
    is the weak signal and decides only when the strong ones agree.
    """
    if not expect:
        return "UNCHECKED", "no expectation given, so nothing was compared"
    got = parse_citation(expect)
    want_year = expect_year or got["year"]
    author_ok = None
    year_ok = None
    notes = []

    if want_year and meta.get("year"):
        year_ok = (str(want_year) == str(meta["year"]))
        if not year_ok:
            notes.append(f"year is {meta['year']}, not {want_year}")

    if got["surnames"]:
        # Both tokens of every author name, not just the last. Crossref has
        # `family: "Arunesh"` for Mathur Arunesh - Indian names are frequently
        # stored given-name-first - so comparing only the trailing token compares
        # given names and reports a correct citation as wrong. Every token is
        # tried, which is looser, and the looseness is in the safe direction: a
        # false MATCH still leaves a person reading the title.
        have = {t.lower() for a in meta["authors"] for t in a.split() if t}
        hit = {s for s in got["surnames"] if s in have}
        author_ok = bool(hit)
        if hit:
            notes.append(f"author {sorted(hit)[:4]} matches")
        elif have:
            notes.append(f"none of {sorted(got['surnames'])[:5]} among "
                         f"{sorted(have)[:5]}")

    # Author and year are the strong signals and they decide. The title only
    # arbitrates when they are silent, because citations and Crossref routinely
    # disagree about titles for reasons that are not errors: the citation carries
    # a subtitle Crossref truncates ("Dark Patterns at Scale: Findings from a
    # Crawl of 11K Shopping Websites" against "Dark Patterns at Scale"), or the
    # record uses the running head rather than the full title.
    if author_ok and (year_ok or not want_year):
        want = tokens(got["title"])
        seen = tokens(meta["title"])
        if not want:
            # **Author and year alone can never be a MATCH.** Making it one
            # created a false positive immediately: the corpus cites
            # "Jussila et al. (2020)" with no title, and the search returned
            # `10.1007/978-981-15-0069-5_13`, "Sensory Technologies for Improving
            # Employee Experience and Strengthening Customer Loyalty" - a
            # different paper, same first author, same year, matched and accepted.
            # An author and a year are a *pair of coordinates*, not a work: any
            # prolific author has dozens of papers in any given year, so the
            # combination narrows the field and does not identify anything in it.
            # It is enough to make a candidate worth reading. It is not enough
            # to record a locator on.
            return "UNCHECKED", "; ".join(notes + [
                "author and year agree, but the citation carries no title, so "
                "nothing distinguishes this from another paper by the same "
                "author in the same year - read it before it becomes a locator"])
        if not want <= seen:
            return "UNCHECKED", "; ".join(notes + [
                f"author and year agree but the title differs (missing "
                f"{sorted(want - seen)[:4]}) - often a subtitle, but read it"])
        return "MATCH", "; ".join(notes + [
            f"author, year and all {len(want)} title words agree"])

    if year_ok is False or author_ok is False:
        return "MISMATCH", "; ".join(notes)

    want = tokens(got["title"])
    if not want:
        return "UNCHECKED", ("; ".join(notes) +
                             "; the citation carries no title to compare")
    seen = tokens(meta["title"])
    missing = sorted(want - seen)
    if not missing:
        return "MATCH", "; ".join(notes + [f"title matches ({len(want)} words)"])
    if len(want & seen) / len(want) < 0.5:
        return "MISMATCH", "; ".join(notes + [
            f"only {len(want & seen)}/{len(want)} title words appear; it "
            f"resolves to {meta['title'][:56]!r}"])
    return "UNCHECKED", "; ".join(notes + [f"title missing {missing[:5]}"])


def show(doi, expect=None, expect_year=None):
    try:
        meta = fetch(doi)
    except Exception as e:
        print(f"  UNRESOLVED  {doi}  ({e})")
        return None
    v, why = verdict(meta, expect, expect_year)
    print(f"  {v:<10} {doi}")
    print(f"      title    : {meta['title'][:88]}")
    print(f"      author   : {', '.join(meta['authors'][:3]) or '(none listed)'}"
          f"   year: {meta['year']}")
    if meta["container"]:
        print(f"      in       : {meta['container'][:74]}")
    print(f"      verdict  : {why}")
    print()
    return meta, v


def search(title, author=None, rows=5):
    """Crossref candidates for a title, optionally narrowed by author.

    `query.bibliographic` alone is a fuzzy search that returns something for
    everything - it produced a paper about dogs for a query about parasocial
    persuasion. Splitting the query into `query.title` and `query.author` narrows
    it, and every candidate still comes back through `verdict()` rather than
    being accepted because it was returned.
    """
    u = ("https://api.crossref.org/works?rows=%d&select=DOI,title,author,"
         "container-title,issued,type&query.title=%s"
         % (rows, urllib.parse.quote(title)))
    if author:
        u += "&query.author=" + urllib.parse.quote(author)
    d = json.loads(_get(u))
    out = []
    for it in (d.get("message") or {}).get("items") or []:
        auth = it.get("author") or []
        out.append({
            "doi": it.get("DOI"),
            "title": clean((it.get("title") or [""])[0]),
            "authors": [clean(f"{a.get('family','')} {a.get('given','')}").strip()
                        for a in auth],
            "container": clean((it.get("container-title") or [""])[0]),
            "year": ((it.get("issued") or {}).get("date-parts") or [[None]])[0][0],
        })
    return out


def find(doi_expect, title=None, author=None):
    """Print candidates with a verdict against the citation being located."""
    expect = doi_expect
    for c in search(title or expect, author):
        v, why = verdict(c, expect=expect)
        mark = {"MATCH": "  MATCH  ", "MISMATCH": "  reject ", "UNCHECKED":
                "  ?      "}[v]
        print(f"{mark}{c['doi']}")
        print(f"          {c['title'][:86]}")
        print(f"          {', '.join(c['authors'][:3]) or '(none)'} "
              f"{c['year']}"
              + (f"  |  {c['container'][:44]}" if c["container"] else ""))
        print(f"          {why[:140]}")
        print()


def main():
    args = sys.argv[1:]
    if not args:
        print(__doc__)
        return
    if args[0] == "--from-citations":
        enc = json.loads((ROOT / "data" / "encyclopedia.json")
                         .read_text(encoding="utf-8"))
        rows = []
        for e in enc["entries"]:
            for s in e.get("sources") or []:
                u = str(s.get("url") or "")
                m = re.search(r"(10\.\d{4,9}/[^\s\"'<>?#]+)", u)
                if m:
                    rows.append((e["id"], s.get("citation"), m.group(1)))
        print(f"{len(rows)} DOI-bearing records in the corpus\n")
        tally = {"MATCH": 0, "MISMATCH": 0, "UNCHECKED": 0}
        unresolved = 0
        for eid, cit, doi in rows:
            print(f"  {eid:<26} {doi}")
            print(f"      citing   : {str(cit)[:84]}")
            got = show(doi, expect=cit)
            if got:
                tally[got[1]] += 1
            else:
                unresolved += 1
        tally["UNRESOLVED"] = unresolved
        print("  ", tally)
        return
    if args[0] == "--find":
        expect = args[1]
        title = args[args.index("--title") + 1] if "--title" in args else None
        author = args[args.index("--author") + 1] if "--author" in args else None
        print(f"locating: {expect}\n")
        find(expect, title, author)
        return
    expect = None
    year = None
    if "--expect" in args:
        expect = args[args.index("--expect") + 1]
    if "--year" in args:
        year = args[args.index("--year") + 1]
    show(args[0], expect, year)


if __name__ == "__main__":
    main()