"""
P/E Compression Calculation Module

Implements the core P/E compression formula:
    compression_pct = ((trailing_pe - forward_pe) / trailing_pe) × 100

- Positive compression = Forward P/E is lower → Market expects earnings to GROW
- Negative compression = Forward P/E is higher → Market expects earnings to DECLINE

Configuration is loaded from config.yaml when available.
"""

import logging
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Optional

import yaml

logger = logging.getLogger(__name__)


# =============================================================================
# Enums and Data Classes
# =============================================================================


class CompressionSignal(Enum):
    """Classification of P/E compression signals."""

    STRONG_BUY = "strong_buy"  # High positive compression (>50%)
    BUY = "buy"  # Moderate positive compression (>20%)
    HOLD = "hold"  # Neutral compression (-20% to +20%)
    SELL = "sell"  # Moderate negative compression (<-20%)
    STRONG_SELL = "strong_sell"  # High negative compression (<-50%)
    DATA_ERROR = "data_error"  # Suspicious data quality


@dataclass
class CompressionResult:
    """Result of P/E compression calculation."""

    ticker: str
    trailing_pe: float
    forward_pe: float
    compression_pct: float
    implied_growth_pct: float
    signal: CompressionSignal
    confidence: str  # "high", "medium", "low"
    warnings: list[str] = field(default_factory=list)

    @property
    def is_buy(self) -> bool:
        """Check if signal indicates buy opportunity."""
        return self.signal in (CompressionSignal.STRONG_BUY, CompressionSignal.BUY)

    @property
    def is_sell(self) -> bool:
        """Check if signal indicates sell opportunity."""
        return self.signal in (CompressionSignal.STRONG_SELL, CompressionSignal.SELL)

    @property
    def is_actionable(self) -> bool:
        """Check if signal warrants action (not hold/error)."""
        return self.signal not in (CompressionSignal.HOLD, CompressionSignal.DATA_ERROR)


# =============================================================================
# Configuration
# =============================================================================


@dataclass
class CompressionConfig:
    """Configuration for compression analysis."""

    compression_signal: float = 20.0  # Minimum % to trigger signal
    high_compression: float = 50.0  # High compression threshold
    extreme_compression: float = 80.0  # Extreme compression threshold
    extreme_growth_threshold: float = 100.0  # Growth % that suggests data error


def _load_config() -> CompressionConfig:
    """Load compression configuration from config.yaml."""
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

                thresholds = config_data.get("thresholds", {})
                validation = config_data.get("validation", {})

                return CompressionConfig(
                    compression_signal=thresholds.get("compression_signal", 20.0),
                    high_compression=thresholds.get("high_compression", 50.0),
                    extreme_compression=thresholds.get("extreme_compression", 80.0),
                    extreme_growth_threshold=validation.get("extreme_growth_threshold", 100.0),
                )
            except Exception as e:
                logger.warning(f"Failed to load config from {config_path}: {e}")

    return CompressionConfig()


# Global config (lazy loaded)
_config: Optional[CompressionConfig] = None


def get_config() -> CompressionConfig:
    """Get compression configuration."""
    global _config
    if _config is None:
        _config = _load_config()
    return _config


def reload_config() -> CompressionConfig:
    """Force reload of configuration from disk."""
    global _config
    _config = None
    return get_config()


# =============================================================================
# Core Calculations
# =============================================================================


def calculate_compression(
    trailing_pe: float,
    forward_pe: float,
    trailing_eps: Optional[float] = None,
    forward_eps: Optional[float] = None,
) -> tuple[float, float]:
    """
    Calculate P/E compression percentage and implied earnings growth.

    Formula: compression_pct = ((trailing_pe - forward_pe) / trailing_pe) × 100

    Interpretation:
    - Positive compression: Forward P/E lower → Market expects earnings GROWTH
    - Negative compression: Forward P/E higher → Market expects earnings DECLINE

    Args:
        trailing_pe: Trailing P/E ratio (TTM)
        forward_pe: Forward P/E ratio (FY1 estimate)
        trailing_eps: Optional trailing EPS for growth calculation
        forward_eps: Optional forward EPS for growth calculation

    Returns:
        Tuple of (compression_pct, implied_growth_pct)

    Raises:
        ValueError: If trailing_pe is zero or negative

    Example:
        >>> calculate_compression(73.27, 156.58)
        (-113.70, 0.0)  # HOOD example - negative compression = earnings collapse

        >>> calculate_compression(73.27, 156.58, 1.56, 0.73)
        (-113.70, -53.2)  # With EPS: -53% growth expected
    """
    # Validate inputs
    if trailing_pe is None or trailing_pe <= 0:
        raise ValueError(f"Trailing P/E must be positive, got: {trailing_pe}")
    if forward_pe is None or forward_pe <= 0:
        raise ValueError(f"Forward P/E must be positive, got: {forward_pe}")

    # Calculate compression percentage
    compression_pct = ((trailing_pe - forward_pe) / trailing_pe) * 100

    # Calculate implied growth if EPS values provided
    implied_growth_pct = 0.0
    if trailing_eps is not None and forward_eps is not None and trailing_eps != 0:
        implied_growth_pct = ((forward_eps - trailing_eps) / abs(trailing_eps)) * 100

    return round(compression_pct, 2), round(implied_growth_pct, 2)


