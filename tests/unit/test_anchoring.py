"""
Unit tests for anchoring engine.

Tests the generation of memorable anchor statements for analysis results.
"""

import pytest

from pe_scanner.analysis.anchoring import generate_anchor, generate_anchors_batch
from pe_scanner.analysis.compression import CompressionResult, CompressionSignal
from pe_scanner.analysis.growth import GrowthAnalysisResult, GrowthSignal
from pe_scanner.analysis.hyper_growth import HyperGrowthAnalysisResult, HyperGrowthSignal


# =============================================================================
# VALUE Mode Anchoring Tests (Profit Multiplication)
# =============================================================================


def test_anchor_value_severe_negative_compression():
    """Test VALUE anchor for severe negative compression (<-30%)."""
    result = CompressionResult(
        ticker="HOOD",
        trailing_pe=73.27,
        forward_pe=156.58,
        compression_pct=-113.70,
        implied_growth_pct=-53.2,
        signal=CompressionSignal.STRONG_SELL,
        confidence="high",
    )
    
    market_cap = 10_000_000_000  # $10B
    anchor = generate_anchor(result, market_cap)
    
    # Should mention profit decline and multiplication required
    assert "HOOD" in anchor
    assert "DROP" in anchor or "decline" in anchor.lower()
    assert "grow profits" in anchor.lower()
    assert "x" in anchor  # Multiplication factor


def test_anchor_value_moderate_negative_compression():
    """Test VALUE anchor for moderate negative compression (-20% to -30%)."""
    result = CompressionResult(
        ticker="TEST",
        trailing_pe=20.0,
        forward_pe=25.0,
        compression_pct=-25.0,
        implied_growth_pct=0.0,
        signal=CompressionSignal.SELL,
        confidence="medium",
    )
    
    anchor = generate_anchor(result)
    
    # Should use fallback anchor (compression not severe enough)
    assert "TEST" in anchor
    assert "priced for" in anchor


def test_anchor_value_positive_compression():
    """Test VALUE anchor for positive compression (BUY signal)."""
    result = CompressionResult(
        ticker="VALUE_BUY",
        trailing_pe=20.0,
        forward_pe=15.0,
        compression_pct=25.0,
        implied_growth_pct=0.0,
        signal=CompressionSignal.BUY,
        confidence="high",
    )
    
    anchor = generate_anchor(result)
    
    assert "VALUE_BUY" in anchor
    assert "buy" in anchor.lower()


# =============================================================================
# GROWTH Mode Anchoring Tests (Growth Requirement)
# =============================================================================


def test_anchor_growth_high_pe():
    """Test GROWTH anchor for high P/E (>30)."""
    result = GrowthAnalysisResult(
        ticker="NVDA",
        trailing_pe=65.0,
        earnings_growth_pct=20.0,
        peg_ratio=3.25,
        signal=GrowthSignal.SELL,
        confidence="high",
        explanation="Expensive",
    )
    
    anchor = generate_anchor(result)
    
    # Should mention growth requirement
    assert "NVDA" in anchor
    assert "65" in anchor or "P/E" in anchor
    assert "growth" in anchor.lower()
    assert "years" in anchor.lower()
    assert "5%" in anchor  # "Only 5% of companies achieve this"


def test_anchor_growth_attractive_peg():
    """Test GROWTH anchor for attractive PEG (<1.0)."""
    result = GrowthAnalysisResult(
        ticker="CRM",
        trailing_pe=30.0,
        earnings_growth_pct=40.0,
        peg_ratio=0.75,
        signal=GrowthSignal.BUY,
        confidence="high",
        explanation="Attractive",
    )
    
    anchor = generate_anchor(result)
    
    assert "CRM" in anchor
    assert "0.75" in anchor or "0.8" in anchor
    assert "attractive" in anchor.lower()
    assert "40" in anchor  # Growth rate


def test_anchor_growth_expensive_peg():
    """Test GROWTH anchor for expensive PEG (>2.0)."""
    result = GrowthAnalysisResult(
        ticker="EXPENSIVE",
        trailing_pe=25.0,
        earnings_growth_pct=10.0,
        peg_ratio=2.5,
        signal=GrowthSignal.SELL,
        confidence="medium",
        explanation="Too expensive",
    )
    
    anchor = generate_anchor(result)
    
    assert "EXPENSIVE" in anchor
    assert "2.5" in anchor
    assert "expensive" in anchor.lower()
    assert "10" in anchor  # Growth rate


def test_anchor_growth_fair_value():
    """Test GROWTH anchor for fair PEG (1.0-2.0)."""
    result = GrowthAnalysisResult(
        ticker="FAIR",
        trailing_pe=28.0,
        earnings_growth_pct=20.0,
        peg_ratio=1.4,
        signal=GrowthSignal.HOLD,
        confidence="medium",
        explanation="Fair",
    )
    
    anchor = generate_anchor(result)
    
    assert "FAIR" in anchor
    assert "1.4" in anchor
    assert "fairly valued" in anchor.lower()


