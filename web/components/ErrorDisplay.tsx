/**
 * ErrorDisplay Component
 * 
 * User-friendly error display for API failures, rate limits, and not found errors.
 */

'use client';

import Link from 'next/link';
import { ApiError, isRateLimitError, isNotFoundError, getErrorMessage, formatRateLimitReset } from '@/lib/api/client';

interface ErrorDisplayProps {
  error: ApiError;
  ticker?: string;
}

export function ErrorDisplay({ error, ticker }: ErrorDisplayProps) {
  const isRateLimit = isRateLimitError(error);
  const isNotFound = isNotFoundError(error);
  
  // Icon based on error type
  const getIcon = () => {
    if (isRateLimit) {
      return '⏱️';
    }
    if (isNotFound) {
      return '🔍';
    }
    if (error.status >= 500) {
      return '🔧';
    }
    if (error.status === 0) {
      return '🌐';
    }
    return '⚠️';
  };

  // Title based on error type
  const getTitle = () => {
    if (isRateLimit) {
      return 'Rate Limit Reached';
    }
    if (isNotFound) {
      return 'Ticker Not Found';
    }
    if (error.status >= 500) {
      return 'Server Error';
    }
    if (error.status === 0) {
      return 'Connection Error';
    }
    return 'Something Went Wrong';
  };

  // Suggested actions based on error type
  const getSuggestedActions = () => {
    if (isRateLimit) {
      const resetTime = error.rateLimitInfo?.resetAt 
        ? formatRateLimitReset(error.rateLimitInfo.resetAt)
        : 'soon';
      
      return (
        <div className="space-y-2">
          <p className="text-slate-700">
            You've reached the free tier limit of <strong>10 analyses per day</strong>.
          </p>
          <p className="text-slate-600">
            Your limit resets {resetTime}. You can:
          </p>
          <ul className="list-disc list-inside space-y-1 text-slate-600">
            <li>Wait for the reset</li>
            <li>Sign up for <strong>Pro</strong> (£25/mo) for unlimited analyses</li>
            <li>Upgrade to <strong>Premium</strong> (£49/mo) for API access</li>
          </ul>
        </div>
      );
    }

    if (isNotFound) {
      return (
        <div className="space-y-2">
          <p className="text-slate-700">
            We couldn't find data for <strong>{ticker || 'this ticker'}</strong>.
          </p>
          <p className="text-slate-600">
            Try:
          </p>
          <ul className="list-disc list-inside space-y-1 text-slate-600">
            <li>Double-checking the ticker symbol</li>
            <li>Adding market suffix (e.g., ".L" for UK stocks)</li>
            <li>Searching for a different company</li>
          </ul>
        </div>
      );
    }

    if (error.status >= 500) {
      return (
        <div className="space-y-2">
          <p className="text-slate-700">
            Our servers are experiencing issues. This is temporary.
          </p>
          <p className="text-slate-600">
            Please try again in a few moments. If the problem persists, contact support.
          </p>
        </div>
      );
    }

    if (error.status === 0) {
      return (
        <div className="space-y-2">
          <p className="text-slate-700">
            We couldn't connect to our servers.
          </p>
          <p className="text-slate-600">
            Check your internet connection and try again.
          </p>
        </div>
      );
    }

    return (
      <div className="space-y-2">
        <p className="text-slate-700">
          {getErrorMessage(error)}
        </p>
        <p className="text-slate-600">
          Please try again or contact support if the issue persists.
        </p>
      </div>
    );
  };

  return (
    <div className="min-h-screen bg-slate-50 flex items-center justify-center px-4">
      <div className="max-w-2xl w-full">
        {/* Navigation Link */}
        <div className="mb-6">
          <Link 
            href="/"
            className="inline-flex items-center gap-2 text-primary hover:text-primary-dark font-medium transition-colors"
          >
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 19l-7-7m0 0l7-7m-7 7h18" />
            </svg>
            Back to Search
          </Link>
        </div>

        {/* Error Card */}
        <div className="bg-white rounded-2xl shadow-lg border border-slate-200 p-8 animate-fade-in">
          {/* Icon and Title */}
          <div className="flex items-start gap-4 mb-6">
            <div className="text-5xl">{getIcon()}</div>
            <div>
              <h1 className="text-2xl font-bold text-slate-900 mb-2">
                {getTitle()}
              </h1>
              <div className="text-slate-500">
                Error Code: {error.status === 0 ? 'Network' : error.status}
              </div>
            </div>
          </div>

          {/* Error Details */}
          <div className="mb-6">
            {getSuggestedActions()}
          </div>

          {/* Actions */}
          <div className="flex flex-wrap gap-3 pt-6 border-t border-slate-200">
            <Link 
              href="/"
              className="px-6 py-3 bg-primary text-white rounded-xl font-semibold hover:bg-primary-dark transition-colors"
            >
              Try Another Ticker
            </Link>
            
            {isRateLimit && (
              <Link
                href="/#pricing"
                className="px-6 py-3 bg-gradient-to-r from-secondary to-orange-600 text-white rounded-xl font-semibold hover:opacity-90 transition-opacity"
              >
                Upgrade to Pro
              </Link>
            )}

            <button
              onClick={() => window.location.reload()}
              className="px-6 py-3 bg-slate-100 text-slate-700 rounded-xl font-semibold hover:bg-slate-200 transition-colors"
            >
              Refresh Page
            </button>
          </div>

          {/* Rate Limit Info Box */}
          {isRateLimit && error.rateLimitInfo && (
            <div className="mt-6 p-4 bg-amber-50 rounded-lg border border-amber-200">
              <div className="flex items-start gap-3">
                <div className="text-2xl">ℹ️</div>
                <div>
                  <div className="font-semibold text-amber-900 mb-1">
                    Free Tier Limits
                  </div>
                  <div className="text-sm text-amber-700 space-y-1">
                    <div>Remaining today: <strong>{error.rateLimitInfo.remaining}</strong></div>
                    {error.rateLimitInfo.resetAt && (
                      <div>
                        Resets: <strong>{formatRateLimitReset(error.rateLimitInfo.resetAt)}</strong>
                      </div>
                    )}
                  </div>
                </div>
              </div>
            </div>
          )}
        </div>

        {/* Help Text */}
        <div className="mt-6 text-center text-sm text-slate-500">
          Need help? Email us at{' '}
          <a href="mailto:support@pe-scanner.com" className="text-primary hover:underline">
            support@pe-scanner.com
          </a>
        </div>
      </div>
    </div>
  );
}

