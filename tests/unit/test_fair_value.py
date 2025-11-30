"""
Unit tests for Fair Value Scenario Calculations
"""

import pytest

from pe_scanner.analysis.fair_value import (
    DEFAULT_BEAR_PE,
    DEFAULT_BULL_PE,
    FairValueResult,
    analyze_fair_value,
    analyze_fair_value_batch,
    calculate_base_fair_value,
    calculate_fair_values,
    calculate_upside,
    rank_by_upside,
)


# =============================================================================
# calculate_fair_values Tests
# =============================================================================


class TestCalculateFairValues:
    """Tests for calculate_fair_values function."""

    def test_basic_calculation(self):
        """Test basic fair value calculation."""
        bear, bull = calculate_fair_values(1.0)

        assert bear == DEFAULT_BEAR_PE  # 1.0 * 17.5
        assert bull == DEFAULT_BULL_PE  # 1.0 * 37.5

    def test_hood_example(self):
        """Test HOOD example from PRD."""
        # HOOD forward EPS = 0.73
        bear, bull = calculate_fair_values(0.73)

        assert bear == pytest.approx(12.78, rel=0.01)  # 0.73 * 17.5
        assert bull == pytest.approx(27.38, rel=0.01)  # 0.73 * 37.5

    def test_custom_multiples(self):
        """Test with custom P/E multiples."""
        bear, bull = calculate_fair_values(10.0, bear_pe=15.0, bull_pe=30.0)

        assert bear == 150.0
        assert bull == 300.0

    def test_zero_eps(self):
        """Test with zero EPS."""
        bear, bull = calculate_fair_values(0.0)

        assert bear == 0.0
        assert bull == 0.0

    def test_negative_eps(self):
        """Test with negative EPS (loss-making company)."""
        bear, bull = calculate_fair_values(-1.0)

        assert bear == -DEFAULT_BEAR_PE
        assert bull == -DEFAULT_BULL_PE

    def test_none_eps_raises_error(self):
        """Test that None EPS raises ValueError."""
        with pytest.raises(ValueError, match="cannot be None"):
            calculate_fair_values(None)


# =============================================================================
# calculate_upside Tests
# =============================================================================


class TestCalculateUpside:
    """Tests for calculate_upside function."""

    def test_positive_upside(self):
        """Test positive upside calculation."""
        upside = calculate_upside(100.0, 150.0)
        assert upside == 50.0  # 50% upside

    def test_negative_upside_downside(self):
        """Test negative upside (downside) calculation."""
        upside = calculate_upside(100.0, 50.0)
        assert upside == -50.0  # 50% downside

    def test_hood_bear_case(self):
        """Test HOOD bear case from PRD."""
        # Current: 114.30, Bear fair value: 12.78
        upside = calculate_upside(114.30, 12.78)
        assert upside == pytest.approx(-88.82, rel=0.01)

    def test_zero_upside(self):
        """Test zero upside when at fair value."""
        upside = calculate_upside(100.0, 100.0)
        assert upside == 0.0

    def test_zero_price_raises_error(self):
        """Test that zero price raises ValueError."""
        with pytest.raises(ValueError):
            calculate_upside(0.0, 100.0)

    def test_negative_price_raises_error(self):
        """Test that negative price raises ValueError."""
        with pytest.raises(ValueError):
            calculate_upside(-10.0, 100.0)

    def test_none_price_raises_error(self):
        """Test that None price raises ValueError."""
        with pytest.raises(ValueError):
            calculate_upside(None, 100.0)


# =============================================================================
# calculate_base_fair_value Tests
# =============================================================================


class TestCalculateBaseFairValue:
    """Tests for calculate_base_fair_value function."""

    def test_default_base(self):
        """Test default base calculation (25x)."""
        base = calculate_base_fair_value(10.0)
        assert base == 250.0  # 10 * 25

    def test_custom_base(self):
        """Test custom base multiple."""
        base = calculate_base_fair_value(10.0, base_pe=20.0)
        assert base == 200.0


# =============================================================================
# FairValueResult Tests
# =============================================================================


