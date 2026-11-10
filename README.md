# PixMint Games — Landing Site

Static marketing site for **PixMint Games**, an independent mobile game studio. The site covers the
studio landing page, the privacy policy for the shipped games, and a custom 404 page.

- **Canonical URL:** https://pixmintgames.com
- **Alias domain:** `pixmint.games` (301 redirect to the canonical domain, path and query preserved)

No build step and no dependencies: every page under `site/` is plain HTML/CSS/JS served as-is.

## Layout

| Path | Purpose |
| --- | --- |
| `site/index.html` | Landing page (hero, games, studio, contact) |
| `site/privacy.html` | Privacy policy for the mobile titles |
| `site/404.html` | Custom not-found page served by GitHub Pages |
| `site/CNAME` | Custom domain marker for GitHub Pages (`pixmintgames.com`) |
| `site/robots.txt` | Crawler rules + sitemap pointer |
| `site/sitemap.xml` | Canonical URL list for search engines |
| `site/assets/` | Styles, scripts, images and fonts used by the pages |
| `.github/workflows/pages.yml` | GitHub Actions workflow that publishes `site/` to Pages |
| `AGENTS.md` | Agent/contributor entry point and project boundaries |
| `.ai/` | Working notes: tasks, lessons learned, feature history, architecture |

## Local preview

Serve the `site/` directory with Python's built-in server:

```bash
python -m http.server 8080 --directory site
```

Then open http://localhost:8080/.

> [!IMPORTANT]
> Spawn this command **detached / in the background** (for example
> `Start-Process ... -WindowStyle Hidden` on Windows, or `nohup ... &` on macOS/Linux).
> It runs until killed, so never run it in the foreground of an agent shell — it will hang the
> session. Verify with a separate call: `curl.exe --max-time 10 http://localhost:8080/`.

## Deploy

Push to `main`. The GitHub Actions workflow in `.github/workflows/pages.yml` uploads **only** the
`site/` directory as the Pages artifact, then deploys it to GitHub Pages. Because there is no build
step, whatever is committed under `site/` is exactly what is served.

## DNS summary

| Host / record | Type | Value | Proxy |
| --- | --- | --- | --- |
| `pixmintgames.com` (apex) | A | `185.199.108.153`, `185.199.109.153`, `185.199.110.153`, `185.199.111.153` | DNS only |
| `pixmintgames.com` (apex) | AAAA | `2606:50c0:8000::153`, `2606:50c0:8001::153`, `2606:50c0:8002::153`, `2606:50c0:8003::153` | DNS only |
| `www.pixmintgames.com` | CNAME / placeholder | Proxied placeholder record that returns a 301 to the apex (`https://pixmintgames.com`) | Proxied |
| `pixmint.games` zone | Placeholder | Proxied placeholder record that returns a 301 to `https://pixmintgames.com`, preserving path and query | Proxied |

Apex records stay DNS-only so GitHub Pages can issue and renew its TLS certificate; the redirect
hosts are proxied so the 301s are applied at the edge.

## Documentation

- `AGENTS.md` — entry point for contributors and AI agents (boundaries, verification rules).
- `.ai/` — `TASKS.md`, `LESSONS_LEARNED.md`, `FEATURE_HISTORY.md`, `ARCHITECTURE.md`.
- `reqs-manifest.md` — release tracker for the requirements shipped in this repo.

## Requirements

None. No package manager, no bundler, no runtime beyond a browser and (for local preview) Python 3.
