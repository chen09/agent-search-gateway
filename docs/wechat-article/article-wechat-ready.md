# 给自己的 AI Agent 搭了一个自托管检索网关

![头图：给 AI Agent 用的自托管检索网关](./images/fig-00-hero-agent-search-gateway.png)

这篇不是产品发布，也不是教程合集。

起因很简单：最近我让 Cursor、Codex、Claude、OpenClaw、Hermes 这些 agent 查资料，发现如果都走 Tavily，免费额度很快就不够用。

一开始我只是想找一个便宜一点、最好能自托管的替代方案。

但做着做着，目标变清楚了：我真正需要的不是一个 Tavily clone，而是一个统一的检索网关。

它要做的事情也很朴素：给所有 agent 一个统一入口。

默认先走自托管 SearXNG，必要时再 fallback 到 Tavily。

将来如果要接 Brave、Firecrawl、Crawl4AI 或其他后端，也都收在同一个 gateway 后面。

这次最后跑通的也不是一个玩具搜索接口。

而是一条完整链路：程序、Docker、CI/CD、Docker Hub、云服务器、域名、HTTPS、MCP、Cursor Rules。

到这一步，它才算从一个本地脚本，变成了能被真实 agent 调用的自托管检索基础设施。

这条链路包括：

- Python API
- Docker Compose
- Docker Hub 发布
- GitHub Actions CI/CD
- 云服务器 Docker 部署
- Nginx 反代
- 域名
- Let’s Encrypt 免费证书
- MCP
- Cursor User Rules
- Cursor 自动调用自托管检索

项目仓库：

GitHub：chen09 / agent-search-gateway

Docker Hub：chen920 / agent-search-gateway

## 为什么 Agent 需要专门的检索工具

这里有一个我之前没想清楚的问题：

**为什么 agent 需要 Tavily 这种检索 API？直接 Google 搜索不行吗？Perplexity 不也能查资料吗？**

调研之后，我的理解变了。

不是 Google、Perplexity 没用，而是它们和 agent 检索工具解决的问题不一样。

没有这类工具，agent 当然也能干活。

写本地代码、解释已有文件、根据你贴进来的资料做总结，这些都没问题。

但一旦任务变成“查一下现在最新是什么”“对比几份官方文档”“抓这个 URL 的正文再分析”“给我带来源的结论”，只靠模型记忆就不够了。

这时 agent 需要的不是一个漂亮搜索框，而是一套可以被程序调用的检索工具。

Google 更像人的搜索入口。

人会看搜索结果、点开页面、扫正文、判断哪个来源可信，然后不断调整关键词。

Google 也有 Programmable Search / Custom Search JSON API，但它主要还是返回搜索结果和元数据。

对 agent 来说，这只是第一步。

后面还要处理正文抽取、噪声过滤、上下文长度、来源保留、失败重试，这些都要自己补。

Perplexity 更像答案引擎。

它适合人直接问问题，然后拿到一个整理过的答案和引用。

现在 Perplexity 也有 Search API，可以返回 ranked results、domain filtering、multi-query search、content extraction。

这说明“AI search API”这个方向本身是成立的。

但从自托管 agent 基础设施的角度看，它仍然是一个 hosted provider。

如果每个 agent 都直接接一个外部 provider，key、额度、成本、日志、失败策略都会散在各个客户端里。

Tavily 这类工具更接近 agent 的工具层。

它不是给人看的搜索页面，而是给程序用的能力组合：search、extract、crawl、rank、filter，把结果整理成 agent 能消费的结构。

这就是它必要的地方。

有了这样的检索层，agent 就可以把调研拆成几步：

- 先搜索候选来源
- 再抽取干净正文
- 再比对多个来源
- 再把结论和 URL 一起返回
- 失败时换 provider 或重试

所以我现在的判断是：

**Tavily 这类工具不是“可有可无的搜索替代品”，而是 agent 想认真做外部调研时需要的工具层。**

