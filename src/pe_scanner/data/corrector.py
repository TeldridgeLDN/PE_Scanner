"""
Data Correction Module

Implements automatic corrections for known data quality issues:
- UK stock pence-to-pounds conversion (100x correction)
- Stock split detection and flagging
- Cross-validation against multiple data points

Configuration is loaded from config.yaml when available.
"""

import copy
import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import TYPE_CHECKING, Optional

import yaml

if TYPE_CHECKING:
    from pe_scanner.data.fetcher import MarketData

logger = logging.getLogger(__name__)


# =============================================================================
# Data Classes
# =============================================================================


@dataclass
class CorrectionResult:
    """Result of data correction operations."""

    ticker: str
    original_forward_pe: Optional[float] = None
    corrected_forward_pe: Optional[float] = None
    original_forward_eps: Optional[float] = None
    corrected_forward_eps: Optional[float] = None
    corrections_applied: list[str] = field(default_factory=list)
    flags_raised: list[str] = field(default_factory=list)
    correction_factor: float = 1.0
    is_uk_stock: bool = False
    potential_stock_split: bool = False

    @property
    def was_corrected(self) -> bool:
        """Check if any corrections were applied."""
        return len(self.corrections_applied) > 0

    @property
    def has_warnings(self) -> bool:
        """Check if any flags were raised."""
        return len(self.flags_raised) > 0


# =============================================================================
# Configuration
# =============================================================================


@dataclass
class CorrectorConfig:
    """Configuration for data correction."""

    uk_stock_correction: bool = True
    stock_split_detection: bool = True
    extreme_growth_threshold: float = 100.0  # % growth that triggers flag
    uk_correction_threshold: float = 1.0  # Forward P/E below this triggers correction
    uk_correction_factor: float = 100.0  # Multiplier for UK pence→pounds


def _load_config() -> CorrectorConfig:
    """Load corrector configuration from config.yaml."""
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

                validation = config_data.get("validation", {})
                return CorrectorConfig(
                    uk_stock_correction=validation.get("uk_stock_correction", True),
                    stock_split_detection=validation.get("stock_split_detection", True),
                    extreme_growth_threshold=validation.get("extreme_growth_threshold", 100.0),
                )
            except Exception as e:
                logger.warning(f"Failed to load config from {config_path}: {e}")

    return CorrectorConfig()


# Global config (lazy loaded)
_config: Optional[CorrectorConfig] = None


def get_config() -> CorrectorConfig:
    """Get corrector configuration."""
    global _config
    if _config is None:
        _config = _load_config()
    return _config


# =============================================================================
# UK Stock Detection and Correction
# =============================================================================


def is_uk_stock(ticker: str) -> bool:
    """
    Check if ticker is a UK stock based on exchange suffix.

    UK stocks on the London Stock Exchange end with '.L'.

    Args:
        ticker: Stock ticker symbol

    Returns:
        True if UK stock (ends with .L), False otherwise

    Example:
        >>> is_uk_stock("BATS.L")
        True
        >>> is_uk_stock("HOOD")
        False
    """
    if not ticker:
        return False
    return ticker.upper().strip().endswith(".L")


