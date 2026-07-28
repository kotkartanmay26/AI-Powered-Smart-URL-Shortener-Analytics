import time
import sys
from pathlib import Path

from fastapi.testclient import TestClient

BACKEND_DIR = Path(__file__).resolve().parents[2] / "backend"
sys.path.insert(0, str(BACKEND_DIR))

from main import app


def test_auth_url_analytics_qr_flow():
    suffix = str(int(time.time()))
    email = f"qa{suffix}@example.com"
    username = f"qa{suffix}"

    with TestClient(app) as client:
        register = client.post(
            "/api/v1/auth/register",
            json={
                "email": email,
                "username": username,
                "full_name": "QA User",
                "password": "StrongPass123",
            },
        )
        assert register.status_code == 201

        login = client.post(
            "/api/v1/auth/login",
            json={"email": email, "password": "StrongPass123"},
        )
        assert login.status_code == 200
        token = login.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        created = client.post(
            "/api/v1/urls/",
            json={
                "original_url": "https://example.com/demo",
                "custom_alias": f"demo{suffix[-5:]}",
                "title": "Demo",
            },
            headers=headers,
        )
        assert created.status_code == 201
        url_id = created.json()["id"]

        listing = client.get("/api/v1/urls/", headers=headers)
        assert listing.status_code == 200
        assert listing.json()["total"] >= 1

        stats = client.get("/api/v1/analytics/stats", headers=headers)
        assert stats.status_code == 200
        assert stats.json()["total_urls"] >= 1

        qr = client.get(f"/api/v1/urls/{url_id}/qr", headers=headers)
        assert qr.status_code == 200
        assert "svg" in qr.json()["qr_code_svg"]

        updated = client.put(
            f"/api/v1/urls/{url_id}",
            json={"title": "Updated", "original_url": "https://example.com/updated"},
            headers=headers,
        )
        assert updated.status_code == 200
        assert updated.json()["title"] == "Updated"

        deleted = client.delete(f"/api/v1/urls/{url_id}", headers=headers)
        assert deleted.status_code == 204
