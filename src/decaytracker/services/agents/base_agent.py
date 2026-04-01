"""Base utilities shared by all audit agents: LLM model, web search, scraping."""
import os
import re
from urllib.parse import urlparse

from loguru import logger
from pydantic_ai.models.openai import OpenAIModel
from pydantic_ai.models.fallback import FallbackModel
from pydantic_ai.providers.openai import OpenAIProvider

OPENROUTER_BASE = "https://openrouter.ai/api/v1"
OPENROUTER_KEY = os.getenv("OPENROUTER_API_KEY", "")


def _make_model() -> FallbackModel:
    def _or(model_id: str) -> OpenAIModel:
        return OpenAIModel(model_id, provider=OpenAIProvider(base_url=OPENROUTER_BASE, api_key=OPENROUTER_KEY))
    return FallbackModel(
        _or("nvidia/nemotron-3-super-120b-a12b:free"),
        _or("minimax/minimax-m2.5:free"),
        _or("stepfun/step-3.5-flash:free"),
    )


async def web_search(query: str, max_results: int = 5) -> str:
    """Google search via Playwright persistent context. Returns titles+snippets+URLs."""
    from playwright.async_api import async_playwright
    import asyncio

    profile_dir = "/tmp/decaytracker-chrome-profile"
    os.makedirs(profile_dir, exist_ok=True)

    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch_persistent_context(
                profile_dir,
                headless=True,
                args=["--disable-blink-features=AutomationControlled", "--no-sandbox"],
            )
            page = browser.pages[0] if browser.pages else await browser.new_page()
            await page.goto(
                f"https://www.google.com/search?q={query}&num={max_results}",
                wait_until="domcontentloaded",
                timeout=15000,
            )
            await page.wait_for_timeout(2000)

            results = []
            items = await page.query_selector_all("div.g")
            for item in items[:max_results]:
                title_el = await item.query_selector("h3")
                snippet_el = await item.query_selector(".VwiC3b")
                link_el = await item.query_selector("a")
                title = await title_el.inner_text() if title_el else ""
                snippet = await snippet_el.inner_text() if snippet_el else ""
                href = await link_el.get_attribute("href") if link_el else ""
                if title:
                    results.append(f"{title}\n{snippet}\n{href}")

            await browser.close()
            return "\n\n".join(results) if results else "No results found"
    except Exception as e:
        logger.warning("Web search failed for '{}': {}", query[:50], e)
        return "Search unavailable"


async def scrape_page(url: str) -> dict:
    """Scrape URL via Playwright. Returns {title, description, text, status_code}."""
    from playwright.async_api import async_playwright

    profile_dir = "/tmp/decaytracker-chrome-profile"
    os.makedirs(profile_dir, exist_ok=True)

    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch_persistent_context(
                profile_dir,
                headless=True,
                args=["--disable-blink-features=AutomationControlled", "--no-sandbox"],
            )
            page = browser.pages[0] if browser.pages else await browser.new_page()
            resp = await page.goto(url, wait_until="domcontentloaded", timeout=20000)
            await page.wait_for_timeout(2000)

            title = await page.title()
            desc_el = await page.query_selector('meta[name="description"]')
            description = await desc_el.get_attribute("content") if desc_el else ""
            text = await page.inner_text("body")
            text = text[:3000] if text else ""
            status = resp.status if resp else 0

            await browser.close()
            return {"title": title, "description": description or "", "text": text, "status_code": status}
    except Exception as e:
        logger.warning("Scrape failed for {}: {}", url[:60], e)
        return {"title": "", "description": "", "text": "", "status_code": 0}


def extract_domain(url: str) -> str:
    """Extract clean domain (no www.)."""
    parsed = urlparse(url)
    domain = parsed.hostname or ""
    if domain.startswith("www."):
        domain = domain[4:]
    return domain


_PLATFORM_PATTERNS = [
    (re.compile(r"amazon\.\w+/(dp|gp/product)/", re.I), "amazon_product"),
    (re.compile(r"apps\.apple\.com/.+/app/", re.I), "appstore_app"),
    (re.compile(r"play\.google\.com/store/apps/", re.I), "gplay_app"),
    (re.compile(r"(google\.\w+/maps|maps\.google)", re.I), "gmaps_place"),
]


def detect_platform(url: str) -> str:
    for pattern, platform in _PLATFORM_PATTERNS:
        if pattern.search(url):
            return platform
    return "website"
