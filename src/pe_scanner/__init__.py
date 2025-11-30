"""
PE Scanner - P/E Compression Analysis Tool

A Python-based portfolio analysis tool that identifies investment opportunities
through P/E (Price-to-Earnings) compression analysis.

Methodology:
    Compression % = ((Trailing P/E - Forward P/E) / Trailing P/E) × 100

    - Positive compression = Forward P/E is lower → Market expects earnings to GROW
    - Negative compression = Forward P/E is higher → Market expects earnings to DECLINE

Fair Value Scenarios:
    - Bear Case: 17.5x P/E multiple
    - Bull Case: 37.5x P/E multiple
"""

__version__ = "0.1.0"
__author__ = "Tom Eldridge"

# Submodule exports - import specific items as needed
# from pe_scanner.analysis import calculate_compression, analyze_fair_value
# from pe_scanner.data import fetch_market_data, validate_market_data
# from pe_scanner.portfolios import load_portfolio, generate_report

__all__ = [
    "__version__",
    "__author__",
]
