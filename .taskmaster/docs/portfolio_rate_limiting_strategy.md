# Portfolio Upload Rate Limiting Strategy

**Status**: Approved for implementation in Task 57  
**Date**: 2024-12-02  
**Dependencies**: Task 34 (Rate Limiting System) ✅ Complete

---

## 🎯 Overview

Implement a **two-tier rate limiting system** that separates single-ticker searches from bulk portfolio uploads, providing optimal UX for free users while preventing abuse.

---

## 📊 Rate Limit Structure

### **Tier 1: Single-Ticker Searches** (✅ Implemented - Task 34)

Used for website search bar: `https://pe-scanner.com/?ticker=AAPL`

| User Tier | Daily Limit | Use Case |
|-----------|-------------|----------|
| **Anonymous** | 3 tickers/day | Quick lookups, no signup |
| **Free** | 10 tickers/day | Regular users with email |
| **Pro** | ✅ Unlimited | Paid subscribers (£25/mo) |
| **Premium** | ✅ Unlimited | API access (£49/mo) |

**Redis Key Format**: `ratelimit:{tier}:{identifier}:{date}`  
**Reset**: Daily at midnight UTC

---

### **Tier 2: Portfolio Uploads** (🔨 To Implement - Task 57)

Used for CSV batch analysis: `POST /api/portfolio`

| User Tier | Uploads/Day | Max Tickers/Upload | Total Daily Tickers |
|-----------|-------------|-------------------|---------------------|
| **Anonymous** | ❌ Not allowed | N/A | Must sign up |
| **Free** | 5 uploads/day | 50 tickers/upload | Up to 250 tickers |
| **Pro** | ✅ Unlimited | 500 tickers/upload | Unlimited |
| **Premium** | ✅ Unlimited | 1000 tickers/upload | Unlimited |

**Redis Key Format**: `portfolio_ratelimit:{tier}:{identifier}:{date}`  
**Reset**: Daily at midnight UTC

---

## 🧠 Rationale

### **Why Separate Limits?**

1. **Better UX for Free Users**:
   - Without separation: Free user uploads 20-stock ISA → hits 10-ticker limit halfway through ❌
   - With separation: Free user uploads 20-stock ISA → analyzes all 20 stocks ✅

2. **Clear Value Proposition**:
   - Free: "Analyze 5 portfolios per day (up to 50 stocks each)"
   - Pro: "Analyze unlimited portfolios (up to 500 stocks each)"

3. **Abuse Prevention**:
   - Free users can't upload massive 1000-ticker CSVs repeatedly
   - Pro users get generous limits (500 tickers = very large portfolio)
   - Portfolio size caps prevent resource exhaustion

4. **Business Model Enforcement**:
   - Free tier provides real value (can analyze full ISA/SIPP)
   - Pro tier is attractive (unlimited uploads + larger portfolios)
   - Premium tier justifies higher price (1000 tickers for fund managers)

---

## 🔧 Implementation Plan

### **1. Update Rate Limit Configuration** (`src/pe_scanner/api/rate_limit.py`)

Add new constants:

```python
# Portfolio-specific rate limits (separate from single-ticker searches)
PORTFOLIO_RATE_LIMITS = {
    "free": 5,           # 5 portfolio uploads/day
    "pro": -1,           # Unlimited uploads
    "premium": -1,       # Unlimited uploads
}

# Maximum tickers allowed per portfolio upload
MAX_PORTFOLIO_SIZE = {
    "free": 50,          # Max 50 tickers per CSV
    "pro": 500,          # Max 500 tickers per CSV
    "premium": 1000,     # Max 1000 tickers per CSV
}
```

### **2. Add Portfolio Rate Limit Check Function**