# =============================================================================
# HYPER_GROWTH Mode Anchoring Tests (Profitability Improvement)
# =============================================================================


def test_anchor_hyper_growth_expensive():
    """Test HYPER_GROWTH anchor for expensive stock (P/S >10)."""
    result = HyperGrowthAnalysisResult(
        ticker="PLTR",
        price_to_sales=25.0,
        revenue_growth_pct=25.0,
        profit_margin_pct=20.0,
        rule_of_40_score=45.0,
        signal=HyperGrowthSignal.SELL,
        confidence="high",
        explanation="Expensive",
    )
    
    anchor = generate_anchor(result)
    
    assert "PLTR" in anchor
    assert "25" in anchor  # P/S ratio
    assert "profitability" in anchor.lower()
    assert "45" in anchor  # Current Rule of 40


def test_anchor_hyper_growth_loss_making():
    """Test HYPER_GROWTH anchor for loss-making company with declining revenue."""
    result = HyperGrowthAnalysisResult(
        ticker="RIVN",
        price_to_sales=12.0,
        revenue_growth_pct=-10.0,
        profit_margin_pct=-50.0,
        rule_of_40_score=-60.0,
        signal=HyperGrowthSignal.SELL,
        confidence="high",
        explanation="Severe issues",
    )
    
    anchor = generate_anchor(result)
    
    assert "RIVN" in anchor
    assert "severe" in anchor.lower() or "challenges" in anchor.lower()
    assert "declining" in anchor.lower() or "losses" in anchor.lower()


def test_anchor_hyper_growth_attractive():
    """Test HYPER_GROWTH anchor for attractive stock (P/S <5, RO40 >=40)."""
    result = HyperGrowthAnalysisResult(
        ticker="ATTRACTIVE",
        price_to_sales=4.0,
        revenue_growth_pct=40.0,
        profit_margin_pct=10.0,
        rule_of_40_score=50.0,
        signal=HyperGrowthSignal.BUY,
        confidence="high",
        explanation="Strong value",
    )
    
    anchor = generate_anchor(result)
    
    assert "ATTRACTIVE" in anchor
    assert "4" in anchor  # P/S
    assert "50" in anchor  # Rule of 40
    assert "strong" in anchor.lower() or "value" in anchor.lower()


def test_anchor_hyper_growth_moderate():
    """Test HYPER_GROWTH anchor for moderate stock."""
    result = HyperGrowthAnalysisResult(
        ticker="MODERATE",
        price_to_sales=8.0,
        revenue_growth_pct=20.0,
        profit_margin_pct=15.0,
        rule_of_40_score=35.0,
        signal=HyperGrowthSignal.HOLD,
        confidence="medium",
        explanation="Fair",
    )
    
    anchor = generate_anchor(result)
    
    assert "MODERATE" in anchor
    assert "priced for" in anchor


# =============================================================================
# Mega-Cap Comparison Tests
# =============================================================================


def test_anchor_mega_cap_comparison():
    """Test mega-cap comparison anchor (market cap > $500B with implied profit > Apple's)."""
    result = CompressionResult(
        ticker="MEGA",
        trailing_pe=60.0,
        forward_pe=25.0,  # Lower forward P/E = higher implied profit
        compression_pct=58.33,  # Positive compression (BUY signal)
        implied_growth_pct=0.0,
        signal=CompressionSignal.STRONG_BUY,
        confidence="high",
    )
    
    market_cap = 3_000_000_000_000  # $3T
    # Implied profit = $3T / 25 = $120B > Apple's $100B
    anchor = generate_anchor(result, market_cap)
    
    # Should trigger mega-cap comparison (implied profit > Apple's)
    assert "MEGA" in anchor
    assert "Apple" in anchor
    assert "$" in anchor
    assert "B" in anchor  # Billions
    assert "120" in anchor or "profit" in anchor.lower()


def test_anchor_mega_cap_below_threshold():
    """Test that mega-cap comparison doesn't trigger for market cap < $500B."""
    result = CompressionResult(
        ticker="NORMAL",
        trailing_pe=20.0,
        forward_pe=18.0,
        compression_pct=10.0,
        implied_growth_pct=0.0,
        signal=CompressionSignal.BUY,
        confidence="medium",
    )
    
    market_cap = 100_000_000_000  # $100B (below threshold)
    anchor = generate_anchor(result, market_cap)
    
    # Should NOT mention Apple or large profit comparisons
    assert "Apple" not in anchor


# =============================================================================
# Fallback Tests
# =============================================================================


def test_anchor_fallback_no_market_cap():
    """Test fallback anchor when market cap not provided."""
    result = CompressionResult(
        ticker="TEST",
        trailing_pe=20.0,
        forward_pe=22.0,
        compression_pct=-10.0,
        implied_growth_pct=0.0,
        signal=CompressionSignal.HOLD,
        confidence="medium",
    )
    
    anchor = generate_anchor(result)  # No market cap
    
    assert "TEST" in anchor
    assert "priced for" in anchor


