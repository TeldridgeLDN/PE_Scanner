"""
Unit tests for Report Generation Module
"""

import json
import pytest
from pathlib import Path
from datetime import datetime
from unittest.mock import Mock

from pe_scanner.portfolios.ranker import (
    Confidence,
    RankedPosition,
    RankingResult,
    Signal,
)
from pe_scanner.portfolios.reporter import (
    Report,
    ReportConfig,
    ReportFormat,
    format_position_detail,
    format_position_row,
    generate_buy_section,
    generate_hold_section,
    generate_methodology_section,
    generate_report,
    generate_sell_section,
    generate_summary,
    generate_text_report,
    generate_warnings_section,
    print_to_console,
    save_report,
)


# =============================================================================
# Test Fixtures
# =============================================================================


@pytest.fixture
def sample_buy_position():
    """Create a sample buy position."""
    return RankedPosition(
        ticker="BATS.L",
        rank=1,
        compression_pct=62.6,
        signal=Signal.STRONG_BUY,
        confidence=Confidence.HIGH,
        bear_upside_pct=56.0,
        bull_upside_pct=234.2,
        data_quality_warnings=[],
        action_priority=1,
    )


@pytest.fixture
def sample_sell_position():
    """Create a sample sell position."""
    return RankedPosition(
        ticker="HOOD",
        rank=1,
        compression_pct=-113.7,
        signal=Signal.STRONG_SELL,
        confidence=Confidence.MEDIUM,
        bear_upside_pct=-88.8,
        bull_upside_pct=-76.0,
        data_quality_warnings=["Extreme negative compression"],
        action_priority=1,
    )


@pytest.fixture
def sample_hold_position():
    """Create a sample hold position."""
    return RankedPosition(
        ticker="AAPL",
        rank=3,
        compression_pct=14.3,
        signal=Signal.HOLD,
        confidence=Confidence.HIGH,
        bear_upside_pct=-27.1,
        bull_upside_pct=56.2,
        data_quality_warnings=[],
        action_priority=3,
    )


@pytest.fixture
def sample_ranking_result(sample_buy_position, sample_sell_position, sample_hold_position):
    """Create a sample ranking result."""
    return RankingResult(
        portfolio_name="Test Portfolio",
        total_positions=3,
        ranked_positions=[sample_buy_position, sample_hold_position, sample_sell_position],
        buy_signals=[sample_buy_position],
        sell_signals=[sample_sell_position],
        hold_signals=[sample_hold_position],
        excluded=[],
    )


# =============================================================================
# ReportFormat Tests
# =============================================================================


class TestReportFormat:
    """Tests for ReportFormat enum."""

    def test_format_values(self):
        """Test format enum values."""
        assert ReportFormat.MARKDOWN.value == "markdown"
        assert ReportFormat.TEXT.value == "text"
        assert ReportFormat.JSON.value == "json"
        assert ReportFormat.CONSOLE.value == "console"


# =============================================================================
# ReportConfig Tests
# =============================================================================


class TestReportConfig:
    """Tests for ReportConfig dataclass."""

    def test_default_config(self):
        """Test default configuration."""
        config = ReportConfig()
        assert config.format == ReportFormat.MARKDOWN
        assert config.include_warnings is True
        assert config.include_fair_values is True
        assert config.max_positions_detail == 50

    def test_custom_config(self):
        """Test custom configuration."""
        config = ReportConfig(
            format=ReportFormat.TEXT,
            include_methodology=True,
            max_positions_detail=10,
        )
        assert config.format == ReportFormat.TEXT
        assert config.include_methodology is True
        assert config.max_positions_detail == 10


# =============================================================================
# format_position_row Tests
# =============================================================================


class TestFormatPositionRow:
    """Tests for format_position_row function."""

    def test_buy_position_row(self, sample_buy_position):
        """Test formatting buy position."""
        row = format_position_row(sample_buy_position)
        assert "BATS.L" in row
        assert "+62.6%" in row
        assert "🟢🟢" in row
        assert "✓" in row  # No warnings

    def test_sell_position_with_warnings(self, sample_sell_position):
        """Test formatting sell position with warnings."""
        row = format_position_row(sample_sell_position)
        assert "HOOD" in row
        assert "-113.7%" in row
        assert "🔴🔴" in row
        assert "⚠️" in row  # Has warnings

    def test_row_is_markdown_table(self, sample_buy_position):
        """Test row format is valid markdown."""
        row = format_position_row(sample_buy_position)
        assert row.startswith("|")
        assert row.endswith("|")
        assert row.count("|") >= 5


