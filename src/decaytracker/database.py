"""
Database initialization and connection management.
DecayTracker v2 "The Trust Feed" — aiosqlite + WAL mode.
"""
import json
import os
from typing import AsyncGenerator

import aiosqlite
from loguru import logger

DB_PATH = os.getenv("DB_PATH", "/tmp/decaytracker.db")


async def get_db() -> AsyncGenerator[aiosqlite.Connection, None]:
    """FastAPI dependency — yields DB connection, closes on request completion."""
    db = await aiosqlite.connect(DB_PATH)
    db.row_factory = aiosqlite.Row
    await db.execute("PRAGMA journal_mode=WAL")
    await db.execute("PRAGMA foreign_keys=ON")
    try:
        yield db
    finally:
        await db.close()


async def init_db() -> None:
    """Create tables, indexes, and seed initial data."""
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        await db.execute("PRAGMA journal_mode=WAL")
        await db.execute("PRAGMA foreign_keys=ON")

        await db.executescript("""
            CREATE TABLE IF NOT EXISTS companies (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                slug TEXT UNIQUE NOT NULL,
                domain TEXT UNIQUE NOT NULL,
                category TEXT NOT NULL DEFAULT 'other',
                description TEXT NOT NULL DEFAULT '',
                logo_url TEXT NOT NULL DEFAULT '',
                trust_score REAL NOT NULL DEFAULT 50.0,
                total_audits INTEGER NOT NULL DEFAULT 0,
                trend_30d REAL NOT NULL DEFAULT 0.0,
                top_findings TEXT NOT NULL DEFAULT '[]',
                created_at TEXT NOT NULL DEFAULT (datetime('now')),
                updated_at TEXT NOT NULL DEFAULT (datetime('now'))
            );

            CREATE TABLE IF NOT EXISTS audits (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                company_id INTEGER NOT NULL REFERENCES companies(id),
                url TEXT NOT NULL,
                platform TEXT NOT NULL DEFAULT 'website',
                title TEXT NOT NULL,
                subtitle TEXT NOT NULL DEFAULT '',
                trust_score INTEGER NOT NULL DEFAULT 50,
                severity TEXT NOT NULL DEFAULT 'neutral',
                ai_summary TEXT NOT NULL DEFAULT '',
                metadata TEXT NOT NULL DEFAULT '{}',
                status TEXT NOT NULL DEFAULT 'pending',
                views INTEGER NOT NULL DEFAULT 0,
                created_at TEXT NOT NULL DEFAULT (datetime('now'))
            );

            CREATE TABLE IF NOT EXISTS findings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                audit_id INTEGER NOT NULL REFERENCES audits(id) ON DELETE CASCADE,
                type TEXT NOT NULL,
                severity TEXT NOT NULL DEFAULT 'warning',
                title TEXT NOT NULL,
                description TEXT NOT NULL DEFAULT '',
                evidence_url TEXT NOT NULL DEFAULT '',
                confidence REAL NOT NULL DEFAULT 0.5
            );

            CREATE INDEX IF NOT EXISTS idx_audits_company ON audits(company_id);
            CREATE INDEX IF NOT EXISTS idx_audits_status ON audits(status);
            CREATE INDEX IF NOT EXISTS idx_audits_created ON audits(created_at DESC);
            CREATE INDEX IF NOT EXISTS idx_findings_audit ON findings(audit_id);
            CREATE INDEX IF NOT EXISTS idx_companies_trust ON companies(trust_score);
            CREATE INDEX IF NOT EXISTS idx_companies_domain ON companies(domain);
        """)

        # Seed if empty
        cur = await db.execute("SELECT COUNT(*) FROM companies")
        row = await cur.fetchone()
        if row[0] == 0:
            await _seed(db)

        await db.commit()


async def _seed(db: aiosqlite.Connection) -> None:
    """Seed initial companies."""
    companies = [
        ("Amazon", "amazon", "amazon.com", "ecommerce", "E-commerce and cloud computing giant"),
        ("Google", "google", "google.com", "tech", "Search, advertising, and cloud platform"),
        ("Apple", "apple", "apple.com", "tech", "Consumer electronics and software ecosystem"),
        ("Netflix", "netflix", "netflix.com", "streaming", "Video streaming subscription service"),
        ("Adobe", "adobe", "adobe.com", "software", "Creative and document software suite"),
        ("Spotify", "spotify", "spotify.com", "streaming", "Music and podcast streaming platform"),
        ("Meta", "meta", "meta.com", "social", "Social media and advertising conglomerate"),
        ("Twitter", "twitter", "x.com", "social", "Microblogging platform, rebranded to X"),
    ]

    for name, slug, domain, category, description in companies:
        logo_url = f"https://www.google.com/s2/favicons?domain={domain}&sz=64"
        await db.execute(
            "INSERT INTO companies (name, slug, domain, category, description, logo_url) "
            "VALUES (?, ?, ?, ?, ?, ?)",
            (name, slug, domain, category, description, logo_url),
        )

    await db.commit()
    logger.info("Seeded {} companies", len(companies))
