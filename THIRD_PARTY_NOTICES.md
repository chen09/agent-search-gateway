# Third-Party Notices

Agent Search Gateway source code is licensed under the Apache License 2.0. See [LICENSE](LICENSE).

This file summarizes important third-party components used by the project. It is not a substitute for the upstream license files.

## Docker Compose Services

The default Compose stack starts separate upstream containers in addition to the Agent Search Gateway API image:

| Component | Role | Notes |
|---|---|---|
| SearXNG | Self-hosted metasearch backend | Runs as the upstream `docker.io/searxng/searxng` image. SearXNG is licensed under AGPL-3.0-or-later upstream. |
| Valkey | Cache/state service used by SearXNG | Runs as the upstream `docker.io/valkey/valkey` image. Valkey uses BSD-style licensing upstream. |
| Jina Reader | Optional extraction fallback | Runs only with the optional `reader` Compose profile. Review the upstream image/repository license before redistribution. |

These services are not bundled into the `retrieval-api` source tree. Their upstream licenses continue to apply.

## Python Dependencies

The `retrieval-api` image installs Python dependencies from PyPI according to [api/requirements.txt](api/requirements.txt). The host-side MCP server installs dependencies from [integrations/mcp/requirements.txt](integrations/mcp/requirements.txt).

Major runtime dependencies include:

- FastAPI
- Uvicorn
- HTTPX
- trafilatura
- python-dotenv
- MCP Python SDK
- Starlette
- sse-starlette

Optional reranker dependencies are listed in [api/requirements-reranker.txt](api/requirements-reranker.txt). They are not part of the base gateway image.

Each dependency remains under its own upstream license. Check package metadata or upstream repositories when redistributing modified bundles.
