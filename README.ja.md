# Agent Search Gateway

言語: [English](README.md) | [中文](README.zh.md) | [日本語](README.ja.md)

Agent Search Gateway は、AI agent 向けのセルフホスト可能な検索・Web 取得ゲートウェイです。Cursor、ChatGPT Codex、MiniMax、DeepSeek などの agent に安定した `/search` API を提供し、provider routing、本文抽出、rerank、cache、fallback をゲートウェイ側でまとめて扱います。

初期版は意図的に小さく、オープンソース優先で構成しています。ローカル検索に SearXNG、本文抽出に trafilatura、必要に応じて Jina Reader fallback、任意でローカル CrossEncoder reranker を使います。Tavily や Brave などの hosted API は互換性または fallback 用であり、MVP の必須依存ではありません。

## できること

```text
Agent が search(query) を呼ぶ
        ↓
Agent Search Gateway
        ↓
SearXNG search
        ↓
trafilatura または任意の Jina Reader で本文抽出
        ↓
local reranker
        ↓
統一 JSON を agent に返す
```

現在の MVP 機能：

- 統一 `GET /search` / `POST /search` API。
- ローカル SearXNG search backend。
- 任意の Tavily search/extract provider。ローカルの日次 credit guard 付きで、明示設定するまで無効。
- ローカル trafilatura article extraction。
- 任意の self-hosted / hosted Jina Reader fallback。
- 任意の CrossEncoder reranking。PyTorch を base gateway に含めないため、依存関係は別にインストール。
- プロセス内 search response / extracted content cache。
- Tavily 互換 adapter：`/tavily/search`、`/compat/tavily/search`、`/extract`、`/tavily/extract`、`/compat/tavily/extract`。
- Cursor、Codex、Claude、OpenClaw、Hermes などの MCP client 向け host-side MCP stdio server。
- agent が使える `agent-search-gateway` skill。
- 後続の Cursor / Codex / MiniMax / DeepSeek 連携用 summary webhook placeholder。
- Docker Compose deployment。

未実装：

- Brave provider と budget guard。
- Crawl/map/research APIs。
- 永続化された共有 cache。
- 本番向け SSRF protection。

## Provider 方針

この gateway は単一の検索 vendor に依存しない設計です。想定している provider model は以下です。

| Provider | 役割 | デフォルト状態 |
|---|---|---|
| SearXNG | ローカル fallback search | 有効 |
| trafilatura | ローカル extraction | 有効 |
| Jina Reader | extraction fallback | 任意 |
| Tavily | hosted search/extract provider | 任意 fallback/compatibility provider。設定するまで無効 |
| Brave Search | 任意の paid/free-credit search provider | 予定。明示設定するまで無効 |
| Crawl4AI | JS-heavy page extraction backend | 予定 |
| CRW / OrioSearch | 代替 self-hosted backend | 予定 |

Hosted providers はデフォルトでは有効にしません。Brave と Tavily は、operator が API key と budget/quota policy を明示的に設定した場合だけ使う想定です。デフォルト chain は `searxng,tavily` なので、まず self-hosted route が試されます。

## ローカル Secret と `.env`

実 key はローカル `.env` にだけ置きます。`.env` は git ignore 済みです。`.env.example` はテンプレートです。

最小セットアップ：

```bash
cp .env.example .env
```

最低限、この 2 つを置き換えてください。

```dotenv
SEARXNG_SECRET=<generated-with-openssl-rand-hex-32>
RETRIEVAL_API_KEY=<generated-with-openssl-rand-hex-32>
```

Docker Compose では以下を維持します。

```dotenv
SEARXNG_BASE_URLS=http://searxng:8080
SEARXNG_HOST_PORT=8888
TAVILY_ENABLED=false
BRAVE_ENABLED=false
RERANKER_ENABLED=false
```

Docker Compose、host Python development、MCP clients、hosted provider keys、Jina Reader、任意 reranking の完全な `.env` 例は [docs/ENVIRONMENT.md](docs/ENVIRONMENT.md) を参照してください。
初期 build の decisions、verification notes、article material は [docs/PROJECT_NOTES.md](docs/PROJECT_NOTES.md) にあります。

Server-side provider keys は gateway の `.env` に置き、agent の MCP config には置きません。

| Key | いつ設定するか |
|---|---|
| `RETRIEVAL_API_KEY` | 非 local の gateway access では必須。Agent 側では `AGENT_SEARCH_GATEWAY_API_KEY` として使います。 |
| `TAVILY_API_KEY` | `TAVILY_ENABLED=true` かつ local credit limit を設定した場合だけ使います。 |
| `BRAVE_API_KEY` | 将来の Brave provider 用です。現時点では `BRAVE_ENABLED=false` のままにしてください。 |
| `JINA_API_KEY` | Hosted Jina Reader を使う場合だけ設定します。例：`JINA_READER_BASE_URL=https://r.jina.ai`。Self-hosted Jina Reader と local trafilatura には不要です。 |
| `MINIMAX_API_KEY` | 将来の native summarization provider 用です。現在の gateway は直接呼びません。 |
| `DEEPSEEK_API_KEY` | 将来の native summarization provider 用です。現在の gateway は直接呼びません。 |

