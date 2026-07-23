from __future__ import annotations

"""Funções auxiliares de cliente HTTP para a mock API externa de agendamentos."""

from typing import Any, cast

import requests


class APIUnavailableError(Exception):
    """Exceção levantada quando a API de agendamentos está indisponível."""


class APIInvalidResponseError(Exception):
    """Exceção levantada quando a API de agendamentos retorna payload inválido."""


REQUIRED_APPOINTMENT_FIELDS = {
    "data",
    "horario",
    "paciente",
    "cpf",
    "medico",
    "especialidade",
    "convenio",
    "status",
}


def _validate_appointments_payload(payload: Any) -> list[dict[str, str]]:
    """Valida e normaliza os payloads de agendamento recebidos da mock API."""
    if not isinstance(payload, list):
        raise APIInvalidResponseError("Expected a list in API response")

    normalized_payload: list[dict[str, str]] = []
    items = cast(list[Any], payload)
    for raw_item in items:
        if not isinstance(raw_item, dict):
            raise APIInvalidResponseError("Appointment item must be an object")

        item = cast(dict[str, Any], raw_item)

        missing_fields = REQUIRED_APPOINTMENT_FIELDS.difference(item)
        if missing_fields:
            missing = ", ".join(sorted(missing_fields))
            raise APIInvalidResponseError(f"Missing fields in appointment item: {missing}")

        # Converte todos os valores para string para o frontend receber um payload previsível.
        normalized_payload.append({field: str(item[field]) for field in REQUIRED_APPOINTMENT_FIELDS})

    return normalized_payload


def fetch_appointments(mock_api_url: str, timeout_seconds: float = 3.0) -> list[dict[str, str]]:
    """Busca agendamentos na mock API e converte falhas de transporte em exceções tipadas."""
    try:
        response = requests.get(mock_api_url, timeout=timeout_seconds)
        response.raise_for_status()
    except requests.RequestException as exc:
        raise APIUnavailableError(f"Failed to reach appointments API: {exc}") from exc

    try:
        payload = response.json()
    except ValueError as exc:
        raise APIInvalidResponseError(f"Invalid JSON payload: {exc}") from exc

    return _validate_appointments_payload(payload)
