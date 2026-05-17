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
“我给自己的 AI Agent 搭了一个自托管检索网关”

Subtitle:
“SearXNG + Docker + MCP 跑通真实调用”

Composition:
Left side: several AI agents labeled Cursor, Codex, Claude, OpenClaw, Hermes all pointing to a small warning card labeled “Tavily 免费额度”.
Center: a strong gateway block labeled “Agent Search Gateway”.
Right side: provider blocks labeled SearXNG, Tavily fallback, Brave optional, Jina Reader.
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

> 图 1：人类搜索看的是页面体验；agent 检索需要稳定结构、可抽取正文、可观测链路和错误处理。

Prompt:

```text
Create a Chinese comparison infographic for a WeChat technical article.

Title:
“人用搜索 ≠ Agent 用检索”

Canvas: 16:9 landscape, warm white background, clean vector style, mobile-readable.

Two-column comparison:

Left column title: “人类搜索”
Visuals: browser search box, blue links, human reading pages, clicking links.
Short labels:
搜索框
网页阅读
人工判断
反复改关键词

Right column title: “Agent 检索”
Visuals: API gateway, JSON card, URL list, extracted content block, provider_chain, errors.
Short labels:
稳定 API
JSON 结果
正文抽取
可观测
可重试

Middle: bold separator “不是一回事”.

Style:
Professional SaaS infographic, clear hierarchy, no paragraphs, no tiny text, no fake brand logos.
```

## Figure 2: Provider Gateway Map

Filename:

```text
fig-02-provider-gateway-map.png
```

Caption:

> 图 2：目标不是替换某一个厂商，而是把自托管和 hosted providers 收拢到一个统一入口。

Prompt:

```text
Create a Chinese architecture infographic.

Title:
“从单一 Tavily 依赖到 Provider Gateway”

Canvas: 16:9 landscape, warm white background, modern SaaS architecture diagram.

Left side:
A narrow funnel labeled “单一 hosted provider”.
Show Tavily with a quota warning icon labeled “额度压力”.

Right side:
A wide gateway architecture.
Top: agents labeled Cursor, Codex, Claude, OpenClaw, Hermes.
Middle: large block “Agent Search Gateway”.
Inside gateway show:
Provider Router
Extraction
Rerank
Cache
Fallback

Bottom provider row:
SearXNG 默认
Tavily 保底
Brave 预留
Jina Reader 可选
Crawl4AI 未来

Use arrows from agents to gateway to providers.
Highlight “SearXNG 默认” in green and “Tavily 保底” in amber.
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
“Agent Search Gateway 架构”

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
