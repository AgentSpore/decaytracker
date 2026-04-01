"""
UI tests for DecayTracker — Playwright against live frontend (:3001) + backend (:8790).

Run: uv run pytest tests/test_ui.py -v
"""
import pytest
from playwright.sync_api import sync_playwright, Page, expect

FRONTEND = "http://localhost:3001"


@pytest.fixture(scope="session")
def browser():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        yield browser
        browser.close()


@pytest.fixture
def page(browser):
    ctx = browser.new_context()
    page = ctx.new_page()
    yield page
    ctx.close()


# ──────────────────────────────────────────────
# Home page
# ──────────────────────────────────────────────

class TestHomePage:
    def test_masthead_visible(self, page: Page):
        page.goto(FRONTEND)
        masthead = page.get_by_test_id("masthead")
        expect(masthead).to_be_visible()
        expect(masthead).to_contain_text("The Index")

    def test_product_list_loaded(self, page: Page):
        page.goto(FRONTEND)
        page.wait_for_selector("[data-testid='product-card']", timeout=10000)
        cards = page.get_by_test_id("product-card")
        assert cards.count() >= 10

    def test_search_filters_products(self, page: Page):
        page.goto(FRONTEND)
        page.wait_for_selector("[data-testid='product-card']", timeout=10000)
        initial_count = page.get_by_test_id("product-card").count()

        search_input = page.get_by_test_id("search-input")
        search_input.fill("netflix")
        search_input.press("Enter")
        page.wait_for_timeout(1500)

        filtered_count = page.get_by_test_id("product-card").count()
        assert filtered_count < initial_count
        assert filtered_count >= 1

    def test_category_filter(self, page: Page):
        page.goto(FRONTEND)
        page.wait_for_selector("[data-testid='product-card']", timeout=10000)

        page.get_by_test_id("category-filter").select_option("social")
        page.wait_for_timeout(1500)

        cards = page.get_by_test_id("product-card")
        assert cards.count() >= 2
        # All visible cards should contain social products

    def test_score_badges_visible(self, page: Page):
        page.goto(FRONTEND)
        page.wait_for_selector("[data-testid='score-badge']", timeout=10000)
        badges = page.get_by_test_id("score-badge")
        assert badges.count() >= 10

    def test_request_button_opens_dialog(self, page: Page):
        page.goto(FRONTEND)
        page.get_by_test_id("request-btn").click()
        dialog = page.locator("dialog[open]")
        expect(dialog).to_be_visible()
        expect(dialog).to_contain_text("Request Product")


# ──────────────────────────────────────────────
# Product detail page
# ──────────────────────────────────────────────

class TestProductPage:
    def test_navigate_to_product(self, page: Page):
        page.goto(FRONTEND)
        page.wait_for_selector("[data-testid='product-card']", timeout=10000)
        page.get_by_test_id("product-card").first.click()
        page.wait_for_selector("[data-testid='product-name']", timeout=10000)
        expect(page.get_by_test_id("product-name")).to_be_visible()

    def test_netflix_detail_page(self, page: Page):
        page.goto(f"{FRONTEND}/product/netflix")
        page.wait_for_selector("[data-testid='product-name']", timeout=10000)

        expect(page.get_by_test_id("product-name")).to_contain_text("Netflix")
        expect(page.get_by_test_id("score-badge")).to_be_visible()

    def test_events_listed(self, page: Page):
        page.goto(f"{FRONTEND}/product/netflix")
        page.wait_for_selector("[data-testid='events-list']", timeout=10000)

        events = page.locator("[data-testid='events-list'] > div")
        assert events.count() >= 3

    def test_back_link_works(self, page: Page):
        page.goto(f"{FRONTEND}/product/netflix")
        page.wait_for_selector("[data-testid='back-link']", timeout=10000)
        page.get_by_test_id("back-link").click()
        page.wait_for_selector("[data-testid='masthead']", timeout=10000)
        expect(page.get_by_test_id("masthead")).to_be_visible()

    def test_report_decay_button(self, page: Page):
        page.goto(f"{FRONTEND}/product/spotify")
        page.wait_for_selector("[data-testid='report-decay-btn']", timeout=10000)
        page.get_by_test_id("report-decay-btn").click()
        dialog = page.locator("dialog[open]")
        expect(dialog).to_be_visible()
        expect(dialog).to_contain_text("Report Decay")

    def test_decay_chart_visible_for_netflix(self, page: Page):
        page.goto(f"{FRONTEND}/product/netflix")
        page.wait_for_selector("[data-testid='decay-chart']", timeout=10000)
        expect(page.get_by_test_id("decay-chart")).to_be_visible()

    def test_adobe_worst_score_display(self, page: Page):
        page.goto(f"{FRONTEND}/product/adobe-cc")
        page.wait_for_selector("[data-testid='score-badge']", timeout=10000)
        score_text = page.get_by_test_id("score-badge").inner_text()
        assert int(score_text) < 20


# ──────────────────────────────────────────────
# Voting flow
# ──────────────────────────────────────────────

class TestVotingFlow:
    def test_submit_vote_flow(self, page: Page):
        page.goto(f"{FRONTEND}/product/discord")
        page.wait_for_selector("[data-testid='report-decay-btn']", timeout=10000)

        # Open dialog
        page.get_by_test_id("report-decay-btn").click()
        dialog = page.locator("dialog[open]")
        expect(dialog).to_be_visible()

        # Fill form
        dialog.locator("select").first.select_option("features")
        dialog.locator("textarea").fill("UI test vote")

        # Submit
        dialog.locator("button", has_text="Submit Vote").click()

        # Dialog should close
        page.wait_for_timeout(1000)
        expect(page.locator("dialog[open]")).not_to_be_visible()
