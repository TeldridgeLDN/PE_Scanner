'use client';

import { useState } from 'react';

// ============================================================================
// Types
// ============================================================================

interface ShareButtonsProps {
  ticker: string;
  headline: string;
  shareUrls?: {
    twitter?: string;
    linkedin?: string;
    copy_text?: string;
  };
}

interface ToastProps {
  message: string;
  onClose: () => void;
}

// ============================================================================
// Toast Notification Component
// ============================================================================

function Toast({ message, onClose }: ToastProps) {
  return (
    <div 
      className="fixed bottom-4 left-1/2 -translate-x-1/2 sm:left-auto sm:right-4 sm:translate-x-0 
                 bg-emerald-600 text-white px-6 py-3 rounded-lg shadow-lg 
                 flex items-center gap-3 animate-slide-up z-50"
      role="alert"
      aria-live="polite"
    >
      <svg 
        className="w-5 h-5 flex-shrink-0" 
        fill="none" 
        stroke="currentColor" 
        viewBox="0 0 24 24"
        aria-hidden="true"
      >
        <path 
          strokeLinecap="round" 
          strokeLinejoin="round" 
          strokeWidth={2} 
          d="M5 13l4 4L19 7" 
        />
      </svg>
      <span className="font-medium">{message}</span>
      <button
        onClick={onClose}
        className="ml-2 hover:opacity-75 transition-opacity"
        aria-label="Close notification"
      >
        <svg 
          className="w-4 h-4" 
          fill="none" 
          stroke="currentColor" 
          viewBox="0 0 24 24"
        >
          <path 
            strokeLinecap="round" 
            strokeLinejoin="round" 
            strokeWidth={2} 
            d="M6 18L18 6M6 6l12 12" 
          />
        </svg>
      </button>
    </div>
  );
}

// ============================================================================
// Share Buttons Component
// ============================================================================

