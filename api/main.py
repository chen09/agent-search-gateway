import asyncio
import os
import re
import time
from dataclasses import dataclass
from typing import Any
from urllib.parse import urlparse

import httpx
import trafilatura
from fastapi import Depends, FastAPI, Header, HTTPException, Query
from pydantic import BaseModel, Field


def env_bool(name: str, default: bool) -> bool:
    value = os.getenv(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


def env_int(name: str, default: int) -> int:
    try:
        return int(os.getenv(name, str(default)))
    except ValueError:
        return default


API_KEY = os.getenv("RETRIEVAL_API_KEY", "")
SEARXNG_BASE_URLS = [
    item.strip().rstrip("/")
    for item in os.getenv("SEARXNG_BASE_URLS", "http://searxng:8080").split(",")
    if item.strip()
]
MAX_RESULTS = env_int("MAX_RESULTS", 8)
EXTRACT_TOP_K = env_int("EXTRACT_TOP_K", 5)
CONTENT_MAX_CHARS = env_int("CONTENT_MAX_CHARS", 12000)
HTTP_TIMEOUT_SECONDS = env_int("HTTP_TIMEOUT_SECONDS", 15)
RERANKER_ENABLED = env_bool("RERANKER_ENABLED", True)
RERANKER_MODEL = os.getenv("RERANKER_MODEL", "cross-encoder/ms-marco-MiniLM-L6-v2")
RERANKER_DEVICE = os.getenv("RERANKER_DEVICE", "cpu")
JINA_READER_BASE_URL = os.getenv("JINA_READER_BASE_URL", "").rstrip("/")
JINA_API_KEY = os.getenv("JINA_API_KEY", "")
SUMMARY_WEBHOOK_URL = os.getenv("SUMMARY_WEBHOOK_URL", "")

USER_AGENT = (
    "Mozilla/5.0 (compatible; agent-search-gateway/0.1; "
    "+https://example.invalid/agent-search-gateway)"
)


class SearchRequest(BaseModel):
    query: str = Field(..., min_length=1)
    max_results: int = Field(default=MAX_RESULTS, ge=1, le=20)
    extract_top_k: int = Field(default=EXTRACT_TOP_K, ge=0, le=10)
    include_summary: bool = True


class SearchResult(BaseModel):
    title: str
    url: str
    snippet: str = ""
    content: str = ""
    score: float = 0.0
    source: str


class SearchResponse(BaseModel):
    query: str
    elapsed_ms: int
    provider_chain: list[str]
    summary: str = ""
    results: list[SearchResult]
    errors: list[str] = Field(default_factory=list)


@dataclass
class Candidate:
    title: str
    url: str
    snippet: str
    content: str
    score: float
    source: str


app = FastAPI(title="Agent Search Gateway", version="0.1.0")
_reranker: Any | None = None


def require_auth(
    authorization: str | None = Header(default=None),
    x_api_key: str | None = Header(default=None),
) -> None:
    if not API_KEY:
        return
    bearer = f"Bearer {API_KEY}"
    if authorization == bearer or x_api_key == API_KEY:
        return
    raise HTTPException(status_code=401, detail="missing or invalid API key")


@app.get("/healthz")
async def healthz() -> dict[str, Any]:
    return {
        "ok": True,
        "searxng_base_urls": SEARXNG_BASE_URLS,
        "reranker_enabled": RERANKER_ENABLED,
        "jina_reader_configured": bool(JINA_READER_BASE_URL),
    }


@app.get("/search", response_model=SearchResponse)
async def search_get(
    q: str = Query(..., min_length=1),
    max_results: int = Query(default=MAX_RESULTS, ge=1, le=20),
    extract_top_k: int = Query(default=EXTRACT_TOP_K, ge=0, le=10),
    _: None = Depends(require_auth),
) -> SearchResponse:
    return await run_search(
        SearchRequest(query=q, max_results=max_results, extract_top_k=extract_top_k)
    )


@app.post("/search", response_model=SearchResponse)
async def search_post(
    request: SearchRequest,
    _: None = Depends(require_auth),
) -> SearchResponse:
    return await run_search(request)


async def run_search(request: SearchRequest) -> SearchResponse:
    started = time.perf_counter()
    errors: list[str] = []
    provider_chain: list[str] = []

    candidates = await search_with_fallback(
        request.query, request.max_results, provider_chain, errors
    )
    candidates = dedupe(candidates)

    top_for_extraction = candidates[: request.extract_top_k]
    await enrich_contents(top_for_extraction, errors)

    ranked = rerank_candidates(request.query, candidates)[: request.max_results]
    summary = await summarize(request.query, ranked, errors) if request.include_summary else ""

    return SearchResponse(
        query=request.query,
        elapsed_ms=int((time.perf_counter() - started) * 1000),
        provider_chain=provider_chain,
        summary=summary,
        results=[SearchResult(**item.__dict__) for item in ranked],
        errors=errors,
    )


async def search_with_fallback(
    query: str,
    max_results: int,
    provider_chain: list[str],
    errors: list[str],
) -> list[Candidate]:
    for base_url in SEARXNG_BASE_URLS:
        try:
            results = await search_searxng(base_url, query, max_results)
            if results:
                provider_chain.append(f"searxng:{netloc(base_url)}")
                return results
            errors.append(f"searxng returned no results: {base_url}")
        except Exception as exc:  # noqa: BLE001
            errors.append(f"searxng failed: {base_url}: {type(exc).__name__}: {exc}")
    return []


async def search_searxng(base_url: str, query: str, max_results: int) -> list[Candidate]:
    params = {
        "q": query,
        "format": "json",
        "language": "auto",
        "safesearch": "0",
    }
    async with httpx.AsyncClient(timeout=HTTP_TIMEOUT_SECONDS, follow_redirects=True) as client:
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


async def enrich_contents(items: list[Candidate], errors: list[str]) -> None:
    semaphore = asyncio.Semaphore(4)

    async def enrich(item: Candidate) -> None:
        async with semaphore:
            item.content = await extract_content(item.url, errors)

    await asyncio.gather(*(enrich(item) for item in items))


async def extract_content(url: str, errors: list[str]) -> str:
    local = await extract_with_trafilatura(url, errors)
    if local:
        return local[:CONTENT_MAX_CHARS]
    if JINA_READER_BASE_URL:
        remote = await extract_with_jina_reader(url, errors)
        if remote:
            return remote[:CONTENT_MAX_CHARS]
    return ""


async def extract_with_trafilatura(url: str, errors: list[str]) -> str:
    headers = {"User-Agent": USER_AGENT, "Accept": "text/html,application/xhtml+xml"}
    try:
        async with httpx.AsyncClient(timeout=HTTP_TIMEOUT_SECONDS, follow_redirects=True) as client:
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


async def extract_with_jina_reader(url: str, errors: list[str]) -> str:
    headers = {
        "User-Agent": USER_AGENT,
        "Accept": "application/json",
        "x-max-tokens": "6000",
    }
    if JINA_API_KEY:
        headers["Authorization"] = f"Bearer {JINA_API_KEY}"
    try:
        async with httpx.AsyncClient(timeout=HTTP_TIMEOUT_SECONDS, follow_redirects=True) as client:
            response = await client.post(
                f"{JINA_READER_BASE_URL}/",
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


def rerank_candidates(query: str, candidates: list[Candidate]) -> list[Candidate]:
    if not candidates:
        return []
    docs = [(item.content or item.snippet or item.title)[:4000] for item in candidates]
    if RERANKER_ENABLED:
        try:
            model = get_reranker()
            rankings = model.rank(query, docs, top_k=len(docs), return_documents=False)
            ranked: list[Candidate] = []
            for row in rankings:
                item = candidates[int(row["corpus_id"])]
                item.score = float(row["score"])
                ranked.append(item)
            return ranked
        except Exception:  # noqa: BLE001
            pass
    return lexical_rerank(query, candidates)


def get_reranker() -> Any:
    global _reranker
    if _reranker is None:
        from sentence_transformers import CrossEncoder

        _reranker = CrossEncoder(RERANKER_MODEL, device=RERANKER_DEVICE)
    return _reranker


def lexical_rerank(query: str, candidates: list[Candidate]) -> list[Candidate]:
    terms = set(tokenize(query))
    for item in candidates:
        body = f"{item.title} {item.snippet} {item.content[:2000]}"
        words = set(tokenize(body))
        item.score = len(terms & words) / max(len(terms), 1)
    return sorted(candidates, key=lambda item: item.score, reverse=True)


async def summarize(query: str, results: list[Candidate], errors: list[str]) -> str:
    payload = {
        "query": query,
        "results": [item.__dict__ for item in results[:5]],
    }
    if SUMMARY_WEBHOOK_URL:
        try:
            async with httpx.AsyncClient(timeout=HTTP_TIMEOUT_SECONDS) as client:
                response = await client.post(SUMMARY_WEBHOOK_URL, json=payload)
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


def dedupe(candidates: list[Candidate]) -> list[Candidate]:
    seen: set[str] = set()
    output: list[Candidate] = []
    for item in candidates:
        key = canonical_url(item.url)
        if not key or key in seen:
            continue
        seen.add(key)
        output.append(item)
    return output


def tokenize(text: str) -> list[str]:
    return re.findall(r"[\w\u3040-\u30ff\u3400-\u9fff]+", text.lower())


def clean_text(text: str) -> str:
    return re.sub(r"\s+", " ", text or "").strip()


def clean_url(url: str) -> str:
    url = url.strip()
    if not url.startswith(("http://", "https://")):
        return ""
    return url


def canonical_url(url: str) -> str:
    parsed = urlparse(url)
    return f"{parsed.scheme}://{parsed.netloc}{parsed.path}".rstrip("/")


def netloc(url: str) -> str:
    return urlparse(url).netloc or url
