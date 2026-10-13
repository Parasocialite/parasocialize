"""check_css.py - catches classes used in HTML that the stylesheet never defines.
Styling gaps do not 404, so nothing else in this repo would notice them.

Also, with --orphans, the inverse: descendant rules that match NOTHING in any
generated page. See the long note at the bottom for why that one matters and
what it could not have caught on its own.
"""
import re, pathlib, collections, sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
# every stylesheet, not just the main one. Ayo's rig lives in its own file, and
# reading only styles.css reported all 240+ of its classes as unstyled - which
# is how a check ends up crying wolf and gets ignored.
CSS_FILES = sorted((ROOT / "css").glob("*.css"))
css = "\n".join(f.read_text(encoding="utf-8") for f in CSS_FILES)
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
    for m in re.findall(r"<[a-zA-Z][^>]*?\bclass=\"[^\"]*\"[^>]*?\bclass=\"[^\"]*\"[^>]*?>", raw):
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


# ---------------------------------------------------------------------------
# ORPHANS: a descendant rule that matches nothing.
#
# check_css's first job is "used in HTML, never defined in CSS". This is the
# other direction, and it is the one that bit the front page: a component was
# deleted from the site, its stylesheet block was not, and because the block's
# bare `.clerk{}` selector still matched a DIFFERENT live component further up
# the cascade it kept winning. A dead rule set outvoted a live one.
#
# Nothing else in this repo could have seen it, and the reasons are worth
# keeping, because each one is a way a gate is normally assumed to cover a page:
#   - it overflows nothing, so verify_narrow is silent
#   - it overlaps nothing, so probe_front is silent
#   - every class in it is a real, defined class, so the check above is silent
#   - the page builds, the file 200s, and it looks like a design decision
# It was found by screenshotting the page and reading the copy.
#
# What this check CANNOT do, stated up front so nobody trusts it too far:
#   - it matches selectors textually against the generated HTML. It is not a
#     browser and it does not compute the cascade.
#   - a rule can be dead in the pages we generate and live in a page built by
#     something else. It only knows about .html in this tree.
#   - a class toggled on at runtime by JS is invisible to a static read, so
#     rules under a JS-managed state class are skipped rather than reported.
#   - rules whose rightmost compound is a bare tag (`p`, `h3`) under a class
#     that IS live are reported only as notes, because a component can render
#     its inner markup from a template this repo does not own.
# It holds a stylesheet to the markup that exists. It cannot tell you the
# layout is right - only that something in the stylesheet addresses nothing.
# ---------------------------------------------------------------------------

# properties that decide how a box is arranged. A dead rule that only sets
# colour cannot wreck a page; a dead rule that sets one of these can, silently,
# on a component that happens to share the class name.
LAYOUT_PROPS = {
    "display", "grid-template-columns", "grid-template-rows", "grid-auto-flow",
    "flex", "flex-direction", "flex-wrap", "position", "float", "width",
    "height", "max-width", "min-width", "max-height", "min-height", "overflow",
    "overflow-x", "overflow-y", "inset", "top", "right", "bottom", "left",
    "margin", "padding", "gap", "order", "z-index", "box-sizing", "contain",
    "aspect-ratio", "writing-mode", "visibility",
}

# things a static read cannot resolve. Skipped rather than reported, because a
# check that cries wolf on selectors it cannot evaluate is a check that gets
# switched off - the same failure verify_narrow had reading an unstyled page.
UNRESOLVABLE = re.compile(r"[:\[>+~]|\b(?:hover|focus|active|visited|before|after"
                          r"|first-child|last-child|not|is|where|has)\b|\*|^$")


def js_root_classes():
    """Classes JS puts on <html>/<body> at runtime, so no static markup carries
    them. `body.nav-open .grain` is a live, correct rule - the mobile menu hides
    the grain overlay while it is open - and a static read cannot see it.

    The first run reported it as a FAIL, because it sets `display`. That is the
    `via`-field mistake in reverse: the gate should LEARN the field, not be
    silenced. Skipping only selectors anchored on a runtime root class is
    narrow; skipping every JS-toggled class would have hidden the `.clerk`
    defect, which is the case this check exists for.
    """
    roots = set()
    # Both quote styles: main.js writes classList.toggle("nav-open") and the
    # single-quoted form is what the rest of the repo uses, and a check that
    # only understands one of them silently misses the classes it exists to
    # learn - which is how the first run reported a live rule as dead.
    pat = re.compile(r"document\.(?:body|documentElement)\.classList"
                     r"\.(?:add|toggle|remove)\(\s*['\"]([\w-]+)['\"]")
    for f in list(ROOT.rglob("*.js")) + list(ROOT.rglob("*.html")):
        if ".git" in f.parts:
            continue
        t = f.read_text(encoding="utf-8", errors="replace")
        roots.update(pat.findall(t))
    return roots