def test_anchor_fallback_data_error():
    """Test fallback anchor for DATA_ERROR signal."""
    result = CompressionResult(
        ticker="ERROR",
        trailing_pe=0.0,
        forward_pe=0.0,
        compression_pct=0.0,
        implied_growth_pct=0.0,
        signal=CompressionSignal.DATA_ERROR,
        confidence="low",
        warnings=["Invalid data"],
    )
    
    anchor = generate_anchor(result)
    
    assert "ERROR" in anchor


# =============================================================================
# Batch Anchoring Tests
# =============================================================================


def test_generate_anchors_batch():
    """Test batch anchor generation."""
    results = [
        CompressionResult(
            ticker="STOCK1",
            trailing_pe=15.0,
            forward_pe=20.0,
            compression_pct=-33.33,
            implied_growth_pct=0.0,
            signal=CompressionSignal.SELL,
            confidence="high",
        ),
        GrowthAnalysisResult(
            ticker="STOCK2",
            trailing_pe=40.0,
            earnings_growth_pct=25.0,
            peg_ratio=1.6,
            signal=GrowthSignal.HOLD,
            confidence="medium",
            explanation="Fair",
        ),
        HyperGrowthAnalysisResult(
            ticker="STOCK3",
            price_to_sales=15.0,
            revenue_growth_pct=30.0,
            profit_margin_pct=10.0,
            rule_of_40_score=40.0,
            signal=HyperGrowthSignal.SELL,
            confidence="medium",
            explanation="Expensive",
        ),
    ]
    
    market_caps = {
        "STOCK1": 10e9,
        "STOCK2": 50e9,
        "STOCK3": 100e9,
    }
    
    anchors = generate_anchors_batch(results, market_caps)
    
    assert len(anchors) == 3
    assert "STOCK1" in anchors["STOCK1"]
    assert "STOCK2" in anchors["STOCK2"]
    assert "STOCK3" in anchors["STOCK3"]


def test_generate_anchors_batch_no_market_caps():
    """Test batch anchor generation without market caps."""
    results = [
        GrowthAnalysisResult(
            ticker="TEST",
            trailing_pe=30.0,
            earnings_growth_pct=25.0,
            peg_ratio=1.2,
            signal=GrowthSignal.HOLD,
            confidence="medium",
            explanation="Fair",
        ),
    ]
    
    anchors = generate_anchors_batch(results)
    
    assert len(anchors) == 1
    assert "TEST" in anchors["TEST"]


def test_generate_anchors_batch_empty():
    """Test batch anchor generation with empty list."""
    anchors = generate_anchors_batch([])
    assert len(anchors) == 0


# =============================================================================
# Real-World Examples (From PRD)
# =============================================================================


def test_anchor_hood_example():
    """Test HOOD example from PRD."""
    result = CompressionResult(
        ticker="HOOD",
        trailing_pe=73.27,
        forward_pe=156.58,
        compression_pct=-113.70,
        implied_growth_pct=-53.2,
        signal=CompressionSignal.STRONG_SELL,
        confidence="high",
    )
    
    market_cap = 10_000_000_000
    anchor = generate_anchor(result, market_cap)
    
    # Should mention profit multiplication (roughly 2.5x-3.5x range)
    assert "HOOD" in anchor
    assert "profit" in anchor.lower()
    assert "x" in anchor


def test_anchor_nvda_growth_requirement():
    """Test NVDA growth requirement example."""
    result = GrowthAnalysisResult(
        ticker="NVDA",
        trailing_pe=65.0,
        earnings_growth_pct=20.0,
        peg_ratio=3.25,
        signal=GrowthSignal.SELL,
        confidence="high",
        explanation="Expensive",
    )
    
    anchor = generate_anchor(result)
    
    # Should mention 65% growth needed for 5 years
    assert "NVDA" in anchor
    assert "65" in anchor
    assert "5 years" in anchor or "5%" in anchor


def test_anchor_rivn_profitability():
    """Test RIVN profitability requirement example (expensive with weak fundamentals)."""
    result = HyperGrowthAnalysisResult(
        ticker="RIVN",
        price_to_sales=12.0,
        revenue_growth_pct=10.0,  # Positive growth, so not "severe challenges"
        profit_margin_pct=-50.0,
        rule_of_40_score=-40.0,
        signal=HyperGrowthSignal.SELL,
        confidence="high",
        explanation="Weak",
    )
    
    anchor = generate_anchor(result)
    
    # Should mention profitability gap (P/S > 10 triggers benchmark comparison)
    assert "RIVN" in anchor
    assert "12" in anchor  # P/S ratio
    assert "profitability" in anchor.lower()
    assert "-40" in anchor  # Current Rule of 40

