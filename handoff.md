# Handoff

## Status
READY TO CONTINUE

## Original Goal
Build Agent Search Gateway as a self-hosted retrieval gateway for Cursor, Codex, Claude, OpenClaw, Hermes, and similar agents, then publish the project and write a WeChat article explaining the engineering story.

## Current State
- Confirmed fact with evidence: the repository contains the gateway implementation, MCP server, agent skill, Cursor rule, Docker files, and trilingual README files. Evidence: `api/`, `integrations/mcp/server.py`, `skills/agent-search-gateway/SKILL.md`, `rules/agent-search-gateway-user-rule.mdc`, `docker-compose.yml`, `README.md`, `README.zh.md`, `README.ja.md`.
- Confirmed fact with evidence: the project roadmap and next technical priorities are documented. Evidence: `docs/ROADMAP.md`, `docs/NEXT_STEPS.md`, `docs/PROJECT_NOTES.md`.
- Confirmed fact with evidence: WeChat article source, copy HTML, image prompt pack, and renderer are documented. Evidence: `docs/wechat-article/article-wechat-ready.md`, `docs/wechat-article/article-wechat-copy.html`, `docs/wechat-article/article-wechat-copy-no-images.html`, `docs/wechat-article/image-production-pack.md`, `docs/wechat-article/render-wechat-html.mjs`.
- Confirmed fact with evidence: the latest committed implementation/article state before this handoff was `93362d8 Improve WeChat article retrieval positioning`. Evidence: `git log --oneline -5`.
- User-reported fact: the WeChat subscription article was published on 2026-05-18. Evidence captured in `docs/wechat-article/README.md` and `docs/PROJECT_NOTES.md`.
- User-reported fact: public API host is `https://api.agentsearchgateway.com`; Docker image is `docker.io/chen920/agent-search-gateway:0.2.2`. Evidence captured in `docs/PROJECT_NOTES.md` and public-facing docs.

## Recent Progress
- Reworked the article around the core idea that agents need a programmable retrieval tool layer, not just a human search box.
- Generated copy-ready WeChat HTML files and verified they include the updated section `为什么 Agent 需要专门的检索工具`.
- Added or preserved GPT Image prompts for Figure 0 through Figure 9 and the WeChat cover image in `docs/wechat-article/image-production-pack.md`.
- Recorded the final article abstract and user-reported publication status in `docs/wechat-article/README.md` and `docs/PROJECT_NOTES.md`.
- Created this `handoff.md` so the next session can restart production hardening without relying on hidden chat context.

## Next Minimal Step
Start production hardening with a narrow branch focused on request safety: implement SSRF protection and request size limits for `/extract` and search requests that trigger content extraction.

## Next 3 Steps
1. Read `docs/NEXT_STEPS.md`, `docs/ROADMAP.md`, `api/main.py`, `api/extraction.py`, and `api/config.py` to locate the safest request-boundary insertion points.
2. Add tests for blocked private/internal URLs, unsupported schemes, oversized inputs, and normal public HTTP/HTTPS URLs.
3. Implement the guard, run the existing tests, then add documentation notes for operators.

## Unfinished Work
### High
- SSRF protection before broader public use. Dependency: URL/IP validation design. Verification: tests covering localhost, private IPv4/IPv6, link-local, metadata IPs, DNS resolution, and allowed public URLs.
- Per-client rate limits and request size limits. Dependency: API key/client identity model. Verification: tests for limit hit, reset behavior, and error shape.
- Docker healthchecks for `retrieval-api`, `searxng`, and `valkey`. Dependency: stable health endpoints. Verification: `docker compose ps` health states and CI Compose validation.

### Medium
- Move cache from in-process TTL cache to Valkey. Dependency: cache key design and serialization. Verification: repeated requests hit shared cache across API process restarts.
- Provider timeout budgets and circuit breakers. Dependency: provider-level error taxonomy. Verification: simulated timeout/429/provider error tests preserve `provider_chain` and `errors`.
- Structured redacted logs. Dependency: request ID and redaction helper. Verification: tests or log inspection proving no API keys, auth headers, cookies, or raw provider secrets are logged.

### Low
- Human-facing root domain page for `agentsearchgateway.com`. Dependency: hosting choice. Verification: root domain opens docs/landing/status page while `api.agentsearchgateway.com` remains API-only.
- More verified screenshots/transcripts for Cursor, Codex, Claude, OpenClaw, and Hermes. Dependency: real client sessions. Verification: docs include exact client behavior without secrets.
- Evaluate Crawl4AI or another JS-capable extraction backend. Dependency: clear page cases where trafilatura is insufficient. Verification: extraction quality comparison.

## Blockers
- Blocker: the public gateway should not be treated as a safe public service yet.
  - Likely cause: SSRF protection, per-client limits, healthchecks, and structured logging are not complete.
  - Impact: keep usage personal/private by API key until hardening is done.
  - Confidence: high.
  - Possible workaround: restrict access at Nginx/firewall/API key level and avoid broad public demos.
