import time
import unittest

from api.cache import TTLCache, cache_key
from api.quota import (
    DailyQuotaGuard,
    estimate_tavily_extract_credits,
    estimate_tavily_search_credits,
)


class CacheQuotaTests(unittest.TestCase):
    def test_cache_key_is_stable_for_equivalent_payloads(self) -> None:
        first = cache_key("search", {"query": "agent search", "max_results": 5})
        second = cache_key("search", {"max_results": 5, "query": "agent search"})
        self.assertEqual(first, second)

    def test_ttl_cache_expires_items(self) -> None:
        cache = TTLCache(ttl_seconds=1)
        cache.set("key", "value")
        self.assertEqual(cache.get("key"), "value")
        time.sleep(1.01)
        self.assertIsNone(cache.get("key"))

    def test_quota_guard_blocks_over_limit(self) -> None:
        guard = DailyQuotaGuard({"tavily": 2})
        self.assertTrue(guard.try_consume("tavily", 1).allowed)
        self.assertTrue(guard.try_consume("tavily", 1).allowed)
        decision = guard.try_consume("tavily", 1)
        self.assertFalse(decision.allowed)
        self.assertIn("daily credit limit reached", decision.reason)

    def test_tavily_credit_estimates(self) -> None:
        self.assertEqual(estimate_tavily_search_credits("basic"), 1)
        self.assertEqual(estimate_tavily_search_credits("advanced"), 2)
        self.assertEqual(
            estimate_tavily_extract_credits(url_count=1, extract_depth="basic"),
            1,
        )
        self.assertEqual(
            estimate_tavily_extract_credits(url_count=6, extract_depth="advanced"),
            4,
        )


if __name__ == "__main__":
    unittest.main()
