"""
Manual Verification Support Module

Provides tools and output formats to support manual verification of
suspicious signals using financial statements and alternative data sources.

Key features:
- Verification checklists for flagged stocks
- Comparison tables (actual vs expected)
- Data source mismatch detection
- Status icons (✅/⚠️/❌) for quick visual assessment
"""

import logging
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from pe_scanner.data.fetcher import MarketData
    from pe_scanner.data.corrector import CorrectionResult
    from pe_scanner.data.validator import ValidationResult

logger = logging.getLogger(__name__)


# =============================================================================
# Enums and Constants
# =============================================================================


class VerificationStatus(Enum):
    """Status of a verification check."""

    PASSED = "passed"  # ✅ Check passed
    WARNING = "warning"  # ⚠️ Needs attention
    FAILED = "failed"  # ❌ Check failed
    SKIPPED = "skipped"  # ⏭️ Not applicable
    PENDING = "pending"  # 🔄 Awaiting manual review


# Status icons for display
STATUS_ICONS = {
    VerificationStatus.PASSED: "✅",
    VerificationStatus.WARNING: "⚠️",
    VerificationStatus.FAILED: "❌",
    VerificationStatus.SKIPPED: "⏭️",
    VerificationStatus.PENDING: "🔄",
}


# =============================================================================
# Data Classes
# =============================================================================


@dataclass
class VerificationCheck:
    """Result of a single verification check."""

    name: str
    description: str
    status: VerificationStatus
    expected_value: Optional[str] = None
    actual_value: Optional[str] = None
    notes: Optional[str] = None
    source: Optional[str] = None

    @property
    def icon(self) -> str:
        """Get status icon."""
        return STATUS_ICONS.get(self.status, "❓")

    def to_row(self) -> list[str]:
        """Convert to table row."""
        return [
            self.icon,
            self.name,
            self.expected_value or "-",
            self.actual_value or "-",
            self.notes or "",
        ]


@dataclass
class VerificationChecklist:
    """Complete verification checklist for a stock."""

    ticker: str
    checks: list[VerificationCheck] = field(default_factory=list)
    overall_status: VerificationStatus = VerificationStatus.PENDING
    verification_timestamp: datetime = field(default_factory=datetime.now)
    manual_notes: Optional[str] = None
    verified_by: Optional[str] = None

    @property
    def passed_count(self) -> int:
        """Count of passed checks."""
        return sum(1 for c in self.checks if c.status == VerificationStatus.PASSED)

    @property
    def warning_count(self) -> int:
        """Count of warning checks."""
        return sum(1 for c in self.checks if c.status == VerificationStatus.WARNING)

    @property
    def failed_count(self) -> int:
        """Count of failed checks."""
        return sum(1 for c in self.checks if c.status == VerificationStatus.FAILED)

    @property
    def total_checks(self) -> int:
        """Total number of checks."""
        return len(self.checks)

    @property
    def summary(self) -> str:
        """Summary string."""
        return f"{self.passed_count}✅ {self.warning_count}⚠️ {self.failed_count}❌"

    def add_check(self, check: VerificationCheck) -> None:
        """Add a verification check."""
        self.checks.append(check)

    def determine_overall_status(self) -> VerificationStatus:
        """Determine overall status based on individual checks."""
        if self.failed_count > 0:
            self.overall_status = VerificationStatus.FAILED
        elif self.warning_count > 0:
            self.overall_status = VerificationStatus.WARNING
        elif self.passed_count == self.total_checks and self.total_checks > 0:
            self.overall_status = VerificationStatus.PASSED
        else:
            self.overall_status = VerificationStatus.PENDING
        return self.overall_status


# =============================================================================
# Verification Check Functions
# =============================================================================


