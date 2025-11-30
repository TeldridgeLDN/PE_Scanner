"""
Fair Value Scenario Calculations

Implements bear and bull case fair value calculations:
    Bear Case: forward_eps × 17.5x P/E (conservative)
    Bull Case: forward_eps × 37.5x P/E (optimistic)

These multiples represent conservative and optimistic valuation scenarios
for comparing against current market prices.

Configuration is loaded from config.yaml when available.
"""

import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

import yaml

logger = logging.getLogger(__name__)


# =============================================================================
# Default Configuration
# =============================================================================

DEFAULT_BEAR_PE = 17.5
DEFAULT_BULL_PE = 37.5


# =============================================================================
# Configuration
# =============================================================================


@dataclass
class FairValueConfig:
    """Configuration for fair value calculations."""

    bear_pe_multiple: float = DEFAULT_BEAR_PE
    bull_pe_multiple: float = DEFAULT_BULL_PE
    base_pe_multiple: float = 25.0  # Mid-point reference


def _load_config() -> FairValueConfig:
    """Load fair value configuration from config.yaml."""
    config_paths = [
        Path.cwd() / "config.yaml",
        Path.cwd().parent / "config.yaml",
        Path(__file__).parent.parent.parent.parent / "config.yaml",
    ]

    for config_path in config_paths:
        if config_path.exists():
            try:
                with open(config_path) as f:
                    config_data = yaml.safe_load(f)

                analysis = config_data.get("analysis", {})
                return FairValueConfig(
                    bear_pe_multiple=analysis.get("bear_pe_multiple", DEFAULT_BEAR_PE),
                    bull_pe_multiple=analysis.get("bull_pe_multiple", DEFAULT_BULL_PE),
                    base_pe_multiple=analysis.get("base_pe_multiple", 25.0),
                )
            except Exception as e:
                logger.warning(f"Failed to load config from {config_path}: {e}")

    return FairValueConfig()


# Global config (lazy loaded)
_config: Optional[FairValueConfig] = None


def get_config() -> FairValueConfig:
    """Get fair value configuration."""
    global _config
    if _config is None:
        _config = _load_config()
    return _config


def reload_config() -> FairValueConfig:
    """Reload configuration from disk."""
    global _config
    _config = _load_config()
    return _config


# =============================================================================
# Data Classes
# =============================================================================


@dataclass
class FairValueResult:
    """Fair value calculation results for a single position."""

    ticker: str
    current_price: float
    forward_eps: float
    bear_fair_value: float
    bear_upside_pct: float
    bull_fair_value: float
    bull_upside_pct: float
    bear_pe_multiple: float = DEFAULT_BEAR_PE
    bull_pe_multiple: float = DEFAULT_BULL_PE
    base_fair_value: Optional[float] = None
    base_upside_pct: Optional[float] = None
    warnings: list[str] = field(default_factory=list)

    @property
    def is_undervalued_bear(self) -> bool:
        """Check if stock is undervalued even in bear case."""
        return self.bear_upside_pct > 0

    @property
    def is_undervalued_bull(self) -> bool:
        """Check if stock is undervalued in bull case."""
        return self.bull_upside_pct > 0

    @property
    def is_overvalued(self) -> bool:
        """Check if stock is overvalued even in bull case."""
        return self.bull_upside_pct < 0

    @property
    def midpoint_upside_pct(self) -> float:
        """Calculate midpoint between bear and bull upside."""
        return (self.bear_upside_pct + self.bull_upside_pct) / 2

    @property
    def upside_range(self) -> float:
        """Calculate the range between bear and bull scenarios."""
        return self.bull_upside_pct - self.bear_upside_pct


# =============================================================================
# Core Calculation Functions
# =============================================================================


