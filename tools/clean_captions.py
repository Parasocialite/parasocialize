"""Re-clean captions already written to the manifest. The first pass of
pretty() left dates, agency names and hex ids in front of the reader, and those
are now stored in data/images.json. Re-running it is safe: it is idempotent on
anything already clean, and it only ever removes, never asserts anything new."""
import sys, pathlib, json
sys.path.insert(0, 'tools')
import images as im

man = im.jload(im.MAN, {"items": []})
n = 0
for it in man["items"]:
    src = it.get("src") or {}
    for key in ("title",):
        if src.get(key):
            new = im.pretty(src[key])
            if new != src[key]:
                src[key] = new
                n += 1
    if it.get("caption"):
        new = im.pretty(it["caption"])
        if new != it["caption"]:
            it["caption"] = new
im.jdump(im.MAN, man)
print(f"cleaned {n} source titles")
print("\nfirst 12 captions now:")
for it in man["items"][:12]:
    if it.get("caption"):
        print("  " + it["caption"][:76])
