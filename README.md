# Awesome MCP Servers

[![Awesome](https://awesome.re/badge.svg)](https://awesome.re)
[![Lint](https://github.com/Sagargupta16/awesome-mcp-servers/actions/workflows/lint.yml/badge.svg)](https://github.com/Sagargupta16/awesome-mcp-servers/actions/workflows/lint.yml)
[![License: CC0-1.0](https://img.shields.io/badge/License-CC0--1.0-lightgrey.svg)](LICENSE)

> A curated list of [Model Context Protocol (MCP)](https://modelcontextprotocol.io/) servers, tools, frameworks, and resources.

MCP is an open protocol that lets AI assistants (Claude, GPT, Cursor, Windsurf, etc.) connect to local and remote data sources through standardized server implementations.

**This list is curated, not exhaustive, and open to anyone.** Bigger MCP lists exist. The point of this one is that everything on it has been checked. Curated does not mean famous: there is no star or age requirement, and submitting your own server is welcome. Every entry:

- implements MCP for real -- not a README with a `server.json` next to it
- states an open-source licence -- a `LICENSE` file, or a licence field in its package manifest
- was pushed within the last 180 days, and is not archived
- documents how to install and configure it, so someone else can actually run it
- appears exactly once, in one category

Those rules are enforced by [CI](.github/workflows/), not by good intentions: a pull request that breaks the format, adds a dead link, or submits an unlicensed repo fails its checks. A [monthly audit](.github/workflows/health.yml) re-checks every listed repository and files what has rotted.

An MCP server runs as a trusted extension of your assistant, with your files and your credentials. Read the source before you configure one -- a place on this list is a filter, not an audit. See [SECURITY.md](SECURITY.md).

## Using a server from this list

Two shapes cover the list. A **stdio** server is one your client starts itself and talks to over stdin and stdout. A **remote** server is hosted by the vendor, so the client needs only the endpoint; those rows carry `Remote` in the Language column.

Two stdio servers, run straight from their published packages:

```json
{
  "mcpServers": {
    "filesystem": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-filesystem", "/path/to/allowed/dir"]
    },
    "fetch": {
      "command": "uvx",
      "args": ["mcp-server-fetch"]
    }
  }
}
```

A remote server. `type` is not optional here: an entry with a `url` and no `type` is read as a stdio server and [skipped by Claude Code](https://code.claude.com/docs/en/mcp), which reports that the server has a `url` but no `type`.

```json
{
  "mcpServers": {
    "example": {
      "type": "http",
      "url": "https://mcp.example.com/mcp"
    }
  }
}
```

Where that JSON lives, and which extra keys it takes, differs per client -- check your own client's docs. The protocol's [guide to connecting a local server](https://modelcontextprotocol.io/docs/develop/connect-local-servers) walks through the stdio case, and each server's README lists the arguments, tokens and environment variables it expects.

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
  - [Design & Creative](#design--creative)
  - [Testing & QA](#testing--qa)
  - [Security](#security)
  - [Web Browsing & Scraping](#web-browsing--scraping)
  - [Media & Entertainment](#media--entertainment)
  - [Travel & Location](#travel--location)
  - [E-commerce](#e-commerce)
  - [Game Development](#game-development)
  - [IoT & Home Automation](#iot--home-automation)
  - [Marketing & Analytics](#marketing--analytics)
  - [Knowledge Management](#knowledge-management)
- [Frameworks & Libraries](#frameworks--libraries)
- [Clients](#clients)
- [Tutorials & Articles](#tutorials--articles)
- [Videos](#videos)
- [Community](#community)

---

## Official

- [MCP Specification](https://modelcontextprotocol.io/specification) - The official protocol specification.
- [MCP Servers (Reference)](https://github.com/modelcontextprotocol/servers) - Official reference server implementations (everything, fetch, filesystem, git, memory, sequentialthinking, time).
- [MCP Inspector](https://github.com/modelcontextprotocol/inspector) - Visual testing tool for MCP servers.
- [MCP Registry](https://github.com/modelcontextprotocol/registry) - Official community-driven registry for MCP servers.
- [MCP Apps](https://github.com/modelcontextprotocol/ext-apps) - Official MCP Apps spec and SDK for interactive UIs in AI clients.
- [MCP Bundles (MCPB)](https://github.com/modelcontextprotocol/mcpb) - Official bundle format for one-click local MCP server installs.
- [MCP Quickstart Resources](https://github.com/modelcontextprotocol/quickstart-resources) - Official quickstart weather servers and clients in five languages.
- [MCP Conformance Suite](https://github.com/modelcontextprotocol/conformance) - Official conformance test suite for MCP implementations.
- [MCP Example Remote Server](https://github.com/modelcontextprotocol/example-remote-server) - Official reference MCP server covering all features plus OAuth 2.0.

## Servers

### Data & Databases

| Server | Description | Language |
|--------|-------------|----------|
| [Apache Doris MCP](https://github.com/apache/doris-mcp-server) | Official Apache Doris analytics database queries and management | Python |
| [BigQuery MCP](https://github.com/ergut/mcp-bigquery-server) | Query Google BigQuery datasets and tables | TypeScript |
| [ClickHouse MCP](https://github.com/ClickHouse/mcp-clickhouse) | Official ClickHouse columnar analytics | Python |
| [Confluent MCP](https://github.com/confluentinc/mcp-confluent) | Official Confluent Cloud Kafka topics, connectors and Flink | TypeScript |
| [Couchbase MCP](https://github.com/couchbase/mcp-server-couchbase) | Official Couchbase and Capella cluster, scope and query access | Python |
| [DBHub](https://github.com/bytebase/dbhub) | Universal database server for Postgres, MySQL, SQL Server, MariaDB, SQLite | TypeScript |
| [dbt MCP](https://github.com/dbt-labs/dbt-mcp) | Official dbt Labs server for dbt projects | Python |
| [Elasticsearch MCP](https://github.com/elastic/mcp-server-elasticsearch) | Official Elasticsearch query interface | Rust |
| [GCP MCP Toolbox](https://github.com/googleapis/mcp-toolbox) | Official Google DB toolbox (Postgres, MySQL, Spanner) | Go |
| [MCP Alchemy](https://github.com/runekaagaard/mcp-alchemy) | SQLAlchemy-backed access to SQLite, Postgres, MySQL, Oracle and MS-SQL | Python |
| [Memgraph MCP](https://github.com/memgraph/ai-toolkit/tree/main/integrations/mcp-memgraph) | Official Memgraph graph database Cypher queries and schema | Python |
| [Milvus MCP](https://github.com/zilliztech/mcp-server-milvus) | Official Milvus vector database search and collection management | Python |
| [MongoDB MCP](https://github.com/mongodb-js/mongodb-mcp-server) | Official MongoDB and Atlas cluster management | TypeScript |
| [MotherDuck / DuckDB MCP](https://github.com/motherduckdb/mcp-server-motherduck) | Local DuckDB and MotherDuck cloud access | Python |
| [MySQL MCP](https://github.com/benborla/mcp-server-mysql) | MySQL database queries and management | TypeScript |
| [Neo4j MCP](https://github.com/neo4j-contrib/mcp-neo4j) | Neo4j Labs Cypher, memory and Aura API graph database servers | Python |
| [Neon MCP](https://github.com/neondatabase/mcp-server-neon) | Neon serverless Postgres branching and management | TypeScript |
| [Pinecone MCP](https://github.com/pinecone-io/pinecone-mcp) | Official Pinecone vector database | TypeScript |
| [PostgreSQL MCP (Pro)](https://github.com/crystaldba/postgres-mcp) | Query, analyze and optimize PostgreSQL databases | Python |
| [Qdrant MCP](https://github.com/qdrant/mcp-server-qdrant) | Official Qdrant vector database server | Python |
| [Redis MCP](https://github.com/redis/mcp-redis) | Official Redis cache and data structures | Python |
| [Snowflake MCP](https://github.com/Snowflake-Labs/mcp) | Official Snowflake Cortex AI + SQL orchestration | Python |
| [StarRocks MCP](https://github.com/StarRocks/mcp-server-starrocks) | Official StarRocks OLAP database query and schema access | Python |
| [Supabase MCP](https://github.com/supabase/mcp) | Supabase database, auth, and storage | TypeScript |
| [Upstash MCP](https://github.com/upstash/mcp-server) | Upstash Redis and Vector databases | TypeScript |

### Developer Tools

| Server | Description | Language |
|--------|-------------|----------|
| [Agentlas OS](https://github.com/agentlas-ai/Agentlas-OS) | Portable agent teams and cross-host orchestration over MCP | Python |
| [Apollo MCP Server](https://github.com/apollographql/apollo-mcp-server) | Official Apollo server exposing GraphQL operations as MCP tools | Rust |
| [Argo CD MCP](https://github.com/argoproj-labs/mcp-for-argocd) | Argo CD applications, syncs and GitOps state (argoproj-labs) | TypeScript |
| [ast-grep MCP](https://github.com/ast-grep/ast-grep-mcp) | Structural code search and rewrite via ast-grep patterns | Python |
| [Atlassian MCP (Jira + Confluence)](https://github.com/sooperset/mcp-atlassian) | Jira and Confluence integration | Python |
| [Azure DevOps MCP](https://github.com/microsoft/azure-devops-mcp) | Official Azure DevOps repos, pipelines, work items and wikis | TypeScript |
| [Bifrost MCP](https://github.com/biegehydra/BifrostMCP) | VS Code extension exposing find-usages, rename and LSP tools over MCP | TypeScript |
| [Buildkite MCP](https://github.com/buildkite/buildkite-mcp-server) | Official Buildkite pipelines, builds, jobs and test runs | Go |
| [Chrome DevTools MCP](https://github.com/ChromeDevTools/chrome-devtools-mcp) | Official Chrome DevTools for coding agents - debug, trace and inspect pages | TypeScript |
| [CircleCI MCP](https://github.com/CircleCI-Public/mcp-server-circleci) | Official CircleCI workflow integration | TypeScript |
| [Desktop Commander MCP](https://github.com/wonderwhy-er/DesktopCommanderMCP) | Terminal control, file search and diff-based file editing | TypeScript |
| [Docker MCP](https://github.com/ckreiling/mcp-server-docker) | Docker container management | Python |
| [Docker MCP Gateway](https://github.com/docker/mcp-gateway) | Official Docker MCP gateway and catalog CLI plugin | Go |
| [GitHub MCP](https://github.com/github/github-mcp-server) | Official GitHub -- repos, issues, PRs, Actions | Go |
| [GitLab MCP](https://github.com/zereight/gitlab-mcp) | GitLab API integration (repos, MRs, issues) | TypeScript |
| [GitMCP](https://github.com/idosal/git-mcp) | Remote MCP server exposing docs and code for any GitHub project | TypeScript |
| [Jenkins MCP Server](https://github.com/jenkinsci/mcp-server-plugin) | Official Jenkins plugin exposing jobs and builds as MCP tools | Java |
| [Jupyter MCP](https://github.com/datalayer/jupyter-mcp-server) | Jupyter notebook cell execution | Python |
| [Klavis](https://github.com/Klavis-AI/klavis) | Self-hostable MCP server platform with OAuth and hosted integrations | Python |
| [kubectl MCP](https://github.com/rohitg00/kubectl-mcp-server) | Natural-language kubectl operations (CNCF listed) | Python |
| [MartinLoop MCP](https://github.com/Keesan12/martin-loop/tree/main/packages/mcp) | Governed agent runtime with budget caps, verifier gates and inspectable runs | TypeScript |
| [MCP Context Forge](https://github.com/IBM/mcp-context-forge) | Official IBM MCP gateway federating MCP, A2A and REST tools | Python |
| [mcp-proxy](https://github.com/sparfenyuk/mcp-proxy) | Bridge between Streamable HTTP and stdio MCP transports | Python |
| [mcp-remote](https://github.com/geelen/mcp-remote) | Bridge stdio-only MCP clients to remote HTTP or SSE servers | TypeScript |
| [mcpo](https://github.com/open-webui/mcpo) | MCP-to-OpenAPI proxy that exposes MCP servers as REST endpoints | Python |
| [MetaMCP](https://github.com/metatool-ai/metamcp) | MCP aggregator, orchestrator and gateway in one container | TypeScript |
| [n8n MCP](https://github.com/czlonkowski/n8n-mcp) | Node docs and workflow building for n8n automations | TypeScript |
| [Nx MCP](https://github.com/nrwl/nx-console/tree/master/apps/nx-mcp) | Official Nx monorepo workspace graph and generator context server | TypeScript |
| [octocode-mcp](https://github.com/bgauryy/octocode-mcp) | Code research across GitHub repos and packages for coding agents | TypeScript |
| [Postman MCP](https://github.com/postmanlabs/postman-mcp-server) | Official Postman API collections server | TypeScript |
| [Probe](https://github.com/buger/probe) | Semantic code search over large codebases with ripgrep and tree-sitter | Rust |
| [Repomix](https://github.com/yamadashy/repomix) | Packs a repository into an AI-friendly file, with built-in MCP server | TypeScript |
| [SandBase Harness](https://github.com/sandbaseai/sandbase-harness) | Self-hosted MCP runtime with sandboxing, permissions and audit replay | TypeScript |
| [Sentry MCP](https://github.com/getsentry/sentry-mcp) | Official Sentry error and performance tracking | TypeScript |
| [Serena](https://github.com/oraios/serena) | Semantic code retrieval and editing toolkit for coding agents | Python |
| [Supergateway](https://github.com/supercorp-ai/supergateway) | Gateway that runs stdio MCP servers over SSE and HTTP | TypeScript |
| [XcodeBuildMCP](https://github.com/cameroncooke/XcodeBuildMCP) | Build, run and debug Xcode iOS and macOS projects from an agent | TypeScript |

### Cloud & Infrastructure

| Server | Description | Language |
|--------|-------------|----------|
| [Appwrite MCP](https://github.com/appwrite/mcp) | Official Appwrite databases, auth, storage, and functions | Python |
| [AWS MCP Servers](https://github.com/awslabs/mcp) | Official AWS MCP servers (S3, Lambda, CDK, Bedrock, etc.) | Multiple |
| [Azure MCP](https://github.com/microsoft/mcp) | Official Azure cloud services | C# |
| [Cloudflare MCP](https://github.com/cloudflare/mcp-server-cloudflare) | Cloudflare Workers, KV, R2, D1 | TypeScript |
| [DigitalOcean MCP](https://github.com/digitalocean-labs/mcp-digitalocean) | Official DO droplets, apps, databases | Go |
| [Firebase MCP](https://github.com/firebase/firebase-tools) | Official Firebase MCP server built into the Firebase CLI | TypeScript |
| [Fly.io MCP](https://github.com/superfly/flyctl) | Official Fly.io MCP server built into the flyctl CLI | Go |
| [Google Cloud MCP](https://github.com/googleapis/gcloud-mcp) | Official gcloud CLI wrapper for GCP services | TypeScript |
| [Google Cloud Run MCP](https://github.com/GoogleCloudPlatform/cloud-run-mcp) | Official Google Cloud Run app deployment and management | JavaScript |
| [Helm MCP](https://github.com/zekker6/mcp-helm) | Helm package manager for Kubernetes | Go |
| [Heroku MCP](https://github.com/heroku/heroku-mcp-server) | Official Heroku platform CLI wrapper | TypeScript |
| [Kubernetes MCP Server](https://github.com/containers/kubernetes-mcp-server) | Kubernetes and OpenShift cluster operations without kubectl | Go |
| [KubeStellar Console kc-agent](https://github.com/kubestellar/console) | MCP server for multi-cluster Kubernetes AI operations (CNCF Sandbox) | Go |
| [LocalStack MCP](https://github.com/localstack/localstack-mcp-server) | Official LocalStack local AWS cloud emulator control | TypeScript |
| [Nomad MCP](https://github.com/kocierik/mcp-nomad) | HashiCorp Nomad cluster operations | Go |
| [Oracle MCP Servers](https://github.com/oracle/mcp) | Official Oracle MCP servers for OCI compute, networking, and databases | Python |
| [Portainer MCP](https://github.com/portainer/portainer-mcp) | Official Portainer container and environment management | Python |
| [Railway MCP](https://docs.railway.com/cli/mcp) | Official Railway MCP server built into the Railway CLI | Rust |
| [Render MCP](https://github.com/render-oss/render-mcp-server) | Official Render deployment server | Go |
| [Tencent CloudBase AI Toolkit](https://github.com/TencentCloudBase/CloudBase-AI-Toolkit) | Tencent CloudBase database, auth, and cloud functions | TypeScript |
| [Terraform MCP](https://github.com/hashicorp/terraform-mcp-server) | Official HashiCorp Terraform / OpenTofu | Go |
| [Vercel Next DevTools MCP](https://github.com/vercel/next-devtools-mcp) | Official Next.js dev tools for coding agents | TypeScript |

### Productivity

| Server | Description | Language |
|--------|-------------|----------|
| [Airtable MCP](https://github.com/domdomegg/airtable-mcp-server) | Airtable base read/write | TypeScript |
| [Asana MCP](https://github.com/roychri/mcp-server-asana) | Asana tasks, projects, workspaces | TypeScript |
| [Coda MCP](https://github.com/orellazri/coda-mcp) | Coda documents and tables | TypeScript |
| [Excel MCP](https://github.com/haris-musa/excel-mcp-server) | Read, write and format Excel workbooks without Excel installed | Python |
| [Google Calendar MCP](https://github.com/nspady/google-calendar-mcp) | Google Calendar management | TypeScript |
| [Google Workspace MCP](https://github.com/taylorwilsdon/google_workspace_mcp) | Gmail, Calendar, Docs, Sheets, Slides, Chat, Forms and Tasks in one server | Python |
| [iMCP](https://github.com/mattt/iMCP) | Exposes macOS Messages, Contacts, Calendar and Reminders to agents | Swift |
| [Make MCP](https://github.com/integromat/make-mcp-server) | Official Make server turning scenarios into callable agent tools | TypeScript |
| [Microsoft 365 MCP](https://github.com/Softeria/ms-365-mcp-server) | Full M365 suite (Outlook, OneDrive, Teams, Excel) | TypeScript |
| [monday.com MCP](https://github.com/mondaycom/mcp) | Official monday.com boards, items and workspace automation | TypeScript |
| [Nextcloud MCP](https://github.com/cbcoutinho/nextcloud-mcp-server) | Nextcloud Notes, Files, Calendar, Tasks, Deck and Talk access | Python |
| [Notion MCP](https://github.com/makenotion/notion-mcp-server) | Official Notion API integration | TypeScript |
| [Outlook MCP](https://github.com/ryaker/outlook-mcp) | Outlook email and calendar via MS Graph | JavaScript |
| [Plane MCP](https://github.com/makeplane/plane-mcp-server) | Official Plane projects, work items and cycles automation | Python |
| [Slack MCP](https://github.com/korotovsky/slack-mcp-server) | Slack workspace integration | Go |
| [Trello MCP](https://github.com/delorenj/mcp-server-trello) | Trello boards, lists, cards | TypeScript |

### Search & Knowledge

| Server | Description | Language |
|--------|-------------|----------|
| [Apify MCP](https://github.com/apify/apify-mcp-server) | Web scraping actors and automation | TypeScript |
| [arXiv MCP](https://github.com/blazickjp/arxiv-mcp-server) | Search arXiv papers and read full LaTeX sections | Python |
| [Brave Search MCP](https://github.com/brave/brave-search-mcp-server) | Official Brave Search API | TypeScript |
| [Context7 MCP](https://github.com/upstash/context7) | Up-to-date library documentation | TypeScript |
| [DeepWiki MCP](https://github.com/regenrek/deepwiki-mcp) | Fetch deepwiki.com repo docs as markdown | TypeScript |
| [Docling MCP](https://github.com/docling-project/docling-mcp) | Official Docling document parsing and conversion to structured text | Python |
| [Docs MCP Server](https://github.com/arabold/docs-mcp-server) | Index and semantically search third-party library documentation | TypeScript |
| [DuckDuckGo MCP](https://github.com/nickclyde/duckduckgo-mcp-server) | DuckDuckGo search with content fetching | Python |
| [Exa MCP](https://github.com/exa-labs/exa-mcp-server) | Exa AI-powered search | TypeScript |
| [Kagi MCP](https://github.com/kagisearch/kagimcp) | Official Kagi search API | Python |
| [MarkItDown MCP](https://github.com/microsoft/markitdown/tree/main/packages/markitdown-mcp) | Convert PDF, Office, HTML and audio files to Markdown for LLMs | Python |
| [MCPDoc](https://github.com/langchain-ai/mcpdoc) | Official LangChain server for llms.txt documentation sources | Python |
| [Meilisearch MCP](https://github.com/meilisearch/meilisearch-mcp) | Official Meilisearch index server | Python |
| [Perplexity MCP](https://github.com/perplexityai/modelcontextprotocol) | Official Perplexity search API | TypeScript |
| [Ref MCP](https://github.com/ref-tools/ref-tools-mcp) | Token-efficient search over public and private technical docs | TypeScript |
| [SearXNG MCP](https://github.com/ihor-sokoliuk/mcp-searxng) | Metasearch across engines via a self-hosted SearXNG instance | TypeScript |
| [SerpAPI MCP](https://github.com/serpapi/serpapi-mcp) | Official SerpAPI Google search results | Python |
| [Tavily MCP](https://github.com/tavily-ai/tavily-mcp) | Tavily AI search for agents | JavaScript |

### Communication

| Server | Description | Language |
|--------|-------------|----------|
| [Discourse MCP](https://github.com/discourse/discourse-mcp) | Official Discourse forum search, topic reading and posting | TypeScript |
| [Joinly](https://github.com/joinly-ai/joinly) | Join Zoom, Google Meet and Teams calls to transcribe and act live | Python |
| [LINE Bot MCP](https://github.com/line/line-bot-mcp-server) | Official LINE Messaging API server for sending and managing messages | TypeScript |
| [Mailgun MCP](https://github.com/mailgun/mailgun-mcp-server) | Official Mailgun email sending, logs and analytics | TypeScript |
| [Mailtrap MCP](https://github.com/mailtrap/mailtrap-mcp) | Official Mailtrap email sending and sandbox testing | TypeScript |
| [Microsoft Teams MCP](https://github.com/InditexTech/mcp-teams-server) | Teams channels, messages, meetings | Python |
| [Resend MCP](https://github.com/resend/resend-mcp) | Official Resend transactional email | TypeScript |
| [sms-florin MCP](https://github.com/flovoice53-tech/sms-florin-mcp) | Rent real UK SMS numbers to test OTP/verification flows | TypeScript |
| [Telegram MCP](https://github.com/chigwell/telegram-mcp) | Telegram messaging | Python |
| [Zulip MCP](https://github.com/zulip/zulipmcp) | Official Zulip streams, messages and mentionable bot agents | Python |

### File Systems & Storage

| Server | Description | Language |
|--------|-------------|----------|
| [Dropbox Dash MCP](https://github.com/dropbox/mcp-server-dash) | Official Dropbox Dash search server | Python |
| [Filesystem MCP](https://github.com/modelcontextprotocol/servers/tree/main/src/filesystem) | Local filesystem operations | TypeScript |
| [Google Sheets MCP](https://github.com/xing5/mcp-google-sheets) | Create and edit Google Sheets spreadsheets via Google Drive | Python |
| [Markdownify MCP](https://github.com/zcaceres/markdownify-mcp) | Convert PDF, Office, audio and web files to Markdown | TypeScript |
| [OneDrive / SharePoint MCP](https://github.com/ftaricano/mcp-onedrive-sharepoint) | OneDrive and SharePoint document access | TypeScript |
| [S3 Tables MCP](https://github.com/awslabs/mcp/tree/main/src/s3-tables-mcp-server) | Official AWS S3 Tables | Python |

### AI & ML

| Server | Description | Language |
|--------|-------------|----------|
| [AISOTools MCP](https://aisotools.com/mcp) | AI-tool catalog search, comparison, and alternatives lookup | Remote |
| [Cognee MCP](https://github.com/topoteretes/cognee) | Memory and knowledge-graph engine with an MCP server | Python |
| [Graphiti MCP](https://github.com/getzep/graphiti/tree/main/mcp_server) | Temporal knowledge-graph memory for agents, by Zep | Python |
| [Groq MCP](https://github.com/groq/groq-mcp-server) | Official Groq inference, audio, and vision tools | Python |
| [Headroom MCP](https://github.com/headroomlabs-ai/headroom) | Token-compression proxy and MCP server for tool output and logs | Python |
| [HuggingFace MCP](https://github.com/huggingface/hf-mcp-server) | Official HF Hub models, datasets, Spaces | TypeScript |
| [LangChain MCP Adapters](https://github.com/langchain-ai/langchain-mcp-adapters) | Official LangChain / LangGraph MCP bridge | Python |
| [prompt-to-asset](https://github.com/MohamedAbdallah-14/prompt-to-asset) | Image generation across 30+ models via unified API | TypeScript |
| [Replicate MCP](https://replicate.com/docs/reference/mcp) | Official Replicate hosted MCP server | Remote |
| [RouterBase MCP](https://github.com/zenlee123/routerbase-mcp) | Model discovery, pricing lookup and OpenAI-compatible chat completions | TypeScript |
| [RunAPI MCP](https://github.com/runapi-ai/mcp) | Model discovery, pricing lookup, task creation, and LLM chat | TypeScript |
| [SandBase CLI](https://github.com/sandbaseai/cli) | Local MCP gateway for discovering and running 2,000+ AI models via one API | TypeScript |
| [Weights & Biases MCP](https://github.com/wandb/wandb-mcp-server) | Official W&B Models + Weave | Python |

### Finance

| Server | Description | Language |
|--------|-------------|----------|
| [Adyen MCP](https://github.com/Adyen/adyen-mcp) | Official Adyen server for checkout, configuration and management APIs | TypeScript |
| [Alpaca MCP](https://github.com/alpacahq/alpaca-mcp-server) | Official Alpaca stocks / ETF / crypto trading | Python |
| [Coinbase MCP](https://github.com/coinbase/agentkit) | Coinbase crypto trading and wallet | TypeScript |
| [Financial Modeling Prep MCP](https://github.com/imbenrabi/Financial-Modeling-Prep-MCP-Server) | FMP market data and fundamentals | TypeScript |
| [Invoice MCP](https://github.com/theluckystrike/mcp-invoice) | Create PDF invoices with VAT lines, sequential numbering and overdue tracking | JavaScript |
| [Massive.com (Polygon.io) MCP](https://github.com/massive-com/mcp_massive) | Official Massive.com (formerly Polygon.io) market data for stocks and crypto | Python |
| [MetaTrader MCP](https://github.com/ariadng/metatrader-mcp-server) | Place and manage MetaTrader 5 trades, positions and market data | Python |
| [ParlayAPI](https://github.com/JacobiusMakes/parlay-api-mcp) | Sports odds and player props using your own API key and account allowances | Python |
| [PayPal Agent Toolkit](https://github.com/paypal/agent-toolkit) | Official PayPal toolkit with an MCP server for payments and invoicing | TypeScript |
| [QuickBooks MCP](https://github.com/intuit/quickbooks-online-mcp-server) | Official Intuit QuickBooks Online | TypeScript |
| [Razorpay MCP](https://github.com/razorpay/razorpay-mcp-server) | Official Razorpay server for payments, orders, refunds and settlements | Go |
| [SEC EDGAR MCP](https://github.com/stefanoamorelli/sec-edgar-mcp) | Query SEC EDGAR filings, XBRL financials and company facts | Python |
| [Square MCP](https://github.com/square/square-mcp-server) | Official Square payments and commerce | TypeScript |
| [Stripe MCP](https://github.com/stripe/ai) | Stripe payments and billing | TypeScript |
| [TWZRD Agent Intel](https://smithery.ai/servers/wzrd/twzrd-agent-intel) | Solana on-chain wallet trust scoring for agents before x402 micropayments | Remote |
| [Xero MCP](https://github.com/XeroAPI/xero-mcp-server) | Official Xero server for invoices, contacts, accounts and payroll | TypeScript |
| [Yahoo Finance MCP](https://github.com/Alex2Yang97/yahoo-finance-mcp) | Stock data and financial info | Python |
| [Zerodha Kite MCP](https://github.com/zerodha/kite-mcp-server) | Official Zerodha Kite server for Indian holdings, orders and quotes | Go |

### Monitoring & Observability

| Server | Description | Language |
|--------|-------------|----------|
| [ax](https://github.com/Necmttn/ax) | Agent session telemetry and cost analytics | TypeScript |
| [Datadog MCP](https://github.com/winor30/mcp-server-datadog) | Datadog metrics, logs, monitors | TypeScript |
| [Dynatrace MCP](https://github.com/dynatrace-oss/dynatrace-mcp) | Official Dynatrace observability problems, logs and traces | TypeScript |
| [Grafana MCP](https://github.com/grafana/mcp-grafana) | Official Grafana dashboards and alerts | Go |
| [Honeycomb MCP](https://docs.honeycomb.io/integrations/mcp/) | Official Honeycomb trace queries | Remote |
| [Logfire MCP](https://logfire.pydantic.dev/docs/how-to-guides/mcp-server/) | Official Pydantic Logfire observability | Remote |
| [Netdata MCP](https://github.com/netdata/netdata) | Official Netdata observability with a built-in MCP server | C |
| [OpenTelemetry MCP](https://github.com/traceloop/opentelemetry-mcp-server) | Unified OTEL traces across backends | Python |
| [Prometheus MCP](https://github.com/pab1it0/prometheus-mcp-server) | Prometheus metrics and PromQL queries | Python |
| [VictoriaMetrics MCP](https://github.com/VictoriaMetrics/mcp-victoriametrics) | Official VictoriaMetrics metrics and logs queries | Go |
| [Zabbix MCP](https://github.com/mpeirone/zabbix-mcp-server) | Zabbix monitoring hosts, triggers, problems and templates | Python |

### Design & Creative

| Server | Description | Language |
|--------|-------------|----------|
| [Adobe Premiere Pro MCP](https://github.com/hetpatel-11/Adobe_Premiere_Pro_MCP) | Drive Adobe Premiere Pro timelines and edits from an agent | TypeScript |
| [AntV Chart MCP](https://github.com/antvis/mcp-server-chart) | Official AntV server generating 25+ chart types | TypeScript |
| [Aseprite MCP](https://github.com/diivi/aseprite-mcp) | Create and edit pixel art through the Aseprite API | Python |
| [Blender MCP](https://github.com/ahujasid/blender-mcp) | Control Blender 3D modeling from AI assistants | Python |
| [ComfyUI MCP](https://github.com/artokun/comfyui-mcp) | Run and author ComfyUI workflows for image, video, and audio | TypeScript |
| [DaVinci Resolve MCP](https://github.com/samuelgursky/davinci-resolve-mcp) | Control DaVinci Resolve editing, color grading, and project media | Python |
| [designlang](https://github.com/Manavarya09/design-extract) | Extract a website's design system into DTCG tokens and framework code | JavaScript |
| [Excalidraw MCP](https://github.com/yctimlin/mcp_excalidraw) | Create and edit Excalidraw diagrams on a live canvas | TypeScript |
| [Figma Context MCP](https://github.com/GLips/Figma-Context-MCP) | Figma layouts for AI coding agents (Framelink) | TypeScript |
| [Houdini MCP](https://github.com/capoomgit/houdini-mcp) | Build and modify SideFX Houdini scenes and nodes | Python |
| [OrkasVideoStudio](https://github.com/Orkas-AI/Orkas-VideoStudio) | Compose, edit, analyze, and render video from coding agents | TypeScript |
| [Photoshop MCP](https://github.com/loonghao/photoshop-python-api-mcp-server) | Adobe Photoshop automation | Python |
| [Webflow MCP](https://github.com/webflow/mcp-server) | Official Webflow server for sites, pages, CMS, and components | TypeScript |

### Testing & QA

| Server | Description | Language |
|--------|-------------|----------|
| [a11y MCP](https://github.com/ronantakizawa/a11ymcp) | Web accessibility / WCAG automated testing | JavaScript |
| [Appium MCP](https://github.com/appium/appium-mcp) | Official Appium mobile app test automation | TypeScript |
| [Axe MCP](https://github.com/dequelabs/axe-mcp-server-public) | Official Deque accessibility testing + AI remediation | TypeScript |
| [BrowserStack MCP](https://github.com/browserstack/mcp-server) | Official BrowserStack cross-browser and device testing | TypeScript |
| [Playwright MCP](https://github.com/microsoft/playwright-mcp) | Official Microsoft Playwright browser automation | TypeScript |

### Security

| Server | Description | Language |
|--------|-------------|----------|
| [Binary Ninja MCP](https://github.com/fosdickio/binary_ninja_mcp) | Binary Ninja plugin for LLM-driven binary analysis | Python |
| [Bitwarden MCP](https://github.com/bitwarden/mcp-server) | Official Bitwarden password manager | TypeScript |
| [Bolt (MCP for Security)](https://github.com/CyberStrikeus/bolt) | SQLMap, FFUF, Nmap, Masscan and 100+ Kali tools via MCP | TypeScript |
| [Burp AI Agent](https://github.com/six2dez/burp-ai-agent) | Burp Suite extension with MCP tooling | Kotlin |
| [CrowdStrike Falcon MCP](https://github.com/CrowdStrike/falcon-mcp) | Official CrowdStrike Falcon threat hunting and detections | Python |
| [Dark-Moon](https://github.com/ASCIT31/Dark-Moon) | Autonomous pentest platform for web, API, Active Directory and Kubernetes | Python |
| [DomScan MCP](https://github.com/estevecastells/domscan-mcp) | Domain intelligence: DNS, WHOIS, SSL, subdomains and typosquatting checks | TypeScript |
| [HashiCorp Vault MCP](https://github.com/hashicorp/vault-mcp-server) | Official HashiCorp Vault secrets and mounts management | Go |
| [http-detection-agent](https://github.com/ai-blueteam/http-detection-agent) | Capability-aware HTTP attack detection over a 76-rule catalog | Rust |
| [IDA Pro MCP](https://github.com/mrexodia/ida-pro-mcp) | IDA Pro reverse engineering assistant for LLM clients | Python |
| [MCP Security Hub](https://github.com/FuzzingLabs/mcp-security-hub) | Offensive tools (Nmap, Ghidra, Nuclei) | Python |
| [mcp-scan](https://github.com/invariantlabs-ai/mcp-scan) | Scans MCP servers for tool poisoning and prompt injection | Python |
| [radare2 MCP](https://github.com/radareorg/radare2-mcp) | Official radare2 reverse engineering stdio server | C |
| [Semgrep MCP](https://github.com/semgrep/semgrep/tree/develop/cli/src/semgrep/mcp) | Official Semgrep static analysis for vulnerabilities | Python |
| [Shodan MCP](https://github.com/w0h1v/mcp-shodan) | Shodan device search, IP recon, DNS and CVE intelligence | TypeScript |
| [vet](https://github.com/safedep/vet) | Dependency and malicious package scanning with an MCP server | Go |

### Web Browsing & Scraping

| Server | Description | Language |
|--------|-------------|----------|
| [Bright Data MCP](https://github.com/brightdata/brightdata-mcp) | Official Bright Data web search, scraping, and browser automation | JavaScript |
| [Browser Tools MCP](https://github.com/AgentDeskAI/browser-tools-mcp) | Read browser console logs, network traffic and DOM via a Chrome extension | TypeScript |
| [Crawl4AI](https://github.com/unclecode/crawl4ai) | LLM-friendly web crawler and scraper with built-in MCP endpoints | Python |
| [Firecrawl MCP](https://github.com/firecrawl/firecrawl-mcp-server) | Official Firecrawl web scraping and search | TypeScript |
| [Jina AI MCP](https://github.com/jina-ai/MCP) | Official Jina AI web reader, search, and content reranking | TypeScript |
| [Skyvern](https://github.com/Skyvern-AI/skyvern/tree/main/integrations/mcp) | Browser workflow automation via LLMs and computer vision, over MCP | Python |
| [Xquik MCP](https://github.com/Xquik-dev/x-twitter-scraper) | X/Twitter search, profile tweets, posting, and media tools | TypeScript |

### Media & Entertainment

| Server | Description | Language |
|--------|-------------|----------|
| [Ableton MCP](https://github.com/ahujasid/ableton-mcp) | Control Ableton Live sessions, tracks, clips, and MIDI from an agent | Python |
| [Arr MCP](https://github.com/aplaceforallmystuff/mcp-arr) | Manage Sonarr, Radarr, and other arr media library services | TypeScript |
| [Live Tennis API MCP](https://github.com/livetennisapi/livetennisapi-mcp) | Live tennis scores, match state, and model win-probability | TypeScript |
| [MiniMax MCP](https://github.com/MiniMax-AI/MiniMax-MCP) | Generate speech, music, images, and video with MiniMax models | Python |
| [TMDB MCP](https://github.com/Laksh-star/mcp-server-tmdb) | The Movie Database (TMDB) | TypeScript |
| [YouTube MCP](https://github.com/ZubeidHendricks/youtube-mcp-server) | YouTube API videos and analytics | TypeScript |
| [YouTube Transcript MCP](https://github.com/kimtaeyoon83/mcp-server-youtube-transcript) | Download YouTube video transcripts | TypeScript |

### Travel & Location

| Server | Description | Language |
|--------|-------------|----------|
| [Airbnb MCP](https://github.com/openbnb-org/mcp-server-airbnb) | Search Airbnb from your AI agent | JavaScript |
| [Cesium MCP](https://github.com/CesiumGS/cesium-ai-integrations/tree/main/mcp) | Official Cesium 3D geospatial and geolocation MCP servers | TypeScript |
| [GIS MCP](https://github.com/mahdin75/gis-mcp) | Geospatial analysis via GDAL, Shapely, GeoPandas, and PyProj | Python |
| [Google Maps MCP](https://github.com/cablate/mcp-google-map) | Google Maps API with LLM processing | TypeScript |
| [Mapbox MCP](https://github.com/mapbox/mcp-server) | Official Mapbox geocoding, POI search, directions, and isochrones | TypeScript |
| [TomTom MCP](https://github.com/tomtom-international/tomtom-mcp) | Official TomTom maps, search, routing, and traffic APIs | TypeScript |

### E-commerce

| Server | Description | Language |
|--------|-------------|----------|
| [Amazon MCP](https://github.com/rigwild/mcp-server-amazon) | Search and purchase Amazon products | TypeScript |
| [commercetools MCP Essentials](https://github.com/commercetools/mcp-essentials) | Official commercetools server for products, carts, orders and customers | TypeScript |
| [eBay MCP](https://github.com/YosefHayim/ebay-mcp) | 325 tools for eBay Sell APIs | TypeScript |
| [Packrift MCP](https://github.com/Packrift/packrift-mcp) | Packaging catalog search, pricing, inventory, and cart URLs | TypeScript |
| [Saleor MCP](https://github.com/saleor/saleor-mcp) | Official Saleor server for products, orders, customers and channels | Python |
| [Shopify MCP](https://github.com/GeLi2001/shopify-mcp) | Shopify API integration | TypeScript |

### Game Development

| Server | Description | Language |
|--------|-------------|----------|
| [Cocos Creator MCP](https://github.com/FunplayAI/funplay-cocos-mcp) | Automate the Cocos Creator editor: scenes, assets, and scripts | JavaScript |
| [Godot MCP](https://github.com/Coding-Solo/godot-mcp) | Godot game engine integration | JavaScript |
| [Minecraft MCP Server](https://github.com/yuniko-software/minecraft-mcp-server) | Control a Minecraft bot to build, mine, and navigate in game | TypeScript |
| [Roblox Studio MCP](https://create.roblox.com/docs/studio/mcp) | Official MCP server built into Roblox Studio | Built-in |
| [STS2MCP](https://github.com/Gennadiyev/STS2MCP) | Read Slay the Spire 2 game state and play runs through a mod | C# |
| [Unity MCP Server](https://github.com/AnkleBreaker-Studio/unity-mcp-server) | 268 tools for Unity Editor / Hub | JavaScript |
| [Unreal MCP](https://github.com/ChiR24/Unreal_mcp) | Unreal Engine C++ Automation Bridge | Multiple |
| [UnrealGenAISupport](https://github.com/prajwalshettydev/UnrealGenAISupport) | UE5 plugin for LLM/GenAI + MCP | C++ |

### IoT & Home Automation

| Server | Description | Language |
|--------|-------------|----------|
| [Apache IoTDB MCP](https://github.com/apache/iotdb-mcp-server) | Official MCP server for the Apache IoTDB time-series database | Python |
| [Bagel](https://github.com/Extelligence-ai/bagel) | Query robotics, drone, and IoT telemetry in plain English | Python |
| [Hass MCP](https://github.com/voska/hass-mcp) | Minimal Home Assistant MCP | Python |
| [Home Assistant MCP (ha-mcp)](https://github.com/homeassistant-ai/ha-mcp) | The unofficial awesome Home Assistant MCP | Python |
| [HomeClaw](https://github.com/omarshahine/HomeClaw) | Control HomeKit lights, locks, thermostats, and scenes on macOS | Swift |
| [MQTT MCP](https://github.com/ezhuk/mqtt-mcp) | Generic MQTT broker interaction | Python |
| [UniFi MCP](https://github.com/sirkirby/unifi-mcp) | Query and control UniFi Network, Protect, Access, and Drive | Python |

### Marketing & Analytics

| Server | Description | Language |
|--------|-------------|----------|
| [BulkPublish MCP](https://github.com/azeemkafridi/bulkpublish-api) | AI-agent API and MCP server for multi-platform social publishing and analytics | TypeScript |
| [DataForSEO MCP](https://github.com/dataforseo/mcp-server-typescript) | Official DataForSEO server for SERP, keyword and backlink data | TypeScript |
| [Google Analytics MCP](https://github.com/surendranb/google-analytics-mcp) | GA4 data for AI agents | Python |
| [Google Search Console MCP](https://github.com/AminForou/mcp-gsc) | Query Google Search Console search analytics, sitemaps and indexing | Python |
| [Google Tag Manager MCP](https://github.com/stape-io/google-tag-manager-mcp-server) | Manage GTM containers, tags, triggers and variables | TypeScript |
| [LLM Pulse MCP](https://github.com/LLM-Pulse/llmpulse-mcp) | AI visibility analytics for mentions, citations, sentiment, and AI traffic | JavaScript |
| [Meta Ads MCP (GoMarble)](https://github.com/gomarble-ai/facebook-ads-mcp-server) | Read and manage Meta and Instagram ad campaigns via the Meta Ads API | Python |
| [NotFair](https://github.com/nowork-studio/NotFair) | Google Ads, Meta Ads, and SEO skills with human-approval gate | TypeScript |
| [PostHog MCP](https://github.com/PostHog/posthog/tree/master/services/mcp) | Official PostHog product analytics | TypeScript |
| [Salesforce MCP](https://github.com/salesforcecli/mcp) | Official Salesforce CLI MCP | TypeScript |
| [UnrealUGC MCP](https://github.com/UnrealUGC/mcp) | Create AI UGC video ads through the UnrealUGC platform | TypeScript |

### Knowledge Management

| Server | Description | Language |
|--------|-------------|----------|
| [Anki MCP](https://github.com/ankimcp/anki-mcp-server) | Anki flashcards via AnkiConnect | TypeScript |
| [Anytype MCP](https://github.com/anyproto/anytype-mcp) | Official MCP server for the Anytype local-first workspace | TypeScript |
| [Basic Memory](https://github.com/basicmachines-co/basic-memory) | Local-first Markdown knowledge base with persistent agent memory | Python |
| [Joplin MCP](https://github.com/alondmnt/joplin-mcp) | Read, search, and write Joplin notes and notebooks | Python |
| [Karakeep MCP](https://github.com/karakeep-app/karakeep/tree/main/apps/mcp) | Official server for the Karakeep bookmark and read-later app | TypeScript |
| [Logseq MCP](https://github.com/ergut/mcp-logseq) | Read / write / manage LogSeq graph | Python |
| [Obsidian MCP](https://github.com/MarkusPfundstein/mcp-obsidian) | Obsidian via REST API community plugin | Python |
| [Obsidian MCP (alt)](https://github.com/StevenStavrakis/obsidian-mcp) | Simple MCP server for Obsidian | TypeScript |
| [Zotero MCP](https://github.com/54yyyu/zotero-mcp) | Search and read your Zotero reference library | Python |

## Frameworks & Libraries

| Project | Description | Language |
|---------|-------------|----------|
| [21st Magic MCP](https://github.com/21st-dev/magic-mcp) | AI component builder for React | TypeScript |
| [FastMCP (Python)](https://github.com/PrefectHQ/fastmcp) | Fast, Pythonic way to build MCP servers | Python |
| [FastMCP (TypeScript)](https://github.com/punkpeye/fastmcp) | TypeScript framework for building MCP servers | TypeScript |
| [Google ADK](https://github.com/google/adk-python) | Official Google Agent Development Kit with an MCP toolset | Python |
| [MCP C# SDK](https://github.com/modelcontextprotocol/csharp-sdk) | Official C# and .NET SDK for MCP servers and clients | C# |
| [MCP Go SDK](https://github.com/modelcontextprotocol/go-sdk) | Official Go SDK for MCP servers and clients | Go |
| [MCP Java SDK](https://github.com/modelcontextprotocol/java-sdk) | Official Java SDK, maintained with Spring AI | Java |
| [MCP Kotlin SDK](https://github.com/modelcontextprotocol/kotlin-sdk) | Official Kotlin SDK for MCP servers and clients | Kotlin |
| [MCP PHP SDK](https://github.com/modelcontextprotocol/php-sdk) | Official PHP SDK for MCP servers and clients | PHP |
| [MCP Python SDK](https://github.com/modelcontextprotocol/python-sdk) | Official Python SDK for servers and clients | Python |
| [MCP Ruby SDK](https://github.com/modelcontextprotocol/ruby-sdk) | Official Ruby SDK for MCP servers and clients | Ruby |
| [MCP Rust SDK](https://github.com/modelcontextprotocol/rust-sdk) | Official Rust SDK for MCP servers and clients | Rust |
| [MCP Swift SDK](https://github.com/modelcontextprotocol/swift-sdk) | Official Swift SDK for MCP servers and clients | Swift |
| [MCP TypeScript SDK](https://github.com/modelcontextprotocol/typescript-sdk) | Official TypeScript SDK for servers and clients | TypeScript |
| [mcp-framework](https://github.com/QuantGeekDev/mcp-framework) | TypeScript framework for building MCP servers | TypeScript |
| [mcp-go (mark3labs)](https://github.com/mark3labs/mcp-go) | Community Go library for building MCP servers and clients | Go |
| [mcp-use](https://github.com/mcp-use/mcp-use) | Fullstack framework for MCP apps, servers, and agent clients | TypeScript |
| [OpenAI Agents SDK](https://github.com/openai/openai-agents-python) | Official OpenAI multi-agent framework with MCP server support | Python |
| [Pydantic AI](https://github.com/pydantic/pydantic-ai) | Typed Python agent framework with MCP client and server support | Python |
| [Quarkus MCP Server](https://github.com/quarkiverse/quarkus-mcp-server) | Quarkus extension for building MCP servers in Java | Java |
| [Spring AI MCP](https://github.com/spring-projects/spring-ai) | Spring Boot starters for MCP servers and clients | Java |
| [Strands Agents SDK](https://github.com/strands-agents/sdk-python) | AWS agent SDK with MCP tool clients and its own MCP server | Python |
| [Vercel mcp-handler](https://github.com/vercel/mcp-handler) | Official Vercel MCP adapter for meta-frameworks | TypeScript |
| [xmcp](https://github.com/basementstudio/xmcp) | TypeScript MCP framework with CLI scaffolding for Next.js and Express | TypeScript |

## Clients

Support tiers reflect which MCP primitives each client implements, verified against its own docs:
**Full** tools, resources, prompts, plus sampling or elicitation. **Standard** tools, resources and
prompts. **Tools + resources** no prompts. **Tools only** tools alone. **Partial** tools plus some
but not all of resources and prompts.

| Client | Description | MCP Support |
|--------|-------------|-------------|
| [Amazon Q Developer CLI](https://github.com/aws/amazon-q-developer-cli) | AWS terminal coding agent | Partial |
| [AnythingLLM](https://github.com/Mintplex-Labs/anything-llm) | All-in-one desktop and Docker RAG chat app | Tools only |
| [Chatbox](https://github.com/Bin-Huang/chatbox) | Desktop and web LLM chat client | Tools only |
| [Cherry Studio](https://github.com/CherryHQ/cherry-studio) | Cross-platform desktop LLM client | Standard |
| [Claude Code](https://docs.anthropic.com/en/docs/claude-code) | Anthropic's CLI coding agent | Full |
| [Claude Desktop](https://claude.ai/download) | Anthropic's desktop app | Standard |
| [Claude Web](https://claude.ai) | Claude in the browser | Standard |
| [Cline](https://github.com/cline/cline) | Autonomous coding agent extension for VS Code | Tools + resources |
| [Continue](https://continue.dev/) | Open-source AI code assistant for VS Code and JetBrains | Standard |
| [Cursor](https://cursor.com/) | AI-powered code editor | Full |
| [Gemini CLI](https://github.com/google-gemini/gemini-cli) | Google's open-source terminal AI agent | Standard |
| [Goose](https://github.com/block/goose) | Block's extensible AI agent for desktop and CLI | Full |
| [Kilo Code](https://github.com/Kilo-Org/kilocode) | AI coding agent for VS Code, JetBrains and the CLI | Standard |
| [Langflow](https://github.com/langflow-ai/langflow) | Visual low-code builder for agents and flows | Tools only |
| [LibreChat](https://github.com/danny-avila/LibreChat) | Self-hosted multi-model chat web app | Tools only |
| [OpenAI Codex CLI](https://github.com/openai/codex) | OpenAI's terminal coding agent | Tools + resources |
| [opencode](https://github.com/sst/opencode) | Open-source terminal coding agent for any model | Standard |
| [OpenHands](https://github.com/All-Hands-AI/OpenHands) | Autonomous coding agent with a web UI | Tools only |
| [Qwen Code](https://github.com/QwenLM/qwen-code) | Alibaba's open-source terminal coding agent | Standard |
| [VS Code + Claude](https://marketplace.visualstudio.com/items?itemName=Anthropic.claude-code) | Claude Code extension for VS Code | Full |
| [Warp](https://www.warp.dev/) | AI terminal with an agent mode | Tools + resources |
| [Windsurf](https://windsurf.com) | Windsurf AI IDE (formerly Codeium) | Standard |
| [Zed](https://zed.dev/) | High-performance code editor | Partial |

## Tutorials & Articles

- [Introduction to MCP](https://modelcontextprotocol.io/introduction) - Official introduction to the protocol.
- [Building Your First MCP Server](https://modelcontextprotocol.io/quickstart/server) - Step-by-step server tutorial.
- [MCP for Claude Desktop](https://modelcontextprotocol.io/quickstart/user) - Getting started as a user.
- [Build an MCP Server (Python / Node / Java)](https://modelcontextprotocol.io/docs/develop/build-server) - Multi-language build guide.
- [MCP for Beginners](https://github.com/microsoft/mcp-for-beginners) - Microsoft open curriculum with hands-on MCP lessons and labs.
- [Writing Effective Tools for AI Agents](https://www.anthropic.com/engineering/writing-tools-for-agents) - Anthropic guide to designing effective tools for AI agents.
- [Code Execution with MCP](https://www.anthropic.com/engineering/code-execution-with-mcp) - Anthropic write-up on calling MCP tools as code to cut token usage.
- [MCP Architecture Overview](https://modelcontextprotocol.io/docs/learn/architecture) - Official docs on how MCP hosts, clients, servers and transports fit together.
- [MCP Authorization Spec](https://modelcontextprotocol.io/specification/latest/basic/authorization) - OAuth 2.1 authorization requirements for remote MCP servers.
- [MCP Security Best Practices](https://modelcontextprotocol.io/specification/latest/basic/security_best_practices) - Spec threat model and mitigations for token passthrough and confused deputy.
- [MCP Course (Hugging Face)](https://huggingface.co/learn/mcp-course) - Hugging Face course covering MCP theory, SDKs and deployment.
- [MCP Tool Poisoning Attacks](https://invariantlabs.ai/blog/mcp-security-notification-tool-poisoning-attacks) - Security write-up on hidden instructions in MCP tool descriptions.

## Videos

- [The Model Context Protocol (MCP) -- Anthropic](https://www.youtube.com/watch?v=CQywdSdi5iA) - Official overview of Model Context Protocol.
- [Build a Real-world MCP Server in One TypeScript File](https://www.youtube.com/watch?v=kXuRJXEzrE0) - Full tutorial by Nader Dabit.
- [Building Agents with MCP - Full Workshop](https://www.youtube.com/watch?v=kQmXtrmQ5Zg) - Mahesh Murag (Anthropic) full workshop on building MCP servers and agents.
- [What is MCP? Integrate AI Agents with Databases and APIs](https://www.youtube.com/watch?v=eur8dUO9mvE) - IBM Technology explainer on MCP connecting agents to databases and APIs.

## Community

- [MCP GitHub Discussions](https://github.com/modelcontextprotocol/modelcontextprotocol/discussions) - Official community discussions.
- [r/ClaudeAI](https://www.reddit.com/r/ClaudeAI/) - Reddit community with MCP discussions.
- [MCP Servers Directory](https://mcpservers.org/) - Web directory of MCP servers.
- [MCP Contributors Discord](https://discord.gg/6CSzBmMkjX) - Official Discord for MCP spec, SDK and working group discussion.
- [Glama MCP Registry](https://glama.ai/mcp/servers) - Searchable registry of open-source MCP servers.
- [Smithery](https://smithery.ai/) - Hosted MCP server registry and marketplace for agent tool connections.

---

## Contributing

**Anyone can contribute, including your own server.** There is no star requirement and no minimum project age -- if it works, is licensed and is documented, it qualifies. Read [CONTRIBUTING.md](CONTRIBUTING.md) for the details.

To add a server:

1. Fork the repo and branch off `main`.
2. Add **one** row to the most appropriate existing category, in alphabetical order.
3. Follow the format: `| [Name](URL) | Description | Language |` with the description at 80 characters or fewer.
4. Run `python scripts/validate.py` and fix what it reports.
5. Open a pull request and answer the affiliation question. Submitting your own project is welcome; not disclosing it is not.

Other ways to help, no pull request needed:

- **Report rot.** Dead link, archived upstream, project that no longer speaks MCP -- [open an issue](https://github.com/Sagargupta16/awesome-mcp-servers/issues/new/choose). Pruning is as useful as adding.
- **Fix a description.** Plenty are terser than they should be, or read like marketing.
- **Fill a gap.** Categories with few entries, and the Clients and Tutorials sections, are the thinnest parts of the list.
- **Triage the [health report](https://github.com/Sagargupta16/awesome-mcp-servers/issues?q=is%3Aissue+label%3Amaintenance).** The monthly audit files what broke; confirming or dismissing an item is a real contribution.

## License

[![CC0](https://licensebuttons.net/p/zero/1.0/88x31.png)](https://creativecommons.org/publicdomain/zero/1.0/)

This list is released under [CC0 1.0 Universal](LICENSE) - public domain.
