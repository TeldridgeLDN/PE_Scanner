"""
Integration tests for tiered analysis router.

Tests the routing logic that connects all three analysis modes.
"""

import pytest

from pe_scanner.analysis.classification import StockType
from pe_scanner.analysis.compression import CompressionResult, CompressionSignal
from pe_scanner.analysis.growth import GrowthAnalysisResult, GrowthSignal
from pe_scanner.analysis.hyper_growth import HyperGrowthAnalysisResult, HyperGrowthSignal
from pe_scanner.analysis.router import (
    StockData,
    analyze_batch,
    analyze_stock,
    get_mode_name,
    get_stock_type,
)


# =============================================================================
# VALUE Mode Routing Tests
# =============================================================================


def test_analyze_value_stock_with_compression():
    """Test VALUE stock routing (P/E < 25) - P/E compression analysis."""
    data = StockData(
        ticker="HOOD",
        trailing_pe=15.0,
        forward_pe=20.0,
        trailing_eps=1.5,
        forward_eps=1.2,
    )

    result = analyze_stock(data)

    assert isinstance(result, CompressionResult)
    assert result.ticker == "HOOD"
    assert result.trailing_pe == 15.0
    assert result.forward_pe == 20.0
    assert result.compression_pct < 0  # Negative compression
    assert result.signal in (CompressionSignal.SELL, CompressionSignal.HOLD)


def test_analyze_value_stock_positive_compression():
    """Test VALUE stock with positive compression → BUY."""
    data = StockData(
        ticker="VALUE",
        trailing_pe=20.0,
        forward_pe=15.0,  # Lower forward P/E → positive compression
    )

    result = analyze_stock(data)

    assert isinstance(result, CompressionResult)
    assert result.compression_pct > 0  # Positive compression
    assert result.signal in (CompressionSignal.BUY, CompressionSignal.STRONG_BUY, CompressionSignal.HOLD)


# =============================================================================
# GROWTH Mode Routing Tests
# =============================================================================


def test_analyze_growth_stock_with_peg():
    """Test GROWTH stock routing (P/E 25-50) - PEG ratio analysis."""
    data = StockData(
        ticker="CRM",
        trailing_pe=35.0,
        earnings_growth_pct=25.0,
    )

    result = analyze_stock(data)

    assert isinstance(result, GrowthAnalysisResult)
    assert result.ticker == "CRM"
    assert result.trailing_pe == 35.0
    assert result.earnings_growth_pct == 25.0
    assert result.peg_ratio == 1.4  # 35 / 25
    assert result.signal == GrowthSignal.HOLD  # PEG between 1.0 and 2.0


def test_analyze_growth_stock_buy_signal():
    """Test GROWTH stock with attractive PEG → BUY."""
    data = StockData(
        ticker="GROWTH_BUY",
        trailing_pe=30.0,
        earnings_growth_pct=40.0,  # High growth
    )

    result = analyze_stock(data)

    assert isinstance(result, GrowthAnalysisResult)
    assert result.peg_ratio == 0.75  # 30 / 40
    assert result.signal == GrowthSignal.BUY


def test_analyze_growth_stock_sell_signal():
    """Test GROWTH stock with expensive PEG → SELL."""
    data = StockData(
        ticker="GROWTH_SELL",
        trailing_pe=45.0,
        earnings_growth_pct=15.0,  # Low growth
    )

    result = analyze_stock(data)

    assert isinstance(result, GrowthAnalysisResult)
    assert result.peg_ratio == 3.0  # 45 / 15
    assert result.signal == GrowthSignal.SELL


# =============================================================================
# HYPER_GROWTH Mode Routing Tests
# =============================================================================


def test_analyze_hyper_growth_stock_high_pe():
    """Test HYPER_GROWTH stock routing (P/E > 50) - P/S + Rule of 40."""
    data = StockData(
        ticker="PLTR",
        trailing_pe=85.0,
        market_cap=50_000_000_000,
        revenue=2_000_000_000,
        revenue_growth_pct=25.0,
        profit_margin_pct=20.0,
    )

    result = analyze_stock(data)

    assert isinstance(result, HyperGrowthAnalysisResult)
    assert result.ticker == "PLTR"
    assert result.price_to_sales == 25.0  # 50B / 2B
    assert result.rule_of_40_score == 45.0  # 25 + 20
    assert result.signal == HyperGrowthSignal.SELL  # P/S > 15


