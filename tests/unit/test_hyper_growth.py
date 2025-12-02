"""
Unit tests for hyper-growth mode analysis (Price/Sales + Rule of 40).

Tests the P/S ratio and Rule of 40 calculations for hyper-growth stocks.
"""

import pytest

from pe_scanner.analysis.hyper_growth import (
    HyperGrowthAnalysisResult,
    HyperGrowthSignal,
    analyze_hyper_growth_batch,
    analyze_hyper_growth_stock,
    calculate_price_to_sales,
    calculate_rule_of_40,
    interpret_hyper_growth_signal,
    rank_by_price_to_sales,
    rank_by_rule_of_40,
)


# =============================================================================
# Price/Sales Calculation Tests
# =============================================================================


def test_calculate_price_to_sales_typical():
    """Test typical P/S calculation."""
    ps = calculate_price_to_sales(10_000_000_000, 5_000_000_000)
    assert ps == 2.0


def test_calculate_price_to_sales_expensive():
    """Test P/S for expensive stock."""
    ps = calculate_price_to_sales(50_000_000_000, 2_000_000_000)
    assert ps == 25.0


def test_calculate_price_to_sales_cheap():
    """Test P/S for cheap stock."""
    ps = calculate_price_to_sales(3_000_000_000, 2_000_000_000)
    assert ps == 1.5


def test_calculate_price_to_sales_zero_revenue():
    """Test P/S calculation fails with zero revenue."""
    with pytest.raises(ValueError, match="Revenue must be positive"):
        calculate_price_to_sales(10_000_000_000, 0)


def test_calculate_price_to_sales_negative_revenue():
    """Test P/S calculation fails with negative revenue."""
    with pytest.raises(ValueError, match="Revenue must be positive"):
        calculate_price_to_sales(10_000_000_000, -1_000_000_000)


# =============================================================================
# Rule of 40 Calculation Tests
# =============================================================================


def test_calculate_rule_of_40_healthy():
    """Test Rule of 40 for healthy company."""
    score = calculate_rule_of_40(30.0, 15.0)
    assert score == 45.0


def test_calculate_rule_of_40_at_threshold():
    """Test Rule of 40 exactly at 40."""
    score = calculate_rule_of_40(25.0, 15.0)
    assert score == 40.0


def test_calculate_rule_of_40_weak():
    """Test Rule of 40 for weak company."""
    score = calculate_rule_of_40(10.0, 5.0)
    assert score == 15.0


def test_calculate_rule_of_40_loss_making():
    """Test Rule of 40 with negative profit margin."""
    score = calculate_rule_of_40(50.0, -10.0)
    assert score == 40.0


def test_calculate_rule_of_40_severe_losses():
    """Test Rule of 40 with severe losses."""
    score = calculate_rule_of_40(10.0, -50.0)
    assert score == -40.0


def test_calculate_rule_of_40_declining_revenue():
    """Test Rule of 40 with declining revenue."""
    score = calculate_rule_of_40(-5.0, 20.0)
    assert score == 15.0


# =============================================================================
# Signal Interpretation Tests
# =============================================================================


def test_interpret_hyper_growth_signal_strong_buy():
    """Test strong BUY signal (P/S < 3, RO40 >= 50)."""
    signal, confidence = interpret_hyper_growth_signal(2.5, 52.0)
    assert signal == HyperGrowthSignal.BUY
    assert confidence == "high"


def test_interpret_hyper_growth_signal_moderate_buy():
    """Test moderate BUY signal (P/S < 5, RO40 >= 40)."""
    signal, confidence = interpret_hyper_growth_signal(4.5, 42.0)
    assert signal == HyperGrowthSignal.BUY
    assert confidence == "medium"


def test_interpret_hyper_growth_signal_strong_sell_both():
    """Test strong SELL signal (expensive AND weak)."""
    signal, confidence = interpret_hyper_growth_signal(18.0, 15.0)
    assert signal == HyperGrowthSignal.SELL
    assert confidence == "high"


def test_interpret_hyper_growth_signal_sell_expensive():
    """Test SELL signal for expensive stock."""
    signal, confidence = interpret_hyper_growth_signal(18.0, 50.0)
    assert signal == HyperGrowthSignal.SELL
    assert confidence == "medium"


def test_interpret_hyper_growth_signal_sell_weak():
    """Test SELL signal for weak fundamentals."""
    signal, confidence = interpret_hyper_growth_signal(8.0, 15.0)
    assert signal == HyperGrowthSignal.SELL
    assert confidence == "medium"


