"""
End-to-End Integration Tests

Tests the complete analysis pipeline from portfolio loading through report generation.
These tests verify all modules work together correctly.
"""

import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock
from datetime import datetime

from pe_scanner.portfolios.loader import (
    Portfolio,
    Position,
    PortfolioType,
    load_portfolio,
)
from pe_scanner.data.fetcher import (
    MarketData,
    FetchResult,
    batch_fetch,
)
from pe_scanner.data.corrector import apply_corrections
from pe_scanner.data.validator import validate_market_data, DataQualityLevel
from pe_scanner.analysis.compression import (
    analyze_compression,
    CompressionSignal,
    CompressionResult,
)
from pe_scanner.analysis.fair_value import analyze_fair_value, FairValueResult
from pe_scanner.portfolios.ranker import rank_portfolio, Signal
from pe_scanner.portfolios.reporter import generate_report, ReportConfig
from pe_scanner.integration.hooks import run_hooks


# =============================================================================
# Test Fixtures
# =============================================================================


@pytest.fixture
def sample_portfolio():
    """Create a realistic portfolio for testing."""
    return Portfolio(
        name="Test ISA",
        portfolio_type=PortfolioType.ISA,
        positions=[
            Position(ticker="AAPL", shares=100, cost_basis=150.0),
            Position(ticker="MSFT", shares=50, cost_basis=300.0),
            Position(ticker="GOOGL", shares=25, cost_basis=2800.0),
        ],
    )


@pytest.fixture
def sample_market_data():
    """Create sample market data for testing."""
    return {
        "AAPL": MarketData(
            ticker="AAPL",
            company_name="Apple Inc.",
            current_price=175.50,
            trailing_pe=28.5,
            forward_pe=24.0,
            trailing_eps=6.16,
            forward_eps=7.31,
            market_cap=2.75e12,
            currency="USD",
            last_updated=datetime.now(),
        ),
        "MSFT": MarketData(
            ticker="MSFT",
            company_name="Microsoft Corporation",
            current_price=380.00,
            trailing_pe=35.0,
            forward_pe=30.0,
            trailing_eps=10.86,
            forward_eps=12.67,
            market_cap=2.83e12,
            currency="USD",
            last_updated=datetime.now(),
        ),
        "GOOGL": MarketData(
            ticker="GOOGL",
            company_name="Alphabet Inc.",
            current_price=140.00,
            trailing_pe=25.0,
            forward_pe=22.0,
            trailing_eps=5.60,
            forward_eps=6.36,
            market_cap=1.77e12,
            currency="USD",
            last_updated=datetime.now(),
        ),
    }


# =============================================================================
# Pipeline Stage Tests
# =============================================================================


class TestDataCorrectionPipeline:
    """Test data correction stage."""

    def test_corrections_preserve_valid_data(self, sample_market_data):
        """Test that valid data passes through corrections unchanged."""
        md = sample_market_data["AAPL"]
        corrected, result = apply_corrections(md)

        assert corrected.ticker == md.ticker
        assert corrected.trailing_pe == md.trailing_pe
        assert not result.was_corrected  # No corrections needed

    def test_uk_stock_correction_applied(self):
        """Test UK stock pence-to-pounds correction."""
        uk_data = MarketData(
            ticker="BATS.L",
            company_name="BAT plc",
            current_price=28.50,  # In pounds
            trailing_pe=9.5,
            forward_pe=0.085,  # Incorrectly in pence
            trailing_eps=3.0,
            forward_eps=0.003,  # Incorrectly in pence
        )

        corrected, result = apply_corrections(uk_data)

        # Forward P/E should be corrected (multiplied by 100)
        assert result.was_corrected
        assert corrected.forward_pe > 1.0


class TestValidationPipeline:
    """Test data validation stage."""

    def test_valid_data_passes(self, sample_market_data):
        """Test valid data passes validation."""
        md = sample_market_data["AAPL"]
        result = validate_market_data(md)

        assert result.quality_level in (DataQualityLevel.VERIFIED, DataQualityLevel.ACCEPTABLE)
        assert result.confidence_score >= 0.7

    def test_missing_data_flagged(self):
        """Test missing critical data is flagged."""
        incomplete = MarketData(
            ticker="TEST",
            current_price=100.0,
            # Missing P/E ratios
        )
        result = validate_market_data(incomplete)

        assert result.quality_level in (DataQualityLevel.SUSPICIOUS, DataQualityLevel.UNRELIABLE)


class TestCompressionAnalysisPipeline:
    """Test compression analysis stage."""

    def test_compression_calculated(self, sample_market_data):
        """Test compression is calculated correctly."""
        md = sample_market_data["AAPL"]
        # Use the function signature: ticker, trailing_pe, forward_pe, trailing_eps, forward_eps
        result = analyze_compression(
            md.ticker, md.trailing_pe, md.forward_pe, md.trailing_eps, md.forward_eps
        )

        # AAPL: trailing 28.5, forward 24.0 = positive compression (P/E shrinking)
        assert result.compression_pct > 0
        assert result.signal in (CompressionSignal.BUY, CompressionSignal.STRONG_BUY, CompressionSignal.HOLD)

    def test_prd_example_hood(self):
        """Test HOOD example from PRD: -113.70% compression."""
        # Use the function signature: ticker, trailing_pe, forward_pe, trailing_eps, forward_eps
        result = analyze_compression(
            "HOOD", 73.27, 156.58, 0.14, 0.07
        )

        # Should show significant negative compression
        assert result.compression_pct < -100
        assert result.signal in (CompressionSignal.SELL, CompressionSignal.STRONG_SELL)


