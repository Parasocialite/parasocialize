"""Wire the iYi logotype into the site.

Run once. Does three things by text substitution on tools/build_cards.py:

  1. the 19 nav marks stop being a 30px mascot and become the logotype, because
     the mascot was measured to collapse at that size and the asymmetry that
     carries the whole concept stops being visible there
  2. the masthead stops being a generated animation and becomes the logotype at
     hero size, which is the front door the page was missing
  3. the mascot import gains the wordmark import

Idempotent: re-running finds nothing left to do and says so.
"""
import pathlib
import re

P = pathlib.Path("tools/build_cards.py")
s = P.read_text(encoding="utf-8")
orig = s

nav = re.compile(r"""mascot\(30,\s*["']wm-mascot["']\)""")
n_nav = len(nav.findall(s))
s = nav.sub('wordmark("nav")', s)

if "from wordmark import" not in s:
    s = re.sub(r"(?m)^(from mascot import .*)$", r"\1\nfrom wordmark import wordmark", s, count=1)

# the masthead: swap the animated plate for the logotype
old_fig = re.search(
    r'    <figure class="mascot-hero">.*?</figure>\n', s, re.S)
if old_fig:
    s = s[:old_fig.start()] + '    <div class="masthead-mark">{wordmark("hero")}</div>\n' + s[old_fig.end():]
    n_fig = 1
else:
    n_fig = 0

P.write_text(s, encoding="utf-8")

print(f"  nav marks replaced      : {n_nav}")
print(f"  masthead figure replaced: {n_fig}")
print(f"  wordmark import present : {'from wordmark import' in s}")
print(f"  wm-mascot left in source: {s.count('wm-mascot')}")
print(f"  file changed            : {s != orig}")