def calculate_fair_values(
    forward_eps: float,
    bear_pe: Optional[float] = None,
    bull_pe: Optional[float] = None,
) -> tuple[float, float]:
    """
    Calculate bear and bull case fair values from forward EPS.

    Formula:
        fair_value = forward_eps × P/E_multiple

    Args:
        forward_eps: Forward EPS estimate (FY1)
        bear_pe: Bear case P/E multiple (default: from config or 17.5)
        bull_pe: Bull case P/E multiple (default: from config or 37.5)

    Returns:
        Tuple of (bear_fair_value, bull_fair_value)

    Raises:
        ValueError: If forward_eps is None or negative

    Example:
        >>> calculate_fair_values(0.73)  # HOOD forward EPS
        (12.775, 27.375)

        >>> calculate_fair_values(2.67)  # BATS.L forward EPS
        (46.725, 100.125)
    """
    if forward_eps is None:
        raise ValueError("Forward EPS cannot be None")

    config = get_config()
    bear_pe = bear_pe if bear_pe is not None else config.bear_pe_multiple
    bull_pe = bull_pe if bull_pe is not None else config.bull_pe_multiple

    # Handle negative EPS (loss-making companies)
    if forward_eps < 0:
        logger.warning(f"Negative forward EPS ({forward_eps}) - fair values will be negative")

    bear_fair_value = forward_eps * bear_pe
    bull_fair_value = forward_eps * bull_pe

    return round(bear_fair_value, 2), round(bull_fair_value, 2)


def calculate_upside(
    current_price: float,
    fair_value: float,
) -> float:
    """
    Calculate upside/downside percentage from current price to fair value.

    Formula:
        upside_pct = ((fair_value - current_price) / current_price) × 100

    Args:
        current_price: Current market price
        fair_value: Calculated fair value

    Returns:
        Percentage upside (positive) or downside (negative)

    Raises:
        ValueError: If current_price is zero or negative

    Example:
        >>> calculate_upside(114.30, 12.78)  # HOOD bear case
        -88.82  # 88.82% downside

        >>> calculate_upside(29.96, 46.73)  # BATS.L bear case (corrected price)
        +55.97  # 55.97% upside
    """
    if current_price is None or current_price <= 0:
        raise ValueError(f"Current price must be positive, got: {current_price}")

    upside_pct = ((fair_value - current_price) / current_price) * 100
    return round(upside_pct, 2)


def calculate_base_fair_value(
    forward_eps: float,
    base_pe: Optional[float] = None,
) -> float:
    """
    Calculate a base/midpoint fair value.

    Args:
        forward_eps: Forward EPS estimate
        base_pe: Base P/E multiple (default: from config or 25.0)

    Returns:
        Base fair value
    """
    config = get_config()
    base_pe = base_pe if base_pe is not None else config.base_pe_multiple
    return round(forward_eps * base_pe, 2)


# =============================================================================
# Full Analysis Function
# =============================================================================


