'use client';

import { useState } from 'react';
import Link from 'next/link';
import { trackPricingViewed, trackUpgradeClicked } from '@/lib/analytics/plausible';

// ============================================================================
// Types
// ============================================================================

type BillingPeriod = 'monthly' | 'annual';

interface PricingTier {
  name: string;
  tagline: string;
  monthlyPrice: number;
  annualPrice: number;
  badge?: string;
  features: string[];
  cta: string;
  ctaHref: string;
  featured?: boolean;
  popular?: boolean;
}

// ============================================================================
// Pricing Data
// ============================================================================

const PRICING_TIERS: PricingTier[] = [
  {
    name: 'Free',
    tagline: 'Perfect for casual investors',
    monthlyPrice: 0,
    annualPrice: 0,
    features: [
      '10 tickers/day (with signup)',
      '3 tickers/day (anonymous)',
      'P/E compression analysis',
      'Shareable headlines',
      'Social sharing buttons',
      'Basic anchoring statements',
    ],
    cta: 'Get Started Free',
    ctaHref: '#search',
  },
  {
    name: 'Pro',
    tagline: 'Analyze your entire portfolio in one click',
    monthlyPrice: 25,
    annualPrice: 240, // Save £60/year (20% discount)
    badge: 'Most Popular',
    features: [
      'Unlimited ticker searches',
      'Portfolio CSV upload',
      'Email reports',
      'Export to Excel',
      'Historical tracking (50 analyses)',
      'Priority API access',
      'Advanced PEG & P/S analysis',
      'Email support',
    ],
    cta: 'Upgrade to Unlimited',
    ctaHref: '/sign-up?plan=pro',
    featured: true,
    popular: true,
  },
  {
    name: 'Premium',
    tagline: 'API access + white-label reports',
    monthlyPrice: 49,
    annualPrice: 470, // Save £118/year (20% discount)
    features: [
      'Everything in Pro',
      'Weekly opportunity digest',
      'Slack/Discord webhooks',
      'API access (1,000 calls/day)',
      'White-label reports',
      'Unlimited saved analyses',
      'Custom alerting rules',
      'Priority support (24h response)',
    ],
    cta: 'Request API Access',
    ctaHref: '/contact?plan=premium',
  },
];

// ============================================================================
// Helper Functions
// ============================================================================

function calculateAnnualSavings(monthlyPrice: number, annualPrice: number): number {
  return monthlyPrice * 12 - annualPrice;
}

// ============================================================================
// PricingSection Component
// ============================================================================

