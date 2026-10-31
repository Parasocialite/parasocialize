#!/usr/bin/env python3
import argparse
import hashlib
import html
import io
import json
import math
import re
import time
import urllib.parse
from datetime import date
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageOps

import images

ROOT = Path(__file__).resolve().parent.parent
SEED = ROOT / "data" / "distilled_sources.json"
CATALOG = ROOT / "data" / "images.json"
OUT = ROOT / "img" / "distilled"
SRC = ROOT / "research-cache" / "distilled-source"
SHEET = ROOT / "research-cache" / "distilled-contact.jpg"
FREE = {"public domain", "pd", "cc0", "cc-zero", "cc zero", "public domain mark"}


def die(message):
    raise SystemExit(f"distill_images: {message}")


def sha(data):
    return hashlib.sha256(data).hexdigest()


def text_value(value):
    raw = html.unescape(str(value or ""))
    raw = re.sub(r"<br\s*/?>", "; ", raw, flags=re.I)
    raw = images.strip_html(raw)
    return re.sub(r"\s+", " ", raw).strip()


def clean_author(value):
    s = text_value(value)
    s = re.sub(r"^(Author|Artist)\s+", "", s, flags=re.I)
    s = re.sub(r"\s+(Author|Artist)\s+", "; ", s, flags=re.I)
    s = re.sub(r"\s*;\s*", "; ", s).strip(" ;")
    return s


def licence_ok(value):
    s = re.sub(r"\s+", " ", (value or "").lower()).strip()
    return s in FREE or s.startswith("pd-") or s.startswith("pd ")


def fetch_json(url):
    last = None
    for attempt in range(3):
        try:
            return images.http(url, 60)
        except Exception as exc:
            last = exc
            if attempt < 2:
                time.sleep(1 + attempt)
    raise last


def fetch_bytes(url):
    last = None
    for attempt in range(3):
        try:
            return images.http(url, 90, binary=True)
        except Exception as exc:
            last = exc
            if attempt < 2:
                time.sleep(1 + attempt)
    raise last


def commons(title):
    query = (
        images.COMMONS
        + "?action=query&format=json&prop=imageinfo"
        + "&iiprop=url|size|extmetadata&titles="
        + urllib.parse.quote(title)
    )
    data = fetch_json(query)
    pages = (data.get("query") or {}).get("pages") or {}
    page = next(iter(pages.values()), None)
    if not page or "missing" in page:
        die(f"Commons page not found: {title}")
    info = (page.get("imageinfo") or [None])[0]
    if not info:
        die(f"Commons has no imageinfo for: {title}")
    ext = info.get("extmetadata") or {}

    def meta(name):
        return text_value((ext.get(name) or {}).get("value"))

    author = clean_author(meta("Artist"))
    licence = meta("LicenseShortName") or meta("License")
    source_date = meta("DateTimeOriginal") or meta("DateTime")
    source_date = re.sub(r"\s*date\s+QS:.*$", "", source_date, flags=re.I).strip()
    source_url = info.get("url") or ""
    parts = urllib.parse.urlsplit(source_url)
    source_url = urllib.parse.urlunsplit((parts.scheme, parts.netloc, parts.path, "", ""))
    return {
        "title": page.get("title") or title,
        "url": source_url,
        "page": info.get("descriptionurl") or "",
        "author": author or "Wikimedia contributor",
        "licence": licence,
        "date": source_date,
        "width": int(info.get("width") or 0),
        "height": int(info.get("height") or 0),
    }


def source_path(slug, url):
    suffix = Path(urllib.parse.urlsplit(url).path).suffix.lower()
    if suffix not in {".jpg", ".jpeg", ".png"}:
        suffix = ".jpg"
    return SRC / f"{slug}{suffix}"


def source_blob(spec, info):
    SRC.mkdir(parents=True, exist_ok=True)
    path = source_path(spec["slug"], info["url"])
    if path.exists():
        blob = path.read_bytes()
    else:
        blob = fetch_bytes(info["url"])
        path.write_bytes(blob)
    return blob, sha(blob)


def crop_16x9(im, focus):
    w, h = im.size
    target = 16 / 9
    fx, fy = focus
    if w / h > target:
        cw, ch = int(round(h * target)), h
        x0, y0 = int(round((w - cw) * fx)), 0
    else:
        cw, ch = w, int(round(w / target))
        x0, y0 = 0, int(round((h - ch) * fy))
    x0 = max(0, min(w - cw, x0))
    y0 = max(0, min(h - ch, y0))
    return im.crop((x0, y0, x0 + cw, y0 + ch))


