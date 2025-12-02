import { SignIn } from '@clerk/nextjs';

export default function SignInPage() {
  return (
    <div className="min-h-screen bg-slate-50 flex items-center justify-center py-12 px-4 sm:px-6 lg:px-8">
      <div className="w-full max-w-md">
        {/* Header */}
        <div className="text-center mb-8">
          <h1 className="text-3xl font-bold text-slate-900 mb-2">
            Welcome Back to StockSignal
          </h1>
          <p className="text-slate-600">
            Sign in to access your dashboard and unlimited analyses
          </p>
        </div>

        {/* Clerk Sign In Component */}
        <SignIn 
          appearance={{
            elements: {
              rootBox: "mx-auto",
              card: "shadow-xl",
            }
          }}
        />

        {/* Additional Info */}
        <div className="mt-8 text-center text-sm text-slate-600">
          <p>
            Don't have an account?{' '}
            <a href="/sign-up" className="text-primary font-semibold hover:text-primary-dark">
              Sign up for free
            </a>
          </p>
        </div>
      </div>
    </div>
  );
}

