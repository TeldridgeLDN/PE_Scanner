"""Analysis modules for P/E compression, fair value, stock classification, growth, hyper-growth, tiered routing, anchoring, and headline generation."""

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
from pe_scanner.analysis.hyper_growth import (
    HyperGrowthAnalysisResult,
    HyperGrowthSignal,
    analyze_hyper_growth_batch,
    analyze_hyper_growth_stock,
    calculate_price_to_sales,
    calculate_rule_of_40,
    interpret_hyper_growth_signal,
    rank_by_price_to_sales,
    rank_by_rule_of_40,
)
from pe_scanner.analysis.router import (
    AnalysisResult,
    StockData,
    analyze_batch as analyze_stocks_batch,
    analyze_stock,
    get_mode_name,
    get_stock_type,
)
from pe_scanner.analysis.anchoring import (
    generate_anchor,
    generate_anchors_batch,
)
from pe_scanner.analysis.headlines import (
    HeadlineResult,
    generate_headline,
    generate_share_urls,
    generate_shareable_headline,
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
    # Hyper-Growth (P/S + Rule of 40)
    "HyperGrowthAnalysisResult",
    "HyperGrowthSignal",
    "analyze_hyper_growth_batch",
    "analyze_hyper_growth_stock",
    "calculate_price_to_sales",
    "calculate_rule_of_40",
    "interpret_hyper_growth_signal",
    "rank_by_price_to_sales",
    "rank_by_rule_of_40",
    # Tiered Analysis Router
    "AnalysisResult",
    "StockData",
    "analyze_stocks_batch",
    "analyze_stock",
    "get_mode_name",
    "get_stock_type",
    # Anchoring
    "generate_anchor",
    "generate_anchors_batch",
    # Headlines
    "HeadlineResult",
    "generate_headline",
    "generate_share_urls",
    "generate_shareable_headline",
]
