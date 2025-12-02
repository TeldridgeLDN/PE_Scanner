#!/usr/bin/env python3
"""
Social Card Generator Script

Generates social media cards from stocksignal.app analysis results.
Useful for:
- Automated Discord/Reddit bots
- Scheduled social media posts
- Batch analysis sharing
- Testing card formatting

Usage:
    python social_card_generator.py AAPL --format reddit
    python social_card_generator.py NVDA,TSLA,AAPL --format json
    python social_card_generator.py MSFT --format discord --output discord.json
"""

import argparse
import json
import sys
from typing import Dict, Any, List
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.pe_scanner.api.service import AnalysisService
from src.pe_scanner.data.fetcher import DataFetcher


class SocialCardGenerator:
    """Generate social media cards from stock analysis."""
    
    def __init__(self):
        self.fetcher = DataFetcher()
        self.service = AnalysisService(self.fetcher)
    
    def generate_reddit_comment(self, analysis: Dict[str, Any]) -> str:
        """Generate Reddit-formatted markdown comment."""
        signal = analysis['signal']
        ticker = analysis['ticker']
        price = analysis.get('current_price', 0)
        confidence = analysis['confidence']
        mode = analysis['analysis_mode']
        metrics = analysis['metrics']
        
        # Signal emoji
        signal_emoji = {
            'STRONG_BUY': '🚀',
            'BUY': '📈',
            'HOLD': '⚖️',
            'SELL': '📉',
            'STRONG_SELL': '🔴'
        }.get(signal, '📊')
        
        # Confidence bars
        confidence_bars = {
            'high': '███',
            'medium': '██▯',
            'low': '█▯▯'
        }.get(confidence, '▯▯▯')
        
        # Extract key metric
        if 'compression_pct' in metrics:
            metric_label = 'P/E Compression'
            metric_value = f"{metrics['compression_pct']:+.1f}%"
        elif 'peg_ratio' in metrics:
            metric_label = 'PEG Ratio'
            metric_value = f"{metrics['peg_ratio']:.2f}"
        elif 'price_to_sales' in metrics:
            metric_label = 'Price/Sales'
            metric_value = f"{metrics['price_to_sales']:.1f}x"
        else:
            metric_label = 'P/E Ratio'
            metric_value = f"{metrics.get('trailing_pe', 0):.1f}"
        
        # Generate reasoning
        reasoning = self._generate_reasoning(signal, mode, metrics)
        
        return f"""**{signal_emoji} ${ticker} Analysis**

**Signal:** {signal.replace('_', ' ')} | Confidence: {confidence_bars}  
**Price:** ${price:.2f}  
**{metric_label}:** {metric_value}

{reasoning}

*Analysis: {mode}*  
^(stocksignal.app • Free • No signup required)"""
    
    def generate_discord_embed(self, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Generate Discord embed JSON."""
        signal = analysis['signal']
        ticker = analysis['ticker']
        price = analysis.get('current_price', 0)
        confidence = analysis['confidence']
        mode = analysis['analysis_mode']
        metrics = analysis['metrics']
        
        # Color based on signal
        color_map = {
            'STRONG_BUY': 0x10b981,
            'BUY': 0x10b981,
            'HOLD': 0xf59e0b,
            'SELL': 0xef4444,
            'STRONG_SELL': 0xef4444
        }
        color = color_map.get(signal, 0x94a3b8)
        
        # Extract key metric
        if 'compression_pct' in metrics:
            metric_label = 'P/E Compression'
            metric_value = f"{metrics['compression_pct']:+.1f}%"
        elif 'peg_ratio' in metrics:
            metric_label = 'PEG Ratio'
            metric_value = f"{metrics['peg_ratio']:.2f}"
        elif 'price_to_sales' in metrics:
            metric_label = 'Price/Sales'
            metric_value = f"{metrics['price_to_sales']:.1f}x"
        else:
            metric_label = 'P/E Ratio'
            metric_value = f"{metrics.get('trailing_pe', 0):.1f}"
        
        # Generate reasoning
        reasoning = self._generate_reasoning(signal, mode, metrics)
        
        return {
            'title': f'${ticker} - {signal.replace("_", " ")}',
            'description': reasoning,
            'color': color,
            'fields': [
                {
                    'name': 'Price',
                    'value': f'${price:.2f}',
                    'inline': True
                },
                {
                    'name': metric_label,
                    'value': metric_value,
                    'inline': True
                },
                {
                    'name': 'Confidence',
                    'value': confidence.capitalize(),
                    'inline': True
                }
            ],
            'footer': {
                'text': f'{mode} • stocksignal.app'
            }
        }
    
    def generate_json(self, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Generate structured JSON card data."""
        metrics = analysis['metrics']
        mode = analysis['analysis_mode']
        
        # Extract key metric
        if 'compression_pct' in metrics:
            key_metric = {
                'label': 'P/E Compression',
                'value': f"{metrics['compression_pct']:+.1f}%",
                'change': f"{metrics['compression_pct']:+.1f}%"
            }
        elif 'peg_ratio' in metrics:
            key_metric = {
                'label': 'PEG Ratio',
                'value': f"{metrics['peg_ratio']:.2f}"
            }
        elif 'price_to_sales' in metrics:
            key_metric = {
                'label': 'Price/Sales',
                'value': f"{metrics['price_to_sales']:.1f}x"
            }
        else:
            key_metric = {
                'label': 'P/E Ratio',
                'value': f"{metrics.get('trailing_pe', 0):.1f}"
            }
        
        return {
            'ticker': analysis['ticker'],
            'companyName': analysis.get('company_name'),
            'currentPrice': analysis.get('current_price', 0),
            'signal': analysis['signal'],
            'analysisMode': mode,
            'keyMetric': key_metric,
            'reasoning': self._generate_reasoning(analysis['signal'], mode, metrics),
            'confidence': analysis['confidence']
        }
    
    def _generate_reasoning(self, signal: str, mode: str, metrics: Dict[str, Any]) -> str:
        """Generate reasoning text based on analysis mode."""
        mode_upper = mode.upper()
        
        # VALUE mode (P/E Compression)
        if 'VALUE' in mode_upper or 'P/E' in mode_upper:
            compression = metrics.get('compression_pct', 0)
            
            if 'BUY' in signal:
                return f"Market expects earnings growth. Forward P/E compressed {abs(compression):.1f}%, indicating undervaluation relative to growth prospects."
            elif 'SELL' in signal:
                return f"Market expects earnings decline. Forward P/E expanded {abs(compression):.1f}%, suggesting overvaluation at current levels."
            else:
                return f"P/E compression of {compression:.1f}% suggests neutral outlook. Fairly valued at current price."
        
        # GROWTH mode (PEG Ratio)
        if 'GROWTH' in mode_upper or 'PEG' in mode_upper:
            peg = metrics.get('peg_ratio', 0)
            
            if 'BUY' in signal:
                return f"PEG ratio of {peg:.2f} means you're paying ${peg:.2f} per 1% of growth. Attractive valuation for growth rate."
            elif 'SELL' in signal:
                return f"PEG ratio of {peg:.2f} suggests you're overpaying for growth. High valuation relative to earnings growth rate."
            else:
                return f"PEG ratio of {peg:.2f} indicates fair valuation. Price aligned with growth expectations."
        
        # HYPER_GROWTH mode (P/S + Rule of 40)
        if 'HYPER' in mode_upper or 'P/S' in mode_upper:
            ps = metrics.get('price_to_sales', 0)
            ro40 = metrics.get('rule_of_40_score', 0)
            
            if 'BUY' in signal:
                return f"P/S of {ps:.1f} with Rule of 40 score {ro40:.0f} shows strong fundamentals. Reasonable valuation for high-growth profile."
            elif 'SELL' in signal:
                if ps > 15:
                    return f"P/S ratio of {ps:.1f} is excessive. Valuation too rich even considering high growth potential."
                else:
                    return f"Rule of 40 score {ro40:.0f} shows weak fundamentals. Growth + profitability metrics concerning."
            else:
                return f"P/S {ps:.1f} and Rule of 40 score {ro40:.0f} show mixed signals. Fairly valued at current levels."
        
        # Fallback
        return f"Analysis suggests {signal.lower().replace('_', ' ')} signal based on current valuation metrics."
    
    def generate(self, ticker: str, format: str = 'json') -> str:
        """Generate social card for a ticker."""
        # Get analysis
        analysis = self.service.analyze(
            ticker=ticker,
            include_headline=False,
            include_anchor=False
        )
        
        # Generate in requested format
        if format == 'reddit':
            return self.generate_reddit_comment(analysis)
        elif format == 'discord':
            return json.dumps(self.generate_discord_embed(analysis), indent=2)
        else:  # json
            return json.dumps(self.generate_json(analysis), indent=2)
    
    def generate_batch(self, tickers: List[str], format: str = 'json') -> str:
        """Generate social cards for multiple tickers."""
        results = []
        
        for ticker in tickers:
            try:
                print(f"Analyzing {ticker}...", file=sys.stderr)
                analysis = self.service.analyze(
                    ticker=ticker,
                    include_headline=False,
                    include_anchor=False
                )
                
                if format == 'reddit':
                    results.append(self.generate_reddit_comment(analysis))
                elif format == 'discord':
                    results.append(self.generate_discord_embed(analysis))
                else:  # json
                    results.append(self.generate_json(analysis))
                    
            except Exception as e:
                print(f"Error analyzing {ticker}: {e}", file=sys.stderr)
                continue
        
        if format in ['discord', 'json']:
            return json.dumps(results, indent=2)
        else:  # reddit
            return '\n\n---\n\n'.join(results)


def main():
    parser = argparse.ArgumentParser(
        description='Generate social media cards from stocksignal.app analysis'
    )
    parser.add_argument(
        'tickers',
        help='Stock ticker(s) to analyze (comma-separated for multiple)'
    )
    parser.add_argument(
        '--format', '-f',
        choices=['json', 'reddit', 'discord'],
        default='json',
        help='Output format (default: json)'
    )
    parser.add_argument(
        '--output', '-o',
        help='Output file (default: stdout)'
    )
    
    args = parser.parse_args()
    
    # Parse tickers
    tickers = [t.strip().upper() for t in args.tickers.split(',')]
    
    # Generate cards
    generator = SocialCardGenerator()
    
    if len(tickers) == 1:
        result = generator.generate(tickers[0], args.format)
    else:
        result = generator.generate_batch(tickers, args.format)
    
    # Output
    if args.output:
        with open(args.output, 'w') as f:
            f.write(result)
        print(f"Saved to {args.output}", file=sys.stderr)
    else:
        print(result)


if __name__ == '__main__':
    main()

