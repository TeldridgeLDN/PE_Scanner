# PE Scanner Free Web Tool - Launch Strategy & Implementation Plan

**Date:** 2025-12-02  
**Based On:** PE_Scanner_Free_Tool_Launch_Strategy.md + Pirouette patterns  
**Status:** Planning → Ready for Task Master

---

## Executive Summary

This document bridges the gap between **PE Scanner's current CLI-only implementation** and the **Free Web Tool Launch Strategy**. It provides detailed implementation guidance based on proven patterns from the **Pirouette** sibling project.

### Current State vs. Target State

| Component | Current (CLI) | Target (Web Launch) | Pattern Source |
|-----------|---------------|---------------------|----------------|
| **Interface** | CLI only | Web landing page | Pirouette `page.tsx` |
| **Analysis Trigger** | `pe-scanner analyze` | URL form submission | `HeroAnalyzeForm.tsx` |
| **Results Display** | Terminal output | Browser UI with headlines | Pirouette report pages |
| **Email Capture** | ❌ None | ConvertKit/Resend integration | `src/lib/email/resend.ts` |
| **Analytics** | ❌ None | Plausible Analytics | `src/lib/analytics/plausible.ts` |
| **Hosting** | Local only | Railway (API) + Vercel (Frontend) | Pirouette deployment |
| **Authentication** | ❌ None | Optional (Clerk for portfolio uploads) | Pirouette Clerk integration |

---

## Architecture Overview

### Recommended Stack (Based on Pirouette)

```
┌─────────────────────────────────────────────────────────────┐
│                    FRONTEND (Vercel)                         │
│  Next.js 15 + Tailwind CSS + TypeScript                     │
│  - Landing page (pe-scanner.com)                            │
│  - Analysis results display                                 │
│  - Email capture modal                                      │
│  - Portfolio upload (auth-gated)                            │
└────────────────┬────────────────────────────────────────────┘
                 │
                 │ HTTPS API Calls
                 ▼
┌─────────────────────────────────────────────────────────────┐
│                    BACKEND (Railway)                         │
│  Flask Python API (existing PE Scanner code)                │
│  - GET /api/analyze/<ticker>                                │
│  - POST /api/portfolio                                      │
│  - POST /api/subscribe (email capture)                     │
└────────────────┬────────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────────┐
│               SUPPORTING SERVICES                            │
│  - Resend (email delivery)                                  │
│  - Plausible Analytics (privacy-friendly)                   │
│  - Supabase (optional: user data, saved analyses)           │
│  - Clerk (optional: authentication for portfolio uploads)   │
└─────────────────────────────────────────────────────────────┘
```

---

## Gap Analysis with Pirouette Patterns

### ✅ **What PE Scanner Has (Ready to Expose)**

1. **Backend Analysis Engine** (Tasks 1-25 complete)
   - Tiered analysis (VALUE/GROWTH/HYPER_GROWTH)
   - Headline generation (`headlines.py`)
   - Anchoring engine (`anchoring.py`)
   - Share URL generation
   - API v2.0 endpoint (`GET /api/analyze/<ticker>`)

2. **Core Business Logic**
   - Data fetching (Yahoo Finance)
   - P/E compression calculations
   - Data quality validation
   - Fair value scenarios
   - Portfolio analysis

### ❌ **What PE Scanner Needs (From Pirouette Patterns)**

#### 1. Frontend Components (Pirouette → PE Scanner Mapping)

| Pirouette Component | PE Scanner Equivalent | Purpose |
|---------------------|----------------------|---------|
| `HeroAnalyzeForm.tsx` | `TickerSearchForm.tsx` | Main ticker input with "Analyze" button |
| `page.tsx` (landing) | `app/page.tsx` | Marketing landing page with hero + pricing |
| `report/[id]/page.tsx` | `report/[ticker]/page.tsx` | Analysis results display with headlines |
| `EmailCaptureModal.tsx` | `PortfolioGateModal.tsx` | Email gate for portfolio CSV upload |
| `Navigation.tsx` | `Navigation.tsx` | Nav bar with optional auth state |
| `ScrollTracker.tsx` | `ScrollTracker.tsx` | Analytics scroll depth tracking |

#### 2. Email Integration (Resend Pattern)

