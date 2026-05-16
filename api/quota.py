from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Optional


@dataclass(frozen=True)
class QuotaDecision:
    allowed: bool
    reason: str = ""


class DailyQuotaGuard:
    def __init__(self, limits: dict[str, int]) -> None:
        self.limits = limits
        self._usage: dict[tuple[str, str], int] = defaultdict(int)

    def try_consume(self, provider: str, credits: int) -> QuotaDecision:
        if credits <= 0:
            return QuotaDecision(allowed=True)
        limit = self.limits.get(provider, 0)
        if limit <= 0:
            return QuotaDecision(allowed=True)
        key = (provider, datetime.now(timezone.utc).strftime("%Y-%m-%d"))
        used = self._usage[key]
        if used + credits > limit:
            return QuotaDecision(
                allowed=False,
                reason=(
                    f"{provider} daily credit limit reached: "
                    f"used={used}, requested={credits}, limit={limit}"
                ),
            )
        self._usage[key] = used + credits
        return QuotaDecision(allowed=True)

    def snapshot(self) -> dict[str, int]:
        today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        return {
            provider: self._usage.get((provider, today), 0)
            for provider in sorted(self.limits)
        }


def estimate_tavily_search_credits(search_depth: Optional[str]) -> int:
    return 2 if (search_depth or "").lower() == "advanced" else 1


def estimate_tavily_extract_credits(url_count: int, extract_depth: str) -> int:
    per_block = 2 if extract_depth.lower() == "advanced" else 1
    blocks = max(1, (url_count + 4) // 5)
    return blocks * per_block
