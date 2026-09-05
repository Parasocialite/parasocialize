# LAUNCH CHECKLIST — Parasocialize (profit stack)

Upload whole `parasocialize/` folder to Cloudflare Pages / GitHub Pages. No build step.

## 1. Before DNS (10 min)
- [ ] Open `index.html` locally: filters, `?member=1` preview, Index copy button, tip form mailto
- [ ] Open `signal/latest.html`: 5 picks + Index block render
- [ ] Open `guide/`, `classroom/`, `audit/`, `tip/` pages: buy buttons point to your email
- [ ] `python tools/build_radar.py && python tools/build_signal.py` both print success

## 2. Email (15 min, unlocks recurring)
- [ ] FormSubmit: submit test via v2 once → click activation email (or subs silently fail)
- [ ] At 200 subs: create Buttondown, replace `<form action>` in v2 (instructions in HTML comment)
- [ ] Paste `signal/latest.html` into first broadcast → send to yourself → check Gmail spam score

## 3. Money (30 min, unlocks $19 → $1,500)
- [ ] Gumroad product 1: Field Guide $19 PDF (print `guide/` via Ctrl+P → upload)
- [ ] Replace `mailto:` buy hrefs in `guide/index.html` with Gumroad link
- [ ] Gumroad product 2: Classroom $49 (same PDF + worksheet) — clone listing
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
- `guide/`, `classroom/`, `audit/`, `tip/` → standalone converters
