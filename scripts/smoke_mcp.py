from __future__ import annotations

import asyncio
import json
import os
from pathlib import Path
from typing import Any

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


ROOT = Path(__file__).resolve().parents[1]


def text_content(result: Any) -> str:
    return "\n".join(
        getattr(item, "text", str(item)) for item in getattr(result, "content", [])
    )


def decode_json_text(result: Any) -> Any:
    text = text_content(result)
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        return text


async def main() -> None:
    python_bin = os.getenv("AGENT_SEARCH_GATEWAY_MCP_PYTHON") or str(
        ROOT / ".venv" / "bin" / "python"
    )
    server_path = str(ROOT / "integrations" / "mcp" / "server.py")
    env = {
        **os.environ,
        "AGENT_SEARCH_GATEWAY_URL": os.getenv(
            "AGENT_SEARCH_GATEWAY_URL", "http://127.0.0.1:8010"
        ),
        "AGENT_SEARCH_GATEWAY_ENV_FILE": os.getenv(
            "AGENT_SEARCH_GATEWAY_ENV_FILE", str(ROOT / ".env")
        ),
    }
    server_params = StdioServerParameters(
        command=python_bin,
        args=[server_path],
        env=env,
    )

    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            tools = await session.list_tools()
            names = sorted(tool.name for tool in tools.tools)
            print("tools:", ", ".join(names))

            health = await session.call_tool("agent_gateway_health", arguments={})
            print("health:", decode_json_text(health))

            search = await session.call_tool(
                "agent_search",
                arguments={
                    "query": "SearXNG self hosted metasearch",
                    "max_results": 2,
                    "extract_top_k": 0,
                    "include_summary": False,
                },
            )
            payload = decode_json_text(search)
            if isinstance(payload, dict):
                print(
                    "search:",
                    {
                        "provider_chain": payload.get("provider_chain"),
                        "results_count": len(payload.get("results", [])),
                        "errors_count": len(payload.get("errors", [])),
                    },
                )
            else:
                print("search:", payload)


if __name__ == "__main__":
    asyncio.run(main())
