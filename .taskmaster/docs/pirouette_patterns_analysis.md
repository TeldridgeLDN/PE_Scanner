# Pirouette Patterns Deep Dive for PE Scanner

**Date:** 2025-12-02  
**Purpose:** Address three critical questions before creating Task Master tasks  
**Status:** Analysis Complete → Ready for Task Creation

---

## 📚 **Question 1: Claude Skills, Workflows & Agents from Pirouette**

### **What Pirouette Has Developed**

Pirouette created a **"Skills Library"** (documented in `SKILLS_IMPORT_PLAN.md` and `ORCHESTRATOR_INTEGRATION.md`) that should be transferred to PE Scanner:

| Skill Name | Location | Relevance to PE Scanner | Priority |
|------------|----------|-------------------------|----------|
| **project-scaffolder** | `.cursor/skills/project-scaffolder.md` | Setup new Next.js projects quickly | 🟢 **HIGH** |
| **skill-import-assistant** | `.cursor/skills/skill-import-assistant.md` | Import code patterns between projects | 🟢 **HIGH** |
| **prd-progress-tracker** | `.cursor/skills/prd-progress-tracker.md` | Track alignment with launch PRD | 🟡 MEDIUM |
| **email-touchpoint-mapper** | `.cursor/skills/email-touchpoint-mapper.md` | Plan email sequences for user journey | 🟡 MEDIUM |
| **scaling-calculator** | `.cursor/skills/scaling-calculator.md` | Cost modeling and breakeven analysis | 🟢 **HIGH** |

### **Key Pirouette Workflows Applicable to PE Scanner**

#### 1. **Rate Limiting & Abuse Prevention Workflow**

**Source:** `src/lib/rate-limit.ts` (426 lines)

**What Pirouette Does:**
```typescript
// Three-tier rate limiting system:
// 1. Anonymous users: 1 analysis/day per IP
// 2. Free users: 3 analyses/week
// 3. Pro users: Unlimited

export async function checkAnonymousRateLimit(ip: string): Promise<AnonymousRateLimitResult> {
  const recentCount = await countAnonymousAnalyses(ip);
  const remaining = Math.max(0, ANONYMOUS_RATE_LIMIT - recentCount);
  
  return {
    allowed: remaining > 0,
    remaining,
    resetAt: new Date(Date.now() + 24 * 60 * 60 * 1000), // 24h window
    suggestSignup: remaining === 0,
    message: remaining === 0
      ? "You've used your free analysis today. Create a free account for 3 analyses per week!"
      : undefined,
  };
}
```

**How to Apply to PE Scanner:**

```python
# src/pe_scanner/api/rate_limit.py (NEW FILE - adapt from Pirouette)

from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Optional
import redis

@dataclass
class RateLimitResult:
    allowed: bool
    remaining: int
    reset_at: Optional[datetime]
    message: Optional[str]
    suggest_signup: bool = False

# Rate limit tiers for PE Scanner
RATE_LIMITS = {
    'anonymous': 3,      # 3 tickers/day per IP (generous for testing)
    'free': 10,          # 10 tickers/day (signup required)
    'pro': -1,           # Unlimited
}

def check_anonymous_rate_limit(ip_address: str, redis_client) -> RateLimitResult:
    """
    Rate limit anonymous ticker searches by IP address.
    Uses Redis for distributed rate limiting (Railway compatible).
    """
    key = f"ratelimit:anon:{ip_address}"
    window_seconds = 86400  # 24 hours
    
    # Get current count
    count = redis_client.get(key)
    count = int(count) if count else 0
    
    if count >= RATE_LIMITS['anonymous']:
        # Get TTL for reset time
        ttl = redis_client.ttl(key)
        reset_at = datetime.now() + timedelta(seconds=ttl)
        
        return RateLimitResult(
            allowed=False,
            remaining=0,
            reset_at=reset_at,
            message=f"You've analyzed {count} tickers today. Create a free account for 10/day!",
            suggest_signup=True
        )
    
    # Increment counter (set expiry if new)
    pipeline = redis_client.pipeline()
    pipeline.incr(key)
    if count == 0:
        pipeline.expire(key, window_seconds)
    pipeline.execute()
    
    remaining = RATE_LIMITS['anonymous'] - (count + 1)
    return RateLimitResult(
        allowed=True,
        remaining=remaining,
        reset_at=None,
        message=None,
        suggest_signup=False
    )
```

