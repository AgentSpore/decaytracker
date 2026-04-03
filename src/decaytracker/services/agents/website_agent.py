"""Website/company audit agent — deep fraud & manipulation detection."""
import asyncio
from datetime import date

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


SYSTEM_PROMPT = """You are an expert fraud and manipulation auditor. Your job is to detect deception, fake reviews, bots, astroturfing, dark patterns, and consumer harm.

## Scoring
- 90-100: Excellent trust. Transparent, honest, no manipulation signals
- 70-89: Good. Minor concerns but generally trustworthy
- 50-69: Mixed. Some manipulation signals detected
- 30-49: Poor. Multiple fraud/manipulation red flags
- 0-29: Critical. Clear evidence of fraud, fake reviews, or deception

## Finding types (use these exact values):
- fake_reviews: Bot reviews, purchased reviews, incentivized reviews, review farms
- review_manipulation: Deleting negative reviews, gating, selective display
- bot_activity: Automated fake engagement, astroturfing, sockpuppets
- price_manipulation: Fake discounts, anchor pricing, bait-and-switch
- dark_pattern: Manipulative UI, forced opt-ins, hidden checkboxes, shame-clicking
- hidden_fees: Charges not disclosed upfront, surprise costs at checkout
- enshittification: Degrading product quality while extracting more money
- data_harvesting: Excessive data collection, selling user data
- subscription_trap: Hard to cancel, dark patterns in cancellation flow
- fake_social_proof: Fake testimonials, inflated numbers, fake urgency
- astroturfing: Fake grassroots campaigns, paid opinions disguised as organic
- positive_signal: Good transparency, fair practices, honest communication

## Severity: critical, warning, info, positive

## Severity for whole audit: "critical" if score<30, "warning" if <50, "neutral" if <70, "clean" if >=70

## Rules:
- Focus on MANIPULATION and FRAUD detection — this is your primary mission
- Look for patterns: fake urgency, inflated numbers, suspicious testimonials
- Check if complaints mention bots, fake reviews, paid reviews, astroturfing
- Report specific evidence with source URLs
- Be balanced — report positive_signal findings for honest practices
- If data is limited, be conservative (lower confidence, moderate score)"""


async def audit_website(url: str) -> WebsiteAuditResult:
    domain = extract_domain(url)
    logger.info("Website audit: {} ({})", url[:60], domain)

    # Step 1: Scrape the page
    page_data = await scrape_page(url)

    # Step 2: Search for fraud/manipulation signals (5 targeted queries)
    await asyncio.sleep(1.5)
    search_scam = await web_search(f"{domain} scam fraud fake complaints 2024 2025 2026", max_results=5)

    await asyncio.sleep(1.5)
    search_reviews = await web_search(f"{domain} fake reviews bots purchased reviews manipulation", max_results=5)

    await asyncio.sleep(1.5)
    search_dark = await web_search(f"{domain} dark patterns hidden fees subscription trap cancellation", max_results=5)

    await asyncio.sleep(1.5)
    search_trust = await web_search(f"{domain} trustpilot reviews site:trustpilot.com OR site:bbb.org OR site:otzovik.com OR site:irecommend.ru", max_results=5)

    await asyncio.sleep(1.5)
    search_decay = await web_search(f"{domain} enshittification price increase worse quality 2025 2026", max_results=5)

    # Step 3: Analyze with LLM
    model = _make_model()
    agent: Agent[None, WebsiteAuditResult] = Agent(
        model=model,
        output_type=WebsiteAuditResult,
        system_prompt=SYSTEM_PROMPT,
        retries=3,
    )

    today = date.today().isoformat()

    prompt = f"""Perform a deep fraud and manipulation audit:

IMPORTANT: Today's date is {today}. Content dated on or before today is NOT from the future. Do NOT flag real current events as "fabricated" or "misinformation" just because they describe recent events.

URL: {url}
Domain: {domain}

== PAGE CONTENT ==
Title: {page_data['title']}
Description: {page_data['description']}
Text (first 2000 chars): {page_data['text'][:2000]}

== SEARCH: Scam/fraud/complaints ==
{search_scam}

== SEARCH: Fake reviews/bots/manipulation ==
{search_reviews}

== SEARCH: Dark patterns/hidden fees/subscription traps ==
{search_dark}

== SEARCH: Trustpilot/BBB/otzovik ratings ==
{search_trust}

== SEARCH: Enshittification/price hikes/quality decline ==
{search_decay}

Analyze all evidence and produce a comprehensive trust audit. Focus on detecting:
1. Fake reviews and bot activity
2. Review manipulation (deleting negatives, gating)
3. Dark patterns in UI
4. Hidden fees and subscription traps
5. Fake social proof (inflated numbers, fake testimonials)
6. Astroturfing and paid opinions
7. Price manipulation and bait-and-switch
8. Data harvesting concerns
9. Product/service quality decline (enshittification)

Include SPECIFIC evidence from search results. Quote sources with URLs."""

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
