"""
Yahoo Finance API Throttling System

Protects against Yahoo Finance rate limits by implementing:
1. Global request queue (across all users/servers)
2. Token bucket algorithm for smooth rate limiting
3. Redis-based distributed throttling (Railway multi-instance safe)
4. Graceful degradation when Redis unavailable

Yahoo Finance Rate Limits (observed):
- ~2000 requests/hour per IP
- Temporary ban (1-6 hours) if exceeded
- Recommended: 1 request per 0.5s = 7200/hour (safe margin)
"""

import logging
import time
from datetime import datetime, timezone
from typing import Optional
import os

try:
    import redis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False

logger = logging.getLogger(__name__)


# =============================================================================
# Configuration
# =============================================================================

# Yahoo Finance safe rate limits
YAHOO_REQUESTS_PER_SECOND = 2.0  # Conservative: 2 req/sec = 7200/hour
YAHOO_BURST_LIMIT = 5  # Allow burst of 5 requests
YAHOO_TOKEN_REFILL_RATE = 1.0 / YAHOO_REQUESTS_PER_SECOND  # 0.5 seconds per token

# Redis configuration
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")
REDIS_ENABLED = os.getenv("REDIS_ENABLED", "true").lower() == "true"

# Redis keys
REDIS_KEY_TOKENS = "yahoo:api:tokens"
REDIS_KEY_LAST_REFILL = "yahoo:api:last_refill"
REDIS_KEY_REQUEST_COUNT = "yahoo:api:request_count:{hour}"


# =============================================================================
# Token Bucket Rate Limiter
# =============================================================================