def check_trailing_eps(
    data: "MarketData",
    reported_eps: Optional[float] = None,
    tolerance: float = 0.05,
) -> VerificationCheck:
    """
    Check trailing EPS against reported financial statements.

    Args:
        data: MarketData with trailing EPS
        reported_eps: EPS from financial statements (if available)
        tolerance: Acceptable % deviation (default: 5%)

    Returns:
        VerificationCheck with comparison result
    """
    if data.trailing_eps is None:
        return VerificationCheck(
            name="Trailing EPS",
            description="Compare trailing EPS with financial statements",
            status=VerificationStatus.SKIPPED,
            notes="No trailing EPS data available",
        )

    if reported_eps is None:
        return VerificationCheck(
            name="Trailing EPS",
            description="Compare trailing EPS with financial statements",
            status=VerificationStatus.PENDING,
            expected_value="Check 10-K/10-Q",
            actual_value=f"${data.trailing_eps:.2f}",
            notes="Manual verification required - compare with SEC filings",
            source="Yahoo Finance",
        )

    # Compare values
    deviation = abs(data.trailing_eps - reported_eps) / abs(reported_eps) if reported_eps != 0 else 0

    if deviation <= tolerance:
        status = VerificationStatus.PASSED
        notes = f"Within {tolerance*100:.0f}% tolerance"
    elif deviation <= tolerance * 2:
        status = VerificationStatus.WARNING
        notes = f"Deviation of {deviation*100:.1f}% - review recommended"
    else:
        status = VerificationStatus.FAILED
        notes = f"Significant deviation of {deviation*100:.1f}%"

    return VerificationCheck(
        name="Trailing EPS",
        description="Compare trailing EPS with financial statements",
        status=status,
        expected_value=f"${reported_eps:.2f}",
        actual_value=f"${data.trailing_eps:.2f}",
        notes=notes,
        source="SEC Filings vs Yahoo Finance",
    )


def check_forward_eps(
    data: "MarketData",
    analyst_consensus: Optional[float] = None,
    tolerance: float = 0.10,
) -> VerificationCheck:
    """
    Check forward EPS against analyst consensus.

    Args:
        data: MarketData with forward EPS
        analyst_consensus: Consensus EPS estimate (if available)
        tolerance: Acceptable % deviation (default: 10%)

    Returns:
        VerificationCheck with comparison result
    """
    if data.forward_eps is None:
        return VerificationCheck(
            name="Forward EPS",
            description="Verify forward EPS with analyst consensus",
            status=VerificationStatus.SKIPPED,
            notes="No forward EPS data available",
        )

    if analyst_consensus is None:
        return VerificationCheck(
            name="Forward EPS",
            description="Verify forward EPS with analyst consensus",
            status=VerificationStatus.PENDING,
            expected_value="Check Bloomberg/FactSet",
            actual_value=f"${data.forward_eps:.2f}",
            notes="Manual verification required - compare with analyst consensus",
            source="Yahoo Finance",
        )

    # Compare values
    deviation = abs(data.forward_eps - analyst_consensus) / abs(analyst_consensus) if analyst_consensus != 0 else 0

    if deviation <= tolerance:
        status = VerificationStatus.PASSED
        notes = f"Within {tolerance*100:.0f}% of consensus"
    elif deviation <= tolerance * 2:
        status = VerificationStatus.WARNING
        notes = f"Deviation of {deviation*100:.1f}% from consensus"
    else:
        status = VerificationStatus.FAILED
        notes = f"Significant deviation of {deviation*100:.1f}% from consensus"

    return VerificationCheck(
        name="Forward EPS",
        description="Verify forward EPS with analyst consensus",
        status=status,
        expected_value=f"${analyst_consensus:.2f}",
        actual_value=f"${data.forward_eps:.2f}",
        notes=notes,
        source="Analyst Consensus vs Yahoo Finance",
    )