def interpret_signal(
    compression_pct: float,
    data_quality_flags: Optional[list[str]] = None,
    thresholds: Optional[dict[str, float]] = None,
) -> tuple[CompressionSignal, str]:
    """
    Interpret compression percentage into actionable signal.

    Signal Logic:
    - STRONG_BUY: compression > high_compression (default: >50%)
    - BUY: compression > compression_signal (default: >20%)
    - HOLD: -compression_signal <= compression <= compression_signal
    - SELL: compression < -compression_signal (default: <-20%)
    - STRONG_SELL: compression < -high_compression (default: <-50%)
    - DATA_ERROR: If data quality flags present

    Args:
        compression_pct: Calculated compression percentage
        data_quality_flags: List of data quality warnings
        thresholds: Custom thresholds dict with keys:
            - "compression_signal": Minimum % to trigger (default: 20)
            - "high_compression": High compression threshold (default: 50)
            - "extreme_compression": Extreme threshold (default: 80)

    Returns:
        Tuple of (signal, confidence)
        - confidence: "high", "medium", "low"

    Example:
        >>> interpret_signal(-113.70)
        (CompressionSignal.STRONG_SELL, "high")

        >>> interpret_signal(70.69)
        (CompressionSignal.STRONG_BUY, "high")
    """
    # Check for data quality issues first
    if data_quality_flags and len(data_quality_flags) > 0:
        # Severe data quality issues
        severe_flags = [f for f in data_quality_flags if "error" in f.lower() or "split" in f.lower()]
        if severe_flags:
            return CompressionSignal.DATA_ERROR, "low"

    # Get thresholds from config or use provided/defaults
    config = get_config()
    if thresholds:
        signal_threshold = thresholds.get("compression_signal", config.compression_signal)
        high_threshold = thresholds.get("high_compression", config.high_compression)
    else:
        signal_threshold = config.compression_signal
        high_threshold = config.high_compression

    # Determine signal based on compression direction and magnitude
    abs_compression = abs(compression_pct)

    # Determine confidence based on magnitude
    if abs_compression >= high_threshold:
        confidence = "high"
    elif abs_compression >= signal_threshold:
        confidence = "medium"
    else:
        confidence = "low"

    # Adjust confidence down if there are data quality warnings
    if data_quality_flags and len(data_quality_flags) > 0:
        confidence = "low" if confidence == "medium" else confidence
        confidence = "medium" if confidence == "high" else confidence

    # Determine signal
    if compression_pct > high_threshold:
        return CompressionSignal.STRONG_BUY, confidence
    elif compression_pct > signal_threshold:
        return CompressionSignal.BUY, confidence
    elif compression_pct < -high_threshold:
        return CompressionSignal.STRONG_SELL, confidence
    elif compression_pct < -signal_threshold:
        return CompressionSignal.SELL, confidence
    else:
        return CompressionSignal.HOLD, confidence


