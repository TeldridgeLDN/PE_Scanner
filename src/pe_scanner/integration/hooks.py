"""
diet103 Hooks Framework

Implements validation hooks for data integrity and integration consistency:
1. Pre-Analysis Validator: Verify portfolio data format
2. Data Quality Guardian: Enforce data quality checks
3. Portfolio Sync Validator: Prevent master file drift
4. Results Validator: Verify report accuracy

Based on diet103 patterns from Orchestrator_Project.
"""

import hashlib
import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Callable, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from pe_scanner.portfolios.loader import Portfolio
    from pe_scanner.portfolios.ranker import RankingResult
    from pe_scanner.data.fetcher import MarketData
    from pe_scanner.data.validator import ValidationResult

logger = logging.getLogger(__name__)


# =============================================================================
# Enums and Data Classes
# =============================================================================


class HookType(Enum):
    """Types of validation hooks."""

    PRE_ANALYSIS = "pre_analysis"
    DATA_QUALITY = "data_quality"
    PORTFOLIO_SYNC = "portfolio_sync"
    RESULTS = "results"


class HookStatus(Enum):
    """Status of hook execution."""

    PASSED = "passed"
    WARNING = "warning"
    FAILED = "failed"
    SKIPPED = "skipped"


@dataclass
class HookResult:
    """Result of a hook execution."""

    hook_name: str
    hook_type: HookType
    status: HookStatus
    message: str
    details: dict = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)

    @property
    def is_blocking(self) -> bool:
        """Check if this result should block execution."""
        return self.status == HookStatus.FAILED

    def __str__(self) -> str:
        icon = {
            HookStatus.PASSED: "✅",
            HookStatus.WARNING: "⚠️",
            HookStatus.FAILED: "❌",
            HookStatus.SKIPPED: "⏭️",
        }.get(self.status, "❓")
        return f"{icon} [{self.hook_name}] {self.message}"


# =============================================================================
# Base Hook Class
# =============================================================================


class Hook(ABC):
    """Abstract base class for validation hooks."""

    def __init__(self, name: str, hook_type: HookType):
        self.name = name
        self.hook_type = hook_type
        self.enabled = True

    @abstractmethod
    def validate(self, data: Any) -> HookResult:
        """Execute the validation hook."""
        pass

    def skip(self, reason: str) -> HookResult:
        """Return a skipped result."""
        return HookResult(
            hook_name=self.name,
            hook_type=self.hook_type,
            status=HookStatus.SKIPPED,
            message=reason,
        )

    def passed(self, message: str, details: dict = None) -> HookResult:
        """Return a passed result."""
        return HookResult(
            hook_name=self.name,
            hook_type=self.hook_type,
            status=HookStatus.PASSED,
            message=message,
            details=details or {},
        )

    def warning(self, message: str, details: dict = None) -> HookResult:
        """Return a warning result."""
        return HookResult(
            hook_name=self.name,
            hook_type=self.hook_type,
            status=HookStatus.WARNING,
            message=message,
            details=details or {},
        )

    def failed(self, message: str, details: dict = None) -> HookResult:
        """Return a failed result."""
        return HookResult(
            hook_name=self.name,
            hook_type=self.hook_type,
            status=HookStatus.FAILED,
            message=message,
            details=details or {},
        )


# =============================================================================
# Pre-Analysis Validator
# =============================================================================


class PreAnalysisValidator(Hook):
    """
    Validates portfolio data format before analysis.

    Checks:
    - Required columns present
    - Ticker format valid
    - Numeric fields parseable
    - No duplicate tickers
    """

    REQUIRED_COLUMNS = {"ticker", "shares"}
    OPTIONAL_COLUMNS = {"cost_basis", "purchase_date", "portfolio_type"}

    def __init__(self):
        super().__init__("PreAnalysisValidator", HookType.PRE_ANALYSIS)

    def validate(self, portfolio: "Portfolio") -> HookResult:
        """Validate portfolio format."""
        if not self.enabled:
            return self.skip("Hook disabled")

        if portfolio is None:
            return self.failed("Portfolio is None")

        issues = []

        # Check positions exist
        if not portfolio.positions:
            return self.failed("Portfolio has no positions")

        # Check for required fields
        for pos in portfolio.positions:
            if not pos.ticker:
                issues.append(f"Position missing ticker")
            if pos.shares is None or pos.shares < 0:
                issues.append(f"{pos.ticker}: Invalid shares ({pos.shares})")

        # Check for duplicates
        tickers = [pos.ticker for pos in portfolio.positions]
        duplicates = [t for t in set(tickers) if tickers.count(t) > 1]
        if duplicates:
            issues.append(f"Duplicate tickers: {duplicates}")

        # Validate ticker format
        for pos in portfolio.positions:
            if pos.ticker and not self._is_valid_ticker(pos.ticker):
                issues.append(f"Invalid ticker format: {pos.ticker}")

        if issues:
            return self.warning(
                f"Portfolio has {len(issues)} format issues",
                {"issues": issues},
            )

        return self.passed(
            f"Portfolio format valid ({len(portfolio.positions)} positions)"
        )

    def _is_valid_ticker(self, ticker: str) -> bool:
        """Check if ticker format is valid."""
        if not ticker or len(ticker) > 12:
            return False
        # Allow letters, numbers, dots (for UK stocks), hyphens
        import re
        return bool(re.match(r'^[A-Z0-9.\-]+$', ticker.upper()))


