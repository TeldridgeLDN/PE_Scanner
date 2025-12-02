"""
Unit Tests for Yahoo API Throttling System

Tests token bucket algorithm, Redis integration, and rate limiting.
"""

import pytest
import time
from unittest.mock import Mock, patch, MagicMock

from pe_scanner.data.api_throttle import (
    YahooAPIThrottle,
    acquire_yahoo_api_token,
    get_throttle_stats,
    YAHOO_BURST_LIMIT,
    YAHOO_REQUESTS_PER_SECOND,
)


# =============================================================================
# Fixtures
# =============================================================================

@pytest.fixture
def mock_redis():
    """Mock Redis client."""
    client = Mock()
    client.ping.return_value = True
    client.exists.return_value = False
    client.get.return_value = str(YAHOO_BURST_LIMIT)
    client.set.return_value = True
    client.incr.return_value = 1
    client.expire.return_value = True
    client.pipeline.return_value.__enter__ = Mock(return_value=client)
    client.pipeline.return_value.__exit__ = Mock(return_value=None)
    client.execute.return_value = [True, True]
    return client


# =============================================================================
# Test Token Bucket Logic (Local Mode)
# =============================================================================

@patch('pe_scanner.data.api_throttle.REDIS_ENABLED', False)
def test_throttle_local_mode_initial_tokens():
    """Test throttle starts with full burst limit in local mode."""
    throttle = YahooAPIThrottle()
    
    assert throttle._use_redis is False
    assert throttle._local_tokens == YAHOO_BURST_LIMIT


@patch('pe_scanner.data.api_throttle.REDIS_ENABLED', False)
def test_throttle_local_mode_acquire_success():
    """Test successful token acquisition in local mode."""
    throttle = YahooAPIThrottle()
    
    result = throttle.acquire(timeout=1.0)
    
    assert result is True
    assert throttle._local_tokens == YAHOO_BURST_LIMIT - 1


@patch('pe_scanner.data.api_throttle.REDIS_ENABLED', False)
def test_throttle_local_mode_burst_limit():
    """Test burst limit prevents excessive rapid requests."""
    throttle = YahooAPIThrottle()
    
    # Consume all burst tokens
    for _ in range(YAHOO_BURST_LIMIT):
        assert throttle.acquire(timeout=0.1) is True
    
    # Next request should fail (timeout)
    result = throttle.acquire(timeout=0.1)
    assert result is False


@patch('pe_scanner.data.api_throttle.REDIS_ENABLED', False)
def test_throttle_local_mode_token_refill():
    """Test tokens refill over time."""
    throttle = YahooAPIThrottle()
    
    # Consume all tokens
    for _ in range(YAHOO_BURST_LIMIT):
        throttle.acquire(timeout=0.1)
    
    # Wait for token refill (0.5s per token at 2 req/sec)
    time.sleep(0.6)
    
    # Should be able to acquire again
    result = throttle.acquire(timeout=0.1)
    assert result is True


@patch('pe_scanner.data.api_throttle.REDIS_ENABLED', False)
def test_throttle_local_mode_stats():
    """Test stats retrieval in local mode."""
    throttle = YahooAPIThrottle()
    
    stats = throttle.get_stats()
    
    assert stats["mode"] == "local"
    assert stats["available_tokens"] == YAHOO_BURST_LIMIT
    assert stats["max_tokens"] == YAHOO_BURST_LIMIT
    assert stats["requests_per_second"] == YAHOO_REQUESTS_PER_SECOND
    assert stats["requests_this_hour"] == -1  # Not tracked in local mode


# =============================================================================
# Test Redis Mode
# =============================================================================

@patch('pe_scanner.data.api_throttle.redis.from_url')
@patch('pe_scanner.data.api_throttle.REDIS_ENABLED', True)
def test_throttle_redis_mode_initialization(mock_from_url, mock_redis):
    """Test throttle initializes Redis correctly."""
    mock_from_url.return_value = mock_redis
    
    throttle = YahooAPIThrottle()
    
    assert throttle._use_redis is True
    assert throttle._redis_client is not None
    mock_redis.ping.assert_called_once()


@patch('pe_scanner.data.api_throttle.redis.from_url')
@patch('pe_scanner.data.api_throttle.REDIS_ENABLED', True)
def test_throttle_redis_mode_fallback_on_error(mock_from_url):
    """Test throttle falls back to local mode if Redis fails."""
    mock_from_url.side_effect = Exception("Connection refused")
    
    throttle = YahooAPIThrottle()
    
    assert throttle._use_redis is False
    assert throttle._redis_client is None


