from fastapi.testclient import TestClient


def _make(auth_client: TestClient, name: str, birth: str) -> dict:
    resp = auth_client.post(
        "/api/profiles",
        json={"name": name, "birth_datetime": birth},
    )
    return resp.json()


def test_bazi_reading_structure(auth_client: TestClient):
    p = _make(auth_client, "Alice", "2000-01-01T12:00:00")
    resp = auth_client.get(f"/api/profiles/{p['id']}/bazi")
    assert resp.status_code == 200
    body = resp.json()
    assert set(body.keys()) >= {"year", "month", "day", "hour", "day_master", "zodiac", "elements"}
    assert body["day_master"] == "戊"
    assert body["day_master_element"] == "earth"
    assert body["zodiac"] == "Rabbit"  # year is 1999 solar year -> 卯 -> Rabbit


def test_daily_luck_returns_score_and_pillar(auth_client: TestClient):
    p = _make(auth_client, "Alice", "2000-01-01T12:00:00")
    resp = auth_client.get(f"/api/profiles/{p['id']}/daily")
    assert resp.status_code == 200
    body = resp.json()
    assert 0 <= body["score"] <= 100
    assert "day_pillar" in body
    assert isinstance(body["summary"], str) and body["summary"]


def test_numerology_endpoint(auth_client: TestClient):
    resp = auth_client.post("/api/numerology", json={"number": "+1 555-888-8888"})
    assert resp.status_code == 200
    body = resp.json()
    assert 0 <= body["wealth"] <= 100
    assert 0 <= body["safety"] <= 100
    assert 0 <= body["health"] <= 100


def test_numerology_rejects_empty(auth_client: TestClient):
    resp = auth_client.post("/api/numerology", json={"number": "abc"})
    assert resp.status_code == 400


def test_compatibility_between_two_profiles(auth_client: TestClient):
    a = _make(auth_client, "Alice", "2000-01-01T12:00:00")
    b = _make(auth_client, "Bob", "1995-06-15T08:00:00")
    resp = auth_client.post(
        "/api/compatibility",
        json={"profile_a_id": a["id"], "profile_b_id": b["id"]},
    )
    assert resp.status_code == 200
    body = resp.json()
    assert 0 <= body["score"] <= 100
    assert isinstance(body["harmony"], list)
    assert isinstance(body["tension"], list)
    assert set(body["element_blend"].keys()) == {"wood", "fire", "earth", "metal", "water"}


def test_compatibility_rejects_same_profile(auth_client: TestClient):
    a = _make(auth_client, "Alice", "2000-01-01T12:00:00")
    resp = auth_client.post(
        "/api/compatibility",
        json={"profile_a_id": a["id"], "profile_b_id": a["id"]},
    )
    assert resp.status_code == 400


def test_readings_require_auth(client: TestClient):
    resp = client.post("/api/numerology", json={"number": "1234"})
    assert resp.status_code == 401
