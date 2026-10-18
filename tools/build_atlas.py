#!/usr/bin/env python3
"""
build_atlas.py - /atlas/. The catalogue as a grid of era by medium.

WHY A GRID AND NOT A CONSTELLATION
This page used to be a hand-written force simulation: 248 dots, 417 edges,
drag to throw it, scroll to fly in. It was pretty and it could not be read.
Nothing in it answered "what does this corpus actually look like" - a reader
could not find an entry in it, could not count anything, and it shipped an
apology in the form of a full list underneath, which was the admission the
map had failed.

The data has two axes that were authored rather than simulated: every entry
carries a medium (some carry several) and a place in time. So the catalogue
fits in a table - 15 media down, eight bins of time across, every cell a
count. That is not a diagram of the corpus. It is the corpus, counted, and
it answers the question the constellation kept drawing around.

THE ROW LABELS ARE LINKS AND THE CELLS ARE NOT
A row name goes to the encyclopedia with that medium already filtered
(`?m=<medium>#db`), because "show me the film entries" is the one thing a
reader wants to do from a row of counts. The counts themselves are inert on
purpose: a number that looks clickable promises to take you somewhere
specific, and a cell holds many entries. A link would be a claim the number
cannot keep.

  python tools/build_atlas.py
"""
import json, pathlib, sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
OUT = ROOT / "atlas" / "index.html"

# The medium list lives in tools/atlas.py, which validates every entry against
# it. It used to be duplicated here, and the two copies had already drifted:
# this file had **eleven** media where atlas.py had fifteen, so `radio` and
# `comics` - the two added specifically because the axis had nowhere to put
# them - were never filterable in the atlas at all. Same family as a plate
# that stops describing its entry: a generated artefact quietly falling
# behind its source, invisible from either file alone. Import, do not copy.
try:
    from atlas import MEDIA as MEDIA_ORDER, MEDIA_LABEL  # noqa: F401
except ImportError:  # running from a different cwd
    import importlib.util as _ilu
    _spec = _ilu.spec_from_file_location(
        "_atlas_mod", str(ROOT / "tools" / "atlas.py"))
    _mod = _ilu.module_from_spec(_spec)
    _spec.loader.exec_module(_mod)
    MEDIA_ORDER = _mod.MEDIA
    MEDIA_LABEL = _mod.MEDIA_LABEL


# Colours are spaced evenly around the wheel, one per medium, and the count is
# derived rather than written down - a hardcoded `n=11` silently mis-spaced
# every colour the day a twelfth medium was added, and nothing would have
# said so.
def media_colour(i, n=None):
    n = n or len(MEDIA_ORDER)
    return f"hsl({int((i / n) * 360)} 76% 62%)"


# Eight columns of time. The bins are deliberately coarse: at this corpus size
# a decade-by-century spread would be mostly zeros, and a grid of zeros reads
# as a broken table rather than as thin coverage. The boundaries are the
# conventional ones for this subject - the old world / the printed world /
# the industrial century / broadcasting / the internet - not values tuned to
# make the picture look even.
ERA_HEAD = ["before<br>0", "0&ndash;<br>1499", "1500&ndash;<br>1799",
            "1800&ndash;<br>1899", "1900&ndash;<br>1949", "1950&ndash;<br>1999",
            "2000+", "undated"]
ERA_TITLE = ["before 0", "0 to 1499", "1500 to 1799", "1800 to 1899",
             "1900 to 1949", "1950 to 1999", "2000 and later", "no year recorded"]
NBIN = len(ERA_HEAD)


def era_bin(y):
    """Which column an entry sits in. None is the undated column."""
    if y is None:
        return NBIN - 1
    if y < 0:
        return 0
    if y < 1500:
        return 1
    if y < 1800:
        return 2
    if y < 1900:
        return 3
    if y < 1950:
        return 4
    if y < 2000:
        return 5
    return 6


def tier(n, mx):
    """Heat, in three steps. Thresholds at a half and a fifth of the fullest
    cell, so the tint is a reading of this table rather than of a fixed band
    that a growing corpus would leave behind."""
    if n >= mx * 0.5:
        return 3
    if n >= mx * 0.2:
        return 2
    return 1


