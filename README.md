# Awesome MCP Servers [![Awesome](https://awesome.re/badge.svg)](https://awesome.re)

> A curated list of [Model Context Protocol (MCP)](https://modelcontextprotocol.io/) servers, tools, and resources.

MCP is an open protocol that enables AI assistants (Claude, GPT, etc.) to securely connect to local and remote data sources through standardized server implementations.

## Contents

- [Official](#official)
- [Servers](#servers)
  - [Data & Databases](#data--databases)
  - [Developer Tools](#developer-tools)
  - [Cloud & Infrastructure](#cloud--infrastructure)
  - [Productivity](#productivity)
  - [Search & Knowledge](#search--knowledge)
  - [Communication](#communication)
  - [File Systems & Storage](#file-systems--storage)
  - [AI & ML](#ai--ml)
  - [Finance](#finance)
  - [Monitoring & Observability](#monitoring--observability)
- [Frameworks & Libraries](#frameworks--libraries)
- [Clients](#clients)
- [Tutorials & Articles](#tutorials--articles)
- [Videos](#videos)
- [Community](#community)

---

## Official

- [MCP Specification](https://spec.modelcontextprotocol.io/) - The official protocol specification.
- [MCP TypeScript SDK](https://github.com/modelcontextprotocol/typescript-sdk) - Official TypeScript/Node.js SDK.
- [MCP Python SDK](https://github.com/modelcontextprotocol/python-sdk) - Official Python SDK.
- [MCP Servers (Reference)](https://github.com/modelcontextprotocol/servers) - Official reference server implementations.
- [MCP Inspector](https://github.com/modelcontextprotocol/inspector) - Visual testing tool for MCP servers.

## Servers

### Data & Databases

| Server | Description | Language |
|--------|-------------|----------|
| [PostgreSQL MCP](https://github.com/modelcontextprotocol/servers/tree/main/src/postgres) | Query and manage PostgreSQL databases | TypeScript |
| [SQLite MCP](https://github.com/modelcontextprotocol/servers/tree/main/src/sqlite) | Local SQLite database access | Python |
| [MongoDB MCP](https://github.com/kiliczsh/mcp-mongo-server) | MongoDB database operations | TypeScript |
| [Redis MCP](https://github.com/modelcontextprotocol/servers/tree/main/src/redis) | Redis cache and data store | TypeScript |
| [MySQL MCP](https://github.com/benborla/mcp-server-mysql) | MySQL database queries and management | TypeScript |
| [Supabase MCP](https://github.com/supabase-community/supabase-mcp) | Supabase database, auth, and storage | TypeScript |
| [Neon MCP](https://github.com/neondatabase/mcp-server-neon) | Neon serverless Postgres management | TypeScript |
| [Turso MCP](https://github.com/tursodatabase/mcp-server-turso) | Turso/libSQL embedded databases | TypeScript |

### Developer Tools

| Server | Description | Language |
|--------|-------------|----------|
| [GitHub MCP](https://github.com/modelcontextprotocol/servers/tree/main/src/github) | GitHub API — repos, issues, PRs, actions | TypeScript |
| [GitLab MCP](https://github.com/modelcontextprotocol/servers/tree/main/src/gitlab) | GitLab API integration | TypeScript |
| [Linear MCP](https://github.com/jerhadf/linear-mcp-server) | Linear project management | TypeScript |
| [Sentry MCP](https://github.com/modelcontextprotocol/servers/tree/main/src/sentry) | Sentry error tracking and monitoring | TypeScript |
| [Docker MCP](https://github.com/ckreiling/mcp-server-docker) | Docker container management | Python |
| [Kubernetes MCP](https://github.com/strowk/mcp-k8s-go) | Kubernetes cluster operations | Go |
| [NPM MCP](https://github.com/punkpeye/mcp-server-npm) | NPM package information and search | TypeScript |

### Cloud & Infrastructure

| Server | Description | Language |
|--------|-------------|----------|
| [AWS MCP Servers](https://github.com/awslabs/mcp) | Official AWS MCP servers (S3, Lambda, CDK, Bedrock, etc.) | Multiple |
| [Cloudflare MCP](https://github.com/cloudflare/mcp-server-cloudflare) | Cloudflare Workers, KV, R2, D1 | TypeScript |
| [Vercel MCP](https://github.com/vercel/mcp-server) | Vercel deployments and projects | TypeScript |
| [Terraform MCP](https://github.com/hashicorp/terraform-mcp-server) | Terraform/OpenTofu infrastructure management | Go |
| [Azure MCP](https://github.com/Azure/azure-mcp) | Azure cloud services | Python |

### Productivity

| Server | Description | Language |
|--------|-------------|----------|
| [Google Drive MCP](https://github.com/modelcontextprotocol/servers/tree/main/src/gdrive) | Google Drive file access | TypeScript |
| [Slack MCP](https://github.com/modelcontextprotocol/servers/tree/main/src/slack) | Slack workspace integration | TypeScript |
| [Notion MCP](https://github.com/modelcontextprotocol/servers/tree/main/src/notion) | Notion pages and databases | TypeScript |
| [Google Calendar MCP](https://github.com/nspady/google-calendar-mcp) | Google Calendar management | TypeScript |
| [Todoist MCP](https://github.com/abhiz123/todoist-mcp-server) | Todoist task management | TypeScript |
| [Obsidian MCP](https://github.com/smithery-ai/mcp-obsidian) | Obsidian vault access | TypeScript |

### Search & Knowledge

| Server | Description | Language |
|--------|-------------|----------|
| [Brave Search MCP](https://github.com/modelcontextprotocol/servers/tree/main/src/brave-search) | Brave Search API | TypeScript |
| [Exa MCP](https://github.com/exa-labs/exa-mcp-server) | Exa AI-powered search | TypeScript |
| [Tavily MCP](https://github.com/tavily-ai/tavily-mcp) | Tavily AI search for agents | Python |
| [Wikipedia MCP](https://github.com/modelcontextprotocol/servers/tree/main/src/wikipedia) | Wikipedia article search | TypeScript |
| [Context7 MCP](https://github.com/upstash/context7) | Up-to-date library documentation | TypeScript |

### Communication

| Server | Description | Language |
|--------|-------------|----------|
| [Discord MCP](https://github.com/v-3/discordmcp) | Discord bot and channel management | Python |
| [Telegram MCP](https://github.com/nicosql/mcp-telegram-server) | Telegram messaging | Python |
| [WhatsApp MCP](https://github.com/lharries/whatsapp-mcp) | WhatsApp messaging via web client | Python |

### File Systems & Storage

| Server | Description | Language |
|--------|-------------|----------|
| [Filesystem MCP](https://github.com/modelcontextprotocol/servers/tree/main/src/filesystem) | Local filesystem operations | TypeScript |
| [S3 MCP](https://github.com/awslabs/mcp/tree/main/src/amazon-s3-mcp-server) | AWS S3 bucket operations | Python |

### AI & ML

| Server | Description | Language |
|--------|-------------|----------|
| [HuggingFace MCP](https://github.com/evalstate/mcp-hfspace) | HuggingFace Spaces and models | TypeScript |
| [OpenAI MCP](https://github.com/pierrebrunelle/mcp-server-openai) | OpenAI API access | Python |
| [Ollama MCP](https://github.com/patruff/ollama-mcp-bridge) | Local Ollama model management | TypeScript |
| [LangChain MCP](https://github.com/rectalogic/langchain-mcp) | LangChain tool integration | Python |

### Finance

| Server | Description | Language |
|--------|-------------|----------|
| [Stripe MCP](https://github.com/stripe/agent-toolkit) | Stripe payments and billing | TypeScript |
| [Yahoo Finance MCP](https://github.com/nick-w-nick/yahoo-finance-mcp) | Stock data and financial info | TypeScript |

### Monitoring & Observability

| Server | Description | Language |
|--------|-------------|----------|
| [Datadog MCP](https://github.com/DataDog/datadog-mcp-server) | Datadog metrics and monitoring | TypeScript |
| [Grafana MCP](https://github.com/grafana/mcp-grafana) | Grafana dashboards and alerts | Go |
| [PagerDuty MCP](https://github.com/PagerDuty/mcp-server-pagerduty) | PagerDuty incident management | TypeScript |

## Frameworks & Libraries

| Project | Description | Language |
|---------|-------------|----------|
| [MCP TypeScript SDK](https://github.com/modelcontextprotocol/typescript-sdk) | Official TypeScript SDK for building MCP servers/clients | TypeScript |
| [MCP Python SDK](https://github.com/modelcontextprotocol/python-sdk) | Official Python SDK for building MCP servers/clients | Python |
| [FastMCP](https://github.com/jlowin/fastmcp) | Fast, Pythonic way to build MCP servers | Python |
| [mcp-framework](https://github.com/QuantGeekDev/mcp-framework) | Framework for building MCP servers with TypeScript | TypeScript |
| [EasyMCP](https://github.com/zueai/EasyMCP) | Simplified MCP server builder | TypeScript |
| [spring-ai-mcp](https://github.com/spring-projects-experimental/spring-ai-mcp) | Spring Boot MCP integration | Java |

## Clients

| Client | Description | MCP Support |
|--------|-------------|-------------|
| [Claude Desktop](https://claude.ai/download) | Anthropic's desktop app | Full |
| [Claude Code](https://docs.anthropic.com/en/docs/claude-code) | Anthropic's CLI coding agent | Full |
| [VS Code + Claude](https://marketplace.visualstudio.com/items?itemName=anthropics.claude-code) | VS Code extension | Full |
| [Cursor](https://cursor.com/) | AI-powered code editor | Partial |
| [Windsurf](https://codeium.com/windsurf) | Codeium's AI IDE | Partial |
| [Zed](https://zed.dev/) | High-performance code editor | Partial |
| [Continue](https://continue.dev/) | Open-source AI code assistant | Full |

## Tutorials & Articles

- [Introduction to MCP](https://modelcontextprotocol.io/introduction) - Official introduction to the protocol.
- [Building Your First MCP Server](https://modelcontextprotocol.io/quickstart/server) - Step-by-step server tutorial.
- [MCP for Claude Desktop](https://modelcontextprotocol.io/quickstart/user) - Getting started as a user.
- [Building MCP Servers with Python](https://modelcontextprotocol.io/tutorials/building-mcp-with-python) - Python-specific guide.

## Videos

- [What is MCP? (Anthropic)](https://www.youtube.com/watch?v=kQmXm3RtKFE) - Official overview of Model Context Protocol.
- [Build an MCP Server in 10 Minutes](https://www.youtube.com/watch?v=F9SJb5spdQM) - Quick tutorial on building MCP servers.

## Community

- [MCP GitHub Discussions](https://github.com/orgs/modelcontextprotocol/discussions) - Official community discussions.
- [r/ClaudeAI](https://www.reddit.com/r/ClaudeAI/) - Reddit community with MCP discussions.
- [MCP Servers Directory](https://mcpservers.org/) - Web directory of MCP servers.

---

## Contributing

Contributions are welcome! Please read the [contribution guidelines](CONTRIBUTING.md) before submitting a PR.

To add a new MCP server:
1. Fork this repo
2. Add your server to the appropriate category in `README.md`
3. Follow the format: `| [Name](URL) | Description | Language |`
4. Submit a PR

## License

[![CC0](https://licensebuttons.net/p/zero/1.0/88x31.png)](https://creativecommons.org/publicdomain/zero/1.0/)

This list is released under [CC0 1.0 Universal](LICENSE) — public domain.
