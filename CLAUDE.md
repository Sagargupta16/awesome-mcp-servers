# CLAUDE.md

> This file stacks on top of the workspace root at `C:\Code\GitHub\`:
> - Root [`CLAUDE.md`](../../CLAUDE.md) -- voice, rules, routing map, references, skills, slash commands, conventions.
> - Root [`MEMORY.md`](../../MEMORY.md) -- live facts across repos.
> - Root [`STATUS.md`](../../STATUS.md) -- live PR/CI/security dashboard.
> - [`.claude/resources/`](../../.claude/resources/README.md) -- deep reference for collaboration, workflow, git, OSS, debugging, voice.
>
> Read those first. The guidance below only adds **repo-specific context** -- it does not override anything in the root.

## Project

Curated awesome-list of MCP servers, frameworks, clients, and resources, maintained by Sagar and open to community PRs. Content-only repo: everything lives in `README.md`, rendered directly on GitHub.

## Stack

- **Language**: Markdown only (no code)
- **Framework**: none
- **Database**: none
- **Package manager**: none
- **Deploy target**: GitHub README (no build, no deploy)

## Run

Nothing to run. Edit `README.md` directly.

## Test

No test suite. CI is a lychee link check ([.github/workflows/lint.yml](.github/workflows/lint.yml)) on PRs to `main` and weekly on Sundays. Mirror it locally with `lychee README.md` if installed.

## Entry points

- `README.md` -- the entire list: Official, Servers (21 categories), Frameworks, Clients, Tutorials, Videos, Community
- `CONTRIBUTING.md` -- entry format, category list, quality standards, PR process

## Key files

- `README.md` -- single source of truth for all entries
- `CONTRIBUTING.md` -- the format contract every entry must follow
- `.github/ISSUE_TEMPLATE/add-server.yml` -- structured server-submission form

## Gotchas

- The link-check workflow runs with `fail: false` -- broken links do NOT fail CI. Read the lychee output in the Actions log; a green check proves nothing about links.
- `.nvmrc`, `.python-version`, `.dockerignore` are leftovers from a bulk maintenance round (`.maintenance` file). No code uses them.
- `renovate.json` extends `Sagargupta16/shared-workflows` but there are no dependencies here; Renovate PRs are unlikely.
- Server entries must be strict `| [Name](URL) | Description | Language |` rows: description under 80 chars, capitalized, no trailing period, alphabetical within each category table.

## Repo-specific rules

- Follow `CONTRIBUTING.md` exactly when adding entries: one server per PR, most-appropriate existing category, alphabetical order.
- Only add servers meeting the quality bar: open source, documented README, actively maintained, working MCP implementation, not a duplicate.
- Don't remove entries without a stated reason (broken link, abandoned, no longer MCP). Community depends on the list.
- New categories need an issue discussion first, not a direct PR.
