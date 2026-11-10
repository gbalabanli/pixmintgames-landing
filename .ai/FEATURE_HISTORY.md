# Feature history

Dated, newest first. Each entry records what changed, why, and any decision that future work must
not silently reverse.

---

## 2026-11-10 — Contact mailbox live via Cloudflare Email Routing

**Goal:** make `contact@pixmintgames.com` — published on every page and in the privacy policy —
actually receive mail without paying for a hosted mailbox.

### What shipped

- Email Routing enabled on `pixmintgames.com`; Cloudflare added MX `route1/2/3.mx.cloudflare.net`,
  SPF `v=spf1 include:_spf.mx.cloudflare.net ~all`, and the `cf2024-1._domainkey` DKIM record.
- Destination `pixmintgames@gmail.com` verified 2026-11-10 18:50 UTC (account scope).
- Rule `contact@pixmintgames.com` → forward → `pixmintgames@gmail.com`, enabled.
- Confirmed on public DNS (1.1.1.1): three MX records plus the SPF TXT.

### Decisions

1. **Forwarding, not a hosted mailbox.** No new credentials, no IMAP client to maintain, and replies
   leave from Gmail under the owner's own account.
2. **Apex web records untouched.** The GitHub Pages A/AAAA set stays DNS-only; MX is independent of
   the web host, so mail and site can be changed separately.
3. **Account-scoped destinations vs zone-scoped rules.** The API refuses to create a rule until the
   destination is verified (`2054`), so the owner has to click Cloudflare's verification mail first.

### Deliberately not done

- No catch-all, and no aliases for `privacy@` or `support@` (one extra rule each if wanted).
- No DMARC record yet.
- No end-to-end delivery test from an external mailbox at ship time.

---

## 2026-11-10 — Second pass: palette v2, P3 overrides, legal identity, indexing off (REQ-14 … REQ-16)

**Goal:** replace the first-pass palette, which read flat on the near-black background, with a hotter
orange/ink system; let the lone game card use the full content width; state the legal identity on
every page; and keep the pre-launch site out of every search index. Shipped 2026-11-10.

### What shipped

- **Footer legal line** trimmed and set in caps: `BORA BALABANLI · Aydınevler Mahallesi 32/3,
  34854 İstanbul (Anadolu), Türkiye` (the studio name was redundant there; the developer name is
  now uppercase everywhere it appears, including the contact card, privacy §1/§16 and JSON-LD
  `legalName`).
- **Palette v2** in `site/assets/styles.css`: `--ink #0B0810`, `--surface #171221`,
  `--surface-subtle #110D18`, `--border #403A64`, `--brand #FF5E1A` (hsl 18 100% 55%),
  `--brand-hot #FFA733` (hsl 34 100% 60%), `--brand-deep #E62600` (hsl 10 100% 45%),
  `--accent #B370FF` (hsl 268 100% 72%, ambient glow only), `--cream #FFF7F2`,
  `--muted #B5ACC7`.
- **Display-P3 override:** a `@media (color-gamut: p3)` block re-declares brand, brand-hot,
  brand-deep, accent, and cream with `color(display-p3 …)` values, so wide-gamut screens get the
  same hues at higher chroma. sRGB hex values remain the fallback.
- **Glow system:** `--glow-brand`, `--glow-hot`, and `--brand-tint` are `color-mix()` derivatives of
  the brand tokens, used on the logo (drop-shadow), buttons, cards, chips, focus rings, h2s, and the
  body's two ambient radial washes (brand 10%, accent 9%).
- **Full-width single card:** `.grid:has(> .card:only-child)` collapses to one column and the lone
  card drops its 680px cap; `.card > p` and `.card .card-lead` cap copy at 62ch so the wider card
  stays readable.
- **Disabled-CTA fix:** the "Coming soon to Google Play" pill is a `.btn-disabled` span, not a dead
  link — surface fill, muted label, no hover lift or glow. Explicit `.card .btn` /
  `.card .btn-disabled` rules restore the label colour that `.card a` had been overriding.
- **Legal identity:** `Bora Balabanli, operating as PixMint Games` +
  `Aydınevler Mahallesi 32/3, 34854 İstanbul (Anadolu), Türkiye` now appears in the index footer,
  the index contact card (`Developer:` line), privacy §1 (controller) and §16 (contact block), the
  privacy/404 footers, and the index JSON-LD (`legalName` + full `PostalAddress`).
- **Indexing off:** all three pages carry `noindex, nofollow` robots + googlebot metas; `robots.txt`
  is `User-agent: *` / `Disallow: /` with the launch-flip comment; `sitemap.xml` is kept but its
  `Sitemap:` reference is commented out.