def check_stock_split(
    data: "MarketData",
    known_split: Optional[str] = None,
    growth_threshold: float = 100.0,
) -> VerificationCheck:
    """
    Check for potential stock split data issues.

    Args:
        data: MarketData to analyze
        known_split: Known recent split info (e.g., "10:1 on 2024-01-15")
        growth_threshold: Growth % that triggers split suspicion

    Returns:
        VerificationCheck with split analysis
    """
    # Calculate implied growth
    implied_growth = None
    if data.trailing_eps and data.forward_eps and data.trailing_eps != 0:
        implied_growth = ((data.forward_eps - data.trailing_eps) / abs(data.trailing_eps)) * 100

    if implied_growth is None:
        return VerificationCheck(
            name="Stock Split Check",
            description="Verify no stock split data inconsistencies",
            status=VerificationStatus.SKIPPED,
            notes="Insufficient EPS data for split detection",
        )

    # Check for extreme growth (split signature)
    is_suspicious = abs(implied_growth) > growth_threshold

    if not is_suspicious:
        return VerificationCheck(
            name="Stock Split Check",
            description="Verify no stock split data inconsistencies",
            status=VerificationStatus.PASSED,
            expected_value="Growth < 100%",
            actual_value=f"{implied_growth:+.1f}%",
            notes="No split-related data issues detected",
        )

    if known_split:
        return VerificationCheck(
            name="Stock Split Check",
            description="Verify no stock split data inconsistencies",
            status=VerificationStatus.WARNING,
            expected_value=f"Split: {known_split}",
            actual_value=f"{implied_growth:+.1f}% growth",
            notes="Known split - verify EPS values are post-split adjusted",
        )

    return VerificationCheck(
        name="Stock Split Check",
        description="Verify no stock split data inconsistencies",
        status=VerificationStatus.WARNING,
        expected_value="No recent split",
        actual_value=f"{implied_growth:+.1f}% growth",
        notes="Extreme growth suggests possible split - check recent corporate actions",
    )


def check_growth_realism(
    data: "MarketData",
    industry_avg_growth: Optional[float] = None,
    max_realistic_growth: float = 50.0,
) -> VerificationCheck:
    """
    Validate earnings growth realism.

    Args:
        data: MarketData to analyze
        industry_avg_growth: Industry average growth rate (if known)
        max_realistic_growth: Maximum realistic growth % (default: 50%)

    Returns:
        VerificationCheck with growth realism assessment
    """
    if data.trailing_eps is None or data.forward_eps is None or data.trailing_eps == 0:
        return VerificationCheck(
            name="Growth Realism",
            description="Validate earnings growth projection is realistic",
            status=VerificationStatus.SKIPPED,
            notes="Insufficient EPS data for growth analysis",
        )

    implied_growth = ((data.forward_eps - data.trailing_eps) / abs(data.trailing_eps)) * 100

    # Compare to industry if available
    if industry_avg_growth is not None:
        deviation = implied_growth - industry_avg_growth
        if abs(deviation) <= 20:  # Within 20pp of industry
            status = VerificationStatus.PASSED
            notes = f"Growth ({implied_growth:+.1f}%) close to industry avg ({industry_avg_growth:+.1f}%)"
        elif abs(deviation) <= 40:
            status = VerificationStatus.WARNING
            notes = f"Growth ({implied_growth:+.1f}%) deviates from industry ({industry_avg_growth:+.1f}%)"
        else:
            status = VerificationStatus.WARNING
            notes = f"Growth ({implied_growth:+.1f}%) significantly differs from industry ({industry_avg_growth:+.1f}%)"

        return VerificationCheck(
            name="Growth Realism",
            description="Validate earnings growth projection is realistic",
            status=status,
            expected_value=f"{industry_avg_growth:+.1f}% (industry)",
            actual_value=f"{implied_growth:+.1f}%",
            notes=notes,
        )

    # General realism check
    if abs(implied_growth) <= max_realistic_growth:
        status = VerificationStatus.PASSED
        notes = "Growth projection within typical range"
    elif abs(implied_growth) <= max_realistic_growth * 2:
        status = VerificationStatus.WARNING
        notes = "Higher than typical growth - verify analyst rationale"
    else:
        status = VerificationStatus.WARNING
        notes = "Unusually high growth projection - requires justification"

    return VerificationCheck(
        name="Growth Realism",
        description="Validate earnings growth projection is realistic",
        status=status,
        expected_value=f"±{max_realistic_growth:.0f}%",
        actual_value=f"{implied_growth:+.1f}%",
        notes=notes,
    )


