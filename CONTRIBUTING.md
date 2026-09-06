# Contributing to Awesome MCP Servers

Thanks for wanting to add to this list. It aims to be a **curated** collection of Model Context Protocol (MCP) servers, tools, and resources -- not an exhaustive one. There are much larger MCP lists; the point of this one is that everything on it works, is maintained, and is safe to install.

That means submissions get checked, and some get declined. Everything below is enforced by CI, so you can see exactly where you stand before a maintainer looks.

## Table of Contents

- [Quick start](#quick-start)
- [Format](#format)
- [Categories](#categories)
- [Quality standards](#quality-standards)
- [What is not accepted](#what-is-not-accepted)
- [Submitting your own project](#submitting-your-own-project)
- [Pull request process](#pull-request-process)
- [Running the checks locally](#running-the-checks-locally)
- [Updating or removing an entry](#updating-or-removing-an-entry)
- [Reporting issues](#reporting-issues)

## Quick start

1. Read [quality standards](#quality-standards) and [what is not accepted](#what-is-not-accepted). Most declined pull requests fail one of those.
2. Fork the repo and branch off `main`.
3. Add **one** row to the most appropriate existing category in `README.md`, in alphabetical order.
4. Run `python scripts/validate.py` and fix anything it reports.
5. Open a pull request and fill in the template, including the affiliation question.

## Format

Server entries are table rows in this exact shape:

```
| [Name](URL) | Description | Language |
```

- **Name** -- the project name, as a user would recognise it. Keep it short.
- **URL** -- a direct `https://` link to the repository or official project page. No tracking parameters, no redirect shorteners.
- **Description** -- what it does, in **80 characters or fewer**. Start with a capital letter. No trailing period. No em-dash or en-dash; write `--` or `-` instead. Describe the function, not the pitch: "Query and optimise PostgreSQL databases" rather than "The ultimate AI-powered database companion".
- **Language** -- the primary implementation language, one of: `TypeScript`, `JavaScript`, `Python`, `Go`, `Rust`, `Java`, `Kotlin`, `C#`, `C++`, `C`, `Ruby`, `PHP`, `Swift`, `Elixir`, `Scala`, `Dart`, `Lua`, `Shell`, `Zig`, `Multiple` for a polyglot monorepo, `Remote` for a hosted endpoint with no public source, or `Built-in` for a server shipped inside another product.

Example:

```markdown
| [Acme MCP](https://github.com/acme/mcp-server) | Acme widget and gadget API integration | TypeScript |
```

The `Clients` table uses `| Client | Description | MCP Support |`, where the third column is one of `Full`, `Tools only`, `Tools + resources`, `Partial`, or `Experimental`.

The `Official`, `Tutorials & Articles`, `Videos`, and `Community` sections are bullet lists instead:

```markdown
- [Name](URL) - Description ending in a period.
```

## Categories

Add your server to the most appropriate **existing** category:

| Category | Scope |
| --- | --- |
| Data & Databases | Database connectors, warehouses, vector stores, data pipelines |
| Developer Tools | Version control, CI, code intelligence, API tooling, MCP meta-tooling |
| Cloud & Infrastructure | Cloud providers, PaaS, orchestration, infrastructure as code |
| Productivity | Docs, notes, tasks, calendars, workspace suites |
| Search & Knowledge | Search APIs, documentation retrieval, knowledge bases |
| Communication | Chat, email, SMS, voice, video meetings |
| File Systems & Storage | Local files, object storage, document extraction |
| AI & ML | Model providers, inference platforms, agent memory, ML tooling |
| Finance | Payments, accounting, market data, trading, banking |
| Monitoring & Observability | Metrics, logs, traces, alerting, incident response |
| Design & Creative | Design tools, image, video, audio, 3D |
| Testing & QA | Test automation, accessibility, protocol conformance |
| Security | Secrets, vulnerability scanning, appsec, offensive tooling |
| Web Browsing & Scraping | Browser automation, crawlers, scrapers |
| Media & Entertainment | Music, video, streaming, media libraries |
| Travel & Location | Maps, transit, weather, booking, geospatial |
| E-commerce | Storefronts, marketplaces, catalogues, fulfilment |
| Game Development | Game engines and game platform tooling |
| IoT & Home Automation | Smart home, device protocols, embedded |
| Marketing & Analytics | CRM, ads, SEO, product and web analytics |
| Knowledge Management | Personal knowledge management, note graphs, reference managers |

Beyond the server categories, the list also has **Official**, **Frameworks & Libraries**, **Clients**, **Tutorials & Articles**, **Videos**, and **Community**.

**New categories need an issue first.** Open one describing what does not fit and roughly how many existing entries would move. Do not add a category in a pull request -- CI rejects unknown headings, because the category list lives in `scripts/validate.py`.

### Alphabetical order

Entries are sorted alphabetically by name within each table, case-insensitively and ignoring leading punctuation. `python scripts/validate.py --fix` sorts them for you.

## Quality standards

Every submission must meet all of these. CI checks the mechanical ones automatically and reports the rest for a maintainer.

1. **It really is an MCP server.** The repository contains a working [MCP](https://modelcontextprotocol.io/) implementation -- server, client, or framework, matching the section. A repository holding only a README and a registry manifest such as `server.json` is rejected.
2. **Open source with a detectable licence.** GitHub must identify a licence for the repository. If the licence sidebar is empty or reads "unknown", add a standard `LICENSE` file first.
3. **Documented.** A README covering what it does, how to install and configure it, and basic usage.
4. **Maintained.** Pushed within the last **180 days**, and not archived.
5. **Notable.** Either 150 or more stars, or the vendor's own official server for a product people already use. A brand-new personal project with a handful of stars is not declined for being new -- it is declined for being unverifiable. Come back when it has traction.
6. **Not a duplicate.** Not already listed, and not a second server for a product already covered. If yours is genuinely better than the listed one, say why in the pull request and propose replacing it.
7. **Not a fork.** Submit the upstream project.

Entries that stop meeting these get removed. A monthly [health workflow](.github/workflows/health.yml) posts dead links, archived projects, missing licences, and stale entries into a tracking issue.

## What is not accepted

Being explicit saves everyone time:

- **Manifest-only repositories.** A README plus `server.json` / `glama.json` with no implementation.
- **Undisclosed self-promotion.** Submitting your own project is welcome; hiding it is not. See below.
- **Batch submissions.** Several servers from one author or organisation in one pull request. One per pull request, and if you have eight, expect scrutiny on all eight.
- **Umbrella "agent OS" projects** that are not primarily an MCP server, however many buzzwords the README carries.
- **Paid or closed products with no MCP implementation to inspect**, other than genuinely well-known hosted servers that document their MCP endpoint publicly.
- **SEO and backlink submissions.** If the goal is a link rather than a useful entry, it will be declined and the pull request closed.
- **Entries whose description is marketing copy.** Rewrite it as a factual capability statement.
- **Removing or reordering unrelated entries** alongside your addition.

## Submitting your own project

That is fine and normal -- much of this list exists because authors submitted their own work. Two requirements:

1. **Disclose it.** Tick the affiliation box in the pull request template. Undisclosed self-promotion that is discovered gets the entry removed.
2. **Meet the same bar as everyone else.** No exceptions on licence, documentation, or maintenance.

If your project is too new to clear the notability bar, open a [server suggestion issue](https://github.com/Sagargupta16/awesome-mcp-servers/issues/new/choose) instead. It stays on record, and you can point at it later once the project has grown.

## Pull request process

1. **One server per pull request.** This keeps review and revert independent. CI fails a pull request that adds more than one entry.
2. Branch off `main`, add your row, and commit with a clear message such as `Add Acme MCP to Developer Tools`.
3. Fill in the pull request template, including the affiliation question.
4. Make sure all checks pass:
   - **Validate format** -- structure, ordering, duplicates, description length
   - **Check links** -- every URL resolves
   - **Submission check** -- licence, maintenance, archived state, real implementation
5. A maintainer reviews. Expect questions if your project is new or the description reads promotionally.

Maintainers can apply the `maintainer-override` label when a submission is genuinely fine but trips a threshold, for example a vendor-official server with few stars.

## Running the checks locally

```bash
python scripts/validate.py
```

```bash
python scripts/validate.py --fix
```

`--fix` repairs alphabetical order, trailing whitespace, and dashes. Everything else -- an over-long description, a duplicate, an unknown category -- needs a real edit.

To preview the submission gate the way CI runs it:

```bash
GITHUB_TOKEN=$(gh auth token) python scripts/check_submission.py --base-ref origin/main
```

The link check needs [lychee](https://github.com/lycheeverse/lychee):

```bash
lychee --config lychee.toml README.md CONTRIBUTING.md
```

## Updating or removing an entry

**Updating** -- open a pull request and explain what changed. Renames, moved repositories, and corrected descriptions are all welcome, and correcting someone else's entry is a genuinely useful contribution.

**Removing** -- if a listed server is dead, archived, no longer implements MCP, or has become malicious, open an issue or a pull request that says which and why. Removals need a stated reason: people rely on this list, so entries are not dropped silently.

## Reporting issues

Use the [issue templates](https://github.com/Sagargupta16/awesome-mcp-servers/issues/new/choose) to suggest a server, report a broken link, propose a category, or raise anything else.

Found something on this list that behaves maliciously? That is a security matter -- see [SECURITY.md](SECURITY.md) and report it privately rather than in a public issue.

## Code of Conduct

This project follows the [Contributor Covenant Code of Conduct](CODE_OF_CONDUCT.md). By participating you agree to uphold it.

---

Thanks for helping keep this list worth reading.