def test_interpret_hyper_growth_signal_sell_very_expensive():
    """Test SELL with high confidence for very expensive (P/S > 20)."""
    signal, confidence = interpret_hyper_growth_signal(25.0, 35.0)
    assert signal == HyperGrowthSignal.SELL
    assert confidence == "high"


def test_interpret_hyper_growth_signal_sell_very_weak():
    """Test SELL with high confidence for very weak (RO40 < 10)."""
    signal, confidence = interpret_hyper_growth_signal(10.0, 5.0)
    assert signal == HyperGrowthSignal.SELL
    assert confidence == "high"


def test_interpret_hyper_growth_signal_hold():
    """Test HOLD signal for mixed signals."""
    signal, confidence = interpret_hyper_growth_signal(8.0, 30.0)
    assert signal == HyperGrowthSignal.HOLD
    assert confidence == "medium"


def test_interpret_hyper_growth_signal_boundary_buy_ps():
    """Test boundary: P/S just below 5 with good RO40 is BUY."""
    signal, confidence = interpret_hyper_growth_signal(4.99, 40.0)
    assert signal == HyperGrowthSignal.BUY


def test_interpret_hyper_growth_signal_boundary_hold_ps():
    """Test boundary: P/S = 5 with good RO40 is HOLD."""
    signal, confidence = interpret_hyper_growth_signal(5.0, 40.0)
    assert signal == HyperGrowthSignal.HOLD


def test_interpret_hyper_growth_signal_boundary_sell_ps():
    """Test boundary: P/S just above 15 is SELL."""
    signal, confidence = interpret_hyper_growth_signal(15.01, 40.0)
    assert signal == HyperGrowthSignal.SELL


def test_interpret_hyper_growth_signal_boundary_sell_ro40():
    """Test boundary: RO40 just below 20 is SELL."""
    signal, confidence = interpret_hyper_growth_signal(10.0, 19.99)
    assert signal == HyperGrowthSignal.SELL


# =============================================================================
# Hyper-Growth Stock Analysis Tests
# =============================================================================


def test_analyze_hyper_growth_stock_buy_signal():
    """Test hyper-growth stock with BUY signal."""
    result = analyze_hyper_growth_stock(
        ticker="PLTR",
        market_cap=40_000_000_000,
        revenue=2_000_000_000,
        revenue_growth_pct=30.0,
        profit_margin_pct=15.0,
    )

    assert result.ticker == "PLTR"
    assert result.analysis_mode == "HYPER_GROWTH (Price/Sales)"
    assert result.price_to_sales == 20.0
    assert result.revenue_growth_pct == 30.0
    assert result.profit_margin_pct == 15.0
    assert result.rule_of_40_score == 45.0
    assert result.signal == HyperGrowthSignal.SELL  # P/S > 15 despite good RO40
    assert result.is_buy is False
    assert result.is_sell is True


def test_analyze_hyper_growth_stock_attractive_buy():
    """Test truly attractive hyper-growth stock (low P/S + strong RO40)."""
    result = analyze_hyper_growth_stock(
        ticker="EXAMPLE",
        market_cap=8_000_000_000,
        revenue=2_000_000_000,
        revenue_growth_pct=40.0,
        profit_margin_pct=10.0,
    )

    assert result.price_to_sales == 4.0
    assert result.rule_of_40_score == 50.0
    assert result.signal == HyperGrowthSignal.BUY
    assert result.confidence == "medium"


def test_analyze_hyper_growth_stock_sell_expensive():
    """Test expensive hyper-growth stock."""
    result = analyze_hyper_growth_stock(
        ticker="EXPENSIVE",
        market_cap=100_000_000_000,
        revenue=2_000_000_000,
        revenue_growth_pct=25.0,
        profit_margin_pct=20.0,
    )

    assert result.price_to_sales == 50.0
    assert result.signal == HyperGrowthSignal.SELL
    assert ("expensive" in result.explanation.lower() or "too high" in result.explanation.lower())


def test_analyze_hyper_growth_stock_sell_weak():
    """Test hyper-growth stock with weak fundamentals."""
    result = analyze_hyper_growth_stock(
        ticker="WEAK",
        market_cap=10_000_000_000,
        revenue=2_000_000_000,
        revenue_growth_pct=5.0,
        profit_margin_pct=10.0,
    )

    assert result.price_to_sales == 5.0
    assert result.rule_of_40_score == 15.0
    assert result.signal == HyperGrowthSignal.SELL  # RO40 < 20
    assert "weak" in result.explanation.lower()


