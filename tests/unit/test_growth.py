"""
Unit tests for growth mode analysis (PEG ratio).

Tests the PEG ratio calculation and signal interpretation for growth stocks.
"""

import pytest

from pe_scanner.analysis.growth import (
    GrowthAnalysisResult,
    GrowthSignal,
    analyze_growth_batch,
    analyze_growth_stock,
    calculate_peg_ratio,
    interpret_peg_signal,
    rank_by_peg,
)


# =============================================================================
# PEG Ratio Calculation Tests
# =============================================================================


def test_calculate_peg_ratio_typical():
    """Test typical PEG calculation."""
    peg = calculate_peg_ratio(30.0, 40.0)
    assert peg == 0.75


def test_calculate_peg_ratio_expensive():
    """Test PEG for expensive stock."""
    peg = calculate_peg_ratio(30.0, 10.0)
    assert peg == 3.0


def test_calculate_peg_ratio_fair():
    """Test PEG at fair value (1.0)."""
    peg = calculate_peg_ratio(20.0, 20.0)
    assert peg == 1.0


def test_calculate_peg_ratio_high_pe():
    """Test PEG with high P/E."""
    peg = calculate_peg_ratio(50.0, 25.0)
    assert peg == 2.0


def test_calculate_peg_ratio_low_growth():
    """Test PEG with low growth rate."""
    peg = calculate_peg_ratio(40.0, 5.0)
    assert peg == 8.0


def test_calculate_peg_ratio_zero_growth():
    """Test PEG calculation fails with zero growth."""
    with pytest.raises(ValueError, match="Earnings growth must be positive"):
        calculate_peg_ratio(30.0, 0.0)


def test_calculate_peg_ratio_negative_growth():
    """Test PEG calculation fails with negative growth."""
    with pytest.raises(ValueError, match="Earnings growth must be positive"):
        calculate_peg_ratio(30.0, -5.0)


# =============================================================================
# Signal Interpretation Tests
# =============================================================================


def test_interpret_peg_signal_buy_attractive():
    """Test BUY signal for attractive PEG < 0.5."""
    signal, confidence = interpret_peg_signal(0.4)
    assert signal == GrowthSignal.BUY
    assert confidence == "high"


def test_interpret_peg_signal_buy_moderate():
    """Test BUY signal for moderate PEG < 1.0."""
    signal, confidence = interpret_peg_signal(0.8)
    assert signal == GrowthSignal.BUY
    assert confidence == "medium"


def test_interpret_peg_signal_sell_expensive():
    """Test SELL signal for expensive PEG > 3.0."""
    signal, confidence = interpret_peg_signal(3.5)
    assert signal == GrowthSignal.SELL
    assert confidence == "high"


def test_interpret_peg_signal_sell_moderate():
    """Test SELL signal for moderate PEG > 2.0."""
    signal, confidence = interpret_peg_signal(2.5)
    assert signal == GrowthSignal.SELL
    assert confidence == "medium"


def test_interpret_peg_signal_hold():
    """Test HOLD signal for fair PEG between 1.0 and 2.0."""
    signal, confidence = interpret_peg_signal(1.5)
    assert signal == GrowthSignal.HOLD
    assert confidence == "medium"


def test_interpret_peg_signal_boundary_buy():
    """Test boundary: PEG just below 1.0 is BUY."""
    signal, confidence = interpret_peg_signal(0.99)
    assert signal == GrowthSignal.BUY


def test_interpret_peg_signal_boundary_hold_low():
    """Test boundary: PEG = 1.0 is HOLD."""
    signal, confidence = interpret_peg_signal(1.0)
    assert signal == GrowthSignal.HOLD


def test_interpret_peg_signal_boundary_hold_high():
    """Test boundary: PEG = 2.0 is HOLD."""
    signal, confidence = interpret_peg_signal(2.0)
    assert signal == GrowthSignal.HOLD


def test_interpret_peg_signal_boundary_sell():
    """Test boundary: PEG just above 2.0 is SELL."""
    signal, confidence = interpret_peg_signal(2.01)
    assert signal == GrowthSignal.SELL


# =============================================================================
# Growth Stock Analysis Tests
# =============================================================================


def test_analyze_growth_stock_buy_signal():
    """Test growth stock with BUY signal (attractive PEG)."""
    result = analyze_growth_stock("CRM", 35.0, 40.0)

    assert result.ticker == "CRM"
    assert result.analysis_mode == "GROWTH (PEG)"
    assert result.trailing_pe == 35.0
    assert result.earnings_growth_pct == 40.0
    assert result.peg_ratio == 0.88
    assert result.signal == GrowthSignal.BUY
    assert result.confidence in ("medium", "high")
    assert "0.88x" in result.explanation
    assert result.is_buy is True
    assert result.is_sell is False
    assert result.is_actionable is True


def test_analyze_growth_stock_sell_signal():
    """Test growth stock with SELL signal (expensive PEG)."""
    result = analyze_growth_stock("ADBE", 40.0, 10.0)

    assert result.ticker == "ADBE"
    assert result.peg_ratio == 4.0
    assert result.signal == GrowthSignal.SELL
    assert result.is_sell is True
    assert result.is_buy is False
    assert "doesn't justify" in result.explanation


