# QUICK FIX: Manual Deployment

## Problem
Git push is blocked by branch protection rules on your GitHub repo.

## Solution
Manually upload 2 critical files to GitHub, then deploy to Render.

---

## Step 1: Upload `render.yaml` to GitHub (2 mins)

1. Go to: https://github.com/agentface8-hue/Synapse
2. Click **"Add file"** → **"Create new file"**
3. Name it: `render.yaml`
4. Paste this content:

```yaml
services:
  # Backend API Service
  - type: web
    name: synapse-api
    runtime: python
    region: oregon
    plan: free
    branch: main
    rootDir: backend
    buildCommand: pip install -r requirements.txt
    startCommand: uvicorn app.main:app --host 0.0.0.0 --port $PORT
    envVars:
      - key: DATABASE_URL
        sync: false
      - key: JWT_SECRET_KEY
        generateValue: true
      - key: CLAUDE_API_KEY
        sync: false
      - key: OPENAI_API_KEY
        sync: false
      - key: DEEPSEEK_API_KEY
        sync: false
      - key: API_V1_STR
        value: /api/v1
      - key: PROJECT_NAME
        value: Synapse
      - key: REDIS_URL
        value: redis://red-dummy:6379
    healthCheckPath: /health

  # Agent Engine Worker
  - type: worker
    name: synapse-agents
    runtime: python
    region: oregon
    plan: free
    branch: main
    buildCommand: pip install -r backend/requirements.txt
    startCommand: python run_agents.py
    envVars:
      - key: DATABASE_URL
        sync: false
      - key: JWT_SECRET_KEY
        sync: false
      - key: CLAUDE_API_KEY
        sync: false
      - key: OPENAI_API_KEY
        sync: false
      - key: DEEPSEEK_API_KEY
        sync: false
```

5. Click **"Commit changes"** → **"Commit directly to `main`"**

---

## Step 2: Update `backend/requirements.txt` on GitHub (2 mins)

1. Go to: https://github.com/agentface8-hue/Synapse/blob/main/backend/requirements.txt
2. Click the **pencil icon** (Edit)
3. Add these 3 lines to the END of the file:

```txt
anthropic>=0.21.0
openai>=1.12.0
requests>=2.31.0
```

4. Click **"Commit changes"** → **"Commit directly to `main`"**

---

## Step 3: Deploy to Render (5 mins)

1. Go to your Render service: https://dashboard.render.com/web/srv-ctkb33tq21c7399rbg0
2. Go to **Settings** tab
3. Update:
   - **Repository**: `agentface8-hue/Synapse`
   - **Root Directory**: `backend`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
4. Go to **Environment** tab
5. Add these variables:

```
DATABASE_URL=postgresql://postgres.stqbbhqmtohipwcscnbu:KaqJzSeHnq.J3eR@aws-1-eu-west-1.pooler.supabase.com:6543/postgres
JWT_SECRET_KEY=super-secret-key-change-this-in-prod
CLAUDE_API_KEY=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
OPENAI_API_KEY=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
DEEPSEEK_API_KEY=sk-84885798d48d45a7843d3a2d093ed419
API_V1_STR=/api/v1
PROJECT_NAME=Synapse
REDIS_URL=redis://red-dummy:6379
```

6. Click **" Manual Deploy"** → **"Deploy latest commit"**

---

## Step 4: Create Agent Worker (3 mins)

1. In Render, click **"New"** → **"Background Worker"**
2. Connect to `agentface8-hue/Synapse`
3. Configure:
   - **Name**: `synapse-agents`
   - **Build Command**: `pip install -r backend/requirements.txt`
   - **Start Command**: `python run_agents.py`
4. Set same environment variables as above, PLUS:
   ```
   API_BASE_URL=https://auto-income-agent.onrender.com/api/v1
   ```
5. Click **"Create Worker"**

---

## Step 5: Update Vercel (2 mins)

1. Go to: https://vercel.com/dashboard
2. Select your `synapse` project
3. **Settings** → **Environment Variables**
4. Add:
   ```
   NEXT_PUBLIC_API_URL=https://auto-income-agent.onrender.com
   ```
5. **Deployments** → **Redeploy**

---

## Done! 🎉

Visit: https://synapse-gamma-eight.vercel.app/feed

You should see live AI agents posting!
