# Personal website router

A permanent QR-code address that redirects immediately to Joey Wilkes online.

- Public website: https://joeywilkes12.github.io/personal-website-router/
- Repository: https://github.com/JoeyWilkes12/personal-website-router
- QR asset: `personal-website-router-qr.png` (1176 × 1176 pixels, 300 DPI, black on white, high error correction).

See the [maintenance guide](MAINTENANCE.md) for changing or reverting the
destination, local and managed-worktree workflows, validation, commit/push
commands, PR approval, and publication.

## Change the destination

Edit only the `redirect_url` value at the top of `index.html`:

```yaml
redirect_url: "https://Joey-wilkes12-website-2026-10-04-static.replit.app/"
```

Commit and push a feature branch, then open a PR. After you approve and merge it
into `main`, GitHub Pages runs Jekyll automatically and replaces
every `page.redirect_url` reference with that value. This updates the JavaScript
redirect, HTML refresh, fallback link, canonical link, and structured metadata
together. Keep the URL in double quotes and use an absolute HTTPS address.

JavaScript uses `location.replace()` so the browser's Back button doesn't loop
through the router. The HTML refresh also works with JavaScript disabled. The
visible link provides a manual way to continue if automatic navigation is blocked.
This is a browser redirect served with HTTP 200, rather than an HTTP 301/302.

The QR encodes the **router's public address**, not the destination. Printed QR
codes keep working after a destination change. Keep the repository name and Pages
address stable. Allow GitHub Pages a few minutes to publish a push.

## Publishing and checks

GitHub Pages publishes the root of the `main` branch with its built-in Jekyll build.
Do not add `.nojekyll`: it would disable the URL substitutions. Opening the source
HTML directly also skips Jekyll; preview the generated site instead.

Run the automated hyperlink and generated-content regression check before a
release, supplying a rendered local preview URL, then verify the public deployment.
The maintenance guide includes a complete preview setup using
`scripts/render_preview.rb`:

```sh
python3 scripts/check_links.py --site-url http://127.0.0.1:4178/personal-website-router/
python3 scripts/check_links.py
```

The checker follows HTTP redirects, fails on HTTP 4xx/5xx, and checks the published
redirect destinations, metadata, sitemap, robots file, and PNG. Browser regression
coverage checks immediate navigation with and without JavaScript, Back-button
behavior, the fallback link, keyboard focus, and overflow at 390px and 1440px.
With Playwright CLI open on that localhost preview, run
`run-code --filename scripts/browser_check.js`. The test substitutes a local
destination so the browser does not visit external sites.

`robots.txt` allows public content. Because this is a GitHub project site, its file
is under the project path; domain-wide crawler rules belong to the account's root
site. The canonical URL points crawlers to the current destination.

## Shared QR source

The workspace's reusable source is
`shared-assets/qr/personal-website-router-qr.png`. This repository includes an
identical copy so deployment never needs access to the parent workspace.
Regenerate the shared source with the QR Code Generator skill only if the stable
Pages address changes, then copy it here. The four-module white border is the
required quiet zone; preserve it when printing or placing the image.
