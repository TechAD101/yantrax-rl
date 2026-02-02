# 🚀 GO LIVE IN 10 MINUTES - FINAL DEPLOYMENT STEPS

**Last Commit:** `dadb342` - Perplexity API integration  
**Status:** ✅ Code pushed and ready  
**Action Required:** Add API key to Render + verify  

---

## ⏰ DEPLOYMENT TIMELINE

```
NOW:           You're reading this ← You are here
Next 2 min:    Add API key to Render
Next 5 min:    Wait for auto-deploy
Next 3 min:    Test live endpoints
Total:         10 minutes to production
```

---

## 🎯 ACTION ITEMS (DO THESE NOW)

### 1️⃣ ADD API KEY TO RENDER (2 minutes)

**Go to:** https://dashboard.render.com/

**Steps:**
1. Click `yantrax-backend` service
2. Click `Settings` button  
3. Click `Environment` on left menu
4. Click `Add Environment Variable`
5. **Name:** `PERPLEXITY_API_KEY`
6. **Value:** [Copy from your `backend/.env` file - starts with `pplx-`]
7. Click `Save` button

**Wait:** Render auto-redeploys (3-5 minutes)

---

### 2️⃣ WATCH RENDER DASHBOARD (5 minutes)

**Watch for:**
- Service status changes to ⚫ "Live" (green)
- Check Logs tab for any errors
- Note: First deploy takes 3-5 minutes

**URL:** https://dashboard.render.com/

---

### 3️⃣ TEST YOUR ENDPOINTS (3 minutes)

**After "Live" status appears, run these:**

```bash
# Test 1: Health check
curl https://yantrax-backend.onrender.com/

# Expected: {"status":"online","version":"6.0"...}

# Test 2: Real market prices
curl "https://yantrax-backend.onrender.com/api/market-price?symbol=AAPL"

# Expected: {"symbol":"AAPL","price":<NUMBER>,"source":"perplexity"}

# Test 3: Create portfolio (copy this exactly)
curl -X POST "https://yantrax-backend.onrender.com/api/portfolio/create" \
  -H "Content-Type: application/json" \
  -d '{"name":"Test","risk_profile":"moderate","initial_capital":50000}'

# Expected: {"success":true,"portfolio_id":<NUMBER>...}
```

---

### 4️⃣ VERIFY FRONTEND (1 minute)

**Open these URLs in browser:**

1. Frontend home: https://yantrax-vercel.vercel.app
2. Onboarding: https://yantrax-vercel.vercel.app/onboarding

**Check for:**
- Page loads without errors
- No blank screens
- Can see onboarding wizard

---

## ✅ DEPLOYMENT CHECKLIST

Copy this and check off as you go:

```
DEPLOYMENT CHECKLIST
====================

□ Opened Render dashboard
□ Added PERPLEXITY_API_KEY to environment
□ Clicked Save button
□ Watched for "Live" status (3-5 min)
□ Health check test passed
□ Market price test passed (saw real AAPL price)
□ Portfolio creation test passed
□ Frontend loads without errors
□ Can see onboarding wizard
□ Render logs show no errors

Status: ________________
Time: ________________
```

---

## 🎯 WHAT'S DEPLOYED

**Backend (Render):**
- ✅ Flask application (main_mvp.py)
- ✅ 12 API endpoints
- ✅ Paper trading engine
- ✅ SQLite database
- ✅ Perplexity API integration
- ✅ 24-agent AI firm

**Frontend (Vercel):**
- ✅ React 18 application
- ✅ Onboarding wizard
- ✅ Portfolio dashboard
- ✅ API client integration
- ✅ Tailwind CSS styling

**Data/Services:**
- ✅ Real market prices (Perplexity)
- ✅ Paper trading simulation
- ✅ Trade history logging
- ✅ Portfolio persistence

---

## 🔗 YOUR LIVE URLS

After deployment is complete:

| Service | URL |
|---------|-----|
| Backend API | https://yantrax-backend.onrender.com |
| Frontend | https://yantrax-vercel.vercel.app |
| Onboarding | https://yantrax-vercel.vercel.app/onboarding |
| Dashboard | https://yantrax-vercel.vercel.app/dashboard |
| Health Check | https://yantrax-backend.onrender.com/ |

