# PE Scanner Pricing Strategy Analysis

**Date:** 2025-12-02  
**Version:** 2.0 (Updated from original PRD)  
**Based On:** Pirouette scaling-calculator patterns + breakeven analysis

---

## Executive Summary

The updated pricing strategy increases baseline revenue by **25%** (£20 → £25 Pro) and adds a **Premium tier at £49/mo**, creating a revenue ceiling **145% higher** than the original single-tier model. The business remains profitable from **customer #1** with a **41% margin**, scaling to **>90% margin** at 100+ customers.

**Key Changes:**
- Pro tier: £20/mo → £25/mo (+25%)
- New Premium tier: £49/mo (new!)
- Annual billing: 20% discount (£240/yr Pro, £470/yr Premium)
- Free tier: Clarified as 10/day (signup) or 3/day (anonymous)

---

## Pricing Tiers Detailed Breakdown

### **Free Tier: £0/month**

**What You Get:**
- ✅ 10 ticker analyses per day (with signup)
- ✅ 3 ticker analyses per day (anonymous, no signup)
- ✅ Full analysis results (VALUE/GROWTH/HYPER_GROWTH modes)
- ✅ Shareable headlines for Twitter/LinkedIn
- ✅ Anchoring statements ("What Would Have To Be True")
- ✅ Basic P/E compression, PEG, P/S analysis
- ✅ Social sharing buttons
- ❌ No portfolio CSV upload
- ❌ No email reports
- ❌ No historical tracking
- ❌ No API access

**Target Users:**
- Curious investors trying the tool
- Casual users checking 1-2 stocks per week
- Social media users sharing analysis results

**Conversion Trigger:**
- Hit 10/day limit (suggests upgrade)
- Want portfolio analysis (gate with email capture)
- Need historical tracking

**Economics:**
- Cost to serve: ~£0.001 per analysis (Yahoo Finance + compute)
- Monthly cost (10 analyses/day): £0.30
- Purpose: Lead generation, viral growth

---

### **Pro Tier: £25/month or £240/year**

**What You Get:**
- ✅ **Unlimited ticker analyses** (no daily limit)
- ✅ **Portfolio CSV upload** (up to 100 positions)
- ✅ **Email reports** (portfolio analysis summary)
- ✅ **Historical tracking** (save last 50 analyses)
- ✅ **Export to Excel** (portfolio results)
- ✅ **Priority API access** (faster response times)
- ✅ All Free tier features
- ❌ No API key (Premium only)
- ❌ No webhooks (Premium only)
- ❌ No white-label reports (Premium only)

**Target Users:**
- Active retail investors managing ISA/SIPP portfolios
- Day traders checking multiple tickers daily
- Small investment clubs (2-5 members)
- Finance bloggers/influencers

**Value Proposition:**
- Portfolio upload saves **hours of manual work**
- Email reports provide **convenience** (check inbox vs. website)
- Historical tracking enables **trend analysis**
- Unlimited analyses = **no anxiety** about hitting limits

**Pricing Rationale:**
- £25/mo = **£0.83/day** (cost of a coffee)
- Competitor pricing: Morningstar Premium £28/mo, Simply Wall St £20/mo
- Annual option: **£20/mo** (£240/yr) = **17% discount** on monthly
- Sweet spot for serious investors

**Economics:**
- Cost to serve: ~£0.50/mo (assuming 100 analyses/mo @ £0.005 each)
- Gross margin: **98%** (£25 - £0.50 = £24.50)
- Break-even: **1 customer** covers all infrastructure (£25 > £14.83)

---

### **Premium Tier: £49/month or £470/year**

**What You Get:**
- ✅ **Everything in Pro**
- ✅ **API access** (1000 calls/day, RESTful API)
- ✅ **Slack/Discord webhooks** (automatic portfolio alerts)
- ✅ **White-label reports** (custom branding for advisors)
- ✅ **Priority support** (24h response time)
- ✅ **Unlimited saved analyses** (no 50-analysis limit)
- ✅ **Weekly opportunity digest** (curated buy/sell signals)
- ✅ **Early access to new features**

