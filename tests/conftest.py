from __future__ import annotations

import os
from collections.abc import Generator
from pathlib import Path

import pytest
from dotenv import load_dotenv
from flask import Flask
from flask.testing import FlaskClient
from werkzeug.security import generate_password_hash

from app import create_app
from app.config import get_seed_credentials
from app.services.db import get_connection


@pytest.fixture
def app(tmp_path: Path) -> Generator[Flask, None, None]:
    load_dotenv(dotenv_path=Path(__file__).resolve().parents[1] / ".env.example")
    seed_credentials = get_seed_credentials()
    database_file = tmp_path / "test.db"

    os.environ["SECRET_KEY"] = "test-secret"
    os.environ["DATABASE_PATH"] = str(database_file)
    os.environ["MOCK_API_URL"] = "http://localhost:5001/appointments"

    flask_app = create_app()
    flask_app.config["TESTING"] = True
    flask_app.config["WTF_CSRF_ENABLED"] = False

    with get_connection(str(database_file)) as connection:
        connection.execute(
            "INSERT INTO users (login, email, password_hash) VALUES (?, ?, ?)",
            (
                seed_credentials.login,
                seed_credentials.email,
                generate_password_hash(seed_credentials.password, method="pbkdf2:sha256"),
            ),
        )
        connection.commit()

    yield flask_app


@pytest.fixture
def client(app: Flask) -> FlaskClient:
    return app.test_client()
