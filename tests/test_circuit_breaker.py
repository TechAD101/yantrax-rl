import time
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

from services.circuit_breaker import RedisCircuitBreaker


def test_circuit_breaker_in_memory_fallback():
    # Force using in-memory fallback by connecting to invalid redis host
    cb = RedisCircuitBreaker(redis_host='127.0.0.254', redis_port=9999, failure_threshold=2, reset_timeout=1)
    key = 'TEST_KEY'

    # Initially allowed
    assert cb.allow_request(key) is True

    # Record failures and ensure circuit opens after threshold
    cb.record_failure(key)
    assert cb.allow_request(key) is True
    cb.record_failure(key)
    # After reaching threshold, allow_request should be False (circuit open)
    assert cb.allow_request(key) is False

    # Wait for reset timeout and ensure circuit resets
    time.sleep(1.2)
    assert cb.allow_request(key) is True


def test_record_success_resets_state():
    cb = RedisCircuitBreaker(redis_host='127.0.0.254', redis_port=9999, failure_threshold=1, reset_timeout=5)
    key = 'TEST_SUCCESS'

    cb.record_failure(key)
    assert cb.allow_request(key) is False

    cb.record_success(key)
    assert cb.allow_request(key) is True
