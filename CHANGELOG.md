# Changelog

Version headings below are documentation milestones. No git tag or GitHub release has been cut for any of them yet.

## [2.8.0] - 2026-10-18

Since the post-merge thank-you went live on 2026-10-14 it had thanked 11 outside contributors 16 times, and none had starred. This asks when the pull request opens, the way Piebald-AI/awesome-gemini-cli-extensions does, and lets a star skip the maintainer review.

### Added

- `star-check.yml` and `scripts/star_check.py`. A pull request from someone who has not starred gets the `missing-star` label and one comment asking. When they star, the label comes off and the comment becomes a thank-you. Bots and the maintainer are never asked.

### Changed

- A starred author skips `needs-review`: `auto-merge.yml` and `issue-to-pr.yml` switch on auto-merge where they would have held the pull request for a maintainer, and starring later releases a held one, under the same file allowlist and stop labels as before. A star never gets an entry past a failing check, and an unstarred entry that passes still merges itself.
- CONTRIBUTING's hosted-server rule 4, the README, the site, the issue form, the submission check's note and the post-merge thank-you say what a star does now, instead of that it does nothing.

## [2.7.0] - 2026-10-14

Hosted MCP servers with no public source get a written bar. Six submissions had hit the gap and gone four different ways.

### Added

- A "Hosted servers" section in CONTRIBUTING.md for `Remote` entries: the link is the operator's own documentation, not a registry listing; that documentation names the endpoint, the authentication and what the tools do; the endpoint answers; and a maintainer reviews every one before it merges. The licence and 180-day rules do not apply to them, since there is no source.
- `check_submission.py` judges `Remote` rows on those terms. It reads the documentation page, or the README and `server.json` of the operator's repository, finds the endpoint and sends it an MCP `initialize`. A 401 from a server that wants a token counts as live; a 404, no answer, or a web page served at an `/mcp` path does not. Each request has one overall deadline, so a host with unreachable IPv6 addresses cannot hold the check for minutes.
- `--review` and `--head-ref` for `check_submission.py`. `auto-merge.yml` and `issue-to-pr.yml` use them to hold any pull request the gate leaves to a maintainer: every `Remote` entry, and any entry with a finding the gate cannot settle itself, such as a licence GitHub cannot classify or a link that is not a GitHub repository. Those get the new `needs-review` label instead of auto-merge. The check itself still passes.
- A hosted section in the monthly health report, which probes every `Remote` entry's endpoint with the gate's own code.
- Worklittle Jobs (#74), CareClinic (#97) and CosVoice (#123), re-judged under the new rule. All three name their endpoint, authentication and tools in their own documentation, and all three endpoints answered.

### Changed

- `Remote` entries with a repository no longer appear as unlicensed or stale in the health report.
- Scout Packs is listed as `Python`: its repository holds the server source under an MIT licence, so it was never a closed-source entry.
- TWZRD Agent Intel links the operator's repository instead of a Smithery listing. Dynatrace MCP, Honeycomb MCP and LogNorm link the page of their own documentation that names the endpoint.
- Statsnet (#98), Clera (#110) and Noveum (#111) meet the rule as written, so Statsnet no longer depends on a `maintainer-override`.
- A dropped connection to the GitHub API is reported as a network error instead of crashing the gate.

### Fixed

- 2.6.1 said the hosted rule covers Axe MCP. It does not: Axe is a closed-source container you run yourself, not a hosted server. It stays listed while that case is decided.

## [2.6.1] - 2026-10-14

Acting on the monthly health report, re-measured against the API on 2026-10-14 rather than the 2026-10-01 snapshot.

### Changed

- LangChain MCP Adapters was archived; it moved into LangChain itself, so the entry now points at `langchain.mcp`.
- Dynatrace MCP was archived and deprecated; the entry now points at Dynatrace's official hosted remote server.
- Square MCP's repository went past 180 days; the entry now points at Square's official hosted server, the one its README recommends.

### Removed

- 11 entries over the 180-day maintenance bar with no successor: a11y MCP, DeepWiki MCP, Bifrost MCP, MetaTrader MCP, Outlook MCP, Coda MCP, Bolt, Shopify MCP, Minecraft MCP Server, kubectl MCP and MCP Security Hub. Each comes back as soon as it is pushed to again.
- MCPDoc, archived with no successor.

### Kept

- All 26 entries the report listed without a recognised licence. Every one has a licence file GitHub cannot classify (`NOASSERTION`), which CONTRIBUTING.md accepts after a read by hand: the official `modelcontextprotocol` repositories, plus MIT, AGPL and Apache texts with custom headers. Axe MCP's file is a proprietary licence, which the hosted and closed-source rule now covers.

## [2.6.0] - 2026-10-14

Of 43 people whose entries merged since 2026-09-01, one had starred the repository. This asks after the merge rather than making a star a condition of it.

### Added

- `thanks.yml` and `scripts/thank_contributors.py`. Once a contributor's entry merges, one comment on their pull request links to the entry on the website, offers a "Listed in Awesome MCP Servers" badge for their README, and asks for a star while saying plainly that it is optional. Form submissions get the same text when their issue closes. Edits to an existing entry, bot pull requests and the maintainer's own get nothing.
- `site/badge.svg`, served at `https://sagargupta.online/awesome-mcp-servers/badge.svg` and linked to the repository.
- An "Already listed? Show it." block on the website with the badge and its snippet.

### Changed

- The website header's GitHub link is now a Star button, and it stays visible on phones. Below 640px it used to be hidden entirely, so mobile readers had no way to the repository.

## [2.5.1] - 2026-09-26

### Added

- A link to the website at the top of the README.

## [2.5.0] - 2026-09-26

### Added

- `issue-to-pr.yml` and `scripts/issue_to_pr.py`. A "Suggest a server" form for a server or a framework now becomes the same one-row pull request a contributor would open: the row is built with the validator's rules (description length, capitalisation, known language and category, no duplicate link), inserted into its table in order, and merged by auto-merge once the required checks pass. A form that breaks a rule gets a comment saying which, and editing the issue retries. Clients, links and guides are still added by a maintainer.
- `submission-check.yml` can be dispatched. A pull request opened with `GITHUB_TOKEN` starts no `pull_request` run, so the issue workflow dispatches `lint.yml` and `submission-check.yml` on the submission branch; their check runs land on the pull request's head commit and satisfy the required checks by name.
- Tests for the form parser, the row rules and the insert in `tests/test_issue_to_pr.py`.

### Changed

- The form and CONTRIBUTING.md say what now happens to a submission instead of "a maintainer can add the row".
- `issue-to-pr.yml` closes a form issue once its pull request has merged, from an hourly run. "Closes #N" never fires here: GitHub skips closing keywords for a merge made by auto-merge on `GITHUB_TOKEN`, which left #119 open after its entry merged in #120 (the first live end-to-end submission, merged with no maintainer involved).
- `issue-to-pr.yml` runs on `opened` and `edited` only. A form issue arrives with its label, so `labeled` fired alongside `opened` and the first live test (#117) got the same comment twice.

## [2.4.0] - 2026-09-26

### Added

- A website for the list, on GitHub Pages. `scripts/build_site.py` reads `README.md` with the validator's own parser, so the README stays the single source of truth, adds live stars and last-push dates from the GitHub API, and renders one static page into `_site/`: search across every entry, tabs for servers, frameworks, clients, official, learning and community, a chip per server category, a language filter, and sorting by stars, recent updates or name. Filters live in the URL, so a search can be shared. Cards are rendered in HTML, so the page works without JavaScript; `site/app.js` only filters and sorts them.
- `servers.json` next to the page: every entry with its tab, category, language or support tier, stars and last push, for anyone who wants the data.
- `pages.yml` builds and deploys the site on every change to `README.md` or the site sources, and every hour. The hourly run is what publishes an auto-merged entry, since a merge made with `GITHUB_TOKEN` starts no workflow run.
- Tests for the site builder in `tests/test_build_site.py`.

## [2.3.0] - 2026-09-17

### Added

- `auto-merge.yml`. A pull request that only touches `README.md` or `CHANGELOG.md` gets GitHub's native auto-merge switched on, so a community entry squash-merges itself the moment every required check passes. No approval, no waiting on a maintainer.
- A `no-auto-merge` label to stop it on a specific pull request.
- Required status checks on `main`, with no required reviews. The checks are now the only gate, which is what makes unattended merging safe.

### Changed

- `submission-check.yml` no longer filters on `paths`. A path-filtered required check never reports on a pull request that misses the filter, and auto-merge would then wait on it forever. The job exits in a few seconds when `README.md` is untouched.
- Auto-merge deliberately excludes any pull request reaching `.github/`, `scripts/`, `tests/` or tooling config. On a `pull_request` event the workflow definition comes from the pull request itself, so a fork can edit the checks that judge it, and merging that unattended would hand over the repository. Those changes stay with a human, as do pull requests carrying `maintainer-override`.

## [2.2.0] - 2026-09-06

The header promised three things the list did not deliver. Measured against the GitHub API on 2026-09-06 and corrected. This release only removes and repairs. It adds no entry, because CONTRIBUTING.md asks for one server per pull request and the gate enforces it.

### Removed

- **42 entries.** 37 had not been pushed in over 180 days, which `scripts/check_submission.py` hard-fails a new contributor for: worst were OpenAI MCP at 646 days, Twitch MCP at 593 and Discord MCP at 592. Kubernetes MCP (`strowk/mcp-k8s-go`, 257 days) was also a duplicate of the Kubernetes MCP Server already listed. The other five state no licence anywhere, neither a `LICENSE` file nor a package manifest: Loki MCP, Spotify MCP, and three whose repository holds no server either -- Weaviate MCP, whose root is one README saying the standalone server is deprecated in favour of the one built into the Weaviate binary, plus Figma Dev Guide and Readwise Skills, which hold a manifest pointing at a hosted endpoint and a `skills/` directory.
- `.maintenance`, `.dockerignore` and `.nvmrc`: leftovers from an old bulk-maintenance round, in a repository with no Dockerfile and no JavaScript.

Six products lost their only entry: Bitbucket, Discord, Linear, Todoist, Weaviate and Wikipedia. A replacement for any of them is a submission like any other -- one per pull request, through the same gate.

### Changed

- **Five Language cells corrected** against each repository's own `languages` breakdown rather than GitHub's primary-language guess: Slack MCP is Go (was TypeScript), Tavily MCP is JavaScript (was Python), STS2MCP is C# (was Python), prompt-to-asset is TypeScript (was JavaScript), and Unreal MCP is `Multiple` at a 54/46 TypeScript-to-C++ split (was C++).
- The licence rule now accepts a licence declared in a package manifest (`package.json`, `pyproject.toml`, `Cargo.toml`, `pom.xml`, `composer.json`, `deno.json`), not only a root `LICENSE` file. GitHub's licence API reads the root file only, so projects such as `vercel/mcp-handler` (Apache-2.0) and `modelcontextprotocol/inspector` (MIT) reported as unlicensed while shipping a real licence. The manifest is parsed rather than pattern-matched: a text search reads a nested `"license"` key as the package's own, and misses PEP 621's `license = {text = "..."}` table and composer's array form. A field that withholds open-source terms instead of granting them -- npm's `UNLICENSED`, `SEE LICENSE IN <file>`, `Proprietary` -- is still a hard failure.
- `staleness_report.py` reads the same manifests through the same two helpers, so an entry the gate accepts no longer lands in the monthly report as work for the maintainer to redo by hand. Its entry regex also required a bare `owner/repo` link, which left 11 of the repositories behind the list unchecked while the header claimed to have checked "all" of them. It now reports repositories that resolve only through a rename or transfer redirect, and skips this repository's own badge and issue links.
- The server-suggestion issue template no longer refers to a "notability bar" that 2.1.0 removed, and its licence checkbox matches the rule instead of asking authors to confirm something GitHub cannot see.
- `renovate.json` switches the pip manager off. `requirements-dev.txt` is a `--generate-hashes` lock installed with `--require-hashes`, and a bump that rewrites the pinned version without regenerating the hash block fails that install. Bump `requirements-dev.in` and recompile with the command in its header.

### Added

- A **"Using a server from this list"** section: the `mcpServers` config shape for a stdio server run straight from its published package, and for a remote one, where `type` is required and an entry with a `url` and no `type` is read as stdio and skipped.
- A **`python-checks` CI job** running `ruff check`, `ruff format --check` and `pytest` over `scripts/` and `tests/`. The submission gate was 1,075 lines of Python with no checks of its own.
- **`tests/`** -- 68 tests over all three scripts, including the reordering invariant that `added_rows()` depends on, the licence values the gate has to refuse, and a guard that CONTRIBUTING.md's category table matches `SERVER_CATEGORIES` exactly.
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
