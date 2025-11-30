"""
Portfolio Loader Module

Loads portfolio data from CSV and JSON files for analysis.
Supports ISA, SIPP, and Wishlist portfolio types with validation.
Configuration is loaded from config.yaml when available.
"""

import csv
import json
import logging
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Optional, Union

import yaml

logger = logging.getLogger(__name__)


# =============================================================================
# Enums and Data Classes
# =============================================================================


class PortfolioType(Enum):
    """Supported portfolio types."""

    ISA = "isa"
    SIPP = "sipp"
    WISHLIST = "wishlist"
    CUSTOM = "custom"

    @classmethod
    def from_string(cls, value: str) -> "PortfolioType":
        """Convert string to PortfolioType, defaulting to CUSTOM."""
        value_lower = value.lower().strip()
        for ptype in cls:
            if ptype.value == value_lower:
                return ptype
        return cls.CUSTOM


@dataclass
class Position:
    """A single position in a portfolio."""

    ticker: str
    shares: float
    cost_basis: float
    current_price: Optional[float] = None
    portfolio_type: PortfolioType = PortfolioType.CUSTOM

    @property
    def total_cost(self) -> float:
        """Total cost of the position."""
        return self.shares * self.cost_basis

    @property
    def market_value(self) -> Optional[float]:
        """Current market value (if price available)."""
        if self.current_price is not None:
            return self.shares * self.current_price
        return None

    @property
    def gain_loss(self) -> Optional[float]:
        """Unrealized gain/loss (if price available)."""
        if self.market_value is not None:
            return self.market_value - self.total_cost
        return None


@dataclass
class Portfolio:
    """A complete portfolio with positions and metadata."""

    name: str
    portfolio_type: PortfolioType
    positions: list[Position] = field(default_factory=list)
    file_path: Optional[Path] = None
    load_errors: list[str] = field(default_factory=list)

    @property
    def total_positions(self) -> int:
        """Total number of positions in portfolio."""
        return len(self.positions)

    @property
    def tickers(self) -> list[str]:
        """List of all tickers in portfolio."""
        return [p.ticker for p in self.positions]

    @property
    def total_cost(self) -> float:
        """Total cost basis of all positions."""
        return sum(p.total_cost for p in self.positions)

    @property
    def total_market_value(self) -> Optional[float]:
        """Total market value (if all prices available)."""
        values = [p.market_value for p in self.positions]
        if all(v is not None for v in values):
            return sum(v for v in values if v is not None)
        return None

    def get_position(self, ticker: str) -> Optional[Position]:
        """Get position by ticker symbol."""
        ticker_upper = ticker.upper()
        for pos in self.positions:
            if pos.ticker.upper() == ticker_upper:
                return pos
        return None


# =============================================================================
# Configuration
# =============================================================================


@dataclass
class LoaderConfig:
    """Configuration for the portfolio loader."""

    isa_path: str = "portfolios/isa.csv"
    sipp_path: str = "portfolios/sipp.csv"
    wishlist_path: str = "portfolios/wishlist.csv"


def _load_config() -> LoaderConfig:
    """Load loader configuration from config.yaml."""
    config_paths = [
        Path.cwd() / "config.yaml",
        Path.cwd().parent / "config.yaml",
        Path(__file__).parent.parent.parent.parent / "config.yaml",
    ]

    for config_path in config_paths:
        if config_path.exists():
            try:
                with open(config_path) as f:
                    config_data = yaml.safe_load(f)

                portfolios_config = config_data.get("portfolios", {})
                return LoaderConfig(
                    isa_path=portfolios_config.get("isa", "portfolios/isa.csv"),
                    sipp_path=portfolios_config.get("sipp", "portfolios/sipp.csv"),
                    wishlist_path=portfolios_config.get("wishlist", "portfolios/wishlist.csv"),
                )
            except Exception as e:
                logger.warning(f"Failed to load config from {config_path}: {e}")

    return LoaderConfig()


# Global config (lazy loaded)
_config: Optional[LoaderConfig] = None


def get_config() -> LoaderConfig:
    """Get loader configuration."""
    global _config
    if _config is None:
        _config = _load_config()
    return _config


# =============================================================================
# Parsing Helpers
# =============================================================================


