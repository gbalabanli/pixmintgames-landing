# AGENTS.md — PixMint Games landing site

Entry point for humans and AI agents working in this repository. Read this file first, then the
four memory files under `.ai/`.

## What this project is

A static marketing + legal site for **PixMint Games**, an independent mobile game studio.
It contains one landing page, one privacy policy page, and a custom 404 page. It is live on GitHub
Pages at **https://pixmintgames.com** (deployed 2026-11-10). `pixmint.games` and
`www.pixmint.games` are 301-redirected at Cloudflare to the canonical `.com` host (path and query
preserved).

- Canonical URL: https://pixmintgames.com
- Alias domain: https://pixmint.games (redirect only, no content)
- Repository: `gbalabanli/pixmintgames-landing` (public — required by GitHub Pages on the Free plan)
- Deploy branch: `main`, Pages `build_type=workflow`, artifact = `site/` only
- Release tracker: `reqs-manifest.md` (16 requirements, six waves + a second pass). **Do not edit it.**

## Stack

| Layer | Choice |
| --- | --- |
| Markup / styling | Plain HTML5 + hand-written CSS (`site/assets/styles.css`) |
| JavaScript | None. The site ships zero JS. |
| Build step | None. Files under `site/` are published byte-for-byte. |
| Package manager | None. No npm, no pnpm, no bundler. |
| Tooling | Python 3.12, manual scripts only — `tool/generate_assets.py` writes/verifies assets and is not part of deploy |
| Hosting | GitHub Pages via GitHub Actions (`actions/upload-pages-artifact` + `actions/deploy-pages`) |
| DNS / CDN / redirects | Cloudflare (both zones in the same account) |
| Fonts | Google Fonts — Orbitron (display) + Plus Jakarta Sans (body), `display=swap` |

Do not introduce a framework, a build step, npm dependencies, or client-side JS. If a change seems
to need one, raise it with the orchestrator first.

Brand palette v2 lives as CSS custom properties in `site/assets/styles.css`: `--ink #0B0810`,
`--surface #171221`, `--surface-subtle #110D18`, `--border #403A64`, `--brand #FF5E1A`
(hsl 18 100% 55%), `--brand-hot #FFA733` (hsl 34 100% 60%), `--brand-deep #E62600`
(hsl 10 100% 45%), `--accent #B370FF` (hsl 268 100% 72%, ambient glow only), `--cream #FFF7F2`,
`--muted #B5ACC7`. The glow/fill tokens (`--glow-brand`, `--glow-hot`, `--brand-tint`) are
`color-mix()` derivatives, and a `@media (color-gamut: p3)` block swaps in `color(display-p3 …)`
values on wide-gamut displays. Change the palette in those token blocks, not in component rules.

## File layout

```
PixmintGamesLanding/
├── AGENTS.md                     # this file
├── reqs-manifest.md              # release tracker (owned by the orchestrator, read-only here)
├── README.md                     # human-facing repo readme
├── .gitignore
├── .ai/
│   ├── ARCHITECTURE.md           # request flow, DNS, file responsibilities, provenance
│   ├── TASKS.md                  # requirement checklist by wave + open items
│   ├── FEATURE_HISTORY.md        # dated log of shipped changes and decisions
│   └── LESSONS_LEARNED.md        # infrastructure pitfalls and how to avoid them
├── .github/
│   └── workflows/
│       └── pages.yml             # builds and deploys ONLY site/ to GitHub Pages
├── site/                         # deploy artifact root — everything here is public
│   ├── index.html                # landing: hero, about, games, contact, footer
│   ├── privacy.html              # privacy policy (Play Console URL)
│   ├── 404.html                  # custom not-found page (served by Pages)
│   ├── CNAME                     # pixmintgames.com
│   ├── robots.txt                # blocks every crawler pre-launch; see Indexing
│   ├── sitemap.xml               # canonical URLs; unreferenced while indexing is off
│   ├── favicon.ico               # root copy so /favicon.ico resolves
│   └── assets/
│       ├── styles.css            # all styling, brand tokens as CSS custom properties
│       ├── favicon-32.png        # 32x32 favicon
│       ├── favicon.ico           # ICO copy of the favicon (used by the generator's asset set)
│       ├── apple-touch-icon.png  # 180x180 iOS icon
│       ├── icon-512.png          # 512x512 icon / PWA-ish metadata
│       ├── og-image.png          # 1200x630 Open Graph / Twitter card
│       └── wordmark.svg          # vector brand mark used by 404.html only
├── tool/
│   └── generate_assets.py        # idempotent asset generator + --check (writes only site/assets)
```

