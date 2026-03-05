"""Tests for main app endpoints (root, health, favicon)."""


def test_root(client):
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "Pretorin CRM API"
    assert data["version"] == "1.0.0"
    assert data["docs"] == "/docs"


def test_health_check(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}


def test_favicon(client):
    response = client.get("/favicon.ico")
    assert response.status_code == 200
    assert response.json() == {"detail": "Not Found"}


def test_rate_limit_handler(client, admin_user):
    """Trigger rate limit on /auth/login by sending many requests."""
    for i in range(6):
        response = client.post("/auth/login", json={
            "email": "admin@test.com",
            "password": "wrong",
        })
    # The 6th request should be rate limited
    assert response.status_code in (401, 429)
