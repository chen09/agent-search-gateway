# Agent Search Gateway

语言: [English](README.md) | [中文](README.zh.md) | [日本語](README.ja.md)

Agent Search Gateway 是一个给 AI agent 使用的自托管搜索和网页检索网关。它给 Cursor、ChatGPT Codex、MiniMax、DeepSeek 等 agent 提供一个稳定的 `/search` API，由网关统一处理 provider 路由、正文抽取、rerank、缓存和 fallback。

首版故意保持小而可运行，并且优先使用开源/自托管组件：SearXNG 做本地搜索，trafilatura 做本地正文抽取，可选 Jina Reader fallback，可选本地 CrossEncoder reranker。Tavily、Brave 这类 hosted API 只作为兼容或 fallback provider，不是 MVP 的默认依赖。

## 功能概览

```text
Agent 调用 search(query)
        ↓
Agent Search Gateway
        ↓
SearXNG 搜索
        ↓
trafilatura 或可选 Jina Reader 抽取正文
        ↓
本地 reranker
        ↓
统一 JSON 返回给 agent
```

当前 MVP 能力：

- 统一 `GET /search` 和 `POST /search` API。
- 本地 SearXNG 搜索后端。
- 可选 Tavily search/extract provider，带本地每日额度保护，默认关闭。
- 本地 trafilatura 文章正文抽取。
- 可选自托管或 hosted Jina Reader fallback。
- 可选 CrossEncoder reranking，独立依赖安装，基础网关不强制安装 PyTorch。
- 进程内搜索结果和正文抽取缓存。
- Tavily 兼容接口：`/tavily/search`、`/compat/tavily/search`、`/extract`、`/tavily/extract`、`/compat/tavily/extract`。
- Host-side MCP stdio server，可给 Cursor、Codex、Claude、OpenClaw、Hermes 等 MCP 客户端使用。
- 可安装的 `agent-search-gateway` skill。
- summary webhook 占位，后续可接 Cursor / Codex / MiniMax / DeepSeek。
- Docker Compose 部署。

暂未实现：

- Brave provider 和预算保护。
- Crawl/map/research APIs。
- 持久化共享缓存。
- 生产级 SSRF 防护。

## Provider 策略

网关不应该依赖单一搜索供应商。预期 provider 模型如下：

| Provider | 作用 | 默认状态 |
|---|---|---|
| SearXNG | 本地 fallback 搜索 | 启用 |
| trafilatura | 本地正文抽取 | 启用 |
| Jina Reader | 正文抽取 fallback | 可选 |
| Tavily | Hosted search/extract provider | 可选 fallback/兼容 provider，配置前关闭 |
| Brave Search | 可选付费/免费额度搜索 provider | 计划中，显式配置前关闭 |
| Crawl4AI | JS-heavy 页面抽取后端 | 计划中 |
| CRW / OrioSearch | 其他自托管后端 | 计划中 |

Hosted providers 默认不启用。Brave 和 Tavily 只有在 operator 明确配置 API key 和预算/额度策略后才应该使用。默认链路是 `searxng,tavily`，所以会先走自托管路线。

## 本地 Secret 和 `.env`

真实 key 只放在本地 `.env`。`.env` 已被 git 忽略；`.env.example` 只是模板。

最小设置：

```bash
cp .env.example .env
```

至少替换这两个必填值：

```dotenv
SEARXNG_SECRET=<generated-with-openssl-rand-hex-32>
RETRIEVAL_API_KEY=<generated-with-openssl-rand-hex-32>
```

Docker Compose 默认场景保持：

```dotenv
SEARXNG_BASE_URLS=http://searxng:8080
SEARXNG_HOST_PORT=8888
TAVILY_ENABLED=false
BRAVE_ENABLED=false
RERANKER_ENABLED=false
```

完整 `.env` 说明见 [docs/ENVIRONMENT.md](docs/ENVIRONMENT.md)，里面有 Docker Compose、本机 Python 开发、MCP 客户端、hosted provider keys、Jina Reader、可选 reranker 的示例。

如果只执行 `cp .env.example .env` 但不生成 `SEARXNG_SECRET` 和 `RETRIEVAL_API_KEY`，服务可能也能启动，但会使用公开模板 secret。这只适合快速本机试用，不适合长期运行或对外暴露。

如果你明确想用 Tavily 作为 hosted fallback 或兼容 provider，编辑 `.env`：

```dotenv
TAVILY_ENABLED=true
TAVILY_API_KEY=tvly-your-real-key
TAVILY_DAILY_CREDIT_LIMIT=50
TAVILY_SEARCH_DEPTH=basic
```

`TAVILY_DAILY_CREDIT_LIMIT` 是本地安全保护。网关会在请求前做保守估算，超过本地配置额度时 fallback，避免消耗过快。

如果后续实现原生 MiniMax 或 DeepSeek summarization，可以把 key 放在同一个 `.env`：

