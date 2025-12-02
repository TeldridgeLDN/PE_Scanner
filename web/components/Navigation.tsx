'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';
import { trackEvent } from '@/lib/analytics/plausible';

// ============================================================================
// Types
// ============================================================================

interface NavigationProps {
  /** Whether user is authenticated (for future auth integration) */
  isAuthenticated?: boolean;
  /** User's plan tier (for future auth integration) */
  userPlan?: 'free' | 'pro' | 'premium';
}

// ============================================================================
// Navigation Links
// ============================================================================

const NAV_LINKS = [
  { label: 'Features', href: '#features' },
  { label: 'Pricing', href: '#pricing' },
  { label: 'How It Works', href: '#how-it-works' },
] as const;

// ============================================================================
// Navigation Component
// ============================================================================

export default function Navigation({ isAuthenticated = false, userPlan }: NavigationProps = {}) {
  const [isScrolled, setIsScrolled] = useState(false);
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);

  // ============================================================================
  // Scroll Detection
  // ============================================================================

  useEffect(() => {
    const handleScroll = () => {
      setIsScrolled(window.scrollY > 50);
    };

    window.addEventListener('scroll', handleScroll, { passive: true });
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  // ============================================================================
  // Body Scroll Lock (Mobile Menu)
  // ============================================================================

  useEffect(() => {
    if (isMobileMenuOpen) {
      document.body.style.overflow = 'hidden';
    } else {
      document.body.style.overflow = '';
    }

    return () => {
      document.body.style.overflow = '';
    };
  }, [isMobileMenuOpen]);

  // ============================================================================
  // Handlers
  // ============================================================================

  const handleNavLinkClick = (label: string, href: string) => {
    trackEvent('Pricing_Viewed'); // Track when clicking to pricing
    
    // Close mobile menu
    setIsMobileMenuOpen(false);

    // Smooth scroll to anchor
    if (href.startsWith('#')) {
      const element = document.querySelector(href);
      if (element) {
        element.scrollIntoView({ behavior: 'smooth' });
      }
    }
  };

  const handleGetStartedClick = () => {
    trackEvent('Pricing_Viewed'); // Track interest in getting started
    setIsMobileMenuOpen(false);
    
    // Focus on search form
    const searchInput = document.querySelector('input[type="text"]') as HTMLInputElement;
    if (searchInput) {
      searchInput.focus();
      searchInput.scrollIntoView({ behavior: 'smooth', block: 'center' });
    }
  };

  // ============================================================================
  // Render
  // ============================================================================

  return (
    <>
      {/* Skip to Content Link (Accessibility) */}
      <a
        href="#main-content"
        className="sr-only focus:not-sr-only focus:absolute focus:top-4 focus:left-4 focus:z-50 focus:px-4 focus:py-2 focus:bg-primary focus:text-white focus:rounded-lg"
      >
        Skip to content
      </a>

      {/* Navigation Bar */}
      <nav
        className={`fixed top-0 left-0 right-0 z-50 transition-all duration-200 ${
          isScrolled
            ? 'bg-white shadow-md'
            : 'bg-white/80 backdrop-blur-md'
        }`}
      >
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            {/* Logo */}
            <Link
              href="/"
              className="flex items-center gap-2 group"
            >
              {/* Icon with gradient background */}
              <div className="relative">
                <div className="absolute inset-0 bg-gradient-to-br from-primary to-accent rounded-lg blur-sm opacity-70 group-hover:opacity-100 transition-opacity"></div>
                <div className="relative bg-gradient-to-br from-primary to-accent p-2 rounded-lg">
                  <svg className="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2.5} d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6" />
                  </svg>
                </div>
              </div>
              {/* Brand text with gradient */}
              <span 
                className="font-bold text-xl bg-clip-text text-transparent bg-gradient-to-r from-primary via-accent to-buy"
                style={{ fontWeight: 700, letterSpacing: '-0.02em' }}
              >
                StockSignal
              </span>
            </Link>

            {/* Desktop Navigation */}
            <div className="hidden md:flex items-center gap-8">
              {/* Nav Links */}
              {NAV_LINKS.map((link) => (
                <a
                  key={link.href}
                  href={link.href}
                  onClick={(e) => {
                    e.preventDefault();
                    handleNavLinkClick(link.label, link.href);
                  }}
                  className="text-slate-700 hover:text-primary font-medium transition-colors"
                >
                  {link.label}
                </a>
              ))}
            </div>

            {/* Desktop Auth Buttons */}
            <div className="hidden md:flex items-center gap-4">
              {isAuthenticated ? (
                <>
                  {/* Dashboard Link */}
                  <Link
                    href="/dashboard"
                    className="text-slate-700 hover:text-primary font-medium transition-colors"
                  >
                    Dashboard
                  </Link>

                  {/* User Menu (Future: Avatar + Dropdown) */}
                  <div className="flex items-center gap-2 px-3 py-1 bg-slate-100 rounded-full text-sm font-medium text-slate-700">
                    <span className="w-6 h-6 rounded-full bg-primary text-white flex items-center justify-center text-xs">
                      U
                    </span>
                    {userPlan && (
                      <span className="capitalize">{userPlan}</span>
                    )}
                  </div>
                </>
              ) : (
                <>
                  {/* Sign In Link (Future) */}
                  <Link
                    href="/sign-in"
                    className="text-slate-700 hover:text-primary font-medium transition-colors"
                  >
                    Sign In
                  </Link>

                  {/* Get Started Button */}
                  <button
                    onClick={handleGetStartedClick}
                    className="px-6 py-2 bg-gradient-to-r from-[#0d9488] to-[#0369a1] text-white font-semibold rounded-lg hover:shadow-lg transition-all"
                  >
                    Get Started Free
                  </button>
                </>
              )}
            </div>

            {/* Mobile Menu Button */}
            <button
              onClick={() => setIsMobileMenuOpen(true)}
              className="md:hidden p-2 text-slate-700 hover:text-primary transition-colors"
              aria-label="Open menu"
              aria-expanded={isMobileMenuOpen}
            >
              <svg
                className="w-6 h-6"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M4 6h16M4 12h16M4 18h16"
                />
              </svg>
            </button>
          </div>
        </div>
      </nav>

      {/* Mobile Menu Overlay */}
      {isMobileMenuOpen && (
        <>
          {/* Backdrop */}
          <div
            className="fixed inset-0 bg-slate-900/50 backdrop-blur-sm z-40 md:hidden"
            onClick={() => setIsMobileMenuOpen(false)}
            aria-hidden="true"
          />

          {/* Menu Panel */}
          <div
            className="fixed top-0 right-0 bottom-0 w-full max-w-sm bg-white z-50 md:hidden animate-slide-in-right shadow-2xl"
            role="dialog"
            aria-modal="true"
            aria-label="Mobile navigation menu"
          >
            {/* Menu Header */}
            <div className="flex items-center justify-between p-4 border-b border-slate-200">
              <Link
                href="/"
                className="flex items-center gap-2 font-bold text-xl text-slate-900"
                onClick={() => setIsMobileMenuOpen(false)}
              >
                <span className="text-2xl">📊</span>
                <span>StockSignal</span>
              </Link>

              <button
                onClick={() => setIsMobileMenuOpen(false)}
                className="p-2 text-slate-700 hover:text-primary transition-colors"
                aria-label="Close menu"
              >
                <svg
                  className="w-6 h-6"
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

            {/* Menu Links */}
            <div className="flex flex-col p-4">
              <nav className="flex flex-col gap-2">
                {NAV_LINKS.map((link) => (
                  <a
                    key={link.href}
                    href={link.href}
                    onClick={(e) => {
                      e.preventDefault();
                      handleNavLinkClick(link.label, link.href);
                    }}
                    className="px-4 py-3 text-lg font-medium text-slate-700 hover:bg-slate-50 hover:text-primary rounded-lg transition-colors"
                  >
                    {link.label}
                  </a>
                ))}

                {isAuthenticated && (
                  <Link
                    href="/dashboard"
                    onClick={() => setIsMobileMenuOpen(false)}
                    className="px-4 py-3 text-lg font-medium text-slate-700 hover:bg-slate-50 hover:text-primary rounded-lg transition-colors"
                  >
                    Dashboard
                  </Link>
                )}
              </nav>

              {/* Mobile Auth Buttons */}
              <div className="mt-8 flex flex-col gap-3">
                {isAuthenticated ? (
                  <>
                    {/* User Info */}
                    <div className="flex items-center gap-3 px-4 py-3 bg-slate-100 rounded-lg">
                      <div className="w-10 h-10 rounded-full bg-primary text-white flex items-center justify-center font-semibold">
                        U
                      </div>
                      <div className="flex-1">
                        <div className="font-medium text-slate-900">Your Account</div>
                        {userPlan && (
                          <div className="text-sm text-slate-600 capitalize">
                            {userPlan} Plan
                          </div>
                        )}
                      </div>
                    </div>

                    {/* Sign Out Button (Future) */}
                    <button className="px-4 py-3 text-slate-700 hover:bg-slate-50 rounded-lg font-medium transition-colors">
                      Sign Out
                    </button>
                  </>
                ) : (
                  <>
                    <button
                      onClick={handleGetStartedClick}
                      className="w-full px-6 py-3 bg-gradient-to-r from-[#0d9488] to-[#0369a1] text-white font-semibold rounded-lg hover:shadow-lg transition-all"
                    >
                      Get Started Free
                    </button>

                    <Link
                      href="/sign-in"
                      onClick={() => setIsMobileMenuOpen(false)}
                      className="w-full px-6 py-3 text-center border-2 border-slate-300 text-slate-700 hover:border-primary hover:text-primary font-semibold rounded-lg transition-colors"
                    >
                      Sign In
                    </Link>
                  </>
                )}
              </div>
            </div>
          </div>
        </>
      )}

      {/* Spacer to prevent content from being hidden under fixed nav */}
      <div className="h-16" aria-hidden="true" />
    </>
  );
}