Agent MCP config に必要なのは `AGENT_SEARCH_GATEWAY_URL`、`AGENT_SEARCH_GATEWAY_API_KEY`、任意の `AGENT_SEARCH_GATEWAY_TIMEOUT` だけです。

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

Gateway API key を rotation する場合は、`.env` を更新し、API container を再起動してから、すべての MCP client config の key を新しい値に更新してください。

```bash
NEW_KEY="$(openssl rand -hex 32)" \
  perl -0pi -e 's/^RETRIEVAL_API_KEY=.*/RETRIEVAL_API_KEY=$ENV{NEW_KEY}/m' .env
docker compose up -d retrieval-api
```

`cp .env.example .env` だけで `SEARXNG_SECRET` と `RETRIEVAL_API_KEY` を生成しない場合でも、stack は起動する可能性があります。ただし公開テンプレート secret を使うため、短時間のローカルテスト以外には使わないでください。

Tavily を hosted fallback または互換 provider として明示的に使いたい場合は `.env` を編集します。

```dotenv
TAVILY_ENABLED=true
TAVILY_API_KEY=tvly-your-real-key
TAVILY_DAILY_CREDIT_LIMIT=50
TAVILY_SEARCH_DEPTH=basic
```

`TAVILY_DAILY_CREDIT_LIMIT` はローカルの安全ガードです。gateway はリクエスト前に保守的な見積もりを行い、設定した上限を超える前に fallback します。

将来、MiniMax または DeepSeek の native summarization を追加する場合、同じ `.env` に key を置けます。

```dotenv
MINIMAX_API_KEY=
DEEPSEEK_API_KEY=
```

現在の summary 実装は `SUMMARY_WEBHOOK_URL` を使います。MiniMax や DeepSeek を直接呼び出す実装はまだありません。

## Quick Start

```bash
cd agent-search-gateway
cp .env.example .env
SEARXNG_SECRET="$(openssl rand -hex 32)" RETRIEVAL_API_KEY="$(openssl rand -hex 32)" \
  perl -0pi -e 's/^SEARXNG_SECRET=.*/SEARXNG_SECRET=$ENV{SEARXNG_SECRET}/m; s/^RETRIEVAL_API_KEY=.*/RETRIEVAL_API_KEY=$ENV{RETRIEVAL_API_KEY}/m' .env
docker compose up -d --build
```

Health checks：

```bash
curl http://127.0.0.1:8888/search?q=searxng\&format=json | head
curl http://127.0.0.1:8010/healthz
API_KEY="$(grep '^RETRIEVAL_API_KEY=' .env | cut -d= -f2-)"
curl -sS -H "Authorization: Bearer ${API_KEY}" \
  "http://127.0.0.1:8010/search?q=local%20AI%20search&max_results=3" | jq .
```

## Prebuilt Docker Image

retrieval API は Docker Hub の prebuilt image からも実行できます。

```bash
cd agent-search-gateway
cp .env.example .env
SEARXNG_SECRET="$(openssl rand -hex 32)" RETRIEVAL_API_KEY="$(openssl rand -hex 32)" \
  perl -0pi -e 's/^SEARXNG_SECRET=.*/SEARXNG_SECRET=$ENV{SEARXNG_SECRET}/m; s/^RETRIEVAL_API_KEY=.*/RETRIEVAL_API_KEY=$ENV{RETRIEVAL_API_KEY}/m' .env
docker compose -f docker-compose.image.yml up -d
```

デフォルト image：

```text
docker.io/chen920/agent-search-gateway:latest
```

ユーザーは自分の `.env` を用意する必要があります。image には API key や provider credentials は含まれません。Docker Hub publishing と image-based deployment の詳細は [docs/DOCKER_HUB.md](docs/DOCKER_HUB.md) を参照してください。

## Agent Client Integration

Cursor、Codex、Claude、OpenClaw、Hermes などの agent には MCP server 経由で接続するのが推奨です。MCP server は host 上で動き、gateway `http://127.0.0.1:8010` を呼びます。SearXNG を直接呼びません。

推奨 MCP config は、`uvx` で GitHub release から直接実行する形です。

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

自分だけが使う private config であれば、key を MCP の `env` block に直接書いても構いません。

```json
{
  "env": {
    "AGENT_SEARCH_GATEWAY_URL": "https://api.agentsearchgateway.com",
    "AGENT_SEARCH_GATEWAY_API_KEY": "replace-with-your-gateway-api-key",
    "AGENT_SEARCH_GATEWAY_TIMEOUT": "90"
  }
}
```

clone した repo の中で開発する場合は、[docs/integrations/agent-clients.md](docs/integrations/agent-clients.md) の local `.venv` 手順を使ってください。
local Docker Compose gateway を使う場合、`AGENT_SEARCH_GATEWAY_ENV_FILE` は clone した repo の `.env` を直接指して構いません。

MCP server が公開する tools：

