from __future__ import annotations

from typing import Any

import httpx

from api.config import Settings
from api.models import Candidate, ExtractRequest, ExtractedResult, SearchOutcome, SearchRequest
from api.text_utils import clean_text, clean_url, netloc


class TavilyProvider:
    name = "tavily"

    def __init__(self, settings: Settings) -> None:
        self.settings = settings

    @property
    def configured(self) -> bool:
        return self.settings.tavily_enabled and bool(self.settings.tavily_api_key)

    async def search(
        self,
        request: SearchRequest,
        errors: list[str],
    ) -> SearchOutcome:
        if not self.configured:
            return SearchOutcome(candidates=[], provider="tavily")

        payload: dict[str, Any] = {
            "query": request.query,
            "max_results": request.max_results,
            "search_depth": request.search_depth or self.settings.tavily_search_depth,
            "include_answer": request.include_answer or request.include_summary,
            "include_raw_content": request.include_raw_content
            or ("text" if request.extract_top_k > 0 else False),
            "include_usage": True,
        }
        optional_fields = {
            "include_domains": request.include_domains,
            "exclude_domains": request.exclude_domains,
            "topic": request.topic,
            "time_range": request.time_range,
            "start_date": request.start_date,
            "end_date": request.end_date,
            "country": request.country,
        }
        payload.update({key: value for key, value in optional_fields.items() if value})

        try:
            data = await self._post_json("/search", payload)
        except httpx.HTTPStatusError as exc:
            errors.append(f"tavily search failed: HTTP {exc.response.status_code}")
            return SearchOutcome(candidates=[], provider="tavily")
        except Exception as exc:  # noqa: BLE001
            errors.append(f"tavily search failed: {type(exc).__name__}: {exc}")
            return SearchOutcome(candidates=[], provider="tavily")

        candidates: list[Candidate] = []
        for result in data.get("results", []):
            url = clean_url(str(result.get("url", "")))
            if not url:
                continue
            title = clean_text(str(result.get("title") or url))
            snippet = clean_text(str(result.get("content") or ""))
            raw_content = clean_text(str(result.get("raw_content") or ""))
            candidates.append(
                Candidate(
                    title=title,
                    url=url,
                    snippet=snippet,
                    content=raw_content,
                    score=float(result.get("score") or 0.0),
                    source="tavily",
                )
            )

        return SearchOutcome(
            candidates=candidates,
            provider=f"tavily:{netloc(self.settings.tavily_base_url)}",
            summary=clean_text(str(data.get("answer") or "")),
            usage_credits=int(data.get("usage", {}).get("credits") or 0),
            raw_response=data,
        )

    async def extract(
        self,
        request: ExtractRequest,
        errors: list[str],
    ) -> tuple[list[ExtractedResult], list[dict[str, Any]], int]:
        if not self.configured:
            return [], [], 0

        payload: dict[str, Any] = {
            "urls": request.urls,
            "extract_depth": request.extract_depth,
            "include_images": request.include_images,
            "include_favicon": request.include_favicon,
            "format": request.format,
            "include_usage": request.include_usage,
        }
        if request.query:
            payload["query"] = request.query
            payload["chunks_per_source"] = request.chunks_per_source
        if request.timeout is not None:
            payload["timeout"] = request.timeout

        try:
            data = await self._post_json("/extract", payload)
        except httpx.HTTPStatusError as exc:
            errors.append(f"tavily extract failed: HTTP {exc.response.status_code}")
            return [], [], 0
        except Exception as exc:  # noqa: BLE001
            errors.append(f"tavily extract failed: {type(exc).__name__}: {exc}")
            return [], [], 0

        results = [
            ExtractedResult(
                url=str(item.get("url", "")),
                raw_content=clean_text(str(item.get("raw_content") or "")),
                images=list(item.get("images") or []),
                favicon=item.get("favicon"),
                source="tavily",
            )
            for item in data.get("results", [])
            if item.get("url")
        ]
        failed = list(data.get("failed_results") or [])
        credits = int(data.get("usage", {}).get("credits") or 0)
        return results, failed, credits

    async def _post_json(self, path: str, payload: dict[str, Any]) -> dict[str, Any]:
        headers = {
            "Authorization": f"Bearer {self.settings.tavily_api_key}",
            "Content-Type": "application/json",
        }
        async with httpx.AsyncClient(
            timeout=self.settings.http_timeout_seconds,
            follow_redirects=True,
        ) as client:
            response = await client.post(
                f"{self.settings.tavily_base_url}{path}",
                json=payload,
                headers=headers,
            )
            response.raise_for_status()
            return response.json()
