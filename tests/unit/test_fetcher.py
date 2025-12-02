"""
Unit tests for Yahoo Finance Data Fetcher Module
"""

import pytest
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, MagicMock

from pe_scanner.data.fetcher import (
    MarketData,
    FetchResult,
    MarketDataCache,
    CacheEntry,
    fetch_market_data,
    batch_fetch,
    clear_cache,
    get_cache_stats,
    _safe_get,
    _extract_market_data,
)


# =============================================================================
# MarketData Tests
# =============================================================================


class TestMarketData:
    """Tests for MarketData dataclass."""

    def test_market_data_creation(self):
        """Test basic MarketData creation."""
        data = MarketData(
            ticker="HOOD",
            current_price=114.30,
            trailing_pe=73.27,
            forward_pe=156.58,
        )
        assert data.ticker == "HOOD"
        assert data.current_price == 114.30
        assert data.trailing_pe == 73.27
        assert data.forward_pe == 156.58

    def test_market_data_is_complete(self):
        """Test is_complete property."""
        # Complete data
        complete = MarketData(
            ticker="HOOD",
            current_price=114.30,
            trailing_pe=73.27,
        )
        assert complete.is_complete is True

        # Missing price
        incomplete = MarketData(ticker="HOOD", trailing_pe=73.27)
        assert incomplete.is_complete is False

    def test_market_data_has_pe_data(self):
        """Test has_pe_data property."""
        # Has both P/E values
        with_pe = MarketData(
            ticker="HOOD",
            trailing_pe=73.27,
            forward_pe=156.58,
        )
        assert with_pe.has_pe_data is True

        # Missing forward P/E
        missing_forward = MarketData(ticker="HOOD", trailing_pe=73.27)
        assert missing_forward.has_pe_data is False

        # Missing trailing P/E
        missing_trailing = MarketData(ticker="HOOD", forward_pe=156.58)
        assert missing_trailing.has_pe_data is False

    def test_market_data_defaults(self):
        """Test default values."""
        data = MarketData(ticker="TEST")
        assert data.currency == "USD"
        assert data.data_source == "yahoo_finance"
        assert data.fetch_errors == []
        assert isinstance(data.last_updated, datetime)


# =============================================================================
# Cache Tests
# =============================================================================


class TestMarketDataCache:
    """Tests for MarketDataCache class."""

    def test_cache_get_miss(self):
        """Test cache miss returns None."""
        cache = MarketDataCache()
        result = cache.get("NONEXISTENT")
        assert result is None

    def test_cache_set_and_get(self):
        """Test setting and getting cache values."""
        cache = MarketDataCache()
        data = MarketData(ticker="HOOD", current_price=100.0)

        cache.set("HOOD", data, ttl_seconds=3600)
        result = cache.get("HOOD")

        assert result is not None
        assert result.ticker == "HOOD"
        assert result.current_price == 100.0

    def test_cache_case_insensitive(self):
        """Test cache is case insensitive."""
        cache = MarketDataCache()
        data = MarketData(ticker="HOOD", current_price=100.0)

        cache.set("hood", data, ttl_seconds=3600)

        # Should find with different cases
        assert cache.get("HOOD") is not None
        assert cache.get("Hood") is not None
        assert cache.get("hood") is not None

    def test_cache_expiration(self):
        """Test cache entries expire correctly."""
        cache = MarketDataCache()
        data = MarketData(ticker="HOOD")

        # Set with very short TTL
        cache.set("HOOD", data, ttl_seconds=0)

        # Should be expired
        result = cache.get("HOOD")
        assert result is None

    def test_cache_clear(self):
        """Test cache clearing."""
        cache = MarketDataCache()
        cache.set("HOOD", MarketData(ticker="HOOD"), ttl_seconds=3600)
        cache.set("AAPL", MarketData(ticker="AAPL"), ttl_seconds=3600)

        count = cache.clear()

        assert count == 2
        assert cache.get("HOOD") is None
        assert cache.get("AAPL") is None

    def test_cache_stats(self):
        """Test cache statistics."""
        cache = MarketDataCache()
        data = MarketData(ticker="HOOD")
        cache.set("HOOD", data, ttl_seconds=3600)

        # Generate hits and misses
        cache.get("HOOD")  # hit
        cache.get("HOOD")  # hit
        cache.get("NONEXISTENT")  # miss

        stats = cache.get_stats()

        assert stats["size"] == 1
        assert stats["hits"] == 2
        assert stats["misses"] == 1
        assert stats["hit_rate"] == 2 / 3


