from __future__ import annotations

"""Factory da aplicação e configuração global do Flask."""

import os

from dotenv import load_dotenv
from flask import Flask, Response, render_template, request
from flask_wtf.csrf import CSRFProtect  # pyright: ignore[reportMissingTypeStubs]
from werkzeug.exceptions import HTTPException, NotFound

from app.agenda import agenda_bp
from app.auth import auth_bp
from app.config import ConfigError, get_app_settings
from app.services.db import DBError, initialize_database

csrf = CSRFProtect()

def create_app() -> Flask:
    """Cria e configura a instância principal da aplicação Flask."""
    load_dotenv()

    try:
        settings = get_app_settings()
    except ConfigError as exc:
        raise RuntimeError(str(exc)) from exc

    app = Flask(__name__, instance_relative_config=True)
    app.config["SECRET_KEY"] = settings.secret_key
    app.config["DATABASE_PATH"] = settings.database_path
    app.config["MOCK_API_URL"] = settings.mock_api_url
    app.config["WTF_CSRF_TIME_LIMIT"] = None
    app.config["WTF_CSRF_ENABLED"] = True

    os.makedirs(app.instance_path, exist_ok=True)
    initialize_database(settings.database_path)

    csrf.init_app(app)  # pyright: ignore[reportUnknownMemberType]
    app.register_blueprint(auth_bp)
    app.register_blueprint(agenda_bp)

    @app.after_request
    def add_security_headers(response: Response) -> Response:
        """Aplica headers básicos de segurança em todas as respostas HTTP."""
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        return response

    @app.errorhandler(DBError)
    def handle_db_error(error: DBError):
        """Converte falhas de banco em uma página de erro controlada para o usuário."""
        app.logger.error(
            "event=database_operation_failed, error_type=DB_ERROR, detail=%s",
            str(error),
            exc_info=True,
        )
        return render_template("error.html", message="Erro interno. Tente novamente."), 500

    @app.errorhandler(NotFound)
    def handle_not_found(error: NotFound):
        """Registra rotas desconhecidas para ajudar a identificar a origem real da requisição."""
        app.logger.info(
            "event=route_not_found, error_type=NOT_FOUND, path=%s, referrer=%s, user_agent=%s",
            request.path,
            request.headers.get("Referer", "-"),
            request.headers.get("User-Agent", "-"),
        )
        return error

    @app.errorhandler(Exception)
    def handle_unexpected_error(error: Exception):
        """Trata exceções inesperadas sem expor detalhes internos."""
        if isinstance(error, HTTPException):
            return error

        app.logger.error(
            "event=unhandled_exception, error_type=INTERNAL_ERROR, detail=%s",
            str(error),
            exc_info=True,
        )
        return render_template("error.html", message="Erro interno. Tente novamente."), 500

    return app