def _parse_float(value: str, field_name: str, row_num: int) -> tuple[Optional[float], Optional[str]]:
    """
    Parse a string to float, returning (value, error_message).

    Args:
        value: String value to parse
        field_name: Name of field (for error messages)
        row_num: Row number (for error messages)

    Returns:
        Tuple of (parsed_value, error_message)
    """
    if value is None or value == "" or value.lower() in ("n/a", "none", "null", "-"):
        return None, None  # Optional field, no error

    try:
        return float(value), None
    except (ValueError, TypeError):
        return None, f"Row {row_num}: Invalid {field_name} value '{value}'"


def _infer_portfolio_type(file_path: Path) -> PortfolioType:
    """Infer portfolio type from filename."""
    name_lower = file_path.stem.lower()

    if "isa" in name_lower:
        return PortfolioType.ISA
    elif "sipp" in name_lower:
        return PortfolioType.SIPP
    elif "wishlist" in name_lower or "watch" in name_lower:
        return PortfolioType.WISHLIST
    else:
        return PortfolioType.CUSTOM


# =============================================================================
# CSV Loading
# =============================================================================


def _load_csv(file_path: Path, portfolio_type: PortfolioType) -> Portfolio:
    """
    Load portfolio from CSV file.

    Expected columns: ticker, shares, cost_basis, current_price (optional)
    """
    positions: list[Position] = []
    errors: list[str] = []

    try:
        with open(file_path, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)

            # Normalize column names (lowercase, strip whitespace)
            if reader.fieldnames:
                reader.fieldnames = [name.lower().strip() for name in reader.fieldnames]

            for row_num, row in enumerate(reader, start=2):  # Start at 2 (header is row 1)
                # Normalize keys
                row = {k.lower().strip(): v.strip() if v else v for k, v in row.items()}

                # Extract ticker (required)
                ticker = row.get("ticker", "").strip().upper()
                if not ticker:
                    errors.append(f"Row {row_num}: Missing ticker")
                    continue

                # Parse shares (required)
                shares, err = _parse_float(row.get("shares", ""), "shares", row_num)
                if err:
                    errors.append(err)
                    continue
                if shares is None or shares <= 0:
                    errors.append(f"Row {row_num}: Invalid or missing shares for {ticker}")
                    continue

                # Parse cost_basis (required)
                cost_basis, err = _parse_float(row.get("cost_basis", ""), "cost_basis", row_num)
                if err:
                    errors.append(err)
                    continue
                if cost_basis is None:
                    errors.append(f"Row {row_num}: Missing cost_basis for {ticker}")
                    continue

                # Parse current_price (optional)
                current_price, err = _parse_float(row.get("current_price", ""), "current_price", row_num)
                if err:
                    errors.append(err)
                    # Don't skip - current_price is optional

                positions.append(Position(
                    ticker=ticker,
                    shares=shares,
                    cost_basis=cost_basis,
                    current_price=current_price,
                    portfolio_type=portfolio_type,
                ))

    except FileNotFoundError:
        raise FileNotFoundError(f"Portfolio file not found: {file_path}")
    except Exception as e:
        errors.append(f"Failed to parse CSV: {str(e)}")

    return Portfolio(
        name=file_path.stem,
        portfolio_type=portfolio_type,
        positions=positions,
        file_path=file_path,
        load_errors=errors,
    )


# =============================================================================
# JSON Loading
# =============================================================================


