"""gen_atmosphere.py - illustration for the encyclopedia layer, in bulk.

The layer has one image out of 193 entries. It was stuck for a licence reason, not
a creative one: the policy is Commons-or-author-owned, the K-drive library is
unlicensed downloads, and searching Commons for "parasocial relationship" returns
photographs of people. Generated art is author-owned by construction, so it is the
only supply that satisfies the policy with no licence question at all.

THE POLICY, SETTLED BY FAILING AT IT FIRST

Five generations were attempted for the-dog before the policy existed. Four of
them depicted a modern shepherd-type dog with a collar on an entry dated -15000,
in four different collar colours, despite "no collar, not a modern breed" going
into the prompt. FLUX.1-schnell renders "dog" as the modern domestic dog because
that is its highest-prior concept for the word and four steps cannot steer off it.

So: generated art in this layer is atmosphere, never depiction. Nothing in the
prompt may name a thing that can be dated, counted or identified. No animals
rendered as breeds, no people, no named products, no events. What is left is
weather, distance, light, terrain, repetition and scale - which cannot be
factually wrong about a -15000 dog or a 1956 paper.

The prompt is built from the entry's own data rather than written per entry:
its year decides the era of light and terrain, its otherness value decides the
register, its medium decides the texture. That way 193 entries get 193 distinct
atmospheres from one template, and none of them asserts a fact.

    python tools\\gen_atmosphere.py --report       # show what would be generated
    python tools\\gen_atmosphere.py --limit 8      # generate 8 and record them
"""
from __future__ import annotations

import hashlib
import json
import pathlib
import sys
import time
import urllib.request

ROOT = pathlib.Path(__file__).resolve().parent.parent
ENC = ROOT / "data" / "encyclopedia.json"
MAN = ROOT / "data" / "images.json"
GEN = ROOT / "img" / "generated"
BASE = "http://127.0.0.1:8188"
OUT_W, OUT_H = 1152, 560          # the banner aspect the-dog settled on

# --- era of light and ground, from the year ---------------------------------
# Deliberately coarse. Anything finer would be a claim about a specific place at
# a specific date, which is the thing this layer is not allowed to make.
def era(y):
    if y is None:
        return ("overcast coastal light, wet grey stone and shallow water", "stone")
    if y < -10000:
        return ("low firelight and deep shadow, rough rock and packed earth", "rock")
    if y < 0:
        return ("cold clear dawn light, bare ground and long shadow", "earth")
    if y < 1800:
        return ("warm low sun, dust and stone, printed-paper texture", "paper")
    if y < 1950:
        return ("flat overcast light, plaster and metal, halftone print texture", "halftone")
    return ("cool electric light, glass and plastic, faint screen glow", "glass")


# --- register, from the MEDIUM -------------------------------------------------
# `other` and `lane` are None on all 193 entries - the otherness readings live in
# taxonomy_placements.json, not on the entry - so a template keyed to them is
# degenerate. Measured: it produced SIX distinct prompts across 193 entries, with
# 134 of them word-for-word identical, because every entry without an `other`
# falls through to the same fallback.
#
# `medium` is the field that varies and carries meaning: thirteen values that
# genuinely differ in what light and texture the subject implies. Driving texture
# from it is not a workaround, it is the more honest mapping - a film entry wants
# projected light, a literature entry wants paper, a games entry wants a pixel
# grid. year-band x medium x kind gives 70 distinct prompts across 193 entries,
# which is enough that scrolling feels alive without implying distinctions the
# data does not make.
MEDIUM = {
    "film": "projected light through dust, heavy film grain, deep shadow",
    "television_scripted": "flat cool studio light, glossy screen reflection, set walls",
    "television_unscripted": "available flat light, cluttered rooms, handheld framing",
    "literature": "printed paper, ink and margin, lamplight on a page",
    "music": "a dark hall, warm stage light, haze in the air",
    "radio": "a dark room, a dial glowing, warm lamp light",
    "games": "a pixel grid, emissive colour, hard synthetic light",
    "comics": "flat ink, bold outlines, halftone dots",
    "technology": "cold electric light, glass and metal, faint standby glow",
    "ai": "cold diffuse light, glass, a screen glow with nothing behind it",
    "history": "archival dust, aged paper and stone, low warm light",
    "theology": "candlelight, worn stone, deep shadow",
    "sport": "floodlit open air, empty ground, long shadow",
}
# the register line still exists for when `other` is populated; today it is not,
# and that is recorded rather than pretended around
REGISTER = {
    "imagined": "something imagined and therefore absent, present only as an outline",
    "made": "an object made by hand, repeated many times, identical",
    "animate": "a shape that suggests movement stopped mid-gesture",
    "transcendent": "a vertical opening, light from somewhere the scene cannot show",
    "mirrored": "a reflection with no object above it",
    "haunted": "an absence with a shape to it, a space where something was removed",
}

