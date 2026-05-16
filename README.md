# Agent Search Gateway

Agent Search Gateway is a self-hostable search and web-retrieval gateway for AI agents. It gives Cursor, ChatGPT Codex, MiniMax, DeepSeek, and similar agents one stable `/search` API while the gateway handles provider routing, extraction, reranking, and fallback.

The first version is intentionally small and open-source first: SearXNG for local search, trafilatura for local content extraction, an optional Jina Reader fallback, and an optional local CrossEncoder reranker. Hosted APIs such as Tavily and Brave are compatibility or fallback providers only; they are not required for the MVP.

## What It Does

```text
Agent asks search(query)
        ↓
Agent Search Gateway
        ↓
SearXNG search
        ↓
trafilatura or optional Jina Reader extraction
        ↓
local reranker
        ↓
unified JSON back to the agent
```

Current MVP capabilities:

- Unified `GET /search` and `POST /search` API.
- Local SearXNG search backend.
- Optional Tavily search/extract provider with local daily credit guard, disabled unless explicitly configured.
- Local trafilatura article extraction.
- Optional self-hosted or hosted Jina Reader fallback.
- Optional CrossEncoder reranking, installed separately so PyTorch is not required for the base gateway.
- In-process response and extracted-content cache.
- Tavily-compatible `/tavily/search`, `/compat/tavily/search`, `/extract`, `/tavily/extract`, and `/compat/tavily/extract` adapters.
- Host-side MCP stdio server for Cursor, Codex, Claude, OpenClaw, Hermes, and other MCP clients.
- Installable `agent-search-gateway` skill for agents that support skills.
- Summary webhook placeholder for later Cursor / Codex / MiniMax / DeepSeek integration.
- Docker Compose deployment.

Not yet implemented:

- Brave provider and budget guard.
- Crawl/map/research APIs.
- Persistent shared cache.
- Production SSRF protection.

## Provider Strategy

The gateway should not depend on one search vendor. The intended provider model is:

| Provider | Role | Default status |
|---|---|---|
| SearXNG | Local fallback search | Enabled |
| trafilatura | Local extraction | Enabled |
| Jina Reader | Extraction fallback | Optional |
| Tavily | Hosted search/extract provider | Optional fallback/compatibility provider, disabled until configured |
| Brave Search | Optional paid/free-credit search provider | Planned, disabled unless explicitly configured |
| Crawl4AI | JS-heavy page extraction backend | Planned |
| CRW / OrioSearch | Alternative self-hosted backends | Planned |

Hosted providers are intentionally not enabled by default. Brave and Tavily should only be used when the operator explicitly configures an API key and a budget or quota policy. The default chain is `searxng,tavily`, so the self-hosted route is tried first.

## Local Secrets

Put real keys only in the local `.env` file. `.env` is ignored by git; `.env.example` is only a template.

Minimum local setup:

```bash
cp .env.example .env
```

If you want Tavily as an explicit hosted fallback or compatibility provider, edit `.env`:

```dotenv
TAVILY_ENABLED=true
TAVILY_API_KEY=tvly-your-real-key
TAVILY_DAILY_CREDIT_LIMIT=50
TAVILY_SEARCH_DEPTH=basic
```

`TAVILY_DAILY_CREDIT_LIMIT` is a local safety guard. Tavily's official docs currently state that basic search costs 1 credit and advanced search costs 2 credits; extract is charged per successful URL batch and depth. The gateway uses a conservative pre-request estimate so it can fall back before burning through a configured local limit.

If native MiniMax or DeepSeek summarization is added later, put those keys in the same `.env`:

```dotenv
MINIMAX_API_KEY=
DEEPSEEK_API_KEY=
```

The current summary implementation uses `SUMMARY_WEBHOOK_URL`; it does not call MiniMax or DeepSeek directly yet.

## Quick Start

```bash
cd agent-search-gateway
cp .env.example .env
SEARXNG_SECRET="$(openssl rand -hex 32)" RETRIEVAL_API_KEY="$(openssl rand -hex 32)" \
  perl -0pi -e 's/^SEARXNG_SECRET=.*/SEARXNG_SECRET=$ENV{SEARXNG_SECRET}/m; s/^RETRIEVAL_API_KEY=.*/RETRIEVAL_API_KEY=$ENV{RETRIEVAL_API_KEY}/m' .env
docker compose up -d --build
```