export default function PricingSection() {
  const [billingPeriod, setBillingPeriod] = useState<BillingPeriod>('monthly');

  // Track pricing page view on mount
  useState(() => {
    trackPricingViewed();
  });

  const handleUpgradeClick = (tier: string) => {
    const tierLower = tier.toLowerCase() as 'pro' | 'premium';
    if (tierLower === 'pro' || tierLower === 'premium') {
      trackUpgradeClicked(tierLower, 'pricing');
    }
  };

  return (
    <section id="pricing" className="py-20 bg-white">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Section Header */}
        <div className="text-center mb-12">
          <h2 className="text-4xl font-bold text-slate-900 mb-4">
            Simple, Transparent Pricing
          </h2>
          <p className="text-xl text-slate-600 max-w-2xl mx-auto">
            Start free, upgrade when you need more. No hidden fees, cancel anytime.
          </p>
        </div>

        {/* Billing Toggle */}
        <div className="flex justify-center items-center gap-4 mb-12">
          <span
            className={`text-lg font-medium transition-colors duration-200 ${
              billingPeriod === 'monthly' ? 'text-slate-900' : 'text-slate-500'
            }`}
          >
            Monthly
          </span>
          
          <button
            onClick={() => setBillingPeriod(billingPeriod === 'monthly' ? 'annual' : 'monthly')}
            className="relative inline-flex h-8 w-16 items-center rounded-full transition-colors duration-200 focus:outline-none focus:ring-2 focus:ring-primary focus:ring-offset-2"
            style={{
              backgroundColor: billingPeriod === 'annual' ? '#0d9488' : '#CBD5E1',
            }}
            aria-label="Toggle billing period"
            role="switch"
            aria-checked={billingPeriod === 'annual'}
          >
            <span
              className={`inline-block h-6 w-6 transform rounded-full bg-white transition-transform duration-200 ${
                billingPeriod === 'annual' ? 'translate-x-9' : 'translate-x-1'
              }`}
            />
          </button>
          
          <span
            className={`text-lg font-medium transition-colors duration-200 ${
              billingPeriod === 'annual' ? 'text-slate-900' : 'text-slate-500'
            }`}
          >
            Annual
          </span>
          
          {/* Reserve space for badge to prevent layout shift */}
          <span 
            className={`ml-2 px-3 py-1 bg-emerald-100 text-emerald-700 text-sm font-semibold rounded-full transition-all duration-200 ${
              billingPeriod === 'annual' 
                ? 'opacity-100 scale-100' 
                : 'opacity-0 scale-95 pointer-events-none'
            }`}
          >
            Save 20%
          </span>
        </div>

        {/* Pricing Cards */}
        <div className="grid md:grid-cols-3 gap-8 max-w-6xl mx-auto">
          {PRICING_TIERS.map((tier) => {
            const price = billingPeriod === 'monthly' ? tier.monthlyPrice : tier.annualPrice;
            const monthlySavings = billingPeriod === 'annual' 
              ? calculateAnnualSavings(tier.monthlyPrice, tier.annualPrice)
              : 0;

            return (
              <div
                key={tier.name}
                className={`relative flex flex-col rounded-2xl border transition-all duration-200 ${
                  tier.featured
                    ? 'bg-gradient-to-br from-[#0d9488] to-[#0369a1] text-white scale-105 shadow-2xl border-transparent'
                    : 'bg-white text-slate-900 shadow-lg border-slate-200 hover:shadow-xl hover:scale-[1.02]'
                }`}
              >
                {/* Popular Badge */}
                {tier.badge && (
                  <div className="absolute -top-4 left-1/2 -translate-x-1/2">
                    <span className="px-4 py-1 bg-gradient-to-r from-[#059669] to-[#10b981] text-white text-sm font-bold rounded-full shadow-lg">
                      {tier.badge}
                    </span>
                  </div>
                )}

                {/* Card Content */}
                <div className="flex-1 p-8">
                  {/* Tier Name */}
                  <h3
                    className={`text-2xl font-bold mb-2 ${
                      tier.featured ? 'text-white' : 'text-slate-900'
                    }`}
                  >
                    {tier.name}
                  </h3>

                  {/* Tagline */}
                  <p
                    className={`text-sm mb-6 ${
                      tier.featured ? 'text-primary-light' : 'text-slate-600'
                    }`}
                  >
                    {tier.tagline}
                  </p>

                  {/* Price */}
                  <div className="mb-6">
                    <div className="flex items-baseline">
                      <span className="text-4xl font-bold">
                        £{price}
                      </span>
                      {tier.monthlyPrice > 0 && (
                        <span
                          className={`ml-2 text-lg ${
                            tier.featured ? 'text-primary-light' : 'text-slate-600'
                          }`}
                        >
                          /{billingPeriod === 'monthly' ? 'month' : 'year'}
                        </span>
                      )}
                      {tier.monthlyPrice === 0 && (
                        <span
                          className={`ml-2 text-lg ${
                            tier.featured ? 'text-primary-light' : 'text-slate-600'
                          }`}
                        >
                          forever
                        </span>
                      )}
                    </div>

                    {/* Annual Savings Badge */}
                    {billingPeriod === 'annual' && monthlySavings > 0 && (
                      <p className="mt-2 text-sm font-medium">
                        Save £{monthlySavings} per year
                      </p>
                    )}

                    {/* Monthly equivalent for annual */}
                    {billingPeriod === 'annual' && tier.monthlyPrice > 0 && (
                      <p
                        className={`mt-1 text-sm ${
                          tier.featured ? 'text-primary-light' : 'text-slate-500'
                        }`}
                      >
                        £{(price / 12).toFixed(0)}/month billed annually
                      </p>
                    )}
                    
                    {/* Value comparison for Pro tier */}
                    {tier.name === 'Pro' && billingPeriod === 'monthly' && (
                      <p className="mt-2 text-xs text-primary-light font-medium">
                        £0.83/day • Less than your morning coffee
                      </p>
                    )}
                  </div>

                  {/* CTA Button */}
                  <Link
                    href={tier.ctaHref}
                    onClick={() => handleUpgradeClick(tier.name)}
                    className={`block w-full py-3 px-6 rounded-lg font-semibold text-center transition-all mb-8 ${
                      tier.featured
                        ? 'bg-white text-[#0d9488] hover:bg-slate-50 hover:text-[#0f766e]'
                        : 'bg-[#0d9488] text-white hover:bg-[#0f766e]'
                    }`}
                  >
                    {tier.cta}
                  </Link>

                  {/* Features List */}
                  <ul className="space-y-3">
                    {tier.features.map((feature, index) => (
                      <li key={index} className="flex items-start gap-3">
                        <svg
                          className={`w-5 h-5 mt-0.5 flex-shrink-0 ${
                            tier.featured ? 'text-white' : 'text-emerald-500'
                          }`}
                          fill="none"
                          stroke="currentColor"
                          viewBox="0 0 24 24"
                        >
                          <path
                            strokeLinecap="round"
                            strokeLinejoin="round"
                            strokeWidth={2}
                            d="M5 13l4 4L19 7"
                          />
                        </svg>
                        <span
                          className={`text-sm ${
                            tier.featured ? 'text-white' : 'text-slate-700'
                          }`}
                        >
                          {feature}
                        </span>
                      </li>
                    ))}
                  </ul>
                </div>
              </div>
            );
          })}
        </div>

        {/* Trust Indicators */}
        <div className="mt-12 text-center space-y-2">
          <p className="text-slate-600">
            ✓ Cancel anytime • No credit card required for free tier
          </p>
          <p className="text-slate-600">
            ✓ 30-day money-back guarantee • Email support included
          </p>
        </div>

        {/* FAQ Teaser (Optional) */}
        <div className="mt-16 text-center p-8 rounded-2xl bg-gradient-to-br from-primary/5 via-accent/5 to-buy/5 border border-primary/10">
          <p className="text-slate-700 mb-6 font-medium text-lg">
            Have questions about our plans?
          </p>
          <Link
            href="/faq"
            className="inline-flex items-center gap-2 px-8 py-4 bg-gradient-to-r from-primary to-accent hover:from-primary-dark hover:to-accent-dark text-white font-bold rounded-xl transition-all shadow-lg hover:shadow-xl hover:scale-105 text-lg"
          >
            View FAQ
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
            </svg>
          </Link>
        </div>
      </div>
    </section>
  );
}

