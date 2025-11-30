"""
Data Quality Validation Module

Implements comprehensive data quality checks:
- Extreme downside projections (-95% to -100%)
- Missing forward P/E or EPS data
- Stale analyst estimates (>6 months old)
- Unrealistic growth projections
- Data completeness validation
- Negative P/E handling

Configuration is loaded from config.yaml when available.
"""

import logging
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path
from typing import TYPE_CHECKING, Optional

import yaml

if TYPE_CHECKING:
    from pe_scanner.data.fetcher import MarketData

logger = logging.getLogger(__name__)


# =============================================================================
# Enums and Data Classes
# =============================================================================


class DataQualityLevel(Enum):
    """Data quality classification levels."""

    VERIFIED = "verified"  # All checks passed, high confidence
    ACCEPTABLE = "acceptable"  # Minor warnings only
    SUSPICIOUS = "suspicious"  # Needs manual review
    UNRELIABLE = "unreliable"  # Do not use for investment decisions


class DataQualityFlag(Enum):
    """Specific data quality flags."""

    MISSING_FORWARD_PE = "missing_forward_pe"
    MISSING_TRAILING_PE = "missing_trailing_pe"
    MISSING_FORWARD_EPS = "missing_forward_eps"
    MISSING_TRAILING_EPS = "missing_trailing_eps"
    MISSING_PRICE = "missing_price"
    NEGATIVE_FORWARD_PE = "negative_forward_pe"
    NEGATIVE_TRAILING_PE = "negative_trailing_pe"
    EXTREME_DOWNSIDE = "extreme_downside"
    EXTREME_GROWTH = "extreme_growth"
    STALE_ESTIMATES = "stale_estimates"
    UK_CORRECTION_NEEDED = "uk_correction_needed"
    POTENTIAL_STOCK_SPLIT = "potential_stock_split"
    FETCH_ERROR = "fetch_error"
    ZERO_PE = "zero_pe"


@dataclass
class ValidationResult:
    """Result of data quality validation."""

    ticker: str
    quality_level: DataQualityLevel = DataQualityLevel.VERIFIED
    flags: list[DataQualityFlag] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)
    checks_passed: list[str] = field(default_factory=list)
    requires_manual_review: bool = False
    validation_timestamp: datetime = field(default_factory=datetime.now)
    confidence_score: float = 1.0  # 0.0 to 1.0

    @property
    def is_usable(self) -> bool:
        """Check if data is usable for analysis."""
        return self.quality_level in (DataQualityLevel.VERIFIED, DataQualityLevel.ACCEPTABLE)

    @property
    def has_critical_issues(self) -> bool:
        """Check if data has critical quality issues."""
        return self.quality_level == DataQualityLevel.UNRELIABLE or len(self.errors) > 0

    def add_flag(self, flag: DataQualityFlag, message: str, is_error: bool = False) -> None:
        """Add a quality flag with associated message."""
        if flag not in self.flags:
            self.flags.append(flag)
        if is_error:
            self.errors.append(message)
        else:
            self.warnings.append(message)


# =============================================================================
# Configuration
# =============================================================================


@dataclass
class ValidatorConfig:
    """Configuration for data validation."""

    extreme_downside_threshold: float = -95.0
    extreme_upside_threshold: float = 500.0
    extreme_growth_threshold: float = 100.0
    stale_estimate_days: int = 180
    min_confidence_for_acceptable: float = 0.7
    min_confidence_for_verified: float = 0.9


def _load_config() -> ValidatorConfig:
    """Load validator configuration from config.yaml."""
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
                return ValidatorConfig(
                    extreme_downside_threshold=validation.get("extreme_downside_threshold", -95.0),
                    extreme_growth_threshold=validation.get("extreme_growth_threshold", 100.0),
                    stale_estimate_days=validation.get("stale_estimate_days", 180),
                )
            except Exception as e:
                logger.warning(f"Failed to load config from {config_path}: {e}")

    return ValidatorConfig()


# Global config (lazy loaded)
_config: Optional[ValidatorConfig] = None


def get_config() -> ValidatorConfig:
    """Get validator configuration."""
    global _config
    if _config is None:
        _config = _load_config()
    return _config


# =============================================================================
# Individual Check Functions
# =============================================================================


