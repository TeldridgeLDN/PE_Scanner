"""
Unit tests for Data Quality Validation Module
"""

import pytest
from datetime import datetime, timedelta
from unittest.mock import Mock

from pe_scanner.data.validator import (
    DataQualityFlag,
    DataQualityLevel,
    ValidationResult,
    check_data_quality,
    check_extreme_downside,
    check_extreme_growth,
    check_fetch_errors,
    check_missing_data,
    check_negative_pe,
    check_stale_estimates,
    filter_usable,
    get_validation_summary,
    validate_batch,
    validate_market_data,
)


# =============================================================================
# Helper to create mock MarketData
# =============================================================================


def create_mock_market_data(
    ticker: str = "TEST",
    forward_pe: float = None,
    forward_eps: float = None,
    trailing_pe: float = None,
    trailing_eps: float = None,
    current_price: float = None,
    last_updated: datetime = None,
    fetch_errors: list = None,
) -> Mock:
    """Create a mock MarketData object for testing."""
    data = Mock()
    data.ticker = ticker
    data.forward_pe = forward_pe
    data.forward_eps = forward_eps
    data.trailing_pe = trailing_pe
    data.trailing_eps = trailing_eps
    data.current_price = current_price
    data.last_updated = last_updated or datetime.now()
    data.fetch_errors = fetch_errors or []
    return data


# =============================================================================
# ValidationResult Tests
# =============================================================================


class TestValidationResult:
    """Tests for ValidationResult dataclass."""

    def test_is_usable_verified(self):
        """Test is_usable for verified quality."""
        result = ValidationResult(
            ticker="TEST",
            quality_level=DataQualityLevel.VERIFIED,
        )
        assert result.is_usable is True

    def test_is_usable_acceptable(self):
        """Test is_usable for acceptable quality."""
        result = ValidationResult(
            ticker="TEST",
            quality_level=DataQualityLevel.ACCEPTABLE,
        )
        assert result.is_usable is True

    def test_is_usable_suspicious(self):
        """Test is_usable for suspicious quality."""
        result = ValidationResult(
            ticker="TEST",
            quality_level=DataQualityLevel.SUSPICIOUS,
        )
        assert result.is_usable is False

    def test_is_usable_unreliable(self):
        """Test is_usable for unreliable quality."""
        result = ValidationResult(
            ticker="TEST",
            quality_level=DataQualityLevel.UNRELIABLE,
        )
        assert result.is_usable is False

    def test_has_critical_issues_with_errors(self):
        """Test has_critical_issues when errors present."""
        result = ValidationResult(
            ticker="TEST",
            errors=["Critical error"],
        )
        assert result.has_critical_issues is True

    def test_has_critical_issues_unreliable(self):
        """Test has_critical_issues for unreliable quality."""
        result = ValidationResult(
            ticker="TEST",
            quality_level=DataQualityLevel.UNRELIABLE,
        )
        assert result.has_critical_issues is True

    def test_add_flag_warning(self):
        """Test adding a warning flag."""
        result = ValidationResult(ticker="TEST")
        result.add_flag(DataQualityFlag.MISSING_FORWARD_PE, "Missing forward P/E")

        assert DataQualityFlag.MISSING_FORWARD_PE in result.flags
        assert "Missing forward P/E" in result.warnings
        assert len(result.errors) == 0

    def test_add_flag_error(self):
        """Test adding an error flag."""
        result = ValidationResult(ticker="TEST")
        result.add_flag(DataQualityFlag.FETCH_ERROR, "Fetch failed", is_error=True)

        assert DataQualityFlag.FETCH_ERROR in result.flags
        assert "Fetch failed" in result.errors


# =============================================================================
# check_missing_data Tests
# =============================================================================


