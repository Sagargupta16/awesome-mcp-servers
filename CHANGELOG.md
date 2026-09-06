# Changelog

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