**Target Users:**
- Portfolio managers (managing multiple client accounts)
- Fintech developers (building on PE Scanner API)
- Financial advisors (white-label reports for clients)
- Quantitative traders (API for algorithmic strategies)
- Investment newsletters (automated content generation)

**Value Proposition:**
- **API access** enables **automation** (no manual checks)
- **Webhooks** provide **real-time alerts** (Slack/Discord integration)
- **White-label** allows **client-facing reports** (professional branding)
- **Unlimited saves** = **complete portfolio history** (trend analysis over years)

**Pricing Rationale:**
- £49/mo = **£1.63/day** (still < price of lunch)
- API access alone worth £30-50/mo (competitor: Alpha Vantage £40/mo)
- White-label saves £100s on report design
- Annual option: **£39.17/mo** (£470/yr) = **20% discount**

**Economics:**
- Cost to serve: ~£2/mo (higher API usage, email digests)
- Gross margin: **96%** (£49 - £2 = £47)
- Target: **10-20% of Pro users** upgrade to Premium

---

## Pricing Comparison: Old vs. New

### Revenue Per Customer

| Tier | Old Model | New Model | Increase |
|------|-----------|-----------|----------|
| Free | £0 | £0 | - |
| Pro (Monthly) | £20/mo | £25/mo | **+25%** |
| Premium (Monthly) | N/A | £49/mo | **New!** |
| Pro (Annual) | £240/yr | £240/yr | Same |
| Premium (Annual) | N/A | £470/yr | **New!** |

### Revenue Ceiling (100 Customers)

| Scenario | Old Model | New Model | Increase |
|----------|-----------|-----------|----------|
| All Pro (monthly) | £2,000/mo | £2,500/mo | **+25%** |
| All Premium (monthly) | N/A | £4,900/mo | **+145%** |
| 80% Pro, 20% Premium | N/A | £2,980/mo | **+49%** |
| All Pro (annual) | £2,000/mo | £2,000/mo | Same |
| All Premium (annual) | N/A | £3,917/mo | **+96%** |

**Realistic Mix (Month 6):**
- 400 Free users
- 80 Pro users (monthly): £2,000/mo
- 15 Pro users (annual): £300/mo
- 4 Premium users (monthly): £196/mo
- 1 Premium user (annual): £39/mo
- **Total MRR: £2,535/mo** vs. Old Model: £2,000/mo (**+27%**)

---

## Break-Even Analysis

### Infrastructure Costs (Monthly)

| Service | Purpose | Free Tier | Paid Tier | PE Scanner Uses | Cost |
|---------|---------|-----------|-----------|-----------------|------|
| **Vercel** | Frontend hosting | 100GB bandwidth | £16/mo Pro | Free → Pro at ~20k visitors | £0 → £16 |
| **Railway** | Backend API | £4/mo Hobby | Usage-based | Hobby initially | £5 |
| **Redis** | Rate limiting | 25MB free | £10/mo | Railway free tier | £0 |
| **Plausible** | Analytics | Self-host | £9/mo | Paid tier | £9 |
| **Resend** | Email service | 3k emails/mo | £20/mo | Free tier initially | £0 |
| **Domain** | pe-scanner.com | N/A | N/A | Namecheap | £0.83 |

**Total Infrastructure Costs:**
- **Minimum (MVP)**: £5.83/mo (Railway + domain, self-host everything else)
- **Recommended (Launch)**: £14.83/mo (Railway + Plausible + domain)
- **Growth (1000 users)**: £45/mo (+ Vercel Pro £16, + Resend Pro £20, + Railway scaling £5)

### Break-Even Customers

| Infrastructure Level | Monthly Cost | Customers Needed (Pro @ £25) | Customers Needed (Premium @ £49) |
|---------------------|--------------|-------------------------------|-----------------------------------|
| **Minimum** | £5.83 | 0.23 → **1 customer** | 0.12 → **1 customer** |
| **Recommended** | £14.83 | 0.59 → **1 customer** | 0.30 → **1 customer** |
| **Growth** | £45 | 1.8 → **2 customers** | 0.92 → **1 customer** |

