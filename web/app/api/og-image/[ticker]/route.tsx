import { ImageResponse } from '@vercel/og';
import { NextRequest } from 'next/server';

// ============================================================================
// Configuration
// ============================================================================

export const runtime = 'edge';

// ============================================================================
// Signal-Based Gradients
// ============================================================================

const GRADIENTS = {
  BUY: 'linear-gradient(135deg, #10b981 0%, #14b8a6 100%)', // Emerald to Teal
  SELL: 'linear-gradient(135deg, #ef4444 0%, #f43f5e 100%)', // Red to Rose
  HOLD: 'linear-gradient(135deg, #f59e0b 0%, #f97316 100%)', // Amber to Orange
};

const SIGNAL_EMOJI = {
  BUY: '🟢',
  SELL: '🔴',
  HOLD: '🟡',
};

// ============================================================================
// Helper Functions
// ============================================================================

function truncate(text: string, maxLength: number): string {
  if (text.length <= maxLength) return text;
  return text.slice(0, maxLength - 3) + '...';
}

function getMetricDisplay(analysis: any): string {
  if (analysis.analysis_mode === 'VALUE' && analysis.metrics.compression_pct !== undefined) {
    const compression = analysis.metrics.compression_pct;
    return `Compression: ${compression > 0 ? '+' : ''}${compression.toFixed(1)}%`;
  }
  
  if (analysis.analysis_mode === 'GROWTH' && analysis.metrics.peg_ratio) {
    return `PEG Ratio: ${analysis.metrics.peg_ratio.toFixed(2)}`;
  }
  
  if (analysis.analysis_mode === 'HYPER_GROWTH' && analysis.metrics.price_to_sales) {
    return `P/S: ${analysis.metrics.price_to_sales.toFixed(2)}x`;
  }
  
  // Fallback
  if (analysis.metrics.trailing_pe) {
    return `P/E: ${analysis.metrics.trailing_pe.toFixed(1)}`;
  }
  
  return '';
}

// ============================================================================
// API Route Handler
// ============================================================================

export async function GET(
  request: NextRequest,
  { params }: { params: Promise<{ ticker: string }> }
) {
  try {
    const { ticker } = await params;
    
    // Fetch analysis data from backend
    const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:5000';
    const analysisUrl = `${apiUrl}/api/analyze/${ticker}?include_headline=true&include_anchor=true`;
    
    const response = await fetch(analysisUrl, {
      next: { revalidate: 3600 }, // Cache for 1 hour
    });
    
    if (!response.ok) {
      throw new Error(`API returned ${response.status}`);
    }
    
    const analysis = await response.json();
    
    // Extract key data
    const signal = analysis.signal || 'HOLD';
    const headline = analysis.headline 
      ? truncate(analysis.headline, 80)
      : `${ticker} ${signal} Signal`;
    const metric = getMetricDisplay(analysis);
    const gradient = GRADIENTS[signal as keyof typeof GRADIENTS] || GRADIENTS.HOLD;
    const emoji = SIGNAL_EMOJI[signal as keyof typeof SIGNAL_EMOJI] || SIGNAL_EMOJI.HOLD;
    
    // Generate OG image
    return new ImageResponse(
      (
        <div
          style={{
            height: '100%',
            width: '100%',
            display: 'flex',
            flexDirection: 'column',
            alignItems: 'center',
            justifyContent: 'space-between',
            background: gradient,
            padding: '60px',
            fontFamily: 'system-ui, -apple-system, sans-serif',
          }}
        >
          {/* Header: PE Scanner Logo */}
          <div
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: '12px',
            }}
          >
            <div
              style={{
                fontSize: '40px',
                display: 'flex',
              }}
            >
              📊
            </div>
            <div
              style={{
                fontSize: '32px',
                fontWeight: 700,
                color: 'white',
                display: 'flex',
              }}
            >
              PE Scanner
            </div>
          </div>

          {/* Center: Ticker & Signal */}
          <div
            style={{
              display: 'flex',
              flexDirection: 'column',
              alignItems: 'center',
              gap: '24px',
            }}
          >
            {/* Ticker Symbol */}
            <div
              style={{
                fontSize: '96px',
                fontWeight: 900,
                color: 'white',
                letterSpacing: '-0.02em',
                display: 'flex',
              }}
            >
              {ticker}
            </div>

            {/* Signal Badge */}
            <div
              style={{
                display: 'flex',
                alignItems: 'center',
                gap: '16px',
                background: 'rgba(255, 255, 255, 0.95)',
                padding: '20px 48px',
                borderRadius: '16px',
                boxShadow: '0 8px 32px rgba(0, 0, 0, 0.15)',
              }}
            >
              <div style={{ fontSize: '48px', display: 'flex' }}>{emoji}</div>
              <div
                style={{
                  fontSize: '48px',
                  fontWeight: 800,
                  color: '#1e293b',
                  display: 'flex',
                }}
              >
                {signal}
              </div>
            </div>

            {/* Headline */}
            <div
              style={{
                fontSize: '36px',
                fontWeight: 600,
                color: 'white',
                textAlign: 'center',
                maxWidth: '900px',
                lineHeight: 1.3,
                display: 'flex',
              }}
            >
              {headline}
            </div>

            {/* Key Metric */}
            {metric && (
              <div
                style={{
                  fontSize: '28px',
                  fontWeight: 500,
                  color: 'rgba(255, 255, 255, 0.9)',
                  display: 'flex',
                }}
              >
                {metric}
              </div>
            )}
          </div>

          {/* Footer: URL */}
          <div
            style={{
              fontSize: '24px',
              fontWeight: 400,
              color: 'rgba(255, 255, 255, 0.8)',
              display: 'flex',
            }}
          >
            pe-scanner.com
          </div>
        </div>
      ),
      {
        width: 1200,
        height: 630,
        headers: {
          'Cache-Control': 'public, max-age=3600, s-maxage=3600, stale-while-revalidate=86400',
        },
      }
    );
  } catch (error) {
    console.error('OG Image generation error:', error);
    
    // Return fallback image on error
    // In production, you'd serve a static fallback image
    return new ImageResponse(
      (
        <div
          style={{
            height: '100%',
            width: '100%',
            display: 'flex',
            flexDirection: 'column',
            alignItems: 'center',
            justifyContent: 'center',
            background: 'linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%)',
            padding: '60px',
            fontFamily: 'system-ui, -apple-system, sans-serif',
          }}
        >
          <div
            style={{
              fontSize: '72px',
              display: 'flex',
              marginBottom: '24px',
            }}
          >
            📊
          </div>
          <div
            style={{
              fontSize: '64px',
              fontWeight: 800,
              color: 'white',
              marginBottom: '16px',
              display: 'flex',
            }}
          >
            PE Scanner
          </div>
          <div
            style={{
              fontSize: '32px',
              fontWeight: 500,
              color: 'rgba(255, 255, 255, 0.9)',
              textAlign: 'center',
              display: 'flex',
            }}
          >
            Stock Valuation Made Simple
          </div>
        </div>
      ),
      {
        width: 1200,
        height: 630,
      }
    );
  }
}

