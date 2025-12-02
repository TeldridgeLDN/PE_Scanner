"""
Unit tests for Data Correction Module
"""

import pytest
from unittest.mock import Mock, MagicMock

from pe_scanner.data.corrector import (
    CorrectionResult,
    apply_corrections,
    calculate_implied_growth,
    correct_uk_stocks,
    detect_stock_splits,
    is_uk_stock,
)


# =============================================================================
# Helper to create mock MarketData
# =============================================================================


def create_mock_market_data(
    ticker: str,
    forward_pe: float = None,
    forward_eps: float = None,
    trailing_pe: float = None,
    trailing_eps: float = None,
    current_price: float = None,
    currency: str = "USD",
) -> Mock:
    """Create a mock MarketData object for testing."""
    data = Mock()
    data.ticker = ticker
    data.forward_pe = forward_pe
    data.forward_eps = forward_eps
    data.trailing_pe = trailing_pe
    data.trailing_eps = trailing_eps
    data.current_price = current_price
    data.currency = currency
    data.market_cap = None
    data.company_name = ticker
    data.last_updated = None
    data.data_source = "test"
    data.fetch_errors = []
    return data


# =============================================================================
# is_uk_stock Tests
# =============================================================================


class TestIsUkStock:
    """Tests for is_uk_stock function."""

    def test_uk_stock_with_l_suffix(self):
        """Test UK stock detection with .L suffix."""
        assert is_uk_stock("BATS.L") is True
        assert is_uk_stock("RR.L") is True
        assert is_uk_stock("BT-A.L") is True
        assert is_uk_stock("BAB.L") is True

    def test_uk_stock_case_insensitive(self):
        """Test UK stock detection is case insensitive."""
        assert is_uk_stock("bats.l") is True
        assert is_uk_stock("BATS.l") is True
        assert is_uk_stock("bats.L") is True

    def test_non_uk_stocks(self):
        """Test non-UK stocks return False."""
        assert is_uk_stock("HOOD") is False
        assert is_uk_stock("AAPL") is False
        assert is_uk_stock("MSFT") is False

    def test_other_exchanges(self):
        """Test other exchange suffixes return False."""
        assert is_uk_stock("ORA.PA") is False  # Paris
        assert is_uk_stock("SAP.DE") is False  # Germany
        assert is_uk_stock("NESN.SW") is False  # Swiss

    def test_empty_ticker(self):
        """Test empty ticker returns False."""
        assert is_uk_stock("") is False
        assert is_uk_stock(None) is False

    def test_ticker_with_whitespace(self):
        """Test ticker with whitespace is handled."""
        assert is_uk_stock("  BATS.L  ") is True
        assert is_uk_stock("HOOD  ") is False


# =============================================================================
# correct_uk_stocks Tests
# =============================================================================


