# Authentication & Payment Setup Guide
## StockSignal - Clerk + Stripe Integration

This guide walks you through setting up Clerk authentication and Stripe payments for StockSignal.

---

## 📋 Prerequisites

- StockSignal repository cloned
- Node.js and npm installed
- Railway account (for backend)
- Vercel account (for frontend)

---

## 🔐 Part 1: Clerk Authentication Setup

### Step 1: Create Clerk Account

1. Go to https://clerk.com and sign up
2. Create a new application: "StockSignal"
3. Select authentication methods:
   - ✅ Email/Password (required)
   - ✅ Google OAuth (recommended)
   - ✅ GitHub OAuth (optional)

### Step 2: Get Clerk API Keys

1. In Clerk Dashboard → API Keys
2. Copy your keys:
   - `NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY` (starts with `pk_test_...`)
   - `CLERK_SECRET_KEY` (starts with `sk_test_...`)

### Step 3: Configure Clerk URLs

1. In Clerk Dashboard → Paths
2. Set these URLs:
   - **Sign-in page**: `/sign-in`
   - **Sign-up page**: `/sign-up`
   - **After sign-in**: `/dashboard`
   - **After sign-up**: `/dashboard`
   - **Home**: `/`

### Step 4: Add Environment Variables to Vercel

1. Go to Vercel Dashboard → Your Project → Settings → Environment Variables
2. Add these variables:

```bash
NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY=pk_test_xxxxx
CLERK_SECRET_KEY=sk_test_xxxxx
NEXT_PUBLIC_CLERK_SIGN_IN_URL=/sign-in
NEXT_PUBLIC_CLERK_SIGN_UP_URL=/sign-up
NEXT_PUBLIC_CLERK_AFTER_SIGN_IN_URL=/dashboard
NEXT_PUBLIC_CLERK_AFTER_SIGN_UP_URL=/dashboard
```

3. **Important**: Redeploy your app after adding environment variables

---

## 💳 Part 2: Stripe Payment Setup

### Step 1: Create Stripe Account

1. Go to https://stripe.com and sign up
2. Complete account verification (for production)
3. For now, stay in **Test Mode** (toggle in top right)

### Step 2: Get Stripe API Keys

1. In Stripe Dashboard → Developers → API keys
2. Copy your keys:
   - **Publishable key**: `pk_test_...` (starts with pk_test_ in test mode)
   - **Secret key**: `sk_test_...` (starts with sk_test_ in test mode)

### Step 3: Create Products and Prices

#### Create Pro Plan (£25/month)

1. Go to Stripe Dashboard → Products → Create product
2. Fill in:
   - **Name**: "StockSignal Pro"
   - **Description**: "Unlimited analyses + portfolio upload"
   - **Pricing model**: Standard pricing
   - **Price**: £25.00
   - **Billing period**: Monthly
   - **Currency**: GBP
3. Click "Save product"
4. **Copy the Price ID** (starts with `price_...`)

#### Create Pro Annual Plan (£240/year)

1. In the same "StockSignal Pro" product
2. Click "Add another price"
3. Fill in:
   - **Price**: £240.00
   - **Billing period**: Yearly
   - **Currency**: GBP
4. **Copy this Price ID** too

#### Create Premium Plan (£49/month)

1. Create new product: "StockSignal Premium"
2. Description: "Everything in Pro + API access"
3. Price: £49.00 / month (GBP)
4. **Copy the Price ID**

#### Create Premium Annual Plan (£470/year)

1. Add another price to "StockSignal Premium"
2. Price: £470.00 / year (GBP)
3. **Copy the Price ID**

### Step 4: Set Up Webhook

1. In Stripe Dashboard → Developers → Webhooks
2. Click "Add endpoint"
3. Endpoint URL: `https://stocksignal.app/api/webhooks/stripe`
   - (For now, use your Vercel preview URL: `https://your-app.vercel.app/api/webhooks/stripe`)
