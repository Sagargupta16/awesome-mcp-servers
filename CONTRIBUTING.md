# Contributing to Awesome MCP Servers

Thank you for your interest in contributing! This list aims to be a high-quality, curated collection of Model Context Protocol (MCP) servers, tools, and resources.

## Table of Contents

- [Adding an MCP Server](#adding-an-mcp-server)
- [Format](#format)
- [Categories](#categories)
- [Quality Standards](#quality-standards)
- [Pull Request Process](#pull-request-process)
- [Updating an Existing Entry](#updating-an-existing-entry)
- [Reporting Issues](#reporting-issues)

## Adding an MCP Server

Before submitting, please make sure your server meets the [quality standards](#quality-standards) below.

### Format

Entries in the server tables must follow this exact format:

```
| [Name](URL) | Description | Language |
```

- **Name**: The project name (e.g., `PostgreSQL MCP`). Keep it concise.
- **URL**: A direct link to the repository or project page.
- **Description**: A short, clear description of what the server does. Start with a capital letter and do not end with a period. Keep it under 80 characters.
- **Language**: The primary implementation language (e.g., `TypeScript`, `Python`, `Go`, `Rust`, `Java`). Use `Multiple` if the project spans several languages.

Example:

```markdown
| [Acme MCP](https://github.com/acme/mcp-server) | Acme API integration for widgets and gadgets | TypeScript |
```

### Categories

Add your server to the most appropriate existing category. The current server categories are:

- **Data & Databases** - Database connectors and data stores
- **Developer Tools** - Tools for software development workflows
- **Cloud & Infrastructure** - Cloud providers and infrastructure management
- **Productivity** - Productivity apps and workspace tools
- **Search & Knowledge** - Search engines and knowledge bases
- **Communication** - Messaging platforms and communication tools
- **File Systems & Storage** - File and object storage systems
- **AI & ML** - AI/ML platforms and model providers
- **Finance** - Financial services and payment platforms
- **Monitoring & Observability** - Monitoring, logging, and alerting tools

Other top-level sections include **Frameworks & Libraries**, **Clients**, **Tutorials & Articles**, **Videos**, and **Community**.

If you believe a new category is needed, open an issue first to discuss it.

### Alphabetical Order

Within each category table, entries should be added in alphabetical order by name.

## Quality Standards

Every submission must meet the following requirements:

1. **Working MCP server** - The project must implement the [Model Context Protocol](https://modelcontextprotocol.io/) and function as a working MCP server (or client/framework, depending on the section).
2. **Open source** - The project must be open source with a clearly stated license.
3. **No dead links** - The URL must point to an active, accessible page.
4. **Documentation** - The repository must have a README with at minimum:
   - What the server does
   - How to install and configure it
   - Basic usage instructions
5. **Not a duplicate** - Check that the server is not already listed.
6. **Maintained** - The project should show signs of active maintenance (recent commits, responses to issues). Abandoned projects may be removed.
7. **Stable enough to use** - The server should be functional. Experimental or proof-of-concept projects are acceptable if clearly labeled, but they must still work.

## Pull Request Process

1. **One server per PR.** If you want to add multiple servers, open separate pull requests for each.
2. Fork this repository and create a branch for your addition.
3. Add your entry to the correct category in `README.md`, following the [format](#format) described above.
4. Fill out the pull request template completely.
5. Ensure the automated link check passes.
6. A maintainer will review your PR. You may be asked to make changes.

### Commit Messages

Use clear, descriptive commit messages. For example:

```
Add Acme MCP server to Developer Tools
```

## Updating an Existing Entry

If a project has moved, changed names, or needs a corrected description:

1. Open a PR with the update.
2. Explain what changed and why in the PR description.

## Removing an Entry

If you notice a listed server is no longer maintained, has a broken link, or no longer implements MCP:

1. Open an issue describing the problem, or
2. Open a PR to remove it with an explanation.

## Reporting Issues

Use the [issue templates](https://github.com/your-username/awesome-mcp-servers/issues/new/choose) to:

- Suggest a new server to add
- Report a broken link
- Suggest a new category
- Report other issues

## Code of Conduct

This project follows the [Contributor Covenant Code of Conduct](CODE_OF_CONDUCT.md). By participating, you are expected to uphold this code.

---

Thank you for helping make this list awesome!
