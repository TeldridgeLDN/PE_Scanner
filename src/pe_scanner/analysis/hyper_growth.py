"""
Hyper-Growth Mode Analysis Module (Price/Sales + Rule of 40)

Implements analysis for hyper-growth or loss-making stocks using:
1. Price/Sales (P/S) Ratio: Market Cap ÷ Revenue
2. Rule of 40: Revenue Growth (%) + Profit Margin (%)

Signal Logic:
- BUY: P/S < 5 AND Rule of 40 >= 40 (attractive valuation + strong fundamentals)
- SELL: P/S > 15 OR Rule of 40 < 20 (expensive OR weak fundamentals)
- HOLD: Otherwise (fairly valued)

Example:
    - P/S = 3.5, Rule of 40 = 45 → BUY (cheap + strong)
    - P/S = 20, Rule of 40 = 50 → SELL (too expensive despite strong metrics)
    - P/S = 8, Rule of 40 = 15 → SELL (weak fundamentals)
"""

import logging
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional

logger = logging.getLogger(__name__)


# =============================================================================
# Enums
# =============================================================================


class HyperGrowthSignal(Enum):
    """Signal classifications for hyper-growth stock analysis."""

    BUY = "buy"  # P/S < 5 AND Rule of 40 >= 40
    SELL = "sell"  # P/S > 15 OR Rule of 40 < 20
    HOLD = "hold"  # Otherwise
    DATA_ERROR = "data_error"  # Missing or invalid data


# =============================================================================
# Data Classes
# =============================================================================


@dataclass
class HyperGrowthAnalysisResult:
    """Result from Price/Sales + Rule of 40 analysis (hyper-growth stocks)."""

    ticker: str
    analysis_mode: str = "HYPER_GROWTH (Price/Sales)"
    price_to_sales: float = 0.0
    revenue_growth_pct: float = 0.0
    profit_margin_pct: float = 0.0
    rule_of_40_score: float = 0.0
    signal: HyperGrowthSignal = HyperGrowthSignal.DATA_ERROR
    confidence: str = "low"  # "high", "medium", "low"
    explanation: str = ""
    warnings: list[str] = field(default_factory=list)

    @property
    def is_buy(self) -> bool:
        """Check if signal indicates buy opportunity."""
        return self.signal == HyperGrowthSignal.BUY

    @property
    def is_sell(self) -> bool:
        """Check if signal indicates sell opportunity."""
        return self.signal == HyperGrowthSignal.SELL

    @property
    def is_actionable(self) -> bool:
        """Check if signal warrants action (not hold/error)."""
        return self.signal in (HyperGrowthSignal.BUY, HyperGrowthSignal.SELL)


# =============================================================================
# Metric Calculations
# =============================================================================


def calculate_price_to_sales(market_cap: float, revenue: float) -> float:
    """
    Calculate Price/Sales (P/S) ratio.

    Formula: P/S = Market Cap ÷ Revenue

    Args:
        market_cap: Company's market capitalization
        revenue: Annual revenue (TTM or forward)

    Returns:
        P/S ratio rounded to 2 decimal places

    Raises:
        ValueError: If revenue is zero or negative

    Examples:
        >>> calculate_price_to_sales(10_000_000_000, 5_000_000_000)
        2.0

        >>> calculate_price_to_sales(50_000_000_000, 10_000_000_000)
        5.0
    """
    if revenue <= 0:
        raise ValueError(f"Revenue must be positive for P/S calculation, got {revenue}")

    ps_ratio = market_cap / revenue
    return round(ps_ratio, 2)


def calculate_rule_of_40(revenue_growth_pct: float, profit_margin_pct: float) -> float:
    """
    Calculate Rule of 40 score.

    Formula: Rule of 40 = Revenue Growth (%) + Profit Margin (%)

    The Rule of 40 is a key SaaS metric suggesting healthy companies should have
    combined growth + profitability >= 40%.

    Args:
        revenue_growth_pct: Revenue growth rate as percentage (e.g., 25.0 for 25%)
        profit_margin_pct: Profit margin as percentage (e.g., 15.0 for 15%)

    Returns:
        Rule of 40 score rounded to 1 decimal place

    Examples:
        >>> calculate_rule_of_40(30.0, 15.0)
        45.0

        >>> calculate_rule_of_40(50.0, -10.0)
        40.0

        >>> calculate_rule_of_40(10.0, 5.0)
        15.0
    """
    score = revenue_growth_pct + profit_margin_pct
    return round(score, 1)