4. Select events to listen to:
   - ✅ `checkout.session.completed`
   - ✅ `customer.subscription.updated`
   - ✅ `customer.subscription.deleted`
   - ✅ `invoice.payment_failed`
5. Click "Add endpoint"
6. **Copy the Signing secret** (starts with `whsec_...`)

### Step 5: Add Stripe Environment Variables to Vercel

Add these to Vercel (same place as Clerk keys):

```bash
NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY=pk_test_xxxxx
STRIPE_SECRET_KEY=sk_test_xxxxx
STRIPE_WEBHOOK_SECRET=whsec_xxxxx

# Replace with your actual Price IDs from Step 3
NEXT_PUBLIC_STRIPE_PRO_MONTHLY_PRICE_ID=price_xxxxx
NEXT_PUBLIC_STRIPE_PRO_ANNUAL_PRICE_ID=price_xxxxx
NEXT_PUBLIC_STRIPE_PREMIUM_MONTHLY_PRICE_ID=price_xxxxx
NEXT_PUBLIC_STRIPE_PREMIUM_ANNUAL_PRICE_ID=price_xxxxx
```

### Step 6: Redeploy Vercel App

After adding all environment variables:
1. Go to Vercel Dashboard → Deployments
2. Click "..." on latest deployment → Redeploy

---

## 🧪 Part 3: Testing

### Test Clerk Authentication

1. Go to your deployed app
2. Click "Sign In" → "Sign Up"
3. Create test account with email
4. Verify you're redirected to `/dashboard`
5. Check that:
   - ✅ User's name shows in dashboard
   - ✅ "Free Plan" is displayed
   - ✅ Navigation shows user avatar
   - ✅ Sign out button works

### Test Stripe Checkout (Test Mode)

1. While signed in, go to Pricing section
2. Click "Upgrade to Unlimited" on Pro tier
3. Use Stripe test card: `4242 4242 4242 4242`
   - Expiry: Any future date (e.g., `12/34`)
   - CVC: Any 3 digits (e.g., `123`)
   - ZIP: Any 5 digits (e.g., `12345`)
4. Complete checkout
5. Verify:
   - ✅ Redirected to `/dashboard?success=true`
   - ✅ Plan shows as "Pro" (may take a few seconds for webhook)
   - ✅ User avatar/menu shows "Pro"

### Test Webhook Delivery

1. In Stripe Dashboard → Developers → Webhooks
2. Click on your webhook endpoint
3. Check "Recent events" - should see:
   - ✅ `checkout.session.completed` with 200 response
4. If webhook failed (non-200 response):
   - Check Vercel logs for errors
   - Verify `STRIPE_WEBHOOK_SECRET` is correct
   - Re-send webhook from Stripe dashboard to test

---

## 🚀 Part 4: Backend Rate Limiting Integration

The backend needs to check user plans from Clerk. Here's what needs updating:

### Update Backend Rate Limiting

In `/Users/tomeldridge/PE_Scanner/src/pe_scanner/api/rate_limit.py`:

1. **Add Clerk JWT verification** (requires adding `pyjwt` and `cryptography` to `requirements.txt`)
2. **Extract user ID from Authorization header**
3. **Fetch user metadata from Clerk API** to get plan
4. **Adjust rate limits based on plan:**
   - Anonymous (no auth): 3/day
   - Free (with auth): 10/day
   - Pro/Premium: Unlimited (return `allowed=True`)

### Example Backend Update (Pseudocode)

```python
# In rate_limit.py
from clerk_backend_api import Clerk

clerk = Clerk(bearer_auth=os.getenv("CLERK_SECRET_KEY"))

def check_user_rate_limit(user_id: str) -> RateLimitResult:
    # Get user from Clerk
    user = clerk.users.get(user_id)
    plan = user.public_metadata.get("plan", "free")
    
    if plan in ["pro", "premium"]:
        return RateLimitResult(allowed=True, remaining=-1)  # Unlimited
    
    # Free users: 10/day
    return check_daily_limit(user_id, limit=10)
```

---

