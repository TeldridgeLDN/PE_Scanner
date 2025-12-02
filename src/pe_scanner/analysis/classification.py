"""
Stock Classification Module

Classifies stocks into VALUE, GROWTH, or HYPER_GROWTH categories based on
trailing P/E ratios to route them to appropriate analysis modes.

Classification Logic:
- VALUE: Trailing P/E < 25 (traditional value stocks)
- GROWTH: Trailing P/E between 25 and 50 (high but not extreme)
- HYPER_GROWTH: Trailing P/E > 50, negative, or None (extreme valuations or loss-making)
"""

import logging
from enum import Enum
from typing import Optional

logger = logging.getLogger(__name__)


# =============================================================================
# Enums
# =============================================================================


class StockType(Enum):
    """Classification of stock types for tiered analysis."""

    VALUE = "value"  # P/E < 25
    GROWTH = "growth"  # P/E 25-50
    HYPER_GROWTH = "hyper_growth"  # P/E > 50, negative, or None


# =============================================================================
# Classification Logic
# =============================================================================


def classify_stock_type(trailing_pe: Optional[float]) -> StockType:
    """
    Classify stock into VALUE, GROWTH, or HYPER_GROWTH based on trailing P/E.

    Classification Rules:
    - None, zero, or negative trailing P/E → HYPER_GROWTH (loss-making or no earnings)
    - Trailing P/E > 50 → HYPER_GROWTH (extreme valuation)
    - Trailing P/E between 25 and 50 → GROWTH (high but not extreme)
    - Trailing P/E < 25 → VALUE (traditional value stock)

    Args:
        trailing_pe: Trailing P/E ratio (TTM). Can be None, zero, negative, or positive.

    Returns:
        StockType enum (VALUE, GROWTH, or HYPER_GROWTH)

    Examples:
        >>> classify_stock_type(15.0)
        StockType.VALUE

        >>> classify_stock_type(35.0)
        StockType.GROWTH

        >>> classify_stock_type(75.0)
        StockType.HYPER_GROWTH

        >>> classify_stock_type(-10.0)
        StockType.HYPER_GROWTH

        >>> classify_stock_type(None)
        StockType.HYPER_GROWTH

        >>> classify_stock_type(0.0)
        StockType.HYPER_GROWTH

        >>> classify_stock_type(25.0)  # Boundary: exactly 25
        StockType.GROWTH

        >>> classify_stock_type(50.0)  # Boundary: exactly 50
        StockType.GROWTH
    """
    # Handle None, zero, or negative P/E (invalid or loss-making companies)
    if trailing_pe is None or trailing_pe <= 0:
        logger.debug(
            f"Classified as HYPER_GROWTH: trailing_pe={trailing_pe} (None, zero, or negative)"
        )
        return StockType.HYPER_GROWTH

    # Extreme valuation (P/E > 50)
    if trailing_pe > 50:
        logger.debug(
            f"Classified as HYPER_GROWTH: trailing_pe={trailing_pe:.2f} (> 50)"
        )
        return StockType.HYPER_GROWTH

    # Growth stocks (P/E 25-50 inclusive)
    if trailing_pe >= 25:
        logger.debug(
            f"Classified as GROWTH: trailing_pe={trailing_pe:.2f} (25-50)"
        )
        return StockType.GROWTH

    # Value stocks (P/E < 25)
    logger.debug(
        f"Classified as VALUE: trailing_pe={trailing_pe:.2f} (< 25)"
    )
    return StockType.VALUE


def get_analysis_mode_name(stock_type: StockType) -> str:
    """
    Get human-readable analysis mode name for a stock type.

    Args:
        stock_type: StockType enum value

    Returns:
        Human-readable string for display/logging

    Examples:
        >>> get_analysis_mode_name(StockType.VALUE)
        'VALUE (P/E Compression)'

        >>> get_analysis_mode_name(StockType.GROWTH)
        'GROWTH (PEG Ratio)'

        >>> get_analysis_mode_name(StockType.HYPER_GROWTH)
        'HYPER_GROWTH (Price/Sales)'
    """
    mode_names = {
        StockType.VALUE: "VALUE (P/E Compression)",
        StockType.GROWTH: "GROWTH (PEG Ratio)",
        StockType.HYPER_GROWTH: "HYPER_GROWTH (Price/Sales)",
    }
    return mode_names[stock_type]

