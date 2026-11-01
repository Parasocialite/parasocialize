#!/usr/bin/env python3
"""
build_deploy.py - rebuild the site, assemble dist/, and prove it holds together.

WHY THIS EXISTS
The first upload to Cloudflare Pages failed: "Your upload exceeds the limit of
1000 files." The site is not that big. Counting the folder gave 439 files.
Counting the repository gave 1950, because 1511 of them were inside .git -
1487 loose git objects, because this repo has six commits of a build that
rewrites every page on every run. Cloudflare's direct upload takes a folder and
uploads what is in it, and it does not read .gitignore.

So the fix is not the 20,000-file Wrangler path, which also needs Node. The fix
is to upload a directory that contains the website and nothing else. 439 files
becomes about 385, which is comfortably under the limit and needs no new
tooling on the machine.

WHY IT BUILDS BEFORE IT PACKAGES
A packaging step that only copies is a packaging step that ships whatever day
the pages were last generated. In October 2026 the front page's date-seeded top
8, register and parasocialite stayed on 21 October while every gate was green:
the rotation was correct, the copy was faithful, and the tree being copied had
simply stopped being current. The deploy command was the defect, not the
rotation.

So this now runs `build_cards.py` and then `plate.py` before it touches dist/,
which makes `python tools/build_deploy.py` the one fresh-deploy command.
`--no-build` exists for `gates.py`, which already runs those two steps in order
and must not run them twice. `--check-only` inspects existing dist/ and never
builds, because a check that quietly rebuilt would no longer be checking what
was handed to it.

WHAT IS IN, AND WHY
    *.html      every page, including the 177 encyclopedia entries
    css/ js/    two stylesheets and one script
    img/        95 cached photographs and 16 svg
    *.txt *.xml robots.txt, sitemap.xml, radar.xml - radar.xml is linked from
                all 260 pages as the autodiscovery feed, so it is load-bearing
                and not a build artifact

WHAT IS OUT
    .git/       the entire problem: 1511 files of history
    tools/      30 python files that build the site and are not the site
    data/       13 json files. Nothing references them at runtime - the atlas
                and the quiz inline their own data deliberately, so that each
                is one file with no fetch. Verified below, not assumed.
    __pycache__ 8 .pyc files
    *.md        working notes that are not pages

THE CHECK THAT MATTERS
An assembly script that copies the wrong set of things ships a broken site
quietly. So after assembling, this walks every local href and src in every page
in dist and confirms it resolves to a file that is actually there, and confirms
the count is under the limit. A missing file is a build failure, not a warning.

THE IMAGES
37.8 of the 41 MB was 96 cached photographs, unoptimised - one frame of Hugh
Jackman was 3.65 MB. That uploads fine and then makes the homepage download
megabytes before a reader sees a headline, which is the sort of thing that
shows up in Core Web Vitals as your problem rather than the host's.

So dist/ ships WebP, re-encoded at 1400px and quality 76, which is 16% of the
original bytes and visually indistinguishable at the sizes these are actually
displayed. The originals stay in img/editorial/ as the cache and the thing a
re-run re-encodes from; only dist/ gets the derived files. If a file comes out
LARGER as WebP, the original is kept and the reference is left alone rather
than paying bytes for nothing.

Critically this rewrites the references. Adding .webp files without repointing
the HTML at them would reduce nothing at all, which is the obvious way to do
this wrong, and the link verifier at the end is what catches it if the mapping
and the filenames ever stop agreeing.

  python tools/build_deploy.py
  python tools/build_deploy.py --no-build
  python tools/build_deploy.py --check-only
  python tools/build_deploy.py --no-optimise
"""
import pathlib, shutil, sys, re, urllib.parse, argparse, io, json, subprocess

ROOT = pathlib.Path(__file__).resolve().parent.parent
DIST = ROOT / "dist"

INCLUDE_GLOBS = ["*.html", "*.css", "*.js", "*.txt", "*.xml", "*.svg", "*.jpg",
                 "*.png", "*.webp", "*.ico", "*.woff2"]
