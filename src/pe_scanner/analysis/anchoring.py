"""
Anchoring Engine Module

Generates memorable, concrete statements ("What Would Have To Be True") that
make abstract analysis results tangible and easy to remember.

The goal is to transform:
- "-113% compression" → "HOOD would need to grow profits 3.3x"
- "PEG 3.2" → "NVDA needs 40%/year growth for 5 years"
- "P/S 12" → "RIVN needs to become as profitable as Tesla"
"""

import logging
from typing import Optional, Union

from pe_scanner.analysis.compression import CompressionResult
from pe_scanner.analysis.growth import GrowthAnalysisResult
from pe_scanner.analysis.hyper_growth import HyperGrowthAnalysisResult

logger = logging.getLogger(__name__)


# Type alias for any analysis result
AnalysisResult = Union[CompressionResult, GrowthAnalysisResult, HyperGrowthAnalysisResult]


# =============================================================================
# Anchoring Strategies
# =============================================================================


def generate_anchor(
    result: AnalysisResult,
    market_cap: Optional[float] = None,
) -> str:
    """
    Generate memorable anchor statement based on analysis result.
    
    Anchoring Strategies:
    1. VALUE mode (compression < -30%): Profit multiplication requirement
    2. GROWTH mode (P/E > 30): Growth rate requirement for fair value
    3. HYPER_GROWTH mode (P/S > 10): Profitability improvement needed
    4. MEGA-CAP (market cap > $500B): Comparison to Apple's profits
    5. FALLBACK: Generic statement based on signal
    
    Args:
        result: Analysis result (CompressionResult, GrowthAnalysisResult, or HyperGrowthAnalysisResult)
        market_cap: Optional market capitalization for mega-cap comparison
        
    Returns:
        Memorable anchor statement
        
    Examples:
        >>> # VALUE mode with severe negative compression
        >>> result = CompressionResult(ticker="HOOD", compression_pct=-113.7, ...)
        >>> anchor = generate_anchor(result, market_cap=10e9)
        >>> print(anchor)
        "Market expects profits to DROP 70%. To return to fair value, HOOD would need to grow profits 3.3x"
        
        >>> # GROWTH mode with high P/E
        >>> result = GrowthAnalysisResult(ticker="NVDA", trailing_pe=65, peg_ratio=3.2, ...)
        >>> anchor = generate_anchor(result)
        >>> print(anchor)
        "To justify P/E of 65, NVDA needs 65% annual earnings growth for 5 years. Only 5% of companies achieve this."
    """
    # Dispatch to appropriate anchoring strategy
    if isinstance(result, CompressionResult):
        return _anchor_value_mode(result, market_cap)
    elif isinstance(result, GrowthAnalysisResult):
        return _anchor_growth_mode(result)
    elif isinstance(result, HyperGrowthAnalysisResult):
        return _anchor_hyper_growth_mode(result)
    else:
        # Fallback for unknown result type
        return _anchor_fallback(result.ticker, "hold")


def _anchor_value_mode(
    result: CompressionResult,
    market_cap: Optional[float] = None,
) -> str:
    """
    Generate anchor for VALUE mode (P/E Compression).
    
    Strategy: Profit multiplication requirement for severe negative compression.
    """
    # PRIORITY 1: Check for mega-cap comparison first (if market cap provided and NOT severe negative compression)
    # Only use mega-cap comparison if compression is moderate (not severe sell signal)
    if (
        market_cap
        and market_cap > 500_000_000_000
        and result.forward_pe > 0
        and result.compression_pct > -30  # Not severe negative compression
    ):
        mega_cap_anchor = _anchor_mega_cap(result.ticker, market_cap, result.forward_pe)
        if mega_cap_anchor:
            return mega_cap_anchor
    
    # Profit multiplication anchor for severe negative compression
    if result.compression_pct < -30 and market_cap:
        if result.trailing_pe > 0 and result.forward_pe > 0:
            # Calculate implied profits
            current_profit = market_cap / result.trailing_pe
            implied_profit = market_cap / result.forward_pe
            
            if current_profit > 0 and implied_profit > 0:
                if implied_profit < current_profit:
                    # Profit needs to DECLINE
                    decline_pct = ((current_profit - implied_profit) / current_profit) * 100
                    multiplier = current_profit / implied_profit
                    return (
                        f"Market expects profits to DROP {decline_pct:.0f}%. "
                        f"To return to fair value, {result.ticker} would need to grow profits {multiplier:.1f}x"
                    )
    
    # Fallback for VALUE mode
    signal_word = result.signal.value.replace('_', ' ')
    
    # Friendly message for data errors
    if signal_word.lower() in ('data_error', 'data error'):
        return f"Sorry, we don't have enough financial data for {result.ticker} to provide a meaningful analysis. This often happens with smaller or newer companies."
    
    return f"At current valuation, {result.ticker} is priced for {signal_word} conditions"


