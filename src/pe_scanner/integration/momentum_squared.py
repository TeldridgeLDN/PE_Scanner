"""
Momentum_Squared Portfolio Integration

Provides compatibility with Momentum_Squared portfolio format:
- CSV import with expected columns
- Ticker symbol normalization
- Portfolio sync and drift detection
"""

import csv
import hashlib
import logging
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Optional

from pe_scanner.portfolios.loader import (
    Portfolio,
    PortfolioType,
    Position,
)

logger = logging.getLogger(__name__)


# =============================================================================
# Momentum_Squared Format Specification
# =============================================================================

# Expected CSV columns for Momentum_Squared master portfolio
REQUIRED_COLUMNS = ["ticker", "shares"]
OPTIONAL_COLUMNS = [
    "cost_basis",
    "purchase_date",
    "portfolio_type",  # ISA, SIPP, WISHLIST
    "sector",
    "notes",
]

# Column name aliases (for flexibility)
COLUMN_ALIASES = {
    "symbol": "ticker",
    "stock": "ticker",
    "quantity": "shares",
    "amount": "shares",
    "cost": "cost_basis",
    "avg_cost": "cost_basis",
    "type": "portfolio_type",
    "account": "portfolio_type",
}


# =============================================================================
# Data Classes
# =============================================================================


@dataclass
class SyncStatus:
    """Status of portfolio synchronization."""

    in_sync: bool
    local_hash: str
    master_hash: Optional[str]
    added_tickers: list[str]
    removed_tickers: list[str]
    changed_positions: list[str]
    last_sync: Optional[datetime]

    @property
    def summary(self) -> str:
        """Get sync status summary."""
        if self.in_sync:
            return f"✅ In sync (hash: {self.local_hash[:8]})"
        changes = []
        if self.added_tickers:
            changes.append(f"+{len(self.added_tickers)} added")
        if self.removed_tickers:
            changes.append(f"-{len(self.removed_tickers)} removed")
        if self.changed_positions:
            changes.append(f"~{len(self.changed_positions)} changed")
        return f"⚠️ Out of sync: {', '.join(changes)}"


# =============================================================================
# Format Validation
# =============================================================================


