"""
Unit tests for Integration Module (Momentum_Squared and diet103 hooks)
"""

import pytest
from pathlib import Path
from datetime import datetime

from pe_scanner.portfolios.loader import Portfolio, Position, PortfolioType
from pe_scanner.integration.hooks import (
    Hook,
    HookResult,
    HookStatus,
    HookType,
    HooksManager,
    DataQualityGuardian,
    PortfolioSyncValidator,
    PreAnalysisValidator,
    ResultsValidator,
    run_hooks,
)
from pe_scanner.integration.momentum_squared import (
    validate_momentum_squared_format,
    load_momentum_squared_portfolio,
    sync_with_master,
    export_to_momentum_squared,
    _calculate_portfolio_hash,
)


# =============================================================================
# Test Fixtures
# =============================================================================


@pytest.fixture
def sample_portfolio():
    """Create a sample portfolio."""
    return Portfolio(
        name="Test Portfolio",
        portfolio_type=PortfolioType.ISA,
        positions=[
            Position(ticker="AAPL", shares=100, cost_basis=150.0),
            Position(ticker="MSFT", shares=50, cost_basis=300.0),
            Position(ticker="GOOGL", shares=25, cost_basis=2800.0),
        ],
    )


@pytest.fixture
def empty_portfolio():
    """Create an empty portfolio."""
    return Portfolio(
        name="Empty",
        portfolio_type=PortfolioType.CUSTOM,
        positions=[],
    )


@pytest.fixture
def sample_csv(tmp_path):
    """Create a sample CSV file."""
    csv_path = tmp_path / "test_portfolio.csv"
    csv_path.write_text("""ticker,shares,cost_basis
AAPL,100,150.00
MSFT,50,300.00
GOOGL,25,2800.00
""")
    return csv_path


# =============================================================================
# HookResult Tests
# =============================================================================


class TestHookResult:
    """Tests for HookResult dataclass."""

    def test_passed_result(self):
        """Test passed result."""
        result = HookResult(
            hook_name="Test",
            hook_type=HookType.PRE_ANALYSIS,
            status=HookStatus.PASSED,
            message="All good",
        )
        assert result.status == HookStatus.PASSED
        assert not result.is_blocking
        assert "✅" in str(result)

    def test_failed_result_is_blocking(self):
        """Test failed result blocks execution."""
        result = HookResult(
            hook_name="Test",
            hook_type=HookType.DATA_QUALITY,
            status=HookStatus.FAILED,
            message="Critical error",
        )
        assert result.is_blocking

    def test_warning_not_blocking(self):
        """Test warning does not block."""
        result = HookResult(
            hook_name="Test",
            hook_type=HookType.DATA_QUALITY,
            status=HookStatus.WARNING,
            message="Minor issue",
        )
        assert not result.is_blocking


# =============================================================================
# PreAnalysisValidator Tests
# =============================================================================


class TestPreAnalysisValidator:
    """Tests for PreAnalysisValidator hook."""

    def test_valid_portfolio(self, sample_portfolio):
        """Test validation of valid portfolio."""
        validator = PreAnalysisValidator()
        result = validator.validate(sample_portfolio)
        assert result.status == HookStatus.PASSED

    def test_empty_portfolio_fails(self, empty_portfolio):
        """Test empty portfolio fails validation."""
        validator = PreAnalysisValidator()
        result = validator.validate(empty_portfolio)
        assert result.status == HookStatus.FAILED
        assert "no positions" in result.message.lower()

    def test_none_portfolio_fails(self):
        """Test None portfolio fails."""
        validator = PreAnalysisValidator()
        result = validator.validate(None)
        assert result.status == HookStatus.FAILED

    def test_duplicate_tickers_warning(self):
        """Test duplicate tickers generate warning."""
        portfolio = Portfolio(
            name="Dupes",
            portfolio_type=PortfolioType.ISA,
            positions=[
                Position(ticker="AAPL", shares=100, cost_basis=150.0),
                Position(ticker="AAPL", shares=50, cost_basis=155.0),
            ],
        )
        validator = PreAnalysisValidator()
        result = validator.validate(portfolio)
        assert result.status == HookStatus.WARNING
        assert "duplicate" in result.message.lower() or "AAPL" in str(result.details)


# =============================================================================
# DataQualityGuardian Tests
# =============================================================================


class TestDataQualityGuardian:
    """Tests for DataQualityGuardian hook."""

    def test_disabled_hook_skips(self):
        """Test disabled hook skips."""
        guardian = DataQualityGuardian()
        guardian.enabled = False
        result = guardian.validate(([], []))
        assert result.status == HookStatus.SKIPPED


# =============================================================================
# ResultsValidator Tests
# =============================================================================


class TestResultsValidator:
    """Tests for ResultsValidator hook."""

    def test_disabled_hook_skips(self):
        """Test disabled hook skips."""
        validator = ResultsValidator()
        validator.enabled = False
        result = validator.validate(None)
        assert result.status == HookStatus.SKIPPED


# =============================================================================
# HooksManager Tests
# =============================================================================


