/**
 * Plausible Analytics Integration
 * 
 * Privacy-friendly analytics for StockSignal.
 * No cookies, GDPR compliant, lightweight.
 */

// ============================================================================
// Types
// ============================================================================

/**
 * Plausible event names (custom goals)
 */
export type PlausibleEvent =
  | 'Ticker_Analyzed'
  | 'Headline_Shared'
  | 'Email_Captured'
  | 'Portfolio_Uploaded'
  | 'Upgrade_Clicked'
  | 'Pricing_Viewed'
  | 'Report_Viewed'
  | 'CTA_Clicked'
  | 'Scroll_Depth_25'
  | 'Scroll_Depth_50'
  | 'Scroll_Depth_75'
  | 'Scroll_Depth_100'
  | 'rate_limit_signup_clicked'
  | 'rate_limit_pro_clicked';

/**
 * Event properties for custom dimensions
 */
export interface PlausibleEventProps {
  ticker?: string;
  signal?: 'BUY' | 'SELL' | 'HOLD';
  analysis_mode?: 'VALUE' | 'GROWTH' | 'HYPER_GROWTH';
  platform?: 'twitter' | 'linkedin' | 'copy';
  source?: 'rate_limit' | 'portfolio_gate' | 'footer' | 'hero' | 'nav' | 'ticker_search_form';
  positions?: number;
  type?: 'ISA' | 'SIPP' | 'GENERAL' | 'WISHLIST';
  tier?: 'pro' | 'premium';
  trigger?: 'limit' | 'feature' | 'pricing';
  owner?: boolean;
  variant?: 'primary' | 'secondary' | 'outline';
  label?: string;
  location?: string;
  [key: string]: string | number | boolean | undefined;
}

/**
 * Plausible function signature
 */
declare global {
  interface Window {
    plausible?: (
      event: PlausibleEvent,
      options?: { props?: PlausibleEventProps }
    ) => void;
  }
}

// ============================================================================
// Core Tracking Function
// ============================================================================

/**
 * Track a custom event in Plausible
 * 
 * @param event - Event name (must match Plausible goals)
 * @param props - Event properties (custom dimensions)
 */
export function trackEvent(
  event: PlausibleEvent,
  props?: PlausibleEventProps
): void {
  // Development mode: Log to console instead of sending
  if (process.env.NODE_ENV !== 'production') {
    console.log('[Analytics]', event, props);
    return;
  }

  // Check if Plausible is loaded
  if (typeof window === 'undefined' || !window.plausible) {
    console.warn('[Analytics] Plausible not loaded, event not tracked:', event);
    return;
  }

  try {
    // Send event to Plausible
    window.plausible(event, props ? { props } : undefined);
  } catch (error) {
    console.error('[Analytics] Failed to track event:', event, error);
  }
}

// ============================================================================
// Convenience Functions
// ============================================================================

/**
 * Track ticker analysis
 * 
 * @example
 * trackTickerAnalysis('HOOD', 'SELL', 'VALUE')
 */
export function trackTickerAnalysis(
  ticker: string,
  signal: 'BUY' | 'SELL' | 'HOLD',
  analysisMode: 'VALUE' | 'GROWTH' | 'HYPER_GROWTH'
): void {
  trackEvent('Ticker_Analyzed', {
    ticker,
    signal,
    analysis_mode: analysisMode,
  });
}

/**
 * Track headline share
 * 
 * @example
 * trackHeadlineShared('HOOD', 'twitter')
 */
export function trackHeadlineShared(
  ticker: string,
  platform: 'twitter' | 'linkedin' | 'copy'
): void {
  trackEvent('Headline_Shared', {
    ticker,
    platform,
  });
}

/**
 * Track email capture
 * 
 * @example
 * trackEmailCaptured('portfolio_gate')
 */
export function trackEmailCaptured(
  source: 'rate_limit' | 'portfolio_gate' | 'footer' | 'hero' | 'nav'
): void {
  trackEvent('Email_Captured', {
    source,
  });
}

/**
 * Track portfolio upload
 * 
 * @example
 * trackPortfolioUploaded(17, 'ISA')
 */
export function trackPortfolioUploaded(
  positionCount: number,
  portfolioType: 'ISA' | 'SIPP' | 'GENERAL' | 'WISHLIST'
): void {
  trackEvent('Portfolio_Uploaded', {
    positions: positionCount,
    type: portfolioType,
  });
}

/**
 * Track upgrade click
 * 
 * @example
 * trackUpgradeClicked('pro', 'limit')
 */
export function trackUpgradeClicked(
  tier: 'pro' | 'premium',
  trigger: 'limit' | 'feature' | 'pricing'
): void {
  trackEvent('Upgrade_Clicked', {
    tier,
    trigger,
  });
}

/**
 * Track pricing page view
 * 
 * @example
 * trackPricingViewed()
 */
export function trackPricingViewed(): void {
  trackEvent('Pricing_Viewed');
}

/**
 * Track report page view
 * 
 * @example
 * trackReportViewed('HOOD', false)
 */
export function trackReportViewed(ticker: string, isOwner: boolean): void {
  trackEvent('Report_Viewed', {
    ticker,
    owner: isOwner,
  });
}

/**
 * Track scroll depth milestone
 * 
 * @example
 * trackScrollDepth(50)
 */
export function trackScrollDepth(percentage: 25 | 50 | 75 | 100): void {
  const event = `Scroll_Depth_${percentage}` as PlausibleEvent;
  trackEvent(event);
}

// ============================================================================
// Utility Functions
// ============================================================================

/**
 * Check if analytics is enabled (production + script loaded)
 */
export function isAnalyticsEnabled(): boolean {
  return (
    process.env.NODE_ENV === 'production' &&
    typeof window !== 'undefined' &&
    typeof window.plausible === 'function'
  );
}

/**
 * Get analytics status for debugging
 */
export function getAnalyticsStatus(): {
  enabled: boolean;
  environment: string;
  scriptLoaded: boolean;
} {
  return {
    enabled: isAnalyticsEnabled(),
    environment: process.env.NODE_ENV || 'unknown',
    scriptLoaded: typeof window !== 'undefined' && typeof window.plausible === 'function',
  };
}

