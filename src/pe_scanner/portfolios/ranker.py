"""
Portfolio Ranking Module

Ranks portfolio positions by P/E compression magnitude and
assigns buy/sell/hold signals with confidence levels.

Integrates:
- Compression analysis (signal direction)
- Fair value analysis (upside potential)
- Data validation (confidence scoring)
"""

import logging
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import TYPE_CHECKING, Optional

import yaml

if TYPE_CHECKING:
    from pe_scanner.analysis.compression import CompressionResult
    from pe_scanner.analysis.fair_value import FairValueResult
    from pe_scanner.data.validator import ValidationResult

logger = logging.getLogger(__name__)


# =============================================================================
# Enums
# =============================================================================


class Signal(Enum):
    """Trading signal classification."""

    STRONG_BUY = "strong_buy"
    BUY = "buy"
    HOLD = "hold"
    SELL = "sell"
    STRONG_SELL = "strong_sell"
    DO_NOT_TRADE = "do_not_trade"  # Data quality issues


class Confidence(Enum):
    """Signal confidence level."""

    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


# Signal display info
SIGNAL_INFO = {
    Signal.STRONG_BUY: {"icon": "🟢🟢", "action": "Buy aggressively"},
    Signal.BUY: {"icon": "🟢", "action": "Buy"},
    Signal.HOLD: {"icon": "🟡", "action": "Hold/Monitor"},
    Signal.SELL: {"icon": "🔴", "action": "Sell"},
    Signal.STRONG_SELL: {"icon": "🔴🔴", "action": "Sell immediately"},
    Signal.DO_NOT_TRADE: {"icon": "⚫", "action": "Do not trade (data issues)"},
}


# =============================================================================
# Data Classes
# =============================================================================


@dataclass
class RankedPosition:
    """A position with ranking and signal information."""

    ticker: str
    rank: int
    compression_pct: float
    signal: Signal
    confidence: Confidence
    bear_upside_pct: float
    bull_upside_pct: float
    current_price: Optional[float] = None
    forward_pe: Optional[float] = None
    trailing_pe: Optional[float] = None
    implied_growth_pct: Optional[float] = None
    data_quality_warnings: list[str] = field(default_factory=list)
    action_priority: int = 0  # 1 = immediate, 2 = soon, 3 = monitor

    @property
    def signal_icon(self) -> str:
        """Get signal icon."""
        return SIGNAL_INFO.get(self.signal, {}).get("icon", "❓")

    @property
    def action_text(self) -> str:
        """Get action recommendation text."""
        return SIGNAL_INFO.get(self.signal, {}).get("action", "Unknown")

    @property
    def is_actionable(self) -> bool:
        """Check if position requires action (not hold)."""
        return self.signal not in (Signal.HOLD, Signal.DO_NOT_TRADE)

    @property
    def is_buy(self) -> bool:
        """Check if buy signal."""
        return self.signal in (Signal.STRONG_BUY, Signal.BUY)

    @property
    def is_sell(self) -> bool:
        """Check if sell signal."""
        return self.signal in (Signal.STRONG_SELL, Signal.SELL)

    @property
    def midpoint_upside_pct(self) -> float:
        """Calculate midpoint between bear and bull upside."""
        return (self.bear_upside_pct + self.bull_upside_pct) / 2


@dataclass
class RankingResult:
    """Complete ranking results for a portfolio."""

    portfolio_name: str
    total_positions: int
    ranked_positions: list[RankedPosition] = field(default_factory=list)
    buy_signals: list[RankedPosition] = field(default_factory=list)
    sell_signals: list[RankedPosition] = field(default_factory=list)
    hold_signals: list[RankedPosition] = field(default_factory=list)
    excluded: list[tuple[str, str]] = field(default_factory=list)  # (ticker, reason)

    @property
    def actionable_count(self) -> int:
        """Count of positions requiring action."""
        return len(self.buy_signals) + len(self.sell_signals)

    @property
    def summary(self) -> str:
        """Summary string."""
        return (
            f"{len(self.buy_signals)} BUY | "
            f"{len(self.hold_signals)} HOLD | "
            f"{len(self.sell_signals)} SELL"
        )


# =============================================================================
# Configuration
# =============================================================================


@dataclass
class RankingConfig:
    """Configuration for ranking and signals."""

    strong_buy_threshold: float = 50.0
    buy_threshold: float = 20.0
    sell_threshold: float = -20.0
    strong_sell_threshold: float = -50.0
    min_confidence_for_signal: float = 0.5


def _load_config() -> RankingConfig:
    """Load ranking configuration from config.yaml."""
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
                thresholds = analysis.get("compression_thresholds", {})
                return RankingConfig(
                    strong_buy_threshold=thresholds.get("strong_buy", 50.0),
                    buy_threshold=thresholds.get("buy", 20.0),
                    sell_threshold=thresholds.get("sell", -20.0),
                    strong_sell_threshold=thresholds.get("strong_sell", -50.0),
                )
            except Exception as e:
                logger.warning(f"Failed to load config from {config_path}: {e}")

    return RankingConfig()