def distill(im, spec, style):
    palette = [tuple(int(c[i : i + 2], 16) for i in (1, 3, 5)) for c in style["palette"]]
    im = crop_16x9(im, spec["focus"])
    im = im.resize((style["width"], style["height"]), Image.Resampling.LANCZOS)
    im = ImageOps.grayscale(im)
    im = ImageOps.autocontrast(im, cutoff=style["autocontrast"])
    im = im.filter(ImageFilter.MedianFilter(style["median_filter"]))
    arr = np.asarray(im, dtype=np.float32) / 255.0
    arr = np.clip(arr, 0, 1) ** spec["gamma"]
    arr = np.clip(arr * 255, 0, 255).astype(np.uint8)
    index = np.digitize(arr, style["thresholds"]).clip(0, len(palette) - 1)
    out = np.array(palette, dtype=np.uint8)[index]
    rng = np.random.default_rng(spec["seed"])
    h, w = out.shape[:2]
    low, high = style["band_height"]
    shift_low, shift_high = style["band_shift"]
    for _ in range(style["glitch_bands"]):
        bh = int(rng.integers(low, high + 1))
        y0 = int(rng.integers(int(h * 0.10), h - bh))
        shift = int(rng.integers(shift_low, shift_high + 1))
        if rng.random() < 0.5:
            shift = -shift
        xs = np.clip(np.arange(w) - shift, 0, w - 1)
        out[y0 : y0 + bh] = out[y0 : y0 + bh][:, xs]
    return Image.fromarray(out, "RGB")


def recipe_hash(spec, style, digest):
    recipe = {
        "source_sha256": digest,
        "focus": spec["focus"],
        "gamma": spec["gamma"],
        "seed": spec["seed"],
        "style": style,
    }
    raw = json.dumps(recipe, sort_keys=True, separators=(",", ":")).encode()
    return sha(raw)[:6]


def validate(spec):
    for key in ("slug", "for", "title", "focus", "gamma", "seed", "caption"):
        if key not in spec:
            die(f"source is missing `{key}`")
    if len(spec["focus"]) != 2 or any(not 0 <= float(v) <= 1 for v in spec["focus"]):
        die(f"{spec['slug']}: focus must be two numbers from 0 to 1")
    if float(spec["gamma"]) <= 0:
        die(f"{spec['slug']}: gamma must be positive")
    if int(spec["seed"]) < 0:
        die(f"{spec['slug']}: seed must be non-negative")
    if not spec["caption"].strip():
        die(f"{spec['slug']}: caption is empty")


