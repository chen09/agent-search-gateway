# Project Notes

These notes capture the working decisions, setup evidence, and article material from the first Agent Search Gateway build-out. They intentionally avoid real API keys, Docker Hub tokens, server `.env` contents, logs, and cached page content.

## Current Position

Agent Search Gateway is a self-hosted search and web retrieval gateway for AI agents. The useful framing is not "a Tavily clone"; it is one stable agent-facing entry point with provider routing, extraction, reranking, cache, quota guard, and fallback.

The repo now supports:

- Unified gateway endpoints: `GET /search`, `POST /search`, and `POST /extract`.
- Tavily-compatible adapters: `/tavily/search`, `/compat/tavily/search`, `/tavily/extract`, `/compat/tavily/extract`.
- Local SearXNG search as the default path.
- Local trafilatura extraction.
- Optional self-hosted or hosted Jina Reader fallback.
- Optional CrossEncoder reranking, kept out of the base install because it pulls PyTorch.
- In-process search and content cache.
- Optional Tavily provider with local daily credit guard, disabled by default.
- Brave provider reserved for future work, disabled by default.
- Docker Compose stack with retrieval API, SearXNG, and Valkey.
- Docker Hub image publishing.
- Python MCP server for Cursor, Codex, Claude, OpenClaw, Hermes, and similar clients.
- Reusable Cursor User Rule template for encouraging the MCP tools when web/current information is needed.
- Apache-2.0 license.

## Release State

GitHub repository:

```text
https://github.com/chen09/agent-search-gateway
```

Docker Hub image:

```text
docker.io/chen920/agent-search-gateway:0.2.2
docker.io/chen920/agent-search-gateway:0.2
docker.io/chen920/agent-search-gateway:latest
```

Important tags:

- `v0.2.0`: MCP and agent integration support.
- `v0.2.1`: Docker Hub image publishing.
- `v0.2.2`: `uvx` MCP package entrypoint and public image update.

The public API host is:

```text
https://api.agentsearchgateway.com
```

Root domain direction:

- `api.agentsearchgateway.com` is the canonical machine/API endpoint.
- `agentsearchgateway.com` can later become docs, landing page, status, or human-facing guide.

## Architecture

Runtime stack:

```text
Agent client
  -> MCP stdio server or HTTP call
  -> retrieval-api FastAPI service
  -> provider router
  -> SearXNG / optional hosted provider
  -> trafilatura / optional Jina Reader
  -> optional reranker
  -> unified JSON response
```

Docker services:

- `retrieval-api`: FastAPI gateway, exposed on `127.0.0.1:8010` in Compose.
- `searxng`: local metasearch backend, exposed on `127.0.0.1:8888`.
- `valkey`: available for cache/state evolution; current cache is still in-process.
- `jina-reader`: optional Compose profile for self-hosted extraction fallback.

Public deployment stack:

- Ubuntu server.
- Docker and Docker Compose.
- Nginx reverse proxy.
- Let’s Encrypt certificate.
- `api.agentsearchgateway.com` proxies to the local retrieval API.

## Key Decisions

Open-source-first default:

- SearXNG is the default search backend.
- trafilatura is the default extraction backend.
- Jina Reader is optional fallback.
- Tavily is optional compatibility/fallback provider, not required.
- Brave is not enabled until a real budget/quota guard exists.
- Firecrawl is not required for the current version; Crawl4AI or another JS-capable extractor can be evaluated later.

Secrets boundary:

- Server/Docker `.env` stores provider and gateway secrets.
- Agent MCP config stores only gateway access information.
- Agent clients should never receive Tavily, Brave, Jina, MiniMax, or DeepSeek provider keys.
- The gateway key exposed to clients is `AGENT_SEARCH_GATEWAY_API_KEY`, which is the same value as server-side `RETRIEVAL_API_KEY`.

MCP install style:

- End users should use `uvx --from git+https://github.com/chen09/agent-search-gateway.git@v0.2.2 agent-search-gateway-mcp`.
- Developers working inside the repo can use `.venv/bin/python integrations/mcp/server.py`.
- Direct MCP `env` is acceptable for a private local config.
- Env-file style remains the safer documentation default for shared/public instructions.