**Database Setup (Supabase - Optional):**

```sql
-- Migration: anonymous_ticker_searches.sql
CREATE TABLE anonymous_ticker_searches (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  ip_address TEXT NOT NULL,
  ticker TEXT NOT NULL,
  searched_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  user_agent TEXT
);

-- Index for rate limiting queries
CREATE INDEX idx_anon_searches_ip_date 
  ON anonymous_ticker_searches(ip_address, searched_at DESC);

-- Auto-cleanup old data (7 days)
CREATE OR REPLACE FUNCTION cleanup_old_searches()
RETURNS void AS $$
BEGIN
  DELETE FROM anonymous_ticker_searches 
  WHERE searched_at < NOW() - INTERVAL '7 days';
END;
$$ LANGUAGE plpgsql;
```

**Redis Alternative (Simpler for MVP):**

If not using Supabase, Railway offers Redis add-on (free tier: 25MB):
- Faster than database queries
- Perfect for rate limiting
- Built-in TTL (automatic expiry)

**Cost:** £0 (Railway free Redis) or £0 (Supabase free tier)

---

#### 2. **Email Capture & Touchpoint Workflow**

**Source:** `email-touchpoint-mapper` skill + `src/lib/email/resend.ts`

**Pirouette's Email Journey:**

```
1. Anonymous Visitor
   └─> Analyzes URL (1/day limit)
       └─> Hits limit → Email capture modal
           ├─> Signs up → Welcome email
           ├─> Gets 3/week → Onboarding email (Day 3)
           └─> Converts to Pro → Thank you + invoice email
```

**PE Scanner Email Journey (Adapted):**

```
1. Anonymous Visitor
   └─> Analyzes ticker (3/day limit)
       └─> Wants portfolio upload → Email capture
           ├─> Signs up → Welcome email + portfolio instructions
           ├─> Uploads portfolio → Report email with results
           └─> 3 days later → "Did you see HOOD's sell signal?" drip email
           └─> 7 days later → "Upgrade for unlimited + weekly alerts"
```

**Email Templates to Create:**

| Template | Trigger | Purpose | Priority |
|----------|---------|---------|----------|
| `WelcomeEmail.tsx` | Email signup | Thank user, explain free tier | 🟢 **P0** |
| `PortfolioReportEmail.tsx` | Portfolio analysis complete | Send results summary with top signals | 🟢 **P0** |
| `WeeklyDigestEmail.tsx` | Every Monday (Pro users) | Top compression opportunities this week | 🟡 P1 |
| `UpgradeReminderEmail.tsx` | Day 7 after signup | Convert free → Pro (£20/mo) | 🟡 P1 |
| `DripSeriesEmail.tsx` | Days 3, 7, 14 | Educational drip campaign | ⚪ P2 |

**Resend Integration (Copy from Pirouette):**

