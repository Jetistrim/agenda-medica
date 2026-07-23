from __future__ import annotations

import os
import tempfile
from typing import Any, cast
from unittest.mock import patch

from dotenv import load_dotenv
from flask import Flask
from flask.testing import FlaskClient
from werkzeug.security import generate_password_hash

from app import create_app
from app.config import get_seed_credentials
from app.services.api_client import APIInvalidResponseError, APIUnavailableError
from app.services.db import DBError, get_connection


def bootstrap_client() -> tuple[str, Flask, FlaskClient]:
    load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), ".env.example"))
    seed_credentials = get_seed_credentials()
    temp_dir = tempfile.mkdtemp(prefix="agenda-manual-check-")
    db_path = os.path.join(temp_dir, "manual_check.db")

    os.environ["SECRET_KEY"] = "manual-check-secret"
    os.environ["DATABASE_PATH"] = db_path
    os.environ["MOCK_API_URL"] = "http://127.0.0.1:5001/appointments"

    app = create_app()
    app.config["TESTING"] = False
    app.config["WTF_CSRF_ENABLED"] = False

    with get_connection(db_path) as connection:
        connection.execute(
            "INSERT INTO users (login, email, password_hash) VALUES (?, ?, ?)",
            (
                seed_credentials.login,
                seed_credentials.email,
                generate_password_hash(seed_credentials.password, method="pbkdf2:sha256"),
            ),
        )
        connection.commit()

    client = app.test_client()
    return temp_dir, app, client


def print_result(name: str, passed: bool, detail: str) -> None:
    status = "PASS" if passed else "FAIL"
    print(f"[{status}] {name}: {detail}")


def to_string_key_dict(payload: Any) -> dict[str, Any]:
    if not isinstance(payload, dict):
        return {}

    typed_payload = cast(dict[Any, Any], payload)
    return {str(key): value for key, value in typed_payload.items()}


def main() -> None:
    temp_dir, _app, client = bootstrap_client()
    seed_credentials = get_seed_credentials()
    response_invalid = client.post(
        "/login",
        data={"login": seed_credentials.login, "password": "senha-invalida"},
        follow_redirects=True,
    )
    print_result(
        "1) Credenciais invalidas",
        response_invalid.status_code == 200 and b"Usuario ou senha invalidos." in response_invalid.data,
        f"status={response_invalid.status_code}",
    )

    client.post(
        "/login",
        data={"login": seed_credentials.login, "password": seed_credentials.password},
        follow_redirects=True,
    )

    with patch(
        "app.agenda.routes.fetch_appointments",
        side_effect=APIUnavailableError("api offline"),
    ):
        response_api_down = client.get("/api/agendamentos")
    payload_api_down = response_api_down.get_json(silent=True)
    payload_api_down_dict = to_string_key_dict(payload_api_down)
    print_result(
        "2) API indisponivel",
        response_api_down.status_code == 200 and payload_api_down_dict.get("error") == "API_UNAVAILABLE",
        f"status={response_api_down.status_code}, payload={payload_api_down_dict}",
    )

    with patch(
        "app.agenda.routes.fetch_appointments",
        side_effect=APIInvalidResponseError("invalid payload"),
    ):
        response_api_invalid = client.get("/api/agendamentos")
    payload_api_invalid = response_api_invalid.get_json(silent=True)
    payload_api_invalid_dict = to_string_key_dict(payload_api_invalid)
    print_result(
        "3) Resposta invalida da API",
        response_api_invalid.status_code == 200
        and payload_api_invalid_dict.get("error") == "API_INVALID_RESPONSE",
        f"status={response_api_invalid.status_code}, payload={payload_api_invalid_dict}",
    )

    with patch("app.agenda.routes.fetch_appointments", return_value=[]):
        response_empty = client.get("/api/agendamentos")
    payload_empty = response_empty.get_json(silent=True)
    payload_empty_dict = to_string_key_dict(payload_empty)
    print_result(
        "4) Nenhum agendamento",
        response_empty.status_code == 200 and payload_empty_dict.get("error") == "NO_RESULTS",
        f"status={response_empty.status_code}, payload={payload_empty_dict}",
    )

    response_home = client.get("/")
    html = response_home.data.decode("utf-8", errors="ignore")
    has_inline_message = "Nenhum registro encontrado para esta busca." in html
    has_filter_fields = all(token in html for token in ["rowData.paciente", "rowData.cpf", "rowData.medico"])
    print_result(
        "5) Busca sem resultado",
        response_home.status_code == 200 and has_inline_message and has_filter_fields,
        f"status={response_home.status_code}, inline_message={has_inline_message}, filter_fields={has_filter_fields}",
    )

    with client.session_transaction() as flask_session:
        flask_session.clear()

    with patch("app.auth.routes.get_user_by_login", side_effect=DBError("db down")):
        response_db_error = client.post(
            "/login",
            data={"login": seed_credentials.login, "password": seed_credentials.password},
            follow_redirects=False,
        )
    body_db_error = response_db_error.data.decode("utf-8", errors="ignore")
    print_result(
        "6) Erro de banco tratado",
        response_db_error.status_code == 500 and "Erro interno. Tente novamente." in body_db_error,
        f"status={response_db_error.status_code}",
    )

    print(f"Validation database path: {os.path.join(temp_dir, 'manual_check.db')}")


if __name__ == "__main__":
    main()