- `agent_gateway_health`
- `agent_search`
- `agent_extract`

任意の agent skill も含まれています。

```bash
mkdir -p ~/.agents/skills
cp -R skills/agent-search-gateway ~/.agents/skills/
```

Cursor users 向けには reusable User Rule template を用意しています。

```text
rules/agent-search-gateway-user-rule.mdc
```

Cursor User Rules の GitHub/GitLab import には repository URL を入力します。`blob` や raw file URL は入力しません。

```text
https://github.com/chen09/agent-search-gateway
```

Cursor、Codex、Claude、OpenClaw、Hermes のセットアップ手順は [docs/integrations/agent-clients.md](docs/integrations/agent-clients.md) を参照してください。

Self-hosted Jina Reader を extraction fallback として有効にする場合：

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

Response shape：

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

Fallback behavior：

1. Search は `SEARXNG_BASE_URLS` を順番に試します。
2. Extraction はまず local `trafilatura`、設定がある場合は `JINA_READER_BASE_URL` を試します。
3. optional dependencies をインストールし `RERANKER_ENABLED=true` の場合、reranking は CrossEncoder を使います。それ以外は lexical matching に fallback します。
4. `SUMMARY_WEBHOOK_URL` が設定されていれば summary webhook を呼びます。未設定なら短い extractive placeholder を返します。

デフォルト `PROVIDER_ORDER=searxng,tavily` では self-hosted path が最初に使われます。Tavily は明示的に有効化した場合、provider を指定した場合、または Tavily-compatible endpoint を呼んだ場合だけ使われます。それでも disabled、quota over、rate limited、unavailable の場合は fallback します。

Tavily-compatible adapter examples：

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

## Python venv Run

```bash
cd agent-search-gateway
pyenv install 3.12.10  # 未インストールの場合
pyenv local 3.12.10
python -m venv .venv
. .venv/bin/activate
pip install --upgrade pip
pip install -r api/requirements.txt
cp .env.example .env
export SEARXNG_BASE_URLS=http://127.0.0.1:8888
uvicorn api.main:app --host 127.0.0.1 --port 8010 --reload
```

## Optional PyTorch Reranker

Base install には PyTorch を含めません。`sentence-transformers` は `torch` を引くため、Mac mini では重い場合があります。無効でも lexical reranking で gateway は動作します。

Local CrossEncoder reranking を有効にする場合：

```bash
. .venv/bin/activate
pip install -r api/requirements-reranker.txt
```

`.env` を編集します。

```dotenv
RERANKER_ENABLED=true
RERANKER_DEVICE=mps
```

MPS が使えない場合、または workload に対して遅い場合は `RERANKER_DEVICE=cpu` を使ってください。この repo は依存関係の互換性を重視して Python 3.12.10 を使います。

## Operations Notes

単一ユーザー deployment なら 2 vCPU / 4 GB RAM で MVP は動きます。reranking を有効にする場合は 8 GB RAM がより安全です。初回 reranker 起動時は model download のため network access が必要です。

Local MVP から provider routing、persistent cache、hardening、agent integration までの roadmap は [docs/ROADMAP.md](docs/ROADMAP.md) を参照してください。

Concurrency が増えたときの主な bottleneck：

- Upstream SearXNG engines と rate limits。
- Webpage fetch latency。
- CPU reranker inference。
- 同じ URL の繰り返し extraction。

推奨される次の最適化：

- Search results と extracted URL content の cache。
- `extract_top_k` の制限。
- Provider-level quota guards。
- 信頼された local network 以外に API を公開する前の SSRF protection。

## Security

- デフォルトでは services を `127.0.0.1` に bind します。
- 非 local 利用では `RETRIEVAL_API_KEY` を有効にしてください。
- Public deployment では Caddy、Nginx、Cloudflare Tunnel、Cloudflare Access などを前段に置いてください。
- API keys、cookies、full authorization headers、sensitive query parameters を log に出さないでください。
- Hosted provider keys を agent に直接渡さず、この gateway を通して quota と fallback を管理してください。

## Troubleshooting

1. SearXNG から `403 Forbidden`：`searxng/settings.yml` の `search.formats` に `json` が含まれているか確認し、SearXNG を再起動してください。
2. Gateway から `401`：`Authorization: Bearer ${RETRIEVAL_API_KEY}` または `X-API-Key` を送信してください。
3. 初回検索が遅い：reranker model を download 中かもしれません。すばやく試すには `RERANKER_ENABLED=false` を設定してください。
4. Content extraction が空：ページが bot をブロックしているか JavaScript を必要としている可能性があります。Jina Reader を設定するか、後で Crawl4AI を追加してください。
5. Search results がない：upstream engines が rate-limited の可能性があります。request rate を下げるか、SearXNG instance を追加してください。
6. Out of memory：`EXTRACT_TOP_K` を下げる、reranking を無効化する、または小さい reranker model を使ってください。

## License

Agent Search Gateway は [Apache License 2.0](LICENSE) で提供されます。

Third-party components はそれぞれの upstream license に従います。詳細は [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md) を参照してください。
