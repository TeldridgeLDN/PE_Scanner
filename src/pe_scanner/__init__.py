"""
PE Scanner - P/E Compression Analysis Tool

A Python-based portfolio analysis tool that identifies investment opportunities
through P/E (Price-to-Earnings) compression analysis.
"""

__version__ = "0.1.0"
__author__ = "Tom Eldridge"

from pe_scanner.analysis import compression, fair_value
from pe_scanner.data import fetcher, validator, corrector
from pe_scanner.portfolios import loader, ranker, reporter

__all__ = [
    "compression",
    "fair_value",
    "fetcher",
    "validator",
    "corrector",
    "loader",
    "ranker",
    "reporter",
]
