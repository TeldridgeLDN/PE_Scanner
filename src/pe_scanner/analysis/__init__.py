"""Analysis modules for P/E compression, fair value, stock classification, and growth analysis."""

from pe_scanner.analysis.classification import (
    StockType,
    classify_stock_type,
    get_analysis_mode_name,
)
from pe_scanner.analysis.compression import (
    CompressionConfig,
    CompressionResult,
    CompressionSignal,
    analyze_batch,
    analyze_compression,
    calculate_compression,
    get_config as get_compression_config,
    interpret_signal,
    rank_by_compression,
)
from pe_scanner.analysis.fair_value import (
    DEFAULT_BEAR_PE,
    DEFAULT_BULL_PE,
    FairValueConfig,
    FairValueResult,
    analyze_fair_value,
    analyze_fair_value_batch,
    calculate_base_fair_value,
    calculate_fair_values,
    calculate_upside,
    get_config as get_fair_value_config,
    rank_by_upside,
)
from pe_scanner.analysis.growth import (
    GrowthAnalysisResult,
    GrowthSignal,
    analyze_growth_batch,
    analyze_growth_stock,
    calculate_peg_ratio,
    interpret_peg_signal,
    rank_by_peg,
)

__all__ = [
    # Classification
    "StockType",
    "classify_stock_type",
    "get_analysis_mode_name",
    # Compression
    "CompressionConfig",
    "CompressionResult",
    "CompressionSignal",
    "analyze_batch",
    "analyze_compression",
    "calculate_compression",
    "get_compression_config",
    "interpret_signal",
    "rank_by_compression",
    # Fair Value
    "DEFAULT_BEAR_PE",
    "DEFAULT_BULL_PE",
    "FairValueConfig",
    "FairValueResult",
    "analyze_fair_value",
    "analyze_fair_value_batch",
    "calculate_base_fair_value",
    "calculate_fair_values",
    "calculate_upside",
    "get_fair_value_config",
    "rank_by_upside",
    # Growth (PEG)
    "GrowthAnalysisResult",
    "GrowthSignal",
    "analyze_growth_batch",
    "analyze_growth_stock",
    "calculate_peg_ratio",
    "interpret_peg_signal",
    "rank_by_peg",
]
