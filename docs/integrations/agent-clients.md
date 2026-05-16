# Agent Client Integration

This guide is for someone who clones this repository and wants Cursor, Codex, Claude, OpenClaw, Hermes, or another agent to use the gateway as a local search and extraction tool.

## 1. Start The Gateway

```bash
git clone https://github.com/chen09/agent-search-gateway.git
cd agent-search-gateway

cp .env.example .env
SEARXNG_SECRET="$(openssl rand -hex 32)" RETRIEVAL_API_KEY="$(openssl rand -hex 32)" \
  perl -0pi -e 's/^SEARXNG_SECRET=.*/SEARXNG_SECRET=$ENV{SEARXNG_SECRET}/m; s/^RETRIEVAL_API_KEY=.*/RETRIEVAL_API_KEY=$ENV{RETRIEVAL_API_KEY}/m' .env

docker compose up -d --build
```

Verify:

```bash
curl http://127.0.0.1:8010/healthz
curl 'http://127.0.0.1:8888/search?q=searxng&format=json' | head
```

## 2. Install MCP Dependencies

The MCP server runs on the host and calls the Dockerized gateway over HTTP.

```bash
pyenv install 3.12.10  # if needed
pyenv local 3.12.10
python -m venv .venv
. .venv/bin/activate
pip install -r api/requirements.txt
pip install -r integrations/mcp/requirements.txt
.venv/bin/python scripts/smoke_mcp.py
```

Use absolute paths in MCP client configs. Many clients do not expand `~` reliably.

```bash
pwd
```

Assume that prints:

```text
/absolute/path/to/agent-search-gateway
```

Then the MCP command is:

```text
/absolute/path/to/agent-search-gateway/.venv/bin/python
```

Arguments:

```text
/absolute/path/to/agent-search-gateway/integrations/mcp/server.py
```

Environment:

```text
AGENT_SEARCH_GATEWAY_URL=http://127.0.0.1:8010
AGENT_SEARCH_GATEWAY_ENV_FILE=/absolute/path/to/agent-search-gateway/.env
```

Do not paste `RETRIEVAL_API_KEY` into MCP config unless your client cannot read env files. Prefer `AGENT_SEARCH_GATEWAY_ENV_FILE`.

## 3. Generic MCP JSON

Use this shape for clients that accept an `mcpServers` JSON object, including many Cursor and Claude-compatible configurations:

```json
{
  "mcpServers": {
    "agent-search-gateway": {
      "command": "/absolute/path/to/agent-search-gateway/.venv/bin/python",
      "args": [
        "/absolute/path/to/agent-search-gateway/integrations/mcp/server.py"
      ],
      "env": {
        "AGENT_SEARCH_GATEWAY_URL": "http://127.0.0.1:8010",
        "AGENT_SEARCH_GATEWAY_ENV_FILE": "/absolute/path/to/agent-search-gateway/.env"
      }
    }
  }
}
```

The MCP server exposes:

- `agent_gateway_health`
- `agent_search`
- `agent_extract`

## 4. Cursor

Use the generic MCP JSON above in Cursor's MCP configuration. Project-local configs commonly live under `.cursor/mcp.json`; global configs depend on your Cursor version and workspace policy.

After adding the server, restart or reload Cursor and ask the agent to list available MCP tools. It should see `agent_search` and `agent_extract`.

## 5. Codex

In Codex app MCP settings, add a stdio server:

- Name: `agent-search-gateway`
- Command: `/absolute/path/to/agent-search-gateway/.venv/bin/python`
- Args: `/absolute/path/to/agent-search-gateway/integrations/mcp/server.py`
- Env:
  - `AGENT_SEARCH_GATEWAY_URL=http://127.0.0.1:8010`
  - `AGENT_SEARCH_GATEWAY_ENV_FILE=/absolute/path/to/agent-search-gateway/.env`

Reload the Codex session after saving the MCP server.

## 6. Claude

For Claude clients that accept `mcpServers`, use the generic MCP JSON. For UI-based clients, map the same command, args, and env values into the MCP server form.

Keep the gateway API key server-side in `.env`; do not paste it into prompts.

## 7. OpenClaw

```bash
openclaw mcp set agent-search-gateway '{"command":"/absolute/path/to/agent-search-gateway/.venv/bin/python","args":["/absolute/path/to/agent-search-gateway/integrations/mcp/server.py"],"env":{"AGENT_SEARCH_GATEWAY_URL":"http://127.0.0.1:8010","AGENT_SEARCH_GATEWAY_ENV_FILE":"/absolute/path/to/agent-search-gateway/.env"}}'
openclaw mcp show agent-search-gateway --json
```

## 8. Hermes

```bash
hermes mcp add agent-search-gateway \
  --command /absolute/path/to/agent-search-gateway/.venv/bin/python \
  --args /absolute/path/to/agent-search-gateway/integrations/mcp/server.py \
  --env AGENT_SEARCH_GATEWAY_URL=http://127.0.0.1:8010 \
  --env AGENT_SEARCH_GATEWAY_ENV_FILE=/absolute/path/to/agent-search-gateway/.env

hermes mcp list
```

If Hermes lists the server but tools are disabled, run:

```bash
hermes tools list --summary
```

Then enable the relevant MCP tools through `hermes tools`.

## 9. Install The Skill

The skill is a lightweight operating guide for agents. It is not required when MCP is configured, but it helps agents decide when to use the gateway.

Shared skill pool:

```bash
mkdir -p ~/.agents/skills
cp -R skills/agent-search-gateway ~/.agents/skills/
```

OpenClaw workspace skill install:

```bash
mkdir -p ~/.openclaw/workspace/skills
cp -R skills/agent-search-gateway ~/.openclaw/workspace/skills/
```

For other agents, copy or symlink `skills/agent-search-gateway` into that agent's skill directory.

## 10. Smoke Prompt

After installing MCP and/or the skill, ask the target agent:

```text
Use Agent Search Gateway to search for "SearXNG self hosted metasearch", return 3 results, and report provider_chain plus any errors.
```

Expected shape:

```text
provider_chain includes searxng
results_count > 0
errors is empty or non-fatal
```
