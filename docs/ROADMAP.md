# Agent Search Gateway Roadmap

This project is a self-hosted retrieval gateway for coding and research agents. The goal is one stable API that can route across self-hosted and hosted providers, extract page content, rerank, cache, and degrade safely when paid or rate-limited providers are unavailable.

## Phase 1: Stable Local Core

- Keep SearXNG as the always-available fallback search provider.
- Keep trafilatura as the default local extraction path.
- Keep Jina Reader as an optional extraction fallback.
- Keep the response shape stable for Cursor, Codex, MiniMax, DeepSeek, and other agents.
- Make PyTorch-dependent reranking optional so the base gateway runs on small machines.

## Phase 2: Hosted Provider Routing

- Add Tavily as an optional fallback and compatibility provider, not the default route.
- Require explicit `TAVILY_ENABLED=true` and `TAVILY_API_KEY`.
- Guard Tavily with a local daily credit limit before each hosted request.
- Keep SearXNG/local extraction as the default route; fall back away from hosted providers when they are disabled, over local quota, rate-limited, or unavailable.
- Keep Brave disabled until a real budget/usage guard exists.

## Phase 3: Compatibility Adapters

- Provide native gateway endpoints:
  - `GET /search`
  - `POST /search`
  - `POST /extract`
- Provide Tavily-compatible aliases:
  - `POST /tavily/search`
  - `POST /tavily/extract`
  - `POST /compat/tavily/search`
  - `POST /compat/tavily/extract`
- Preserve a gateway-native response that exposes `provider_chain`, `errors`, and normalized result fields.

## Phase 4: Cache and Quota

- Keep in-process TTL cache for single-user local runs.
- Add persistent shared cache later, preferably Valkey because it already exists in Docker Compose.
- Cache search responses and extracted URL content separately.
- Never cache API keys, authorization headers, cookies, or full request headers.
- Extend quota guards to Brave and future paid providers before enabling them.

## Phase 5: Production Hardening

- Add SSRF protection before exposing the gateway outside trusted local networks.
- Add request size limits, per-client rate limits, and structured redacted logs.
- Add provider timeout budgets and circuit breakers.
- Keep Docker Compose verification in release checks.
- Expand CI beyond the current unit/import/Docker build checks with Docker Compose config validation and release smoke tests.

## Phase 6: Agent Integration

- Keep the stdio MCP server as the primary integration surface for Cursor, Codex, Claude, OpenClaw, Hermes, and similar agents.
- Keep the installable agent skill as usage guidance and HTTP fallback documentation.
- Add more copyable client examples after each target client is smoke-tested.
- Keep hosted provider keys server-side; agents should only receive the gateway API key.
- Add native MiniMax or DeepSeek summarization only if it is more useful than the current `SUMMARY_WEBHOOK_URL` handoff.