def _anchor_growth_mode(result: GrowthAnalysisResult) -> str:
    """
    Generate anchor for GROWTH mode (PEG Ratio).
    
    Strategy: Growth rate requirement for high P/E stocks.
    """
    # Growth requirement anchor for high P/E (> 30)
    if result.trailing_pe > 30:
        # Calculate required growth for PEG of 1.0 (fair value)
        required_growth = result.trailing_pe / 1.0
        years = 5  # Standard timeframe
        return (
            f"To justify P/E of {result.trailing_pe:.0f}, {result.ticker} needs "
            f"{required_growth:.0f}% annual earnings growth for {years} years. "
            "Only 5% of companies achieve this."
        )
    
    # For moderate P/E, focus on current PEG interpretation
    if result.peg_ratio < 1.0:
        return (
            f"{result.ticker} is paying {result.peg_ratio:.2f}x for each % of growth — "
            f"attractive valuation for {result.earnings_growth_pct:.0f}% growth rate"
        )
    elif result.peg_ratio > 2.0:
        return (
            f"{result.ticker} is paying {result.peg_ratio:.1f}x for each % of growth — "
            f"expensive relative to {result.earnings_growth_pct:.0f}% growth rate"
        )
    else:
        return (
            f"{result.ticker} is fairly valued at PEG {result.peg_ratio:.1f} "
            f"with {result.earnings_growth_pct:.0f}% growth"
        )


def _anchor_hyper_growth_mode(result: HyperGrowthAnalysisResult) -> str:
    """
    Generate anchor for HYPER_GROWTH mode (Price/Sales + Growth/Profit).
    
    Strategy: Simple language about what needs to improve.
    """
    growth = result.revenue_growth_pct
    margin = result.profit_margin_pct
    combined = result.rule_of_40_score  # Growth + Profit combined
    
    # PRIORITY 1: For loss-making companies with declining revenue
    if growth < 0 and margin < -20:
        return (
            f"{result.ticker} faces challenges: revenue declining "
            f"{abs(growth):.0f}% while losing {abs(margin):.0f}% on every sale"
        )
    
    # PRIORITY 2: Expensive stocks need better fundamentals
    if result.price_to_sales > 10:
        if combined < 40:
            # Show what needs to improve
            if margin < 0:
                return (
                    f"At {result.price_to_sales:.1f}x sales, {result.ticker} needs to turn its "
                    f"{abs(margin):.0f}% losses into profits to justify this price"
                )
            else:
                needed_growth = 40 - margin
                return (
                    f"At {result.price_to_sales:.1f}x sales, {result.ticker} needs "
                    f"{needed_growth:.0f}% revenue growth (currently {growth:.0f}%) to justify valuation"
                )
        else:
            return (
                f"At {result.price_to_sales:.1f}x sales, {result.ticker} is expensive "
                f"but has strong {growth:.0f}% growth and {margin:.0f}% margins"
            )
    
    # PRIORITY 3: For attractive hyper-growth stocks
    if result.price_to_sales < 5 and combined >= 40:
        return (
            f"{result.ticker} offers good value: only {result.price_to_sales:.1f}x sales "
            f"with {growth:.0f}% growth and {margin:.0f}% profit margins"
        )
    
    # Fallback for HYPER_GROWTH mode
    signal_word = result.signal.value
    
    # Friendly message for data errors
    if signal_word.lower() in ('data_error', 'data error'):
        return f"Sorry, we don't have enough financial data for {result.ticker} to provide a meaningful analysis. This often happens with smaller or newer companies."
    
    return f"At current valuation, {result.ticker} is priced for {signal_word.lower()} conditions"


def _anchor_mega_cap(
    ticker: str,
    market_cap: float,
    forward_pe: float,
) -> Optional[str]:
    """
    Generate mega-cap comparison anchor (market cap > $500B).
    
    Compares implied future profits to Apple's benchmark.
    """
    if market_cap <= 500_000_000_000 or forward_pe <= 0:
        return None
    
    # Calculate implied annual profit
    implied_profit = market_cap / forward_pe
    implied_profit_b = implied_profit / 1_000_000_000
    
    # Benchmark: Apple's ~$100B annual profit
    apple_profit = 100
    
    if implied_profit_b > apple_profit:
        return (
            f"At current price, {ticker} is valued as if it will generate "
            f"${implied_profit_b:.0f}B in annual profit — more than Apple's ${apple_profit}B"
        )
    
    return None


def _anchor_fallback(ticker: str, signal: str) -> str:
    """
    Generate fallback anchor when no specific strategy applies.
    """
    # Friendly message for data errors
    if signal.lower() in ('data_error', 'data error'):
        return f"Sorry, we don't have enough financial data for {ticker} to provide a meaningful analysis. This often happens with smaller or newer companies."
    
    return f"At current valuation, {ticker} is priced for {signal} conditions"


# =============================================================================
# Batch Anchoring
# =============================================================================


def generate_anchors_batch(
    results: list[AnalysisResult],
    market_caps: Optional[dict[str, float]] = None,
) -> dict[str, str]:
    """
    Generate anchors for multiple analysis results.
    
    Args:
        results: List of analysis results
        market_caps: Optional dict mapping tickers to market caps
        
    Returns:
        Dict mapping tickers to anchor statements
        
    Example:
        >>> results = [result1, result2, result3]
        >>> market_caps = {"HOOD": 10e9, "NVDA": 1e12}
        >>> anchors = generate_anchors_batch(results, market_caps)
        >>> print(anchors["HOOD"])
        "Market expects profits to DROP 70%..."
    """
    anchors = {}
    market_caps = market_caps or {}
    
    for result in results:
        try:
            ticker = result.ticker
            market_cap = market_caps.get(ticker)
            anchor = generate_anchor(result, market_cap)
            anchors[ticker] = anchor
        except Exception as e:
            logger.error(f"Failed to generate anchor for {result.ticker}: {e}")
            anchors[result.ticker] = f"Analysis complete for {result.ticker}"
    
    return anchors