```typescript
// pe-scanner-web/src/lib/email/templates/PortfolioReportEmail.tsx
import { BaseEmail } from './BaseEmail';

export default function PortfolioReportEmail({ 
  userName, 
  portfolioName,
  sellSignals,    // Array of tickers with SELL signal
  buySignals,     // Array of tickers with BUY signal
  reportUrl 
}: Props) {
  return (
    <BaseEmail>
      <h1>Your {portfolioName} Analysis is Ready! 📊</h1>
      <p>Hi {userName},</p>
      
      {sellSignals.length > 0 && (
        <div style={{ backgroundColor: '#FEE2E2', padding: '16px', borderRadius: '8px' }}>
          <h2>🚨 Sell Signals ({sellSignals.length})</h2>
          <ul>
            {sellSignals.map(s => (
              <li key={s.ticker}>
                <strong>{s.ticker}</strong>: {s.headline}
              </li>
            ))}
          </ul>
        </div>
      )}
      
      {buySignals.length > 0 && (
        <div style={{ backgroundColor: '#D1FAE5', padding: '16px', borderRadius: '8px' }}>
          <h2>🟢 Buy Opportunities ({buySignals.length})</h2>
          <ul>
            {buySignals.map(s => (
              <li key={s.ticker}>
                <strong>{s.ticker}</strong>: {s.headline}
              </li>
            ))}
          </ul>
        </div>
      )}
      
      <a href={reportUrl} style={{ 
        display: 'inline-block',
        padding: '12px 24px',
        backgroundColor: '#4F46E5',
        color: 'white',
        textDecoration: 'none',
        borderRadius: '6px',
        marginTop: '20px'
      }}>
        View Full Report →
      </a>
    </BaseEmail>
  );
}
```

---

#### 3. **Scaling Calculator & Breakeven Analysis**

**Source:** `docs/SCALING_ECONOMICS.md` + `scaling-calculator` skill

**Pirouette's Breakeven Formula:**

```
Break-Even Users = Monthly Costs ÷ Net Revenue Per User

Where:
- Monthly Costs = Infrastructure + Domain + Services
- Net Revenue = Price - Stripe Fees
- Stripe Fees ≈ 3.6% (£1.04 for £29 plan)
```

**PE Scanner Breakeven Analysis (£20/mo pricing):**

| Scenario | Monthly Costs | Price | Stripe Fee | Net Revenue | Users Needed | Break-Even MRR |
|----------|---------------|-------|------------|-------------|--------------|----------------|
| **Minimum Stack** | £5.83 | £20 | £0.92 | £19.08 | **1 user** | £20 |
| **Recommended Stack** | £14.83 | £20 | £0.92 | £19.08 | **1 user** | £20 |
| **Upgraded Stack** (Month 3+) | £60 | £20 | £0.92 | £19.08 | **4 users** | £80 |

**Key Insight:** Even with upgraded infrastructure, PE Scanner is profitable at just 4 paying users!

**Pricing Optimization Analysis (Your Question 3):**

Let's compare pricing tiers using Pirouette's breakeven methodology:

| Price Point | Stripe Fee | Net Revenue | Users for £60 Costs | Perceived Value | Recommended? |
|-------------|-----------|-------------|---------------------|-----------------|--------------|
| **£10/mo** | £0.56 | £9.44 | 7 users | Too cheap, devalues tool | ❌ No |
| **£15/mo** | £0.74 | £14.26 | 5 users | Better, but still low | ⚠️ Maybe |
| **£20/mo** | £0.92 | £19.08 | 4 users | Good balance | ✅ **Recommended** |
| **£25/mo** | £1.10 | £23.90 | 3 users | Strong value signal | ✅ Excellent |
| **£29/mo** (Pirouette) | £1.25 | £27.75 | 3 users | SaaS standard | ✅ Proven |
| **£49/mo** (Pirouette Pro+) | £1.96 | £47.04 | 2 users | Premium positioning | 🟡 For portfolio users |

**Recommendation: Tiered Pricing Strategy**

```
Free Tier:
  - 3 tickers/day (anonymous)
  - 10 tickers/day (with account)
  - Basic headline + anchor
  - No portfolio upload
  - Social sharing
  
Pro Tier - £25/mo:  ← UP from £20
  - Unlimited ticker searches
  - Portfolio CSV upload (unlimited)
  - Email reports
  - Historical tracking (coming soon)
  - Priority API access
  - Export to Excel
  
Premium Tier - £49/mo:  ← NEW
  - Everything in Pro
  - Weekly opportunity digest email
  - Slack/Discord alerts (coming soon)
  - API access (1000 calls/month)
  - White-label reports (coming soon)
```

