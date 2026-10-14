# CLAUDE.md

> This file stacks on top of the workspace root at `C:\Code\GitHub\`:
> - Root [`CLAUDE.md`](../../CLAUDE.md) -- voice, rules, routing map, references, skills, slash commands, conventions.
> - Root [`MEMORY.md`](../../MEMORY.md) -- live facts across repos.
> - Root [`STATUS.md`](../../STATUS.md) -- live PR/CI/security dashboard.
> - [`.claude/resources/`](../../.claude/resources/README.md) -- deep reference for collaboration, workflow, git, OSS, debugging, voice.
>
> Read those first. The guidance below only adds **repo-specific context** -- it does not override anything in the root.

## Project

Curated awesome-list of MCP servers, frameworks, clients, and resources, maintained by Sagar and open to community PRs. `README.md` is the product; `scripts/` is the machinery that keeps its promises true.

## Stack

- **Language**: Markdown (the list) plus Python (the gate scripts in `scripts/`, stdlib only)
- **Framework**: none
- **Database**: none
- **Package manager**: none for the list; `requirements-dev.in` / `requirements-dev.txt` hash-lock `ruff` and `pytest` for the scripts
- **Deploy target**: the GitHub README, plus a static site on GitHub Pages built from it by `scripts/build_site.py` (`site/` holds the template, CSS and JS; output `_site/` is gitignored)

## Run

```bash
python scripts/validate.py          # structure, format, duplicates (ordering is a note)
python scripts/validate.py --fix    # auto-repair ordering, whitespace, dashes
GITHUB_TOKEN=$(gh auth token) python scripts/check_submission.py --base-ref origin/main
python scripts/check_new_links.py --base-ref origin/main   # only the links a change adds
GITHUB_TOKEN=$(gh auth token) python scripts/thank_contributors.py --dry-run   # who the thank-you bot would comment on
GITHUB_TOKEN=$(gh auth token) python scripts/staleness_report.py
GITHUB_TOKEN=$(gh auth token) python scripts/build_site.py      # site into _site/; without a token it builds with no stars
python -m http.server 8766 --directory _site                   # preview it
```

`.python-version` (3.14) is the interpreter every workflow installs via `python-version-file`.

## Test

```bash
pip install --require-hashes -r requirements-dev.txt
pytest tests/ -q
ruff check scripts/ tests/
ruff format --check scripts/ tests/
```

`requirements-dev.txt` is a uv-generated universal hash lock; `requirements-dev.in` is the source and carries the regeneration command. Both the pin and `ruff.toml`'s rule set exist so `ruff format --check` cannot flip on a formatter release.

Seven workflows:

- [lint.yml](.github/workflows/lint.yml) -- `validate` (README structure), `python-checks` (ruff + pytest on the gate scripts), `link-check` (lychee over README, CONTRIBUTING, SECURITY, CHANGELOG). Runs on PRs to `main`, pushes to `main`, and daily at 06:00 UTC.
- [submission-check.yml](.github/workflows/submission-check.yml) -- inspects the rows a PR adds against the GitHub API: licence, last push, archived, fork, real implementation. Honours the `maintainer-override` label. Deliberately has no `paths` filter: it is a required status check, and a path-filtered required check never reports on a PR that misses the filter, which hangs auto-merge forever.
- [auto-merge.yml](.github/workflows/auto-merge.yml) -- switches on GitHub's native auto-merge for PRs that only touch `README.md` or `CHANGELOG.md`, so a community entry lands unattended once the required checks pass. Runs on `pull_request_target` so a fork cannot edit the workflow that judges it, and never checks out PR code, so the writable token is never exposed to contributor-controlled input. Skipped when a PR reaches `.github/`, `scripts/`, `tests/` or tooling config, or carries `maintainer-override` or `no-auto-merge`. Also skipped, with the `needs-review` label added, when `check_submission.py --review` finds any entry it leaves to a maintainer (every `Remote` row, an unclassifiable licence, a non-GitHub link): the job checks out `main`, fetches the PR head as data, and judges the head's README against the merge base with main's copy of the script.
- [health.yml](.github/workflows/health.yml) -- monthly (1st, 06:00 UTC) audit of every listed repository, plus an endpoint probe of every `Remote` entry, rewritten into one `maintenance`-labelled tracking issue. First scheduled run: 2026-10-01.
- [pages.yml](.github/workflows/pages.yml) -- builds the website from `README.md` and deploys it to GitHub Pages, on push to `main` (README, `site/`, the builder or the validator) and hourly at :17. The hourly run is load-bearing for the same reason as lint's schedule: an auto-merged entry never produces a push run, so without it the site would not show community additions. Not a required check.
- [issue-to-pr.yml](.github/workflows/issue-to-pr.yml) -- turns a "Suggest a server" form (label `addition`) for a server or framework into a one-row pull request on `submission/issue-N`, via `scripts/issue_to_pr.py`, which reads the untrusted issue body from the event payload file and never lets it reach a shell. Because a `GITHUB_TOKEN` pull request starts no `pull_request` runs, it dispatches `lint.yml` and `submission-check.yml` on the branch (their check runs land on the PR head, so the required checks match by name) and enables auto-merge itself, or labels `needs-review` under the same `--review` rule auto-merge.yml applies. Needs the repository setting "Allow GitHub Actions to create and approve pull requests"; no reviews are required, so only "create" is used. An invalid form gets a comment and retries on edit. Its hourly sweep closes the issue with the thank-you text from `scripts/thank_contributors.py`.
- [thanks.yml](.github/workflows/thanks.yml) -- after a contributor's entry merges, comments once on their pull request with a link to the entry on the site, the "Listed in" badge for their README, and a star ask that says it is optional. Hourly plus `pull_request_target: closed`, because an auto-merged pull request fires no `closed` run; a hidden `<!-- awesome-mcp-servers:thanks -->` marker stops double posts, and `NOT_BEFORE` (2026-10-14) stops it reaching back over old merges. Skips bots (form issues are thanked on the issue), the maintainer, and edits to an existing entry. Not a required check.

## Entry points

- `README.md` -- the entire list: Official, Servers (21 categories), Frameworks, Clients, Tutorials, Videos, Community
- `CONTRIBUTING.md` -- entry format, category list, quality standards, PR process
- `scripts/validate.py` -- the format contract, in code. `SERVER_CATEGORIES` is the canonical category list.

## Key files

- `README.md` -- single source of truth for all entries
- `CONTRIBUTING.md` -- the format contract every entry must follow
- `scripts/validate.py` / `check_submission.py` / `check_new_links.py` / `staleness_report.py` -- the enforcement
- `scripts/thank_contributors.py` -- the post-merge thank-you; `BADGE_URL` and `BADGE_MARKDOWN` live in `scripts/build_site.py` and both import them
- `site/badge.svg` -- the "Listed in" badge, served from the Pages site. Never make a star a condition of anything: asking after the merge is the whole design
- `tests/` -- pytest suite covering all three scripts, plus a guard that CONTRIBUTING's category table matches `SERVER_CATEGORIES`
- `ruff.toml` -- pins the lint rule set so a local run and CI agree
- `.github/ISSUE_TEMPLATE/add-server.yml` -- structured server-submission form

## Gotchas

- The link check is split by event. On a pull request only `scripts/check_new_links.py` can fail it, judging the links that change introduces against the base ref; the full lychee sweep still runs but with `fail: false`. On a push, the schedule or a dispatch, lychee sweeps the whole file with `fail: true`. A full sweep on pull requests charged authors for rot on the base branch and blocked six innocent submissions across three rotted entries before this split. `lychee.toml` is the single source of accept codes and host exclusions -- `check_new_links.py` reads it rather than restating them, so the two cannot drift. It excludes five hosts that hard-block automation (x.com, twitter.com, linkedin.com, discord.gg, smithery.ai), and links to those are never verified.
- Auto-merge is the only merge path for content PRs and the checks are the only gate, so the required-check list on the `main` ruleset is load-bearing. Adding a `paths` filter to any required check, or renaming a job, silently breaks it: a required check that never reports leaves auto-merge waiting forever, and a renamed job means the old name never arrives. Change a job name and the ruleset in the same pass.
- Ruleset bypass is granted to `repository_admin` on purpose. Without it, required checks would lock Sagar out of an emergency fix on `main`.
- Fork PR workflow approval is set to `first_time_contributors_new_to_github` (2026-09-30, repo setting, not in version control). A contributor brand new to GitHub still parks `Lint` and `Submission check` at `action_required`, so auto-merge waits until someone approves the runs: `gh api -X POST repos/Sagargupta16/awesome-mcp-servers/actions/runs/<id>/approve`. GitHub offers no `never` value.
- An auto-merged pull request produces **no push-to-main workflow run**. GitHub does not start a run from a `GITHUB_TOKEN` push, and auto-merge lands the commit as `github-actions[bot]`. Since the PR-side `Validate format` is baseline-scoped and only judges what that PR introduced, the daily 06:00 UTC `lint.yml` schedule is the only thing holding `main` to the full bar. Do not thin that schedule out, and do not assume a green PR means `main` is green.
- Required checks are not strict (`strict_required_status_checks_policy: false`), so a branch need not be up to date to merge. Two individually-clean pull requests can therefore interleave their rows out of order. That is harmless now that ordering is only a note; `--fix` tidies it whenever someone runs it.
- The submission gate hard-fails at 181 days since last push and on a repo with no licence anywhere. Incumbent entries are held to the same bar; that is what the monthly health report is for.
- `Remote` rows skip the licence, 180-day and stub checks and are judged on CONTRIBUTING's "Hosted servers" rules instead. The gate finds the endpoint in the docs page or the repo README and `server.json`, POSTs an MCP `initialize`, and counts any non-404/410 status, or a 2xx in JSON or SSE, as live; a 2xx in HTML is a web page. Probes send only the MCP `Accept` header: with `text/html` in it, a server on its website's host served the website. Each request has one 20s deadline on a daemon thread, because urllib's timeout is per socket operation and per resolved address.
- This machine's IPv6 hangs instead of failing, so a local probe pays about 10s per dual-stack host and docs pages can hit the 20s deadline. GitHub runners do not. For a local audit, filter `socket.getaddrinfo` to `AF_INET` in the harness, not in the script.
- Every `Remote` entry waits for a maintainer by design. Merge a `needs-review` PR by hand after checking the docs (`gh pr merge N --squash`); removing the label does nothing, since the next auto-merge run re-adds it.
- A licence declared only in `package.json` / `pyproject.toml` is accepted (GitHub's licence API reads the root `LICENSE` file only, so those repos report as unlicensed). See `MANIFEST_LICENCE_FILES` in `check_submission.py`. The field having a value is not enough: `is_open_source()` rejects `UNLICENSED`, `SEE LICENSE IN <file>` and `Proprietary`, which fill the field while withholding the terms. `staleness_report.py` imports both helpers so the report and the gate cannot disagree.
- GitHub serves renamed and transferred repos over a redirect, so a stale slug keeps working until someone claims the old name. `staleness_report.py` compares `nameWithOwner` to the listed slug to catch that.
- `renovate.json` extends `Sagargupta16/shared-workflows`, which is `config:recommended` plus `automerge: true` on a monthly grouped PR. That covers the pinned GitHub Actions and, by default, `requirements-dev.txt`. The pip manager is switched off in `renovate.json` because it rewrites the pinned version without regenerating the `--hash=` block, which then fails `pip install --require-hashes`. Bumping `ruff` or `pytest` means editing `requirements-dev.in` and running the compile command in its header.
- Server entries must be strict `| [Name](URL) | Description | Language |` rows: description under 80 chars, capitalized, no trailing period. Alphabetical order within a table is a note, not an error, so it never fails a pull request.
- No git tag or GitHub release exists for any version heading in `CHANGELOG.md`. Treat them as documentation milestones until someone cuts real tags.

## Repo-specific rules

- Follow `CONTRIBUTING.md` when adding entries: most-appropriate existing category, and alphabetical order where convenient. Neither one-server-per-PR nor ordering is enforced; both are preferences the checks only mention.
- Only add servers meeting the quality bar: open source, documented README, actively maintained, working MCP implementation, not a duplicate. A hosted server with closed source meets the "Hosted servers" rules in CONTRIBUTING.md instead; a closed-source server you run yourself (Axe MCP's container) has no written rule yet.
- Don't remove entries without a stated reason (broken link, abandoned, no longer MCP, over the 180-day bar, no licence). Community depends on the list.
- New categories need an issue discussion first, not a direct PR. Adding one means editing `SERVER_CATEGORIES` in `scripts/validate.py` and the table in `CONTRIBUTING.md` together -- a test fails if they disagree.
- Changing a rule in `CONTRIBUTING.md` means changing `scripts/check_submission.py` in the same commit. A documented bar the gate does not enforce, or a gate stricter than the docs, is the defect this repo keeps producing.
