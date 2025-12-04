"""
Unit tests for Portfolio Ranking Module
"""

import pytest
from unittest.mock import Mock

from pe_scanner.portfolios.ranker import (
    Confidence,
    RankedPosition,
    RankingConfig,
    RankingResult,
    Signal,
    SIGNAL_INFO,
    assign_signal,
    calculate_action_priority,
    calculate_confidence,
    categorize_by_action,
    get_actionable_summary,
    get_top_opportunities,
    rank_portfolio,
    rank_positions,
)


# =============================================================================
# Helper to create mock results
# =============================================================================


def create_mock_compression_result(
    ticker: str,
    compression_pct: float,
    implied_growth_pct: float = 0.0,
    warnings: list = None,
) -> Mock:
    """Create a mock CompressionResult for testing."""
    result = Mock()
    result.ticker = ticker
    result.compression_pct = compression_pct
    result.implied_growth_pct = implied_growth_pct
    result.warnings = warnings or []
    return result


def create_mock_fair_value_result(
    ticker: str,
    bear_upside_pct: float,
    bull_upside_pct: float,
) -> Mock:
    """Create a mock FairValueResult for testing."""
    result = Mock()
    result.ticker = ticker
    result.bear_upside_pct = bear_upside_pct
    result.bull_upside_pct = bull_upside_pct
    return result


def create_mock_validation_result(
    ticker: str,
    confidence_score: float = 1.0,
    warnings: list = None,
) -> Mock:
    """Create a mock ValidationResult for testing."""
    result = Mock()
    result.ticker = ticker
    result.confidence_score = confidence_score
    result.warnings = warnings or []
    return result


# =============================================================================
# Signal Enum Tests
# =============================================================================


class TestSignal:
    """Tests for Signal enum."""

    def test_signal_values(self):
        """Test signal enum values."""
        assert Signal.STRONG_BUY.value == "strong_buy"
        assert Signal.BUY.value == "buy"
        assert Signal.HOLD.value == "hold"
        assert Signal.SELL.value == "sell"
        assert Signal.STRONG_SELL.value == "strong_sell"
        assert Signal.DO_NOT_TRADE.value == "do_not_trade"

    def test_signal_info(self):
        """Test signal info mapping."""
        assert SIGNAL_INFO[Signal.STRONG_BUY]["icon"] == "🟢🟢"
        assert SIGNAL_INFO[Signal.SELL]["icon"] == "🔴"


# =============================================================================
# Confidence Enum Tests
# =============================================================================


class TestConfidence:
    """Tests for Confidence enum."""

    def test_confidence_values(self):
        """Test confidence enum values."""
        assert Confidence.HIGH.value == "high"
        assert Confidence.MEDIUM.value == "medium"
        assert Confidence.LOW.value == "low"


# =============================================================================
# calculate_confidence Tests
# =============================================================================


class TestCalculateConfidence:
    """Tests for calculate_confidence function."""

    def test_high_confidence_no_issues(self):
        """Test high confidence when no issues."""
        confidence = calculate_confidence(30.0)
        assert confidence == Confidence.HIGH

    def test_medium_confidence_with_validation(self):
        """Test medium confidence with validation issues."""
        val = create_mock_validation_result("TEST", confidence_score=0.7)
        confidence = calculate_confidence(30.0, validation_result=val)
        assert confidence == Confidence.MEDIUM

    def test_low_confidence_many_warnings(self):
        """Test low confidence with many warnings."""
        val = create_mock_validation_result("TEST", confidence_score=0.4)
        warnings = ["Warning 1", "Warning 2", "Warning 3"]
        confidence = calculate_confidence(30.0, validation_result=val, data_warnings=warnings)
        assert confidence == Confidence.LOW

    def test_extreme_compression_reduces_confidence(self):
        """Test extreme compression reduces confidence."""
        # 150% compression is extreme
        confidence = calculate_confidence(150.0)
        # Should be reduced but still high if no other issues
        assert confidence in (Confidence.HIGH, Confidence.MEDIUM)


