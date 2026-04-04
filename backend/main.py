"""
FastAPI application entrypoint for the Plasma Intelligence Platform.
"""
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pathlib import Path

from database import create_tables
from scheduler import start_scheduler, shutdown_scheduler
from api import papers, subfields, lit_reviews, open_problems, pipeline

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting Plasma Intelligence Platform...")
    await create_tables()
    start_scheduler()
    yield
    shutdown_scheduler()
    logger.info("Shutdown complete.")


app = FastAPI(
    title="Plasma Intelligence API",
    description="Automated plasma physics research aggregation and synthesis",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve locally stored figures in dev
static_dir = Path("static")
static_dir.mkdir(exist_ok=True)
app.mount("/static", StaticFiles(directory="static"), name="static")

# Routers
app.include_router(papers.router, prefix="/api/papers", tags=["papers"])
app.include_router(subfields.router, prefix="/api/subfields", tags=["subfields"])
app.include_router(lit_reviews.router, prefix="/api/literature", tags=["literature"])
app.include_router(open_problems.router, prefix="/api/open-problems", tags=["open-problems"])
app.include_router(pipeline.router, prefix="/api/pipeline", tags=["pipeline"])


@app.get("/health")
async def health():
    return {"status": "ok", "service": "plasma-intelligence"}
