from __future__ import annotations

import logging
import os

from dotenv import load_dotenv
from werkzeug.security import generate_password_hash

from app.config import ConfigError, get_seed_credentials
from app.services.db import get_connection, initialize_database

LOGGER = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")


def seed_user(database_path: str, login: str, email: str, raw_password: str) -> None:
    password_hash = generate_password_hash(raw_password, method="pbkdf2:sha256")

    query = (
        "INSERT INTO users (login, email, password_hash) "
        "VALUES (?, ?, ?) "
        "ON CONFLICT(login) DO UPDATE SET "
        "email = excluded.email, "
        "password_hash = excluded.password_hash"
    )

    with get_connection(database_path) as connection:
        connection.execute(query, (login, email, password_hash))
        connection.commit()


def main() -> None:
    load_dotenv()

    database_path = os.getenv("DATABASE_PATH")
    if not database_path:
        raise RuntimeError("DATABASE_PATH is required to run seed")

    try:
        seed_credentials = get_seed_credentials()
    except ConfigError as exc:
        raise RuntimeError(str(exc)) from exc

    os.makedirs(os.path.dirname(database_path), exist_ok=True)
    initialize_database(database_path)
    seed_user(
        database_path,
        login=seed_credentials.login,
        email=seed_credentials.email,
        raw_password=seed_credentials.password,
    )
    LOGGER.info("event=seed_completed, error_type=NONE, detail=database initialized")


if __name__ == "__main__":
    main()