class TestFairValueResult:
    """Tests for FairValueResult dataclass."""

    def test_is_undervalued_bear(self):
        """Test is_undervalued_bear property."""
        # Undervalued even in bear case
        result = FairValueResult(
            ticker="TEST",
            current_price=100.0,
            forward_eps=10.0,
            bear_fair_value=150.0,
            bear_upside_pct=50.0,
            bull_fair_value=300.0,
            bull_upside_pct=200.0,
        )
        assert result.is_undervalued_bear is True

    def test_is_overvalued(self):
        """Test is_overvalued property."""
        # Overvalued even in bull case
        result = FairValueResult(
            ticker="TEST",
            current_price=200.0,
            forward_eps=2.0,
            bear_fair_value=35.0,
            bear_upside_pct=-82.5,
            bull_fair_value=75.0,
            bull_upside_pct=-62.5,
        )
        assert result.is_overvalued is True

    def test_midpoint_upside(self):
        """Test midpoint_upside_pct property."""
        result = FairValueResult(
            ticker="TEST",
            current_price=100.0,
            forward_eps=5.0,
            bear_fair_value=87.5,
            bear_upside_pct=-12.5,
            bull_fair_value=187.5,
            bull_upside_pct=87.5,
        )
        assert result.midpoint_upside_pct == 37.5

    def test_upside_range(self):
        """Test upside_range property."""
        result = FairValueResult(
            ticker="TEST",
            current_price=100.0,
            forward_eps=5.0,
            bear_fair_value=87.5,
            bear_upside_pct=-10.0,
            bull_fair_value=187.5,
            bull_upside_pct=90.0,
        )
        assert result.upside_range == 100.0  # 90 - (-10)


# =============================================================================
# analyze_fair_value Tests
# =============================================================================


class TestAnalyzeFairValue:
    """Tests for analyze_fair_value function."""

    def test_hood_analysis(self):
        """Test HOOD analysis matches PRD expectations."""
        result = analyze_fair_value("HOOD", 114.30, 0.73)

        assert result.ticker == "HOOD"
        assert result.current_price == 114.30
        assert result.forward_eps == 0.73
        assert result.bear_fair_value == pytest.approx(12.78, rel=0.01)
        assert result.bear_upside_pct == pytest.approx(-88.82, rel=0.01)
        assert result.bull_fair_value == pytest.approx(27.38, rel=0.01)
        assert result.bull_upside_pct == pytest.approx(-76.05, rel=0.01)
        assert result.is_overvalued is True

    def test_bats_analysis(self):
        """Test BATS.L analysis (corrected EPS)."""
        # BATS.L with corrected forward EPS of 2.67, price in £
        result = analyze_fair_value("BATS.L", 29.96, 2.67)

        assert result.is_undervalued_bear is True
        assert result.bear_upside_pct > 0
        assert result.bull_upside_pct > 0

    def test_includes_base_case(self):
        """Test base case is included by default."""
        result = analyze_fair_value("TEST", 100.0, 5.0)

        assert result.base_fair_value is not None
        assert result.base_upside_pct is not None

    def test_excludes_base_case(self):
        """Test base case can be excluded."""
        result = analyze_fair_value("TEST", 100.0, 5.0, include_base=False)

        assert result.base_fair_value is None
        assert result.base_upside_pct is None

    def test_custom_multiples(self):
        """Test custom P/E multiples are used."""
        result = analyze_fair_value("TEST", 100.0, 5.0, bear_pe=10.0, bull_pe=20.0)

        assert result.bear_pe_multiple == 10.0
        assert result.bull_pe_multiple == 20.0
        assert result.bear_fair_value == 50.0
        assert result.bull_fair_value == 100.0

    def test_extreme_downside_warning(self):
        """Test warning for extreme bear case downside."""
        # Create a case with >90% downside to trigger warning
        result = analyze_fair_value("OVERPRICED", 200.0, 0.5)

        # Bear fair value = 0.5 * 17.5 = 8.75, which is -95.6% from 200
        assert result.bear_upside_pct < -90
        assert any("extreme" in w.lower() for w in result.warnings)

    def test_invalid_price_raises(self):
        """Test invalid price raises ValueError."""
        with pytest.raises(ValueError):
            analyze_fair_value("TEST", 0.0, 5.0)

        with pytest.raises(ValueError):
            analyze_fair_value("TEST", -10.0, 5.0)

    def test_none_eps_raises(self):
        """Test None EPS raises ValueError."""
        with pytest.raises(ValueError):
            analyze_fair_value("TEST", 100.0, None)


# =============================================================================
# analyze_fair_value_batch Tests
# =============================================================================


