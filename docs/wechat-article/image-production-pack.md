# WeChat Article Image Production Pack

## Purpose

This pack provides GPT Image prompts for a WeChat article about Agent Search Gateway.

Article positioning:

- Personal engineering story.
- One-day vibe coding build.
- Self-hosted, open-source-first replacement/fallback layer for Tavily-style agent search.
- Full-stack delivery: Python, Docker, CI/CD, Docker Hub, Nginx, domain, SSL, MCP, Cursor User Rules.
- Core visual message: this is not just an API demo; it is a complete chain from code to public service to agent tool usage.

Visual direction:

- Clean technical Chinese infographics.
- Warm white background.
- Modern SaaS architecture style.
- Large readable labels.
- Avoid tiny UI screenshots.
- Avoid decorative gradient blobs.
- Use short Chinese labels; keep paragraphs in article body.

Output directory:

```text
docs/wechat-article/images/
```

Recommended export:

- PNG
- 16:9 landscape
- At least 1792px wide
- Prefer 3840x2160 if available

## Figure 0: Hero

Filename:

```text
fig-00-hero-agent-search-gateway.png
```

Caption:

> 头图：给 AI Agent 用的自托管检索网关。

Prompt:

```text
Create a polished Chinese hero image for a WeChat technical article.

Theme: building a self-hosted retrieval gateway for personal AI agents.

Canvas: 16:9 landscape, warm white background, premium SaaS architecture style, crisp vector illustration, high readability.

Main title in Chinese:
“给自己的 AI Agent 搭了一个自托管检索网关”

Subtitle:
“SearXNG + Docker + MCP 跑通真实调用”

Composition:
Left side: several AI agents labeled Cursor, Codex, Claude, OpenClaw, Hermes.
Above them: a small problem card labeled “每个 Agent 都要查资料”.
Center: a strong gateway block labeled “Agent Search Gateway”.
Right side: provider blocks labeled SearXNG 默认, Tavily 兜底, Brave 可选, Jina Reader.
Bottom: deployment strip labeled Code → Docker → GitHub Actions → Docker Hub → Ubuntu Docker → Nginx → HTTPS → MCP.

Style:
Professional, technical, optimistic but not flashy.
Use blue, green, and amber accents.
No fake screenshots.
No tiny text.
Make the gateway block visually central.
```

## Figure 1: Human Search vs Agent Retrieval

Filename:

```text
fig-01-human-search-vs-agent-retrieval.png
```

Caption:

> 图 1：Google 更像人的搜索入口，Perplexity 更像答案引擎，Tavily 这类服务更接近 agent 的检索工具层。

Prompt:

```text
Create a Chinese positioning infographic for a WeChat technical article.

Title:
“Google、Perplexity、Tavily 解决的不是同一个问题”

Canvas: 16:9 landscape, warm white background, clean vector style, mobile-readable.

Three clear columns plus one gateway layer:

Column 1 title: “Google”
Subtitle: “人的搜索入口”
Visuals: search box, web results, human reading pages.
Short labels:
搜索框
人工判断
网页结果

Column 2 title: “Perplexity”
Subtitle: “答案引擎”
Visuals: question bubble, synthesized answer, citation marks.
Short labels:
直接问答
引用
人来阅读

Column 3 title: “Tavily 类工具”
Subtitle: “Agent 检索工具层”
Visuals: API card, URL list, extracted content block, relevance score.
Short labels:
Search
Extract
Crawl
结构化结果

Bottom layer:
“Agent Search Gateway”
Show it collecting SearXNG, Tavily 兜底, Brave 可选 into one controlled route.

Style:
Professional SaaS infographic, clear hierarchy, no paragraphs, no tiny text, no fake brand logos.
```

## Figure 2: Provider Gateway Map

Filename:

```text
fig-02-provider-gateway-map.png
```

Caption:

> 图 2：Cursor、Codex、Claude、OpenClaw、Hermes 通过 MCP 接入同一个公网 API；服务器侧再统一路由到 SearXNG、Tavily 兜底和其他 provider。

Prompt:

```text
Create a Chinese architecture infographic.

Title:
“Agent Search Gateway 整体链路”

Canvas: 16:9 landscape, warm white background, modern SaaS architecture diagram.

Left side:
Agent clients labeled Cursor, Codex, Claude, OpenClaw, Hermes.
Small labels under clients: “User Rule / Skill” and “MCP tools”.

Center:
HTTPS API block labeled “api.agentsearchgateway.com”.
Below it: Docker server block labeled “Ubuntu + Docker Compose”.
Inside server show:
retrieval-api
SearXNG
Valkey

Right side:
Provider row:
SearXNG 默认
Tavily 兜底
Brave 可选
Jina Reader 可选
Crawl4AI / Firecrawl 未来

Inside retrieval-api show:
Provider Router
Extraction
Cache
Fallback
Quota Guard

Show returned response fields:
provider_chain
results
errors

Use arrows:
Agents → MCP → HTTPS API → retrieval-api → Provider Router → Providers → unified JSON response.

Highlight “SearXNG 默认” in green and “Tavily 兜底” in amber.
No long text.
```