def test_analyze_growth_stock_hold_signal():
    """Test growth stock with HOLD signal (fair PEG)."""
    result = analyze_growth_stock("NOW", 30.0, 20.0)

    assert result.ticker == "NOW"
    assert result.peg_ratio == 1.5
    assert result.signal == GrowthSignal.HOLD
    assert result.confidence == "medium"
    assert "fairly valued" in result.explanation


def test_analyze_growth_stock_invalid_pe():
    """Test handling of invalid trailing P/E."""
    result = analyze_growth_stock("TEST", None, 25.0)

    assert result.signal == GrowthSignal.DATA_ERROR
    assert result.confidence == "low"
    assert "Invalid trailing P/E" in result.explanation
    assert len(result.warnings) > 0


def test_analyze_growth_stock_missing_growth():
    """Test handling of missing earnings growth."""
    result = analyze_growth_stock("TEST", 30.0, None)

    assert result.signal == GrowthSignal.DATA_ERROR
    assert result.confidence == "low"
    assert "Missing earnings growth" in result.explanation


def test_analyze_growth_stock_zero_growth():
    """Test handling of zero earnings growth."""
    result = analyze_growth_stock("TEST", 30.0, 0.0)

    assert result.signal == GrowthSignal.DATA_ERROR
    assert result.confidence == "low"
    assert "zero earnings growth" in result.explanation.lower()
    assert any("HYPER_GROWTH" in w for w in result.warnings)


def test_analyze_growth_stock_negative_growth():
    """Test handling of negative earnings growth."""
    result = analyze_growth_stock("TEST", 30.0, -5.0)

    assert result.signal == GrowthSignal.DATA_ERROR
    assert "Negative" in result.explanation
    assert result.earnings_growth_pct == -5.0


def test_analyze_growth_stock_extreme_peg():
    """Test warning for extreme PEG ratio."""
    result = analyze_growth_stock("TEST", 50.0, 5.0)

    assert result.peg_ratio == 10.0
    assert any("Extreme PEG" in w for w in result.warnings)
    # Should still have a signal despite warning
    assert result.signal == GrowthSignal.SELL


def test_analyze_growth_stock_high_growth_warning():
    """Test warning for very high growth rate."""
    result = analyze_growth_stock("TEST", 30.0, 150.0)

    assert result.earnings_growth_pct == 150.0
    assert any("Very high growth" in w for w in result.warnings)
    assert any("not be sustainable" in w for w in result.warnings)


def test_analyze_growth_stock_negative_pe():
    """Test handling of negative P/E."""
    result = analyze_growth_stock("TEST", -10.0, 25.0)

    assert result.signal == GrowthSignal.DATA_ERROR
    assert "non-positive" in result.explanation.lower()


# =============================================================================
# Real-World Examples (From PRD)
# =============================================================================


def test_analyze_crm_example():
    """Test CRM example from PRD (typical growth stock)."""
    # CRM with P/E ~35 and growth ~25%
    result = analyze_growth_stock("CRM", 35.0, 25.0)

    assert result.peg_ratio == 1.4
    assert result.signal == GrowthSignal.HOLD
    # Fair value - paying 1.4x for each % growth


def test_analyze_attractive_growth_stock():
    """Test attractive growth stock (low PEG)."""
    # P/E 30, growth 50% → PEG = 0.6 → BUY
    result = analyze_growth_stock("EXAMPLE", 30.0, 50.0)

    assert result.peg_ratio == 0.6
    assert result.signal == GrowthSignal.BUY
    assert result.confidence == "medium"


def test_analyze_expensive_growth_stock():
    """Test expensive growth stock (high PEG)."""
    # P/E 45, growth 12% → PEG = 3.75 → SELL
    result = analyze_growth_stock("EXAMPLE", 45.0, 12.0)

    assert result.peg_ratio == 3.75
    assert result.signal == GrowthSignal.SELL
    assert result.confidence == "high"  # PEG > 3.0


# =============================================================================
# Batch Analysis Tests
# =============================================================================


def test_analyze_growth_batch_success():
    """Test batch analysis with valid data."""
    data = [
        {"ticker": "CRM", "trailing_pe": 35.0, "earnings_growth_pct": 40.0},
        {"ticker": "ADBE", "trailing_pe": 40.0, "earnings_growth_pct": 15.0},
        {"ticker": "NOW", "trailing_pe": 30.0, "earnings_growth_pct": 20.0},
    ]

    results = analyze_growth_batch(data)

    assert len(results) == 3
    assert results[0].ticker == "CRM"
    assert results[0].signal == GrowthSignal.BUY  # PEG = 0.88
    assert results[1].ticker == "ADBE"
    assert results[1].signal == GrowthSignal.SELL  # PEG = 2.67
    assert results[2].ticker == "NOW"
    assert results[2].signal == GrowthSignal.HOLD  # PEG = 1.5