class TestCheckMissingData:
    """Tests for check_missing_data function."""

    def test_all_data_present(self):
        """Test no issues when all data present."""
        data = create_mock_market_data(
            forward_pe=15.0,
            trailing_pe=20.0,
            forward_eps=5.0,
            trailing_eps=4.0,
            current_price=100.0,
        )

        issues = check_missing_data(data)
        assert len(issues) == 0

    def test_missing_forward_pe(self):
        """Test detection of missing forward P/E."""
        data = create_mock_market_data(
            forward_pe=None,
            trailing_pe=20.0,
        )

        issues = check_missing_data(data)
        flags = [f for f, _ in issues]
        assert DataQualityFlag.MISSING_FORWARD_PE in flags

    def test_missing_trailing_pe(self):
        """Test detection of missing trailing P/E."""
        data = create_mock_market_data(
            forward_pe=15.0,
            trailing_pe=None,
        )

        issues = check_missing_data(data)
        flags = [f for f, _ in issues]
        assert DataQualityFlag.MISSING_TRAILING_PE in flags

    def test_missing_eps(self):
        """Test detection of missing EPS values."""
        data = create_mock_market_data(
            forward_eps=None,
            trailing_eps=None,
        )

        issues = check_missing_data(data)
        flags = [f for f, _ in issues]
        assert DataQualityFlag.MISSING_FORWARD_EPS in flags
        assert DataQualityFlag.MISSING_TRAILING_EPS in flags

    def test_missing_price(self):
        """Test detection of missing price."""
        data = create_mock_market_data(current_price=None)

        issues = check_missing_data(data)
        flags = [f for f, _ in issues]
        assert DataQualityFlag.MISSING_PRICE in flags


# =============================================================================
# check_negative_pe Tests
# =============================================================================


class TestCheckNegativePe:
    """Tests for check_negative_pe function."""

    def test_positive_pe_ok(self):
        """Test no issues with positive P/E values."""
        data = create_mock_market_data(
            trailing_pe=20.0,
            forward_pe=15.0,
        )

        issues = check_negative_pe(data)
        assert len(issues) == 0

    def test_negative_trailing_pe(self):
        """Test detection of negative trailing P/E."""
        data = create_mock_market_data(trailing_pe=-10.0)

        issues = check_negative_pe(data)
        flags = [f for f, _ in issues]
        assert DataQualityFlag.NEGATIVE_TRAILING_PE in flags

    def test_negative_forward_pe(self):
        """Test detection of negative forward P/E."""
        data = create_mock_market_data(forward_pe=-5.0)

        issues = check_negative_pe(data)
        flags = [f for f, _ in issues]
        assert DataQualityFlag.NEGATIVE_FORWARD_PE in flags

    def test_zero_pe(self):
        """Test detection of zero P/E."""
        data = create_mock_market_data(trailing_pe=0.0, forward_pe=0.0)

        issues = check_negative_pe(data)
        flags = [f for f, _ in issues]
        assert DataQualityFlag.ZERO_PE in flags


# =============================================================================
# check_extreme_downside Tests
# =============================================================================


class TestCheckExtremeDownside:
    """Tests for check_extreme_downside function."""

    def test_normal_downside_ok(self):
        """Test no flag for normal downside."""
        result = check_extreme_downside(-50.0)
        assert result is None

    def test_extreme_downside_flagged(self):
        """Test extreme downside is flagged."""
        result = check_extreme_downside(-97.5)

        assert result is not None
        assert result[0] == DataQualityFlag.EXTREME_DOWNSIDE

    def test_custom_threshold(self):
        """Test custom threshold works."""
        # With default -95%, -80% should be OK
        result1 = check_extreme_downside(-80.0)
        assert result1 is None

        # With -70% threshold, -80% should be flagged
        result2 = check_extreme_downside(-80.0, threshold=-70.0)
        assert result2 is not None

    def test_none_value(self):
        """Test None value returns None."""
        result = check_extreme_downside(None)
        assert result is None


# =============================================================================
# check_extreme_growth Tests
# =============================================================================


class TestCheckExtremeGrowth:
    """Tests for check_extreme_growth function."""

    def test_normal_growth_ok(self):
        """Test no flag for normal growth."""
        result = check_extreme_growth(5.0, 6.0)  # 20% growth
        assert result is None

    def test_extreme_positive_growth_flagged(self):
        """Test extreme positive growth is flagged."""
        result = check_extreme_growth(1.0, 5.0)  # 400% growth

        assert result is not None
        assert result[0] == DataQualityFlag.EXTREME_GROWTH
        assert "400" in result[1]

    def test_extreme_negative_growth_flagged(self):
        """Test extreme negative decline is flagged."""
        # -105% decline (below -100% threshold)
        result = check_extreme_growth(10.0, -0.5)

        assert result is not None
        assert result[0] == DataQualityFlag.EXTREME_GROWTH

    def test_missing_eps_ok(self):
        """Test missing EPS returns None."""
        result = check_extreme_growth(None, 5.0)
        assert result is None

        result = check_extreme_growth(5.0, None)
        assert result is None

    def test_zero_trailing_eps(self):
        """Test zero trailing EPS returns None."""
        result = check_extreme_growth(0.0, 5.0)
        assert result is None

    def test_custom_threshold(self):
        """Test custom threshold works."""
        # 60% growth should be OK with default 100% threshold
        result1 = check_extreme_growth(5.0, 8.0)  # 60% growth
        assert result1 is None

        # But flagged with 50% threshold
        result2 = check_extreme_growth(5.0, 8.0, threshold=50.0)
        assert result2 is not None