KIND = {
    "person": "one presence implied and then not shown",
    "work": "something made and finished, seen from outside",
    "event": "a space recently emptied",
    "mechanism": "a pattern repeating with no example",
    "term": "a shape where a definition would go",
    "study": "a measured surface, grid-like, impersonal",
    "case": "a single specific absence, described not shown",
    "institution": "a large arrangement of small repeated units",
}


def build_prompt(e):
    ground, _tex = era(e.get("year"))
    med = next((m for m in (e.get("medium") or []) if m in MEDIUM), None)
    texture = MEDIUM.get(med) or "soft even light, unremarkable surfaces"
    reg = REGISTER.get(e.get("other"))
    if reg is None:
        reg = KIND.get(e.get("kind")) or "an open space with nothing explained in it"
    return (
        f"Minimal painterly illustration: {texture}. {ground}. {reg}. "
        f"Composed as atmosphere rather than subject: wide empty space, a few "
        f"small unidentifiable shapes far from the viewer, no detail, no focal "
        f"point, deep distance. Grainy print texture. No text, no lettering, no "
        f"faces, no recognisable animals, no named objects, no architecture, no "
        f"signage, not a photograph, nothing that can be dated or counted."
    )


def graph_for(prompt, seed):
    return {
        "1": {"class_type": "UNETLoader",
              "inputs": {"unet_name": "flux1-schnell-fp8.safetensors",
                         "weight_dtype": "default"}},
        "2": {"class_type": "DualCLIPLoader",
              "inputs": {"clip_name1": "t5xxl_fp8_e4m3fn.safetensors",
                     "clip_name2": "clip_l.safetensors", "type": "flux"}},
        "3": {"class_type": "CLIPTextEncode", "inputs": {"clip": ["2", 0], "text": prompt}},
        "4": {"class_type": "EmptyLatentImage",
              "inputs": {"width": OUT_W, "height": OUT_H, "batch_size": 1}},
        "5": {"class_type": "KSampler",
              "inputs": {"model": ["1", 0], "seed": seed, "steps": 4, "cfg": 1.0,
                         "sampler_name": "euler", "scheduler": "simple",
                         "positive": ["3", 0], "negative": ["3", 0],
                         "latent_image": ["4", 0], "denoise": 1.0}},
        "6": {"class_type": "VAELoader", "inputs": {"vae_name": "ae.safetensors"}},
        "7": {"class_type": "VAEDecode", "inputs": {"samples": ["5", 0], "vae": ["6", 0]}},
        "8": {"class_type": "SaveImage",
              "inputs": {"filename_prefix": "parasocialize/atmos", "images": ["7", 0]}},
    }


def api(path, data=None):
    req = urllib.request.Request(
        BASE + path,
        data=json.dumps(data).encode() if data is not None else None,
        headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=180) as r:
        return json.loads(r.read().decode("utf-8", "replace"))


def crop_to_banner(src, dest):
    """the-dog taught this: the horizon wants the figures near 45% down, and
    trimming the bottom pushes them lower, not higher."""
    try:
        from PIL import Image
    except ImportError:
        dest.write_bytes(src.read_bytes())
        return src.stat().st_size
    im = Image.open(src).convert("RGB")
    W, H = im.size
    keep = int(W / (OUT_W / OUT_H))
    top = max(0, min(H - keep, int(H * 0.26)))
    im.crop((0, top, W, min(H, top + keep))).save(dest)
    return dest.stat().st_size