def check_missing_data(data: "MarketData") -> list[tuple[DataQualityFlag, str]]:
    """
    Check for missing critical data fields.

    Args:
        data: MarketData object to check

    Returns:
        List of (flag, message) tuples for missing fields
    """
    issues = []

    # Critical fields for P/E analysis
    if data.forward_pe is None:
        issues.append(
            (DataQualityFlag.MISSING_FORWARD_PE, "Missing forward P/E ratio")
        )

    if data.trailing_pe is None:
        issues.append(
            (DataQualityFlag.MISSING_TRAILING_PE, "Missing trailing P/E ratio")
        )

    # EPS fields (needed for growth calculation)
    if data.forward_eps is None:
        issues.append(
            (DataQualityFlag.MISSING_FORWARD_EPS, "Missing forward EPS estimate")
        )

    if data.trailing_eps is None:
        issues.append(
            (DataQualityFlag.MISSING_TRAILING_EPS, "Missing trailing EPS")
        )

    # Price is essential
    if data.current_price is None:
        issues.append(
            (DataQualityFlag.MISSING_PRICE, "Missing current stock price")
        )

    return issues


def check_negative_pe(data: "MarketData") -> list[tuple[DataQualityFlag, str]]:
    """
    Check for negative P/E ratios (company not profitable).

    Args:
        data: MarketData object to check

    Returns:
        List of (flag, message) tuples for negative P/E issues
    """
    issues = []

    if data.trailing_pe is not None and data.trailing_pe < 0:
        issues.append(
            (
                DataQualityFlag.NEGATIVE_TRAILING_PE,
                f"Negative trailing P/E ({data.trailing_pe:.2f}) - company currently unprofitable",
            )
        )

    if data.forward_pe is not None and data.forward_pe < 0:
        issues.append(
            (
                DataQualityFlag.NEGATIVE_FORWARD_PE,
                f"Negative forward P/E ({data.forward_pe:.2f}) - expected to be unprofitable",
            )
        )

    # Zero P/E is also problematic
    if data.trailing_pe is not None and data.trailing_pe == 0:
        issues.append(
            (DataQualityFlag.ZERO_PE, "Trailing P/E is zero - invalid data")
        )

    if data.forward_pe is not None and data.forward_pe == 0:
        issues.append(
            (DataQualityFlag.ZERO_PE, "Forward P/E is zero - invalid data")
        )

    return issues


def check_extreme_downside(
    implied_upside_pct: Optional[float],
    threshold: Optional[float] = None,
) -> Optional[tuple[DataQualityFlag, str]]:
    """
    Check for extreme downside projections that suggest data errors.

    Args:
        implied_upside_pct: Implied upside percentage from valuation
        threshold: Threshold below which to flag (default: -95%)

    Returns:
        (flag, message) tuple if extreme, None otherwise

    Example:
        >>> check_extreme_downside(-97.5)
        (DataQualityFlag.EXTREME_DOWNSIDE, "Extreme downside projection (-97.5%)...")
    """
    if implied_upside_pct is None:
        return None

    config = get_config()
    threshold = threshold if threshold is not None else config.extreme_downside_threshold

    if implied_upside_pct < threshold:
        return (
            DataQualityFlag.EXTREME_DOWNSIDE,
            f"Extreme downside projection ({implied_upside_pct:+.1f}%) suggests data error or extreme pessimism",
        )

    return None


def check_extreme_growth(
    trailing_eps: Optional[float],
    forward_eps: Optional[float],
    threshold: Optional[float] = None,
) -> Optional[tuple[DataQualityFlag, str]]:
    """
    Check for unrealistic growth projections.

    Args:
        trailing_eps: Trailing EPS
        forward_eps: Forward EPS estimate
        threshold: Growth % above which to flag (default: 100%)

    Returns:
        (flag, message) tuple if extreme, None otherwise
    """
    if trailing_eps is None or forward_eps is None or trailing_eps == 0:
        return None

    config = get_config()
    threshold = threshold if threshold is not None else config.extreme_growth_threshold

    implied_growth = ((forward_eps - trailing_eps) / abs(trailing_eps)) * 100

    if implied_growth > threshold:
        return (
            DataQualityFlag.EXTREME_GROWTH,
            f"Extreme implied EPS growth ({implied_growth:+.1f}%) - possible stock split or data error",
        )

    if implied_growth < -threshold:
        return (
            DataQualityFlag.EXTREME_GROWTH,
            f"Extreme implied EPS decline ({implied_growth:+.1f}%) - verify analyst estimates",
        )

    return None