# =============================================================================
# check_stale_estimates Tests
# =============================================================================


class TestCheckStaleEstimates:
    """Tests for check_stale_estimates function."""

    def test_fresh_data_ok(self):
        """Test fresh data is not flagged."""
        data = create_mock_market_data(last_updated=datetime.now())

        result = check_stale_estimates(data)
        assert result is None

    def test_stale_data_flagged(self):
        """Test stale data is flagged."""
        old_date = datetime.now() - timedelta(days=200)
        data = create_mock_market_data(last_updated=old_date)

        result = check_stale_estimates(data)

        assert result is not None
        assert result[0] == DataQualityFlag.STALE_ESTIMATES

    def test_custom_max_age(self):
        """Test custom max age works."""
        old_date = datetime.now() - timedelta(days=100)
        data = create_mock_market_data(last_updated=old_date)

        # With default 180 days, should be OK
        result1 = check_stale_estimates(data)
        assert result1 is None

        # With 90 days max, should be flagged
        result2 = check_stale_estimates(data, max_age_days=90)
        assert result2 is not None

    def test_no_timestamp(self):
        """Test no timestamp returns None."""
        data = create_mock_market_data(last_updated=None)

        result = check_stale_estimates(data)
        assert result is None


# =============================================================================
# check_fetch_errors Tests
# =============================================================================


class TestCheckFetchErrors:
    """Tests for check_fetch_errors function."""

    def test_no_errors(self):
        """Test no flag when no fetch errors."""
        data = create_mock_market_data(fetch_errors=[])

        issues = check_fetch_errors(data)
        assert len(issues) == 0

    def test_with_errors(self):
        """Test flags generated for fetch errors."""
        data = create_mock_market_data(
            fetch_errors=["Connection timeout", "Rate limit exceeded"]
        )

        issues = check_fetch_errors(data)
        assert len(issues) == 2
        assert all(f == DataQualityFlag.FETCH_ERROR for f, _ in issues)


# =============================================================================
# check_data_quality Tests
# =============================================================================


class TestCheckDataQuality:
    """Tests for check_data_quality quick check function."""

    def test_good_data_no_warnings(self):
        """Test good data produces no warnings."""
        data = create_mock_market_data(
            forward_pe=15.0,
            trailing_pe=20.0,
            forward_eps=5.0,
            trailing_eps=4.0,
            current_price=100.0,
        )

        warnings = check_data_quality(data)
        assert len(warnings) == 0

    def test_missing_data_warning(self):
        """Test missing data produces warning."""
        data = create_mock_market_data(forward_pe=None)

        warnings = check_data_quality(data)
        assert any("forward P/E" in w for w in warnings)

    def test_multiple_issues(self):
        """Test multiple issues are all reported."""
        data = create_mock_market_data(
            forward_pe=None,
            trailing_pe=-10.0,
            fetch_errors=["Error"],
        )

        warnings = check_data_quality(data)
        assert len(warnings) >= 3


# =============================================================================
# validate_market_data Tests
# =============================================================================


