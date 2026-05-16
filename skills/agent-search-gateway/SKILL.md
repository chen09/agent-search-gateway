---
name: agent-search-gateway
description: Use this skill whenever an agent needs current web search, source discovery, or URL extraction through a self-hosted Agent Search Gateway. Prefer the MCP tools agent_search and agent_extract when available; otherwise use the HTTP API fallback. This skill is for Cursor, Codex, Claude, OpenClaw, Hermes, and similar coding or research agents that should use a controlled local search gateway instead of ad hoc hosted search APIs.
---

# Agent Search Gateway

Use Agent Search Gateway when a task needs current external information, source discovery, article extraction, or repeatable research results. It gives the agent one controlled local retrieval endpoint backed by SearXNG and local extraction.

Do not use it for purely local code reading, editing, or stable background knowledge.

## Preferred Tool Path

If MCP tools are available, use them in this order:

1. `agent_gateway_health` to confirm the gateway is reachable.
2. `agent_search` for web search.
3. `agent_extract` when the user provides URLs or when search results need deeper page text.

Default search parameters:

- `max_results`: 5 unless the user asks for more.
- `extract_top_k`: 3 for research, 0 for quick link discovery.
- `include_summary`: true unless the caller only needs URLs.
- `provider`: `auto` unless the user explicitly asks to test a provider.

## HTTP Fallback

If MCP tools are not available but shell access is available, call the local gateway directly. Read the API key from the repo `.env`; do not print it.

```bash
API_KEY="$(grep '^RETRIEVAL_API_KEY=' .env | cut -d= -f2-)"
curl -sS -X POST http://127.0.0.1:8010/search \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer ${API_KEY}" \
  -d '{"query":"self hosted search gateway","max_results":5,"extract_top_k":3}'
```

Extraction fallback:

```bash
API_KEY="$(grep '^RETRIEVAL_API_KEY=' .env | cut -d= -f2-)"
curl -sS -X POST http://127.0.0.1:8010/extract \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer ${API_KEY}" \
  -d '{"urls":["https://example.com"],"extract_depth":"basic"}'
```

## How To Read Results

Use `provider_chain` to explain where the answer came from. Use `errors` to decide whether to retry, reduce scope, or report partial results.

When answering the user, cite result URLs and prefer content from `content` over `snippet` when it is present. If search results are weak, say so and include the provider errors instead of pretending the search was conclusive.

## Operating Assumptions

The expected local services are:

- Gateway: `http://127.0.0.1:8010`
- SearXNG debug UI/API: `http://127.0.0.1:8888`

The agent should call the gateway, not SearXNG directly, because the gateway owns authentication, routing, extraction, reranking, cache, quota guards, and fallback behavior.