它解决的不是“能不能搜到网页”，而是“agent 能不能稳定、可控、可观测地使用网页信息”。

这也是为什么这个项目最后没有做成一个简单搜索代理，而是做成 gateway。

agent 检索层至少要考虑：

- 稳定 API
- JSON 结果
- 来源 URL
- 摘要和正文抽取
- 错误信息
- 成本和额度控制
- 可重试
- 可 fallback
- 可观测

商业检索 API 的存在，反而说明这个需求是真实的。

只是如果每天多个 agent 都要用，额度、成本和可控性就会变成自己的问题。

![图 1：Google、Perplexity 和 Tavily 在检索链路里的位置](./images/fig-01-human-search-vs-agent-retrieval.png)

图 1：Google 更像人的搜索入口，Perplexity 更像答案引擎，Tavily 这类服务更接近 agent 的检索工具层。

## 竞品调研之后，目标变成了 Gateway

我看了几个方向。

Tavily 很适合 AI agent。官方文档里，它有 Search、Extract、Map、Crawl，并且是 credit-based 计费。免费额度可以开始用，但不是无限用。

Brave Search API 有自己的搜索索引，也明确面向 AI apps。它很有吸引力，但仍然要考虑费用、速率和预算。

Firecrawl 更偏抓取、抽取、爬取、动态页面处理。它适合复杂页面，但不是首版必须依赖。

Perplexity Search API 则更能说明一件事：AI 时代的 search API 不只是关键词搜索，而是要给开发者提供 ranked results、过滤、抽取和实时网页数据。

所以项目目标变成：

**不要把某一个 provider 当成唯一答案，而是做一个 provider router。**

也就是说：

- SearXNG 做默认自托管 search provider
- trafilatura 做本地正文抽取
- Jina Reader 做可选 fallback
- Tavily 做兼容/保底 provider
- Brave 先预留，等预算保护做好后再启用
- 后续再考虑 Crawl4AI 或 Firecrawl 类能力

![图 2：Agent Search Gateway 的整体链路](./images/fig-02-provider-gateway-map.png)

图 2：Cursor、Codex、Claude、OpenClaw、Hermes 通过 MCP 接入同一个公网 API；服务器侧再统一路由到 SearXNG、Tavily 兜底和其他 provider。

## 这个 Gateway 到底做什么

现在的 Agent Search Gateway 提供一个统一 API：

```text
GET /search
POST /search
POST /extract
```

返回统一 JSON：

```json
{
  "query": "string",
  "elapsed_ms": 1234,
  "provider_chain": ["searxng:searxng:8080"],
  "summary": "string",
  "results": [],
  "errors": []
}
```

这里最重要的是两个字段：

```text
provider_chain
errors
```

agent 不只是拿到结果，还能知道这次到底走了哪个 provider，有没有 fallback，有没有失败。

这比“给我几个搜索结果”更适合工程化。

![图 3：Agent Search Gateway 内部架构图](./images/fig-03-gateway-architecture.png)

图 3：agent 只面对一个 gateway；gateway 负责 provider routing、正文抽取、缓存、rerank 和 fallback。

## 技术栈：小而完整

首版我故意没有做大。

但“小”不等于只做半截。

这个项目的完整性在于，它把一个 agent tool 真正需要的几层都接上了：

- 程序层：统一 search / extract API
- provider 层：SearXNG 优先，Tavily/Brave/Jina 预留
- 抽取层：trafilatura + 可选 Jina Reader
- 运行层：Docker Compose
- 发布层：GitHub Actions + Docker Hub
- 部署层：Ubuntu server + Nginx + Let’s Encrypt
- 接入层：MCP + Rules / Skills

后端用 Python + FastAPI。

搜索默认走 SearXNG。

正文抽取用 trafilatura。

缓存先用进程内 TTL cache。

Valkey 已经在 Docker Compose 里，后面可以升级成共享缓存。

reranker 做成可选能力，默认不影响基础部署。

部署用 Docker Compose。

发布用 GitHub Actions 自动推 Docker Hub。