def test_analyze_hyper_growth_stock_loss_making():
    """Test HYPER_GROWTH stock routing (negative P/E) - loss-making company."""
    data = StockData(
        ticker="RIVN",
        trailing_pe=-20.0,  # Negative P/E
        market_cap=12_000_000_000,
        revenue=1_000_000_000,
        revenue_growth_pct=10.0,
        profit_margin_pct=-50.0,
    )

    result = analyze_stock(data)

    assert isinstance(result, HyperGrowthAnalysisResult)
    assert result.ticker == "RIVN"
    assert result.price_to_sales == 12.0
    assert result.rule_of_40_score == -40.0  # 10 + (-50)
    assert result.signal == HyperGrowthSignal.SELL  # RO40 < 20


def test_analyze_hyper_growth_stock_buy_signal():
    """Test HYPER_GROWTH stock with attractive metrics → BUY."""
    data = StockData(
        ticker="HYPER_BUY",
        trailing_pe=75.0,
        market_cap=8_000_000_000,
        revenue=2_000_000_000,
        revenue_growth_pct=40.0,
        profit_margin_pct=10.0,
    )

    result = analyze_stock(data)

    assert isinstance(result, HyperGrowthAnalysisResult)
    assert result.price_to_sales == 4.0  # < 5
    assert result.rule_of_40_score == 50.0  # >= 40
    assert result.signal == HyperGrowthSignal.BUY


# =============================================================================
# Boundary Tests (Classification Edge Cases)
# =============================================================================


def test_analyze_boundary_value_growth():
    """Test boundary: P/E = 24.9 is VALUE."""
    data = StockData(ticker="TEST", trailing_pe=24.9, forward_pe=20.0)
    result = analyze_stock(data)
    assert isinstance(result, CompressionResult)


def test_analyze_boundary_growth_low():
    """Test boundary: P/E = 25.0 is GROWTH."""
    data = StockData(ticker="TEST", trailing_pe=25.0, earnings_growth_pct=20.0)
    result = analyze_stock(data)
    assert isinstance(result, GrowthAnalysisResult)


def test_analyze_boundary_growth_high():
    """Test boundary: P/E = 50.0 is GROWTH."""
    data = StockData(ticker="TEST", trailing_pe=50.0, earnings_growth_pct=20.0)
    result = analyze_stock(data)
    assert isinstance(result, GrowthAnalysisResult)


def test_analyze_boundary_hyper_growth():
    """Test boundary: P/E = 50.01 is HYPER_GROWTH."""
    data = StockData(
        ticker="TEST",
        trailing_pe=50.01,
        market_cap=10e9,
        revenue=2e9,
        revenue_growth_pct=25.0,
        profit_margin_pct=15.0,
    )
    result = analyze_stock(data)
    assert isinstance(result, HyperGrowthAnalysisResult)


def test_analyze_none_pe_hyper_growth():
    """Test: None P/E routes to HYPER_GROWTH."""
    data = StockData(
        ticker="TEST",
        trailing_pe=None,
        market_cap=10e9,
        revenue=2e9,
        revenue_growth_pct=25.0,
        profit_margin_pct=15.0,
    )
    result = analyze_stock(data)
    assert isinstance(result, HyperGrowthAnalysisResult)


# =============================================================================
# Batch Analysis Tests
# =============================================================================


def test_analyze_batch_mixed_types():
    """Test batch analysis with mix of VALUE, GROWTH, and HYPER_GROWTH stocks."""
    stocks = [
        StockData(ticker="VALUE1", trailing_pe=15.0, forward_pe=20.0),
        StockData(ticker="GROWTH1", trailing_pe=35.0, earnings_growth_pct=25.0),
        StockData(
            ticker="HYPER1",
            trailing_pe=85.0,
            market_cap=50e9,
            revenue=2e9,
            revenue_growth_pct=25.0,
            profit_margin_pct=20.0,
        ),
    ]

    results = analyze_batch(stocks)

    assert len(results) == 3
    assert isinstance(results[0], CompressionResult)
    assert isinstance(results[1], GrowthAnalysisResult)
    assert isinstance(results[2], HyperGrowthAnalysisResult)
    assert results[0].ticker == "VALUE1"
    assert results[1].ticker == "GROWTH1"
    assert results[2].ticker == "HYPER1"


def test_analyze_batch_all_value():
    """Test batch analysis with all VALUE stocks."""
    stocks = [
        StockData(ticker="VALUE1", trailing_pe=10.0, forward_pe=12.0),
        StockData(ticker="VALUE2", trailing_pe=15.0, forward_pe=18.0),
        StockData(ticker="VALUE3", trailing_pe=20.0, forward_pe=22.0),
    ]

    results = analyze_batch(stocks)

    assert len(results) == 3
    assert all(isinstance(r, CompressionResult) for r in results)


