"""
Report Generation Module

Generates markdown reports with analysis results, warnings,
and actionable recommendations for portfolio positions.

Report sections:
1. Summary - Immediate actions, key metrics
2. Buy Opportunities - Ranked by compression
3. Sell Signals - Positions to exit
4. Hold Positions - Monitor list
5. Data Quality Warnings - Flags and issues
"""

import logging
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import TYPE_CHECKING, Optional, Union

if TYPE_CHECKING:
    from pe_scanner.portfolios.ranker import RankedPosition, RankingResult

logger = logging.getLogger(__name__)


# =============================================================================
# Enums and Configuration
# =============================================================================


class ReportFormat(Enum):
    """Supported report output formats."""

    MARKDOWN = "markdown"
    TEXT = "text"
    JSON = "json"
    CONSOLE = "console"


@dataclass
class ReportConfig:
    """Configuration for report generation."""

    format: ReportFormat = ReportFormat.MARKDOWN
    include_warnings: bool = True
    include_verification_status: bool = True
    include_fair_values: bool = True
    include_methodology: bool = False
    max_positions_detail: int = 50
    show_confidence: bool = True
    show_priority: bool = True


# =============================================================================
# Data Classes
# =============================================================================


@dataclass
class Report:
    """Generated analysis report."""

    title: str
    generated_at: datetime = field(default_factory=datetime.now)
    content: str = ""
    summary_stats: dict = field(default_factory=dict)
    format: ReportFormat = ReportFormat.MARKDOWN
    sections: dict = field(default_factory=dict)

    def save(self, path: Union[str, Path]) -> Path:
        """Save report to file."""
        return save_report(self, path)


# =============================================================================
# Helper Functions
# =============================================================================


def _format_pct(value: float, width: int = 7) -> str:
    """Format percentage with sign."""
    return f"{value:+{width}.1f}%"


def _format_signal_icon(signal_value: str) -> str:
    """Get icon for signal."""
    icons = {
        "strong_buy": "🟢🟢",
        "buy": "🟢",
        "hold": "🟡",
        "sell": "🔴",
        "strong_sell": "🔴🔴",
        "do_not_trade": "⚫",
    }
    return icons.get(signal_value, "❓")


def _format_confidence_icon(confidence_value: str) -> str:
    """Get icon for confidence level."""
    icons = {
        "high": "●●●",
        "medium": "●●○",
        "low": "●○○",
    }
    return icons.get(confidence_value, "○○○")


def _format_priority(priority: int) -> str:
    """Format action priority."""
    priorities = {
        1: "🔥 Immediate",
        2: "⚡ Soon",
        3: "👀 Monitor",
    }
    return priorities.get(priority, "")


# =============================================================================
# Position Formatting
# =============================================================================


def format_position_row(
    position: "RankedPosition",
    include_fair_values: bool = True,
    include_confidence: bool = True,
) -> str:
    """
    Format a single position as a markdown table row.

    Args:
        position: RankedPosition to format
        include_fair_values: Include bear/bull upside
        include_confidence: Include confidence indicator

    Returns:
        Formatted markdown table row
    """
    signal_icon = _format_signal_icon(position.signal.value)
    compression = _format_pct(position.compression_pct)

    cols = [
        str(position.rank),
        signal_icon,
        position.ticker,
        compression,
    ]

    if include_fair_values:
        cols.extend([
            _format_pct(position.bear_upside_pct),
            _format_pct(position.bull_upside_pct),
        ])

    if include_confidence:
        confidence_icon = _format_confidence_icon(position.confidence.value)
        cols.append(confidence_icon)

    # Warnings indicator
    warning_indicator = "⚠️" if position.data_quality_warnings else "✓"
    cols.append(warning_indicator)

    return "| " + " | ".join(cols) + " |"