**Why £25 is Better Than £20:**

1. **Stronger Value Signal:** £20 feels "budget," £25 feels "professional"
2. **Better Margins:** 27% more net revenue per user (£23.90 vs £19.08)
3. **Industry Standard:** Most finance tools start at £25-30/mo
4. **Room for Growth:** Can offer £20 promotional pricing later
5. **Covers Costs Faster:** Only 3 users to hit £60/mo upgraded stack

**Annual Pricing (Add 20% Discount):**

```
£25/mo × 12 = £300/year
Annual price: £240/year (save £60)
Effective monthly: £20/mo

- Encourages commitment
- Locks in revenue
- Reduces churn
- Feels like a win for customer
```

---

### **Pirouette's Agent/Workflow Documentation Patterns**

**File Structure Pirouette Uses:**

```
pirouette/
├── .cursor/
│   └── skills/           # Reusable AI prompts/workflows
│       ├── project-scaffolder.md
│       ├── email-touchpoint-mapper.md
│       └── scaling-calculator.md
├── .claude/
│   └── rules/            # Session protocols
│       ├── wake-up-protocol.md
│       └── wrap-up-protocol.md
├── docs/
│   ├── patterns/         # Design patterns
│   │   ├── rate-limiting-pattern.md
│   │   └── feature-gating-pattern.md
│   └── ORCHESTRATOR_INTEGRATION.md  # Cross-project sharing
└── AGENTS.md             # Main AI assistant config
```

**Skills to Port to PE Scanner:**

#### **High Priority Skills (Port Immediately):**

1. **`project-scaffolder.md`**
   - Purpose: Fast Next.js project setup with PE Scanner defaults
   - Usage: Initialize `pe-scanner-web` frontend
   - Copy to: `.cursor/skills/project-scaffolder.md`

2. **`skill-import-assistant.md`**
   - Purpose: Import Pirouette patterns (rate limiting, email, etc.)
   - Usage: Copy working code between projects safely
   - Copy to: `.cursor/skills/skill-import-assistant.md`

3. **`scaling-calculator.md`**
   - Purpose: Calculate breakeven, costs, pricing tiers
   - Usage: Financial modeling for PE Scanner pricing
   - Copy to: `.cursor/skills/scaling-calculator.md`

#### **Medium Priority Skills (Port After MVP):**

4. **`prd-progress-tracker.md`**
   - Purpose: Check launch PRD alignment
   - Usage: Ensure all PRD features are implemented
   - Copy to: `.cursor/skills/prd-progress-tracker.md`

5. **`email-touchpoint-mapper.md`**
   - Purpose: Plan email sequences and user journeys
   - Usage: Design drip campaigns for free → Pro conversion
   - Copy to: `.cursor/skills/email-touchpoint-mapper.md`

---

## 🛡️ **Question 2: Mitigating Free Tier Abuse ("Ticker Spamming")**

### **The Problem**

Without rate limiting, malicious users could:
- ✅ Analyze every ticker on NASDAQ/LSE (10,000+ API calls)
- ✅ Scrape data for competing products
- ✅ Run bots to exhaust API quotas
- ✅ DDoS Yahoo Finance via your API

### **Pirouette's Three-Layer Defense (Apply to PE Scanner)**

#### **Layer 1: IP-Based Rate Limiting (Anonymous Users)**

**Strategy:** Track by IP address, limit to 3 tickers/day