### Decisions

1. **Palette v2 replaces v1 rather than layering a second theme.** The v1 orange on the v1 ink
   measured 4.84:1 — technically AA but visually flat, with little separation between surface and
   page. The v2 ink is darker and the brand hotter; the brand now measures 6.50:1 on `--ink`,
   6.00:1 on `--surface`, and 6.27:1 on `--surface-subtle`, so it can carry text.
2. **P3 is an enhancement, not a requirement.** The sRGB values stay authoritative for every
   display; the `color-gamut: p3` block only upgrades capable devices, and every glow resolves
   through the tokens so the override propagates.
3. **Accent purple is ambient only.** `--accent` never carries text or a control state; it exists
   solely for the body's second radial wash, which keeps the near-black background from going dead.
4. **One card fills the row.** With a single game, `auto-fit` left an empty column and a 680px card
   stranded in a wide container. The `:has(:only-child)` rule is conditional, so adding a second
   card restores the normal grid with no further CSS.
5. **Indexing is off on both layers.** `robots.txt` alone does not stop indexing of already-known
   URLs, and metas alone do not stop crawling, so both are set. The site is live but intentionally
   unlisted until launch; the flip is documented in `AGENTS.md` → Indexing.

### Deliberately not done

- No change to copy, nav, page structure, fonts, or the zero-JS/zero-build constraints.
- No new games, no Play Store URL, no social links, no analytics, no cookie banner.
- No HSTS, no Cloudflare proxy on the apex, no Email Routing.
- `sitemap.xml` is not deleted — it stays valid and is re-referenced at the launch flip.

## 2026-11-10 — Initial public site: workspace docs + landing release (REQ-01)

**Goal:** put the studio's existing one-page landing online at `https://pixmintgames.com` on GitHub
Pages, make `pixmint.games` redirect to it, and document the project so later work starts from facts
instead of guesswork.

### What shipped in this session (REQ-01)

- `AGENTS.md` rewritten from the init-workspace template into a project-specific entry point:
  purpose, stack, exact `site/` layout, detached local-preview procedure, deploy commands
  (`gh repo create`, Pages enable/bind, push), the Cloudflare DNS table, a verification checklist,
  and hard boundaries (no secrets, no build step, no edits to the parent `agents` repo).
- `.ai/ARCHITECTURE.md` — request/DNS flow browser → Cloudflare → GitHub Pages CDN → `site/`,
  file responsibilities, content-ship lifecycle, redirect-zone placement, brand tokens, asset
  provenance, security/privacy posture.
- `.ai/TASKS.md` — the 13 manifest requirements as wave-grouped checkboxes with acceptance
  criteria, plus the open items list (legal entity, mailbox, Play Store URL, optional Terms,
  optional Turkish locale).
- `.ai/FEATURE_HISTORY.md` — this log.
- `.ai/LESSONS_LEARNED.md` — six concrete infrastructure pitfalls already hit or known in advance
  (apex proxying vs. certificate issuance, redirects requiring proxied records, edge-cached 301s,
  public-repo requirement, nested git repo, `404.html`/`CNAME` needing a real server/artifact).
- Generated with `init-workspace` (`python .../init_workspace.py --path . --output-dir .ai`) and then
  fully replaced with the content above so no template scaffolding remains.
- **Site set complete (2026-11-10):** `site/` now holds `index.html`, `privacy.html`, `404.html`,
  `CNAME`, `robots.txt`, `sitemap.xml`, a root `favicon.ico`, and six image assets plus `styles.css`
  in `site/assets/`; the legacy `one-page-landing.html` single-file source was removed after the
  parity audit.

### Release pieces landing under this release

| Area | Files | Status at time of writing |
| --- | --- | --- |
| Landing page | `site/index.html`, `site/assets/styles.css` | Content ported from `one-page-landing.html`, brand tokens applied |
| Head metadata | `site/index.html` `<head>` | Canonical, OG/Twitter, JSON-LD `Organization`, favicons, `theme-color` |
| Legal | `site/privacy.html` | Standalone policy at the Play Console URL |
| Support files | `site/404.html`, `site/robots.txt`, `site/sitemap.xml`, `site/CNAME` | Present, canonical host only |
| Assets | `site/assets/{favicon-32,apple-touch-icon,icon-512,og-image}.png`, `wordmark.svg` | Derived from the app repo's brand/store folders |
| CI | `.github/workflows/pages.yml` | Uploads only `site/`, deploys via `deploy-pages` |
| Git | dedicated repo in this folder | Parent `agents` repo untouched |

