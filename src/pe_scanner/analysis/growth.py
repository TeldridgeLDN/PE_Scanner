"""
Growth Mode Analysis Module (PEG Ratio)

Implements PEG (Price/Earnings to Growth) ratio analysis for growth stocks
with P/E ratios between 25 and 50.

PEG Ratio Formula:
    PEG = Trailing P/E ÷ Earnings Growth Rate (%)

Signal Logic:
- PEG < 1.0: BUY (paying less than 1x for each % of growth)
- PEG > 2.0: SELL (paying more than 2x for each % of growth)
- Otherwise: HOLD (fairly valued)

Example:
    - P/E of 30, growth rate of 40% → PEG = 0.75 → BUY
    - P/E of 30, growth rate of 10% → PEG = 3.0 → SELL
"""

import logging
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional

logger = logging.getLogger(__name__)


# =============================================================================
# Enums
# =============================================================================


class GrowthSignal(Enum):
    """Signal classifications for growth stock analysis."""

    BUY = "buy"  # PEG < 1.0
    SELL = "sell"  # PEG > 2.0
    HOLD = "hold"  # 1.0 <= PEG <= 2.0
    DATA_ERROR = "data_error"  # Missing or invalid data


# =============================================================================
# Data Classes
# =============================================================================


@dataclass
class GrowthAnalysisResult:
    """Result from PEG ratio analysis (growth stocks)."""

    ticker: str
    analysis_mode: str = "GROWTH (PEG)"
    trailing_pe: float = 0.0
    earnings_growth_pct: float = 0.0
    peg_ratio: float = 0.0
    signal: GrowthSignal = GrowthSignal.DATA_ERROR
    confidence: str = "low"  # "high", "medium", "low"
    explanation: str = ""
    warnings: list[str] = field(default_factory=list)

    @property
    def is_buy(self) -> bool:
        """Check if signal indicates buy opportunity."""
        return self.signal == GrowthSignal.BUY

    @property
    def is_sell(self) -> bool:
        """Check if signal indicates sell opportunity."""
        return self.signal == GrowthSignal.SELL

    @property
    def is_actionable(self) -> bool:
        """Check if signal warrants action (not hold/error)."""
        return self.signal in (GrowthSignal.BUY, GrowthSignal.SELL)


# =============================================================================
# PEG Calculation
# =============================================================================


def calculate_peg_ratio(trailing_pe: float, earnings_growth_pct: float) -> float:
    """
    Calculate PEG ratio.

    Formula: PEG = Trailing P/E ÷ Earnings Growth (%)

    Args:
        trailing_pe: Trailing P/E ratio
        earnings_growth_pct: Earnings growth rate as percentage (e.g., 25.0 for 25%)

    Returns:
        PEG ratio rounded to 2 decimal places

    Raises:
        ValueError: If earnings growth is zero or negative

    Examples:
        >>> calculate_peg_ratio(30.0, 40.0)
        0.75

        >>> calculate_peg_ratio(30.0, 10.0)
        3.0

        >>> calculate_peg_ratio(40.0, 20.0)
        2.0
    """
    if earnings_growth_pct <= 0:
        raise ValueError(
            f"Earnings growth must be positive for PEG calculation, got {earnings_growth_pct}%"
        )

    peg = trailing_pe / earnings_growth_pct
    return round(peg, 2)


def interpret_peg_signal(peg_ratio: float) -> tuple[GrowthSignal, str]:
    """
    Interpret PEG ratio into actionable signal.

    Signal Logic:
    - PEG < 1.0: BUY (undervalued relative to growth)
    - PEG > 2.0: SELL (overvalued relative to growth)
    - 1.0 <= PEG <= 2.0: HOLD (fairly valued)

    Args:
        peg_ratio: Calculated PEG ratio

    Returns:
        Tuple of (signal, confidence)
        - confidence: "high" for extreme PEGs, "medium" otherwise

    Examples:
        >>> interpret_peg_signal(0.75)
        (GrowthSignal.BUY, 'high')

        >>> interpret_peg_signal(3.0)
        (GrowthSignal.SELL, 'high')

        >>> interpret_peg_signal(1.5)
        (GrowthSignal.HOLD, 'medium')
    """
    # Determine signal
    if peg_ratio < 1.0:
        signal = GrowthSignal.BUY
        # Very attractive if PEG < 0.5
        confidence = "high" if peg_ratio < 0.5 else "medium"
    elif peg_ratio > 2.0:
        signal = GrowthSignal.SELL
        # Very expensive if PEG > 3.0
        confidence = "high" if peg_ratio > 3.0 else "medium"
    else:
        signal = GrowthSignal.HOLD
        confidence = "medium"

    return signal, confidence


# =============================================================================
# Growth Stock Analysis
# =============================================================================


