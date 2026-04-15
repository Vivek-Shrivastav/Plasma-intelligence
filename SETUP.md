# Plasma Intelligence — Free Stack Setup Guide

## What You Need (Both Free, No Credit Card)
1. A Google account → Gemini API key
2. A GitHub account → Supabase account (sign in with GitHub)

## Step 1 — Get Your Free Gemini API Key (2 minutes)
1. Go to https://aistudio.google.com/app/apikey
2. Click "Create API key"
3. Select "Create API key in new project"
4. Copy the key

## Step 2 — Create Your Free Supabase Database (5 minutes)
1. Go to https://supabase.com and sign in with GitHub
2. Click "New Project"
3. Choose a name (e.g. "plasma-intelligence")
4. Choose a strong database password (save it!)
5. Select the region closest to you
6. Click "Create new project" and wait ~2 minutes
7. Go to Settings → Database
8. Under "Connection string" select "URI" mode
9. Copy the connection string — it looks like:
   `postgresql://postgres:[YOUR-PASSWORD]@[host].supabase.co:5432/postgres`
10. Replace `[YOUR-PASSWORD]` with the password you set in step 4

## Step 3 — Configure The App
```bash
cp .env.example .env
```
Open `.env` and fill in:
- `GEMINI_API_KEY` — from Step 1
- `DATABASE_URL` — from Step 2
- `ADMIN_TOKEN` — type any random string (e.g. "mysecrettoken123")
- `NEXT_PUBLIC_API_URL` — leave as `http://localhost:8000`

## Step 4 — Start The App
```bash
docker compose up -d
```
Wait ~30 seconds for everything to start.

## Step 5 — Initialize The Database (first time only)
```bash
docker compose exec backend python -c "
from database import create_tables
import asyncio
asyncio.run(create_tables())
print('Database ready')
"
```

## Step 6 — Seed The Literature Reviews (one-time, ~20 minutes)
```bash
cd backend
pip install -r requirements.txt
python ../scripts/seed_literature.py
```
This runs ~20 minutes. You can watch it print progress.
Free tier handles this comfortably.

## Step 7 — Backfill Recent Papers
```bash
python ../scripts/backfill.py --months 3
```

## Step 8 — Open The App
Go to http://localhost:3000

## Step 9 — Test Everything Works
```bash
cd backend
python ../scripts/test_pipeline.py
```
Should print `PIPELINE TEST PASSED`

## Daily Operation
The app runs automatically. Every day at 02:00 UTC:
- New papers are fetched from arXiv + Semantic Scholar
- Each paper is analyzed by Gemini 2.0 Flash
- Figures are extracted and described
- Literature reviews are updated
- Open problems are extracted

Daily cost: **$0.00**
Daily Gemini API usage: ~200-400 calls (well within 1500/day free limit)

## Deploying to the Cloud (Free)

### Backend on Render (free tier)
1. Go to https://render.com and sign in with GitHub
2. Click "New" → "Web Service"
3. Connect your `Plasma-intelligence` repo
4. Set Root Directory to `backend`
5. Build Command: `pip install -r requirements.txt`
6. Start Command: `uvicorn main:app --host 0.0.0.0 --port $PORT`
7. Add environment variables: `GEMINI_API_KEY`, `DATABASE_URL`, `ADMIN_TOKEN`
8. Deploy!

### Frontend on Vercel (free tier)
1. Go to https://vercel.com and sign in with GitHub
2. Import the `Plasma-intelligence` repo
3. Set Root Directory to `frontend`
4. Add environment variable: `NEXT_PUBLIC_API_URL` = your Render backend URL
5. Deploy!

## Troubleshooting
- **Backend logs:** `docker compose logs backend`
- **Frontend logs:** `docker compose logs frontend`
- **Restart app:** `docker compose restart`
- **Full reset:** `docker compose down && docker compose up -d`
- **Rate limit errors:** The app handles these automatically with exponential backoff
