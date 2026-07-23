from __future__ import annotations

from unittest.mock import patch

from app.config import get_seed_credentials
from flask.testing import FlaskClient

from app.services.api_client import APIInvalidResponseError, APIUnavailableError


def authenticate(client: FlaskClient) -> None:
    """Autentica o usuário padrão para acessar rotas protegidas da agenda."""
    seed_credentials = get_seed_credentials()
    client.post(
        "/login",
        data={"login": seed_credentials.login, "password": seed_credentials.password},
        follow_redirects=True,
    )


def test_agenda_requires_authentication(client: FlaskClient) -> None:
    """Sem sessão ativa, a rota principal deve redirecionar para login."""
    response = client.get("/", follow_redirects=False)

    assert response.status_code == 302
    assert response.headers["Location"].endswith("/login")


def test_api_unavailable_returns_controlled_error(client: FlaskClient) -> None:
    """Quando a API externa está fora, a resposta deve seguir o contrato controlado."""
    authenticate(client)

    # Força erro de conectividade da API sem depender de HTTP real.
    with patch(
        "app.agenda.routes.fetch_appointments",
        side_effect=APIUnavailableError("api offline"),
    ):
        response = client.get("/api/agendamentos")

    assert response.status_code == 200
    payload = response.get_json()
    assert payload["error"] == "API_UNAVAILABLE"


def test_api_invalid_response_returns_controlled_error(client: FlaskClient) -> None:
    """Payload inválido da API deve virar erro de negócio previsível para o frontend."""
    authenticate(client)

    # Simula JSON malformado/fora de contrato vindo da integração.
    with patch(
        "app.agenda.routes.fetch_appointments",
        side_effect=APIInvalidResponseError("invalid payload"),
    ):
        response = client.get("/api/agendamentos")

    assert response.status_code == 200
    payload = response.get_json()
    assert payload["error"] == "API_INVALID_RESPONSE"


def test_empty_appointments_returns_no_results_payload(client: FlaskClient) -> None:
    """Lista vazia de agendamentos deve retornar NO_RESULTS com data vazia."""
    authenticate(client)

    with patch("app.agenda.routes.fetch_appointments", return_value=[]):
        response = client.get("/api/agendamentos")

    assert response.status_code == 200
    payload = response.get_json()
    assert payload["error"] == "NO_RESULTS"
    assert payload["data"] == []