**Pirouette Pattern:**
```typescript
// src/lib/email/resend.ts
const EMAIL_CONFIG = {
  from: {
    default: 'Pirouette <hello@pirouette.app>',
    noreply: 'Pirouette <noreply@pirouette.app>',
  },
  replyTo: 'support@pirouette.app',
};

export async function sendEmail(options: SendEmailOptions): Promise<SendEmailResult> {
  const { data, error } = await resend.emails.send({
    from: options.from || EMAIL_CONFIG.from.default,
    to: options.to,
    subject: options.subject,
    react: options.react, // React Email component
  });
  // ...
}
```

**PE Scanner Adaptation:**
```typescript
// src/lib/email/resend.ts (NEW FILE)
const EMAIL_CONFIG = {
  from: {
    default: 'PE Scanner <hello@pe-scanner.com>',
    noreply: 'PE Scanner <noreply@pe-scanner.com>',
  },
};

// Email templates:
// - WelcomeEmail.tsx (after email capture)
// - PortfolioReportEmail.tsx (portfolio analysis results)
```

**Environment Variables Needed:**
```bash
RESEND_API_KEY=re_xxxxx  # Get from resend.com
NEXT_PUBLIC_APP_URL=https://pe-scanner.com
```

#### 3. Analytics Integration (Plausible Pattern)

**Pirouette Pattern:**
```typescript
// src/lib/analytics/plausible.ts
export type PlausibleEvent =
  | 'Analysis_Submitted'
  | 'Analysis_Completed'
  | 'Signup_Started'
  | 'PDF_Downloaded';

export function trackEvent(
  eventName: PlausibleEvent,
  eventProps?: { props?: Record<string, string | number> }
) {
  if (typeof window === 'undefined') return;
  const plausible = (window as any).plausible;
  if (!plausible) return;
  plausible(eventName, eventProps);
}

// Convenience functions
export function trackAnalysisSubmitted(source: 'hero' | 'dashboard') {
  trackEvent('Analysis_Submitted', { props: { source } });
}
```

**PE Scanner Adaptation:**
```typescript
// src/lib/analytics/plausible.ts (NEW FILE)
export type PlausibleEvent =
  | 'Ticker_Analyzed'         // User searches ticker
  | 'Headline_Shared'         // User clicks share button
  | 'Email_Captured'          // User submits email
  | 'Portfolio_Uploaded'      // User uploads CSV
  | 'Portfolio_Report_Viewed' // User views portfolio report
  | 'Scroll_Depth_50'
  | 'Scroll_Depth_100';

export function trackTickerAnalysis(ticker: string, signal: 'BUY' | 'SELL' | 'HOLD') {
  trackEvent('Ticker_Analyzed', { 
    props: { ticker, signal } 
  });
}
```

**Plausible Setup:**
```bash
# .env.local
NEXT_PUBLIC_PLAUSIBLE_DOMAIN=pe-scanner.com

# In src/app/layout.tsx, add:
<Script
  defer
  data-domain={process.env.NEXT_PUBLIC_PLAUSIBLE_DOMAIN}
  src="https://plausible.io/js/script.js"
/>
```

**Cost:** £9/month (10k pageviews)

#### 4. Deployment Configuration

**Railway (Backend API)**

Pirouette uses Railway for the Python analysis worker. PE Scanner should use the same pattern.

**New Files Needed:**
```
pe-scanner/
├── railway/
│   ├── Dockerfile           # Python Flask container
│   ├── railway.json         # Railway config
│   └── requirements.txt     # Python deps
└── Procfile                 # Railway start command
```

**Dockerfile Example (adapted from Pirouette):**
```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY src/ ./src/

# Expose port
EXPOSE 8000

# Start Flask app
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "src.pe_scanner.api.app:app"]
```

**railway.json:**
```json
{
  "$schema": "https://railway.app/railway.schema.json",
  "build": {
    "builder": "DOCKERFILE",
    "dockerfilePath": "railway/Dockerfile"
  },
  "deploy": {
    "startCommand": "gunicorn --bind 0.0.0.0:$PORT src.pe_scanner.api.app:app",
    "healthcheckPath": "/health",
    "restartPolicyType": "ON_FAILURE"
  }
}
```

**Environment Variables (Railway Dashboard):**
```bash
FLASK_ENV=production
YAHOO_FINANCE_RATE_LIMIT=0.2
MAX_TICKERS_PER_REQUEST=50
RESEND_API_KEY=re_xxxxx
ALLOWED_ORIGINS=https://pe-scanner.com,https://www.pe-scanner.com
```