def format_position_detail(position: "RankedPosition") -> str:
    """
    Format detailed position information.

    Args:
        position: RankedPosition to format

    Returns:
        Detailed markdown for the position
    """
    lines = [
        f"### {position.rank}. {position.ticker}",
        "",
        f"**Signal:** {_format_signal_icon(position.signal.value)} {position.signal.value.upper()}",
        f"**Compression:** {position.compression_pct:+.2f}%",
        f"**Confidence:** {_format_confidence_icon(position.confidence.value)} {position.confidence.value}",
        f"**Priority:** {_format_priority(position.action_priority)}",
        "",
        f"| Scenario | Upside |",
        f"|----------|--------|",
        f"| Bear Case (17.5x) | {position.bear_upside_pct:+.1f}% |",
        f"| Bull Case (37.5x) | {position.bull_upside_pct:+.1f}% |",
        f"| Midpoint | {position.midpoint_upside_pct:+.1f}% |",
    ]

    if position.data_quality_warnings:
        lines.extend(["", "**⚠️ Warnings:**"])
        for warning in position.data_quality_warnings:
            lines.append(f"- {warning}")

    lines.append("")
    return "\n".join(lines)


# =============================================================================
# Section Generators
# =============================================================================


def generate_summary(ranking_result: "RankingResult") -> str:
    """
    Generate a brief summary of analysis results.

    Args:
        ranking_result: Ranking results to summarize

    Returns:
        Markdown-formatted summary string
    """
    lines = [
        f"# 📊 {ranking_result.portfolio_name} Analysis",
        "",
        f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M')}",
        f"**Total Positions:** {ranking_result.total_positions}",
        "",
        "## 📈 Summary",
        "",
        f"| Category | Count |",
        f"|----------|-------|",
        f"| 🟢 Buy Signals | {len(ranking_result.buy_signals)} |",
        f"| 🟡 Hold | {len(ranking_result.hold_signals)} |",
        f"| 🔴 Sell Signals | {len(ranking_result.sell_signals)} |",
        f"| ⚫ Excluded (Data Issues) | {len(ranking_result.excluded)} |",
        "",
    ]

    # Immediate actions section
    if ranking_result.buy_signals or ranking_result.sell_signals:
        lines.append("## 🚨 Immediate Actions")
        lines.append("")

        if ranking_result.sell_signals:
            lines.append("### 🔴 SELL")
            for pos in ranking_result.sell_signals[:5]:
                warning = " ⚠️" if pos.data_quality_warnings else ""
                lines.append(
                    f"- **{pos.ticker}**: {pos.compression_pct:+.1f}% compression{warning}"
                )
            lines.append("")

        if ranking_result.buy_signals:
            lines.append("### 🟢 BUY")
            for pos in ranking_result.buy_signals[:5]:
                lines.append(
                    f"- **{pos.ticker}**: {pos.compression_pct:+.1f}% compression, "
                    f"Bull upside: {pos.bull_upside_pct:+.1f}%"
                )
            lines.append("")

    return "\n".join(lines)


def generate_buy_section(
    buy_signals: list["RankedPosition"],
    max_positions: int = 20,
) -> str:
    """Generate buy opportunities section."""
    if not buy_signals:
        return "## 🟢 Buy Opportunities\n\nNo buy signals identified.\n"

    lines = [
        "## 🟢 Buy Opportunities",
        "",
        f"Found **{len(buy_signals)}** positions with positive P/E compression.",
        "",
        "| # | Signal | Ticker | Compression | Bear | Bull | Conf | Qual |",
        "|---|:------:|--------|------------:|-----:|-----:|:----:|:----:|",
    ]

    for pos in buy_signals[:max_positions]:
        lines.append(format_position_row(pos))

    if len(buy_signals) > max_positions:
        lines.append(f"\n*...and {len(buy_signals) - max_positions} more*")

    lines.append("")
    return "\n".join(lines)


def generate_sell_section(
    sell_signals: list["RankedPosition"],
    max_positions: int = 20,
) -> str:
    """Generate sell signals section."""
    if not sell_signals:
        return "## 🔴 Sell Signals\n\nNo sell signals identified.\n"

    lines = [
        "## 🔴 Sell Signals",
        "",
        f"Found **{len(sell_signals)}** positions with negative P/E compression.",
        "",
        "| # | Signal | Ticker | Compression | Bear | Bull | Conf | Qual |",
        "|---|:------:|--------|------------:|-----:|-----:|:----:|:----:|",
    ]

    for pos in sell_signals[:max_positions]:
        lines.append(format_position_row(pos))

    lines.append("")
    return "\n".join(lines)


