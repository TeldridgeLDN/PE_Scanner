"""
Yahoo Finance Data Fetcher Module

Fetches market data using yfinance library including:
- Current price
- Trailing P/E (TTM)
- Forward P/E (FY1 estimate)
- Trailing EPS (TTM)
- Forward EPS (FY1 estimate)
- Market cap
- Last updated timestamp

Implements caching to reduce API calls and rate limiting handling.
Configuration is loaded from config.yaml when available.
"""

import logging
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from pathlib import Path
from threading import Lock
from typing import Optional

import yaml
import yfinance as yf

logger = logging.getLogger(__name__)


# =============================================================================
# Configuration
# =============================================================================


@dataclass
class FetcherConfig:
    """Configuration for the data fetcher."""

    cache_ttl: int = 3600  # seconds
    rate_limit_delay: float = 0.2  # seconds between API calls
    max_concurrent: int = 5  # for future async support
    max_retries: int = 3
    timeout: int = 30  # seconds


def _load_config() -> FetcherConfig:
    """
    Load fetcher configuration from config.yaml.

    Searches for config.yaml in:
    1. Current working directory
    2. Project root (parent directories up to 3 levels)

    Returns:
        FetcherConfig with values from file or defaults
    """
    config_paths = [
        Path.cwd() / "config.yaml",
        Path.cwd().parent / "config.yaml",
        Path(__file__).parent.parent.parent.parent / "config.yaml",  # src/../config.yaml
    ]

    for config_path in config_paths:
        if config_path.exists():
            try:
                with open(config_path) as f:
                    config_data = yaml.safe_load(f)

                data_config = config_data.get("data", {})
                return FetcherConfig(
                    cache_ttl=data_config.get("cache_ttl", 3600),
                    rate_limit_delay=data_config.get("rate_limit_delay", 0.2),
                    max_concurrent=data_config.get("max_concurrent", 5),
                    max_retries=data_config.get("max_retries", 3),
                    timeout=data_config.get("timeout", 30),
                )
            except Exception as e:
                logger.warning(f"Failed to load config from {config_path}: {e}")

    logger.debug("No config.yaml found, using defaults")
    return FetcherConfig()


# Global config instance (lazy loaded)
_config: Optional[FetcherConfig] = None


def get_config() -> FetcherConfig:
    """Get the fetcher configuration (loaded once, cached)."""
    global _config
    if _config is None:
        _config = _load_config()
        logger.info(
            f"Fetcher config: cache_ttl={_config.cache_ttl}s, "
            f"rate_limit_delay={_config.rate_limit_delay}s"
        )
    return _config


def reload_config() -> FetcherConfig:
    """Force reload of configuration from disk."""
    global _config
    _config = None
    return get_config()


# =============================================================================
# Data Classes
# =============================================================================


@dataclass
class MarketData:
    """Market data for a single ticker from Yahoo Finance."""

    ticker: str
    current_price: Optional[float] = None
    trailing_pe: Optional[float] = None
    forward_pe: Optional[float] = None
    trailing_eps: Optional[float] = None
    forward_eps: Optional[float] = None
    market_cap: Optional[float] = None
    company_name: Optional[str] = None
    currency: str = "USD"
    last_updated: datetime = field(default_factory=datetime.now)
    data_source: str = "yahoo_finance"
    fetch_errors: list[str] = field(default_factory=list)

    @property
    def fetched_at(self) -> datetime:
        """Alias for last_updated for CLI compatibility."""
        return self.last_updated

    @property
    def is_complete(self) -> bool:
        """Check if all essential fields have data."""
        return all([
            self.current_price is not None,
            self.trailing_pe is not None or self.forward_pe is not None,
        ])

    @property
    def has_pe_data(self) -> bool:
        """Check if P/E data is available for compression analysis."""
        return self.trailing_pe is not None and self.forward_pe is not None


@dataclass
class FetchResult:
    """Result of a batch fetch operation."""

    successful: list[MarketData] = field(default_factory=list)
    failed: list[tuple[str, str]] = field(default_factory=list)  # (ticker, error_message)
    cache_hits: int = 0
    api_calls: int = 0
    total_time_seconds: float = 0.0

    @property
    def data(self) -> dict[str, MarketData]:
        """Get successful results as a dict keyed by ticker."""
        return {md.ticker: md for md in self.successful}

    @property
    def errors(self) -> dict[str, str]:
        """Get failed results as a dict keyed by ticker."""
        return {ticker: error for ticker, error in self.failed}


# =============================================================================
# Cache Implementation
# =============================================================================


@dataclass
class CacheEntry:
    """A single cache entry with expiration tracking."""

    data: MarketData
    expires_at: datetime


