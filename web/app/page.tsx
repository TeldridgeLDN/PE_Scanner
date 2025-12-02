import Link from 'next/link';
import TickerSearchForm from '@/components/TickerSearchForm';
import PricingSection from '@/components/PricingSection';
import Footer from '@/components/Footer';

// ============================================================================
// PE SCANNER LANDING PAGE
// Stock Valuation Made Simple
// ============================================================================

export default function Home() {
  return (
    <div className="min-h-screen bg-slate-50">
      {/* Hero Section */}
      <HeroSection />
      
      {/* Social Proof Bar */}
      <SocialProofBar />
      
      {/* How It Works */}
      <HowItWorksSection />
      
      {/* Features - 7 Analysis Features */}
      <FeaturesSection />
      
      {/* Pricing */}
      <PricingSection />
      
      {/* Example Results */}
      <ExampleResultsSection />
      
      {/* Final CTA */}
      <FinalCTASection />
      
      {/* FAQ */}
      <FAQSection />
      
      {/* Footer */}
      <Footer />
    </div>
  );
}

// ============================================================================
// HERO SECTION
// ============================================================================

function HeroSection() {
  return (
    <section id="analyze" className="relative pt-32 pb-20 md:pt-40 md:pb-32 overflow-hidden">
      {/* Background Gradient Mesh */}
      <div 
        className="absolute inset-0 -z-10"
        style={{
          background: `
            radial-gradient(at 40% 20%, hsla(238, 83%, 67%, 0.12) 0px, transparent 50%),
            radial-gradient(at 80% 0%, hsla(155, 80%, 50%, 0.08) 0px, transparent 50%),
            radial-gradient(at 0% 50%, hsla(0, 84%, 60%, 0.08) 0px, transparent 50%),
            radial-gradient(at 80% 50%, hsla(43, 96%, 56%, 0.08) 0px, transparent 50%),
            radial-gradient(at 0% 100%, hsla(180, 100%, 50%, 0.08) 0px, transparent 50%),
            linear-gradient(to bottom, #FAFAFA, #F1F5F9)
          `
        }}
      />
      
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="text-center max-w-4xl mx-auto">
          {/* Badge */}
          <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-primary/10 border border-primary/20 mb-8 animate-fade-in">
            <span className="w-2 h-2 rounded-full bg-primary animate-pulse"></span>
            <span className="text-sm font-medium text-primary-dark">Free analysis • No signup required</span>
          </div>
          
          {/* Headline */}
          <h1 className="font-heading text-4xl sm:text-5xl md:text-6xl lg:text-7xl font-bold text-slate-900 mb-6 leading-tight animate-slide-up">
            Spot Earnings Collapses{' '}
            <span 
              className="bg-clip-text text-transparent"
              style={{ backgroundImage: 'linear-gradient(135deg, #0d9488 0%, #0369a1 50%, #059669 100%)' }}
            >
              Before Your Portfolio Does
            </span>
          </h1>
          
          {/* Subheadline */}
          <p className="text-lg sm:text-xl text-slate-600 mb-10 max-w-2xl mx-auto animate-slide-up" style={{ animationDelay: '100ms' }}>
            Free analysis reveals which stocks are priced for disaster. Get clear BUY/SELL/HOLD signals in 30 seconds.
          </p>
          
          {/* Ticker Search Form */}
          <div className="animate-slide-up" style={{ animationDelay: '200ms' }}>
            <TickerSearchForm />
          </div>
          
          {/* Trust Indicators */}
          <div className="flex flex-wrap items-center justify-center gap-6 mt-8 text-sm text-slate-500 animate-fade-in" style={{ animationDelay: '300ms' }}>
            <div className="flex items-center gap-2">
              <svg className="w-5 h-5 text-buy" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
              </svg>
              <span>Results in 30 seconds</span>
            </div>
            <div className="flex items-center gap-2">
              <svg className="w-5 h-5 text-buy" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
              </svg>
              <span>No credit card required</span>
            </div>
            <div className="flex items-center gap-2">
              <svg className="w-5 h-5 text-buy" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
              </svg>
              <span>10 free analyses per day</span>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}


// ============================================================================
// SOCIAL PROOF BAR
// ============================================================================

function SocialProofBar() {
  return (
    <section className="py-8 bg-white border-y border-slate-200">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex flex-col md:flex-row items-center justify-center gap-8 text-center md:text-left">
          <div className="flex items-center gap-3">
            <div className="text-3xl font-bold text-slate-900">10,000+</div>
            <div className="text-sm text-slate-600">Stocks analyzed<br />in November 2024</div>
          </div>
          <div className="hidden md:block w-px h-12 bg-slate-300"></div>
          <div className="flex items-center gap-3">
            <div className="px-3 py-1 rounded-lg bg-sell/10 text-sell font-semibold">-113% SELL</div>
            <div className="text-sm text-slate-600">HOOD predicted<br />(53% drop confirmed)</div>
          </div>
          <div className="hidden md:block w-px h-12 bg-slate-300"></div>
          <div className="flex items-center gap-3">
            <div className="px-3 py-1 rounded-lg bg-buy/10 text-buy font-semibold">+62% BUY</div>
            <div className="text-sm text-slate-600">BATS.L identified<br />(undervalued gem)</div>
          </div>
        </div>
      </div>
    </section>
  );
}

// ============================================================================
// HOW IT WORKS SECTION
// ============================================================================

function HowItWorksSection() {
  const steps = [
    {
      number: "1",
      title: "Enter Ticker Symbol",
      description: "Type any stock ticker (AAPL, HOOD, BATS.L). We support US and UK markets with automatic data corrections.",
      icon: "🔍"
    },
    {
      number: "2",
      title: "AI Analyzes in 30 Seconds",
      description: "Our engine classifies your stock into VALUE, GROWTH, or HYPER_GROWTH tiers and runs the appropriate analysis (P/E compression, PEG ratio, or Rule of 40).",
      icon: "🤖"
    },
    {
      number: "3",
      title: "Get Shareable Results",
      description: "Receive a clear BUY/SELL/HOLD signal with a viral-optimised headline and 'What Would Have To Be True' anchoring statement. Share on Twitter or LinkedIn instantly.",
      icon: "📊"
    }
  ];

  return (
    <section id="how-it-works" className="py-20 bg-slate-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="text-center max-w-3xl mx-auto mb-16">
          <h2 className="font-heading text-3xl sm:text-4xl md:text-5xl font-bold text-slate-900 mb-4">
            How It Works
          </h2>
          <p className="text-lg text-slate-600">
            From ticker to insight in three simple steps
          </p>
        </div>

        <div className="grid md:grid-cols-3 gap-8">
          {steps.map((step, index) => (
            <div 
              key={index}
              className="relative p-8 bg-white rounded-2xl shadow-sm border border-slate-200 hover:shadow-md transition-shadow"
            >
              {/* Step Number */}
              <div className="absolute -top-4 left-8 w-8 h-8 rounded-full bg-primary text-white flex items-center justify-center font-bold">
                {step.number}
              </div>
              
              {/* Icon */}
              <div className="text-5xl mb-4">{step.icon}</div>
              
              {/* Content */}
              <h3 className="font-heading text-xl font-bold text-slate-900 mb-3">
                {step.title}
              </h3>
              <p className="text-slate-600">
                {step.description}
              </p>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}

// ============================================================================
// FEATURES SECTION
// ============================================================================

function FeaturesSection() {
  const features = [
    {
      title: "P/E Compression Analysis",
      description: "Detect market expectations by comparing Trailing P/E vs Forward P/E. Negative compression = earnings collapse expected.",
      icon: (
        <svg className="w-10 h-10 text-primary" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 17h8m0 0V9m0 8l-8-8-4 4-6-6" />
        </svg>
      ),
      tier: "VALUE"
    },
    {
      title: "Growth Stock (PEG) Support",
      description: "For stocks with P/E 25-50, we calculate PEG ratio to find undervalued growth opportunities. PEG < 1.0 = BUY signal.",
      icon: (
        <svg className="w-10 h-10 text-primary" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6" />
        </svg>
      ),
      tier: "GROWTH"
    },
    {
      title: "Hyper-Growth Analysis",
      description: "For unprofitable or P/E > 50 stocks, we use Price/Sales + Rule of 40 (Revenue Growth % + Profit Margin %).",
      icon: (
        <svg className="w-10 h-10 text-primary" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 3v4M3 5h4M6 17v4m-2-2h4m5-16l2.286 6.857L21 12l-5.714 2.143L13 21l-2.286-6.857L5 12l5.714-2.143L13 3z" />
        </svg>
      ),
      tier: "HYPER_GROWTH"
    },
    {
      title: "Shareable Headlines",
      description: "Get viral-optimised headlines like '🚨 HOOD is priced like it's going bankrupt' that capture attention on social media.",
      icon: (
        <svg className="w-10 h-10 text-primary" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 20H5a2 2 0 01-2-2V6a2 2 0 012-2h10a2 2 0 012 2v1m2 13a2 2 0 01-2-2V7m2 13a2 2 0 002-2V9a2 2 0 00-2-2h-2m-4-3H9M7 16h6M7 8h6v4H7V8z" />
        </svg>
      ),
      tier: "ALL"
    },
    {
      title: "Anchoring Context",
      description: "'What Would Have To Be True' statements make analysis memorable: 'HOOD would need to 2.5x profits to justify current price'.",
      icon: (
        <svg className="w-10 h-10 text-primary" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 7h.01M7 3h5c.512 0 1.024.195 1.414.586l7 7a2 2 0 010 2.828l-7 7a2 2 0 01-2.828 0l-7-7A1.994 1.994 0 013 12V7a4 4 0 014-4z" />
        </svg>
      ),
      tier: "ALL"
    },
    {
      title: "Fair Value Scenarios",
      description: "Bear case (17.5x P/E) and Bull case (37.5x P/E) valuations show upside/downside potential from current price.",
      icon: (
        <svg className="w-10 h-10 text-primary" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
      ),
      tier: "VALUE"
    },
    {
      title: "Data Quality Validation",
      description: "Auto-corrects UK stock data (pence→pounds), detects stock splits, flags suspicious analyst estimates.",
      icon: (
        <svg className="w-10 h-10 text-primary" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
      ),
      tier: "ALL"
    }
  ];

  return (
    <section id="features" className="py-20 bg-white">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="text-center max-w-3xl mx-auto mb-16">
          <h2 className="font-heading text-3xl sm:text-4xl md:text-5xl font-bold text-slate-900 mb-4">
            Comprehensive Analysis Features
          </h2>
          <p className="text-lg text-slate-600">
            Tiered approach adapts to VALUE, GROWTH, or HYPER_GROWTH stocks
          </p>
        </div>

        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
          {features.map((feature, index) => (
            <div 
              key={index}
              className="p-6 bg-slate-50 rounded-xl border border-slate-200 hover:border-primary/30 hover:shadow-md transition-all"
            >
              {/* Icon & Tier Badge */}
              <div className="flex items-start justify-between mb-4">
                <div className="flex items-center justify-center w-12 h-12 rounded-lg bg-primary/10">
                  {feature.icon}
                </div>
                <span className="px-2 py-1 text-xs font-semibold rounded-md bg-primary/10 text-primary">
                  {feature.tier}
                </span>
              </div>
              
              {/* Content */}
              <h3 className="font-heading text-lg font-bold text-slate-900 mb-2">
                {feature.title}
              </h3>
              <p className="text-sm text-slate-600">
                {feature.description}
              </p>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}

// ============================================================================
// PRICING SECTION (imported from components/PricingSection.tsx)
// ============================================================================

// ============================================================================
// EXAMPLE RESULTS SECTION
// ============================================================================

function ExampleResultsSection() {
  const examples = [
    {
      ticker: "HOOD",
      company: "Robinhood",
      signal: "SELL",
      compression: "-113%",
      headline: "🚨 HOOD is priced like it's going bankrupt",
      anchor: "HOOD would need to 2.5x profits to justify current price",
      outcome: "53% drop confirmed",
      signalColor: "sell"
    },
    {
      ticker: "META",
      company: "Meta Platforms",
      signal: "BUY",
      compression: "+42%",
      headline: "📈 META is undervalued despite strong fundamentals",
      anchor: "META would need earnings to fall 30% to justify selling",
      outcome: "Holding strong",
      signalColor: "buy"
    },
    {
      ticker: "BATS.L",
      company: "British American Tobacco",
      signal: "BUY",
      compression: "+62%",
      headline: "💎 BATS.L hidden gem with massive upside",
      anchor: "BATS.L has 280% bull case upside from current price",
      outcome: "Undervalued dividend play",
      signalColor: "buy"
    }
  ];

  return (
    <section id="examples" className="py-20 bg-white">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="text-center max-w-3xl mx-auto mb-16">
          <h2 className="font-heading text-3xl sm:text-4xl md:text-5xl font-bold text-slate-900 mb-4">
            Real Analysis Examples
          </h2>
          <p className="text-lg text-slate-600">
            See how PE Scanner caught major moves in November 2024
          </p>
        </div>

        <div className="grid md:grid-cols-3 gap-6">
          {examples.map((example, index) => (
            <div 
              key={index}
              className="p-6 bg-slate-50 rounded-xl border-2 border-slate-200 hover:border-primary/30 hover:shadow-lg transition-all"
            >
              {/* Header */}
              <div className="flex items-start justify-between mb-4">
                <div>
                  <div className="font-bold text-xl text-slate-900">{example.ticker}</div>
                  <div className="text-sm text-slate-600">{example.company}</div>
                </div>
                <div className={`px-3 py-1 rounded-lg font-bold signal-${example.signalColor}`}>
                  {example.signal}
                </div>
              </div>
              
              {/* Compression */}
              <div className="mb-4">
                <div className="text-sm text-slate-600 mb-1">P/E Compression</div>
                <div className={`text-2xl font-bold ${example.signalColor === 'buy' ? 'text-buy' : 'text-sell'}`}>
                  {example.compression}
                </div>
              </div>
              
              {/* Headline */}
              <div className="mb-3 p-3 bg-white rounded-lg border border-slate-200">
                <div className="text-sm font-medium text-slate-900">
                  {example.headline}
                </div>
              </div>
              
              {/* Anchor */}
              <div className="mb-3 text-sm text-slate-600 italic">
                "{example.anchor}"
              </div>
              
              {/* Outcome */}
              <div className="pt-3 border-t border-slate-200">
                <div className="text-xs text-slate-500">Outcome:</div>
                <div className="text-sm font-medium text-slate-900">{example.outcome}</div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}

// ============================================================================
// FINAL CTA SECTION
// ============================================================================

function FinalCTASection() {
  return (
    <section className="py-20 bg-gradient-to-br from-[#0d9488] to-[#0369a1] text-white">
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
        <h2 className="font-heading text-3xl sm:text-4xl md:text-5xl font-bold mb-6">
          Don't Let Your Portfolio Hold the Next Collapse
        </h2>
        <p className="text-xl mb-8 text-primary-light">
          Start scanning for free. Get 10 analyses per day. No credit card required.
        </p>
        <div className="flex flex-col sm:flex-row gap-4 justify-center">
          <button className="px-8 py-4 bg-white text-[#0d9488] rounded-xl font-bold text-lg hover:bg-slate-50 hover:text-[#0f766e] transition-colors">
            Scan My Portfolio Now
          </button>
          <button className="px-8 py-4 bg-[#0f766e] text-white rounded-xl font-bold text-lg hover:bg-[#0d9488] transition-colors border-2 border-white/20">
            View Pricing
          </button>
        </div>
        <p className="text-sm text-primary-light mt-6">
          Pro users get unlimited analyses + portfolio CSV upload for just £25/mo
        </p>
      </div>
    </section>
  );
}

// ============================================================================
// FAQ SECTION
// ============================================================================

function FAQSection() {
  const faqs = [
    {
      question: "How is this different from a stock screener?",
      answer: "Screeners show current P/E ratios. We show market expectations via P/E compression. Screeners are backward-looking—they tell you what the stock has done. PE Scanner is forward-looking—it reveals what the market expects to happen. That's the difference between looking in the rearview mirror and seeing what's ahead."
    },
    {
      question: "Why should I trust AI-generated headlines?",
      answer: "The headlines are viral-optimized, but the signal is pure math. When HOOD showed -113% compression, that meant the market expected a 53% earnings collapse. That's not hype—that's data. The algorithm doesn't guess; it reads market expectations from P/E ratios that Wall Street analysts set."
    },
    {
      question: "What if Yahoo Finance data is wrong?",
      answer: "We auto-correct UK stocks (pence → pounds), detect stock splits, and flag suspicious analyst estimates. Data quality is our obsession. When Netflix showed +89% compression, we caught the stock split error that Yahoo Finance missed. We validate everything before showing you a signal."
    },
    {
      question: "Can I use this for day trading?",
      answer: "Yes. Pro users get unlimited analyses—check multiple tickers, spot momentum shifts, and act fast. P/E compression reveals when market sentiment is changing, which creates volatility you can trade. Many day traders use PE Scanner to find oversold bounces or catch breakdown signals early."
    },
    {
      question: "Can I cancel anytime?",
      answer: "Yes. Cancel with one click, effective immediately. No long-term contracts, no hassle. We earn your subscription every month by delivering value—if we don't, you're free to go. Most Pro users stay because they catch opportunities that far exceed the £25/mo cost."
    },
    {
      question: "How accurate are your predictions?",
      answer: "We don't predict—we reveal market expectations. In November 2024, we flagged HOOD at -113% compression (market expected collapse). HOOD dropped 53%. We flagged BATS.L at +62% compression (market was pessimistic). It was undervalued. The accuracy comes from reading what Wall Street analysts already believe, not from guessing."
    }
  ];

  return (
    <section className="py-20 bg-slate-50">
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="text-center mb-12">
          <h2 className="font-heading text-3xl sm:text-4xl md:text-5xl font-bold text-slate-900 mb-4">
            Common Questions
          </h2>
          <p className="text-lg text-slate-600">
            Everything you need to know about PE Scanner
          </p>
        </div>

        <div className="space-y-6">
          {faqs.map((faq, index) => (
            <details
              key={index}
              className="group bg-white rounded-xl border border-slate-200 p-6 hover:border-primary/30 transition-colors"
            >
              <summary className="flex justify-between items-center cursor-pointer list-none">
                <h3 className="font-semibold text-lg text-slate-900 pr-8">
                  {faq.question}
                </h3>
                <svg
                  className="w-6 h-6 text-primary transform transition-transform group-open:rotate-180"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M19 9l-7 7-7-7"
                  />
                </svg>
              </summary>
              <div className="mt-4 text-slate-600 leading-relaxed">
                {faq.answer}
              </div>
            </details>
          ))}
        </div>

        <div className="mt-12 text-center">
          <p className="text-slate-600 mb-4">
            Still have questions?
          </p>
          <Link
            href="/contact"
            className="inline-flex items-center gap-2 text-primary hover:text-primary-dark font-medium"
          >
            Contact us
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
            </svg>
          </Link>
        </div>
      </div>
    </section>
  );
}

// ============================================================================
// FOOTER (imported from components/Footer.tsx)
// ============================================================================
