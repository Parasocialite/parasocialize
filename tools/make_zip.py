"""Zip dist/ for upload, reproducibly.

This was being done by hand, which is how the last archive ended up five hours
stale and missing the entire masthead change: nothing recorded that the upload
artifact had to be rebuilt after a commit, so nothing prompted it. The site
builds from tools/, so the deploy artifact should too.

Two details that are easy to get wrong and expensive to debug on Pages:

  - entries sit at the ROOT of the archive. Nesting them under dist/ produces an
    upload that looks successful and serves 404s.
  - entries are added in sorted order with a fixed timestamp, so two builds of
    the same tree produce byte-identical archives and a changed hash means
    something actually changed.

The tree is hashed and printed so the archive can be tied to a commit.
"""
from __future__ import annotations

import hashlib
import pathlib
import sys
import zipfile

DIST = pathlib.Path("dist")
# a fixed mtime keeps the archive deterministic; without it every build differs
STAMP = (2026, 1, 1, 0, 0, 0)

# Pages serves index.html at /, and these are load-bearing for the site chrome.
REQUIRED_AT_ROOT = ["index.html", "css/styles.css", "css/mascot.css"]


def main():
    out = pathlib.Path(sys.argv[1] if len(sys.argv) > 1
                       else pathlib.Path.home() / "Desktop" / "parasocialize-SITE.zip")
    if not DIST.is_dir():
        sys.exit(f"  {DIST}/ is missing - run tools/build_deploy.py first")

    files = sorted(p for p in DIST.rglob("*") if p.is_file())
    if not files:
        sys.exit(f"  {DIST}/ is empty - run tools/build_deploy.py first")

    missing = [r for r in REQUIRED_AT_ROOT if not (DIST / r).is_file()]
    if missing:
        sys.exit(f"  {DIST}/ is missing {missing} - refusing to package a broken tree")

    out.parent.mkdir(parents=True, exist_ok=True)
    h = hashlib.sha256()
    with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED, compresslevel=9) as z:
        for p in files:
            rel = p.relative_to(DIST).as_posix()   # root of the archive, not dist/
            data = p.read_bytes()
            h.update(rel.encode())
            h.update(data)
            zi = zipfile.ZipInfo(rel, date_time=STAMP)
            zi.compress_type = zipfile.ZIP_DEFLATED
            zi.external_attr = 0o644 << 16
            z.writestr(zi, data)

    with zipfile.ZipFile(out) as z:
        names = z.namelist()
        bad = z.testzip()
        rootless = [n for n in names if "/" in n and n.split("/")[0] in ("dist", "parasocialize")]

    print(f"  {len(files)} files -> {out}")
    print(f"  {out.stat().st_size/1e6:.2f} MB   tree sha256 {h.hexdigest()[:16]}")
    print(f"  index.html at root: {'index.html' in names}")
    print(f"  nested dist/ entries: {len(rootless)}")
    print(f"  archive integrity: {'ok' if bad is None else f'CORRUPT at {bad}'}")

    anim = [n for n in names if "iyi-hero" in n]
    for n in anim:
        print(f"  carries {n}")


if __name__ == "__main__":
    main()
