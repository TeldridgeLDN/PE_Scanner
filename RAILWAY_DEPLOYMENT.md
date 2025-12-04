# Railway Deployment Guide - StockSignal Backend API

**Status**: Task 39 - Deploy Flask API to Railway  
**Date**: 2024-12-02  
**Dependencies**: Task 34 (Rate Limiting) ✅ Complete

---

## 🚀 Quick Start

### **Prerequisites**
1. Railway account (sign up at [railway.app](https://railway.app))
2. GitHub repository with StockSignal code
3. Redis service (will be added in Railway)

### **Deployment Steps**

#### **1. Create New Railway Project**
```bash
# Option A: Using Railway CLI
railway login
railway init
railway up

# Option B: Using Railway Dashboard (Recommended)
1. Go to https://railway.app/new
2. Select "Deploy from GitHub repo"
3. Choose: tomeldridge/StockSignal (or your fork)
4. Railway will auto-detect the Dockerfile
```

#### **2. Add Redis Service**
1. In Railway project dashboard, click "+ New"
2. Select "Database" → "Redis"
3. Railway will automatically create `REDIS_URL` environment variable
4. Free tier: 25MB storage (plenty for rate limiting)

#### **3. Configure Environment Variables**

In Railway project settings → Variables, add:

```bash
# Flask Configuration
FLASK_ENV=production
PORT=8000  # Railway auto-provides this

# CORS Origins (comma-separated)
ALLOWED_ORIGINS=https://stocksignal.app,https://www.stocksignal.app,http://localhost:3000

# Redis (auto-provided by Railway Redis service)
REDIS_URL=${REDIS_URL}
REDIS_ENABLED=true

# Yahoo Finance Rate Limiting
YAHOO_FINANCE_RATE_LIMIT=0.5
MAX_CONCURRENT_REQUESTS=3

# Optional: Logging
LOG_LEVEL=INFO

# Future: Email service (when implemented)
# RESEND_API_KEY=re_xxxxx

# Future: Database (if added)
# SUPABASE_URL=https://xxxxx.supabase.co
# SUPABASE_SERVICE_KEY=xxxxx
```

#### **4. Deploy**

Railway will automatically:
1. Build the Docker image from `Dockerfile`
2. Install dependencies from `requirements.txt`
3. Start the gunicorn server
4. Expose the service with a public URL

**First deployment takes ~3-5 minutes**

#### **5. Verify Deployment**

Test the health endpoint:
```bash
# Get your Railway URL from dashboard
curl https://your-app.railway.app/health

# Expected response:
{
  "status": "healthy",
  "timestamp": "2024-12-02T10:30:00Z",
  "version": "2.0",
  "services": {
    "api": "operational",
    "redis": "operational"
  }
}
```

Test stock analysis:
```bash
curl https://your-app.railway.app/api/analyze/HOOD

# Should return full analysis JSON
```

---

## 📁 Deployment Files

### **1. Dockerfile** (`/Dockerfile`)
- Base image: `python:3.11-slim`
- Installs: All requirements + gunicorn
- Workers: 2 (safe for Railway Hobby plan 512MB RAM)
- Timeout: 60s (Yahoo Finance can be slow)
- Healthcheck: Calls `/health` every 30s

### **2. railway.json** (`/railway.json`)
- Builder: Dockerfile
- Restart policy: ON_FAILURE (max 10 retries)
- Health check path: `/health`
- Health check timeout: 100ms

### **3. .dockerignore** (`/.dockerignore`)
- Excludes: tests, venv, .taskmaster, logs, frontend
- Keeps: src/, config.yaml, requirements.txt

### **4. requirements.txt**
- Production dependencies + gunicorn
- Development dependencies marked (not installed in Docker)

---

## 🔧 Custom Domain Setup

### **Option A: Subdomain (Recommended)**
Set up `api.stocksignal.app`:

1. **Railway Settings**:
   - Go to project → Settings → Domains
   - Click "Generate Domain" → Gets: `xxx.railway.app`
   - Click "Custom Domain" → Enter: `api.stocksignal.app`

2. **DNS Configuration** (your domain registrar):
   ```
   Type: CNAME
   Name: api
   Value: your-app.railway.app
   TTL: 3600
   ```

3. **Update CORS Origins**:
   - Add `https://api.stocksignal.app` to `ALLOWED_ORIGINS`

### **Option B: Main Domain Path**
Use `stocksignal.app/api`:

1. Deploy frontend to Vercel (Task 40)
2. Add Vercel rewrite:
   ```json
   // vercel.json
   {
     "rewrites": [
       {
         "source": "/api/:path*",
         "destination": "https://your-app.railway.app/api/:path*"
       }
     ]
   }
   ```

---

## 📊 Monitoring & Logs

### **View Logs**
```bash
# Railway CLI
railway logs

# Or: Railway Dashboard → Deployments → Click deployment → Logs
```

### **Key Metrics to Monitor**
1. **Health Check Status**: Should always return 200 OK
2. **Redis Connection**: Check `"redis": "operational"` in `/health`
3. **Response Times**: `/api/analyze/<ticker>` should be <5s
4. **Error Rate**: Monitor 429 (rate limit) and 500 errors
5. **Memory Usage**: Should stay under 400MB (Hobby plan: 512MB)

### **Log Patterns to Watch**
```bash
# Good
INFO: Redis connection available for rate limiting
INFO: Analysis completed for HOOD in 2.3s

# Warning (expected if Redis down)
WARNING: Redis unavailable - rate limiting will be disabled

# Error (needs attention)
ERROR: Failed to fetch market data for TICKER
ERROR: Redis connection failed
```

---

## 🧪 Testing in Production

### **1. Health Check**
```bash
curl https://your-app.railway.app/health
# Should return: {"status": "healthy", ...}
```

### **2. Stock Analysis (No Rate Limit)**
```bash
# Test with HOOD (known good ticker)
curl https://your-app.railway.app/api/analyze/HOOD

# Expected: Full JSON response with analysis
```

### **3. Rate Limiting (Anonymous - 3/day)**
```bash
# Make 4 requests quickly
for i in {1..4}; do
  curl -i https://your-app.railway.app/api/analyze/AAPL
  echo "\n---\n"
done

# 4th request should return 429 with friendly message
```

### **4. CORS Headers**
```bash
curl -i -X OPTIONS \
  -H "Origin: https://stocksignal.app" \
  -H "Access-Control-Request-Method: GET" \
  https://your-app.railway.app/api/analyze/HOOD

# Should include:
# Access-Control-Allow-Origin: https://stocksignal.app
# Access-Control-Expose-Headers: X-RateLimit-Limit, ...
```

---

## 🔒 Security Checklist

- ✅ CORS origins restricted to production domains
- ✅ Rate limiting enforced (3/10/unlimited tiers)
- ✅ Redis password-protected (Railway default)
- ✅ No sensitive data in logs
- ✅ HTTPS enforced (Railway default)
- ✅ Request size limited (16KB max)
- ✅ Timeout protection (60s gunicorn timeout)

---

## 💰 Cost Estimates

### **Railway Hobby Plan**
- **API Service**: $5/month
  - 512MB RAM
  - Shared CPU
  - Up to $5 free credit/month (first deploy free!)
  
- **Redis Service**: Free tier
  - 25MB storage
  - Plenty for rate limit counters
  - Upgrade if needed: $1/month for 100MB

### **Total Monthly Cost**: ~$5 (or $0 with free credit!)

---

## 🐛 Troubleshooting

### **Deployment Fails**
```bash
# Check build logs
railway logs --deployment

# Common issues:
# 1. Missing dependencies → Check requirements.txt
# 2. Port binding error → Railway auto-provides $PORT
# 3. Import errors → Run: pip install -e .
```

### **Health Check Fails**
```bash
# Check if app is running
railway status

# Check logs for startup errors
railway logs | grep ERROR

# Test locally first:
docker build -t pe-scanner-api .
docker run -p 8000:8000 -e PORT=8000 pe-scanner-api
curl http://localhost:8000/health
```

### **Redis Connection Errors**
```bash
# Verify REDIS_URL is set
railway variables

# Check Redis service status
# Railway Dashboard → Redis service → Logs

# Fallback: API works without Redis (degraded mode)
# Rate limiting will be disabled but API functional
```

### **Slow Response Times**
```bash
# Check Yahoo Finance delays
# Monitor logs for "Fetching market data" duration

# Adjust rate limiting if needed:
railway variables set YAHOO_FINANCE_RATE_LIMIT=0.5
railway variables set MAX_CONCURRENT_REQUESTS=2
```

### **CORS Errors**
```bash
# Verify ALLOWED_ORIGINS includes your frontend
railway variables get ALLOWED_ORIGINS

# Add if missing:
railway variables set ALLOWED_ORIGINS=https://stocksignal.app,https://www.stocksignal.app
```

---

## 🔄 Continuous Deployment

Railway automatically redeploys on git push:

1. **Automatic Triggers**:
   - Push to `main` branch → Auto-deploy
   - Can configure branch in Railway settings

2. **Manual Deploy**:
   ```bash
   railway up
   ```

3. **Rollback** (if needed):
   - Railway Dashboard → Deployments → Select previous deployment → "Redeploy"

---

## 📈 Scaling Considerations

### **Current Setup (Hobby Plan)**
- **Capacity**: ~100-500 requests/hour
- **Bottleneck**: Yahoo Finance rate limit (2 req/sec)
- **Users**: Supports 50-100 active users

### **When to Upgrade**

**Upgrade to Pro Plan ($20/month) when:**
- Consistently >500 requests/hour
- Need more memory (current: 512MB)
- Want faster response times

**Horizontal Scaling (Multiple Instances):**
- Redis coordination already implemented ✅
- Rate limiting works across instances ✅
- Just add more Railway services (load balanced automatically)

---

## ✅ Post-Deployment Checklist

After Railway deployment:

- [ ] Health endpoint returns 200 OK
- [ ] `/api/analyze/HOOD` returns valid JSON
- [ ] Redis connection operational (check `/health`)
- [ ] Rate limiting works (test 4 requests)
- [ ] CORS headers present
- [ ] Response time <5s per ticker
- [ ] Logs show no errors
- [ ] Custom domain configured (if using)
- [ ] Frontend can connect (once deployed)
- [ ] Update `.env` in frontend with Railway URL

---

## 📝 Next Steps After Deployment

1. **Task 40**: Deploy Next.js frontend to Vercel
2. **Update Frontend**: Set `NEXT_PUBLIC_API_URL` to Railway URL
3. **Test Integration**: Verify frontend → backend communication
4. **Monitor**: Watch Railway logs for first 24 hours
5. **Optimize**: Adjust gunicorn workers if needed

---

## 🆘 Support

- **Railway Docs**: https://docs.railway.app
- **Railway Discord**: https://discord.gg/railway
- **StockSignal Issues**: Check logs first, then create GitHub issue

---

**Deployment Status**: ✅ Ready for Railway!  
**Estimated Setup Time**: 15-20 minutes  
**First Deploy**: Free with Railway credits 🎉


