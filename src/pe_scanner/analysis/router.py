"""
Tiered Analysis Router Module

Routes stocks to the appropriate analysis mode based on classification:
- VALUE (P/E < 25): P/E Compression analysis
- GROWTH (P/E 25-50): PEG ratio analysis
- HYPER_GROWTH (P/E > 50 or loss-making): Price/Sales + Rule of 40 analysis

This module provides a unified interface for analyzing any stock type.
"""

import logging
from dataclasses import dataclass
from typing import Optional, Union

from pe_scanner.analysis.classification import StockType, classify_stock_type, get_analysis_mode_name
from pe_scanner.analysis.compression import CompressionResult, analyze_compression
from pe_scanner.analysis.growth import GrowthAnalysisResult, analyze_growth_stock
from pe_scanner.analysis.hyper_growth import HyperGrowthAnalysisResult, analyze_hyper_growth_stock

logger = logging.getLogger(__name__)


# =============================================================================
# Unified Result Type
# =============================================================================

# Type alias for any analysis result
AnalysisResult = Union[CompressionResult, GrowthAnalysisResult, HyperGrowthAnalysisResult]


# =============================================================================
# Stock Data Input
# =============================================================================


@dataclass
class StockData:
    """
    Input data for tiered stock analysis.
    
    Contains all metrics needed for any analysis mode.
    """
    ticker: str
    
    # Core metrics (for classification and VALUE mode)
    trailing_pe: Optional[float] = None
    forward_pe: Optional[float] = None
    trailing_eps: Optional[float] = None
    forward_eps: Optional[float] = None
    
    # GROWTH mode metrics
    earnings_growth_pct: Optional[float] = None
    
    # HYPER_GROWTH mode metrics
    market_cap: Optional[float] = None
    revenue: Optional[float] = None
    revenue_growth_pct: Optional[float] = None
    profit_margin_pct: Optional[float] = None
    
    # Optional data quality flags
    data_quality_flags: Optional[list[str]] = None


# =============================================================================
# Tiered Analysis Router
# =============================================================================


def analyze_stock(stock_data: StockData) -> AnalysisResult:
    """
    Analyze a stock using the appropriate mode based on its characteristics.
    
    This is the main entry point for tiered analysis. It:
    1. Classifies the stock based on trailing P/E
    2. Routes to the appropriate analysis mode
    3. Returns a mode-specific result
    
    Args:
        stock_data: StockData object with all available metrics
        
    Returns:
        Analysis result (CompressionResult, GrowthAnalysisResult, or HyperGrowthAnalysisResult)
        
    Examples:
        >>> # VALUE stock
        >>> data = StockData(ticker="HOOD", trailing_pe=15.0, forward_pe=20.0)
        >>> result = analyze_stock(data)
        >>> print(type(result).__name__)
        CompressionResult
        
        >>> # GROWTH stock
        >>> data = StockData(ticker="CRM", trailing_pe=35.0, earnings_growth_pct=25.0)
        >>> result = analyze_stock(data)
        >>> print(type(result).__name__)
        GrowthAnalysisResult
        
        >>> # HYPER_GROWTH stock
        >>> data = StockData(ticker="PLTR", trailing_pe=85.0, market_cap=50e9, 
        ...                   revenue=2e9, revenue_growth_pct=25.0, profit_margin_pct=20.0)
        >>> result = analyze_stock(data)
        >>> print(type(result).__name__)
        HyperGrowthAnalysisResult
    """
    # Classify stock type
    stock_type = classify_stock_type(stock_data.trailing_pe)
    mode_name = get_analysis_mode_name(stock_type)
    
    logger.info(f"Analyzing {stock_data.ticker} as {mode_name}")
    
    # Route to appropriate analysis mode
    if stock_type == StockType.VALUE:
        return _analyze_value_mode(stock_data)
    elif stock_type == StockType.GROWTH:
        return _analyze_growth_mode(stock_data)
    else:  # HYPER_GROWTH
        return _analyze_hyper_growth_mode(stock_data)


def _analyze_value_mode(stock_data: StockData) -> CompressionResult:
    """
    Analyze stock using VALUE mode (P/E Compression).
    
    Args:
        stock_data: Stock data with P/E metrics
        
    Returns:
        CompressionResult with compression analysis
    """
    result = analyze_compression(
        ticker=stock_data.ticker,
        trailing_pe=stock_data.trailing_pe,
        forward_pe=stock_data.forward_pe,
        trailing_eps=stock_data.trailing_eps,
        forward_eps=stock_data.forward_eps,
        data_quality_flags=stock_data.data_quality_flags,
    )
    
    logger.debug(
        f"{stock_data.ticker} VALUE analysis: {result.compression_pct:+.1f}% compression → {result.signal.value}"
    )
    
    return result


