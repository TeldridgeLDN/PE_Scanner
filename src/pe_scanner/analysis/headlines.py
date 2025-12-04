"""
Headline Generator Module

Generates shareable, viral-optimized headlines for stock analysis signals.
Supports all analysis modes: VALUE (P/E Compression), GROWTH (PEG), and HYPER_GROWTH (P/S).

Features:
- Concise, action-oriented language optimized for Twitter/LinkedIn
- Emoji integration for quick visual identification
- Severity-aware templates based on signal strength
- Pre-formatted share URLs for social platforms
"""

import logging
from dataclasses import dataclass
from typing import Union
from urllib.parse import quote

from pe_scanner.analysis.compression import CompressionResult, CompressionSignal
from pe_scanner.analysis.growth import GrowthAnalysisResult, GrowthSignal
from pe_scanner.analysis.hyper_growth import HyperGrowthAnalysisResult, HyperGrowthSignal

logger = logging.getLogger(__name__)


# Type alias for any analysis result
AnalysisResult = Union[CompressionResult, GrowthAnalysisResult, HyperGrowthAnalysisResult]


# =============================================================================
# Data Classes
# =============================================================================


@dataclass
class HeadlineResult:
    """Result containing generated headline and share URLs."""
    
    ticker: str
    headline: str
    twitter_url: str
    linkedin_url: str
    copy_text: str


# =============================================================================
# Headline Templates
# =============================================================================


def _generate_value_headline(result: CompressionResult) -> str:
    """
    Generate headline for VALUE mode (P/E Compression analysis).
    
    Args:
        result: CompressionResult from P/E compression analysis
        
    Returns:
        Formatted headline string optimized for social media
    """
    ticker = result.ticker
    compression = result.compression_pct
    
    if result.signal == CompressionSignal.STRONG_BUY:
        return f"${ticker}: STRONG BUY signal! {compression:+.1f}% P/E compression suggests massive earnings growth ahead. Market underpricing this opportunity."
    
    elif result.signal == CompressionSignal.BUY:
        return f"${ticker}: BUY signal detected. {compression:+.1f}% P/E compression indicates solid earnings growth potential. Value opportunity."
    
    elif result.signal == CompressionSignal.HOLD:
        return f"${ticker}: HOLD signal. {compression:+.1f}% P/E compression shows neutral outlook. Fairly valued at current levels."
    
    elif result.signal == CompressionSignal.SELL:
        return f"${ticker}: SELL signal. {compression:+.1f}% P/E expansion warns of earnings decline. Consider reducing exposure."
    
    elif result.signal == CompressionSignal.STRONG_SELL:
        return f"${ticker}: STRONG SELL! {compression:+.1f}% P/E expansion signals major earnings deterioration ahead. High risk."
    
    else:  # DATA_ERROR
        return f"${ticker}: We couldn't find enough data to analyse this stock right now. Try a larger company or check back later."


def _generate_growth_headline(result: GrowthAnalysisResult) -> str:
    """
    Generate headline for GROWTH mode (PEG Ratio analysis).
    
    Args:
        result: GrowthAnalysisResult from PEG analysis
        
    Returns:
        Formatted headline string optimized for social media
    """
    ticker = result.ticker
    peg = result.peg_ratio
    
    if result.signal == GrowthSignal.BUY:
        return f"${ticker}: GROWTH BUY! PEG ratio of {peg:.2f} means you're paying less than ${peg:.2f} for every 1% of growth. Strong value."
    
    elif result.signal == GrowthSignal.HOLD:
        return f"${ticker}: HOLD signal. PEG ratio of {peg:.2f} suggests fair valuation for current growth rate. Watch and wait."
    
    elif result.signal == GrowthSignal.SELL:
        return f"${ticker}: GROWTH SELL. PEG ratio of {peg:.2f} means you're overpaying for growth. Valuation stretched."
    
    else:  # DATA_ERROR
        return f"${ticker}: We couldn't find the growth data needed for this stock. It may be too small or newly listed."


def _generate_hyper_growth_headline(result: HyperGrowthAnalysisResult) -> str:
    """
    Generate headline for HYPER_GROWTH mode (Price/Sales + Rule of 40 analysis).
    
    Args:
        result: HyperGrowthAnalysisResult from P/S and Rule of 40 analysis
        
    Returns:
        Formatted headline string optimized for social media
    """
    ticker = result.ticker
    ps = result.price_to_sales
    ro40 = result.rule_of_40_score
    
    if result.signal == HyperGrowthSignal.BUY:
        return f"${ticker}: HYPER-GROWTH BUY! Strong growth and profits at attractive valuation."
    
    elif result.signal == HyperGrowthSignal.HOLD:
        return f"${ticker}: HOLD. Mixed signals on growth vs valuation. Fairly valued for now."
    
    elif result.signal == HyperGrowthSignal.SELL:
        # Determine which metric triggered the sell
        if ps > 15:
            return f"${ticker}: HYPER-GROWTH SELL. Price-to-Sales of {ps:.1f}x is too expensive. Valuation stretched."
        else:
            return f"${ticker}: HYPER-GROWTH SELL. Weak growth + profit combination. Fundamentals concerning."
    
    else:  # DATA_ERROR
        return f"${ticker}: We couldn't find the revenue data needed for this stock. Try a more established company."


