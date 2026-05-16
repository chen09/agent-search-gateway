# Changelog

## 0.2.0 - 2026-05-17

- Added Docker Compose verified local stack with SearXNG on host port 8888, retrieval API on 8010, and Valkey.
- Added open-source-first provider routing with SearXNG as the default path and Tavily disabled unless explicitly configured.
- Split the API into config, model, provider, extraction, rerank, cache, quota, and summary modules.
- Kept PyTorch and sentence-transformers out of the base install; optional reranker dependencies live in `api/requirements-reranker.txt`.
- Added a host-side MCP stdio server for Cursor, Codex, Claude, OpenClaw, Hermes, and other MCP clients.
- Added an installable `agent-search-gateway` skill for agents that support skills.
- Added integration docs for clone-and-run agent setup.