def _load_json(file_path: Path, portfolio_type: PortfolioType) -> Portfolio:
    """
    Load portfolio from JSON file.

    Expected format:
    {
        "name": "My ISA",
        "positions": [
            {"ticker": "HOOD", "shares": 100, "cost_basis": 25.50, "current_price": 114.30}
        ]
    }

    Or simple array format:
    [
        {"ticker": "HOOD", "shares": 100, "cost_basis": 25.50}
    ]
    """
    positions: list[Position] = []
    errors: list[str] = []
    portfolio_name = file_path.stem

    try:
        with open(file_path, encoding="utf-8") as f:
            data = json.load(f)

        # Handle both object and array formats
        if isinstance(data, dict):
            portfolio_name = data.get("name", file_path.stem)
            positions_data = data.get("positions", [])
        elif isinstance(data, list):
            positions_data = data
        else:
            raise ValueError("JSON must be an object or array")

        for idx, item in enumerate(positions_data):
            row_num = idx + 1

            if not isinstance(item, dict):
                errors.append(f"Position {row_num}: Invalid format (expected object)")
                continue

            # Extract ticker (required)
            ticker = str(item.get("ticker", "")).strip().upper()
            if not ticker:
                errors.append(f"Position {row_num}: Missing ticker")
                continue

            # Get shares (required)
            shares = item.get("shares")
            if shares is None:
                errors.append(f"Position {row_num}: Missing shares for {ticker}")
                continue
            try:
                shares = float(shares)
                if shares <= 0:
                    errors.append(f"Position {row_num}: Invalid shares for {ticker}")
                    continue
            except (ValueError, TypeError):
                errors.append(f"Position {row_num}: Invalid shares value for {ticker}")
                continue

            # Get cost_basis (required)
            cost_basis = item.get("cost_basis")
            if cost_basis is None:
                errors.append(f"Position {row_num}: Missing cost_basis for {ticker}")
                continue
            try:
                cost_basis = float(cost_basis)
            except (ValueError, TypeError):
                errors.append(f"Position {row_num}: Invalid cost_basis for {ticker}")
                continue

            # Get current_price (optional)
            current_price = item.get("current_price")
            if current_price is not None:
                try:
                    current_price = float(current_price)
                except (ValueError, TypeError):
                    errors.append(f"Position {row_num}: Invalid current_price for {ticker}")
                    current_price = None

            positions.append(Position(
                ticker=ticker,
                shares=shares,
                cost_basis=cost_basis,
                current_price=current_price,
                portfolio_type=portfolio_type,
            ))

    except FileNotFoundError:
        raise FileNotFoundError(f"Portfolio file not found: {file_path}")
    except json.JSONDecodeError as e:
        errors.append(f"Invalid JSON: {str(e)}")
    except Exception as e:
        errors.append(f"Failed to parse JSON: {str(e)}")

    return Portfolio(
        name=portfolio_name,
        portfolio_type=portfolio_type,
        positions=positions,
        file_path=file_path,
        load_errors=errors,
    )


# =============================================================================
# Public API
# =============================================================================


def load_portfolio(
    file_path: Union[str, Path],
    portfolio_type: Optional[PortfolioType] = None,
) -> Portfolio:
    """
    Load a portfolio from a CSV or JSON file.

    Expected CSV format:
        ticker,shares,cost_basis,current_price
        HOOD,100,25.50,114.30

    Expected JSON format:
        [{"ticker": "HOOD", "shares": 100, "cost_basis": 25.50}]

    Args:
        file_path: Path to portfolio file (CSV or JSON)
        portfolio_type: Optional type classification (auto-detected if not provided)

    Returns:
        Portfolio object with loaded positions

    Raises:
        FileNotFoundError: If file doesn't exist
        ValueError: If file format is not supported

    Example:
        >>> portfolio = load_portfolio("portfolios/isa.csv", PortfolioType.ISA)
        >>> print(f"Loaded {portfolio.total_positions} positions")
    """
    path = Path(file_path)

    if not path.exists():
        raise FileNotFoundError(f"Portfolio file not found: {path}")

    # Auto-detect portfolio type if not provided
    if portfolio_type is None:
        portfolio_type = _infer_portfolio_type(path)

    # Load based on file extension
    suffix = path.suffix.lower()

    if suffix == ".csv":
        portfolio = _load_csv(path, portfolio_type)
    elif suffix == ".json":
        portfolio = _load_json(path, portfolio_type)
    else:
        raise ValueError(f"Unsupported file format: {suffix}. Use .csv or .json")

    # Log results
    if portfolio.load_errors:
        logger.warning(
            f"Loaded {portfolio.name} with {len(portfolio.load_errors)} errors: "
            f"{portfolio.load_errors[:3]}..."
        )
    else:
        logger.info(f"Loaded {portfolio.name}: {portfolio.total_positions} positions")

    return portfolio


