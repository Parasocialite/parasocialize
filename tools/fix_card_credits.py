"""Set `via` to the host a reader actually lands on, and fix platform-as-publisher.

Three cards credit Phys.org, The Economic Times and ABC News (Australia) while
linking to www.msn.com. MSN syndicates other outlets wholesale; that is a
legitimate route to a reader and not the same as reading the originating outlet,
so the credit has to name both. `via` was the field for exactly that and held
`report`, which means nothing, on eight records.

`oshi-katsu-half-century` has `publisher: "note"`. note.com is a Japanese
publishing *platform*, like Substack or Medium, and the account is `lesser_p` -
visible in the URL. "note" is an identifier printed where an organisation belongs,
which is the anchor-in-the-bibliography trap in a small key.

The two sole-Substack warnings are editorial and are deliberately NOT touched
here. `sasaeng-j-songwriter-conviction` asserts a criminal conviction about a
named living person on one person's Substack; that needs a court or news record
or an admission on the page, not a metadata fix.

Asserts the card count and the set of slugs before and after.
"""
import json
import pathlib
import re
import sys
from urllib.parse import urlparse

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ROOT = pathlib.Path(__file__).resolve().parent.parent
APPLY = "--apply" in sys.argv

p = ROOT / "data" / "shop.json"
shop = json.loads(p.read_text(encoding="utf-8"))
before_cards = len(shop["cards"])
before_slugs = sorted(c["slug"] for c in shop["cards"])
before_keys = sorted(shop)

# host -> how to name it in a credit
HOST_LABEL = {
    "www.msn.com": "MSN",
    "note.com": "note.com",
}

# a platform is not an organisation; where the account is in the path, use it
PLATFORM = re.compile(r"^(note|substack\.com|medium\.com|dev\.to|wordpress\.com)$", re.I)

changed = []
for c in shop["cards"]:
    for s in c.get("sources") or []:
        url = str(s.get("url") or "")
        if not url:
            continue
        host = (urlparse(url).netloc or "").lower()
        pub = str(s.get("publisher") or "")

        # 1. platform named as the publisher
        if PLATFORM.match(pub.replace(" ", "").lower()):
            acct = ""
            m = re.search(r"\.com/([^/]+)/", url)
            if m and m.group(1) not in ("p", "posts", "en"):
                acct = m.group(1)
            new = f"{pub} ({acct})" if acct else pub
            changed.append((c["slug"], "publisher", pub, new))
            s["publisher"] = new
            s["publisher_note"] = (
                f"{pub} is a publishing platform, not an organisation; the "
                f"account is {acct}. Crediting the platform alone names a host "
                f"rather than whoever wrote it."
            )
            pub = new

        # 2. host differs from the credited organisation
        #
        # Not when the host IS the publisher's own platform. A note.com post is
        # published by an account ON note.com; there is no separate originating
        # organisation being syndicated, and setting `via` there produced the
        # credit "note (lesser_p), via note.com" - two names for one thing. The
        # case `via` exists for is a wire story republished somewhere else.
        label = HOST_LABEL.get(host)
        platform_own = PLATFORM.match(pub.split("(")[0].replace(" ", "").lower())
        if label and not platform_own and pub and \
                label.lower() not in pub.lower() and \
                pub.lower() not in label.lower():
            if str(s.get("via") or "") != label:
                changed.append((c["slug"], "via", s.get("via"), label))
                s["via"] = label

print(f"{before_cards} cards; {len(changed)} field(s) to change\n")
for slug, field, old, new in changed:
    print(f"  {slug:<40} {field}: {old!r} -> {new!r}")
print("\n  (the two sole-Substack warnings are left alone deliberately - they are")
print("   editorial, and one of them is a criminal conviction about a named person)")

if not APPLY:
    print("\ndry run. re-run with --apply")
    raise SystemExit(0)

after_cards = len(shop["cards"])
if after_cards != before_cards or \
        sorted(c["slug"] for c in shop["cards"]) != before_slugs or \
        sorted(shop) != before_keys:
    sys.exit("refusing to write: card count or key set moved")

tmp = p.with_suffix(".json.tmp")
tmp.write_text(json.dumps(shop, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
if len(json.loads(tmp.read_text(encoding="utf-8"))["cards"]) != before_cards:
    sys.exit("refusing to write: reparse did not reconcile")
tmp.replace(p)
print(f"\nwritten. cards {before_cards} unchanged.")