- Blocker: exact WeChat article URL is not stored in the repo.
  - Likely cause: article was published manually after local preparation.
  - Impact: future marketing docs cannot link to the article unless the user provides the URL.
  - Confidence: high.
  - Possible workaround: ask user for the published article URL if a public reference page is added.
- Blocker: cloud server state may drift from repo state.
  - Likely cause: server operations and `.env` are intentionally not committed.
  - Impact: verify remote Compose/Nginx/cert state before making production changes.
  - Confidence: medium.
  - Possible workaround: SSH to the server only when the user requests/authorizes it; never print secrets.

## Do Not Retry Without New Evidence
- Do not automate WeChat editor copy/paste again without explicit user request. Earlier browser automation risked title/body formatting problems; manual copy from copy-only HTML worked better.
- Do not print, copy, commit, or summarize `.env` secret values. Provider keys and gateway keys must remain outside Git.
- Do not enable Brave as a default provider until budget/usage guard exists.
- Do not make Firecrawl or Tavily required for the base gateway; the project direction is open-source-first with hosted providers optional/fallback.
- Do not move reranker/PyTorch dependencies into the base install. Keep heavy reranker dependencies optional.

## Files And Artifacts
- `README.md`, `README.zh.md`, `README.ja.md`: trilingual GitHub user entry points.
- `docs/DOCKER_HUB.md`, `docs/DOCKER_HUB_OVERVIEW.md`: Docker Hub usage and overview docs.
- `docs/ENVIRONMENT.md`: environment variable guidance; do not add real secrets.
- `docs/NEXT_STEPS.md`: prioritized production hardening list.
- `docs/ROADMAP.md`: phase roadmap.
- `docs/PROJECT_NOTES.md`: build decisions, evidence, article lessons, and next technical work.
- `docs/wechat-article/README.md`: article publication status and publishing flow.
- `docs/wechat-article/image-production-pack.md`: image prompts for Figure 0 through Figure 9 plus WeChat cover.
- `docs/wechat-article/article-wechat-copy.html`: copy-only WeChat body with images.
- `docs/wechat-article/article-wechat-copy-no-images.html`: copy-only WeChat body with image placeholders.
- `integrations/mcp/server.py`: MCP server entrypoint.
- `rules/agent-search-gateway-user-rule.mdc`: Cursor User Rule for MCP usage.
- `skills/agent-search-gateway/SKILL.md`: agent skill usage guidance.

## Decisions
- Decision: this is a gateway, not a Tavily clone.
  - Reason: agents need one stable, observable entry point with provider routing, extraction, cache, quota guard, and fallback.
  - Evidence: `docs/ROADMAP.md`, `docs/PROJECT_NOTES.md`, `docs/wechat-article/article-wechat-ready.md`.
- Decision: SearXNG remains the default provider; Tavily is optional fallback.
  - Reason: the project is open-source-first and designed to reduce paid-provider dependency.
  - Evidence: `docs/ROADMAP.md`, `api/config.py`.
- Decision: provider keys live on the server; agents only receive gateway URL/key/timeout.
  - Reason: prevents provider keys from spreading across Cursor/Codex/Claude/OpenClaw/Hermes configs and enables centralized quota/rate controls.
  - Evidence: `docs/PROJECT_NOTES.md`, `docs/wechat-article/article-wechat-ready.md`.
- Decision: MCP is the primary agent integration surface.
  - Reason: Cursor, Codex, Claude, OpenClaw, Hermes can all consume MCP-style tools.
  - Evidence: `integrations/mcp/server.py`, `docs/integrations/agent-clients.md`, `rules/agent-search-gateway-user-rule.mdc`.
- Decision: WeChat article visuals are prompt-preserved rather than generated assets committed.
  - Reason: images were created manually in ChatGPT Image and inserted into WeChat; prompts are reusable and repo-safe.
  - Evidence: `docs/wechat-article/image-production-pack.md`.

## Assumptions
- Assumption: the deployed public API is still reachable at `https://api.agentsearchgateway.com`.
  - Why it is plausible: it was verified during the project build and documented in `docs/PROJECT_NOTES.md`.
  - How to verify: call `curl https://api.agentsearchgateway.com/healthz` without printing secrets.
- Assumption: Docker Hub image `chen920/agent-search-gateway:0.2.2` remains public.
  - Why it is plausible: Docker publishing and docs were completed earlier.
  - How to verify: `docker pull chen920/agent-search-gateway:0.2.2`.
- Assumption: current user priority after article publication is production hardening rather than article editing.
  - Why it is plausible: user explicitly said future restart should focus on production environment hardening.
  - How to verify: ask only if the next request is ambiguous.

## Quick Resume
Agent Search Gateway is usable and documented: repo, Docker image, public API, MCP, Cursor rule, and WeChat article materials are in place. The article was user-reported published on 2026-05-18. The next restart should begin production hardening, starting narrowly with SSRF protection and request size limits, while preserving the core decisions: SearXNG default, hosted providers optional, provider keys server-side, and MCP as the agent-facing integration.
