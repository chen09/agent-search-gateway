# Next Steps

This project is now usable as a local, self-hosted retrieval gateway for agents. The next work should make it easier to operate, safer to expose, and more useful for long-running research agents.

## Priority 1: Agent Integration Polish

- Add screenshots or per-client config examples after verifying Cursor, Codex, Claude, OpenClaw, and Hermes on real installs.
- Add an optional installer script that prints absolute-path MCP config without writing user global config.

## Priority 2: Reliability

- Add Docker healthchecks for `retrieval-api`, `searxng`, and `valkey`.
- Add provider timeout budgets and circuit breakers.
- Add request size limits for `/search` and `/extract`.
- Add structured redacted logs that never include API keys or authorization headers.

## Priority 3: Cache And State

- Move search/content cache from in-process TTL cache to Valkey for shared multi-process use.
- Add cache keys that include provider, query, extraction settings, and version.
- Add cache invalidation or TTL controls per request.

## Priority 4: Security

- Add SSRF protection before exposing the gateway beyond trusted local access.
- Restrict extraction to http/https URLs and block private/internal address ranges by default.
- Add basic per-client rate limits.

## Priority 5: More Open-Source Providers

- Add Crawl4AI or another JS-capable extraction backend for pages that trafilatura cannot read.
- Add additional SearXNG instance routing for fallback and rate-limit recovery.
- Keep Tavily, Firecrawl, and Brave optional; do not make hosted APIs part of the default route.

## Priority 6: Release Quality

- Add GitHub Actions for Python syntax checks, unit tests, MCP import checks, and Docker build checks.
- Add tagged release notes for each version.
- Choose a LICENSE before treating the repository as a public reusable package.