INCLUDE_DIRS = ["css", "js", "img", "assets"]
# ".html" comes out of "*.html" by dropping the asterisk and nothing else.
# lstrip("*.") also ate the dot and matched nothing, which put a dist/ with 116
# files and no pages in it - see the page-count guard in main().
EXTS = {g.lstrip("*") for g in INCLUDE_GLOBS}
# `episode` is a BUILD WORKING DIRECTORY, not part of the site. Three episodes
# of 1080x1920 frames and narration took the deploy zip from 8.5MB to 71MB and
# the verifier refused it, which is the check earning its keep: nothing about a
# 71MB upload looks wrong until something refuses it.
EXCLUDE_NAMES = {".git", "__pycache__", "tools", "data", "node_modules", "dist",
                  ".github", "audit_out", "__dist__", "episode", "research-cache"}
LIMIT = 1000

# Order matters: build_cards writes the pages and the day records, plate draws
# its SVGs from the data build_cards just read, and only then may anything be
# copied. Running plate first would draw plates from yesterday's corpus, which
# is the same defect as shipping yesterday's HTML with better colours.
#
# These run as subprocesses rather than imported functions because both files
# are programs with their own module-level paths and output, and importing one
# into a packaging script would make a build failure look like an import error.
BUILD_STEPS = (
    ("build_cards", ["build_cards.py"]),
    ("plate", ["plate.py"]),
)

# only these get re-encoded. the mascot and the logo are vectors, already a few
# hundred bytes, and re-rendering them would be a waste of a build.
PHOTO_DIR = "img/editorial"
IMG_MAX_W = 1400
IMG_Q = 76

HEADERS = """\
# Cloudflare Pages headers.
#
# /css/* and /js/* are content-addressed by fingerprint_assets() - the file is
# named `styles.<sha256[:10]>.css`, so the URL changes whenever the bytes do.
# That makes `immutable` TRUE rather than aspirational: a year-long cache is safe
# precisely because a deploy cannot reuse a name whose content has changed.
#
# This used to serve stable names under the same header, which was a promise the
# build did not keep: `css/styles.css` changes on every stylesheet edit, so a
# browser that had seen it once would never ask again - not on reload, not on
# deploy, not for a year. A front-page redesign was built, every gate ran green,
# the folder was uploaded, and the site was unchanged, because the browser was
# reading a year-old copy off disk while the server had the new one. Same family
# as a `retrievable` citation with no URL: a header promising a property the
# build did not provide. Dropping the header made deploys arrive but made every
# reader re-fetch every asset; hashing the filename is what allows both.
#
# /img/* is deliberately NOT hashed - the photographs keep stable names, so they
# get a bounded cache that revalidates rather than a year. An image that changes
# can be a day late; a stylesheet that changes cannot, because a day of an
# unstyled page is a broken page.
/*.html
  Cache-Control: public, max-age=0, must-revalidate
/css/*
  Cache-Control: public, max-age=31536000, immutable
/js/*
  Cache-Control: public, max-age=31536000, immutable
/img/*
  Cache-Control: public, max-age=86400, stale-while-revalidate=604800

/*
  X-Content-Type-Options: nosniff
  Referrer-Policy: strict-origin-when-cross-origin
  X-Frame-Options: SAMEORIGIN
  Permissions-Policy: geolocation=(), microphone=(), camera=()
  Strict-Transport-Security: max-age=31536000; includeSubDomains
"""


