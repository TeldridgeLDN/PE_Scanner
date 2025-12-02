"""
Rate Limiting System for PE Scanner API

Implements 3-tier rate limiting:
- Anonymous (IP-based): 3 tickers/day
- Free users (account-based): 10 tickers/day  
- Pro/Premium users: Unlimited

Uses Redis for distributed rate limiting across multiple server instances.

NOTE: This module handles SINGLE-TICKER searches (website search bar).
Portfolio CSV uploads will have separate rate limits in Task 57:
- Free: 5 uploads/day, max 50 tickers per upload
- Pro: Unlimited uploads, max 500 tickers per upload
- Premium: Unlimited uploads, max 1000 tickers per upload

See .taskmaster/docs/portfolio_rate_limiting_strategy.md for full details.
"""

import logging
import os
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Optional, Tuple
from functools import wraps

from flask import request, jsonify
import redis

logger = logging.getLogger(__name__)


# =============================================================================
# Configuration
# =============================================================================

# Rate limit configuration
RATE_LIMITS = {
    "anonymous": 3,      # 3 tickers/day for anonymous users (IP-based)
    "free": 10,          # 10 tickers/day for free accounts
    "pro": -1,           # Unlimited for Pro tier
    "premium": -1,       # Unlimited for Premium tier
}

# Time window for rate limits (24 hours in seconds)
RATE_LIMIT_WINDOW = 86400

# Redis configuration
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")
REDIS_ENABLED = os.getenv("REDIS_ENABLED", "true").lower() == "true"


# =============================================================================
# Redis Client
# =============================================================================

class RedisClient:
    """Singleton Redis client with connection pooling."""
    
    _instance: Optional[redis.Redis] = None
    _enabled: bool = REDIS_ENABLED
    
    @classmethod
    def get_client(cls) -> Optional[redis.Redis]:
        """
        Get Redis client instance (singleton).
        
        Returns:
            Redis client if enabled and connected, None otherwise
        """
        if not cls._enabled:
            logger.warning("Redis is disabled - rate limiting will not work")
            return None
            
        if cls._instance is None:
            try:
                cls._instance = redis.from_url(
                    REDIS_URL,
                    decode_responses=True,
                    socket_connect_timeout=5,
                    socket_timeout=5,
                    retry_on_timeout=True,
                )
                # Test connection
                cls._instance.ping()
                logger.info("Redis connection established")
            except (redis.ConnectionError, redis.TimeoutError) as e:
                logger.error(f"Failed to connect to Redis: {e}")
                cls._instance = None
                
        return cls._instance
    
    @classmethod
    def is_available(cls) -> bool:
        """Check if Redis is available."""
        client = cls.get_client()
        if client is None:
            return False
        try:
            client.ping()
            return True
        except (redis.ConnectionError, redis.TimeoutError):
            return False


# =============================================================================
# Rate Limit Result
# =============================================================================

@dataclass
class RateLimitResult:
    """Result of a rate limit check."""
    
    allowed: bool
    remaining: int
    limit: int
    reset_at: datetime
    tier: str
    suggest_upgrade: bool = False
    
    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return {
            "allowed": self.allowed,
            "remaining": self.remaining,
            "limit": self.limit,
            "reset_at": self.reset_at.isoformat() + "Z",
            "tier": self.tier,
            "suggest_upgrade": self.suggest_upgrade,
        }


# =============================================================================
# Helper Functions
# =============================================================================

def get_client_ip(req) -> str:
    """
    Extract client IP from request headers.
    
    Handles x-forwarded-for header for proxied requests (Railway, Vercel, etc).
    
    Args:
        req: Flask request object
        
    Returns:
        Client IP address
    """
    # Check x-forwarded-for header (set by proxies)
    forwarded_for = req.headers.get("X-Forwarded-For")
    if forwarded_for:
        # Take first IP in comma-separated list (client IP)
        return forwarded_for.split(",")[0].strip()
    
    # Check x-real-ip header (alternative proxy header)
    real_ip = req.headers.get("X-Real-IP")
    if real_ip:
        return real_ip.strip()
    
    # Fallback to direct connection IP
    return req.remote_addr or "unknown"


def get_user_tier(req) -> Tuple[str, Optional[str]]:
    """
    Determine user tier from request.
    
    For now, this is a stub that returns 'anonymous'.
    When Clerk integration is added (Task 35+), this will check:
    - Authorization header for JWT
    - Decode JWT to get user_id and plan
    - Return tier (free/pro/premium) and user_id
    
    Args:
        req: Flask request object
        
    Returns:
        Tuple of (tier, user_id)
    """
    # TODO: Add Clerk JWT validation when auth is implemented
    # auth_header = req.headers.get("Authorization")
    # if auth_header and auth_header.startswith("Bearer "):
    #     token = auth_header[7:]
    #     user = decode_jwt(token)
    #     return (user.plan, user.id)
    
    return ("anonymous", None)


