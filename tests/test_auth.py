from __future__ import annotations

from flask.testing import FlaskClient
from unittest.mock import patch

from app.config import get_seed_credentials
from app.services.db import DBError


def test_login_success_redirects_to_home(client: FlaskClient) -> None:
    """Valida o caminho feliz: credenciais corretas devem redirecionar para a home."""
    seed_credentials = get_seed_credentials()
    response = client.post(
        "/login",
        data={"login": seed_credentials.login, "password": seed_credentials.password},
        follow_redirects=False,
    )

    assert response.status_code == 302
    assert response.headers["Location"].endswith("/")


def test_login_invalid_shows_error_message(client: FlaskClient) -> None:
    """Garante feedback amigável quando a senha informada é inválida."""
    seed_credentials = get_seed_credentials()
    response = client.post(
        "/login",
        data={"login": seed_credentials.login, "password": "wrong-password"},
        follow_redirects=True,
    )

    assert response.status_code == 200
    assert b"Usuario ou senha invalidos." in response.data


def test_login_database_error_returns_friendly_error(client: FlaskClient) -> None:
    """Confirma que falhas de banco retornam erro tratado sem quebrar a UI."""
    seed_credentials = get_seed_credentials()

    # Simula indisponibilidade na camada de persistência durante o login.
    with patch("app.auth.routes.get_user_by_login", side_effect=DBError("db down")):
        response = client.post(
            "/login",
            data={"login": seed_credentials.login, "password": seed_credentials.password},
            follow_redirects=False,
        )

    assert response.status_code == 500
    assert b"Erro interno. Tente novamente." in response.data
