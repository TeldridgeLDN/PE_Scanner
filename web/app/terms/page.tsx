import type { Metadata } from 'next';
import { generateLegalMetadata } from '@/lib/metadata';

export const metadata: Metadata = generateLegalMetadata('terms');

export default function TermsPage() {
  return (
    <div className="min-h-screen bg-slate-50 py-20">
      <article className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Header */}
        <div className="mb-12">
          <h1 className="text-4xl font-bold text-slate-900 mb-4">Terms of Service</h1>
          <p className="text-slate-600">
            Last updated: <time dateTime="2024-12-02">2 December 2024</time>
          </p>
        </div>

        {/* Content */}
        <div className="prose prose-slate max-w-none">
          <section className="mb-8">
            <h2 className="text-2xl font-bold text-slate-900 mb-4">Acceptance of Terms</h2>
            <p className="text-slate-700 leading-relaxed">
              By accessing or using PE Scanner (&quot;the Service&quot;), you agree to be bound by these 
              Terms of Service (&quot;Terms&quot;). If you do not agree to these Terms, please do not use the Service.
            </p>
          </section>

          <section className="mb-8">
            <h2 className="text-2xl font-bold text-slate-900 mb-4">Service Description</h2>
            <p className="text-slate-700 leading-relaxed">
              PE Scanner is a stock analysis tool that provides P/E compression analysis, valuation metrics, 
              and shareable investment insights. The Service is designed for informational and educational 
              purposes only.
            </p>
          </section>

          <section className="mb-8">
            <h2 className="text-2xl font-bold text-slate-900 mb-4">Acceptable Use</h2>
            <p className="text-slate-700 leading-relaxed mb-4">
              You agree to use PE Scanner:
            </p>
            <ul className="list-disc list-inside space-y-2 text-slate-700">
              <li>For personal investment research and educational purposes</li>
              <li>In compliance with all applicable laws and regulations</li>
              <li>Without attempting to circumvent rate limits or security measures</li>
              <li>Without scraping, copying, or reselling our data or analysis</li>
            </ul>
          </section>

          <section className="mb-8">
            <h2 className="text-2xl font-bold text-slate-900 mb-4">Prohibited Use</h2>
            <p className="text-slate-700 leading-relaxed mb-4">
              You must NOT:
            </p>
            <ul className="list-disc list-inside space-y-2 text-slate-700">
              <li>Use automated tools to scrape or extract data from PE Scanner</li>
              <li>Resell, redistribute, or commercialize our analysis or data</li>
              <li>Attempt to reverse engineer or access our systems unauthorizedly</li>
              <li>Violate rate limits or attempt to abuse the service</li>
              <li>Use the Service for any illegal or harmful purposes</li>
            </ul>
          </section>

          <section className="mb-8 bg-amber-50 border-l-4 border-amber-500 p-6">
            <h2 className="text-2xl font-bold text-slate-900 mb-4">⚠️ Investment Disclaimer</h2>
            <div className="space-y-4 text-slate-700">
              <p className="font-semibold">
                PE Scanner is NOT financial advice. We are NOT registered financial advisers.
              </p>
              <p>
                All analysis, signals, and recommendations provided by PE Scanner are for informational 
                and educational purposes only. They do not constitute investment advice, recommendations, 
                or endorsements.
              </p>
              <p>
                <strong>Key points:</strong>
              </p>
              <ul className="list-disc list-inside space-y-2 mt-2">
                <li>Past performance does not guarantee future results</li>
                <li>Stock prices can go down as well as up</li>
                <li>You may lose some or all of your invested capital</li>
                <li>Data from Yahoo Finance may contain errors or be outdated</li>
                <li>Our analysis is a screening tool, not a sole decision factor</li>
              </ul>
              <p className="font-semibold">
                Always conduct your own research and consult with a qualified financial adviser 
                before making investment decisions.
              </p>
            </div>
          </section>

          <section className="mb-8">
            <h2 className="text-2xl font-bold text-slate-900 mb-4">Account Terms</h2>
            <div className="space-y-4 text-slate-700">
              <div>
                <h3 className="font-semibold text-slate-900 mb-2">Free Tier</h3>
                <ul className="list-disc list-inside space-y-1">
                  <li>10 ticker analyses per day (with email signup)</li>
                  <li>3 ticker analyses per day (anonymous, IP-based)</li>
                  <li>Basic analysis features</li>
                  <li>No portfolio uploads</li>
                </ul>
              </div>
              <div>
                <h3 className="font-semibold text-slate-900 mb-2">Pro Tier (£25/month)</h3>
                <ul className="list-disc list-inside space-y-1">
                  <li>Unlimited ticker analyses</li>
                  <li>Portfolio CSV uploads (up to 100 positions)</li>
                  <li>Email portfolio reports</li>
                  <li>Priority support</li>
                </ul>
              </div>
              <div>
                <h3 className="font-semibold text-slate-900 mb-2">Premium Tier (£49/month)</h3>
                <ul className="list-disc list-inside space-y-1">
                  <li>All Pro features</li>
                  <li>API access for automated analysis</li>
                  <li>Webhook notifications</li>
                  <li>Dedicated support</li>
                </ul>
              </div>
            </div>
          </section>

          <section className="mb-8">
            <h2 className="text-2xl font-bold text-slate-900 mb-4">Payment & Refunds</h2>
            <div className="space-y-4 text-slate-700">
              <p>
                <strong>Billing:</strong> Subscriptions are billed monthly or annually in British Pounds (GBP). 
                Annual subscriptions receive a 20% discount.
              </p>
              <p>
                <strong>Cancellation:</strong> You may cancel your subscription at any time. Cancellation 
                takes effect at the end of the current billing period. No partial refunds are provided 
                for monthly subscriptions.
              </p>
              <p>
                <strong>Refunds:</strong> Annual subscriptions may receive a pro-rata refund if cancelled 
                within the first 30 days. After 30 days, no refunds are provided for annual subscriptions.
              </p>
              <p>
                <strong>Price Changes:</strong> We reserve the right to change subscription prices with 
                30 days&apos; notice. Existing subscribers will be notified via email before any price changes.
              </p>
            </div>
          </section>

          <section className="mb-8">
            <h2 className="text-2xl font-bold text-slate-900 mb-4">Data Accuracy</h2>
            <p className="text-slate-700 leading-relaxed">
              PE Scanner sources data from Yahoo Finance and other third-party providers. While we strive 
              for accuracy, we cannot guarantee that all data is error-free, complete, or up-to-date. 
              Data quality issues may exist, particularly for UK stocks and recent corporate actions 
              (splits, dividends, etc.).
            </p>
          </section>

          <section className="mb-8">
            <h2 className="text-2xl font-bold text-slate-900 mb-4">Limitation of Liability</h2>
            <div className="space-y-4 text-slate-700">
              <p>
                To the fullest extent permitted by law:
              </p>
              <ul className="list-disc list-inside space-y-2">
                <li>
                  PE Scanner is provided &quot;as-is&quot; without warranties of any kind, express or implied
                </li>
                <li>
                  We are NOT liable for any investment losses, damages, or financial harm resulting 
                  from use of the Service
                </li>
                <li>
                  We are NOT responsible for data errors, outages, or service interruptions
                </li>
                <li>
                  Our total liability to you for all claims shall not exceed the amount you paid us 
                  in the 12 months before the claim
                </li>
              </ul>
            </div>
          </section>

          <section className="mb-8">
            <h2 className="text-2xl font-bold text-slate-900 mb-4">Intellectual Property</h2>
            <p className="text-slate-700 leading-relaxed">
              PE Scanner and its original content, features, and functionality are owned by PE Scanner 
              and are protected by international copyright, trademark, and other intellectual property laws. 
              You may not copy, modify, or create derivative works without explicit written permission.
            </p>
          </section>

          <section className="mb-8">
            <h2 className="text-2xl font-bold text-slate-900 mb-4">Termination</h2>
            <p className="text-slate-700 leading-relaxed">
              We reserve the right to suspend or terminate your access to PE Scanner at any time, without 
              notice, for conduct that we believe violates these Terms or is harmful to other users, us, 
              or third parties, or for any other reason at our sole discretion.
            </p>
          </section>

          <section className="mb-8">
            <h2 className="text-2xl font-bold text-slate-900 mb-4">Governing Law</h2>
            <p className="text-slate-700 leading-relaxed">
              These Terms shall be governed by and construed in accordance with the laws of England and Wales. 
              Any disputes arising from these Terms or your use of PE Scanner shall be subject to the 
              exclusive jurisdiction of the courts of England and Wales.
            </p>
          </section>

          <section className="mb-8">
            <h2 className="text-2xl font-bold text-slate-900 mb-4">Changes to Terms</h2>
            <p className="text-slate-700 leading-relaxed">
              We reserve the right to modify these Terms at any time. We will notify users of material 
              changes via email or through a prominent notice on the Service. Continued use of PE Scanner 
              after changes constitutes acceptance of the modified Terms.
            </p>
          </section>

          <section className="mb-8">
            <h2 className="text-2xl font-bold text-slate-900 mb-4">Contact Us</h2>
            <p className="text-slate-700 leading-relaxed">
              For questions about these Terms of Service, contact us:
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

