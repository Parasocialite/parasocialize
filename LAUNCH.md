# LAUNCH CHECKLIST — Parasocialize (profit stack)

Upload whole `parasocialize/` folder to Cloudflare Pages / GitHub Pages. No build step.

## 1. Before DNS (10 min)
- [ ] Open `index.html` locally: filters, `?member=1` preview, Index copy button, tip form mailto
- [ ] Open `signal/latest.html`: 5 picks + Index block render
- [ ] Open `classroom/`, `audit/`, `tip/` pages: buy buttons point to your email
- [ ] `python tools/build_radar.py && python tools/build_signal.py` both print success

## 2. Email (15 min, unlocks recurring)
- [ ] FormSubmit: submit test via v2 once → click activation email (or subs silently fail)
- [ ] At 200 subs: create Buttondown, replace `<form action>` in v2 (instructions in HTML comment)
- [ ] Paste `signal/latest.html` into first broadcast → send to yourself → check Gmail spam score

## 3. Money (30 min) - SHELVED until the revenue avenue is decided
- [X] ~~Gumroad product 1: Field Guide $19 PDF~~ **CANCELLED 2026-09-29.** A $19 PDF of writing the reader can already read free in the browser is not a product, it is a toll on the same words. `guide/` is recoverable at commit ad17778 if it ever earns its place back.
- [ ] Decide the actual revenue avenue *before* building the next thing. The $6/mo index tier and the $18 clinic already stand on their own and do not depend on this.
- [ ] Gumroad product 1 (now the first product): Classroom $49 - worksheet + rubric. No longer a clone of a guide listing, so it needs its own cover, its own proof, and its own reason to exist at $49.
- [ ] Audit: keep mailto until 2 bookings, then add Stripe payment link
- [ ] Affiliate: confirm Amazon Associates tag on Company Dreamer links (or keep bare)

## 4. Traffic (weekly loop, 90 min/week)
- Mon: 1 Radar `.md` → `build_radar.py` → push
- Wed: 1 Radar `.md` → push
- Fri: update `index.json` (15 min) → `build_signal.py` → send Signal → copy Index text to X/TikTok
- Monthly: 1 Case File `.md` → `cases.json` append → push

## 5. SEO (one-time)
- [ ] Submit `sitemap.xml` in Google Search Console
- [ ] og:image: add 1200×630 to `img/` + reference in `index.html` head
- [ ] When ready: 301 or canonical V1 → V2 (keep `index.html` until V2 converts)

## File map (source of truth)
- `radar/*.md` → `radar.json` → `radar.xml` + grid + email
- `cases/*.md` → `cases.json` → paywall grid
- `index.json` (+ `index/YYYY-Www.json` archive) → table + email block
- `signal/latest.html/.txt` → Buttondown paste
- `classroom/`, `audit/`, `tip/` -> standalone converters