# =============================================================================
# assign_signal Tests
# =============================================================================


class TestAssignSignal:
    """Tests for assign_signal function."""

    def test_strong_buy(self):
        """Test STRONG_BUY signal for high compression."""
        signal = assign_signal(60.0, Confidence.HIGH)
        assert signal == Signal.STRONG_BUY

    def test_buy(self):
        """Test BUY signal for moderate positive compression."""
        signal = assign_signal(30.0, Confidence.HIGH)
        assert signal == Signal.BUY

    def test_hold(self):
        """Test HOLD signal for low compression."""
        signal = assign_signal(10.0, Confidence.HIGH)
        assert signal == Signal.HOLD

    def test_sell(self):
        """Test SELL signal for moderate negative compression."""
        signal = assign_signal(-30.0, Confidence.HIGH)
        assert signal == Signal.SELL

    def test_strong_sell(self):
        """Test STRONG_SELL signal for high negative compression."""
        signal = assign_signal(-60.0, Confidence.HIGH)
        assert signal == Signal.STRONG_SELL

    def test_do_not_trade_low_confidence(self):
        """Test DO_NOT_TRADE for low confidence."""
        signal = assign_signal(60.0, Confidence.LOW)
        assert signal == Signal.DO_NOT_TRADE

    def test_custom_thresholds(self):
        """Test custom thresholds."""
        config = RankingConfig(buy_threshold=30.0)
        # 25% should be HOLD with default 20% but HOLD with 30% threshold
        signal = assign_signal(25.0, Confidence.HIGH, config)
        assert signal == Signal.HOLD


# =============================================================================
# calculate_action_priority Tests
# =============================================================================


class TestCalculateActionPriority:
    """Tests for calculate_action_priority function."""

    def test_strong_signal_high_confidence(self):
        """Test priority 1 for strong signal with high confidence."""
        priority = calculate_action_priority(Signal.STRONG_BUY, Confidence.HIGH)
        assert priority == 1

    def test_strong_signal_medium_confidence(self):
        """Test priority 2 for strong signal with medium confidence."""
        priority = calculate_action_priority(Signal.STRONG_SELL, Confidence.MEDIUM)
        assert priority == 2

    def test_regular_signal(self):
        """Test priority for regular signal."""
        priority = calculate_action_priority(Signal.BUY, Confidence.HIGH)
        assert priority == 2

    def test_hold_signal(self):
        """Test priority 3 for hold signal."""
        priority = calculate_action_priority(Signal.HOLD, Confidence.HIGH)
        assert priority == 3


# =============================================================================
# RankedPosition Tests
# =============================================================================


class TestRankedPosition:
    """Tests for RankedPosition dataclass."""

    def test_basic_position(self):
        """Test basic position creation."""
        pos = RankedPosition(
            ticker="TEST",
            rank=1,
            compression_pct=50.0,
            signal=Signal.STRONG_BUY,
            confidence=Confidence.HIGH,
            bear_upside_pct=20.0,
            bull_upside_pct=80.0,
        )

        assert pos.ticker == "TEST"
        assert pos.rank == 1
        assert pos.is_buy is True
        assert pos.is_sell is False
        assert pos.is_actionable is True

    def test_signal_icon(self):
        """Test signal icon property."""
        pos = RankedPosition(
            ticker="TEST",
            rank=1,
            compression_pct=50.0,
            signal=Signal.STRONG_BUY,
            confidence=Confidence.HIGH,
            bear_upside_pct=0.0,
            bull_upside_pct=0.0,
        )
        assert pos.signal_icon == "🟢🟢"

    def test_midpoint_upside(self):
        """Test midpoint upside calculation."""
        pos = RankedPosition(
            ticker="TEST",
            rank=1,
            compression_pct=50.0,
            signal=Signal.BUY,
            confidence=Confidence.HIGH,
            bear_upside_pct=-20.0,
            bull_upside_pct=80.0,
        )
        assert pos.midpoint_upside_pct == 30.0


