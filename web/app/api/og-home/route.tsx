import { ImageResponse } from '@vercel/og';

// ============================================================================
// Configuration
// ============================================================================

export const runtime = 'edge';

// ============================================================================
// Landing Page OG Image
// ============================================================================

export async function GET() {
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
          background: 'linear-gradient(135deg, #6366f1 0%, #8b5cf6 50%, #a855f7 100%)',
          padding: '80px',
          fontFamily: 'system-ui, -apple-system, sans-serif',
          position: 'relative',
        }}
      >
        {/* Background Pattern */}
        <div
          style={{
            position: 'absolute',
            inset: 0,
            background: 'radial-gradient(circle at 20% 20%, rgba(255,255,255,0.1) 0%, transparent 50%)',
            display: 'flex',
          }}
        />
        
        {/* Content */}
        <div
          style={{
            display: 'flex',
            flexDirection: 'column',
            alignItems: 'center',
            gap: '32px',
            zIndex: 1,
          }}
        >
          {/* Logo */}
          <div
            style={{
              fontSize: '96px',
              display: 'flex',
              marginBottom: '16px',
            }}
          >
            📊
          </div>

          {/* Headline */}
          <div
            style={{
              fontSize: '72px',
              fontWeight: 900,
              color: 'white',
              textAlign: 'center',
              lineHeight: 1.1,
              maxWidth: '1000px',
              display: 'flex',
              flexDirection: 'column',
              alignItems: 'center',
            }}
          >
            <div style={{ display: 'flex' }}>Spot Earnings Collapses</div>
            <div style={{ display: 'flex' }}>Before Your Portfolio Does</div>
          </div>

          {/* Subheadline */}
          <div
            style={{
              fontSize: '32px',
              fontWeight: 500,
              color: 'rgba(255, 255, 255, 0.95)',
              textAlign: 'center',
              maxWidth: '900px',
              lineHeight: 1.4,
              display: 'flex',
            }}
          >
            Free P/E compression analysis reveals which stocks are priced for disaster
          </div>

          {/* Features */}
          <div
            style={{
              display: 'flex',
              gap: '48px',
              marginTop: '32px',
            }}
          >
            <div
              style={{
                display: 'flex',
                alignItems: 'center',
                gap: '12px',
                color: 'white',
                fontSize: '24px',
              }}
            >
              <div style={{ fontSize: '32px', display: 'flex' }}>✓</div>
              <div style={{ display: 'flex' }}>30 Second Analysis</div>
            </div>
            <div
              style={{
                display: 'flex',
                alignItems: 'center',
                gap: '12px',
                color: 'white',
                fontSize: '24px',
              }}
            >
              <div style={{ fontSize: '32px', display: 'flex' }}>✓</div>
              <div style={{ display: 'flex' }}>No Credit Card</div>
            </div>
            <div
              style={{
                display: 'flex',
                alignItems: 'center',
                gap: '12px',
                color: 'white',
                fontSize: '24px',
              }}
            >
              <div style={{ fontSize: '32px', display: 'flex' }}>✓</div>
              <div style={{ display: 'flex' }}>10 Free Daily</div>
            </div>
          </div>
        </div>

        {/* Footer */}
        <div
          style={{
            position: 'absolute',
            bottom: '40px',
            fontSize: '28px',
            fontWeight: 600,
            color: 'rgba(255, 255, 255, 0.9)',
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
        'Cache-Control': 'public, max-age=604800, immutable', // Cache for 1 week (static)
      },
    }
  );
}