def test_analyze_growth_batch_with_errors():
    """Test batch analysis handles errors gracefully."""
    data = [
        {"ticker": "VALID", "trailing_pe": 30.0, "earnings_growth_pct": 40.0},  # PEG = 0.75 → BUY
        {"ticker": "INVALID1", "trailing_pe": None, "earnings_growth_pct": 20.0},
        {"ticker": "INVALID2", "trailing_pe": 35.0, "earnings_growth_pct": 0.0},
    ]

    results = analyze_growth_batch(data)

    assert len(results) == 3
    assert results[0].signal == GrowthSignal.BUY
    assert results[1].signal == GrowthSignal.DATA_ERROR
    assert results[2].signal == GrowthSignal.DATA_ERROR


def test_analyze_growth_batch_empty():
    """Test batch analysis with empty list."""
    results = analyze_growth_batch([])
    assert len(results) == 0


# =============================================================================
# Ranking Tests
# =============================================================================


def test_rank_by_peg_ascending():
    """Test ranking by PEG (lowest first - best values)."""
    results = [
        GrowthAnalysisResult(ticker="HIGH", peg_ratio=3.0),
        GrowthAnalysisResult(ticker="LOW", peg_ratio=0.7),
        GrowthAnalysisResult(ticker="MID", peg_ratio=1.5),
    ]

    ranked = rank_by_peg(results, ascending=True)

    assert ranked[0].ticker == "LOW"  # 0.7
    assert ranked[1].ticker == "MID"  # 1.5
    assert ranked[2].ticker == "HIGH"  # 3.0


def test_rank_by_peg_descending():
    """Test ranking by PEG (highest first)."""
    results = [
        GrowthAnalysisResult(ticker="HIGH", peg_ratio=3.0),
        GrowthAnalysisResult(ticker="LOW", peg_ratio=0.7),
        GrowthAnalysisResult(ticker="MID", peg_ratio=1.5),
    ]

    ranked = rank_by_peg(results, ascending=False)

    assert ranked[0].ticker == "HIGH"  # 3.0
    assert ranked[1].ticker == "MID"  # 1.5
    assert ranked[2].ticker == "LOW"  # 0.7


# =============================================================================
# Edge Cases and Boundary Tests
# =============================================================================


@pytest.mark.parametrize(
    "pe,growth,expected_peg,expected_signal",
    [
        # BUY signals (PEG < 1.0)
        (25.0, 30.0, 0.83, GrowthSignal.BUY),
        (30.0, 40.0, 0.75, GrowthSignal.BUY),
        (40.0, 50.0, 0.80, GrowthSignal.BUY),
        (50.0, 100.0, 0.50, GrowthSignal.BUY),
        # HOLD signals (1.0 <= PEG <= 2.0)
        (25.0, 25.0, 1.00, GrowthSignal.HOLD),
        (30.0, 20.0, 1.50, GrowthSignal.HOLD),
        (40.0, 20.0, 2.00, GrowthSignal.HOLD),
        # SELL signals (PEG > 2.0)
        (40.0, 15.0, 2.67, GrowthSignal.SELL),
        (45.0, 10.0, 4.50, GrowthSignal.SELL),
        (50.0, 5.0, 10.00, GrowthSignal.SELL),
    ],
)
def test_analyze_growth_stock_parametrized(pe, growth, expected_peg, expected_signal):
    """Parametrized test covering various P/E and growth combinations."""
    result = analyze_growth_stock("TEST", pe, growth)
    assert result.peg_ratio == expected_peg
    assert result.signal == expected_signal


# =============================================================================
# GrowthAnalysisResult Property Tests
# =============================================================================


def test_growth_result_is_buy():
    """Test is_buy property."""
    result = GrowthAnalysisResult(ticker="TEST", signal=GrowthSignal.BUY)
    assert result.is_buy is True
    assert result.is_sell is False


def test_growth_result_is_sell():
    """Test is_sell property."""
    result = GrowthAnalysisResult(ticker="TEST", signal=GrowthSignal.SELL)
    assert result.is_sell is True
    assert result.is_buy is False


def test_growth_result_is_actionable_buy():
    """Test is_actionable for BUY signal."""
    result = GrowthAnalysisResult(ticker="TEST", signal=GrowthSignal.BUY)
    assert result.is_actionable is True


def test_growth_result_is_actionable_sell():
    """Test is_actionable for SELL signal."""
    result = GrowthAnalysisResult(ticker="TEST", signal=GrowthSignal.SELL)
    assert result.is_actionable is True


def test_growth_result_not_actionable_hold():
    """Test is_actionable for HOLD signal."""
    result = GrowthAnalysisResult(ticker="TEST", signal=GrowthSignal.HOLD)
    assert result.is_actionable is False


def test_growth_result_not_actionable_error():
    """Test is_actionable for DATA_ERROR signal."""
    result = GrowthAnalysisResult(ticker="TEST", signal=GrowthSignal.DATA_ERROR)
    assert result.is_actionable is False