**Vercel (Frontend)**

**New Files Needed:**
```
pe-scanner-web/        # New Next.js project
├── src/
│   ├── app/
│   │   ├── page.tsx           # Landing page
│   │   ├── report/
│   │   │   └── [ticker]/
│   │   │       └── page.tsx   # Results page
│   │   └── api/
│   │       ├── analyze/
│   │       │   └── route.ts   # Proxy to Railway
│   │       └── subscribe/
│   │           └── route.ts   # Email capture
│   ├── components/
│   │   ├── TickerSearchForm.tsx
│   │   ├── ResultsDisplay.tsx
│   │   ├── PortfolioGateModal.tsx
│   │   └── ShareButtons.tsx
│   └── lib/
│       ├── analytics/
│       │   └── plausible.ts
│       └── email/
│           └── resend.ts
├── public/
├── tailwind.config.ts
├── next.config.js
└── vercel.json
```

**vercel.json:**
```json
{
  "env": {
    "NEXT_PUBLIC_API_URL": "https://pe-scanner-api.railway.app",
    "NEXT_PUBLIC_PLAUSIBLE_DOMAIN": "pe-scanner.com"
  },
  "headers": [
    {
      "source": "/(.*)",
      "headers": [
        {
          "key": "X-Frame-Options",
          "value": "DENY"
        }
      ]
    }
  ]
}
```

#### 5. Landing Page Structure (Pirouette Pattern)

**Sections (from Pirouette `page.tsx`):**

1. **Hero Section**
   - Headline: "Is Your Stock Overpriced? Find Out in 30 Seconds"
   - Subheadline: Trust indicators
   - **Ticker Input Form** (no signup required)
   - Trust badges: "No signup required • Results in 30 seconds"

2. **Benchmark Proof Bar**
   - "Analyzed 10,000+ stocks in November 2024"
   - Show example tickers with signals (HOOD -113% → SELL, BATS +62% → BUY)

3. **How It Works** (3 steps)
   - Step 1: Enter Ticker
   - Step 2: AI Analysis (tiered: VALUE/GROWTH/HYPER_GROWTH)
   - Step 3: Get Shareable Headline + Anchor

4. **Features Grid**
   - P/E Compression Analysis
   - Growth Stock (PEG) Analysis
   - Hyper-Growth (P/S + Rule of 40)
   - Shareable Headlines
   - Anchoring Context
   - Fair Value Scenarios
   - Data Quality Validation

5. **Pricing Section**
   - **Free Plan:** 3 tickers/day, basic results
   - **Pro Plan:** £20/mo, unlimited tickers, portfolio CSV upload, email reports
   - **Agency Plan:** £100/mo (future)

6. **Example Results Section**
   - Show real examples: HOOD (SELL), META (BUY), BATS.L (BUY)
   - Display headlines in Twitter-card style

7. **Final CTA**
   - "Ready to Scan Your Portfolio?"
   - Email capture for portfolio upload

**Key Differences from Pirouette:**
- Pirouette: URL input → Waiting page → Report
- PE Scanner: Ticker input → **Instant results** (cached, fast API)

---

## Email Capture Strategy

### Trigger Points (From Launch PRD)

1. **Primary Trigger:** Portfolio Batch Upload
   - User wants to analyze entire ISA/SIPP CSV
   - Gate this behind email capture
   - Modal: "Upload your portfolio (requires free account)"

2. **Secondary Trigger:** Save Results
   - User wants to save/bookmark a ticker analysis
   - Optional: "Save this analysis for later (free account)"

3. **Newsletter Signup (Future):**
   - "The Regime Report" - weekly top opportunities
   - £20/mo paid newsletter (separate from tool)

### Email Service: Resend (Pirouette Pattern)

**Why Resend (vs. ConvertKit/Buttondown from PRD):**
- ✅ Used successfully in Pirouette
- ✅ Transactional + marketing emails
- ✅ React Email templates (beautiful, maintainable)
- ✅ Free tier: 3,000 emails/month (sufficient for launch)
- ✅ £20/mo after free tier

**Email Templates Needed:**

```typescript
// src/lib/email/templates/
├── WelcomeEmail.tsx              // After email capture
├── PortfolioReportEmail.tsx      // Portfolio analysis complete
└── BaseEmail.tsx                 // Layout wrapper
```

