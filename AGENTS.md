# Personal website router: agent instructions

This repository is the stable public address (and printed QR code) for Joey
Wilkes's personal website. GitHub Pages renders `index.html`, which redirects
visitors to the current destination.

## Environments

| Environment | Address | Role here |
| --- | --- | --- |
| Dev | Local Liquid preview, also shared on the owner's tailnet | Render and check changes before a PR |
| Test | A throwaway duplicate Replit app | Not a router destination |
| Staging | https://joeywilkes12.github.io/personal-website-backup/ | Failover destination (PR branch `failover/github-pages-backup`) |
| Production | https://joey-wilkes12-website-2026-10-04-static.replit.app, moving to https://joey-wilkes12-home.replit.app | The destination on `main` |

The full environment reference lives in the owner's private source repository.

## Rules

- Change only `redirect_url` at the top of `index.html`; keep it an absolute
  HTTPS URL in double quotes. The QR image never changes.
- Work on a feature branch or worktree and open a PR. Merge, or push to `main`,
  only with the owner's explicit approval for that specific change: `main` is
  what GitHub Pages publishes.
- **Failover:** when Production degrades, the owner merges the failover PR to
  route to Staging, then uses **Revert** on it to route back.
- Before a PR, render the preview and run `scripts/check_links.py` and
  `scripts/browser_check.js` as described in [MAINTENANCE.md](MAINTENANCE.md).
- Share any local preview on the owner's tailnet
  (`Tailscale serve --bg --http=<port> <port>`) so it can be reviewed from a
  phone.