Deploy, DNS cut-over, and HTTPS enforcement are tracked as REQ-10…REQ-13 and are not claimed as
done by this entry.

### Decisions made

1. **Brand tokens centralized as CSS custom properties.** Ink `#1E1B2E`, orange `#F2541B`
   (hover `#D8480F`), cream `#F4EEE9`, surface `#2A2540`, surface-subtle `#241F35`, border
   `#3A3450`, muted `#A9A3BE`. One source of truth in `styles.css`; components reference variables
   only, so a palette change is a one-block edit. Fonts: Orbitron (display) + Plus Jakarta Sans
   (body), Google Fonts with `display=swap`.
2. **One app card, not a grid.** Only one game exists publicly. A single centered card with a
   non-link "Coming soon to Google Play" state avoids a dead `href="#"` and avoids implying a
   portfolio that does not exist yet. Adding games later means repeating the card, not redesigning.
3. **Dedicated `privacy.html` instead of a `#privacy` anchor.** Play Console requires a stable URL
   for the privacy policy; a standalone page survives landing-page redesigns and can be linked from
   the store listing directly. The old in-page anchor was removed so there is exactly one policy.
4. **English only.** The audience and the app listings are English; a half-translated site is worse
   than a monolingual one. Turkish is deferred as an optional item in `.ai/TASKS.md` and would need
   `hreflang` and a legally reviewed translation.
5. **No framework, no build step, no JS.** The artifact is the source. This keeps Pages deploys
   atomic and fast and removes an entire class of toolchain failures.
6. **Apex is canonical and DNS-only; `www`/alias zones are proxied redirectors.** Canonical host
   keeps one origin for SEO and cookies (none are set). Proxy on the redirect zones is mandatory for
   Cloudflare redirect rules to fire.
7. **Repo must be public.** Free-plan GitHub Pages does not publish from private repositories.
   Consequence: no secrets in the repo, ever.

### Deliberately not done

- No analytics or cookie banner on the site (the site sets no cookies; the app's analytics
  disclosures live in the privacy policy).
- No social links, no newsletter form, no contact form backend — `mailto:` only.
- No Terms page and no Turkish locale (see open items).
- No exact legal entity name/registered address yet; the footer uses the approved fallback
  `PixMint Games · İstanbul, Türkiye` rather than shipping a bracket placeholder.

## 2026-11-10 — Release shipped: repo, Pages, DNS, HTTPS (REQ-10 … REQ-13)

**Goal:** put the finished site on the real domain and retire the alias zone.

**What shipped**
- Public repo `gbalabanli/pixmintgames-landing`, first commit `5b1b3f3`, workflow run
  `42847144949` green; Pages `build_type=workflow`, custom domain `pixmintgames.com`.
- Cloudflare `pixmintgames.com`: apex 4×A (`185.199.108.153`–`185.199.111.153`) + 4×AAAA
  (`2606:50c0:8000::153`–`8003::153`) **DNS-only**; `www` proxied placeholder `192.0.2.1` +
  Single Redirect → apex.
- Cloudflare `pixmint.games`: apex + `www` proxied placeholders, one 301 rule →
  `https://pixmintgames.com` with path and query preserved.
- Both zones: SSL mode Full (strict), Always Use HTTPS on. Pages certificate approved
  (expires 2027-02-08), `https_enforced: true`.
- Production matrix (13 URLs) all as designed: http apex 301 → https, https apex 200,
  `www` 301, alias zone 301 with `/some/path?x=1&y=2` preserved, custom 404 served at 2,890 B.

**Decisions**
1. **Apex stays DNS-only.** Cloudflare proxying would break GitHub's HTTP-01 issuance; GitHub's
   CDN already provides edge caching, so the proxy buys nothing for the canonical host.
2. **Redirect-only zones use a proxied `192.0.2.1` placeholder.** Redirect rules only fire on
   proxied traffic, and there is no origin to point at.
3. **Enforce HTTPS was set through the API, then a rebuild was forced.** The flag alone did not
   change edge behaviour; see LESSONS_LEARNED §8.
4. **Commit identity is repo-local** (`gbalabanli <gbalabanli@users.noreply.github.com>`); no global
   git config was touched.

**Deliberately not done:** no Cloudflare proxy on the apex, no HSTS, no Email Routing, no analytics
on the site, no legal-entity line beyond `PixMint Games · İstanbul, Türkiye` (owner TODO).

---

New entries go directly above this line, newest first, in the same shape: title with date and REQ
ids, goal, what shipped, decisions with rationale, and what was deliberately excluded.
