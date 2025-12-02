"""
Analysis Service Layer

Handles business logic for stock analysis, coordinating between
data fetching, analysis modules, and response formatting.
"""

import logging
from typing import Optional

from pe_scanner.analysis import (
    analyze_stock,
    StockData,
    get_analysis_mode_name,
    classify_stock_type,
    generate_anchor,
    generate_shareable_headline,
    CompressionResult,
    GrowthAnalysisResult,
    HyperGrowthAnalysisResult,
)
from pe_scanner.api.schema import AnalysisResponse, ShareURLs
from pe_scanner.data.fetcher import fetch_market_data

logger = logging.getLogger(__name__)


class AnalysisService:
    """
    Service for performing stock analysis and formatting API responses.
    
    Coordinates between data fetching, analysis modules, and response formatting.
    """
    
    def analyze(
        self,
        ticker: str,
        include_anchor: bool = True,
        include_headline: bool = True,
        include_share_urls: bool = True,
        base_url: str = "",
    ) -> AnalysisResponse:
        """
        Perform complete stock analysis and format API response.
        
        Args:
            ticker: Stock ticker symbol
            include_anchor: Include anchor statement in response
            include_headline: Include headline in response
            include_share_urls: Include share URLs in response
            base_url: Base URL for share URL generation
            
        Returns:
            AnalysisResponse with complete analysis
            
        Raises:
            ValueError: If ticker is invalid or data not found
            Exception: For other analysis errors
        """
        # Fetch market data
        try:
            market_data = fetch_market_data(ticker, use_cache=True)
        except Exception as e:
            logger.error(f"Failed to fetch data for {ticker}: {e}")
            raise ValueError(f"Could not fetch data for ticker {ticker}: {str(e)}")
        
        # Prepare stock data for analysis
        stock_data = StockData(
            ticker=ticker,
            trailing_pe=market_data.trailing_pe,
            forward_pe=market_data.forward_pe,
            trailing_eps=market_data.trailing_eps,
            forward_eps=market_data.forward_eps,
            earnings_growth_pct=getattr(market_data, "earnings_growth_pct", None),
            market_cap=market_data.market_cap,
            revenue=getattr(market_data, "revenue", None),
            revenue_growth_pct=getattr(market_data, "revenue_growth_pct", None),
            profit_margin_pct=getattr(market_data, "profit_margin_pct", None),
            data_quality_flags=getattr(market_data, "fetch_errors", []),
        )
        
        # Perform tiered analysis
        analysis_result = analyze_stock(stock_data)
        
        # Determine analysis mode
        stock_type = classify_stock_type(stock_data.trailing_pe)
        analysis_mode = get_analysis_mode_name(stock_type)
        
        # Extract metrics based on analysis type
        metrics = self._extract_metrics(analysis_result)
        
        # Extract signal and confidence
        signal = analysis_result.signal.value.upper().replace("_", " ")
        confidence = getattr(analysis_result, "confidence", "medium")
        
        # Generate anchor if requested
        anchor = None
        if include_anchor:
            try:
                anchor = generate_anchor(
                    result=analysis_result,
                    market_cap=market_data.market_cap,
                )
            except Exception as e:
                logger.warning(f"Failed to generate anchor for {ticker}: {e}")
        
        # Generate headline and share URLs if requested
        headline = None
        share_urls = None
        if include_headline or include_share_urls:
            try:
                shareable = generate_shareable_headline(analysis_result, base_url)
                if include_headline:
                    headline = shareable.headline
                if include_share_urls:
                    share_urls = ShareURLs(
                        twitter=shareable.twitter_url,
                        linkedin=shareable.linkedin_url,
                        copy_text=shareable.copy_text,
                    )
            except Exception as e:
                logger.warning(f"Failed to generate headline/URLs for {ticker}: {e}")
        
        # Determine data quality
        data_quality = self._assess_data_quality(getattr(market_data, "fetch_errors", []))
        
        # Extract warnings
        warnings = list(getattr(analysis_result, "warnings", []))
        fetch_errors = getattr(market_data, "fetch_errors", [])
        if fetch_errors:
            warnings.extend(fetch_errors)
        
        # Build response
        response = AnalysisResponse(
            ticker=ticker,
            company_name=market_data.company_name,
            current_price=market_data.current_price,
            analysis_mode=analysis_mode,
            metrics=metrics,
            signal=signal,
            confidence=confidence,
            anchor=anchor,
            headline=headline,
            share_urls=share_urls,
            data_quality=data_quality,
            warnings=warnings,
        )
        
        return response
    
    def _extract_metrics(self, result) -> dict:
        """
        Extract analysis metrics based on result type.
        
        Args:
            result: Analysis result (CompressionResult, GrowthAnalysisResult, or HyperGrowthAnalysisResult)
            
        Returns:
            Dictionary of metrics
        """
        if isinstance(result, CompressionResult):
            return {
                "trailing_pe": round(result.trailing_pe, 2),
                "forward_pe": round(result.forward_pe, 2),
                "compression_pct": round(result.compression_pct, 1),
                "implied_growth_pct": round(result.implied_growth_pct, 1),
            }
        elif isinstance(result, GrowthAnalysisResult):
            return {
                "trailing_pe": round(result.trailing_pe, 2) if result.trailing_pe else 0,
                "earnings_growth_pct": round(result.earnings_growth_pct, 1) if result.earnings_growth_pct else 0,
                "peg_ratio": round(result.peg_ratio, 2) if result.peg_ratio else 0,
            }
        elif isinstance(result, HyperGrowthAnalysisResult):
            return {
                "price_to_sales": round(result.price_to_sales, 1) if result.price_to_sales else 0,
                "revenue_growth_pct": round(result.revenue_growth_pct, 1) if result.revenue_growth_pct else 0,
                "profit_margin_pct": round(result.profit_margin_pct, 1) if result.profit_margin_pct else 0,
                "rule_of_40_score": round(result.rule_of_40_score, 0) if result.rule_of_40_score else 0,
            }
        else:
            # Fallback for unknown types
            return {}
    
    def _assess_data_quality(self, flags: Optional[list]) -> str:
        """
        Assess overall data quality based on flags.
        
        Args:
            flags: List of data quality flags/warnings
            
        Returns:
            Data quality assessment: "verified", "warning", or "error"
        """
        if not flags:
            return "verified"
        
        # Check for critical errors
        error_keywords = ["missing", "invalid", "error", "failed"]
        if any(any(keyword in flag.lower() for keyword in error_keywords) for flag in flags):
            return "error"
        
        # Has warnings but not critical
        return "warning"