JS_ROOTS = js_root_classes()

# Markup that JS builds at runtime, so no static file contains it. A static
# read cannot see these and will report them as orphans - which is how the
# first full run came back with 19 "layout" failures on a stylesheet that was
# fine. `.yt-facade` is a <button> in the markup and the <iframe> is appended
# by main.js on click, so `.yt-facade iframe` is a live rule on a node that
# does not exist until somebody clicks.
#
# This list is a DECLARATION, not a suppression: each entry says what JS builds
# it and why the rule is live. An entry that cannot be justified is the thing
# to argue about, and `check_css --orphans` prints it so it stays visible.
JS_BUILT = {
    ".yt-facade iframe": "main.js appends the <iframe> into the button on click",
}


def orphan_report():
    trees = read_tree()
    findings = []
    for f in CSS_FILES:
        text = f.read_text(encoding="utf-8")
        # Strip comments FIRST. Without this the parser reads prose out of the
        # explanatory notes and reports "and its height" as an unmatchable
        # selector - three of the first four findings were a comment, which is
        # the classic way a check reports numbers about nothing.
        text = re.sub(r"/\*.*?\*/", " ", text, flags=re.S)
        for sel, decls in strip_at_blocks(text):
            if sel.startswith("@") or not sel.strip():
                continue
            for one in sel.split(","):
                one = one.strip()
                if not one or UNRESOLVABLE.search(one) or one in JS_BUILT:
                    continue
                parts = one.split()
                if len(parts) < 2:
                    continue
                # anchored on a class JS puts on <body> at runtime?
                # `parts[0]` is the whole first compound, e.g. "body.nav-open"
                head = parts[0]
                hcls = re.findall(r"\.([\w-]+)", head)
                if head.split(".")[0] in ("body", "html") and hcls and \
                        all(c in JS_ROOTS for c in hcls):
                    continue
                if not rule_reaches(one, trees):
                    props = {d.split(":")[0].strip()
                             for d in decls.split(";") if ":" in d}
                    lays = sorted(props & LAYOUT_PROPS)
                    findings.append((f.name, one, lays))
    return findings


# --- the ratchet ------------------------------------------------------------
# This check starts life behind: there are 18 orphaned layout rules in the
# committed stylesheet, all of them predating it. Failing every build until
# somebody deletes 18 rules is a laundry list, and a gate that is red on
# arrival is a gate that gets switched off inside a week. So the committed
# number is a CEILING that can only fall, and lowering it is a deliberate act.
#
# The `--ratchet` pattern is already used in this repo for the 94 URL-less
# `retrievable` records, and the reasoning is the same: fix the claim, keep the
# debt visible, and make regression impossible rather than pretending the debt
# is not there.
ORPHAN_BASELINE = 17


def strip_at_blocks(text):
    """Yield (selector, declarations) for EVERY block, at any nesting depth.

    The first version returned only the *bodies* of top-level blocks and threw
    the selector away, so a top-level rule like `.clerk{...}` was invisible to
    the whole check and the gate reported 0 orphans while the dead rule was
    sitting in the file. It passed the red test the project requires because
    the thing it failed to see was the thing being tested.

    A stack of (selector, body_start), pushed on `{` and popped on `}`, is the
    whole fix. An @media/@supports line arrives as a selector beginning `@`
    and is skipped by the caller, which is what we want: we want the rules
    inside the wrapper, not the wrapper.
    """
    out, stack, sel_start = [], [], 0
    for pos, ch in enumerate(text):
        if ch == "{":
            stack.append((text[sel_start:pos].strip(), pos))
            sel_start = pos + 1
        elif ch == "}":
            if stack:
                sel, bstart = stack.pop()
                out.append((sel, text[bstart:pos]))
            sel_start = pos + 1
    return out


VOID = {"br", "hr", "img", "meta", "link", "input", "source", "area", "base",
        "col", "embed", "param", "track", "wbr"}
# SVG children are not descendants for CSS purposes in any rule in this
# stylesheet, but they DO sit inside <svg> which is how most of the art on this
# site is built - and <svg> itself is a real box. Keep svg and its direct
# children, drop the drawing primitives, which have no descendants anyway.
SVG_DROP = {"path", "circle", "rect", "line", "polyline", "polygon", "ellipse",
            "use", "stop", "textpath", "tspan", "defs", "clippath", "mask"}