**Key Insight:** Business is profitable from **Day 1** with a single paying customer at any tier and any infrastructure level.

---

## Gross Margin Analysis

### Margin at Different Scales

| Stage | Users | Paid | MRR | Infrastructure | Gross Margin |
|-------|-------|------|-----|----------------|--------------|
| **Launch** | 100 | 10 | £250 | £15 | **94%** |
| **Month 3** | 500 | 50 | £1,250 | £25 | **98%** |
| **Month 6** | 1,000 | 100 | £2,500 | £45 | **98.2%** |
| **Month 12** | 5,000 | 500 | £12,500 | £150 | **98.8%** |
| **Scale** | 10,000 | 1,000 | £25,000 | £300 | **98.8%** |

**SaaS Benchmark:** 70-80% gross margin is considered good.  
**PE Scanner:** >94% at all scales (exceptional!).

**Why So High?**
- Low per-user costs (API calls are cheap)
- No human support costs (self-service)
- Scalable infrastructure (serverless/managed)
- No COGS (software, not physical product)

---

## Competitive Analysis

### Direct Competitors

| Tool | Pricing | Analysis Type | Limitation |
|------|---------|---------------|------------|
| **Simply Wall St** | £20/mo | Fundamental analysis | US-focused, generic scoring |
| **Morningstar Premium** | £28/mo | Star ratings + reports | Complex, analyst-driven |
| **Seeking Alpha Premium** | £24/mo | Articles + data | Content-heavy, not tool-focused |
| **TipRanks** | £30/mo | Analyst consensus | US-only, no P/E compression |
| **Finviz Elite** | $25/mo (~£20) | Screeners + charts | Technical focus, no valuation |

**PE Scanner Positioning:**
- **Price:** £25 Pro is **competitive** (middle of pack)
- **Premium:** £49 is **below** professional tools (Bloomberg £2k+, FactSet £10k+)
- **Unique:** **Only tool** focused specifically on P/E compression
- **UK-Friendly:** Handles UK stocks (pence/pounds) correctly

### Indirect Competitors (Free Tools)

| Tool | What It Does | Limitation |
|------|--------------|------------|
| **Yahoo Finance** | P/E ratios, forward estimates | No analysis, just raw data |
| **Google Finance** | Basic metrics | No forward P/E, no compression calc |
| **Finviz (Free)** | Screeners | No detailed valuation analysis |

**PE Scanner Advantage:**
- **Synthesis:** Combines trailing P/E, forward P/E, and interpretation
- **Actionable:** BUY/SELL/HOLD signals with confidence levels
- **Shareable:** Headlines optimized for social media
- **Portfolio:** Batch analysis (competitors require manual 1-by-1)

---

## Annual Billing Strategy

### Monthly vs. Annual Comparison

| Tier | Monthly | Annual (Monthly Equivalent) | Savings | Discount |
|------|---------|----------------------------|---------|----------|
| **Pro** | £25/mo | £20/mo (£240/yr) | £60/yr | **20%** |
| **Premium** | £49/mo | £39.17/mo (£470/yr) | £118/yr | **20%** |

### Why Offer Annual Billing?

**For PE Scanner (Business Benefits):**
- **Cash flow:** £240 upfront vs. £25/mo drip
- **Retention:** 12-month commitment reduces churn
- **Predictability:** Easier revenue forecasting
- **LTV:** Higher lifetime value per customer

**For Customers (User Benefits):**
- **Savings:** £60-118/year discount
- **Convenience:** "Set and forget" (no monthly charges)
- **Commitment:** Shows confidence in long-term use

### Expected Annual Mix

Based on SaaS benchmarks (30-40% choose annual):

