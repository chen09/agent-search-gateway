# Agent Search Gateway

Languages: English | 中文 | 日本語

Self-hosted search and extraction gateway for AI agents. This image runs the `retrieval-api` service. Use the provided Docker Compose file to run it together with SearXNG and Valkey.

自托管的 AI agent 搜索与正文抽取网关。这个镜像运行 `retrieval-api` 服务。请配合仓库里的 Docker Compose 文件一起使用，它会同时启动 SearXNG 和 Valkey。

AI agent 向けのセルフホスト検索・本文抽出ゲートウェイです。この image は `retrieval-api` service を実行します。SearXNG と Valkey も含めて起動するため、GitHub repo の Docker Compose file と一緒に使ってください。

Source and full documentation:

- GitHub: https://github.com/chen09/agent-search-gateway
- English README: https://github.com/chen09/agent-search-gateway/blob/main/README.md
- 中文 README: https://github.com/chen09/agent-search-gateway/blob/main/README.zh.md
- 日本語 README: https://github.com/chen09/agent-search-gateway/blob/main/README.ja.md
- Environment guide: https://github.com/chen09/agent-search-gateway/blob/main/docs/ENVIRONMENT.md
- Agent client setup: https://github.com/chen09/agent-search-gateway/blob/main/docs/integrations/agent-clients.md

## English

### イメージタグ

```text
docker.io/chen920/agent-search-gateway:latest
docker.io/chen920/agent-search-gateway:0.2
docker.io/chen920/agent-search-gateway:0.2.2
```

Published platforms:

- `linux/amd64`
- `linux/arm64`

### Quick Start

Clone the repo so you also get the SearXNG config and Compose files:

```bash
git clone https://github.com/chen09/agent-search-gateway.git
cd agent-search-gateway
cp .env.example .env
```

Generate the two required local secrets:

```bash
SEARXNG_SECRET="$(openssl rand -hex 32)" RETRIEVAL_API_KEY="$(openssl rand -hex 32)" \
  perl -0pi -e 's/^SEARXNG_SECRET=.*/SEARXNG_SECRET=$ENV{SEARXNG_SECRET}/m; s/^RETRIEVAL_API_KEY=.*/RETRIEVAL_API_KEY=$ENV{RETRIEVAL_API_KEY}/m' .env
```

Start the stack with the prebuilt Docker Hub image:

```bash
docker compose -f docker-compose.image.yml up -d
```

Verify:

```bash
curl http://127.0.0.1:8010/healthz
curl 'http://127.0.0.1:8888/search?q=searxng&format=json' | head
```

### Required `.env`

Users must create `.env` before running Compose because the stack loads it with `env_file`.

The values that must be unique per install are:

```dotenv
SEARXNG_SECRET=<generated-random-hex>
RETRIEVAL_API_KEY=<generated-random-hex>
```

Keep these defaults for Docker Compose:

```dotenv
SEARXNG_BASE_URLS=http://searxng:8080
SEARXNG_HOST_PORT=8888
PROVIDER_ORDER=searxng,tavily
TAVILY_ENABLED=false
BRAVE_ENABLED=false
RERANKER_ENABLED=false
CACHE_ENABLED=true
```

If a user only runs `cp .env.example .env`, the stack may start, but it uses public placeholder secrets. That is acceptable only for a quick local test. Generate real secrets before using the gateway long term or exposing it beyond localhost.

Hosted provider keys are optional. Tavily, Brave, MiniMax, and DeepSeek are not required for the default route. The default route is SearXNG plus local extraction.

### API

Gateway:

```text
http://127.0.0.1:8010
```

SearXNG:

```text
http://127.0.0.1:8888
```

Search example:

```bash
API_KEY="$(grep '^RETRIEVAL_API_KEY=' .env | cut -d= -f2-)"
curl -sS -H "Authorization: Bearer ${API_KEY}" \
  "http://127.0.0.1:8010/search?q=self%20hosted%20agent%20search&max_results=3"
```