```python
# src/pe_scanner/api/app.py (MODIFY EXISTING)

from flask import request
from .rate_limit import check_anonymous_rate_limit, get_client_ip

@app.route('/api/analyze/<ticker>', methods=['GET'])
def analyze_ticker(ticker):
    # Get user authentication status
    user_id = get_current_user_id()  # Returns None if anonymous
    
    if not user_id:
        # Anonymous user - check IP rate limit
        client_ip = get_client_ip(request)
        rate_limit = check_anonymous_rate_limit(client_ip)
        
        if not rate_limit.allowed:
            return jsonify({
                'error': 'Rate limit exceeded',
                'message': rate_limit.message,
                'resetAt': rate_limit.reset_at.isoformat(),
                'suggestSignup': True,
                'remaining': 0
            }), 429  # HTTP 429 Too Many Requests
    
    # Proceed with analysis...
    result = service.analyze_stock(ticker)
    return jsonify(result)
```

**Advantages:**
- ✅ Works without auth (good for SEO, testing)
- ✅ Converts users ("Sign up for 10/day!")
- ✅ Blocks bot abuse per IP

**Limitations:**
- ⚠️ VPNs can bypass (acceptable trade-off)
- ⚠️ Shared IPs (corporate networks) hit limit faster

**Mitigation for Shared IPs:**
- Use fingerprinting (browser + user agent + accept headers)
- More generous limit (5/day instead of 3)
- Show "Sign up for free to remove limits" earlier

---

#### **Layer 2: Account-Based Rate Limiting (Free Users)**

**Strategy:** Require email signup for higher limits (10 tickers/day)

```python
# src/pe_scanner/api/rate_limit.py

def check_user_rate_limit(user_id: str) -> RateLimitResult:
    """
    Rate limit authenticated free users.
    Uses database to track usage.
    """
    # Get user plan from database
    user = db.users.find_one({'id': user_id})
    plan = user.get('plan', 'free')
    
    if plan == 'pro':
        return RateLimitResult(
            allowed=True,
            remaining=-1,  # Unlimited
            message=None
        )
    
    # Free user - check daily limit
    today = datetime.now().date()
    count = db.ticker_searches.count_documents({
        'user_id': user_id,
        'searched_at': {'$gte': datetime.combine(today, datetime.min.time())}
    })
    
    limit = RATE_LIMITS['free']  # 10/day
    remaining = limit - count
    
    if remaining <= 0:
        return RateLimitResult(
            allowed=False,
            remaining=0,
            message="You've used your 10 free searches today. Upgrade to Pro for unlimited!",
            suggest_upgrade=True
        )
    
    return RateLimitResult(
        allowed=True,
        remaining=remaining,
        message=None
    )
```

**Advantages:**
- ✅ Build email list (lead generation)
- ✅ Track usage per user (not per IP)
- ✅ Can offer personalized upsells

---

#### **Layer 3: Behavioral Analysis (Advanced - Phase 2)**

**Detect Suspicious Patterns:**

```python
# src/pe_scanner/api/abuse_detection.py (NEW FILE - Phase 2)

def is_suspicious_usage(user_or_ip: str, ticker_history: list) -> bool:
    """
    Detect bot-like behavior patterns.
    Returns True if usage looks automated/malicious.
    """
    suspicious_signals = []
    
    # Signal 1: Sequential ticker scanning (AAAA, AAAB, AAAC...)
    if is_sequential_pattern(ticker_history):
        suspicious_signals.append('sequential_scan')
    
    # Signal 2: Too fast (< 2 seconds between requests)
    if has_rapid_requests(ticker_history):
        suspicious_signals.append('rapid_fire')
    
    # Signal 3: No social shares (real users share interesting results)
    if never_shares(user_or_ip):
        suspicious_signals.append('no_engagement')
    
    # Signal 4: Same user agent, different IPs (bot network)
    if distributed_bot_pattern(user_or_ip):
        suspicious_signals.append('bot_network')
    
    return len(suspicious_signals) >= 2  # Require 2+ signals
```

**Actions on Suspicious Users:**
1. **Soft Limit:** Reduce to 1 ticker/day
2. **CAPTCHA:** Require human verification
3. **Ban:** Block IP/user temporarily (1 hour)

---

### **Additional Anti-Abuse Measures**

#### **1. Caching Strategy**

**Problem:** 1000 users analyzing "AAPL" = 1000 API calls to Yahoo Finance