def check_stale_estimates(
    data: "MarketData",
    max_age_days: Optional[int] = None,
) -> Optional[tuple[DataQualityFlag, str]]:
    """
    Check if analyst estimates are potentially stale.

    Args:
        data: MarketData object to check
        max_age_days: Maximum age in days before flagging

    Returns:
        (flag, message) tuple if stale, None otherwise

    Note:
        Yahoo Finance doesn't provide estimate timestamps, so this check
        is based on data freshness (last_updated) as a proxy.
    """
    config = get_config()
    max_age = max_age_days if max_age_days is not None else config.stale_estimate_days

    if data.last_updated is None:
        return None

    # Check if data is old
    age = datetime.now() - data.last_updated
    if age > timedelta(days=max_age):
        return (
            DataQualityFlag.STALE_ESTIMATES,
            f"Data is {age.days} days old - estimates may be stale",
        )

    return None


def check_fetch_errors(data: "MarketData") -> list[tuple[DataQualityFlag, str]]:
    """
    Check for fetch errors recorded in the data.

    Args:
        data: MarketData object to check

    Returns:
        List of (flag, message) tuples for fetch errors
    """
    issues = []

    if hasattr(data, "fetch_errors") and data.fetch_errors:
        for error in data.fetch_errors:
            issues.append(
                (DataQualityFlag.FETCH_ERROR, f"Fetch error: {error}")
            )

    return issues


# =============================================================================
# Quick Quality Check
# =============================================================================


def check_data_quality(
    data: "MarketData",
    extreme_downside_threshold: Optional[float] = None,
    stale_estimate_days: Optional[int] = None,
    extreme_growth_threshold: Optional[float] = None,
) -> list[str]:
    """
    Quick check for common data quality issues.

    Args:
        data: MarketData object to check
        extreme_downside_threshold: % threshold for extreme downside warning
        stale_estimate_days: Days after which estimates are considered stale
        extreme_growth_threshold: % threshold for unrealistic growth

    Returns:
        List of warning messages (empty if no issues)

    Example:
        >>> warnings = check_data_quality(market_data)
        >>> if warnings:
        ...     print(f"Warnings: {warnings}")
    """
    warnings = []

    # Check missing data
    missing = check_missing_data(data)
    for _, msg in missing:
        warnings.append(msg)

    # Check negative P/E
    negative = check_negative_pe(data)
    for _, msg in negative:
        warnings.append(msg)

    # Check extreme growth
    growth_issue = check_extreme_growth(
        data.trailing_eps, data.forward_eps, extreme_growth_threshold
    )
    if growth_issue:
        warnings.append(growth_issue[1])

    # Check stale estimates
    stale = check_stale_estimates(data, stale_estimate_days)
    if stale:
        warnings.append(stale[1])

    # Check fetch errors
    fetch_issues = check_fetch_errors(data)
    for _, msg in fetch_issues:
        warnings.append(msg)

    return warnings


# =============================================================================
# Main Validation Function
# =============================================================================


