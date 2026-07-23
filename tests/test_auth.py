from __future__ import annotations

from app.config import get_seed_credentials
from flask.testing import FlaskClient


def test_login_success_redirects_to_home(client: FlaskClient) -> None:
    seed_credentials = get_seed_credentials()
    response = client.post(
        "/login",
        data={"login": seed_credentials.login, "password": seed_credentials.password},
        follow_redirects=False,
    )

    assert response.status_code == 302
    assert response.headers["Location"].endswith("/")


def test_login_invalid_shows_error_message(client: FlaskClient) -> None:
    seed_credentials = get_seed_credentials()
    response = client.post(
        "/login",
        data={"login": seed_credentials.login, "password": "wrong-password"},
        follow_redirects=True,
    )

    assert response.status_code == 200
    assert b"Usuario ou senha invalidos." in response.data
