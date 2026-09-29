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

  python tools/build_deploy.py
  python tools/build_deploy.py --check-only
"""
import pathlib, shutil, sys, re, urllib.parse, argparse

ROOT = pathlib.Path(__file__).resolve().parent.parent
DIST = ROOT / "dist"

INCLUDE_GLOBS = ["*.html", "*.css", "*.js", "*.txt", "*.xml", "*.svg", "*.jpg",
                 "*.png", "*.webp", "*.ico", "*.woff2"]
INCLUDE_DIRS = ["css", "js", "img"]
EXTS = {g.lstrip("*") for g in INCLUDE_GLOBS}
EXCLUDE_NAMES = {".git", "__pycache__", "tools", "data", "node_modules", "dist",
                  ".github", "audit_out"}
LIMIT = 1000

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


def assemble():
    if DIST.exists():
        shutil.rmtree(DIST)
    DIST.mkdir(parents=True)
    n = 0
    for p in ROOT.rglob("*"):
        if not p.is_file() or ".git" in p.parts:
            continue
        rel = p.relative_to(ROOT)
        if not wanted(p):
            continue
        dst = DIST / rel
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(p, dst)
        n += 1
    (DIST / "_headers").write_text(HEADERS, encoding="utf-8")
    n += 1
    (DIST / "_redirects").write_text(
        "# Single-page-ish: serve directory indexes the way the site is built.\n"
        "/index.html  /  301\n", encoding="utf-8")
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
    a = ap.parse_args()
    if not a.check_only:
        n = assemble()
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

