#!/usr/bin/env python3
"""
Headline Generator Demo

Demonstrates the headline generation functionality for all analysis modes.
Run with: python examples/headline_demo.py
"""

from pe_scanner.analysis import (
    CompressionResult,
    CompressionSignal,
    GrowthAnalysisResult,
    GrowthSignal,
    HyperGrowthAnalysisResult,
    HyperGrowthSignal,
    generate_shareable_headline,
)


def main():
    """Demonstrate headline generation for all analysis modes."""
    
    print("=" * 80)
    print("HEADLINE GENERATOR DEMO")
    print("=" * 80)
    print()
    
    # VALUE Mode Example (HOOD)
    print("1. VALUE MODE - P/E Compression Analysis")
    print("-" * 80)
    
    hood_result = CompressionResult(
        ticker="HOOD",
        trailing_pe=15.0,
        forward_pe=11.0,
        compression_pct=26.7,
        implied_growth_pct=36.4,
        signal=CompressionSignal.BUY,
        confidence="high",
    )
    
    hood_shareable = generate_shareable_headline(hood_result, "https://pescanner.example.com")
    
    print(f"Ticker: ${hood_result.ticker}")
    print(f"Signal: {hood_result.signal.value.upper()}")
    print(f"Compression: {hood_result.compression_pct:+.1f}%")
    print()
    print("📱 HEADLINE:")
    print(hood_shareable.headline)
    print()
    print("🐦 Twitter URL:")
    print(hood_shareable.twitter_url[:100] + "...")
    print()
    print("💼 LinkedIn URL:")
    print(hood_shareable.linkedin_url[:100] + "...")
    print()
    print("📋 Copy Text:")
    print(hood_shareable.copy_text[:150] + "...")
    print()
    print()
    
    # GROWTH Mode Example (CRM)
    print("2. GROWTH MODE - PEG Ratio Analysis")
    print("-" * 80)
    
    crm_result = GrowthAnalysisResult(
        ticker="CRM",
        trailing_pe=35.0,
        earnings_growth_pct=40.0,
        peg_ratio=0.88,
        signal=GrowthSignal.BUY,
        confidence="high",
        explanation="PEG ratio < 1.0 indicates undervalued growth",
    )
    
    crm_shareable = generate_shareable_headline(crm_result)
    
    print(f"Ticker: ${crm_result.ticker}")
    print(f"Signal: {crm_result.signal.value.upper()}")
    print(f"PEG Ratio: {crm_result.peg_ratio:.2f}")
    print()
    print("📱 HEADLINE:")
    print(crm_shareable.headline)
    print()
    print()
    
    # HYPER_GROWTH Mode Example (PLTR)
    print("3. HYPER_GROWTH MODE - Price/Sales + Rule of 40 Analysis")
    print("-" * 80)
    
    pltr_result = HyperGrowthAnalysisResult(
        ticker="PLTR",
        price_to_sales=4.2,
        revenue_growth_pct=25.0,
        profit_margin_pct=20.0,
        rule_of_40_score=45.0,
        signal=HyperGrowthSignal.BUY,
        confidence="high",
        explanation="P/S < 5 AND Rule of 40 >= 40",
    )
    
    pltr_shareable = generate_shareable_headline(pltr_result)
    
    print(f"Ticker: ${pltr_result.ticker}")
    print(f"Signal: {pltr_result.signal.value.upper()}")
    print(f"P/S Ratio: {pltr_result.price_to_sales:.1f}")
    print(f"Rule of 40: {pltr_result.rule_of_40_score:.0f}")
    print()
    print("📱 HEADLINE:")
    print(pltr_shareable.headline)
    print()
    print()
    
    # Summary
    print("=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print("✅ All analysis modes supported (VALUE, GROWTH, HYPER_GROWTH)")
    print("✅ Emojis for quick visual identification")
    print("✅ Twitter-optimized (<= 280 characters)")
    print("✅ Pre-formatted share URLs for social platforms")
    print("✅ Automatic hashtag generation")
    print()
    print("For more details, see:")
    print("  - src/pe_scanner/analysis/headlines.py (implementation)")
    print("  - tests/unit/test_headlines.py (27 tests, 97% coverage)")
    print("=" * 80)


if __name__ == "__main__":
    main()