class TestFairValuePipeline:
    """Test fair value calculation stage."""

    def test_fair_value_calculated(self, sample_market_data):
        """Test fair values are calculated."""
        md = sample_market_data["AAPL"]
        # Use the function signature: ticker, current_price, forward_eps
        result = analyze_fair_value(md.ticker, md.current_price, md.forward_eps)

        assert result.bear_fair_value > 0
        assert result.bull_fair_value > result.bear_fair_value


# =============================================================================
# Full Pipeline Tests
# =============================================================================


class TestFullPipeline:
    """Test complete end-to-end pipeline."""

    def test_full_analysis_pipeline(self, sample_portfolio, sample_market_data):
        """Test complete pipeline from portfolio to report."""
        # 1. Validate portfolio with hooks
        hook_results, has_failures = run_hooks(portfolio=sample_portfolio)
        assert not has_failures

        # 2. Apply corrections
        corrected_data = {}
        for ticker, md in sample_market_data.items():
            corrected, _ = apply_corrections(md)
            corrected_data[ticker] = corrected

        # 3. Validate data
        validation_results = []
        for ticker, md in corrected_data.items():
            validation_results.append(validate_market_data(md))

        # 4. Analyze compression
        compression_results = []
        for ticker, md in corrected_data.items():
            comp = analyze_compression(
                md.ticker, md.trailing_pe, md.forward_pe, md.trailing_eps, md.forward_eps
            )
            compression_results.append(comp)

        # 5. Calculate fair values
        fair_value_results = []
        for ticker, md in corrected_data.items():
            if md.current_price and md.forward_eps:
                fv = analyze_fair_value(md.ticker, md.current_price, md.forward_eps)
                fair_value_results.append(fv)

        # 6. Rank portfolio
        ranking = rank_portfolio(
            compression_results,
            fair_value_results,
            validation_results,
            sample_portfolio.name,
        )

        assert ranking is not None
        assert ranking.total_positions == 3

        # 7. Generate report
        report = generate_report(ranking, ReportConfig(include_methodology=True))

        assert report is not None
        assert len(report.content) > 100


class TestPrdExamples:
    """Test examples from the PRD document."""

    def test_hood_sell_signal(self):
        """Test HOOD produces sell signal as per PRD."""
        # Use the function signature: ticker, trailing_pe, forward_pe, trailing_eps, forward_eps
        compression = analyze_compression("HOOD", 73.27, 156.58, 0.14, 0.07)

        # PRD states: -113.70% to -228.77% compression = confirmed sell
        assert compression.compression_pct < -100
        assert compression.signal in (CompressionSignal.SELL, CompressionSignal.STRONG_SELL)

    def test_uk_stock_correction(self):
        """Test UK stocks get 100x correction as per PRD."""
        bats = MarketData(
            ticker="BATS.L",
            company_name="British American Tobacco",
            current_price=28.50,
            trailing_pe=9.5,
            forward_pe=0.085,  # Pence-denominated error
            trailing_eps=3.0,
            forward_eps=0.003,  # Pence-denominated error
        )

        corrected, result = apply_corrections(bats)

        # PRD: If forward P/E < 1.0, apply 100x correction
        assert result.was_corrected
        assert corrected.forward_pe > 1.0


# =============================================================================
# Edge Case Tests
# =============================================================================


class TestEdgeCases:
    """Test edge cases and boundary conditions."""

    def test_empty_portfolio(self):
        """Test handling of empty portfolio."""
        empty = Portfolio(
            name="Empty",
            portfolio_type=PortfolioType.CUSTOM,
            positions=[],
        )

        hook_results, has_failures = run_hooks(portfolio=empty)
        assert has_failures  # Should fail validation

    def test_zero_pe_handling(self):
        """Test handling of zero P/E ratio."""
        zero_pe = MarketData(
            ticker="TEST",
            current_price=100.0,
            trailing_pe=0.0,
            forward_pe=15.0,
        )

        validation = validate_market_data(zero_pe)
        # Should flag as suspicious
        assert validation.quality_level in (DataQualityLevel.SUSPICIOUS, DataQualityLevel.UNRELIABLE)

    def test_negative_pe_handling(self):
        """Test handling of negative P/E (loss-making company)."""
        negative_pe = MarketData(
            ticker="LOSS",
            current_price=50.0,
            trailing_pe=-10.0,  # Loss-making
            forward_pe=25.0,  # Expected to become profitable
            trailing_eps=-5.0,
            forward_eps=2.0,
        )

        validation = validate_market_data(negative_pe)

        # Compression should handle gracefully even with negative P/E
        # The function will warn about negative trailing P/E
        compression = analyze_compression(
            "LOSS", -10.0, 25.0, -5.0, 2.0
        )
        assert compression is not None

    def test_missing_forward_data(self):
        """Test handling of missing forward estimates."""
        no_forward = MarketData(
            ticker="OLD",
            current_price=75.0,
            trailing_pe=20.0,
            # No forward P/E or EPS
        )

        validation = validate_market_data(no_forward)
        # Should flag missing forward data
        assert validation.quality_level != DataQualityLevel.VERIFIED


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

