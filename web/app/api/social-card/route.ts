import { NextRequest, NextResponse } from 'next/server';
import { generateSocialCardData, generateRedditComment, generateDiscordEmbed } from '@/lib/generate-social-card';

/**
 * Social Card API Endpoint
 * 
 * GET /api/social-card?ticker=AAPL&format=json
 * 
 * Query Parameters:
 * - ticker: Stock ticker symbol (required)
 * - format: Response format - 'json' | 'reddit' | 'discord' (default: 'json')
 * 
 * Returns social media card data optimized for sharing
 */

const BACKEND_API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export async function GET(request: NextRequest) {
  const searchParams = request.nextUrl.searchParams;
  const ticker = searchParams.get('ticker');
  const format = searchParams.get('format') || 'json';

  // Validate ticker
  if (!ticker) {
    return NextResponse.json(
      { error: 'Missing required parameter: ticker' },
      { status: 400 }
    );
  }

  try {
    // Fetch analysis from backend (with anchor for tangible context)
    const response = await fetch(
      `${BACKEND_API_URL}/api/analyze/${ticker}?include_headline=true&include_anchor=true`,
      {
        headers: {
          'Content-Type': 'application/json',
        },
      }
    );

    if (!response.ok) {
      const error = await response.json();
      return NextResponse.json(
        { error: error.message || 'Failed to fetch analysis' },
        { status: response.status }
      );
    }

    const analysisResult = await response.json();

    // Generate social card data
    const cardData = generateSocialCardData(analysisResult);

    // Return in requested format
    switch (format.toLowerCase()) {
      case 'reddit':
        return new NextResponse(generateRedditComment(cardData), {
          headers: { 'Content-Type': 'text/plain' },
        });

      case 'discord':
        return NextResponse.json(generateDiscordEmbed(cardData));

      case 'json':
      default:
        return NextResponse.json(cardData);
    }
  } catch (error) {
    console.error('Social card generation error:', error);
    return NextResponse.json(
      { error: 'Internal server error' },
      { status: 500 }
    );
  }
}