# =============================================================================
# format_position_detail Tests
# =============================================================================


class TestFormatPositionDetail:
    """Tests for format_position_detail function."""

    def test_detail_includes_ticker(self, sample_buy_position):
        """Test detail includes ticker."""
        detail = format_position_detail(sample_buy_position)
        assert "BATS.L" in detail
        assert "### 1. BATS.L" in detail

    def test_detail_includes_scenarios(self, sample_buy_position):
        """Test detail includes fair value scenarios."""
        detail = format_position_detail(sample_buy_position)
        assert "Bear Case" in detail
        assert "Bull Case" in detail
        assert "Midpoint" in detail

    def test_detail_shows_warnings(self, sample_sell_position):
        """Test detail shows warnings when present."""
        detail = format_position_detail(sample_sell_position)
        assert "⚠️ Warnings" in detail
        assert "Extreme negative compression" in detail


# =============================================================================
# generate_summary Tests
# =============================================================================


class TestGenerateSummary:
    """Tests for generate_summary function."""

    def test_summary_includes_portfolio_name(self, sample_ranking_result):
        """Test summary includes portfolio name."""
        summary = generate_summary(sample_ranking_result)
        assert "Test Portfolio" in summary

    def test_summary_includes_counts(self, sample_ranking_result):
        """Test summary includes signal counts."""
        summary = generate_summary(sample_ranking_result)
        assert "1" in summary  # Buy count
        assert "Buy Signals" in summary
        assert "Sell Signals" in summary

    def test_summary_has_immediate_actions(self, sample_ranking_result):
        """Test summary has immediate actions section."""
        summary = generate_summary(sample_ranking_result)
        assert "Immediate Actions" in summary
        assert "SELL" in summary
        assert "BUY" in summary


# =============================================================================
# Section Generator Tests
# =============================================================================


class TestSectionGenerators:
    """Tests for section generation functions."""

    def test_buy_section(self, sample_buy_position):
        """Test buy section generation."""
        section = generate_buy_section([sample_buy_position])
        assert "Buy Opportunities" in section
        assert "BATS.L" in section

    def test_sell_section(self, sample_sell_position):
        """Test sell section generation."""
        section = generate_sell_section([sample_sell_position])
        assert "Sell Signals" in section
        assert "HOOD" in section

    def test_hold_section(self, sample_hold_position):
        """Test hold section generation."""
        section = generate_hold_section([sample_hold_position])
        assert "Hold Positions" in section
        assert "AAPL" in section

    def test_empty_buy_section(self):
        """Test empty buy section."""
        section = generate_buy_section([])
        assert "No buy signals" in section

    def test_empty_sell_section(self):
        """Test empty sell section."""
        section = generate_sell_section([])
        assert "No sell signals" in section

    def test_methodology_section(self):
        """Test methodology section."""
        section = generate_methodology_section()
        assert "P/E Compression" in section
        assert "Formula" in section
        assert "Fair Value" in section


class TestWarningsSection:
    """Tests for warnings section generation."""

    def test_no_warnings(self, sample_buy_position):
        """Test no warnings message."""
        result = RankingResult(
            portfolio_name="Test",
            total_positions=1,
            ranked_positions=[sample_buy_position],
        )
        section = generate_warnings_section(result)
        assert "No data quality issues" in section

    def test_with_warnings(self, sample_sell_position):
        """Test warnings are shown."""
        result = RankingResult(
            portfolio_name="Test",
            total_positions=1,
            ranked_positions=[sample_sell_position],
        )
        section = generate_warnings_section(result)
        assert "HOOD" in section
        assert "Extreme negative compression" in section


# =============================================================================
# generate_report Tests
# =============================================================================


