from __future__ import annotations

import re
from urllib.parse import urlparse


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
