#!/usr/bin/env python3
"""
build_deploy.py - assemble dist/ and prove it holds together.

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

WHAT IS IN, AND WHY
    *.html      every page, including the 177 encyclopedia entries
    css/ js/    two stylesheets and one script
    img/        95 cached photographs and 16 svg
    *.txt *.xml robots.txt, sitemap.xml, radar.xml - radar.xml is linked from
                all 260 pages as the autodiscovery feed, so it is load-bearing
                and not a build artefact

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
  python tools/build_deploy.py --check-only
  python tools/build_deploy.py --no-optimise
"""
import pathlib, shutil, sys, re, urllib.parse, argparse, io, json

ROOT = pathlib.Path(__file__).resolve().parent.parent
DIST = ROOT / "dist"

INCLUDE_GLOBS = ["*.html", "*.css", "*.js", "*.txt", "*.xml", "*.svg", "*.jpg",
                 "*.png", "*.webp", "*.ico", "*.woff2"]
INCLUDE_DIRS = ["css", "js", "img"]
# ".html" comes out of "*.html" by dropping the asterisk and nothing else.
# lstrip("*.") also ate the dot and matched nothing, which put a dist/ with 116
# files and no pages in it - see the page-count guard in main().
EXTS = {g.lstrip("*") for g in INCLUDE_GLOBS}
# `episode` is a BUILD WORKING DIRECTORY, not part of the site. Three episodes
# of 1080x1920 frames and narration took the deploy zip from 8.5MB to 71MB and
# the verifier refused it, which is the check earning its keep: nothing about a
# 71MB upload looks wrong until something refuses it.
EXCLUDE_NAMES = {".git", "__pycache__", "tools", "data", "node_modules", "dist",
                  ".github", "audit_out", "__dist__", "episode"}
LIMIT = 1000

# only these get re-encoded. the mascot and the logo are vectors, already a few
# hundred bytes, and re-rendering them would be a waste of a build.
PHOTO_DIR = "img/editorial"
IMG_MAX_W = 1400
IMG_Q = 76

HEADERS = """\
# Cloudflare Pages headers. Static assets are content-addressed by the build in
# spirit and never change under a given name, so they get a long cache; HTML
# must not, or a deploy would never reach anybody.
/css/*
  Cache-Control: public, max-age=31536000, immutable
/js/*
  Cache-Control: public, max-age=31536000, immutable
/img/*
  Cache-Control: public, max-age=31536000, immutable
/*.html
  Cache-Control: public, max-age=0, must-revalidate

/*
  X-Content-Type-Options: nosniff
  Referrer-Policy: strict-origin-when-cross-origin
  X-Frame-Options: SAMEORIGIN
  Permissions-Policy: geolocation=(), microphone=(), camera=()
  Strict-Transport-Security: max-age=31536000; includeSubDomains
"""


def wanted(p: pathlib.Path):
    rel = p.relative_to(ROOT)
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


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--check-only", action="store_true")
    ap.add_argument("--no-optimise", action="store_true",
                    help="copy the photographs as they are, no webp")
    a = ap.parse_args()
    if not a.check_only:
        n = assemble(not a.no_optimise)
        print(f"assembled {n} files -> {DIST}")
    else:
        n = sum(1 for p in DIST.rglob("*") if p.is_file())
        print(f"checking {n} files in {DIST}")

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