## 📊 Part 5: Monitoring & Admin

### Clerk Admin

- View users: Clerk Dashboard → Users
- Check user metadata: Click user → Metadata tab
- Manually update plan: Edit Public Metadata → `{"plan": "pro"}`

### Stripe Admin

- View customers: Stripe Dashboard → Customers
- View subscriptions: Stripe Dashboard → Subscriptions
- Test webhooks: Stripe Dashboard → Developers → Webhooks → Send test event

### Vercel Logs

- View webhook logs: Vercel Dashboard → Your Project → Logs
- Filter by `/api/webhooks/stripe` to see payment events

---

## 🔄 Part 6: Going Live (Production)

### Clerk Production

1. In Clerk Dashboard, switch to "Production" instance
2. Get new production API keys (starts with `pk_live_` and `sk_live_`)
3. Update Vercel environment variables with production keys
4. Redeploy

### Stripe Production

1. Complete Stripe account verification
2. Switch to "Live mode" (toggle in Stripe Dashboard)
3. Recreate products and prices (get new Price IDs)
4. Get new live API keys (`pk_live_` and `sk_live_`)
5. Create new webhook for production URL
6. Update Vercel environment variables with live keys
7. Redeploy

### Important: Update Domain in Clerk

1. Clerk Dashboard → Domains
2. Add your production domain: `stocksignal.app`
3. Verify domain ownership (follow Clerk's instructions)

---

## ❓ Troubleshooting

### "User not found" errors

- ✅ Check that `CLERK_SECRET_KEY` is set in Vercel
- ✅ Verify user is actually signed in (check Network tab for auth cookies)

### Webhook not working

- ✅ Check Vercel logs for errors
- ✅ Verify `STRIPE_WEBHOOK_SECRET` matches Stripe Dashboard
- ✅ Test webhook from Stripe Dashboard → Send test event

### Plan not updating after payment

- ✅ Check Stripe webhook logs for errors
- ✅ Verify webhook received `checkout.session.completed` event
- ✅ Check that `userId` is in session metadata
- ✅ Sign out and sign back in to refresh user data

### Rate limiting not working

- ✅ Check backend logs for rate limit checks
- ✅ Verify `Authorization` header is being sent from frontend
- ✅ Test with curl: `curl -H "Authorization: Bearer <token>" <api-url>`

---

## 📚 Additional Resources

- **Clerk Docs**: https://clerk.com/docs
- **Stripe Docs**: https://stripe.com/docs
- **Next.js Auth**: https://clerk.com/docs/quickstarts/nextjs
- **Stripe Webhooks**: https://stripe.com/docs/webhooks

---

## ✅ Setup Checklist

### Clerk Setup
- [ ] Clerk account created
- [ ] Application configured (email + OAuth)
- [ ] API keys copied
- [ ] Paths configured in Clerk Dashboard
- [ ] Environment variables added to Vercel
- [ ] App redeployed
- [ ] Sign up/sign in tested
- [ ] Dashboard access verified

### Stripe Setup
- [ ] Stripe account created (Test mode)
- [ ] API keys copied
- [ ] Pro monthly product/price created (£25/mo)
- [ ] Pro annual product/price created (£240/yr)
- [ ] Premium monthly product/price created (£49/mo)
- [ ] Premium annual product/price created (£470/yr)
- [ ] All 4 Price IDs copied
- [ ] Webhook endpoint created
- [ ] Webhook secret copied
- [ ] Environment variables added to Vercel
- [ ] App redeployed
- [ ] Test payment completed (4242... card)
- [ ] Plan upgrade verified in dashboard
- [ ] Webhook delivery confirmed

### Backend Integration
- [ ] Backend updated to check Clerk user plan
- [ ] Rate limiting respects Pro/Premium unlimited access
- [ ] Anonymous users limited to 3/day
- [ ] Free users limited to 10/day
- [ ] Backend redeployed to Railway

---

**Status**: Frontend integration complete ✅  
**Next**: Backend rate limiting integration + testing



