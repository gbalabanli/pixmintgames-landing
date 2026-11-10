# Tasks — PixMint Games landing release

Source of truth for scope: `reqs-manifest.md` (13 requirements, six waves). This file mirrors that
tracker with acceptance criteria and status. Update checkboxes as work lands; never edit the manifest.

Legend: `[ ]` not started · `[/]` in progress · `[x]` done and verified.

## Wave 1 — parallel foundation

- [x] **REQ-01 — Workspace docs.** `AGENTS.md` + `.ai/{ARCHITECTURE,TASKS,FEATURE_HISTORY,LESSONS_LEARNED}.md`
      generated with the init-workspace skill, then rewritten with real project content: file layout,
      detached preview command, deploy + DNS commands, boundaries, verification checklist.
      *Done when:* 5 files non-empty, no template placeholders, every `.ai/*` link in `AGENTS.md`
      resolves on disk.
- [ ] **REQ-02 — Dedicated git repo.** `git init` inside `PixmintGamesLanding`, `.gitignore`,
      `README.md`; parent `agents` repo untouched.
      *Done when:* `git rev-parse --show-toplevel` prints this folder, ignore rules verified with
      `git check-ignore`, no staged files from `../`.
- [ ] **REQ-03 — Landing page + stylesheet.** `site/index.html` + `site/assets/styles.css`: brand
      tokens as custom properties, one app card in Games, nav = About / Games / Privacy / Contact,
      skip link, `:focus-visible`, `prefers-reduced-motion`, contrast >= 4.5:1, sticky-header scroll
      margin, all anchors resolve. Legacy single-file source removed after the parity audit.
      *Done when:* Playwright at 1440px and 390px shows no overflow/dead links.
- [ ] **REQ-04 — Head metadata.** Canonical, OG + Twitter cards, JSON-LD `Organization`, favicon set,
      `theme-color`, `color-scheme`.
      *Done when:* tags present and every referenced asset returns `200`.
- [ ] **REQ-07 — Asset set.** `favicon-32.png`, `apple-touch-icon.png` (180), `icon-512.png`,
      `og-image.png` (1200x630), `wordmark.svg` in `site/assets/`.
      *Done when:* PIL reports exact dimensions and each file is < 200 KB.
- [ ] **REQ-08 — Pages workflow.** `.github/workflows/pages.yml` uploads only `site/` via
      `actions/upload-pages-artifact` and publishes with `actions/deploy-pages`; permissions
      `pages: write` + `id-token: write`; concurrency configured.
      *Done when:* YAML parses and the artifact path is scoped to `site`.

## Wave 2 — legal + crawler files

- [ ] **REQ-05 — Privacy policy.** `site/privacy.html`: Firebase Analytics opt-in (off by default),
      Crashlytics opt-out (on by default), no ad SDKs, no website cookies, retention windows,
      children's privacy, GDPR/CCPA rights, deletion via `contact@pixmintgames.com`.
      *Done when:* audited against the app policy, no AdMob mention, no bracket placeholders.
- [ ] **REQ-06 — Static support files.** `site/404.html`, `site/robots.txt`, `site/sitemap.xml`,
      `site/CNAME`.
      *Done when:* sitemap lists canonical URLs only, `CNAME` is exactly `pixmintgames.com`,
      `robots.txt` references the sitemap.

## Wave 3 — verification harness

- [ ] **REQ-09 — Local verification.** Detached static server on `site/`, Playwright desktop (1440)
      and mobile (390) screenshots, clean console/network, anchor and asset sweep, contrast check.
      *Done when:* report exists with screenshot paths and zero failures.

## Wave 4 — repository + Pages

- [ ] **REQ-10 — GitHub repo live.** Public repo `gbalabanli/pixmintgames-landing`, pushed `main`,
      Pages enabled with `build_type=workflow`, custom domain `pixmintgames.com`.
      *Done when:* `gh api repos/gbalabanli/pixmintgames-landing/pages` shows `status: built` and
      `cname: pixmintgames.com`.

## Wave 5 — DNS + redirects

- [ ] **REQ-11 — Canonical zone.** Cloudflare `pixmintgames.com`: 4x A + 4x AAAA to GitHub Pages,
      **DNS-only**; `www` proxied placeholder + 301 to apex.
      *Done when:* `dig` returns the Pages ranges and `curl -I https://www.pixmintgames.com/` is a
      single `301` to the apex.
- [ ] **REQ-12 — Alias zone.** Cloudflare `pixmint.games`: proxied placeholder records + one 301
      rule to the `.com` apex preserving path and query.
      *Done when:* `https://pixmint.games/foo?bar=1` → `https://pixmintgames.com/foo?bar=1` in one hop.

## Wave 6 — HTTPS enforcement + production matrix

- [ ] **REQ-13 — Enforce HTTPS.** Enable only after the Pages certificate is approved; run the full
      matrix (http/https x apex/www x both domains) + TLS check and capture evidence.
      *Done when:* `https_enforced: true`, certificate approved, all status codes match expectations.

---

## Open items (TODO)

Owner: project owner (Bora). Resolve before or shortly after launch.

- [ ] **REQ-09..13 pending:** local Playwright acceptance, GitHub repo + Pages, Cloudflare DNS/redirects,
      HTTPS enforcement.
- [ ] **Legal entity details.** Supply the exact registered company name from the vergi levhası and
      the registered address. Apply to the site footer (currently `PixMint Games · İstanbul, Türkiye`)
      and to the data-controller block in `site/privacy.html`. No bracket placeholders may ship in
      the meantime.
- [ ] **Contact mailbox.** Confirm `contact@pixmintgames.com` actually receives mail. Consider
      Cloudflare Email Routing (forward to a personal inbox) since the zone is already on Cloudflare,
      then send a test message from an external account.
- [ ] **Play Store listing URL.** Once the first app is published, replace the non-link
      "Coming soon to Google Play" span in the Games card with the real listing URL (`target="_blank"`
      + `rel="noopener"`), and update the JSON-LD `sameAs` if applicable.
- [ ] **Terms of service page (optional).** Only needed if the studio wants contractual terms
      separate from the privacy policy; would add `site/terms.html` plus a sitemap entry.
- [ ] **Turkish locale (optional).** English-only was a locked decision for this release. A future
      `tr` locale would need `site/tr/` (or `/tr.html`), `hreflang` pairs, and translated privacy text
      reviewed for legal accuracy.