# Global config (lazy loaded)
_config: Optional[RankingConfig] = None


def get_config() -> RankingConfig:
    """Get ranking configuration."""
    global _config
    if _config is None:
        _config = _load_config()
    return _config


# =============================================================================
# Core Ranking Functions
# =============================================================================


def calculate_confidence(
    compression_pct: float,
    validation_result: Optional["ValidationResult"] = None,
    data_warnings: Optional[list[str]] = None,
) -> Confidence:
    """
    Calculate confidence level based on data quality and signal strength.

    Args:
        compression_pct: P/E compression percentage
        validation_result: Data validation result
        data_warnings: List of data quality warnings

    Returns:
        Confidence level (HIGH, MEDIUM, LOW)
    """
    confidence_score = 1.0

    # Reduce confidence based on validation results
    if validation_result:
        confidence_score *= validation_result.confidence_score

    # Reduce confidence based on warnings
    if data_warnings:
        warning_penalty = min(len(data_warnings) * 0.1, 0.3)
        confidence_score -= warning_penalty

    # Extreme compression values are less reliable
    if abs(compression_pct) > 100:
        confidence_score *= 0.8

    # Map to confidence levels
    if confidence_score >= 0.8:
        return Confidence.HIGH
    elif confidence_score >= 0.5:
        return Confidence.MEDIUM
    else:
        return Confidence.LOW


def assign_signal(
    compression_pct: float,
    confidence: Confidence,
    config: Optional[RankingConfig] = None,
) -> Signal:
    """
    Assign trading signal based on compression and confidence.

    Args:
        compression_pct: P/E compression percentage
        confidence: Confidence level
        config: Optional ranking configuration

    Returns:
        Trading signal
    """
    cfg = config or get_config()

    # Low confidence -> DO_NOT_TRADE
    if confidence == Confidence.LOW:
        return Signal.DO_NOT_TRADE

    # Assign signal based on thresholds
    if compression_pct >= cfg.strong_buy_threshold:
        return Signal.STRONG_BUY
    elif compression_pct >= cfg.buy_threshold:
        return Signal.BUY
    elif compression_pct <= cfg.strong_sell_threshold:
        return Signal.STRONG_SELL
    elif compression_pct <= cfg.sell_threshold:
        return Signal.SELL
    else:
        return Signal.HOLD


def calculate_action_priority(signal: Signal, confidence: Confidence) -> int:
    """
    Calculate action priority (1=immediate, 2=soon, 3=monitor).

    Args:
        signal: Trading signal
        confidence: Confidence level

    Returns:
        Priority level (1-3)
    """
    if signal in (Signal.STRONG_BUY, Signal.STRONG_SELL):
        return 1 if confidence == Confidence.HIGH else 2
    elif signal in (Signal.BUY, Signal.SELL):
        return 2 if confidence == Confidence.HIGH else 3
    else:
        return 3


def rank_positions(
    compression_results: list["CompressionResult"],
    fair_value_results: Optional[list["FairValueResult"]] = None,
    validation_results: Optional[list["ValidationResult"]] = None,
    sort_by: str = "compression",
) -> list[RankedPosition]:
    """
    Rank positions by compression magnitude and assign signals.

    Args:
        compression_results: P/E compression analysis results
        fair_value_results: Fair value scenario results (optional)
        validation_results: Data quality validation results (optional)
        sort_by: Ranking criteria ("compression", "bull_upside", "bear_upside", "compression_abs")

    Returns:
        List of RankedPosition objects sorted by criteria
    """
    # Build lookup maps
    fv_map = {}
    if fair_value_results:
        for fv in fair_value_results:
            fv_map[fv.ticker] = fv

    val_map = {}
    if validation_results:
        for val in validation_results:
            val_map[val.ticker] = val

    # Create ranked positions
    positions = []
    for cr in compression_results:
        ticker = cr.ticker

        # Get fair value data
        fv = fv_map.get(ticker)
        bear_upside = fv.bear_upside_pct if fv else 0.0
        bull_upside = fv.bull_upside_pct if fv else 0.0

        # Get validation data
        val = val_map.get(ticker)
        warnings = cr.warnings.copy()
        if val:
            warnings.extend(val.warnings)

        # Calculate confidence and signal
        confidence = calculate_confidence(cr.compression_pct, val, warnings)
        signal = assign_signal(cr.compression_pct, confidence)
        priority = calculate_action_priority(signal, confidence)

        position = RankedPosition(
            ticker=ticker,
            rank=0,  # Will be assigned after sorting
            compression_pct=cr.compression_pct,
            signal=signal,
            confidence=confidence,
            bear_upside_pct=bear_upside,
            bull_upside_pct=bull_upside,
            forward_pe=getattr(cr, 'forward_pe', None),
            trailing_pe=getattr(cr, 'trailing_pe', None),
            implied_growth_pct=cr.implied_growth_pct,
            data_quality_warnings=warnings,
            action_priority=priority,
        )
        positions.append(position)

    # Sort positions
    if sort_by == "compression":
        # Highest compression first (best buys)
        positions.sort(key=lambda p: p.compression_pct, reverse=True)
    elif sort_by == "compression_abs":
        # Highest absolute compression first
        positions.sort(key=lambda p: abs(p.compression_pct), reverse=True)
    elif sort_by == "bull_upside":
        positions.sort(key=lambda p: p.bull_upside_pct, reverse=True)
    elif sort_by == "bear_upside":
        positions.sort(key=lambda p: p.bear_upside_pct, reverse=True)
    elif sort_by == "priority":
        # Lowest priority number first (most urgent)
        positions.sort(key=lambda p: (p.action_priority, -abs(p.compression_pct)))
    else:
        logger.warning(f"Unknown sort_by: {sort_by}, using compression")
        positions.sort(key=lambda p: p.compression_pct, reverse=True)

    # Assign ranks
    for i, pos in enumerate(positions, 1):
        pos.rank = i

    return positions