| Month | Total Paid | Annual % | Annual Customers | Monthly Customers |
|-------|-----------|----------|------------------|-------------------|
| 1 | 10 | 20% | 2 | 8 |
| 3 | 50 | 30% | 15 | 35 |
| 6 | 100 | 35% | 35 | 65 |
| 12 | 500 | 40% | 200 | 300 |

**Annual MRR Impact (Month 6):**
- 65 monthly Pro: £1,625/mo
- 30 annual Pro: £600/mo (£240/yr ÷ 12)
- 4 monthly Premium: £196/mo
- 1 annual Premium: £39/mo (£470/yr ÷ 12)
- **Total: £2,460/mo** (vs. all-monthly: £2,500/mo)

**Trade-off:** Slightly lower MRR, but **higher cash collected** and **better retention**.

---

## Free Tier Strategy

### Conversion Funnel

```
Anonymous User (3/day)
    ↓ [Hit limit, want more]
Signup for Free (10/day)
    ↓ [Hit limit OR want portfolio]
Email Capture Modal
    ↓ [Upload portfolio]
See Value (ranked buy/sell signals)
    ↓ [Want unlimited OR history]
Upgrade to Pro (£25/mo)
    ↓ [Need API OR white-label]
Upgrade to Premium (£49/mo)
```

### Free Tier Limits (Why 10/day?)

**Too Restrictive (3/day for all):**
- ❌ Users can't properly evaluate the tool
- ❌ Conversion rate drops (no "aha" moment)
- ❌ Negative perception ("too limiting")

**Too Generous (Unlimited free):**
- ❌ No incentive to upgrade
- ❌ High infrastructure costs
- ❌ Attracts scrapers/abusers

**Just Right (10/day with signup):**
- ✅ Enough to analyze a small portfolio (5-10 stocks)
- ✅ Creates upgrade desire (power users hit limit)
- ✅ Prevents abuse (require signup)
- ✅ Builds email list (for drip campaign)

**Conversion Triggers:**
- **Volume:** Power user hits 10/day limit
- **Feature:** Wants portfolio CSV upload
- **History:** Needs to track changes over time
- **Convenience:** Wants email reports instead of manual checks

---

## Premium Tier Strategy

### Target Market Sizing

**UK Market:**
- Retail investors: ~12 million
- Active traders (check stocks weekly): ~1 million
- Portfolio managers/advisors: ~30,000
- **TAM (Total Addressable Market):** 1M+ users

**Premium Segment:**
- Portfolio managers: 30,000
- Fintech developers: ~5,000
- Financial advisors: ~50,000
- **Premium TAM:** ~85,000 users

**Realistic Premium Penetration:**
- Year 1: 10-20 Premium users (0.02% of TAM)
- Year 2: 100-200 Premium users (0.2% of TAM)
- Year 3: 500-1000 Premium users (1% of TAM)

### Premium Features Justification

**API Access (1000 calls/day):**
- **Use Case:** Automated portfolio monitoring, algorithmic trading
- **Value:** Saves 10+ hours/week vs. manual checks
- **Cost to Build:** £5k+ for equivalent in-house solution
- **Pricing:** £49/mo = £588/yr (8.5% of build cost)

**Webhooks (Slack/Discord):**
- **Use Case:** Real-time alerts when P/E compression changes
- **Value:** Never miss a buying opportunity or sell signal
- **Alternative:** Manual daily checks (time-consuming)
- **Integration:** 10-minute setup vs. hours building custom alerts

**White-Label Reports:**
- **Use Case:** Financial advisors sending reports to clients
- **Value:** Professional branding, client retention
- **Alternative:** Hire designer (£500+) + developer (£2k+)
- **Pricing:** £49/mo = £588/yr (23% of build cost)

---

## Revenue Projections

### Conservative Scenario (10% Free→Paid Conversion)

