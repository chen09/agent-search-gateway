# Article Draft Notes

This file keeps the working draft direction. The polished publishing draft is `article-wechat-ready.md`.

## Core Message

The project started from Tavily free-credit pressure, but the real insight was that agent search is infrastructure. The useful outcome is not a Tavily clone; it is a self-hosted, open-source-first gateway that lets multiple agents share one retrieval layer.

## Article Spine

1. Start with the concrete pain: Cursor/Codex/Claude/OpenClaw/Hermes all need search.
2. Explain why Tavily-like APIs are useful and why Google/Perplexity are different categories.
3. Show the gateway decision: SearXNG first, Tavily fallback, Brave optional later.
4. Emphasize engineering completeness: program -> Docker -> CI/CD -> Docker Hub -> cloud server -> Nginx -> domain -> free SSL -> MCP -> Rules.
5. Show proof: Cursor called the MCP and provider_chain returned SearXNG.
6. Show what is still not production-grade.
7. Close with the vibe-coding / Codex GPT-5.5 point: fast because human direction plus AI execution stayed tight.

## Tone

- First-person, practical, not corporate marketing.
- Admit limitations.
- Praise Codex lightly but keep the article about engineering judgment.
- Avoid exaggerated claims such as "production ready" or "replaces all search APIs".
- Make clear that the result is distributable infrastructure, not only a local script or API demo.
