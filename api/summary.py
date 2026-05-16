from __future__ import annotations

import httpx

from api.config import Settings
from api.models import Candidate


async def summarize(
    query: str,
    results: list[Candidate],
    errors: list[str],
    settings: Settings,
) -> str:
    payload = {
        "query": query,
        "results": [item.__dict__ for item in results[:5]],
    }
    if settings.summary_webhook_url:
        try:
            async with httpx.AsyncClient(
                timeout=settings.http_timeout_seconds,
            ) as client:
                response = await client.post(settings.summary_webhook_url, json=payload)
                response.raise_for_status()
                data = response.json()
            return str(data.get("summary") or data.get("text") or "")
        except Exception as exc:  # noqa: BLE001
            errors.append(f"summary webhook failed: {type(exc).__name__}: {exc}")

    bullets = []
    for item in results[:3]:
        text = item.content or item.snippet
        if text:
            bullets.append(f"- {item.title}: {text[:280]}")
    return "\n".join(bullets)