Python and PyTorch:

- Local development uses Python 3.12 through `pyenv` and a repo-local `.venv`.
- Base gateway does not require PyTorch.
- Reranker dependencies live separately because `sentence-transformers` pulls PyTorch.
- On Apple Silicon, `RERANKER_DEVICE=mps` should only be used after confirming the installed PyTorch build supports the workload.

License:

- Apache-2.0 was chosen because the project is intended to be reused, self-hosted, and extended by other operators.

## MCP Client Configuration

Copyable JSON for clients that support `mcpServers`:

```json
{
  "mcpServers": {
    "agent-search-gateway": {
      "command": "uvx",
      "args": [
        "--from",
        "git+https://github.com/chen09/agent-search-gateway.git@v0.2.2",
        "agent-search-gateway-mcp"
      ],
      "env": {
        "AGENT_SEARCH_GATEWAY_URL": "https://api.agentsearchgateway.com",
        "AGENT_SEARCH_GATEWAY_API_KEY": "replace-with-your-gateway-api-key",
        "AGENT_SEARCH_GATEWAY_TIMEOUT": "90"
      }
    }
  }
}
```

The MCP server exposes:

- `agent_gateway_health`
- `agent_search`
- `agent_extract`

Getting the key:

```bash
grep '^RETRIEVAL_API_KEY=' .env | cut -d= -f2-
```

Remote operator shape:

```bash
ssh ubuntu@your-server
cd ~/agent-search-gateway
grep '^RETRIEVAL_API_KEY=' .env | cut -d= -f2-
```

Key rotation shape:

```bash
NEW_KEY="$(openssl rand -hex 32)" \
  perl -0pi -e 's/^RETRIEVAL_API_KEY=.*/RETRIEVAL_API_KEY=$ENV{NEW_KEY}/m' .env
docker compose up -d retrieval-api
```

After rotation, every MCP client config that still uses the old gateway key must be updated.

## Cursor Integration

MCP gives Cursor callable tools. Cursor rules tell Cursor when to prefer those tools.

Current repo includes a reusable rule for customers importing from GitHub into Cursor User Rules:

```text
rules/agent-search-gateway-user-rule.mdc
```

For Cursor User Rules GitHub/GitLab import, use the repository URL:

```text
https://github.com/chen09/agent-search-gateway
```

For manual copy, use the raw file URL:

```text
https://raw.githubusercontent.com/chen09/agent-search-gateway/main/rules/agent-search-gateway-user-rule.mdc
```

The rule says to use Agent Search Gateway MCP tools for web search, current information, external documentation lookup, and URL extraction. It also says not to use the gateway for local repository search.

Test prompt for Cursor Agent mode:

```text
请主动使用 agent-search-gateway MCP 做一次真实检索测试。

要求：
1. 先调用 `agent_gateway_health`，确认 gateway 可用，并报告 version、provider_order、providers。
2. 再调用 `agent_search`，搜索：
   "SearXNG self hosted metasearch engine"
3. 参数：
   max_results=3
   extract_top_k=1
   include_summary=true
   provider=auto
4. 返回：
   - 是否成功
   - provider_chain
   - results 数量
   - 每个 result 的 title、url、source、score
   - errors 是否为空
5. 不要用你自己的内置联网能力，不要只解释。必须实际调用 MCP tools。
```

If Cursor does not call the tools:

```text
你现在必须测试 MCP 工具。请不要回答说明文字，直接调用 `agent_gateway_health` 和 `agent_search`。如果你看不到这些 tools，请明确说“当前 Cursor 会话看不到 agent-search-gateway MCP tools”。
```

Practical expectation:

- Cursor Agent may automatically call MCP tools when it decides they are relevant.
- A Cursor User Rule improves reliability but does not make tool use a hard guarantee.
- Cursor Agent mode is the right place to test MCP tools.
- Auto-run settings affect whether Cursor asks for confirmation before tool calls.

## Verified Evidence

Local and repo checks completed during the build:

