from __future__ import annotations

import os
from collections.abc import Generator
from pathlib import Path
from uuid import uuid4

import pytest
from dotenv import load_dotenv
from flask import Flask
from flask.testing import FlaskClient
from werkzeug.security import generate_password_hash

from app import create_app
from app.config import get_seed_credentials
from app.services.db import get_connection


@pytest.fixture
def app() -> Generator[Flask, None, None]:
    """Cria uma app de teste com SQLite em memória compartilhada e usuário seedado."""
    load_dotenv(dotenv_path=Path(__file__).resolve().parents[1] / ".env.example")
    seed_credentials = get_seed_credentials()
    database_uri = f"file:agenda-phase2-tests-{uuid4().hex}?mode=memory&cache=shared"

    os.environ["SECRET_KEY"] = "test-secret"
    os.environ["DATABASE_PATH"] = database_uri
    os.environ["MOCK_API_URL"] = "http://localhost:5001/appointments"

    # Mantém a conexão aberta para preservar o banco em memória durante o teste.
    keeper_connection = get_connection(database_uri)

    flask_app = create_app()
    flask_app.config["TESTING"] = True
    flask_app.config["WTF_CSRF_ENABLED"] = False

    try:
        keeper_connection.execute(
            "INSERT INTO users (login, email, password_hash) VALUES (?, ?, ?)",
            (
                seed_credentials.login,
                seed_credentials.email,
                generate_password_hash(seed_credentials.password, method="pbkdf2:sha256"),
            ),
        )
        keeper_connection.commit()

        yield flask_app
    finally:
        keeper_connection.close()


@pytest.fixture
def client(app: Flask) -> FlaskClient:
    """Expõe o cliente HTTP do Flask para chamadas de integração."""
    return app.test_client()
