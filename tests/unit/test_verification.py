"""
Unit tests for Manual Verification Support Module
"""

import pytest
from datetime import datetime
from unittest.mock import Mock

from pe_scanner.verification import (
    STATUS_ICONS,
    VerificationCheck,
    VerificationChecklist,
    VerificationStatus,
    check_data_source,
    check_forward_eps,
    check_growth_realism,
    check_pe_ratio,
    check_stock_split,
    check_trailing_eps,
    create_verification_checklist,
    format_checklist_markdown,
    format_checklist_text,
    format_comparison_table,
    get_verification_summary,
    verify_batch,
)


# =============================================================================
# Helper to create mock MarketData
# =============================================================================


def create_mock_market_data(
    ticker: str = "TEST",
    current_price: float = 100.0,
    trailing_pe: float = 20.0,
    forward_pe: float = 15.0,
    trailing_eps: float = 5.0,
    forward_eps: float = 6.67,
) -> Mock:
    """Create a mock MarketData object for testing."""
    data = Mock()
    data.ticker = ticker
    data.current_price = current_price
    data.trailing_pe = trailing_pe
    data.forward_pe = forward_pe
    data.trailing_eps = trailing_eps
    data.forward_eps = forward_eps
    return data


# =============================================================================
# VerificationStatus Tests
# =============================================================================


class TestVerificationStatus:
    """Tests for VerificationStatus enum."""

    def test_status_values(self):
        """Test status enum values."""
        assert VerificationStatus.PASSED.value == "passed"
        assert VerificationStatus.WARNING.value == "warning"
        assert VerificationStatus.FAILED.value == "failed"
        assert VerificationStatus.SKIPPED.value == "skipped"
        assert VerificationStatus.PENDING.value == "pending"

    def test_status_icons(self):
        """Test status icons mapping."""
        assert STATUS_ICONS[VerificationStatus.PASSED] == "✅"
        assert STATUS_ICONS[VerificationStatus.WARNING] == "⚠️"
        assert STATUS_ICONS[VerificationStatus.FAILED] == "❌"
        assert STATUS_ICONS[VerificationStatus.SKIPPED] == "⏭️"
        assert STATUS_ICONS[VerificationStatus.PENDING] == "🔄"


# =============================================================================
# VerificationCheck Tests
# =============================================================================


class TestVerificationCheck:
    """Tests for VerificationCheck dataclass."""

    def test_basic_check(self):
        """Test basic check creation."""
        check = VerificationCheck(
            name="Test Check",
            description="A test check",
            status=VerificationStatus.PASSED,
        )

        assert check.name == "Test Check"
        assert check.status == VerificationStatus.PASSED
        assert check.icon == "✅"

    def test_check_with_values(self):
        """Test check with expected/actual values."""
        check = VerificationCheck(
            name="EPS Check",
            description="Compare EPS",
            status=VerificationStatus.WARNING,
            expected_value="$5.00",
            actual_value="$4.50",
            notes="10% deviation",
        )

        assert check.expected_value == "$5.00"
        assert check.actual_value == "$4.50"
        assert check.notes == "10% deviation"

    def test_to_row(self):
        """Test conversion to table row."""
        check = VerificationCheck(
            name="Test",
            description="Desc",
            status=VerificationStatus.PASSED,
            expected_value="100",
            actual_value="98",
            notes="Close match",
        )

        row = check.to_row()
        assert len(row) == 5
        assert row[0] == "✅"
        assert row[1] == "Test"


# =============================================================================
# VerificationChecklist Tests
# =============================================================================