class TestCorrectUkStocks:
    """Tests for correct_uk_stocks function."""

    def test_correction_applied_low_forward_pe(self):
        """Test 100x correction applied when forward P/E < 1.0."""
        data = create_mock_market_data(
            ticker="BATS.L",
            forward_pe=0.12,
            forward_eps=3.72,
            trailing_pe=31.8,
        )

        result = correct_uk_stocks(data)

        assert result.is_uk_stock is True
        assert result.was_corrected is True
        assert result.correction_factor == 100.0
        assert result.corrected_forward_pe == pytest.approx(12.0, rel=0.01)
        assert result.corrected_forward_eps == pytest.approx(372.0, rel=0.01)
        assert len(result.corrections_applied) > 0

    def test_no_correction_high_forward_pe(self):
        """Test no correction when forward P/E >= 1.0."""
        data = create_mock_market_data(
            ticker="RR.L",
            forward_pe=15.5,
            forward_eps=2.0,
            trailing_pe=20.0,
        )

        result = correct_uk_stocks(data)

        assert result.is_uk_stock is True
        assert result.was_corrected is False
        assert result.corrected_forward_pe == 15.5
        assert result.correction_factor == 1.0

    def test_no_correction_non_uk_stock(self):
        """Test non-UK stocks are not corrected."""
        data = create_mock_market_data(
            ticker="HOOD",
            forward_pe=0.5,  # Low P/E but not UK
            forward_eps=1.0,
        )

        result = correct_uk_stocks(data)

        assert result.is_uk_stock is False
        assert result.was_corrected is False

    def test_missing_forward_pe_flagged(self):
        """Test missing forward P/E is flagged."""
        data = create_mock_market_data(
            ticker="BATS.L",
            forward_pe=None,
        )

        result = correct_uk_stocks(data)

        assert result.was_corrected is False
        assert "Missing forward P/E" in result.flags_raised[0]

    def test_auto_correct_disabled(self):
        """Test correction not applied when auto_correct=False."""
        data = create_mock_market_data(
            ticker="BATS.L",
            forward_pe=0.12,
            forward_eps=3.72,
        )

        result = correct_uk_stocks(data, auto_correct=False)

        assert result.was_corrected is False
        assert len(result.flags_raised) > 0  # Should have warning flag

    def test_prd_example_bats(self):
        """Test BATS.L example from PRD."""
        # PRD: Raw Forward P/E 0.11, Corrected 11.20
        data = create_mock_market_data(
            ticker="BATS.L",
            forward_pe=0.11,
            forward_eps=2.67,
            trailing_pe=31.8,
        )

        result = correct_uk_stocks(data)

        assert result.corrected_forward_pe == pytest.approx(11.0, rel=0.1)


# =============================================================================
# calculate_implied_growth Tests
# =============================================================================


class TestCalculateImpliedGrowth:
    """Tests for calculate_implied_growth function."""

    def test_positive_growth(self):
        """Test positive growth calculation."""
        growth = calculate_implied_growth(5.0, 10.0)
        assert growth == 100.0  # 100% growth

    def test_negative_growth(self):
        """Test negative growth calculation (HOOD example)."""
        growth = calculate_implied_growth(1.56, 0.73)
        assert growth == pytest.approx(-53.21, rel=0.01)

    def test_zero_growth(self):
        """Test zero growth."""
        growth = calculate_implied_growth(10.0, 10.0)
        assert growth == 0.0

    def test_none_trailing_eps(self):
        """Test None handling for trailing EPS."""
        growth = calculate_implied_growth(None, 10.0)
        assert growth is None

    def test_none_forward_eps(self):
        """Test None handling for forward EPS."""
        growth = calculate_implied_growth(10.0, None)
        assert growth is None

    def test_zero_trailing_eps(self):
        """Test zero trailing EPS returns None."""
        growth = calculate_implied_growth(0.0, 10.0)
        assert growth is None


# =============================================================================
# detect_stock_splits Tests
# =============================================================================


class TestDetectStockSplits:
    """Tests for detect_stock_splits function."""

    def test_extreme_positive_growth_detected(self):
        """Test extreme positive growth is flagged as potential split."""
        # NFLX-like case: >1000% growth suggests split issue
        data = create_mock_market_data(
            ticker="NFLX",
            trailing_eps=1.98,
            forward_eps=23.78,  # Pre-split value mixed with post-split price
        )

        is_split, warning = detect_stock_splits(data)

        assert is_split is True
        assert warning is not None
        assert "split" in warning.lower() or "growth" in warning.lower()

    def test_extreme_negative_growth_detected(self):
        """Test extreme negative growth is flagged."""
        data = create_mock_market_data(
            ticker="TEST",
            trailing_eps=10.0,
            forward_eps=0.5,  # -95% decline
        )

        is_split, warning = detect_stock_splits(data, growth_threshold=50.0)

        assert is_split is True

    def test_normal_growth_not_flagged(self):
        """Test normal growth is not flagged."""
        data = create_mock_market_data(
            ticker="AAPL",
            trailing_eps=6.0,
            forward_eps=7.2,  # 20% growth
        )

        is_split, warning = detect_stock_splits(data)

        assert is_split is False
        assert warning is None

    def test_missing_eps_not_flagged(self):
        """Test missing EPS data is not flagged as split."""
        data = create_mock_market_data(
            ticker="TEST",
            trailing_eps=None,
            forward_eps=10.0,
        )

        is_split, warning = detect_stock_splits(data)

        assert is_split is False

    def test_custom_threshold(self):
        """Test custom growth threshold."""
        data = create_mock_market_data(
            ticker="TEST",
            trailing_eps=10.0,
            forward_eps=15.0,  # 50% growth
        )

        # With default 100% threshold, should not flag
        is_split, _ = detect_stock_splits(data)
        assert is_split is False

        # With 30% threshold, should flag
        is_split, _ = detect_stock_splits(data, growth_threshold=30.0)
        assert is_split is True