def check_pe_ratio(
    data: "MarketData",
    sector_avg_pe: Optional[float] = None,
) -> VerificationCheck:
    """
    Validate P/E ratio against sector average.

    Args:
        data: MarketData to analyze
        sector_avg_pe: Sector average P/E (if known)

    Returns:
        VerificationCheck with P/E comparison
    """
    if data.trailing_pe is None:
        return VerificationCheck(
            name="P/E Ratio",
            description="Compare P/E ratio with sector average",
            status=VerificationStatus.SKIPPED,
            notes="No P/E data available",
        )

    if sector_avg_pe is None:
        return VerificationCheck(
            name="P/E Ratio",
            description="Compare P/E ratio with sector average",
            status=VerificationStatus.PENDING,
            expected_value="Check sector average",
            actual_value=f"{data.trailing_pe:.1f}x",
            notes="Manual verification required - compare with sector peers",
        )

    ratio = data.trailing_pe / sector_avg_pe if sector_avg_pe > 0 else 0

    if 0.5 <= ratio <= 2.0:
        status = VerificationStatus.PASSED
        notes = f"P/E ({data.trailing_pe:.1f}x) reasonable vs sector ({sector_avg_pe:.1f}x)"
    elif 0.25 <= ratio <= 4.0:
        status = VerificationStatus.WARNING
        notes = f"P/E ({data.trailing_pe:.1f}x) significantly differs from sector ({sector_avg_pe:.1f}x)"
    else:
        status = VerificationStatus.WARNING
        notes = f"Extreme P/E deviation - verify data accuracy"

    return VerificationCheck(
        name="P/E Ratio",
        description="Compare P/E ratio with sector average",
        status=status,
        expected_value=f"{sector_avg_pe:.1f}x (sector)",
        actual_value=f"{data.trailing_pe:.1f}x",
        notes=notes,
    )


def check_data_source(
    data: "MarketData",
    alternative_source: Optional[dict] = None,
) -> VerificationCheck:
    """
    Cross-reference data with alternative sources.

    Args:
        data: MarketData from primary source
        alternative_source: Dict with alternative data (price, pe, eps)

    Returns:
        VerificationCheck with source comparison
    """
    if alternative_source is None:
        return VerificationCheck(
            name="Data Source Cross-Reference",
            description="Verify data against Bloomberg/FactSet/Reuters",
            status=VerificationStatus.PENDING,
            expected_value="Check alternative sources",
            actual_value=f"Price: ${data.current_price:.2f}" if data.current_price else "N/A",
            notes="Manual verification required - cross-reference with Bloomberg/FactSet",
            source="Yahoo Finance",
        )

    mismatches = []
    
    # Compare price
    if "price" in alternative_source and data.current_price:
        alt_price = alternative_source["price"]
        price_diff = abs(data.current_price - alt_price) / alt_price * 100
        if price_diff > 2:  # >2% difference
            mismatches.append(f"Price: ${data.current_price:.2f} vs ${alt_price:.2f}")

    # Compare P/E
    if "pe" in alternative_source and data.trailing_pe:
        alt_pe = alternative_source["pe"]
        pe_diff = abs(data.trailing_pe - alt_pe) / alt_pe * 100
        if pe_diff > 5:  # >5% difference
            mismatches.append(f"P/E: {data.trailing_pe:.1f}x vs {alt_pe:.1f}x")

    if not mismatches:
        status = VerificationStatus.PASSED
        notes = "Data consistent across sources"
    else:
        status = VerificationStatus.WARNING
        notes = f"Mismatches found: {'; '.join(mismatches)}"

    return VerificationCheck(
        name="Data Source Cross-Reference",
        description="Verify data against Bloomberg/FactSet/Reuters",
        status=status,
        expected_value="Consistent across sources",
        actual_value="See notes",
        notes=notes,
        source=f"Yahoo Finance vs {alternative_source.get('source', 'Alternative')}",
    )


