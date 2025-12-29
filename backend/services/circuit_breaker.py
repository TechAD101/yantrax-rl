"""
services/circuit_breaker.py

Simple Redis-backed circuit breaker with in-memory fallback.
Provides per-key failure counting, open/close state, and reset timeout.
"""
import time
from typing import Dict, Any

try:
    import redis
except Exception:
    redis = None


class RedisCircuitBreaker:
    def __init__(self, redis_host: str = 'localhost', redis_port: int = 6379,
                 failure_threshold: int = 3, reset_timeout: int = 30):
        self.failure_threshold = failure_threshold
        self.reset_timeout = reset_timeout

        if redis:
            try:
                self.client = redis.Redis(host=redis_host, port=redis_port, decode_responses=True)
                # quick ping to ensure connection (may raise)
                self.client.ping()
            except Exception:
                self.client = None
        else:
            self.client = None

        # in-memory fallback
        self._memory: Dict[str, dict[str, float | int]] = {}

    def _mem_get(self, key: str):
        return self._memory.get(key, {'failures': 0, 'opened_at': 0})

    def allow_request(self, key: str) -> bool:
        """Return True if the request should be allowed (circuit closed)"""
        if self.client:
            opened = self.client.get(f"cb:{key}:opened")
            if opened:
                opened_at = float(self.client.get(f"cb:{key}:opened_at") or 0)
                if time.time() - opened_at > self.reset_timeout:
                    # reset
                    self.client.delete(f"cb:{key}:opened")
                    self.client.delete(f"cb:{key}:opened_at")
                    self.client.delete(f"cb:{key}:failures")
                    return True
                return False
            return True

        mem = self._mem_get(key)
        if mem['failures'] >= self.failure_threshold:
            if time.time() - mem['opened_at'] > self.reset_timeout:
                # reset
                self._memory[key] = {'failures': 0, 'opened_at': 0}
                return True
            return False
        return True

    def record_failure(self, key: str):
        if self.client:
            failures = int(self.client.incr(f"cb:{key}:failures"))
            if failures >= self.failure_threshold:
                self.client.set(f"cb:{key}:opened", "1")
                self.client.set(f"cb:{key}:opened_at", str(time.time()))
        else:
            mem = self._mem_get(key)
            mem['failures'] = mem.get('failures', 0) + 1
            if mem['failures'] >= self.failure_threshold:
                mem['opened_at'] = time.time()
            self._memory[key] = mem

    def record_success(self, key: str):
        if self.client:
            self.client.delete(f"cb:{key}:failures")
            self.client.delete(f"cb:{key}:opened")
            self.client.delete(f"cb:{key}:opened_at")
        else:
            self._memory[key] = {'failures': 0, 'opened_at': 0}

    def is_open(self, key: str) -> bool:
        if self.client:
            return bool(self.client.get(f"cb:{key}:opened"))
        mem = self._mem_get(key)
        return mem.get('failures', 0) >= self.failure_threshold and mem.get('opened_at', 0) > 0
