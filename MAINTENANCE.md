# Change, revert, and publish the website router

The QR code and public address stay fixed:

```text
https://joeywilkes12.github.io/personal-website-router/
```

Change only `redirect_url` at the top of `index.html`. GitHub Pages renders the
JavaScript redirect, HTML refresh, fallback link, canonical link, and metadata
from that one setting. The router is served by GitHub Pages; pointing it at a
Replit URL does not republish the Replit application.

## 1. Choose where to work

The router is an **independent repository** inside the personal-websites
workspace. Commands must run inside the router checkout, not its parent.

### Your existing local checkout, without a worktree

For changes you make yourself, open a terminal here:

```sh
cd "/Users/joeywilkes/Desktop/Scripts & Code/personal websites/personal-website-router"
git rev-parse --show-toplevel
git remote get-url origin
git status --short
```

The repository root must be the router directory, and the remote must be
`https://github.com/JoeyWilkes12/personal-website-router.git`. Start with a clean
checkout. Preserve any existing edits before switching branches.

```sh
git fetch origin
git switch main
git pull --ff-only origin main
git switch -c codex/update-router-destination
```

Choose a fresh branch name for each change. For a **Codex task**, your standing
instructions require a registered, attached managed worktree. Direct work in
this local checkout requires your explicit exception; these commands do not
grant that exception.

### A Codex-managed worktree

Select or add the **router directory itself** as the Codex project. Start its
chat in Worktree mode from the latest `main`, or ask Codex to reuse/create a
managed worktree attached to that chat. If the tools are bound to the parent
repository, open a router-specific chat or explicitly authorize an exception.
Do not substitute an unregistered `git worktree add` or temporary clone.

Wait for both creation and attachment to finish. In the returned checkout:

```sh
cd "/absolute/path/returned/by/the/Codex/worktree/manager"
git rev-parse --show-toplevel
git remote get-url origin
git status --short
git worktree list --porcelain
git rev-parse HEAD
git branch --show-current
```

The path above is a placeholder: use the actual full path returned by the
manager. Git's list verifies Git registration; the chat's worktree attachment
verifies Codex registration. Neither check replaces the other.

Managed worktrees may start at a detached commit. If no working branch exists,
create one in that worktree:

```sh
git switch -c codex/update-router-destination
```