# =============================================================================
# Main Verification Function
# =============================================================================


def create_verification_checklist(
    data: "MarketData",
    correction_result: Optional["CorrectionResult"] = None,
    validation_result: Optional["ValidationResult"] = None,
    manual_data: Optional[dict] = None,
) -> VerificationChecklist:
    """
    Create a complete verification checklist for a stock.

    Args:
        data: MarketData to verify
        correction_result: Optional correction result for context
        validation_result: Optional validation result for context
        manual_data: Optional dict with manual verification data:
            - reported_eps: EPS from financial statements
            - analyst_consensus: Forward EPS consensus
            - known_split: Recent split info
            - industry_growth: Industry average growth
            - sector_pe: Sector average P/E
            - alternative_source: Data from other sources

    Returns:
        VerificationChecklist with all checks
    """
    checklist = VerificationChecklist(ticker=data.ticker)
    manual_data = manual_data or {}

    # 1. Trailing EPS verification
    checklist.add_check(check_trailing_eps(
        data,
        reported_eps=manual_data.get("reported_eps"),
    ))

    # 2. Forward EPS verification
    checklist.add_check(check_forward_eps(
        data,
        analyst_consensus=manual_data.get("analyst_consensus"),
    ))

    # 3. Stock split check
    checklist.add_check(check_stock_split(
        data,
        known_split=manual_data.get("known_split"),
    ))

    # 4. Growth realism check
    checklist.add_check(check_growth_realism(
        data,
        industry_avg_growth=manual_data.get("industry_growth"),
    ))

    # 5. P/E ratio comparison
    checklist.add_check(check_pe_ratio(
        data,
        sector_avg_pe=manual_data.get("sector_pe"),
    ))

    # 6. Data source cross-reference
    checklist.add_check(check_data_source(
        data,
        alternative_source=manual_data.get("alternative_source"),
    ))

    # Determine overall status
    checklist.determine_overall_status()

    return checklist


# =============================================================================
# Output Formatters
# =============================================================================


def format_checklist_markdown(checklist: VerificationChecklist) -> str:
    """
    Format verification checklist as Markdown.

    Args:
        checklist: VerificationChecklist to format

    Returns:
        Markdown formatted string
    """
    lines = [
        f"## Verification Checklist: {checklist.ticker}",
        "",
        f"**Overall Status:** {STATUS_ICONS[checklist.overall_status]} {checklist.overall_status.value.upper()}",
        f"**Summary:** {checklist.summary}",
        f"**Verified:** {checklist.verification_timestamp.strftime('%Y-%m-%d %H:%M')}",
        "",
        "| Status | Check | Expected | Actual | Notes |",
        "|:------:|-------|----------|--------|-------|",
    ]

    for check in checklist.checks:
        row = check.to_row()
        lines.append(f"| {row[0]} | {row[1]} | {row[2]} | {row[3]} | {row[4]} |")

    if checklist.manual_notes:
        lines.extend(["", f"**Manual Notes:** {checklist.manual_notes}"])

    if checklist.verified_by:
        lines.append(f"**Verified By:** {checklist.verified_by}")

    return "\n".join(lines)


def format_checklist_text(checklist: VerificationChecklist) -> str:
    """
    Format verification checklist as plain text.

    Args:
        checklist: VerificationChecklist to format

    Returns:
        Plain text formatted string
    """
    lines = [
        f"=== Verification Checklist: {checklist.ticker} ===",
        f"Overall: {STATUS_ICONS[checklist.overall_status]} {checklist.overall_status.value.upper()}",
        f"Summary: {checklist.summary}",
        "",
    ]

    for check in checklist.checks:
        lines.append(f"{check.icon} {check.name}")
        if check.expected_value:
            lines.append(f"   Expected: {check.expected_value}")
        if check.actual_value:
            lines.append(f"   Actual:   {check.actual_value}")
        if check.notes:
            lines.append(f"   Notes:    {check.notes}")
        lines.append("")

    return "\n".join(lines)