def interpret_hyper_growth_signal(
    price_to_sales: float,
    rule_of_40: float,
) -> tuple[HyperGrowthSignal, str]:
    """
    Interpret P/S ratio and Rule of 40 into actionable signal.

    Signal Logic:
    - BUY: P/S < 5 AND Rule of 40 >= 40 (attractive + strong)
    - SELL: P/S > 15 OR Rule of 40 < 20 (expensive OR weak)
    - HOLD: Otherwise (fairly valued or mixed signals)

    Args:
        price_to_sales: P/S ratio
        rule_of_40: Rule of 40 score

    Returns:
        Tuple of (signal, confidence)

    Examples:
        >>> interpret_hyper_growth_signal(3.5, 45.0)
        (HyperGrowthSignal.BUY, 'high')

        >>> interpret_hyper_growth_signal(20.0, 50.0)
        (HyperGrowthSignal.SELL, 'high')

        >>> interpret_hyper_growth_signal(8.0, 30.0)
        (HyperGrowthSignal.HOLD, 'medium')
    """
    # Strong BUY: Low P/S + Strong Rule of 40
    if price_to_sales < 5 and rule_of_40 >= 40:
        confidence = "high" if (price_to_sales < 3 and rule_of_40 >= 50) else "medium"
        return HyperGrowthSignal.BUY, confidence

    # Strong SELL: Expensive OR Weak fundamentals
    if price_to_sales > 15 or rule_of_40 < 20:
        # High confidence if both conditions are bad
        if price_to_sales > 15 and rule_of_40 < 20:
            confidence = "high"
        # High confidence if extremely expensive (P/S > 20) or very weak (RO40 < 10)
        elif price_to_sales > 20 or rule_of_40 < 10:
            confidence = "high"
        else:
            confidence = "medium"
        return HyperGrowthSignal.SELL, confidence

    # Otherwise HOLD
    return HyperGrowthSignal.HOLD, "medium"


# =============================================================================
# Hyper-Growth Stock Analysis
# =============================================================================


def analyze_hyper_growth_stock(
    ticker: str,
    market_cap: float,
    revenue: float,
    revenue_growth_pct: float,
    profit_margin_pct: float,
) -> HyperGrowthAnalysisResult:
    """
    Perform Price/Sales + Rule of 40 analysis for hyper-growth stocks.

    Args:
        ticker: Stock ticker symbol
        market_cap: Company's market capitalization
        revenue: Annual revenue (TTM or forward)
        revenue_growth_pct: Revenue growth rate as percentage
        profit_margin_pct: Profit margin as percentage

    Returns:
        HyperGrowthAnalysisResult with signal, confidence, and explanation

    Examples:
        >>> result = analyze_hyper_growth_stock("PLTR", 50e9, 2e9, 25.0, 20.0)
        >>> print(f"{result.ticker}: {result.signal.value}")
        PLTR: hold

        >>> result = analyze_hyper_growth_stock("RIVN", 12e9, 1e9, 10.0, -50.0)
        >>> print(f"{result.ticker}: {result.signal.value}")
        RIVN: sell
    """
    warnings = []

    # Validate market cap
    if market_cap is None or market_cap <= 0:
        return HyperGrowthAnalysisResult(
            ticker=ticker,
            signal=HyperGrowthSignal.DATA_ERROR,
            confidence="low",
            explanation="Invalid market cap (missing or non-positive)",
            warnings=["Invalid market cap data"],
        )

    # Validate revenue
    if revenue is None or revenue <= 0:
        return HyperGrowthAnalysisResult(
            ticker=ticker,
            signal=HyperGrowthSignal.DATA_ERROR,
            confidence="low",
            explanation="Missing or invalid revenue data",
            warnings=["No revenue data available for P/S calculation"],
        )

    # Handle missing growth/margin data
    if revenue_growth_pct is None:
        warnings.append("Missing revenue growth data")
        revenue_growth_pct = 0.0

    if profit_margin_pct is None:
        warnings.append("Missing profit margin data")
        profit_margin_pct = 0.0

    # Calculate P/S ratio
    try:
        price_to_sales = calculate_price_to_sales(market_cap, revenue)
    except ValueError as e:
        return HyperGrowthAnalysisResult(
            ticker=ticker,
            signal=HyperGrowthSignal.DATA_ERROR,
            confidence="low",
            explanation=str(e),
            warnings=[str(e)],
        )

    # Calculate Rule of 40
    rule_of_40 = calculate_rule_of_40(revenue_growth_pct, profit_margin_pct)

    # Check for extreme values
    if price_to_sales > 30:
        warnings.append(f"Extreme P/S ratio ({price_to_sales:.1f}x) - verify data accuracy")

    if rule_of_40 < 0:
        warnings.append(
            f"Negative Rule of 40 ({rule_of_40:.0f}) - severe losses with declining revenue"
        )

    if revenue_growth_pct < 0:
        warnings.append(
            f"Revenue declining ({revenue_growth_pct:+.1f}%) - company may be in trouble"
        )

    if profit_margin_pct < -50:
        warnings.append(
            f"Severe losses (margin: {profit_margin_pct:.1f}%) - path to profitability unclear"
        )

    # Interpret signal
    signal, confidence = interpret_hyper_growth_signal(price_to_sales, rule_of_40)

    # Generate explanation
    explanation = f"At {price_to_sales:.1f}x sales with Rule of 40 score of {rule_of_40:.0f}"

    if signal == HyperGrowthSignal.BUY:
        explanation += " - attractive valuation for strong fundamentals"
    elif signal == HyperGrowthSignal.SELL:
        if price_to_sales > 15 and rule_of_40 < 20:
            explanation += " - expensive with weak fundamentals"
        elif price_to_sales > 15:
            explanation += " - valuation too high despite strong metrics"
        else:
            explanation += " - fundamentals too weak to justify price"
    else:
        explanation += " - fairly valued with mixed signals"

    # Adjust confidence if there are warnings
    if len(warnings) > 1:
        confidence = "low" if confidence == "high" else "medium"

    return HyperGrowthAnalysisResult(
        ticker=ticker,
        price_to_sales=price_to_sales,
        revenue_growth_pct=revenue_growth_pct,
        profit_margin_pct=profit_margin_pct,
        rule_of_40_score=rule_of_40,
        signal=signal,
        confidence=confidence,
        explanation=explanation,
        warnings=warnings,
    )


