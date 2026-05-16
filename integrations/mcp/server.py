import os
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

import httpx
from dotenv import dotenv_values
from mcp.server.fastmcp import FastMCP


mcp = FastMCP("agent-search-gateway")


def project_root() -> Path:
    return Path(__file__).resolve().parents[2]


def configured_env_file() -> Optional[Path]:
    explicit = os.getenv("AGENT_SEARCH_GATEWAY_ENV_FILE")
    candidates = []
    if explicit:
        candidates.append(Path(explicit).expanduser())
    candidates.extend(
        [
            Path.cwd() / ".env",
            project_root() / ".env",
        ]
    )
    for candidate in candidates:
        if candidate.is_file():
            return candidate
    return None


def env_values() -> Dict[str, str]:
    env_file = configured_env_file()
    values: Dict[str, str] = {}
    if env_file:
        values.update(
            {key: value for key, value in dotenv_values(env_file).items() if value}
        )
    values.update({key: value for key, value in os.environ.items() if value})
    return values


def gateway_url(values: Dict[str, str]) -> str:
    return values.get("AGENT_SEARCH_GATEWAY_URL", "http://127.0.0.1:8010").rstrip("/")


def gateway_api_key(values: Dict[str, str]) -> str:
    return values.get("AGENT_SEARCH_GATEWAY_API_KEY") or values.get(
        "RETRIEVAL_API_KEY", ""
    )


def gateway_timeout(values: Dict[str, str]) -> float:
    raw = values.get("AGENT_SEARCH_GATEWAY_TIMEOUT", "60")
    try:
        return max(1.0, float(raw))
    except ValueError:
        return 60.0


def auth_headers(values: Dict[str, str]) -> Dict[str, str]:
    api_key = gateway_api_key(values)
    if not api_key:
        return {}
    return {"Authorization": f"Bearer {api_key}"}


async def request_gateway(
    method: str,
    path: str,
    payload: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    values = env_values()
    url = f"{gateway_url(values)}{path}"
    try:
        async with httpx.AsyncClient(timeout=gateway_timeout(values)) as client:
            response = await client.request(
                method,
                url,
                headers=auth_headers(values),
                json=payload,
            )
            if response.status_code == 401:
                raise RuntimeError(
                    "Agent Search Gateway returned 401. Set "
                    "AGENT_SEARCH_GATEWAY_API_KEY, RETRIEVAL_API_KEY, or "
                    "AGENT_SEARCH_GATEWAY_ENV_FILE pointing to the repo .env file."
                )
            response.raise_for_status()
            return response.json()
    except httpx.ConnectError as exc:
        raise RuntimeError(
            "Cannot connect to Agent Search Gateway. Start it with "
            "`docker compose up -d --build` and confirm "
            "`curl http://127.0.0.1:8010/healthz` works."
        ) from exc
    except httpx.HTTPStatusError as exc:
        body = exc.response.text[:500]
        raise RuntimeError(
            f"Agent Search Gateway request failed with HTTP "
            f"{exc.response.status_code}: {body}"
        ) from exc


@mcp.tool()
async def agent_gateway_health() -> Dict[str, Any]:
    """Check whether the configured Agent Search Gateway is reachable."""

    return await request_gateway("GET", "/healthz")


@mcp.tool()
async def agent_search(
    query: str,
    max_results: int = 5,
    extract_top_k: int = 3,
    include_summary: bool = True,
    provider: str = "auto",
) -> Dict[str, Any]:
    """Search the web through the self-hosted Agent Search Gateway."""

    payload = {
        "query": query,
        "max_results": max_results,
        "extract_top_k": extract_top_k,
        "include_summary": include_summary,
        "provider": provider,
    }
    return await request_gateway("POST", "/search", payload)


@mcp.tool()
async def agent_extract(
    urls: Union[str, List[str]],
    query: Optional[str] = None,
    extract_depth: str = "basic",
    chunks_per_source: int = 3,
) -> Dict[str, Any]:
    """Extract clean page content from one or more URLs through the gateway."""

    payload = {
        "urls": urls,
        "query": query,
        "extract_depth": extract_depth,
        "chunks_per_source": chunks_per_source,
    }
    return await request_gateway("POST", "/extract", payload)


def main() -> None:
    mcp.run()


if __name__ == "__main__":
    main()
