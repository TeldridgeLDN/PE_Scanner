'use client';

import { useEffect } from 'react';
import { trackTickerAnalysis, trackReportViewed } from '@/lib/analytics/plausible';

// ============================================================================
// Types
// ============================================================================

interface ReportPageTrackerProps {
  ticker: string;
  signal: 'BUY' | 'SELL' | 'HOLD';
  analysisMode: 'VALUE' | 'GROWTH' | 'HYPER_GROWTH';
}

// ============================================================================
// ReportPageTracker Component
// ============================================================================

/**
 * Client component to track report page views
 * 
 * Fires analytics events when results page is viewed.
 * Must be a client component because useEffect is needed.
 */
export default function ReportPageTracker({ 
  ticker, 
  signal, 
  analysisMode 
}: ReportPageTrackerProps) {
  useEffect(() => {
    // Track full analysis with signal and mode
    trackTickerAnalysis(ticker, signal, analysisMode);
    
    // Track report view (for page view metrics)
    trackReportViewed(ticker, false); // false = not owner (anonymous view)
  }, [ticker, signal, analysisMode]);

  // No visual component (tracking only)
  return null;
}

