"""
PE Scanner Integration Module

Provides integration with Momentum_Squared portfolio format
and diet103 validation hooks for data integrity.
"""

from pe_scanner.integration.hooks import (
    Hook,
    HookResult,
    HookType,
    HooksManager,
    DataQualityGuardian,
    PortfolioSyncValidator,
    PreAnalysisValidator,
    ResultsValidator,
    run_hooks,
)
from pe_scanner.integration.momentum_squared import (
    load_momentum_squared_portfolio,
    validate_momentum_squared_format,
    sync_with_master,
)

__all__ = [
    # Hooks
    "Hook",
    "HookResult",
    "HookType",
    "HooksManager",
    "DataQualityGuardian",
    "PortfolioSyncValidator",
    "PreAnalysisValidator",
    "ResultsValidator",
    "run_hooks",
    # Momentum_Squared
    "load_momentum_squared_portfolio",
    "validate_momentum_squared_format",
    "sync_with_master",
]