- Python syntax check passed for `api/main.py`.
- Python syntax check passed for `integrations/mcp/server.py`.
- Repo-local `.venv` uses Python 3.12.10.
- Editable package install succeeded for `agent-search-gateway==0.2.2`.
- `uvx --from /local/path agent-search-gateway-mcp` started and listed MCP tools.
- `uvx --from git+https://github.com/chen09/agent-search-gateway.git@v0.2.2 agent-search-gateway-mcp` started and listed MCP tools.
- MCP `agent_gateway_health` returned `ok=true`.
- Public health endpoint returned `version=0.2.2`.
- GitHub Actions Docker image workflow completed successfully for `v0.2.2`.
- GitHub Actions Docker Hub description workflow completed successfully after documentation updates.

Public health endpoint:

```text
https://api.agentsearchgateway.com/healthz
```

Expected current response characteristics:

- `ok=true`
- `version=0.2.2`
- `providers.searxng=true`
- `providers.tavily=false`
- `providers.brave=false`
- `reranker_enabled=false`
- `jina_reader_configured=false`

## Useful Article Angles

The project story is about replacing paid-first search APIs with a controllable open-source-first retrieval layer for agents.

Possible article outline:

1. The problem: coding agents need current web context, but built-in search and hosted APIs are opaque, paid, or inconsistent.
2. The design choice: build a gateway, not a vendor clone.
3. The default route: SearXNG plus trafilatura, with optional Jina Reader.
4. The hosted provider rule: Tavily/Brave are optional fallback, never default.
5. The agent integration: MCP as the primary tool surface.
6. The operational boundary: provider keys live on the server; agents only get the gateway key.
7. The deployment path: Docker Compose locally, Docker Hub image for reuse, Nginx and Let’s Encrypt for public API.
8. The result: Cursor/Codex/Claude/OpenClaw/Hermes can all use the same retrieval endpoint.
9. The next work: hardening, persistent cache, rate limits, SSRF protection, provider circuit breakers, and richer open-source extraction.

Useful phrasing:

- "Not a Tavily clone; a provider router and retrieval gateway."
- "Agents should not own provider credentials."
- "The cheapest reliable provider is the one you can run yourself."
- "MCP is the agent-facing adapter; Docker Compose is the operator-facing runtime."
- "A search tool for agents is still useful for humans because the API returns normalized sources, extracted content, scores, and errors."

## What Went Well

The progress stayed fast because decisions were kept explicit:

- Avoided overbuilding a full Firecrawl/Tavily/Perplexica clone.
- Kept Brave disabled because free-credit behavior and budget safety were not yet proven.
- Kept PyTorch out of the base image to avoid making Mac mini and small-server installs heavy.
- Used `uvx` for MCP because users can run the server from GitHub without cloning.
- Kept direct MCP `env` acceptable for private configs while keeping env-file docs as the safer public pattern.
- Chose `api.agentsearchgateway.com` as the canonical API endpoint and left the root domain open for docs or landing content.
- Published Docker Hub image early so users can run without building locally.
- Made README and Docker Hub overview trilingual early.

## Next Technical Work

Highest value next steps:

- Add Docker healthchecks for `retrieval-api`, `searxng`, and `valkey`.
- Add CI for Python syntax, import checks, unit tests, MCP startup, and Docker build.
- Add SSRF protection before marketing the public API broadly.
- Add per-client rate limits and request size limits.
- Move cache from in-process TTL to Valkey.
- Add structured redacted logs with request IDs.
- Add provider timeout budgets and circuit breakers.
- Add a small human-facing web page or docs landing page on `agentsearchgateway.com`.
- Verify Cursor, Codex, Claude, OpenClaw, and Hermes installs one by one with screenshots or exact transcripts.
- Evaluate Crawl4AI or another JS-capable extraction backend before adding Firecrawl.

## Open Questions

- Should the public gateway remain personal/private by key, or become a limited public demo?
- Should the MCP package also be published to PyPI later, or is `uvx --from git+...` enough?
- Should the Docker image pin SearXNG by version instead of using `latest`?
- Should API version and package version always move together, or should MCP-only changes have separate package versions?
- Should the Cursor User Rule also be mirrored into `AGENTS.md` or other agent-specific instruction files?
