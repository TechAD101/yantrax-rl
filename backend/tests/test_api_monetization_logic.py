import sys
from unittest.mock import MagicMock

# Mock redis module
mock_redis = MagicMock()
sys.modules["redis"] = mock_redis

import asyncio
import unittest
from backend.services.api_monetization import RateLimiter, APIQuota

class TestRateLimiter(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.mock_redis = MagicMock()
        self.pipe_mock = MagicMock()
        self.mock_redis.pipeline.return_value = self.pipe_mock
        self.limiter = RateLimiter(self.mock_redis)
        self.quota = APIQuota(
            requests_per_second=2,
            requests_per_minute=5,
            requests_per_hour=10
        )

    async def test_not_rate_limited(self):
        # Mock results: all counts are below limits
        # second: 1 (limit 2), minute: 1 (limit 5), hour: 1 (limit 10)
        self.pipe_mock.execute.return_value = [1, True, 1, True, 1, True]

        is_limited, remaining = await self.limiter.is_rate_limited("test_key", self.quota)

        self.assertFalse(is_limited)
        self.assertEqual(remaining['second'], 1)
        self.assertEqual(remaining['minute'], 4)
        self.assertEqual(remaining['hour'], 9)
        self.assertEqual(self.pipe_mock.execute.call_count, 1)
        self.assertEqual(self.pipe_mock.incr.call_count, 3)

    async def test_rate_limited_second(self):
        # Mock results: second count exceeds limit
        # second: 3 (limit 2), minute: 1 (limit 5), hour: 1 (limit 10)
        self.pipe_mock.execute.return_value = [3, True, 1, True, 1, True]

        is_limited, remaining = await self.limiter.is_rate_limited("test_key", self.quota)

        self.assertTrue(is_limited)
        self.assertEqual(remaining['second'], 0)
        self.assertEqual(remaining['minute'], 4)
        self.assertEqual(remaining['hour'], 9)

    async def test_rate_limited_hour(self):
        # Mock results: hour count exceeds limit
        # second: 1 (limit 2), minute: 1 (limit 5), hour: 11 (limit 10)
        self.pipe_mock.execute.return_value = [1, True, 1, True, 11, True]

        is_limited, remaining = await self.limiter.is_rate_limited("test_key", self.quota)

        self.assertTrue(is_limited)
        self.assertEqual(remaining['second'], 1)
        self.assertEqual(remaining['minute'], 4)
        self.assertEqual(remaining['hour'], 0)

    async def test_redis_error_fallback(self):
        # Mock Redis error
        self.pipe_mock.execute.side_effect = Exception("Redis connection lost")

        is_limited, remaining = await self.limiter.is_rate_limited("test_key", self.quota)

        self.assertFalse(is_limited)
        self.assertEqual(remaining['second'], 2)
        self.assertEqual(remaining['minute'], 5)
        self.assertEqual(remaining['hour'], 10)

if __name__ == "__main__":
    unittest.main()
