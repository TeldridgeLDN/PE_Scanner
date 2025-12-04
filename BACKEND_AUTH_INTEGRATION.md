# Backend Authentication Integration
## Integrating Clerk User Authentication with Flask Rate Limiting

---

## 📋 Overview

The frontend now has complete Clerk authentication. The backend needs to:
1. Verify Clerk JWT tokens from `Authorization` header
2. Extract user ID and fetch plan from Clerk
3. Apply tiered rate limiting based on plan

---

## 🔧 Required Changes

### 1. Add Dependencies

Add to `requirements.txt`:
```txt
clerk-backend-sdk>=0.1.0
pyjwt>=2.8.0
cryptography>=41.0.0
```

Install:
```bash
pip install clerk-backend-sdk pyjwt cryptography
```

### 2. Add Environment Variable to Railway

In Railway dashboard, add:
```bash
CLERK_SECRET_KEY=sk_test_xxxxx  # Or sk_live_xxxxx for production
```

### 3. Update `rate_limit.py`

Add Clerk integration to `/Users/tomeldridge/PE_Scanner/src/pe_scanner/api/rate_limit.py`:

```python
import os
from clerk_backend_api import Clerk
from clerk_backend_api.jwks_helpers import authenticate_request
from flask import Request

# Initialize Clerk client
clerk_client = Clerk(bearer_auth=os.getenv("CLERK_SECRET_KEY"))

def get_user_from_auth_header(request: Request) -> tuple[str | None, str]:
    """
    Extract user ID and plan from Clerk JWT token.
    
    Returns:
        tuple: (user_id, plan) where plan is 'anonymous', 'free', 'pro', or 'premium'
    """
    auth_header = request.headers.get("Authorization", "")
    
    if not auth_header or not auth_header.startswith("Bearer "):
        return (None, "anonymous")
    
    token = auth_header.replace("Bearer ", "")
    
    try:
        # Verify JWT token with Clerk
        session = authenticate_request(request, clerk_client)
        if not session or not session.user_id:
            return (None, "anonymous")
        
        # Fetch user metadata from Clerk
        user = clerk_client.users.get(session.user_id)
        plan = user.public_metadata.get("plan", "free")
        
        return (session.user_id, plan)
        
    except Exception as e:
        print(f"Auth error: {e}")
        return (None, "anonymous")


def check_rate_limit(request: Request) -> RateLimitResult:
    """
    Check rate limit based on user authentication and plan.
    
    Tiered limits:
    - Anonymous (no auth): 3 requests/day
    - Free (authenticated): 10 requests/day  
    - Pro/Premium: Unlimited
    """
    user_id, plan = get_user_from_auth_header(request)
    
    # Pro/Premium users: unlimited access
    if plan in ["pro", "premium"]:
        return RateLimitResult(
            allowed=True,
            remaining=-1,  # -1 indicates unlimited
            reset_at=None,
            user_plan=plan
        )
    
    # Free authenticated users: 10/day
    if user_id and plan == "free":
        return check_daily_limit(
            key=f"user:{user_id}",
            limit=10,
            window=86400,
            message="Free plan limit: 10 analyses/day. Upgrade to Pro for unlimited access."
        )
    
    # Anonymous users: 3/day (by IP)
    client_ip = request.headers.get("X-Forwarded-For", request.remote_addr).split(",")[0].strip()
    return check_daily_limit(
        key=f"ip:{client_ip}",
        limit=3,
        window=86400,
        message="Anonymous limit: 3 analyses/day. Sign up for 10/day free, or upgrade to Pro for unlimited."
    )


# Update RateLimitResult to include plan info
@dataclass
class RateLimitResult:
    allowed: bool
    remaining: int
    reset_at: datetime | None
    user_plan: str = "anonymous"
    message: str | None = None
```

### 4. Update API Endpoints

In `/Users/tomeldridge/PE_Scanner/src/pe_scanner/api/app.py`:

```python
@app.route('/api/analyze/<ticker>', methods=['GET'])
def analyze_ticker(ticker: str):
    # Check rate limit
    rate_limit_result = check_rate_limit(request)
    
    if not rate_limit_result.allowed:
        return jsonify({
            'error': 'Rate limit exceeded',
            'message': rate_limit_result.message,
            'plan': rate_limit_result.user_plan,
            'reset_at': rate_limit_result.reset_at.isoformat() if rate_limit_result.reset_at else None,
            'upgrade_url': 'https://stocksignal.app/#pricing'
        }), 429
    
    # Add rate limit headers
    response_headers = {
        'X-RateLimit-Plan': rate_limit_result.user_plan,
        'X-RateLimit-Remaining': str(rate_limit_result.remaining),
    }
    if rate_limit_result.reset_at:
        response_headers['X-RateLimit-Reset'] = rate_limit_result.reset_at.isoformat()
    
    # ... rest of analysis logic ...
```

---

## 🧪 Testing

### Test with cURL

#### Anonymous Request (should limit to 3/day)
```bash
curl https://pescanner-production.up.railway.app/api/analyze/AAPL
```

#### Authenticated Free User (should limit to 10/day)
```bash
curl -H "Authorization: Bearer <clerk_jwt_token>" \
     https://pescanner-production.up.railway.app/api/analyze/AAPL
```

#### Pro User (should be unlimited)
```bash
# First upgrade a test user to Pro in Clerk Dashboard
# Then make request with their token
curl -H "Authorization: Bearer <pro_user_token>" \
     https://pescanner-production.up.railway.app/api/analyze/AAPL
```

### Get JWT Token for Testing

1. Sign in to your app at `https://stocksignal.vercel.app`
2. Open browser DevTools → Application → Cookies
3. Find cookie named `__session`
4. Copy the value - this is your JWT token
5. Use it in the `Authorization: Bearer <token>` header

---

## 📊 Rate Limit Response Headers

Clients should respect these headers:

```
X-RateLimit-Plan: free|pro|premium|anonymous
X-RateLimit-Remaining: 7  # or -1 for unlimited
X-RateLimit-Reset: 2024-12-03T00:00:00Z
```

---

## ⚠️ Important Notes

### Security
- ✅ Always verify JWT signature (Clerk does this automatically)
- ✅ Use HTTPS only in production
- ✅ Never log JWT tokens
- ✅ Check token expiry

### Performance
- Consider caching user plan lookups (TTL: 5 minutes)
- Redis can store `user_id:plan` pairs temporarily
- Reduces Clerk API calls

### Error Handling
- If Clerk API is down, fall back to IP-based limiting
- Log authentication failures but don't expose details to client
- Graceful degradation: if Redis is down, allow requests (with logging)

---

## 🚀 Deployment Checklist

- [ ] Add `clerk-backend-sdk`, `pyjwt`, `cryptography` to `requirements.txt`
- [ ] Update `rate_limit.py` with Clerk integration
- [ ] Update `app.py` to use new rate limit check
- [ ] Add `CLERK_SECRET_KEY` to Railway environment
- [ ] Deploy to Railway
- [ ] Test anonymous limit (3/day)
- [ ] Test free user limit (10/day)
- [ ] Test Pro user (unlimited)
- [ ] Verify rate limit headers in responses
- [ ] Check Railway logs for any auth errors

---

## 📈 Monitoring

### Key Metrics to Track

- **Anonymous requests**: Track IPs hitting 3/day limit
- **Free signups**: Users creating accounts for 10/day
- **Upgrade conversions**: Free users hitting limit who then upgrade
- **Pro usage**: Requests from paid users (should be unlimited)

### Railway Logs to Watch

```bash
# Successful auth
INFO: User abc123 (plan: pro) - unlimited access

# Free user hitting limit
WARNING: User xyz789 (plan: free) - limit reached (10/10)

# Anonymous hitting limit
WARNING: IP 1.2.3.4 - limit reached (3/3)

# Auth failures
ERROR: Invalid JWT token - falling back to IP limit
```

---

## 🔄 Future Enhancements

1. **Usage Dashboard**: Show users their usage stats in `/dashboard`
2. **Email Alerts**: Notify users when approaching daily limit
3. **Soft Limits**: Warn users at 80% of limit
4. **Burst Protection**: Prevent rapid-fire requests (5 req/minute)
5. **API Keys**: For Premium users who want programmatic access

---

**Status**: Frontend complete, backend integration pending  
**Estimated Time**: 2-3 hours for backend changes + testing  
**Priority**: High (required for revenue generation)