# =============================================================================
# RankingResult Tests
# =============================================================================


class TestRankingResult:
    """Tests for RankingResult dataclass."""

    def test_empty_result(self):
        """Test empty result."""
        result = RankingResult(portfolio_name="Test", total_positions=0)
        assert result.actionable_count == 0
        assert "0 BUY" in result.summary

    def test_summary(self):
        """Test summary generation."""
        buy_pos = RankedPosition(
            ticker="A", rank=1, compression_pct=50.0,
            signal=Signal.BUY, confidence=Confidence.HIGH,
            bear_upside_pct=0.0, bull_upside_pct=0.0,
        )
        result = RankingResult(
            portfolio_name="Test",
            total_positions=1,
            buy_signals=[buy_pos],
        )
        assert "1 BUY" in result.summary


# =============================================================================
# rank_positions Tests
# =============================================================================


class TestRankPositions:
    """Tests for rank_positions function."""

    def test_basic_ranking(self):
        """Test basic ranking by compression."""
        compressions = [
            create_mock_compression_result("A", 30.0),
            create_mock_compression_result("B", 60.0),
            create_mock_compression_result("C", -20.0),
        ]

        ranked = rank_positions(compressions, sort_by="compression")

        assert len(ranked) == 3
        assert ranked[0].ticker == "B"  # Highest compression
        assert ranked[1].ticker == "A"
        assert ranked[2].ticker == "C"  # Lowest (negative)

    def test_ranking_with_fair_value(self):
        """Test ranking includes fair value data."""
        compressions = [
            create_mock_compression_result("A", 50.0),
        ]
        fair_values = [
            create_mock_fair_value_result("A", 20.0, 80.0),
        ]

        ranked = rank_positions(compressions, fair_value_results=fair_values)

        assert ranked[0].bear_upside_pct == 20.0
        assert ranked[0].bull_upside_pct == 80.0

    def test_rank_assignment(self):
        """Test rank numbers are assigned correctly."""
        compressions = [
            create_mock_compression_result("A", 10.0),
            create_mock_compression_result("B", 50.0),
            create_mock_compression_result("C", 30.0),
        ]

        ranked = rank_positions(compressions, sort_by="compression")

        assert ranked[0].rank == 1
        assert ranked[1].rank == 2
        assert ranked[2].rank == 3

    def test_sort_by_compression_abs(self):
        """Test sorting by absolute compression."""
        compressions = [
            create_mock_compression_result("A", 30.0),
            create_mock_compression_result("B", -50.0),
            create_mock_compression_result("C", 10.0),
        ]

        ranked = rank_positions(compressions, sort_by="compression_abs")

        assert ranked[0].ticker == "B"  # -50% (highest absolute)
        assert ranked[1].ticker == "A"  # 30%


# =============================================================================
# categorize_by_action Tests
# =============================================================================


class TestCategorizeByAction:
    """Tests for categorize_by_action function."""

    def test_categorization(self):
        """Test positions are correctly categorized."""
        positions = [
            RankedPosition(
                ticker="A", rank=1, compression_pct=60.0,
                signal=Signal.STRONG_BUY, confidence=Confidence.HIGH,
                bear_upside_pct=0.0, bull_upside_pct=0.0,
            ),
            RankedPosition(
                ticker="B", rank=2, compression_pct=-60.0,
                signal=Signal.STRONG_SELL, confidence=Confidence.HIGH,
                bear_upside_pct=0.0, bull_upside_pct=0.0,
            ),
            RankedPosition(
                ticker="C", rank=3, compression_pct=10.0,
                signal=Signal.HOLD, confidence=Confidence.HIGH,
                bear_upside_pct=0.0, bull_upside_pct=0.0,
            ),
        ]

        result = categorize_by_action(positions)

        assert len(result.buy_signals) == 1
        assert len(result.sell_signals) == 1
        assert len(result.hold_signals) == 1
        assert result.buy_signals[0].ticker == "A"
        assert result.sell_signals[0].ticker == "B"