def validate_market_data(
    data: "MarketData",
    config: Optional[dict] = None,
) -> ValidationResult:
    """
    Validate market data quality with comprehensive checks.

    Performs the following validations:
    1. Missing data checks (forward P/E, trailing P/E, EPS, price)
    2. Negative P/E checks (unprofitable companies)
    3. Extreme growth projections (>100% implied growth)
    4. Stale estimate detection (>6 months)
    5. Fetch error aggregation

    Args:
        data: MarketData object to validate
        config: Optional validation config with thresholds

    Returns:
        ValidationResult with quality level, flags, and messages

    Example:
        >>> result = validate_market_data(market_data)
        >>> if result.quality_level == DataQualityLevel.UNRELIABLE:
        ...     print(f"Skip {result.ticker}: {result.errors}")
        >>> if result.is_usable:
        ...     # Safe to use for analysis
        ...     analyze(market_data)
    """
    result = ValidationResult(ticker=data.ticker)
    confidence_penalties = []

    # 1. Check for fetch errors (most critical)
    fetch_issues = check_fetch_errors(data)
    for flag, msg in fetch_issues:
        result.add_flag(flag, msg, is_error=True)
        confidence_penalties.append(0.3)

    # 2. Check missing data
    missing_issues = check_missing_data(data)
    for flag, msg in missing_issues:
        # Missing forward P/E is critical for P/E compression
        is_critical = flag in (DataQualityFlag.MISSING_FORWARD_PE, DataQualityFlag.MISSING_TRAILING_PE)
        result.add_flag(flag, msg, is_error=is_critical)
        confidence_penalties.append(0.2 if is_critical else 0.1)

    if not any(f in result.flags for f in [DataQualityFlag.MISSING_FORWARD_PE, DataQualityFlag.MISSING_TRAILING_PE]):
        result.checks_passed.append("P/E data present")

    # 3. Check negative P/E
    negative_issues = check_negative_pe(data)
    for flag, msg in negative_issues:
        is_zero = flag == DataQualityFlag.ZERO_PE
        result.add_flag(flag, msg, is_error=is_zero)
        confidence_penalties.append(0.2 if is_zero else 0.1)
        result.requires_manual_review = True

    if not negative_issues:
        result.checks_passed.append("P/E values valid")

    # 4. Check extreme growth
    growth_issue = check_extreme_growth(data.trailing_eps, data.forward_eps)
    if growth_issue:
        result.add_flag(growth_issue[0], growth_issue[1], is_error=False)
        confidence_penalties.append(0.15)
        result.requires_manual_review = True
    else:
        if data.trailing_eps is not None and data.forward_eps is not None:
            result.checks_passed.append("Growth projection reasonable")

    # 5. Check stale estimates
    stale_issue = check_stale_estimates(data)
    if stale_issue:
        result.add_flag(stale_issue[0], stale_issue[1], is_error=False)
        confidence_penalties.append(0.1)
    else:
        result.checks_passed.append("Data freshness OK")

    # Calculate confidence score
    result.confidence_score = max(0.0, 1.0 - sum(confidence_penalties))

    # Determine quality level
    validator_config = get_config()

    if result.errors:
        result.quality_level = DataQualityLevel.UNRELIABLE
    elif result.confidence_score >= validator_config.min_confidence_for_verified:
        result.quality_level = DataQualityLevel.VERIFIED
    elif result.confidence_score >= validator_config.min_confidence_for_acceptable:
        result.quality_level = DataQualityLevel.ACCEPTABLE
    elif result.requires_manual_review:
        result.quality_level = DataQualityLevel.SUSPICIOUS
    else:
        result.quality_level = DataQualityLevel.ACCEPTABLE

    logger.debug(
        f"{data.ticker}: Quality={result.quality_level.value}, "
        f"Confidence={result.confidence_score:.2f}, "
        f"Flags={len(result.flags)}"
    )

    return result


# =============================================================================
# Batch Validation
# =============================================================================


def validate_batch(
    data_list: list["MarketData"],
) -> list[ValidationResult]:
    """
    Validate a batch of market data objects.

    Args:
        data_list: List of MarketData objects to validate

    Returns:
        List of ValidationResult objects
    """
    return [validate_market_data(data) for data in data_list]


def get_validation_summary(results: list[ValidationResult]) -> dict:
    """
    Generate a summary of validation results.

    Args:
        results: List of ValidationResult objects

    Returns:
        Summary dictionary with counts and statistics
    """
    summary = {
        "total": len(results),
        "verified": 0,
        "acceptable": 0,
        "suspicious": 0,
        "unreliable": 0,
        "usable": 0,
        "requires_review": 0,
        "avg_confidence": 0.0,
        "common_issues": {},
    }

    confidence_sum = 0.0
    issue_counts: dict[DataQualityFlag, int] = {}

    for result in results:
        # Count by quality level
        level_key = result.quality_level.value
        summary[level_key] = summary.get(level_key, 0) + 1

        # Count usable
        if result.is_usable:
            summary["usable"] += 1

        # Count requires review
        if result.requires_manual_review:
            summary["requires_review"] += 1

        # Sum confidence
        confidence_sum += result.confidence_score

        # Count flags
        for flag in result.flags:
            issue_counts[flag] = issue_counts.get(flag, 0) + 1

    # Calculate average confidence
    if results:
        summary["avg_confidence"] = confidence_sum / len(results)

    # Convert flags to string keys for JSON compatibility
    summary["common_issues"] = {
        flag.value: count
        for flag, count in sorted(issue_counts.items(), key=lambda x: -x[1])
    }

    return summary


def filter_usable(
    data_list: list["MarketData"],
    validation_results: Optional[list[ValidationResult]] = None,
) -> list["MarketData"]:
    """
    Filter market data to only usable quality.

    Args:
        data_list: List of MarketData objects
        validation_results: Optional pre-computed validation results

    Returns:
        List of MarketData objects that pass quality checks
    """
    if validation_results is None:
        validation_results = validate_batch(data_list)

    usable = []
    for data, result in zip(data_list, validation_results):
        if result.is_usable:
            usable.append(data)
        else:
            logger.info(
                f"Filtered out {data.ticker}: {result.quality_level.value} "
                f"({len(result.errors)} errors, {len(result.warnings)} warnings)"
            )

    return usable