| Month | Free Users | Paid Users | Pro (£25) | Premium (£49) | MRR | ARR |
|-------|-----------|------------|-----------|---------------|-----|-----|
| 1 | 100 | 10 | 10 | 0 | £250 | £3,000 |
| 3 | 500 | 50 | 48 | 2 | £1,348 | £16,176 |
| 6 | 1,000 | 100 | 95 | 5 | £2,620 | £31,440 |
| 12 | 5,000 | 500 | 475 | 25 | £13,100 | £157,200 |
| 24 | 10,000 | 1,000 | 950 | 50 | £26,200 | £314,400 |

**Assumptions:**
- 10% conversion rate (industry standard)
- 5% of paid users choose Premium
- 30% choose annual billing (not reflected in MRR)

### Optimistic Scenario (15% Conversion)

| Month | Free Users | Paid Users | Pro (£25) | Premium (£49) | MRR | ARR |
|-------|-----------|------------|-----------|---------------|-----|-----|
| 1 | 100 | 15 | 15 | 0 | £375 | £4,500 |
| 3 | 500 | 75 | 71 | 4 | £1,971 | £23,652 |
| 6 | 1,000 | 150 | 143 | 7 | £3,918 | £47,016 |
| 12 | 5,000 | 750 | 713 | 37 | £19,638 | £235,656 |
| 24 | 10,000 | 1,500 | 1,425 | 75 | £39,300 | £471,600 |

---

## Pricing Psychology

### Anchoring Effect

**Three-Tier Pricing Creates Anchor:**
- Free (£0) = **Entry point** (low commitment)
- Pro (£25) = **Target tier** (seems reasonable vs. £49)
- Premium (£49) = **Anchor** (makes £25 feel cheap)

**Without Premium Tier:**
- Users compare £25 to £0 (seems expensive)

**With Premium Tier:**
- Users compare £25 to £49 (seems reasonable)
- Premium legitimizes Pro as "good value"

### Decoy Effect

**Premium acts as a decoy:**
- Most users don't need API/webhooks
- But its existence makes Pro seem like a deal
- Expected split: 90% Pro, 10% Premium

### Price-Value Perception

| Price Point | Perception | Reality |
|-------------|-----------|---------|
| **£9.99** | "Cheap toy" | Undervalued |
| **£19.99** | "Budget tool" | Competitive but low-margin |
| **£25** | "Serious tool" | ✅ **Sweet spot** |
| **£49** | "Professional" | ✅ **Premium positioning** |
| **£99+** | "Enterprise" | Requires sales team |

**PE Scanner Positioning:**
- Pro (£25) = **Prosumer** (serious retail investors)
- Premium (£49) = **Professional** (advisors, developers)

---

## Competitive Moats

### Why Customers Won't Leave

**Switching Costs:**
- **Data Lock-in:** Historical analyses saved (Premium: unlimited)
- **Workflow Integration:** API/webhooks embedded in systems
- **Learning Curve:** Familiarity with P/E compression methodology

**Network Effects:**
- **Shared Headlines:** Social proof (more shares = more credibility)
- **Community:** Users discussing signals on Twitter/Reddit

**Feature Velocity:**
- **Continuous Improvement:** New analysis modes, better data quality
- **First-Mover:** Only P/E compression-focused tool

---

## Pricing Optimization Recommendations

### Short-Term (Months 1-6)

1. **Grandfather Early Adopters:**
   - First 50 customers: Lock in £20/mo forever
   - Creates urgency: "Early bird pricing expires soon"
   - Builds loyalty: "Thank you for believing in us"

2. **A/B Test Pricing:**
   - Test £25 vs. £29 for Pro
   - Test £49 vs. £59 for Premium
   - Use Stripe Experiments (built-in A/B testing)

3. **Seasonal Promotions:**
   - Q4 (tax year planning): "Prepare your ISA for 2025"
   - January (New Year): "Start 2025 with better investing"
   - Never discount >20% (devalues product)

### Medium-Term (Months 7-12)

1. **Add Team Tier:**
   - £75/mo for 3 users (£25/user)
   - Target: Investment clubs, small firms
   - Features: Shared analyses, team dashboard