def format_comparison_table(
    data: "MarketData",
    manual_data: dict,
) -> str:
    """
    Format a comparison table between data sources.

    Args:
        data: MarketData from primary source
        manual_data: Manual verification data

    Returns:
        Markdown table comparing data
    """
    lines = [
        f"## Data Comparison: {data.ticker}",
        "",
        "| Field | Yahoo Finance | Manual/Alternative | Match |",
        "|-------|---------------|-------------------|:-----:|",
    ]

    # Price comparison
    yf_price = f"${data.current_price:.2f}" if data.current_price else "N/A"
    alt_price = f"${manual_data.get('price', 'N/A')}" if manual_data.get('price') else "N/A"
    match = "✅" if data.current_price and manual_data.get('price') and abs(data.current_price - manual_data['price']) / manual_data['price'] < 0.02 else "⚠️"
    lines.append(f"| Current Price | {yf_price} | {alt_price} | {match} |")

    # Trailing P/E comparison
    yf_pe = f"{data.trailing_pe:.2f}x" if data.trailing_pe else "N/A"
    alt_pe = f"{manual_data.get('pe', 'N/A')}x" if manual_data.get('pe') else "N/A"
    match = "✅" if data.trailing_pe and manual_data.get('pe') and abs(data.trailing_pe - manual_data['pe']) / manual_data['pe'] < 0.05 else "⚠️"
    lines.append(f"| Trailing P/E | {yf_pe} | {alt_pe} | {match} |")

    # Trailing EPS comparison
    yf_eps = f"${data.trailing_eps:.2f}" if data.trailing_eps else "N/A"
    alt_eps = f"${manual_data.get('reported_eps', 'N/A')}" if manual_data.get('reported_eps') else "N/A"
    match = "✅" if data.trailing_eps and manual_data.get('reported_eps') and abs(data.trailing_eps - manual_data['reported_eps']) / manual_data['reported_eps'] < 0.05 else "⚠️"
    lines.append(f"| Trailing EPS | {yf_eps} | {alt_eps} | {match} |")

    # Forward EPS comparison
    yf_fwd = f"${data.forward_eps:.2f}" if data.forward_eps else "N/A"
    alt_fwd = f"${manual_data.get('analyst_consensus', 'N/A')}" if manual_data.get('analyst_consensus') else "N/A"
    match = "✅" if data.forward_eps and manual_data.get('analyst_consensus') and abs(data.forward_eps - manual_data['analyst_consensus']) / manual_data['analyst_consensus'] < 0.10 else "⚠️"
    lines.append(f"| Forward EPS | {yf_fwd} | {alt_fwd} | {match} |")

    return "\n".join(lines)


# =============================================================================
# Batch Verification
# =============================================================================


def verify_batch(
    data_list: list["MarketData"],
    manual_data_map: Optional[dict[str, dict]] = None,
) -> list[VerificationChecklist]:
    """
    Create verification checklists for multiple stocks.

    Args:
        data_list: List of MarketData objects
        manual_data_map: Optional dict mapping ticker -> manual_data

    Returns:
        List of VerificationChecklist objects
    """
    manual_data_map = manual_data_map or {}
    results = []

    for data in data_list:
        manual_data = manual_data_map.get(data.ticker, {})
        checklist = create_verification_checklist(data, manual_data=manual_data)
        results.append(checklist)

    return results


def get_verification_summary(checklists: list[VerificationChecklist]) -> dict:
    """
    Generate summary of verification results.

    Args:
        checklists: List of VerificationChecklist objects

    Returns:
        Summary dictionary
    """
    summary = {
        "total": len(checklists),
        "passed": 0,
        "warning": 0,
        "failed": 0,
        "pending": 0,
        "needs_review": [],
    }

    for checklist in checklists:
        status_key = checklist.overall_status.value
        if status_key in summary:
            summary[status_key] += 1

        if checklist.overall_status in (VerificationStatus.WARNING, VerificationStatus.FAILED):
            summary["needs_review"].append(checklist.ticker)

    return summary


