"""
Unit tests for Portfolio Loader Module
"""

import json
import tempfile
from pathlib import Path

import pytest

from pe_scanner.portfolios.loader import (
    Portfolio,
    PortfolioType,
    Position,
    load_portfolio,
    load_all_portfolios,
    merge_portfolios,
    validate_portfolio,
    _infer_portfolio_type,
    _parse_float,
)


# =============================================================================
# Position Tests
# =============================================================================


class TestPosition:
    """Tests for Position dataclass."""

    def test_position_creation(self):
        """Test basic Position creation."""
        pos = Position(
            ticker="HOOD",
            shares=100,
            cost_basis=25.50,
            current_price=114.30,
        )
        assert pos.ticker == "HOOD"
        assert pos.shares == 100
        assert pos.cost_basis == 25.50
        assert pos.current_price == 114.30

    def test_position_total_cost(self):
        """Test total_cost calculation."""
        pos = Position(ticker="HOOD", shares=100, cost_basis=25.50)
        assert pos.total_cost == 2550.0

    def test_position_market_value(self):
        """Test market_value calculation."""
        pos = Position(ticker="HOOD", shares=100, cost_basis=25.50, current_price=114.30)
        assert pos.market_value == 11430.0

    def test_position_market_value_none(self):
        """Test market_value is None when price not available."""
        pos = Position(ticker="HOOD", shares=100, cost_basis=25.50)
        assert pos.market_value is None

    def test_position_gain_loss(self):
        """Test gain_loss calculation."""
        pos = Position(ticker="HOOD", shares=100, cost_basis=25.50, current_price=114.30)
        assert pos.gain_loss == 8880.0  # 11430 - 2550

    def test_position_gain_loss_none(self):
        """Test gain_loss is None when price not available."""
        pos = Position(ticker="HOOD", shares=100, cost_basis=25.50)
        assert pos.gain_loss is None


# =============================================================================
# Portfolio Tests
# =============================================================================


class TestPortfolio:
    """Tests for Portfolio dataclass."""

    def test_portfolio_creation(self):
        """Test basic Portfolio creation."""
        portfolio = Portfolio(name="Test", portfolio_type=PortfolioType.ISA)
        assert portfolio.name == "Test"
        assert portfolio.portfolio_type == PortfolioType.ISA
        assert portfolio.positions == []
        assert portfolio.total_positions == 0

    def test_portfolio_tickers(self):
        """Test tickers property."""
        portfolio = Portfolio(
            name="Test",
            portfolio_type=PortfolioType.ISA,
            positions=[
                Position(ticker="HOOD", shares=100, cost_basis=25.50),
                Position(ticker="AAPL", shares=50, cost_basis=150.00),
            ],
        )
        assert portfolio.tickers == ["HOOD", "AAPL"]

    def test_portfolio_total_cost(self):
        """Test total_cost calculation."""
        portfolio = Portfolio(
            name="Test",
            portfolio_type=PortfolioType.ISA,
            positions=[
                Position(ticker="HOOD", shares=100, cost_basis=25.50),
                Position(ticker="AAPL", shares=50, cost_basis=150.00),
            ],
        )
        assert portfolio.total_cost == 10050.0  # 2550 + 7500

    def test_portfolio_get_position(self):
        """Test get_position method."""
        portfolio = Portfolio(
            name="Test",
            portfolio_type=PortfolioType.ISA,
            positions=[
                Position(ticker="HOOD", shares=100, cost_basis=25.50),
            ],
        )
        assert portfolio.get_position("HOOD") is not None
        assert portfolio.get_position("hood") is not None  # Case insensitive
        assert portfolio.get_position("NONEXISTENT") is None


# =============================================================================
# PortfolioType Tests
# =============================================================================


class TestPortfolioType:
    """Tests for PortfolioType enum."""

    def test_from_string_valid(self):
        """Test from_string with valid values."""
        assert PortfolioType.from_string("isa") == PortfolioType.ISA
        assert PortfolioType.from_string("ISA") == PortfolioType.ISA
        assert PortfolioType.from_string("sipp") == PortfolioType.SIPP
        assert PortfolioType.from_string("wishlist") == PortfolioType.WISHLIST

    def test_from_string_invalid(self):
        """Test from_string with invalid value defaults to CUSTOM."""
        assert PortfolioType.from_string("unknown") == PortfolioType.CUSTOM
        assert PortfolioType.from_string("") == PortfolioType.CUSTOM


# =============================================================================
# Helper Function Tests
# =============================================================================


