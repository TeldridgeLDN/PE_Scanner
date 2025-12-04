import { Metadata } from 'next';
import Link from 'next/link';
import { fetchAnalysis, AnalysisResponse } from '@/lib/api/client';
import { ErrorDisplay } from '@/components/ErrorDisplay';
import ShareButtons from '@/components/ShareButtons';
import ReportPageTracker from '@/components/ReportPageTracker';
import { generateReportMetadata } from '@/lib/metadata';

// ============================================================================
// Types
// ============================================================================

interface PageProps {
  params: Promise<{ ticker: string }>;
}

// ============================================================================
// Metadata
// ============================================================================

export async function generateMetadata({ params }: PageProps): Promise<Metadata> {
  const { ticker } = await params;
  const { data: analysis } = await fetchAnalysis(ticker);

  // Use comprehensive metadata generator with full OG and Twitter Card tags
  return generateReportMetadata(ticker, analysis || undefined);
}

// ============================================================================
// Page Component
// ============================================================================

export default async function ReportPage({ params }: PageProps) {
  const { ticker } = await params;
  const { data: analysis, error } = await fetchAnalysis(ticker);

  // Handle errors with user-friendly error display
  if (error) {
    return <ErrorDisplay error={error} ticker={ticker} />;
  }

  // Should not happen, but TypeScript needs this
  if (!analysis) {
    return <ErrorDisplay error={{ status: 500, message: 'No data returned' }} ticker={ticker} />;
  }

  // Signal styles with inline colors to ensure visibility
  const signalStyles: Record<string, { bg: string; text: string }> = {
    BUY: { bg: '#10b981', text: '#ffffff' },      // Emerald/Green
    SELL: { bg: '#ef4444', text: '#ffffff' },     // Red
    HOLD: { bg: '#f59e0b', text: '#ffffff' },     // Amber
    'DATA ERROR': { bg: '#f59e0b', text: '#ffffff' },
  };

  // SVG icons for each signal type
  const SignalIcon = ({ signal }: { signal: string }) => {
    switch (signal) {
      case 'BUY':
        // Upward trending arrow
        return (
          <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2.5} d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6" />
          </svg>
        );
      case 'SELL':
        // Downward trending arrow
        return (
          <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2.5} d="M13 17h8m0 0v-8m0 8l-8-8-4 4-6-6" />
          </svg>
        );
      case 'HOLD':
        // Horizontal line / pause
        return (
          <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2.5} d="M5 12h14" />
          </svg>
        );
      default:
        // Warning/error icon
        return (
          <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2.5} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
          </svg>
        );
    }
  };

  return (
    <div className="min-h-screen bg-slate-50">
      {/* Analytics Tracking */}
      <ReportPageTracker
        ticker={analysis.ticker}
        signal={analysis.signal}
        analysisMode={analysis.analysis_mode}
      />
      
      {/* Navigation */}
      <nav className="bg-white border-b border-slate-200">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            <Link href="/" className="flex items-center gap-2">
              <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-[#0d9488] to-[#0369a1] flex items-center justify-center">
                <span className="text-white font-bold text-lg">PE</span>
              </div>
              <span className="font-heading font-bold text-xl text-slate-900">StockSignal</span>
            </Link>
            <Link 
              href="/"
              className="text-sm font-semibold text-slate-700 hover:text-primary transition-colors flex items-center gap-1"
            >
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 19l-7-7m0 0l7-7m-7 7h18" />
              </svg>
              Analyze Another
            </Link>
          </div>
        </div>
      </nav>

      {/* Main Content */}
      <main className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Results Card */}
        <div className="bg-white rounded-2xl shadow-lg border border-slate-200 p-8 mb-6 animate-fade-in">
          {/* Signal Badge */}
          <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 mb-6 pb-6 border-b border-slate-200">
            <div className="flex items-center gap-3">
              <div 
                className="px-6 py-3 rounded-xl font-bold text-2xl flex items-center gap-2"
                style={{ 
                  backgroundColor: signalStyles[analysis.signal]?.bg || signalStyles['DATA ERROR'].bg,
                  color: signalStyles[analysis.signal]?.text || signalStyles['DATA ERROR'].text
                }}
              >
                <SignalIcon signal={analysis.signal} />
                {analysis.signal}
              </div>
              <div className="text-sm">
                <div className="font-semibold text-slate-900">{analysis.ticker}</div>
                <div className="text-slate-500">{analysis.analysis_mode} Mode</div>
              </div>
            </div>
            <div className="text-right">
              <div className="text-sm text-slate-500">Confidence</div>
              <div className="font-semibold text-slate-900 capitalize">{analysis.confidence}</div>
            </div>
          </div>

          {/* Headline */}
          {analysis.headline && (
            <div className="mb-6">
              <h1 className="text-2xl sm:text-3xl font-bold text-slate-900 leading-tight">
                {analysis.headline}
              </h1>
            </div>
          )}

          {/* Anchor Statement */}
          {analysis.anchor && (
            <div className="mb-6 p-4 bg-slate-50 rounded-xl border border-slate-200">
              <div className="text-xs font-semibold text-slate-500 uppercase tracking-wide mb-2">
                What Would Have To Be True
              </div>
              <p className="text-slate-700 italic">
                "{analysis.anchor}"
              </p>
            </div>
          )}

          {/* Metrics Grid */}
          <div className="mb-6">
            <h2 className="text-lg font-bold text-slate-900 mb-4">Key Metrics</h2>
            <div className="grid grid-cols-2 sm:grid-cols-3 gap-4">
              {/* Current Price */}
              {analysis.metrics.current_price && (
                <div className="p-4 bg-slate-50 rounded-lg">
                  <div className="text-xs text-slate-500 mb-1">Current Price</div>
                  <div className="text-xl font-bold text-slate-900">
                    ${analysis.metrics.current_price.toFixed(2)}
                  </div>
                </div>
              )}

              {/* Trailing P/E */}
              {analysis.metrics.trailing_pe && (
                <div className="p-4 bg-slate-50 rounded-lg">
                  <div className="text-xs text-slate-500 mb-1">Trailing P/E</div>
                  <div className="text-xl font-bold text-slate-900">
                    {analysis.metrics.trailing_pe.toFixed(2)}
                  </div>
                  <div className={`text-xs font-semibold mt-1 ${
                    analysis.metrics.trailing_pe < 15 
                      ? 'text-emerald-600' 
                      : analysis.metrics.trailing_pe < 25 
                        ? 'text-slate-500' 
                        : 'text-amber-600'
                  }`}>
                    {analysis.metrics.trailing_pe < 15 
                      ? '✓ Cheap (under 15)' 
                      : analysis.metrics.trailing_pe < 25 
                        ? '• Fair (15-25)' 
                        : analysis.metrics.trailing_pe < 50 
                          ? '⚠ Expensive (25-50)' 
                          : '⚠ Very expensive (50+)'}
                  </div>
                </div>
              )}

              {/* Forward P/E */}
              {analysis.metrics.forward_pe && (
                <div className="p-4 bg-slate-50 rounded-lg">
                  <div className="text-xs text-slate-500 mb-1">Forward P/E</div>
                  <div className="text-xl font-bold text-slate-900">
                    {analysis.metrics.forward_pe.toFixed(2)}
                  </div>
                </div>
              )}

              {/* P/E Compression */}
              {analysis.metrics.compression_pct !== undefined && (
                <div className="p-4 bg-slate-50 rounded-lg">
                  <div className="text-xs text-slate-500 mb-1">P/E Compression</div>
                  <div 
                    className="text-xl font-bold"
                    style={{ color: analysis.metrics.compression_pct > 0 ? '#059669' : '#dc2626' }}
                  >
                    {analysis.metrics.compression_pct > 0 ? '+' : ''}
                    {analysis.metrics.compression_pct.toFixed(1)}%
                  </div>
                  <div className={`text-xs font-semibold mt-1 ${
                    analysis.metrics.compression_pct > 10 
                      ? 'text-emerald-600' 
                      : analysis.metrics.compression_pct > 0 
                        ? 'text-slate-500' 
                        : 'text-amber-600'
                  }`}>
                    {analysis.metrics.compression_pct > 10 
                      ? '✓ Strong growth expected' 
                      : analysis.metrics.compression_pct > 0 
                        ? '• Mild growth expected' 
                        : analysis.metrics.compression_pct > -10 
                          ? '⚠ Mild decline expected' 
                          : '⚠ Sharp decline expected'}
                  </div>
                </div>
              )}

              {/* PEG Ratio (GROWTH mode) */}
              {analysis.metrics.peg_ratio && (
                <div className="p-4 bg-slate-50 rounded-lg">
                  <div className="text-xs text-slate-500 mb-1">PEG Ratio</div>
                  <div className="text-xl font-bold text-slate-900">
                    {analysis.metrics.peg_ratio.toFixed(2)}
                  </div>
                  <div className={`text-xs font-semibold mt-1 ${
                    analysis.metrics.peg_ratio < 1 
                      ? 'text-emerald-600' 
                      : analysis.metrics.peg_ratio < 2 
                        ? 'text-slate-500' 
                        : 'text-amber-600'
                  }`}>
                    {analysis.metrics.peg_ratio < 1 
                      ? '✓ Undervalued (under 1)' 
                      : analysis.metrics.peg_ratio < 2 
                        ? '• Fair value (1-2)' 
                        : '⚠ Overvalued (2+)'}
                  </div>
                </div>
              )}

              {/* Earnings Growth (GROWTH mode) */}
              {analysis.metrics.earnings_growth && (
                <div className="p-4 bg-slate-50 rounded-lg">
                  <div className="text-xs text-slate-500 mb-1">Earnings Growth</div>
                  <div className="text-xl font-bold text-slate-900">
                    {analysis.metrics.earnings_growth.toFixed(1)}%
                  </div>
                </div>
              )}

              {/* Price/Sales (HYPER_GROWTH mode) */}
              {analysis.metrics.price_to_sales && (
                <div className="p-4 bg-slate-50 rounded-lg">
                  <div className="text-xs text-slate-500 mb-1">Price/Sales</div>
                  <div className="text-xl font-bold text-slate-900">
                    {analysis.metrics.price_to_sales.toFixed(2)}x
                  </div>
                  <div className={`text-xs font-semibold mt-1 ${
                    analysis.metrics.price_to_sales < 5 
                      ? 'text-emerald-600' 
                      : analysis.metrics.price_to_sales < 10 
                        ? 'text-slate-500' 
                        : 'text-amber-600'
                  }`}>
                    {analysis.metrics.price_to_sales < 5 
                      ? '✓ Cheap (under 5x)' 
                      : analysis.metrics.price_to_sales < 10 
                        ? '• Fair (5-10x)' 
                        : analysis.metrics.price_to_sales < 15 
                          ? '⚠ Expensive (10-15x)' 
                          : '⚠ Very expensive (15x+)'}
                  </div>
                </div>
              )}

              {/* Growth + Profit Score (HYPER_GROWTH mode) */}
              {analysis.metrics.rule_of_40 !== undefined && (
                <div className="p-4 bg-slate-50 rounded-lg">
                  <div className="text-xs text-slate-500 mb-1">Growth + Profit</div>
                  <div className="text-xl font-bold text-slate-900">
                    {analysis.metrics.rule_of_40.toFixed(0)}
                  </div>
                  <div className={`text-xs font-semibold mt-1 ${
                    analysis.metrics.rule_of_40 >= 40 ? 'text-emerald-600' : 'text-amber-600'
                  }`}>
                    {analysis.metrics.rule_of_40 >= 40 ? '✓ Healthy (40+)' : '⚠ Below healthy (40+)'}
                  </div>
                </div>
              )}
            </div>
          </div>

          {/* Fair Value Scenarios */}
          {analysis.fair_value && (
            <div className="mb-6">
              <h2 className="text-lg font-bold text-slate-900 mb-4">Fair Value Scenarios</h2>
              <div className="grid sm:grid-cols-2 gap-4">
                {/* Bear Case */}
                {analysis.fair_value.bear_case && (
                  <div className="p-4 bg-red-50 rounded-lg border border-red-200">
                    <div className="text-xs font-semibold text-red-600 uppercase tracking-wide mb-1">
                      Bear Case
                    </div>
                    <div className="text-2xl font-bold text-red-700 mb-1">
                      ${analysis.fair_value.bear_case.toFixed(2)}
                    </div>
                    {analysis.fair_value.bear_pe && (
                      <div className="text-xs text-red-600">
                        {analysis.fair_value.bear_pe.toFixed(1)}x P/E
                      </div>
                    )}
                    {analysis.metrics.current_price && (
                      <div className="text-xs text-red-600 mt-2">
                        {((analysis.fair_value.bear_case / analysis.metrics.current_price - 1) * 100).toFixed(0)}% from current
                      </div>
                    )}
                  </div>
                )}

                {/* Bull Case */}
                {analysis.fair_value.bull_case && (
                  <div className="p-4 bg-green-50 rounded-lg border border-green-200">
                    <div className="text-xs font-semibold text-green-600 uppercase tracking-wide mb-1">
                      Bull Case
                    </div>
                    <div className="text-2xl font-bold text-green-700 mb-1">
                      ${analysis.fair_value.bull_case.toFixed(2)}
                    </div>
                    {analysis.fair_value.bull_pe && (
                      <div className="text-xs text-green-600">
                        {analysis.fair_value.bull_pe.toFixed(1)}x P/E
                      </div>
                    )}
                    {analysis.metrics.current_price && (
                      <div className="text-xs text-green-600 mt-2">
                        +{((analysis.fair_value.bull_case / analysis.metrics.current_price - 1) * 100).toFixed(0)}% upside
                      </div>
                    )}
                  </div>
                )}
              </div>
            </div>
          )}

          {/* Data Quality Flags */}
          {analysis.data_quality && ((analysis.data_quality.flags?.length ?? 0) > 0 || analysis.data_quality.uk_corrected) && (
            <div className="mb-6">
              <h2 className="text-lg font-bold text-slate-900 mb-4">Data Quality</h2>
              <div className="space-y-2">
                {analysis.data_quality.uk_corrected && (
                  <div className="flex items-start gap-2 text-sm text-slate-600">
                    <svg className="w-5 h-5 text-buy flex-shrink-0 mt-0.5" fill="currentColor" viewBox="0 0 20 20">
                      <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                    </svg>
                    <span>UK stock data automatically corrected (pence → pounds)</span>
                  </div>
                )}
                {analysis.data_quality.flags?.map((flag, index) => (
                  <div key={index} className="flex items-start gap-2 text-sm text-amber-700">
                    <svg className="w-5 h-5 flex-shrink-0 mt-0.5" fill="currentColor" viewBox="0 0 20 20">
                      <path fillRule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
                    </svg>
                    <span>{flag}</span>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Share Buttons */}
          <div className="border-t border-slate-200 pt-6">
            <ShareButtons 
              ticker={analysis.ticker}
              headline={analysis.headline || `${analysis.ticker} ${analysis.signal}`}
              shareUrls={analysis.share_urls}
            />
          </div>
        </div>

        {/* CTA Card */}
        <div className="bg-gradient-to-br from-[#0d9488] to-[#0369a1] rounded-2xl shadow-lg p-8 text-white text-center animate-slide-up">
          <h2 className="text-2xl font-bold mb-3">
            Want to Scan Your Whole Portfolio?
          </h2>
          <p className="text-primary-light mb-6">
            Upload your portfolio CSV and get ranked analysis for all your holdings
          </p>
          <button className="px-8 py-4 bg-white text-slate-900 rounded-xl font-bold text-lg hover:bg-slate-100 transition-colors">
            Upload Portfolio CSV
          </button>
          <p className="text-sm text-primary-light mt-4">
            Free tier: 10 analyses per day • Pro: Unlimited + portfolio uploads
          </p>
        </div>
      </main>
    </div>
  );
}