class TestValidateMarketData:
    """Tests for validate_market_data function."""

    def test_verified_quality(self):
        """Test verified quality for good data."""
        data = create_mock_market_data(
            forward_pe=15.0,
            trailing_pe=20.0,
            forward_eps=5.5,
            trailing_eps=5.0,
            current_price=100.0,
        )

        result = validate_market_data(data)

        assert result.quality_level == DataQualityLevel.VERIFIED
        assert result.confidence_score >= 0.9
        assert result.is_usable is True
        assert len(result.checks_passed) > 0

    def test_unreliable_quality_missing_pe(self):
        """Test unreliable quality when missing critical P/E."""
        data = create_mock_market_data(
            forward_pe=None,
            trailing_pe=None,
        )

        result = validate_market_data(data)

        assert result.quality_level == DataQualityLevel.UNRELIABLE
        assert result.is_usable is False
        assert len(result.errors) > 0

    def test_acceptable_quality_with_warnings(self):
        """Test acceptable quality with minor warnings."""
        data = create_mock_market_data(
            forward_pe=15.0,
            trailing_pe=20.0,
            forward_eps=None,  # Missing but not critical
            trailing_eps=5.0,
            current_price=100.0,
        )

        result = validate_market_data(data)

        assert result.quality_level in (DataQualityLevel.VERIFIED, DataQualityLevel.ACCEPTABLE)
        assert result.is_usable is True

    def test_suspicious_quality_extreme_growth(self):
        """Test suspicious quality with extreme growth."""
        data = create_mock_market_data(
            forward_pe=5.0,
            trailing_pe=20.0,
            forward_eps=50.0,  # 10x trailing
            trailing_eps=5.0,
            current_price=100.0,
        )

        result = validate_market_data(data)

        assert result.requires_manual_review is True
        assert DataQualityFlag.EXTREME_GROWTH in result.flags

    def test_fetch_errors_reduce_confidence(self):
        """Test fetch errors significantly reduce confidence."""
        data = create_mock_market_data(
            forward_pe=15.0,
            trailing_pe=20.0,
            fetch_errors=["Error 1", "Error 2"],
        )

        result = validate_market_data(data)

        assert result.confidence_score < 0.5
        assert result.has_critical_issues is True


# =============================================================================
# Batch Validation Tests
# =============================================================================


class TestValidateBatch:
    """Tests for validate_batch function."""

    def test_batch_validation(self):
        """Test batch validation returns results for all items."""
        data_list = [
            create_mock_market_data(ticker="A", forward_pe=15.0, trailing_pe=20.0),
            create_mock_market_data(ticker="B", forward_pe=10.0, trailing_pe=12.0),
            create_mock_market_data(ticker="C", forward_pe=None),  # Bad
        ]

        results = validate_batch(data_list)

        assert len(results) == 3
        assert results[0].ticker == "A"
        assert results[1].ticker == "B"
        assert results[2].ticker == "C"


class TestGetValidationSummary:
    """Tests for get_validation_summary function."""

    def test_summary_counts(self):
        """Test summary produces correct counts."""
        results = [
            ValidationResult(ticker="A", quality_level=DataQualityLevel.VERIFIED, confidence_score=1.0),
            ValidationResult(ticker="B", quality_level=DataQualityLevel.ACCEPTABLE, confidence_score=0.8),
            ValidationResult(ticker="C", quality_level=DataQualityLevel.UNRELIABLE, confidence_score=0.3),
        ]

        summary = get_validation_summary(results)

        assert summary["total"] == 3
        assert summary["verified"] == 1
        assert summary["acceptable"] == 1
        assert summary["unreliable"] == 1
        assert summary["usable"] == 2
        assert summary["avg_confidence"] == pytest.approx(0.7, rel=0.01)


class TestFilterUsable:
    """Tests for filter_usable function."""

    def test_filters_bad_data(self):
        """Test filter removes unusable data."""
        data_list = [
            create_mock_market_data(ticker="A", forward_pe=15.0, trailing_pe=20.0),
            create_mock_market_data(ticker="B", forward_pe=None, trailing_pe=None),  # Bad
            create_mock_market_data(ticker="C", forward_pe=10.0, trailing_pe=12.0),
        ]

        usable = filter_usable(data_list)

        assert len(usable) == 2
        tickers = [d.ticker for d in usable]
        assert "A" in tickers
        assert "C" in tickers
        assert "B" not in tickers


# =============================================================================
# DataQualityLevel Tests
# =============================================================================


class TestDataQualityLevel:
    """Tests for DataQualityLevel enum."""

    def test_level_values(self):
        """Test quality level values."""
        assert DataQualityLevel.VERIFIED.value == "verified"
        assert DataQualityLevel.ACCEPTABLE.value == "acceptable"
        assert DataQualityLevel.SUSPICIOUS.value == "suspicious"
        assert DataQualityLevel.UNRELIABLE.value == "unreliable"


# =============================================================================
# DataQualityFlag Tests
# =============================================================================


class TestDataQualityFlag:
    """Tests for DataQualityFlag enum."""

    def test_flag_values(self):
        """Test quality flag values."""
        assert DataQualityFlag.MISSING_FORWARD_PE.value == "missing_forward_pe"
        assert DataQualityFlag.NEGATIVE_TRAILING_PE.value == "negative_trailing_pe"
        assert DataQualityFlag.EXTREME_DOWNSIDE.value == "extreme_downside"
        assert DataQualityFlag.STALE_ESTIMATES.value == "stale_estimates"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

