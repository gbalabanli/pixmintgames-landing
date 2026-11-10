# Lessons learned

Infrastructure pitfalls already encountered or identified for this project. Read before touching DNS,
Pages, or git. Each entry has the symptom so it is recognizable in the wild.

---

## 1. Proxying the apex blocks GitHub Pages certificate issuance

**Symptom:** Cloudflare proxies `pixmintgames.com` (orange cloud); GitHub Pages custom-domain check
stays at "Certificate not yet approved" indefinitely. HTTPS either fails or serves a Cloudflare edge
certificate while Pages still thinks the domain is unverified.

**Cause:** GitHub Pages validates domain ownership with an HTTP-01 challenge against the apex. With
Cloudflare proxying, the challenge request never reaches GitHub, so issuance cannot complete.

**Rule:** keep the apex A/AAAA records **DNS-only (grey cloud)** from the moment they are created until
Pages reports the certificate approved. Only then consider enabling HTTPS enforcement (REQ-13) and,
separately, any proxying decision. Never enable proxy + "Full (strict)" against GitHub Pages and
assume it will sort itself out.

---

## 2. Cloudflare Redirect Rules only fire on proxied traffic

**Symptom:** a Single Redirect exists for `pixmint.games/*`, but the hostname resolves to nothing /
times out / returns the placeholder instead of a 301.

**Cause:** redirect rules are evaluated at the Cloudflare edge, and edge processing only happens for
records with the orange cloud enabled. A DNS-only record bypasses the edge entirely, so the rule is
never consulted. A proxied record with no origin is fine for redirect-only zones.

**Rule:** redirect-only hostnames need **proxied** placeholder records. `A 192.0.2.1` (RFC 5737
documentation range) with proxy on is the safe placeholder: never contacted, never a real origin,
and it keeps the edge in the path so the 301 fires. Do the same for `www.pixmintgames.com`.

---

## 3. Cloudflare caches 301s at the edge — test with cache-busting

**Symptom:** you fix a redirect target or change `www` behaviour, but `curl -I` still shows the old
`Location` or a stale status long after saving the rule.

**Cause:** Cloudflare caches redirect responses (including 301s) at the edge and browsers cache 301s
aggressively. Neither respects your edit timing.

**Rule:** verify with a cache-busting query string and headers:
`curl.exe -sI --max-time 15 "https://pixmint.games/foo?cb=$([guid]::NewGuid())"` and add
`-H "Cache-Control: no-cache"`. Use a fresh `curl.exe` invocation rather than a browser tab, which
may serve a disk-cached 301. Expect `curl` to be the only reliable witness during cut-over.

---

## 4. Free-plan GitHub Pages requires a public repository

**Symptom:** Pages settings are unavailable, or deploys fail with a plan/permission error, on a
private repo.

**Cause:** GitHub Pages on the Free plan only publishes from public repositories. (Private-repo Pages
requires a paid plan.)

**Rule:** the repo `gbalabanli/pixmintgames-landing` is public by design. Treat every committed file
as world-readable: no Cloudflare tokens, no zone/account IDs paired with tokens, no `.env`, no draft
legal text with personal data. Keep credentials in the shell environment only.

---

## 5. This project is nested inside another git repository

**Symptom:** `git status` in the project folder lists dozens of unrelated sibling projects, or a
commit accidentally stages files from the parent `agents` repo.

**Cause:** `C:\Users\Bora\Desktop\Workspace\agents` is itself a git repository. `PixmintGamesLanding`
lives inside it and must be its own repo; the parent is never part of this release.

**Rule:** run `git rev-parse --show-toplevel` before any git operation and confirm it prints
`.../agents/PixmintGamesLanding`. Always pass the explicit project path (`git -C <path> ...`). Never
run `git add -A` from a parent directory, never `git init` in the parent, and never commit from a
shell whose cwd drifted. If the toplevel is wrong, stop and fix it before staging anything.

---

## 6. `404.html` and `CNAME` only work when served, not from `file://`

**Symptom:** opening `site/index.html` directly (double-click / `file://`) shows broken relative
links, `CNAME` appears to do nothing, and unknown paths do not render the custom 404. Some asset
paths also resolve differently than in production.

**Cause:** `CNAME` is a GitHub Pages artifact instruction, not something a browser reads. Custom 404
handling is a server/CDN behaviour. `file://` has no HTTP status codes, no host mapping, and
different path resolution rules.

**Rule:** always preview through HTTP — `python -m http.server 8080 --directory site`, started
**detached** (never in the foreground, it blocks the agent session), then verify with `curl.exe`
against `127.0.0.1:8080`. Judge `404.html` and `CNAME` only after a real Pages deploy; local HTTP
proves markup and links, not Pages semantics.

