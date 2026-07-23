from __future__ import annotations

"""Funções auxiliares de acesso ao SQLite usadas na autenticação."""

import sqlite3
from dataclasses import dataclass
from typing import Optional

from app.models import USER_TABLE_SCHEMA_SQL


class DBError(Exception):
    """Exceção levantada quando uma operação de banco falha."""


@dataclass(frozen=True)
class User:
    """Representação serializável de um registro de usuário autenticado."""

    id: int
    login: str
    email: str
    password_hash: str


def _uses_sqlite_uri(database_path: str) -> bool:
    """Retorna se o caminho configurado usa sintaxe de URI do SQLite."""
    return database_path.startswith("file:")


def get_connection(database_path: str) -> sqlite3.Connection:
    """Cria uma conexão SQLite com acesso às colunas por nome."""
    try:
        connection = sqlite3.connect(database_path, uri=_uses_sqlite_uri(database_path))
        connection.row_factory = sqlite3.Row
        return connection
    except sqlite3.Error as exc:
        raise DBError(f"Failed to connect to database: {exc}") from exc


def initialize_database(database_path: str) -> None:
    """Garante que o schema exista antes da aplicação começar a responder."""
    try:
        with get_connection(database_path) as connection:
            connection.executescript(USER_TABLE_SCHEMA_SQL)
            connection.commit()
    except sqlite3.Error as exc:
        raise DBError(f"Failed to initialize database: {exc}") from exc


def get_user_by_login(database_path: str, login_or_email: str) -> Optional[User]:
    """Busca um usuário por login ou e-mail para validar credenciais."""
    query = (
        "SELECT id, login, email, password_hash "
        "FROM users "
        "WHERE login = ? OR email = ? "
        "LIMIT 1"
    )

    try:
        with get_connection(database_path) as connection:
            row = connection.execute(query, (login_or_email, login_or_email)).fetchone()
    except sqlite3.Error as exc:
        raise DBError(f"Failed to fetch user: {exc}") from exc

    if row is None:
        return None

    # Normaliza os valores da linha SQLite no objeto imutável usado pelas rotas.
    return User(
        id=int(row["id"]),
        login=str(row["login"]),
        email=str(row["email"]),
        password_hash=str(row["password_hash"]),
    )
