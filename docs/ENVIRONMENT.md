# Environment Configuration

Every user must create their own local `.env` file before starting Agent Search Gateway. The repository only includes `.env.example`; real `.env` files are ignored by git and must never be committed.

## Minimum `.env` For Docker Compose

Start from the template:

```bash
cp .env.example .env
```

Generate the two required secrets:

```bash
SEARXNG_SECRET="$(openssl rand -hex 32)" RETRIEVAL_API_KEY="$(openssl rand -hex 32)" \
  perl -0pi -e 's/^SEARXNG_SECRET=.*/SEARXNG_SECRET=$ENV{SEARXNG_SECRET}/m; s/^RETRIEVAL_API_KEY=.*/RETRIEVAL_API_KEY=$ENV{RETRIEVAL_API_KEY}/m' .env
```

For the default Docker Compose stack, this is enough:

```dotenv
SEARXNG_SECRET=<generated-random-hex>
RETRIEVAL_API_KEY=<generated-random-hex>
SEARXNG_BASE_URLS=http://searxng:8080
SEARXNG_HOST_PORT=8888
PROVIDER_ORDER=searxng,tavily
TAVILY_ENABLED=false
BRAVE_ENABLED=false
RERANKER_ENABLED=false
CACHE_ENABLED=true
```

Keep `SEARXNG_BASE_URLS=http://searxng:8080` when the API runs inside Docker Compose. That is the container-internal SearXNG address.

## Minimum `.env` For Host Python Development

If you run `uvicorn` directly on the host while SearXNG is still in Docker, use the host-mapped SearXNG URL:

```dotenv
SEARXNG_SECRET=<generated-random-hex>
RETRIEVAL_API_KEY=<generated-random-hex>
SEARXNG_BASE_URLS=http://127.0.0.1:8888
SEARXNG_HOST_PORT=8888
PROVIDER_ORDER=searxng,tavily
TAVILY_ENABLED=false
BRAVE_ENABLED=false
RERANKER_ENABLED=false
CACHE_ENABLED=true
```

## Required Variables

| Variable | Required | Example | Notes |
|---|---:|---|---|
| `SEARXNG_SECRET` | Yes | `openssl rand -hex 32` | Used by SearXNG. Replace the template value. |
| `RETRIEVAL_API_KEY` | Yes | `openssl rand -hex 32` | Protects the gateway API. Agents should not see this in prompts. |
| `SEARXNG_BASE_URLS` | Yes | `http://searxng:8080` | Use Docker internal URL in Compose; use `http://127.0.0.1:8888` for host Python. |
| `SEARXNG_HOST_PORT` | No | `8888` | Host port for SearXNG UI/API. |

## Open-Source-First Defaults

These defaults keep the gateway self-hosted first:

```dotenv
PROVIDER_ORDER=searxng,tavily
TAVILY_ENABLED=false
BRAVE_ENABLED=false
RERANKER_ENABLED=false
```

With this configuration, the gateway searches through SearXNG and local extraction. Tavily is listed in the provider order only so it can be enabled later without changing API clients; it is skipped while `TAVILY_ENABLED=false`.

## Optional Hosted Provider Keys

Only add hosted provider keys when you explicitly want that provider and have a quota policy.

Tavily fallback:

```dotenv
TAVILY_ENABLED=true
TAVILY_API_KEY=<your-tavily-key>
TAVILY_DAILY_CREDIT_LIMIT=50
TAVILY_SEARCH_DEPTH=basic
```

Brave is reserved for future provider support. Keep it disabled for now:

```dotenv
BRAVE_ENABLED=false
BRAVE_API_KEY=
BRAVE_DAILY_CREDIT_LIMIT=0
```

Future native summarization keys can live in `.env`, but the current gateway does not call these providers directly:

```dotenv
MINIMAX_API_KEY=
DEEPSEEK_API_KEY=
```

## Optional Extraction Fallback

For self-hosted Jina Reader through the compose `reader` profile:

```dotenv
JINA_READER_BASE_URL=http://jina-reader:8081
```

For hosted Jina Reader:

```dotenv
JINA_READER_BASE_URL=https://r.jina.ai
JINA_API_KEY=<your-jina-key>
```

Leave both empty if you only want local `trafilatura` extraction.

## Optional Reranker

The base install does not include PyTorch. Keep this disabled unless you install `api/requirements-reranker.txt`:

```dotenv
RERANKER_ENABLED=false
RERANKER_MODEL=cross-encoder/ms-marco-MiniLM-L6-v2
RERANKER_DEVICE=cpu
```

On Apple Silicon, use `RERANKER_DEVICE=mps` only after confirming your local PyTorch install supports MPS for your workload.

## MCP Client Environment

MCP clients run the MCP server as a local process. Prefer a private env file or pointing the MCP server at the repo `.env`.

For a local Docker Compose gateway:

```text
AGENT_SEARCH_GATEWAY_URL=http://127.0.0.1:8010
AGENT_SEARCH_GATEWAY_ENV_FILE=/absolute/path/to/agent-search-gateway/.env
```

For a remote gateway:

```text
AGENT_SEARCH_GATEWAY_URL=https://api.agentsearchgateway.com
AGENT_SEARCH_GATEWAY_API_KEY=<your-gateway-api-key>
AGENT_SEARCH_GATEWAY_TIMEOUT=90
```

If your MCP client config is private and never committed or synced, the same values can be written directly into the client's MCP `env` block.

These are MCP process environment variables, not values that normally need to be written into the gateway `.env`.

## Do Not Commit

Never commit these files or values:

- `.env`
- `.env.bak-*`
- API keys
- Docker Hub tokens
- logs
- extracted content caches