```python
def check_portfolio_rate_limit(
    tier: str, 
    identifier: str, 
    ticker_count: int
) -> RateLimitResult:
    """
    Check if portfolio upload is within rate limits.
    
    Validates both:
    1. Daily portfolio upload count
    2. Portfolio size (ticker count)
    
    Args:
        tier: User tier (free, pro, premium)
        identifier: User ID or IP address
        ticker_count: Number of tickers in uploaded portfolio
        
    Returns:
        RateLimitResult with limit status
    """
    # Check 1: Portfolio size limit
    max_size = MAX_PORTFOLIO_SIZE.get(tier, MAX_PORTFOLIO_SIZE["free"])
    if ticker_count > max_size:
        return RateLimitResult(
            allowed=False,
            remaining=0,
            limit=max_size,
            reset_at=get_reset_time(),
            tier=tier,
            message=f"Portfolio too large. {tier.title()} tier allows up to {max_size} tickers per upload.",
            suggest_upgrade=(tier == "free"),
            upgrade_url="https://pe-scanner.com/pricing" if tier == "free" else None,
        )
    
    # Check 2: Daily upload count (Pro/Premium unlimited)
    upload_limit = PORTFOLIO_RATE_LIMITS.get(tier, PORTFOLIO_RATE_LIMITS["free"])
    if upload_limit == -1:  # Unlimited
        return RateLimitResult(
            allowed=True,
            remaining=-1,
            limit=-1,
            reset_at=get_reset_time(),
            tier=tier,
        )
    
    # Check Redis for upload count
    client = RedisClient.get_client()
    if client is None:
        # Fail open if Redis unavailable
        logger.warning(f"Redis unavailable - allowing portfolio upload for {tier}:{identifier}")
        return RateLimitResult(
            allowed=True,
            remaining=upload_limit,
            limit=upload_limit,
            reset_at=get_reset_time(),
            tier=tier,
        )
    
    try:
        key = f"portfolio_ratelimit:{tier}:{identifier}:{datetime.now(timezone.utc).strftime('%Y-%m-%d')}"
        current_count = client.get(key)
        current_count = int(current_count) if current_count else 0
        
        if current_count >= upload_limit:
            return RateLimitResult(
                allowed=False,
                remaining=0,
                limit=upload_limit,
                reset_at=get_reset_time(),
                tier=tier,
                message=PORTFOLIO_RATE_LIMIT_MESSAGES[tier]["message"],
                suggest_upgrade=PORTFOLIO_RATE_LIMIT_MESSAGES[tier].get("suggest_upgrade", False),
                upgrade_url=PORTFOLIO_RATE_LIMIT_MESSAGES[tier].get("upgrade_url"),
                hint=PORTFOLIO_RATE_LIMIT_MESSAGES[tier].get("hint"),
            )
        
        return RateLimitResult(
            allowed=True,
            remaining=upload_limit - current_count,
            limit=upload_limit,
            reset_at=get_reset_time(),
            tier=tier,
        )
        
    except redis.RedisError as e:
        logger.error(f"Redis error checking portfolio rate limit: {e}")
        # Fail open
        return RateLimitResult(
            allowed=True,
            remaining=upload_limit,
            limit=upload_limit,
            reset_at=get_reset_time(),
            tier=tier,
        )
```

### **3. Add Portfolio Upload Recording**

```python
def record_portfolio_upload(tier: str, identifier: str, ticker_count: int) -> None:
    """
    Record a portfolio upload for rate limiting.
    
    Args:
        tier: User tier
        identifier: User ID or IP address
        ticker_count: Number of tickers analyzed
    """
    # Pro/Premium users don't need tracking (unlimited)
    if tier in ["pro", "premium"]:
        return
    
    client = RedisClient.get_client()
    if client is None:
        logger.warning("Redis unavailable - cannot record portfolio upload")
        return
    
    try:
        key = f"portfolio_ratelimit:{tier}:{identifier}:{datetime.now(timezone.utc).strftime('%Y-%m-%d')}"
        
        with client.pipeline() as pipe:
            pipe.incr(key)
            pipe.expire(key, RATE_LIMIT_WINDOW + 3600)  # 24h + 1h buffer
            pipe.execute()
            
        logger.info(f"Recorded portfolio upload for {tier}:{identifier} ({ticker_count} tickers)")
        
    except redis.RedisError as e:
        logger.error(f"Failed to record portfolio upload: {e}")
```

### **4. Add Friendly Error Messages**

```python
PORTFOLIO_RATE_LIMIT_MESSAGES = {
    "free": {
        "message": "You've used all 5 of your daily portfolio uploads. Your full portfolio is being tracked—prices update throughout the day. Upgrade to Pro for unlimited portfolio uploads and analysis of up to 500 stocks at once. Or wait until tomorrow when your limit resets.",
        "suggest_upgrade": True,
        "hint": "Stock signals update throughout the day as prices move. Pro users never miss a shift!",
        "upgrade_url": "https://pe-scanner.com/pricing",
    },
}
```

### **5. Create Flask Decorator**

```python
def portfolio_rate_limit_check(f):
    """
    Decorator to enforce portfolio upload rate limits.
    
    Usage:
        @app.route('/api/portfolio', methods=['POST'])
        @portfolio_rate_limit_check
        def upload_portfolio():
            # ... process portfolio
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Get user tier from headers or JWT
        tier = request.headers.get('X-User-Tier', 'free').lower()
        
        # Get identifier (user_id or IP)
        identifier = request.headers.get('X-User-ID')
        if not identifier:
            identifier = get_client_ip()
        
        # Get ticker count from request
        data = request.get_json()
        tickers = data.get('tickers', [])
        ticker_count = len(tickers)
        
        # Check rate limit
        result = check_portfolio_rate_limit(tier, identifier, ticker_count)
        
        if not result.allowed:
            error_response = {
                "error": "PortfolioRateLimitExceeded",
                "message": result.message,
                "limit": result.limit,
                "reset_at": result.reset_at.isoformat(),
                "suggest_upgrade": result.suggest_upgrade,
                "upgrade_url": result.upgrade_url,
                "hint": result.hint,
            }
            return jsonify(error_response), 429
        
        # Add rate limit headers to response
        response = f(*args, **kwargs)
        if hasattr(response, 'headers'):
            response.headers['X-Portfolio-Limit'] = str(result.limit)
            response.headers['X-Portfolio-Remaining'] = str(result.remaining)
            response.headers['X-Portfolio-Reset'] = result.reset_at.isoformat()
        
        # Record upload AFTER successful processing
        record_portfolio_upload(tier, identifier, ticker_count)
        
        return response
    
    return decorated_function
```

