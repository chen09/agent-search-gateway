from __future__ import annotations

import asyncio
from typing import Any

import httpx
import trafilatura

from api.cache import TTLCache, cache_key
from api.config import Settings
from api.models import Candidate, ExtractedResult
from api.text_utils import clean_text

USER_AGENT = (
    "Mozilla/5.0 (compatible; agent-search-gateway/0.2.0; "
    "+https://example.invalid/agent-search-gateway)"
)


class ContentExtractor:
    def __init__(self, settings: Settings, cache: TTLCache) -> None:
        self.settings = settings
        self.cache = cache

    async def enrich_candidates(
        self,
        items: list[Candidate],
        errors: list[str],
    ) -> None:
        semaphore = asyncio.Semaphore(4)

        async def enrich(item: Candidate) -> None:
            if item.content:
                return
            async with semaphore:
                item.content = await self.extract_content(item.url, errors)

        await asyncio.gather(*(enrich(item) for item in items))

    async def extract_urls(
        self,
        urls: list[str],
        errors: list[str],
    ) -> tuple[list[ExtractedResult], list[dict[str, Any]]]:
        results: list[ExtractedResult] = []
        failed: list[dict[str, Any]] = []
        for url in urls:
            content = await self.extract_content(url, errors)
            if content:
                results.append(
                    ExtractedResult(url=url, raw_content=content, source="local")
                )
            else:
                failed.append({"url": url, "error": "content extraction failed"})
        return results, failed

    async def extract_content(self, url: str, errors: list[str]) -> str:
        key = cache_key("content", {"url": url})
        cached = self.cache.get(key)
        if cached is not None:
            return cached

        local = await self.extract_with_trafilatura(url, errors)
        if local:
            content = local[: self.settings.content_max_chars]
            self.cache.set(key, content)
            return content
        if self.settings.jina_reader_base_url:
            remote = await self.extract_with_jina_reader(url, errors)
            if remote:
                content = remote[: self.settings.content_max_chars]
                self.cache.set(key, content)
                return content
        return ""

    async def extract_with_trafilatura(self, url: str, errors: list[str]) -> str:
        headers = {"User-Agent": USER_AGENT, "Accept": "text/html,application/xhtml+xml"}
        try:
            async with httpx.AsyncClient(
                timeout=self.settings.http_timeout_seconds,
                follow_redirects=True,
            ) as client:
                response = await client.get(url, headers=headers)
                response.raise_for_status()
            extracted = trafilatura.extract(
                response.text,
                url=url,
                include_comments=False,
                include_tables=False,
                favor_recall=True,
                output_format="txt",
            )
            return clean_text(extracted or "")
        except Exception as exc:  # noqa: BLE001
            errors.append(f"trafilatura failed: {url}: {type(exc).__name__}: {exc}")
            return ""

    async def extract_with_jina_reader(self, url: str, errors: list[str]) -> str:
        headers = {
            "User-Agent": USER_AGENT,
            "Accept": "application/json",
            "x-max-tokens": "6000",
        }
        if self.settings.jina_api_key:
            headers["Authorization"] = f"Bearer {self.settings.jina_api_key}"
        try:
            async with httpx.AsyncClient(
                timeout=self.settings.http_timeout_seconds,
                follow_redirects=True,
            ) as client:
                response = await client.post(
                    f"{self.settings.jina_reader_base_url}/",
                    data={"url": url},
                    headers=headers,
                )
                response.raise_for_status()
            content_type = response.headers.get("content-type", "")
            if "application/json" in content_type:
                payload = response.json()
                data = payload.get("data", payload)
                text = data.get("content") or data.get("text") or data.get("markdown") or ""
                return clean_text(str(text))
            return clean_text(response.text)
        except Exception as exc:  # noqa: BLE001
            errors.append(f"jina reader failed: {url}: {type(exc).__name__}: {exc}")
            return ""
