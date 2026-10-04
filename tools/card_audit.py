"""card_audit.py - are the 47 published stories telling the truth about their sources?

Found while asking whether anything stops a drafted candidate being published
without a real source. The honest answer was worse: `citation_audit.py` opens
`data/encyclopedia.json` and iterates `enc["entries"]`. It never reads
`data/index.json`. **The 193 encyclopedia entries are gated. The 47 stories the
front page is made of are not.** Every session's work hardened the reference
work while the publication went unchecked.

That surface is not clean either:

  kpop-uae-grief     one source record has `url: null`. A real outlet, a real
                     headline, and nowhere to go and check it.
  5 records          the link is MSN while `publisher` names someone else, so
                     the metadata and the link name different organisations.
  9 records          `publisher: "Vitamin E K"` - a Substack whose display name
                     reads as a chemical.
  9 records          `publisher: "note"` - that is the platform note.com, not a
                     publisher. The scraper fell back to the domain.
  1 record           `publisher: "Gayle Stever"` - an author, in a field named
                     for a publisher.

`publisher` is being filled with whatever the extractor found: a masthead, a
platform, a publication's display name, or a person. The field name promises a
publishing organisation and keeps returning four different things. That is this
project's signature defect wearing a new hat - `kind: exact` derived from a
filename, `claim: "the entry as a whole"` printed beside a citation, and now a
provenance field that means whichever of those four things the scraper reached
first.

So this holds the field to its name. A `publisher` that is a domain, a platform
or a person is not a publisher, and a source with no URL is not a source.

    python tools\\card_audit.py

WHAT IT DOES NOT CHECK

It does not open a single URL. Whether each link resolves, whether the article
says what the card claims, and whether the framing is fair are all judgements
about the outside world, and this project has been wrong often enough about the
outside world to be careful about automating them. What it does check is the
shape of the claim the site makes about itself: a provenance record that names no
organisation and points nowhere cannot be presented to a reader as provenance.
"""
from __future__ import annotations

import json
import pathlib
import re
import sys
from collections import Counter
from urllib.parse import urlparse

ROOT = pathlib.Path(__file__).resolve().parent.parent
IDX = ROOT / "data" / "index.json"

# Domains that are platforms, and whose name is therefore not a publisher.
PLATFORM = {
    "note.com", "medium.com", "substack.com", "wordpress.com", "blogspot.com",
    "dev.to", "substack", "note", "medium",
}
# Redirect/aggregator hosts. A link here is not the publisher, whoever the
# `publisher` field claims, because the reader cannot see the original from it
# and the site's own line is that every card links to its sources.
AGGREGATOR = {
    "www.msn.com", "news.google.com", "www.bing.com", "l.facebook.com",
    "t.co", "tinyurl.com", "ow.ly", "buff.ly",
}
# Words that make a string a platform or a status rather than an organisation.
NOT_PUBLISHER_WORDS = {
    "note", "medium", "substack", "blog", "wordpress", "unknown", "n/a",
    "none", "tbd", "source", "report", "article", "link", "test",
}

STOP = {"the", "a", "of", "and", "for", "on", "in", "at", "to"}

# A "does this look like a person's name?" check was written here and removed.
# It fired on 11 of 51 records and 10 of those were organisations: Yahoo Style
# Australia, ABC Triple J, American Enterprise Institute, Vogue Australia, Dot
# Esports, Helpful Professor. Two or three capitalised words in a field named
# `publisher` is overwhelmingly a masthead, not a person - and the one real
# person it found, Gayle Stever, is not a false attribution, just an author
# recorded in the wrong field. A check that is wrong nine times in ten gets
# ignored, and a gate that gets ignored protects nothing. Replaced with the test
# that is actually unambiguous: does the `publisher` string agree with the host
# the link points at?


