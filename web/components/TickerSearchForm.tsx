'use client';

/**
 * Ticker Search Form Component
 * 
 * A prominent ticker input form designed for the landing page hero section.
 * Allows users to submit stock tickers for P/E compression analysis.
 * 
 * Features:
 * - Works without authentication (free tier gets 10/day with email, 3/day anonymous)
 * - Inline form design matching the hero aesthetic
 * - Redirects to results page on successful submission
 * - Auto-formats ticker input (uppercase, validates format)
 * - Supports UK tickers (.L suffix)
 */

import { useState, FormEvent } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { mapTickerToYahooFormat, isUKTicker } from '@/lib/ticker-mapper';
import { trackEvent } from '@/lib/analytics/plausible';

// ============================================================================
// Types
// ============================================================================

interface TickerSearchFormProps {
  className?: string;
}

interface FormErrors {
  ticker?: string;
  general?: string;
}

interface ApiResponse {
  success: boolean;
  ticker?: string;
  error?: string;
  resetAt?: string;
  suggestSignup?: boolean;
  isAnonymous?: boolean;
}

// ============================================================================
// Ticker Validation
// ============================================================================

function validateTicker(ticker: string): { valid: boolean; error?: string; normalized?: string } {
  if (!ticker || ticker.trim() === '') {
    return { valid: false, error: 'Please enter a stock ticker' };
  }
  
  // Normalize: uppercase, trim whitespace
  let normalized = ticker.trim().toUpperCase();
  
  // Allow alphanumeric only (dots handled by mapper)
  // User enters: BAT, AAPL (simple, no Yahoo Finance knowledge needed)
  // Mapper converts: BAT → BATS.L automatically
  const tickerRegex = /^[A-Z0-9]{1,10}$/;
  
  if (!tickerRegex.test(normalized)) {
    return { 
      valid: false, 
      error: 'Invalid ticker format (e.g., AAPL, BAT, VOD)' 
    };
  }
  
  // Common mistakes
  if (normalized.length < 1) {
    return { valid: false, error: 'Ticker too short' };
  }
  
  if (normalized.length > 10 && !normalized.includes('.')) {
    return { valid: false, error: 'Ticker too long (max 10 characters)' };
  }
  
  return { valid: true, normalized };
}

// ============================================================================
// Component
// ============================================================================

