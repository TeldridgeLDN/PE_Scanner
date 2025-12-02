'use client';

import { useState } from 'react';
import SocialMediaCard from '@/components/SocialMediaCard';
import { generateRedditComment, generateDiscordEmbed } from '@/lib/generate-social-card';

/**
 * Social Media Card Demo Page
 * 
 * Showcases how StockSignal cards look in different contexts:
 * - Reddit/WSB comments
 * - Discord embeds
 * - Twitter/X replies
 * 
 * This is an internal demo page for testing card designs.
 */

export default function SocialCardsDemoPage() {
  const [selectedExample, setSelectedExample] = useState('aapl-sell');

  // Example scenarios
  const examples = {
    'aapl-sell': {
      ticker: 'AAPL',
      companyName: 'Apple Inc.',
      currentPrice: 182.45,
      signal: 'SELL' as const,
      analysisMode: 'VALUE (P/E Compression)',
      keyMetric: {
        label: 'P/E Compression',
        value: '-15.2%',
        change: '-15.2%'
      },
      reasoning: 'Market expects earnings decline. Forward P/E expanded 15.2%, suggesting overvaluation at current levels.',
      confidence: 'high' as const,
      anchor: 'At current price, AAPL is valued as if it will generate $120B in annual profit — more than Apple\'s $100B historical peak'
    },
    'nvda-buy': {
      ticker: 'NVDA',
      companyName: 'NVIDIA Corporation',
      currentPrice: 495.20,
      signal: 'STRONG_BUY' as const,
      analysisMode: 'GROWTH (PEG Ratio)',
      keyMetric: {
        label: 'PEG Ratio',
        value: '0.68',
      },
      reasoning: 'PEG ratio of 0.68 means you\'re paying $0.68 per 1% of growth. Attractive valuation for growth rate.',
      confidence: 'high' as const,
      anchor: 'NVDA is paying 0.68x for each % of growth — attractive valuation for 72% growth rate'
    },
    'pltr-hold': {
      ticker: 'PLTR',
      companyName: 'Palantir Technologies Inc.',
      currentPrice: 28.15,
      signal: 'HOLD' as const,
      analysisMode: 'HYPER_GROWTH (P/S + Rule of 40)',
      keyMetric: {
        label: 'Price/Sales',
        value: '18.5x',
      },
      reasoning: 'P/S 18.5 and Rule of 40 score 35 show mixed signals. Fairly valued at current levels.',
      confidence: 'medium' as const
    },
    'tsla-sell': {
      ticker: 'TSLA',
      companyName: 'Tesla, Inc.',
      currentPrice: 242.80,
      signal: 'STRONG_SELL' as const,
      analysisMode: 'VALUE (P/E Compression)',
      keyMetric: {
        label: 'P/E Compression',
        value: '-42.3%',
        change: '-42.3%'
      },
      reasoning: 'Market expects earnings decline. Forward P/E expanded 42.3%, suggesting significant overvaluation.',
      confidence: 'high' as const,
      anchor: 'Market expects profits to DROP 58%. To return to fair value, TSLA would need to grow profits 2.4x'
    }
  };

  const currentExample = examples[selectedExample as keyof typeof examples];
  const redditComment = generateRedditComment(currentExample);
  const discordEmbed = generateDiscordEmbed(currentExample);

  return (
    <div className="min-h-screen bg-slate-50 py-12">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Header */}
        <div className="text-center mb-12">
          <h1 className="font-heading text-4xl font-black text-slate-900 mb-4">
            Social Media Card Demo
          </h1>
          <p className="text-lg text-slate-600 max-w-2xl mx-auto">
            Shareable stock analysis cards optimized for Reddit, Discord, and Twitter contexts.
            Designed to be informative without being overly promotional.
          </p>
        </div>

        {/* Example Selector */}
        <div className="flex flex-wrap justify-center gap-3 mb-12">
          {Object.keys(examples).map((key) => {
            const example = examples[key as keyof typeof examples];
            return (
              <button
                key={key}
                onClick={() => setSelectedExample(key)}
                className={`
                  px-4 py-2 rounded-lg font-bold text-sm transition-all
                  ${selectedExample === key
                    ? 'bg-primary text-white shadow-md'
                    : 'bg-white text-slate-700 border border-slate-200 hover:border-primary/30'
                  }
                `}
              >
                ${example.ticker} - {example.signal.replace('_', ' ')}
              </button>
            );
          })}
        </div>

        <div className="grid lg:grid-cols-2 gap-8 mb-12">
          {/* Visual Card */}
          <div>
            <h2 className="font-heading text-2xl font-bold text-slate-900 mb-4">
              Visual Card (Screenshot for Sharing)
            </h2>
            <div className="flex justify-center">
              <SocialMediaCard {...currentExample} />
            </div>
            <div className="mt-4 p-4 bg-white rounded-lg border border-slate-200">
              <p className="text-sm text-slate-600">
                <strong>Use Case:</strong> Screenshot this card and share it in Reddit comments,
                Discord channels, or Twitter replies. Clean, informative design that doesn't look like spam.
              </p>
            </div>
          </div>

          {/* Reddit Text Format */}
          <div>
            <h2 className="font-heading text-2xl font-bold text-slate-900 mb-4">
              Reddit Comment Format
            </h2>
            <div className="bg-white rounded-lg border border-slate-200 p-6 font-mono text-sm">
              <pre className="whitespace-pre-wrap text-slate-700">
                {redditComment}
              </pre>
            </div>
            <div className="mt-4 p-4 bg-white rounded-lg border border-slate-200">
              <p className="text-sm text-slate-600">
                <strong>Use Case:</strong> Copy this markdown-formatted text directly into Reddit comments.
                Works great for r/wallstreetbets, r/stocks, and r/investing.
              </p>
            </div>
          </div>
        </div>

        {/* Discord Embed Preview */}
        <div className="mb-12">
          <h2 className="font-heading text-2xl font-bold text-slate-900 mb-4">
            Discord Embed Data
          </h2>
          <div className="bg-slate-900 rounded-lg p-6">
            <pre className="text-xs text-green-400 overflow-x-auto">
              {JSON.stringify(discordEmbed, null, 2)}
            </pre>
          </div>
          <div className="mt-4 p-4 bg-white rounded-lg border border-slate-200">
            <p className="text-sm text-slate-600">
              <strong>Use Case:</strong> This JSON structure can be used with Discord webhooks or bots
              to post rich embedded analysis directly into Discord channels.
            </p>
          </div>
        </div>

        {/* Compact Version */}
        <div className="mb-12">
          <h2 className="font-heading text-2xl font-bold text-slate-900 mb-4">
            Compact Version (For Smaller Spaces)
          </h2>
          <div className="flex justify-center">
            <SocialMediaCard {...currentExample} compact />
          </div>
          <div className="mt-4 p-4 bg-white rounded-lg border border-slate-200 max-w-md mx-auto">
            <p className="text-sm text-slate-600">
              <strong>Use Case:</strong> Compact version for mobile screenshots or tight spaces.
              Same information, smaller footprint.
            </p>
          </div>
        </div>

        {/* Design Principles */}
        <div className="bg-white rounded-xl border border-slate-200 p-8">
          <h2 className="font-heading text-2xl font-bold text-slate-900 mb-6">
            Design Principles
          </h2>
          <div className="grid md:grid-cols-2 gap-6">
            <div>
              <h3 className="font-bold text-slate-900 mb-2">✅ What We DO</h3>
              <ul className="space-y-2 text-sm text-slate-700">
                <li>• Show clear, factual analysis</li>
                <li>• Use professional, clean design</li>
                <li>• Include confidence indicators</li>
                <li>• Provide context with key metrics</li>
                <li>• Subtle branding at bottom</li>
                <li>• "Free • No signup" messaging</li>
              </ul>
            </div>
            <div>
              <h3 className="font-bold text-slate-900 mb-2">❌ What We DON'T DO</h3>
              <ul className="space-y-2 text-sm text-slate-700">
                <li>• No "click here" CTAs</li>
                <li>• No promotional language</li>
                <li>• No large logos or watermarks</li>
                <li>• No financial advice disclaimers</li>
                <li>• No urgency tactics ("Act now!")</li>
                <li>• No affiliate links or spam</li>
              </ul>
            </div>
          </div>
          <div className="mt-6 p-4 bg-slate-50 rounded-lg">
            <p className="text-sm text-slate-700">
              <strong>Philosophy:</strong> These cards are designed to be genuinely helpful contributions
              to investment discussions, not advertisements. The goal is to provide value first,
              brand awareness second. Users will naturally check out StockSignal if the analysis is good.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}