def make_sheet(items):
    cols, cell_w, cell_h, pad, label_h = 2, 370, 208, 12, 18
    rows = math.ceil(len(items) / cols)
    width = cols * cell_w + (cols + 1) * pad
    height = rows * (cell_h + label_h) + (rows + 1) * pad
    sheet = Image.new("RGB", (width, height), (241, 231, 212))
    draw = ImageDraw.Draw(sheet)
    for i, (spec, path) in enumerate(items):
        with Image.open(path) as im:
            tile = im.convert("RGB")
            tile.thumbnail((cell_w, cell_h), Image.Resampling.LANCZOS)
        x = pad + (i % cols) * (cell_w + pad)
        y = pad + (i // cols) * (cell_h + label_h + pad)
        sheet.paste(tile, (x, y))
        draw.text((x, y + cell_h + 2), spec["slug"], fill=(14, 8, 4))
    SHEET.parent.mkdir(parents=True, exist_ok=True)
    sheet.save(SHEET, "JPEG", quality=90)
    print(f"sheet: {SHEET.relative_to(ROOT)}")


def build(spec, info, style):
    if not licence_ok(info["licence"]):
        die(f"{spec['slug']}: licence `{info['licence']}` is not public domain or CC0")
    if info["width"] < 400 or info["height"] < 400:
        die(f"{spec['slug']}: source is too small ({info['width']}x{info['height']})")
    blob, digest = source_blob(spec, info)
    try:
        with Image.open(io.BytesIO(blob)) as raw:
            im = ImageOps.exif_transpose(raw).convert("RGB")
    except Exception as exc:
        die(f"{spec['slug']}: cannot decode source: {exc}")
    if im.width < 400 or im.height < 400:
        die(f"{spec['slug']}: decoded source is too small")
    OUT.mkdir(parents=True, exist_ok=True)
    name = f"{spec['slug']}-{digest[:10]}-{recipe_hash(spec, style, digest)}.png"
    path = OUT / name
    for old in OUT.glob(f"{spec['slug']}-*.png"):
        if old.name != name:
            old.unlink()
    distilled = distill(im, spec, style)
    distilled.save(path, "PNG", optimize=True)
    output_digest = sha(path.read_bytes())
    author = clean_author(info["author"])
    credit = f"{author} / Wikimedia Commons" if author else "Wikimedia Commons"
    src = {
        "title": images.pretty(info["title"]),
        "author": author,
        "licence": info["licence"],
        "credit": credit,
        "page": info["page"],
        "source_url": info["url"],
    }
    if info.get("date"):
        src["date"] = info["date"]
    record = {
        "slug": spec["slug"],
        "for": spec["for"],
        "caption": spec["caption"].strip(),
        "kind": "illustrative",
        "style": "distilled",
        "note": (
            "DISTILLED from a public-domain or CC0 Commons source with the "
            "deterministic recipe in `transform`. The frame is a stylized "
            "derivative; `kind: illustrative` means the pinned source record, "
            "not the pixels, establishes identity and date."
        ),
        "local": path.relative_to(ROOT).as_posix(),
        "src": src,
        "transform": {
            "source_title": info["title"],
            "source_page": info["page"],
            "source_sha256": digest,
            "output_sha256": output_digest,
            "width": style["width"],
            "height": style["height"],
            "crop": style["crop"],
            "focus": spec["focus"],
            "gamma": spec["gamma"],
            "seed": spec["seed"],
            "autocontrast": style["autocontrast"],
            "median_filter": style["median_filter"],
            "tones": style["tones"],
            "palette": style["palette"],
            "thresholds": style["thresholds"],
            "glitch_bands": style["glitch_bands"],
            "band_height": style["band_height"],
            "band_shift": style["band_shift"],
            "source_width": info["width"],
            "source_height": info["height"],
        },
        "cached": date.today().isoformat(),
        "looked": spec.get("looked", ""),
        "look_reason": spec.get("look_reason", ""),
    }
    print(
        f"{spec['slug']}: {path.name} | {info['width']}x{info['height']} "
        f"| {info['licence']} | {author}"
    )
    return record


def merge(records):
    catalog = json.loads(CATALOG.read_text(encoding="utf-8"))
    entries = catalog.get("items")
    if not isinstance(entries, list):
        die("data/images.json has no `items` list")
    keys = list(catalog.keys())
    before = len(entries)
    replaced = added = 0
    old_locals = []
    for record in records:
        index = next(
            (
                i
                for i, item in enumerate(entries)
                if item.get("for") == record["for"] and item.get("slug") == record["slug"]
            ),
            None,
        )
        if index is None:
            entries.append(record)
            added += 1
        else:
            old = entries[index]
            if old.get("local") and old["local"] != record["local"]:
                old_locals.append(old["local"])
            entries[index] = record
            replaced += 1
    if len(entries) != before + added:
        die("image count changed unexpectedly during merge")
    if list(catalog.keys()) != keys:
        die("top-level image schema changed unexpectedly")
    note = catalog.get("_note", "")
    if "style: distilled" not in note:
        catalog["_note"] = (
            note.rstrip()
            + " Distilled records carry `style: distilled` and a `transform` recipe; "
            + "their `kind` is `illustrative` because the pinned source record, not the frame, "
            + "establishes identity and date."
        )
    CATALOG.write_text(json.dumps(catalog, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"images.json: {replaced} replaced, {added} added, {len(entries)} total")
    for old in old_locals:
        print(f"old file retained: {old}")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--install", action="store_true")
    parser.add_argument("--sheet", action="store_true")
    parser.add_argument("--only", action="append", default=[])
    args = parser.parse_args()

    seed = json.loads(SEED.read_text(encoding="utf-8"))
    style = seed["style"]
    sources = seed["sources"]
    seen = set()
    for spec in sources:
        validate(spec)
        if spec["slug"] in seen:
            die(f"duplicate slug: {spec['slug']}")
        seen.add(spec["slug"])
    if args.only:
        missing = sorted(set(args.only) - seen)
        if missing:
            die(f"unknown slug(s): {', '.join(missing)}")
        sources = [spec for spec in sources if spec["slug"] in args.only]

    items = []
    records = []
    for spec in sources:
        info = commons(spec["title"])
        record = build(spec, info, style)
        items.append((spec, ROOT / record["local"]))
        records.append(record)

    if args.sheet:
        make_sheet(items)

    if args.install:
        for spec, record in zip(sources, records):
            if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", record.get("looked", "")):
                die(f"{spec['slug']}: `looked` must be set before install")
            if len(record.get("look_reason", "").strip()) < 60:
                die(f"{spec['slug']}: `look_reason` is too short before install")
        merge(records)


if __name__ == "__main__":
    main()
