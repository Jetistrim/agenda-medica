from __future__ import annotations

"""Leitura centralizada de configuração de ambiente da aplicação."""

import os
from dataclasses import dataclass


class ConfigError(RuntimeError):
    """Erro levantado quando falta uma configuração obrigatória."""


@dataclass(frozen=True)
class AppSettings:
    """Configurações obrigatórias usadas para subir a aplicação."""

    secret_key: str
    database_path: str
    mock_api_url: str


@dataclass(frozen=True)
class SeedCredentials:
    """Credenciais do usuário de teste carregadas do ambiente."""

    login: str
    email: str
    password: str


def _get_required_env(setting_name: str) -> str:
    """Lê uma variável obrigatória do ambiente e falha com mensagem objetiva."""
    setting_value = os.getenv(setting_name)
    if not setting_value:
        raise ConfigError(f"Missing environment setting: {setting_name}")

    return setting_value


def get_app_settings() -> AppSettings:
    """Retorna as configurações necessárias para a aplicação web."""
    return AppSettings(
        secret_key=_get_required_env("SECRET_KEY"),
        database_path=_get_required_env("DATABASE_PATH"),
        mock_api_url=_get_required_env("MOCK_API_URL"),
    )


def get_seed_credentials() -> SeedCredentials:
    """Retorna as credenciais do usuário inicial usadas por seed e testes."""
    return SeedCredentials(
        login=_get_required_env("TEST_USER_LOGIN"),
        email=_get_required_env("TEST_USER_EMAIL"),
        password=_get_required_env("TEST_USER_PASSWORD"),
    )