**Solution:** Cache ticker results for 1 hour

```python
# src/pe_scanner/data/fetcher.py (ALREADY HAS CACHING!)

# Existing code uses MarketDataCache with 1-hour TTL
_cache = MarketDataCache(ttl=3600)  # Already implemented ✅

# Result: 1000 users analyzing AAPL = 1 API call (if within 1 hour)
```

**Cost Savings:**
- Without cache: 10,000 users × 5 tickers/day = 50,000 API calls/day
- With cache (popular tickers): ~5,000 API calls/day (90% reduction)

#### **2. Throttling on Frontend**

**Prevent Accidental Spam:**

```typescript
// pe-scanner-web/src/components/TickerSearchForm.tsx

const [isLoading, setIsLoading] = useState(false);
const [lastSearchTime, setLastSearchTime] = useState<number>(0);

const handleSubmit = async (e: FormEvent) => {
  e.preventDefault();
  
  // Throttle: Min 2 seconds between searches
  const now = Date.now();
  if (now - lastSearchTime < 2000) {
    setError('Please wait a moment before searching again');
    return;
  }
  
  setIsLoading(true);
  setLastSearchTime(now);
  
  try {
    const response = await fetch(`/api/analyze/${ticker}`);
    // ...
  } finally {
    setIsLoading(false);
  }
};
```

#### **3. Progressive Rate Limiting**

**Generous at first, stricter if abused:**

```python
# First 3 searches: Instant
# Searches 4-10: Show "Rate limit: X remaining" warning
# Searches 11+: Block with upgrade CTA
# After signup: Reset to 10/day
# After Pro upgrade: Unlimited
```

**User Experience:**
- ✅ Doesn't feel restrictive at first
- ✅ Clear warning before hitting limit
- ✅ Upgrade path is obvious

---

### **Recommended Rate Limits for PE Scanner**

| User Type | Daily Limit | Window | Upgrade Path |
|-----------|-------------|--------|--------------|
| **Anonymous** (no account) | 3 tickers | 24 hours | "Sign up for 10/day" |
| **Free** (email signup) | 10 tickers | 24 hours | "Upgrade to Pro for unlimited" |
| **Pro** (£25/mo) | Unlimited | N/A | Upsell to Premium (£49/mo) for API |
| **Premium** (£49/mo) | Unlimited + API | 1000 API calls/day | Enterprise custom pricing |

**Why These Numbers:**
- **3 anonymous:** Enough to test (e.g., AAPL, MSFT, GOOGL) without signup
- **10 free:** Can analyze a small portfolio (10-15 positions) daily
- **Unlimited Pro:** Main value prop for £25/mo
- **1000 API calls:** Covers automated tools, still sustainable

---

## 💰 **Question 3: Pricing Optimization Using Breakeven Analysis**

### **Current Pricing (from PRD): £20/mo**

**Problems with £20:**
1. Too close to "budget" tier pricing (£15-20 typical for low-end SaaS)
2. Weak value signal (finance tools usually £25-50/mo)
3. Thin margins after Stripe fees (£19.08 net)
4. Leaves no room for promotional discounts

### **Recommended New Pricing: £25/mo + £49/mo Premium**

#### **Pricing Tier Breakdown**