---

## 🧪 Testing Requirements

### **Unit Tests** (`tests/unit/test_portfolio_rate_limit.py`)

1. **Portfolio Size Limits**:
   - ✅ Free user: 50 tickers allowed, 51 rejected
   - ✅ Pro user: 500 tickers allowed, 501 rejected
   - ✅ Premium user: 1000 tickers allowed, 1001 rejected

2. **Daily Upload Limits**:
   - ✅ Free user: 5 uploads allowed, 6th rejected
   - ✅ Pro user: Unlimited uploads
   - ✅ Premium user: Unlimited uploads

3. **Separate from Ticker Limits**:
   - ✅ Free user: Can upload 5 portfolios (50 tickers each) AND do 10 single-ticker searches
   - ✅ Single-ticker searches don't affect portfolio upload count
   - ✅ Portfolio uploads don't affect single-ticker count

4. **Error Handling**:
   - ✅ Redis unavailable: Fail open (allow upload)
   - ✅ Redis errors: Fail open with logging

5. **Flask Integration**:
   - ✅ Decorator blocks request when limit exceeded
   - ✅ Decorator adds response headers
   - ✅ Decorator records upload after success

### **Integration Tests** (`tests/integration/test_portfolio_api.py`)

1. **Free User Journey**:
   - Upload 5 portfolios (30 tickers each) → All succeed ✅
   - Upload 6th portfolio → 429 error with upgrade message ✅
   - Do 10 single-ticker searches → All succeed ✅
   - Wait 24h (mock time) → Limits reset ✅

2. **Pro User Journey**:
   - Upload 20 portfolios (200 tickers each) → All succeed ✅
   - No rate limit errors ever ✅

3. **Portfolio Size Edge Cases**:
   - Free user uploads 50-ticker CSV → Success ✅
   - Free user uploads 51-ticker CSV → 429 with size limit message ✅
   - Pro user uploads 500-ticker CSV → Success ✅

---

## 📊 Analytics & Monitoring

### **Metrics to Track**

1. **Portfolio Upload Stats** (by tier):
   - Average portfolio size
   - % of free users hitting 5 upload/day limit
   - % of free users hitting 50 ticker/upload limit
   - Conversion rate after hitting limits

2. **Redis Keys to Monitor**:
   - `portfolio_ratelimit:free:*` - Free user uploads
   - `portfolio_ratelimit:pro:*` - Pro user uploads (should be empty)
   - `portfolio_ratelimit:premium:*` - Premium user uploads (should be empty)

3. **Admin Dashboard Queries**:
   ```python
   # Get users hitting portfolio limits today
   def get_portfolio_limit_hits(tier: str = "free") -> dict:
       client = RedisClient.get_client()
       date_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")
       pattern = f"portfolio_ratelimit:{tier}:*:{date_str}"
       
       limit = PORTFOLIO_RATE_LIMITS[tier]
       hits = []
       for key in client.scan_iter(match=pattern):
           count = int(client.get(key))
           if count >= limit:
               identifier = key.split(":")[2]
               hits.append({"identifier": identifier, "count": count})
       
       return {
           "tier": tier,
           "date": date_str,
           "limit": limit,
           "users_at_limit": len(hits),
           "details": hits,
       }
   ```

---

## 🎯 User Experience Flows

### **Scenario 1: Free User with Small Portfolio**

```
1. User uploads ISA.csv (17 tickers)
   → Check: 1/5 uploads used ✅
   → Check: 17 < 50 ticker limit ✅
   → Analyze all 17 stocks
   → Email report with top sells/buys
   
2. User uploads SIPP.csv (22 tickers)
   → Check: 2/5 uploads used ✅
   → Check: 22 < 50 ticker limit ✅
   → Analyze all 22 stocks
   
3. User does 10 single-ticker searches on website
   → Separate rate limit (10/10 used) ✅
   → No impact on portfolio uploads
   
4. User uploads Wishlist.csv (8 tickers)
   → Check: 3/5 uploads used ✅
   → Still has 2 uploads remaining today
```