def correct_uk_stocks(
    data: "MarketData",
    auto_correct: bool = True,
) -> CorrectionResult:
    """
    Detect and correct UK stock pence/pounds data errors.

    UK stocks on LSE (suffix .L) often have P/E ratios reported
    incorrectly due to price being in pence vs. EPS in pounds.
    If forward P/E < 1.0, apply 100x correction to forward P/E and EPS.

    The issue: Yahoo Finance may report:
    - Price in GBp (pence): e.g., 2996.0 pence = £29.96
    - Forward EPS in pounds: e.g., £2.67
    - This gives forward P/E = 2996 / 267 = 0.112 (WRONG!)
    - Correct forward P/E should be 29.96 / 2.67 = 11.22

    Args:
        data: MarketData object for a UK stock
        auto_correct: Whether to automatically apply correction

    Returns:
        CorrectionResult with original and corrected values

    Example:
        >>> result = correct_uk_stocks(bats_data)
        >>> print(f"Corrected P/E: {result.corrected_forward_pe}")  # 11.22 vs 0.11
    """
    config = get_config()
    ticker = data.ticker

    result = CorrectionResult(
        ticker=ticker,
        original_forward_pe=data.forward_pe,
        corrected_forward_pe=data.forward_pe,
        original_forward_eps=data.forward_eps,
        corrected_forward_eps=data.forward_eps,
        is_uk_stock=is_uk_stock(ticker),
    )

    # Only process UK stocks
    if not result.is_uk_stock:
        return result

    # Check if correction is needed
    if data.forward_pe is None:
        result.flags_raised.append("Missing forward P/E data")
        return result

    # Check if forward P/E indicates pence/pounds issue
    if data.forward_pe < config.uk_correction_threshold:
        correction_factor = config.uk_correction_factor

        if auto_correct and config.uk_stock_correction:
            # Apply 100x correction to forward P/E
            result.corrected_forward_pe = data.forward_pe * correction_factor
            result.correction_factor = correction_factor

            # Also correct forward EPS if available
            if data.forward_eps is not None:
                result.corrected_forward_eps = data.forward_eps * correction_factor

            result.corrections_applied.append(
                f"UK stock pence→pounds: P/E {data.forward_pe:.2f} → {result.corrected_forward_pe:.2f} (×{int(correction_factor)})"
            )

            logger.info(
                f"{ticker}: Applied UK correction - Forward P/E {data.forward_pe:.4f} → {result.corrected_forward_pe:.2f}"
            )
        else:
            # Just flag without correcting
            result.flags_raised.append(
                f"UK stock with forward P/E < {config.uk_correction_threshold}: {data.forward_pe:.4f} (likely pence issue)"
            )

    # Validate correction against trailing P/E
    if result.was_corrected and data.trailing_pe is not None:
        # Check if corrected forward P/E is reasonable relative to trailing
        ratio = result.corrected_forward_pe / data.trailing_pe if data.trailing_pe > 0 else 0
        if ratio > 10 or ratio < 0.1:
            result.flags_raised.append(
                f"Corrected P/E ratio questionable: forward/trailing = {ratio:.2f}"
            )

    return result


# =============================================================================
# Stock Split Detection
# =============================================================================


def calculate_implied_growth(
    trailing_eps: Optional[float],
    forward_eps: Optional[float],
) -> Optional[float]:
    """
    Calculate implied earnings growth rate.

    Args:
        trailing_eps: Trailing EPS (TTM)
        forward_eps: Forward EPS estimate

    Returns:
        Implied growth percentage, or None if calculation not possible

    Example:
        >>> calculate_implied_growth(1.56, 0.73)  # HOOD
        -53.21  # 53.2% earnings decline expected

        >>> calculate_implied_growth(1.0, 5.0)
        400.0  # 400% growth (suspicious!)
    """
    if trailing_eps is None or forward_eps is None:
        return None
    if trailing_eps == 0:
        return None

    return ((forward_eps - trailing_eps) / abs(trailing_eps)) * 100


