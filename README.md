# ⚛ Plasma Intelligence

> An automated, self-updating research intelligence platform for plasma physics — delivering daily newspaper-style digests, subfield deep-dives, living literature reviews, and open-problem tracking across 18 journals.

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

---

## What it does

| Feature | Description |
|---|---|
| **Daily Newspaper** | Every morning at 02:00 UTC, fetches yesterday's papers, analyzes each with Claude, and presents them as a beautiful newspaper-style digest with headlines, summaries, and extracted figures |
| **Subfield Pages** | 18 subfield pages (tokamak, magnetic reconnection, two-stream instability, etc.) each showing 6 months of papers with full AI analysis |
| **Living Literature Reviews** | One review per subfield, starting from founding papers and auto-appending daily. Historical backbone seeded once with Claude Opus |
| **Open Problems Tracker** | Extracts open research questions from every paper, clusters them weekly, ranks by urgency |
| **Figure Extraction** | Downloads PDFs, extracts all figures, describes them with Claude Vision, displays inline |

## Architecture

```
arXiv API + NASA ADS + Semantic Scholar
          ↓
  FastAPI backend + APScheduler (daily 02:00 UTC)
          ↓
  PyMuPDF (figures) + Claude API (analysis)
          ↓
  PostgreSQL + pgvector
          ↓
  Next.js 14 frontend (Vercel)
```

## Quick Start

### Prerequisites
- Python 3.12+
- Node.js 20+
- Docker + Docker Compose (recommended)
- An Anthropic API key
- (Optional) NASA ADS token for journal-specific metadata

### 1. Clone & configure

```bash
git clone https://github.com/YOUR_USERNAME/plasma-intelligence.git
cd plasma-intelligence
cp .env.example .env
# Edit .env and add your ANTHROPIC_API_KEY
```

### 2. Start with Docker Compose

```bash
docker compose up -d
```

This starts PostgreSQL, the FastAPI backend, and the Next.js frontend.

- Frontend: http://localhost:3000
- API docs: http://localhost:8000/docs

### 3. Seed the literature reviews (one-time, ~$5-8)

```bash
cd backend
pip install -r requirements.txt
python ../scripts/seed_literature.py
```

This generates the historical literature review backbone for all 18 subfields using Claude Opus.

### 4. Backfill recent papers

```bash
python ../scripts/backfill.py --months 3
```

### 5. Test the pipeline with one paper

```bash
python ../scripts/test_pipeline.py
```

---

## Manual Setup (without Docker)

### Backend

```bash
cd backend
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
# make sure PostgreSQL is running and DATABASE_URL is set in .env
uvicorn main:app --reload --port 8000
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

---

## Deployment

### Backend → Railway

```bash
npm install -g @railway/cli
railway login
railway new
railway up          # from the backend/ directory
# Add PostgreSQL plugin in Railway dashboard
# Set all env vars in Railway settings
```

### Frontend → Vercel

```bash
cd frontend
npx vercel
# Set NEXT_PUBLIC_API_URL to your Railway backend URL
```

---

## Environment Variables

| Variable | Required | Description |
|---|---|---|
| `ANTHROPIC_API_KEY` | ✅ | Your Anthropic API key |
| `DATABASE_URL` | ✅ | PostgreSQL connection string |
| `NASA_ADS_TOKEN` | Recommended | Extends coverage to all 18 journals |
| `ADMIN_TOKEN` | Recommended | Token for manual pipeline triggers |
| `R2_ACCOUNT_ID` | Optional | Cloudflare R2 for figure storage |
| `R2_ACCESS_KEY_ID` | Optional | R2 access key |
| `R2_SECRET_ACCESS_KEY` | Optional | R2 secret |
| `R2_BUCKET_NAME` | Optional | R2 bucket name |
| `R2_PUBLIC_URL` | Optional | Public CDN URL for figures |
| `NEXT_PUBLIC_API_URL` | ✅ | Backend URL for the frontend |

Without R2 credentials, figures are saved locally to `backend/static/figures/`.

---

## Daily Cost Estimate

| Operation | Volume | Model | Cost/day |
|---|---|---|---|
| Paper analysis | ~80 papers | Sonnet | ~$0.60 |
| Figure description | ~40 figures | Sonnet (vision) | ~$0.30 |
| Lit review patches | ~80 patches | Sonnet | ~$0.20 |
| Open problem extract | ~80 papers | Sonnet | ~$0.10 |
| Weekly synthesis | 1×/week | Opus | ~$0.20/week |
| **Total** | | | **~$1.25/day** |

Historical seed (one-time): ~$5–8 for all 18 subfields.

---

## Journals Covered

- The Astrophysical Journal (ApJ / ApJL / ApJS)
- Journal of Geophysical Research: Space Physics
- Geophysical Research Letters
- Monthly Notices of the Royal Astronomical Society
- Astronomy & Astrophysics
- Space Science Reviews
- Solar Physics
- Advances in Space Research
- Physics of Plasmas
- Journal of Plasma Physics
- Plasma Physics and Controlled Fusion
- Nuclear Fusion
- Physical Review Letters
- Physical Review E
- Reviews of Modern Physics
- arXiv (physics.plasm-ph, astro-ph.SR, astro-ph.HE, physics.space-ph, nucl-th)

---

## API Endpoints

```
GET  /api/papers/today              Daily newspaper papers
GET  /api/papers/date/{YYYY-MM-DD}  Papers for a specific date
GET  /api/papers/{id}               Full paper detail
GET  /api/papers/                   List with filters

GET  /api/subfields/                All subfields
GET  /api/subfields/{slug}          Subfield paper feed

GET  /api/literature/               All literature reviews (metadata)
GET  /api/literature/{subfield}     Full literature review markdown

GET  /api/open-problems/clusters    Synthesized open problem clusters
GET  /api/open-problems/raw         Raw extracted problems

POST /api/pipeline/run-daily        Trigger daily job manually
POST /api/pipeline/seed-literature/{subfield}  Seed one review
POST /api/pipeline/analyze-paper    Analyze a single arXiv paper
```

All POST endpoints require `X-Admin-Token` header.

---

## License

MIT — see [LICENSE](LICENSE)

---

*Plasma Intelligence is an independent research tool. It is not affiliated with any journal publisher. All paper content remains the property of its respective authors and publishers.*