2. **Introduce Add-Ons:**
   - Extra API calls: £10/mo for +5k calls
   - Custom webhooks: £15/mo for unlimited
   - Advanced analytics: £20/mo for custom reports

3. **Volume Discounts:**
   - Annual: 20% off (already planned)
   - 3-year: 30% off (for committed users)
   - Lifetime: £2,000 one-time (40 months of Pro)

### Long-Term (Year 2+)

1. **Enterprise Tier:**
   - Custom pricing (£500-2000/mo)
   - White-label entire platform
   - Dedicated support
   - Custom integrations

2. **Usage-Based Pricing:**
   - Pro: Unlimited up to 10k analyses/mo
   - Overage: £0.01 per analysis
   - Appeals to occasional users

3. **Freemium+:**
   - Free tier stays at 10/day
   - Increase Pro to £29/mo (inflation)
   - Add "Plus" tier at £19/mo (50 analyses/mo)

---

## Pricing FAQs

### "Why £25 instead of £20?"

**Answer:** Our original pricing (£20/mo) was calculated before we fully understood infrastructure costs. At £25/mo:
- We maintain a healthy 98% gross margin
- We can invest more in features and support
- It's still competitive with similar tools (£20-30 range)
- Annual option (£20/mo equivalent) matches original pricing

### "Why offer a free tier at all?"

**Answer:** The free tier serves multiple purposes:
- **Lead Generation:** Builds email list for drip campaigns
- **Viral Growth:** Free users share headlines on social media
- **Product Validation:** Proves demand before investing in paid features
- **Conversion Funnel:** 10% of free users convert to paid

### "What if nobody pays £49/mo for Premium?"

**Answer:** Premium tier is intentionally niche (target: 5-10% of paid users). Even if only 1% upgrade:
- 5 Premium users = £245/mo additional revenue
- Still provides anchoring effect (makes £25 seem reasonable)
- API access alone justifies the price for developers

### "Should we offer refunds?"

**Answer:** Yes, implement a **30-day money-back guarantee**:
- Reduces purchase anxiety ("What if I don't like it?")
- Increases conversion rate (industry standard: +10-15%)
- Actual refund rate typically <5% for SaaS
- Builds trust and credibility

---

## Summary & Recommendations

### ✅ Keep These Elements

1. **£25 Pro Tier** - Perfect balance of value and margin
2. **£49 Premium Tier** - Creates anchoring effect, serves niche
3. **20% Annual Discount** - Industry standard, improves retention
4. **10/day Free Tier** - Generous enough to convert, restrictive enough to prevent abuse

### 🔄 Consider Testing

1. **Early Bird Pricing** - First 50 customers at £20/mo forever
2. **Monthly/Annual Toggle** - Prominently display annual savings (£60/yr)
3. **Team Tier** - £75/mo for 3 users (if demand emerges)
4. **30-Day Money-Back** - Reduces friction, increases conversions

### 📊 Monitor These Metrics

1. **Conversion Rate** - Target: 10% free → paid (industry avg: 2-10%)
2. **Annual Mix** - Target: 30-40% choose annual
3. **Premium Uptake** - Target: 5-10% of paid users
4. **Churn Rate** - Target: <5% monthly (< 60% annual)

### 💡 Next Steps

1. **Update Frontend** (Task 33) - Display new pricing tiers
2. **Implement Stripe** (Future) - Support monthly/annual billing
3. **Add Rate Limiting** (Task 34) - Enforce 3/10/unlimited tiers
4. **Track Analytics** (Task 44) - Monitor conversion funnel

---

**Conclusion:** The updated pricing strategy positions PE Scanner as a **professional-grade tool** with a **clear path from free to Premium**. The £25 Pro tier balances value and margins, while the £49 Premium tier serves power users and creates anchoring. The business is **profitable from customer #1** and scales to **>98% gross margins**, setting up PE Scanner for sustainable growth.

---

**Next Task:** Proceed to Task 27 (Initialize Next.js 15 Frontend) to start building the interface for this pricing model.