def test_analyze_hyper_growth_stock_hold():
    """Test hyper-growth stock with HOLD signal."""
    result = analyze_hyper_growth_stock(
        ticker="HOLD",
        market_cap=15_000_000_000,
        revenue=2_000_000_000,
        revenue_growth_pct=20.0,
        profit_margin_pct=15.0,
    )

    assert result.price_to_sales == 7.5
    assert result.rule_of_40_score == 35.0
    assert result.signal == HyperGrowthSignal.HOLD
    assert "fairly valued" in result.explanation


def test_analyze_hyper_growth_stock_invalid_market_cap():
    """Test handling of invalid market cap."""
    result = analyze_hyper_growth_stock(
        ticker="TEST", market_cap=None, revenue=2e9, revenue_growth_pct=25.0, profit_margin_pct=10.0
    )

    assert result.signal == HyperGrowthSignal.DATA_ERROR
    assert "Invalid market cap" in result.explanation


def test_analyze_hyper_growth_stock_missing_revenue():
    """Test handling of missing revenue."""
    result = analyze_hyper_growth_stock(
        ticker="TEST", market_cap=10e9, revenue=None, revenue_growth_pct=25.0, profit_margin_pct=10.0
    )

    assert result.signal == HyperGrowthSignal.DATA_ERROR
    assert "revenue" in result.explanation.lower()


def test_analyze_hyper_growth_stock_missing_growth():
    """Test handling of missing revenue growth."""
    result = analyze_hyper_growth_stock(
        ticker="TEST", market_cap=10e9, revenue=2e9, revenue_growth_pct=None, profit_margin_pct=10.0
    )

    # Should still work, defaulting growth to 0
    assert result.signal in (HyperGrowthSignal.SELL, HyperGrowthSignal.HOLD)
    assert any("Missing revenue growth" in w for w in result.warnings)


def test_analyze_hyper_growth_stock_missing_margin():
    """Test handling of missing profit margin."""
    result = analyze_hyper_growth_stock(
        ticker="TEST", market_cap=10e9, revenue=2e9, revenue_growth_pct=30.0, profit_margin_pct=None
    )

    # Should still work, defaulting margin to 0
    assert result.signal in (
        HyperGrowthSignal.BUY,
        HyperGrowthSignal.SELL,
        HyperGrowthSignal.HOLD,
    )
    assert any("Missing profit margin" in w for w in result.warnings)


def test_analyze_hyper_growth_stock_extreme_ps():
    """Test warning for extreme P/S ratio."""
    result = analyze_hyper_growth_stock(
        ticker="TEST", market_cap=100e9, revenue=2e9, revenue_growth_pct=30.0, profit_margin_pct=15.0
    )

    assert result.price_to_sales == 50.0
    assert any("Extreme P/S" in w for w in result.warnings)


def test_analyze_hyper_growth_stock_negative_ro40():
    """Test warning for negative Rule of 40."""
    result = analyze_hyper_growth_stock(
        ticker="TEST", market_cap=10e9, revenue=2e9, revenue_growth_pct=-10.0, profit_margin_pct=-50.0
    )

    assert result.rule_of_40_score == -60.0
    assert any("Negative Rule of 40" in w for w in result.warnings)


def test_analyze_hyper_growth_stock_declining_revenue():
    """Test warning for declining revenue."""
    result = analyze_hyper_growth_stock(
        ticker="TEST", market_cap=10e9, revenue=2e9, revenue_growth_pct=-15.0, profit_margin_pct=10.0
    )

    assert any("declining" in w.lower() for w in result.warnings)


def test_analyze_hyper_growth_stock_severe_losses():
    """Test warning for severe losses."""
    result = analyze_hyper_growth_stock(
        ticker="RIVN",
        market_cap=12e9,
        revenue=1e9,
        revenue_growth_pct=10.0,
        profit_margin_pct=-60.0,
    )

    assert any("Severe losses" in w for w in result.warnings)


# =============================================================================
# Real-World Examples (From PRD)
# =============================================================================