```dotenv
MINIMAX_API_KEY=
DEEPSEEK_API_KEY=
```

当前 summary 实现使用 `SUMMARY_WEBHOOK_URL`；还不会直接调用 MiniMax 或 DeepSeek。

## 快速启动

```bash
cd agent-search-gateway
cp .env.example .env
SEARXNG_SECRET="$(openssl rand -hex 32)" RETRIEVAL_API_KEY="$(openssl rand -hex 32)" \
  perl -0pi -e 's/^SEARXNG_SECRET=.*/SEARXNG_SECRET=$ENV{SEARXNG_SECRET}/m; s/^RETRIEVAL_API_KEY=.*/RETRIEVAL_API_KEY=$ENV{RETRIEVAL_API_KEY}/m' .env
docker compose up -d --build
```

健康检查：

```bash
curl http://127.0.0.1:8888/search?q=searxng\&format=json | head
curl http://127.0.0.1:8010/healthz
API_KEY="$(grep '^RETRIEVAL_API_KEY=' .env | cut -d= -f2-)"
curl -sS -H "Authorization: Bearer ${API_KEY}" \
  "http://127.0.0.1:8010/search?q=local%20AI%20search&max_results=3" | jq .
```

## 预构建 Docker 镜像

retrieval API 也可以直接使用 Docker Hub 镜像，而不是本地 build：

```bash
cd agent-search-gateway
cp .env.example .env
SEARXNG_SECRET="$(openssl rand -hex 32)" RETRIEVAL_API_KEY="$(openssl rand -hex 32)" \
  perl -0pi -e 's/^SEARXNG_SECRET=.*/SEARXNG_SECRET=$ENV{SEARXNG_SECRET}/m; s/^RETRIEVAL_API_KEY=.*/RETRIEVAL_API_KEY=$ENV{RETRIEVAL_API_KEY}/m' .env
docker compose -f docker-compose.image.yml up -d
```

默认镜像：

```text
docker.io/chen920/agent-search-gateway:latest
```

用户仍然必须自己提供 `.env`；镜像里不包含 API key 或 provider credentials。Docker Hub 发布和镜像部署说明见 [docs/DOCKER_HUB.md](docs/DOCKER_HUB.md)。

## Agent 客户端集成

Cursor、Codex、Claude、OpenClaw、Hermes 和类似 agent 推荐通过 MCP server 接入。MCP server 在 host 上运行，并调用 `http://127.0.0.1:8010` 的网关；它不会直接调用 SearXNG。

推荐 MCP config，使用 `uvx` 直接从 GitHub release 运行：

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
        "AGENT_SEARCH_GATEWAY_ENV_FILE": "/absolute/path/to/agent-search-gateway.env"
      }
    }
  }
}
```

如果这是你的私有本机配置，也可以直接把 key 写进 MCP 的 `env` block：

```json
{
  "env": {
    "AGENT_SEARCH_GATEWAY_URL": "https://api.agentsearchgateway.com",
    "AGENT_SEARCH_GATEWAY_API_KEY": "replace-with-your-gateway-api-key",
    "AGENT_SEARCH_GATEWAY_TIMEOUT": "90"
  }
}
```

如果是在 clone 下来的仓库里开发，再使用 [docs/integrations/agent-clients.md](docs/integrations/agent-clients.md) 里的本地 `.venv` 方式。
如果使用本地 Docker Compose 网关，`AGENT_SEARCH_GATEWAY_ENV_FILE` 可以直接指向 clone 仓库里的 `.env`。

MCP server 暴露：

- `agent_gateway_health`
- `agent_search`
- `agent_extract`

仓库也包含一个可选 agent skill：

```bash
mkdir -p ~/.agents/skills
cp -R skills/agent-search-gateway ~/.agents/skills/
```

Cursor、Codex、Claude、OpenClaw、Hermes 的配置步骤见 [docs/integrations/agent-clients.md](docs/integrations/agent-clients.md)。

启用自托管 Jina Reader 作为正文抽取 fallback：

```bash
cd agent-search-gateway
perl -0pi -e 's|^JINA_READER_BASE_URL=.*|JINA_READER_BASE_URL=http://jina-reader:8081|m' .env
docker compose --profile reader up -d --build
```

## API

GET：

```bash
curl -H "Authorization: Bearer ${API_KEY}" \
  "http://127.0.0.1:8010/search?q=your%20query&max_results=5&extract_top_k=3"
```

POST：

```bash
curl -sS -X POST http://127.0.0.1:8010/search \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer ${API_KEY}" \
  -d '{"query":"Tavily alternatives self hosted","max_results":5,"extract_top_k":3}' | jq .
