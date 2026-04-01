"""
E2E API tests for DecayTracker v2 — The Trust Feed.
Run: uv run pytest tests/test_e2e.py -v
"""
import time
import uuid

import httpx
import pytest

BASE = "http://localhost:8790"


def _unique_url(domain: str = "wikipedia.org") -> str:
    """Generate a unique URL on a real domain to bypass dedup + DNS validation."""
    return f"https://{domain}/test/{uuid.uuid4().hex[:8]}"


@pytest.fixture(scope="session")
def client():
    with httpx.Client(base_url=BASE, timeout=10) as c:
        yield c


# ── Health ──

class TestHealth:
    def test_health_ok(self, client):
        r = client.get("/health")
        assert r.status_code == 200
        data = r.json()
        assert data["status"] == "ok"
        assert data["version"] == "2.0.0"


# ── Companies ──

class TestCompanies:
    def test_leaderboard_returns_list(self, client):
        r = client.get("/api/companies?order=best&limit=5")
        assert r.status_code == 200
        data = r.json()
        assert isinstance(data, list)
        assert len(data) <= 5

    def test_leaderboard_worst(self, client):
        r = client.get("/api/companies?order=worst&limit=3")
        assert r.status_code == 200
        data = r.json()
        assert isinstance(data, list)

    def test_company_fields(self, client):
        r = client.get("/api/companies?order=best&limit=1")
        data = r.json()
        if data:
            c = data[0]
            assert "name" in c
            assert "slug" in c
            assert "domain" in c
            assert "trust_score" in c
            assert "total_audits" in c
            assert "trend_30d" in c
            assert "top_findings" in c

    def test_company_by_slug(self, client):
        r = client.get("/api/company/netflix")
        assert r.status_code == 200
        data = r.json()
        assert data["name"] == "Netflix"
        assert data["slug"] == "netflix"
        assert data["domain"] == "netflix.com"
        assert "recent_audits" in data

    def test_company_not_found(self, client):
        r = client.get("/api/company/nonexistent-xyz")
        assert r.status_code == 404

    def test_company_search(self, client):
        r = client.get("/api/companies/search?q=net")
        assert r.status_code == 200
        data = r.json()
        assert isinstance(data, list)
        found = [c for c in data if "net" in c["name"].lower()]
        assert len(found) > 0

    def test_company_audits_paginated(self, client):
        r = client.get("/api/company/netflix/audits?page=1&per_page=5")
        assert r.status_code == 200
        data = r.json()
        assert "items" in data
        assert "total" in data
        assert "has_more" in data

    def test_seeded_companies(self, client):
        r = client.get("/api/companies?order=best&limit=20")
        data = r.json()
        names = [c["name"] for c in data]
        for expected in ["Amazon", "Google", "Apple", "Netflix"]:
            assert expected in names


# ── Audit Submission ──

class TestAuditSubmission:
    def test_submit_url(self, client):
        r = client.post("/api/audit", json={"url": _unique_url("example.com")})
        assert r.status_code == 202
        data = r.json()
        assert "audit_id" in data
        assert "company_slug" in data
        assert data["status"] == "pending"

    def test_submit_amazon_url(self, client):
        r = client.post("/api/audit", json={"url": "https://www.amazon.com/dp/B0TEST12345"})
        assert r.status_code == 202
        data = r.json()
        assert data["platform"] == "amazon_product"
        assert data["company_slug"] == "amazon"

    def test_submit_appstore_url(self, client):
        r = client.post("/api/audit", json={"url": "https://apps.apple.com/us/app/test/id123"})
        assert r.status_code == 202
        data = r.json()
        assert data["platform"] == "appstore_app"

    def test_submit_invalid_url(self, client):
        r = client.post("/api/audit", json={"url": "not-a-url"})
        assert r.status_code == 422

    def test_submit_empty_url(self, client):
        r = client.post("/api/audit", json={"url": ""})
        assert r.status_code == 422

    def test_submit_creates_company(self, client):
        r = client.post("/api/audit", json={"url": _unique_url("cloudflare.com")})
        assert r.status_code == 202
        data = r.json()
        # Company was auto-created
        slug = data["company_slug"]
        r2 = client.get(f"/api/company/{slug}")
        assert r2.status_code == 200


# ── Audit Detail ──