def get_rate_limit_key(tier: str, identifier: str) -> str:
    """
    Generate Redis key for rate limiting.
    
    Keys are scoped by date to automatically reset after 24 hours.
    
    Args:
        tier: User tier (anonymous, free, pro, premium)
        identifier: IP address or user_id
        
    Returns:
        Redis key string
    """
    # Get current date in UTC (YYYY-MM-DD format)
    date_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    
    # Format: ratelimit:{tier}:{identifier}:{date}
    return f"ratelimit:{tier}:{identifier}:{date_str}"


def get_reset_time() -> datetime:
    """
    Calculate when the rate limit resets (midnight UTC tomorrow).
    
    Returns:
        datetime object for next midnight UTC
    """
    now = datetime.now(timezone.utc)
    # Get tomorrow's date, set time to 00:00:00
    tomorrow = datetime(
        now.year, now.month, now.day,
        tzinfo=timezone.utc
    ).timestamp() + RATE_LIMIT_WINDOW
    
    return datetime.fromtimestamp(tomorrow, tz=timezone.utc)


# =============================================================================
# Rate Limit Core Logic
# =============================================================================

def check_rate_limit(tier: str, identifier: str) -> RateLimitResult:
    """
    Check if request is within rate limit.
    
    Args:
        tier: User tier (anonymous, free, pro, premium)
        identifier: IP address or user_id
        
    Returns:
        RateLimitResult with limit status
    """
    # Pro/Premium users have unlimited access
    limit = RATE_LIMITS.get(tier, RATE_LIMITS["anonymous"])
    if limit == -1:
        return RateLimitResult(
            allowed=True,
            remaining=-1,
            limit=-1,
            reset_at=get_reset_time(),
            tier=tier,
            suggest_upgrade=False,
        )
    
    # Check Redis availability
    client = RedisClient.get_client()
    if client is None:
        # Redis unavailable - fail open (allow request but log warning)
        logger.warning(f"Redis unavailable - allowing request for {tier}:{identifier}")
        return RateLimitResult(
            allowed=True,
            remaining=limit,
            limit=limit,
            reset_at=get_reset_time(),
            tier=tier,
            suggest_upgrade=False,
        )
    
    # Get Redis key
    key = get_rate_limit_key(tier, identifier)
    
    try:
        # Get current count
        current = client.get(key)
        count = int(current) if current else 0
        
        # Check if limit exceeded
        if count >= limit:
            return RateLimitResult(
                allowed=False,
                remaining=0,
                limit=limit,
                reset_at=get_reset_time(),
                tier=tier,
                suggest_upgrade=(tier == "anonymous"),  # Suggest signup for anon users
            )
        
        # Within limit
        remaining = limit - count
        return RateLimitResult(
            allowed=True,
            remaining=remaining,
            limit=limit,
            reset_at=get_reset_time(),
            tier=tier,
            suggest_upgrade=False,
        )
        
    except redis.RedisError as e:
        logger.error(f"Redis error during rate limit check: {e}")
        # Fail open - allow request
        return RateLimitResult(
            allowed=True,
            remaining=limit,
            limit=limit,
            reset_at=get_reset_time(),
            tier=tier,
            suggest_upgrade=False,
        )


def record_usage(tier: str, identifier: str, ticker: str) -> None:
    """
    Record a successful API usage.
    
    Increments the rate limit counter in Redis.
    
    Args:
        tier: User tier (anonymous, free, pro, premium)
        identifier: IP address or user_id
        ticker: Ticker symbol analyzed
    """
    # Pro/Premium users - track for analytics only, don't increment limit
    limit = RATE_LIMITS.get(tier, RATE_LIMITS["anonymous"])
    
    # Get Redis client
    client = RedisClient.get_client()
    if client is None:
        logger.warning(f"Redis unavailable - cannot record usage for {tier}:{identifier}")
        return
    
    # Get Redis key
    key = get_rate_limit_key(tier, identifier)
    
    try:
        # Increment counter
        if limit != -1:  # Only increment for limited tiers
            pipeline = client.pipeline()
            pipeline.incr(key)
            # Set expiry to 24 hours + 1 hour buffer
            pipeline.expire(key, RATE_LIMIT_WINDOW + 3600)
            pipeline.execute()
            
            logger.info(f"Recorded usage: {tier}:{identifier} analyzed {ticker}")
        
        # TODO: Add analytics tracking for Pro/Premium users
        # This could feed into usage dashboards, popular ticker tracking, etc.
        
    except redis.RedisError as e:
        logger.error(f"Redis error during usage recording: {e}")


