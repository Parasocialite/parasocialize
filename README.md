# parasocialize.com

Static flagship site for Parasocial Productions / Enan Joe Heneghan.
No build step. No dependencies. Pure HTML/CSS/JS.

## Preview locally

```
python -m http.server 8000
```

Then open http://localhost:8000

## Deploy free (pick one)

### Option A — Cloudflare Pages (recommended)
1. Push this folder to a GitHub repo (or drag-and-drop the folder at https://dash.cloudflare.com -> Workers & Pages -> Create -> Pages -> Upload assets).
2. Build command: none. Output dir: `/`.
3. In NameBright, either:
   - Point `www.parasocialize.com` CNAME to `<your-project>.pages.dev`, or
   - Add the site to Cloudflare (free) and change nameservers at NameBright once - then all DNS is managed in Cloudflare.

### Option B — GitHub Pages
1. Repo Settings -> Pages -> deploy from branch `main` / root.
2. Custom domain: `www.parasocialize.com` (add CNAME record at NameBright pointing www -> `<user>.github.io`). Enforce HTTPS after DNS propagates.

## Notes
- Newsletter form uses FormSubmit.co pointed at iNNERdreamers@gmail.com.
  The FIRST submission triggers a one-time activation email - click it or subscribers silently fail.
  For a proper list, swap the form action for Buttondown / Mailchimp embed.
- Video cards are click-to-load YouTube facades (fast page, no autoplay bloat).
- All copy lives in index.html - edit titles/descriptions there freely.
- og:image is not set; add a 1200x630 image later and reference it in index.html head for better social shares.