def analyze_growth_stock(
    ticker: str,
    trailing_pe: float,
    earnings_growth_pct: float,
    forward_pe: Optional[float] = None,
) -> GrowthAnalysisResult:
    """
    Perform PEG ratio analysis for growth stocks (P/E 25-50).

    PEG = Trailing P/E ÷ Earnings Growth Rate (%)

    Args:
        ticker: Stock ticker symbol
        trailing_pe: Trailing P/E ratio (TTM)
        earnings_growth_pct: Earnings growth rate as percentage (e.g., 25.0 for 25%)
        forward_pe: Optional forward P/E for additional context

    Returns:
        GrowthAnalysisResult with signal, confidence, and explanation

    Examples:
        >>> result = analyze_growth_stock("CRM", 35.0, 25.0)
        >>> print(f"{result.ticker}: {result.signal.value} (PEG: {result.peg_ratio})")
        CRM: buy (PEG: 1.4)

        >>> result = analyze_growth_stock("ADBE", 40.0, 10.0)
        >>> print(f"{result.ticker}: {result.signal.value} (PEG: {result.peg_ratio})")
        ADBE: sell (PEG: 4.0)
    """
    warnings = []

    # Validate inputs
    if trailing_pe is None or trailing_pe <= 0:
        return GrowthAnalysisResult(
            ticker=ticker,
            trailing_pe=trailing_pe or 0,
            signal=GrowthSignal.DATA_ERROR,
            confidence="low",
            explanation="Invalid trailing P/E (missing or non-positive)",
            warnings=["Invalid trailing P/E data"],
        )

    if earnings_growth_pct is None:
        return GrowthAnalysisResult(
            ticker=ticker,
            trailing_pe=trailing_pe,
            signal=GrowthSignal.DATA_ERROR,
            confidence="low",
            explanation="Missing earnings growth data",
            warnings=["No earnings growth data available"],
        )

    # Handle zero or negative growth
    if earnings_growth_pct <= 0:
        explanation = (
            f"Negative or zero earnings growth ({earnings_growth_pct:+.1f}%) "
            "- PEG ratio not applicable for shrinking earnings"
        )
        return GrowthAnalysisResult(
            ticker=ticker,
            trailing_pe=trailing_pe,
            earnings_growth_pct=earnings_growth_pct,
            signal=GrowthSignal.DATA_ERROR,
            confidence="low",
            explanation=explanation,
            warnings=["Earnings growth is zero or negative - consider HYPER_GROWTH mode"],
        )

    # Calculate PEG ratio
    try:
        peg_ratio = calculate_peg_ratio(trailing_pe, earnings_growth_pct)
    except ValueError as e:
        return GrowthAnalysisResult(
            ticker=ticker,
            trailing_pe=trailing_pe,
            earnings_growth_pct=earnings_growth_pct,
            signal=GrowthSignal.DATA_ERROR,
            confidence="low",
            explanation=str(e),
            warnings=[str(e)],
        )

    # Check for extreme values
    if peg_ratio > 5.0:
        warnings.append(f"Extreme PEG ratio ({peg_ratio:.2f}) - verify data accuracy")

    if earnings_growth_pct > 100:
        warnings.append(
            f"Very high growth rate ({earnings_growth_pct:.1f}%) - may not be sustainable"
        )

    # Interpret signal
    signal, confidence = interpret_peg_signal(peg_ratio)

    # Generate explanation
    explanation = f"Paying {peg_ratio:.2f}x for each % of growth"

    if signal == GrowthSignal.BUY:
        explanation += f" - growth at {earnings_growth_pct:.0f}%/year justifies P/E of {trailing_pe:.0f}"
    elif signal == GrowthSignal.SELL:
        explanation += f" - {earnings_growth_pct:.0f}% growth doesn't justify P/E of {trailing_pe:.0f}"
    else:
        explanation += " - fairly valued relative to growth rate"

    # Adjust confidence if there are warnings
    if warnings:
        confidence = "low" if confidence == "high" else "medium"

    return GrowthAnalysisResult(
        ticker=ticker,
        trailing_pe=trailing_pe,
        earnings_growth_pct=earnings_growth_pct,
        peg_ratio=peg_ratio,
        signal=signal,
        confidence=confidence,
        explanation=explanation,
        warnings=warnings,
    )


def analyze_growth_batch(
    data: list[dict],
    ticker_key: str = "ticker",
    trailing_pe_key: str = "trailing_pe",
    earnings_growth_key: str = "earnings_growth_pct",
) -> list[GrowthAnalysisResult]:
    """
    Analyze multiple growth stocks using PEG ratio.

    Args:
        data: List of dicts containing ticker and growth data
        ticker_key: Key for ticker in dict
        trailing_pe_key: Key for trailing P/E
        earnings_growth_key: Key for earnings growth percentage

    Returns:
        List of GrowthAnalysisResult objects

    Example:
        >>> data = [
        ...     {"ticker": "CRM", "trailing_pe": 35.0, "earnings_growth_pct": 25.0},
        ...     {"ticker": "ADBE", "trailing_pe": 40.0, "earnings_growth_pct": 15.0},
        ... ]
        >>> results = analyze_growth_batch(data)
    """
    results = []

    for item in data:
        ticker = item.get(ticker_key, "UNKNOWN")
        trailing_pe = item.get(trailing_pe_key)
        earnings_growth = item.get(earnings_growth_key)

        try:
            result = analyze_growth_stock(
                ticker=ticker,
                trailing_pe=trailing_pe,
                earnings_growth_pct=earnings_growth,
            )
            results.append(result)
        except Exception as e:
            logger.error(f"Failed to analyze {ticker}: {e}")
            results.append(
                GrowthAnalysisResult(
                    ticker=ticker,
                    trailing_pe=trailing_pe or 0,
                    signal=GrowthSignal.DATA_ERROR,
                    confidence="low",
                    explanation=f"Analysis failed: {str(e)}",
                    warnings=[str(e)],
                )
            )

    return results


def rank_by_peg(
    results: list[GrowthAnalysisResult],
    ascending: bool = True,
) -> list[GrowthAnalysisResult]:
    """
    Rank growth analysis results by PEG ratio.

    Args:
        results: List of GrowthAnalysisResult objects
        ascending: If True, lowest PEG first (best values at top)
                   If False, highest PEG first

    Returns:
        Sorted list of GrowthAnalysisResult objects
    """
    return sorted(results, key=lambda r: r.peg_ratio, reverse=not ascending)


