"""
Unit Tests for Headline Generator Module

Tests headline generation, emoji integration, and share URL creation
for all analysis modes (VALUE, GROWTH, HYPER_GROWTH).
"""

import pytest
from urllib.parse import unquote

from pe_scanner.analysis.compression import CompressionResult, CompressionSignal
from pe_scanner.analysis.growth import GrowthAnalysisResult, GrowthSignal
from pe_scanner.analysis.hyper_growth import HyperGrowthAnalysisResult, HyperGrowthSignal
from pe_scanner.analysis.headlines import (
    generate_headline,
    generate_share_urls,
    generate_shareable_headline,
    HeadlineResult,
)


# =============================================================================
# Fixtures
# =============================================================================


@pytest.fixture
def value_strong_buy():
    """VALUE mode STRONG_BUY result."""
    return CompressionResult(
        ticker="HOOD",
        trailing_pe=15.0,
        forward_pe=8.0,
        compression_pct=46.7,
        implied_growth_pct=87.5,
        signal=CompressionSignal.STRONG_BUY,
        confidence="high",
    )


@pytest.fixture
def value_buy():
    """VALUE mode BUY result."""
    return CompressionResult(
        ticker="HOOD",
        trailing_pe=15.0,
        forward_pe=11.0,
        compression_pct=26.7,
        implied_growth_pct=36.4,
        signal=CompressionSignal.BUY,
        confidence="high",
    )


@pytest.fixture
def value_hold():
    """VALUE mode HOLD result."""
    return CompressionResult(
        ticker="HOOD",
        trailing_pe=15.0,
        forward_pe=14.0,
        compression_pct=6.7,
        implied_growth_pct=7.1,
        signal=CompressionSignal.HOLD,
        confidence="medium",
    )


@pytest.fixture
def value_sell():
    """VALUE mode SELL result."""
    return CompressionResult(
        ticker="HOOD",
        trailing_pe=15.0,
        forward_pe=20.0,
        compression_pct=-33.3,
        implied_growth_pct=-25.0,
        signal=CompressionSignal.SELL,
        confidence="high",
    )


@pytest.fixture
def value_strong_sell():
    """VALUE mode STRONG_SELL result."""
    return CompressionResult(
        ticker="HOOD",
        trailing_pe=15.0,
        forward_pe=30.0,
        compression_pct=-100.0,
        implied_growth_pct=-50.0,
        signal=CompressionSignal.STRONG_SELL,
        confidence="high",
    )


@pytest.fixture
def value_data_error():
    """VALUE mode DATA_ERROR result."""
    return CompressionResult(
        ticker="HOOD",
        trailing_pe=15.0,
        forward_pe=5.0,
        compression_pct=66.7,
        implied_growth_pct=200.0,
        signal=CompressionSignal.DATA_ERROR,
        confidence="low",
        warnings=["Extreme compression suggests data error"],
    )


@pytest.fixture
def growth_buy():
    """GROWTH mode BUY result."""
    return GrowthAnalysisResult(
        ticker="CRM",
        trailing_pe=35.0,
        earnings_growth_pct=40.0,
        peg_ratio=0.88,
        signal=GrowthSignal.BUY,
        confidence="high",
        explanation="PEG ratio < 1.0 indicates undervalued growth",
    )


@pytest.fixture
def growth_hold():
    """GROWTH mode HOLD result."""
    return GrowthAnalysisResult(
        ticker="CRM",
        trailing_pe=35.0,
        earnings_growth_pct=25.0,
        peg_ratio=1.40,
        signal=GrowthSignal.HOLD,
        confidence="medium",
        explanation="PEG ratio between 1.0 and 2.0, fairly valued",
    )


@pytest.fixture
def growth_sell():
    """GROWTH mode SELL result."""
    return GrowthAnalysisResult(
        ticker="CRM",
        trailing_pe=35.0,
        earnings_growth_pct=10.0,
        peg_ratio=3.50,
        signal=GrowthSignal.SELL,
        confidence="high",
        explanation="PEG ratio > 2.0 indicates overvaluation",
    )


@pytest.fixture
def growth_data_error():
    """GROWTH mode DATA_ERROR result."""
    return GrowthAnalysisResult(
        ticker="CRM",
        signal=GrowthSignal.DATA_ERROR,
        confidence="low",
        explanation="Missing earnings growth data",
        warnings=["earnings_growth_pct is None"],
    )


@pytest.fixture
def hyper_growth_buy():
    """HYPER_GROWTH mode BUY result."""
    return HyperGrowthAnalysisResult(
        ticker="PLTR",
        price_to_sales=4.2,
        revenue_growth_pct=25.0,
        profit_margin_pct=20.0,
        rule_of_40_score=45.0,
        signal=HyperGrowthSignal.BUY,
        confidence="high",
        explanation="P/S < 5 AND Rule of 40 >= 40",
    )