**Example: WelcomeEmail.tsx**
```tsx
import { BaseEmail } from './BaseEmail';

export default function WelcomeEmail({ name }: { name: string }) {
  return (
    <BaseEmail>
      <h1>Welcome to PE Scanner! 🎯</h1>
      <p>Hi {name},</p>
      <p>
        Thanks for signing up! You can now upload your portfolio CSV 
        for instant P/E compression analysis.
      </p>
      <a href="https://pe-scanner.com/dashboard">
        Analyze Your Portfolio →
      </a>
    </BaseEmail>
  );
}
```

---

## Social Sharing Implementation

### Share Button Component (New)

```tsx
// src/components/ShareButtons.tsx
'use client';

import { trackEvent } from '@/lib/analytics';

interface ShareButtonsProps {
  ticker: string;
  headline: string;
  twitterUrl: string;
  linkedinUrl: string;
  copyText: string;
}

export function ShareButtons({ 
  ticker, 
  headline, 
  twitterUrl, 
  linkedinUrl,
  copyText 
}: ShareButtonsProps) {
  
  const handleShare = (platform: 'twitter' | 'linkedin' | 'copy') => {
    trackEvent('Headline_Shared', { 
      props: { ticker, platform } 
    });
    
    if (platform === 'copy') {
      navigator.clipboard.writeText(copyText);
      // Show toast: "Copied to clipboard!"
    }
  };

  return (
    <div className="flex gap-3">
      <a
        href={twitterUrl}
        target="_blank"
        rel="noopener noreferrer"
        onClick={() => handleShare('twitter')}
        className="btn btn-twitter"
      >
        Share on Twitter
      </a>
      <a
        href={linkedinUrl}
        target="_blank"
        rel="noopener noreferrer"
        onClick={() => handleShare('linkedin')}
        className="btn btn-linkedin"
      >
        Share on LinkedIn
      </a>
      <button
        onClick={() => handleShare('copy')}
        className="btn btn-secondary"
      >
        Copy Link
      </button>
    </div>
  );
}
```

**Usage in Results Page:**
```tsx
// src/app/report/[ticker]/page.tsx
import { ShareButtons } from '@/components/ShareButtons';

export default async function ReportPage({ params }: { params: { ticker: string } }) {
  const analysis = await fetchAnalysis(params.ticker);
  
  return (
    <div>
      <h1 className="headline">{analysis.headline}</h1>
      <p className="anchor">{analysis.anchor}</p>
      
      <ShareButtons
        ticker={params.ticker}
        headline={analysis.headline}
        twitterUrl={analysis.share_urls.twitter}
        linkedinUrl={analysis.share_urls.linkedin}
        copyText={analysis.share_urls.copy_text}
      />
    </div>
  );
}
```

---

## Domain & DNS Setup

### Domain Options (From Launch PRD)
1. **pe-scanner.com** (Recommended - clear, memorable)
2. **pescan.app** (Shorter, modern .app TLD)
3. **compressioncheck.com** (Descriptive but long)

### DNS Configuration (Namecheap/Cloudflare)

**For Vercel (Frontend):**
```
Type: CNAME
Name: @
Value: cname.vercel-dns.com
```

**For Railway (API Subdomain):**
```
Type: CNAME
Name: api
Value: xxx.railway.app
```

**Result:**
- Frontend: `https://pe-scanner.com`
- API: `https://api.pe-scanner.com`

**SSL:** Automatic via Vercel and Railway

---

## Cost Breakdown (Month 1)

| Service | Purpose | Cost |
|---------|---------|------|
| **Domain** | pe-scanner.com | £10/year (£0.83/mo) |
| **Vercel** | Frontend hosting | £0 (Hobby plan) |
| **Railway** | Backend API | £5/mo (500 hrs) |
| **Resend** | Email delivery | £0 (3k emails) |
| **Plausible** | Analytics | £9/mo (10k pageviews) |
| **Supabase** | Database (optional) | £0 (Free tier) |
| **Total** | | **£14.83/mo** |

**Break-even:** 1 customer at £20/mo

---

## Next Steps: Task Master Implementation Plan

### Recommended Phase Approach

#### **Phase 1: Minimum Viable Web Tool (Week 1-2)**
**Goal:** Get a basic web interface working with existing API