# =============================================================================
# Helper Function Tests
# =============================================================================


class TestSafeGet:
    """Tests for _safe_get helper function."""

    def test_safe_get_valid_float(self):
        """Test extracting valid float."""
        info = {"price": 100.50}
        result = _safe_get(info, "price")
        assert result == 100.50

    def test_safe_get_valid_int(self):
        """Test extracting valid int (converted to float)."""
        info = {"price": 100}
        result = _safe_get(info, "price")
        assert result == 100.0

    def test_safe_get_missing_key(self):
        """Test missing key returns default."""
        info = {}
        result = _safe_get(info, "price", default=0.0)
        assert result == 0.0

    def test_safe_get_none_value(self):
        """Test None value returns default."""
        info = {"price": None}
        result = _safe_get(info, "price", default=0.0)
        assert result == 0.0

    def test_safe_get_string_value(self):
        """Test string value returns default."""
        info = {"price": "N/A"}
        result = _safe_get(info, "price")
        assert result is None

    def test_safe_get_nan(self):
        """Test NaN returns default."""
        import math
        info = {"price": float('nan')}
        result = _safe_get(info, "price")
        assert result is None

    def test_safe_get_inf(self):
        """Test infinity returns default."""
        info = {"price": float('inf')}
        result = _safe_get(info, "price")
        assert result is None


# =============================================================================
# fetch_market_data Tests
# =============================================================================


class TestFetchMarketData:
    """Tests for fetch_market_data function."""

    def test_fetch_invalid_ticker_empty(self):
        """Test empty ticker raises ValueError."""
        with pytest.raises(ValueError, match="non-empty string"):
            fetch_market_data("")

    def test_fetch_invalid_ticker_whitespace(self):
        """Test whitespace ticker raises ValueError."""
        with pytest.raises(ValueError, match="empty or whitespace"):
            fetch_market_data("   ")

    def test_fetch_invalid_ticker_none(self):
        """Test None ticker raises ValueError."""
        with pytest.raises(ValueError, match="non-empty string"):
            fetch_market_data(None)

    def test_fetch_normalizes_ticker(self):
        """Test ticker is normalized to uppercase."""
        with patch('pe_scanner.data.fetcher.yf.Ticker') as mock_ticker:
            mock_ticker.return_value.info = {
                "shortName": "Test",
                "currentPrice": 100.0,
            }
            data = fetch_market_data("  hood  ", use_cache=False)
            assert data.ticker == "HOOD"

    @patch('pe_scanner.data.fetcher.yf.Ticker')
    def test_fetch_extracts_all_fields(self, mock_ticker_class):
        """Test all fields are extracted correctly."""
        mock_ticker_class.return_value.info = {
            "shortName": "Robinhood Markets, Inc.",
            "currentPrice": 114.30,
            "trailingPE": 73.27,
            "forwardPE": 156.58,
            "trailingEps": 1.56,
            "forwardEps": 0.73,
            "marketCap": 100000000000,
            "currency": "USD",
        }

        data = fetch_market_data("HOOD", use_cache=False)

        assert data.ticker == "HOOD"
        assert data.company_name == "Robinhood Markets, Inc."
        assert data.current_price == 114.30
        assert data.trailing_pe == 73.27
        assert data.forward_pe == 156.58
        assert data.trailing_eps == 1.56
        assert data.forward_eps == 0.73
        assert data.market_cap == 100000000000
        assert data.currency == "USD"

    @patch('pe_scanner.data.fetcher.yf.Ticker')
    def test_fetch_handles_api_error(self, mock_ticker_class):
        """Test API errors are handled gracefully."""
        mock_ticker_class.side_effect = Exception("Network error")

        data = fetch_market_data("HOOD", use_cache=False)

        assert data.ticker == "HOOD"
        assert len(data.fetch_errors) > 0
        assert "Network error" in data.fetch_errors[0]