@pytest.fixture
def hyper_growth_hold():
    """HYPER_GROWTH mode HOLD result."""
    return HyperGrowthAnalysisResult(
        ticker="PLTR",
        price_to_sales=8.0,
        revenue_growth_pct=20.0,
        profit_margin_pct=15.0,
        rule_of_40_score=35.0,
        signal=HyperGrowthSignal.HOLD,
        confidence="medium",
        explanation="Mixed signals, fairly valued",
    )


@pytest.fixture
def hyper_growth_sell_high_ps():
    """HYPER_GROWTH mode SELL result (high P/S)."""
    return HyperGrowthAnalysisResult(
        ticker="PLTR",
        price_to_sales=20.0,
        revenue_growth_pct=30.0,
        profit_margin_pct=25.0,
        rule_of_40_score=55.0,
        signal=HyperGrowthSignal.SELL,
        confidence="high",
        explanation="P/S > 15, too expensive",
    )


@pytest.fixture
def hyper_growth_sell_low_ro40():
    """HYPER_GROWTH mode SELL result (low Rule of 40)."""
    return HyperGrowthAnalysisResult(
        ticker="PLTR",
        price_to_sales=6.0,
        revenue_growth_pct=10.0,
        profit_margin_pct=5.0,
        rule_of_40_score=15.0,
        signal=HyperGrowthSignal.SELL,
        confidence="high",
        explanation="Rule of 40 < 20, weak fundamentals",
    )


@pytest.fixture
def hyper_growth_data_error():
    """HYPER_GROWTH mode DATA_ERROR result."""
    return HyperGrowthAnalysisResult(
        ticker="PLTR",
        signal=HyperGrowthSignal.DATA_ERROR,
        confidence="low",
        explanation="Missing revenue data",
        warnings=["revenue is None"],
    )


# =============================================================================
# VALUE Mode Headline Tests
# =============================================================================


def test_value_strong_buy_headline(value_strong_buy):
    """Test STRONG_BUY headline for VALUE mode."""
    headline = generate_headline(value_strong_buy)
    
    assert "$HOOD" in headline
    assert "STRONG BUY" in headline
    assert "🚀" in headline
    assert "+46.7%" in headline
    assert "compression" in headline.lower()
    assert len(headline) <= 280  # Twitter length limit


def test_value_buy_headline(value_buy):
    """Test BUY headline for VALUE mode."""
    headline = generate_headline(value_buy)
    
    assert "$HOOD" in headline
    assert "BUY" in headline
    assert "📈" in headline
    assert "+26.7%" in headline
    assert len(headline) <= 280


def test_value_hold_headline(value_hold):
    """Test HOLD headline for VALUE mode."""
    headline = generate_headline(value_hold)
    
    assert "$HOOD" in headline
    assert "HOLD" in headline
    assert "⚖️" in headline
    assert "+6.7%" in headline
    assert len(headline) <= 280


def test_value_sell_headline(value_sell):
    """Test SELL headline for VALUE mode."""
    headline = generate_headline(value_sell)
    
    assert "$HOOD" in headline
    assert "SELL" in headline
    assert "📉" in headline
    assert "-33.3%" in headline
    assert len(headline) <= 280


def test_value_strong_sell_headline(value_strong_sell):
    """Test STRONG_SELL headline for VALUE mode."""
    headline = generate_headline(value_strong_sell)
    
    assert "$HOOD" in headline
    assert "STRONG SELL" in headline
    assert "🔴" in headline
    assert "-100.0%" in headline
    assert len(headline) <= 280


def test_value_data_error_headline(value_data_error):
    """Test DATA_ERROR headline for VALUE mode."""
    headline = generate_headline(value_data_error)
    
    assert "$HOOD" in headline
    assert "⚠️" in headline
    assert "Data quality" in headline or "issue" in headline.lower()
    assert len(headline) <= 280


# =============================================================================
# GROWTH Mode Headline Tests
# =============================================================================


def test_growth_buy_headline(growth_buy):
    """Test BUY headline for GROWTH mode."""
    headline = generate_headline(growth_buy)
    
    assert "$CRM" in headline
    assert "BUY" in headline
    assert "🚀" in headline
    assert "0.88" in headline or "PEG" in headline
    assert len(headline) <= 280


def test_growth_hold_headline(growth_hold):
    """Test HOLD headline for GROWTH mode."""
    headline = generate_headline(growth_hold)
    
    assert "$CRM" in headline
    assert "HOLD" in headline
    assert "⚖️" in headline
    assert "1.40" in headline or "PEG" in headline
    assert len(headline) <= 280