---

## 7. Static-site edits are only real after the artifact redeploys

**Symptom:** a file looks correct in the working tree and on the local server, but production still
shows the old content.

**Cause:** Pages serves the last successfully deployed artifact. A commit that was not pushed, a
workflow that failed, or a push that did not touch a path matched by the workflow's triggers all
leave production unchanged. GitHub Pages also caches aggressively at the CDN.

**Rule:** after pushing, check `gh run list --workflow pages.yml --limit 3` and
`gh api repos/gbalabanli/pixmintgames-landing/pages` for `status: built` before judging production.
When verifying, use a cache-busted URL. Confirm the deployed commit matches the intended one.

---

## 8. GitHub "Enforce HTTPS" reports true before the edge redirects

**Symptom:** `gh api .../pages` returns `https_enforced: true` and the certificate is `approved`,
but `http://pixmintgames.com/` still answers `200 OK` from GitHub's Fastly edge — including for a
cache-busting query string.

**Cause:** the flag is stored immediately, but the http→https redirect only appears after the Pages
site is rebuilt and the edge configuration refreshes. CDN-cached 200s can also mask the change.

**Rule:** set `https_enforced`, then force a build (`gh workflow run pages.yml --ref main`), wait for
the run to finish, and re-test with a unique query string (`?cb=<random>`). Only then judge the
result. Expect minutes, not seconds.

## 9. Account-owned Cloudflare tokens fail `/user/tokens/verify`

**Symptom:** `GET /client/v4/user/tokens/verify` returns `{"success":false,"errors":[{"code":1000,
"message":"Invalid API Token"}]}` even though the same token can read and write zones.

**Cause:** that endpoint validates *user*-owned tokens only; account-owned tokens are not visible
there.

**Rule:** verify with `GET /client/v4/zones` (or any zone-scoped call) instead. A successful zone
list proves the token and its permissions; the verify endpoint is not authoritative here.

## 10. Redirect-only Cloudflare zones need proxied placeholder records

**Symptom:** a Single Redirect rule on a zone with no DNS records never fires — the hostname does
not even resolve.

**Cause:** redirect rules are evaluated at the edge, so the request must reach Cloudflare first,
which requires a **proxied** (orange-cloud) record. It does not need a real origin.

**Rule:** create a proxied `A` record to `192.0.2.1` for every hostname the redirect covers, then
add the rule. Never proxy the canonical apex that GitHub Pages terminates TLS for.

## 11. Pages API `status` is `null` for workflow builds

**Symptom:** `gh api .../pages` shows `status: null` while the site is live and the workflow run is
green.

**Cause:** the `status` field describes the legacy branch-build pipeline; with
`build_type=workflow` it is not populated.

**Rule:** treat `gh run list --workflow pages.yml` plus a live `curl` as the real deployment check.
Do not block a release on `status: built`.

## 12. Gradient-clipped text ignores `text-shadow`

**Symptom:** the `.logo` uses `background-clip: text` with `-webkit-text-fill-color: transparent`.
Adding `text-shadow` for a glow either does nothing or paints a solid halo that swallows the
gradient; a child `<span>` inside the logo also disappears or keeps the parent's transparency.

**Cause:** `text-shadow` is derived from the text's glyph colour, which is transparent once the
background is clipped to the text — it does not read the background gradient. Child spans inherit
`-webkit-text-fill-color: transparent` unless it is reset.

**Rule:** glow gradient-clipped text with `filter: drop-shadow(0 0 14px var(--glow-brand))`; it
follows the painted glyph shape. Reset both `color` and `-webkit-text-fill-color` on child spans that
must render normally (`.logo span` uses `-webkit-text-fill-color: var(--muted)`). Never stack
`text-shadow` on `background-clip: text`.

## 13. `.card a` outranks `.btn` and repaints button labels

**Symptom:** a link styled as a button inside a card renders brand-coloured text on a brand-coloured
fill — an unreadable label — even though the `.btn` block sets `color: var(--ink)`.

**Cause:** `.card a` has specificity (0,1,1); `.btn` has (0,1,0). The descendant selector wins
regardless of source order, so the card's link colour overrides the button's label colour.

**Rule:** scope button rules to the card context with equal-or-higher specificity:
`.card .btn { color: var(--ink); text-decoration: none; }` and
`.card .btn-disabled { color: var(--muted); }` (repeat for `.contact-card` and `.policy-box` if they
share the link rule). When a label colour looks wrong, inspect the computed style and the competing
selectors — not just the `.btn` block.