def wanted(p: pathlib.Path):
    rel = p.relative_to(ROOT)
    # A backup of an earlier version is not a page. Nothing links to it, and
    # shipping it puts a second, stale copy of the site's front page at a live
    # URL - two versions of the same content, which is exactly what a reader or
    # a search engine cannot tell apart. It stays in the repository; it just
    # does not get deployed.
    if rel.name == "v1-oxalpha-backup.html":
        return False
    # requirements.txt is build metadata for the runner, not site content. It
    # is a .txt, so the extension filter would otherwise ship it at the root of
    # the deploy tree beside robots.txt.
    if rel.name == "requirements.txt":
        return False
    if any(part in EXCLUDE_NAMES for part in rel.parts):
        return False
    if rel.parts and rel.parts[0] in INCLUDE_DIRS:
        return True
    # ".html" must come out of "*.html" by dropping the asterisk and nothing
    # else. lstrip("*.") also ate the dot and matched nothing; comparing the raw
    # glob matched nothing either. Both versions produced a dist/ with no pages
    # in it, which is why the page-count guard below exists.
    return p.suffix.lower() in EXTS


def photos():
    d = ROOT / PHOTO_DIR
    if not d.is_dir():
        return []
    return sorted(p for p in d.iterdir()
                  if p.suffix.lower() in (".jpg", ".jpeg", ".png") and p.is_file())


def reencode(src: pathlib.Path) -> tuple[bytes, int, int]:
    """Return (webp bytes, new width, new height) for one cached photograph."""
    from PIL import Image
    im = Image.open(src)
    # a palette PNG with transparency has to become RGBA before it goes to
    # WebP, or Pillow warns and the alpha silently flattens onto black
    if im.mode in ("P", "LA") or (im.mode == "P" and "transparency" in im.info):
        im = im.convert("RGBA")
    elif im.mode != "RGB":
        im = im.convert("RGB")
    w0, h0 = im.size
    if im.width > IMG_MAX_W:
        im.thumbnail((IMG_MAX_W, 10_000), Image.LANCZOS)
    b = io.BytesIO()
    im.save(b, "WEBP", quality=IMG_Q, method=4)
    return b.getvalue(), im.width, im.height


def optimise():
    """Write the optimised photographs into dist/ and return {old: new}.

    The mapping is what the HTML rewrite uses, so the filenames and the
    references cannot drift apart. If a file comes out bigger as WebP the
    original is copied instead and the name is left alone, because paying more
    bytes for a worse-looking image is not a trade anyone wants."""
    from PIL import Image, features
    if not features.check("webp"):
        print("  Pillow has no webp support - copying photographs unchanged")
        return {}
    mapping, before, after, skipped = {}, 0, 0, 0
    outdir = DIST / PHOTO_DIR
    outdir.mkdir(parents=True, exist_ok=True)
    for src in photos():
        before += src.stat().st_size
        try:
            blob, w, h = reencode(src)
        except Exception as e:
            shutil.copy2(src, outdir / src.name)
            skipped += 1
            continue
        if len(blob) >= src.stat().st_size and src.suffix.lower() != ".png":
            # a tiny or already-efficient file; leave it be
            shutil.copy2(src, outdir / src.name)
            skipped += 1
            continue
        name = src.stem + ".webp"
        (outdir / name).write_bytes(blob)
        after += len(blob)
        mapping[src.name] = name
    print(f"  {len(mapping)} photographs -> webp at {IMG_MAX_W}px q{IMG_Q}: "
          f"{before/1024/1024:.1f} MB -> {after/1024/1024:.1f} MB"
          + (f", {skipped} left alone" if skipped else ""))
    return mapping


FINGERPRINT_DIRS = ("css", "js")
# .svg is excluded on purpose: the wordmark and the plates are generated and
# several are referenced from inside the stylesheet as well as from markup, so
# renaming those needs the stylesheet rewrite to run before this. CSS and JS
# are the assets that change on every meaningful edit, which is what made the
# one-year `immutable` header unkeepable.
FINGERPRINT_EXT = {".css", ".js"}


