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

  return (
    <div className="min-h-screen bg-slate-50 py-12">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-4xl font-bold text-slate-900 mb-2">
            Welcome back, {user.firstName || 'Investor'}!
          </h1>
          <p className="text-lg text-slate-600">
            Your StockSignal dashboard
          </p>
        </div>

        {/* Plan Status Card */}
        <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-8 mb-8">
          <div className="flex items-center justify-between">
            <div>
              <h2 className="text-2xl font-bold text-slate-900 mb-2">
                {userPlan === 'premium' ? '💎 Premium' : userPlan === 'pro' ? '⭐ Pro' : '🆓 Free'} Plan
              </h2>
              <p className="text-slate-600">
                {isPro ? (
                  'You have unlimited analyses'
                ) : (
                  'You have 10 analyses per day'
                )}
              </p>
            </div>
            {!isPro && (
              <Link
                href="#pricing"
                className="px-6 py-3 bg-gradient-to-r from-primary to-accent text-white font-bold rounded-xl hover:shadow-lg transition-all"
              >
                Upgrade to Pro
              </Link>
            )}
          </div>
        </div>

        {/* Quick Actions Grid */}
        <div className="grid md:grid-cols-3 gap-6 mb-8">
          <Link
            href="/#analyze"
            className="bg-white rounded-xl shadow-sm border border-slate-200 p-6 hover:shadow-md transition-all group"
          >
            <div className="flex items-center gap-4 mb-4">
              <div className="w-12 h-12 rounded-lg bg-primary/10 flex items-center justify-center group-hover:bg-primary/20 transition-colors">
                <svg className="w-6 h-6 text-primary" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <circle cx="11" cy="11" r="8" strokeWidth="2"/>
                  <path d="M21 21l-4.35-4.35" strokeWidth="2" strokeLinecap="round"/>
                </svg>
              </div>
              <div>
                <h3 className="text-lg font-bold text-slate-900">Analyze Stock</h3>
                <p className="text-sm text-slate-600">Search any ticker</p>
              </div>
            </div>
          </Link>

          <Link
            href="#portfolio"
            className="bg-white rounded-xl shadow-sm border border-slate-200 p-6 hover:shadow-md transition-all group opacity-50 cursor-not-allowed"
          >
            <div className="flex items-center gap-4 mb-4">
              <div className="w-12 h-12 rounded-lg bg-accent/10 flex items-center justify-center">
                <svg className="w-6 h-6 text-accent" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                </svg>
              </div>
              <div>
                <h3 className="text-lg font-bold text-slate-900">Upload Portfolio</h3>
                <p className="text-sm text-slate-600">Coming soon</p>
              </div>
            </div>
          </Link>

          <Link
            href="#history"
            className="bg-white rounded-xl shadow-sm border border-slate-200 p-6 hover:shadow-md transition-all group opacity-50 cursor-not-allowed"
          >
            <div className="flex items-center gap-4 mb-4">
              <div className="w-12 h-12 rounded-lg bg-buy/10 flex items-center justify-center">
                <svg className="w-6 h-6 text-buy" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
              </div>
              <div>
                <h3 className="text-lg font-bold text-slate-900">Analysis History</h3>
                <p className="text-sm text-slate-600">Coming soon</p>
              </div>
            </div>
          </Link>
        </div>

        {/* Account Info */}
        <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-8">
          <h2 className="text-xl font-bold text-slate-900 mb-4">Account Information</h2>
          <div className="space-y-3 text-slate-600">
            <div className="flex justify-between">
              <span>Email:</span>
              <span className="font-medium">{user.emailAddresses[0]?.emailAddress}</span>
            </div>
            <div className="flex justify-between">
              <span>Member since:</span>
              <span className="font-medium">
                {new Date(user.createdAt).toLocaleDateString('en-GB', { 
                  year: 'numeric', 
                  month: 'long', 
                  day: 'numeric' 
                })}
              </span>
            </div>
            <div className="flex justify-between">
              <span>Plan:</span>
              <span className="font-medium capitalize">{userPlan}</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