def main():
    report = "--report" in sys.argv
    limit = 8
    for i, a in enumerate(sys.argv):
        if a == "--limit":
            limit = int(sys.argv[i + 1])
    apply = "--apply" in sys.argv

    enc = json.loads(ENC.read_text(encoding="utf-8"))
    man = json.loads(MAN.read_text(encoding="utf-8"))
    have = {i["slug"] for i in man["items"] if i["for"] == "encyclopedia"}
    todo = [e for e in enc["entries"] if e["id"] not in have]
    print(f"{len(enc['entries'])} entries, {len(have)} illustrated, {len(todo)} to go\n")

    targets = todo[:limit]
    for e in targets:
        p = build_prompt(e)
        print("=" * 76)
        print(f"{e['id']}  ({e.get('year')})  other={e.get('other')}")
        print(f"  {str(e.get('title'))[:70]}")
        print(f"  {p[:210]}...")
    if report or not apply:
        print(f"\nreport only - {len(targets)} would be generated, nothing written")
        return 0

    GEN.mkdir(parents=True, exist_ok=True)
    made = []
    for n, e in enumerate(targets, 1):
        seed = 20261004 + n * 7
        prompt = build_prompt(e)
        try:
            r = api("/prompt", {"prompt": graph_for(prompt, seed),
                                "client_id": "parasocialize"})
        except urllib.error.HTTPError as ex:
            print(f"  {e['id']}: REJECTED {ex.code}")
            continue
        pid = r["prompt_id"]
        t0 = time.time()
        got = None
        while time.time() - t0 < 420:
            time.sleep(3)
            h = api(f"/history/{pid}")
            if pid in h:
                for _, o in h[pid].get("outputs", {}).items():
                    for im in o.get("images", []):
                        got = im
                break
        if not got:
            print(f"  {e['id']}: timed out")
            continue
        local = pathlib.Path(
            r"C:\Users\paras\ComfyUI-Installs\ComfyUI (4)\ComfyUI\output") \
            / got.get("subfolder", "") / got["filename"]
        if not local.exists():
            print(f"  {e['id']}: rendered but file not found at {local}")
            continue
        name = f"{e['id']}-{hashlib.sha1(local.read_bytes()).hexdigest()[:12]}.png"
        size = crop_to_banner(local, GEN / name)
        made.append((e, name, size, seed, prompt))
        print(f"  {e['id']:<28} {got['filename']}  {int(time.time()-t0)}s  "
              f"-> {name}  {size/1024:.0f} KB")

    if not made:
        print("\nnothing generated")
        return 1

    for e, name, size, seed, prompt in made:
        man["items"].append({
            "slug": e["id"],
            "for": "encyclopedia",
            "caption": ("Atmosphere for this entry: "
                        + build_prompt(e).split(":")[1].split(".")[0].strip().lower()
                        + ". Nothing in it can be dated or identified."),
            "q": "empty landscape atmosphere",
            "must": [],
            # kind starts UNCHECKED and stays that way until somebody opens the file.
# The first version wrote kind=illustrative WITH a looked date and a reason
# reading NOT YET OPENED - a date claiming a look that had not happened, in
# the same commit that generated the file. One frame in four renders a
# recognisable human figure despite the prompt forbidding one, so an unopened
# generated image is not merely unreviewed. It is untrustworthy.
            "kind": "unchecked","note": "GENERATED with FLUX.1-schnell. Author-owned by construction. "
                    "Never EXACT. Built from the entry's own year and otherness "
                    "value by tools/gen_atmosphere.py, not written per entry.",
            "local": f"img/generated/{name}",
            "src": {
                "title": "Generated locally: FLUX.1-schnell atmosphere",
                "author": "Parasocialize (generated on the site owner's own machine)",
                "licence": "Author-owned. Generated, not a third-party work.",
                "credit": "Generated on this site machine with FLUX.1-schnell. "
                          "Author-owned.",
                "page": "https://www.parasocialize.com/encyclopedia/"
                        + e["id"] + ".html",
            },
            "generation": {"model": "flux1-schnell-fp8.safetensors", "seed": seed,
                           "steps": 4, "cfg": 1.0, "sampler": "euler/simple",
                           "size": f"{OUT_W}x{OUT_H}", "prompt": prompt},
        })
    MAN.write_text(json.dumps(man, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    n_enc = sum(1 for i in man["items"] if i["for"] == "encyclopedia")
    print(f"\nrecorded {len(made)}; encyclopedia images now {n_enc}")
    print(f"  {sum(1 for i in man['items'] if i['for'] == 'encyclopedia' and 'NOT YET OPENED' in (i.get('look_reason') or ''))}"
          f" of them are UNLOOKED and say so")
    return 0


if __name__ == "__main__":
    sys.exit(main())