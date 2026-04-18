from fastapi.testclient import TestClient


def test_register_returns_token_and_user(client: TestClient):
    resp = client.post(
        "/api/auth/register",
        json={"email": "a@b.com", "password": "hunter22!", "display_name": "A"},
    )
    assert resp.status_code == 201
    body = resp.json()
    assert body["token_type"] == "bearer"
    assert body["access_token"]
    assert body["user"]["email"] == "a@b.com"
    assert body["user"]["is_premium"] is False


def test_cannot_register_duplicate_email(client: TestClient):
    payload = {"email": "dup@x.com", "password": "hunter22!"}
    r1 = client.post("/api/auth/register", json=payload)
    assert r1.status_code == 201
    r2 = client.post("/api/auth/register", json=payload)
    assert r2.status_code == 400


def test_login_with_valid_credentials(client: TestClient):
    client.post("/api/auth/register", json={"email": "l@x.com", "password": "hunter22!"})
    resp = client.post("/api/auth/login", data={"username": "l@x.com", "password": "hunter22!"})
    assert resp.status_code == 200
    assert resp.json()["access_token"]


def test_login_wrong_password_fails(client: TestClient):
    client.post("/api/auth/register", json={"email": "l2@x.com", "password": "hunter22!"})
    resp = client.post("/api/auth/login", data={"username": "l2@x.com", "password": "wrongpass"})
    assert resp.status_code == 401


def test_me_requires_auth(client: TestClient):
    resp = client.get("/api/auth/me")
    assert resp.status_code == 401


def test_me_returns_current_user(auth_client: TestClient):
    resp = auth_client.get("/api/auth/me")
    assert resp.status_code == 200
    assert resp.json()["email"] == "test@example.com"


def test_password_min_length(client: TestClient):
    resp = client.post("/api/auth/register", json={"email": "x@x.com", "password": "short"})
    assert resp.status_code == 422
