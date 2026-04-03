"""Audit service — submit audits, build feed, detect platforms."""
import json
import re
from typing import Optional
from urllib.parse import urlparse

import aiosqlite
from loguru import logger

from ..repositories.audit_repository import AuditRepository
from ..repositories.company_repository import CompanyRepository
from ..repositories.finding_repository import FindingRepository
from ..schemas.audit import AuditCard, AuditDetail, FindingResponse
from ..schemas.feed import FeedResponse
from .url_validator import URLValidationError, validate_url

# Platform detection patterns: (regex, platform_name)
_PLATFORM_PATTERNS: list[tuple[re.Pattern, str]] = [
    (re.compile(r"amazon\.\w+/.*(?:dp|gp/product)/", re.IGNORECASE), "amazon_product"),
    (re.compile(r"apps\.apple\.com/.+/app/", re.IGNORECASE), "appstore_app"),
    (re.compile(r"play\.google\.com/store/apps/", re.IGNORECASE), "gplay_app"),
    (re.compile(r"google\.\w+/maps/", re.IGNORECASE), "gmaps_place"),
    (re.compile(r"maps\.google\.\w+/", re.IGNORECASE), "gmaps_place"),
]


# Domain alias mapping — merge related domains to canonical parent
DOMAIN_ALIASES: dict[str, str] = {
    "amazon.co.uk": "amazon.com",
    "amazon.de": "amazon.com",
    "amazon.fr": "amazon.com",
    "amazon.co.jp": "amazon.com",
    "amazon.in": "amazon.com",
    "x.com": "x.com",
    "twitter.com": "x.com",
    "fb.com": "meta.com",
    "facebook.com": "meta.com",
    "instagram.com": "meta.com",
    "whatsapp.com": "meta.com",
    "youtube.com": "google.com",
    "gmail.com": "google.com",
}


def _normalize_domain(domain: str) -> str:
    """Normalize domain via alias mapping."""
    return DOMAIN_ALIASES.get(domain, domain)


def _detect_platform(url: str) -> str:
    """Detect platform type from URL. Falls back to 'website'."""
    for pattern, platform in _PLATFORM_PATTERNS:
        if pattern.search(url):
            return platform
    return "website"


_DOUBLE_TLDS = {"co.uk", "co.jp", "com.au", "com.br", "co.in", "co.kr", "com.mx", "com.tr", "co.za"}

def _extract_domain(url: str) -> str:
    """Extract root domain from URL — strips www., handles double TLDs."""
    parsed = urlparse(url)
    hostname = (parsed.hostname or "").lower()
    if hostname.startswith("www."):
        hostname = hostname[4:]
    # First check if full hostname is in DOMAIN_ALIASES (e.g. amazon.co.uk)
    if hostname in DOMAIN_ALIASES:
        return hostname
    parts = hostname.split(".")
    if len(parts) > 2:
        # Check for double TLDs like co.uk, com.au
        last_two = ".".join(parts[-2:])
        if last_two in _DOUBLE_TLDS:
            hostname = ".".join(parts[-3:])  # amazon.co.uk
        else:
            hostname = ".".join(parts[-2:])  # apps.apple.com → apple.com
    return hostname


def _domain_to_name(domain: str) -> str:
    """Generate human-readable company name from domain."""
    # Take the part before TLD
    parts = domain.split(".")
    if len(parts) >= 2:
        name = parts[-2]  # e.g., "google" from "google.com"
    else:
        name = parts[0]
    return name.capitalize()


def _generate_audit_title(url: str, platform: str, domain: str) -> str:
    """Generate a default audit title from URL metadata."""
    platform_labels = {
        "amazon_product": "Amazon Product Audit",
        "appstore_app": "App Store App Audit",
        "gplay_app": "Google Play App Audit",
        "gmaps_place": "Google Maps Place Audit",
        "website": f"Website Audit: {domain}",
        "company": f"Company Audit: {domain}",
    }
    return platform_labels.get(platform, f"Audit: {domain}")


def _row_to_audit_card(row: aiosqlite.Row) -> AuditCard:
    """Convert a joined audit+company row into AuditCard schema."""
    return AuditCard(
        id=row["id"],
        company_id=row["company_id"],
        company_name=row["company_name"],
        company_slug=row["company_slug"],
        company_logo=row["company_logo"],
        url=row["url"],
        platform=row["platform"],
        title=row["title"],
        subtitle=row["subtitle"],
        trust_score=row["trust_score"],
        severity=row["severity"],
        ai_summary=row["ai_summary"],
        findings_count=row["findings_count"] if "findings_count" in row.keys() else 0,
        status=row["status"],
        views=row["views"],
        created_at=row["created_at"],
    )