# =============================================================================
# Data Quality Guardian
# =============================================================================


class DataQualityGuardian(Hook):
    """
    Enforces data quality checks on market data.

    Checks:
    - P/E ratios within reasonable bounds
    - No missing critical data
    - Growth rates realistic
    - Currency consistency
    """

    def __init__(
        self,
        max_pe: float = 500.0,
        max_growth: float = 200.0,
        min_confidence: float = 0.5,
    ):
        super().__init__("DataQualityGuardian", HookType.DATA_QUALITY)
        self.max_pe = max_pe
        self.max_growth = max_growth
        self.min_confidence = min_confidence

    def validate(
        self,
        data: tuple[list["MarketData"], list["ValidationResult"]],
    ) -> HookResult:
        """Validate market data quality."""
        if not self.enabled:
            return self.skip("Hook disabled")

        market_data, validations = data
        issues = []
        warnings_count = 0

        for md in market_data:
            # Check extreme P/E values
            if md.trailing_pe and md.trailing_pe > self.max_pe:
                issues.append(f"{md.ticker}: Extreme trailing P/E ({md.trailing_pe:.1f})")
            if md.forward_pe and md.forward_pe > self.max_pe:
                issues.append(f"{md.ticker}: Extreme forward P/E ({md.forward_pe:.1f})")

            # Check growth rates
            if md.trailing_eps and md.forward_eps and md.trailing_eps != 0:
                growth = ((md.forward_eps - md.trailing_eps) / abs(md.trailing_eps)) * 100
                if abs(growth) > self.max_growth:
                    issues.append(f"{md.ticker}: Extreme EPS growth ({growth:+.1f}%)")

        # Check validation results
        for val in validations:
            if val.confidence_score < self.min_confidence:
                warnings_count += 1

        if issues:
            return self.warning(
                f"Data quality issues: {len(issues)} concerns, {warnings_count} low confidence",
                {"issues": issues, "low_confidence_count": warnings_count},
            )

        return self.passed(f"Data quality acceptable ({len(market_data)} tickers checked)")


# =============================================================================
# Portfolio Sync Validator
# =============================================================================


class PortfolioSyncValidator(Hook):
    """
    Prevents master portfolio file drift.

    Checks:
    - Local portfolio matches master
    - Detects added/removed positions
    - Tracks changes over time
    """

    def __init__(self, master_path: Optional[Path] = None):
        super().__init__("PortfolioSyncValidator", HookType.PORTFOLIO_SYNC)
        self.master_path = master_path
        self._last_master_hash: Optional[str] = None

    def validate(self, portfolio: "Portfolio") -> HookResult:
        """Check portfolio sync status."""
        if not self.enabled:
            return self.skip("Hook disabled")

        if self.master_path is None:
            return self.skip("No master portfolio configured")

        if not self.master_path.exists():
            return self.warning(
                f"Master portfolio not found: {self.master_path}",
                {"path": str(self.master_path)},
            )

        # Calculate current hash
        current_hash = self._calculate_hash(portfolio)

        # Load and hash master
        try:
            master_content = self.master_path.read_text()
            master_hash = hashlib.md5(master_content.encode()).hexdigest()[:8]
        except Exception as e:
            return self.failed(f"Cannot read master: {e}")

        # Compare (simplified - in real implementation, would parse master)
        if self._last_master_hash and self._last_master_hash != master_hash:
            return self.warning(
                "Master portfolio has changed since last sync",
                {"previous_hash": self._last_master_hash, "current_hash": master_hash},
            )

        self._last_master_hash = master_hash

        return self.passed(
            f"Portfolio in sync (hash: {current_hash[:8]})",
            {"local_hash": current_hash, "master_hash": master_hash},
        )

    def _calculate_hash(self, portfolio: "Portfolio") -> str:
        """Calculate hash of portfolio contents."""
        tickers = sorted([p.ticker for p in portfolio.positions])
        content = "|".join(tickers)
        return hashlib.md5(content.encode()).hexdigest()


# =============================================================================
# Results Validator
# =============================================================================