# =============================================================================
# apply_corrections Tests
# =============================================================================


class TestApplyCorrections:
    """Tests for apply_corrections function."""

    def test_uk_stock_corrected(self):
        """Test UK stock gets corrected through pipeline."""
        from pe_scanner.data.fetcher import MarketData

        data = MarketData(
            ticker="BATS.L",
            forward_pe=0.12,
            forward_eps=3.72,
            trailing_pe=31.8,
            trailing_eps=1.39,
            current_price=2996.0,
            currency="GBp",
        )

        corrected, result = apply_corrections(data)

        assert result.was_corrected is True
        assert corrected.forward_pe == pytest.approx(12.0, rel=0.01)

    def test_non_uk_stock_unchanged(self):
        """Test non-UK stock passes through unchanged."""
        from pe_scanner.data.fetcher import MarketData

        data = MarketData(
            ticker="HOOD",
            forward_pe=156.58,
            forward_eps=0.73,
            trailing_pe=73.27,
            trailing_eps=1.56,
            current_price=114.30,
        )

        corrected, result = apply_corrections(data)

        assert result.was_corrected is False
        assert corrected.forward_pe == 156.58


# =============================================================================
# CorrectionResult Tests
# =============================================================================


class TestCorrectionResult:
    """Tests for CorrectionResult dataclass."""

    def test_was_corrected_true(self):
        """Test was_corrected property when corrections applied."""
        result = CorrectionResult(
            ticker="BATS.L",
            corrections_applied=["UK correction applied"],
        )
        assert result.was_corrected is True

    def test_was_corrected_false(self):
        """Test was_corrected property when no corrections."""
        result = CorrectionResult(ticker="HOOD")
        assert result.was_corrected is False

    def test_has_warnings_true(self):
        """Test has_warnings property when flags present."""
        result = CorrectionResult(
            ticker="TEST",
            flags_raised=["Warning message"],
        )
        assert result.has_warnings is True

    def test_has_warnings_false(self):
        """Test has_warnings property when no flags."""
        result = CorrectionResult(ticker="TEST")
        assert result.has_warnings is False


# =============================================================================
# PRD Reference Examples
# =============================================================================


class TestPRDExamples:
    """Tests verifying examples from the PRD."""

    def test_bats_correction(self):
        """
        BATS.L UK stock correction from PRD.

        Raw Forward P/E: 0.11
        Corrected P/E: 11.20
        Factor: 100x
        """
        from pe_scanner.data.fetcher import MarketData

        data = MarketData(
            ticker="BATS.L",
            forward_pe=0.11,
            forward_eps=2.67,
            trailing_pe=31.8,
            current_price=2996.0,
            currency="GBp",
        )

        corrected, result = apply_corrections(data)

        assert result.was_corrected is True
        assert result.correction_factor == 100.0
        assert corrected.forward_pe == pytest.approx(11.0, rel=0.1)

    def test_bab_correction(self):
        """
        BAB.L UK stock correction from PRD.

        Raw Forward P/E: 0.23
        Corrected P/E: 23.41
        Factor: 100x
        """
        from pe_scanner.data.fetcher import MarketData

        data = MarketData(
            ticker="BAB.L",
            forward_pe=0.23,
            trailing_pe=25.0,
        )

        corrected, result = apply_corrections(data)

        assert result.was_corrected is True
        assert corrected.forward_pe == pytest.approx(23.0, rel=0.1)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])