def generate_hold_section(
    hold_signals: list["RankedPosition"],
    max_positions: int = 20,
) -> str:
    """Generate hold positions section."""
    if not hold_signals:
        return "## 🟡 Hold Positions\n\nNo hold positions.\n"

    lines = [
        "## 🟡 Hold Positions",
        "",
        f"**{len(hold_signals)}** positions within neutral range (±20% compression).",
        "",
        "| # | Signal | Ticker | Compression | Bear | Bull | Conf | Qual |",
        "|---|:------:|--------|------------:|-----:|-----:|:----:|:----:|",
    ]

    for pos in hold_signals[:max_positions]:
        lines.append(format_position_row(pos))

    lines.append("")
    return "\n".join(lines)


def generate_warnings_section(
    ranking_result: "RankingResult",
) -> str:
    """Generate data quality warnings section."""
    warnings_found = []

    for pos in ranking_result.ranked_positions:
        if pos.data_quality_warnings:
            warnings_found.append((pos.ticker, pos.data_quality_warnings))

    if not warnings_found and not ranking_result.excluded:
        return "## ⚠️ Data Quality\n\nNo data quality issues detected. ✅\n"

    lines = [
        "## ⚠️ Data Quality Warnings",
        "",
    ]

    if ranking_result.excluded:
        lines.append("### Excluded Positions")
        lines.append("")
        for ticker, reason in ranking_result.excluded:
            lines.append(f"- **{ticker}**: {reason}")
        lines.append("")

    if warnings_found:
        lines.append("### Positions with Warnings")
        lines.append("")
        for ticker, warnings in warnings_found[:10]:
            lines.append(f"**{ticker}:**")
            for warning in warnings[:3]:
                lines.append(f"  - {warning}")
        lines.append("")

    return "\n".join(lines)


def generate_methodology_section() -> str:
    """Generate methodology explanation section."""
    return """## 📚 Methodology

### P/E Compression Analysis

**Formula:** `Compression % = ((Trailing P/E - Forward P/E) / Trailing P/E) × 100`

- **Positive compression** = Forward P/E is lower → Market expects earnings to GROW
- **Negative compression** = Forward P/E is higher → Market expects earnings to DECLINE

### Signal Thresholds

| Compression | Signal |
|-------------|--------|
| > +50% | 🟢🟢 STRONG BUY |
| > +20% | 🟢 BUY |
| ±20% | 🟡 HOLD |
| < -20% | 🔴 SELL |
| < -50% | 🔴🔴 STRONG SELL |

### Fair Value Scenarios

- **Bear Case**: Forward EPS × 17.5x P/E
- **Bull Case**: Forward EPS × 37.5x P/E

"""


# =============================================================================
# Main Report Generation
# =============================================================================


def generate_report(
    ranking_result: "RankingResult",
    config: Optional[ReportConfig] = None,
) -> Report:
    """
    Generate a complete analysis report.

    Args:
        ranking_result: Ranking results to report on
        config: Optional report configuration

    Returns:
        Report object with formatted content
    """
    config = config or ReportConfig()

    # Build sections
    sections = {}
    content_parts = []

    # Summary
    summary = generate_summary(ranking_result)
    sections["summary"] = summary
    content_parts.append(summary)

    # Buy opportunities
    buy_section = generate_buy_section(
        ranking_result.buy_signals,
        config.max_positions_detail,
    )
    sections["buy"] = buy_section
    content_parts.append(buy_section)

    # Sell signals
    sell_section = generate_sell_section(
        ranking_result.sell_signals,
        config.max_positions_detail,
    )
    sections["sell"] = sell_section
    content_parts.append(sell_section)

    # Hold positions
    hold_section = generate_hold_section(
        ranking_result.hold_signals,
        config.max_positions_detail,
    )
    sections["hold"] = hold_section
    content_parts.append(hold_section)

    # Warnings
    if config.include_warnings:
        warnings_section = generate_warnings_section(ranking_result)
        sections["warnings"] = warnings_section
        content_parts.append(warnings_section)

    # Methodology
    if config.include_methodology:
        methodology = generate_methodology_section()
        sections["methodology"] = methodology
        content_parts.append(methodology)

    # Footer
    footer = f"\n---\n*Report generated by PE Scanner v0.1.0*\n"
    content_parts.append(footer)

    # Build report
    report = Report(
        title=f"{ranking_result.portfolio_name} Analysis Report",
        content="\n".join(content_parts),
        summary_stats={
            "total": ranking_result.total_positions,
            "buy_count": len(ranking_result.buy_signals),
            "sell_count": len(ranking_result.sell_signals),
            "hold_count": len(ranking_result.hold_signals),
            "excluded_count": len(ranking_result.excluded),
        },
        format=config.format,
        sections=sections,
    )

    logger.info(f"Generated report: {report.title}")
    return report


