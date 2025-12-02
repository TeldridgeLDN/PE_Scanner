# 🚀 Deploy PE Scanner Backend to Railway - Quick Start

**Time**: 15 minutes | **Cost**: $5/month (FREE with Railway credits!)

---

## Step 1: Create Railway Project (3 min)

1. Go to **https://railway.app/new**
2. Click **"Deploy from GitHub repo"**
3. Select your **PE_Scanner** repository
4. Railway auto-detects Python and uses Nixpacks ✅

**Note**: Railway will automatically use the `Procfile` or `railway.json` start command

---

## Step 2: Add Redis Service (2 min)

1. In Railway project dashboard, click **"+ New"**
2. Select **"Database"** → **"Redis"**
3. Done! Railway automatically creates `REDIS_URL` ✅

---

## Step 3: Set Environment Variables (5 min)

In Railway → **Variables** tab, add these:

```bash
FLASK_ENV=production
ALLOWED_ORIGINS=https://pe-scanner.com,https://www.pe-scanner.com,http://localhost:3000
REDIS_ENABLED=true
YAHOO_FINANCE_RATE_LIMIT=0.5
MAX_CONCURRENT_REQUESTS=3
LOG_LEVEL=INFO
```

**Note**: `PORT` and `REDIS_URL` are auto-provided by Railway ✅

---

## Step 4: Deploy! (3-5 min)

Railway automatically:
- ✅ Builds Docker image
- ✅ Installs dependencies  
- ✅ Starts gunicorn server
- ✅ Provides a public URL

**Wait for**: "Deployment successful" notification

---

## Step 5: Test (2 min)

Get your Railway URL from the dashboard, then:

```bash
# Health check
curl https://your-app.railway.app/health
# Should return: {"status": "healthy", "services": {"api": "operational", "redis": "operational"}}

# Stock analysis
curl https://your-app.railway.app/api/analyze/HOOD
# Should return: Full JSON analysis
```

---

## ✅ Success!

Your API is live at: `https://your-app.railway.app`

---

## Next Steps

1. **Optional**: Configure custom domain `api.pe-scanner.com`
   - Railway Settings → Domains → Custom Domain
   - Add CNAME: `api` → `your-app.railway.app`

2. **Deploy Frontend** (Task 40): Deploy Next.js to Vercel
   - Set `NEXT_PUBLIC_API_URL=https://your-app.railway.app`

3. **Monitor**: Check Railway logs for any errors

---

## Need Help?

📖 **Full Guide**: See `RAILWAY_DEPLOYMENT.md`  
💬 **Railway Discord**: https://discord.gg/railway  
🐛 **Issues**: Check logs in Railway dashboard

---

**Cost**: ~$5/month (or $0 with free Railway credits) 🎉

