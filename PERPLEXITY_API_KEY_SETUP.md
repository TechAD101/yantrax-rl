# 🔑 Perplexity API Setup Guide

## What You Need
- Your **Perplexity API Key** (format: `pplx-...`)

## How to Get It

### Step 1: Visit Perplexity API Console
Go to: **https://www.perplexity.ai/account/api/keys**

### Step 2: Create API Key
1. Click **"Create API Key"** button
2. Copy the generated key (starts with `pplx-`)
3. **DO NOT SHARE** this key publicly

### Step 3: Store It Securely

**For Local Development:**
1. In this terminal, run:
```bash
cd /workspaces/yantrax-rl
echo "PERPLEXITY_API_KEY=pplx-YOUR_KEY_HERE" >> .env
```

Replace `pplx-YOUR_KEY_HERE` with your actual key

**For Render Deployment:**
1. Go to: https://dashboard.render.com/
2. Select "yantrax-backend" service
3. Click **Settings** → **Environment**
4. Add new variable:
   - **Name:** `PERPLEXITY_API_KEY`
   - **Value:** `pplx-YOUR_KEY_HERE`
5. Click **Save**

## Verification

To test your key works:

```bash
curl -X POST "https://api.perplexity.ai/chat/completions" \
  -H "Authorization: Bearer pplx-YOUR_KEY_HERE" \
  -H "Content-Type: application/json" \
  -d '{"model": "sonar-pro", "messages": [{"role": "user", "content": "What is the current price of AAPL stock?"}]}'
```

Expected response: Market data about Apple stock

## Status

- [ ] API Key Generated
- [ ] Local .env Updated
- [ ] Render Environment Variable Added
- [ ] Test Request Successful

**⏭️ Next:** Once set, run deployment steps in `DEPLOYMENT_READY.md`