class TestGenerateReport:
    """Tests for generate_report function."""

    def test_report_created(self, sample_ranking_result):
        """Test report is created."""
        report = generate_report(sample_ranking_result)
        assert isinstance(report, Report)
        assert report.title == "Test Portfolio Analysis Report"

    def test_report_has_content(self, sample_ranking_result):
        """Test report has content."""
        report = generate_report(sample_ranking_result)
        assert len(report.content) > 0
        assert "Test Portfolio" in report.content

    def test_report_has_stats(self, sample_ranking_result):
        """Test report has summary stats."""
        report = generate_report(sample_ranking_result)
        assert report.summary_stats["total"] == 3
        assert report.summary_stats["buy_count"] == 1
        assert report.summary_stats["sell_count"] == 1

    def test_report_has_sections(self, sample_ranking_result):
        """Test report has all sections."""
        report = generate_report(sample_ranking_result)
        assert "summary" in report.sections
        assert "buy" in report.sections
        assert "sell" in report.sections
        assert "hold" in report.sections

    def test_methodology_optional(self, sample_ranking_result):
        """Test methodology section is optional."""
        config = ReportConfig(include_methodology=False)
        report = generate_report(sample_ranking_result, config)
        assert "methodology" not in report.sections

        config = ReportConfig(include_methodology=True)
        report = generate_report(sample_ranking_result, config)
        assert "methodology" in report.sections


# =============================================================================
# save_report Tests
# =============================================================================


class TestSaveReport:
    """Tests for save_report function."""

    def test_save_markdown(self, sample_ranking_result, tmp_path):
        """Test saving markdown report."""
        report = generate_report(sample_ranking_result)
        output_path = tmp_path / "test_report"

        saved_path = save_report(report, output_path)

        assert saved_path.suffix == ".md"
        assert saved_path.exists()
        content = saved_path.read_text()
        assert "Test Portfolio" in content

    def test_save_json(self, sample_ranking_result, tmp_path):
        """Test saving JSON report."""
        config = ReportConfig(format=ReportFormat.JSON)
        report = generate_report(sample_ranking_result, config)
        output_path = tmp_path / "test_report"

        saved_path = save_report(report, output_path)

        assert saved_path.suffix == ".json"
        content = json.loads(saved_path.read_text())
        assert content["title"] == "Test Portfolio Analysis Report"

    def test_creates_directory(self, sample_ranking_result, tmp_path):
        """Test creates parent directory."""
        report = generate_report(sample_ranking_result)
        output_path = tmp_path / "subdir" / "test_report"

        saved_path = save_report(report, output_path)

        assert saved_path.exists()
        assert saved_path.parent.exists()


# =============================================================================
# generate_text_report Tests
# =============================================================================


class TestGenerateTextReport:
    """Tests for generate_text_report function."""

    def test_text_format(self, sample_ranking_result):
        """Test text report format."""
        text = generate_text_report(sample_ranking_result)
        assert "ANALYSIS REPORT" in text
        assert "=" * 60 in text
        assert "SUMMARY" in text

    def test_text_includes_positions(self, sample_ranking_result):
        """Test text includes position data."""
        text = generate_text_report(sample_ranking_result)
        assert "BATS.L" in text or "BUY OPPORTUNITIES" in text


# =============================================================================
# Report Dataclass Tests
# =============================================================================


class TestReport:
    """Tests for Report dataclass."""

    def test_report_creation(self):
        """Test basic report creation."""
        report = Report(
            title="Test Report",
            content="Test content",
        )
        assert report.title == "Test Report"
        assert report.content == "Test content"
        assert isinstance(report.generated_at, datetime)

    def test_report_save_method(self, tmp_path):
        """Test report save method."""
        report = Report(
            title="Test",
            content="Content",
        )
        path = report.save(tmp_path / "test.md")
        assert path.exists()


# =============================================================================
# PRD Examples Tests
# =============================================================================


class TestPRDExamples:
    """Tests verifying PRD requirements."""

    def test_prd_report_sections(self, sample_ranking_result):
        """Test report has required sections from PRD."""
        report = generate_report(sample_ranking_result)

        # PRD requires: summary, buy, sell, hold, warnings
        assert "summary" in report.sections
        assert "buy" in report.sections
        assert "sell" in report.sections
        assert "hold" in report.sections
        assert "warnings" in report.sections

    def test_prd_immediate_actions(self, sample_ranking_result):
        """Test immediate actions are highlighted."""
        summary = generate_summary(sample_ranking_result)
        assert "Immediate Actions" in summary

    def test_prd_compression_shown(self, sample_ranking_result):
        """Test compression percentages are shown."""
        report = generate_report(sample_ranking_result)
        assert "62.6%" in report.content or "+62.6%" in report.content

    def test_prd_fair_values_shown(self, sample_ranking_result):
        """Test fair value upside is shown."""
        report = generate_report(sample_ranking_result)
        # Bull upside for BATS.L
        assert "234" in report.content


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

