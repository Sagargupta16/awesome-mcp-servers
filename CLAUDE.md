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
- **Package manager**: none for the list; `pip install -r requirements-dev.txt` pins `ruff` and `pytest` for the scripts
- **Deploy target**: GitHub README (no build, no deploy)

## Run

```bash
python scripts/validate.py          # structure, format, duplicates, ordering
python scripts/validate.py --fix    # auto-repair ordering, whitespace, dashes
GITHUB_TOKEN=$(gh auth token) python scripts/check_submission.py --base-ref origin/main
GITHUB_TOKEN=$(gh auth token) python scripts/staleness_report.py
```

`.python-version` (3.14) is the interpreter every workflow installs via `python-version-file`.

## Test

```bash
pip install -r requirements-dev.txt
pytest tests/ -q
ruff check scripts/ tests/
ruff format --check scripts/ tests/
```

`ruff` and `pytest` are pinned in `requirements-dev.txt` so `ruff format --check` cannot flip on a formatter release; `ruff.toml` pins the rule set for the same reason.

Three workflows:

- [lint.yml](.github/workflows/lint.yml) -- `validate` (README structure), `python-checks` (ruff + pytest on the gate scripts), `link-check` (lychee over README, CONTRIBUTING, SECURITY, CHANGELOG). Runs on PRs to `main`, pushes to `main`, and weekly on Sundays.
- [submission-check.yml](.github/workflows/submission-check.yml) -- inspects the rows a PR adds against the GitHub API: licence, last push, archived, fork, real implementation. Honours the `maintainer-override` label.
- [health.yml](.github/workflows/health.yml) -- monthly (1st, 06:00 UTC) audit of every listed repository, rewritten into one `maintenance`-labelled tracking issue. First scheduled run: 2026-10-01.

## Entry points

- `README.md` -- the entire list: Official, Servers (21 categories), Frameworks, Clients, Tutorials, Videos, Community
- `CONTRIBUTING.md` -- entry format, category list, quality standards, PR process
- `scripts/validate.py` -- the format contract, in code. `SERVER_CATEGORIES` is the canonical category list.

## Key files

- `README.md` -- single source of truth for all entries
- `CONTRIBUTING.md` -- the format contract every entry must follow
- `scripts/validate.py` / `check_submission.py` / `staleness_report.py` -- the enforcement
- `tests/` -- pytest suite covering all three scripts, plus a guard that CONTRIBUTING's category table matches `SERVER_CATEGORIES`
- `ruff.toml` -- pins the lint rule set so a local run and CI agree
- `.github/ISSUE_TEMPLATE/add-server.yml` -- structured server-submission form

## Gotchas

- The link check runs with `fail: true`, so a broken link fails CI. `lychee.toml` excludes five hosts that hard-block automation (x.com, twitter.com, linkedin.com, discord.gg, smithery.ai) -- links to those are never verified by CI.
- The submission gate hard-fails at 181 days since last push and on a repo with no licence anywhere. Incumbent entries are held to the same bar; that is what the monthly health report is for.
- A licence declared only in `package.json` / `pyproject.toml` is accepted (GitHub's licence API reads the root `LICENSE` file only, so those repos report as unlicensed). See `MANIFEST_LICENCE_FILES` in `check_submission.py`.
- GitHub serves renamed and transferred repos over a redirect, so a stale slug keeps working until someone claims the old name. `staleness_report.py` compares `nameWithOwner` to the listed slug to catch that.
- `renovate.json` extends `Sagargupta16/shared-workflows`; the only things it can bump are the pinned GitHub Actions.
- Server entries must be strict `| [Name](URL) | Description | Language |` rows: description under 80 chars, capitalized, no trailing period, alphabetical within each category table.
- `CHANGELOG.md` declares 2.1.0, 2.0.0, 1.0.0 and 0.1.0, but no git tag or GitHub release exists for any of them. Treat the version headings as documentation milestones until someone cuts real tags.

## Repo-specific rules

- Follow `CONTRIBUTING.md` exactly when adding entries: one server per PR, most-appropriate existing category, alphabetical order.
- Only add servers meeting the quality bar: open source, documented README, actively maintained, working MCP implementation, not a duplicate.
- Don't remove entries without a stated reason (broken link, abandoned, no longer MCP, over the 180-day bar, no licence). Community depends on the list.
- New categories need an issue discussion first, not a direct PR. Adding one means editing `SERVER_CATEGORIES` in `scripts/validate.py` and the table in `CONTRIBUTING.md` together -- a test fails if they disagree.
- Changing a rule in `CONTRIBUTING.md` means changing `scripts/check_submission.py` in the same commit. A documented bar the gate does not enforce, or a gate stricter than the docs, is the defect this repo keeps producing.