def fingerprint_assets():
    """Give every css and js file in dist a content-addressed name.

    `Cache-Control: immutable` on `/css/*` used to be a promise the build did
    not keep. `css/styles.css` is one stable filename that changes on every
    stylesheet edit, so `max-age=31536000, immutable` meant a browser that had
    seen it once would never ask again - not on reload, not on deploy, not for
    a year. A front page was redesigned, every gate ran green, the folder was
    uploaded, and the site was unchanged, because the browser was reading a
    year-old copy off disk while the server had the new one. Nothing in the repo
    could see it: the file on disk and the file in the cache had the same name.

    Removing the header made deploys arrive, but left every reader re-fetching
    every asset on every load. Hashing the filename makes the original claim
    true instead of retracting it: the name changes when the bytes change, so
    `immutable` is safe, a cache hit lasts a year, and a deploy reaches
    everybody at once because it is a different URL.

    Only dist/ is touched. The source tree keeps its stable names, so
    `build_cards.py`'s templates, `test_front_copy.py` and anything else that
    reads the source are unaffected.
    """
    import hashlib
    mapping = {}
    for sub in FINGERPRINT_DIRS:
        d = DIST / sub
        if not d.is_dir():
            continue
        for p in sorted(d.iterdir()):
            if not p.is_file() or p.suffix.lower() not in FINGERPRINT_EXT:
                continue
            digest = hashlib.sha256(p.read_bytes()).hexdigest()[:10]
            newname = f"{p.stem}.{digest}{p.suffix.lower()}"
            (d / newname).write_bytes(p.read_bytes())
            p.unlink()
            mapping[f"{sub}/{p.name}"] = f"{sub}/{newname}"
    if not mapping:
        print("  no css or js in dist to fingerprint")
        return {}

    # one pass, so a replacement can never be rewritten again by a later key
    pat = re.compile("|".join(re.escape(k) for k in
                             sorted(mapping, key=len, reverse=True)))
    n = 0
    for f in DIST.rglob("*.html"):
        t = f.read_text(encoding="utf-8", errors="replace")
        new = pat.sub(lambda m: mapping[m.group(0)], t)
        if new != t:
            f.write_text(new, encoding="utf-8")
            n += 1

    for old, new in sorted(mapping.items()):
        print(f"  {old} -> {new}")
    print(f"  content-addressed {len(mapping)} asset(s), repointed {n} pages")

    # The assertion that matters: nothing in dist may still ask for a name that
    # is no longer there. A silent miss here is a 404 on the stylesheet, which
    # renders as an unstyled page - and an unstyled page passes every layout
    # gate on this site, which is documented in verify_narrow.py's preconditions.
    stale = []
    for f in DIST.rglob("*.html"):
        t = f.read_text(encoding="utf-8", errors="replace")
        for old in mapping:
            if old in t:
                stale.append((f.relative_to(DIST).as_posix(), old))
    if stale:
        seen = sorted({s[1] for s in stale})
        sys.exit(f"refusing to ship: {len(stale)} reference(s) in dist still "
                 f"ask for a pre-hash name. Unrewritten: {seen[:4]} "
                 f"(first at {stale[0][0]})")
    return mapping


def rewrite_photos(mapping):
    """Point every reference at the optimised file.

    Without this the WebP files sit in dist/ doing nothing, because 269 pages
    still ask for the .jpg. This is the step that makes the saving real, and
    the link verifier at the end is what catches it if the two ever disagree.
    """
    if not mapping:
        return 0
    n = 0
    for f in DIST.rglob("*.html"):
        t = f.read_text(encoding="utf-8", errors="replace")
        orig = t
        for old, new in mapping.items():
            t = t.replace(f"{PHOTO_DIR}/{old}", f"{PHOTO_DIR}/{new}")
        if t != orig:
            f.write_text(t, encoding="utf-8")
            n += 1
    print(f"  repointed photographs in {n} pages")
    return n