def _analyze_growth_mode(stock_data: StockData) -> GrowthAnalysisResult:
    """
    Analyze stock using GROWTH mode (PEG Ratio).
    
    Args:
        stock_data: Stock data with P/E and growth metrics
        
    Returns:
        GrowthAnalysisResult with PEG analysis
    """
    result = analyze_growth_stock(
        ticker=stock_data.ticker,
        trailing_pe=stock_data.trailing_pe,
        earnings_growth_pct=stock_data.earnings_growth_pct,
        forward_pe=stock_data.forward_pe,
    )
    
    logger.debug(
        f"{stock_data.ticker} GROWTH analysis: PEG {result.peg_ratio:.2f} → {result.signal.value}"
    )
    
    return result


def _analyze_hyper_growth_mode(stock_data: StockData) -> HyperGrowthAnalysisResult:
    """
    Analyze stock using HYPER_GROWTH mode (Price/Sales + Rule of 40).
    
    Args:
        stock_data: Stock data with market cap, revenue, and growth metrics
        
    Returns:
        HyperGrowthAnalysisResult with P/S and Rule of 40 analysis
    """
    result = analyze_hyper_growth_stock(
        ticker=stock_data.ticker,
        market_cap=stock_data.market_cap,
        revenue=stock_data.revenue,
        revenue_growth_pct=stock_data.revenue_growth_pct,
        profit_margin_pct=stock_data.profit_margin_pct,
    )
    
    logger.debug(
        f"{stock_data.ticker} HYPER_GROWTH analysis: P/S {result.price_to_sales:.1f}, "
        f"RO40 {result.rule_of_40_score:.0f} → {result.signal.value}"
    )
    
    return result


# =============================================================================
# Batch Analysis
# =============================================================================


def analyze_batch(stock_data_list: list[StockData]) -> list[AnalysisResult]:
    """
    Analyze multiple stocks using tiered analysis.
    
    Each stock is automatically routed to the appropriate analysis mode
    based on its characteristics.
    
    Args:
        stock_data_list: List of StockData objects
        
    Returns:
        List of analysis results (mixed types based on stock classification)
        
    Example:
        >>> stocks = [
        ...     StockData(ticker="HOOD", trailing_pe=15.0, forward_pe=20.0),
        ...     StockData(ticker="CRM", trailing_pe=35.0, earnings_growth_pct=25.0),
        ...     StockData(ticker="PLTR", trailing_pe=85.0, market_cap=50e9, revenue=2e9,
        ...               revenue_growth_pct=25.0, profit_margin_pct=20.0),
        ... ]
        >>> results = analyze_batch(stocks)
        >>> len(results)
        3
    """
    results = []
    
    for stock_data in stock_data_list:
        try:
            result = analyze_stock(stock_data)
            results.append(result)
        except Exception as e:
            logger.error(f"Failed to analyze {stock_data.ticker}: {e}")
            # Create a generic error result based on stock type
            stock_type = classify_stock_type(stock_data.trailing_pe)
            
            if stock_type == StockType.VALUE:
                from pe_scanner.analysis.compression import CompressionSignal
                error_result = CompressionResult(
                    ticker=stock_data.ticker,
                    trailing_pe=stock_data.trailing_pe or 0,
                    forward_pe=stock_data.forward_pe or 0,
                    compression_pct=0.0,
                    implied_growth_pct=0.0,
                    signal=CompressionSignal.DATA_ERROR,
                    confidence="low",
                    warnings=[f"Analysis failed: {str(e)}"],
                )
            elif stock_type == StockType.GROWTH:
                from pe_scanner.analysis.growth import GrowthSignal
                error_result = GrowthAnalysisResult(
                    ticker=stock_data.ticker,
                    signal=GrowthSignal.DATA_ERROR,
                    confidence="low",
                    explanation=f"Analysis failed: {str(e)}",
                    warnings=[str(e)],
                )
            else:  # HYPER_GROWTH
                from pe_scanner.analysis.hyper_growth import HyperGrowthSignal
                error_result = HyperGrowthAnalysisResult(
                    ticker=stock_data.ticker,
                    signal=HyperGrowthSignal.DATA_ERROR,
                    confidence="low",
                    explanation=f"Analysis failed: {str(e)}",
                    warnings=[str(e)],
                )
            
            results.append(error_result)
    
    return results


# =============================================================================
# Helper Functions
# =============================================================================


def get_stock_type(trailing_pe: Optional[float]) -> StockType:
    """
    Convenience function to get stock type without full analysis.
    
    Args:
        trailing_pe: Trailing P/E ratio
        
    Returns:
        StockType enum
    """
    return classify_stock_type(trailing_pe)


def get_mode_name(trailing_pe: Optional[float]) -> str:
    """
    Convenience function to get analysis mode name without full analysis.
    
    Args:
        trailing_pe: Trailing P/E ratio
        
    Returns:
        Human-readable mode name
    """
    stock_type = classify_stock_type(trailing_pe)
    return get_analysis_mode_name(stock_type)


