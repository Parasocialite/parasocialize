"""check_css.py - catches classes used in HTML that the stylesheet never defines.
Styling gaps do not 404, so nothing else in this repo would notice them."""
import re, pathlib, collections

ROOT = pathlib.Path(__file__).resolve().parent.parent
# every stylesheet, not just the main one. Ayo's rig lives in its own file, and
# reading only styles.css reported all 240+ of its classes as unstyled - which
# is how a check ends up crying wolf and gets ignored.
css = "\n".join(f.read_text(encoding="utf-8")
                for f in sorted((ROOT / "css").glob("*.css")))
defined = set(re.findall(r"\.([A-Za-z][\w-]*)", css))

used = collections.Counter()
inline_ok = set()
for f in ROOT.rglob("*.html"):
    if ".git" in f.parts:
        continue
    html = f.read_text(encoding="utf-8", errors="replace")
    html = re.sub(r"<script\b[^>]*>.*?</script>", "", html, flags=re.S | re.I)
    for m in re.findall(r'class="([^"]+)"', html):
        for tok in m.split():
            used[tok] += 1

# js-driven class names are added at runtime
for js in ROOT.rglob("*.js"):
    t = js.read_text(encoding="utf-8", errors="replace")
    for m in re.findall(r"classList\.(?:add|toggle|remove)\('([\w-]+)'", t):
        inline_ok.add(m)
for f in ROOT.rglob("*.html"):
    t = f.read_text(encoding="utf-8", errors="replace")
    for m in re.findall(r"classList\.(?:add|toggle|remove)\('([\w-]+)'", t):
        inline_ok.add(m)

missing = sorted(k for k in used
                 if k not in defined and k not in inline_ok
                 and not re.match(r"^(?:w-|h-|flex|grid|hidden|block|inline)", k))

print(f"css: {len(defined)} classes defined, {len(used)} used across the site")
if missing:
    print(f"  {len(missing)} used but never styled:")
    for m in missing:
        print(f"    .{m}  (x{used[m]})")
else:
    print("  every class used is styled.")

# --- structural guards. these fail silently in a browser and wreck a layout ---
bad = 0
for f in ROOT.rglob("*.html"):
    if ".git" in f.parts:
        continue
    raw = f.read_text(encoding="utf-8", errors="replace")
    rel = f.relative_to(ROOT)

    # a duplicate class attribute: the parser keeps the first and drops the
    # rest, so the second block of styling silently vanishes. shipped once.
    for m in re.findall(r"<[a-zA-Z][^>]*?\bclass=\"[^\"]*\"[^>]*?\bclass=\"[^\"]*\"[^>]*>", raw):
        bad += 1
        print(f"  FAIL  {rel}: duplicate class attribute -> {m[:90]}")

    # unbalanced divs: the classic cause of a page element overlapping
    # content above it, because the browser re-parents everything after.
    stripped = re.sub(r"<script\b[^>]*>.*?</script>", "", raw, flags=re.S | re.I)
    stripped = re.sub(r"<!--.*?-->", "", stripped, flags=re.S)
    opens = len(re.findall(r"<div\b", stripped, re.I))
    closes = len(re.findall(r"</div>", stripped, re.I))
    if opens != closes:
        bad += 1
        print(f"  FAIL  {rel}: {opens} <div> vs {closes} </div> — content will re-parent")

print("  structure ok." if not bad else f"  {bad} structural problem(s).")
raise SystemExit(1 if bad else 0)