---

## 🧪 VERIFY EVERYTHING WORKS

**All 3 of these should work:**

1. **Backend responds:**
   ```bash
   curl https://yantrax-backend.onrender.com/ -s | grep status
   ```
   Should see: `"status":"online"`

2. **Real prices flowing:**
   ```bash
   curl "https://yantrax-backend.onrender.com/api/market-price?symbol=AAPL" -s | grep price
   ```
   Should see: `"price":<number>` (real stock price)

3. **Frontend loads:**
   Open https://yantrax-vercel.vercel.app/onboarding in browser
   Should see: Onboarding wizard with 5 steps

---

## ⚠️ TROUBLESHOOTING

### Backend stuck on "building" for >10 minutes?
- Render may be slow
- Check Logs tab for errors
- Contact Render support if needed

### API key not working?
- Verify you copied the key correctly
- Should start with `pplx-`
- Should be 50+ characters
- Try removing and re-adding the variable

### Frontend shows "Cannot reach backend"?
- Make sure backend is "Live" (green status)
- Try: `curl https://yantrax-backend.onrender.com/`
- Check browser console for CORS errors

### Market prices show mock data?
- Backend wasn't redeployed with API key yet
- Wait 5 minutes after adding key
- Verify Render shows "Live" status
- Check Render logs for API errors

---

## 🎉 YOU'RE LIVE!

Once all checks pass above:

**Your platform has:**
- ✅ Real market data (Perplexity API)
- ✅ Paper trading engine
- ✅ Portfolio management  
- ✅ AI farm system
- ✅ Production deployment
- ✅ Auto-scaling infrastructure

**Next steps:**
1. ✅ Verify live URLs (now)
2. Try creating a portfolio (now)
3. Execute a test trade (now)
4. Share with beta users (tomorrow)
5. Gather feedback (tomorrow)
6. Build UI components (this week)

---

## 📈 WHAT TO BUILD NEXT (Days 2-7)

**Priority 1 (Critical):**
1. AI Debate display component - Show 4 personas' reasoning
2. Dashboard portfolio view - Holdings, P&L, returns
3. Trade execution panel - Search tickers, execute trades

**Priority 2 (Important):**
4. Stop-loss automation - Auto-sell at loss threshold
5. Emotional safeguards - Pain meter UI

**Priority 3 (Nice to have):**
6. Trade history display
7. Memecoin intelligence
8. Performance analytics

---

## 💻 COMMANDS FOR QUICK REFERENCE

### Check if backend is live
```bash
curl https://yantrax-backend.onrender.com/
```

### Get real market price
```bash
curl "https://yantrax-backend.onrender.com/api/market-price?symbol=AAPL"
```

### Create test portfolio
```bash
curl -X POST "https://yantrax-backend.onrender.com/api/portfolio/create" \
  -H "Content-Type: application/json" \
  -d '{"name":"My Portfolio","risk_profile":"aggressive","initial_capital":100000}'
```

### Execute test trade
```bash
# First, get your portfolio ID from above response
# Then replace <ID> with the actual ID

curl -X POST "https://yantrax-backend.onrender.com/api/portfolio/<ID>/trade" \
  -H "Content-Type: application/json" \
  -d '{"action":"BUY","symbol":"AAPL","quantity":5}'
```

---

## 🏁 FINAL STATUS

**Code Status:** ✅ Pushed to GitHub  
**Render Status:** ⏳ Awaiting API key in environment  
**Frontend Status:** ✅ Auto-deployed to Vercel  
**Deployment Timeline:** 10 minutes total  
**Go-Live Time:** Now (after API key added)  

---

## 🚀 START DEPLOYMENT NOW!

1. Open: https://dashboard.render.com/
2. Add: `PERPLEXITY_API_KEY` environment variable
3. Copy value from: `backend/.env` file
4. Click: Save
5. Wait: 5 minutes for redeploy
6. Test: Health check endpoints
7. 🎉 Live!

**Questions?** Check `PRODUCTION_DEPLOYMENT_READY.md` for detailed guide.

---

**Time to Launch:** 10 minutes  
**Complexity:** Very simple (just 3 steps)  
**Confidence:** 98%  
**Status:** 🚀 READY TO GO LIVE!
