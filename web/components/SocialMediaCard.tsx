'use client';

import React from 'react';

/**
 * Social Media Card Component
 * 
 * Designed for Reddit/WSB contexts where users share stock positions.
 * Balances informative analysis with subtle branding - not too promotional.
 * 
 * Optimized for:
 * - Reddit comments and posts
 * - Discord embeds
 * - Twitter/X replies
 * - Screenshot sharing
 */

interface SocialMediaCardProps {
  ticker: string;
  companyName?: string;
  currentPrice: number;
  signal: 'BUY' | 'SELL' | 'HOLD' | 'STRONG_BUY' | 'STRONG_SELL';
  analysisMode: string;
  keyMetric: {
    label: string;
    value: string;
    change?: string; // e.g., "+26.7%" or "-15.2%"
  };
  reasoning: string; // Short, punchy explanation (1-2 lines max)
  confidence: 'high' | 'medium' | 'low';
  compact?: boolean; // For smaller contexts
}

export default function SocialMediaCard({
  ticker,
  companyName,
  currentPrice,
  signal,
  analysisMode,
  keyMetric,
  reasoning,
  confidence,
  compact = false
}: SocialMediaCardProps) {
  // Signal styling
  const signalConfig = {
    'STRONG_BUY': {
      bg: 'bg-buy',
      text: 'text-white',
      emoji: '🚀',
      label: 'Strong Buy'
    },
    'BUY': {
      bg: 'bg-buy',
      text: 'text-white',
      emoji: '📈',
      label: 'Buy'
    },
    'HOLD': {
      bg: 'bg-amber-500',
      text: 'text-white',
      emoji: '⚖️',
      label: 'Hold'
    },
    'SELL': {
      bg: 'bg-sell',
      text: 'text-white',
      emoji: '📉',
      label: 'Sell'
    },
    'STRONG_SELL': {
      bg: 'bg-sell',
      text: 'text-white',
      emoji: '🔴',
      label: 'Strong Sell'
    }
  };

  const config = signalConfig[signal];
  const isPositive = signal.includes('BUY');
  const isNegative = signal.includes('SELL');

  return (
    <div 
      className={`
        bg-white rounded-xl border-2 shadow-lg overflow-hidden
        ${isPositive ? 'border-buy/30' : isNegative ? 'border-sell/30' : 'border-amber-500/30'}
        ${compact ? 'max-w-md' : 'max-w-lg'}
      `}
    >
      {/* Header - Ticker & Price */}
      <div className="p-4 bg-slate-50 border-b border-slate-200 flex items-center justify-between">
        <div>
          <div className="flex items-center gap-2">
            <span className="text-2xl font-black text-slate-900">${ticker}</span>
            <span className={`px-2 py-0.5 rounded-md text-xs font-bold ${config.bg} ${config.text}`}>
              {config.emoji} {config.label}
            </span>
          </div>
          {companyName && !compact && (
            <p className="text-sm text-slate-600 mt-0.5">{companyName}</p>
          )}
        </div>
        <div className="text-right">
          <p className="text-2xl font-bold text-slate-900">
            ${currentPrice.toFixed(2)}
          </p>
        </div>
      </div>

      {/* Key Metric - The "Why" */}
      <div className="p-4 bg-white">
        <div className="flex items-start justify-between gap-4">
          <div className="flex-1">
            <p className="text-xs font-medium text-slate-500 uppercase tracking-wide mb-1">
              {keyMetric.label}
            </p>
            <div className="flex items-baseline gap-2">
              <span className="text-3xl font-bold text-slate-900">
                {keyMetric.value}
              </span>
              {keyMetric.change && (
                <span className={`
                  text-lg font-semibold
                  ${keyMetric.change.startsWith('+') ? 'text-buy' : 'text-sell'}
                `}>
                  {keyMetric.change}
                </span>
              )}
            </div>
          </div>

          {/* Confidence Indicator */}
          <div className="text-right">
            <p className="text-xs font-medium text-slate-500 uppercase tracking-wide mb-1">
              Confidence
            </p>
            <div className="flex gap-1">
              {['high', 'medium', 'low'].map((level, idx) => {
                const active = confidence === 'high' 
                  ? idx < 3 
                  : confidence === 'medium' 
                  ? idx < 2 
                  : idx < 1;
                return (
                  <div
                    key={level}
                    className={`
                      w-2 h-8 rounded-sm
                      ${active 
                        ? isPositive ? 'bg-buy' : isNegative ? 'bg-sell' : 'bg-amber-500'
                        : 'bg-slate-200'
                      }
                    `}
                  />
                );
              })}
            </div>
          </div>
        </div>

        {/* Reasoning - Short & Punchy */}
        <p className="text-sm text-slate-700 mt-3 leading-relaxed">
          {reasoning}
        </p>

        {/* Analysis Mode Tag */}
        <div className="mt-3 pt-3 border-t border-slate-100">
          <span className="text-xs text-slate-500 font-medium">
            Analysis: {analysisMode}
          </span>
        </div>
      </div>

      {/* Footer - Subtle Branding */}
      <div className="px-4 py-2 bg-slate-50 border-t border-slate-100 flex items-center justify-between">
        <span className="text-xs text-slate-500 font-medium">
          StockSignal Analysis
        </span>
        <span className="text-xs text-slate-400">
          Free • No signup required
        </span>
      </div>
    </div>
  );
}

/**
 * Example Usage:
 * 
 * <SocialMediaCard
 *   ticker="AAPL"
 *   companyName="Apple Inc."
 *   currentPrice={182.45}
 *   signal="SELL"
 *   analysisMode="VALUE (P/E Compression)"
 *   keyMetric={{
 *     label: "P/E Compression",
 *     value: "-15.2%",
 *     change: "-15.2%"
 *   }}
 *   reasoning="Market expects earnings to decline. Forward P/E expanded significantly, suggesting overvaluation at current levels."
 *   confidence="high"
 * />
 */