@patch('pe_scanner.data.api_throttle.redis.from_url')
@patch('pe_scanner.data.api_throttle.REDIS_ENABLED', True)
def test_throttle_redis_mode_acquire_success(mock_from_url, mock_redis):
    """Test successful token acquisition in Redis mode."""
    mock_redis.get.return_value = str(YAHOO_BURST_LIMIT)
    mock_from_url.return_value = mock_redis
    
    throttle = YahooAPIThrottle()
    result = throttle.acquire(timeout=1.0)
    
    assert result is True
    # Should have called Redis set to update tokens
    assert mock_redis.set.called


@patch('pe_scanner.data.api_throttle.redis.from_url')
@patch('pe_scanner.data.api_throttle.REDIS_ENABLED', True)
def test_throttle_redis_mode_stats(mock_from_url, mock_redis):
    """Test stats retrieval in Redis mode."""
    mock_redis.get.side_effect = [str(YAHOO_BURST_LIMIT), "42"]  # tokens, hourly count
    mock_from_url.return_value = mock_redis
    
    throttle = YahooAPIThrottle()
    stats = throttle.get_stats()
    
    assert stats["mode"] == "redis"
    assert stats["available_tokens"] == YAHOO_BURST_LIMIT
    assert stats["requests_this_hour"] == 42


# =============================================================================
# Test Global Functions
# =============================================================================

@patch('pe_scanner.data.api_throttle.get_throttle')
def test_acquire_yahoo_api_token_success(mock_get_throttle):
    """Test global acquire function."""
    mock_throttle = Mock()
    mock_throttle.acquire.return_value = True
    mock_get_throttle.return_value = mock_throttle
    
    result = acquire_yahoo_api_token(timeout=10.0)
    
    assert result is True
    mock_throttle.acquire.assert_called_once_with(10.0)


@patch('pe_scanner.data.api_throttle.get_throttle')
def test_acquire_yahoo_api_token_timeout(mock_get_throttle):
    """Test global acquire function timeout."""
    mock_throttle = Mock()
    mock_throttle.acquire.return_value = False
    mock_get_throttle.return_value = mock_throttle
    
    result = acquire_yahoo_api_token(timeout=0.1)
    
    assert result is False


@patch('pe_scanner.data.api_throttle.get_throttle')
def test_get_throttle_stats_function(mock_get_throttle):
    """Test global stats function."""
    mock_throttle = Mock()
    mock_throttle.get_stats.return_value = {"mode": "local"}
    mock_get_throttle.return_value = mock_throttle
    
    stats = get_throttle_stats()
    
    assert stats["mode"] == "local"
    mock_throttle.get_stats.assert_called_once()


# =============================================================================
# Test Concurrent Access
# =============================================================================

@patch('pe_scanner.data.api_throttle.REDIS_ENABLED', False)
def test_throttle_concurrent_access():
    """Test throttle handles concurrent requests correctly."""
    import threading
    
    throttle = YahooAPIThrottle()
    results = []
    
    def acquire_token():
        result = throttle.acquire(timeout=2.0)
        results.append(result)
    
    # Try to acquire more tokens than burst limit concurrently
    threads = []
    for _ in range(YAHOO_BURST_LIMIT + 2):
        thread = threading.Thread(target=acquire_token)
        threads.append(thread)
        thread.start()
    
    for thread in threads:
        thread.join()
    
    # Should have some successes and some failures/timeouts
    successes = sum(1 for r in results if r is True)
    assert successes <= YAHOO_BURST_LIMIT + 1  # Allow some refill during test


# =============================================================================
# Test Rate Limit Protection
# =============================================================================

@patch('pe_scanner.data.api_throttle.REDIS_ENABLED', False)
def test_throttle_prevents_yahoo_ban():
    """Test throttle enforces safe rate limit (2 req/sec)."""
    throttle = YahooAPIThrottle()
    
    start_time = time.time()
    request_count = 0
    
    # Try to make 10 requests
    for _ in range(10):
        if throttle.acquire(timeout=10.0):
            request_count += 1
    
    elapsed = time.time() - start_time
    
    # At 2 req/sec, 10 requests should take ~5 seconds (after burst)
    # Burst allows first 5 immediately, then need to wait for remaining 5
    # 5 remaining * 0.5s per token = 2.5s minimum
    assert request_count == 10
    assert elapsed >= 2.0  # Should have some throttling delay

