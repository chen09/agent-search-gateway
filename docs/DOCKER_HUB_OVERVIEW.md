# Agent Search Gateway

Self-hosted search and extraction gateway for AI agents. This image runs the `retrieval-api` service. Use the provided Docker Compose file to run it together with SearXNG and Valkey.

Source and full documentation:

- GitHub: https://github.com/chen09/agent-search-gateway
- Environment guide: https://github.com/chen09/agent-search-gateway/blob/main/docs/ENVIRONMENT.md
- Agent client setup: https://github.com/chen09/agent-search-gateway/blob/main/docs/integrations/agent-clients.md

## Image Tags

```text
docker.io/chen920/agent-search-gateway:latest
docker.io/chen920/agent-search-gateway:0.2
docker.io/chen920/agent-search-gateway:0.2.1
```

Multi-architecture images are published for:

- `linux/amd64`
- `linux/arm64`

## Quick Start

Clone the repo so you also get the SearXNG config and Compose files:

```bash
git clone https://github.com/chen09/agent-search-gateway.git
cd agent-search-gateway
cp .env.example .env
```

Generate the two required local secrets:

```bash
SEARXNG_SECRET="$(openssl rand -hex 32)" RETRIEVAL_API_KEY="$(openssl rand -hex 32)" \
  perl -0pi -e 's/^SEARXNG_SECRET=.*/SEARXNG_SECRET=$ENV{SEARXNG_SECRET}/m; s/^RETRIEVAL_API_KEY=.*/RETRIEVAL_API_KEY=$ENV{RETRIEVAL_API_KEY}/m' .env
```

Start the stack with the prebuilt Docker Hub image:

```bash
docker compose -f docker-compose.image.yml up -d
```

Verify:

```bash
curl http://127.0.0.1:8010/healthz
curl 'http://127.0.0.1:8888/search?q=searxng&format=json' | head
```

## Required `.env`

Users must create `.env` before running Compose because the stack loads it with `env_file`.

The only values that must be unique per install are:

```dotenv
SEARXNG_SECRET=<generated-random-hex>
RETRIEVAL_API_KEY=<generated-random-hex>
```

Keep these defaults for Docker Compose:

```dotenv
SEARXNG_BASE_URLS=http://searxng:8080
SEARXNG_HOST_PORT=8888
PROVIDER_ORDER=searxng,tavily
TAVILY_ENABLED=false
BRAVE_ENABLED=false
RERANKER_ENABLED=false
CACHE_ENABLED=true
```

If a user only runs `cp .env.example .env`, the stack may start, but it uses public placeholder secrets. That is acceptable only for a quick local test. Generate real secrets before using the gateway long term or exposing it beyond localhost.

Hosted provider keys are optional. Tavily, Brave, MiniMax, and DeepSeek are not required for the default route. The default route is SearXNG plus local extraction.

## API

Gateway:

```text
http://127.0.0.1:8010
```

SearXNG:

```text
http://127.0.0.1:8888
```

Search example:

```bash
API_KEY="$(grep '^RETRIEVAL_API_KEY=' .env | cut -d= -f2-)"
curl -sS -H "Authorization: Bearer ${API_KEY}" \
  "http://127.0.0.1:8010/search?q=self%20hosted%20agent%20search&max_results=3"
```

## Agent Clients

Cursor, Codex, Claude, OpenClaw, Hermes, and other MCP-capable agents should use the MCP server from the GitHub repo:

```text
Command: /absolute/path/to/agent-search-gateway/.venv/bin/python
Args: /absolute/path/to/agent-search-gateway/integrations/mcp/server.py
Env:
  AGENT_SEARCH_GATEWAY_URL=http://127.0.0.1:8010
  AGENT_SEARCH_GATEWAY_ENV_FILE=/absolute/path/to/agent-search-gateway/.env
```

MCP tools:

- `agent_gateway_health`
- `agent_search`
- `agent_extract`

## Secret Policy

The image does not contain `.env`, API keys, provider keys, logs, extracted content, or caches.

Do not commit:

- `.env`
- `.env.bak-*`
- Docker Hub tokens
- hosted provider API keys

## License

No license is declared yet. Review the repository before redistribution or production use.
