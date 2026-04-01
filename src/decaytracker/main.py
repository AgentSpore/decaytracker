"""
DecayTracker v2 — The Trust Feed.
AI-powered URL audits forming a public trust feed.
"""
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger

from .database import init_db
from .api.feed import router as feed_router
from .api.companies import router as companies_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Initializing database...")
    await init_db()
    logger.info("Database ready")
    yield
    logger.info("Shutting down")


app = FastAPI(
    title="DecayTracker",
    description="The Trust Feed — AI-powered URL audits for corporate trust scoring",
    version="2.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(feed_router)
app.include_router(companies_router)


@app.get("/health")
async def health():
    return {"status": "ok", "service": "decaytracker", "version": "2.0.0"}