# =============================================================================
# Flask Decorator
# =============================================================================

def rate_limit_check(f):
    """
    Flask decorator to enforce rate limiting on endpoints.
    
    Usage:
        @app.route('/api/analyze/<ticker>')
        @rate_limit_check
        def analyze_stock(ticker):
            # ... endpoint logic ...
    
    Returns 429 status with rate limit headers if limit exceeded.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Get user tier and identifier
        tier, user_id = get_user_tier(request)
        identifier = user_id if user_id else get_client_ip(request)
        
        # Check rate limit
        result = check_rate_limit(tier, identifier)
        
        # Add rate limit headers to response (even if allowed)
        def add_rate_limit_headers(response):
            """Add rate limit headers to response."""
            response.headers["X-RateLimit-Limit"] = str(result.limit)
            response.headers["X-RateLimit-Remaining"] = str(result.remaining)
            response.headers["X-RateLimit-Reset"] = str(int(result.reset_at.timestamp()))
            return response
        
        # If rate limit exceeded, return 429 error
        if not result.allowed:
            # Calculate retry-after in seconds
            retry_after = int((result.reset_at - datetime.now(timezone.utc)).total_seconds())
            
            # Build friendly, helpful error message with urgency
            if result.suggest_upgrade:
                # Anonymous user - encourage signup with market movement urgency
                message = (
                    f"You've hit your daily limit of {result.limit} free analyses. "
                    f"Markets are moving—prices and signals update throughout the day. "
                    f"Sign up free for {RATE_LIMITS['free']} daily analyses and never miss a signal shift!"
                )
            else:
                # Free user - encourage upgrade with FOMO
                message = (
                    f"You've used all {result.limit} of your daily analyses—you're clearly active! "
                    f"Stock prices change by the minute. Upgrade to Pro for unlimited real-time analysis "
                    f"so you never miss when a signal flips. Or wait until tomorrow when your limit resets."
                )
            
            # Create error response with conversion hooks
            error_response = {
                "error": "RateLimitExceeded",
                "message": message,
                "remaining": result.remaining,
                "reset_at": result.reset_at.isoformat() + "Z",
                "limit": result.limit,
                "tier": result.tier,
                "upgrade_url": "https://pe-scanner.com/pricing" if tier != "pro" else None,
                "signup_url": "https://pe-scanner.com/sign-up" if result.suggest_upgrade else None,
                "timestamp": datetime.now(timezone.utc).isoformat() + "Z",
                "hint": "Stock signals update throughout the day as prices move. Don't miss the next shift!" if result.suggest_upgrade else "Markets don't wait. Upgrade for unlimited real-time analysis.",
            }
            
            response = jsonify(error_response)
            response.status_code = 429
            response.headers["Retry-After"] = str(retry_after)
            response = add_rate_limit_headers(response)
            
            return response
        
        # Rate limit OK - execute endpoint
        response = f(*args, **kwargs)
        
        # Record usage after successful analysis
        ticker = kwargs.get("ticker") or args[0] if args else "unknown"
        record_usage(tier, identifier, ticker)
        
        # Add rate limit headers to success response
        if hasattr(response, "headers"):
            response = add_rate_limit_headers(response)
        
        return response
    
    return decorated_function


# =============================================================================
# Admin/Debug Functions
# =============================================================================

def get_usage_stats(tier: str, identifier: str) -> dict:
    """
    Get current usage stats for a user/IP.
    
    Args:
        tier: User tier
        identifier: IP address or user_id
        
    Returns:
        Dictionary with usage stats
    """
    client = RedisClient.get_client()
    if client is None:
        return {"error": "Redis unavailable"}
    
    key = get_rate_limit_key(tier, identifier)
    limit = RATE_LIMITS.get(tier, RATE_LIMITS["anonymous"])
    
    try:
        count = client.get(key)
        count = int(count) if count else 0
        
        return {
            "tier": tier,
            "identifier": identifier,
            "limit": limit,
            "used": count,
            "remaining": max(0, limit - count) if limit != -1 else -1,
            "reset_at": get_reset_time().isoformat() + "Z",
        }
    except redis.RedisError as e:
        return {"error": f"Redis error: {str(e)}"}


def reset_user_limit(tier: str, identifier: str) -> bool:
    """
    Reset rate limit for a specific user/IP (admin function).
    
    Args:
        tier: User tier
        identifier: IP address or user_id
        
    Returns:
        True if successful, False otherwise
    """
    client = RedisClient.get_client()
    if client is None:
        return False
    
    key = get_rate_limit_key(tier, identifier)
    
    try:
        client.delete(key)
        logger.info(f"Reset rate limit for {tier}:{identifier}")
        return True
    except redis.RedisError as e:
        logger.error(f"Failed to reset rate limit: {e}")
        return False