### Agent Clients

Cursor, Codex, Claude, OpenClaw, Hermes, and other MCP-capable agents should use the MCP server from the GitHub repo:

```text
Command: uvx
Args: --from git+https://github.com/chen09/agent-search-gateway.git@v0.2.2 agent-search-gateway-mcp
Env:
  AGENT_SEARCH_GATEWAY_ENV_FILE=/absolute/path/to/agent-search-gateway.env
```

The env file should contain `AGENT_SEARCH_GATEWAY_URL` and either `AGENT_SEARCH_GATEWAY_API_KEY` for a remote gateway or `RETRIEVAL_API_KEY` for a local gateway.

`AGENT_SEARCH_GATEWAY_API_KEY` is the value of `RETRIEVAL_API_KEY` from the gateway `.env`.

For local Docker Compose:

```bash
grep '^RETRIEVAL_API_KEY=' .env | cut -d= -f2-
```

For a remote Ubuntu server:

```bash
ssh ubuntu@your-server
cd ~/agent-search-gateway
grep '^RETRIEVAL_API_KEY=' .env | cut -d= -f2-
```

To rotate it:

```bash
NEW_KEY="$(openssl rand -hex 32)" \
  perl -0pi -e 's/^RETRIEVAL_API_KEY=.*/RETRIEVAL_API_KEY=$ENV{NEW_KEY}/m' .env
docker compose up -d retrieval-api
```

After rotating, update every MCP client config that uses the old key.

MCP tools:

- `agent_gateway_health`
- `agent_search`
- `agent_extract`

### Secret Policy

The image does not contain `.env`, API keys, provider keys, logs, extracted content, or caches.

Do not commit:

- `.env`
- `.env.bak-*`
- Docker Hub tokens
- hosted provider API keys

### License

Agent Search Gateway is licensed under the Apache License 2.0.

Third-party components keep their own upstream licenses. See the GitHub repository's `THIRD_PARTY_NOTICES.md`.

## 中文

### 镜像 Tag

```text
docker.io/chen920/agent-search-gateway:latest
docker.io/chen920/agent-search-gateway:0.2
docker.io/chen920/agent-search-gateway:0.2.2
```

已发布平台：

- `linux/amd64`
- `linux/arm64`

### 快速启动

先 clone GitHub 仓库，这样可以拿到 SearXNG 配置和 Compose 文件：

```bash
git clone https://github.com/chen09/agent-search-gateway.git
cd agent-search-gateway
cp .env.example .env
```

生成两个必填的本地 secret：

```bash
SEARXNG_SECRET="$(openssl rand -hex 32)" RETRIEVAL_API_KEY="$(openssl rand -hex 32)" \
  perl -0pi -e 's/^SEARXNG_SECRET=.*/SEARXNG_SECRET=$ENV{SEARXNG_SECRET}/m; s/^RETRIEVAL_API_KEY=.*/RETRIEVAL_API_KEY=$ENV{RETRIEVAL_API_KEY}/m' .env
```

使用 Docker Hub 预构建镜像启动：

```bash
docker compose -f docker-compose.image.yml up -d
```

验证：

```bash
curl http://127.0.0.1:8010/healthz
curl 'http://127.0.0.1:8888/search?q=searxng&format=json' | head
```

### 必需的 `.env`

Compose 会通过 `env_file` 读取 `.env`，所以运行前必须创建 `.env`。

每个安装环境都应该唯一生成的值：

```dotenv
SEARXNG_SECRET=<generated-random-hex>
RETRIEVAL_API_KEY=<generated-random-hex>
```

Docker Compose 场景保持这些默认值：

```dotenv
SEARXNG_BASE_URLS=http://searxng:8080
SEARXNG_HOST_PORT=8888
PROVIDER_ORDER=searxng,tavily
TAVILY_ENABLED=false
BRAVE_ENABLED=false
RERANKER_ENABLED=false
CACHE_ENABLED=true
```

