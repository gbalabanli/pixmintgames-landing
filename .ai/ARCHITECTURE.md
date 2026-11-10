# Architecture — PixMint Games landing site

Static, dependency-free site served by GitHub Pages behind Cloudflare DNS. There is no application
server, no build pipeline beyond the Pages artifact upload, and no runtime state.

## Request flow

```
Browser
  │  DNS query (pixmintgames.com A/AAAA)
  ▼
Cloudflare DNS (authoritative, DNS-only for apex)
  │  A     185.199.108.153 / .109 / .110 / .111
  │  AAAA  2606:50c0:8000::153 … 2606:50c0:8003::153
  ▼
GitHub Pages CDN  ── TLS (Let's Encrypt cert issued for the custom domain)
  │  serves the artifact produced by the latest successful `pages.yml` run
  ▼
site/index.html | site/privacy.html | site/404.html | site/assets/*
```

Key properties:

- **No origin server.** GitHub Pages terminates TLS and serves blobs from its CDN.
- **No Cloudflare proxy on the apex.** Traffic bypasses Cloudflare's edge entirely; Cloudflare is
  authoritative DNS only. This is deliberate so GitHub can complete HTTP-01 certificate issuance.
- **No caching layer we control.** Cache behavior is GitHub Pages' CDN defaults. HTML is expected to
  be revalidated relatively quickly; a hard refresh or cache-busting query string is the escape hatch
  when a deploy appears stale.
- **404 handling** is done by Pages: `site/404.html` is served for unknown paths on the custom domain.

## Redirect zones

Two zones exist in one Cloudflare account. Only the `.com` apex serves content.

```
pixmintgames.com        ── content (GitHub Pages, DNS-only apex)
  www.pixmintgames.com  ── proxied placeholder (192.0.2.1) → Single Redirect 301 → apex
pixmint.games           ── proxied placeholder (192.0.2.1) → Single Redirect 301 → apex of .com
  www.pixmint.games     ── proxied placeholder (192.0.2.1) → Single Redirect 301 → apex of .com
```

- The placeholder `A 192.0.2.1` records are RFC 5737 documentation addresses. They are never
  contacted because Cloudflare answers at the edge once the record is proxied.
- Redirect rules match on host and use a dynamic expression that forwards path and query:
  target `https://pixmintgames.com/${uri.path}` with "preserve query string" enabled.
- One hop only: `pixmint.games/foo?bar=1` → `https://pixmintgames.com/foo?bar=1` → `200`.
  No redirect chain through `www`.
- Because Cloudflare only applies redirect rules to proxied (orange-cloud) traffic, the placeholder
  records must stay proxied even though no origin exists.

## File responsibilities

| File | Responsibility | Change cadence |
| --- | --- | --- |
| `site/index.html` | Single landing page: hero, about, one game card ("Coming soon to Google Play"), contact, footer. All nav targets (`#about`, `#games`, `#contact`, `privacy.html`) live here. | Copy/marketing edits |
| `site/privacy.html` | Standalone privacy policy used as the Play Console privacy URL. Covers Firebase Analytics (opt-in, off by default), Crashlytics (opt-out, on), no ad SDKs, no website cookies, retention, children, GDPR/CCPA, deletion contact. | Legal review only |
| `site/404.html` | Branded not-found page with a link back to `/`. Served by Pages for unknown paths. | Rare |
| `site/CNAME` | Exactly `pixmintgames.com`. Tells Pages which custom domain the artifact belongs to. | Never, unless the domain changes |
| `site/robots.txt` | Allows all crawlers and points to the sitemap. | Rare |
| `site/sitemap.xml` | Canonical `https://pixmintgames.com/` and `/privacy.html` entries only. Never list alias hosts or 404. | When pages are added/removed |
| `site/assets/*.png`, `site/assets/favicon.ico` | Icons and OG card, all referenced from `<head>`; `site/favicon.ico` is a root copy so `/favicon.ico` resolves. | Asset refresh |
| `site/assets/wordmark.svg` | Vector brand mark, referenced by `site/404.html` only (the landing header uses a text logo). | Asset refresh |
| `site/assets/styles.css` | All layout and theming. Brand tokens are CSS custom properties on `:root`. Includes skip link, focus-visible rings, reduced-motion handling, and sticky-header scroll margin. | Design changes |
| `.github/workflows/pages.yml` | CI: checkout → configure Pages → `upload-pages-artifact` with `path: site` → `deploy-pages`. Permissions `contents: read`, `pages: write`, `id-token: write`; concurrency group `pages` with cancel-in-progress. | Infra changes only |
| `reqs-manifest.md` | Release tracker for the 13 requirements and waves. Owned by the orchestrator. | Orchestrator only |

