#!/usr/bin/env python3
"""Smoke test — быстрая проверка что сервис работает."""
import sys
import httpx

BASE = "http://localhost:8790"

checks = [
    ("GET /health", "GET", "/health", 200),
    ("GET /api/products", "GET", "/api/products", 200),
    ("GET /api/categories", "GET", "/api/categories", 200),
    ("GET /api/products/netflix", "GET", "/api/products/netflix", 200),
    ("GET /api/products/search?q=twit", "GET", "/api/products/search?q=twit", 200),
    ("GET /api/votes/999999 (404)", "GET", "/api/votes/999999", 404),
]

passed = 0
failed = 0

for name, method, path, expected in checks:
    try:
        r = httpx.request(method, f"{BASE}{path}", timeout=5)
        ok = r.status_code == expected
        status = "PASS" if ok else f"FAIL (got {r.status_code})"
        if ok:
            passed += 1
        else:
            failed += 1
    except Exception as e:
        status = f"FAIL ({e})"
        failed += 1
    print(f"  {'✓' if 'PASS' in status else '✗'} {name} → {status}")

print(f"\n{'=' * 40}")
print(f"Results: {passed} passed, {failed} failed")
sys.exit(1 if failed else 0)
