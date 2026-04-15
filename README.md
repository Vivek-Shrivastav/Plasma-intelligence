# ⚛ Plasma Intelligence

![Free Stack](https://img.shields.io/badge/cost-$0%2Fday-brightgreen)
![Powered by Gemini](https://img.shields.io/badge/AI-Gemini%202.0%20Flash-blue)
![License](https://img.shields.io/badge/license-MIT-green)

**Automated daily research intelligence for plasma physics.** Every morning, Plasma Intelligence fetches new papers from arXiv and Semantic Scholar, analyzes them with Gemini 2.0 Flash, extracts figures, maintains living literature reviews across 18 subfields, and identifies open research problems — all for **$0.00/day**.

---

## Features

| Feature | Description |
|---------|-------------|
| 📰 **Daily Paper Digest** | Headlines + summaries for every new plasma physics paper |
| 🔬 **Deep Analysis** | Structured analysis: methodology, significance, key findings, open questions |
| 📊 **Figure Extraction** | Automatically extracts and describes figures from PDFs |
| 📚 **Literature Reviews** | Living, self-updating literature reviews for 18 subfields |
| ❓ **Open Problems** | Extracts and clusters unsolved research questions across the field |
| 🔍 **Semantic Search** | Vector similarity search across all analyzed papers |
| 📈 **Importance Scoring** | AI-rated importance score (1-10) for every paper |

## Architecture

```
arXiv API + Semantic Scholar API
        ↓
FastAPI backend + APScheduler (daily 02:00 UTC)
        ↓
PyMuPDF (figures) + Gemini 2.0 Flash API (analysis)
        ↓
Supabase PostgreSQL + pgvector
        ↓
Next.js 14 frontend
```

## Journals & Sources Covered

**arXiv Categories:** physics.plasm-ph, astro-ph.SR, astro-ph.HE, physics.space-ph, nucl-th

**Via Semantic Scholar:** Physics of Plasmas, Journal of Plasma Physics, Nuclear Fusion, Physical Review Letters, Physical Review E, Plasma Physics and Controlled Fusion, The Astrophysical Journal, Journal of Geophysical Research, and more.

## 18 Subfields Tracked

Magnetic Reconnection · Plasma Turbulence · Two-Stream Instability · Tokamak Physics · Stellarator Physics · Solar Wind Plasma · Magnetospheric Physics · MHD Waves · Kinetic Effects · Plasma Heating · Plasma Confinement · Plasma Transport · Collisionless Shocks · Accretion Disk Plasma · PIC Simulations · Drift Waves · Plasma Instabilities · Plasma Diagnostics

## Prerequisites

- Python 3.12+
- Node.js 20+
- Docker + Docker Compose
- Free Gemini API key → [aistudio.google.com](https://aistudio.google.com/app/apikey)
- Free Supabase account → [supabase.com](https://supabase.com)

## Quick Start

See **[SETUP.md](SETUP.md)** for complete step-by-step instructions.

```bash
# 1. Clone and configure
git clone https://github.com/Vivek-Shrivastav/Plasma-intelligence.git
cd Plasma-intelligence
cp .env.example .env
# Edit .env with your keys

# 2. Start
docker compose up -d

# 3. Test
cd backend && python ../scripts/test_pipeline.py
```

## Daily Cost Estimate

| Operation | Volume | Model | Cost/day |
|-----------|--------|-------|----------|
| Paper analysis | ~80 papers | Gemini 2.0 Flash | $0.00 |
| Figure description | ~40 figs | Gemini 2.0 Flash | $0.00 |
| Literature review patches | ~80 | Gemini 2.0 Flash | $0.00 |
| Open problems extraction | ~80 | Gemini 2.0 Flash | $0.00 |
| **Total** | | | **$0.00/day** |

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/papers` | GET | List papers (filterable by date, subfield, importance) |
| `/api/papers/{id}` | GET | Full paper details + analysis |
| `/api/subfields` | GET | List all 18 subfields with stats |
| `/api/subfields/{slug}` | GET | Subfield details + recent papers |
| `/api/literature/{slug}` | GET | Literature review for a subfield |
| `/api/open-problems` | GET | Clustered open problems |
| `/api/pipeline/trigger` | POST | Manually trigger the daily pipeline |
| `/health` | GET | Health check |

## Tech Stack

- **Backend:** Python 3.12, FastAPI, APScheduler, PyMuPDF
- **AI:** Google Gemini 2.0 Flash (free tier)
- **Database:** Supabase PostgreSQL + pgvector
- **Frontend:** Next.js 14, React 18, TailwindCSS
- **Paper Sources:** arXiv API, Semantic Scholar API

## License

MIT