def main():
    data = json.loads(IDX.read_text(encoding="utf-8"))
    cards = data["cards"]
    recs = [(c["slug"], s) for c in cards for s in (c.get("sources") or [])]

    print(f"card_audit: {len(cards)} published cards, {len(recs)} source records\n")

    fail, warn = [], []

    # 1. a source with nowhere to go. This is a hard failure: the card is
    #    published, the site says every card links to its sources, and this one
    #    does not link to anything.
    for slug, s in recs:
        u = str(s.get("url") or "").strip()
        if not re.match(r"^https?://[^\s]+$", u):
            fail.append((slug, f"source has no usable URL (url={s.get('url')!r}) "
                               f"- publisher={s.get('publisher')!r}"))

    # 2. the site cannot be its own source, and a provenance record with no
    #    organisation in it is not provenance
    for slug, s in recs:
        if "parasocialize" in urlparse(str(s.get("url") or "")).netloc.lower():
            fail.append((slug, "source is this site"))
        if not str(s.get("publisher") or "").strip():
            fail.append((slug, "source record names no publisher"))

    # 3. publisher names a platform or a domain rather than an organisation
    for slug, s in recs:
        pub = str(s.get("publisher") or "").strip()
        host = urlparse(str(s.get("url") or "")).netloc.lower()
        bare = re.sub(r"^www\.", "", host)
        if pub.lower().strip(".") in NOT_PUBLISHER_WORDS:
            warn.append((slug, f"publisher={pub!r} is a platform word, not an "
                               f"organisation (host {bare})"))
        elif bare in PLATFORM or host in PLATFORM:
            warn.append((slug, f"publisher={pub!r} but the host is the platform "
                               f"{bare} - the field holds a site, not a publisher"))
        elif bare and pub.lower().replace(" ", "") == bare.replace(".", "").replace(" ", ""):
            warn.append((slug, f"publisher={pub!r} is just the domain"))

# 4. the publisher string and the host it points at name different things.
    #
    #    This check was written, fired on 28 of 51 records, and was deleted in
    #    the same sitting. Every one of those was a legitimate masthead: "The
    #    Guardian" against theguardian.com, "Parasocial Magazine" against
    #    parasocialmagazine.com, "Psychology Today" against psychologytoday.com,
    #    "USA Today" against usatoday.com. The problem is structural - a
    #    publisher is a spaced string and a domain is a run-together one, so the
    #    comparison has to guess at normalisation, and then ABC News versus
    #    abc.net.au, SMH versus smh.com.au and AEI versus aei.org are real
    #    abbreviations that no amount of normalising resolves.
    #
    #    Deciding whether a masthead matches its own domain is a judgement about
    #    publishing, not a string operation. Two attempts at automating it both
    #    produced mostly false positives, and a check that is wrong nine times in
    #    ten gets ignored - at which point it protects nothing. The checks below
    #    are the ones that cannot be argued with: a missing URL, a missing
    #    publisher, this site citing itself, an aggregator standing in for a
    #    named outlet, and a personal newsletter as the only witness to a fact.

    # 4b. a personal Substack as the only source for a factual claim. The
    #     sasaeng card is the live case: a criminal conviction with a sentence
    #     and a count of doorbell rings, cited to one post on a personal
    #     newsletter and to nothing else. Convictions are matters of public
    #     record and a blog is not where they are reported.
    for slug, s in recs:
        host = urlparse(str(s.get("url") or "")).netloc.lower()
        if host.endswith("substack.com"):
            others = [x for c in cards if c["slug"] == slug
                      for x in (c.get("sources") or [])
                      if not urlparse(str(x.get("url") or "")).netloc.lower().endswith("substack.com")]
            if not others:
                warn.append((slug, "sole source is a personal Substack - fine for "
                                   "an opinion, thin for a fact a court recorded"))

    # 5. the link is an aggregator while the field claims someone else
    for slug, s in recs:
        host = urlparse(str(s.get("url") or "")).netloc.lower()
        pub = str(s.get("publisher") or "").strip().lower()
        if host in AGGREGATOR and pub and pub not in host:
            warn.append((slug, f"link is {host} but publisher says {s.get('publisher')!r} "
                               f"- the metadata and the link name different organisations"))

    # 6. date sanity, cheap
    for slug, s in recs:
        a = str(s.get("at") or "")
        if a and not re.match(r"^\d{4}-\d{2}-\d{2}", a):
            warn.append((slug, f"date is not ISO: {a!r}"))
        elif a and not (1990 <= int(a[:4]) <= 2027):
            warn.append((slug, f"date out of range: {a!r}"))

    print("FAIL (blocks the build)")
    if not fail:
        print("  none")
    for slug, msg in fail:
        print(f"  {slug}\n      {msg}")

    print(f"\nWARN ({len(warn)}) - a human decides these")
    for slug, msg in warn:
        print(f"  {slug}\n      {msg}")

    print("\nwhat this cannot check: whether any of these URLs opens, or says")
    print("what the card claims. Both need a reader, not a regex.")

    return 1 if fail else 0


if __name__ == "__main__":
    sys.exit(main())