export default function ShareButtons({ ticker, headline, shareUrls }: ShareButtonsProps) {
  const [showToast, setShowToast] = useState(false);
  const [isCopying, setIsCopying] = useState(false);

  // ============================================================================
  // Analytics Tracking
  // ============================================================================

  const trackShare = (platform: 'twitter' | 'linkedin' | 'copy') => {
    // Track event with Plausible (will be implemented in Task 34)
    if (typeof window !== 'undefined' && (window as any).plausible) {
      (window as any).plausible('Headline_Shared', {
        props: {
          ticker,
          platform,
        },
      });
    }
  };

  // ============================================================================
  // Share Handlers
  // ============================================================================

  const handleTwitterShare = () => {
    if (!shareUrls?.twitter) return;
    
    trackShare('twitter');
    window.open(shareUrls.twitter, '_blank', 'noopener,noreferrer,width=550,height=420');
  };

  const handleLinkedInShare = () => {
    if (!shareUrls?.linkedin) return;
    
    trackShare('linkedin');
    window.open(shareUrls.linkedin, '_blank', 'noopener,noreferrer,width=550,height=570');
  };

  const handleCopyToClipboard = async () => {
    if (!shareUrls?.copy_text || isCopying) return;
    
    setIsCopying(true);

    try {
      // Modern clipboard API
      if (navigator.clipboard && window.isSecureContext) {
        await navigator.clipboard.writeText(shareUrls.copy_text);
        trackShare('copy');
        setShowToast(true);
        
        // Auto-dismiss after 2 seconds
        setTimeout(() => setShowToast(false), 2000);
      } else {
        // Fallback for older browsers or non-HTTPS
        const textarea = document.createElement('textarea');
        textarea.value = shareUrls.copy_text;
        textarea.style.position = 'fixed';
        textarea.style.left = '-9999px';
        textarea.style.top = '-9999px';
        document.body.appendChild(textarea);
        textarea.focus();
        textarea.select();
        
        try {
          const successful = document.execCommand('copy');
          if (successful) {
            trackShare('copy');
            setShowToast(true);
            setTimeout(() => setShowToast(false), 2000);
          }
        } catch (err) {
          console.error('Fallback copy failed:', err);
        }
        
        document.body.removeChild(textarea);
      }
    } catch (err) {
      console.error('Failed to copy to clipboard:', err);
    } finally {
      setIsCopying(false);
    }
  };

  // Native share API (mobile)
  const handleNativeShare = async () => {
    if (!navigator.share || !shareUrls?.copy_text) return;

    try {
      await navigator.share({
        title: `${ticker} Analysis - StockSignal`,
        text: headline,
        url: window.location.href,
      });
      trackShare('copy'); // Use 'copy' as platform for native share
    } catch (err) {
      // User cancelled or error occurred
      if ((err as Error).name !== 'AbortError') {
        console.error('Native share failed:', err);
      }
    }
  };

  // Show native share button on mobile if available
  const supportsNativeShare = typeof navigator !== 'undefined' && navigator.share;

  // ============================================================================
  // Render
  // ============================================================================

  // Don't render if no share URLs provided
  if (!shareUrls) return null;

  return (
    <>
      <div className="space-y-4">
        {/* Section Title */}
        <h2 className="text-lg font-bold text-slate-900">
          Share Analysis
        </h2>

        {/* Share Buttons Grid */}
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
          {/* Twitter Button */}
          {shareUrls.twitter && (
            <button
              onClick={handleTwitterShare}
              className="flex items-center justify-center gap-2 px-6 py-3
                       bg-gradient-to-r from-blue-500 to-blue-600 
                       hover:from-blue-600 hover:to-blue-700
                       text-white font-semibold rounded-lg
                       transition-all duration-200 transform hover:scale-105
                       focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2
                       min-h-[44px]"
              aria-label={`Share ${ticker} analysis on Twitter`}
            >
              <svg 
                className="w-5 h-5" 
                fill="currentColor" 
                viewBox="0 0 24 24"
                aria-hidden="true"
              >
                <path d="M18.244 2.25h3.308l-7.227 8.26 8.502 11.24H16.17l-5.214-6.817L4.99 21.75H1.68l7.73-8.835L1.254 2.25H8.08l4.713 6.231zm-1.161 17.52h1.833L7.084 4.126H5.117z" />
              </svg>
              <span>Twitter</span>
            </button>
          )}

          {/* LinkedIn Button */}
          {shareUrls.linkedin && (
            <button
              onClick={handleLinkedInShare}
              className="flex items-center justify-center gap-2 px-6 py-3
                       bg-[#0A66C2] hover:bg-[#084e96]
                       text-white font-semibold rounded-lg
                       transition-all duration-200 transform hover:scale-105
                       focus:outline-none focus:ring-2 focus:ring-[#0A66C2] focus:ring-offset-2
                       min-h-[44px]"
              aria-label={`Share ${ticker} analysis on LinkedIn`}
            >
              <svg 
                className="w-5 h-5" 
                fill="currentColor" 
                viewBox="0 0 24 24"
                aria-hidden="true"
              >
                <path d="M20.447 20.452h-3.554v-5.569c0-1.328-.027-3.037-1.852-3.037-1.853 0-2.136 1.445-2.136 2.939v5.667H9.351V9h3.414v1.561h.046c.477-.9 1.637-1.85 3.37-1.85 3.601 0 4.267 2.37 4.267 5.455v6.286zM5.337 7.433c-1.144 0-2.063-.926-2.063-2.065 0-1.138.92-2.063 2.063-2.063 1.14 0 2.064.925 2.064 2.063 0 1.139-.925 2.065-2.064 2.065zm1.782 13.019H3.555V9h3.564v11.452zM22.225 0H1.771C.792 0 0 .774 0 1.729v20.542C0 23.227.792 24 1.771 24h20.451C23.2 24 24 23.227 24 22.271V1.729C24 .774 23.2 0 22.222 0h.003z" />
              </svg>
              <span>LinkedIn</span>
            </button>
          )}

          {/* Copy Button (Desktop) or Native Share (Mobile) */}
          {shareUrls.copy_text && (
            supportsNativeShare ? (
              <button
                onClick={handleNativeShare}
                className="flex items-center justify-center gap-2 px-6 py-3
                         bg-slate-100 hover:bg-slate-200
                         text-slate-700 font-semibold rounded-lg
                         transition-all duration-200 transform hover:scale-105
                         focus:outline-none focus:ring-2 focus:ring-slate-400 focus:ring-offset-2
                         min-h-[44px]"
                aria-label={`Share ${ticker} analysis`}
              >
                <svg 
                  className="w-5 h-5" 
                  fill="none" 
                  stroke="currentColor" 
                  viewBox="0 0 24 24"
                  aria-hidden="true"
                >
                  <path 
                    strokeLinecap="round" 
                    strokeLinejoin="round" 
                    strokeWidth={2} 
                    d="M8.684 13.342C8.886 12.938 9 12.482 9 12c0-.482-.114-.938-.316-1.342m0 2.684a3 3 0 110-2.684m0 2.684l6.632 3.316m-6.632-6l6.632-3.316m0 0a3 3 0 105.367-2.684 3 3 0 00-5.367 2.684zm0 9.316a3 3 0 105.368 2.684 3 3 0 00-5.368-2.684z" 
                  />
                </svg>
                <span>Share</span>
              </button>
            ) : (
              <button
                onClick={handleCopyToClipboard}
                disabled={isCopying}
                className="flex items-center justify-center gap-2 px-6 py-3
                         bg-slate-100 hover:bg-slate-200
                         text-slate-700 font-semibold rounded-lg
                         transition-all duration-200 transform hover:scale-105
                         focus:outline-none focus:ring-2 focus:ring-slate-400 focus:ring-offset-2
                         disabled:opacity-50 disabled:cursor-not-allowed disabled:transform-none
                         min-h-[44px]"
                aria-label={`Copy ${ticker} analysis to clipboard`}
              >
                <svg 
                  className="w-5 h-5" 
                  fill="none" 
                  stroke="currentColor" 
                  viewBox="0 0 24 24"
                  aria-hidden="true"
                >
                  <path 
                    strokeLinecap="round" 
                    strokeLinejoin="round" 
                    strokeWidth={2} 
                    d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z" 
                  />
                </svg>
                <span>{isCopying ? 'Copying...' : 'Copy Link'}</span>
              </button>
            )
          )}
        </div>

        {/* Helper Text */}
        <p className="text-sm text-slate-600 text-center sm:text-left">
          Share this analysis with your network
        </p>
      </div>

      {/* Toast Notification */}
      {showToast && (
        <Toast 
          message="Copied to clipboard!" 
          onClose={() => setShowToast(false)} 
        />
      )}
    </>
  );
}


