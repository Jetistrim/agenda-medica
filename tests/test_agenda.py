from __future__ import annotations

from unittest.mock import patch

from app.config import get_seed_credentials
from flask.testing import FlaskClient

from app.services.api_client import APIUnavailableError


def test_agenda_requires_authentication(client: FlaskClient) -> None:
    response = client.get("/", follow_redirects=False)

    assert response.status_code == 302
    assert response.headers["Location"].endswith("/login")


def test_api_unavailable_returns_controlled_error(client: FlaskClient) -> None:
    seed_credentials = get_seed_credentials()
    client.post(
        "/login",
        data={"login": seed_credentials.login, "password": seed_credentials.password},
        follow_redirects=True,
    )

    with patch(
        "app.agenda.routes.fetch_appointments",
        side_effect=APIUnavailableError("api offline"),
    ):
        response = client.get("/api/agendamentos")

    assert response.status_code == 200
    payload = response.get_json()
    assert payload["error"] == "API_UNAVAILABLE"
