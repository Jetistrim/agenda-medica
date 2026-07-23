from __future__ import annotations

"""Views da agenda e endpoints JSON consumidos pela tabela do frontend."""

from typing import cast

from flask import Blueprint, current_app, jsonify, redirect, render_template, session, url_for

from app.services.api_client import APIInvalidResponseError, APIUnavailableError, fetch_appointments

agenda_bp = Blueprint("agenda", __name__)


@agenda_bp.route("/")
def index():
    """Renderiza a página da agenda para usuários autenticados."""
    session_data = cast(dict[str, object], session)

    if session_data.get("user_id") is None:
        return redirect(url_for("auth.login"))

    user_login = cast(str, session_data.get("user_login", ""))
    return render_template("agenda.html", user_login=user_login)


@agenda_bp.route("/api/agendamentos", methods=["GET"])
def appointments_api():
    """Expõe os agendamentos ao frontend com contratos de erro controlados."""
    session_data = cast(dict[str, object], session)
    if session_data.get("user_id") is None:
        return jsonify({"error": "AUTH_REQUIRED", "message": "Login necessario."}), 401

    mock_api_url = cast(str, current_app.config["MOCK_API_URL"])

    try:
        appointments = fetch_appointments(mock_api_url)
    except APIUnavailableError as exc:
        current_app.logger.error(
            "event=fetch_appointments, error_type=API_UNAVAILABLE, detail=%s",
            str(exc),
            exc_info=True,
        )
        return (
            jsonify(
                {
                    "error": "API_UNAVAILABLE",
                    "message": "Servico de agendamentos temporariamente indisponivel.",
                }
            ),
            200,
        )
    except APIInvalidResponseError as exc:
        current_app.logger.error(
            "event=fetch_appointments, error_type=API_INVALID_RESPONSE, detail=%s",
            str(exc),
            exc_info=True,
        )
        return (
            jsonify(
                {
                    "error": "API_INVALID_RESPONSE",
                    "message": "Dados recebidos estao incompletos.",
                }
            ),
            200,
        )

    # Resultado vazio é um cenário de negócio válido e não deve aparecer como falha técnica.
    if not appointments:
        return (
            jsonify(
                {
                    "error": "NO_RESULTS",
                    "message": "Nenhum agendamento encontrado.",
                    "data": [],
                }
            ),
            200,
        )

    return jsonify({"data": appointments}), 200