If the manager already selected a branch, use it. Keep the worktree on its own
feature branch; `main` may already be checked out in the original checkout.
Use Codex Handoff to move the chat when needed, and archive/restore through
Codex for cleanup. See [official worktree guidance](https://developers.openai.com/codex/app/worktrees).

## 2. Change the destination

Edit `index.html` in your chosen checkout. For the Replit website, set:

```yaml
redirect_url: "https://Joey-wilkes12-website-2026-10-03.replit.app"
```

Keep an absolute HTTPS URL in double quotes. The QR PNG does not change.

```sh
git diff --check
git diff -- index.html
```

## 3. Check before committing

Check the external destination through its HTTP redirect chain:

```sh
curl --fail --show-error --location --output /dev/null \
  --write-out 'HTTP %{http_code}: %{url_effective}\n' \
  https://Joey-wilkes12-website-2026-10-03.replit.app
```

Then render a local preview and run the existing automated checks. A raw
`python3 -m http.server` over the source directory does **not** process Liquid.
The following preview uses the Liquid engine; GitHub Pages performs the final
Jekyll build after publication.

From the chosen router checkout, prepare the renderer dependency once per
terminal session:

```sh
ROUTER_GEMS="$(mktemp -d "${TMPDIR:-/tmp}/router-gems.XXXXXX")"
gem install liquid --version 4.0.4 --install-dir "$ROUTER_GEMS" --no-document
ROUTER_PREVIEW="$(mktemp -d "${TMPDIR:-/tmp}/router-preview.XXXXXX")"
ruby -I "$ROUTER_GEMS/gems/liquid-4.0.4/lib" scripts/render_preview.rb \
  --output-dir "$ROUTER_PREVIEW"
python3 -m http.server 4178 --bind 127.0.0.1 --directory "$ROUTER_PREVIEW"
```

Keep that terminal running. In a second terminal, `cd` to the same chosen router
checkout and run:

```sh
python3 scripts/check_links.py --site-url http://127.0.0.1:4178/personal-website-router/
```

The checker verifies the rendered destination in all references, follows the
external destination's redirects, fails on HTTP 4xx/5xx, and checks the QR PNG,
sitemap, and robots file.

For the required browser regression check, use Playwright CLI:

```sh
npx --yes --package @playwright/cli playwright-cli \
  --session router-check open http://127.0.0.1:4178/start.html
npx --yes --package @playwright/cli playwright-cli \
  --session router-check run-code --filename scripts/browser_check.js
npx --yes --package @playwright/cli playwright-cli \
  --session router-check close
```

The browser test covers 390px and 1440px viewports, JavaScript enabled/disabled,
the fallback link, Back-button behavior, keyboard access, and overflow. It
substitutes a local destination to keep automated browser activity within the
approved preview. The HTTP checker verifies the actual external destination.
This existing coverage is sufficient for a destination-only change.

After each subsequent edit, rerun the render command and affected checks. Stop
the preview server with Ctrl+C in its terminal when finished.

## 4. Commit, push, and open a PR

These commands work the same in a feature branch in the original checkout or
in a managed worktree:

```sh
git diff --check
git add index.html
git commit -m "Update personal website redirect destination"
git push -u origin HEAD
gh pr create --repo JoeyWilkes12/personal-website-router --base main \
  --title "Update personal website redirect destination" \
  --body "Updates the redirect destination. Local redirect and hyperlink checks passed."
```

If you also changed documentation or scripts, review and stage those specific
files alongside `index.html`. A PR description should describe the actual final
change and checks you ran. Opening and pushing a feature branch does **not**
publish the router because Pages publishes `main`.

Codex must give you the specific PR link, summary, and validation results and
wait for your affirmative approval before merging that PR. A request to publish
does not approve a PR merge.

If signing fails, fix your signing setup or deliberately make a single unsigned
commit with `git -c commit.gpgsign=false commit -m "..."`. That override affects
only the one command; do not disable signing globally as a workaround.

## 5. Publish after approval

After you approve the specific PR, merge it on GitHub. The corresponding CLI
command is below; replace `123` with the real approved PR number:

```sh
gh pr merge 123 --repo JoeyWilkes12/personal-website-router --squash
```

Do not use this command before approval, and do not enable auto-merge to skip
that approval. Merging updates `main`, which starts GitHub Pages publication.

For an intentional **manual update you perform directly on `main`**, after
editing and completing the same checks, the commit/publish commands are:

```sh
git diff --check
git add index.html
git commit -m "Update personal website redirect destination"
git push origin main
```

Use that route only when already working on a clean, up-to-date `main` checkout
and intentionally choosing direct publication. It is not a way for Codex to
bypass the worktree or PR approval rules.

There is no separate website-upload command. The configured Pages source is
`main`, root folder `/`, with HTTPS enabled. Keep `.nojekyll` absent so URL
substitutions run. See [GitHub Pages publishing sources](https://docs.github.com/en/pages/getting-started-with-github-pages/configuring-a-publishing-source-for-your-github-pages-site).

## 6. Confirm publication

Find the deployment for the new commit:

```sh
gh run list --repo JoeyWilkes12/personal-website-router --branch main \
  --limit 5 --json databaseId,name,headSha,status,conclusion,url
```

Choose the `pages build and deployment` run whose `headSha` matches the new
`main` commit. Replace `RUN_ID` below with its numeric `databaseId`:

```sh
gh run watch RUN_ID --repo JoeyWilkes12/personal-website-router --exit-status
gh api repos/JoeyWilkes12/personal-website-router/pages \
  --jq '{status,html_url,source,https_enforced}'
```

Once the run succeeds, fetch the new `main` and run the public checks against
the matching source. In the original local checkout with a clean working tree:

```sh
git switch main
git pull --ff-only origin main
python3 scripts/check_links.py
```

If still in a managed feature worktree, synchronize the original checkout
separately; keep the worktree on its own branch. After a squash merge the new
commit has a different SHA, so compare the deployed `index.html` with `main`,
not the feature-branch SHA. A successful HTTP fetch of the router is HTTP 200;
the automatic redirect happens in the browser rather than as an HTTP 301/302.

## 7. Restore an earlier destination

The easiest rollback is another destination change: put the old URL back in
`redirect_url`, run the checks, then follow the same commit/PR/publish process.
This preserves the guide and unrelated later changes.

To restore the previously published Imperial portfolio destination:

```yaml
redirect_url: "https://joeywilkes12.github.io/imperial-portfolio/"
```

You can also restore only the router file from its known-good commit. Start
from a clean checkout or a clean managed worktree based on current `main`:

```sh
git log --oneline -- index.html
git show d6e4377:index.html
git restore --source=d6e4377 -- index.html
git diff -- index.html
```

Then run the local checks, stage `index.html`, make a new commit, push, and open
a PR as above. The `d6e4377` example restores the Imperial destination and that
commit's entire `index.html`; manually changing the one value is better if you
want to retain subsequent HTML improvements.

For a **whole-commit revert**, first inspect the exact commit's full scope:

```sh
git show --stat COMMIT_SHA
git revert --no-commit COMMIT_SHA
git diff --cached
```

Replace `COMMIT_SHA` with the specific non-merge commit being undone. This
stages inverse changes; it can undo documentation and scripts too. Reverting
a merge commit requires a deliberate mainline choice and is outside this
simple recipe. Resolve any conflicts and rerun checks before committing:

```sh
git commit -m "Revert the selected router change"
git push -u origin HEAD
```

Open a PR and obtain approval before merging it. If a revert conflicts and you
want to cancel, use `git revert --abort`. Published rollbacks should be new
commits; avoid rewriting shared `main` history or force-pushing. See
[Git's revert documentation](https://git-scm.com/docs/git-revert).

## Command references

- [GitHub CLI: create a PR](https://cli.github.com/manual/gh_pr_create)
- [GitHub CLI: merge a PR](https://cli.github.com/manual/gh_pr_merge)
- [GitHub CLI: list workflow runs](https://cli.github.com/manual/gh_run_list)