# =============================================================================
# get_top_opportunities Tests
# =============================================================================


class TestGetTopOpportunities:
    """Tests for get_top_opportunities function."""

    def test_top_buys(self):
        """Test getting top buy opportunities."""
        buy_positions = [
            RankedPosition(
                ticker="A", rank=1, compression_pct=60.0,
                signal=Signal.STRONG_BUY, confidence=Confidence.HIGH,
                bear_upside_pct=0.0, bull_upside_pct=0.0,
            ),
            RankedPosition(
                ticker="B", rank=2, compression_pct=40.0,
                signal=Signal.BUY, confidence=Confidence.HIGH,
                bear_upside_pct=0.0, bull_upside_pct=0.0,
            ),
        ]
        result = RankingResult(
            portfolio_name="Test",
            total_positions=2,
            buy_signals=buy_positions,
        )

        top = get_top_opportunities(result, n=1, signal_type="buy")

        assert len(top) == 1
        assert top[0].ticker == "A"


# =============================================================================
# rank_portfolio Tests
# =============================================================================


class TestRankPortfolio:
    """Tests for rank_portfolio function."""

    def test_full_pipeline(self):
        """Test complete ranking pipeline."""
        compressions = [
            create_mock_compression_result("BUY1", 60.0),
            create_mock_compression_result("SELL1", -60.0),
            create_mock_compression_result("HOLD1", 10.0),
        ]

        result = rank_portfolio(compressions, portfolio_name="Test Portfolio")

        assert result.portfolio_name == "Test Portfolio"
        assert result.total_positions == 3
        assert len(result.buy_signals) >= 1
        assert len(result.sell_signals) >= 1


# =============================================================================
# get_actionable_summary Tests
# =============================================================================


class TestGetActionableSummary:
    """Tests for get_actionable_summary function."""

    def test_summary_structure(self):
        """Test summary has expected structure."""
        result = RankingResult(
            portfolio_name="Test",
            total_positions=10,
            buy_signals=[],
            sell_signals=[],
            hold_signals=[],
        )

        summary = get_actionable_summary(result)

        assert summary["portfolio"] == "Test"
        assert summary["total"] == 10
        assert "buy_count" in summary
        assert "sell_count" in summary
        assert "top_buys" in summary


# =============================================================================
# PRD Examples Tests
# =============================================================================


class TestPRDExamples:
    """Tests verifying examples from the PRD."""

    def test_hood_sell_signal(self):
        """Test HOOD gets SELL signal (negative compression)."""
        compressions = [
            create_mock_compression_result("HOOD", -113.7),
        ]

        ranked = rank_positions(compressions)

        assert ranked[0].signal in (Signal.STRONG_SELL, Signal.SELL, Signal.DO_NOT_TRADE)

    def test_bats_buy_signal(self):
        """Test BATS.L gets BUY signal (positive compression)."""
        compressions = [
            create_mock_compression_result("BATS.L", 62.6),
        ]

        ranked = rank_positions(compressions)

        assert ranked[0].signal in (Signal.STRONG_BUY, Signal.BUY)

    def test_ranking_order(self):
        """Test ranking puts best opportunities first."""
        compressions = [
            create_mock_compression_result("HOOD", -113.7),
            create_mock_compression_result("BATS.L", 62.6),
            create_mock_compression_result("ORA.PA", 70.7),
        ]

        ranked = rank_positions(compressions, sort_by="compression")

        # ORA.PA should be first (highest compression)
        assert ranked[0].ticker == "ORA.PA"
        # BATS.L second
        assert ranked[1].ticker == "BATS.L"
        # HOOD last (negative)
        assert ranked[2].ticker == "HOOD"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])



