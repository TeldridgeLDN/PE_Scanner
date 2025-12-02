import { currentUser } from '@clerk/nextjs/server';
import { redirect } from 'next/navigation';
import Link from 'next/link';

export default async function DashboardPage() {
  const user = await currentUser();

  if (!user) {
    redirect('/sign-in');
  }

  // Get user plan from metadata (default to 'free')
  const userPlan = (user.publicMetadata?.plan as string) || 'free';
  const isPro = userPlan === 'pro' || userPlan === 'premium';

  // Plan badge styling with colored backgrounds
  const planBadge = {
    free: { 
      emoji: '🆓', 
      text: 'Free',
      badgeBg: 'bg-slate-100',
      badgeText: 'text-slate-700',
      badgeBorder: 'border-slate-200'
    },
    pro: { 
      emoji: '⭐', 
      text: 'Pro',
      badgeBg: 'bg-primary/10',
      badgeText: 'text-primary',
      badgeBorder: 'border-primary/20'
    },
    premium: { 
      emoji: '💎', 
      text: 'Premium',
      badgeBg: 'bg-purple-100',
      badgeText: 'text-purple-700',
      badgeBorder: 'border-purple-200'
    }
  }[userPlan] || { 
    emoji: '🆓', 
    text: 'Free',
    badgeBg: 'bg-slate-100',
    badgeText: 'text-slate-700',
    badgeBorder: 'border-slate-200'
  };

  return (
    <div className="min-h-screen bg-slate-50">
      {/* Hero Section - Light style matching main page */}
      <section className="relative pt-32 pb-12 overflow-hidden bg-white border-b border-slate-200">
        {/* Subtle gradient background like main page */}
        <div className="absolute inset-0 -z-10">
          <div 
            className="absolute inset-0"
            style={{
              background: `linear-gradient(135deg, #ffffff 0%, #f0fdfa 25%, #ecfeff 50%, #f0f9ff 75%, #ffffff 100%)`
            }}
          />
          
          {/* Animated gradient orbs like main page */}
          <div 
            className="absolute inset-0 opacity-40"
            style={{
              background: `
                radial-gradient(circle at 20% 30%, rgba(13, 148, 136, 0.15) 0%, transparent 50%),
                radial-gradient(circle at 80% 20%, rgba(3, 105, 161, 0.12) 0%, transparent 50%),
                radial-gradient(circle at 40% 70%, rgba(5, 150, 105, 0.1) 0%, transparent 50%)
              `,
              animation: 'float 20s ease-in-out infinite'
            }}
          />
        </div>
        
        <div className="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between mb-8">
            <div className="animate-slide-up">
              <div className="mb-2">
                <p className="text-sm text-slate-600 font-medium">Welcome back</p>
                <h1 className="font-heading text-4xl md:text-5xl font-black text-slate-900 tracking-tight">
                  {user.firstName || 'Investor'}
                </h1>
              </div>
              <p className="text-slate-600 text-lg">
                Here's what's happening with your investments today
              </p>
            </div>

            {/* Plan Badge - Colored badge style */}
            <div className="animate-fade-in text-right">
              <p className="text-xs text-slate-600 font-medium mb-2">Current Plan</p>
              <span className={`inline-block px-4 py-2 rounded-lg border-2 ${planBadge.badgeBg} ${planBadge.badgeText} ${planBadge.badgeBorder} font-bold text-sm`}>
                {planBadge.text}
              </span>
              {isPro && (
                <p className="text-xs text-buy font-bold mt-1">✓ Unlimited</p>
              )}
            </div>
          </div>
        </div>
      </section>

      {/* Main Content Section - Light background like main page */}
      <section className="py-12 bg-slate-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          {/* Today's Summary - Matching main page card style */}
          <div className="mb-12 animate-fade-in">
            <div className="bg-white rounded-2xl shadow-sm border border-slate-200 p-8">
              <div className="flex items-center justify-between mb-8">
                <h2 className="font-heading text-3xl font-bold text-slate-900 flex items-center gap-3">
                  <div className="w-12 h-12 rounded-lg bg-primary/10 flex items-center justify-center">
                    <svg className="w-6 h-6 text-primary" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2.5} d="M13 10V3L4 14h7v7l9-11h-7z" />
                    </svg>
                  </div>
                  Today's Summary
                </h2>
                <span className="text-sm text-slate-600 font-medium">
                  {new Date().toLocaleDateString('en-GB', { weekday: 'long', month: 'long', day: 'numeric' })}
                </span>
              </div>

              <div className="grid grid-cols-3 gap-6">
                {/* Analyses Today */}
                <div className="relative group">
                  <div className="relative p-6 rounded-xl bg-slate-50 border border-slate-200 hover:border-primary/30 hover:shadow-md transition-all">
                    <div className="flex items-start justify-between mb-4">
                      <div className="w-12 h-12 rounded-lg bg-primary/10 flex items-center justify-center">
                        <svg className="w-6 h-6 text-primary" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2.5} d="M16 8v8m-4-5v5m-4-2v2m-2 4h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
                        </svg>
                      </div>
                      {!isPro && (
                        <span className="px-2 py-1 bg-primary/10 text-primary text-xs font-bold rounded-lg">
                          {10 - 0} left
                        </span>
                      )}
                    </div>
                    <div className="space-y-1">
                      <p className="text-4xl font-black text-slate-900">
                        0<span className="text-2xl text-slate-400 font-normal"> / {isPro ? '∞' : '10'}</span>
                      </p>
                      <p className="text-sm text-slate-600 font-medium">Analyses used</p>
                    </div>
                  </div>
                </div>

                {/* Days Active */}
                <div className="relative group">
                  <div className="relative p-6 rounded-xl bg-slate-50 border border-slate-200 hover:border-accent/30 hover:shadow-md transition-all">
                    <div className="flex items-start justify-between mb-4">
                      <div className="w-12 h-12 rounded-lg bg-accent/10 flex items-center justify-center">
                        <svg className="w-6 h-6 text-accent" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2.5} d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
                        </svg>
                      </div>
                      <span className="px-2 py-1 bg-accent/10 text-accent text-xs font-bold rounded-lg">
                        Active
                      </span>
                    </div>
                    <div className="space-y-1">
                      <p className="text-4xl font-black text-slate-900">
                        {Math.floor((Date.now() - new Date(user.createdAt).getTime()) / (1000 * 60 * 60 * 24))}
                      </p>
                      <p className="text-sm text-slate-600 font-medium">Days as member</p>
                    </div>
                  </div>
                </div>

                {/* Portfolio Value (Coming Soon) */}
                <div className="relative group opacity-60">
                  <div className="relative p-6 rounded-xl bg-slate-50 border border-slate-200">
                    <div className="flex items-start justify-between mb-4">
                      <div className="w-12 h-12 rounded-lg bg-buy/10 flex items-center justify-center">
                        <svg className="w-6 h-6 text-buy" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2.5} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                        </svg>
                      </div>
                      <span className="px-2 py-1 bg-slate-100 text-slate-500 text-xs font-bold rounded-lg">
                        Soon
                      </span>
                    </div>
                    <div className="space-y-1">
                      <p className="text-4xl font-black text-slate-400">—</p>
                      <p className="text-sm text-slate-500 font-medium">Portfolio tracked</p>
                    </div>
                  </div>
                </div>
              </div>

              {/* Upgrade CTA */}
              {!isPro && (
                <div className="mt-6 p-4 rounded-2xl bg-gradient-to-r from-primary/5 via-accent/5 to-buy/5 border-2 border-primary/20">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-4">
                      <div className="w-10 h-10 rounded-full bg-gradient-to-br from-primary to-buy flex items-center justify-center">
                        <svg className="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2.5} d="M13 10V3L4 14h7v7l9-11h-7z" />
                        </svg>
                      </div>
                      <div>
                        <p className="text-sm font-bold text-slate-900">Unlock unlimited analyses</p>
                        <p className="text-xs text-slate-600">Upgrade to Pro for just £25/month</p>
                      </div>
                    </div>
                    <Link
                      href="/#pricing"
                      className="group relative px-6 py-3 bg-gradient-to-r from-primary via-accent to-buy text-white font-bold rounded-xl hover:shadow-xl hover:shadow-primary/30 transition-all hover:scale-105 overflow-hidden"
                    >
                      <span className="relative z-10 flex items-center gap-2">
                        Upgrade Now
                        <svg className="w-4 h-4 group-hover:translate-x-1 transition-transform" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2.5} d="M13 7l5 5m0 0l-5 5m5-5H6" />
                        </svg>
                      </span>
                      <div className="absolute inset-0 bg-gradient-to-r from-transparent via-white/20 to-transparent translate-x-[-100%] group-hover:translate-x-[100%] transition-transform duration-700"></div>
                    </Link>
                  </div>
                </div>
              )}
            </div>
          </div>

          {/* Quick Actions Section - Matching main page style */}
          <div className="mb-12">
            <div className="text-center max-w-3xl mx-auto mb-8">
              <h2 className="font-heading text-3xl sm:text-4xl font-bold text-slate-900 mb-4">
                Quick Actions
              </h2>
              <p className="text-lg text-slate-600">
                Everything you need to analyze stocks and manage your portfolio
              </p>
            </div>
            
            {/* Grid layout matching main page */}
            <div className="grid md:grid-cols-3 gap-6">
              {/* Primary Action - Analyze Stock */}
              <Link
                href="/#analyze"
                className="group relative p-8 bg-white rounded-2xl shadow-sm border border-slate-200 hover:shadow-md hover:border-primary/30 transition-all"
              >
                <div className="mb-6">
                  <div className="w-12 h-12 rounded-lg bg-primary/10 flex items-center justify-center mb-4 group-hover:scale-110 transition-transform">
                    <svg className="w-6 h-6 text-primary" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2.5} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
                    </svg>
                  </div>
                  
                  <h3 className="font-heading text-xl font-bold text-slate-900 mb-3 group-hover:text-primary transition-colors">
                    Analyze Stock
                  </h3>
                  <p className="text-slate-600">
                    Search any ticker and get instant P/E compression analysis with clear BUY/SELL/HOLD signals.
                  </p>
                </div>
                
                <div className="flex items-center gap-2 text-primary font-bold group-hover:gap-3 transition-all">
                  <span>Start analyzing</span>
                  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2.5} d="M13 7l5 5m0 0l-5 5m5-5H6" />
                  </svg>
                </div>
              </Link>

              {/* Secondary Actions */}
              <div className="relative p-8 bg-white rounded-2xl shadow-sm border border-slate-200 opacity-60">
                <div className="mb-6">
                  <div className="w-12 h-12 rounded-lg bg-accent/10 flex items-center justify-center mb-4">
                    <svg className="w-6 h-6 text-accent" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2.5} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                    </svg>
                  </div>
                  
                  <div className="flex items-center gap-2 mb-3">
                    <h3 className="font-heading text-xl font-bold text-slate-900">Portfolio Upload</h3>
                    <span className="px-2 py-1 bg-amber-100 text-amber-700 text-xs font-bold rounded-md">Soon</span>
                  </div>
                  <p className="text-slate-600">
                    Upload your portfolio CSV and analyze all holdings in one click.
                  </p>
                </div>
              </div>

              <div className="relative p-8 bg-white rounded-2xl shadow-sm border border-slate-200 opacity-60">
                <div className="mb-6">
                  <div className="w-12 h-12 rounded-lg bg-buy/10 flex items-center justify-center mb-4">
                    <svg className="w-6 h-6 text-buy" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2.5} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                    </svg>
                  </div>
                  
                  <div className="flex items-center gap-2 mb-3">
                    <h3 className="font-heading text-xl font-bold text-slate-900">Analysis History</h3>
                    <span className="px-2 py-1 bg-amber-100 text-amber-700 text-xs font-bold rounded-md">Soon</span>
                  </div>
                  <p className="text-slate-600">
                    View past analyses and track performance over time.
                  </p>
                </div>
              </div>
            </div>
          </div>

          {/* Resources & Support Section */}
          <div className="mb-12">
            <div className="text-center max-w-3xl mx-auto mb-8">
              <h2 className="font-heading text-3xl sm:text-4xl font-bold text-slate-900 mb-4">
                Resources & Support
              </h2>
              <p className="text-lg text-slate-600">
                Get help, learn more, and connect with us
              </p>
            </div>
          
            
            <div className="grid md:grid-cols-3 gap-6">
              <a href="/#how-it-works" className="group p-6 bg-white rounded-xl border border-slate-200 hover:border-primary/30 hover:shadow-md transition-all">
              <div className="flex items-center gap-4 mb-3">
                <div className="w-10 h-10 rounded-xl bg-primary/10 flex items-center justify-center group-hover:scale-110 transition-transform">
                  <svg className="w-5 h-5 text-primary" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2.5} d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253" />
                  </svg>
                </div>
                <h4 className="font-bold text-slate-900 group-hover:text-primary transition-colors">Learn the Basics</h4>
              </div>
              <p className="text-sm text-slate-600">Understand P/E compression</p>
            </a>

              <a href="/#faq" className="group p-6 bg-white rounded-xl border border-slate-200 hover:border-accent/30 hover:shadow-md transition-all">
              <div className="flex items-center gap-4 mb-3">
                <div className="w-10 h-10 rounded-xl bg-accent/10 flex items-center justify-center group-hover:scale-110 transition-transform">
                  <svg className="w-5 h-5 text-accent" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2.5} d="M8.228 9c.549-1.165 2.03-2 3.772-2 2.21 0 4 1.343 4 3 0 1.4-1.278 2.575-3.006 2.907-.542.104-.994.54-.994 1.093m0 3h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                </div>
                <h4 className="font-bold text-slate-900 group-hover:text-accent transition-colors">FAQs</h4>
              </div>
              <p className="text-sm text-slate-600">Get answers quickly</p>
            </a>

              <a href="mailto:support@stocksignal.app" className="group p-6 bg-white rounded-xl border border-slate-200 hover:border-buy/30 hover:shadow-md transition-all">
              <div className="flex items-center gap-4 mb-3">
                <div className="w-10 h-10 rounded-xl bg-buy/10 flex items-center justify-center group-hover:scale-110 transition-transform">
                  <svg className="w-5 h-5 text-buy" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2.5} d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
                  </svg>
                </div>
                <h4 className="font-bold text-slate-900 group-hover:text-buy transition-colors">Contact Support</h4>
              </div>
              <p className="text-sm text-slate-600">We're here to help</p>
              </a>
            </div>
          </div>

          {/* Account Details Card */}
          <div className="bg-white rounded-2xl shadow-sm border border-slate-200 p-8">
            <div className="flex items-center justify-between mb-8">
              <h3 className="font-heading text-2xl font-bold text-slate-900 flex items-center gap-3">
                <div className="w-10 h-10 rounded-lg bg-primary/10 flex items-center justify-center">
                  <svg className="w-5 h-5 text-primary" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2.5} d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
                  </svg>
                </div>
                Account Details
              </h3>
              <span className="px-3 py-1.5 bg-buy/10 text-buy text-xs font-bold rounded-full flex items-center gap-2">
                <span className="w-2 h-2 bg-buy rounded-full animate-pulse"></span>
                Active
              </span>
            </div>
          
            <div className="grid md:grid-cols-3 gap-8">
              <div>
                <p className="text-slate-600 font-medium mb-2 text-sm">Email Address</p>
                <p className="text-slate-900 font-semibold">{user.emailAddresses[0]?.emailAddress}</p>
              </div>
              
              <div>
                <p className="text-slate-600 font-medium mb-2 text-sm">Member Since</p>
                <p className="text-slate-900 font-semibold">
                  {new Date(user.createdAt).toLocaleDateString('en-GB', { 
                    year: 'numeric', 
                    month: 'long', 
                    day: 'numeric' 
                  })}
                </p>
              </div>
              
              <div>
                <p className="text-slate-600 font-medium mb-2 text-sm">Subscription Plan</p>
                <span className={`inline-block px-4 py-2 rounded-lg border-2 ${planBadge.badgeBg} ${planBadge.badgeText} ${planBadge.badgeBorder} font-bold text-sm`}>
                  {planBadge.text}
                </span>
              </div>
            </div>
          </div>
        </div>
      </section>
    </div>
  );
}

