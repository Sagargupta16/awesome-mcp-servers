# Awesome MCP Servers [![Awesome](https://awesome.re/badge.svg)](https://awesome.re)

> A curated list of [Model Context Protocol (MCP)](https://modelcontextprotocol.io/) servers, tools, frameworks, and resources.

MCP is an open protocol that lets AI assistants (Claude, GPT, Cursor, Windsurf, etc.) connect to local and remote data sources through standardized server implementations. This list favors **vendor-maintained** and **actively-developed** servers over abandoned forks.

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
- [MCP TypeScript SDK](https://github.com/modelcontextprotocol/typescript-sdk) - Official TypeScript/Node.js SDK.
- [MCP Python SDK](https://github.com/modelcontextprotocol/python-sdk) - Official Python SDK.
- [MCP Servers (Reference)](https://github.com/modelcontextprotocol/servers) - Official reference server implementations (everything, fetch, filesystem, git, memory, sequentialthinking, time).
- [MCP Inspector](https://github.com/modelcontextprotocol/inspector) - Visual testing tool for MCP servers.
- [MCP Registry](https://github.com/modelcontextprotocol/registry) - Official community-driven registry for MCP servers.

## Servers

### Data & Databases

| Server | Description | Language |
|--------|-------------|----------|
| [PostgreSQL MCP (Pro)](https://github.com/crystaldba/postgres-mcp) | Query, analyze and optimize PostgreSQL databases | Python |
| [MongoDB MCP](https://github.com/mongodb-js/mongodb-mcp-server) | Official MongoDB and Atlas cluster management | TypeScript |
| [Redis MCP](https://github.com/redis/mcp-redis) | Official Redis cache and data structures | Python |
| [MySQL MCP](https://github.com/benborla/mcp-server-mysql) | MySQL database queries and management | TypeScript |
| [Supabase MCP](https://github.com/supabase-community/supabase-mcp) | Supabase database, auth, and storage | TypeScript |
| [Neon MCP](https://github.com/neondatabase/mcp-server-neon) | Neon serverless Postgres branching and management | TypeScript |
| [Upstash MCP](https://github.com/upstash/mcp-server) | Upstash Redis and Vector databases | TypeScript |
| [SQL Database MCP](https://github.com/executeautomation/mcp-database-server) | SQLite, Postgres and SQL Server unified server | TypeScript |
| [ClickHouse MCP](https://github.com/ClickHouse/mcp-clickhouse) | Official ClickHouse columnar analytics | Python |
| [MotherDuck / DuckDB MCP](https://github.com/motherduckdb/mcp-server-motherduck) | Local DuckDB and MotherDuck cloud access | Python |
| [BigQuery MCP](https://github.com/ergut/mcp-bigquery-server) | Query Google BigQuery datasets and tables | TypeScript |
| [Snowflake MCP](https://github.com/Snowflake-Labs/mcp) | Official Snowflake Cortex AI + SQL orchestration | Python |
| [Elasticsearch MCP](https://github.com/elastic/mcp-server-elasticsearch) | Official Elasticsearch query interface | Rust |
| [Qdrant MCP](https://github.com/qdrant/mcp-server-qdrant) | Official Qdrant vector database server | Python |
| [Chroma MCP](https://github.com/chroma-core/chroma-mcp) | Official Chroma vector DB for RAG workflows | Python |
| [Pinecone MCP](https://github.com/pinecone-io/pinecone-mcp) | Official Pinecone vector database | TypeScript |
| [Weaviate MCP](https://github.com/weaviate/mcp-server-weaviate) | Official Weaviate vector database | Go |
| [GCP MCP Toolbox](https://github.com/googleapis/mcp-toolbox) | Official Google DB toolbox (Postgres, MySQL, Spanner) | Go |
| [dbt MCP](https://github.com/dbt-labs/dbt-mcp) | Official dbt Labs server for dbt projects | Python |
| [Airflow MCP](https://github.com/yangkyeongmo/mcp-server-apache-airflow) | Apache Airflow DAG management and runs | Python |
| [Wikipedia MCP](https://github.com/timjuenemann/wikipedia-mcp) | Wikipedia article search and retrieval | TypeScript |

### Developer Tools

| Server | Description | Language |
|--------|-------------|----------|
| [GitHub MCP](https://github.com/github/github-mcp-server) | Official GitHub — repos, issues, PRs, Actions | Go |
| [GitLab MCP](https://github.com/zereight/gitlab-mcp) | GitLab API integration (repos, MRs, issues) | TypeScript |
| [Atlassian MCP (Jira + Confluence)](https://github.com/sooperset/mcp-atlassian) | Jira and Confluence integration | Python |
| [Bitbucket MCP](https://github.com/aashari/mcp-server-atlassian-bitbucket) | Bitbucket Cloud repos, PRs, pipelines | TypeScript |
| [Linear MCP](https://github.com/jerhadf/linear-mcp-server) | Linear project management | TypeScript |
| [Sentry MCP](https://github.com/getsentry/sentry-mcp) | Official Sentry error and performance tracking | TypeScript |
| [Docker MCP](https://github.com/ckreiling/mcp-server-docker) | Docker container management | Python |
| [Kubernetes MCP](https://github.com/strowk/mcp-k8s-go) | Kubernetes cluster operations | Go |
| [kubectl MCP](https://github.com/rohitg00/kubectl-mcp-server) | Natural-language kubectl operations (CNCF listed) | Python |
| [Playwright MCP](https://github.com/microsoft/playwright-mcp) | Browser automation and testing | TypeScript |
| [Figma Context MCP](https://github.com/GLips/Figma-Context-MCP) | Figma design file access for coding agents | TypeScript |
| [Postman MCP](https://github.com/postmanlabs/postman-mcp-server) | Official Postman API collections server | TypeScript |
| [CircleCI MCP](https://github.com/CircleCI-Public/mcp-server-circleci) | Official CircleCI workflow integration | TypeScript |
| [Jupyter MCP](https://github.com/datalayer/jupyter-mcp-server) | Jupyter notebook cell execution | Python |
| [toprank](https://github.com/nowork-studio/toprank) | SEO & Google Ads skills for Claude Code | TypeScript |

### Cloud & Infrastructure

| Server | Description | Language |
|--------|-------------|----------|
| [AWS MCP Servers](https://github.com/awslabs/mcp) | Official AWS MCP servers (S3, Lambda, CDK, Bedrock, etc.) | Multiple |
| [Cloudflare MCP](https://github.com/cloudflare/mcp-server-cloudflare) | Cloudflare Workers, KV, R2, D1 | TypeScript |
| [Google Cloud MCP](https://github.com/googleapis/gcloud-mcp) | Official gcloud CLI wrapper for GCP services | TypeScript |
| [Azure MCP](https://github.com/Azure/azure-mcp) | Official Azure cloud services | Python |
| [Terraform MCP](https://github.com/hashicorp/terraform-mcp-server) | Official HashiCorp Terraform / OpenTofu | Go |
| [Vercel MCP Handler](https://github.com/vercel/mcp-handler) | Official Vercel MCP handler for Next.js / Nuxt / Svelte | TypeScript |
| [Vercel Next DevTools MCP](https://github.com/vercel/next-devtools-mcp) | Official Next.js dev tools for coding agents | TypeScript |
| [Railway MCP](https://github.com/railwayapp/railway-mcp-server) | Official Railway deployment platform | TypeScript |
| [Render MCP](https://github.com/render-oss/render-mcp-server) | Official Render deployment server | Go |
| [DigitalOcean MCP](https://github.com/digitalocean-labs/mcp-digitalocean) | Official DO droplets, apps, databases | Go |
| [Heroku MCP](https://github.com/heroku/heroku-mcp-server) | Official Heroku platform CLI wrapper | TypeScript |
| [Helm MCP](https://github.com/zekker6/mcp-helm) | Helm package manager for Kubernetes | Go |
| [Nomad MCP](https://github.com/kocierik/mcp-nomad) | HashiCorp Nomad cluster operations | Go |

### Productivity

| Server | Description | Language |
|--------|-------------|----------|
| [Google Drive MCP](https://github.com/felores/gdrive-mcp-server) | Google Drive file access and search | TypeScript |
| [Slack MCP](https://github.com/korotovsky/slack-mcp-server) | Slack workspace integration | TypeScript |
| [Notion MCP](https://github.com/makenotion/notion-mcp-server) | Official Notion API integration | TypeScript |
| [Google Calendar MCP](https://github.com/nspady/google-calendar-mcp) | Google Calendar management | TypeScript |
| [Gmail MCP](https://github.com/GongRzhe/Gmail-MCP-Server) | Gmail read/send with OAuth auto-auth | JavaScript |
| [Outlook MCP](https://github.com/ryaker/outlook-mcp) | Outlook email and calendar via MS Graph | JavaScript |
| [Microsoft 365 MCP](https://github.com/Softeria/ms-365-mcp-server) | Full M365 suite (Outlook, OneDrive, Teams, Excel) | TypeScript |
| [Todoist MCP](https://github.com/abhiz123/todoist-mcp-server) | Todoist task management | TypeScript |
| [Airtable MCP](https://github.com/domdomegg/airtable-mcp-server) | Airtable base read/write | TypeScript |
| [Asana MCP](https://github.com/roychri/mcp-server-asana) | Asana tasks, projects, workspaces | TypeScript |
| [Trello MCP](https://github.com/delorenj/mcp-server-trello) | Trello boards, lists, cards | TypeScript |
| [Coda MCP](https://github.com/orellazri/coda-mcp) | Coda documents and tables | TypeScript |
| [Apple MCP](https://github.com/supermemoryai/apple-mcp) | Apple Notes, Reminders, Calendar, Contacts, Maps | TypeScript |

### Search & Knowledge

| Server | Description | Language |
|--------|-------------|----------|
| [Brave Search MCP](https://github.com/brave/brave-search-mcp-server) | Official Brave Search API | TypeScript |
| [Exa MCP](https://github.com/exa-labs/exa-mcp-server) | Exa AI-powered search | TypeScript |
| [Tavily MCP](https://github.com/tavily-ai/tavily-mcp) | Tavily AI search for agents | Python |
| [Perplexity MCP](https://github.com/perplexityai/modelcontextprotocol) | Official Perplexity search API | TypeScript |
| [DuckDuckGo MCP](https://github.com/nickclyde/duckduckgo-mcp-server) | DuckDuckGo search with content fetching | Python |
| [Kagi MCP](https://github.com/kagisearch/kagimcp) | Official Kagi search API | Python |
| [SerpAPI MCP](https://github.com/serpapi/serpapi-mcp) | Official SerpAPI Google search results | Python |
| [Algolia MCP](https://github.com/algolia/mcp-node) | Official Algolia search index management | TypeScript |
| [Meilisearch MCP](https://github.com/meilisearch/meilisearch-mcp) | Official Meilisearch index server | Python |
| [Context7 MCP](https://github.com/upstash/context7) | Up-to-date library documentation | TypeScript |
| [DeepWiki MCP](https://github.com/regenrek/deepwiki-mcp) | Fetch deepwiki.com repo docs as markdown | TypeScript |
| [Firecrawl MCP](https://github.com/firecrawl/firecrawl-mcp-server) | Web scraping and crawling | TypeScript |
| [Apify MCP](https://github.com/apify/apify-mcp-server) | Web scraping actors and automation | TypeScript |

### Communication

| Server | Description | Language |
|--------|-------------|----------|
| [Discord MCP](https://github.com/v-3/discordmcp) | Discord bot and channel management | Python |
| [Telegram MCP](https://github.com/chigwell/telegram-mcp) | Telegram messaging | Python |
| [WhatsApp MCP](https://github.com/lharries/whatsapp-mcp) | WhatsApp messaging via web client | Python |
| [Microsoft Teams MCP](https://github.com/InditexTech/mcp-teams-server) | Teams channels, messages, meetings | Python |
| [Matrix MCP](https://github.com/mjknowles/matrix-mcp-server) | Matrix chat protocol server | TypeScript |
| [Resend MCP](https://github.com/resend/resend-mcp) | Official Resend transactional email | TypeScript |

### File Systems & Storage

| Server | Description | Language |
|--------|-------------|----------|
| [Filesystem MCP](https://github.com/modelcontextprotocol/servers/tree/main/src/filesystem) | Local filesystem operations | TypeScript |
| [S3 Tables MCP](https://github.com/awslabs/mcp/tree/main/src/s3-tables-mcp-server) | Official AWS S3 Tables | Python |
| [PDF MCP](https://github.com/Sohaib-2/pdf-mcp-server) | Extract text and metadata from PDF files | TypeScript |
| [Box MCP](https://github.com/box-community/mcp-server-box) | Box file storage and metadata | Python |
| [Dropbox Dash MCP](https://github.com/dropbox/mcp-server-dash) | Official Dropbox Dash search server | Python |
| [OneDrive / SharePoint MCP](https://github.com/ftaricano/mcp-onedrive-sharepoint) | OneDrive and SharePoint document access | TypeScript |
| [IPFS MCP](https://github.com/alexbakers/mcp-ipfs) | IPFS pin, get, publish operations | TypeScript |

### AI & ML

| Server | Description | Language |
|--------|-------------|----------|
| [HuggingFace MCP](https://github.com/huggingface/hf-mcp-server) | Official HF Hub models, datasets, Spaces | TypeScript |
| [OpenAI MCP](https://github.com/pierrebrunelle/mcp-server-openai) | OpenAI API access | Python |
| [Ollama MCP](https://github.com/patruff/ollama-mcp-bridge) | Local Ollama model management | TypeScript |
| [LangChain MCP Adapters](https://github.com/langchain-ai/langchain-mcp-adapters) | Official LangChain / LangGraph MCP bridge | Python |
| [LlamaCloud MCP](https://github.com/run-llama/llamacloud-mcp) | Official LlamaIndex Cloud index query | Python |
| [Replicate MCP](https://github.com/deepfates/mcp-replicate) | Run Replicate-hosted models | TypeScript |
| [Weights & Biases MCP](https://github.com/wandb/wandb-mcp-server) | Official W&B Models + Weave | Python |
| [prompt-to-asset](https://github.com/MohamedAbdallah-14/prompt-to-asset) | Image generation across 30+ models via unified API | JavaScript |

### Finance

| Server | Description | Language |
|--------|-------------|----------|
| [Stripe MCP](https://github.com/stripe/agent-toolkit) | Stripe payments and billing | TypeScript |
| [Coinbase MCP](https://github.com/coinbase/agentkit) | Coinbase crypto trading and wallet | TypeScript |
| [Yahoo Finance MCP](https://github.com/Alex2Yang97/yahoo-finance-mcp) | Stock data and financial info | Python |
| [Financial Datasets MCP](https://github.com/financial-datasets/mcp-server) | Stock financials, prices, insider trades | Python |
| [Financial Modeling Prep MCP](https://github.com/imbenrabi/Financial-Modeling-Prep-MCP-Server) | FMP market data and fundamentals | TypeScript |
| [Alpaca MCP](https://github.com/alpacahq/alpaca-mcp-server) | Official Alpaca stocks / ETF / crypto trading | Python |
| [QuickBooks MCP](https://github.com/intuit/quickbooks-online-mcp-server) | Official Intuit QuickBooks Online | TypeScript |
| [Square MCP](https://github.com/square/square-mcp-server) | Official Square payments and commerce | TypeScript |
| [Ramp MCP](https://github.com/ramp-public/ramp_mcp) | Official Ramp corporate cards + expenses | Python |

### Monitoring & Observability

| Server | Description | Language |
|--------|-------------|----------|
| [Datadog MCP](https://github.com/winor30/mcp-server-datadog) | Datadog metrics, logs, monitors | TypeScript |
| [Grafana MCP](https://github.com/grafana/mcp-grafana) | Official Grafana dashboards and alerts | Go |
| [Loki MCP](https://github.com/grafana/loki-mcp) | Official Grafana Loki log aggregation | Go |
| [PagerDuty MCP](https://github.com/PagerDuty/pagerduty-mcp-server) | Official PagerDuty incident management | TypeScript |
| [Prometheus MCP](https://github.com/pab1it0/prometheus-mcp-server) | Prometheus metrics and PromQL queries | Python |
| [OpenTelemetry MCP](https://github.com/traceloop/opentelemetry-mcp-server) | Unified OTEL traces across backends | Python |
| [Logfire MCP](https://github.com/pydantic/logfire-mcp) | Official Pydantic Logfire observability | Python |
| [Honeycomb MCP](https://github.com/honeycombio/honeycomb-mcp) | Official Honeycomb trace queries | TypeScript |

### Design & Creative

| Server | Description | Language |
|--------|-------------|----------|
| [Figma Dev Guide (official)](https://github.com/figma/mcp-server-guide) | Official Figma MCP usage guide and reference | JavaScript |
| [Figma Context MCP](https://github.com/GLips/Figma-Context-MCP) | Figma layouts for AI coding agents (Framelink) | TypeScript |
| [Blender MCP](https://github.com/ahujasid/blender-mcp) | Control Blender 3D modeling from AI assistants | Python |
| [Photoshop MCP](https://github.com/loonghao/photoshop-python-api-mcp-server) | Adobe Photoshop automation | Python |
| [Framer Plugin MCP](https://github.com/Sheshiyer/framer-plugin-mcp) | Create and manage Framer plugins | JavaScript |

### Testing & QA

| Server | Description | Language |
|--------|-------------|----------|
| [Playwright MCP](https://github.com/microsoft/playwright-mcp) | Official Microsoft Playwright browser automation | TypeScript |
| [a11y MCP](https://github.com/ronantakizawa/a11ymcp) | Web accessibility / WCAG automated testing | JavaScript |
| [Axe MCP](https://github.com/dequelabs/axe-mcp-server-public) | Official Deque accessibility testing + AI remediation | TypeScript |
| [Vibetest (browser-use)](https://github.com/browser-use/vibetest-use) | Automated QA using Browser-Use agents | Python |
| [Web Eval Agent](https://github.com/refreshdotdev/web-eval-agent) | Autonomously evaluates web applications | Python |

### Security

| Server | Description | Language |
|--------|-------------|----------|
| [Bitwarden MCP](https://github.com/bitwarden/mcp-server) | Official Bitwarden password manager | TypeScript |
| [Semgrep MCP](https://github.com/semgrep/mcp) | Official Semgrep static analysis for vulnerabilities | Python |
| [Burp AI Agent](https://github.com/six2dez/burp-ai-agent) | Burp Suite extension with MCP tooling | Kotlin |
| [BurpMCP](https://github.com/swgee/BurpMCP) | Burp Suite MCP server for app security testing | Java |
| [MCP Security Hub](https://github.com/FuzzingLabs/mcp-security-hub) | Offensive tools (Nmap, Ghidra, Nuclei) | Python |
| [MCP for Security](https://github.com/cyproxio/mcp-for-security) | SQLMap, FFUF, Nmap, Masscan via MCP | TypeScript |

### Web Browsing & Scraping

| Server | Description | Language |
|--------|-------------|----------|
| [Browserbase MCP](https://github.com/browserbase/mcp-server-browserbase) | Cloud browser automation via Stagehand | TypeScript |
| [Firecrawl MCP](https://github.com/firecrawl/firecrawl-mcp-server) | Official Firecrawl web scraping and search | TypeScript |
| [Puppeteer MCP](https://github.com/merajmehrabi/puppeteer-mcp-server) | Browser automation via Puppeteer | TypeScript |
| [Browser Use MCP](https://github.com/Saik0s/mcp-browser-use) | browser-use agent wrapped as MCP server | Python |
| [Fetcher MCP](https://github.com/jae-jae/fetcher-mcp) | Headless Playwright page fetcher | TypeScript |

### Media & Entertainment

| Server | Description | Language |
|--------|-------------|----------|
| [Spotify MCP](https://github.com/marcelmarais/spotify-mcp-server) | Lightweight Spotify integration | TypeScript |
| [YouTube MCP](https://github.com/ZubeidHendricks/youtube-mcp-server) | YouTube API videos and analytics | TypeScript |
| [YouTube Transcript MCP](https://github.com/kimtaeyoon83/mcp-server-youtube-transcript) | Download YouTube video transcripts | TypeScript |
| [Plex MCP](https://github.com/vladimir-tutin/plex-mcp-server) | Converse with a Plex media server | Python |
| [TMDB MCP](https://github.com/Laksh-star/mcp-server-tmdb) | The Movie Database (TMDB) | TypeScript |
| [Twitch MCP](https://github.com/TomCools/twitch-mcp) | Connect MCP clients to Twitch Chat | TypeScript |

### Travel & Location

| Server | Description | Language |
|--------|-------------|----------|
| [Google Maps MCP](https://github.com/cablate/mcp-google-map) | Google Maps API with LLM processing | TypeScript |
| [OpenStreetMap MCP](https://github.com/jagan-shanmugam/open-streetmap-mcp) | Location services and geospatial data | Python |
| [Airbnb MCP](https://github.com/openbnb-org/mcp-server-airbnb) | Search Airbnb from your AI agent | JavaScript |
| [Weather MCP](https://github.com/ezh0v/weather-mcp-server) | Real-time weather data | Go |
| [Flights MCP](https://github.com/ravinahp/flights-mcp) | Flight search via Duffel API | Python |
| [Flight Search MCP](https://github.com/arjunprabhulal/mcp-flight-search) | Realtime flight search server | Python |

### E-commerce

| Server | Description | Language |
|--------|-------------|----------|
| [Shopify MCP](https://github.com/GeLi2001/shopify-mcp) | Shopify API integration | TypeScript |
| [WooCommerce MCP](https://github.com/techspawn/woocommerce-mcp-server) | WooCommerce MCP server | JavaScript |
| [eBay MCP](https://github.com/YosefHayim/ebay-mcp) | 325 tools for eBay Sell APIs | TypeScript |
| [Amazon MCP](https://github.com/rigwild/mcp-server-amazon) | Search and purchase Amazon products | TypeScript |

### Game Development

| Server | Description | Language |
|--------|-------------|----------|
| [Godot MCP](https://github.com/Coding-Solo/godot-mcp) | Godot game engine integration | JavaScript |
| [Unreal MCP](https://github.com/ChiR24/Unreal_mcp) | Unreal Engine C++ Automation Bridge | C++ |
| [UnrealGenAISupport](https://github.com/prajwalshettydev/UnrealGenAISupport) | UE5 plugin for LLM/GenAI + MCP | C++ |
| [Unity Natural MCP](https://github.com/notargs/UnityNaturalMCP) | Natural UX Unity MCP implementation | C# |
| [Unity MCP Server](https://github.com/AnkleBreaker-Studio/unity-mcp-server) | 268 tools for Unity Editor / Hub | JavaScript |
| [Roblox Studio MCP](https://github.com/Roblox/studio-rust-mcp-server) | Official Roblox Studio standalone MCP | Rust |

### IoT & Home Automation

| Server | Description | Language |
|--------|-------------|----------|
| [Home Assistant MCP (ha-mcp)](https://github.com/homeassistant-ai/ha-mcp) | The unofficial awesome Home Assistant MCP | Python |
| [Home Assistant MCP](https://github.com/tevonsb/homeassistant-mcp) | Alternative Home Assistant MCP | TypeScript |
| [Hass MCP](https://github.com/voska/hass-mcp) | Minimal Home Assistant MCP | Python |
| [MQTT MCP](https://github.com/ezhuk/mqtt-mcp) | Generic MQTT broker interaction | Python |
| [EMQX MCP](https://github.com/Benniu/emqx-mcp-server) | EMQX MQTT broker | Python |
| [Philips Hue MCP](https://github.com/ykhli/mcp-light-control) | Control Philips Hue lights | TypeScript |

### Marketing & Analytics

| Server | Description | Language |
|--------|-------------|----------|
| [Salesforce MCP](https://github.com/salesforcecli/mcp) | Official Salesforce CLI MCP | TypeScript |
| [Google Analytics MCP](https://github.com/surendranb/google-analytics-mcp) | GA4 data for AI agents | Python |
| [HubSpot MCP](https://github.com/baryhuang/mcp-hubspot) | HubSpot CRM with vector storage | Python |
| [PostHog MCP](https://github.com/PostHog/mcp) | Official PostHog product analytics | TypeScript |
| [Mixpanel MCP](https://github.com/dragonkhoi/mixpanel-mcp) | Talk to your Mixpanel data | TypeScript |

### Knowledge Management

| Server | Description | Language |
|--------|-------------|----------|
| [Obsidian MCP](https://github.com/MarkusPfundstein/mcp-obsidian) | Obsidian via REST API community plugin | Python |
| [Obsidian MCP (alt)](https://github.com/StevenStavrakis/obsidian-mcp) | Simple MCP server for Obsidian | TypeScript |
| [Logseq MCP](https://github.com/ergut/mcp-logseq) | Read / write / manage LogSeq graph | Python |
| [Anki MCP](https://github.com/ankimcp/anki-mcp-server) | Anki flashcards via AnkiConnect | TypeScript |
| [Readwise Skills](https://github.com/readwiseio/readwise-skills) | Official Readwise agent skills + MCP | Python |

## Frameworks & Libraries

| Project | Description | Language |
|---------|-------------|----------|
| [MCP TypeScript SDK](https://github.com/modelcontextprotocol/typescript-sdk) | Official TypeScript SDK for servers and clients | TypeScript |
| [MCP Python SDK](https://github.com/modelcontextprotocol/python-sdk) | Official Python SDK for servers and clients | Python |
| [FastMCP](https://github.com/jlowin/fastmcp) | Fast, Pythonic way to build MCP servers | Python |
| [mcp-framework](https://github.com/QuantGeekDev/mcp-framework) | TypeScript framework for building MCP servers | TypeScript |
| [easymcp (promptmesh)](https://github.com/promptmesh/easymcp) | Simplified Python MCP client SDK | Python |
| [spring-ai-mcp](https://github.com/spring-projects-experimental/spring-ai-mcp) | Spring Boot MCP integration | Java |
| [21st Magic MCP](https://github.com/21st-dev/magic-mcp) | AI component builder for React | TypeScript |
| [Vercel mcp-handler](https://github.com/vercel/mcp-handler) | Official Vercel MCP adapter for meta-frameworks | TypeScript |
| [MCP Registry](https://github.com/modelcontextprotocol/registry) | Official community-driven MCP server registry | TypeScript |

## Clients

| Client | Description | MCP Support |
|--------|-------------|-------------|
| [Claude Desktop](https://claude.ai/download) | Anthropic's desktop app | Full |
| [Claude Code](https://docs.anthropic.com/en/docs/claude-code) | Anthropic's CLI coding agent | Full |
| [VS Code + Claude](https://marketplace.visualstudio.com/items?itemName=Anthropic.claude-code) | VS Code extension | Full |
| [Cursor](https://cursor.com/) | AI-powered code editor | Full |
| [Windsurf](https://codeium.com/windsurf) | Codeium's AI IDE | Full |
| [Zed](https://zed.dev/) | High-performance code editor | Partial |
| [Continue](https://continue.dev/) | Open-source AI code assistant | Full |
| [Claude Mobile](https://claude.ai/download) | Claude on iOS / Android | Full |
| [Claude Web](https://claude.ai) | Claude in the browser | Full |

## Tutorials & Articles

- [Introduction to MCP](https://modelcontextprotocol.io/introduction) - Official introduction to the protocol.
- [Building Your First MCP Server](https://modelcontextprotocol.io/quickstart/server) - Step-by-step server tutorial.
- [MCP for Claude Desktop](https://modelcontextprotocol.io/quickstart/user) - Getting started as a user.
- [Build an MCP Server (Python / Node / Java)](https://modelcontextprotocol.io/docs/develop/build-server) - Multi-language build guide.

## Videos

- [The Model Context Protocol (MCP) — Anthropic](https://www.youtube.com/watch?v=CQywdSdi5iA) - Official overview of Model Context Protocol.
- [Build a Real-world MCP Server in One TypeScript File](https://www.youtube.com/watch?v=kXuRJXEzrE0) - Full tutorial by Nader Dabit.

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
4. Prefer official / vendor-maintained servers over community forks
5. Submit a PR

## License

[![CC0](https://licensebuttons.net/p/zero/1.0/88x31.png)](https://creativecommons.org/publicdomain/zero/1.0/)

This list is released under [CC0 1.0 Universal](LICENSE) - public domain.