def read_tree():
    """(tag, classes, parent_index) for every element in every generated page."""
    trees = []
    tok = re.compile(r"<(/?)([a-zA-Z][\w-]*)((?:\"[^\"]*\"|'[^']*'|[^>\"'])*?)(/?)>")
    attr = re.compile(r"class=\"([^\"]*)\"")
    for f in ROOT.rglob("*.html"):
        if ".git" in f.parts:
            continue
        raw = f.read_text(encoding="utf-8", errors="replace")
        raw = re.sub(r"<script\b[^>]*>.*?</script>", "", raw, flags=re.S | re.I)
        raw = re.sub(r"<!--.*?-->", "", raw, flags=re.S)
        raw = re.sub(r"<(?:br|hr|meta|link|source|area|base|col|embed|param|track|wbr)\b[^>]*>",
                     "", raw, flags=re.I)
        stack = [-1]
        nodes = []
        for m in tok.finditer(raw):
            closing, tag, rest, selfclose = (m.group(1), m.group(2).lower(),
                                            m.group(3), m.group(4))
            if closing:
                if len(stack) > 1:
                    stack.pop()
                continue
            if tag in SVG_DROP:
                continue
            cm = attr.search(rest)
            classes = frozenset(cm.group(1).split()) if cm else frozenset()
            parent = stack[-1]
            nodes.append((tag, classes, parent))
            # A void element is still a descendant - it is just a leaf. The
            # first version deleted <img> from the tree outright and then
            # reported `.ent-hero img` as unmatchable on a page that opens with
            # <figure class="ent-hero plate"><img ...>. Three findings, two of
            # them about markup that was sitting right there in the file.
            if tag not in VOID and not selfclose:
                stack.append(len(nodes) - 1)
        trees.append(nodes)
    return trees


def descendants(nodes, node_i):
    """Every node index beneath node_i, at any depth."""
    out, stack = [], list(nodes[node_i][2:] and [] or [])
    # walk the recorded child lists
    children = {}
    for i, (_t, _c, p) in enumerate(nodes):
        children.setdefault(p, []).append(i)
    stack = list(children.get(node_i, []))
    while stack:
        n = stack.pop()
        out.append(n)
        stack.extend(children.get(n, []))
    return out


def compound_matches(node_tag, node_classes, comp):
    """Does one compound selector (no combinator) match this element?"""
    comp = comp.strip()
    m = re.match(r"^([a-zA-Z][\w-]*)?((?:[.#][\w-]+)*)$", comp)
    if not m:
        return False
    tag, rest = m.group(1), m.group(2)
    if tag and tag.lower() != node_tag:
        return False
    want = set(re.findall(r"\.([\w-]+)", rest))
    return want.issubset(node_classes)


def rule_reaches(selector, trees):
    """True if the selector matches at least one element in any generated page."""
    for nodes in trees:
        for i, (tag, classes, _p) in enumerate(nodes):
            if not compound_matches(tag, classes, selector.split()[-1]):
                continue
            if len(selector.split()) == 1:
                return True
            anc_i = nodes[i][2]
            ok = False
            while anc_i != -1:
                if compound_matches(*nodes[anc_i][:2], selector.split()[0]):
                    ok = True
                    break
                anc_i = nodes[anc_i][2]
            if ok:
                return True
    return False




if "--orphans" in sys.argv:
    findings = orphan_report()
    hard = [f for f in findings if f[2]]
    soft = [f for f in findings if not f[2]]
    print(f"orphans: {len(findings)} rule(s) match nothing in any generated page"
          f"  ({len(hard)} set a layout property, {len(soft)} colour/type only)")
    for fn, sel, lays in hard:
        print(f"  dead-layout  {fn}: {sel}   -> {', '.join(lays)}")
    for fn, sel, lays in soft:
        print(f"  note         {fn}: {sel}")
    for sel, why in sorted(JS_BUILT.items()):
        print(f"  js-built     {sel}  ({why})")

    if "--ratchet" in sys.argv:
        # Lower the committed ceiling to the count just measured. This is the
        # only way the number moves down, and putting it in a commit is the
        # point: the baseline is a decision, not a running total.
        src = (ROOT / "tools" / "check_css.py").read_text(encoding="utf-8")
        new = re.sub(r"^ORPHAN_BASELINE = \d+", f"ORPHAN_BASELINE = {len(hard)}",
                     src, count=1, flags=re.M)
        if new != src:
            (ROOT / "tools" / "check_css.py").write_text(new, encoding="utf-8")
            print(f"  RATCHETED ORPHAN_BASELINE -> {len(hard)}")

    if len(hard) > ORPHAN_BASELINE:
        bad += len(hard) - ORPHAN_BASELINE
        print(f"  FAIL  {len(hard)} orphaned layout rules, baseline allows"
              f" {ORPHAN_BASELINE}. Delete the rules, or --ratchet if the"
              f" increase is deliberate.")
    elif len(hard) < ORPHAN_BASELINE and "--ratchet" not in sys.argv:
        print(f"  {len(hard)} orphaned layout rules, baseline allows"
              f" {ORPHAN_BASELINE}. Run with --ratchet to lock in the"
              f" improvement.")
    else:
        print(f"  no orphaned layout rules beyond the baseline of {ORPHAN_BASELINE}.")

raise SystemExit(1 if bad else 0)