class TestParseFloat:
    """Tests for _parse_float helper."""

    def test_parse_valid_float(self):
        """Test parsing valid float string."""
        value, error = _parse_float("123.45", "test", 1)
        assert value == 123.45
        assert error is None

    def test_parse_valid_int(self):
        """Test parsing integer string."""
        value, error = _parse_float("100", "test", 1)
        assert value == 100.0
        assert error is None

    def test_parse_empty(self):
        """Test parsing empty string returns None."""
        value, error = _parse_float("", "test", 1)
        assert value is None
        assert error is None

    def test_parse_na(self):
        """Test parsing N/A returns None."""
        value, error = _parse_float("N/A", "test", 1)
        assert value is None
        assert error is None

    def test_parse_invalid(self):
        """Test parsing invalid string returns error."""
        value, error = _parse_float("abc", "test", 1)
        assert value is None
        assert error is not None
        assert "Invalid test value" in error


class TestInferPortfolioType:
    """Tests for _infer_portfolio_type helper."""

    def test_infer_isa(self):
        """Test inferring ISA from filename."""
        assert _infer_portfolio_type(Path("my_isa.csv")) == PortfolioType.ISA
        assert _infer_portfolio_type(Path("ISA_2024.csv")) == PortfolioType.ISA

    def test_infer_sipp(self):
        """Test inferring SIPP from filename."""
        assert _infer_portfolio_type(Path("sipp.csv")) == PortfolioType.SIPP

    def test_infer_wishlist(self):
        """Test inferring WISHLIST from filename."""
        assert _infer_portfolio_type(Path("wishlist.csv")) == PortfolioType.WISHLIST
        assert _infer_portfolio_type(Path("watchlist.csv")) == PortfolioType.WISHLIST

    def test_infer_custom(self):
        """Test custom/unknown filenames default to CUSTOM."""
        assert _infer_portfolio_type(Path("my_stocks.csv")) == PortfolioType.CUSTOM


# =============================================================================
# CSV Loading Tests
# =============================================================================


class TestLoadCSV:
    """Tests for CSV loading."""

    def test_load_csv_valid(self, tmp_path):
        """Test loading valid CSV file."""
        csv_content = """ticker,shares,cost_basis,current_price
HOOD,100,25.50,114.30
AAPL,50,150.00,175.00"""
        csv_file = tmp_path / "test.csv"
        csv_file.write_text(csv_content)

        portfolio = load_portfolio(csv_file, PortfolioType.ISA)

        assert portfolio.total_positions == 2
        assert portfolio.tickers == ["HOOD", "AAPL"]
        assert len(portfolio.load_errors) == 0

    def test_load_csv_optional_price(self, tmp_path):
        """Test CSV with missing optional current_price."""
        csv_content = """ticker,shares,cost_basis,current_price
HOOD,100,25.50,
AAPL,50,150.00,175.00"""
        csv_file = tmp_path / "test.csv"
        csv_file.write_text(csv_content)

        portfolio = load_portfolio(csv_file)

        assert portfolio.total_positions == 2
        assert portfolio.get_position("HOOD").current_price is None
        assert portfolio.get_position("AAPL").current_price == 175.00

    def test_load_csv_missing_required(self, tmp_path):
        """Test CSV with missing required field logs error."""
        csv_content = """ticker,shares,cost_basis
HOOD,,25.50
AAPL,50,150.00"""
        csv_file = tmp_path / "test.csv"
        csv_file.write_text(csv_content)

        portfolio = load_portfolio(csv_file)

        assert portfolio.total_positions == 1  # Only AAPL loaded
        assert len(portfolio.load_errors) > 0

    def test_load_csv_file_not_found(self):
        """Test FileNotFoundError for missing file."""
        with pytest.raises(FileNotFoundError):
            load_portfolio("nonexistent.csv")

    def test_load_csv_case_insensitive_columns(self, tmp_path):
        """Test CSV with different column casing."""
        csv_content = """TICKER,Shares,COST_BASIS,Current_Price
HOOD,100,25.50,114.30"""
        csv_file = tmp_path / "test.csv"
        csv_file.write_text(csv_content)

        portfolio = load_portfolio(csv_file)

        assert portfolio.total_positions == 1
        assert portfolio.get_position("HOOD") is not None


# =============================================================================
# JSON Loading Tests
# =============================================================================


class TestLoadJSON:
    """Tests for JSON loading."""

    def test_load_json_object_format(self, tmp_path):
        """Test loading JSON with object format."""
        json_data = {
            "name": "My Portfolio",
            "positions": [
                {"ticker": "HOOD", "shares": 100, "cost_basis": 25.50, "current_price": 114.30},
                {"ticker": "AAPL", "shares": 50, "cost_basis": 150.00},
            ],
        }
        json_file = tmp_path / "test.json"
        json_file.write_text(json.dumps(json_data))

        portfolio = load_portfolio(json_file, PortfolioType.ISA)

        assert portfolio.name == "My Portfolio"
        assert portfolio.total_positions == 2
        assert len(portfolio.load_errors) == 0

    def test_load_json_array_format(self, tmp_path):
        """Test loading JSON with array format."""
        json_data = [
            {"ticker": "HOOD", "shares": 100, "cost_basis": 25.50},
            {"ticker": "AAPL", "shares": 50, "cost_basis": 150.00},
        ]
        json_file = tmp_path / "test.json"
        json_file.write_text(json.dumps(json_data))

        portfolio = load_portfolio(json_file)

        assert portfolio.total_positions == 2

    def test_load_json_invalid(self, tmp_path):
        """Test loading invalid JSON."""
        json_file = tmp_path / "test.json"
        json_file.write_text("not valid json {")

        portfolio = load_portfolio(json_file)

        assert portfolio.total_positions == 0
        assert len(portfolio.load_errors) > 0