class AuditService:
    def __init__(self, db: aiosqlite.Connection):
        self.db = db
        self.audits = AuditRepository(db)
        self.companies = CompanyRepository(db)
        self.findings = FindingRepository(db)

    async def submit_audit(self, url: str) -> dict:
        """
        Submit a new URL for audit:
        1. Validate URL (SSRF protection)
        2. Check for existing recent audit (24h dedup)
        3. Detect platform from URL
        4. Extract + normalize domain, get_or_create company
        5. Create audit as 'pending'
        6. Return audit_id + metadata
        """
        # Task 2: URL validation + SSRF protection
        url = validate_url(url)

        # Task 3: Deduplication — check for recent audit within 24h
        existing = await self.audits.get_recent_by_url(url, hours=24)
        if existing:
            status = existing["status"]
            cached = status == "done"
            logger.info(
                "Dedup hit: url={} existing_audit_id={} status={}",
                url, existing["id"], status,
            )
            return {
                "audit_id": existing["id"],
                "company_id": existing["company_id"],
                "company_slug": existing["company_slug"],
                "platform": existing["platform"],
                "status": status,
                "cached": cached,
            }

        platform = _detect_platform(url)
        domain = _extract_domain(url)

        if not domain:
            raise ValueError("Could not extract domain from URL")

        # Task 4: Domain normalization via aliases
        domain = _normalize_domain(domain)
        name = _domain_to_name(domain)

        company = await self.companies.get_or_create_by_domain(domain, name)
        title = _generate_audit_title(url, platform, domain)

        audit_id = await self.audits.create(
            company_id=company["id"],
            url=url,
            platform=platform,
            title=title,
        )

        logger.info(
            "Audit submitted: id={} url={} platform={} company={}",
            audit_id, url, platform, company["name"],
        )

        return {
            "audit_id": audit_id,
            "company_id": company["id"],
            "company_slug": company["slug"],
            "platform": platform,
            "status": "pending",
        }

    async def get_audit(self, audit_id: int) -> Optional[AuditDetail]:
        """Get full audit detail with findings."""
        row = await self.audits.get_by_id(audit_id)
        if not row:
            return None

        # Increment views (fire-and-forget)
        await self.audits.increment_views(audit_id)

        findings_rows = await self.findings.get_by_audit(audit_id)
        findings = [
            FindingResponse(
                id=f["id"],
                type=f["type"],
                severity=f["severity"],
                title=f["title"],
                description=f["description"],
                evidence_url=f["evidence_url"],
                confidence=f["confidence"],
            )
            for f in findings_rows
        ]

        # Count findings for the card fields
        metadata = json.loads(row["metadata"]) if row["metadata"] else {}

        # Queue position for pending/processing audits
        queue_position = 0
        queue_total = 0
        if row["status"] in ("pending", "processing"):
            cur = await self.db.execute(
                "SELECT COUNT(*) FROM audits WHERE status IN ('pending','processing') AND created_at <= ?",
                (row["created_at"],),
            )
            queue_position = (await cur.fetchone())[0]
            cur = await self.db.execute("SELECT COUNT(*) FROM audits WHERE status IN ('pending','processing')")
            queue_total = (await cur.fetchone())[0]

        return AuditDetail(
            id=row["id"],
            company_id=row["company_id"],
            company_name=row["company_name"],
            company_slug=row["company_slug"],
            company_logo=row["company_logo"],
            url=row["url"],
            platform=row["platform"],
            title=row["title"],
            subtitle=row["subtitle"],
            trust_score=row["trust_score"],
            severity=row["severity"],
            ai_summary=row["ai_summary"],
            findings_count=len(findings),
            status=row["status"],
            views=row["views"],
            created_at=row["created_at"],
            findings=findings,
            metadata=metadata,
            queue_position=queue_position,
            queue_total=queue_total,
        )

    async def retry_audit(self, audit_id: int) -> dict:
        """
        Retry a failed audit:
        1. Check audit exists and is failed
        2. Reset status to pending, clear ai_summary
        3. Return audit info for background task scheduling
        """
        row = await self.audits.get_by_id(audit_id)
        if not row:
            return None

        if row["status"] != "failed":
            raise ValueError("Only failed audits can be retried")

        await self.audits.reset_for_retry(audit_id)

        logger.info("Audit {} reset for retry", audit_id)

        return {
            "audit_id": audit_id,
            "company_id": row["company_id"],
            "status": "pending",
        }

    async def get_feed(
        self,
        page: int = 1,
        per_page: int = 20,
        platform: Optional[str] = None,
        severity: Optional[str] = None,
    ) -> FeedResponse:
        """Get paginated feed of completed audits."""
        # Clamp pagination
        page = max(1, page)
        per_page = max(1, min(100, per_page))

        rows, total = await self.audits.get_feed(
            page=page,
            per_page=per_page,
            platform_filter=platform,
            severity_filter=severity,
        )

        items = [_row_to_audit_card(r) for r in rows]
        has_more = (page * per_page) < total

        return FeedResponse(
            items=items,
            total=total,
            page=page,
            per_page=per_page,
            has_more=has_more,
        )