`site/` is the only directory that reaches production. Anything outside it (docs, workflows,
scripts) is never served. Run tooling explicitly, e.g.
`python tool/generate_assets.py`; there is no watcher and no automatic step on commit.

## Local preview

The site must be served over HTTP, not opened with `file://` — `CNAME`, `404.html`, and relative
asset paths only behave correctly behind a web server. Never run a server in the foreground; it
will hang the agent session. Spawn it detached, then verify in a **separate** command.

```powershell
# Step 1 — spawn detached (returns immediately)
New-Item -ItemType Directory -Force .logs | Out-Null
Start-Process -FilePath "python" `
  -ArgumentList "-m","http.server","8080","--directory","site" `
  -WindowStyle Hidden `
  -RedirectStandardOutput ".logs/preview.out.log" `
  -RedirectStandardError  ".logs/preview.err.log"
```

```powershell
# Step 2 — verify (separate call)
Start-Sleep 1
curl.exe -sI --max-time 10 http://127.0.0.1:8080/
curl.exe -sI --max-time 10 http://127.0.0.1:8080/privacy.html
```

```powershell
# Stop the preview server when done
Get-NetTCPConnection -LocalPort 8080 -State Listen -ErrorAction SilentlyContinue |
  ForEach-Object { Stop-Process -Id $_.OwningProcess -Force }
```

Then load `http://127.0.0.1:8080/` in Playwright at 1440px and 390px viewports for visual checks.
Do not use real Chrome profiles for this site.

## Deploy

Deployment is GitHub Actions only. A push to `main` that touches `site/`, `.github/workflows/`, or
the CNAME triggers `.github/workflows/pages.yml`, which uploads `site/` as the Pages artifact and
publishes it.

```powershell
# One-time: create the public repo, set the remote, push main
gh repo create gbalabanli/pixmintgames-landing --public --source . --remote origin --push

# One-time: enable Pages with workflow builds and bind the custom domain
gh api -X POST repos/gbalabanli/pixmintgames-landing/pages -f build_type=workflow
gh api -X PUT  repos/gbalabanli/pixmintgames-landing/pages -f cname=pixmintgames.com

# Routine deploy: commit site changes and push
git add site/ .github/ .ai/ AGENTS.md
git commit -m "site: <what changed>"
git push origin main

# Inspect the deployment
gh api repos/gbalabanli/pixmintgames-landing/pages
gh run list --workflow pages.yml --limit 5
```

Optional manual re-run: **Actions → pages → Run workflow**. There is no other deploy path; do not
upload to Pages from a local machine.

## DNS (Cloudflare)

`pixmintgames.com` is the canonical zone; `pixmint.games` is a redirect-only zone in the same
Cloudflare account. The apex records point at GitHub Pages and must stay **DNS-only (grey cloud)**
until the Pages certificate is approved and HTTPS is enforced.

| Zone | Name | Type | Value | Proxy |
| --- | --- | --- | --- | --- |
| pixmintgames.com | `@` | A | 185.199.108.153 | DNS only |
| pixmintgames.com | `@` | A | 185.199.109.153 | DNS only |
| pixmintgames.com | `@` | A | 185.199.110.153 | DNS only |
| pixmintgames.com | `@` | A | 185.199.111.153 | DNS only |
| pixmintgames.com | `@` | AAAA | 2606:50c0:8000::153 | DNS only |
| pixmintgames.com | `@` | AAAA | 2606:50c0:8001::153 | DNS only |
| pixmintgames.com | `@` | AAAA | 2606:50c0:8002::153 | DNS only |
| pixmintgames.com | `@` | AAAA | 2606:50c0:8003::153 | DNS only |
| pixmintgames.com | `www` | A | 192.0.2.1 (placeholder) | Proxied |
| pixmint.games | `@` | A | 192.0.2.1 (placeholder) | Proxied |
| pixmint.games | `www` | A | 192.0.2.1 (placeholder) | Proxied |

Redirects are Cloudflare **Single Redirects** (not Page Rules):

1. `www.pixmintgames.com/*` → `https://pixmintgames.com/$1`, 301, preserve query string.
2. `pixmint.games/*` and `www.pixmint.games/*` → `https://pixmintgames.com/$1`, 301, preserve query.

Verification commands:

```powershell
# Apex must resolve to GitHub Pages ranges, not Cloudflare proxies
dig +short A pixmintgames.com
dig +short AAAA pixmintgames.com

# www and the alias zone must answer with a single 301 to the canonical host
curl.exe -sI --max-time 15 https://www.pixmintgames.com/
curl.exe -sI --max-time 15 "https://pixmint.games/some/path?x=1"
```