**Tasks to Create:**
1. Initialize Next.js 15 project with Tailwind CSS
2. Create landing page with hero section
3. Build TickerSearchForm component
4. Create results display page
5. Integrate with existing Flask API v2.0
6. Deploy to Vercel (frontend) + Railway (backend)
7. Set up custom domain

**Deliverable:** Live site at `pe-scanner.com` with single-ticker analysis

---

#### **Phase 2: Email Capture & Portfolio Upload (Week 3)**
**Goal:** Add lead generation and portfolio batch analysis

**Tasks to Create:**
8. Integrate Resend email service
9. Build email capture modal
10. Create authentication (Clerk) for portfolio uploads
11. Build portfolio upload interface
12. Create portfolio results page
13. Send portfolio report emails

**Deliverable:** Email-gated portfolio CSV upload feature

---

#### **Phase 3: Analytics & Social (Week 4)**
**Goal:** Add tracking and viral sharing features

**Tasks to Create:**
14. Integrate Plausible Analytics
15. Implement scroll depth tracking
16. Build ShareButtons component
17. Add TrackableButton for CTAs
18. Create social share preview cards (Open Graph)

**Deliverable:** Full tracking and social sharing

---

#### **Phase 4: Marketing & Launch (Week 5-6)**
**Goal:** Prepare for public launch

**Tasks to Create:**
19. Write launch blog post
20. Create Product Hunt submission materials
21. Prepare Reddit posts (r/UKInvesting, r/StockMarket)
22. Create Twitter thread templates
23. Set up LinkedIn post
24. Prepare email sequence for early users

**Deliverable:** Launch kit ready for go-live

---

## Technical Decisions Summary

### Confirmed Tech Stack

| Layer | Technology | Rationale |
|-------|------------|-----------|
| **Frontend** | Next.js 15 + Vercel | Proven in Pirouette, fast deploys |
| **Backend** | Flask + Railway | Existing PE Scanner code, easy migration |
| **Styling** | Tailwind CSS | Pirouette pattern, fast iteration |
| **Email** | Resend | Proven in Pirouette, React templates |
| **Analytics** | Plausible | Privacy-friendly, GDPR compliant |
| **Auth** | Clerk (optional) | Pirouette pattern, easy setup |
| **Database** | Supabase (optional) | For saved analyses, user data |

### Key Files to Create (Summary)

**Frontend (New Project):**
```
pe-scanner-web/
├── src/app/
│   ├── page.tsx                      # Landing page
│   ├── report/[ticker]/page.tsx      # Results display
│   ├── portfolio/page.tsx            # Portfolio upload
│   └── api/
│       ├── analyze/route.ts          # API proxy
│       └── subscribe/route.ts        # Email capture
├── src/components/
│   ├── TickerSearchForm.tsx
│   ├── ResultsDisplay.tsx
│   ├── ShareButtons.tsx
│   ├── PortfolioGateModal.tsx
│   └── ScrollTracker.tsx
├── src/lib/
│   ├── analytics/plausible.ts
│   └── email/resend.ts
└── tailwind.config.ts
```

**Backend (Enhance Existing):**
```
PE_Scanner/
├── railway/
│   ├── Dockerfile
│   └── railway.json
├── src/pe_scanner/api/
│   ├── app.py                        # ✅ Already exists
│   └── routes.py                     # Add email capture endpoint
└── Procfile
```

---

## Reference Links

### Pirouette Patterns Used
- Landing page structure: `/Users/tomeldridge/pirouette/src/app/page.tsx`
- Hero form: `/Users/tomeldridge/pirouette/src/components/HeroAnalyzeForm.tsx`
- Analytics: `/Users/tomeldridge/pirouette/src/lib/analytics/plausible.ts`
- Email: `/Users/tomeldridge/pirouette/src/lib/email/resend.ts`
- Deployment: `/Users/tomeldridge/pirouette/railway/`

### External Resources
- **Resend Docs:** https://resend.com/docs
- **Plausible Docs:** https://plausible.io/docs
- **Railway Docs:** https://docs.railway.app/
- **Vercel Docs:** https://vercel.com/docs
- **Next.js 15 Docs:** https://nextjs.org/docs

---

**Status:** Ready for Task Master task generation  
**Next Action:** Create detailed Task Master tasks for Phase 1-4  
**Owner:** PE Scanner Development Team

