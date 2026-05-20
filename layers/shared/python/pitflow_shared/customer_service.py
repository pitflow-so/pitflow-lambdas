import re
from typing import Any

import psycopg2
from psycopg2.extras import RealDictCursor
from psycopg2 import OperationalError, InterfaceError


from pitflow_shared.secret_manager_service import get_secret_value


DEFAULT_DB_PORT = "5432"

_connection = None


def find_customer(cpf: str) -> dict[str, Any] | None:
    normalized_cpf = _normalize_cpf(cpf)

    connection = _connect()

    with connection.cursor() as cursor:
        cursor.execute(
            """
            SELECT
                id,
                name,
                document,
                phone,
                email,
                status,
                created_at
            FROM customer
            WHERE document = %s
            LIMIT 1
            """,
            (normalized_cpf,),
        )

        customer = cursor.fetchone()

    return dict(customer) if customer else None


def _connect():
    global _connection

    try:
        if _connection is None or _connection.closed:
            raise OperationalError("Nova conexão necessária")

        with _connection.cursor() as cursor:
            cursor.execute("SELECT 1")

        return _connection

    except (OperationalError, InterfaceError):
        _connection = psycopg2.connect(
            host=get_secret_value("DB_HOST"),
            port=get_secret_value("DB_PORT", DEFAULT_DB_PORT),
            dbname=get_secret_value("DB_NAME"),
            user=get_secret_value("DB_USERNAME"),
            password=get_secret_value("DB_PASSWORD"),
            cursor_factory=RealDictCursor,
            connect_timeout=5,
        )

        return _connection


def _normalize_cpf(cpf: str) -> str:
    return re.sub(r"\D", "", cpf or "")
