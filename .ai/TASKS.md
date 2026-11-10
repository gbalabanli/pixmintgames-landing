# Tasks — PixMint Games landing release

Source of truth for scope: `reqs-manifest.md` (16 requirements, six waves plus a second pass). This
file mirrors that tracker with acceptance criteria and status. Update checkboxes as work lands; never
edit the manifest.

Legend: `[ ]` not started · `[/]` in progress · `[x]` done and verified.

## Wave 1 — parallel foundation

- [x] **REQ-01 — Workspace docs.** `AGENTS.md` + `.ai/{ARCHITECTURE,TASKS,FEATURE_HISTORY,LESSONS_LEARNED}.md`
      generated with the init-workspace skill, then rewritten with real project content: file layout,
      detached preview command, deploy + DNS commands, boundaries, verification checklist.
      *Done when:* 5 files non-empty, no template placeholders, every `.ai/*` link in `AGENTS.md`
      resolves on disk.
- [x] **REQ-02 — Dedicated git repo.** `git init` inside `PixmintGamesLanding`, `.gitignore`,
      `README.md`; parent `agents` repo untouched.
      *Done when:* `git rev-parse --show-toplevel` prints this folder, ignore rules verified with
      `git check-ignore`, no staged files from `../`.
- [x] **REQ-03 — Landing page + stylesheet.** `site/index.html` + `site/assets/styles.css`: brand
      tokens as custom properties, one app card in Games, nav = About / Games / Privacy / Contact,
      skip link, `:focus-visible`, `prefers-reduced-motion`, contrast >= 4.5:1, sticky-header scroll
      margin, all anchors resolve. Legacy single-file source removed after the parity audit.
      *Done when:* Playwright at 1440px and 390px shows no overflow/dead links.
- [x] **REQ-04 — Head metadata.** Canonical, OG + Twitter cards, JSON-LD `Organization`, favicon set,
      `theme-color`, `color-scheme`.
      *Done when:* tags present and every referenced asset returns `200`.
- [x] **REQ-07 — Asset set.** `favicon-32.png`, `apple-touch-icon.png` (180), `icon-512.png`,
      `og-image.png` (1200x630), `wordmark.svg` in `site/assets/`.
      *Done when:* PIL reports exact dimensions and each file is < 200 KB.
- [x] **REQ-08 — Pages workflow.** `.github/workflows/pages.yml` uploads only `site/` via
      `actions/upload-pages-artifact` and publishes with `actions/deploy-pages`; permissions
      `pages: write` + `id-token: write`; concurrency configured.
      *Done when:* YAML parses and the artifact path is scoped to `site`.

## Wave 2 — legal + crawler files

- [x] **REQ-05 — Privacy policy.** `site/privacy.html`: Firebase Analytics opt-in (off by default),
      Crashlytics opt-out (on by default), no ad SDKs, no website cookies, retention windows,
      children's privacy, GDPR/CCPA rights, deletion via `contact@pixmintgames.com`.
      *Done when:* audited against the app policy, no AdMob mention, no bracket placeholders.
- [x] **REQ-06 — Static support files.** `site/404.html`, `site/robots.txt`, `site/sitemap.xml`,
      `site/CNAME`.
      *Done when:* sitemap lists canonical URLs only, `CNAME` is exactly `pixmintgames.com`,
      `robots.txt` references the sitemap.

## Wave 3 — verification harness

- [x] **REQ-09 — Local verification.** Detached static server on `site/`, Playwright desktop (1440)
      and mobile (390) screenshots, clean console/network, anchor and asset sweep, contrast check.
      *Done when:* report exists with screenshot paths and zero failures.

## Wave 4 — repository + Pages

- [x] **REQ-10 — GitHub repo live.** Public repo `gbalabanli/pixmintgames-landing`, pushed `main`,
      Pages enabled with `build_type=workflow`, custom domain `pixmintgames.com`.
      *Done when:* `gh api repos/gbalabanli/pixmintgames-landing/pages` shows `status: built` and
      `cname: pixmintgames.com`. *Note:* the API returns `status: null` for workflow builds even
      when the deployment succeeded; use `gh run list` + a live `curl` as the real check.

## Wave 5 — DNS + redirects

- [x] **REQ-11 — Canonical zone.** Cloudflare `pixmintgames.com`: 4x A + 4x AAAA to GitHub Pages,
      **DNS-only**; `www` proxied placeholder + 301 to apex.
      *Done when:* `dig` returns the Pages ranges and `curl -I https://www.pixmintgames.com/` is a
      single `301` to the apex.