```

响应结构：

```json
{
  "query": "string",
  "elapsed_ms": 1234,
  "provider_chain": ["searxng:searxng:8080"],
  "summary": "string",
  "results": [
    {
      "title": "string",
      "url": "https://example.com",
      "snippet": "string",
      "content": "clean extracted text",
      "score": 0.91,
      "source": "searxng:duckduckgo"
    }
  ],
  "errors": []
}
```

Fallback 行为：

1. 搜索按顺序尝试 `SEARXNG_BASE_URLS`。
2. 正文抽取先尝试本地 `trafilatura`，如果配置了 `JINA_READER_BASE_URL` 再尝试 Jina Reader。
3. 如果安装了可选依赖并设置 `RERANKER_ENABLED=true`，reranking 使用 CrossEncoder；否则 fallback 到 lexical matching。
4. 如果配置了 `SUMMARY_WEBHOOK_URL`，summary 会调用 webhook；否则返回短的 extractive placeholder。

默认 `PROVIDER_ORDER=searxng,tavily` 会先走自托管路径。Tavily 只有在显式启用、显式调整 provider 或调用 Tavily 兼容接口时才会使用；如果未启用、超本地额度、rate-limited 或不可用，会继续 fallback。

Tavily 兼容接口示例：

```bash
curl -sS -X POST http://127.0.0.1:8010/tavily/search \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer ${API_KEY}" \
  -d '{"query":"self hosted agent search gateway","max_results":5,"include_answer":true}' | jq .

curl -sS -X POST http://127.0.0.1:8010/extract \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer ${API_KEY}" \
  -d '{"urls":["https://example.com"],"extract_depth":"basic"}' | jq .
```

## Python venv 运行

```bash
cd agent-search-gateway
pyenv install 3.12.10  # 如果还没安装
pyenv local 3.12.10
python -m venv .venv
. .venv/bin/activate
pip install --upgrade pip
pip install -r api/requirements.txt
cp .env.example .env
export SEARXNG_BASE_URLS=http://127.0.0.1:8888
uvicorn api.main:app --host 127.0.0.1 --port 8010 --reload
```

## 可选 PyTorch Reranker

基础安装故意不安装 PyTorch。`sentence-transformers` 会拉取 `torch`，对 Mac mini 可能较重。不启用它时，网关仍然可以使用 lexical reranking。

启用本地 CrossEncoder reranking：

```bash
. .venv/bin/activate
pip install -r api/requirements-reranker.txt
```

然后编辑 `.env`：

```dotenv
RERANKER_ENABLED=true
RERANKER_DEVICE=mps
```

如果 MPS 不可用或对你的 workload 更慢，使用 `RERANKER_DEVICE=cpu`。本仓库使用 Python 3.12.10，作为较保守的依赖兼容选择。

## 运维说明

单用户部署：2 vCPU 和 4 GB RAM 可以运行 MVP；启用 reranking 时 8 GB RAM 更稳。第一次启动 reranker 会下载模型，需要网络。

从本地 MVP 到 provider routing、持久化 cache、hardening 和 agent integration 的路线见 [docs/ROADMAP.md](docs/ROADMAP.md)。

并发上升后的主要瓶颈：

- 上游 SearXNG engines 和 rate limits。
- 网页 fetch latency。
- CPU reranker inference。
- 重复抽取同一批 URL。

推荐后续优化：

- 缓存搜索结果和 URL 正文。
- 限制 `extract_top_k`。
- 增加 provider-level quota guards。
- 对可信本地网络之外暴露 API 前增加 SSRF 防护。

## 安全

- 默认绑定到 `127.0.0.1`。
- 非本地使用时保持 `RETRIEVAL_API_KEY` 启用。
- 公网部署前放在 Caddy、Nginx、Cloudflare Tunnel 或 Cloudflare Access 后面。
- 不要记录 API keys、cookies、完整 authorization headers 或敏感 query parameters。
- 不要把 hosted provider keys 直接交给 agents；通过这个带 quota/fallback 的 gateway 路由。

## Troubleshooting

1. SearXNG 返回 `403 Forbidden`：确认 `searxng/settings.yml` 的 `search.formats` 包含 `json`，然后重启 SearXNG。
2. 网关返回 `401`：发送 `Authorization: Bearer ${RETRIEVAL_API_KEY}` 或 `X-API-Key`。
3. 第一次搜索很慢：可能在下载 reranker 模型；设置 `RERANKER_ENABLED=false` 快速测试。
4. 正文抽取为空：页面可能阻止 bot 或需要 JavaScript；可配置 Jina Reader，后续也可以加 Crawl4AI。
5. 没有搜索结果：上游 engine 可能 rate-limited；降低请求频率或配置更多 SearXNG 实例。
6. 内存不足：降低 `EXTRACT_TOP_K`，关闭 reranking，或使用更小的 reranker model。

## License

Agent Search Gateway 使用 [Apache License 2.0](LICENSE)。

第三方组件保留各自 upstream license。见 [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md)。
