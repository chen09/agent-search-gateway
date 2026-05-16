from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel, Field

from api.config import settings


class SearchRequest(BaseModel):
    query: str = Field(..., min_length=1)
    max_results: int = Field(default=settings.max_results, ge=1, le=20)
    extract_top_k: int = Field(default=settings.extract_top_k, ge=0, le=10)
    include_summary: bool = True
    provider: str = "auto"
    search_depth: Optional[str] = None
    include_answer: Union[bool, str] = False
    include_raw_content: Union[bool, str] = False
    include_domains: List[str] = Field(default_factory=list)
    exclude_domains: List[str] = Field(default_factory=list)
    topic: Optional[str] = None
    time_range: Optional[str] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    country: Optional[str] = None


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
    provider_chain: List[str]
    summary: str = ""
    results: List[SearchResult]
    errors: List[str] = Field(default_factory=list)


class ExtractRequest(BaseModel):
    urls: Union[str, List[str]]
    query: Optional[str] = None
    provider: str = "auto"
    extract_depth: str = "basic"
    chunks_per_source: int = Field(default=3, ge=1, le=5)
    include_images: bool = False
    include_favicon: bool = False
    format: str = "markdown"
    timeout: Optional[float] = Field(default=None, ge=1.0, le=60.0)
    include_usage: bool = True


class ExtractedResult(BaseModel):
    url: str
    raw_content: str
    images: List[Any] = Field(default_factory=list)
    favicon: Optional[str] = None
    source: str = "local"


@dataclass
class Candidate:
    title: str
    url: str
    snippet: str
    content: str
    score: float
    source: str


@dataclass
class SearchOutcome:
    candidates: List[Candidate]
    provider: str
    summary: str = ""
    usage_credits: int = 0
    raw_response: Optional[Dict[str, Any]] = None


def normalize_urls(urls: Union[str, List[str]]) -> List[str]:
    if isinstance(urls, str):
        return [urls]
    return urls