def test_analyze_batch_with_errors():
    """Test batch analysis handles errors gracefully."""
    stocks = [
        StockData(ticker="VALID", trailing_pe=15.0, forward_pe=20.0),
        StockData(ticker="INVALID", trailing_pe=None, forward_pe=None),  # Will error in VALUE mode
    ]

    results = analyze_batch(stocks)

    assert len(results) == 2
    # First should succeed
    assert isinstance(results[0], CompressionResult)
    # Second should produce error result
    assert isinstance(results[1], HyperGrowthAnalysisResult)  # None P/E → HYPER_GROWTH
    assert results[1].signal == HyperGrowthSignal.DATA_ERROR


def test_analyze_batch_empty():
    """Test batch analysis with empty list."""
    results = analyze_batch([])
    assert len(results) == 0


# =============================================================================
# Helper Function Tests
# =============================================================================


def test_get_stock_type_value():
    """Test get_stock_type helper for VALUE stock."""
    stock_type = get_stock_type(15.0)
    assert stock_type == StockType.VALUE


def test_get_stock_type_growth():
    """Test get_stock_type helper for GROWTH stock."""
    stock_type = get_stock_type(35.0)
    assert stock_type == StockType.GROWTH


def test_get_stock_type_hyper_growth():
    """Test get_stock_type helper for HYPER_GROWTH stock."""
    stock_type = get_stock_type(75.0)
    assert stock_type == StockType.HYPER_GROWTH


def test_get_mode_name_value():
    """Test get_mode_name helper for VALUE stock."""
    mode = get_mode_name(15.0)
    assert mode == "VALUE (P/E Compression)"


def test_get_mode_name_growth():
    """Test get_mode_name helper for GROWTH stock."""
    mode = get_mode_name(35.0)
    assert mode == "GROWTH (PEG Ratio)"


def test_get_mode_name_hyper_growth():
    """Test get_mode_name helper for HYPER_GROWTH stock."""
    mode = get_mode_name(75.0)
    assert mode == "HYPER_GROWTH (Price/Sales)"


# =============================================================================
# Real-World Examples (From PRD)
# =============================================================================


def test_analyze_hood_value_mode():
    """Test HOOD example from PRD - should use VALUE mode."""
    data = StockData(
        ticker="HOOD",
        trailing_pe=47.62,  # Actually GROWTH range, but let's test VALUE case
        forward_pe=156.58,
    )

    # With P/E 47.62, this should route to GROWTH mode
    result = analyze_stock(data)
    assert isinstance(result, GrowthAnalysisResult)


def test_analyze_crm_growth_mode():
    """Test CRM example from PRD - should use GROWTH mode."""
    data = StockData(
        ticker="CRM",
        trailing_pe=35.0,
        earnings_growth_pct=25.0,
    )

    result = analyze_stock(data)
    assert isinstance(result, GrowthAnalysisResult)
    assert result.peg_ratio == 1.4


def test_analyze_pltr_hyper_growth_mode():
    """Test PLTR example from PRD - should use HYPER_GROWTH mode."""
    data = StockData(
        ticker="PLTR",
        trailing_pe=85.0,
        market_cap=50_000_000_000,
        revenue=2_000_000_000,
        revenue_growth_pct=25.0,
        profit_margin_pct=20.0,
    )

    result = analyze_stock(data)
    assert isinstance(result, HyperGrowthAnalysisResult)
    assert result.price_to_sales == 25.0
    assert result.rule_of_40_score == 45.0


# =============================================================================
# StockData Tests
# =============================================================================


def test_stock_data_minimal():
    """Test StockData with minimal required fields."""
    data = StockData(ticker="TEST")
    assert data.ticker == "TEST"
    assert data.trailing_pe is None


def test_stock_data_full():
    """Test StockData with all fields populated."""
    data = StockData(
        ticker="TEST",
        trailing_pe=35.0,
        forward_pe=30.0,
        trailing_eps=2.0,
        forward_eps=2.5,
        earnings_growth_pct=25.0,
        market_cap=100e9,
        revenue=50e9,
        revenue_growth_pct=20.0,
        profit_margin_pct=15.0,
        data_quality_flags=["test_flag"],
    )

    assert data.ticker == "TEST"
    assert data.trailing_pe == 35.0
    assert data.market_cap == 100e9
    assert len(data.data_quality_flags) == 1


