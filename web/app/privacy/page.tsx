import type { Metadata } from 'next';
import { generateLegalMetadata } from '@/lib/metadata';

export const metadata: Metadata = generateLegalMetadata('privacy');

export default function PrivacyPage() {
  return (
    <div className="min-h-screen bg-slate-50 py-20">
      <article className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Header */}
        <div className="mb-12">
          <h1 className="text-4xl font-bold text-slate-900 mb-4">Privacy Policy</h1>
          <p className="text-slate-600">
            Last updated: <time dateTime="2024-12-02">2 December 2024</time>
          </p>
        </div>

        {/* Content */}
        <div className="prose prose-slate max-w-none">
          <section className="mb-8">
            <h2 className="text-2xl font-bold text-slate-900 mb-4">Overview</h2>
            <p className="text-slate-700 leading-relaxed">
              PE Scanner (&quot;we&quot;, &quot;our&quot;, or &quot;us&quot;) is committed to protecting your privacy. 
              This Privacy Policy explains how we collect, use, and protect your information when you use 
              our stock analysis service.
            </p>
          </section>

          <section className="mb-8">
            <h2 className="text-2xl font-bold text-slate-900 mb-4">What Data We Collect</h2>
            <ul className="list-disc list-inside space-y-2 text-slate-700">
              <li><strong>Email addresses:</strong> When you sign up for portfolio analysis or Pro features</li>
              <li><strong>IP addresses:</strong> For rate limiting and abuse prevention (anonymized after 24 hours)</li>
              <li><strong>Ticker searches:</strong> Anonymous search history (no personally identifiable information)</li>
              <li><strong>Analytics data:</strong> Via Plausible Analytics (privacy-friendly, no cookies, GDPR compliant)</li>
            </ul>
          </section>

          <section className="mb-8">
            <h2 className="text-2xl font-bold text-slate-900 mb-4">How We Use Your Data</h2>
            <p className="text-slate-700 leading-relaxed mb-4">
              We use your information to:
            </p>
            <ul className="list-disc list-inside space-y-2 text-slate-700">
              <li>Send portfolio analysis reports to your email</li>
              <li>Prevent abuse and maintain service quality</li>
              <li>Improve our service based on aggregate usage patterns</li>
              <li>Communicate important updates about the service</li>
            </ul>
          </section>

          <section className="mb-8">
            <h2 className="text-2xl font-bold text-slate-900 mb-4">Data Retention</h2>
            <ul className="list-disc list-inside space-y-2 text-slate-700">
              <li><strong>Email addresses:</strong> Retained until you delete your account or unsubscribe</li>
              <li><strong>IP addresses:</strong> Anonymized after 7 days</li>
              <li><strong>Search history:</strong> Aggregate data retained for 90 days</li>
              <li><strong>Portfolio analyses:</strong> Free tier: Last 5; Pro: Last 50; Premium: Unlimited</li>
            </ul>
          </section>

          <section className="mb-8">
            <h2 className="text-2xl font-bold text-slate-900 mb-4">Third-Party Services</h2>
            <p className="text-slate-700 leading-relaxed mb-4">
              We work with the following third-party services:
            </p>
            <ul className="list-disc list-inside space-y-2 text-slate-700">
              <li><strong>Resend:</strong> Email delivery (GDPR compliant, EU servers)</li>
              <li><strong>Plausible Analytics:</strong> Privacy-friendly analytics (no cookies, EU servers)</li>
              <li><strong>Railway:</strong> Hosting provider (EU region available)</li>
              <li><strong>Vercel:</strong> Frontend hosting (global CDN with EU compliance)</li>
            </ul>
          </section>

          <section className="mb-8">
            <h2 className="text-2xl font-bold text-slate-900 mb-4">Your Rights (UK GDPR)</h2>
            <p className="text-slate-700 leading-relaxed mb-4">
              Under UK GDPR, you have the right to:
            </p>
            <ul className="list-disc list-inside space-y-2 text-slate-700">
              <li><strong>Access:</strong> Request a copy of your personal data</li>
              <li><strong>Correction:</strong> Update inaccurate or incomplete data</li>
              <li><strong>Deletion:</strong> Request deletion of your personal data</li>
              <li><strong>Export:</strong> Download your data in a portable format</li>
              <li><strong>Object:</strong> Object to processing of your data for marketing</li>
            </ul>
            <p className="text-slate-700 leading-relaxed mt-4">
              To exercise any of these rights, contact us at:{' '}
              <a href="mailto:privacy@pe-scanner.com" className="text-primary hover:underline">
                privacy@pe-scanner.com
              </a>
            </p>
          </section>

          <section className="mb-8">
            <h2 className="text-2xl font-bold text-slate-900 mb-4">Cookies</h2>
            <p className="text-slate-700 leading-relaxed">
              <strong>We do not use cookies.</strong> Plausible Analytics operates without cookies, 
              making PE Scanner fully privacy-compliant without requiring cookie consent banners.
            </p>
          </section>

          <section className="mb-8">
            <h2 className="text-2xl font-bold text-slate-900 mb-4">Data Security</h2>
            <p className="text-slate-700 leading-relaxed">
              We implement industry-standard security measures to protect your data, including:
            </p>
            <ul className="list-disc list-inside space-y-2 text-slate-700 mt-4">
              <li>Encrypted connections (HTTPS/TLS)</li>
              <li>Secure server infrastructure</li>
              <li>Regular security audits</li>
              <li>Limited data retention policies</li>
            </ul>
          </section>

          <section className="mb-8">
            <h2 className="text-2xl font-bold text-slate-900 mb-4">Changes to This Policy</h2>
            <p className="text-slate-700 leading-relaxed">
              We may update this Privacy Policy from time to time. We will notify you of any material 
              changes by email or through a notice on our website. Continued use of PE Scanner after 
              changes constitutes acceptance of the updated policy.
            </p>
          </section>

          <section className="mb-8">
            <h2 className="text-2xl font-bold text-slate-900 mb-4">Contact Us</h2>
            <p className="text-slate-700 leading-relaxed">
              For questions about this Privacy Policy or your data, contact us:
            </p>
            <div className="mt-4 p-6 bg-slate-100 rounded-lg">
              <p className="text-slate-900 font-medium">PE Scanner</p>
              <p className="text-slate-700">Email: <a href="mailto:privacy@pe-scanner.com" className="text-primary hover:underline">privacy@pe-scanner.com</a></p>
              <p className="text-slate-700">United Kingdom</p>
            </div>
          </section>
        </div>
      </article>
    </div>
  );
}

