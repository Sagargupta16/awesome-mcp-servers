# Changelog

Version headings below are documentation milestones. No git tag or GitHub release has been cut for any of them yet.

## [2.2.0] - 2026-09-06

The header promised three things the list did not deliver. Measured against the GitHub API on 2026-09-06 and corrected.

### Removed

- **36 entries.** 32 had not been pushed in over 180 days, which `scripts/check_submission.py` hard-fails a new contributor for: worst was OpenAI MCP at 647 days, with Twitch MCP at 593 and Puppeteer MCP at 541. The other four had no licence anywhere, in a `LICENSE` file or a package manifest: Loki MCP, Spotify MCP, and two that held no MCP implementation either. Kubernetes MCP (`strowk/mcp-k8s-go`, 257 days) went as a duplicate of the maintained Kubernetes MCP Server already listed.
- Figma Dev Guide and Readwise Skills, whose repository roots hold a README, a `server.json` and a `skills/` directory with no server in them -- the exact shape CONTRIBUTING.md rejects.
- `.maintenance`, `.dockerignore` and `.nvmrc`: leftovers from an old bulk-maintenance round, in a repository with no Dockerfile and no JavaScript.

### Changed

- **Six rotted entries replaced by the maintained or vendor-official server for the same product**: Todoist (`Doist/todoist-mcp`), Discord (`SaseQ/discord-mcp`), Wikipedia (`Rudra-ravi/wikipedia-mcp`), Linear (its hosted server), Bitbucket (the official Atlassian Rovo server, which covers Jira, Confluence, JSM, Bitbucket and Compass), and Weaviate, whose standalone server is deprecated in favour of the one built into the Weaviate binary.
- **12 URLs rewritten to their current slug.** Each resolved only through a GitHub rename or transfer redirect, which holds just until someone claims the old name: mcp-scan is now `snyk/agent-scan`, XcodeBuildMCP is under `getsentry`, Strands Agents SDK is `harness-sdk`, plus Chatbox, Goose, opencode, OpenHands, Probe, octocode, mcp-remote, TomTom MCP and NotFair. Names and descriptions were re-checked for the ones that were renamed rather than just moved.
- **Six Language cells corrected** against each repository's own language breakdown rather than GitHub's primary-language guess: Slack MCP is Go (was TypeScript), Tavily MCP is JavaScript (was Python), STS2MCP is C# (was Python), prompt-to-asset is TypeScript (was JavaScript), Unreal MCP is `Multiple`. TypeScript-versus-JavaScript disagreements caused by a committed `dist/` were left alone.
- The licence rule now accepts a licence declared in a package manifest (`package.json`, `pyproject.toml`, `Cargo.toml`, `pom.xml`, `composer.json`, `deno.json`), not only a root `LICENSE` file. GitHub's licence API reads the root file only, so projects such as `vercel/mcp-handler` and `modelcontextprotocol/inspector` reported as unlicensed while shipping a real licence. `check_submission.py` reads the manifest before blocking, and flags the case for a maintainer.
- `staleness_report.py` now reaches every listed repository. Its entry regex required a bare `owner/repo` link, so 13 entries pointing into a subdirectory were silently skipped, and the report header claimed to have checked "all" of them. It also reports repositories that only resolve through a redirect, and skips this repository's own badge and issue links.
- The server-suggestion issue template no longer refers to a "notability bar" that 2.1.0 removed, and its licence checkbox matches the rule instead of asking authors to confirm something GitHub cannot see.

### Added

- A **"Using a server from this list"** section: the `mcpServers` config shape for a local (`npx` / `uvx`) server and for a remote one. The file listed 389 entries and gave no example of wiring even one into a client.
- A **`python-checks` CI job** running `ruff check`, `ruff format --check` and `pytest` over `scripts/` and `tests/`. The submission gate was 1,075 lines of Python with no checks of its own.
- **`tests/`** -- 46 tests over all three scripts, including the reordering invariant that `added_rows()` depends on and a guard that CONTRIBUTING.md's category table matches `SERVER_CATEGORIES` exactly.
- `ruff.toml`, so a contributor's global ruff config cannot report rules CI never runs, and `requirements-dev.in` / `requirements-dev.txt`, a hash-locked pin of `ruff` and `pytest` installed with `--require-hashes` so nothing enters the job without a checksum and a formatter release cannot flip `ruff format --check` on an unrelated pull request.
- `SECURITY.md` and `CHANGELOG.md` to the link check, which only covered README and CONTRIBUTING.

