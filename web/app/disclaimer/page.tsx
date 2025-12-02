import type { Metadata } from 'next';
import { generateLegalMetadata } from '@/lib/metadata';

export const metadata: Metadata = generateLegalMetadata('disclaimer');

export default function DisclaimerPage() {
  return (
    <div className="min-h-screen bg-slate-50 py-20">
      <article className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Header */}
        <div className="mb-12">
          <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-amber-100 border border-amber-300 mb-6">
            <span className="text-2xl">⚠️</span>
            <span className="text-sm font-semibold text-amber-900">Important Legal Notice</span>
          </div>
          <h1 className="text-4xl font-bold text-slate-900 mb-4">Investment Disclaimer</h1>
          <p className="text-slate-600">
            Last updated: <time dateTime="2024-12-02">2 December 2024</time>
          </p>
        </div>

        {/* Content */}
        <div className="prose prose-slate max-w-none">
          <section className="mb-8 bg-red-50 border-l-4 border-red-500 p-6">
            <h2 className="text-2xl font-bold text-slate-900 mb-4">Not Financial Advice</h2>
            <p className="text-slate-900 font-semibold text-lg">
              PE Scanner is NOT a registered financial adviser. Nothing on this website constitutes 
              financial advice, investment recommendations, or an endorsement to buy, sell, or hold 
              any security.
            </p>
          </section>

          <section className="mb-8">
            <h2 className="text-2xl font-bold text-slate-900 mb-4">What PE Scanner Does</h2>
            <p className="text-slate-700 leading-relaxed mb-4">
              PE Scanner is an <strong>educational and informational tool</strong> that:
            </p>
            <ul className="list-disc list-inside space-y-2 text-slate-700">
              <li>Analyzes publicly available stock data using mathematical formulas</li>
              <li>Provides P/E compression analysis and valuation metrics</li>
              <li>Generates shareable headlines and analysis summaries</li>
              <li>Helps investors screen stocks for further research</li>
            </ul>
            <p className="text-slate-700 leading-relaxed mt-4">
              PE Scanner is <strong>NOT</strong> a substitute for:
            </p>
            <ul className="list-disc list-inside space-y-2 text-slate-700 mt-2">
              <li>Professional financial advice from a qualified adviser</li>
              <li>Comprehensive fundamental analysis</li>
              <li>Due diligence and independent research</li>
              <li>Understanding your personal financial situation and risk tolerance</li>
            </ul>
          </section>

          <section className="mb-8">
            <h2 className="text-2xl font-bold text-slate-900 mb-4">Investment Risks</h2>
            <div className="space-y-4 text-slate-700">
              <p className="font-semibold text-slate-900">
                All investments carry risk. You should be aware that:
              </p>
              <ul className="list-disc list-inside space-y-2">
                <li>
                  <strong>Capital loss:</strong> The value of investments can go down as well as up. 
                  You may lose some or all of your invested capital.
                </li>
                <li>
                  <strong>Past performance:</strong> Historical returns do not guarantee future results. 
                  Previous analysis accuracy does not predict future accuracy.
                </li>
                <li>
                  <strong>Market volatility:</strong> Stock prices can fluctuate significantly due to 
                  market conditions, economic factors, and company-specific events.
                </li>
                <li>
                  <strong>Currency risk:</strong> For international investments, currency fluctuations 
                  may affect returns.
                </li>
                <li>
                  <strong>Liquidity risk:</strong> Some stocks may be difficult to sell quickly at 
                  desired prices.
                </li>
              </ul>
            </div>
          </section>

          <section className="mb-8">
            <h2 className="text-2xl font-bold text-slate-900 mb-4">Data Limitations</h2>
            <div className="space-y-4 text-slate-700">
              <p>
                PE Scanner relies on data from third-party sources, primarily Yahoo Finance. 
                Important limitations include:
              </p>
              <ul className="list-disc list-inside space-y-2">
                <li>
                  <strong>Data accuracy:</strong> Third-party data may contain errors, omissions, 
                  or delays. We cannot guarantee accuracy.
                </li>
                <li>
                  <strong>Analyst estimates:</strong> Forward P/E ratios are based on analyst 
                  estimates, which may be incorrect or outdated.
                </li>
                <li>
                  <strong>Corporate actions:</strong> Stock splits, dividends, and other events 
                  may not be immediately reflected in our data.
                </li>
                <li>
                  <strong>UK stocks:</strong> UK stock data may have specific quirks (pence vs. pounds) 
                  that our automatic corrections attempt to address but may miss.
                </li>
                <li>
                  <strong>Real-time data:</strong> Data may be delayed by up to 15 minutes or more.
                </li>
              </ul>
              <p className="mt-4 font-semibold">
                Always verify important data with official company filings and regulatory sources 
                before making investment decisions.
              </p>
            </div>
          </section>

          <section className="mb-8">
            <h2 className="text-2xl font-bold text-slate-900 mb-4">Methodology Limitations</h2>
            <div className="space-y-4 text-slate-700">
              <p>
                P/E compression analysis is one of many valuation methodologies. It has limitations:
              </p>
              <ul className="list-disc list-inside space-y-2">
                <li>
                  <strong>Not comprehensive:</strong> P/E analysis does not account for debt, 
                  cash flow, assets, competitive position, or many other factors.
                </li>
                <li>
                  <strong>Analyst bias:</strong> Forward P/E is based on analyst estimates, which 
                  may be overly optimistic or pessimistic.
                </li>
                <li>
                  <strong>Industry variation:</strong> Different industries have different normal 
                  P/E ranges, which our analysis attempts to account for but may not perfectly capture.
                </li>
                <li>
                  <strong>Market efficiency:</strong> Markets may remain irrational longer than 
                  expected. A &quot;overvalued&quot; stock may continue rising.
                </li>
                <li>
                  <strong>Special situations:</strong> Mergers, acquisitions, restructurings, and 
                  other events may make P/E analysis less relevant.
                </li>
              </ul>
            </div>
          </section>

          <section className="mb-8">
            <h2 className="text-2xl font-bold text-slate-900 mb-4">No Performance Guarantees</h2>
            <p className="text-slate-700 leading-relaxed">
              While we may showcase example analyses that predicted market movements (such as HOOD&apos;s 
              decline), these are historical examples for illustration purposes only. PE Scanner:
            </p>
            <ul className="list-disc list-inside space-y-2 text-slate-700 mt-4">
              <li>Does NOT guarantee any investment returns</li>
              <li>Does NOT promise that signals will be accurate</li>
              <li>Does NOT claim to predict future stock prices</li>
              <li>Does NOT track or verify long-term signal accuracy systematically</li>
            </ul>
            <p className="text-slate-700 leading-relaxed mt-4 font-semibold">
              Historical success does not imply future success. Every investment carries unique risks.
            </p>
          </section>

          <section className="mb-8">
            <h2 className="text-2xl font-bold text-slate-900 mb-4">Your Responsibility</h2>
            <div className="space-y-4 text-slate-700">
              <p>
                By using PE Scanner, you acknowledge that:
              </p>
              <ul className="list-disc list-inside space-y-2">
                <li>You are solely responsible for your investment decisions</li>
                <li>You should conduct independent research and due diligence</li>
                <li>You should consult with a qualified financial adviser before investing</li>
                <li>You understand the risks involved in stock market investing</li>
                <li>You accept full responsibility for any losses incurred</li>
              </ul>
            </div>
          </section>

          <section className="mb-8">
            <h2 className="text-2xl font-bold text-slate-900 mb-4">Jurisdiction-Specific Warnings</h2>
            <div className="space-y-4 text-slate-700">
              <p className="font-semibold text-slate-900">United Kingdom:</p>
              <ul className="list-disc list-inside space-y-2">
                <li>
                  PE Scanner is not authorized or regulated by the Financial Conduct Authority (FCA)
                </li>
                <li>
                  We do not provide regulated investment advice as defined by UK law
                </li>
                <li>
                  For regulated advice, consult an FCA-authorized financial adviser
                </li>
              </ul>
              <p className="font-semibold text-slate-900 mt-4">United States:</p>
              <ul className="list-disc list-inside space-y-2">
                <li>
                  PE Scanner is not a registered investment adviser with the SEC
                </li>
                <li>
                  We do not provide investment advice as defined by US securities laws
                </li>
                <li>
                  For regulated advice, consult an SEC-registered investment adviser
                </li>
              </ul>
            </div>
          </section>

          <section className="mb-8">
            <h2 className="text-2xl font-bold text-slate-900 mb-4">How to Use PE Scanner Responsibly</h2>
            <div className="bg-slate-100 p-6 rounded-lg space-y-4 text-slate-700">
              <p className="font-semibold text-slate-900">
                PE Scanner is best used as a starting point for further research:
              </p>
              <ol className="list-decimal list-inside space-y-2">
                <li>Use PE Scanner to screen stocks and identify potential opportunities or risks</li>
                <li>Verify all data with official company filings (10-K, annual reports, etc.)</li>
                <li>Conduct comprehensive fundamental analysis</li>
                <li>Consider your personal financial situation and risk tolerance</li>
                <li>Diversify your portfolio to manage risk</li>
                <li>Consult with a qualified financial adviser before making significant decisions</li>
                <li>Never invest more than you can afford to lose</li>
              </ol>
            </div>
          </section>

          <section className="mb-8">
            <h2 className="text-2xl font-bold text-slate-900 mb-4">Questions or Concerns?</h2>
            <p className="text-slate-700 leading-relaxed">
              If you have questions about this disclaimer or how to use PE Scanner responsibly, contact us:
            </p>
            <div className="mt-4 p-6 bg-slate-100 rounded-lg">
              <p className="text-slate-900 font-medium">PE Scanner</p>
              <p className="text-slate-700">Email: <a href="mailto:legal@pe-scanner.com" className="text-primary hover:underline">legal@pe-scanner.com</a></p>
              <p className="text-slate-700">United Kingdom</p>
            </div>
          </section>
        </div>
      </article>
    </div>
  );
}