def categorize_by_action(
    ranked_positions: list[RankedPosition],
    portfolio_name: str = "Portfolio",
) -> RankingResult:
    """
    Categorize positions by recommended action.

    Args:
        ranked_positions: List of ranked positions with signals
        portfolio_name: Name of the portfolio

    Returns:
        RankingResult with positions categorized
    """
    result = RankingResult(
        portfolio_name=portfolio_name,
        total_positions=len(ranked_positions),
        ranked_positions=ranked_positions,
    )

    for pos in ranked_positions:
        if pos.signal == Signal.DO_NOT_TRADE:
            result.excluded.append((pos.ticker, "Data quality issues"))
        elif pos.is_buy:
            result.buy_signals.append(pos)
        elif pos.is_sell:
            result.sell_signals.append(pos)
        else:
            result.hold_signals.append(pos)

    return result


def get_top_opportunities(
    ranking_result: RankingResult,
    n: int = 5,
    signal_type: str = "buy",
) -> list[RankedPosition]:
    """
    Get top N opportunities from ranking results.

    Args:
        ranking_result: Complete ranking results
        n: Number of top opportunities to return
        signal_type: Type of signal ("buy", "sell", or "actionable")

    Returns:
        List of top positions
    """
    if signal_type == "buy":
        positions = ranking_result.buy_signals
    elif signal_type == "sell":
        positions = ranking_result.sell_signals
    elif signal_type == "actionable":
        positions = [p for p in ranking_result.ranked_positions if p.is_actionable]
    else:
        positions = ranking_result.ranked_positions

    return positions[:n]


# =============================================================================
# High-Level API
# =============================================================================


def rank_portfolio(
    compression_results: list["CompressionResult"],
    fair_value_results: Optional[list["FairValueResult"]] = None,
    validation_results: Optional[list["ValidationResult"]] = None,
    portfolio_name: str = "Portfolio",
    sort_by: str = "compression",
) -> RankingResult:
    """
    Complete portfolio ranking pipeline.

    This is the main entry point for ranking a portfolio.

    Args:
        compression_results: P/E compression analysis results
        fair_value_results: Fair value scenario results (optional)
        validation_results: Data quality validation results (optional)
        portfolio_name: Name of the portfolio
        sort_by: Ranking criteria

    Returns:
        Complete RankingResult with categorized positions

    Example:
        >>> result = rank_portfolio(compressions, fair_values, validations)
        >>> print(f"Summary: {result.summary}")
        >>> for pos in result.buy_signals[:5]:
        ...     print(f"{pos.signal_icon} {pos.ticker}: {pos.compression_pct:+.1f}%")
    """
    # Rank and assign signals
    ranked = rank_positions(
        compression_results,
        fair_value_results,
        validation_results,
        sort_by=sort_by,
    )

    # Categorize by action
    result = categorize_by_action(ranked, portfolio_name)

    logger.info(
        f"Ranked {result.total_positions} positions: {result.summary}"
    )

    return result


def get_actionable_summary(result: RankingResult) -> dict:
    """
    Get a summary of actionable positions.

    Args:
        result: RankingResult from ranking

    Returns:
        Summary dictionary
    """
    return {
        "portfolio": result.portfolio_name,
        "total": result.total_positions,
        "buy_count": len(result.buy_signals),
        "sell_count": len(result.sell_signals),
        "hold_count": len(result.hold_signals),
        "excluded_count": len(result.excluded),
        "top_buys": [
            {"ticker": p.ticker, "compression": p.compression_pct, "signal": p.signal.value}
            for p in result.buy_signals[:3]
        ],
        "top_sells": [
            {"ticker": p.ticker, "compression": p.compression_pct, "signal": p.signal.value}
            for p in result.sell_signals[:3]
        ],
    }