# =============================================================================
# Validation Tests
# =============================================================================


class TestValidatePortfolio:
    """Tests for validate_portfolio function."""

    def test_validate_empty_portfolio(self):
        """Test validating empty portfolio."""
        portfolio = Portfolio(name="Empty", portfolio_type=PortfolioType.CUSTOM)
        errors = validate_portfolio(portfolio)
        assert "no positions" in errors[0].lower()

    def test_validate_duplicate_tickers(self):
        """Test detecting duplicate tickers."""
        portfolio = Portfolio(
            name="Test",
            portfolio_type=PortfolioType.ISA,
            positions=[
                Position(ticker="HOOD", shares=100, cost_basis=25.50),
                Position(ticker="HOOD", shares=50, cost_basis=30.00),
            ],
        )
        errors = validate_portfolio(portfolio)
        assert any("duplicate" in e.lower() for e in errors)

    def test_validate_negative_shares(self):
        """Test detecting negative shares."""
        portfolio = Portfolio(
            name="Test",
            portfolio_type=PortfolioType.ISA,
            positions=[
                Position(ticker="HOOD", shares=-100, cost_basis=25.50),
            ],
        )
        errors = validate_portfolio(portfolio)
        assert any("shares" in e.lower() and "positive" in e.lower() for e in errors)

    def test_validate_valid_portfolio(self):
        """Test valid portfolio has no errors."""
        portfolio = Portfolio(
            name="Test",
            portfolio_type=PortfolioType.ISA,
            positions=[
                Position(ticker="HOOD", shares=100, cost_basis=25.50),
                Position(ticker="AAPL", shares=50, cost_basis=150.00),
            ],
        )
        errors = validate_portfolio(portfolio)
        assert len(errors) == 0


# =============================================================================
# Merge Tests
# =============================================================================


class TestMergePortfolios:
    """Tests for merge_portfolios function."""

    def test_merge_empty_list(self):
        """Test merging empty list."""
        merged = merge_portfolios([])
        assert merged.total_positions == 0
        assert merged.portfolio_type == PortfolioType.CUSTOM

    def test_merge_single_portfolio(self):
        """Test merging single portfolio."""
        portfolio = Portfolio(
            name="Test",
            portfolio_type=PortfolioType.ISA,
            positions=[
                Position(ticker="HOOD", shares=100, cost_basis=25.50),
            ],
        )
        merged = merge_portfolios([portfolio])
        assert merged.total_positions == 1

    def test_merge_duplicate_tickers(self):
        """Test merging portfolios with duplicate tickers."""
        p1 = Portfolio(
            name="P1",
            portfolio_type=PortfolioType.ISA,
            positions=[Position(ticker="HOOD", shares=100, cost_basis=20.00)],
        )
        p2 = Portfolio(
            name="P2",
            portfolio_type=PortfolioType.SIPP,
            positions=[Position(ticker="HOOD", shares=100, cost_basis=30.00)],
        )

        merged = merge_portfolios([p1, p2])

        assert merged.total_positions == 1
        hood = merged.get_position("HOOD")
        assert hood.shares == 200  # 100 + 100
        assert hood.cost_basis == 25.00  # Weighted average: (100*20 + 100*30) / 200

    def test_merge_preserves_unique_tickers(self):
        """Test merging portfolios preserves all unique tickers."""
        p1 = Portfolio(
            name="P1",
            portfolio_type=PortfolioType.ISA,
            positions=[Position(ticker="HOOD", shares=100, cost_basis=25.50)],
        )
        p2 = Portfolio(
            name="P2",
            portfolio_type=PortfolioType.SIPP,
            positions=[Position(ticker="AAPL", shares=50, cost_basis=150.00)],
        )

        merged = merge_portfolios([p1, p2])

        assert merged.total_positions == 2
        assert "HOOD" in merged.tickers
        assert "AAPL" in merged.tickers


# =============================================================================
# Integration Tests
# =============================================================================


class TestLoadActualFile:
    """Integration tests with actual portfolio file."""

    def test_load_example_isa(self):
        """Test loading the example ISA file."""
        portfolio = load_portfolio("portfolios/example_isa.csv", PortfolioType.ISA)

        assert portfolio.name == "example_isa"
        assert portfolio.portfolio_type == PortfolioType.ISA
        assert portfolio.total_positions == 8
        assert "HOOD" in portfolio.tickers
        assert "BATS.L" in portfolio.tickers
        assert len(portfolio.load_errors) == 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

