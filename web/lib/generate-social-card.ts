/**
 * Social Media Card Generator
 * 
 * Converts analysis results into social media card data
 * optimized for Reddit, Discord, Twitter contexts.
 * 
 * Focuses on clarity and value, not promotional content.
 */

interface AnalysisResult {
  ticker: string;
  company_name?: string;
  current_price: number;
  analysis_mode: string;
  signal: 'BUY' | 'SELL' | 'HOLD' | 'STRONG_BUY' | 'STRONG_SELL';
  confidence: 'high' | 'medium' | 'low';
  metrics: Record<string, any>;
  anchor?: string; // "What Would Have To Be True" statement
}

interface SocialCardData {
  ticker: string;
  companyName?: string;
  currentPrice: number;
  signal: 'BUY' | 'SELL' | 'HOLD' | 'STRONG_BUY' | 'STRONG_SELL';
  analysisMode: string;
  keyMetric: {
    label: string;
    value: string;
    change?: string;
  };
  reasoning: string;
  confidence: 'high' | 'medium' | 'low';
  anchor?: string; // "What Would Have To Be True" statement
}

/**
 * Generate Reddit-optimized reasoning text
 * Short, factual, non-promotional
 */
function generateReasoning(
  signal: string,
  analysisMode: string,
  metrics: Record<string, any>
): string {
  const mode = analysisMode.toUpperCase();

  // VALUE mode (P/E Compression)
  if (mode.includes('VALUE') || mode.includes('P/E')) {
    const compression = metrics.compression_pct || 0;
    
    if (signal.includes('BUY')) {
      return `Market expects earnings growth. Forward P/E compressed ${Math.abs(compression).toFixed(1)}%, indicating undervaluation relative to growth prospects.`;
    } else if (signal.includes('SELL')) {
      return `Market expects earnings decline. Forward P/E expanded ${Math.abs(compression).toFixed(1)}%, suggesting overvaluation at current levels.`;
    } else {
      return `P/E compression of ${compression.toFixed(1)}% suggests neutral outlook. Fairly valued at current price.`;
    }
  }

  // GROWTH mode (PEG Ratio)
  if (mode.includes('GROWTH') || mode.includes('PEG')) {
    const peg = metrics.peg_ratio || 0;
    
    if (signal.includes('BUY')) {
      return `PEG ratio of ${peg.toFixed(2)} means you're paying $${peg.toFixed(2)} per 1% of growth. Attractive valuation for growth rate.`;
    } else if (signal.includes('SELL')) {
      return `PEG ratio of ${peg.toFixed(2)} suggests you're overpaying for growth. High valuation relative to earnings growth rate.`;
    } else {
      return `PEG ratio of ${peg.toFixed(2)} indicates fair valuation. Price aligned with growth expectations.`;
    }
  }

  // HYPER_GROWTH mode (P/S + Rule of 40)
  if (mode.includes('HYPER') || mode.includes('P/S')) {
    const ps = metrics.price_to_sales || 0;
    const ro40 = metrics.rule_of_40_score || 0;
    
    if (signal.includes('BUY')) {
      return `P/S of ${ps.toFixed(1)} with Rule of 40 score ${ro40.toFixed(0)} shows strong fundamentals. Reasonable valuation for high-growth profile.`;
    } else if (signal.includes('SELL')) {
      if (ps > 15) {
        return `P/S ratio of ${ps.toFixed(1)} is excessive. Valuation too rich even considering high growth potential.`;
      } else {
        return `Rule of 40 score ${ro40.toFixed(0)} shows weak fundamentals. Growth + profitability metrics concerning.`;
      }
    } else {
      return `P/S ${ps.toFixed(1)} and Rule of 40 score ${ro40.toFixed(0)} show mixed signals. Fairly valued at current levels.`;
    }
  }

  // Fallback
  return `Analysis suggests ${signal.toLowerCase().replace('_', ' ')} signal based on current valuation metrics.`;
}

/**
 * Extract key metric for display
 */