```
┌────────────────────────────────────────────────────────┐
│  FREE TIER                                              │
│  - 10 tickers/day (requires email signup)              │
│  - 3 tickers/day (anonymous)                           │
│  - Basic headline + anchor                              │
│  - Social sharing                                       │
│  Cost to serve: ~£0.001/user/month (cached API calls)  │
└────────────────────────────────────────────────────────┘
                    ▼
┌────────────────────────────────────────────────────────┐
│  PRO TIER - £25/month  ← NEW PRICE (+£5 from PRD)     │
│  - Unlimited ticker searches                            │
│  - Portfolio CSV upload (unlimited)                     │
│  - Email reports with full analysis                     │
│  - Export to Excel                                      │
│  - Historical tracking (save 50 analyses)               │
│  - Priority API access (faster responses)               │
│  Net revenue: £23.90/month (after Stripe 3.6%)         │
└────────────────────────────────────────────────────────┘
                    ▼
┌────────────────────────────────────────────────────────┐
│  PREMIUM TIER - £49/month  ← NEW TIER                  │
│  - Everything in Pro                                    │
│  - Weekly opportunity digest email                      │
│  - Slack/Discord webhook alerts                         │
│  - API access (1000 calls/month)                        │
│  - White-label reports (remove branding)                │
│  - Save unlimited analyses                              │
│  - Priority support (24h response)                      │
│  Net revenue: £47.04/month (after Stripe 3.6%)         │
└────────────────────────────────────────────────────────┘
```

### **Financial Comparison**

| Metric | Current (£20) | Recommended (£25) | Premium (£49) |
|--------|---------------|-------------------|---------------|
| **Gross Revenue** | £20.00 | £25.00 | £49.00 |
| **Stripe Fee (3.6%)** | -£0.92 | -£1.10 | -£1.96 |
| **Net Revenue** | £19.08 | £23.90 | £47.04 |
| **Margin Improvement** | Baseline | **+25.3%** | **+146.5%** |
| **Users for £60 costs** | 4 users | **3 users** | **2 users** |
| **MRR to £1k** | 53 users | **42 users** | **22 users** |

### **Annual Pricing (Recommended)**

```
Monthly Billing:
  Pro: £25/month = £300/year
  Premium: £49/month = £588/year

Annual Billing (20% discount):
  Pro: £240/year (save £60) = £20/month effective
  Premium: £470/year (save £118) = £39.17/month effective

Benefits:
  - Reduces churn (committed for year)
  - Locks in revenue upfront
  - Can invest in features with certainty
  - Customer perceives value ("2 months free")
```

### **Pricing Psychology**

**Why £25 > £20:**

1. **Anchoring Effect:**
   - £20 feels "cheap" (anchors to £15 budget tools)
   - £25 feels "professional" (anchors to £29 Pirouette, £30 industry standard)

2. **Value Perception:**
   - "If it's only £20, how good can it be?"
   - "£25 = serious analysis tool for serious investors"

3. **Feature Justification:**
   - Portfolio upload alone worth £15-20/mo
   - Unlimited searches = £10/mo value
   - Excel export = £5/mo value
   - Total perceived value: £30-35/mo → £25 feels like a deal

4. **Competitor Benchmarking:**
   - Seeking Alpha Premium: $240/year (£200) = £16.67/mo
   - Simply Wall St: $100/year (£83) = £7/mo
   - Finviz Elite: $40/month (£33/mo)
   - Koyfin: $50/month (£42/mo)
   - **PE Scanner at £25/mo = mid-tier, justified by unique P/E compression focus**

### **Premium Tier Justification (£49/mo)**

**Target Audience:**
- Active traders (5-10 trades/week)
- Semi-professional investors (managing £100k+ portfolios)
- Financial advisors (need API for client reports)
- Power users (want automation via Slack/Discord)

**Feature Breakdown:**
- **API Access:** Similar tools charge £30-50/mo for API alone
- **White-label Reports:** Agencies would pay £50/mo for this
- **Webhook Alerts:** Real-time notifications worth £20/mo
- **Priority Support:** Expected at this tier

**Why It Works:**
- Creates price anchoring (£25 looks cheaper next to £49)
- Captures high-value users (10% of Pro users might upgrade)
- Demonstrates product sophistication (has enterprise features)

### **Promotional Pricing Strategy**