### Fixed

- Six ruff findings in the gate scripts: five ambiguous `l` identifiers and an f-string with no placeholders.
- Every workflow now installs the interpreter named in `.python-version`. They pinned 3.12 while the file said 3.14, with nothing reconciling the two.

## [2.1.0] - 2026-09-06

### Changed

- **Removed the star and project-age bar.** Anyone can submit an MCP server, including a brand-new one with no traction. The checks now ask whether a thing is real -- working implementation, licence file, documentation, recent activity -- not whether it is popular. A 3-day-old server with 10 stars and clear setup instructions qualifies.
- `check_submission.py` no longer warns on low stars or a young repository. Both are still shown as context in the report, without a verdict attached.
- `CONTRIBUTING.md` leads with "anyone can contribute, including your own project", and the "what is not accepted" list is now only about spam and broken submissions. Declining a PR has to name a specific reason, and "too new" or "too few stars" is not available as one.
- Affiliation disclosure is framed as the one thing asked, rather than as a suspicion.

## [2.0.0] - 2026-09-06

Curation is now enforced by CI rather than promised in a document. The list goes
from 231 entries to 389: 181 added, 23 removed, every one of them checked against
the GitHub API rather than taken on trust.

### Added

- `scripts/validate.py` -- checks structure, table-of-contents anchors, row format, description length and casing, language values, duplicate URLs and names, alphabetical order, dashes and whitespace. `--fix` repairs the mechanical problems.
- `scripts/check_submission.py` -- looks up each entry a pull request adds and reports stars, licence, last push, archived state, repo age, and whether the repository holds an implementation or only a registry manifest.
- `scripts/staleness_report.py` and a monthly `health.yml` workflow that rewrites one tracking issue with everything that has rotted.
- `submission-check.yml` workflow gating new entries, with a `maintainer-override` label for judgement calls.
- `lychee.toml` so the link check can fail the build without being flaky.
- An issue template for reporting a dead, moved, or abandoned entry.
- 181 entries, each confirmed by a live API call: not archived, not a fork, licence detectable, pushed within 180 days, and either 150+ stars or the vendor's own official server. Among them the official Go, C#, Rust, PHP, Swift, Kotlin and Ruby SDKs, MCP Apps, MCP Bundles, the conformance suite, Langflow, OpenHands, OpenAI Agents SDK, Google ADK, Pydantic AI, mcp-go, mcp-use, Spring AI, Jenkins, HashiCorp Vault and Firebase.
- The Clients table grew from 8 rows to 23, and its `MCP Support` column now reports which protocol primitives each client actually implements, taken from that client's own documentation rather than assumed.

### Changed

- The link check now **fails** on a broken link. It previously ran with `fail: false`, so six 404s sat on `main` while CI stayed green.
- `CONTRIBUTING.md` documents all 21 categories (it listed 10), states what is not accepted, and requires affiliation disclosure.
- `SECURITY.md` covers the real risk for a list of MCP servers: a malicious entry is a supply-chain problem, since an MCP server runs with the user's files and credentials.
- The README header states the curation policy instead of implying it.

### Removed

- 23 entries: 6 dead links, 6 archived upstreams, 2 repositories containing only a README and registry manifests, 8 from a single-account batch submission, and duplicate rows for Playwright, Figma Context, Firecrawl, Vercel mcp-handler, Claude Mobile, MCP Registry and Graphiti.
- `.github/pull_request_template.md`. Both case variants were committed, so GitHub saw two templates.

### Fixed

- 81 alphabetical-order violations across all 21 tables.
- 7 over-length or uncapitalised descriptions, and a markdown link nested inside a description cell.
- The MCP GitHub Discussions link, which pointed at an org-level URL that 404s.

## [1.0.0] - 2026-03-16

- Add PR template for submitting new MCP servers

## [0.1.0] - 2026-03-04

- Initial awesome list with 50+ MCP servers across 10 categories