# =============================================================================
# batch_fetch Tests
# =============================================================================


class TestBatchFetch:
    """Tests for batch_fetch function."""

    def test_batch_fetch_empty_list(self):
        """Test empty ticker list returns empty result."""
        result = batch_fetch([])

        assert len(result.successful) == 0
        assert len(result.failed) == 0
        assert result.cache_hits == 0
        assert result.api_calls == 0

    def test_batch_fetch_deduplicates(self):
        """Test duplicate tickers are deduplicated."""
        with patch('pe_scanner.data.fetcher.yf.Ticker') as mock_ticker:
            mock_ticker.return_value.info = {
                "shortName": "Test",
                "currentPrice": 100.0,
            }

            # Clear cache first
            clear_cache()

            result = batch_fetch(
                ["HOOD", "hood", "HOOD", "  HOOD  "],
                use_cache=False,
                rate_limit_delay=0,
            )

            # Should only fetch once despite duplicates
            assert result.api_calls == 1

    @patch('pe_scanner.data.fetcher.yf.Ticker')
    def test_batch_fetch_success(self, mock_ticker_class):
        """Test successful batch fetch."""
        mock_ticker_class.return_value.info = {
            "shortName": "Test Company",
            "currentPrice": 100.0,
            "trailingPE": 20.0,
            "forwardPE": 15.0,
        }

        clear_cache()
        result = batch_fetch(["AAPL", "MSFT"], use_cache=False, rate_limit_delay=0)

        assert len(result.successful) == 2
        assert len(result.failed) == 0
        assert result.api_calls == 2
        assert result.total_time_seconds > 0

    @patch('pe_scanner.data.fetcher.yf.Ticker')
    def test_batch_fetch_partial_failure(self, mock_ticker_class):
        """Test batch fetch with some failures."""
        def side_effect(ticker):
            mock = Mock()
            if ticker == "INVALID":
                mock.info = {}  # Empty info, no price
            else:
                mock.info = {
                    "shortName": "Test",
                    "currentPrice": 100.0,
                }
            return mock

        mock_ticker_class.side_effect = side_effect
        clear_cache()

        result = batch_fetch(
            ["AAPL", "INVALID"],
            use_cache=False,
            rate_limit_delay=0,
        )

        assert len(result.successful) == 1
        assert len(result.failed) == 1
        assert result.failed[0][0] == "INVALID"


# =============================================================================
# Integration-style Tests (with real API if needed)
# =============================================================================


@pytest.mark.integration
class TestFetcherIntegration:
    """Integration tests that may call real API. Skip in CI."""

    def test_fetch_real_hood(self):
        """Test fetching real HOOD data."""
        data = fetch_market_data("HOOD")

        assert data.ticker == "HOOD"
        assert data.current_price is not None
        assert data.current_price > 0
        # HOOD should have P/E data (it's a profitable company now)
        assert data.company_name is not None

    def test_fetch_real_uk_stock(self):
        """Test fetching real UK stock (BATS.L)."""
        data = fetch_market_data("BATS.L")

        assert data.ticker == "BATS.L"
        assert data.currency == "GBp"  # Pence
        # Note: forward_pe might be < 1.0 due to pence/pounds issue
        # This is the data quality issue Task 5 addresses


if __name__ == "__main__":
    pytest.main([__file__, "-v"])


