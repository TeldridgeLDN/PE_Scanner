"""Analysis modules for P/E compression and fair value calculations."""

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

__all__ = [
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
]