def analyze_fair_value(
    ticker: str,
    current_price: float,
    forward_eps: float,
    bear_pe: Optional[float] = None,
    bull_pe: Optional[float] = None,
    include_base: bool = True,
) -> FairValueResult:
    """
    Perform complete fair value analysis for a position.

    Calculates bear and bull case fair values and their respective
    upside/downside percentages relative to current market price.

    Args:
        ticker: Stock ticker symbol
        current_price: Current market price
        forward_eps: Forward EPS estimate (FY1)
        bear_pe: Bear case P/E multiple (default: from config)
        bull_pe: Bull case P/E multiple (default: from config)
        include_base: Whether to include base case calculation

    Returns:
        FairValueResult with all scenario calculations

    Raises:
        ValueError: If required inputs are invalid

    Example:
        >>> result = analyze_fair_value("HOOD", 114.30, 0.73)
        >>> print(f"Bear upside: {result.bear_upside_pct}%")
        Bear upside: -88.82%
        >>> print(f"Bull upside: {result.bull_upside_pct}%")
        Bull upside: -76.05%
    """
    warnings = []

    # Validate inputs
    if current_price is None or current_price <= 0:
        raise ValueError(f"Invalid current price for {ticker}: {current_price}")

    if forward_eps is None:
        raise ValueError(f"Forward EPS is required for {ticker}")

    # Get config
    config = get_config()
    bear_pe = bear_pe if bear_pe is not None else config.bear_pe_multiple
    bull_pe = bull_pe if bull_pe is not None else config.bull_pe_multiple

    # Handle edge cases
    if forward_eps < 0:
        warnings.append(f"Negative forward EPS ({forward_eps}) - company expected to be loss-making")

    if forward_eps == 0:
        warnings.append("Zero forward EPS - fair values will be zero")

    # Calculate fair values
    bear_fair_value, bull_fair_value = calculate_fair_values(forward_eps, bear_pe, bull_pe)

    # Calculate upside percentages
    bear_upside_pct = calculate_upside(current_price, bear_fair_value)
    bull_upside_pct = calculate_upside(current_price, bull_fair_value)

    # Calculate base case if requested
    base_fair_value = None
    base_upside_pct = None
    if include_base:
        base_fair_value = calculate_base_fair_value(forward_eps)
        base_upside_pct = calculate_upside(current_price, base_fair_value)

    # Add warnings for extreme scenarios
    if bear_upside_pct < -90:
        warnings.append(f"Extreme bear case downside ({bear_upside_pct:.1f}%) suggests overvaluation or data error")

    if bull_upside_pct > 200:
        warnings.append(f"Extreme bull case upside ({bull_upside_pct:.1f}%) suggests significant undervaluation")

    result = FairValueResult(
        ticker=ticker,
        current_price=current_price,
        forward_eps=forward_eps,
        bear_fair_value=bear_fair_value,
        bear_upside_pct=bear_upside_pct,
        bull_fair_value=bull_fair_value,
        bull_upside_pct=bull_upside_pct,
        bear_pe_multiple=bear_pe,
        bull_pe_multiple=bull_pe,
        base_fair_value=base_fair_value,
        base_upside_pct=base_upside_pct,
        warnings=warnings,
    )

    logger.debug(
        f"{ticker}: Bear=${bear_fair_value:.2f} ({bear_upside_pct:+.1f}%), "
        f"Bull=${bull_fair_value:.2f} ({bull_upside_pct:+.1f}%)"
    )

    return result


# =============================================================================
# Batch Analysis
# =============================================================================


def analyze_fair_value_batch(
    data: list[dict],
    bear_pe: Optional[float] = None,
    bull_pe: Optional[float] = None,
) -> list[FairValueResult]:
    """
    Perform fair value analysis on multiple positions.

    Args:
        data: List of dicts with keys: ticker, current_price, forward_eps
        bear_pe: Optional bear P/E multiple (default: from config)
        bull_pe: Optional bull P/E multiple (default: from config)

    Returns:
        List of FairValueResult objects

    Example:
        >>> data = [
        ...     {"ticker": "HOOD", "current_price": 114.30, "forward_eps": 0.73},
        ...     {"ticker": "BATS.L", "current_price": 29.96, "forward_eps": 2.67},
        ... ]
        >>> results = analyze_fair_value_batch(data)
    """
    results = []

    for item in data:
        try:
            result = analyze_fair_value(
                ticker=item["ticker"],
                current_price=item["current_price"],
                forward_eps=item["forward_eps"],
                bear_pe=bear_pe,
                bull_pe=bull_pe,
            )
            results.append(result)
        except (ValueError, KeyError) as e:
            logger.warning(f"Skipping {item.get('ticker', 'unknown')}: {e}")
            continue

    return results


def rank_by_upside(
    results: list[FairValueResult],
    use_bear: bool = True,
    ascending: bool = False,
) -> list[FairValueResult]:
    """
    Rank results by upside potential.

    Args:
        results: List of FairValueResult objects
        use_bear: If True, rank by bear case upside; else bull case
        ascending: If True, lowest upside first (most overvalued)

    Returns:
        Sorted list of FairValueResult objects
    """
    key_func = lambda r: r.bear_upside_pct if use_bear else r.bull_upside_pct
    return sorted(results, key=key_func, reverse=not ascending)