class TestVerificationChecklist:
    """Tests for VerificationChecklist dataclass."""

    def test_empty_checklist(self):
        """Test empty checklist."""
        checklist = VerificationChecklist(ticker="TEST")

        assert checklist.ticker == "TEST"
        assert checklist.total_checks == 0
        assert checklist.passed_count == 0

    def test_add_checks(self):
        """Test adding checks."""
        checklist = VerificationChecklist(ticker="TEST")

        checklist.add_check(VerificationCheck(
            name="Check 1",
            description="First check",
            status=VerificationStatus.PASSED,
        ))
        checklist.add_check(VerificationCheck(
            name="Check 2",
            description="Second check",
            status=VerificationStatus.WARNING,
        ))

        assert checklist.total_checks == 2
        assert checklist.passed_count == 1
        assert checklist.warning_count == 1

    def test_determine_overall_status(self):
        """Test overall status determination."""
        checklist = VerificationChecklist(ticker="TEST")

        # All passed
        checklist.checks = [
            VerificationCheck(name="A", description="", status=VerificationStatus.PASSED),
            VerificationCheck(name="B", description="", status=VerificationStatus.PASSED),
        ]
        assert checklist.determine_overall_status() == VerificationStatus.PASSED

        # Has warning
        checklist.checks.append(
            VerificationCheck(name="C", description="", status=VerificationStatus.WARNING)
        )
        assert checklist.determine_overall_status() == VerificationStatus.WARNING

        # Has failure
        checklist.checks.append(
            VerificationCheck(name="D", description="", status=VerificationStatus.FAILED)
        )
        assert checklist.determine_overall_status() == VerificationStatus.FAILED

    def test_summary(self):
        """Test summary string."""
        checklist = VerificationChecklist(ticker="TEST")
        checklist.checks = [
            VerificationCheck(name="A", description="", status=VerificationStatus.PASSED),
            VerificationCheck(name="B", description="", status=VerificationStatus.PASSED),
            VerificationCheck(name="C", description="", status=VerificationStatus.WARNING),
        ]

        assert "2✅" in checklist.summary
        assert "1⚠️" in checklist.summary


# =============================================================================
# Individual Check Function Tests
# =============================================================================


class TestCheckTrailingEps:
    """Tests for check_trailing_eps function."""

    def test_no_trailing_eps(self):
        """Test when no trailing EPS data."""
        data = create_mock_market_data(trailing_eps=None)
        check = check_trailing_eps(data)

        assert check.status == VerificationStatus.SKIPPED

    def test_pending_without_reported(self):
        """Test pending status when no reported EPS."""
        data = create_mock_market_data(trailing_eps=5.0)
        check = check_trailing_eps(data)

        assert check.status == VerificationStatus.PENDING
        assert "Manual verification" in check.notes

    def test_passed_within_tolerance(self):
        """Test passed when within tolerance."""
        data = create_mock_market_data(trailing_eps=5.0)
        check = check_trailing_eps(data, reported_eps=5.1)

        assert check.status == VerificationStatus.PASSED

    def test_warning_moderate_deviation(self):
        """Test warning for moderate deviation."""
        data = create_mock_market_data(trailing_eps=5.0)
        check = check_trailing_eps(data, reported_eps=5.4)  # 8% deviation

        assert check.status == VerificationStatus.WARNING

    def test_failed_large_deviation(self):
        """Test failed for large deviation."""
        data = create_mock_market_data(trailing_eps=5.0)
        check = check_trailing_eps(data, reported_eps=6.0)  # 20% deviation

        assert check.status == VerificationStatus.FAILED


class TestCheckForwardEps:
    """Tests for check_forward_eps function."""

    def test_no_forward_eps(self):
        """Test when no forward EPS data."""
        data = create_mock_market_data(forward_eps=None)
        check = check_forward_eps(data)

        assert check.status == VerificationStatus.SKIPPED

    def test_passed_within_tolerance(self):
        """Test passed when within tolerance."""
        data = create_mock_market_data(forward_eps=6.0)
        check = check_forward_eps(data, analyst_consensus=6.3)  # 5% deviation

        assert check.status == VerificationStatus.PASSED


