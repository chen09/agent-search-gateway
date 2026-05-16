# Agent Search Gateway

Agent Search Gateway is a self-hostable search and web-retrieval gateway for AI agents. It gives Cursor, ChatGPT Codex, MiniMax, DeepSeek, and similar agents one stable `/search` API while the gateway handles provider routing, extraction, reranking, and fallback.

The first version is intentionally small: SearXNG for local search, trafilatura for local content extraction, an optional Jina Reader fallback, and a local CrossEncoder reranker. Tavily, Brave, Crawl4AI, CRW, OrioSearch, and other providers are planned as pluggable backends; they are not required for the MVP.

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
- Local trafilatura article extraction.
- Optional self-hosted or hosted Jina Reader fallback.
- Optional CrossEncoder reranking.
- Summary webhook placeholder for later Cursor / Codex / MiniMax / DeepSeek integration.
- Docker Compose deployment.

Not yet implemented:

- Tavily-compatible `/search` and `/extract` parameter compatibility.
- Tavily provider and quota guard.
- Brave provider and budget guard.
- Crawl/map/research APIs.
- MCP server.
- Persistent cache.
- Production SSRF protection.

## Provider Strategy

The gateway should not depend on one search vendor. The intended provider model is:

| Provider | Role | Default status |
|---|---|---|
| SearXNG | Local fallback search | Enabled |
| trafilatura | Local extraction | Enabled |
| Jina Reader | Extraction fallback | Optional |
| Tavily | Hosted search/extract provider | Planned |
| Brave Search | Optional paid/free-credit search provider | Planned, disabled unless explicitly configured |
| Crawl4AI | JS-heavy page extraction backend | Planned |
| CRW / OrioSearch | Alternative self-hosted backends | Planned |

Brave is intentionally not enabled by default. It should only be used when the operator explicitly configures an API key and a budget or quota policy.

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
curl http://127.0.0.1:8080/search?q=searxng\&format=json | head
curl http://127.0.0.1:8010/healthz
API_KEY="$(grep '^RETRIEVAL_API_KEY=' .env | cut -d= -f2-)"
curl -sS -H "Authorization: Bearer ${API_KEY}" \
  "http://127.0.0.1:8010/search?q=local%20AI%20search&max_results=3" | jq .
```

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
3. Reranking uses CrossEncoder when enabled; otherwise it falls back to lexical matching.
4. Summary calls `SUMMARY_WEBHOOK_URL` when configured; otherwise it returns a short extractive placeholder.

## Python venv Run

```bash
cd agent-search-gateway
python3 -m venv .venv
. .venv/bin/activate
pip install --upgrade pip
pip install -r api/requirements.txt
cp .env.example .env
export $(grep -v '^#' .env | xargs)
export SEARXNG_BASE_URLS=http://127.0.0.1:8080
uvicorn api.main:app --host 127.0.0.1 --port 8010 --reload
```

## Operations Notes

Single-user deployment: 2 vCPU and 4 GB RAM can run the MVP; 8 GB RAM is safer when reranking is enabled. The first reranker startup downloads the model and needs network access.

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