def test_analyze_rivn_example():
    """Test RIVN example from PRD (loss-making hyper-growth)."""
    # RIVN at ~12x sales with weak fundamentals
    result = analyze_hyper_growth_stock(
        ticker="RIVN",
        market_cap=12_000_000_000,
        revenue=1_000_000_000,
        revenue_growth_pct=10.0,
        profit_margin_pct=-50.0,
    )

    assert result.price_to_sales == 12.0
    assert result.rule_of_40_score == -40.0
    assert result.signal == HyperGrowthSignal.SELL  # RO40 < 20


def test_analyze_pltr_expensive():
    """Test PLTR when expensive (high P/S)."""
    result = analyze_hyper_growth_stock(
        ticker="PLTR",
        market_cap=50_000_000_000,
        revenue=2_000_000_000,
        revenue_growth_pct=25.0,
        profit_margin_pct=20.0,
    )

    assert result.price_to_sales == 25.0
    assert result.signal == HyperGrowthSignal.SELL  # P/S > 15


# =============================================================================
# Batch Analysis Tests
# =============================================================================


def test_analyze_hyper_growth_batch_success():
    """Test batch analysis with valid data."""
    data = [
        {
            "ticker": "BUY",
            "market_cap": 8e9,
            "revenue": 2e9,
            "revenue_growth_pct": 40.0,
            "profit_margin_pct": 10.0,
        },
        {
            "ticker": "SELL",
            "market_cap": 100e9,
            "revenue": 2e9,
            "revenue_growth_pct": 10.0,
            "profit_margin_pct": 5.0,
        },
        {
            "ticker": "HOLD",
            "market_cap": 15e9,
            "revenue": 2e9,
            "revenue_growth_pct": 20.0,
            "profit_margin_pct": 15.0,
        },
    ]

    results = analyze_hyper_growth_batch(data)

    assert len(results) == 3
    assert results[0].ticker == "BUY"
    assert results[0].signal == HyperGrowthSignal.BUY  # P/S=4, RO40=50
    assert results[1].ticker == "SELL"
    assert results[1].signal == HyperGrowthSignal.SELL  # P/S=50
    assert results[2].ticker == "HOLD"
    assert results[2].signal == HyperGrowthSignal.HOLD  # P/S=7.5, RO40=35


def test_analyze_hyper_growth_batch_with_errors():
    """Test batch analysis handles errors gracefully."""
    data = [
        {
            "ticker": "VALID",
            "market_cap": 10e9,
            "revenue": 2e9,
            "revenue_growth_pct": 30.0,
            "profit_margin_pct": 15.0,
        },
        {
            "ticker": "INVALID1",
            "market_cap": None,
            "revenue": 2e9,
            "revenue_growth_pct": 25.0,
            "profit_margin_pct": 10.0,
        },
        {
            "ticker": "INVALID2",
            "market_cap": 10e9,
            "revenue": 0,
            "revenue_growth_pct": 20.0,
            "profit_margin_pct": 5.0,
        },
    ]

    results = analyze_hyper_growth_batch(data)

    assert len(results) == 3
    assert results[0].signal in (
        HyperGrowthSignal.BUY,
        HyperGrowthSignal.SELL,
        HyperGrowthSignal.HOLD,
    )
    assert results[1].signal == HyperGrowthSignal.DATA_ERROR
    assert results[2].signal == HyperGrowthSignal.DATA_ERROR


def test_analyze_hyper_growth_batch_empty():
    """Test batch analysis with empty list."""
    results = analyze_hyper_growth_batch([])
    assert len(results) == 0


# =============================================================================
# Ranking Tests
# =============================================================================


def test_rank_by_rule_of_40_descending():
    """Test ranking by Rule of 40 (highest first - best)."""
    results = [
        HyperGrowthAnalysisResult(ticker="LOW", rule_of_40_score=15.0),
        HyperGrowthAnalysisResult(ticker="HIGH", rule_of_40_score=50.0),
        HyperGrowthAnalysisResult(ticker="MID", rule_of_40_score=35.0),
    ]

    ranked = rank_by_rule_of_40(results, ascending=False)

    assert ranked[0].ticker == "HIGH"  # 50.0
    assert ranked[1].ticker == "MID"  # 35.0
    assert ranked[2].ticker == "LOW"  # 15.0


def test_rank_by_rule_of_40_ascending():
    """Test ranking by Rule of 40 (lowest first)."""
    results = [
        HyperGrowthAnalysisResult(ticker="LOW", rule_of_40_score=15.0),
        HyperGrowthAnalysisResult(ticker="HIGH", rule_of_40_score=50.0),
        HyperGrowthAnalysisResult(ticker="MID", rule_of_40_score=35.0),
    ]

    ranked = rank_by_rule_of_40(results, ascending=True)

    assert ranked[0].ticker == "LOW"  # 15.0
    assert ranked[1].ticker == "MID"  # 35.0
    assert ranked[2].ticker == "HIGH"  # 50.0


