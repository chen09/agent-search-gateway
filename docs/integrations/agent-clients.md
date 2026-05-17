# Agent Client Integration

This guide is for someone who wants Cursor, Codex, Claude, OpenClaw, Hermes, or another agent to use Agent Search Gateway.

There are two supported MCP styles:

- `uvx` from GitHub: best for end users and remote gateways because it does not require cloning or creating a venv.
- Local `.venv`: best for developers working inside a cloned repo.

## 1. Start The Gateway

```bash
git clone https://github.com/chen09/agent-search-gateway.git
cd agent-search-gateway

cp .env.example .env
SEARXNG_SECRET="$(openssl rand -hex 32)" RETRIEVAL_API_KEY="$(openssl rand -hex 32)" \
  perl -0pi -e 's/^SEARXNG_SECRET=.*/SEARXNG_SECRET=$ENV{SEARXNG_SECRET}/m; s/^RETRIEVAL_API_KEY=.*/RETRIEVAL_API_KEY=$ENV{RETRIEVAL_API_KEY}/m' .env

docker compose up -d --build
```

For the default Docker Compose stack, users should keep `SEARXNG_BASE_URLS=http://searxng:8080` in `.env`. If they run the API directly on the host, use `SEARXNG_BASE_URLS=http://127.0.0.1:8888` instead. See [../ENVIRONMENT.md](../ENVIRONMENT.md) for complete `.env` examples.

Verify:

```bash
curl http://127.0.0.1:8010/healthz
curl 'http://127.0.0.1:8888/search?q=searxng&format=json' | head
```

## 2. MCP Environment

The MCP server runs on the agent machine and calls the gateway over HTTP.

For a public or remote gateway, create a local env file on the agent machine:

```bash
mkdir -p ~/.agents/env
chmod 700 ~/.agents/env
cat > ~/.agents/env/agent-search-gateway.env <<'EOF'
AGENT_SEARCH_GATEWAY_URL=https://api.agentsearchgateway.com
AGENT_SEARCH_GATEWAY_API_KEY=replace-with-your-gateway-api-key
AGENT_SEARCH_GATEWAY_TIMEOUT=90
EOF
chmod 600 ~/.agents/env/agent-search-gateway.env
```

For a local Docker Compose gateway, point the MCP config directly at the repo `.env`:

```json
{
  "env": {
    "AGENT_SEARCH_GATEWAY_URL": "http://127.0.0.1:8010",
    "AGENT_SEARCH_GATEWAY_ENV_FILE": "/absolute/path/to/agent-search-gateway/.env"
  }
}
```

Do not paste `RETRIEVAL_API_KEY` into prompts. Prefer a local env file readable only by your user.

If your MCP config is private and never committed or synced, it is also valid to put the key directly in the MCP `env` block:

```json
{
  "env": {
    "AGENT_SEARCH_GATEWAY_URL": "https://api.agentsearchgateway.com",
    "AGENT_SEARCH_GATEWAY_API_KEY": "replace-with-your-gateway-api-key",
    "AGENT_SEARCH_GATEWAY_TIMEOUT": "90"
  }
}
```

`AGENT_SEARCH_GATEWAY_API_KEY` is the value of `RETRIEVAL_API_KEY` from the gateway `.env`.

Local Docker Compose:

```bash
grep '^RETRIEVAL_API_KEY=' .env | cut -d= -f2-
```

Remote Ubuntu server:

```bash
ssh ubuntu@your-server
cd ~/agent-search-gateway
grep '^RETRIEVAL_API_KEY=' .env | cut -d= -f2-
```

To rotate the gateway API key:

```bash
NEW_KEY="$(openssl rand -hex 32)" \
  perl -0pi -e 's/^RETRIEVAL_API_KEY=.*/RETRIEVAL_API_KEY=$ENV{NEW_KEY}/m' .env
docker compose up -d retrieval-api
```

After rotating, update every MCP client config that still uses the old key.

## 3. Recommended MCP: uvx From GitHub

Use this shape for clients that accept an `mcpServers` JSON object, including many Cursor and Claude-compatible configurations:

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

For a tagged release, pin the Git source:

```text
git+https://github.com/chen09/agent-search-gateway.git@v0.2.2
```

The MCP server exposes:

- `agent_gateway_health`
- `agent_search`
- `agent_extract`

## 4. Developer MCP: Local venv

Use this when editing the repository or when the target agent is running on the same machine as the cloned repo.

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

Environment for a local gateway:

```text
AGENT_SEARCH_GATEWAY_URL=http://127.0.0.1:8010
AGENT_SEARCH_GATEWAY_ENV_FILE=/absolute/path/to/agent-search-gateway/.env
```

Local venv MCP JSON:

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

## 5. Cursor

Use the generic MCP JSON above in Cursor's MCP configuration. Project-local configs commonly live under `.cursor/mcp.json`; global configs depend on your Cursor version and workspace policy.

After adding the server, restart or reload Cursor and ask the agent to list available MCP tools. It should see `agent_search` and `agent_extract`.

This repo includes a reusable Cursor User Rule template:

```text
rules/agent-search-gateway-user-rule.mdc
```

For Cursor User Rules GitHub/GitLab import, paste the repository URL. Cursor clones repositories during import, so do not paste a `blob` URL or raw file URL:

```text
https://github.com/chen09/agent-search-gateway
```

For manual copy, use the raw file URL:

```text
https://raw.githubusercontent.com/chen09/agent-search-gateway/main/rules/agent-search-gateway-user-rule.mdc
```

The MCP config makes the tools available. The User Rule improves the chance that Cursor chooses `agent_search` and `agent_extract` for web search, current information, external documentation lookup, and URL extraction across the user's projects.

## 6. Codex

In Codex app MCP settings, add a stdio server:

- Name: `agent-search-gateway`
- Command: `uvx`
- Args:
  - `--from`
  - `git+https://github.com/chen09/agent-search-gateway.git@v0.2.2`
  - `agent-search-gateway-mcp`
- Env:
  - `AGENT_SEARCH_GATEWAY_ENV_FILE=/absolute/path/to/agent-search-gateway.env`

Reload the Codex session after saving the MCP server.

## 7. Claude

For Claude clients that accept `mcpServers`, use the generic MCP JSON. For UI-based clients, map the same command, args, and env values into the MCP server form.

Keep the gateway API key server-side in `.env`; do not paste it into prompts.

## 8. OpenClaw

```bash
openclaw mcp set agent-search-gateway '{"command":"uvx","args":["--from","git+https://github.com/chen09/agent-search-gateway.git@v0.2.2","agent-search-gateway-mcp"],"env":{"AGENT_SEARCH_GATEWAY_ENV_FILE":"/absolute/path/to/agent-search-gateway.env"}}'
openclaw mcp show agent-search-gateway --json
```

## 9. Hermes

```bash
hermes mcp add agent-search-gateway \
  --command uvx \
  --args --from \
  --args git+https://github.com/chen09/agent-search-gateway.git@v0.2.2 \
  --args agent-search-gateway-mcp \
  --env AGENT_SEARCH_GATEWAY_ENV_FILE=/absolute/path/to/agent-search-gateway.env

hermes mcp list
```

If Hermes lists the server but tools are disabled, run:

```bash
hermes tools list --summary
```

Then enable the relevant MCP tools through `hermes tools`.

## 10. Install The Skill

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

## 11. Smoke Prompt

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