公网服务用 Ubuntu server + Docker + Nginx + Let’s Encrypt。

域名用：

```text
api.agentsearchgateway.com
```

root domain 以后可以做文档站或 landing page。

![图 4：从代码到公网 API 的全栈链路](./images/fig-04-full-stack-deployment.png)

图 4：从程序到 Docker、CI/CD、Docker Hub、云服务器、Nginx、HTTPS、域名和 MCP，全部打通成一条完整链路。

## Secrets 边界：provider key 不给 agent

这个项目里有一个很重要的边界：

**agent 不应该直接拿 Tavily、Brave、Jina、MiniMax、DeepSeek 这些 provider key。**

provider key 只放在服务器的 `.env`。

agent 只拿 gateway 的访问 key。

也就是说，服务器 `.env` 放：

```text
RETRIEVAL_API_KEY
TAVILY_API_KEY
BRAVE_API_KEY
JINA_API_KEY
MINIMAX_API_KEY
DEEPSEEK_API_KEY
```

MCP client config 只放：

```text
AGENT_SEARCH_GATEWAY_URL
AGENT_SEARCH_GATEWAY_API_KEY
AGENT_SEARCH_GATEWAY_TIMEOUT
```

这样做有几个好处。

第一，provider key 不会散落到各个 agent 配置里。

第二，切换 provider 不需要改每个 agent。

第三，额度保护可以放在 gateway 层统一做。

第四，后续做限流、审计、缓存、fallback，都有一个统一入口。

![图 5：Secrets 边界](./images/fig-05-secret-boundary.png)

图 5：agent 只拿 gateway key；真正的 provider keys 留在服务器上，由 gateway 控制。

## MCP：让 Cursor / Codex / Claude / OpenClaw / Hermes 都能用

为了让 agent 真正用上这个 gateway，我做了 MCP server。

现在 MCP 可以用 `uvx` 直接从 GitHub 跑。

微信正文里不贴完整外链，下面是简化示意；可复制版本放在 GitHub README 里。

```json
{
  "mcpServers": {
    "agent-search-gateway": {
      "command": "uvx",
      "args": [
        "--from",
        "git+GitHub repo @ v0.2.2",
        "agent-search-gateway-mcp"
      ],
      "env": {
        "AGENT_SEARCH_GATEWAY_URL": "api.agentsearchgateway.com",
        "AGENT_SEARCH_GATEWAY_API_KEY": "replace-with-your-key",
        "AGENT_SEARCH_GATEWAY_TIMEOUT": "90"
      }
    }
  }
}
```

MCP 暴露 3 个 tools：

```text
agent_gateway_health
agent_search
agent_extract
```

这样 Cursor、Codex、Claude、OpenClaw、Hermes 都可以接同一个检索网关。

当前 Cursor 已经完成真实检索验证，Codex 里也已经配置了同一个 `agent-search-gateway` MCP。

Claude、OpenClaw、Hermes 走的是同一类 MCP 配置，不需要把 Tavily、Brave 这些 provider key 下发给每个客户端。

注意：MCP 只是让工具可用，不保证 agent 每次都会主动用。

所以我还准备了 Cursor User Rule。

Cursor 的 User Rules GitHub/GitLab import 里，选择这个仓库：

```text
chen09 / agent-search-gateway
```

不要填 `blob/...mdc` 文件 URL。Cursor 实际会 clone repo。

可复用 rule 文件在：

```text
rules/agent-search-gateway-user-rule.mdc
```

![图 6：Agent 客户端接入图](./images/fig-06-agent-client-integration.png)

图 6：MCP 负责工具接入，User Rule / Skill 负责告诉 agent 什么时候应该用。

## 真实验证：Cursor 已经自动走了我们的 Gateway

最关键的一步，不是“我配好了 MCP”。

而是 Cursor 在普通研究任务里真的调用了它。

同时，Codex 里也已经接入同一个 MCP。这个项目开始变成一个多 agent 共用的检索层，而不是 Cursor 专用插件。