# =============================================================================
# Main Headline Generation
# =============================================================================


def generate_headline(result: AnalysisResult) -> str:
    """
    Generate a shareable headline based on analysis result.
    
    Automatically detects the analysis mode (VALUE, GROWTH, or HYPER_GROWTH)
    and generates an appropriate headline with emojis and key metrics.
    
    Args:
        result: Analysis result from any mode (CompressionResult, GrowthAnalysisResult,
                or HyperGrowthAnalysisResult)
                
    Returns:
        Formatted headline string optimized for Twitter/LinkedIn sharing
        
    Examples:
        >>> from pe_scanner.analysis.compression import CompressionResult, CompressionSignal
        >>> result = CompressionResult(
        ...     ticker="HOOD",
        ...     trailing_pe=15.0,
        ...     forward_pe=10.0,
        ...     compression_pct=33.3,
        ...     implied_growth_pct=50.0,
        ...     signal=CompressionSignal.BUY,
        ...     confidence="high"
        ... )
        >>> headline = generate_headline(result)
        >>> "BUY signal" in headline
        True
        >>> "$HOOD" in headline
        True
    """
    # Detect result type and route to appropriate template
    if isinstance(result, CompressionResult):
        return _generate_value_headline(result)
    elif isinstance(result, GrowthAnalysisResult):
        return _generate_growth_headline(result)
    elif isinstance(result, HyperGrowthAnalysisResult):
        return _generate_hyper_growth_headline(result)
    else:
        # Fallback for unknown types
        logger.warning(f"Unknown result type: {type(result)}")
        return f"⚠️ ${result.ticker}: Analysis complete but unable to format headline. Check data manually."


# =============================================================================
# Share URL Generation
# =============================================================================


def generate_share_urls(ticker: str, headline: str, base_url: str = "") -> HeadlineResult:
    """
    Generate pre-formatted share URLs for Twitter, LinkedIn, and copy text.
    
    Creates properly encoded URLs for one-click sharing on social platforms.
    
    Args:
        ticker: Stock ticker symbol (e.g., "HOOD")
        headline: Generated headline text to share
        base_url: Optional base URL for "Learn more" link (e.g., project homepage)
                 If empty, no URL is appended to the share text
                 
    Returns:
        HeadlineResult containing headline and all share URLs
        
    Examples:
        >>> urls = generate_share_urls("HOOD", "🚀 $HOOD: BUY signal detected!")
        >>> "text=" in urls.twitter_url
        True
        >>> "$HOOD" in urls.copy_text
        True
    """
    # Prepare share text
    share_text = headline
    
    # Add base URL if provided
    if base_url:
        share_text += f"\n\nLearn more: {base_url}"
    
    # Add hashtags for better discoverability
    hashtags = f"${ticker} #stocks #investing #stockmarket"
    full_text = f"{share_text}\n\n{hashtags}"
    
    # URL encode for different platforms
    twitter_text = quote(full_text)
    linkedin_text = quote(share_text)  # LinkedIn doesn't support hashtags as well
    
    # Generate platform-specific URLs
    twitter_url = f"https://twitter.com/intent/tweet?text={twitter_text}"
    linkedin_url = f"https://www.linkedin.com/sharing/share-offsite/?url={quote(base_url)}" if base_url else f"https://www.linkedin.com/feed/?shareActive=true&text={linkedin_text}"
    
    # Copy text (plain text with line breaks)
    copy_text = full_text
    
    return HeadlineResult(
        ticker=ticker,
        headline=headline,
        twitter_url=twitter_url,
        linkedin_url=linkedin_url,
        copy_text=copy_text,
    )


# =============================================================================
# Convenience Function
# =============================================================================


def generate_shareable_headline(result: AnalysisResult, base_url: str = "") -> HeadlineResult:
    """
    Generate headline and share URLs in one call.
    
    Convenience function that combines headline generation and share URL creation.
    
    Args:
        result: Analysis result from any mode
        base_url: Optional base URL for "Learn more" link
        
    Returns:
        HeadlineResult with headline and all share URLs
        
    Examples:
        >>> from pe_scanner.analysis.compression import CompressionResult, CompressionSignal
        >>> result = CompressionResult(
        ...     ticker="HOOD",
        ...     trailing_pe=15.0,
        ...     forward_pe=10.0,
        ...     compression_pct=33.3,
        ...     implied_growth_pct=50.0,
        ...     signal=CompressionSignal.BUY,
        ...     confidence="high"
        ... )
        >>> shareable = generate_shareable_headline(result)
        >>> shareable.ticker
        'HOOD'
        >>> len(shareable.twitter_url) > 0
        True
    """
    headline = generate_headline(result)
    return generate_share_urls(result.ticker, headline, base_url)