class TestAnalyzeFairValueBatch:
    """Tests for analyze_fair_value_batch function."""

    def test_batch_analysis(self):
        """Test batch analysis returns correct results."""
        data = [
            {"ticker": "A", "current_price": 100.0, "forward_eps": 5.0},
            {"ticker": "B", "current_price": 50.0, "forward_eps": 2.0},
        ]

        results = analyze_fair_value_batch(data)

        assert len(results) == 2
        assert results[0].ticker == "A"
        assert results[1].ticker == "B"

    def test_batch_skips_invalid(self):
        """Test batch skips invalid entries."""
        data = [
            {"ticker": "A", "current_price": 100.0, "forward_eps": 5.0},
            {"ticker": "B", "current_price": 0.0, "forward_eps": 2.0},  # Invalid
            {"ticker": "C", "current_price": 50.0, "forward_eps": 2.0},
        ]

        results = analyze_fair_value_batch(data)

        assert len(results) == 2
        tickers = [r.ticker for r in results]
        assert "A" in tickers
        assert "C" in tickers
        assert "B" not in tickers

    def test_empty_batch(self):
        """Test empty batch returns empty list."""
        results = analyze_fair_value_batch([])
        assert results == []


# =============================================================================
# rank_by_upside Tests
# =============================================================================


class TestRankByUpside:
    """Tests for rank_by_upside function."""

    def create_result(self, ticker: str, bear_upside: float, bull_upside: float) -> FairValueResult:
        """Helper to create FairValueResult for testing."""
        return FairValueResult(
            ticker=ticker,
            current_price=100.0,
            forward_eps=5.0,
            bear_fair_value=100.0 + bear_upside,
            bear_upside_pct=bear_upside,
            bull_fair_value=100.0 + bull_upside,
            bull_upside_pct=bull_upside,
        )

    def test_rank_by_bear_descending(self):
        """Test ranking by bear upside descending (best first)."""
        results = [
            self.create_result("A", -50.0, 10.0),
            self.create_result("B", 30.0, 100.0),
            self.create_result("C", -10.0, 50.0),
        ]

        ranked = rank_by_upside(results, use_bear=True, ascending=False)

        assert ranked[0].ticker == "B"  # 30%
        assert ranked[1].ticker == "C"  # -10%
        assert ranked[2].ticker == "A"  # -50%

    def test_rank_by_bull_descending(self):
        """Test ranking by bull upside descending."""
        results = [
            self.create_result("A", -50.0, 10.0),
            self.create_result("B", 30.0, 100.0),
            self.create_result("C", -10.0, 50.0),
        ]

        ranked = rank_by_upside(results, use_bear=False, ascending=False)

        assert ranked[0].ticker == "B"  # 100%
        assert ranked[1].ticker == "C"  # 50%
        assert ranked[2].ticker == "A"  # 10%

    def test_rank_ascending(self):
        """Test ascending order (worst first)."""
        results = [
            self.create_result("A", 30.0, 100.0),
            self.create_result("B", -50.0, 10.0),
        ]

        ranked = rank_by_upside(results, use_bear=True, ascending=True)

        assert ranked[0].ticker == "B"  # -50% (worst)
        assert ranked[1].ticker == "A"  # 30% (best)


# =============================================================================
# PRD Examples Verification
# =============================================================================


class TestPRDExamples:
    """Tests verifying examples from the PRD."""

    def test_hood_fair_value(self):
        """
        HOOD from PRD:
        - Current Price: $114.30
        - Forward EPS: $0.73
        - Bear Fair Value: $12.78 (17.5x)
        - Bull Fair Value: $27.38 (37.5x)
        """
        result = analyze_fair_value("HOOD", 114.30, 0.73)

        # Fair values
        assert result.bear_fair_value == pytest.approx(12.78, abs=0.01)
        assert result.bull_fair_value == pytest.approx(27.38, abs=0.01)

        # Stock is overvalued
        assert result.is_overvalued is True
        assert result.bear_upside_pct < -80  # Significant downside

    def test_formula_bear_case(self):
        """Test bear case formula: forward_eps × 17.5."""
        # For any forward EPS, bear = EPS * 17.5
        test_eps = 5.0
        bear, _ = calculate_fair_values(test_eps)
        assert bear == test_eps * DEFAULT_BEAR_PE

    def test_formula_bull_case(self):
        """Test bull case formula: forward_eps × 37.5."""
        # For any forward EPS, bull = EPS * 37.5
        test_eps = 5.0
        _, bull = calculate_fair_values(test_eps)
        assert bull == test_eps * DEFAULT_BULL_PE


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