def detect_stock_splits(
    data: "MarketData",
    growth_threshold: Optional[float] = None,
) -> tuple[bool, Optional[str]]:
    """
    Detect potential stock split data inconsistencies.

    If implied EPS growth exceeds threshold (default 100%), flag as
    potential stock split issue requiring manual verification.

    Common issue: After a stock split, Yahoo Finance may mix:
    - Post-split price (e.g., $114.09 after 10:1 split)
    - Pre-split forward EPS (e.g., $23.78 pre-split instead of $2.378)
    - This gives impossibly low forward P/E and >1000% implied "growth"

    Args:
        data: MarketData object to analyze
        growth_threshold: % growth that triggers split detection (default: from config)

    Returns:
        Tuple of (is_suspicious, warning_message)

    Example:
        >>> is_split, warning = detect_stock_splits(nflx_data)
        >>> if is_split:
        ...     print(f"Manual review needed: {warning}")
    """
    config = get_config()
    threshold = growth_threshold if growth_threshold is not None else config.extreme_growth_threshold

    # Calculate implied growth
    implied_growth = calculate_implied_growth(data.trailing_eps, data.forward_eps)

    if implied_growth is None:
        return False, None

    # Check for extreme positive growth (stock split signature)
    if implied_growth > threshold:
        warning = (
            f"Extreme implied EPS growth: {implied_growth:+.1f}% "
            f"(trailing: {data.trailing_eps}, forward: {data.forward_eps}). "
            f"Possible stock split data error - verify forward EPS is post-split."
        )
        logger.warning(f"{data.ticker}: {warning}")
        return True, warning

    # Check for extreme negative growth (also suspicious)
    if implied_growth < -threshold:
        warning = (
            f"Extreme implied EPS decline: {implied_growth:+.1f}% "
            f"(trailing: {data.trailing_eps}, forward: {data.forward_eps}). "
            f"Verify data accuracy."
        )
        logger.warning(f"{data.ticker}: {warning}")
        return True, warning

    return False, None


# =============================================================================
# Full Correction Pipeline
# =============================================================================


def apply_corrections(
    data: "MarketData",
    config: Optional[dict] = None,
) -> tuple["MarketData", CorrectionResult]:
    """
    Apply all applicable corrections to market data.

    This is the main entry point for the correction pipeline.
    It applies:
    1. UK stock pence→pounds correction
    2. Stock split detection and flagging

    Args:
        data: MarketData object to correct
        config: Optional config dict with correction settings

    Returns:
        Tuple of (corrected_data, correction_result)

    Example:
        >>> corrected, result = apply_corrections(bats_data)
        >>> print(f"Corrections: {result.corrections_applied}")
        >>> print(f"Warnings: {result.flags_raised}")
    """
    # Import here to avoid circular dependency
    from pe_scanner.data.fetcher import MarketData

    # Create a copy of the data to modify
    corrected_data = MarketData(
        ticker=data.ticker,
        current_price=data.current_price,
        trailing_pe=data.trailing_pe,
        forward_pe=data.forward_pe,
        trailing_eps=data.trailing_eps,
        forward_eps=data.forward_eps,
        market_cap=data.market_cap,
        company_name=data.company_name,
        currency=data.currency,
        last_updated=data.last_updated,
        data_source=data.data_source,
        fetch_errors=list(data.fetch_errors),
    )

    # Initialize result
    result = CorrectionResult(
        ticker=data.ticker,
        original_forward_pe=data.forward_pe,
        original_forward_eps=data.forward_eps,
        is_uk_stock=is_uk_stock(data.ticker),
    )

    # Apply UK stock corrections
    if is_uk_stock(data.ticker):
        uk_result = correct_uk_stocks(data)
        if uk_result.was_corrected:
            corrected_data.forward_pe = uk_result.corrected_forward_pe
            corrected_data.forward_eps = uk_result.corrected_forward_eps
            result.corrected_forward_pe = uk_result.corrected_forward_pe
            result.corrected_forward_eps = uk_result.corrected_forward_eps
            result.correction_factor = uk_result.correction_factor
            result.corrections_applied.extend(uk_result.corrections_applied)
        result.flags_raised.extend(uk_result.flags_raised)
    else:
        result.corrected_forward_pe = data.forward_pe
        result.corrected_forward_eps = data.forward_eps

    # Detect stock splits
    is_suspicious, warning = detect_stock_splits(corrected_data)
    if is_suspicious:
        result.potential_stock_split = True
        if warning:
            result.flags_raised.append(warning)

    return corrected_data, result


def apply_corrections_batch(
    data_list: list["MarketData"],
) -> list[tuple["MarketData", CorrectionResult]]:
    """
    Apply corrections to multiple MarketData objects.

    Args:
        data_list: List of MarketData objects to correct

    Returns:
        List of (corrected_data, correction_result) tuples
    """
    results = []
    for data in data_list:
        corrected, result = apply_corrections(data)
        results.append((corrected, result))
    return results