Health checks:

```bash
curl http://127.0.0.1:8888/search?q=searxng\&format=json | head
curl http://127.0.0.1:8010/healthz
API_KEY="$(grep '^RETRIEVAL_API_KEY=' .env | cut -d= -f2-)"
curl -sS -H "Authorization: Bearer ${API_KEY}" \
  "http://127.0.0.1:8010/search?q=local%20AI%20search&max_results=3" | jq .
```

## Prebuilt Docker Image

The retrieval API can also run from Docker Hub instead of building locally:

```bash
cd agent-search-gateway
cp .env.example .env
SEARXNG_SECRET="$(openssl rand -hex 32)" RETRIEVAL_API_KEY="$(openssl rand -hex 32)" \
  perl -0pi -e 's/^SEARXNG_SECRET=.*/SEARXNG_SECRET=$ENV{SEARXNG_SECRET}/m; s/^RETRIEVAL_API_KEY=.*/RETRIEVAL_API_KEY=$ENV{RETRIEVAL_API_KEY}/m' .env
docker compose -f docker-compose.image.yml up -d
```

Default image:

```text
docker.io/chen920/agent-search-gateway:latest
```

Users still provide their own `.env`; the image does not contain API keys or provider credentials. See [docs/DOCKER_HUB.md](docs/DOCKER_HUB.md) for publishing and image-based deployment details.

## Agent Client Integration

For Cursor, Codex, Claude, OpenClaw, Hermes, and similar agents, use the MCP server as the primary integration point. The MCP server runs on the host and calls the gateway at `http://127.0.0.1:8010`; it does not call SearXNG directly.

Install host-side MCP dependencies:

```bash
cd agent-search-gateway
pyenv install 3.12.10  # if needed
pyenv local 3.12.10
python -m venv .venv
. .venv/bin/activate
pip install -r api/requirements.txt
pip install -r integrations/mcp/requirements.txt
.venv/bin/python scripts/smoke_mcp.py
```

Generic MCP config shape:

```json
{
  "mcpServers": {
    "agent-search-gateway": {
      "command": "/absolute/path/to/agent-search-gateway/.venv/bin/python",
      "args": [
        "/absolute/path/to/agent-search-gateway/integrations/mcp/server.py"
      ],
      "env": {
        "AGENT_SEARCH_GATEWAY_URL": "http://127.0.0.1:8010",
        "AGENT_SEARCH_GATEWAY_ENV_FILE": "/absolute/path/to/agent-search-gateway/.env"
      }
    }
  }
}
```

The MCP server exposes:

- `agent_gateway_health`
- `agent_search`
- `agent_extract`

The repo also includes an optional agent skill:

```bash
mkdir -p ~/.agents/skills
cp -R skills/agent-search-gateway ~/.agents/skills/
```

See [docs/integrations/agent-clients.md](docs/integrations/agent-clients.md) for Cursor, Codex, Claude, OpenClaw, and Hermes setup steps.

Enable self-hosted Jina Reader as an extraction fallback:

```bash
cd agent-search-gateway
perl -0pi -e 's|^JINA_READER_BASE_URL=.*|JINA_READER_BASE_URL=http://jina-reader:8081|m' .env
docker compose --profile reader up -d --build
```

## API

GET:

```bash
curl -H "Authorization: Bearer ${API_KEY}" \
  "http://127.0.0.1:8010/search?q=your%20query&max_results=5&extract_top_k=3"
```

POST:

```bash
curl -sS -X POST http://127.0.0.1:8010/search \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer ${API_KEY}" \
  -d '{"query":"Tavily alternatives self hosted","max_results":5,"extract_top_k":3}' | jq .
```

Response shape:

```json
{
  "query": "string",
  "elapsed_ms": 1234,
  "provider_chain": ["searxng:searxng:8080"],
  "summary": "string",
  "results": [
    {
      "title": "string",
      "url": "https://example.com",
      "snippet": "string",
      "content": "clean extracted text",
      "score": 0.91,
      "source": "searxng:duckduckgo"
    }
  ],
  "errors": []
}
```

Fallback behavior:

1. Search tries `SEARXNG_BASE_URLS` in order.
2. Extraction tries local `trafilatura` first, then `JINA_READER_BASE_URL` if configured.
3. Reranking uses CrossEncoder when its optional dependencies are installed and `RERANKER_ENABLED=true`; otherwise it falls back to lexical matching.
4. Summary calls `SUMMARY_WEBHOOK_URL` when configured; otherwise it returns a short extractive placeholder.

With the default `PROVIDER_ORDER=searxng,tavily`, the gateway tries the self-hosted path first. Tavily is only used if you explicitly reorder providers or call a Tavily-compatible endpoint with `provider=tavily`, and it still falls back when disabled, over local quota, rate-limited, or unavailable.

Tavily-compatible adapter examples:

```bash
curl -sS -X POST http://127.0.0.1:8010/tavily/search \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer ${API_KEY}" \
  -d '{"query":"self hosted agent search gateway","max_results":5,"include_answer":true}' | jq .

curl -sS -X POST http://127.0.0.1:8010/extract \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer ${API_KEY}" \
  -d '{"urls":["https://example.com"],"extract_depth":"basic"}' | jq .
```

## Python venv Run

```bash
cd agent-search-gateway
pyenv install 3.12.10  # if it is not already installed
pyenv local 3.12.10
python -m venv .venv
. .venv/bin/activate
pip install --upgrade pip
pip install -r api/requirements.txt
cp .env.example .env
export SEARXNG_BASE_URLS=http://127.0.0.1:8888
uvicorn api.main:app --host 127.0.0.1 --port 8010 --reload
```

## Optional PyTorch Reranker

The base install intentionally does not install PyTorch. `sentence-transformers` pulls `torch`, and this can be heavy on a Mac mini. The gateway still works without it by using lexical reranking.

To enable local CrossEncoder reranking:

```bash
. .venv/bin/activate
pip install -r api/requirements-reranker.txt
```

Then edit `.env`:

```dotenv
RERANKER_ENABLED=true
RERANKER_DEVICE=mps
```

Use `RERANKER_DEVICE=cpu` if MPS is unavailable or slower for your workload. PyTorch's official macOS install guide recommends pip wheels and currently lists Python 3.10-3.14 for macOS, so this repo pins pyenv to Python 3.12.10 as a conservative dependency-compatible choice.

## Operations Notes

Single-user deployment: 2 vCPU and 4 GB RAM can run the MVP; 8 GB RAM is safer when reranking is enabled. The first reranker startup downloads the model and needs network access.

See [docs/ROADMAP.md](docs/ROADMAP.md) for the phased plan from local MVP to provider routing, persistent cache, hardening, and agent integration.

Main bottlenecks as concurrency rises:

- Upstream SearXNG engines and rate limits.
- Webpage fetch latency.
- CPU reranker inference.
- Repeated extraction of the same URLs.

Recommended next optimizations:

- Cache search results and extracted URL content.
- Limit `extract_top_k`.
- Add provider-level quota guards.
- Add SSRF protection before exposing the API beyond trusted networks.

## Security

- Bind services to `127.0.0.1` by default.
- Keep `RETRIEVAL_API_KEY` enabled for any non-local use.
- Put Caddy, Nginx, Cloudflare Tunnel, or Cloudflare Access in front of public deployments.
- Do not log API keys, cookies, full authorization headers, or sensitive query parameters.
- Do not hand hosted provider keys directly to agents; route them through this gateway with quotas and fallback.

## Troubleshooting

1. `403 Forbidden` from SearXNG: confirm `searxng/settings.yml` includes `json` under `search.formats`, then restart SearXNG.
2. `401` from the gateway: send `Authorization: Bearer ${RETRIEVAL_API_KEY}` or `X-API-Key`.
3. First search is slow: the reranker model may be downloading; set `RERANKER_ENABLED=false` to test quickly.
4. Empty content extraction: the page may block bots or require JavaScript; configure Jina Reader or add Crawl4AI later.
5. No search results: upstream engines may be rate-limited; reduce request rate or configure additional SearXNG instances.
6. Out of memory: lower `EXTRACT_TOP_K`, disable reranking, or use a smaller reranker model.

## License

No license is declared yet. Treat this repository as private/internal tooling until a license is chosen.