function extractKeyMetric(
  analysisMode: string,
  metrics: Record<string, any>
): { label: string; value: string; change?: string } {
  const mode = analysisMode.toUpperCase();

  // VALUE mode - show P/E Compression
  if (mode.includes('VALUE') || mode.includes('P/E')) {
    const compression = metrics.compression_pct || 0;
    return {
      label: 'P/E Compression',
      value: `${compression > 0 ? '+' : ''}${compression.toFixed(1)}%`,
      change: `${compression > 0 ? '+' : ''}${compression.toFixed(1)}%`
    };
  }

  // GROWTH mode - show PEG Ratio
  if (mode.includes('GROWTH') || mode.includes('PEG')) {
    const peg = metrics.peg_ratio || 0;
    return {
      label: 'PEG Ratio',
      value: peg.toFixed(2),
    };
  }

  // HYPER_GROWTH mode - show P/S Ratio
  if (mode.includes('HYPER') || mode.includes('P/S')) {
    const ps = metrics.price_to_sales || 0;
    return {
      label: 'Price/Sales',
      value: `${ps.toFixed(1)}x`,
    };
  }

  // Fallback - show trailing P/E if available
  const trailingPE = metrics.trailing_pe;
  if (trailingPE) {
    return {
      label: 'P/E Ratio',
      value: trailingPE.toFixed(1),
    };
  }

  return {
    label: 'Signal',
    value: 'See Analysis'
  };
}

/**
 * Convert API analysis result to social card data
 */
export function generateSocialCardData(result: AnalysisResult): SocialCardData {
  return {
    ticker: result.ticker,
    companyName: result.company_name,
    currentPrice: result.current_price,
    signal: result.signal,
    analysisMode: result.analysis_mode,
    keyMetric: extractKeyMetric(result.analysis_mode, result.metrics),
    reasoning: generateReasoning(result.signal, result.analysis_mode, result.metrics),
    confidence: result.confidence,
    anchor: result.anchor // Include anchor if provided by API
  };
}

/**
 * Generate plain text version for Reddit comments
 * Markdown-formatted for Reddit
 */
export function generateRedditComment(data: SocialCardData): string {
  const signalEmoji = {
    'STRONG_BUY': '🚀',
    'BUY': '📈',
    'HOLD': '⚖️',
    'SELL': '📉',
    'STRONG_SELL': '🔴'
  }[data.signal];

  const confidenceBars = {
    'high': '███',
    'medium': '██▯',
    'low': '█▯▯'
  }[data.confidence];

  let comment = `**${signalEmoji} $${data.ticker} Analysis**

**Signal:** ${data.signal.replace('_', ' ')} | Confidence: ${confidenceBars}  
**Price:** $${data.currentPrice.toFixed(2)}  
**${data.keyMetric.label}:** ${data.keyMetric.value}${data.keyMetric.change ? ` (${data.keyMetric.change})` : ''}

${data.reasoning}`;

  // Add anchor if available (makes it more concrete)
  if (data.anchor) {
    comment += `\n\n**What Would Have To Be True:** ${data.anchor}`;
  }

  comment += `\n\n*Analysis: ${data.analysisMode}*  
^(stocksignal.app • Free • No signup required)`;

  return comment;
}

/**
 * Generate Discord embed data
 */
export function generateDiscordEmbed(data: SocialCardData) {
  const color = data.signal.includes('BUY') 
    ? 0x10b981  // Green
    : data.signal.includes('SELL')
    ? 0xef4444  // Red
    : 0xf59e0b; // Amber

  return {
    title: `$${data.ticker} - ${data.signal.replace('_', ' ')}`,
    description: data.reasoning,
    color: color,
    fields: [
      {
        name: 'Price',
        value: `$${data.currentPrice.toFixed(2)}`,
        inline: true
      },
      {
        name: data.keyMetric.label,
        value: data.keyMetric.value,
        inline: true
      },
      {
        name: 'Confidence',
        value: data.confidence.charAt(0).toUpperCase() + data.confidence.slice(1),
        inline: true
      }
    ],
    footer: {
      text: `${data.analysisMode} • stocksignal.app`
    },
    timestamp: new Date().toISOString()
  };
}