def assemble(do_optimise=True):
    if DIST.exists():
        shutil.rmtree(DIST)
    DIST.mkdir(parents=True)
    n = 0
    mapping = {}
    if do_optimise:
        DIST.mkdir(parents=True, exist_ok=True)
        mapping = optimise()
    for p in ROOT.rglob("*"):
        if not p.is_file() or ".git" in p.parts:
            continue
        rel = p.relative_to(ROOT)
        if not wanted(p):
            continue
        if do_optimise and mapping and p.parent == ROOT / PHOTO_DIR \
                and p.name in mapping:
            continue                      # already written as webp
        dst = DIST / rel
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(p, dst)
        n += 1
    if do_optimise:
        n += len(mapping) - sum(1 for p in (DIST / PHOTO_DIR).iterdir()
                                if p.suffix.lower() != ".webp")
    rewrite_photos(mapping)
    fingerprint_assets()
    (DIST / "_headers").write_text(HEADERS, encoding="utf-8")
    n += 1
    # /e/<id> - a short path to an encyclopedia entry, for video end cards.
    #
    # The episodes already ended on "Entry 53 of 175. ELIZA" but pointed at a
    # bare domain, so a viewer who wanted the entry had to guess the path. A
    # full /encyclopedia/<id>.html is unreadable burned into a 1080x1920 frame,
    # and a QR code on a phone is worse. /e/eliza is four characters and goes
    # straight there.
    #
    # Generated for every entry rather than only the three with episodes, so a
    # future episode needs no deploy change to get a working end card.
    enc_path = ROOT / "data" / "encyclopedia.json"
    lines = [
        "# Single-page-ish: serve directory indexes the way the site is built.",
        "/index.html  /  301",
        "# The ten categories were called 'aisles' until 2026-09-30. The word was",
        "# doing no work and the nav already said SECTIONS, so the URL followed.",
        "/aisle/       /sections/  301",
        "/aisle/*      /sections/:splat  301",
        "# Short path to an encyclopedia entry, for video end cards and citations.",
    ]
    if enc_path.is_file():
        entries = json.loads(enc_path.read_text(encoding="utf-8"))["entries"]
        for e in sorted(entries, key=lambda x: x["id"]):
            lines.append(f"/e/{e['id']}  /encyclopedia/{e['id']}.html  301")

    # Renamed slugs.
    #
    # A slug is a published assertion, not a label. `vid-summit-bars-fans` said
    # in the URL that a named conference banned fans, which it does not, so the
    # claim came down and the URL went with it. The old address still has to
    # work for anyone who linked to it or read it in a feed, and the record of
    # why it moved lives in data/shop.json under `_retired_sources` - so the
    # redirect is generated from that rather than hand-maintained here, and a
    # retired slug with no redirect is a broken link rather than a stale habit.
    shop_path = ROOT / "data" / "shop.json"
    if shop_path.is_file():
        shop = json.loads(shop_path.read_text(encoding="utf-8"))
        live = {c["slug"] for c in shop.get("cards", [])}
        for r in shop.get("_retired_sources", []):
            old, new = r.get("slug"), r.get("new_slug")
            if old and new and new in live:
                lines.append(f"/radar/{old}.html  /radar/{new}.html  301")
            elif old and new:
                print(f"  WARN retired slug {old!r} points at {new!r}, "
                      f"which is not a live card - the redirect would 404")
    (DIST / "_redirects").write_text("\n".join(lines) + "\n", encoding="utf-8")
    n += 1
    return n