class TestAuditDetail:
    def test_get_audit(self, client):
        # Submit first
        r = client.post("/api/audit", json={"url": _unique_url("spotify.com")})
        audit_id = r.json()["audit_id"]
        # Get detail
        r2 = client.get(f"/api/audit/{audit_id}")
        assert r2.status_code == 200
        data = r2.json()
        assert data["id"] == audit_id
        assert "company_name" in data
        assert "findings" in data

    def test_audit_not_found(self, client):
        r = client.get("/api/audit/999999")
        assert r.status_code == 404

    def test_audit_has_required_fields(self, client):
        r = client.post("/api/audit", json={"url": _unique_url("github.com")})
        assert r.status_code == 202
        audit_id = r.json()["audit_id"]
        r2 = client.get(f"/api/audit/{audit_id}")
        data = r2.json()
        for field in ["id", "url", "platform", "title", "trust_score", "severity", "status", "views", "created_at"]:
            assert field in data, f"Missing field: {field}"


# ── Feed ──

class TestFeed:
    def test_feed_returns_paginated(self, client):
        r = client.get("/api/feed")
        assert r.status_code == 200
        data = r.json()
        assert "items" in data
        assert "total" in data
        assert "page" in data
        assert "per_page" in data
        assert "has_more" in data

    def test_feed_pagination(self, client):
        r = client.get("/api/feed?page=1&per_page=2")
        assert r.status_code == 200
        data = r.json()
        assert len(data["items"]) <= 2

    def test_feed_includes_all_visible_statuses(self, client):
        """Feed should contain done, pending, processing, and failed audits."""
        r = client.get("/api/feed")
        data = r.json()
        allowed = {"done", "pending", "processing", "failed"}
        for item in data["items"]:
            assert item["status"] in allowed

    def test_feed_shows_pending_after_submit(self, client):
        """Newly submitted audit appears in feed as pending/processing/done."""
        r = client.post("/api/audit", json={"url": _unique_url("reddit.com")})
        assert r.status_code == 202
        audit_id = r.json()["audit_id"]

        r2 = client.get("/api/feed?per_page=100")
        data = r2.json()
        ids = [item["id"] for item in data["items"]]
        assert audit_id in ids

        found = [item for item in data["items"] if item["id"] == audit_id][0]
        assert found["status"] in ("pending", "processing", "done", "failed")


# ── Retry ──

class TestRetry:
    def test_retry_not_found(self, client):
        """Retry on non-existent audit returns 404."""
        r = client.post("/api/audit/999999/retry")
        assert r.status_code == 404

    def test_retry_non_failed_audit(self, client):
        """Retry on a non-failed audit returns 409."""
        r = client.post("/api/audit", json={"url": _unique_url("mozilla.org")})
        assert r.status_code == 202
        audit_id = r.json()["audit_id"]
        # Immediately retry — audit is pending/processing, not failed
        r2 = client.post(f"/api/audit/{audit_id}/retry")
        assert r2.status_code == 409

    def test_retry_failed_audit(self, client):
        """Submit an audit, wait for it to potentially fail, then retry."""
        r = client.post("/api/audit", json={"url": _unique_url("twitch.tv")})
        assert r.status_code == 202
        audit_id = r.json()["audit_id"]

        # Wait for background agent to process (it will likely fail
        # since there's no real OpenRouter key configured in test env)
        time.sleep(2)

        r2 = client.get(f"/api/audit/{audit_id}")
        assert r2.status_code == 200
        status = r2.json()["status"]

        # If the audit failed (expected in test env without API keys),
        # retry should reset it to pending
        if status == "failed":
            r3 = client.post(f"/api/audit/{audit_id}/retry")
            assert r3.status_code == 202
            data = r3.json()
            assert data["status"] == "pending"
            assert data["audit_id"] == audit_id
        else:
            # If audit didn't fail, at least verify retry rejects non-failed audits
            r3 = client.post(f"/api/audit/{audit_id}/retry")
            assert r3.status_code == 409


# ── Stats ──

class TestStats:
    def test_stats_endpoint(self, client):
        """Stats returns expected fields."""
        r = client.get("/api/stats")
        assert r.status_code == 200
        data = r.json()
        assert "total_audits" in data
        assert "total_companies" in data
        assert "total_findings" in data
        assert "audits_today" in data

    def test_stats_types(self, client):
        """Stats values are non-negative integers."""
        r = client.get("/api/stats")
        data = r.json()
        assert isinstance(data["total_audits"], int)
        assert isinstance(data["total_companies"], int)
        assert isinstance(data["total_findings"], int)
        assert isinstance(data["audits_today"], int)
        assert data["total_audits"] >= 0
        assert data["total_companies"] >= 0
        assert data["total_findings"] >= 0
        assert data["audits_today"] >= 0

    def test_stats_companies_count(self, client):
        """Stats should report at least the seeded companies."""
        r = client.get("/api/stats")
        data = r.json()
        # We have at least 8 seeded companies
        assert data["total_companies"] >= 8
