/**
 * Ticker Mapping Service
 * 
 * Automatically maps user-friendly ticker symbols to Yahoo Finance format.
 * Primary use case: UK stocks (BAT → BAT.L for London Stock Exchange)
 * 
 * Features:
 * - Transparent mapping (BAT → BATS.L)
 * - Case-insensitive matching
 * - Supports aliases (BRITISHAMERICANTOBACCO → BATS.L)
 * - Extensible to other markets (EU, Canada, Australia)
 */

import tickerMappingData from './ticker-mapping.json';

// ============================================================================
// Types
// ============================================================================

interface TickerMapping {
  yahooTicker: string;
  market: 'uk' | 'us' | 'eu' | 'canada' | 'australia';
  displayName: string;
  isAlias?: boolean;
}

interface MappingResult {
  original: string;
  mapped: string;
  market: 'uk' | 'us' | 'unknown';
  wasTransformed: boolean;
  displayName?: string;
}

// ============================================================================
// Database Access
// ============================================================================

const ukTickers = tickerMappingData.markets.uk.tickers;
const aliases = tickerMappingData.aliases;

/**
 * Check if ticker already has a known suffix
 */
function hasSuffix(ticker: string): boolean {
  const suffixes = ['.L', '.LN', '.LSE', '.PA', '.DE', '.AS', '.TO', '.AX'];
  return suffixes.some(suffix => ticker.toUpperCase().endsWith(suffix));
}

/**
 * Get company display name from ticker
 */
function getDisplayName(ticker: string): string | undefined {
  const upperTicker = ticker.toUpperCase();
  
  // Check UK tickers
  if (ukTickers[upperTicker as keyof typeof ukTickers]) {
    // Map common tickers to display names
    const displayNames: Record<string, string> = {
      'BATS': 'British American Tobacco',
      'BAT': 'British American Tobacco',
      'BP': 'BP plc',
      'VOD': 'Vodafone',
      'BARC': 'Barclays',
      'LLOY': 'Lloyds Banking Group',
      'HSBA': 'HSBC',
      'SHEL': 'Shell',
      'AZN': 'AstraZeneca',
      'GSK': 'GSK',
      'GLEN': 'Glencore',
      'RIO': 'Rio Tinto',
      'ULVR': 'Unilever',
      'DGE': 'Diageo',
      'TSCO': 'Tesco',
      'SBRY': 'Sainsbury\'s',
      'RR': 'Rolls-Royce',
      'BRBY': 'Burberry',
    };
    
    return displayNames[upperTicker];
  }
  
  return undefined;
}

// ============================================================================
// Main Mapping Function
// ============================================================================

/**
 * Map user input to Yahoo Finance ticker format
 * 
 * @param userInput - Ticker symbol entered by user (e.g., "BAT", "aapl", "BATS.L")
 * @returns Mapping result with original, mapped ticker, and metadata
 * 
 * @example
 * mapTickerToYahooFormat("BAT")     // → { mapped: "BATS.L", market: "uk", wasTransformed: true }
 * mapTickerToYahooFormat("AAPL")    // → { mapped: "AAPL", market: "us", wasTransformed: false }
 * mapTickerToYahooFormat("BATS.L")  // → { mapped: "BATS.L", market: "uk", wasTransformed: false }
 */
export function mapTickerToYahooFormat(userInput: string): MappingResult {
  const normalized = userInput.trim().toUpperCase();
  
  // If already has suffix, return as-is
  if (hasSuffix(normalized)) {
    return {
      original: userInput,
      mapped: normalized,
      market: normalized.endsWith('.L') || normalized.endsWith('.LN') || normalized.endsWith('.LSE') ? 'uk' : 'unknown',
      wasTransformed: false,
      displayName: getDisplayName(normalized.split('.')[0]),
    };
  }
  
  // Check UK ticker database
  const ukMapped = ukTickers[normalized as keyof typeof ukTickers];
  if (ukMapped) {
    return {
      original: userInput,
      mapped: ukMapped,
      market: 'uk',
      wasTransformed: true,
      displayName: getDisplayName(normalized),
    };
  }
  
  // Check aliases (company names)
  const aliasMapped = aliases[normalized as keyof typeof aliases];
  if (aliasMapped) {
    return {
      original: userInput,
      mapped: aliasMapped,
      market: 'uk',
      wasTransformed: true,
      displayName: getDisplayName(normalized),
    };
  }
  
  // Not found in UK database, assume US ticker
  return {
    original: userInput,
    mapped: normalized,
    market: 'us',
    wasTransformed: false,
  };
}

/**
 * Check if a ticker is a known UK stock
 */
export function isUKTicker(ticker: string): boolean {
  const normalized = ticker.trim().toUpperCase();
  
  // Check if already has .L suffix
  if (normalized.endsWith('.L') || normalized.endsWith('.LN') || normalized.endsWith('.LSE')) {
    return true;
  }
  
  // Check UK database
  return normalized in ukTickers || normalized in aliases;
}

/**
 * Get all available UK tickers (for autocomplete or suggestions)
 */
export function getAvailableUKTickers(): string[] {
  return Object.keys(ukTickers);
}

/**
 * Search UK tickers by partial match
 */
export function searchUKTickers(query: string, limit: number = 10): string[] {
  const normalized = query.trim().toUpperCase();
  const tickers = Object.keys(ukTickers);
  
  // Exact matches first
  const exactMatches = tickers.filter(t => t === normalized);
  
  // Starts with matches
  const startsWithMatches = tickers
    .filter(t => t.startsWith(normalized) && t !== normalized)
    .slice(0, limit - exactMatches.length);
  
  // Contains matches
  const containsMatches = tickers
    .filter(t => t.includes(normalized) && !t.startsWith(normalized))
    .slice(0, limit - exactMatches.length - startsWithMatches.length);
  
  return [...exactMatches, ...startsWithMatches, ...containsMatches];
}

/**
 * Format ticker for display to user
 * Shows user-friendly format with UK indicator
 * 
 * @example
 * formatTickerForDisplay("BATS.L") // → "BAT 🇬🇧"
 * formatTickerForDisplay("AAPL")   // → "AAPL"
 */
export function formatTickerForDisplay(yahooTicker: string): string {
  const normalized = yahooTicker.trim().toUpperCase();
  
  if (normalized.endsWith('.L')) {
    const base = normalized.replace('.L', '');
    
    // Reverse lookup to find user-friendly version
    const userFriendly = Object.keys(ukTickers).find(
      key => ukTickers[key as keyof typeof ukTickers] === normalized
    );
    
    if (userFriendly && userFriendly !== base) {
      return `${userFriendly} 🇬🇧`;
    }
    
    return `${base} 🇬🇧`;
  }
  
  return normalized;
}

// ============================================================================
// Export Database for Reference
// ============================================================================

export const tickerDatabase = {
  uk: ukTickers,
  aliases,
};