Cloudflare API work uses a scoped token supplied through the `CLOUDFLARE_API_TOKEN` environment
variable at runtime. Never write tokens, zone IDs paired with tokens, or account IDs into any file
in this repo.

## Indexing (pre-launch)

Indexing is **deliberately disabled** until launch, on both crawler layers:

- `site/robots.txt` serves `User-agent: *` / `Disallow: /`; its `Sitemap:` line is commented out.
- `site/index.html`, `site/privacy.html`, and `site/404.html` each carry
  `<meta name="robots" content="noindex, nofollow">` and the same `googlebot` meta.

`site/sitemap.xml` is kept current but unreferenced, so it can be re-exposed at launch. The launch
flip is exactly three edits, and they must land together:

1. In `site/robots.txt`, remove the `User-agent: *` / `Disallow: /` pair.
2. In `site/robots.txt`, restore `Sitemap: https://pixmintgames.com/sitemap.xml`.
3. In all three pages, change both robots metas to `index, follow`.

Do not flip one layer only: metas alone still leave the sitemap hidden, and `robots.txt` alone still
leaves `noindex` in the HTML.

## Verification checklist

Run before declaring any site change done. Each item maps to a requirement in `reqs-manifest.md`.

- [ ] `git rev-parse --show-toplevel` prints this project folder, not the parent `agents` repo.
- [ ] Local preview returns `200` for `/`, `/privacy.html`, `/assets/styles.css`, and every asset.
- [ ] Every nav/footer anchor resolves (`#about`, `#games`, `#contact`, `privacy.html`).
- [ ] Playwright screenshots at 1440px and 390px: no overflow, no overlap, header offset correct.
- [ ] Console clean (no errors, no failed requests) and no requests to nonexistent files.
- [ ] `site/CNAME` contains exactly `pixmintgames.com`.
- [ ] `sitemap.xml` lists only canonical `https://pixmintgames.com/...` URLs (unreferenced while
      pre-launch).
- [ ] All three pages still carry `noindex, nofollow` (robots + googlebot) and `robots.txt` is
      `User-agent: *` / `Disallow: /` while pre-launch.
- [ ] Legal line matches across index/privacy/404: `Bora Balabanli · Aydınevler Mahallesi 32/3,
      34854 İstanbul (Anadolu), Türkiye`.
- [ ] `404.html` renders through the server and through the Pages artifact path.
- [ ] Image dimensions: favicon 32x32, apple-touch 180x180, icon 512x512, OG 1200x630; each < 200 KB.
- [ ] Contrast >= 4.5:1 for body text on ink/surface backgrounds.
- [ ] `pages.yml` uploads only `site/` and uses `pages: write` + `id-token: write`.
- [ ] After deploy: `gh run list --workflow pages.yml` shows a green run and the live `curl` matches
      the intended commit (the Pages API returns `status: null` for workflow builds — see
      `.ai/LESSONS_LEARNED.md` §11).
- [ ] `curl -sI https://pixmintgames.com/` returns `200`; `www` and `pixmint.games` return one `301`.
- [ ] `https_enforced: true` only after the certificate is approved (REQ-13).

## Boundaries

- **Never commit secrets**: no Cloudflare API tokens, no account/zone IDs paired with tokens, no
  `.env`, no credentials. Keep them in the shell environment only.
- **Never edit files under `site/` by hand without logging the change** in
  `.ai/FEATURE_HISTORY.md` in the same change set.
- **No frameworks, no build step, no npm.** The published artifact must stay plain static files.
- **Do not touch the parent `agents` repository.** It is a separate repo; this project is nested
  inside it. Run git commands from this folder and confirm the toplevel first. Do not run
  `git init` or commit unless that task is explicitly assigned.
- **Do not modify `reqs-manifest.md`** or files owned by other requirement workers
  (`site/`, `.github/`, `README.md`, `.gitignore`) unless your task names them.
- **Brand source art is read-only**: `../PixMintGamesMobile/docs/brand` and
  `../PixMintGamesMobile/docs/store`. Copy assets in; never edit the originals.
- **No inline JS, no analytics, no cookie banner.** The site sets no cookies.
- Keep `.ai/` files current: update TASKS checkboxes, FEATURE_HISTORY, and LESSONS_LEARNED as part
  of the same change that alters reality.

## Memory files

- `.ai/ARCHITECTURE.md` — request/DNS flow, file responsibilities, deploy pipeline, asset provenance.
- `.ai/TASKS.md` — the 16 release requirements grouped by wave and second pass, plus open items.
- `.ai/FEATURE_HISTORY.md` — dated record of what shipped and why.
- `.ai/LESSONS_LEARNED.md` — infrastructure pitfalls (DNS, redirects, caching, nested repos).
