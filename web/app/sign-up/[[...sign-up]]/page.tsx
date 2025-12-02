import { SignUp } from '@clerk/nextjs';

export default function SignUpPage() {
  return (
    <div className="min-h-screen bg-slate-50 flex items-center justify-center py-12 px-4 sm:px-6 lg:px-8">
      <div className="w-full max-w-md">
        {/* Header */}
        <div className="text-center mb-8">
          <h1 className="text-3xl font-bold text-slate-900 mb-2">
            Start Your Free Account
          </h1>
          <p className="text-slate-600">
            Get 10 free analyses per day. Upgrade anytime for unlimited access.
          </p>
        </div>

        {/* Clerk Sign Up Component */}
        <SignUp 
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
            Already have an account?{' '}
            <a href="/sign-in" className="text-primary font-semibold hover:text-primary-dark">
              Sign in
            </a>
          </p>
        </div>

        {/* Trust Indicators */}
        <div className="mt-6 text-center text-xs text-slate-500">
          <p>✓ No credit card required • ✓ Cancel anytime</p>
        </div>
      </div>
    </div>
  );
}