def load_all_portfolios(
    portfolio_dir: Union[str, Path] = "portfolios",
    config: Optional[dict] = None,
) -> dict[PortfolioType, Portfolio]:
    """
    Load all configured portfolios from directory.

    Uses config.yaml portfolio paths if available, otherwise looks for
    standard files (isa.csv, sipp.csv, wishlist.csv) in the directory.

    Args:
        portfolio_dir: Directory containing portfolio files
        config: Optional config dict with portfolio paths

    Returns:
        Dict mapping PortfolioType to loaded Portfolio

    Example:
        >>> portfolios = load_all_portfolios()
        >>> for ptype, portfolio in portfolios.items():
        ...     print(f"{ptype.value}: {portfolio.total_positions} positions")
    """
    portfolios: dict[PortfolioType, Portfolio] = {}
    base_dir = Path(portfolio_dir)

    # Get paths from config
    loader_config = get_config()

    portfolio_files = [
        (PortfolioType.ISA, loader_config.isa_path),
        (PortfolioType.SIPP, loader_config.sipp_path),
        (PortfolioType.WISHLIST, loader_config.wishlist_path),
    ]

    for ptype, file_path in portfolio_files:
        path = Path(file_path)

        # Try relative to base_dir if not absolute
        if not path.is_absolute():
            # Check config path first
            if path.exists():
                full_path = path
            # Then check relative to portfolio_dir
            elif (base_dir / path.name).exists():
                full_path = base_dir / path.name
            else:
                logger.debug(f"Portfolio file not found: {path}")
                continue
        else:
            full_path = path

        if full_path.exists():
            try:
                portfolio = load_portfolio(full_path, ptype)
                portfolios[ptype] = portfolio
            except Exception as e:
                logger.error(f"Failed to load {ptype.value} portfolio: {e}")

    logger.info(f"Loaded {len(portfolios)} portfolios: {[p.value for p in portfolios.keys()]}")
    return portfolios


def validate_portfolio(portfolio: Portfolio) -> list[str]:
    """
    Validate a loaded portfolio for data integrity.

    Checks:
    - All required fields present
    - No duplicate tickers
    - Positive share counts
    - Valid cost basis values

    Args:
        portfolio: Portfolio to validate

    Returns:
        List of validation error messages (empty if valid)
    """
    errors: list[str] = []

    # Check for empty portfolio
    if not portfolio.positions:
        errors.append("Portfolio has no positions")
        return errors

    # Track tickers for duplicate detection
    seen_tickers: set[str] = set()

    for pos in portfolio.positions:
        ticker = pos.ticker.upper()

        # Check for duplicate tickers
        if ticker in seen_tickers:
            errors.append(f"Duplicate ticker: {ticker}")
        seen_tickers.add(ticker)

        # Validate shares
        if pos.shares <= 0:
            errors.append(f"{ticker}: Shares must be positive (got {pos.shares})")

        # Validate cost basis
        if pos.cost_basis < 0:
            errors.append(f"{ticker}: Cost basis cannot be negative (got {pos.cost_basis})")

        # Validate current price if present
        if pos.current_price is not None and pos.current_price < 0:
            errors.append(f"{ticker}: Current price cannot be negative (got {pos.current_price})")

        # Validate ticker format (basic check)
        if not ticker or len(ticker) > 20:
            errors.append(f"Invalid ticker format: '{ticker}'")

    # Add any load errors
    errors.extend(portfolio.load_errors)

    return errors


def merge_portfolios(portfolios: list[Portfolio], name: str = "Combined") -> Portfolio:
    """
    Merge multiple portfolios into a single combined portfolio.

    If the same ticker appears in multiple portfolios, positions are combined
    by adding shares and calculating weighted average cost basis.

    Args:
        portfolios: List of portfolios to merge
        name: Name for the combined portfolio

    Returns:
        Combined Portfolio with all positions
    """
    if not portfolios:
        return Portfolio(name=name, portfolio_type=PortfolioType.CUSTOM)

    # Track positions by ticker for merging
    merged_positions: dict[str, Position] = {}
    all_errors: list[str] = []

    for portfolio in portfolios:
        all_errors.extend(portfolio.load_errors)

        for pos in portfolio.positions:
            ticker = pos.ticker.upper()

            if ticker in merged_positions:
                # Merge with existing position
                existing = merged_positions[ticker]

                # Calculate weighted average cost basis
                total_shares = existing.shares + pos.shares
                weighted_cost = (
                    (existing.shares * existing.cost_basis + pos.shares * pos.cost_basis)
                    / total_shares
                )

                # Use most recent price
                current_price = pos.current_price or existing.current_price

                merged_positions[ticker] = Position(
                    ticker=ticker,
                    shares=total_shares,
                    cost_basis=weighted_cost,
                    current_price=current_price,
                    portfolio_type=PortfolioType.CUSTOM,
                )
            else:
                # Add new position
                merged_positions[ticker] = Position(
                    ticker=ticker,
                    shares=pos.shares,
                    cost_basis=pos.cost_basis,
                    current_price=pos.current_price,
                    portfolio_type=PortfolioType.CUSTOM,
                )

    return Portfolio(
        name=name,
        portfolio_type=PortfolioType.CUSTOM,
        positions=list(merged_positions.values()),
        load_errors=all_errors,
    )
