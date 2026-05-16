from __future__ import annotations

import httpx

from api.config import Settings
from api.models import Candidate, SearchOutcome
from api.text_utils import clean_text, clean_url, netloc


class SearxngProvider:
    name = "searxng"

    def __init__(self, settings: Settings) -> None:
        self.settings = settings

    async def search(
        self,
        query: str,
        max_results: int,
        errors: list[str],
    ) -> SearchOutcome:
        for base_url in self.settings.searxng_base_urls:
            try:
                results = await self._search_base_url(base_url, query, max_results)
                if results:
                    return SearchOutcome(
                        candidates=results,
                        provider=f"searxng:{netloc(base_url)}",
                    )
                errors.append(f"searxng returned no results: {base_url}")
            except Exception as exc:  # noqa: BLE001
                errors.append(
                    f"searxng failed: {base_url}: {type(exc).__name__}: {exc}"
                )
        return SearchOutcome(candidates=[], provider="searxng")

    async def _search_base_url(
        self,
        base_url: str,
        query: str,
        max_results: int,
    ) -> list[Candidate]:
        params = {
            "q": query,
            "format": "json",
            "language": "auto",
            "safesearch": "0",
        }
        async with httpx.AsyncClient(
            timeout=self.settings.http_timeout_seconds,
            follow_redirects=True,
        ) as client:
            response = await client.get(f"{base_url}/search", params=params)
            response.raise_for_status()
            payload = response.json()

        items: list[Candidate] = []
        for index, result in enumerate(payload.get("results", [])):
            url = clean_url(str(result.get("url", "")))
            if not url:
                continue
            title = clean_text(str(result.get("title") or url))
            snippet = clean_text(str(result.get("content") or result.get("snippet") or ""))
            engine = result.get("engine") or result.get("engines") or "searxng"
            score = float(max_results - index) / max(max_results, 1)
            items.append(
                Candidate(
                    title=title,
                    url=url,
                    snippet=snippet,
                    content="",
                    score=score,
                    source=f"searxng:{engine}",
                )
            )
            if len(items) >= max_results:
                break
        return items