class TestCheckStockSplit:
    """Tests for check_stock_split function."""

    def test_no_eps_data(self):
        """Test when insufficient EPS data."""
        data = create_mock_market_data(trailing_eps=None)
        check = check_stock_split(data)

        assert check.status == VerificationStatus.SKIPPED

    def test_normal_growth_passed(self):
        """Test passed when normal growth."""
        data = create_mock_market_data(trailing_eps=5.0, forward_eps=5.5)  # 10% growth
        check = check_stock_split(data)

        assert check.status == VerificationStatus.PASSED

    def test_extreme_growth_warning(self):
        """Test warning for extreme growth."""
        data = create_mock_market_data(trailing_eps=5.0, forward_eps=15.0)  # 200% growth
        check = check_stock_split(data)

        assert check.status == VerificationStatus.WARNING
        assert "split" in check.notes.lower()

    def test_known_split_info(self):
        """Test with known split information."""
        data = create_mock_market_data(trailing_eps=5.0, forward_eps=15.0)
        check = check_stock_split(data, known_split="10:1 on 2024-01-15")

        assert check.status == VerificationStatus.WARNING
        assert "Known split" in check.notes


class TestCheckGrowthRealism:
    """Tests for check_growth_realism function."""

    def test_realistic_growth_passed(self):
        """Test passed for realistic growth."""
        data = create_mock_market_data(trailing_eps=5.0, forward_eps=6.0)  # 20% growth
        check = check_growth_realism(data)

        assert check.status == VerificationStatus.PASSED

    def test_high_growth_warning(self):
        """Test warning for high growth."""
        data = create_mock_market_data(trailing_eps=5.0, forward_eps=8.0)  # 60% growth
        check = check_growth_realism(data)

        assert check.status == VerificationStatus.WARNING

    def test_with_industry_comparison(self):
        """Test with industry average comparison."""
        data = create_mock_market_data(trailing_eps=5.0, forward_eps=5.5)  # 10% growth
        check = check_growth_realism(data, industry_avg_growth=8.0)

        assert check.status == VerificationStatus.PASSED


class TestCheckPeRatio:
    """Tests for check_pe_ratio function."""

    def test_no_pe_data(self):
        """Test when no P/E data."""
        data = create_mock_market_data(trailing_pe=None)
        check = check_pe_ratio(data)

        assert check.status == VerificationStatus.SKIPPED

    def test_pending_without_sector(self):
        """Test pending when no sector P/E."""
        data = create_mock_market_data(trailing_pe=20.0)
        check = check_pe_ratio(data)

        assert check.status == VerificationStatus.PENDING

    def test_passed_close_to_sector(self):
        """Test passed when close to sector average."""
        data = create_mock_market_data(trailing_pe=20.0)
        check = check_pe_ratio(data, sector_avg_pe=22.0)

        assert check.status == VerificationStatus.PASSED


class TestCheckDataSource:
    """Tests for check_data_source function."""

    def test_pending_without_alternative(self):
        """Test pending when no alternative source."""
        data = create_mock_market_data()
        check = check_data_source(data)

        assert check.status == VerificationStatus.PENDING

    def test_passed_consistent_data(self):
        """Test passed when data is consistent."""
        data = create_mock_market_data(current_price=100.0, trailing_pe=20.0)
        alt_source = {"price": 100.5, "pe": 20.5, "source": "Bloomberg"}
        check = check_data_source(data, alternative_source=alt_source)

        assert check.status == VerificationStatus.PASSED

    def test_warning_mismatched_data(self):
        """Test warning when data mismatches."""
        data = create_mock_market_data(current_price=100.0, trailing_pe=20.0)
        alt_source = {"price": 110.0, "pe": 25.0, "source": "Bloomberg"}
        check = check_data_source(data, alternative_source=alt_source)

        assert check.status == VerificationStatus.WARNING


# =============================================================================
# create_verification_checklist Tests
# =============================================================================


