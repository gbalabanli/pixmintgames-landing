# Requirements — PixMint Games landing release

Goal: ship the existing one-page landing as **https://pixmintgames.com** on GitHub Pages,
301-redirect **pixmint.games** → `pixmintgames.com` (path + query preserved) at Cloudflare,
and document the project in `AGENTS.md` + `.ai/`.

Confirmed 2026-11-10. Verification method in brackets.

## Locked decisions

- Host: GitHub Pages, repo `gbalabanli/pixmintgames-landing` (public), deploy via Actions, artifact = `site/` only.
- Canonical host: apex `pixmintgames.com` (GitHub Pages A/AAAA, **DNS-only** in Cloudflare).
- `www.pixmintgames.com` → 301 → apex (Cloudflare redirect, proxied placeholder).
- `pixmint.games` + `www.pixmint.games` → 301 → apex of `.com`, path/query preserved.
- Palette: Ink `#1E1B2E`, Orange `#F2541B` (hover `#D8480F`), Cream `#F4EEE9`, surface `#2A2540`,
  surface-subtle `#241F35`, border `#3A3450`, muted `#A9A3BE`.
- Fonts: Orbitron (display) + Plus Jakarta Sans (body), Google Fonts with `display=swap`.
- Stack: static HTML/CSS, **no framework, no build step, no npm dependencies**.
- Language: English only.
- Privacy: dedicated `site/privacy.html` (Play Console URL), `#privacy` anchor removed from landing.

## Defaults for open content gaps

1. Legal entity: footer keeps `PixMint Games · İstanbul, Türkiye`; privacy names "PixMint Games" as
   data controller. **No bracket placeholders ship.** Exact vergi levhası name + registered address
   is a TODO in `.ai/TASKS.md`.
2. `contact@pixmintgames.com` kept as the published contact (no mail routing in this release).
3. Play Store CTA = non-link "Coming soon to Google Play" (never `href="#"`).
4. No social links; nav = About / Games / Privacy / Contact.
5. Brand assets reused from `../PixMintGamesMobile/docs/brand` and `../PixMintGamesMobile/docs/store`.
6. Repo is public (Free-plan Pages requirement).

---

## Requirements

- [x] REQ-01 — `AGENTS.md` + `.ai/{ARCHITECTURE,TASKS,FEATURE_HISTORY,LESSONS_LEARNED}.md` generated
      with the init-workspace skill, then rewritten with real project content (deploy commands, DNS
      table, boundaries, verification matrix). [5 files non-empty + no template placeholders]
- [x] REQ-02 — Dedicated git repository inside `PixmintGamesLanding` (parent `agents` repo untouched):
      `git init`, `.gitignore`, `README.md`. [git repo root correct, ignore rules effective]
- [x] REQ-03 — `site/index.html` + `site/assets/styles.css`: brand tokens, accessibility (skip link,
      focus-visible, reduced-motion, contrast >= 4.5:1, sticky-header scroll margin), one-app-card
      Games section, nav/footer link arrangement, all anchors resolve. Original
      `one-page-landing.html` removed after content parity. [Playwright 1440 + 390, no dead links]
- [x] REQ-04 — `site/index.html` head: canonical, OG/Twitter cards, JSON-LD `Organization`,
      favicon set references, `theme-color`, `color-scheme`. [tags present, assets return 200]
- [x] REQ-05 — `site/privacy.html`: accurate policy (Firebase Analytics opt-in/off by default,
      Crashlytics opt-out/on, no ad SDKs, no website cookies, retention, children, GDPR/CCPA,
      deletion contact). [content audit vs app policy; no AdMob mention]
- [x] REQ-06 — `site/404.html`, `site/robots.txt`, `site/sitemap.xml`, `site/CNAME`. [files valid,
      sitemap canonical, CNAME = pixmintgames.com]
- [x] REQ-07 — `site/assets/`: `favicon-32.png`, `apple-touch-icon.png` (180), `icon-512.png`,
      `og-image.png` (1200x630), `wordmark.svg`. [dimensions via PIL, each < 200 KB]
- [x] REQ-08 — `.github/workflows/pages.yml` deploying only `site/` with `upload-pages-artifact` +
      `deploy-pages`, correct permissions/concurrency. [YAML parses, path scoped]
- [x] REQ-09 — Local verification harness: detached static server on `site/`, Playwright desktop +
      mobile screenshots, console/network clean, anchor + asset sweep, contrast check.
      [report + screenshot paths]
- [x] REQ-10 — GitHub repo created (public), pushed, Pages enabled (`build_type=workflow`), custom
      domain `pixmintgames.com`. [`gh api /pages` -> built, cname correct]