Everything outside `site/` is invisible to production. That includes `.ai/`, docs, and the workflow.

## Content change lifecycle

```
edit site/*                    (plain files, no compile)
  │
  ├─ local preview              python -m http.server 8080 --directory site   (detached)
  ├─ verification               Playwright 1440/390, anchor sweep, asset 200s, contrast
  │
  ├─ git commit + push main
  │
  ▼
GitHub Actions  .github/workflows/pages.yml
  ├─ actions/checkout
  ├─ actions/configure-pages
  ├─ actions/upload-pages-artifact   (path: site)
  └─ actions/deploy-pages            → Pages CDN, atomic swap of the artifact
  │
  ▼
https://pixmintgames.com           live within seconds of the deploy job finishing
```

- Only one Pages deployment runs at a time; the concurrency group cancels superseded runs.
- A failed run leaves the previous artifact live. There is no partial deploy.
- Rollback = revert the commit and push, or re-run a previous successful workflow.
- DNS is not part of routine deploys. It changes once per domain, not per release.

## Brand tokens

Defined once in `site/assets/styles.css` as custom properties:

| Token | Value | Role |
| --- | --- | --- |
| `--ink` | `#1E1B2E` | Page background |
| `--orange` | `#F2541B` | Primary accent, CTAs (hover `#D8480F`) |
| `--cream` | `#F4EEE9` | Primary text |
| `--surface` | `#2A2540` | Cards, header, panels |
| `--surface-subtle` | `#241F35` | Alternating section background |
| `--border` | `#3A3450` | Hairlines and card borders |
| `--muted` | `#A9A3BE` | Secondary text |

Typography: **Orbitron** 600/800/900 for display, **Plus Jakarta Sans** 400–700 for body, loaded from
Google Fonts with `display=swap`. No self-hosted fonts, no font build step.

## Asset provenance

All imagery derives from the mobile app repository, read-only:

| Deployed asset | Source | Derivation |
| --- | --- | --- |
| `site/assets/favicon-32.png` | `PixMintGamesMobile/docs/brand/app-icon-master-1024.png` | Downscale to 32x32 |
| `site/assets/favicon.ico` | `site/assets/favicon-32.png` | ICO container for `/favicon.ico`; `site/favicon.ico` is a byte copy of it |
| `site/assets/apple-touch-icon.png` | same master | Downscale to 180x180 |
| `site/assets/icon-512.png` | same master | Downscale to 512x512 |
| `site/assets/og-image.png` | `PixMintGamesMobile/docs/store/feature-graphic-1024x500.jpg` (plus icon/wordmark) | Recomposed to 1200x630 |
| `site/assets/wordmark.svg` | `PixMintGamesMobile/docs/brand/wordmark-1024-wide.svg` | Copied, viewBox preserved |
| In-page imagery | `PixMintGamesMobile/docs/store/screenshots/` | None at present — the landing page is text-only; screenshots can be copied in later |

Rules: the source folders are read-only; assets are copied into `site/assets/` and never linked
across repositories at runtime. Every PNG must stay under 200 KB and match its documented
dimensions (REQ-07).

## Security and privacy posture

- No JavaScript, so no client-side injection surface and no third-party scripts beyond Google Fonts.
- No cookies, no analytics on the website itself (the app's Firebase Analytics/Crashlytics
  disclosures concern the games, not the site).
- No form posts; contact is a `mailto:` link.
- Secrets (Cloudflare tokens) exist only as environment variables at execution time, never in the
  repo. The repo is public by necessity (Free-plan Pages).