def test_growth_sell_headline(growth_sell):
    """Test SELL headline for GROWTH mode."""
    headline = generate_headline(growth_sell)
    
    assert "$CRM" in headline
    assert "SELL" in headline
    assert "🔴" in headline
    assert "3.50" in headline or "PEG" in headline
    assert len(headline) <= 280


def test_growth_data_error_headline(growth_data_error):
    """Test DATA_ERROR headline for GROWTH mode."""
    headline = generate_headline(growth_data_error)
    
    assert "$CRM" in headline
    assert "⚠️" in headline
    assert "data" in headline.lower() or "insufficient" in headline.lower()
    assert len(headline) <= 280


# =============================================================================
# HYPER_GROWTH Mode Headline Tests
# =============================================================================


def test_hyper_growth_buy_headline(hyper_growth_buy):
    """Test BUY headline for HYPER_GROWTH mode."""
    headline = generate_headline(hyper_growth_buy)
    
    assert "$PLTR" in headline
    assert "BUY" in headline
    assert "🚀" in headline
    assert "4.2" in headline or "P/S" in headline
    assert "45" in headline or "Rule of 40" in headline
    assert len(headline) <= 280


def test_hyper_growth_hold_headline(hyper_growth_hold):
    """Test HOLD headline for HYPER_GROWTH mode."""
    headline = generate_headline(hyper_growth_hold)
    
    assert "$PLTR" in headline
    assert "HOLD" in headline
    assert "⚖️" in headline
    assert len(headline) <= 280


def test_hyper_growth_sell_high_ps_headline(hyper_growth_sell_high_ps):
    """Test SELL headline for HYPER_GROWTH mode (high P/S trigger)."""
    headline = generate_headline(hyper_growth_sell_high_ps)
    
    assert "$PLTR" in headline
    assert "SELL" in headline
    assert "🔴" in headline
    assert "20.0" in headline  # P/S value
    assert "P/S" in headline or "excessive" in headline.lower()
    assert len(headline) <= 280


def test_hyper_growth_sell_low_ro40_headline(hyper_growth_sell_low_ro40):
    """Test SELL headline for HYPER_GROWTH mode (low Rule of 40 trigger)."""
    headline = generate_headline(hyper_growth_sell_low_ro40)
    
    assert "$PLTR" in headline
    assert "SELL" in headline
    assert "🔴" in headline
    assert "15" in headline  # Rule of 40 score
    assert "Rule of 40" in headline or "fundamentals" in headline.lower()
    assert len(headline) <= 280


def test_hyper_growth_data_error_headline(hyper_growth_data_error):
    """Test DATA_ERROR headline for HYPER_GROWTH mode."""
    headline = generate_headline(hyper_growth_data_error)
    
    assert "$PLTR" in headline
    assert "⚠️" in headline
    assert "data" in headline.lower() or "missing" in headline.lower()
    assert len(headline) <= 280


# =============================================================================
# Share URL Generation Tests
# =============================================================================


def test_generate_share_urls_basic():
    """Test basic share URL generation."""
    headline = "🚀 $HOOD: BUY signal detected!"
    result = generate_share_urls("HOOD", headline)
    
    assert isinstance(result, HeadlineResult)
    assert result.ticker == "HOOD"
    assert result.headline == headline
    assert result.twitter_url.startswith("https://twitter.com/intent/tweet")
    assert "text=" in result.twitter_url
    assert result.linkedin_url.startswith("https://www.linkedin.com")
    assert "$HOOD" in result.copy_text
    assert "#stocks" in result.copy_text


def test_generate_share_urls_with_base_url():
    """Test share URL generation with base URL."""
    headline = "🚀 $HOOD: BUY signal!"
    base_url = "https://example.com/analysis"
    result = generate_share_urls("HOOD", headline, base_url)
    
    assert "Learn more" in result.copy_text
    assert base_url in result.copy_text
    assert base_url in result.linkedin_url or "linkedin.com" in result.linkedin_url


def test_twitter_url_encoding():
    """Test that Twitter URLs are properly encoded."""
    headline = "Test with special chars: & % # @"
    result = generate_share_urls("TEST", headline)
    
    # Check that URL is encoded
    assert "%20" in result.twitter_url or "+" in result.twitter_url  # Space encoding
    assert "%" in result.twitter_url  # Some encoding present
    
    # Decode and verify content is preserved
    decoded = unquote(result.twitter_url.split("text=")[1])
    assert "special chars" in decoded