class MarketDataCache:
    """Thread-safe in-memory cache for market data with TTL support."""

    def __init__(self) -> None:
        self._cache: dict[str, CacheEntry] = {}
        self._lock = Lock()
        self._hits = 0
        self._misses = 0

    def get(self, ticker: str) -> Optional[MarketData]:
        """
        Get cached data for a ticker if it exists and hasn't expired.

        Args:
            ticker: Stock ticker symbol

        Returns:
            MarketData if found and valid, None otherwise
        """
        with self._lock:
            entry = self._cache.get(ticker.upper())
            if entry is None:
                self._misses += 1
                return None

            if datetime.now() > entry.expires_at:
                # Entry expired, remove it
                del self._cache[ticker.upper()]
                self._misses += 1
                return None

            self._hits += 1
            return entry.data

    def set(self, ticker: str, data: MarketData, ttl_seconds: int) -> None:
        """
        Store market data in cache with TTL.

        Args:
            ticker: Stock ticker symbol
            data: MarketData to cache
            ttl_seconds: Time-to-live in seconds
        """
        with self._lock:
            expires_at = datetime.now() + timedelta(seconds=ttl_seconds)
            self._cache[ticker.upper()] = CacheEntry(data=data, expires_at=expires_at)

    def clear(self) -> int:
        """Clear all cached entries. Returns number of entries cleared."""
        with self._lock:
            count = len(self._cache)
            self._cache.clear()
            self._hits = 0
            self._misses = 0
            return count

    def get_stats(self) -> dict:
        """Get cache statistics."""
        with self._lock:
            total = self._hits + self._misses
            return {
                "size": len(self._cache),
                "hits": self._hits,
                "misses": self._misses,
                "hit_rate": self._hits / total if total > 0 else 0.0,
            }


# Global cache instance
_cache = MarketDataCache()


# =============================================================================
# Data Extraction Helpers
# =============================================================================


def _safe_get(info: dict, key: str, default: Optional[float] = None) -> Optional[float]:
    """
    Safely extract a numeric value from yfinance info dict.

    Handles None, 'N/A', inf, and other edge cases.
    """
    value = info.get(key)
    if value is None:
        return default
    if isinstance(value, str):
        return default
    if isinstance(value, (int, float)):
        # Check for infinity or NaN
        import math
        if math.isnan(value) or math.isinf(value):
            return default
        return float(value)
    return default


def _extract_market_data(ticker_symbol: str, yf_ticker: yf.Ticker) -> MarketData:
    """
    Extract MarketData from a yfinance Ticker object.

    Args:
        ticker_symbol: The ticker symbol string
        yf_ticker: yfinance Ticker object with data

    Returns:
        MarketData with extracted fields
    """
    errors: list[str] = []

    try:
        info = yf_ticker.info
    except Exception as e:
        logger.warning(f"Failed to get info for {ticker_symbol}: {e}")
        return MarketData(
            ticker=ticker_symbol,
            fetch_errors=[f"Failed to fetch info: {str(e)}"],
        )

    # Extract current price (try multiple fields)
    current_price = _safe_get(info, "currentPrice")
    if current_price is None:
        current_price = _safe_get(info, "regularMarketPrice")
    if current_price is None:
        current_price = _safe_get(info, "previousClose")
        if current_price is not None:
            errors.append("Using previousClose as current price")

    # Extract P/E ratios
    trailing_pe = _safe_get(info, "trailingPE")
    forward_pe = _safe_get(info, "forwardPE")

    # Extract EPS values
    trailing_eps = _safe_get(info, "trailingEps")
    forward_eps = _safe_get(info, "forwardEps")

    # Extract other fields
    market_cap = _safe_get(info, "marketCap")
    company_name = info.get("shortName") or info.get("longName")
    currency = info.get("currency", "USD")

    # Log missing critical data
    if trailing_pe is None:
        errors.append("Missing trailing P/E")
    if forward_pe is None:
        errors.append("Missing forward P/E")
    if current_price is None:
        errors.append("Missing current price")

    return MarketData(
        ticker=ticker_symbol,
        current_price=current_price,
        trailing_pe=trailing_pe,
        forward_pe=forward_pe,
        trailing_eps=trailing_eps,
        forward_eps=forward_eps,
        market_cap=market_cap,
        company_name=company_name,
        currency=currency if currency else "USD",
        last_updated=datetime.now(),
        data_source="yahoo_finance",
        fetch_errors=errors,
    )


# =============================================================================
# Public API
# =============================================================================


def fetch_market_data(
    ticker: str,
    use_cache: bool = True,
    cache_ttl: Optional[int] = None,
) -> MarketData:
    """
    Fetch market data for a single ticker from Yahoo Finance.

    Args:
        ticker: Stock ticker symbol (e.g., "HOOD", "BATS.L")
        use_cache: Whether to use cached data if available
        cache_ttl: Cache time-to-live in seconds (default: from config.yaml)

    Returns:
        MarketData object with all available fields populated

    Raises:
        ValueError: If ticker is invalid or empty

    Example:
        >>> data = fetch_market_data("HOOD")
        >>> print(f"Current P/E: {data.trailing_pe}")
    """
    if not ticker or not isinstance(ticker, str):
        raise ValueError("Ticker must be a non-empty string")

    ticker = ticker.strip().upper()
    if not ticker:
        raise ValueError("Ticker cannot be empty or whitespace")

    # Use config defaults if not specified
    config = get_config()
    if cache_ttl is None:
        cache_ttl = config.cache_ttl

    # Check cache first
    if use_cache:
        cached = _cache.get(ticker)
        if cached is not None:
            logger.debug(f"Cache hit for {ticker}")
            return cached

    # Fetch from Yahoo Finance
    logger.info(f"Fetching market data for {ticker}")
    try:
        yf_ticker = yf.Ticker(ticker)
        data = _extract_market_data(ticker, yf_ticker)

        # Cache the result
        if use_cache:
            _cache.set(ticker, data, cache_ttl)

        return data

    except Exception as e:
        logger.error(f"Error fetching {ticker}: {e}")
        return MarketData(
            ticker=ticker,
            fetch_errors=[f"Fetch failed: {str(e)}"],
        )


