"""Pytest fixtures: isolated SQLite per test, authenticated client helper."""

from __future__ import annotations

import os
import tempfile
from collections.abc import Iterator

import pytest

# Configure environment before any app imports so ``get_settings()`` picks it up.
_tmp = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
_tmp.close()
os.environ["DATABASE_URL"] = f"sqlite:///{_tmp.name}"
os.environ["JWT_SECRET"] = "test-secret"

from fastapi.testclient import TestClient  # noqa: E402
from sqlalchemy import create_engine  # noqa: E402
from sqlalchemy.orm import sessionmaker  # noqa: E402

from backend.app import db as db_module  # noqa: E402
from backend.app.db import Base  # noqa: E402
from backend.app.main import app  # noqa: E402


@pytest.fixture
def client() -> Iterator[TestClient]:
    # Fresh in-memory-ish DB per test: point the app engine at a new file.
    fd, path = tempfile.mkstemp(suffix=".db")
    os.close(fd)
    url = f"sqlite:///{path}"
    test_engine = create_engine(url, connect_args={"check_same_thread": False})
    test_session = sessionmaker(bind=test_engine, autoflush=False, autocommit=False, expire_on_commit=False)

    # Swap the module-level engine and session so routes see this DB.
    db_module.engine = test_engine
    db_module.SessionLocal = test_session
    Base.metadata.create_all(bind=test_engine)

    with TestClient(app) as c:
        yield c

    Base.metadata.drop_all(bind=test_engine)
    try:
        os.unlink(path)
    except OSError:
        pass


@pytest.fixture
def auth_client(client: TestClient) -> TestClient:
    """TestClient pre-authenticated as a fresh user."""
    resp = client.post(
        "/api/auth/register",
        json={"email": "test@example.com", "password": "hunter22!", "display_name": "Tester"},
    )
    assert resp.status_code == 201, resp.text
    token = resp.json()["access_token"]
    client.headers.update({"Authorization": f"Bearer {token}"})
    return client