def test_rank_by_price_to_sales_ascending():
    """Test ranking by P/S (lowest first - best values)."""
    results = [
        HyperGrowthAnalysisResult(ticker="HIGH", price_to_sales=20.0),
        HyperGrowthAnalysisResult(ticker="LOW", price_to_sales=3.0),
        HyperGrowthAnalysisResult(ticker="MID", price_to_sales=10.0),
    ]

    ranked = rank_by_price_to_sales(results, ascending=True)

    assert ranked[0].ticker == "LOW"  # 3.0
    assert ranked[1].ticker == "MID"  # 10.0
    assert ranked[2].ticker == "HIGH"  # 20.0


def test_rank_by_price_to_sales_descending():
    """Test ranking by P/S (highest first)."""
    results = [
        HyperGrowthAnalysisResult(ticker="HIGH", price_to_sales=20.0),
        HyperGrowthAnalysisResult(ticker="LOW", price_to_sales=3.0),
        HyperGrowthAnalysisResult(ticker="MID", price_to_sales=10.0),
    ]

    ranked = rank_by_price_to_sales(results, ascending=False)

    assert ranked[0].ticker == "HIGH"  # 20.0
    assert ranked[1].ticker == "MID"  # 10.0
    assert ranked[2].ticker == "LOW"  # 3.0


# =============================================================================
# Parametrized Tests
# =============================================================================


@pytest.mark.parametrize(
    "ps,ro40,expected_signal",
    [
        # BUY signals (P/S < 5 AND RO40 >= 40)
        (2.0, 50.0, HyperGrowthSignal.BUY),
        (3.5, 45.0, HyperGrowthSignal.BUY),
        (4.5, 40.0, HyperGrowthSignal.BUY),
        # SELL signals (P/S > 15 OR RO40 < 20)
        (18.0, 50.0, HyperGrowthSignal.SELL),  # Expensive
        (8.0, 15.0, HyperGrowthSignal.SELL),  # Weak
        (20.0, 10.0, HyperGrowthSignal.SELL),  # Both
        # HOLD signals (otherwise)
        (8.0, 30.0, HyperGrowthSignal.HOLD),
        (10.0, 25.0, HyperGrowthSignal.HOLD),
        (5.0, 35.0, HyperGrowthSignal.HOLD),
    ],
)
def test_interpret_hyper_growth_signal_parametrized(ps, ro40, expected_signal):
    """Parametrized test covering various P/S and Rule of 40 combinations."""
    signal, _ = interpret_hyper_growth_signal(ps, ro40)
    assert signal == expected_signal


# =============================================================================
# HyperGrowthAnalysisResult Property Tests
# =============================================================================


def test_hyper_growth_result_is_buy():
    """Test is_buy property."""
    result = HyperGrowthAnalysisResult(ticker="TEST", signal=HyperGrowthSignal.BUY)
    assert result.is_buy is True
    assert result.is_sell is False


def test_hyper_growth_result_is_sell():
    """Test is_sell property."""
    result = HyperGrowthAnalysisResult(ticker="TEST", signal=HyperGrowthSignal.SELL)
    assert result.is_sell is True
    assert result.is_buy is False


def test_hyper_growth_result_is_actionable_buy():
    """Test is_actionable for BUY signal."""
    result = HyperGrowthAnalysisResult(ticker="TEST", signal=HyperGrowthSignal.BUY)
    assert result.is_actionable is True


def test_hyper_growth_result_is_actionable_sell():
    """Test is_actionable for SELL signal."""
    result = HyperGrowthAnalysisResult(ticker="TEST", signal=HyperGrowthSignal.SELL)
    assert result.is_actionable is True


def test_hyper_growth_result_not_actionable_hold():
    """Test is_actionable for HOLD signal."""
    result = HyperGrowthAnalysisResult(ticker="TEST", signal=HyperGrowthSignal.HOLD)
    assert result.is_actionable is False


def test_hyper_growth_result_not_actionable_error():
    """Test is_actionable for DATA_ERROR signal."""
    result = HyperGrowthAnalysisResult(ticker="TEST", signal=HyperGrowthSignal.DATA_ERROR)
    assert result.is_actionable is False