def analyze_compression(
    ticker: str,
    trailing_pe: float,
    forward_pe: float,
    trailing_eps: Optional[float] = None,
    forward_eps: Optional[float] = None,
    data_quality_flags: Optional[list[str]] = None,
) -> CompressionResult:
    """
    Perform complete P/E compression analysis for a single ticker.

    Args:
        ticker: Stock ticker symbol
        trailing_pe: Trailing P/E ratio (TTM)
        forward_pe: Forward P/E ratio (FY1 estimate)
        trailing_eps: Optional trailing EPS
        forward_eps: Optional forward EPS
        data_quality_flags: List of data quality warnings

    Returns:
        CompressionResult with all analysis fields populated

    Example:
        >>> result = analyze_compression("HOOD", 73.27, 156.58, 1.56, 0.73)
        >>> print(f"{result.ticker}: {result.signal.value} ({result.compression_pct}%)")
        HOOD: strong_sell (-113.70%)
    """
    warnings: list[str] = list(data_quality_flags) if data_quality_flags else []
    config = get_config()

    # Validate inputs and handle edge cases
    if trailing_pe is None or trailing_pe <= 0:
        return CompressionResult(
            ticker=ticker,
            trailing_pe=trailing_pe or 0,
            forward_pe=forward_pe or 0,
            compression_pct=0.0,
            implied_growth_pct=0.0,
            signal=CompressionSignal.DATA_ERROR,
            confidence="low",
            warnings=["Invalid trailing P/E (zero or negative)"],
        )

    if forward_pe is None or forward_pe <= 0:
        return CompressionResult(
            ticker=ticker,
            trailing_pe=trailing_pe,
            forward_pe=forward_pe or 0,
            compression_pct=0.0,
            implied_growth_pct=0.0,
            signal=CompressionSignal.DATA_ERROR,
            confidence="low",
            warnings=["Invalid forward P/E (zero or negative)"],
        )

    # Calculate compression and implied growth
    compression_pct, implied_growth_pct = calculate_compression(
        trailing_pe=trailing_pe,
        forward_pe=forward_pe,
        trailing_eps=trailing_eps,
        forward_eps=forward_eps,
    )

    # Check for suspicious growth rates (potential data error)
    if abs(implied_growth_pct) > config.extreme_growth_threshold:
        warnings.append(
            f"Extreme implied growth ({implied_growth_pct:+.1f}%) may indicate data error"
        )

    # Check for extreme compression (potential data error)
    if abs(compression_pct) > config.extreme_compression:
        warnings.append(
            f"Extreme compression ({compression_pct:+.1f}%) requires verification"
        )

    # Interpret signal
    signal, confidence = interpret_signal(
        compression_pct=compression_pct,
        data_quality_flags=warnings if warnings else None,
    )

    return CompressionResult(
        ticker=ticker,
        trailing_pe=trailing_pe,
        forward_pe=forward_pe,
        compression_pct=compression_pct,
        implied_growth_pct=implied_growth_pct,
        signal=signal,
        confidence=confidence,
        warnings=warnings,
    )


# =============================================================================
# Batch Analysis
# =============================================================================


def analyze_batch(
    data: list[dict],
    ticker_key: str = "ticker",
    trailing_pe_key: str = "trailing_pe",
    forward_pe_key: str = "forward_pe",
    trailing_eps_key: str = "trailing_eps",
    forward_eps_key: str = "forward_eps",
) -> list[CompressionResult]:
    """
    Analyze compression for multiple tickers.

    Args:
        data: List of dicts containing ticker and P/E data
        ticker_key: Key for ticker in dict
        trailing_pe_key: Key for trailing P/E
        forward_pe_key: Key for forward P/E
        trailing_eps_key: Key for trailing EPS
        forward_eps_key: Key for forward EPS

    Returns:
        List of CompressionResult objects

    Example:
        >>> data = [
        ...     {"ticker": "HOOD", "trailing_pe": 73.27, "forward_pe": 156.58},
        ...     {"ticker": "ORA.PA", "trailing_pe": 40.81, "forward_pe": 11.96},
        ... ]
        >>> results = analyze_batch(data)
    """
    results = []

    for item in data:
        ticker = item.get(ticker_key, "UNKNOWN")
        trailing_pe = item.get(trailing_pe_key)
        forward_pe = item.get(forward_pe_key)
        trailing_eps = item.get(trailing_eps_key)
        forward_eps = item.get(forward_eps_key)

        try:
            result = analyze_compression(
                ticker=ticker,
                trailing_pe=trailing_pe,
                forward_pe=forward_pe,
                trailing_eps=trailing_eps,
                forward_eps=forward_eps,
            )
            results.append(result)
        except Exception as e:
            logger.error(f"Failed to analyze {ticker}: {e}")
            results.append(CompressionResult(
                ticker=ticker,
                trailing_pe=trailing_pe or 0,
                forward_pe=forward_pe or 0,
                compression_pct=0.0,
                implied_growth_pct=0.0,
                signal=CompressionSignal.DATA_ERROR,
                confidence="low",
                warnings=[f"Analysis failed: {str(e)}"],
            ))

    return results


def rank_by_compression(
    results: list[CompressionResult],
    ascending: bool = False,
) -> list[CompressionResult]:
    """
    Rank compression results by compression percentage.

    Args:
        results: List of CompressionResult objects
        ascending: If True, lowest compression first (sells at top)
                   If False, highest compression first (buys at top)

    Returns:
        Sorted list of CompressionResult objects
    """
    return sorted(results, key=lambda r: r.compression_pct, reverse=not ascending)
