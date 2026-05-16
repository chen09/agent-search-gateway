from __future__ import annotations

import time
from typing import Any, Dict, List, Optional, Set
from uuid import uuid4

from fastapi import Depends, FastAPI, Header, HTTPException, Query

from api.cache import TTLCache, cache_key
from api.config import settings
from api.extraction import ContentExtractor
from api.models import (
    Candidate,
    ExtractRequest,
    SearchRequest,
    SearchResponse,
    SearchResult,
    normalize_urls,
)
from api.providers.searxng import SearxngProvider
from api.providers.tavily import TavilyProvider
from api.quota import (
    DailyQuotaGuard,
    estimate_tavily_extract_credits,
    estimate_tavily_search_credits,
)
from api.rerank import rerank_candidates
from api.summary import summarize
from api.text_utils import canonical_url

app = FastAPI(title="Agent Search Gateway", version="0.2.0")

search_cache = TTLCache(
    ttl_seconds=settings.search_cache_ttl_seconds,
    enabled=settings.cache_enabled,
)
content_cache = TTLCache(
    ttl_seconds=settings.content_cache_ttl_seconds,
    enabled=settings.cache_enabled,
)
quota_guard = DailyQuotaGuard(
    limits={
        "tavily": settings.tavily_daily_credit_limit,
        "brave": settings.brave_daily_credit_limit,
    }
)
extractor = ContentExtractor(settings=settings, cache=content_cache)
searxng_provider = SearxngProvider(settings=settings)
tavily_provider = TavilyProvider(settings=settings)


def require_auth(
    authorization: Optional[str] = Header(default=None),
    x_api_key: Optional[str] = Header(default=None),
) -> None:
    if not settings.api_key:
        return
    bearer = f"Bearer {settings.api_key}"
    if authorization == bearer or x_api_key == settings.api_key:
        return
    raise HTTPException(status_code=401, detail="missing or invalid API key")


@app.get("/healthz")
async def healthz() -> Dict[str, Any]:
    return {
        "ok": True,
        "version": app.version,
        "provider_order": settings.provider_order,
        "providers": {
            "searxng": bool(settings.searxng_base_urls),
            "tavily": tavily_provider.configured,
            "brave": settings.brave_enabled and bool(settings.brave_api_key),
        },
        "searxng_base_urls": settings.searxng_base_urls,
        "reranker_enabled": settings.reranker_enabled,
        "jina_reader_configured": bool(settings.jina_reader_base_url),
        "cache": {
            "search": search_cache.stats(),
            "content": content_cache.stats(),
        },
        "quota_usage_today": quota_guard.snapshot(),
    }


@app.get("/search", response_model=SearchResponse)
async def search_get(
    q: str = Query(..., min_length=1),
    max_results: int = Query(default=settings.max_results, ge=1, le=20),
    extract_top_k: int = Query(default=settings.extract_top_k, ge=0, le=10),
    provider: str = Query(default="auto"),
    _: None = Depends(require_auth),
) -> SearchResponse:
    return await run_search(
        SearchRequest(
            query=q,
            max_results=max_results,
            extract_top_k=extract_top_k,
            provider=provider,
        )
    )


@app.post("/search", response_model=SearchResponse)
async def search_post(
    request: SearchRequest,
    _: None = Depends(require_auth),
) -> SearchResponse:
    return await run_search(request)


@app.post("/extract")
@app.post("/tavily/extract")
@app.post("/compat/tavily/extract")
async def extract_post(
    request: ExtractRequest,
    _: None = Depends(require_auth),
) -> Dict[str, Any]:
    return await run_extract(request)


@app.post("/tavily/search")
@app.post("/compat/tavily/search")
async def tavily_search_post(
    request: SearchRequest,
    _: None = Depends(require_auth),
) -> Dict[str, Any]:
    response = await run_search(request)
    output: Dict[str, Any] = {
        "query": response.query,
        "results": [
            {
                "title": item.title,
                "url": item.url,
                "content": item.snippet or item.content[:600],
                "score": item.score,
                "raw_content": item.content or None,
            }
            for item in response.results
        ],
        "response_time": round(response.elapsed_ms / 1000, 3),
        "usage": {"credits": 0},
        "request_id": str(uuid4()),
    }
    if request.include_answer or request.include_summary:
        output["answer"] = response.summary
    return output


