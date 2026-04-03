"""Amazon product audit agent — deep fake review & manipulation detection."""
import asyncio
import re
from datetime import date

from loguru import logger
from pydantic_ai import Agent

from .base_agent import _make_model, web_search, scrape_page, extract_domain
from .website_agent import AuditFinding, WebsiteAuditResult


AMAZON_PROMPT = """You are an expert product fraud auditor for Amazon and online marketplaces.
Your mission: help consumers decide if this product is safe to buy.

## What to detect:
1. FAKE REVIEWS: Bot-generated, purchased, incentivized ("free product for review"), review farms
2. REVIEW MANIPULATION: Suspicious rating distribution, review date clustering, repeated phrases
3. SELLER RED FLAGS: New seller with too many reviews, multiple identical listings, company history
4. PRICE MANIPULATION: Fake "was" price, artificial discounts, bait-and-switch
5. PRODUCT SAFETY: No certifications, FDA/CE missing, counterfeit signals
6. MISLEADING CLAIMS: Exaggerated marketing, fake before/after, pseudo-science
7. POSITIVE SIGNALS: Verified brand, consistent quality, honest marketing

## Scoring: 0-100 (consumer perspective — would you recommend buying this?)
- 90-100: Safe to buy, verified quality, honest seller
- 70-89: Likely safe, minor concerns
- 50-69: Proceed with caution, some red flags
- 30-49: High risk, likely manipulation
- 0-29: Do not buy, clear fraud signals

## Finding types: fake_reviews, review_manipulation, bot_activity, price_manipulation,
   fake_social_proof, dark_pattern, hidden_fees, positive_signal

## Rules:
- Be specific: "67% of reviews posted within 3 days" not "some reviews seem fake"
- Quote numbers and dates from evidence
- Include source URLs
- Think like a consumer protection investigator"""


def _extract_asin(url: str) -> str:
    m = re.search(r"/(?:dp|gp/product)/([A-Z0-9]{10})", url)
    return m.group(1) if m else ""


def _extract_product_info(text: str) -> dict:
    info = {}
    price_m = re.search(r"\$(\d+\.?\d*)", text)
    if price_m:
        info["price"] = price_m.group(0)
    was_price_m = re.search(r"(?:was|list price)[:\s]*\$(\d+\.?\d*)", text, re.I)
    if was_price_m:
        info["was_price"] = f"${was_price_m.group(1)}"
    rating_m = re.search(r"(\d\.?\d?) out of 5", text)
    if rating_m:
        info["rating"] = rating_m.group(1)
    reviews_m = re.search(r"([\d,]+)\s+(?:rating|review|customer)", text, re.I)
    if reviews_m:
        info["review_count"] = reviews_m.group(1)
    brand_m = re.search(r"(?:Brand|by)[:\s]+([A-Za-z0-9][\w\s]{1,30}?)(?:\s*[|\-]|\s*$)", text)
    if brand_m:
        info["brand"] = brand_m.group(1).strip()
    return info


async def audit_amazon(url: str) -> WebsiteAuditResult:
    domain = extract_domain(url)
    asin = _extract_asin(url)
    logger.info("Amazon audit: {} (ASIN: {})", url[:60], asin)

    page_data = await scrape_page(url)
    product_info = _extract_product_info(page_data["text"])
    product_title = page_data["title"].split(" - Amazon")[0].strip() if page_data["title"] else "Amazon Product"

    # Deep search: 5 targeted queries
    await asyncio.sleep(1.5)
    search_fake = await web_search(f'"{product_title}" OR "ASIN {asin}" fake reviews scam 2024 2025', max_results=5)

    await asyncio.sleep(1.5)
    search_fakespot = await web_search(f'amazon {asin} fakespot reviewmeta analysis adjusted rating', max_results=5)

    await asyncio.sleep(1.5)
    search_seller = await web_search(f'amazon seller "{product_info.get("brand", product_title)}" complaints fraud', max_results=5)

    await asyncio.sleep(1.5)
    search_price = await web_search(f'amazon {asin} price history camelcamelcamel keepa', max_results=5)

    await asyncio.sleep(1.5)
    search_safety = await web_search(f'"{product_title}" safety recall FDA warning counterfeit', max_results=3)

    model = _make_model()
    agent: Agent[None, WebsiteAuditResult] = Agent(
        model=model,
        output_type=WebsiteAuditResult,
        system_prompt=AMAZON_PROMPT,
        retries=3,
    )

    today = date.today().isoformat()

    prompt = f"""Deep product audit — should a consumer buy this?

IMPORTANT: Today's date is {today}. Do NOT flag current-date content as "future" or "fabricated".

URL: {url}
ASIN: {asin}
Product: {product_title}
Extracted: {product_info}

== PAGE CONTENT (first 2000 chars) ==
{page_data['text'][:2000]}

== SEARCH: Fake reviews/scam reports ==
{search_fake}

== SEARCH: Fakespot/ReviewMeta analysis ==
{search_fakespot}

== SEARCH: Seller reputation ==
{search_seller}

== SEARCH: Price history (CamelCamelCamel/Keepa) ==
{search_price}

== SEARCH: Safety/recall/counterfeit ==
{search_safety}

Analyze all evidence. Focus on:
1. Are the reviews authentic? Look for date clustering, repeated phrases, incentivized signals
2. Is the price real or manipulated? Check if "was" price is fake
3. Is the seller legitimate? Brand history, complaint patterns
4. Is the product safe? Certifications, recalls, counterfeits
5. Would you recommend a friend to buy this?

Be specific with numbers and evidence."""

    try:
        result = await agent.run(prompt)
        output = result.output
        output.metadata = {**output.metadata, **product_info, "asin": asin}
        return output
    except Exception as e:
        logger.error("Amazon agent LLM failed for {}: {}", asin or url[:40], e)
        subtitle = f"amazon.com · {product_info.get('price', '?')} · ★{product_info.get('rating', '?')}"
        return WebsiteAuditResult(
            title=product_title,
            subtitle=subtitle,
            trust_score=50,
            severity="neutral",
            ai_summary="Automated analysis could not be completed for this Amazon product.",
            findings=[],
            metadata={**product_info, "asin": asin, "error": "LLM unavailable"},
        )
