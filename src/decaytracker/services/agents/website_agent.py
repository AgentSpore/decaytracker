"""Website/company audit agent — default for any URL."""
import asyncio

from loguru import logger
from pydantic import BaseModel
from pydantic_ai import Agent

from .base_agent import _make_model, web_search, scrape_page, extract_domain


class AuditFinding(BaseModel):
    type: str
    severity: str
    title: str
    description: str
    evidence_url: str = ""
    confidence: float = 0.5


class WebsiteAuditResult(BaseModel):
    title: str
    subtitle: str
    trust_score: int
    severity: str
    ai_summary: str
    findings: list[AuditFinding] = []
    metadata: dict = {}


SYSTEM_PROMPT = """You are a trust auditor analyzing websites and companies.

Scoring guide:
- 90-100: Excellent. Transparent, user-friendly, no complaints
- 70-89: Good. Minor issues but generally trustworthy
- 50-69: Mixed. Some concerning signals
- 30-49: Poor. Multiple red flags, deceptive patterns
- 0-29: Critical. Scam signals, widespread fraud

Finding types: fake_reviews, price_manipulation, dark_pattern, hidden_fees,
enshittification, permission_creep, data_harvesting, subscription_trap, positive_signal

Severity for findings: critical, warning, info, positive
Severity for the whole audit: "critical" if score < 30, "warning" if < 50, "neutral" if < 70, "clean" if >= 70

Rules:
- ONLY report findings supported by evidence from the provided data
- Include source URLs for findings when available
- Be balanced — include positive_signal findings too
- Low data = lower confidence scores
- All text in English"""


async def audit_website(url: str) -> WebsiteAuditResult:
    domain = extract_domain(url)
    logger.info("Website audit: {} ({})", url[:60], domain)

    page_data = await scrape_page(url)
    await asyncio.sleep(1.5)
    search1 = await web_search(f"{domain} scam complaints reviews 2025 2026", max_results=5)
    await asyncio.sleep(1.5)
    search2 = await web_search(f"{domain} dark patterns price increase enshittification", max_results=5)

    model = _make_model()
    agent: Agent[None, WebsiteAuditResult] = Agent(
        model=model,
        output_type=WebsiteAuditResult,
        system_prompt=SYSTEM_PROMPT,
        retries=3,
    )

    prompt = f"""Audit this website/company:
URL: {url}
Domain: {domain}

Page content:
Title: {page_data['title']}
Description: {page_data['description']}
Text (first 2000 chars): {page_data['text'][:2000]}

Google search — complaints/scams:
{search1}

Google search — dark patterns/enshittification:
{search2}

Produce a structured trust audit with title, subtitle, trust_score (0-100), severity, ai_summary, and findings list."""

    try:
        result = await agent.run(prompt)
        return result.output
    except Exception as e:
        logger.error("Website agent LLM failed for {}: {}", domain, e)
        return WebsiteAuditResult(
            title=page_data["title"] or f"Audit of {domain}",
            subtitle=domain,
            trust_score=50,
            severity="neutral",
            ai_summary=f"Automated audit could not be completed. Limited data available for {domain}.",
            findings=[],
            metadata={"error": "LLM analysis unavailable", "page_title": page_data["title"]},
        )