class TestHooksManager:
    """Tests for HooksManager."""

    def test_register_hook(self):
        """Test registering hooks."""
        manager = HooksManager()
        manager.register(PreAnalysisValidator())
        assert len(manager.hooks[HookType.PRE_ANALYSIS]) == 1

    def test_register_defaults(self):
        """Test default hooks registration."""
        manager = HooksManager()
        manager.register_defaults()
        assert len(manager.hooks[HookType.PRE_ANALYSIS]) >= 1
        assert len(manager.hooks[HookType.DATA_QUALITY]) >= 1
        assert len(manager.hooks[HookType.RESULTS]) >= 1

    def test_run_hooks(self, sample_portfolio):
        """Test running hooks."""
        manager = HooksManager()
        manager.register_defaults()
        results = manager.run(HookType.PRE_ANALYSIS, sample_portfolio)
        assert len(results) >= 1

    def test_get_summary(self, sample_portfolio):
        """Test summary generation."""
        manager = HooksManager()
        manager.register_defaults()
        manager.run_all(portfolio=sample_portfolio)
        summary = manager.get_summary()
        assert "total" in summary
        assert "passed" in summary

    def test_has_blocking_failures(self, empty_portfolio):
        """Test blocking failure detection."""
        manager = HooksManager()
        manager.register_defaults()
        manager.run_all(portfolio=empty_portfolio)
        assert manager.has_blocking_failures()


# =============================================================================
# run_hooks Convenience Function Tests
# =============================================================================


class TestRunHooks:
    """Tests for run_hooks convenience function."""

    def test_run_hooks_returns_results(self, sample_portfolio):
        """Test run_hooks returns results."""
        results, has_failures = run_hooks(portfolio=sample_portfolio)
        assert isinstance(results, list)
        assert isinstance(has_failures, bool)


# =============================================================================
# Momentum_Squared Format Tests
# =============================================================================


class TestMomentumSquaredFormat:
    """Tests for Momentum_Squared CSV format."""

    def test_validate_valid_csv(self, sample_csv):
        """Test validation of valid CSV."""
        is_valid, issues = validate_momentum_squared_format(sample_csv)
        assert is_valid
        assert len(issues) == 0

    def test_validate_missing_file(self, tmp_path):
        """Test validation of missing file."""
        is_valid, issues = validate_momentum_squared_format(tmp_path / "nonexistent.csv")
        assert not is_valid
        assert "not found" in issues[0].lower()

    def test_validate_wrong_extension(self, tmp_path):
        """Test validation of wrong file extension."""
        txt_path = tmp_path / "test.txt"
        txt_path.write_text("ticker,shares\nAAPL,100")
        is_valid, issues = validate_momentum_squared_format(txt_path)
        assert not is_valid

    def test_validate_missing_columns(self, tmp_path):
        """Test validation with missing columns."""
        csv_path = tmp_path / "bad.csv"
        csv_path.write_text("name,quantity\nApple,100")
        is_valid, issues = validate_momentum_squared_format(csv_path)
        assert not is_valid
        assert any("ticker" in issue.lower() for issue in issues)


# =============================================================================
# Portfolio Loading Tests
# =============================================================================


class TestLoadMomentumSquaredPortfolio:
    """Tests for loading Momentum_Squared portfolios."""

    def test_load_valid_csv(self, sample_csv):
        """Test loading valid CSV."""
        portfolio = load_momentum_squared_portfolio(sample_csv)
        assert portfolio is not None
        assert len(portfolio.positions) == 3
        assert portfolio.positions[0].ticker == "AAPL"

    def test_load_with_type_override(self, sample_csv):
        """Test loading with portfolio type override."""
        portfolio = load_momentum_squared_portfolio(sample_csv, PortfolioType.SIPP)
        assert portfolio.portfolio_type == PortfolioType.SIPP

    def test_load_infers_type_from_filename(self, tmp_path):
        """Test type inference from filename."""
        isa_csv = tmp_path / "my_isa_portfolio.csv"
        isa_csv.write_text("ticker,shares\nAAPL,100")
        portfolio = load_momentum_squared_portfolio(isa_csv)
        assert portfolio.portfolio_type == PortfolioType.ISA


# =============================================================================
# Sync Tests
# =============================================================================


class TestPortfolioSync:
    """Tests for portfolio synchronization."""

    def test_hash_calculation(self, sample_portfolio):
        """Test hash is calculated consistently."""
        hash1 = _calculate_portfolio_hash(sample_portfolio)
        hash2 = _calculate_portfolio_hash(sample_portfolio)
        assert hash1 == hash2
        assert len(hash1) == 32  # MD5 hex length

    def test_sync_with_nonexistent_master(self, sample_portfolio, tmp_path):
        """Test sync with missing master file."""
        status = sync_with_master(sample_portfolio, tmp_path / "nonexistent.csv")
        assert not status.in_sync
        assert status.master_hash is None

    def test_sync_with_matching_master(self, sample_csv, tmp_path):
        """Test sync with matching master."""
        portfolio = load_momentum_squared_portfolio(sample_csv)
        status = sync_with_master(portfolio, sample_csv)
        assert status.in_sync


# =============================================================================
# Export Tests
# =============================================================================


class TestExportToMomentumSquared:
    """Tests for exporting to Momentum_Squared format."""

    def test_export_creates_file(self, sample_portfolio, tmp_path):
        """Test export creates CSV file."""
        output_path = tmp_path / "exported.csv"
        result = export_to_momentum_squared(sample_portfolio, output_path)
        assert result.exists()
        assert result.suffix == ".csv"

    def test_export_roundtrip(self, sample_portfolio, tmp_path):
        """Test export and reload produces same data."""
        output_path = tmp_path / "roundtrip.csv"
        export_to_momentum_squared(sample_portfolio, output_path)
        loaded = load_momentum_squared_portfolio(output_path)
        assert len(loaded.positions) == len(sample_portfolio.positions)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

