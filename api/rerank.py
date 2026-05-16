from __future__ import annotations

from typing import Any

from api.config import Settings
from api.models import Candidate
from api.text_utils import tokenize

_reranker: Any = None


def rerank_candidates(
    query: str,
    candidates: list[Candidate],
    settings: Settings,
) -> list[Candidate]:
    if not candidates:
        return []
    docs = [(item.content or item.snippet or item.title)[:4000] for item in candidates]
    if settings.reranker_enabled:
        try:
            model = get_reranker(settings)
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


def get_reranker(settings: Settings) -> Any:
    global _reranker
    if _reranker is None:
        from sentence_transformers import CrossEncoder

        _reranker = CrossEncoder(settings.reranker_model, device=settings.reranker_device)
    return _reranker


def lexical_rerank(query: str, candidates: list[Candidate]) -> list[Candidate]:
    terms = set(tokenize(query))
    for item in candidates:
        body = f"{item.title} {item.snippet} {item.content[:2000]}"
        words = set(tokenize(body))
        item.score = len(terms & words) / max(len(terms), 1)
    return sorted(candidates, key=lambda item: item.score, reverse=True)