def validate_momentum_squared_format(file_path: Path) -> tuple[bool, list[str]]:
    """
    Validate that a CSV file matches Momentum_Squared format.

    Args:
        file_path: Path to CSV file

    Returns:
        Tuple of (is_valid, list of issues)
    """
    issues = []

    if not file_path.exists():
        return False, [f"File not found: {file_path}"]

    if file_path.suffix.lower() != ".csv":
        issues.append(f"Expected .csv file, got {file_path.suffix}")

    try:
        with open(file_path, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            headers = reader.fieldnames or []

            # Normalize headers
            normalized = {h.lower().strip(): h for h in headers}

            # Check required columns
            for required in REQUIRED_COLUMNS:
                if required not in normalized:
                    # Check aliases
                    found = False
                    for alias, canonical in COLUMN_ALIASES.items():
                        if alias in normalized and canonical == required:
                            found = True
                            break
                    if not found:
                        issues.append(f"Missing required column: {required}")

            # Validate row count
            rows = list(reader)
            if not rows:
                issues.append("File contains no data rows")

            # Validate data types
            for i, row in enumerate(rows[:10], 1):  # Check first 10 rows
                ticker = _get_column_value(row, "ticker", normalized)
                shares = _get_column_value(row, "shares", normalized)

                if not ticker:
                    issues.append(f"Row {i}: Missing ticker")
                if shares:
                    try:
                        float(shares)
                    except ValueError:
                        issues.append(f"Row {i}: Invalid shares value '{shares}'")

    except Exception as e:
        issues.append(f"Error reading file: {e}")

    return len(issues) == 0, issues


def _get_column_value(
    row: dict,
    column: str,
    normalized_headers: dict[str, str],
) -> Optional[str]:
    """Get column value with alias support."""
    # Try direct match
    for orig_header, norm_header in [(k, k.lower().strip()) for k in row.keys()]:
        if norm_header == column:
            return row.get(orig_header)

    # Try aliases
    for alias, canonical in COLUMN_ALIASES.items():
        if canonical == column:
            for orig_header in row.keys():
                if orig_header.lower().strip() == alias:
                    return row.get(orig_header)

    return None


# =============================================================================
# Portfolio Loading
# =============================================================================


def load_momentum_squared_portfolio(
    file_path: Path,
    portfolio_type: Optional[PortfolioType] = None,
) -> Portfolio:
    """
    Load a portfolio from Momentum_Squared CSV format.

    Args:
        file_path: Path to CSV file
        portfolio_type: Override portfolio type (optional)

    Returns:
        Portfolio object

    Raises:
        ValueError: If file format is invalid
    """
    is_valid, issues = validate_momentum_squared_format(file_path)
    if not is_valid:
        raise ValueError(f"Invalid Momentum_Squared format: {', '.join(issues)}")

    positions = []

    with open(file_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        normalized = {h.lower().strip(): h for h in reader.fieldnames or []}

        for row in reader:
            ticker = _get_column_value(row, "ticker", normalized)
            shares_str = _get_column_value(row, "shares", normalized)
            cost_basis_str = _get_column_value(row, "cost_basis", normalized)
            row_type = _get_column_value(row, "portfolio_type", normalized)

            if not ticker:
                continue

            # Parse numeric values
            shares = float(shares_str) if shares_str else 0.0
            cost_basis = 0.0
            if cost_basis_str:
                try:
                    cost_basis = float(cost_basis_str.replace("$", "").replace(",", ""))
                except ValueError:
                    pass

            # Determine portfolio type
            if portfolio_type is None and row_type:
                try:
                    portfolio_type = PortfolioType[row_type.upper()]
                except (KeyError, AttributeError):
                    portfolio_type = PortfolioType.CUSTOM

            positions.append(Position(
                ticker=ticker.upper().strip(),
                shares=shares,
                cost_basis=cost_basis,
            ))

    # Determine final portfolio type
    if portfolio_type is None:
        # Infer from filename
        name_lower = file_path.stem.lower()
        if "isa" in name_lower:
            portfolio_type = PortfolioType.ISA
        elif "sipp" in name_lower:
            portfolio_type = PortfolioType.SIPP
        elif "wish" in name_lower:
            portfolio_type = PortfolioType.WISHLIST
        else:
            portfolio_type = PortfolioType.CUSTOM

    return Portfolio(
        name=file_path.stem,
        portfolio_type=portfolio_type,
        positions=positions,
        file_path=file_path,
    )


# =============================================================================
# Sync Functions
# =============================================================================


def _calculate_portfolio_hash(portfolio: Portfolio) -> str:
    """Calculate hash of portfolio contents for sync detection."""
    # Sort positions by ticker for consistent hashing
    sorted_positions = sorted(portfolio.positions, key=lambda p: p.ticker)
    content_parts = []
    for pos in sorted_positions:
        content_parts.append(f"{pos.ticker}:{pos.shares}:{pos.cost_basis}")
    content = "|".join(content_parts)
    return hashlib.md5(content.encode()).hexdigest()


def sync_with_master(
    local_portfolio: Portfolio,
    master_path: Path,
) -> SyncStatus:
    """
    Check synchronization status with master portfolio.

    Args:
        local_portfolio: Local portfolio to check
        master_path: Path to master portfolio file

    Returns:
        SyncStatus with sync details
    """
    local_hash = _calculate_portfolio_hash(local_portfolio)
    local_tickers = {pos.ticker for pos in local_portfolio.positions}

    # Load master if exists
    if not master_path.exists():
        return SyncStatus(
            in_sync=False,
            local_hash=local_hash,
            master_hash=None,
            added_tickers=[],
            removed_tickers=[],
            changed_positions=[],
            last_sync=None,
        )

    try:
        master = load_momentum_squared_portfolio(master_path)
        master_hash = _calculate_portfolio_hash(master)
        master_tickers = {pos.ticker for pos in master.positions}

        # Find differences
        added = list(local_tickers - master_tickers)
        removed = list(master_tickers - local_tickers)

        # Find changed positions (same ticker, different shares/cost)
        changed = []
        for local_pos in local_portfolio.positions:
            for master_pos in master.positions:
                if local_pos.ticker == master_pos.ticker:
                    if local_pos.shares != master_pos.shares or local_pos.cost_basis != master_pos.cost_basis:
                        changed.append(local_pos.ticker)
                    break

        in_sync = local_hash == master_hash

        return SyncStatus(
            in_sync=in_sync,
            local_hash=local_hash,
            master_hash=master_hash,
            added_tickers=added,
            removed_tickers=removed,
            changed_positions=changed,
            last_sync=datetime.now(),
        )

    except Exception as e:
        logger.error(f"Failed to sync with master: {e}")
        return SyncStatus(
            in_sync=False,
            local_hash=local_hash,
            master_hash=None,
            added_tickers=[],
            removed_tickers=[],
            changed_positions=[],
            last_sync=None,
        )


def export_to_momentum_squared(
    portfolio: Portfolio,
    output_path: Path,
    include_optional: bool = True,
) -> Path:
    """
    Export portfolio to Momentum_Squared CSV format.

    Args:
        portfolio: Portfolio to export
        output_path: Output file path
        include_optional: Include optional columns

    Returns:
        Path to exported file
    """
    columns = list(REQUIRED_COLUMNS)
    if include_optional:
        columns.extend(["cost_basis", "portfolio_type"])

    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=columns)
        writer.writeheader()

        for pos in portfolio.positions:
            row = {
                "ticker": pos.ticker,
                "shares": pos.shares,
            }
            if include_optional:
                row["cost_basis"] = pos.cost_basis
                row["portfolio_type"] = portfolio.portfolio_type.value

            writer.writerow(row)

    logger.info(f"Exported {len(portfolio.positions)} positions to {output_path}")
    return output_path