def test_linkedin_url_structure():
    """Test LinkedIn URL structure."""
    headline = "Test headline"
    result = generate_share_urls("TEST", headline)
    
    assert "linkedin.com" in result.linkedin_url
    # Should have either share-offsite or feed endpoint
    assert "share" in result.linkedin_url.lower() or "feed" in result.linkedin_url.lower()


def test_copy_text_format():
    """Test copy text formatting."""
    headline = "🚀 $HOOD: BUY signal!"
    result = generate_share_urls("HOOD", headline)
    
    # Should include headline
    assert headline in result.copy_text
    
    # Should include hashtags
    assert "$HOOD" in result.copy_text
    assert "#stocks" in result.copy_text
    assert "#investing" in result.copy_text
    assert "#stockmarket" in result.copy_text


# =============================================================================
# Convenience Function Tests
# =============================================================================


def test_generate_shareable_headline_value_mode(value_buy):
    """Test convenience function with VALUE mode."""
    result = generate_shareable_headline(value_buy)
    
    assert isinstance(result, HeadlineResult)
    assert result.ticker == "HOOD"
    assert "$HOOD" in result.headline
    assert "BUY" in result.headline
    assert result.twitter_url.startswith("https://twitter.com")
    assert result.linkedin_url.startswith("https://www.linkedin.com")


def test_generate_shareable_headline_growth_mode(growth_buy):
    """Test convenience function with GROWTH mode."""
    result = generate_shareable_headline(growth_buy)
    
    assert result.ticker == "CRM"
    assert "$CRM" in result.headline
    assert "BUY" in result.headline


def test_generate_shareable_headline_hyper_growth_mode(hyper_growth_buy):
    """Test convenience function with HYPER_GROWTH mode."""
    result = generate_shareable_headline(hyper_growth_buy)
    
    assert result.ticker == "PLTR"
    assert "$PLTR" in result.headline
    assert "BUY" in result.headline


def test_generate_shareable_headline_with_base_url(value_buy):
    """Test convenience function with base URL."""
    base_url = "https://example.com"
    result = generate_shareable_headline(value_buy, base_url)
    
    assert "Learn more" in result.copy_text
    assert base_url in result.copy_text


# =============================================================================
# Edge Cases and Integration Tests
# =============================================================================


def test_all_emojis_present():
    """Verify all expected emojis are used in headlines."""
    # Create one result for each emoji type
    results = [
        CompressionResult("TEST", 10, 5, 50, 100, CompressionSignal.STRONG_BUY, "high"),
        CompressionResult("TEST", 10, 9, 10, 11, CompressionSignal.BUY, "high"),
        CompressionResult("TEST", 10, 10, 0, 0, CompressionSignal.HOLD, "medium"),
        CompressionResult("TEST", 10, 12, -20, -17, CompressionSignal.SELL, "high"),
        CompressionResult("TEST", 10, 20, -100, -50, CompressionSignal.STRONG_SELL, "high"),
        CompressionResult("TEST", 10, 5, 50, 200, CompressionSignal.DATA_ERROR, "low"),
    ]
    
    headlines = [generate_headline(r) for r in results]
    all_headlines = " ".join(headlines)
    
    # Check all emoji types are present across all headlines
    assert "🚀" in all_headlines
    assert "📈" in all_headlines
    assert "⚖️" in all_headlines
    assert "📉" in all_headlines
    assert "🔴" in all_headlines
    assert "⚠️" in all_headlines


def test_headline_consistency_across_modes():
    """Test that headlines from different modes have consistent structure."""
    value_result = CompressionResult("TEST", 10, 8, 20, 25, CompressionSignal.BUY, "high")
    growth_result = GrowthAnalysisResult("TEST", signal=GrowthSignal.BUY, confidence="high", explanation="Test")
    hyper_result = HyperGrowthAnalysisResult("TEST", signal=HyperGrowthSignal.BUY, confidence="high", explanation="Test")
    
    headlines = [
        generate_headline(value_result),
        generate_headline(growth_result),
        generate_headline(hyper_result),
    ]
    
    # All should have ticker with $
    for h in headlines:
        assert "$TEST" in h
        assert "BUY" in h
        assert len(h) <= 280


def test_special_characters_in_headlines():
    """Test handling of special characters in generated content."""
    result = CompressionResult(
        ticker="BRK-B",  # Ticker with special char
        trailing_pe=10.0,
        forward_pe=8.0,
        compression_pct=20.0,
        implied_growth_pct=25.0,
        signal=CompressionSignal.BUY,
        confidence="high",
    )
    
    shareable = generate_shareable_headline(result)
    
    assert "$BRK-B" in shareable.headline
    # URLs should be encoded properly
    assert "twitter.com" in shareable.twitter_url
    assert "linkedin.com" in shareable.linkedin_url