def analyze_hyper_growth_batch(
    data: list[dict],
    ticker_key: str = "ticker",
    market_cap_key: str = "market_cap",
    revenue_key: str = "revenue",
    revenue_growth_key: str = "revenue_growth_pct",
    profit_margin_key: str = "profit_margin_pct",
) -> list[HyperGrowthAnalysisResult]:
    """
    Analyze multiple hyper-growth stocks.

    Args:
        data: List of dicts containing ticker and financial data
        ticker_key: Key for ticker in dict
        market_cap_key: Key for market cap
        revenue_key: Key for revenue
        revenue_growth_key: Key for revenue growth percentage
        profit_margin_key: Key for profit margin percentage

    Returns:
        List of HyperGrowthAnalysisResult objects

    Example:
        >>> data = [
        ...     {"ticker": "PLTR", "market_cap": 50e9, "revenue": 2e9,
        ...      "revenue_growth_pct": 25.0, "profit_margin_pct": 20.0},
        ...     {"ticker": "RIVN", "market_cap": 12e9, "revenue": 1e9,
        ...      "revenue_growth_pct": 10.0, "profit_margin_pct": -50.0},
        ... ]
        >>> results = analyze_hyper_growth_batch(data)
    """
    results = []

    for item in data:
        ticker = item.get(ticker_key, "UNKNOWN")
        market_cap = item.get(market_cap_key)
        revenue = item.get(revenue_key)
        revenue_growth = item.get(revenue_growth_key)
        profit_margin = item.get(profit_margin_key)

        try:
            result = analyze_hyper_growth_stock(
                ticker=ticker,
                market_cap=market_cap,
                revenue=revenue,
                revenue_growth_pct=revenue_growth,
                profit_margin_pct=profit_margin,
            )
            results.append(result)
        except Exception as e:
            logger.error(f"Failed to analyze {ticker}: {e}")
            results.append(
                HyperGrowthAnalysisResult(
                    ticker=ticker,
                    signal=HyperGrowthSignal.DATA_ERROR,
                    confidence="low",
                    explanation=f"Analysis failed: {str(e)}",
                    warnings=[str(e)],
                )
            )

    return results


def rank_by_rule_of_40(
    results: list[HyperGrowthAnalysisResult],
    ascending: bool = False,
) -> list[HyperGrowthAnalysisResult]:
    """
    Rank hyper-growth analysis results by Rule of 40 score.

    Args:
        results: List of HyperGrowthAnalysisResult objects
        ascending: If False, highest Rule of 40 first (best at top)
                   If True, lowest Rule of 40 first

    Returns:
        Sorted list of HyperGrowthAnalysisResult objects
    """
    return sorted(results, key=lambda r: r.rule_of_40_score, reverse=not ascending)


def rank_by_price_to_sales(
    results: list[HyperGrowthAnalysisResult],
    ascending: bool = True,
) -> list[HyperGrowthAnalysisResult]:
    """
    Rank hyper-growth analysis results by P/S ratio.

    Args:
        results: List of HyperGrowthAnalysisResult objects
        ascending: If True, lowest P/S first (best values at top)
                   If False, highest P/S first

    Returns:
        Sorted list of HyperGrowthAnalysisResult objects
    """
    return sorted(results, key=lambda r: r.price_to_sales, reverse=not ascending)