## Figure 3: Gateway Architecture

Filename:

```text
fig-03-gateway-architecture.png
```

Caption:

> 图 3：agent 只面对一个 gateway；gateway 负责 provider routing、正文抽取、缓存、rerank 和 fallback。

Prompt:

```text
Create a detailed but readable Chinese system architecture diagram.

Title:
“Agent Search Gateway 内部架构”

Canvas: 16:9 landscape, clean vector, white background, technical but friendly.

Layout:
Left: “Agent Clients”
List: Cursor, Codex, Claude, OpenClaw, Hermes

Center: “Agent Search Gateway”
Show internal modules as stacked blocks:
统一 Search API
Provider Router
Extractor
Reranker 可选
Cache
Quota Guard
Summary Webhook

Right: “Providers”
SearXNG
Tavily fallback
Jina Reader
Brave future

Bottom: “统一响应”
Show fields:
query
provider_chain
results
errors

Use clear arrows.
No code except field names.
Keep text large.
```

## Figure 4: Full Stack Deployment

Filename:

```text
fig-04-full-stack-deployment.png
```

Caption:

> 图 4：从程序到 Docker、CI/CD、Docker Hub、云服务器、Nginx、HTTPS、域名和 MCP，全部打通成一条完整链路。

Prompt:

```text
Create a Chinese full-stack deployment diagram for a WeChat technical article.

Title:
“从代码到公网 API”

Canvas: 16:9 landscape, warm white background, premium infrastructure diagram style.

Show a left-to-right pipeline:
GitHub Repo
GitHub Actions
Docker Hub Image
Ubuntu Server
Docker Compose
Nginx
Let’s Encrypt
api.agentsearchgateway.com
MCP Clients

Inside Docker Compose show three services:
retrieval-api
SearXNG
Valkey

Add small success badges:
v0.2.2
HTTPS OK
Docker Hub OK

Style:
Clean, credible, engineering-focused.
Use blue for cloud/deployment, green for success, amber for warnings.
No tiny text.
```

## Figure 5: Secret Boundary

Filename:

```text
fig-05-secret-boundary.png
```

Caption:

> 图 5：agent 只拿 gateway key；真正的 provider keys 留在服务器上，由 gateway 控制。

Prompt:

```text
Create a Chinese security boundary infographic.

Title:
“Provider Key 不给 Agent”

Canvas: 16:9 landscape, white background, crisp vector style.

Left side: Agent clients labeled Cursor, Codex, Claude, OpenClaw, Hermes.
Show they only hold:
AGENT_SEARCH_GATEWAY_URL
AGENT_SEARCH_GATEWAY_API_KEY
TIMEOUT

Center: shield labeled “Agent Search Gateway”.

Right side: locked server .env vault labeled “服务器 .env”.
Inside vault show:
RETRIEVAL_API_KEY
TAVILY_API_KEY
BRAVE_API_KEY
JINA_API_KEY
MINIMAX_API_KEY
DEEPSEEK_API_KEY

Add red blocked arrow from agents to provider keys labeled “不直接暴露”.
Add green arrow through gateway labeled “统一路由 + 额度保护”.

No long text.
Make the security boundary visually obvious.
```

## Figure 6: Agent Client Integration

Filename:

```text
fig-06-agent-client-integration.png
```

Caption:

> 图 6：MCP 负责工具接入，User Rule / Skill 负责告诉 agent 什么时候应该用。

Prompt:

```text
Create a Chinese agent integration diagram.

Title:
“MCP + Rules：让 Agent 主动用 Gateway”

Canvas: 16:9 landscape, warm white background, clean technical vector.

Top row: Cursor, Codex, Claude, OpenClaw, Hermes.
Middle row:
MCP Server labeled “agent-search-gateway-mcp”
Tools:
agent_gateway_health
agent_search
agent_extract

Side label: “User Rule / Skill”
Text: “需要当前资料 → 优先检索”

Bottom: Agent Search Gateway → SearXNG.

Show Cursor User Rule imported from GitHub:
https://github.com/chen09/agent-search-gateway

Keep URL readable but not too large.
Use clean arrows and clear grouping.
```

## Figure 7: Validation Dashboard

Filename:

```text
fig-07-validation-dashboard.png
```

Caption:

> 图 7：provider_chain 明确显示走的是自托管 SearXNG，而不是 Tavily 或 Cursor 内置搜索。

Prompt:

```text
Create a Chinese validation dashboard infographic.

Title:
“真实验证：Cursor 已自动调用 Gateway，Codex 已接入 MCP”

Canvas: 16:9 landscape, dark-on-light dashboard style, professional SaaS metrics.

Show four proof cards:
Health OK
version 0.2.2
provider_chain: searxng:searxng:8080
errors: []

Show a simplified chain:
Cursor User Rule → MCP → api.agentsearchgateway.com → retrieval-api → SearXNG

Add small provider status:
SearXNG true
Tavily false
Brave false

Use green success indicators.
Avoid fake charts with meaningless numbers.
No tiny text.
```

## Figure 8: One-Day Vibe Coding Roadmap

Filename:

```text
fig-08-one-day-vibe-coding-roadmap.png
```

Caption:

> 图 8：一天内完成的不是单点功能，而是一条从想法到公网服务、再到 agent 自动调用的完整链路。

Prompt:

```text
Create a Chinese one-day engineering roadmap infographic.

Title:
“一天内跑通的全栈链路”

Canvas: 16:9 landscape, warm white background, premium roadmap style.

Horizontal timeline with 8 steps:
1 起因：Tavily 额度压力
2 方案：Gateway 而不是 clone
3 Python API
4 Docker Compose
5 GitHub Actions + Docker Hub
6 云服务器 + Nginx + HTTPS
7 MCP + uvx
8 Cursor User Rule 自动调用

Add a small note:
“Codex GPT-5.5 单 Agent 辅助完成”

Use icons:
quota gauge, gateway, Python, Docker, GitHub, server, lock, MCP tools, Cursor.

Style:
Optimistic, credible, engineering-focused.
No over-the-top hype.
Keep labels short and large.
```

## Figure 9: Production Hardening Roadmap

Filename:

```text
fig-09-production-hardening-roadmap.png
```

Caption:

> 图 9：现在已经跑通完整闭环；下一阶段要补的是安全、限流、缓存、观测和 provider 健康治理。

Prompt:

```text
Create a Chinese production hardening roadmap infographic for a WeChat technical article.

Title:
“从 MVP 到生产级 Gateway”

Canvas: 16:9 landscape, warm white background, clean engineering roadmap style.

Show the current baseline on the left:
“已跑通”
Python API
Docker Compose
Docker Hub
Nginx + HTTPS
MCP
Cursor 自动调用

Show five improvement lanes moving to the right:
安全: SSRF 防护, request size limit
限流: per-client rate limit, quota guard
稳定性: timeout budget, circuit breaker, healthcheck
缓存: Valkey 持久缓存, content cache
观测: provider_chain, errors, 脱敏日志

Right endpoint:
“更可靠的 Agent 检索基础设施”

Style:
Readable, practical, no hype.
Use green for completed baseline, amber for next work, blue for stable target.
No tiny text.
```

## WeChat Cover Image

Filename suggestion:

```text
wechat-cover-agent-search-gateway.png
```

Recommended size:

```text
900x383px, 2.35:1
```

Prompt:

```text
Create a WeChat article cover image for a Chinese technical article.

Aspect ratio:
2.35:1 wide cover, optimized for 900px x 383px.

Theme:
A modern, futuristic AI infrastructure cover for an article about building a self-hosted Agent Search Gateway for AI agents.

Main title in Chinese:
“给 AI Agent 搭一个自托管检索网关”

Optional small subtitle:
“SearXNG · Docker · MCP · HTTPS”

Visual concept:
A clean futuristic command center / network gateway scene.
Several glowing AI agent nodes on the left flow into a central luminous gateway core.
From the gateway, clean data streams route to multiple search/provider nodes on the right.
The scene should imply:
AI Agents
MCP
Search Gateway
Self-hosted infrastructure
Secure HTTPS API
Provider routing

Composition:
Wide cinematic layout.
Central focus: a bright blue-green gateway core with a subtle search icon or shield-search symbol.
Left side: abstract agent nodes, not detailed logos.
Right side: abstract provider/search nodes, not detailed logos.
Bottom or background: subtle server racks, Docker/container blocks, network lines, and cloud/server hints.
Keep the title large and readable on mobile.

Style:
Modern AI infrastructure.
Premium SaaS / cyber engineering aesthetic.
Clean, bright, not dark.
Warm white to light blue background with blue, green, and amber accents.
Futuristic but credible.
No dense diagram.
No small text.
No fake screenshots.
No brand logos.
No complicated arrows.
No clutter.

Text requirements:
Only include the main title and optional subtitle.
Make all Chinese text clean, correct, and large.
Leave enough safe margin around all text so it will not be cropped in WeChat.

Mood:
Practical, technical, self-hosted, secure, future-facing.
Not marketing hype.
Not fantasy.
Not cyberpunk dark.
```