CSS = """
.atlwrap{margin-top:24px;overflow-x:auto;border:1px solid var(--line);border-radius:10px}
/* A table with width:100% cannot go below the sum of its cells' min-content
   widths, and eight count columns plus a label cannot fit 390px. The scroller
   is the designed answer here, exactly as .dbwrap is on /encyclopedia/ - the
   reader pans the grid rather than the page losing its end off the side. */
table.atl{width:100%;min-width:640px;border-collapse:collapse}
.atl th,.atl td{border-bottom:1px solid var(--line);vertical-align:middle}
.atl thead th{border-bottom:1px solid var(--line2);font-family:var(--label);
  font-size:.6rem;font-weight:400;letter-spacing:.05em;text-transform:uppercase;
  color:var(--dimmer);padding:10px 7px;text-align:center;line-height:1.35;
  white-space:nowrap}
.atl thead th:first-child{text-align:left;padding-left:14px}
.atl-m{border-right:1px solid var(--line);font-family:var(--label);
  font-size:.62rem;font-weight:400;letter-spacing:.02em;color:var(--paper);
  padding:9px 12px;text-align:left;white-space:nowrap}
.atl-m a{color:inherit;text-decoration:none;border-bottom:1px dotted var(--line2)}
.atl-m a:hover{color:var(--hot);border-bottom-color:var(--hot)}
.atl-dot{display:inline-block;width:8px;height:8px;border-radius:50%;
  margin-right:8px}
.atl-n{font-family:var(--label);font-size:.62rem;color:var(--dim);
  padding:9px 7px;text-align:center;font-variant-numeric:tabular-nums}
.atl-n.z{color:var(--dimmer)}
.atl-n[data-f="1"]{background:rgba(255,90,26,.08);color:#f0e4d4}
.atl-n[data-f="2"]{background:rgba(255,90,26,.19)}
.atl-n[data-f="3"]{background:rgba(255,90,26,.34);color:#fff}
.atl-u{border-left:1px solid var(--line2)}
.atl-tot{color:#f4e8d8;border-left:1px solid var(--line2)}
.atl tbody tr:last-child th,.atl tbody tr:last-child td{
  border-bottom:1px solid var(--line2)}
.atl tfoot th,.atl tfoot td{border-bottom:0;font-family:var(--label);
  font-size:.6rem;color:var(--dimmer);padding:10px 7px;text-align:center;
  font-variant-numeric:tabular-nums}
.atl tfoot th:first-child{text-align:left;padding-left:14px}
.atl tfoot .atl-tot{color:var(--warm)}
"""

PAGE = """<!DOCTYPE html>
<html lang="en"><head><meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>The Atlas - Parasocialize</title>
{head}
<style>{css}</style>
</head>
<body>
<div class="grain" aria-hidden="true"></div>
{mk}
<main>
<section class="section" id="atl">
  <p class="kicker">The Atlas</p>
  <h1 class="h-title">Every entry has an era and a medium</h1>
  <p class="sec-lede" style="max-width:66ch">Every one of the {n} entries in the
  catalogue carries at least one medium, and a place in time. {n} entries,
  {nmedia} media, {nbins} bins of time - this grid is the whole corpus at once.
  A row name opens the encyclopedia already filtered to that medium.</p>

  <div class="atlwrap">
  <table class="atl" aria-label="Entries counted by medium and era">
    <thead><tr><th scope="col">Medium</th>{heads}<th scope="col" class="atl-tot">Total</th></tr></thead>
    <tbody>{body_rows}</tbody>
    <tfoot>{foot_row}</tfoot>
  </table>
  </div>

  <div class="note" style="margin-top:26px">{notes}</div>
</section>
</main>
{foot}
</body></html>"""


def esc(s):
    return (str(s or "").replace("&", "&amp;").replace("<", "&lt;")
            .replace(">", "&gt;").replace('"', "&quot;"))