如果只执行 `cp .env.example .env`，服务可能也能启动，但会使用公开模板 secret。这只适合快速本机测试。长期使用或对 localhost 之外暴露前，请一定生成真实 secret。

Hosted provider keys 是可选的。默认路线不需要 Tavily、Brave、MiniMax、DeepSeek。默认路线是 SearXNG + 本地正文抽取。

### API

Gateway：

```text
http://127.0.0.1:8010
```

SearXNG：

```text
http://127.0.0.1:8888
```

搜索示例：

```bash
API_KEY="$(grep '^RETRIEVAL_API_KEY=' .env | cut -d= -f2-)"
curl -sS -H "Authorization: Bearer ${API_KEY}" \
  "http://127.0.0.1:8010/search?q=self%20hosted%20agent%20search&max_results=3"
```

### Agent 客户端

Cursor、Codex、Claude、OpenClaw、Hermes 和其他支持 MCP 的 agent，推荐使用 GitHub 仓库里的 MCP server：

```text
Command: uvx
Args: --from git+https://github.com/chen09/agent-search-gateway.git@v0.2.2 agent-search-gateway-mcp
Env:
  AGENT_SEARCH_GATEWAY_ENV_FILE=/absolute/path/to/agent-search-gateway.env
```

这个 env 文件里应包含 `AGENT_SEARCH_GATEWAY_URL`，以及远程网关使用的 `AGENT_SEARCH_GATEWAY_API_KEY`，或本地网关使用的 `RETRIEVAL_API_KEY`。

`AGENT_SEARCH_GATEWAY_API_KEY` 的值，就是网关 `.env` 里的 `RETRIEVAL_API_KEY`。

本地 Docker Compose：

```bash
grep '^RETRIEVAL_API_KEY=' .env | cut -d= -f2-
```

远程 Ubuntu server：

```bash
ssh ubuntu@your-server
cd ~/agent-search-gateway
grep '^RETRIEVAL_API_KEY=' .env | cut -d= -f2-
```

轮换 key：

```bash
NEW_KEY="$(openssl rand -hex 32)" \
  perl -0pi -e 's/^RETRIEVAL_API_KEY=.*/RETRIEVAL_API_KEY=$ENV{NEW_KEY}/m' .env
docker compose up -d retrieval-api
```

轮换后，需要更新所有仍在使用旧 key 的 MCP client config。

MCP tools：

- `agent_gateway_health`
- `agent_search`
- `agent_extract`

### Secret 策略

镜像不包含 `.env`、API key、provider key、日志、抽取正文或缓存。

不要提交：

- `.env`
- `.env.bak-*`
- Docker Hub tokens
- hosted provider API keys

### License

Agent Search Gateway 使用 Apache License 2.0。

第三方组件保留各自 upstream license。请查看 GitHub 仓库里的 `THIRD_PARTY_NOTICES.md`。

## 日本語

### Image Tags

```text
docker.io/chen920/agent-search-gateway:latest
docker.io/chen920/agent-search-gateway:0.2
docker.io/chen920/agent-search-gateway:0.2.2
```

公開プラットフォーム：

- `linux/amd64`
- `linux/arm64`

### クイックスタート

SearXNG config と Compose files も必要なので、まず GitHub repo を clone してください。

```bash
git clone https://github.com/chen09/agent-search-gateway.git
cd agent-search-gateway
cp .env.example .env
```

必須の local secrets を 2 つ生成します。

```bash
SEARXNG_SECRET="$(openssl rand -hex 32)" RETRIEVAL_API_KEY="$(openssl rand -hex 32)" \
  perl -0pi -e 's/^SEARXNG_SECRET=.*/SEARXNG_SECRET=$ENV{SEARXNG_SECRET}/m; s/^RETRIEVAL_API_KEY=.*/RETRIEVAL_API_KEY=$ENV{RETRIEVAL_API_KEY}/m' .env
```

