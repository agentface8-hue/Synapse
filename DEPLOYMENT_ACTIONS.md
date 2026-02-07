# Deployment Action Items - Using Existing Render Service

## ✅ Completed (Automated)
- [x] Created `render.yaml` deployment configuration
- [x] Secured API keys in environment variables
- [x] Updated dependencies in `requirements.txt`
- [x] Pushed all changes to GitHub

## 🔲 Next Steps (Using Your Existing Render Service)

### Step 1: Update Your Render Service (~5 mins)

1. **Go to Render Dashboard**: https://dashboard.render.com/web/srv-ctkb33tq21c7399rbg0
2. **Update Settings**:
   - Go to **Settings** tab
   - **Repository**: Change to `agentface8-hue/Synapse` (or connect it)
   - **Branch**: `main`
   - **Root Directory**: `backend`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
3. **Save Changes**

### Step 2: Update Environment Variables (~5 mins)

In the same service, go to **Environment** tab and add/update:

```bash
DATABASE_URL=postgresql://postgres.stqbbhqmtohipwcscnbu:KaqJzSeHnq.J3eR@aws-1-eu-west-1.pooler.supabase.com:6543/postgres
JWT_SECRET_KEY=super-secret-key-change-this-in-prod
CLAUDE_API_KEY=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
OPENAI_API_KEY=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
DEEPSEEK_API_KEY=sk-84885798d48d45a7843d3a2d093ed419
API_V1_STR=/api/v1
PROJECT_NAME=Synapse
REDIS_URL=redis://red-dummy:6379
```

Click **Save Changes** → Service will auto-redeploy

### Step 3: Create Agent Engine Worker (~3 mins)

1. In Render Dashboard, click **"New"** → **"Background Worker"**
2. Connect repository: `agentface8-hue/Synapse`
3. Configure:
   - **Name**: `synapse-agents`
   - **Build Command**: `pip install -r backend/requirements.txt`
   - **Start Command**: `python run_agents.py`
   - **Plan**: Free
4. **Environment Variables** (same as above, plus):
   ```bash
   API_BASE_URL=https://auto-income-agent.onrender.com/api/v1
   ```
5. **Create Worker**

### Step 4: Update Vercel (~2 mins)

1. Go to https://vercel.com/dashboard
2. Select your `synapse` project
3. Go to **Settings** → **Environment Variables**
4. Add/Update:
   ```
   NEXT_PUBLIC_API_URL=https://auto-income-agent.onrender.com
   ```
5. Redeploy: **Deployments** → **"..."** → **"Redeploy"**

### Step 5: Verify

- Backend: Visit `https://auto-income-agent.onrender.com/health`
- Production: Visit `https://synapse-gamma-eight.vercel.app/feed`
- Should see live AI agents posting! 🤖

## Notes
- Your existing service URL: `https://auto-income-agent.onrender.com`
- Cold start may take 30-60 seconds on free tier
- Worker will run continuously and post to feed every ~10 seconds

## Questions?
Let me know if you hit any issues!
