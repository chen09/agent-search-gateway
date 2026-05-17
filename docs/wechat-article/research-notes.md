# WeChat Article Research Notes

> Snapshot date: 2026-05-17. Pricing, quotas, and vendor plans change often. Treat the numbers below as article context, not permanent documentation.

## Why This Project Started

The practical trigger was simple: multiple agents can burn through hosted search API quotas quickly.

Observed agent users:

- Cursor
- Codex
- Claude
- OpenClaw
- Hermes

Initial pain:

- Tavily is useful, but free monthly credits are finite.
- Once several coding/research agents share the same search provider, the free quota becomes a real bottleneck.
- The operator wanted a self-hosted default path, while keeping Tavily as fallback.

Core reframing:

- The goal is not a narrow Tavily clone.
- The goal is an agent-facing search gateway that can route, extract, rerank, cache, observe, and fall back across providers.

Engineering completeness:

- The result is not only a Python endpoint.
- The result is an end-to-end chain:
  program -> Docker Compose -> GitHub Actions CI -> Docker Hub publishing -> Ubuntu server -> Nginx -> domain -> Let's Encrypt -> MCP -> Cursor/Codex agent usage.
- This completeness is the article's strongest proof point.
- The project is already useful as self-hosted agent infrastructure, while still being honest about production hardening gaps.

## Why Tavily-Like Search APIs Are Useful

The investigation changed the framing. A normal search UI, an AI answer engine, and an agent retrieval backend solve related but different problems.

| Option | What it is good at | Why it is not enough by itself |
|---|---|---|
| Google / browser search | Human browsing, interactive refinement, large web index | Not a stable agent API surface; agents need normalized JSON, extraction, source metadata, retries, and quotas. |
| Perplexity-style answer engine | Human-facing synthesized answers with citations | It may answer the question directly, but a gateway often needs raw ranked results, extraction control, provider observability, and routing. |
| Tavily / Brave Search API / Firecrawl | Programmatic AI search, extraction, web grounding | Useful, but each provider has quotas, cost, rate limits, and vendor-specific response shapes. |
| Self-hosted gateway | One internal contract for agents | Requires engineering: provider routing, extraction, cache, auth, rate limits, deployment, and maintenance. |

## Competitor / Provider Notes

### Tavily

Official docs say Tavily has a credit-based model with free API credits and per-credit paid usage. The docs also describe Search, Extract, Map, and Crawl credit costs.

Article angle:

- Tavily is valuable because it packages search and extraction for AI workflows.
- The problem is not that Tavily is bad; the problem is shared agent usage and credit limits.
- Tavily is a strong fallback/compatibility provider, not necessarily the default path.

Source:

- https://docs.tavily.com/documentation/api-credits

### Brave Search API

Official Brave Search API material positions it as an independent search API with AI-app usage rights on paid plans and a Free AI tier.

Article angle:

- Brave is interesting because it has its own web index at scale.
- It should be optional until budget/usage guardrails are built.
- In this project Brave remains disabled by default.

Source:

- https://brave.com/search/api/

### Firecrawl

Firecrawl focuses on web data extraction, crawling, scraping, and AI-oriented web data workflows. Its docs describe credits, endpoint costs, and plan/concurrency concepts.

Article angle:

- Firecrawl is relevant for extraction/crawl-heavy use cases.
- It is not needed for the current MVP because SearXNG + trafilatura + optional Jina Reader is enough for a first open-source-first gateway.
- Later, Crawl4AI or Firecrawl-like capabilities can be added for JS-heavy pages.

Sources:

- https://docs.firecrawl.dev/pt-BR/billing
- https://docs.firecrawl.dev/developer-guides/usage-guides/choosing-the-data-extractor

### Perplexity Search API

Perplexity’s Search API docs describe real-time web search results, ranked results, domain filtering, multi-query search, and content extraction for developers. Pricing docs also list Search API as priced per 1K requests.

Article angle:

- Perplexity helps explain why "AI search" is not the same as just opening Google.
- For this gateway, Perplexity-like products are a category reference, not the first default provider.

Sources:

- https://docs.perplexity.ai/docs/search/quickstart
- https://docs.perplexity.ai/docs/getting-started/pricing

## Open-Source Default Notes

### SearXNG

Official SearXNG docs describe it as a free internet metasearch engine that aggregates results from many search services and does not track/profile users. It can be self-hosted.

Its Search API can return JSON, CSV, or RSS when enabled, but public instances often disable these output formats. This is a strong reason to self-host.

Its limiter docs explain the operational risk: because SearXNG forwards traffic to upstream search engines, it can be classified as bot-like and hit CAPTCHA or blocks. Limiter, Valkey, and correct proxy headers matter.

Article angle:

- SearXNG is suitable as the default first-hop provider for a self-hosted agent gateway.
- It should not be treated as the only provider in production.
- The gateway should expose provider_chain and errors so agents/operators can see what happened.

Sources:

- https://docs.searxng.org/
- https://docs.searxng.org/dev/search_api.html
- https://docs.searxng.org/admin/searx.limiter

## Cursor Rules / MCP Notes

Cursor official rules docs distinguish:

- Project Rules: stored under `.cursor/rules`, version-controlled and scoped to a codebase.
- User Rules: global to the Cursor environment and defined in settings.

The user tested Cursor User Rules import and confirmed the repository import worked when using the repo URL:

```text
https://github.com/chen09/agent-search-gateway
```

Do not use a `blob/...mdc` file URL for Cursor's GitHub/GitLab import because Cursor attempts to `git clone` the URL.

Source:

- https://docs.cursor.com/context/rules

## Verified Project Evidence

Public gateway:

```text
https://api.agentsearchgateway.com
```

Health evidence observed from Cursor:

```json
{
  "ok": true,
  "version": "0.2.2",
  "provider_order": ["searxng", "tavily"],
  "providers": {
    "searxng": true,
    "tavily": false,
    "brave": false
  },
  "searxng_base_urls": ["http://searxng:8080"],
  "reranker_enabled": false,
  "jina_reader_configured": false
}
```

Cursor search evidence from user:

```text
Search A:
provider_chain: ["searxng:searxng:8080"]
results count: 2
errors: []

Search B:
provider_chain: ["searxng:searxng:8080"]
results count: 3
errors: []

Search C:
provider_chain: ["searxng:searxng:8080"]
results count: 1
errors: []
```

This confirms:

- Cursor User Rule import worked.
- Cursor saw and called the MCP tools.
- The MCP server called the public gateway.
- The public gateway routed to self-hosted SearXNG.
- Tavily/Brave were not used.
- Codex is also configured with the same `agent-search-gateway` MCP, so the gateway is positioned as shared infrastructure rather than a Cursor-only integration.
