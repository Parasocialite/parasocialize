"""Add proper reporting to `sasaeng-jungkook-conviction` and close a warning.

The card asserts a criminal conviction about a named living person, with two
specific numbers, and cited **one person's Substack** as its sole source. That is
the warning, and it is a fair one: a conviction is a matter of public record and
should not rest on a newsletter.

Checking the claims rather than assuming them, every number holds, and the case
is reported by several independent outlets including a bylined wire story and a
paper that names the judge and the court:

  22 visits          Korea Times: the court heard she visited the residence and
                     the surrounding area 22 times between 7 and 28 December
  133 doorbell rings BBC, The Independent, NME, GMA: 133 times on one visit,
                     which the court called an "extreme level of obsession"
  conviction         one year imprisonment, suspended for two years; sentenced
                     8 May by Judge Park Ji-won of the Seoul Western District
                     Court for violating the anti-stalking law and trespassing

So this is not a false card. It is a true card resting on the weakest available
citation, which is the same defect as a `retrievable` record with no URL: the
claim is true and the support is not there yet.

The woman is unnamed in every report and in the court documents, and the card
does not name her. That is worth preserving deliberately - a conviction is a
fact about a person, and the site has no need to make her findable.

The Substack is kept. It is a secondary commentary and it is not wrong; it is
simply no longer the only thing standing under the claim.

Asserts the card count and slug set before and after.
"""
import json
import pathlib
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ROOT = pathlib.Path(r"C:\Users\paras\Documents\Default Project\parasocialize")
APPLY = "--apply" in sys.argv
SLUG = "sasaeng-jungkook-conviction"

ADD = [
    {
        "publisher": "BBC News",
        "title": "BTS fan who rang Jungkook's doorbell 133 times faces deportation",
        "url": "https://www.bbc.com/news/articles/c9v2d9edx9wo",
        "at": "2026-06-23",
        "via": "report",
    },
    {
        "publisher": "The Korea Times",
        "title": ("Brazilian woman gets suspended prison term for stalking BTS' "
                  "Jung Kook"),
        "url": ("https://www.koreatimes.co.kr/entertainment/k-pop/20260623/"
                "brazilian-woman-gets-suspended-prison-term-for-stalking-bts-jung-kook"),
        "at": "2026-06-23",
        "via": "report",
    },
]

NOTE = ("The card's figures were checked against the court reporting before this "
        "record was added, not after: 22 visits between 7 and 28 December, 133 "
        "rings on a single visit, one year suspended for two years, sentenced "
        "8 May by Judge Park Ji-won of the Seoul Western District Court. The "
        "defendant is unnamed in every report and in the court documents, and "
        "this card does not name her.")

p = ROOT / "data" / "shop.json"
shop = json.loads(p.read_text(encoding="utf-8"))
before = len(shop["cards"])
before_slugs = sorted(c["slug"] for c in shop["cards"])
before_keys = sorted(shop)

card = next((c for c in shop["cards"] if c["slug"] == SLUG), None)
if card is None:
    sys.exit(f"no card {SLUG}")
srcs = card.setdefault("sources", [])
have = {str(s.get("url") or "") for s in srcs}

todo = [a for a in ADD if a["url"] not in have]
print(f"{SLUG}: {len(srcs)} source record(s), {len(todo)} to add\n")
for a in todo:
    print(f"  + {a['publisher']}  {a['at']}")
    print(f"    {a['title'][:88]}")

if not todo:
    print("\nnothing to add")
if not APPLY:
    print("\ndry run. re-run with --apply")
    raise SystemExit(0)

for a in todo:
    rec = dict(a)
    rec["corroborates"] = NOTE
    srcs.insert(0, rec)
card["sources_note"] = (
    "Originally sole-sourced to one personal Substack, which is thin for a "
    "criminal conviction. The figures were checked against the court reporting "
    "and the card now carries a bylined wire story and the paper that names the "
    "judge and the court. The Substack is kept as secondary commentary.")

if len(shop["cards"]) != before or \
        sorted(c["slug"] for c in shop["cards"]) != before_slugs or \
        sorted(shop) != before_keys:
    sys.exit("refusing to write: card count or key set moved")

tmp = p.with_suffix(".json.tmp")
tmp.write_text(json.dumps(shop, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
if len(json.loads(tmp.read_text(encoding="utf-8"))["cards"]) != before:
    sys.exit("refusing to write: reparse did not reconcile")
tmp.replace(p)
print(f"\nwritten. cards {before}, sources on {SLUG} now "
      f"{len(card['sources'])}.")