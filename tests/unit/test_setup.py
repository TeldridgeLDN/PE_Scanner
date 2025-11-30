"""
Setup verification tests.

These tests verify that the project environment is correctly configured
and all modules can be imported without errors.
"""

import pytest


class TestPackageImports:
    """Test that all package modules can be imported."""

    def test_import_main_package(self) -> None:
        """Test importing the main pe_scanner package."""
        import pe_scanner

        assert pe_scanner.__version__ == "0.1.0"
        assert pe_scanner.__author__ == "Tom Eldridge"

    def test_import_analysis_module(self) -> None:
        """Test importing the analysis submodule."""
        from pe_scanner import analysis

        # Check key exports exist
        assert hasattr(analysis, "CompressionResult")
        assert hasattr(analysis, "CompressionSignal")
        assert hasattr(analysis, "calculate_compression")
        assert hasattr(analysis, "FairValueResult")
        assert hasattr(analysis, "calculate_fair_values")

    def test_import_data_module(self) -> None:
        """Test importing the data submodule."""
        from pe_scanner import data

        # Check key exports exist
        assert hasattr(data, "MarketData")
        assert hasattr(data, "fetch_market_data")
        assert hasattr(data, "ValidationResult")
        assert hasattr(data, "CorrectionResult")
        assert hasattr(data, "is_uk_stock")

    def test_import_portfolios_module(self) -> None:
        """Test importing the portfolios submodule."""
        from pe_scanner import portfolios

        # Check key exports exist
        assert hasattr(portfolios, "Portfolio")
        assert hasattr(portfolios, "Position")
        assert hasattr(portfolios, "load_portfolio")
        assert hasattr(portfolios, "RankedPosition")
        assert hasattr(portfolios, "Report")


class TestDataClasses:
    """Test that data classes are properly defined."""

    def test_market_data_creation(self) -> None:
        """Test MarketData dataclass can be instantiated."""
        from pe_scanner.data.fetcher import MarketData

        data = MarketData(ticker="AAPL")
        assert data.ticker == "AAPL"
        assert data.current_price is None
        assert data.data_source == "yahoo_finance"

    def test_position_creation(self) -> None:
        """Test Position dataclass can be instantiated."""
        from pe_scanner.portfolios.loader import Position

        pos = Position(ticker="HOOD", shares=100, cost_basis=25.50)
        assert pos.ticker == "HOOD"
        assert pos.shares == 100
        assert pos.cost_basis == 25.50

    def test_compression_result_creation(self) -> None:
        """Test CompressionResult dataclass can be instantiated."""
        from pe_scanner.analysis.compression import CompressionResult, CompressionSignal

        result = CompressionResult(
            ticker="HOOD",
            trailing_pe=73.27,
            forward_pe=156.58,
            compression_pct=-113.70,
            implied_growth_pct=-53.2,
            signal=CompressionSignal.STRONG_SELL,
            confidence="high",
            warnings=[],
        )
        assert result.ticker == "HOOD"
        assert result.compression_pct == -113.70
        assert result.signal == CompressionSignal.STRONG_SELL


class TestHelperFunctions:
    """Test helper functions that are already implemented."""

    def test_is_uk_stock_with_suffix(self) -> None:
        """Test UK stock detection with .L suffix."""
        from pe_scanner.data.corrector import is_uk_stock

        assert is_uk_stock("BATS.L") is True
        assert is_uk_stock("bats.l") is True  # Case insensitive
        assert is_uk_stock("BT-A.L") is True

    def test_is_uk_stock_without_suffix(self) -> None:
        """Test UK stock detection for non-UK stocks."""
        from pe_scanner.data.corrector import is_uk_stock

        assert is_uk_stock("HOOD") is False
        assert is_uk_stock("AAPL") is False
        assert is_uk_stock("ORA.PA") is False  # Paris exchange


class TestEnums:
    """Test that enums are properly defined."""

    def test_compression_signal_enum(self) -> None:
        """Test CompressionSignal enum values."""
        from pe_scanner.analysis.compression import CompressionSignal

        assert CompressionSignal.STRONG_BUY.value == "strong_buy"
        assert CompressionSignal.SELL.value == "sell"
        assert CompressionSignal.DATA_ERROR.value == "data_error"

    def test_portfolio_type_enum(self) -> None:
        """Test PortfolioType enum values."""
        from pe_scanner.portfolios.loader import PortfolioType

        assert PortfolioType.ISA.value == "isa"
        assert PortfolioType.SIPP.value == "sipp"
        assert PortfolioType.WISHLIST.value == "wishlist"

    def test_data_quality_level_enum(self) -> None:
        """Test DataQualityLevel enum values."""
        from pe_scanner.data.validator import DataQualityLevel

        assert DataQualityLevel.VERIFIED.value == "verified"
        assert DataQualityLevel.UNRELIABLE.value == "unreliable"


class TestImplementedFunctions:
    """Test that core functions are implemented and working."""

    def test_calculate_compression_works(self) -> None:
        """Test calculate_compression returns valid results."""
        from pe_scanner.analysis.compression import calculate_compression

        compression_pct, implied_growth = calculate_compression(73.27, 156.58)
        assert compression_pct < 0  # Negative compression (P/E expanding)
        assert isinstance(compression_pct, float)

    def test_calculate_compression_prd_example(self) -> None:
        """Test HOOD example from PRD: -113.70% compression."""
        from pe_scanner.analysis.compression import calculate_compression

        compression_pct, _ = calculate_compression(73.27, 156.58)
        assert abs(compression_pct - (-113.70)) < 1.0  # Within 1% of expected