```
Launch Phase (Month 1-2):
  - Pro: £20/month (£5 off, "Early Bird Special")
  - Premium: £39/month (£10 off)
  - Annual: 25% off (instead of 20%)
  
  Goal: Acquire first 50 customers at discount
  Result: Lock in revenue, get testimonials, build credibility

Standard Pricing (Month 3+):
  - Pro: £25/month (raise from £20)
  - Premium: £49/month (raise from £39)
  - Annual: 20% off standard pricing
  
  For early birds: "Grandfather" pricing
    - Keep early customers at £20/£39
    - Creates loyalty
    - "You're locked in at our launch price forever!"
```

### **Conversion Funnel Estimates**

```
Month 1:
  1000 visitors
  → 100 sign ups (10% conversion)
  → 10 Pro users (10% of signups) at £20 launch price
  → 1 Premium user (10% of Pro) at £39 launch price
  = £200 + £39 = £239 MRR

Month 3 (standard pricing):
  5000 visitors
  → 500 sign ups (10% conversion)
  → 50 Pro users (10% of signups) at £25
  → 5 Premium users (10% of Pro) at £49
  = £1,250 + £245 = £1,495 MRR

Month 6:
  10,000 visitors
  → 1,000 signups
  → 100 Pro users at £25
  → 10 Premium users at £49
  = £2,500 + £490 = £2,990 MRR
```

**Key Insight:** Premium tier adds ~15-20% to total MRR with minimal extra cost

---

## 📊 **Summary: Recommended Changes**

### **1. Skills/Workflows to Port:**

✅ **Immediate (Before Task Creation):**
- Copy `project-scaffolder.md` → `.cursor/skills/`
- Copy `skill-import-assistant.md` → `.cursor/skills/`
- Copy `scaling-calculator.md` → `.cursor/skills/`
- Create PE Scanner-specific `AGENTS.md`

✅ **Phase 1 (With Frontend):**
- Implement rate limiting (port from `rate-limit.ts`)
- Add email templates (port from `src/lib/email/templates/`)
- Set up Resend integration

### **2. Rate Limiting Strategy:**

✅ **Implement:**
- Anonymous: 3 tickers/day per IP
- Free: 10 tickers/day per account
- Pro: Unlimited
- Premium: Unlimited + API (1000 calls/day)

✅ **Tech Stack:**
- Redis for rate limiting (Railway free tier)
- Supabase for user tracking (optional, or use Clerk metadata)
- IP detection via `x-forwarded-for` header

### **3. Updated Pricing:**

✅ **New Pricing Tiers:**
- Free: 10 tickers/day (signup required)
- **Pro: £25/month** (was £20) - Unlimited searches + portfolio
- **Premium: £49/month** (new tier) - API + webhooks + white-label
- Annual: 20% discount on both tiers

✅ **Launch Pricing:**
- Early bird: £20/month Pro (£5 off) for first 50 customers
- Grandfather pricing for early adopters
- Standard pricing starts Month 3

---

## 📝 **Updated Task Master Tasks (Additions)**

Based on this analysis, **add these tasks before creating the main web tasks**:

### **New Task 26: Port Pirouette Skills & Workflows**
- Copy `project-scaffolder.md`, `skill-import-assistant.md`, `scaling-calculator.md`
- Create PE Scanner `AGENTS.md`
- Document rate limiting strategy
- Document pricing tiers
- **Effort:** 0.5 days
- **Priority:** HIGH
- **Dependencies:** None

### **Modified Task 34: Implement Rate Limiting**
- Add Redis connection (Railway)
- Create `rate_limit.py` module (port from Pirouette)
- Add IP-based limiting (anonymous users)
- Add user-based limiting (free/pro tiers)
- Add abuse detection (Phase 2)
- **Effort:** 2 days (was part of email capture)
- **Priority:** HIGH
- **Dependencies:** Task 26

### **Modified Pricing Throughout:**
- Change all references from £20 → £25 for Pro tier
- Add Premium tier (£49) to pricing pages
- Update breakeven calculations
- Add annual billing option

---

**Status:** Ready to create Task Master tasks with these patterns integrated  
**Next Action:** Create tasks 26-52 incorporating Pirouette skills and updated pricing