def _fetch_single_ticker(
    ticker: str,
    cache_ttl: int,
    use_cache: bool,
) -> tuple[str, Optional[MarketData], Optional[str]]:
    """
    Fetch a single ticker (used by ThreadPoolExecutor).

    Returns:
        Tuple of (ticker, MarketData or None, error_message or None)
    """
    try:
        yf_ticker = yf.Ticker(ticker)
        data = _extract_market_data(ticker, yf_ticker)

        if data.current_price is not None:
            if use_cache:
                _cache.set(ticker, data, cache_ttl)
            return (ticker, data, None)
        else:
            return (ticker, None, "No price data available")

    except Exception as e:
        logger.error(f"Failed to fetch {ticker}: {e}")
        return (ticker, None, str(e))


def batch_fetch(
    tickers: list[str],
    use_cache: bool = True,
    cache_ttl: Optional[int] = None,
    max_concurrent: Optional[int] = None,
    rate_limit_delay: Optional[float] = None,
) -> FetchResult:
    """
    Fetch market data for multiple tickers efficiently using concurrent requests.

    Uses ThreadPoolExecutor for parallel fetching, significantly improving
    performance for large portfolios. Respects rate limiting between batches.

    Args:
        tickers: List of stock ticker symbols
        use_cache: Whether to use cached data
        cache_ttl: Cache time-to-live in seconds (default: from config.yaml)
        max_concurrent: Maximum concurrent API requests (default: from config.yaml)
        rate_limit_delay: Delay between API calls in seconds (default: from config.yaml)

    Returns:
        FetchResult with successful fetches, failures, and stats

    Example:
        >>> result = batch_fetch(["HOOD", "AAPL", "BATS.L"])
        >>> print(f"Fetched {len(result.successful)} of {len(tickers)}")
    """
    if not tickers:
        return FetchResult()

    # Use config defaults if not specified
    config = get_config()
    if cache_ttl is None:
        cache_ttl = config.cache_ttl
    if max_concurrent is None:
        max_concurrent = config.max_concurrent
    if rate_limit_delay is None:
        rate_limit_delay = config.rate_limit_delay

    start_time = time.time()
    result = FetchResult()

    # Normalize and deduplicate tickers
    unique_tickers = list(dict.fromkeys(t.strip().upper() for t in tickers if t and t.strip()))

    # Separate cached from non-cached
    tickers_to_fetch = []
    for ticker in unique_tickers:
        if use_cache:
            cached = _cache.get(ticker)
            if cached is not None:
                result.successful.append(cached)
                result.cache_hits += 1
                continue
        tickers_to_fetch.append(ticker)

    # Concurrent fetch for non-cached tickers
    if tickers_to_fetch:
        logger.info(f"Concurrent fetch for {len(tickers_to_fetch)} tickers (max_workers={max_concurrent})")

        with ThreadPoolExecutor(max_workers=max_concurrent) as executor:
            # Submit all fetch tasks
            futures = {
                executor.submit(_fetch_single_ticker, ticker, cache_ttl, use_cache): ticker
                for ticker in tickers_to_fetch
            }

            # Collect results as they complete
            for future in as_completed(futures):
                ticker, data, error = future.result()
                result.api_calls += 1

                if data is not None:
                    result.successful.append(data)
                else:
                    result.failed.append((ticker, error or "Unknown error"))

                # Optional rate limiting (between result processing, not blocking)
                if rate_limit_delay > 0 and result.api_calls < len(tickers_to_fetch):
                    time.sleep(rate_limit_delay / max_concurrent)

    result.total_time_seconds = time.time() - start_time
    logger.info(
        f"Batch fetch complete: {len(result.successful)} successful, "
        f"{len(result.failed)} failed, {result.cache_hits} cache hits, "
        f"{result.total_time_seconds:.2f}s"
    )

    return result


def clear_cache() -> int:
    """
    Clear the market data cache.

    Returns:
        Number of cached entries cleared
    """
    count = _cache.clear()
    logger.info(f"Cache cleared: {count} entries removed")
    return count


def get_cache_stats() -> dict:
    """
    Get cache statistics.

    Returns:
        Dict with keys: "size", "hits", "misses", "hit_rate"
    """
    return _cache.get_stats()
