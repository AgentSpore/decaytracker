"""Website/company audit agent — default for any URL."""
import asyncio
from typing import Optional

from loguru import logger
from pydantic import BaseModel
from pydantic_ai import Agent

from .base_agent import _make_model, web_search, scrape_page, extract_domain


class LocalizedText(BaseModel):
    en: str = ""
    ru: str = ""
    cn: str = ""


class AuditFinding(BaseModel):
    type: str
    severity: str
    title: LocalizedText
    description: LocalizedText
    evidence_url: str = ""
    confidence: float = 0.5


class WebsiteAuditResult(BaseModel):
    title: LocalizedText
    subtitle: LocalizedText
    trust_score: int
    severity: str
    ai_summary: LocalizedText
    findings: list[AuditFinding] = []
    metadata: dict = {}


SYSTEM_PROMPT = """You are a trust auditor analyzing websites and companies.

CRITICAL: All text fields (title, subtitle, ai_summary, finding titles, finding descriptions)
MUST be provided in 3 languages simultaneously as a JSON object: {"en": "...", "ru": "...", "cn": "..."}
- "en" = English
- "ru" = Russian (Русский)
- "cn" = Chinese Simplified (简体中文)

Scoring guide:
- 90-100: Excellent. Transparent, user-friendly, no complaints
- 70-89: Good. Minor issues but generally trustworthy
- 50-69: Mixed. Some concerning signals
- 30-49: Poor. Multiple red flags, deceptive patterns
- 0-29: Critical. Scam signals, widespread fraud

Finding types: fake_reviews, price_manipulation, dark_pattern, hidden_fees,
enshittification, permission_creep, data_harvesting, subscription_trap, positive_signal

Severity: critical, warning, info, positive

Rules:
- ONLY report findings supported by evidence
- Include source URLs for findings
- Be balanced — include positive_signal findings too
- Low data = lower confidence scores
- severity field for the whole audit: "critical" if score < 30, "warning" if < 50, "neutral" if < 70, "clean" if >= 70"""


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
    )

    prompt = f"""Audit this website/company:
URL: {url}
Domain: {domain}

Page content:
Title: {page_data['title']}
Description: {page_data['description']}
Text (first 3000 chars): {page_data['text'][:3000]}

Google search — complaints/scams:
{search1}

Google search — dark patterns/enshittification:
{search2}

Produce a structured trust audit."""

    try:
        result = await agent.run(prompt)
        return result.output
    except Exception as e:
        logger.error("Website agent LLM failed for {}: {}", domain, e)
        t = page_data["title"] or f"Audit of {domain}"
        return WebsiteAuditResult(
            title=LocalizedText(en=t, ru=t, cn=t),
            subtitle=LocalizedText(en=domain, ru=domain, cn=domain),
            trust_score=50,
            severity="neutral",
            ai_summary=LocalizedText(
                en=f"Automated audit could not be completed. Limited data available for {domain}.",
                ru=f"Автоматический аудит не удалось завершить. Недостаточно данных для {domain}.",
                cn=f"自动审核无法完成。{domain} 的可用数据有限。",
            ),
            findings=[],
            metadata={"error": "LLM analysis unavailable", "page_title": page_data["title"]},
        )
