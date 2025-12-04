import type { Metadata } from 'next';
import type { AnalysisResponse } from './api/client';

// ============================================================================
// Metadata Generation Helpers for StockSignal SEO
// Following best practices from Orchestrator SEO Rule:
// - Title: 50-60 characters optimal
// - Description: 120-158 characters optimal
// - Open Graph: og:title, og:description, og:image, og:url
// - Twitter Cards: twitter:card, twitter:title, twitter:description, twitter:image
// - Canonical URLs: Always HTTPS, full URLs
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
    ? 'https://stocksignal.app'
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
  const defaultTitle = `${ticker} Stock Analysis - StockSignal`;
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
        siteName: 'StockSignal',
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
        site: '@StockSignalApp',
        creator: '@StockSignalApp',
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
      siteName: 'StockSignal',
      locale: 'en_GB',
      images: [
        {
          url: fallbackImage,
          width: 1200,
          height: 630,
          alt: 'StockSignal - Stock Valuation Made Simple',
        },
      ],
    },
    twitter: {
      card: 'summary_large_image',
      site: '@StockSignalApp',
      creator: '@StockSignalApp',
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
  const title = 'StockSignal - Spot Earnings Collapses Before Your Portfolio Does';
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
    authors: [{ name: 'StockSignal' }],
    openGraph: {
      title,
      description,
      type: 'website',
      url: baseUrl,
      siteName: 'StockSignal',
      locale: 'en_GB',
      images: [
        {
          url: ogImage,
          width: 1200,
          height: 630,
          alt: 'StockSignal - Stock Valuation Made Simple',
        },
      ],
    },
    twitter: {
      card: 'summary_large_image',
      site: '@StockSignalApp',
      creator: '@StockSignalApp',
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
 * Descriptions optimized to 120-158 characters per SEO best practices
 */
export function generateLegalMetadata(
  page: 'privacy' | 'terms' | 'disclaimer'
): Metadata {
  const baseUrl = getBaseUrl();
  
  const titles = {
    privacy: 'Privacy Policy - StockSignal',
    terms: 'Terms of Service - StockSignal',
    disclaimer: 'Investment Disclaimer - StockSignal',
  };
  
  // Optimized descriptions: 120-158 characters for better SEO
  const descriptions = {
    privacy: 'How StockSignal protects your data. UK GDPR compliant privacy policy covering data collection, retention, and your rights. No cookies required.',
    terms: 'Terms of service for StockSignal stock analysis tool. Usage conditions, subscription terms, and UK law compliance. Read before using our service.',
    disclaimer: 'Important investment disclaimer for StockSignal. Our analysis is educational, not financial advice. Understand the risks before investing.',
  };
  
  const title = titles[page];
  const description = descriptions[page];
  const url = `${baseUrl}/${page}`;
  const ogImage = `${baseUrl}/api/og-home`;
  
  return {
    title,
    description,
    robots: {
      index: true,
      follow: true,
    },
    openGraph: {
      title,
      description,
      type: 'website',
      url,
      siteName: 'StockSignal',
      locale: 'en_GB',
      images: [
        {
          url: ogImage,
          width: 1200,
          height: 630,
          alt: `${title} | StockSignal`,
        },
      ],
    },
    twitter: {
      card: 'summary',
      site: '@StockSignalApp',
      title,
      description,
    },
    alternates: {
      canonical: url,
    },
  };
}

/**
 * Generate metadata for the dashboard page
 */
export function generateDashboardMetadata(): Metadata {
  const baseUrl = getBaseUrl();
  const title = 'Dashboard - StockSignal';
  const description = 'Your StockSignal dashboard. View analysis history, manage your portfolio, and track your subscription. Analyse stocks with P/E compression.';
  const url = `${baseUrl}/dashboard`;
  
  return {
    title,
    description,
    robots: {
      index: false, // Dashboard is private, don't index
      follow: false,
    },
    alternates: {
      canonical: url,
    },
  };
}

/**
 * Generate metadata for authentication pages
 */
export function generateAuthMetadata(
  page: 'sign-in' | 'sign-up'
): Metadata {
  const baseUrl = getBaseUrl();
  
  const titles = {
    'sign-in': 'Sign In - StockSignal',
    'sign-up': 'Create Account - StockSignal',
  };
  
  const descriptions = {
    'sign-in': 'Sign in to your StockSignal account. Access your dashboard, analysis history, and Pro features. Free P/E compression analysis for investors.',
    'sign-up': 'Create your free StockSignal account. Get 10 stock analyses per day, shareable reports, and portfolio insights. No credit card required.',
  };
  
  const title = titles[page];
  const description = descriptions[page];
  const url = `${baseUrl}/${page}`;
  const ogImage = `${baseUrl}/api/og-home`;
  
  return {
    title,
    description,
    openGraph: {
      title,
      description,
      type: 'website',
      url,
      siteName: 'StockSignal',
      locale: 'en_GB',
      images: [
        {
          url: ogImage,
          width: 1200,
          height: 630,
          alt: `${title} | StockSignal`,
        },
      ],
    },
    twitter: {
      card: 'summary',
      site: '@StockSignalApp',
      title,
      description,
    },
    alternates: {
      canonical: url,
    },
  };
}