def verify():
    """Every local link in dist must resolve inside dist.

    Three things this gets right that a naive regex does not:

    - <script> and <style> bodies are removed first. The atlas and the quiz
      build their HTML in template literals, so a raw scan of the file finds
      things like "' + esc(s.url) + '" and reports them as broken links.
    - ".." is folded one segment at a time, the way a browser does.
    - A path that walks above dist is CLAMPED to dist, not called broken,
      because that is what a browser does at a domain root. Those are counted
      separately as `clamped`, because they are legal but they are also a
      latent bug: they break the moment the site is served from a subpath, and
      a static-file host has nothing above the deployed folder to clamp to.
    """
    pages = list(DIST.rglob("*.html"))
    broken, clamped, external = [], 0, 0
    for f in pages:
        t = f.read_text(encoding="utf-8", errors="replace")
        t = re.sub(r"<script\b[^>]*>.*?</script>", " ", t, flags=re.S | re.I)
        t = re.sub(r"<style\b[^>]*>.*?</style>", " ", t, flags=re.S | re.I)
        for m in re.findall(r'(?:src|href)="([^"#?]+)"', t):
            u = urllib.parse.unquote(m.strip())
            if not u:
                continue
            if u.startswith(("http://", "https://", "mailto:", "data:", "//")):
                external += 1
                continue
            segs = []
            for seg in (f.parent.relative_to(DIST) / u).parts:
                if seg == ".":
                    continue
                if seg == "..":
                    if segs:
                        segs.pop()
                    else:
                        clamped += 1          # a browser clamps here
                else:
                    segs.append(seg)
            target = DIST.joinpath(*segs)
            if target.is_dir():
                target = target / "index.html"
            if not target.exists():
                broken.append((f.relative_to(DIST), m, "missing"))
    return pages, broken, clamped, external


def build_site():
    """Regenerate every page and plate before dist/ is assembled.

    The date-seeded features are computed from the UTC date at build time, so
    there is no way to make yesterday's HTML current by copying it. The only
    correct move is to run the generator, and the failure this prevents is
    silent: a stale tree has no broken links, no missing assets and no failing
    gate, because it is a perfectly valid copy of the wrong day.
    """
    for name, argv in BUILD_STEPS:
        print(f"rebuilding: {name}")
        rc = subprocess.run(
            [sys.executable, "-X", "utf8", str(ROOT / "tools" / argv[0])] + argv[1:],
            cwd=ROOT,
        ).returncode
        if rc:
            raise SystemExit(
                f"{name} failed with exit {rc}; dist/ was left untouched")
    print()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--check-only", action="store_true")
    ap.add_argument("--no-build", action="store_true",
                    help="package the pages already on disk instead of "
                         "rebuilding them first")
    ap.add_argument("--no-optimise", action="store_true",
                    help="copy the photographs as they are, no webp")
    a = ap.parse_args()
    if a.check_only:
        # --check-only exists to inspect a tree something else produced. It
        # deliberately does not build, or it would be checking its own work.
        n = sum(1 for p in DIST.rglob("*") if p.is_file())
        print(f"checking {n} files in {DIST}")
    else:
        if a.no_build:
            print("packaging the existing pages (--no-build)\n")
        else:
            build_site()
        n = assemble(not a.no_optimise)
        print(f"assembled {n} files -> {DIST}")

    pages, broken, clamped, external = verify()
    size = sum(p.stat().st_size for p in DIST.rglob("*") if p.is_file())
    print(f"{len(pages)} pages, {size/1024/1024:.1f} MB, {external} external links")
    # A link check that passes on an empty directory is worse than no link
    # check: it reports success while the folder has nothing in it. The first
    # version of this script did exactly that, because the include filter was
    # comparing ".html" against "html" and copying no pages at all.
    if len(pages) < 50:
        raise SystemExit(f"only {len(pages)} pages in dist/ - that is not a "
                         "website, and the link check just agreed with it")
    if broken:
        print(f"\n{len(broken)} BROKEN LOCAL LINKS:")
        for f, u, why in broken[:30]:
            print(f"  {f}  ->  {u}  ({why})")
        raise SystemExit("dist/ is not safe to upload")
    if clamped:
        print(f"\n{clamped} links walk above the deployed root.")
        print("  A browser clamps them, so the site works at a domain root.")
        print("  They will break if the site is ever served from a subpath.")
    if n > LIMIT:
        raise SystemExit(f"{n} files is over the {LIMIT}-file direct-upload limit; "
                         "use wrangler or check what is being copied")
    print(f"every local link resolves, and {n} is under the {LIMIT}-file limit")
    print(f"\nupload the {DIST.name}/ folder, not the repository")


if __name__ == "__main__":
    main()