async def run_search(request: SearchRequest) -> SearchResponse:
    started = time.perf_counter()
    cache_payload = request_to_cache_payload(request)
    key = cache_key("search", cache_payload)
    cached = search_cache.get(key)
    if cached is not None:
        response = copy_search_response(cached)
        response.elapsed_ms = int((time.perf_counter() - started) * 1000)
        response.provider_chain = ["cache", *response.provider_chain]
        return response

    errors: List[str] = []
    provider_chain: List[str] = []

    outcome = await search_with_router(request, provider_chain, errors)
    candidates = dedupe(outcome.candidates)

    top_for_extraction = [
        item for item in candidates[: request.extract_top_k] if not item.content
    ]
    await extractor.enrich_candidates(top_for_extraction, errors)

    ranked = rerank_candidates(request.query, candidates, settings)[: request.max_results]
    summary = ""
    if request.include_summary:
        summary = outcome.summary or await summarize(request.query, ranked, errors, settings)

    response = SearchResponse(
        query=request.query,
        elapsed_ms=int((time.perf_counter() - started) * 1000),
        provider_chain=provider_chain,
        summary=summary,
        results=[SearchResult(**item.__dict__) for item in ranked],
        errors=errors,
    )
    search_cache.set(key, copy_search_response(response))
    return response


async def search_with_router(
    request: SearchRequest,
    provider_chain: List[str],
    errors: List[str],
):
    explicit_provider = request.provider != "auto"
    order = [request.provider] if explicit_provider else settings.provider_order

    for provider in order:
        provider = provider.lower()
        if provider == "tavily":
            if not tavily_provider.configured:
                if explicit_provider:
                    errors.append("tavily provider is not enabled or missing TAVILY_API_KEY")
                continue
            credits = estimate_tavily_search_credits(
                request.search_depth or settings.tavily_search_depth
            )
            decision = quota_guard.try_consume("tavily", credits)
            if not decision.allowed:
                errors.append(decision.reason)
                continue
            outcome = await tavily_provider.search(request, errors)
            if outcome.candidates:
                provider_chain.append(outcome.provider)
                return outcome
        elif provider == "searxng":
            outcome = await searxng_provider.search(
                request.query,
                request.max_results,
                errors,
            )
            if outcome.candidates:
                provider_chain.append(outcome.provider)
                return outcome
        elif provider == "brave":
            if explicit_provider:
                errors.append("brave provider is planned but not implemented")
        else:
            errors.append(f"unknown provider: {provider}")

    outcome = await searxng_provider.search(request.query, request.max_results, errors)
    if outcome.candidates:
        provider_chain.append(outcome.provider)
    return outcome


async def run_extract(request: ExtractRequest) -> Dict[str, Any]:
    started = time.perf_counter()
    errors: List[str] = []
    urls = normalize_urls(request.urls)
    provider_chain: List[str] = []
    usage_credits = 0

    explicit_provider = request.provider != "auto"
    order = [request.provider] if explicit_provider else settings.provider_order
    results = []
    failed = []

    for provider in [item.lower() for item in order]:
        if provider == "tavily":
            if not tavily_provider.configured:
                if explicit_provider:
                    errors.append("tavily provider is not enabled or missing TAVILY_API_KEY")
                continue
            credits = estimate_tavily_extract_credits(len(urls), request.extract_depth)
            decision = quota_guard.try_consume("tavily", credits)
            if not decision.allowed:
                errors.append(decision.reason)
                continue
            results, failed, usage_credits = await tavily_provider.extract(request, errors)
            if results:
                provider_chain.append("tavily")
                break
        elif provider in {"searxng", "local"}:
            results, failed = await extractor.extract_urls(urls, errors)
            if results:
                provider_chain.append("local")
                break

    if not results and not provider_chain:
        results, failed = await extractor.extract_urls(urls, errors)
        provider_chain.append("local")

    return {
        "results": [model_to_dict(result) for result in results],
        "failed_results": failed,
        "response_time": round(time.perf_counter() - started, 3),
        "usage": {"credits": usage_credits},
        "request_id": str(uuid4()),
        "provider_chain": provider_chain,
        "errors": errors,
    }


def dedupe(candidates: List[Candidate]) -> List[Candidate]:
    seen: Set[str] = set()
    output: List[Candidate] = []
    for item in candidates:
        key = canonical_url(item.url)
        if not key or key in seen:
            continue
        seen.add(key)
        output.append(item)
    return output


def request_to_cache_payload(request: SearchRequest) -> Dict[str, Any]:
    if hasattr(request, "model_dump"):
        return request.model_dump()
    return request.dict()


def model_to_dict(model: Any) -> Dict[str, Any]:
    if hasattr(model, "model_dump"):
        return model.model_dump()
    return model.dict()


def copy_search_response(response: SearchResponse) -> SearchResponse:
    if hasattr(response, "model_copy"):
        return response.model_copy(deep=True)
    return response.copy(deep=True)