- [x] REQ-11 — Cloudflare `pixmintgames.com`: 4x A + 4x AAAA to GitHub Pages **DNS-only**, `www`
      proxied placeholder + 301 redirect to apex. [dig matches Pages IPs, `curl -I www` -> 301]
- [x] REQ-12 — Cloudflare `pixmint.games`: proxied placeholder records + single 301 redirect rule
      preserving path and query. [`/foo?bar=1` -> `https://pixmintgames.com/foo?bar=1`, one hop]
- [x] REQ-13 — Enforce HTTPS after cert approval; full production matrix (http/https x apex/www x both
      domains) + TLS check + evidence report. [`https_enforced: true`, cert approved, statuses match]

## DAG

```
wave 1  REQ-01   REQ-02   REQ-03(+04)   REQ-07   REQ-08      (parallel, disjoint files)
wave 2  REQ-05   REQ-06                                     (need styles.css from REQ-03)
wave 3  REQ-09                                              (needs all site files)
wave 4  REQ-10                                              (needs REQ-08 green + REQ-09 pass)
wave 5  REQ-11   REQ-12                                     (parallel, Cloudflare API token)
wave 6  REQ-13                                              (needs REQ-10..12 green)
```

## Evidence log

## Evidence log

| Date | Req | Evidence |
| --- | --- | --- |
| 2026-11-10 | REQ-01 | init-workspace script run, then 5 files rewritten (AGENTS.md 216 lines + 4 `.ai` files); template/placeholder scan clean; every `.ai/*` link resolves |
| 2026-11-10 | REQ-02 | `git rev-parse --show-toplevel` -> this folder; parent `agents` status byte-identical before/after; 14 ignore rules verified with `git check-ignore`; first commit `5b1b3f3` |
| 2026-11-10 | REQ-03 | Playwright 1440x900 + 390x844: exactly 1 `h1`, heading order never skips, 0 empty anchors, 0 broken fragments, no horizontal overflow (1425/1425, 375/375), header 73/90px under 96px scroll margin |
| 2026-11-10 | REQ-04 | canonical + OG + Twitter + JSON-LD `Organization` present, description 126 chars, all 6 referenced assets 200 |
| 2026-11-10 | REQ-05 | 16 numbered sections, 1,459 words, no AdMob/ad-network mention, no bracket placeholders, 3 external links verified 200 |
| 2026-11-10 | REQ-06 | sitemap parses (2 canonical URLs, lastmod 2026-11-10), `CNAME` repr `b'pixmintgames.com\n'`, robots ASCII + sitemap pointer, 404 root-absolute link audit pass |
| 2026-11-10 | REQ-07 | favicon 32, apple-touch 180 (RGB, no alpha), icon 512, OG 1200x630 (34,369 B); image payload 63 KB total; wordmark byte-identical to brand source |
| 2026-11-10 | REQ-08 | YAML parses; `path: ./site`; `pages: write` + `id-token: write`; no `path: .`; guard fails fast when `site/index.html` or `site/CNAME` missing |
| 2026-11-10 | REQ-09 | 13/13 local paths 200; 0 console messages; 0 broken images; contrast 4.58:1 (brand on surface-subtle) to 14.59:1 (cream on ink); screenshots in `%TEMP%\opencode\pixmint-proof` |
| 2026-11-10 | REQ-10 | public repo `gbalabanli/pixmintgames-landing`; run 42847144949 success; `build_type=workflow`; `cname=pixmintgames.com`; github.io artifact 8/8 paths 200 |
| 2026-11-10 | REQ-11 | apex 4xA `185.199.108-111.153` + 4xAAAA `2606:50c0:8000-8003::153` all DNS-only; `www` proxied placeholder + single 301 to apex on both schemes |
| 2026-11-10 | REQ-12 | `pixmint.games` and `www.pixmint.games` -> single 301 to apex; `https://pixmint.games/some/path?x=1&y=2` -> `https://pixmintgames.com/some/path?x=1&y=2` (1 hop) |
| 2026-11-10 | REQ-13 | cert approved (domains `pixmintgames.com`, expires 2027-02-08); `https_enforced: true`; http apex -> 301 https; `ssl_verify=0` on every production URL; custom 404 served (2,890 B) |

Production screenshots: `%TEMP%\opencode\pixmint-proof\prod-index-1440.png`, `prod-index-390.png`,
`prod-404-390.png`. Release run: `https://github.com/gbalabanli/pixmintgames-landing/actions`.
