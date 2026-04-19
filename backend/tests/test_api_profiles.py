from fastapi.testclient import TestClient


def _make(auth_client: TestClient, name: str, is_main: bool = False) -> dict:
    resp = auth_client.post(
        "/api/profiles",
        json={
            "name": name,
            "birth_datetime": "1990-06-15T08:30:00",
            "relationship_label": "self",
            "is_main": is_main,
        },
    )
    assert resp.status_code == 201, resp.text
    return resp.json()


def _promote_to_premium(email: str = "test@example.com") -> None:
    """Helper to allow tests that need multi-profile setups to bypass the free limit."""
    from backend.app.db import SessionLocal
    from backend.app.models import User
    with SessionLocal() as db:
        user = db.query(User).filter(User.email == email).first()
        user.is_premium = True
        db.commit()


def test_create_and_list_profiles(auth_client: TestClient):
    _promote_to_premium()
    _make(auth_client, "Alice", is_main=True)
    _make(auth_client, "Bob")
    resp = auth_client.get("/api/profiles")
    assert resp.status_code == 200
    body = resp.json()
    assert len(body) == 2
    # Main profile should be first.
    assert body[0]["name"] == "Alice"
    assert body[0]["is_main"] is True


def test_free_tier_limit_is_one(auth_client: TestClient):
    _make(auth_client, "P1")
    resp = auth_client.post(
        "/api/profiles",
        json={"name": "P2", "birth_datetime": "1990-01-01T00:00:00"},
    )
    assert resp.status_code == 402
    detail = resp.json()["detail"]
    # Message should hint that more slots cost $16 or the $88/mo plan unlocks all.
    assert "$16" in detail and "$88" in detail


def test_setting_main_unsets_other_mains(auth_client: TestClient):
    _promote_to_premium()
    a = _make(auth_client, "A", is_main=True)
    b = _make(auth_client, "B", is_main=True)

    resp = auth_client.get("/api/profiles")
    mains = [p for p in resp.json() if p["is_main"]]
    assert len(mains) == 1
    assert mains[0]["id"] == b["id"]

    # Re-flip back to A via PATCH.
    patch = auth_client.patch(f"/api/profiles/{a['id']}", json={"is_main": True})
    assert patch.status_code == 200

    resp = auth_client.get("/api/profiles")
    mains = [p for p in resp.json() if p["is_main"]]
    assert len(mains) == 1
    assert mains[0]["id"] == a["id"]


def test_cannot_access_other_users_profile(client: TestClient):
    # User 1 creates a profile.
    r1 = client.post("/api/auth/register", json={"email": "u1@x.com", "password": "hunter22!"})
    t1 = r1.json()["access_token"]
    p = client.post(
        "/api/profiles",
        headers={"Authorization": f"Bearer {t1}"},
        json={"name": "mine", "birth_datetime": "1990-01-01T00:00:00"},
    ).json()

    # User 2 tries to read it.
    r2 = client.post("/api/auth/register", json={"email": "u2@x.com", "password": "hunter22!"})
    t2 = r2.json()["access_token"]
    resp = client.get(f"/api/profiles/{p['id']}", headers={"Authorization": f"Bearer {t2}"})
    assert resp.status_code == 404


def test_delete_profile(auth_client: TestClient):
    a = _make(auth_client, "Alice")
    resp = auth_client.delete(f"/api/profiles/{a['id']}")
    assert resp.status_code == 204
    assert auth_client.get(f"/api/profiles/{a['id']}").status_code == 404


def test_premium_user_bypasses_limit(auth_client: TestClient):
    # Promote the test user to premium directly via DB.
    from backend.app.db import SessionLocal
    from backend.app.models import User

    with SessionLocal() as db:
        user = db.query(User).filter(User.email == "test@example.com").first()
        user.is_premium = True
        db.commit()

    for i in range(5):
        _make(auth_client, f"P{i}")
    resp = auth_client.get("/api/profiles")
    assert len(resp.json()) == 5