# =============================================================================
# Output Functions
# =============================================================================


def save_report(
    report: Report,
    output_path: Union[str, Path],
) -> Path:
    """
    Save a report to file.

    Args:
        report: Report to save
        output_path: Destination file path

    Returns:
        Path where report was saved
    """
    path = Path(output_path)

    # Ensure directory exists
    path.parent.mkdir(parents=True, exist_ok=True)

    # Add extension if missing
    if not path.suffix:
        if report.format == ReportFormat.MARKDOWN:
            path = path.with_suffix(".md")
        elif report.format == ReportFormat.JSON:
            path = path.with_suffix(".json")
        else:
            path = path.with_suffix(".txt")

    # Write content
    if report.format == ReportFormat.JSON:
        import json
        content = json.dumps({
            "title": report.title,
            "generated_at": report.generated_at.isoformat(),
            "summary_stats": report.summary_stats,
            "sections": report.sections,
        }, indent=2)
    else:
        content = report.content

    path.write_text(content)
    logger.info(f"Saved report to {path}")

    return path


def print_to_console(
    ranking_result: "RankingResult",
    verbose: bool = False,
) -> None:
    """
    Print analysis results to console.

    Args:
        ranking_result: Results to display
        verbose: Include detailed information
    """
    # Generate summary
    summary = generate_summary(ranking_result)
    print(summary)

    if verbose:
        # Detailed positions
        if ranking_result.buy_signals:
            print("\n" + "=" * 60)
            print("BUY OPPORTUNITIES - DETAILS")
            print("=" * 60)
            for pos in ranking_result.buy_signals[:5]:
                print(format_position_detail(pos))

        if ranking_result.sell_signals:
            print("\n" + "=" * 60)
            print("SELL SIGNALS - DETAILS")
            print("=" * 60)
            for pos in ranking_result.sell_signals[:5]:
                print(format_position_detail(pos))


def generate_text_report(ranking_result: "RankingResult") -> str:
    """
    Generate plain text report.

    Args:
        ranking_result: Ranking results

    Returns:
        Plain text report
    """
    lines = [
        "=" * 60,
        f"  {ranking_result.portfolio_name} ANALYSIS REPORT",
        "=" * 60,
        "",
        f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}",
        f"Total Positions: {ranking_result.total_positions}",
        "",
        "-" * 60,
        "SUMMARY",
        "-" * 60,
        f"  Buy Signals:  {len(ranking_result.buy_signals)}",
        f"  Hold:         {len(ranking_result.hold_signals)}",
        f"  Sell Signals: {len(ranking_result.sell_signals)}",
        f"  Excluded:     {len(ranking_result.excluded)}",
        "",
    ]

    if ranking_result.buy_signals:
        lines.extend([
            "-" * 60,
            "TOP BUY OPPORTUNITIES",
            "-" * 60,
        ])
        for i, pos in enumerate(ranking_result.buy_signals[:10], 1):
            lines.append(
                f"  {i}. {pos.ticker:8} {pos.compression_pct:+6.1f}%  "
                f"Bull: {pos.bull_upside_pct:+6.1f}%"
            )
        lines.append("")

    if ranking_result.sell_signals:
        lines.extend([
            "-" * 60,
            "SELL SIGNALS",
            "-" * 60,
        ])
        for i, pos in enumerate(ranking_result.sell_signals[:10], 1):
            lines.append(
                f"  {i}. {pos.ticker:8} {pos.compression_pct:+6.1f}%  "
                f"Bear: {pos.bear_upside_pct:+6.1f}%"
            )
        lines.append("")

    lines.extend([
        "=" * 60,
        "  End of Report",
        "=" * 60,
    ])

    return "\n".join(lines)
