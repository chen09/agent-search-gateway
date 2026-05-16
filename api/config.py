from __future__ import annotations

import os
from dataclasses import dataclass

from dotenv import load_dotenv


load_dotenv()


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


def env_csv(name: str, default: str = "") -> list[str]:
    return [item.strip() for item in os.getenv(name, default).split(",") if item.strip()]


@dataclass(frozen=True)
class Settings:
    api_key: str
    searxng_base_urls: list[str]
    max_results: int
    extract_top_k: int
    content_max_chars: int
    http_timeout_seconds: int
    provider_order: list[str]
    cache_enabled: bool
    search_cache_ttl_seconds: int
    content_cache_ttl_seconds: int
    reranker_enabled: bool
    reranker_model: str
    reranker_device: str
    jina_reader_base_url: str
    jina_api_key: str
    summary_webhook_url: str
    tavily_enabled: bool
    tavily_api_key: str
    tavily_base_url: str
    tavily_daily_credit_limit: int
    tavily_search_depth: str
    brave_enabled: bool
    brave_api_key: str
    brave_daily_credit_limit: int
    minimax_api_key: str
    deepseek_api_key: str

    @classmethod
    def from_env(cls) -> "Settings":
        return cls(
            api_key=os.getenv("RETRIEVAL_API_KEY", ""),
            searxng_base_urls=[
                item.rstrip("/")
                for item in env_csv("SEARXNG_BASE_URLS", "http://searxng:8080")
            ],
            max_results=env_int("MAX_RESULTS", 8),
            extract_top_k=env_int("EXTRACT_TOP_K", 5),
            content_max_chars=env_int("CONTENT_MAX_CHARS", 12000),
            http_timeout_seconds=env_int("HTTP_TIMEOUT_SECONDS", 15),
            provider_order=env_csv("PROVIDER_ORDER", "searxng,tavily"),
            cache_enabled=env_bool("CACHE_ENABLED", True),
            search_cache_ttl_seconds=env_int("SEARCH_CACHE_TTL_SECONDS", 900),
            content_cache_ttl_seconds=env_int("CONTENT_CACHE_TTL_SECONDS", 86400),
            reranker_enabled=env_bool("RERANKER_ENABLED", False),
            reranker_model=os.getenv(
                "RERANKER_MODEL", "cross-encoder/ms-marco-MiniLM-L6-v2"
            ),
            reranker_device=os.getenv("RERANKER_DEVICE", "cpu"),
            jina_reader_base_url=os.getenv("JINA_READER_BASE_URL", "").rstrip("/"),
            jina_api_key=os.getenv("JINA_API_KEY", ""),
            summary_webhook_url=os.getenv("SUMMARY_WEBHOOK_URL", ""),
            tavily_enabled=env_bool("TAVILY_ENABLED", False),
            tavily_api_key=os.getenv("TAVILY_API_KEY", ""),
            tavily_base_url=os.getenv("TAVILY_BASE_URL", "https://api.tavily.com").rstrip(
                "/"
            ),
            tavily_daily_credit_limit=env_int("TAVILY_DAILY_CREDIT_LIMIT", 50),
            tavily_search_depth=os.getenv("TAVILY_SEARCH_DEPTH", "basic"),
            brave_enabled=env_bool("BRAVE_ENABLED", False),
            brave_api_key=os.getenv("BRAVE_API_KEY", ""),
            brave_daily_credit_limit=env_int("BRAVE_DAILY_CREDIT_LIMIT", 0),
            minimax_api_key=os.getenv("MINIMAX_API_KEY", ""),
            deepseek_api_key=os.getenv("DEEPSEEK_API_KEY", ""),
        )


settings = Settings.from_env()