Docker Hub の prebuilt image で stack を起動します。

```bash
docker compose -f docker-compose.image.yml up -d
```

確認：

```bash
curl http://127.0.0.1:8010/healthz
curl 'http://127.0.0.1:8888/search?q=searxng&format=json' | head
```

### 必須の `.env`

Compose は `env_file` で `.env` を読み込むため、起動前に `.env` を作成する必要があります。

インストールごとに unique にするべき値：

```dotenv
SEARXNG_SECRET=<generated-random-hex>
RETRIEVAL_API_KEY=<generated-random-hex>
```

Docker Compose では以下の defaults を維持してください。

```dotenv
SEARXNG_BASE_URLS=http://searxng:8080
SEARXNG_HOST_PORT=8888
PROVIDER_ORDER=searxng,tavily
TAVILY_ENABLED=false
BRAVE_ENABLED=false
RERANKER_ENABLED=false
CACHE_ENABLED=true
```

`cp .env.example .env` だけでも stack が起動する場合がありますが、公開テンプレート secret を使うことになります。短時間の local test だけにしてください。長期利用、または localhost 以外へ公開する前に必ず real secrets を生成してください。

Hosted provider keys は任意です。デフォルト route では Tavily、Brave、MiniMax、DeepSeek は不要です。デフォルト route は SearXNG + local extraction です。

### API

Gateway：

```text
http://127.0.0.1:8010
```

SearXNG：

```text
http://127.0.0.1:8888
```

Search example：

```bash
API_KEY="$(grep '^RETRIEVAL_API_KEY=' .env | cut -d= -f2-)"
curl -sS -H "Authorization: Bearer ${API_KEY}" \
  "http://127.0.0.1:8010/search?q=self%20hosted%20agent%20search&max_results=3"
```

### Agent クライアント

Cursor、Codex、Claude、OpenClaw、Hermes などの MCP-capable agents は、GitHub repo の MCP server を使うのが推奨です。

```text
Command: uvx
Args: --from git+https://github.com/chen09/agent-search-gateway.git@v0.2.2 agent-search-gateway-mcp
Env:
  AGENT_SEARCH_GATEWAY_ENV_FILE=/absolute/path/to/agent-search-gateway.env
```

この env file には `AGENT_SEARCH_GATEWAY_URL` と、remote gateway 用の `AGENT_SEARCH_GATEWAY_API_KEY` または local gateway 用の `RETRIEVAL_API_KEY` を入れてください。

`AGENT_SEARCH_GATEWAY_API_KEY` には、gateway `.env` の `RETRIEVAL_API_KEY` の値を使います。

Local Docker Compose：

```bash
grep '^RETRIEVAL_API_KEY=' .env | cut -d= -f2-
```

Remote Ubuntu server：

```bash
ssh ubuntu@your-server
cd ~/agent-search-gateway
grep '^RETRIEVAL_API_KEY=' .env | cut -d= -f2-
```

Key rotation：

```bash
NEW_KEY="$(openssl rand -hex 32)" \
  perl -0pi -e 's/^RETRIEVAL_API_KEY=.*/RETRIEVAL_API_KEY=$ENV{NEW_KEY}/m' .env
docker compose up -d retrieval-api
```

Rotation 後、古い key を使っているすべての MCP client config を更新してください。

MCP tools：

- `agent_gateway_health`
- `agent_search`
- `agent_extract`

### Secret Policy

Image には `.env`、API keys、provider keys、logs、extracted content、cache は含まれません。

Commit しないでください：

- `.env`
- `.env.bak-*`
- Docker Hub tokens
- hosted provider API keys

### License

Agent Search Gateway は Apache License 2.0 で提供されます。

Third-party components はそれぞれの upstream license に従います。GitHub repository の `THIRD_PARTY_NOTICES.md` を参照してください。