- [x] **REQ-12 — Alias zone.** Cloudflare `pixmint.games`: proxied placeholder records + one 301
      rule to the `.com` apex preserving path and query.
      *Done when:* `https://pixmint.games/foo?bar=1` → `https://pixmintgames.com/foo?bar=1` in one hop.

## Wave 6 — HTTPS enforcement + production matrix

- [x] **REQ-13 — Enforce HTTPS.** Enable only after the Pages certificate is approved; run the full
      matrix (http/https x apex/www x both domains) + TLS check and capture evidence.
      *Done when:* `https_enforced: true`, certificate approved, all status codes match expectations.

## Second pass — visual + legal + indexing (2026-11-10)

- [x] **REQ-14 — Palette v2.** `site/assets/styles.css`: near-black ink `#0B0810`, surface
      `#171221`, subtle `#110D18`, border `#403A64`, brand `#FF5E1A` (hsl 18 100% 55%), brand-hot
      `#FFA733` (hsl 34 100% 60%), brand-deep `#E62600` (hsl 10 100% 45%), accent `#B370FF`
      (ambient glow only), cream `#FFF7F2`, muted `#B5ACC7`; `@media (color-gamut: p3)` overrides;
      `color-mix()` glow tokens; body ambient radial wash; single Games card full width; disabled
      CTA keeps its label colour.
      *Done when:* contrast >= AA on every text pair, Playwright 1440 + 390, no overflow.
- [x] **REQ-15 — Indexing off.** `noindex, nofollow` + `googlebot` metas on `index.html`,
      `privacy.html`, and `404.html`; `robots.txt` `User-agent: *` / `Disallow: /` with the
      launch-flip comment; sitemap kept but unreferenced.
      *Done when:* metas present on all three pages, robots body exact, sitemap file intact.
- [x] **REQ-16 — Legal identity.** `Bora Balabanli, operating as PixMint Games` +
      `Aydınevler Mahallesi 32/3, 34854 İstanbul (Anadolu), Türkiye` in the index footer + contact
      card, privacy §1 and §16, the privacy/404 footers, and JSON-LD (`legalName` + full
      `PostalAddress`).
      *Done when:* all locations updated, no placeholder text.

---

## Open items (TODO)

Owner: project owner (Bora). Resolve before or shortly after launch.

- [x] **REQ-09..13 pending:** local Playwright acceptance, GitHub repo + Pages, Cloudflare DNS/redirects,
      HTTPS enforcement.
- [x] **Legal entity details — shipped 2026-11-10.** Registered identity recorded as
      `Bora Balabanli, operating as PixMint Games`, `Aydınevler Mahallesi 32/3, 34854 İstanbul
      (Anadolu), Türkiye`. Applied to the index footer + contact card (`Developer:` line), privacy
      §1 (controller) and §16 (contact block), the privacy/404 footers, and the index JSON-LD
      (`legalName` + `PostalAddress`).
- [ ] **Enable indexing at launch.** Flip the three pages' robots metas to `index, follow`, remove
      the `User-agent: *` / `Disallow: /` pair from `site/robots.txt`, and restore
      `Sitemap: https://pixmintgames.com/sitemap.xml`. All three edits together; see `AGENTS.md` →
      Indexing.
- [x] **Contact mailbox — live 2026-11-10.** Cloudflare Email Routing enabled on `pixmintgames.com`
      (MX `route1/2/3.mx.cloudflare.net`, SPF `include:_spf.mx.cloudflare.net`, DKIM
      `cf2024-1._domainkey`), destination `pixmintgames@gmail.com` verified, rule
      `contact@pixmintgames.com` → forward → `pixmintgames@gmail.com` enabled. Outstanding: one
      end-to-end test message from an external account to confirm delivery.
- [ ] **Play Store listing URL.** Once the first app is published, replace the non-link
      "Coming soon to Google Play" span in the Games card with the real listing URL (`target="_blank"`
      + `rel="noopener"`), and update the JSON-LD `sameAs` if applicable.
- [ ] **Terms of service page (optional).** Only needed if the studio wants contractual terms
      separate from the privacy policy; would add `site/terms.html` plus a sitemap entry.
- [ ] **Turkish locale (optional).** English-only was a locked decision for this release. A future
      `tr` locale would need `site/tr/` (or `/tr.html`), `hreflang` pairs, and translated privacy text
      reviewed for legal accuracy.