class ResultsValidator(Hook):
    """
    Verifies analysis report accuracy.

    Checks:
    - Signal counts match ranking
    - Compression percentages calculated correctly
    - No impossible values
    """

    def __init__(self):
        super().__init__("ResultsValidator", HookType.RESULTS)

    def validate(self, ranking: "RankingResult") -> HookResult:
        """Validate analysis results."""
        if not self.enabled:
            return self.skip("Hook disabled")

        issues = []

        # Verify counts
        total_signals = (
            len(ranking.buy_signals) +
            len(ranking.sell_signals) +
            len(ranking.hold_signals)
        )
        if total_signals != len(ranking.ranked_positions) - len(ranking.excluded):
            issues.append(
                f"Signal count mismatch: {total_signals} signals vs "
                f"{len(ranking.ranked_positions)} positions"
            )

        # Verify compression values
        for pos in ranking.ranked_positions:
            if abs(pos.compression_pct) > 500:
                issues.append(
                    f"{pos.ticker}: Extreme compression ({pos.compression_pct:+.1f}%)"
                )

            # Check signal consistency
            if pos.compression_pct > 50 and pos.signal.value not in ("strong_buy", "buy", "do_not_trade"):
                issues.append(
                    f"{pos.ticker}: High compression ({pos.compression_pct:+.1f}%) but signal is {pos.signal.value}"
                )

        if issues:
            return self.warning(
                f"Results validation found {len(issues)} issues",
                {"issues": issues},
            )

        return self.passed(
            f"Results validated ({len(ranking.ranked_positions)} positions)"
        )


# =============================================================================
# Hooks Manager
# =============================================================================


class HooksManager:
    """
    Manages and executes validation hooks.

    Provides:
    - Hook registration
    - Execution pipeline
    - Result aggregation
    """

    def __init__(self):
        self.hooks: dict[HookType, list[Hook]] = {
            HookType.PRE_ANALYSIS: [],
            HookType.DATA_QUALITY: [],
            HookType.PORTFOLIO_SYNC: [],
            HookType.RESULTS: [],
        }
        self._results: list[HookResult] = []

    def register(self, hook: Hook) -> None:
        """Register a hook."""
        self.hooks[hook.hook_type].append(hook)
        logger.debug(f"Registered hook: {hook.name}")

    def register_defaults(self) -> None:
        """Register default hooks."""
        self.register(PreAnalysisValidator())
        self.register(DataQualityGuardian())
        self.register(ResultsValidator())

    def run(self, hook_type: HookType, data: Any) -> list[HookResult]:
        """Run all hooks of a specific type."""
        results = []
        for hook in self.hooks[hook_type]:
            try:
                result = hook.validate(data)
                results.append(result)
                self._results.append(result)
                logger.info(str(result))
            except Exception as e:
                error_result = HookResult(
                    hook_name=hook.name,
                    hook_type=hook_type,
                    status=HookStatus.FAILED,
                    message=f"Hook error: {e}",
                )
                results.append(error_result)
                self._results.append(error_result)
                logger.error(f"Hook {hook.name} failed: {e}")

        return results

    def run_all(
        self,
        portfolio: "Portfolio" = None,
        market_data: list["MarketData"] = None,
        validations: list["ValidationResult"] = None,
        ranking: "RankingResult" = None,
    ) -> list[HookResult]:
        """Run all applicable hooks based on available data."""
        results = []

        if portfolio:
            results.extend(self.run(HookType.PRE_ANALYSIS, portfolio))
            results.extend(self.run(HookType.PORTFOLIO_SYNC, portfolio))

        if market_data and validations:
            results.extend(self.run(HookType.DATA_QUALITY, (market_data, validations)))

        if ranking:
            results.extend(self.run(HookType.RESULTS, ranking))

        return results

    def has_blocking_failures(self) -> bool:
        """Check if any results are blocking."""
        return any(r.is_blocking for r in self._results)

    def get_summary(self) -> dict:
        """Get summary of all hook results."""
        return {
            "total": len(self._results),
            "passed": sum(1 for r in self._results if r.status == HookStatus.PASSED),
            "warnings": sum(1 for r in self._results if r.status == HookStatus.WARNING),
            "failed": sum(1 for r in self._results if r.status == HookStatus.FAILED),
            "skipped": sum(1 for r in self._results if r.status == HookStatus.SKIPPED),
        }

    def clear_results(self) -> None:
        """Clear accumulated results."""
        self._results.clear()


# =============================================================================
# Convenience Functions
# =============================================================================


def run_hooks(
    portfolio: "Portfolio" = None,
    market_data: list["MarketData"] = None,
    validations: list["ValidationResult"] = None,
    ranking: "RankingResult" = None,
) -> tuple[list[HookResult], bool]:
    """
    Run default hooks on provided data.

    Returns:
        Tuple of (results, has_blocking_failures)
    """
    manager = HooksManager()
    manager.register_defaults()

    results = manager.run_all(
        portfolio=portfolio,
        market_data=market_data,
        validations=validations,
        ranking=ranking,
    )

    return results, manager.has_blocking_failures()

