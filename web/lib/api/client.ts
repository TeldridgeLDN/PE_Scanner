/**
 * PE Scanner API Client
 * 
 * Handles communication with the Flask backend API.
 * Provides type-safe methods for fetching stock analysis.
 */

// ============================================================================
// Types - Match Flask API v2.0 Schema
// ============================================================================

export interface AnalysisResponse {
  ticker: string;
  analysis_mode: 'VALUE' | 'GROWTH' | 'HYPER_GROWTH';
  metrics: {
    trailing_pe?: number;
    forward_pe?: number;
    compression_pct?: number;
    current_price?: number;
    peg_ratio?: number;
    earnings_growth?: number;
    price_to_sales?: number;
    rule_of_40?: number;
  };
  signal: 'BUY' | 'SELL' | 'HOLD';
  confidence: 'high' | 'medium' | 'low';
  anchor?: string;
  headline?: string;
  share_urls?: {
    twitter?: string;
    linkedin?: string;
    copy_text?: string;
  };
  fair_value?: {
    bear_case?: number;
    bull_case?: number;
    bear_pe?: number;
    bull_pe?: number;
  };
  data_quality?: {
    flags: string[];
    uk_corrected?: boolean;
  };
  timestamp: string;
}

export interface ErrorResponse {
  error: string;
  ticker?: string;
  timestamp?: string;
}

export interface RateLimitInfo {
  remaining: number;
  resetAt?: string;
  message: string;
}

export interface ApiError {
  status: number;
  message: string;
  rateLimitInfo?: RateLimitInfo;
}

// ============================================================================
// API Configuration
// ============================================================================

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:5000';

/**
 * Get full API URL for an endpoint
 */
function getApiUrl(path: string): string {
  return `${API_BASE_URL}${path}`;
}

// ============================================================================
// Fetch with Error Handling
// ============================================================================

/**
 * Fetch wrapper with enhanced error handling
 */
async function apiFetch<T>(
  path: string,
  options?: RequestInit
): Promise<{ data?: T; error?: ApiError }> {
  try {
    const url = getApiUrl(path);
    
    const response = await fetch(url, {
      headers: {
        'Accept': 'application/json',
        ...options?.headers,
      },
      ...options,
    });

    // Handle rate limiting
    if (response.status === 429) {
      const errorData: ErrorResponse = await response.json();
      const rateLimitRemaining = response.headers.get('X-RateLimit-Remaining');
      const rateLimitReset = response.headers.get('X-RateLimit-Reset');
      
      return {
        error: {
          status: 429,
          message: errorData.error || 'Rate limit exceeded',
          rateLimitInfo: {
            remaining: rateLimitRemaining ? parseInt(rateLimitRemaining) : 0,
            resetAt: rateLimitReset || undefined,
            message: errorData.error || 'Rate limit exceeded. Try again later.',
          },
        },
      };
    }

    // Handle not found
    if (response.status === 404) {
      const errorData: ErrorResponse = await response.json();
      return {
        error: {
          status: 404,
          message: errorData.error || 'Ticker not found',
        },
      };
    }

    // Handle data quality issues
    if (response.status === 422) {
      const errorData: ErrorResponse = await response.json();
      return {
        error: {
          status: 422,
          message: errorData.error || 'Data quality issue detected',
        },
      };
    }

    // Handle server errors
    if (response.status >= 500) {
      return {
        error: {
          status: response.status,
          message: 'Server error. Please try again later.',
        },
      };
    }

    // Handle other errors
    if (!response.ok) {
      const errorData: ErrorResponse = await response.json().catch(() => ({}));
      return {
        error: {
          status: response.status,
          message: errorData.error || `Request failed with status ${response.status}`,
        },
      };
    }

    // Success
    const data: T = await response.json();
    return { data };

  } catch (error) {
    console.error('API fetch error:', error);
    return {
      error: {
        status: 0,
        message: error instanceof Error ? error.message : 'Network error. Please check your connection.',
      },
    };
  }
}

// ============================================================================
// Public API Methods
// ============================================================================

/**
 * Fetch stock analysis for a ticker
 * 
 * @param ticker - Stock ticker symbol (e.g., "AAPL", "BATS.L")
 * @param options - Optional fetch configuration
 * @returns Analysis response or error
 * 
 * @example
 * const { data, error } = await fetchAnalysis("AAPL");
 * if (error) {
 *   console.error(error.message);
 * } else {
 *   console.log(data.signal); // "BUY" | "SELL" | "HOLD"
 * }
 */
export async function fetchAnalysis(
  ticker: string,
  options?: RequestInit
): Promise<{ data?: AnalysisResponse; error?: ApiError }> {
  return apiFetch<AnalysisResponse>(`/api/analyze/${ticker}`, {
    method: 'GET',
    // Cache for 1 hour on server, allow stale-while-revalidate
    next: { revalidate: 3600 },
    ...options,
  });
}

/**
 * Check API health
 */
export async function checkHealth(): Promise<{ healthy: boolean; message?: string }> {
  const { data, error } = await apiFetch<{ status: string; timestamp: string }>('/health');
  
  if (error) {
    return { healthy: false, message: error.message };
  }
  
  return { healthy: data?.status === 'healthy' };
}

/**
 * Get API info
 */
export async function getApiInfo(): Promise<{
  name?: string;
  version?: string;
  endpoints?: Record<string, string>;
}> {
  const { data } = await apiFetch<{
    name: string;
    version: string;
    endpoints: Record<string, string>;
  }>('/');
  
  return data || {};
}

// ============================================================================
// Helper Functions
// ============================================================================

/**
 * Format rate limit reset time as human-readable string
 */
export function formatRateLimitReset(resetAt?: string): string {
  if (!resetAt) return 'soon';
  
  try {
    const resetDate = new Date(resetAt);
    const now = new Date();
    const diffMs = resetDate.getTime() - now.getTime();
    
    if (diffMs < 0) return 'now';
    
    const diffMins = Math.ceil(diffMs / 1000 / 60);
    
    if (diffMins < 60) {
      return `in ${diffMins} minute${diffMins === 1 ? '' : 's'}`;
    }
    
    const diffHours = Math.ceil(diffMins / 60);
    return `in ${diffHours} hour${diffHours === 1 ? '' : 's'}`;
  } catch {
    return 'soon';
  }
}

/**
 * Check if error is a rate limit error
 */
export function isRateLimitError(error?: ApiError): error is ApiError & { rateLimitInfo: RateLimitInfo } {
  return error?.status === 429 && !!error.rateLimitInfo;
}

/**
 * Check if error is a not found error
 */
export function isNotFoundError(error?: ApiError): boolean {
  return error?.status === 404;
}

/**
 * Get user-friendly error message
 */
export function getErrorMessage(error: ApiError): string {
  if (isRateLimitError(error)) {
    const resetTime = formatRateLimitReset(error.rateLimitInfo?.resetAt);
    return `Rate limit exceeded. You can try again ${resetTime}.`;
  }
  
  if (isNotFoundError(error)) {
    return 'Ticker not found. Please check the spelling and try again.';
  }
  
  if (error.status === 422) {
    return error.message || 'Data quality issue detected for this ticker.';
  }
  
  if (error.status >= 500) {
    return 'Server error. Please try again in a few moments.';
  }
  
  if (error.status === 0) {
    return 'Network error. Please check your internet connection.';
  }
  
  return error.message || 'An unexpected error occurred.';
}

// ============================================================================
// Export Configuration (for debugging)
// ============================================================================

export const apiConfig = {
  baseUrl: API_BASE_URL,
  version: '2.0',
};