export default function TickerSearchForm({ className = '' }: TickerSearchFormProps) {
  const router = useRouter();
  
  // Form state
  const [ticker, setTicker] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [errors, setErrors] = useState<FormErrors>({});
  const [rateLimitInfo, setRateLimitInfo] = useState<{ message: string; resetAt?: string } | null>(null);
  
  // Get mapped ticker for display
  const mappingResult = ticker ? mapTickerToYahooFormat(ticker) : null;
  
  // Handle form submission
  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    setErrors({});
    setRateLimitInfo(null);
    
    // Validate ticker
    const validation = validateTicker(ticker);
    if (!validation.valid || !validation.normalized) {
      setErrors({ ticker: validation.error || 'Invalid ticker' });
      return;
    }
    
    // Map ticker to Yahoo Finance format
    const mapping = mapTickerToYahooFormat(validation.normalized);
    const yahooTicker = mapping.mapped;
    
    // Submit to API
    setIsLoading(true);
    
    try {
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:5000';
      const response = await fetch(`${apiUrl}/api/analyze/${yahooTicker}`, {
        method: 'GET',
        headers: {
          'Accept': 'application/json',
        },
      });
      
      const data: ApiResponse = await response.json();
      
      if (!response.ok) {
        // Handle rate limiting
        if (response.status === 429) {
          setRateLimitInfo({
            message: data.error || 'Rate limit exceeded',
            resetAt: data.resetAt,
          });
          return;
        }
        
        // Handle ticker not found
        if (response.status === 404) {
          const displayTicker = mapping.wasTransformed 
            ? `${validation.normalized} (${yahooTicker})`
            : validation.normalized;
          setErrors({ ticker: `Ticker "${displayTicker}" not found. Check spelling or try a different ticker.` });
          return;
        }
        
        // Handle data quality issues
        if (response.status === 422) {
          setErrors({ general: data.error || 'Data quality issue detected for this ticker' });
          return;
        }
        
        setErrors({ general: data.error || 'Failed to analyze ticker' });
        return;
      }
      
      // Success! Track search and redirect to results page using Yahoo ticker
      if (yahooTicker) {
        // Track ticker search (analysis tracking happens on results page)
        trackEvent('Ticker_Analyzed', { ticker: yahooTicker });
        router.push(`/report/${yahooTicker}`);
      }
      
    } catch (err) {
      console.error('Analysis request error:', err);
      setErrors({ general: 'Network error. Please check your connection and try again.' });
    } finally {
      setIsLoading(false);
    }
  };
  
  return (
    <div className={`w-full max-w-2xl mx-auto ${className}`}>
      <form onSubmit={handleSubmit} className="relative">
        {/* Input Group */}
        <div className="flex flex-col sm:flex-row gap-3 p-2 bg-white rounded-2xl shadow-lg border border-slate-200">
          {/* Ticker Input */}
          <div className="flex-1 relative">
            <input
              type="text"
              value={ticker}
              onChange={(e) => {
                // Auto-uppercase as user types
                setTicker(e.target.value.toUpperCase());
                if (errors.ticker) setErrors({});
                if (rateLimitInfo) setRateLimitInfo(null);
              }}
              placeholder="Enter stock ticker (e.g., AAPL, HOOD, BATS.L)"
              disabled={isLoading}
              className={`
                w-full px-4 py-3 rounded-xl text-slate-900 placeholder-slate-400
                bg-transparent border-none text-lg
                focus:outline-none focus:ring-2 focus:ring-primary/20
                disabled:bg-slate-100 disabled:cursor-not-allowed
                transition-all duration-200
              `}
              aria-label="Stock ticker symbol"
              maxLength={15}
            />
            
            {/* Ticker Format Hint - Shows mapped ticker */}
            {mappingResult && mappingResult.market === 'uk' && (
              <div className="absolute right-4 top-1/2 -translate-y-1/2 text-xs text-slate-500 bg-slate-50 px-2 py-1 rounded-md border border-slate-200">
                🇬🇧 {mappingResult.wasTransformed ? mappingResult.mapped : 'UK'}
              </div>
            )}
            {mappingResult && mappingResult.market === 'us' && ticker.length <= 5 && (
              <div className="absolute right-4 top-1/2 -translate-y-1/2 text-xs text-slate-400">
                US
              </div>
            )}
          </div>
          
          {/* Submit Button */}
          <button
            type="submit"
            disabled={isLoading || !ticker.trim()}
            className="px-8 py-3 rounded-xl font-semibold text-lg text-white transition-all duration-200 whitespace-nowrap hover:-translate-y-0.5 hover:shadow-lg active:translate-y-0 disabled:cursor-not-allowed"
            style={{
              backgroundColor: isLoading || !ticker.trim() ? '#cbd5e1' : '#0d9488',
            }}
          >
            {isLoading ? (
              <span className="flex items-center justify-center gap-2">
                <svg className="animate-spin h-5 w-5" viewBox="0 0 24 24">
                  <circle
                    className="opacity-25"
                    cx="12"
                    cy="12"
                    r="10"
                    stroke="currentColor"
                    strokeWidth="4"
                    fill="none"
                  />
                  <path
                    className="opacity-75"
                    fill="currentColor"
                    d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
                  />
                </svg>
                <span>Analyzing...</span>
              </span>
            ) : (
              'Analyze →'
            )}
          </button>
        </div>
        
        {/* Error Messages */}
        {errors.ticker && (
          <p className="mt-3 text-sm text-red-600 text-center sm:text-left">
            {errors.ticker}
          </p>
        )}
        
        {errors.general && (
          <div className="mt-3 p-3 bg-red-50 border border-red-200 rounded-lg">
            <p className="text-sm text-red-600 text-center">{errors.general}</p>
          </div>
        )}
        
        {/* Rate Limit Message - Conversion-Focused Design */}
        {rateLimitInfo && (
          <div className="mt-4 p-6 bg-gradient-to-br from-slate-50 to-slate-100 border-2 border-slate-200 rounded-2xl shadow-lg">
            {/* Headline */}
            <div className="text-center mb-4">
              <h4 className="font-heading text-lg font-bold text-slate-900 mb-1">
                Daily Limit Reached
              </h4>
              <p className="text-sm text-slate-600">
                {rateLimitInfo.message}
              </p>
            </div>

            {/* CTA Buttons - Visual Hierarchy */}
            <div className="space-y-3">
              {/* Primary CTA - Sign Up (Most Prominent) */}
              <Link 
                href="/sign-up" 
                className="block w-full px-6 py-3 bg-gradient-to-r from-primary via-accent to-buy text-white font-bold text-center rounded-xl hover:shadow-xl hover:scale-105 transition-all"
                onClick={() => trackEvent('rate_limit_signup_clicked', { source: 'ticker_search_form' })}
              >
                🎉 Sign Up Free - Get 10 Per Day
              </Link>

              {/* Secondary CTA - Go Pro (Clear Value) */}
              <a 
                href="#pricing"
                className="block w-full px-6 py-3 bg-white border-2 border-slate-200 text-slate-900 font-bold text-center rounded-xl hover:border-primary hover:shadow-md transition-all"
                onClick={() => trackEvent('rate_limit_pro_clicked', { source: 'ticker_search_form' })}
              >
                ⚡ Go Pro - Unlimited Analyses <span className="text-primary">£25/mo</span>
              </a>
            </div>

            {/* Social Proof Micro-Copy */}
            <p className="mt-4 text-xs text-center text-slate-500">
              Join 2,000+ investors using StockSignal
            </p>
          </div>
        )}
      </form>
      
      {/* Helper Text */}
      <div className="mt-4 flex flex-wrap items-center justify-center gap-x-6 gap-y-2 text-sm text-slate-500">
        <div className="flex items-center gap-2">
          <svg className="w-4 h-4 text-buy" fill="currentColor" viewBox="0 0 20 20">
            <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
          </svg>
          <span>Results in 30 seconds</span>
        </div>
        <div className="flex items-center gap-2">
          <svg className="w-4 h-4 text-buy" fill="currentColor" viewBox="0 0 20 20">
            <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
          </svg>
          <span>No signup required</span>
        </div>
        <div className="flex items-center gap-2">
          <svg className="w-4 h-4 text-buy" fill="currentColor" viewBox="0 0 20 20">
            <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
          </svg>
          <span>3/day free (10/day with signup)</span>
        </div>
      </div>
      
      {/* Popular Tickers - User-friendly names (no .L suffix) */}
      <div className="mt-4 text-center">
        <p className="text-xs text-slate-400 mb-2">Popular tickers:</p>
        <div className="flex flex-wrap items-center justify-center gap-2">
          {['AAPL', 'MSFT', 'GOOGL', 'TSLA', 'META', 'NVDA', 'BAT', 'BP'].map((popularTicker) => (
            <button
              key={popularTicker}
              type="button"
              onClick={() => {
                setTicker(popularTicker);
                setErrors({});
                setRateLimitInfo(null);
              }}
              disabled={isLoading}
              className="px-3 py-1 text-xs font-medium rounded-md bg-slate-100 text-slate-700 hover:bg-slate-200 hover:text-slate-900 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {popularTicker}
            </button>
          ))}
        </div>
      </div>
    </div>
  );
}