### **Scenario 2: Free User Hitting Limits**

```
1. User uploads 5 portfolios throughout the day
   → All succeed ✅
   
2. User tries to upload 6th portfolio
   → 429 Error: "You've used all 5 daily uploads"
   → Message: "Upgrade to Pro for unlimited uploads"
   → CTA button: "Upgrade Now" → pricing page
   → Hint: "Your limits reset at midnight UTC"
```

### **Scenario 3: Free User with Large Portfolio**

```
1. User uploads large_portfolio.csv (75 tickers)
   → Check: 75 > 50 ticker limit ❌
   → 429 Error: "Portfolio too large"
   → Message: "Free tier allows up to 50 tickers per upload"
   → Suggestion: "Upgrade to Pro for up to 500 tickers"
   → Alternative: "Split your portfolio into 2 uploads"
```

### **Scenario 4: Pro User with Large Portfolio**

```
1. User uploads institutional_portfolio.csv (350 tickers)
   → Check: Unlimited uploads ✅
   → Check: 350 < 500 ticker limit ✅
   → Analyze all 350 stocks
   → No rate limit tracking needed
   → Email report with comprehensive analysis
```

---

## 💰 Pricing Page Messaging

Update `web/app/page.tsx` pricing section:

### **Free Tier**
- ✅ 10 single-ticker searches/day
- ✅ **5 portfolio uploads/day** (new!)
- ✅ **Up to 50 stocks per portfolio** (new!)
- ✅ Email reports
- ✅ Basic analysis

### **Pro Tier (£25/mo)**
- ✅ **Unlimited ticker searches**
- ✅ **Unlimited portfolio uploads** (new!)
- ✅ **Up to 500 stocks per portfolio** (new!)
- ✅ Priority support
- ✅ Advanced analytics

### **Premium Tier (£49/mo)**
- ✅ Everything in Pro
- ✅ **Up to 1000 stocks per portfolio** (new!)
- ✅ API access
- ✅ Webhooks
- ✅ White-label reports

---

## 🚀 Deployment Checklist

### **Task 57: Backend Portfolio Endpoint**
- [ ] Add `PORTFOLIO_RATE_LIMITS` constants
- [ ] Add `MAX_PORTFOLIO_SIZE` constants
- [ ] Implement `check_portfolio_rate_limit()`
- [ ] Implement `record_portfolio_upload()`
- [ ] Add `PORTFOLIO_RATE_LIMIT_MESSAGES`
- [ ] Create `@portfolio_rate_limit_check` decorator
- [ ] Apply decorator to `POST /api/portfolio`
- [ ] Write unit tests (30+ tests expected)
- [ ] Write integration tests (10+ tests expected)
- [ ] Update API documentation

### **Task 38: Frontend Portfolio Upload**
- [ ] Display portfolio upload limit: "4 uploads remaining today"
- [ ] Show portfolio size validation before upload
- [ ] Handle 429 errors gracefully
- [ ] Show upgrade CTA when limits hit
- [ ] Display reset time countdown
- [ ] Add "Split Portfolio" helper for oversized uploads

### **Task 40: Pricing Page**
- [ ] Update Free tier features (add portfolio limits)
- [ ] Update Pro tier features (add portfolio limits)
- [ ] Update Premium tier features (add portfolio limits)
- [ ] Add FAQ: "What counts as a portfolio upload?"
- [ ] Add FAQ: "Can I split large portfolios?"

---

## 📝 Documentation Updates

### **API_DOCUMENTATION.md**
- Add `/api/portfolio` endpoint details
- Document portfolio rate limiting
- Show example 429 responses
- Explain tier differences

### **README.md**
- Update pricing tier comparison table
- Add portfolio upload limits

### **AGENTS.md**
- Document portfolio rate limiting strategy
- Update technical stack (mention Redis)

---

## ✅ Success Metrics

### **Pre-Launch**
- ✅ All rate limit tests passing (100%)
- ✅ Redis properly configured on Railway
- ✅ Error messages user-tested for clarity
- ✅ Admin dashboard shows live stats

### **Post-Launch (Week 1)**
- **Target**: <5% of free users hit portfolio size limit
- **Target**: 10-15% of free users hit 5 upload/day limit (good conversion opportunity)
- **Target**: 0 Redis connection errors
- **Target**: <100ms overhead for rate limit checks

### **Post-Launch (Month 1)**
- **Target**: 10% conversion rate from free → Pro (portfolio limits as driver)
- **Target**: Average free user uploads 2-3 portfolios/day
- **Target**: Average Pro user uploads 5-10 portfolios/day

---

**Status**: Ready for implementation in Task 57 🚀  
**Approved By**: User (2024-12-02)  
**Dependencies**: Task 34 (Rate Limiting System) ✅ Complete

