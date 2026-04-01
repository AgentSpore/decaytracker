"""Amazon product audit agent — specialized review/price analysis."""
import asyncio
import re
from typing import Optional

from loguru import logger
from pydantic import BaseModel
from pydantic_ai import Agent

from .base_agent import _make_model, web_search, scrape_page, extract_domain
from .website_agent import AuditFinding, WebsiteAuditResult, LocalizedText


AMAZON_PROMPT = """You are an Amazon product trust auditor. Analyze the product listing data and search results.

CRITICAL: All text fields (title, subtitle, ai_summary, finding titles, finding descriptions)
MUST be provided in 3 languages simultaneously as a JSON object: {"en": "...", "ru": "...", "cn": "..."}
- "en" = English
- "ru" = Russian (Русский)
- "cn" = Chinese Simplified (简体中文)

Pay special attention to:
1. Review authenticity — fake/incentivized reviews, suspicious timing, repeated phrases
2. Price manipulation — fake "was" prices, inflated discounts
3. Seller reliability — new seller, multiple identical listings, complaint history
4. Product claims vs reality — exaggerated marketing
5. Listing quality — legitimate brand vs fly-by-night operation

Scoring: 0-100 trust score. Finding types: fake_reviews, price_manipulation,
dark_pattern, hidden_fees, subscription_trap, positive_signal.

Be balanced — include positive_signal findings if the product looks legitimate."""


def _extract_asin(url: str) -> str:
    m = re.search(r"/(?:dp|gp/product)/([A-Z0-9]{10})", url)
    return m.group(1) if m else ""


def _extract_product_info(text: str) -> dict:
    info = {}
    price_m = re.search(r"\$(\d+\.?\d*)", text)
    if price_m:
        info["price"] = price_m.group(0)
    rating_m = re.search(r"(\d\.?\d?) out of 5", text)
    if rating_m:
        info["rating"] = rating_m.group(1)
    reviews_m = re.search(r"([\d,]+)\s+(?:rating|review|customer)", text, re.I)
    if reviews_m:
        info["review_count"] = reviews_m.group(1)
    return info


async def audit_amazon(url: str) -> WebsiteAuditResult:
    domain = extract_domain(url)
    asin = _extract_asin(url)
    logger.info("Amazon audit: {} (ASIN: {})", url[:60], asin)

    page_data = await scrape_page(url)
    product_info = _extract_product_info(page_data["text"])

    product_title = page_data["title"].split(" - Amazon")[0].strip() if page_data["title"] else "Amazon Product"

    await asyncio.sleep(1.5)
    search1 = await web_search(f'"{product_title}" fake reviews scam 2025 2026', max_results=5)
    await asyncio.sleep(1.5)
    search2 = await web_search(f"amazon ASIN {asin} review analysis", max_results=3) if asin else ""
    await asyncio.sleep(1.5)
    search3 = await web_search(f'"{product_title}" price history deal', max_results=3)

    model = _make_model()
    agent: Agent[None, WebsiteAuditResult] = Agent(
        model=model,
        output_type=WebsiteAuditResult,
        system_prompt=AMAZON_PROMPT,
    )

    prompt = f"""Audit this Amazon product:
URL: {url}
ASIN: {asin}
Product Title: {product_title}
Extracted Info: {product_info}

Page text (first 3000 chars):
{page_data['text'][:3000]}

Search — fake reviews/scam:
{search1}

Search — ASIN review analysis:
{search2}

Search — price history:
{search3}

Produce a structured trust audit for this product."""

    try:
        result = await agent.run(prompt)
        output = result.output
        output.metadata = {**output.metadata, **product_info, "asin": asin}
        return output
    except Exception as e:
        logger.error("Amazon agent LLM failed for {}: {}", asin or url[:40], e)
        subtitle = f"amazon.com · {product_info.get('price', '?')} · ★{product_info.get('rating', '?')}"
        return WebsiteAuditResult(
            title=LocalizedText(en=product_title, ru=product_title, cn=product_title),
            subtitle=LocalizedText(en=subtitle, ru=subtitle, cn=subtitle),
            trust_score=50,
            severity="neutral",
            ai_summary=LocalizedText(
                en=f"Automated analysis could not be completed for this Amazon product.",
                ru=f"Автоматический анализ не удалось завершить для этого товара на Amazon.",
                cn=f"无法完成此亚马逊产品的自动分析。",
            ),
            findings=[],
            metadata={**product_info, "asin": asin, "error": "LLM unavailable"},
        )