class TestCreateVerificationChecklist:
    """Tests for create_verification_checklist function."""

    def test_creates_all_checks(self):
        """Test that all standard checks are created."""
        data = create_mock_market_data()
        checklist = create_verification_checklist(data)

        assert checklist.ticker == "TEST"
        assert checklist.total_checks == 6  # All standard checks

    def test_with_manual_data(self):
        """Test with manual verification data."""
        data = create_mock_market_data(trailing_eps=5.0)
        manual_data = {"reported_eps": 5.1}
        checklist = create_verification_checklist(data, manual_data=manual_data)

        # Should have a passed trailing EPS check
        trailing_check = next(c for c in checklist.checks if c.name == "Trailing EPS")
        assert trailing_check.status == VerificationStatus.PASSED

    def test_overall_status_determined(self):
        """Test that overall status is determined based on checks."""
        data = create_mock_market_data()
        checklist = create_verification_checklist(data)

        # Without manual data, status should be PENDING (many checks need verification)
        # The checklist should have 2 passed checks (split, growth) and 4 pending
        assert checklist.passed_count >= 2  # Split check and growth realism pass
        assert checklist.overall_status in (
            VerificationStatus.PENDING,  # When most checks need manual verification
            VerificationStatus.PASSED,    # If all checks pass
            VerificationStatus.WARNING,   # If any warnings
        )


# =============================================================================
# Output Formatter Tests
# =============================================================================


class TestFormatChecklistMarkdown:
    """Tests for format_checklist_markdown function."""

    def test_markdown_format(self):
        """Test markdown output format."""
        data = create_mock_market_data()
        checklist = create_verification_checklist(data)
        md = format_checklist_markdown(checklist)

        assert "## Verification Checklist: TEST" in md
        assert "| Status | Check |" in md
        assert "Overall Status:" in md


class TestFormatChecklistText:
    """Tests for format_checklist_text function."""

    def test_text_format(self):
        """Test text output format."""
        data = create_mock_market_data()
        checklist = create_verification_checklist(data)
        text = format_checklist_text(checklist)

        assert "=== Verification Checklist: TEST ===" in text
        assert "Overall:" in text


class TestFormatComparisonTable:
    """Tests for format_comparison_table function."""

    def test_comparison_table(self):
        """Test comparison table format."""
        data = create_mock_market_data(
            current_price=100.0,
            trailing_pe=20.0,
            trailing_eps=5.0,
            forward_eps=6.0,
        )
        manual_data = {
            "price": 101.0,
            "pe": 20.5,
            "reported_eps": 5.1,
            "analyst_consensus": 6.2,
        }
        table = format_comparison_table(data, manual_data)

        assert "## Data Comparison: TEST" in table
        assert "| Current Price |" in table
        assert "| Trailing P/E |" in table


# =============================================================================
# Batch Verification Tests
# =============================================================================


class TestVerifyBatch:
    """Tests for verify_batch function."""

    def test_batch_verification(self):
        """Test batch verification."""
        data_list = [
            create_mock_market_data(ticker="A"),
            create_mock_market_data(ticker="B"),
            create_mock_market_data(ticker="C"),
        ]

        checklists = verify_batch(data_list)

        assert len(checklists) == 3
        assert checklists[0].ticker == "A"
        assert checklists[1].ticker == "B"
        assert checklists[2].ticker == "C"

    def test_batch_with_manual_data(self):
        """Test batch with manual data mapping."""
        data_list = [
            create_mock_market_data(ticker="A", trailing_eps=5.0),
            create_mock_market_data(ticker="B", trailing_eps=10.0),
        ]
        manual_data_map = {
            "A": {"reported_eps": 5.1},
            "B": {"reported_eps": 10.0},
        }

        checklists = verify_batch(data_list, manual_data_map)

        # Both should have passed trailing EPS checks
        for checklist in checklists:
            trailing_check = next(c for c in checklist.checks if c.name == "Trailing EPS")
            assert trailing_check.status == VerificationStatus.PASSED


class TestGetVerificationSummary:
    """Tests for get_verification_summary function."""

    def test_summary_counts(self):
        """Test summary produces correct counts."""
        checklists = [
            VerificationChecklist(ticker="A", overall_status=VerificationStatus.PASSED),
            VerificationChecklist(ticker="B", overall_status=VerificationStatus.WARNING),
            VerificationChecklist(ticker="C", overall_status=VerificationStatus.FAILED),
        ]

        summary = get_verification_summary(checklists)

        assert summary["total"] == 3
        assert summary["passed"] == 1
        assert summary["warning"] == 1
        assert summary["failed"] == 1
        assert "B" in summary["needs_review"]
        assert "C" in summary["needs_review"]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