先看到 health：

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
  "searxng_base_urls": ["searxng:8080"]
}
```

然后在几次检索里看到了：

```text
provider_chain: ["searxng:searxng:8080"]
errors: []
```

这说明链路已经跑通：

```text
Cursor User Rule
  -> Cursor Agent 自动选择 MCP
  -> agent-search-gateway MCP
  -> api.agentsearchgateway.com
  -> retrieval-api 0.2.2
  -> SearXNG
  -> provider_chain / results / errors 返回 Cursor
```

这也是我最满意的地方。

不是做了一个 demo，也不是只把 Docker 跑起来。

而是一个从公网 API 到 MCP tool，再到 Cursor 自动选择工具的闭环已经真实发生。

程序可运行，镜像可分发，服务器可访问，证书可用，agent 可调用，调用证据可观测。

![图 7：验证结果仪表盘](./images/fig-07-validation-dashboard.png)

图 7：provider_chain 明确显示走的是自托管 SearXNG，而不是 Tavily 或 Cursor 内置搜索。

## 这件事为什么只用了一天

这个项目从空仓库到公网可用，只用了大约一天。

代码、Docker、CI/CD、Docker Hub、域名、Nginx、HTTPS、MCP、Cursor Rule、文档，基本都是通过 AI 完成的。

这次主要是 Codex，GPT-5.5，单 agent 贯穿到底。

这件事值得记录，是因为一天内完成的不是某个孤立功能，而是从想法到可用服务的完整交付链路。

写代码只是其中一部分。

服务能不能跑，镜像能不能发，域名和 HTTPS 能不能通，MCP 能不能接上，Cursor 是否真的会调用，这些都被验证之后，它才从“代码仓库”变成了“可以被 agent 使用的检索基础设施”。

![图 8：一天完成的 Vibe Coding 全栈路线](./images/fig-08-one-day-vibe-coding-roadmap.png)

图 8：一天内完成的不是单点功能，而是一条从想法到公网服务、再到 agent 自动调用的完整链路。

## 它还不是生产级

现在这个项目能用，但我不会说它已经生产级。

还需要继续做：

- SSRF 防护
- per-client rate limit
- request size limit
- Docker healthcheck
- provider timeout budget
- circuit breaker
- Valkey 持久缓存
- 结构化脱敏日志
- 更多 provider 的健康检查
- 更完整的 CI 测试
- root domain 的文档站或状态页

![图 9：从 MVP 到生产级 Gateway 的优化路线](./images/fig-09-production-hardening-roadmap.png)

图 9：现在已经跑通完整闭环；下一阶段要补的是安全、限流、缓存、观测和 provider 健康治理。

但这不影响它当前的价值。

它已经证明了一件事：

**一个自托管、开源优先、可 fallback 的 agent search gateway，是完全可行的。**

## 我的结论

这次项目最大的收获，不是省下 Tavily 的一点额度。

而是我真正理解了 AI agent 为什么需要检索 API。

也理解了为什么单一 provider 不够。

一个好的 agent 检索层，应该有统一入口、可观测链路、provider routing、fallback、缓存、限流和安全边界。

这就是 Agent Search Gateway 的价值。

它不是替代某个工具。

它是把这些工具收拢起来，变成自己的基础设施。

完整项目在这里：

GitHub：chen09 / agent-search-gateway

Docker Hub：

```text
chen920 / agent-search-gateway
```

Docker image name：

```text
docker.io/chen920/agent-search-gateway:0.2.2
```

公网 API：

```text
api.agentsearchgateway.com
```

## 参考资料

微信正文里不贴外链。资料来源可以按下面这些名称搜索：

- Tavily Credits & Pricing
- Tavily API Reference
- Tavily FAQ
- Google Custom Search JSON API
- Brave Search API
- Firecrawl Billing
- Perplexity Search API
- Perplexity API Pricing
- SearXNG Documentation
- SearXNG Search API
- SearXNG Limiter
- Cursor Rules