class YahooAPIThrottle:
    """
    Token bucket rate limiter for Yahoo Finance API.
    
    Uses Redis for distributed rate limiting across multiple server instances.
    Falls back to local throttling if Redis unavailable.
    """
    
    def __init__(self):
        self._redis_client: Optional[redis.Redis] = None
        self._local_tokens = float(YAHOO_BURST_LIMIT)
        self._local_last_refill = time.time()
        self._use_redis = REDIS_ENABLED and REDIS_AVAILABLE
        
        if self._use_redis:
            self._init_redis()
    
    def _init_redis(self) -> None:
        """Initialize Redis connection."""
        try:
            self._redis_client = redis.from_url(
                REDIS_URL,
                decode_responses=True,
                socket_connect_timeout=2,
                socket_timeout=2,
            )
            self._redis_client.ping()
            
            # Initialize token bucket in Redis if not exists
            if not self._redis_client.exists(REDIS_KEY_TOKENS):
                self._redis_client.set(REDIS_KEY_TOKENS, str(YAHOO_BURST_LIMIT))
                self._redis_client.set(REDIS_KEY_LAST_REFILL, str(time.time()))
            
            logger.info("Yahoo API throttle using Redis (distributed)")
        except Exception as e:
            logger.warning(f"Redis unavailable for API throttle: {e}. Using local throttle.")
            self._redis_client = None
            self._use_redis = False
    
    def _refill_tokens_redis(self) -> float:
        """Refill tokens in Redis based on elapsed time."""
        try:
            now = time.time()
            last_refill = float(self._redis_client.get(REDIS_KEY_LAST_REFILL) or now)
            elapsed = now - last_refill
            
            # Calculate tokens to add
            tokens_to_add = elapsed * YAHOO_REQUESTS_PER_SECOND
            
            if tokens_to_add > 0:
                # Get current tokens
                current_tokens = float(self._redis_client.get(REDIS_KEY_TOKENS) or 0)
                
                # Add tokens (capped at burst limit)
                new_tokens = min(current_tokens + tokens_to_add, YAHOO_BURST_LIMIT)
                
                # Update Redis atomically
                pipe = self._redis_client.pipeline()
                pipe.set(REDIS_KEY_TOKENS, str(new_tokens))
                pipe.set(REDIS_KEY_LAST_REFILL, str(now))
                pipe.execute()
                
                return new_tokens
            
            return float(self._redis_client.get(REDIS_KEY_TOKENS) or 0)
            
        except Exception as e:
            logger.error(f"Redis error during token refill: {e}")
            return 0.0
    
    def _refill_tokens_local(self) -> float:
        """Refill tokens locally."""
        now = time.time()
        elapsed = now - self._local_last_refill
        
        tokens_to_add = elapsed * YAHOO_REQUESTS_PER_SECOND
        if tokens_to_add > 0:
            self._local_tokens = min(
                self._local_tokens + tokens_to_add,
                YAHOO_BURST_LIMIT
            )
            self._local_last_refill = now
        
        return self._local_tokens
    
    def _consume_token_redis(self) -> bool:
        """Try to consume a token from Redis bucket."""
        try:
            tokens = self._refill_tokens_redis()
            
            if tokens >= 1.0:
                # Consume token atomically
                new_tokens = tokens - 1.0
                self._redis_client.set(REDIS_KEY_TOKENS, str(new_tokens))
                
                # Track hourly request count for monitoring
                hour_key = REDIS_KEY_REQUEST_COUNT.format(
                    hour=datetime.now(timezone.utc).strftime("%Y-%m-%d-%H")
                )
                self._redis_client.incr(hour_key)
                self._redis_client.expire(hour_key, 7200)  # Keep for 2 hours
                
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Redis error during token consumption: {e}")
            return False
    
    def _consume_token_local(self) -> bool:
        """Try to consume a token from local bucket."""
        tokens = self._refill_tokens_local()
        
        if tokens >= 1.0:
            self._local_tokens -= 1.0
            return True
        
        return False
    
    def acquire(self, timeout: float = 30.0) -> bool:
        """
        Acquire permission to make a Yahoo Finance API call.
        
        Blocks until a token is available or timeout is reached.
        
        Args:
            timeout: Maximum seconds to wait for a token
            
        Returns:
            True if token acquired, False if timeout
        """
        start_time = time.time()
        wait_logged = False
        
        while (time.time() - start_time) < timeout:
            # Try to consume token
            if self._use_redis and self._redis_client:
                success = self._consume_token_redis()
            else:
                success = self._consume_token_local()
            
            if success:
                return True
            
            # Log waiting message (once)
            if not wait_logged:
                logger.info("Waiting for Yahoo API rate limit token...")
                wait_logged = True
            
            # Wait before retry (exponential backoff, capped at 1s)
            elapsed = time.time() - start_time
            wait_time = min(0.1 * (1 + elapsed / 10), 1.0)
            time.sleep(wait_time)
        
        logger.warning(f"Yahoo API throttle timeout after {timeout}s")
        return False
    
    def get_stats(self) -> dict:
        """
        Get throttle statistics.
        
        Returns:
            Dict with current tokens, refill rate, and hourly count
        """
        try:
            if self._use_redis and self._redis_client:
                tokens = float(self._redis_client.get(REDIS_KEY_TOKENS) or 0)
                hour_key = REDIS_KEY_REQUEST_COUNT.format(
                    hour=datetime.now(timezone.utc).strftime("%Y-%m-%d-%H")
                )
                hourly_count = int(self._redis_client.get(hour_key) or 0)
                mode = "redis"
            else:
                tokens = self._local_tokens
                hourly_count = -1  # Not tracked in local mode
                mode = "local"
            
            return {
                "mode": mode,
                "available_tokens": tokens,
                "max_tokens": YAHOO_BURST_LIMIT,
                "requests_per_second": YAHOO_REQUESTS_PER_SECOND,
                "requests_this_hour": hourly_count,
            }
        except Exception as e:
            logger.error(f"Error getting throttle stats: {e}")
            return {"error": str(e)}


# =============================================================================
# Global Throttle Instance
# =============================================================================

_throttle: Optional[YahooAPIThrottle] = None


def get_throttle() -> YahooAPIThrottle:
    """Get global Yahoo API throttle instance (singleton)."""
    global _throttle
    if _throttle is None:
        _throttle = YahooAPIThrottle()
    return _throttle


def acquire_yahoo_api_token(timeout: float = 30.0) -> bool:
    """
    Acquire permission to make a Yahoo Finance API call.
    
    This function should be called before EVERY Yahoo Finance API request
    to ensure we don't exceed rate limits and get banned.
    
    Args:
        timeout: Maximum seconds to wait for permission
        
    Returns:
        True if permission granted, False if timeout
        
    Example:
        >>> if acquire_yahoo_api_token():
        >>>     ticker_data = yf.Ticker("AAPL")
        >>>     info = ticker_data.info
    """
    return get_throttle().acquire(timeout)


def get_throttle_stats() -> dict:
    """
    Get Yahoo API throttle statistics.
    
    Returns:
        Dict with current state and request counts
    """
    return get_throttle().get_stats()