def main():
    sys.path.insert(0, str(ROOT / "tools"))
    import build_cards as bc

    graph = json.loads((ROOT / "data" / "atlas.json").read_text(encoding="utf-8"))
    nodes = graph["nodes"]
    enc = json.loads((ROOT / "data" / "encyclopedia.json").read_text(encoding="utf-8"))
    n = len(nodes)

    # An entry with no medium would be counted in no row and simply vanish from
    # a page whose whole job is counting. atlas.py validates the axis so this
    # should never fire, but a generator that silently drops a row is the same
    # family as a plate that stops describing its entry - so it refuses loudly.
    orphans = [nd["id"] for nd in nodes if not nd["m"]]
    if orphans:
        raise SystemExit(
            f"atlas: {len(orphans)} entries carry no medium: {orphans[:5]}")

    matrix = {m: [0] * NBIN for m in MEDIA_ORDER}
    unknown = set()
    for nd in nodes:
        b = era_bin(nd.get("y"))
        for m in set(nd["m"]):
            if m not in matrix:
                unknown.add(m)
                continue
            matrix[m][b] += 1
    if unknown:
        raise SystemExit(
            f"atlas: media not in the validated list: {sorted(unknown)}")

    colours = {m: media_colour(i) for i, m in enumerate(MEDIA_ORDER)}
    mx = max(max(row) for row in matrix.values())

    def cell(count, f, label, era, undated):
        cls = "atl-n atl-u" if undated else "atl-n"
        if not count:
            return (f'<td class="{cls} z" title="no entries &middot; '
                    f'{esc(label)} &middot; {esc(era)}">&middot;</td>')
        return (f'<td class="{cls}" data-f="{f}" title="{count} entries '
                f'&middot; {esc(label)} &middot; {esc(era)}">{count}</td>')

    heads = "".join(
        '<th scope="col" title="{}"{}>{}</th>'.format(
            esc(ERA_TITLE[j]),
            ' class="atl-u"' if j == NBIN - 1 else "",
            ERA_HEAD[j])
        for j in range(NBIN))

    body_rows = []
    for m in MEDIA_ORDER:
        row = matrix[m]
        label = MEDIA_LABEL.get(m, m)
        cells = "".join(cell(count, tier(count, mx), label, ERA_TITLE[j],
                             j == NBIN - 1)
                        for j, count in enumerate(row))
        body_rows.append(
            '<tr><th scope="row" class="atl-m">'
            f'<span class="atl-dot" style="background:{colours[m]}"></span>'
            f'<a href="../encyclopedia/index.html?m={m}#db">{esc(label)}</a>'
            '</th>' + cells +
            f'<td class="atl-n atl-tot">{sum(row)}</td></tr>')

    era_counts = [0] * NBIN
    for nd in nodes:
        era_counts[era_bin(nd.get("y"))] += 1
    foot_row = ('<tr><th scope="row" class="atl-m">Total</th>' + "".join(
        '<td class="atl-n atl-tot{}">{}</td>'.format(
            " atl-u" if j == NBIN - 1 else "", era_counts[j])
        for j in range(NBIN)) +
        f'<td class="atl-n atl-tot">{n}</td></tr>')

    undated = era_counts[-1]
    placements = sum(sum(r) for r in matrix.values())
    inferred = sum(1 for nd in nodes if nd.get("mi"))
    checked = sum(1 for nd in nodes if nd.get("v"))

    # The notes are the table's own honest limits, computed rather than typed.
    # A figure inside a paragraph is not obviously a claim, which is what makes
    # it the dangerous kind - so none of these is a literal.
    notes = (
        "<p><b>Eras</b> are bins of each entry's start year, not spans of "
        "activity: before 0, 0&ndash;1499, 1500&ndash;1799, 1800&ndash;1899, "
        "1900&ndash;1949, 1950&ndash;1999, 2000 and later.</p>"
        f"<p><b>Undated.</b> {undated} entries carry no year this site can "
        "stand behind. They are given a column of their own rather than "
        "dropped, the same way unverified dates are marked on the timeline.</p>"
        f"<p><b>An entry can sit in more than one medium.</b> The rows add up "
        f"to {placements} placements across {n} entries, so the row totals sum "
        "past the entry count; the bottom row counts each entry once, in its "
        "own era.</p>"
        f"<p><b>On medium tags.</b> {inferred} of the {n} entries carry an "
        "inferred medium tag rather than one recorded from a source.</p>"
        f"<p><b>Citations.</b> {checked} of the {n} entries have had every "
        "citation checked. The rest are marked in the encyclopedia and listed "
        'on <a href="../citations/index.html">the citation board</a>.</p>')

    head = bc.HEAD.format(
        site=bc.SITE, path="/atlas/", otype="website",
        title="The Atlas - Parasocialize",
        desc=(f"All {n} entries counted by medium and by era, in one grid. "
              "A row name filters the encyclopedia to that medium."),
        root="../")
    mk = bc.NAV.format(root="../", total=len(enc["entries"]), mk="")
    foot = bc.FOOT.format(
        root="../", sweep=bc.MESSY,
        motto='EVERY ENTRY SITS SOMEWHERE.<br>THIS IS WHERE THEY MEET.')

    html = PAGE.format(head=head, css=CSS, mk=mk, n=n,
                       nmedia=len(MEDIA_ORDER), nbins=NBIN,
                       heads=heads, body_rows="".join(body_rows),
                       foot_row=foot_row, notes=notes, foot=foot)
    OUT.parent.mkdir(exist_ok=True)
    OUT.write_text(html, encoding="utf-8")
    print(f"atlas: {n} entries, {len(MEDIA_ORDER)} media x {NBIN} bins, "
          f"{placements} placements -> {OUT}")


if __name__ == "__main__":
    main()
