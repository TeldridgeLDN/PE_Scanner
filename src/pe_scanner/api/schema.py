"""
API Response Schema Models

Defines Pydantic models for API responses following the v2.0 schema specification.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


# =============================================================================
# Share URLs Schema
# =============================================================================


class ShareURLs(BaseModel):
    """Social media share URLs for analysis results."""

    twitter: str = Field(..., description="Pre-formatted Twitter share URL")
    linkedin: str = Field(..., description="Pre-formatted LinkedIn share URL")
    copy_text: str = Field(..., description="Plain text for clipboard copying")


# =============================================================================
# Analysis Response Schema
# =============================================================================


class AnalysisResponse(BaseModel):
    """
    Complete v2.0 API response schema for stock analysis.
    
    Includes tiered analysis mode, metrics, signal, confidence,
    anchor statement, headline, and share URLs.
    """

    # Core identification
    ticker: str = Field(..., description="Stock ticker symbol")
    company_name: Optional[str] = Field(None, description="Company name if available")
    current_price: Optional[float] = Field(None, description="Current stock price")
    
    # Analysis classification
    analysis_mode: str = Field(
        ...,
        description="Analysis mode used (VALUE, GROWTH, or HYPER_GROWTH)",
        examples=["VALUE (P/E Compression)", "GROWTH (PEG)", "HYPER_GROWTH (Price/Sales)"]
    )
    
    # Mode-specific metrics (dynamic based on analysis_mode)
    metrics: Dict[str, Any] = Field(
        ...,
        description="Analysis metrics (varies by mode)",
        examples=[
            {
                "trailing_pe": 15.0,
                "forward_pe": 11.0,
                "compression_pct": 26.7,
                "implied_growth_pct": 36.4
            }
        ]
    )
    
    # Signal and confidence
    signal: str = Field(
        ...,
        description="Trading signal (BUY, SELL, HOLD, STRONG_BUY, STRONG_SELL, DATA_ERROR)",
        examples=["BUY", "SELL", "HOLD"]
    )
    confidence: str = Field(
        ...,
        description="Confidence level (high, medium, low)",
        examples=["high", "medium", "low"]
    )
    
    # v2.0 enhancements (optional fields based on query params)
    anchor: Optional[str] = Field(
        None,
        description="Memorable comparison statement ('what would have to be true')",
        examples=["Growing profits 1.4x would return HOOD to fair value"]
    )
    headline: Optional[str] = Field(
        None,
        description="Viral-optimized shareable headline",
        examples=["🚀 $HOOD: BUY signal detected. +26.7% P/E compression..."]
    )
    share_urls: Optional[ShareURLs] = Field(
        None,
        description="Pre-formatted social media share URLs"
    )
    
    # Data quality and metadata
    data_quality: str = Field(
        ...,
        description="Data quality assessment (verified, warning, error)",
        examples=["verified", "warning", "error"]
    )
    warnings: List[str] = Field(
        default_factory=list,
        description="Any warnings or data quality issues"
    )
    timestamp: datetime = Field(
        default_factory=datetime.utcnow,
        description="Analysis timestamp (UTC)"
    )
    
    class Config:
        """Pydantic model configuration."""
        json_schema_extra = {
            "example": {
                "ticker": "HOOD",
                "company_name": "Robinhood Markets Inc",
                "current_price": 114.30,
                "analysis_mode": "VALUE (P/E Compression)",
                "metrics": {
                    "trailing_pe": 15.0,
                    "forward_pe": 11.0,
                    "compression_pct": 26.7,
                    "implied_growth_pct": 36.4
                },
                "signal": "BUY",
                "confidence": "high",
                "anchor": "Growing profits 1.4x would return HOOD to fair value",
                "headline": "📈 $HOOD: BUY signal detected. +26.7% P/E compression indicates solid earnings growth potential.",
                "share_urls": {
                    "twitter": "https://twitter.com/intent/tweet?text=...",
                    "linkedin": "https://www.linkedin.com/sharing/share-offsite/?url=...",
                    "copy_text": "📈 $HOOD: BUY signal detected..."
                },
                "data_quality": "verified",
                "warnings": [],
                "timestamp": "2025-12-02T12:00:00Z"
            }
        }


# =============================================================================
# Error Response Schema
# =============================================================================


class ErrorResponse(BaseModel):
    """Error response for API failures."""

    error: str = Field(..., description="Error type or category")
    message: str = Field(..., description="Human-readable error message")
    ticker: Optional[str] = Field(None, description="Ticker that caused the error")
    timestamp: datetime = Field(
        default_factory=datetime.utcnow,
        description="Error timestamp (UTC)"
    )
    
    class Config:
        """Pydantic model configuration."""
        json_schema_extra = {
            "example": {
                "error": "InvalidTicker",
                "message": "Ticker symbol 'INVALID' not found",
                "ticker": "INVALID",
                "timestamp": "2025-12-02T12:00:00Z"
            }
        }


# =============================================================================
# Deprecation Warning Response
# =============================================================================


class DeprecatedEndpointResponse(BaseModel):
    """Response for deprecated endpoints with migration guidance."""

    warning: str = Field(
        default="This endpoint is deprecated",
        description="Deprecation warning message"
    )
    deprecated_endpoint: str = Field(..., description="The deprecated endpoint path")
    new_endpoint: str = Field(..., description="The new endpoint to use")
    migration_guide: str = Field(
        ...,
        description="URL or instructions for migration"
    )
    sunset_date: Optional[str] = Field(
        None,
        description="Date when this endpoint will be removed (YYYY-MM-DD)"
    )
    data: AnalysisResponse = Field(..., description="The actual analysis data")
    
    class Config:
        """Pydantic model configuration."""
        json_schema_extra = {
            "example": {
                "warning": "This endpoint is deprecated and will be removed on 2026-01-01",
                "deprecated_endpoint": "/api/compression/HOOD",
                "new_endpoint": "/api/analyze/HOOD",
                "migration_guide": "https://docs.pescanner.com/migration-v2",
                "sunset_date": "2026-01-01",
                "data": {
                    "ticker": "HOOD",
                    "analysis_mode": "VALUE (P/E Compression)",
                    "signal": "BUY"
                }
            }
        }

