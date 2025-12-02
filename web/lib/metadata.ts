import type { Metadata } from 'next';
import type { AnalysisResponse } from './api/client';

// ============================================================================
// Metadata Generation Helpers
// ============================================================================

/**
 * Base URL for the application
 * Falls back to localhost in development
 */
const getBaseUrl = (): string => {
  if (process.env.NEXT_PUBLIC_APP_URL) {
    return process.env.NEXT_PUBLIC_APP_URL;
  }
  return process.env.NODE_ENV === 'production'
    ? 'https://pe-scanner.com'
    : 'http://localhost:3000';
};

/**
 * Truncate text to specified length with ellipsis
 */
const truncate = (text: string, maxLength: number): string => {
  if (text.length <= maxLength) return text;
  return text.slice(0, maxLength - 3) + '...';
};

/**
 * Generate metadata for stock analysis report pages
 * Creates dynamic Open Graph and Twitter Card tags
 */
export function generateReportMetadata(
  ticker: string,
  analysis?: AnalysisResponse
): Metadata {
  const baseUrl = getBaseUrl();
  const url = `${baseUrl}/report/${ticker}`;
  
  // Default metadata (used while loading or on error)
  const defaultTitle = `${ticker} Stock Analysis - PE Scanner`;
  const defaultDescription = `Real-time P/E compression analysis for ${ticker}. Get instant BUY/SELL/HOLD signals with shareable headlines.`;
  
  // If analysis data is available, use it for rich previews
  if (analysis) {
    const title = analysis.headline 
      ? `${ticker} Analysis: ${truncate(analysis.headline, 60)}`
      : defaultTitle;
    
    const description = analysis.anchor
      ? truncate(analysis.anchor, 150)
      : `${analysis.signal} signal with ${analysis.confidence} confidence. ${defaultDescription}`;
    
    // Dynamic OG image will be generated in Task 48
    const ogImage = `${baseUrl}/api/og-image/${ticker}`;
    
    return {
      title,
      description,
      openGraph: {
        title,
        description,
        type: 'website',
        url,
        siteName: 'PE Scanner',
        locale: 'en_GB',
        images: [
          {
            url: ogImage,
            width: 1200,
            height: 630,
            alt: `${ticker} P/E compression analysis`,
          },
        ],
      },
      twitter: {
        card: 'summary_large_image',
        site: '@PEScanner',
        creator: '@PEScanner',
        title,
        description,
        images: [ogImage],
      },
      alternates: {
        canonical: url,
      },
    };
  }
  
  // Fallback metadata (loading state or error)
  // Use home OG image as fallback for reports
  const fallbackImage = `${baseUrl}/api/og-home`;
  
  return {
    title: defaultTitle,
    description: defaultDescription,
    openGraph: {
      title: defaultTitle,
      description: defaultDescription,
      type: 'website',
      url,
      siteName: 'PE Scanner',
      locale: 'en_GB',
      images: [
        {
          url: fallbackImage,
          width: 1200,
          height: 630,
          alt: 'PE Scanner - Stock Valuation Made Simple',
        },
      ],
    },
    twitter: {
      card: 'summary_large_image',
      site: '@PEScanner',
      creator: '@PEScanner',
      title: defaultTitle,
      description: defaultDescription,
      images: [fallbackImage],
    },
    alternates: {
      canonical: url,
    },
  };
}

/**
 * Generate metadata for the landing page
 */
export function generateLandingMetadata(): Metadata {
  const baseUrl = getBaseUrl();
  const title = 'PE Scanner - Spot Earnings Collapses Before Your Portfolio Does';
  const description = 'Free P/E compression analysis reveals which stocks are priced for disaster. Get clear BUY/SELL/HOLD signals in 30 seconds. No credit card required.';
  
  // Use dynamic OG image generation
  const ogImage = `${baseUrl}/api/og-home`;
  
  return {
    title,
    description,
    keywords: [
      'P/E ratio analysis',
      'P/E compression',
      'stock valuation',
      'portfolio analysis',
      'investment tools',
      'ISA stocks',
      'SIPP analysis',
      'UK stock analysis',
      'earnings analysis',
      'overvalued stocks',
    ],
    authors: [{ name: 'PE Scanner' }],
    openGraph: {
      title,
      description,
      type: 'website',
      url: baseUrl,
      siteName: 'PE Scanner',
      locale: 'en_GB',
      images: [
        {
          url: ogImage,
          width: 1200,
          height: 630,
          alt: 'PE Scanner - Stock Valuation Made Simple',
        },
      ],
    },
    twitter: {
      card: 'summary_large_image',
      site: '@PEScanner',
      creator: '@PEScanner',
      title,
      description,
      images: [ogImage],
    },
    alternates: {
      canonical: baseUrl,
    },
  };
}

/**
 * Generate metadata for legal pages
 */
export function generateLegalMetadata(
  page: 'privacy' | 'terms' | 'disclaimer'
): Metadata {
  const baseUrl = getBaseUrl();
  
  const titles = {
    privacy: 'Privacy Policy - PE Scanner',
    terms: 'Terms of Service - PE Scanner',
    disclaimer: 'Investment Disclaimer - PE Scanner',
  };
  
  const descriptions = {
    privacy: 'Privacy policy and data protection information for PE Scanner users. UK GDPR compliant.',
    terms: 'Terms of service and usage conditions for PE Scanner. UK law applies.',
    disclaimer: 'Important investment disclaimer and risk warnings for PE Scanner users. Not financial advice.',
  };
  
  return {
    title: titles[page],
    description: descriptions[page],
    robots: {
      index: true,
      follow: true,
    },
    alternates: {
      canonical: `${baseUrl}/${page}`,
    },
  };
}

