"""
Pytest configuration and fixtures for PE Scanner tests.

Provides common test fixtures, mock data, and configuration for
both unit and integration tests.
"""

from pathlib import Path
from typing import Generator

import pytest


# ============================================================================
# Path Fixtures
# ============================================================================


@pytest.fixture
def project_root() -> Path:
    """Return the project root directory."""
    return Path(__file__).parent.parent


@pytest.fixture
def test_data_dir(project_root: Path) -> Path:
    """Return the test data directory."""
    return project_root / "tests" / "data"


@pytest.fixture
def portfolios_dir(project_root: Path) -> Path:
    """Return the portfolios directory."""
    return project_root / "portfolios"


# ============================================================================
# Sample Data Fixtures
# ============================================================================


@pytest.fixture
def sample_market_data() -> dict:
    """Sample market data for HOOD (Robinhood) - verified example from PRD."""
    return {
        "ticker": "HOOD",
        "current_price": 114.30,
        "trailing_pe": 73.27,  # Based on 2024 actual EPS $1.56
        "forward_pe": 156.58,  # Based on forward EPS $0.73
        "trailing_eps": 1.56,
        "forward_eps": 0.73,
        "market_cap": 10_000_000_000,
        "company_name": "Robinhood Markets Inc",
    }


@pytest.fixture
def sample_uk_stock_data() -> dict:
    """Sample UK stock data with pence/pounds issue."""
    return {
        "ticker": "BATS.L",
        "current_price": 29.96,
        "trailing_pe": 12.5,
        "forward_pe": 0.125,  # Needs 100x correction
        "trailing_eps": 2.40,
        "forward_eps": 0.024,  # Needs 100x correction
    }


@pytest.fixture
def sample_stock_split_data() -> dict:
    """Sample data showing stock split error (NFLX example from PRD)."""
    return {
        "ticker": "NFLX",
        "current_price": 114.09,  # Post-split price
        "trailing_pe": 47.54,
        "forward_pe": 4.80,  # FALSE - uses pre-split EPS
        "trailing_eps": 1.98,  # Post-split
        "forward_eps": 23.78,  # PRE-SPLIT ERROR!
    }


@pytest.fixture
def sample_portfolio_csv(tmp_path: Path) -> Path:
    """Create a temporary portfolio CSV file."""
    csv_content = """ticker,shares,cost_basis,current_price
HOOD,100,25.50,114.30
BATS.L,500,30.25,29.96
ORA.PA,200,9.50,40.81
ENGI.PA,150,15.00,10.69
"""
    csv_file = tmp_path / "test_portfolio.csv"
    csv_file.write_text(csv_content)
    return csv_file


# ============================================================================
# Expected Results Fixtures
# ============================================================================


@pytest.fixture
def expected_hood_compression() -> dict:
    """Expected compression analysis results for HOOD."""
    return {
        "compression_pct": -113.70,  # Negative = earnings collapse expected
        "implied_growth_pct": -53.2,  # 53% earnings decline
        "signal": "strong_sell",
        "bear_fair_value": 12.78,  # $0.73 × 17.5
        "bear_upside_pct": -88.82,
        "bull_fair_value": 27.38,  # $0.73 × 37.5
        "bull_upside_pct": -76.05,
    }


# ============================================================================
# Configuration Fixtures
# ============================================================================


@pytest.fixture
def default_thresholds() -> dict:
    """Default analysis thresholds from config."""
    return {
        "compression_signal": 20,
        "high_compression": 50,
        "extreme_compression": 80,
    }


@pytest.fixture
def default_scenarios() -> dict:
    """Default fair value scenario P/E multiples."""
    return {
        "bear_pe": 17.5,
        "bull_pe": 37.5,
    }


