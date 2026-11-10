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

- [ ] REQ-01 — `AGENTS.md` + `.ai/{ARCHITECTURE,TASKS,FEATURE_HISTORY,LESSONS_LEARNED}.md` generated
      with the init-workspace skill, then rewritten with real project content (deploy commands, DNS
      table, boundaries, verification matrix). [5 files non-empty + no template placeholders]
- [ ] REQ-02 — Dedicated git repository inside `PixmintGamesLanding` (parent `agents` repo untouched):
      `git init`, `.gitignore`, `README.md`. [git repo root correct, ignore rules effective]
- [ ] REQ-03 — `site/index.html` + `site/assets/styles.css`: brand tokens, accessibility (skip link,
      focus-visible, reduced-motion, contrast >= 4.5:1, sticky-header scroll margin), one-app-card
      Games section, nav/footer link arrangement, all anchors resolve. Original
      `one-page-landing.html` removed after content parity. [Playwright 1440 + 390, no dead links]
- [ ] REQ-04 — `site/index.html` head: canonical, OG/Twitter cards, JSON-LD `Organization`,
      favicon set references, `theme-color`, `color-scheme`. [tags present, assets return 200]
- [ ] REQ-05 — `site/privacy.html`: accurate policy (Firebase Analytics opt-in/off by default,
      Crashlytics opt-out/on, no ad SDKs, no website cookies, retention, children, GDPR/CCPA,
      deletion contact). [content audit vs app policy; no AdMob mention]
- [ ] REQ-06 — `site/404.html`, `site/robots.txt`, `site/sitemap.xml`, `site/CNAME`. [files valid,
      sitemap canonical, CNAME = pixmintgames.com]
- [ ] REQ-07 — `site/assets/`: `favicon-32.png`, `apple-touch-icon.png` (180), `icon-512.png`,
      `og-image.png` (1200x630), `wordmark.svg`. [dimensions via PIL, each < 200 KB]
- [ ] REQ-08 — `.github/workflows/pages.yml` deploying only `site/` with `upload-pages-artifact` +
      `deploy-pages`, correct permissions/concurrency. [YAML parses, path scoped]
- [ ] REQ-09 — Local verification harness: detached static server on `site/`, Playwright desktop +
      mobile screenshots, console/network clean, anchor + asset sweep, contrast check.
      [report + screenshot paths]
- [ ] REQ-10 — GitHub repo created (public), pushed, Pages enabled (`build_type=workflow`), custom
      domain `pixmintgames.com`. [`gh api /pages` -> built, cname correct]
- [ ] REQ-11 — Cloudflare `pixmintgames.com`: 4x A + 4x AAAA to GitHub Pages **DNS-only**, `www`
      proxied placeholder + 301 redirect to apex. [dig matches Pages IPs, `curl -I www` -> 301]
- [ ] REQ-12 — Cloudflare `pixmint.games`: proxied placeholder records + single 301 redirect rule
      preserving path and query. [`/foo?bar=1` -> `https://pixmintgames.com/foo?bar=1`, one hop]
- [ ] REQ-13 — Enforce HTTPS after cert approval; full production matrix (http/https x apex/www x both
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

(filled during verification)
